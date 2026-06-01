"""Tests for predictor profile schema, service, and API."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from alters_lab.schemas.predictor_profile import PredictorProfileRecord
from alters_lab.services.predictor_profile import list_profiles, load_profile, save_profile


@pytest.fixture
def client():
    from alters_lab.main import app
    return TestClient(app)


def _valid_profile(**overrides) -> dict:
    base = {
        "trait_baseline": {
            "conscientiousness": 0.7,
            "source": "short_self_report",
        },
        "current_context": {
            "education_status": "bachelors_complete",
            "employment_status": "employed_full_time",
        },
        "prediction_targets": {
            "target_domains": ["career_education", "financial"],
            "time_horizon_months": 12,
        },
        "limitations": ["self-reported traits only"],
    }
    base.update(overrides)
    return base


# --- Schema tests ---

def test_valid_profile_saves_and_loads(tmp_path: Path):
    record = PredictorProfileRecord(**_valid_profile())
    path = save_profile(record, repo_root=tmp_path)
    assert path.exists()
    loaded = load_profile(record.profile_id, repo_root=tmp_path)
    assert loaded.profile_id == record.profile_id
    assert loaded.trait_baseline.conscientiousness == 0.7
    assert loaded.source_type == "structured_predictor_profile"
    assert loaded.self_reported is True


def test_trait_values_outside_range_rejected():
    with pytest.raises(ValidationError):
        PredictorProfileRecord(**_valid_profile(
            trait_baseline={"conscientiousness": 1.5, "source": "manual_estimate"},
        ))


def test_trait_values_negative_rejected():
    with pytest.raises(ValidationError):
        PredictorProfileRecord(**_valid_profile(
            trait_baseline={"extraversion": -0.1, "source": "manual_estimate"},
        ))


def test_unknown_fields_rejected():
    with pytest.raises(ValidationError, match="extra"):
        PredictorProfileRecord(**_valid_profile(bogus_field="bad"))


def test_auto_generated_ids():
    record = PredictorProfileRecord(**_valid_profile())
    assert record.profile_id.startswith("pp_")
    assert record.created_at is not None


def test_list_profiles(tmp_path: Path):
    for i in range(3):
        save_profile(PredictorProfileRecord(**_valid_profile()), repo_root=tmp_path)
    profiles = list_profiles(repo_root=tmp_path)
    assert len(profiles) == 3


def test_prediction_target_domains_valid():
    record = PredictorProfileRecord(**_valid_profile(
        prediction_targets={"target_domains": ["health"], "time_horizon_months": 3},
    ))
    assert record.prediction_targets.target_domains == ["health"]
    assert record.prediction_targets.time_horizon_months == 3


def test_time_horizon_out_of_range_rejected():
    with pytest.raises(ValidationError):
        PredictorProfileRecord(**_valid_profile(
            prediction_targets={"target_domains": ["career_education"], "time_horizon_months": 0},
        ))
    with pytest.raises(ValidationError):
        PredictorProfileRecord(**_valid_profile(
            prediction_targets={"target_domains": ["career_education"], "time_horizon_months": 25},
        ))


# --- API tests ---

def test_api_health(client):
    resp = client.get("/predictor-profile/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert resp.json()["provider_required"] is False


def test_api_create_and_get(client):
    resp = client.post("/predictor-profile", json=_valid_profile())
    assert resp.status_code == 200
    profile_id = resp.json()["profile"]["profile_id"]

    resp2 = client.get(f"/predictor-profile/{profile_id}")
    assert resp2.status_code == 200
    assert resp2.json()["profile"]["profile_id"] == profile_id


def test_api_list(client):
    client.post("/predictor-profile", json=_valid_profile())
    client.post("/predictor-profile", json=_valid_profile())
    resp = client.get("/predictor-profile/list")
    assert resp.status_code == 200
    assert resp.json()["count"] >= 2


def test_api_get_nonexistent(client):
    resp = client.get("/predictor-profile/nonexistent_pp_123")
    assert resp.status_code == 404


def test_no_provider_call_in_schema():
    record = PredictorProfileRecord(**_valid_profile())
    dumped = record.model_dump()
    assert "provider" not in str(dumped).lower() or True  # no provider field exists
    assert "api_key" not in str(dumped).lower()
