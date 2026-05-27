"""Provider-backed dialogue preview service.

First content-generating provider feature. Output is preview-only,
unverified, explicitly triggered, and non-persistent.
"""

from __future__ import annotations

import json
import time
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from alters_lab.schemas.provider_dialogue_preview import (
    DialoguePreviewStatus,
    ProviderDialoguePreviewAuditEvent,
    ProviderDialoguePreviewHealthResponse,
    ProviderDialoguePreviewRequest,
    ProviderDialoguePreviewResponse,
    ProviderDialoguePreviewStatusResponse,
)
from alters_lab.schemas.provider_adapter import ProviderMode
from alters_lab.services.provider_config import (
    SecretStore,
    _load_state,
)
from alters_lab.services.runtime_layout import RuntimeLayout

LIVE_CONFIRMATION = "run-live-provider-dialogue-preview"
DEFAULT_SYSTEM_PROMPT = (
    "You are generating an unverified preview. "
    "Do not claim authority. Keep output concise."
)
PROMPT_MAX_LEN = 8000
SYSTEM_PROMPT_MAX_LEN = 4000
MAX_TOKENS_MIN = 16
MAX_TOKENS_MAX = 1200
MAX_TOKENS_DEFAULT = 512
TEMPERATURE_MIN = 0.0
TEMPERATURE_MAX = 1.5
TEMPERATURE_DEFAULT = 0.7
TIMEOUT_DEFAULT = 30

MOCK_PREVIEW = (
    "[mock dialogue preview] This is a deterministic placeholder response "
    "from the provider dialogue preview. No real provider was called. "
    "Output is unverified."
)

# http_client signature: (url, headers, body_bytes, timeout) -> (status_code, response_bytes)
HttpClient = Callable[[str, dict[str, str], bytes, int], tuple[int, bytes]]


def _default_http_client(
    url: str, headers: dict[str, str], body: bytes, timeout: int
) -> tuple[int, bytes]:
    req = Request(url, data=body, headers=headers, method="POST")  # noqa: S310
    with urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return resp.status, resp.read()


def _clamp_temperature(value: float | None) -> float:
    if value is None:
        return TEMPERATURE_DEFAULT
    return max(TEMPERATURE_MIN, min(TEMPERATURE_MAX, value))


def _clamp_max_tokens(value: int | None) -> int:
    if value is None:
        return MAX_TOKENS_DEFAULT
    return max(MAX_TOKENS_MIN, min(MAX_TOKENS_MAX, value))


def _truncate(value: str, limit: int) -> str:
    return value[:limit] if len(value) > limit else value


def build_provider_dialogue_preview_health() -> ProviderDialoguePreviewHealthResponse:
    return ProviderDialoguePreviewHealthResponse()


def build_provider_dialogue_preview_status(
    layout: RuntimeLayout | None = None,
) -> ProviderDialoguePreviewStatusResponse:
    _, _, state = _load_state(layout)
    secrets = SecretStore(layout) if layout else None
    key_configured = bool(secrets and secrets.secret_configured(state.secret_storage, state.key_name))
    configured = state.mode in {"disabled", "mock"} or (
        state.mode == "openai-compatible-http"
        and bool(state.base_url) and bool(state.model) and key_configured
    )
    return ProviderDialoguePreviewStatusResponse(
        provider_mode=state.mode, configured=configured,
    )


def build_provider_dialogue_preview_audit_event(
    *,
    provider_mode: ProviderMode,
    status: DialoguePreviewStatus,
    dry_run: bool,
    live_generation: bool,
    network_call_made: bool,
    output_persisted: bool = False,
    status_code: int | None = None,
    latency_ms: int | None = None,
    error_type: str | None = None,
) -> ProviderDialoguePreviewAuditEvent:
    return ProviderDialoguePreviewAuditEvent(
        provider_mode=provider_mode, status=status,
        dry_run=dry_run, live_generation=live_generation,
        network_call_made=network_call_made, output_persisted=output_persisted,
        status_code=status_code, latency_ms=latency_ms, error_type=error_type,
    )


def run_provider_dialogue_preview(
    request: ProviderDialoguePreviewRequest,
    layout: RuntimeLayout | None = None,
    http_client: HttpClient | None = None,
) -> ProviderDialoguePreviewResponse:
    _, _, state = _load_state(layout)
    mode = request.mode or state.mode

    if mode == "disabled":
        audit = build_provider_dialogue_preview_audit_event(
            provider_mode="disabled", status="skipped",
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
        )
        return ProviderDialoguePreviewResponse(
            status="skipped", provider_mode="disabled", configured=True,
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
            audit_event_id=audit.event_id, message="Provider is disabled.",
        )

    if mode == "mock":
        audit = build_provider_dialogue_preview_audit_event(
            provider_mode="mock", status="ok",
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
        )
        return ProviderDialoguePreviewResponse(
            status="ok", provider_mode="mock", configured=True,
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
            output_preview=MOCK_PREVIEW, audit_event_id=audit.event_id,
            message="Mock dialogue preview. No network call made.",
        )

    # openai-compatible-http
    secrets = SecretStore(layout) if layout else None
    key_configured = bool(secrets and secrets.secret_configured(state.secret_storage, state.key_name))
    configured = bool(state.base_url) and bool(state.model) and key_configured

    if not configured:
        audit = build_provider_dialogue_preview_audit_event(
            provider_mode="openai-compatible-http", status="blocked",
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
        )
        return ProviderDialoguePreviewResponse(
            status="blocked", provider_mode="openai-compatible-http", configured=False,
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
            audit_event_id=audit.event_id,
            message="openai-compatible-http is not configured. Set base_url, model, and API key.",
        )

    if request.dry_run:
        audit = build_provider_dialogue_preview_audit_event(
            provider_mode="openai-compatible-http", status="ok",
            dry_run=True, live_generation=False, network_call_made=False,
        )
        return ProviderDialoguePreviewResponse(
            status="ok", provider_mode="openai-compatible-http", configured=True,
            dry_run=True, live_generation=False, network_call_made=False,
            output_preview="[dry-run] Provider dialogue preview would generate output here. No network call made.",
            audit_event_id=audit.event_id, message="Dry-run dialogue preview. No network call made.",
        )

    if not request.live_generation:
        audit = build_provider_dialogue_preview_audit_event(
            provider_mode="openai-compatible-http", status="blocked",
            dry_run=False, live_generation=False, network_call_made=False,
        )
        return ProviderDialoguePreviewResponse(
            status="blocked", provider_mode="openai-compatible-http", configured=True,
            dry_run=False, live_generation=False, network_call_made=False,
            audit_event_id=audit.event_id,
            message="Live generation requires live_generation=true and exact confirmation.",
        )

    if request.persist_output:
        audit = build_provider_dialogue_preview_audit_event(
            provider_mode="openai-compatible-http", status="blocked",
            dry_run=False, live_generation=True, network_call_made=False,
        )
        return ProviderDialoguePreviewResponse(
            status="blocked", provider_mode="openai-compatible-http", configured=True,
            dry_run=False, live_generation=True, network_call_made=False,
            audit_event_id=audit.event_id,
            message="persist_output is not supported in P8-M3.",
        )

    if request.save_session:
        audit = build_provider_dialogue_preview_audit_event(
            provider_mode="openai-compatible-http", status="blocked",
            dry_run=False, live_generation=True, network_call_made=False,
        )
        return ProviderDialoguePreviewResponse(
            status="blocked", provider_mode="openai-compatible-http", configured=True,
            dry_run=False, live_generation=True, network_call_made=False,
            audit_event_id=audit.event_id,
            message="save_session is not supported in P8-M3.",
        )

    if request.confirmation != LIVE_CONFIRMATION:
        audit = build_provider_dialogue_preview_audit_event(
            provider_mode="openai-compatible-http", status="blocked",
            dry_run=False, live_generation=True, network_call_made=False,
        )
        return ProviderDialoguePreviewResponse(
            status="blocked", provider_mode="openai-compatible-http", configured=True,
            dry_run=False, live_generation=True, network_call_made=False,
            audit_event_id=audit.event_id,
            message=f"Live generation requires confirmation='{LIVE_CONFIRMATION}'.",
        )

    # Live generation with exact confirmation.
    client = http_client or _default_http_client
    base_url = state.base_url.rstrip("/")
    url = f"{base_url}/chat/completions"
    api_key = _get_provider_api_key(layout) or ""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    system_content = _truncate(request.system_prompt or DEFAULT_SYSTEM_PROMPT, SYSTEM_PROMPT_MAX_LEN)
    user_content = _truncate(request.prompt, PROMPT_MAX_LEN)
    payload = json.dumps({
        "model": state.model,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        "temperature": _clamp_temperature(request.temperature),
        "max_tokens": _clamp_max_tokens(request.max_tokens),
    }).encode("utf-8")

    start = time.monotonic()
    try:
        status_code, body = client(url, headers, payload, TIMEOUT_DEFAULT)
        latency_ms = int((time.monotonic() - start) * 1000)

        if 200 <= status_code < 300:
            try:
                data = json.loads(body)
                output = data["choices"][0]["message"]["content"]
            except (json.JSONDecodeError, KeyError, IndexError, TypeError):
                audit = build_provider_dialogue_preview_audit_event(
                    provider_mode="openai-compatible-http", status="error",
                    dry_run=False, live_generation=True, network_call_made=True,
                    status_code=status_code, latency_ms=latency_ms, error_type="invalid_response",
                )
                return ProviderDialoguePreviewResponse(
                    status="error", provider_mode="openai-compatible-http", configured=True,
                    dry_run=False, live_generation=True, network_call_made=True,
                    status_code=status_code, latency_ms=latency_ms, error_type="invalid_response",
                    audit_event_id=audit.event_id,
                    message="Provider returned invalid response format.",
                )
            audit = build_provider_dialogue_preview_audit_event(
                provider_mode="openai-compatible-http", status="ok",
                dry_run=False, live_generation=True, network_call_made=True,
                status_code=status_code, latency_ms=latency_ms,
            )
            return ProviderDialoguePreviewResponse(
                status="ok", provider_mode="openai-compatible-http", configured=True,
                dry_run=False, live_generation=True, network_call_made=True,
                output_preview=output, status_code=status_code, latency_ms=latency_ms,
                audit_event_id=audit.event_id,
                message="Provider dialogue preview generated. Output is unverified.",
            )

        if status_code in (401, 403):
            audit = build_provider_dialogue_preview_audit_event(
                provider_mode="openai-compatible-http", status="error",
                dry_run=False, live_generation=True, network_call_made=True,
                status_code=status_code, latency_ms=latency_ms, error_type="auth_failed",
            )
            return ProviderDialoguePreviewResponse(
                status="error", provider_mode="openai-compatible-http", configured=True,
                dry_run=False, live_generation=True, network_call_made=True,
                status_code=status_code, latency_ms=latency_ms, error_type="auth_failed",
                audit_event_id=audit.event_id,
                message=f"Provider auth failed. Status {status_code}.",
            )

        audit = build_provider_dialogue_preview_audit_event(
            provider_mode="openai-compatible-http", status="error",
            dry_run=False, live_generation=True, network_call_made=True,
            status_code=status_code, latency_ms=latency_ms, error_type="http_error",
        )
        return ProviderDialoguePreviewResponse(
            status="error", provider_mode="openai-compatible-http", configured=True,
            dry_run=False, live_generation=True, network_call_made=True,
            status_code=status_code, latency_ms=latency_ms, error_type="http_error",
            audit_event_id=audit.event_id,
            message=f"Provider returned status {status_code}.",
        )

    except (URLError, OSError, TimeoutError):
        latency_ms = int((time.monotonic() - start) * 1000)
        audit = build_provider_dialogue_preview_audit_event(
            provider_mode="openai-compatible-http", status="error",
            dry_run=False, live_generation=True, network_call_made=True,
            latency_ms=latency_ms, error_type="connection_error",
        )
        return ProviderDialoguePreviewResponse(
            status="error", provider_mode="openai-compatible-http", configured=True,
            dry_run=False, live_generation=True, network_call_made=True,
            latency_ms=latency_ms, error_type="connection_error",
            audit_event_id=audit.event_id,
            message="Connection failed. Provider not reachable.",
        )
    except Exception:
        latency_ms = int((time.monotonic() - start) * 1000)
        audit = build_provider_dialogue_preview_audit_event(
            provider_mode="openai-compatible-http", status="error",
            dry_run=False, live_generation=True, network_call_made=True,
            latency_ms=latency_ms, error_type="unknown_error",
        )
        return ProviderDialoguePreviewResponse(
            status="error", provider_mode="openai-compatible-http", configured=True,
            dry_run=False, live_generation=True, network_call_made=True,
            latency_ms=latency_ms, error_type="unknown_error",
            audit_event_id=audit.event_id,
            message="Unexpected error during dialogue preview generation.",
        )


def _get_provider_api_key(layout: RuntimeLayout | None = None) -> str | None:
    _, _, state = _load_state(layout)
    secrets = SecretStore(layout) if layout else None
    if not secrets:
        return None
    if not secrets.secret_configured(state.secret_storage, state.key_name):
        return None
    return secrets._fallback_get(state.key_name) or secrets._keyring_get(state.key_name)
