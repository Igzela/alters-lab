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
    else:
        parser.error(f"Unknown command: {args.command}")

    _print_result(result, json_output=args.json)
    return 0


def _print_result(result: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    for key, value in result.items():
        if isinstance(value, (dict, list)):
            print(f"{key}={json.dumps(value, sort_keys=True)}")
        else:
            print(f"{key}={value}")
