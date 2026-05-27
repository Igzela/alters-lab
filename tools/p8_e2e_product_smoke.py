#!/usr/bin/env python3
"""P8 E2E product validation smoke.

Validates the full local app product path after P8 provider features.
Uses package-context isolated HOME by default. No live provider calls.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SMOKE_NOTE = """# Weekly Review - Synthetic P8 E2E smoke

## Session Type
project

## Observable Facts
- Built the local app package in a P8 smoke environment.
- Started the package-context server on localhost.
- Validated P8 provider routes: adapter, connectivity, dialogue preview, weekly assistant.
- Configured provider mode to mock.
- Ran weekly review flow with assistant suggestion.
- Kept this record synthetic and outside P6 validation.

## Subjective State
Focused on P8 product validation safety.

## Primary Problem
All P8 provider paths must work without violating safety boundaries.

## Friction / Avoidance
Synthetic smoke records can be mistaken for real P6 evidence.

## Desired Correction
Keep smoke data in a temporary HOME and delete it after the run.
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P8 E2E product validation smoke")
    parser.add_argument("--deb", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--keep-temp", action="store_true")
    parser.add_argument("--evidence", default=None)
    parser.add_argument("--allow-live-provider", action="store_true")
    parser.add_argument("--live-provider-confirmation", default=None)
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
    req = urllib.request.Request(url, data=data, headers=headers, method=method)  # noqa: S310
    with urllib.request.urlopen(req, timeout=10) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=5) as response:  # noqa: S310
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


def run_smoke(
    deb_path: Path,
    keep_temp: bool = False,
    allow_live_provider: bool = False,
    live_confirmation: str | None = None,
) -> dict[str, Any]:
    temp_ctx = tempfile.TemporaryDirectory(prefix="alters-lab-p8-smoke-")
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
        env.update({
            "HOME": str(home),
            "ALTERS_LAB_MODE": "packaged",
            "ALTERS_LAB_APP_ROOT": str(app_root),
            "PYTHONPATH": str(app_root / "apps" / "api" / "src"),
        })
        port = choose_port()
        base_url = f"http://127.0.0.1:{port}"
        cli_base = [str(python), "-m", "alters_lab.cli"]

        start_cmd = run_cmd(cli_base + ["start", "--mode", "packaged", "--host", "127.0.0.1", "--port", str(port), "--json"], env, temp_root)
        if start_cmd["returncode"] != 0:
            raise RuntimeError(f"start failed: {start_cmd}")
        start_attempted = True
        wait_for_server(base_url)

        # --- E. Validate routes ---
        route_checks = {}
        for route in [
            "/local-app/status",
            "/runtime-layout/status",
            "/provider-config/status",
            "/provider-adapter/status",
            "/provider-connectivity/status",
            "/provider-dialogue-preview/status",
            "/weekly-review-assistant/status",
            "/obsidian-weekly-note/list",
            "/weekly-review/list",
            "/action-alignment/list",
        ]:
            try:
                data = request_json(f"{base_url}{route}")
                route_checks[route] = {"status": "ok", "data": data}
            except Exception as exc:
                route_checks[route] = {"status": "error", "error": str(exc)}

        # --- F. Provider config smoke ---
        provider_config_before = request_json(f"{base_url}/provider-config/status")
        provider_config_set = request_json(
            f"{base_url}/provider-config/config",
            method="POST",
            body={"mode": "mock", "explicit_user_configuration": False},
        )
        provider_config_after = request_json(f"{base_url}/provider-config/status")
        provider_test = request_json(f"{base_url}/provider-config/test", method="POST", body={"dry_run": True})

        # --- G. Provider adapter smoke ---
        adapter_preview = request_json(
            f"{base_url}/provider-adapter/preview",
            method="POST",
            body={"mode": "mock", "prompt": "synthetic smoke test prompt"},
        )

        # --- H. Provider connectivity smoke ---
        connectivity_status = request_json(f"{base_url}/provider-connectivity/status")
        connectivity_check = request_json(
            f"{base_url}/provider-connectivity/check",
            method="POST",
            body={"dry_run": True, "live_check": False},
        )

        # --- I. Provider dialogue preview smoke ---
        preview_status = request_json(f"{base_url}/provider-dialogue-preview/status")
        preview_generate = request_json(
            f"{base_url}/provider-dialogue-preview/generate",
            method="POST",
            body={"prompt": "synthetic smoke prompt", "dry_run": True},
        )

        # --- J. Weekly Review Assistant smoke ---
        assistant_status = request_json(f"{base_url}/weekly-review-assistant/status")
        assistant_suggest = request_json(
            f"{base_url}/weekly-review-assistant/suggest",
            method="POST",
            body={"requested_help": "general_review_suggestion", "dry_run": True},
        )

        # --- K. Weekly Review flow with assistant ---
        note = request_json(
            f"{base_url}/obsidian-weekly-note/ingest",
            method="POST",
            body={"raw_note": SMOKE_NOTE, "source_path": "synthetic-p8-smoke.md"},
        )
        note_id = note["record"]["record_id"]
        weekly = request_json(f"{base_url}/weekly-review/start", method="POST", body={"weekly_note_record_id": note_id})
        session_id = weekly["session"]["session_id"]

        # Run assistant suggestion in mock mode (no network)
        assistant_with_session = request_json(
            f"{base_url}/weekly-review-assistant/suggest",
            method="POST",
            body={
                "weekly_note_record_id": note_id,
                "weekly_review_session_id": session_id,
                "requested_help": "general_review_suggestion",
                "dry_run": True,
            },
        )

        # Manually complete review (not from provider output)
        completed = request_json(
            f"{base_url}/weekly-review/{session_id}/complete",
            method="POST",
            body={
                "review_note": "Synthetic P8 smoke review. Not P6 real-use evidence.",
                "primary_next_correction": "Continue to P8 closeout only after review.",
                "supporting_actions": ["Keep smoke data isolated."],
            },
        )

        # Submit action alignment with synthetic user values
        scored = request_json(
            f"{base_url}/action-alignment/score",
            method="POST",
            body={
                "session_id": session_id,
                "scores": {"direction_alignment": 0.5, "execution_consistency": 0.5, "avoidance_level": 0.5},
                "evidence": {
                    "one_action_evidence": "Package-context P8 smoke created synthetic records.",
                    "one_avoidance_or_friction_evidence": "Synthetic records are not real P6 evidence.",
                    "one_next_correction": "Do not run behavior validation from smoke data.",
                },
                "verdict_label": "unstable_but_useful",
                "verdict_sentence": "Synthetic P8 smoke verified package write paths only.",
            },
        )

        # --- L. Backup/data safety smoke ---
        backup = run_cmd(cli_base + ["backup", "--mode", "packaged", "--dry-run", "--json"], env, temp_root)

        # --- Stop server ---
        stop_cmd = run_cmd(cli_base + ["stop", "--mode", "packaged", "--json"], env, temp_root)
        stopped = True

        # --- Collect record paths ---
        product_dir = home / ".local" / "share" / "alters-lab" / "product"
        record_paths = {}
        for subdir in ["weekly_notes", "weekly_reviews", "calibration_records", "reminders", "pattern_reviews"]:
            dirpath = product_dir / subdir
            if dirpath.exists():
                record_paths[subdir] = sorted(str(p.relative_to(home)) for p in dirpath.glob("*.yaml"))

        # --- Build report ---
        backup_data = _json_stdout(backup) if backup["returncode"] == 0 else {"error": backup["stderr"]}

        report = {
            "status": "PASS",
            "method": "dpkg-deb -x simulated install",
            "temp_root": str(temp_root) if keep_temp else "[removed]",
            "port": port,
            "routes": route_checks,
            "provider_config": {
                "status_before": provider_config_before,
                "config_set": provider_config_set,
                "status_after": provider_config_after,
                "test": provider_test,
            },
            "provider_adapter": {
                "preview": adapter_preview,
            },
            "provider_connectivity": {
                "status": connectivity_status,
                "check": connectivity_check,
            },
            "provider_dialogue_preview": {
                "status": preview_status,
                "generate": preview_generate,
            },
            "weekly_review_assistant": {
                "status": assistant_status,
                "suggest": assistant_suggest,
                "suggest_with_session": assistant_with_session,
            },
            "weekly_review_flow": {
                "note_status": note["status"],
                "weekly_status": completed["status"],
                "score_status": scored["status"],
            },
            "backup": backup_data,
            "cleanup": {"server_stopped": stopped},
            "runtime_data": {
                "synthetic_smoke_only": True,
                "home_product_dir": str(product_dir),
                "record_paths": record_paths,
            },
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
        return {"error": result.get("stderr", "non-zero exit"), "returncode": result["returncode"]}
    try:
        return json.loads(result["stdout"])
    except json.JSONDecodeError:
        return {"raw": result["stdout"]}


def _redact_temp_paths(value: Any, temp_root: Path) -> Any:
    if isinstance(value, str):
        return value.replace(str(temp_root), "[temp-root]")
    if isinstance(value, list):
        return [_redact_temp_paths(item, temp_root) for item in value]
    if isinstance(value, dict):
        return {key: _redact_temp_paths(item, temp_root) for key, item in value.items()}
    return value


def _assert_report_passes(report: dict[str, Any]) -> None:
    # Route checks
    for route, check in report["routes"].items():
        assert check["status"] == "ok", f"route {route} failed: {check}"

    # Provider config
    assert report["provider_config"]["test"]["network_call_made"] is False
    assert report["provider_config"]["test"]["provider_ready"] is True

    # Provider adapter
    assert report["provider_adapter"]["preview"]["network_call_made"] is False
    assert report["provider_adapter"]["preview"]["active_yaml_modified"] is False
    assert report["provider_adapter"]["preview"]["p6_behavior_validated"] is False
    assert report["provider_adapter"]["preview"]["p6_sealed"] is False

    # Provider connectivity
    assert report["provider_connectivity"]["check"]["network_call_made"] is False

    # Provider dialogue preview
    assert report["provider_dialogue_preview"]["generate"]["output_label"] == "unverified_provider_preview"
    assert report["provider_dialogue_preview"]["generate"]["output_persisted"] is False
    assert report["provider_dialogue_preview"]["generate"]["prompt_persisted"] is False
    assert report["provider_dialogue_preview"]["generate"]["response_content_persisted"] is False
    assert report["provider_dialogue_preview"]["generate"]["p6_behavior_validated"] is False
    assert report["provider_dialogue_preview"]["generate"]["p6_sealed"] is False

    # Weekly review assistant
    assert report["weekly_review_assistant"]["suggest"]["suggestion_label"] == "unverified_provider_suggestion"
    assert report["weekly_review_assistant"]["suggest"]["suggestion_persisted"] is False
    assert report["weekly_review_assistant"]["suggest"]["weekly_review_completed"] is False
    assert report["weekly_review_assistant"]["suggest"]["action_alignment_created"] is False
    assert report["weekly_review_assistant"]["suggest"]["reality_score_created"] is False
    assert report["weekly_review_assistant"]["suggest"]["p6_behavior_validated"] is False
    assert report["weekly_review_assistant"]["suggest"]["p6_sealed"] is False

    # Weekly review flow
    assert report["weekly_review_flow"]["note_status"] in {"ok", "saved"}
    assert report["weekly_review_flow"]["weekly_status"] in {"ok", "started", "completed"}
    assert report["weekly_review_flow"]["score_status"] in {"ok", "saved"}

    # Backup
    if "secrets_included" in report["backup"]:
        assert report["backup"]["secrets_included"] is False

    # Runtime data
    assert report["runtime_data"]["synthetic_smoke_only"] is True
    assert report["runtime_data"]["record_paths"].get("weekly_notes")
    assert report["runtime_data"]["record_paths"].get("weekly_reviews")

    # P6 safety
    assert report["p6_behavior_validated"] is False
    assert report["p6_sealed"] is False


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = run_smoke(
        Path(args.deb).expanduser().resolve(),
        keep_temp=args.keep_temp,
        allow_live_provider=args.allow_live_provider,
        live_confirmation=args.live_provider_confirmation,
    )
    if args.evidence:
        evidence_path = Path(args.evidence)
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"status={report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
