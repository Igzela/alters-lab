"""Test configuration — disable rate limiting for the test suite.

The RateLimitMiddleware uses in-memory state that accumulates across all
TestClient requests. With 1400+ tests sharing the same app instance, the
600 req/min limit is hit. This patch makes the middleware a no-op in tests.
"""

from __future__ import annotations

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
