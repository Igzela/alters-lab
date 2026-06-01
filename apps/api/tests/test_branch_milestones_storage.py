"""Tests for branch milestones storage service."""

from __future__ import annotations

from pathlib import Path

import pytest

from alters_lab.schemas.branch_milestones import BranchMilestoneRecord
from alters_lab.services.branch_milestones import (
    list_milestones,
    load_milestone,
    save_milestone,
)


def _make_milestone(milestone_id: str = "ms_001") -> BranchMilestoneRecord:
    return BranchMilestoneRecord(
        milestone_id=milestone_id,
        branch_id="branch_A",
        title="Ship feature X",
        target_completion_date="2026-06-30",
        observable_done_definition="Feature deployed to production",
        created_at="2026-06-01T00:00:00Z",
    )


def test_save_and_load(tmp_path: Path):
    record = _make_milestone()
    path = save_milestone(record, repo_root=tmp_path)
    assert path.exists()

    loaded = load_milestone("ms_001", repo_root=tmp_path)
    assert loaded.milestone_id == "ms_001"
    assert loaded.branch_id == "branch_A"


def test_list_milestones(tmp_path: Path):
    for i in range(2):
        save_milestone(_make_milestone(f"ms_{i:03d}"), repo_root=tmp_path)

    milestones = list_milestones(repo_root=tmp_path)
    assert len(milestones) == 2


def test_load_nonexistent_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_milestone("nonexistent", repo_root=tmp_path)
