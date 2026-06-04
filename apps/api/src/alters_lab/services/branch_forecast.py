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
from alters_lab.services.personal_prior_adapter import adapt_personal_prior
from alters_lab.services.public_prior import list_approved_artifacts, list_contextual_priors, list_model_cards


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

    # Load approved population prior artifacts (data-backed only)
    approved_artifacts = list_approved_artifacts(repo_root=repo_root)
    contextual_priors = list_contextual_priors(repo_root=repo_root)
    model_cards = {c.model_id: c for c in list_model_cards(repo_root=repo_root)}
    artifacts_by_domain: dict[str, list] = {}
    for a in approved_artifacts:
        artifacts_by_domain.setdefault(a.domain, []).append(a)

    artifact_ids: list[str] = []
    model_card_ids: list[str] = []
    dataset_source_ids: list[str] = []
    artifact_classes: set[str] = set()
    for a in approved_artifacts:
        artifact_ids.append(a.artifact_id)
        artifact_classes.add(a.artifact_class)
        if a.model_id not in model_card_ids:
            model_card_ids.append(a.model_id)
        card = model_cards.get(a.model_id)
        if card:
            for dsid in card.source_dataset_ids:
                if dsid not in dataset_source_ids:
                    dataset_source_ids.append(dsid)

    # Best artifact class (highest priority among all approved artifacts)
    best_artifact_class = max(
        artifact_classes, key=_artifact_class_priority, default="none"
    ) if artifact_classes else "none"

    # Determine aggregate artifact class
    if not artifact_classes:
        agg_class = "none"
    elif len(artifact_classes) == 1:
        agg_class = artifact_classes.pop()
    else:
        agg_class = "mixed"

    contextual_prior_ids = [a.artifact_id for a in contextual_priors]

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

    # Aggregate calibration_metrics from best model card (calibrated_model > data_backed_baseline)
    agg_calibration_metrics: dict[str, float | None] = {}
    # Determine strength level from best approved artifact
    strength_priority = {"strong_calibrated": 3, "data_backed": 2, "contextual": 1, "none": 0}
    best_strength = "none"
    for a in approved_artifacts:
        card = model_cards.get(a.model_id)
        sl = _strength_level(a.artifact_class, card.approval_level if card else "unapproved")
        if strength_priority.get(sl, 0) > strength_priority.get(best_strength, 0):
            best_strength = sl
        if card and card.calibration_metrics:
            cm = card.calibration_metrics
            if cm.brier_score is not None:
                agg_calibration_metrics.setdefault("brier_score", cm.brier_score)
            if cm.calibration_slope is not None:
                agg_calibration_metrics.setdefault("calibration_slope", cm.calibration_slope)
            if cm.auc is not None:
                agg_calibration_metrics.setdefault("auc", cm.auc)
            if cm.r2 is not None:
                agg_calibration_metrics.setdefault("r2", cm.r2)
            if agg_calibration_metrics:
                break  # Take metrics from the highest-priority artifact

    route_b = RouteBPopulationPrior(
        available=anchor.route_b_available or len(approved_artifacts) > 0,
        prior_direction=prior_dir,  # type: ignore[arg-type]
        transfer_risk=transfer_risk,  # type: ignore[arg-type]
        evidence_strength=evidence_strength,  # type: ignore[arg-type]
        population_percentile=None,  # No numeric prior data by default
        deviation_from_baseline=None,  # No numeric baseline by default
        explanation=route_b_explanation,
        artifact_ids=artifact_ids,
        model_card_ids=model_card_ids,
        dataset_source_ids=dataset_source_ids,
        approved_artifact_count=len(approved_artifacts),
        artifact_class=agg_class,  # type: ignore[arg-type]
        contextual_prior_ids=contextual_prior_ids,
        calibration_metrics=agg_calibration_metrics,
        strength_level=best_strength,  # type: ignore[arg-type]
    )

    # Domain-level predictions from anchor data
    domain_predictions = _build_domain_predictions(
        anchor.domain_anchors if anchor.route_b_available else [],
        route_a_available,
        overall_direction=trajectory if route_a_available else "unknown",
        artifacts_by_domain=artifacts_by_domain,
        model_cards=model_cards,
    )

    # Personal prior adapter — combines Route A, Route B, external evidence
    behavior_metric_count = sum(1 for t in trend_resp.trends if t.direction in ("improving", "declining", "stable"))
    adapter_result = adapt_personal_prior(
        domain_predictions=domain_predictions,
        route_a=route_a,
        behavior_metric_count=behavior_metric_count,
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
        best_artifact_class=best_artifact_class,
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
        personal_prior_adapter=adapter_result,
        limitations=limitations,
        next_evidence_to_collect=next_evidence,
        best_artifact_class=best_artifact_class,
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
    best_artifact_class: str = "none",
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
        # Boost credibility for calibrated models (they're individually validated)
        if _artifact_class_priority(best_artifact_class) >= 3 and credibility == "medium":
            credibility = "high"
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


def _artifact_class_priority(cls: str) -> int:
    """Higher return = preferred artifact class."""
    return {"calibrated_model": 3, "data_backed_baseline": 2, "contextual_prior": 1}.get(cls, 0)


def _strength_level(artifact_class: str, approval_level: str) -> str:
    """Map artifact_class + approval_level to a strength level for display.

    Promotion gate:
    - calibrated_model + route_b_approved → "strong_calibrated"
    - data_backed_baseline + route_b_approved → "data_backed"
    - contextual_prior or lab_only → "contextual"
    - none → "none"
    """
    if artifact_class == "calibrated_model" and approval_level == "route_b_approved":
        return "strong_calibrated"
    if artifact_class == "data_backed_baseline" and approval_level == "route_b_approved":
        return "data_backed"
    if artifact_class in ("contextual_prior", "calibrated_model", "data_backed_baseline"):
        return "contextual"
    return "none"


def _build_domain_predictions(
    domain_anchors: list,
    route_a_available: bool,
    overall_direction: str,
    artifacts_by_domain: dict[str, list] | None = None,
    model_cards: dict[str, object] | None = None,
) -> list[DomainForecastPrediction]:
    """Build per-domain predictions from anchor data.

    Source priority:
    1. route_a_direction from domain anchor (if available and not insufficient_data)
    2. route_b_prior_direction from domain anchor (if not unknown)
    3. overall_fallback using overall trajectory
    """
    predictions: list[DomainForecastPrediction] = []
    artifacts_by_domain = artifacts_by_domain or {}
    model_cards = model_cards or {}

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

        # Look up approved artifact for this domain
        domain_artifacts = artifacts_by_domain.get(domain, [])
        best_artifact = None
        best_card = None
        if domain_artifacts:
            # Sort by artifact_class priority (calibrated_model > data_backed_baseline > contextual_prior),
            # then by transfer_risk (low > medium > high)
            risk_order = {"low": 0, "medium": 1, "high": 2}
            best_artifact = min(
                domain_artifacts,
                key=lambda a: (
                    -_artifact_class_priority(getattr(a, "artifact_class", "none") or "none"),
                    risk_order.get(a.transfer_risk, 2),
                ),
            )
            best_card = model_cards.get(best_artifact.model_id)

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

        # Use artifact transfer risk if available, overriding anchor risk
        domain_strength = "none"
        if best_artifact:
            t_risk = best_artifact.transfer_risk
            ev_strength = "moderate" if best_artifact.confidence in ("medium", "high") else "weak"
            artifact_cls = getattr(best_artifact, "artifact_class", "none") or "none"
            approval_lvl = best_card.approval_level if best_card else "unapproved"
            domain_strength = _strength_level(artifact_cls, approval_lvl)
            if artifact_cls == "calibrated_model":
                base_confidence = "high"
            elif artifact_cls == "data_backed_baseline":
                base_confidence = "medium"
            else:
                base_confidence = "low"

        predictions.append(DomainForecastPrediction(
            domain=domain,  # type: ignore[arg-type]
            route_a_direction=route_a_dir,  # type: ignore[arg-type]
            route_b_prior_direction=route_b_dir,  # type: ignore[arg-type]
            predicted_direction=predicted,  # type: ignore[arg-type]
            predicted_direction_source=source,  # type: ignore[arg-type]
            confidence=base_confidence if best_artifact else "low",
            evidence_strength=ev_strength,  # type: ignore[arg-type]
            transfer_risk=t_risk,  # type: ignore[arg-type]
            explanation=explanation,
            artifact_id=best_artifact.artifact_id if best_artifact else None,
            model_card_id=best_artifact.model_id if best_artifact else None,
            dataset_source_id=best_card.source_dataset_ids[0] if best_card and best_card.source_dataset_ids else None,
            approved_for_route_b=best_card.approval_level == "route_b_approved" if best_card else False,
            artifact_class=best_artifact.artifact_class if best_artifact else "none",  # type: ignore[arg-type]
            strength_level=domain_strength,  # type: ignore[arg-type]
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
