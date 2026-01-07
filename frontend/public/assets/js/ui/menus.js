// public/assets/js/ui/ilModal.js
// Internal Linking Modal with: multi-title/URL choices, required fields validation,
// duplicate link prevention (phrase+url), and underlined link result.

import { escapeHtml } from "../core/dom.js";

export function wireILModal({
  viewerEl,
  elements,
  linkedSet,
  saveLinkedSet,
  getSuggestionsForPhrase, // (phrase:string)=>{titles:string[], urls:string[]}
  isPairAlreadyLinked,     // (phrase:string, url:string)=>boolean
  recordLinkedPair,        // (phrase:string, url:string)=>void
  onAfterApply,
}) {
  const {
    ilModal, ilClose, ilCancel, ilApply, ilToast,
    ilKeyword, ilUrl, ilTitle, ilText, ilNewTab,
    ilAcceptUrl, ilRejectUrl, ilUrlStatus,
    ilAcceptTitle, ilRejectTitle, ilTitleStatus,
    ilSearch, ilResults, ilResultsList,
  } = elements;

  let currentMark = null;
  let currentPhrase = "";

  function openIL(markEl) {
    currentMark = markEl;
    currentPhrase = decodeURIComponent(markEl.getAttribute("data-phrase") || "").trim();
    if (ilKeyword) ilKeyword.textContent = currentPhrase;

    // Load candidates
    const picks = getSuggestionsForPhrase ? getSuggestionsForPhrase(currentPhrase) : { titles: [], urls: [] };
    const titles = Array.isArray(picks?.titles) ? picks.titles : [];
    const urls = Array.isArray(picks?.urls) ? picks.urls : [];

    // Prefill first options (if any)
    if (ilTitle) ilTitle.value = titles[0] || "";
    if (ilUrl) ilUrl.value = urls[0] || "";
    if (ilText) ilText.value = (markEl.textContent || "").trim();

    // Populate selection list
    renderResults(titles, urls);

    // Reset statuses
    if (ilUrlStatus) ilUrlStatus.textContent = "";
    if (ilTitleStatus) ilTitleStatus.textContent = "";
    if (ilToast) ilToast.textContent = "";

    validateApplyButton();

    if (ilModal) {
      ilModal.style.display = "flex";
      ilModal.setAttribute("aria-hidden", "false");
    }
  }

  function closeIL() {
    if (ilModal) {
      ilModal.style.display = "none";
      ilModal.setAttribute("aria-hidden", "true");
    }
    currentMark = null;
    currentPhrase = "";
    if (ilResults) { ilResults.style.display = "none"; }
    if (ilResultsList) { ilResultsList.innerHTML = ""; }
  }

  function validateApplyButton() {
    const ok =
      !!(ilText?.value || "").trim() &&
      !!(ilTitle?.value || "").trim() &&
      !!(ilUrl?.value || "").trim();

    if (ilApply) {
      ilApply.disabled = !ok;
      ilApply.title = ok ? "" : "Fill Link Text, Title/Topic, and URL";
    }
  }

  function renderResults(titles, urls) {
    if (!ilResults || !ilResultsList) return;

    const bufs = [];
    if (titles.length) {
      bufs.push(`<div class="il-result-item" style="background:#f9fafb;font-weight:600;">Matched Titles</div>`);
      for (const t of titles) {
        const safe = escapeHtml(t);
        bufs.push(`<div class="il-result-item" data-type="title" data-value="${safe}">${safe}</div>`);
      }
    }
    if (urls.length) {
      bufs.push(`<div class="il-result-item" style="background:#f9fafb;font-weight:600;">Matched URLs</div>`);
      for (const u of urls) {
        const safe = escapeHtml(u);
        bufs.push(`<div class="il-result-item" data-type="url" data-value="${safe}">${safe}</div>`);
      }
    }

    ilResultsList.innerHTML = bufs.join("");
    ilResults.style.display = bufs.length ? "block" : "none";
  }

  // click in suggestion list
  if (ilResultsList) {
    ilResultsList.addEventListener("click", (e) => {
      const item = e.target.closest(".il-result-item");
      if (!item) return;
      const kind = item.getAttribute("data-type");
      const val = item.getAttribute("data-value") || "";
      if (kind === "title" && ilTitle) ilTitle.value = val;
      if (kind === "url" && ilUrl) ilUrl.value = val;
      validateApplyButton();
    });
  }

  // Accept/Reject quick helpers
  if (ilAcceptUrl) ilAcceptUrl.addEventListener("click", () => { ilUrlStatus && (ilUrlStatus.textContent = "URL accepted"); });
  if (ilRejectUrl) ilRejectUrl.addEventListener("click", () => {
    ilUrlStatus && (ilUrlStatus.textContent = "URL cleared");
    if (ilUrl) ilUrl.value = "";
    validateApplyButton();
  });
  if (ilAcceptTitle) ilAcceptTitle.addEventListener("click", () => { ilTitleStatus && (ilTitleStatus.textContent = "Title accepted"); });
  if (ilRejectTitle) ilRejectTitle.addEventListener("click", () => {
    ilTitleStatus && (ilTitleStatus.textContent = "Title cleared");
    if (ilTitle) ilTitle.value = "";
    validateApplyButton();
  });

  // Validate on typing
  [ilUrl, ilTitle, ilText].forEach((el) => el && el.addEventListener("input", validateApplyButton));

  // Apply link
  if (ilApply) {
    ilApply.addEventListener("click", () => {
      const linkText = (ilText?.value || "").trim();
      const href = (ilUrl?.value || "").trim();
      const title = (ilTitle?.value || "").trim();
      const newTab = !!ilNewTab?.checked;

      if (!linkText || !href || !title) {
        ilToast && (ilToast.textContent = "Fill all fields");
        return;
      }

      // Prevent duplicate phrase+URL linkage
      if (isPairAlreadyLinked && isPairAlreadyLinked(currentPhrase, href)) {
        ilToast && (ilToast.textContent = "This phrase is already linked to that URL.");
        return;
      }

      // Replace the <mark> node with <a> (underlined)
      if (!currentMark || !viewerEl) return;
      const a = document.createElement("a");
      a.href = href;
      a.textContent = linkText;
      a.title = title;
      if (newTab) a.target = "_blank";
      a.style.textDecoration = "underline"; // visually underlined after link
      currentMark.parentNode.replaceChild(a, currentMark);

      // Record in sets
      linkedSet.add(currentPhrase);
      saveLinkedSet && saveLinkedSet();
      recordLinkedPair && recordLinkedPair(currentPhrase, href);

      // Done
      ilToast && (ilToast.textContent = "Linked");
      closeIL();
      onAfterApply && onAfterApply();
    });
  }

  // close & cancel
  if (ilClose) ilClose.addEventListener("click", closeIL);
  if (ilCancel) ilCancel.addEventListener("click", closeIL);

  return { openIL: openIL, closeIL: closeIL };
}
