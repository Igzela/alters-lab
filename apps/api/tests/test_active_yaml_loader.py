import hashlib
import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

from alters_lab.loaders.active_yaml import (
    active_yaml_paths,
    default_project_root,
    load_active_yaml_chain,
    load_yaml_file,
    summarize_active_yaml_chain,
    validate_active_yaml_chain,
)


def _project_root() -> Path:
    return default_project_root()


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --- active_yaml_paths ---


def test_active_yaml_paths_returns_all_9_canonical_paths():
    paths = active_yaml_paths()
    assert paths.snapshot.name == "snapshot.yaml"
    assert paths.branches.name == "branches.yaml"
    assert len(paths.alters) == 4
    for key in ("alter_A", "alter_B", "alter_C", "alter_D"):
        assert key in paths.alters
        assert paths.alters[key].name == f"{key}.yaml"
    assert paths.value_alignment.name == "alignment_2026-05-19.yaml"
    assert paths.dialogue.name == "dialogue_alter_D_2026-05-19.yaml"
    assert paths.reality_trace.name == "reality_trace.yaml"


def test_active_yaml_paths_are_absolute():
    paths = active_yaml_paths()
    assert paths.snapshot.is_absolute()
    assert paths.branches.is_absolute()
    for p in paths.alters.values():
        assert p.is_absolute()


# --- load_yaml_file ---


def test_load_yaml_file_loads_snapshot_as_dict():
    paths = active_yaml_paths()
    data = load_yaml_file(paths.snapshot)
    assert isinstance(data, dict)
    assert "snapshot" in data


def test_load_yaml_file_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_yaml_file(Path("/nonexistent/file.yaml"))


def test_load_yaml_file_non_dict_raises(tmp_path):
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text("- item1\n- item2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Expected dict"):
        load_yaml_file(bad_file)


def test_load_yaml_file_scalar_raises(tmp_path):
    bad_file = tmp_path / "scalar.yaml"
    bad_file.write_text('"just a string"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="Expected dict"):
        load_yaml_file(bad_file)


# --- load_active_yaml_chain ---


def test_load_active_yaml_chain_loads_all_9_artifacts():
    chain = load_active_yaml_chain()
    assert isinstance(chain.snapshot, dict)
    assert isinstance(chain.branches, dict)
    assert len(chain.alters) == 4
    assert isinstance(chain.value_alignment, dict)
    assert isinstance(chain.dialogue, dict)
    assert isinstance(chain.reality_trace, dict)


# --- validate_active_yaml_chain ---


def test_validate_returns_ok_on_sealed_baseline():
    chain = load_active_yaml_chain()
    result = validate_active_yaml_chain(chain)
    assert result.ok is True
    assert result.errors == []


# --- summarize_active_yaml_chain ---


def test_summarize_returns_expected_values():
    chain = load_active_yaml_chain()
    summary = summarize_active_yaml_chain(chain)
    assert summary["branch_count"] == 4
    assert summary["selected_branch"] == "branch_D"
    assert summary["primary_candidate"] == "branch_D"
    assert summary["reality_trace_status"] == "active"
    assert summary["snapshot_phase"] == "completed"
    assert summary["calibration_ready"] is False


# --- loader does not modify active YAML ---


def test_loader_does_not_modify_active_yaml():
    paths = active_yaml_paths()
    snap_hash_before = _hash_file(paths.snapshot)
    snap_text_before = _text_file(paths.snapshot)
    br_hash_before = _hash_file(paths.branches)
    br_text_before = _text_file(paths.branches)
    rt_hash_before = _hash_file(paths.reality_trace)
    rt_text_before = _text_file(paths.reality_trace)

    chain = load_active_yaml_chain()
    validate_active_yaml_chain(chain)
    summarize_active_yaml_chain(chain)

    assert _hash_file(paths.snapshot) == snap_hash_before
    assert _text_file(paths.snapshot) == snap_text_before
    assert _hash_file(paths.branches) == br_hash_before
    assert _text_file(paths.branches) == br_text_before
    assert _hash_file(paths.reality_trace) == rt_hash_before
    assert _text_file(paths.reality_trace) == rt_text_before


# --- default_project_root ---


def test_default_project_root_points_to_repo():
    root = default_project_root()
    assert (root / "alters").is_dir()
    assert (root / "apps").is_dir()
