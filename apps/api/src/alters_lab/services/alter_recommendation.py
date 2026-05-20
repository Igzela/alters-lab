"""P6-M5 alter recommendation service."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.alter_recommendation import (
    AlterFactorScores,
    AlterOverrideRequest,
    AlterRecommendationRecord,
    AlterRecommendationRequest,
)
from alters_lab.services.p6_runtime import generate_record_id, list_records, read_record, utc_now, write_record

VALID_ALTER_IDS = ("alter_A", "alter_B", "alter_C", "alter_D")
SESSION_TYPE_PREFERRED = {
    "personal": "alter_A",
    "relationship": "alter_B",
    "learning": "alter_C",
    "project": "alter_D",
}


def build_alter_recommendation(request: AlterRecommendationRequest) -> AlterRecommendationRecord:
    scores: dict[str, AlterFactorScores] = {}
    for alter_id in VALID_ALTER_IDS:
        session_match = 1.0 if SESSION_TYPE_PREFERRED[request.session_type] == alter_id else 0.35
        drift_match = 1.0 if alter_id in request.unresolved_drift_alter_ids else 0.2
        challenge_value = 0.9 if request.self_deception_risk in ("medium", "high") else 0.45
        action_relevance = 0.8 if session_match == 1.0 or drift_match == 1.0 else 0.45
        overuse_penalty = 0.35 if alter_id in request.overused_alter_ids else 0.0
        total = round(session_match + drift_match + challenge_value + action_relevance - overuse_penalty, 4)
        scores[alter_id] = AlterFactorScores(
            session_type_match=session_match,
            unresolved_drift_match=drift_match,
            challenge_value=challenge_value,
            action_alignment_relevance=action_relevance,
            overuse_penalty=overuse_penalty,
            total=total,
        )
    ranked = sorted(scores.items(), key=lambda item: item[1].total, reverse=True)
    primary = ranked[0][0]
    counter = None
    counter_reason = None
    if _counter_alter_allowed(request):
        counter = ranked[1][0]
        counter_reason = "Counter-alter allowed by conflict/risk trigger; use it to expose tension, not debate."
    return AlterRecommendationRecord(
        recommendation_id=generate_record_id("alter_recommendation"),
        session_type=request.session_type,
        primary_alter_id=primary,
        counter_alter_id=counter,
        counter_alter_reason=counter_reason,
        factor_scores=scores,
        created_at=utc_now(),
    )


def save_alter_recommendation(record: AlterRecommendationRecord, repo_root: Path | None = None) -> Path:
    return write_record("alter_recommendations", record.recommendation_id, record.model_dump(), repo_root)


def load_alter_recommendation(recommendation_id: str, repo_root: Path | None = None) -> AlterRecommendationRecord:
    return AlterRecommendationRecord(**read_record("alter_recommendations", recommendation_id, repo_root))


def list_alter_recommendations(repo_root: Path | None = None) -> list[AlterRecommendationRecord]:
    return [AlterRecommendationRecord(**r) for r in list_records("alter_recommendations", repo_root)]


def override_alter_recommendation(
    record: AlterRecommendationRecord,
    request: AlterOverrideRequest,
) -> AlterRecommendationRecord:
    if request.override_alter_id not in VALID_ALTER_IDS:
        raise ValueError(f"Invalid override_alter_id: {request.override_alter_id}")
    updated = record.model_copy(deep=True)
    updated.override_alter_id = request.override_alter_id
    updated.override_reason = request.reason
    return updated


def _counter_alter_allowed(request: AlterRecommendationRequest) -> bool:
    return (
        request.decision_conflict_high
        or request.self_deception_risk in ("medium", "high")
        or request.repeated_failure_same_category
        or request.user_requests_deeper_review
    )
