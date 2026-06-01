"""Forecast snapshot API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.branch_forecast import BranchForecastResult
from alters_lab.schemas.forecast_snapshot import ForecastSnapshotRecord, ForecastSummarySnapshot
from alters_lab.services.forecast_snapshot import (
    list_snapshots,
    load_snapshot,
    save_snapshot,
)

router = APIRouter(prefix="/forecast-snapshots", tags=["forecast-snapshots"])


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
