"""P5-M6 User Workflow Integration service.

Provides integrated workflow state and optional workflow-run record.
No provider calls in state. No active YAML write.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from alters_lab.services import io

from alters_lab.loaders.active_yaml import active_yaml_paths
from alters_lab.services.calibration_loop import list_reality_score_records, calculate_drift_values, CalibrationScoreValues
from alters_lab.schemas.user_workflow import (
    UserWorkflowHealthResponse,
    UserWorkflowStateResponse,
    WorkflowRunSummaryRequest,
    WorkflowRunSummaryResponse,
)


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def get_user_workflow_health() -> UserWorkflowHealthResponse:
    return UserWorkflowHealthResponse()


def get_user_workflow_state(repo_root: Path | None = None) -> UserWorkflowStateResponse:
    root = repo_root or _get_repo_root()

    paths = active_yaml_paths(root)
    available_alters = sorted(paths.alters.keys())

    scores = list_reality_score_records(root)
    last_scores = []
    drift_summary = None

    if scores:
        for s in scores[-5:]:
            last_scores.append({
                "id": s.id,
                "alter_id": s.alter_id,
                "branch_id": s.branch_id,
                "actual_scores": s.actual_scores.model_dump(),
            })

        if scores[-1].expected_scores is not None:
            drift = calculate_drift_values(
                scores[-1].expected_scores,
                scores[-1].actual_scores,
            )
            drift_summary = {
                "overall": drift["overall"],
                "threshold_exceeded": drift["threshold_exceeded"],
                "score_id": scores[-1].id,
            }

    rubric_delta_available = _check_rubric_delta(root)
    checkpoint_plan_available = _check_checkpoint_plan(root)

    next_action = "select_an_alter"
    if scores:
        next_action = "submit_next_reality_score"
    if rubric_delta_available:
        next_action = "review_rubric_delta_suggestion"

    return UserWorkflowStateResponse(
        available_alters=available_alters,
        provider_status="mock_default",
        last_reality_scores=last_scores,
        drift_summary=drift_summary,
        rubric_delta_available=rubric_delta_available,
        checkpoint_plan_available=checkpoint_plan_available,
        next_recommended_action=next_action,
    )


def _check_rubric_delta(repo_root: Path) -> bool:
    suggestions_dir = repo_root / "alters" / "calibration" / "rubric_delta_suggestions"
    if suggestions_dir.exists():
        return len(list(suggestions_dir.glob("*.yaml"))) > 0
    return False


def _check_checkpoint_plan(repo_root: Path) -> bool:
    plans_dir = repo_root / "alters" / "calibration" / "checkpoint_plans"
    if plans_dir.exists():
        return len(list(plans_dir.glob("*.yaml"))) > 0
    return False


def save_workflow_run_summary(
    request: WorkflowRunSummaryRequest,
    repo_root: Path | None = None,
) -> WorkflowRunSummaryResponse:
    root = repo_root or _get_repo_root()
    runs_dir = root / "alters" / "product" / "workflow_runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"run_{ts}_{uuid.uuid4().hex[:8]}"
    run_path = runs_dir / f"{run_id}.yaml"

    run_data = {
        "run_id": run_id,
        "timestamp": ts,
        "action": request.action,
        "alter_id": request.alter_id,
        "notes": request.notes,
        "caller": request.caller,
        "safety_metadata": {
            "active_yaml_modified": False,
            "persisted_to_product_area": True,
        },
    }

    io.write_yaml(run_path, run_data)

    return WorkflowRunSummaryResponse(
        status="saved",
        run_id=run_id,
        run_path=str(run_path),
    )
