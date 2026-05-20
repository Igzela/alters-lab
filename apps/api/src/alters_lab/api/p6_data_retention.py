"""P6-M8 data retention/export/delete routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.p6_data_retention import (
    P6ArchiveRequest,
    P6DeleteRequest,
    P6ExportRequest,
    P6RetentionActionResponse,
    P6RetentionHealthResponse,
    P6RetentionManifestResponse,
)
from alters_lab.services.p6_data_retention import (
    archive_p6_records,
    build_retention_manifest,
    delete_p6_record,
    export_p6_records,
)

router = APIRouter(prefix="/p6-data-retention", tags=["p6-data-retention"])


@router.get("/health", response_model=P6RetentionHealthResponse)
def health():
    return P6RetentionHealthResponse()


@router.get("/manifest", response_model=P6RetentionManifestResponse)
def manifest():
    areas, counts = build_retention_manifest()
    return P6RetentionManifestResponse(runtime_areas=areas, record_counts=counts)


@router.post("/export", response_model=P6RetentionActionResponse)
def export(body: P6ExportRequest):
    try:
        path = export_p6_records(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return P6RetentionActionResponse(status="exported", path=str(path))


@router.post("/delete", response_model=P6RetentionActionResponse)
def delete(body: P6DeleteRequest):
    try:
        delete_p6_record(body)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"P6 record not found: {body.record.record_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return P6RetentionActionResponse(status="deleted", deleted_record=body.record)


@router.post("/archive", response_model=P6RetentionActionResponse)
def archive(body: P6ArchiveRequest):
    try:
        path = archive_p6_records(body)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return P6RetentionActionResponse(status="archived", path=str(path))
