"""Branch outcome targets service — save/load/evaluate objective targets."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.branch_outcome_targets import (
    BranchOutcomeTargetRecord,
    evaluate_target,
)
from alters_lab.services.p6_runtime import (
    list_records,
    read_record,
    write_record,
)

AREA = "branch_outcome_targets"


def save_target(record: BranchOutcomeTargetRecord, repo_root: Path | None = None) -> Path:
    data = record.model_dump(mode="json")
    return write_record(AREA, record.target_id, data, repo_root=repo_root)


def load_target(target_id: str, repo_root: Path | None = None) -> BranchOutcomeTargetRecord:
    data = read_record(AREA, target_id, repo_root=repo_root)
    return BranchOutcomeTargetRecord(**data)


def list_targets(repo_root: Path | None = None) -> list[BranchOutcomeTargetRecord]:
    records = list_records(AREA, repo_root=repo_root)
    return [BranchOutcomeTargetRecord(**r) for r in records]


def list_targets_for_branch(branch_id: str, repo_root: Path | None = None) -> list[BranchOutcomeTargetRecord]:
    return [t for t in list_targets(repo_root=repo_root) if t.branch_id == branch_id]


def evaluate_existing_target(
    target_id: str,
    final_observed_value: str,
    achieved: bool,
    repo_root: Path | None = None,
) -> BranchOutcomeTargetRecord:
    record = load_target(target_id, repo_root=repo_root)
    if record.status not in ("planned", "active"):
        raise ValueError(f"Cannot evaluate target in status '{record.status}'")
    evaluated = evaluate_target(record, final_observed_value, achieved)
    save_target(evaluated, repo_root=repo_root)
    return evaluated
