"""Tests for repository layer — YAML and SQLite implementations."""

from __future__ import annotations

import pytest
from pathlib import Path

from alters_lab.repository.base import Repository
from alters_lab.repository.yaml_repo import YamlRepository
from alters_lab.repository.sqlite_repo import SqliteRepository
from alters_lab.repository.factory import configure_repository, get_repository, reset_repository
from alters_lab.repository.migration import (
    migrate_yaml_to_sqlite,
    migrate_sqlite_to_yaml,
    dry_run_migration,
)


# --- YAML Repository Tests ---

class TestYamlRepository:

    @pytest.fixture()
    def repo(self, tmp_path: Path) -> YamlRepository:
        return YamlRepository(repo_root=tmp_path)

    def test_write_and_read(self, repo: YamlRepository):
        repo.write("test_area", "rec_001", {"name": "test", "value": 42})
        data = repo.read("test_area", "rec_001")
        assert data["name"] == "test"
        assert data["value"] == 42

    def test_list_records(self, repo: YamlRepository):
        repo.write("test_area", "rec_001", {"name": "a"})
        repo.write("test_area", "rec_002", {"name": "b"})
        records = repo.list_records("test_area")
        assert len(records) == 2

    def test_delete(self, repo: YamlRepository):
        repo.write("test_area", "rec_001", {"name": "test"})
        repo.delete("test_area", "rec_001")
        assert not repo.exists("test_area", "rec_001")

    def test_delete_not_found(self, repo: YamlRepository):
        with pytest.raises(FileNotFoundError):
            repo.delete("test_area", "nonexistent")

    def test_read_not_found(self, repo: YamlRepository):
        with pytest.raises(FileNotFoundError):
            repo.read("test_area", "nonexistent")

    def test_exists(self, repo: YamlRepository):
        assert not repo.exists("test_area", "rec_001")
        repo.write("test_area", "rec_001", {"name": "test"})
        assert repo.exists("test_area", "rec_001")

    def test_list_empty(self, repo: YamlRepository):
        records = repo.list_records("nonexistent_area")
        assert records == []

    def test_overwrite(self, repo: YamlRepository):
        repo.write("test_area", "rec_001", {"version": 1})
        repo.write("test_area", "rec_001", {"version": 2})
        data = repo.read("test_area", "rec_001")
        assert data["version"] == 2

    def test_export_area(self, repo: YamlRepository):
        repo.write("test_area", "rec_001", {"name": "a"})
        repo.write("test_area", "rec_002", {"name": "b"})
        exported = repo.export_area("test_area")
        assert len(exported) == 2

    def test_import_area(self, repo: YamlRepository):
        records = [
            {"record_id": "r1", "value": 1},
            {"record_id": "r2", "value": 2},
        ]
        count = repo.import_area("test_area", records, id_key="record_id")
        assert count == 2
        assert repo.exists("test_area", "r1")
        assert repo.exists("test_area", "r2")


# --- SQLite Repository Tests ---

class TestSqliteRepository:

    @pytest.fixture()
    def repo(self, tmp_path: Path) -> SqliteRepository:
        db_path = tmp_path / "test.db"
        return SqliteRepository(db_path)

    def test_write_and_read(self, repo: SqliteRepository):
        repo.write("test_area", "rec_001", {"name": "test", "value": 42})
        data = repo.read("test_area", "rec_001")
        assert data["name"] == "test"
        assert data["value"] == 42

    def test_list_records(self, repo: SqliteRepository):
        repo.write("test_area", "rec_001", {"name": "a"})
        repo.write("test_area", "rec_002", {"name": "b"})
        records = repo.list_records("test_area")
        assert len(records) == 2

    def test_delete(self, repo: SqliteRepository):
        repo.write("test_area", "rec_001", {"name": "test"})
        repo.delete("test_area", "rec_001")
        assert not repo.exists("test_area", "rec_001")

    def test_delete_not_found(self, repo: SqliteRepository):
        with pytest.raises(FileNotFoundError):
            repo.delete("test_area", "nonexistent")

    def test_read_not_found(self, repo: SqliteRepository):
        with pytest.raises(FileNotFoundError):
            repo.read("test_area", "nonexistent")

    def test_exists(self, repo: SqliteRepository):
        assert not repo.exists("test_area", "rec_001")
        repo.write("test_area", "rec_001", {"name": "test"})
        assert repo.exists("test_area", "rec_001")

    def test_list_empty(self, repo: SqliteRepository):
        records = repo.list_records("nonexistent_area")
        assert records == []

    def test_overwrite(self, repo: SqliteRepository):
        repo.write("test_area", "rec_001", {"version": 1})
        repo.write("test_area", "rec_001", {"version": 2})
        data = repo.read("test_area", "rec_001")
        assert data["version"] == 2

    def test_count(self, repo: SqliteRepository):
        repo.write("test_area", "rec_001", {"name": "a"})
        repo.write("test_area", "rec_002", {"name": "b"})
        assert repo.count("test_area") == 2

    def test_list_areas(self, repo: SqliteRepository):
        repo.write("area_a", "r1", {"x": 1})
        repo.write("area_b", "r2", {"x": 2})
        areas = repo.list_areas()
        assert "area_a" in areas
        assert "area_b" in areas

    def test_transaction_commit(self, repo: SqliteRepository):
        with repo.transaction():
            repo.write("test_area", "rec_001", {"name": "test"})
        assert repo.exists("test_area", "rec_001")

    def test_transaction_rollback(self, repo: SqliteRepository):
        try:
            with repo.transaction():
                repo.write("test_area", "rec_001", {"name": "test"})
                raise ValueError("force rollback")
        except ValueError:
            pass
        # After rollback, record should not exist
        assert not repo.exists("test_area", "rec_001")

    def test_export_area(self, repo: SqliteRepository):
        repo.write("test_area", "rec_001", {"name": "a"})
        exported = repo.export_area("test_area")
        assert len(exported) == 1

    def test_import_area(self, repo: SqliteRepository):
        records = [
            {"record_id": "r1", "value": 1},
            {"record_id": "r2", "value": 2},
        ]
        count = repo.import_area("test_area", records, id_key="record_id")
        assert count == 2
        assert repo.exists("test_area", "r1")


# --- Migration Tests ---

class TestMigration:

    @pytest.fixture()
    def yaml_repo(self, tmp_path: Path) -> YamlRepository:
        return YamlRepository(repo_root=tmp_path)

    @pytest.fixture()
    def sqlite_repo(self, tmp_path: Path) -> SqliteRepository:
        return SqliteRepository(tmp_path / "test.db")

    def test_yaml_to_sqlite(self, yaml_repo: YamlRepository, sqlite_repo: SqliteRepository):
        yaml_repo.write("forecast_snapshots", "fs_001", {"snapshot_id": "fs_001", "data": "test"})
        yaml_repo.write("forecast_snapshots", "fs_002", {"snapshot_id": "fs_002", "data": "test2"})

        results = migrate_yaml_to_sqlite(yaml_repo, sqlite_repo, areas=["forecast_snapshots"])
        assert results["forecast_snapshots"] == 2

        data = sqlite_repo.read("forecast_snapshots", "fs_001")
        assert data["data"] == "test"

    def test_sqlite_to_yaml(self, yaml_repo: YamlRepository, sqlite_repo: SqliteRepository):
        sqlite_repo.write("model_cards", "mc_001", {"model_id": "mc_001", "data": "test"})

        results = migrate_sqlite_to_yaml(sqlite_repo, yaml_repo, areas=["model_cards"])
        assert results["model_cards"] == 1

        data = yaml_repo.read("model_cards", "mc_001")
        assert data["data"] == "test"

    def test_dry_run(self, yaml_repo: YamlRepository):
        yaml_repo.write("forecast_snapshots", "fs_001", {"snapshot_id": "fs_001"})
        yaml_repo.write("forecast_snapshots", "fs_002", {"snapshot_id": "fs_002"})

        result = dry_run_migration(yaml_repo, areas=["forecast_snapshots"])
        assert result["forecast_snapshots"]["count"] == 2
        assert "fs_001" in result["forecast_snapshots"]["sample_ids"]


# --- Factory Tests ---

class TestFactory:

    def teardown_method(self):
        reset_repository()

    def test_configure_yaml(self, tmp_path: Path):
        repo = configure_repository("yaml", repo_root=tmp_path)
        assert isinstance(repo, YamlRepository)

    def test_configure_sqlite(self, tmp_path: Path):
        db_path = tmp_path / "test.db"
        repo = configure_repository("sqlite", db_path=db_path)
        assert isinstance(repo, SqliteRepository)

    def test_get_repository_auto_configures(self):
        repo = get_repository()
        assert repo is not None
