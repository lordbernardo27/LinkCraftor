// assets/js/ui/stopwords.js
// Sidebar: Stopwords — saves to store and notifies app via a custom event.

import {
  loadStopwords as loadStopwordsFromStore,
  saveStopwords as saveStopwordsToStore,
  resetStopwords as resetStopwordsInStore,
} from "../data/settings.js";

function fillBox() {
  const box = document.getElementById("stopwordsBox");
  if (!box) return;
  const custom = loadStopwordsFromStore();
  box.value = (custom || []).join("\n");
}

function toastMsg(msg) {
  const t = document.getElementById("stopwordsToast");
  if (!t) return;
  t.textContent = msg;
  setTimeout(() => (t.textContent = ""), 1200);
}

export function initStopwordsUI() {
  const box   = document.getElementById("stopwordsBox");
  const save  = document.getElementById("saveStopwords");
  const reset = document.getElementById("resetStopwords");

  if (!box || !save || !reset) return;

  // initial paint
  fillBox();

  save.addEventListener("click", () => {
    const list = (box.value || "")
      .split(/[\n,]+/)
      .map(w => String(w || "").toLowerCase().trim())
      .filter(Boolean);
    saveStopwordsToStore(list);
    window.dispatchEvent(new CustomEvent("lc:stopwords-updated", { detail: { list } }));
    toastMsg("Stopwords saved");
  });

  reset.addEventListener("click", () => {
    resetStopwordsInStore();
    fillBox();
    window.dispatchEvent(new CustomEvent("lc:stopwords-updated", { detail: { reset: true } }));
    toastMsg("Defaults restored");
  });
}
