// assets/js/features/il-modal.js
// Isolates the Internal/External Link (IL) modal logic and mark interactions.
// No globals: everything is passed via a context object to initILModal().

/**
 * initILModal(ctx)
 * Wires up the Inline Linking (IL) modal + mark hover controls.
 *
 * Required ctx fields:
 *  - root: Document or HTMLElement used for getElementById (usually document)
 *  - getViewerEl(): HTMLElement
 *  - ensureReferencesModule(): Promise<{ getExternalReferences?(anchor, opts) }|null>
 *  - computeFinalUrl(kind, topicId, title, url): string
 *  - slugifyHeading(str): string
 *  - findEngineSuggestionsForPhrase(phrase): Array<{title,url,topicId,kind,tier,score}>
 *  - rejectPhrase(phrase, type): void
 *  - unwrapMark(markEl): TextNode
 *  - underlineLinkedPhrases(): void
 *  - highlightBucketKeywords(): void
 *  - updateHighlightBadge(): void
 *  - rebuildEngineHighlightsPanel(): void
 *  - saveLinkedSet(): void
 *  - state: {
 *      LINKED_SET: Set<string>,
 *      LINKED_MAP: Map<string, Set<string>>,
 *      APPLIED_LINKS: Array<any>,
 *      setCurrentMark(el|null): void,
 *      setCurrentPhrase(str): void,
 *      getCurrentMark(): Element|null,
 *      getCurrentPhrase(): string
 *    }
 */
export function initILModal(ctx) {
  const $ = (id) => ctx.root.getElementById(id);
  const escapeHtml = (s)=> String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  const escRe      = (s)=> String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const norm       = (s)=> String(s||"").toLowerCase().trim().replace(/\s+/g, " ");

  // ========= Core IL modal nodes (ensure these exist) =========
  const ilModal       = $("ilModal");
  const ilTitle       = $("ilTitle");
  const ilTitleList   = $("ilTitleList");
  const ilUrl         = $("ilUrl");
  const ilUrlList     = $("ilUrlList");
  const ilKeyword     = $("ilKeyword");
  const ilApply       = $("ilApply");
  const ilCancel      = $("ilCancel");
  const ilClose       = $("ilClose");
  const ilToast       = $("ilToast");
  const ilSourceLabel = $("ilSourceLabel");

  // ========= Extended UI (Top Targets, domain hint, etc.) =========
  const ilDomain            = $("ilDomain");          // optional domain hint (may be null)
  const ilTTUPrimary        = $("ilTTUPrimary");      // Top Targets (Strong)
  const ilTTUPrimaryList    = $("ilTTUPrimaryList");
  const ilTTUPrimaryStatus  = $("ilTTUPrimaryStatus");
  const ilTTUOptional       = $("ilTTUOptional");     // Top Targets (Optional)
  const ilTTUOptionalList   = $("ilTTUOptionalList");
  const ilTTUOptionalStatus = $("ilTTUOptionalStatus");
  const ilNewTab            = $("ilNewTab");          // (presentational; not enforced here)
  const ilText              = $("ilText");            // link text
  const ilSearch            = $("ilSearch");          // internal finder
  const ilResults           = $("ilResults");         // internal finder panel
  const ilResultsList       = $("ilResultsList");     // internal finder list

  // ========= External bits =========
  const extRow         = $("extRow");
  const extReferences  = $("extReferences");
  const extAdvancedBtn = $("extAdvancedBtn");

  let IL_MODE = "internal"; // or "external"

  // ------------------------------------------------------------
  // Helpers
  // ------------------------------------------------------------

  function setILMode(mode){
    IL_MODE = mode;
    const internalOn = (mode === "internal");

    const row = (el)=> el && el.closest ? el.closest(".il-row") : null;
    const rowTitle  = row(ilTitle);
    const rowUrl    = row(ilUrl);
    const rowText   = row(ilText);
    const rowSearch = row(ilSearch);

    if (rowTitle)  rowTitle.style.display  = internalOn ? "" : "none";
    if (rowUrl)    rowUrl.style.display    = internalOn ? "" : "none";
    if (rowText)   rowText.style.display   = internalOn ? "" : "none";
    if (rowSearch) rowSearch.style.display = internalOn ? "" : "none";
    if (extRow)    extRow.hidden = internalOn;

    [ilTitle, ilUrl, ilText, ilSearch].forEach(el=>{ if(el) el.disabled = !internalOn; });
    if (extReferences) extReferences.disabled = internalOn;

    ilApply?.setAttribute("disabled","true");
    if (ilToast) ilToast.textContent = "";

    // Hide/show Top-Targets groups depending on mode
    if (ilTTUPrimary)  ilTTUPrimary.style.display  = internalOn ? "" : "none";
    if (ilTTUOptional) ilTTUOptional.style.display = internalOn ? "" : "none";
  }

  function makeBoundaryRx(phrase){
    const escaped = escRe(phrase).replace(/\s+/g, "\\s+");
    return new RegExp(`(^|[^\\p{L}\\p{N}])(${escaped})(?=$|[^\\p{L}\\p{N}])`, "giu");
  }

  function fillDatalist(listEl, items, key){
    if(!listEl) return;
    listEl.innerHTML = "";
    const uniq = new Set();
    for(const it of (items || [])){
      const v = it[key];
      if(!v || uniq.has(v)) continue;
      uniq.add(v);
      const opt = document.createElement("option");
      opt.value = v;
      listEl.appendChild(opt);
    }
  }

  // Only allow cross-document targets: exclude same-doc headings and in-page anchors
  function isCrossDoc(it){
    if (!it) return false;
    if (String(it.kind||"").toLowerCase() === "same-doc") return false;
    if (it.url && String(it.url).trim().startsWith("#")) return false;
    return true;
  }

  // Read imported topics safely from app.js (sitemap/backup/draft/external)
  function getImportedTopicsSafe(){
    try {
      const out = window.LC_getImportedTopics ? window.LC_getImportedTopics() : [];
      return Array.isArray(out) ? out : [];
    } catch {
      return [];
    }
  }

  // ====== BEST-FIT suggestion builder (NO hard priority: sitemap>backup>engine>draft) ======

  function scoreLexicalMatch(normPhrase, title){
    const t = norm(title || "");
    if (!t || !normPhrase) return 0;

    let score = 0;

    if (t === normPhrase) {
      // exact title match
      score += 120;
    } else if (t.includes(normPhrase)) {
      // phrase is contained in title
      score += 80;
    } else if (normPhrase.includes(t)) {
      // title is contained in phrase
      score += 50;
    }

    const pTokens = normPhrase.split(" ").filter(Boolean);
    const tTokens = t.split(" ").filter(Boolean);
    const overlap = pTokens.filter(w => tTokens.includes(w)).length;
    score += overlap * 10;

    return score;
  }

  // Build "best-fit" candidate list from engine suggestions + imported topics
  function buildBestFitSuggestions(phrase, engineSuggestions){
    const normPhrase = norm(phrase);
    const out  = [];
    const seen = new Set();

    function pushCandidate(rec){
      const key = `${norm(rec.title || "")}|${(rec.url || "").trim()}`;
      if (seen.has(key)) return;
      seen.add(key);
      out.push(rec);
    }

    // 1) Engine suggestions (already have some score/tier/kind from engine)
    for (const s of (engineSuggestions || [])){
      if (!isCrossDoc(s)) continue;

      const baseScore = typeof s.score === "number" ? s.score : 0;
      let score = baseScore;

      score += scoreLexicalMatch(normPhrase, s.title);

      const kind = String(s.kind || "").toLowerCase();
      if (kind === "internal" || kind === "published") score += 8;
      if (kind === "semantic") score += 4;

      pushCandidate({
        ...s,
        score
      });
    }

    // 2) Imported topics (sitemap/backup/draft) – treated equally, only lexical decides
    const imported = getImportedTopicsSafe().filter(rec =>
      rec &&
      rec.url &&
      rec.title &&
      rec.source !== "external"  // keep external URLs for external mode only
    );

    for (const r of imported){
      const s = String(r.source || "").toLowerCase();
      let score = scoreLexicalMatch(normPhrase, r.title);

      // light boost if the source looks more "official", but still minor vs lexical
      if (s === "sitemap") score += 6;
      if (s === "backup")  score += 4;
      if (s === "draft")   score += 2;

      pushCandidate({
        title:   r.title || "",
        url:     r.url   || "",
        topicId: `imp:${s}:${r.id || r.url || r.title}`,
        kind:    s || "imported",
        score
      });
    }

    // Sort purely by score (best fit first)
    out.sort((a,b)=> (b.score || 0) - (a.score || 0));

    // Derive tier from score (used by Top Targets + UI)
    out.forEach((item, idx)=>{
      const s = item.score || 0;
      if (s >= 140 || idx === 0) {
        item.tier = "high";
      } else if (s >= 80) {
        item.tier = "mid";
      } else {
        item.tier = "low";
      }
    });

    return out;
  }

  // External fallback:
  // If no auto-suggested external references are available,
  // use imported External URL list (source: 'external') as options.
  function fillExternalFromImportsIfEmpty(phrase){
    if (!extReferences) return;

    // If we already have real options with URLs, do nothing.
    const hasReal =
      Array.from(extReferences.options || []).some(opt => (opt.value || "").trim());

    if (hasReal) return;

    const imported = getImportedTopicsSafe()
      .filter(r => r.source === "external" && r.url);

    if (!imported.length){
      // Ensure there's at least a clear "no sources" message
      extReferences.innerHTML = "";
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "No external URLs available";
      extReferences.appendChild(opt);
      return;
    }

    // Optional: light phrase-matching so list is relevant
    const q = norm(phrase || "");
    const scored = imported.map(r => {
      const t = norm(r.title || "");
      const u = norm(r.url || "");
      const hit = (q && (t.includes(q) || u.includes(q))) ? 1 : 0;
      return { rec: r, score: hit };
    }).sort((a,b)=> b.score - a.score);

    extReferences.innerHTML = "";
    for (const { rec } of scored){
      const opt = document.createElement("option");
      opt.value = rec.url;
      opt.textContent = rec.title
        ? `${rec.title} — imported`
        : rec.url;
      extReferences.appendChild(opt);
    }
  }

  async function populateExternalReferences(phrase){
    if (!extReferences) return;
    extReferences.innerHTML = "";
    const api = await ctx.ensureReferencesModule();
    let list = [];
    try {
      if (api?.getExternalReferences) {
        list = await api.getExternalReferences(phrase, { limit: 16 });
      }
    } catch {
      list = [];
    }

    // Do NOT default to Wikipedia-only.
// Show all results sorted by score; if you want wiki last, we push it down.
const source = Array.isArray(list) ? list.slice() : [];

if (!source.length){
  const opt = document.createElement("option");
  opt.value = "";
  opt.textContent = "No references available";
  extReferences.appendChild(opt);
  return;
}

// Sort by score (desc), but push Wikipedia to the bottom
console.log("[ILModal] external refs BEFORE sort:", source);
source.sort((a,b)=> {
  const aWiki = String(a?.url||"").toLowerCase().includes("wikipedia.org");
  const bWiki = String(b?.url||"").toLowerCase().includes("wikipedia.org");
  if (aWiki !== bWiki) return aWiki ? 1 : -1; // wiki last
  return (b.score||0) - (a.score||0);
});

for (const r of source.slice(0,12)){
  const opt = document.createElement("option");
  opt.value = r.url || "";
  const labelDom = r.domainRoot || r.domain || "";
  opt.textContent = r.title ? `${r.title} — ${labelDom}` : (r.url||"");
  opt.dataset.title    = r.title || "";
  opt.dataset.provider = labelDom || "";
  opt.dataset.refId    = r.id || "";
  extReferences.appendChild(opt);
}

}

  function validateILFieldsSilent(){
    if (IL_MODE === "external"){
      const v = (extReferences?.value||"").trim();
      return !!v;
    }
    const u = (ilUrl?.value||"").trim();
    const t = (ilTitle?.value||"").trim();
    const x = (ilText?.value||"").trim();
    if (!t || !x) return false;

    if (u){
      try {
        if (!u.startsWith("#")) new URL(u);
      } catch {
        return false;
      }
    }

    const key = norm(ctx.state.getCurrentPhrase());
    const set = ctx.state.LINKED_MAP.get(key);
    if (set && set.has(u || t)) return false; // already linked to this target
    return true;
  }

  function replaceMarkedWithUnderline(phrase, meta){
    const viewerEl = ctx.getViewerEl();
    if(!viewerEl) return null;

    const target = ctx.state.getCurrentMark();

    const applyAttrs = (el, coreText) => {
      el.className = "lc-underlined";
      el.style.textDecoration = "underline";
      el.setAttribute("data-phrase", encodeURIComponent(coreText || phrase));
      if (meta?.topicId) el.setAttribute("data-topic-id", meta.topicId);
      if (meta?.kind)    el.setAttribute("data-kind", meta.kind);
      if (meta?.url)     el.setAttribute("data-url", meta.url);
      if (meta?.title)   el.setAttribute("data-title", meta.title);
    };

    // If we still have the original <mark>, replace it directly
    if (target && target.parentNode){
      const core = target.querySelector?.(".kw-core");
      const visibleText = (core?.textContent ?? phrase).trim();
      const span = document.createElement("span");
      applyAttrs(span, visibleText);
      span.textContent = visibleText;
      target.parentNode.replaceChild(span, target);
      return span;
    }

    // Otherwise, walk the viewer and replace the first boundary-matching text node
    const walker = document.createTreeWalker(viewerEl, NodeFilter.SHOW_TEXT, null);
    const rx = makeBoundaryRx(phrase);
    while (walker.nextNode()){
      const tn = walker.currentNode;
      rx.lastIndex = 0;
      const m = rx.exec(tn.nodeValue || "");
      if (m){
        const before   = tn.nodeValue.slice(0, m.index + (m[1] ? m[1].length : 0));
        const coreText = m[2];
        const after    = tn.nodeValue.slice(m.index + m[0].length);
        const outer = document.createElement("span");
        const final = document.createElement("span");
        applyAttrs(final, coreText);
        final.textContent = coreText;
        outer.innerHTML = `${escapeHtml(before)}${final.outerHTML}${escapeHtml(after)}`;
        tn.parentNode.replaceChild(outer, tn);
        return outer.querySelector("span.lc-underlined");
      }
    }
    return null;
  }

  // ======= Entity/Content-aware: "Top Targets" in the modal =======
  function populateTTUFromSuggestions(suggestions){
    if (!ilTTUPrimaryList || !ilTTUOptionalList) return;

    if (!suggestions || !suggestions.length) {
      ilTTUPrimaryList.innerHTML  = "";
      ilTTUOptionalList.innerHTML = "";
      if (ilTTUPrimaryStatus)  ilTTUPrimaryStatus.textContent  = "No strong matches";
      if (ilTTUOptionalStatus) ilTTUOptionalStatus.textContent = "No optional matches";
      return;
    }

    const strong   = suggestions.filter(s=> s.tier === "high");
    const optional = suggestions.filter(s=> s.tier !== "high");

    if (ilTTUPrimaryList) {
      ilTTUPrimaryList.innerHTML = strong.slice(0, 6).map(s => `
        <div class="ttu-item" data-title="${escapeHtml(s.title||'')}" data-url="${escapeHtml(s.url||'')}">
          <div class="ttu-title">${escapeHtml(s.title||"(no title)")}</div>
          <div class="ttu-url">${escapeHtml(s.url||"(no url)")}</div>
        </div>
      `).join("");
      if (ilTTUPrimaryStatus) ilTTUPrimaryStatus.textContent = strong.length ? "" : "None";
    }

    if (ilTTUOptionalList) {
      ilTTUOptionalList.innerHTML = optional.slice(0, 10).map(s => `
        <div class="ttu-item" data-title="${escapeHtml(s.title||'')}" data-url="${escapeHtml(s.url||'')}">
          <div class="ttu-title">${escapeHtml(s.title||"(no title)")}</div>
          <div class="ttu-url">${escapeHtml(s.url||"(no url)")}</div>
        </div>
      `).join("");
      if (ilTTUOptionalStatus) ilTTUOptionalStatus.textContent = optional.length ? "" : "None";
    }

    const wire = (root) => {
      root?.querySelectorAll(".ttu-item")?.forEach(el=>{
        el.addEventListener("click", ()=>{
          const t = el.getAttribute("data-title")||"";
          const u = el.getAttribute("data-url")||"";
          if (ilTitle) ilTitle.value = t;
          if (ilUrl)   ilUrl.value   = u;
          if (validateILFieldsSilent()) ilApply?.removeAttribute("disabled");
          showDomainHint(u);
        });
      });
    };
    wire(ilTTUPrimary);
    wire(ilTTUOptional);
  }

  // ======= Small helper to show a domain hint beside the URL (optional) =======
  function showDomainHint(url){
    if (!ilDomain) return;
    try {
      if (!url || url.startsWith("#")) { ilDomain.textContent = ""; return; }
      const h = new URL(url).hostname;
      ilDomain.textContent = h;
    } catch {
      ilDomain.textContent = "";
    }
  }

  function setSourceLabel(kind){
    if (!ilSourceLabel) return;
    if (!kind) {
      ilSourceLabel.textContent = "";
      return;
    }

    const k = String(kind).toLowerCase();
    let txt = "";

    if (k === "sitemap")          txt = "Source: Sitemap";
    else if (k === "backup")      txt = "Source: Backup (CSV/TXT)";
    else if (k === "draft")       txt = "Source: Draft map";
    else if (k === "external")    txt = "Source: External list";
    else if (k === "same-doc")    txt = "Source: This document";
    else if (k.startsWith("imp:"))txt = "Source: Imported";
    else                          txt = "Source: Internal suggestions";

    ilSourceLabel.textContent = txt;
  }

  // ------------------------------------------------------------
  // Open / Close modal
  // ------------------------------------------------------------

  async function openIL(phrase, markEl, forceMode){
    // Remember what was clicked
    ctx.state.setCurrentMark(markEl || null);
    ctx.state.setCurrentPhrase(phrase || "");

    // Snapshot what the suggestion was when the modal opened (for EDITED vs ACCEPTED)
try { markEl && markEl.setAttribute("data-orig-url", String(markEl.getAttribute("data-url") || "").trim()); } catch {}
try { markEl && markEl.setAttribute("data-orig-title", String(markEl.getAttribute("data-title") || "").trim()); } catch {}


    if (ilKeyword) ilKeyword.textContent = phrase || "";

    const isExternalMark = !!(
      markEl?.classList?.contains("kwd-external") ||
      markEl?.classList?.contains("kwd-ext") ||
      markEl?.getAttribute("data-mode") === "external"
    );

    // Decide mode: forced, or based on mark type
    setILMode(forceMode ? forceMode : (isExternalMark ? "external" : "internal"));

    if (IL_MODE === "internal") {
      const currPhrase = ctx.state.getCurrentPhrase();
      const engineRaw  = ctx.findEngineSuggestionsForPhrase(currPhrase) || [];

      // Best-fit from engine + imported topics
      const combined = buildBestFitSuggestions(currPhrase, engineRaw);
      const cross    = combined.filter(isCrossDoc);

      // ⭐ Internal routing: prefer internal, then semantic, never external for prefill
      const internalOnly = cross.filter(s => {
        const k = String(s.kind || "").toLowerCase();
        return k === "internal" || k === "published";
      });

      const semanticOnly = cross.filter(s => {
        const k = String(s.kind || "").toLowerCase();
        return k === "semantic";
      });

      const pool =
        internalOnly.length
          ? internalOnly
          : (semanticOnly.length
              ? semanticOnly
              // fallback: any non-external cross-doc
              : cross.filter(s => (String(s.kind||"").toLowerCase() !== "external")));

      // Fill datalists from this pool
      fillDatalist(ilTitleList, pool, "title");
      fillDatalist(ilUrlList,   pool.filter(s => s.url), "url");

      // Pick best suggestion (already sorted by score, so take first)
      const pick = pool[0] || null;

      if (ilTitle) ilTitle.value = pick ? (pick.title || "") : "";
      if (ilUrl)   ilUrl.value   = pick ? (pick.url   || "") : "";
      if (ilText)  ilText.value  = currPhrase || "";

      // Top Targets displays the same pool (internal-first, semantic fallback)
      populateTTUFromSuggestions(pool);
      showDomainHint(ilUrl?.value || "");

      // Label: use suggestion kind if present, else "Internal suggestions"
      setSourceLabel(
        pick
          ? (pick.kind || "Internal suggestions")
          : ""
      );

      // Enable Apply if we have a valid prefilled combo; otherwise keep disabled
      if (pick && validateILFieldsSilent()) {
        ilApply?.removeAttribute("disabled");
      } else {
        ilApply?.setAttribute("disabled", "true");
      }

    } else {
      // -------- EXTERNAL MODE --------
      if (extReferences) {
        // 1) Prefer baked suggestions from the mark itself (if present)
        if (markEl && (markEl.getAttribute("data-suggestions") || "").length > 0) {
          extReferences.innerHTML = "";
          let list = [];
          try {
            list = JSON.parse(markEl.getAttribute("data-suggestions") || "[]");
          } catch {
            list = [];
          }

          if (!Array.isArray(list) || !list.length) {
            const opt = document.createElement("option");
            opt.value = "";
            opt.textContent = "No suggestions available";
            extReferences.appendChild(opt);
          } else {
            for (const r of list) {
              const opt = document.createElement("option");
              opt.value = r.url || "";
              opt.textContent = r.title
                ? `${r.title} — ${r.domainRoot || r.domain || ""}`
                : (r.url || "");
              opt.dataset.title    = r.title || "";
              opt.dataset.provider = r.domainRoot || r.domain || "";
              extReferences.appendChild(opt);
            }
          }

        } else {
          // 2) Otherwise, try engine/remote external references (e.g. Wikipedia)
          await populateExternalReferences(phrase);
        }

        // 3) If still nothing usable, fallback to imported External URL list (csv/txt)
        //    This only looks at source:'external' and does NOT affect internal mode.
        fillExternalFromImportsIfEmpty(phrase);
      }

      setSourceLabel("external");
    }

    // Enable Apply if a valid state; otherwise disabled
    if (validateILFieldsSilent()) {
      ilApply?.removeAttribute("disabled");
    } else {
      ilApply?.setAttribute("disabled", "true");
    }

    // Clear toast; open modal
    if (ilToast) ilToast.textContent = "";
    if (ilModal) ilModal.style.display = "flex";
  }

  function closeIL(){
    if (ilModal) ilModal.style.display = "none";
    ctx.state.setCurrentMark(null);
    ctx.state.setCurrentPhrase("");
    if (ilResults)     ilResults.style.display = "none";
    if (ilResultsList) ilResultsList.innerHTML = "";
    if (ilSourceLabel) ilSourceLabel.textContent = "";
  }

  // ------------------------------------------------------------
  // Inputs validation + events
  // ------------------------------------------------------------

  ["input","change"].forEach(evt=>{
    ilUrl?.addEventListener(evt, ()=>{
      showDomainHint(ilUrl.value||"");
      if (validateILFieldsSilent()) ilApply?.removeAttribute("disabled");
      else ilApply?.setAttribute("disabled","true");
    });
    ilTitle?.addEventListener(evt, ()=>{
      if (validateILFieldsSilent()) ilApply?.removeAttribute("disabled");
      else ilApply?.setAttribute("disabled","true");
    });
    ilText?.addEventListener(evt,  ()=>{
      if (validateILFieldsSilent()) ilApply?.removeAttribute("disabled");
      else ilApply?.setAttribute("disabled","true");
    });
    extReferences?.addEventListener(evt, ()=>{
      showDomainHint(extReferences.value||"");
      if (validateILFieldsSilent()) ilApply?.removeAttribute("disabled");
      else ilApply?.setAttribute("disabled","true");
    });
  });

  // Enter-to-apply (QoL)
  [ilTitle, ilUrl, ilText, extReferences].forEach(el=>{
    el?.addEventListener("keydown", (e)=>{
      if (e.key === "Enter" && validateILFieldsSilent()) {
        e.preventDefault();
        ilApply?.click();
      }
    });
  });

  // ======= Internal search within modal =======
  ilSearch?.addEventListener("input", ()=>{
    if (IL_MODE === "external") return;
    const q    = (ilSearch.value||"").toLowerCase().trim();
    const base = buildBestFitSuggestions(
      ctx.state.getCurrentPhrase(),
      ctx.findEngineSuggestionsForPhrase(ctx.state.getCurrentPhrase()) || []
    );
    const filtered = q
      ? base.filter(it =>
          (it.title||"").toLowerCase().includes(q) ||
          (it.url||"").toLowerCase().includes(q)
        )
      : base;

    if(!ilResults || !ilResultsList) return;
    if(!filtered.length){
      ilResults.style.display = "none";
      ilResultsList.innerHTML = "";
      return;
    }

    ilResultsList.innerHTML = filtered.map((it,idx)=>`
      <div class="il-result-item" data-i="${idx}">
        <div style="font-weight:600;">
          ${escapeHtml(it.title||"(no title)")}
          ${it.tier==='mid' ? '<span style="font-size:10px;color:#6b7280;">(suggestion)</span>' : ''}
        </div>
        <div style="font-size:12px;color:#6b7280;">${escapeHtml(it.url||"(no url)")}</div>
      </div>`).join("");

    ilResults.style.display = "block";

    Array.from(ilResultsList.querySelectorAll(".il-result-item")).forEach((el)=>{
      el.addEventListener("click", ()=>{
        const i    = parseInt(el.getAttribute("data-i")||"0",10)||0;
        const item = filtered[i];
        if(item){
          if(ilTitle) ilTitle.value = item.title || "";
          if(ilUrl)   ilUrl.value   = item.url   || "";
        }
        if (validateILFieldsSilent()) ilApply?.removeAttribute("disabled");
        ilResults.style.display = "none";
        showDomainHint(ilUrl?.value || "");
      });
    });
  });

  ilClose?.addEventListener("click", closeIL);
  ilCancel?.addEventListener("click", closeIL);

  // ------------------------------------------------------------
  // Apply
  // ------------------------------------------------------------
  ilApply?.addEventListener("click", ()=>{
    if (!validateILFieldsSilent()){
      if (ilToast){
        ilToast.textContent = IL_MODE === "external"
          ? "Choose a reference."
          : "Provide Title and Link text. URL is optional (draft).";
        setTimeout(()=> ilToast.textContent = "", 1500);
      }
      return;
    }

    const phrase = ctx.state.getCurrentPhrase();
    let url = "", title = "", topicId = "", kind = "";

    if (IL_MODE === "external"){
      const opt = extReferences?.selectedOptions?.[0];
      url   = (opt?.value||"").trim();
      title = (opt?.dataset?.title || opt?.textContent || "").trim();
      topicId = `x:${norm(title || phrase)}`;
      kind  = "external";
    } else {
      url   = (ilUrl?.value||"").trim();
      title = (ilTitle?.value||"").trim();

      // Prefer engine/imported suggestions from best-fit pool
      const pool   = buildBestFitSuggestions(
        phrase,
        ctx.findEngineSuggestionsForPhrase(phrase) || []
      );
      const nTitle = norm(title);
      let pick     = pool.find(x=> norm(x.title) === nTitle) || null;

      if (pick){
        topicId = pick.topicId || "";
        kind    = pick.kind || "";
        url     = url || pick.url || "";
      } else {
        // same-doc heading fallback
        const viewerEl = ctx.getViewerEl();
        const slug     = ctx.slugifyHeading(title);
        const h        = viewerEl?.querySelector(`h1,h2,h3[id="${slug}"]`);
        if (h) {
          topicId = `h:${h.id}`;
          kind    = "same-doc";
          url     = url || (`#${h.id}`);
        }
      }
    }

    const el = replaceMarkedWithUnderline(phrase, { topicId, kind, url, title });
    if (!el) return;

    // ensure data-url is present for exports
    const finalUrl = ctx.computeFinalUrl(kind, topicId, title, url);
   
   // Decide if user edited the suggestion (compare against snapshot from openIL)
let decisionEventType = "LINK_SUGGESTION_ACCEPTED";
try {
  const m = ctx.state.getCurrentMark(); // the <mark> clicked (may be detached after replace)
  const origUrl   = String(m?.getAttribute("data-orig-url")   || "").trim();
  const origTitle = String(m?.getAttribute("data-orig-title") || "").trim();

  const chosenUrl   = String(finalUrl || url || "").trim();
  const chosenTitle = String(title || "").trim();

  const edited =
    (origUrl   && chosenUrl   && origUrl   !== chosenUrl) ||
    (origTitle && chosenTitle && origTitle !== chosenTitle);

  if (edited) decisionEventType = "LINK_SUGGESTION_EDITED";
} catch {}

// 🔁 Decision Intelligence (Layer 1.3): emit exactly ONE canonical eventType (silent)
try {
  if (typeof window !== "undefined" && typeof window.LC_registerLinkFeedback === "function") {
    window.LC_registerLinkFeedback("accept", {
      eventType: decisionEventType,
      workspaceId: (window.LC_WORKSPACE_ID || "default"),
      docId: (window.LC_ACTIVE_DOC_ID || "doc_demo_001"),
      phraseText: phrase || "",
      targetId:   topicId || "",
      url:        (finalUrl || url || ""),
      title:      (title || ""),
      kind:       (kind || "internal")
    });
  }
} catch (e) {
  console.warn("[IL Modal] decision emit failed", e);
}



    ctx.underlineLinkedPhrases();
    ctx.highlightBucketKeywords();
    ctx.updateHighlightBadge();
    ctx.rebuildEngineHighlightsPanel();

    if (ilToast){
      ilToast.textContent = "Linked (stored) and underlined.";
      setTimeout(()=> ilToast.textContent = "", 900);
    }

    // Keep Link Resolution panel in sync
    if (typeof window !== "undefined" && typeof window.LR_rebuild === "function") {
      try { window.LR_rebuild(); } catch(e2) {
        console.warn("[IL Modal] LR_rebuild failed", e2);
      }
    }

    // ✅ NEW: keep the Linked phrases panel in sync
    try {
      if (typeof window !== "undefined" && typeof window.LC_rebuildLinkedList === "function") {
        window.LC_rebuildLinkedList();
      }
    } catch (e3) {
      console.warn("[IL Modal] failed to rebuild linked phrases list", e3);
    }

    closeIL();
  });

  // ------------------------------------------------------------
  // MARK hover controls (show ✓/✕) + click handlers
  // ------------------------------------------------------------
  const viewerEl = ctx.getViewerEl();
  const hoverSel = "mark.kwd, mark.kwd-int, mark.kwd-ext, mark.kwd-sem";

  viewerEl?.addEventListener("mouseover", (e)=>{
    const mark = e.target?.closest?.(hoverSel);
    if (!mark || !viewerEl.contains(mark)) return;
    const ctl = mark.querySelector(".kw-ctl");
    if (ctl){
      ctl.style.opacity       = "1";
      ctl.style.pointerEvents = "auto";
    }
  });

  viewerEl?.addEventListener("mouseout", (e)=>{
    const mark = e.target?.closest?.(hoverSel);
    if (!mark || !viewerEl.contains(mark)) return;
    const toEl = e.relatedTarget;
    if (toEl && mark.contains(toEl)) return;
    const ctl = mark.querySelector(".kw-ctl");
    if (ctl){
      ctl.style.opacity       = "0";
      ctl.style.pointerEvents = "none";
    }
  });

  // Accept / Reject / Open modal
  viewerEl?.addEventListener("click", (e) => {
    const t = e.target;
    if (!t) return;

    if (t.classList?.contains("kw-accept")) {
      e.preventDefault();
      const mark   = t.closest("mark");
      const phrase = decodeURIComponent(mark.getAttribute("data-phrase") || "");
      const force  =
        mark.classList.contains("kwd-external") ||
        mark.classList.contains("kwd-ext") ||
        mark.getAttribute("data-mode")==="external"
          ? "external"
          : "internal";
      openIL(phrase, mark, force);
      return;
    }

    if (t.classList?.contains("kw-reject")) {
      e.preventDefault();
      const mark = t.closest("mark");
      if (!mark) return;

      const phrase = decodeURIComponent(mark.getAttribute("data-phrase") || "");
      const type =
        mark.classList.contains("kwd-int") ? "internal"  :
        mark.classList.contains("kwd-sem") ? "semantic"  :
        mark.classList.contains("kwd-ext") ? "external"  :
        "engine";

      // 🔁 capture current target info BEFORE unwrapping
      const targetId  = mark.getAttribute("data-topic-id") || "";
      const urlAttr   = mark.getAttribute("data-url") || "";
      const titleAttr = mark.getAttribute("data-title") || "";

      ctx.unwrapMark(mark);
      ctx.rejectPhrase(phrase, type);
      ctx.highlightBucketKeywords();
      ctx.rebuildEngineHighlightsPanel();
      ctx.updateHighlightBadge();

      if (typeof window !== "undefined" && typeof window.LR_rebuild === "function") {
        try { window.LR_rebuild(); } catch(e2) {
          console.warn("[IL Modal] LR_rebuild failed after reject", e2);
        }
      }

      // 🔁 Memory & Feedback Layer – record REJECT
      try {
        if (typeof window !== "undefined" && typeof window.LC_registerLinkFeedback === "function") {
         window.LC_registerLinkFeedback("reject", {
  eventType: "LINK_SUGGESTION_REJECTED",
  workspaceId: (window.LC_WORKSPACE_ID || "ws_demo"),
  docId: (window.LC_ACTIVE_DOC_ID || "doc_demo_001"),
  phraseText: phrase || "",
  targetId:   targetId || "",
  url:        urlAttr || "",
  title:      titleAttr || "",
  kind:       type || "internal"
});

        }
      } catch (e2) {
        console.warn("[IL Modal] feedback reject failed", e2);
      }
      return;
    }

    const mark = t.closest?.("mark");
    if (mark && viewerEl.contains(mark)){
      e.preventDefault();
      const phrase = decodeURIComponent(mark.getAttribute("data-phrase")||"");
      const force  =
        mark.classList.contains("kwd-external") ||
        mark.classList.contains("kwd-ext") ||
        mark.getAttribute("data-mode")==="external"
          ? "external"
          : "internal";
      openIL(phrase, mark, force);
    }
  });

  // ======= Ext Advanced (placeholder toast) =======
  extAdvancedBtn?.addEventListener("click", ()=>{
    const toast = $("error");
    if (toast) {
      toast.textContent = "Advanced external view is coming next (sources, weights, filters).";
      setTimeout(()=> toast.textContent = "", 1500);
    }
  });

  return { openIL, closeIL };
}
