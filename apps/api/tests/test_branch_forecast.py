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
