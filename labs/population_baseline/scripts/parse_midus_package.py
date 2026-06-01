#!/usr/bin/env python3
"""
Phase 13 — MIDUS Package Parser Scaffold.

Accepts a directory path containing MIDUS subdirectories (midus1/, midus2/, midus3/),
reads CSV files, prints column names and shape, and optionally writes processed output.

Usage:
    python parse_midus_package.py --dir labs/population_baseline/data/raw/midus/
    python parse_midus_package.py --dir labs/population_baseline/data/raw/midus/ --write
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = REPO_ROOT / "labs" / "population_baseline" / "data" / "processed"

EXPECTED_SUBDIRS = {
    "midus1": {
        "required": ["midus1_saq.csv"],
        "optional": ["midus1_phone.csv"],
    },
    "midus2": {
        "required": ["midus2_saq.csv"],
        "optional": ["midus2_phone.csv"],
    },
    "midus3": {
        "required": ["midus3_saq.csv"],
        "optional": [],
    },
    "midus_refresher": {
        "required": [],
        "optional": ["midus_refresher_saq.csv"],
    },
}

# Key MIDUS variable prefixes to look for
MIDUS_KEY_VARIABLES = [
    "B1SCON", "B1SNEU", "B1SEXT", "B1SAGR", "B1SOPN",  # Big Five
    "B1PACON", "B1PANEGAFF",  # Alternate forms
    "B1SCMAS",  # Mastery
    "B1SA1",  # Self-rated health
    "B1SCONDP",  # Chronic conditions
    "B1SMSTAT",  # Marital status
    "B1SKINSP",  # Closest relationship support
    "B1SCALL",  # Social support availability
    "B1SCSAT",  # Social support satisfaction
    "B1SA52A", "B1SA52B",  # Sleep
    "B1SA40A", "B1SA40B",  # Physical activity
]


def read_csv_safe(filepath: Path):
    """Read CSV with common fallbacks. Returns DataFrame or None."""
    try:
        import pandas as pd
    except ImportError:
        print("ERROR: pandas is required. Install with: pip install pandas")
        sys.exit(1)

    if not filepath.exists():
        return None

    for sep in [",", "\t", "|"]:
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                df = pd.read_csv(filepath, sep=sep, encoding=enc, low_memory=False)
                if len(df.columns) > 1:
                    return df
            except Exception:
                continue
    return None


def inspect_file(filepath: Path) -> dict:
    """Read a CSV file and return basic inspection results."""
    df = read_csv_safe(filepath)
    if df is None:
        return {
            "path": str(filepath.name),
            "status": "unreadable_or_missing",
            "columns": [],
            "shape": (0, 0),
        }

    cols = list(df.columns)
    # Check for key MIDUS variables
    found_vars = [v for v in MIDUS_KEY_VARIABLES if v in cols]
    return {
        "path": str(filepath.name),
        "status": "ok",
        "columns": cols,
        "shape": list(df.shape),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "key_variables_found": found_vars,
        "key_variables_missing": [v for v in MIDUS_KEY_VARIABLES if v not in cols],
    }


def main():
    parser = argparse.ArgumentParser(description="MIDUS package parser scaffold")
    parser.add_argument("--dir", type=str, required=True,
                        help="Path to MIDUS raw data directory")
    parser.add_argument("--write", action="store_true",
                        help="Write processed output to data/processed/")
    args = parser.parse_args()

    raw_dir = Path(args.dir)
    if not raw_dir.is_absolute():
        raw_dir = REPO_ROOT / raw_dir

    if not raw_dir.exists():
        print(f"ERROR: Directory not found: {raw_dir}")
        print("Download MIDUS data first. See P13_USER_DOWNLOAD_INSTRUCTIONS.md")
        return 1

    print(f"MIDUS Package Parser")
    print(f"Source directory: {raw_dir}")
    print(f"Write mode: {'ON' if args.write else 'OFF (inspect only)'}")
    print()

    found_any = False
    all_key_vars_found = set()
    all_key_vars_missing = set()

    for subdir_name, file_spec in EXPECTED_SUBDIRS.items():
        subdir = raw_dir / subdir_name
        print(f"=== {subdir_name} ===")

        if not subdir.exists():
            print(f"  Directory not found: {subdir}")
            print(f"  Expected files: {file_spec['required'] + file_spec['optional']}")
            print()
            continue

        all_files = file_spec["required"] + file_spec["optional"]
        for fname in all_files:
            fpath = subdir / fname
            is_required = fname in file_spec["required"]
            label = "REQUIRED" if is_required else "optional"

            print(f"  --- {fname} ({label}) ---")
            if not fpath.exists():
                print(f"    Status: MISSING")
                continue

            found_any = True
            result = inspect_file(fpath)
            print(f"    Status: {result['status']}")
            print(f"    Shape: {result['shape']}")
            print(f"    Columns ({len(result['columns'])}): {result['columns'][:15]}")
            if len(result['columns']) > 15:
                print(f"    ... and {len(result['columns']) - 15} more")

            if result.get("key_variables_found"):
                print(f"    Key MIDUS variables found: {result['key_variables_found']}")
                all_key_vars_found.update(result["key_variables_found"])
            if result.get("key_variables_missing"):
                all_key_vars_missing.update(result["key_variables_missing"])

            if args.write and result['status'] == 'ok':
                df = read_csv_safe(fpath)
                if df is not None:
                    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
                    out_path = PROCESSED_DIR / f"midus_{subdir_name}_{fname.replace('.csv', '')}_processed.csv"
                    df.to_csv(out_path, index=False)
                    print(f"    Written: {out_path.relative_to(REPO_ROOT)}")

        print()

    if not found_any:
        print("No MIDUS data files found.")
        print("Download data first. See P13_USER_DOWNLOAD_INSTRUCTIONS.md")
        return 1

    # Summary of key variable coverage
    if all_key_vars_found or all_key_vars_missing:
        print("=== Key MIDUS Variable Coverage ===")
        print(f"Found: {sorted(all_key_vars_found)}")
        print(f"Not found in any file: {sorted(all_key_vars_missing)}")
        print()

    print("Done. No processed data written unless --write was used.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
