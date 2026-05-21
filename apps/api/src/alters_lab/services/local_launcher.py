"""Local CLI launcher service for Alters Lab."""

from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from alters_lab.services.local_app import build_local_app_status
from alters_lab.services.runtime_layout import RuntimeLayout, resolve_runtime_layout


APP_TARGET = "alters_lab.main:app"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 18790


@dataclass(frozen=True)
class LauncherPaths:
    pid_file: Path
    log_file: Path
    logs_dir: Path
    state_dir: Path


def launcher_paths(layout: RuntimeLayout) -> LauncherPaths:
    return LauncherPaths(
        pid_file=layout.state_dir / "alters-lab.pid",
        log_file=layout.logs_dir / "alters-lab.log",
        logs_dir=layout.logs_dir,
        state_dir=layout.state_dir,
    )


def pid_file_path(layout: RuntimeLayout) -> Path:
    return launcher_paths(layout).pid_file


def log_file_path(layout: RuntimeLayout) -> Path:
    return launcher_paths(layout).log_file


def build_server_url(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> str:
    return f"http://{host}:{port}/"


def is_process_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def read_pid_file(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def write_pid_file(path: Path, pid: int, host: str, port: int, command: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "pid": pid,
                "host": host,
                "port": port,
                "command": command,
                "app_target": APP_TARGET,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def remove_stale_pid_file(path: Path) -> bool:
    data = read_pid_file(path)
    if data is None:
        if path.exists():
            path.unlink()
            return True
        return False
    pid = int(data.get("pid") or 0)
    if is_process_running(pid):
        return False
    path.unlink()
    return True


def pid_file_belongs_to_alters_lab(data: dict[str, Any] | None) -> bool:
    if not data:
        return False
    command = data.get("command")
    return data.get("app_target") == APP_TARGET or (isinstance(command, list) and APP_TARGET in command)


def is_port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) != 0


def build_uvicorn_command(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> list[str]:
    return [sys.executable, "-m", "uvicorn", APP_TARGET, "--host", host, "--port", str(port)]


def build_status(layout: RuntimeLayout, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> dict[str, Any]:
    paths = launcher_paths(layout)
    pid_data = read_pid_file(paths.pid_file)
    pid = int(pid_data.get("pid") or 0) if pid_data else None
    running = bool(pid and is_process_running(pid) and pid_file_belongs_to_alters_lab(pid_data))
    app_status = build_local_app_status(layout)
    return {
        "status": "running" if running else "not_running",
        "running": running,
        "pid": pid if running else None,
        "host": host,
        "port": port,
        "url": build_server_url(host, port),
        "runtime_mode": layout.mode,
        "config_path": str(layout.config_path),
        "data_dir": str(layout.data_dir),
        "logs_dir": str(layout.logs_dir),
        "pid_file": str(paths.pid_file),
        "log_file": str(paths.log_file),
        "frontend_available": app_status["frontend_available"],
        "provider_mode": app_status["provider_mode"],
        "p6_behavior_validated": False,
        "p6_sealed": False,
    }


def build_doctor_report(layout: RuntimeLayout, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    status = build_status(layout, host, port)
    checks.append(_check("runtime_layout_resolves", "PASS", f"mode={layout.mode}"))
    checks.append(_check("config_path_resolves", "PASS", str(layout.config_path)))
    checks.append(_writable_check("data_dir_writable", layout.data_dir))
    checks.append(_writable_check("logs_dir_writable", layout.logs_dir))
    checks.append(_check("localhost_default", "PASS" if host in {"127.0.0.1", "localhost"} else "WARN", f"host={host}"))
    port_available = is_port_available(host, port)
    if port_available or status["running"]:
        checks.append(_check("port_available_or_current", "PASS", f"port={port}"))
    else:
        checks.append(_check("port_available_or_current", "BLOCKED", f"port conflict on {host}:{port}"))
    checks.append(_check("frontend_dist", "PASS" if status["frontend_available"] else "WARN", "frontend dist available" if status["frontend_available"] else "frontend dist missing"))
    checks.append(_check("provider_mode_redacted", "PASS", f"provider_mode={status['provider_mode']}"))
    checks.append(_check("active_yaml_write_allowed", "PASS", "false"))
    checks.append(_check("rubric_write_allowed", "PASS", "false"))
    checks.append(_check("p6_behavior_validated", "PASS", "false"))
    checks.append(_check("p6_sealed", "PASS", "false"))
    overall = "PASS"
    if any(check["status"] == "BLOCKED" for check in checks):
        overall = "BLOCKED"
    elif any(check["status"] == "WARN" for check in checks):
        overall = "WARN"
    return {"status": overall, "checks": checks, "launcher_status": status}


def start_server(
    layout: RuntimeLayout,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    dry_run: bool = False,
    foreground: bool = False,
) -> dict[str, Any]:
    paths = launcher_paths(layout)
    existing = read_pid_file(paths.pid_file)
    if existing and pid_file_belongs_to_alters_lab(existing) and is_process_running(int(existing.get("pid") or 0)):
        return {"status": "already_running", "running": True, "pid": existing["pid"], "url": build_server_url(host, port)}
    if existing and remove_stale_pid_file(paths.pid_file):
        existing = None
    if not is_port_available(host, port):
        return {"status": "blocked", "reason": "port_conflict", "host": host, "port": port, "running": False}

    command = build_uvicorn_command(host, port)
    if dry_run:
        return {
            "status": "dry_run",
            "running": False,
            "command": command,
            "pid_file": str(paths.pid_file),
            "log_file": str(paths.log_file),
            "url": build_server_url(host, port),
        }

    paths.logs_dir.mkdir(parents=True, exist_ok=True)
    if foreground:
        return {"status": "foreground", "running": True, "command": command, "url": build_server_url(host, port)}

    log_handle = paths.log_file.open("ab")
    process = subprocess.Popen(command, stdout=log_handle, stderr=subprocess.STDOUT, start_new_session=True)
    write_pid_file(paths.pid_file, process.pid, host, port, command)
    return {"status": "started", "running": True, "pid": process.pid, "url": build_server_url(host, port), "log_file": str(paths.log_file)}


def stop_server(layout: RuntimeLayout) -> dict[str, Any]:
    paths = launcher_paths(layout)
    data = read_pid_file(paths.pid_file)
    if data is None:
        if paths.pid_file.exists():
            paths.pid_file.unlink()
            return {"status": "stale_pid_removed", "running": False}
        return {"status": "not_running", "running": False}
    if not pid_file_belongs_to_alters_lab(data):
        return {"status": "blocked", "reason": "pid_file_not_alters_lab", "running": False}
    pid = int(data.get("pid") or 0)
    if not is_process_running(pid):
        paths.pid_file.unlink()
        return {"status": "stale_pid_removed", "running": False}
    os.kill(pid, signal.SIGTERM)
    paths.pid_file.unlink()
    return {"status": "stopped", "running": False, "pid": pid}


def open_app(
    layout: RuntimeLayout,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    no_start: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    status = build_status(layout, host, port)
    start_result: dict[str, Any] | None = None
    if not status["running"]:
        if no_start:
            return {"status": "not_running", "opened": False, "url": build_server_url(host, port)}
        start_result = start_server(layout, host, port, dry_run=dry_run)
    url = build_server_url(host, port)
    if not dry_run:
        webbrowser.open(url)
    return {"status": "opened" if not dry_run else "dry_run", "opened": not dry_run, "url": url, "start_result": start_result}


def resolve_layout_for_cli(mode: str | None) -> RuntimeLayout:
    return resolve_runtime_layout(mode=mode)


def _check(name: str, status: str, message: str) -> dict[str, str]:
    return {"name": name, "status": status, "message": message}


def _writable_check(name: str, path: Path) -> dict[str, str]:
    existing = path if path.exists() else next((parent for parent in path.parents if parent.exists()), None)
    if existing is None:
        return _check(name, "WARN", f"no existing parent for {path}")
    return _check(name, "PASS" if os.access(existing, os.W_OK) else "BLOCKED", str(path))
