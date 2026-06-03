"""Public prior service — load and query approved population prior artifacts and model cards."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.population_baseline import (
    PopulationBaselineModelCard,
    PopulationPriorArtifact,
)
from alters_lab.services.p6_runtime import list_records, read_record


def _load_model_cards(repo_root: Path | None = None) -> list[PopulationBaselineModelCard]:
    records = list_records("model_cards", repo_root=repo_root)
    return [PopulationBaselineModelCard(**r) for r in records]


def _load_artifacts(repo_root: Path | None = None) -> list[PopulationPriorArtifact]:
    records = list_records("population_prior_artifacts", repo_root=repo_root)
    return [PopulationPriorArtifact(**r) for r in records]


def list_model_cards(repo_root: Path | None = None) -> list[PopulationBaselineModelCard]:
    return _load_model_cards(repo_root)


def get_model_card(model_id: str, repo_root: Path | None = None) -> PopulationBaselineModelCard:
    data = read_record("model_cards", model_id, repo_root=repo_root)
    return PopulationBaselineModelCard(**data)


def list_approved_artifacts(repo_root: Path | None = None) -> list[PopulationPriorArtifact]:
    """List artifacts approved for Route B (data-backed or calibrated only)."""
    artifacts = _load_artifacts(repo_root)
    cards = {c.model_id: c for c in _load_model_cards(repo_root)}
    approved = []
    for a in artifacts:
        card = cards.get(a.model_id)
        if not card:
            continue
        # Route B requires: approval_level == route_b_approved AND
        # artifact_class is data_backed or calibrated (not contextual)
        if (
            card.approval_level == "route_b_approved"
            and a.artifact_class in ("data_backed_baseline", "calibrated_model")
        ):
            approved.append(a)
    return approved


def list_contextual_priors(repo_root: Path | None = None) -> list[PopulationPriorArtifact]:
    """List contextual (literature-only) priors — visible but not Route B approved."""
    artifacts = _load_artifacts(repo_root)
    return [a for a in artifacts if a.artifact_class == "contextual_prior"]


def list_artifacts_for_domain(
    domain: str,
    repo_root: Path | None = None,
) -> list[PopulationPriorArtifact]:
    return [a for a in list_approved_artifacts(repo_root) if a.domain == domain]


def get_artifact(artifact_id: str, repo_root: Path | None = None) -> PopulationPriorArtifact:
    data = read_record("population_prior_artifacts", artifact_id, repo_root=repo_root)
    return PopulationPriorArtifact(**data)


def list_all_artifacts(repo_root: Path | None = None) -> list[PopulationPriorArtifact]:
    return _load_artifacts(repo_root)


def get_domain_coverage(repo_root: Path | None = None) -> dict[str, dict]:
    """Return coverage summary per domain with Route B approval status."""
    all_domains = [
        "career_education",
        "financial",
        "health",
        "relationship",
        "subjective_wellbeing",
    ]
    approved = list_approved_artifacts(repo_root)
    contextual = list_contextual_priors(repo_root)
    cards = {c.model_id: c for c in _load_model_cards(repo_root)}

    coverage = {}
    for domain in all_domains:
        domain_approved = [a for a in approved if a.domain == domain]
        domain_contextual = [a for a in contextual if a.domain == domain]
        if domain_approved:
            best = min(
                domain_approved,
                key=lambda a: {"low": 0, "medium": 1, "high": 2}.get(a.transfer_risk, 2),
            )
            card = cards.get(best.model_id)
            coverage[domain] = {
                "has_approved_artifact": True,
                "artifact_count": len(domain_approved),
                "contextual_prior_count": len(domain_contextual),
                "best_confidence": best.confidence,
                "best_transfer_risk": best.transfer_risk,
                "prior_direction": best.prior_direction,
                "model_family": card.model_family if card else "unknown",
                "artifact_class": best.artifact_class,
                "artifact_ids": [a.artifact_id for a in domain_approved],
                "route_b_status": "approved",
            }
        elif domain_contextual:
            coverage[domain] = {
                "has_approved_artifact": False,
                "artifact_count": 0,
                "contextual_prior_count": len(domain_contextual),
                "best_confidence": "low",
                "best_transfer_risk": "high",
                "prior_direction": "unknown",
                "model_family": "unknown",
                "artifact_class": "contextual_prior",
                "artifact_ids": [a.artifact_id for a in domain_contextual],
                "route_b_status": "contextual_only",
            }
        else:
            coverage[domain] = {
                "has_approved_artifact": False,
                "artifact_count": 0,
                "contextual_prior_count": 0,
                "best_confidence": "low",
                "best_transfer_risk": "high",
                "prior_direction": "unknown",
                "model_family": "unknown",
                "artifact_class": "none",
                "artifact_ids": [],
                "route_b_status": "no_prior",
            }
    return coverage
