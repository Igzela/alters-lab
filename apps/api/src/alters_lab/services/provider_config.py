"""Local provider configuration service.

This module manages local configuration only. It never calls a provider and
never returns secret values.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from alters_lab.schemas.provider_config import (
    ProviderConfigResponse,
    ProviderConfigStatusResponse,
    ProviderConfigTestRequest,
    ProviderConfigTestResponse,
    ProviderConfigUpdateRequest,
    ProviderMode,
    ProviderSecretMutationResponse,
    SecretStorage,
)
from alters_lab.services.runtime_layout import (
    RuntimeLayout,
    default_config,
    ensure_secrets_fallback_file,
    load_user_config,
    resolve_runtime_layout,
    write_user_config,
)

DEFAULT_KEY_NAME = "alters-lab/provider-api-key"
VALID_PROVIDER_MODES = {"disabled", "mock", "openai-compatible-http"}
SAFETY_FLAGS = {
    "provider_output_persists_by_default": False,
    "provider_output_can_write_active_yaml": False,
    "provider_output_can_generate_reality_score": False,
    "p6_behavior_validated": False,
    "p6_sealed": False,
}


@dataclass(frozen=True)
class ProviderConfigState:
    mode: ProviderMode
    base_url: str | None
    model: str | None
    timeout_seconds: int
    secret_storage: SecretStorage
    key_name: str


class ProviderConfigError(ValueError):
    """Raised when a provider config mutation is invalid."""


class SecretStore:
    def __init__(self, layout: RuntimeLayout) -> None:
        self.layout = layout

    def keyring_available(self) -> bool:
        return importlib.util.find_spec("keyring") is not None

    def secret_configured(self, storage: SecretStorage, key_name: str) -> bool:
        if storage == "keyring" and self.keyring_available():
            return self._keyring_get(key_name) is not None
        return self._fallback_get(key_name) is not None

    def set_secret(self, storage: SecretStorage, key_name: str, value: str) -> SecretStorage:
        if storage == "keyring" and self.keyring_available():
            self._keyring_set(key_name, value)
            return "keyring"
        self._fallback_set(key_name, value)
        return "secrets_yaml_fallback"

    def delete_secret(self, storage: SecretStorage, key_name: str) -> SecretStorage:
        if storage == "keyring" and self.keyring_available():
            self._keyring_delete(key_name)
            return "keyring"
        self._fallback_delete(key_name)
        return "secrets_yaml_fallback"

    def _keyring_get(self, key_name: str) -> str | None:
        try:
            import keyring  # type: ignore[import-not-found]

            return keyring.get_password("alters-lab", key_name)
        except Exception:
            return None

    def _keyring_set(self, key_name: str, value: str) -> None:
        import keyring  # type: ignore[import-not-found]

        keyring.set_password("alters-lab", key_name, value)

    def _keyring_delete(self, key_name: str) -> None:
        try:
            import keyring  # type: ignore[import-not-found]

            keyring.delete_password("alters-lab", key_name)
        except Exception:
            return

    def _fallback_data(self, create: bool = False) -> dict[str, Any]:
        if not create and not self.layout.secrets_path.exists():
            return {"version": 1}
        path = ensure_secrets_fallback_file(self.layout)
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise ProviderConfigError("secrets fallback file is not a mapping")
        return data

    def _write_fallback_data(self, data: dict[str, Any]) -> Path:
        path = ensure_secrets_fallback_file(self.layout)
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        path.chmod(0o600)
        return path

    def _fallback_get(self, key_name: str) -> str | None:
        data = self._fallback_data(create=False)
        provider = data.get("provider")
        if not isinstance(provider, dict):
            return None
        value = provider.get(key_name)
        return value if isinstance(value, str) and value else None

    def _fallback_set(self, key_name: str, value: str) -> None:
        data = self._fallback_data(create=True)
        provider = data.setdefault("provider", {})
        if not isinstance(provider, dict):
            provider = {}
            data["provider"] = provider
        provider[key_name] = value
        self._write_fallback_data(data)

    def _fallback_delete(self, key_name: str) -> None:
        data = self._fallback_data(create=True)
        provider = data.get("provider")
        if isinstance(provider, dict):
            provider.pop(key_name, None)
        self._write_fallback_data(data)


def _provider_section(config: dict[str, Any]) -> dict[str, Any]:
    provider = config.setdefault("provider", {})
    if not isinstance(provider, dict):
        provider = {}
        config["provider"] = provider
    return provider


def _openai_section(provider: dict[str, Any]) -> dict[str, Any]:
    section = provider.setdefault("openai_compatible_http", {})
    if not isinstance(section, dict):
        section = {}
        provider["openai_compatible_http"] = section
    return section


def _secrets_section(provider: dict[str, Any]) -> dict[str, Any]:
    section = provider.setdefault("secrets", {})
    if not isinstance(section, dict):
        section = {}
        provider["secrets"] = section
    return section


def _normalize_mode(value: Any) -> ProviderMode:
    if value == "openai_compatible_http":
        value = "openai-compatible-http"
    if value not in VALID_PROVIDER_MODES:
        return "disabled"
    return value


def _load_state(layout: RuntimeLayout | None = None) -> tuple[RuntimeLayout, dict[str, Any], ProviderConfigState]:
    resolved_layout = layout or resolve_runtime_layout()
    config = load_user_config(resolved_layout)
    base = default_config(resolved_layout)
    provider = _provider_section(config)
    base_provider = base["provider"]
    openai = _openai_section(provider)
    base_openai = base_provider["openai_compatible_http"]
    secrets = _secrets_section(provider)
    base_secrets = base_provider["secrets"]
    state = ProviderConfigState(
        mode=_normalize_mode(provider.get("mode", base_provider["mode"])),
        base_url=openai.get("base_url") or base_openai["base_url"],
        model=openai.get("model") or base_openai["model"],
        timeout_seconds=int(openai.get("timeout_seconds") or base_openai["timeout_seconds"]),
        secret_storage=secrets.get("storage") or base_secrets["storage"],
        key_name=secrets.get("key_name") or base_secrets["key_name"],
    )
    return resolved_layout, config, state


def get_provider_config(layout: RuntimeLayout | None = None) -> ProviderConfigResponse:
    resolved_layout, _, state = _load_state(layout)
    return ProviderConfigResponse(
        mode=state.mode,
        base_url=state.base_url,
        model=state.model,
        timeout_seconds=state.timeout_seconds,
        secret_storage=state.secret_storage,
        key_name=state.key_name,
        keyring_available=SecretStore(resolved_layout).keyring_available(),
        **SAFETY_FLAGS,
    )


def get_provider_status(layout: RuntimeLayout | None = None) -> ProviderConfigStatusResponse:
    resolved_layout, _, state = _load_state(layout)
    secrets = SecretStore(resolved_layout)
    base_url_configured = bool(state.base_url)
    model_configured = bool(state.model)
    api_key_configured = secrets.secret_configured(state.secret_storage, state.key_name)
    configured = state.mode in {"disabled", "mock"} or (
        state.mode == "openai-compatible-http" and base_url_configured and model_configured and api_key_configured
    )
    return ProviderConfigStatusResponse(
        provider_mode=state.mode,
        configured=configured,
        base_url_configured=base_url_configured,
        model_configured=model_configured,
        api_key_configured=api_key_configured,
        secret_storage=state.secret_storage,
        keyring_available=secrets.keyring_available(),
        **SAFETY_FLAGS,
    )


def update_provider_config(
    request: ProviderConfigUpdateRequest,
    layout: RuntimeLayout | None = None,
) -> ProviderConfigResponse:
    if request.mode == "openai-compatible-http" and not request.explicit_user_configuration:
        raise ProviderConfigError("openai-compatible-http requires explicit_user_configuration=true")

    resolved_layout, config, _ = _load_state(layout)
    provider = _provider_section(config)
    openai = _openai_section(provider)
    secrets = _secrets_section(provider)

    provider["mode"] = request.mode
    openai["base_url"] = request.base_url
    openai["model"] = request.model
    openai["timeout_seconds"] = request.timeout_seconds
    secrets["storage"] = request.secret_storage
    secrets["key_name"] = request.key_name or DEFAULT_KEY_NAME
    config["safety"] = {
        "active_yaml_write_allowed": False,
        "rubric_write_allowed": False,
        "provider_output_persists_by_default": False,
        "provider_output_can_write_active_yaml": False,
    }

    write_user_config(resolved_layout, config)
    return get_provider_config(resolved_layout)


def store_provider_secret(
    api_key: str,
    storage: SecretStorage,
    confirmation: str,
    layout: RuntimeLayout | None = None,
) -> ProviderSecretMutationResponse:
    if confirmation != "store-secret":
        raise ProviderConfigError("secret storage requires confirmation=store-secret")
    resolved_layout, _, state = _load_state(layout)
    actual_storage = SecretStore(resolved_layout).set_secret(storage, state.key_name, api_key)
    return ProviderSecretMutationResponse(
        status="stored",
        api_key_configured=True,
        secret_storage=actual_storage,
    )


def delete_provider_secret(
    confirmation: str,
    storage: SecretStorage | None = None,
    layout: RuntimeLayout | None = None,
) -> ProviderSecretMutationResponse:
    if confirmation != "delete-secret":
        raise ProviderConfigError("secret deletion requires confirmation=delete-secret")
    resolved_layout, _, state = _load_state(layout)
    selected_storage = storage or state.secret_storage
    actual_storage = SecretStore(resolved_layout).delete_secret(selected_storage, state.key_name)
    return ProviderSecretMutationResponse(
        status="deleted",
        api_key_configured=False,
        secret_storage=actual_storage,
    )


def test_provider_config(
    request: ProviderConfigTestRequest,
    layout: RuntimeLayout | None = None,
) -> ProviderConfigTestResponse:
    status = get_provider_status(layout)
    if status.provider_mode == "disabled":
        return ProviderConfigTestResponse(
            status="skipped",
            provider_ready=False,
            provider_mode=status.provider_mode,
            dry_run=request.dry_run,
            message="Provider is disabled.",
            **SAFETY_FLAGS,
        )
    if status.provider_mode == "mock":
        return ProviderConfigTestResponse(
            status="ok",
            provider_ready=True,
            provider_mode=status.provider_mode,
            dry_run=request.dry_run,
            message="Mock provider is ready; no network call made.",
            **SAFETY_FLAGS,
        )
    if request.live_check:
        return ProviderConfigTestResponse(
            status="not_implemented",
            provider_ready=False,
            provider_mode=status.provider_mode,
            dry_run=request.dry_run,
            message="Live provider checks are not implemented in P7-M4.",
            **SAFETY_FLAGS,
        )
    if status.configured:
        return ProviderConfigTestResponse(
            status="configured",
            provider_ready=True,
            provider_mode=status.provider_mode,
            dry_run=True,
            message="Provider config is complete; dry-run made no network call.",
            **SAFETY_FLAGS,
        )
    return ProviderConfigTestResponse(
        status="misconfigured",
        provider_ready=False,
        provider_mode=status.provider_mode,
        dry_run=True,
        message="Provider config requires base_url, model, and API key.",
        **SAFETY_FLAGS,
    )
