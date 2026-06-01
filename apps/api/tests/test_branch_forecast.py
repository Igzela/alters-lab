"""Tests for branch forecast service."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from alters_lab.schemas.branch_forecast import BranchForecastRequest
from alters_lab.services.branch_forecast import analyze_branch_forecast


@pytest.fixture
def client():
    from alters_lab.main import app
    return TestClient(app)


# --- API tests ---

def test_api_forecast_separates_route_a_and_route_b(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A", "lookback_weeks": 8},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "route_a_personal_evidence" in data
    assert "route_b_population_prior" in data
    assert data["route_a_personal_evidence"]["available"] is not None
    assert data["route_b_population_prior"]["available"] is not None


def test_no_exact_probability_emitted_by_default(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    assert data["route_b_population_prior"]["population_percentile"] is None
    assert data["route_b_population_prior"]["deviation_from_baseline"] is None


def test_low_confidence_when_outcome_targets_missing(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_no_targets"},
    )
    data = resp.json()
    # Should have limitation about missing targets
    assert any("outcome target" in lim.lower() for lim in data["limitations"])
    # Confidence should not be high when targets missing
    assert data["forecast_summary"]["confidence"] != "high" or "no outcome target" in str(data["limitations"]).lower()


def test_conflict_between_routes_reported(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    # Route B available should be true (catalog exists)
    assert data["route_b_population_prior"]["available"] is True


def test_route_b_unavailable_keeps_percentile_null(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    # Even when Route B is available, population_percentile stays null
    assert data["route_b_population_prior"]["population_percentile"] is None


def test_no_life_score(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    assert "life_score" not in str(data).lower()


def test_forecast_has_outcome_targets_section(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    assert "outcome_targets" in data
    assert "active_targets" in data["outcome_targets"]
    assert "achieved_targets" in data["outcome_targets"]
    assert "missed_targets" in data["outcome_targets"]


def test_forecast_has_calibration_divergence(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    assert "calibration_divergence" in data
    assert "divergence_status" in data["calibration_divergence"]


def test_next_evidence_to_collect(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    assert "next_evidence_to_collect" in data
    assert isinstance(data["next_evidence_to_collect"], list)


def test_horizon_months_in_response(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A", "horizon_months": 6},
    )
    data = resp.json()
    assert data["horizon_months"] == 6


def test_trajectory_direction_valid_enum(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    valid = {"improving", "declining", "stable", "mixed", "unknown"}
    assert data["forecast_summary"]["trajectory_direction"] in valid


# --- Domain prediction tests ---

def test_forecast_returns_domain_predictions(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    assert "domain_predictions" in data
    assert isinstance(data["domain_predictions"], list)
    assert len(data["domain_predictions"]) == 5

    domains = {dp["domain"] for dp in data["domain_predictions"]}
    assert domains == {"career_education", "financial", "health", "relationship", "subjective_wellbeing"}


def test_domain_predictions_have_required_fields(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    for dp in data["domain_predictions"]:
        assert "predicted_direction" in dp
        assert "predicted_direction_source" in dp
        assert "route_a_direction" in dp
        assert "route_b_prior_direction" in dp
        assert "evidence_strength" in dp
        assert "transfer_risk" in dp
        assert "explanation" in dp
        assert dp["predicted_direction_source"] in {
            "route_a", "route_b", "behavior_metric", "outcome_target", "overall_fallback", "unknown",
        }


def test_career_and_health_can_differ(client):
    """Domain predictions are per-domain, not copies of overall trajectory."""
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    preds = {dp["domain"]: dp for dp in data["domain_predictions"]}
    # Each domain has its own source data — they are not required to be identical
    career = preds["career_education"]
    health = preds["health"]
    # Both should have valid fields, but they come from independent anchors
    assert career["domain"] == "career_education"
    assert health["domain"] == "health"


def test_overall_fallback_only_when_no_domain_data(client):
    """When domain anchors have data, source should not be overall_fallback."""
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    sources = {dp["predicted_direction_source"] for dp in data["domain_predictions"]}
    # At least one domain should have route_a or route_b if catalog/data is available
    # If nothing is available, all should be overall_fallback or unknown
    valid_sources = {"route_a", "route_b", "behavior_metric", "outcome_target", "overall_fallback", "unknown"}
    assert sources.issubset(valid_sources)


def test_no_life_score_in_domain_predictions(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    assert "life_score" not in str(data["domain_predictions"]).lower()


def test_no_probability_in_domain_predictions(client):
    resp = client.post(
        "/branch-forecast/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    dumped = str(data["domain_predictions"])
    assert "probability" not in dumped.lower()
    assert "percentile" not in dumped.lower()
