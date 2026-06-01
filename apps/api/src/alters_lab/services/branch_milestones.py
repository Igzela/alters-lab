"""Branch milestones storage service."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.branch_milestones import BranchMilestoneRecord
from alters_lab.services.p6_runtime import (
    list_records,
    read_record,
    write_record,
)


def save_milestone(
    record: BranchMilestoneRecord,
    repo_root: Path | None = None,
) -> Path:
    return write_record(
        "branch_milestones", record.milestone_id, record.model_dump(), repo_root
    )


def load_milestone(
    milestone_id: str,
    repo_root: Path | None = None,
) -> BranchMilestoneRecord:
    data = read_record("branch_milestones", milestone_id, repo_root)
    return BranchMilestoneRecord(**data)


def list_milestones(
    repo_root: Path | None = None,
) -> list[BranchMilestoneRecord]:
    return [
        BranchMilestoneRecord(**r)
        for r in list_records("branch_milestones", repo_root)
    ]
