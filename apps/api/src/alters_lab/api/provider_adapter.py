"""Routes for hardened provider adapter contract layer."""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.provider_adapter import (
    ProviderAdapterHealthResponse,
    ProviderAdapterRequest,
    ProviderAdapterResponse,
    ProviderAdapterStatusResponse,
)
from alters_lab.services.provider_adapter import (
    build_provider_adapter_health,
    build_provider_adapter_status,
    run_provider_adapter,
)

router = APIRouter(prefix="/provider-adapter", tags=["provider-adapter"])


@router.get("/health", response_model=ProviderAdapterHealthResponse)
def health():
    return build_provider_adapter_health()


@router.get("/status", response_model=ProviderAdapterStatusResponse)
def status():
    return build_provider_adapter_status()


@router.post("/preview", response_model=ProviderAdapterResponse)
def preview(request: ProviderAdapterRequest):
    return run_provider_adapter(request)
