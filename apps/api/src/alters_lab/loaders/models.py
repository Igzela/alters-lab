from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ActiveYamlPaths:
    snapshot: Path
    branches: Path
    alters: dict[str, Path]
    value_alignment: Path
    dialogue: Path
    reality_trace: Path


@dataclass
class ActiveYamlChain:
    snapshot: dict
    branches: dict
    alters: dict[str, dict]
    value_alignment: dict
    dialogue: dict
    reality_trace: dict


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
