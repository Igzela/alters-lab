#!/usr/bin/env python3
"""
Phase 16G — MIDUS Cross-Wave Analysis.

Analyzes aggregate cross-wave patterns in MIDUS data.
No individual longitudinal linkage - aggregate comparisons only.

Usage:
    python analyze_midus_cross_wave.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "labs" / "population_baseline" / "artifacts"

# MIDUS datasets
DATASETS = {
    "midus1": {
        "name": "MIDUS 1",
        "year": "1995-1996",
        "path": REPO_ROOT / "labs/population_baseline/data/raw/midus/midus1/M1_P1_SURVEY_N7108_20190116.sav",
        "n_total": 7108,
    },
    "midus2": {
        "name": "MIDUS 2",
        "year": "2004-2006",
        "path": REPO_ROOT / "labs/population_baseline/data/raw/midus/midus2/M2_P1_SURVEY_N4963_20200720.sav",
        "n_total": 4963,
    },
    "midus3": {
        "name": "MIDUS 3",
        "year": "2013-2014",
        "path": REPO_ROOT / "labs/population_baseline/data/raw/midus/midus3/M3_P1_SURVEY_N3294_20251029.sav",
        "n_total": 3294,
    },
}

# Variables to analyze across waves
VARIABLES = {
    "self_rated_health": {
        "label": "Self-Rated Health",
        "codes": {"midus1": "A1PA4", "midus2": "B1PA1", "midus3": "C1PA1"},
        "scale": "1-5 (1=excellent, 5=poor)",
        "direction": "lower_is_better",
    },
    "life_satisfaction": {
        "label": "Life Satisfaction",
        "codes": {"midus1": "A1SSATIS", "midus2": "B1SSATIS", "midus3": "C1SSATIS"},
        "scale": "0-10 Cantril ladder",
        "direction": "higher_is_better",
    },
    "neuroticism": {
        "label": "Neuroticism",
        "codes": {"midus1": "A1SNEURO", "midus2": "B1SNEURO", "midus3": "C1SNEURO"},
        "scale": "1-4 (low to high)",
        "direction": "lower_is_better",
    },
    "perceived_mastery": {
        "label": "Perceived Mastery",
        "codes": {"midus1": "A1SMASTE", "midus2": "B1SMASTE", "midus3": "C1SMASTE"},
        "scale": "1-7 (low to high mastery)",
        "direction": "higher_is_better",
    },
    "age": {
        "label": "Age",
        "codes": {"midus1": "A1PAGE_M2", "midus2": "B1PAGE_M2", "midus3": "C1PRAGE"},
        "scale": "continuous (years)",
        "direction": "neutral",
    },
}


def analyze_wave(dataset_id: str, dataset_info: dict) -> dict:
    """Analyze a single MIDUS wave."""
    import pyreadstat

    sav_path = dataset_info["path"]
    if not sav_path.exists():
        return {"error": f"File not found: {sav_path}"}

    df, metadata = pyreadstat.read_sav(str(sav_path))

    wave_stats = {
        "dataset_id": dataset_id,
        "dataset_name": dataset_info["name"],
        "year": dataset_info["year"],
        "n_total": dataset_info["n_total"],
        "variables": {},
    }

    for var_id, var_info in VARIABLES.items():
        code = var_info["codes"].get(dataset_id)
        if not code or code not in df.columns:
            continue

        data = df[code].dropna()

        # Filter invalid values based on variable
        if var_id == "self_rated_health":
            data = data[data <= 5]
        elif var_id == "life_satisfaction":
            data = data[(data >= 0) & (data <= 10)]
        elif var_id == "neuroticism":
            data = data[(data >= 1) & (data <= 4)]
        elif var_id == "perceived_mastery":
            data = data[(data >= 1) & (data <= 7)]
        elif var_id == "age":
            data = data[(data >= 15) & (data <= 100)]

        if len(data) > 0:
            wave_stats["variables"][var_id] = {
                "variable_code": code,
                "variable_label": var_info["label"],
                "n_valid": int(len(data)),
                "n_missing": int(df[code].isna().sum()),
                "missingness_rate": round(df[code].isna().sum() / len(df) * 100, 2),
                "mean": round(data.mean(), 4),
                "std": round(data.std(), 4),
                "min": float(data.min()),
                "max": float(data.max()),
                "median": float(data.median()),
            }

    return wave_stats


def main():
    print(f"MIDUS Cross-Wave Analysis")
    print()

    all_waves = []

    for dataset_id, dataset_info in DATASETS.items():
        print(f"Analyzing {dataset_info['name']}...")
        wave_stats = analyze_wave(dataset_id, dataset_info)
        all_waves.append(wave_stats)

        if "error" in wave_stats:
            print(f"  ERROR: {wave_stats['error']}")
        else:
            print(f"  Variables analyzed: {len(wave_stats['variables'])}")

    print()

    # Build cross-wave comparison
    cross_wave = {
        "artifact_id": "midus_cross_wave_analysis_p16",
        "phase": "16",
        "created_at": "2026-06-03",
        "waves": all_waves,
        "comparison_notes": {
            "methodology": "Aggregate cross-wave comparison, not individual longitudinal linkage",
            "attrition": "Sample sizes decrease across waves due to attrition",
            "cohort_effects": "Not controlled - interpret as cross-sectional patterns",
            "caution": "Do not claim aging effects without controlling cohort/attrition",
        },
        "approved_for_route_b": False,
    }

    # Write output
    output_path = ARTIFACTS_DIR / "midus_cross_wave_analysis_p16.json"
    with open(output_path, 'w') as f:
        json.dump(cross_wave, f, indent=2)

    print(f"Cross-wave analysis written to: {output_path.relative_to(REPO_ROOT)}")

    # Print comparison table
    print("\nCross-Wave Comparison:")
    print(f"{'Variable':<25} {'MIDUS 1':<15} {'MIDUS 2':<15} {'MIDUS 3':<15}")
    print("-" * 70)

    for var_id, var_info in VARIABLES.items():
        means = []
        for wave in all_waves:
            if "error" not in wave and var_id in wave["variables"]:
                means.append(f"{wave['variables'][var_id]['mean']:.2f}")
            else:
                means.append("N/A")

        print(f"{var_info['label']:<25} {means[0]:<15} {means[1]:<15} {means[2]:<15}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
