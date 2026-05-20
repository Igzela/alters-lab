"""Tests for P5-M1 API Product Surface service."""

from __future__ import annotations

from alters_lab.schemas.product_surface import (
    ProductHealthResponse,
    ProductRoutesResponse,
    ProductStatusResponse,
    ProductWorkflowCapabilitiesResponse,
    RouteClassification,
)
from alters_lab.services.product_surface import (
    get_product_health,
    get_product_routes,
    get_product_status,
    get_product_workflow_capabilities,
    _classify_route,
)
from alters_lab.main import app


def test_health_response():
    r = get_product_health()
    assert isinstance(r, ProductHealthResponse)
    assert r.status == "ok"
    assert r.read_only is True


def test_status_has_no_secrets():
    r = get_product_status()
    assert isinstance(r, ProductStatusResponse)
    assert r.no_secrets_exposed is True
    assert "key" not in str(r.safe_public_endpoints).lower()
    assert "secret" not in str(r.safe_public_endpoints).lower()


def test_status_phase_info():
    r = get_product_status()
    assert r.phase3_status == "sealed_with_notes"
    assert r.phase4_status == "pass"
    assert r.provider_gateway_status == "mock_default"
    assert r.storage_backend == "yaml"


def test_route_inventory_includes_product_routes():
    r = get_product_routes(app)
    assert isinstance(r, ProductRoutesResponse)
    paths = {route.path for route in r.safe_routes + r.internal_routes + r.dangerous_routes}
    assert "/product/health" in paths
    assert "/product/routes" in paths
    assert "/product/status" in paths
    assert "/product/workflow-capabilities" in paths


def test_route_classification_safe_vs_internal():
    safe = _classify_route("/product/health", "GET", ["product-surface"])
    assert safe.classification == "safe"

    internal = _classify_route("/promotion-live-execution/run", "POST", ["promotion-live-execution"])
    assert internal.classification == "dangerous"


def test_dangerous_keywords_detected():
    r = _classify_route("/promotion-live-execution/run", "POST", [])
    assert r.classification == "dangerous"


def test_workflow_capabilities_read_only():
    r = get_product_workflow_capabilities()
    assert isinstance(r, ProductWorkflowCapabilitiesResponse)
    assert r.read_only is True
    assert len(r.capabilities) > 0
    assert "select_alter" in r.capabilities
    assert "provider_mock_dialogue" in r.capabilities
    assert "submit_reality_score" in r.capabilities


def test_route_inventory_total():
    r = get_product_routes(app)
    assert r.total == len(r.safe_routes) + len(r.internal_routes) + len(r.dangerous_routes)
