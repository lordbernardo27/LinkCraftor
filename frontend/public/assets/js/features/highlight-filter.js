// assets/js/features/highlight-filter.js
// Temporary stub for highlight filtering.
// Right now it just says "yes, highlight this phrase" for everything,
// so the rest of the engine can run without errors.

export function shouldHighlightPhrase(phrase, meta = {}) {
  // basic sanity checks – you can leave this as-is for now
  const text = String(phrase || "").trim();
  if (!text) return false;          // nothing to highlight
  if (text.length < 3) return false; // super tiny fragments

  // For now, always allow – we’ll make this smarter later.
  return true;
}
