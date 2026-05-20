"""P5-M3 Provider-backed Alter Dialogue routes.

Provider-backed dialogue using full alter YAML prompt packet.
No active YAML write. No auto reality score. No auto drift. No auto archive.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.provider_dialogue import (
    ProviderDialogueHealthResponse,
    ProviderDialogueReplyRequest,
    ProviderDialogueReplyResponse,
)
from alters_lab.services.provider_dialogue import (
    get_provider_dialogue_health,
    provider_dialogue_reply,
)

router = APIRouter(prefix="/provider-dialogue", tags=["provider-dialogue"])


@router.get("/health", response_model=ProviderDialogueHealthResponse)
def health():
    return get_provider_dialogue_health()


@router.post("/{alter_id}/reply", response_model=ProviderDialogueReplyResponse)
def reply(alter_id: str, request: ProviderDialogueReplyRequest):
    try:
        return provider_dialogue_reply(request, alter_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
