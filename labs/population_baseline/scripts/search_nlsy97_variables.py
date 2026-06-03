#!/usr/bin/env python3
"""
Phase 16C — NLSY97 Priority Variable Search.

Searches the extracted variable dictionary for priority constructs
across domains: career_education, employment, financial, cognitive, demographics.

Usage:
    python search_nlsy97_variables.py --dictionary labs/population_baseline/config/nlsy97_variable_dictionary_p16.yaml
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = REPO_ROOT / "labs" / "population_baseline" / "config"

# Priority search terms by domain
PRIORITY_SEARCHES = {
    "career_education": {
        "keywords": [
            "degree", "education", "school", "college", "university",
            "enrollment", "attended", "graduate", "diploma", "credential",
            "highest grade", "highest degree", "year of schooling",
        ],
        "priority": "high",
        "variables": [
            "highest degree", "highest grade", "enrollment", "education status",
        ],
    },
    "employment": {
        "keywords": [
            "employment", "employed", "unemployed", "work", "job",
            "occupation", "industry", "hours worked", "weeks worked",
            "labor force", "labor status", "job tenure",
        ],
        "priority": "high",
        "variables": [
            "employment status", "weeks worked", "hours worked",
            "occupation", "industry", "unemployment",
        ],
    },
    "financial": {
        "keywords": [
            "income", "earnings", "wage", "salary", "household income",
            "net worth", "assets", "debt", "poverty", "financial",
            "hardship", "bills", "money problems",
        ],
        "priority": "high",
        "variables": [
            "personal income", "household income", "wage", "earnings",
            "financial hardship", "difficulty paying bills",
        ],
    },
    "cognitive_non_cognitive": {
        "keywords": [
            "asvab", "afqt", "cognitive", "intelligence", "iq",
            "locus of control", "self-esteem", "self-regulation",
            "risk behavior", "behavior problems",
        ],
        "priority": "medium",
        "variables": [
            "ASVAB", "AFQT", "cognitive", "locus of control",
            "self-esteem", "risk behavior",
        ],
    },
    "demographics": {
        "keywords": [
            "age", "sex", "gender", "race", "ethnicity", "birth year",
            "birth date", "hispanic", "black", "white", "respondent id",
            "survey year", "round", "cohort",
        ],
        "priority": "high",
        "variables": [
            "respondent ID", "age", "sex", "race", "ethnicity",
            "birth year", "survey year", "round",
        ],
    },
}


def search_variables(dictionary: list[dict], search_config: dict) -> list[dict]:
    """Search dictionary for variables matching keywords."""
    matches = []

    for var in dictionary:
        var_code = var.get("variable_code", "").upper()
        var_label = var.get("variable_label", "").lower()

        # Check if any keyword matches the label
        for keyword in search_config["keywords"]:
            if keyword.lower() in var_label:
                # Determine confidence based on keyword specificity
                if keyword.lower() in var_label:
                    confidence = "high"
                else:
                    confidence = "medium"

                matches.append({
                    "variable_code": var_code,
                    "variable_label": var.get("variable_label", ""),
                    "matched_keyword": keyword,
                    "domain": "",
                    "priority": search_config["priority"],
                    "confidence": confidence,
                    "reason": f"Label contains '{keyword}'",
                    "source_file": var.get("source_file", ""),
                })
                break  # Only count each variable once per search

    return matches


def main():
    parser = argparse.ArgumentParser(description="NLSY97 priority variable search")
    parser.add_argument("--dictionary", type=str, required=True,
                        help="Path to variable dictionary YAML")
    parser.add_argument("--output", type=str, default=None,
                        help="Output path for priority variables YAML")
    args = parser.parse_args()

    dict_path = Path(args.dictionary)
    if not dict_path.is_absolute():
        dict_path = REPO_ROOT / dict_path

    print(f"NLSY97 Priority Variable Search")
    print(f"Dictionary: {dict_path}")
    print()

    if not dict_path.exists():
        print(f"ERROR: Dictionary not found: {dict_path}")
        return 1

    # Load dictionary
    with open(dict_path) as f:
        data = yaml.safe_load(f)

    variables = data.get("variables", [])
    print(f"Loaded {len(variables)} variables from dictionary")
    print()

    # Search for priority variables
    all_matches = []
    for domain, config in PRIORITY_SEARCHES.items():
        print(f"Searching {domain}...")
        matches = search_variables(variables, config)
        for m in matches:
            m["domain"] = domain
        all_matches.extend(matches)
        print(f"  Found {len(matches)} matches")

    print()
    print(f"Total priority variable matches: {len(all_matches)}")

    # Group by domain for summary
    by_domain = {}
    for m in all_matches:
        domain = m["domain"]
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(m)

    for domain, matches in by_domain.items():
        print(f"\n{domain}: {len(matches)} variables")
        for m in matches[:5]:  # Show first 5
            print(f"  {m['variable_code']}: {m['variable_label'][:60]}")
        if len(matches) > 5:
            print(f"  ... and {len(matches) - 5} more")

    # Write output
    output_path = Path(args.output) if args.output else CONFIG_DIR / "nlsy97_priority_variables_p16.yaml"
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path

    with open(output_path, 'w') as f:
        f.write("# NLSY97 Priority Variables\n")
        f.write(f"# Search date: 2026-06-03\n")
        f.write(f"# Total matches: {len(all_matches)}\n\n")
        f.write("priority_variables:\n")
        for m in all_matches:
            f.write(f"  - variable_code: \"{m['variable_code']}\"\n")
            f.write(f"    variable_label: \"{m['variable_label']}\"\n")
            f.write(f"    matched_keyword: \"{m['matched_keyword']}\"\n")
            f.write(f"    domain: \"{m['domain']}\"\n")
            f.write(f"    priority: \"{m['priority']}\"\n")
            f.write(f"    confidence: \"{m['confidence']}\"\n")
            f.write(f"    reason: \"{m['reason']}\"\n")
            f.write(f"    source_file: \"{m['source_file']}\"\n\n")

    print(f"\nPriority variables written to: {output_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
