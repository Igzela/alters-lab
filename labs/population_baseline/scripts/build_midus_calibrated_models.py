#!/usr/bin/env python3
"""
MIDUS Calibrated Model Builder.

Builds logistic regression models predicting cross-domain binary outcomes
from MIDUS-2 baseline features using actual survey data. Produces calibrated
baseline models with Brier scores, AUC, calibration curves, and model cards.

Reads MIDUS-2 SPSS file via pyreadstat. Respects scale directions:
  - M2 health (B1PA1): 1=excellent, 5=poor (lower = better)

Usage:
    python build_midus_calibrated_models.py \
        --sav-path labs/population_baseline/data/raw/midus/midus2/M2_P1_SURVEY_N4963_20200720.sav \
        --output labs/population_baseline/artifacts/midus_calibrated_models_v3.json
"""

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

import pyreadstat
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "labs" / "population_baseline" / "artifacts"

# --- Variable definitions ---

# Feature variables (predictors from MIDUS-2)
FEATURE_VARIABLES = {
    "B1SCONDP": {
        "label": "Chronic conditions count",
        "domain": "health",
        "measurement": "continuous",
    },
    "B1SCALL": {
        "label": "Social support total",
        "domain": "social",
        "measurement": "continuous",
    },
    "B1SCSAT": {
        "label": "Social satisfaction",
        "domain": "social",
        "measurement": "continuous",
    },
    "B1SSATIS": {
        "label": "Life satisfaction",
        "domain": "wellbeing",
        "measurement": "ordinal",
    },
    "B1SMASTE": {
        "label": "Personal mastery",
        "domain": "psychological",
        "measurement": "continuous",
    },
    "B1SNEURO": {
        "label": "Neuroticism",
        "domain": "personality",
        "measurement": "continuous",
    },
    "B1PAGE_M2": {
        "label": "Age at MIDUS-2",
        "domain": "demographics",
        "measurement": "continuous",
    },
    "B1PRSEX": {
        "label": "Sex",
        "domain": "demographics",
        "measurement": "categorical",
        "value_labels": {"1": "Male", "2": "Female"},
    },
    "B1SA52A": {
        "label": "Sleep quality",
        "domain": "health_behavior",
        "measurement": "ordinal",
    },
    "B1SA40A": {
        "label": "Physical activity level",
        "domain": "health_behavior",
        "measurement": "ordinal",
    },
}

# Outcome variable used to derive binary labels
OUTCOME_VARIABLE = {
    "B1PA1": {
        "label": "Self-rated health",
        "domain": "health",
        "measurement": "ordinal",
        "value_labels": {
            "1": "Excellent", "2": "Very good", "3": "Good",
            "4": "Fair", "5": "Poor",
        },
        "direction": "lower_is_better",
    },
}

# Sentinel values to filter out (MIDUS-2 SAQ / non-applicable codes)
SENTINEL_NEGATIVE = {-1}   # No SAQ data
SENTINEL_HIGH = {8, 9, 98, 99}  # Not calculated / missing

# Default imputation values per feature
IMPUTATION_DEFAULTS = {
    "B1SCONDP": 0.0,   # No chronic conditions
    "B1SCALL": 0.0,    # No social support
    "B1SCSAT": 0.0,    # No social satisfaction
    "B1SSATIS": 5.0,   # Neutral life satisfaction
    "B1SMASTE": 3.0,   # Mid-range mastery
    "B1SNEURO": 3.0,   # Mid-range neuroticism
    "B1PAGE_M2": 55.0, # MIDUS-2 median age approximate
    "B1PRSEX": 1.0,    # Default male
    "B1SA52A": 3.0,    # Mid-range sleep
    "B1SA40A": 2.0,    # Mid-range activity
}


def is_sentinel(value: float) -> bool:
    """Check if a value is a MIDUS sentinel / missing code."""
    if value != value:  # NaN check
        return True
    iv = int(value)
    return iv in SENTINEL_NEGATIVE or iv in SENTINEL_HIGH


def read_midus_sav(sav_path: Path) -> tuple:
    """Read MIDUS-2 SPSS file and return (DataFrame, metadata)."""
    print(f"  Reading: {sav_path.name}")
    df, metadata = pyreadstat.read_sav(str(sav_path))
    print(f"  Rows: {len(df):,}, Columns: {len(df.columns):,}")
    return df, metadata


def extract_and_clean(df, variables: dict[str, dict]) -> tuple[list[dict], dict]:
    """
    Extract variables from DataFrame and filter sentinel values.

    Returns (cleaned_rows, variable_stats) where cleaned_rows is a list of
    dicts mapping variable name to float value (no NaN / sentinels).
    """
    var_names = list(variables.keys())
    available = [v for v in var_names if v in df.columns]
    missing = [v for v in var_names if v not in df.columns]

    if missing:
        print(f"  WARNING: Missing variables: {missing}")

    stats = {v: {"total": len(df), "valid": 0, "sentinel": 0, "nan": 0} for v in available}
    cleaned_rows = []

    for _, row in df.iterrows():
        record = {}
        skip = False
        for v in available:
            val = row[v]
            if val != val:  # NaN
                stats[v]["nan"] += 1
                skip = True
                break
            if is_sentinel(val):
                stats[v]["sentinel"] += 1
                skip = True
                break
            record[v] = float(val)
            stats[v]["valid"] += 1
        if not skip:
            cleaned_rows.append(record)

    return cleaned_rows, stats


def create_binary_outcomes(rows: list[dict]) -> tuple[list[int], dict]:
    """
    Create binary outcome labels from MIDUS-2 data.

    Outcomes:
      - health_good_excellent: B1PA1 <= 3 (1=excellent, lower is better in M2)
      - high_social_support: B1SCALL > median of valid values
      - high_life_satisfaction: B1SSATIS >= 7

    Returns (health_labels, outcome_metadata).
    """
    # Compute median social support for binary split
    valid_support = [r["B1SCALL"] for r in rows if "B1SCALL" in r]
    support_median = statistics.median(valid_support) if valid_support else 0

    valid_lsat = [r["B1SSATIS"] for r in rows if "B1SSATIS" in r]
    lsat_median = statistics.median(valid_lsat) if valid_lsat else 0

    health_labels = []
    social_labels = []
    lsat_labels = []

    for row in rows:
        # Health: B1PA1 <= 3 means good/very good/excellent (lower = better)
        hp = row.get("B1PA1")
        health_labels.append(1 if hp is not None and hp <= 3 else 0)

        # Social support: above median
        sp = row.get("B1SCALL")
        social_labels.append(1 if sp is not None and sp > support_median else 0)

        # Life satisfaction: >= 7
        lp = row.get("B1SSATIS")
        lsat_labels.append(1 if lp is not None and lp >= 7 else 0)

    n_h = sum(health_labels)
    n_s = sum(social_labels)
    n_l = sum(lsat_labels)
    n = len(rows)
    print(f"  health_good_excellent: {n_h}/{n} ({n_h/n*100:.1f}%)")
    print(f"  high_social_support:   {n_s}/{n} ({n_s/n*100:.1f}%)")
    print(f"  high_life_satisfaction: {n_l}/{n} ({n_l/n*100:.1f}%)")

    metadata = {
        "support_median": round(support_median, 4),
        "lsat_median": round(lsat_median, 4),
    }
    return health_labels, social_labels, lsat_labels, metadata


def build_feature_matrix(rows: list[dict]) -> tuple[list[list[float]], list[str]]:
    """
    Build feature matrix from MIDUS-2 variables.

    Imputes missing values with population-mode defaults.
    Sex (B1PRSEX): 1=male, 2=female → sex_female binary.
    """
    feature_names = [
        "chronic_conditions", "social_support", "social_satisfaction",
        "life_satisfaction", "mastery", "neuroticism",
        "age", "sex_female", "sleep_quality", "physical_activity",
    ]

    X = []
    for row in rows:
        chronic = row.get("B1SCONDP", IMPUTATION_DEFAULTS["B1SCONDP"])
        support = row.get("B1SCALL", IMPUTATION_DEFAULTS["B1SCALL"])
        soc_sat = row.get("B1SCSAT", IMPUTATION_DEFAULTS["B1SCSAT"])
        life_sat = row.get("B1SSATIS", IMPUTATION_DEFAULTS["B1SSATIS"])
        mastery = row.get("B1SMASTE", IMPUTATION_DEFAULTS["B1SMASTE"])
        neuro = row.get("B1SNEURO", IMPUTATION_DEFAULTS["B1SNEURO"])
        age = row.get("B1PAGE_M2", IMPUTATION_DEFAULTS["B1PAGE_M2"])
        sex = row.get("B1PRSEX", IMPUTATION_DEFAULTS["B1PRSEX"])
        sleep = row.get("B1SA52A", IMPUTATION_DEFAULTS["B1SA52A"])
        activity = row.get("B1SA40A", IMPUTATION_DEFAULTS["B1SA40A"])

        # Sex: 2=female → 1.0, else 0.0
        sex_female = 1.0 if sex == 2.0 else 0.0

        X.append([
            chronic, support, soc_sat, life_sat, mastery, neuro,
            age, sex_female, sleep, activity,
        ])

    return X, feature_names


def compute_calibration_bins(y_true: list[int], y_prob: list[float], n_bins: int = 10) -> list[dict]:
    """Compute calibration curve: for each bin of predicted probabilities, show actual fraction positive."""
    pairs = sorted(zip(y_prob, y_true), key=lambda p: p[0])
    bin_size = max(1, len(pairs) // n_bins)

    bins = []
    for i in range(0, len(pairs), bin_size):
        chunk = pairs[i : i + bin_size]
        if not chunk:
            continue
        mean_predicted = sum(p for p, _ in chunk) / len(chunk)
        mean_actual = sum(y for _, y in chunk) / len(chunk)
        bins.append({
            "bin_lower": round(min(p for p, _ in chunk), 4),
            "bin_upper": round(max(p for p, _ in chunk), 4),
            "mean_predicted_prob": round(mean_predicted, 4),
            "fraction_positive": round(mean_actual, 4),
            "n_samples": len(chunk),
        })

    return bins


def train_and_evaluate(
    X_train: list[list[float]],
    X_test: list[list[float]],
    y_train: list[int],
    y_test: list[int],
    feature_names: list[str],
    outcome_name: str,
) -> dict:
    """Train logistic regression and compute all metrics."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_prob = model.predict_proba(X_test_scaled)[:, 1].tolist()
    y_pred = model.predict(X_test_scaled).tolist()

    brier = brier_score_loss(y_test, y_prob)

    unique_test = set(y_test)
    if len(unique_test) >= 2:
        auc = roc_auc_score(y_test, y_prob)
    else:
        auc = None

    accuracy = sum(1 for a, b in zip(y_pred, y_test) if a == b) / len(y_test)
    calibration_bins = compute_calibration_bins(y_test, y_prob)

    coefficients = {}
    for name, coef in zip(feature_names, model.coef_[0].tolist()):
        coefficients[name] = round(coef, 4)
    intercept = round(float(model.intercept_[0]), 4)

    # Weak model gate
    is_weak = False
    rejection_reasons = []
    if auc is not None and auc < 0.6:
        is_weak = True
        rejection_reasons.append(f"AUC {auc:.3f} < 0.6 threshold")
    if brier > 0.25:
        is_weak = True
        rejection_reasons.append(f"Brier score {brier:.4f} > 0.25 threshold")

    status = "rejected" if is_weak else "accepted"
    artifact_class = "data_backed_baseline" if is_weak else "calibrated_model"

    n_positive_train = sum(y_train)
    n_positive_test = sum(y_test)

    return {
        "model_type": "logistic_regression",
        "outcome": outcome_name,
        "n_train": len(y_train),
        "n_test": len(y_test),
        "n_positive_train": n_positive_train,
        "n_positive_test": n_positive_test,
        "positive_rate_train": round(n_positive_train / len(y_train), 4),
        "positive_rate_test": round(n_positive_test / len(y_test), 4),
        "brier_score": round(brier, 6),
        "auc_roc": round(auc, 6) if auc is not None else None,
        "accuracy": round(accuracy, 4),
        "calibration_bins": calibration_bins,
        "coefficients": coefficients,
        "intercept": intercept,
        "feature_names": feature_names,
        "feature_imputation": {k: f"missing -> {v}" for k, v in IMPUTATION_DEFAULTS.items()},
        "status": status,
        "rejection_reasons": rejection_reasons if rejection_reasons else None,
        "artifact_class": artifact_class,
        "approval_level": "descriptive_only" if is_weak else "data_backed",
    }


def build_model_card(models: list[dict], n_accepted: int, n_rejected: int, total_rows: int) -> dict:
    """Build the model card metadata block."""
    return {
        "artifact_class": "calibrated_model" if n_accepted > 0 else "data_backed_baseline",
        "approval_level": "data_backed" if n_accepted > 0 else "descriptive_only",
        "n_models": len(models),
        "n_accepted": n_accepted,
        "n_rejected": n_rejected,
        "acceptance_criteria": {
            "min_auc": 0.6,
            "max_brier": 0.25,
        },
        "feature_variables": [
            {"code": code, "label": info["label"], "domain": info["domain"]}
            for code, info in FEATURE_VARIABLES.items()
        ],
        "outcome_variable": {
            "code": "B1PA1",
            "label": "Self-rated health (MIDUS-2)",
            "domain": "health",
            "scale_direction": "lower_is_better (1=excellent, 5=poor)",
        },
        "binary_outcomes": [
            {
                "name": "health_good_excellent",
                "definition": "B1PA1 <= 3 (good, very good, or excellent)",
                "source_variable": "B1PA1",
                "scale_note": "M2 health: 1=excellent, lower is better",
            },
            {
                "name": "high_social_support",
                "definition": "B1SCALL > median of valid values",
                "source_variable": "B1SCALL",
            },
            {
                "name": "high_life_satisfaction",
                "definition": "B1SSATIS >= 7",
                "source_variable": "B1SSATIS",
            },
        ],
        "imputation_policy": {
            k: f"missing -> {v}" for k, v in IMPUTATION_DEFAULTS.items()
        },
        "limitations": [
            f"MIDUS-2 cross-sectional sample: {total_rows:,} usable respondents",
            "Cross-domain prediction (health, social, wellbeing) from single-wave data",
            "Logistic regression only — no nonlinear interaction terms",
            "No individual-level predictions committed",
            "No life_score or personal probability emitted",
            "Sentinel values (-1, 8, 9, 98, 99) excluded as missing",
            "Missing features imputed with population-mode defaults",
            "Scale direction respected: M2 health 1=excellent (lower=better)",
        ],
        "transfer_risk": {
            "level": "moderate",
            "reasons": [
                "MIDUS-2 is a US national sample (not population-representative for all contexts)",
                "Single-wave cross-sectional design limits causal inference",
                "Age range ~25-74 at MIDUS-2 — transfer to younger/older populations uncertain",
            ],
        },
    }


def main():
    parser = argparse.ArgumentParser(description="MIDUS Calibrated Model Builder")
    parser.add_argument(
        "--sav-path", type=str, required=True,
        help="Path to MIDUS-2 SPSS .sav file",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output JSON path (default: labs/population_baseline/artifacts/midus_calibrated_models_v3.json)",
    )
    args = parser.parse_args()

    sav_path = Path(args.sav_path)
    if not sav_path.is_absolute():
        sav_path = REPO_ROOT / sav_path

    if not sav_path.exists():
        print(f"ERROR: File not found: {sav_path}")
        return 1

    output_path = Path(args.output) if args.output else ARTIFACTS_DIR / "midus_calibrated_models_v3.json"
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path

    print("MIDUS Calibrated Model Builder")
    print(f"  Source: {sav_path.name}")
    print(f"  Output: {output_path}")
    print()

    # --- Step 1: Read SPSS ---
    print("Step 1: Reading MIDUS-2 SPSS file...")
    df, metadata = read_midus_sav(sav_path)

    # --- Step 2: Extract and clean ---
    print("\nStep 2: Extracting variables and filtering sentinels...")
    all_vars = {**FEATURE_VARIABLES, **OUTCOME_VARIABLE}
    rows, var_stats = extract_and_clean(df, all_vars)

    print(f"  Usable rows after sentinel filter: {len(rows):,}")
    for v, s in var_stats.items():
        print(f"    {v}: {s['valid']:,} valid, {s['sentinel']:,} sentinel, {s['nan']:,} NaN")

    if len(rows) < 100:
        print(f"\nERROR: Too few usable rows ({len(rows)}). Need at least 100.")
        return 1

    print()

    # --- Step 3: Build features ---
    print("Step 3: Building feature matrix...")
    X, feature_names = build_feature_matrix(rows)
    print(f"  Features: {feature_names}")
    print(f"  Matrix shape: {len(X)} x {len(X[0])}")
    print()

    # --- Step 4: Create binary outcomes ---
    print("Step 4: Creating binary outcomes...")
    health_labels, social_labels, lsat_labels, outcome_meta = create_binary_outcomes(rows)
    print()

    # --- Step 5: Train/test split ---
    print("Step 5: Splitting data 80/20...")
    X_tr_h, X_te_h, y_tr_h, y_te_h = train_test_split(X, health_labels, test_size=0.2, random_state=42)
    X_tr_s, X_te_s, y_tr_s, y_te_s = train_test_split(X, social_labels, test_size=0.2, random_state=42)
    X_tr_l, X_te_l, y_tr_l, y_te_l = train_test_split(X, lsat_labels, test_size=0.2, random_state=42)
    print(f"  health model: train={len(y_tr_h)}, test={len(y_te_h)}")
    print(f"  social model: train={len(y_tr_s)}, test={len(y_te_s)}")
    print(f"  lsat model:   train={len(y_tr_l)}, test={len(y_te_l)}")
    print()

    # --- Step 6: Train models ---
    print("Step 6: Training logistic regression models...")
    health_model = train_and_evaluate(X_tr_h, X_te_h, y_tr_h, y_te_h, feature_names, "health_good_excellent")
    social_model = train_and_evaluate(X_tr_s, X_te_s, y_tr_s, y_te_s, feature_names, "high_social_support")
    lsat_model = train_and_evaluate(X_tr_l, X_te_l, y_tr_l, y_te_l, feature_names, "high_life_satisfaction")

    for m in [health_model, social_model, lsat_model]:
        auc_str = f"{m['auc_roc']:.3f}" if m['auc_roc'] is not None else "N/A"
        print(f"  {m['outcome']}: AUC={auc_str}, Brier={m['brier_score']:.4f}, status={m['status']}")
    print()

    # --- Step 7: Build artifact ---
    print("Step 7: Building artifact...")
    models = [health_model, social_model, lsat_model]
    n_accepted = sum(1 for m in models if m["status"] == "accepted")
    n_rejected = sum(1 for m in models if m["status"] == "rejected")

    output = {
        "artifact_id": "midus_calibrated_models_v3",
        "version": "3.0",
        "artifact_class": "calibrated_model" if n_accepted > 0 else "data_backed_baseline",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data_source": "midus2",
        "data_source_description": "Midlife in the United States (MIDUS-2) Survey",
        "data_file": sav_path.name,
        "sample_size_usable": len(rows),
        "scale_direction": "M2 health: 1=excellent, 5=poor (lower=better)",
        "train_test_split": "80/20",
        "model_family": "logistic_regression",
        "outcome_metadata": outcome_meta,
        "models": models,
        "model_card": build_model_card(models, n_accepted, n_rejected, len(rows)),
        "safety_confirmations": {
            "no_raw_data_committed": True,
            "no_individual_predictions": True,
            "no_individual_data": True,
            "no_personal_probabilities": True,
            "no_life_score": True,
            "aggregate_statistics_only": True,
        },
    }

    # --- Step 8: Write output ---
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {output_path}")
    print(f"Models: {len(models)} ({n_accepted} accepted, {n_rejected} rejected)")
    for m in models:
        auc_str = f"{m['auc_roc']:.3f}" if m['auc_roc'] is not None else "N/A"
        print(f"  {m['outcome']}: AUC={auc_str}, Brier={m['brier_score']:.4f}, status={m['status']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
