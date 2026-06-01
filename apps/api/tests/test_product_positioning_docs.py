"""Doc smoke tests — validate required and forbidden phrases in product positioning docs."""

from __future__ import annotations

from pathlib import Path

import pytest

DOCS_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "docs"

POSITIONING_PATH = DOCS_ROOT / "PRODUCT_POSITIONING.md"
VALIDATION_PATH = DOCS_ROOT / "VALIDATION_STANDARD.md"


@pytest.fixture(scope="module")
def positioning_text() -> str:
    return POSITIONING_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def validation_text() -> str:
    return VALIDATION_PATH.read_text(encoding="utf-8")


# --- Required phrases ---


class TestRequiredPhrases:
    def test_public_prior_personal_calibration(self, positioning_text):
        assert "public-prior + personal-calibration" in positioning_text

    def test_calibration_first(self, positioning_text):
        assert "calibration-first" in positioning_text

    def test_forecast_snapshot(self, positioning_text):
        assert "forecast snapshot" in positioning_text.lower()

    def test_external_evidence(self, positioning_text):
        assert "external evidence" in positioning_text.lower()

    def test_hit_miss_partial_unknown(self, positioning_text):
        assert "hit/miss/partial/unknown" in positioning_text

    def test_transfer_risk(self, positioning_text):
        assert "transfer risk" in positioning_text.lower()

    def test_not_trained_ml_model(self, positioning_text):
        assert "not a trained ml model" in positioning_text.lower()

    def test_no_life_score(self, positioning_text):
        assert "no life_score" in positioning_text

    def test_unknown_remains_unknown(self, positioning_text):
        assert "unknown remains unknown" in positioning_text.lower()


# --- Forbidden phrases ---


class TestForbiddenPhrases:
    def test_no_predicts_your_destiny(self, positioning_text):
        assert "predicts your destiny" not in positioning_text.lower()

    def test_no_guaranteed_prediction(self, positioning_text):
        assert "guaranteed prediction" not in positioning_text.lower()

    def test_no_exact_personal_probability(self, positioning_text):
        assert "exact personal probability" not in positioning_text.lower()

    def test_no_life_score_as_feature(self, positioning_text):
        assert "life_score" not in positioning_text.replace("no life_score", "")

    def test_no_trained_ffc_in_production(self, positioning_text):
        assert "trained FFC model in production" not in positioning_text

    def test_no_trained_nlsy_in_production(self, positioning_text):
        assert "trained NLSY model in production" not in positioning_text


# --- Validation standard tests ---


class TestValidationStandardPhrases:
    def test_gate_1_public_data_traceability(self, validation_text):
        assert "Public Data Traceability" in validation_text or "public data traceability" in validation_text

    def test_gate_2_model_calibration(self, validation_text):
        assert "Model Calibration" in validation_text

    def test_gate_3_transfer_risk(self, validation_text):
        assert "Transfer Risk" in validation_text

    def test_gate_4_hybrid_integration(self, validation_text):
        assert "Hybrid Integration" in validation_text

    def test_gate_5_no_false_precision(self, validation_text):
        assert "No False Precision" in validation_text

    def test_gate_6_calibration_module_preserved(self, validation_text):
        assert "Calibration Module Preserved" in validation_text or "calibration module preserved" in validation_text
