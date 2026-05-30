"""Pattern adjustment service — modifies trend forecast based on detected patterns.

All output is evidence-only. Pattern adjustments never trigger automatic actions.
"""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.pattern_adjustment import (
    AdjustedForecastPoint,
    PatternAdjustmentRequest,
    PatternAdjustmentResult,
)
from alters_lab.schemas.trend_analysis import ForecastPoint
from alters_lab.services.pattern_review import list_pattern_reviews
from alters_lab.services.trend_analysis import analyze_trend
from alters_lab.services.p6_runtime import utc_now

# Per-pattern weekly dampening factors (reduction applied to forecast each week)
PATTERN_DAMPENING = {
    "repeated_noisy_progress": 0.05,
    "repeated_avoidance_disguised_as_work": 0.08,
    "repeated_sleep_breakdown": 0.03,
    "repeated_over_scope": 0.04,
    "repeated_action_mismatch": 0.06,
    "repeated_primary_correction_failure": 0.07,
}

PATTERN_LABELS = {
    "repeated_noisy_progress": "Noisy Progress",
    "repeated_avoidance_disguised_as_work": "Avoidance Disguised as Work",
    "repeated_sleep_breakdown": "Sleep Breakdown",
    "repeated_over_scope": "Over Scope",
    "repeated_action_mismatch": "Action Mismatch",
    "repeated_primary_correction_failure": "Correction Failure",
}


def adjust_forecast(
    request: PatternAdjustmentRequest,
    repo_root: Path | None = None,
) -> PatternAdjustmentResult:
    # Get trend forecast as baseline
    from alters_lab.schemas.trend_analysis import TrendAnalysisRequest
    trend_request = TrendAnalysisRequest(
        lookback_weeks=request.lookback_weeks,
        forecast_weeks=request.forecast_weeks,
    )
    trend = analyze_trend(trend_request, repo_root)

    if not trend.forecast:
        return PatternAdjustmentResult(
            has_patterns=False,
            original_forecast=[],
            adjusted_forecast=[],
            generated_at=utc_now(),
        )

    # Find latest pattern review with triggered patterns
    pattern_reviews = list_pattern_reviews(repo_root)
    triggered_patterns: dict[str, float] = {}  # pattern_name -> dampening per week

    for review in reversed(pattern_reviews):
        if review.status == "pattern_triggered" and review.triggered_patterns:
            for tp in review.triggered_patterns:
                pattern_name = tp.pattern if isinstance(tp.pattern, str) else tp.pattern.value
                if pattern_name in PATTERN_DAMPENING:
                    triggered_patterns[pattern_name] = PATTERN_DAMPENING[pattern_name]
            break  # only use the most recent triggered review

    # Build adjusted forecast
    adjusted: list[AdjustedForecastPoint] = []
    adjustments_applied: list[str] = []

    for fp in trend.forecast:
        total_delta = 0.0
        reasons: list[str] = []
        for pattern_name, dampening in triggered_patterns.items():
            delta = dampening * fp.week_offset  # cumulative effect over weeks
            total_delta += delta
            label = PATTERN_LABELS.get(pattern_name, pattern_name)
            reasons.append(f"{label} (-{delta:.3f})")
            if pattern_name not in adjustments_applied:
                adjustments_applied.append(pattern_name)

        adjusted_score = max(0.0, min(1.0, fp.predicted_score - total_delta))
        margin = fp.upper_bound - fp.predicted_score

        adjusted.append(AdjustedForecastPoint(
            week_offset=fp.week_offset,
            original_score=fp.predicted_score,
            adjusted_score=round(adjusted_score, 4),
            adjustment_delta=round(-total_delta, 4),
            adjustment_reason="; ".join(reasons) if reasons else "No pattern adjustment",
            lower_bound=round(max(0.0, adjusted_score - margin), 4),
            upper_bound=round(min(1.0, adjusted_score + margin), 4),
        ))

    return PatternAdjustmentResult(
        has_patterns=bool(triggered_patterns),
        original_forecast=trend.forecast,
        adjusted_forecast=adjusted,
        adjustments_applied=adjustments_applied,
        generated_at=utc_now(),
    )
