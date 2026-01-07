// assets/js/engine/scoring.js
// Central “best-fit” scoring brain for LinkCraftor.
// No DOM or UI here — pure logic so it can be reused by engine, APIs, SDKs, plugins.

/**
 * Types (conceptual, for reference)
 *
 * PhraseContext = {
 *   phraseText: string,
 *   contextText?: string,
 *   docId?: string,
 *   sectionId?: string,
 *   position?: number,
 *   entities?: Array<RichEntity>,
 *   graphVector?: Array<number> | null,
 *   graphRelations?: Array<{
 *      targetId: string,
 *      type: string,    // "TREATS" | "CAUSES" | "ASSOCIATED_WITH" | "ALTERNATIVE_TO" | ...
 *      weight?: number  // 0–1
 *   }>,
 *   contextType?: string,   // e.g. "SIDE_EFFECTS", "OVERVIEW", "TREATMENT", "PREGNANCY"
 *   sectionType?: string,   // "INTRO" | "BODY" | "FAQ" | "CONCLUSION" | ...
 *   intent?: string,        // "INFORMATIONAL" | "COMPARISON" | "WARNING" | "ACTIONABLE"
 *   discourseRole?: string  // "QUESTION" | "ANSWER" | "CONDITION" | "RECOMMENDATION"
 * }
 *
 * RichEntity = {
 *   id: string,
 *   type: string,            // "DRUG" | "DISEASE" | "SYMPTOM" | ...
 *   canonicalName?: string,
 *   aliases?: string[],
 *   categories?: string[],
 *   parents?: string[],      // hierarchical
 *   children?: string[],     // hierarchical
 *   meta?: {
 *     role?: "PILLAR" | "SUPPORTING" | "FAQ" | "CHECKLIST" | string,
 *     [key: string]: any
 *   }
 * }
 *
 * CandidateTarget = {
 *   id: string,
 *   title: string,
 *   url: string,
 *   docId?: string,
 *   sectionId?: string | null,
 *   sourceType?: "sitemap" | "backup" | "uploaded" | "draft" | string,
 *   isExternal?: boolean,
 *   entities?: Array<RichEntity>,
 *   topicTypes?: Array<string>,        // e.g. ["SIDE_EFFECTS", "PILLAR"]
 *   sectionRoles?: Array<string>,      // e.g. ["FAQ", "INTRO"]
 *   intentTags?: Array<string>,        // e.g. ["RECOMMENDATION", "WARNING"]
 *   discourseTags?: Array<string>,     // e.g. ["ANSWER"]
 *   graphVector?: Array<number> | null,
 *   graphRelations?: Array<{
 *      targetId: string,
 *      type: string,
 *      weight?: number
 *   }>,
 *   domain?: string,                   // for external (e.g. "nhs.uk")
 *   isCanonicalTopic?: boolean        // mark main pillar pages
 * }
 *
 * ScoredSuggestion = {
 *   id, title, url, topicId,
 *   kind,    // "internal" | "semantic" | "external"
 *   tier,    // "high" | "mid" | "low"
 *   score,   // 0–1
 *   scores: { lexical, entity, graph, context, source },
 *   feedback?: { accepts:number, rejects:number, delta:number }
 * }
 */

// -------------------------------------------------------------
// 1) Weight tables & thresholds
// -------------------------------------------------------------

// Entity importance by type. Adjust as you learn from real data.
const ENTITY_TYPE_WEIGHT = {
  DRUG:      3.0,
  DISEASE:   2.5,
  CONDITION: 2.5,
  SYMPTOM:   2.0,
  MECHANISM: 1.5,
  TOPIC:     1.0
};

// Extra weights for advanced entity relations
const ENTITY_RELATION_WEIGHTS = {
  EXACT_ID:       1.0,
  ALIAS:          0.85,
  CATEGORY:       0.75,
  PARENT_CHILD:   0.75, // class ↔ member
  SIBLING_CLASS:  0.55, // same parent
};

// How compatible phrase context types are with target topic types.
const CONTEXT_TOPIC_COMPAT = {
  SIDE_EFFECTS: {
    SIDE_EFFECTS: 1.0,
    MECHANISM:    0.8,
    TREATMENT:    0.8,
    OVERVIEW:     0.5,
    GENERAL:      0.2
  },
  OVERVIEW: {
    OVERVIEW: 1.0,
    GENERAL:  0.7
  },
  TREATMENT: {
    TREATMENT:    1.0,
    SIDE_EFFECTS: 0.7,
    OVERVIEW:     0.5
  },
  PREGNANCY: {
    PREGNANCY:    1.0,
    SAFETY:       0.9,
    SIDE_EFFECTS: 0.7,
    OVERVIEW:     0.4
  }
  // extend as needed
};

// Optional: section-type compatibility (advanced Content-Aware)
const SECTION_TOPIC_COMPAT = {
  INTRO: {
    OVERVIEW: 1.0,
    GENERAL:  0.8,
    PILLAR:   0.9
  },
  BODY: {
    SIDE_EFFECTS: 0.9,
    TREATMENT:    0.9,
    DETAIL:       1.0
  },
  FAQ: {
    FAQ:      1.0,
    GENERAL:  0.6
  },
  CONCLUSION: {
    OVERVIEW: 0.8,
    PILLAR:   0.9
  }
};

// Optional: intent-level compatibility (advanced Content-Aware)
const INTENT_TOPIC_COMPAT = {
  WARNING: {
    SIDE_EFFECTS: 1.0,
    SAFETY:       1.0,
    PREGNANCY:    0.9
  },
  RECOMMENDATION: {
    TREATMENT: 1.0,
    PILLAR:    0.8
  },
  COMPARISON: {
    COMPARISON: 1.0,
    ALTERNATIVES: 0.9
  },
  ACTIONABLE: {
    CHECKLIST: 1.0,
    HOW_TO:    0.9
  }
};

// Internal sources: sitemap > backup > uploaded > draft
const INTERNAL_SOURCE_BASE = {
  sitemap:  1.0,
  backup:   0.9,
  uploaded: 0.8,
  draft:    0.6
};

// External authority (you can extend/override this at runtime)
const EXTERNAL_DOMAIN_AUTHORITY = {
  "nhs.uk":         1.0,
  "nih.gov":        1.0,
  "who.int":        1.0,
  "mayoclinic.org": 0.9,
  "healthline.com": 0.8
  // others default to ~0.5
};

// Weights for combining signals (per mode)
const WEIGHTS_INTERNAL = {
  lexical: 0.25,
  entity:  0.30,
  graph:   0.20,
  context: 0.15,
  source:  0.10
};

const WEIGHTS_SEMANTIC = {
  lexical: 0.15,
  entity:  0.30,
  graph:   0.30,
  context: 0.15,
  source:  0.10
};

const WEIGHTS_EXTERNAL = {
  lexical: 0.25,
  entity:  0.30,
  graph:   0.15,
  context: 0.10,
  source:  0.20
};

// -------------------------------------------------------------
// 1b) Memory & Feedback Layer (already wired)
// -------------------------------------------------------------

// Stores editor decisions per (phraseNorm || targetKey) in localStorage.
const FEEDBACK_LS_KEY = "lc_link_feedback_v1";

// in-memory cache: { [feedbackKey]: { accepts:number, rejects:number, lastOutcome?, lastAt? } }
let FEEDBACK_CACHE = null;

function ensureFeedbackLoaded() {
  if (FEEDBACK_CACHE !== null) return;

  FEEDBACK_CACHE = Object.create(null);
  if (typeof window === "undefined" || !window.localStorage) return;

  try {
    const raw = window.localStorage.getItem(FEEDBACK_LS_KEY);
    if (!raw) return;
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") {
      FEEDBACK_CACHE = parsed;
    }
  } catch (e) {
    console.warn("[feedback] load failed", e);
  }
}

function persistFeedback() {
  if (typeof window === "undefined" || !window.localStorage) return;
  if (!FEEDBACK_CACHE) return;
  try {
    window.localStorage.setItem(FEEDBACK_LS_KEY, JSON.stringify(FEEDBACK_CACHE));
  } catch (e) {
    console.warn("[feedback] save failed", e);
  }
}

function safeNorm(str) {
  return String(str || "").toLowerCase().trim().replace(/\s+/g, " ");
}

// Build the key that identifies (phrase, target) for feedback memory.
function makeFeedbackKey(phraseText, cand) {
  const pNorm = safeNorm(phraseText);
  const tKey =
    cand?.id ||
    cand?.topicId ||
    (cand?.url && String(cand.url).trim()) ||
    safeNorm(cand?.title || "");
  if (!pNorm || !tKey) return null;
  return `${pNorm}||${tKey}`;
}

function getFeedbackStats(phraseText, cand) {
  ensureFeedbackLoaded();
  const key = makeFeedbackKey(phraseText, cand);
  if (!key || !FEEDBACK_CACHE) {
    return { accepts: 0, rejects: 0 };
  }
  const rec = FEEDBACK_CACHE[key] || { accepts: 0, rejects: 0 };
  return {
    accepts: Number(rec.accepts || 0),
    rejects: Number(rec.rejects || 0),
    lastOutcome: rec.lastOutcome || null,
    lastAt: rec.lastAt || null
  };
}

// Map stats -> small score delta in [-0.18, +0.18]
function computeFeedbackDelta(stats) {
  const a = stats.accepts;
  const r = stats.rejects;
  const total = a + r;
  if (!total) return 0;

  // ratio in [-1, +1]
  const ratio = (a - r) / total;

  // small bonus/penalty; we keep it gentle so it “nudges” but doesn’t dominate.
  const MAX_DELTA = 0.18;
  return ratio * MAX_DELTA;
}

// Public entry: record that user accepted/rejected a given target for a phrase.
export function registerLinkFeedback(outcome, payload) {
  // outcome: "accept" | "reject"
  // payload: { phraseText, targetId?, url?, title? }
  ensureFeedbackLoaded();
  if (!FEEDBACK_CACHE) FEEDBACK_CACHE = Object.create(null);

  const phraseText = payload?.phraseText || "";
  const cand = {
    id:    payload?.targetId,
    url:   payload?.url,
    title: payload?.title
  };

  const key = makeFeedbackKey(phraseText, cand);
  if (!key) return;

  const rec = FEEDBACK_CACHE[key] || { accepts: 0, rejects: 0 };

  if (outcome === "accept") {
    rec.accepts = Number(rec.accepts || 0) + 1;
    rec.lastOutcome = "accept";
  } else if (outcome === "reject") {
    rec.rejects = Number(rec.rejects || 0) + 1;
    rec.lastOutcome = "reject";
  } else {
    return; // ignore unknown outcome
  }

  rec.lastAt = Date.now();
  FEEDBACK_CACHE[key] = rec;
  persistFeedback();
}

// Helper used inside scorer to get delta & stats together
function feedbackAdjustmentForCandidate(phraseCtx, cand) {
  const stats = getFeedbackStats(phraseCtx?.phraseText || "", cand);
  const delta = computeFeedbackDelta(stats);
  return { delta, stats };
}

// Also expose to window so non-module code (IL modal, etc.) can call it easily later.
if (typeof window !== "undefined") {
  window.LC_registerLinkFeedback = registerLinkFeedback;
}

// -------------------------------------------------------------
// 2) Generic helpers
// -------------------------------------------------------------

function tokenize(str) {
  return String(str || "")
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter(Boolean);
}

// Helpers for advanced entity map
function asArray(v) {
  if (!v) return [];
  return Array.isArray(v) ? v : [v];
}

function intersectCount(a, b) {
  if (!a?.length || !b?.length) return 0;
  const setB = new Set(b);
  let c = 0;
  for (const x of a) if (setB.has(x)) c++;
  return c;
}

// -------------------------------------------------------------
// 3) Individual signal computations
// -------------------------------------------------------------

// 3.1 Lexical: phrase vs title similarity
function lexicalScore(phraseText, candidateTitle) {
  const pTokens = tokenize(phraseText);
  const tTokens = tokenize(candidateTitle);

  if (!pTokens.length || !tTokens.length) return 0;

  const pSet = new Set(pTokens);
  const tSet = new Set(tTokens);

  let overlap = 0;
  for (const tok of pSet) {
    if (tSet.has(tok)) overlap++;
  }

  const unionSize = pSet.size + tSet.size - overlap;
  const jaccard = unionSize ? overlap / unionSize : 0;

  const titleStr  = tTokens.join(" ");
  const phraseStr = pTokens.join(" ");

  const containsPhrase = titleStr.includes(phraseStr) ? 1 : 0;
  const prefixMatch    = titleStr.startsWith(pTokens[0]) ? 1 : 0;

  let score = 0.4 * jaccard +
              0.3 * containsPhrase +
              0.3 * prefixMatch;

  if (score > 1) score = 1;
  if (score < 0) score = 0;
  return score;
}

// 3.2 Entity: overlap in canonical entities (advanced Entity Map)
// Includes: exact id, alias/category match, parent-child and siblings within taxonomies.
function entityScore(phraseEntities, candidateEntities) {
  if (!phraseEntities?.length || !candidateEntities?.length) return 0;

  let maxPossible = 0;
  let actual = 0;

  const cById = new Map();
  for (const ce of candidateEntities) {
    if (!ce?.id) continue;
    cById.set(ce.id, ce);
  }

  for (const pe of phraseEntities) {
    if (!pe) continue;
    const typeWeight = ENTITY_TYPE_WEIGHT[pe.type] || 1.0;
    maxPossible += typeWeight;

    const pId   = pe.id;
    const pAli  = asArray(pe.aliases || pe.meta?.aliases);
    const pCats = asArray(pe.categories || pe.meta?.categories);
    const pPar  = asArray(pe.parents  || pe.meta?.parents);
    const pChi  = asArray(pe.children || pe.meta?.children);

    let bestLocal = 0;

    for (const ce of candidateEntities) {
      if (!ce) continue;
      const cId   = ce.id;
      const cAli  = asArray(ce.aliases || ce.meta?.aliases);
      const cCats = asArray(ce.categories || ce.meta?.categories);
      const cPar  = asArray(ce.parents  || ce.meta?.parents);
      const cChi  = asArray(ce.children || ce.meta?.children);

      let relWeight = 0;

      // A) Exact same canonical entity id
      if (pId && cId && pId === cId) {
        relWeight = ENTITY_RELATION_WEIGHTS.EXACT_ID;
      } else {
        // B) Alias overlap
        const aliasOverlap =
          intersectCount(pAli.map(safeNorm), [safeNorm(cId), ...cAli.map(safeNorm)]) ||
          intersectCount(cAli.map(safeNorm), [safeNorm(pId), ...pAli.map(safeNorm)]);
        if (aliasOverlap > 0) {
          relWeight = Math.max(relWeight, ENTITY_RELATION_WEIGHTS.ALIAS);
        }

        // C) Category overlap
        const catOverlap = intersectCount(pCats, cCats);
        if (catOverlap > 0) {
          relWeight = Math.max(relWeight, ENTITY_RELATION_WEIGHTS.CATEGORY);
        }

        // D) Parent–child (class ↔ member)
        const sharedParent =
          intersectCount(pPar, cPar) ||
          intersectCount(pPar, cChi) ||
          intersectCount(pChi, cPar);
        if (sharedParent > 0) {
          relWeight = Math.max(relWeight, ENTITY_RELATION_WEIGHTS.PARENT_CHILD);
        }

        // E) Siblings (share a parent but not same id)
        const pAllParents = new Set(pPar);
        const cAllParents = new Set(cPar);
        const sibParents = [...pAllParents].some(x => cAllParents.has(x));
        if (sibParents && !relWeight) {
          relWeight = Math.max(relWeight, ENTITY_RELATION_WEIGHTS.SIBLING_CLASS);
        }
      }

      if (relWeight > bestLocal) {
        bestLocal = relWeight;
      }
    }

    if (bestLocal > 0) {
      actual += typeWeight * bestLocal;
    }
  }

  if (!maxPossible) return 0;
  let score = actual / maxPossible;
  if (score > 1) score = 1;
  return score;
}

// 3.3 Graph: neighborhood similarity (advanced Entity Graph)
// Uses:
//   - graphVector cosine similarity (existing)
//   - optional typed relations overlap as a small extra boost.
// If no vectors, fallback to entityScore * 0.7.
function graphScore(phraseCtx, candidate) {
  const phraseVec = phraseCtx?.graphVector;
  const candVec   = candidate?.graphVector;

  // ---- Vector similarity (old behaviour) ----
  let base = 0;
  if (phraseVec && candVec && phraseVec.length && candVec.length) {
    const a = phraseVec;
    const b = candVec;
    let dot = 0, na = 0, nb = 0;

    for (let i = 0; i < a.length && i < b.length; i++) {
      dot += a[i] * b[i];
      na  += a[i] * a[i];
      nb  += b[i] * b[i];
    }

    if (na && nb) {
      base = dot / (Math.sqrt(na) * Math.sqrt(nb));
      if (base < 0) base = 0;
      if (base > 1) base = 1;
    }
  } else {
    // No vectors: reuse entityScore as a soft proxy.
    base = entityScore(phraseCtx?.entities || [], candidate?.entities || []) * 0.7;
  }

  // ---- Typed relation overlap (advanced) ----
  const pRel = phraseCtx?.graphRelations || [];
  const cRel = candidate?.graphRelations || [];
  let relBoost = 0;

  if (pRel.length && cRel.length) {
    const keyOf = (r) => `${r.type || "GEN"}::${r.targetId || ""}`;
    const pMap  = new Map();
    for (const r of pRel) {
      if (!r?.targetId) continue;
      pMap.set(keyOf(r), (r.weight ?? 1));
    }
    let hits = 0;
    let totalWeight = 0;
    for (const r of cRel) {
      if (!r?.targetId) continue;
      const k = keyOf(r);
      if (pMap.has(k)) {
        hits++;
        totalWeight += (pMap.get(k) + (r.weight ?? 1)) / 2;
      }
    }
    if (hits) {
      const avg = totalWeight / hits; // 0–1
      // Tiny boost: max +0.2
      relBoost = Math.min(0.2, avg * 0.2 + hits * 0.02);
    }
  }

  let final = base + relBoost;
  if (final > 1) final = 1;
  if (final < 0) final = 0;
  return final;
}

// 3.4 Context: advanced Content-Aware scoring
// Uses:
//   - contextType vs topicTypes (existing)
//   - sectionType vs topicTypes (advanced)
//   - intent vs topicTypes (advanced)
//   - discourseRole vs candidate.discourseTags (if present)
function contextScore(phraseCtx, candidate) {
  const ctxType      = phraseCtx?.contextType || null;
  const sectionType  = phraseCtx?.sectionType || null;
  const intent       = phraseCtx?.intent || null;
  const discourse    = phraseCtx?.discourseRole || null;
  const topicTypes   = candidate?.topicTypes || [];
  const sectionRoles = candidate?.sectionRoles || [];
  const intentTags   = candidate?.intentTags || [];
  const discourseTags= candidate?.discourseTags || [];

  if (!topicTypes.length && !sectionRoles.length && !intentTags.length && !discourseTags.length) {
    return 0;
  }

  let ctxScore = 0;
  if (ctxType && CONTEXT_TOPIC_COMPAT[ctxType] && topicTypes.length) {
    const row = CONTEXT_TOPIC_COMPAT[ctxType];
    let best = 0;
    for (const t of topicTypes) {
      const v = row[t] ?? 0;
      if (v > best) best = v;
    }
    ctxScore = best; // 0–1
  }

  let secScore = 0;
  if (sectionType && SECTION_TOPIC_COMPAT[sectionType]) {
    const row = SECTION_TOPIC_COMPAT[sectionType];
    let best = 0;
    // sectionRoles often mirror topicTypes or roles like PILLAR/FAQ
    const pool = [...topicTypes, ...sectionRoles];
    for (const t of pool) {
      const v = row[t] ?? 0;
      if (v > best) best = v;
    }
    secScore = best; // 0–1
  }

  let intentScore = 0;
  if (intent && INTENT_TOPIC_COMPAT[intent]) {
    const row = INTENT_TOPIC_COMPAT[intent];
    let best = 0;
    const pool = [...topicTypes, ...intentTags];
    for (const t of pool) {
      const v = row[t] ?? 0;
      if (v > best) best = v;
    }
    intentScore = best; // 0–1
  }

  let discourseScore = 0;
  if (discourse && discourseTags.length) {
    // Simple: give 1.0 if discourse role matches, otherwise 0
    const normDisc = safeNorm(discourse);
    const discHit = discourseTags.some(d => safeNorm(d) === normDisc);
    discourseScore = discHit ? 1.0 : 0;
  }

  // Combine: contextType is primary, then section, then intent, tiny discourse bump
  const combined =
    0.45 * ctxScore +
    0.30 * secScore +
    0.20 * intentScore +
    0.05 * discourseScore;

  return combined > 1 ? 1 : combined;
}

// 3.5 Source: quality of where the target came from

function internalSourceScore(candidate) {
  const base = INTERNAL_SOURCE_BASE[candidate.sourceType] ?? 0.6;

  const role = candidate?.topicTypes?.includes("PILLAR") ||
               candidate?.sectionRoles?.includes("PILLAR") ||
               candidate?.entities?.some(e => e.meta?.role === "PILLAR");

  const canonicalBoost = candidate.isCanonicalTopic || role ? 0.1 : 0;
  let score = base + canonicalBoost;
  if (score > 1) score = 1;
  return score;
}

function externalSourceScore(candidate) {
  const host = String(candidate.domain || "").toLowerCase();
  let base = EXTERNAL_DOMAIN_AUTHORITY[host];
  if (base == null) {
    // Unknown domains get a neutral/medium value
    base = 0.5;
  }
  return base;
}

// -------------------------------------------------------------
// 4) Mode-specific combination (internal / semantic / external)
// -------------------------------------------------------------
//
// IMPORTANT for “tightened semantic”:
// - Internal: can still work even if entities/graph are missing (falls back to lexical + source).
// - Semantic: ONLY allowed when we have entity and/or graph signals or at least some lexical.
// -------------------------------------------------------------

// --- Internal ---
function computeInternalScore(phraseCtx, candidate, signals) {
  const { lexical, entity, graph, context, source } = signals;

  const hasEntities = !!(phraseCtx?.entities?.length && candidate?.entities?.length);
  const hasGraph    = !!(phraseCtx?.graphVector && candidate?.graphVector);

  // If we do have entities, require a minimum (but not super strict)
  if (hasEntities && entity < 0.25) {
    return 0;
  }

  // If we do have graph vectors, require some neighborhood similarity
  if (hasGraph && graph < 0.30) {
    return 0;
  }

  // If we have any semantic signal, block very suspicious combinations
  // where both entity+graph are weak and lexical is also weak.
  if ((hasEntities || hasGraph) && (entity + graph) < 0.40 && lexical < 0.60) {
    return 0;
  }

  let score =
    WEIGHTS_INTERNAL.lexical * lexical +
    WEIGHTS_INTERNAL.entity  * entity  +
    WEIGHTS_INTERNAL.graph   * graph   +
    WEIGHTS_INTERNAL.context * context +
    WEIGHTS_INTERNAL.source  * source;

  if (score < 0) score = 0;
  if (score > 1) score = 1;
  return score;
}

function classifyInternalTier(score) {
  if (score >= 0.75) return "high";
  if (score >= 0.55) return "mid";
  if (score >= 0.35) return "low";
  return null; // too weak
}

// --- Semantic ---
function computeSemanticScore(phraseCtx, candidate, signals) {
  const { lexical, entity, graph, context, source } = signals;

  // 1) Only kill *completely* empty candidates
  //    (no entity, no graph, no context, almost no lexical)
  if (entity === 0 && graph === 0 && context === 0 && lexical < 0.20) {
    return 0;
  }

  // 2) Very soft sanity check:
  //    - either we have *some* semantic signal (entity+graph)
  //    - or lexical similarity is at least mild
  const hasEntityGraph = (entity + graph) >= 0.15;   // soft
  const hasLexical     = lexical >= 0.30;            // lower than before

  if (!hasEntityGraph && !hasLexical) {
    return 0;
  }

  let score =
    WEIGHTS_SEMANTIC.lexical * lexical +
    WEIGHTS_SEMANTIC.entity  * entity  +
    WEIGHTS_SEMANTIC.graph   * graph   +
    WEIGHTS_SEMANTIC.context * context +
    WEIGHTS_SEMANTIC.source  * source;

  // 3) If this candidate looks like a *perfect internal match*
  //    (same entities + strong lexical), we do NOT zero it out anymore.
  //    We just damp its semantic score so the internal mode still wins
  //    in the routing step, but semantic isn't completely dead.
  if (entity >= 0.70 && lexical >= 0.80) {
    score *= 0.4; // strong penalty, but not 0
  }

  if (score < 0) score = 0;
  if (score > 1) score = 1;
  return score;
}

function classifySemanticTier(score) {
  if (score >= 0.40) return "high";
  if (score >= 0.22) return "mid";
  if (score >= 0.12) return "low";
  return null; // below this is considered noise
}

// --- External ---
function computeExternalScore(phraseCtx, candidate, signals) {
  const { lexical, entity, graph, context, source } = signals;

  // Authority & relevance checks:
  if (source < 0.5) return 0;  // domain must be at least medium quality
  if (entity < 0.3) return 0;  // must match main entity

  let score =
    WEIGHTS_EXTERNAL.lexical * lexical +
    WEIGHTS_EXTERNAL.entity  * entity  +
    WEIGHTS_EXTERNAL.graph   * graph   +
    WEIGHTS_EXTERNAL.context * context +
    WEIGHTS_EXTERNAL.source  * source;

  if (score < 0) score = 0;
  if (score > 1) score = 1;
  return score;
}

function classifyExternalTier(score) {
  if (score >= 0.75) return "high";
  if (score >= 0.55) return "mid";
  return null;
}

// -------------------------------------------------------------
// 5) Main API
// -------------------------------------------------------------

/**
 * scoreCandidatesForPhrase
 *
 * @param {PhraseContext} phraseCtx
 * @param {CandidateTarget[]} candidates
 * @returns {ScoredSuggestion[]} sorted by score desc
 */

export function scoreCandidatesForPhrase(phraseCtx, candidates) {
  const results = [];
  if (!phraseCtx || !Array.isArray(candidates) || !candidates.length) {
    return results;
  }

  for (const cand of candidates) {
    // 1) compute base signals
    const lexical = lexicalScore(phraseCtx.phraseText, cand.title);
    const entity  = entityScore(phraseCtx.entities || [], cand.entities || []);
    const graph   = graphScore(phraseCtx, cand);
    const context = contextScore(phraseCtx, cand);
    const source  = cand.isExternal
      ? externalSourceScore(cand)
      : internalSourceScore(cand);

    const signals = { lexical, entity, graph, context, source };

    let bestKind  = null;
    let bestScore = 0;
    let tier      = null;

    if (cand.isExternal) {
      // ---------------- EXTERNAL ----------------
      const sExt = computeExternalScore(phraseCtx, cand, signals);
      const tExt = sExt > 0 ? classifyExternalTier(sExt) : null;

      if (tExt) {
        bestKind  = "external";
        bestScore = sExt;
        tier      = tExt;
      }

    } else {
      // ---------------- INTERNAL vs SEMANTIC ----------------
      const sInt = computeInternalScore(phraseCtx, cand, signals);
      const sSem = computeSemanticScore(phraseCtx, cand, signals);

      const tInt = sInt > 0 ? classifyInternalTier(sInt) : null;
      const tSem = sSem > 0 ? classifySemanticTier(sSem) : null;

      if (tInt && !tSem) {
        // Only internal is strong enough
        bestKind  = "internal";
        bestScore = sInt;
        tier      = tInt;

      } else if (!tInt && tSem) {
        // Only semantic is strong enough
        bestKind  = "semantic";
        bestScore = sSem;
        tier      = tSem;

      } else if (tInt && tSem) {
        // Both are valid: prefer internal ONLY if it clearly wins.
        // Otherwise route as semantic so we actually see semantic highlights.
        if (sInt >= sSem + 0.10) {
          bestKind  = "internal";
          bestScore = sInt;
          tier      = tInt;
        } else {
          bestKind  = "semantic";
          bestScore = sSem;
          tier      = tSem;
        }
      }
    }

    // If we still don't have a valid kind/tier, skip this candidate
    if (!bestKind || !tier) continue;

    // 2) Memory & Feedback adjustment (tiny bias up/down)
    const fb = feedbackAdjustmentForCandidate(phraseCtx, cand);
    let finalScore = bestScore + fb.delta;

    if (finalScore < 0) finalScore = 0;
    if (finalScore > 1) finalScore = 1;

    // Re-classify tier using adjusted score so feedback can push things
    if (bestKind === "internal") {
      tier = classifyInternalTier(finalScore);
    } else if (bestKind === "semantic") {
      tier = classifySemanticTier(finalScore);
    } else if (bestKind === "external") {
      tier = classifyExternalTier(finalScore);
    }

    // If feedback pushed it below all thresholds, drop it
    if (!tier) continue;

    results.push({
      id:      cand.id,
      title:   cand.title,
      url:     cand.url,
      topicId: cand.id,   // you can swap this for real topicId later
      kind:    bestKind,  // "internal" | "semantic" | "external"
      tier,               // "high" | "mid" | "low"
      score:   finalScore,
      scores:  signals,
      feedback: {
        accepts: fb.stats.accepts || 0,
        rejects: fb.stats.rejects || 0,
        delta:   fb.delta
      }
    });
  }

  // Sort by final score (best first)
  results.sort((a, b) => b.score - a.score);
  return results;
}

// -------------------------------------------------------------
// 6) Optional: export helpers for debugging / future APIs
// -------------------------------------------------------------
export const ScoringDebug = {
  safeNorm,
  tokenize,
  lexicalScore,
  entityScore,
  graphScore,
  contextScore,
  internalSourceScore,
  externalSourceScore,
  computeInternalScore,
  computeSemanticScore,
  computeExternalScore,
  classifyInternalTier,
  classifySemanticTier,
  classifyExternalTier,
  WEIGHTS_INTERNAL,
  WEIGHTS_SEMANTIC,
  WEIGHTS_EXTERNAL,
  ENTITY_TYPE_WEIGHT,
  ENTITY_RELATION_WEIGHTS,
  CONTEXT_TOPIC_COMPAT,
  SECTION_TOPIC_COMPAT,
  INTENT_TOPIC_COMPAT,
  INTERNAL_SOURCE_BASE,
  EXTERNAL_DOMAIN_AUTHORITY,
  getFeedbackStats,
  computeFeedbackDelta
};


// assets/js/engine/scoring.js
// ---------------------------------------------------------------------------
// External reference provider scoring hook for LinkcraftorExternalRefs
// ---------------------------------------------------------------------------

window.LinkcraftorScoring = window.LinkcraftorScoring || {};

/**
 * scoreExternalProvider(phrase, providerId, baseScore)
 *
 * You can tweak this to fine-tune how different providers are ranked.
 * It is optional: external_helix.js has its own default if this is missing.
 */
window.LinkcraftorScoring.scoreExternalProvider = function (
  phrase,
  providerId,
  baseScore
) {
  let score = baseScore || 1;
  const p = String(phrase || "").toLowerCase();

  const pregnancy =
    p.includes("pregnancy") ||
    p.includes("pregnant") ||
    p.includes("ovulation") ||
    p.includes("due date") ||
    p.includes("conception") ||
    p.includes("fertile");

  const drugPhrase =
    p.includes("mg") ||
    p.includes("tablet") ||
    p.includes("capsule") ||
    p.includes("dose") ||
    p.includes("dosage") ||
    p.includes("side effect") ||
    p.includes("side effects") ||
    p.includes("interaction") ||
    p.includes("drug") ||
    p.includes("medicine");

  const childPhrase =
    p.includes("baby") ||
    p.includes("newborn") ||
    p.includes("infant") ||
    p.includes("child") ||
    p.includes("toddler");

  // Pregnancy / fertility → favour ACOG + WHO maternal + pregnancy group
  if (pregnancy) {
    if (providerId === "acog") score += 0.8;
    if (providerId === "who_maternal") score += 0.6;
    if (providerId === "who_reproductive") score += 0.5;
    if (providerId === "cleveland_obgyn") score += 0.5;
  }

  // Drugs → favour professional drug resources
  if (drugPhrase) {
    if (providerId === "drugs") score += 0.7;
    if (providerId === "rxlist") score += 0.6;
    if (providerId === "webmd") score += 0.3;
    if (providerId === "pubmed") score += 0.4;
  }

  // Child / baby → favour UNICEF + children’s hospitals
  if (childPhrase) {
    if (providerId === "unicef") score += 0.7;
    if (providerId === "stanford_childrens") score += 0.6;
  }

  // Light global boosts for big evidence/guideline sources
  if (providerId === "pubmed" || providerId === "cochrane" || providerId === "nice") {
    score += 0.3;
  }

  return score;
};
