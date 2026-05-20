"""Tests for P4 calibration loop MVP service."""

from __future__ import annotations

import pytest

from alters_lab.schemas.calibration_loop import (
    CalibrationLoopBoundaryConfirmations,
    CalibrationScoreValues,
    DriftCalculationRequest,
    RealityScoreRequest,
)
from alters_lab.services.calibration_loop import (
    build_calibration_history,
    build_reality_score_record,
    calculate_drift,
    calculate_drift_values,
    calibration_boundary_confirmations,
    list_reality_score_records,
    load_reality_score_record,
    score_directory,
    submit_reality_score,
)


def _scores(value: int = 3) -> dict:
    return {
        "execution_discipline": value,
        "exploration_freedom": value,
        "life_state_match": value,
        "energy_level": value,
    }


def _request(**overrides) -> RealityScoreRequest:
    data = {
        "score_id": "score_test_001",
        "branch_id": "branch_A",
        "alter_id": "alter_A",
        "actual_scores": _scores(3),
        "user_notes": "Explicit user check-in.",
        "evidence_refs": ["manual-note"],
    }
    data.update(overrides)
    return RealityScoreRequest(**data)


def test_boundary_confirmations_are_safe():
    bc = calibration_boundary_confirmations()
    assert isinstance(bc, CalibrationLoopBoundaryConfirmations)
    assert bc.active_yaml_modified is False
    assert bc.rubric_modified is False
    assert bc.provider_used is False
    assert bc.frontend_added is False
    assert bc.database_added is False
    assert bc.archive_created is False
    assert bc.regeneration_triggered is False
    assert bc.reality_score_requires_explicit_user_submission is True
    assert bc.drift_evidence_only is True
    assert bc.calibration_history_read_only is True


def test_score_values_reject_out_of_range():
    with pytest.raises(Exception):
        CalibrationScoreValues(**{**_scores(3), "energy_level": 6})
    with pytest.raises(Exception):
        CalibrationScoreValues(**{**_scores(3), "life_state_match": 0})


def test_reality_score_requires_explicit_user_submission():
    with pytest.raises(Exception):
        RealityScoreRequest(
            score_id="score_bad",
            branch_id="branch_A",
            alter_id="alter_A",
            actual_scores=_scores(3),
            submitted_by_user=False,
        )
    with pytest.raises(Exception):
        RealityScoreRequest(
            score_id="score_bad",
            branch_id="branch_A",
            alter_id="alter_A",
            actual_scores=_scores(3),
            source="inferred",
        )


def test_reality_score_rejects_mismatched_alter_branch():
    with pytest.raises(Exception):
        _request(branch_id="branch_B", alter_id="alter_A")


def test_reality_score_rejects_path_score_id():
    with pytest.raises(Exception):
        _request(score_id="../score_bad")


def test_build_reality_score_record_has_no_drift_by_default():
    record = build_reality_score_record(_request(), created_at="2026-05-20T00:00:00+00:00")
    assert record.id == "score_test_001"
    assert record.branch_id == "branch_A"
    assert record.alter_id == "alter_A"
    assert record.drift is None
    assert record.submitted_by_user is True
    assert record.input_refs.alter_ref == "alters/current/alters/alter_A.yaml"
    assert record.boundary_confirmations.active_yaml_modified is False


def test_submit_reality_score_writes_score_record_only(tmp_path):
    status, record, path = submit_reality_score(_request(), tmp_path)
    assert status == "recorded"
    assert record.id == "score_test_001"
    assert path == tmp_path / "alters" / "calibration" / "scores" / "score_test_001.yaml"
    assert path.exists()
    assert not (tmp_path / "alters" / "current").exists()
    loaded = load_reality_score_record(path)
    assert loaded.id == "score_test_001"
    assert loaded.drift is None


def test_submit_reality_score_is_idempotent_for_same_score_id(tmp_path):
    request = _request()
    first_status, first_record, first_path = submit_reality_score(request, tmp_path)
    second_status, second_record, second_path = submit_reality_score(request, tmp_path)
    assert first_status == "recorded"
    assert second_status == "already_exists"
    assert first_path == second_path
    assert first_record.id == second_record.id


def test_submit_reality_score_rejects_conflicting_score_id(tmp_path):
    submit_reality_score(_request(), tmp_path)
    with pytest.raises(ValueError):
        submit_reality_score(_request(actual_scores=_scores(4)), tmp_path)


def test_calculate_drift_values():
    result = calculate_drift_values(
        expected_scores=CalibrationScoreValues(**_scores(5)),
        actual_scores=CalibrationScoreValues(**_scores(3)),
    )
    assert result["per_dimension"] == {
        "execution_discipline": 0.5,
        "exploration_freedom": 0.5,
        "life_state_match": 0.5,
        "energy_level": 0.5,
    }
    assert result["overall"] == 0.5
    assert result["threshold_exceeded"] is False


def test_calculate_drift_threshold_is_evidence_only():
    result = calculate_drift(DriftCalculationRequest(
        expected_scores=CalibrationScoreValues(**_scores(5)),
        actual_scores=CalibrationScoreValues(**_scores(1)),
        branch_id="branch_A",
        alter_id="alter_A",
        score_id="score_test_001",
    ))
    assert result.overall == 1.0
    assert result.threshold_exceeded is True
    assert result.evidence_only is True
    assert result.regeneration_triggered is False
    assert result.rubric_modified is False


def test_history_lists_records_and_derives_drift_without_writing(tmp_path):
    submit_reality_score(_request(expected_scores=_scores(5)), tmp_path)
    before = sorted(p.name for p in score_directory(tmp_path).iterdir())
    history = build_calibration_history(tmp_path)
    after = sorted(p.name for p in score_directory(tmp_path).iterdir())
    assert before == after
    assert history["count"] == 1
    assert history["records"][0].id == "score_test_001"
    assert len(history["drift_evidence"]) == 1
    assert history["drift_evidence"][0].overall == 0.5
    assert history["boundary_confirmations"].calibration_history_read_only is True


def test_history_empty_when_no_scores(tmp_path):
    assert list_reality_score_records(tmp_path) == []
    history = build_calibration_history(tmp_path)
    assert history["count"] == 0
    assert history["drift_evidence"] == []


def test_schema_extra_forbid():
    with pytest.raises(Exception):
        CalibrationScoreValues(**_scores(3), provider="openai")
    with pytest.raises(Exception):
        RealityScoreRequest(
            score_id="score_bad",
            branch_id="branch_A",
            alter_id="alter_A",
            actual_scores=_scores(3),
            database=True,
        )
