"""Tests for behavior metrics catalog with research metadata."""

from __future__ import annotations

from pathlib import Path

import pytest

from alters_lab.schemas.behavior_metrics_catalog import (
    METRIC_ID_TO_FIELD,
    load_catalog,
    load_known_metric_ids,
)


_REPO_ROOT = Path(__file__).resolve().parents[3]
_CATALOG_PATH = (
    _REPO_ROOT / "alters" / "product" / "behavior_metrics" / "catalog" / "behavior_metric_set_v0_2.yaml"
)


@pytest.fixture
def catalog():
    return load_catalog(_CATALOG_PATH)


def test_catalog_loads(catalog):
    assert catalog.behavior_metric_set.id == "behavior_metric_set_v0_2"
    assert len(catalog.behavior_metric_set.metrics) == 9


def test_every_metric_has_literature_construct(catalog):
    for metric in catalog.behavior_metric_set.metrics:
        assert metric.literature_construct is not None, f"{metric.id} missing literature_construct"
        assert metric.literature_construct.primary, f"{metric.id} missing primary construct"


def test_every_metric_has_predicted_domains(catalog):
    for metric in catalog.behavior_metric_set.metrics:
        assert len(metric.predicted_domains) > 0, f"{metric.id} missing predicted_domains"


def test_every_metric_has_direction(catalog):
    for metric in catalog.behavior_metric_set.metrics:
        assert metric.direction in ("higher_is_better", "lower_is_better"), (
            f"{metric.id} has invalid direction: {metric.direction}"
        )


def test_evidence_source_ids_resolve(catalog):
    source_ids = {s.source_id for s in catalog.behavior_metric_set.evidence_sources}
    for metric in catalog.behavior_metric_set.metrics:
        for eid in metric.evidence_source_ids:
            assert eid in source_ids, f"{metric.id} references unknown evidence_source_id: {eid}"


def test_metric_id_to_field_covers_all(catalog):
    metric_ids = {m.id for m in catalog.behavior_metric_set.metrics}
    assert set(METRIC_ID_TO_FIELD.keys()) == metric_ids


def test_no_duplicate_metric_ids(catalog):
    ids = [m.id for m in catalog.behavior_metric_set.metrics]
    assert len(ids) == len(set(ids)), f"Duplicate metric IDs found: {[x for x in ids if ids.count(x) > 1]}"


def test_evidence_sources_defined(catalog):
    assert len(catalog.behavior_metric_set.evidence_sources) >= 7


def test_predicted_domains_use_valid_values(catalog):
    valid_domains = {"career_education", "financial", "health", "relationship", "subjective_wellbeing"}
    for metric in catalog.behavior_metric_set.metrics:
        for domain in metric.predicted_domains:
            assert domain in valid_domains, f"{metric.id} has invalid predicted_domain: {domain}"
