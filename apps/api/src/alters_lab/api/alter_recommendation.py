"""P6-M5 alter recommendation routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.alter_recommendation import (
    AlterOverrideRequest,
    AlterRecommendationHealthResponse,
    AlterRecommendationListResponse,
    AlterRecommendationRequest,
    AlterRecommendationResponse,
)
from alters_lab.services.alter_recommendation import (
    build_alter_recommendation,
    list_alter_recommendations,
    load_alter_recommendation,
    override_alter_recommendation,
    save_alter_recommendation,
)

router = APIRouter(prefix="/alter-recommendation", tags=["alter-recommendation"])


@router.get("/health", response_model=AlterRecommendationHealthResponse)
def health():
    return AlterRecommendationHealthResponse()


@router.post("/recommend", response_model=AlterRecommendationResponse)
def recommend(body: AlterRecommendationRequest):
    record = build_alter_recommendation(body)
    path = save_alter_recommendation(record) if body.save else None
    return AlterRecommendationResponse(status="saved" if body.save else "recommended", recommendation=record, recommendation_path=str(path) if path else None)


@router.post("/{recommendation_id}/override", response_model=AlterRecommendationResponse)
def override(recommendation_id: str, body: AlterOverrideRequest):
    try:
        record = load_alter_recommendation(recommendation_id)
        updated = override_alter_recommendation(record, body)
        path = save_alter_recommendation(updated)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Alter recommendation not found: {recommendation_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return AlterRecommendationResponse(status="overridden", recommendation=updated, recommendation_path=str(path))


@router.get("/list", response_model=AlterRecommendationListResponse)
def list_records():
    recommendations = list_alter_recommendations()
    return AlterRecommendationListResponse(recommendations=recommendations, count=len(recommendations))
