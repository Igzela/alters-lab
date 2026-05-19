from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, model_validator


class IntakePhase(str, Enum):
    not_started = "not_started"
    asking_heaviest_constraint = "asking_heaviest_constraint"
    asking_most_unclear = "asking_most_unclear"
    asking_unwilling_to_give_up = "asking_unwilling_to_give_up"
    ready_for_snapshot_confirmation = "ready_for_snapshot_confirmation"
    completed = "completed"


class AnchorName(str, Enum):
    heaviest_constraint = "heaviest_constraint"
    most_unclear = "most_unclear"
    unwilling_to_give_up = "unwilling_to_give_up"


class SnapshotAnchors(BaseModel):
    heaviest_constraint: str = ""
    most_unclear: str = ""
    unwilling_to_give_up: str = ""


class SnapshotContext(BaseModel):
    current_commitments: list[str] = []
    external_deadlines: list[str] = []
    energy_state: str = ""


class SnapshotIntakeStatus(BaseModel):
    phase: IntakePhase = IntakePhase.not_started
    completed_anchors: list[AnchorName] = []
    pending_anchor: AnchorName | None = AnchorName.heaviest_constraint


class EvidencePolicy(BaseModel):
    source_mode: str = "self_report_only_phase0"
    confidence: str = "unset"
    unresolved_assumptions: list[str] = []


class Snapshot(BaseModel):
    date: str | None = None
    version: int = 1
    anchors: SnapshotAnchors = SnapshotAnchors()
    context: SnapshotContext = SnapshotContext()
    intake_status: SnapshotIntakeStatus = SnapshotIntakeStatus()
    evidence_policy: EvidencePolicy = EvidencePolicy()
    notes: list[str] = []

    @model_validator(mode="after")
    def validate_completion(self) -> Snapshot:
        if self.version < 1:
            raise ValueError("version must be >= 1")
        if self.intake_status.phase == IntakePhase.completed:
            if not self.anchors.heaviest_constraint:
                raise ValueError("completed snapshot requires heaviest_constraint")
            if not self.anchors.most_unclear:
                raise ValueError("completed snapshot requires most_unclear")
            if not self.anchors.unwilling_to_give_up:
                raise ValueError("completed snapshot requires unwilling_to_give_up")
            required = {
                AnchorName.heaviest_constraint,
                AnchorName.most_unclear,
                AnchorName.unwilling_to_give_up,
            }
            if set(self.intake_status.completed_anchors) != required:
                raise ValueError("completed snapshot must list all three anchors")
            if self.intake_status.pending_anchor is not None:
                raise ValueError("completed snapshot must have null pending_anchor")
        return self
