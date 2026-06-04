"""Personal prior adapter service.

Combines Route A personal evidence, Route B public priors, external evidence,
outcome targets, and calibration history into per-domain adapted forecasts.

Rules:
1. External evidence can override weak Route B.
2. Strong Route A can reduce pessimism from Route B, but cannot erase transfer risk.
3. strong_calibrated Route B increases confidence when aligned with Route A.
4. data_backed Route B supports baseline context but cannot create high confidence alone.
5. contextual prior cannot drive adjusted_forecast_direction.
6. Missing or stale behavior data lowers forecast_readiness.
7. Unknown remains unknown.
8. No exact probabilities.
"""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.personal_prior_adapter import (
    EvidenceComponent,
    PersonalPriorAdapterResult,
    PersonalPriorAdapterSummary,
)
from alters_lab.schemas.branch_forecast import DomainForecastPrediction, RouteAPersonalEvidence
from alters_lab.schemas.external_evidence import ExternalEvidenceRecord
from alters_lab.schemas.forecast_snapshot import DomainPrediction

_ALL_DOMAINS = [
    "career_education",
    "financial",
    "health",
    "relationship",
    "subjective_wellbeing",
]

_ROUTE_B_TO_DIRECTION = {
    "favorable": "improving",
    "unfavorable": "declining",
    "mixed": "mixed",
}

_STRENGTH_PRIORITY = {"strong_calibrated": 3, "data_backed": 2, "contextual": 1, "unavailable": 0}


def _map_route_b_direction(route_b_dir: str) -> str:
    return _ROUTE_B_TO_DIRECTION.get(route_b_dir, "unknown")


def _determine_alignment(
    route_a_dir: str,
    route_b_dir: str,
    external_dir: str,
    route_b_strength: str,
) -> str:
    """Determine evidence alignment across sources."""
    has_route_a = route_a_dir not in ("unknown", "insufficient_data")
    has_route_b = route_b_dir != "unknown" and route_b_strength != "unavailable"
    has_external = external_dir != "unknown"

    if not has_route_a and not has_route_b:
        return "insufficient_data"
    if has_route_a and not has_route_b:
        return "route_a_only"
    if has_route_b and not has_route_a:
        return "route_b_only"

    # Both available — check alignment
    ra_mapped = route_a_dir
    rb_mapped = _map_route_b_direction(route_b_dir)

    if ra_mapped == rb_mapped:
        return "aligned"
    if ra_mapped == "mixed" or rb_mapped == "mixed":
        return "conflicted"
    if ra_mapped == "unknown" or rb_mapped == "unknown":
        return "insufficient_data"
    # Opposite directions
    return "conflicted"


def _determine_conflict_level(
    alignment: str,
    route_a_confidence: str,
    route_b_strength: str,
) -> str:
    """Determine conflict severity."""
    if alignment != "conflicted":
        return "none"
    if route_b_strength == "strong_calibrated" and route_a_confidence == "high":
        return "high"
    if route_b_strength == "strong_calibrated" or route_a_confidence == "high":
        return "medium"
    return "low"


def _resolve_adjusted_direction(
    route_a_dir: str,
    route_b_dir: str,
    external_dir: str,
    route_b_strength: str,
    route_a_confidence: str,
) -> str:
    """Resolve the adjusted forecast direction.

    Priority:
    1. External evidence (if strong and available)
    2. Route A (if available with data)
    3. Route B strong_calibrated (if Route A insufficient)
    4. Route B data_backed (only supports, doesn't drive)
    5. Unknown
    """
    has_route_a = route_a_dir not in ("unknown", "insufficient_data")
    has_external = external_dir != "unknown"

    # External evidence can override weak Route B
    if has_external:
        return external_dir

    # Route A drives direction when available
    if has_route_a:
        return route_a_dir

    # Route B strong_calibrated can drive when Route A is insufficient
    if route_b_strength == "strong_calibrated":
        return _map_route_b_direction(route_b_dir)

    # data_backed and contextual cannot drive direction
    return "unknown"


def _resolve_adjusted_confidence(
    route_a_dir: str,
    route_b_dir: str,
    external_dir: str,
    route_b_strength: str,
    route_a_confidence: str,
    alignment: str,
    conflict_level: str,
    has_behavior_data: bool,
    behavior_metric_count: int,
) -> tuple[str, list[str], list[str]]:
    """Resolve adjusted confidence. Returns (confidence, drivers, penalties)."""
    drivers: list[str] = []
    penalties: list[str] = []

    has_route_a = route_a_dir not in ("unknown", "insufficient_data")
    has_external = external_dir != "unknown"

    # Start with base confidence
    base = "low"

    if has_route_a and behavior_metric_count >= 3:
        base = "medium"
        drivers.append("Route A with 3+ behavior metrics")
    elif has_route_a:
        base = "low"
        penalties.append("Route A available but fewer than 3 behavior metrics")

    if has_external:
        if base == "medium":
            base = "high"
            drivers.append("External evidence confirms direction")
        else:
            base = "medium"
            drivers.append("External evidence present")

    # Route B alignment effects
    if alignment == "aligned":
        if route_b_strength == "strong_calibrated":
            if base == "medium":
                base = "high"
            drivers.append("Aligned with strong calibrated public model")
        elif route_b_strength == "data_backed":
            drivers.append("Aligned with data-backed public baseline")
    elif alignment == "conflicted":
        if conflict_level == "high":
            penalties.append("Strong conflict between personal evidence and calibrated public model")
            if base == "high":
                base = "medium"
        elif conflict_level == "medium":
            penalties.append("Moderate conflict between personal and public evidence")

    # Missing data penalties
    if not has_behavior_data:
        penalties.append("No personal behavior data available")
        base = "low"
    elif behavior_metric_count < 3:
        penalties.append("Limited behavior data (fewer than 3 metrics)")

    if route_b_strength == "unavailable":
        penalties.append("No public prior available for comparison")

    # data_backed alone cannot produce high confidence
    if route_b_strength == "data_backed" and not has_route_a and not has_external:
        if base == "high":
            base = "medium"
        penalties.append("Data-backed baseline alone cannot produce high confidence")

    return base, drivers, penalties


def _determine_readiness(
    domain_results: list[PersonalPriorAdapterResult],
    has_behavior_data: bool,
    behavior_metric_count: int,
) -> tuple[str, list[str], list[str]]:
    """Determine overall forecast readiness."""
    reasons: list[str] = []
    blockers: list[str] = []

    if not has_behavior_data:
        blockers.append("No personal behavior data available")
        return "insufficient", reasons, blockers

    if behavior_metric_count < 3:
        blockers.append("Fewer than 3 behavior metrics tracked")

    aligned_count = sum(1 for d in domain_results if d.alignment == "aligned")
    conflicted_count = sum(1 for d in domain_results if d.alignment == "conflicted")
    strong_calibrated_count = sum(1 for d in domain_results if d.route_b_strength_level == "strong_calibrated")

    if aligned_count >= 3 and strong_calibrated_count >= 2:
        reasons.append("Multiple domains aligned with strong calibrated models")
        readiness = "strong"
    elif aligned_count >= 2:
        reasons.append("Multiple domains with aligned evidence")
        readiness = "usable"
    elif behavior_metric_count >= 3:
        reasons.append("Sufficient behavior data for provisional forecast")
        readiness = "provisional"
    else:
        readiness = "provisional"

    if conflicted_count >= 3:
        blockers.append("Majority of domains show conflicting evidence")
        if readiness == "strong":
            readiness = "usable"

    if blockers and readiness == "strong":
        readiness = "usable"

    return readiness, reasons, blockers


def adapt_personal_prior(
    domain_predictions: list[DomainForecastPrediction],
    route_a: RouteAPersonalEvidence,
    external_evidence: list[ExternalEvidenceRecord] | None = None,
    behavior_metric_count: int = 0,
) -> PersonalPriorAdapterSummary:
    """Run the personal prior adapter on branch forecast data.

    Args:
        domain_predictions: Per-domain predictions from branch forecast.
        route_a: Route A personal evidence summary.
        external_evidence: External evidence records (optional).
        behavior_metric_count: Number of behavior metrics with data.

    Returns:
        PersonalPriorAdapterSummary with per-domain results.
    """
    external_evidence = external_evidence or []
    has_behavior_data = route_a.available and behavior_metric_count > 0

    # Index external evidence by domain
    evidence_by_domain: dict[str, list[ExternalEvidenceRecord]] = {}
    for e in external_evidence:
        evidence_by_domain.setdefault(e.domain, []).append(e)

    # Build per-domain results
    domain_results: list[PersonalPriorAdapterResult] = []
    evidence_components: list[EvidenceComponent] = []

    for dp in domain_predictions:
        domain = dp.domain

        # Extract directions
        route_a_dir = dp.route_a_direction
        route_b_dir = dp.route_b_prior_direction
        route_b_strength = dp.strength_level if hasattr(dp, "strength_level") else "unavailable"
        if route_b_strength == "none":
            route_b_strength = "unavailable"

        # External evidence for this domain
        domain_evidence = evidence_by_domain.get(domain, [])
        external_dir = "unknown"
        if domain_evidence:
            positives = sum(1 for e in domain_evidence if e.polarity == "positive")
            negatives = sum(1 for e in domain_evidence if e.polarity == "negative")
            if positives > negatives:
                external_dir = "improving"
            elif negatives > positives:
                external_dir = "declining"
            elif positives > 0 and negatives > 0:
                external_dir = "mixed"
            else:
                external_dir = "stable"

        # Route A confidence estimate
        route_a_confidence = "low"
        if route_a_dir not in ("unknown", "insufficient_data"):
            if behavior_metric_count >= 3:
                route_a_confidence = "medium"
            if behavior_metric_count >= 5:
                route_a_confidence = "high"

        # Compute alignment
        alignment = _determine_alignment(route_a_dir, route_b_dir, external_dir, route_b_strength)

        # Compute conflict level
        conflict_level = _determine_conflict_level(alignment, route_a_confidence, route_b_strength)

        # Resolve adjusted direction
        adjusted_direction = _resolve_adjusted_direction(
            route_a_dir, route_b_dir, external_dir, route_b_strength, route_a_confidence,
        )

        # Resolve adjusted confidence
        adjusted_confidence, drivers, penalties = _resolve_adjusted_confidence(
            route_a_dir, route_b_dir, external_dir, route_b_strength,
            route_a_confidence, alignment, conflict_level,
            has_behavior_data, behavior_metric_count,
        )

        # Next evidence suggestions
        next_evidence: list[str] = []
        if route_a_dir in ("unknown", "insufficient_data"):
            next_evidence.append("Collect behavior metric data for this domain")
        if route_b_strength == "unavailable":
            next_evidence.append("No public prior available — external evidence especially valuable")
        if not domain_evidence:
            next_evidence.append("Add external evidence for this domain to improve forecast accuracy")
        if conflict_level in ("medium", "high"):
            next_evidence.append("Conflict detected — collect more evidence to resolve direction")

        # Build explanation
        explanation_parts: list[str] = []
        if adjusted_direction == "unknown":
            explanation_parts.append("Insufficient data to determine direction.")
        else:
            explanation_parts.append(f"Adjusted direction: {adjusted_direction}.")
        if alignment == "aligned":
            explanation_parts.append("Personal and public evidence align.")
        elif alignment == "conflicted":
            explanation_parts.append(f"Conflict detected ({conflict_level}): personal evidence and public prior disagree.")
        elif alignment == "route_a_only":
            explanation_parts.append("Direction based on personal evidence only — no public prior available.")
        elif alignment == "route_b_only":
            explanation_parts.append("Direction based on public prior — insufficient personal data.")
        if route_b_strength == "strong_calibrated":
            explanation_parts.append("Public prior is a strong calibrated model — transfer risk still applies.")
        elif route_b_strength == "data_backed":
            explanation_parts.append("Public prior is a descriptive baseline — supports context but does not drive direction.")
        elif route_b_strength == "contextual":
            explanation_parts.append("Public prior is contextual literature only — not driving forecast.")

        result = PersonalPriorAdapterResult(
            domain=domain,
            route_a_direction=route_a_dir,
            route_b_direction=route_b_dir,
            route_b_strength_level=route_b_strength,
            external_evidence_direction=external_dir,
            alignment=alignment,
            conflict_level=conflict_level,
            adjusted_forecast_direction=adjusted_direction,
            adjusted_confidence=adjusted_confidence,
            confidence_drivers=drivers,
            confidence_penalties=penalties,
            next_evidence_to_collect=next_evidence,
            explanation=" ".join(explanation_parts),
        )
        domain_results.append(result)

        # Build evidence components for traceability
        if route_a_dir not in ("unknown", "insufficient_data"):
            evidence_components.append(EvidenceComponent(
                source="route_a_behavior",
                domain=domain,
                direction=route_a_dir,
                strength="medium" if behavior_metric_count >= 3 else "weak",
                confidence=route_a_confidence,
                explanation=f"Route A behavior direction: {route_a_dir}",
            ))
        if route_b_dir != "unknown" and route_b_strength != "unavailable":
            evidence_components.append(EvidenceComponent(
                source="route_b_public_prior",
                domain=domain,
                direction=_map_route_b_direction(route_b_dir),
                strength="strong" if route_b_strength == "strong_calibrated" else ("medium" if route_b_strength == "data_backed" else "weak"),
                confidence="high" if route_b_strength == "strong_calibrated" else ("medium" if route_b_strength == "data_backed" else "low"),
                explanation=f"Route B prior: {route_b_dir} ({route_b_strength})",
            ))
        if domain_evidence:
            evidence_components.append(EvidenceComponent(
                source="external_evidence",
                domain=domain,
                direction=external_dir,
                strength="strong" if any(e.objective_strength == "strong" for e in domain_evidence) else "medium",
                confidence="high" if len(domain_evidence) >= 2 else "medium",
                explanation=f"{len(domain_evidence)} external evidence record(s)",
            ))

    # Overall alignment
    alignments = [d.alignment for d in domain_results]
    if all(a == "aligned" for a in alignments):
        overall_alignment = "aligned"
    elif all(a in ("insufficient_data", "route_a_only", "route_b_only") for a in alignments):
        overall_alignment = "insufficient_data"
    elif any(a == "conflicted" for a in alignments) and any(a == "aligned" for a in alignments):
        overall_alignment = "mixed"
    elif any(a == "conflicted" for a in alignments):
        overall_alignment = "conflicted"
    else:
        overall_alignment = "insufficient_data"

    conflict_levels = [d.conflict_level for d in domain_results]
    if "high" in conflict_levels:
        overall_conflict = "high"
    elif "medium" in conflict_levels:
        overall_conflict = "medium"
    elif "low" in conflict_levels:
        overall_conflict = "low"
    else:
        overall_conflict = "none"

    readiness, readiness_reasons, readiness_blockers = _determine_readiness(
        domain_results, has_behavior_data, behavior_metric_count,
    )

    return PersonalPriorAdapterSummary(
        domain_results=domain_results,
        overall_alignment=overall_alignment,
        overall_conflict_level=overall_conflict,
        forecast_readiness=readiness,
        readiness_reasons=readiness_reasons,
        readiness_blockers=readiness_blockers,
        evidence_components=evidence_components,
    )
