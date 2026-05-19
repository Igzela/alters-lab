"""Day 30 Demo Harness — bounded read-only validator for CYCLE-001 v0.1 demo."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from alters_lab.api.snapshot_intake import store
from alters_lab.main import app
from alters_lab.services.snapshot_export import snapshot_to_yaml, write_snapshot_yaml

PROJECT_ROOT = Path(__file__).resolve().parents[5]
ALTERS_CURRENT = PROJECT_ROOT / "alters" / "current"
ALERTS_DIR = PROJECT_ROOT / "apps" / "api" / "src"


# ---------------------------------------------------------------------------
# Step helpers
# ---------------------------------------------------------------------------

def _step_health(client: TestClient) -> dict:
    r = client.get("/health")
    return {"step": "health_check", "pass": r.status_code == 200, "status_code": r.status_code}


def _step_create_session(client: TestClient) -> dict:
    r = client.post("/snapshot-intake/sessions")
    return {
        "step": "create_session",
        "pass": r.status_code == 201,
        "status_code": r.status_code,
        "session_id": r.json().get("session_id"),
    }


def _step_submit_anchors(client: TestClient, session_id: str) -> dict:
    anchors = [
        ("heaviest_constraint", "Demo: primary constraint for testing"),
        ("most_unclear", "Demo: most unclear dimension"),
        ("unwilling_to_give_up", "Demo: non-negotiable value"),
    ]
    results = []
    for anchor, answer in anchors:
        r = client.post(
            f"/snapshot-intake/sessions/{session_id}/answers",
            json={"anchor": anchor, "answer": answer},
        )
        results.append({"anchor": anchor, "status_code": r.status_code})
    all_ok = all(res["status_code"] == 200 for res in results)
    return {"step": "submit_anchors", "pass": all_ok, "results": results}


def _step_confirm(client: TestClient, session_id: str) -> dict:
    r = client.post(f"/snapshot-intake/sessions/{session_id}/confirm")
    return {
        "step": "confirm",
        "pass": r.status_code == 200,
        "status_code": r.status_code,
        "phase": r.json().get("snapshot", {}).get("intake_status", {}).get("phase"),
    }


def _step_confirm_no_yaml_write(client: TestClient, session_id: str) -> dict:
    snapshot_path = ALTERS_CURRENT / "snapshot.yaml"
    before = snapshot_path.read_text(encoding="utf-8") if snapshot_path.exists() else None
    client.post(f"/snapshot-intake/sessions/{session_id}/confirm")
    after = snapshot_path.read_text(encoding="utf-8") if snapshot_path.exists() else None
    unchanged = before == after
    return {"step": "confirm_no_yaml_write", "pass": unchanged}


def _step_export_to_temp(client: TestClient, session_id: str, export_dir: Path | None) -> dict:
    import uuid as _uuid

    export_dir = export_dir or Path("/tmp")
    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = export_dir / f"demo_export_snapshot_{_uuid.uuid4().hex[:8]}.yaml"

    snapshot_resp = client.get(f"/snapshot-intake/sessions/{session_id}")
    intake = snapshot_resp.json()["snapshot"]["intake_status"]
    if intake["phase"] != "completed":
        return {"step": "export_to_temp", "pass": False, "reason": "snapshot not completed"}

    from alters_lab.schemas.snapshot import (
        AnchorName,
        IntakePhase,
        Snapshot,
        SnapshotAnchors,
        SnapshotIntakeStatus,
    )

    anchors_raw = snapshot_resp.json()["snapshot"]["anchors"]
    snapshot = Snapshot(
        anchors=SnapshotAnchors(
            heaviest_constraint=anchors_raw["heaviest_constraint"],
            most_unclear=anchors_raw["most_unclear"],
            unwilling_to_give_up=anchors_raw["unwilling_to_give_up"],
        ),
        intake_status=SnapshotIntakeStatus(
            phase=IntakePhase.completed,
            completed_anchors=[
                AnchorName.heaviest_constraint,
                AnchorName.most_unclear,
                AnchorName.unwilling_to_give_up,
            ],
            pending_anchor=None,
        ),
    )
    written = write_snapshot_yaml(snapshot, export_path)
    return {"step": "export_to_temp", "pass": written.exists(), "export_path": str(written)}


def validate_active_yaml_chain() -> dict:
    """Validate that the active YAML artifact chain is structurally consistent."""
    checks: dict[str, Any] = {}

    # snapshot.yaml
    snap_path = ALTERS_CURRENT / "snapshot.yaml"
    if snap_path.exists():
        snap = yaml.safe_load(snap_path.read_text(encoding="utf-8"))
        phase = snap.get("snapshot", {}).get("intake_status", {}).get("phase")
        checks["snapshot_yaml_exists"] = True
        checks["snapshot_phase_completed"] = phase == "completed"
    else:
        checks["snapshot_yaml_exists"] = False
        checks["snapshot_phase_completed"] = False

    # branches.yaml
    branches_path = ALTERS_CURRENT / "branches.yaml"
    if branches_path.exists():
        br = yaml.safe_load(branches_path.read_text(encoding="utf-8"))
        bd = br.get("branch_discovery", {})
        checks["branches_yaml_exists"] = True
        checks["branches_discovery_completed"] = bd.get("status") == "completed"
    else:
        checks["branches_yaml_exists"] = False
        checks["branches_discovery_completed"] = False

    # alter files
    alters_dir = ALTERS_CURRENT / "alters"
    alter_files = ["alter_A.yaml", "alter_B.yaml", "alter_C.yaml", "alter_D.yaml"]
    for af in alter_files:
        af_path = alters_dir / af
        if af_path.exists():
            data = yaml.safe_load(af_path.read_text(encoding="utf-8"))
            has_source_refs = "source_refs" in data
            has_quality_status = "quality_status" in data
            checks[f"{af}_exists"] = True
            checks[f"{af}_has_source_refs"] = has_source_refs
            checks[f"{af}_has_quality_status"] = has_quality_status
        else:
            checks[f"{af}_exists"] = False
            checks[f"{af}_has_source_refs"] = False
            checks[f"{af}_has_quality_status"] = False

    # value alignment
    va_dir = ALTERS_CURRENT / "value_alignment"
    alignment_files = list(va_dir.glob("alignment_*.yaml")) if va_dir.exists() else []
    checks["alignment_file_exists"] = len(alignment_files) > 0

    # dialogue
    dl_dir = ALTERS_CURRENT / "dialogue"
    dialogue_files = list(dl_dir.glob("dialogue_*.yaml")) if dl_dir.exists() else []
    checks["dialogue_file_exists"] = len(dialogue_files) > 0

    # reality_trace.yaml
    rt_path = ALTERS_CURRENT / "reality_trace.yaml"
    if rt_path.exists():
        rt = yaml.safe_load(rt_path.read_text(encoding="utf-8"))
        rt_status = rt.get("reality_trace", {}).get("status")
        checks["reality_trace_yaml_exists"] = True
        checks["reality_trace_status_active"] = rt_status == "active"
    else:
        checks["reality_trace_yaml_exists"] = False
        checks["reality_trace_status_active"] = False

    all_pass = all(v is True for v in checks.values())
    return {"all_pass": all_pass, "checks": checks}


def validate_no_forbidden_components() -> dict:
    """Check that no forbidden runtime modules, providers, databases, or frontends exist."""
    checks: dict[str, bool] = {}

    # .env file
    checks["no_env_file"] = not (PROJECT_ROOT / ".env").exists()

    # provider config in source
    api_src = ALERTS_DIR
    forbidden_patterns = ["openai", "anthropic", "ollama", "llm_provider", "database", "sqlalchemy"]
    for pat in forbidden_patterns:
        matches = list(api_src.rglob(f"*{pat}*"))
        matches = [m for m in matches if m.suffix in (".py", ".yaml", ".yml", ".json")]
        checks[f"no_{pat}_config"] = len(matches) == 0

    # frontend code
    web_dir = PROJECT_ROOT / "apps" / "web"
    checks["no_frontend_code"] = not web_dir.exists()

    # runtime dialogue / calibration / archive modules
    for mod_name in ["dialogue_runtime", "calibration_runtime", "archive_runtime"]:
        found = list(api_src.rglob(f"*{mod_name}*"))
        checks[f"no_{mod_name}"] = len(found) == 0

    all_pass = all(v is True for v in checks.values())
    return {"all_pass": all_pass, "checks": checks}


# ---------------------------------------------------------------------------
# Main harness
# ---------------------------------------------------------------------------

def run_day30_demo(
    output_path: Path | None = None,
    export_dir: Path | None = None,
) -> dict:
    """Run the bounded Day 30 demo and return machine-readable evidence dict."""
    client = TestClient(app)
    store.clear()

    evidence: dict[str, Any] = {"steps": [], "validations": {}}

    # Step 1: health
    evidence["steps"].append(_step_health(client))

    # Step 2: create session
    create_result = _step_create_session(client)
    evidence["steps"].append(create_result)
    session_id = create_result.get("session_id")
    if not session_id:
        evidence["all_pass"] = False
        return evidence

    # Step 3: submit anchors in order
    evidence["steps"].append(_step_submit_anchors(client, session_id))

    # Step 4: confirm
    evidence["steps"].append(_step_confirm(client, session_id))

    # Step 5: confirm does not write active YAML
    evidence["steps"].append(_step_confirm_no_yaml_write(client, session_id))

    # Step 6: export to temp YAML
    evidence["steps"].append(_step_export_to_temp(client, session_id, export_dir))

    # Step 7: validate active YAML chain
    evidence["validations"]["active_yaml_chain"] = validate_active_yaml_chain()

    # Step 8: validate no forbidden components
    evidence["validations"]["no_forbidden_components"] = validate_no_forbidden_components()

    all_pass = (
        all(s["pass"] for s in evidence["steps"])
        and evidence["validations"]["active_yaml_chain"]["all_pass"]
        and evidence["validations"]["no_forbidden_components"]["all_pass"]
    )
    evidence["all_pass"] = all_pass

    # Write evidence report
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")

    return evidence
