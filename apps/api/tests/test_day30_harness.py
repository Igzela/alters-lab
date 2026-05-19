"""Tests for the Day 30 demo harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from alters_lab.api.snapshot_intake import store
from alters_lab.demo.day30_harness import (
    run_day30_demo,
    validate_active_yaml_chain,
    validate_no_forbidden_components,
)
from alters_lab.main import app


@pytest.fixture(autouse=True)
def _clear_store():
    store.clear()
    yield
    store.clear()


def test_run_day30_demo_returns_evidence_with_all_steps_passing(tmp_path: Path):
    evidence = run_day30_demo(output_path=tmp_path / "evidence.json")
    assert evidence["all_pass"] is True
    for step in evidence["steps"]:
        assert step["pass"] is True, f"Step {step['step']} failed: {step}"
    assert "active_yaml_chain" in evidence["validations"]
    assert "no_forbidden_components" in evidence["validations"]


def test_validate_active_yaml_chain_passes():
    result = validate_active_yaml_chain()
    assert result["all_pass"] is True, f"Checks: {result['checks']}"


def test_validate_no_forbidden_components_passes():
    result = validate_no_forbidden_components()
    assert result["all_pass"] is True, f"Checks: {result['checks']}"


def test_demo_evidence_report_can_be_written_to_tmp(tmp_path: Path):
    output = tmp_path / "DEMO_EVIDENCE_DAY30.json"
    evidence = run_day30_demo(output_path=output)
    assert output.exists()
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded == evidence


def test_harness_does_not_modify_active_yaml(tmp_path: Path):
    snapshot_path = Path("alters/current/snapshot.yaml")
    before = snapshot_path.read_text(encoding="utf-8") if snapshot_path.exists() else None

    client = TestClient(app)
    store.clear()

    # Run through the full flow
    r = client.post("/snapshot-intake/sessions")
    sid = r.json()["session_id"]
    for anchor, answer in [
        ("heaviest_constraint", "test constraint"),
        ("most_unclear", "test unclear"),
        ("unwilling_to_give_up", "test unwilling"),
    ]:
        client.post(
            f"/snapshot-intake/sessions/{sid}/answers",
            json={"anchor": anchor, "answer": answer},
        )
    client.post(f"/snapshot-intake/sessions/{sid}/confirm")

    after = snapshot_path.read_text(encoding="utf-8") if snapshot_path.exists() else None
    assert before == after
