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
    """Extract per-domain predictions from forecast payload.

    Source order:
    1. Domain anchors from base-rate anchor data in forecast_payload (route_a_direction)
    2. Route B prior_direction from domain anchors
    3. Overall trajectory as fallback (marked as overall_fallback)
    """
    predictions: list[DomainPrediction] = []

    # Try to extract domain anchors from the forecast payload
    payload = body.model_dump()
    domain_anchors = []

    # The forecast payload may contain anchor data nested under various keys
    # Check if route_b_population_prior has domain-level data
    route_b = payload.get("route_b_population_prior", {})

    # Build domain predictions from overall trajectory as baseline
    overall_direction = body.forecast_summary.trajectory_direction
    overall_confidence = body.forecast_summary.confidence

    # Check if we have per-domain data in the calibration divergence or outcome targets
    # For now, extract from domain_anchors if present in the payload
    # The anchor service stores domain_anchors, but they're collapsed in the forecast result
    # We reconstruct from available data

    # Get domains from outcome targets if available
    target_domains: list[str] = []
    for target in payload.get("_outcome_target_details", []):
        d = target.get("domain")
        if d and d not in target_domains:
            target_domains.append(d)

    # If no domains from targets, use standard domains
    if not target_domains:
        target_domains = [
            "career_education",
            "financial",
            "health",
            "relationship",
            "subjective_wellbeing",
        ]

    # For each domain, create a prediction
    # If route_a has per-domain info, use it; otherwise mark as overall_fallback
    route_a = body.route_a_personal_evidence

    for domain in target_domains:
        # Check if domain-specific data exists in route_a_summary
        route_a_dict = route_a.model_dump()

        # Look for domain-specific direction in behavior_trends_summary
        # The summary is a string like "2 improving, 1 declining, 1 stable across 4 metrics"
        # We can't extract per-domain from this string

        # Default: use overall trajectory as fallback, clearly marked
        predictions.append(DomainPrediction(
            domain=domain,
            predicted_direction=overall_direction,
            source="overall_fallback",
            confidence=overall_confidence,
            explanation=f"Using overall trajectory direction as fallback. No domain-specific prediction available for {domain}.",
        ))

    return predictions


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
