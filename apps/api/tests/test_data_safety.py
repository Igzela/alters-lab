"""Tests for P7-M7 data safety and backups."""

from __future__ import annotations

import tarfile
from pathlib import Path

import pytest

from alters_lab.services.data_safety import (
    DataSafetyError,
    build_backup_plan,
    build_user_data_manifest,
    create_backup_archive,
    verify_maintainer_scripts_preserve_user_data,
    verify_no_package_owned_user_paths,
)
from alters_lab.services.runtime_layout import RuntimeLayout, resolve_runtime_layout


def _layout(tmp_path: Path) -> RuntimeLayout:
    repo = tmp_path / "repo"
    repo.mkdir()
    return resolve_runtime_layout(
        mode="packaged",
        repo_root=repo,
        app_root=tmp_path / "opt" / "alters-lab",
        config_dir=tmp_path / "home" / ".config" / "alters-lab",
        data_dir=tmp_path / "home" / ".local" / "share" / "alters-lab",
        state_dir=tmp_path / "home" / ".local" / "state" / "alters-lab",
    )


def _seed_user_data(layout: RuntimeLayout) -> None:
    layout.product_data_dir.mkdir(parents=True)
    (layout.product_data_dir / "weekly_reviews").mkdir()
    (layout.product_data_dir / "weekly_reviews" / "review.yaml").write_text("review: true\n", encoding="utf-8")
    layout.config_dir.mkdir(parents=True)
    layout.config_path.write_text("version: 1\n", encoding="utf-8")
    layout.secrets_path.write_text("api_key: test-key-not-real\n", encoding="utf-8")
    layout.logs_dir.mkdir(parents=True)
    (layout.logs_dir / "alters-lab.log").write_text("log\n", encoding="utf-8")


def test_manifest_redacts_secret_path(tmp_path: Path):
    layout = _layout(tmp_path)
    _seed_user_data(layout)

    manifest = build_user_data_manifest(layout)

    assert manifest["paths"]["secrets_path"]["redacted"] is True
    assert manifest["secrets_redacted"] is True
    assert manifest["behavior_validated"] is False
    assert manifest["p6_sealed"] is False


def test_default_backup_plan_includes_data_and_config_excludes_secrets(tmp_path: Path):
    layout = _layout(tmp_path)
    _seed_user_data(layout)

    plan = build_backup_plan(layout, output_path=tmp_path / "backup.tar.gz")

    assert "data" in plan["included_sections"]
    assert "config" in plan["included_sections"]
    assert "secrets" in plan["excluded_sections"]
    assert plan["secrets_included"] is False


def test_include_logs_only_when_requested(tmp_path: Path):
    layout = _layout(tmp_path)
    _seed_user_data(layout)

    without_logs = build_backup_plan(layout, output_path=tmp_path / "a.tar.gz")
    with_logs = build_backup_plan(layout, output_path=tmp_path / "b.tar.gz", include_logs=True)

    assert "logs" in without_logs["excluded_sections"]
    assert "logs" in with_logs["included_sections"]


def test_include_secrets_requires_exact_confirmation(tmp_path: Path):
    layout = _layout(tmp_path)
    _seed_user_data(layout)

    with pytest.raises(DataSafetyError):
        build_backup_plan(layout, output_path=tmp_path / "backup.tar.gz", include_secrets=True)

    plan = build_backup_plan(
        layout,
        output_path=tmp_path / "backup.tar.gz",
        include_secrets=True,
        confirm_include_secrets="include-secrets-in-backup",
    )
    assert plan["secrets_included"] is True


def test_backup_dry_run_writes_no_archive(tmp_path: Path):
    layout = _layout(tmp_path)
    _seed_user_data(layout)
    output = tmp_path / "backup.tar.gz"

    plan = build_backup_plan(layout, output_path=output)

    assert plan["dry_run"] is True
    assert not output.exists()


def test_backup_archive_excludes_secrets_by_default(tmp_path: Path):
    layout = _layout(tmp_path)
    _seed_user_data(layout)
    output = tmp_path / "backups" / "backup.tar.gz"

    result = create_backup_archive(layout, output_path=output)

    assert result["status"] == "created"
    assert output.exists()
    with tarfile.open(output, "r:gz") as archive:
        names = archive.getnames()
    assert "data/product/weekly_reviews/review.yaml" in names
    assert "config/config.yaml" in names
    assert "config/secrets.yaml" not in names
    assert result["behavior_validated"] is False
    assert result["p6_sealed"] is False


def test_backup_archive_can_include_dummy_secret_with_confirmation(tmp_path: Path):
    layout = _layout(tmp_path)
    _seed_user_data(layout)
    output = tmp_path / "backup-with-secret.tar.gz"

    result = create_backup_archive(
        layout,
        output_path=output,
        include_secrets=True,
        confirm_include_secrets="include-secrets-in-backup",
    )

    assert result["secrets_included"] is True
    with tarfile.open(output, "r:gz") as archive:
        names = archive.getnames()
    assert "config/secrets.yaml" in names


def test_verify_package_contents_rejects_user_paths_and_runtime_records():
    ok = verify_no_package_owned_user_paths(["./opt/alters-lab/apps/api/src/main.py", "./usr/bin/alters-lab"])
    bad = verify_no_package_owned_user_paths(["./home/user/.local/share/alters-lab/product/raw.yaml", "./opt/node_modules/x"])

    assert ok["status"] == "PASS"
    assert bad["status"] == "FAIL"


def test_maintainer_scripts_preserve_user_data():
    repo_root = Path(__file__).resolve().parents[3]
    report = verify_maintainer_scripts_preserve_user_data(
        [
            repo_root / "packaging" / "deb" / "postinst",
            repo_root / "packaging" / "deb" / "prerm",
            repo_root / "packaging" / "deb" / "postrm",
        ]
    )

    assert report["status"] == "PASS"
