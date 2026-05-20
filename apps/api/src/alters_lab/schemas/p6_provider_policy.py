"""P6-M9 explicit provider enablement policy schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


ProviderMode = Literal["mock", "disabled", "openai_compatible_http"]


class P6ProviderPolicyHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    component: str = "p6-provider-policy"
    default_safe: bool = True


class P6ProviderPolicyStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    mode: str
    default_safe: bool
    real_provider_explicit_only: bool = True
    weekly_review_runs_with_mock: bool = True
    api_key_configured: bool
    api_key_returned: bool = False
    provider_output_can_write_active_yaml: bool = False
    provider_output_can_auto_generate_reality_score: bool = False


class P6ProviderConfigValidationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: ProviderMode
    base_url_configured: bool = False
    api_key_configured: bool = False
    explicit_user_configuration: bool = False


class P6ProviderConfigValidationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    valid: bool
    mode: ProviderMode
    reasons: list[str]
    api_key_returned: bool = False
    active_yaml_modified: bool = False
