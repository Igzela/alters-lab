"""Behavior metric trend analysis service."""

from __future__ import annotations

import statistics
from datetime import date, timedelta
from pathlib import Path

from alters_lab.schemas.behavior_metrics_catalog import METRIC_ID_TO_FIELD, load_catalog
from alters_lab.schemas.behavior_metrics_record import (
    WeeklyBehaviorMetricsRecord,
    get_metric_value_for_analysis,
)
from alters_lab.schemas.behavior_metric_trend import (
    BehaviorMetricTrendRequest,
    BehaviorMetricTrendResponse,
    BehaviorMetricTrendResult,
)
from alters_lab.services.behavior_metrics import list_weekly_records
from alters_lab.services.p6_runtime import utc_now


def analyze_behavior_trends(
    request: BehaviorMetricTrendRequest,
    repo_root: Path | None = None,
) -> BehaviorMetricTrendResponse:
    catalog = load_catalog(_resolve_catalog_path(repo_root))
    metric_ids = [m.id for m in catalog.behavior_metric_set.metrics]

    records = list_weekly_records(repo_root)
    cutoff = date.today() - timedelta(weeks=request.lookback_weeks)
    records = [r for r in records if r.week_start >= cutoff]
    records.sort(key=lambda r: r.week_start)

    trends = []
    for metric_id in metric_ids:
        trends.append(_compute_metric_trend(metric_id, records))

    return BehaviorMetricTrendResponse(
        lookback_weeks=request.lookback_weeks,
        trends=trends,
        generated_at=utc_now(),
    )


def _compute_metric_trend(
    metric_id: str,
    records: list[WeeklyBehaviorMetricsRecord],
) -> BehaviorMetricTrendResult:
    values: list[float] = []
    for record in records:
        val = get_metric_value_for_analysis(record, metric_id)
        if val is not None:
            values.append(float(val))

    if len(values) < 2:
        return BehaviorMetricTrendResult(
            metric_id=metric_id,
            direction="insufficient_data",
            slope=0.0,
            confidence_level="low",
            data_points=len(values),
            current_value=values[-1] if values else None,
        )

    slope = _linear_slope(values)
    direction = _classify_direction(slope, values)
    confidence = _classify_confidence(len(values))
    rolling_4w = _rolling_median(values, window=4)

    return BehaviorMetricTrendResult(
        metric_id=metric_id,
        direction=direction,
        slope=round(slope, 6),
        confidence_level=confidence,
        data_points=len(values),
        current_value=values[-1],
        rolling_4w_median=round(rolling_4w, 4) if rolling_4w is not None else None,
    )


def _linear_slope(values: list[float]) -> float:
    n = len(values)
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    den = sum((i - x_mean) ** 2 for i in range(n))
    if den == 0:
        return 0.0
    return num / den


def _classify_direction(
    slope: float, values: list[float]
) -> Literal["improving", "declining", "stable"]:
    if not values:
        return "stable"
    y_mean = sum(values) / len(values)
    if y_mean == 0:
        threshold = 0.01
    else:
        threshold = abs(y_mean) * 0.05
    if slope > threshold:
        return "improving"
    if slope < -threshold:
        return "declining"
    return "stable"


def _classify_confidence(data_points: int) -> Literal["low", "medium", "high"]:
    if data_points >= 8:
        return "high"
    if data_points >= 4:
        return "medium"
    return "low"


def _rolling_median(values: list[float], window: int = 4) -> float | None:
    recent = values[-window:]
    if not recent:
        return None
    return statistics.median(recent)


def _resolve_catalog_path(repo_root: Path | None) -> Path | None:
    if repo_root is None:
        return None
    return (
        repo_root
        / "alters"
        / "product"
        / "behavior_metrics"
        / "catalog"
        / "behavior_metric_set_v0_2.yaml"
    )
