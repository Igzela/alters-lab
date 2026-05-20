"""P5-M5 Durable Storage Boundary routes.

YAML remains default. No database migration. No active writes.
"""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.storage_boundary import (
    StorageBoundaryHealthResponse,
    StorageManifestResponse,
)
from alters_lab.services.storage_boundary import (
    get_storage_boundary_health,
    get_storage_manifest,
)

router = APIRouter(prefix="/storage-boundary", tags=["storage-boundary"])


@router.get("/health", response_model=StorageBoundaryHealthResponse)
def health():
    return get_storage_boundary_health()


@router.get("/manifest", response_model=StorageManifestResponse)
def manifest():
    return get_storage_manifest()
