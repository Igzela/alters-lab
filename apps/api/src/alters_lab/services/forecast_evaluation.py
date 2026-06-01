"""Forecast evaluation service — compare locked forecasts against external evidence."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.forecast_evaluation import DomainResult, ForecastEvaluationRecord
from alters_lab.schemas.forecast_snapshot import ForecastSnapshotRecord
from alters_lab.schemas.external_evidence import ExternalEvidenceRecord
from alters_lab.services.forecast_snapshot import load_snapshot
from alters_lab.services.external_evidence import load_evidence
from alters_lab.services.p6_runtime import (
    list_records,
    read_record,
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


def _aggregate_polarity(evidence_list: list[ExternalEvidenceRecord]) -> str:
    """Aggregate polarity from multiple evidence records into an observed direction."""
    if not evidence_list:
        return "unknown"
    polarities = [e.polarity for e in evidence_list]
    unique = set(polarities)
    if unique == {"positive"}:
        return "improved"
    if unique == {"negative"}:
        return "declined"
    if unique == {"neutral"}:
        return "stable"
    if len(unique) > 1 and "positive" in unique and "negative" in unique:
        return "mixed"
    if "positive" in unique:
        return "improved"
    if "negative" in unique:
        return "declined"
    return "mixed"


def _build_domain_result(
    domain: str,
    predicted_direction: str,
    evidence_list: list[ExternalEvidenceRecord],
) -> DomainResult:
    """Build a single domain evaluation result."""
    if not evidence_list:
        return DomainResult(
            domain=domain,
            predicted_direction=predicted_direction,
            observed_direction="unknown",
            match_result="unknown",
            evidence_strength="weak",
            explanation=f"No external evidence available for {domain}.",
        )

    observed = _aggregate_polarity(evidence_list)
    match = _evaluate_direction(predicted_direction, observed)
    strength = _strongest_strength(evidence_list)
    descriptions = "; ".join(e.description for e in evidence_list[:3])
    explanation = f"Observed {observed} based on {len(evidence_list)} evidence record(s): {descriptions}"

    return DomainResult(
        domain=domain,
        predicted_direction=predicted_direction,
        observed_direction=observed,
        match_result=match,
        evidence_strength=strength,
        explanation=explanation,
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
) -> ForecastEvaluationRecord:
    """Evaluate a locked forecast snapshot against external evidence.

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

    # Get predicted directions from route_a_summary if available,
    # otherwise fall back to forecast_summary trajectory_direction
    trajectory = snapshot.forecast_summary.trajectory_direction
    route_a = snapshot.route_a_summary

    # Build domain results — we know the domains from evidence or from snapshot
    domain_results: list[DomainResult] = []
    seen_domains: set[str] = set()

    # Evaluate domains that have evidence
    for domain, ev_list in by_domain.items():
        predicted = trajectory  # Use overall trajectory as predicted direction per domain
        result = _build_domain_result(domain, predicted, ev_list)
        domain_results.append(result)
        seen_domains.add(domain)

    # If no evidence at all, create a single unknown result
    if not domain_results:
        domain_results.append(DomainResult(
            domain="career_education",  # placeholder domain
            predicted_direction=trajectory,
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
            predictive.append(f"Trajectory prediction for {dr.domain} matched observed outcome.")
        elif dr.match_result == "miss":
            misleading.append(f"Trajectory prediction for {dr.domain} did not match: predicted {dr.predicted_direction}, observed {dr.observed_direction}.")
        elif dr.match_result == "partial":
            calibration_notes.append(f"Partial match for {dr.domain}: predicted {dr.predicted_direction}, observed {dr.observed_direction}.")

    if not evidence_list:
        calibration_notes.append("No external evidence provided — evaluation is unknown, not a miss.")

    limitations = list(snapshot.limitations)
    if not evidence_list:
        limitations.append("No external evidence was available for this evaluation.")

    return ForecastEvaluationRecord(
        snapshot_id=snapshot_id,
        branch_id=snapshot.branch_id,
        evidence_ids=evidence_ids,
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
