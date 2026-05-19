"""Read-only CLI for validating the sealed active YAML chain."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from alters_lab.loaders import (
    default_project_root,
    load_active_yaml_chain,
    summarize_active_yaml_chain,
    validate_active_yaml_chain,
)

REPORT_ID = "ACTIVE-YAML-VALIDATION"
SCHEMA_VERSION = 1


def is_forbidden_output_path(path: Path, project_root: Path) -> bool:
    """Return true if resolved output path is inside a forbidden directory."""
    resolved = path.resolve()
    for forbidden in ("alters/current", "alters/calibration", "alters/archive"):
        if resolved.is_relative_to((project_root / forbidden).resolve()):
            return True
    return False


def _build_report(
    *,
    ok: bool,
    status: str,
    errors: list[str],
    warnings: list[str],
    summary: dict,
    artifacts_checked: list[str],
) -> dict:
    return {
        "report_id": REPORT_ID,
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "summary": summary,
        "artifacts_checked": artifacts_checked,
        "boundary_confirmations": {
            "read_only_validation": True,
            "active_yaml_modified": False,
            "calibration_score_created": False,
            "drift_computed": False,
            "archive_created": False,
            "llm_provider_used": False,
            "frontend_added": False,
            "database_added": False,
            "generation_runtime_added": False,
        },
    }


def _artifacts_checked(project_root: Path) -> list[str]:
    current = project_root / "alters" / "current"
    date = "2026-05-19"
    return [
        "alters/current/snapshot.yaml",
        "alters/current/branches.yaml",
        "alters/current/alters/alter_A.yaml",
        "alters/current/alters/alter_B.yaml",
        "alters/current/alters/alter_C.yaml",
        "alters/current/alters/alter_D.yaml",
        f"alters/current/value_alignment/alignment_{date}.yaml",
        f"alters/current/dialogue/dialogue_alter_D_{date}.yaml",
        "alters/current/reality_trace.yaml",
    ]


def main(argv: list[str] | None = None) -> int:
    """Run the active YAML validation CLI. Returns exit code."""
    parser = argparse.ArgumentParser(
        description="Validate the sealed active YAML chain."
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true",
        help="Print JSON report to stdout instead of human-readable text.",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Write JSON report to explicit output path.",
    )
    parser.add_argument(
        "--project-root", type=Path, default=None,
        help="Optional explicit repo root.",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat warnings as failure.",
    )

    args = parser.parse_args(argv)

    project_root = args.project_root or default_project_root()

    # Check forbidden output path early
    if args.output is not None:
        if is_forbidden_output_path(args.output, project_root):
            print("ERROR: output path is forbidden", file=sys.stderr)
            return 2

    # Load
    try:
        chain = load_active_yaml_chain(project_root)
    except Exception as exc:
        if args.json_output:
            report = _build_report(
                ok=False,
                status="ERROR",
                errors=[str(exc)],
                warnings=[],
                summary={},
                artifacts_checked=_artifacts_checked(project_root),
            )
            print(json.dumps(report, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    # Validate
    result = validate_active_yaml_chain(chain)
    summary = summarize_active_yaml_chain(chain)

    ok = result.ok
    status = "PASS" if ok else "FAIL"

    if args.strict and result.warnings:
        ok = False
        status = "FAIL"

    report = _build_report(
        ok=ok,
        status=status,
        errors=result.errors,
        warnings=result.warnings,
        summary=summary,
        artifacts_checked=_artifacts_checked(project_root),
    )

    # Output
    if args.json_output or args.output:
        report_json = json.dumps(report, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report_json, encoding="utf-8")
        if args.json_output:
            print(report_json)
    else:
        # Human-readable output
        print(f"Status: {status}")
        print(f"OK: {ok}")
        if result.errors:
            print(f"Errors ({len(result.errors)}):")
            for e in result.errors:
                print(f"  - {e}")
        if result.warnings:
            print(f"Warnings ({len(result.warnings)}):")
            for w in result.warnings:
                print(f"  - {w}")
        print(f"Selected branch: {summary.get('selected_branch')}")
        print(f"Primary candidate: {summary.get('primary_candidate')}")
        print(f"Artifacts checked: {len(_artifacts_checked(project_root))}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
