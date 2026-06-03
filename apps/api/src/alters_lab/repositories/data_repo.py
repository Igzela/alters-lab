"""Unified data repository for all Alters Lab data domains.

Encapsulates YAML/JSON I/O with atomic writes. Services should receive
a DataRepo instance (via FastAPI Depends or explicit construction) and
use it for all file operations instead of direct yaml.safe_load/safe_dump.

This replaces:
- 35+ scattered yaml.safe_load/safe_dump call sites
- Duplicated safe_read_yaml/safe_read_json in phase closeout services
- Direct path.write_text() calls in p6_runtime, calibration_loop, etc.
"""

from __future__ import annotations

import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from alters_lab.services import io
from alters_lab.services.controlled_write import (
    append_jsonl_audit,
    create_backup_if_exists,
    hash_approval_token,
    sha256_file,
    sha256_text,
)
from alters_lab.services.runtime_layout import RuntimeLayout, resolve_runtime_layout


class DataRepo:
    """Unified data access for all Alters Lab data domains.

    Each method handles path resolution, atomic I/O, and error handling.
    Services receive this via FastAPI Depends() or explicit construction.
    """

    def __init__(self, layout: RuntimeLayout | None = None) -> None:
        self._layout = layout or resolve_runtime_layout()

    @property
    def layout(self) -> RuntimeLayout:
        return self._layout

    @property
    def repo_root(self) -> Path:
        root = self._layout.repo_root
        if root is None:
            raise RuntimeError("repo_root not available in packaged mode")
        return root

    # ─── Active YAML (alters/current/) ───

    def active_dir(self) -> Path:
        return self.repo_root / "alters" / "current"

    def snapshot_path(self) -> Path:
        return self.active_dir() / "snapshot.yaml"

    def branches_path(self) -> Path:
        return self.active_dir() / "branches.yaml"

    def alters_dir(self) -> Path:
        return self.active_dir() / "alters"

    def alter_path(self, alter_id: str) -> Path:
        return self.alters_dir() / f"{alter_id}.yaml"

    def reality_trace_path(self) -> Path:
        return self.active_dir() / "reality_trace.yaml"

    def dialogue_dir(self) -> Path:
        return self.active_dir() / "dialogue"

    def value_alignment_dir(self) -> Path:
        return self.active_dir() / "value_alignment"

    def read_snapshot(self) -> dict[str, Any] | None:
        return io.read_yaml(self.snapshot_path())

    def read_branches(self) -> dict[str, Any] | None:
        return io.read_yaml(self.branches_path())

    def read_alter(self, alter_id: str) -> dict[str, Any] | None:
        return io.read_yaml(self.alter_path(alter_id))

    def list_alters(self) -> list[dict[str, Any]]:
        """List all alter YAML files, excluding _template."""
        alters = []
        for p in sorted(self.alters_dir().glob("*.yaml")):
            if p.name.startswith("_"):
                continue
            data = io.read_yaml(p)
            if isinstance(data, dict):
                alters.append(data)
        return alters

    def read_reality_trace(self) -> dict[str, Any] | None:
        return io.read_yaml(self.reality_trace_path())

    def write_snapshot(
        self, data: dict, *, audit_log: Path | None = None, backup_dir: Path | None = None
    ) -> Path:
        path = self.snapshot_path()
        if backup_dir:
            create_backup_if_exists(path, backup_dir, prefix="snapshot")
        io.write_yaml(path, data)
        if audit_log:
            content = path.read_text(encoding="utf-8")
            append_jsonl_audit(audit_log, {
                "ts": datetime.now(timezone.utc).isoformat(),
                "action": "write_snapshot",
                "sha256": sha256_text(content),
            })
        return path

    def write_branches(
        self, data: dict, *, audit_log: Path | None = None, backup_dir: Path | None = None
    ) -> Path:
        path = self.branches_path()
        if backup_dir:
            create_backup_if_exists(path, backup_dir, prefix="branches")
        io.write_yaml(path, data)
        if audit_log:
            content = path.read_text(encoding="utf-8")
            append_jsonl_audit(audit_log, {
                "ts": datetime.now(timezone.utc).isoformat(),
                "action": "write_branches",
                "sha256": sha256_text(content),
            })
        return path

    def write_alter(
        self, alter_id: str, data: dict, *, audit_log: Path | None = None, backup_dir: Path | None = None
    ) -> Path:
        path = self.alter_path(alter_id)
        if backup_dir:
            create_backup_if_exists(path, backup_dir, prefix=alter_id)
        io.write_yaml(path, data)
        if audit_log:
            append_jsonl_audit(audit_log, {
                "ts": datetime.now(timezone.utc).isoformat(),
                "action": "write_alter",
                "alter_id": alter_id,
                "sha256": sha256_file(path),
            })
        return path

    # ─── Calibration (alters/calibration/) ───

    def calibration_dir(self) -> Path:
        return self.repo_root / "alters" / "calibration"

    def rubric_path(self) -> Path:
        return self.calibration_dir() / "rubric.yaml"

    def read_rubric(self) -> dict[str, Any] | None:
        return io.read_yaml(self.rubric_path())

    def scores_dir(self) -> Path:
        return self.calibration_dir() / "scores"

    def list_scores(self) -> list[dict[str, Any]]:
        results = []
        for p in sorted(self.scores_dir().glob("*.yaml")):
            if p.name.startswith("_"):
                continue
            data = io.read_yaml(p)
            if isinstance(data, dict):
                results.append(data)
        return results

    def write_score(self, score_id: str, data: dict) -> Path:
        path = self.scores_dir() / f"{score_id}.yaml"
        io.write_yaml(path, data)
        return path

    def rubric_delta_dir(self) -> Path:
        return self.calibration_dir() / "rubric_delta_suggestions"

    def list_rubric_delta_suggestions(self) -> list[dict[str, Any]]:
        results = []
        directory = self.rubric_delta_dir()
        if not directory.exists():
            return results
        for p in sorted(directory.glob("*.yaml")):
            if p.name.startswith("_"):
                continue
            data = io.read_yaml(p)
            if isinstance(data, dict):
                results.append(data)
        return results

    def write_rubric_delta_suggestion(self, suggestion_id: str, data: dict) -> Path:
        path = self.rubric_delta_dir() / f"{suggestion_id}.yaml"
        io.write_yaml(path, data)
        return path

    def checkpoint_plans_dir(self) -> Path:
        return self.calibration_dir() / "checkpoint_plans"

    def list_checkpoint_plans(self) -> list[dict[str, Any]]:
        results = []
        directory = self.checkpoint_plans_dir()
        if not directory.exists():
            return results
        for p in sorted(directory.glob("*.yaml")):
            if p.name.startswith("_"):
                continue
            data = io.read_yaml(p)
            if isinstance(data, dict):
                results.append(data)
        return results

    def write_checkpoint_plan(self, plan_id: str, data: dict) -> Path:
        path = self.checkpoint_plans_dir() / f"{plan_id}.yaml"
        io.write_yaml(path, data)
        return path

    # ─── Draft workspace (alters/drafts/) ───

    def drafts_dir(self) -> Path:
        return self.repo_root / "alters" / "drafts"

    def draft_dir(self, draft_id: str) -> Path:
        return self.drafts_dir() / draft_id

    def read_draft_artifact(self, draft_id: str, artifact_name: str) -> dict[str, Any] | None:
        path = self.draft_dir(draft_id) / artifact_name
        return io.read_yaml(path)

    def write_draft_artifact(self, draft_id: str, artifact_name: str, data: dict) -> Path:
        path = self.draft_dir(draft_id) / artifact_name
        io.write_yaml(path, data)
        return path

    def write_draft_artifact_model(self, draft_id: str, artifact_name: str, model: Any) -> Path:
        path = self.draft_dir(draft_id) / artifact_name
        io.write_model_yaml(path, model)
        return path

    # ─── Archive (alters/archive/) ───

    def archive_dir(self) -> Path:
        return self.repo_root / "alters" / "archive"

    def create_archive(self, archive_id: str, manifest: dict, source_files: dict[str, Path]) -> Path:
        """Create an archive checkpoint with manifest and copied source files."""
        archive_root = self.archive_dir() / "checkpoints" / archive_id
        archive_root.mkdir(parents=True, exist_ok=False)
        io.write_yaml(archive_root / "manifest.yaml", manifest)
        for relative_path, source in source_files.items():
            dest = archive_root / relative_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        return archive_root

    def list_archives(self) -> list[dict[str, Any]]:
        results = []
        checkpoints = self.archive_dir() / "checkpoints"
        if not checkpoints.exists():
            return results
        for d in sorted(checkpoints.iterdir()):
            if not d.is_dir():
                continue
            manifest_path = d / "manifest.yaml"
            if manifest_path.exists():
                data = io.read_yaml(manifest_path)
                if isinstance(data, dict):
                    results.append(data)
        return results

    # ─── Product data (alters/product/) ───

    _PRODUCT_AREAS = {
        "weekly_notes": "alters/product/weekly_notes",
        "weekly_reviews": "alters/product/weekly_reviews",
        "calibration_records": "alters/product/calibration_records",
        "self_deception_challenges": "alters/product/self_deception_challenges",
        "alter_recommendations": "alters/product/alter_recommendations",
        "reminders": "alters/product/reminders",
        "pattern_reviews": "alters/product/pattern_reviews",
        "exports": "alters/product/exports",
        "behavior_validation": "alters/product/behavior_validation",
        "behavior_metrics": "alters/product/behavior_metrics/weekly_records",
        "branch_milestones": "alters/product/branch_milestones",
        "predictor_profiles": "alters/product/predictor_profiles",
        "branch_outcome_targets": "alters/product/branch_outcome_targets",
        "forecast_snapshots": "alters/product/forecast_snapshots",
        "external_evidence": "alters/product/external_evidence",
        "forecast_evaluations": "alters/product/forecast_evaluations",
    }

    def product_dir(self) -> Path:
        return self._layout.product_data_dir

    def _area_dir(self, area: str) -> Path:
        if area not in self._PRODUCT_AREAS:
            raise ValueError(f"Unknown product area: {area}")
        return self.repo_root / self._PRODUCT_AREAS[area]

    def list_records(self, area: str) -> list[dict[str, Any]]:
        results = []
        directory = self._area_dir(area)
        if not directory.exists():
            return results
        for p in sorted(directory.glob("*.yaml")):
            if p.name.startswith("_"):
                continue
            data = io.read_yaml(p)
            if isinstance(data, dict):
                results.append(data)
        return results

    def read_record(self, area: str, record_id: str) -> dict[str, Any] | None:
        path = self._area_dir(area) / f"{record_id}.yaml"
        return io.read_yaml(path)

    def write_record(self, area: str, record_id: str, data: dict) -> Path:
        path = self._area_dir(area) / f"{record_id}.yaml"
        io.write_yaml(path, data)
        return path

    def delete_record(self, area: str, record_id: str) -> bool:
        path = self._area_dir(area) / f"{record_id}.yaml"
        if path.exists():
            path.unlink()
            return True
        return False

    # ─── Transactions ───

    @contextmanager
    def transaction(self, *paths: Path):
        """Multi-file transaction: snapshot before, rollback on exception.

        Usage:
            with repo.transaction(repo.snapshot_path(), repo.branches_path()):
                repo.write_snapshot(...)
                repo.write_branches(...)  # if this fails, snapshot is restored
        """
        snapshots: dict[Path, bytes] = {}
        tmp_files: dict[Path, Path] = {}
        target_list = list(paths)

        try:
            for p in target_list:
                if p.exists():
                    snapshots[p] = p.read_bytes()
                    tmp = tempfile.NamedTemporaryFile(
                        dir=p.parent, delete=False, prefix=f".txn-{p.name}."
                    )
                    tmp.write(snapshots[p])
                    tmp.close()
                    tmp_files[p] = Path(tmp.name)
            yield
        except Exception:
            for p, original in snapshots.items():
                p.write_bytes(original)
            for tmp_path in tmp_files.values():
                if tmp_path.exists():
                    tmp_path.unlink()
            raise
        else:
            for tmp_path in tmp_files.values():
                if tmp_path.exists():
                    tmp_path.unlink()

    # ─── Config ───

    def read_config(self) -> dict[str, Any]:
        from alters_lab.services.runtime_layout import ensure_user_config, load_user_config
        ensure_user_config(self._layout)
        return load_user_config(self._layout)

    def write_config(self, config: dict[str, Any]) -> Path:
        from alters_lab.services.runtime_layout import write_user_config
        return write_user_config(self._layout, config)


def get_data_repo(layout: RuntimeLayout | None = None) -> DataRepo:
    """Factory: create a DataRepo from layout."""
    return DataRepo(layout)
