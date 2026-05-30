"""Command-line launcher for Alters Lab local app."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from alters_lab.services.data_safety import DataSafetyError, build_backup_plan, create_backup_archive
from alters_lab.services.local_launcher import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    build_doctor_report,
    build_status,
    open_app,
    resolve_layout_for_cli,
    start_server,
    stop_server,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="alters-lab", description="Run Alters Lab local app.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    for name in ("start", "status", "doctor", "open"):
        sub = subcommands.add_parser(name)
        _add_common_options(sub)
        if name == "start":
            sub.add_argument("--foreground", action="store_true")
            sub.add_argument("--no-open", action="store_true")
            sub.add_argument("--dry-run", action="store_true")
        if name == "open":
            sub.add_argument("--no-start", action="store_true")
            sub.add_argument("--dry-run", action="store_true")

    stop = subcommands.add_parser("stop")
    stop.add_argument("--mode", choices=["dev", "packaged"], default=None)
    stop.add_argument("--json", action="store_true")

    backup = subcommands.add_parser("backup")
    backup.add_argument("--mode", choices=["dev", "packaged"], default=None)
    backup.add_argument("--output", default=None)
    backup.add_argument("--include-logs", action="store_true")
    backup.add_argument("--include-config", dest="include_config", action="store_true", default=True)
    backup.add_argument("--no-include-config", dest="include_config", action="store_false")
    backup.add_argument("--include-secrets", action="store_true")
    backup.add_argument("--confirm-include-secrets", default=None)
    backup.add_argument("--dry-run", action="store_true")
    backup.add_argument("--json", action="store_true")

    load_sample = subcommands.add_parser("load-sample", help="Load sample data for new users")
    load_sample.add_argument("--mode", choices=["dev", "packaged"], default=None)
    load_sample.add_argument("--force", action="store_true", help="Overwrite existing data")
    load_sample.add_argument("--json", action="store_true")
    return parser


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--mode", choices=["dev", "packaged"], default=None)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--json", action="store_true")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    layout = resolve_layout_for_cli(args.mode)

    if args.command == "start":
        result = start_server(layout, args.host, args.port, dry_run=args.dry_run, foreground=args.foreground)
    elif args.command == "stop":
        result = stop_server(layout)
    elif args.command == "status":
        result = build_status(layout, args.host, args.port)
    elif args.command == "doctor":
        result = build_doctor_report(layout, args.host, args.port)
    elif args.command == "open":
        result = open_app(layout, args.host, args.port, no_start=args.no_start, dry_run=args.dry_run)
    elif args.command == "backup":
        output = Path(args.output).expanduser() if args.output else None
        try:
            if args.dry_run:
                result = build_backup_plan(
                    layout,
                    output_path=output,
                    include_logs=args.include_logs,
                    include_config=args.include_config,
                    include_secrets=args.include_secrets,
                    confirm_include_secrets=args.confirm_include_secrets,
                )
            else:
                result = create_backup_archive(
                    layout,
                    output_path=output,
                    include_logs=args.include_logs,
                    include_config=args.include_config,
                    include_secrets=args.include_secrets,
                    confirm_include_secrets=args.confirm_include_secrets,
                )
        except DataSafetyError as exc:
            result = {"status": "blocked", "reason": str(exc), "p6_behavior_validated": False, "p6_sealed": False}
    elif args.command == "load-sample":
        result = _load_sample_data(layout, force=args.force)
    else:
        parser.error(f"Unknown command: {args.command}")

    _print_result(result, json_output=args.json)
    return 0


def _load_sample_data(layout: Any, force: bool = False) -> dict[str, Any]:
    """Copy sample data from alters/sample/ into alters/current/."""
    import shutil

    root = layout.project_root if hasattr(layout, "project_root") else Path(layout.data_dir)
    sample_dir = root / "alters" / "sample"
    current_dir = root / "alters" / "current"

    if not sample_dir.exists():
        return {"status": "error", "reason": f"Sample data not found: {sample_dir}"}

    copied: list[str] = []

    # Copy snapshot and branches
    for name in ("snapshot.yaml", "branches.yaml"):
        src = sample_dir / name
        dst = current_dir / name
        if dst.exists() and not force:
            continue
        if src.exists():
            shutil.copy2(src, dst)
            copied.append(name)

    # Copy alter files
    alters_src = sample_dir / "alters"
    alters_dst = current_dir / "alters"
    if alters_src.exists():
        alters_dst.mkdir(parents=True, exist_ok=True)
        for f in alters_src.glob("*.yaml"):
            dst = alters_dst / f.name
            if dst.exists() and not force:
                continue
            shutil.copy2(f, dst)
            copied.append(f"alters/{f.name}")

    # Copy reality trace
    rt_src = sample_dir / "reality_trace.yaml"
    rt_dst = current_dir / "reality_trace.yaml"
    if rt_src.exists() and (not rt_dst.exists() or force):
        shutil.copy2(rt_src, rt_dst)
        copied.append("reality_trace.yaml")

    return {
        "status": "ok",
        "files_copied": copied,
        "target": str(current_dir),
        "note": "Restart the app to see sample data." if copied else "All files already exist. Use --force to overwrite.",
    }


def _print_result(result: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    for key, value in result.items():
        if isinstance(value, (dict, list)):
            print(f"{key}={json.dumps(value, sort_keys=True)}")
        else:
            print(f"{key}={value}")
