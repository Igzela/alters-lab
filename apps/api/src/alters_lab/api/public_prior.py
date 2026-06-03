"""Public prior API — list and view approved population prior artifacts and model cards."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.services.public_prior import (
    get_artifact,
    get_domain_coverage,
    get_model_card,
    list_all_artifacts,
    list_approved_artifacts,
    list_artifacts_for_domain,
    list_model_cards,
)

router = APIRouter(prefix="/public-priors", tags=["public-priors"])


@router.get("/artifacts")
def list_artifacts(approved_only: bool = True):
    if approved_only:
        artifacts = list_approved_artifacts()
    else:
        artifacts = list_all_artifacts()
    return {"artifacts": [a.model_dump(mode="json") for a in artifacts]}


@router.get("/artifacts/{artifact_id}")
def get_artifact_by_id(artifact_id: str):
    try:
        artifact = get_artifact(artifact_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Artifact not found: {artifact_id}")
    return artifact.model_dump(mode="json")


@router.get("/artifacts/domain/{domain}")
def list_artifacts_by_domain(domain: str):
    artifacts = list_artifacts_for_domain(domain)
    return {"domain": domain, "artifacts": [a.model_dump(mode="json") for a in artifacts]}


@router.get("/model-cards")
def list_all_model_cards():
    cards = list_model_cards()
    return {"model_cards": [c.model_dump(mode="json") for c in cards]}


@router.get("/model-cards/{model_id}")
def get_model_card_by_id(model_id: str):
    try:
        card = get_model_card(model_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Model card not found: {model_id}")
    return card.model_dump(mode="json")


@router.get("/coverage")
def domain_coverage():
    return get_domain_coverage()
