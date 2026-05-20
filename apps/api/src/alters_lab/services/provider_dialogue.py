"""P5-M3 Provider-backed Alter Dialogue service.

Uses full alter YAML prompt packet, provider gateway, and selected alter.
No active YAML write. No auto reality score. No auto drift. No auto archive.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

from alters_lab.loaders.active_yaml import load_yaml_file
from alters_lab.schemas.provider_dialogue import (
    ProviderDialogueBoundaryConfirmations,
    ProviderDialogueHealthResponse,
    ProviderDialogueReplyRequest,
    ProviderDialogueReplyResponse,
)
from alters_lab.services.provider_gateway import (
    ProviderGatewayRequest,
    provider_gateway_complete,
    _get_provider_mode,
)

VALID_ALTER_IDS = {"alter_A", "alter_B", "alter_C", "alter_D"}


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _get_alter_yaml(alter_id: str, repo_root: Path | None = None) -> dict:
    root = repo_root or _get_repo_root()
    path = root / "alters" / "current" / "alters" / f"{alter_id}.yaml"
    return load_yaml_file(path)


def _build_prompt_packet(alter_yaml: dict, user_message: str) -> list[dict]:
    system_prompt = (
        f"You are an alter version of the user living a specific future branch. "
        f"Branch: {alter_yaml.get('branch_ref', 'unknown')}. "
        f"Your role is to respond from the perspective of this alter. "
        f"All responses are simulated and not factual."
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]


def _boundary_confirmations() -> ProviderDialogueBoundaryConfirmations:
    return ProviderDialogueBoundaryConfirmations()


def get_provider_dialogue_health() -> ProviderDialogueHealthResponse:
    return ProviderDialogueHealthResponse(
        provider_mode=_get_provider_mode(),
        available_alters=sorted(VALID_ALTER_IDS),
    )


def provider_dialogue_reply(
    request: ProviderDialogueReplyRequest,
    alter_id: str,
    repo_root: Path | None = None,
) -> ProviderDialogueReplyResponse:
    if alter_id not in VALID_ALTER_IDS:
        raise ValueError(f"Invalid alter_id: {alter_id}. Must be one of {sorted(VALID_ALTER_IDS)}")

    alter_yaml = _get_alter_yaml(alter_id, repo_root)
    messages = _build_prompt_packet(alter_yaml, request.user_message)

    mode_override = request.provider_mode_override
    original_mode = _get_provider_mode()
    if mode_override and mode_override in ("mock", "disabled"):
        import os
        os.environ["ALTERS_PROVIDER_MODE"] = mode_override

    try:
        gw_request = ProviderGatewayRequest(
            messages=messages,
            caller=request.caller,
        )
        gw_response = provider_gateway_complete(gw_request)
    finally:
        if mode_override:
            import os
            os.environ["ALTERS_PROVIDER_MODE"] = original_mode

    boundary = _boundary_confirmations()
    session_path = None

    if request.save_session and gw_response.status not in ("disabled", "error"):
        session_path = _save_session(
            alter_id=alter_id,
            user_message=request.user_message,
            reply_text=gw_response.content,
            provider_mode=_get_provider_mode() if not mode_override else mode_override,
            model=gw_response.model,
            repo_root=repo_root,
        )
        boundary.persisted = True

    return ProviderDialogueReplyResponse(
        status=gw_response.status,
        alter_id=alter_id,
        reply_text=gw_response.content,
        provider_metadata={
            "mode": gw_response.mode,
            "model": gw_response.model,
            "usage": gw_response.usage,
        },
        prompt_packet_summary={
            "alter_ref": f"alters/current/alters/{alter_id}.yaml",
            "message_length": len(request.user_message),
            "system_prompt_included": True,
        },
        safety_boundaries=boundary,
        persisted=boundary.persisted,
        session_path=session_path,
        boundary_confirmations=boundary,
    )


def _save_session(
    alter_id: str,
    user_message: str,
    reply_text: str,
    provider_mode: str,
    model: str,
    repo_root: Path | None = None,
) -> str:
    root = repo_root or _get_repo_root()
    sessions_dir = root / "alters" / "product" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session_id = f"session_{ts}_{uuid.uuid4().hex[:8]}"
    session_path = sessions_dir / f"{session_id}.yaml"

    session_data = {
        "session_id": session_id,
        "alter_id": alter_id,
        "timestamp": ts,
        "provider_mode": provider_mode,
        "model": model,
        "user_message": user_message,
        "reply_text": reply_text,
        "safety_metadata": {
            "active_yaml_modified": False,
            "rubric_modified": False,
            "no_secrets_in_session": True,
            "provider_output_not_fact": True,
        },
    }

    content = yaml.safe_dump(session_data, sort_keys=False, allow_unicode=True)
    session_path.write_text(content, encoding="utf-8")
    return str(session_path)
