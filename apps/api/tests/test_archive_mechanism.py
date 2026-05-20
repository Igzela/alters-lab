"""Tests for P4-M6 Archive Mechanism service."""

from __future__ import annotations

import pytest

from alters_lab.schemas.archive_mechanism import ArchiveCreateRequest, ArchivePlanRequest
from alters_lab.services.archive_mechanism import create_archive, list_archives, plan_archive


def _write_allowed_sources(tmp_path):
    files = {
        "alters/current/snapshot.yaml": "snapshot: ok\n",
        "alters/current/branches.yaml": "branches: []\n",
        "alters/current/alters/alter_A.yaml": "id: alter_A\n",
        "alters/current/reality_trace.yaml": "trace: ok\n",
        "alters/calibration/rubric.yaml": "rubric: ok\n",
        "alters/calibration/scores/score_one.yaml": "id: score_one\n",
        "alters/calibration/rubric_delta_suggestions/rubric_delta_one.yaml": "id: rubric_delta_one\n",
        "alters/calibration/checkpoint_plans/checkpoint_plan_one.yaml": "id: checkpoint_plan_one\n",
    }
    for rel, content in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    (tmp_path / "alters" / "current" / "unexpected.yaml").write_text("no\n", encoding="utf-8")
    return files


def test_plan_archive_creates_manifest_without_writing(tmp_path):
    _write_allowed_sources(tmp_path)
    manifest = plan_archive(ArchivePlanRequest(reason="before future write"), tmp_path)
    assert manifest.status == "planned"
    assert manifest.entries
    assert not (tmp_path / "alters" / "archive" / "checkpoints").exists()


def test_create_archive_copies_only_allowed_files_and_manifest_has_sha256(tmp_path):
    sources = _write_allowed_sources(tmp_path)
    before = {rel: (tmp_path / rel).read_text(encoding="utf-8") for rel in sources}
    manifest, archive_path = create_archive(ArchiveCreateRequest(reason="explicit archive"), tmp_path)
    assert manifest.status == "created"
    assert (archive_path / "manifest.yaml").exists()
    archived_sources = {entry.source_path for entry in manifest.entries}
    assert "alters/current/unused.yaml" not in archived_sources
    assert "alters/current/branches.yaml" in archived_sources
    assert all(len(entry.sha256) == 64 for entry in manifest.entries)
    for rel, content in before.items():
        assert (tmp_path / rel).read_text(encoding="utf-8") == content


def test_invalid_reason_rejected():
    with pytest.raises(Exception):
        ArchivePlanRequest(reason="")
    with pytest.raises(Exception):
        ArchiveCreateRequest(reason="")
    with pytest.raises(Exception):
        ArchivePlanRequest(reason="x", auto_archive=True)


def test_no_active_yaml_modified(tmp_path):
    _write_allowed_sources(tmp_path)
    snapshot = tmp_path / "alters" / "current" / "snapshot.yaml"
    before = snapshot.read_text(encoding="utf-8")
    create_archive(ArchiveCreateRequest(reason="explicit archive"), tmp_path)
    assert snapshot.read_text(encoding="utf-8") == before


def test_list_archives_metadata_only(tmp_path):
    _write_allowed_sources(tmp_path)
    create_archive(ArchiveCreateRequest(reason="explicit archive"), tmp_path)
    archives = list_archives(tmp_path)
    assert len(archives) == 1
    assert archives[0]["status"] == "created"
    assert "entries" not in archives[0]
