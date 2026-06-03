"""Tests for the unified DataRepo data access layer."""

from __future__ import annotations

import pytest
from pathlib import Path

from alters_lab.repositories.data_repo import DataRepo


@pytest.fixture
def repo(tmp_path: Path) -> DataRepo:
    """Create a DataRepo rooted at a temporary directory."""
    from alters_lab.services.runtime_layout import RuntimeLayout
    layout = RuntimeLayout(
        mode="dev",
        app_root=tmp_path,
        repo_root=tmp_path,
        config_dir=tmp_path / "config",
        config_path=tmp_path / "config" / "config.yaml",
        data_dir=tmp_path / "data",
        product_data_dir=tmp_path / "alters" / "product",
        state_dir=tmp_path / "state",
        logs_dir=tmp_path / "logs",
        secrets_path=tmp_path / "secrets" / "secrets.yaml",
    )
    return DataRepo(layout)


class TestActiveYAML:
    def test_snapshot_path(self, repo: DataRepo) -> None:
        assert repo.snapshot_path().name == "snapshot.yaml"

    def test_branches_path(self, repo: DataRepo) -> None:
        assert repo.branches_path().name == "branches.yaml"

    def test_alter_path(self, repo: DataRepo) -> None:
        assert repo.alter_path("alter_A").name == "alter_A.yaml"

    def test_read_snapshot_missing(self, repo: DataRepo) -> None:
        assert repo.read_snapshot() is None

    def test_write_and_read_snapshot(self, repo: DataRepo) -> None:
        data = {"snapshot": {"intake_status": {"phase": "completed"}}}
        repo.write_snapshot(data)
        loaded = repo.read_snapshot()
        assert loaded is not None
        assert loaded["snapshot"]["intake_status"]["phase"] == "completed"

    def test_write_and_read_branches(self, repo: DataRepo) -> None:
        data = {"branches": {"branch_A": {"id": "branch_A"}}}
        repo.write_branches(data)
        loaded = repo.read_branches()
        assert loaded is not None
        assert "branch_A" in loaded["branches"]

    def test_write_and_read_alter(self, repo: DataRepo) -> None:
        data = {"alter_A": {"branch_ref": "branch_A"}}
        repo.write_alter("alter_A", data)
        loaded = repo.read_alter("alter_A")
        assert loaded is not None
        assert loaded["alter_A"]["branch_ref"] == "branch_A"

    def test_list_alters_empty(self, repo: DataRepo) -> None:
        assert repo.list_alters() == []

    def test_list_alters(self, repo: DataRepo) -> None:
        repo.write_alter("alter_A", {"alter_A": {"id": "A"}})
        repo.write_alter("alter_B", {"alter_B": {"id": "B"}})
        alters = repo.list_alters()
        assert len(alters) == 2

    def test_list_alters_excludes_template(self, repo: DataRepo) -> None:
        repo.write_alter("alter_A", {"alter_A": {"id": "A"}})
        # Create a _template file
        template_dir = repo.alters_dir()
        template_dir.mkdir(parents=True, exist_ok=True)
        (template_dir / "_template.yaml").write_text("template: true")
        alters = repo.list_alters()
        assert len(alters) == 1


class TestCalibration:
    def test_read_rubric_missing(self, repo: DataRepo) -> None:
        assert repo.read_rubric() is None

    def test_list_scores_empty(self, repo: DataRepo) -> None:
        assert repo.list_scores() == []

    def test_write_and_list_scores(self, repo: DataRepo) -> None:
        repo.write_score("score_1", {"score_id": "score_1", "value": 0.8})
        scores = repo.list_scores()
        assert len(scores) == 1
        assert scores[0]["score_id"] == "score_1"

    def test_list_rubric_delta_empty(self, repo: DataRepo) -> None:
        assert repo.list_rubric_delta_suggestions() == []

    def test_write_and_list_checkpoint_plans(self, repo: DataRepo) -> None:
        repo.write_checkpoint_plan("plan_1", {"plan_id": "plan_1"})
        plans = repo.list_checkpoint_plans()
        assert len(plans) == 1


class TestProductRecords:
    def test_list_records_empty(self, repo: DataRepo) -> None:
        assert repo.list_records("weekly_notes") == []

    def test_write_and_read_record(self, repo: DataRepo) -> None:
        repo.write_record("weekly_notes", "note_1", {"note_id": "note_1", "text": "hello"})
        record = repo.read_record("weekly_notes", "note_1")
        assert record is not None
        assert record["text"] == "hello"

    def test_list_records(self, repo: DataRepo) -> None:
        repo.write_record("behavior_metrics", "wk1", {"week": 1})
        repo.write_record("behavior_metrics", "wk2", {"week": 2})
        records = repo.list_records("behavior_metrics")
        assert len(records) == 2

    def test_delete_record(self, repo: DataRepo) -> None:
        repo.write_record("weekly_notes", "note_1", {"text": "hello"})
        assert repo.delete_record("weekly_notes", "note_1") is True
        assert repo.read_record("weekly_notes", "note_1") is None

    def test_delete_nonexistent(self, repo: DataRepo) -> None:
        assert repo.delete_record("weekly_notes", "missing") is False

    def test_invalid_area_raises(self, repo: DataRepo) -> None:
        with pytest.raises(ValueError, match="Unknown product area"):
            repo.list_records("nonexistent_area")

    @pytest.mark.parametrize("area", [
        "weekly_notes", "weekly_reviews", "calibration_records",
        "behavior_metrics", "forecast_snapshots", "predictor_profiles",
        "branch_outcome_targets", "pattern_reviews", "external_evidence",
        "forecast_evaluations",
    ])
    def test_all_areas_resolve(self, repo: DataRepo, area: str) -> None:
        repo.write_record(area, "test_id", {"test": True})
        assert repo.read_record(area, "test_id") is not None


class TestTransactions:
    def test_transaction_commits(self, repo: DataRepo) -> None:
        with repo.transaction(repo.snapshot_path(), repo.branches_path()):
            repo.write_snapshot({"snapshot": {"ok": True}})
            repo.write_branches({"branches": {"ok": True}})
        assert repo.read_snapshot() is not None
        assert repo.read_branches() is not None

    def test_transaction_rollback(self, repo: DataRepo) -> None:
        repo.write_snapshot({"snapshot": {"original": True}})
        with pytest.raises(RuntimeError):
            with repo.transaction(repo.snapshot_path()):
                repo.write_snapshot({"snapshot": {"corrupted": True}})
                raise RuntimeError("simulated failure")
        # Should be restored to original
        loaded = repo.read_snapshot()
        assert loaded["snapshot"]["original"] is True
        assert "corrupted" not in loaded["snapshot"]

    def test_transaction_no_files_just_yields(self, repo: DataRepo) -> None:
        with repo.transaction():
            pass  # no-op transaction


class TestArchive:
    def test_list_archives_empty(self, repo: DataRepo) -> None:
        assert repo.list_archives() == []
