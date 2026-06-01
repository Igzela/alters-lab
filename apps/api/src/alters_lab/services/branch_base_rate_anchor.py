"""Branch base-rate anchor service.

Combines Route A (personal behavior trends) and Route B (literature priors)
into a cautious base-rate anchor report. Does NOT produce exact probabilities.
"""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.behavior_metric_trend import BehaviorMetricTrendRequest
from alters_lab.schemas.branch_base_rate_anchor import (
    BranchBaseRateAnchorRequest,
    BranchBaseRateAnchorResult,
    DomainAnchor,
    PriorSummary,
)
from alters_lab.schemas.literature_priors import LiteraturePriorCatalog
from alters_lab.services.behavior_metric_trend import analyze_behavior_trends
from alters_lab.services.branch_outcome_targets import list_targets_for_branch
from alters_lab.services.literature_priors import get_catalog
from alters_lab.services.predictor_profile import list_profiles
from alters_lab.services.p6_runtime import utc_now

_DOMAINS = ["career_education", "financial", "health", "relationship", "subjective_wellbeing"]


def analyze_base_rate_anchor(
    request: BranchBaseRateAnchorRequest,
    repo_root: Path | None = None,
) -> BranchBaseRateAnchorResult:
    limitations: list[str] = []

    # Route A: personal behavior trends
    trend_req = BehaviorMetricTrendRequest(lookback_weeks=request.lookback_weeks)
    trend_resp = analyze_behavior_trends(trend_req, repo_root=repo_root)
    route_a_available = any(t.direction != "insufficient_data" for t in trend_resp.trends)

    # Route B: literature priors
    route_b_available = False
    catalog: LiteraturePriorCatalog | None = None
    try:
        catalog = get_catalog(repo_root)
        route_b_available = True
    except FileNotFoundError:
        limitations.append("Literature prior catalog not found; Route B unavailable")

    # Load outcome targets for limitations
    targets = list_targets_for_branch(request.branch_id, repo_root=repo_root)
    if not targets:
        limitations.append("No outcome targets defined for this branch; prediction accuracy cannot be verified")

    # Load predictor profile if requested
    if request.profile_id:
        try:
            profiles = list_profiles(repo_root=repo_root)
            matching = [p for p in profiles if p.profile_id == request.profile_id]
            if not matching:
                limitations.append(f"Predictor profile {request.profile_id} not found")
        except Exception:
            limitations.append("Could not load predictor profiles")

    # Build domain anchors
    domain_anchors: list[DomainAnchor] = []
    if catalog:
        for domain in _DOMAINS:
            anchor = _build_domain_anchor(domain, trend_resp.trends, catalog, route_a_available)
            domain_anchors.append(anchor)

    # Build prior summary
    prior_summary = _build_prior_summary(catalog, domain_anchors)

    return BranchBaseRateAnchorResult(
        branch_id=request.branch_id,
        generated_at=utc_now(),
        route_a_available=route_a_available,
        route_b_available=route_b_available,
        prior_summary=prior_summary,
        domain_anchors=domain_anchors,
        limitations=limitations,
    )


def _build_domain_anchor(
    domain: str,
    trends: list,
    catalog: LiteraturePriorCatalog,
    route_a_available: bool,
) -> DomainAnchor:
    # Map domain to relevant metric directions
    domain_trend_directions = []
    for trend in trends:
        # Find if this metric is linked to this domain via constructs
        for cdl in catalog.construct_domain_links:
            if cdl.predicted_domain == domain:
                for construct in catalog.constructs:
                    if construct.construct_id == cdl.construct_id:
                        if trend.metric_id in construct.measured_by.behavior_metrics:
                            if trend.direction != "insufficient_data":
                                domain_trend_directions.append(trend.direction)

    if domain_trend_directions:
        improving_count = domain_trend_directions.count("improving")
        declining_count = domain_trend_directions.count("declining")
        if improving_count > declining_count:
            route_a_dir = "improving"
        elif declining_count > improving_count:
            route_a_dir = "declining"
        else:
            route_a_dir = "stable"
    elif route_a_available:
        route_a_dir = "insufficient_data"
    else:
        route_a_dir = "insufficient_data"

    # Route B: find priors for this domain
    domain_priors = [p for p in catalog.priors if p.predicted_domain == domain]
    if domain_priors:
        favorable = sum(1 for p in domain_priors if p.base_rate_direction == "favorable")
        unfavorable = sum(1 for p in domain_priors if p.base_rate_direction == "unfavorable")
        mixed = sum(1 for p in domain_priors if p.base_rate_direction == "mixed")
        if favorable > unfavorable and favorable > mixed:
            route_b_dir = "favorable"
        elif unfavorable > favorable and unfavorable > mixed:
            route_b_dir = "unfavorable"
        elif mixed > 0:
            route_b_dir = "mixed"
        else:
            route_b_dir = "unknown"
        strengths = [p.prior_confidence for p in domain_priors]
        risks = [p.transfer_risk for p in domain_priors]
        evidence_strength = _aggregate_strength(strengths)
        transfer_risk = _aggregate_risk(risks)
        explanation = "; ".join(p.explanation for p in domain_priors[:2])
    else:
        route_b_dir = "unknown"
        evidence_strength = "weak"
        transfer_risk = "high"
        explanation = f"No literature priors found for domain: {domain}"

    return DomainAnchor(
        domain=domain,  # type: ignore[arg-type]
        route_a_direction=route_a_dir,  # type: ignore[arg-type]
        route_b_prior_direction=route_b_dir,  # type: ignore[arg-type]
        evidence_strength=evidence_strength,  # type: ignore[arg-type]
        transfer_risk=transfer_risk,  # type: ignore[arg-type]
        explanation=explanation,
    )


def _build_prior_summary(
    catalog: LiteraturePriorCatalog | None,
    domain_anchors: list[DomainAnchor],
) -> PriorSummary:
    if not domain_anchors:
        return PriorSummary(
            overall_prior_direction="unknown",
            confidence="low",
            transfer_risk="high",
            explanation="No domain anchors available",
        )

    favorable = sum(1 for a in domain_anchors if a.route_b_prior_direction == "favorable")
    unfavorable = sum(1 for a in domain_anchors if a.route_b_prior_direction == "unfavorable")
    mixed = sum(1 for a in domain_anchors if a.route_b_prior_direction == "mixed")

    if favorable > unfavorable and favorable > mixed:
        overall = "favorable"
    elif unfavorable > favorable and unfavorable > mixed:
        overall = "unfavorable"
    elif mixed > 0:
        overall = "mixed"
    else:
        overall = "unknown"

    strengths = [a.evidence_strength for a in domain_anchors]
    risks = [a.transfer_risk for a in domain_anchors]

    return PriorSummary(
        overall_prior_direction=overall,  # type: ignore[arg-type]
        confidence=_aggregate_strength_to_confidence(strengths),  # type: ignore[arg-type]
        transfer_risk=_aggregate_risk(risks),  # type: ignore[arg-type]
        explanation="Aggregated from domain-level literature priors",
    )


def _aggregate_strength(strengths: list[str]) -> str:
    """Aggregate evidence_strength values (weak/moderate/strong)."""
    if not strengths:
        return "weak"
    if "strong" in strengths and strengths.count("strong") >= len(strengths) / 2:
        return "strong"
    if "weak" in strengths and strengths.count("weak") >= len(strengths) / 2:
        return "weak"
    return "moderate"


def _aggregate_strength_to_confidence(strengths: list[str]) -> str:
    """Aggregate evidence_strength values into confidence (low/medium/high)."""
    agg = _aggregate_strength(strengths)
    if agg == "strong":
        return "high"
    if agg == "weak":
        return "low"
    return "medium"


def _aggregate_risk(risks: list[str]) -> str:
    if not risks:
        return "high"
    if "high" in risks:
        return "high"
    if risks.count("medium") > len(risks) / 2:
        return "medium"
    return "low"
