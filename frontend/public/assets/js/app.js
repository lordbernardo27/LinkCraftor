 console.log("APP.JS ACTIVE VERSION: ? EDIT CONFIRMED 2025-12-14-AAA");

// ---- COMPAT SHIM: hydrateImportsOnLoad calls reloadFromBackend() in some builds ----
if (typeof window.reloadFromBackend !== "function") {
  window.reloadFromBackend = async function reloadFromBackend(){
    try { await window.loadImportedUrlsLocal?.(); } catch(e) {}
    try {
  const ws = getCurrentWorkspaceId("");




  if (ws) await window.updateUnifiedImportCount?.(ws);
} catch(e) {}
    try {
      return (window.IMPORTED_URLS && window.IMPORTED_URLS.size) ? window.IMPORTED_URLS.size : 0;
    } catch(e) {}
    return 0;
  };
  console.log("[Imports] reloadFromBackend shim installed ");
}
// ---- END SHIM ----


// -------------------------------------------------------------------------------------------
// app.js â€” LinkCraftor (Full, updated)  
// -------------------------------------------------------------------------------------------

import { KEYS, lsGet, lsSet, lsDel } from "./core/storage.js";
import { renderDocInfoPanel as renderDocInfo } from "./sidebar/docinfo.js";
import { initStopwordsUI } from "./ui/stopwords.js";
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
// Layer 1.3 â€“ UI â†’ Decision Ingestion (canonical Layer 0)
// Endpoint: POST /api/engine/decision
// =====================================================
const API_DECISION = "/api/engine/decision";



async function emitDecision(eventType, phraseCtx, candidate, meta){
  try{
    const ws = String(
      (phraseCtx && phraseCtx.workspaceId) ||
      window.LC_WORKSPACE_ID ||
      window.CURRENT_WORKSPACE_ID ||
      getCurrentWorkspaceId("")
    ).trim();
const doc = String((phraseCtx && phraseCtx.docId) || window.LC_ACTIVE_DOC_ID || "doc_demo_001").trim();
const user = String(window.LC_USER_ID || "bernard").trim();

const decisionPayload = {
  phraseText: String(phraseCtx?.phraseText || phraseCtx?.phrase || "").trim(),
  targetId: String(candidate?.id || candidate?.topicId || "").trim(),
  title: String(candidate?.title || "").trim(),
  url: String(candidate?.url || "").trim()
};

const payload = {
  // required by backend model
  workspaceId: ws,
  userId: user,
  docId: doc,
  eventType,

  // required by feedback aggregator
  payload: decisionPayload,

  // diagnostic/debug context
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
// Layer 1.3.1 â€” Global bridge for IL Modal ? Decision API
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
  console.log("[RB2 FETCH START]", `${base}/api/engine/run`);

  const res = await fetch(`${base}/api/engine/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify({
      html: "",
      text: payload?.text || "",
      workspace_id: payload?.workspaceId || payload?.workspace_id || getCurrentWorkspaceId(""),
      workspaceId: payload?.workspaceId || payload?.workspace_id || getCurrentWorkspaceId(""),
      docId: payload?.docId || payload?.doc_id || window.LC_ACTIVE_DOC_ID || "",
      doc_id: payload?.docId || payload?.doc_id || window.LC_ACTIVE_DOC_ID || "",
      limit: payload?.limit || 50,
      targets: []
    })
  });

  console.log("[RB2 FETCH RESPONSE]", { status: res.status, ok: res.ok });

  const rawText = await res.text();
  console.log("[RB2 FETCH TEXT LEN]", rawText.length);

  let data = {};
  try {
    data = JSON.parse(rawText || "{}");
  } catch (e) {
    console.error("[RB2 JSON PARSE FAILED]", rawText.slice(0, 500));
    throw e;
  }

  if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);
  if (!data || data.ok !== true) throw new Error(data?.error || "RB2 backend returned ok:false");

  const out = data || {};
  try { window.__RB2_LAST_OUT = out; } catch (e) {}

  console.log("[RB2 BACKEND OUT JSON]", { ok: out.ok, strong: (out.internal_strong || []).length, optional: (out.semantic_optional || []).length, meta: out.meta || {} });
 
console.log("[RB2 SAMPLE internal_strong[0]]", (out.internal_strong && out.internal_strong[0]) || null);
console.log("[RB2 SAMPLE semantic_optional[0]]", (out.semantic_optional && out.semantic_optional[0]) || null);

try {
  const allPaintCandidates = [
    ...(Array.isArray(out.internal_strong) ? out.internal_strong : []),
    ...(Array.isArray(out.semantic_optional) ? out.semantic_optional : [])
  ];

  console.log("[RB2 URL DIAGNOSTIC ALL]", JSON.stringify(allPaintCandidates.map(x => ({
    phrase: x.phrase || x.phrase_text || x.text || x.label || "",
    bucket: x.bucket || "",
    source: x.source || "",
    best_target_url: x.best_target_url || "",
    best_target_title: x.best_target_title || "",
    resolved_targets: Array.isArray(x.resolved_targets) ? x.resolved_targets.length : 0
  })), null, 2));
} catch (e) {
  console.warn("[RB2 URL DIAGNOSTIC] failed", e);
}

return {
  internal_strong: Array.isArray(out.internal_strong) ? out.internal_strong : [],
  semantic_optional: Array.isArray(out.semantic_optional) ? out.semantic_optional : [],
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
  } catch (e) {
    console.warn("[importCount] set failed:", e);
  }
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

let draftCount = 0;

if (r2.ok) {
  if (typeof d2.count === "number") {
    draftCount = d2.count;
  } else if (Array.isArray(d2.topics)) {
    draftCount = d2.topics.length;
  } else if (d2.topics && typeof d2.topics === "object") {
    draftCount = Object.keys(d2.topics).length;
  }
}


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

// Spacing radius for mark placement (â€”words)
const WINDOW_RADIUS_WORDS = 90;

/* ==========================================================================
   NEW: External V2 (local, rule-based) â€” mirrors internal placement logic
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
// Canonical editor families: .docx | .md | .html | .txt
let SESSION_FORMAT = null;

// All physical extensions accepted by the Uploaded Document backend.
const DEFAULT_DOCUMENT_ACCEPT =
  ".docx,.md,.markdown,.html,.htm,.txt";

// Extract lowercase physical extension (includes leading dot).
function extOf(name = "") {
  return (String(name).match(/\.[^.]+$/)?.[0] || "").toLowerCase();
}

// Convert physical upload aliases into the four editor session families.
// The original filename/extension is NOT modified before backend upload.
function canonicalSessionFormat(ext = "") {
  let value = String(ext || "").trim().toLowerCase();

  if (value && !value.startsWith(".")) {
    value = `.${value}`;
  }

  if (value === ".markdown") return ".md";
  if (value === ".htm") return ".html";

  return value;
}

function acceptListForSession(ext = "") {
  const family = canonicalSessionFormat(ext);

  if (family === ".docx") return ".docx";
  if (family === ".txt") return ".txt";
  if (family === ".md") return ".md,.markdown";
  if (family === ".html") return ".html,.htm";

  return DEFAULT_DOCUMENT_ACCEPT;
}

function uploadMenuSessionFormat(acceptValue = "") {
  const accept = String(acceptValue || "").trim().toLowerCase();

  if (!accept || accept === ".zip,.rar") {
    return "";
  }

  return canonicalSessionFormat(
    accept.split(",")[0] || ""
  );
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

let LAST_ENGINE_OUTPUT = { internal_strong: [], semantic_optional: [], hidden: [], meta: {} };


/* ==========================================================================
   UI HOOKS
   ========================================================================== */
const fileInput = $("file");
const sitemapFile = $("sitemapFile");
const draftFile = $("draftFile");
const btnImportMap = $("btnImportMain"); // ? correct ID in your HTML

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
// Draft + Sitemap Audit (Right Sidebar Card) â€” no new button
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
    Loadingâ€”
  </div>

  <div id="auditList" style="margin-top:10px;">
    <div style="font-size:12px;color:#6b7280;">No items yet.</div>
  </div>

  <div id="auditHint" style="margin-top:10px;font-size:12px;color:#6b7280;">
    Tip: Use the filter to switch between draft gaps and sitemap topics that didnâ€”t match any phrase in this doc.
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

    add(out.internal_strong);
    add(out.semantic_optional);
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

    add(out.internal_strong);
    add(out.semantic_optional);

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
 
  (unmatched.length > limit ? `<div style="opacity:.7;margin-top:6px;">+ ${unmatched.length - limit} moreâ€”</div>` : "");
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
    if (mountEl) mountEl.innerHTML = `<div style="font-size:12px;color:#6b7280;">â€”</div>`;
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
    if (stats) stats.textContent = "Loadingâ€”";

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
    listEl.innerHTML = `<div style="font-size:12px;color:#6b7280;">â€”</div>`;
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
let currentAccept = DEFAULT_DOCUMENT_ACCEPT;

const btnBulkApply = $("btnBulkApply");


// Keep every frontend session-format surface synchronized.
function getSessionFormat(){
  try {
    const raw =
      window.__LC_SESSION_FORMAT__ ||
      SESSION_FORMAT ||
      window.__LC__?.SESSION_FORMAT ||
      localStorage.getItem("lc_session_format") ||
      "";

    return canonicalSessionFormat(raw);
  } catch {
    return canonicalSessionFormat(
      window.__LC_SESSION_FORMAT__ || SESSION_FORMAT || ""
    );
  }
}

function setSessionFormat(ext){
  try {
    const family = canonicalSessionFormat(ext);
    if (!family) return;

    SESSION_FORMAT = family;
    currentAccept = acceptListForSession(family);
    window.__LC_SESSION_FORMAT__ = family;

    window.__LC__ = window.__LC__ || {};
    window.__LC__.SESSION_FORMAT = family;

    try {
      localStorage.setItem("lc_session_format", family);
    } catch {}
  } catch {}
}

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

async function runRB2PipelineAndHighlight(opts = {}) {
  if (window.__LC_RB2_RUNNING === true) {
    console.warn("[RB2] skipped duplicate in-flight run");
    return 0;
  }
  window.__LC_RB2_RUNNING = true;
  try {
  if (!viewerEl) return 0;

  const append        = opts.append !== false;
  const perPassLimit  = opts.perPassLimit || MAX_UNIQUE_PHRASES;
  const silent        = !!opts.silent;

  

  const plainText = viewerEl?.textContent || "";

  const wsId = (() => {
    const domain = String(
      window.LC_CONNECTED_DOMAIN ||
      window.CURRENT_DOMAIN ||
      localStorage.getItem("lc_domain") ||
      ""
    ).trim();

    if (domain) {
      return "ws_" + domain
        .replace(/^https?:\/\//i, "")
        .replace(/^www\./i, "")
        .replace(/\/.*$/, "")
        .replace(/[^a-zA-Z0-9]+/g, "_")
        .replace(/^_+|_+$/g, "")
        .toLowerCase();
    }

    return getCurrentWorkspaceId("");
  })();

 console.log("[RB2 WS CHECK]", {
  wsId,
  localImportedCount: (IMPORTED_URLS instanceof Set) ? IMPORTED_URLS.size : -1,
  localDraftCount: (DRAFT_TOPICS instanceof Map) ? DRAFT_TOPICS.size : -1,
  localPublishedCount: (PUBLISHED_TOPICS instanceof Map) ? PUBLISHED_TOPICS.size : -1
});

  const activeDoc = Array.isArray(docs) ? docs[currentIndex] : null;

  const docId =
    window.LC_ACTIVE_DOC_ID ||
    activeDoc?.doc_id ||
    activeDoc?.docId ||
    activeDoc?.id ||
    (typeof allDocs !== "undefined" && allDocs ? allDocs.value : "") ||
    null;

  if (docId) {
    window.LC_ACTIVE_DOC_ID = docId;
  }

  console.log("[RB2 DOCID CHECK]", {
    docId,
    activeIndex: currentIndex,
    activeDocKeys: activeDoc ? Object.keys(activeDoc) : [],
    dropdownValue: (typeof allDocs !== "undefined" && allDocs) ? allDocs.value : null
  });

  const rootEl = (viewerEl?.querySelector?.(".doc-root")) || viewerEl;

  let html = (rootEl?.innerHTML || "").trim();
  let text = (rootEl?.textContent || "").replace(/\u00A0/g, " ").trim();

  if (!/<p[\s>]/i.test(html) && text) {
    const paras = text.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
    html = paras.map(p => `<p>${escapeHtml(p).replace(/\n/g, "<br>")}</p>`).join("");
  }

// Hydrate URL/topic targets before building RB2 payload.
// Otherwise highlights can appear but links remain empty.
try { await loadImportedUrlsLocal?.(); } catch (e) { console.warn("[RB2 FIX] loadImportedUrlsLocal failed", e); }
try { await loadImportsFromBackend?.(); } catch (e) { console.warn("[RB2 FIX] loadImportsFromBackend failed", e); }
try { rebuildPublishedTopics?.(); } catch (e) { console.warn("[RB2 FIX] rebuildPublishedTopics failed", e); }
try { rebuildTitleUrlDatalists?.(); } catch (e) { console.warn("[RB2 FIX] rebuildTitleUrlDatalists failed", e); }

const urlsFromSet = (IMPORTED_URLS instanceof Set) ? Array.from(IMPORTED_URLS) : [];
const draftFromMap = (DRAFT_TOPICS instanceof Map) ? Array.from(DRAFT_TOPICS.values()) : [];
const publishedFromMap = (PUBLISHED_TOPICS instanceof Map) ? Array.from(PUBLISHED_TOPICS.values()) : [];

  let targets = [];

  if (publishedFromMap.length) {
    targets.push(
      ...publishedFromMap
        .map(t => ({
          url: String(t.url || t.planned_url || t.plannedUrl || "").trim(),
          title: String(t.title || t.working_title || t.workingTitle || "").trim(),
          aliases: Array.isArray(t.aliases) ? t.aliases : [],
          inboundLinks: Number(t.inlinks || t.inboundLinks || 0) || 0
        }))
        .filter(x => x.url && x.title)
    );
  }

  if (draftFromMap.length) {
    targets.push(
      ...draftFromMap
        .map(t => ({
          url: String(t.planned_url || t.url || "").trim(),
          title: String(t.working_title || t.title || "").trim(),
          aliases: Array.isArray(t.aliases) ? t.aliases : [],
          inboundLinks: 0
        }))
        .filter(x => x.title)
    );
  }

  if (!targets.length && urlsFromSet.length) {
    targets = urlsFromSet
      .filter(Boolean)
      .map(u => {
        const url = String(u).trim();
        const slug = url.split("/").filter(Boolean).slice(-1)[0] || url;
        const title = slug.replace(/[-_]/g, " ");
        return { url, title, aliases: [], inboundLinks: 0 };
      });
  }

  const runtimeRoot =
  viewerEl ||
  document.getElementById("doc-content") ||
  document.querySelector("#doc-content .doc-root");

console.log("[RB2 DEBUG viewerEl]", viewerEl);
console.log("[RB2 DEBUG doc-content]", document.getElementById("doc-content"));
console.log("[RB2 DEBUG runtimeRoot]", runtimeRoot);

if (runtimeRoot) {
  console.log("[RB2 DEBUG innerText len]", (runtimeRoot.innerText || "").length);
  console.log("[RB2 DEBUG textContent len]", (runtimeRoot.textContent || "").length);
}

const runtimeHtml =
  runtimeRoot?.innerHTML ||
  html ||
  "";

const runtimeText =
  runtimeRoot?.innerText ||
  runtimeRoot?.textContent ||
  text ||
  "";

const cleanedRuntimeText = String(runtimeText)
  .replace(/\s+/g, " ")
  .trim();

console.log("[RB2 RUNTIME TEXT LENGTH]", cleanedRuntimeText.length);

const payload = {
  workspaceId: wsId,
  docId,
  phase: (window.PHASE || "publish"),
  html: runtimeHtml,
  text: cleanedRuntimeText,
  targets
};

console.log(
  "[RB2 FIX CHECK]",
  "IMPORTED_URLS=",
  IMPORTED_URLS instanceof Set ? IMPORTED_URLS.size : "missing",
  "PUBLISHED_TOPICS=",
  PUBLISHED_TOPICS instanceof Map ? PUBLISHED_TOPICS.size : "missing"
);

console.log("[RB2 PIPELINE] calling apiEngineRun now", {
  highlightEnabled,
  targetsLen: payload?.targets?.length,
  hasHtml: !!(payload?.html && String(payload.html).trim()),
  hasText: !!(payload?.text && String(payload.text).trim())
});

const out = await apiEngineRun(payload);

console.log("[RB2 OUT COUNTS @PAINT]", {
  strong: (out?.internal_strong || []).length,
  optional: (out?.semantic_optional || []).length,
  hid: (out?.hidden || []).length,
  meta: out?.meta || {}
});

unwrapBucketMarksOnly();

const strongOnly = (out.internal_strong || []).map(s => ({
  ...s,
  bucket: "strong"
}));

const appliedStrong = highlightEnabled
  ? applyMarksFromSuggestions(strongOnly, {
      append: false,
      perPassLimit
    })
  : 0;

const optionalOnly = (out.semantic_optional || []).map(s => ({
  ...s,
  bucket: "optional"
}));

const appliedOptional = highlightEnabled
  ? applyMarksFromSuggestions(optionalOnly, {
      append: true,
      perPassLimit
    })
  : 0;

console.log("[HIGHLIGHT APPLIED COUNTS]", {
  strong: appliedStrong || 0,
  optional: appliedOptional || 0
});

cleanupMarksInHeadings(viewerEl);
underlineLinkedPhrases();
updateHighlightBadge();
rebuildEngineHighlightsPanel();

LAST_ENGINE_OUTPUT = {
  internal_strong: out.internal_strong || [],
  semantic_optional: out.semantic_optional || [],
  hidden: out.hidden || [],
  meta: out.meta || {}
};

  try {
    window.LC_LAST_ENGINE_RUN = {
      completed_at: new Date().toISOString(),
      internal_strong_count: (out.internal_strong || []).length,
      semantic_optional_count: (out.semantic_optional || []).length,
      hidden_count: (out.hidden || []).length
    };

    if (typeof window.lcAutosaveWorkspaceSession === "function") {
      window.lcSetAutosaveStatus?.("saving");
      const autosaveResult = await window.lcAutosaveWorkspaceSession("after_engine_run");

      if (autosaveResult && autosaveResult.ok) {
        window.lcSetAutosaveStatus?.("saved");
      } else {
        window.lcSetAutosaveStatus?.("error", autosaveResult);
      }
    }
  } catch (autosaveErr) {
    console.warn("[LinkCraftor Autosave] after engine run failed:", autosaveErr);
    window.lcSetAutosaveStatus?.("error", autosaveErr);
  }



return (appliedStrong || 0) + (appliedOptional || 0);
  } finally {
    window.__LC_RB2_RUNNING = false;
  }
}

// === Auto-Link main button: run engine on CURRENT document ===
btnAutoLinkMain?.addEventListener("click", async () => {
  console.log("[AutoLink] Bulk Auto-Link button clicked");
  highlightsArmed = true;

  if (!docs || !docs.length) {
    showToast(errorBox, "Upload at least one document first.", 2000);
    return;
  }

  try {
    await runRB2PipelineAndHighlight({ append: true });
  } catch (e) {
    console.error("[AutoLink] failed:", e);
    showToast(errorBox, "Auto-Link failed: " + (e?.message || e), 2500);
  }
});

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
// Session format helpers (upload/download lock to one format) â€” COLLISION-SAFE
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
      return canonicalSessionFormat(
        W.__LC__.SESSION_FORMAT ||
        W.__LC_SESSION_FORMAT__ ||
        localStorage.getItem("lc_session_format") ||
        ""
      );
    } catch {
      return canonicalSessionFormat(
        W.__LC__.SESSION_FORMAT ||
        W.__LC_SESSION_FORMAT__ ||
        ""
      );
    }
  }

  function __setSessionFormatNS(ext){
    try{
      const family = canonicalSessionFormat(ext);
      if (!family) return;

      SESSION_FORMAT = family;
      currentAccept = acceptListForSession(family);
      W.__LC_SESSION_FORMAT__ = family;
      W.__LC__.SESSION_FORMAT = family;

      try {
        localStorage.setItem("lc_session_format", family);
      } catch {}

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
      const sess = canonicalSessionFormat(
        __getSessionFormatNS() || ""
      );
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

        // Never show â€”originalâ€” or â€”.htmâ€”
        if (kill.has(extAttr)) { btn.style.display = "none"; return; }

        // If a session format is locked, show only that matching option
        if (sess){
          btn.style.display = allow.has(extAttr) ? "" : "none";
        } else {
          // No session yet ? show everything except killers
          btn.style.display = "";
        }
      }).filter(Boolean);
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
const rxWord = /[\p{L}\p{N}â€”'-]+/gu;
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

    // Collect inline styles from <head> (ignore <link> for nowâ€”canâ€”t fetch local files)
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

  // 2) Escape HTML (so markdown canâ€”t inject raw tags)
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





/* Uploads */
function setAcceptAndOpen(acceptList) {
  const accept = acceptList || DEFAULT_DOCUMENT_ACCEPT;
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
      const requestedFamily = uploadMenuSessionFormat(acc);
      const sessionFamily = canonicalSessionFormat(SESSION_FORMAT || "");

      // Keep zip/rar visible for the separate bulk-import path.
      if (!sessionFamily) {
        btn.style.display = "";
      } else if (
        acc === ".zip,.rar" ||
        acc === "" ||
        requestedFamily === sessionFamily
      ) {
        btn.style.display = "";
      } else {
        btn.style.display = "none";
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
    const requestedFamily = uploadMenuSessionFormat(accept);
    const sessionFamily = canonicalSessionFormat(
      getSessionFormat() || SESSION_FORMAT || ""
    );

    // A locked session accepts physical aliases from the same family.
    if (
      sessionFamily &&
      requestedFamily &&
      accept !== ".zip,.rar" &&
      requestedFamily !== sessionFamily
    ) {
      showToast(
        errorBox,
        `This session is locked to ${sessionFamily} files.`,
        1600
      );
      return;
    }

    const pickerAccept =
      accept === ".zip,.rar"
        ? ".zip,.rar"
        : sessionFamily
          ? acceptListForSession(sessionFamily)
          : (accept || DEFAULT_DOCUMENT_ACCEPT);

    setAcceptAndOpen(pickerAccept);
    hideMenu(uploadMenu, btnUploadMenu);
  });
});

if (downloadMenu) downloadMenu.querySelectorAll("button").forEach(btn=>{
  btn.addEventListener("click", async(e)=>{
    e.stopPropagation();
    hideMenu(downloadMenu, btnDownloadMenu);

    try{
      // Prefer the locked session format; if not set yet, use the buttonâ€”s request
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
fileInput?.addEventListener("change", async () => {
  const fl = fileInput.files;
  if (!fl || !fl.length) return;

  safeSetText(errorBox, "", "error");

  let sessExt = canonicalSessionFormat(
    getSessionFormat()
  );

  const firstExt = canonicalSessionFormat(
    extOf(fl[0]?.name || "")
  );

  if (!sessExt) {
    setSessionFormat(firstExt || ".txt");
    sessExt = getSessionFormat();

    currentAccept = acceptListForSession(sessExt);

    try {
      if (fileInput) {
        fileInput.setAttribute(
          "accept",
          acceptListForSession(sessExt)
        );
      }
    } catch {}

    try {
      if (typeof refreshUploadMenuForSessionFormat === "function") {
        refreshUploadMenuForSessionFormat();
      }
    } catch {}
  }

  let accepted = 0;
  let skipped = 0;

  try {
    for (const file of fl) {
      const ext = canonicalSessionFormat(
        extOf(file?.name || "")
      );

      if (ext !== sessExt) {
        skipped++;
        continue;
      }

      const ws = getCurrentWorkspaceId("");

      const data = await uploadFile(file, ws);

      if (data?.ok === false) {
        throw new Error(
          data?.message || data?.reason || "Upload failed."
        );
      }

      getOrAssignCode(data);
      docs.push(data);
      accepted++;
    }

    if (accepted === 0) {
      const parts = [];

      if (skipped) {
        parts.push(`${skipped} skipped because session is locked to ${sessExt}`);
      }

      showToast(
        errorBox,
        parts.length
          ? parts.join(". ") + "."
          : `No files uploaded â€” session is locked to ${sessExt}.`,
        2600
      );

      return;
    }

    refreshDropdown();
    rebuildTitleIndexFromDocs();
    rebuildPublishedTopics();

    renderDoc(docs.length - 1);

    try {
      window.renderPreview?.(docs[docs.length - 1]);
    } catch {}

    saveState();

    // Phase 1 recovery:
    // Do not block editor display on autosave after upload.
    setTimeout(async () => {
      try {
        if (typeof window.lcAutosaveWorkspaceSession === "function") {
          window.lcSetAutosaveStatus?.("saving");
          const autosaveResult = await window.lcAutosaveWorkspaceSession("after_document_upload");
          if (autosaveResult && autosaveResult.ok) {
            window.lcSetAutosaveStatus?.("saved");
          } else {
            window.lcSetAutosaveStatus?.("error", autosaveResult);
          }
        }
      } catch (autosaveErr) {
        console.warn("[LinkCraftor Autosave] after upload failed:", autosaveErr);
        window.lcSetAutosaveStatus?.("error", autosaveErr);
      }
    }, 0);

    const msgParts = [`Uploaded ${accepted} file(s)`];

    if (duplicates) {
      msgParts.push("File already exists");
    }

    if (skipped) {
      msgParts.push(`${skipped} skipped because not ${sessExt}`);
    }

    showToast(errorBox, msgParts.join(". ") + ".", 2200);
  } catch (e) {
    safeSetText(errorBox, "Upload failed: " + (e?.message || e), "error");
  } finally {
    if (fileInput) fileInput.value = "";
  }
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
    if (highlightsArmed) runRB2PipelineAndHighlight({ append: true });
  } catch (e) {
    console.error("[SITEMAP->BACKEND] failed:", e);
    showToast(errorBox, `Import failed: ${e?.message || e}`, 2200);
  }
});


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
  if (highlightsArmed) runRB2PipelineAndHighlight({ append: true });
  else { underlineLinkedPhrases(); highlightBucketKeywords(); updateHighlightBadge(); rebuildEngineHighlightsPanel(); }
}, 200);


/* ==========================================================================
   EXTERNAL AUTO-LINK ENRICHMENT (backend + 24 providers + logging)
   ========================================================================== */

const EXTERNAL_API_BASE = ""; 
// If your backend is same origin, leave "" and use "/api/..."
// If it's on another port/host, you can change to e.g. "http://localhost:8002"

/**
 * Small helper: resolve a phrase via backend /api/external/runtime/resolve (GET).
 * Backend returns an ARRAY of candidates (or []).
 * Returns { url, providerId, providerLabel, title } or null.
 */



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
btnClearSession?.addEventListener("click", async () => {
  const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
  const ws = getCurrentWorkspaceId("");

     // Clear backend uploaded document session.
  try {
    await fetch(`${API_BASE}/api/files/clear_session?workspace_id=${encodeURIComponent(ws)}`, {
      method: "POST",
    });
  } catch (e) {
    console.warn("[ClearSession] uploaded file session clear failed:", e);
  }

  // Clear backend imported sitemap URLs.
  try {
    await fetch(`${API_BASE}/api/urls/clear?workspace_id=${encodeURIComponent(ws)}`, {
      method: "POST",
    });
  } catch (e) {
    console.warn("[ClearSession] imported URL clear failed:", e);
  }

  // Clear backend draft map imports.
  try {
    await fetch(`${API_BASE}/api/draft/clear?workspace_id=${encodeURIComponent(ws)}`, {
      method: "POST",
    });
  } catch (e) {
    console.warn("[ClearSession] draft clear failed:", e);
  }

  try {
  await loadDraftsFromBackend(ws);
} catch {}

try {
  await loadImportsFromBackend();
} catch {}

try {
  await updateUnifiedImportCount(ws);
} catch {}

try {
  setImportCount(0);
} catch {}

  // Clear frontend imported-memory systems.
  try { IMPORTED_URLS = new Set(); } catch {}
  try { window.IMPORTED_URLS = new Set(); } catch {}
  try { IMPORTED_TOPICS.length = 0; } catch {}
  try { window.LC_IMPORTS = []; } catch {}
  try { window.LC_getImportedTopics = () => []; } catch {}
  try { DRAFT_TOPICS = new Map(); } catch {}
  try { PUBLISHED_TOPICS = new Map(); } catch {}
  try { TITLE_INDEX = new Map(); } catch {}
  try { TITLE_ALIAS_MAP = new Map(); } catch {}

  // Clear loaded editor session.
  try { clearState(); } catch {}
  try { docs.splice(0, docs.length); } catch {}
  try { currentIndex = -1; } catch {}
  try { LAST_ENGINE_OUTPUT = { internal_strong: [], semantic_optional: [], hidden: [], meta: {} }; } catch {}
  try { APPLIED_LINKS = []; } catch {}
  try { LINKED_SET.clear(); } catch {}
  try { LINKED_MAP.clear(); } catch {}
  // Clear UI.
  if (viewerEl) viewerEl.innerHTML = "Upload a document to begin editingâ€¦";
  if (editor) editor.innerHTML = "";

  safeSetText(topMeta, "No document loaded", "topMeta");
  safeSetText(docMeta, "Code: â€”", "docMeta");
  safeSetText(docCountMeta, "Doc 0 of 0", "docCountMeta");

  if (allDocs) allDocs.innerHTML = "<option value=''>All docs</option>";

  try { setImportCount(0); } catch {}
  try { updateImportBadge?.(); } catch {}
  try { updateDocNavButtons(); } catch {}
  try { underlineLinkedPhrases(); } catch {}
  try { highlightBucketKeywords(); } catch {}
  try { updateHighlightBadge(); } catch {}
  try { rebuildEngineHighlightsPanel(); } catch {}
  try { rebuildLinkedPhrasesList(); } catch {}
  try { rebuildRejectionsPanel(); } catch {}

  showToast(errorBox, "Session cleared.", 1600);
  console.log("[ClearSession] completed");
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
   BULK APPLY â€” TURN MARKS INTO UNDERLINED LINKS
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
      "mark.kwd-int, mark.kwd-sem"
    )
  );

  console.log("[BulkApply] DEBUG: total marks found in container:", marks.length);

  let applied = 0;
  let skippedNoHref = 0;
  let skippedNoText = 0;
  let skippedMissingTitle = 0;
  let skippedLowConfidence = 0;
  let skippedSuggestOnly = 0;
  let skippedAutoLinkBlocked = 0;

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
        : "internal");

    const strength = ds.strength || ds.rank || "optional";
    const urlAttr = ds.url || ds.href || "";

    const topicId = ds.topicId || ds.targetId || "";
    const title = ds.title || ds.targetTitle || "";
    const confidence = Number(
      ds.runtimeNormalizedScore ||
      ds.resolverConfidence ||
      ds.score ||
      0
    );

    const suggestOnly =
      String(ds.suggestOnly || "").toLowerCase() === "true";

    const hasAutoLinkFlag =
      String(ds.autoLinkAllowed || "").trim() !== "";

    const autoLinkAllowed =
      String(ds.autoLinkAllowed || "").toLowerCase() === "true";

    console.log(
      `[BulkApply] MARK #${i}: phrase="${phrase}" kind="${kind}" strength="${strength}" urlAttr="${urlAttr}" title="${title}"`
    );

    if (suggestOnly) {
      skippedSuggestOnly++;

      console.log(
        `[BulkApply] MARK #${i}: SKIP (suggest-only) ? phrase="${phrase}"`
      );

      continue;
    }

    if (hasAutoLinkFlag && !autoLinkAllowed) {
      skippedAutoLinkBlocked++;

      console.log(
        `[BulkApply] MARK #${i}: SKIP (auto-link blocked) ? phrase="${phrase}"`
      );

      continue;
    }

    if (!title) {
      skippedMissingTitle++;
      console.log(
        `[BulkApply] MARK #${i}: SKIP (missing title) ? phrase="${phrase}", urlAttr="${urlAttr}"`
      );
      continue;
    }

    if (confidence && confidence < 0.42) {
      skippedLowConfidence++;
      console.log(
        `[BulkApply] MARK #${i}: SKIP (low confidence) ? phrase="${phrase}", confidence="${confidence}"`
      );
      continue;
    }

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
        `[BulkApply] MARK #${i}: SKIP (no href) â€” phrase="${phrase}", kind="${kind}", strength="${strength}", title="${title}"`
      );
      continue;
    }

    const cleanClone = mark.cloneNode(true);
    cleanClone.querySelectorAll(".kw-ctl, .kw-accept, .kw-reject").forEach(el => el.remove());

    const coreNode = cleanClone.querySelector(".kw-core");
    const text = (coreNode?.textContent || cleanClone.textContent || "")
      .replace(/[?????]/g, "")
      .replace(/\s+/g, " ")
      .trim();
    if (!text) {
      skippedNoText++;
      console.log(
        `[BulkApply] MARK #${i}: SKIP (no text) â€” href="${href}", phrase="${phrase}"`
      );
      continue;
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
    if (title) {
      a.title = title;
      a.dataset.title = title;
    }
    if (urlAttr && !a.dataset.url) a.dataset.url = urlAttr;
    if (confidence) a.dataset.runtimeNormalizedScore = String(confidence);

    mark.replaceWith(a);

    // Save applied state + emit LINK_SUGGESTION_ACCEPTED
    try {
      rememberAppliedLink(phrase, topicId, href, title, kind);
    } catch (e) {
      console.warn("[BulkApply] rememberAppliedLink failed", e);
    }

    applied++;

    console.log(
      `[BulkApply] MARK #${i}: APPLY â€” href="${href}", text="${text}"`
    );
  }

  console.log(
    "[BulkApply] SUMMARY (container) â€” applied=%d, skippedNoHref=%d, skippedNoText=%d",
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
 *  2) bulkApplyInContainer(viewerEl)            ? turns marks into <a> links
 *  3) save updated HTML/text back into docs[i]
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

        try {
      if (typeof runPipelineAndHighlight === "function") {
        console.log("[BulkApplyAll] Running highlight pipeline for doc %d", i);
        await runRB2PipelineAndHighlight({ append: true });
      } else {
        console.log("[BulkApplyAll] No highlight pipeline defined, skipping mark generation.");
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
    "[BulkApplyAll] DONE â€” totalApplied=%d, skippedNoHref=%d, skippedNoText=%d",
    totalApplied,
    totalSkippedNoHref,
    totalSkippedNoText
  );
}

/* ------------------------------------------------------------------
 * Button wiring â€” ONE CLICK = BULK APPLY ACROSS ALL DOCS
 * ------------------------------------------------------------------ */

async function handleBulkApplyAllClick() {
  console.log("[BulkApply] Button clicked");

  const currentMarks = viewerEl
    ? viewerEl.querySelectorAll("mark.kwd, mark.kwd-strong, mark.kwd-optional, mark.kwd-int, mark.kwd-sem").length
    : 0;

  if (viewerEl && currentMarks > 0) {
    console.log("[BulkApply] Applying current document marks:", currentMarks);
    const stats = await bulkApplyInContainer(viewerEl);

    try { underlineLinkedPhrases?.(); } catch {}
    try { highlightBucketKeywords?.(); } catch {}
    try { updateHighlightBadge?.(); } catch {}
    try { rebuildEngineHighlightsPanel?.(); } catch {}
    try { rebuildLinkedPhrasesList?.(); } catch {}
    try { LR_rebuild?.(); } catch {}
    try { saveLinkedSet?.(); } catch {}

    console.log("[BulkApply] Current document applied:", stats);
    return stats;
  }

  console.log("[BulkApplyAll] No current marks found; falling back to all-doc bulk apply.");
  const stats = await bulkApplyAllDocs();

  try { underlineLinkedPhrases?.(); } catch {}
  try { highlightBucketKeywords?.(); } catch {}
  try { updateHighlightBadge?.(); } catch {}
  try { rebuildEngineHighlightsPanel?.(); } catch {}

  return stats;
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

// Remove keyword marks around/inside headings (h1â€”h6) so titles are never highlighted
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

function applyMarksFromSuggestions(items = [], opts = {}) {
  const root = document.getElementById("doc-content");
  if (!root) return 0;

  const append = opts.append !== false;
  const perPassLimit = opts.perPassLimit || MAX_UNIQUE_PHRASES;

  if (!append) {
    root.querySelectorAll("mark.kwd").forEach(el => {
      el.replaceWith(document.createTextNode(el.textContent || ""));
    });
    root.normalize();
  }

  let applied = 0;
  const phraseHits = new Map();
  const list = Array.isArray(items) ? items : [];

  for (const item of list) {
    const phrase = String(item?.phrase || "").trim();
    if (!phrase) continue;

    const phraseNorm = norm(phrase);
    if (!phraseNorm) continue;
    if (!shouldHighlightPhrase(phrase)) continue;
    if ((phraseHits.get(phraseNorm) || 0) >= perPassLimit) continue;
    if (getEngineMarkCount() >= MAX_TOTAL_HIGHLIGHTS) break;

    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;

        let p = node.parentNode;
        while (p && p !== root) {
          if (p.nodeType === 1) {
            const tag = p.tagName;
            if (tag === "MARK" || tag === "A" || /^H[1-6]$/.test(tag)) {
              return NodeFilter.FILTER_REJECT;
            }
          }
          p = p.parentNode;
        }

        return NodeFilter.FILTER_ACCEPT;
      }
    });

    let node;
    let matched = false;

    while ((node = walker.nextNode())) {
      const text = node.nodeValue;
      const idx = text.toLowerCase().indexOf(phrase.toLowerCase());
      if (idx === -1) continue;

      const before = text.slice(0, idx);
      const hit = text.slice(idx, idx + phrase.length);
      const after = text.slice(idx + phrase.length);

      const mark = document.createElement("mark");
      mark.className = item.bucket === "strong" ? "kwd kwd-strong" : "kwd kwd-optional";
      mark.dataset.strength = item.bucket === "strong" ? "strong" : "optional";
      mark.dataset.phrase = encodeURIComponent(phraseNorm);

      // Attach resolver target metadata directly to the painted mark.
      // This allows the IL modal, bulk apply, export, and decision layer to read the URL/title.
      const bestTarget =
        Array.isArray(item.resolved_targets) && item.resolved_targets.length
          ? item.resolved_targets[0]
          : (
              item.best_target_url ||
              item.best_target_title ||
              item.target_url ||
              item.target_title ||
              item.url ||
              item.title
            )
              ? {
                  runtime_url: item.best_target_url || item.target_url || item.url || "",
                  title: item.best_target_title || item.target_title || item.title || "",
                  source_type: item.best_target_kind || item.target_kind || item.kind || "internal",
                  document_id: item.best_target_id || item.target_id || item.topic_id || item.topicId || ""
                }
              : null;

      if (bestTarget) {
        mark.setAttribute(
          "data-url",
          bestTarget.runtime_url ||
          bestTarget.url ||
          bestTarget.published_url ||
          bestTarget.placeholder_url ||
          ""
        );

        mark.setAttribute("data-title", bestTarget.title || "");
        mark.setAttribute("data-kind", bestTarget.source_type || "internal");

        mark.setAttribute("data-auto-link-allowed", String(bestTarget.auto_link_allowed === true));
        mark.setAttribute("data-suggest-only", String(bestTarget.suggest_only === true));
        mark.setAttribute("data-confidence-reason", bestTarget.confidence_reason || "");
        mark.setAttribute("data-cluster-confidence-floor", String(bestTarget.cluster_confidence_floor || ""));

        mark.setAttribute(
          "data-topic-id",
          bestTarget.document_id ||
          bestTarget.documentId ||
          bestTarget.topicId ||
          bestTarget.topic_id ||
          bestTarget.targetId ||
          bestTarget.target_id ||
          bestTarget.draftId ||
          bestTarget.draft_id ||
          bestTarget.id ||
          ""
        );
      }

      mark.textContent = hit;

const ctl = document.createElement("span");
ctl.className = "kw-ctl";

const acceptBtn = document.createElement("button");
acceptBtn.type = "button";
acceptBtn.className = "kw-btn kw-accept";
acceptBtn.title = "Accept suggestion";
acceptBtn.textContent = "âœ“";

const rejectBtn = document.createElement("button");
rejectBtn.type = "button";
rejectBtn.className = "kw-btn kw-reject";
rejectBtn.title = "Reject suggestion";
rejectBtn.textContent = "Ã—";

ctl.appendChild(acceptBtn);
ctl.appendChild(rejectBtn);
mark.appendChild(ctl);

      const frag = document.createDocumentFragment();
      if (before) frag.appendChild(document.createTextNode(before));
      frag.appendChild(mark);
      if (after) frag.appendChild(document.createTextNode(after));

      node.parentNode.replaceChild(frag, node);

      applied++;
      phraseHits.set(phraseNorm, (phraseHits.get(phraseNorm) || 0) + 1);
      matched = true;
      break;
    }

    if (!matched) {
      // no-op
    }
  }

  console.log("[PAINTER STABLE] applied =", applied);
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
          <span class="qty" style="font-size:12px;color:#6b7280;">â€” ${r.tier} (Bucket)</span>
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
        <span class="qty" style="font-size:12px;color:#6b7280;">â€” ${tier}</span>
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
    safeSetText(errorBox, "Nothing to download yet â€” upload a document first.", "error");
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
    safeSetText(errorBox, "Nothing to download yet â€” upload a document first.", "error");
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
    safeSetText(errorBox, "Nothing to download yet â€” upload a document first.", "error");
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
    safeSetText(errorBox, "Nothing to download yet â€” upload a document first.", "error");
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
    opt.textContent = r.title ? `${r.title} â€” ${r.domainRoot || r.domain || ""}` : (r.url || "");
    opt.dataset.title = r.title || "";
    opt.dataset.provider = r.domainRoot || r.domain || "";
    extReferences.appendChild(opt);
  }
}

// ==========================================================================
// HEADING CLEANUP â€” remove any marks from H1â€”H6 *and* heading-like <p> tags
// ==========================================================================
function cleanupMarksInHeadings(root) {
  if (!root) return;

  const MARK_SELECTOR =
    "mark.kwd, mark.kwd-strong, mark.kwd-optional," +
    " mark.kwd-external, mark.kwd-int, mark.kwd-sem, mark.kwd-ext";

  // -------------------------------------------------
  // A) Real heading tags: <h1>â€”<h6>
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
  //    <mark class="kwd-â€”"><h1>Heading</h1></mark>
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
  //    <p><strong><span><mark â€”><span class="kw-core">Heading</span>â€”</mark></span></strong></p>
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
      const added = await runRB2PipelineAndHighlight({ append: true, silent: true });
      const nowMarks = getEngineMarkCount();
      const gained = Math.max(0, nowMarks - prevMarks);
      if (!added && gained === 0) break;
      passes += 1;
      prevMarks = nowMarks;
      await delay(30);
    }
  } finally {
    showToast(errorBox, `Apply All (this doc) â€” added ${Math.max(0, getEngineMarkCount() - startMarks)} highlight(s) in ${passes} pass(es).`, 2200);
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
        const added = await runRB2PipelineAndHighlight({
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
      `Apply All (all docs) â€” total added ${totalAdded}.`,
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
  console.log("[DecisionDebug] rememberAppliedLink called", {
    phrase,
    topicId,
    url,
    title,
    kind
  });
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

    // Decision memory: only save ACCEPTED after a link is actually applied.
    try {
      const workspaceId =
        window.LC_WORKSPACE_ID ||
        window.CURRENT_WORKSPACE_ID ||
        getCurrentWorkspaceId("");
      const docId =
        (window.LC_ACTIVE_DOC_ID || null) ||
        (docs && currentIndex >= 0 && docs[currentIndex]
          ? (docs[currentIndex].doc_id || docs[currentIndex].docId || null)
          : null);

      const phraseCtx = {
        workspaceId,
        docId,
        phraseText: phrase,
        sectionType: "BODY",
        intent: "INFO",
        entities: []
      };

      const candidate = {
        id: topicId || "",
        title: title || phrase,
        url: url || "",
        sourceType: kind || "applied",
        isExternal: kind === "external",
        entities: []
      };

      if (typeof emitDecision === "function") {
        emitDecision("LINK_SUGGESTION_ACCEPTED", phraseCtx, candidate, {
          uiControl: "apply-link",
          kind,
          source: "rememberAppliedLink"
        }).catch(e => console.warn("[Decision] accepted emit failed", e));

        try {
          window.LC_ACCEPTED_LINKS = window.LC_ACCEPTED_LINKS || [];
          window.LC_ACCEPTED_LINKS.push({
            phrase,
            topicId,
            url,
            title,
            kind,
            accepted_at: new Date().toISOString()
          });

          if (typeof window.lcAutosaveWorkspaceSession === "function") {
            window.lcAutosaveWorkspaceSession("after_accept_link")
              .then(function(result){
                if (result && result.ok) {
                  window.lcSetAutosaveStatus?.("saved");
                } else {
                  window.lcSetAutosaveStatus?.("error", result);
                }
              })
              .catch(function(err){
                console.warn("[LinkCraftor Autosave] after accept link failed:", err);
                window.lcSetAutosaveStatus?.("error", err);
              });
          }
        } catch (autosaveErr) {
          console.warn("[LinkCraftor Autosave] after accept link setup failed:", autosaveErr);
        }

      }
    } catch (e) {
      console.warn("[Decision] accepted emit setup failed", e);
    }
  }
}

/**
 * Auto-apply all engine suggestions in the CURRENT doc.
 * Includes strong, optional, and external suggestions.
 */
function autoApplyMarksInCurrentDoc() {
  if (!viewerEl) return 0;

  // Use the real anchor-insertion engine.
  // This converts <mark> suggestions into actual <a href="..."> links.
  if (typeof bulkApplyInContainer === "function") {
    bulkApplyInContainer(viewerEl)
      .then((stats) => {
        try { rebuildLinkedPhrasesList?.(); } catch {}
        try { LR_rebuild?.(); } catch {}
        try { saveLinkedSet?.(); } catch {}
        try { updateHighlightBadge?.(); } catch {}
        try { rebuildEngineHighlightsPanel?.(); } catch {}

        console.log("[ApplyLink] autoApplyMarksInCurrentDoc applied:", stats);
      })
      .catch((e) => console.warn("[ApplyLink] bulkApplyInContainer failed", e));

    return 1;
  }

  console.warn("[ApplyLink] bulkApplyInContainer not available");
  return 0;
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
   Uses LAST_ENGINE_OUTPUT only â€” stable and simple.
   ========================================================================== */
function findEngineSuggestionsForPhrase(phrase) {
  const norm = (s) => String(s || "").toLowerCase().trim().replace(/\s+/g, " ");
  const normp = norm(
    typeof phrase === "string"
      ? phrase
      : (
          phrase?.phrase ||
          phrase?.text ||
          phrase?.innerText ||
          ""
        )
  );

  const pool = [
    ...(LAST_ENGINE_OUTPUT?.internal_strong || []),
    ...(LAST_ENGINE_OUTPUT?.semantic_optional || [])
  ];

  const hits = pool
    .filter(x => {
      const anchorText = norm(x.anchor?.text || "");
      return (
        anchorText === normp ||
        normp.includes(anchorText) ||
        anchorText.includes(normp)
      );
    })
    .flatMap(x => {

      // NEW resolver/runtime targets
      const resolved = Array.isArray(x.resolved_targets)
        ? x.resolved_targets
        : [];

      if (resolved.length){
        return resolved.map(t => ({
          title: t.title || "",
          url: (
            t.runtime_url ||
            t.url ||
            t.published_url ||
            t.placeholder_url ||
            ""
          ),
          topicId: t.topicId || t.document_id || t.id || "",
          kind: t.kind || t.source_type || x.kind || "internal",

          // IMPORTANT: modal safety layer depends on these
          resolver_confidence:
            typeof t.runtime_balanced_score === "number"
              ? t.runtime_balanced_score
              : (
                  typeof t.runtime_normalized_score === "number"
                    ? t.runtime_normalized_score
                    : 0
                ),

          runtime_normalized_score:
            typeof t.runtime_normalized_score === "number"
              ? t.runtime_normalized_score
              : 0,

          source_type: t.source_type || "",

          auto_link_allowed: t.auto_link_allowed === true,
          suggest_only: t.suggest_only === true,
          confidence_reason: t.confidence_reason || "",
          cluster_confidence_floor: t.cluster_confidence_floor || "",

          tier: x.bucket === "strong" ? "high" : "mid",

          score:
            typeof t.runtime_balanced_score === "number"
              ? t.runtime_balanced_score
              : (
                  typeof x.finalScore === "number"
                    ? x.finalScore
                    : 0
                )
        }));
      }

      // LEGACY fallback
      return [{
        title:   x.target?.title || "",
        url:     x.target?.url || "",
        topicId: x.target?.topicId || x.target?.id || "",
        kind:    x.target?.kind || x.kind || (x.target?.isExternal ? "external" : "internal"),
        tier:    x.bucket === "strong" ? "high" : "mid",
        score:   typeof x.finalScore === "number" ? x.finalScore : 0
      }];
    });

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

  // Optional hook â€” if you later define window.LC_getPhraseContext,
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
    ...(window.LAST_ENGINE_OUTPUT?.internal_strong || []),
    ...(window.LAST_ENGINE_OUTPUT?.semantic_optional || [])
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
  if (highlightsArmed) runRB2PipelineAndHighlight({ append: true });
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


async function syncActiveDocumentMembership(docId) {
  try {
    if (!docId) return;

    const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
    const ws = getCurrentWorkspaceId("");

    console.log("[ActiveDocSync]", docId);

    await fetch(`${API_BASE}/api/files/active_target_set/save`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        workspace_id: ws,
        active_document_ids: [docId],
        active_upload_ids: [docId],
      }),
    });

  } catch (e) {
    console.warn("[ActiveDocSync] failed:", e);
  }
}

/* ==========================================================================
   RENDERING + SESSION
   ========================================================================== */
function renderDoc(i){
  if (i<0 || i>=docs.length) return;
  currentIndex = i;
  const d = docs[i];
  const activeDocId = d?.doc_id || d?.docId || "";
  window.LC_ACTIVE_DOC_ID = activeDocId;
  syncActiveDocumentMembership(activeDocId);
  const code = getOrAssignCode(d);

  const ext = canonicalSessionFormat(
    (d.ext || "").toLowerCase()
  );
  const safeText = typeof d.text === "string" ? d.text : String(d.text || "");
  const safeHtml = typeof d.html === "string" ? d.html : "";

  if (viewerEl){
    const ext = canonicalSessionFormat(
      (
        d.ext ||
        ((d.filename || "").match(/\.[^.]+$/)?.[0] || "")
      ).toLowerCase()
    );

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
        viewerEl.innerHTML = `<div class="doc-root"><p>Upload a document to begin editingâ€”</p></div>`;
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
        if (viewerEl) viewerEl.innerHTML = `<div class="doc-root"><p>Upload a document to begin editingâ€”</p></div>`;
        safeSetText(topMeta, "File: â€”", "topMeta");
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
            if (viewerEl) viewerEl.innerHTML = `<div class="doc-root"><p>Upload a document to begin editingâ€”</p></div>`;
            safeSetText(topMeta, "File: â€”", "topMeta");
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

function lcInstallDocsSnapshotBridge(){
  try {
    window.LC_getDocsSnapshot = function(){
      try {
        return Array.isArray(docs) ? docs : [];
      } catch(e) {
        return [];
      }
    };

    window.LC_getCurrentDocIndex = function(){
      try {
        return typeof currentIndex === "number" ? currentIndex : 0;
      } catch(e) {
        return 0;
      }
    };
  } catch(e) {}
}

lcInstallDocsSnapshotBridge();

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
function clearState(){
  try { localStorage.removeItem(STORAGE_KEY); } catch {}

  // A cleared editor session must not retain its previous document-format lock.
  try { SESSION_FORMAT = ""; } catch {}
  try { currentAccept = DEFAULT_DOCUMENT_ACCEPT; } catch {}
  try { window.__LC_SESSION_FORMAT__ = ""; } catch {}
  try {
    window.__LC__ = window.__LC__ || {};
    window.__LC__.SESSION_FORMAT = "";
  } catch {}
  try { localStorage.removeItem("lc_session_format"); } catch {}
  try {
    if (fileInput) {
      fileInput.value = "";
      fileInput.setAttribute("accept", DEFAULT_DOCUMENT_ACCEPT);
    }
  } catch {}
  try { refreshUploadMenuForSessionFormat(); } catch {}
}
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
// IMPORTED_URLS storage â€” BACKEND ONLY (localStorage disabled)
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
// Draft Topics â€” BACKEND load on startup
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
      const firstExt = canonicalSessionFormat(
        extOf(docs[0]?.filename || docs[0]?.ext || "")
      );

      if (firstExt) {
        setSessionFormat(firstExt);

        const recoveredFamily = getSessionFormat();

        currentAccept = acceptListForSession(
          recoveredFamily
        );

        fileInput?.setAttribute(
          "accept",
          acceptListForSession(recoveredFamily)
        );

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
      if (highlightsArmed) runRB2PipelineAndHighlight({ append: true });
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


  try {
    if (typeof window.lcAutosaveWorkspaceSession === "function") {
      window.lcSetAutosaveStatus?.("saving");
      const autosaveResult = await window.lcAutosaveWorkspaceSession("after_draft_import");
      if (autosaveResult && autosaveResult.ok) {
        window.lcSetAutosaveStatus?.("saved");
      } else {
        window.lcSetAutosaveStatus?.("error", autosaveResult);
      }
    }
  } catch (autosaveErr) {
    console.warn("[LinkCraftor Autosave] after draft import failed:", autosaveErr);
    window.lcSetAutosaveStatus?.("error", autosaveErr);
  }

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
async function bootExtras() {
  console.log("APP.JS ACTIVE VERSION: HELLO FROM TOP");

  const ws = getCurrentWorkspaceId("");
  if (ws) {
    await updateUnifiedImportCount(ws);
  }

  initRejectionsUI({
    onChange: () => {
      try { LR_rebuild(); } catch {}
      try { rebuildLinkedPhrasesList(); } catch {}
    }
  });

  initLinkedPhrasesUI({
    onUndoPhrase: (phrase) => {
      console.log("[LinkedPhrases] undo phrase:", phrase);
    },
    onChange: () => {
      try { LR_rebuild(); } catch {}
    }
  });

  initLinkResolutionPanel();

  try { rebuildRejectionsPanel(); } catch {}
  try { rebuildLinkedPhrasesList(); } catch {}
}

// =====================================================
// Layer 1.3 â€” Wire ? Accept / ? Reject buttons to /api/engine/decision
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

    // Identify action type
    const isAccept = btn.classList.contains("kw-accept");
    // IMPORTANT:
    // Accept button only opens/reviews the suggestion.
    // It must NOT save LINK_SUGGESTION_ACCEPTED.
    // Final acceptance is saved only when Apply Link / Bulk Apply actually inserts a link.
    if (isAccept) {
      console.log("[Decision] Accept clicked: review/open only; no accepted decision saved yet.");
      return;
    }

    const eventType = "LINK_SUGGESTION_REJECTED";

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

    const workspaceId =
        window.LC_WORKSPACE_ID ||
        window.CURRENT_WORKSPACE_ID ||
        getCurrentWorkspaceId("");
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

    // Candidate (from mark dataset, with fallback metadata lookup)
    const kind = String(mark.getAttribute("data-kind") || "").toLowerCase();

    let url  = String(mark.getAttribute("data-url") || "").trim();
    let title = String(mark.getAttribute("data-title") || "").trim();
    let topicId = String(mark.getAttribute("data-topic-id") || "").trim();

    // If this specific clicked mark has no metadata, search sibling/current marks
    // for the same phrase that may carry resolver metadata.
    if (!url && !title && !topicId) {
      try {
        const samePhraseMarks = Array.from(viewerEl.querySelectorAll("mark.kwd"))
          .filter(m => {
            let mp = "";
            try {
              mp = decodeURIComponent(m.getAttribute("data-phrase") || "").trim();
            } catch {
              mp = String(m.getAttribute("data-phrase") || "").trim();
            }
            return norm(mp) === norm(phrase);
          });

        const metadataMark = samePhraseMarks.find(m =>
          String(m.getAttribute("data-url") || "").trim() ||
          String(m.getAttribute("data-title") || "").trim() ||
          String(m.getAttribute("data-topic-id") || "").trim()
        );

        if (metadataMark) {
          url = String(metadataMark.getAttribute("data-url") || "").trim();
          title = String(metadataMark.getAttribute("data-title") || "").trim();
          topicId = String(metadataMark.getAttribute("data-topic-id") || "").trim();
        }
      } catch (e) {
        console.warn("[Decision] reject metadata fallback failed", e);
      }
    }

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

      try {
        window.LC_REJECTED_LINKS = window.LC_REJECTED_LINKS || [];
        window.LC_REJECTED_LINKS.push({
          phrase,
          topicId,
          url,
          title,
          kind,
          rejected_at: new Date().toISOString()
        });

        if (typeof window.lcAutosaveWorkspaceSession === "function") {
          window.lcSetAutosaveStatus?.("saving");
          const autosaveResult = await window.lcAutosaveWorkspaceSession("after_reject_link");

          if (autosaveResult && autosaveResult.ok) {
            window.lcSetAutosaveStatus?.("saved");
          } else {
            window.lcSetAutosaveStatus?.("error", autosaveResult);
          }
        }
      } catch (autosaveErr) {
        console.warn("[LinkCraftor Autosave] after reject link failed:", autosaveErr);
        window.lcSetAutosaveStatus?.("error", autosaveErr);
      }

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

    try {
      if (typeof window.lcAutosaveWorkspaceSession === "function") {
        window.lcSetAutosaveStatus?.("saving");
        const autosaveResult = await window.lcAutosaveWorkspaceSession("after_sitemap_import");
        if (autosaveResult && autosaveResult.ok) {
          window.lcSetAutosaveStatus?.("saved");
        } else {
          window.lcSetAutosaveStatus?.("error", autosaveResult);
        }
      }
    } catch (autosaveErr) {
      console.warn("[LinkCraftor Autosave] after sitemap import failed:", autosaveErr);
      window.lcSetAutosaveStatus?.("error", autosaveErr);
    }


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
  // LC_CONNECTION_TOGGLE_STATUS_SYNC_6_1
  const connectionDot = document.getElementById("connectionDot");
  const connectionText = document.getElementById("connectionText");
  const connectionSwitch = document.getElementById("btnConnectionSwitch");

  if (!connectionDot || !connectionText) return;

  if (domain) {
    connectionDot.classList.remove("disconnected");
    connectionDot.classList.add("connected");
    connectionText.textContent = "Connected";
    if (connectionSwitch) {
      connectionSwitch.classList.add("is-connected");
      connectionSwitch.setAttribute("aria-pressed", "true");
      connectionSwitch.title = "Disconnect workspace domain";
    }
  } else {
    connectionDot.classList.remove("connected");
    connectionDot.classList.add("disconnected");
    connectionText.textContent = "Disconnected";
    if (connectionSwitch) {
      connectionSwitch.classList.remove("is-connected");
      connectionSwitch.setAttribute("aria-pressed", "false");
      connectionSwitch.title = "Connect workspace domain";
    }
  }
}


function lcMakeNewWorkspaceIdentity(domain, projectName){
  const cleanDomain = String(domain || "")
    .trim()
    .replace(/^https?:\/\//i, "")
    .replace(/^www\./i, "")
    .replace(/\/.*$/, "");

  const base = cleanDomain
    .replace(/[^a-zA-Z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .toLowerCase() || "workspace";

  const now = new Date();
  const stamp =
    now.getFullYear().toString() +
    String(now.getMonth() + 1).padStart(2, "0") +
    String(now.getDate()).padStart(2, "0") +
    "_" +
    String(now.getHours()).padStart(2, "0") +
    String(now.getMinutes()).padStart(2, "0") +
    String(now.getSeconds()).padStart(2, "0");

  const workspaceId = "ws_" + base + "_" + stamp;

  const displayTime =
    now.getFullYear().toString() + "-" +
    String(now.getMonth() + 1).padStart(2, "0") + "-" +
    String(now.getDate()).padStart(2, "0") + " " +
    String(now.getHours()).padStart(2, "0") + ":" +
    String(now.getMinutes()).padStart(2, "0");

  const baseName = String(projectName || "").trim() || cleanDomain;
  const workspaceName = baseName + " - " + displayTime;
  const sessionId = "session_" + base + "_" + stamp;

  return { workspaceId, workspaceName, sessionId, cleanDomain };
}

// ===============================
// DOMAIN CONNECT POPUP
// ===============================

document.addEventListener("DOMContentLoaded", () => {
  const domainModal = document.getElementById("domainModal");
  const domainInput = document.getElementById("domainInput");
  const sitemapInput = document.getElementById("sitemapInput");
  const btnConnectDomain = document.getElementById("btnConnectDomain");
    const workspaceNameInput = document.getElementById("workspaceNameInput");

    const customWorkspaceName = String(
      workspaceNameInput?.value || ""
    ).trim();

  // LC_WORKSPACE_RESTORE_ON_REFRESH_6_9
  const savedWorkspaceId = localStorage.getItem("lc_workspace_id") || "";
  const savedDomain = localStorage.getItem("lc_domain") || "";

  if (savedWorkspaceId) {
    window.LINKCRAFTOR_WORKSPACE_ID = savedWorkspaceId;
    window.CURRENT_WORKSPACE_ID = savedWorkspaceId;
    window.LC_WORKSPACE_ID = savedWorkspaceId;

    updateConnectionStatus(savedDomain);

    if (domainModal) {
      domainModal.style.display = "none";
    }
  } else {
    window.LINKCRAFTOR_WORKSPACE_ID = "";
    window.CURRENT_WORKSPACE_ID = "";
    window.LC_WORKSPACE_ID = "";

    updateConnectionStatus("");

    if (domainModal) {
      domainModal.style.display = "flex";
    }
  }

  if (!btnConnectDomain) {
    console.warn("Connect domain button not found");
    return;
  }

  btnConnectDomain.addEventListener("click", async () => {
    // LC_CONTINUE_ROUTING_PHASE_3_1_DOMAIN_MODE_GUARD
    const selectedWorkspaceMode = String(
      window.LC_WORKSPACE_START_MODE ||
      window.workspaceMode ||
      document.querySelector('input[name="workspaceStartMode"]:checked')?.value ||
      "domain"
    ).trim();

    if (selectedWorkspaceMode === "sitemap") {
      // LC_CONTINUE_ROUTING_PHASE_3_2_3_SITE_URL_MODE
      // LC_NORMALIZE_SITE_URL_3_2_4
      let siteUrl = (sitemapInput?.value || "").trim();

      siteUrl = siteUrl
        .replace(/^https?:\/\//i, "")
        .replace(/^www\./i, "")
        .replace(/\/.*$/g, "")
        .trim();

      siteUrl = siteUrl ? "https://" + siteUrl : "";

      if (!siteUrl) {
        alert("Please enter a site URL");
        return;
      }

      const identity = lcMakeNewWorkspaceIdentity(siteUrl, customWorkspaceName);
      const workspaceId = identity.workspaceId;
      const workspaceName = customWorkspaceName || identity.workspaceName;
      const sessionId = localStorage.getItem("lc_active_session_id_" + workspaceId) || identity.sessionId;

      localStorage.setItem("lc_workspace_id", workspaceId);
      localStorage.setItem("lc_site_url", siteUrl);
      localStorage.setItem("lc_active_session_id_" + workspaceId, sessionId);

      window.LINKCRAFTOR_WORKSPACE_ID = workspaceId;
      window.CURRENT_WORKSPACE_ID = workspaceId;
      window.LC_WORKSPACE_ID = workspaceId;
      window.LC_ACTIVE_SESSION_ID = sessionId;
      window.LC_ACTIVE_SESSION_TITLE = workspaceName;
      window.LC_WORKSPACE_MODE = "sitemap";
      window.LC_SITE_URL = siteUrl;

      try {
        const saveRes = await fetch("/api/workspace/workspace-folder/name", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            workspace_id: workspaceId,
            workspace_name: workspaceName,
            workspace_mode: "sitemap",
            site_url: siteUrl,
            source_type: "site_url"
          })
        });

        const saveData = await saveRes.json().catch(() => ({}));
        if (!saveRes.ok || !saveData.ok) {
          throw new Error(saveData.detail || "Could not save site URL workspace");
        }
      } catch (profileErr) {
        console.warn("[Site URL Workspace] profile save failed:", profileErr);
        alert("Could not create Site URL workspace");
        return;
      }

      // LC_FIX_NON_DOMAIN_WORKSPACE_DISCONNECTED_6_10
      updateConnectionStatus("");

      if (domainModal) {
        domainModal.style.display = "none";
      }

      console.log("[Site URL Workspace] New workspace:", {
        workspaceId,
        workspaceName,
        sessionId,
        siteUrl
      });

      return;
    }

    if (selectedWorkspaceMode === "blank") {
      // LC_CONTINUE_ROUTING_PHASE_3_3_BLANK_MODE

      const identity = lcMakeNewWorkspaceIdentity("blank-workspace", customWorkspaceName);
      const workspaceId = identity.workspaceId;
      const workspaceName = customWorkspaceName || identity.workspaceName;
      const sessionId = localStorage.getItem("lc_active_session_id_" + workspaceId) || identity.sessionId;

      localStorage.setItem("lc_workspace_id", workspaceId);
      localStorage.removeItem("lc_domain");
      localStorage.removeItem("lc_site_url");
      localStorage.setItem("lc_active_session_id_" + workspaceId, sessionId);

      window.LINKCRAFTOR_WORKSPACE_ID = workspaceId;
      window.CURRENT_WORKSPACE_ID = workspaceId;
      window.LC_WORKSPACE_ID = workspaceId;
      window.LC_ACTIVE_SESSION_ID = sessionId;
      window.LC_ACTIVE_SESSION_TITLE = workspaceName;
      window.LC_WORKSPACE_MODE = "blank";
      window.LC_SITE_URL = "";
      window.LC_CONNECTED_DOMAIN = "";
      window.CURRENT_DOMAIN = "";

      try {
        // LC_BLANK_WORKSPACE_CALL_CREATE_ROUTE_3_3_2
        const saveRes = await fetch("/api/workspace/create_blank", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            workspace_id: workspaceId,
            workspace_name: workspaceName,
            session_id: sessionId
          })
        });

        const saveData = await saveRes.json().catch(() => ({}));
        if (!saveRes.ok || !saveData.ok) {
          throw new Error(saveData.detail || "Could not create blank workspace");
        }
      } catch (profileErr) {
        console.warn("[Blank Workspace] create failed:", profileErr);
        alert("Could not create blank workspace");
        return;
      }

      // LC_FIX_NON_DOMAIN_WORKSPACE_DISCONNECTED_6_10
      updateConnectionStatus("");

      if (domainModal) {
        domainModal.style.display = "none";
      }

      console.log("[Blank Workspace] New workspace:", {
        workspaceId,
        workspaceName,
        sessionId
      });

      return;
    }


    if (selectedWorkspaceMode !== "domain") {
      console.log("[Workspace Continue] Non-domain mode selected; domain pipeline skipped:", selectedWorkspaceMode);
      return;
    }

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
          body: JSON.stringify({
            workspace_id: null,
            workspace_name: customWorkspaceName || null,
            workspace_mode: "domain",
            domain,
            site_url: null
          })
        }
      );

      const data = await res.json();

      if (!data.ok) {
        alert("Could not connect domain");
        return;
      }

        const identity = lcMakeNewWorkspaceIdentity(data.domain || domain, customWorkspaceName);

        // Use backend canonical workspace ID for all runtime engines.
        // Do NOT use timestamped identity.workspaceId for RB2/target pools.
        const workspaceId = data.workspace_id;
        const workspaceName = data.workspace_name || customWorkspaceName || identity.workspaceName;
        const sessionId = localStorage.getItem("lc_active_session_id_" + workspaceId) || identity.sessionId;
        const cleanDomain = data.domain || identity.cleanDomain;

        if (!workspaceId) {
          alert("Could not connect domain: missing backend workspace ID");
          return;
        }

        localStorage.setItem("lc_workspace_id", workspaceId);
        localStorage.setItem("lc_domain", cleanDomain);
        // LC_STORE_DOMAIN_WORKSPACE_MODE_1_3
        localStorage.setItem("lc_workspace_mode", "domain");
        localStorage.setItem("lc_active_session_id_" + workspaceId, sessionId);

        window.LINKCRAFTOR_WORKSPACE_ID = workspaceId;
        window.CURRENT_WORKSPACE_ID = workspaceId;
        window.LC_WORKSPACE_ID = workspaceId;
        window.LC_ACTIVE_SESSION_ID = sessionId;
        window.LC_ACTIVE_SESSION_TITLE = workspaceName;
        window.LC_CONNECTED_DOMAIN = cleanDomain;
        window.CURRENT_DOMAIN = cleanDomain;

        // Workspace profile is persisted atomically by
        // /api/site/workspace/connect_domain.

        updateConnectionStatus(cleanDomain);

        if (domainModal) {
          domainModal.style.display = "none";
        }

        console.log("[Domain Connect] New workspace:", {
          workspaceId,
          workspaceName,
          sessionId,
          cleanDomain
        });
    } catch (err) {
      console.error(err);
      alert("Server connection failed");
    }
  });
});
// ===============================




// LC_CONNECTION_TOGGLE_SMALL_POPUP_6_2_FIX
document.addEventListener("DOMContentLoaded", function(){
  const switchBtn = document.getElementById("btnConnectionSwitch");
  const modal = document.getElementById("connectLaterModal");
  const input = document.getElementById("connectLaterDomainInput");
  const cancelBtn = document.getElementById("btnConnectLaterCancel");
  const submitBtn = document.getElementById("btnConnectLaterSubmit");

  function getCurrentWorkspaceIdSafe(){
    return String(
      window.LC_WORKSPACE_ID ||
      window.CURRENT_WORKSPACE_ID ||
      window.LINKCRAFTOR_WORKSPACE_ID ||
      localStorage.getItem("lc_workspace_id") ||
      ""
    ).trim();
  }

  function openConnectLaterModal(){
    if (!modal) return;
    modal.style.display = "flex";
    if (input) {
      input.value = "";
      setTimeout(() => input.focus(), 50);
    }
  }

  function closeConnectLaterModal(){
    if (modal) modal.style.display = "none";
  }

  if (cancelBtn) {
    cancelBtn.addEventListener("click", closeConnectLaterModal);
  }

  if (modal) {
    modal.addEventListener("click", function(e){
      if (e.target === modal) closeConnectLaterModal();
    });
  }

  if (switchBtn) {
    switchBtn.addEventListener("click", function(){
      const currentDomain = String(
        window.LC_CONNECTED_DOMAIN ||
        window.CURRENT_DOMAIN ||
        localStorage.getItem("lc_domain") ||
        ""
      ).trim();

      if (currentDomain) {
        // LC_DOMAIN_WORKSPACE_LOCKED_CONNECTION_1_3
        const currentMode = String(
          window.LC_WORKSPACE_MODE ||
          localStorage.getItem("lc_workspace_mode") ||
          ""
        ).trim().toLowerCase();

        if (currentMode === "domain") {
          alert("This is a Domain Workspace. The domain connection is locked for this workspace type.");
          return;
        }

        // LC_CONNECTION_TOGGLE_DISCONNECT_6_5
        const workspaceId = getCurrentWorkspaceIdSafe();

        if (!workspaceId) {
          alert("No active workspace found.");
          return;
        }

        if (!confirm("Disconnect this domain from the current workspace? Your documents, imports, and drafts will remain.")) {
          return;
        }

        switchBtn.disabled = true;

        fetch("/api/workspace/disconnect_domain", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ workspace_id: workspaceId })
        })
          .then(res => res.json().then(data => ({ ok: res.ok, data })))
          .then(({ ok, data }) => {
            if (!ok || !data.ok) {
              throw new Error(data.detail || "Could not disconnect domain");
            }

            localStorage.removeItem("lc_domain");
            window.LC_CONNECTED_DOMAIN = "";
            window.CURRENT_DOMAIN = "";

            updateConnectionStatus("");
            console.log("[Connect Later] disconnected domain:", data);
          })
          .catch(err => {
            console.error("[Connect Later] disconnect failed:", err);
            alert("Could not disconnect domain.");
          })
          .finally(() => {
            switchBtn.disabled = false;
          });

        return;
      }

      openConnectLaterModal();
    });
  }

  if (submitBtn) {
    submitBtn.addEventListener("click", async function(){
      const workspaceId = getCurrentWorkspaceIdSafe();
      const domain = String(input?.value || "").trim();

      if (!workspaceId) {
        alert("No active workspace found.");
        return;
      }

      if (!domain) {
        alert("Please enter a domain.");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = "Connecting...";

      try {
        const res = await fetch(`${window.LINKCRAFTOR_API_BASE}/api/site/workspace/connect_domain`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            workspace_id: workspaceId,
            domain: domain
          })
        });

        const data = await res.json().catch(() => ({}));

        if (!res.ok || !data.ok) {
          throw new Error(data.error || data.detail || "Could not connect domain");
        }

        const cleanDomain = data.domain || domain;

        localStorage.setItem("lc_domain", cleanDomain);
        window.LC_CONNECTED_DOMAIN = cleanDomain;
        window.CURRENT_DOMAIN = cleanDomain;

        updateConnectionStatus(cleanDomain);
        closeConnectLaterModal();

        console.log("[Connect Later] connected domain:", {
          workspaceId,
          cleanDomain
        });
      } catch (err) {
        console.error("[Connect Later] failed:", err);
        alert("Could not connect domain.");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Connect";
      }
    });
  }
});


// TMS Customer Support Tab Shell
// ===============================
function initSupportTabShell() {
  const supportTab = document.getElementById("supportTab");
  const supportShell = document.getElementById("supportShell");
  const mainArea = document.querySelector(".main-area");
  const allTabs = Array.from(document.querySelectorAll(".tabs .tab"));

  if (!supportTab || !supportShell || !mainArea) {
    console.warn("[TMS] Support tab shell not ready");
    return;
  }

  function setActiveTab(activeTab) {
    allTabs.forEach((tab) => {
      const isActive = tab === activeTab;
      tab.classList.toggle("active", isActive);
      tab.setAttribute("aria-selected", isActive ? "true" : "false");
      tab.setAttribute("tabindex", isActive ? "0" : "-1");
    });
  }

  supportTab.addEventListener("click", () => {
    setActiveTab(supportTab);

    mainArea.hidden = true;
    mainArea.style.display = "none";

    supportShell.hidden = false;
    supportShell.style.display = "block";
    supportShell.style.visibility = "visible";

    window.location.hash = "#/support";
    supportShell.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  const editorTab = allTabs.find((tab) => (tab.textContent || "").trim() === "Editor");
  if (editorTab) {
    editorTab.addEventListener("click", () => {
      setActiveTab(editorTab);

      supportShell.hidden = true;
      supportShell.style.display = "none";

      mainArea.hidden = false;
      mainArea.style.display = "";

      window.location.hash = "#/editor";
    });
  }

  if (window.location.hash === "#/support") {
    supportTab.click();
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initSupportTabShell);
} else {
  initSupportTabShell();
}
// ===============================
// TMS Customer Support Form Submit
// ===============================
function initSupportTicketForm() {
  const form = document.getElementById("supportTicketForm");
  const subjectEl = document.getElementById("supportTicketSubject");
  const categoryEl = document.getElementById("supportTicketCategory");
  const descriptionEl = document.getElementById("supportTicketDescription");
  const statusEl = document.getElementById("supportFormStatus");

  if (!form || !subjectEl || !categoryEl || !descriptionEl || !statusEl) {
    console.warn("[TMS] Support ticket form not ready");
    return;
  }

  const apiBase = window.LINKCRAFTOR_API_BASE || "";

  function setSupportFormStatus(message, type = "") {
    statusEl.textContent = message || "";
    statusEl.classList.remove("ok", "error");
    if (type) statusEl.classList.add(type);
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const subject = subjectEl.value.trim();
    const category = categoryEl.value.trim() || "general";
    const description = descriptionEl.value.trim();

    if (!subject || !description) {
      setSupportFormStatus("Please enter a subject and description.", "error");
      return;
    }

    const payload = {
      subject,
      description,
      category,
      source: "app",
      channel: "web",
      requester_user_id: "user_phase3_validation",
      requester_email: "phase3@example.com",
      requester_name: "Phase 3 Validation",
      workspace_id: getCurrentWorkspaceId(""),
      plan_tier: "starter"
    };

    setSupportFormStatus("Submitting ticket...", "");

    try {
      const res = await fetch(`${apiBase}/api/tms/tickets`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (!res.ok || !data.ok) {
        throw new Error(data?.detail || "Ticket submission failed");
      }

      setSupportFormStatus(`âœ… Ticket submitted successfully: ${data.ticket_number}`, "ok");
      alert(`Ticket submitted successfully: ${data.ticket_number}`);
      form.reset();

      document.dispatchEvent(new CustomEvent("tms:ticket-created", {
        detail: data
      }));
    } catch (err) {
      console.error("[TMS] Ticket submit failed", err);
      setSupportFormStatus(err?.message || "Ticket submission failed.", "error");
    }
  });
}

function bootSupportTicketFormSafe() {
  try {
    initSupportTicketForm();
  } catch (err) {
    console.error("[TMS] Support form boot failed", err);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootSupportTicketFormSafe);
} else {
  bootSupportTicketFormSafe();
}

document.addEventListener("click", (event) => {
  const tab = event.target?.closest?.("#supportTab");
  if (tab) {
    setTimeout(bootSupportTicketFormSafe, 50);
  }
});
// ===============================
// TMS Customer Ticket History
// ===============================
async function loadSupportTicketHistory() {
  const listEl = document.getElementById("supportTicketList");
  if (!listEl) return;

  const apiBase = window.LINKCRAFTOR_API_BASE || "";
  const requesterUserId = "user_phase3_validation";

  listEl.textContent = "Loading tickets...";

  try {
    const res = await fetch(`${apiBase}/api/tms/customers/${encodeURIComponent(requesterUserId)}/tickets`);
    const data = await res.json();

    if (!res.ok || !data.ok) {
      throw new Error(data?.detail || "Could not load tickets");
    }

    if (!data.tickets || data.tickets.length === 0) {
      listEl.innerHTML = `<div class="support-empty">No support tickets yet.</div>`;
      return;
    }

    listEl.innerHTML = data.tickets.map((ticket) => `
      <button class="support-ticket-item" type="button" data-ticket-id="${ticket.ticket_id}">
        <div class="support-ticket-main">
          <strong>${ticket.ticket_number || ticket.ticket_id}</strong>
          <span>${ticket.subject || "Untitled ticket"}</span>
        </div>
        <div class="support-ticket-meta">
          <span>${ticket.status || "new"}</span>
          <span>${ticket.priority || "normal"}</span>
        </div>
      </button>
    `).join("");
  } catch (err) {
    console.error("[TMS] Failed to load support tickets", err);
    listEl.innerHTML = `<div class="support-error">Could not load support tickets.</div>`;
  }
}

document.addEventListener("click", (event) => {
  const tab = event.target?.closest?.("#supportTab");
  if (tab) {
    setTimeout(loadSupportTicketHistory, 80);
  }
});

document.addEventListener("tms:ticket-created", () => {
  loadSupportTicketHistory();
});
// ===============================
// TMS Customer Ticket History Boot Fix
// ===============================
function bootSupportTicketHistorySafe() {
  try {
    if (typeof loadSupportTicketHistory === "function") {
      loadSupportTicketHistory();
    }
  } catch (err) {
    console.error("[TMS] Ticket history boot failed", err);
  }
}

document.addEventListener("click", (event) => {
  const tab = event.target?.closest?.("#supportTab");
  if (tab) {
    setTimeout(bootSupportTicketHistorySafe, 150);
  }
});

window.addEventListener("hashchange", () => {
  if (window.location.hash === "#/support") {
    setTimeout(bootSupportTicketHistorySafe, 150);
  }
});

document.addEventListener("DOMContentLoaded", () => {
  if (window.location.hash === "#/support") {
    setTimeout(bootSupportTicketHistorySafe, 200);
  }
});

document.addEventListener("tms:ticket-created", () => {
  setTimeout(bootSupportTicketHistorySafe, 150);
});
// ===============================
// TMS Customer Ticket Thread Viewer
// ===============================
async function loadSupportTicketThread(ticketId) {
  const threadEl = document.getElementById("supportThreadView");
  if (!threadEl || !ticketId) return;

  const apiBase = window.LINKCRAFTOR_API_BASE || "";
  const requesterUserId = "user_phase3_validation";

  threadEl.textContent = "Loading ticket thread...";

  try {
    const res = await fetch(
      `${apiBase}/api/tms/customers/${encodeURIComponent(requesterUserId)}/tickets/${encodeURIComponent(ticketId)}`
    );
    const data = await res.json();

    if (!res.ok || !data.ok) {
      throw new Error(data?.detail || "Could not load ticket thread");
    }

    const ticket = data.ticket || {};
    const messages = data.messages || [];

    const messageHtml = messages.length
      ? messages.map((message) => `
          <div class="support-thread-message">
            <div class="support-thread-message-meta">
              <strong>${message.author_type || "message"}</strong>
              <span>${message.created_at || ""}</span>
            </div>
            <div class="support-thread-message-body">
              ${message.body || ""}
            </div>
          </div>
        `).join("")
      : `<div class="support-empty">No messages yet.</div>`;

    threadEl.innerHTML = `
      <div class="support-thread-header">
        <div>
          <strong>${ticket.ticket_number || ticket.ticket_id}</strong>
          <h3>${ticket.subject || "Untitled ticket"}</h3>
        </div>
        <div class="support-thread-badges">
          <span>${ticket.status || "new"}</span>
          <span>${ticket.priority || "normal"}</span>
          <span>${ticket.severity || "minor"}</span>
        </div>
      </div>

      <div class="support-thread-description">
        ${ticket.description || ""}
      </div>

      <div class="support-thread-messages">
        ${messageHtml}
      </div>

      <form id="supportReplyForm" class="support-reply-form" data-ticket-id="${ticket.ticket_id}">
        <label>
          Reply
          <textarea id="supportReplyBody" rows="4" placeholder="Write your reply..." required></textarea>
        </label>
        <button class="primary" type="submit">Send Reply</button>
        <div id="supportReplyStatus" class="support-form-status" aria-live="polite"></div>
      </form>
    `;
  } catch (err) {
    console.error("[TMS] Failed to load ticket thread", err);
    threadEl.innerHTML = `<div class="support-error">Could not load ticket thread.</div>`;
  }
}

document.addEventListener("click", (event) => {
  const item = event.target?.closest?.(".support-ticket-item");
  if (!item) return;

  const ticketId = item.getAttribute("data-ticket-id");
  if (!ticketId) return;

  document.querySelectorAll(".support-ticket-item").forEach((el) => {
    el.classList.toggle("active", el === item);
  });

  loadSupportTicketThread(ticketId);
});
// ===============================
// TMS Ticket Thread Click Fix
// ===============================
function bootSupportTicketThreadClickFix() {
  const listEl = document.getElementById("supportTicketList");
  const threadEl = document.getElementById("supportThreadView");

  if (!listEl || !threadEl) {
    console.warn("[TMS] Thread click fix not ready");
    return;
  }

  if (listEl.dataset.threadClickBound === "1") return;
  listEl.dataset.threadClickBound = "1";

  listEl.addEventListener("click", async (event) => {
    const item = event.target.closest(".support-ticket-item");
    if (!item) return;

    const ticketId = item.dataset.ticketId;
    if (!ticketId) {
      threadEl.innerHTML = `<div class="support-error">Ticket ID missing.</div>`;
      return;
    }

    document.querySelectorAll(".support-ticket-item").forEach((el) => {
      el.classList.toggle("active", el === item);
    });

    if (typeof loadSupportTicketThread === "function") {
      await loadSupportTicketThread(ticketId);
    } else {
      threadEl.innerHTML = `<div class="support-error">Thread loader not found.</div>`;
    }
  });

  console.log("[TMS] Ticket thread click fix bound");
}

document.addEventListener("click", (event) => {
  if (event.target?.closest?.("#supportTab")) {
    setTimeout(bootSupportTicketThreadClickFix, 250);
  }
});

document.addEventListener("tms:ticket-created", () => {
  setTimeout(bootSupportTicketThreadClickFix, 250);
});

setTimeout(bootSupportTicketThreadClickFix, 500);
// ===============================
// TMS Customer Reply Composer
// ===============================
function initSupportReplyComposer() {
  document.addEventListener("submit", async (event) => {
    const form = event.target;
    if (!form || form.id !== "supportReplyForm") return;

    event.preventDefault();

    const ticketId = form.getAttribute("data-ticket-id");
    const bodyEl = document.getElementById("supportReplyBody");
    const statusEl = document.getElementById("supportReplyStatus");

    if (!ticketId || !bodyEl || !statusEl) return;

    const body = bodyEl.value.trim();
    if (!body) {
      statusEl.textContent = "Please enter a reply.";
      statusEl.classList.remove("ok");
      statusEl.classList.add("error");
      return;
    }

    const apiBase = window.LINKCRAFTOR_API_BASE || "";
    const requesterUserId = "user_phase3_validation";

    statusEl.textContent = "Sending reply...";
    statusEl.classList.remove("ok", "error");

    try {
      const res = await fetch(
        `${apiBase}/api/tms/customers/${encodeURIComponent(requesterUserId)}/tickets/${encodeURIComponent(ticketId)}/messages`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            body,
            author_type: "customer",
            author_id: requesterUserId,
            is_customer_visible: true
          })
        }
      );

      const data = await res.json();

      if (!res.ok || !data.ok) {
        throw new Error(data?.detail || "Could not send reply");
      }

      statusEl.textContent = "Reply sent.";
      statusEl.classList.add("ok");
      bodyEl.value = "";

      if (typeof loadSupportTicketThread === "function") {
        await loadSupportTicketThread(ticketId);
      }

      if (typeof loadSupportTicketHistory === "function") {
        await loadSupportTicketHistory();
      }
    } catch (err) {
      console.error("[TMS] Reply failed", err);
      statusEl.textContent = err?.message || "Could not send reply.";
      statusEl.classList.add("error");
    }
  });
}

if (!window.__tmsReplyComposerBound) {
  window.__tmsReplyComposerBound = true;
  initSupportReplyComposer();
}







// =====================================================
// Rebuild Governance
// Automatic stale sweep every 3 minutes
// =====================================================

(function initRebuildGovernanceSweep() {

  if (window.__LC_REBUILD_SWEEP_STARTED) {
    return;
  }

  window.__LC_REBUILD_SWEEP_STARTED = true;

  async function runSweep() {

    try {

      const ws = getCurrentWorkspaceId("");

      if (!ws) {
        return;
      }

      const API_BASE =
        (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001")
        .replace(/\/+$/, "");

      await fetch(
        `${API_BASE}/api/rebuild/sweep/${encodeURIComponent(ws)}`,
        {
          method: "POST"
        }
      );

      await fetch(
        `${API_BASE}/api/rebuild/process/${encodeURIComponent(ws)}?limit=20`,
        {
          method: "POST"
        }
      );

    } catch (e) {
      console.warn(
        "[REBUILD_SWEEP]",
        e?.message || e
      );
    }

  }

  runSweep();

  setInterval(
    runSweep,
    180000
  );

})();



// =====================================================
// Reload Governance
// Automatic frontend reload orchestrator
// =====================================================

(function initReloadGovernanceOrchestrator() {

  if (window.__LC_RELOAD_ORCHESTRATOR_STARTED) {
    return;
  }

  window.__LC_RELOAD_ORCHESTRATOR_STARTED = true;

  async function executeReloadActions(source = "reload_governance", layers = null) {

    try {
      const ws = getCurrentWorkspaceId("default");

      const requestedLayers = layers && typeof layers === "object" ? layers : {};
      const hasLayer = (name) => {
        if (!requestedLayers || !Object.keys(requestedLayers).length) return true;
        return !!requestedLayers[name];
      };

      if (hasLayer("backend_state_reload")) {
        try {
          if (typeof window.__LC_reloadFromBackend === "function") {
            await window.__LC_reloadFromBackend();
          } else if (typeof window.reloadFromBackend === "function") {
            await window.reloadFromBackend();
          }
        } catch (e) {
          console.warn("[RELOAD_GOVERNANCE] backend_state_reload failed", e?.message || e);
        }
      }

      if (hasLayer("runtime_refresh")) {
        try {
          if (typeof loadImportsFromBackend === "function") {
            await loadImportsFromBackend();
          }
        } catch (e) {
          console.warn("[RELOAD_GOVERNANCE] loadImportsFromBackend failed", e?.message || e);
        }

        try {
          if (typeof loadDraftsFromBackend === "function") {
            await loadDraftsFromBackend(ws);
          }
        } catch (e) {
          console.warn("[RELOAD_GOVERNANCE] loadDraftsFromBackend failed", e?.message || e);
        }
      }

      if (hasLayer("panel_refresh")) {
        try {
          if (typeof refreshDropdown === "function") {
            refreshDropdown();
          }
        } catch (e) {
          console.warn("[RELOAD_GOVERNANCE] refreshDropdown failed", e?.message || e);
        }
      }

      if (hasLayer("highlight_repaint")) {
        try {
          if (typeof underlineLinkedPhrases === "function") {
            underlineLinkedPhrases();
          }
        } catch (e) {
          console.warn("[RELOAD_GOVERNANCE] underlineLinkedPhrases failed", e?.message || e);
        }

        try {
          if (typeof highlightBucketKeywords === "function") {
            highlightBucketKeywords();
          }
        } catch (e) {
          console.warn("[RELOAD_GOVERNANCE] highlightBucketKeywords failed", e?.message || e);
        }
      }

      if (hasLayer("panel_refresh")) {
        try {
          if (typeof rebuildEngineHighlightsPanel === "function") {
            rebuildEngineHighlightsPanel();
          }
        } catch (e) {
          console.warn("[RELOAD_GOVERNANCE] rebuildEngineHighlightsPanel failed", e?.message || e);
        }
      }

      window.__LC_LAST_RELOAD_GOVERNANCE_RUN = {
        source,
        workspace_id: ws,
        ran_at: new Date().toISOString()
      };

    } catch (e) {
      console.warn("[RELOAD_GOVERNANCE] reload orchestrator failed", e?.message || e);
    }

  }

  window.__LC_executeReloadGovernance = executeReloadActions;

})();



// =====================================================
// Reload Governance State Poller
// =====================================================

(function initReloadGovernancePoller() {

  if (window.__LC_RELOAD_POLLER_STARTED) {
    return;
  }

  window.__LC_RELOAD_POLLER_STARTED = true;

  async function checkReloadState() {

    try {

      const ws = getCurrentWorkspaceId("");

      if (!ws) {
        return;
      }

      const API_BASE =
        (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001")
        .replace(/\/+$/, "");

      const res = await fetch(
        `${API_BASE}/api/reload/state/${encodeURIComponent(ws)}`
      );

      if (!res.ok) {
        return;
      }

      const data = await res.json();

      const lastReloadAt =
        data?.state?.last_reload_at || null;

      if (!lastReloadAt) {
        return;
      }

      const lastProcessed =
        window.__LC_LAST_RELOAD_STATE_PROCESSED || null;

      if (lastProcessed === lastReloadAt) {
        return;
      }

      window.__LC_LAST_RELOAD_STATE_PROCESSED = lastReloadAt;

      const layers = data?.state?.layers || {};

      if (typeof window.__LC_executeReloadGovernance === "function") {
        await window.__LC_executeReloadGovernance(
          "reload_state_poller",
          layers
        );
      }

    } catch (e) {
      console.warn(
        "[RELOAD_STATE_POLLER]",
        e?.message || e
      );
    }

  }

  checkReloadState();

  setInterval(
    checkReloadState,
    180000
  );

})();



// =====================================================
// Profile Logout / Hard Workspace Disconnect
// =====================================================

(function initProfileLogoutHardDisconnect() {
  document.addEventListener("DOMContentLoaded", () => {
    const profileBtn = document.getElementById("profileMenuBtn");
    const profileDropdown = document.getElementById("profileDropdown");
    const logoutBtn = document.getElementById("btnProfileLogout");

    if (!profileBtn || !profileDropdown || !logoutBtn) {
      return;
    }

    profileBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      profileDropdown.style.display =
        profileDropdown.style.display === "none" || !profileDropdown.style.display
          ? "block"
          : "none";
    });

    document.addEventListener("click", (e) => {
      if (!profileDropdown.contains(e.target) && !profileBtn.contains(e.target)) {
        profileDropdown.style.display = "none";
      }
    });

    logoutBtn.addEventListener("click", async () => {
      const API_BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");
      const ws = getCurrentWorkspaceId("");

        try {
          if (typeof window.lcAutosaveWorkspaceSession === "function") {
            window.lcSetAutosaveStatus?.("saving");

            const autosaveResult =
              await window.lcAutosaveWorkspaceSession("before_logout_final_autosave");

            if (autosaveResult && autosaveResult.ok) {
              window.lcSetAutosaveStatus?.("saved");
              console.log("[Logout] Final autosave completed");
            } else {
              console.warn("[Logout] Final autosave returned failure", autosaveResult);
              window.lcSetAutosaveStatus?.("error", autosaveResult);
              showToast?.(errorBox, "Logout stopped: final autosave failed.", 2600);
              return;
            }
          }
        } catch (autosaveErr) {
          console.warn("[Logout] Final autosave failed", autosaveErr);
          window.lcSetAutosaveStatus?.("error", autosaveErr);
          showToast?.(errorBox, "Logout stopped: final autosave failed.", 2600);
          return;
        }



      const domainModal = document.getElementById("domainModal");
      const domainInput = document.getElementById("domainInput");

      if (profileDropdown) {
        profileDropdown.style.display = "none";
      }

      if (ws) {
        try {
          await fetch(`${API_BASE}/api/files/clear_session?workspace_id=${encodeURIComponent(ws)}`, {
            method: "POST",
          });
        } catch (e) {
          console.warn("[Logout] file session clear failed:", e?.message || e);
        }

        try {
          await fetch(`${API_BASE}/api/urls/clear?workspace_id=${encodeURIComponent(ws)}`, {
            method: "POST",
          });
        } catch (e) {
          console.warn("[Logout] URL clear failed:", e?.message || e);
        }

        try {
          await fetch(`${API_BASE}/api/draft/clear?workspace_id=${encodeURIComponent(ws)}`, {
            method: "POST",
          });
        } catch (e) {
          console.warn("[Logout] draft clear failed:", e?.message || e);
        }
      }

      try { localStorage.removeItem("lc_domain"); } catch {}
      try { localStorage.removeItem("lc_workspace_id"); } catch {}

      window.LINKCRAFTOR_WORKSPACE_ID = "";
      window.CURRENT_WORKSPACE_ID = "";
      window.LC_WORKSPACE_ID = "";
      window.LC_ACTIVE_DOC_ID = "";

        // LC_LOGOUT_HARD_RESET_PATCH_V1
        try { if (ws) localStorage.removeItem("lc_active_session_id_" + ws); } catch {}
        try { localStorage.removeItem("workspace_id"); } catch {}

        window.LC_ACTIVE_SESSION_ID = "";
        window.LC_ACTIVE_SESSION_TITLE = "";
        window.LC_CONNECTED_DOMAIN = "";
        window.CURRENT_DOMAIN = "";

        try { clearState(); } catch {}
        try { docs.splice(0, docs.length); } catch {}
        try { currentIndex = -1; } catch {}

        try {
          if (viewerEl) {
            viewerEl.innerHTML = "<div class='doc-root'><p>Upload a document to begin editing...</p></div>";
          }
        } catch {}

        try {
          if (editor) editor.innerHTML = "";
        } catch {}

        try {
          if (allDocs) allDocs.innerHTML = "<option value=''>All docs</option>";
        } catch {}

        try { safeSetText(topMeta, "No document loaded", "topMeta"); } catch {}
        try { safeSetText(docMeta, "Code: ?", "docMeta"); } catch {}
        try { safeSetText(docCountMeta, "Doc 0 of 0", "docCountMeta"); } catch {}

      try { IMPORTED_URLS = new Set(); } catch {}
      try { DRAFT_TOPICS = []; } catch {}
      try { LAST_ENGINE_OUTPUT = null; } catch {}
      try { window.__LC_LAST_RELOAD_STATE_PROCESSED = null; } catch {}

      try {
        if (typeof setImportCount === "function") {
          setImportCount(0);
        } else {
          const importCount = document.getElementById("importCount");
          if (importCount) importCount.textContent = "0";
        }
      } catch {}

      try {
        const panelIds = [
          "detectedKeywords",
          "linkSuggestions",
          "unmatchedTopics",
          "engineHighlightsPanel",
          "draftTopicsPanel"
        ];

        for (const id of panelIds) {
          const el = document.getElementById(id);
          if (el) el.innerHTML = "";
        }
      } catch {}

      try {
        document.querySelectorAll("mark.kwd, mark[data-phrase]").forEach((mark) => {
          const text = document.createTextNode(mark.textContent || "");
          mark.replaceWith(text);
        });
      } catch {}

      try {
        if (typeof updateConnectionStatus === "function") {
          updateConnectionStatus("");
        }
      } catch {}

      if (domainInput) {
        domainInput.value = "";
      }

      if (domainModal) {
        domainModal.style.display = "flex";
      }

      console.log("[Logout] Hard workspace disconnect complete. Domain reconnect required.");
    });
  });
})();


// ============================================================
// LinkCraftor Workspace Autosave Engine
// Phase 3.1: Base autosave function
// ============================================================

window.LC_AUTOSAVE_STATE = window.LC_AUTOSAVE_STATE || {
  lastSavedAt: null,
  saving: false,
  lastError: null
};

function lcGetAutosaveWorkspaceId(){
  try {
    return (
      window.LC_WORKSPACE_ID ||
      window.CURRENT_WORKSPACE_ID ||
      (typeof getCurrentWorkspaceId === "function" ? getCurrentWorkspaceId("") : "") ||
      ""
    );
  } catch(e) {
    return "";
  }
}

function lcGetAutosaveSessionId(){
  try {
    if (window.LC_ACTIVE_SESSION_ID) return window.LC_ACTIVE_SESSION_ID;

    const ws = lcGetAutosaveWorkspaceId();
    const key = "lc_active_session_id_" + ws;
    let existing = localStorage.getItem(key);

    if (!existing) {
      existing = "autosave_" + new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14);
      localStorage.setItem(key, existing);
    }

    window.LC_ACTIVE_SESSION_ID = existing;
    return existing;
  } catch(e) {
    return "autosave_fallback_session";
  }
}

function lcGetEditorSnapshot(){
  const editor =
    document.querySelector("#editor") ||
    document.querySelector(".ql-editor") ||
    document.querySelector("[contenteditable='true']");

  const html = editor ? editor.innerHTML : "";
  const text = editor ? editor.innerText : "";

  return {
    document_id: window.LC_ACTIVE_DOCUMENT_ID || window.ACTIVE_DOCUMENT_ID || "active_document",
    title: window.LC_ACTIVE_DOCUMENT_TITLE || document.title || "Untitled Document",
    filename: window.LC_ACTIVE_DOCUMENT_FILENAME || "",
    html: html,
    text: text,
    metadata: {
      source: "frontend_autosave",
      captured_at: new Date().toISOString()
    }
  };
}




function lcFixMojibakeText(value){
  let text = String(value || "");

  const replacements = [
    ["\u00e2\u20ac\u201d", "\u2014"],
    ["\u00e2\u20ac\u201c", "\u2013"],
    ["\u00e2\u20ac\u02dc", "\u2018"],
    ["\u00e2\u20ac\u2122", "\u2019"],
    ["\u00e2\u20ac\u0153", "\u201c"],
    ["\u00e2\u20ac\u009d", "\u201d"],
    ["\u00e2\u20ac\u00a6", "\u2026"],
    ["\u00c2\u00a0", " "],
    ["\u00c2", ""]
  ];

  for (const pair of replacements) {
    text = text.split(pair[0]).join(pair[1]);
  }

  return text;
}

function lcGetAutosaveDocumentsSnapshot(){
  try {
    const docsSource = (typeof window.LC_getDocsSnapshot === "function") ? window.LC_getDocsSnapshot() : [];
    if (Array.isArray(docsSource) && docsSource.length) {
      return docsSource.map(function(d, index){
        const rawText = lcFixMojibakeText(d.text || "").trim();
        const rawHtml = lcFixMojibakeText(d.html || "").trim();

        const isPlaceholder =
          rawText === "Upload a document to begin editing?" ||
          rawText === "Upload a document to begin editing?" ||
          rawHtml.includes("Upload a document to begin editing");

        if (isPlaceholder) return null;

        const id = d.doc_id || d.docId || d.document_id || ("doc_" + (index + 1));
        return {
          document_id: id,
          doc_id: id,
          docId: id,
          title: lcFixMojibakeText(d.title || d.filename || ("Document " + (index + 1))),
          filename: lcFixMojibakeText(d.filename || ""),
          ext: d.ext || ((d.filename || "").match(/\.[^.]+$/)?.[0] || ""),
          html: rawHtml,
          text: rawText,
          metadata: d.metadata || {},
          code: d.code || d.shortCode || ""
        };
      });
    }

    const fallback = lcGetEditorSnapshot();

    const isPlaceholder =
      String(fallback.text || "").trim() === "Upload a document to begin editing?" ||
      String(fallback.text || "").trim() === "Upload a document to begin editing?";

    if (isPlaceholder) {
      return [];
    }

    return [fallback];
  } catch(e) {
    return [];
  }
}

function lcAutosaveArray(value){
  try {
    if (!value) return [];
    if (Array.isArray(value)) return value;
    if (value instanceof Set) return Array.from(value).map(function(item){
      if (typeof item === "string") return { url: item };
      return item;
    });
    if (value instanceof Map) return Array.from(value.values());
    if (typeof value === "object") return Object.values(value);
    return [];
  } catch(e) {
    return [];
  }
}

async function lcAutosaveWorkspaceSession(reason){

  const autosaveWorkspaceId = String(
    window.LC_WORKSPACE_ID ||
    window.currentWorkspaceId ||
    localStorage.getItem("lc_workspace_id") ||
    localStorage.getItem("workspace_id") ||
    ""
  ).trim();

  if (
    !autosaveWorkspaceId ||
    autosaveWorkspaceId === "default" ||
    autosaveWorkspaceId === "null" ||
    autosaveWorkspaceId === "undefined"
  ) {
    console.debug(
      "[LinkCraftor Autosave] skipped: workspace_id unavailable"
    );

    return {
      ok: true,
      skipped: true,
      reason: "workspace_id_unavailable",
    };
  }

  if (window.LC_AUTOSAVE_STATE.saving) {
    return {
      ok: false,
      skipped: true,
      reason: "autosave_already_running"
    };
  }

  window.LC_AUTOSAVE_STATE.saving = true;
  window.LC_AUTOSAVE_STATE.lastError = null;

  try {
    const ws = lcGetAutosaveWorkspaceId();
    const sessionId = lcGetAutosaveSessionId();
    const autosaveDocuments = lcGetAutosaveDocumentsSnapshot();
    const doc = autosaveDocuments[0] || lcGetEditorSnapshot();

    const payload = {
      workspace_id: ws,
      session_id: sessionId,
      domain: window.LC_CONNECTED_DOMAIN || window.CURRENT_DOMAIN || "",
      title: window.LC_ACTIVE_SESSION_TITLE || "Autosaved Workspace Session",
      active_document_id: doc.document_id,
      documents: autosaveDocuments,
      imported_urls: lcAutosaveArray(window.IMPORTED_URLS || window.LC_IMPORTED_URLS),
      draft_topics: lcAutosaveArray(window.DRAFT_TOPICS || window.LC_DRAFT_TOPICS),
      engine_state: {
        reason: reason || "manual_autosave",
        last_engine_run: window.LC_LAST_ENGINE_RUN || null,
        accepted_links: lcAutosaveArray(window.LC_ACCEPTED_LINKS),
        rejected_links: lcAutosaveArray(window.LC_REJECTED_LINKS),
        manual_links: lcAutosaveArray(window.LC_MANUAL_LINKS)
      },
      decisions: lcAutosaveArray(window.LC_LINK_DECISIONS)
    };

    const res = await fetch("/api/workspace/autosave", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok || !data.ok) {
      throw new Error(data.detail || "Autosave failed");
    }

    window.LC_AUTOSAVE_STATE.lastSavedAt = data.saved_at || new Date().toISOString();
    window.LC_AUTOSAVE_STATE.saving = false;

    console.log("[LinkCraftor Autosave] saved", data);

    return data;
  } catch (err) {
    window.LC_AUTOSAVE_STATE.saving = false;
    window.LC_AUTOSAVE_STATE.lastError = String(err && err.message ? err.message : err);

    console.warn("[LinkCraftor Autosave] failed", err);

    return {
      ok: false,
      error: window.LC_AUTOSAVE_STATE.lastError
    };
  }
}

window.lcAutosaveWorkspaceSession = lcAutosaveWorkspaceSession;



// ============================================================
// LinkCraftor Workspace Autosave Engine
// Phase 3.2 + 3.9: Autosave timer and status display
// ============================================================

function lcEnsureAutosaveStatusEl(){
  let el = document.getElementById("lcAutosaveStatus");

  if (!el) {
    el = document.createElement("div");
    el.id = "lcAutosaveStatus";
    el.style.position = "fixed";
    el.style.right = "18px";
    el.style.bottom = "18px";
    el.style.zIndex = "99999";
    el.style.padding = "8px 12px";
    el.style.borderRadius = "999px";
    el.style.background = "rgba(15, 23, 42, 0.92)";
    el.style.color = "#ffffff";
    el.style.fontSize = "12px";
    el.style.fontWeight = "600";
    el.style.boxShadow = "0 8px 24px rgba(0,0,0,0.18)";
    el.style.display = "none";
    el.textContent = "Saved";
    document.body.appendChild(el);
  }

  return el;
}

function lcSetAutosaveStatus(status, detail){
  const el = lcEnsureAutosaveStatusEl();

  if (status === "saving") {
    el.textContent = "Saving...";
    el.style.display = "block";
    return;
  }

  if (status === "saved") {
    el.textContent = "Saved";
    el.style.display = "block";

    setTimeout(function(){
      if (el.textContent === "Saved") {
        el.style.display = "none";
      }
    }, 2500);

    return;
  }

  if (status === "error") {
    el.textContent = "Autosave failed";
    el.style.display = "block";
    console.warn("[LinkCraftor Autosave Status]", detail || "");
  }
}

async function lcRunTimedAutosave(){
  try {
    lcSetAutosaveStatus("saving");
    const result = await window.lcAutosaveWorkspaceSession?.("timer_30_seconds");

    if (result && result.ok) {
      lcSetAutosaveStatus("saved");
    } else {
      lcSetAutosaveStatus("error", result);
    }

    return result;
  } catch(e) {
    lcSetAutosaveStatus("error", e);
    return {
      ok: false,
      error: String(e && e.message ? e.message : e)
    };
  }
}

function lcStartAutosaveTimer(){
  if (window.LC_AUTOSAVE_TIMER_STARTED) {
    return;
  }

  window.LC_AUTOSAVE_TIMER_STARTED = true;

  window.LC_AUTOSAVE_TIMER = setInterval(function(){
    lcRunTimedAutosave();
  }, 30000);

  console.log("[LinkCraftor Autosave] 30-second timer started");
}

window.lcSetAutosaveStatus = lcSetAutosaveStatus;
window.lcRunTimedAutosave = lcRunTimedAutosave;
window.lcStartAutosaveTimer = lcStartAutosaveTimer;

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", function(){
    lcStartAutosaveTimer();
  });
} else {
  lcStartAutosaveTimer();
}













// ============================================================
// Workspace Folder Restore
// Opens a saved workspace file directly into the editor
// ============================================================

window.LC_openWorkspaceFileInEditor = async function(workspaceId, sessionId){
  if (!workspaceId || !sessionId) {
    alert("This workspace has no saved session yet.");
    return;
  }

  try {
    const res = await fetch(
      `/api/workspace/saved-session?workspace_id=${encodeURIComponent(workspaceId)}&session_id=${encodeURIComponent(sessionId)}`
    );

    const data = await res.json();

    if (!res.ok || !data.ok) {
      throw new Error(data.detail || "Could not open workspace");
    }

    const documentsBlock = data.documents || {};
    const savedDocs = Array.isArray(documentsBlock.documents)
      ? documentsBlock.documents
      : [];

    if (!savedDocs.length) {
      alert("Workspace opened, but no saved documents were found.");
      return;
    }

    window.LINKCRAFTOR_WORKSPACE_ID = workspaceId;
    window.CURRENT_WORKSPACE_ID = workspaceId;
    window.LC_WORKSPACE_ID = workspaceId;
    window.LC_ACTIVE_SESSION_ID = sessionId;

    try { localStorage.setItem("lc_workspace_id", workspaceId); } catch {}

    docs.splice(0, docs.length, ...savedDocs.map(function(d, index){
      return {
        doc_id: d.document_id || d.doc_id || ("restored_doc_" + (index + 1)),
        docId: d.document_id || d.docId || d.doc_id || ("restored_doc_" + (index + 1)),
        title: d.title || d.filename || ("Restored Document " + (index + 1)),
        filename: d.filename || d.title || ("restored-document-" + (index + 1)),
        html: d.html || "",
        text: d.text || "",
        metadata: d.metadata || {}
      };
    }));

    currentIndex = 0;

    try { saveState(); } catch(e) {}
    try { refreshDropdown(); } catch(e) {}
    try { updateDocNavButtons(); } catch(e) {}
    try { renderDoc(0); } catch(e) { console.warn("[Workspace Restore] renderDoc failed:", e); }

    try {
      if (documentsBlock.active_document_id) {
        const activeIdx = docs.findIndex(function(d){
          return String(d.doc_id || d.docId || "") === String(documentsBlock.active_document_id);
        });
        if (activeIdx >= 0) {
          currentIndex = activeIdx;
          renderDoc(activeIdx);
        }
      }
    } catch(e) {}

    try {
      const importsBlock = data.imported_sitemaps || {};
      const imported = Array.isArray(importsBlock.imported_urls) ? importsBlock.imported_urls : [];
      window.LC_IMPORTED_URLS = imported;
      window.IMPORTED_URLS = new Set(imported);
    } catch(e) {}

    try {
      const draftsBlock = data.draft_topics || {};
      const draftRows = Array.isArray(draftsBlock.draft_topics) ? draftsBlock.draft_topics : [];
      window.LC_DRAFT_TOPICS = draftRows;
      window.DRAFT_TOPICS = draftRows;
    } catch(e) {}

    try {
      const engineBlock = data.engine_state || {};
      window.LC_LAST_ENGINE_RUN = engineBlock.last_engine_run || null;
      window.LC_ACCEPTED_LINKS = engineBlock.accepted_links || [];
      window.LC_REJECTED_LINKS = engineBlock.rejected_links || [];
      window.LC_MANUAL_LINKS = engineBlock.manual_links || [];
    } catch(e) {}

    try { updateImportBadge(); } catch(e) {}
    try { updateUnifiedImportCount?.(workspaceId); } catch(e) {}

    const panel = document.getElementById("workFolderPanel");
    if (panel) panel.style.display = "none";

    try { showToast(errorBox, "Workspace opened.", 1800); } catch(e) {}

    console.log("[Workspace Restore] opened", {
      workspaceId,
      sessionId,
      documents: docs.length
    });

  } catch(e) {
    console.warn("[Workspace Restore] failed:", e);
    alert("Could not open workspace: " + (e.message || e));
  }
};
