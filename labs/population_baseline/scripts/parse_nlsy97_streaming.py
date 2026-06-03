#!/usr/bin/env python3
"""
Phase 15C/16D — NLSY97 Streaming Parser.

Streams CSV data from ZIP archive without full extraction.
Reads header and limited chunks for metadata inspection.
Does not load entire dataset into memory.

Usage:
    python parse_nlsy97_streaming.py --zip labs/population_baseline/data/raw/nlsy97/nlsy97_all_1997-2023.zip
    python parse_nlsy97_streaming.py --zip ... --columns CASEID R0000100 R0000200
    python parse_nlsy97_streaming.py --zip ... --sample-rows 5
    python parse_nlsy97_streaming.py --zip ... --verify-columns path/to/candidate_variables.yaml
"""

import argparse
import csv
import io
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = REPO_ROOT / "labs" / "population_baseline" / "data" / "processed"


def stream_csv_header(zip_path: Path) -> tuple[list[str], int]:
    """Stream CSV header from ZIP without loading full file."""
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Find the CSV file
        csv_files = [f for f in zf.namelist() if f.lower().endswith('.csv')]
        if not csv_files:
            return [], 0

        csv_name = csv_files[0]
        with zf.open(csv_name) as f:
            # Read just the header line
            header_line = f.readline().decode('utf-8', errors='replace')
            reader = csv.reader(io.StringIO(header_line))
            headers = next(reader, [])
            return headers, len(headers)


def stream_csv_sample(zip_path: Path, n_rows: int = 5) -> list[list[str]]:
    """Stream sample rows from CSV in ZIP."""
    rows = []
    with zipfile.ZipFile(zip_path, 'r') as zf:
        csv_files = [f for f in zf.namelist() if f.lower().endswith('.csv')]
        if not csv_files:
            return rows

        csv_name = csv_files[0]
        with zf.open(csv_name) as f:
            reader = csv.reader(io.TextIOWrapper(f, encoding='utf-8', errors='replace'))
            header = next(reader, None)  # Skip header
            for i, row in enumerate(reader):
                if i >= n_rows:
                    break
                rows.append(row)
    return rows


def stream_csv_count_rows(zip_path: Path) -> int:
    """Count total rows in CSV by streaming."""
    count = 0
    with zipfile.ZipFile(zip_path, 'r') as zf:
        csv_files = [f for f in zf.namelist() if f.lower().endswith('.csv')]
        if not csv_files:
            return 0

        csv_name = csv_files[0]
        with zf.open(csv_name) as f:
            reader = csv.reader(io.TextIOWrapper(f, encoding='utf-8', errors='replace'))
            next(reader, None)  # Skip header
            for _ in reader:
                count += 1
    return count


def compute_missingness(zip_path: Path, columns: list[str], sample_size: int = 1000) -> dict:
    """Compute missingness rate for selected columns using streaming."""
    missing_counts = {col: 0 for col in columns}
    total_rows = 0

    with zipfile.ZipFile(zip_path, 'r') as zf:
        csv_files = [f for f in zf.namelist() if f.lower().endswith('.csv')]
        if not csv_files:
            return {}

        csv_name = csv_files[0]
        with zf.open(csv_name) as f:
            reader = csv.reader(io.TextIOWrapper(f, encoding='utf-8', errors='replace'))
            header = next(reader, None)
            if not header:
                return {}

            # Map column names to indices
            col_indices = {}
            for col in columns:
                if col in header:
                    col_indices[col] = header.index(col)

            for i, row in enumerate(reader):
                if i >= sample_size:
                    break
                total_rows += 1
                for col, idx in col_indices.items():
                    if idx < len(row) and (not row[idx] or row[idx].strip() == ''):
                        missing_counts[col] += 1

    # Compute rates
    result = {}
    for col in columns:
        if col in col_indices:
            result[col] = {
                "missing_count": missing_counts[col],
                "total_sampled": total_rows,
                "missingness_rate": round(missing_counts[col] / total_rows * 100, 2) if total_rows > 0 else 0,
            }
    return result


def verify_columns_in_header(zip_path: Path, candidate_vars: list[dict]) -> dict:
    """Verify candidate variable codes exist in CSV header."""
    headers, _ = stream_csv_header(zip_path)
    if not headers:
        return {"error": "No CSV file found in archive"}

    header_set = set(headers)

    results = {
        "total_candidates": len(candidate_vars),
        "verified": [],
        "not_found": [],
    }

    for var in candidate_vars:
        code = var.get("variable_code", "").upper()
        if code in header_set:
            results["verified"].append({
                "variable_code": code,
                "variable_label": var.get("variable_label", ""),
                "domain": var.get("domain", ""),
                "status": "data_confirmed",
            })
        else:
            results["not_found"].append({
                "variable_code": code,
                "variable_label": var.get("variable_label", ""),
                "domain": var.get("domain", ""),
                "status": "not_in_header",
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="NLSY97 streaming parser")
    parser.add_argument("--zip", type=str, required=True,
                        help="Path to NLSY97 ZIP archive")
    parser.add_argument("--columns", nargs="*", default=None,
                        help="Column names to inspect")
    parser.add_argument("--sample-rows", type=int, default=0,
                        help="Number of sample rows to print (default: 0)")
    parser.add_argument("--count-rows", action="store_true",
                        help="Count total rows (may take time for large files)")
    parser.add_argument("--missingness", action="store_true",
                        help="Compute missingness for selected columns")
    parser.add_argument("--verify-columns", type=str, default=None,
                        help="Path to YAML file with candidate variables to verify")
    parser.add_argument("--output", type=str, default=None,
                        help="Output path for markdown report")
    parser.add_argument("--output-verification", type=str, default=None,
                        help="Output path for verification JSON")
    args = parser.parse_args()

    zip_path = Path(args.zip)
    if not zip_path.is_absolute():
        zip_path = REPO_ROOT / zip_path

    print(f"NLSY97 Streaming Parser")
    print(f"Archive: {zip_path}")
    print()

    # Get header
    headers, col_count = stream_csv_header(zip_path)
    if not headers:
        print("ERROR: No CSV file found in archive")
        return 1

    print(f"Column count: {col_count}")
    print(f"First 50 column names:")
    for i, h in enumerate(headers[:50]):
        print(f"  {i+1}. {h}")
    if col_count > 50:
        print(f"  ... and {col_count - 50} more columns")
    print()

    # Verify columns if requested
    if args.verify_columns:
        import yaml
        verify_path = Path(args.verify_columns)
        if not verify_path.is_absolute():
            verify_path = REPO_ROOT / verify_path

        if verify_path.exists():
            print(f"Verifying columns from: {verify_path.relative_to(REPO_ROOT)}")
            with open(verify_path) as f:
                verify_data = yaml.safe_load(f)

            candidate_vars = verify_data.get("priority_variables", [])
            print(f"  Candidate variables: {len(candidate_vars)}")

            verification = verify_columns_in_header(zip_path, candidate_vars)
            print(f"  Verified: {len(verification.get('verified', []))}")
            print(f"  Not found: {len(verification.get('not_found', []))}")

            # Write verification output
            output_ver_path = Path(args.output_verification) if args.output_verification else ARTIFACTS_DIR / "nlsy97_column_verification_p16.json"
            if not output_ver_path.is_absolute():
                output_ver_path = REPO_ROOT / output_ver_path

            import json
            with open(output_ver_path, 'w') as f:
                json.dump(verification, f, indent=2)

            print(f"  Verification written to: {output_ver_path.relative_to(REPO_ROOT)}")
            print()

    # Count rows if requested
    if args.count_rows:
        print("Counting rows (this may take a moment)...")
        row_count = stream_csv_count_rows(zip_path)
        print(f"Total rows: {row_count:,}")
        print()

    # Print sample rows if requested
    if args.sample_rows > 0:
        print(f"Sample rows ({args.sample_rows}):")
        sample = stream_csv_sample(zip_path, args.sample_rows)
        for i, row in enumerate(sample):
            print(f"  Row {i+1}: {row[:10]}{'...' if len(row) > 10 else ''}")
        print()

    # Compute missingness if requested
    if args.missingness and args.columns:
        print(f"Missingness for selected columns (sample size: 1000):")
        missingness = compute_missingness(zip_path, args.columns)
        for col, stats in missingness.items():
            print(f"  {col}: {stats['missingness_rate']}% missing "
                  f"({stats['missing_count']}/{stats['total_sampled']})")
        print()

    # Generate markdown report if requested
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = REPO_ROOT / output_path

        with open(output_path, 'w') as f:
            f.write("# NLSY97 Streaming Parser Report\n\n")
            f.write(f"**Archive:** `{zip_path.relative_to(REPO_ROOT)}`\n\n")
            f.write("## Header Info\n\n")
            f.write(f"- Column count: {col_count}\n")
            f.write(f"- First 50 columns: {headers[:50]}\n\n")

            if args.count_rows:
                f.write("## Row Count\n\n")
                f.write(f"- Total rows: {row_count:,}\n\n")

            if args.missingness and args.columns:
                f.write("## Missingness\n\n")
                f.write("| Column | Missing Count | Total Sampled | Missingness Rate |\n")
                f.write("|--------|---------------|---------------|------------------|\n")
                for col, stats in missingness.items():
                    f.write(f"| {col} | {stats['missing_count']} | {stats['total_sampled']} | {stats['missingness_rate']}% |\n")
                f.write("\n")

        print(f"Report written to: {output_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
