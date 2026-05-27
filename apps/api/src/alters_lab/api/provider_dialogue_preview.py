"""Routes for provider-backed dialogue preview."""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.provider_dialogue_preview import (
    ProviderDialoguePreviewHealthResponse,
    ProviderDialoguePreviewRequest,
    ProviderDialoguePreviewResponse,
    ProviderDialoguePreviewStatusResponse,
)
from alters_lab.services.provider_dialogue_preview import (
    build_provider_dialogue_preview_health,
    build_provider_dialogue_preview_status,
    run_provider_dialogue_preview,
)

router = APIRouter(prefix="/provider-dialogue-preview", tags=["provider-dialogue-preview"])


@router.get("/health", response_model=ProviderDialoguePreviewHealthResponse)
def health():
    return build_provider_dialogue_preview_health()


@router.get("/status", response_model=ProviderDialoguePreviewStatusResponse)
def status():
    return build_provider_dialogue_preview_status()


@router.post("/generate", response_model=ProviderDialoguePreviewResponse)
def generate(request: ProviderDialoguePreviewRequest):
    return run_provider_dialogue_preview(request)
