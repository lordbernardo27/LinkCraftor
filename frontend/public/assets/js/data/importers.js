// data/importers.js
// Lightweight URL import helpers for CSV / XML / TXT inputs.
// Each function accepts (text, targetSet) and returns the count of new URLs added.

const URL_RX = /\bhttps?:\/\/[^\s"'<>()]+/gi;

// --- Utilities --------------------------------------------------------------

function stripBOM(s = "") {
  if (typeof s !== "string") return "";
  return s.charCodeAt(0) === 0xFEFF ? s.slice(1) : s;
}

function isHttpUrl(u) {
  if (!u || typeof u !== "string") return false;
  const s = u.trim();
  if (!/^https?:\/\//i.test(s)) return false;
  try {
    const parsed = new URL(s);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

/** Normalize a URL minimally for dedupe without being destructive. */
function normalizeUrl(u) {
  try {
    const parsed = new URL(u.trim());
    // Strip fragments; keep query (so we don't break distinct pages)
    parsed.hash = "";
    // Remove default ports
    if ((parsed.protocol === "http:" && parsed.port === "80") ||
        (parsed.protocol === "https:" && parsed.port === "443")) {
      parsed.port = "";
    }
    // Collapse multiple slashes in path (but keep a single leading slash)
    parsed.pathname = parsed.pathname.replace(/\/{2,}/g, "/");
    // Avoid adding trailing slash unless path is empty
    if (parsed.pathname !== "/" && parsed.pathname.endsWith("/")) {
      parsed.pathname = parsed.pathname.replace(/\/+$/, "");
    }
    return parsed.toString();
  } catch {
    return "";
  }
}

function addMany(rawUrls, targetSet) {
  let added = 0;
  for (const ru of rawUrls) {
    if (!isHttpUrl(ru)) continue;
    const norm = normalizeUrl(ru);
    if (!norm) continue;
    if (!targetSet.has(norm)) {
      targetSet.add(norm);
      added++;
    }
  }
  return added;
}

/** Very small CSV parser (handles quotes and commas). Returns array of string[] rows. */
function parseCSV(text) {
  const rows = [];
  let i = 0, cur = "", row = [], inQ = false;
  const s = stripBOM(String(text || ""));
  while (i < s.length) {
    const ch = s[i];

    if (inQ) {
      if (ch === '"') {
        if (s[i + 1] === '"') { cur += '"'; i += 2; continue; } // escaped quote
        inQ = false; i++; continue;
      }
      cur += ch; i++; continue;
    }

    if (ch === '"') { inQ = true; i++; continue; }
    if (ch === ",") { row.push(cur); cur = ""; i++; continue; }
    if (ch === "\r") { i++; continue; }
    if (ch === "\n") { row.push(cur); rows.push(row); cur = ""; row = []; i++; continue; }

    cur += ch; i++;
  }
  // Flush last cell
  row.push(cur);
  rows.push(row);
  // Trim cells
  return rows.map(r => r.map(c => c.trim()));
}

/** Extract all http(s) URLs from arbitrary text */
function extractUrlsLoose(text) {
  const out = new Set();
  const s = stripBOM(String(text || ""));
  const matches = s.match(URL_RX) || [];
  for (const m of matches) out.add(m.replace(/[),.;]+$/g, "")); // trim trailing punctuation
  return Array.from(out);
}

// --- CSV --------------------------------------------------------------------

/**
 * CSV import: looks for common URL columns (url, link, loc, canonical, permalink, page, homepage).
 * If no header is detected, scans all cells for URLs.
 * @param {string} text
 * @param {Set<string>} targetSet
 * @returns {number} count of newly-added URLs
 */
export function importUrlsFromCSV(text, targetSet) {
  const rows = parseCSV(text);
  if (!rows.length) return 0;

  const header = rows[0].map(h => h.toLowerCase());
  const hasHeader =
    header.some(h => ["url", "link", "loc", "canonical", "permalink", "page", "homepage"].includes(h));

  const urlCols = [];
  if (hasHeader) {
    const wanted = new Set(["url", "link", "loc", "canonical", "permalink", "page", "homepage"]);
    header.forEach((h, idx) => { if (wanted.has(h)) urlCols.push(idx); });
  }

  const rawUrls = [];
  const start = hasHeader ? 1 : 0;

  for (let r = start; r < rows.length; r++) {
    const cells = rows[r];
    if (hasHeader && urlCols.length) {
      for (const ci of urlCols) {
        const val = (cells[ci] || "").trim();
        if (isHttpUrl(val)) rawUrls.push(val);
        else if (val) {
          // handle cases where a cell might contain multiple URLs separated by spaces or |
          rawUrls.push(...extractUrlsLoose(val));
        }
      }
    } else {
      // No header—scan every cell for URLs
      for (const c of cells) {
        if (!c) continue;
        if (isHttpUrl(c)) rawUrls.push(c);
        else rawUrls.push(...extractUrlsLoose(c));
      }
    }
  }

  return addMany(rawUrls, targetSet);
}

// --- XML (sitemap, RSS, Atom) ----------------------------------------------

/**
 * XML import: supports:
 *  - Sitemap <urlset><url><loc>...</loc></url>
 *  - RSS/Atom: <link>http(s)://..</link> or <link href="..."/>
 * Gracefully falls back to regex if DOMParser isn’t available.
 * @param {string} text
 * @param {Set<string>} targetSet
 * @returns {number}
 */
export function importUrlsFromXML(text, targetSet) {
  const xmlStr = stripBOM(String(text || ""));
  let rawUrls = [];

  try {
    if (typeof DOMParser !== "undefined") {
      const parser = new DOMParser();
      const doc = parser.parseFromString(xmlStr, "application/xml");

      // Errors?
      const err = doc.querySelector("parsererror");
      if (err) throw new Error("XML parse error");

      // Sitemap: <loc>
      doc.querySelectorAll("loc").forEach(loc => {
        const v = (loc.textContent || "").trim();
        if (isHttpUrl(v)) rawUrls.push(v);
      });

      // RSS/Atom: <link>text</link>
      doc.querySelectorAll("link").forEach(node => {
        const href = node.getAttribute && node.getAttribute("href");
        if (href && isHttpUrl(href)) { rawUrls.push(href); return; }
        const v = (node.textContent || "").trim();
        if (isHttpUrl(v)) rawUrls.push(v);
      });
    } else {
      // Fallback: regex all http(s) occurrences
      rawUrls = extractUrlsLoose(xmlStr);
    }
  } catch {
    // On any parsing error, fallback to regex
    rawUrls = extractUrlsLoose(xmlStr);
  }

  return addMany(rawUrls, targetSet);
}

// --- TXT --------------------------------------------------------------------

/**
 * TXT import: extracts all http(s) URLs from plain text (one per line or embedded).
 * @param {string} text
 * @param {Set<string>} targetSet
 * @returns {number}
 */
export function importUrlsFromTXT(text, targetSet) {
  const urls = extractUrlsLoose(text);
  return addMany(urls, targetSet);
}

export default {
  importUrlsFromCSV,
  importUrlsFromXML,
  importUrlsFromTXT,
};
