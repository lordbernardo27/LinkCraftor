// assets/js/ui/rejections.js
// Sidebar:
// 1) "Manage rejections" — lists rejected phrases and lets you restore/clear.
// 2) "Linked phrases" list — lists underlined phrases and lets you undo one phrase at a time.

const STORAGE_KEY = "linkcraftor_rejected_set_v1";

// ---------- Small helpers ----------

// assets/js/ui/rejections.js

function esc(s){
  return String(s ?? "").replace(/[&<>"']/g, m => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  }[m]));
}


function parseKey(k){
  const i = String(k || "").indexOf(":");
  if (i < 0) return { type: "engine", phrase: String(k || "") };
  return { type: k.slice(0, i), phrase: k.slice(i + 1) };
}

function typeLabel(t){
  if (t === "internal") return "Internal";
  if (t === "semantic") return "Semantic";
  if (t === "external") return "External";
  return "Engine";
}

// ---- Store helpers for rejections ----

function loadStore(){
  if (window.REJECTED_SET instanceof Set) return window.REJECTED_SET;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const arr = raw ? JSON.parse(raw) : [];
    return new Set(Array.isArray(arr) ? arr : []);
  } catch {
    return new Set();
  }
}

function saveStore(S){
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(S)));
  } catch {
    // ignore
  }
}

// ---- Highlight repaint nudger (shared by rejections + linked phrases) ----

function nudgeHighlightPaint(reason){
  // 1) Fire a semantic event in case the app listens for it
  document.dispatchEvent(new CustomEvent("lc:rejections:changed", { detail: { reason } }));

  // 2) Hard nudge: flip the Highlight checkbox off→on to trigger its "change" handler
  const t = document.getElementById("toggleHighlight");
  if (t) {
    const was = !!t.checked;
    t.checked = !was;
    t.dispatchEvent(new Event("change", { bubbles: true }));
    t.checked = was;
    t.dispatchEvent(new Event("change", { bubbles: true }));
  }

  // 3) Optional: if the app exposes a repaint hook, call it
  const fn =
    (window.LC && window.LC.repaintHighlights) ||
    window.repaintEngineHighlights ||
    window.repaintHighlights;
  if (typeof fn === "function") {
    try { fn({ reason }); } catch {}
  }
}

// Make this accessible to other modules if needed
if (typeof window !== "undefined") {
  window.LC_nudgeHighlightPaint = nudgeHighlightPaint;
}

// ---------- Rejections Panel ----------

/** Re-render the panel UI from window.REJECTED_SET */
export function rebuildRejectionsPanel(){
  const list = document.getElementById("rejectionsList");
  if (!list) return;

  const S = loadStore();
  window.REJECTED_SET = S;

  if (S.size === 0){
    list.innerHTML = `<div style="font-size:12px;color:#6b7280;">No rejections.</div>`;
    return;
  }

  const items = Array.from(S).map(k => ({ key: k, ...parseKey(k) }))
    .sort((a, b) => a.type.localeCompare(b.type) || a.phrase.localeCompare(b.phrase));

  list.innerHTML = items.map(it => `
    <div class="rej-item"
         data-key="${esc(it.key)}"
         style="display:flex;align-items:center;justify-content:space-between;gap:8px;padding:6px 0;border-bottom:1px solid #e5e7eb;">
      <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
        <span style="font-size:12px;color:#6b7280;border:1px solid #e5e7eb;border-radius:999px;padding:2px 8px;background:#f9fafb;">
          ${esc(typeLabel(it.type))}
        </span>
        <span style="font-size:13px;">${esc(it.phrase)}</span>
      </div>
      <button class="rej-restore"
              style="font-size:12px;padding:4px 8px;border:1px solid #e5e7eb;border-radius:6px;background:#fff;cursor:pointer;">
        Restore
      </button>
    </div>
  `).join("");
}

/** Wire buttons & item restore. Call once on load. */
export function initRejectionsUI(opts = {}){
  const { onChange = () => {} } = opts;

  // Ensure in-memory store mirrors persisted data
  window.REJECTED_SET = loadStore();

  const wrap = document.getElementById("rejectionsPanel");
  const clearBtn = document.getElementById("btnClearRejections");

  // Clear all
  clearBtn?.addEventListener("click", () => {
    window.REJECTED_SET = new Set();
    saveStore(window.REJECTED_SET);
    rebuildRejectionsPanel();
    onChange();
    nudgeHighlightPaint("clear-all");
  });

  // Restore one (event delegation)
  wrap?.addEventListener("click", (e) => {
    const b = e.target?.closest?.(".rej-restore");
    if (!b) return;
    const row = b.closest(".rej-item");
    const key = row?.getAttribute("data-key") || "";
    if (!key) return;

    const S = loadStore();
    S.delete(key);
    window.REJECTED_SET = S;
    saveStore(S);

    rebuildRejectionsPanel();
    onChange();
    nudgeHighlightPaint("restore-one");
  });

  // First paint
  rebuildRejectionsPanel();
}

// ---------- Linked Phrases List (per-phrase Undo) ----------

// Scan the editor for all underlined phrases
function collectLinkedFromDom(root){
  const out = new Map(); // phrase -> { phrase, count }
  if (!root) return out;

  const nodes = root.querySelectorAll("span.lc-underlined[data-phrase]");
  nodes.forEach(el => {
    const phrase = decodeURIComponent(el.getAttribute("data-phrase") || "");
    if (!phrase) return;
    if (!out.has(phrase)) {
      out.set(phrase, { phrase, count: 1 });
    } else {
      out.get(phrase).count++;
    }
  });
  return out;
}

function jumpToLinkedPhrase(phrase){
  const root = document.getElementById("doc-content");
  if (!root || !phrase) return;

  const encoded = encodeURIComponent(phrase);
  const target = root.querySelector(`span.lc-underlined[data-phrase="${encoded}"]`);
  if (!target) return;

  target.scrollIntoView({ behavior: "smooth", block: "center" });
  target.classList.add("flash");
  setTimeout(() => target.classList.remove("flash"), 900);
}

// DOM-only fallback undo: remove underlines for this phrase.
// Engine will be nudged to repaint highlights so suggestions can return.
function naiveUndoPhraseInDom(phrase){
  const root = document.getElementById("doc-content");
  if (!root || !phrase) return;

  const encoded = encodeURIComponent(phrase);
  const nodes = Array.from(root.querySelectorAll(`span.lc-underlined[data-phrase="${encoded}"]`));
  nodes.forEach(span => {
    const text = span.textContent || "";
    const tn = document.createTextNode(text);
    span.parentNode.replaceChild(tn, span);
  });
}

function renderLinkedList(listEl, dataMap){
  if (!listEl) return;

  if (!dataMap || dataMap.size === 0){
    listEl.innerHTML = `<div style="font-size:12px;color:#6b7280;">No linked phrases yet.</div>`;
    return;
  }

  const items = Array.from(dataMap.values())
    .sort((a, b) => a.phrase.localeCompare(b.phrase));

  listEl.innerHTML = items.map(it => `
    <div class="pill-row" data-phrase="${encodeURIComponent(it.phrase)}">
      <span class="pill-phrase" title="${esc(it.phrase)}">${esc(it.phrase)}</span>
      <span style="font-size:11px;color:#6b7280;">×${it.count}</span>
      <button class="pill-undo">Undo</button>
    </div>
  `).join("");
}

/** Public: rebuild the Linked phrases list from current DOM */
export function rebuildLinkedPhrasesList(){
  const list = document.getElementById("linkedPhrasesList");
  if (!list) return;
  const root = document.getElementById("doc-content");
  const data = collectLinkedFromDom(root);
  renderLinkedList(list, data);
}

// Also expose to window so IL modal / bulk engine can call it after changes
if (typeof window !== "undefined") {
  window.LC_rebuildLinkedList = rebuildLinkedPhrasesList;
}

/**
 * Init Linked phrases list UI.
 * opts:
 *  - onUndoPhrase(phrase): optional callback so app.js can update engine state
 *  - onChange(): called after undo, for any extra refreshes
 */
export function initLinkedPhrasesUI(opts = {}){
  const {
    onUndoPhrase = () => {},
    onChange = () => {}
  } = opts;

  const list = document.getElementById("linkedPhrasesList");
  if (!list) return;

  // First paint from current doc
  rebuildLinkedPhrasesList();

  // Row / undo interactions
  list.addEventListener("click", (e) => {
    const undoBtn = e.target?.closest?.(".pill-undo");
    const row = e.target?.closest?.(".pill-row");
    if (!row) return;

    const phrase = decodeURIComponent(row.getAttribute("data-phrase") || "");
    if (!phrase) return;

    if (undoBtn) {
      // 1) Let app.js update internal LINKED_SET/LINKED_MAP if it wants to
      try { onUndoPhrase(phrase); } catch {}

      // 2) DOM fallback: remove the underlines for that phrase
      naiveUndoPhraseInDom(phrase);

      // 3) Rebuild list + nudge highlights & link resolution
      rebuildLinkedPhrasesList();
      onChange();
      nudgeHighlightPaint("undo-linked-phrase");

      // 4) If link resolution panel exists, ask it to refresh
      if (typeof window.LR_rebuild === "function") {
        try { window.LR_rebuild(); } catch {}
      }
    } else {
      // Clicked the row/phrase itself: just jump to that phrase
      jumpToLinkedPhrase(phrase);
    }
  });
}
