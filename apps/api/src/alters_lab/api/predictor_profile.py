"""Predictor profile API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.predictor_profile import PredictorProfileRecord
from alters_lab.services.predictor_profile import (
    list_profiles,
    load_profile,
    save_profile,
)

router = APIRouter(prefix="/predictor-profile", tags=["predictor-profile"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "predictor-profile",
        "storage_area": "alters/product/predictor_profiles",
        "provider_required": False,
    }


@router.post("")
def create_profile(body: PredictorProfileRecord):
    try:
        path = save_profile(body)
        return {
            "status": "saved",
            "profile": body.model_dump(),
            "profile_path": str(path),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/list")
def list_all():
    profiles = list_profiles()
    return {
        "status": "ok",
        "profiles": [p.model_dump() for p in profiles],
        "count": len(profiles),
    }


@router.get("/{profile_id}")
def get_profile(profile_id: str):
    try:
        profile = load_profile(profile_id)
        return {"status": "ok", "profile": profile.model_dump()}
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Profile not found: {profile_id}"
        )
