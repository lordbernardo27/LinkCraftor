// assets/js/editor/panels.js
import { getKeywords, getClassForWordToken } from "./detect.js";

const $ = (id) => document.getElementById(id);

function renderPanel(containerId, items, colorHex, groupKey){
  const box = $(containerId);
  const countEl = $(groupKey === "int" ? "countInt" : groupKey === "ext" ? "countExt" : "countSem");
  if (!box) return;
  if (!items || !items.length){
    box.innerHTML = "(no keywords yet)";
    if (countEl) countEl.textContent = "(0)";
    return;
  }
  const renderItem = (it)=>`
    <li class="kw-item">
      <span class="kw-dot" style="background:${colorHex}"></span>
      <button class="kw-jump" data-word="${it.word}" data-kind="${it.cls || ""}">${it.word}</button>
      <span class="qty">×${it.count}</span>
    </li>`;
  box.innerHTML = `<ul class="kw-list">${items.map(renderItem).join("")}</ul>`;
  if (countEl) countEl.textContent = `(${items.length})`;
}

export function updateDetected(){
  const viewer = $("doc-content");
  const rawText = viewer?.textContent || "";
  const kws = getKeywords(rawText);
  const groups = { int:[], ext:[], sem:[] };
  for (const k of kws){
    const cls = getClassForWordToken(k.word);
    const key = cls === "kwd-int" ? "int" : (cls === "kwd-ext" ? "ext" : "sem");
    groups[key].push({ word:k.word, count:k.count, cls });
  }
  const sortFn = (a,b)=> (b.count-a.count)||a.word.localeCompare(b.word);
  groups.int.sort(sortFn); groups.ext.sort(sortFn); groups.sem.sort(sortFn);
  renderPanel("detectedInt", groups.int, "#10b981", "int");
  renderPanel("detectedExt", groups.ext, "#f59e0b", "ext");
  renderPanel("detectedSem", groups.sem, "#6366f1", "sem");
}
