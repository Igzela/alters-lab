"""Calibration scorecard service — aggregate forecast evaluation statistics."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.calibration_scorecard import (
    CalibrationScorecard,
    DomainScore,
    SignalQuality,
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
        calibration_confidence=confidence,
        limitations=limitations,
    )
