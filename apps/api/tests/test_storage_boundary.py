"""Tests for P5-M5 Durable Storage Boundary service."""

from __future__ import annotations

from alters_lab.schemas.storage_boundary import (
    StorageBoundaryHealthResponse,
    StorageManifestResponse,
)
from alters_lab.services.storage_boundary import (
    get_storage_boundary_health,
    get_storage_manifest,
)


def test_health_response():
    r = get_storage_boundary_health()
    assert isinstance(r, StorageBoundaryHealthResponse)
    assert r.status == "ok"
    assert r.component == "storage-boundary"
    assert r.default_backend == "yaml"
    assert r.database_added is False


def test_manifest_classifies_paths():
    r = get_storage_manifest()
    assert isinstance(r, StorageManifestResponse)
    assert r.default_backend == "yaml"
    assert r.database_implemented is False
    assert r.no_migration is True
    assert len(r.active_yaml_read_only) > 0
    assert len(r.calibration_score_write) > 0
    assert len(r.product_session_write) > 0
    assert len(r.ignored_runtime_areas) > 0
    assert len(r.evidence_areas) > 0


def test_active_yaml_read_only():
    r = get_storage_manifest()
    assert "alters/current/snapshot.yaml" in r.active_yaml_read_only
    assert "alters/current/branches.yaml" in r.active_yaml_read_only
    for alter in ("alter_A", "alter_B", "alter_C", "alter_D"):
        assert f"alters/current/alters/{alter}.yaml" in r.active_yaml_read_only


def test_product_session_write_area():
    r = get_storage_manifest()
    assert "alters/product/sessions/" in r.product_session_write
    assert "alters/product/provider_runs/" in r.product_session_write
    assert "alters/product/workflow_runs/" in r.product_session_write


def test_ignored_runtime_areas():
    r = get_storage_manifest()
    assert "alters/product/sessions/" in r.ignored_runtime_areas


def test_no_db_imports():
    import alters_lab.services.storage_boundary as mod
    content = open(mod.__file__).read().lower()
    for pattern in ["sqlite", "sqlalchemy", "psycopg", "alembic", "django.db"]:
        assert pattern not in content
