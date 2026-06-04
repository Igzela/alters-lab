"""Promotion gate tests — verify strength levels and promotion rules."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from alters_lab.schemas.branch_forecast import (
    BranchForecastResult,
    DomainForecastPrediction,
    RouteBPopulationPrior,
)
from alters_lab.schemas.population_baseline import (
    PopulationBaselineModelCard,
    PopulationPriorArtifact,
)
from alters_lab.services.public_prior import _strength_level


# --- strength_level helper ---


class TestStrengthLevel:
    def test_calibrated_model_route_b_approved_is_strong(self):
        assert _strength_level("calibrated_model", "route_b_approved") == "strong_calibrated"

    def test_data_backed_baseline_route_b_approved_is_data_backed(self):
        assert _strength_level("data_backed_baseline", "route_b_approved") == "data_backed"

    def test_calibrated_model_lab_only_is_contextual(self):
        assert _strength_level("calibrated_model", "lab_only") == "contextual"

    def test_data_backed_baseline_lab_only_is_contextual(self):
        assert _strength_level("data_backed_baseline", "lab_only") == "contextual"

    def test_contextual_prior_is_contextual(self):
        assert _strength_level("contextual_prior", "lab_only") == "contextual"

    def test_none_is_none(self):
        assert _strength_level("none", "unapproved") == "none"


# --- MIDUS weak model cannot be strong_calibrated ---


class TestMIDUSPromotionGate:
    def test_weak_midus_model_cannot_be_promoted_to_strong_calibrated(self):
        """A calibrated_model with lab_only approval gets contextual strength, not strong."""
        card = PopulationBaselineModelCard(
            model_id="mc_test_weak",
            outcome_id="test_outcome",
            model_family="logistic_regression",
            training_status="trained",
            transfer_risk="medium",
            artifact_class="calibrated_model",
            approval_level="lab_only",
            calibration_metrics={"auc": 0.689, "brier_score": 0.226},
        )
        # lab_only → contextual, even if calibrated_model
        assert _strength_level(card.artifact_class, card.approval_level) == "contextual"

    def test_data_backed_baseline_still_counts_as_route_b_coverage(self):
        """A data_backed_baseline + route_b_approved is valid Route B coverage."""
        card = PopulationBaselineModelCard(
            model_id="mc_test_data_backed",
            outcome_id="test_outcome",
            model_family="logistic_regression",
            training_status="trained",
            transfer_risk="medium",
            artifact_class="data_backed_baseline",
            approval_level="route_b_approved",
        )
        assert card.approved_for_route_b is True
        assert _strength_level(card.artifact_class, card.approval_level) == "data_backed"

    def test_data_backed_artifact_valid(self):
        """A data_backed_baseline artifact with actual_data_used is valid."""
        artifact = PopulationPriorArtifact(
            artifact_id="pa_test",
            model_id="mc_test",
            generated_at="2026-06-03",
            domain="health",
            prior_type="baseline_table",
            prior_direction="favorable",
            confidence="medium",
            transfer_risk="medium",
            explanation="Test baseline",
            artifact_class="data_backed_baseline",
            actual_data_used=True,
        )
        assert artifact.artifact_class == "data_backed_baseline"
        assert artifact.actual_data_used is True


# --- NLSY97 promotion ---


class TestNLSY97PromotionGate:
    def test_nlsy97_model_can_be_promoted_with_brier_auc_improvement(self):
        """A calibrated_model with route_b_approved and good metrics gets strong_calibrated."""
        card = PopulationBaselineModelCard(
            model_id="mc_nlsy97_test",
            outcome_id="career_education_composite",
            model_family="logistic_regression",
            training_status="trained",
            transfer_risk="high",
            artifact_class="calibrated_model",
            approval_level="route_b_approved",
            calibration_metrics={"auc": 0.939, "brier_score": 0.0824, "n_train": 5680, "n_test": 1420},
        )
        assert card.approved_for_route_b is True
        assert _strength_level(card.artifact_class, card.approval_level) == "strong_calibrated"

    def test_calibrated_model_requires_metrics_for_route_b(self):
        """A calibrated_model + route_b_approved must have brier_score or auc."""
        with pytest.raises(ValidationError, match="brier_score or auc"):
            PopulationBaselineModelCard(
                model_id="mc_test_no_metrics",
                outcome_id="test_outcome",
                model_family="logistic_regression",
                training_status="trained",
                transfer_risk="medium",
                artifact_class="calibrated_model",
                approval_level="route_b_approved",
                calibration_metrics={},
            )


# --- Forecast strength_level ---


class TestForecastStrengthLevel:
    def test_domain_prediction_has_strength_level(self):
        """DomainForecastPrediction includes strength_level field."""
        dp = DomainForecastPrediction(
            domain="career_education",
            artifact_class="calibrated_model",
            strength_level="strong_calibrated",
        )
        assert dp.strength_level == "strong_calibrated"

    def test_domain_prediction_default_strength_is_none(self):
        """DomainForecastPrediction defaults strength_level to none."""
        dp = DomainForecastPrediction(domain="health")
        assert dp.strength_level == "none"

    def test_route_b_has_strength_level(self):
        """RouteBPopulationPrior includes strength_level field."""
        rb = RouteBPopulationPrior(
            available=True,
            prior_direction="favorable",
            transfer_risk="medium",
            evidence_strength="moderate",
            explanation="test",
            artifact_class="data_backed_baseline",
            strength_level="data_backed",
        )
        assert rb.strength_level == "data_backed"

    def test_no_life_score_in_strength_context(self):
        """BranchForecastResult schema does not contain life_score."""
        fields = set(BranchForecastResult.model_fields.keys())
        assert "life_score" not in fields
        assert "lifeScore" not in fields

    def test_no_fake_probability_in_strength_context(self):
        """BranchForecastResult schema does not contain exact probability."""
        fields = set(BranchForecastResult.model_fields.keys())
        assert "probability" not in fields
        assert "probability_of_success" not in fields
        assert "exact_probability" not in fields
