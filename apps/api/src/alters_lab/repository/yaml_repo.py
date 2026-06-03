"""YAML repository — wraps existing p6_runtime file I/O."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from alters_lab.repository.base import Repository
from alters_lab.services import io
from alters_lab.services.p6_runtime import (
    P6_RUNTIME_AREAS,
    get_repo_root,
    record_path,
    runtime_dir,
    validate_record_id,
)


class YamlRepository(Repository):
    """YAML file-based repository. Wraps p6_runtime."""

    def __init__(self, repo_root: Path | None = None):
        self._repo_root = repo_root

    def _resolve_area_dir(self, area: str) -> Path:
        if area in P6_RUNTIME_AREAS:
            return runtime_dir(area, repo_root=self._repo_root)
        # Allow arbitrary areas under alters/product/
        root = self._repo_root or get_repo_root()
        return root / "alters" / "product" / area

    def write(self, area: str, record_id: str, data: dict[str, Any]) -> Path:
        validate_record_id(record_id)
        area_dir = self._resolve_area_dir(area)
        area_dir.mkdir(parents=True, exist_ok=True)
        path = area_dir / f"{record_id}.yaml"
        io.write_yaml(path, data)
        return path

    def read(self, area: str, record_id: str) -> dict[str, Any]:
        validate_record_id(record_id)
        path = self._resolve_area_dir(area) / f"{record_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Record not found: {area}/{record_id}")
        data = io.read_yaml(path)
        if not isinstance(data, dict):
            raise ValueError(f"Record is not a mapping: {area}/{record_id}")
        return data

    def list_records(self, area: str) -> list[dict[str, Any]]:
        directory = self._resolve_area_dir(area)
        if not directory.exists():
            return []
        records: list[dict[str, Any]] = []
        for path in sorted(directory.glob("*.yaml")):
            if path.name.startswith("_template"):
                continue
            data = io.read_yaml(path)
            if isinstance(data, dict):
                records.append(data)
        return records

    def delete(self, area: str, record_id: str) -> Path:
        validate_record_id(record_id)
        path = self._resolve_area_dir(area) / f"{record_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Record not found: {area}/{record_id}")
        path.unlink()
        return path

    def exists(self, area: str, record_id: str) -> bool:
        validate_record_id(record_id)
        path = self._resolve_area_dir(area) / f"{record_id}.yaml"
        return path.exists()
