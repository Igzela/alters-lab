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
    assert status["p6_behavior_validated"] is False
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
    assert report["launcher_status"]["p6_behavior_validated"] is False
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
