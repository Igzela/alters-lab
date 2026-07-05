"""Regression tests for runtime flow linkage."""

from fastapi.routing import APIRoute

from alters_lab.api.calibration_conversation import router as calibration_conversation_router
from alters_lab.services.local_app import should_block_spa_fallback


def _router_endpoint_index(endpoint_name: str, method: str) -> int:
    for index, route in enumerate(calibration_conversation_router.routes):
        endpoint = getattr(route, "endpoint", None)
        if (
            isinstance(route, APIRoute)
            and getattr(endpoint, "__name__", None) == endpoint_name
            and method in route.methods
        ):
            return index
    raise AssertionError(f"Route endpoint not found: {method} {endpoint_name}")


def test_calibration_drafts_route_precedes_dynamic_conversation_route() -> None:
    assert _router_endpoint_index("list_drafts", "GET") < _router_endpoint_index(
        "get_conversation", "GET"
    )


def test_api_prefixes_block_spa_fallback_for_newer_routes() -> None:
    for prefix in [
        "behavior-metrics",
        "branch-forecast",
        "calibration-conversation",
        "external-evidence",
        "forecast-evaluations",
        "forecast-scorecard",
        "forecast-snapshots",
        "provider-config",
        "public-priors",
    ]:
        assert should_block_spa_fallback(f"{prefix}/missing")

    assert not should_block_spa_fallback("dashboard")
