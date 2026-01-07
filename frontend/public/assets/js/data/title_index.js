// public/assets/js/data/titleIndex.js
// Title catalog + URL pairing (≥85% rule), self-contained (no external imports).

/* ----------------------------- Normalizers -------------------------------- */

function normalizeWord(w) {
  return (w || "")
    .toLowerCase()
    .trim()
    .replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, "");
}

export function normalizePhrase(s) {
  return (s || "").toLowerCase().trim().replace(/\s+/g, " ");
}

/* ------------------------- Tokenization utilities ------------------------- */

function tokenizeTitleForMatch(title, options) {
  const { includeNums = true, minLen = 1, stopwords = new Set() } = options || {};
  const words = (title || "")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]+/gu, " ")
    .split(/\s+/)
    .map(normalizeWord)
    .filter(Boolean);

  const filtered = words.filter((w) => {
    if (!includeNums && /^\d+([\.,]\d+)?$/.test(w)) return false;
    if (stopwords.has(w)) return false;
    if (w.length < minLen) return false;
    return true;
  });
  return filtered;
}

function tokenizeUrl(url) {
  try {
    const u = new URL(url);
    const host = (u.hostname || "").replace(/^www\./, "");
    const hostParts = host.split(/[.\-]+/).filter(Boolean);
    const path = (u.pathname || "").replace(/\/+/g, "/");
    const pathParts = path.split(/[\/\-_]+/).filter(Boolean);
    return hostParts.concat(pathParts).map((t) => normalizeWord(t)).filter(Boolean);
  } catch {
    return [];
  }
}

/* ---------------------------- Coverage functions -------------------------- */

export function titleCoverageInUrl(title, url, options) {
  const tTokens = tokenizeTitleForMatch(title, options);
  if (tTokens.length === 0) return 0;
  const uTokens = tokenizeUrl(url);
  if (uTokens.length === 0) return 0;

  let hit = 0;
  for (const w of tTokens) {
    const ok = uTokens.some((tok) => tok.includes(w) || w.includes(tok));
    if (ok) hit++;
  }
  return hit / tTokens.length;
}

export function phraseCoverageInTitle(phrase, title, options) {
  const pTokens = tokenizeTitleForMatch(phrase, options);
  const tTokens = tokenizeTitleForMatch(title, options);
  if (pTokens.length === 0 || tTokens.length === 0) return 0;

  let hit = 0;
  for (const w of pTokens) {
    const ok = tTokens.some((tok) => tok.includes(w) || w.includes(tok));
    if (ok) hit++;
  }
  return hit / pTokens.length;
}

/* ------------------------------ Catalog build ----------------------------- */

/**
 * Build a catalog of titles for all docs.
 * @param {Array} docs
 * @returns {Array<{key:string, raw:string, docIndex:number, code:string}>}
 */
export function buildTitleCatalog(docs) {
  const out = [];
  for (let i = 0; i < docs.length; i++) {
    const d = docs[i];
    if (!d) continue;
    const t = extractTitleFromDoc(d);
    if (!t) continue;
    const key = normalizePhrase(t);
    out.push({ key, raw: t, docIndex: i, code: d.docCode || "" });
  }
  return out;
}

/**
 * Pair titles to URLs using ≥85% title coverage within the URL.
 * Returns a Map<titleKey, { raw:string, urls:string[] }>
 */
export function pairTitlesToUrls(urlSet, titleCatalog, options) {
  const minCoverage = options?.minCoverage ?? 0.85;
  const m = new Map(); // key -> { raw, urls[] }

  for (const t of titleCatalog) m.set(t.key, { raw: t.raw, urls: [] });
  if (!urlSet || urlSet.size === 0) return m;

  const urls = Array.from(urlSet);
  for (const t of titleCatalog) {
    const rec = m.get(t.key);
    for (const u of urls) {
      const s = titleCoverageInUrl(t.raw, u, options);
      if (s >= minCoverage) rec.urls.push(u);
    }
  }
  return m;
}

/* ------------------------------ Title extract ----------------------------- */

export function extractTitleFromDoc(d) {
  // 1) explicit title from backend
  if (d.title && d.title.trim()) return d.title.trim();

  // 2) parse from HTML
  if (d.html) {
    try {
      const div = document.createElement("div");
      div.innerHTML = d.html;
      const h1 = div.querySelector("h1");
      if (h1?.textContent?.trim()) return h1.textContent.trim();
      const htmlTitle = div.querySelector("title");
      if (htmlTitle?.textContent?.trim()) return htmlTitle.textContent.trim();
    } catch {
      /* ignore */
    }
  }

  // 3) first non-empty text line
  if (d.text) {
    const first = (d.text.split(/\r?\n/).map((s) => s.trim()).find((s) => s.length > 0)) || "";
    if (first) return first.slice(0, 120);
  }

  // 4) filename fallback
  if (d.filename) {
    return d.filename.replace(/\.[^.\s]+$/, "").replace(/[_\-]+/g, " ").trim();
  }
  return "";
}

/* --------------------------- Local storage helpers ------------------------ */

const TITLE_INDEX_KEY = "linkcraftor_title_catalog_v1";

export function saveTitleCatalogToLocal(catalog, pairsMap) {
  try {
    const payload = {
      catalog,
      pairs: Array.from(pairsMap.entries()),
    };
    localStorage.setItem(TITLE_INDEX_KEY, JSON.stringify(payload));
  } catch {}
}

export function loadTitleCatalogFromLocal() {
  try {
    const raw = localStorage.getItem(TITLE_INDEX_KEY);
    if (!raw) return { catalog: [], pairs: new Map() };
    const obj = JSON.parse(raw);
    return {
      catalog: Array.isArray(obj.catalog) ? obj.catalog : [],
      pairs: new Map(Array.isArray(obj.pairs) ? obj.pairs : []),
    };
  } catch {
    return { catalog: [], pairs: new Map() };
  }
}
