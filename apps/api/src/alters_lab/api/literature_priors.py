"""Literature priors API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.services.literature_priors import get_catalog

router = APIRouter(prefix="/literature-priors", tags=["literature-priors"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "literature-priors",
        "storage_area": "alters/product/literature_priors",
        "provider_required": False,
    }


@router.get("/catalog")
def get_full_catalog():
    try:
        catalog = get_catalog()
        return catalog.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/constructs")
def get_constructs():
    try:
        catalog = get_catalog()
        return {
            "status": "ok",
            "constructs": [c.model_dump() for c in catalog.constructs],
            "construct_domain_links": [cdl.model_dump() for cdl in catalog.construct_domain_links],
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/domain/{domain}")
def get_priors_for_domain(domain: str):
    try:
        catalog = get_catalog()
        priors = [p for p in catalog.priors if p.predicted_domain == domain]
        links = [cdl for cdl in catalog.construct_domain_links if cdl.predicted_domain == domain]
        return {
            "status": "ok",
            "domain": domain,
            "priors": [p.model_dump() for p in priors],
            "construct_domain_links": [cdl.model_dump() for cdl in links],
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
