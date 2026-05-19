"""Alter Dialogue Runtime API — read-only, no provider (P4-M1)."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.alter_dialogue import (
    AlterDialogueHealthResponse,
    AlterDialogueListResponse,
    AlterDialogueRequest,
    AlterDialogueResponse,
)
from alters_lab.services.alter_dialogue import (
    alter_dialogue_boundary_confirmations,
    build_dialogue_response,
    get_repo_root,
    list_active_alters,
    load_active_alter,
    build_alter_dialogue_context,
    validate_alter_id,
    validate_active_alter_for_dialogue,
)

router = APIRouter(prefix="/alter-dialogue", tags=["alter-dialogue"])


def _repo_root() -> Path:
    return get_repo_root()


@router.get("/health", response_model=AlterDialogueHealthResponse)
def health():
    return AlterDialogueHealthResponse(
        status="ok",
        component="alter-dialogue",
        mode="read_only_no_provider",
        provider_used=False,
        active_write_allowed=False,
    )


@router.get("/alters", response_model=AlterDialogueListResponse)
def list_alters():
    alters = list_active_alters(_repo_root())
    bc = alter_dialogue_boundary_confirmations()
    return AlterDialogueListResponse(
        status="ok",
        alters=alters,
        count=len(alters),
        boundary_confirmations=bc,
    )


@router.get("/{alter_id}/context")
def get_context(alter_id: str):
    try:
        validate_alter_id(alter_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        alter = load_active_alter(alter_id, _repo_root())
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    validation = validate_active_alter_for_dialogue(alter)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=f"Alter validation failed: {'; '.join(validation['errors'])}")

    context = build_alter_dialogue_context(alter)
    bc = alter_dialogue_boundary_confirmations()
    return {
        "status": "context_ready",
        "alter_id": alter_id,
        "dialogue_context": context.model_dump(),
        "boundary_confirmations": bc,
    }


@router.post("/{alter_id}/prompt", response_model=AlterDialogueResponse)
def prompt(alter_id: str, request: AlterDialogueRequest):
    try:
        response = build_dialogue_response(alter_id, request, _repo_root())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return response
