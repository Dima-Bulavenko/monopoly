"""Generate the WebSocket JSON Schema from Pydantic DTOs.

Prints deterministic JSON to stdout. Redirect to ws_schema.json at the repo
root via `make gen-types`.

Usage:
    uv run python scripts/generate_ws_schema.py
"""

from __future__ import annotations

import json
import sys

# Make sure the app package is importable when run from the backend/ directory.
sys.path.insert(0, ".")

from app.application.dto.websocket_dto import InboundAdapter, OutboundAdapter

inbound_schema = InboundAdapter.json_schema()
outbound_schema = OutboundAdapter.json_schema()

combined = {
    "inbound": inbound_schema,
    "outbound": outbound_schema,
}

print(json.dumps(combined, indent=2, sort_keys=True))
