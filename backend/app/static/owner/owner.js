console.log("OWNER.JS PATCH CONFIRMED ✅", Date.now());




console.log("OWNER.JS LOADED ✅ BUILD=2026-01-15-B");
window.__OWNER_JS_BUILD__ = "2026-01-15-B";

// =====================================================
// Owner auth + auto-retry (canonical for Owner Console)
// File: backend/app/static/owner/owner.js
// =====================================================

// ------------------------------
// API endpoints
// ------------------------------
const API_LIST   = "/api/external/manual/list?limit=500";
const API_ADD    = "/api/external/manual/add";
const API_TOGGLE = "/api/external/manual/toggle";
const API_DELETE = "/api/external/manual/delete";

const API_IMPORT = "/api/external/owner/sitemap/import";

// Owner resolver (Queue 11)
const API_RESOLVER_SEARCH = "/api/external/owner/resolver/search";
const API_RESOLVER_ADD    = "/api/external/owner/resolver/add";

// Resolver test endpoint (public / not owner-protected in your middleware)
const API_RESOLVE = "/api/external/resolve";

// Import runs + rollback
const API_RUNS = "/api/external/owner/import/runs";
const API_ROLLBACK = "/api/external/owner/import/rollback";
const API_COUNTS = "/api/external/owner/counts";



function $(id){ return document.getElementById(id); }

function escapeHtml(s){
  return String(s||"").replace(/[&<>"']/g, (m)=>( {
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[m] ));
}
function escapeAttr(s){ return String(s||"").replace(/"/g,"&quot;"); }

function slugify(s){
  s = String(s || "").trim().toLowerCase();
  s = s.replace(/[^a-z0-9\s-]/g, "");
  s = s.replace(/\s+/g, "-");
  s = s.replace(/-{2,}/g, "-");
  return s.slice(0, 120).replace(/^-+|-+$/g, "");
}

// ------------------------------
// Resolver Builder state (Queue 11)
// ------------------------------
let RB_LAST = {
  phrase: "",
  source_label: "",
  items: [],
  total_count: 0,
  returned: 0,
  limit: 0,
  retstart: 0,
  next_retstart: 0,
  has_more: false,
};
window.RB_LAST = RB_LAST;

// ------------------------------
// Owner Auth + Auto-Retry
// ------------------------------
const OWNER_KEY_STORAGE = "LINKCRAFTOR_OWNER_KEY";

async function ownerLoginFlow({ silent = false } = {}){
  let key = (sessionStorage.getItem(OWNER_KEY_STORAGE) || "").trim();

  if(!key){
    if(silent) return false;
    key = prompt("Enter Owner Key (LinkCraftor Control Tower):");
    key = (key || "").trim();
    if(!key) return false;
  }

  const loginRes = await fetch("/owner-api/login", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    credentials: "include",
    body: JSON.stringify({ key })
  });

  const data = await loginRes.json().catch(()=>({}));

  if(!loginRes.ok || data.ok === false){
    sessionStorage.removeItem(OWNER_KEY_STORAGE);
    if(!silent) alert("Invalid Owner Key.");
    return false;
  }

  sessionStorage.setItem(OWNER_KEY_STORAGE, key);
  return true;
}

async function ownerFetch(url, options = {}){
  const opts = { credentials: "include", ...options };
  let res = await fetch(url, opts);

  if(res.status === 401){
    const ok = await ownerLoginFlow({ silent: true });
    if(ok){
      res = await fetch(url, opts);
    }
  }
  return res;
}



async function fetchJson(url, opts){
  const res = await ownerFetch(url, opts);
  const data = await res.json().catch(()=> ({}));
  return { res, data };
}

// ------------------------------
// Counts (Manual + Auto JSON totals) — Queue 7
// ------------------------------
function applyCountsToUI(counts){
  const manual = Number(counts?.manual_count ?? 0);
  const auto = Number(counts?.auto_count ?? 0);
  const total = Number(counts?.total_count ?? (manual + auto));

  // ✅ Overview KPIs (match your updated HTML ids)
  if ($("kpiTotalUrls"))  $("kpiTotalUrls").textContent  = String(total);
  if ($("kpiManualUrls")) $("kpiManualUrls").textContent = String(manual);
  if ($("kpiAutoUrls"))   $("kpiAutoUrls").textContent   = String(auto);

  // ✅ Resolver header KPIs (these are in your HTML)
  if ($("rbManualCount")) $("rbManualCount").textContent = String(manual);
  if ($("rbAutoCount"))   $("rbAutoCount").textContent   = String(auto);
  if ($("rbTotalCount"))  $("rbTotalCount").textContent  = String(total);
}

async function loadOwnerCounts({ silent = true } = {}){
  try{
    const { res, data } = await fetchJson(API_COUNTS + "?_ts=" + Date.now(), { cache: "no-store" });

    if (res.status === 401){
      if(!silent){
        // If you have a UI slot for counts errors, use it; otherwise do nothing.
        if($("kpiUrlsHint")) $("kpiUrlsHint").textContent = "Counts: owner auth required.";
      }
      return null;
    }
    if(!res.ok || data?.ok === false){
      if(!silent && $("kpiUrlsHint")) $("kpiUrlsHint").textContent = `Counts error: ${data?.detail || data?.error || ("HTTP " + res.status)}`;
      return null;
    }

    applyCountsToUI(data);
    return data;
  }catch(e){
    if(!silent && $("kpiUrlsHint")) $("kpiUrlsHint").textContent = `Counts error: ${e?.message || e}`;
    return null;
  }
}


// ------------------------------
// Session chip + Navigation
// ------------------------------
function setSessionChip(state){
  const chip = $("sessionChip");
  const kpi = $("kpiStatus");
  if(!chip) return;

  if(state === "ok"){
    chip.textContent = "Session: Active";
    chip.style.color = "#34d399";
    chip.style.borderColor = "rgba(52,211,153,.35)";
    if(kpi) kpi.textContent = "Active";
  } else if(state === "need"){
    chip.textContent = "Session: Login Required";
    chip.style.color = "#fb7185";
    chip.style.borderColor = "rgba(251,113,133,.35)";
    if(kpi) kpi.textContent = "Login Required";
  } else {
    chip.textContent = "Session: Unknown";
    chip.style.color = "";
    chip.style.borderColor = "";
    if(kpi) kpi.textContent = "—";
  }
}

function showSection(key){
  // Persist last opened section
  try{ localStorage.setItem(OWNER_LAST_SECTION_KEY, String(key || "overview")); }catch(e){}

  document.querySelectorAll("[data-section]").forEach(sec=>{
    sec.classList.toggle("isVisible", sec.getAttribute("data-section") === key);
  });

  document.querySelectorAll("[data-nav]").forEach(b=> b.classList.remove("isActive"));
  const btn = document.querySelector(`[data-nav="${key}"]`);
  if(btn) btn.classList.add("isActive");

  // keep External Intelligence submenu open for any child panel
  const externalChildren = ["manual","sitemap","sources","resolve","runs","rollback","resolver"];
  const isExternalChild = externalChildren.includes(key);

  const sub = document.querySelector(`[data-sub="external"]`);
  const parent = document.querySelector(`[data-nav="external"]`);

  if(sub && parent && isExternalChild){
    sub.classList.add("isOpen");
    parent.classList.add("isActive");
  }

  // Resolver: restore bars + history safely
  if(key === "resolver"){
    try{ rbPersistLoad(); }catch(e){}
    try{
      if (typeof window.rbHistoryRender === "function") window.rbHistoryRender();
    }catch(e){}
  }
} // ✅ IMPORTANT: this closing brace was missing in your file



async function ownerLogout(){
  try{
    await fetch("/owner-api/logout", { method: "POST", credentials: "include" });
  }catch(e){}
  sessionStorage.removeItem(OWNER_KEY_STORAGE);
  setSessionChip("need");
  location.href = "/owner/";
}

// ------------------------------
// Manual dataset UI
// ------------------------------
async function loadManual(){
  const tbody = $("rows");
  const msg = $("msg");
  if(!tbody){
    if(msg) msg.textContent = "UI error: tbody#rows not found.";
    return;
  }

  try{
    if(msg) msg.textContent = "Fetching manual URLs...";
    const {res, data} = await fetchJson(API_LIST + "&_ts=" + Date.now(), { cache: "no-store" });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner login required. Refresh to login.";
      tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">Owner auth required.</td></tr>`;
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }

    const items = Array.isArray(data.items) ? data.items : [];
    if(!items.length){
      tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">No manual URLs yet.</td></tr>`;
      if(msg) msg.textContent = "Manual dataset is empty.";
      return;
    }

    tbody.innerHTML = items.slice().reverse().map((it)=>{
      const key = it.key || "";
      const phrase = it.phrase || "";
      const url = it.url || "";
      const source = it.source || "";
      const added = it.added_at || it.updated_at || "";
      const disabled = !!it.disabled;

      const btnLabel = disabled ? "Enable" : "Disable";
      const btnStyle = disabled
        ? "background:#065f46;border:1px solid #064e3b;color:#e5e7eb"
        : "background:#7c2d12;border:1px solid #431407;color:#e5e7eb";

      return `
        <tr>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(key)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(phrase)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">
            <a href="${escapeAttr(url)}" target="_blank" rel="noreferrer">${escapeHtml(url)}</a>
          </td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(source)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(added)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937;white-space:nowrap">
            <button data-act="toggle" data-url="${escapeAttr(url)}" data-disabled="${disabled ? "1":"0"}"
              style="padding:6px 10px;border-radius:10px;cursor:pointer;${btnStyle}">
              ${btnLabel}
            </button>
            <button data-act="delete" data-url="${escapeAttr(url)}"
              style="margin-left:8px;padding:6px 10px;border-radius:10px;cursor:pointer;background:#111827;border:1px solid #374151;color:#e5e7eb">
              Delete
            </button>
          </td>
        </tr>
      `;
    }).join("");

   tbody.querySelectorAll("button[data-act]").forEach(btn=>{
  btn.addEventListener("click", async ()=>{
    const act = btn.getAttribute("data-act");
    const url = btn.getAttribute("data-url");
    if(!url) return;

    if(act === "toggle"){
      const isDisabled = btn.getAttribute("data-disabled") === "1";
      await manualToggle(url, !isDisabled);   // manualToggle will refresh counts itself
    } else if(act === "delete"){
      await manualDelete(url);                // manualDelete will refresh counts itself
      await loadOwnerCounts({ silent: true });

    }
  });
});


    if(msg) msg.textContent = `Loaded ${items.length} manual URL(s).`;
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
    tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">Failed to load.</td></tr>`;
  }
}

async function saveManual(){
  const msg = $("msg");
  const phrase = ($("inPhrase")?.value || "").trim();
  const url = ($("inUrl")?.value || "").trim();
  const title = ($("inTitle")?.value || "").trim();

  if(!phrase || !url){
    if(msg) msg.textContent = "Phrase and URL are required.";
    return;
  }

  try{
    if(msg) msg.textContent = "Saving...";
    const {res, data} = await fetchJson(API_ADD, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ phrase, url, title: title || null }),
    });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner auth required. Refresh to login.";
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }

    if($("inPhrase")) $("inPhrase").value = "";
    if($("inUrl")) $("inUrl").value = "";
    if($("inTitle")) $("inTitle").value = "";

    if(msg) msg.textContent = "Saved. Refreshing...";
    await loadManual();
    if(msg) msg.textContent = "Done.";
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
  }
}

async function manualToggle(url, disabled){
  const msg = $("msg");
  try{
    const yes = confirm(disabled ? "Disable this manual URL?" : "Enable this manual URL?");
    if(!yes) return;

    const {res, data} = await fetchJson(API_TOGGLE, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ url, disabled: !!disabled }),
    });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner auth required. Refresh to login.";
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }
    await loadManual();
    await loadOwnerCounts({ silent: true });


  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
  }
}

async function manualDelete(url){
  const msg = $("msg");
  try{
    const yes = confirm("Delete this manual URL permanently?");
    if(!yes) return;

    const {res, data} = await fetchJson(API_DELETE, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ url }),
    });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner auth required. Refresh to login.";
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }
    await loadManual();
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
  }
}

// ------------------------------
// Authority Import UI
// ------------------------------
function buildSitemapImportPayload(commit){
  const domain = ($("smDomain")?.value || "").trim();
  const sitemap_url = ($("smUrl")?.value || "").trim();
  const source_label = ($("smLabel")?.value || "").trim();

  if(!source_label) throw new Error("Source label is required.");
  if(domain && sitemap_url) throw new Error("Provide only one: Domain OR Sitemap URL (not both).");

  const payload = { source_label, commit: !!commit };
  if(domain) payload.domain = domain;
  if(sitemap_url) payload.sitemap_url = sitemap_url;
  return payload;
}

async function runSitemapImport(commit){
  const msg = $("smMsg");
  const out = $("smOut");

  try{
    if(!out) return;

    if(msg) msg.textContent = commit ? "Running import (COMMIT)..." : "Running import (dry run)...";
    out.textContent = commit ? "Running commit...\n" : "Running dry run...\n";

    const payload = buildSitemapImportPayload(commit);

    const {res, data} = await fetchJson(API_IMPORT, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload),
    });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner auth required. Refresh to login.";
      out.textContent = "Owner auth required.";
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }

    out.textContent = JSON.stringify(data, null, 2);
    if(msg) msg.textContent = commit ? "Commit completed." : "Dry run completed.";
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
    if(out) out.textContent = `Error: ${e.message || e}`;
  }
}

// ------------------------------
// Resolver Test UI (public endpoint)
// ------------------------------
async function runResolveTest(){
  const phrase = ($("rsPhrase")?.value || "").trim();
  const src = ($("rsSource")?.value || "").trim();

  const msg = $("rsMsg");
  const out = $("rsOut");

  if(!phrase){
    if(msg) msg.textContent = "Type a phrase first (e.g. syphilis).";
    return;
  }

  try{
    if(msg) msg.textContent = "Searching...";
    if(out) out.textContent = "Searching...\n";

    let url = `${API_RESOLVE}?phrase=${encodeURIComponent(phrase)}`;
    if(src) url += `&source_label=${encodeURIComponent(src)}`;

    const {res, data} = await fetchJson(url, { cache: "no-store" });

    if(!res.ok){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }

    if(out) out.textContent = JSON.stringify(data, null, 2);
    if(msg) msg.textContent = `Done.`;
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
    if(out) out.textContent = `Error: ${e.message || e}`;
  }
} // ✅ important close

// ------------------------------
// Resolver Builder (Queue 11)
// ------------------------------
function rbSetText(id, txt){
  const el = $(id);
  if(el) el.textContent = String(txt ?? "");
}
function rbSetDisabled(id, disabled){
  const el = $(id);
  if(el){
    el.disabled = !!disabled;
    el.style.opacity = disabled ? "0.6" : "";
  }
}

// --- Message UI that will NOT wipe job bars ---
function ensureRbMsgUI(){
  const host = $("rbSearchMsg");
  if(!host) return null;

  // Create message-text holder once so we never overwrite job bars container
  let text = document.getElementById("rbSearchMsgText");
  if(text) return text;

  text = document.createElement("div");
  text.id = "rbSearchMsgText";
  text.style.marginBottom = "6px";
  text.style.whiteSpace = "pre-wrap";
  host.prepend(text);
  return text;
}
function setRbMsg(t){
  const text = ensureRbMsgUI();
  if(text) text.textContent = t || "";
}

// Multi-phrase helpers
function rbParsePhrases(raw){
  return String(raw || "")
    .split(/[,;\n]+/g)
    .map(s => s.trim())
    .filter(Boolean);
}
function rbSleep(ms){ return new Promise(r => setTimeout(r, ms)); }

// Inputs
function getRbPhraseRaw(){ return String($("rbPhrase")?.value || "").trim(); }
function getRbFirstPhrase(){
  const raw = getRbPhraseRaw();
  const list = rbParsePhrases(raw);
  return (list[0] || "").trim();
}
function getRbCurrentPhrase(){
  // Prefer the phrase currently loaded in the table (RB_LAST), otherwise fall back to first phrase.
  return String(RB_LAST?.phrase || getRbFirstPhrase() || "").trim();
}
function getRbSource(){
  const el = $("rbProvider");
  return String(el?.value || "").trim().toLowerCase();
}
function getRbLimit(){
  // ✅ Default should be unlimited when empty
  const raw = String($("rbLimit")?.value ?? "0").trim();
  if(raw === "") return 0;

  const n = parseInt(raw, 10);
  if(isNaN(n)) return 0;
  if(n <= 0) return 0; // unlimited
  return n;
}

function getRbRetstart(){
  const raw = String($("rbRetstart")?.value ?? "0").trim();
  const n = parseInt(raw === "" ? "0" : raw, 10);
  if(isNaN(n) || n < 0) return 0;
  return n;
}

// Pager UI
function updateResolverPagerUI(payload){
  const total = Number(payload?.total_count ?? 0);
  const returned = Number(payload?.returned ?? 0);
  const retstart = Number(payload?.retstart ?? 0);
  const hasMore = payload?.has_more === true;
  const nextStart = (payload?.next_retstart === null || typeof payload?.next_retstart === "undefined")
    ? (retstart + returned)
    : Number(payload?.next_retstart);

  const startHuman = total > 0 ? (retstart + 1) : 0;
  const endHuman = total > 0 ? Math.min(retstart + returned, total) : 0;
  const showing = total > 0 ? `${startHuman}–${endHuman}` : "—";

  rbSetText("rbShowing", showing);
  rbSetText("rbTotal", total ? String(total) : "—");
  rbSetText("rbNextRetstart", hasMore ? String(nextStart) : "—");

  rbSetDisabled("btnRbPrev", !(retstart > 0));
  rbSetDisabled("btnRbNext", !(hasMore === true));

  if($("rbRetstart")) $("rbRetstart").value = String(retstart);
}

function rbParseYear(s){
  const n = parseInt(String(s || "").trim(), 10);
  return (isNaN(n) ? null : n);
}

function rbPubdateToKey(pubdate){
  // pubdate examples: "2023 Apr 17", "1994 Sep", "2020 Mar"
  const t = String(pubdate || "");
  const m = t.match(/\b(19|20)\d{2}\b/);
  const year = m ? parseInt(m[0], 10) : null;

  const months = {
    jan:1,feb:2,mar:3,apr:4,may:5,jun:6,jul:7,aug:8,sep:9,oct:10,nov:11,dec:12
  };
  let month = 0;
  const mm = t.toLowerCase().match(/\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b/);
  if(mm) month = months[mm[1]] || 0;

  // key lets us sort roughly by recency: YYYYMM
  const key = (year ? (year * 100 + month) : 0);
  return { year, key };
}

function rbApplyYearSort(items){
  const minY = rbParseYear($("rbYearMin")?.value);
  const maxY = rbParseYear($("rbYearMax")?.value);
  const sort = String($("rbSort")?.value || "relevance");

  let out = Array.isArray(items) ? items.slice() : [];

  // Filter
  if(minY !== null || maxY !== null){
    out = out.filter(it=>{
      const { year } = rbPubdateToKey(it?.pubdate);
      if(year === null) return false; // if no year, drop it under filter mode
      if(minY !== null && year < minY) return false;
      if(maxY !== null && year > maxY) return false;
      return true;
    });
  }

  // Sort
  if(sort === "newest" || sort === "oldest"){
    out.sort((a,b)=>{
      const ak = rbPubdateToKey(a?.pubdate).key;
      const bk = rbPubdateToKey(b?.pubdate).key;
      return (sort === "newest") ? (bk - ak) : (ak - bk);
    });
  }
  // relevance = keep original order

  return out;
}



function renderResolverBuilderRows(items){
  items = rbApplyYearSort(items);

  const tbody = $("rbRows");
  if(!tbody) return;

  if(!Array.isArray(items) || !items.length){
    tbody.innerHTML = `<tr><td colspan="8" style="padding:10px">0 results.</td></tr>`;
    return;
  }

  tbody.innerHTML = items.map((it)=>{
    const title = String(it.title || "");
    const titleSlug = slugify(title);
    const url = String(it.url || "");
    const id = String(it.id || "");
    const journal = String(it.journal || "");
    const pubdate = String(it.pubdate || "");
    const score = (it.score ?? "");

    return `
      <tr>
        <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(id)}</td>
        <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(title)}</td>
        <td style="padding:10px;border-bottom:1px solid #1f2937"><code>${escapeHtml(titleSlug)}</code></td>
        <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(journal)}</td>
        <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(pubdate)}</td>
        <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(score)}</td>
        <td style="padding:10px;border-bottom:1px solid #1f2937">
          <a href="${escapeAttr(url)}" target="_blank" rel="noreferrer">${escapeHtml(url)}</a>
        </td>
        <td style="padding:10px;border-bottom:1px solid #1f2937;white-space:nowrap">
          <button data-act="add-one"
            data-id="${escapeAttr(id)}"
            data-title="${escapeAttr(title)}"
            data-url="${escapeAttr(url)}"
            style="padding:6px 10px;border-radius:10px;cursor:pointer;background:#2563eb;border:1px solid #1f2937;color:#e5e7eb">
            Add
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

// ✅ updated: supports phraseOverride + TRUE unlimited when UI limit=0 (client-side paging)
async function runResolverBuilderSearch({ retstartOverride = null, phraseOverride = null } = {}){
  const phrase = String(phraseOverride ?? getRbCurrentPhrase() ?? "").trim();
  const source_label = getRbSource() || "pubmed";

  // UI: 0 = unlimited (but backend does NOT accept limit=0)
  const uiLimit = getRbLimit();
  const SERVER_PAGE_SIZE = 50; // backend max page size (your server rejects 0)
  const isUnlimited = (uiLimit <= 0);

  // Always send a valid backend limit (>=1)
  const limitParam = isUnlimited
    ? SERVER_PAGE_SIZE
    : Math.max(1, Math.min(uiLimit, SERVER_PAGE_SIZE));

  // retstart
  let start = (retstartOverride !== null)
    ? Math.max(0, parseInt(String(retstartOverride), 10) || 0)
    : getRbRetstart();

  const raw = $("rbRaw");
  const rows = $("rbRows");

  if(!phrase){
    setRbMsg("Phrase is required.");
    return;
  }

  if($("rbRetstart")) $("rbRetstart").value = String(start);

  try{
    if(isUnlimited){
      setRbMsg(`Unlimited mode: fetching in pages of ${SERVER_PAGE_SIZE}…`);
    } else {
      setRbMsg(`Searching: "${phrase}"`);
    }

    if(raw) raw.textContent = "Searching...\n";
    if(rows) rows.innerHTML = `<tr><td colspan="8" style="padding:10px">Searching…</td></tr>`;

    let allItems = [];
    let lastPayload = null;

    // Hard safety guard
    let guard = 0;

    while(true){
      guard += 1;
      if(guard > 20000){
        throw new Error("Paging guard triggered (too many pages). Check backend next_retstart/has_more.");
      }

      const url =
        `${API_RESOLVER_SEARCH}?phrase=${encodeURIComponent(phrase)}` +
        `&source_label=${encodeURIComponent(source_label)}` +
        `&limit=${encodeURIComponent(String(limitParam))}` +
        `&retstart=${encodeURIComponent(String(start))}` +
        `&_ts=${Date.now()}`;

      const { res, data } = await fetchJson(url, { cache: "no-store" });

      if(res.status === 401){
        setRbMsg("Owner auth required.");
        if(raw) raw.textContent = "Owner auth required (401). Please refresh and login.\n";
        if(rows) rows.innerHTML = `<tr><td colspan="8" style="padding:10px">Owner auth required.</td></tr>`;
        return;
      }

      if(!res.ok || data?.ok === false){
        const pretty = (data && typeof data === "object")
          ? JSON.stringify(data, null, 2)
          : String(data ?? "");
        console.error("[RB_SEARCH] HTTP error", { status: res.status, url, payload: data });
        throw new Error(pretty || `HTTP ${res.status}`);
      }

      const items = Array.isArray(data.items) ? data.items : [];
      lastPayload = data;

      if(items.length) allItems.push(...items);

      const total = Number(data.total_count || 0);
      const returnedNow = items.length;

      if(isUnlimited){
        setRbMsg(`Unlimited mode: fetching in pages of ${SERVER_PAGE_SIZE}… Fetched ${allItems.length}${total ? ` / ${total}` : ""}`);
      }

      // stop if no items
      if(!items.length) break;

      // stop after one page in non-unlimited mode
      if(!isUnlimited) break;

      // compute hasMore safely
      const hasMore =
        (typeof data.has_more === "boolean")
          ? data.has_more
          : (total > 0 ? ((start + returnedNow) < total) : (returnedNow > 0));

      // compute nextStart safely
      let nextStart =
        (data.next_retstart === null || typeof data.next_retstart === "undefined")
          ? (start + returnedNow)
          : Number(data.next_retstart || 0);

      // stall protection
      if(!nextStart || nextStart <= start){
        nextStart = start + returnedNow;
      }
      if(!nextStart || nextStart <= start) break;

      if(!hasMore) break;

      start = nextStart;
      if($("rbRetstart")) $("rbRetstart").value = String(start);
    }

    // Build RB_LAST using combined results
    const totalCount = Number(lastPayload?.total_count || allItems.length || 0);
    RB_LAST = {
      phrase,
      source_label,
      items: allItems,
      total_count: totalCount,
      returned: allItems.length,
      limit: isUnlimited ? 0 : limitParam, // keep UI meaning (0 = unlimited)
      retstart: isUnlimited ? 0 : Number(lastPayload?.retstart || 0),
      next_retstart: isUnlimited ? 0 : Number(lastPayload?.next_retstart || 0),
      has_more: false,
    };
    window.RB_LAST = RB_LAST;

    // render
    if(raw) raw.textContent = JSON.stringify({ ...lastPayload, items: allItems, returned: allItems.length }, null, 2);
    renderResolverBuilderRows(allItems);
    updateResolverPagerUI({
      total_count: totalCount,
      returned: isUnlimited ? allItems.length : Number(lastPayload?.returned || allItems.length),
      retstart: isUnlimited ? 0 : Number(lastPayload?.retstart || 0),
      has_more: false,
      next_retstart: null,
    });

    setRbMsg(isUnlimited
      ? `Done (Unlimited): "${phrase}". Returned ${allItems.length}.`
      : `Done: "${phrase}". Returned ${allItems.length}.`
    );

  } catch(e){
    let msg = "";
    try{
      msg = (e && typeof e === "object" && typeof e.message === "string") ? e.message : JSON.stringify(e, null, 2);
    } catch(_){
      msg = String(e ?? "");
    }

    console.error("[RB_SEARCH] Error:", e);
    setRbMsg(`Error: ${msg || "Unknown error"}`);
    if(raw) raw.textContent = `Error: ${msg || "Unknown error"}`;
    if(rows) rows.innerHTML = `<tr><td colspan="8" style="padding:10px">Failed to load.</td></tr>`;
  }
}


// ✅ NEW: Multi-phrase Search runner (sequential; updates table per phrase)
async function runResolverBuilderSearchMulti(){
  const raw = getRbPhraseRaw();
  const phrases = rbParsePhrases(raw);

  if(!phrases.length){
    setRbMsg("Phrase is required.");
    return;
  }

  // single phrase => normal search
  if(phrases.length === 1){
    if($("rbRetstart")) $("rbRetstart").value = "0";
    await runResolverBuilderSearch({ retstartOverride: 0, phraseOverride: phrases[0] });
    return;
  }

  const btn = $("btnRbSearch");
  if(btn){ btn.disabled = true; btn.style.opacity = "0.7"; }

  try{
    for(let i=0; i<phrases.length; i++){
      const p = String(phrases[i] || "").trim();
      if(!p) continue;

      setRbMsg(`Batch Search ${i+1}/${phrases.length}: "${p}"`);
      if($("rbRetstart")) $("rbRetstart").value = "0";
      await runResolverBuilderSearch({ retstartOverride: 0, phraseOverride: p });

      // small pause so you see each phrase "finish" before the next starts
      await rbSleep(250);
    }
    setRbMsg(`Batch Search complete (${phrases.length} phrase(s)).`);
  } finally {
    // preserve your multi-phrase input as-is
    if($("rbPhrase")) $("rbPhrase").value = raw;
    if(btn){ btn.disabled = false; btn.style.opacity = ""; }
  }
}

async function addOneFromResolverSelection({ phrase, source_label, url, title, id }){
  const {res, data} = await fetchJson(API_RESOLVER_ADD + "?_ts=" + Date.now(), {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ phrase, source_label, selection: { url, title, id } }),
  });

  if(res.status === 401) throw new Error("Owner auth required.");
  if(!res.ok || data?.ok === false) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);
  return data;
}

// =====================================================
// RB Jobs (unlimited progress bars, keyed by phrase)
// =====================================================

// =====================================================
// RB Jobs Persistence (Step 1) — survive refresh
// =====================================================
const RB_PERSIST_KEY = "LC_OWNER_RB_JOBS_V1";
const RB_FAILED_KEY  = "LC_OWNER_RB_FAILED_V1";
const OWNER_LAST_SECTION_KEY = "LC_OWNER_LAST_SECTION_V1";


let __rbPersistT = null;

function rbPersistSave(){
  try{
    // Throttle writes (avoid saving on every single row)
    if(__rbPersistT) clearTimeout(__rbPersistT);
    __rbPersistT = setTimeout(()=>{
      try{
        const jobs = window.__rbJobs || {};
        const safeJobs = {};

        // keep only JSON-safe primitives
        for(const [k, v] of Object.entries(jobs)){
          if(!v || typeof v !== "object") continue;
          safeJobs[k] = {
            id: String(v.id || k),
            label: String(v.label || ""),
            paused: !!v.paused,
            stopped: !!v.stopped,
            running: !!v.running,
            done: Number(v.done || 0),
            total: Number(v.total || 0),
            ok: Number(v.ok || 0),
            fail: Number(v.fail || 0),
            startedAt: v.startedAt || null,
            endedAt: v.endedAt || null,
            note: String(v.note || ""),
          };
        }

        localStorage.setItem(RB_PERSIST_KEY, JSON.stringify({
          ts: Date.now(),
          jobs: safeJobs,
        }));

        // failed ids (optional but useful)
        const failed = Array.isArray(window.__rbFailedIds) ? window.__rbFailedIds : [];
        localStorage.setItem(RB_FAILED_KEY, JSON.stringify(failed.slice(0, 200000))); // practical ceiling
        rbHistoryInvalidate(); // ✅ Step 2: refresh history whenever we persist
      }catch(_e){}
    }, 250);
  }catch(_e){}
}

function rbPersistLoad(){
  try{
    const raw = localStorage.getItem(RB_PERSIST_KEY);
    if(!raw) return false;

    const parsed = JSON.parse(raw);
    const jobs = parsed?.jobs;
    if(!jobs || typeof jobs !== "object") return false;

    window.__rbJobs = window.__rbJobs || {};
    for(const [k, v] of Object.entries(jobs)){
      if(!v || typeof v !== "object") continue;
      window.__rbJobs[k] = {
        id: String(v.id || k),
        label: String(v.label || ""),
        paused: !!v.paused,
        stopped: !!v.stopped,
        running: !!v.running,
        done: Number(v.done || 0),
        total: Number(v.total || 0),
        ok: Number(v.ok || 0),
        fail: Number(v.fail || 0),
        startedAt: v.startedAt || null,
        endedAt: v.endedAt || null,
        note: String(v.note || ""),
      };
    }

    // restore failed ids
    try{
      const fr = localStorage.getItem(RB_FAILED_KEY);
      const arr = fr ? JSON.parse(fr) : [];
      window.__rbFailedIds = Array.isArray(arr) ? arr : [];
    }catch(_e){
      window.__rbFailedIds = window.__rbFailedIds || [];
    }

    // Re-render all job cards so they appear after refresh
    for(const id of Object.keys(window.__rbJobs)){
      try{ rbRenderJob(id); }catch(_e){}
    }

    return true;
  }catch(_e){
    return false;
  }
}

// =====================================================
// RB Job History Panel (Step 1) — UI-only (GLOBAL SCOPE)
// =====================================================
function rbJobStateLabel(job){
  if(!job) return "—";
  if(job.stopped) return "Stopped";
  if(job.paused) return "Paused";
  if(job.running) return "Running";
  if(job.endedAt) return "Completed";
  return "Idle";
}

function rbFmtDurationMs(ms){
  const s = Math.max(0, Math.floor(ms / 1000));
  const m = Math.floor(s / 60);
  const r = s % 60;
  if(m <= 0) return `${r}s`;
  return `${m}m ${r}s`;
}

function rbGetJobDuration(job){
  try{
    const a = job?.startedAt ? Date.parse(job.startedAt) : null;
    const b = job?.endedAt ? Date.parse(job.endedAt) : null;
    if(a && b && b >= a) return rbFmtDurationMs(b - a);
    if(a && job?.running) return rbFmtDurationMs(Date.now() - a);
  }catch(e){}
  return "—";
}

window.rbHistoryRender = function rbHistoryRender(){
  const tbody = $("rbHistoryRows");
  if(!tbody) return;

  const jobs = window.__rbJobs || {};
  const list = Object.values(jobs).filter(x => x && typeof x === "object");

  list.sort((a,b)=>{
    const ta = Date.parse(a.endedAt || a.startedAt || 0) || 0;
    const tb = Date.parse(b.endedAt || b.startedAt || 0) || 0;
    return tb - ta;
  });

  if(!list.length){
    tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">No job history yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = list.map(job=>{
    const phrase = String(job.label || job.id || "").trim();
    const state =
      job.stopped ? "Stopped" :
      job.paused  ? "Paused"  :
      job.running ? "Running" :
      job.endedAt ? "Completed" : "Idle";

    const done = Number(job.done || 0);
    const total = Number(job.total || 0);
    const prog = (total > 0) ? `${done} / ${total}` : `${done} / —`;

    const ok = Number(job.ok || 0);
    const fail = Number(job.fail || 0);

    return `
      <tr>
        <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(phrase)}</td>
        <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(state)}</td>
        <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(prog)}</td>
        <td style="padding:10px;border-bottom:1px solid #1f2937">OK: ${escapeHtml(ok)} | Fail: ${escapeHtml(fail)}</td>
        <td style="padding:10px;border-bottom:1px solid #1f2937">—</td>
        <td style="padding:10px;border-bottom:1px solid #1f2937;white-space:nowrap">
          <button type="button" class="btnGhost" data-act="rb-hist-load" data-phrase="${escapeAttr(phrase)}" style="padding:6px 10px">Load</button>
          <button type="button" class="btnGhost" data-act="rb-hist-run"  data-phrase="${escapeAttr(phrase)}" style="margin-left:8px;padding:6px 10px">Run Again</button>
        </td>
      </tr>
    `;
  }).join("");

  tbody.onclick = async (ev)=>{
    const btn = ev.target?.closest?.("button[data-act]");
    if(!btn) return;

    const act = btn.getAttribute("data-act");
    const phrase = String(btn.getAttribute("data-phrase") || "").trim();
    if(!phrase) return;

    if(act === "rb-hist-load"){
      if($("rbPhrase")) $("rbPhrase").value = phrase;
      if($("rbRetstart")) $("rbRetstart").value = "0";
      setRbMsg(`Loaded phrase from history: "${phrase}"`);
      return;
    }

    if(act === "rb-hist-run"){
      if($("rbPhrase")) $("rbPhrase").value = phrase;
      if($("rbRetstart")) $("rbRetstart").value = "0";
      setRbMsg(`Running from history: "${phrase}"`);
      await addAllResolverResults({ phraseOverride: phrase, retstartOverride: 0, silent: false });
    }
  };
};

window.rbHistoryClear = function rbHistoryClear(){
  try{
    localStorage.removeItem(RB_PERSIST_KEY);
    localStorage.removeItem(RB_FAILED_KEY);
  }catch(e){}
  try{
    window.__rbJobs = {};
    window.__rbFailedIds = [];
  }catch(e){}
  try{
    const wrap = document.getElementById("rbJobsWrap");
    if(wrap) wrap.innerHTML = "";
  }catch(e){}
  if (typeof window.rbHistoryRender === "function") window.rbHistoryRender();
  setRbMsg("Job history cleared.");
};

window.rbHistoryClear = function rbHistoryClear(){
  try{
    localStorage.removeItem(RB_PERSIST_KEY);
    localStorage.removeItem(RB_FAILED_KEY);
  }catch(e){}
  try{
    window.__rbJobs = {};
    window.__rbFailedIds = [];
  }catch(e){}
  try{
    const wrap = document.getElementById("rbJobsWrap");
    if(wrap) wrap.innerHTML = "";
  }catch(e){}
  if (typeof window.rbHistoryRender === "function") window.rbHistoryRender();
  setRbMsg("Job history cleared.");
};

// =====================================================
// Step 2 — Live History Refresh (debounced)
// =====================================================
let __rbHistoryT = null;

function rbHistoryInvalidate(){
  try{
    if(__rbHistoryT) clearTimeout(__rbHistoryT);
    __rbHistoryT = setTimeout(()=>{
      try{
        if (typeof window.rbHistoryRender === "function") window.rbHistoryRender();
      }catch(e){}
    }, 150);
  }catch(e){}
}



window.__rbJobs = window.__rbJobs || {};
window.__rbFailedIds = window.__rbFailedIds || [];

function rbJobIdFromPhrase(phrase){
  return String(phrase || "").trim().toLowerCase();
}
function rbGetJob(jobId){
  const id = String(jobId || "").trim();
  window.__rbJobs[id] = window.__rbJobs[id] || {
    id, label: id,
    paused:false, stopped:false, running:false,
    done:0, total:0, ok:0, fail:0,
    startedAt:null, endedAt:null,
    note:"",
    reachedEnd:false, // ✅ NEW
  };
  return window.__rbJobs[id];
}
async function rbWaitIfPaused(jobId){
  const job = rbGetJob(jobId);
  while(job.paused && !job.stopped){
    await new Promise(r => setTimeout(r, 200));
  }
}

function rbPause(jobId){ rbGetJob(jobId).paused = true; rbRenderJob(jobId); rbPersistSave(); }
function rbResume(jobId){ rbGetJob(jobId).paused = false; rbRenderJob(jobId); rbPersistSave(); }
function rbStop(jobId){ rbGetJob(jobId).stopped = true; rbRenderJob(jobId); rbPersistSave(); }


function rbEnsureJobsUI(){
  ensureRbMsgUI();
  const host = $("rbSearchMsg");
  if(!host) return;

  let wrap = document.getElementById("rbJobsWrap");
  if(wrap) return;

  wrap = document.createElement("div");
wrap.id = "rbJobsWrap";
wrap.style.marginTop = "10px";
wrap.style.display = "flex";
wrap.style.flexDirection = "row";      // left → right
wrap.style.flexWrap = "wrap";          // ✅ allow wrapping into rows
wrap.style.alignItems = "flex-start";  // ✅ keep cards aligned at top
wrap.style.gap = "12px";
wrap.style.width = "100%";             // ✅ take full row width
host.appendChild(wrap);
}

function rbEnsureJobUI(jobId){
  rbEnsureJobsUI();
  const wrap = document.getElementById("rbJobsWrap");
  if(!wrap) return null;

  const id = String(jobId);
  let card = wrap.querySelector(`[data-rb-job="${CSS.escape(id)}"]`);
  if(card) return card;

  card = document.createElement("div");
  card.setAttribute("data-rb-job", id);
  card.style.border = "1px solid rgba(148,163,184,.25)";
  card.style.borderRadius = "14px";
  card.style.padding = "10px 12px";
  card.style.background = "rgba(15,23,42,.25)";
  // ✅ fixed card width so wrap becomes a clean grid
card.style.width = "340px";
card.style.flex = "0 0 340px";


  card.innerHTML = `
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <strong data-rb-title style="font-size:12px;color:#e5e7eb"></strong>
      <span data-rb-state style="font-size:12px;color:#94a3b8"></span>
      <span style="margin-left:auto;display:flex;gap:8px;flex-wrap:wrap">
        <button type="button" class="btnGhost" data-rb-act="pause" style="padding:4px 10px">Pause</button>
        <button type="button" class="btnGhost" data-rb-act="resume" style="padding:4px 10px;display:none">Continue</button>
        <button type="button" class="btnGhost" data-rb-act="stop" style="padding:4px 10px">Stop</button>
      </span>
    </div>

    <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:6px;font-size:12px;color:#94a3b8">
      <span data-rb-pct>Progress: 0%</span>
      <span data-rb-counts>0 / 0</span>
      <span data-rb-okfail>OK: 0 | Fail: 0</span>
    </div>

    <div style="height:10px;border-radius:999px;overflow:hidden;border:1px solid rgba(148,163,184,.25);background:rgba(15,23,42,.35);margin-top:6px">
      <div data-rb-bar style="height:100%;width:0%;background:rgba(37,99,235,.9)"></div>
    </div>

    <div data-rb-note style="margin-top:6px;font-size:12px;color:#94a3b8"></div>
  `;

  wrap.appendChild(card);

  card.addEventListener("click", (ev)=>{
    const b = ev.target?.closest?.("button[data-rb-act]");
    if(!b) return;
    const act = b.getAttribute("data-rb-act");
    if(act === "pause") rbPause(id);
    if(act === "resume") rbResume(id);
    if(act === "stop") rbStop(id);
  });

  return card;
}

function rbRenderJob(jobId){
  const job = rbGetJob(jobId);
  const card = rbEnsureJobUI(jobId);
  if(!card) return;

  const title = card.querySelector("[data-rb-title]");
  const state = card.querySelector("[data-rb-state]");
  const pctEl = card.querySelector("[data-rb-pct]");
  const counts = card.querySelector("[data-rb-counts]");
  const okfail = card.querySelector("[data-rb-okfail]");
  const bar = card.querySelector("[data-rb-bar]");
  const note = card.querySelector("[data-rb-note]");
  const pauseBtn = card.querySelector('button[data-rb-act="pause"]');
  const resumeBtn = card.querySelector('button[data-rb-act="resume"]');

  let total = Math.max(0, Number(job.total || 0));
  const done = Math.max(0, Number(job.done || 0));

  // ✅ Completed means: endedAt set, not running, and not stopped.
  const isCompleted = !!job.endedAt && !job.running && !job.stopped;

  // ✅ If completed, force UI to show 100% and make counts consistent.
  // This prevents: "Completed" but progress stuck at 45% etc.
  if(isCompleted){
    if(total <= 0 || done < total) total = done;
  }

  const pct = isCompleted
    ? 100
    : (total > 0 ? Math.min(100, Math.round((done / total) * 100)) : 0);

  if(title) title.textContent = job.label || job.id;
  if(pctEl) pctEl.textContent = `Progress: ${pct}%`;
  if(counts){
  // If total is 0 and completed, show 0/0 (not 0/?)
  const denom = (total > 0) ? total : (isCompleted ? done : "—");
  counts.textContent = `${done} / ${denom}`;
}
  if(okfail) okfail.textContent = `OK: ${job.ok || 0} | Fail: ${job.fail || 0}`;
  if(bar) bar.style.width = `${pct}%`;
  if(note) note.textContent = job.note || "";

  let s = "";
  if(job.stopped) s = "Stopped";
  else if(job.paused) s = "Paused";
  else if(job.running) s = "Running…";
  else if(job.endedAt) s = "Completed";

  if(state) state.textContent = s ? `— ${s}` : "";
  if(pauseBtn) pauseBtn.style.display = job.paused ? "none" : "inline-block";
  if(resumeBtn) resumeBtn.style.display = job.paused ? "inline-block" : "none";
  rbHistoryInvalidate(); // ✅ Step 2: keep history table in sync with bars
}

function rbNum(x, fallback = 0){
  const n = Number(x);
  return Number.isFinite(n) ? n : fallback;
}



// ---- Single-phrase AddAll worker ----
async function addAllResolverResults({ phraseOverride=null, sourceOverride=null, retstartOverride=0, silent=false } = {}){
  const phrase = String(phraseOverride ?? getRbFirstPhrase() ?? "").trim();
  const source_label = String(sourceOverride ?? getRbSource() ?? RB_LAST.source_label ?? "pubmed").trim().toLowerCase();
  if(!phrase){ setRbMsg("Type a phrase first."); return; }

  // Use UI limit as chunk size; if 0, use safe chunk=200
  let pageLimit = parseInt(String($("rbLimit")?.value || "0"), 10);
  if(isNaN(pageLimit) || pageLimit < 0) pageLimit = 0;
 // ✅ pageSize is used by some notes/UI — make sure it always exists
const pageSize = pageLimit;




  let start = parseInt(String(retstartOverride ?? 0), 10);
  if(isNaN(start) || start < 0) start = 0;

  const jobId = rbJobIdFromPhrase(phrase);
  const job = rbGetJob(jobId);
  job.label = phrase;
  job.paused = false;
  job.stopped = false;
  job.running = true;
  job.done = 0;
  job.ok = 0;
  job.fail = 0;
  job.note = "Starting…";
  job.startedAt = new Date().toISOString();
  job.endedAt = null;
  rbRenderJob(jobId);



  const btn = $("btnRbAddAll");
  if(!silent && btn){ btn.disabled = true; btn.style.opacity = "0.7"; }

  try{
    setRbMsg(`Adding pages for: ${phrase}`);

    // ✅ UNLIMITED: removed MAX_PAGES + MAX_TOTAL caps
let pages = 0;

while(true){
  pages += 1;

  const url =
    `${API_RESOLVER_SEARCH}?phrase=${encodeURIComponent(phrase)}` +
    `&source_label=${encodeURIComponent(source_label)}` +
    `&limit=${encodeURIComponent(String(pageSize))}` +
    `&retstart=${encodeURIComponent(String(start))}` +
    `&_ts=${Date.now()}`;

  const {res, data} = await fetchJson(url, { cache: "no-store" });

  if(res.status === 401) throw new Error("Owner auth required.");
  if(!res.ok || data?.ok === false) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);

  const items = Array.isArray(data.items) ? data.items : [];

  // Total from backend (for %)
  job.total = Number(data.total_count || job.total || 0);
  rbRenderJob(jobId);
  rbPersistSave();


  if(!items.length) break;

  for(const it of items){
    await rbWaitIfPaused(jobId);

    if(job.stopped){
      job.note = "Stopped by user.";
      job.running = false;
      job.endedAt = new Date().toISOString();
      rbRenderJob(jobId);
      rbPersistSave();

      return;
    }

     // ----------------------------
  // Self-healing paging logic
  // ----------------------------
  const totalCount = rbNum(data?.total_count, 0);
  const returnedNow = Array.isArray(items) ? items.length : 0;

  // Track total for progress (keep the biggest known total)
  if(totalCount > 0){
    job.total = Math.max(rbNum(job.total, 0), totalCount);
  } else {
    job.total = Math.max(rbNum(job.total, 0), rbNum(job.done, 0));
  }

  // Compute "should we continue" even if backend has_more is wrong/missing
  const fallbackHasMore =
    (totalCount > 0) ? ((start + returnedNow) < totalCount) : (returnedNow > 0);

  const hasMore =
    (typeof data?.has_more === "boolean") ? data.has_more : fallbackHasMore;

  // Compute nextStart even if next_retstart is wrong/missing
  let nextStart =
    (data?.next_retstart === null || typeof data?.next_retstart === "undefined")
      ? (start + returnedNow)
      : rbNum(data.next_retstart, 0);

  // If backend gave nonsense, fall back
  if(!nextStart || nextStart <= start){
    nextStart = start + returnedNow;
  }

  // Stall guard (prevents infinite loop)
  job.__stall = rbNum(job.__stall, 0);
  if(nextStart <= start){
    job.__stall += 1;
  } else {
    job.__stall = 0;
  }

  if(job.__stall >= 3){
    job.note = `Paging stalled at retstart=${start}. Stopping to avoid infinite loop.`;
    rbRenderJob(jobId);
    rbPersistSave();
    break;
  }

  // Stop if no more pages
  if(!hasMore) break;

  // Continue paging
  start = nextStart;

  // Persist so refresh never loses current progress
  rbPersistSave();



    try{
      await addOneFromResolverSelection({
        phrase,
        source_label,
        url: String(it.url || ""),
        title: String(it.title || ""),
        id: String(it.id || ""),
      });
      job.ok += 1;
    }catch(_e){
      job.fail += 1;
      try{ window.__rbFailedIds.push(String(it.id || "")); }catch(_){}
    }

    job.done = job.ok + job.fail;
    job.note = `Paging… retstart=${start}`;
    rbRenderJob(jobId);
    rbPersistSave();

  }

       const hasMore = !!data.has_more;
      const nextStart =
        (data.next_retstart === null || typeof data.next_retstart === "undefined")
          ? 0
          : Number(data.next_retstart || 0);

      // Stop if no more pages
      if(!hasMore) break;

      // Or stop if backend gave an invalid next offset
      if(!nextStart || nextStart <= start) break;

      // Otherwise continue paging
      start = nextStart;
    } // ✅ closes while(true)

    // ✅ Completed normally (only after loop ends)
    job.running = false;
    job.endedAt = new Date().toISOString();
    job.done = job.ok + job.fail;

    // ✅ force 100% at the end (prevents "Completed" with <100% bar)
    job.total = Math.max(job.total || 0, job.done);

    job.note = `Completed. OK: ${job.ok}. Fail: ${job.fail}.`;
    rbRenderJob(jobId);
    rbPersistSave();


    setRbMsg(`Completed: ${phrase} (OK ${job.ok}, Fail ${job.fail})`);
    await loadOwnerCounts({ silent: true });

  } catch(e){
    console.error(e);
    job.running = false;
    job.endedAt = new Date().toISOString();
    job.note = `Error: ${e.message || e}`;
    rbRenderJob(jobId);
    rbPersistSave();
    setRbMsg(`Error: ${e.message || e}`);
  } finally {
    if(!silent && btn){ btn.disabled = false; btn.style.opacity = ""; }
  }
} // ✅ closes addAllResolverResults(...)



// Multi runner (creates unlimited job bars)
async function addAllResolverResultsMulti(){
  const raw = getRbPhraseRaw();
  const phrases = rbParsePhrases(raw);

  if(!phrases.length){
    setRbMsg("Type at least one phrase.");
    return;
  }

  if(phrases.length === 1){
    await addAllResolverResults({ phraseOverride: phrases[0], retstartOverride: 0, silent: false });
    return;
  }

  // Create bars up-front
  for(const p of phrases){
    const jobId = rbJobIdFromPhrase(p);
    const job = rbGetJob(jobId);
    job.label = p;
    job.running = false;
    job.paused = false;
    job.stopped = false;
    job.done = 0;
    job.total = 0;
    job.ok = 0;
    job.fail = 0;
    job.note = "Queued…";
    job.startedAt = null;
    job.endedAt = null;
    rbRenderJob(jobId);
  }
 rbPersistSave();


  const btn = $("btnRbAddAll");
  if(btn){ btn.disabled = true; btn.style.opacity = "0.7"; }

  const MAX_CONCURRENT = 3;
  let idx = 0;
  let active = 0;

  setRbMsg(`Starting ${phrases.length} job(s)…`);

  return new Promise((resolve)=>{
    const pump = ()=>{
      while(active < MAX_CONCURRENT && idx < phrases.length){
        const p = phrases[idx++];
        active += 1;

        addAllResolverResults({ phraseOverride: p, retstartOverride: 0, silent: true })
          .finally(()=>{
            active -= 1;
            if(idx >= phrases.length && active === 0){
              if(btn){ btn.disabled = false; btn.style.opacity = ""; }
              setRbMsg(`Completed ${phrases.length} job(s).`);
              resolve();
            } else {
              pump();
            }
          });
      }
    };
    pump();
  });
}
window.addAllResolverResultsMulti = addAllResolverResultsMulti;

// Clear Results button (just clears table; no writes)
function rejectAllResolverResults(){
  RB_LAST = { phrase: getRbCurrentPhrase(), source_label: getRbSource(), items: [] };
  window.RB_LAST = RB_LAST;

  if($("rbRows")) $("rbRows").innerHTML = `<tr><td colspan="8" style="padding:10px">Cleared results.</td></tr>`;
  if($("rbRaw")) $("rbRaw").textContent = "Cleared results.";
  setRbMsg("Cleared results (no data written).");

  rbSetText("rbShowing", "—");
  rbSetText("rbTotal", "—");
  rbSetText("rbNextRetstart", "—");
  rbSetDisabled("btnRbPrev", true);
  rbSetDisabled("btnRbNext", true);
}

// Prev/Next behavior (uses currently loaded phrase)
async function rbGoPrev(){
  const limit = getRbLimit();
  const cur = getRbRetstart();
  const step = (limit && limit > 0) ? limit : 200;
  const next = Math.max(0, cur - step);
  if($("rbRetstart")) $("rbRetstart").value = String(next);
  await runResolverBuilderSearch({ retstartOverride: next, phraseOverride: getRbCurrentPhrase() });
}
async function rbGoNext(){
  const next = Number(RB_LAST?.next_retstart ?? (getRbRetstart() + (RB_LAST?.returned || 0)));
  if($("rbRetstart")) $("rbRetstart").value = String(next);
  await runResolverBuilderSearch({ retstartOverride: next, phraseOverride: getRbCurrentPhrase() });
}

function clearResolverBuilderUI(){
  if($("rbPhrase")) $("rbPhrase").value = "";
  if($("rbProvider")) $("rbProvider").value = "pubmed";

  if($("rbLimit")) $("rbLimit").value = "0";
  if($("rbRetstart")) $("rbRetstart").value = "0";

  setRbMsg("");
  if($("rbRaw")) $("rbRaw").textContent = "No search yet.";
  if($("rbRows")) $("rbRows").innerHTML = `<tr><td colspan="8" style="padding:10px">No results yet.</td></tr>`;

  rbSetText("rbShowing", "—");
  rbSetText("rbTotal", "—");
  rbSetText("rbNextRetstart", "—");
  rbSetDisabled("btnRbPrev", true);
  rbSetDisabled("btnRbNext", true);

  RB_LAST = {
    phrase: "",
    source_label: "",
    items: [],
    total_count: 0,
    returned: 0,
    limit: 0,
    retstart: 0,
    next_retstart: 0,
    has_more: false,
  };
  window.RB_LAST = RB_LAST;
}

// ✅ IMPORTANT: you have duplicate id="btnRbClear" (Rollback + Resolver).
// So we must bind by "which section the click happened in".
function initResolverBuilderActions(){
  if(window.__rbActionsInit) return;
  window.__rbActionsInit = true;

  // AddAll + clear results + pager
  $("btnRbAddAll")?.addEventListener("click", addAllResolverResultsMulti);
  $("btnRbRejectAll")?.addEventListener("click", rejectAllResolverResults);
  $("btnRbPrev")?.addEventListener("click", rbGoPrev);
  $("btnRbNext")?.addEventListener("click", rbGoNext);

  // Add one (delegation)
  document.addEventListener("click", async (ev)=>{
    const btn = ev.target?.closest?.('button[data-act="add-one"]');
    if(!btn) return;

    const phrase = getRbCurrentPhrase();
    const source_label = getRbSource() || (RB_LAST.source_label || "pubmed");
    if(!phrase) return setRbMsg("Type a phrase first.");

    const url = String(btn.getAttribute("data-url") || "");
    const title = String(btn.getAttribute("data-title") || "");
    const id = String(btn.getAttribute("data-id") || "");

    try{
      btn.disabled = true;
      btn.style.opacity = "0.7";
      setRbMsg("Adding selection to AUTO…");
      const data = await addOneFromResolverSelection({ phrase, source_label, url, title, id });
      await loadOwnerCounts({ silent: true });


      if($("rbRaw")) $("rbRaw").textContent = JSON.stringify(data, null, 2);
      btn.textContent = "Added";
      setRbMsg(`Saved. title_slug: ${data?.saved_record?.title_slug || "—"}`);
    }catch(e){
      btn.disabled = false;
      btn.style.opacity = "";
      setRbMsg(`Error: ${e.message || e}`);
    }
  });

  // ✅ Clear Resolver Builder (delegation + section check)
  document.addEventListener("click", (ev)=>{
    const c = ev.target?.closest?.("#btnRbClear");
    if(!c) return;

    // Only treat this as resolver-clear if the clicked button is inside the resolver panel
    const inResolver = !!c.closest?.('[data-section="resolver"]');
    if(!inResolver) return;

    ev.preventDefault();
    clearResolverBuilderUI();
  });
}

// ------------------------------
// Import Runs UI
// ------------------------------
function normalizeRunRow(r){
  return {
    ts: r.ts || "",
    run_id: r.import_run_id || "",
    source_label: r.source_label || "",
    auto_added: r.auto_added ?? "",
    auto_updated: r.auto_updated ?? "",
    event: r.event || "",
    snapshot_path: r.snapshot_path || "",
  };
}

async function loadImportRuns(){
  const tbody = $("runsRows");
  const msg = $("runsMsg");
  const limit = parseInt(($("runsLimit")?.value || "20"), 10) || 20;

  if(!tbody) return;

  try{
    if(msg) msg.textContent = "Loading runs...";
    tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">Loading…</td></tr>`;

    const url = `${API_RUNS}?limit=${encodeURIComponent(String(limit))}&_ts=${Date.now()}`;
    const {res, data} = await fetchJson(url, { cache: "no-store" });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner auth required.";
      tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">Owner auth required.</td></tr>`;
      return;
    }

    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }

    const items = Array.isArray(data.items) ? data.items : [];
    if(!items.length){
      tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">No runs found.</td></tr>`;
      if(msg) msg.textContent = "No runs yet.";
      return;
    }

    const commits = items.filter(x => String(x.event || "") === "owner_sitemap_commit_auto");
    const rows = commits.map(normalizeRunRow);

    tbody.innerHTML = rows.slice().reverse().map((r)=>{
      const ts = r.ts;
      const runId = r.run_id || "";
      const label = r.source_label || "";
      const added = String(r.auto_added ?? "");
      const updated = String(r.auto_updated ?? "");
      const note = r.snapshot_path ? "has snapshot" : "";

      const useBtn = runId
        ? `<button data-act="use-run" data-run="${escapeAttr(runId)}"
             style="padding:6px 10px;border-radius:10px;cursor:pointer;background:#0b1220;border:1px solid #1f2937;color:#e5e7eb">
             Use
           </button>`
        : "";

      return `
        <tr>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(ts)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937"><code>${escapeHtml(runId)}</code></td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(label)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(added)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(updated)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937;white-space:nowrap">
            ${useBtn}
            <span style="margin-left:10px;color:#94a3b8">${escapeHtml(note)}</span>
          </td>
        </tr>
      `;
    }).join("");

    tbody.onclick = (ev)=>{
      const btn = ev.target.closest("button[data-act]");
      if(!btn) return;
      const act = btn.getAttribute("data-act");
      if(act === "use-run"){
        const runId = btn.getAttribute("data-run") || "";
        if($("rbRunId")) $("rbRunId").value = runId;
        if($("rbMsg")) $("rbMsg").textContent = "Run ID copied into rollback panel.";
      }
    };

    if(msg) msg.textContent = `Loaded ${rows.length} commit run(s).`;
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
    tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">Failed to load.</td></tr>`;
  }
}

// ------------------------------
// Rollback Panel
// ------------------------------
function getRollbackRunId(){
  return ($("rbRunId")?.value || "").trim();
}

async function rollbackPreviewOrRestore(preview){
  const runId = getRollbackRunId();
  const msg = $("rbMsg");
  const out = $("rbOut");

  if(!runId){
    if(msg) msg.textContent = "Paste a Run ID first.";
    return;
  }

  try{
    if(msg) msg.textContent = preview ? "Previewing..." : "Restoring (this writes)...";
    if(out) out.textContent = preview ? "Previewing...\n" : "Restoring...\n";

    if(!preview){
      const yes = confirm("Restore snapshot for this run? This will overwrite AUTO dataset.");
      if(!yes){
        if(msg) msg.textContent = "Cancelled.";
        return;
      }
    }

    const {res, data} = await fetchJson(API_ROLLBACK, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ import_run_id: runId, preview: !!preview }),
    });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner auth required. Refresh to login.";
      if(out) out.textContent = "Owner auth required.";
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }

    if(out) out.textContent = JSON.stringify(data, null, 2);
    if(msg) msg.textContent = preview ? "Preview loaded." : "Restore completed.";
    if(!preview) await loadOwnerCounts({ silent: true });




    if(!preview){
      await loadImportRuns();
    }
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
    if(out) out.textContent = `Error: ${e.message || e}`;
  }
}

function clearRollback(){
  if($("rbRunId")) $("rbRunId").value = "";
  if($("rbOut")) $("rbOut").textContent = "No rollback yet.";
  if($("rbMsg")) $("rbMsg").textContent = "";
}

// ------------------------------
// Boot
// ------------------------------
window.addEventListener("DOMContentLoaded", async ()=>{
  // nav
  (function initNav(){
    document.querySelectorAll(".navItem[data-nav]").forEach(btn=>{
      btn.addEventListener("click", ()=>{
        const key = btn.getAttribute("data-nav");
        if(key === "external"){
  const sub = document.querySelector(`[data-sub="external"]`);
  if(sub) sub.classList.toggle("isOpen");

  // ✅ do NOT force "manual" — keep current section as-is
  return;
}

        showSection(key);
      });
    });

    document.querySelectorAll(".navSubItem[data-nav]").forEach(btn=>{
      btn.addEventListener("click", ()=>{
        showSection(btn.getAttribute("data-nav"));
      });
    });

    document.querySelectorAll("[data-jump]").forEach(btn=>{
      btn.addEventListener("click", async ()=>{
        const key = btn.getAttribute("data-jump");
        showSection(key);
      });
    });

    
    $("btnRbApplyFilters")?.addEventListener("click", ()=>{
  // re-render current RB_LAST items using the filters
  renderResolverBuilderRows(RB_LAST.items || []);
  setRbMsg(`Filters applied. Showing ${($("rbRows")?.querySelectorAll("tr")?.length || 0) - 0} row(s).`);
});

$("btnRbClearFilters")?.addEventListener("click", ()=>{
  if($("rbYearMin")) $("rbYearMin").value = "";
  if($("rbYearMax")) $("rbYearMax").value = "";
  if($("rbSort")) $("rbSort").value = "relevance";
  renderResolverBuilderRows(RB_LAST.items || []);
  setRbMsg("Filters cleared.");
});




    $("btnLogout")?.addEventListener("click", ownerLogout);
    let last = "overview";
try{
  last = localStorage.getItem(OWNER_LAST_SECTION_KEY) || "overview";
}catch(e){}
showSection(last);

  })();

  // ✅ init resolver builder actions
  initResolverBuilderActions();

 rbPersistLoad();

// ✅ safe call (won't throw ReferenceError)
if (typeof window.rbHistoryRender === "function") window.rbHistoryRender();

$("btnRbClearHistory")?.addEventListener("click", ()=>{
  if (typeof window.rbHistoryClear === "function") window.rbHistoryClear();
});



  // session chip
  setSessionChip(sessionStorage.getItem(OWNER_KEY_STORAGE) ? "ok" : "need");

  // manual
  $("btnSave")?.addEventListener("click", saveManual);
  $("btnRefresh")?.addEventListener("click", loadManual);

  // resolver builder search (NOW supports multi-phrase sequential display)
  $("btnRbSearch")?.addEventListener("click", runResolverBuilderSearchMulti);

  // authority import
  $("btnSmDryRun")?.addEventListener("click", ()=> runSitemapImport(false));
  $("btnSmRun")?.addEventListener("click", ()=> runSitemapImport(true));
  $("btnSmClear")?.addEventListener("click", ()=>{
    if($("smOut")) $("smOut").textContent = "No import yet.";
    if($("smMsg")) $("smMsg").textContent = "";
  });

  // resolver test
  $("btnResolveTest")?.addEventListener("click", runResolveTest);
  $("btnResolveClear")?.addEventListener("click", ()=>{
    if($("rsOut")) $("rsOut").textContent = "No search yet.";
    if($("rsMsg")) $("rsMsg").textContent = "";
  });

  // runs
  $("btnRunsRefresh")?.addEventListener("click", loadImportRuns);

  // rollback
  $("btnRbPreview")?.addEventListener("click", ()=> rollbackPreviewOrRestore(true));
  $("btnRbRestore")?.addEventListener("click", ()=> rollbackPreviewOrRestore(false));

  // ✅ Rollback Clear (delegation + section check) because id="btnRbClear" is duplicated
  document.addEventListener("click", (ev)=>{
  const c = ev.target?.closest?.("#btnRbClearRollback");
  if(!c) return;
  const inRollback = !!c.closest?.('[data-section="rollback"]');
  if(!inRollback) return;
  ev.preventDefault();
  clearRollback();
});


  // login
  const ok = await ownerLoginFlow({ silent: false });
  if(!ok){
    const msg = $("msg");
    if(msg) msg.textContent = "Login cancelled.";
    return;
  }

  // initial loads
  await loadManual();
  await loadOwnerCounts({ silent: true });



  if($("smOut")) $("smOut").textContent = "No import yet.";
  if($("rsOut")) $("rsOut").textContent = "No search yet.";
  if($("rbOut")) $("rbOut").textContent = "No rollback yet.";

  // defaults
  if($("rbLimit") && String($("rbLimit").value || "").trim() === "") $("rbLimit").value = "0";
  if($("rbRetstart") && String($("rbRetstart").value || "").trim() === "") $("rbRetstart").value = "0";
  rbSetDisabled("btnRbPrev", true);
  rbSetDisabled("btnRbNext", true);

  await loadImportRuns();
});
