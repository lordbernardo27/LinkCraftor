// assets/js/features/buckets.js
// Buckets: highlighting + small settings UI. No globals; init with ctx.

import {
  loadBuckets as loadBucketsFromStore,
  saveBuckets as saveBucketsToStore,
  resetBuckets as resetBucketsInStore,
} from "../data/settings.js"; // adjust if your relative path differs (from app.js to features/)

function escRe(s){ return String(s).replace(/[.*+?^${}()|[\]\\]/g,"\\$&"); }
function norm(s){ return String(s||"").toLowerCase().trim().replace(/\s+/g," "); }
function $(id, root=document){ return root.getElementById(id); }
function makeBoundaryRx(phrase){
  const escaped = escRe(phrase).replace(/\s+/g, "\\s+");
  return new RegExp(`(^|[^\\p{L}\\p{N}])(${escaped})(?=$|[^\\p{L}\\p{N}])`, "giu");
}

// Colors (kept same look as before)
const CLR = {
  STRONG_BG:   "rgba(59,130,246,.18)",
  STRONG_IN:   "rgba(59,130,246,.45)",
  OPTIONAL_BG: "rgba(245,158,11,.22)",
  OPTIONAL_IN: "rgba(245,158,11,.48)",
  EXTERNAL_BG: "rgba(16,185,129,.18)",
  EXTERNAL_IN: "rgba(16,185,129,.45)",
};

let CTX = null; // { getViewerEl, isRejected, root }

// Public: read the buckets from store (used by right-panel filter)
export function getBucketMap(){
  const map = { strong: new Set(), optional: new Set(), external: new Set() };
  try {
    const b = loadBucketsFromStore() || {};
    const toN = (arr)=> (arr||[]).map(x=>norm(x)).filter(Boolean);

    // Back-compat aliases
    const strong   = b.strong   ?? b.internal ?? [];
    const optional = b.optional ?? b.semantic ?? [];
    const external = b.external ?? [];

    for (const w of toN(strong))   map.strong.add(w);
    for (const w of toN(optional)) map.optional.add(w);
    for (const w of toN(external)) map.external.add(w);
  } catch {}
  return map;
}

// Remove only bucket marks (keep engine .kwd)
export function unwrapBucketMarksOnly(){
  const viewerEl = CTX?.getViewerEl();
  if (!viewerEl) return;
  viewerEl.querySelectorAll("mark.kwd-int:not(.kwd), mark.kwd-ext:not(.kwd), mark.kwd-sem:not(.kwd)").forEach(m=>{
    const core = m.querySelector?.(".kw-core");
    const plain = (core?.textContent ?? m.textContent ?? "");
    m.parentNode.replaceChild(document.createTextNode(plain), m);
  });
}

/**
 * Create the ✓ / ✕ control bubble using DOM (no innerHTML).
 * Returns: <span class="kw-ctl">...</span>
 */
function buildControlsEl(){
  const ctl = document.createElement("span");
  ctl.className = "kw-ctl";
  ctl.setAttribute("aria-hidden", "true");
  ctl.style.position = "absolute";
  ctl.style.right = "-8px";
  ctl.style.top = "-8px";
  ctl.style.display = "flex";
  ctl.style.gap = "2px";
  ctl.style.opacity = "0";
  ctl.style.pointerEvents = "none";

  const mkBtn = (cls, title, borderColor, text) => {
    const b = document.createElement("button");
    b.className = `kw-btn ${cls}`;
    b.title = title;
    b.style.fontSize = "11px";
    b.style.width = "16px";
    b.style.height = "16px";
    b.style.borderRadius = "999px";
    b.style.border = `1px solid ${borderColor}`;
    b.style.color = borderColor;
    b.style.background = "#fff";
    b.style.cursor = "pointer";
    b.style.padding = "0";
    b.type = "button";
    b.textContent = text;
    return b;
  };

  ctl.appendChild(mkBtn("kw-accept", "Accept", "#10b981", "✓"));
  ctl.appendChild(mkBtn("kw-reject", "Reject", "#ef4444", "✕"));
  return ctl;
}

/**
 * Safely replace one text node with: [beforeText][markEl(core)][afterText]
 * No HTML parsing, no innerHTML.
 */
function replaceTextNodeWithMark(tn, beforeText, coreText, afterText, item){
  const frag = document.createDocumentFragment();

  if (beforeText) frag.appendChild(document.createTextNode(beforeText));

  const mark = document.createElement("mark");
  mark.className = item.cls;

  const isExternal = (item.type === "external");
  mark.dataset.mode = isExternal ? "external" : "internal";
  mark.dataset.phrase = encodeURIComponent(item.w);
  mark.tabIndex = 0;

  mark.style.position = "relative";
  mark.style.background = item.bg;
  mark.style.boxShadow = `0 -2px 0 ${item.inset} inset`;

  const coreSpan = document.createElement("span");
  coreSpan.className = "kw-core";
  coreSpan.textContent = coreText; // safe text only
  mark.appendChild(coreSpan);

  mark.appendChild(buildControlsEl());

  frag.appendChild(mark);

  if (afterText) frag.appendChild(document.createTextNode(afterText));

  tn.parentNode.replaceChild(frag, tn);
}

// Main: highlight buckets (now with ✓ / ✕ and hover bubble) — hardened (no innerHTML)
export function highlightBucketKeywords(){
  const viewerEl = CTX?.getViewerEl();
  if (!viewerEl) return;

  // Clean previous bucket marks
  unwrapBucketMarksOnly();

  const { strong, external, optional } = getBucketMap();
  const hasAny = (strong?.size||0) + (optional?.size||0) + (external?.size||0) > 0;
  if (!hasAny) return;

  const conf = [
    ...Array.from(strong||[]).map(w => ({ w, cls:"kwd-int", type:"internal", bg:CLR.STRONG_BG,    inset:CLR.STRONG_IN })),
    ...Array.from(optional||[]).map(w => ({ w, cls:"kwd-sem", type:"internal", bg:CLR.OPTIONAL_BG, inset:CLR.OPTIONAL_IN })),
    ...Array.from(external||[]).map(w => ({ w, cls:"kwd-ext", type:"external", bg:CLR.EXTERNAL_BG, inset:CLR.EXTERNAL_IN })),
  ].sort((a,b)=> b.w.length - a.w.length); // longer first

  const placed = { internal:false, external:false }; // show at most one per type to reduce clutter

  // Walk text nodes (avoid headings, existing marks, links)
  const walker = document.createTreeWalker(viewerEl, NodeFilter.SHOW_TEXT, {
    acceptNode(node){
      if(!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      let p=node.parentNode;
      while(p && p!==viewerEl){
        if(p.nodeType===1){
          if(p.tagName==='A' || p.tagName==='MARK' || p.classList?.contains('lc-underlined')) return NodeFilter.FILTER_REJECT;
          if(/^(H1|H2|H3|H4|H5|H6|NAV|ASIDE|HEADER|FOOTER)$/i.test(p.tagName)) return NodeFilter.FILTER_REJECT;
        }
        p=p.parentNode;
      }
      return NodeFilter.FILTER_ACCEPT;
    }
  });

  const nodes=[]; while(walker.nextNode()) nodes.push(walker.currentNode);

  for (const tn of nodes){
    if (placed.internal && placed.external) break;

    const text = tn.nodeValue;

    for (const item of conf){
      if (placed[item.type]) continue;

      // Respect rejections from app store
      if (CTX?.isRejected && CTX.isRejected(item.type, item.w)) continue;

      const rx = makeBoundaryRx(item.w);
      rx.lastIndex = 0;
      const hit = rx.exec(text);
      if (!hit) continue;

      const preLen = hit.index + (hit[1] ? hit[1].length : 0);
      const before = text.slice(0, preLen);
      const core   = hit[2];
      const after  = text.slice(hit.index + hit[0].length);

      replaceTextNodeWithMark(tn, before, core, after, item);

      placed[item.type] = true;
      break;
    }
  }
}

// Small Buckets UI wiring (Strong/Optional/External boxes)
function renderBucketsBoxes(root=document){
  const strongBox = $("strongBox", root), optionalBox = $("optionalBox", root), externalBox = $("externalBox", root);
  if (!strongBox || !optionalBox || !externalBox) return;
  const b = loadBucketsFromStore() || {};
  const strong   = b.strong   ?? b.internal ?? [];
  const optional = b.optional ?? b.semantic ?? [];
  const external = b.external ?? [];
  strongBox.value   = (Array.isArray(strong)   ? strong   : []).join("\n");
  optionalBox.value = (Array.isArray(optional) ? optional : []).join("\n");
  externalBox.value = (Array.isArray(external) ? external : []).join("\n");
}

// Public init
export function initBuckets(ctx){
  CTX = ctx || {};
  // Wire Save/Reset (if present)
  const root = CTX.root || document;
  const strongBox = $("strongBox", root), optionalBox = $("optionalBox", root), externalBox = $("externalBox", root);
  const saveBtn = $("saveBuckets", root), resetBtn = $("resetBuckets", root), toast = $("bucketsToast", root);

  const toastFn=(msg,ms=1200)=>{ if(!toast) return; toast.textContent=msg; setTimeout(()=> (toast.textContent=""), ms); };

  if (saveBtn && strongBox && optionalBox && externalBox){
    saveBtn.addEventListener("click", ()=>{
      const toList = (v)=> (v||"").split(/[\n,]+/).map(x=>x.trim()).filter(Boolean);
      const payload = {
        strong:   toList(strongBox.value),
        optional: toList(optionalBox.value),
        external: toList(externalBox.value),
        // back-compat mirrors
        internal: toList(strongBox.value),
        semantic: toList(optionalBox.value),
      };
      saveBucketsToStore(payload);
      highlightBucketKeywords(); // re-mark
      toastFn("Buckets saved");
    });
  }

  if (resetBtn){
    resetBtn.addEventListener("click", ()=>{
      resetBucketsInStore();
      renderBucketsBoxes(root);
      highlightBucketKeywords();
      toastFn("Buckets reset");
    });
  }

  renderBucketsBoxes(root);
}
