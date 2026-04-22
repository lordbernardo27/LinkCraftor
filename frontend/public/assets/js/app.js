console.log("APP.JS ACTIVE VERSION: ROOTCHECK-001");

// ---- COMPAT SHIM: hydrateImportsOnLoad calls reloadFromBackend()
if (typeof window.reloadFromBackend !== "function") {
  window.reloadFromBackend = async function reloadFromBackend() {
    try { await window.loadImportedUrlsLocal?.(); } catch (e) {}
    try {
      const ws = getCurrentWorkspaceId("");
      if (ws) await window.updateUnifiedImportCount?.(ws);
    } catch (e) {}
    try {
      return (window.IMPORTED_URLS && window.IMPORTED_URLS.size) ? window.IMPORTED_URLS.size : 0;
    } catch (e) {}
    return 0;
  };
  console.log("[Imports] reloadFromBackend shim installed ");
}
// ---- END SHIM ----


// -------------------------------------------------------------------------------------------
// app.js � LinkCraftor (Full, updated)  ? wired to external_categories.js
// -------------------------------------------------------------------------------------------

import { KEYS, lsGet, lsSet, lsDel } from "./core/storage.js";
import { renderDocInfoPanel as renderDocInfo } from "./sidebar/docinfo.js";
import { initStopwordsUI } from "./ui/stopwords.js";
import { scoreCandidatesForPhrase } from "./engine/scoring.js";
import { shouldHighlightPhrase } from "./features/highlight-filter.js";

// ?? Link Resolution panel (resolved / unresolved phrases)
import { initLinkResolutionPanel, LR_rebuild } from "./sidebar/link-resolution.js";

// ?? Rejections + Linked Phrases (per-phrase undo)
import {
  initRejectionsUI,
  rebuildRejectionsPanel,
  initLinkedPhrasesUI,
  rebuildLinkedPhrasesList
} from "./ui/rejections.js";

import { initBuckets, highlightBucketKeywords, unwrapBucketMarksOnly, getBucketMap } from "./features/buckets.js";
import { initILModal } from "./features/il-modal.js";
import { $, safeSetText, showToast, escapeHtml, escapeRegExp } from "./core/dom.js";
import {
  defaultSettings,
  DEFAULT_STOPWORDS,
  loadSettings as loadSettingsFromStore,
  saveSettings as saveSettingsToStore,
  resetSettings as resetSettingsInStore,
  loadStopwords as loadStopwordsFromStore,
  saveStopwords as saveStopwordsToStore,
  resetStopwords as resetStopwordsInStore,
  loadBuckets as loadBucketsFromStore,
  saveBuckets as saveBucketsToStore,
  resetBuckets as resetBucketsInStore,
} from "./data/settings.js";

import {
  uploadFile as apiUploadFile,
  exportDocx as apiExportDocx,
  downloadOriginalUrl,
  exportZipUrl,
  exportRarUrl
} from "./app/api.js";


// --- LinkCraftor: XML sitemap helper (reads <loc> URLs) ---
// NOTE: kept for compatibility / debugging, not required for backend import flow.
function lcImportSitemapXML(file, onDone) {
  const reader = new FileReader();

  reader.onload = (e) => {
    const text = e.target.result;

    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(text, "application/xml");

    const locNodes = xmlDoc.getElementsByTagName("loc");
    const entries = [];

    for (let i = 0; i < locNodes.length; i++) {
      const url = (locNodes[i].textContent || "").trim();
      if (url) {
        entries.push({ URL: url });
      }
    }

    console.log("? lcImportSitemapXML:", entries);

    if (typeof onDone === "function") {
      onDone(entries);
    }
  };

  reader.readAsText(file);
}



// NOTE: removed static import that could crash the whole app
// import { runExternalEngine } from "./engine/external_helix.js"


/* ==========================================================================
   GLOBALS (Single-mode; prepublish-friendly)
   ========================================================================== */
const DEBUG = false;


const API_BASE =
  (typeof window !== "undefined" && window.LINKCRAFTOR_API_BASE)
    ? String(window.LINKCRAFTOR_API_BASE).replace(/\/+$/, "")
    : "";

function getCurrentWorkspaceId(fallback = "default") {
  return String(
    window.LINKCRAFTOR_WORKSPACE_ID ||
    window.LC_WORKSPACE_ID ||
    localStorage.getItem("lc_workspace_id") ||
    localStorage.getItem("workspace_id") ||
    fallback
  ).trim();
}

// =====================================================
// Layer 1.3 – UI → Decision Ingestion (canonical Layer 0)
// Endpoint: POST /api/engine/decision
// =====================================================
const API_DECISION = "/api/engine/decision";



async function emitDecision(eventType, phraseCtx, candidate, meta){
  try{
    const ws = String((phraseCtx && phraseCtx.workspaceId) || getCurrentWorkspaceId("ws_demo")).trim();
const doc = String((phraseCtx && phraseCtx.docId) || window.LC_ACTIVE_DOC_ID || "doc_demo_001").trim();
const user = String(window.LC_USER_ID || "bernard").trim();

const payload = {
  // ? required by backend model (top-level)
  workspaceId: ws,
  userId: user,
  docId: doc,

  // existing fields
  eventType,
  phraseCtx: phraseCtx || {},
  candidate: candidate || {},
  meta: {
  ts: Date.now(),
  ui: "editor",
  ...(meta || {})
}

};


    const res = await fetch(`${API_BASE}${API_DECISION}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      console.warn("[DECISION] failed", res.status, data);
      return { ok:false, status:res.status, data };
    }

    console.log("[DECISION] ok", eventType, data);
    return { ok:true, data };
  }catch(err){
    console.warn("[DECISION] error", err);
    return { ok:false, error:String(err) };
  }
}

// =====================================================
// Layer 1.3.1 � Global bridge for IL Modal ? Decision API
// IL modal calls window.LC_registerLinkFeedback(...)
// =====================================================
if (typeof window !== "undefined" && typeof window.LC_registerLinkFeedback !== "function") {
  window.LC_registerLinkFeedback = async function(action, data){
    try{
      const eventType = String(data?.eventType || "").trim();
      if (!eventType) return { ok:false, error:"missing eventType" };

      const workspaceId = String(data?.workspaceId || getCurrentWorkspaceId("default")).trim();
      const docId       = String(data?.docId || window.LC_ACTIVE_DOC_ID || "").trim();

      const phraseText  = String(data?.phraseText || "").trim();
      const targetId    = String(data?.targetId || "").trim();
      const url         = String(data?.url || "").trim();
      const title       = String(data?.title || "").trim();
      const kind        = String(data?.kind || "").trim();

      const phraseCtx = {
        workspaceId,
        docId,
        phraseText,
        contextType: data?.contextType || null,
        sectionType: data?.sectionType || "BODY",
        intent: data?.intent || "INFO",
        entities: Array.isArray(data?.entities) ? data.entities : []
      };

      const candidate = {
        id: targetId || "",
        title: title || "",
        url: url || "",
        sourceType: kind || "ui",
        isExternal: (kind === "external"),
        topicTypes: Array.isArray(data?.topicTypes) ? data.topicTypes : [],
        entities: Array.isArray(data?.candidateEntities) ? data.candidateEntities : []
      };

      // Use the canonical helper already in app.js
      if (typeof emitDecision === "function") {
        return await emitDecision(eventType, phraseCtx, candidate, {
          action: action || "ui",
          ui: "il-modal"
        });
      }

      return { ok:false, error:"emitDecision not available" };
    }catch(e){
      console.warn("[LC_registerLinkFeedback] failed", e);
      return { ok:false, error:String(e) };
    }
  };
}




// ================================
// Backend URLs API base (single source of truth)
// ================================
const URLS_API_BASE =
  (API_BASE && String(API_BASE).trim())
    ? String(API_BASE).replace(/\/+$/, "")
    : "http://127.0.0.1:8001";


async function apiEngineRun(payload){

  // ---- RB2 TARGETS AUTOFILL (fix internal/semantic highlights) ----
  try {
    const t = payload && payload.targets;
    const empty = !Array.isArray(t) || t.length === 0;

    if (empty) {
      const rows =
        (typeof window.LC_getImportedTopics === "function"
          ? window.LC_getImportedTopics()
          : (Array.isArray(window.LC_IMPORTS) ? window.LC_IMPORTS : []));

      if (Array.isArray(rows) && rows.length) {
        payload.targets = rows
          .map(r => {
            const url = r && r.url ? String(r.url).trim() : "";
            const title = r && r.title ? String(r.title).trim() : "";
            if (!url || !title) return null;
            return { url, title, aliases: [], inboundLinks: 0 };
          })
          .filter(Boolean);

        console.log("[RB2 FIX] Autofilled targets from imports:", payload.targets.length);
      } else {
        console.warn("[RB2 FIX] No imports available to autofill targets");
      }
    }
  } catch (e) {
    console.warn("[RB2 FIX] Autofill failed", e);
  }
  // ---- END RB2 TARGETS AUTOFILL ----

  console.log("[RB2 PAYLOAD CHECK]", {
    __rb2_capture: (() => {
      try {
        window.__RB2_LAST_PAYLOAD = payload;
        const n = (payload && payload.targets) ? payload.targets.length : null;
        console.log("[RB2 DEBUG] UI targets length =", n);
        return n;
      } catch (e) {
        console.warn("[RB2 DEBUG] capture failed", e);
        return null;
      }
    })(),
    hasHtml: !!(payload && payload.html && String(payload.html).trim()),
    hasText: !!(payload && payload.text && String(payload.text).trim()),
    targetsType: payload && payload.targets ? Object.prototype.toString.call(payload.targets) : null,
    targetsLen: Array.isArray(payload?.targets) ? payload.targets.length : null,
    sampleTarget0: Array.isArray(payload?.targets) ? (payload.targets[0] || null) : null,
    keys: payload ? Object.keys(payload) : null
  });

  const base = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");

  // ---- TARGET NORMALIZATION (restores internal/strong lexical grounding) ----
  function __lc_slugToTitle(u) {
    try {
      const x = new URL(String(u || ""));
      const parts = (x.pathname || "").split("/").filter(Boolean);
      const last = (parts[parts.length - 1] || "").trim();
      if (!last) return "";
      return last.replace(/[-_]+/g, " ").replace(/\s+/g, " ").trim();
    } catch {
      return "";
    }
  }

  function __lc_normTarget(t) {
    const url = String(t?.url || t?.href || "").trim();
    let title = String(t?.title || "").trim();
    if (!title && url) title = __lc_slugToTitle(url);

    const aliasesRaw = Array.isArray(t?.aliases) ? t.aliases : [];
    const aliases = aliasesRaw.map(a => String(a || "").trim()).filter(Boolean);

    if (title && !aliases.includes(title)) aliases.unshift(title);

    return {
      url,
      title,
      aliases,
      inboundLinks: Number(t?.inboundLinks || t?.inlinks || 0) || 0
    };
  }

  // normalize payload.targets so RB2 can produce internal/strong again
  payload.targets = Array.isArray(payload?.targets) ? payload.targets.map(__lc_normTarget) : [];
  console.log("[RB2 TARGETS NORMALIZED] first5=",
    payload.targets.slice(0, 5).map(x => ({ title: x.title, aliases_len: x.aliases.length }))
  );
  // ---- END TARGET NORMALIZATION ----

  // ? IMPORTANT FIX: correct backend RB2 route
  const res = await fetch(`${base}/api/engine/run`, {

    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify({
      html: payload?.html || "",
      text: payload?.text || "",
      workspaceId: payload?.workspaceId || getCurrentWorkspaceId("default"),
      limit: payload?.limit || 50,
      targets: Array.isArray(payload?.targets) ? payload.targets : [],
      include: (payload?.include && typeof payload.include === "object") ? payload.include : {},
      block: Array.isArray(payload?.block) ? payload.block : [],
      synonyms: (payload?.synonyms && typeof payload.synonyms === "object") ? payload.synonyms : {},
      config: (payload?.config && typeof payload.config === "object") ? payload.config : {}
    })
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);
if (!data || data.ok !== true) throw new Error(data?.error || "RB2 backend returned ok:false");

const out = data || {};
  try { window.__RB2_LAST_OUT = out; } catch (e) {}

  console.log("[RB2 BACKEND OUT JSON]", JSON.stringify(out, null, 2));

  console.log("[RB2 SAMPLE strong[0]]", (out.internal_strong && out.internal_strong[0]) || null);
console.log("[RB2 SAMPLE optional[0]]", (out.semantic_optional && out.semantic_optional[0]) || null);

  return {
  recommended: Array.isArray(out.internal_strong) ? out.internal_strong : [],
  optional: Array.isArray(out.semantic_optional) ? out.semantic_optional : [],
  external: [],
  hidden: Array.isArray(out.hidden) ? out.hidden : [],
  meta: (out.meta && typeof out.meta === "object") ? out.meta : {}
};
}




// ================================
// URL / SITEMAP IMPORT (BACKEND)
// ================================
async function apiImportUrlsFile(file, workspaceId = "default") {
  const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
  const fd = new FormData();
  fd.append("file", file);

  const res = await fetch(
    `${API_BASE}/api/urls/import?workspace_id=${encodeURIComponent(workspaceId)}`,
    { method: "POST", body: fd }
  );

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);
  return data; // { ok, added, total, ... } (depends on backend)
}

async function apiLoadImportedUrls(workspaceId = "default", limit = 200000) {
  const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
  const res = await fetch(
    `${API_BASE}/api/urls/list?workspace_id=${encodeURIComponent(workspaceId)}&limit=${encodeURIComponent(limit)}`
  );

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);

  // Be tolerant to backend field names
  const arr =
    (Array.isArray(data.urls) && data.urls) ||
    (Array.isArray(data.items) && data.items) ||
    [];

  // Ensure it's an array of strings
  return arr.map(x => String(x || "").trim()).filter(Boolean);
}

function setImportCount(value = 0) {
  try {
    const el = document.getElementById("importCount");
    if (el) el.textContent = String(Number(value) || 0);
  } catch {}
}

async function updateUnifiedImportCount(workspaceId = "default") {
  try {
    const base = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");

    // A) URLs (sitemap/backup) count
    const r1 = await fetch(`${base}/api/urls/list?workspace_id=${encodeURIComponent(workspaceId)}&limit=200000`);
    const d1 = await r1.json().catch(() => ({}));
    const urlCount = (r1.ok && Array.isArray(d1.urls)) ? d1.urls.length : 0;

    // B) Draft topics count
    const r2 = await fetch(`${base}/api/draft/list?workspace_id=${encodeURIComponent(workspaceId)}&limit=200000`);
    const d2 = await r2.json().catch(() => ({}));
    const draftCount = (r2.ok && Array.isArray(d2.topics)) ? d2.topics.length : 0;

    // ? Unified total into the EXISTING badge
    const el = document.getElementById("importCount");
    setImportCount(urlCount + draftCount);

    return { ok: true, urlCount, draftCount, total: urlCount + draftCount };
  } catch (e) {
    console.warn("[importCount] unified count failed:", e?.message || e);
    return { ok: false, error: String(e) };
  }
}



// Engine caps
const MAX_UNIQUE_PHRASES = 30;        // per pass (internal)
const MAX_TOTAL_HIGHLIGHTS = 200;     // hard cap across the whole doc
const APPLY_ALL_PASS_LIMIT = 30;      // safety guard

// Per-phrase cap: how many times the same phrase can be highlighted per doc
const MAX_HITS_PER_PHRASE = 2;  // you can later change to 1, 2, or 3 as you prefer


// Phase (prepublish by default; you can flip this via localStorage if needed)
const PHASE_KEY = "linkcraftor_phase_v2";
const PHASE = (localStorage.getItem(PHASE_KEY) || "prepublish") === "publish" ? "publish" : "prepublish";

/* LOCKED THRESHOLDS (as agreed) */
const FLOORS = (PHASE === "publish")
  ? { STRONG: 0.75, OPTIONAL: 0.65, MIN_OVERLAP: 2 }
  : { STRONG: 0.70, OPTIONAL: 0.60, MIN_OVERLAP: 1 };

const CAPS = Object.freeze({ MAX_PER_SECTION: 4, MAX_PER_200W: 5, MAX_PER_TOPIC: 3 });

// Spacing radius for mark placement (�words)
const WINDOW_RADIUS_WORDS = 90;

/* ==========================================================================
   NEW: External V2 (local, rule-based) � mirrors internal placement logic
   ========================================================================== */
const EXT_V2 = Object.freeze({
  ENABLED: true,
  THRESHOLDS: Object.freeze({
    MIN_TOKENS: 3,
    MAX_TOKENS: 16,
    MIN_CONTENT_RATIO: 0.55,
    MIN_DOC_FREQ: 1,
    HEADING_BOOST: 0.06,
    NOVELTY_PENALTY: 0.12,
    STRONG: 0.70,
    OPTIONAL: 0.50
  }),
  CAPS: Object.freeze({
    MAX_TOTAL: 24,
    MAX_PER_SECTION: 1,
    MAX_PER_200W: 2
  }),
  BLOCK_SINGLE_TOKEN_UPPERCASE: true,
  RESPECT_REJECTIONS: true,
  HONOR_BUCKETS: true,
});

/* ==========================================================================
   STATE
   ========================================================================== */
const docs = [];
let currentIndex = -1;
let highlightsArmed = false;
let applyingAll = false;

let STOPWORDS = new Set(DEFAULT_STOPWORDS);

// --- Session format lock (null until first upload) ---
let SESSION_FORMAT = null; // ".docx" | ".md" | ".html" | ".txt"

// Extract lowercase extension (includes leading dot, e.g., ".docx")
function extOf(name = "") {
  return (String(name).match(/\.[^.]+$/)?.[0] || "").toLowerCase();
}



let LINKED_SET = new Set();          // phrases accepted (normalized)
let LINKED_MAP = new Map();          // phraseNorm -> Set(urls or tokens)
let APPLIED_LINKS = [];              // [{phrase, sectionIdx, topicId, title, url, kind}] for manifest

let IMPORTED_URLS = new Set();       // raw list (legacy; still used)
let PUBLISHED_TOPICS = new Map();    // url -> { id, url, title, slugTokens, inlinks?, depth?, aliases[] }
let DRAFT_TOPICS = new Map();

let TITLE_INDEX = new Map();         // (kept for same-doc heuristics)
let TITLE_ALIAS_MAP = new Map();

// Cache for scraped sitemap page content: url -> { url, title, text, tokens }
const SITEMAP_CONTENT = new Map();

// Expose for console debugging
if (typeof window !== "undefined") {
  window.SITEMAP_CONTENT = SITEMAP_CONTENT;
}


let CURRENT_MARK = null;
let CURRENT_PHRASE = "";

function setCurrentMark(el) { CURRENT_MARK = el; }
function setCurrentPhrase(s) { CURRENT_PHRASE = s; }
function getCurrentMark() { return CURRENT_MARK; }
function getCurrentPhrase() { return CURRENT_PHRASE; }
function getViewerEl() { return viewerEl; }
function getLastEngineOutput() { return LAST_ENGINE_OUTPUT; } // not strictly required, but handy


let highlightEnabled = true;

let LAST_ENGINE_OUTPUT = { recommended: [], optional: [], external: [], hidden: [], meta: {} };

// ---------------------------------------------------------------------------
// External references bridge for IL modal
// Uses window.LinkcraftorExternalRefs defined in external_helix.js
// ---------------------------------------------------------------------------
let REF_API = null;

async function ensureReferencesModule() {
  // If already loaded, reuse
  if (REF_API) return REF_API;

  // Prefer global from external_helix.js
  if (window.LinkcraftorExternalRefs) {
    REF_API = window.LinkcraftorExternalRefs;
    console.log("[refs] using window.LinkcraftorExternalRefs");
    return REF_API;
  }

  // Fallback: nothing available
  console.warn("[refs] No external references module available");
  return null;
}



// SAFE dynamic loader for the External HELIX engine (legacy; no longer used in pipeline)
let RUN_EXT_ENGINE = null;
let EXTERNAL_ENGINE_OK = false;
async function ensureExternalHelix() {
  if (RUN_EXT_ENGINE) return RUN_EXT_ENGINE;
  try {
    const mod = await import("./engine/external_helix.js");
    RUN_EXT_ENGINE = mod.runExternalEngine || mod.default;
    if (typeof RUN_EXT_ENGINE !== "function") {
      throw new Error("runExternalEngine export missing");
    }
    EXTERNAL_ENGINE_OK = true;
  } catch (e) {
    EXTERNAL_ENGINE_OK = false;
    console.warn("[external_helix] not available:", e);
    // Fallback no-op; we no longer depend on this module
    RUN_EXT_ENGINE = async () => ({ tokens: [] });
  }
  return RUN_EXT_ENGINE;
}

/* ==========================================================================
   UI HOOKS
   ========================================================================== */
const fileInput = $("file");
const sitemapFile = $("sitemapFile");
const draftFile = $("draftFile");
const btnImportMap = $("btnImportMain"); // ? correct ID in your HTML
const btnImportDraft = $("btnImportDraft");

const allDocs = $("allDocs");
const editor = $("editor");
const viewerEl = $("doc-content");


const topMeta = $("topMeta");
const docMeta = $("docMeta");
const docCountMeta = $("docCountMeta");
const errorBox = $("error");
const toggleHighlight = $("toggleHighlight");
const highlightCountBadge = $("highlightCountBadge");

// ============================================================================
// Draft + Sitemap Audit (Right Sidebar Card) � no new button
// Combines:
//  A) Draft ? Sitemap audit (backend truth)
//  B) Topics NOT matched to a phrase (this doc/run) using LAST_ENGINE_OUTPUT
// ============================================================================
(function wireDraftSitemapAuditCard(){
  const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");

  function esc(s){ return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  function normUrl(u){
    u = String(u||"").trim();
    u = u.split("#",1)[0];
    if (u.endsWith("/") && u.length > 8) u = u.replace(/\/+$/, "");
    return u;
  }

  function getRightSidebar(){
    // Your HTML uses: <aside class="right">
    return document.querySelector("aside.right");
  }

  function ensureCard(){
    const side = getRightSidebar();
    if (!side) {
      console.warn("[AuditCard] sidebar <aside.right> not found");
      return null;
    }

    let card = document.getElementById("draftSitemapAuditCard");
    if (card) return card;

    card = document.createElement("div");
    card.className = "card";
    card.id = "draftSitemapAuditCard";

    card.innerHTML = `
  <h3 style="display:flex;align-items:center;gap:8px;">
    Draft + Sitemap Audit
    <span class="spacer"></span>

    <label for="auditFilter" style="font-size:12px;color:#374151;display:flex;gap:6px;align-items:center;">
      Filter:
      <select id="auditFilter" style="font-size:12px;padding:2px 6px;border:1px solid var(--il-border);border-radius:8px;">
        <option value="all" selected>All</option>
        <option value="missing">Missing drafts</option>
        <option value="matched">Matched drafts</option>
        <option value="unmatched">Unmatched topics (this doc)</option>
      </select>
    </label>

    <button id="auditRefreshBtn" class="ghost" type="button">Refresh</button>
  </h3>

  <div id="auditStats" style="font-size:12px;color:#6b7280;margin-top:6px;">
    Loading�
  </div>

  <div id="auditList" style="margin-top:10px;">
    <div style="font-size:12px;color:#6b7280;">No items yet.</div>
  </div>

  <div id="auditHint" style="margin-top:10px;font-size:12px;color:#6b7280;">
    Tip: Use the filter to switch between draft gaps and sitemap topics that didn�t match any phrase in this doc.
  </div>
`;


    // Insert after the "Link Resolution" card (last), or just append
    side.appendChild(card);
    return card;
  }

  async function fetchAudit(){
    const ws = getCurrentWorkspaceId("default");
const res = await fetch(`${API_BASE}/api/planning/draft_audit?workspace_id=${encodeURIComponent(ws)}&limit=5000`);
    const data = await res.json().catch(()=>({}));
    if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);
    return data;
  }

 function renderDraftRows(rows, el, limit = 50) {
  if (!el) return;

  // ? HARDEN: rows must be an array
  const safeRows = Array.isArray(rows) ? rows : [];

  if (!safeRows.length) {
    el.innerHTML = `<div style="opacity:.65">None</div>`;
    return;
  }

  // ? HARDEN: limit must be a finite number
  const lim = Number.isFinite(Number(limit)) ? Number(limit) : 50;

  const cut = safeRows.slice(0, lim);

  el.innerHTML = (Array.isArray(cut)?cut:[]).map((r) => {
    const title = esc((r && (r.working_title || r.topic_id)) || "");
    const url = esc((r && r.planned_url) || "");
    return `
      <div style="padding:6px 0;border-bottom:1px solid #f3f4f6;">
        <div style="font-weight:600;font-size:12px;">${title}</div>
        ${url ? `<div style="font-size:11px;opacity:.85;word-break:break-all;">${url}</div>` : ""}
      </div>
    `;
  }).join("");
}


   function findBestPhraseForUrl(targetUrl){
    const out = (typeof LAST_ENGINE_OUTPUT !== "undefined" && LAST_ENGINE_OUTPUT) ? LAST_ENGINE_OUTPUT : null;
    if (!out) return null;

    const target = normUrl(targetUrl);
    if (!target) return null;

    const pool = [];
    const add = (arr) => {
      if (!Array.isArray(arr)) return;
      for (const it of arr){
        const u = normUrl(it?.url || it?.href || "");
        if (!u || u !== target) continue;

        const phrase =
          (it.phrase || it.keyword || it.text || it.anchor || it.phraseText || "").toString().trim();

        if (!phrase) continue;

        pool.push({
          phrase,
          score: Number(it.score ?? it.confidence ?? it.finalScore ?? 0) || 0,
        });
      }
    };

    add(out.recommended);
    add(out.optional);
    add(out.external);

    if (!pool.length) return null;

    pool.sort((a,b)=> b.score - a.score);
    return pool[0].phrase;
  }

  function collectSuggestedUrls(){
    // Reads from your global LAST_ENGINE_OUTPUT which your engine updates
    const out = (typeof LAST_ENGINE_OUTPUT !== "undefined" && LAST_ENGINE_OUTPUT) ? LAST_ENGINE_OUTPUT : null;
    const s = new Set();
    if (!out) return s;

    function add(list){
      if (!Array.isArray(list)) return;
      for (const it of list){
        const url = (it && (it.url || it.href)) ? String(it.url || it.href).trim() : "";
        const nu = normUrl(url);
        if (nu) s.add(nu);
      }
    }

    add(out.recommended);
    add(out.optional);
    add(out.external);

    return s;
  }


  function renderUnmatchedTopics(el){
    if (!el) return;

    const imported = (typeof IMPORTED_URLS !== "undefined" && IMPORTED_URLS) ? Array.from(IMPORTED_URLS) : [];
    const importedNorm = imported.map(normUrl).filter(Boolean);

    const suggested = collectSuggestedUrls(); // normalized already
    const unmatched = importedNorm.filter(u => !suggested.has(u));

    if (!unmatched.length) {
      el.innerHTML = `<div style="opacity:.65">None</div>`;
      return;
    }

    const limit = 60;
    const cut = unmatched.slice(0, limit);

    el.innerHTML =
  `<div style="margin-bottom:6px;opacity:.9;">
    Imported: <strong>${importedNorm.length}</strong> |
    Suggested (this doc): <strong>${suggested.size}</strong> |
    Unmatched: <strong>${unmatched.length}</strong>
  </div>` +

(Array.isArray(cut)?cut:[]).map(u => {
  const phrase = findBestPhraseForUrl(u);
  const has = !!phrase;

  const badge = has
    ? `<span style="font-size:10px;padding:2px 6px;border-radius:999px;border:1px solid #bbf7d0;background:#ecfdf5;color:#065f46;">Phrase found</span>`
    : `<span style="font-size:10px;padding:2px 6px;border-radius:999px;border:1px solid #e5e7eb;background:#f9fafb;color:#6b7280;">No match</span>`;

  return `
    <button
      type="button"
      class="ghost"
      data-audit-url="${esc(u)}"
      data-has-phrase="${has ? "1" : "0"}"
      title="${has ? esc(phrase) : "No phrase match"}"
      style="width:100%;text-align:left;padding:6px 8px;margin:0;border:0;background:transparent;border-bottom:1px solid #f3f4f6;cursor:pointer;">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
        <div style="font-size:11px;word-break:break-all;flex:1;">${esc(u)}</div>
        ${badge}
      </div>
    </button>
  `;
}).join("")
 
  (unmatched.length > limit ? `<div style="opacity:.7;margin-top:6px;">+ ${unmatched.length - limit} more�</div>` : "");
  }


function renderDraftRows(rows, mountEl, limit = 120){
  try{
    if (!mountEl) return;

    const arr = Array.isArray(rows) ? rows : [];
    const cut = arr.slice(0, Math.max(0, Number(limit) || 0));

    if (!cut.length){
      mountEl.innerHTML = `<div style="opacity:.65;font-size:12px;">None</div>`;
      return;
    }

    mountEl.innerHTML = (Array.isArray(cut)?cut:[]).map((r) => {
      // Support either string rows or object rows
      const obj = (r && typeof r === "object") ? r : null;

      const url =
        obj && (obj.url || obj.href || obj.target_url || obj.targetUrl)
          ? String(obj.url || obj.href || obj.target_url || obj.targetUrl).trim()
          : (typeof r === "string" ? String(r).trim() : "");

      const title =
        obj && (obj.title || obj.h1 || obj.name)
          ? String(obj.title || obj.h1 || obj.name).trim()
          : "";

      const phrase =
        obj && (obj.phrase || obj.anchor || obj.keyword)
          ? String(obj.phrase || obj.anchor || obj.keyword).trim()
          : "";

      const reason =
        obj && (obj.reason || obj.status || obj.note)
          ? String(obj.reason || obj.status || obj.note).trim()
          : "";

      const safeUrl = esc(url || "");
      const safeTitle = esc(title || "");
      const safePhrase = esc(phrase || "");
      const safeReason = esc(reason || "");

      // If we have a URL, make it clickable (same click handler you already wired)
      const dataUrlAttr = url ? `data-audit-url="${safeUrl}"` : "";

      const rightBadge = safePhrase
        ? `<span style="font-size:10px;padding:2px 6px;border-radius:999px;border:1px solid #bfdbfe;background:#eff6ff;color:#1d4ed8;">${safePhrase}</span>`
        : (safeReason
            ? `<span style="font-size:10px;padding:2px 6px;border-radius:999px;border:1px solid #e5e7eb;background:#f9fafb;color:#6b7280;">${safeReason}</span>`
            : `<span style="font-size:10px;padding:2px 6px;border-radius:999px;border:1px solid #e5e7eb;background:#f9fafb;color:#6b7280;">Draft</span>`);

      const mainLine = safeTitle || safeUrl || `(unknown)`;

      return `
        <button
          type="button"
          class="ghost"
          ${dataUrlAttr}
          style="width:100%;text-align:left;padding:6px 8px;margin:0;border:0;background:transparent;border-bottom:1px solid #f3f4f6;cursor:${url ? "pointer" : "default"};">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
            <div style="font-size:11px;word-break:break-word;flex:1;line-height:1.25;">
              <div style="font-weight:600;">${mainLine}</div>
              ${safeUrl && safeTitle ? `<div style="opacity:.7;word-break:break-all;">${safeUrl}</div>` : ``}
            </div>
            ${rightBadge}
          </div>
        </button>
      `;
    }).join("");
  } catch(e){
    console.warn("[renderDraftRows] failed:", e?.message || e);
    if (mountEl) mountEl.innerHTML = `<div style="font-size:12px;color:#6b7280;">�</div>`;
  }
}



 async function refreshCard(){
  ensureCard();

  const stats  = document.getElementById("auditStats");
  const listEl = document.getElementById("auditList");

  const card   = document.getElementById("draftSitemapAuditCard");
  const filterEl = card ? card.querySelector("#auditFilter") : null;

  if (!listEl) return;

  try {
    if (stats) stats.textContent = "Loading�";

    const data = await fetchAudit();

            // -------------------------------------------------------------------
    // FALLBACK MATCHER (client-side, self-contained)
    // Matches drafts to imported sitemap URLs by final slug, ignoring:
    // - "/drafts/" path segment in draft planned_url
    // - "Drafts " prefix in working_title
    // -------------------------------------------------------------------
    (async function applyLocalAuditFallback(){
      try {
        // Only run fallback if backend has no matches
        const matchedArr = Array.isArray(data?.matched) ? data.matched : [];
        if (matchedArr.length > 0) return;

        // Gather imports from the canonical place your backend hydrate uses
        const importedSet =
          (window.IMPORTED_URLS && window.IMPORTED_URLS instanceof Set) ? window.IMPORTED_URLS :
          ((typeof IMPORTED_URLS !== "undefined" && IMPORTED_URLS instanceof Set) ? IMPORTED_URLS : null);

        // If imports not ready, attempt one hydrate (race-proof)
        if ((!importedSet || importedSet.size === 0) && typeof window.__LC_reloadFromBackend === "function") {
          try { await window.__LC_reloadFromBackend(); } catch {}
        }

        const importedSet2 =
          (window.IMPORTED_URLS && window.IMPORTED_URLS instanceof Set) ? window.IMPORTED_URLS :
          ((typeof IMPORTED_URLS !== "undefined" && IMPORTED_URLS instanceof Set) ? IMPORTED_URLS : null);

        const imported = importedSet2 ? Array.from(importedSet2) : [];
        if (!imported.length) {
          console.log("[AuditCard] FALLBACK skipped: no imported URLs available");
          return;
        }

        // Drafts: prefer explicit list from payload; otherwise use "missing"
        const missingArr = Array.isArray(data?.missing) ? data.missing : [];
        const draftsRaw =
          (Array.isArray(data?.drafts) ? data.drafts :
          (Array.isArray(data?.draft_topics) ? data.draft_topics :
          (Array.isArray(data?.topics) ? data.topics : [])));

        const drafts = draftsRaw.length ? draftsRaw : missingArr;
        if (!Array.isArray(drafts) || drafts.length === 0) {
          console.log("[AuditCard] FALLBACK skipped: no drafts available");
          return;
        }

        function normText(s){
          return String(s || "")
            .toLowerCase()
            .replace(/&/g, " and ")
            .replace(/['"]/g, "")
            .replace(/[^a-z0-9\s-]/g, " ")
            .replace(/\s+/g, " ")
            .trim();
        }

        function slugifyLite(s){
          return normText(s)
            .replace(/\s+/g, "-")
            .replace(/-+/g, "-")
            .replace(/^-|-$/g, "");
        }

        function stripDraftsPrefix(title){
          return String(title || "").replace(/^drafts?\s+/i, "").trim();
        }

        function urlLastSlug(u){
          try{
            const url = String(u || "").trim();
            if (!url) return "";
            const clean = url.split("#")[0].split("?")[0].replace(/\/+$/, "");
            const parts = clean.split("/").filter(Boolean);
            return String(parts[parts.length - 1] || "").toLowerCase();
          } catch {
            return "";
          }
        }

        // Build imported slug -> url map
        const importedSlugSet = new Set();
        const slugToImportedUrl = new Map();

        for (const u of imported) {
          const slug = urlLastSlug(u);
          if (!slug) continue;
          importedSlugSet.add(slug);
          if (!slugToImportedUrl.has(slug)) slugToImportedUrl.set(slug, u);
        }

        const outMatched = [];
        const outMissing = [];

        for (const d of drafts) {
          const obj = (d && typeof d === "object") ? d : { working_title: String(d || "") };

          const plannedUrl = String(obj.planned_url || obj.plannedUrl || obj.url || "").trim();
          const slugFromPlanned = urlLastSlug(plannedUrl);

          // 1) Match by planned_url slug (best)
          if (slugFromPlanned && importedSlugSet.has(slugFromPlanned)) {
            outMatched.push({
              ...obj,
              title: obj.working_title || obj.title || "",
              url: slugToImportedUrl.get(slugFromPlanned) || "",
              reason: "local-planned-url-slug-match"
            });
            continue;
          }

          // 2) Match by cleaned working_title
          const rawTitle = String(obj.working_title || obj.title || obj.h1 || obj.name || obj.topic || "").trim();
          const cleanTitle = stripDraftsPrefix(rawTitle);
          const titleSlug = slugifyLite(cleanTitle);

          if (titleSlug && importedSlugSet.has(titleSlug)) {
            outMatched.push({
              ...obj,
              title: rawTitle,
              url: slugToImportedUrl.get(titleSlug) || "",
              reason: "local-title-slug-match"
            });
            continue;
          }

          outMissing.push({
            ...obj,
            title: rawTitle,
            reason: "no-slug-match"
          });
        }

        data.matched = outMatched;
        data.missing = outMissing;

        console.log("[AuditCard] FALLBACK applied:", {
          imported: imported.length,
          drafts: drafts.length,
          matched: outMatched.length,
          missing: outMissing.length
        });

      } catch (e) {
        console.log("[AuditCard] FALLBACK failed:", e?.message || e);
      }
    })();



    const c = data.counts || {};

        // If fallback modified matched/missing arrays, reflect that in the displayed stats
    const uiMissing = Array.isArray(data?.missing) ? data.missing.length : (c.missing ?? "-");
    const uiMatched = Array.isArray(data?.matched) ? data.matched.length : (c.matched ?? "-");



    if (stats){
      stats.innerHTML = `
        <div>Sitemap URLs: <strong>${c.sitemap_urls ?? "-"}</strong></div>
        <div>Draft topics: <strong>${c.draft_topics_total ?? "-"}</strong></div>
        <div>Missing: <strong>${uiMissing}</strong> | Matched: <strong>${uiMatched}</strong></div>

      `;
    }

    // clear list every refresh
    listEl.innerHTML = "";

    const mode = String(filterEl?.value || "all").trim(); // all | missing | matched | unmatched

    if (mode === "missing") {
      renderDraftRows(Array.isArray(data.missing) ? data.missing : [], listEl, 120);
      return;
    }

    if (mode === "matched") {
      renderDraftRows(Array.isArray(data.matched) ? data.matched : [], listEl, 120);
      return;
    }

    if (mode === "unmatched") {
      renderUnmatchedTopics(listEl);
      return;
    }

    // Default: ALL (stacked)
    listEl.innerHTML = `
      <div style="font-weight:700;font-size:12px;margin-bottom:6px;">Missing drafts</div>
      <div id="auditAllMissing"></div>

      <div style="height:10px;"></div>

      <div style="font-weight:700;font-size:12px;margin-bottom:6px;">Matched drafts</div>
      <div id="auditAllMatched"></div>

      <div style="height:10px;"></div>

      <div style="font-weight:700;font-size:12px;margin-bottom:6px;">Unmatched topics (this doc)</div>
      <div id="auditAllUnmatched"></div>
    `;

    renderDraftRows(Array.isArray(data.missing) ? data.missing : [], document.getElementById("auditAllMissing"), 50);
    renderDraftRows(Array.isArray(data.matched) ? data.matched : [], document.getElementById("auditAllMatched"), 50);
    renderUnmatchedTopics(document.getElementById("auditAllUnmatched"));

    console.log("[AuditCard] refreshed", c);

  } catch(e){
    console.warn("[AuditCard] refresh failed:", e?.message || e);
    if (stats) stats.textContent = "Audit failed: " + (e?.message || e);
    listEl.innerHTML = `<div style="font-size:12px;color:#6b7280;">�</div>`;
  }
}


  // DOM ready init
  document.addEventListener("DOMContentLoaded", ()=>{
    ensureCard();
    refreshCard();

    const btn = document.getElementById("auditRefreshBtn");
    if (btn && btn.dataset.bound !== "1") {
      btn.dataset.bound = "1";
      btn.addEventListener("click", refreshCard);
    }
  });

  // Click unmatched URL -> open IL modal with URL prefilled
const card = document.getElementById("draftSitemapAuditCard");
if (card && card.dataset.urlClickBound !== "1") {
  card.dataset.urlClickBound = "1";

 card.addEventListener("click", (e) => {
  const btn = e.target?.closest?.("[data-audit-url]");
  if (!btn) return;

  const url = String(btn.getAttribute("data-audit-url") || "").trim();
  if (!url) return;

  // Try to find a phrase already mapped to this URL by the engine
  const bestPhrase = findBestPhraseForUrl(url);

  // Open IL modal
  const modal = document.getElementById("ilModal");
  const urlInput = document.getElementById("ilUrl");
  const titleInput = document.getElementById("ilTitle");
  const searchInput = document.getElementById("ilSearch");
  const keywordChip = document.getElementById("ilKeyword");
  const textInput = document.getElementById("ilText");

  // URL is ALWAYS prefilled
  if (urlInput) urlInput.value = url;

  if (bestPhrase) {
    // ? URL MATCHED A PHRASE ? PREFILL
    if (keywordChip) keywordChip.textContent = bestPhrase;
    if (textInput) textInput.value = bestPhrase;
    if (titleInput) titleInput.value = "";

    console.log("[AuditCard] Prefilled phrase:", bestPhrase, "for", url);
  } else {
    // ? NO MATCH ? LEAVE PHRASE EMPTY
    if (keywordChip) keywordChip.textContent = "";
    if (textInput) textInput.value = "";
    if (titleInput) titleInput.value = "";

    console.log("[AuditCard] No phrase match for URL:", url);
  }

  if (modal) modal.style.display = "flex";

  // Focus intelligently
  setTimeout(() => {
    try {
      (bestPhrase ? (titleInput || urlInput) : (searchInput || titleInput || urlInput))?.focus?.();
    } catch {}
  }, 50);
});

}


   const f = document.getElementById("auditFilter");
if (f && f.dataset.bound !== "1") {
  f.dataset.bound = "1";
  f.addEventListener("change", refreshCard);
}


  // Expose a hook so we can refresh after engine runs (optional)
  window.__LC_REFRESH_AUDIT_CARD__ = refreshCard;
})();




/* NEW: engine filter in the highlights panel */
const engineFilter = $("engineFilter");

const btnPrevDoc = $("btnPrevDoc");
const btnNextDoc = $("btnNextDoc");

const btnUploadMain = $("btnUploadMain");
const btnUploadMenu = $("btnUploadMenu");
const uploadMenu = $("uploadMenu");
let currentAccept = ".docx,.md,.html,.txt";

const btnBulkApply = $("btnBulkApply");


// Session format kept on a safe global key to avoid redeclare/HMR issues
function getSessionFormat(){ try { return window.__LC_SESSION_FORMAT__ || ""; } catch { return ""; } }
function setSessionFormat(ext){ try { window.__LC_SESSION_FORMAT__ = ext || ""; } catch {} }

const btnDownloadMain = $("btnDownloadMain");
const btnDownloadMenu = $("btnDownloadMenu");
const downloadMenu = $("downloadMenu");
let currentExport = "original";

/* ? Correct Auto-Link button hook (matches HTML: id="btnAutoLinkMain") */
const btnAutoLinkMain = $("btnAutoLinkMain");

/* Progress bar (present in HTML) */
const autolinkProgressBox = $("autolinkProgress");
const autolinkProgressBar = autolinkProgressBox?.querySelector(".lp-bar") || null;
const autolinkProgressPct = autolinkProgressBox?.querySelector(".lp-pct") || null;

/* Progress helpers (operate on existing DOM) */
function showAutolinkProgress() {
  if (!autolinkProgressBox) return;
  autolinkProgressBox.style.display = "block";
  updateAutolinkProgress(0);
}
function updateAutolinkProgress(pct) {
  if (!autolinkProgressBox) return;
  const n = Math.max(0, Math.min(100, Math.round(pct || 0)));
  if (autolinkProgressBar) autolinkProgressBar.style.width = n + "%";
  if (autolinkProgressPct) autolinkProgressPct.textContent = n + "%";
}
function hideAutolinkProgress() {
  if (!autolinkProgressBox) return;
  updateAutolinkProgress(100);
  setTimeout(() => { autolinkProgressBox.style.display = "none"; updateAutolinkProgress(0); }, 400);
}




/* ==========================================================================
   STORAGE KEYS
   ========================================================================== */
const STORAGE_KEY         = "linkcraftor_state_v2";
const HILITE_KEY          = "linkcraftor_highlight_enabled_v1";
const IL_LINKED_SET_KEY   = "linkcraftor_il_linked_set_v2";
const IL_REJECTED_SET_KEY = "linkcraftor_rejected_set_v1";

const IMPORTED_URLS_KEY   = "linkcraftor_imported_urls_v1";
const PUBLISHED_TOPICS_KEY= "linkcraftor_published_topics_v1";
const DRAFT_TOPICS_KEY    = "linkcraftor_draft_topics_v1";

const TITLE_INDEX_KEY     = "linkcraftor_title_index_v2";


// ==========================================================================
// Session format helpers (upload/download lock to one format) � COLLISION-SAFE
// ==========================================================================
(function(){
  const W = (typeof window !== "undefined") ? window : globalThis;

  // Namespace (never collides)
  W.__LC__ = W.__LC__ || {};
  if (typeof W.__LC__.SESSION_FORMAT === "undefined") {
    W.__LC__.SESSION_FORMAT = "";
  }

  // Core implementations (namespaced; never collide)
  function __getSessionFormatNS(){
    try {
      return W.__LC__.SESSION_FORMAT || (localStorage.getItem("lc_session_format") || "");
    } catch {
      return W.__LC__.SESSION_FORMAT || "";
    }
  }

  function __setSessionFormatNS(ext){
    try{
      if (!ext) return;
      W.__LC__.SESSION_FORMAT = ext;
      try { localStorage.setItem("lc_session_format", ext); } catch {}
      // defer menu sync until DOM is ready; no crash if not present
      const sync = () => { try { __ensureDownloadMenuForSessionNS(); } catch {} };
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", sync, { once: true });
      } else {
        sync();
      }
    }catch{}
  }

  function __ensureDownloadMenuForSessionNS(){
    try{
      const sess = (__getSessionFormatNS() || "").toLowerCase();   // ".docx" | ".md" | ".txt" | ".html" | ""
      const menu = document.getElementById("downloadMenu");
      if (!menu) return;

      // Allowed single choice when locked
      const allow = new Set();
      if (sess === ".docx") allow.add("docx");
      if (sess === ".md")   allow.add("md");
      if (sess === ".txt")  allow.add("txt");
      if (sess === ".html") allow.add("html");

      // Always hidden (features removed): "original" and "htm"
      const kill = new Set(["original","htm"]);

      menu.querySelectorAll("button[data-ext]").forEach(btn=>{
        const extAttr = (btn.getAttribute("data-ext") || "").toLowerCase();

        // Never show �original� or �.htm�
        if (kill.has(extAttr)) { btn.style.display = "none"; return; }

        // If a session format is locked, show only that matching option
        if (sess){
          btn.style.display = allow.has(extAttr) ? "" : "none";
        } else {
          // No session yet ? show everything except killers
          btn.style.display = "";
        }
      });
    } catch {}
  }

  // Expose namespaced API (always)
  W.__LC__.getSessionFormat = __getSessionFormatNS;
  W.__LC__.setSessionFormat = __setSessionFormatNS;
  W.__LC__.ensureDownloadMenuForSession = __ensureDownloadMenuForSessionNS;

  // Create global wrappers ONLY if they don't already exist (prevents redeclare errors)
  if (typeof W.getSessionFormat !== "function") {
    W.getSessionFormat = __getSessionFormatNS;
  }
  if (typeof W.setSessionFormat !== "function") {
    W.setSessionFormat = __setSessionFormatNS;
  }
  if (typeof W.ensureDownloadMenuForSession !== "function") {
    W.ensureDownloadMenuForSession = __ensureDownloadMenuForSessionNS;
  }
})();


async function loadAndRenderDocByIndex(idx){
  if (idx < 0 || idx >= (docs || []).length) return;
  const d = docs[idx] || {};
  const docId = String(d.doc_id || "");
  if (!docId) { renderDoc(idx); return; }

  try{
    const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
    
    const ws = getCurrentWorkspaceId("default");
     const res = await fetch(`${API_BASE}/api/files/preview?workspace_id=${encodeURIComponent(ws)}&doc_id=${encodeURIComponent(docId)}`);

    const data = await res.json().catch(()=>({}));
    if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);

    // merge preview into the placeholder doc
    docs[idx] = Object.assign({}, docs[idx], data, data.doc || {});
    renderDoc(idx);

    // keep dropdown in sync
    try { if (allDocs) allDocs.value = docId; } catch {}
  } catch(e){
    console.error("[preview] failed:", e);
    showToast?.(errorBox, "Preview failed: " + (e?.message || e), 2200);
    renderDoc(idx); // fallback
  }
}



/* ==========================================================================
   HELPERS
   ========================================================================== */
const rxWord = /[\p{L}\p{N}�'-]+/gu;
const norm   = (s)=> String(s||"").toLowerCase().trim().replace(/\s+/g, " ");
const tokens = (s)=> (String(s||"").toLowerCase().match(rxWord) || []).filter(Boolean);
const uniq   = (a)=> Array.from(new Set(a));
function escapeAttr(s) { return (s||"").replace(/"/g, '&quot;'); }
function debounce(fn, ms = 200) { let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a), ms); }; }
function isStop(w){ return STOPWORDS.has(String(w||"").toLowerCase()); }
function clamp01(x){ return x<0?0:x>1?1:x; }

/* === High-fidelity HTML + Markdown render helpers ======================== */
function extractHtmlPayload(rawHtml = "") {
  // Safely parse full HTML docs; pull out head <style> and body content.
  try {
    const doc = document.implementation.createHTMLDocument("");
    // If it's a fragment (no <html>), treat as body content
    const hasHtmlTag = /<html[\s>]/i.test(rawHtml);
    if (!hasHtmlTag) {
      return { headStyles: "", bodyHtml: rawHtml };
    }
    doc.documentElement.innerHTML = rawHtml;

    // Collect inline styles from <head> (ignore <link> for now�can�t fetch local files)
    const head = doc.querySelector("head");
    let styles = "";
    if (head) {
      const styleEls = head.querySelectorAll("style");
      styleEls.forEach(s => { styles += s.outerHTML + "\n"; });
    }

    const body = doc.body ? doc.body.innerHTML : rawHtml;
    return { headStyles: styles, bodyHtml: body };
  } catch {
    return { headStyles: "", bodyHtml: rawHtml };
  }
}

function markdownToHtml(md = "") {
  // Minimal but solid MD ? HTML (supports: headings, bold/italic, code, lists, tables, links/images)
  // 1) Fence blocks
  const fences = [];
  md = md.replace(/```([\s\S]*?)```/g, (_, code) => {
    fences.push(code);
    return `\uE000CODE${fences.length - 1}\uE000`;
  });

  // 2) Escape HTML (so markdown can�t inject raw tags)
  const esc = s => String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  // 3) Headings
  md = md
    .replace(/^###### (.*)$/gm, "<h6>$1</h6>")
    .replace(/^##### (.*)$/gm, "<h5>$1</h5>")
    .replace(/^#### (.*)$/gm, "<h4>$1</h4>")
    .replace(/^### (.*)$/gm, "<h3>$1</h3>")
    .replace(/^## (.*)$/gm, "<h2>$1</h2>")
    .replace(/^# (.*)$/gm, "<h1>$1</h1>");

  // 4) Tables (GitHub-style)
  // Detect header | --- | row and subsequent rows
  md = md.replace(
    /(^|\n)\s*\|(.+)\|\s*\n\s*\|([ \t:\-\|]+)\|\s*\n((?:\s*\|.*\|\s*\n?)*)/g,
    (_, pfx, headRow, sep, bodyRows) => {
      const th = headRow.split("|").map(s => s.trim()).map(h => `<th>${esc(h)}</th>`).join("");
      const trs = bodyRows.trim().split(/\n+/).filter(Boolean).map(r => {
        const tds = r.replace(/^\s*\||\|\s*$/g, "").split("|").map(s => `<td>${esc(s.trim())}</td>`).join("");
        return `<tr>${tds}</tr>`;
      }).join("");
      return `${pfx}<table><thead><tr>${th}</tr></thead><tbody>${trs}</tbody></table>\n`;
    }
  );

  // 5) Lists (unordered + ordered)
  // Unordered blocks
  md = md.replace(
    /(^|\n)(?:[ \t]*[-+*] .+(?:\n[ \t]*[-+*] .+)*)/g,
    block => {
      const items = block.trim().split(/\n/).map(l =>
        l.replace(/^[ \t]*[-+*] +/, "").trim()
      ).map(txt => `<li>${txt}</li>`).join("");
      return `\n<ul>${items}</ul>`;
    }
  );
  // Ordered blocks
  md = md.replace(
    /(^|\n)(?:[ \t]*\d+\. .+(?:\n[ \t]*\d+\. .+)*)/g,
    block => {
      const items = block.trim().split(/\n/).map(l =>
        l.replace(/^[ \t]*\d+\. +/, "").trim()
      ).map(txt => `<li>${txt}</li>`).join("");
      return `\n<ol>${items}</ol>`;
    }
  );

  // 6) Images + Links
  md = md
    .replace(/!\[([^\]]*)\]\((\S+?)(?:\s+"([^"]+)")?\)/g, (_, alt, url, title) =>
      `<img src="${url}" alt="${esc(alt)}"${title ? ` title="${esc(title)}"` : ""}>`
    )
    .replace(/\[([^\]]+)\]\((\S+?)\)/g, (_, text, url) =>
      `<a href="${url}" target="_blank" rel="noopener">${esc(text)}</a>`
    );

  // 7) Inline formatting
  md = md
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/__([^_]+)__/g, "<strong>$1</strong>")
    .replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, "<em>$1</em>")
    .replace(/(?<!_)_([^_]+)_(?!_)/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");

  // 8) Paragraphs (two+ newlines split)
  md = md.split(/\n{2,}/).map(block => {
    if (/^\s*<(h\d|ul|ol|table|pre|blockquote|p)\b/i.test(block)) return block;
    return `<p>${block.replace(/\n/g, "<br>")}</p>`;
  }).join("\n\n");

  // 9) Restore code fences
  md = md.replace(/\uE000CODE(\d+)\uE000/g, (_, i) => {
    const code = esc(fences[Number(i)] || "");
    return `<pre><code>${code}</code></pre>`;
  });

  return md;
}


// Safe escapeRegExp fallback
const escRe = (s)=> {
  try { return typeof escapeRegExp === "function" ? escapeRegExp(s) : String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
  catch { return String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
};

function makeBoundaryRx(phrase){
  const escaped = escRe(phrase).replace(/\s+/g, "\\s+");
  return new RegExp(`(^|[^\\p{L}\\p{N}])(${escaped})(?=$|[^\\p{L}\\p{N}])`, "giu");
}
function contentRatio(tokArr){ if(!tokArr?.length) return 0; const c = tokArr.filter(t=>!isStop(t)&&t.length>=4).length; return c/tokArr.length; }
function noStopEdges(tokArr){ if(!tokArr?.length) return false; return !isStop(tokArr[0]) && !isStop(tokArr[tokArr.length-1]); }

function tokenizeUrl(url){
  try{
    const u = new URL(url);
    const host=(u.hostname||"").replace(/^www\./,"");
    const hostParts=host.split(/[.\-]+/).filter(Boolean);
    const path=(u.pathname||"").replace(/\/+/g,"/");
    const pathParts=path.split(/[\/\-_]+/).filter(Boolean);
    return hostParts.concat(pathParts).map(t=>t.toLowerCase());
  }catch{ return []; }
}
function tokenizeSlug(slugOrUrl){
  if (!slugOrUrl) return [];
  if (/^https?:\/\//i.test(slugOrUrl)) return tokenizeUrl(slugOrUrl);
  return String(slugOrUrl).toLowerCase().split(/[\/\-_]+/).filter(Boolean);
}

// Debug helper: inspect cached sitemap content for a given URL
function debugSitemapPage(url) {
  const key = String(url || "").trim();
  const rec = SITEMAP_CONTENT.get(key);
  console.log("[debugSitemapPage]", key, rec);
  return rec;
}

// Expose for console use
if (typeof window !== "undefined") {
  window.debugSitemapPage = debugSitemapPage;
}


/* ==========================================================================
   TITLE / URL INDEX (kept; same-doc discovery)
   ========================================================================== */
function extractTitleFromDoc(d) {
  if (d.title && d.title.trim()) return d.title.trim();
  if (d.html) {
    const div = document.createElement("div"); div.innerHTML = d.html;
    const h1 = div.querySelector("h1"); if (h1?.textContent?.trim()) return h1.textContent.trim();
    const htmlTitle = div.querySelector("title"); if (htmlTitle?.textContent?.trim()) return htmlTitle.textContent.trim();
  }
  if (d.text) {
    const first = (d.text.split(/\r?\n/).map(s=>s.trim()).find(s=>s.length>0)) || "";
    if (first) return first.slice(0, 120);
  }
  if (d.filename) return d.filename.replace(/\.[^\.\s]+$/, "").replace(/[_\-]+/g, " ").trim();
  return "";
}
function generateAliasesForTitle(title) {
  const s = (title || "").toLowerCase().trim();
  const aliases = new Set();
  const base = s.replace(/\s+/g, " ").trim();
  const noPunct = base.replace(/[^\p{L}\p{N}\s\-]/gu, "");
  const hyph2sp = noPunct.replace(/\-/g, " ");
  const sp2hyph = noPunct.replace(/\s+/g, "-");
  [base, noPunct, hyph2sp, sp2hyph].forEach(v => { const n = norm(v); if (n) aliases.add(n); });
  return Array.from(aliases);
}
function titleCoverageInUrl(title, url){
  const t = (title||"").toLowerCase().split(/\s+/).filter(Boolean);
  const u = tokenizeUrl(url);
  if (!t.length || !u.length) return 0;
  let hit=0; for(const w of t){ if(u.some(tok=>tok.includes(w)||w.includes(tok))) hit++; }
  return hit / t.length;
}
function bestUrlForTitle(title, urls, minCoverage = 0.85){
  let best = "", bestScore = 0;
  for (const url of urls){ const s = titleCoverageInUrl(title, url); if (s>bestScore){ bestScore=s; best=url; } }
  return bestScore >= minCoverage ? best : "";
}
function rebuildTitleIndexFromDocs(){
  const m = new Map(); const aliasMap = new Map(); const urls = Array.from(IMPORTED_URLS);
  for (const d of docs){
    if (!d) continue;
    const title = extractTitleFromDoc(d); if (!title) continue;
    const key = norm(title);
    const urlMatch = bestUrlForTitle(title, urls, 0.85);
    m.set(key, { title, url: urlMatch || "" });
    for (const alias of generateAliasesForTitle(title)) aliasMap.set(alias, key);
  }
  TITLE_INDEX = m; TITLE_ALIAS_MAP = aliasMap; saveTitleIndexToLocal();
  if (DEBUG) console.log("[Index] Title index rebuilt:", m.size, "titles");
}
function loadTitleIndexFromLocal(){ try{ const raw = localStorage.getItem(TITLE_INDEX_KEY); if(!raw) return; const obj = JSON.parse(raw); if (obj && obj.entries && obj.aliases){ TITLE_INDEX = new Map(obj.entries); TITLE_ALIAS_MAP = new Map(obj.aliases); } }catch{} }
function saveTitleIndexToLocal(){ try{ const payload = { entries: Array.from(TITLE_INDEX.entries()), aliases: Array.from(TITLE_ALIAS_MAP.entries()) }; localStorage.setItem(TITLE_INDEX_KEY, JSON.stringify(payload)); }catch{} }

/* ==========================================================================
   DOC CODE + PERSIST
   ========================================================================== */
function generateDocCode(existing = new Set()){
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  function randCode(){ let out=""; for (let i=0;i<4;i++) out += chars[Math.floor(Math.random()*chars.length)]; return out; }
  let code = randCode(), guard = 0;
  while (existing.has(code) && guard < 1000){ code = randCode(); guard++; }
  return code;
}
function getOrAssignCode(d){
  const codes = new Set(docs.filter(x=>x && x.docCode).map(x=>String(x.docCode).toUpperCase()));
  if (!d.docCode || !/^[A-Z0-9]{4}$/.test(String(d.docCode).toUpperCase())){
    d.docCode = generateDocCode(codes);
  } else { d.docCode = String(d.docCode).toUpperCase().slice(0,4); }
  return d.docCode;
}
function loadLinkedSet(){ try { const raw = localStorage.getItem(IL_LINKED_SET_KEY); LINKED_SET = new Set(raw ? JSON.parse(raw) : []); } catch { LINKED_SET = new Set(); } }
function saveLinkedSet(){ try { localStorage.setItem(IL_LINKED_SET_KEY, JSON.stringify(Array.from(LINKED_SET))); } catch {} }
function loadRejectedSet(){ try { const raw = localStorage.getItem(IL_REJECTED_SET_KEY); window.REJECTED_SET = new Set(raw ? JSON.parse(raw) : []); } catch { window.REJECTED_SET = new Set(); } }
function saveRejectedSet(){ try { localStorage.setItem(IL_REJECTED_SET_KEY, JSON.stringify(Array.from(window.REJECTED_SET||[]))); } catch {} }

/* === Rejection helpers (scoped) === */
function rejectedKey(type, phrase){ return `${type}:${norm(phrase)}`; }
function isRejected(type, phrase){
  window.REJECTED_SET = window.REJECTED_SET || new Set();
  return window.REJECTED_SET.has(rejectedKey(type, phrase));
}
function rejectPhrase(phrase, type="engine"){
  const p = norm(phrase);
  window.REJECTED_SET = window.REJECTED_SET || new Set();
  window.REJECTED_SET.add(rejectedKey(type, p));
  saveRejectedSet();
}

// Cache scraped sitemap content in memory (not persisted yet)
function registerSitemapContent(pages = []) {
  if (!Array.isArray(pages)) return;
  let added = 0;

  for (const p of pages) {
    if (!p || !p.url) continue;
    const url = String(p.url).trim();
    if (!url) continue;

    const title = (p.title || "").trim();
    const text  = (p.text  || "").trim();
    const toks  = tokens(text);

    SITEMAP_CONTENT.set(url, {
      url,
      title,
      text,
      tokens: toks,
    });
    added++;
  }

  if (DEBUG) {
    console.log("[sitemap-content] cached pages:", added, "total:", SITEMAP_CONTENT.size);
  }
}


/* ==========================================================================
   PUBLISHED & DRAFT REGISTRIES (new)
   ========================================================================== */
function savePublishedTopics(){ try {
  const payload = Array.from(PUBLISHED_TOPICS.entries());
  localStorage.setItem(PUBLISHED_TOPICS_KEY, JSON.stringify(payload));
} catch{} }
function loadPublishedTopics(){ try {
  const raw = localStorage.getItem(PUBLISHED_TOPICS_KEY); if(!raw) return;
  PUBLISHED_TOPICS = new Map(JSON.parse(raw));
} catch{} }

function saveDraftTopics(){ try {
  const payload = Array.from(DRAFT_TOPICS.entries());
  localStorage.setItem(DRAFT_TOPICS_KEY, JSON.stringify(payload));
} catch{} }
function loadDraftTopics(){ try {
  const raw = localStorage.getItem(DRAFT_TOPICS_KEY); if(!raw) return;
  DRAFT_TOPICS = new Map(JSON.parse(raw));
} catch{} }

// Build/refresh PUBLISHED_TOPICS from IMPORTED_URLS + TITLE_INDEX
function rebuildPublishedTopics(){
  const next = new Map();
  const urls = Array.from(IMPORTED_URLS);
  let i = 0;
  for (const url of urls){
    let title = "";
    for (const [, v] of TITLE_INDEX.entries()){
      if (v?.url === url) { title = v.title; break; }
    }
    if (!title){
      const parts = tokenizeUrl(url).slice(-3);
      title = parts.map(s=> s.charAt(0).toUpperCase()+s.slice(1)).join(" ");
    }
    const id = `p:${i++}`;
    next.set(url, {
      id, url, title,
      slugTokens: tokenizeUrl(url),
      inlinks: 0, depth: 0,
      aliases: generateAliasesForTitle(title)
    });
  }
  PUBLISHED_TOPICS = next;
  savePublishedTopics();
  if (DEBUG) console.log("[Published] topics:", PUBLISHED_TOPICS.size);
}

// Parse Draft CSV/TXT
function importDraftFromText(text){
  const lines = text.split(/\r?\n/).filter(l=>l.trim().length>0);
  let added = 0;
  const head = lines[0].split(",").map(s=>s.trim().toLowerCase());
  const looksCSV = (head.includes("topic_id") || head.includes("working_title") || head.includes("planned_slug"));
  const rows = looksCSV
    ? lines.slice(1).map(l=>l.split(","))
    : lines.map(l=> l.split("|"));

  const header = looksCSV ? head : ["topic_id","working_title","planned_slug","planned_url","aliases","priority","canonical"];
  const idx = (name)=> header.indexOf(name);

  for (const r of rows){
    const get = (n)=> (idx(n)>=0 ? (r[idx(n)]||"").trim() : "");
    const topic_id = get("topic_id") || get("id") || "";
    const working_title = get("working_title") || get("title") || "";
    const planned_slug = get("planned_slug") || "";
    const planned_url  = get("planned_url")  || "";
    const aliasesStr   = get("aliases")      || "";
    const priority     = parseInt(get("priority")||"0",10) || 0;
    const canonical    = String(get("canonical")||"").toLowerCase() === "true";

    if (!topic_id || !working_title) continue;

    DRAFT_TOPICS.set(topic_id, {
      id: `d:${topic_id}`,
      topic_id,
      working_title,
      planned_slug,
      planned_url,
      aliases: aliasesStr ? aliasesStr.split("|").map(s=>s.trim()).filter(Boolean) : [],
      priority, canonical
    });
    added++;
  }
  saveDraftTopics(); // ? disabled: draft is backend-only
  return added;
}

/* ==========================================================================
   MENUS / UI (Upload + Download only; Auto-Link is a simple button now)
   ========================================================================== */
function hideMenu(menuEl, btnEl) {
  if (!menuEl) return;
  menuEl.classList.remove("open");
  menuEl.setAttribute("hidden", "");
  if (btnEl) btnEl.setAttribute("aria-expanded", "false");
}

function showMenu(menuEl, btnEl) {
  if (!menuEl) return;
  // Only manage uploadMenu and downloadMenu now
  [uploadMenu, downloadMenu].forEach(m => {
    if (m && m !== menuEl) {
      const b =
        m === uploadMenu ? btnUploadMenu :
        m === downloadMenu ? btnDownloadMenu :
        null;
      hideMenu(m, b);
    }
  });
  menuEl.classList.add("open");
  menuEl.removeAttribute("hidden");
  if (btnEl) btnEl.setAttribute("aria-expanded", "true");
}

function toggleMenu(menuEl, btnEl) {
  if (!menuEl) return;
  if (menuEl.classList.contains("open")) hideMenu(menuEl, btnEl);
  else showMenu(menuEl, btnEl);
}

// Close menus when clicking outside
document.addEventListener("click", () => {
  hideMenu(uploadMenu, btnUploadMenu);
  hideMenu(downloadMenu, btnDownloadMenu);
});

// Close menus on Escape
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    hideMenu(uploadMenu, btnUploadMenu);
    hideMenu(downloadMenu, btnDownloadMenu);
  }
});

// Stop propagation inside menus
[uploadMenu, downloadMenu].forEach(m => {
  m?.addEventListener("click", e => e.stopPropagation());
});

// Stop propagation on menu buttons
[btnUploadMenu, btnDownloadMenu].forEach(b => {
  b?.addEventListener("click", e => e.stopPropagation());
  b?.addEventListener("pointerdown", e => e.stopPropagation());
});

// Wire the actual toggles
btnUploadMenu?.addEventListener("click", () => toggleMenu(uploadMenu, btnUploadMenu));
btnDownloadMenu?.addEventListener("click", () => toggleMenu(downloadMenu, btnDownloadMenu));

btnAutoLinkMain?.addEventListener("click", async () => {
  console.log("[RB2 CLICK] btnAutoLinkMain fired");

  if (!docs || !docs.length) {
    showToast(errorBox, "Upload at least one document first.", 2000);
    return;
  }

  highlightsArmed = true;
  await runPipelineAndHighlight({ append: true });
});

/* Uploads */
function setAcceptAndOpen(acceptList) {
  const accept = acceptList || ".docx,.md,.html,.txt";
  if (fileInput) {
    fileInput.setAttribute("accept", accept);
    fileInput.click();
  }
}

function refreshUploadMenuForSessionFormat(){
  try{
    if (!uploadMenu) return;
    const buttons = Array.from(uploadMenu.querySelectorAll("button[data-accept]"));
    buttons.forEach(btn=>{
      const acc = btn.getAttribute("data-accept") || "";
      // Keep zip/rar visible if you still use them for bulk-import; otherwise hide them too.
      if (!SESSION_FORMAT) {
        btn.style.display = ""; // show all before the first upload
      } else if (acc === SESSION_FORMAT || acc === ".zip,.rar" || acc === "") {
        btn.style.display = ""; // show same-format, bulk, and default
      } else {
        btn.style.display = "none"; // hide other formats
      }
    });
  } catch {}
}



btnUploadMain?.addEventListener("click", () => {
  const ws = getCurrentWorkspaceId("");

  if (!ws) {
    showToast(errorBox, "Connect a domain first.", 1600);
    return;
  }

  console.log("[Upload Workspace]", ws);
  setAcceptAndOpen(currentAccept);
});


if (uploadMenu) uploadMenu.querySelectorAll("button").forEach(btn=>{
  btn.addEventListener("click", (e)=>{
    e.stopPropagation();
    const accept = btn.getAttribute("data-accept") || "";
    const map = { "": ".docx,.md,.html,.txt", ".zip,.rar": ".zip,.rar", ".docx": ".docx", ".md": ".md", ".html": ".html", ".txt": ".txt" };

    // If SESSION_FORMAT is locked, only allow that exact format (zip/rar still allowed for bulk-import if you use it).
    if (SESSION_FORMAT && accept && accept.startsWith(".")) {
      if (accept !== SESSION_FORMAT) {
        showToast(errorBox, `This session is locked to ${SESSION_FORMAT} files.`, 1600);
        return;
      }
    }

    setAcceptAndOpen(SESSION_FORMAT ? SESSION_FORMAT : (map[accept] || ".docx,.md,.html,.txt"));
    hideMenu(uploadMenu, btnUploadMenu);
  });
});

if (downloadMenu) downloadMenu.querySelectorAll("button").forEach(btn=>{
  btn.addEventListener("click", async(e)=>{
    e.stopPropagation();
    hideMenu(downloadMenu, btnDownloadMenu);

    try{
      // Prefer the locked session format; if not set yet, use the button�s request
      const sess = getSessionFormat(); // ".docx" | ".md" | ".txt" | ".html" | ""
      const requested = (btn.getAttribute("data-ext") || "").toLowerCase();

      // Decide final export strictly from locked format (no .htm, no "original")
      const ext = (sess || requested || "").toLowerCase();

      if (ext === ".docx") { await downloadDocx();          return; }
      if (ext === ".md")   {        downloadText("md");      return; }
      if (ext === ".txt")  {        downloadText("txt");     return; }
      if (ext === ".html") {        downloadHTML("html");    return; }

      // Fallback: export clean HTML
      downloadHTML("html");
    } catch(err){
      safeSetText(errorBox, "Download failed: " + err.message, "error");
    }
  });
});


if (downloadMenu) downloadMenu.querySelectorAll("button").forEach(btn=>{
  btn.addEventListener("click", async(e)=>{
    e.stopPropagation();
    currentExport = btn.getAttribute("data-ext")||"original";
    hideMenu(downloadMenu, btnDownloadMenu);
    try{
      if(currentExport==="original") { await downloadOriginal();      return; }
      if(currentExport==="docx")     { await downloadDocx();          return; }
      if(currentExport==="html")     { downloadHTML("html");          return; }
      if(currentExport==="txt")      { downloadText("txt");           return; }
      if(currentExport==="md")       { downloadText("md");            return; }
     if(currentExport==="zip")      { window.location.href = exportZipUrl(); return; }
if(currentExport==="rar")      { window.location.href = exportRarUrl(); return; }
 
    } catch(err){ safeSetText(errorBox, "Download failed: "+err.message, "error"); }
  });
});
function delay(ms){ return new Promise(res=>setTimeout(res, ms)); }


/* Upload handler */
fileInput?.addEventListener("change", async()=>{
  const fl = fileInput.files;
  if (!fl || !fl.length) return;

  safeSetText(errorBox, "", "error");

  // Determine or enforce the locked session format
  let sessExt = getSessionFormat();
  const firstExt = extOf(fl[0]?.name || "");

  if (!sessExt) {
    // First successful selection: lock the session to the first file's extension
    setSessionFormat(firstExt || ".txt");
    sessExt = getSessionFormat();

    // Keep accept in sync and hide other menu options
    currentAccept = sessExt;
    try {
      if (fileInput) fileInput.setAttribute("accept", sessExt);
    } catch {}
    try {
      // only if you added this helper earlier
      if (typeof refreshUploadMenuForSessionFormat === "function") {
        refreshUploadMenuForSessionFormat();
      }
    } catch {}
  }

  // Process only files that match the locked extension
  let accepted = 0;
  let skipped  = 0;

  try {
    for (const file of fl) {
      const ext = extOf(file?.name || "");
      if (ext !== sessExt) { skipped++; continue; }

      const ws = getCurrentWorkspaceId("ws_betterhealthcheck_com");
      const data = await uploadFile(file, ws);
      getOrAssignCode(data);
      docs.push(data);
      accepted++;
    }

    if (accepted === 0) {
      showToast(errorBox, `No files uploaded � session is locked to ${sessExt}.`, 2200);
      fileInput.value = "";
      return;
    }

  refreshDropdown();
rebuildTitleIndexFromDocs();
rebuildPublishedTopics();
renderDoc(docs.length - 1);

// ? NEW: render using the backend preview contract (is_html)
try { window.renderPreview?.(docs[docs.length - 1]); } catch {}

saveState();


    const msg = skipped
      ? `Uploaded ${accepted} file(s). Skipped ${skipped} (not ${sessExt}).`
      : `Uploaded ${accepted} file(s).`;
    showToast(errorBox, msg, 2000);

  } catch (e) {
    safeSetText(errorBox, "Upload failed: " + (e?.message || e), "error");
  }

  fileInput.value = "";
});


sitemapFile.addEventListener("change", async () => {
  const f = sitemapFile.files && sitemapFile.files[0];
  sitemapFile.value = "";
  if (!f) return;

  try {
    const before = new Set(Array.from(IMPORTED_URLS || []));

    // 1) Import into backend storage
    const r = await apiImportUrlsFile(f, "default");
    const added = Number(r.added || 0);

    // 2) Load full saved set from backend into engine memory
    const ws = getCurrentWorkspaceId("");
const urls = ws ? await apiLoadImportedUrls(ws, 200000) : [];
    IMPORTED_URLS = new Set(urls);

   // ? Update the badge in the top bar
try {
  const el = document.getElementById("importCount");
  setImportCount(IMPORTED_URLS.size || 0);
} catch {}


    // 3) Continue normal pipeline (no distortion)
    rebuildTitleIndexFromDocs();
    rebuildPublishedTopics();

    // 4) Scrape only newly added URLs (optional)
    const nowUrls = Array.from(IMPORTED_URLS);
    const newOnes = nowUrls.filter(u => u && !before.has(u) && !SITEMAP_CONTENT.has(u));
    if (newOnes.length) {
      fetchSitemapContentForUrls(newOnes);
    }

    showToast(errorBox, `Imported ${added} URL(s) from ${f.name}.`, 2000);
    if (highlightsArmed) runPipelineAndHighlight({ append: true });
  } catch (e) {
    console.error("[SITEMAP->BACKEND] failed:", e);
    showToast(errorBox, `Import failed: ${e?.message || e}`, 2200);
  }
});


/* Import Draft Map � BACKEND ONLY (single source of truth) */
if (btnImportDraft && draftFile) {
  const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");

  async function apiImportDraftFile(file, workspaceId = "default") {
    const fd = new FormData();
    fd.append("file", file);

    const res = await fetch(
      `${API_BASE}/api/draft/import?workspace_id=${encodeURIComponent(workspaceId)}`,
      { method: "POST", body: fd }
    );

    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);
    return data; // { ok, added, updated, total }
  }

  async function apiLoadDraft(workspaceId = "default", limit = 200000) {
    const res = await fetch(
      `${API_BASE}/api/draft/list?workspace_id=${encodeURIComponent(workspaceId)}&limit=${limit}`
    );
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);
    return Array.isArray(data.topics) ? data.topics : [];
  }

  function applyDraftToMemory(rows) {
    // Convert backend list -> your in-memory DRAFT_TOPICS map
    const next = new Map();
    for (const r of (rows || [])) {
      const topic_id = String(r.topic_id || "").trim();
      const working_title = String(r.working_title || "").trim();
      if (!topic_id || !working_title) continue;

      next.set(topic_id, {
        id: `d:${topic_id}`,
        topic_id,
        working_title,
        planned_slug: r.planned_slug || "",
        planned_url: r.planned_url || "",
        aliases: Array.isArray(r.aliases) ? r.aliases : [],
        priority: Number(r.priority || 0) || 0,
        canonical: Boolean(r.canonical),
      });
    }
    DRAFT_TOPICS = next;
    console.log("[Draft] BACKEND loaded:", DRAFT_TOPICS.size);
  }

   // ? Hydrate drafts from backend on initial load (so Draft BACKEND loaded is never 0 unless backend is empty)
(async function hydrateDraftsOnLoad(){
  try{
    const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
    const ws = getCurrentWorkspaceId("default");
const url = `${API_BASE}/api/draft/list?workspace_id=${encodeURIComponent(ws)}&limit=200000`;

    const res = await fetch(url);
    const data = await res.json().catch(()=>({}));
    if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);

    // backend can return {topics:{}} or {items:[]} depending on your route version
    const topicsObj = (data && typeof data.topics === "object" && data.topics) ? data.topics : null;
    const itemsArr  = Array.isArray(data?.items) ? data.items : null;

    // Normalize into DRAFT_TOPICS Map (url -> topic)
    if (!window.DRAFT_TOPICS) window.DRAFT_TOPICS = new Map();
    window.DRAFT_TOPICS.clear();

    let count = 0;

    if (topicsObj) {
      // { url: {title,...}, ... }
      for (const [u, meta] of Object.entries(topicsObj)) {
        const url2 = String(u || "").trim();
        if (!url2) continue;
        window.DRAFT_TOPICS.set(url2, meta || {});
        count++;
      }
    } else if (itemsArr) {
      // [{planned_url,title,topic_id,...}, ...]
      for (const r of itemsArr) {
        const url2 = String(r?.planned_url || r?.url || "").trim();
        if (!url2) continue;
        window.DRAFT_TOPICS.set(url2, r);
        count++;
      }
    }

    // ? Update any Draft count element if you have one
    try{
      const el = document.getElementById("draftCount");
      if (el) el.textContent = String(count);
    }catch{}

    console.log("[Draft] BACKEND loaded:", count);
  }catch(e){
    console.warn("[Draft] BACKEND hydrate failed:", e);
  }
})();



  btnImportDraft.addEventListener("click", () => {
    draftFile.value = "";
    draftFile.click();
  });

  draftFile.addEventListener("change", async () => {
    const f = draftFile.files && draftFile.files[0];
    draftFile.value = "";
    if (!f) return;

    try {
      const r = await apiImportDraftFile(f, "default");
      const rows = await apiLoadDraft("default", 200000);
      applyDraftToMemory(rows);
      const ws = getCurrentWorkspaceId("");
if (ws) await updateUnifiedImportCount(ws);



      showToast(
        errorBox,
        `Draft saved (backend): +${r.added || 0} added, ${r.updated || 0} updated. Total: ${r.total || DRAFT_TOPICS.size}`,
        2400
      );

      if (highlightsArmed) runPipelineAndHighlight({ append: true });
    } catch (e) {
      console.error("[Draft] import failed:", e);
      showToast(errorBox, `Draft import failed: ${e.message || e}`, 2400);
    }
  });
}


/* Toolbar basics */
const toolbar = $("toolbar");
function ensureViewerFocus(){ try{ viewerEl?.focus(); }catch{} }
function exec(name, value = null){ ensureViewerFocus(); document.execCommand(name, false, value); viewerEl?.dispatchEvent(new Event("input", { bubbles:true })); }
if (toolbar){
  toolbar.querySelectorAll("[data-cmd]").forEach(btn=>{
    btn.addEventListener("click", ()=> exec(btn.getAttribute("data-cmd")));
  });
}

const updateDetectedDebounced = debounce(()=>{
  if (highlightsArmed) runPipelineAndHighlight({ append: true });
  else { underlineLinkedPhrases(); highlightBucketKeywords(); updateHighlightBadge(); rebuildEngineHighlightsPanel(); }
}, 200);


/* ==========================================================================
   EXTERNAL AUTO-LINK ENRICHMENT (backend + 24 providers + logging)
   ========================================================================== */

const EXTERNAL_API_BASE = ""; 
// If your backend is same origin, leave "" and use "/api/..."
// If it's on another port/host, you can change to e.g. "http://localhost:8002"

/**
 * Small helper: resolve a phrase via backend /api/external/resolve (GET).
 * Backend returns an ARRAY of candidates (or []).
 * Returns { url, providerId, providerLabel, title } or null.
 */

async function resolveExternalViaBackend(phrase, mark) {
  const q = String(phrase || "").trim();
  if (!q) return null;

  console.log("[ExtAutoLink] resolveExternalViaBackend CALLED for:", q);

  const base = String(window.LINKCRAFTOR_API_BASE || "").replace(/\/+$/,"");
  if (!base) {
    console.warn("[ExtAutoLink] LINKCRAFTOR_API_BASE is empty � cannot call backend");
    return null;
  }

  const url = base + "/api/external/resolve?phrase=" + encodeURIComponent(q) + "&lang=en";



  const res = await fetch(url, { method:"GET", headers:{ "Accept":"application/json" } });
  if (!res.ok) return null;

 const data = await res.json();

// /engine/external/local returns { items: [...] }
const arr = Array.isArray(data) ? data : [];
if (!arr.length || !arr[0] || !arr[0].url) return null;

const r = arr[0];
return {
  url: r.url,
  providerId: r.providerId || r.source || null,
  providerLabel: r.providerLabel || r.source || null,
  title: r.title || q
};
}


async function logExternalLink(eventType, phrase, url, mark) {
  const ds = mark?.dataset || {};

  const body = {
    event: eventType,
    phrase,
    url,
    providerId: ds.providerId || null,
    providerLabel: ds.providerName || null,
    docCode: ds.docCode || null,
    docTitle: ds.docTitle || null,
    lang: "en",
    source: "auto_link"
  };

  // Ensure we log ONE AT A TIME (prevents 500s from concurrent writes)
  window.__lcExternalLogQueue = window.__lcExternalLogQueue || Promise.resolve();

  window.__lcExternalLogQueue = window.__lcExternalLogQueue.then(async () => {
    try {
      const base = (window.LINKCRAFTOR_API_BASE || EXTERNAL_API_BASE || "")
        .replace(/\/+$/, "");

      if (!base) return;

      console.log(
        "[ExtAutoLink] POST /api/external/log ?",
        base + "/api/external/log",
        body
      );

      await fetch(base + "/api/external/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
    } catch (err) {
      console.warn("[ExtAutoLink] /log failed (non-blocking)", err);
    }
  });
}


/**
 * For every external mark in a container, we now:
 *   1) Try backend /api/external/resolve
 *   2) If no match, fall back to LinkcraftorExternalRefs 24-provider search
 *   3) Attach mark.dataset.url + provider info
 *   4) (Later, when applied) /api/external/log will be called
 */
async function enrichExternalMarksWithUrls(root) {
  const container = root || viewerEl;
  if (!container) {
    console.log("[ExtAutoLink] No container to enrich.");
    return;
  }

  // We only care about external marks
  const marks = Array.from(
    container.querySelectorAll(
      "mark[data-kind='external'], mark.kwd-ext, mark.kwd-external"
    )
  );

  if (!marks.length) {
    console.log("[ExtAutoLink] No external marks to enrich.");
    return;
  }

  const engine = window.LinkcraftorExternalRefs;
  if (!engine || typeof engine.getExternalReferences !== "function") {
    console.warn(
      "[ExtAutoLink] External engine not ready (LinkcraftorExternalRefs)."
    );
  }

  console.log(
    "[ExtAutoLink] Enriching",
    marks.length,
    "external marks with URLs�"
  );

  for (const mark of marks) {
    try {
      const ds = mark.dataset || {};

      // Already has URL ? skip
      if (ds.url) continue;

      // Phrase: prefer data-phrase, fallback to text
      let phrase = "";
      if (ds.phrase) {
        try {
          phrase = decodeURIComponent(ds.phrase);
        } catch {
          phrase = ds.phrase;
        }
      } else {
        phrase = (mark.textContent || "").trim();
      }
      if (!phrase) continue;

      let finalUrl = null;
      let finalProviderId = null;
      let finalProviderName = null;

      // -------------------------------
      // 1) Try backend canonical resolve
      // -------------------------------
      const backendResult = await resolveExternalViaBackend(phrase, mark);
      if (backendResult && backendResult.url) {
        finalUrl = backendResult.url;
        finalProviderId = backendResult.providerId;
        finalProviderName = backendResult.providerLabel;
        console.log(
          "[ExtAutoLink] Backend resolved phrase:",
          `"${phrase}" ? ${finalUrl} | provider:`,
          finalProviderName || finalProviderId || "unknown"
        );
      }

      // -------------------------------------------
// 2) If backend had no match ? DO NOT LINK
// (fallback is disabled by design)
// -------------------------------------------
if (!finalUrl) {
  console.log(
    "[ExtAutoLink] No backend match ? fallback DISABLED ? leaving unlinked:",
    `"${phrase}"`
  );
  return null;
}

      // -------------------------
      // 3) If we found a URL ? set
      // -------------------------
      if (finalUrl) {
        mark.dataset.url = finalUrl;
        if (finalProviderId) {
          mark.dataset.providerId = finalProviderId;
        }
        if (finalProviderName) {
          mark.dataset.providerName = finalProviderName;
        }
        // Title: keep whatever is there, or phrase
        if (!mark.dataset.title) {
          mark.dataset.title = phrase;
        }
      }
    } catch (err) {
      console.warn("[ExtAutoLink] Error enriching one external mark:", err);
    }
  }

  console.log("[ExtAutoLink] Enrichment pass complete.");
}


/* ==========================================================================
   EDITOR + DOC NAV (unchanged)
   ========================================================================== */

editor?.addEventListener("input", () => {
  if (currentIndex >= 0 && docs[currentIndex]) {
    docs[currentIndex].text = viewerEl?.textContent || "";
    docs[currentIndex].html = viewerEl?.innerHTML || "";
    saveState();
    updateDetectedDebounced();
  }
});

allDocs?.addEventListener("change", async () => {
  const docId = allDocs.value;
  if (!docId) return;

  const idx = docs.findIndex(d => String(d.doc_id || "") === String(docId));
  if (idx < 0) return;

  try{
    const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
    
   const ws = getCurrentWorkspaceId("default");
const res = await fetch(`${API_BASE}/api/files/preview?workspace_id=${encodeURIComponent(ws)}&doc_id=${encodeURIComponent(docId)}`);

    const data = await res.json().catch(()=>({}));
    if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);

    // Update the placeholder doc with real preview content
    docs[idx] = Object.assign({}, docs[idx], data, data.doc || {});

    // Render using the new preview contract
    renderDoc(idx);
  } catch(e){
    console.error("[preview] failed:", e);
    showToast?.(errorBox, "Preview failed: " + (e?.message || e), 2200);
  }
});



const btnClearSession = $("btnClearSession");
btnClearSession?.addEventListener("click", () => {
  clearState();
  docs.splice(0, docs.length);
  currentIndex = -1;
  if (viewerEl) viewerEl.innerHTML = "Upload a document to begin editing�";
  safeSetText(topMeta, "No document loaded", "topMeta");
  safeSetText(docMeta, "Code: �", "docMeta");
  safeSetText(docCountMeta, "Doc 0 of 0", "docCountMeta");
  allDocs && (allDocs.innerHTML = "<option value=''>All docs</option>");
  APPLIED_LINKS = [];
  showToast(errorBox, "Session cleared.", 1200);
  updateDocNavButtons();
  underlineLinkedPhrases();
  highlightBucketKeywords();
  updateHighlightBadge();
  rebuildEngineHighlightsPanel();
});

/* Stopwords UI */
function applyStopwords() {
  const custom = new Set(
    loadStopwordsFromStore()
      .map(w => String(w || "").toLowerCase().trim())
      .filter(Boolean)
  );
  STOPWORDS = new Set(DEFAULT_STOPWORDS);
  custom.forEach(w => STOPWORDS.add(w));
}

/* Doc navigation */
btnPrevDoc?.addEventListener("click", () => {
  if (currentIndex > 0) loadAndRenderDocByIndex(currentIndex - 1);
});
btnNextDoc?.addEventListener("click", () => {
  if (currentIndex < docs.length - 1) loadAndRenderDocByIndex(currentIndex + 1);
});

/* ==========================================================================
   BULK APPLY � TURN MARKS INTO UNDERLINED LINKS
   ========================================================================== */

/**
 * Core helper: apply links inside any container element
 * - Converts <mark> elements with data-url / TITLE_INDEX into <a> links.
 * - Adds .lc-underlined class so they show as underlined.
 *
 * RETURNS:
 *   { applied, skippedNoHref, skippedNoText }
 */
async function bulkApplyInContainer(root) {
  if (!root) {
    console.log("[BulkApply] ABORT: no root container");
    return { applied: 0, skippedNoHref: 0, skippedNoText: 0 };
  }

  const marks = Array.from(
    root.querySelectorAll(
      "mark.kwd, mark.kwd-strong, mark.kwd-optional, " +
      "mark.kwd-external, mark.kwd-ext, " +
      "mark.kwd-int, mark.kwd-sem"
    )
  );

  console.log("[BulkApply] DEBUG: total marks found in container:", marks.length);

  let applied = 0;
  let skippedNoHref = 0;
  let skippedNoText = 0;

  for (let i = 0; i < marks.length; i++) {
    const mark = marks[i];
    const ds = mark.dataset || {};

    // Phrase (decode data-phrase if present, else use text)
    let phrase = "";
    if (ds.phrase) {
      try {
        phrase = decodeURIComponent(ds.phrase);
      } catch {
        phrase = ds.phrase;
      }
    } else {
      phrase = (mark.textContent || "").trim();
    }

    const kind =
      ds.kind ||
      ds.linkKind ||
      (mark.classList.contains("kwd-external") ||
        mark.classList.contains("kwd-ext") ||
        ds.kind === "external"
        ? "external"
        : "same-doc");

    const strength = ds.strength || ds.rank || "optional";
    const urlAttr = ds.url || ds.href || "";

    const topicId = ds.topicId || ds.targetId || "";
    const title = ds.title || ds.targetTitle || phrase || "";

    console.log(
      `[BulkApply] MARK #${i}: phrase="${phrase}" kind="${kind}" strength="${strength}" urlAttr="${urlAttr}" title="${title}"`
    );

    // Compute final href using your existing helper
    let href = "";
    try {
      if (typeof computeFinalUrl === "function") {
        href = computeFinalUrl(kind, topicId, title, urlAttr) || "";
      } else {
        href = urlAttr || "";
      }
    } catch (e) {
      console.warn("[BulkApply] computeFinalUrl failed for mark", i, e);
      href = urlAttr || "";
    }

    console.log(
      `[BulkApply] MARK #${i}: computed href from computeFinalUrl = "${href}"`
    );

    // Validate href + text
    if (!href) {
      skippedNoHref++;
      console.log(
        `[BulkApply] MARK #${i}: SKIP (no href) � phrase="${phrase}", kind="${kind}", strength="${strength}", title="${title}"`
      );
      continue;
    }

    const text = (mark.textContent || "").trim();
    if (!text) {
      skippedNoText++;
      console.log(
        `[BulkApply] MARK #${i}: SKIP (no text) � href="${href}", phrase="${phrase}"`
      );
      continue;
    }

   
// ------------------------------
// LOG EXTERNAL AUTO-APPLIED LINK (non-blocking)
// ------------------------------
const isExternalKind = kind === "external";
const isHttpUrl = /^https?:\/\//i.test(href);

if (isExternalKind && isHttpUrl && typeof logExternalLink === "function") {
  const phraseText = String(text || phrase || (mark?.textContent || ""))
  .replace(/[??]/g, "")
  .replace(/\s+/g, " ")
  .trim();

  logExternalLink("auto_apply", phraseText, href, mark);
}


    // ------------------------------
    // Turn <mark> into an <a> link
    // ------------------------------
    const a = document.createElement("a");
    a.href = href;
    a.textContent = String(text || "")
  .replace(/[??]/g, "")
  .replace(/\s+/g, " ")
  .trim();

    a.className = (mark.className || "") + " lc-underlined";
    a.setAttribute("data-lc", "1"); // optional tracking flag

    // Preserve some metadata on the <a> if useful
    if (kind) a.dataset.kind = kind;
    if (strength) a.dataset.strength = strength;
    if (topicId) a.dataset.topicId = topicId;
    if (title) a.title = title;
    if (urlAttr && !a.dataset.url) a.dataset.url = urlAttr;

    mark.replaceWith(a);
    applied++;

    console.log(
      `[BulkApply] MARK #${i}: APPLY � href="${href}", text="${text}"`
    );
  }

  console.log(
    "[BulkApply] SUMMARY (container) � applied=%d, skippedNoHref=%d, skippedNoText=%d",
    applied,
    skippedNoHref,
    skippedNoText
  );

  return { applied, skippedNoHref, skippedNoText };
}


/**
 * Bulk apply ACROSS ALL DOCS
 * --------------------------
 * For each doc:
 *  1) renderDoc(i)
 *  2) runPipelineAndHighlight({ append: true })  ? creates marks (+ external enrichment via wrapper)
 *  3) bulkApplyInContainer(viewerEl)            ? turns marks into <a> links
 *  4) save updated HTML/text back into docs[i]
 */
async function bulkApplyAllDocs() {
  console.log("[BulkApplyAll] Starting bulk apply across ALL docs");

  if (!Array.isArray(docs) || !docs.length) {
    console.log("[BulkApplyAll] ABORT: docs[] is empty or not an array");
    return;
  }
  if (!viewerEl) {
    console.log("[BulkApplyAll] ABORT: no viewerEl");
    return;
  }

  const originalIndex = currentIndex;

  let totalApplied       = 0;
  let totalSkippedNoHref = 0;
  let totalSkippedNoText = 0;

  for (let i = 0; i < docs.length; i++) {
    const d = docs[i];
    if (!d) {
      console.log(`[BulkApplyAll] Doc #${i}: SKIP (no doc object)`);
      continue;
    }

    console.log(
      `[BulkApplyAll] === Processing doc #${i} (${d.filename || d.name || "untitled"}) ===`
    );

    // 1) Render this doc into the viewer
    try {
      await renderDoc(i);
    } catch (e) {
      console.warn("[BulkApplyAll] Doc #%d: renderDoc failed", i, e);
      continue;
    }

    // 2) ALWAYS run the highlight pipeline so marks exist in this doc.
    //    The wrapper around runPipelineAndHighlight will also call
    //    enrichExternalMarksWithUrls(viewerEl) for external URLs.
    try {
      if (typeof runPipelineAndHighlight === "function") {
        console.log("[BulkApplyAll] Running highlight pipeline for doc %d", i);
        await runPipelineAndHighlight({ append: true });
      } else {
        console.log("[BulkApplyAll] No runPipelineAndHighlight() defined, skipping mark generation.");
      }
    } catch (e) {
      console.warn(
        "[BulkApplyAll] Doc #%d: error running highlight pipeline",
        i,
        e
      );
    }

    // 3) Apply links in this doc (internal + external)
    let stats = {
      applied: 0,
      skippedNoHref: 0,
      skippedNoText: 0
    };

    try {
      // Treat bulkApplyInContainer as async-safe
      stats = await bulkApplyInContainer(viewerEl);
    } catch (e) {
      console.warn(
        "[BulkApplyAll] Doc #%d: bulkApplyInContainer failed",
        i,
        e
      );
      continue;
    }

    console.log(
      "[BulkApplyAll] Doc #%d: applied=%d, skippedNoHref=%d, skippedNoText=%d",
      i,
      stats.applied,
      stats.skippedNoHref,
      stats.skippedNoText
    );

    totalApplied       += stats.applied;
    totalSkippedNoHref += stats.skippedNoHref;
    totalSkippedNoText += stats.skippedNoText;

    // 4) Persist updated document back into docs[]
    if (docs[i]) {
      docs[i].html = viewerEl.innerHTML;
      docs[i].text = viewerEl.textContent || "";
    }
  }

  // Restore whichever doc was active before bulk
  try {
    if (
      typeof originalIndex === "number" &&
      originalIndex >= 0 &&
      originalIndex < docs.length
    ) {
      await renderDoc(originalIndex);
    }
  } catch (e) {
    console.warn("[BulkApplyAll] Error restoring original doc", e);
  }

  if (typeof saveState === "function") {
    saveState();
  }

  console.log(
    "[BulkApplyAll] DONE � totalApplied=%d, skippedNoHref=%d, skippedNoText=%d",
    totalApplied,
    totalSkippedNoHref,
    totalSkippedNoText
  );
}

/* ------------------------------------------------------------------
 * Button wiring � ONE CLICK = BULK APPLY ACROSS ALL DOCS
 * ------------------------------------------------------------------ */

async function handleBulkApplyAllClick() {
  console.log("[BulkApplyAll] Button clicked � bulk apply across *ALL* docs");
  await bulkApplyAllDocs();

  // After the bulk, refresh UI for the currently visible doc
  underlineLinkedPhrases?.();
  highlightBucketKeywords?.();
  updateHighlightBadge?.();
  rebuildEngineHighlightsPanel?.();
}

// If you only have ONE bulk apply button (btnBulkApply), this will make
// that button run "bulk apply across ALL docs".
if (typeof btnBulkApply !== "undefined" && btnBulkApply) {
  btnBulkApply.addEventListener("click", handleBulkApplyAllClick);
}

// If you also have a separate "Apply All" button with id="btnBulkApplyAll",
// this will attach the same behavior without errors if it doesn't exist.
if (typeof btnBulkApplyAll !== "undefined" && btnBulkApplyAll) {
  btnBulkApplyAll.addEventListener("click", handleBulkApplyAllClick);
}


/* ==========================================================================
   ENGINE (A/B/C base config + HELIX add-ons)
   ========================================================================== */
const RB2 = Object.freeze({
  ngramMin: 2,
  ngramMax: 16,
  minContentRatio: 0.45,
  boostHeading: 0.10,
  boostIntro: 0.08,
  titleEchoPenalty: 0.10,
  W: Object.freeze({ overlap: 0.50, anchorQ: 0.40, coverage: 0.20 }),
  CONNECTORS: new Set(['of','for','in','on','to','and','with','vs','&','or','the','a','an','by','from']),
});

// HELIX: extra weights & toggles (layered on top of RB2)
const HELIX = Object.freeze({
  ENABLED: true,
  W2: Object.freeze({ embedSim: 0.20 }),
  cluster: Object.freeze({ hubBoost: 0.04, sameClusterBoost: 0.02, crossClusterPenalty: 0.02 }),
  ilrBand: Object.freeze({ base: 0.90, span: 0.10 }),
  embedDim: 192
});


/* ==========================================================================
   NEW: Entity features flags + caches (Entity Map / Graph / Content-Aware)
   ========================================================================== */
const ENTITY_FEATURES = Object.freeze({ MAP: true, GRAPH: true, CONTENT_AWARE: true });
let ENTITY_MAP = new Map();   // canon -> { title, aliases:Set, kind, slugTokens:[], freq }
let ENTITY_GRAPH = new Map(); // canon -> Map<canonNeighbor, weight>

/* ============================
   HELIX helpers (normalization)
   ============================ */
function lemma(tok){
  let t = tok;
  if (t.endsWith("ies") && t.length>4) return t.slice(0,-3)+"y";
  if (t.endsWith("sses") || t.endsWith("shes") || t.endsWith("ches")) return t.slice(0,-2);
  if (t.endsWith("ing") && t.length>5) return t.slice(0,-3);
  if (t.endsWith("ed") && t.length>4) return t.slice(0,-2);
  if (t.endsWith("s") && t.length>3) return t.slice(0,-1);
  return t;
}
const SYN_CANON = new Map([]);
function canonToken(w){ const base = SYN_CANON.get(w) || w; return lemma(base); }
function tokensNL(s){ return tokens(s).map(canonToken); }

/* === NEW: entity helpers (map/graph) ===================================== */
function isLikelyEntityTokens(tokArr){
  if (!tokArr || tokArr.length === 0) return false;
  if (tokArr.length > 5) return false;
  if (!noStopEdges(tokArr)) return false;
  return contentRatio(tokArr) >= 0.6;
}
function canonEntity(s){
  const t = tokensNL(s).filter(w=>!isStop(w));
  return t.join(" ").trim();
}

/* ============================
   HELIX helpers (embedding)
   ============================ */
function hash32(str){ let h=5381; for(let i=0;i<str.length;i++){ h=((h<<5)+h) ^ str.charCodeAt(i); } return (h>>>0); }
function embedHashed3Gram(text, dim = HELIX.embedDim){
  const T = tokensNL(text), v = new Float32Array(dim);
  for (let i=0;i<T.length;i++){
    const g = (T[i-1]||"") + "|" + T[i] + "|" + (T[i+1]||"");
    v[hash32(g) % dim] += 1;
  }
  let s=0; for (let i=0;i<dim;i++) s += v[i]*v[i];
  const n = Math.sqrt(s) || 1;
  for (let i=0;i<dim;i++) v[i] /= n;
  return v;
}
function cosineSim(a,b){
  const n = Math.min(a.length,b.length);
  let dot=0, na=0, nb=0;
  for (let i=0;i<n;i++){ dot += a[i]*b[i]; na += a[i]*a[i]; nb += b[i]*b[i]; }
  if (!na || !nb) return 0;
  return dot / Math.sqrt(na*nb);
}
function embedText(text){
  try { if (window.EMBED_API?.embed){ const v = window.EMBED_API.embed(String(text||"")); if (Array.isArray(v) && v.length>0) return v; } } catch {}
  return embedHashed3Gram(String(text||""));
}

/* === NEW: content-aware nudges helpers =================================== */
function entityOverlap01(anchorTokNL, entityMap){
  const a = anchorTokNL.join(" ");
  let best = 0;
  for (const canon of entityMap.keys()){
    if (a.includes(canon) || canon.includes(a)) {
      best = Math.max(best, Math.min(1, a.length / Math.max(1, canon.length)));
      if (best >= 1) break;
    }
  }
  return clamp01(best);
}
function graphNeighborBoost01(anchorTokNL, targetTitle, entityMap, entityGraph, secTokNL){
  if (!entityGraph || !entityGraph.size) return 0;
  const sec = secTokNL.join(" ");
  const locals = [];
  for (const k of entityMap.keys()){
    if (sec.includes(k)) locals.push(k);
    if (locals.length > 50) break;
  }
  if (!locals.length) return 0;
  const tgt = canonEntity(targetTitle);
  if (!tgt) return 0;
  let score = 0;
  for (const e of locals){
    const row = entityGraph.get(e);
    if (!row) continue;
    const w = row.get(tgt) || 0;
    if (w > 0) score += w;
  }
  return Math.min(1, score / 6);
}
function paragraphContextSim01(sectionText, targetTitle){
  try{
    const vs = embedText(sectionText);
    const vt = embedText(targetTitle);
    return clamp01(cosineSim(vs, vt));
  }catch{return 0;}
}


// ================================
// loadAndRenderDocByIndex (declare-once; collision-safe)
// ================================
(function(){
  const W = (typeof window !== "undefined") ? window : globalThis;

  // If already defined, do nothing (prevents "already been declared")
  if (typeof W.loadAndRenderDocByIndex === "function") return;

  W.loadAndRenderDocByIndex = async function(idx){
    if (idx < 0 || idx >= (docs || []).length) return;
    const d = docs[idx] || {};
    const docId = String(d.doc_id || "");
    if (!docId) { renderDoc(idx); return; }

    try{
      const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
       
      const ws = getCurrentWorkspaceId("default");
      const res = await fetch(`${API_BASE}/api/files/preview?workspace_id=${encodeURIComponent(ws)}&doc_id=${encodeURIComponent(docId)}`);

      const data = await res.json().catch(()=>({}));
      if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);

      docs[idx] = Object.assign({}, docs[idx], data, data.doc || {});
      renderDoc(idx);

      try { if (allDocs) allDocs.value = docId; } catch {}
    } catch(e){
      console.error("[preview] failed:", e);
      showToast?.(errorBox, "Preview failed: " + (e?.message || e), 2200);
      renderDoc(idx);
    }
  };
})();



/* ============================
   HELIX helpers (authority/cluster)
   ============================ */
function urlDepthHeuristic(url){
  try { const u = new URL(url); return (u.pathname || "").split("/").filter(Boolean).length; } catch { return 3; }
}
function ilr01(url){
  if (!url) return 0.5;
  const depth = urlDepthHeuristic(url);
  const maxDepth = 8;
  const val = 1 - Math.min(depth, maxDepth)/maxDepth;
  return Math.max(0, Math.min(1, val));
}
function targetClusterKey(t){
  const st = t.slugTokens || tokenizeSlug(t.url || t.planned_slug || "");
  if (!st.length) return (tokensNL(t.title||"").slice(0,2).join("/"));
  return st[0] || "";
}
function docClusterKey(){
  const d = docs[currentIndex] || null;
  if (!d) return "";
  const title = extractTitleFromDoc(d) || d.filename || "";
  const cl = tokenizeSlug(title);
  return cl[0] || cl.slice(0,2).join("/") || "";
}
function isHubTarget(t){
  const st = (t.slugTokens || []).map(x=>x.toLowerCase());
  if (st.length <= 1) return true;
  const hubWords = new Set(["index","guide","overview","basics","what","start","introduction"]);
  return st.some(x=> hubWords.has(x));
}

/* ============================
   Heading + section utilities
   ============================ */
function slugifyHeading(s){
  return (String(s||"")
    .toLowerCase()
    .trim()
    .replace(/[^\p{L}\p{N}\s-]/gu, "")
    .replace(/\s+/g, "-")
    .replace(/\-+/g, "-")
    .replace(/^\-+|\-+$/g, "")
  ) || "section";
}
function ensureHeadingIds(root){
  const hs = Array.from(root.querySelectorAll("h1,h2,h3"));
  for (const h of hs){ if (!h.id || !h.id.trim()) h.id = slugifyHeading(h.textContent||""); }
  return hs.map((h,i)=>({ level: parseInt(h.tagName.slice(1),10), text: (h.textContent||"").trim(), slug: h.id, index: i }));
}
function extractSections(root){
  const blocks = Array.from(root.querySelectorAll("p, li, td, blockquote, pre"));
  const sections = [];
  let idx=0;
  for (const el of blocks){
    const t = (el.textContent||"").trim();
    if (!t) continue;
    sections.push({ idx: idx++, text: t, el });
  }
  return sections;
}
function nearestHeadingSlug(headings, el){
  if (!headings.length || !el) return { slug:"", text:"", level:0 };
  let p = el.previousElementSibling;
  while(p){
    if (/^H[1-6]$/i.test(p.tagName)) return { slug:p.id||"", text:(p.textContent||"").trim(), level:parseInt(p.tagName.slice(1),10) };
    p = p.previousElementSibling;
  }
  const h1 = headings.find(h=>h.level===1);
  return h1 ? { slug:h1.slug, text:h1.text, level:1 } : { slug:"", text:"", level:0 };
}

/* ============================
   Topics (same-doc/published/draft/other docs)
   ============================ */
function topicsFromHeadings(headings){
  const out = [];
  for (const h of headings){
    if (h.level < 1 || h.level > 3) continue;
    const title = h.text || "";
    const aliases = generateAliasesForTitle(title);
    out.push({ id: `h:${h.slug}`, title, aliases, origin: "same-doc", url: "#"+h.slug, sectionSlug: h.slug });
  }
  return out;
}
function topicsFromPublished(){
  const out = [];
  for (const [, v] of PUBLISHED_TOPICS.entries()){
    out.push({ id: v.id, title: v.title, aliases: v.aliases||[], origin: "published", url: v.url, slugTokens: v.slugTokens||[] });
  }
  return out;
}
function topicsFromDraft(){
  const out = [];
  for (const [, v] of DRAFT_TOPICS.entries()){
    const aliasSet = new Set([...(v.aliases||[]), ...generateAliasesForTitle(v.working_title)]);
    out.push({
      id: v.id, topicId: v.topic_id, title: v.working_title, aliases: Array.from(aliasSet),
      origin: "draft", planned_slug: v.planned_slug, planned_url: v.planned_url || "",
      priority: v.priority || 0, canonical: !!v.canonical, slugTokens: tokenizeSlug(v.planned_url || v.planned_slug)
    });
  }
  return out;
}
function extractH1sFromDoc(d){
  const titles = [];
  try{
    if (d?.html) {
      const div = document.createElement("div");
      div.innerHTML = d.html;
      const hs = Array.from(div.querySelectorAll("h1"));
      for (const h of hs) {
        const t = (h.textContent || "").trim();
        if (t) titles.push(t);
      }
    }
    if (!titles.length && d?.text) {
      const first = (d.text.split(/\r?\n/).map(s=>s.trim()).find(Boolean)) || "";
      if (first) titles.push(first);
    }
  }catch{}
  return uniq(titles.map(s => s.slice(0, 200)));
}
function topicsFromOtherDocsH1(){
  const out = [];
  const urls = Array.from(IMPORTED_URLS);
  let k = 0;
  for (let i=0; i<docs.length; i++){
    if (i === currentIndex) continue;
    const d = docs[i]; if (!d) continue;
    const h1s = extractH1sFromDoc(d);
    for (const title of h1s){
      const urlMatch = bestUrlForTitle(title, urls, 0.80) || "";
      out.push({ id: `o:${i}:${k++}`, title, aliases: generateAliasesForTitle(title), origin: "other-doc", url: urlMatch, slugTokens: urlMatch ? tokenizeUrl(urlMatch) : [] });
    }
  }
  return out;
}


 /* ============================
   Candidate discovery + scoring helpers
   ============================ */
function extractAnchorsFromText(text){
  const toks = tokens(text);
  const anchors = new Set();
  for (let n=RB2.ngramMin; n<=RB2.ngramMax; n++){
    for (let i=0; i<=toks.length-n; i++){
      const gram = toks.slice(i,i+n);
      if (!noStopEdges(gram)) continue;
      if (contentRatio(gram) < RB2.minContentRatio) continue;
      anchors.add(gram.join(" "));
    }
  }
  return Array.from(anchors);
}
function tokenOverlapRatio(anchorTok, titleTok){
  const A = anchorTok.filter(t=>!isStop(t));
  const T = titleTok.filter(t=>!isStop(t));
  if (!A.length || !T.length) return 0;
  const S = new Set(T);
  let inter=0; for (const w of A) if (S.has(w)) inter++;
  const denom = Math.max(A.length, T.length);
  return inter / Math.max(1, denom);
}
function sectionCoverage(titleTok, sectionTok){
  const T = titleTok.filter(t=>!isStop(t));
  if (!T.length) return 0;
  const S = new Set(sectionTok);
  let hit=0; for (const w of T) if (S.has(w)) hit++;
  return hit / T.length;
}

/* Word windows */
function cumulativeWordOffsets(sections){
  const offs = []; let acc=0;
  const rx = /\b[\p{L}\p{N}'-]+\b/gu;
  for (const s of sections){ offs.push(acc); acc += (s.text.match(rx)||[]).length; }
  return offs;
}
function anchorWordIndex(section, anchorText, startOffset){
  const rxWord = /\b[\p{L}\p{N}'-]+\b/gu;
  const bRx = makeBoundaryRx(anchorText);
  bRx.lastIndex = 0;
  const m = bRx.exec(section.text);
  const before = m ? section.text.slice(0, m.index + (m[1] ? m[1].length : 0)) : "";
  const wordsBefore = (before.match(rxWord)||[]).length;
  return startOffset + wordsBefore;
}

/* ==========================================================================
   HELIX Engine � with Entity Map, Entity Graph & Content-Aware nudges
   ========================================================================== */
function helixRun(){
  if (!viewerEl) return { recommended:[], optional:[], external: [], hidden:[], meta:{} };

  const floors = { strong: FLOORS.STRONG, optional: FLOORS.OPTIONAL, minOverlap: FLOORS.MIN_OVERLAP };

  const headings = ensureHeadingIds(viewerEl);
  const sections = extractSections(viewerEl);
  const introCount = Math.min(2, sections.length);

  const topics = [
    ...topicsFromHeadings(headings),
    ...topicsFromOtherDocsH1(),
    ...topicsFromPublished(),
    ...topicsFromDraft(),
  ];

  // Token caches
  const sectionTokensRaw = sections.map(s => tokens(s.text));
  const sectionTokensNL  = sections.map(s => tokensNL(s.text));

  // Build/refresh Entity Map from headings + visible text (lightweight)
  // � keyed by canonical form
  if (ENTITY_FEATURES.MAP) {
    ENTITY_MAP = new Map();
    const lexSeen = new Set();
    for (const h of headings){
      const can = canonEntity(h.text);
      if (can && !lexSeen.has(can)){
        lexSeen.add(can);
        ENTITY_MAP.set(can, {
          title: h.text,
          aliases: new Set(generateAliasesForTitle(h.text)),
          kind: "heading",
          slugTokens: tokenizeSlug(h.slug),
          freq: 1
        });
      }
    }
    // Mine frequent capitalized multi-words (very light heuristic)
    const rxCapMulti = /\b([A-Z][a-z0-9]+(?:\s+[A-Z][a-z0-9]+){1,4})\b/g;
    const allText = (viewerEl.textContent||"").slice(0, 300000);
    let m;
    while ((m = rxCapMulti.exec(allText))){
      const phrase = m[1].trim();
      const can = canonEntity(phrase);
      if (!can) continue;
      const rec = ENTITY_MAP.get(can) || { title: phrase, aliases:new Set(), kind:"phrase", slugTokens:[], freq:0 };
      rec.freq = (rec.freq||0) + 1;
      ENTITY_MAP.set(can, rec);
    }
  }

  // Build/refresh Entity Graph (co-occurrence within paragraphs)
  if (ENTITY_FEATURES.GRAPH) {
    ENTITY_GRAPH = new Map();
    for (let sIdx=0; sIdx<sections.length; sIdx++){
      const sec = sections[sIdx];
      const toks = tokensNL(sec.text);
      // pull entities present in this section
      const present = [];
      for (const can of ENTITY_MAP.keys()){
        if (toks.join(" ").includes(can)) present.push(can);
        if (present.length>30) break;
      }
      for (let i=0;i<present.length;i++){
        for (let j=i+1;j<present.length;j++){
          const a = present[i], b = present[j];
          if (!a || !b || a===b) continue;
          if (!ENTITY_GRAPH.has(a)) ENTITY_GRAPH.set(a, new Map());
          if (!ENTITY_GRAPH.has(b)) ENTITY_GRAPH.set(b, new Map());
          const rowA = ENTITY_GRAPH.get(a); rowA.set(b, (rowA.get(b)||0)+1);
          const rowB = ENTITY_GRAPH.get(b); rowB.set(a, (rowB.get(a)||0)+1);
        }
      }
    }
    // light normalization (cap weights)
    for (const [, row] of ENTITY_GRAPH.entries()){
      for (const [k,w] of row.entries()){
        row.set(k, Math.min(6, w)); // cap per-partner weight
      }
    }
  }

  // Prepare variant tokens for each topic title/aliases
  const topicTitleVariants = new Map(); // id -> [{rawTok, nlTok, text}]
  for (const t of topics){
    const variants = [t.title, ...(t.aliases||[])].filter(Boolean);
    const uniqV = Array.from(new Set(variants.map(v=>norm(v))));
    topicTitleVariants.set(
      t.id,
      uniqV.map(v => ({ text: v, rawTok: tokens(v), nlTok: tokensNL(v) }))
    );
  }

  const candidates = [];
  const srcCluster = docClusterKey();

  for (let sIdx=0; sIdx<sections.length; sIdx++){
    const sec = sections[sIdx];
    const secTokRaw = sectionTokensRaw[sIdx];
    const secTokNL  = sectionTokensNL[sIdx];
    const anchors = extractAnchorsFromText(sec.text);
    const near = nearestHeadingSlug(headings, sec.el);
    const nearTokensRaw = tokens(near.text);
    const nearTokensNL  = tokensNL(near.text);

    for (const anchor of anchors){
      const anchorTokRaw = tokens(anchor);
      const anchorTokNL  = tokensNL(anchor);
      const aQ = noStopEdges(anchorTokRaw) ? contentRatio(anchorTokRaw) : 0;

      for (const t of topics){
        const variants = topicTitleVariants.get(t.id) || [];
        if (!variants.length) continue;

        let bestVar = variants[0];
        let bestOverlap = 0;
        for (const v of variants){
          const ov = tokenOverlapRatio(anchorTokNL, v.nlTok);
          if (ov > bestOverlap){ bestOverlap = ov; bestVar = v; }
        }

        const A = anchorTokNL.filter(w=>!isStop(w));
        const Tset = new Set(bestVar.nlTok.filter(w=>!isStop(w)));
        let overlapCt = 0; for (const w of A) if (Tset.has(w)) overlapCt++;
        if (overlapCt < floors.minOverlap) continue;

        const overlap = tokenOverlapRatio(anchorTokNL, bestVar.nlTok);
        const cov = sectionCoverage(bestVar.nlTok, secTokNL);

        // URL coverage (slug overlap)
        let urlCov = 0;
        if (t.origin === "published" || t.origin === "other-doc"){
          const utoks = t.slugTokens || (t.url ? tokenizeUrl(t.url) : []); 
          const Aset = new Set(A);
          urlCov = utoks.length ? (utoks.reduce((acc,u)=> acc + (Aset.has(u)?1:0), 0) / utoks.length) : 0;
        } else if (t.origin === "draft"){
          const stoks = t.slugTokens || tokenizeSlug(t.planned_url || t.planned_slug || "");
          const Aset = new Set(A);
          urlCov = stoks.length ? (stoks.reduce((acc,u)=> acc + (Aset.has(u)?1:0), 0) / stoks.length) : 0;
        }

        // Base score
        let score = RB2.W.overlap*overlap + RB2.W.anchorQ*aQ + RB2.W.coverage*cov;
        if (sIdx < introCount) score += RB2.boostIntro;
        if (nearTokensRaw.length && tokenOverlapRatio(bestVar.rawTok, nearTokensRaw) > 0) score += RB2.boostHeading;

        if (t.origin === "draft"){
          if (t.priority && t.priority>=4) score += 0.04;
          if (t.canonical) score += 0.02;
        }

        const anchorNorm = norm(anchor);
        if (t.origin !== "same-doc"){
          const fullTitle = norm(t.title);
          const exactAlias = (t.aliases||[]).some(a => norm(a) === anchorNorm);
          if (anchorNorm === fullTitle || exactAlias) score -= RB2.titleEchoPenalty;
        }

        // Small bump for URL coverage
        score += Math.min(0.06, urlCov*0.12);

        // Embedding similarity (content-aware ?)
        try {
          const aText = anchorTokNL.join(" ");
          const tText = bestVar.nlTok.join(" ");
          const va = embedText(aText);
          const vt = embedText(tText);
          const cs = cosineSim(va, vt);
          score += HELIX.W2.embedSim * cs;
        } catch{}

        // === NEW: Content-Aware nudges (entity overlap, graph neighbors, paragraph sim) ===
        if (ENTITY_FEATURES.CONTENT_AWARE){
          const entOv = entityOverlap01(anchorTokNL, ENTITY_MAP);                // 0..1
          const graphB = graphNeighborBoost01(anchorTokNL, t.title, ENTITY_MAP, ENTITY_GRAPH, secTokNL); // 0..1
          const paraCS = paragraphContextSim01(sec.text, t.title);               // 0..1
          // blend (small, controlled)
          score += 0.06 * entOv + 0.05 * graphB + 0.05 * paraCS;
        }

        // ILR band (authority)
        const tUrl = t.origin==="same-doc" ? t.url
                 : (t.origin==="published" || t.origin==="other-doc" ? (t.url || "") : (t.planned_url || ""));
        const mult = HELIX.ilrBand.base + HELIX.ilrBand.span * ilr01(tUrl || "");
        score *= clamp01(mult);

        // Cluster dynamics
        const tgtCluster = targetClusterKey(t);
        if (isHubTarget(t)) score += HELIX.cluster.hubBoost;
        if (srcCluster && tgtCluster){
          if (srcCluster === tgtCluster) score += HELIX.cluster.sameClusterBoost;
          else score -= HELIX.cluster.crossClusterPenalty;
        }

        candidates.push({
          anchor: { text: anchor, sectionIdx: sIdx },
          target: {
            topicId: t.topicId || t.id,
            title: t.title,
            kind: t.origin,
            url: tUrl,
            planned_slug: t.planned_slug || ""
          },
          reason: { overlap, anchorQ: aQ, coverage: cov, urlCov },
          rawScore: clamp01(score)
        });
      }
    }
  }

  const rankKind = k => (k==="published"?3 : k==="other-doc"?2 : k==="draft"?1 : 0);

  // Deduplicate per anchor (keep best score/kind)
  const byAnchor = new Map();
  for (const c of candidates){
    const k = norm(c.anchor.text);
    const prev = byAnchor.get(k);
    if (!prev) { byAnchor.set(k, c); continue; }
    if (c.rawScore > prev.rawScore) { byAnchor.set(k, c); continue; }
    if (c.rawScore === prev.rawScore){
      if (rankKind(c.target.kind) > rankKind(prev.target.kind)) byAnchor.set(k, c);
    }
  }
  const deduped = Array.from(byAnchor.values());

  // Visibility cut
  const visible = deduped.filter(c => c.rawScore >= FLOORS.OPTIONAL);
  const hidden  = deduped.filter(c => c.rawScore < FLOORS.OPTIONAL);
  visible.sort((a,b)=> b.rawScore - a.rawScore);

  // Placement caps + word windowing
  const perTopic = new Map();
  const perSection = new Map();
  const placed = [];
  const wordOff = cumulativeWordOffsets(extractSections(viewerEl));

  function underWordWindow(idx){
    const r = WINDOW_RADIUS_WORDS - 1;
    const wStart = idx - r, wEnd = idx + r;
    return placed.filter(p=> p.wordIdx>=wStart && p.wordIdx<=wEnd).length;
  }

  for (const c of visible){
    const sIdx = c.anchor.sectionIdx;
    const tId = c.target.topicId;
    const tCnt = (perTopic.get(tId)||0); if (tCnt >= CAPS.MAX_PER_TOPIC) continue;
    const sCnt = (perSection.get(sIdx)||0); if (sCnt >= CAPS.MAX_PER_SECTION) continue;

    // recompute in fresh DOM (unchanged logic)
    const sections2 = extractSections(viewerEl);
    const idx = anchorWordIndex(sections2[sIdx], c.anchor.text, wordOff[sIdx]);
    if (underWordWindow(idx) >= CAPS.MAX_PER_200W) continue;

    placed.push({ wordIdx: idx, item: c });
    perTopic.set(tId, tCnt+1);
    perSection.set(sIdx, sCnt+1);
  }

  const picked = placed.map(p=>p.item);

  const recommended = picked
    .filter(c=> c.rawScore >= FLOORS.STRONG)
    .map(c=> ({ ...c, bucket: "strong", finalScore: c.rawScore }));
  const optional = picked
    .filter(c=> c.rawScore < FLOORS.STRONG && c.rawScore >= FLOORS.OPTIONAL)
    .map(c=> ({ ...c, bucket: "optional", finalScore: c.rawScore }));

  // Gap candidates for playbook (no published URL)
  const gapCandidates = deduped
    .filter(c => c.target.kind !== "published" || !c.target.url)
    .map(c => ({ anchor: c.anchor.text, title: c.target.title, kind: c.target.kind, url: c.target.url || "", score: c.rawScore }));

  // Prepublish fallback
  if (!recommended.length && !optional.length && PHASE === "prepublish"){
    const fallback = deduped
      .sort((a,b)=> b.rawScore - a.rawScore)
      .slice(0,3)
      .map(c=> ({ ...c, bucket:"optional", finalScore:c.rawScore, reason:{...c.reason, fallback:true} }));
    return {
      recommended: [],
      optional: fallback,
      external: [],
      hidden,
      meta: { floors: FLOORS, caps: CAPS, totals: { candidates: candidates.length, passed: visible.length, picked: fallback.length }, phase: PHASE, gapCandidates, engine:"HELIX" }
    };
  }

  return {
    recommended,
    optional,
    external: [],
    hidden,
    meta: { floors: FLOORS, caps: CAPS, totals: { candidates: candidates.length, passed: visible.length, picked: picked.length }, phase: PHASE, gapCandidates, engine:"HELIX" }
  };
}

/* RB2 fallback (kept) */
function rb2Run(){ return helixRun(); }

/* ==========================================================================
   External Categories (pluggable) � dynamic import
   ========================================================================== */
let EXT_CAT = {
  API: null,            // the whole default export (object)
  EXTERNAL_CATEGORY_SET: new Set(), // convenience cache
};

async function ensureExternalCategories(){
  if (ensureExternalCategories.loaded) return EXT_CAT;
  try {
    // Load from /data/ (stable path)
    const mod = await import("./data/external_categories.js");
    const api = mod?.default || mod || {};
    // sanity check
    if (api && (api.EXTERNAL_CATEGORY_SET || api.EXTERNAL_CATEGORY_WHITELIST)) {
      EXT_CAT.API = api;
      EXT_CAT.EXTERNAL_CATEGORY_SET = api.EXTERNAL_CATEGORY_SET
        ? api.EXTERNAL_CATEGORY_SET
        : new Set((api.EXTERNAL_CATEGORY_WHITELIST || []).map(s => String(s||"").toLowerCase().trim()).filter(Boolean));
      if (DEBUG) console.log("[external_categories] loaded:", {
        categories: EXT_CAT.EXTERNAL_CATEGORY_SET.size
      });
    } else {
      console.warn("[external_categories] present but missing expected fields; continuing with empty set.");
      EXT_CAT.API = null;
      EXT_CAT.EXTERNAL_CATEGORY_SET = new Set();
    }
  } catch (e){
    console.warn("[external_categories] not available; using built-ins only.", e);
    EXT_CAT.API = null;
    EXT_CAT.EXTERNAL_CATEGORY_SET = new Set();
  }
  ensureExternalCategories.loaded = true;
  return EXT_CAT;
}

/* ==========================================================================
   External V2 helpers (local) � mirrors internal logic for external cues
   ========================================================================== */
function isAlphaPhrase(tokArr) {
  if (!tokArr || tokArr.length < EXT_V2.THRESHOLDS.MIN_TOKENS || tokArr.length > EXT_V2.THRESHOLDS.MAX_TOKENS) return false;
  if (!noStopEdges(tokArr)) return false;
  return contentRatio(tokArr) >= EXT_V2.THRESHOLDS.MIN_CONTENT_RATIO;
}
function docTermFreq(text, phrase) {
  try {
    const rx = makeBoundaryRx(phrase);
    let m, n = 0;
    while ((m = rx.exec(text))) n++;
    return n;
  } catch { return 0; }
}
function nearHeadingBoost(headings, el) {
  if (!el) return 0;
  const near = nearestHeadingSlug(headings, el);
  return near?.text ? EXT_V2.THRESHOLDS.HEADING_BOOST : 0;
}
function noveltyPenaltyVsInternal(anchorTokNL, internalPool) {
  if (!internalPool || !internalPool.length) return 0;
  let best = 0;
  for (const it of internalPool) {
    const tTok = tokensNL(it?.target?.title || "");
    const ov = tokenOverlapRatio(anchorTokNL, tTok);
    if (ov > best) best = ov;
  }
  return Math.min(EXT_V2.THRESHOLDS.NOVELTY_PENALTY, best * EXT_V2.THRESHOLDS.NOVELTY_PENALTY);
}
function makeWikiHeuristicSuggestion(anchor) {
  const slug = anchor.trim().replace(/\s+/g, "_").replace(/[^\p{L}\p{N}_()-]/gu, "");
  return {
    title: anchor,
    url: `https://en.wikipedia.org/wiki/${slug}`,
    domainRoot: "wikipedia.org",
    provider: "heuristic",
    score: 0.5
  };
}

/* === External Positive Cues (subset) ================= */
function isTitleCaseWord(w){ return /^[A-Z][a-z0-9\-]*$/.test(w||""); }
const BUILTIN_KNOWN_TECH = new Set([
  "React","Angular","Vue","Svelte","Next.js","Nuxt","Kubernetes","Docker","Terraform","Ansible","Airflow","Spark","Hadoop","PostgreSQL","MySQL","MongoDB","Redis","Elasticsearch","Kibana","Grafana","Prometheus","PyTorch","TensorFlow","Scikit-learn","Pandas","NumPy","Django","Flask","Laravel","Symfony","FastAPI","Go","Rust","Node.js","Vite","Webpack","Babel","Tailwind","Bootstrap","jQuery","Sass","Keras","XGBoost","LightGBM","CatBoost","OpenAI","Hugging Face","LangChain","Celery","RabbitMQ","Kafka","Jenkins","GitLab","GitHub Actions"
]);
function cueProperNounMulti(tokRaw){
  if (!tokRaw || tokRaw.length < 2) return false;
  const tc = tokRaw.every(t => isTitleCaseWord(t) || /^[A-Z0-9\-]+$/.test(t));
  const stopEdge = noStopEdges(tokRaw);
  return tc && stopEdge;
}
function cueStandardsSpec(text){
  const rx = /\b(?:ISO(?:\/IEC)?|IEC|NIST|PCI|SOC\s*2|SOC\s*1|RFC|IEEE|WCAG|FIPS|CSA|EN|BSI|ETSI)\s*[-:]?\s*\d{2,5}(?:[:\-]\d{2,4})?(?:\s*(?:v(?:er(?:sion)?)?\.?\s*\d+(?:\.\d+)*))?\b/i;
  const rx2 = /\b(?:GDPR|HIPAA|CCPA)\b(?:.*?\b(?:Article|Section)\s*\d+[a-z]?)?/i;
  return rx.test(text) || rx2.test(text);
}
function cueLibraryTool(text, tokRaw){
  const KNOWN = BUILTIN_KNOWN_TECH;
  const first = (tokRaw && tokRaw[0]) ? tokRaw[0] : "";
  const normFirst = first.charAt(0).toUpperCase()+first.slice(1);
  const cleaned = text.replace(/\s+\d+.*$/,"");
  const hasKnown = KNOWN.has(normFirst) || KNOWN.has(cleaned);
  const titleish = tokRaw && tokRaw.every(t => isTitleCaseWord(t) || /^[A-Za-z0-9\.\-]+$/.test(t));
  const hasVersion = /\b(?:v(?:er(?:sion)?)?\.?\s*)?\d+(?:\.\d+)*\b/.test(text);
  return (hasKnown || titleish) && (tokRaw?.length>=1) && (hasVersion || tokRaw.length>=2);
}
function cueProtocolFormat(text){
  const t = text.toLowerCase();
  if (/\boauth\s*2(\.0)?\b/.test(t)) return true;
  if (/\bopenid\s+connect\b/.test(t)) return true;
  if (/\bjson\s+schema\b/.test(t)) return true;
  if (/\bopenapi\b/.test(t)) return true;
  if (/\bgraphql\b/.test(t)) return true;
  if (/\bgrpc\b/.test(t)) return true;
  if (/\bsaml\b/.test(t)) return true;
  if (/\bjwt\b/.test(t)) return true;
  if (/\bhttp\/[23]\b/.test(t)) return true;
  if (/\bwebsocket\b/.test(t)) return true;
  return false;
}
function cueSciMed(text){
  const t = text;
  const morph = /\b[\p{L}]{5,}(itis|osis|emia|algia|ectomy|opathy|genesis|omics)\b/iu.test(t);
  const gene  = /\b[A-Z]{2,}\d+(?:-\d+)?\b/.test(t);
  const crispr = /\bCRISPR[-�]?[A-Za-z0-9]+\b/.test(t);
  return morph || gene || crispr;
}
function cueCanonicalCollocation(tokRaw){
  if (!tokRaw || tokRaw.length < 2 || tokRaw.length > 4) return false;
  const ratio = contentRatio(tokRaw);
  if (ratio < 0.75) return false;
  const hasLower = tokRaw.some(t => /^[a-z]/.test(t));
  return hasLower;
}
function cueAcronymExpansion(text){
  const rx1 = /^\s*[A-Za-z][A-Za-z0-9&\-\s]{2,}\s*\(\s*[A-Z]{2,}\s*\)\s*$/;
  const rx2 = /^\s*[A-Z]{2,}\s*\(\s*[A-Za-z][A-Za-z0-9&\-\s]{2,}\s*\)\s*$/;
  return rx1.test(text) || rx2.test(text);
}
function cueRegulatory(text){
  const t = text.toLowerCase();
  if (/\b(gdpr|hipaa|ccpa|ferpa|sox|sarbanes[- ]oxley|coppa|fcpa)\b/.test(t)) return true;
  if (/\b(article|section|rule|directive|regulation|act)\s*\d+[a-z]?\b/.test(t)) return true;
  return false;
}

/* Category hits via external_categories.js (door 2 + door 1) */
function externalCategoryHits(anchorText){
  const out = [];
  const api = EXT_CAT?.API;
  if (!api) return out;

  const cats = Array.from(EXT_CAT.EXTERNAL_CATEGORY_SET || []);
  const phraseNorm = norm(anchorText);

  for (const cat of cats){
    try {
      // (2) Exact match in category gazetteer
      if (typeof api.inCategoryGazetteer === "function" && api.inCategoryGazetteer(cat, phraseNorm)) {
        out.push(cat);
        continue;
      }
      // (3) Match to a category recognizer regex
      const recs = typeof api.recognizersFor === "function" ? (api.recognizersFor(cat) || []) : [];
      if (recs.some(rx => { try { return rx.test(anchorText); } catch { return false; } })) {
        out.push(cat);
      }
    } catch { /* ignore */ }
  }
  return out;
}

/* Replaces previous detectPositiveCuesExternal(...); includes category bumps */
function detectPositiveCuesExternal(anchorText, tokRaw){
  const cats = [];
  try {
    if (cueProperNounMulti(tokRaw))                               cats.push(["ProperNounMulti", 0.06]);
    if (cueStandardsSpec(anchorText))                             cats.push(["StandardsSpecID", 0.10]);
    if (cueLibraryTool(anchorText, tokRaw))                       cats.push(["LibraryToolProduct", 0.08]);
    if (cueProtocolFormat(anchorText))                            cats.push(["ProtocolFormat", 0.08]);
    if (cueSciMed(anchorText))                                    cats.push(["SciMed", 0.09]);
    if (cueCanonicalCollocation(tokRaw))                          cats.push(["CanonicalCollocation", 0.06]);
    if (cueAcronymExpansion(anchorText))                          cats.push(["AcronymExpansion", 0.10]);
    if (cueRegulatory(anchorText))                                cats.push(["RegulatoryGov", 0.10]);

    // NEW: category-based bumps
    const hits = externalCategoryHits(anchorText);
    const catBumpEach = 0.06;
    const catCap = 0.18;
    const catBump = Math.min(catCap, (hits.length * catBumpEach));
    hits.forEach(h => cats.push([`cat:${h}`, catBumpEach]));

  } catch {}

  // total cap across all positives (legacy cap kept)
  const bump = Math.min(0.18, cats.reduce((a, [,w]) => a + w, 0));
  return { bump, categories: cats.map(([n])=>n) };
}

/* ==========================================================================
   External V2 (local) � scoring and placement
   ========================================================================== */
function externalLocalRun(options = {}) {
  if (!viewerEl || !EXT_V2.ENABLED) return { suggestions: [], meta: { passed:0, filtered:0 } };

  const text = viewerEl.textContent || "";
  const headings = ensureHeadingIds(viewerEl);
  const sections = extractSections(viewerEl);

  const internalPool = options.internalPool || [
    ...(LAST_ENGINE_OUTPUT?.recommended || []),
    ...(LAST_ENGINE_OUTPUT?.optional || [])
  ];

  const bucket = getBucketMap();
  const externalBucket = bucket.external || new Set();

  const seen = new Set();
  const candidates = [];
  for (let sIdx = 0; sIdx < sections.length; sIdx++) {
    const sec = sections[sIdx];
    const anchors = extractAnchorsFromText(sec.text);
    for (const a of anchors) {
      const rawTok = tokens(a);
      const nlTok  = tokensNL(a);
      const key = norm(a);
      if (seen.has(key)) continue;
      seen.add(key);

      const alphaOk = isAlphaPhrase(rawTok);
      const bucketWhitelisted = externalBucket.has(key);
      // NEW: category gate � if it matches any recognizer or gazetteer we allow it through
      const catHits = externalCategoryHits(a);
      const categoryQualified = catHits.length > 0;

      // Gate: must be alpha phrase OR in bucket OR matched a category
      if (!alphaOk && !bucketWhitelisted && !categoryQualified) continue;

      if (EXT_V2.BLOCK_SINGLE_TOKEN_UPPERCASE && rawTok.length === 1 && /^[A-Z0-9\-]+$/.test(rawTok[0]) && !bucketWhitelisted && !categoryQualified) continue;
      if (EXT_V2.RESPECT_REJECTIONS && isRejected("external", key)) continue;

      candidates.push({ anchorTokRaw: rawTok, anchorTokNL: nlTok, anchorText: a, sectionIdx: sIdx, secEl: sec.el, catHits });
    }
  }

  const textFull = text;
  const sorted = candidates.sort((a,b) => {
    const aKey = externalBucket.has(norm(a.anchorText)), bKey = externalBucket.has(norm(b.anchorText));
    if (aKey !== bKey) return aKey ? -1 : 1;
    const aQ = contentRatio(a.anchorTokRaw), bQ = contentRatio(b.anchorTokRaw);
    const aF = docTermFreq(textFull, a.anchorText), bF = docTermFreq(textFull, b.anchorText);
    return (bQ*bF) - (aQ*aF);
  });

  const wordOff = cumulativeWordOffsets(sections);
  const placed = [];
  let filtered = 0;

  function underWordWindow(idx){
    const wStart = idx - WINDOW_RADIUS_WORDS, wEnd = idx + WINDOW_RADIUS_WORDS;
    return placed.filter(p=> p.wordIdx>=wStart && p.wordIdx<=wEnd).length;
  }
  const perSection = new Map();

  for (const c of sorted) {
    const key = norm(c.anchorText);
    const aQ = contentRatio(c.anchorTokRaw);
    const df = Math.max(0, Math.min(5, docTermFreq(textFull, c.anchorText)));
    const dfNorm = df >= EXT_V2.THRESHOLDS.MIN_DOC_FREQ ? Math.min(1, df/3) : 0;

    if (df < EXT_V2.THRESHOLDS.MIN_DOC_FREQ) { filtered++; continue; }

    let score = 0;
    score += 0.55 * aQ;
    score += 0.20 * dfNorm;
    score += nearHeadingBoost(headings, c.secEl);
    score -= noveltyPenaltyVsInternal(c.anchorTokNL, internalPool);

    // Positive cues (includes NEW category bumps)
    const pos = detectPositiveCuesExternal(c.anchorText, c.anchorTokRaw);
    score += pos.bump;

    // Tiering � but if user bucket-whitelisted it, never drop
    const tier = score >= EXT_V2.THRESHOLDS.STRONG ? "strong"
               : score >= EXT_V2.THRESHOLDS.OPTIONAL ? "optional" : "drop";

    if (tier === "drop" && !externalBucket.has(key)) { filtered++; continue; }

    const idx = anchorWordIndex(sections[c.sectionIdx], c.anchorText, wordOff[c.sectionIdx]);
    if (underWordWindow(idx) >= EXT_V2.CAPS.MAX_PER_200W) { filtered++; continue; }

    const sCnt = (perSection.get(c.sectionIdx) || 0);
    if (sCnt >= EXT_V2.CAPS.MAX_PER_SECTION) { filtered++; continue; }

    placed.push({
      wordIdx: idx,
      item: c,
      score,
      tier,
      posCats: pos.categories,
      posBoost: pos.bump
    });
    perSection.set(c.sectionIdx, sCnt + 1);

    if (placed.length >= EXT_V2.CAPS.MAX_TOTAL) break;
  }

  const suggestions = placed
    .sort((a,b)=> b.score - a.score)
    .map(p => ({
      anchor: { text: p.item.anchorText, sectionIdx: p.item.sectionIdx },
      target: {
        topicId: `x:${norm(p.item.anchorText)}`,
        title: p.item.anchorText,
        kind: "external",
        url: "" // picked later in modal
      },
      bucket: p.tier,
      finalScore: Math.max(0, Math.min(1, p.score)),
      posCues: p.posCats || [],
      posBoost: p.posBoost || 0,
      // keep the quick-start suggestion to Wikipedia
      suggestions: [ makeWikiHeuristicSuggestion(p.item.anchorText) ]
    }));

  return { suggestions, meta: { passed: suggestions.length, filtered } };
}

/* ==========================================================================
   Bucket highlights + mark rendering helpers
   ========================================================================== */
function unwrapMarks(){
  if (!viewerEl) return;
  viewerEl.querySelectorAll("mark.kwd, mark.kwd-int, mark.kwd-ext, mark.kwd-sem").forEach(m=>{
    const core = m.querySelector?.(".kw-core");
    const plain = (core?.textContent ?? m.textContent ?? "");
    m.parentNode.replaceChild(document.createTextNode(plain), m);
  });
}
function getEngineMarkCount(){
  return viewerEl ? Array.from(viewerEl.querySelectorAll("mark.kwd")).length : 0;
}
function updateHighlightBadge(){
  if (!highlightCountBadge) return;
  const count = getEngineMarkCount();
  highlightCountBadge.textContent = String(count);
}
function underlineLinkedPhrases(){
  if (!viewerEl || !LINKED_SET.size) return;
  const walker=document.createTreeWalker(viewerEl, NodeFilter.SHOW_TEXT,null);
  const phrases=Array.from(LINKED_SET).sort((a,b)=>b.length-a.length);
  const nodes=[]; while(walker.nextNode()) nodes.push(walker.currentNode);
  for(const tn of nodes){
    let text=tn.nodeValue, changed=false;
    for(const phrase of phrases){
      const rx=makeBoundaryRx(phrase); if(!rx.test(text)) continue;
      text=text.replace(
        rx,
        (m,pre,core)=>`${pre}<span class="lc-underlined" style="text-decoration:underline;" data-phrase="${encodeURIComponent(phrase)}"><span class="kw-core">${core}</span></span>`
      );
      changed=true;
    }
    if(changed){ const span=document.createElement("span"); span.innerHTML=text; tn.parentNode.replaceChild(span, tn); }
  }
}

// Remove keyword marks around/inside headings (h1�h6) so titles are never highlighted
function stripMarksFromHeadings(root) {
  if (!root) return;

  // 1) Case A: <mark> WRAPS a heading, e.g. <mark><h1>Title</h1></mark>
  const allMarks = root.querySelectorAll(
    "mark.kwd, mark.kwd-strong, mark.kwd-optional, " +
    "mark.kwd-external, mark.kwd-int, mark.kwd-sem, mark.kwd-ext"
  );

  allMarks.forEach(mark => {
    const heading = mark.querySelector("h1,h2,h3,h4,h5,h6");
    // If the only real element inside the mark is a heading, unwrap it
    if (heading && mark.childElementCount === 1 && heading === mark.firstElementChild) {
      mark.replaceWith(heading);   // keep <h1>...</h1>, drop <mark>
    }
  });

  // 2) Case B: <mark> INSIDE a heading, e.g. <h1><mark>Title</mark></h1>
  const headings = root.querySelectorAll("h1,h2,h3,h4,h5,h6");

  headings.forEach(h => {
    const innerMarks = h.querySelectorAll(
      "mark.kwd, mark.kwd-strong, mark.kwd-optional, " +
      "mark.kwd-external, mark.kwd-int, mark.kwd-sem, mark.kwd-ext"
    );

    innerMarks.forEach(m => {
      const text = m.textContent || "";
      const textNode = document.createTextNode(text);
      m.replaceWith(textNode);   // plain text inside the heading
    });
  });
}


/* Residue-safe unwrap (used by IL modal) */
function unwrapMark(el){
  if (!el || !el.parentNode) return null;
  const core = el.querySelector?.(".kw-core");
  const text = (core?.textContent ?? el.textContent ?? "").trim();
  const tn = document.createTextNode(text);
  el.parentNode.replaceChild(tn, el);
  return tn;
}

/* Apply engine/bucket marks to DOM */
function applyMarksFromSuggestions(suggestions, opts = {}) {
  const append       = opts.append !== false;
  const perPassLimit = opts.perPassLimit || MAX_UNIQUE_PHRASES;
  if (!viewerEl) return 0;

  // If not appending, unwrap existing engine marks first
  if (!append) {
    viewerEl.querySelectorAll("mark.kwd").forEach(m => {
      const core = m.querySelector?.(".kw-core");
      const t = document.createTextNode((core?.textContent ?? m.textContent) || "");
      // GUARD 1: parent may be null if DOM changed
      if (m.parentNode) {
        m.parentNode.replaceChild(t, m);
      }
    });
  }



  // Existing phrases already marked in the viewer
  const existingMarked = new Set(
    Array.from(viewerEl.querySelectorAll("mark.kwd")).map(m => {
      const p = decodeURIComponent(m.getAttribute("data-phrase") || "").trim() ||
                (m.textContent || "").trim();
      return norm(p);
    })
  );

  // Collect eligible text nodes
  const walker = document.createTreeWalker(viewerEl, NodeFilter.SHOW_TEXT, {
    acceptNode(node){
      if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      let p = node.parentNode;
      while (p && p !== viewerEl) {
        if (p.nodeType === 1) {
          if (p.tagName === "A" || p.tagName === "MARK" || p.classList?.contains("lc-underlined")) {
            return NodeFilter.FILTER_REJECT;
          }
          if (/^(H1|H2|H3|H4|H5|H6|NAV|ASIDE|HEADER|FOOTER)$/i.test(p.tagName)) {
            return NodeFilter.FILTER_REJECT;
          }
        }
        p = p.parentNode;
      }
      return NodeFilter.FILTER_ACCEPT;
    }
  });
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);

  const controlsHtml = `<span class="kw-ctl" aria-hidden="true"
      style="position:absolute;right:-8px;top:-8px;display:flex;gap:2px;opacity:0;pointer-events:none;">
    <button class="kw-btn kw-accept" title="Accept"
      style="font-size:11px;width:16px;height:16px;border-radius:999px;border:1px solid #10b981;color:#10b981;background:#fff;cursor:pointer;padding:0;">✓</button>
    <button class="kw-btn kw-reject" title="Reject"
      style="font-size:11px;width:16px;height:16px;border-radius:999px;border:1px solid #ef4444;color:#ef4444;background:#fff;cursor:pointer;padding:0;">✕</button>
    </span>`;

  window.REJECTED_SET = window.REJECTED_SET || new Set();

  let applied = 0;
  const usedAnchors = new Set();    // phraseNorm -> already used once
  const phraseHits  = new Map();    // phraseNorm -> count in this document

  outer: for (const s of suggestions) {

    const rawPhrase =
  (s.anchor && (s.anchor.paint || s.anchor.text)) ||
  s.phrase ||
  "";

    const phraseNorm = norm(rawPhrase);

    // 1) No raw text ? skip
    if (!rawPhrase) continue;

    // 2) Use existing phrase filter (stopwords, length, etc.)
    if (!shouldHighlightPhrase(rawPhrase)) continue;

    // 3) Bucket comes from RB2 (backend) � DO NOT re-floor here.
// RB2 already decided strong vs optional using its own thresholds.
const bucket = (s.bucket === "strong" ? "strong" : "optional");
const score  = (typeof s.score === "number" ? s.score : 1.0);

// Keep debug only (optional)
// console.log("[MARKS CHECK]", { rawPhrase, bucket, score });



    // 4) Global guards
    if (!phraseNorm ||
        usedAnchors.has(phraseNorm) ||
        LINKED_SET.has(phraseNorm) ||
        existingMarked.has(phraseNorm) ||
        isRejected("engine", phraseNorm)) {
      continue;
    }

    // 5) Cap total marks
    if (getEngineMarkCount() + applied >= MAX_TOTAL_HIGHLIGHTS) break outer;

    const rx = makeBoundaryRx(phraseNorm);

    for (const tn of nodes) {
      // GUARD 2: node may be detached by previous replacements
      if (!tn || !tn.parentNode) continue;

      rx.lastIndex = 0;
      const m = rx.exec(tn.nodeValue);
      if (!m) continue;

      const preLen = m.index + (m[1] ? m[1].length : 0);
      const before = tn.nodeValue.slice(0, preLen);
      const core   = m[2];
      const after  = tn.nodeValue.slice(m.index + m[0].length);
      const span   = document.createElement("span");

      const isExternal = (s.target?.kind || "").toLowerCase() === "external";
      let cls = "kwd " + (isExternal ? "kwd-external kwd-ext" :
                          (s.bucket === "strong" ? "kwd-strong" : "kwd-optional"));
      const dataStrength = (s.bucket === "strong" ? "strong" : "optional");

      const extStyle  = "background:rgba(16,185,129,.18);box-shadow:0 -2px 0 rgba(16,185,129,.45) inset;";
      const styleAttr = isExternal ? `position:relative;${extStyle}` : "position:relative;";

      const suggAttr = s.suggestions
        ? ` data-suggestions="${escapeAttr(JSON.stringify((s.suggestions || []).slice(0,3)))}"`
        : "";
      const posAttr  = (s.posCues && s.posCues.length)
        ? ` data-poscues="${escapeAttr(JSON.stringify(s.posCues))}" data-posboost="${String(s.posBoost || 0)}"`
        : "";

      span.innerHTML =
        `${escapeHtml(before)}<mark class="${cls}" data-strength="${dataStrength}"` +
        ` data-phrase="${encodeURIComponent(phraseNorm)}"` +
        ` data-topic-id="${escapeAttr(s.target?.topicId || "")}"` +
        ` data-kind="${escapeAttr(s.target?.kind || "")}"` +
        ` data-url="${escapeAttr(s.target?.url || "")}"` +
        ` data-title="${escapeAttr(s.target?.title || "")}"` +
        `${suggAttr}${posAttr} tabindex="0" style="${styleAttr}">` +
          `<span class="kw-core">${escapeHtml(core)}</span>${controlsHtml}` +
        `</mark>${escapeHtml(after)}`;

      tn.parentNode.replaceChild(span, tn);

      usedAnchors.add(phraseNorm);
      applied++;

      const count = phraseHits.get(phraseNorm) || 0;
      phraseHits.set(phraseNorm, count + 1);

      // Per-phrase cap for this pass
      if (phraseHits.get(phraseNorm) >= perPassLimit) {
        continue outer;
      }

      // Global cap
      if (getEngineMarkCount() + applied >= MAX_TOTAL_HIGHLIGHTS) {
        break outer;
      }

      // Move to next suggestion after first replacement in this node
      break;
    }
  }

  return applied;
}


/* Side panel list */
function engineCardEl() { return highlightCountBadge ? highlightCountBadge.closest(".card") : null; }
function ensureEnginePanelScaffold() {
  const card = engineCardEl();
  if (!card) return null;
  let list = card.querySelector("#engineHighlightList");
  if (!list) {
    list = document.createElement("div");
    list.id = "engineHighlightList";
    list.style.marginTop = "8px";
    card.insertBefore(list, card.lastElementChild);
  }
  const resetBtn = card.querySelector("#btnResetLinked");
  const resetRow = resetBtn ? resetBtn.parentElement : null;
  if (resetRow && resetRow !== card.lastElementChild) card.appendChild(resetRow);
  return list;
}
function scrollToMark(mark) {
  try { mark.scrollIntoView({ behavior: "smooth", block: "center" }); mark.classList.add("flash"); setTimeout(() => mark.classList.remove("flash"), 900); mark.focus?.(); } catch {}
}
function rebuildEngineHighlightsPanel() {
  const list = ensureEnginePanelScaffold();
  if (!list) return;

  const filt = (engineFilter?.value || "all");

  if (filt === "bucket"){
    const b = loadBucketsFromStore() || {};
    const strong   = (b.strong   ?? b.internal ?? []);
    const optional = (b.optional ?? b.semantic ?? []);
    const external = (b.external ?? []);
    const rows = [
      ...strong.map(w => ({phrase:w, tier:"Strong",   mode:"internal", dot:"#3b82f6"})),
      ...optional.map(w => ({phrase:w, tier:"Optional", mode:"internal", dot:"#f59e0b"})),
      ...external.map(w => ({phrase:w, tier:"External", mode:"external", dot:"#10b981"})),
    ];

    if (!rows.length){
      list.innerHTML = `<div style="font-size:12px;color:#6b7280;">No bucket entries saved.</div>`;
      return;
    }

    list.innerHTML = rows.map((r, i) => {
      return `
        <div class="kw-item" data-phrase="${escapeHtml(r.phrase)}" data-mode="${r.mode}" data-i="${i}">
          <span class="kw-dot" style="display:inline-block;width:8px;height:8px;border-radius:999px;background:${r.dot};margin-right:6px;"></span>
          <button class="kw-jump" title="Find in doc" style="font-size:12px;">${escapeHtml(r.phrase)}</button>
          <span class="qty" style="font-size:12px;color:#6b7280;">� ${r.tier} (Bucket)</span>
        </div>
      `;
    }).join("");

    Array.from(list.querySelectorAll(".kw-item")).forEach((row) => {
      const phrase = row.getAttribute("data-phrase") || "";
      row.querySelector(".kw-jump")?.addEventListener("click", (e)=>{
        e.preventDefault();
        const m = Array.from(viewerEl.querySelectorAll(`mark.kwd-int, mark.kwd-ext, mark.kwd-sem, mark.kwd`))
          .find(x => decodeURIComponent(x.getAttribute("data-phrase")||"") === phrase);
        if (m) { scrollToMark(m); return; }
        const rx = makeBoundaryRx(phrase);
        const tnWalker = document.createTreeWalker(viewerEl, NodeFilter.SHOW_TEXT, null);
        while (tnWalker.nextNode()){
          const tn = tnWalker.currentNode;
          rx.lastIndex = 0;
          if (rx.test(tn.nodeValue||"")) { tn.parentElement?.scrollIntoView({behavior:"smooth", block:"center"}); break; }
        }
      });
    });

    updateHighlightBadge();
    return;
  }

  let marks = viewerEl ? Array.from(viewerEl.querySelectorAll("mark.kwd")) : [];
  if (filt === "strong")   marks = marks.filter(m => m.classList.contains("kwd-strong"));
  if (filt === "optional") marks = marks.filter(m => m.classList.contains("kwd-optional"));
  if (filt === "external") marks = marks.filter(m => m.classList.contains("kwd-external"));

  updateHighlightBadge();
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
    const dot = external ? '#10b981' : strong ? '#3b82f6' : '#f59e0b';
    return `
      <div class="kw-item" data-i="${i}">
        <span class="kw-dot" style="display:inline-block;width:8px;height:8px;border-radius:999px;background:${dot};margin-right:6px;"></span>
        <button class="kw-jump" title="Jump to highlight" style="font-size:12px;">${escapeHtml(phrase)}</button>
        <span class="qty" style="font-size:12px;color:#6b7280;">� ${tier}</span>
      </div>
    `;
  }).join("");

  Array.from(list.querySelectorAll(".kw-item")).forEach((row, idx) => {
    row.querySelector(".kw-jump")?.addEventListener("click", (e)=>{
      e.preventDefault();
      const m = marks[idx];
      if (m) scrollToMark(m);
    });
  });
}
engineFilter?.addEventListener("change", rebuildEngineHighlightsPanel);

/* ==========================================================================
   API + Downloads (+ manifest)
   ========================================================================== */
// === BEGIN: export helpers for HTML/TXT ===
function resolveUrlForSpan(span){
  let url = (span.getAttribute("data-url") || "").trim();
  if (url) return url;

  const kind    = (span.getAttribute("data-kind") || "").toLowerCase();
  const topicId = span.getAttribute("data-topic-id") || "";
  const title   = (span.getAttribute("data-title") || span.textContent || "").trim();

  if (kind === "same-doc") {
    const slug = slugifyHeading(title);
    return "#" + slug;
  }

  if (kind === "published") {
    for (const [,v] of PUBLISHED_TOPICS.entries()){
      if ((topicId && v.id === topicId) || norm(v.title) === norm(title)) {
        if (v.url) return v.url;
      }
    }
    const rec = TITLE_INDEX.get(norm(title));
    if (rec?.url) return rec.url;
    const urls = Array.from(IMPORTED_URLS || []);
    const guess = bestUrlForTitle(title, urls, 0.70);
    if (guess) return guess;
  }

  if (kind === "draft") {
    for (const [,v] of DRAFT_TOPICS.entries()){
      if ((topicId && v.id === topicId) || norm(v.working_title) === norm(title)) {
        if (v.planned_url) return v.planned_url;
      }
    }
  }
  return "";
}

function exportableInnerHTML(){
  if (!viewerEl) return "";
  const root = viewerEl.cloneNode(true);

  // unwrap engine/bucket marks
  root.querySelectorAll("mark.kwd, mark.kwd-int, mark.kwd-ext, mark.kwd-sem").forEach(m => {
    const core = m.querySelector?.(".kw-core");
    const t = document.createTextNode((core?.textContent ?? m.textContent) || "");
    m.parentNode.replaceChild(t, m);
  });

  // convert accepted underlines to <a href="">
  root.querySelectorAll("span.lc-underlined").forEach(span => {
    const text = span.textContent || "";
    const href = resolveUrlForSpan(span);
    if (href) {
      const a = document.createElement("a");
      a.textContent = String(text || "")
  .replace(/[??]/g, "")
  .replace(/\s+/g, " ")
  .trim();

      a.href = href;
      if (!href.startsWith("#")) { a.target = "_blank"; a.rel = "noopener"; }
      a.style.textDecoration = "underline";
      span.parentNode.replaceChild(a, span);
    } else {
      span.style.textDecoration = "underline";
    }
  });

  return root.innerHTML;
}

function exportablePlainText(){
  if (!viewerEl) return "";
  const root = viewerEl.cloneNode(true);

  // unwrap marks
  root.querySelectorAll("mark.kwd, mark.kwd-int, mark.kwd-ext, mark.kwd-sem").forEach(m => {
    const core = m.querySelector?.(".kw-core");
    const t = document.createTextNode((core?.textContent ?? m.textContent) || "");
    m.parentNode.replaceChild(t, m);
  });

  // turn accepted underlines into "text (url)"
  root.querySelectorAll("span.lc-underlined").forEach(span => {
    const text = span.textContent || "";
    const href = resolveUrlForSpan(span);
    const repl = document.createTextNode(href ? `${text} (${href})` : text);
    span.parentNode.replaceChild(repl, span);
  });

  // basic HTML?text layout
  let html = root.innerHTML;
  html = html.replace(/<br\s*\/?>/gi, "\n")
             .replace(/<\/p>\s*<p>/gi, "\n\n")
             .replace(/<\/?p>/gi, "");

  const div = document.createElement("div");
  div.innerHTML = html;
  return div.textContent || "";
}
// === END: export helpers for HTML/TXT ===

// Computes a final URL given what we know at apply time (so exports are clickable)
function computeFinalUrl(kind, topicId, title, url){
  if (url && url.trim()) return url.trim();
  const t = (title||"").trim();

  if (kind === "same-doc") {
    const slug = slugifyHeading(t);
    return "#" + slug;
  }

  if (kind === "published") {
    for (const [,v] of PUBLISHED_TOPICS.entries()){
      if ((topicId && v.id === topicId) || norm(v.title) === norm(t)) {
        if (v.url) return v.url;
      }
    }
    const rec = TITLE_INDEX.get(norm(t));
    if (rec?.url) return rec.url;

    const urls = Array.from(IMPORTED_URLS || []);
    const guess = bestUrlForTitle(t, urls, 0.70);
    if (guess) return guess;
  }

  if (kind === "draft") {
    for (const [,v] of DRAFT_TOPICS.entries()){
      if ((topicId && v.id === topicId) || norm(v.working_title) === norm(t)) {
        if (v.planned_url) return v.planned_url;
      }
    }
  }

  return "";
}

async function uploadFile(file){
  return await apiUploadFile(file);
}

// Fetch scraped content for a batch of sitemap URLs
async function fetchSitemapContent(urls) {
  if (!Array.isArray(urls) || urls.length === 0) return [];

  try {
    const res = await fetch(`${API_BASE}/sitemap/fetch-content`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ urls })
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      console.error("[sitemap] fetch-content failed:", res.status, errText);
      showToast(errorBox, `Sitemap content fetch failed (${res.status}).`, 2000);
      return [];
    }

    const data = await res.json();
    // Expected format: { items: [ { url, title, content, status }, ... ] }
    if (DEBUG) console.log("[sitemap] fetched content:", data);

    return Array.isArray(data.items) ? data.items : [];
  } catch (err) {
    console.error("[sitemap] fetch-content error:", err);
    showToast(errorBox, "Sitemap content fetch: network error.", 2000);
    return [];
  }
}


async function downloadDocx() {
  if (currentIndex < 0 || !docs[currentIndex]) {
    safeSetText(errorBox, "Nothing to download yet � upload a document first.", "error");
    return;
  }
  const d = docs[currentIndex];
  const body = exportableInnerHTML();
  const blob = await apiExportDocx(d.filename, body);

  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  const base = (d.filename || "document").replace(/\.[^\.\s]+$/, "");
  a.download = `${base}.docx`;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
}

function downloadHTML(ext = "html") {
  if (currentIndex < 0 || !docs[currentIndex]) {
    safeSetText(errorBox, "Nothing to download yet � upload a document first.", "error");
    return;
  }
  const d = docs[currentIndex];
  const base = (d.filename || "document").replace(/\.[^\.\s]+$/, "");
  const filename = `${base}.${ext}`;

  const body = exportableInnerHTML();
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>${base}</title></head><body>${body}</body></html>`;
  const blob = new Blob([html], { type: "text/html;charset=utf-8" });

  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
}

function downloadText(ext = "txt") {
  if (currentIndex < 0 || !docs[currentIndex]) {
    safeSetText(errorBox, "Nothing to download yet � upload a document first.", "error");
    return;
  }
  const d = docs[currentIndex];
  const base = (d.filename || "document").replace(/\.[^\.\s]+$/, "");
  const filename = `${base}.${ext}`;

  const content = exportablePlainText();
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });

  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
}

async function downloadOriginal() {
  if (currentIndex < 0 || !docs[currentIndex]) {
    safeSetText(errorBox, "Nothing to download yet � upload a document first.", "error");
    return;
  }
  const d = docs[currentIndex];
  const url = downloadOriginalUrl(d.filename);

  const a = document.createElement("a");
  a.href = url;
  a.download = d.filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

/* Manifest builder */
function buildManifest(){
  const manifest = [];
  if (!viewerEl) return manifest;

  const spans = viewerEl.querySelectorAll(".lc-underlined, mark.kwd");
  spans.forEach(el=>{
    const coreNode = el.querySelector?.(".kw-core");
    const coreText = (coreNode?.textContent || el.textContent || "").trim();
    const phrase = decodeURIComponent(el.getAttribute("data-phrase")||"").trim() || coreText;
    const topicId = el.getAttribute("data-topic-id") || "";
    const kind = el.getAttribute("data-kind") || "";
    const url = el.getAttribute("data-url") || "";
    const title = el.getAttribute("data-title") || "";
    if (!phrase) return;

    let rec = APPLIED_LINKS.find(x=> norm(x.phrase)===norm(phrase));
    if (!rec){ rec = { phrase, topicId, url, title, kind }; }
    manifest.push({
      phrase: rec.phrase || phrase,
      topic_id: rec.topicId || topicId || "",
      final_url: rec.url || url || "",
      title: rec.title || title || "",
      kind: rec.kind || kind || (rec.topicId?.startsWith("d:") ? "draft" : rec.topicId?.startsWith("p:") ? "published" : "same-doc"),
      status: (rec.url || url) ? "published" : (rec.topicId ? "draft" : "unknown")
    });
  });

  const uniqMap = new Map();
  for (const m of manifest){
    const key = `${norm(m.phrase)}|${m.topic_id}|${m.final_url}`;
    if (!uniqMap.has(key)) uniqMap.set(key, m);
  }
  return Array.from(uniqMap.values());
}
async function downloadManifestJSON(){
  const d=docs[currentIndex];
  const base=(d?.filename||"document").replace(/\.[^\.\s]+$/,"");
  const payload = { doc: { filename: d?.filename||"", code: d?.docCode||"", phase: PHASE }, links: buildManifest() };
  const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json;charset=utf-8"});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob); a.download=`${base}_link_manifest.json`;
  document.body.appendChild(a); a.click(); setTimeout(()=>{ URL.revokeObjectURL(a.href); a.remove(); },0);
}

/* ============================
   External engine helpers (glue)
   ============================ */
const EXTERNAL_DEFAULTS = Object.freeze({
  MODE: "balanced",
  EXTERNAL: {
    DOMAIN_TIERS: {
      "who.int":1, "cdc.gov":1, "nih.gov":1, "ncbi.nlm.nih.gov":1,
      "medlineplus.gov":1, "cochranelibrary.com":1, "ema.europa.eu":1,
      "fda.gov":1, "nice.org.uk":1, "bmj.com":2, "nature.com":2,
      "sciencedirect.com":2, "wikipedia.org":3
    },
    WHITELIST: [],
    BLACKLIST: [],
    ENFORCE_YMYL_GATE: true,
    YMYL_TOPICS: ["medical"],
    MAX_STOPWORD_RATIO: 0.40,
    MIN_ANCHOR_TOKENS: 3,
    MAX_ANCHOR_TOKENS: 16,
    FRESHNESS_YEARS: { default: 5, ymyl: 5 },
    PER_PARAGRAPH_CAP: 1,
  },
});
function getExternalSettings() {
  try {
    const s = loadSettingsFromStore?.() || {};
    return { ...EXTERNAL_DEFAULTS, ...s, EXTERNAL: { ...EXTERNAL_DEFAULTS.EXTERNAL, ...(s?.EXTERNAL||{}) } };
  } catch {
    return EXTERNAL_DEFAULTS;
  }
}
function domainRootOf(host) {
  const h = String(host||"").toLowerCase();
  const parts = h.split(".").filter(Boolean);
  return parts.length <= 2 ? h : parts.slice(-2).join(".");
}
async function searchProvidersShim({ anchor, context, limit = 6 }) {
  const api = await ensureReferencesModule();
  if (!api?.getExternalReferences) return [];
  try {
    const list = await api.getExternalReferences(anchor, { context, limit });
    return (list||[]).map(r => {
      const url = r.url || r.link || "";
      let domain = r.domain || "";
      try { if (!domain && url) domain = new URL(url).hostname; } catch {}
      return {
        title: r.title || r.name || domain || anchor,
        url,
        domain,
        abstract: r.snippet || r.abstract || "",
        pubYear: r.year || r.pubYear || null,
        topicalScore: typeof r.score === "number" ? r.score
                     : (typeof r.topicalScore === "number" ? r.topicalScore : 0.7),
      };
    });
  } catch {
    return [];
  }
}
function internalSimilarityShim(anchor) {
  const anchorTok = tokensNL(anchor);
  const headings = viewerEl ? ensureHeadingIds(viewerEl) : [];
  const topics = [
    ...topicsFromHeadings(headings),
    ...topicsFromOtherDocsH1(),
    ...topicsFromPublished(),
    ...topicsFromDraft(),
  ];
  let best = 0;
  for (const t of topics) {
    const v = tokensNL(t.title || "");
    const ov = tokenOverlapRatio(anchorTok, v);
    if (ov > best) best = ov;
  }
  return clamp01(best);
}
function isCompetitorDomainShim(domain) {
  try {
    const s = getExternalSettings();
    const root = domainRootOf(domain);
    const comps = new Set(s?.EXTERNAL?.COMPETITORS || []);
    return comps.has(root);
  } catch { return false; }
}
function buildReservedSpansFromMarks(plainText) {
  const spans = [];
  const used = new Set();
  const marks = viewerEl
    ? Array.from(viewerEl.querySelectorAll("mark.kwd:not(.kwd-external), .lc-underlined"))
    : [];
  for (const el of marks) {
    const core = el.querySelector?.(".kw-core");
    const phrase = decodeURIComponent(el.getAttribute("data-phrase")||"").trim()
                || (core?.textContent || el.textContent || "").trim();
    if (!phrase) continue;
    const rx = new RegExp(`(^|[^\\p{L}\\p{N}])(${escRe(phrase).replace(/\s+/g,"\\s+")})(?=$|[^\\p{L}\\p{N}])`, "u");
    const m = rx.exec(plainText);
    if (!m) continue;
    const start = m.index + (m[1] ? m[1].length : 0);
    const end = start + (m[2] || "").length;
    const key = `${start}-${end}`;
    if (!used.has(key)) { used.add(key); spans.push({ start, end }); }
  }
  return spans;
}
function fillExternalReferencesFromMark(markEl) {
  const extReferences = $("extReferences");
  if (!extReferences) return;
  extReferences.innerHTML = "";
  let list = [];
  try {
    const raw = markEl?.getAttribute("data-suggestions") || "[]";
    list = JSON.parse(raw);
  } catch { list = []; }

  if (!Array.isArray(list) || !list.length) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "No suggestions available";
    extReferences.appendChild(opt);
    return;
  }

  for (const r of list) {
    const opt = document.createElement("option");
    opt.value = r.url || "";
    opt.textContent = r.title ? `${r.title} � ${r.domainRoot || r.domain || ""}` : (r.url || "");
    opt.dataset.title = r.title || "";
    opt.dataset.provider = r.domainRoot || r.domain || "";
    extReferences.appendChild(opt);
  }
}

// ==========================================================================
// HEADING CLEANUP � remove any marks from H1�H6 *and* heading-like <p> tags
// ==========================================================================
function cleanupMarksInHeadings(root) {
  if (!root) return;

  const MARK_SELECTOR =
    "mark.kwd, mark.kwd-strong, mark.kwd-optional," +
    " mark.kwd-external, mark.kwd-int, mark.kwd-sem, mark.kwd-ext";

  // -------------------------------------------------
  // A) Real heading tags: <h1>�<h6>
  // -------------------------------------------------
  const headings = root.querySelectorAll("h1, h2, h3, h4, h5, h6");
  headings.forEach(h => {
    const marks = h.querySelectorAll(MARK_SELECTOR);
    marks.forEach(mark => {
      const core = mark.querySelector?.(".kw-core");
      const text = (core?.textContent || mark.textContent || "") || "";
      mark.replaceWith(document.createTextNode(text));
    });
  });

  // -------------------------------------------------
  // B) Mark WRAPPING a heading:
  //    <mark class="kwd-�"><h1>Heading</h1></mark>
  // -------------------------------------------------
  const allMarks = root.querySelectorAll(MARK_SELECTOR);
  allMarks.forEach(mark => {
    const child = mark.firstElementChild;
    if (child && /^H[1-6]$/.test(child.tagName.toUpperCase())) {
      mark.replaceWith(child);
    }
  });

  // -------------------------------------------------
  // C) "Heading-like" paragraphs (your exact case):
  //    <p><strong><span><mark �><span class="kw-core">Heading</span>�</mark></span></strong></p>
  //    We treat short, mostly-bold <p> as headings and remove marks inside.
  // -------------------------------------------------
  const paras = root.querySelectorAll("p");
  paras.forEach(p => {
    const pText = (p.textContent || "").trim();
    if (!pText) return;

    // Very long paragraphs are probably body text, not headings
    if (pText.length > 140) return;

    // Require that most of the text is inside <strong> / <b>
    const strongNodes = p.querySelectorAll("strong, b");
    if (!strongNodes.length) return;

    const strongText = Array.from(strongNodes)
      .map(n => n.textContent || "")
      .join(" ")
      .trim();
    if (!strongText) return;

    // If less than 70% of the paragraph text is bold, skip
    if (strongText.length / pText.length < 0.7) return;

    // At this point, we treat this <p> as a "heading-like" line.
    // Remove all engine marks inside it (but keep the text).
    const marks = p.querySelectorAll(MARK_SELECTOR);
    marks.forEach(mark => {
      const core = mark.querySelector?.(".kw-core");
      const text = (core?.textContent || mark.textContent || "") || "";
      mark.replaceWith(document.createTextNode(text));
    });
  });
}


/* ==========================================================================
   PIPELINE (invoke engine) � internal + External V2 local
   ========================================================================== */
async function runPipelineAndHighlight(opts = {}) {

  if (!viewerEl) return 0;

  const append        = opts.append !== false;
const perPassLimit  = opts.perPassLimit || MAX_UNIQUE_PHRASES;
const silent        = !!opts.silent;


const wsId = getCurrentWorkspaceId("default");
const docId =
  window.LC_ACTIVE_DOC_ID ||
  docs?.[currentIndex]?.doc_id ||
  docs?.[currentIndex]?.docId ||
  null;

const rootEl =
  viewerEl.querySelector(".doc-root") ||
  viewerEl.querySelector("[contenteditable='true']") ||
  viewerEl.querySelector(".editor") ||
  viewerEl;

console.log("[RB2 ROOTEL TAG]", rootEl?.tagName || null);
console.log("[RB2 ROOTEL CLASS]", rootEl?.className || "");
console.log("[RB2 ROOTEL TEXTLEN]", (rootEl?.textContent || "").trim().length);
console.log("[RB2 ROOTEL HTMLLEN]", (rootEl?.innerHTML || "").trim().length);


let html = (rootEl?.innerHTML || "").trim();
let text = (rootEl?.textContent || "").replace(/\u00A0/g, " ").trim();

if (!/<p[\s>]/i.test(html) && text) {
  const paras = text.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
  html = paras.map(p => `<p>${escapeHtml(p).replace(/\n/g, "<br>")}</p>`).join("");
}

const payload = {
  workspaceId: wsId,
  docId,
  phase: (window.PHASE || "publish"),
  html,
  text
};

console.log("[PIPELINE] calling RB2 apiEngineRun now ?", {
  workspaceId: wsId,
  docId,
  highlightEnabled,
  hasHtml: !!(payload?.html && String(payload.html).trim()),
  hasText: !!(payload?.text && String(payload.text).trim())
});

const out = await apiEngineRun(payload);


console.log("[RB2 OUT COUNTS @PAINT]", {
  strong_backend: (out?.internal_strong || []).length,
  optional_backend: (out?.semantic_optional || []).length,
  meta: out?.meta || {}
});

/* ============================
   INTERNAL HIGHLIGHTS (RB2)
   ============================ */

// ?? CLEAR OLD BUCKET MARKS ONCE
unwrapBucketMarksOnly();

// ?? STRONG (blue)
const strongOnly = (out.recommended || []).map(s => ({
  ...s,
  bucket: "strong"
}));


console.log("[PAINT INPUT STRONG COUNT]", strongOnly.length);
const appliedStrong = highlightEnabled
  ? applyMarksFromSuggestions(strongOnly, {
      container: rootEl,
      append: false,
      perPassLimit
    })
  : 0;



// ?? OPTIONAL (yellow) � MUST be painted explicitly
const optionalOnly = (out.optional || []).map(s => ({
  ...s,
  bucket: "optional"
}));


console.log("[PAINT INPUT OPTIONAL COUNT]", optionalOnly.length);
const appliedOptional = highlightEnabled
  ? applyMarksFromSuggestions(optionalOnly, {
      container: rootEl,
      append: true,
      perPassLimit
    })
  : 0;

console.log("[HIGHLIGHT APPLIED COUNTS]", {
  strong: Number(appliedStrong || 0),
  optional: Number(appliedOptional || 0)
});

console.log(
  "[DOM MARK COUNT AFTER PAINT]",
  rootEl.querySelectorAll(".kwd").length
);


console.log(
  "[PAINTED PHRASES]",
  Array.from(rootEl.querySelectorAll("mark.kwd")).map(m =>
    decodeURIComponent(m.getAttribute("data-phrase") || "").trim() ||
    (m.textContent || "").trim()
  )
);

// ?? COMBINED INTERNAL POOL (for external + audit)
const internalPool = [...strongOnly, ...optionalOnly];


/* ============================
   POST-PROCESSING
   ============================ */

cleanupMarksInHeadings(rootEl);
underlineLinkedPhrases();
// highlightBucketKeywords();   // ? DISABLE HERE ONLY
updateHighlightBadge();
rebuildEngineHighlightsPanel();


try { window.__LC_REFRESH_AUDIT_CARD__?.(); } catch {}

const added = appliedStrong + appliedOptional;

console.log("[HIGHLIGHT RESULT]", {
  strong_backend: (out?.recommended || []).length,
  optional_backend: (out?.optional || []).length,
  appliedStrong: Number(appliedStrong || 0),
  appliedOptional: Number(appliedOptional || 0),
  appliedExternal: 0
});

return added;
}


/** Apply All (this doc) */
async function applyAllThisDoc(){
  if (applyingAll) return;
  applyingAll = true;
  highlightsArmed = true;

  let passes = 0;
  let prevMarks = getEngineMarkCount();
  const startMarks = prevMarks;

  try {
    while (passes < APPLY_ALL_PASS_LIMIT && getEngineMarkCount() < MAX_TOTAL_HIGHLIGHTS){
      const added = await runPipelineAndHighlight({ append: true, silent: true });
      const nowMarks = getEngineMarkCount();
      const gained = Math.max(0, nowMarks - prevMarks);
      if (!added && gained === 0) break;
      passes += 1;
      prevMarks = nowMarks;
      await delay(30);
    }
  } finally {
    showToast(errorBox, `Apply All (this doc) � added ${Math.max(0, getEngineMarkCount() - startMarks)} highlight(s) in ${passes} pass(es).`, 2200);
    applyingAll = false;
    updateHighlightBadge();
    rebuildEngineHighlightsPanel();
    rebuildRejectionsPanel();
  }
}

async function applyAllAcrossDocs() {
  if (applyingAll) return;
  applyingAll = true;
  highlightsArmed = true;

  const savedIndex = currentIndex;
  let totalAdded = 0;

  try {
    for (let i = 0; i < docs.length; i++) {
      // Load doc i into the viewer
      renderDoc(i);

      let passes = 0;
      let before = getEngineMarkCount();

      while (
        passes < APPLY_ALL_PASS_LIMIT &&
        getEngineMarkCount() < MAX_TOTAL_HIGHLIGHTS
      ) {
        const added = await runPipelineAndHighlight({
          append: true,
          silent: true
        });

        const after  = getEngineMarkCount();
        const gained = Math.max(0, after - before);

        if (!added && gained === 0) break;

        totalAdded += (added || gained);
        passes += 1;
        before = after;
        await delay(20);
      }

      // ? NEW: persist highlights back into docs[i]
      if (viewerEl && docs[i]) {
        docs[i].html = viewerEl.innerHTML;
        docs[i].text = viewerEl.textContent || docs[i].text || "";
      }
    }

    // Save full session with updated docs[]
    saveState();
  } finally {
    // Restore whichever doc was active
    if (savedIndex >= 0 && savedIndex < docs.length) {
      renderDoc(savedIndex);
    }

    applyingAll = false;
    showToast(
      errorBox,
      `Apply All (all docs) � total added ${totalAdded}.`,
      2300
    );
    updateHighlightBadge();
    rebuildEngineHighlightsPanel();
    rebuildRejectionsPanel();
  }
}


// ---------------------------------------------------------------------------
// Bulk apply helpers (current doc)
// ---------------------------------------------------------------------------
function rememberAppliedLink(phrase, topicId, url, title, kind) {
  const pNorm = norm(phrase);
  const key = `${pNorm}|${topicId || ""}|${url || ""}`;

  // Ensure globals exist
  if (!window.LINKED_SET) window.LINKED_SET = new Set();
  if (!window.LINKED_MAP) window.LINKED_MAP = new Map();
  if (!Array.isArray(window.APPLIED_LINKS)) window.APPLIED_LINKS = [];

  LINKED_SET.add(pNorm);
  LINKED_MAP.set(pNorm, { phrase, topicId, url, title, kind });

  if (!rememberAppliedLink._seen) rememberAppliedLink._seen = new Set();
  if (!rememberAppliedLink._seen.has(key)) {
    rememberAppliedLink._seen.add(key);
    APPLIED_LINKS.push({ phrase, topicId, url, title, kind });
  }
}

/**
 * Auto-apply all engine suggestions in the CURRENT doc.
 * Includes strong, optional, and external suggestions.
 */
function autoApplyMarksInCurrentDoc() {
  if (!viewerEl) return 0;

  // Select ALL engine marks, including external
  const marks = Array.from(
    viewerEl.querySelectorAll("mark.kwd, mark.kwd-int, mark.kwd-ext, mark.kwd-sem")
  );
  if (!marks.length) return 0;

  let applied = 0;

  for (const m of marks) {
    const coreNode = m.querySelector?.(".kw-core");
    const phrase =
      decodeURIComponent(m.getAttribute("data-phrase") || "").trim() ||
      (coreNode?.textContent || m.textContent || "").trim();
    if (!phrase) continue;

    const topicId = m.getAttribute("data-topic-id") || "";
    const kindAttr = (m.getAttribute("data-kind") || "").toLowerCase();
    const kind =
      kindAttr ||
      (topicId?.startsWith("d:") ? "draft" :
       topicId?.startsWith("p:") ? "published" :
       "same-doc");

    const title = (m.getAttribute("data-title") || coreNode?.textContent || phrase).trim();
    const rawUrl = m.getAttribute("data-url") || "";
    const finalUrl = computeFinalUrl(kind, topicId, title, rawUrl);

    // Save this as an applied link
    rememberAppliedLink(phrase, topicId, finalUrl, title, kind);
    applied++;
  }

  // Remove engine marks and redraw underlines from LINKED_SET
  unwrapMarks();
  underlineLinkedPhrases();
  highlightBucketKeywords();
  updateHighlightBadge();
  rebuildEngineHighlightsPanel();

  try { rebuildLinkedPhrasesList?.(); } catch {}
  try { LR_rebuild?.(); } catch {}

  saveLinkedSet();

  return applied;
}


/* ==========================================================================
   RESET LINKED PHRASES
   ========================================================================== */
const btnResetLinked = $("btnResetLinked");
const resetLinkedToast = $("resetLinkedToast");
btnResetLinked?.addEventListener("click", () => {
  LINKED_SET = new Set();
  LINKED_MAP = new Map();
  APPLIED_LINKS = [];
  saveLinkedSet();
  window.REJECTED_SET = new Set();
  saveRejectedSet();

  if (viewerEl) {
    const uds = Array.from(viewerEl.querySelectorAll(".lc-underlined"));
    for (const u of uds) {
      const tx = u.textContent || "";
      u.parentNode.replaceChild(document.createTextNode(tx), u);
    }
    viewerEl
      .querySelectorAll("mark.kwd, mark.kwd-int, mark.kwd-ext, mark.kwd-sem")
      .forEach(m => {
        const core = m.querySelector?.(".kw-core");
        const t = document.createTextNode((core?.textContent ?? m.textContent) || "");
        m.parentNode.replaceChild(t, m);
      });
  }

  highlightsArmed = false;
  updateHighlightBadge();
  rebuildEngineHighlightsPanel();
  underlineLinkedPhrases();
  highlightBucketKeywords();
  updateHighlightBadge();
  rebuildEngineHighlightsPanel();

  if (resetLinkedToast) {
    resetLinkedToast.textContent = "Linked & rejected phrases cleared";
    setTimeout(() => (resetLinkedToast.textContent = ""), 1200);
  }
});


/* ==========================================================================
   Suggestion picker (for IL modal)
   Uses LAST_ENGINE_OUTPUT only � stable and simple.
   ========================================================================== */
function findEngineSuggestionsForPhrase(phrase) {
  const norm = (s) => String(s || "").toLowerCase().trim().replace(/\s+/g, " ");
  const normp = norm(phrase);

  const pool = [
    ...(LAST_ENGINE_OUTPUT?.recommended || []),
    ...(LAST_ENGINE_OUTPUT?.optional || [])
  ];

  const hits = pool
    .filter(x => norm(x.anchor?.text || "") === normp)
    .map(x => ({
      title:   x.target?.title || "",
      url:     x.target?.url || "",
      topicId: x.target?.topicId || x.target?.id || "",
      kind:    x.target?.kind || x.kind || (x.target?.isExternal ? "external" : "internal"),
      tier:    x.bucket === "strong" ? "high" : "mid",
      score:   typeof x.finalScore === "number" ? x.finalScore : 0
    }));

  const uniqHits = [];
  const seen = new Set();

  for (const h of hits) {
    const k = `${h.title}|${h.url}|${h.topicId}`;
    if (seen.has(k)) continue;
    seen.add(k);
    uniqHits.push(h);
  }

  // Sort: high tier first, then by score, then alphabetically by title
  uniqHits.sort((a, b) =>
    (a.tier === b.tier ? 0 : (a.tier === "high" ? -1 : 1)) ||
    (b.score - a.score) ||
    a.title.localeCompare(b.title)
  );

  return uniqHits;
}

/**
 * Build PhraseContext for scoring.
 * This now wires in:
 *  - basic pseudo-entities from the phrase text
 *  - a simple contextType based on the phrase content
 *  - optional hook LC_getPhraseContext() if you later want deeper Entity Map/Graph.
 */
function buildPhraseContext(phraseText) {
  const ctx = {
    phraseText: phraseText || "",
    contextText: "",
    docId: window.LC_ACTIVE_DOC_ID || null,
    sectionId: null,
    position: null,
    entities: [],
    graphVector: null,
    contextType: null
  };

  // Optional hook � if you later define window.LC_getPhraseContext,
  // it can enrich this context (entities, graphVector, contextType, etc.)
  if (typeof window.LC_getPhraseContext === "function") {
    try {
      const extra = window.LC_getPhraseContext(phraseText) || {};
      Object.assign(ctx, extra || {});
    } catch (e) {
      console.warn("LC_getPhraseContext error", e);
    }
  }

  const norm = (s) => String(s || "").toLowerCase().trim().replace(/\s+/g, " ");

  // --- Fallback: inject a pseudo-entity based on the phrase text ---
  // This lets the scoring engine use entityScore/graphScore even
  // before the full Entity Map is plugged in.
  if (!Array.isArray(ctx.entities) || !ctx.entities.length) {
    const key = norm(ctx.phraseText);
    if (key) {
      ctx.entities = [
        {
          id: key,      // canonical id based on phrase text
          type: "TOPIC" // generic topic entity
        }
      ];
    } else {
      ctx.entities = [];
    }
  }

  // --- Fallback: simple contextType heuristics from phrase text ---
  if (!ctx.contextType) {
    const t = norm(ctx.phraseText);
    if (/(side effect|adverse|reaction|tolerability)/.test(t)) {
      ctx.contextType = "SIDE_EFFECTS";
    } else if (/(treat|treatment|manage|management|therapy)/.test(t)) {
      ctx.contextType = "TREATMENT";
    } else if (/(what is|overview|summary|introduction)/.test(t)) {
      ctx.contextType = "OVERVIEW";
    } else {
      ctx.contextType = "GENERAL"; // not in CONTEXT_TOPIC_COMPAT, but safe default
    }
  }

  // graphVector stays null for now; scoring will fall back to entityScore * 0.7

  return ctx;
}


// Small helper: extract domain from URL for external authority scoring
function tryExtractDomain(rawUrl) {
  if (!rawUrl) return "";
  try {
    const u = new URL(rawUrl);
    return u.hostname.replace(/^www\./, "").toLowerCase();
  } catch (e) {
    return "";
  }
}


/**
 * Collect CandidateTarget[] for this phrase.
 *
 * 1) If LC_collectCandidatesForPhrase exists, let it drive everything
 *    (future: Entity Map, Entity Graph, uploaded docs, etc.).
 * 2) Otherwise, merge imported topics + engine output (LAST_ENGINE_OUTPUT),
 *    and enrich with pseudo-entities + topicTypes for semantic scoring.
 */
function collectCandidatesForPhrase(phraseCtx) {
  const candidates = [];
  const seen = new Set();

  const norm = (s) => String(s || "").toLowerCase().trim().replace(/\s+/g, " ");
  const phraseKey = norm(phraseCtx?.phraseText || "");

  function guessTopicTypesFromTitle(title) {
    const t = norm(title);
    const types = [];

    if (/(side effect|adverse|reaction|tolerability)/.test(t)) {
      types.push("SIDE_EFFECTS");
    }
    if (/(treat|treatment|manage|management|therapy)/.test(t)) {
      types.push("TREATMENT");
    }
    if (/(what is|overview|introduction|guide|summary)/.test(t)) {
      types.push("OVERVIEW");
    }
    if (!types.length) {
      types.push("GENERAL");
    }
    return types;
  }

  function ensureEntitiesAndTypes(c) {
    // Entities: if none, create a pseudo entity based on title/url
    if (!Array.isArray(c.entities) || !c.entities.length) {
      const key =
        norm(c.title || "") ||
        norm(c.url || "") ||
        phraseKey;
      if (key) {
        c.entities = [{ id: key, type: "TOPIC" }];
      } else {
        c.entities = [];
      }
    }

    // Topic types: if none, guess from title
    if (!Array.isArray(c.topicTypes) || !c.topicTypes.length) {
      c.topicTypes = guessTopicTypesFromTitle(c.title || "");
    }
  }

  function addCandidate(raw) {
    if (!raw) return;

    const title = raw.title || "";
    const url   = raw.url   || "";
    const docId = raw.docId || null;

    const key = `${norm(title)}|${String(url).trim()}|${docId || ""}`;
    if (seen.has(key)) return;
    seen.add(key);

    const sourceType = raw.sourceType || raw.source || "uploaded";
    const isExternal = !!raw.isExternal;

    const cand = {
      id: raw.id || raw.topicId || `cand-${candidates.length + 1}`,
      title,
      url,
      docId,
      sectionId: raw.sectionId || null,
      sourceType,
      isExternal,
      entities: raw.entities || [],
      topicTypes: raw.topicTypes || [],
      graphVector: raw.graphVector || null,
      domain: raw.domain || (url ? tryExtractDomain(url) : ""),
      isCanonicalTopic: !!raw.isCanonicalTopic
    };

    ensureEntitiesAndTypes(cand);
    candidates.push(cand);
  }

  // 1) Full custom collector hook (future: Entity Map + Graph, etc.)
  if (typeof window.LC_collectCandidatesForPhrase === "function") {
    try {
      const out = window.LC_collectCandidatesForPhrase(phraseCtx) || [];
      if (Array.isArray(out)) {
        out.forEach(addCandidate);
        return candidates;
      }
    } catch (e) {
      console.warn("LC_collectCandidatesForPhrase error", e);
    }
  }

  // 2) Imported topics (sitemap / backup / draft / external lists)
  let imported = [];
  if (typeof window.LC_getImportedTopics === "function") {
    try {
      imported = window.LC_getImportedTopics() || [];
    } catch (e) {
      console.warn("LC_getImportedTopics error", e);
    }
  }
  if (!Array.isArray(imported)) imported = [];

  imported.forEach((rec, index) => {
    if (!rec) return;

    const sourceType = rec.source || "uploaded";
    const isExternal = sourceType === "external";

    addCandidate({
      id: rec.id || `imp-${sourceType}-${index}`,
      title: rec.title || "",
      url: rec.url || "",
      docId: rec.docId || null,
      sectionId: rec.sectionId || null,
      sourceType,
      isExternal,
      entities: rec.entities || [],
      topicTypes: rec.topicTypes || [],
      graphVector: rec.graphVector || null,
      domain: rec.domain || (rec.url ? tryExtractDomain(rec.url) : ""),
      // heuristic: sitemap URLs are usually pillar/canonical pages
      isCanonicalTopic: !!rec.isCanonicalTopic || sourceType === "sitemap"
    });
  });

  // 3) Engine output (recommended + optional) as additional candidates
  const pool = [
    ...(window.LAST_ENGINE_OUTPUT?.recommended || []),
    ...(window.LAST_ENGINE_OUTPUT?.optional || [])
  ];

  pool.forEach((item, index) => {
    const target = item?.target || {};
    const kind   = String(target.kind || "").toLowerCase();
    const isExternal = kind === "external";

    addCandidate({
      id: target.topicId || target.id || `eng-${index}`,
      title: target.title || "",
      url: target.url || "",
      docId: target.docId || null,
      sectionId: item.sectionId || target.sectionId || null,
      sourceType: target.kind || "engine",
      isExternal,
      entities: target.entities || [],
      topicTypes: target.topicTypes || [],
      graphVector: target.graphVector || null,
      domain: target.domain || (target.url ? tryExtractDomain(target.url) : ""),
      isCanonicalTopic: !!target.isCanonicalTopic
    });
  });

  return candidates;
}


/* ==========================================================================
   STOPWORDS + UI hooks
   ========================================================================== */
applyStopwords();
initStopwordsUI();
window.addEventListener("lc:stopwords-updated", () => {
  applyStopwords();
  if (highlightsArmed) runPipelineAndHighlight({ append: true });
});

/* ==========================================================================
   RICH PREVIEW HELPERS (HTML/MD/TXT)
   ========================================================================== */
function sanitizeHtml(html) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(String(html || ""), "text/html");
  doc.querySelectorAll("script, iframe, object, embed, meta[http-equiv='refresh']").forEach(n => n.remove());
  const all = doc.body.querySelectorAll("*");
  all.forEach(el => {
    for (const attr of Array.from(el.attributes)) {
      const n = attr.name.toLowerCase();
      const v = (attr.value || "").trim().toLowerCase();
      if (n.startsWith("on")) el.removeAttribute(attr.name);
      if ((n === "href" || n === "src") && v.startsWith("javascript:")) el.removeAttribute(attr.name);
    }
    if (el.tagName === "IMG") el.setAttribute("style", (el.getAttribute("style") || "") + ";max-width:100%;height:auto;");
    if (el.tagName === "TABLE") el.setAttribute("style", (el.getAttribute("style") || "") + ";border-collapse:collapse;max-width:100%;");
  });
  return doc.body.innerHTML || "";
}
function extractBodyAndStyles(html) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(String(html || ""), "text/html");
  const bodyHTML = doc.body ? doc.body.innerHTML : html;
  const styles = [];
  doc.querySelectorAll("style").forEach(s => styles.push(s.textContent || ""));
  return { bodyHTML, styleText: styles.join("\n") };
}
function prefixCss(cssText, scope = "#doc-content .doc-root") {
  try {
    return (cssText || "").split("}").map(block => {
      const i = block.indexOf("{");
      if (i === -1) return block;
      const sel = block.slice(0, i).trim();
      const body = block.slice(i + 1);
      if (!sel || sel.startsWith("@")) return `${sel}{${body}}`;
      const scoped = sel.split(",").map(s => `${scope} ${s.trim()}`).join(", ");
      return `${scoped}{${body}}`;
    }).join("}");
  } catch {
    return cssText || "";
  }
}
function renderFromHTML(html, inlineStyles = "") {
  if (!viewerEl) return;
  const scopedId = "doc-inline-style";
  document.getElementById(scopedId)?.remove();
  if (inlineStyles && inlineStyles.trim()) {
    const tag = document.createElement("style");
    tag.id = scopedId;
    tag.textContent = prefixCss(inlineStyles, "#doc-content .doc-root");
    document.head.appendChild(tag);
  }
  const clean = sanitizeHtml(html);
  viewerEl.innerHTML = `<div class="doc-root">${clean}</div>`;
}
function mdToHtmlLite(md) {
  let text = String(md || "");
  text = text.replace(/```([\s\S]*?)```/g, (_, code) => `<pre><code>${escapeHtml(code)}</code></pre>`);
  text = text.replace(/`([^`]+?)`/g, (_, c) => `<code>${escapeHtml(c)}</code>`);
  text = text.replace(/!\[([^\]]*?)\]\(([^)]+?)\)/g, (_, alt, url) => `<img alt="${escapeHtml(alt)}" src="${escapeAttr(url)}" style="max-width:100%;height:auto;" />`);
  text = text.replace(/\[([^\]]+?)\]\(([^)]+?)\)/g, (_, t, url) => `<a href="${escapeAttr(url)}" target="_blank" rel="noopener">${escapeHtml(t)}</a>`);
  text = text.replace(/^######\s+(.+)$/gm, "<h6>$1</h6>")
             .replace(/^#####\s+(.+)$/gm, "<h5>$1</h5>")
             .replace(/^####\s+(.+)$/gm, "<h4>$1</h4>")
             .replace(/^###\s+(.+)$/gm, "<h3>$1</h3>")
             .replace(/^##\s+(.+)$/gm, "<h2>$1</h2>")
             .replace(/^#\s+(.+)$/gm, "<h1>$1</h1>");
  text = text.replace(/^\s*>\s?(.*)$/gm, "<blockquote>$1</blockquote>");
  text = text.replace(
    /(^|\n)(\|.+\|)\n(\|[ \-:\|\t]+)\n((?:\|.*\|\n?)+)/g,
    (_, pfx, header, sep, body) => {
      const th = header.split("|").slice(1, -1).map(h => `<th>${h.trim()}</th>`).join("");
      const rows = body.trim().split("\n").map(r => {
        const tds = r.split("|").slice(1, -1).map(c => `<td>${c.trim()}</td>`).join("");
        return `<tr>${tds}</tr>`;
      }).join("");
      return `${pfx}<table><thead><tr>${th}</tr></thead><tbody>${rows}</tbody></table>`;
    }
  );
  text = text.replace(/(?:^|\n)(\d+\.\s+.*(?:\n(?!\n|\d+\. ).+)*)/g, (m) => {
    const items = m.trim().split(/\n/).map(line => line.replace(/^\d+\.\s+/, "")).map(li => `<li>${li}</li>`).join("");
    return `\n<ol>${items}</ol>`;
  });
  text = text.replace(/(?:^|\n)([-*]\s+.*(?:\n(?!\n|[-*]\s).+)*)/g, (m) => {
    const items = m.trim().split(/\n/).map(line => line.replace(/^[-*]\s+/, "")).map(li => `<li>${li}</li>`).join("");
    return `\n<ul>${items}</ul>`;
  });
  const lines = text.split(/\n{2,}/).map(chunk => {
    if (/^\s*<(h\d|ul|ol|li|pre|blockquote|table|thead|tbody|tr|td|th|img|p|code|hr)\b/i.test(chunk.trim())) return chunk;
    return `<p>${chunk.replace(/\n/g, "<br>")}</p>`;
  });
  return lines.join("\n");
}
function renderFromMarkdown(md) {
  const html = mdToHtmlLite(md);
  renderFromHTML(html, "");
}
function renderFromText(txt) {
  const safe = escapeHtml(String(txt || ""));
  viewerEl.innerHTML = `<div class="doc-root"><pre style="white-space:pre-wrap;line-height:1.6">${safe}</pre></div>`;
}

/* ==========================================================================
   RENDERING + SESSION
   ========================================================================== */
function renderDoc(i){
  if (i<0 || i>=docs.length) return;
  currentIndex = i;
  const d = docs[i];
  const code = getOrAssignCode(d);

  const ext = (d.ext || "").toLowerCase();
  const safeText = typeof d.text === "string" ? d.text : String(d.text || "");
  const safeHtml = typeof d.html === "string" ? d.html : "";

  if (viewerEl){
    const ext = (d.ext || ((d.filename||"").match(/\.[^.]+$/)?.[0] || "")).toLowerCase();

    if ((ext === ".html" || ext === ".htm") && safeHtml && safeHtml.trim()){
      const { headStyles, bodyHtml } = extractHtmlPayload(safeHtml);
      viewerEl.innerHTML = `${headStyles || ""}${bodyHtml || ""}`;
    }
    else if (ext === ".md" && typeof safeText === "string"){
      viewerEl.innerHTML = markdownToHtml(safeText);
    }
    else if (ext === ".txt"){
      viewerEl.innerHTML = `<pre style="white-space:pre-wrap;line-height:1.6">${escapeHtml(safeText)}</pre>`;
    }
    else if (safeHtml && safeHtml.trim()){
      viewerEl.innerHTML = safeHtml;
    }
    else {
      const parts = String(safeText||"").replace(/\r\n/g,"\n").split(/\n{2,}/);
      const htmlFromText = parts.map(p=>`<p>${escapeHtml(p).replace(/\n/g,"<br>")}</p>`).join("");
      viewerEl.innerHTML = htmlFromText || `<pre style="white-space:pre-wrap;line-height:1.6">${escapeHtml(safeText)}</pre>`;
    }
  }

  try {
    if (ext === ".html" || ext === ".htm" || /<\s*html[\s>]/i.test(safeHtml) || /<\s*body[\s>]/i.test(safeHtml)) {
      const { bodyHTML, styleText } = extractBodyAndStyles(safeHtml || safeText);
      renderFromHTML(bodyHTML || "", styleText || "");
    } else if (ext === ".md") {
      renderFromMarkdown(safeText);
    } else if (ext === ".txt") {
      renderFromText(safeText);
    } else {
      if (safeHtml && safeHtml.trim()) {
        renderFromHTML(safeHtml, "");
      } else if (safeText && safeText.trim()) {
        renderFromText(safeText);
      } else {
        viewerEl.innerHTML = `<div class="doc-root"><p>Upload a document to begin editing�</p></div>`;
      }
    }
  } catch (e) {
    console.error("[renderDoc] failed:", e);
    viewerEl.innerHTML = `<div class="doc-root"><pre style="white-space:pre-wrap;">${escapeHtml(safeText)}</pre></div>`;
  }

  safeSetText(topMeta, `File: ${d.filename || "Untitled"}${d.ext ? " | Format: "+d.ext : ""} | Code: ${code}`, "topMeta");
  renderDocInfo(
  docs,
  currentIndex,
  (i) => {                 // onGoto
    renderDoc(i);
  },
  (i) => {                 // onRemove
    try {
      // 1) Remove the doc
      docs.splice(i, 1);

      // 2) Recompute currentIndex safely
      if (docs.length === 0) {
        currentIndex = -1;
        // Clear viewer + meta when no docs left
        if (viewerEl) viewerEl.innerHTML = `<div class="doc-root"><p>Upload a document to begin editing�</p></div>`;
        safeSetText(topMeta, "File: �", "topMeta");
        safeSetText(docCountMeta, "Doc 0 of 0", "docCountMeta");
      } else {
        currentIndex = Math.min(currentIndex, docs.length - 1);
        currentIndex = currentIndex < 0 ? 0 : currentIndex;
      }

      // 3) Persist + refresh UI bits
      saveState();
      refreshDropdown();
      updateDocNavButtons();

      // 4) Re-render active doc if any
      if (currentIndex >= 0) renderDoc(currentIndex);

      // 5) Rebuild doc chips after change
      renderDocInfo(
        docs,
        currentIndex,
        (j) => renderDoc(j),
        (j) => {
          // recursion-safe: call same remove logic
          docs.splice(j, 1);
          if (docs.length === 0) {
            currentIndex = -1;
            if (viewerEl) viewerEl.innerHTML = `<div class="doc-root"><p>Upload a document to begin editing�</p></div>`;
            safeSetText(topMeta, "File: �", "topMeta");
            safeSetText(docCountMeta, "Doc 0 of 0", "docCountMeta");
          } else {
            currentIndex = Math.min(currentIndex, docs.length - 1);
            currentIndex = currentIndex < 0 ? 0 : currentIndex;
          }
          saveState();
          refreshDropdown();
          updateDocNavButtons();
          if (currentIndex >= 0) renderDoc(currentIndex);
        }
      );
    } catch (err) {
      console.error("Remove-doc failed:", err);
    }
  }
);

  safeSetText(docCountMeta, `Doc ${i+1} of ${docs.length}`, "docCountMeta");
  if (allDocs) allDocs.value = d.filename || "";

  updateDocNavButtons();
  underlineLinkedPhrases();
  highlightBucketKeywords();
  updateHighlightBadge();
  rebuildEngineHighlightsPanel();
  saveState();
}
function updateDocNavButtons(){ const b1 = $("btnPrevDoc"), b2=$("btnNextDoc"); if (!b1||!b2) return; b1.disabled = currentIndex<=0; b2.disabled = currentIndex>=docs.length-1 || docs.length===0; }
function saveState(){ try { localStorage.setItem(STORAGE_KEY, JSON.stringify({ docs, currentIndex })); } catch {} }
function loadState(){
  try{
    const raw=localStorage.getItem(STORAGE_KEY); if(!raw) return false;
    const state=JSON.parse(raw);
    if(!state||!Array.isArray(state.docs)||state.docs.length===0) return false;
    docs.splice(0, docs.length, ...state.docs);
    docs.forEach(d=>d&&getOrAssignCode(d));
    refreshDropdown();
    const idx=Math.min(typeof state.currentIndex==="number"?state.currentIndex:0, docs.length-1);
    renderDoc(idx);
    return true;
  }catch{ return false; }
}
function clearState(){ try { localStorage.removeItem(STORAGE_KEY); } catch {} }
function refreshDropdown(){
  for(let i=0;i<docs.length;i++){
  const code=docs[i]?(docs[i].docCode||getOrAssignCode(docs[i])):"";
  const opt=document.createElement("option");
  opt.value = String(docs[i].doc_id || docs[i].docId || "");
  if (!opt.value) opt.value = String(i); // fallback only if doc_id missing
  opt.textContent = `${docs[i].filename}${code?" ["+code+"]":""}`;
  allDocs.appendChild(opt);
}

}

// ==========================================================================
// IMPORTED_URLS storage � BACKEND ONLY (localStorage disabled)
// ==========================================================================

async function saveImportedUrlsLocal(){
  // Backend is the source of truth now; nothing to do here.
  return true;
}

async function loadImportedUrlsLocal(){
  // Load from backend instead of localStorage
  try {
    const base = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
    const ws = getCurrentWorkspaceId("default");
const res = await fetch(`${base}/api/urls/list?workspace_id=${encodeURIComponent(ws)}&limit=200000`);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data?.detail || "Not Found");

    IMPORTED_URLS = new Set(Array.isArray(data.urls) ? data.urls : []);
    console.log("[Imports] BACKEND loaded:", IMPORTED_URLS.size);
    return IMPORTED_URLS;
  } catch (e) {
    console.warn("[Imports] Could not load imports from backend:", e?.message || e);
    IMPORTED_URLS = new Set();
    return IMPORTED_URLS;
  }
}




// ================================
// Draft Topics � BACKEND load on startup
// ================================
async function loadDraftsFromBackend(workspaceId = "default") {
  const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");

  const res = await fetch(`${API_BASE}/api/draft/list?workspace_id=${encodeURIComponent(workspaceId)}&limit=200000`);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);

  const rows = Array.isArray(data.topics) ? data.topics : [];
  const next = new Map();

  for (const r of rows) {
    const topic_id = String(r.topic_id || "").trim();
    const working_title = String(r.working_title || "").trim();
    if (!topic_id || !working_title) continue;

    next.set(topic_id, {
      id: `d:${topic_id}`,
      topic_id,
      working_title,
      planned_slug: r.planned_slug || "",
      planned_url: r.planned_url || "",
      aliases: Array.isArray(r.aliases) ? r.aliases : [],
      priority: Number(r.priority || 0) || 0,
      canonical: Boolean(r.canonical),
    });
  }

  DRAFT_TOPICS = next;
  console.log("[Draft] BACKEND loaded:", DRAFT_TOPICS.size);
  return DRAFT_TOPICS;
}

const startupWs = getCurrentWorkspaceId("");
if (startupWs) {
  loadDraftsFromBackend(startupWs)
    .catch(e => console.warn("[Draft] startup load failed:", e?.message || e));
}


// === Imported topics store (titles/URLs from sitemap/drafts/external lists) ===
// This is the SINGLE source of truth for imports (sitemap, backup CSV/TXT, draft, external).

const IMPORT_LS_KEY = "lc_imported_topics_v1";  // localStorage key

const IMPORTED_TOPICS    = [];        // [{ id, title, url, source }]
const IMPORT_TITLE_INDEX = new Map(); // norm(title) -> rec
const IMPORT_URL_INDEX   = new Map(); // url -> rec

function normTitle(s) {
  return String(s || "").trim().toLowerCase();
}

function mkId(title, url) {
  const base = (title || url || "item")
    .replace(/[^\w]+/g, "-")
    .slice(0, 40) || "item";
  return `${base}-${Math.random().toString(36).slice(2, 7)}`;
}

/**
 * Persist IMPORTED_TOPICS to localStorage (for reloads).
 */
function saveImportsToStorage() {
  try {
    const payload = IMPORTED_TOPICS.map(rec => ({
      id:     rec.id,
      title:  rec.title,
      url:    rec.url,
      source: rec.source
    }));
    localStorage.setItem(IMPORT_LS_KEY, JSON.stringify(payload));
  } catch (e) {
    console.warn("Could not save imports:", e);
  }
}

/**
 * Load IMPORTED_TOPICS from BACKEND (single source of truth).
 * Replaces localStorage imports completely.
 */
async function loadImportsFromBackend() {
  try {
    const base =
      (typeof window !== "undefined" && window.LINKCRAFTOR_API_BASE)
        ? String(window.LINKCRAFTOR_API_BASE).replace(/\/+$/, "")
        : "http://127.0.0.1:8001";

    const ws = getCurrentWorkspaceId("default");
const url = `${base}/api/urls/list?workspace_id=${encodeURIComponent(ws)}&limit=200000`;
    const res = await fetch(url);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      const msg = data?.detail || data?.error || `HTTP ${res.status}`;
      throw new Error(msg);
    }

    const urls = Array.isArray(data.urls) ? data.urls : [];

    // Reset in-memory structures (same as before)
    IMPORTED_TOPICS.length = 0;
    IMPORT_TITLE_INDEX.clear();
    IMPORT_URL_INDEX.clear();

    // Convert URLs -> your IMPORTED_TOPICS records
    // Title is unknown here, so we generate a lightweight title from the URL.
    for (const u of urls) {
      const urlStr = String(u || "").trim();
      if (!urlStr) continue;

      let title = urlStr;
      try {
        const U = new URL(urlStr);
        const host = (U.hostname || "").replace(/^www\./, "");
        const parts = (U.pathname || "/")
          .split("/")
          .filter(Boolean)
          .slice(-3);
        title = parts.length ? parts.join(" ") : host;
      } catch {}

      const rec = {
        id: mkId(title || "", urlStr),
        title,
        url: urlStr,
        source: "backend"
      };

      const keyT = title ? normTitle(title) : null;
      const keyU = urlStr;

      IMPORTED_TOPICS.push(rec);
      if (keyT) IMPORT_TITLE_INDEX.set(keyT, rec);
      if (keyU) IMPORT_URL_INDEX.set(keyU, rec);
    }

    updateImportBadge();
    rebuildTitleUrlDatalists();

    if (typeof window !== "undefined") {
      window.LC_IMPORTS = IMPORTED_TOPICS;
      window.LC_getImportedTopics = () => [...IMPORTED_TOPICS];
    }

    console.log("[Imports] BACKEND loaded:", IMPORTED_TOPICS.length);
  } catch (e) {
    console.warn("[Imports] Could not load imports from backend:", e?.message || e);
  }
}



/**
 * Ingest rows from any import (sitemap/backup/draft/external).
 * rows: [{title, url}], source: 'sitemap' | 'backup' | 'draft' | 'external' | 'import'
 */
function ingestImportedRows(rows, source = "import") {
  let added = 0, updated = 0;

  for (const row of (rows || [])) {
    const title = row.title ? String(row.title).trim() : null;
    const url   = row.url   ? String(row.url).trim()   : null;
    const keyT  = title ? normTitle(title) : null;
    const keyU  = url   ? url : null;

    // Prefer de-dup by URL; otherwise de-dup by normalized title
    let existing = null;
    if (keyU && IMPORT_URL_INDEX.has(keyU)) {
      existing = IMPORT_URL_INDEX.get(keyU);
    } else if (keyT && IMPORT_TITLE_INDEX.has(keyT)) {
      existing = IMPORT_TITLE_INDEX.get(keyT);
    }

    if (existing) {
      if (!existing.title && title) {
        existing.title = title;
        if (keyT) IMPORT_TITLE_INDEX.set(keyT, existing);
      }
      if (!existing.url && url) {
        existing.url = url;
        if (keyU) IMPORT_URL_INDEX.set(keyU, existing);
      }
      existing.source = existing.source || source;
      updated++;
    } else {
      const rec = {
        id:     mkId(title || "", url || ""),
        title,
        url,
        source
      };
      IMPORTED_TOPICS.push(rec);
      if (keyT) IMPORT_TITLE_INDEX.set(keyT, rec);
      if (keyU) IMPORT_URL_INDEX.set(keyU, rec);
      added++;
    }
  }

  console.log(`[Import] ${added} added, ${updated} updated. Total: ${IMPORTED_TOPICS.length}`);
  updateImportBadge();
  rebuildTitleUrlDatalists();
  saveImportsToStorage();

  // Expose for engine + IL modal
  if (typeof window !== "undefined") {
    window.LC_IMPORTS = IMPORTED_TOPICS;
    window.LC_getImportedTopics = () => [...IMPORTED_TOPICS];
  }
}

/**
 * Rebuild IL datalists (Title / URL) from IMPORTED_TOPICS.
 */
function rebuildTitleUrlDatalists() {
  const dlTitle = document.getElementById("ilTitleList");
  const dlUrl   = document.getElementById("ilUrlList");
  if (!dlTitle && !dlUrl) return;

  if (dlTitle) {
    dlTitle.innerHTML = "";
    for (const rec of IMPORTED_TOPICS) {
      const label = rec.title || (rec.url ? `[URL] ${rec.url}` : null);
      if (!label) continue;
      const opt = document.createElement("option");
      opt.value = label;
      dlTitle.appendChild(opt);
    }
  }

  if (dlUrl) {
    dlUrl.innerHTML = "";
    for (const rec of IMPORTED_TOPICS) {
      if (!rec.url) continue;
      const opt = document.createElement("option");
      opt.value = rec.url;
      dlUrl.appendChild(opt);
    }
  }
}

/**
 * Update the badge that shows total imported items.
 */
function updateImportBadge() {
  // ? Unified total: (backend URLs) + (backend drafts)
  try {
  const ws = getCurrentWorkspaceId("");
  if (ws) updateUnifiedImportCount?.(ws);
  else setImportCount(0);
} catch {}
}


/**
 * Tiny helper used in boot() to know if we already have a sitemap.
 */
function hasSitemapImported() {
  return IMPORTED_TOPICS.some(rec => rec.source === "sitemap");
}


// === Parsers (XML / CSV / TXT) ===
async function readText(file) {
  return await file.text();
}

// Returns: [{title, url}] (title may be null)
// Tolerant: tries XML first; if invalid, falls back to plain-text URL list.
async function parseXmlSitemap(file) {
  const text = await readText(file);
  const trimmed = String(text || "").trim();
  if (!trimmed) return [];

  // If it doesn't even look like XML, treat as plain-text list of URLs
  if (!trimmed.startsWith("<")) {
    return trimmed
      .split(/\r?\n/)
      .map(line => line.trim())
      .filter(Boolean)
      .map(u => ({ title: null, url: u }));
  }

  try {
    const parser = new DOMParser();
    const xml    = parser.parseFromString(trimmed, "application/xml");

    const errNode = xml.querySelector("parsererror");
    if (errNode) {
      console.warn("Sitemap XML parser error, falling back to plain text:", errNode.textContent);
      // Fallback: treat as plain text, one URL per line
      return trimmed
        .split(/\r?\n/)
        .map(line => line.trim())
        .filter(Boolean)
        .map(u => ({ title: null, url: u }));
    }

    // Handle <urlset><url><loc> and <sitemapindex><sitemap><loc>
    const locs = Array.from(xml.querySelectorAll("url > loc, sitemap > loc"));
    const items = locs
      .map(node => (node.textContent || "").trim())
      .filter(Boolean)
      .map(u => ({ title: null, url: u }));

    return items;
  } catch (err) {
    console.error("Sitemap parse failed as XML, falling back to plain text:", err);
    // Final fallback: treat whole file as plain text URLs
    return trimmed
      .split(/\r?\n/)
      .map(line => line.trim())
      .filter(Boolean)
      .map(u => ({ title: null, url: u }));
  }
}

// CSV: support "title,url" | "url" | "title|url" | tabs/semicolons
// Returns: [{title, url}] (url optional for drafts)
async function parseCsvList(file) {
  const text = await readText(file);
  const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  const items = [];
  for (const line of lines) {
    const parts = line.split(/,(?!\s)|;|\t|\|/).map(s => s.trim());
    if (parts.length === 1) {
      const v = parts[0];
      if (/^https?:\/\//i.test(v)) items.push({ title: null, url: v });
      else items.push({ title: v, url: null });
    } else {
      const a = parts[0], b = parts[1];
      if (/^https?:\/\//i.test(b)) items.push({ title: a || null, url: b });
      else items.push({ title: a || null, url: b || null });
    }
  }
  return items;
}

// TXT: one entry per line; URL or Title or "Title - URL" / "Title | URL"
async function parseTxtList(file) {
  const text = await readText(file);
  const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  const items = [];
  for (const line of lines) {
    let m = line.match(/^(.+?)\s*[-|]\s*(https?:\/\/\S+)$/i);
    if (m) {
      items.push({ title: m[1].trim(), url: m[2].trim() });
      continue;
    }
    if (/^https?:\/\//i.test(line)) {
      items.push({ title: null, url: line });
    } else {
      items.push({ title: line, url: null });
    }
  }
  return items;
}

// Drafts: title-only OK; pick CSV/TXT parser
async function parseDraftList(file) {
  const ext = (file.name.split(".").pop() || "").toLowerCase();
  return ext === "csv" ? parseCsvList(file) : parseTxtList(file);
}

// External (CSV/TXT): prefer URL if present
async function parseExternalList(file) {
  const ext = (file.name.split(".").pop() || "").toLowerCase();
  return ext === "csv" ? parseCsvList(file) : parseTxtList(file);
}


// ========================== BOOT ===============================
async function boot() {
  await ensureExternalCategories();

  applyStopwords();
  loadSettingsFromStore();

  loadLinkedSet();
  loadRejectedSet();
  wireDecisionButtons();
  LINKED_MAP = new Map();
  loadImportedUrlsLocal();

  // NEW: reload imported topics (sitemap/backup/draft/external) from localStorage
  loadImportsFromBackend(); // DISABLED: /api/urls/list not available



  loadTitleIndexFromLocal();
  loadPublishedTopics();
  loadDraftTopics();

  const recovered = loadState();
  if (!recovered) {
    safeSetText(docCountMeta, "Doc 0 of 0", "docCountMeta");
    updateDocNavButtons();
    underlineLinkedPhrases();
    highlightBucketKeywords();
    updateHighlightBadge();
    rebuildEngineHighlightsPanel();
  } else {
    rebuildTitleIndexFromDocs();
    rebuildPublishedTopics();

    if (docs.length) {
      const firstExt = extOf(docs[0]?.filename || docs[0]?.ext || "");
      if (firstExt) {
        SESSION_FORMAT = firstExt;
        currentAccept = SESSION_FORMAT;
        fileInput?.setAttribute("accept", SESSION_FORMAT);
        refreshUploadMenuForSessionFormat();
      }
    }

    underlineLinkedPhrases();
    highlightBucketKeywords();
    updateHighlightBadge();
    rebuildEngineHighlightsPanel();
    showToast(errorBox, "Recovered previous session.", 1200);
  }

  const saved = localStorage.getItem(HILITE_KEY);
  highlightEnabled = saved === null ? true : saved === "true";
  if (toggleHighlight) {
    toggleHighlight.checked = highlightEnabled;
    toggleHighlight.addEventListener("change", () => {
      highlightEnabled = !!toggleHighlight.checked;
      localStorage.setItem(HILITE_KEY, String(highlightEnabled));
      if (highlightsArmed) runPipelineAndHighlight({ append: true });
      else {
        underlineLinkedPhrases();
        highlightBucketKeywords();
        updateHighlightBadge();
        rebuildEngineHighlightsPanel();
      }
    });

    // If a sitemap is already imported, hide any sitemap tip that might have been rendered
    if (hasSitemapImported()) {
      const banner = document.getElementById("playbookBanner");
      if (banner && (banner.textContent || "").toLowerCase().includes("sitemap")) {
        banner.style.display = "none";
      }
      const err = document.getElementById("error");
      if (err && (err.textContent || "").toLowerCase().includes("sitemap")) {
        err.textContent = "";
        err.style.display = "none";
      }
      // catch any aria-live notices that mention sitemap
      document
        .querySelectorAll(".toast,.banner,.notice,[role='status'],[aria-live]")
        .forEach(el => {
          const t = (el.textContent || "").toLowerCase();
          if (t.includes("sitemap") && t.includes("cross-document")) el.style.display = "none";
        });
    }
  }

  btnAutoLinkMain && (btnAutoLinkMain.disabled = false);

  // IL modal wiring (entity-aware, content-aware compatible)
  initILModal({
    root: document,
    getViewerEl,
    ensureReferencesModule,
    computeFinalUrl,
    slugifyHeading,
    findEngineSuggestionsForPhrase,
    rejectPhrase,
    unwrapMark,
    underlineLinkedPhrases,
    highlightBucketKeywords,
    updateHighlightBadge,
    rebuildEngineHighlightsPanel,
    saveLinkedSet,
    state: {
      LINKED_SET,
      LINKED_MAP,
      APPLIED_LINKS,
      setCurrentMark,
      setCurrentPhrase,
      getCurrentMark,
      getCurrentPhrase,
    },
  });

  // Buckets wiring
  initBuckets({
    root: document,
    getViewerEl: () => viewerEl,
    isRejected: (type, phrase) => isRejected(type, phrase),
  });

  // First paint of bucket highlights on load
  highlightBucketKeywords();

  // === Import Sitemap split dropdown (UI + file pickers) ===
  {
    const split    = document.getElementById("importSplit");
    const btnMain  = document.getElementById("btnImportMain");
    const btnCaret = document.getElementById("btnImportMenu");
    const menu     = document.getElementById("importMenu");

    const inSitemap = document.getElementById("sitemapFile"); // .xml,.csv,.txt
    const inDraft   = document.getElementById("draftFile");   // draft/external .csv,.txt

    if (split && btnMain && btnCaret && menu && (inSitemap || inDraft)) {
      let CURRENT_IMPORT_KIND = null; // 'xml' | 'csv' | 'txt' | 'draft' | 'external'

      function openMenu()  { menu.hidden = false; menu.classList.add("open"); btnCaret.setAttribute("aria-expanded", "true"); }
      function closeMenu() { menu.hidden = true;  menu.classList.remove("open"); btnCaret.setAttribute("aria-expanded", "false"); }
      function toggleMenu(){ menu.hidden ? openMenu() : closeMenu(); }

      btnMain.addEventListener("click", (e) => { e.stopPropagation(); toggleMenu(); });
      btnCaret.addEventListener("click", (e) => { e.stopPropagation(); toggleMenu(); });

      document.addEventListener("click", (e) => { if (!split.contains(e.target)) closeMenu(); });
      document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeMenu(); });

      menu.addEventListener("click", (e) => {
        const btn = e.target.closest("button[data-action]");
        if (!btn) return;
        const action = btn.getAttribute("data-action");

        if (action === "imp-xml") {
          CURRENT_IMPORT_KIND = "xml";
          if (inSitemap) {
            inSitemap.setAttribute("accept", ".xml");
            inSitemap.value = "";
            closeMenu(); inSitemap.click();
          }
          return;
        }
        if (action === "imp-csv") {
          CURRENT_IMPORT_KIND = "csv";
          if (inSitemap) {
            inSitemap.setAttribute("accept", ".csv");
            inSitemap.value = "";
            closeMenu(); inSitemap.click();
          }
          return;
        }
        if (action === "imp-txt") {
          CURRENT_IMPORT_KIND = "txt";
          if (inSitemap) {
            inSitemap.setAttribute("accept", ".txt");
            inSitemap.value = "";
            closeMenu(); inSitemap.click();
          }
          return;
        }
        if (action === "draft-map") {
          CURRENT_IMPORT_KIND = "draft";
          if (inDraft) {
            inDraft.setAttribute("accept", ".csv,.txt");
            inDraft.value = "";
            closeMenu(); inDraft.click();
          }
          return;
        }
        if (action === "external-url") {
          CURRENT_IMPORT_KIND = "external";
          if (inDraft) {
            inDraft.setAttribute("accept", ".csv,.txt");
            inDraft.value = "";
            closeMenu(); inDraft.click();
          }
          return;
        }

       if (action === "clear-imports") {
  (async () => {
    try {
      const base = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
      const ws = getCurrentWorkspaceId("default");

      // 1) Clear sitemap/imported URLs (backend)
      await fetch(`${base}/api/urls/clear?workspace_id=${encodeURIComponent(ws)}`, { method: "POST" });

      // 2) Clear draft map (backend)  ?
      const r2 = await fetch(`${base}/api/draft/clear?workspace_id=${encodeURIComponent(ws)}`, { method: "POST" });
      const d2 = await r2.json().catch(() => ({}));
      if (!r2.ok) throw new Error(d2?.detail || d2?.error || `HTTP ${r2.status}`);

      // 3) Reload both backend stores to repaint UI immediately
      await loadImportsFromBackend();
      await loadDraftsFromBackend(ws);

      // 4) Update unified badge
      updateImportBadge();

      closeMenu();
      alert("Imported URLs + Draft map cleared (backend).");
    } catch (e) {
      console.error("[clear-imports] failed:", e);
      alert("Clear failed: " + (e?.message || e));
    }
  })();

  return;
}

      });

      // Change handlers: call parsers + ingest
      inSitemap?.addEventListener("change", async () => {
        const file = inSitemap.files?.[0];
        if (!file) return;

        try {
          let rows = [];

          if (CURRENT_IMPORT_KIND === "xml") {
            rows = await parseXmlSitemap(file);
          } else if (CURRENT_IMPORT_KIND === "csv") {
            rows = await parseCsvList(file);
          } else if (CURRENT_IMPORT_KIND === "txt") {
            rows = await parseTxtList(file);
          } else {
            const ext = (file.name.split(".").pop() || "").toLowerCase();
            if (ext === "xml") rows = await parseXmlSitemap(file);
            else if (ext === "csv") rows = await parseCsvList(file);
            else rows = await parseTxtList(file);
          }

          let src;
          if (CURRENT_IMPORT_KIND === "xml") {
            src = "sitemap";
          } else if (CURRENT_IMPORT_KIND === "csv" || CURRENT_IMPORT_KIND === "txt") {
            src = "backup";
          } else {
            const ext = (file.name.split(".").pop() || "").toLowerCase();
            src = (ext === "xml") ? "sitemap" : "backup";
          }

          ingestImportedRows(rows, src);
          console.log("[Import Sitemap]", CURRENT_IMPORT_KIND, file.name, rows, "src=", src);
          alert(`Parsed ${rows.length} item(s) from ${file.name}`);
        } catch (err) {
          console.error("Sitemap parse failed:", err);
          alert("Failed to parse sitemap file.");
        }
      });

      inDraft?.addEventListener("change", async () => {
  const file = inDraft.files?.[0];
  inDraft.value = "";
  if (!file) return;

  // ? Draft Map must be backend-only (so unified count works)
  if (CURRENT_IMPORT_KIND !== "draft") {
    alert("External URL import is disabled here. Use the External Resolver flow instead.");
    return;
  }

  try {
  // Use the backend draft importer that already exists earlier in app.js
  const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");

  const fd = new FormData();
  fd.append("file", file);

  const ws = getCurrentWorkspaceId("default");

  const res = await fetch(
    `${API_BASE}/api/draft/import?workspace_id=${encodeURIComponent(ws)}`,
    { method: "POST", body: fd }
  );
  const r = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(r?.detail || r?.error || `HTTP ${res.status}`);

  // Reload draft topics into memory (same logic you already use elsewhere)
  const res2 = await fetch(
    `${API_BASE}/api/draft/list?workspace_id=${encodeURIComponent(ws)}&limit=200000`
  );
  const data2 = await res2.json().catch(() => ({}));
  if (!res2.ok) throw new Error(data2?.detail || data2?.error || `HTTP ${res2.status}`);

  const rows = Array.isArray(data2.topics) ? data2.topics : [];

  const activeDraftIds = rows.map((_, i) => `draft_${String(i + 1).padStart(4, "0")}`);

await fetch(`${API_BASE}/api/site/target_pools/active_target_set/save`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    workspace_id: ws,
    active_draft_ids: activeDraftIds,
    preserve_omitted_fields: true
  })
});

  // Reuse your existing mapper if present; otherwise keep it simple
  try { applyDraftToMemory?.(rows); } catch {}

// Update the single combined badge
await updateUnifiedImportCount(ws);

await fetch(
  `${API_BASE}/api/site/target_pools/rebuild_all?workspace_id=${encodeURIComponent(ws)}`,
  { method: "POST" }
);

alert(`Draft saved to backend. Total drafts: ${rows.length}`);


} catch (err) {
  console.error("[Draft backend import] failed:", err);
  alert("Draft import failed: " + (err?.message || err));
}
});

} 
 
 } 

  } updateImportBadge();


  // ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
function bootExtras() {
  console.log("APP.JS ACTIVE VERSION: HELLO FROM TOP");

  // ?? IMPORTANT:
  // Keep whatever initialization you already had inside boot()
  // (wiring uploads, toolbar, loading saved docs, stopwords, buckets, etc.).
  // Do NOT remove your existing setup lines here.
  //
  // Just make sure the following three sidebar initialisers are ALSO called
  // somewhere inside this boot() function.

  // 1) Manage rejections panel (right sidebar)
  initRejectionsUI({
    onChange: () => {
      // Whenever rejections change, keep related panels in sync
      try { LR_rebuild(); } catch {}
      try { rebuildLinkedPhrasesList(); } catch {}
    }
  });

  // 2) Linked phrases list (per-phrase Undo)
  initLinkedPhrasesUI({
    onUndoPhrase: (phrase) => {
      // Hook where you can also update LINKED_SET / LINKED_MAP later
      console.log("[LinkedPhrases] undo phrase:", phrase);
    },
    onChange: () => {
      // After undoing a phrase, refresh Link Resolution panel
      try { LR_rebuild(); } catch {}
    }
  });

  // 3) Link Resolution panel (resolved vs unresolved phrases)
  initLinkResolutionPanel();

  // Optionally ensure rejections panel is painted once at boot
  try { rebuildRejectionsPanel(); } catch {}
  try { rebuildLinkedPhrasesList(); } catch {}
}

// =====================================================
// Layer 1.3 � Wire ? Accept / ? Reject buttons to /api/engine/decision
// (Event delegation on viewerEl; no UI logic changes beyond emitting decisions)
// =====================================================
function wireDecisionButtons(){
  if (!viewerEl) return;
  if (viewerEl.dataset.decisionWired === "1") return;
  viewerEl.dataset.decisionWired = "1";

  viewerEl.addEventListener("click", async (e) => {
    const btn = e.target?.closest?.("button.kw-btn.kw-accept, button.kw-btn.kw-reject");
    if (!btn) return;

    const mark = btn.closest("mark.kwd");
    if (!mark) return;

    // Identify event type
    const isAccept = btn.classList.contains("kw-accept");
    const eventType = isAccept ? "LINK_SUGGESTION_ACCEPTED" : "LINK_SUGGESTION_REJECTED";

    // Phrase
    let phrase = "";
    try {
      phrase = decodeURIComponent(mark.getAttribute("data-phrase") || "").trim();
    } catch {
      phrase = String(mark.getAttribute("data-phrase") || "").trim();
    }
    if (!phrase) phrase = (mark.textContent || "").replace(/[??]/g, "").trim();

    // Build phraseCtx (reuse your existing helper)
    const baseCtx = (typeof buildPhraseContext === "function") ? buildPhraseContext(phrase) : { phraseText: phrase };

    const workspaceId = getCurrentWorkspaceId("ws_demo");
    const docId =
      (window.LC_ACTIVE_DOC_ID || null) ||
      (docs && currentIndex >= 0 && docs[currentIndex] ? (docs[currentIndex].doc_id || docs[currentIndex].docId || null) : null);

    const phraseCtx = {
      workspaceId,
      docId,
      phraseText: phrase,
      contextType: baseCtx.contextType || null,
      sectionType: "BODY",
      intent: "INFO",
      entities: Array.isArray(baseCtx.entities) ? baseCtx.entities : []
    };

    // Candidate (from mark dataset)
    const kind = String(mark.getAttribute("data-kind") || "").toLowerCase();
    const url  = String(mark.getAttribute("data-url") || "").trim();
    const title = String(mark.getAttribute("data-title") || "").trim();
    const topicId = String(mark.getAttribute("data-topic-id") || "").trim();

    const candidate = {
      id: topicId || "",
      title: title || phrase,
      url: url || "",
      sourceType: kind || "engine",
      isExternal: kind === "external",
      entities: Array.isArray(baseCtx.entities) ? baseCtx.entities : []
    };

    // Emit decision (do not block UI)
    await emitDecision(eventType, phraseCtx, candidate, {
      uiControl: isAccept ? "kw-accept" : "kw-reject",
      kind
    });
  }, true);
}



// DOM ready wrapper
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => { boot(); }, { once: true });
} else {
  boot();
}

// === Download menu click delegation (respects session format)
(function wireDownloadMenu(){
  const menu = document.getElementById("downloadMenu");
  if (!menu) return;

  // Hide disallowed options (and permanently removed ones) on load
  try { ensureDownloadMenuForSession(); } catch {}

  menu.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-ext]");
    if (!btn) return;

    const ext = (btn.getAttribute("data-ext") || "").toLowerCase();  // "docx" | "md" | "txt" | "html"
    const sess = (getSessionFormat() || "").toLowerCase();           // ".docx" | ".md" | ".txt" | ".html" | ""

    // If a session format is locked, only allow the matching option
    if (sess) {
      const expected = ({ ".docx":"docx", ".md":"md", ".txt":"txt", ".html":"html" })[sess];
      if (ext !== expected) {
        const toast = document.getElementById("error");
        if (toast) {
          toast.textContent = `This session is locked to ${sess} downloads.`;
          setTimeout(()=> toast.textContent="", 1600);
        }
        return;
      }
    }

    // Dispatch to the correct exporter
    if (ext === "docx")       { downloadDocx(); }
    else if (ext === "md")    { downloadText("md"); }   // MD uses plain-text pipeline with .md extension
    else if (ext === "txt")   { downloadText("txt"); }
    else if (ext === "html")  { downloadHTML("html"); }
    // "original" and "htm" are intentionally not handled (removed)
  });
})();


/* ==========================================================================
   FORCE Sitemap Import ? BACKEND (single picker, hard takeover)
   - Click: we open ONE picker in the same user gesture
   - Change: we upload to backend and block legacy local parsing
   ========================================================================== */

(function wireSitemapImportBackend() {
  const API_BASE =
    (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");

  const sitemapFile = document.getElementById("sitemapFile");
  if (!sitemapFile) {
    console.error("[SITEMAP->BACKEND] sitemapFile not found (#sitemapFile)");
    return;
  }

  // Make sure it is truly a file input
  if (String(sitemapFile.type || "").toLowerCase() !== "file") {
    console.error("[SITEMAP->BACKEND] #sitemapFile is not <input type='file'>");
    return;
  }

  const scope = document.getElementById("importMenu") || document;

  function findBtnContains(txt) {
    const t = String(txt || "").toLowerCase();
    return [...scope.querySelectorAll("button")]
      .find(b => (b.textContent || "").toLowerCase().includes(t));
  }

  const btnXML = findBtnContains("xml");
  const btnCSV = findBtnContains("csv");
  const btnTXT = findBtnContains("txt");

  if (!btnXML || !btnCSV || !btnTXT) {
    console.error("[SITEMAP->BACKEND] Import buttons not found (xml/csv/txt)");
    return;
  }

  function toast(msg, ms = 2400) {
    try { window.showToast?.(window.errorBox, msg, ms); } catch {}
    console.log("[SITEMAP->BACKEND]", msg);
  }

  function ensureImportedUrlsSet() {
    if (!window.IMPORTED_URLS || !(window.IMPORTED_URLS instanceof Set)) {
      window.IMPORTED_URLS = new Set();
    }
    return window.IMPORTED_URLS;
  }

 async function uploadToBackend(file) {
  const fd = new FormData();
  // Backend MUST be expecting UploadFile named "file"
  fd.append("file", file, file.name);

  const ws = getCurrentWorkspaceId("default");
  const url = `${API_BASE}/api/urls/import?workspace_id=${encodeURIComponent(ws)}`;
  const res = await fetch(url, { method: "POST", body: fd });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data?.detail || data?.error || `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}

  async function reloadFromBackend() {
  const ws = getCurrentWorkspaceId("default");
const url = `${API_BASE}/api/urls/list?workspace_id=${encodeURIComponent(ws)}&limit=200000`;
  const res = await fetch(url);

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data?.detail || data?.error || `HTTP ${res.status}`;
    throw new Error(detail);
  }

  const set = ensureImportedUrlsSet();
  const before = set.size;

  const urls = Array.isArray(data?.urls) ? data.urls : [];

  // ? GUARD: never wipe a non-empty in-memory set with an empty backend response
  // This prevents the "82 then 0" flip you keep seeing.
  if (urls.length === 0 && before > 0) {
    console.warn("[Imports] BACKEND returned 0; keeping existing:", before);
    return before;
  }

  // ? Normal replace when backend has data (or when we had nothing yet)
  set.clear();
  for (const u of urls) set.add(u);

  return set.size;
}

// ? add this line:
window.__LC_reloadFromBackend = reloadFromBackend;

  // Hard-takeover click: stop legacy click handlers and open picker once
  function takeoverClick(btn, accept) {
    btn.addEventListener("click", (e) => {
      // Block other handlers that might also call click() or set accept differently
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();

      sitemapFile.setAttribute("accept", accept);

      // ONE picker, opened in the same user gesture (no setTimeout)
      sitemapFile.click();
    }, true); // capture-phase so we win
  }

  // More permissive accept strings (some browsers are picky)
  takeoverClick(btnXML, ".xml,application/xml,text/xml");
  takeoverClick(btnCSV, ".csv,text/csv,application/vnd.ms-excel");
  takeoverClick(btnTXT, ".txt,text/plain");

  // Hard-takeover change: upload to backend, block any legacy local-parse handlers
  let uploading = false;

  sitemapFile.addEventListener("change", async (e) => {
    const f = sitemapFile.files?.[0];
    if (!f) return;

    // Prevent any other change listeners (legacy local parsing)
e.stopImmediatePropagation();

if (uploading) return;
uploading = true;

try {
  const set = ensureImportedUrlsSet();
  const before = set.size;

  toast(`Uploading ${f.name} to backend...`, 1800);

  await uploadToBackend(f);

  const ws = getCurrentWorkspaceId("");
  const after = ws ? (await apiLoadImportedUrls(ws, 200000)).length : 0;

  if (ws) await updateUnifiedImportCount(ws);

  if (ws) {
    try {
      const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
      const importedUrls = await apiLoadImportedUrls(ws, 200000);

    const saveRes = await fetch(`${API_BASE}/api/site/target_pools/active_target_set/save`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    workspace_id: ws,
    active_imported_urls: importedUrls,
    preserve_omitted_fields: true
  })
});

      const saveData = await saveRes.json().catch(() => ({}));
      if (!saveRes.ok) {
        throw new Error(saveData?.detail || saveData?.error || `active_target_set/save failed: HTTP ${saveRes.status}`);
      }

      const rebuildRes = await fetch(
        `${API_BASE}/api/site/target_pools/rebuild_all?workspace_id=${encodeURIComponent(ws)}`,
        { method: "POST" }
      );

      const rebuildData = await rebuildRes.json().catch(() => ({}));
      if (!rebuildRes.ok) {
        throw new Error(rebuildData?.detail || rebuildData?.error || `rebuild_all failed: HTTP ${rebuildRes.status}`);
      }

      console.log("[SITEMAP->ACTIVE] save result:", saveData);
      console.log("[SITEMAP->ACTIVE] rebuild result:", rebuildData);

      console.log("[SITEMAP->ACTIVE] activated imported URLs:", importedUrls.length);
    } catch (err) {
      console.warn("[SITEMAP->ACTIVE] activation/rebuild failed:", err);
    }
  }

  // Immediately update the existing count display
  try {
    const el = document.getElementById("importCount");
    setImportCount(ws ? (after || 0) : 0);
  } catch {}


      // Optional rebuild hooks if present
      try { window.rebuildTitleIndexFromDocs?.(); } catch {}
      try { window.rebuildPublishedTopics?.(); } catch {}

      const delta = after - before;
      toast(`Imported ${delta >= 0 ? delta : 0} URLs (backend). Total: ${after}`, 2600);
    } catch (err) {
      const msg = err?.message || String(err);
      toast(`Import failed: ${msg}`, 3200);
      console.error("[SITEMAP->BACKEND] import failed:", err);
    } finally {
      // Reset so picking the same file again still triggers change
      sitemapFile.value = "";
      uploading = false;
    }
  }, true);

  console.log("[SITEMAP->BACKEND] ? wired (click+change takeover, backend-only)");
})();

// Hydrate import count + imported URLs from backend on initial load
(async function hydrateImportsOnLoad(){
  try {
    const ws = getCurrentWorkspaceId("");

    if (!ws) {
      const el = document.getElementById("importCount");
      if (el) el.textContent = "0";
      console.log("[Imports] BACKEND loaded:", 0);
      return;
    }

    const after = await (window.__LC_reloadFromBackend
      ? window.__LC_reloadFromBackend()
      : window.reloadFromBackend());

    await updateUnifiedImportCount(ws);

    try {
      const el = document.getElementById("importCount");
      if (el) el.textContent = String(after || 0);
    } catch {}

    console.log("[Imports] BACKEND loaded:", after || 0);
  } catch (e) {
    console.warn("[Imports] BACKEND hydrate failed:", e);
    try {
      const el = document.getElementById("importCount");
      if (el) el.textContent = "0";
    } catch {}
  }
})();


function updateConnectionStatus(domain = "") {
  const connectionDot = document.getElementById("connectionDot");
  const connectionText = document.getElementById("connectionText");

  if (!connectionDot || !connectionText) return;

  if (domain) {
    connectionDot.classList.remove("disconnected");
    connectionDot.classList.add("connected");
    connectionText.textContent = "Connected";
  } else {
    connectionDot.classList.remove("connected");
    connectionDot.classList.add("disconnected");
    connectionText.textContent = "Disconnected";
  }
}


// ===============================
// DOMAIN CONNECT POPUP
// ===============================

document.addEventListener("DOMContentLoaded", () => {

  const domainModal = document.getElementById("domainModal");
  const domainInput = document.getElementById("domainInput");
  const btnConnectDomain = document.getElementById("btnConnectDomain");
  const btnClearSession = document.getElementById("btnClearSession");

  const savedDomain = localStorage.getItem("lc_domain") || "";

  if (savedDomain) {
  window.LINKCRAFTOR_WORKSPACE_ID = getCurrentWorkspaceId("");
  updateConnectionStatus(savedDomain);
  if (domainModal) {
    domainModal.style.display = "none";
  }
} else {
  window.LINKCRAFTOR_WORKSPACE_ID = "";
  updateConnectionStatus("");

  const importCountEl = document.getElementById("importCount");
  if (importCountEl) {
    importCountEl.textContent = "0";
  }

  if (domainModal) {
    domainModal.style.display = "flex";
  }
}

  if (!btnConnectDomain) {
    console.warn("Connect domain button not found");
    return;
  }

  btnConnectDomain.addEventListener("click", async () => {

    const domain = (domainInput.value || "").trim();

    if (!domain) {
      alert("Please enter a domain");
      return;
    }

    try {

      const res = await fetch(
        `${window.LINKCRAFTOR_API_BASE}/api/site/workspace/connect_domain`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ domain })
        }
      );

      const data = await res.json();

      if (!data.ok) {
        alert("Could not connect domain");
        return;
      }

      localStorage.setItem("lc_workspace_id", data.workspace_id);
      localStorage.setItem("lc_domain", data.domain);

      window.LINKCRAFTOR_WORKSPACE_ID = data.workspace_id;

      updateConnectionStatus(data.domain);

      console.log("[Workspace]", data.workspace_id);

      if (domainModal) {
        domainModal.style.display = "none";
      }

    } catch (err) {
      console.error(err);
      alert("Server connection failed");
    }

  });

if (btnClearSession) {
  btnClearSession.addEventListener("click", async () => {
    const ws = getCurrentWorkspaceId("default");
    const base = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");

    try {
      await fetch(`${base}/api/urls/clear?workspace_id=${encodeURIComponent(ws)}`, { method: "POST" });
      await fetch(`${base}/api/draft/clear?workspace_id=${encodeURIComponent(ws)}`, { method: "POST" });
      await fetch(`${base}/api/site/target_pools/active_target_set/clear?workspace_id=${encodeURIComponent(ws)}`, { method: "POST" });
      await fetch(`${base}/api/site/target_pools/rebuild_all?workspace_id=${encodeURIComponent(ws)}`, { method: "POST" });
    } catch (err) {
      console.error("Clear Session backend reset failed:", err);
    }

    localStorage.removeItem("lc_workspace_id");
    localStorage.removeItem("lc_domain");
    window.LINKCRAFTOR_WORKSPACE_ID = "";

    updateConnectionStatus("");

    if (domainInput) {
      domainInput.value = "";
    }

    if (domainModal) {
      domainModal.style.display = "flex";
    }
  });
}

});