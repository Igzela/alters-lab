#!/usr/bin/env python3
"""
Phase 13 — Raw Data Inventory Script.

Scans data/raw/nlsy97/ and data/raw/midus/ directories,
lists files with sizes and optional checksums, and writes
an inventory artifact to artifacts/raw_data_inventory_p13.json.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_BASE = REPO_ROOT / "labs" / "population_baseline" / "data" / "raw"
ARTIFACTS_DIR = REPO_ROOT / "labs" / "population_baseline" / "artifacts"

EXPECTED_FILES = {
    "nlsy97": [
        "nlsy97_core_demographics.csv",
        "nlsy97_education.csv",
        "nlsy97_employment.csv",
        "nlsy97_income.csv",
        "nlsy97_financial_hardship.csv",
        "nlsy97_cognitive.csv",
        "codebook/nlsy97_codebook.pdf",
    ],
    "midus/midus1": [
        "midus1_saq.csv",
        "midus1_phone.csv",
    ],
    "midus/midus2": [
        "midus2_saq.csv",
        "midus2_phone.csv",
    ],
    "midus/midus3": [
        "midus3_saq.csv",
    ],
    "midus/midus_refresher": [
        "midus_refresher_saq.csv",
    ],
}

SKIP_EXTENSIONS = {".gitkeep"}


def compute_checksum(filepath: Path, algorithm: str = "sha256") -> str:
    """Compute file checksum."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def classify_file(filepath: Path) -> str:
    """Classify a file's status based on extension and size."""
    if not filepath.exists():
        return "missing"
    if filepath.suffix == ".gitkeep":
        return "gitkeep"
    size = filepath.stat().st_size
    if size == 0:
        return "empty"
    return "present"


def scan_directory(base: Path, rel_prefix: str = "") -> list:
    """Scan a directory tree and return file inventory."""
    files = []
    if not base.exists():
        return files
    for p in sorted(base.rglob("*")):
        if p.is_dir():
            continue
        if p.name in SKIP_EXTENSIONS or p.suffix in SKIP_EXTENSIONS:
            continue
        rel = str(p.relative_to(base))
        entry = {
            "path": f"{rel_prefix}/{rel}" if rel_prefix else rel,
            "size_bytes": p.stat().st_size,
            "status": classify_file(p),
        }
        # Only compute checksum for reasonably sized files (< 500MB)
        if p.stat().st_size < 500 * 1024 * 1024:
            entry["sha256"] = compute_checksum(p)
        files.append(entry)
    return files


def check_expected_files() -> dict:
    """Check which expected files are present or missing."""
    results = {}
    for group, filenames in EXPECTED_FILES.items():
        group_dir = RAW_BASE / group
        group_results = []
        for fname in filenames:
            fpath = group_dir / fname
            entry = {
                "filename": fname,
                "expected_path": str(fpath.relative_to(REPO_ROOT)),
                "status": classify_file(fpath),
            }
            if fpath.exists():
                entry["size_bytes"] = fpath.stat().st_size
            group_results.append(entry)
        results[group] = group_results
    return results


def main():
    """Run inventory scan."""
    inventory = {
        "phase": "P13",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_base": str(RAW_BASE.relative_to(REPO_ROOT)),
        "scanned_files": [],
        "expected_files": {},
        "summary": {
            "total_files": 0,
            "total_size_bytes": 0,
            "present": 0,
            "missing": 0,
            "empty": 0,
        },
    }

    # Scan all files in raw directories
    for subdir in ["nlsy97", "midus"]:
        scan_dir = RAW_BASE / subdir
        if scan_dir.exists():
            files = scan_directory(scan_dir, rel_prefix=subdir)
            inventory["scanned_files"].extend(files)

    # Check expected files
    inventory["expected_files"] = check_expected_files()

    # Compute summary
    all_scanned = inventory["scanned_files"]
    inventory["summary"]["total_files"] = len(all_scanned)
    inventory["summary"]["total_size_bytes"] = sum(f["size_bytes"] for f in all_scanned)
    for f in all_scanned:
        status = f["status"]
        if status in inventory["summary"]:
            inventory["summary"][status] += 1

    # Count expected file statuses
    expected_missing = 0
    expected_present = 0
    for group_files in inventory["expected_files"].values():
        for f in group_files:
            if f["status"] == "missing":
                expected_missing += 1
            elif f["status"] == "present":
                expected_present += 1
    inventory["summary"]["expected_missing"] = expected_missing
    inventory["summary"]["expected_present"] = expected_present

    # Write inventory artifact
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ARTIFACTS_DIR / "raw_data_inventory_p13.json"
    with open(out_path, "w") as f:
        json.dump(inventory, f, indent=2)

    # Print summary
    print(f"Inventory written to {out_path.relative_to(REPO_ROOT)}")
    print(f"  Scanned files: {inventory['summary']['total_files']}")
    print(f"  Total size: {inventory['summary']['total_size_bytes']:,} bytes")
    print(f"  Expected files present: {expected_present}")
    print(f"  Expected files missing: {expected_missing}")

    if expected_missing > 0:
        print(f"\n  See P13_USER_DOWNLOAD_INSTRUCTIONS.md for download steps.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
