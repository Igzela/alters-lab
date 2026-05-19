from __future__ import annotations

from pathlib import Path

import yaml

from alters_lab.loaders.models import ActiveYamlChain, ActiveYamlPaths, ValidationResult

_SEALED_BASELINE_DATE = "2026-05-19"


def default_project_root() -> Path:
    return Path(__file__).resolve().parents[5]


def active_yaml_paths(project_root: Path | None = None) -> ActiveYamlPaths:
    root = project_root or default_project_root()
    current = root / "alters" / "current"
    alters_dir = current / "alters"
    date = _SEALED_BASELINE_DATE

    return ActiveYamlPaths(
        snapshot=current / "snapshot.yaml",
        branches=current / "branches.yaml",
        alters={
            "alter_A": alters_dir / "alter_A.yaml",
            "alter_B": alters_dir / "alter_B.yaml",
            "alter_C": alters_dir / "alter_C.yaml",
            "alter_D": alters_dir / "alter_D.yaml",
        },
        value_alignment=current / "value_alignment" / f"alignment_{date}.yaml",
        dialogue=current / "dialogue" / f"dialogue_alter_D_{date}.yaml",
        reality_trace=current / "reality_trace.yaml",
    )


def load_yaml_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict from {path}, got {type(data).__name__}")
    return data


def load_active_yaml_chain(project_root: Path | None = None) -> ActiveYamlChain:
    paths = active_yaml_paths(project_root)
    return ActiveYamlChain(
        snapshot=load_yaml_file(paths.snapshot),
        branches=load_yaml_file(paths.branches),
        alters={k: load_yaml_file(v) for k, v in paths.alters.items()},
        value_alignment=load_yaml_file(paths.value_alignment),
        dialogue=load_yaml_file(paths.dialogue),
        reality_trace=load_yaml_file(paths.reality_trace),
    )


def validate_active_yaml_chain(chain: ActiveYamlChain) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    # --- snapshot ---
    snap = chain.snapshot
    if "snapshot" not in snap:
        errors.append("snapshot: top-level 'snapshot' key missing")
    else:
        s = snap["snapshot"]
        intake = s.get("intake_status", {})
        if intake.get("phase") != "completed":
            errors.append("snapshot: intake_status.phase != 'completed'")
        if intake.get("pending_anchor") is not None:
            errors.append("snapshot: pending_anchor is not null")
        anchors = s.get("anchors", {})
        for name in ("heaviest_constraint", "most_unclear", "unwilling_to_give_up"):
            val = anchors.get(name)
            if not val or not str(val).strip():
                errors.append(f"snapshot: anchors.{name} is empty")

    # --- branches ---
    br = chain.branches
    bd = br.get("branch_discovery", {})
    if bd.get("status") != "completed":
        errors.append("branches: branch_discovery.status != 'completed'")
    branch_list = br.get("branches", [])
    if len(branch_list) != 4:
        errors.append(f"branches: expected 4 branches, got {len(branch_list)}")
    expected_ids = {"branch_A", "branch_B", "branch_C", "branch_D"}
    actual_ids = {b.get("id") for b in branch_list}
    if actual_ids != expected_ids:
        errors.append(f"branches: ids mismatch: {actual_ids} != {expected_ids}")
    for b in branch_list:
        iw = b.get("incompatible_with", [])
        if not iw:
            errors.append(f"branches: {b.get('id', '?')} incompatible_with is empty")

    # --- alters ---
    if len(chain.alters) != 4:
        errors.append(f"alters: expected 4, got {len(chain.alters)}")
    for key in ("alter_A", "alter_B", "alter_C", "alter_D"):
        a = chain.alters.get(key, {})
        if a.get("id") != key:
            errors.append(f"alters: {key} id mismatch: {a.get('id')}")
        expected_branch = key.replace("alter_", "branch_")
        if a.get("branch_ref") != expected_branch:
            errors.append(f"alters: {key} branch_ref != {expected_branch}")
        if a.get("generated_at") != _SEALED_BASELINE_DATE:
            errors.append(f"alters: {key} generated_at != {_SEALED_BASELINE_DATE}")
        if a.get("time_horizon") != "1.5-2年后":
            errors.append(f"alters: {key} time_horizon != '1.5-2年后'")
        src = a.get("source_refs", {})
        if src.get("snapshot_ref") != "alters/current/snapshot.yaml":
            errors.append(f"alters: {key} source_refs.snapshot_ref wrong")
        if src.get("branches_ref") != "alters/current/branches.yaml":
            errors.append(f"alters: {key} source_refs.branches_ref wrong")
        if src.get("rubric_ref") != "alters/calibration/rubric.yaml":
            errors.append(f"alters: {key} source_refs.rubric_ref wrong")
        qs = a.get("quality_status", {})
        if qs.get("human_confirmed") is not True:
            errors.append(f"alters: {key} quality_status.human_confirmed != true")
        if qs.get("active") is not True:
            errors.append(f"alters: {key} quality_status.active != true")

    # --- value_alignment ---
    va = chain.value_alignment
    var = va.get("value_alignment_report", {})
    if var.get("status") != "human_confirmed":
        errors.append("value_alignment: status != 'human_confirmed'")
    fi = var.get("final_interpretation", {})
    if fi.get("primary_candidate") != "branch_D":
        errors.append("value_alignment: final_interpretation.primary_candidate != branch_D")
    pc = var.get("provisional_commitment", {})
    if pc.get("selected_branch") != "branch_D":
        errors.append("value_alignment: provisional_commitment.selected_branch != branch_D")

    # --- dialogue ---
    dl = chain.dialogue
    d = dl.get("dialogue", {})
    if d.get("status") != "human_confirmed_static_artifact":
        errors.append("dialogue: status != 'human_confirmed_static_artifact'")
    sess = d.get("session", {})
    if sess.get("alter_ref") != "alters/current/alters/alter_D.yaml":
        errors.append("dialogue: session.alter_ref wrong")
    cp = d.get("context_policy", {})
    if cp.get("provider_used") is not None:
        errors.append("dialogue: context_policy.provider_used is not null")
    if cp.get("runtime_used") is not False:
        errors.append("dialogue: context_policy.runtime_used is not false")

    # --- reality_trace ---
    rt = chain.reality_trace
    rtr = rt.get("reality_trace", {})
    if rtr.get("status") != "active":
        errors.append("reality_trace: status != 'active'")
    cp_rt = rtr.get("current_probe", {})
    if cp_rt.get("selected_branch") != "branch_D":
        errors.append("reality_trace: current_probe.selected_branch != branch_D")
    d14 = cp_rt.get("day_14_gate", {})
    if d14.get("status") != "completed":
        errors.append("reality_trace: day_14_gate.status != 'completed'")
    d30 = cp_rt.get("day_30_gate", {})
    d30_status = d30.get("status")
    if d30_status not in ("pending", "passed", "completed"):
        errors.append(f"reality_trace: day_30_gate.status invalid: {d30_status}")
    cr = rtr.get("calibration_readiness", {})
    if cr.get("ready_for_reality_score") is not False:
        errors.append("reality_trace: calibration_readiness.ready_for_reality_score != false")

    return ValidationResult(ok=len(errors) == 0, errors=errors, warnings=warnings)


def summarize_active_yaml_chain(chain: ActiveYamlChain) -> dict:
    snap = chain.snapshot.get("snapshot", {})
    intake = snap.get("intake_status", {})
    rtr = chain.reality_trace.get("reality_trace", {})
    cp = rtr.get("current_probe", {})
    cr = rtr.get("calibration_readiness", {})
    var = chain.value_alignment.get("value_alignment_report", {})
    fi = var.get("final_interpretation", {})
    pc = var.get("provisional_commitment", {})

    return {
        "snapshot_phase": intake.get("phase"),
        "branch_count": len(chain.branches.get("branches", [])),
        "alter_ids": sorted(chain.alters.keys()),
        "primary_candidate": fi.get("primary_candidate"),
        "selected_branch": pc.get("selected_branch"),
        "reality_trace_status": rtr.get("status"),
        "day_14_gate": cp.get("day_14_gate", {}).get("status"),
        "day_30_gate": cp.get("day_30_gate", {}).get("status"),
        "calibration_ready": cr.get("ready_for_reality_score"),
    }
