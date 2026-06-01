"""Behavior metrics API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.behavior_metrics_catalog import load_catalog
from alters_lab.schemas.behavior_metrics_record import WeeklyBehaviorMetricsRecord
from alters_lab.services.behavior_metrics import (
    build_weekly_record,
    list_weekly_records,
    load_weekly_record,
    save_weekly_record,
    validate_milestone_reference,
)
from alters_lab.services.p6_runtime import utc_now

router = APIRouter(prefix="/behavior-metrics", tags=["behavior-metrics"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "behavior-metrics",
        "storage_area": "alters/product/behavior_metrics",
        "provider_required": False,
    }


@router.get("/catalog")
def get_catalog():
    try:
        catalog = load_catalog()
        return catalog.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/weekly-records")
def create_weekly_record(body: WeeklyBehaviorMetricsRecord):
    try:
        record = build_weekly_record(body)
        validate_milestone_reference(record)
        path = save_weekly_record(record)
        return {
            "status": "saved",
            "record": record.model_dump(),
            "record_path": str(path),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/weekly-records")
def list_records():
    records = list_weekly_records()
    return {
        "status": "ok",
        "records": [r.model_dump() for r in records],
        "count": len(records),
    }


@router.get("/weekly-records/{record_id}")
def get_record(record_id: str):
    try:
        record = load_weekly_record(record_id)
        return {"status": "ok", "record": record.model_dump()}
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Record not found: {record_id}"
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
