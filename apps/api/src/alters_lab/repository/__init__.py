"""Repository layer — abstract interface and implementations for data persistence."""

from alters_lab.repository.base import Repository
from alters_lab.repository.factory import get_repository, configure_repository

__all__ = ["Repository", "get_repository", "configure_repository"]
