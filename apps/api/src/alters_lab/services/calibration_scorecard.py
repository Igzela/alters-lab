"""Calibration scorecard service — aggregate forecast evaluation statistics."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.calibration_scorecard import (
    CalibrationScorecard,
    DomainScore,
    SignalQuality,
    SourceHitRates,
)
from alters_lab.schemas.forecast_evaluation import ForecastEvaluationRecord
from alters_lab.services.forecast_evaluation import list_evaluations

_MIN_EVALUATIONS_FOR_MEDIUM = 5
_MIN_EVALUATIONS_FOR_HIGH = 15


def _compute_confidence(total: int) -> str:
    if total >= _MIN_EVALUATIONS_FOR_HIGH:
        return "high"
    if total >= _MIN_EVALUATIONS_FOR_MEDIUM:
        return "medium"
    return "low"


def build_scorecard(repo_root: Path | None = None) -> CalibrationScorecard:
    """Build a calibration scorecard from all forecast evaluations."""
    evaluations = list_evaluations(repo_root=repo_root)
    total = len(evaluations)

    if total == 0:
        return CalibrationScorecard(
            limitations=["No evaluations available. Complete forecast evaluations to build calibration data."],
        )

    hit = 0
    miss = 0
    partial = 0
    unknown = 0
    domain_hits: dict[str, int] = {}
    domain_counts: dict[str, int] = {}
    domain_strengths: dict[str, dict[str, int]] = {}
    all_predictive: list[str] = []
    all_misleading: list[str] = []

    # Per-source hit tracking
    ra_hit = ra_miss = ra_partial = ra_unknown = 0
    rb_hit = rb_miss = rb_partial = rb_unknown = 0
    adapter_hit = adapter_miss = adapter_partial = adapter_unknown = 0
    conflict_outcomes: dict[str, int] = {}

    for ev in evaluations:
        if ev.overall_result == "hit":
            hit += 1
        elif ev.overall_result == "miss":
            miss += 1
        elif ev.overall_result == "partial":
            partial += 1
        else:
            unknown += 1

        for dr in ev.domain_results:
            domain_counts[dr.domain] = domain_counts.get(dr.domain, 0) + 1
            if dr.match_result == "hit":
                domain_hits[dr.domain] = domain_hits.get(dr.domain, 0) + 1
            strengths = domain_strengths.setdefault(dr.domain, {})
            strengths[dr.evidence_strength] = strengths.get(dr.evidence_strength, 0) + 1

            # Track per-source match results
            if dr.route_a_match_result:
                if dr.route_a_match_result == "hit":
                    ra_hit += 1
                elif dr.route_a_match_result == "miss":
                    ra_miss += 1
                elif dr.route_a_match_result == "partial":
                    ra_partial += 1
                else:
                    ra_unknown += 1

            if dr.route_b_match_result:
                if dr.route_b_match_result == "hit":
                    rb_hit += 1
                elif dr.route_b_match_result == "miss":
                    rb_miss += 1
                elif dr.route_b_match_result == "partial":
                    rb_partial += 1
                else:
                    rb_unknown += 1

            if dr.adapter_match_result:
                if dr.adapter_match_result == "hit":
                    adapter_hit += 1
                elif dr.adapter_match_result == "miss":
                    adapter_miss += 1
                elif dr.adapter_match_result == "partial":
                    adapter_partial += 1
                else:
                    adapter_unknown += 1

            # Track conflict outcomes
            if dr.conflict_level_at_forecast_time and dr.conflict_level_at_forecast_time != "none":
                key = f"{dr.conflict_level_at_forecast_time}_{dr.match_result}"
                conflict_outcomes[key] = conflict_outcomes.get(key, 0) + 1

        all_predictive.extend(ev.predictive_signals)
        all_misleading.extend(ev.misleading_signals)

    # Build per-domain scores
    by_domain: list[DomainScore] = []
    for domain in sorted(domain_counts):
        count = domain_counts[domain]
        hits = domain_hits.get(domain, 0)
        hit_rate = hits / count if count > 0 else None
        by_domain.append(DomainScore(
            domain=domain,
            hit_rate=hit_rate,
            evidence_strength_distribution=domain_strengths.get(domain, {}),
        ))

    confidence = _compute_confidence(total)
    limitations: list[str] = []
    if total < _MIN_EVALUATIONS_FOR_MEDIUM:
        limitations.append(f"Only {total} evaluation(s) — calibration confidence is low. Need at least {_MIN_EVALUATIONS_FOR_MEDIUM} for medium confidence.")
    if unknown > 0:
        limitations.append(f"{unknown} evaluation(s) had unknown results due to missing evidence.")

    return CalibrationScorecard(
        total_evaluations=total,
        hit_count=hit,
        miss_count=miss,
        partial_count=partial,
        unknown_count=unknown,
        by_domain=by_domain,
        signal_quality=SignalQuality(
            predictive_signals=list(set(all_predictive)),
            misleading_signals=list(set(all_misleading)),
        ),
        source_hit_rates=SourceHitRates(
            route_a_hit_count=ra_hit,
            route_a_miss_count=ra_miss,
            route_a_partial_count=ra_partial,
            route_a_unknown_count=ra_unknown,
            route_b_hit_count=rb_hit,
            route_b_miss_count=rb_miss,
            route_b_partial_count=rb_partial,
            route_b_unknown_count=rb_unknown,
            adapter_hit_count=adapter_hit,
            adapter_miss_count=adapter_miss,
            adapter_partial_count=adapter_partial,
            adapter_unknown_count=adapter_unknown,
            conflict_outcomes=conflict_outcomes,
        ),
        calibration_confidence=confidence,
        limitations=limitations,
    )
