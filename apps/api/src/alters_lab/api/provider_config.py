"""Routes for local provider configuration."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.provider_config import (
    ProviderConfigHealthResponse,
    ProviderConfigResponse,
    ProviderConfigStatusResponse,
    ProviderConfigTestRequest,
    ProviderConfigTestResponse,
    ProviderConfigUpdateRequest,
    ProviderSecretDeleteRequest,
    ProviderSecretMutationResponse,
    ProviderSecretUpdateRequest,
)
from alters_lab.services.provider_config import (
    ProviderConfigError,
    delete_provider_secret,
    get_provider_config,
    get_provider_status,
    store_provider_secret,
    test_provider_config,
    update_provider_config,
)

router = APIRouter(prefix="/provider-config", tags=["provider-config"])


@router.get("/health", response_model=ProviderConfigHealthResponse)
def health():
    return ProviderConfigHealthResponse()


@router.get("/status", response_model=ProviderConfigStatusResponse)
def status():
    return get_provider_status()


@router.get("/config", response_model=ProviderConfigResponse)
def config():
    return get_provider_config()


@router.post("/config", response_model=ProviderConfigResponse)
def update_config(request: ProviderConfigUpdateRequest):
    try:
        return update_provider_config(request)
    except ProviderConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/secret", response_model=ProviderSecretMutationResponse)
def update_secret(request: ProviderSecretUpdateRequest):
    try:
        return store_provider_secret(
            api_key=request.api_key,
            storage=request.storage,
            confirmation=request.confirmation,
        )
    except ProviderConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/secret", response_model=ProviderSecretMutationResponse)
def delete_secret(request: ProviderSecretDeleteRequest):
    try:
        return delete_provider_secret(
            confirmation=request.confirmation,
            storage=request.storage,
        )
    except ProviderConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/test", response_model=ProviderConfigTestResponse)
def test_config(request: ProviderConfigTestRequest):
    return test_provider_config(request)
