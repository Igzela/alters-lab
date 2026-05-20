"""P6-M10 behavior validation gate routes."""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.behavior_validation import (
    BehaviorValidationEvaluateRequest,
    BehaviorValidationHealthResponse,
    BehaviorValidationReportResponse,
    BehaviorValidationResponse,
)
from alters_lab.services.behavior_validation import (
    evaluate_behavior_validation,
    latest_behavior_validation,
    save_behavior_validation,
)

router = APIRouter(prefix="/behavior-validation", tags=["behavior-validation"])


@router.get("/health", response_model=BehaviorValidationHealthResponse)
def health():
    return BehaviorValidationHealthResponse()


@router.post("/evaluate", response_model=BehaviorValidationResponse)
def evaluate(body: BehaviorValidationEvaluateRequest):
    validation = evaluate_behavior_validation(body)
    path = save_behavior_validation(validation) if body.save else None
    return BehaviorValidationResponse(status=validation.status, validation=validation, validation_path=str(path) if path else None)


@router.get("/report", response_model=BehaviorValidationReportResponse)
def report():
    validation = latest_behavior_validation()
    return BehaviorValidationReportResponse(status="ok" if validation else "no_report", validation=validation)
