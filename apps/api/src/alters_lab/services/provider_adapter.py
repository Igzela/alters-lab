"""Provider adapter contract service.

Separated from provider_config and provider_gateway. This module defines the
hardened contract layer for provider adapter operations. It never calls real
providers, never writes active YAML, and never creates scores.
"""

from __future__ import annotations

from alters_lab.schemas.provider_adapter import (
    AdapterStatus,
    ProviderAdapterHealthResponse,
    ProviderAdapterRequest,
    ProviderAdapterResponse,
    ProviderAdapterStatusResponse,
    ProviderAuditEvent,
    ProviderMode,
)
from alters_lab.services.provider_config import (
    get_provider_status,
)
from alters_lab.services.runtime_layout import RuntimeLayout

MOCK_PREVIEW = (
    "[mock adapter preview] This is a deterministic placeholder response "
    "from the provider adapter. No real provider was called."
)

ACTIVE_YAML_MODIFIED = False
RUBRIC_MODIFIED = False
REALITY_SCORE_CREATED = False
ACTION_ALIGNMENT_CREATED = False
BEHAVIOR_VALIDATED = False
P6_SEALED = False
REAL_NETWORK_CALLS_ENABLED = False


def build_provider_adapter_health() -> ProviderAdapterHealthResponse:
    return ProviderAdapterHealthResponse()


def build_provider_adapter_status(
    layout: RuntimeLayout | None = None,
) -> ProviderAdapterStatusResponse:
    status = get_provider_status(layout)
    return ProviderAdapterStatusResponse(
        provider_mode=status.provider_mode,
        configured=status.configured,
        real_network_calls_enabled=REAL_NETWORK_CALLS_ENABLED,
        provider_output_persists_by_default=False,
        provider_output_can_write_active_yaml=False,
        provider_output_can_generate_reality_score=False,
        provider_output_can_generate_action_alignment=False,
        behavior_validated=BEHAVIOR_VALIDATED,
        p6_sealed=P6_SEALED,
    )


def build_provider_audit_event(
    *,
    provider_mode: ProviderMode,
    operation: str,
    status: AdapterStatus,
    dry_run: bool,
    live_check: bool,
    network_call_made: bool,
    output_persisted: bool,
    latency_ms: int | None = None,
    error_type: str | None = None,
) -> ProviderAuditEvent:
    return ProviderAuditEvent(
        provider_mode=provider_mode,
        operation=operation,
        status=status,
        dry_run=dry_run,
        live_check=live_check,
        network_call_made=network_call_made,
        output_persisted=output_persisted,
        latency_ms=latency_ms,
        error_type=error_type,
    )


def redact_provider_error(exc: Exception) -> str:
    return f"provider_adapter_error: {type(exc).__name__}"


def validate_provider_request(request: ProviderAdapterRequest) -> str | None:
    if request.live_check:
        return "blocked"
    if request.persist_output:
        return "blocked"
    return None


def run_provider_adapter(
    request: ProviderAdapterRequest,
    layout: RuntimeLayout | None = None,
) -> ProviderAdapterResponse:
    block_reason = validate_provider_request(request)
    if block_reason == "blocked":
        if request.live_check:
            audit = build_provider_audit_event(
                provider_mode=request.mode,
                operation="preview",
                status="blocked",
                dry_run=request.dry_run,
                live_check=True,
                network_call_made=False,
                output_persisted=False,
            )
            return ProviderAdapterResponse(
                status="blocked",
                provider_ready=False,
                provider_mode=request.mode,
                dry_run=request.dry_run,
                live_check=True,
                network_call_made=False,
                audit_event_id=audit.event_id,
                message="live_check is not implemented in P8-M1. P8-M2 owns real connectivity.",
            )
        if request.persist_output:
            audit = build_provider_audit_event(
                provider_mode=request.mode,
                operation="preview",
                status="blocked",
                dry_run=request.dry_run,
                live_check=False,
                network_call_made=False,
                output_persisted=False,
            )
            return ProviderAdapterResponse(
                status="blocked",
                provider_ready=False,
                provider_mode=request.mode,
                dry_run=request.dry_run,
                live_check=False,
                network_call_made=False,
                audit_event_id=audit.event_id,
                message="persist_output is not supported in P8-M1.",
            )

    if request.mode == "disabled":
        audit = build_provider_audit_event(
            provider_mode="disabled",
            operation="preview",
            status="skipped",
            dry_run=request.dry_run,
            live_check=False,
            network_call_made=False,
            output_persisted=False,
        )
        return ProviderAdapterResponse(
            status="skipped",
            provider_ready=False,
            provider_mode="disabled",
            dry_run=request.dry_run,
            live_check=False,
            network_call_made=False,
            audit_event_id=audit.event_id,
            message="Provider is disabled.",
        )

    if request.mode == "mock":
        audit = build_provider_audit_event(
            provider_mode="mock",
            operation="preview",
            status="ok",
            dry_run=request.dry_run,
            live_check=False,
            network_call_made=False,
            output_persisted=False,
        )
        return ProviderAdapterResponse(
            status="ok",
            provider_ready=True,
            provider_mode="mock",
            dry_run=request.dry_run,
            live_check=False,
            network_call_made=False,
            output_preview=MOCK_PREVIEW,
            audit_event_id=audit.event_id,
            message="Mock adapter preview returned. No network call made.",
        )

    if request.mode == "openai-compatible-http":
        config_status = get_provider_status(layout)
        configured = config_status.configured
        audit = build_provider_audit_event(
            provider_mode="openai-compatible-http",
            operation="preview",
            status="blocked" if not configured else "ok",
            dry_run=request.dry_run,
            live_check=False,
            network_call_made=False,
            output_persisted=False,
        )
        if not configured:
            return ProviderAdapterResponse(
                status="blocked",
                provider_ready=False,
                provider_mode="openai-compatible-http",
                dry_run=request.dry_run,
                live_check=False,
                network_call_made=False,
                audit_event_id=audit.event_id,
                message="openai-compatible-http is not configured. Configure provider config first.",
            )
        return ProviderAdapterResponse(
            status="ok",
            provider_ready=True,
            provider_mode="openai-compatible-http",
            dry_run=request.dry_run,
            live_check=False,
            network_call_made=False,
            output_preview="[dry-run] Provider would be called in P8-M2+. No network call made in P8-M1.",
            audit_event_id=audit.event_id,
            message="openai-compatible-http dry-run preview. No network call made. P8-M2 owns real connectivity.",
        )

    audit = build_provider_audit_event(
        provider_mode=request.mode,
        operation="preview",
        status="error",
        dry_run=request.dry_run,
        live_check=False,
        network_call_made=False,
        output_persisted=False,
        error_type="unknown_mode",
    )
    return ProviderAdapterResponse(
        status="error",
        provider_ready=False,
        provider_mode=request.mode,
        dry_run=request.dry_run,
        live_check=False,
        network_call_made=False,
        audit_event_id=audit.event_id,
        error_type="unknown_mode",
        message=f"Unknown provider mode: {request.mode}",
    )
