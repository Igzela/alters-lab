"""Tests for personal prior adapter service."""

from __future__ import annotations

import pytest

from alters_lab.schemas.branch_forecast import DomainForecastPrediction, RouteAPersonalEvidence
from alters_lab.schemas.external_evidence import ExternalEvidenceRecord
from alters_lab.schemas.personal_prior_adapter import (
    EvidenceComponent,
    PersonalPriorAdapterResult,
    PersonalPriorAdapterSummary,
)
from alters_lab.services.personal_prior_adapter import (
    adapt_personal_prior,
    _determine_alignment,
    _determine_conflict_level,
    _resolve_adjusted_direction,
    _resolve_adjusted_confidence,
)


def _make_route_a(available: bool = True) -> RouteAPersonalEvidence:
    return RouteAPersonalEvidence(
        available=available,
        behavior_trends_summary="2 improving, 1 declining, 1 stable",
        milestone_progress_summary="on track",
        action_alignment_summary="aligned",
    )


def _make_domain_pred(
    domain: str = "career_education",
    route_a_dir: str = "improving",
    route_b_dir: str = "favorable",
    strength: str = "strong_calibrated",
) -> DomainForecastPrediction:
    return DomainForecastPrediction(
        domain=domain,
        route_a_direction=route_a_dir,
        route_b_prior_direction=route_b_dir,
        predicted_direction="improving",
        predicted_direction_source="route_a",
        confidence="medium",
        evidence_strength="moderate",
        transfer_risk="low",
        explanation="test",
        strength_level=strength,
    )


def _make_evidence(
    domain: str = "career_education",
    polarity: str = "positive",
    strength: str = "strong",
) -> ExternalEvidenceRecord:
    return ExternalEvidenceRecord(
        domain=domain,
        evidence_type="milestone_completed",
        description=f"Test {polarity} evidence",
        objective_strength=strength,
        polarity=polarity,
    )


# --- Alignment tests ---


def test_alignment_when_both_positive():
    assert _determine_alignment("improving", "favorable", "unknown", "strong_calibrated") == "aligned"


def test_alignment_when_opposite():
    assert _determine_alignment("improving", "unfavorable", "unknown", "strong_calibrated") == "conflicted"


def test_alignment_route_a_only():
    assert _determine_alignment("improving", "unknown", "unknown", "unavailable") == "route_a_only"


def test_alignment_route_b_only():
    assert _determine_alignment("unknown", "favorable", "unknown", "data_backed") == "route_b_only"


def test_alignment_insufficient():
    assert _determine_alignment("unknown", "unknown", "unknown", "unavailable") == "insufficient_data"


# --- Conflict level tests ---


def test_conflict_none_when_aligned():
    assert _determine_conflict_level("aligned", "medium", "strong_calibrated") == "none"


def test_conflict_high_when_strong_calibrated_vs_high_confidence():
    assert _determine_conflict_level("conflicted", "high", "strong_calibrated") == "high"


def test_conflict_medium_when_strong_calibrated():
    assert _determine_conflict_level("conflicted", "medium", "strong_calibrated") == "medium"


def test_conflict_low_otherwise():
    assert _determine_conflict_level("conflicted", "low", "data_backed") == "low"


# --- Adjusted direction tests ---


def test_external_evidence_overrides_weak_route_b():
    result = _resolve_adjusted_direction("unknown", "unfavorable", "improving", "data_backed", "low")
    assert result == "improving"


def test_route_a_drives_when_available():
    result = _resolve_adjusted_direction("improving", "unfavorable", "unknown", "strong_calibrated", "medium")
    assert result == "improving"


def test_strong_calibrated_drives_when_route_a_insufficient():
    result = _resolve_adjusted_direction("unknown", "favorable", "unknown", "strong_calibrated", "low")
    assert result == "improving"


def test_data_backed_does_not_drive_direction():
    result = _resolve_adjusted_direction("unknown", "favorable", "unknown", "data_backed", "low")
    assert result == "unknown"


def test_contextual_does_not_drive_direction():
    result = _resolve_adjusted_direction("unknown", "favorable", "unknown", "contextual", "low")
    assert result == "unknown"


def test_unknown_stays_unknown():
    result = _resolve_adjusted_direction("unknown", "unknown", "unknown", "unavailable", "low")
    assert result == "unknown"


# --- Adjusted confidence tests ---


def test_confidence_high_when_aligned_strong_calibrated():
    conf, drivers, penalties = _resolve_adjusted_confidence(
        "improving", "favorable", "unknown", "strong_calibrated",
        "medium", "aligned", "none", True, 4,
    )
    assert conf == "high"
    assert any("aligned" in d.lower() or "calibrated" in d.lower() for d in drivers)


def test_confidence_medium_when_data_backed_alone():
    conf, drivers, penalties = _resolve_adjusted_confidence(
        "unknown", "favorable", "unknown", "data_backed",
        "low", "route_b_only", "none", False, 0,
    )
    assert conf != "high"
    assert any("data-backed" in p.lower() or "baseline" in p.lower() for p in penalties)


def test_confidence_low_when_no_behavior_data():
    conf, drivers, penalties = _resolve_adjusted_confidence(
        "unknown", "unknown", "unknown", "unavailable",
        "low", "insufficient_data", "none", False, 0,
    )
    assert conf == "low"
    assert any("no personal" in p.lower() for p in penalties)


def test_confidence_penalized_on_high_conflict():
    conf, drivers, penalties = _resolve_adjusted_confidence(
        "improving", "unfavorable", "unknown", "strong_calibrated",
        "high", "conflicted", "high", True, 4,
    )
    assert any("conflict" in p.lower() for p in penalties)


# --- Full adapter tests ---


def test_strong_calibrated_aligned_increases_confidence():
    preds = [_make_domain_pred("career_education", "improving", "favorable", "strong_calibrated")]
    result = adapt_personal_prior(preds, _make_route_a(), behavior_metric_count=4)
    career = result.domain_results[0]
    assert career.alignment == "aligned"
    assert career.adjusted_forecast_direction == "improving"
    assert career.adjusted_confidence in ("medium", "high")


def test_data_backed_alone_cannot_produce_high_confidence():
    preds = [_make_domain_pred("health", "unknown", "favorable", "data_backed")]
    result = adapt_personal_prior(preds, _make_route_a(available=False), behavior_metric_count=0)
    health = result.domain_results[0]
    assert health.adjusted_confidence != "high"
    assert any("baseline" in p.lower() or "data-backed" in p.lower() for p in health.confidence_penalties)


def test_contextual_cannot_drive_direction():
    preds = [_make_domain_pred("relationship", "unknown", "favorable", "contextual")]
    result = adapt_personal_prior(preds, _make_route_a(available=False), behavior_metric_count=0)
    rel = result.domain_results[0]
    assert rel.adjusted_forecast_direction == "unknown"


def test_external_evidence_overrides_conflicting_route_b():
    preds = [_make_domain_pred("career_education", "unknown", "unfavorable", "data_backed")]
    evidence = [_make_evidence("career_education", "positive")]
    result = adapt_personal_prior(preds, _make_route_a(available=False), external_evidence=evidence, behavior_metric_count=0)
    career = result.domain_results[0]
    assert career.adjusted_forecast_direction == "improving"


def test_route_a_positive_route_b_negative_produces_conflict():
    preds = [_make_domain_pred("career_education", "improving", "unfavorable", "strong_calibrated")]
    result = adapt_personal_prior(preds, _make_route_a(), behavior_metric_count=4)
    career = result.domain_results[0]
    assert career.alignment == "conflicted"
    assert career.conflict_level in ("medium", "high")
    assert "conflict" in career.explanation.lower()


def test_missing_behavior_data_lowers_readiness():
    preds = [_make_domain_pred()]
    result = adapt_personal_prior(preds, _make_route_a(available=False), behavior_metric_count=0)
    assert result.forecast_readiness == "insufficient"
    assert any("no personal" in b.lower() for b in result.readiness_blockers)


def test_adapter_result_stored_in_snapshot():
    """Adapter result schema is serializable and can be stored."""
    preds = [_make_domain_pred()]
    result = adapt_personal_prior(preds, _make_route_a(), behavior_metric_count=4)
    dumped = result.model_dump(mode="json")
    assert "domain_results" in dumped
    assert "forecast_readiness" in dumped
    assert "evidence_components" in dumped


def test_no_life_score():
    preds = [_make_domain_pred()]
    result = adapt_personal_prior(preds, _make_route_a(), behavior_metric_count=4)
    dumped = str(result.model_dump())
    assert "life_score" not in dumped.lower()


def test_no_exact_probability():
    preds = [_make_domain_pred()]
    result = adapt_personal_prior(preds, _make_route_a(), behavior_metric_count=4)
    dumped = str(result.model_dump())
    assert "probability" not in dumped.lower()
    assert "percentile" not in dumped.lower()


def test_unknown_stays_unknown_in_adapter():
    preds = [DomainForecastPrediction(
        domain="relationship",
        route_a_direction="unknown",
        route_b_prior_direction="unknown",
        predicted_direction="unknown",
        predicted_direction_source="unknown",
        confidence="low",
        explanation="no data",
    )]
    result = adapt_personal_prior(preds, _make_route_a(available=False), behavior_metric_count=0)
    rel = result.domain_results[0]
    assert rel.adjusted_forecast_direction == "unknown"
    assert rel.adjusted_confidence == "low"


def test_all_five_domains_present():
    preds = [_make_domain_pred(d) for d in [
        "career_education", "financial", "health", "relationship", "subjective_wellbeing",
    ]]
    result = adapt_personal_prior(preds, _make_route_a(), behavior_metric_count=4)
    domains = {d.domain for d in result.domain_results}
    assert len(domains) == 5


def test_readiness_strong_when_aligned_and_calibrated():
    preds = [_make_domain_pred(d, "improving", "favorable", "strong_calibrated") for d in [
        "career_education", "financial", "health", "relationship", "subjective_wellbeing",
    ]]
    result = adapt_personal_prior(preds, _make_route_a(), behavior_metric_count=5)
    assert result.forecast_readiness in ("usable", "strong")
    assert result.overall_alignment == "aligned"


def test_evidence_components_populated():
    preds = [_make_domain_pred("career_education", "improving", "favorable", "strong_calibrated")]
    evidence = [_make_evidence("career_education", "positive")]
    result = adapt_personal_prior(preds, _make_route_a(), external_evidence=evidence, behavior_metric_count=4)
    sources = {ec.source for ec in result.evidence_components}
    assert "route_a_behavior" in sources
    assert "route_b_public_prior" in sources
    assert "external_evidence" in sources


def test_next_evidence_suggestions_when_missing():
    preds = [_make_domain_pred("health", "unknown", "unknown", "none")]
    result = adapt_personal_prior(preds, _make_route_a(available=False), behavior_metric_count=0)
    health = result.domain_results[0]
    assert len(health.next_evidence_to_collect) > 0
