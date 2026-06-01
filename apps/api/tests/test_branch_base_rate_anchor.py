"""Tests for branch base-rate anchor service."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from alters_lab.schemas.branch_base_rate_anchor import BranchBaseRateAnchorRequest
from alters_lab.services.branch_base_rate_anchor import analyze_base_rate_anchor


@pytest.fixture
def client():
    from alters_lab.main import app
    return TestClient(app)


def test_api_analyze(client):
    resp = client.post(
        "/branch-base-rate-anchor/analyze",
        json={"branch_id": "branch_A", "lookback_weeks": 8},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["branch_id"] == "branch_A"
    assert "route_a_available" in data
    assert "route_b_available" in data
    assert "prior_summary" in data
    assert "domain_anchors" in data
    assert "limitations" in data


def test_route_b_available_when_catalog_exists(client):
    resp = client.post(
        "/branch-base-rate-anchor/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    assert data["route_b_available"] is True


def test_no_fake_population_percentile(client):
    resp = client.post(
        "/branch-base-rate-anchor/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    assert data["population_percentile"] is None


def test_no_fake_deviation_from_baseline(client):
    resp = client.post(
        "/branch-base-rate-anchor/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    assert data["deviation_from_baseline"] is None


def test_limitations_include_missing_outcome_targets(client):
    resp = client.post(
        "/branch-base-rate-anchor/analyze",
        json={"branch_id": "branch_no_targets_exist"},
    )
    data = resp.json()
    assert any("outcome targets" in lim.lower() for lim in data["limitations"])


def test_domain_anchors_cover_all_domains(client):
    resp = client.post(
        "/branch-base-rate-anchor/analyze",
        json={"branch_id": "branch_A"},
    )
    data = resp.json()
    domains = {a["domain"] for a in data["domain_anchors"]}
    assert domains == {"career_education", "financial", "health", "relationship", "subjective_wellbeing"}
