#!/usr/bin/env python3
"""
Phase 13 — Safe Public Resource Acquisition Script.

Creates raw data directories, checks public page availability for NLSY97 and MIDUS,
and writes an acquisition log. Does NOT download any login-protected data.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_BASE = REPO_ROOT / "labs" / "population_baseline" / "data" / "raw"
ARTIFACTS_DIR = REPO_ROOT / "labs" / "population_baseline" / "artifacts"

PUBLIC_URLS = {
    "nlsy97_investigator": "https://www.nlsinfo.org/investigator/",
    "nlsy97_register": "https://www.nlsinfo.org/investigator/pages/register",
    "midus_home": "https://midus.wisc.edu",
    "midus_i": "https://www.icpsr.umich.edu/web/ICPSR/studies/02760",
    "midus_ii": "https://www.icpsr.umich.edu/web/ICPSR/studies/04652",
    "midus_iii": "https://www.icpsr.umich.edu/web/ICPSR/studies/36346",
    "midus_series": "https://www.icpsr.umich.edu/web/ICPSR/series/203",
}

DIRS_TO_CREATE = [
    RAW_BASE / "nlsy97",
    RAW_BASE / "nlsy97" / "codebook",
    RAW_BASE / "midus",
    RAW_BASE / "midus" / "midus1",
    RAW_BASE / "midus" / "midus1" / "codebook",
    RAW_BASE / "midus" / "midus2",
    RAW_BASE / "midus" / "midus2" / "codebook",
    RAW_BASE / "midus" / "midus3",
    RAW_BASE / "midus" / "midus3" / "codebook",
    RAW_BASE / "midus" / "midus_refresher",
]


def create_directories():
    """Create raw data directories with .gitkeep files."""
    created = []
    for d in DIRS_TO_CREATE:
        d.mkdir(parents=True, exist_ok=True)
        gitkeep = d / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
            created.append(str(d.relative_to(REPO_ROOT)))
    return created


def check_url(url: str, timeout: int = 10) -> dict:
    """Check if a URL is publicly accessible. Returns status dict."""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={
            "User-Agent": "alters-lab-population-baseline/1.0"
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {
                "url": url,
                "status_code": resp.status,
                "accessible": True,
                "content_type": resp.headers.get("Content-Type", ""),
            }
    except urllib.error.HTTPError as e:
        return {
            "url": url,
            "status_code": e.code,
            "accessible": e.code < 400,
            "error": str(e),
        }
    except Exception as e:
        return {
            "url": url,
            "status_code": None,
            "accessible": False,
            "error": str(e),
        }


def main():
    """Run acquisition checks."""
    log = {
        "phase": "P13",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "directories_created": [],
        "url_checks": {},
        "user_action_required": True,
        "notes": [
            "No raw data downloaded by this script.",
            "Both NLSY97 and MIDUS require authenticated accounts.",
            "See P13_USER_DOWNLOAD_INSTRUCTIONS.md for manual steps.",
        ],
    }

    # Create directories
    created = create_directories()
    log["directories_created"] = created
    print(f"Created {len(created)} directories with .gitkeep files.")

    # Check public page availability
    print("\nChecking public page availability...")
    for name, url in PUBLIC_URLS.items():
        result = check_url(url)
        log["url_checks"][name] = result
        status = "OK" if result["accessible"] else f"BLOCKED ({result.get('error', result.get('status_code', 'unknown'))})"
        print(f"  {name}: {status}")

    # Ensure artifacts dir exists for log
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # Write acquisition log
    log_path = ARTIFACTS_DIR / "acquisition_log_p13.json"
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
    print(f"\nAcquisition log written to {log_path.relative_to(REPO_ROOT)}")

    # Summary
    accessible_count = sum(1 for v in log["url_checks"].values() if v["accessible"])
    total_count = len(log["url_checks"])
    print(f"\nSummary: {accessible_count}/{total_count} public pages accessible.")
    print("User action required: download data manually via authenticated accounts.")
    print("See labs/population_baseline/P13_USER_DOWNLOAD_INSTRUCTIONS.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
