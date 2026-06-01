"""Branch forecast API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alters_lab.schemas.branch_forecast import BranchForecastRequest
from alters_lab.services.branch_forecast import analyze_branch_forecast

router = APIRouter(prefix="/branch-forecast", tags=["branch-forecast"])


@router.post("/analyze")
def analyze(body: BranchForecastRequest):
    try:
        result = analyze_branch_forecast(body)
        return result.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
