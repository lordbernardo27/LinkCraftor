// public/assets/js/data/urls.js
export let IMPORTED_URLS = new Set();

const DEFAULT_WORKSPACE = "default";

async function apiFetch(path, opts = {}) {
  const res = await fetch(path, opts);
  if (!res.ok) {
    const msg = await res.text().catch(() => "");
    throw new Error(msg || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function loadImportedUrls(workspaceId = DEFAULT_WORKSPACE) {
  const data = await apiFetch(`/api/urls/list?workspace_id=${encodeURIComponent(workspaceId)}`);
  IMPORTED_URLS = new Set(Array.isArray(data.urls) ? data.urls : []);
  return IMPORTED_URLS;
}

export async function clearImportedUrls(workspaceId = DEFAULT_WORKSPACE) {
  await apiFetch(`/api/urls/clear?workspace_id=${encodeURIComponent(workspaceId)}`, { method: "POST" });
  IMPORTED_URLS = new Set();
  return true;
}

/**
 * Import via backend (UploadFile) — this is the NEW “correct” import path.
 * Returns number added.
 */
export async function importUrlsFromFile(file, workspaceId = DEFAULT_WORKSPACE) {
  const fd = new FormData();
  fd.append("file", file);

  const data = await apiFetch(`/api/urls/import?workspace_id=${encodeURIComponent(workspaceId)}`, {
    method: "POST",
    body: fd,
  });

  // refresh local cache
  await loadImportedUrls(workspaceId);

  return Number(data.added || 0);
}

/**
 * Back-compat (if anything still calls these):
 * We keep names, but route them to backend by creating a Blob File.
 */
function textToFile(text, filename) {
  const blob = new Blob([String(text || "")], { type: "text/plain" });
  return new File([blob], filename || "import.txt", { type: "text/plain" });
}

export async function importUrlsFromCSV(text, workspaceId = DEFAULT_WORKSPACE) {
  return importUrlsFromFile(textToFile(text, "import.csv"), workspaceId);
}

export async function importUrlsFromTXT(text, workspaceId = DEFAULT_WORKSPACE) {
  return importUrlsFromFile(textToFile(text, "import.txt"), workspaceId);
}

export async function importUrlsFromXML(text, workspaceId = DEFAULT_WORKSPACE) {
  return importUrlsFromFile(textToFile(text, "import.xml"), workspaceId);
}
