"""P6-M3 action alignment scoring routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.action_alignment import (
    ActionAlignmentHealthResponse,
    ActionAlignmentListResponse,
    ActionAlignmentLoadResponse,
    ActionAlignmentScoreRequest,
    ActionAlignmentScoreResponse,
)
from alters_lab.services.action_alignment import (
    build_action_alignment_score,
    list_action_alignment_scores,
    load_action_alignment_score,
    save_action_alignment_score,
)

router = APIRouter(prefix="/action-alignment", tags=["action-alignment"])


@router.get("/health", response_model=ActionAlignmentHealthResponse)
def health():
    return ActionAlignmentHealthResponse()


@router.post("/score", response_model=ActionAlignmentScoreResponse)
def score(body: ActionAlignmentScoreRequest):
    try:
        record = build_action_alignment_score(body)
        path = save_action_alignment_score(record) if body.save else None
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Weekly review session not found: {body.session_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ActionAlignmentScoreResponse(status="saved" if body.save else "scored", score=record, score_path=str(path) if path else None)


@router.get("/list", response_model=ActionAlignmentListResponse)
def list_scores():
    scores = list_action_alignment_scores()
    return ActionAlignmentListResponse(scores=scores, count=len(scores))


@router.get("/{score_id}", response_model=ActionAlignmentLoadResponse)
def load(score_id: str):
    try:
        return ActionAlignmentLoadResponse(score=load_action_alignment_score(score_id))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Action alignment score not found: {score_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
