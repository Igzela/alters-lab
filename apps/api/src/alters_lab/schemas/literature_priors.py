"""Literature prior catalog schema and loader.

NOT a trained model. NOT individual prediction.
Deterministic curated prior anchors for cautious base-rate reasoning.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class EvidenceSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    label: str
    source_type: Literal[
        "longitudinal_dataset",
        "meta_analysis",
        "review",
        "guideline",
        "benchmark_context",
    ]
    population_notes: str = ""
    transfer_risk: Literal["low", "medium", "high"] = "medium"
    citation_hint: str = ""


class MeasuredBy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    behavior_metrics: list[str] = Field(default_factory=list)
    predictor_profile_fields: list[str] = Field(default_factory=list)


class Construct(BaseModel):
    model_config = ConfigDict(extra="forbid")

    construct_id: str
    label: str
    description: str
    measured_by: MeasuredBy = Field(default_factory=MeasuredBy)


class ConstructDomainLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    construct_id: str
    predicted_domain: Literal[
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    expected_direction: Literal["positive", "negative", "mixed"]
    evidence_strength: Literal["weak", "moderate", "strong"]
    transfer_risk: Literal["low", "medium", "high"]
    explanation: str
    evidence_source_ids: list[str] = Field(default_factory=list)


class Prior(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prior_id: str
    branch_feature: str
    predicted_domain: Literal[
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    base_rate_direction: Literal["favorable", "unfavorable", "mixed", "unknown"]
    prior_confidence: Literal["low", "medium", "high"]
    transfer_risk: Literal["low", "medium", "high"]
    explanation: str
    evidence_source_ids: list[str] = Field(default_factory=list)


class LiteraturePriorCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    catalog_id: str
    version: str
    created_at: str
    description: str = ""
    evidence_sources: list[EvidenceSource] = Field(default_factory=list)
    constructs: list[Construct] = Field(default_factory=list)
    construct_domain_links: list[ConstructDomainLink] = Field(default_factory=list)
    priors: list[Prior] = Field(default_factory=list)


DEFAULT_CATALOG_PATH = (
    Path(__file__).resolve().parents[5]
    / "alters"
    / "product"
    / "literature_priors"
    / "catalog"
    / "literature_prior_catalog_v0_1.yaml"
)


def load_literature_prior_catalog(catalog_path: Path | None = None) -> LiteraturePriorCatalog:
    path = catalog_path or DEFAULT_CATALOG_PATH
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return LiteraturePriorCatalog(**data)


def get_priors_for_domain(
    catalog: LiteraturePriorCatalog,
    domain: str,
) -> list[Prior]:
    return [p for p in catalog.priors if p.predicted_domain == domain]


def get_constructs_for_domain(
    catalog: LiteraturePriorCatalog,
    domain: str,
) -> list[ConstructDomainLink]:
    return [cdl for cdl in catalog.construct_domain_links if cdl.predicted_domain == domain]
