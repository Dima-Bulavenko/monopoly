#!/usr/bin/env bash
# Regenerates the OpenAPI JSON schema in memory and compares it to the
# committed frontend/openapi.json. Exits non-zero if they differ, blocking
# the push.
#
# Run automatically as a pre-push git hook via pre-commit.
# Also callable manually: bash backend/scripts/check_openapi_schema.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
SCHEMA_FILE="$ROOT/frontend/openapi.json"

FRESH=$(cd "$ROOT/backend" && uv run python scripts/generate_openapi_schema.py 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo ""
  echo "ERROR: generate_openapi_schema.py failed:"
  echo "$FRESH"
  exit 1
fi

if [ ! -f "$SCHEMA_FILE" ]; then
  echo ""
  echo "ERROR: frontend/openapi.json does not exist."
  echo "Run 'make gen-openapi' to generate it, then commit the result."
  echo ""
  exit 1
fi

COMMITTED=$(cat "$SCHEMA_FILE")

if [ "$FRESH" != "$COMMITTED" ]; then
  echo ""
  echo "ERROR: frontend/openapi.json is out of date."
  echo "The OpenAPI schema does not match the current FastAPI app."
  echo ""
  echo "Run 'make gen-openapi' to regenerate, then commit the changed file:"
  echo "  frontend/openapi.json"
  echo ""
  exit 1
fi

echo "frontend/openapi.json is up to date."
