"""Generate the OpenAPI JSON schema from the FastAPI app.

Prints deterministic JSON to stdout. Redirect to frontend/openapi.json via
`make gen-openapi`.

Usage:
    uv run python scripts/generate_openapi_schema.py
"""

from __future__ import annotations

import json
import sys

# Make sure the app package is importable when run from the backend/ directory.
sys.path.insert(0, ".")

from app.main import app

schema = app.openapi()

print(json.dumps(schema, indent=2, sort_keys=True))
