// assets/js/sidebar/link-resolution.js
// Renders the Link Resolution Panel by scanning the editor DOM.
// Resolved  = phrases already underlined (.lc-underlined)
// Unresolved = phrases still marked (mark.kwd / mark.kwd-int / mark.kwd-ext / mark.kwd-sem)
//
// It also exposes LR_rebuild() so other modules (IL modal, bulk autolink, etc.)
// can refresh the panel after changes.

function esc(s){
  return String(s ?? "").replace(/[&<>"']/g, m => ({
    "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"
  }[m]));
}

function collectResolutionFromDom(root){
  const res = {
    resolved: new Set(),   // phrases (decoded)
    unresolved: new Set(), // phrases (decoded)
    order: []              // stable display order
  };
  if (!root) return res;

  // 1) Collect unresolved phrases from engine marks
  //    This captures any keyword/phrase that the engine highlighted
  //    but which has NOT yet been linked.
  const markSel = "mark.kwd, mark.kwd-int, mark.kwd-ext, mark.kwd-sem";
  const marks = Array.from(root.querySelectorAll(markSel));
  for (const m of marks){
    const p = decodeURIComponent(m.getAttribute("data-phrase") || "");
    if (!p) continue;
    if (!res.unresolved.has(p)) {
      res.unresolved.add(p);
      res.order.push(p);
    }
  }

  // 2) Collect resolved phrases from underlined spans
  //    These are phrases that successfully found a target (manual or auto).
  const linked = Array.from(root.querySelectorAll("span.lc-underlined[data-phrase]"));
  for (const el of linked){
    const p = decodeURIComponent(el.getAttribute("data-phrase") || "");
    if (!p) continue;
    res.resolved.add(p);
    // If something got linked, it's no longer unresolved
    if (res.unresolved.has(p)) {
      res.unresolved.delete(p);
    }
    if (!res.order.includes(p)) res.order.push(p);
  }

  return res;
}

function jumpToPhrase(phrase){
  const root = document.getElementById("doc-content");
  if (!root || !phrase) return;

  const encoded = encodeURIComponent(phrase);

  // Prefer an unresolved mark first (so we can open the IL modal),
  // otherwise fall back to the already-linked span.
  let target = root.querySelector(`mark[data-phrase="${encoded}"]`)
            || root.querySelector(`span.lc-underlined[data-phrase="${encoded}"]`);
  if (!target) return;

  target.scrollIntoView({ behavior: "smooth", block: "center" });
  target.classList.add("flash");
  setTimeout(()=> target.classList.remove("flash"), 900);

  // If it's an unresolved mark, synthesize a click to open the IL modal
  if (target.tagName === "MARK") {
    const evt = new MouseEvent("click", { bubbles: true, cancelable: true, view: window });
    target.dispatchEvent(evt);
  }
}

function renderList(listEl, data, filter){
  if (!listEl) return;
  const items = [];

  for (const p of data.order){
    const isResolved = data.resolved.has(p);
    if (filter === "resolved" && !isResolved) continue;
    if (filter === "unresolved" && isResolved) continue;
    items.push({ phrase: p, resolved: isResolved });
  }

  if (!items.length){
    listEl.innerHTML = `<div style="font-size:12px;color:#6b7280;">No items.</div>`;
    return;
  }

  listEl.innerHTML = items.map(it => `
    <div class="lr-item"
         data-phrase="${encodeURIComponent(it.phrase)}"
         style="display:flex;align-items:center;gap:8px;padding:6px 8px;border:1px solid #e5e7eb;border-radius:8px;margin:6px 0;cursor:pointer;">
      <span class="lr-dot" aria-hidden="true"
            style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${it.resolved ? "#10b981" : "#ef4444"};"></span>
      <span class="lr-text" style="font-size:13px;">${esc(it.phrase)}</span>
    </div>
  `).join("");

  // Clicking an item jumps to first occurrence in the editor and flashes it
  listEl.querySelectorAll(".lr-item").forEach(el => {
    el.addEventListener("click", () => {
      const phrase = decodeURIComponent(el.getAttribute("data-phrase") || "");
      jumpToPhrase(phrase);
    });
  });
}

export function initLinkResolutionPanel(){
  const card   = document.getElementById("linkResolutionCard");
  const filter = document.getElementById("lrFilter");
  const list   = document.getElementById("lrList");
  if (!card || !filter || !list) return;

  // Save references for rebuilds
  card.__lr = { filter, list };

  // Initial render from current doc
  const data = collectResolutionFromDom(document.getElementById("doc-content"));
  renderList(list, data, filter.value);

  // Filter changes
  filter.addEventListener("change", () => {
    const dataNow = collectResolutionFromDom(document.getElementById("doc-content"));
    renderList(list, dataNow, filter.value);
  });
}

// Expose a simple rebuild hook for other modules (e.g., after link accept/reject)
// This can be called from IL modal, bulk auto-link, undo linked phrase, etc.
export function LR_rebuild(){
  const card = document.getElementById("linkResolutionCard");
  const ctx  = card?.__lr;
  if (!ctx) return;
  const { filter, list } = ctx;
  const data = collectResolutionFromDom(document.getElementById("doc-content"));
  renderList(list, data, filter.value);
}

// Optional: make it callable from non-module code
if (typeof window !== "undefined") {
  window.LR_rebuild = LR_rebuild;
}
