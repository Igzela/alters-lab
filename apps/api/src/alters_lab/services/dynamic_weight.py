"""Dynamic weight computation service.

Computes advisory rubric dimension weights based on current behavioral state.
Weights are never auto-applied to rubric — they are evidence-only recommendations.
"""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.dynamic_weight import (
    DimensionWeight,
    DynamicWeightRequest,
    DynamicWeightResult,
)
from alters_lab.services.action_alignment import list_action_alignment_scores
from alters_lab.services.p6_runtime import utc_now

RUBRIC_DIMENSIONS = (
    "execution_discipline",
    "exploration_freedom",
    "life_state_match",
    "energy_level",
)

DEFAULT_WEIGHT = 1.0
MIN_WEIGHT = 0.5
MAX_WEIGHT = 2.0


def _clamp_weight(value: float) -> float:
    return round(max(MIN_WEIGHT, min(MAX_WEIGHT, value)), 4)


def compute_dynamic_weights(
    request: DynamicWeightRequest,
    repo_root: Path | None = None,
) -> DynamicWeightResult:
    scores = list_action_alignment_scores(repo_root)

    if not scores:
        weights = [DimensionWeight(dimension=d, weight=DEFAULT_WEIGHT, rationale="No data — using default weight.") for d in RUBRIC_DIMENSIONS]
        return DynamicWeightResult(
            weights=weights,
            overall_alignment=0.0,
            recommendation="Insufficient data. Start weekly reviews to generate alignment scores.",
            generated_at=utc_now(),
        )

    sorted_scores = sorted(scores, key=lambda s: s.created_at)
    lookback = sorted_scores[-request.lookback_weeks:]
    alignment_values = [s.action_alignment_score for s in lookback]
    avg_alignment = sum(alignment_values) / len(alignment_values)

    # Compute per-dimension averages from the 3 alignment dimensions
    avg_direction = sum(s.scores.direction_alignment for s in lookback) / len(lookback)
    avg_execution = sum(s.scores.execution_consistency for s in lookback) / len(lookback)
    avg_avoidance = sum(s.scores.avoidance_level for s in lookback) / len(lookback)

    weights: list[DimensionWeight] = []

    # execution_discipline: boost when alignment is low (user needs structure)
    if avg_alignment <= 0.3:
        w = _clamp_weight(1.5)
        rationale = "Low overall alignment — increase execution discipline emphasis."
    elif avg_alignment >= 0.7:
        w = _clamp_weight(0.8)
        rationale = "High alignment — reduce execution discipline, allow more exploration."
    else:
        w = DEFAULT_WEIGHT
        rationale = "Moderate alignment — keep default weight."
    weights.append(DimensionWeight(dimension="execution_discipline", weight=w, rationale=rationale))

    # exploration_freedom: inverse of execution_discipline logic
    if avg_alignment >= 0.7:
        w = _clamp_weight(1.2)
        rationale = "High alignment — user can handle more exploration freedom."
    elif avg_alignment <= 0.3:
        w = _clamp_weight(0.7)
        rationale = "Low alignment — reduce exploration, focus on fundamentals."
    else:
        w = DEFAULT_WEIGHT
        rationale = "Moderate alignment — keep default weight."
    weights.append(DimensionWeight(dimension="exploration_freedom", weight=w, rationale=rationale))

    # life_state_match: boost when direction alignment is low
    if avg_direction < 0.4:
        w = _clamp_weight(1.3)
        rationale = "Low direction alignment — life state may be misaligned with goals."
    else:
        w = DEFAULT_WEIGHT
        rationale = "Direction alignment acceptable — keep default weight."
    weights.append(DimensionWeight(dimension="life_state_match", weight=w, rationale=rationale))

    # energy_level: boost when avoidance is high (energy may be the root cause)
    if avg_avoidance > 0.6:
        w = _clamp_weight(1.3)
        rationale = "High avoidance level — energy state may be the bottleneck."
    elif avg_avoidance < 0.2:
        w = _clamp_weight(0.8)
        rationale = "Low avoidance — energy is not a constraint."
    else:
        w = DEFAULT_WEIGHT
        rationale = "Moderate avoidance — keep default weight."
    weights.append(DimensionWeight(dimension="energy_level", weight=w, rationale=rationale))

    # Recommendation
    if avg_alignment >= 0.7:
        rec = "Alignment is strong. Consider increasing challenge scope."
    elif avg_alignment <= 0.3:
        rec = "Alignment is low. Focus on execution discipline and reducing avoidance."
    else:
        rec = "Moderate alignment. Continue weekly reviews to build evidence."

    return DynamicWeightResult(
        weights=weights,
        overall_alignment=round(avg_alignment, 4),
        recommendation=rec,
        generated_at=utc_now(),
    )
