"""P6-M9 explicit provider enablement policy service."""

from __future__ import annotations

from alters_lab.schemas.p6_provider_policy import (
    P6ProviderConfigValidationRequest,
    P6ProviderConfigValidationResponse,
    P6ProviderPolicyStatusResponse,
)
from alters_lab.services.provider_gateway import _get_provider_api_key, _get_provider_mode


def get_p6_provider_policy_status() -> P6ProviderPolicyStatusResponse:
    mode = _get_provider_mode()
    return P6ProviderPolicyStatusResponse(
        mode=mode,
        default_safe=mode in ("mock", "disabled"),
        api_key_configured=_get_provider_api_key() is not None,
    )


def validate_p6_provider_config(
    request: P6ProviderConfigValidationRequest,
) -> P6ProviderConfigValidationResponse:
    reasons: list[str] = []
    if request.mode in ("mock", "disabled"):
        reasons.append("mock/disabled mode is safe for weekly review")
        return P6ProviderConfigValidationResponse(status="ok", valid=True, mode=request.mode, reasons=reasons)

    if not request.explicit_user_configuration:
        reasons.append("real provider mode requires explicit_user_configuration=true")
    if not request.base_url_configured:
        reasons.append("real provider mode requires base_url_configured=true")
    if not request.api_key_configured:
        reasons.append("real provider mode requires api_key_configured=true")
    valid = not reasons
    return P6ProviderConfigValidationResponse(
        status="ok" if valid else "rejected",
        valid=valid,
        mode=request.mode,
        reasons=reasons or ["real provider configuration is explicit and complete"],
    )
