// assets/js/engine/scoring.js
// Thin wrapper: scoring + decision emission moved to backend.
// Keeps exported API stable so the frontend does not break.

/**
 * Backend endpoints:
 *  - POST /api/engine/score
 *  - POST /api/engine/decision
 */

/**
 * Configure backend base URL.
 * Priority:
 *  1) window.LINKCRAFTOR_API_BASE (your canonical config)
 *  2) window.LC_ENGINE_BASE       (legacy)
 *  3) default localhost
 */
const LC_ENGINE_BASE = (function resolveEngineBase() {
  try {
    const raw =
      (typeof window !== "undefined" && (window.LINKCRAFTOR_API_BASE || window.LC_ENGINE_BASE))
        ? String(window.LINKCRAFTOR_API_BASE || window.LC_ENGINE_BASE)
        : "http://127.0.0.1:8001";
    return raw.replace(/\/+$/, "");
  } catch {
    return "http://127.0.0.1:8001";
  }
})();

/**
 * scoreCandidatesForPhrase
 * Keeps the old function signature and return shape:
 * - Input: (phraseCtx, candidates)
 * - Output: Promise<ScoredSuggestion[]>
 */
export async function scoreCandidatesForPhrase(phraseCtx, candidates) {
  try {
    if (!phraseCtx || !Array.isArray(candidates) || candidates.length === 0) return [];

    const res = await fetch(`${LC_ENGINE_BASE}/api/engine/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phraseCtx, candidates })
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      console.warn("[LC scoring] backend returned non-OK:", res.status, data);
      return [];
    }

    if (!data || data.ok !== true || !Array.isArray(data.results)) {
      console.warn("[LC scoring] backend payload not ok:", data);
      return [];
    }

    return data.results;
  } catch (err) {
    console.warn("[LC scoring] request failed:", err);
    return [];
  }
}

/**
 * registerLinkFeedback (Layer 1.3)
 * UI -> Backend decision emitter (SILENT)
 *
 * outcome: "accept" | "reject"
 * payload: {
 *   phraseText, targetId?, url?, title?, kind?,
 *   workspaceId?, docId?, userId?, eventType?,
 *   contextType?, sectionType?, intent?, entities?
 * }
 */
export async function registerLinkFeedback(outcome, payload) {
  try {
    const ws = String(payload?.workspaceId || window.LC_WORKSPACE_ID || "ws_demo").trim();
    const docId = String(payload?.docId || window.LC_ACTIVE_DOC_ID || "doc_demo_001").trim();
    const userId = String(payload?.userId || window.LC_USER_ID || "bernard").trim();

    const phraseText = String(payload?.phraseText || "").trim();
    if (!phraseText) return null;

    const incomingEventType = String(payload?.eventType || "").trim();

    const eventType =
      outcome === "reject"
        ? "LINK_SUGGESTION_REJECTED"
        : (incomingEventType || "LINK_SUGGESTION_ACCEPTED");

    const targetId = String(payload?.targetId || "").trim();
    const url = String(payload?.url || "").trim();
    const title = String(payload?.title || "").trim();
    const kind = String(payload?.kind || "internal").trim();

    const body = {
      eventType,
      workspaceId: ws,
      userId,
      docId,
      timestamp: Date.now(),
      contextType: String(payload?.contextType || "").trim(),
      sectionType: String(payload?.sectionType || "").trim(),
      intent: String(payload?.intent || "").trim(),
      entities: Array.isArray(payload?.entities) ? payload.entities : [],
      payload: {
        targetId: targetId || null,
        url,
        title,
        phraseText,
        kind
      },
      source: "web"
    };

    const res = await fetch(`${LC_ENGINE_BASE}/api/engine/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);

    // Silent by design (no UI toasts)
    return data;
  } catch (e) {
    // Non-blocking and silent (no toasts)
    console.warn("[LC feedback] decision emit failed:", e?.message || e);
    return null;
  }
}

// Keep global compatibility for non-module callers (IL modal, etc.)
if (typeof window !== "undefined") {
  window.LC_registerLinkFeedback = registerLinkFeedback;
}

/**
 * ScoringDebug
 * Stub to avoid breaking any code that expects ScoringDebug to exist.
 */
export const ScoringDebug = {};
