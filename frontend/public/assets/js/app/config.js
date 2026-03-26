// public/assets/js/app/config.js

// Base for your backend API. You can override it by setting window.LC_API_BASE before scripts load.
export const API_BASE =
  (typeof window !== "undefined" && window.LC_API_BASE
    ? String(window.LC_API_BASE).replace(/\/$/, "")
    : (typeof window !== "undefined" ? window.location.origin : "")) || "";

// (Optional) central paths used by api.js. Safe to keep even if app.js only imports API_BASE.
export const ENDPOINTS = Object.freeze({
  upload:          `${API_BASE}/api/upload?workspace_id=default`,
  exportDocx:      `${API_BASE}/api/export/docx`,
  exportZip:       `${API_BASE}/api/export/zip`,
  exportRar:       `${API_BASE}/api/export/rar`,
  downloadOriginal: (filename) =>
    `${API_BASE}/api/original/${encodeURIComponent(filename || "")}`,
});
