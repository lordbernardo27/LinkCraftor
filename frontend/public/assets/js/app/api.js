// assets/js/app/api.js
// Client-only for HTML/MD/TXT; uses backend for DOCX.
// Point API_BASE at your FastAPI server (we default to 8001 for dev).
const API_BASE =
  (typeof window !== "undefined" && window.LINKCRAFTOR_API_BASE) ||
  "http://127.0.0.1:8001";

// Keep originals so “Download original” works without a server.
const ORIGINAL_BLOBS = new Map();
const ORIGINAL_URLS  = new Map();

function extOf(name = "") {
  const m = /\.[^.]+$/.exec(name);
  return m ? m[0].toLowerCase() : "";
}

function asDocRecord({ filename, ext, text = "", html = "", size = 0 }) {
  return { filename, ext, text, html, size };
}

// -------------------------
// Upload
// -------------------------
export async function uploadFile(file) {
  const ext = extOf(file.name);

  // 1) Handle browser-native formats locally
  if (ext === ".html" || ext === ".htm" || ext === ".md" || ext === ".txt") {
    const text = await file.text();
    ORIGINAL_BLOBS.set(file.name, file);

    if (ext === ".html" || ext === ".htm") {
      return asDocRecord({ filename: file.name, ext, text, html: text, size: file.size });
    }
    return asDocRecord({ filename: file.name, ext, text, html: "", size: file.size });
  }

  // 2) DOCX → call our FastAPI converter
  if (ext === ".docx") {
    const fd = new FormData();
    fd.append("file", file);

    const res = await fetch(`${API_BASE}/api/convert/docx`, { method: "POST", body: fd });
    if (!res.ok) throw new Error(`DOCX convert failed (${res.status})`);

    const data = await res.json(); // { filename, ext, html, text }
    ORIGINAL_BLOBS.set(file.name, file);

    return asDocRecord({
      filename: data.filename || file.name,
      ext: ".docx",
      text: data.text || "",
      html: data.html || "",
      size: file.size
    });
  }

  // 3) Anything else is unsupported (we’ll add later)
  throw new Error(`Unsupported file type: ${ext || "unknown"}`);
}

// -------------------------
// Downloads / Exports
// -------------------------
export function downloadOriginalUrl(filename) {
  if (ORIGINAL_BLOBS.has(filename)) {
    try { if (ORIGINAL_URLS.has(filename)) URL.revokeObjectURL(ORIGINAL_URLS.get(filename)); } catch {}
    const url = URL.createObjectURL(ORIGINAL_BLOBS.get(filename));
    ORIGINAL_URLS.set(filename, url);
    return url;
  }
  // If you later persist originals on the server, you can serve them here:
  return `${API_BASE}/api/download/original?file=${encodeURIComponent(filename)}`;
}

// (Optional) bulk export stubs kept for later; safe to leave as-is.
export function exportZipUrl() { return `${API_BASE}/api/export/zip`; }
export function exportRarUrl() { return `${API_BASE}/api/export/rar`; }

// Try backend DOCX first; if missing, fall back to Word-compatible .doc (HTML)
export async function exportDocx(filename, bodyHtml) {
  try {
    const res = await fetch(`${API_BASE}/api/export/docx`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename, html: bodyHtml })
    });
    if (res.ok) return await res.blob();
  } catch (_) {
    // ignore and fall through
  }

  const htmlDoc =
    `<!doctype html>
<html xmlns:o="urn:schemas-microsoft-com:office:office"
      xmlns:w="urn:schemas-microsoft-com:office:word"
      xmlns="http://www.w3.org/TR/REC-html40">
<head><meta charset="utf-8"><title>${filename}</title></head>
<body>${bodyHtml}</body></html>`;

  return new Blob([htmlDoc], { type: "application/msword" });
}
