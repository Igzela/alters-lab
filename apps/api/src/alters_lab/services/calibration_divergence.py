"""Calibration divergence service.

Compares subjective action_alignment trend against objective behavior/milestone
trends. Deterministic thresholds, no provider call, no life_score.
"""

from __future__ import annotations

import statistics
from datetime import date, timedelta
from pathlib import Path

from alters_lab.schemas.behavior_metric_trend import BehaviorMetricTrendRequest
from alters_lab.schemas.calibration_divergence import (
    CalibrationDivergenceRequest,
    CalibrationDivergenceResult,
    DivergenceFlag,
    ObjectiveTrack,
    SubjectiveTrack,
)
from alters_lab.services.action_alignment import list_action_alignment_scores
from alters_lab.services.behavior_metric_trend import analyze_behavior_trends
from alters_lab.services.branch_outcome_targets import list_targets_for_branch
from alters_lab.services.p6_runtime import utc_now

_FLAG_ID_COUNTER = 0


def analyze_calibration_divergence(
    request: CalibrationDivergenceRequest,
    repo_root: Path | None = None,
) -> CalibrationDivergenceResult:
    global _FLAG_ID_COUNTER
    limitations: list[str] = []
    flags: list[DivergenceFlag] = []

    # Subjective track: action alignment scores
    scores = list_action_alignment_scores(repo_root)
    cutoff = date.today() - timedelta(weeks=request.lookback_weeks)
    filtered_scores = []
    for s in scores:
        try:
            created = date.fromisoformat(s.created_at[:10])
            if created >= cutoff:
                filtered_scores.append(s)
        except (ValueError, IndexError):
            pass
    filtered_scores.sort(key=lambda s: s.created_at)

    subj_direction = _compute_subjective_direction(filtered_scores)
    subjective = SubjectiveTrack(
        action_alignment_direction=subj_direction,
        data_points=len(filtered_scores),
    )

    # Objective track: behavior metric trends
    trend_req = BehaviorMetricTrendRequest(lookback_weeks=request.lookback_weeks)
    trend_resp = analyze_behavior_trends(trend_req, repo_root=repo_root)

    behavior_directions = [
        t.direction for t in trend_resp.trends
        if t.direction != "insufficient_data"
    ]
    behavior_direction = _aggregate_behavior_direction(behavior_directions)

    milestone_direction = "insufficient_data"
    for t in trend_resp.trends:
        if t.metric_id == "key_milestone_progress":
            milestone_direction = t.direction
            break

    objective = ObjectiveTrack(
        behavior_direction=behavior_direction,
        milestone_direction=milestone_direction,
        data_points=sum(1 for t in trend_resp.trends if t.data_points > 0),
    )

    # Divergence detection
    divergence_status = _detect_divergence(subj_direction, behavior_direction, milestone_direction)

    if divergence_status == "diverging_positive_subjective":
        _FLAG_ID_COUNTER += 1
        flags.append(DivergenceFlag(
            flag_id=f"div_pos_subj_{_FLAG_ID_COUNTER}",
            severity="warn",
            explanation="Subjective alignment is improving but objective behavior evidence is declining. You may feel more aligned while behavior evidence weakens.",
            suggested_calibration_question="Are you feeling aligned because of real progress, or because you've adjusted your expectations downward?",
        ))

    if divergence_status == "diverging_negative_subjective":
        _FLAG_ID_COUNTER += 1
        flags.append(DivergenceFlag(
            flag_id=f"div_neg_subj_{_FLAG_ID_COUNTER}",
            severity="warn",
            explanation="Subjective alignment is declining but objective behavior is improving. You may be underestimating your actual progress.",
            suggested_calibration_question="Is your self-criticism calibrated to your actual behavior data, or are you holding yourself to an unrealistic standard?",
        ))

    if subj_direction == "insufficient_data":
        limitations.append("Insufficient subjective data (action alignment scores) for divergence analysis")

    if behavior_direction == "insufficient_data":
        limitations.append("Insufficient objective behavior data for divergence analysis")

    if milestone_direction == "insufficient_data":
        limitations.append("No milestone progress data available for divergence analysis")

    if request.branch_id:
        targets = list_targets_for_branch(request.branch_id, repo_root=repo_root)
        if not targets:
            limitations.append("No outcome targets defined; divergence analysis cannot verify prediction accuracy")

    return CalibrationDivergenceResult(
        generated_at=utc_now(),
        subjective_track=subjective,
        objective_track=objective,
        divergence_status=divergence_status,
        flags=flags,
        limitations=limitations,
    )


def _compute_subjective_direction(
    scores: list,
) -> str:
    if len(scores) < 2:
        return "insufficient_data"

    values = [s.action_alignment_score for s in scores]
    slope = _linear_slope(values)
    y_mean = sum(values) / len(values)
    threshold = abs(y_mean) * 0.05 if y_mean != 0 else 0.01

    if slope > threshold:
        return "improving"
    if slope < -threshold:
        return "declining"
    return "stable"


def _aggregate_behavior_direction(directions: list[str]) -> str:
    if not directions:
        return "insufficient_data"
    improving = directions.count("improving")
    declining = directions.count("declining")
    stable = directions.count("stable")

    if improving > declining and improving > stable:
        return "improving"
    if declining > improving and declining > stable:
        return "declining"
    if stable > improving and stable > declining:
        return "stable"
    if improving > 0 and declining > 0:
        return "mixed"
    return "stable"


def _detect_divergence(
    subjective: str,
    behavior: str,
    milestone: str,
) -> str:
    if subjective == "insufficient_data" or behavior == "insufficient_data":
        return "insufficient_data"

    obj_positive = behavior in ("improving",) or milestone == "improving"
    obj_negative = behavior in ("declining",) or milestone == "declining"
    subj_positive = subjective == "improving"
    subj_negative = subjective == "declining"

    if subj_positive and obj_negative:
        return "diverging_positive_subjective"
    if subj_negative and obj_positive:
        return "diverging_negative_subjective"
    if (subj_positive and obj_positive) or (subj_negative and obj_negative):
        return "converging"
    if behavior == "mixed":
        return "mixed"
    return "converging"


def _linear_slope(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    den = sum((i - x_mean) ** 2 for i in range(n))
    if den == 0:
        return 0.0
    return num / den
