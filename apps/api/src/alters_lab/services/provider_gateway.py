"""P5-M2 / P8-M1 Provider Gateway Boundary service.

All provider calls go through this single gateway. No feature module directly
imports provider SDKs. Default mode is mock.

P8-M1: Added real OpenAI-compatible HTTP provider integration.
Bridges to provider_config service for YAML-based config resolution.
"""

from __future__ import annotations

import os
import re

from alters_lab.schemas.provider_gateway import (
    ProviderConfigStatusResponse,
    ProviderGatewayHealthResponse,
    ProviderGatewayRequest,
    ProviderGatewayResponse,
)

VALID_MODES = {"mock", "disabled", "openai_compatible_http"}

ANTHROPIC_API_VERSION = "2023-06-01"

_MOCK_REPLIES = {
    "default": "I understand your question. As a mock provider, I'm simulating a thoughtful response based on the alter context provided.",
}


def _normalize_mode(value: str) -> str:
    """Normalize provider mode to internal canonical form (underscore)."""
    return value.replace("-", "_")


def _get_provider_mode() -> str:
    raw = os.environ.get("ALTERS_PROVIDER_MODE")
    if raw:
        return _normalize_mode(raw)
    config_mode = _resolve_config_value("mode")
    return _normalize_mode(config_mode) if config_mode else "mock"


def _get_provider_base_url() -> str | None:
    env_val = os.environ.get("ALTERS_PROVIDER_BASE_URL")
    if env_val:
        return env_val
    return _resolve_config_value("base_url")


def _get_provider_api_key() -> str | None:
    env_val = os.environ.get("ALTERS_PROVIDER_API_KEY")
    if env_val:
        return env_val
    return _resolve_secret()


def _get_provider_model() -> str:
    env_val = os.environ.get("ALTERS_PROVIDER_MODEL")
    if env_val:
        return env_val
    config_model = _resolve_config_value("model")
    return config_model or "mock-model"


def _resolve_config_value(field: str) -> str | None:
    """Resolve a config value from the provider config YAML, falling back to None."""
    try:
        from alters_lab.services.runtime_layout import resolve_runtime_layout, load_user_config
        layout = resolve_runtime_layout()
        config = load_user_config(layout)
        provider = config.get("provider", {})
        if not isinstance(provider, dict):
            return None
        # Check provider-level fields first (e.g., "mode")
        value = provider.get(field)
        if isinstance(value, str) and value:
            return value
        # Check openai_compatible_http sub-section
        openai = provider.get("openai_compatible_http", {})
        if not isinstance(openai, dict):
            return None
        value = openai.get(field)
        return value if isinstance(value, str) and value else None
    except Exception:
        return None


def _resolve_secret() -> str | None:
    """Resolve the API key from the secrets store (keyring or YAML fallback)."""
    try:
        from alters_lab.services.runtime_layout import resolve_runtime_layout
        from alters_lab.services.provider_config import SecretStore, _load_state
        layout = resolve_runtime_layout()
        _, _, state = _load_state(layout)
        store = SecretStore(layout)
        if store.secret_configured(state.secret_storage, state.key_name):
            return store.get_secret(state.secret_storage, state.key_name)
        return None
    except Exception:
        return None


def _redact_secrets(text: str) -> str:
    patterns = [
        r"sk-[A-Za-z0-9]{20,}",
        r"Bearer\s+[A-Za-z0-9._-]+",
        r"api[_-]?key\s*[:=]\s*\S+",
    ]
    result = text
    for pattern in patterns:
        result = re.sub(pattern, "[REDACTED]", result, flags=re.IGNORECASE)
    return result


def _count_redactions(original: str, redacted: str) -> int:
    return max(0, original.count("[REDACTED]") - redacted.count("[REDACTED]"))


def get_provider_gateway_health() -> ProviderGatewayHealthResponse:
    mode = _get_provider_mode()
    return ProviderGatewayHealthResponse(
        mode=mode,
        model=_get_provider_model(),
        api_key_configured=_get_provider_api_key() is not None,
    )


def get_provider_config_status() -> ProviderConfigStatusResponse:
    mode = _get_provider_mode()
    return ProviderConfigStatusResponse(
        mode=mode,
        model=_get_provider_model(),
        base_url_configured=_get_provider_base_url() is not None,
        api_key_configured=_get_provider_api_key() is not None,
    )


def provider_gateway_complete(request: ProviderGatewayRequest) -> ProviderGatewayResponse:
    mode = _get_provider_mode()

    if mode == "disabled":
        return ProviderGatewayResponse(
            status="disabled",
            mode=mode,
            model=_get_provider_model(),
            content="Provider gateway is disabled. Set ALTERS_PROVIDER_MODE to enable.",
            persisted=False,
            active_yaml_modified=False,
        )

    if mode == "mock" or mode not in VALID_MODES:
        content = _MOCK_REPLIES["default"]
        if request.messages:
            last_user = ""
            for msg in reversed(request.messages):
                if msg.get("role") == "user":
                    last_user = msg.get("content", "")
                    break
            if last_user:
                content = f"[Mock] Acknowledging: {last_user[:100]}"

        redacted = _redact_secrets(content)
        return ProviderGatewayResponse(
            status="mock_response",
            mode=mode,
            model=request.model or _get_provider_model(),
            content=redacted,
            usage={"prompt_tokens": 0, "completion_tokens": len(content.split()), "total_tokens": len(content.split())},
            redaction_summary={"fields_redacted": _count_redactions(content, redacted), "api_key_exposed": False},
            persisted=False,
            active_yaml_modified=False,
        )

    # openai_compatible_http mode
    base_url = _get_provider_base_url()
    api_key = _get_provider_api_key()
    if not base_url or not api_key:
        return ProviderGatewayResponse(
            status="error",
            mode=mode,
            model=_get_provider_model(),
            content="Provider mode requires base_url and api_key. Configure via ALTERS_PROVIDER_BASE_URL / ALTERS_PROVIDER_API_KEY env vars, or via /provider-config endpoints.",
            persisted=False,
            active_yaml_modified=False,
        )

    try:
        import httpx

        model = request.model or _get_provider_model()
        is_anthropic = "anthropic" in base_url.lower()
        timeout = float(_resolve_config_value("timeout_seconds") or 60)

        max_tokens = max(1, request.max_tokens) if request.max_tokens else 800
        temperature = request.temperature if request.temperature is not None else 0.2

        if is_anthropic:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": ANTHROPIC_API_VERSION,
                "Content-Type": "application/json",
            }
            system_msg = None
            user_messages = []
            for msg in request.messages:
                if msg.get("role") == "system":
                    system_msg = msg.get("content", "")
                else:
                    user_messages.append(msg)
            payload: dict = {
                "model": model,
                "messages": user_messages,
                "max_tokens": max_tokens,
            }
            if system_msg:
                payload["system"] = system_msg
            payload["temperature"] = temperature
            resp = httpx.post(f"{base_url}/v1/messages", json=payload, headers=headers, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            content = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    content += block.get("text", "")
            usage = data.get("usage")
        else:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": request.messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            resp = httpx.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage")
    except ModuleNotFoundError:
        return ProviderGatewayResponse(
            status="error",
            mode=mode,
            model=_get_provider_model(),
            content="httpx package not installed. Install with: pip install httpx",
            persisted=False,
            active_yaml_modified=False,
        )
    except Exception as exc:
        return ProviderGatewayResponse(
            status="error",
            mode=mode,
            model=_get_provider_model(),
            content=f"Provider request failed: {type(exc).__name__}",
            persisted=False,
            active_yaml_modified=False,
        )

    redacted_content = _redact_secrets(content)
    return ProviderGatewayResponse(
        status="provider_response",
        mode=mode,
        model=request.model or _get_provider_model(),
        content=redacted_content,
        usage=usage,
        redaction_summary={"fields_redacted": _count_redactions(content, redacted_content), "api_key_exposed": False},
        persisted=False,
        active_yaml_modified=False,
    )
