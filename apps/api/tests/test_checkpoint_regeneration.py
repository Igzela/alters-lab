"""Tests for P4-M7 Checkpoint Regeneration Plan service."""

from __future__ import annotations

import pytest

from alters_lab.schemas.calibration_loop import RealityScoreRequest
from alters_lab.schemas.checkpoint_regeneration import (
    CheckpointPlanRequest,
    CheckpointRegenerationPlan,
    CheckpointRegenerationPlanStep,
)
from alters_lab.services.calibration_loop import submit_reality_score
from alters_lab.services.checkpoint_regeneration import (
    checkpoint_plan_directory,
    list_checkpoint_regeneration_plans,
    plan_checkpoint_regeneration,
)


def _scores(value: int) -> dict:
    return {
        "execution_discipline": value,
        "exploration_freedom": value,
        "life_state_match": value,
        "energy_level": value,
    }


def _record(tmp_path, score_id: str, actual: int, expected: int):
    submit_reality_score(RealityScoreRequest(
        score_id=score_id,
        branch_id="branch_A",
        alter_id="alter_A",
        actual_scores=_scores(actual),
        expected_scores=_scores(expected),
        submitted_by_user=True,
    ), tmp_path)


def test_no_high_drift_returns_no_action(tmp_path):
    _record(tmp_path, "score_low", actual=4, expected=5)
    status, plan, path = plan_checkpoint_regeneration(CheckpointPlanRequest(drift_threshold=0.6), tmp_path)
    assert status == "no_action"
    assert plan is None
    assert path is None


def test_high_drift_creates_pending_review_plan(tmp_path):
    _record(tmp_path, "score_high", actual=1, expected=5)
    status, plan, path = plan_checkpoint_regeneration(CheckpointPlanRequest(drift_threshold=0.6), tmp_path)
    assert status == "plan_created"
    assert path is None
    assert plan is not None
    assert plan.status == "pending_review"
    assert plan.regeneration_allowed_now is False
    assert plan.active_write_allowed is False
    assert plan.human_confirmation_required is True
    assert all(step.execution_allowed_now is False for step in plan.steps)


def test_plan_schema_rejects_execution_and_active_write():
    with pytest.raises(Exception):
        CheckpointRegenerationPlanStep(
            step_id="step_bad",
            title="bad",
            description="bad",
            required_evidence=[],
            execution_allowed_now=True,
        )
    with pytest.raises(Exception):
        CheckpointRegenerationPlan(
            id="checkpoint_plan_bad",
            trigger_reason="bad",
            source_drift_refs=[],
            source_score_refs=[],
            recommended_scope="review_branch",
            steps=[],
            regeneration_allowed_now=True,
            active_write_allowed=False,
            human_confirmation_required=True,
            created_at="2026-05-20T00:00:00+00:00",
            boundary_confirmations={},
        )


def test_save_plan_writes_only_tmp_checkpoint_plan_dir(tmp_path):
    _record(tmp_path, "score_high", actual=1, expected=5)
    snapshot = tmp_path / "alters" / "current" / "snapshot.yaml"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_text("snapshot: unchanged\n", encoding="utf-8")
    before = snapshot.read_text(encoding="utf-8")

    status, plan, path = plan_checkpoint_regeneration(
        CheckpointPlanRequest(drift_threshold=0.6, save_plan=True),
        tmp_path,
    )

    assert status == "saved"
    assert plan is not None
    assert path is not None
    assert path.parent == checkpoint_plan_directory(tmp_path)
    assert path.exists()
    assert snapshot.read_text(encoding="utf-8") == before


def test_extra_execute_regenerate_active_write_rejected():
    with pytest.raises(Exception):
        CheckpointPlanRequest(execute=True)
    with pytest.raises(Exception):
        CheckpointPlanRequest(regenerate=True)
    with pytest.raises(Exception):
        CheckpointPlanRequest(active_write=True)


def test_list_checkpoint_plans_metadata_only(tmp_path):
    _record(tmp_path, "score_high", actual=1, expected=5)
    plan_checkpoint_regeneration(CheckpointPlanRequest(save_plan=True), tmp_path)
    plans = list_checkpoint_regeneration_plans(tmp_path)
    assert len(plans) == 1
    assert plans[0]["status"] == "pending_review"
    assert "steps" not in plans[0]
