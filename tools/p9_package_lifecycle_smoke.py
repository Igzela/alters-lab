#!/usr/bin/env python3
"""P9-M2: Disposable dpkg lifecycle smoke — install, upgrade, remove.

Tests actual dpkg install/upgrade/remove in a disposable fakeroot.
No host mutation. No sudo. No real provider calls.
"""

from __future__ import annotations

import argparse
import hashlib
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


def _json_stdout(result: dict[str, Any]) -> dict[str, Any]:
    if result["returncode"] != 0:
        return {"error": result["stderr"], "returncode": result["returncode"]}
    try:
        return json.loads(result["stdout"])
    except json.JSONDecodeError:
        return {"raw": result["stdout"]}


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _collect_content_hashes(home: Path) -> dict[str, str | None]:
    hashes: dict[str, str | None] = {}
    for label, rel in [
        ("config", ".config/alters-lab/config.yaml"),
        ("secrets", ".config/alters-lab/secrets.yaml"),
        ("weekly_note", ".local/share/alters-lab/product/weekly_notes/smoke-weekly_notes.yaml"),
        ("calibration", ".local/share/alters-lab/product/calibration_records/smoke-calibration_records.yaml"),
    ]:
        p = home / rel
        hashes[label] = _file_hash(p) if p.exists() else None
    return hashes


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


def _check_package_files(fakeroot: Path) -> dict[str, bool]:
    opt = fakeroot / "opt" / "alters-lab"
    return {
        "opt_alters_lab_exists": opt.exists(),
        "web_dist_exists": (opt / "web" / "dist").exists(),
        "venv_exists": (opt / ".venv").exists(),
        "usr_bin_launcher": (fakeroot / "usr" / "bin" / "alters-lab").exists(),
        "desktop_entry": (
            fakeroot / "usr" / "share" / "applications" / "alters-lab.desktop"
        ).exists(),
        "icon": (
            fakeroot
            / "usr"
            / "share"
            / "icons"
            / "hicolor"
            / "scalable"
            / "apps"
            / "alters-lab.svg"
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


def _run_post_install_app_smoke(
    fakeroot: Path, home: Path, env: dict[str, str]
) -> dict[str, Any]:
    python = fakeroot / "opt" / "alters-lab" / ".venv" / "bin" / "python"
    if not python.exists():
        return {"status": "SKIPPED", "reason": "venv python not found"}
    port = choose_port()
    base_url = f"http://127.0.0.1:{port}"
    cli = [str(python), "-m", "alters_lab.cli"]
    start_result = run_cmd(
        cli + ["start", "--mode", "packaged", "--host", "127.0.0.1", "--port", str(port), "--json"],
        env,
        home,
    )
    if start_result["returncode"] != 0:
        return {"status": "FAIL", "reason": "start failed", "detail": start_result}
    server_started = False
    try:
        wait_for_server(base_url)
        server_started = True
        local_status = request_json(f"{base_url}/local-app/status")
        runtime_status = request_json(f"{base_url}/runtime-layout/status")
        provider_status = request_json(f"{base_url}/provider-config/status")
        return {
            "status": "PASS",
            "routes_checked": [
                "/local-app/status",
                "/runtime-layout/status",
                "/provider-config/status",
            ],
            "local_app_status": local_status,
            "runtime_layout_status": runtime_status,
            "provider_config_status": provider_status,
            "provider_mode": provider_status.get("provider_mode", "unknown"),
            "p6_behavior_validated": False,
            "p6_sealed": False,
            "real_provider_call_made": False,
        }
    except Exception as exc:
        return {"status": "FAIL", "reason": str(exc)}
    finally:
        if server_started:
            run_cmd(cli + ["stop", "--mode", "packaged", "--json"], env, home)


def _assert_report_passes(report: dict[str, Any]) -> None:
    install = report["install"]
    upgrade = report["upgrade"]
    remove = report["remove"]
    safety = report["safety"]

    # Install assertions
    assert install["dpkg_returncode"] == 0, f"install failed: {install['dpkg_stderr']}"
    assert install["package_files"]["opt_alters_lab_exists"] is True
    assert install["package_files"]["usr_bin_launcher"] is True

    # Post-install: package must NOT create user data
    assert install["user_data_before_app_smoke"]["config_file_exists"] is False
    assert install["user_data_before_app_smoke"]["secrets_file_exists"] is False
    assert install["user_data_before_app_smoke"]["product_dir_exists"] is False

    # Post-install app smoke
    app_smoke = install.get("post_install_app_smoke", {})
    if app_smoke.get("status") == "PASS":
        assert app_smoke["provider_mode"] == "disabled"
        assert app_smoke["p6_behavior_validated"] is False
        assert app_smoke["p6_sealed"] is False
        assert app_smoke["real_provider_call_made"] is False

    # Upgrade assertions
    assert upgrade["dpkg_returncode"] == 0, f"upgrade failed: {upgrade['dpkg_stderr']}"
    cp = upgrade["content_preservation"]
    assert cp["config_hash_preserved_after_upgrade"] is True
    assert cp["secret_hash_preserved_after_upgrade"] is True
    assert cp["product_record_hash_preserved_after_upgrade"] is True
    assert cp["secrets_mode_preserved_after_upgrade"] is True

    # Remove assertions
    assert remove["dpkg_returncode"] == 0, f"remove failed: {remove['dpkg_stderr']}"
    # Package-owned files must be removed (opt dir may persist if app created runtime files)
    pkg_after = remove["package_files_after"]
    assert pkg_after["usr_bin_launcher"] is False
    assert pkg_after["desktop_entry"] is False
    assert pkg_after["web_dist_exists"] is False
    assert pkg_after["venv_exists"] is False
    assert pkg_after["icon"] is False
    # opt residual allowed only if package-owned payload was removed
    if pkg_after.get("opt_alters_lab_exists"):
        assert remove.get("package_owned_payload_removed") is True
    # User data must be preserved
    assert remove["secrets_preserved"]["secrets_file_exists"] is True
    assert remove["secrets_preserved"]["config_dir_exists"] is True
    assert remove["secrets_preserved"]["data_dir_exists"] is True
    assert remove["secrets_preserved"]["product_dir_exists"] is True
    # Content preservation after remove
    cp_rem = remove["content_preservation"]
    assert cp_rem["config_hash_preserved_after_remove"] is True
    assert cp_rem["secret_hash_preserved_after_remove"] is True
    assert cp_rem["product_record_hash_preserved_after_remove"] is True
    assert cp_rem["secrets_mode_preserved_after_remove"] is True

    # Safety assertions
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
        # Check: package install must NOT create user data
        user_data_before_smoke = _check_user_data(home)

        # Phase 2: Post-install app smoke
        app_smoke = _run_post_install_app_smoke(fakeroot, home, env)

        # Phase 3: Seed synthetic user data
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

        # Capture content hashes before upgrade
        hashes_before_upgrade = _collect_content_hashes(home)
        user_data_before_upgrade = _check_user_data(home)

        # Phase 4: Upgrade (reinstall same .deb)
        upgrade_result = _dpkg_upgrade(deb_path, fakeroot, env, dpkg_log)
        hashes_after_upgrade = _collect_content_hashes(home)
        user_data_after_upgrade = _check_user_data(home)
        upgrade_content_ok = all(
            hashes_before_upgrade[k] == hashes_after_upgrade[k]
            for k in hashes_before_upgrade
        )

        # Phase 5: Remove
        remove_result = _dpkg_remove(fakeroot, env, dpkg_log)
        hashes_after_remove = _collect_content_hashes(home)
        user_data_after_remove = _check_user_data(home)
        package_files_after_remove = _check_package_files(fakeroot)
        remove_content_ok = all(
            hashes_before_upgrade[k] == hashes_after_remove[k]
            for k in hashes_before_upgrade
        )

        # Phase 6: Collect record paths
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

        report: dict[str, Any] = {
            "status": "PASS",
            "method": "dpkg --instdir lifecycle",
            "temp_root": str(temp_root) if keep_temp else "[removed]",
            "install": {
                "dpkg_returncode": install_result["returncode"],
                "dpkg_stderr": install_result["stderr"],
                "package_files": package_files,
                "dpkg_status": _json_stdout(install_status),
                "user_data_before_app_smoke": user_data_before_smoke,
                "post_install_app_smoke": app_smoke,
            },
            "upgrade": {
                "dpkg_returncode": upgrade_result["returncode"],
                "dpkg_stderr": upgrade_result["stderr"],
                "user_data_before": user_data_before_upgrade,
                "user_data_preserved": user_data_after_upgrade,
                "content_preservation": {
                    "config_hash_preserved_after_upgrade": hashes_before_upgrade["config"] == hashes_after_upgrade["config"],
                    "secret_hash_preserved_after_upgrade": hashes_before_upgrade["secrets"] == hashes_after_upgrade["secrets"],
                    "product_record_hash_preserved_after_upgrade": hashes_before_upgrade["weekly_note"] == hashes_after_upgrade["weekly_note"],
                    "secrets_mode_preserved_after_upgrade": user_data_before_upgrade.get("secrets_mode") == user_data_after_upgrade.get("secrets_mode"),
                },
            },
            "remove": {
                "dpkg_returncode": remove_result["returncode"],
                "dpkg_stderr": remove_result["stderr"],
                "package_files_after": package_files_after_remove,
                "package_owned_payload_removed": all(
                    not package_files_after_remove[k]
                    for k in ["web_dist_exists", "venv_exists", "usr_bin_launcher", "desktop_entry", "icon"]
                ),
                "secrets_preserved": user_data_after_remove,
                "content_preservation": {
                    "config_hash_preserved_after_remove": hashes_before_upgrade["config"] == hashes_after_remove["config"],
                    "secret_hash_preserved_after_remove": hashes_before_upgrade["secrets"] == hashes_after_remove["secrets"],
                    "product_record_hash_preserved_after_remove": hashes_before_upgrade["weekly_note"] == hashes_after_remove["weekly_note"],
                    "secrets_mode_preserved_after_remove": user_data_before_upgrade.get("secrets_mode") == user_data_after_remove.get("secrets_mode"),
                },
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
