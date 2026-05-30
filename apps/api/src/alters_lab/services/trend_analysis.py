"""Trend analysis service — linear extrapolation from historical scores.

All output is evidence-only read-only. No probability forecasting.
Trend direction and forecasts are descriptive, not predictive.
"""

from __future__ import annotations

import statistics
from pathlib import Path

from alters_lab.schemas.trend_analysis import (
    ConfidenceInterval,
    ForecastPoint,
    TrendAnalysisRequest,
    TrendAnalysisResult,
    TrendDimensionResult,
)
from alters_lab.services.action_alignment import list_action_alignment_scores
from alters_lab.services.p6_runtime import utc_now


def _linear_regression(values: list[float]) -> tuple[float, float, float]:
    """Return (slope, intercept, r_squared) for a simple linear regression."""
    n = len(values)
    if n < 2:
        return 0.0, values[0] if values else 0.0, 0.0

    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = values[n - 1]  # use last value as y intercept reference

    sum_xy = sum((i - mean_x) * (v - mean_y) for i, v in enumerate(values))
    sum_x_sq = sum((i - mean_x) ** 2 for i in range(n))

    if sum_x_sq == 0:
        return 0.0, mean_y, 0.0

    slope = sum_xy / sum_x_sq
    intercept = mean_y - slope * (n - 1)

    # R² calculation
    ss_tot = sum((v - mean_y) ** 2 for v in values)
    if ss_tot == 0:
        r_sq = 1.0 if slope == 0 else 0.0
    else:
        ss_res = sum((v - (slope * i + intercept)) ** 2 for i, v in enumerate(values))
        r_sq = max(0.0, 1.0 - (ss_res / ss_tot))

    return slope, intercept, r_sq


def _classify_direction(slope: float) -> str:
    if slope > 0.02:
        return "improving"
    if slope < -0.02:
        return "declining"
    return "stable"


def _compute_confidence(data_count: int, r_squared: float) -> str:
    if data_count >= 6 and r_squared >= 0.5:
        return "high"
    if data_count >= 4 and r_squared >= 0.3:
        return "medium"
    return "low"


def _compute_consistency(values: list[float]) -> float:
    """Compute consistency as 1 - normalized_std_dev, clamped [0, 1]."""
    if len(values) < 2:
        return 0.0
    std_dev = statistics.stdev(values)
    # Normalize: std_dev of 0 = perfect consistency (1.0), std_dev of 0.5 = 0.0
    return round(max(0.0, min(1.0, 1.0 - (std_dev / 0.5))), 4)


def analyze_trend(
    request: TrendAnalysisRequest,
    repo_root: Path | None = None,
) -> TrendAnalysisResult:
    scores = list_action_alignment_scores(repo_root)

    if len(scores) < 2:
        return TrendAnalysisResult(
            overall_direction="insufficient_data",
            confidence_interval=ConfidenceInterval(
                level="low",
                data_count=len(scores),
                consistency_score=0.0,
                description="Need at least 2 data points for trend analysis.",
            ),
            generated_at=utc_now(),
        )

    # Sort by time, take last N weeks
    sorted_scores = sorted(scores, key=lambda s: s.created_at)
    lookback = sorted_scores[-request.lookback_weeks:]
    values = [s.action_alignment_score for s in lookback]

    slope, intercept, r_sq = _linear_regression(values)
    direction = _classify_direction(slope)
    confidence = _compute_confidence(len(values), r_sq)
    consistency = _compute_consistency(values)

    # Generate forecast
    forecast: list[ForecastPoint] = []
    for week in range(1, request.forecast_weeks + 1):
        predicted = slope * (len(values) - 1 + week) + intercept
        # Confidence band widens with distance
        margin = 0.05 + (0.03 * week) * (1.0 if confidence == "high" else 1.5 if confidence == "medium" else 2.0)
        forecast.append(ForecastPoint(
            week_offset=week,
            predicted_score=round(max(0.0, min(1.0, predicted)), 4),
            lower_bound=round(max(0.0, min(1.0, predicted - margin)), 4),
            upper_bound=round(max(0.0, min(1.0, predicted + margin)), 4),
        ))

    # Build per-dimension results from the 3 action alignment dimensions
    dim_names = ["direction_alignment", "execution_consistency", "avoidance_level"]
    dimensions: list[TrendDimensionResult] = []
    for dim in dim_names:
        dim_values = [getattr(s.scores, dim) for s in lookback]
        d_slope, _, d_r_sq = _linear_regression(dim_values)
        dimensions.append(TrendDimensionResult(
            dimension=dim,
            direction=_classify_direction(d_slope),
            slope=round(d_slope, 6),
            r_squared=round(d_r_sq, 4),
            confidence_level=_compute_confidence(len(dim_values), d_r_sq),
            data_points=len(dim_values),
        ))

    confidence_desc = {
        "high": f"High confidence based on {len(values)} data points with r²={r_sq:.2f}.",
        "medium": f"Medium confidence based on {len(values)} data points with r²={r_sq:.2f}.",
        "low": f"Low confidence — need more data or data is inconsistent (r²={r_sq:.2f}).",
    }

    return TrendAnalysisResult(
        overall_direction=direction,
        dimensions=dimensions,
        forecast=forecast,
        confidence_interval=ConfidenceInterval(
            level=confidence,
            data_count=len(values),
            consistency_score=consistency,
            description=confidence_desc[confidence],
        ),
        generated_at=utc_now(),
    )
