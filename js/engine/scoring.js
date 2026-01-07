// assets/js/engine/scoring.js
// Thin wrapper: scoring logic moved to backend.
// Keeps the same exported API so the frontend does not break.

/**
 * NOTE:
 * - The real scoring brain now lives in the backend endpoint:
 *     POST /api/engine/score
 * - This file intentionally contains NO scoring logic.
 */

/**
 * Configure the backend base URL.
 * - If your frontend is served from the same origin as FastAPI later on AWS,
 *   you can change this to "" (empty) and use relative paths.
 */
const LC_ENGINE_BASE =
  window.LC_ENGINE_BASE || "http://127.0.0.1:8001";

/**
 * scoreCandidatesForPhrase
 * Keeps the old function signature and return shape:
 * - Input: (phraseCtx, candidates)
 * - Output: Promise<ScoredSuggestion[]>
 */
export async function scoreCandidatesForPhrase(phraseCtx, candidates) {
  try {
    if (!phraseCtx || !Array.isArray(candidates) || candidates.length === 0) {
      return [];
    }

    const res = await fetch(`${LC_ENGINE_BASE}/api/engine/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phraseCtx, candidates })
    });

    if (!res.ok) {
      console.warn("[LC scoring] backend returned non-OK:", res.status);
      return [];
    }

    const data = await res.json();

    if (!data || data.ok !== true) {
      console.warn("[LC scoring] backend payload not ok:", data);
      return [];
    }

    if (!Array.isArray(data.results)) return [];
    return data.results;
  } catch (err) {
    console.warn("[LC scoring] request failed:", err);
    return [];
  }
}

/**
 * registerLinkFeedback
 * Placeholder to preserve compatibility because older UI code may call:
 *   - registerLinkFeedback(...)
 *   - window.LC_registerLinkFeedback(...)
 *
 * In the next step (Step 2), we will move feedback storage to the backend too.
 */
export function registerLinkFeedback(outcome, payload) {
  console.warn(
    "[LC feedback] registerLinkFeedback called, but feedback is not yet moved to backend.",
    { outcome, payload }
  );
}

// Keep global compatibility for any non-module code still calling this
if (typeof window !== "undefined") {
  window.LC_registerLinkFeedback = registerLinkFeedback;
}

/**
 * ScoringDebug
 * Stub to avoid breaking any code that expects ScoringDebug to exist.
 * (Backend has the debug internals now.)
 */
export const ScoringDebug = {};
