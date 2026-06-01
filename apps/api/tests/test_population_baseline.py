"""Tests for population baseline schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from alters_lab.schemas.population_baseline import (
    CalibrationMetrics,
    PopulationBaselineModelCard,
    PopulationPriorArtifact,
    PublicDatasetSource,
    PublicFeatureMapping,
    PublicOutcomeDefinition,
)


# --- Helper factories ---


def _valid_dataset_source(**overrides):
    base = {
        "source_id": "nlsy79",
        "label": "National Longitudinal Survey of Youth 1979",
        "source_type": "longitudinal_dataset",
        "population_description": "12,686 youth aged 14-22 in 1979",
        "time_horizon": "40+ years",
        "available_domains": ["career_education", "financial"],
        "transfer_risk": "high",
        "allowed_use": "research_only",
    }
    base.update(overrides)
    return base


def _valid_outcome_def(**overrides):
    base = {
        "outcome_id": "income_above_median",
        "domain": "career_education",
        "label": "Income Above National Median",
        "definition": "Average household income over 5 years exceeds national median",
        "measurement_type": "binary",
    }
    base.update(overrides)
    return base


def _valid_feature_mapping(**overrides):
    base = {
        "feature_id": "conscientiousness",
        "construct_id": "big5_conscientiousness",
        "label": "Conscientiousness",
        "expected_direction": "positive",
        "transfer_risk": "high",
    }
    base.update(overrides)
    return base


def _valid_model_card(**overrides):
    base = {
        "model_id": "nlsy79_income_logistic",
        "outcome_id": "income_above_median",
        "model_family": "logistic_regression",
        "transfer_risk": "high",
    }
    base.update(overrides)
    return base


def _valid_prior_artifact(**overrides):
    base = {
        "artifact_id": "art_001",
        "model_id": "nlsy79_income_logistic",
        "generated_at": "2026-01-01T00:00:00Z",
        "domain": "career_education",
        "prior_type": "textual",
        "prior_direction": "favorable",
        "confidence": "medium",
        "transfer_risk": "high",
        "explanation": "Higher conscientiousness correlates with higher income",
    }
    base.update(overrides)
    return base


# --- Schema tests ---


class TestPublicDatasetSource:
    def test_valid_source(self):
        source = PublicDatasetSource(**_valid_dataset_source())
        assert source.source_id == "nlsy79"
        assert source.source_type == "longitudinal_dataset"
        assert source.transfer_risk == "high"

    def test_optional_fields_default(self):
        source = PublicDatasetSource(**_valid_dataset_source())
        assert source.access_url is None
        assert source.access_notes == ""
        assert source.notes == ""

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="extra"):
            PublicDatasetSource(**_valid_dataset_source(bogus_field="x"))

    def test_invalid_source_type(self):
        with pytest.raises(ValidationError):
            PublicDatasetSource(**_valid_dataset_source(source_type="invalid_type"))

    def test_invalid_transfer_risk(self):
        with pytest.raises(ValidationError):
            PublicDatasetSource(**_valid_dataset_source(transfer_risk="extreme"))


class TestPublicOutcomeDefinition:
    def test_valid_outcome(self):
        outcome = PublicOutcomeDefinition(**_valid_outcome_def())
        assert outcome.outcome_id == "income_above_median"
        assert outcome.measurement_type == "binary"

    def test_optional_fields_default(self):
        outcome = PublicOutcomeDefinition(**_valid_outcome_def())
        assert outcome.time_horizon_months is None
        assert outcome.dataset_source_ids == []
        assert outcome.limitations == []

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="extra"):
            PublicOutcomeDefinition(**_valid_outcome_def(bogus_field="x"))

    def test_invalid_measurement_type(self):
        with pytest.raises(ValidationError):
            PublicOutcomeDefinition(**_valid_outcome_def(measurement_type="invalid"))


class TestPublicFeatureMapping:
    def test_valid_mapping(self):
        mapping = PublicFeatureMapping(**_valid_feature_mapping())
        assert mapping.feature_id == "conscientiousness"
        assert mapping.expected_direction == "positive"

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="extra"):
            PublicFeatureMapping(**_valid_feature_mapping(bogus_field="x"))

    def test_invalid_expected_direction(self):
        with pytest.raises(ValidationError):
            PublicFeatureMapping(**_valid_feature_mapping(expected_direction="up"))


class TestCalibrationMetrics:
    def test_valid_metrics(self):
        metrics = CalibrationMetrics(brier_score=0.15, auc=0.75)
        assert metrics.brier_score == 0.15
        assert metrics.auc == 0.75

    def test_all_none_by_default(self):
        metrics = CalibrationMetrics()
        assert metrics.brier_score is None
        assert metrics.calibration_slope is None
        assert metrics.calibration_intercept is None
        assert metrics.auc is None
        assert metrics.r2 is None

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="extra"):
            CalibrationMetrics(brier_score=0.15, bogus_field="x")


class TestPopulationBaselineModelCard:
    def test_valid_card(self):
        card = PopulationBaselineModelCard(**_valid_model_card())
        assert card.model_id == "nlsy79_income_logistic"
        assert card.approved_for_route_b is False

    def test_approved_for_route_b_defaults_false(self):
        card = PopulationBaselineModelCard(**_valid_model_card())
        assert card.approved_for_route_b is False

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="extra"):
            PopulationBaselineModelCard(**_valid_model_card(bogus_field="x"))

    def test_invalid_model_family(self):
        with pytest.raises(ValidationError):
            PopulationBaselineModelCard(
                **_valid_model_card(model_family="deep_neural_network")
            )

    def test_invalid_training_status(self):
        with pytest.raises(ValidationError):
            PopulationBaselineModelCard(
                **_valid_model_card(training_status="deployed")
            )


class TestPopulationPriorArtifact:
    def test_valid_textual_artifact(self):
        artifact = PopulationPriorArtifact(**_valid_prior_artifact())
        assert artifact.prior_type == "textual"
        assert artifact.confidence == "medium"

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="extra"):
            PopulationPriorArtifact(**_valid_prior_artifact(bogus_field="x"))

    def test_high_transfer_risk_caps_confidence(self):
        """High transfer risk should cap confidence from high to medium."""
        artifact = PopulationPriorArtifact(
            **_valid_prior_artifact(confidence="high", transfer_risk="high")
        )
        assert artifact.confidence == "medium"

    def test_low_transfer_risk_allows_high_confidence(self):
        artifact = PopulationPriorArtifact(
            **_valid_prior_artifact(confidence="high", transfer_risk="low")
        )
        assert artifact.confidence == "high"

    def test_medium_transfer_risk_allows_high_confidence(self):
        artifact = PopulationPriorArtifact(
            **_valid_prior_artifact(confidence="high", transfer_risk="medium")
        )
        assert artifact.confidence == "high"

    def test_invalid_prior_type(self):
        with pytest.raises(ValidationError):
            PopulationPriorArtifact(**_valid_prior_artifact(prior_type="exact_prob"))

    def test_invalid_prior_direction(self):
        with pytest.raises(ValidationError):
            PopulationPriorArtifact(**_valid_prior_artifact(prior_direction="good"))

    def test_no_life_score_field(self):
        """life_score must not exist anywhere in the schema."""
        artifact = PopulationPriorArtifact(**_valid_prior_artifact())
        assert not hasattr(artifact, "life_score")
        assert "life_score" not in PopulationPriorArtifact.model_fields


class TestNoLifeScoreAnywhere:
    """Ensure life_score does not appear in any population baseline schema."""

    def test_no_life_score_in_dataset_source(self):
        assert "life_score" not in PublicDatasetSource.model_fields

    def test_no_life_score_in_outcome_def(self):
        assert "life_score" not in PublicOutcomeDefinition.model_fields

    def test_no_life_score_in_feature_mapping(self):
        assert "life_score" not in PublicFeatureMapping.model_fields

    def test_no_life_score_in_model_card(self):
        assert "life_score" not in PopulationBaselineModelCard.model_fields

    def test_no_life_score_in_prior_artifact(self):
        assert "life_score" not in PopulationPriorArtifact.model_fields

    def test_no_life_score_in_calibration_metrics(self):
        assert "life_score" not in CalibrationMetrics.model_fields
