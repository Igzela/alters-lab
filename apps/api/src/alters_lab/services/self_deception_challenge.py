"""P6-M4 self-deception and evidence challenge service."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.self_deception_challenge import (
    EditChallengeRequest,
    EditChallengeResponse,
    SelfDeceptionChallengeRecord,
    SelfDeceptionEvaluateRequest,
)
from alters_lab.services.p6_runtime import generate_record_id, list_records, utc_now, write_record
from alters_lab.services.weekly_review_session import load_weekly_review_session


def evaluate_self_deception(
    request: SelfDeceptionEvaluateRequest,
    repo_root: Path | None = None,
) -> SelfDeceptionChallengeRecord:
    load_weekly_review_session(request.session_id, repo_root)
    strong_allowed = (
        request.self_deception_risk == "high"
        and request.action_evidence_weak
        and request.explanation_contradicts_behavior
        and request.existing_strong_challenge_count == 0
    )
    challenge_level = "none"
    challenge_text = None
    if request.self_deception_risk in ("medium", "high"):
        challenge_level = "gentle"
        challenge_text = "What concrete action evidence supports this explanation?"
    if strong_allowed:
        challenge_level = "strong"
        challenge_text = "The action evidence is weak and contradicts the explanation; name the avoided truth before choosing next steps."
    return SelfDeceptionChallengeRecord(
        challenge_id=generate_record_id("self_deception"),
        session_id=request.session_id,
        self_deception_risk=request.self_deception_risk,
        rationalization_pattern=request.rationalization_pattern,
        evidence=request.evidence,
        avoided_truth=request.avoided_truth,
        strong_challenge_allowed=strong_allowed,
        challenge_level=challenge_level,
        challenge_text=challenge_text,
        created_at=utc_now(),
    )


def save_self_deception_record(record: SelfDeceptionChallengeRecord, repo_root: Path | None = None) -> Path:
    return write_record("self_deception_challenges", record.challenge_id, record.model_dump(), repo_root)


def list_self_deception_records(repo_root: Path | None = None) -> list[SelfDeceptionChallengeRecord]:
    return [SelfDeceptionChallengeRecord(**r) for r in list_records("self_deception_challenges", repo_root)]


def build_edit_challenge(request: EditChallengeRequest) -> EditChallengeResponse:
    triggers: list[str] = []
    if request.lowered_self_deception_risk:
        triggers.append("lowered_self_deception_risk")
    if request.changed_failure_status:
        triggers.append("changed_failure_status")
    if request.lowered_avoidance_level:
        triggers.append("lowered_avoidance_level")
    if request.deleted_negative_facts:
        triggers.append("deleted_negative_facts")
    required = bool(triggers)
    return EditChallengeResponse(
        status="challenge_required" if required else "no_challenge",
        challenge_required=required,
        challenge_question="这是事实修正，还是叙事软化？" if required else None,
        triggers=triggers,
    )
