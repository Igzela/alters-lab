"""CLI tests for P7 local launcher."""

from __future__ import annotations

import json

from alters_lab import cli


def test_cli_parser_has_expected_commands():
    parser = cli.build_parser()
    for command in ("start", "stop", "status", "open", "doctor", "backup"):
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


def test_cli_backup_dry_run_json_excludes_secrets(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    assert cli.main(["backup", "--mode", "dev", "--dry-run", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)

    assert data["status"] == "planned"
    assert data["dry_run"] is True
    assert data["secrets_included"] is False
    assert "secrets" in data["excluded_sections"]
    assert data["p6_behavior_validated"] is False
    assert data["p6_sealed"] is False


def test_cli_backup_include_secrets_without_confirmation_blocks(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)

    assert cli.main(["backup", "--mode", "dev", "--dry-run", "--include-secrets", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)

    assert data["status"] == "blocked"
    assert "include_secrets requires confirmation" in data["reason"]
    assert data["p6_behavior_validated"] is False
    assert data["p6_sealed"] is False


def test_cli_doctor_json_includes_checks_list(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("alters_lab.services.local_launcher.is_port_available", lambda host, port: True)

    assert cli.main(["doctor", "--mode", "dev", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)

    assert isinstance(data["checks"], list)
    assert len(data["checks"]) >= 10
    check_names = {c["name"] for c in data["checks"]}
    assert "runtime_layout_resolves" in check_names
    assert "provider_configured" in check_names
    assert "secrets_file" in check_names


def test_cli_doctor_json_never_includes_api_key(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("alters_lab.services.local_launcher.is_port_available", lambda host, port: True)

    assert cli.main(["doctor", "--mode", "dev", "--json"]) == 0
    raw = capsys.readouterr().out

    assert "sk-" not in raw
    assert "api_key" not in raw


def test_cli_doctor_json_reports_provider_mode(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("alters_lab.services.local_launcher.is_port_available", lambda host, port: True)

    assert cli.main(["doctor", "--mode", "dev", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)

    assert "provider_mode" in data["launcher_status"]


def test_cli_doctor_json_reports_p6_flags_false(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("alters_lab.services.local_launcher.is_port_available", lambda host, port: True)

    assert cli.main(["doctor", "--mode", "dev", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)

    assert data["launcher_status"]["p6_behavior_validated"] is False
    assert data["launcher_status"]["p6_sealed"] is False


def test_cli_doctor_text_output(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("alters_lab.services.runtime_layout.get_repo_root", lambda: tmp_path)
    monkeypatch.setattr("alters_lab.services.local_launcher.is_port_available", lambda host, port: True)

    assert cli.main(["doctor", "--mode", "dev"]) == 0
    output = capsys.readouterr().out

    assert "status=" in output
    assert "checks=" in output
