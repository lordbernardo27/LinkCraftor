// Scoring & normalization helpers — full implementation (no network).
// These utilities are pure and side-effect free, except for the configurable stopwords.

// ---------- Stopwords plumbing ----------
let _stopwords = new Set();

/**
 * Provide a stopwords set used by all overlap metrics.
 * You can call this once from app.js with your combined DEFAULT + custom list.
 * @param {Set<string>} set
 */
export function configureStopwords(set) {
  if (set && typeof set.has === "function") _stopwords = set;
}

function isStop(w) {
  return _stopwords.has(String(w || "").toLowerCase());
}

function nonStop(tokens) {
  return (tokens || []).filter(t => !isStop(t));
}

// ---------- Tokenization ----------
/**
 * @param {string} s
 * @returns {string[]} lowercased tokens (keeps internal hyphens & apostrophes)
 */
export function tokenize(s) {
  if (!s) return [];
  const rx = /[\p{L}\p{N}'-]+/gu;
  return (s.toLowerCase().match(rx) || []);
}

/**
 * Split URL host/path into slug tokens: host parts + path parts.
 * @param {string} u
 * @returns {string[]}
 */
export function tokenizeUrl(u) {
  try {
    const url = new URL(u);
    const host = url.hostname.replace(/^www\./i, "");
    const hostParts = host.split(/[.\-]+/).filter(Boolean);
    const pathParts = (url.pathname || "/").split(/[\/\-_]+/).filter(Boolean);
    return hostParts.concat(pathParts).map(s => s.toLowerCase());
  } catch {
    return [];
  }
}

// ---------- Overlap & context ----------
/**
 * Jaccard-like overlap between phrase tokens and (title|url) tokens.
 * Title gets 70% weight, URL slug 30%.
 * @param {string[]} phraseTokens
 * @param {string[]} titleTokens
 * @param {string[]} urlTokens
 * @returns {number} 0..1
 */
export function titleSlugOverlap(phraseTokens, titleTokens, urlTokens) {
  const A = new Set(nonStop(phraseTokens));
  const T = new Set(nonStop(titleTokens));
  const U = new Set(nonStop(urlTokens));

  if (!A.size || (!T.size && !U.size)) return 0;

  const interTitle = interCount(A, T);
  const denomTitle = Math.max(A.size, T.size || 1);
  const scoreTitle = interTitle / denomTitle;

  const interUrl = interCount(A, U);
  const denomUrl = Math.max(A.size, U.size || 1);
  const scoreUrl = interUrl / denomUrl;

  const score = 0.7 * scoreTitle + 0.3 * scoreUrl;
  return clamp01(score);
}

/**
 * Measures how well context (near heading/topic hints) matches title/summary.
 * @param {string[]} contextTokens
 * @param {string[]} titleTokens
 * @param {string[]} summaryTokens
 * @returns {number} 0..1
 */
export function contextMatch(contextTokens, titleTokens, summaryTokens) {
  const C = new Set(nonStop(contextTokens));
  if (!C.size) return 0;

  const T = new Set(nonStop(titleTokens));
  const S = new Set(nonStop(summaryTokens));

  const TS = union(T, S);
  if (!TS.size) return 0;

  // Slightly prioritize title hits over summary hits
  const hitsTitle = interCount(C, T);
  const hitsSummary = interCount(C, S);

  const weightedHits = hitsTitle * 1.0 + hitsSummary * 0.6;
  const denom = Math.max(C.size, TS.size);
  return clamp01(weightedHits / Math.max(1, denom));
}

// ---------- Freshness ----------
/**
 * @param {string=} publishedAt ISO
 * @param {"evergreen"|"scholarly"|"news"=} policy
 * @returns {number} 0..1
 */
export function freshnessScore(publishedAt, policy) {
  if (!publishedAt) {
    // For news, lack of date is a small penalty (but not zero);
    // for others it contributes nothing.
    return policy === "news" ? 0.1 : 0;
  }
  const t = Date.parse(publishedAt);
  if (Number.isNaN(t)) return 0;

  const days = (Date.now() - t) / (1000 * 60 * 60 * 24);

  if (policy === "evergreen") {
    // Specs/docs/books change slowly — freshness lightly matters
    return days <= 90 ? 0.2 : 0.05;
  }
  if (policy === "scholarly") {
    // Recent papers/grants matter a bit more
    if (days <= 180) return 0.7;
    if (days <= 365) return 0.4;
    return 0.15;
  }
  // policy === "news" (security advisories, data feeds, etc.)
  if (days <= 7) return 1.0;
  if (days <= 30) return 0.6;
  if (days <= 180) return 0.25;
  return 0.1;
}

// ---------- Final score ----------
/**
 * @param {{overlap:number, ctx:number, trust:number, fresh:number}} p
 * @returns {number}
 */
export function finalScore(p) {
  // 0.55 overlap + 0.20 context + 0.20 trust + 0.05 freshness
  return clamp01(
    0.55 * (p.overlap || 0) +
    0.20 * (p.ctx || 0) +
    0.20 * (p.trust || 0) +
    0.05 * (p.fresh || 0)
  );
}

// ---------- URL canonicalization & dedupe ----------
/**
 * Normalize URLs: https, drop tracking params, collapse www.
 * @param {string} u
 * @returns {string}
 */
export function canonicalUrl(u) {
  try {
    const url = new URL(u);
    url.protocol = "https:";
    // Drop common trackers
    const drop = ["utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid"];
    drop.forEach(k => url.searchParams.delete(k));
    url.hostname = url.hostname.replace(/^www\./i, "");
    // Remove trailing slash noise
    if (url.pathname !== "/" && url.pathname.endsWith("/")) {
      url.pathname = url.pathname.replace(/\/+$/,"");
    }
    return url.toString();
  } catch {
    return u || "";
  }
}

/**
 * Collapse duplicates by canonical URL; if URL missing, use a title hash.
 * If multiple items share URL, keep the one with better score signal (if present).
 * @param {import("./references.js").ReferenceItem[]} items
 * @returns {import("./references.js").ReferenceItem[]}
 */
export function dedupe(items) {
  const out = [];
  const seen = new Map(); // key -> index in out

  for (const it of items || []) {
    const key = (it.url ? canonicalUrl(it.url) : `__title__:${titleKey(it.title)}`).toLowerCase();
    if (!seen.has(key)) {
      out.push(it);
      seen.set(key, out.length - 1);
      continue;
    }
    // Prefer the one with more metadata completeness
    const idx = seen.get(key);
    const prev = out[idx];
    const prevScore = metaScore(prev);
    const nextScore = metaScore(it);
    if (nextScore > prevScore) out[idx] = it;
  }
  return out;
}

// ---------- Internals ----------
function interCount(A, B) {
  if (!A.size || !B.size) return 0;
  let c = 0;
  for (const x of A) if (B.has(x)) c++;
  return c;
}

function union(A, B) {
  const U = new Set(A);
  for (const x of B) U.add(x);
  return U;
}

function clamp01(x) {
  if (x < 0) return 0;
  if (x > 1) return 1;
  return x;
}

function titleKey(title) {
  return (title || "").toLowerCase().replace(/\s+/g, " ").trim().slice(0, 200);
}

function metaScore(it) {
  let s = 0;
  if (it.title) s += 1;
  if (it.url) s += 2;
  if (it.publishedAt) s += 0.5;
  if (it.summary) s += 0.25;
  return s + (typeof it.sourceTrust === "number" ? it.sourceTrust * 0.1 : 0);
}
