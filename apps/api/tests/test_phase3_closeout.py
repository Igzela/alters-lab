"""Tests for Phase 3 Closeout Gate service."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from alters_lab.schemas.phase3_closeout import (
    Phase3CloseoutBoundaryConfirmations,
    Phase3CloseoutCheck,
    Phase3CloseoutReport,
    Phase3CloseoutSummary,
)
from alters_lab.services.phase3_closeout import (
    build_phase3_closeout_report,
    check_active_yaml_chain,
    check_live_execution_default_safe,
    check_no_raw_audit_logs_committed,
    check_no_runtime_artifacts_committed,
    check_p3_m7_semantic_noop_evidence,
    check_phase3_evidence_files,
    check_phase3_governance_status,
    check_raw_dict_repersist_path_exists,
    check_smuggling_boundary_restored,
    get_repo_root,
    phase3_closeout_boundary_confirmations,
    write_phase3_closeout_artifacts,
)


def test_boundary_confirmations_read_only():
    bc = phase3_closeout_boundary_confirmations()
    assert bc["read_only"] is True
    assert bc["active_yaml_modified"] is False
    assert bc["controlled_persist_called"] is False
    assert bc["live_execution_called"] is False


def test_get_repo_root():
    root = get_repo_root()
    assert root.exists()
    assert (root / "apps").exists()


def test_check_active_yaml_chain():
    check = check_active_yaml_chain()
    assert isinstance(check, Phase3CloseoutCheck)
    assert check.name == "active_yaml_chain"
    assert check.status in ("PASS", "FAIL")


def test_check_smuggling_boundary_restored():
    check = check_smuggling_boundary_restored()
    assert check.name == "smuggling_boundary_restored"
    assert check.status == "PASS"


def test_check_raw_dict_repersist_path_exists():
    check = check_raw_dict_repersist_path_exists()
    assert check.name == "raw_dict_repersist_path_exists"
    assert check.status == "PASS"


def test_check_live_execution_default_safe():
    check = check_live_execution_default_safe()
    assert check.name == "live_execution_default_safe"
    assert check.status == "PASS"


def test_check_phase3_evidence_files(tmp_path):
    check = check_phase3_evidence_files(tmp_path)
    assert check.name == "phase3_evidence_files"
    assert check.status == "FAIL"


def test_check_phase3_evidence_files_with_files(tmp_path):
    harness = tmp_path / "docs" / "harness"
    harness.mkdir(parents=True)
    for name in [
        "P3_M7_LIVE_PROMOTION_EVIDENCE.json",
        "PROJECT_BOARD.md",
        "TASK_QUEUE.md",
        "DECISION_RECORD.md",
        "RUN_LOG.md",
        "EVIDENCE_INDEX.md",
    ]:
        (harness / name).write_text("test")
    check = check_phase3_evidence_files(tmp_path)
    assert check.status == "PASS"


def test_check_p3_m7_semantic_noop_evidence(tmp_path):
    check = check_p3_m7_semantic_noop_evidence(tmp_path)
    assert check.status == "FAIL"
    assert "not found" in check.message


def test_check_p3_m7_semantic_noop_evidence_valid(tmp_path):
    harness = tmp_path / "docs" / "harness"
    harness.mkdir(parents=True)
    evidence = {
        "verdict": "PASS",
        "semantic_noop_result": "PASS",
        "active_chain_validation": "PASS",
        "tests": {"result": "PASS"},
        "raw_token_committed": False,
        "raw_audit_committed": False,
        "runtime_drafts_committed": False,
        "boundary_confirmations": {
            "first_controlled_live_promotion_run_completed": True,
            "promotion_was_semantic_noop": True,
        },
    }
    (harness / "P3_M7_LIVE_PROMOTION_EVIDENCE.json").write_text(json.dumps(evidence))
    check = check_p3_m7_semantic_noop_evidence(tmp_path)
    assert check.status == "PASS"


def test_check_no_runtime_artifacts_committed(tmp_path):
    check = check_no_runtime_artifacts_committed(tmp_path)
    assert check.status == "PASS"


def test_check_no_runtime_artifacts_with_drafts(tmp_path):
    drafts = tmp_path / "alters" / "drafts" / "draft_001"
    drafts.mkdir(parents=True)
    (drafts / "test.yaml").write_text("test")
    check = check_no_runtime_artifacts_committed(tmp_path)
    assert check.status == "WARN"


def test_check_no_raw_audit_logs_committed(tmp_path):
    check = check_no_raw_audit_logs_committed(tmp_path)
    assert check.status == "PASS"


def test_check_no_raw_audit_logs_with_local_audit(tmp_path):
    """Local untracked audit file returns WARN, not FAIL."""
    harness = tmp_path / "docs" / "harness"
    harness.mkdir(parents=True)
    (harness / "test_audit.jsonl").write_text("test")
    check = check_no_raw_audit_logs_committed(tmp_path)
    assert check.status == "WARN"
    assert check.severity == "warning"


def test_check_no_raw_audit_logs_with_tracked_audit(tmp_path, monkeypatch):
    """Tracked audit file returns FAIL."""
    import subprocess

    harness = tmp_path / "docs" / "harness"
    harness.mkdir(parents=True)
    (harness / "test_audit.jsonl").write_text("test")

    def fake_run(cmd, **kwargs):
        class FakeResult:
            returncode = 0
            stdout = "docs/harness/test_audit.jsonl\n"
            stderr = ""
        return FakeResult()

    monkeypatch.setattr(subprocess, "run", fake_run)
    check = check_no_raw_audit_logs_committed(tmp_path)
    assert check.status == "FAIL"
    assert check.severity == "blocking"


def test_check_phase3_governance_status(tmp_path):
    check = check_phase3_governance_status(tmp_path)
    assert check.status == "FAIL"


def test_check_phase3_governance_status_with_files(tmp_path):
    harness = tmp_path / "docs" / "harness"
    harness.mkdir(parents=True)
    (harness / "PROJECT_BOARD.md").write_text("P3-M6R2 done P3-M7 done")
    (harness / "TASK_QUEUE.md").write_text(
        "First Human-Approved Live Promotion Run\nRaw Dict Re-persist Preserves Extras"
    )
    check = check_phase3_governance_status(tmp_path)
    assert check.status == "PASS"


def test_build_closeout_report(tmp_path):
    report = build_phase3_closeout_report(
        repo_root=tmp_path,
        baseline_commit="test123",
        test_count=576,
    )
    assert isinstance(report, Phase3CloseoutReport)
    assert report.baseline_commit == "test123"
    assert report.test_count == 576
    assert report.summary.total_checks == len(report.checks)
    assert report.summary.sealed_baseline_candidate in (True, False)


def test_write_closeout_artifacts(tmp_path):
    report = build_phase3_closeout_report(
        repo_root=tmp_path,
        baseline_commit="test123",
    )
    result = write_phase3_closeout_artifacts(report, tmp_path)
    assert result["status"] == "artifacts_written"
    assert Path(result["report_path"]).exists()
    assert Path(result["evidence_path"]).exists()


def test_write_closeout_artifacts_content(tmp_path):
    report = build_phase3_closeout_report(
        repo_root=tmp_path,
        baseline_commit="test123",
        test_count=576,
    )
    write_phase3_closeout_artifacts(report, tmp_path)
    md = (tmp_path / "docs" / "harness" / "PHASE3_CLOSEOUT_REPORT.md").read_text()
    assert "Phase 3 Controlled Mutation Closeout Report" in md
    assert "test123" in md
    evidence = json.loads(
        (tmp_path / "docs" / "harness" / "PHASE3_CLOSEOUT_EVIDENCE.json").read_text()
    )
    assert evidence["baseline_commit"] == "test123"


def test_closeout_report_schema_extra_forbid():
    with pytest.raises(Exception):
        Phase3CloseoutReport(
            status="PASS",
            baseline_commit="x",
            checks=[],
            summary=Phase3CloseoutSummary(
                status="PASS", total_checks=0, passed_checks=0,
                warning_checks=0, failed_checks=0,
                sealed_baseline_candidate=True, next_phase_status="ok",
            ),
            boundary_confirmations=Phase3CloseoutBoundaryConfirmations(),
            created_at="2026-01-01",
            evil_field=True,
        )
