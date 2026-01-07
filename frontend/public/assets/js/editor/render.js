// public/assets/js/editor/render.js
import { $, safeSetText } from "../core/dom.js";
import { state } from "../core/state.js";
import { saveState } from "../core/state.js";
import { highlightKeywords } from "./highlight.js";
import { updateDetected } from "./panels.js";

// Re-render a document by index
export function renderDoc(i) {
  if (!Array.isArray(state.docs) || i < 0 || i >= state.docs.length) return;

  state.currentIndex = i;
  const d = state.docs[i];

  const viewerEl = $("doc-content");
  const topMeta = $("topMeta");
  const docMeta = $("docMeta");
  const docCountMeta = $("docCountMeta");
  const allDocs = $("allDocs");

  // Render content
  if (viewerEl) {
    if (d.html && d.html.trim()) {
      viewerEl.innerHTML = d.html;
    } else {
      const safeText = typeof d.text === "string" ? d.text : "";
      viewerEl.textContent = safeText || "Empty document";
    }
  }

  // Update meta
  safeSetText(topMeta, `File: ${d.filename || "Untitled"}`, "topMeta");
  safeSetText(docMeta, `Code: ${d.docCode || ""}`, "docMeta");
  safeSetText(docCountMeta, `Doc ${i + 1} of ${state.docs.length}`, "docCountMeta");

  // Update dropdown
  if (allDocs) {
    allDocs.value = d.filename || "";
  }

  updateDocNavButtons();
  updateDetected();
  highlightKeywords();
  saveState({ docs: state.docs, currentIndex: state.currentIndex });
}

// Refresh dropdown with doc list
export function refreshDropdown() {
  const allDocs = $("allDocs");
  if (!allDocs) return;

  allDocs.innerHTML = "<option value=''>All docs</option>";
  state.docs.forEach((d) => {
    const opt = document.createElement("option");
    opt.value = d.filename || "";
    opt.textContent = d.filename || "Untitled";
    allDocs.appendChild(opt);
  });
}

// Enable/disable prev/next navigation buttons
export function updateDocNavButtons() {
  const btnPrevDoc = $("btnPrevDoc");
  const btnNextDoc = $("btnNextDoc");

  if (!btnPrevDoc || !btnNextDoc) return;
  const idx = state.currentIndex;
  const total = state.docs.length;

  btnPrevDoc.disabled = idx <= 0;
  btnNextDoc.disabled = idx >= total - 1 || total === 0;
}

// Navigate to previous document
export function goPrevDoc() {
  if (!Array.isArray(state.docs) || state.docs.length === 0) return;
  const idx = Number.isInteger(state.currentIndex) ? state.currentIndex : 0;
  if (idx > 0) {
    renderDoc(idx - 1);
  }
}

// Navigate to next document
export function goNextDoc() {
  if (!Array.isArray(state.docs) || state.docs.length === 0) return;
  const last = state.docs.length - 1;
  const idx = Number.isInteger(state.currentIndex) ? state.currentIndex : 0;
  if (idx < last) {
    renderDoc(idx + 1);
  }
}
