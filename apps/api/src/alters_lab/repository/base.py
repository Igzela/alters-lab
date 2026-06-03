"""Abstract repository interface for data persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Repository(ABC):
    """Abstract base for all repository implementations.

    Each area (e.g. forecast_snapshots, model_cards) is a collection.
    Records are dicts keyed by record_id.
    """

    @abstractmethod
    def write(self, area: str, record_id: str, data: dict[str, Any]) -> Path:
        """Write a record. Returns the storage path."""
        ...

    @abstractmethod
    def read(self, area: str, record_id: str) -> dict[str, Any]:
        """Read a record. Raises FileNotFoundError if not found."""
        ...

    @abstractmethod
    def list_records(self, area: str) -> list[dict[str, Any]]:
        """List all records in an area."""
        ...

    @abstractmethod
    def delete(self, area: str, record_id: str) -> Path:
        """Delete a record. Raises FileNotFoundError if not found."""
        ...

    @abstractmethod
    def exists(self, area: str, record_id: str) -> bool:
        """Check if a record exists."""
        ...

    def transaction(self) -> TransactionContext:
        """Return a transaction context manager. Default is no-op."""
        return _NoOpTransaction()

    def export_area(self, area: str) -> list[dict[str, Any]]:
        """Export all records in an area as a list of dicts."""
        return self.list_records(area)

    def import_area(self, area: str, records: list[dict[str, Any]], id_key: str = "record_id") -> int:
        """Import records into an area. Returns count imported."""
        count = 0
        for record in records:
            record_id = record.get(id_key) or record.get(f"{area.rstrip('s')}_id") or record.get("model_id") or record.get("artifact_id")
            if not record_id:
                continue
            self.write(area, record_id, record)
            count += 1
        return count


class TransactionContext:
    """Transaction context manager."""

    def __enter__(self) -> TransactionContext:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...


class _NoOpTransaction(TransactionContext):
    """No-op transaction for YAML repo."""
    pass
