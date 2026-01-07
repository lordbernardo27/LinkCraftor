// assets/js/editor/editor-ui.js
import { state, saveState } from "../core/state.js";
import { renderDoc, goPrevDoc, goNextDoc } from "./render.js";
import { debounce } from "../core/utils.js";
import { highlightKeywords } from "./highlight.js";
import { updateDetected } from "./panels.js";

const $ = (id) => document.getElementById(id);
const viewer = $("doc-content");

const updateDetectedDebounced = debounce(() => { updateDetected(); highlightKeywords(); }, 200);

function ensureViewerFocus() {
  if (!viewer) return false;
  const sel = window.getSelection();
  if (!sel || sel.rangeCount === 0) { viewer.focus(); return true; }
  const range = sel.getRangeAt(0);
  const node = range.commonAncestorContainer.nodeType === 1
    ? range.commonAncestorContainer
    : range.commonAncestorContainer.parentNode;
  if (!viewer.contains(node)) { viewer.focus(); return true; }
  return true;
}
function exec(name, value = null) {
  if (!ensureViewerFocus()) return;
  try { document.execCommand(name, false, value); } catch (e) { console.warn("execCommand failed:", name, e); }
  persistEditor();
}

function persistEditor(){
  if (state.currentIndex >= 0 && state.docs[state.currentIndex]) {
    const d = state.docs[state.currentIndex];
    d.text = viewer?.textContent || "";
    d.html = viewer?.innerHTML || "";
    saveState();
    updateDetectedDebounced();
  }
}

export function wireToolbar(){
  const toolbar = $("toolbar");
  const headingSelect = $("headingSelect");
  const fontSizeSelect = $("fontSizeSelect");
  const alignSelect = $("alignSelect");
  const btnLink = $("btnLink");
  const btnOpenLink = $("btnOpenLink");
  const btnHR = $("btnHR");
  const btnImage = $("btnImage");
  const tableSelect = $("tableSelect");
  const btnChecklist = $("btnChecklist");
  const btnPrevDoc = $("btnPrevDoc");
  const btnNextDoc = $("btnNextDoc");

  if (toolbar){
    toolbar.addEventListener("click", (e)=>{
      const btn = e.target.closest("button.btn");
      if (!btn) return;
      const cmd = btn.getAttribute("data-cmd");
      if (!cmd) return;
      exec(cmd);
    });
  }
  if (headingSelect) headingSelect.addEventListener("change", ()=>{ const val = headingSelect.value || "P"; exec("formatBlock", val === "P" ? "P" : val); });
  if (fontSizeSelect) fontSizeSelect.addEventListener("change", ()=> exec("fontSize", fontSizeSelect.value));
  if (alignSelect) alignSelect.addEventListener("change", ()=>{
    const v = alignSelect.value;
    if (v === "left") exec("justifyLeft");
    else if (v === "center") exec("justifyCenter");
    else if (v === "right") exec("justifyRight");
    else if (v === "justify") exec("justifyFull");
  });

  function getLinkAtSelection() {
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return null;
    let node = sel.anchorNode;
    if (node && node.nodeType === Node.TEXT_NODE) node = node.parentNode;
    while (node && node !== viewer) { if (node.tagName === "A") return node; node = node.parentNode; }
    return null;
  }

  if (btnLink) {
    btnLink.addEventListener("click", ()=>{
      let url = prompt("Enter URL (https://…):", "http://127.0.0.1:8001/index.html");
      if (!url) return;
      if (!/^https?:\/\//i.test(url)) url = "http://" + url;
      try {
        const u = new URL(url);
        const isLocal = ["127.0.0.1","localhost","::1"].includes(u.hostname);
        if (isLocal && (!u.pathname || u.pathname === "/")) { u.pathname = "/index.html"; url = u.toString(); }
      } catch {}
      exec("createLink", url);
    });
  }
  if (btnOpenLink) {
    btnOpenLink.addEventListener("click", ()=>{
      const a = getLinkAtSelection();
      if (a?.href) {
        let url = a.href;
        try {
          const u = new URL(url);
          const isLocal = ["127.0.0.1","localhost","::1"].includes(u.hostname);
          if (isLocal && (!u.pathname || u.pathname === "/")) { u.pathname = "/index.html"; url = u.toString(); }
        } catch {}
        window.open(url, "_blank", "noopener,noreferrer");
      } else {
        alert("No link found at the selection.");
      }
    });
  }
  if (btnHR) btnHR.addEventListener("click", ()=> exec("insertHorizontalRule"));
  if (btnImage){
    btnImage.addEventListener("click", ()=>{
      let url = prompt("Image URL (https://…):", "https://");
      if (!url) return;
      if (!/^https?:\/\//i.test(url)) url = "https://" + url;
      exec("insertImage", url);
    });
  }
  if (tableSelect) {
    tableSelect.addEventListener("change", ()=>{
      const val = tableSelect.value;
      if (!val) return;
      const [r,c] = val.split("x").map(Number);
      insertTable(r|0, c|0);
      tableSelect.value = "";
    });
  }
  if (btnChecklist){
    btnChecklist.addEventListener("click", ()=>{
      if (!ensureViewerFocus()) return;
      const sel = window.getSelection();
      if (!sel || sel.rangeCount === 0) return;
      const text = sel.toString().trim();
      const lines = text ? text.split(/\r?\n/).filter(Boolean) : ["Item 1","Item 2","Item 3"];
      const items = lines.map(l=>`<li><label style="display:flex;gap:8px;align-items:center;"><input type="checkbox"> <span>${l}</span></label></li>`).join("");
      const html = `<ul class="checklist">${items}</ul>`;
      document.execCommand("insertHTML", false, html);
      const styleId = "checklist-style";
      if (!document.getElementById(styleId)) {
        const st=document.createElement("style");
        st.id=styleId; st.textContent = `.checklist{list-style:none;padding-left:0;margin-left:0;} .checklist li{margin:4px 0;}`;
        document.head.appendChild(st);
      }
      persistEditor();
    });
  }

  if (btnPrevDoc) btnPrevDoc.addEventListener("click", goPrevDoc);
  if (btnNextDoc) btnNextDoc.addEventListener("click", goNextDoc);

  if (viewer) viewer.addEventListener("input", persistEditor);
}

function insertTable(rows, cols){
  rows = Math.max(1, rows); cols = Math.max(1, cols);
  let html = '<table style="border-collapse:collapse;width:100%;">';
  for (let r=0; r<rows; r++){
    html += "<tr>";
    for (let c=0; c<cols; c++){
      html += '<td style="border:1px solid #e5e7eb;padding:6px;">&nbsp;</td>';
    }
    html += "</tr>";
  }
  html += "</table>";
  document.execCommand("insertHTML", false, html);
}
