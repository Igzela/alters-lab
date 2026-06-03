#!/usr/bin/env python3
"""
Phase 16B — NLSY97 Variable Dictionary Extractor.

Extracts variable dictionary from files inside nlsy97_all_1997-2023.zip.
Searches for SAS scripts, R scripts, and metadata files that map
numeric variable codes to labels.

Usage:
    python extract_nlsy97_variable_dictionary.py --zip labs/population_baseline/data/raw/nlsy97/nlsy97_all_1997-2023.zip
"""

import argparse
import re
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = REPO_ROOT / "labs" / "population_baseline" / "config"
ARTIFACTS_DIR = REPO_ROOT / "labs" / "population_baseline" / "artifacts"


def extract_sas_variable_labels(zf: zipfile.ZipFile, sas_filename: str) -> dict:
    """Extract variable labels from SAS file."""
    labels = {}
    try:
        with zf.open(sas_filename) as f:
            content = f.read().decode('utf-8', errors='replace')

            # Look for LABEL statements
            # Pattern: label VARIABLE = "Label text";
            label_pattern = re.compile(
                r'label\s+(\w+)\s*=\s*["\']([^"\']+)["\']',
                re.IGNORECASE
            )
            for match in label_pattern.finditer(content):
                var_name = match.group(1).upper()
                label = match.group(2).strip()
                labels[var_name] = {
                    "variable_code": var_name,
                    "variable_label": label,
                    "source_file": sas_filename,
                }

            # Also look for variable name assignments in format statements
            # Pattern: value $VARNAME. or value VARNAME.
            value_pattern = re.compile(
                r'value\s+\$?(\w+)\.',
                re.IGNORECASE
            )
            for match in value_pattern.finditer(content):
                var_name = match.group(1).upper()
                if var_name not in labels:
                    labels[var_name] = {
                        "variable_code": var_name,
                        "variable_label": "",
                        "source_file": sas_filename,
                    }

    except Exception as e:
        print(f"  Warning: Could not parse {sas_filename}: {e}")

    return labels


def extract_r_variable_labels(zf: zipfile.ZipFile, r_filename: str) -> dict:
    """Extract variable labels from R file."""
    labels = {}
    try:
        with zf.open(r_filename) as f:
            content = f.read().decode('utf-8', errors='replace')

            # Look for variable label assignments
            # Pattern: attr(VARNAME, "label") = "Label text"
            label_pattern = re.compile(
                r'attr\((\w+),\s*["\']label["\']\)\s*=\s*["\']([^"\']+)["\']',
                re.IGNORECASE
            )
            for match in label_pattern.finditer(content):
                var_name = match.group(1).upper()
                label = match.group(2).strip()
                labels[var_name] = {
                    "variable_code": var_name,
                    "variable_label": label,
                    "source_file": r_filename,
                }

            # Also look for variable.label assignments
            # Pattern: variable.label$VARNAME = "Label text"
            var_label_pattern = re.compile(
                r'variable\.label\[\s*["\'](\w+)["\']\s*\]\s*=\s*["\']([^"\']+)["\']',
                re.IGNORECASE
            )
            for match in var_label_pattern.finditer(content):
                var_name = match.group(1).upper()
                label = match.group(2).strip()
                labels[var_name] = {
                    "variable_code": var_name,
                    "variable_label": label,
                    "source_file": r_filename,
                }

    except Exception as e:
        print(f"  Warning: Could not parse {r_filename}: {e}")

    return labels


def extract_cdb_metadata(zf: zipfile.ZipFile, cdb_filename: str) -> dict:
    """Extract metadata from CDB file (if human-readable)."""
    labels = {}
    try:
        with zf.open(cdb_filename) as f:
            # Read first 10KB to check if it's text
            sample = f.read(10240)

            # Try to decode as text
            try:
                content = sample.decode('utf-8', errors='replace')

                # Look for variable label patterns
                # This is heuristic - CDB format may vary
                label_pattern = re.compile(
                    r'(\w{2,10})\s+[:=]\s*["\']?([^"\'\n]{5,100})["\']?',
                    re.IGNORECASE
                )
                for match in label_pattern.finditer(content):
                    var_name = match.group(1).upper()
                    label = match.group(2).strip()
                    if len(var_name) <= 10 and len(label) > 5:
                        labels[var_name] = {
                            "variable_code": var_name,
                            "variable_label": label,
                            "source_file": cdb_filename,
                        }
            except:
                pass

    except Exception as e:
        print(f"  Warning: Could not parse {cdb_filename}: {e}")

    return labels


def list_metadata_files(zf: zipfile.ZipFile) -> list[dict]:
    """List candidate metadata files in ZIP."""
    metadata_files = []

    for info in zf.infolist():
        if info.is_dir():
            continue

        filename = info.filename.lower()
        name = Path(info.filename).name

        # Identify metadata files
        is_metadata = False
        file_type = "unknown"

        if filename.endswith('.sas'):
            is_metadata = True
            file_type = "sas_script"
        elif filename.endswith('.r'):
            is_metadata = True
            file_type = "r_script"
        elif filename.endswith('.cdb'):
            is_metadata = True
            file_type = "cdb_metadata"
        elif filename.endswith('.sdf'):
            is_metadata = True
            file_type = "sdf_data"
        elif 'codebook' in filename or 'label' in filename or 'variable' in filename:
            is_metadata = True
            file_type = "codebook"
        elif filename.endswith('.csv') and info.file_size < 1_000_000:
            # Small CSV might be variable list
            is_metadata = True
            file_type = "small_csv"

        if is_metadata:
            metadata_files.append({
                "filename": info.filename,
                "name": name,
                "type": file_type,
                "size": info.file_size,
                "compressed_size": info.compress_size,
            })

    return metadata_files


def main():
    parser = argparse.ArgumentParser(description="NLSY97 variable dictionary extractor")
    parser.add_argument("--zip", type=str, required=True,
                        help="Path to NLSY97 ZIP archive")
    parser.add_argument("--output", type=str, default=None,
                        help="Output path for YAML dictionary")
    parser.add_argument("--artifact", type=str, default=None,
                        help="Output path for full JSON artifact")
    args = parser.parse_args()

    zip_path = Path(args.zip)
    if not zip_path.is_absolute():
        zip_path = REPO_ROOT / zip_path

    print(f"NLSY97 Variable Dictionary Extractor")
    print(f"Archive: {zip_path}")
    print()

    if not zip_path.exists():
        print(f"ERROR: File not found: {zip_path}")
        return 1

    with zipfile.ZipFile(zip_path, 'r') as zf:
        # List metadata files
        metadata_files = list_metadata_files(zf)
        print(f"Found {len(metadata_files)} candidate metadata files:")
        for f in metadata_files:
            print(f"  {f['name']} ({f['type']}, {f['size']:,} bytes)")
        print()

        # Extract labels from each metadata file
        all_labels = {}
        for f in metadata_files:
            print(f"Parsing {f['name']}...")
            if f['type'] == 'sas_script':
                labels = extract_sas_variable_labels(zf, f['filename'])
            elif f['type'] == 'r_script':
                labels = extract_r_variable_labels(zf, f['filename'])
            elif f['type'] == 'cdb_metadata':
                labels = extract_cdb_metadata(zf, f['filename'])
            else:
                labels = {}

            if labels:
                print(f"  Extracted {len(labels)} variable labels")
                all_labels.update(labels)
            else:
                print(f"  No labels extracted")

        print()
        print(f"Total unique variables with labels: {len(all_labels)}")

        # Write output
        output_path = Path(args.output) if args.output else CONFIG_DIR / "nlsy97_variable_dictionary_p16.yaml"
        if not output_path.is_absolute():
            output_path = REPO_ROOT / output_path

        # Convert to list for YAML
        variables_list = sorted(all_labels.values(), key=lambda x: x['variable_code'])

        # Write YAML (safe for commit if small enough)
        with open(output_path, 'w') as f:
            f.write("# NLSY97 Variable Dictionary\n")
            f.write(f"# Extracted from: {zip_path.name}\n")
            f.write(f"# Total variables: {len(variables_list)}\n\n")
            f.write("variables:\n")
            for var in variables_list:
                f.write(f"  - variable_code: \"{var['variable_code']}\"\n")
                f.write(f"    variable_label: \"{var['variable_label']}\"\n")
                f.write(f"    source_file: \"{var['source_file']}\"\n\n")

        print(f"Dictionary written to: {output_path.relative_to(REPO_ROOT)}")

        # Write full JSON artifact
        artifact_path = Path(args.artifact) if args.artifact else ARTIFACTS_DIR / "nlsy97_variable_dictionary_full_p16.json"
        if not artifact_path.is_absolute():
            artifact_path = REPO_ROOT / artifact_path

        import json
        with open(artifact_path, 'w') as f:
            json.dump({
                "archive": str(zip_path.name),
                "total_variables": len(variables_list),
                "metadata_files_scanned": len(metadata_files),
                "variables": variables_list,
            }, f, indent=2)

        print(f"Full artifact written to: {artifact_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
