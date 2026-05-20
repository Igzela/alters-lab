"""P6-M7 four-week pattern review routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.pattern_review import (
    PatternReviewHealthResponse,
    PatternReviewListResponse,
    PatternReviewLoadResponse,
    PatternReviewRequest,
    PatternReviewResponse,
)
from alters_lab.services.pattern_review import (
    build_pattern_review,
    list_pattern_reviews,
    load_pattern_review,
    save_pattern_review,
)

router = APIRouter(prefix="/pattern-review", tags=["pattern-review"])


@router.get("/health", response_model=PatternReviewHealthResponse)
def health():
    return PatternReviewHealthResponse()


@router.post("/build", response_model=PatternReviewResponse)
def build(body: PatternReviewRequest):
    review = build_pattern_review(body)
    path = save_pattern_review(review) if body.save else None
    return PatternReviewResponse(status=review.status, review=review, review_path=str(path) if path else None)


@router.get("/list", response_model=PatternReviewListResponse)
def list_reviews():
    reviews = list_pattern_reviews()
    return PatternReviewListResponse(reviews=reviews, count=len(reviews))


@router.get("/{review_id}", response_model=PatternReviewLoadResponse)
def load(review_id: str):
    try:
        return PatternReviewLoadResponse(review=load_pattern_review(review_id))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Pattern review not found: {review_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
