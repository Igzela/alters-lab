"""Branch base-rate anchor API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.branch_base_rate_anchor import BranchBaseRateAnchorRequest
from alters_lab.services.branch_base_rate_anchor import analyze_base_rate_anchor

router = APIRouter(prefix="/branch-base-rate-anchor", tags=["branch-base-rate-anchor"])


@router.post("/analyze")
def analyze(body: BranchBaseRateAnchorRequest):
    try:
        result = analyze_base_rate_anchor(body)
        return result.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
