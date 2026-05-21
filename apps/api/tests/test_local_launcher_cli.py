"""CLI tests for P7 local launcher."""

from __future__ import annotations

import json

from alters_lab import cli


def test_cli_parser_has_expected_commands():
    parser = cli.build_parser()
    for command in ("start", "stop", "status", "open", "doctor"):
        parsed = parser.parse_args([command, "--mode", "dev"])
        assert parsed.command == command


def test_cli_status_json(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    assert cli.main(["status", "--mode", "dev", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)

    assert data["status"] == "not_running"
    assert data["running"] is False


def test_cli_doctor_json(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("alters_lab.services.local_launcher.is_port_available", lambda host, port: True)

    assert cli.main(["doctor", "--mode", "dev", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)

    assert data["status"] in ("PASS", "WARN")
    assert data["launcher_status"]["p6_behavior_validated"] is False
    assert data["launcher_status"]["p6_sealed"] is False


def test_cli_start_dry_run_json(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("alters_lab.services.local_launcher.is_port_available", lambda host, port: True)

    assert cli.main(["start", "--mode", "dev", "--dry-run", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)

    assert data["status"] == "dry_run"
    assert "alters_lab.main:app" in data["command"]


def test_cli_stop_json_not_running(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    assert cli.main(["stop", "--mode", "dev", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)

    assert data["status"] == "not_running"


def test_cli_open_dry_run_uses_expected_url(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("alters_lab.services.local_launcher.is_port_available", lambda host, port: True)
    opened: list[str] = []
    monkeypatch.setattr("webbrowser.open", lambda url: opened.append(url))

    assert cli.main(["open", "--mode", "dev", "--dry-run", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)

    assert data["url"] == "http://127.0.0.1:18790/"
    assert data["status"] == "dry_run"
    assert opened == []
