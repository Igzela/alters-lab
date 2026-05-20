"""Service tests for P6 code-complete runtime gates."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from alters_lab.schemas.action_alignment import ActionAlignmentEvidence, ActionAlignmentScoreRequest, ActionAlignmentScores
from alters_lab.schemas.alter_recommendation import AlterOverrideRequest, AlterRecommendationRequest
from alters_lab.schemas.behavior_validation import (
    BehaviorValidationEvaluateRequest,
    BehaviorValidationMetrics,
    UsageIntegrityAudit,
)
from alters_lab.schemas.p6_data_retention import P6ArchiveRequest, P6DeleteRequest, P6ExportRequest, P6RecordRef
from alters_lab.schemas.p6_provider_policy import P6ProviderConfigValidationRequest
from alters_lab.schemas.pattern_review import PatternReviewRequest, WeeklyPatternSignal
from alters_lab.schemas.self_deception_challenge import EditChallengeRequest, SelfDeceptionEvaluateRequest
from alters_lab.schemas.weekly_reminder import WeeklyReminderCompleteRequest, WeeklyReminderSkipRequest
from alters_lab.schemas.weekly_review_session import WeeklyReviewCompleteRequest, WeeklyReviewStartRequest
from alters_lab.services.action_alignment import build_action_alignment_score, save_action_alignment_score
from alters_lab.services.alter_recommendation import (
    build_alter_recommendation,
    override_alter_recommendation,
    save_alter_recommendation,
)
from alters_lab.services.behavior_validation import evaluate_behavior_validation, save_behavior_validation
from alters_lab.services.obsidian_weekly_note import build_extracted_record, save_weekly_note_record
from alters_lab.services.p6_data_retention import archive_p6_records, delete_p6_record, export_p6_records
from alters_lab.services.p6_provider_policy import validate_p6_provider_config
from alters_lab.services.pattern_review import build_pattern_review, save_pattern_review
from alters_lab.services.phase6_closeout import build_phase6_closeout_report
from alters_lab.services.self_deception_challenge import build_edit_challenge, evaluate_self_deception
from alters_lab.services.weekly_reminder import build_complete_record, build_skip_record, save_reminder_record
from alters_lab.services.weekly_review_session import (
    complete_weekly_review_session,
    save_weekly_review_session,
    start_weekly_review_session,
)
from tests.test_obsidian_weekly_note import VALID_NOTE


def _create_completed_review(tmp_path):
    note = build_extracted_record(VALID_NOTE)
    save_weekly_note_record(note, tmp_path)
    session = start_weekly_review_session(WeeklyReviewStartRequest(weekly_note_record_id=note.record_id), tmp_path)
    save_weekly_review_session(session, tmp_path)
    completed = complete_weekly_review_session(
        session,
        WeeklyReviewCompleteRequest(
            review_note="Review note.",
            primary_next_correction="Pick one primary correction.",
            supporting_actions=["Block one review slot."],
        ),
    )
    save_weekly_review_session(completed, tmp_path)
    return note, completed


def _score_request(session_id: str) -> ActionAlignmentScoreRequest:
    return ActionAlignmentScoreRequest(
        session_id=session_id,
        scores=ActionAlignmentScores(direction_alignment=0.8, execution_consistency=0.7, avoidance_level=0.2),
        evidence=ActionAlignmentEvidence(
            one_action_evidence="Completed two focused coding sessions.",
            one_avoidance_or_friction_evidence="Missed one planned review block.",
            one_next_correction="Pick one primary correction.",
        ),
        verdict_label="aligned_progress",
        verdict_sentence="Progress was aligned but still somewhat noisy.",
    )


def _integrity(valid: bool = True) -> UsageIntegrityAudit:
    return UsageIntegrityAudit(
        weekly_notes_completed_honestly=valid,
        calibration_records_created=True,
        primary_corrections_set=True,
        failure_reviews_honest=True,
        self_deception_risk_not_softened=True,
        sessions_not_skipped_too_often=True,
    )


def _metrics(improved: bool = True) -> BehaviorValidationMetrics:
    return BehaviorValidationMetrics(
        action_alignment_score_improves=improved,
        repeated_negative_patterns_reduce=improved,
        primary_correction_completion_rate_improves=improved,
    )


def test_weekly_review_session_and_action_alignment(tmp_path):
    _, session = _create_completed_review(tmp_path)
    assert session.status == "completed"
    assert session.calibration_record_shell["derived_from_raw_note"] is True
    score = build_action_alignment_score(_score_request(session.session_id), tmp_path)
    path = save_action_alignment_score(score, tmp_path)
    assert score.action_alignment_score == pytest.approx(0.7667)
    assert "alters/product/calibration_records" in str(path)
    assert not (tmp_path / "alters" / "current").exists()


def test_action_alignment_rejects_out_of_range_score():
    with pytest.raises(ValidationError):
        ActionAlignmentScores(direction_alignment=1.2, execution_consistency=0.7, avoidance_level=0.2)


def test_self_deception_rules_and_edit_challenge(tmp_path):
    _, session = _create_completed_review(tmp_path)
    with pytest.raises(ValidationError):
        SelfDeceptionEvaluateRequest(session_id=session.session_id, self_deception_risk="medium")
    record = evaluate_self_deception(
        SelfDeceptionEvaluateRequest(
            session_id=session.session_id,
            self_deception_risk="high",
            rationalization_pattern="over_analysis",
            evidence="I spent the week planning instead of doing.",
            avoided_truth="The next action was small enough to do.",
            action_evidence_weak=True,
            explanation_contradicts_behavior=True,
        ),
        tmp_path,
    )
    assert record.challenge_level == "strong"
    edit = build_edit_challenge(EditChallengeRequest(lowered_avoidance_level=True))
    assert edit.challenge_required is True


def test_alter_recommendation_and_override(tmp_path):
    rec = build_alter_recommendation(
        AlterRecommendationRequest(
            session_type="project",
            self_deception_risk="medium",
            decision_conflict_high=True,
        )
    )
    assert rec.primary_alter_id in rec.factor_scores
    assert rec.counter_alter_id is not None
    path = save_alter_recommendation(rec, tmp_path)
    assert "alters/product/alter_recommendations" in str(path)
    updated = override_alter_recommendation(rec, AlterOverrideRequest(override_alter_id="alter_A", reason="Need the personal angle."))
    assert updated.override_alter_id == "alter_A"
    with pytest.raises(ValidationError):
        AlterOverrideRequest(override_alter_id="alter_A", reason="")


def test_reminder_skip_and_complete(tmp_path):
    _, session = _create_completed_review(tmp_path)
    with pytest.raises(ValidationError):
        WeeklyReminderSkipRequest(reason="")
    skipped = build_skip_record(WeeklyReminderSkipRequest(reason="Travel week."))
    save_reminder_record(skipped, tmp_path)
    completed = build_complete_record(WeeklyReminderCompleteRequest(weekly_review_session_id=session.session_id), tmp_path)
    assert completed.action == "completed"


def test_pattern_review_detects_three_of_four():
    review = build_pattern_review(
        PatternReviewRequest(
            weekly_patterns=[
                WeeklyPatternSignal(week_id="w1", patterns=["repeated_over_scope"], confidence=0.9),
                WeeklyPatternSignal(week_id="w2", patterns=["repeated_over_scope"], confidence=0.85),
                WeeklyPatternSignal(week_id="w3", patterns=[], confidence=0.9),
                WeeklyPatternSignal(week_id="w4", patterns=["repeated_over_scope"], confidence=0.95),
            ]
        )
    )
    assert review.status == "pattern_triggered"
    assert review.triggered_patterns[0].occurrences == 3


def test_data_retention_export_delete_archive(tmp_path):
    note = build_extracted_record(VALID_NOTE)
    save_weekly_note_record(note, tmp_path)
    export_path = export_p6_records(P6ExportRequest(areas=["weekly_notes"]), tmp_path)
    assert "alters/product/exports" in str(export_path)
    archive_path = archive_p6_records(
        P6ArchiveRequest(
            records=[P6RecordRef(area="weekly_notes", record_id=note.record_id)],
            confirmation="archive",
        ),
        tmp_path,
    )
    assert archive_path.exists()
    delete_p6_record(P6DeleteRequest(record=P6RecordRef(area="weekly_notes", record_id=note.record_id), confirmation="delete"), tmp_path)
    assert not (tmp_path / "alters" / "product" / "weekly_notes" / f"{note.record_id}.yaml").exists()


def test_provider_policy_requires_explicit_real_config():
    rejected = validate_p6_provider_config(P6ProviderConfigValidationRequest(mode="openai_compatible_http"))
    assert rejected.valid is False
    accepted = validate_p6_provider_config(
        P6ProviderConfigValidationRequest(
            mode="openai_compatible_http",
            base_url_configured=True,
            api_key_configured=True,
            explicit_user_configuration=True,
        )
    )
    assert accepted.valid is True
    assert accepted.api_key_returned is False


def test_behavior_validation_outcomes_and_phase6_gate(tmp_path):
    insufficient = evaluate_behavior_validation(
        BehaviorValidationEvaluateRequest(
            weekly_review_ids=["w1"],
            calibration_record_ids=["c1"],
            pattern_review_ids=[],
            metrics=_metrics(True),
            usage_integrity=_integrity(True),
        )
    )
    assert insufficient.outcome == "P6_INSUFFICIENT_DATA"

    invalid = evaluate_behavior_validation(
        BehaviorValidationEvaluateRequest(
            weekly_review_ids=["w1", "w2", "w3", "w4"],
            calibration_record_ids=["c1", "c2", "c3", "c4"],
            pattern_review_ids=["p1"],
            metrics=_metrics(True),
            usage_integrity=_integrity(False),
        )
    )
    assert invalid.outcome == "P6_USAGE_INVALID"

    validated = evaluate_behavior_validation(
        BehaviorValidationEvaluateRequest(
            weekly_review_ids=["w1", "w2", "w3", "w4"],
            calibration_record_ids=["c1", "c2", "c3", "c4"],
            pattern_review_ids=["p1"],
            metrics=_metrics(True),
            usage_integrity=_integrity(True),
        )
    )
    save_behavior_validation(validated, tmp_path)
    pattern = build_pattern_review(PatternReviewRequest(weekly_patterns=[]))
    save_pattern_review(pattern, tmp_path)
    report = build_phase6_closeout_report(tmp_path)
    assert report.status == "PASS"


def test_phase6_closeout_blocked_without_behavior_validation(tmp_path):
    report = build_phase6_closeout_report(tmp_path)
    assert report.status == "BLOCKED"
    assert report.summary.sealed_baseline_candidate is False
