"""Forecast evaluation service — compare locked forecasts against external evidence."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from alters_lab.schemas.forecast_evaluation import DomainResult, ForecastEvaluationRecord
from alters_lab.schemas.forecast_snapshot import DomainPrediction, ForecastSnapshotRecord
from alters_lab.schemas.external_evidence import ExternalEvidenceRecord
from alters_lab.schemas.branch_outcome_targets import BranchOutcomeTargetRecord
from alters_lab.services.forecast_snapshot import load_snapshot
from alters_lab.services.external_evidence import load_evidence
from alters_lab.services.branch_outcome_targets import load_target
from alters_lab.services.p6_runtime import (
    list_records,
    read_record,
    utc_now,
    write_record,
)

AREA = "forecast_evaluations"

# Mapping from predicted trajectory_direction to the expected observed_direction for a "hit"
_PREDICTION_TO_EXPECTED: dict[str, list[str]] = {
    "improving": ["improved"],
    "declining": ["declined"],
    "stable": ["stable"],
    "mixed": ["mixed"],
    "unknown": ["unknown"],
}

# Partial matches — direction is plausible but not exact
_PARTIAL_MATCHES: dict[str, list[str]] = {
    "improving": ["stable"],
    "declining": ["stable"],
    "stable": ["improved", "declined"],
}

_ALL_DOMAINS = [
    "career_education",
    "financial",
    "health",
    "relationship",
    "subjective_wellbeing",
]


def _evaluate_direction(
    predicted: str,
    observed: str,
) -> str:
    """Return hit, miss, partial, or unknown."""
    if observed == "unknown":
        return "unknown"
    if predicted == "unknown":
        return "unknown"
    expected = _PREDICTION_TO_EXPECTED.get(predicted, [])
    if observed in expected:
        return "hit"
    partial = _PARTIAL_MATCHES.get(predicted, [])
    if observed in partial:
        return "partial"
    # mixed observed is partial when predicted direction is not mixed
    if observed == "mixed":
        return "partial"
    return "miss"


def _compute_horizon(
    snapshot: ForecastSnapshotRecord,
    evaluated_at: str,
    force_final: bool = False,
) -> tuple[bool, str, str, int | None]:
    """Compute horizon elapsed status.

    Returns (horizon_elapsed, evaluation_type, horizon_due_at, days_until_due).
    """
    try:
        created = datetime.fromisoformat(snapshot.created_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        created = datetime.now(timezone.utc)

    try:
        evaluated = datetime.fromisoformat(evaluated_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        evaluated = datetime.now(timezone.utc)

    # Compute horizon due date from created_at + horizon_months
    months = snapshot.horizon_months
    # Approximate: 1 month = 30 days
    horizon_due = created + timedelta(days=months * 30)

    horizon_elapsed = evaluated >= horizon_due
    days_until = (horizon_due - evaluated).days
    if days_until < 0:
        days_until = 0

    horizon_due_str = horizon_due.isoformat()

    if force_final:
        return True, "final", horizon_due_str, days_until if not horizon_elapsed else 0

    if horizon_elapsed:
        return True, "final", horizon_due_str, 0

    return False, "provisional", horizon_due_str, days_until


def _get_domain_predictions(snapshot: ForecastSnapshotRecord) -> dict[str, DomainPrediction]:
    """Extract domain predictions from snapshot, keyed by domain."""
    if snapshot.domain_predictions:
        return {dp.domain: dp for dp in snapshot.domain_predictions}
    return {}


def _resolve_predicted_direction(
    domain: str,
    domain_preds: dict[str, DomainPrediction],
) -> tuple[str, str, str, str, str, str, str]:
    """Resolve predicted direction for a domain.

    Returns (direction, source, confidence, explanation, route_a_direction, route_b_prior_direction, transfer_risk).
    """
    if domain in domain_preds:
        dp = domain_preds[domain]
        return (
            dp.predicted_direction,
            dp.source,
            dp.confidence,
            dp.explanation,
            dp.route_a_direction,
            dp.route_b_prior_direction,
            dp.transfer_risk,
        )

    return "unknown", "unknown", "low", f"No domain prediction available for {domain}.", "unknown", "unknown", "high"


def _aggregate_evidence_by_domain(
    evidence_list: list[ExternalEvidenceRecord],
) -> dict[str, list[ExternalEvidenceRecord]]:
    """Group evidence records by domain."""
    by_domain: dict[str, list[ExternalEvidenceRecord]] = {}
    for e in evidence_list:
        by_domain.setdefault(e.domain, []).append(e)
    return by_domain


def _strongest_strength(evidence_list: list[ExternalEvidenceRecord]) -> str:
    """Return the strongest evidence strength from a list."""
    if not evidence_list:
        return "weak"
    strengths = [e.objective_strength for e in evidence_list]
    if "strong" in strengths:
        return "strong"
    if "moderate" in strengths:
        return "moderate"
    return "weak"


def _infer_direction_from_numeric(
    numeric_value: float,
    baseline_str: str | None,
    target_str: str | None,
) -> str | None:
    """Infer direction from numeric evidence relative to baseline/target.

    Returns improved/declined/stable or None if not inferable.
    """
    if baseline_str is None or target_str is None:
        return None

    try:
        baseline = float(baseline_str)
        target = float(target_str)
    except (ValueError, TypeError):
        return None

    if target == baseline:
        return None  # Can't determine direction

    target_direction = target - baseline
    actual_movement = numeric_value - baseline

    if target_direction > 0:
        # Higher is better
        if actual_movement > 0:
            return "improved"
        elif actual_movement < 0:
            return "declined"
        else:
            return "stable"
    else:
        # Lower is better
        if actual_movement < 0:
            return "improved"
        elif actual_movement > 0:
            return "declined"
        else:
            return "stable"


def _aggregate_observed_direction(
    evidence_list: list[ExternalEvidenceRecord],
    targets: dict[str, BranchOutcomeTargetRecord] | None = None,
) -> str:
    """Aggregate evidence into an observed direction.

    Uses numeric interpretation when baseline/target available.
    Falls back to polarity mapping.
    """
    if not evidence_list:
        return "unknown"

    # Try numeric interpretation first
    numeric_directions: list[str] = []
    polarity_directions: list[str] = []

    for e in evidence_list:
        inferred = None
        if e.numeric_value is not None and targets and e.target_id and e.target_id in targets:
            target = targets[e.target_id]
            inferred = _infer_direction_from_numeric(
                e.numeric_value, target.baseline_value, target.target_value,
            )

        if inferred:
            numeric_directions.append(inferred)
        else:
            # Fall back to polarity mapping
            if e.polarity == "positive":
                polarity_directions.append("improved")
            elif e.polarity == "negative":
                polarity_directions.append("declined")
            elif e.polarity == "neutral":
                polarity_directions.append("stable")
            else:
                polarity_directions.append("mixed")

    # Prefer numeric if available
    all_directions = numeric_directions if numeric_directions else polarity_directions

    if not all_directions:
        return "unknown"

    unique = set(all_directions)
    if len(unique) == 1:
        return unique.pop()
    if "improved" in unique and "declined" in unique:
        return "mixed"
    if "improved" in unique:
        return "improved"
    if "declined" in unique:
        return "declined"
    return "mixed"


def _build_domain_result(
    domain: str,
    predicted_direction: str,
    pred_source: str,
    pred_confidence: str,
    pred_explanation: str,
    evidence_list: list[ExternalEvidenceRecord],
    targets: dict[str, BranchOutcomeTargetRecord] | None = None,
    route_a_direction: str = "unknown",
    route_b_prior_direction: str = "unknown",
    transfer_risk: str = "high",
) -> DomainResult:
    """Build a single domain evaluation result."""
    if not evidence_list:
        return DomainResult(
            domain=domain,
            predicted_direction=predicted_direction,
            predicted_direction_source=pred_source,
            predicted_direction_confidence=pred_confidence,
            predicted_direction_explanation=pred_explanation,
            observed_direction="unknown",
            match_result="unknown",
            evidence_strength="weak",
            explanation=f"No external evidence available for {domain}.",
            route_a_direction=route_a_direction,
            route_b_prior_direction=route_b_prior_direction,
            transfer_risk=transfer_risk,
        )

    observed = _aggregate_observed_direction(evidence_list, targets)
    match = _evaluate_direction(predicted_direction, observed)
    strength = _strongest_strength(evidence_list)
    descriptions = "; ".join(e.description for e in evidence_list[:3])
    explanation = f"Observed {observed} based on {len(evidence_list)} evidence record(s): {descriptions}"

    return DomainResult(
        domain=domain,
        predicted_direction=predicted_direction,
        predicted_direction_source=pred_source,
        predicted_direction_confidence=pred_confidence,
        predicted_direction_explanation=pred_explanation,
        observed_direction=observed,
        match_result=match,
        evidence_strength=strength,
        explanation=explanation,
        route_a_direction=route_a_direction,
        route_b_prior_direction=route_b_prior_direction,
        transfer_risk=transfer_risk,
    )


def _overall_from_domain_results(results: list[DomainResult]) -> str:
    """Compute overall match result from domain results."""
    if not results:
        return "unknown"
    matches = [r.match_result for r in results]
    if all(m == "unknown" for m in matches):
        return "unknown"
    non_unknown = [m for m in matches if m != "unknown"]
    if not non_unknown:
        return "unknown"
    if all(m == "hit" for m in non_unknown):
        return "hit"
    if all(m == "miss" for m in non_unknown):
        return "miss"
    if any(m == "hit" for m in non_unknown) and any(m == "miss" for m in non_unknown):
        return "partial"
    if any(m == "partial" for m in non_unknown):
        return "partial"
    return "partial"


def evaluate_forecast(
    snapshot_id: str,
    evidence_ids: list[str],
    repo_root: Path | None = None,
    force_final: bool = False,
) -> ForecastEvaluationRecord:
    """Evaluate a locked forecast snapshot against external evidence.

    Uses domain-level predictions from the snapshot when available.
    If no external evidence is provided, result is unknown — never guessed.
    The original snapshot is never mutated.
    """
    snapshot = load_snapshot(snapshot_id, repo_root=repo_root)
    evidence_list: list[ExternalEvidenceRecord] = []
    for eid in evidence_ids:
        try:
            evidence_list.append(load_evidence(eid, repo_root=repo_root))
        except FileNotFoundError:
            continue

    by_domain = _aggregate_evidence_by_domain(evidence_list)
    domain_preds = _get_domain_predictions(snapshot)

    # Load outcome targets for numeric evidence interpretation
    targets_map: dict[str, BranchOutcomeTargetRecord] = {}
    for e in evidence_list:
        if e.target_id:
            try:
                targets_map[e.target_id] = load_target(e.target_id, repo_root=repo_root)
            except FileNotFoundError:
                pass

    # Compute horizon status
    evaluated_at = utc_now()
    horizon_elapsed, eval_type, horizon_due_at, days_until = _compute_horizon(
        snapshot, evaluated_at, force_final=force_final,
    )

    # Build domain results — evaluate domains that have evidence or predictions
    domain_results: list[DomainResult] = []
    seen_domains: set[str] = set()

    # Evaluate domains that have evidence
    for domain, ev_list in by_domain.items():
        direction, source, confidence, explanation, ra_dir, rb_dir, t_risk = _resolve_predicted_direction(domain, domain_preds)
        result = _build_domain_result(
            domain, direction, source, confidence, explanation, ev_list, targets_map,
            route_a_direction=ra_dir, route_b_prior_direction=rb_dir, transfer_risk=t_risk,
        )
        domain_results.append(result)
        seen_domains.add(domain)

    # Also include domains that have predictions but no evidence (as unknown observed)
    for domain, dp in domain_preds.items():
        if domain not in seen_domains:
            domain_results.append(DomainResult(
                domain=domain,
                predicted_direction=dp.predicted_direction,
                predicted_direction_source=dp.source,
                predicted_direction_confidence=dp.confidence,
                predicted_direction_explanation=dp.explanation,
                observed_direction="unknown",
                match_result="unknown",
                evidence_strength="weak",
                explanation=f"No external evidence available for {domain}.",
                route_a_direction=dp.route_a_direction,
                route_b_prior_direction=dp.route_b_prior_direction,
                transfer_risk=dp.transfer_risk,
            ))
            seen_domains.add(domain)

    # If still no domain results, create a single unknown result
    if not domain_results:
        domain_results.append(DomainResult(
            domain="career_education",
            predicted_direction="unknown",
            predicted_direction_source="unknown",
            predicted_direction_confidence="low",
            predicted_direction_explanation="No domain predictions or evidence available.",
            observed_direction="unknown",
            match_result="unknown",
            evidence_strength="weak",
            explanation="No external evidence provided for evaluation.",
        ))

    overall = _overall_from_domain_results(domain_results)

    # Build signals
    predictive: list[str] = []
    misleading: list[str] = []
    calibration_notes: list[str] = []

    for dr in domain_results:
        if dr.match_result == "hit":
            predictive.append(f"Domain prediction for {dr.domain} (source: {dr.predicted_direction_source}) matched observed outcome.")
        elif dr.match_result == "miss":
            misleading.append(f"Domain prediction for {dr.domain} did not match: predicted {dr.predicted_direction} ({dr.predicted_direction_source}), observed {dr.observed_direction}.")
        elif dr.match_result == "partial":
            calibration_notes.append(f"Partial match for {dr.domain}: predicted {dr.predicted_direction}, observed {dr.observed_direction}.")

    if not evidence_list:
        calibration_notes.append("No external evidence provided — evaluation is unknown, not a miss.")

    if eval_type == "provisional":
        calibration_notes.append(f"Evaluation is provisional — horizon not yet due (due: {horizon_due_at}, {days_until} days remaining).")

    limitations = list(snapshot.limitations)
    if not evidence_list:
        limitations.append("No external evidence was available for this evaluation.")
    if eval_type == "provisional":
        limitations.append("Provisional evaluation before horizon elapsed — final result may differ.")

    return ForecastEvaluationRecord(
        snapshot_id=snapshot_id,
        branch_id=snapshot.branch_id,
        evidence_ids=evidence_ids,
        evaluation_horizon_elapsed=horizon_elapsed,
        evaluation_type=eval_type,
        horizon_due_at=horizon_due_at,
        days_until_due=days_until,
        domain_results=domain_results,
        overall_result=overall,
        calibration_notes=calibration_notes,
        misleading_signals=misleading,
        predictive_signals=predictive,
        limitations=limitations,
    )


def save_evaluation(record: ForecastEvaluationRecord, repo_root: Path | None = None) -> Path:
    data = record.model_dump(mode="json")
    return write_record(AREA, record.evaluation_id, data, repo_root=repo_root)


def load_evaluation(evaluation_id: str, repo_root: Path | None = None) -> ForecastEvaluationRecord:
    data = read_record(AREA, evaluation_id, repo_root=repo_root)
    return ForecastEvaluationRecord(**data)


def list_evaluations(repo_root: Path | None = None) -> list[ForecastEvaluationRecord]:
    records = list_records(AREA, repo_root=repo_root)
    return [ForecastEvaluationRecord(**r) for r in records]
