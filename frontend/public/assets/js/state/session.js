// public/assets/js/state/session.js
// Centralized persistence for LinkCraftor.
// Handles: editor session (docs + currentIndex), linked-set, imported URLs,
// and the highlight toggle. Uses localStorage only (no network).

/* ------------------------------ Storage keys ------------------------------ */

const STORAGE_KEY        = "linkcraftor_state_v1";
const HILITE_KEY         = "linkcraftor_highlight_enabled_v1";
const IL_LINKED_SET_KEY  = "linkcraftor_il_linked_set_v2";
const IMPORTED_URLS_KEY  = "linkcraftor_imported_urls_v1";

/* --------------------------- Editor state (docs) --------------------------- */

/**
 * Persist the editor state (docs + currentIndex).
 * @param {Array} docs
 * @param {number} currentIndex
 */
export function saveEditorState(docs, currentIndex) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ docs, currentIndex }));
  } catch {}
}

/**
 * Load the editor state.
 * @returns {{docs: Array, currentIndex: number}|null}
 */
export function loadEditorState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const state = JSON.parse(raw);
    if (!state || !Array.isArray(state.docs) || state.docs.length === 0) return null;
    const idx = Math.min(
      typeof state.currentIndex === "number" ? state.currentIndex : 0,
      state.docs.length - 1
    );
    return { docs: state.docs, currentIndex: idx };
  } catch {
    return null;
  }
}

/** Clear the editor state. */
export function clearEditorState() {
  try { localStorage.removeItem(STORAGE_KEY); } catch {}
}

/* ------------------------------ Linked phrases ---------------------------- */

/** @returns {Set<string>} */
export function loadLinkedSet() {
  try {
    const raw = localStorage.getItem(IL_LINKED_SET_KEY);
    return new Set(raw ? JSON.parse(raw) : []);
  } catch {
    return new Set();
  }
}

/** @param {Set<string>} set */
export function saveLinkedSet(set) {
  try {
    localStorage.setItem(IL_LINKED_SET_KEY, JSON.stringify(Array.from(set || [])));
  } catch {}
}

/* ------------------------------ Imported URLs ----------------------------- */

/** @returns {Set<string>} */
export function loadImportedUrls() {
  try {
    const raw = localStorage.getItem(IMPORTED_URLS_KEY);
    return new Set(raw ? JSON.parse(raw) : []);
  } catch {
    return new Set();
  }
}

/** @param {Set<string>} set */
export function saveImportedUrls(set) {
  try {
    localStorage.setItem(IMPORTED_URLS_KEY, JSON.stringify(Array.from(set || [])));
  } catch {}
}

/* ------------------------------ Highlight toggle -------------------------- */

/** @returns {boolean} default=true */
export function getHighlightSetting() {
  try {
    const saved = localStorage.getItem(HILITE_KEY);
    return saved === null ? true : saved === "true";
  } catch {
    return true;
  }
}

/** @param {boolean} enabled */
export function setHighlightSetting(enabled) {
  try { localStorage.setItem(HILITE_KEY, String(!!enabled)); } catch {}
}
