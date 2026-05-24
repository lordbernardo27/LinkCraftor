from pathlib import Path

p = Path("frontend/public/assets/js/app.js")
s = p.read_text(encoding="utf-8", errors="replace")

start = s.find('const btnClearSession = $("btnClearSession");\nbtnClearSession?.addEventListener("click", async () => {')
if start == -1:
    raise SystemExit("Clear Session block start not found")

end_marker = "\n});\n\n/* Stopwords UI */"
end = s.find(end_marker, start)
if end == -1:
    raise SystemExit("Clear Session block end not found")

new_block = r'''const btnClearSession = $("btnClearSession");
btnClearSession?.addEventListener("click", async () => {
  const confirmed = window.confirm(
    "Clear current session?\n\nThis will clear:\n- Current editor document\n- Runtime highlights\n- Temporary link review state\n- Imported sitemap URLs\n- Draft map imports\n\nThis will NOT disconnect the domain."
  );

  if (!confirmed) return;

  const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
  const ws = getCurrentWorkspaceId("ws_betterhealthcheck_com");

  // Clear backend imported sitemap URLs.
  try {
    await fetch(`${API_BASE}/api/urls/clear?workspace_id=${encodeURIComponent(ws)}`, {
      method: "POST",
    });
  } catch (e) {
    console.warn("[ClearSession] imported URL clear failed:", e);
  }

  // Clear backend draft map imports.
  try {
    await fetch(`${API_BASE}/api/draft/clear?workspace_id=${encodeURIComponent(ws)}`, {
      method: "POST",
    });
  } catch (e) {
    console.warn("[ClearSession] draft clear failed:", e);
  }

  // Clear frontend imported-memory systems.
  try { IMPORTED_URLS = new Set(); } catch {}
  try { window.IMPORTED_URLS = new Set(); } catch {}
  try { IMPORTED_TOPICS.length = 0; } catch {}
  try { window.LC_IMPORTS = []; } catch {}
  try { window.LC_getImportedTopics = () => []; } catch {}
  try { DRAFT_TOPICS = new Map(); } catch {}
  try { PUBLISHED_TOPICS = new Map(); } catch {}
  try { TITLE_INDEX = new Map(); } catch {}
  try { TITLE_ALIAS_MAP = new Map(); } catch {}

  // Clear loaded editor session.
  try { clearState(); } catch {}
  try { docs.splice(0, docs.length); } catch {}
  try { currentIndex = -1; } catch {}
  try { LAST_ENGINE_OUTPUT = { internal_strong: [], semantic_optional: [], hidden: [], meta: {} }; } catch {}
  try { APPLIED_LINKS = []; } catch {}
  try { LINKED_SET.clear(); } catch {}
  try { LINKED_MAP.clear(); } catch {}

  // Clear UI.
  if (viewerEl) viewerEl.innerHTML = "Upload a document to begin editing…";
  if (editor) editor.innerHTML = "";

  safeSetText(topMeta, "No document loaded", "topMeta");
  safeSetText(docMeta, "Code: —", "docMeta");
  safeSetText(docCountMeta, "Doc 0 of 0", "docCountMeta");

  if (allDocs) allDocs.innerHTML = "<option value=''>All docs</option>";

  try { setImportCount(0); } catch {}
  try { updateImportBadge?.(); } catch {}
  try { updateDocNavButtons(); } catch {}
  try { underlineLinkedPhrases(); } catch {}
  try { highlightBucketKeywords(); } catch {}
  try { updateHighlightBadge(); } catch {}
  try { rebuildEngineHighlightsPanel(); } catch {}
  try { rebuildLinkedPhrasesList(); } catch {}
  try { rebuildRejectionsPanel(); } catch {}

  showToast(errorBox, "Session cleared.", 1600);
  console.log("[ClearSession] completed");
});'''

s = s[:start] + new_block + s[end:]

p.write_text(s, encoding="utf-8")
print("Clear Session block replaced")
