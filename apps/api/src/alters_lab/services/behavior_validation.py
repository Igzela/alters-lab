"""P6-M10 behavior validation gate service."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.behavior_validation import (
    BehaviorValidationEvaluateRequest,
    BehaviorValidationRecord,
)
from alters_lab.services.p6_runtime import generate_record_id, list_records, utc_now, write_record


def evaluate_behavior_validation(request: BehaviorValidationEvaluateRequest) -> BehaviorValidationRecord:
    review_count = len(set(request.weekly_review_ids))
    calibration_count = len(set(request.calibration_record_ids))
    pattern_count = len(set(request.pattern_review_ids))
    usage_valid = all(request.usage_integrity.model_dump().values())
    improved = all(request.metrics.model_dump().values())

    outcome = "P6_INSUFFICIENT_DATA"
    status = "insufficient_data"
    message = "P6 requires 4 weekly reviews, 4 calibration records, and 1 pattern review before behavior validation."

    if review_count >= 4 and calibration_count >= 4 and pattern_count >= 1:
        if not usage_valid:
            outcome = "P6_USAGE_INVALID"
            status = "usage_invalid"
            message = "Usage integrity failed; fix usage behavior before adding features or redesigning."
        elif improved:
            outcome = "P6_BEHAVIOR_VALIDATED"
            status = "validated"
            message = "P6 behavior validation passed based on supplied four-week evidence."
        else:
            outcome = "P6_FAILED_TO_VALIDATE"
            status = "failed_to_validate"
            message = "Usage was valid but behavior improvement was not demonstrated."

    return BehaviorValidationRecord(
        validation_id=generate_record_id("behavior_validation"),
        outcome=outcome,  # type: ignore[arg-type]
        status=status,
        weekly_review_count=review_count,
        calibration_record_count=calibration_count,
        pattern_review_count=pattern_count,
        metrics=request.metrics,
        usage_integrity=request.usage_integrity,
        usage_integrity_valid=usage_valid,
        behavior_improved=improved,
        message=message,
        created_at=utc_now(),
    )


def save_behavior_validation(record: BehaviorValidationRecord, repo_root: Path | None = None) -> Path:
    return write_record("behavior_validation", record.validation_id, record.model_dump(), repo_root)


def list_behavior_validations(repo_root: Path | None = None) -> list[BehaviorValidationRecord]:
    return [BehaviorValidationRecord(**r) for r in list_records("behavior_validation", repo_root)]


def latest_behavior_validation(repo_root: Path | None = None) -> BehaviorValidationRecord | None:
    records = list_behavior_validations(repo_root)
    return records[-1] if records else None
