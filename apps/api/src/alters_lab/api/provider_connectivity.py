"""Routes for provider connectivity check contract."""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.provider_connectivity import (
    ProviderConnectivityHealthResponse,
    ProviderConnectivityRequest,
    ProviderConnectivityResponse,
    ProviderConnectivityStatusResponse,
)
from alters_lab.services.provider_connectivity import (
    build_provider_connectivity_status,
    run_provider_connectivity_check,
)

router = APIRouter(prefix="/provider-connectivity", tags=["provider-connectivity"])


@router.get("/health", response_model=ProviderConnectivityHealthResponse)
def health():
    return ProviderConnectivityHealthResponse()


@router.get("/status", response_model=ProviderConnectivityStatusResponse)
def status():
    return build_provider_connectivity_status()


@router.post("/check", response_model=ProviderConnectivityResponse)
def check(request: ProviderConnectivityRequest):
    return run_provider_connectivity_check(request)
