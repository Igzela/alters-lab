"""Tests for public prior service and API."""

from __future__ import annotations

import pytest
import yaml
from pathlib import Path

from alters_lab.schemas.population_baseline import (
    PopulationBaselineModelCard,
    PopulationPriorArtifact,
)
from alters_lab.services.public_prior import (
    get_artifact,
    get_domain_coverage,
    get_model_card,
    list_all_artifacts,
    list_approved_artifacts,
    list_artifacts_for_domain,
    list_model_cards,
)


@pytest.fixture()
def prior_repo(tmp_path: Path) -> Path:
    """Create a temporary repo with model cards and artifacts."""
    cards_dir = tmp_path / "alters" / "product" / "model_cards"
    cards_dir.mkdir(parents=True)
    artifacts_dir = tmp_path / "alters" / "product" / "population_prior_artifacts"
    artifacts_dir.mkdir(parents=True)

    # Approved model card
    card = {
        "model_id": "mc_test_approved",
        "source_dataset_ids": ["test_dataset"],
        "outcome_id": "test_outcome",
        "feature_mapping_ids": ["test_feature"],
        "model_family": "literature_prior_only",
        "training_status": "validated",
        "evaluation_summary": "Test model card",
        "calibration_metrics": {},
        "transfer_risk": "medium",
        "approved_for_route_b": True,
        "limitations": ["Test limitation"],
    }
    (cards_dir / "mc_test_approved.yaml").write_text(yaml.dump(card))

    # Unapproved model card
    card_unapproved = {
        "model_id": "mc_test_unapproved",
        "source_dataset_ids": ["test_dataset"],
        "outcome_id": "test_outcome",
        "feature_mapping_ids": [],
        "model_family": "baseline_table",
        "training_status": "not_trained",
        "transfer_risk": "high",
        "approved_for_route_b": False,
    }
    (cards_dir / "mc_test_unapproved.yaml").write_text(yaml.dump(card_unapproved))

    # Approved artifact
    artifact = {
        "artifact_id": "pa_test_approved",
        "model_id": "mc_test_approved",
        "generated_at": "2026-06-03T00:00:00Z",
        "domain": "health",
        "prior_type": "textual",
        "prior_direction": "favorable",
        "confidence": "medium",
        "transfer_risk": "medium",
        "explanation": "Test artifact",
        "limitations": ["Test limitation"],
    }
    (artifacts_dir / "pa_test_approved.yaml").write_text(yaml.dump(artifact))

    # Artifact linked to unapproved model
    artifact_unapproved = {
        "artifact_id": "pa_test_unapproved",
        "model_id": "mc_test_unapproved",
        "generated_at": "2026-06-03T00:00:00Z",
        "domain": "financial",
        "prior_type": "textual",
        "prior_direction": "unknown",
        "confidence": "low",
        "transfer_risk": "high",
        "explanation": "Unapproved artifact",
    }
    (artifacts_dir / "pa_test_unapproved.yaml").write_text(yaml.dump(artifact_unapproved))

    # Second approved artifact for a different domain
    artifact2 = {
        "artifact_id": "pa_test_career",
        "model_id": "mc_test_approved",
        "generated_at": "2026-06-03T00:00:00Z",
        "domain": "career_education",
        "prior_type": "textual",
        "prior_direction": "favorable",
        "confidence": "medium",
        "transfer_risk": "medium",
        "explanation": "Career test artifact",
    }
    (artifacts_dir / "pa_test_career.yaml").write_text(yaml.dump(artifact2))

    return tmp_path


def test_list_model_cards(prior_repo: Path):
    cards = list_model_cards(repo_root=prior_repo)
    assert len(cards) == 2
    ids = {c.model_id for c in cards}
    assert "mc_test_approved" in ids
    assert "mc_test_unapproved" in ids


def test_get_model_card(prior_repo: Path):
    card = get_model_card("mc_test_approved", repo_root=prior_repo)
    assert card.model_id == "mc_test_approved"
    assert card.approved_for_route_b is True
    assert card.model_family == "literature_prior_only"


def test_get_model_card_not_found(prior_repo: Path):
    with pytest.raises(FileNotFoundError):
        get_model_card("nonexistent", repo_root=prior_repo)


def test_list_approved_artifacts(prior_repo: Path):
    artifacts = list_approved_artifacts(repo_root=prior_repo)
    assert len(artifacts) == 2
    ids = {a.artifact_id for a in artifacts}
    assert "pa_test_approved" in ids
    assert "pa_test_career" in ids
    # Unapproved artifact should not be included
    assert "pa_test_unapproved" not in ids


def test_list_artifacts_for_domain(prior_repo: Path):
    health = list_artifacts_for_domain("health", repo_root=prior_repo)
    assert len(health) == 1
    assert health[0].artifact_id == "pa_test_approved"

    career = list_artifacts_for_domain("career_education", repo_root=prior_repo)
    assert len(career) == 1
    assert career[0].artifact_id == "pa_test_career"

    empty = list_artifacts_for_domain("relationship", repo_root=prior_repo)
    assert len(empty) == 0


def test_list_all_artifacts(prior_repo: Path):
    all_arts = list_all_artifacts(repo_root=prior_repo)
    assert len(all_arts) == 3


def test_get_artifact(prior_repo: Path):
    art = get_artifact("pa_test_approved", repo_root=prior_repo)
    assert art.artifact_id == "pa_test_approved"
    assert art.domain == "health"


def test_get_artifact_not_found(prior_repo: Path):
    with pytest.raises(FileNotFoundError):
        get_artifact("nonexistent", repo_root=prior_repo)


def test_get_domain_coverage(prior_repo: Path):
    coverage = get_domain_coverage(repo_root=prior_repo)
    assert len(coverage) == 5

    # Health should have coverage
    assert coverage["health"]["has_approved_artifact"] is True
    assert coverage["health"]["artifact_count"] == 1

    # Career should have coverage
    assert coverage["career_education"]["has_approved_artifact"] is True

    # Relationship should have no coverage
    assert coverage["relationship"]["has_approved_artifact"] is False
    assert coverage["relationship"]["artifact_count"] == 0


def test_domain_coverage_best_risk(prior_repo: Path):
    coverage = get_domain_coverage(repo_root=prior_repo)
    # Health has medium transfer risk
    assert coverage["health"]["best_transfer_risk"] == "medium"
    assert coverage["health"]["best_confidence"] == "medium"


# --- API tests ---

from fastapi.testclient import TestClient
from alters_lab.main import app

client = TestClient(app)


def test_api_list_artifacts_approved():
    resp = client.get("/public-priors/artifacts?approved_only=true")
    assert resp.status_code == 200
    data = resp.json()
    assert "artifacts" in data


def test_api_list_artifacts_all():
    resp = client.get("/public-priors/artifacts?approved_only=false")
    assert resp.status_code == 200
    data = resp.json()
    assert "artifacts" in data


def test_api_list_model_cards():
    resp = client.get("/public-priors/model-cards")
    assert resp.status_code == 200
    data = resp.json()
    assert "model_cards" in data


def test_api_coverage():
    resp = client.get("/public-priors/coverage")
    assert resp.status_code == 200
    data = resp.json()
    assert "career_education" in data
    assert "financial" in data
    assert "health" in data
    assert "relationship" in data
    assert "subjective_wellbeing" in data


def test_api_artifact_not_found():
    resp = client.get("/public-priors/artifacts/nonexistent_id")
    assert resp.status_code == 404


def test_api_model_card_not_found():
    resp = client.get("/public-priors/model-cards/nonexistent_id")
    assert resp.status_code == 404
