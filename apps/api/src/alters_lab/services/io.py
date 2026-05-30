"""Centralized YAML/JSON I/O with atomic writes and consistent error handling.

All file I/O in the services layer should go through this module.
Atomic writes use temp-file + os.replace() to prevent partial writes on crash.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import yaml


# --- Read helpers ---

def read_yaml(path: Path) -> Any:
    """Read and parse a YAML file. Returns None if file doesn't exist."""
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def read_yaml_or_empty(path: Path) -> dict[str, Any]:
    """Read YAML file, returning {} if missing or non-dict content."""
    data = read_yaml(path)
    if not isinstance(data, dict):
        return {}
    return data


def read_json(path: Path) -> Any:
    """Read and parse a JSON file. Returns None if file doesn't exist."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_or_empty(path: Path) -> dict[str, Any]:
    """Read JSON file, returning {} if missing or non-dict content."""
    data = read_json(path)
    if not isinstance(data, dict):
        return {}
    return data


def read_text(path: Path) -> str | None:
    """Read text file contents. Returns None if file doesn't exist."""
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


# --- Write helpers (atomic) ---

def _atomic_write(path: Path, content: str) -> None:
    """Write content atomically via temp file + os.replace()."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), suffix=".tmp", prefix=f".{path.name}."
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(path))
    except BaseException:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def write_yaml(
    path: Path,
    data: Any,
    *,
    sort_keys: bool = False,
    allow_unicode: bool = True,
) -> None:
    """Write data to YAML file atomically."""
    content = yaml.safe_dump(data, sort_keys=sort_keys, allow_unicode=allow_unicode)
    _atomic_write(path, content)


def dump_yaml_str(
    data: Any,
    *,
    sort_keys: bool = False,
    allow_unicode: bool = True,
) -> str:
    """Dump data to YAML string (no file write)."""
    return yaml.safe_dump(data, sort_keys=sort_keys, allow_unicode=allow_unicode)


def dump_model_yaml(model: Any, *, default_flow_style: bool = False) -> str:
    """Dump a Pydantic model to YAML string via model_dump()."""
    return yaml.dump(
        model.model_dump(),
        default_flow_style=default_flow_style,
        allow_unicode=True,
    )


def write_model_yaml(path: Path, model: Any) -> None:
    """Write a Pydantic model to YAML file atomically."""
    _atomic_write(path, dump_model_yaml(model))


def write_json(path: Path, data: Any, *, indent: int = 2) -> None:
    """Write data to JSON file atomically."""
    content = json.dumps(data, indent=indent, ensure_ascii=False)
    _atomic_write(path, content)


def write_text(path: Path, content: str) -> None:
    """Write text content to file atomically."""
    _atomic_write(path, content)


def append_jsonl(path: Path, record: dict) -> None:
    """Append a JSON record as a new line to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def ensure_parent_dir(path: Path) -> None:
    """Ensure the parent directory of path exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
