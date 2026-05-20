"""P4-M7 Checkpoint Regeneration Plan service.

The service creates pending-review plans from high drift evidence. It does not
regenerate branches/alters, call providers, or write active YAML.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

from alters_lab.schemas.checkpoint_regeneration import (
    CheckpointBoundaryConfirmations,
    CheckpointPlanRequest,
    CheckpointRegenerationPlan,
    CheckpointRegenerationPlanStep,
)
from alters_lab.services.calibration_loop import build_calibration_history, get_repo_root


def checkpoint_boundary_confirmations() -> dict:
    return CheckpointBoundaryConfirmations().model_dump()


def checkpoint_plan_directory(repo_root: Path | None = None) -> Path:
    root = repo_root or get_repo_root()
    return root / "alters" / "calibration" / "checkpoint_plans"


def generate_checkpoint_plan_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"checkpoint_plan_{ts}_{uuid.uuid4().hex[:8]}"


def _recommended_scope(max_drift: float) -> str:
    if max_drift >= 0.8:
        return "full_checkpoint_review"
    if max_drift >= 0.7:
        return "review_branch"
    if max_drift >= 0.6:
        return "review_alter"
    return "review_rubric"


def _plan_steps() -> list[CheckpointRegenerationPlanStep]:
    return [
        CheckpointRegenerationPlanStep(
            step_id="step_1",
            title="Review reality score evidence",
            description="Inspect score records and drift values that triggered this plan.",
            required_evidence=["source_score_refs", "source_drift_refs"],
        ),
        CheckpointRegenerationPlanStep(
            step_id="step_2",
            title="Review rubric delta suggestions",
            description="Compare drift patterns against any pending rubric delta suggestions.",
            required_evidence=["rubric_delta_suggestions"],
        ),
        CheckpointRegenerationPlanStep(
            step_id="step_3",
            title="Review alter voice consistency",
            description="Check whether the active alter voice remains consistent with observed reality.",
            required_evidence=["active_alter_yaml", "dialogue_contract"],
        ),
        CheckpointRegenerationPlanStep(
            step_id="step_4",
            title="Decide whether a semantic promotion slice is needed",
            description="Determine whether future work should prepare a reviewed semantic promotion package.",
            required_evidence=["human_review_notes", "governance_decision"],
        ),
        CheckpointRegenerationPlanStep(
            step_id="step_5",
            title="Require explicit human approval before active write",
            description="No active branch or alter write is allowed from this plan without a later approved slice.",
            required_evidence=["human_approval_record", "archive_manifest"],
        ),
    ]


def build_checkpoint_regeneration_plan(
    request: CheckpointPlanRequest,
    repo_root: Path | None = None,
) -> tuple[str, CheckpointRegenerationPlan | None]:
    history = build_calibration_history(repo_root)
    high_drift = [
        drift for drift in history["drift_evidence"]
        if drift.overall >= request.drift_threshold
    ]
    if not high_drift:
        return "no_action", None

    max_drift = max(drift.overall for drift in high_drift)
    source_score_refs = sorted({drift.score_id for drift in high_drift if drift.score_id})
    source_drift_refs = [
        f"{drift.score_id or 'unknown_score'}:overall={drift.overall}"
        for drift in high_drift
    ]
    plan = CheckpointRegenerationPlan(
        id=generate_checkpoint_plan_id(),
        trigger_reason=(
            f"Detected {len(high_drift)} drift record(s) at or above threshold "
            f"{request.drift_threshold:.2f}; max drift {max_drift:.2f}."
        ),
        source_drift_refs=source_drift_refs,
        source_score_refs=source_score_refs,
        recommended_scope=_recommended_scope(max_drift),  # type: ignore[arg-type]
        steps=_plan_steps(),
        created_at=datetime.now(timezone.utc).isoformat(),
        boundary_confirmations=CheckpointBoundaryConfirmations(),
    )
    return "plan_created", plan


def save_checkpoint_regeneration_plan(
    plan: CheckpointRegenerationPlan,
    repo_root: Path | None = None,
) -> Path:
    directory = checkpoint_plan_directory(repo_root)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{plan.id}.yaml"
    path.write_text(
        yaml.safe_dump(plan.model_dump(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


def plan_checkpoint_regeneration(
    request: CheckpointPlanRequest,
    repo_root: Path | None = None,
) -> tuple[str, CheckpointRegenerationPlan | None, Path | None]:
    status, plan = build_checkpoint_regeneration_plan(request, repo_root)
    if plan is None:
        return status, None, None
    if request.save_plan:
        path = save_checkpoint_regeneration_plan(plan, repo_root)
        return "saved", plan, path
    return status, plan, None


def list_checkpoint_regeneration_plans(repo_root: Path | None = None) -> list[dict]:
    directory = checkpoint_plan_directory(repo_root)
    if not directory.exists():
        return []

    plans: list[dict] = []
    for path in sorted(directory.glob("checkpoint_plan_*.yaml")):
        if path.name == "_template.yaml":
            continue
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            continue
        plans.append({
            "id": raw.get("id", path.stem),
            "status": raw.get("status"),
            "created_at": raw.get("created_at"),
            "recommended_scope": raw.get("recommended_scope"),
            "path": str(path),
        })
    return plans
