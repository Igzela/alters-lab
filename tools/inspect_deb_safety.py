#!/usr/bin/env python3
"""Inspect an Alters Lab .deb for P7 data-safety boundaries."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


REQUIRED_PATHS = [
    "/opt/alters-lab/",
    "/usr/bin/alters-lab",
    "/usr/share/applications/alters-lab.desktop",
    "/usr/share/icons/hicolor/scalable/apps/alters-lab.svg",
]
FORBIDDEN_FRAGMENTS = [
    "node_modules",
    ".env",
    ".env.local",
    "alters/product",
    "secrets.yaml",
    "config.yaml",
    ".config/alters-lab",
    ".local/share/alters-lab",
    ".local/state/alters-lab",
    "/logs/",
]
USER_DELETE_PATTERNS = [
    "rm -rf ~/.config",
    "rm -rf ~/.local",
    ".config/alters-lab",
    ".local/share/alters-lab",
    ".local/state/alters-lab",
]


def package_contents(deb_path: Path) -> list[str]:
    result = subprocess.run(["dpkg-deb", "--contents", str(deb_path)], check=True, text=True, capture_output=True)
    return result.stdout.splitlines()


def inspect_deb(deb_path: Path, repo_root: Path | None = None) -> dict:
    lines = package_contents(deb_path)
    present = {required: any(required.lstrip("/") in line for line in lines) for required in REQUIRED_PATHS}
    forbidden = sorted({fragment for line in lines for fragment in FORBIDDEN_FRAGMENTS if fragment in line})
    script_findings = inspect_maintainer_scripts(repo_root or Path(__file__).resolve().parents[1])
    status = "PASS" if all(present.values()) and not forbidden and not script_findings else "FAIL"
    return {
        "status": status,
        "deb_path": str(deb_path),
        "required_paths": present,
        "forbidden_matches": forbidden,
        "maintainer_script_findings": script_findings,
        "p6_behavior_validated": False,
        "p6_sealed": False,
    }


def inspect_maintainer_scripts(repo_root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for name in ["postinst", "prerm", "postrm"]:
        path = repo_root / "packaging" / "deb" / name
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8").lower()
        for pattern in USER_DELETE_PATTERNS:
            if pattern in content:
                findings.append({"script": str(path), "pattern": pattern})
    return findings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect Alters Lab Debian package safety")
    parser.add_argument("deb_path")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = inspect_deb(Path(args.deb_path).expanduser().resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"status={report['status']}")
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
