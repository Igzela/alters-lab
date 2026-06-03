#!/usr/bin/env python3
"""Export the FastAPI OpenAPI schema to JSON for frontend type generation."""

import json
import sys
from pathlib import Path

# Add the src directory to the path so we can import the app
_SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(_SRC_DIR))

from alters_lab.main import app  # noqa: E402

# apps/api/scripts/ → 4 parents up = project root
_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_OUTPUT = _ROOT / "apps" / "web" / "src" / "api-schema.json"


def main() -> None:
    schema = app.openapi()
    _OUTPUT.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"OpenAPI schema written to {_OUTPUT}")


if __name__ == "__main__":
    main()
