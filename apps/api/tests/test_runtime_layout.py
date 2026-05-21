"""Service tests for P7 runtime layout resolution."""

from __future__ import annotations

import stat

import yaml

from alters_lab.services.p6_runtime import read_record, runtime_dir, write_record
from alters_lab.services.runtime_layout import (
    default_config,
    ensure_secrets_fallback_file,
    ensure_user_config,
    load_user_config,
    resolve_runtime_layout,
)


def test_dev_mode_default_resolves_repo_compatible_paths(tmp_path, monkeypatch):
    monkeypatch.delenv("ALTERS_LAB_MODE", raising=False)
    layout = resolve_runtime_layout(mode="dev", repo_root=tmp_path)

    assert layout.mode == "dev"
    assert layout.repo_root == tmp_path.resolve()
    assert layout.product_data_dir == tmp_path.resolve() / "alters" / "product"
    assert layout.config_path == tmp_path.resolve() / "alters" / "product" / "config" / "config.yaml"
    assert layout.active_yaml_write_allowed is False
    assert layout.rubric_write_allowed is False


def test_explicit_packaged_mode_resolves_user_owned_paths(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    layout = resolve_runtime_layout(mode="packaged")

    assert layout.mode == "packaged"
    assert layout.repo_root is None
    assert layout.config_path == home / ".config" / "alters-lab" / "config.yaml"
    assert layout.data_dir == home / ".local" / "share" / "alters-lab"
    assert layout.product_data_dir == home / ".local" / "share" / "alters-lab" / "product"
    assert layout.logs_dir == home / ".local" / "state" / "alters-lab" / "logs"
    assert layout.secrets_path == home / ".config" / "alters-lab" / "secrets.yaml"


def test_environment_packaged_mode_selects_packaged_paths(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("ALTERS_LAB_MODE", "packaged")

    layout = resolve_runtime_layout()

    assert layout.mode == "packaged"
    assert layout.data_dir == home / ".local" / "share" / "alters-lab"


def test_explicit_repo_root_preserves_p6_dev_test_behavior(tmp_path, monkeypatch):
    monkeypatch.setenv("ALTERS_LAB_MODE", "packaged")

    assert runtime_dir("weekly_reviews", repo_root=tmp_path) == tmp_path / "alters" / "product" / "weekly_reviews"


def test_p6_write_record_dev_mode_writes_under_repo_product(tmp_path, monkeypatch):
    monkeypatch.delenv("ALTERS_LAB_MODE", raising=False)

    path = write_record("weekly_reviews", "review_1", {"id": "review_1"}, repo_root=tmp_path)

    assert path == tmp_path / "alters" / "product" / "weekly_reviews" / "review_1.yaml"
    assert read_record("weekly_reviews", "review_1", repo_root=tmp_path) == {"id": "review_1"}


def test_p6_write_record_packaged_mode_writes_under_data_product(tmp_path):
    layout = resolve_runtime_layout(
        mode="packaged",
        config_dir=tmp_path / "config",
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
    )

    path = write_record("weekly_reviews", "review_1", {"id": "review_1"}, layout=layout)

    assert path == tmp_path / "data" / "product" / "weekly_reviews" / "review_1.yaml"
    assert read_record("weekly_reviews", "review_1", layout=layout) == {"id": "review_1"}
    assert not (tmp_path / "alters" / "product").exists()


def test_mode_argument_packaged_uses_user_data_paths(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))

    path = write_record("weekly_notes", "note_1", {"id": "note_1"}, mode="packaged")

    assert path == home / ".local" / "share" / "alters-lab" / "product" / "weekly_notes" / "note_1.yaml"


def test_ensure_user_config_creates_config_without_secrets(tmp_path):
    layout = resolve_runtime_layout(
        mode="packaged",
        config_dir=tmp_path / "config",
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
    )

    path = ensure_user_config(layout)
    config = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert path == tmp_path / "config" / "config.yaml"
    assert config == default_config(layout)
    assert "api_key" not in path.read_text(encoding="utf-8").lower()
    assert not layout.secrets_path.exists()


def test_load_user_config_preserves_existing_config(tmp_path):
    layout = resolve_runtime_layout(
        mode="packaged",
        config_dir=tmp_path / "config",
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
    )
    custom = default_config(layout)
    custom["provider"]["mode"] = "mock"
    layout.config_dir.mkdir(parents=True)
    layout.config_path.write_text(yaml.safe_dump(custom, sort_keys=False), encoding="utf-8")

    assert load_user_config(layout)["provider"]["mode"] == "mock"


def test_secrets_fallback_file_has_0600_permissions(tmp_path):
    layout = resolve_runtime_layout(
        mode="packaged",
        config_dir=tmp_path / "config",
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
    )

    path = ensure_secrets_fallback_file(layout)
    mode = stat.S_IMODE(path.stat().st_mode)

    assert path == tmp_path / "config" / "secrets.yaml"
    assert mode == 0o600
    assert "sk-" not in path.read_text(encoding="utf-8")

