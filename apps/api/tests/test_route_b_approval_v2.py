"""Tests for Route B approval hardening v2 — artifact_class and approval guardrails."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from alters_lab.schemas.population_baseline import (
    PopulationBaselineModelCard,
    PopulationPriorArtifact,
)


# --- Helper factories ---


def _valid_model_card(**overrides):
    base = {
        "model_id": "test_model",
        "outcome_id": "test_outcome",
        "model_family": "baseline_table",
        "transfer_risk": "medium",
    }
    base.update(overrides)
    return base


def _valid_prior_artifact(**overrides):
    base = {
        "artifact_id": "test_artifact",
        "model_id": "test_model",
        "generated_at": "2026-01-01T00:00:00Z",
        "domain": "health",
        "prior_type": "baseline_table",
        "prior_direction": "favorable",
        "confidence": "medium",
        "transfer_risk": "medium",
        "explanation": "Test explanation",
    }
    base.update(overrides)
    return base


# --- Artifact class tests ---


class TestArtifactClass:
    def test_defaults_to_contextual_prior(self):
        artifact = PopulationPriorArtifact(**_valid_prior_artifact())
        assert artifact.artifact_class == "contextual_prior"

    def test_accepts_data_backed_baseline(self):
        artifact = PopulationPriorArtifact(
            **_valid_prior_artifact(
                artifact_class="data_backed_baseline",
                actual_data_used=True,
            )
        )
        assert artifact.artifact_class == "data_backed_baseline"

    def test_accepts_calibrated_model(self):
        artifact = PopulationPriorArtifact(
            **_valid_prior_artifact(
                artifact_class="calibrated_model",
                actual_data_used=True,
                value_labels_confirmed=True,
                missingness_reviewed=True,
            )
        )
        assert artifact.artifact_class == "calibrated_model"

    def test_rejects_invalid_class(self):
        with pytest.raises(ValidationError):
            PopulationPriorArtifact(
                **_valid_prior_artifact(artifact_class="invalid_class")
            )


class TestActualDataUsedGuardrail:
    def test_contextual_prior_cannot_have_actual_data(self):
        with pytest.raises(ValidationError, match="contextual_prior cannot have actual_data_used=true"):
            PopulationPriorArtifact(
                **_valid_prior_artifact(
                    artifact_class="contextual_prior",
                    actual_data_used=True,
                )
            )

    def test_data_backed_must_have_actual_data(self):
        with pytest.raises(ValidationError, match="data_backed_baseline must have actual_data_used=true"):
            PopulationPriorArtifact(
                **_valid_prior_artifact(
                    artifact_class="data_backed_baseline",
                    actual_data_used=False,
                )
            )

    def test_data_backed_with_actual_data_ok(self):
        artifact = PopulationPriorArtifact(
            **_valid_prior_artifact(
                artifact_class="data_backed_baseline",
                actual_data_used=True,
                baseline_table_id="midus_self_rated_health",
            )
        )
        assert artifact.actual_data_used is True
        assert artifact.baseline_table_id == "midus_self_rated_health"


# --- Model card approval guardrails ---


class TestModelCardApprovalGuardrails:
    def test_defaults_to_unapproved(self):
        card = PopulationBaselineModelCard(**_valid_model_card())
        assert card.approval_level == "unapproved"
        assert card.approved_for_route_b is False

    def test_route_b_approved_syncs_flag(self):
        card = PopulationBaselineModelCard(
            **_valid_model_card(
                artifact_class="data_backed_baseline",
                approval_level="route_b_approved",
            )
        )
        assert card.approved_for_route_b is True

    def test_unapproved_syncs_flag_false(self):
        card = PopulationBaselineModelCard(
            **_valid_model_card(
                artifact_class="data_backed_baseline",
                approval_level="route_b_approved",
            )
        )
        # Manually set to unapproved
        card2 = PopulationBaselineModelCard(
            **_valid_model_card(
                artifact_class="data_backed_baseline",
                approval_level="unapproved",
            )
        )
        assert card2.approved_for_route_b is False

    def test_contextual_prior_cannot_be_route_b_approved(self):
        with pytest.raises(ValidationError, match="contextual_prior cannot be route_b_approved"):
            PopulationBaselineModelCard(
                **_valid_model_card(
                    artifact_class="contextual_prior",
                    approval_level="route_b_approved",
                )
            )

    def test_contextual_prior_can_be_lab_only(self):
        card = PopulationBaselineModelCard(
            **_valid_model_card(
                artifact_class="contextual_prior",
                approval_level="lab_only",
            )
        )
        assert card.approval_level == "lab_only"
        assert card.approved_for_route_b is False

    def test_route_b_approved_requires_empty_blockers(self):
        with pytest.raises(ValidationError, match="Cannot approve for Route B with blockers"):
            PopulationBaselineModelCard(
                **_valid_model_card(
                    artifact_class="data_backed_baseline",
                    approval_level="route_b_approved",
                    approval_blockers=["missing_value_labels"],
                )
            )

    def test_route_b_approved_with_empty_blockers_ok(self):
        card = PopulationBaselineModelCard(
            **_valid_model_card(
                artifact_class="data_backed_baseline",
                approval_level="route_b_approved",
                approval_blockers=[],
            )
        )
        assert card.approval_level == "route_b_approved"

    def test_approval_reason_and_blockers_default(self):
        card = PopulationBaselineModelCard(**_valid_model_card())
        assert card.approval_reason == ""
        assert card.approval_blockers == []


# --- New field defaults ---


class TestNewFieldDefaults:
    def test_artifact_new_fields_default(self):
        artifact = PopulationPriorArtifact(**_valid_prior_artifact())
        assert artifact.actual_data_used is False
        assert artifact.baseline_table_id is None
        assert artifact.value_labels_confirmed is False
        assert artifact.missingness_reviewed is False
        assert artifact.validation_report_id is None

    def test_model_card_new_fields_default(self):
        card = PopulationBaselineModelCard(**_valid_model_card())
        assert card.artifact_class == "contextual_prior"
        assert card.approval_level == "unapproved"
        assert card.approval_reason == ""
        assert card.approval_blockers == []


# --- Literature-only artifact rejection ---


class TestLiteratureOnlyRejection:
    def test_textual_artifact_is_contextual_by_default(self):
        artifact = PopulationPriorArtifact(
            **_valid_prior_artifact(
                prior_type="textual",
                artifact_class="contextual_prior",
            )
        )
        assert artifact.artifact_class == "contextual_prior"
        assert artifact.actual_data_used is False

    def test_textual_artifact_cannot_claim_data_backed(self):
        with pytest.raises(ValidationError, match="contextual_prior cannot have actual_data_used=true"):
            PopulationPriorArtifact(
                **_valid_prior_artifact(
                    prior_type="textual",
                    artifact_class="contextual_prior",
                    actual_data_used=True,
                )
            )


# --- No life score anywhere ---


class TestNoLifeScoreV2:
    def test_no_life_score_in_new_fields(self):
        artifact = PopulationPriorArtifact(**_valid_prior_artifact())
        assert not hasattr(artifact, "life_score")

    def test_no_life_score_in_model_card_new_fields(self):
        card = PopulationBaselineModelCard(**_valid_model_card())
        assert not hasattr(card, "life_score")
