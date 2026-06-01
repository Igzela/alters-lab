"""Tests for milestone validation in weekly behavior records."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from alters_lab.schemas.behavior_metrics_record import WeeklyBehaviorMetricsRecord
from alters_lab.schemas.branch_milestones import BranchMilestoneRecord
from alters_lab.services.behavior_metrics import (
    build_weekly_record,
    validate_milestone_reference,
)
from alters_lab.services.branch_milestones import save_milestone


def _setup_catalog(tmp_path: Path) -> None:
    catalog_dir = tmp_path / "alters" / "product" / "behavior_metrics" / "catalog"
    catalog_dir.mkdir(parents=True)
    catalog = {
        "behavior_metric_set": {
            "id": "test_set",
            "version": "0.1",
            "created_at": "2026-01-01T00:00:00Z",
            "metrics": [
                {"id": "key_milestone_progress", "domain": "milestone", "label": "MP", "unit": "ratio", "aggregation": "last"},
            ],
        }
    }
    (catalog_dir / "behavior_metric_set_v0_2.yaml").write_text(
        yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8"
    )


def _make_milestone(
    milestone_id: str = "ms_001", branch_id: str = "branch_A"
) -> BranchMilestoneRecord:
    return BranchMilestoneRecord(
        milestone_id=milestone_id,
        branch_id=branch_id,
        title="Ship feature X",
        target_completion_date="2026-06-30",
        observable_done_definition="Feature deployed",
        created_at="2026-06-01T00:00:00Z",
    )


def test_milestone_id_must_exist(tmp_path: Path):
    _setup_catalog(tmp_path)
    record = WeeklyBehaviorMetricsRecord(
        record_id="wr_001",
        week_start="2026-05-25",
        week_end="2026-05-31",
        key_milestone_progress_pct=0.5,
        milestone_id="nonexistent",
        milestone_observable_evidence="some evidence",
    )
    with pytest.raises(ValueError, match="does not exist"):
        validate_milestone_reference(record, repo_root=tmp_path)


def test_branch_id_mismatch_rejected(tmp_path: Path):
    _setup_catalog(tmp_path)
    save_milestone(_make_milestone(branch_id="branch_A"), repo_root=tmp_path)

    record = WeeklyBehaviorMetricsRecord(
        record_id="wr_002",
        week_start="2026-05-25",
        week_end="2026-05-31",
        branch_id="branch_B",
        key_milestone_progress_pct=0.3,
        milestone_id="ms_001",
        milestone_observable_evidence="some evidence",
    )
    with pytest.raises(ValueError, match="branch_id mismatch"):
        validate_milestone_reference(record, repo_root=tmp_path)


def test_valid_milestone_reference_passes(tmp_path: Path):
    _setup_catalog(tmp_path)
    save_milestone(_make_milestone(branch_id="branch_A"), repo_root=tmp_path)

    record = WeeklyBehaviorMetricsRecord(
        record_id="wr_003",
        week_start="2026-05-25",
        week_end="2026-05-31",
        branch_id="branch_A",
        key_milestone_progress_pct=0.5,
        milestone_id="ms_001",
        milestone_observable_evidence="deployed to staging",
    )
    validate_milestone_reference(record, repo_root=tmp_path)


def test_no_milestone_id_skips_validation(tmp_path: Path):
    _setup_catalog(tmp_path)
    record = WeeklyBehaviorMetricsRecord(
        record_id="wr_004",
        week_start="2026-05-25",
        week_end="2026-05-31",
    )
    validate_milestone_reference(record, repo_root=tmp_path)
