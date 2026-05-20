"""P6-M3 action alignment scoring service."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.action_alignment import (
    ActionAlignmentScoreRecord,
    ActionAlignmentScoreRequest,
)
from alters_lab.services.p6_runtime import generate_record_id, list_records, read_record, utc_now, write_record
from alters_lab.services.weekly_review_session import load_weekly_review_session


def build_action_alignment_score(
    request: ActionAlignmentScoreRequest,
    repo_root: Path | None = None,
) -> ActionAlignmentScoreRecord:
    load_weekly_review_session(request.session_id, repo_root)
    scores = request.scores
    aggregate = round(
        (scores.direction_alignment + scores.execution_consistency + (1.0 - scores.avoidance_level)) / 3.0,
        4,
    )
    return ActionAlignmentScoreRecord(
        score_id=generate_record_id("action_alignment"),
        session_id=request.session_id,
        scores=scores,
        action_alignment_score=aggregate,
        evidence=request.evidence,
        verdict_label=request.verdict_label,
        verdict_sentence=request.verdict_sentence.strip(),
        created_at=utc_now(),
    )


def save_action_alignment_score(record: ActionAlignmentScoreRecord, repo_root: Path | None = None) -> Path:
    return write_record("calibration_records", record.score_id, record.model_dump(), repo_root)


def load_action_alignment_score(score_id: str, repo_root: Path | None = None) -> ActionAlignmentScoreRecord:
    return ActionAlignmentScoreRecord(**read_record("calibration_records", score_id, repo_root))


def list_action_alignment_scores(repo_root: Path | None = None) -> list[ActionAlignmentScoreRecord]:
    return [
        ActionAlignmentScoreRecord(**r)
        for r in list_records("calibration_records", repo_root)
        if r.get("source_type") == "weekly_review_session"
    ]
