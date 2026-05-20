"""P6-M9 explicit provider enablement policy routes."""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.p6_provider_policy import (
    P6ProviderConfigValidationRequest,
    P6ProviderConfigValidationResponse,
    P6ProviderPolicyHealthResponse,
    P6ProviderPolicyStatusResponse,
)
from alters_lab.services.p6_provider_policy import (
    get_p6_provider_policy_status,
    validate_p6_provider_config,
)

router = APIRouter(prefix="/p6-provider-policy", tags=["p6-provider-policy"])


@router.get("/health", response_model=P6ProviderPolicyHealthResponse)
def health():
    return P6ProviderPolicyHealthResponse()


@router.get("/status", response_model=P6ProviderPolicyStatusResponse)
def status():
    return get_p6_provider_policy_status()


@router.post("/validate-config", response_model=P6ProviderConfigValidationResponse)
def validate_config(body: P6ProviderConfigValidationRequest):
    return validate_p6_provider_config(body)
