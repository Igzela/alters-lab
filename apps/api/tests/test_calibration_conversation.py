"""Tests for LLM-Driven Calibration conversation service."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from alters_lab.schemas.calibration_conversation import (
    BehaviorMetricsExtract,
    CalibrationConversation,
    CalibrationDraft,
    ConversationMessage,
    ExternalEvidenceExtract,
    OutcomeTargetExtract,
    PredictorProfileExtract,
)
from alters_lab.schemas.calibration_loop import CalibrationScoreValues
from alters_lab.services import calibration_conversation as svc


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """Provide a temporary repo root for tests."""
    return tmp_path


# --- Schema tests ---


class TestSchemaValidation:
    def test_behavior_metrics_extract_all_none(self):
        bm = BehaviorMetricsExtract()
        assert bm.career_education_deep_work_minutes is None
        assert bm.week_start is None

    def test_behavior_metrics_extract_with_values(self):
        bm = BehaviorMetricsExtract(
            career_education_deep_work_minutes=120,
            regular_sleep_nights=5,
            planned_commitment_follow_through_rate=0.75,
        )
        assert bm.career_education_deep_work_minutes == 120
        assert bm.regular_sleep_nights == 5

    def test_behavior_metrics_extract_rejects_negative(self):
        with pytest.raises(Exception):
            BehaviorMetricsExtract(career_education_deep_work_minutes=-1)

    def test_behavior_metrics_extract_rejects_rate_over_one(self):
        with pytest.raises(Exception):
            BehaviorMetricsExtract(planned_commitment_follow_through_rate=1.5)

    def test_rubric_scores_validation(self):
        scores = CalibrationScoreValues(
            execution_discipline=3,
            exploration_freedom=4,
            life_state_match=3,
            energy_level=2,
        )
        assert scores.execution_discipline == 3

    def test_rubric_scores_rejects_zero(self):
        with pytest.raises(Exception):
            CalibrationScoreValues(
                execution_discipline=0,
                exploration_freedom=4,
                life_state_match=3,
                energy_level=2,
            )

    def test_rubric_scores_rejects_six(self):
        with pytest.raises(Exception):
            CalibrationScoreValues(
                execution_discipline=3,
                exploration_freedom=4,
                life_state_match=3,
                energy_level=6,
            )

    def test_external_evidence_requires_description(self):
        with pytest.raises(Exception):
            ExternalEvidenceExtract(
                domain="health",
                evidence_type="health_measurement",
                description="",
                objective_strength="moderate",
                polarity="positive",
            )

    def test_external_evidence_valid(self):
        ev = ExternalEvidenceExtract(
            domain="health",
            evidence_type="health_measurement",
            description="Ran 5k in 25 minutes",
            objective_strength="strong",
            polarity="positive",
            numeric_value=5.0,
            unit="km",
        )
        assert ev.description == "Ran 5k in 25 minutes"

    def test_draft_auto_generates_id(self):
        draft = CalibrationDraft(conversation_id="conv_test")
        assert draft.draft_id.startswith("cd_")
        assert draft.created_at  # auto-filled
        assert draft.status == "pending"

    def test_conversation_auto_generates_id(self):
        conv = CalibrationConversation()
        assert conv.conversation_id.startswith("conv_")
        assert conv.status == "active"

    def test_conversation_message_auto_fills_timestamp(self):
        msg = ConversationMessage(role="user", content="hello")
        assert msg.timestamp  # auto-filled

    def test_outcome_target_extract(self):
        ot = OutcomeTargetExtract(
            domain="career_education",
            outcome_name="Get promoted",
            objective_definition="Receive a promotion to senior engineer",
            success_threshold="Title change confirmed by manager",
            measurement_method="HR records",
            horizon_months=12,
            baseline_value="mid-level",
            target_value="senior",
        )
        assert ot.domain == "career_education"
        assert ot.outcome_name == "Get promoted"
        assert ot.horizon_months == 12
        assert ot.baseline_value == "mid-level"

    def test_outcome_target_extract_requires_objective_definition(self):
        with pytest.raises(Exception):
            OutcomeTargetExtract(
                domain="health",
                outcome_name="Lose weight",
                objective_definition="",
                success_threshold="5kg lost",
                measurement_method="scale",
            )

    def test_predictor_profile_extract(self):
        pp = PredictorProfileExtract(
            conscientiousness=0.7,
            neuroticism_negative_emotionality=0.3,
            extraversion=0.6,
            agreeableness=0.8,
            openness=0.9,
            trait_source="short_self_report",
            education_status="bachelors",
            employment_status="full_time",
            financial_stability="stable",
            relationship_status="single",
            health_constraints=["mild_back_pain"],
            target_domains=["career_education", "health"],
            time_horizon_months=12,
            limitations=["limited_evening_time"],
        )
        assert pp.conscientiousness == 0.7
        assert pp.trait_source == "short_self_report"
        assert pp.target_domains == ["career_education", "health"]
        assert pp.limitations == ["limited_evening_time"]


# --- Extraction parser tests ---


class TestExtractionParser:
    def test_valid_extraction(self):
        output = """Here's what I understood:

<extraction>
{
  "behavior_metrics": {"career_education_deep_work_minutes": 120},
  "extraction_confidence": "medium",
  "reasoning": "User mentioned 2 hours daily"
}
</extraction>"""
        result = svc._extract_json_from_llm_output(output)
        assert result is not None
        assert result["behavior_metrics"]["career_education_deep_work_minutes"] == 120

    def test_no_extraction_returns_none(self):
        result = svc._extract_json_from_llm_output("Just a normal message")
        assert result is None

    def test_invalid_json_returns_none(self):
        output = "<extraction>not json</extraction>"
        result = svc._extract_json_from_llm_output(output)
        assert result is None

    def test_extraction_with_evidence(self):
        output = """<extraction>
{
  "external_evidence": [
    {
      "domain": "career_education",
      "evidence_type": "milestone_completed",
      "description": "Finished the Python course",
      "objective_strength": "strong",
      "polarity": "positive"
    }
  ],
  "extraction_confidence": "high",
  "reasoning": "User clearly stated course completion"
}
</extraction>"""
        result = svc._extract_json_from_llm_output(output)
        assert result is not None
        assert len(result["external_evidence"]) == 1

    def test_extraction_with_outcome_targets(self):
        output = """<extraction>
{
  "outcome_targets": [
    {
      "domain": "career_education",
      "outcome_name": "Learn Rust",
      "objective_definition": "Complete Rust book and ship a CLI tool",
      "success_threshold": "Published CLI on GitHub with 10+ stars",
      "measurement_method": "GitHub metrics",
      "horizon_months": 6
    }
  ],
  "extraction_confidence": "medium",
  "reasoning": "User mentioned learning goal"
}
</extraction>"""
        result = svc._extract_json_from_llm_output(output)
        assert result is not None
        assert len(result["outcome_targets"]) == 1
        assert result["outcome_targets"][0]["outcome_name"] == "Learn Rust"

    def test_extraction_with_predictor_profile(self):
        output = """<extraction>
{
  "predictor_profile": {
    "conscientiousness": 0.7,
    "extraversion": 0.5,
    "education_status": "bachelors",
    "employment_status": "full_time",
    "target_domains": ["career_education"],
    "time_horizon_months": 12
  },
  "extraction_confidence": "medium",
  "reasoning": "User described personality and situation"
}
</extraction>"""
        result = svc._extract_json_from_llm_output(output)
        assert result is not None
        assert result["predictor_profile"]["conscientiousness"] == 0.7
        assert result["predictor_profile"]["target_domains"] == ["career_education"]


# --- Draft building tests ---


class TestDraftBuilding:
    def test_build_draft_with_behavior_metrics(self):
        extraction = {
            "behavior_metrics": {"career_education_deep_work_minutes": 90},
            "extraction_confidence": "high",
            "reasoning": "User said 1.5 hours",
        }
        draft = svc._build_draft_from_extraction(extraction, "conv_test")
        assert draft is not None
        assert draft.behavior_metrics is not None
        assert draft.behavior_metrics.career_education_deep_work_minutes == 90
        assert draft.extraction_confidence == "high"

    def test_build_draft_with_rubric_scores(self):
        extraction = {
            "rubric_scores": {
                "execution_discipline": 3,
                "exploration_freedom": 4,
                "life_state_match": 3,
                "energy_level": 2,
            },
            "extraction_confidence": "medium",
            "reasoning": "",
        }
        draft = svc._build_draft_from_extraction(extraction, "conv_test")
        assert draft is not None
        assert draft.rubric_scores is not None
        assert draft.rubric_scores.execution_discipline == 3

    def test_build_draft_with_evidence(self):
        extraction = {
            "external_evidence": [
                {
                    "domain": "health",
                    "evidence_type": "health_measurement",
                    "description": "Lost 2kg this month",
                    "objective_strength": "moderate",
                    "polarity": "positive",
                }
            ],
            "extraction_confidence": "medium",
            "reasoning": "",
        }
        draft = svc._build_draft_from_extraction(extraction, "conv_test")
        assert draft is not None
        assert len(draft.external_evidence) == 1

    def test_build_draft_empty_returns_none(self):
        extraction = {"extraction_confidence": "low", "reasoning": "nothing"}
        draft = svc._build_draft_from_extraction(extraction, "conv_test")
        assert draft is None

    def test_build_draft_none_returns_none(self):
        draft = svc._build_draft_from_extraction(None, "conv_test")
        assert draft is None

    def test_build_draft_with_outcome_targets(self):
        extraction = {
            "outcome_targets": [
                {
                    "domain": "health",
                    "outcome_name": "Run a marathon",
                    "objective_definition": "Complete a full 42km marathon",
                    "success_threshold": "Finish under 4:30",
                    "measurement_method": "Race timing chip",
                    "horizon_months": 12,
                }
            ],
            "extraction_confidence": "medium",
            "reasoning": "User shared fitness goal",
        }
        draft = svc._build_draft_from_extraction(extraction, "conv_test")
        assert draft is not None
        assert len(draft.outcome_targets) == 1
        assert draft.outcome_targets[0].outcome_name == "Run a marathon"
        assert draft.extraction_confidence == "medium"

    def test_build_draft_with_predictor_profile(self):
        extraction = {
            "predictor_profile": {
                "conscientiousness": 0.8,
                "neuroticism_negative_emotionality": 0.4,
                "trait_source": "manual_estimate",
                "education_status": "masters",
                "employment_status": "freelance",
                "target_domains": ["career_education", "financial"],
                "time_horizon_months": 6,
            },
            "extraction_confidence": "medium",
            "reasoning": "User described background",
        }
        draft = svc._build_draft_from_extraction(extraction, "conv_test")
        assert draft is not None
        assert draft.predictor_profile is not None
        assert draft.predictor_profile.conscientiousness == 0.8
        assert draft.predictor_profile.trait_source == "manual_estimate"
        assert draft.predictor_profile.target_domains == [
            "career_education",
            "financial",
        ]


# --- Conversation lifecycle tests ---


class TestConversationLifecycle:
    def test_start_conversation(self, repo):
        conv = svc.start_conversation(repo_root=repo)
        assert conv.conversation_id.startswith("conv_")
        assert conv.status == "active"
        assert len(conv.messages) == 1
        assert conv.messages[0].role == "assistant"

    def test_send_message_mock_mode(self, repo):
        original = os.environ.get("ALTERS_PROVIDER_MODE")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "mock"
            conv = svc.start_conversation(repo_root=repo)
            conv, draft = svc.send_message(
                conv.conversation_id, "这周学了两小时 Python", repo_root=repo
            )
            assert len(conv.messages) == 3  # opening + user + assistant
            assert conv.messages[1].role == "user"
            assert conv.messages[2].role == "assistant"
        finally:
            if original is not None:
                os.environ["ALTERS_PROVIDER_MODE"] = original
            else:
                os.environ.pop("ALTERS_PROVIDER_MODE", None)

    def test_send_message_to_inactive_raises(self, repo):
        conv = svc.start_conversation(repo_root=repo)
        conv.status = "completed"
        svc._save_conversation(conv, repo_root=repo)
        with pytest.raises(ValueError, match="not active"):
            svc.send_message(conv.conversation_id, "hello", repo_root=repo)

    def test_get_conversation(self, repo):
        conv = svc.start_conversation(repo_root=repo)
        loaded = svc.get_conversation(conv.conversation_id, repo_root=repo)
        assert loaded.conversation_id == conv.conversation_id

    def test_get_nonexistent_conversation_raises(self, repo):
        with pytest.raises(FileNotFoundError):
            svc.get_conversation("conv_nonexistent", repo_root=repo)


# --- Draft lifecycle tests ---


class TestDraftLifecycle:
    def test_save_and_load_draft(self, repo):
        draft = CalibrationDraft(conversation_id="conv_test")
        svc._save_draft(draft, repo_root=repo)
        loaded = svc._load_draft(draft.draft_id, repo_root=repo)
        assert loaded.draft_id == draft.draft_id

    def test_list_drafts_empty(self, repo):
        drafts = svc.list_drafts(repo_root=repo)
        assert drafts == []

    def test_list_drafts_with_filter(self, repo):
        draft = CalibrationDraft(conversation_id="conv_test")
        svc._save_draft(draft, repo_root=repo)
        assert len(svc.list_drafts(status="pending", repo_root=repo)) == 1
        assert len(svc.list_drafts(status="confirmed", repo_root=repo)) == 0

    def test_confirm_draft(self, repo):
        draft = CalibrationDraft(
            conversation_id="conv_test",
            behavior_metrics=BehaviorMetricsExtract(
                career_education_deep_work_minutes=100,
                regular_sleep_nights=5,
            ),
        )
        svc._save_draft(draft, repo_root=repo)
        confirmed = svc.confirm_draft(draft.draft_id, repo_root=repo)
        assert confirmed.status == "confirmed"
        assert confirmed.confirmed_at is not None

    def test_confirm_non_pending_raises(self, repo):
        draft = CalibrationDraft(conversation_id="conv_test", status="confirmed")
        svc._save_draft(draft, repo_root=repo)
        with pytest.raises(ValueError, match="not pending"):
            svc.confirm_draft(draft.draft_id, repo_root=repo)

    def test_reject_draft(self, repo):
        draft = CalibrationDraft(conversation_id="conv_test")
        svc._save_draft(draft, repo_root=repo)
        rejected = svc.reject_draft(draft.draft_id, repo_root=repo)
        assert rejected.status == "rejected"

    def test_reject_non_pending_raises(self, repo):
        draft = CalibrationDraft(conversation_id="conv_test", status="rejected")
        svc._save_draft(draft, repo_root=repo)
        with pytest.raises(ValueError, match="not pending"):
            svc.reject_draft(draft.draft_id, repo_root=repo)

    def test_confirm_draft_writes_outcome_targets(self, repo, monkeypatch):
        written = []

        def fake_write_record(record_type, record_id, data, repo_root):
            written.append(record_type)

        monkeypatch.setattr(svc, "write_record", fake_write_record)

        draft = CalibrationDraft(
            conversation_id="conv_test",
            outcome_targets=[
                OutcomeTargetExtract(
                    domain="career_education",
                    outcome_name="Ship a product",
                    objective_definition="Launch v1 of side project",
                    success_threshold="100 users signed up",
                    measurement_method="Analytics dashboard",
                    horizon_months=6,
                ),
            ],
        )
        svc._save_draft(draft, repo_root=repo)
        confirmed = svc.confirm_draft(draft.draft_id, repo_root=repo)
        assert confirmed.status == "confirmed"
        assert "branch_outcome_targets" in written

    def test_confirm_draft_writes_predictor_profile(self, repo, monkeypatch):
        written = []

        def fake_write_record(record_type, record_id, data, repo_root):
            written.append(record_type)

        monkeypatch.setattr(svc, "write_record", fake_write_record)

        draft = CalibrationDraft(
            conversation_id="conv_test",
            predictor_profile=PredictorProfileExtract(
                conscientiousness=0.7,
                extraversion=0.5,
                trait_source="short_self_report",
                target_domains=["health"],
                time_horizon_months=6,
            ),
        )
        svc._save_draft(draft, repo_root=repo)
        confirmed = svc.confirm_draft(draft.draft_id, repo_root=repo)
        assert confirmed.status == "confirmed"
        assert "predictor_profiles" in written


# --- Mock provider integration test ---


class TestMockProviderIntegration:
    def test_full_flow_start_message_confirm(self, repo):
        original = os.environ.get("ALTERS_PROVIDER_MODE")
        try:
            os.environ["ALTERS_PROVIDER_MODE"] = "mock"

            # Start conversation
            conv = svc.start_conversation(repo_root=repo)
            cid = conv.conversation_id

            # Send a message (mock won't produce extraction, but flow should work)
            conv, draft = svc.send_message(cid, "这周还不错", repo_root=repo)
            assert conv.messages[-1].role == "assistant"

            # If mock produced a draft, confirm it
            if draft:
                confirmed = svc.confirm_draft(draft.draft_id, repo_root=repo)
                assert confirmed.status == "confirmed"

        finally:
            if original is not None:
                os.environ["ALTERS_PROVIDER_MODE"] = original
            else:
                os.environ.pop("ALTERS_PROVIDER_MODE", None)


# --- Edge case tests ---


class TestEdgeCases:
    def test_draft_with_all_metrics(self, repo):
        draft = CalibrationDraft(
            conversation_id="conv_test",
            behavior_metrics=BehaviorMetricsExtract(
                week_start="2026-06-01",
                week_end="2026-06-07",
                career_education_deep_work_minutes=120,
                planned_commitment_follow_through_rate=0.8,
                expense_logged_days=5,
                regular_sleep_nights=6,
                moderate_vigorous_activity_minutes=90,
                avoidable_health_risk_events=0,
                meaningful_social_contact_count=3,
                abandoned_committed_blocks=1,
                notes="Good week overall",
            ),
            rubric_scores=CalibrationScoreValues(
                execution_discipline=4,
                exploration_freedom=3,
                life_state_match=4,
                energy_level=3,
            ),
            extraction_confidence="high",
            llm_reasoning="User provided clear numbers",
        )
        svc._save_draft(draft, repo_root=repo)
        confirmed = svc.confirm_draft(draft.draft_id, repo_root=repo)
        assert confirmed.status == "confirmed"

    def test_extraction_with_multiline_json(self):
        output = """<extraction>
{
  "behavior_metrics": {
    "career_education_deep_work_minutes": 60,
    "regular_sleep_nights": 7
  },
  "rubric_scores": {
    "execution_discipline": 4,
    "exploration_freedom": 3,
    "life_state_match": 4,
    "energy_level": 3
  },
  "extraction_confidence": "high",
  "reasoning": "User was very specific"
}
</extraction>"""
        result = svc._extract_json_from_llm_output(output)
        assert result is not None
        assert result["behavior_metrics"]["career_education_deep_work_minutes"] == 60
        assert result["rubric_scores"]["execution_discipline"] == 4

    def test_extraction_with_extra_text(self):
        output = """Here's my understanding:

<extraction>
{
  "behavior_metrics": {"career_education_deep_work_minutes": 90},
  "extraction_confidence": "medium",
  "reasoning": "Approximate from conversation"
}
</extraction>

Let me know if I got anything wrong!"""
        result = svc._extract_json_from_llm_output(output)
        assert result is not None
        assert result["behavior_metrics"]["career_education_deep_work_minutes"] == 90

    def test_draft_with_user_corrections(self, repo):
        draft = CalibrationDraft(
            conversation_id="conv_test",
            behavior_metrics=BehaviorMetricsExtract(
                career_education_deep_work_minutes=100,
            ),
        )
        svc._save_draft(draft, repo_root=repo)
        confirmed = svc.confirm_draft(
            draft.draft_id,
            corrections={"career_education_deep_work_minutes": 120},
            repo_root=repo,
        )
        assert confirmed.user_corrections["career_education_deep_work_minutes"] == 120

    def test_draft_with_empty_evidence_list(self, repo):
        draft = CalibrationDraft(
            conversation_id="conv_test",
            behavior_metrics=BehaviorMetricsExtract(
                career_education_deep_work_minutes=60,
            ),
            external_evidence=[],
        )
        svc._save_draft(draft, repo_root=repo)
        confirmed = svc.confirm_draft(draft.draft_id, repo_root=repo)
        assert confirmed.status == "confirmed"

    def test_full_extraction_with_all_types(self):
        output = """<extraction>
{
  "behavior_metrics": {
    "career_education_deep_work_minutes": 120,
    "regular_sleep_nights": 6
  },
  "rubric_scores": {
    "execution_discipline": 4,
    "exploration_freedom": 3,
    "life_state_match": 4,
    "energy_level": 3
  },
  "external_evidence": [
    {
      "domain": "health",
      "evidence_type": "health_measurement",
      "description": "Ran 5k in 22 minutes",
      "objective_strength": "strong",
      "polarity": "positive"
    }
  ],
  "outcome_targets": [
    {
      "domain": "career_education",
      "outcome_name": "Master Rust",
      "objective_definition": "Build a production CLI tool in Rust",
      "success_threshold": "Published on crates.io with downloads",
      "measurement_method": "crates.io stats",
      "horizon_months": 6
    }
  ],
  "predictor_profile": {
    "conscientiousness": 0.8,
    "neuroticism_negative_emotionality": 0.3,
    "extraversion": 0.5,
    "trait_source": "short_self_report",
    "education_status": "bachelors",
    "employment_status": "full_time",
    "target_domains": ["career_education", "health"],
    "time_horizon_months": 12
  },
  "extraction_confidence": "high",
  "reasoning": "User provided detailed information across all categories"
}
</extraction>"""
        result = svc._extract_json_from_llm_output(output)
        assert result is not None
        assert result["behavior_metrics"]["career_education_deep_work_minutes"] == 120
        assert result["rubric_scores"]["execution_discipline"] == 4
        assert len(result["external_evidence"]) == 1
        assert len(result["outcome_targets"]) == 1
        assert result["predictor_profile"]["conscientiousness"] == 0.8

        draft = svc._build_draft_from_extraction(result, "conv_test")
        assert draft is not None
        assert draft.behavior_metrics is not None
        assert draft.rubric_scores is not None
        assert len(draft.external_evidence) == 1
        assert len(draft.outcome_targets) == 1
        assert draft.predictor_profile is not None
        assert draft.extraction_confidence == "high"
