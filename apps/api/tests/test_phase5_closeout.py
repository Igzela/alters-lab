"""Tests for P5-M7 Phase 5 Closeout service."""

from __future__ import annotations

import os

from alters_lab.schemas.phase5_closeout import (
    CloseoutCheck,
    CloseoutSummary,
    Phase5CloseoutReportResponse,
)
from alters_lab.services.phase5_closeout import (
    build_phase5_closeout_report,
    write_phase5_closeout_artifacts,
    _check_provider_gateway_default_safe,
    _check_provider_dialogue_no_default_persist,
)


def test_provider_gateway_default_safe():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ.pop("ALTERS_PROVIDER_MODE", None)
        check = _check_provider_gateway_default_safe()
        assert check.status == "PASS"
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_provider_dialogue_no_default_persist():
    check = _check_provider_dialogue_no_default_persist()
    assert check.status == "PASS"


def test_build_report():
    r = build_phase5_closeout_report()
    assert isinstance(r, Phase5CloseoutReportResponse)
    assert r.status in ("PASS", "PASS_WITH_NOTES", "FAIL")
    assert isinstance(r.summary, CloseoutSummary)
    assert r.summary.sealed_baseline_candidate is True
    assert len(r.checks) > 0
    for check in r.checks:
        assert isinstance(check, CloseoutCheck)
        assert check.status in ("PASS", "FAIL", "NOTE")
        assert check.severity in ("critical", "warning", "info")


def test_summary_counts():
    r = build_phase5_closeout_report()
    s = r.summary
    assert s.total_checks == s.passed + s.failed + s.notes


def test_write_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.services.phase5_closeout._get_repo_root", lambda: tmp_path)
    report = build_phase5_closeout_report()
    result = write_phase5_closeout_artifacts(report)
    assert "harness" in result
    evidence_path = tmp_path / "docs" / "harness" / "PHASE5_CLOSEOUT_EVIDENCE.json"
    final_path = tmp_path / "docs" / "harness" / "P5_FINAL_EVIDENCE.json"
    assert evidence_path.exists()
    assert final_path.exists()
