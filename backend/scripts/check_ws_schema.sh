#!/usr/bin/env bash
# Regenerates the WebSocket JSON Schema in memory and compares it to the
# committed ws_schema.json. Exits non-zero if they differ, blocking the push.
#
# Run automatically as a pre-push git hook via pre-commit.
# Also callable manually: bash backend/scripts/check_ws_schema.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
SCHEMA_FILE="$ROOT/ws_schema.json"

FRESH=$(cd "$ROOT/backend" && uv run python scripts/generate_ws_schema.py 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo ""
  echo "ERROR: generate_ws_schema.py failed:"
  echo "$FRESH"
  exit 1
fi

if [ ! -f "$SCHEMA_FILE" ]; then
  echo ""
  echo "ERROR: ws_schema.json does not exist."
  echo "Run 'make gen-types' to generate it, then commit the result."
  echo ""
  exit 1
fi

COMMITTED=$(cat "$SCHEMA_FILE")

if [ "$FRESH" != "$COMMITTED" ]; then
  echo ""
  echo "ERROR: ws_schema.json is out of date."
  echo "The WebSocket schema does not match the source Pydantic DTOs."
  echo ""
  echo "Run 'make gen-types' to regenerate, then commit all changed files:"
  echo "  ws_schema.json"
  echo "  frontend/src/types/ws.ts"
  echo ""
  exit 1
fi

echo "ws_schema.json is up to date."
