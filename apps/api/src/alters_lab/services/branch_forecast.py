"""Branch forecast service.

Combines Route A (personal evidence), Route B (literature priors),
calibration divergence, and outcome targets into a user-facing forecast report.

Separates evidence types. No life_score. No exact probabilities.
"""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.behavior_metric_trend import BehaviorMetricTrendRequest
from alters_lab.schemas.branch_base_rate_anchor import BranchBaseRateAnchorRequest
from alters_lab.schemas.branch_forecast import (
    BranchForecastRequest,
    BranchForecastResult,
    CalibrationDivergenceSummary,
    DomainForecastPrediction,
    ForecastSummary,
    OutcomeTargetSummary,
    RouteAPersonalEvidence,
    RouteBPopulationPrior,
)
from alters_lab.schemas.calibration_divergence import CalibrationDivergenceRequest
from alters_lab.services.action_alignment import list_action_alignment_scores
from alters_lab.services.behavior_metric_trend import analyze_behavior_trends
from alters_lab.services.branch_base_rate_anchor import analyze_base_rate_anchor
from alters_lab.services.branch_outcome_targets import list_targets_for_branch
from alters_lab.services.calibration_divergence import analyze_calibration_divergence
from alters_lab.services.p6_runtime import utc_now


def analyze_branch_forecast(
    request: BranchForecastRequest,
    repo_root: Path | None = None,
) -> BranchForecastResult:
    limitations: list[str] = []
    next_evidence: list[str] = []

    # Route A: personal evidence
    trend_req = BehaviorMetricTrendRequest(lookback_weeks=request.lookback_weeks)
    trend_resp = analyze_behavior_trends(trend_req, repo_root=repo_root)

    improving = sum(1 for t in trend_resp.trends if t.direction == "improving")
    declining = sum(1 for t in trend_resp.trends if t.direction == "declining")
    stable = sum(1 for t in trend_resp.trends if t.direction == "stable")
    insufficient = sum(1 for t in trend_resp.trends if t.direction == "insufficient_data")
    total_with_data = improving + declining + stable

    if total_with_data == 0:
        route_a_available = False
        behavior_summary = "No behavior metric data available for this lookback period"
        limitations.append("No personal behavior data available; Route A analysis cannot be performed")
        next_evidence.append("Collect at least 2 weeks of behavior metric data")
    else:
        route_a_available = True
        behavior_summary = f"{improving} improving, {declining} declining, {stable} stable across {total_with_data} metrics"
        if insufficient > 0:
            behavior_summary += f" ({insufficient} metrics with insufficient data)"

    milestone_summary = "No milestone data available"
    for t in trend_resp.trends:
        if t.metric_id == "key_milestone_progress":
            if t.direction == "insufficient_data":
                milestone_summary = "Insufficient milestone progress data"
                next_evidence.append("Track key milestone progress for at least 2 weeks")
            else:
                milestone_summary = f"Milestone progress: {t.direction} (slope: {t.slope:.4f}, {t.data_points} data points)"

    # Action alignment
    alignment_scores = list_action_alignment_scores(repo_root)
    if alignment_scores:
        latest = alignment_scores[-1]
        alignment_summary = f"Latest alignment score: {latest.action_alignment_score:.2f} ({latest.verdict_label})"
    else:
        alignment_summary = "No action alignment scores available"
        next_evidence.append("Complete a weekly review to generate action alignment scores")

    route_a = RouteAPersonalEvidence(
        available=route_a_available,
        behavior_trends_summary=behavior_summary,
        milestone_progress_summary=milestone_summary,
        action_alignment_summary=alignment_summary,
    )

    # Route B: literature priors via base-rate anchor
    anchor_req = BranchBaseRateAnchorRequest(
        branch_id=request.branch_id,
        profile_id=request.profile_id,
        lookback_weeks=request.lookback_weeks,
    )
    anchor = analyze_base_rate_anchor(anchor_req, repo_root=repo_root)

    if anchor.route_b_available and anchor.domain_anchors:
        favorable = sum(1 for a in anchor.domain_anchors if a.route_b_prior_direction == "favorable")
        unfavorable = sum(1 for a in anchor.domain_anchors if a.route_b_prior_direction == "unfavorable")
        if favorable > unfavorable:
            prior_dir = "favorable"
        elif unfavorable > favorable:
            prior_dir = "unfavorable"
        else:
            prior_dir = "mixed"

        risks = [a.transfer_risk for a in anchor.domain_anchors]
        strengths = [a.evidence_strength for a in anchor.domain_anchors]
        transfer_risk = "high" if "high" in risks else ("medium" if risks.count("medium") > len(risks) / 2 else "low")
        evidence_strength = "strong" if "strong" in strengths and strengths.count("strong") >= len(strengths) / 2 else ("weak" if strengths.count("weak") >= len(strengths) / 2 else "moderate")

        route_b_explanation = "; ".join(a.explanation for a in anchor.domain_anchors[:3])
    else:
        prior_dir = "unknown"
        transfer_risk = "high"
        evidence_strength = "weak"
        route_b_explanation = "Literature priors not available or no matching priors found"

    route_b = RouteBPopulationPrior(
        available=anchor.route_b_available,
        prior_direction=prior_dir,  # type: ignore[arg-type]
        transfer_risk=transfer_risk,  # type: ignore[arg-type]
        evidence_strength=evidence_strength,  # type: ignore[arg-type]
        population_percentile=None,  # No numeric prior data by default
        deviation_from_baseline=None,  # No numeric baseline by default
        explanation=route_b_explanation,
    )

    # Domain-level predictions from anchor data
    domain_predictions = _build_domain_predictions(
        anchor.domain_anchors if anchor.route_b_available else [],
        route_a_available,
        overall_direction=trajectory if route_a_available else "unknown",
    )

    # Calibration divergence
    div_req = CalibrationDivergenceRequest(
        branch_id=request.branch_id,
        lookback_weeks=request.lookback_weeks,
    )
    divergence = analyze_calibration_divergence(div_req, repo_root=repo_root)
    div_summary = CalibrationDivergenceSummary(
        divergence_status=divergence.divergence_status,
        flags=[f.model_dump() for f in divergence.flags],
    )

    # Outcome targets
    targets = list_targets_for_branch(request.branch_id, repo_root=repo_root)
    active = sum(1 for t in targets if t.status in ("planned", "active"))
    achieved = sum(1 for t in targets if t.status == "achieved")
    missed = sum(1 for t in targets if t.status == "missed")
    outcome_summary = OutcomeTargetSummary(
        active_targets=active,
        achieved_targets=achieved,
        missed_targets=missed,
    )

    if not targets:
        limitations.append("No outcome targets defined; cannot verify prediction accuracy")
        next_evidence.append("Define at least one objective outcome target for this branch")

    if not anchor.route_b_available:
        limitations.append("Route B (literature priors) unavailable")

    # Trajectory direction and confidence
    trajectory, confidence, credibility = _compute_trajectory(
        route_a_available=route_a_available,
        improving=improving,
        declining=declining,
        stable=stable,
        total_with_data=total_with_data,
        route_b_available=anchor.route_b_available,
        prior_dir=prior_dir,
        divergence_status=divergence.divergence_status,
        has_targets=len(targets) > 0,
        has_divergence_warnings=len(divergence.flags) > 0,
    )

    explanation = _build_explanation(trajectory, confidence, route_a_available, anchor.route_b_available, divergence.divergence_status)

    limitations.extend(divergence.limitations)

    return BranchForecastResult(
        branch_id=request.branch_id,
        generated_at=utc_now(),
        horizon_months=request.horizon_months,
        forecast_summary=ForecastSummary(
            trajectory_direction=trajectory,  # type: ignore[arg-type]
            confidence=confidence,  # type: ignore[arg-type]
            credibility=credibility,  # type: ignore[arg-type]
            explanation=explanation,
        ),
        route_a_personal_evidence=route_a,
        route_b_population_prior=route_b,
        calibration_divergence=div_summary,
        outcome_targets=outcome_summary,
        domain_predictions=domain_predictions,
        limitations=limitations,
        next_evidence_to_collect=next_evidence,
    )


def _compute_trajectory(
    route_a_available: bool,
    improving: int,
    declining: int,
    stable: int,
    total_with_data: int,
    route_b_available: bool,
    prior_dir: str,
    divergence_status: str,
    has_targets: bool,
    has_divergence_warnings: bool,
) -> tuple[str, str, str]:
    """Returns (trajectory_direction, confidence, credibility)."""

    if not route_a_available:
        return "unknown", "low", "low"

    if total_with_data == 0:
        return "unknown", "low", "low"

    # Direction from Route A
    if improving > declining and improving > stable:
        direction = "improving"
    elif declining > improving and declining > stable:
        direction = "declining"
    elif stable > improving and stable > declining:
        direction = "stable"
    elif improving > 0 and declining > 0:
        direction = "mixed"
    else:
        direction = "unknown"

    # Confidence: needs enough data, targets, no major divergence
    has_enough_data = total_with_data >= 3
    if has_enough_data and has_targets and not has_divergence_warnings:
        confidence = "high"
    elif has_enough_data and (has_targets or not has_divergence_warnings):
        confidence = "medium"
    else:
        confidence = "low"

    # Credibility: Route B adds credibility if available and aligned
    if route_b_available and prior_dir != "unknown":
        if direction == "improving" and prior_dir == "favorable":
            credibility = "high" if confidence == "high" else "medium"
        elif direction == "declining" and prior_dir == "unfavorable":
            credibility = "medium"
        else:
            credibility = "medium" if confidence != "low" else "low"
    else:
        credibility = confidence

    return direction, confidence, credibility


_ALL_DOMAINS = [
    "career_education",
    "financial",
    "health",
    "relationship",
    "subjective_wellbeing",
]


def _build_domain_predictions(
    domain_anchors: list,
    route_a_available: bool,
    overall_direction: str,
) -> list[DomainForecastPrediction]:
    """Build per-domain predictions from anchor data.

    Source priority:
    1. route_a_direction from domain anchor (if available and not insufficient_data)
    2. route_b_prior_direction from domain anchor (if not unknown)
    3. overall_fallback using overall trajectory
    """
    predictions: list[DomainForecastPrediction] = []

    # Index anchors by domain for lookup
    anchor_by_domain: dict[str, object] = {}
    for anchor in domain_anchors:
        anchor_by_domain[anchor.domain] = anchor

    for domain in _ALL_DOMAINS:
        anchor = anchor_by_domain.get(domain)

        if anchor is not None:
            route_a_dir = anchor.route_a_direction
            route_b_dir = anchor.route_b_prior_direction
            ev_strength = anchor.evidence_strength
            t_risk = anchor.transfer_risk
            anchor_explanation = anchor.explanation
        else:
            route_a_dir = "unknown"
            route_b_dir = "unknown"
            ev_strength = "weak"
            t_risk = "high"
            anchor_explanation = ""

        # Resolve predicted direction with source priority
        if route_a_available and route_a_dir not in ("insufficient_data", "unknown"):
            predicted = route_a_dir
            source = "route_a"
            explanation = f"Route A direction: {route_a_dir}. {anchor_explanation}"
        elif route_b_dir != "unknown":
            # Map route_b prior directions to predicted directions
            _r2d = {"favorable": "improving", "unfavorable": "declining", "mixed": "mixed"}
            predicted = _r2d.get(route_b_dir, "unknown")
            source = "route_b"
            explanation = f"Route B prior: {route_b_dir}. {anchor_explanation}"
        else:
            predicted = overall_direction if overall_direction != "unknown" else "unknown"
            source = "overall_fallback" if predicted != "unknown" else "unknown"
            explanation = (
                f"Using overall trajectory direction as fallback for {domain}."
                if predicted != "unknown"
                else f"No domain-specific data available for {domain}."
            )

        predictions.append(DomainForecastPrediction(
            domain=domain,  # type: ignore[arg-type]
            route_a_direction=route_a_dir,  # type: ignore[arg-type]
            route_b_prior_direction=route_b_dir,  # type: ignore[arg-type]
            predicted_direction=predicted,  # type: ignore[arg-type]
            predicted_direction_source=source,  # type: ignore[arg-type]
            confidence="low",  # will be refined by evaluation
            evidence_strength=ev_strength,  # type: ignore[arg-type]
            transfer_risk=t_risk,  # type: ignore[arg-type]
            explanation=explanation,
        ))

    return predictions


def _build_explanation(
    trajectory: str,
    confidence: str,
    route_a_available: bool,
    route_b_available: bool,
    divergence_status: str,
) -> str:
    parts = []
    if trajectory == "unknown":
        parts.append("Insufficient data to determine trajectory direction.")
    else:
        parts.append(f"Trajectory appears {trajectory} based on available evidence.")

    if not route_a_available:
        parts.append("No personal behavior data available for Route A analysis.")
    if not route_b_available:
        parts.append("Literature priors (Route B) unavailable.")

    if divergence_status == "diverging_positive_subjective":
        parts.append("Warning: subjective feeling improving while objective evidence declining.")
    elif divergence_status == "diverging_negative_subjective":
        parts.append("Note: you may be underestimating your actual progress.")

    parts.append(f"Confidence: {confidence}.")
    return " ".join(parts)
