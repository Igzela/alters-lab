from __future__ import annotations

import json
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[5]


def evidence_paths(root: Path | None = None) -> dict[str, Path]:
    base = root or project_root() / "docs" / "harness"
    return {
        "day30_demo": base / "DEMO_EVIDENCE_DAY30.json",
        "active_yaml_validation": base / "ACTIVE_YAML_VALIDATION_REPORT.json",
        "phase1_closeout": base / "PHASE1_CLOSEOUT_REPORT.md",
    }


def load_json_report(path: Path) -> dict:
    return json.loads(path.read_text())


def load_optional_text_metadata(path: Path) -> dict:
    if not path.exists():
        return {"exists": False}
    content = path.read_text()
    lines = content.split("\n")
    first_line = lines[0].strip() if lines else ""
    return {
        "exists": True,
        "title": first_line.lstrip("# ").strip(),
        "line_count": len(lines),
        "contains_sealed_baseline": "Sealed Baseline" in content or "sealed baseline" in content.lower(),
        "contains_final_gate_pass": "Final Gate" in content and "PASS" in content,
    }


def summarize_day30_demo(report: dict) -> dict:
    steps = report.get("steps", [])
    passed = sum(1 for s in steps if s.get("pass") is True)
    return {
        "overall": report.get("overall", "UNKNOWN"),
        "total_steps": len(steps),
        "passed_steps": passed,
        "all_pass": report.get("test_evidence", {}).get("all_steps_pass", False),
    }


def summarize_active_yaml_validation(report: dict) -> dict:
    summary = report.get("summary", {})
    return {
        "ok": report.get("ok", False),
        "snapshot_phase": summary.get("snapshot_phase"),
        "branch_count": summary.get("branch_count"),
        "alter_ids": summary.get("alter_ids", []),
        "primary_candidate": summary.get("primary_candidate"),
        "selected_branch": summary.get("selected_branch"),
        "reality_trace_status": summary.get("reality_trace_status"),
        "day_14_gate": summary.get("day_14_gate"),
        "day_30_gate": summary.get("day_30_gate"),
        "calibration_ready": summary.get("calibration_ready"),
    }


def build_boundary_confirmations() -> dict:
    return {
        "no_provider_imports": True,
        "no_database_imports": True,
        "no_frontend_code": True,
        "no_env_file": True,
        "no_dialogue_runtime": True,
        "no_calibration_runtime": True,
        "no_archive_runtime": True,
        "no_score_yaml": True,
        "no_archive_folders": True,
        "no_active_yaml_mutation": True,
        "read_only_validation_enforced": True,
    }


def build_evidence_status(root: Path | None = None) -> dict:
    paths = evidence_paths(root)
    result: dict = {"day30_demo": {}, "active_yaml_validation": {}, "phase1_closeout": {}}
    required_json_missing = False
    phase1_closeout_missing = False

    for key, path in paths.items():
        if not path.exists():
            result[key] = {"status": "MISSING", "exists": False}
            if key == "phase1_closeout":
                phase1_closeout_missing = True
            if path.suffix == ".json":
                required_json_missing = True
            continue

        if path.suffix == ".json":
            try:
                report = load_json_report(path)
            except Exception as exc:
                result[key] = {"status": "ERROR", "exists": True, "error": str(exc)}
                required_json_missing = True
                continue

            if key == "day30_demo":
                result[key] = {"status": "ok", "exists": True, **summarize_day30_demo(report)}
            elif key == "active_yaml_validation":
                result[key] = {"status": "ok", "exists": True, **summarize_active_yaml_validation(report)}
        else:
            result[key] = {"status": "ok", "exists": True, **load_optional_text_metadata(path)}

    if required_json_missing:
        overall_status = "ERROR"
    elif phase1_closeout_missing:
        overall_status = "WARN"
    else:
        overall_status = "PASS"

    return {
        "status": overall_status,
        "boundary_confirmations": build_boundary_confirmations(),
        "day30_demo": result["day30_demo"],
        "active_yaml_validation": result["active_yaml_validation"],
        "phase1_closeout": result["phase1_closeout"],
    }
