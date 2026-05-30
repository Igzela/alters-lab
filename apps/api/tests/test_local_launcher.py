"""Service tests for P7 local launcher."""

from __future__ import annotations

import json

from alters_lab.services import local_launcher
from alters_lab.services.local_launcher import (
    APP_TARGET,
    build_doctor_report,
    build_server_url,
    build_status,
    launcher_paths,
    remove_stale_pid_file,
    start_server,
    stop_server,
    write_pid_file,
)
from alters_lab.services.runtime_layout import resolve_runtime_layout


def test_build_server_url_default_localhost():
    assert build_server_url() == "http://127.0.0.1:18790/"


def test_status_not_running_without_pid_file(tmp_path):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)

    status = build_status(layout)

    assert status["running"] is False
    assert status["status"] == "not_running"
    assert status["behavior_validated"] is False
    assert status["p6_sealed"] is False


def test_stale_pid_file_detected_and_removed(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    paths = launcher_paths(layout)
    write_pid_file(paths.pid_file, 999999, "127.0.0.1", 18790, ["python", "-m", "uvicorn", APP_TARGET])
    monkeypatch.setattr(local_launcher, "is_process_running", lambda pid: False)

    assert remove_stale_pid_file(paths.pid_file) is True
    assert not paths.pid_file.exists()


def test_start_dry_run_returns_uvicorn_command(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: True)

    result = start_server(layout, dry_run=True)

    assert result["status"] == "dry_run"
    assert APP_TARGET in result["command"]
    assert "uvicorn" in result["command"]
    assert not launcher_paths(layout).pid_file.exists()


def test_doctor_missing_frontend_is_warn(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: True)

    report = build_doctor_report(layout)

    assert report["status"] == "WARN"
    frontend = [check for check in report["checks"] if check["name"] == "frontend_dist"][0]
    assert frontend["status"] == "WARN"
    assert report["launcher_status"]["behavior_validated"] is False
    assert report["launcher_status"]["p6_sealed"] is False


def test_doctor_port_conflict_blocks(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: False)

    report = build_doctor_report(layout)

    assert report["status"] == "BLOCKED"
    blocked = [check for check in report["checks"] if check["status"] == "BLOCKED"]
    assert any(check["name"] == "port_available_or_current" for check in blocked)


def test_stop_not_running_is_clean(tmp_path):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)

    result = stop_server(layout)

    assert result["status"] == "not_running"
    assert result["running"] is False


def test_stop_cleans_stale_pid(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    paths = launcher_paths(layout)
    write_pid_file(paths.pid_file, 999999, "127.0.0.1", 18790, ["python", "-m", "uvicorn", APP_TARGET])
    monkeypatch.setattr(local_launcher, "is_process_running", lambda pid: False)

    result = stop_server(layout)

    assert result["status"] == "stale_pid_removed"
    assert not paths.pid_file.exists()


def test_stop_blocks_pid_file_not_owned_by_alters(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    paths = launcher_paths(layout)
    paths.pid_file.parent.mkdir(parents=True)
    paths.pid_file.write_text(json.dumps({"pid": 123, "command": ["python", "other.py"]}), encoding="utf-8")
    monkeypatch.setattr(local_launcher, "is_process_running", lambda pid: True)

    result = stop_server(layout)

    assert result["status"] == "blocked"
    assert result["reason"] == "pid_file_not_alters_lab"


def test_packaged_pid_and_log_paths_under_local_state(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    layout = resolve_runtime_layout(mode="packaged")
    paths = launcher_paths(layout)

    assert paths.pid_file == home / ".local" / "state" / "alters-lab" / "alters-lab.pid"
    assert paths.log_file == home / ".local" / "state" / "alters-lab" / "logs" / "alters-lab.log"


def test_dev_pid_and_log_paths_repo_compatible(tmp_path):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    paths = launcher_paths(layout)

    assert paths.pid_file == tmp_path / "alters" / "product" / "state" / "alters-lab.pid"
    assert paths.log_file == tmp_path / "alters" / "product" / "state" / "logs" / "alters-lab.log"


def _find_check(report: dict, name: str) -> dict[str, str]:
    return next(c for c in report["checks"] if c["name"] == name)


def test_doctor_checks_include_runtime_layout(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: True)

    report = build_doctor_report(layout)

    check = _find_check(report, "runtime_layout_resolves")
    assert check["status"] == "PASS"
    assert "mode=dev" in check["message"]


def test_doctor_checks_app_root_exists(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: True)

    report = build_doctor_report(layout)

    check = _find_check(report, "app_root_exists")
    assert check["status"] in ("PASS", "WARN")


def test_doctor_checks_config_exists(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: True)

    report = build_doctor_report(layout)

    check = _find_check(report, "config_exists")
    assert check["status"] in ("PASS", "WARN")


def test_doctor_checks_data_dirs_writable(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: True)

    report = build_doctor_report(layout)

    for name in ("data_dir_writable", "product_data_dir_writable", "logs_dir_writable", "state_dir_writable"):
        check = _find_check(report, name)
        assert check["status"] in ("PASS", "WARN", "BLOCKED")


def test_doctor_checks_provider_configured(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: True)

    report = build_doctor_report(layout)

    check = _find_check(report, "provider_configured")
    assert check["status"] == "PASS"
    assert "no live provider" in check["message"].lower() or "live provider" in check["message"].lower()


def test_doctor_checks_secrets_file(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: True)

    report = build_doctor_report(layout)

    check = _find_check(report, "secrets_file")
    assert check["status"] == "PASS"


def test_doctor_checks_safety_flags(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: True)

    report = build_doctor_report(layout)

    for name in ("active_yaml_write_allowed", "rubric_write_allowed", "behavior_validated", "p6_sealed"):
        check = _find_check(report, name)
        assert check["status"] == "PASS"
        assert check["message"] == "false"


def test_doctor_checks_localhost_default(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: True)

    report = build_doctor_report(layout)

    check = _find_check(report, "localhost_default")
    assert check["status"] == "PASS"
    assert "127.0.0.1" in check["message"]


def test_doctor_never_includes_api_key(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: True)

    report = build_doctor_report(layout)
    report_text = json.dumps(report)

    assert "sk-" not in report_text
    assert "api_key" not in report_text


def test_doctor_warn_actionable_messages(tmp_path, monkeypatch):
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)
    monkeypatch.setattr(local_launcher, "is_port_available", lambda host, port: True)

    report = build_doctor_report(layout)

    for check in report["checks"]:
        if check["status"] == "WARN":
            assert len(check["message"]) > 10, f"check '{check['name']}' WARN message should be actionable"
