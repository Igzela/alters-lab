"""Deterministic draft-only generation service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from alters_lab.schemas.generation_drafts import (
    AlterDraftCandidate,
    BranchDraftCandidate,
    DraftGeneratorInfo,
    GenerationBoundaryConfirmations,
    GenerationDraftPackage,
    GenerationSourceRefs,
)
from alters_lab.loaders.models import ActiveYamlChain
from alters_lab.services.controlled_write import append_jsonl_audit, sha256_text


def normalize_active_chain(active_chain: ActiveYamlChain | dict | None) -> dict:
    """Normalize active chain to dict shape, handling dataclass and wrapped YAML."""
    if active_chain is None:
        return {}
    if isinstance(active_chain, ActiveYamlChain):
        return {
            "snapshot": active_chain.snapshot,
            "branches": active_chain.branches,
            "alters": active_chain.alters,
            "value_alignment": active_chain.value_alignment,
            "dialogue": active_chain.dialogue,
            "reality_trace": active_chain.reality_trace,
        }
    return dict(active_chain)


def extract_snapshot_body(snapshot_doc: dict) -> dict:
    """Extract snapshot body from possibly wrapped YAML shape.

    Real YAML: {"snapshot": {"intake_status": {...}, "anchors": {...}, ...}}
    Returns the inner snapshot dict.
    """
    if "snapshot" in snapshot_doc and isinstance(snapshot_doc["snapshot"], dict):
        return snapshot_doc["snapshot"]
    return snapshot_doc


def extract_branch_list(branches_doc: dict) -> list[dict]:
    """Extract branches list from branches YAML document.

    Real YAML: {"branch_discovery": {...}, "branches": [...]}
    """
    return branches_doc.get("branches", [])


def generate_draft_id(prefix: str = "draft") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short = uuid.uuid4().hex[:8]
    return f"{prefix}_{ts}_{short}"


def generation_boundary_confirmations() -> dict:
    return GenerationBoundaryConfirmations().model_dump()


def validate_generation_inputs(active_chain: ActiveYamlChain | dict | None) -> dict:
    errors: list[str] = []
    chain = normalize_active_chain(active_chain)
    if not chain:
        return {"valid": False, "errors": ["active_chain is None"]}
    snapshot_doc = chain.get("snapshot", {})
    snapshot_body = extract_snapshot_body(snapshot_doc)
    if not snapshot_body:
        errors.append("snapshot missing")
    else:
        intake = snapshot_body.get("intake_status", {})
        if intake.get("phase") != "completed":
            errors.append("snapshot intake phase not completed")
    branches_doc = chain.get("branches", {})
    branch_list = extract_branch_list(branches_doc)
    if branch_list and len(branch_list) != 4:
        errors.append(f"expected 4 branches, got {len(branch_list)}")
    return {"valid": len(errors) == 0, "errors": errors}


BRANCH_TEMPLATES = [
    {
        "id": "branch_A",
        "label": "Single-Path Exam Commitment",
        "core_choice": "Commit fully to exam preparation as the primary life structure",
        "structural_commitment": "All scheduling and energy allocation oriented around exam milestones",
        "key_tension_resolved": "Uncertainty resolved by narrowing to one high-stakes path",
        "incompatible_with": ["branch_B", "branch_C", "branch_D"],
        "source_reasoning": [
            "Snapshot shows exam as dominant near-term constraint",
            "Anchors suggest clarity-seeking under pressure",
            "Tradeoff: depth vs breadth of life exploration",
        ],
    },
    {
        "id": "branch_B",
        "label": "Employment-First Engineering Path",
        "core_choice": "Prioritize employment outcomes over academic credentials",
        "structural_commitment": "Portfolio, interviews, and practical skills take scheduling priority",
        "key_tension_resolved": "Certification delay traded for immediate market entry",
        "incompatible_with": ["branch_A", "branch_C", "branch_D"],
        "source_reasoning": [
            "Snapshot shows engineering output as high-priority anchor",
            "Anchors suggest pragmatism and tangible results",
            "Tradeoff: credential security vs market timing",
        ],
    },
    {
        "id": "branch_C",
        "label": "Timeboxed Dual-Track Calibration",
        "core_choice": "Run exam and employment tracks in parallel for a fixed window",
        "structural_commitment": "Strict timebox with go/no-go decision at boundary",
        "key_tension_resolved": "Ambiguity preserved temporarily, resolved by deadline",
        "incompatible_with": ["branch_A", "branch_B", "branch_D"],
        "source_reasoning": [
            "Snapshot shows multiple competing anchors without clear hierarchy",
            "Anchors suggest evidence-based decision making",
            "Tradeoff: cognitive load vs option preservation",
        ],
    },
    {
        "id": "branch_D",
        "label": "Project-Closure-First Engineering Proof",
        "core_choice": "Complete a significant project as proof of capability before other commitments",
        "structural_commitment": "Project completion becomes the gating event for next decisions",
        "key_tension_resolved": "Ambition channeled into single demonstrable output",
        "incompatible_with": ["branch_A", "branch_B", "branch_C"],
        "source_reasoning": [
            "Snapshot shows desire for concrete evidence of ability",
            "Anchors suggest project-based learning preference",
            "Tradeoff: isolation for depth vs social proof timing",
        ],
    },
]


def generate_branch_drafts_from_snapshot(snapshot: dict) -> list[BranchDraftCandidate]:
    """Generate branch draft candidates. Accepts raw snapshot dict or snapshot body."""
    drafts = []
    for tmpl in BRANCH_TEMPLATES:
        drafts.append(BranchDraftCandidate(**tmpl))
    return drafts


def generate_alter_drafts_from_branches(branches: list[dict]) -> list[AlterDraftCandidate]:
    """Generate alter draft candidates from branch list."""
    alter_map = [
        ("alter_A", "branch_A", "Exam-Committed Alter"),
        ("alter_B", "branch_B", "Employment-First Alter"),
        ("alter_C", "branch_C", "Dual-Track Calibration Alter"),
        ("alter_D", "branch_D", "Project-Closure Alter"),
    ]
    stance_map = {
        "alter_A": "Structured, focused, exam-oriented",
        "alter_B": "Pragmatic, market-aware, output-driven",
        "alter_C": "Analytical, evidence-seeking, deadline-bound",
        "alter_D": "Deep-focus, project-oriented, proof-driven",
    }
    drafts = []
    for alter_id, branch_ref, label in alter_map:
        drafts.append(AlterDraftCandidate(
            id=alter_id,
            branch_ref=branch_ref,
            label=label,
            voice={"core_stance": stance_map[alter_id]},
        ))
    return drafts


def build_generation_draft_package(
    active_chain: ActiveYamlChain | dict | None,
    include_branches: bool,
    include_alters: bool,
    draft_id: str | None = None,
) -> GenerationDraftPackage:
    validation = validate_generation_inputs(active_chain)
    if not validation["valid"]:
        raise ValueError(f"Invalid generation inputs: {'; '.join(validation['errors'])}")

    if not include_branches and not include_alters:
        raise ValueError("At least one of include_branches or include_alters must be true")

    chain = normalize_active_chain(active_chain)
    snapshot_doc = chain.get("snapshot", {})
    snapshot_body = extract_snapshot_body(snapshot_doc)
    branches_doc = chain.get("branches", {})
    branch_list = extract_branch_list(branches_doc)

    branch_drafts = []
    alter_drafts = []

    if include_branches:
        branch_drafts = generate_branch_drafts_from_snapshot(snapshot_body)

    if include_alters:
        alter_drafts = generate_alter_drafts_from_branches(branch_list)

    draft_type = "cycle_package" if (include_branches and include_alters) else ("branches" if include_branches else "alters")

    return GenerationDraftPackage(
        draft_id=draft_id or generate_draft_id(),
        draft_type=draft_type,
        branch_drafts=branch_drafts,
        alter_drafts=alter_drafts,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def save_generation_draft_package(
    draft_package: GenerationDraftPackage,
    draft_workspace: Path,
    audit_log_path: Path,
    approval_token: str,
    caller: str = "api",
) -> dict:
    if not approval_token or not approval_token.strip():
        raise ValueError("approval_token must not be empty or whitespace-only")

    draft_dir = draft_workspace / draft_package.draft_id
    draft_dir.mkdir(parents=True, exist_ok=True)
    draft_path = draft_dir / "draft_package.yaml"

    from alters_lab.services import io
    io.write_model_yaml(draft_path, draft_package)

    audit_record = {
        "operation": "generation_draft_save",
        "draft_id": draft_package.draft_id,
        "draft_type": draft_package.draft_type,
        "target_path": str(draft_path),
        "approval_token_hash": sha256_text(approval_token),
        "caller": caller,
    }
    append_jsonl_audit(audit_log_path, audit_record)

    return {
        "status": "draft_saved",
        "draft_path": str(draft_path),
        "audit_log_path": str(audit_log_path),
    }


def preview_generation_draft(
    active_chain: ActiveYamlChain | dict | None,
    include_branches: bool,
    include_alters: bool,
) -> GenerationDraftPackage:
    return build_generation_draft_package(active_chain, include_branches, include_alters)


def list_generation_drafts(draft_workspace: Path) -> list[dict]:
    if not draft_workspace.exists():
        return []
    drafts = []
    for d in sorted(draft_workspace.iterdir()):
        if d.is_dir() and d.name.startswith("draft_"):
            pkg = d / "draft_package.yaml"
            drafts.append({
                "draft_id": d.name,
                "path": str(pkg),
                "exists": pkg.exists(),
            })
    return drafts
