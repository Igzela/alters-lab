#!/usr/bin/env python3
"""Run P7-M8 local app release-candidate smoke in an isolated HOME."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SMOKE_NOTE = """# Weekly Review - Synthetic P7 smoke

## Session Type
project

## Observable Facts
- Built the local app package in a smoke environment.
- Started the package-context server on localhost.
- Opened local app health endpoints.
- Configured provider mode to mock.
- Kept this record synthetic and outside P6 validation.

## Subjective State
Focused on release-candidate safety.

## Primary Problem
The package must run without a repo checkout.

## Friction / Avoidance
Synthetic smoke records can be mistaken for real P6 evidence.

## Desired Correction
Keep smoke data in a temporary HOME and delete it after the run.
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run P7 local app smoke test")
    parser.add_argument("--deb", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--keep-temp", action="store_true")
    parser.add_argument("--evidence", default=None)
    return parser.parse_args(argv)


def choose_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def run_cmd(cmd: list[str], env: dict[str, str], cwd: Path) -> dict[str, Any]:
    result = subprocess.run(cmd, env=env, cwd=cwd, text=True, capture_output=True)
    return {
        "cmd": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def request_json(url: str, method: str = "GET", body: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.read().decode("utf-8")


def wait_for_server(base_url: str, timeout_seconds: float = 20.0) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            request_json(f"{base_url}/local-app/health")
            return
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(0.25)
    raise RuntimeError(f"server did not become ready: {last_error}")


def run_smoke(deb_path: Path, keep_temp: bool = False) -> dict[str, Any]:
    temp_ctx = tempfile.TemporaryDirectory(prefix="alters-lab-p7-smoke-")
    temp_root = Path(temp_ctx.name)
    env: dict[str, str] | None = None
    cli_base: list[str] | None = None
    start_attempted = False
    stopped = False
    try:
        pkgroot = temp_root / "pkgroot"
        home = temp_root / "home"
        home.mkdir()
        subprocess.run(["dpkg-deb", "-x", str(deb_path), str(pkgroot)], check=True)

        app_root = pkgroot / "opt" / "alters-lab"
        python = app_root / ".venv" / "bin" / "python"
        env = os.environ.copy()
        env.update(
            {
                "HOME": str(home),
                "ALTERS_LAB_MODE": "packaged",
                "ALTERS_LAB_APP_ROOT": str(app_root),
                "PYTHONPATH": str(app_root / "apps" / "api" / "src"),
            }
        )
        port = choose_port()
        base_url = f"http://127.0.0.1:{port}"
        cli_base = [str(python), "-m", "alters_lab.cli"]

        status_cmd = run_cmd(cli_base + ["status", "--mode", "packaged", "--host", "127.0.0.1", "--port", str(port), "--json"], env, temp_root)
        doctor_cmd = run_cmd(cli_base + ["doctor", "--mode", "packaged", "--host", "127.0.0.1", "--port", str(port), "--json"], env, temp_root)
        start_dry_run_cmd = run_cmd(cli_base + ["start", "--mode", "packaged", "--host", "127.0.0.1", "--port", str(port), "--dry-run", "--json"], env, temp_root)
        start_cmd = run_cmd(cli_base + ["start", "--mode", "packaged", "--host", "127.0.0.1", "--port", str(port), "--json"], env, temp_root)
        if start_cmd["returncode"] != 0:
            raise RuntimeError(start_cmd)
        start_attempted = True
        wait_for_server(base_url)

        health = request_json(f"{base_url}/local-app/health")
        local_status = request_json(f"{base_url}/local-app/status")
        runtime_status = request_json(f"{base_url}/runtime-layout/status")
        provider_status_before = request_json(f"{base_url}/provider-config/status")
        provider_config_before = request_json(f"{base_url}/provider-config/config")
        frontend = request_text(f"{base_url}/")
        asset_ok = _check_frontend_asset(base_url, frontend)

        provider_config = request_json(
            f"{base_url}/provider-config/config",
            method="POST",
            body={"mode": "mock", "explicit_user_configuration": False},
        )
        provider_test = request_json(f"{base_url}/provider-config/test", method="POST", body={"dry_run": True})

        note = request_json(
            f"{base_url}/obsidian-weekly-note/ingest",
            method="POST",
            body={"raw_note": SMOKE_NOTE, "source_path": "synthetic-p7-smoke.md"},
        )
        note_id = note["record"]["record_id"]
        weekly = request_json(f"{base_url}/weekly-review/start", method="POST", body={"weekly_note_record_id": note_id})
        session_id = weekly["session"]["session_id"]
        completed = request_json(
            f"{base_url}/weekly-review/{session_id}/complete",
            method="POST",
            body={
                "review_note": "Synthetic P7 smoke review. Not P6 real-use evidence.",
                "primary_next_correction": "Continue to P7 closeout only after review.",
                "supporting_actions": ["Keep smoke data isolated."],
            },
        )
        scored = request_json(
            f"{base_url}/action-alignment/score",
            method="POST",
            body={
                "session_id": session_id,
                "scores": {"direction_alignment": 0.5, "execution_consistency": 0.5, "avoidance_level": 0.5},
                "evidence": {
                    "one_action_evidence": "Package-context smoke created synthetic records.",
                    "one_avoidance_or_friction_evidence": "Synthetic records are not real P6 evidence.",
                    "one_next_correction": "Do not run behavior validation from smoke data.",
                },
                "verdict_label": "unstable_but_useful",
                "verdict_sentence": "Synthetic smoke verified package write paths only.",
            },
        )

        backup = run_cmd(cli_base + ["backup", "--mode", "packaged", "--dry-run", "--json"], env, temp_root)
        stop_cmd = run_cmd(cli_base + ["stop", "--mode", "packaged", "--json"], env, temp_root)
        stopped = True

        product_dir = home / ".local" / "share" / "alters-lab" / "product"
        record_paths = {
            "weekly_notes": sorted(str(p.relative_to(home)) for p in (product_dir / "weekly_notes").glob("*.yaml")),
            "weekly_reviews": sorted(str(p.relative_to(home)) for p in (product_dir / "weekly_reviews").glob("*.yaml")),
            "calibration_records": sorted(str(p.relative_to(home)) for p in (product_dir / "calibration_records").glob("*.yaml")),
        }
        report = {
            "status": "PASS",
            "method": "dpkg-deb -x simulated install",
            "temp_root": str(temp_root) if keep_temp else "[removed]",
            "port": port,
            "launcher": {
                "status": _json_stdout(status_cmd),
                "doctor": _json_stdout(doctor_cmd),
                "start_dry_run": _json_stdout(start_dry_run_cmd),
                "start": _json_stdout(start_cmd),
                "stop": _json_stdout(stop_cmd),
            },
            "server": {
                "local_app_health": health,
                "local_app_status": local_status,
                "runtime_layout_status": runtime_status,
                "frontend_index_loaded": "<!doctype html>" in frontend.lower() or "<div id=\"root\"" in frontend.lower(),
                "frontend_asset_loaded": asset_ok,
            },
            "provider": {
                "status_before": provider_status_before,
                "config_before": provider_config_before,
                "config_after": provider_config,
                "test": provider_test,
            },
            "runtime_data": {
                "synthetic_smoke_only": True,
                "home_product_dir": str(product_dir),
                "record_paths": record_paths,
                "note_status": note["status"],
                "weekly_status": completed["status"],
                "score_status": scored["status"],
            },
            "backup": _json_stdout(backup),
            "cleanup": {"server_stopped": stopped},
            "p6_behavior_validated": False,
            "p6_sealed": False,
        }
        _assert_report_passes(report)
        if not keep_temp:
            report = _redact_temp_paths(report, temp_root)
        return report
    finally:
        if start_attempted and not stopped and env is not None and cli_base is not None:
            run_cmd(cli_base + ["stop", "--mode", "packaged", "--json"], env, temp_root)
        if keep_temp:
            temp_ctx.cleanup = lambda: None  # type: ignore[method-assign]
        temp_ctx.cleanup()


def _json_stdout(result: dict[str, Any]) -> dict[str, Any]:
    if result["returncode"] != 0:
        raise RuntimeError(result)
    return json.loads(result["stdout"])


def _check_frontend_asset(base_url: str, html: str) -> bool:
    match = re.search(r"/(assets/[^\"']+\.js)", html)
    if not match:
        return False
    asset = request_text(f"{base_url}/{match.group(1)}")
    return len(asset) > 0


def _redact_temp_paths(value: Any, temp_root: Path) -> Any:
    if isinstance(value, str):
        return value.replace(str(temp_root), "[temp-root]")
    if isinstance(value, list):
        return [_redact_temp_paths(item, temp_root) for item in value]
    if isinstance(value, dict):
        return {key: _redact_temp_paths(item, temp_root) for key, item in value.items()}
    return value


def _assert_report_passes(report: dict[str, Any]) -> None:
    assert report["server"]["frontend_index_loaded"] is True
    assert report["server"]["frontend_asset_loaded"] is True
    assert report["provider"]["test"]["network_call_made"] is False
    assert report["provider"]["test"]["provider_ready"] is True
    assert report["runtime_data"]["synthetic_smoke_only"] is True
    assert report["runtime_data"]["record_paths"]["weekly_notes"]
    assert report["runtime_data"]["record_paths"]["weekly_reviews"]
    assert report["runtime_data"]["record_paths"]["calibration_records"]
    assert report["backup"]["secrets_included"] is False
    assert report["p6_behavior_validated"] is False
    assert report["p6_sealed"] is False


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = run_smoke(Path(args.deb).expanduser().resolve(), keep_temp=args.keep_temp)
    if args.evidence:
        Path(args.evidence).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"status={report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
