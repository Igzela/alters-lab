"""Tests for the public-prior integration contract."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from alters_lab.schemas.public_prior_contract import (
    ALLOWED_OUTPUT_FIELDS,
    DISALLOWED_BEHAVIORS,
    REQUIRED_GUARDS,
    PublicPriorIntegrationContract,
)


def _valid_contract(**overrides):
    base = {
        "contract_id": "ppic_v1",
        "version": "1.0.0",
        "allowed_input_artifacts": ["PopulationPriorArtifact"],
    }
    base.update(overrides)
    return base


# --- Schema tests ---


class TestPublicPriorIntegrationContract:
    def test_valid_contract(self):
        contract = PublicPriorIntegrationContract(**_valid_contract())
        assert contract.contract_id == "ppic_v1"
        assert contract.version == "1.0.0"

    def test_defaults_populated(self):
        contract = PublicPriorIntegrationContract(**_valid_contract())
        assert len(contract.allowed_output_fields) > 0
        assert len(contract.required_guards) > 0
        assert len(contract.disallowed_behaviors) > 0

    def test_extra_fields_rejected(self):
        with pytest.raises(ValidationError, match="extra"):
            PublicPriorIntegrationContract(**_valid_contract(bogus_field="x"))

    def test_empty_lists_allowed(self):
        contract = PublicPriorIntegrationContract(
            **_valid_contract(
                allowed_output_fields=[],
                required_guards=[],
                disallowed_behaviors=[],
            )
        )
        assert contract.allowed_output_fields == []
        assert contract.required_guards == []
        assert contract.disallowed_behaviors == []


# --- Guard requirement tests ---


class TestRequiredGuards:
    def test_contract_requires_model_card_guard(self):
        assert "model_card_required" in REQUIRED_GUARDS

    def test_contract_requires_approved_for_route_b_guard(self):
        assert "approved_for_route_b_required" in REQUIRED_GUARDS

    def test_contract_requires_transfer_risk_guard(self):
        assert "transfer_risk_required" in REQUIRED_GUARDS

    def test_contract_requires_calibration_layer_guard(self):
        assert "calibration_layer_required" in REQUIRED_GUARDS

    def test_contract_requires_no_exact_probability_guard(self):
        assert "no_exact_probability_without_calibration" in REQUIRED_GUARDS

    def test_contract_requires_no_override_guard(self):
        assert "no_override_of_personal_evidence" in REQUIRED_GUARDS

    def test_contract_default_guards_match_constants(self):
        contract = PublicPriorIntegrationContract(**_valid_contract())
        assert set(contract.required_guards) == set(REQUIRED_GUARDS)


# --- Disallowed behavior tests ---


class TestDisallowedBehaviors:
    def test_contract_disallows_individual_destiny_prediction(self):
        assert "direct_individual_destiny_prediction" in DISALLOWED_BEHAVIORS

    def test_contract_disallows_hidden_model_output(self):
        assert "hidden_model_output" in DISALLOWED_BEHAVIORS

    def test_contract_disallows_exact_probability_without_model_card(self):
        assert "exact_probability_without_model_card" in DISALLOWED_BEHAVIORS

    def test_contract_disallows_bypass_forecast_snapshot(self):
        assert "bypass_forecast_snapshot" in DISALLOWED_BEHAVIORS

    def test_contract_disallows_bypass_external_evidence(self):
        assert "bypass_external_evidence" in DISALLOWED_BEHAVIORS

    def test_contract_disallows_bypass_forecast_evaluation(self):
        assert "bypass_forecast_evaluation" in DISALLOWED_BEHAVIORS

    def test_contract_disallows_overwrite_action_alignment(self):
        assert "overwrite_action_alignment" in DISALLOWED_BEHAVIORS

    def test_contract_default_behaviors_match_constants(self):
        contract = PublicPriorIntegrationContract(**_valid_contract())
        assert set(contract.disallowed_behaviors) == set(DISALLOWED_BEHAVIORS)


# --- Allowed output fields tests ---


class TestAllowedOutputFields:
    def test_prior_direction_allowed(self):
        assert "prior_direction" in ALLOWED_OUTPUT_FIELDS

    def test_probability_band_allowed(self):
        assert "probability_band" in ALLOWED_OUTPUT_FIELDS

    def test_transfer_risk_allowed(self):
        assert "transfer_risk" in ALLOWED_OUTPUT_FIELDS

    def test_confidence_allowed(self):
        assert "confidence" in ALLOWED_OUTPUT_FIELDS

    def test_explanation_allowed(self):
        assert "explanation" in ALLOWED_OUTPUT_FIELDS

    def test_life_score_not_allowed(self):
        assert "life_score" not in ALLOWED_OUTPUT_FIELDS

    def test_exact_probability_not_in_allowed_fields(self):
        assert "exact_probability" not in ALLOWED_OUTPUT_FIELDS
