// backend/server/engine_js/rb2/node_dom_shim.mjs
// Provides DOMParser in Node so rulebook_v2_core.js can remain unchanged.

import { DOMParser } from "linkedom";

if (typeof globalThis.DOMParser === "undefined") {
  globalThis.DOMParser = DOMParser;
}
