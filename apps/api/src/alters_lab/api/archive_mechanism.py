"""Archive Mechanism API for P4-M6."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.archive_mechanism import (
    ArchiveCreateRequest,
    ArchiveHealthResponse,
    ArchiveListResponse,
    ArchivePlanRequest,
    ArchiveResponse,
)
from alters_lab.services.archive_mechanism import (
    archive_boundary_confirmations,
    create_archive,
    list_archives,
    plan_archive,
)
from alters_lab.services.calibration_loop import get_repo_root

router = APIRouter(prefix="/archive-mechanism", tags=["archive-mechanism"])


def _repo_root() -> Path:
    return get_repo_root()


@router.get("/health", response_model=ArchiveHealthResponse)
def health():
    return ArchiveHealthResponse()


@router.post("/plan", response_model=ArchiveResponse)
def plan(request: ArchivePlanRequest):
    try:
        manifest = plan_archive(request, _repo_root())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ArchiveResponse(
        status="planned",
        manifest=manifest,
        archive_path=None,
        boundary_confirmations=archive_boundary_confirmations(),
    )


@router.post("/create", response_model=ArchiveResponse)
def create(request: ArchiveCreateRequest):
    try:
        manifest, path = create_archive(request, _repo_root())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ArchiveResponse(
        status="created",
        manifest=manifest,
        archive_path=str(path),
        boundary_confirmations=archive_boundary_confirmations(),
    )


@router.get("/list", response_model=ArchiveListResponse)
def list_archive_packages():
    archives = list_archives(_repo_root())
    return ArchiveListResponse(
        status="ok",
        archives=archives,
        count=len(archives),
        boundary_confirmations=archive_boundary_confirmations(),
    )
