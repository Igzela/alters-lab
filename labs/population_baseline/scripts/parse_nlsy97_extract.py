#!/usr/bin/env python3
"""
Phase 13 — NLSY97 Extract Parser Scaffold.

Accepts a directory path containing NLSY97 CSV files,
reads them, prints column names and shape, and optionally
writes processed output to data/processed/.

Usage:
    python parse_nlsy97_extract.py --dir labs/population_baseline/data/raw/nlsy97/
    python parse_nlsy97_extract.py --dir labs/population_baseline/data/raw/nlsy97/ --write
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = REPO_ROOT / "labs" / "population_baseline" / "data" / "processed"

EXPECTED_FILES = [
    "nlsy97_core_demographics.csv",
    "nlsy97_education.csv",
    "nlsy97_employment.csv",
    "nlsy97_income.csv",
    "nlsy97_financial_hardship.csv",
    "nlsy97_cognitive.csv",
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
            "path": str(filepath),
            "status": "unreadable_or_missing",
            "columns": [],
            "shape": (0, 0),
        }
    return {
        "path": str(filepath.name),
        "status": "ok",
        "columns": list(df.columns),
        "shape": list(df.shape),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "sample_column_count": len(df.columns),
    }


def write_processed(df, name: str, write: bool):
    """Optionally write processed DataFrame."""
    if not write:
        return
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / f"nlsy97_{name}_processed.csv"
    df.to_csv(out_path, index=False)
    print(f"  Written: {out_path.relative_to(REPO_ROOT)}")


def main():
    parser = argparse.ArgumentParser(description="NLSY97 extract parser scaffold")
    parser.add_argument("--dir", type=str, required=True,
                        help="Path to NLSY97 raw data directory")
    parser.add_argument("--write", action="store_true",
                        help="Write processed output to data/processed/")
    args = parser.parse_args()

    raw_dir = Path(args.dir)
    if not raw_dir.is_absolute():
        raw_dir = REPO_ROOT / raw_dir

    if not raw_dir.exists():
        print(f"ERROR: Directory not found: {raw_dir}")
        print("Download NLSY97 data first. See P13_USER_DOWNLOAD_INSTRUCTIONS.md")
        return 1

    print(f"NLSY97 Extract Parser")
    print(f"Source directory: {raw_dir}")
    print(f"Write mode: {'ON' if args.write else 'OFF (inspect only)'}")
    print()

    found_any = False
    for fname in EXPECTED_FILES:
        fpath = raw_dir / fname
        print(f"--- {fname} ---")
        if not fpath.exists():
            print(f"  Status: MISSING")
            print(f"  Expected at: {fpath}")
            continue

        found_any = True
        result = inspect_file(fpath)
        print(f"  Status: {result['status']}")
        print(f"  Shape: {result['shape']}")
        print(f"  Columns ({result['sample_column_count']}): {result['columns'][:20]}")
        if len(result['columns']) > 20:
            print(f"  ... and {len(result['columns']) - 20} more columns")

        if args.write and result['status'] == 'ok':
            df = read_csv_safe(fpath)
            if df is not None:
                write_processed(df, fname.replace('.csv', '').replace('nlsy97_', ''), True)
        print()

    if not found_any:
        print("No NLSY97 data files found.")
        print("Download data first. See P13_USER_DOWNLOAD_INSTRUCTIONS.md")
        return 1

    # Also scan for any non-expected CSV files
    other_csvs = [f for f in raw_dir.glob("*.csv")
                  if f.name not in EXPECTED_FILES]
    if other_csvs:
        print(f"--- Other CSV files found ({len(other_csvs)}) ---")
        for f in other_csvs[:10]:
            result = inspect_file(f)
            print(f"  {f.name}: {result['shape']} cols={result['columns'][:10]}")
        print()

    print("Done. No processed data written unless --write was used.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
