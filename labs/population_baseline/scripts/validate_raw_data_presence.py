#!/usr/bin/env python3
"""
Phase 13 — Raw Data Presence Validation Script.

Checks that expected raw data files exist and are non-empty.
Writes validation results to stdout and exits with appropriate code.
Does NOT check content validity (use parser scripts for that).
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_BASE = REPO_ROOT / "labs" / "population_baseline" / "data" / "raw"

# Required files: if any of these are missing, validation fails
REQUIRED_FILES = [
    "nlsy97/nlsy97_core_demographics.csv",
    "nlsy97/nlsy97_education.csv",
    "nlsy97/nlsy97_employment.csv",
    "nlsy97/nlsy97_income.csv",
    "nlsy97/codebook/nlsy97_codebook.pdf",
    "midus/midus1/midus1_saq.csv",
    "midus/midus2/midus2_saq.csv",
    "midus/midus3/midus3_saq.csv",
]

# Optional files: nice to have but not blocking
OPTIONAL_FILES = [
    "nlsy97/nlsy97_financial_hardship.csv",
    "nlsy97/nlsy97_cognitive.csv",
    "midus/midus1/midus1_phone.csv",
    "midus/midus2/midus2_phone.csv",
    "midus/midus_refresher/midus_refresher_saq.csv",
]


def validate():
    """Check file presence and report results."""
    results = {
        "required": [],
        "optional": [],
        "pass": True,
    }

    print("Validating raw data presence...\n")

    # Check required files
    print("Required files:")
    for rel_path in REQUIRED_FILES:
        fpath = RAW_BASE / rel_path
        exists = fpath.exists() and fpath.stat().st_size > 0
        status = "OK" if exists else "MISSING"
        print(f"  [{status}] {rel_path}")
        results["required"].append({
            "path": rel_path,
            "exists": fpath.exists(),
            "non_empty": fpath.exists() and fpath.stat().st_size > 0,
            "size_bytes": fpath.stat().st_size if fpath.exists() else 0,
        })
        if not exists:
            results["pass"] = False

    # Check optional files
    print("\nOptional files:")
    for rel_path in OPTIONAL_FILES:
        fpath = RAW_BASE / rel_path
        exists = fpath.exists() and fpath.stat().st_size > 0
        status = "OK" if exists else "MISSING"
        print(f"  [{status}] {rel_path}")
        results["optional"].append({
            "path": rel_path,
            "exists": fpath.exists(),
            "non_empty": fpath.exists() and fpath.stat().st_size > 0,
            "size_bytes": fpath.stat().st_size if fpath.exists() else 0,
        })

    # Summary
    required_ok = sum(1 for r in results["required"] if r["non_empty"])
    optional_ok = sum(1 for r in results["optional"] if r["non_empty"])
    print(f"\nRequired: {required_ok}/{len(REQUIRED_FILES)} present")
    print(f"Optional: {optional_ok}/{len(OPTIONAL_FILES)} present")

    if results["pass"]:
        print("\nValidation PASSED — all required files present.")
    else:
        print("\nValidation FAILED — some required files are missing.")
        print("See P13_USER_DOWNLOAD_INSTRUCTIONS.md for download steps.")

    return results


def main():
    results = validate()

    # Write results to artifacts
    artifacts_dir = REPO_ROOT / "labs" / "population_baseline" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifacts_dir / "validation_result_p13.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {out_path.relative_to(REPO_ROOT)}")

    return 0 if results["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
