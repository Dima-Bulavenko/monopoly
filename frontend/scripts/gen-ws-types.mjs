/**
 * Generates frontend/src/types/ws.ts from ws_schema.json.
 *
 * Run via: make gen-types
 * Requires: json-schema-to-zod (devDependency)
 */

import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { jsonSchemaToZod } from "json-schema-to-zod";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, "../..");

const combined = JSON.parse(
  readFileSync(resolve(root, "ws_schema.json"), "utf-8"),
);

/**
 * Recursively resolve all local $ref (#/$defs/...) occurrences in a JSON
 * Schema document.  Pydantic emits only local refs so this is sufficient.
 * The domain models have no circular references, so no cycle detection is
 * needed.
 */
function resolveRefs(node, defs) {
  if (typeof node !== "object" || node === null) return node;
  if (Array.isArray(node)) return node.map((item) => resolveRefs(item, defs));

  if ("$ref" in node && typeof node.$ref === "string") {
    const ref = node.$ref;
    if (ref.startsWith("#/$defs/")) {
      const defName = ref.slice("#/$defs/".length);
      if (defs[defName]) return resolveRefs(defs[defName], defs);
    }
    return node;
  }

  const result = {};
  for (const [key, value] of Object.entries(node)) {
    if (key === "$defs") continue; // strip after inlining
    result[key] = resolveRefs(value, defs);
  }
  return result;
}

function prepareSchema(schema) {
  return resolveRefs(schema, schema.$defs ?? {});
}

const inboundZod = jsonSchemaToZod(prepareSchema(combined.inbound));
const outboundZod = jsonSchemaToZod(prepareSchema(combined.outbound));

const output = `\
// AUTO-GENERATED — do not edit manually.
// Source of truth: backend/app/application/dto/websocket_dto.py
// Regenerate with: make gen-types

import { z } from "zod";

// ---------------------------------------------------------------------------
// Inbound messages (client → server)
// ---------------------------------------------------------------------------

export const InboundMessageSchema = ${inboundZod};

export type InboundMessage = z.infer<typeof InboundMessageSchema>;

// ---------------------------------------------------------------------------
// Outbound messages (server → client)
// ---------------------------------------------------------------------------

export const OutboundMessageSchema = ${outboundZod};

export type OutboundMessage = z.infer<typeof OutboundMessageSchema>;
`;

const outPath = resolve(__dirname, "../src/types/ws.ts");
mkdirSync(dirname(outPath), { recursive: true });
writeFileSync(outPath, output, "utf-8");
console.log("Generated frontend/src/types/ws.ts");
