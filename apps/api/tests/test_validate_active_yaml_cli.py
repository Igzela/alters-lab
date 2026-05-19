import hashlib
import json
from pathlib import Path

import pytest

from alters_lab.cli.validate_active_yaml import (
    _artifacts_checked,
    is_forbidden_output_path,
    main,
)
from alters_lab.loaders import default_project_root


def _project_root() -> Path:
    return default_project_root()


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- module imports ---


def test_cli_module_imports():
    from alters_lab.cli import validate_active_yaml
    assert hasattr(validate_active_yaml, "main")
    assert hasattr(validate_active_yaml, "is_forbidden_output_path")


# --- main([]) returns 0 on sealed baseline ---


def test_main_returns_0_on_sealed_baseline():
    exit_code = main([])
    assert exit_code == 0


# --- --json prints valid JSON with ok=true and status=PASS ---


def test_json_output_valid_json(capsys):
    exit_code = main(["--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["ok"] is True
    assert report["status"] == "PASS"
    assert report["report_id"] == "ACTIVE-YAML-VALIDATION"
    assert report["schema_version"] == 1


# --- --output writes report to tmp_path only when explicitly requested ---


def test_output_writes_report_to_tmp_path(tmp_path):
    out_file = tmp_path / "report.json"
    exit_code = main(["--output", str(out_file)])
    assert exit_code == 0
    assert out_file.exists()
    report = json.loads(out_file.read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["status"] == "PASS"


# --- --output under alters/current is rejected ---


def test_output_under_alters_current_rejected(capsys):
    root = _project_root()
    forbidden = root / "alters" / "current" / "report.json"
    exit_code = main(["--output", str(forbidden)])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "forbidden" in captured.err.lower()


def test_output_under_alters_calibration_rejected(capsys):
    root = _project_root()
    forbidden = root / "alters" / "calibration" / "report.json"
    exit_code = main(["--output", str(forbidden)])
    assert exit_code == 2


def test_output_under_alters_archive_rejected(capsys):
    root = _project_root()
    forbidden = root / "alters" / "archive" / "report.json"
    exit_code = main(["--output", str(forbidden)])
    assert exit_code == 2


# --- --project-root works when pointed at repo root ---


def test_project_root_flag(tmp_path, capsys):
    root = _project_root()
    exit_code = main(["--project-root", str(root), "--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["ok"] is True


# --- report includes 9 artifacts_checked ---


def test_report_has_9_artifacts_checked(capsys):
    main(["--json"])
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert len(report["artifacts_checked"]) == 9


# --- report summary selected_branch == branch_D ---


def test_report_summary_selected_branch(capsys):
    main(["--json"])
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["summary"]["selected_branch"] == "branch_D"


# --- report summary primary_candidate == branch_D ---


def test_report_summary_primary_candidate(capsys):
    main(["--json"])
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["summary"]["primary_candidate"] == "branch_D"


# --- report boundary_confirmations.read_only_validation is true ---


def test_report_boundary_read_only_validation(capsys):
    main(["--json"])
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["boundary_confirmations"]["read_only_validation"] is True


# --- CLI does not modify active YAML ---


def test_cli_does_not_modify_snapshot_yaml():
    path = _project_root() / "alters" / "current" / "snapshot.yaml"
    h = _hash_file(path)
    main([])
    assert _hash_file(path) == h


def test_cli_does_not_modify_branches_yaml():
    path = _project_root() / "alters" / "current" / "branches.yaml"
    h = _hash_file(path)
    main([])
    assert _hash_file(path) == h


def test_cli_does_not_modify_reality_trace_yaml():
    path = _project_root() / "alters" / "current" / "reality_trace.yaml"
    h = _hash_file(path)
    main([])
    assert _hash_file(path) == h


# --- CLI does not create score_*.yaml ---


def test_cli_does_not_create_score_files():
    cal_dir = _project_root() / "alters" / "calibration" / "scores"
    before = set(cal_dir.glob("score_*.yaml")) if cal_dir.exists() else set()
    main([])
    after = set(cal_dir.glob("score_*.yaml")) if cal_dir.exists() else set()
    assert after == before


# --- CLI does not create alters/archive/20* folders ---


def test_cli_does_not_create_archive_folders():
    archive_dir = _project_root() / "alters" / "archive"
    before = set(archive_dir.glob("20*")) if archive_dir.exists() else set()
    main([])
    after = set(archive_dir.glob("20*")) if archive_dir.exists() else set()
    assert after == before


# --- is_forbidden_output_path ---


def test_is_forbidden_output_path_true_for_current(tmp_path):
    root = _project_root()
    assert is_forbidden_output_path(root / "alters" / "current" / "x.json", root) is True


def test_is_forbidden_output_path_true_for_calibration(tmp_path):
    root = _project_root()
    assert is_forbidden_output_path(root / "alters" / "calibration" / "x.json", root) is True


def test_is_forbidden_output_path_true_for_archive(tmp_path):
    root = _project_root()
    assert is_forbidden_output_path(root / "alters" / "archive" / "x.json", root) is True


def test_is_forbidden_output_path_false_for_docs(tmp_path):
    root = _project_root()
    assert is_forbidden_output_path(tmp_path / "report.json", root) is False


# --- --strict treats warnings as failure ---


def test_strict_with_no_warnings_passes():
    # Sealed baseline has no warnings, so --strict still passes
    exit_code = main(["--strict"])
    assert exit_code == 0
