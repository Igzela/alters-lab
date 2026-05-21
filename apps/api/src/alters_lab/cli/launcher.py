"""Command-line launcher for Alters Lab local app."""

from __future__ import annotations

import argparse
import json
from typing import Any

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
