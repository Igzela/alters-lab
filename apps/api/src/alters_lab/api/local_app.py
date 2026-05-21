"""Local app server status routes."""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.local_app import (
    LocalAppFrontendStatusResponse,
    LocalAppHealthResponse,
    LocalAppStatusResponse,
)
from alters_lab.services.local_app import build_local_app_status

router = APIRouter(prefix="/local-app", tags=["local-app"])


@router.get("/health", response_model=LocalAppHealthResponse)
def health():
    return LocalAppHealthResponse()


@router.get("/status", response_model=LocalAppStatusResponse)
def status():
    return LocalAppStatusResponse(**build_local_app_status())


@router.get("/frontend-status", response_model=LocalAppFrontendStatusResponse)
def frontend_status():
    status_data = build_local_app_status()
    return LocalAppFrontendStatusResponse(
        frontend_available=status_data["frontend_available"],
        frontend_dist_path=status_data["frontend_dist_path"],
    )
