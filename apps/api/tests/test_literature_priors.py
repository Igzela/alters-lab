"""Tests for literature prior catalog schema, service, and API."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from alters_lab.schemas.literature_priors import (
    LiteraturePriorCatalog,
    load_literature_prior_catalog,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CATALOG_PATH = (
    _REPO_ROOT
    / "alters"
    / "product"
    / "literature_priors"
    / "catalog"
    / "literature_prior_catalog_v0_1.yaml"
)


@pytest.fixture
def catalog():
    return load_literature_prior_catalog(_CATALOG_PATH)


@pytest.fixture
def client():
    from alters_lab.main import app
    return TestClient(app)


def test_catalog_loads(catalog):
    assert catalog.catalog_id == "literature_prior_catalog_v0_1"
    assert len(catalog.evidence_sources) > 0
    assert len(catalog.constructs) > 0
    assert len(catalog.priors) > 0


def test_every_evidence_source_id_resolves(catalog):
    source_ids = {s.source_id for s in catalog.evidence_sources}
    for cdl in catalog.construct_domain_links:
        for eid in cdl.evidence_source_ids:
            assert eid in source_ids, f"construct_domain_link references unknown source: {eid}"
    for p in catalog.priors:
        for eid in p.evidence_source_ids:
            assert eid in source_ids, f"prior references unknown source: {eid}"


def test_no_fake_numeric_percentile(catalog):
    for prior in catalog.priors:
        assert not hasattr(prior, "population_percentile") or getattr(prior, "population_percentile", None) is None


def test_prior_confidence_exists(catalog):
    for prior in catalog.priors:
        assert prior.prior_confidence in ("low", "medium", "high")


def test_transfer_risk_exists(catalog):
    for prior in catalog.priors:
        assert prior.transfer_risk in ("low", "medium", "high")
    for cdl in catalog.construct_domain_links:
        assert cdl.transfer_risk in ("low", "medium", "high")


def test_predicted_domains_use_allowed_enum(catalog):
    allowed = {"career_education", "financial", "health", "relationship", "subjective_wellbeing"}
    for prior in catalog.priors:
        assert prior.predicted_domain in allowed, f"prior {prior.prior_id} has invalid domain"
    for cdl in catalog.construct_domain_links:
        assert cdl.predicted_domain in allowed, f"cdl for {cdl.construct_id} has invalid domain"


def test_constructs_have_measured_by(catalog):
    for construct in catalog.constructs:
        assert len(construct.measured_by.behavior_metrics) > 0 or len(construct.measured_by.predictor_profile_fields) > 0


def test_api_health(client):
    resp = client.get("/literature-priors/health")
    assert resp.status_code == 200
    assert resp.json()["provider_required"] is False


def test_api_catalog(client):
    resp = client.get("/literature-priors/catalog")
    assert resp.status_code == 200
    assert resp.json()["catalog_id"] == "literature_prior_catalog_v0_1"


def test_api_constructs(client):
    resp = client.get("/literature-priors/constructs")
    assert resp.status_code == 200
    assert len(resp.json()["constructs"]) > 0


def test_api_domain(client):
    resp = client.get("/literature-priors/domain/health")
    assert resp.status_code == 200
    assert len(resp.json()["priors"]) > 0
    for prior in resp.json()["priors"]:
        assert prior["predicted_domain"] == "health"
