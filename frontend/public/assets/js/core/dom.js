// public/assets/js/core/dom.js
// Small DOM/utility helpers used across the app.

export const $ = (id) => document.getElementById(id);

export function safeSetText(el, text, id) {
  if (!el) { console.warn(`[LinkCraftor] Missing #${id}`); return; }
  el.textContent = text;
}

export function showToast(el, msg, ms = 1400) {
  if (!el) return;
  el.textContent = msg;
  setTimeout(() => (el.textContent = ""), ms);
}

export function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
