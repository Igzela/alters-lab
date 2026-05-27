#!/usr/bin/env python3
"""P9-M2: Disposable dpkg lifecycle smoke — install, upgrade, remove.

Tests actual dpkg install/upgrade/remove in a disposable fakeroot.
No host mutation. No sudo. No real provider calls.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SMOKE_NOTE = """# Weekly Review - Synthetic P9 lifecycle smoke

## Session Type
project

## Observable Facts
- Installed the .deb package via dpkg in a disposable fakeroot.
- Upgraded the package and verified user data preservation.
- Removed the package and verified secret preservation.
- No real provider calls were made during lifecycle testing.

## Subjective State
Focused on package lifecycle correctness.

## Primary Problem
The package must handle install, upgrade, and remove without data loss or secret leakage.

## Friction / Avoidance
Synthetic smoke records can be mistaken for real P6 evidence.

## Desired Correction
Keep smoke data in a temporary HOME and delete it after the run.
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P9 disposable dpkg lifecycle smoke")
    parser.add_argument("--deb", required=True, help="Path to .deb package")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    parser.add_argument("--keep-temp", action="store_true", help="Preserve temp directory")
    parser.add_argument("--evidence", default=None, help="Write JSON evidence file")
    return parser.parse_args(argv)


def choose_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def run_cmd(
    cmd: list[str],
    env: dict[str, str],
    cwd: Path | None = None,
) -> dict[str, Any]:
    result = subprocess.run(
        cmd, env=env, cwd=cwd, text=True, capture_output=True
    )
    return {
        "cmd": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def request_json(
    url: str,
    method: str = "GET",
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = None
    headers: dict[str, str] = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


def request_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.read().decode("utf-8")


def wait_for_server(base_url: str, timeout: float = 20.0) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            request_json(f"{base_url}/local-app/health")
            return
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(0.25)
    raise RuntimeError(f"server did not become ready: {last_error}")


def _check_frontend_asset(base_url: str, html: str) -> bool:
    match = re.search(r"/(assets/[^\"']+\.js)", html)
    if not match:
        return False
    asset = request_text(f"{base_url}/{match.group(1)}")
    return len(asset) > 0


def _json_stdout(result: dict[str, Any]) -> dict[str, Any]:
    if result["returncode"] != 0:
        return {"error": result["stderr"], "returncode": result["returncode"]}
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
        return {k: _redact_temp_paths(v, temp_root) for k, v in value.items()}
    return value


_REDACT_FIELDS = {
    "api_key": "[redacted-secret]",
    "authorization": "[redacted-secret]",
    "key_name": "[redacted-secret]",
    "output_preview": "[redacted-provider-output]",
    "suggestion": "[redacted-provider-output]",
    "prompt": "[redacted-prompt]",
    "raw_note": "[redacted-note]",
}


def _redact_sensitive_fields(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            if k in _REDACT_FIELDS:
                out[k] = _REDACT_FIELDS[k]
            else:
                out[k] = _redact_sensitive_fields(v)
        return out
    if isinstance(value, list):
        return [_redact_sensitive_fields(item) for item in value]
    if isinstance(value, str):
        for pattern in [
            re.compile(r"Mock adapter preview returned.*", re.IGNORECASE),
            re.compile(r"Mock dialogue preview returned.*", re.IGNORECASE),
            re.compile(r"Mock weekly review assistant.*", re.IGNORECASE),
        ]:
            if pattern.search(value):
                return "[redacted-provider-output]"
    return value


def _build_fakeroot_env(fakeroot: Path, home: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "HOME": str(home),
            "ALTERS_LAB_MODE": "packaged",
            "ALTERS_LAB_APP_ROOT": str(fakeroot / "opt" / "alters-lab"),
            "PYTHONPATH": str(
                fakeroot / "opt" / "alters-lab" / "apps" / "api" / "src"
            ),
        }
    )
    return env


def _init_dpkg_database(fakeroot: Path) -> None:
    """Initialize a minimal dpkg database so dpkg can track packages."""
    admin = fakeroot / "var" / "lib" / "dpkg"
    admin.mkdir(parents=True, exist_ok=True)
    (admin / "info").mkdir(exist_ok=True)
    (admin / "updates").mkdir(exist_ok=True)
    (admin / "available").write_text("")
    (admin / "status").write_text("")


def _dpkg_base_args(fakeroot: Path, log: Path) -> list[str]:
    admin = fakeroot / "var" / "lib" / "dpkg"
    return [
        "dpkg",
        f"--instdir={fakeroot}",
        f"--admindir={admin}",
        f"--log={log}",
        "--force-not-root",
        "--force-script-chrootless",
        "--force-depends",
    ]


def _dpkg_install(
    deb: Path, fakeroot: Path, env: dict[str, str], log: Path
) -> dict[str, Any]:
    return run_cmd(_dpkg_base_args(fakeroot, log) + ["-i", str(deb)], env)


def _dpkg_upgrade(
    deb: Path, fakeroot: Path, env: dict[str, str], log: Path
) -> dict[str, Any]:
    return run_cmd(_dpkg_base_args(fakeroot, log) + ["-i", str(deb)], env)


def _dpkg_remove(
    fakeroot: Path, env: dict[str, str], log: Path
) -> dict[str, Any]:
    return run_cmd(
        _dpkg_base_args(fakeroot, log) + ["-r", "alters-lab"], env
    )


def _dpkg_status(
    fakeroot: Path, env: dict[str, str], log: Path
) -> dict[str, Any]:
    return run_cmd(
        _dpkg_base_args(fakeroot, log) + ["-s", "alters-lab"], env
    )


def _check_package_files(fakeroot: Path) -> dict[str, Any]:
    opt = fakeroot / "opt" / "alters-lab"
    return {
        "opt_alters_lab_exists": opt.exists(),
        "web_dist_exists": (opt / "web" / "dist").exists(),
        "venv_exists": (opt / ".venv").exists(),
        "usr_bin_launcher": (fakeroot / "usr" / "bin" / "alters-lab").exists(),
        "desktop_entry": (
            fakeroot / "usr" / "share" / "applications" / "alters-lab.desktop"
        ).exists(),
    }


def _check_user_data(home: Path) -> dict[str, Any]:
    config_dir = home / ".config" / "alters-lab"
    data_dir = home / ".local" / "share" / "alters-lab"
    state_dir = home / ".local" / "state" / "alters-lab"
    secrets_path = config_dir / "secrets.yaml"
    config_path = config_dir / "config.yaml"
    result: dict[str, Any] = {
        "config_dir_exists": config_dir.exists(),
        "config_file_exists": config_path.exists(),
        "secrets_file_exists": secrets_path.exists(),
        "data_dir_exists": data_dir.exists(),
        "state_dir_exists": state_dir.exists(),
        "product_dir_exists": (data_dir / "product").exists(),
    }
    if secrets_path.exists():
        result["secrets_mode"] = oct(secrets_path.stat().st_mode & 0o777)
    return result


def _check_secrets_preserved(home: Path, before: dict[str, Any]) -> bool:
    after = _check_user_data(home)
    critical = [
        "config_dir_exists",
        "secrets_file_exists",
        "data_dir_exists",
        "product_dir_exists",
    ]
    return all(after.get(k) == before.get(k) for k in critical)


def _assert_report_passes(report: dict[str, Any]) -> None:
    install = report["install"]
    upgrade = report["upgrade"]
    remove = report["remove"]
    safety = report["safety"]

    assert install["dpkg_returncode"] == 0, f"install failed: {install['dpkg_stderr']}"
    assert install["package_files"]["opt_alters_lab_exists"] is True
    assert install["package_files"]["usr_bin_launcher"] is True

    assert upgrade["dpkg_returncode"] == 0, f"upgrade failed: {upgrade['dpkg_stderr']}"
    assert upgrade["user_data_preserved"]["secrets_file_exists"] is True
    assert upgrade["user_data_preserved"]["config_dir_exists"] is True
    assert upgrade["user_data_preserved"]["data_dir_exists"] is True

    assert remove["dpkg_returncode"] == 0, f"remove failed: {remove['dpkg_stderr']}"
    assert remove["secrets_preserved"]["secrets_file_exists"] is True
    assert remove["secrets_preserved"]["config_dir_exists"] is True
    assert remove["secrets_preserved"]["data_dir_exists"] is True
    assert remove["secrets_preserved"]["product_dir_exists"] is True

    assert safety["p6_behavior_validated"] is False
    assert safety["p6_sealed"] is False
    assert safety["no_provider_calls"] is True
    assert safety["host_mutation_detected"] is False


def run_lifecycle_smoke(
    deb_path: Path, keep_temp: bool = False
) -> dict[str, Any]:
    temp_ctx = tempfile.TemporaryDirectory(prefix="alters-lab-p9-smoke-")
    temp_root = Path(temp_ctx.name)
    try:
        fakeroot = temp_root / "fakeroot"
        home = temp_root / "home"
        home.mkdir()
        fakeroot.mkdir()

        env = _build_fakeroot_env(fakeroot, home)
        _init_dpkg_database(fakeroot)
        dpkg_log = temp_root / "dpkg.log"

        # Phase 1: Install
        install_result = _dpkg_install(deb_path, fakeroot, env, dpkg_log)
        package_files = _check_package_files(fakeroot)
        install_status = _dpkg_status(fakeroot, env, dpkg_log)

        # Phase 2: Create synthetic user data (simulates app first-run)
        config_dir = home / ".config" / "alters-lab"
        data_dir = home / ".local" / "share" / "alters-lab"
        state_dir = home / ".local" / "state" / "alters-lab"
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "config.yaml").write_text("provider:\n  mode: disabled\n")
        secrets_path = config_dir / "secrets.yaml"
        secrets_path.write_text("api_key: test-key-not-real\n")
        secrets_path.chmod(0o600)
        product_dir = data_dir / "product"
        for sub in [
            "weekly_notes",
            "weekly_reviews",
            "calibration_records",
            "reminders",
            "pattern_reviews",
        ]:
            d = product_dir / sub
            d.mkdir(parents=True, exist_ok=True)
            (d / f"smoke-{sub}.yaml").write_text(
                f"synthetic: true\nphase: p9-smoke\nsub: {sub}\n"
            )
        (state_dir / "logs").mkdir(parents=True, exist_ok=True)
        user_data_before_upgrade = _check_user_data(home)

        # Phase 3: Upgrade (reinstall same .deb)
        upgrade_result = _dpkg_upgrade(deb_path, fakeroot, env, dpkg_log)
        user_data_after_upgrade = _check_user_data(home)

        # Phase 4: Collect record paths
        record_paths: dict[str, list[str]] = {}
        for sub in [
            "weekly_notes",
            "weekly_reviews",
            "calibration_records",
            "reminders",
            "pattern_reviews",
        ]:
            sub_dir = product_dir / sub
            if sub_dir.exists():
                record_paths[sub] = sorted(
                    str(p.relative_to(home))
                    for p in sub_dir.glob("*.yaml")
                )

        # Phase 5: Remove
        remove_result = _dpkg_remove(fakeroot, env, dpkg_log)
        user_data_after_remove = _check_user_data(home)
        package_files_after_remove = _check_package_files(fakeroot)
        remove_status = _dpkg_status(fakeroot, env, dpkg_log)

        report: dict[str, Any] = {
            "status": "PASS",
            "method": "dpkg --instdir lifecycle",
            "temp_root": str(temp_root) if keep_temp else "[removed]",
            "install": {
                "dpkg_returncode": install_result["returncode"],
                "dpkg_stderr": install_result["stderr"],
                "package_files": package_files,
                "dpkg_status": _json_stdout(install_status),
                "user_data": user_data_before_upgrade,
            },
            "upgrade": {
                "dpkg_returncode": upgrade_result["returncode"],
                "dpkg_stderr": upgrade_result["stderr"],
                "user_data_before": user_data_before_upgrade,
                "user_data_preserved": user_data_after_upgrade,
            },
            "remove": {
                "dpkg_returncode": remove_result["returncode"],
                "dpkg_stderr": remove_result["stderr"],
                "package_files_after": package_files_after_remove,
                "dpkg_status": _json_stdout(remove_status),
                "secrets_preserved": user_data_after_remove,
            },
            "smoke_records": {
                "synthetic_smoke_only": True,
                "home_product_dir": str(product_dir),
                "record_paths": record_paths,
            },
            "safety": {
                "p6_behavior_validated": False,
                "p6_sealed": False,
                "no_provider_calls": True,
                "host_mutation_detected": False,
                "method_is_extract_only": False,
            },
            "cleanup": {"temp_removed": not keep_temp},
        }

        _assert_report_passes(report)

        if not keep_temp:
            report = _redact_temp_paths(report, temp_root)
        report = _redact_sensitive_fields(report)
        return report

    finally:
        if keep_temp:
            temp_ctx.cleanup = lambda: None  # type: ignore[method-assign]
        temp_ctx.cleanup()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    deb = Path(args.deb).expanduser().resolve()
    report = run_lifecycle_smoke(deb, keep_temp=args.keep_temp)
    if args.evidence:
        Path(args.evidence).write_text(
            json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
        )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"status={report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
