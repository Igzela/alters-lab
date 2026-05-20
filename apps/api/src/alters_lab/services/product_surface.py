"""P5-M1 API Product Surface Hardening service.

Read-only product-facing route inventory and health/status summary.
No writes, no provider calls, no active YAML mutation.
"""

from __future__ import annotations

from fastapi import FastAPI

from alters_lab.schemas.product_surface import (
    ProductHealthResponse,
    ProductRoutesResponse,
    ProductStatusResponse,
    ProductWorkflowCapabilitiesResponse,
    RouteClassification,
)

SAFE_TAGS = {"product-surface", "provider-dialogue", "calibration-loop", "rubric-delta", "checkpoint-regeneration", "provider-gateway"}
INTERNAL_TAGS = {"promotion-live-execution", "promotion-orchestration", "promotion-execution-gate"}
DANGEROUS_KEYWORDS = {"promotion-live-execution", "controlled", "persist"}


def _classify_route(path: str, method: str, tags: list[str]) -> RouteClassification:
    lower_path = path.lower()
    for kw in DANGEROUS_KEYWORDS:
        if kw in lower_path:
            return RouteClassification(path=path, method=method, classification="dangerous", tags=tags)
    tag_set = set(tags)
    if tag_set & INTERNAL_TAGS:
        return RouteClassification(path=path, method=method, classification="internal", tags=tags)
    if tag_set & SAFE_TAGS or path.startswith("/product") or path.startswith("/provider-dialogue") or path.startswith("/provider-gateway") or path.startswith("/calibration-loop") or path.startswith("/rubric-delta") or path.startswith("/checkpoint-regeneration") or path.startswith("/storage-boundary") or path.startswith("/user-workflow") or path.startswith("/phase5-closeout") or path == "/health":
        return RouteClassification(path=path, method=method, classification="safe", tags=tags)
    return RouteClassification(path=path, method=method, classification="internal", tags=tags)


def get_product_health() -> ProductHealthResponse:
    return ProductHealthResponse()


def get_product_routes(app: FastAPI) -> ProductRoutesResponse:
    safe: list[RouteClassification] = []
    internal: list[RouteClassification] = []
    dangerous: list[RouteClassification] = []
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        tags = list(getattr(route, "tags", []))
        if path is None or methods is None:
            continue
        for method in sorted(methods):
            classification = _classify_route(path, method, tags)
            if classification.classification == "safe":
                safe.append(classification)
            elif classification.classification == "dangerous":
                dangerous.append(classification)
            else:
                internal.append(classification)
    total = len(safe) + len(internal) + len(dangerous)
    return ProductRoutesResponse(
        safe_routes=safe,
        internal_routes=internal,
        dangerous_routes=dangerous,
        total=total,
    )


def get_product_status() -> ProductStatusResponse:
    return ProductStatusResponse(
        safe_public_endpoints=[
            "/alter-dialogue/*",
            "/calibration-loop/*",
            "/rubric-delta/*",
            "/checkpoint-regeneration/*",
            "/product/*",
            "/provider-dialogue/*",
        ],
        internal_only_endpoints=[
            "/promotion-live-execution/*",
            "/branches/persist",
            "/alters/persist",
        ],
    )


def get_product_workflow_capabilities() -> ProductWorkflowCapabilitiesResponse:
    return ProductWorkflowCapabilitiesResponse(
        capabilities=[
            "select_alter",
            "provider_mock_dialogue",
            "submit_reality_score",
            "view_calibration_history",
            "view_drift_evidence",
            "generate_rubric_delta_suggestion",
            "generate_checkpoint_plan",
            "view_product_status",
            "view_storage_manifest",
            "view_workflow_state",
        ],
    )
