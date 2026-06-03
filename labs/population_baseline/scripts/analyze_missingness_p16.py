#!/usr/bin/env python3
"""
Phase 16H — Missingness and Attrition Audit.

Computes aggregate missingness for MIDUS and NLSY97 variables.
No individual rows - aggregate statistics only.

Usage:
    python analyze_missingness_p16.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "labs" / "population_baseline" / "artifacts"

# MIDUS datasets
MIDUS_DATASETS = {
    "midus1": {
        "name": "MIDUS 1",
        "year": "1995-1996",
        "path": REPO_ROOT / "labs/population_baseline/data/raw/midus/midus1/M1_P1_SURVEY_N7108_20190116.sav",
    },
    "midus2": {
        "name": "MIDUS 2",
        "year": "2004-2006",
        "path": REPO_ROOT / "labs/population_baseline/data/raw/midus/midus2/M2_P1_SURVEY_N4963_20200720.sav",
    },
    "midus3": {
        "name": "MIDUS 3",
        "year": "2013-2014",
        "path": REPO_ROOT / "labs/population_baseline/data/raw/midus/midus3/M3_P1_SURVEY_N3294_20251029.sav",
    },
}

# Variables to audit
MIDUS_VARIABLES = {
    "self_rated_health": {
        "label": "Self-Rated Health",
        "codes": {"midus1": "A1PA4", "midus2": "B1PA1", "midus3": "C1PA1"},
    },
    "life_satisfaction": {
        "label": "Life Satisfaction",
        "codes": {"midus1": "A1SSATIS", "midus2": "B1SSATIS", "midus3": "C1SSATIS"},
    },
    "neuroticism": {
        "label": "Neuroticism",
        "codes": {"midus1": "A1SNEURO", "midus2": "B1SNEURO", "midus3": "C1SNEURO"},
    },
    "perceived_mastery": {
        "label": "Perceived Mastery",
        "codes": {"midus1": "A1SMASTE", "midus2": "B1SMASTE", "midus3": "C1SMASTE"},
    },
}


def audit_midus_missingness() -> list[dict]:
    """Audit missingness for MIDUS variables."""
    import pyreadstat

    audit_results = []

    for dataset_id, dataset_info in MIDUS_DATASETS.items():
        sav_path = dataset_info["path"]
        if not sav_path.exists():
            continue

        df, metadata = pyreadstat.read_sav(str(sav_path))
        n_total = len(df)

        for var_id, var_info in MIDUS_VARIABLES.items():
            code = var_info["codes"].get(dataset_id)
            if not code or code not in df.columns:
                continue

            n_missing = int(df[code].isna().sum())
            n_valid = n_total - n_missing
            missingness_rate = round(n_missing / n_total * 100, 2) if n_total > 0 else 0

            # Determine interpretation
            if missingness_rate < 5:
                interpretation = "Low missingness - acceptable for analysis"
            elif missingness_rate < 20:
                interpretation = "Moderate missingness - consider multiple imputation"
            else:
                interpretation = "High missingness - may bias results"

            audit_results.append({
                "variable": var_id,
                "variable_label": var_info["label"],
                "dataset": dataset_id,
                "dataset_name": dataset_info["name"],
                "wave": dataset_info["year"],
                "variable_code": code,
                "n_total": n_total,
                "n_valid": n_valid,
                "n_missing": n_missing,
                "missingness_rate": missingness_rate,
                "interpretation": interpretation,
                "limitation": "SAQ non-response for personality variables",
            })

    return audit_results


def main():
    print(f"Missingness and Attrition Audit")
    print()

    # Audit MIDUS
    print("Auditing MIDUS missingness...")
    midus_audit = audit_midus_missingness()
    print(f"  Audited {len(midus_audit)} variable-dataset combinations")

    # Build audit report
    audit_report = {
        "artifact_id": "missingness_audit_p16",
        "phase": "16",
        "created_at": "2026-06-03",
        "midus_audit": midus_audit,
        "nlsy97_audit": [],  # Placeholder - NLSY97 missingness not computed yet
        "summary": {
            "midus_variables_audited": len(set(r["variable"] for r in midus_audit)),
            "midus_datasets_audited": len(set(r["dataset"] for r in midus_audit)),
            "high_missingness_count": sum(1 for r in midus_audit if r["missingness_rate"] >= 20),
            "moderate_missingness_count": sum(1 for r in midus_audit if 5 <= r["missingness_rate"] < 20),
            "low_missingness_count": sum(1 for r in midus_audit if r["missingness_rate"] < 5),
        },
        "approved_for_route_b": False,
    }

    # Write output
    output_path = ARTIFACTS_DIR / "missingness_audit_p16.json"
    with open(output_path, 'w') as f:
        json.dump(audit_report, f, indent=2)

    print(f"Missingness audit written to: {output_path.relative_to(REPO_ROOT)}")

    # Print summary table
    print("\nMissingness Summary:")
    print(f"{'Variable':<25} {'Dataset':<15} {'N Total':<10} {'N Valid':<10} {'Missing %':<10} {'Interpretation'}")
    print("-" * 100)

    for r in midus_audit:
        print(f"{r['variable_label']:<25} {r['dataset_name']:<15} {r['n_total']:<10} "
              f"{r['n_valid']:<10} {r['missingness_rate']:<10} {r['interpretation']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
