#!/usr/bin/env python3
"""
Phase 16F — NLSY97 Baseline Table Builder.

Builds aggregate baseline tables from verified NLSY97 variables.
Uses streaming/chunks to avoid loading full 8GB CSV into memory.

Usage:
    python build_nlsy97_baseline_tables.py --zip labs/population_baseline/data/raw/nlsy97/nlsy97_all_1997-2023.zip
"""

import argparse
import csv
import io
import json
import sys
import zipfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = REPO_ROOT / "labs" / "population_baseline" / "config"
ARTIFACTS_DIR = REPO_ROOT / "labs" / "population_baseline" / "artifacts"

# Selected priority variables for baseline tables
SELECTED_VARIABLES = {
    "demographics": [
        {"code": "R0000100", "label": "Respondent ID", "type": "id"},
        {"code": "R0000200", "label": "Survey Year", "type": "demographic"},
        {"code": "R0000300", "label": "Age", "type": "demographic"},
        {"code": "R0000400", "label": "Sex", "type": "demographic"},
        {"code": "R0000500", "label": "Race/Ethnicity", "type": "demographic"},
    ],
    "education": [
        {"code": "R0010100", "label": "Highest Degree", "type": "education"},
        {"code": "R0010200", "label": "Highest Grade", "type": "education"},
        {"code": "R0010300", "label": "Enrollment Status", "type": "education"},
    ],
    "employment": [
        {"code": "R0020100", "label": "Employment Status", "type": "employment"},
        {"code": "R0020200", "label": "Weeks Worked", "type": "employment"},
        {"code": "R0020300", "label": "Hours Worked", "type": "employment"},
    ],
    "financial": [
        {"code": "R0030100", "label": "Personal Income", "type": "financial"},
        {"code": "R0030200", "label": "Household Income", "type": "financial"},
    ],
}


def stream_csv_chunk(zip_path: Path, chunk_size: int = 10000) -> list[list[str]]:
    """Stream CSV in chunks for processing."""
    chunks = []
    with zipfile.ZipFile(zip_path, 'r') as zf:
        csv_files = [f for f in zf.namelist() if f.lower().endswith('.csv')]
        if not csv_files:
            return chunks

        csv_name = csv_files[0]
        with zf.open(csv_name) as f:
            reader = csv.reader(io.TextIOWrapper(f, encoding='utf-8', errors='replace'))
            header = next(reader, None)
            if not header:
                return chunks

            chunk = []
            for i, row in enumerate(reader):
                chunk.append(row)
                if len(chunk) >= chunk_size:
                    chunks.append(chunk)
                    chunk = []
            if chunk:
                chunks.append(chunk)

    return chunks


def compute_column_stats(zip_path: Path, columns: list[dict], sample_size: int = 50000) -> dict:
    """Compute aggregate statistics for selected columns using streaming."""
    stats = {}

    # Get header first
    with zipfile.ZipFile(zip_path, 'r') as zf:
        csv_files = [f for f in zf.namelist() if f.lower().endswith('.csv')]
        if not csv_files:
            return stats

        csv_name = csv_files[0]
        with zf.open(csv_name) as f:
            reader = csv.reader(io.TextIOWrapper(f, encoding='utf-8', errors='replace'))
            header = next(reader, None)
            if not header:
                return stats

            # Map column names to indices
            col_map = {}
            for col in columns:
                code = col["code"]
                if code in header:
                    col_map[code] = {
                        "index": header.index(code),
                        "label": col["label"],
                        "type": col["type"],
                    }

            # Initialize stats
            for code, info in col_map.items():
                stats[code] = {
                    "variable_code": code,
                    "variable_label": info["label"],
                    "type": info["type"],
                    "n_total": 0,
                    "n_valid": 0,
                    "n_missing": 0,
                    "values": {},
                }

            # Stream through rows
            for i, row in enumerate(reader):
                if i >= sample_size:
                    break

                for code, info in col_map.items():
                    idx = info["index"]
                    if idx < len(row):
                        value = row[idx].strip()
                        stats[code]["n_total"] += 1

                        if not value or value == "":
                            stats[code]["n_missing"] += 1
                        else:
                            stats[code]["n_valid"] += 1
                            # Count values for distribution
                            if value not in stats[code]["values"]:
                                stats[code]["values"][value] = 0
                            stats[code]["values"][value] += 1

    # Compute missingness rates
    for code in stats:
        s = stats[code]
        if s["n_total"] > 0:
            s["missingness_rate"] = round(s["n_missing"] / s["n_total"] * 100, 2)
        else:
            s["missingness_rate"] = 0

        # Get top values for distribution
        sorted_values = sorted(s["values"].items(), key=lambda x: x[1], reverse=True)
        s["distribution"] = {v: c for v, c in sorted_values[:10]}

        # Remove raw values dict to save space
        del s["values"]

    return stats


def main():
    parser = argparse.ArgumentParser(description="NLSY97 baseline table builder")
    parser.add_argument("--zip", type=str, required=True,
                        help="Path to NLSY97 ZIP archive")
    parser.add_argument("--sample-size", type=int, default=50000,
                        help="Number of rows to sample (default: 50000)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output path for JSON report")
    args = parser.parse_args()

    zip_path = Path(args.zip)
    if not zip_path.is_absolute():
        zip_path = REPO_ROOT / zip_path

    print(f"NLSY97 Baseline Table Builder")
    print(f"Archive: {zip_path}")
    print(f"Sample size: {args.sample_size:,}")
    print()

    if not zip_path.exists():
        print(f"ERROR: File not found: {zip_path}")
        return 1

    # Flatten selected variables
    all_vars = []
    for domain, vars_list in SELECTED_VARIABLES.items():
        for v in vars_list:
            v["domain"] = domain
            all_vars.append(v)

    print(f"Computing statistics for {len(all_vars)} variables...")
    stats = compute_column_stats(zip_path, all_vars, args.sample_size)

    # Print summary
    for code, s in stats.items():
        print(f"  {code} ({s['variable_label']}): "
              f"n_valid={s['n_valid']}, n_missing={s['n_missing']}, "
              f"missingness={s['missingness_rate']}%")

    # Build baseline tables
    tables = []
    for code, s in stats.items():
        table = {
            "artifact_id": f"nlsy97_{s['type']}_{code}",
            "dataset_source_id": "nlsy97",
            "outcome_id": s["variable_label"].lower().replace(" ", "_"),
            "variable_codes": [code],
            "variable_labels": [s["variable_label"]],
            "subgroup_definition": f"sample_{args.sample_size}",
            "n_valid": s["n_valid"],
            "n_missing": s["n_missing"],
            "missingness_rate": s["missingness_rate"],
            "observed_rate_or_mean": None,
            "distribution": s["distribution"],
            "confidence_interval": None,
            "transfer_risk": "medium",
            "limitations": [
                f"Sample of {args.sample_size:,} rows from full dataset",
                "Aggregate statistics only",
                "No individual-level data",
            ],
            "approved_for_route_b": False,
        }
        tables.append(table)

    # Write output
    output_path = Path(args.output) if args.output else ARTIFACTS_DIR / "nlsy97_baseline_tables_p16.json"
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path

    with open(output_path, 'w') as f:
        json.dump({
            "artifact_id": "nlsy97_baseline_tables_p16",
            "phase": "16",
            "created_at": "2026-06-03",
            "sample_size": args.sample_size,
            "tables": tables,
            "total_tables": len(tables),
            "approved_for_route_b": False,
            "limitations": [
                "Exploratory baseline tables only",
                "No individual-level data",
                "No production ML integration",
                "No personal probabilities",
                f"Sample of {args.sample_size:,} rows",
            ]
        }, f, indent=2)

    print(f"\nTotal tables generated: {len(tables)}")
    print(f"Output written to: {output_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
