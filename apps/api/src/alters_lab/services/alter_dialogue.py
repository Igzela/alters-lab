"""Alter Dialogue Runtime — read-only dialogue context builder (P4-M1)."""

from __future__ import annotations

from pathlib import Path

from alters_lab.services import io

from alters_lab.schemas.alter_dialogue import (
    AlterDialogueBoundaryConfirmations,
    AlterDialogueContext,
    AlterDialoguePromptPacket,
    AlterDialogueRequest,
    AlterDialogueResponse,
)

VALID_ALTER_IDS = {"alter_A", "alter_B", "alter_C", "alter_D"}

ALTER_TO_BRANCH = {
    "alter_A": "branch_A",
    "alter_B": "branch_B",
    "alter_C": "branch_C",
    "alter_D": "branch_D",
}

ALLOWED_SCOPE = [
    "explain this alter's perspective",
    "help user reason from this alter's stance",
    "ask clarifying questions",
    "identify tradeoffs and tensions",
    "remain consistent with alter voice",
]

FORBIDDEN_SCOPE = [
    "write active YAML",
    "claim to be the real user",
    "override human choice",
    "invent new branch/alter semantics as confirmed",
    "trigger calibration/drift/archive",
    "call providers",
    "make irreversible recommendations",
]

FORBIDDEN_ALTER_FIELDS = {"provider", "runtime", "database", "frontend", "live_execution", "controlled_persist", "archive_trigger"}

SAFETY_BOUNDARIES = [
    "Dialogue is read-only — no active YAML will be written.",
    "Do not claim active state has changed.",
    "Do not make final life decisions for the user.",
    "Ask for clarification if user asks outside alter scope.",
    "provider_ready is false — no LLM provider will be called.",
]

STYLE_CONSTRAINTS = [
    "Stay grounded in core_stance, typical_concern, decision_style, self_warning.",
    "Do not write YAML.",
    "Do not make irreversible recommendations.",
    "Maintain persona consistency with the loaded alter.",
]


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def alter_dialogue_boundary_confirmations() -> dict:
    return AlterDialogueBoundaryConfirmations().model_dump()


def validate_alter_id(alter_id: str) -> None:
    if not alter_id or not isinstance(alter_id, str):
        raise ValueError("alter_id must be a non-empty string")
    if "/" in alter_id or "\\" in alter_id or ".." in alter_id:
        raise ValueError(f"Invalid alter_id: {alter_id}")
    if alter_id not in VALID_ALTER_IDS:
        raise ValueError(f"Invalid alter_id: {alter_id}. Must be one of: {', '.join(sorted(VALID_ALTER_IDS))}")


def load_active_alter(alter_id: str, repo_root: Path | None = None) -> dict:
    validate_alter_id(alter_id)
    root = repo_root or get_repo_root()
    alter_path = root / "alters" / "current" / "alters" / f"{alter_id}.yaml"
    if not alter_path.exists():
        raise FileNotFoundError(f"Active alter not found: {alter_path}")
    data = io.read_yaml(alter_path)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid alter YAML: {alter_path}")
    return data


def validate_active_alter_for_dialogue(alter: dict) -> dict:
    errors: list[str] = []

    alter_id = alter.get("id", "")
    if alter_id not in VALID_ALTER_IDS:
        errors.append(f"Invalid alter id: {alter_id}")

    expected_branch = ALTER_TO_BRANCH.get(alter_id, "")
    actual_branch = alter.get("branch_ref", "")
    if expected_branch and actual_branch != expected_branch:
        errors.append(f"branch_ref mismatch: expected {expected_branch}, got {actual_branch}")

    source_refs = alter.get("source_refs", {})
    if source_refs.get("snapshot_ref") != "alters/current/snapshot.yaml":
        errors.append(f"source_refs.snapshot_ref invalid: {source_refs.get('snapshot_ref')}")
    if source_refs.get("branches_ref") != "alters/current/branches.yaml":
        errors.append(f"source_refs.branches_ref invalid: {source_refs.get('branches_ref')}")
    if source_refs.get("rubric_ref") != "alters/calibration/rubric.yaml":
        errors.append(f"source_refs.rubric_ref invalid: {source_refs.get('rubric_ref')}")

    quality = alter.get("quality_status", {})
    if quality.get("human_confirmed") is not True:
        errors.append("quality_status.human_confirmed is not true")
    if quality.get("active") is not True:
        errors.append("quality_status.active is not true")

    voice = alter.get("voice", {})
    if not voice.get("core_stance"):
        errors.append("voice.core_stance is empty or missing")

    for field in FORBIDDEN_ALTER_FIELDS:
        if field in alter:
            errors.append(f"Forbidden top-level field present: {field}")

    return {"valid": len(errors) == 0, "errors": errors}


def build_alter_dialogue_context(alter: dict) -> AlterDialogueContext:
    voice = alter.get("voice", {})
    return AlterDialogueContext(
        alter_id=alter.get("id", ""),
        branch_ref=alter.get("branch_ref", ""),
        label=alter.get("label", ""),
        core_stance=voice.get("core_stance", ""),
        typical_concern=voice.get("typical_concern", ""),
        decision_style=voice.get("decision_style", ""),
        self_warning=voice.get("self_warning", ""),
        source_refs=alter.get("source_refs", {}),
        quality_status=alter.get("quality_status", {}),
        allowed_scope=list(ALLOWED_SCOPE),
        forbidden_scope=list(FORBIDDEN_SCOPE),
    )


def build_system_instruction(context: AlterDialogueContext) -> str:
    return (
        f"You are speaking as alter perspective '{context.alter_id}' ({context.label}), "
        "not as the whole user.\n\n"
        f"Core stance: {context.core_stance}\n"
        f"Typical concern: {context.typical_concern}\n"
        f"Decision style: {context.decision_style}\n"
        f"Self-warning: {context.self_warning}\n\n"
        "Stay grounded in this alter's voice. Do not claim active state has changed. "
        "Do not write YAML. Do not make final life decisions for the user. "
        "Ask for clarification if user asks outside alter scope. "
        "Dialogue is read-only and non-persistent. The full alter YAML is injected "
        "into the prompt packet; summary-only context is invalid."
    )


def build_prompt_packet(
    alter: dict,
    user_message: str,
) -> AlterDialoguePromptPacket:
    validation = validate_active_alter_for_dialogue(alter)
    if not validation["valid"]:
        raise ValueError(f"Alter validation failed: {'; '.join(validation['errors'])}")

    context = build_alter_dialogue_context(alter)
    system_instruction = build_system_instruction(context)

    context_summary = {
        "alter_id": context.alter_id,
        "branch_ref": context.branch_ref,
        "label": context.label,
        "core_stance": context.core_stance,
        "typical_concern": context.typical_concern,
        "decision_style": context.decision_style,
        "self_warning": context.self_warning,
    }

    return AlterDialoguePromptPacket(
        alter_id=context.alter_id,
        system_instruction=system_instruction,
        user_message=user_message,
        full_alter_yaml=dict(alter),
        full_context_injected=True,
        context_summary=context_summary,
        safety_boundaries=list(SAFETY_BOUNDARIES),
        style_constraints=list(STYLE_CONSTRAINTS),
        context_injection_policy="full_alter_yaml_required",
        persistence_policy="read_only_no_active_yaml_write",
        provider_ready=False,
    )


def list_active_alters(repo_root: Path | None = None) -> list[dict]:
    root = repo_root or get_repo_root()
    alters_dir = root / "alters" / "current" / "alters"
    results = []
    for alter_id in sorted(VALID_ALTER_IDS):
        alter_path = alters_dir / f"{alter_id}.yaml"
        if not alter_path.exists():
            continue
        data = io.read_yaml(alter_path)
        if not isinstance(data, dict):
            continue
        voice = data.get("voice", {})
        quality = data.get("quality_status", {})
        results.append({
            "alter_id": data.get("id", alter_id),
            "branch_ref": data.get("branch_ref", ""),
            "label": data.get("label", ""),
            "core_stance": voice.get("core_stance", ""),
            "active": quality.get("active", False),
            "human_confirmed": quality.get("human_confirmed", False),
        })
    return results


def build_dialogue_response(
    alter_id: str,
    request: AlterDialogueRequest,
    repo_root: Path | None = None,
) -> AlterDialogueResponse:
    bc = alter_dialogue_boundary_confirmations()

    validate_alter_id(alter_id)

    root = repo_root or get_repo_root()
    alter = load_active_alter(alter_id, root)

    validation = validate_active_alter_for_dialogue(alter)
    if not validation["valid"]:
        return AlterDialogueResponse(
            status="rejected",
            alter_id=alter_id,
            dialogue_context=None,
            prompt_packet=None,
            boundary_confirmations=bc,
        )

    context = build_alter_dialogue_context(alter)

    if request.include_context_packet:
        prompt_packet = build_prompt_packet(alter, request.user_message)
        return AlterDialogueResponse(
            status="prompt_packet_ready",
            alter_id=alter_id,
            dialogue_context=context,
            prompt_packet=prompt_packet,
            boundary_confirmations=bc,
        )

    return AlterDialogueResponse(
        status="context_ready",
        alter_id=alter_id,
        dialogue_context=context,
        prompt_packet=None,
        boundary_confirmations=bc,
    )
