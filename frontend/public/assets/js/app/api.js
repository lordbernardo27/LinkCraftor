// assets/js/app/api.js
// Uploads ALL formats to backend /api/files/upload (so they get stored + indexed into pools).
// Also keeps originals locally so “Download original” works without a server.
//
// Point API_BASE at your FastAPI server (we default to 8001 for dev).
const API_BASE =
  (typeof window !== "undefined" && window.LINKCRAFTOR_API_BASE) ||
  "http://127.0.0.1:8001";

// Keep originals so “Download original” works without a server.
const ORIGINAL_BLOBS = new Map();
const ORIGINAL_URLS = new Map();

function extOf(name = "") {
  const m = /\.[^.]+$/.exec(name);
  return m ? m[0].toLowerCase() : "";
}

function asDocRecord({
  filename,
  ext,
  text = "",
  html = "",
  size = 0,
  doc_id = "",
  h1 = "",
  h1_source = "",
  h1_error = "",
  workspace_id = "",
}) {
  return { filename, ext, text, html, size, doc_id, h1, h1_source, h1_error, workspace_id };
}

function getWorkspaceId(explicitWs) {
  let ws =
    (explicitWs || "").trim() ||
    (
      (typeof window !== "undefined" &&
        (window.WORKSPACE_ID || window.LINKCRAFTOR_WORKSPACE_ID)) ||
      ""
    ).trim() ||
    (
      (typeof localStorage !== "undefined" &&
        (localStorage.getItem("workspace_id") || localStorage.getItem("ws"))) ||
      ""
    ).trim() ||
    "ws_betterhealthcheck_com";

  if (!ws.toLowerCase().startsWith("ws_")) {
    ws = `ws_${ws}`;
  }

  return ws;
}

// -------------------------
// Upload
// -------------------------
// NOTE: This now uploads every file type to backend so it is persisted + indexed for pools.
// It still reads some formats locally only to keep a smooth preview, but the source of truth is backend.
export async function uploadFile(file, workspaceId) {
  if (!file || !file.name) throw new Error("No file provided");

  const ws = getWorkspaceId(workspaceId);
  const ext = extOf(file.name);

  // Store original blob locally for "Download original"
  ORIGINAL_BLOBS.set(file.name, file);

  // Always upload to backend so it lands in:
  // backend/server/data/docs/<ws>/
  const fd = new FormData();
  fd.append("file", file);

  const res = await fetch(`${API_BASE}/api/files/upload?workspace_id=${encodeURIComponent(ws)}`, {
    method: "POST",
    body: fd,
  });

  let data;
  try {
    data = await res.json();
  } catch {
    throw new Error(`upload_failed_http_${res.status}`);
  }

  if (!res.ok || !data || data.ok !== true) {
    const msg =
      data && (data.detail || data.error)
        ? (data.detail || data.error)
        : `upload_failed_http_${res.status}`;
    throw new Error(msg);
  }

  // Backend returns:
  // { ok, workspace_id, doc:{...}, filename, ext, text, html, is_html, truncated }
  const doc = data.doc || {};
  const text = (data.text ?? doc.text ?? "") || "";
  const html = (data.html ?? doc.html ?? "") || "";

  return asDocRecord({
    filename: data.filename || doc.filename || file.name,
    ext: data.ext || doc.ext || ext,
    text,
    html,
    size: file.size,
    doc_id: doc.doc_id || "",
    h1: doc.h1 || "",
    h1_source: doc.h1_source || "",
    h1_error: doc.h1_error || "",
    workspace_id: data.workspace_id || ws,
  });
}

// -------------------------
// Downloads / Exports
// -------------------------
export function downloadOriginalUrl(filename) {
  if (ORIGINAL_BLOBS.has(filename)) {
    try {
      if (ORIGINAL_URLS.has(filename)) {
        URL.revokeObjectURL(ORIGINAL_URLS.get(filename));
      }
    } catch {}
    const url = URL.createObjectURL(ORIGINAL_BLOBS.get(filename));
    ORIGINAL_URLS.set(filename, url);
    return url;
  }
  // If you later persist originals on the server, you can serve them here:
  return `${API_BASE}/api/download/original?file=${encodeURIComponent(filename)}`;
}

// (Optional) bulk export stubs kept for later; safe to leave as-is.
export function exportZipUrl() {
  return `${API_BASE}/api/export/zip`;
}

export function exportRarUrl() {
  return `${API_BASE}/api/export/rar`;
}

// Try backend DOCX first; if missing, fall back to Word-compatible .doc (HTML)
export async function exportDocx(filename, bodyHtml) {
  try {
    const res = await fetch(`${API_BASE}/api/export/docx`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename, html: bodyHtml }),
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