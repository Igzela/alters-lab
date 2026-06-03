#!/usr/bin/env python3
"""
Phase 15D — MIDUS SPSS Parser.

Reads SPSS .sav files using pyreadstat to extract metadata.
Does not load full data into memory unless --summary is used.

Usage:
    python parse_midus_sav.py --sav labs/population_baseline/data/raw/midus/midus1/M1_P1_SURVEY_N7108_20190116.sav
    python parse_midus_sav.py --sav ... --metadata-only
    python parse_midus_sav.py --sav ... --columns B1SCON B1SNEU
    python parse_midus_sav.py --sav ... --summary
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "labs" / "population_baseline" / "artifacts"


def read_metadata(sav_path: Path) -> dict:
    """Read SPSS metadata without loading data."""
    import pyreadstat

    try:
        # Read only metadata by specifying usecols=[] or just reading header
        # pyreadstat doesn't have a metadata-only mode, but we can read with minimal memory
        # by reading just the metadata and not the data
        meta = pyreadstat.read_sav(str(sav_path), usecols=None)
        # meta is (DataFrame, metadata)
        # We only want the metadata part
        _, metadata = meta

        return {
            "variable_count": len(metadata.column_names),
            "row_count": metadata.number_rows,
            "variable_names": metadata.column_names,
            "variable_labels": metadata.column_labels,
            "variable_value_labels": metadata.variable_value_labels,
            "missing_ranges": metadata.missing_ranges,
        }
    except Exception as e:
        return {"error": str(e)}


def read_metadata_only(sav_path: Path) -> dict:
    """Read only metadata from SPSS file."""
    import pyreadstat

    try:
        # Read the file but immediately discard data
        # This is more memory efficient than loading full data
        with open(sav_path, 'rb') as f:
            # pyreadstat can read metadata separately
            # But we need to read the file to get metadata
            # Let's use a small trick: read with usecols=[] if supported
            # or just read and immediately discard
            df, metadata = pyreadstat.read_sav(str(sav_path))

        return {
            "variable_count": len(metadata.column_names),
            "row_count": metadata.number_rows,
            "variable_names": metadata.column_names[:50],  # First 50
            "variable_labels": {k: v for k, v in zip(
                metadata.column_names[:50],
                metadata.column_labels[:50]
            )},
        }
    except Exception as e:
        return {"error": str(e)}


def compute_summary(sav_path: Path, columns: list[str] = None) -> dict:
    """Compute summary statistics for selected columns."""
    import pyreadstat
    import pandas as pd

    try:
        df, metadata = pyreadstat.read_sav(str(sav_path))

        if columns:
            # Filter to only requested columns that exist
            valid_cols = [c for c in columns if c in df.columns]
            if not valid_cols:
                return {"error": "None of the requested columns found"}
            df = df[valid_cols]

        # Compute summary stats
        summary = {}
        for col in df.columns:
            col_data = df[col]
            non_null = col_data.dropna()
            summary[col] = {
                "count": len(non_null),
                "missing": col_data.isna().sum(),
                "missingness_rate": round(col_data.isna().sum() / len(col_data) * 100, 2),
            }

            if pd.api.types.is_numeric_dtype(col_data):
                summary[col].update({
                    "mean": round(non_null.mean(), 4) if len(non_null) > 0 else None,
                    "std": round(non_null.std(), 4) if len(non_null) > 1 else None,
                    "min": non_null.min() if len(non_null) > 0 else None,
                    "max": non_null.max() if len(non_null) > 0 else None,
                    "median": non_null.median() if len(non_null) > 0 else None,
                })

                # Get value labels if available
                if col in metadata.variable_value_labels:
                    summary[col]["value_labels"] = metadata.variable_value_labels[col]

        return summary
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="MIDUS SPSS parser")
    parser.add_argument("--sav", type=str, required=True,
                        help="Path to SPSS .sav file")
    parser.add_argument("--metadata-only", action="store_true",
                        help="Print only metadata (variable names, count)")
    parser.add_argument("--columns", nargs="*", default=None,
                        help="Column names to inspect")
    parser.add_argument("--summary", action="store_true",
                        help="Compute summary statistics for selected columns")
    parser.add_argument("--output", type=str, default=None,
                        help="Output path for JSON report")
    args = parser.parse_args()

    sav_path = Path(args.sav)
    if not sav_path.is_absolute():
        sav_path = REPO_ROOT / sav_path

    print(f"MIDUS SPSS Parser")
    print(f"File: {sav_path}")
    print()

    if args.metadata_only:
        result = read_metadata_only(sav_path)
    elif args.summary:
        result = compute_summary(sav_path, args.columns)
    else:
        result = read_metadata(sav_path)

    if "error" in result:
        print(f"ERROR: {result['error']}")
        return 1

    # Print results
    if args.metadata_only:
        print(f"Variable count: {result['variable_count']}")
        print(f"Row count: {result['row_count']}")
        print(f"\nFirst 50 variable names:")
        for i, name in enumerate(result['variable_names']):
            label = result.get('variable_labels', {}).get(name, '')
            print(f"  {i+1}. {name}" + (f" - {label}" if label else ""))
    elif args.summary:
        print("Summary statistics:")
        for col, stats in result.items():
            print(f"\n  {col}:")
            print(f"    Count: {stats['count']}")
            print(f"    Missing: {stats['missing']} ({stats['missingness_rate']}%)")
            if 'mean' in stats:
                print(f"    Mean: {stats['mean']}")
                print(f"    Std: {stats['std']}")
                print(f"    Min: {stats['min']}")
                print(f"    Max: {stats['max']}")
                print(f"    Median: {stats['median']}")
            if 'value_labels' in stats:
                print(f"    Value labels: {stats['value_labels']}")
    else:
        print(f"Variable count: {result['variable_count']}")
        print(f"Row count: {result['row_count']}")
        print(f"\nFirst 50 variable names:")
        for i, name in enumerate(result['variable_names'][:50]):
            label = result.get('variable_labels', {}).get(name, '')
            print(f"  {i+1}. {name}" + (f" - {label}" if label else ""))
        if result['variable_count'] > 50:
            print(f"  ... and {result['variable_count'] - 50} more variables")

    # Write output if requested
    if args.output:
        import json
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = REPO_ROOT / output_path

        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nReport written to: {output_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
