"""Regression tests for runtime flow linkage."""

from fastapi.routing import APIRoute

from alters_lab.main import app
from alters_lab.services.local_app import should_block_spa_fallback


def _route_index(path: str, method: str) -> int:
    for index, route in enumerate(app.routes):
        if isinstance(route, APIRoute) and route.path == path and method in route.methods:
            return index
    raise AssertionError(f"Route not found: {method} {path}")


def test_calibration_drafts_route_precedes_dynamic_conversation_route() -> None:
    assert _route_index("/calibration-conversation/drafts", "GET") < _route_index(
        "/calibration-conversation/{conversation_id}", "GET"
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
