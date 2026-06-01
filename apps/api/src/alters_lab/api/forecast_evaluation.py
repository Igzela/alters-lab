"""Forecast evaluation API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from alters_lab.services.forecast_evaluation import (
    evaluate_forecast,
    list_evaluations,
    load_evaluation,
    save_evaluation,
)

router = APIRouter(prefix="/forecast-evaluations", tags=["forecast-evaluations"])


class EvaluateRequest(BaseModel):
    snapshot_id: str
    evidence_ids: list[str] = []


@router.get("/health")
def health():
    return {
        "status": "ok",
        "component": "forecast-evaluations",
        "storage_area": "alters/product/forecast_evaluations",
        "provider_required": False,
    }


@router.post("/evaluate")
def run_evaluation(body: EvaluateRequest):
    try:
        evaluation = evaluate_forecast(
            snapshot_id=body.snapshot_id,
            evidence_ids=body.evidence_ids,
        )
        path = save_evaluation(evaluation)
        return {
            "status": "saved",
            "evaluation": evaluation.model_dump(),
            "evaluation_path": str(path),
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/list")
def list_all():
    evaluations = list_evaluations()
    return {
        "status": "ok",
        "evaluations": [e.model_dump() for e in evaluations],
        "count": len(evaluations),
    }


@router.get("/{evaluation_id}")
def get_evaluation(evaluation_id: str):
    try:
        evaluation = load_evaluation(evaluation_id)
        return {"status": "ok", "evaluation": evaluation.model_dump()}
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Evaluation not found: {evaluation_id}"
        )
