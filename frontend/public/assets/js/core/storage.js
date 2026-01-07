// public/assets/js/core/storage.js
// Centralized localStorage helpers + keys

export const KEYS = {
  STATE: "linkcraftor_state_v1",
  HILITE: "linkcraftor_highlight_enabled_v1",
  SETTINGS: "linkcraftor_kw_settings_v2",
  INTERNAL: "linkcraftor_internal_terms_v1",
  EXTERNAL: "linkcraftor_external_terms_v1",
  SEMANTIC: "linkcraftor_semantic_terms_v1",
  STOPWORDS: "linkcraftor_stopwords_v1",
  IL_LINKED_SET: "linkcraftor_il_linked_set_v2",
  IMPORTED_URLS: "linkcraftor_imported_urls_v1",
  TITLE_INDEX: "linkcraftor_title_index_v1",
};

export function lsGet(key, fallback = null) {
  try {
    const raw = localStorage.getItem(key);
    if (raw === null) return fallback;
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export function lsSet(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {}
}

export function lsDel(key) {
  try {
    localStorage.removeItem(key);
  } catch {}
}
