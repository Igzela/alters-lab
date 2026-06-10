"""Tests for P4 calibration loop MVP service."""

from __future__ import annotations

import json

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


def test_reality_score_accepts_llm_source():
    req = RealityScoreRequest(
        score_id="score_llm",
        branch_id="branch_A",
        alter_id="alter_A",
        actual_scores=_scores(3),
        source="llm_calibration_draft",
    )
    assert req.source == "llm_calibration_draft"


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


# --- Closed-loop integration tests ---


def test_calibration_loop_state_update(tmp_path):
    """update_calibration_state() writes active status, increments cycle, records drift."""
    from alters_lab.services.calibration_loop import update_calibration_state

    state1 = update_calibration_state(
        drift_overall=0.3, drift_exceeded=False, branch_id="branch_A", repo_root=tmp_path
    )
    state_path = tmp_path / "alters" / "calibration" / "state.json"
    assert state_path.exists()
    assert state1["status"] == "active"
    assert state1["total_cycles"] == 1
    assert state1["current_drift"] == 0.3
    assert state1["drift_exceeded"] is False
    assert state1["branch_id"] == "branch_A"
    assert state1["mode"] == "evidence_accumulation"

    state2 = update_calibration_state(drift_overall=0.7, drift_exceeded=True, repo_root=tmp_path)
    assert state2["total_cycles"] == 2
    assert state2["current_drift"] == 0.7
    assert state2["drift_exceeded"] is True
    assert state2["status"] == "active"


def test_calibration_loop_reads_product_records(tmp_path):
    """list_reality_score_records() merges records from both alters/calibration/scores/ and alters/product/calibration_records/."""
    import yaml
    from alters_lab.services.calibration_loop import list_reality_score_records, score_directory

    # Write a record to the primary location (alters/calibration/scores/)
    primary_dir = score_directory(tmp_path)
    primary_dir.mkdir(parents=True, exist_ok=True)
    primary_record = {
        "id": "score_primary_001",
        "status": "recorded",
        "created_at": "2026-06-01T00:00:00+00:00",
        "branch_id": "branch_A",
        "alter_id": "alter_A",
        "input_refs": {"alter_ref": "alters/current/alters/alter_A.yaml"},
        "actual_scores": _scores(3),
        "submitted_by_user": True,
        "source": "explicit_user_submission",
        "caller": "api",
    }
    (primary_dir / "score_primary_001.yaml").write_text(
        yaml.dump(primary_record, allow_unicode=True), encoding="utf-8"
    )

    # Write a record to the product location (alters/product/calibration_records/)
    product_dir = tmp_path / "alters" / "product" / "calibration_records"
    product_dir.mkdir(parents=True, exist_ok=True)
    product_record = {
        "id": "score_product_001",
        "status": "recorded",
        "created_at": "2026-06-02T00:00:00+00:00",
        "branch_id": "branch_B",
        "alter_id": "alter_B",
        "input_refs": {"alter_ref": "alters/current/alters/alter_B.yaml"},
        "actual_scores": _scores(4),
        "submitted_by_user": True,
        "source": "llm_calibration_draft",
        "caller": "calibration_conversation",
    }
    (product_dir / "score_product_001.yaml").write_text(
        yaml.dump(product_record, allow_unicode=True), encoding="utf-8"
    )

    records = list_reality_score_records(repo_root=tmp_path)
    ids = {r.id for r in records}
    assert "score_primary_001" in ids
    assert "score_product_001" in ids
    assert len(records) == 2


def test_confirm_draft_writes_to_both_locations(tmp_path):
    """confirm_draft() with rubric_scores writes to both product/ and calibration/ locations and updates state.json."""
    import yaml
    from alters_lab.schemas.calibration_conversation import CalibrationDraft
    from alters_lab.schemas.calibration_loop import CalibrationScoreValues
    from alters_lab.services import calibration_conversation as svc

    draft = CalibrationDraft(
        conversation_id="conv_test",
        rubric_scores=CalibrationScoreValues(**_scores(4)),
    )
    svc._save_draft(draft, repo_root=tmp_path)

    confirmed = svc.confirm_draft(draft.draft_id, repo_root=tmp_path)
    assert confirmed.status == "confirmed"

    # Check product/calibration_records/ location
    product_dir = tmp_path / "alters" / "product" / "calibration_records"
    assert product_dir.exists()
    product_files = list(product_dir.glob("score_*.yaml"))
    assert len(product_files) == 1

    # Check alters/calibration/scores/ location
    loop_dir = tmp_path / "alters" / "calibration" / "scores"
    assert loop_dir.exists()
    loop_files = list(loop_dir.glob("score_*.yaml"))
    assert len(loop_files) == 1

    # Verify both files have the same score ID
    product_data = yaml.safe_load(product_files[0].read_text(encoding="utf-8"))
    loop_data = yaml.safe_load(loop_files[0].read_text(encoding="utf-8"))
    assert product_data["id"] == loop_data["id"]
    assert product_data["source"] == "llm_calibration_draft"

    # Verify state.json was updated
    state_path = tmp_path / "alters" / "calibration" / "state.json"
    assert state_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["status"] == "active"
    assert state["total_cycles"] >= 1


def test_schema_accepts_llm_source():
    """RealityScoreRequest with source='llm_calibration_draft' validates without error."""
    request = RealityScoreRequest(
        score_id="score_llm_001",
        branch_id="branch_A",
        alter_id="alter_A",
        actual_scores=_scores(3),
        source="llm_calibration_draft",
    )
    assert request.source == "llm_calibration_draft"
