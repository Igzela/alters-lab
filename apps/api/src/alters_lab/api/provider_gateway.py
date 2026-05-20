"""P5-M2 Provider Gateway Boundary routes.

All provider calls go through this gateway. No feature module directly imports provider SDKs.
"""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.provider_gateway import (
    ProviderConfigStatusResponse,
    ProviderGatewayHealthResponse,
    ProviderGatewayRequest,
    ProviderGatewayResponse,
)
from alters_lab.services.provider_gateway import (
    get_provider_config_status,
    get_provider_gateway_health,
    provider_gateway_complete,
)

router = APIRouter(prefix="/provider-gateway", tags=["provider-gateway"])


@router.get("/health", response_model=ProviderGatewayHealthResponse)
def health():
    return get_provider_gateway_health()


@router.post("/complete", response_model=ProviderGatewayResponse)
def complete(request: ProviderGatewayRequest):
    return provider_gateway_complete(request)


@router.get("/config-status", response_model=ProviderConfigStatusResponse)
def config_status():
    return get_provider_config_status()
