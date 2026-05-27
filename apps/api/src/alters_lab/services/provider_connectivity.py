"""Provider connectivity check service.

This module implements explicit real-provider connectivity checking for
openai-compatible-http mode. It never sends user prompt content, never
persists provider response content, and never creates scores or active
YAML mutations.
"""

from __future__ import annotations

import time
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from alters_lab.schemas.provider_connectivity import (
    ConnectivityStatus,
    ProviderConnectivityAuditEvent,
    ProviderConnectivityRequest,
    ProviderConnectivityResponse,
    ProviderConnectivityStatusResponse,
)
from alters_lab.schemas.provider_adapter import ProviderMode
from alters_lab.services.provider_config import (
    ProviderConfigState,
    SecretStore,
    _load_state,
)
from alters_lab.services.runtime_layout import RuntimeLayout

LIVE_CONFIRMATION = "run-live-provider-connectivity-check"
TIMEOUT_MIN = 1
TIMEOUT_MAX = 30
TIMEOUT_DEFAULT = 10

# Type alias for the HTTP client callable used in connectivity checks.
# Signature: (url, headers, timeout) -> (status_code, response_bytes)
HttpClient = Callable[[str, dict[str, str], int], tuple[int, bytes]]


def _default_http_client(url: str, headers: dict[str, str], timeout: int) -> tuple[int, bytes]:
    req = Request(url, headers=headers, method="GET")  # noqa: S310
    with urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return resp.status, resp.read()


def build_provider_connectivity_status(
    layout: RuntimeLayout | None = None,
) -> ProviderConnectivityStatusResponse:
    _, _, state = _load_state(layout)
    secrets = SecretStore(layout) if layout else None
    key_configured = False
    if secrets:
        key_configured = secrets.secret_configured(state.secret_storage, state.key_name)
    return ProviderConnectivityStatusResponse(
        provider_mode=state.mode,
        configured=state.mode in {"disabled", "mock"} or (
            state.mode == "openai-compatible-http"
            and bool(state.base_url)
            and bool(state.model)
            and key_configured
        ),
        key_configured=key_configured,
    )


def build_provider_connectivity_audit_event(
    *,
    provider_mode: ProviderMode,
    status: ConnectivityStatus,
    live_check: bool,
    dry_run: bool,
    network_call_made: bool,
    provider_reachable: bool | None = None,
    auth_valid: bool | None = None,
    status_code: int | None = None,
    latency_ms: int | None = None,
    error_type: str | None = None,
) -> ProviderConnectivityAuditEvent:
    return ProviderConnectivityAuditEvent(
        provider_mode=provider_mode,
        status=status,
        live_check=live_check,
        dry_run=dry_run,
        network_call_made=network_call_made,
        provider_reachable=provider_reachable,
        auth_valid=auth_valid,
        status_code=status_code,
        latency_ms=latency_ms,
        error_type=error_type,
    )


def _clamp_timeout(value: int | None, default: int = TIMEOUT_DEFAULT) -> int:
    if value is None:
        return default
    return max(TIMEOUT_MIN, min(TIMEOUT_MAX, value))


def _get_provider_api_key(layout: RuntimeLayout | None = None) -> str | None:
    _, _, state = _load_state(layout)
    secrets = SecretStore(layout) if layout else None
    if not secrets:
        return None
    if not secrets.secret_configured(state.secret_storage, state.key_name):
        return None
    # Internal use only — never exposed via API response.
    return secrets.get_secret(state.secret_storage, state.key_name)


def run_provider_connectivity_check(
    request: ProviderConnectivityRequest,
    layout: RuntimeLayout | None = None,
    http_client: HttpClient | None = None,
) -> ProviderConnectivityResponse:
    _, _, state = _load_state(layout)
    mode = state.mode
    timeout = _clamp_timeout(request.timeout_seconds)

    if mode == "disabled":
        audit = build_provider_connectivity_audit_event(
            provider_mode="disabled", status="skipped", live_check=request.live_check,
            dry_run=request.dry_run, network_call_made=False,
        )
        return ProviderConnectivityResponse(
            status="skipped", provider_mode="disabled", configured=True,
            live_check=request.live_check, dry_run=request.dry_run,
            network_call_made=False, audit_event_id=audit.event_id,
            message="Provider is disabled.",
        )

    if mode == "mock":
        audit = build_provider_connectivity_audit_event(
            provider_mode="mock", status="ok", live_check=request.live_check,
            dry_run=request.dry_run, network_call_made=False,
            provider_reachable=True, auth_valid=True,
        )
        return ProviderConnectivityResponse(
            status="ok", provider_mode="mock", configured=True,
            live_check=request.live_check, dry_run=request.dry_run,
            network_call_made=False, provider_reachable=True, auth_valid=True,
            audit_event_id=audit.event_id, message="Mock connectivity ok.",
        )

    # openai-compatible-http
    secrets = SecretStore(layout) if layout else None
    key_configured = bool(secrets and secrets.secret_configured(state.secret_storage, state.key_name))
    configured = bool(state.base_url) and bool(state.model) and key_configured

    if not configured:
        audit = build_provider_connectivity_audit_event(
            provider_mode="openai-compatible-http", status="blocked",
            live_check=request.live_check, dry_run=request.dry_run, network_call_made=False,
        )
        return ProviderConnectivityResponse(
            status="blocked", provider_mode="openai-compatible-http", configured=False,
            live_check=request.live_check, dry_run=request.dry_run,
            network_call_made=False, audit_event_id=audit.event_id,
            message="openai-compatible-http is not configured. Set base_url, model, and API key.",
        )

    if request.dry_run and not request.live_check:
        audit = build_provider_connectivity_audit_event(
            provider_mode="openai-compatible-http", status="ok",
            live_check=False, dry_run=True, network_call_made=False,
            provider_reachable=None, auth_valid=None,
        )
        return ProviderConnectivityResponse(
            status="ok", provider_mode="openai-compatible-http", configured=True,
            live_check=False, dry_run=True, network_call_made=False,
            audit_event_id=audit.event_id,
            message="Dry-run connectivity check. No network call made.",
        )

    if not request.live_check:
        audit = build_provider_connectivity_audit_event(
            provider_mode="openai-compatible-http", status="blocked",
            live_check=False, dry_run=request.dry_run, network_call_made=False,
        )
        return ProviderConnectivityResponse(
            status="blocked", provider_mode="openai-compatible-http", configured=True,
            live_check=False, dry_run=request.dry_run, network_call_made=False,
            audit_event_id=audit.event_id,
            message="Live network check requires live_check=true and exact confirmation.",
        )

    if request.live_check and request.confirmation != LIVE_CONFIRMATION:
        audit = build_provider_connectivity_audit_event(
            provider_mode="openai-compatible-http", status="blocked",
            live_check=True, dry_run=request.dry_run, network_call_made=False,
        )
        return ProviderConnectivityResponse(
            status="blocked", provider_mode="openai-compatible-http", configured=True,
            live_check=True, dry_run=request.dry_run, network_call_made=False,
            audit_event_id=audit.event_id,
            message=f"Live check requires confirmation='{LIVE_CONFIRMATION}'.",
        )

    # Live check with exact confirmation — perform minimal connectivity check.
    client = http_client or _default_http_client
    base_url = state.base_url.rstrip("/")
    url = f"{base_url}/models"
    api_key = _get_provider_api_key(layout) or ""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    start = time.monotonic()
    try:
        status_code, _ = client(url, headers, timeout)
        latency_ms = int((time.monotonic() - start) * 1000)
        if 200 <= status_code < 300:
            audit = build_provider_connectivity_audit_event(
                provider_mode="openai-compatible-http", status="ok",
                live_check=True, dry_run=False, network_call_made=True,
                provider_reachable=True, auth_valid=True,
                status_code=status_code, latency_ms=latency_ms,
            )
            return ProviderConnectivityResponse(
                status="ok", provider_mode="openai-compatible-http", configured=True,
                live_check=True, dry_run=False, network_call_made=True,
                provider_reachable=True, auth_valid=True,
                status_code=status_code, latency_ms=latency_ms,
                audit_event_id=audit.event_id,
                message=f"Provider reachable. Status {status_code}.",
            )
        if status_code in (401, 403):
            audit = build_provider_connectivity_audit_event(
                provider_mode="openai-compatible-http", status="error",
                live_check=True, dry_run=False, network_call_made=True,
                provider_reachable=True, auth_valid=False,
                status_code=status_code, latency_ms=latency_ms,
            )
            return ProviderConnectivityResponse(
                status="error", provider_mode="openai-compatible-http", configured=True,
                live_check=True, dry_run=False, network_call_made=True,
                provider_reachable=True, auth_valid=False,
                status_code=status_code, latency_ms=latency_ms,
                audit_event_id=audit.event_id, error_type="auth_failed",
                message=f"Provider reachable but auth failed. Status {status_code}.",
            )
        audit = build_provider_connectivity_audit_event(
            provider_mode="openai-compatible-http", status="error",
            live_check=True, dry_run=False, network_call_made=True,
            provider_reachable=True, auth_valid=None,
            status_code=status_code, latency_ms=latency_ms,
        )
        return ProviderConnectivityResponse(
            status="error", provider_mode="openai-compatible-http", configured=True,
            live_check=True, dry_run=False, network_call_made=True,
            provider_reachable=True, auth_valid=None,
            status_code=status_code, latency_ms=latency_ms,
            audit_event_id=audit.event_id, error_type="http_error",
            message=f"Provider returned status {status_code}.",
        )
    except HTTPError as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        code = exc.code if hasattr(exc, "code") else None
        if code in (401, 403):
            audit = build_provider_connectivity_audit_event(
                provider_mode="openai-compatible-http", status="error",
                live_check=True, dry_run=False, network_call_made=True,
                provider_reachable=True, auth_valid=False,
                status_code=code, latency_ms=latency_ms, error_type="auth_failed",
            )
            return ProviderConnectivityResponse(
                status="error", provider_mode="openai-compatible-http", configured=True,
                live_check=True, dry_run=False, network_call_made=True,
                provider_reachable=True, auth_valid=False,
                status_code=code, latency_ms=latency_ms,
                audit_event_id=audit.event_id, error_type="auth_failed",
                message=f"Provider reachable but auth failed. Status {code}.",
            )
        audit = build_provider_connectivity_audit_event(
            provider_mode="openai-compatible-http", status="error",
            live_check=True, dry_run=False, network_call_made=True,
            provider_reachable=True, auth_valid=None,
            status_code=code, latency_ms=latency_ms, error_type="http_error",
        )
        return ProviderConnectivityResponse(
            status="error", provider_mode="openai-compatible-http", configured=True,
            live_check=True, dry_run=False, network_call_made=True,
            provider_reachable=True, auth_valid=None,
            status_code=code, latency_ms=latency_ms,
            audit_event_id=audit.event_id, error_type="http_error",
            message=f"HTTP error. Status {code}.",
        )
    except (URLError, OSError, TimeoutError) as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        audit = build_provider_connectivity_audit_event(
            provider_mode="openai-compatible-http", status="error",
            live_check=True, dry_run=False, network_call_made=True,
            provider_reachable=False, auth_valid=None,
            latency_ms=latency_ms, error_type="connection_error",
        )
        return ProviderConnectivityResponse(
            status="error", provider_mode="openai-compatible-http", configured=True,
            live_check=True, dry_run=False, network_call_made=True,
            provider_reachable=False, auth_valid=None,
            latency_ms=latency_ms,
            audit_event_id=audit.event_id, error_type="connection_error",
            message="Connection failed. Provider not reachable.",
        )
    except Exception:
        latency_ms = int((time.monotonic() - start) * 1000)
        audit = build_provider_connectivity_audit_event(
            provider_mode="openai-compatible-http", status="error",
            live_check=True, dry_run=False, network_call_made=True,
            provider_reachable=False, auth_valid=None,
            latency_ms=latency_ms, error_type="unknown_error",
        )
        return ProviderConnectivityResponse(
            status="error", provider_mode="openai-compatible-http", configured=True,
            live_check=True, dry_run=False, network_call_made=True,
            provider_reachable=False, auth_valid=None,
            latency_ms=latency_ms,
            audit_event_id=audit.event_id, error_type="unknown_error",
            message="Unexpected error during connectivity check.",
        )
