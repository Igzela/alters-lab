#!/usr/bin/env python3
"""
NLSY97 Calibrated Model Builder.

Builds logistic regression models predicting 2015 outcomes from 2005 baseline
features using actual NLSY97 data. Produces calibrated baseline models with
Brier scores, AUC, calibration curves, and model cards.

Streams from ZIP archive (no full extraction) to avoid loading 8GB CSV into memory.

Usage:
    python build_nlsy97_calibrated_models.py \
        --zip labs/population_baseline/data/raw/nlsy97/nlsy97_all_1997-2023.zip \
        --sample-size 50000
"""

import argparse
import csv
import io
import json
import statistics
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from sklearn.calibration import CalibratedClassifierCV
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "labs" / "population_baseline" / "artifacts"

# NLSY97 standard missing value codes
NLSY97_MISSING_CODES = {"-1", "-2", "-3", "-4", "-5"}

# --- Variable definitions ---

# 2015 outcome variables (respondents age 31-35)
OUTCOME_VARIABLES = {
    "U0009400": {
        "label": "CV_HIGHEST_DEGREE_EVER 2015",
        "domain": "career_education",
        "measurement": "ordinal",
    },
    "U0008900": {
        "label": "CV_INCOME_FAMILY 2015",
        "domain": "financial",
        "measurement": "continuous",
    },
}

# 2005 baseline feature variables (respondents age 25-29)
FEATURE_VARIABLES = {
    "S5412600": {
        "label": "CV_HGC_EVER 2005 (Highest Grade Completed)",
        "domain": "career_education",
        "measurement": "continuous",
    },
    "S5413300": {
        "label": "CV_HIGHEST_DEGREE_EVER 2005",
        "domain": "career_education",
        "measurement": "ordinal",
        "value_labels": {
            "0": "None", "1": "GED", "2": "High school diploma",
            "3": "Associate degree", "4": "Bachelor's degree",
            "5": "Master's degree", "6": "Doctorate", "7": "Professional degree",
        },
    },
    "S5412800": {
        "label": "CV_INCOME_FAMILY 2005",
        "domain": "financial",
        "measurement": "continuous",
    },
    "R0000400": {
        "label": "Sex",
        "domain": "demographics",
        "measurement": "categorical",
        "value_labels": {"0": "Male", "1": "Female"},
    },
    "R0000500": {
        "label": "Race",
        "domain": "demographics",
        "measurement": "categorical",
        "value_labels": {
            "1": "Black",
            "2": "Hispanic",
            "3": "Mixed race",
            "0": "Other",
        },
    },
    # --- Tier 1 additions: more features ---
    "S5405600": {
        "label": "CV_CENSUS_REGION 2005",
        "domain": "demographics",
        "measurement": "categorical",
    },
    "S5413000": {
        "label": "CV_HH_SIZE 2005 (Household Size)",
        "domain": "social",
        "measurement": "continuous",
    },
    "S5423000": {
        "label": "CV_MARSTAT 2005 (Marital Status)",
        "domain": "social",
        "measurement": "categorical",
    },
    "R1210700": {
        "label": "CV_PIAT_PERCENTILE_SCORE 1997 (Cognitive Ability)",
        "domain": "cognitive",
        "measurement": "continuous",
    },
    "R0538900": {
        "label": "CAT-ASVAB!STPEL (Symbol) 1997",
        "domain": "cognitive",
        "measurement": "continuous",
    },
    "R1302400": {
        "label": "CV_HGC_BIO_DAD 1997 (Father's Education)",
        "domain": "demographics",
        "measurement": "continuous",
    },
    "R1302500": {
        "label": "CV_HGC_BIO_MOM 1997 (Mother's Education)",
        "domain": "demographics",
        "measurement": "continuous",
    },
}

DEGREE_VALUE_LABELS = {
    "0": "None", "1": "GED", "2": "High school diploma",
    "3": "Associate degree", "4": "Bachelor's degree",
    "5": "Master's degree", "6": "Doctorate", "7": "Professional degree",
}


def safe_float(value: str) -> float | None:
    """Parse float from NLSY97 value, returning None for missing/invalid."""
    if not value or value.strip() in NLSY97_MISSING_CODES:
        return None
    try:
        return float(value.strip())
    except ValueError:
        return None


def stream_nlsy97_rows(
    zip_path: Path,
    feature_codes: list[str],
    outcome_codes: list[str],
    sample_size: int,
) -> list[dict[str, float | None]]:
    """
    Stream NLSY97 CSV from ZIP and collect rows with complete feature+outcome data.

    Returns list of dicts, each dict mapping variable code to numeric value (or None).
    Only rows with at least one valid outcome are included; features may have None
    (imputed to 0 later).
    """
    all_codes = list(dict.fromkeys(feature_codes + outcome_codes))
    rows: list[dict[str, float | None]] = []

    with zipfile.ZipFile(zip_path, "r") as zf:
        csv_files = [f for f in zf.namelist() if f.lower().endswith(".csv")]
        if not csv_files:
            raise FileNotFoundError(f"No CSV file found in {zip_path}")

        csv_name = csv_files[0]
        print(f"  Opening {csv_name} from ZIP archive...")

        with zf.open(csv_name) as f:
            reader = csv.reader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"))
            header = next(reader, None)
            if not header:
                raise ValueError("Empty CSV header")

            col_indices = {}
            missing_codes = set()
            for code in all_codes:
                if code in header:
                    col_indices[code] = header.index(code)
                else:
                    print(f"  WARNING: {code} not in CSV header — will be skipped")

            found_codes = list(col_indices.keys())
            print(f"  Found {len(found_codes)}/{len(all_codes)} variables in CSV")

            n_scanned = 0
            n_with_outcome = 0

            for row in reader:
                n_scanned += 1
                if n_scanned > sample_size:
                    break

                # Check at least one outcome is valid
                has_valid_outcome = False
                for oc in outcome_codes:
                    if oc in col_indices:
                        idx = col_indices[oc]
                        if idx < len(row):
                            val = safe_float(row[idx])
                            if val is not None:
                                has_valid_outcome = True
                                break

                if not has_valid_outcome:
                    continue

                record: dict[str, float | None] = {}
                for code in found_codes:
                    idx = col_indices[code]
                    val = safe_float(row[idx]) if idx < len(row) else None
                    record[code] = val

                rows.append(record)
                n_with_outcome += 1

            print(f"  Scanned {n_scanned:,} rows, {n_with_outcome:,} with valid outcome data")

    return rows


def create_binary_outcomes(rows: list[dict], income_col: str) -> tuple[list[int], list[int]]:
    """
    Create binary outcome vectors from raw data.

    bachelor_or_higher: degree (U0009400) >= 4
    above_median_income: income (U0008900) > median of valid values

    Returns (bachelor_labels, income_labels) — both length = len(rows).
    Rows missing the relevant outcome get label 0 (conservative default).
    """
    degree_col = "U0009400"

    # Compute income median from valid values first
    valid_incomes = [
        rows[i][income_col]
        for i in range(len(rows))
        if rows[i].get(income_col) is not None and rows[i][income_col] > 0
    ]
    income_median = statistics.median(valid_incomes) if valid_incomes else 0
    print(f"  Income median (valid values): ${income_median:,.0f}")
    print(f"  Valid income values for median: {len(valid_incomes):,}")

    bachelor_labels = []
    income_labels = []

    for row in rows:
        # Bachelor or higher
        deg = row.get(degree_col)
        if deg is not None:
            bachelor_labels.append(1 if deg >= 4 else 0)
        else:
            bachelor_labels.append(0)

        # Above median income
        inc = row.get(income_col)
        if inc is not None and inc > 0:
            income_labels.append(1 if inc > income_median else 0)
        else:
            income_labels.append(0)

    n_bachelor = sum(bachelor_labels)
    n_above = sum(income_labels)
    print(f"  bachelor_or_higher: {n_bachelor}/{len(bachelor_labels)} positive ({n_bachelor/len(bachelor_labels)*100:.1f}%)")
    print(f"  above_median_income: {n_above}/{len(income_labels)} positive ({n_above/len(income_labels)*100:.1f}%)")

    return bachelor_labels, income_labels, income_median


def build_feature_matrix(
    rows: list[dict],
    exclude_columns: set[str] | None = None,
) -> tuple[list[list[float]], list[str]]:
    """
    Build feature matrix from 2005 baseline variables + Tier 1 additions.

    Base features:
      - grade_2005, degree_2005, income_2005
      - sex_female, race_white, race_black, race_hispanic

    Tier 1 additions:
      - census_region (S5405600): region dummies
      - hh_size_2005 (S5413000): household size
      - marital_2005 (S5423000): married=1 / else=0
      - piat_pct_1997 (R1210700): cognitive ability percentile
      - asvab_stpel_1997 (R0538900): ASVAB symbol test
      - father_educ (R1302400): father's years of education
      - mother_educ (R1302500): mother's years of education

    Interaction terms:
      - degree_x_income: degree * log1p(income)
      - sex_x_grade: sex_female * grade

    Args:
        rows: data rows
        exclude_columns: variable codes to exclude (for leakage prevention)
    """
    exclude_columns = exclude_columns or set()

    # Build raw columns first (may include NaN for IterativeImputer)
    raw_columns: dict[str, list[float | None]] = {
        "grade_2005": [],
        "degree_2005": [],
        "income_2005": [],
        "sex_female": [],
        "race_white": [],
        "race_black": [],
        "race_hispanic": [],
        "census_region": [],
        "hh_size_2005": [],
        "married_2005": [],
        "piat_pct_1997": [],
        "asvab_stpel_1997": [],
        "father_educ": [],
        "mother_educ": [],
    }

    # Map raw column names to source variable codes
    col_to_var = {
        "grade_2005": "S5412600",
        "degree_2005": "S5413300",
        "income_2005": "S5412800",
        "sex_female": "R0000400",
        "race_white": "R0000500",
        "race_black": "R0000500",
        "race_hispanic": "R0000500",
        "census_region": "S5405600",
        "hh_size_2005": "S5413000",
        "married_2005": "S5423000",
        "piat_pct_1997": "R1210700",
        "asvab_stpel_1997": "R0538900",
        "father_educ": "R1302400",
        "mother_educ": "R1302500",
    }

    # Remove columns whose source variable is excluded
    if exclude_columns:
        raw_columns = {
            name: vals for name, vals in raw_columns.items()
            if col_to_var.get(name) not in exclude_columns
        }

    for row in rows:
        sex = row.get("R0000400")
        race = row.get("R0000500")
        income = row.get("S5412800")
        marital = row.get("S5423000")

        grade = row.get("S5412600")
        degree = row.get("S5413300")

        sex_female = 1.0 if sex == 1.0 else (0.0 if sex is not None else None)
        race_val = race if race is not None else None
        race_white = 1.0 if race_val == 0.0 else (0.0 if race_val is not None else None)
        race_black = 1.0 if race_val == 1.0 else (0.0 if race_val is not None else None)
        race_hispanic = 1.0 if race_val == 2.0 else (0.0 if race_val is not None else None)

        married = 1.0 if marital == 1.0 else (0.0 if marital is not None else None)

        raw_columns["grade_2005"].append(grade)
        raw_columns["degree_2005"].append(degree)
        raw_columns["income_2005"].append(income)
        raw_columns["sex_female"].append(sex_female)
        raw_columns["race_white"].append(race_white)
        raw_columns["race_black"].append(race_black)
        raw_columns["race_hispanic"].append(race_hispanic)
        if "census_region" in raw_columns:
            raw_columns["census_region"].append(row.get("S5405600"))
        if "hh_size_2005" in raw_columns:
            raw_columns["hh_size_2005"].append(row.get("S5413000"))
        if "married_2005" in raw_columns:
            raw_columns["married_2005"].append(married)
        if "piat_pct_1997" in raw_columns:
            raw_columns["piat_pct_1997"].append(row.get("R1210700"))
        if "asvab_stpel_1997" in raw_columns:
            raw_columns["asvab_stpel_1997"].append(row.get("R0538900"))
        if "father_educ" in raw_columns:
            raw_columns["father_educ"].append(row.get("R1302400"))
        if "mother_educ" in raw_columns:
            raw_columns["mother_educ"].append(row.get("R1302500"))

    # --- IterativeImputer for missing values ---
    feature_names = list(raw_columns.keys())
    n_rows = len(rows)
    n_features = len(feature_names)

    # Build matrix with NaN for missing
    import numpy as np
    X_nan = np.full((n_rows, n_features), np.nan)
    for j, name in enumerate(feature_names):
        for i, val in enumerate(raw_columns[name]):
            if val is not None:
                X_nan[i, j] = val

    imputer = IterativeImputer(max_iter=10, random_state=42, sample_posterior=False)
    X_imputed = imputer.fit_transform(X_nan)

    # Add interaction terms after imputation
    grade_idx = feature_names.index("grade_2005")
    degree_idx = feature_names.index("degree_2005")
    income_idx = feature_names.index("income_2005")
    sex_idx = feature_names.index("sex_female")

    import numpy as np
    log_income = np.log1p(np.clip(X_imputed[:, income_idx], 0, None))
    degree_x_income = X_imputed[:, degree_idx] * log_income
    sex_x_grade = X_imputed[:, sex_idx] * X_imputed[:, grade_idx]

    X_imputed = np.column_stack([X_imputed, degree_x_income, sex_x_grade])
    feature_names.extend(["degree_x_income", "sex_x_grade"])

    X = X_imputed.tolist()
    return X, feature_names


def compute_calibration_bins(y_true: list[int], y_prob: list[float], n_bins: int = 10) -> list[dict]:
    """Compute calibration curve bins: for each bin of predicted probabilities, show actual fraction positive."""
    # Pair and sort by predicted probability
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
    sample_size: int,
) -> dict:
    """Train logistic regression with isotonic calibration and compute all metrics."""
    import numpy as np

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    base_model = LogisticRegression(max_iter=1000, random_state=42)

    # Use isotonic calibration via CalibratedClassifierCV (Tier 1 improvement)
    # cv=5 for calibration on training set
    min_class = min(sum(y_train), len(y_train) - sum(y_train))
    cv_folds = min(5, min_class) if min_class > 1 else 2
    calibrated_model = CalibratedClassifierCV(
        base_model, method="isotonic", cv=cv_folds
    )
    calibrated_model.fit(X_train_scaled, y_train)

    # Predictions from calibrated model
    y_prob = calibrated_model.predict_proba(X_test_scaled)[:, 1].tolist()
    y_pred = [1 if p >= 0.5 else 0 for p in y_prob]

    # Also get uncalibrated probabilities for comparison
    base_model.fit(X_train_scaled, y_train)
    y_prob_raw = base_model.predict_proba(X_test_scaled)[:, 1].tolist()

    # Metrics (calibrated)
    brier = brier_score_loss(y_test, y_prob)
    brier_raw = brier_score_loss(y_test, y_prob_raw)

    # AUC requires both classes present
    unique_test = set(y_test)
    if len(unique_test) >= 2:
        auc = roc_auc_score(y_test, y_prob)
    else:
        auc = None

    # Classification accuracy
    accuracy = sum(1 for a, b in zip(y_pred, y_test) if a == b) / len(y_test)

    # Calibration curve
    calibration_bins = compute_calibration_bins(y_test, y_prob)

    # Coefficients (from base model, calibrated model doesn't expose coef)
    coefficients = {}
    for name, coef in zip(feature_names, base_model.coef_[0].tolist()):
        coefficients[name] = round(coef, 4)
    intercept = round(float(base_model.intercept_[0]), 4)

    # Quality gate
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
        "model_type": "logistic_regression_isotonic_calibrated",
        "outcome": outcome_name,
        "n_train": len(y_train),
        "n_test": len(y_test),
        "n_positive_train": n_positive_train,
        "n_positive_test": n_positive_test,
        "positive_rate_train": round(n_positive_train / len(y_train), 4),
        "positive_rate_test": round(n_positive_test / len(y_test), 4),
        "brier_score": round(brier, 6),
        "brier_score_raw": round(brier_raw, 6),
        "brier_improvement": round(brier_raw - brier, 6),
        "auc_roc": round(auc, 6) if auc is not None else None,
        "accuracy": round(accuracy, 4),
        "calibration_bins": calibration_bins,
        "coefficients": coefficients,
        "intercept": intercept,
        "feature_names": feature_names,
        "imputation_method": "IterativeImputer (multivariate, max_iter=10)",
        "calibration_method": "isotonic (CalibratedClassifierCV, cv=5)",
        "status": status,
        "rejection_reasons": rejection_reasons if rejection_reasons else None,
        "artifact_class": artifact_class,
        "approval_level": "descriptive_only" if is_weak else "data_backed",
    }


def main():
    parser = argparse.ArgumentParser(description="NLSY97 Calibrated Model Builder")
    parser.add_argument(
        "--zip", type=str, required=True,
        help="Path to NLSY97 ZIP archive",
    )
    parser.add_argument(
        "--sample-size", type=int, default=50000,
        help="Maximum rows to scan from CSV (default: 50000)",
    )
    args = parser.parse_args()

    zip_path = Path(args.zip)
    if not zip_path.is_absolute():
        zip_path = REPO_ROOT / zip_path

    if not zip_path.exists():
        print(f"ERROR: File not found: {zip_path}")
        return 1

    print("NLSY97 Calibrated Model Builder")
    print(f"Archive: {zip_path}")
    print(f"Sample size: {args.sample_size:,}")
    print(f"Outcome year: 2015 (respondents age 31-35)")
    print(f"Feature year: 2005 (respondents age 25-29)")
    print()

    # --- Step 1: Stream rows ---
    feature_codes = list(FEATURE_VARIABLES.keys())
    outcome_codes = list(OUTCOME_VARIABLES.keys())

    print("Step 1: Streaming NLSY97 data...")
    rows = stream_nlsy97_rows(zip_path, feature_codes, outcome_codes, args.sample_size)

    if len(rows) < 100:
        print(f"ERROR: Too few complete rows ({len(rows)}). Need at least 100.")
        return 1

    print(f"  Total usable rows: {len(rows):,}")
    print()

    # --- Step 2: Build features ---
    print("Step 2: Building feature matrix (2005 baseline)...")
    X, feature_names = build_feature_matrix(rows)
    print(f"  Features: {feature_names}")
    print(f"  Matrix shape: {len(X)} x {len(X[0])}")
    print()

    # --- Step 3: Create binary outcomes ---
    print("Step 3: Creating binary outcomes (2015)...")
    bachelor_labels, income_labels, income_median = create_binary_outcomes(rows, "U0008900")
    print()

    # --- Step 4: Train/test split ---
    print("Step 4: Splitting data 80/20...")
    X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(
        X, bachelor_labels, test_size=0.2, random_state=42
    )
    X_train_i, X_test_i, y_train_i, y_test_i = train_test_split(
        X, income_labels, test_size=0.2, random_state=42
    )
    print(f"  Bachelor model: train={len(y_train_b)}, test={len(y_test_b)}")
    print(f"  Income model: train={len(y_train_i)}, test={len(y_test_i)}")
    print()

    # --- Step 5: Train models ---
    print("Step 5: Training logistic regression models...")
    bachelor_model = train_and_evaluate(
        X_train_b, X_test_b, y_train_b, y_test_b,
        feature_names, "bachelor_or_higher", args.sample_size,
    )
    income_model = train_and_evaluate(
        X_train_i, X_test_i, y_train_i, y_test_i,
        feature_names, "above_median_income", args.sample_size,
    )

    print(f"  Bachelor model: AUC={bachelor_model['auc_roc']}, Brier={bachelor_model['brier_score']}, status={bachelor_model['status']}")
    print(f"  Income model:   AUC={income_model['auc_roc']}, Brier={income_model['brier_score']}, status={income_model['status']}")
    print()

    # --- Step 6: Build output artifact ---
    print("Step 6: Building artifact...")

    models = [bachelor_model, income_model]
    n_accepted = sum(1 for m in models if m["status"] == "accepted")
    n_rejected = sum(1 for m in models if m["status"] == "rejected")

    output = {
        "artifact_id": "nlsy97_calibrated_models_v4",
        "version": "4.0",
        "artifact_class": "calibrated_model" if n_accepted > 0 else "data_backed_baseline",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sample_size_scanned": args.sample_size,
        "sample_size_used": len(rows),
        "data_source": "nlsy97",
        "data_source_description": "National Longitudinal Survey of Youth 1997 (NLSY97)",
        "outcome_year": 2015,
        "outcome_age_range": "31-35",
        "feature_year": 2005,
        "feature_age_range": "25-29",
        "income_median_2015": income_median,
        "train_test_split": "80/20",
        "model_family": "logistic_regression_isotonic_calibrated",
        "models": models,
        "model_card": {
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
            "outcome_variables": [
                {"code": code, "label": info["label"], "domain": info["domain"]}
                for code, info in OUTCOME_VARIABLES.items()
            ],
            "binary_outcomes": [
                {
                    "name": "bachelor_or_higher",
                    "definition": "degree >= 4 (Bachelor's or higher)",
                    "source_variable": "U0009400",
                    "base_year": 2015,
                },
                {
                    "name": "above_median_income",
                    "definition": f"income > ${income_median:,.0f} (median of valid values)",
                    "source_variable": "U0008900",
                    "base_year": 2015,
                },
            ],
            "imputation_policy": {
                "method": "IterativeImputer (multivariate, max_iter=10, random_state=42)",
                "description": "Chained equations imputation using all observed features",
            },
            "limitations": [
                f"Sample of {args.sample_size:,} rows from full NLSY97 dataset ({len(rows):,} usable)",
                "Cohort born 1980-84 — transfer to other generations limited",
                "Logistic regression with interaction terms (degree×income, sex×grade)",
                "Isotonic calibration via CalibratedClassifierCV (cv=5)",
                "IterativeImputer for missing data (multivariate chained equations)",
                "No individual-level predictions committed",
                "No life_score or personal probability emitted",
                "2005 baseline → 2015 outcome only — no longitudinal trajectory",
            ],
        },
        "safety_confirmations": {
            "no_raw_data_committed": True,
            "no_individual_predictions": True,
            "no_individual_data": True,
            "no_personal_probabilities": True,
            "no_life_score": True,
            "aggregate_statistics_only": True,
        },
    }

    # --- Step 7: Write output ---
    output_path = ARTIFACTS_DIR / "nlsy97_calibrated_models_v4.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {output_path.relative_to(REPO_ROOT)}")
    print(f"Models: {len(models)} ({n_accepted} accepted, {n_rejected} rejected)")
    for m in models:
        auc_str = f"{m['auc_roc']:.3f}" if m['auc_roc'] is not None else "N/A"
        print(f"  {m['outcome']}: AUC={auc_str}, Brier={m['brier_score']:.4f}, status={m['status']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
