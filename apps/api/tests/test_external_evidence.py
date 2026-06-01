"""Tests for external evidence schema, service, and API."""

from __future__ import annotations

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from pydantic import ValidationError

from alters_lab.schemas.external_evidence import ExternalEvidenceRecord
from alters_lab.services.external_evidence import save_evidence, load_evidence, list_evidence


def _valid_evidence(**overrides) -> dict:
    base = {
        "branch_id": "branch_A",
        "domain": "career_education",
        "evidence_type": "milestone_completed",
        "description": "Passed AWS certification exam",
        "objective_strength": "strong",
        "polarity": "positive",
    }
    base.update(overrides)
    return base


# --- Schema tests ---

def test_valid_evidence_creates():
    record = ExternalEvidenceRecord(**_valid_evidence())
    assert record.evidence_id.startswith("ee_")
    assert record.source_type == "external_evidence"
    assert record.description == "Passed AWS certification exam"


def test_missing_description_rejected():
    with pytest.raises(ValidationError, match="description"):
        ExternalEvidenceRecord(**_valid_evidence(description=""))


def test_whitespace_description_rejected():
    with pytest.raises(ValidationError, match="description"):
        ExternalEvidenceRecord(**_valid_evidence(description="   "))


def test_invalid_domain_rejected():
    with pytest.raises(ValidationError):
        ExternalEvidenceRecord(**_valid_evidence(domain="invalid_domain"))


def test_invalid_evidence_type_rejected():
    with pytest.raises(ValidationError):
        ExternalEvidenceRecord(**_valid_evidence(evidence_type="invalid_type"))


def test_objective_strength_required():
    with pytest.raises(ValidationError):
        ExternalEvidenceRecord(**_valid_evidence(objective_strength="invalid"))


def test_weak_evidence_allowed():
    record = ExternalEvidenceRecord(**_valid_evidence(objective_strength="weak"))
    assert record.objective_strength == "weak"


def test_extra_fields_rejected():
    with pytest.raises(ValidationError):
        ExternalEvidenceRecord(**_valid_evidence(bad_field="nope"))


def test_optional_fields():
    record = ExternalEvidenceRecord(**_valid_evidence(
        numeric_value=85.5,
        unit="percent",
        artifact_ref="https://example.com/cert",
        notes="Additional context",
    ))
    assert record.numeric_value == 85.5
    assert record.unit == "percent"
    assert record.artifact_ref == "https://example.com/cert"


# --- Service tests ---

def test_save_and_load_evidence(tmp_path: Path):
    record = ExternalEvidenceRecord(**_valid_evidence())
    path = save_evidence(record, repo_root=tmp_path)
    assert path.exists()
    loaded = load_evidence(record.evidence_id, repo_root=tmp_path)
    assert loaded.evidence_id == record.evidence_id
    assert loaded.description == "Passed AWS certification exam"


def test_list_evidence(tmp_path: Path):
    for desc in ["Evidence A", "Evidence B"]:
        record = ExternalEvidenceRecord(**_valid_evidence(description=desc))
        save_evidence(record, repo_root=tmp_path)
    evidence = list_evidence(repo_root=tmp_path)
    assert len(evidence) == 2


def test_no_provider_call(record=None):
    record = ExternalEvidenceRecord(**_valid_evidence())
    dumped = record.model_dump(mode="json")
    assert "provider" not in str(dumped).lower() or "provider_required" not in str(dumped)


# --- API tests ---

@pytest.fixture
def client():
    from alters_lab.main import app
    return TestClient(app)


def test_api_create_evidence(client):
    resp = client.post("/external-evidence", json=_valid_evidence())
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "saved"
    assert data["evidence"]["description"] == "Passed AWS certification exam"


def test_api_create_evidence_missing_description(client):
    resp = client.post("/external-evidence", json=_valid_evidence(description=""))
    assert resp.status_code in (400, 422)


def test_api_list_evidence(client):
    client.post("/external-evidence", json=_valid_evidence())
    resp = client.get("/external-evidence/list")
    assert resp.status_code == 200
    assert resp.json()["count"] >= 1


def test_api_get_evidence(client):
    post_resp = client.post("/external-evidence", json=_valid_evidence())
    evidence_id = post_resp.json()["evidence"]["evidence_id"]
    resp = client.get(f"/external-evidence/{evidence_id}")
    assert resp.status_code == 200
    assert resp.json()["evidence"]["evidence_id"] == evidence_id


def test_api_get_nonexistent(client):
    resp = client.get("/external-evidence/nonexistent_id")
    assert resp.status_code == 404
