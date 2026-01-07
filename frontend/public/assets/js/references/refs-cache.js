// Tiny in-memory cache with TTLs (stubs + minimal helpers)

const store = new Map(); // key -> { items, expiresAt }

/**
 * @param {"evergreen"|"scholarly"|"news"} policy
 * @returns {number} ttl in ms
 */
export function ttlFor(policy) {
  switch (policy) {
    case "evergreen": return 7 * 24 * 60 * 60 * 1000;   // 7d
    case "scholarly": return 3 * 24 * 60 * 60 * 1000;   // 3d
    case "news":      return 24 * 60 * 60 * 1000;       // 24h
    default:          return 3 * 24 * 60 * 60 * 1000;
  }
}

/**
 * Deterministic cache key.
 * @param {string} phrase
 * @param {import("./references.js").DocContext} context
 * @param {{sources?:string[], sort?:string}=} opts
 */
export function makeKey(phrase, context = {}, opts = {}) {
  const srcs = (opts.sources || []).slice().sort().join(",");
  const sort = opts.sort || "relevance";
  const ctxBits = [
    context.docTitle || "",
    context.nearHeading || "",
    (context.topicHints || []).slice().sort().join(","),
    context.locale || "en"
  ].join("|");
  return `${phrase.toLowerCase().trim()}|${ctxBits}|${srcs}|${sort}`;
}

/**
 * @param {string} key
 * @returns {any[]|undefined}
 */
export function get(key) {
  const hit = store.get(key);
  if (!hit) return undefined;
  if (hit.expiresAt && hit.expiresAt < Date.now()) {
    store.delete(key);
    return undefined;
  }
  return hit.items;
}

/**
 * @param {string} key
 * @param {any[]} items
 * @param {number} ttlMs
 */
export function set(key, items, ttlMs) {
  store.set(key, { items, expiresAt: Date.now() + Math.max(0, ttlMs|0) });
}
