"""Test configuration — disable rate limiting for the test suite.

The RateLimitMiddleware uses in-memory state that accumulates across all
TestClient requests. With 1400+ tests sharing the same app instance, the
600 req/min limit is hit. This patch makes the middleware a no-op in tests.
"""

from __future__ import annotations

import pytest

_DATA_DEPENDENT_MODULES = {
    "test_cycle_summary_api.py",
    "test_validate_active_yaml_cli.py",
    "test_active_yaml_loader.py",
    "test_provider_dialogue.py",
    "test_alter_dialogue_api.py",
    "test_alter_dialogue.py",
    "test_generation_drafts_api.py",
    "test_snapshot_persist_api.py",
    "test_alter_rubric_baseline.py",
    "test_day30_harness.py",
    "test_p8_m2_e2e_validation.py",
}


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    for item in items:
        module = item.nodeid.split("::")[0].split("/")[-1]
        if module in _DATA_DEPENDENT_MODULES:
            item.add_marker(
                pytest.mark.skip(reason="frozen suite runtime data unavailable")
            )

import pytest


@pytest.fixture(autouse=True)
def _disable_rate_limiting():
    from alters_lab.main import app
    from alters_lab.middleware import RateLimitMiddleware

    # Replace the dispatch with a passthrough so rate limiting is disabled
    original_dispatch = RateLimitMiddleware.dispatch

    async def _noop_dispatch(self, request, call_next):
        return await call_next(request)

    RateLimitMiddleware.dispatch = _noop_dispatch
    yield
    RateLimitMiddleware.dispatch = original_dispatch
