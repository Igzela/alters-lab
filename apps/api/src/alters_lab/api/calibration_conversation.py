"""API router for LLM-Driven Calibration conversations."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.calibration_conversation import (
    ConfirmDraftRequest,
    ConfirmDraftResponse,
    DraftListResponse,
    RejectDraftResponse,
    SendMessageRequest,
    SendMessageResponse,
    StartConversationRequest,
    StartConversationResponse,
)
from alters_lab.services import calibration_conversation as svc

router = APIRouter(
    prefix="/calibration-conversation", tags=["calibration-conversation"]
)


@router.get("/health")
def health():
    return {"status": "ok", "component": "calibration-conversation"}


@router.post("/start", response_model=StartConversationResponse)
def start_conversation(request: StartConversationRequest):
    try:
        conversation = svc.start_conversation(
            branch_id=request.branch_id,
        )
        opening = (
            conversation.messages[0].content if conversation.messages else ""
        )
        return StartConversationResponse(
            conversation_id=conversation.conversation_id,
            opening_message=opening,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post(
    "/{conversation_id}/message", response_model=SendMessageResponse
)
def send_message(conversation_id: str, request: SendMessageRequest):
    try:
        conversation, draft = svc.send_message(
            conversation_id=conversation_id,
            user_message=request.message,
        )
        last_reply = (
            conversation.messages[-1].content
            if conversation.messages
            else ""
        )
        return SendMessageResponse(
            conversation_id=conversation_id,
            reply=last_reply,
            draft=draft,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{conversation_id}")
def get_conversation(conversation_id: str):
    try:
        conversation = svc.get_conversation(conversation_id)
        return conversation.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{conversation_id}/draft")
def get_conversation_draft(conversation_id: str):
    try:
        conversation = svc.get_conversation(conversation_id)
        if not conversation.draft_ids:
            return {"drafts": []}
        drafts = []
        for did in conversation.draft_ids:
            try:
                drafts.append(svc.get_draft(did).model_dump())
            except FileNotFoundError:
                pass
        return {"drafts": drafts}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/drafts", response_model=DraftListResponse)
def list_drafts(status: str | None = None):
    drafts = svc.list_drafts(status=status)
    return DraftListResponse(drafts=drafts)


@router.post(
    "/drafts/{draft_id}/confirm", response_model=ConfirmDraftResponse
)
def confirm_draft(draft_id: str, request: ConfirmDraftRequest):
    try:
        draft = svc.confirm_draft(
            draft_id=draft_id,
            corrections=request.corrections,
        )
        # Reconstruct what was written from the draft
        records_written = []
        if draft.behavior_metrics:
            records_written.append("behavior_metrics")
        if draft.rubric_scores:
            records_written.append("calibration_score")
        for ev in draft.external_evidence:
            records_written.append(f"external_evidence:{ev.domain}")

        return ConfirmDraftResponse(
            status="confirmed",
            draft_id=draft.draft_id,
            records_written=records_written,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post(
    "/drafts/{draft_id}/reject", response_model=RejectDraftResponse
)
def reject_draft(draft_id: str):
    try:
        draft = svc.reject_draft(draft_id=draft_id)
        return RejectDraftResponse(
            status="rejected",
            draft_id=draft.draft_id,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
