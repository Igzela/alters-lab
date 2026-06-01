"""Branch milestone schema."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


class BranchMilestoneRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    milestone_id: str
    branch_id: str
    title: str
    description: str = ""
    target_completion_date: date
    observable_done_definition: str
    status: Literal["planned", "active", "completed", "abandoned"] = "active"
    created_at: str
