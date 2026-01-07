// assets/js/ui/engine_highlights.js
// Sidebar: Engine Highlights list + filter + highlight toggle.

import { escapeHtml } from "../core/dom.js";
import { loadBuckets as loadBucketsFromStore } from "../data/settings.js";

/* local helpers (self-contained) */
const norm = s => String(s || "").toLowerCase().trim().replace(/\s+/g, " ");
const escRe = s => String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
function makeBoundaryRx(phrase) {
  const escaped = escRe(phrase).replace(/\s+/g, "\\s+");
  return new RegExp(`(^|[^\\p{L}\\p{N}])(${escaped})(?=$|[^\\p{L}\\p{N}])`, "giu");
}

/* deps injected from app.js */
let onToggleHighlight = null;
let onUpdateBadge = null;

function updateBadge() {
  if (typeof onUpdateBadge === "function") {
    onUpdateBadge();
    return;
  }
  const badge = document.getElementById("highlightCountBadge");
  if (badge) {
    const count = document.querySelectorAll("#doc-content mark.kwd").length;
    badge.textContent = String(count);
  }
}

function scrollToMark(mark) {
  try {
    mark.scrollIntoView({ behavior: "smooth", block: "center" });
    mark.classList.add("flash");
    setTimeout(() => mark.classList.remove("flash"), 900);
    mark.focus?.();
  } catch {}
}

export function rebuildEngineHighlightsPanel() {
  const list = document.getElementById("engineHighlightList");
  const viewer = document.getElementById("doc-content");
  if (!list || !viewer) return;

  const filt = (document.getElementById("engineFilter")?.value || "all");

  // Bucket view (reads from settings store)
  if (filt === "bucket") {
    const b = loadBucketsFromStore() || {};
    const strong   = (b.strong   ?? b.internal ?? []);
    const optional = (b.optional ?? b.semantic ?? []);
    const external = (b.external ?? []);

    const rows = [
      ...strong.map(w => ({ phrase:w, tier:"Strong",   mode:"internal", dot:"#3b82f6" })),
      ...optional.map(w => ({ phrase:w, tier:"Optional",mode:"internal", dot:"#f59e0b" })),
      ...external.map(w => ({ phrase:w, tier:"External",mode:"external", dot:"#10b981"})),
    ];

    if (!rows.length) {
      list.innerHTML = `<div style="font-size:12px;color:#6b7280;">No bucket entries saved.</div>`;
      updateBadge();
      return;
    }

    list.innerHTML = rows.map((r, i) => `
      <div class="kw-item" data-phrase="${escapeHtml(r.phrase)}" data-mode="${r.mode}" data-i="${i}">
        <span class="kw-dot" style="display:inline-block;width:8px;height:8px;border-radius:999px;background:${r.dot};margin-right:6px;"></span>
        <button class="kw-jump" title="Find in doc" style="font-size:12px;">${escapeHtml(r.phrase)}</button>
        <span class="qty" style="font-size:12px;color:#6b7280;">· ${r.tier} (Bucket)</span>
      </div>
    `).join("");

    Array.from(list.querySelectorAll(".kw-item")).forEach((row) => {
      const phrase = row.getAttribute("data-phrase") || "";
      row.querySelector(".kw-jump")?.addEventListener("click", (e) => {
        e.preventDefault();
        // try to jump to an existing mark (bucket or engine); fallback to text search
        const m = Array.from(viewer.querySelectorAll("mark.kwd-int, mark.kwd-ext, mark.kwd-sem, mark.kwd"))
          .find(x => decodeURIComponent(x.getAttribute("data-phrase")||"") === phrase);
        if (m) { scrollToMark(m); return; }
        const rx = makeBoundaryRx(phrase);
        const tnWalker = document.createTreeWalker(viewer, NodeFilter.SHOW_TEXT, null);
        while (tnWalker.nextNode()) {
          const tn = tnWalker.currentNode;
          rx.lastIndex = 0;
          if (rx.test(tn.nodeValue || "")) {
            tn.parentElement?.scrollIntoView({ behavior:"smooth", block:"center" });
            break;
          }
        }
      });
    });

    updateBadge();
    return;
  }

  // Normal (engine marks)
  let marks = Array.from(viewer.querySelectorAll("mark.kwd"));
  if (filt === "strong")   marks = marks.filter(m => m.classList.contains("kwd-strong"));
  if (filt === "optional") marks = marks.filter(m => m.classList.contains("kwd-optional"));
  if (filt === "external") marks = marks.filter(m => m.classList.contains("kwd-external"));

  updateBadge();

  if (!marks.length) {
    list.innerHTML = `<div style="font-size:12px;color:#6b7280;">No highlights${filt==='all'?' yet.':' for this filter.'}</div>`;
    return;
  }

  list.innerHTML = marks.map((m, i) => {
    const phrase = decodeURIComponent(m.getAttribute("data-phrase") || "") || (m.textContent || "").trim();
    const strong   = m.classList.contains("kwd-strong");
    const optional = m.classList.contains("kwd-optional");
    const external = m.classList.contains("kwd-external");
    const tier = external ? "External" : strong ? "Strong" : "Optional";
    const dot  = external ? "#10b981" : strong ? "#3b82f6" : "#f59e0b";
    return `
      <div class="kw-item" data-i="${i}">
        <span class="kw-dot" style="display:inline-block;width:8px;height:8px;border-radius:999px;background:${dot};margin-right:6px;"></span>
        <button class="kw-jump" title="Jump to highlight" style="font-size:12px;">${escapeHtml(phrase)}</button>
        <span class="qty" style="font-size:12px;color:#6b7280;">· ${tier}</span>
      </div>
    `;
  }).join("");

  Array.from(list.querySelectorAll(".kw-item")).forEach((row, idx) => {
    row.querySelector(".kw-jump")?.addEventListener("click", (e) => {
      e.preventDefault();
      const m = marks[idx];
      if (m) scrollToMark(m);
    });
  });
}

export function initEngineHighlightsUI({ onToggle, onUpdate }) {
  onToggleHighlight = typeof onToggle === "function" ? onToggle : null;
  onUpdateBadge     = typeof onUpdate === "function" ? onUpdate : null;

  document.getElementById("engineFilter")?.addEventListener("change", rebuildEngineHighlightsPanel);

  const toggle = document.getElementById("toggleHighlight");
  if (toggle) {
    toggle.addEventListener("change", () => {
      const enabled = !!toggle.checked;
      if (onToggleHighlight) onToggleHighlight(enabled);
      rebuildEngineHighlightsPanel();
    });
  }

  // first paint
  rebuildEngineHighlightsPanel();
}
