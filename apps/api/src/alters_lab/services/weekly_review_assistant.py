"""Weekly review assistant service.

Advisory-only provider suggestions during weekly review flow.
Provider suggests; user decides and submits. Output is unverified,
non-persistent, and never auto-submitted.
"""

from __future__ import annotations

from typing import Callable

from alters_lab.schemas.provider_dialogue_preview import (
    ProviderDialoguePreviewRequest,
)
from alters_lab.schemas.provider_adapter import ProviderMode
from alters_lab.schemas.weekly_review_assistant import (
    RequestedHelp,
    WeeklyReviewAssistantAuditEvent,
    WeeklyReviewAssistantHealthResponse,
    WeeklyReviewAssistantRequest,
    WeeklyReviewAssistantResponse,
    WeeklyReviewAssistantStatusResponse,
)
from alters_lab.services.provider_config import (
    SecretStore,
    _load_state,
)
from alters_lab.services.provider_dialogue_preview import (
    LIVE_CONFIRMATION as PROVIDER_LIVE_CONFIRMATION,
    MOCK_PREVIEW,
    run_provider_dialogue_preview,
)
from alters_lab.services.runtime_layout import RuntimeLayout

LIVE_CONFIRMATION = "run-live-weekly-review-assistant"

SYSTEM_PROMPT = (
    "You are an assistant generating an unverified weekly review suggestion. "
    "Do not claim authority. Do not submit records. Do not score the user. "
    "Do not claim validation. Produce concise draft text only."
)

HELP_INSTRUCTIONS: dict[RequestedHelp, str] = {
    "summarize_facts": "Summarize the key observable facts from this weekly note.",
    "identify_friction": "Identify friction or avoidance points in this weekly note.",
    "draft_primary_correction": "Draft a primary next correction based on this weekly review context.",
    "suggest_supporting_actions": "Suggest 1-2 supporting actions for next week.",
    "challenge_avoidance": "Gently challenge any avoidance patterns you see in this note.",
    "general_review_suggestion": "Provide a general review suggestion based on the available context.",
}

MOCK_SUGGESTION = (
    "[mock weekly review assistant] This is a deterministic placeholder suggestion. "
    "No real provider was called. Output is unverified."
)


def _build_audit_event(
    *,
    provider_mode: ProviderMode,
    status: str,
    dry_run: bool,
    live_generation: bool,
    network_call_made: bool,
    status_code: int | None = None,
    latency_ms: int | None = None,
    error_type: str | None = None,
) -> WeeklyReviewAssistantAuditEvent:
    return WeeklyReviewAssistantAuditEvent(
        provider_mode=provider_mode,
        status=status,
        dry_run=dry_run,
        live_generation=live_generation,
        network_call_made=network_call_made,
        status_code=status_code,
        latency_ms=latency_ms,
        error_type=error_type,
    )


def _build_user_prompt(request: WeeklyReviewAssistantRequest) -> str:
    parts: list[str] = []

    instruction = HELP_INSTRUCTIONS.get(request.requested_help, HELP_INSTRUCTIONS["general_review_suggestion"])
    parts.append(f"Task: {instruction}")

    if request.raw_note_excerpt:
        parts.append(f"Weekly note excerpt:\n{request.raw_note_excerpt}")

    if request.review_context:
        parts.append(f"Review context:\n{request.review_context}")

    return "\n\n".join(parts)


def _load_weekly_note_context(
    record_id: str,
    layout: RuntimeLayout | None = None,
) -> str | None:
    from alters_lab.services.obsidian_weekly_note import load_weekly_note_record

    try:
        _, _, state = _load_state(layout)
        from alters_lab.services.p6_runtime import runtime_dir
        repo_root = runtime_dir(layout) if layout else None
        record = load_weekly_note_record(record_id, repo_root)
        return (
            f"Session type: {record.session_type}\n"
            f"Observable facts: {'; '.join(record.observable_facts)}\n"
            f"Subjective state: {record.subjective_state}\n"
            f"Primary problem: {record.primary_problem}\n"
            f"Friction/avoidance: {record.friction_or_avoidance_point}\n"
            f"Desired correction: {record.desired_correction}"
        )
    except Exception:
        return None


def _load_review_session_context(
    session_id: str,
    layout: RuntimeLayout | None = None,
) -> str | None:
    from alters_lab.services.weekly_review_session import load_weekly_review_session

    try:
        from alters_lab.services.p6_runtime import runtime_dir
        repo_root = runtime_dir(layout) if layout else None
        session = load_weekly_review_session(session_id, repo_root)
        parts = [f"Session type: {session.session_type}", f"Status: {session.status}"]
        if session.review_note:
            parts.append(f"Review note: {session.review_note}")
        if session.next_week_primary_correction:
            parts.append(f"Primary correction: {session.next_week_primary_correction}")
        return "\n".join(parts)
    except Exception:
        return None


def build_weekly_review_assistant_health() -> WeeklyReviewAssistantHealthResponse:
    return WeeklyReviewAssistantHealthResponse()


def build_weekly_review_assistant_status(
    layout: RuntimeLayout | None = None,
) -> WeeklyReviewAssistantStatusResponse:
    resolved_layout, _, state = _load_state(layout)
    secrets = SecretStore(resolved_layout)
    key_configured = secrets.secret_configured(state.secret_storage, state.key_name)
    configured = state.mode in {"disabled", "mock"} or (
        state.mode == "openai-compatible-http"
        and bool(state.base_url) and bool(state.model) and key_configured
    )
    return WeeklyReviewAssistantStatusResponse(
        provider_mode=state.mode,
        configured=configured,
    )


def run_weekly_review_assistant(
    request: WeeklyReviewAssistantRequest,
    layout: RuntimeLayout | None = None,
    http_client: Callable | None = None,
) -> WeeklyReviewAssistantResponse:
    resolved_layout, _, state = _load_state(layout)
    saved_mode = state.mode

    # Block: save_suggestion=true in P8-M4
    if request.save_suggestion:
        audit = _build_audit_event(
            provider_mode=saved_mode, status="blocked",
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
        )
        return WeeklyReviewAssistantResponse(
            status="blocked", provider_mode=saved_mode, configured=True,
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
            audit_event_id=audit.event_id,
            message="save_suggestion is not supported in P8-M4.",
        )

    # request.mode=openai-compatible-http but saved config is not
    if (request.provider_mode or saved_mode) == "openai-compatible-http" and saved_mode != "openai-compatible-http":
        audit = _build_audit_event(
            provider_mode=saved_mode, status="blocked",
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
        )
        return WeeklyReviewAssistantResponse(
            status="blocked", provider_mode=saved_mode, configured=False,
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
            audit_event_id=audit.event_id,
            message="Real provider suggestion requires saved provider mode openai-compatible-http.",
        )

    # request.provider_mode=disabled is always safe
    if request.provider_mode == "disabled":
        audit = _build_audit_event(
            provider_mode="disabled", status="skipped",
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
        )
        return WeeklyReviewAssistantResponse(
            status="skipped", provider_mode="disabled", configured=True,
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
            audit_event_id=audit.event_id, message="Weekly review assistant disabled by request mode.",
        )

    if saved_mode == "disabled":
        audit = _build_audit_event(
            provider_mode="disabled", status="skipped",
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
        )
        return WeeklyReviewAssistantResponse(
            status="skipped", provider_mode="disabled", configured=True,
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
            audit_event_id=audit.event_id, message="Provider is disabled.",
        )

    if saved_mode == "mock":
        audit = _build_audit_event(
            provider_mode="mock", status="ok",
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
        )
        return WeeklyReviewAssistantResponse(
            status="ok", provider_mode="mock", configured=True,
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
            suggestion=MOCK_SUGGESTION, audit_event_id=audit.event_id,
            message="Mock weekly review assistant suggestion. No network call made.",
        )

    # request.provider_mode=mock overrides saved openai for preview only
    if request.provider_mode == "mock":
        audit = _build_audit_event(
            provider_mode="mock", status="ok",
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
        )
        return WeeklyReviewAssistantResponse(
            status="ok", provider_mode="mock", configured=True,
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
            suggestion=MOCK_SUGGESTION, audit_event_id=audit.event_id,
            message="Mock weekly review assistant suggestion. No network call made.",
        )

    # openai-compatible-http path
    secrets = SecretStore(resolved_layout)
    key_configured = secrets.secret_configured(state.secret_storage, state.key_name)
    configured = bool(state.base_url) and bool(state.model) and key_configured

    if not configured:
        audit = _build_audit_event(
            provider_mode="openai-compatible-http", status="blocked",
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
        )
        return WeeklyReviewAssistantResponse(
            status="blocked", provider_mode="openai-compatible-http", configured=False,
            dry_run=request.dry_run, live_generation=False, network_call_made=False,
            audit_event_id=audit.event_id,
            message="openai-compatible-http is not configured. Set base_url, model, and API key.",
        )

    if request.dry_run:
        audit = _build_audit_event(
            provider_mode="openai-compatible-http", status="ok",
            dry_run=True, live_generation=False, network_call_made=False,
        )
        return WeeklyReviewAssistantResponse(
            status="ok", provider_mode="openai-compatible-http", configured=True,
            dry_run=True, live_generation=False, network_call_made=False,
            suggestion="[dry-run] Weekly review assistant would generate suggestion here. No network call made.",
            audit_event_id=audit.event_id, message="Dry-run weekly review assistant. No network call made.",
        )

    if not request.live_generation:
        audit = _build_audit_event(
            provider_mode="openai-compatible-http", status="blocked",
            dry_run=False, live_generation=False, network_call_made=False,
        )
        return WeeklyReviewAssistantResponse(
            status="blocked", provider_mode="openai-compatible-http", configured=True,
            dry_run=False, live_generation=False, network_call_made=False,
            audit_event_id=audit.event_id,
            message="Live generation requires live_generation=true and exact confirmation.",
        )

    if request.confirmation != LIVE_CONFIRMATION:
        audit = _build_audit_event(
            provider_mode="openai-compatible-http", status="blocked",
            dry_run=False, live_generation=True, network_call_made=False,
        )
        return WeeklyReviewAssistantResponse(
            status="blocked", provider_mode="openai-compatible-http", configured=True,
            dry_run=False, live_generation=True, network_call_made=False,
            audit_event_id=audit.event_id,
            message=f"Live generation requires confirmation='{LIVE_CONFIRMATION}'.",
        )

    # Build context from provided IDs
    context_parts: list[str] = []
    if request.weekly_note_record_id:
        note_ctx = _load_weekly_note_context(request.weekly_note_record_id, layout)
        if note_ctx:
            context_parts.append(note_ctx)
    if request.weekly_review_session_id:
        session_ctx = _load_review_session_context(request.weekly_review_session_id, layout)
        if session_ctx:
            context_parts.append(session_ctx)
    if request.raw_note_excerpt:
        context_parts.append(f"User-provided note excerpt:\n{request.raw_note_excerpt}")
    if request.review_context:
        context_parts.append(f"Review context:\n{request.review_context}")

    user_prompt = _build_user_prompt(request)
    if context_parts:
        user_prompt = "\n\n".join(context_parts) + "\n\n" + user_prompt

    # Delegate to provider_dialogue_preview with its own confirmation
    preview_request = ProviderDialoguePreviewRequest(
        prompt=user_prompt,
        system_prompt=SYSTEM_PROMPT,
        dry_run=False,
        live_generation=True,
        confirmation=PROVIDER_LIVE_CONFIRMATION,
    )

    preview_response = run_provider_dialogue_preview(preview_request, layout, http_client)

    audit = _build_audit_event(
        provider_mode=preview_response.provider_mode,
        status=preview_response.status,
        dry_run=False,
        live_generation=True,
        network_call_made=preview_response.network_call_made,
        status_code=preview_response.status_code,
        latency_ms=preview_response.latency_ms,
        error_type=preview_response.error_type,
    )

    return WeeklyReviewAssistantResponse(
        status=preview_response.status,
        configured=True,
        suggestion=preview_response.output_preview,
        provider_mode=preview_response.provider_mode,
        dry_run=False,
        live_generation=True,
        network_call_made=preview_response.network_call_made,
        status_code=preview_response.status_code,
        latency_ms=preview_response.latency_ms,
        error_type=preview_response.error_type,
        audit_event_id=audit.event_id,
        message=preview_response.message,
    )
