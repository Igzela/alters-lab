"""Repository factory — selects and caches the active repository implementation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from alters_lab.repository.base import Repository
from alters_lab.repository.sqlite_repo import SqliteRepository
from alters_lab.repository.yaml_repo import YamlRepository

_REPO: Repository | None = None
_REPO_TYPE: str = "yaml"


def configure_repository(
    repo_type: str = "yaml",
    db_path: Path | None = None,
    repo_root: Path | None = None,
) -> Repository:
    """Configure and return the active repository.

    Args:
        repo_type: "yaml" or "sqlite"
        db_path: Path for SQLite database (default: alters/product/alters_lab.db)
        repo_root: Root directory for YAML repo
    """
    global _REPO, _REPO_TYPE

    if repo_type == "sqlite":
        if db_path is None:
            root = repo_root or Path(__file__).resolve().parents[5]
            db_path = root / "alters" / "product" / "alters_lab.db"
        _REPO = SqliteRepository(db_path)
    else:
        _REPO = YamlRepository(repo_root)

    _REPO_TYPE = repo_type
    return _REPO


def get_repository() -> Repository:
    """Get the active repository. Auto-configures from environment if not set."""
    global _REPO
    if _REPO is None:
        env_type = os.environ.get("ALTERS_LAB_REPO", "yaml")
        configure_repository(repo_type=env_type)
    return _REPO


def get_repo_type() -> str:
    return _REPO_TYPE


def reset_repository() -> None:
    """Reset the global repository (for testing)."""
    global _REPO
    if isinstance(_REPO, SqliteRepository):
        _REPO.close()
    _REPO = None
