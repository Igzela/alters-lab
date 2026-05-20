"""P6-M10 behavior validation gate service."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from alters_lab.schemas.behavior_validation import (
    BehaviorValidationEvaluateRequest,
    BehaviorValidationRecord,
)
from alters_lab.services.p6_runtime import generate_record_id, list_records, utc_now, write_record
from alters_lab.services.action_alignment import load_action_alignment_score
from alters_lab.services.pattern_review import load_pattern_review
from alters_lab.services.weekly_review_session import load_weekly_review_session


MIN_VALIDATION_WINDOW_DAYS = 21


def evaluate_behavior_validation(
    request: BehaviorValidationEvaluateRequest,
    repo_root: Path | None = None,
) -> BehaviorValidationRecord:
    weekly_ids = _distinct_ids(request.weekly_review_ids)
    calibration_ids = _distinct_ids(request.calibration_record_ids)
    pattern_ids = _distinct_ids(request.pattern_review_ids)
    evidence = verify_behavior_validation_evidence(
        weekly_ids=weekly_ids,
        calibration_ids=calibration_ids,
        pattern_ids=pattern_ids,
        repo_root=repo_root,
    )
    review_count = len(weekly_ids)
    calibration_count = len(calibration_ids)
    pattern_count = len(pattern_ids)
    usage_valid = all(request.usage_integrity.model_dump().values())
    improved = all(request.metrics.model_dump().values())

    outcome = "P6_INSUFFICIENT_DATA"
    status = "insufficient_data"
    message = "P6 requires 4 weekly reviews, 4 calibration records, and 1 pattern review before behavior validation."

    if not evidence["verified"]:
        message = f"Verified persisted evidence is insufficient: {'; '.join(evidence['errors'])}"
    elif review_count >= 4 and calibration_count >= 4 and pattern_count >= 1:
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
        evidence_verified=evidence["verified"],
        evidence_window_days=evidence["window_days"],
        evidence_verification_errors=evidence["errors"],
        verified_weekly_review_ids=weekly_ids if evidence["verified"] else [],
        verified_calibration_record_ids=calibration_ids if evidence["verified"] else [],
        verified_pattern_review_ids=pattern_ids if evidence["verified"] else [],
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


def behavior_validation_has_verified_evidence(
    record: BehaviorValidationRecord,
    repo_root: Path | None = None,
) -> bool:
    if record.outcome != "P6_BEHAVIOR_VALIDATED" or not record.evidence_verified:
        return False
    try:
        evidence = verify_behavior_validation_evidence(
            weekly_ids=record.verified_weekly_review_ids,
            calibration_ids=record.verified_calibration_record_ids,
            pattern_ids=record.verified_pattern_review_ids,
            repo_root=repo_root,
        )
    except ValueError:
        return False
    return evidence["verified"]


def verify_behavior_validation_evidence(
    weekly_ids: list[str],
    calibration_ids: list[str],
    pattern_ids: list[str],
    repo_root: Path | None = None,
) -> dict:
    weekly_records = []
    calibration_records = []
    pattern_records = []
    errors: list[str] = []

    for weekly_id in weekly_ids:
        try:
            weekly_records.append(load_weekly_review_session(weekly_id, repo_root))
        except FileNotFoundError as exc:
            raise ValueError(f"weekly review record not found: {weekly_id}") from exc

    for calibration_id in calibration_ids:
        try:
            calibration_records.append(load_action_alignment_score(calibration_id, repo_root))
        except FileNotFoundError as exc:
            raise ValueError(f"calibration record not found: {calibration_id}") from exc

    for pattern_id in pattern_ids:
        try:
            pattern_records.append(load_pattern_review(pattern_id, repo_root))
        except FileNotFoundError as exc:
            raise ValueError(f"pattern review not found: {pattern_id}") from exc

    if len(weekly_records) < 4:
        errors.append("requires at least 4 distinct weekly review records")
    if len(calibration_records) < 4:
        errors.append("requires at least 4 distinct calibration records")
    if len(pattern_records) < 1:
        errors.append("requires at least 1 real pattern review")

    weekly_id_set = set(weekly_ids)
    unlinked = [score.score_id for score in calibration_records if score.session_id not in weekly_id_set]
    if unlinked:
        errors.append(f"calibration records not linked to supplied weekly reviews: {', '.join(unlinked)}")

    invalid_patterns = [review.review_id for review in pattern_records if review.weeks_evaluated < 4]
    if pattern_records and len(pattern_records) == len(invalid_patterns):
        errors.append("requires at least 1 pattern review covering 4 weeks")

    window = _weekly_review_window(weekly_records)
    if len(weekly_records) >= 4 and not window["valid"]:
        errors.append("requires evidence to cover a real 4-week validation window")

    return {
        "verified": not errors,
        "errors": errors,
        "window_days": window["days"],
    }


def _distinct_ids(ids: list[str]) -> list[str]:
    seen = set()
    result: list[str] = []
    for record_id in ids:
        if record_id not in seen:
            seen.add(record_id)
            result.append(record_id)
    return result


def _weekly_review_window(weekly_records: list) -> dict:
    dates = [_parse_datetime(record.created_at) for record in weekly_records]
    dates = [date for date in dates if date is not None]
    if len(dates) < len(weekly_records):
        return {"valid": False, "days": None}
    if not dates:
        return {"valid": False, "days": None}
    ordered = sorted(dates)
    days = (ordered[-1] - ordered[0]).days
    iso_weeks = {(date.isocalendar().year, date.isocalendar().week) for date in ordered}
    return {
        "valid": days >= MIN_VALIDATION_WINDOW_DAYS or len(iso_weeks) >= 4,
        "days": days,
    }


def _parse_datetime(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed
