"""Forecast snapshot API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.branch_forecast import BranchForecastResult
from alters_lab.schemas.forecast_snapshot import (
    DomainPrediction,
    ForecastSnapshotRecord,
    ForecastSummarySnapshot,
)
from alters_lab.services.forecast_snapshot import (
    list_snapshots,
    load_snapshot,
    save_snapshot,
)

router = APIRouter(prefix="/forecast-snapshots", tags=["forecast-snapshots"])


def _extract_domain_predictions(body: BranchForecastResult) -> list[DomainPrediction]:
    """Extract per-domain predictions from forecast result.

    If BranchForecastResult contains domain_predictions (from the anchor service),
    map each to a DomainPrediction directly. Only fall back to overall_fallback
    when no domain-level data exists.
    """
    # Index adapter results by domain for enrichment
    adapter_by_domain: dict[str, object] = {}
    if body.personal_prior_adapter and body.personal_prior_adapter.domain_results:
        for ar in body.personal_prior_adapter.domain_results:
            adapter_by_domain[ar.domain] = ar

    if body.domain_predictions:
        results = []
        for dp in body.domain_predictions:
            adapter = adapter_by_domain.get(dp.domain)
            results.append(DomainPrediction(
                domain=dp.domain,
                predicted_direction=dp.predicted_direction,
                source=dp.predicted_direction_source,
                confidence=dp.confidence,
                explanation=dp.explanation,
                route_a_direction=dp.route_a_direction,
                route_b_prior_direction=dp.route_b_prior_direction,
                evidence_strength=dp.evidence_strength,
                transfer_risk=dp.transfer_risk,
                artifact_class=dp.artifact_class,
                strength_level=dp.strength_level,
                adapter_adjusted_direction=adapter.adjusted_forecast_direction if adapter else None,
                adapter_conflict_level=adapter.conflict_level if adapter else None,
                adapter_alignment=adapter.alignment if adapter else None,
            ))
        return results

    # Fallback: no domain-level data, use overall trajectory for all domains
    overall_direction = body.forecast_summary.trajectory_direction
    overall_confidence = body.forecast_summary.confidence
    _ALL_DOMAINS = [
        "career_education", "financial", "health",
        "relationship", "subjective_wellbeing",
    ]
    return [
        DomainPrediction(
            domain=domain,
            predicted_direction=overall_direction,
            source="overall_fallback",
            confidence=overall_confidence,
            explanation=f"Using overall trajectory direction as fallback. No domain-specific prediction available for {domain}.",
        )
        for domain in _ALL_DOMAINS
    ]


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "forecast-snapshots",
        "storage_area": "alters/product/forecast_snapshots",
        "provider_required": False,
    }


@router.post("/create-from-forecast")
def create_from_forecast(body: BranchForecastResult):
    try:
        summary = body.forecast_summary
        domain_predictions = _extract_domain_predictions(body)
        snapshot = ForecastSnapshotRecord(
            branch_id=body.branch_id,
            horizon_months=body.horizon_months,
            forecast_payload=body.model_dump(),
            forecast_summary=ForecastSummarySnapshot(
                trajectory_direction=summary.trajectory_direction,
                confidence=summary.confidence,
                credibility=summary.credibility,
                explanation=summary.explanation,
            ),
            domain_predictions=domain_predictions,
            route_a_summary=body.route_a_personal_evidence.model_dump(),
            route_b_summary=body.route_b_population_prior.model_dump(),
            adapter_summary=body.personal_prior_adapter.model_dump() if body.personal_prior_adapter else {},
            calibration_divergence_summary=body.calibration_divergence.model_dump(),
            limitations=body.limitations,
        )
        path = save_snapshot(snapshot)
        return {
            "status": "saved",
            "snapshot": snapshot.model_dump(),
            "snapshot_path": str(path),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/list")
def list_all():
    snapshots = list_snapshots()
    return {
        "status": "ok",
        "snapshots": [s.model_dump() for s in snapshots],
        "count": len(snapshots),
    }


@router.get("/{snapshot_id}")
def get_snapshot(snapshot_id: str):
    try:
        snapshot = load_snapshot(snapshot_id)
        return {"status": "ok", "snapshot": snapshot.model_dump()}
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Snapshot not found: {snapshot_id}"
        )
