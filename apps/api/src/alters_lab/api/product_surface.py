"""P5-M1 API Product Surface Hardening routes.

Read-only product-facing route inventory and health/status summary.
"""

from __future__ import annotations

from fastapi import APIRouter

from alters_lab.schemas.product_surface import (
    ProductHealthResponse,
    ProductRoutesResponse,
    ProductStatusResponse,
    ProductWorkflowCapabilitiesResponse,
)
from alters_lab.services.product_surface import (
    get_product_health,
    get_product_routes,
    get_product_status,
    get_product_workflow_capabilities,
)

router = APIRouter(prefix="/product", tags=["product-surface"])


@router.get("/health", response_model=ProductHealthResponse)
def health():
    return get_product_health()


@router.get("/routes", response_model=ProductRoutesResponse)
def routes():
    from alters_lab.main import app
    return get_product_routes(app)


@router.get("/status", response_model=ProductStatusResponse)
def status():
    return get_product_status()


@router.get("/workflow-capabilities", response_model=ProductWorkflowCapabilitiesResponse)
def workflow_capabilities():
    return get_product_workflow_capabilities()
