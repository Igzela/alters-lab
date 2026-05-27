"""Schemas for local provider configuration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ProviderMode = Literal["disabled", "mock", "openai-compatible-http"]
SecretStorage = Literal["keyring", "secrets_yaml_fallback"]


class ProviderSafetyFlags(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_output_persists_by_default: Literal[False] = False
    provider_output_can_write_active_yaml: Literal[False] = False
    provider_output_can_generate_reality_score: Literal[False] = False
    p6_behavior_validated: Literal[False] = False
    p6_sealed: Literal[False] = False


class ProviderConfigHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "provider-config"
    real_provider_default_enabled: bool = False
    secrets_redacted: bool = True


class ProviderConfigStatusResponse(ProviderSafetyFlags):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    provider_mode: ProviderMode
    configured: bool
    base_url_configured: bool
    model_configured: bool
    api_key_configured: bool
    secret_storage: SecretStorage
    keyring_available: bool = False
    secrets_redacted: bool = True


class ProviderConfigResponse(ProviderSafetyFlags):
    model_config = ConfigDict(extra="forbid")

    mode: ProviderMode
    base_url: str | None = None
    model: str | None = None
    timeout_seconds: int = Field(default=60, ge=1, le=600)
    secret_storage: SecretStorage = "keyring"
    key_name: str = "alters-lab/provider-api-key"
    keyring_available: bool = False
    secrets_redacted: bool = True


class ProviderConfigUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: ProviderMode
    base_url: str | None = None
    model: str | None = None
    timeout_seconds: int = Field(default=60, ge=1, le=600)
    secret_storage: SecretStorage = "keyring"
    key_name: str = "alters-lab/provider-api-key"
    explicit_user_configuration: bool = False

    @field_validator("base_url", "model", "key_name")
    @classmethod
    def trim_optional_string(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class ProviderSecretUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(min_length=1)
    storage: SecretStorage = "secrets_yaml_fallback"
    confirmation: str

    @field_validator("api_key")
    @classmethod
    def trim_api_key(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("api_key must not be empty")
        return stripped


class ProviderSecretDeleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    storage: SecretStorage | None = None
    confirmation: str


class ProviderSecretMutationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    api_key_configured: bool
    secret_storage: SecretStorage
    secrets_redacted: bool = True


class ProviderConfigTestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool = True
    live_check: bool = False


class ProviderConfigTestResponse(ProviderSafetyFlags):
    model_config = ConfigDict(extra="forbid")

    status: str
    provider_ready: bool
    provider_mode: ProviderMode
    dry_run: bool = True
    live_check_supported: bool = False
    message: str
    network_call_made: Literal[False] = False
    secrets_redacted: bool = True
