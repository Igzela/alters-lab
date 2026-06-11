"""Calibration loop API for P4-M2/M3/M4."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.calibration_loop import (
    CalibrationHistoryResponse,
    CalibrationLoopHealthResponse,
    DriftCalculationRequest,
    DriftCalculationResult,
    RealityScoreRequest,
    RealityScoreResponse,
)
from alters_lab.services.calibration_loop import (
    build_calibration_history,
    calculate_drift,
    calibration_boundary_confirmations,
    get_repo_root,
    list_reality_score_records,
    submit_reality_score,
)

router = APIRouter(prefix="/calibration-loop", tags=["calibration-loop"])


def _repo_root() -> Path:
    return get_repo_root()


@router.get("/health", response_model=CalibrationLoopHealthResponse)
def health():
    return CalibrationLoopHealthResponse()


@router.post("/reality-scores", response_model=RealityScoreResponse)
def submit_score(request: RealityScoreRequest):
    try:
        status, record, path = submit_reality_score(request, _repo_root())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RealityScoreResponse(
        status=status,
        record=record,
        score_path=str(path),
        boundary_confirmations=calibration_boundary_confirmations(),
    )


@router.post("/drift/calculate", response_model=DriftCalculationResult)
def calculate_drift_evidence(request: DriftCalculationRequest):
    return calculate_drift(request)


@router.get("/history", response_model=CalibrationHistoryResponse)
def history():
    try:
        result = build_calibration_history(_repo_root())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return CalibrationHistoryResponse(
        records=result["records"],
        drift_evidence=result["drift_evidence"],
        count=result["count"],
        boundary_confirmations=result["boundary_confirmations"],
    )


@router.get("/prediction-accuracy")
def prediction_accuracy(branch_id: str | None = None):
    """Compare alter predictions against actual calibration scores."""
    from alters_lab.services.alter_rubric_baseline import get_baseline_for_branch

    repo = _repo_root()
    limitations = []

    bid = branch_id or "branch_D"

    baseline = get_baseline_for_branch(bid, repo_root=repo)
    if not baseline:
        limitations.append(f"No alter baseline found for {bid}")
        return {
            "branch_id": bid,
            "alter_id": None,
            "baseline": None,
            "actual_trajectory": [],
            "accuracy": None,
            "limitations": limitations,
        }

    records = list_reality_score_records(repo_root=repo)
    branch_records = [r for r in records if r.branch_id == bid]
    branch_records.sort(key=lambda r: r.created_at)

    if not branch_records:
        limitations.append("No calibration scores recorded yet for this branch")
        return {
            "branch_id": bid,
            "alter_id": baseline.alter_id,
            "baseline": {
                "expected_initial": baseline.expected_initial.model_dump(),
                "expected_30d": baseline.expected_30d.model_dump(),
                "expected_90d": baseline.expected_90d.model_dump(),
                "drift_direction": baseline.drift_direction,
                "reasoning": baseline.reasoning,
            },
            "actual_trajectory": [],
            "accuracy": None,
            "limitations": limitations,
        }

    trajectory = []
    for r in branch_records:
        trajectory.append({
            "score_id": r.id,
            "created_at": r.created_at,
            "scores": r.actual_scores.model_dump() if r.actual_scores else None,
            "expected": r.expected_scores.model_dump() if r.expected_scores else None,
            "drift": r.drift,
        })

    first_date_str = branch_records[0].created_at
    from datetime import datetime, timezone

    first_date = datetime.fromisoformat(first_date_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    elapsed_days = (now - first_date).days

    if elapsed_days <= 15:
        target_expected = baseline.expected_initial
        horizon_label = "initial"
    elif elapsed_days <= 45:
        target_expected = baseline.expected_30d
        horizon_label = "30d"
    else:
        target_expected = baseline.expected_90d
        horizon_label = "90d"

    latest = branch_records[-1]
    actual = latest.actual_scores
    dims = ["execution_discipline", "exploration_freedom", "life_state_match", "energy_level"]

    per_dimension = {}
    for dim in dims:
        exp_val = getattr(target_expected, dim)
        act_val = getattr(actual, dim)
        direction_match = (
            (act_val >= exp_val and baseline.drift_direction.get(dim, "").startswith("↑"))
            or (act_val <= exp_val and baseline.drift_direction.get(dim, "").startswith("↓"))
            or (abs(act_val - exp_val) <= 1 and baseline.drift_direction.get(dim, "") in ("→", "↑/mixed", "↓/mixed"))
        )
        per_dimension[dim] = {
            "predicted_value": exp_val,
            "actual_value": act_val,
            "predicted_direction": baseline.drift_direction.get(dim, "unknown"),
            "gap": act_val - exp_val,
            "direction_aligned": direction_match,
        }

    aligned_count = sum(1 for d in per_dimension.values() if d["direction_aligned"])
    if aligned_count >= 3:
        assessment = "on_track"
    elif aligned_count >= 2:
        assessment = "partial_match"
    else:
        assessment = "diverging"

    failure_signals = []
    for dim, info in per_dimension.items():
        if info["predicted_direction"] == "↑" and info["gap"] <= -2:
            failure_signals.append(f"{dim}: predicted improving but dropped significantly")
        if info["predicted_direction"] == "→" and info["gap"] <= -2:
            failure_signals.append(f"{dim}: predicted stable but dropped significantly")

    if failure_signals:
        assessment = "failure_mode_emerging"

    return {
        "branch_id": bid,
        "alter_id": baseline.alter_id,
        "horizon": horizon_label,
        "elapsed_days": elapsed_days,
        "baseline": {
            "expected_initial": baseline.expected_initial.model_dump(),
            "expected_30d": baseline.expected_30d.model_dump(),
            "expected_90d": baseline.expected_90d.model_dump(),
            "drift_direction": baseline.drift_direction,
            "reasoning": baseline.reasoning,
        },
        "actual_trajectory": trajectory,
        "accuracy": {
            "overall_assessment": assessment,
            "per_dimension": per_dimension,
            "aligned_dimensions": aligned_count,
            "total_dimensions": 4,
            "failure_signals": failure_signals,
        },
        "limitations": limitations,
    }
