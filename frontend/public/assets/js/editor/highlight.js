import { state } from "../core/state.js";
import { normalizePhrase, escapeRegExp } from "../core/utils.js";
import { INTERNAL_LIST } from "../data/buckets.js";
import { extractTitleFromDoc } from "../data/titles.js";

const badge = document.getElementById("highlightCountBadge");
const toggle = document.getElementById("toggleHighlight");
const viewer = document.getElementById("doc-content");

export function setHighlightToggle(){
  const saved = localStorage.getItem("linkcraftor_highlight_enabled_v1");
  state.highlightEnabled = saved === null ? true : saved === "true";
  if (toggle){
    toggle.checked = state.highlightEnabled;
    toggle.addEventListener("change", ()=>{
      state.highlightEnabled = !!toggle.checked;
      localStorage.setItem("linkcraftor_highlight_enabled_v1", String(state.highlightEnabled));
      highlightKeywords();
    });
  }
}
function phrasesForHighlighting(){
  const set = new Set();
  let currentTitleNorm = "";
  if (state.currentIndex>=0 && state.docs[state.currentIndex]){
    currentTitleNorm = normalizePhrase(extractTitleFromDoc(state.docs[state.currentIndex]));
  }
  state.TITLE_ALIAS_MAP.forEach((canonical, alias)=>{
    if (alias && canonical !== currentTitleNorm) set.add(alias);
  });
  for (const p of INTERNAL_LIST){
    const n = normalizePhrase(p); if (n) set.add(n);
  }
  return Array.from(set).sort((a,b)=> b.length-a.length);
}
function unwrapMarks(){
  if (!viewer) return;
  viewer.querySelectorAll("mark.kwd-int").forEach(m=>{
    const t=document.createTextNode(m.textContent||"");
    m.parentNode.replaceChild(t, m);
  });
}
function updateBadge(){
  if (!badge){ return; }
  badge.textContent = (!viewer || !state.highlightEnabled) ? "0" : String(viewer.querySelectorAll("mark.kwd-int").length);
}
export function highlightKeywords(){
  if (!viewer){ updateBadge(); return; }
  unwrapMarks();
  if (!state.highlightEnabled){ updateBadge(); return; }
  const phrases = phrasesForHighlighting(); if (!phrases.length){ updateBadge(); return; }

  const walker = document.createTreeWalker(viewer, NodeFilter.SHOW_TEXT, {
    acceptNode(node){
      if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      let p=node.parentNode;
      while(p && p!==viewer){
        if (p.nodeType===1 && (p.tagName==="A"||p.tagName==="MARK")) return NodeFilter.FILTER_REJECT;
        p=p.parentNode;
      }
      return NodeFilter.FILTER_ACCEPT;
    }
  });
  const nodes=[]; while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const tn of nodes){
    let text = tn.nodeValue, changed=false;
    for (const phrase of phrases){
      if (state.LINKED_SET.has(phrase)) continue;
      const rx = new RegExp(`\\b(${escapeRegExp(phrase).replace(/\s+/g,"\\s+")})\\b`, "gi");
      if (rx.test(text)){
        text = text.replace(rx, m=>`<mark class="kwd-int" data-phrase="${encodeURIComponent(phrase)}" tabindex="0">${m}</mark>`);
        changed=true;
      }
    }
    if (changed){
      const span=document.createElement("span"); span.innerHTML=text; tn.parentNode.replaceChild(span, tn);
    }
  }
  updateBadge();
}
