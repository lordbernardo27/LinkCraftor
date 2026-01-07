// Adapter implementations for selected sources + signatures for the rest.
// Implemented now: OpenLibrary (search) and Wikipedia (search).
// Everything else returns [] so it's safe until you expand.
//
// Each adapter returns an array of provider-specific raw items.
// The shared `normalize()` maps a raw item to the ReferenceItem shape.

//
// Types (for reference):
// ReferenceItem:
// { sourceId, title, url, summary?, publishedAt?, license?, attribution?, contentType?, sourceTrust }
//
// ReferenceItemRaw:
// { _raw: any, _meta?: any }  // provider-specific payload
//

/** Fetch JSON with a timeout (browser-friendly). */
async function fetchJSON(url, opts = {}, timeoutMs = 4000) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...opts, signal: ctrl.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(t);
  }
}

/** Small utility: strip HTML tags (Wikipedia snippets). */
function stripHTML(s) {
  return String(s || "").replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
}

/** Title → Wikipedia article URL ("Machine learning" → /wiki/Machine_learning). */
function wikipediaUrlFromTitle(title) {
  const slug = String(title || "").replace(/\s+/g, "_");
  return `https://en.wikipedia.org/wiki/${encodeURIComponent(slug)}`;
}

// ---------------------------------------------------------------------------
// SEARCH ADAPTER
// ---------------------------------------------------------------------------

export async function searchAdapter(source, phrase, context) {
  const q = String(phrase || "").trim();
  if (!q) return [];

  switch (source.id) {
    case "ref_openlibrary":
      return openLibrarySearch(source, q);

    case "ref_wikipedia":
      return wikipediaSearch(source, q);

    // Add more sources here over time...
    default:
      return [];
  }
}

// OpenLibrary search (no auth, CORS OK)
// API: GET https://openlibrary.org/search.json?q=...&limit=30
async function openLibrarySearch(source, q) {
  const base = source.baseUrl?.replace(/\/+$/, "") || "https://openlibrary.org";
  const url = `${base}/search.json?q=${encodeURIComponent(q)}&limit=30`;
  const json = await fetchJSON(url);
  const docs = Array.isArray(json?.docs) ? json.docs : [];

  return docs.map(d => ({ _raw: d, _meta: { provider: "openlibrary" } }));
}

// Wikipedia search (no key; must include origin=* for CORS)
// API: GET https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=...&format=json&utf8=1&origin=*
async function wikipediaSearch(source, q) {
  // Ignore registry.queryParam; Wikipedia needs its own params.
  const api = "https://en.wikipedia.org/w/api.php";
  const params = new URLSearchParams({
    action: "query",
    list: "search",
    srsearch: q,
    format: "json",
    utf8: "1",
    origin: "*" // required for browser CORS
  });
  const url = `${api}?${params.toString()}`;
  const json = await fetchJSON(url);
  const arr = Array.isArray(json?.query?.search) ? json.query.search : [];

  return arr.map(s => ({ _raw: s, _meta: { provider: "wikipedia" } }));
}

// ---------------------------------------------------------------------------
// REST ADAPTER (stub)
// ---------------------------------------------------------------------------
export async function restAdapter(source, phrase, context) {
  // e.g., DOI content negotiation, PubChem, RxNorm, etc.
  // Not implemented yet; safe empty return.
  return [];
}

// ---------------------------------------------------------------------------
// SPARQL ADAPTER (stub)
// ---------------------------------------------------------------------------
export async function sparqlAdapter(source, phrase, context) {
  // e.g., Wikidata/DBpedia templated queries.
  // Not implemented yet; safe empty return.
  return [];
}

// ---------------------------------------------------------------------------
// BROWSE ADAPTER (stub)
// ---------------------------------------------------------------------------
export async function browseAdapter(source, phrase, context) {
  // e.g., CISA KEV feed, MDN BCD static datasets.
  // Not implemented yet; safe empty return.
  return [];
}

// ---------------------------------------------------------------------------
// NORMALIZER
// ---------------------------------------------------------------------------

/**
 * Normalize a provider raw item to ReferenceItem.
 * NOTE: sourceTrust is injected upstream; we still fill sensible fields here.
 * @param {any} source
 * @param {{_raw:any, _meta?:{provider?:string}}} item
 * @returns {import("./references.js").ReferenceItem}
 */
export function normalize(source, item) {
  const provider = item?._meta?.provider;

  if (provider === "openlibrary") {
    const d = item._raw || {};
    const title = d.title || d.title_suggest || "";
    const key = d.key || (Array.isArray(d.edition_key) ? `/books/${d.edition_key[0]}` : "");
    const url = key ? `https://openlibrary.org${key}` : "";
    const authors = Array.isArray(d.author_name) ? d.author_name.join(", ") : (d.author_name || "");
    const year = d.first_publish_year ? ` (${d.first_publish_year})` : "";
    const summary = [authors || "", year || ""].join("").trim();

    return {
      sourceId: source?.id || "ref_openlibrary",
      title,
      url,
      summary: summary || undefined,
      publishedAt: undefined, // OpenLibrary search doesn't include exact pub date
      license: undefined,
      attribution: "OpenLibrary",
      contentType: "doc",
      sourceTrust: typeof source?.trust === "number" ? source.trust : 0.75
    };
  }

  if (provider === "wikipedia") {
    const s = item._raw || {};
    const title = s.title || "";
    const url = wikipediaUrlFromTitle(title);
    const snippet = stripHTML(s.snippet || "");
    const publishedAt = s.timestamp || undefined;

    return {
      sourceId: source?.id || "ref_wikipedia",
      title,
      url,
      summary: snippet || undefined,
      publishedAt,
      license: "CC BY-SA", // Wikipedia content license
      attribution: "Wikipedia",
      contentType: "article",
      sourceTrust: typeof source?.trust === "number" ? source.trust : 0.7
    };
  }

  // Fallback: if the raw already looks normalized, pass it through,
  // otherwise return a minimal shell (will be filtered out upstream if missing title/url).
  const r = item?._raw || {};
  return {
    sourceId: source?.id || "unknown",
    title: r.title || "",
    url: r.url || "",
    summary: r.summary || undefined,
    publishedAt: r.publishedAt || undefined,
    license: r.license || undefined,
    attribution: r.attribution || undefined,
    contentType: r.contentType || undefined,
    sourceTrust: typeof source?.trust === "number" ? source.trust : 0.5
  };
}
