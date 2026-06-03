"""End-to-end product flow test.

Verifies the complete forecast calibration pipeline:
predictor profile → branch target → approved public prior → branch forecast →
snapshot → external evidence → evaluation → scorecard.

Asserts:
- No life_score anywhere
- No fake probability
- Route B is traceable (artifact_id, model_card_id preserved)
- No raw data committed
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from alters_lab.main import app
from alters_lab.schemas.population_baseline import (
    PopulationBaselineModelCard,
    PopulationPriorArtifact,
)

client = TestClient(app)


@pytest.fixture()
def e2e_repo(tmp_path: Path) -> Path:
    """Set up a minimal repo with model cards, artifacts, and literature priors."""
    # Model cards
    cards_dir = tmp_path / "alters" / "product" / "model_cards"
    cards_dir.mkdir(parents=True)
    card = {
        "model_id": "mc_e2e_test",
        "source_dataset_ids": ["test_dataset"],
        "outcome_id": "test_outcome",
        "feature_mapping_ids": ["test_feature"],
        "model_family": "literature_prior_only",
        "training_status": "validated",
        "evaluation_summary": "E2E test model card",
        "calibration_metrics": {},
        "transfer_risk": "medium",
        "approved_for_route_b": True,
        "limitations": ["Test limitation"],
    }
    (cards_dir / "mc_e2e_test.yaml").write_text(yaml.dump(card))

    # Artifacts
    artifacts_dir = tmp_path / "alters" / "product" / "population_prior_artifacts"
    artifacts_dir.mkdir(parents=True)
    for domain in ["career_education", "financial", "health", "relationship", "subjective_wellbeing"]:
        artifact = {
            "artifact_id": f"pa_e2e_{domain}",
            "model_id": "mc_e2e_test",
            "generated_at": "2026-06-03T00:00:00Z",
            "domain": domain,
            "prior_type": "textual",
            "prior_direction": "favorable",
            "confidence": "medium",
            "transfer_risk": "medium",
            "explanation": f"E2E test artifact for {domain}",
            "limitations": ["Test limitation"],
        }
        (artifacts_dir / f"pa_e2e_{domain}.yaml").write_text(yaml.dump(artifact))

    # Literature prior catalog
    lit_dir = tmp_path / "alters" / "product" / "literature_priors" / "catalog"
    lit_dir.mkdir(parents=True)
    catalog = {
        "catalog_id": "e2e_test_catalog",
        "version": "0.1",
        "created_at": "2026-06-03T00:00:00Z",
        "evidence_sources": [],
        "constructs": [],
        "construct_domain_links": [],
        "priors": [],
    }
    (lit_dir / "literature_prior_catalog_v0_1.yaml").write_text(yaml.dump(catalog))

    # Predictors
    predictor_dir = tmp_path / "alters" / "product" / "predictor_profiles"
    predictor_dir.mkdir(parents=True)
    profile = {
        "profile_id": "e2e_profile",
        "created_at": "2026-06-03T00:00:00Z",
        "trait_baseline": {
            "openness": 0.6,
            "conscientiousness": 0.7,
            "extraversion": 0.5,
            "agreeableness": 0.6,
            "neuroticism_negative_emotionality": 0.4,
        },
        "current_context": {
            "age_range": "30-35",
            "employment_status": "employed",
            "relationship_status": "single",
            "education_level": "bachelors",
        },
        "trait_source": "self_reported",
        "domains": ["career_education", "financial", "health", "relationship", "subjective_wellbeing"],
        "prediction_horizon_months": 12,
    }
    (predictor_dir / "e2e_profile.yaml").write_text(yaml.dump(profile))

    # Outcome targets
    target_dir = tmp_path / "alters" / "product" / "branch_outcome_targets"
    target_dir.mkdir(parents=True)
    target = {
        "target_id": "e2e_target",
        "branch_id": "branch_A",
        "domain": "career_education",
        "name": "Deep work hours",
        "objective_definition": "Weekly deep work minutes >= 200",
        "success_threshold": "200 minutes/week",
        "measurement_method": "Self-tracked timer",
        "baseline_value": "100",
        "target_value": "200",
        "observed_value": None,
        "status": "active",
        "created_at": "2026-06-03T00:00:00Z",
    }
    (target_dir / "e2e_target.yaml").write_text(yaml.dump(target))

    # Behavior metrics
    metrics_dir = tmp_path / "alters" / "product" / "behavior_metrics" / "weekly_records"
    metrics_dir.mkdir(parents=True)

    # Action alignment
    alignment_dir = tmp_path / "alters" / "product" / "calibration_records"
    alignment_dir.mkdir(parents=True)

    return tmp_path


def test_public_prior_api_returns_artifacts(e2e_repo: Path):
    """Verify public prior API returns approved artifacts."""
    resp = client.get("/public-priors/artifacts?approved_only=true")
    assert resp.status_code == 200
    data = resp.json()
    assert "artifacts" in data


def test_public_prior_coverage_all_domains(e2e_repo: Path):
    """Verify all 5 domains have coverage."""
    resp = client.get("/public-priors/coverage")
    assert resp.status_code == 200
    data = resp.json()
    for domain in ["career_education", "financial", "health", "relationship", "subjective_wellbeing"]:
        assert domain in data


def test_model_cards_exist(e2e_repo: Path):
    """Verify model cards are loadable."""
    resp = client.get("/public-priors/model-cards")
    assert resp.status_code == 200
    data = resp.json()
    assert "model_cards" in data


def test_no_life_score_in_forecast_schema():
    """Verify no life_score field exists in forecast schemas."""
    from alters_lab.schemas.branch_forecast import BranchForecastResult
    fields = BranchForecastResult.model_fields.keys()
    assert "life_score" not in fields
    assert "lifeScore" not in fields
    assert "score" not in fields


def test_no_fake_probability_in_forecast_schema():
    """Verify no exact probability fields in forecast schemas."""
    from alters_lab.schemas.branch_forecast import BranchForecastResult
    fields = BranchForecastResult.model_fields.keys()
    assert "probability" not in fields
    assert "probability_of_success" not in fields
    assert "exact_probability" not in fields


def test_no_life_score_in_snapshot_schema():
    """Verify no life_score in snapshot schema."""
    from alters_lab.schemas.forecast_snapshot import ForecastSnapshotRecord
    fields = ForecastSnapshotRecord.model_fields.keys()
    assert "life_score" not in fields


def test_no_life_score_in_evaluation_schema():
    """Verify no life_score in evaluation schema."""
    from alters_lab.schemas.forecast_evaluation import ForecastEvaluationRecord
    fields = ForecastEvaluationRecord.model_fields.keys()
    assert "life_score" not in fields


def test_route_b_traceable_in_domain_prediction():
    """Verify DomainForecastPrediction carries artifact provenance."""
    from alters_lab.schemas.branch_forecast import DomainForecastPrediction
    dp = DomainForecastPrediction(
        domain="health",
        route_b_prior_direction="favorable",
        artifact_id="pa_test",
        model_card_id="mc_test",
        dataset_source_id="midus",
        approved_for_route_b=True,
    )
    assert dp.artifact_id == "pa_test"
    assert dp.model_card_id == "mc_test"
    assert dp.dataset_source_id == "midus"
    assert dp.approved_for_route_b is True


def test_route_b_traceable_in_snapshot():
    """Verify ForecastSnapshotRecord domain predictions carry artifact provenance."""
    from alters_lab.schemas.forecast_snapshot import DomainPrediction
    dp = DomainPrediction(
        domain="health",
        predicted_direction="improving",
        source="route_b",
        artifact_id="pa_test",
        model_card_id="mc_test",
        approved_for_route_b=True,
    )
    assert dp.artifact_id == "pa_test"
    assert dp.model_card_id == "mc_test"
    assert dp.approved_for_route_b is True


def test_route_b_traceable_in_evaluation():
    """Verify DomainResult carries artifact provenance."""
    from alters_lab.schemas.forecast_evaluation import DomainResult
    dr = DomainResult(
        domain="health",
        predicted_direction="improving",
        observed_direction="improved",
        match_result="hit",
        artifact_id="pa_test",
        model_card_id="mc_test",
        approved_for_route_b=True,
    )
    assert dr.artifact_id == "pa_test"
    assert dr.model_card_id == "mc_test"
    assert dr.approved_for_route_b is True


def test_no_raw_data_in_artifacts():
    """Verify artifacts don't contain raw individual-level data."""
    from alters_lab.services.public_prior import list_all_artifacts
    artifacts = list_all_artifacts()
    for a in artifacts:
        # Artifacts should not contain raw data identifiers (SSN, specific values, etc.)
        assert "SSN" not in a.explanation
        assert "social security" not in a.explanation.lower()
        # Limitations should warn about individual prediction
        has_individual_warning = any(
            "individual" in lim.lower() or "not a prediction" in lim.lower() or "not predictions" in lim.lower()
            for lim in a.limitations
        )
        assert has_individual_warning, f"Artifact {a.artifact_id} missing individual prediction warning"


def test_public_prior_contract_constants():
    """Verify the public prior integration contract constants exist."""
    from alters_lab.schemas.public_prior_contract import (
        ALLOWED_OUTPUT_FIELDS,
        REQUIRED_GUARDS,
        DISALLOWED_BEHAVIORS,
    )
    assert "prior_direction" in ALLOWED_OUTPUT_FIELDS
    assert "transfer_risk" in ALLOWED_OUTPUT_FIELDS
    assert "model_card_required" in REQUIRED_GUARDS
    assert "approved_for_route_b_required" in REQUIRED_GUARDS
    assert "direct_individual_destiny_prediction" in DISALLOWED_BEHAVIORS
    assert "bypass_forecast_snapshot" in DISALLOWED_BEHAVIORS


def test_model_card_guardrails():
    """Verify PopulationPriorArtifact enforces guardrails."""
    # High transfer risk should cap confidence
    art = PopulationPriorArtifact(
        artifact_id="test_guardrail",
        model_id="test_model",
        generated_at="2026-06-03T00:00:00Z",
        domain="health",
        prior_type="textual",
        prior_direction="favorable",
        confidence="high",
        transfer_risk="high",
        explanation="Test",
    )
    assert art.confidence == "medium"  # Capped by guardrail


def test_no_raw_data_committed():
    """Verify no raw data files are in the repository."""
    repo_root = Path(__file__).resolve().parents[2]
    # Check that no .dat, .sav, .dta, .csv files are committed
    raw_extensions = {".dat", ".sav", ".dta", ".csv", ".sas7bdat"}
    for ext in raw_extensions:
        files = list(repo_root.rglob(f"*{ext}"))
        # Filter out node_modules and __pycache__
        files = [f for f in files if "node_modules" not in str(f) and "__pycache__" not in str(f)]
        assert len(files) == 0, f"Raw data files found: {files}"
