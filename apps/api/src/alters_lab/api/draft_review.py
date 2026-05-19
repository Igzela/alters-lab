"""Draft review and promotion boundary API endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.draft_review import (
    DraftReviewListResponse,
    DraftReviewRequest,
    DraftReviewResponse,
)
from alters_lab.services.draft_review import (
    build_promotion_package,
    create_review_decision,
    draft_review_boundary_confirmations,
    list_draft_reviews,
    load_draft_package,
    save_promotion_package,
    save_review_decision,
    validate_draft_package_for_review,
)

router = APIRouter(prefix="/draft-review", tags=["draft-review"])


def get_draft_review_workspace() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "alters/drafts"


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "draft-review",
        "mode": "review_boundary",
        "active_write_allowed": False,
        "provider_used": False,
    }


@router.post(
    "/{draft_id}/review",
    response_model=DraftReviewResponse,
)
def review_draft(draft_id: str, body: DraftReviewRequest):
    workspace = get_draft_review_workspace()

    try:
        draft_package = load_draft_package(workspace, draft_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Draft package not found: {draft_id}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    validation = validate_draft_package_for_review(draft_package)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"draft validation failed: {'; '.join(validation['errors'])}",
        )

    review_decision = create_review_decision(draft_id, body)

    promotion_package = None
    promotion_package_path = None
    if review_decision.decision == "approve_for_promotion_package":
        promotion_package = build_promotion_package(draft_package, review_decision)

    review_path = None
    if body.save_review:
        if not body.approval_token:
            raise HTTPException(status_code=400, detail="approval_token required when save_review=true")
        result = save_review_decision(workspace, draft_id, review_decision, body.approval_token, body.caller)
        review_path = result["review_path"]
        if promotion_package:
            save_result = save_promotion_package(workspace, draft_id, promotion_package, body.approval_token, body.caller)
            promotion_package_path = save_result["promotion_package_path"]

    return DraftReviewResponse(
        status="review_saved" if body.save_review else "reviewed",
        draft_id=draft_id,
        review_decision=review_decision,
        review_path=review_path,
        promotion_package=promotion_package,
        promotion_package_path=promotion_package_path,
        boundary_confirmations=draft_review_boundary_confirmations(),
    )


@router.get("/list", response_model=DraftReviewListResponse)
def list_reviews():
    workspace = get_draft_review_workspace()
    reviews = list_draft_reviews(workspace)
    return DraftReviewListResponse(
        status="ok",
        reviews=reviews,
        count=len(reviews),
    )
