#!/usr/bin/env python3
"""
NLSY97 Route B Baseline Builder v2.

Builds data-backed baseline tables for career_education and financial domains
from actual NLSY97 data with value labels, missingness audit, and Route B
approval metadata.

Uses 2005 round data (respondents age 25+) instead of Round 1 (1997, age 12-16).
Uses streaming/chunked parsing to avoid loading 8GB CSV into memory.

Usage:
    python build_nlsy97_route_b_baselines.py \
        --zip labs/population_baseline/data/raw/nlsy97/nlsy97_all_1997-2023.zip \
        --sample-size 50000
"""

import argparse
import csv
import io
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = REPO_ROOT / "labs" / "population_baseline" / "config"
ARTIFACTS_DIR = REPO_ROOT / "labs" / "population_baseline" / "artifacts"

# NLSY97 standard missing value codes
NLSY97_MISSING_CODES = {"-1", "-2", "-3", "-4", "-5"}
NLSY97_MISSING_LABELS = {
    "-1": "Not in universe",
    "-2": "Don't know",
    "-3": "Refuse",
    "-4": "Valid skip",
    "-5": "Invalid skip",
}

# Route B baseline variables — using 2005 round (respondents age 25-29)
# Variable codes confirmed via NLSY97 variable dictionary grep
ROUTE_B_VARIABLES = [
    # career_education domain
    {
        "code": "S5412600",
        "label": "CV_HGC_EVER 2005",
        "display_label": "Highest Grade Completed (Ever)",
        "domain": "career_education",
        "value_labels": {str(i): f"Grade {i}" for i in range(0, 21)},
        "measurement_type": "continuous",
        "year": 2005,
    },
    {
        "code": "S5413300",
        "label": "CV_HIGHEST_DEGREE_EVER 2005",
        "display_label": "Highest Degree Ever Received",
        "domain": "career_education",
        "value_labels": {
            "0": "None",
            "1": "GED",
            "2": "High school diploma",
            "3": "Associate degree",
            "4": "Bachelor's degree",
            "5": "Master's degree",
            "6": "Doctorate",
            "7": "Professional degree",
        },
        "measurement_type": "ordinal",
        "year": 2005,
    },
    # financial domain
    {
        "code": "S5412800",
        "label": "CV_INCOME_FAMILY 2005",
        "display_label": "Total Family Income",
        "domain": "financial",
        "value_labels": {},
        "measurement_type": "continuous",
        "year": 2005,
    },
]


def stream_nlsy97(zip_path: Path, variable_codes: list[str], sample_size: int) -> dict:
    """Stream NLSY97 CSV and compute stats for selected variables."""
    stats = {}

    with zipfile.ZipFile(zip_path, "r") as zf:
        csv_files = [f for f in zf.namelist() if f.lower().endswith(".csv")]
        if not csv_files:
            raise FileNotFoundError(f"No CSV file found in {zip_path}")

        csv_name = csv_files[0]
        with zf.open(csv_name) as f:
            reader = csv.reader(
                io.TextIOWrapper(f, encoding="utf-8", errors="replace")
            )
            header = next(reader, None)
            if not header:
                raise ValueError("Empty CSV header")

            # Map variable codes to column indices
            col_indices = {}
            for code in variable_codes:
                if code in header:
                    col_indices[code] = header.index(code)
                    print(f"  Found {code} at column index {header.index(code)}")
                else:
                    print(f"  WARNING: {code} not in CSV header")

            # Initialize stats for each variable
            for code in col_indices:
                stats[code] = {
                    "n_total": 0,
                    "n_valid": 0,
                    "n_missing": 0,
                    "missing_by_code": {},
                    "values": {},
                    "numeric_sum": 0.0,
                    "numeric_count": 0,
                    "numeric_min": float("inf"),
                    "numeric_max": float("-inf"),
                }

            # Stream through rows
            for i, row in enumerate(reader):
                if i >= sample_size:
                    break

                for code, idx in col_indices.items():
                    if idx >= len(row):
                        continue

                    value = row[idx].strip()
                    s = stats[code]
                    s["n_total"] += 1

                    if not value or value in NLSY97_MISSING_CODES:
                        s["n_missing"] += 1
                        if value:
                            s["missing_by_code"][value] = (
                                s["missing_by_code"].get(value, 0) + 1
                            )
                    else:
                        s["n_valid"] += 1
                        s["values"][value] = s["values"].get(value, 0) + 1

                        # Track numeric stats for continuous variables
                        try:
                            num = float(value)
                            s["numeric_sum"] += num
                            s["numeric_count"] += 1
                            s["numeric_min"] = min(s["numeric_min"], num)
                            s["numeric_max"] = max(s["numeric_max"], num)
                        except ValueError:
                            pass

    return stats


def build_distribution(values: dict, value_labels: dict) -> dict:
    """Build labeled distribution from raw value counts."""
    labeled = {}
    for code, count in sorted(values.items(), key=lambda x: x[1], reverse=True)[:15]:
        label = value_labels.get(code, code)
        labeled[f"{code}: {label}"] = count
    return labeled


def build_continuous_summary(s: dict) -> dict | None:
    """Build summary statistics for continuous variables."""
    if s["numeric_count"] == 0:
        return None
    mean = s["numeric_sum"] / s["numeric_count"]

    # Approximate median from distribution
    sorted_vals = sorted(s["values"].items(), key=lambda x: float(x[0]))
    total = sum(v for _, v in sorted_vals)
    cumulative = 0
    median = None
    for val, count in sorted_vals:
        cumulative += count
        if cumulative >= total / 2:
            median = float(val)
            break

    return {
        "mean": round(mean, 2),
        "median": median,
        "min": round(s["numeric_min"], 2) if s["numeric_min"] != float("inf") else None,
        "max": round(s["numeric_max"], 2) if s["numeric_max"] != float("-inf") else None,
        "n_valid": s["numeric_count"],
    }


def build_income_bands(values: dict) -> dict:
    """Group income values into bands for readability."""
    bands = {
        "$0": 0,
        "$1-$9,999": 0,
        "$10,000-$24,999": 0,
        "$25,000-$49,999": 0,
        "$50,000-$74,999": 0,
        "$75,000-$99,999": 0,
        "$100,000-$149,999": 0,
        "$150,000+": 0,
    }
    for val_str, count in values.items():
        try:
            val = float(val_str)
        except ValueError:
            continue
        if val <= 0:
            bands["$0"] += count
        elif val < 10000:
            bands["$1-$9,999"] += count
        elif val < 25000:
            bands["$10,000-$24,999"] += count
        elif val < 50000:
            bands["$25,000-$49,999"] += count
        elif val < 75000:
            bands["$50,000-$74,999"] += count
        elif val < 100000:
            bands["$75,000-$99,999"] += count
        elif val < 150000:
            bands["$100,000-$149,999"] += count
        else:
            bands["$150,000+"] += count
    return {k: v for k, v in bands.items() if v > 0}


def main():
    parser = argparse.ArgumentParser(description="NLSY97 Route B Baseline Builder v2")
    parser.add_argument(
        "--zip",
        type=str,
        required=True,
        help="Path to NLSY97 ZIP archive",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=50000,
        help="Number of rows to sample (default: 50000)",
    )
    args = parser.parse_args()

    zip_path = Path(args.zip)
    if not zip_path.is_absolute():
        zip_path = REPO_ROOT / zip_path

    if not zip_path.exists():
        print(f"ERROR: File not found: {zip_path}")
        return 1

    print("NLSY97 Route B Baseline Builder v2")
    print(f"Archive: {zip_path}")
    print(f"Sample size: {args.sample_size:,}")
    print(f"Using 2005 round data (respondents age 25-29)")
    print()

    var_codes = [v["code"] for v in ROUTE_B_VARIABLES]
    var_by_code = {v["code"]: v for v in ROUTE_B_VARIABLES}

    print(f"Streaming {len(var_codes)} variables from NLSY97...")
    stats = stream_nlsy97(zip_path, var_codes, args.sample_size)

    # Build baseline tables
    tables = []
    for var_info in ROUTE_B_VARIABLES:
        code = var_info["code"]
        if code not in stats:
            print(f"  SKIPPED: {code} ({var_info['display_label']}) — not found in CSV")
            continue

        s = stats[code]
        value_labels = var_info.get("value_labels", {})
        domain = var_info["domain"]
        measurement = var_info["measurement_type"]

        missingness_rate = (
            round(s["n_missing"] / s["n_total"] * 100, 2) if s["n_total"] > 0 else 0
        )

        # Build distribution
        distribution = build_distribution(s["values"], value_labels)

        # Build income bands for financial variables
        income_bands = None
        if domain == "financial" and s["values"]:
            income_bands = build_income_bands(s["values"])

        # Build continuous summary
        continuous_summary = None
        if measurement == "continuous":
            continuous_summary = build_continuous_summary(s)

        # Build missingness detail
        missingness_detail = {}
        for mc, count in s["missing_by_code"].items():
            missingness_detail[f"{mc}: {NLSY97_MISSING_LABELS.get(mc, 'Unknown')}"] = count

        table = {
            "artifact_id": f"nlsy97_route_b_{domain}_{code}",
            "dataset_source_id": "nlsy97",
            "outcome_id": var_info["display_label"].lower().replace(" ", "_").replace("(", "").replace(")", ""),
            "variable_codes": [code],
            "variable_labels": [var_info["display_label"]],
            "value_labels": value_labels if value_labels else None,
            "measurement_type": measurement,
            "survey_year": var_info["year"],
            "respondent_age_range": "25-29",
            "subgroup_definition": f"nlsy97_2005_round_sample_{args.sample_size}",
            "n_valid": s["n_valid"],
            "n_missing": s["n_missing"],
            "missingness_rate": missingness_rate,
            "missingness_detail": missingness_detail if missingness_detail else None,
            "distribution": distribution,
            "income_bands": income_bands,
            "continuous_summary": continuous_summary,
            "confidence_interval": None,
            "transfer_risk": "high",
            "limitations": [
                f"Sample of {args.sample_size:,} rows from full NLSY97 dataset",
                f"2005 round data — respondents aged 25-29 (born 1980-84)",
                "Aggregate statistics only — no individual-level data",
                "Value labels from NLSY97 standard codebook conventions",
                "Family income is household-level, not individual earnings",
                "Transfer to modern populations limited by cohort effects",
                "No longitudinal follow-up linked in this table",
            ],
        }
        tables.append(table)

        # Print summary
        print(f"  {code} ({var_info['display_label']}):")
        print(f"    domain={domain}, n_valid={s['n_valid']}, n_missing={s['n_missing']}, missingness={missingness_rate}%")
        if continuous_summary:
            print(f"    mean={continuous_summary['mean']}, median={continuous_summary['median']}, min={continuous_summary['min']}, max={continuous_summary['max']}")
        if income_bands:
            print(f"    income_bands={income_bands}")
        if distribution:
            top3 = list(distribution.items())[:3]
            print(f"    top_values={top3}")

    # Build domain-level summary
    domain_summaries = {}
    for domain in ["career_education", "financial"]:
        domain_tables = [t for t in tables if t["dataset_source_id"] == "nlsy97"
                         and any(v["domain"] == domain for v in ROUTE_B_VARIABLES
                                 if v["code"] in t["variable_codes"])]
        domain_summaries[domain] = {
            "table_count": len(domain_tables),
            "total_n_valid": sum(t["n_valid"] for t in domain_tables),
            "variables": [t["variable_codes"][0] for t in domain_tables],
            "survey_year": 2005,
        }

    # Write output
    output = {
        "artifact_id": "nlsy97_route_b_baselines_v2",
        "version": "2.0",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sample_size": args.sample_size,
        "data_source": "nlsy97",
        "data_source_description": "National Longitudinal Survey of Youth 1997 (NLSY97)",
        "survey_round": "2005",
        "survey_year": 2005,
        "respondent_age_range": "25-29",
        "tables": tables,
        "total_tables": len(tables),
        "domain_summaries": domain_summaries,
        "value_labels_source": "NLSY97 standard codebook conventions",
        "approved_for_route_b": False,
        "limitations": [
            "2005 round baseline only — longitudinal follow-up not linked",
            f"Sample drawn from ZIP archive ({args.sample_size:,} rows from 89K+ respondents)",
            "Cohort born 1980-84 — transfer to other generations limited",
            "Family income is household-level, not individual earnings",
            "No individual-level data committed",
            "No production ML integration",
            "No personal probabilities emitted",
        ],
        "safety_confirmations": {
            "no_raw_data_committed": True,
            "no_individual_data": True,
            "no_personal_probabilities": True,
            "no_life_score": True,
        },
    }

    output_path = ARTIFACTS_DIR / "nlsy97_route_b_baselines_v2.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nTotal tables: {len(tables)}")
    print(f"Output: {output_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
