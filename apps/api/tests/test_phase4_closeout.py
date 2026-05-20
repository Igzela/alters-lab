"""Tests for Phase 4 Closeout service."""

from __future__ import annotations

from pathlib import Path

from alters_lab.services.phase4_closeout import (
    build_phase4_closeout_report,
    check_no_git_diff,
    check_no_provider_imports,
    check_p4_modules_importable,
    check_p4_m1r_dialogue_contract,
    check_p4_routes_registered,
    phase4_closeout_boundary_confirmations,
    write_phase4_closeout_artifacts,
)


def test_boundary_confirmations_safe():
    bc = phase4_closeout_boundary_confirmations()
    assert bc["active_yaml_modified"] is False
    assert bc["rubric_modified"] is False
    assert bc["provider_used"] is False
    assert bc["frontend_added"] is False
    assert bc["database_added"] is False


def test_closeout_detects_p4_modules_and_routes():
    assert check_p4_modules_importable().status == "PASS"
    assert check_p4_routes_registered().status == "PASS"


def test_dialogue_contract_regression_still_passes():
    assert check_p4_m1r_dialogue_contract().status == "PASS"


def test_no_provider_imports_in_p4_services():
    repo_root = Path(__file__).resolve().parents[3]
    assert check_no_provider_imports(repo_root).status == "PASS"


def test_no_active_yaml_and_rubric_diff_checks_pass():
    repo_root = Path(__file__).resolve().parents[3]
    assert check_no_git_diff(repo_root, "alters/current", "no_active_yaml_diff").status == "PASS"
    assert check_no_git_diff(repo_root, "alters/calibration/rubric.yaml", "no_rubric_yaml_diff").status == "PASS"


def test_write_phase4_closeout_artifacts_to_tmp_path(tmp_path):
    report = build_phase4_closeout_report(repo_root=Path(__file__).resolve().parents[3])
    result = write_phase4_closeout_artifacts(report, tmp_path)
    assert result["status"] == "artifacts_written"
    assert (tmp_path / "docs" / "harness" / "PHASE4_CLOSEOUT_REPORT.md").exists()
    assert (tmp_path / "docs" / "harness" / "PHASE4_CLOSEOUT_EVIDENCE.json").exists()
    assert (tmp_path / "docs" / "harness" / "P4_FINAL_EVIDENCE.json").exists()
