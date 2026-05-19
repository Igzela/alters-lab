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
    first_line = content.split("\n", 1)[0].strip() if content else ""
    return {"exists": True, "title": first_line.lstrip("# ").strip()}


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


def build_evidence_status(root: Path | None = None) -> dict:
    paths = evidence_paths(root)
    result: dict = {"day30_demo": {}, "active_yaml_validation": {}, "phase1_closeout": {}}

    for key, path in paths.items():
        if not path.exists():
            result[key] = {"status": "MISSING", "exists": False}
            continue

        if path.suffix == ".json":
            try:
                report = load_json_report(path)
            except Exception as exc:
                result[key] = {"status": "ERROR", "exists": True, "error": str(exc)}
                continue

            if key == "day30_demo":
                result[key] = {"status": "ok", "exists": True, **summarize_day30_demo(report)}
            elif key == "active_yaml_validation":
                result[key] = {"status": "ok", "exists": True, **summarize_active_yaml_validation(report)}
        else:
            result[key] = {"status": "ok", "exists": True, **load_optional_text_metadata(path)}

    return result
