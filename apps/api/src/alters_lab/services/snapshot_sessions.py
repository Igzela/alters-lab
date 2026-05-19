from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from alters_lab.schemas.snapshot import Snapshot


class SnapshotSession:
    __slots__ = ("session_id", "snapshot", "created_at", "updated_at")

    def __init__(self, snapshot: Snapshot) -> None:
        now = datetime.now(timezone.utc)
        self.session_id: UUID = uuid4()
        self.snapshot: Snapshot = snapshot
        self.created_at: datetime = now
        self.updated_at: datetime = now


class InMemorySnapshotSessionStore:
    def __init__(self) -> None:
        self._sessions: dict[UUID, SnapshotSession] = {}

    def create_session(self, snapshot: Snapshot) -> SnapshotSession:
        session = SnapshotSession(snapshot=snapshot)
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: UUID) -> SnapshotSession | None:
        return self._sessions.get(session_id)

    def update_session(self, session: SnapshotSession) -> SnapshotSession:
        session.updated_at = datetime.now(timezone.utc)
        self._sessions[session.session_id] = session
        return session

    def clear(self) -> None:
        self._sessions.clear()
