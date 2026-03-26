// backend/server/engine_js/rb2/run_rb2.mjs
// Runs the exact RB2 engine (rulebook_v2_core.js) under Node using linkedom (DOMParser shim).
// Input: JSON on stdin
// Output: JSON on stdout

import { parseHTML } from "linkedom";
import { fileURLToPath } from "url";
import path from "path";

// ---- DOM + browser globals shim (minimal; does not change RB2) ----
const { window } = parseHTML("<html><body></body></html>");
globalThis.window = window;
globalThis.document = window.document;
globalThis.DOMParser = window.DOMParser;

// RB2 uses URL() and Math/Set/Map etc (already in Node). Ensure URL exists:
globalThis.URL = globalThis.URL || window.URL;

// ---- Load input from stdin ----
async function readStdin() {
  return await new Promise((resolve, reject) => {
    let buf = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (c) => (buf += c));
    process.stdin.on("end", () => resolve(buf));
    process.stdin.on("error", reject);
  });
}

function safeJsonParse(s) {
  try {
    return JSON.parse(s);
  } catch {
    return null;
  }
}

// ---- Import RB2 (exact file) ----
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rb2Path = path.join(__dirname, "rulebook_v2_core.js");

// Convert path -> file:// URL (Windows-safe)
function pathToFileUrl(p) {
  let x = path.resolve(p).replace(/\\/g, "/");
  if (!x.startsWith("/")) x = "/" + x;
  return new URL("file://" + x);
}

// Dynamic import (ESM). This imports your exact file with exports.
const RB2 = await import(pathToFileUrl(rb2Path).href);

function fail(msg, extra = {}) {
  process.stdout.write(JSON.stringify({ ok: false, error: msg, ...extra }));
  process.exit(0);
}

// ---- Main ----
const raw = await readStdin();
const input = safeJsonParse(raw);
if (!input) fail("Invalid JSON on stdin.");

if (typeof RB2.runRulebookV2 !== "function") {
  fail("runRulebookV2 export missing from rulebook_v2_core.js");
}

// ✅ Phase 3 plumbing: prefer extracted rb2Doc contract if present
const rb2Doc =
  input && input.rb2Doc && typeof input.rb2Doc === "object"
    ? input.rb2Doc
    : null;

// Prefer joinedText when present (paragraph-separated via \n\n)
const preferredText =
  rb2Doc && typeof rb2Doc.joinedText === "string" ? rb2Doc.joinedText : "";

// Keep html as-is (RB2 may still rely on html; we are not changing that here)
const preferredHtml = typeof input.html === "string" ? input.html : "";

// ---- Build opts for RB2 ----
const opts = {
  html: preferredHtml || "",
  text:
    preferredText ||
    (typeof input.text === "string" ? input.text : "") ||
    "",
  targets: Array.isArray(input.targets) ? input.targets : [],
  include: input.include && typeof input.include === "object" ? input.include : {},
  block: Array.isArray(input.block) ? input.block : [],
  synonyms: input.synonyms && typeof input.synonyms === "object" ? input.synonyms : {},

  // ✅ Step 5.1: entity map pass-through (plumbing only)
  entityMap: input.entityMap && typeof input.entityMap === "object" ? input.entityMap : {},

  config: input.config && typeof input.config === "object" ? input.config : {},
  rb2Doc: rb2Doc || undefined,
};

try {
  const out = RB2.runRulebookV2(opts);

  // ------------------------------------------------------------------
  // Bucket fallback only:
  // - If RB2 core already set x.bucket, keep it.
  // - Otherwise apply floors to assign bucket.
  // ------------------------------------------------------------------
  const FLOORS =
    input && input.floors && typeof input.floors === "object"
      ? input.floors
      : opts.config && typeof opts.config === "object" && opts.config.floors
        ? opts.config.floors
        : { STRONG: 0.75, OPTIONAL: 0.65 };

  const strongFloor = Number(FLOORS.STRONG ?? FLOORS.strong ?? 0.7);
  const optionalFloor = Number(FLOORS.OPTIONAL ?? FLOORS.optional ?? 0.5);

  function ensureBucket(arr, forcedBucket) {
    if (!Array.isArray(arr)) return [];
    return arr.map((x) => {
      const score = typeof x?.score === "number" ? x.score : 1.0;

      const existing =
        (x && typeof x.bucket === "string") ? String(x.bucket || "").toLowerCase() : "";

      // ✅ Treat "hidden" like "unset" so floors can promote it
      const bucket =
        (existing && existing !== "hidden")
          ? existing
          : (forcedBucket
              ? forcedBucket
              : (score >= strongFloor
                  ? "strong"
                  : (score >= optionalFloor ? "optional" : "hidden")
                )
            );

      return { ...x, bucket };
    });
  }

  if (out && typeof out === "object") {
    // ✅ CRITICAL FIX:
    // RB2 may dump everything inside out.hidden even when score is high.
    // Frontend highlights based on arrays (recommended/optional), not just bucket.
    // So we flatten and repartition by bucket.
    const all = []
      .concat(Array.isArray(out.recommended) ? out.recommended : [])
      .concat(Array.isArray(out.optional) ? out.optional : [])
      .concat(Array.isArray(out.hidden) ? out.hidden : []);

    const allWithBuckets = ensureBucket(all, null);

    out.recommended = allWithBuckets.filter(
      (x) => (x?.bucket || "").toLowerCase() === "strong"
    );
    out.optional = allWithBuckets.filter(
      (x) => (x?.bucket || "").toLowerCase() === "optional"
    );
    out.hidden = allWithBuckets.filter(
      (x) => !x?.bucket || (x.bucket || "").toLowerCase() === "hidden"
    );

    out.meta = {
      ...(out.meta || {}),
      floorsUsed: { STRONG: strongFloor, OPTIONAL: optionalFloor },
      rebucketed: {
        in_all: all.length,
        strong: out.recommended.length,
        optional: out.optional.length,
        hidden: out.hidden.length,
      },

      // ✅ debug: prove rb2Doc was received and used for text
      rb2Extract: rb2Doc
        ? {
            version: rb2Doc.version || null,
            paragraphs: Array.isArray(rb2Doc.paragraphs) ? rb2Doc.paragraphs.length : null,
            usedJoinedText: Boolean(preferredText && preferredText.length),
          }
        : { version: null, paragraphs: null, usedJoinedText: false },
    };
  }

  process.stdout.write(JSON.stringify({ ok: true, out }));
} catch (e) {
  fail("RB2 execution failed.", { detail: String(e?.message || e) });
}
