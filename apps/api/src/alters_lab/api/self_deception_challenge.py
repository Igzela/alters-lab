"""P6-M4 self-deception and evidence challenge routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.self_deception_challenge import (
    EditChallengeRequest,
    EditChallengeResponse,
    SelfDeceptionEvaluateRequest,
    SelfDeceptionEvaluateResponse,
    SelfDeceptionHealthResponse,
    SelfDeceptionListResponse,
)
from alters_lab.services.self_deception_challenge import (
    build_edit_challenge,
    evaluate_self_deception,
    list_self_deception_records,
    save_self_deception_record,
)

router = APIRouter(prefix="/self-deception-challenge", tags=["self-deception-challenge"])


@router.get("/health", response_model=SelfDeceptionHealthResponse)
def health():
    return SelfDeceptionHealthResponse()


@router.post("/evaluate", response_model=SelfDeceptionEvaluateResponse)
def evaluate(body: SelfDeceptionEvaluateRequest):
    try:
        record = evaluate_self_deception(body)
        path = save_self_deception_record(record) if body.save else None
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Weekly review session not found: {body.session_id}")
    return SelfDeceptionEvaluateResponse(status="saved" if body.save else "evaluated", record=record, record_path=str(path) if path else None)


@router.post("/edit-challenge", response_model=EditChallengeResponse)
def edit_challenge(body: EditChallengeRequest):
    return build_edit_challenge(body)


@router.get("/list", response_model=SelfDeceptionListResponse)
def list_records():
    records = list_self_deception_records()
    return SelfDeceptionListResponse(records=records, count=len(records))
