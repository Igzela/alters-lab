#!/usr/bin/env python3
"""
Phase 15F — Baseline Table Builder.

Builds aggregate baseline tables from confirmed variables.
No individual-level data is output. Only aggregate statistics.

Usage:
    python build_baseline_tables.py --dataset midus1
    python build_baseline_tables.py --dataset all
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "labs" / "population_baseline" / "artifacts"


def build_midus_baseline_tables(dataset_id: str, sav_path: Path) -> list[dict]:
    """Build baseline tables for a MIDUS dataset."""
    import pyreadstat
    import pandas as pd

    df, metadata = pyreadstat.read_sav(str(sav_path))

    tables = []

    # Table 1: Self-rated health
    health_vars = [col for col in df.columns if col in ['B1PA1', 'B1PA4', 'C1PA1']]
    if health_vars:
        col = health_vars[0]
        data = df[col].dropna()
        # Filter out invalid values (7=DK, 8=Refused)
        data = data[data <= 5]
        if len(data) > 0:
            tables.append({
                "artifact_id": f"{dataset_id}_health_self_rated",
                "dataset_source_id": dataset_id,
                "outcome_id": "self_rated_health",
                "source_file": str(sav_path.name),
                "variable_names": [col],
                "subgroup_definition": "all_valid_respondents",
                "n_valid": int(len(data)),
                "n_missing": int(df[col].isna().sum()),
                "missingness_rate": round(df[col].isna().sum() / len(df) * 100, 2),
                "observed_rate_or_mean": round(data.mean(), 4),
                "distribution": {
                    "excellent": int((data == 1).sum()),
                    "very_good": int((data == 2).sum()),
                    "good": int((data == 3).sum()),
                    "fair": int((data == 4).sum()),
                    "poor": int((data == 5).sum()),
                },
                "confidence_interval": None,
                "transfer_risk": "medium",
                "limitations": [
                    "Single-item measure",
                    "Self-report bias",
                    "Scale direction: 1=excellent, 5=poor"
                ],
                "approved_for_route_b": False,
            })

    # Table 2: Life satisfaction
    sat_vars = [col for col in df.columns if col in ['A1SSATIS', 'B1SSATIS', 'C1SSATIS']]
    if sat_vars:
        col = sat_vars[0]
        data = df[col].dropna()
        # Filter out invalid values (98=DK, 99=Refused, -1=no SAQ)
        data = data[(data >= 0) & (data <= 10)]
        if len(data) > 0:
            tables.append({
                "artifact_id": f"{dataset_id}_life_satisfaction",
                "dataset_source_id": dataset_id,
                "outcome_id": "life_satisfaction",
                "source_file": str(sav_path.name),
                "variable_names": [col],
                "subgroup_definition": "all_valid_respondents",
                "n_valid": int(len(data)),
                "n_missing": int(df[col].isna().sum()),
                "missingness_rate": round(df[col].isna().sum() / len(df) * 100, 2),
                "observed_rate_or_mean": round(data.mean(), 4),
                "distribution": {
                    "mean": round(data.mean(), 4),
                    "std": round(data.std(), 4),
                    "min": float(data.min()),
                    "max": float(data.max()),
                    "median": float(data.median()),
                },
                "confidence_interval": None,
                "transfer_risk": "high",
                "limitations": [
                    "Scale: 0-10 Cantril ladder",
                    "Social desirability bias",
                    "Set-point theory may limit predictive value"
                ],
                "approved_for_route_b": False,
            })

    # Table 3: Big Five - Neuroticism
    neuro_vars = [col for col in df.columns if col in ['A1SNEURO', 'B1SNEURO', 'C1SNEURO']]
    if neuro_vars:
        col = neuro_vars[0]
        data = df[col].dropna()
        # Filter out invalid values (-1=no SAQ, 8/9=not calculated)
        data = data[(data >= 1) & (data <= 4)]
        if len(data) > 0:
            tables.append({
                "artifact_id": f"{dataset_id}_big5_neuroticism",
                "dataset_source_id": dataset_id,
                "outcome_id": "neuroticism_negative_emotionality",
                "source_file": str(sav_path.name),
                "variable_names": [col],
                "subgroup_definition": "all_valid_respondents_with_SAQ",
                "n_valid": int(len(data)),
                "n_missing": int(df[col].isna().sum()),
                "missingness_rate": round(df[col].isna().sum() / len(df) * 100, 2),
                "observed_rate_or_mean": round(data.mean(), 4),
                "distribution": {
                    "mean": round(data.mean(), 4),
                    "std": round(data.std(), 4),
                    "min": float(data.min()),
                    "max": float(data.max()),
                },
                "confidence_interval": None,
                "transfer_risk": "high",
                "limitations": [
                    "Scale: 1-4 (low to high)",
                    "~11-19% missing due to SAQ non-response",
                    "Composite score from multiple items"
                ],
                "approved_for_route_b": False,
            })

    # Table 4: Perceived Mastery
    mast_vars = [col for col in df.columns if col in ['A1SMASTE', 'B1SMASTE', 'C1SMASTE']]
    if mast_vars:
        col = mast_vars[0]
        data = df[col].dropna()
        # Filter out invalid values (-1=no SAQ, 99=not calculated)
        data = data[(data >= 1) & (data <= 7)]
        if len(data) > 0:
            tables.append({
                "artifact_id": f"{dataset_id}_perceived_mastery",
                "dataset_source_id": dataset_id,
                "outcome_id": "perceived_control_or_mastery",
                "source_file": str(sav_path.name),
                "variable_names": [col],
                "subgroup_definition": "all_valid_respondents_with_SAQ",
                "n_valid": int(len(data)),
                "n_missing": int(df[col].isna().sum()),
                "missingness_rate": round(df[col].isna().sum() / len(df) * 100, 2),
                "observed_rate_or_mean": round(data.mean(), 4),
                "distribution": {
                    "mean": round(data.mean(), 4),
                    "std": round(data.std(), 4),
                    "min": float(data.min()),
                    "max": float(data.max()),
                },
                "confidence_interval": None,
                "transfer_risk": "medium",
                "limitations": [
                    "Scale: 1-7 (low to high mastery)",
                    "~11-19% missing due to SAQ non-response",
                    "Pearlin Mastery Scale composite"
                ],
                "approved_for_route_b": False,
            })

    # Table 5: Social Support
    support_vars = [col for col in df.columns if col in ['B1SCALL', 'B1SCSAT']]
    if support_vars:
        col = support_vars[0]
        data = df[col].dropna()
        # Filter out invalid values
        data = data[(data >= 1) & (data <= 5)]
        if len(data) > 0:
            tables.append({
                "artifact_id": f"{dataset_id}_social_support",
                "dataset_source_id": dataset_id,
                "outcome_id": "social_support_quality",
                "source_file": str(sav_path.name),
                "variable_names": support_vars,
                "subgroup_definition": "all_valid_respondents",
                "n_valid": int(len(data)),
                "n_missing": int(df[col].isna().sum()),
                "missingness_rate": round(df[col].isna().sum() / len(df) * 100, 2),
                "observed_rate_or_mean": round(data.mean(), 4),
                "distribution": {
                    "mean": round(data.mean(), 4),
                    "std": round(data.std(), 4),
                },
                "confidence_interval": None,
                "transfer_risk": "high",
                "limitations": [
                    "Self-reported quality",
                    "May not capture digital/remote support"
                ],
                "approved_for_route_b": False,
            })

    # Table 6: Demographics - Age
    age_vars = [col for col in df.columns if col in ['A1PAGE_M2', 'B1PAGE_M2', 'C1PRAGE']]
    if age_vars:
        col = age_vars[0]
        data = df[col].dropna()
        # Filter out invalid values (98=Refused, 99=Inapp)
        data = data[(data >= 15) & (data <= 100)]
        if len(data) > 0:
            tables.append({
                "artifact_id": f"{dataset_id}_demographics_age",
                "dataset_source_id": dataset_id,
                "outcome_id": "age_distribution",
                "source_file": str(sav_path.name),
                "variable_names": [col],
                "subgroup_definition": "all_valid_respondents",
                "n_valid": int(len(data)),
                "n_missing": int(df[col].isna().sum()),
                "missingness_rate": round(df[col].isna().sum() / len(df) * 100, 2),
                "observed_rate_or_mean": round(data.mean(), 4),
                "distribution": {
                    "mean": round(data.mean(), 4),
                    "std": round(data.std(), 4),
                    "min": float(data.min()),
                    "max": float(data.max()),
                    "median": float(data.median()),
                },
                "confidence_interval": None,
                "transfer_risk": "low",
                "limitations": [
                    "Age at interview, not current age"
                ],
                "approved_for_route_b": False,
            })

    # Table 7: Demographics - Sex
    sex_vars = [col for col in df.columns if col in ['A1PRSEX', 'B1PRSEX', 'C1PRSEX']]
    if sex_vars:
        col = sex_vars[0]
        data = df[col].dropna()
        # Filter out invalid values (8=Refused)
        data = data[(data >= 1) & (data <= 2)]
        if len(data) > 0:
            tables.append({
                "artifact_id": f"{dataset_id}_demographics_sex",
                "dataset_source_id": dataset_id,
                "outcome_id": "sex_distribution",
                "source_file": str(sav_path.name),
                "variable_names": [col],
                "subgroup_definition": "all_valid_respondents",
                "n_valid": int(len(data)),
                "n_missing": int(df[col].isna().sum()),
                "missingness_rate": round(df[col].isna().sum() / len(df) * 100, 2),
                "observed_rate_or_mean": round(data.mean(), 4),
                "distribution": {
                    "male": int((data == 1).sum()),
                    "female": int((data == 2).sum()),
                    "pct_female": round((data == 2).sum() / len(data) * 100, 2),
                },
                "confidence_interval": None,
                "transfer_risk": "low",
                "limitations": [
                    "Binary classification only"
                ],
                "approved_for_route_b": False,
            })

    return tables


def main():
    parser = argparse.ArgumentParser(description="Build baseline tables")
    parser.add_argument("--dataset", type=str, default="all",
                        choices=["midus1", "midus2", "midus3", "all"],
                        help="Dataset to process")
    parser.add_argument("--output", type=str, default=None,
                        help="Output path for JSON report")
    args = parser.parse_args()

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    datasets = {
        "midus1": REPO_ROOT / "labs/population_baseline/data/raw/midus/midus1/M1_P1_SURVEY_N7108_20190116.sav",
        "midus2": REPO_ROOT / "labs/population_baseline/data/raw/midus/midus2/M2_P1_SURVEY_N4963_20200720.sav",
        "midus3": REPO_ROOT / "labs/population_baseline/data/raw/midus/midus3/M3_P1_SURVEY_N3294_20251029.sav",
    }

    all_tables = []

    if args.dataset == "all":
        process_datasets = list(datasets.keys())
    else:
        process_datasets = [args.dataset]

    for dataset_id in process_datasets:
        sav_path = datasets[dataset_id]
        if not sav_path.exists():
            print(f"WARNING: {dataset_id} file not found: {sav_path}")
            continue

        print(f"Processing {dataset_id}...")
        tables = build_midus_baseline_tables(dataset_id, sav_path)
        all_tables.extend(tables)
        print(f"  Generated {len(tables)} baseline tables")

    # Write output
    output_path = Path(args.output) if args.output else ARTIFACTS_DIR / "baseline_tables_p15.json"
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path

    with open(output_path, 'w') as f:
        json.dump({
            "artifact_id": "baseline_tables_p15",
            "phase": "15",
            "created_at": "2026-06-03",
            "tables": all_tables,
            "total_tables": len(all_tables),
            "approved_for_route_b": False,
            "limitations": [
                "Exploratory baseline tables only",
                "No individual-level data",
                "No production ML integration",
                "No personal probabilities"
            ]
        }, f, indent=2)

    print(f"\nTotal tables generated: {len(all_tables)}")
    print(f"Output written to: {output_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
