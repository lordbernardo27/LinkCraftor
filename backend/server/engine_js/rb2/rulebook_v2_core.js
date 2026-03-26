/**
 * Rulebook v2 - Step 1: JSON-only engine (no DOM writes)
 *
 * What this module does:
 *  - Parses the current article (HTML or plain text) into sections.
 *  - Extracts candidate anchors (2-4 token n-grams; connectors allowed).
 *  - Maps anchors to targets using lexical signals (titles/aliases + URL slugs).
 *  - Scores, filters with adaptive floor, and enforces caps:
 *      per-target (<=2), per-section (<=3), per-200 words rolling (<=4).
 *  - Returns JSON with {recommended, optional, hidden, meta, diagnostics}.
 *
 * Nothing is inserted into the DOM at this step.
 */

// --------------------------- Config (Balanced) ---------------------------
export const RB2_DEFAULTS = {
  mode: "balanced",                 // "strict" | "balanced" | "exploratory"
  adaptivePercentile: 0.40,         // 40th percentile floor (balanced)
  perTargetMax: 2,                  // <= 2 links to same URL across doc
  perSectionMax: 3,                 // <= 3 links in same section
  per200WordsMax: 4,                // <= 4 in any rolling 200-word window
  minSectionLen: 30,                // ignore tiny sections
  ngramMin: 2,
  ngramMax: 4,
  minContentTokens: 2,
  headingPlacement: false,          // Balanced: avoid heading placements
  titleEchoPenalty: 0.20,
  orphanBoost: 0.06,
  hubPenaltyThreshold: 20,
  hubPenalty: 0.08,

  // Step 4.3: semantic/optional placeholder (until entity/graph is wired)
  // Optional allowed only via include/synonyms/entityMap evidence.
  optionalTitleMatchFloor: 0.58,

  // weights
  W: { titleMatch: 0.40, urlCoverage: 0.25, bm25Url: 0.20, prominence: 0.10, rarity: 0.05 },

  // connectors allowed inside anchors
  CONNECTORS: new Set(["of","for","in","on","to","and","with","vs","&","or","the","a","an","by","from"]),

  // minimal stopwords (can be overridden)
  STOPWORDS: new Set(["the","a","an","and","or","for","to","of","in","on","with","by","from","at","as","is","are","was","were","be","been","being"])
};

// ------------------------------- Utilities -------------------------------
const clamp01 = (x) => (x < 0 ? 0 : (x > 1 ? 1 : x));
const uniq = (arr) => Array.from(new Set(arr));
const foldAccents = (s) => String(s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
const norm = (s) =>
  foldAccents(String(s || "")
    .toLowerCase()
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201C\u201D]/g, '"')
  );

const tokenize = (s) =>
  norm(s)
    .replace(/-/g, " ")                       // ✅ Step 6.1.1: split hyphen compounds into tokens
    .replace(/[^\p{L}\p{N}']+/gu, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);


function tokenSet(s) { return new Set(tokenize(s)); }

function jaccard(a, b) {
  const A = tokenSet(a), B = tokenSet(b);
  if (!A.size || !B.size) return 0;
  let inter = 0;
  for (const t of A) if (B.has(t)) inter++;
  return inter / Math.max(A.size, B.size);
}

function urlTokens(u) {
  try {
    const x = new URL(u);
    const host = (x.hostname || "").replace(/^www\./, "");
    const hostParts = host.split(/[.\-]+/).filter(Boolean);
    const pathParts = (x.pathname || "").split(/[\/_\-]+/).filter(Boolean);
    return hostParts.concat(pathParts).map((t) => t.toLowerCase());
  } catch {
    return [];
  }
}

function urlCoverage(anchor, url) {
  const a = tokenize(anchor);
  const u = urlTokens(url);
  if (!a.length || !u.length) return 0;
  let hit = 0;
  for (const t of a) {
    if (u.some((z) => z.includes(t) || t.includes(z))) hit++;
  }
  return clamp01(hit / a.length);
}

function simplePluralVariants(w) {
  if (w.endsWith("ies")) return [w, w.slice(0, -3) + "y"];
  if (w.endsWith("es")) return [w, w.slice(0, -2)];
  if (w.endsWith("s")) return [w, w.slice(0, -1)];
  return [w, w + "s"];
}

function variantsForPhrase(s) {
  const base = norm(s).trim();
  const hy2sp = base.replace(/\-/g, " ");
  const sp2hy = base.replace(/\s+/g, "-");
  const toks = tokenize(base);
  const last = toks[toks.length - 1] || "";
  const pluralV = simplePluralVariants(last).map((v) => toks.slice(0, -1).concat(v).join(" "));
  return uniq([base, hy2sp, sp2hy, ...pluralV]);
}

// Cache normalized entityMap keys so we don't recompute for every anchor
const _entityKeyCache = new WeakMap();

function _getEntityMapKeyPairs(entityMap) {
  if (!entityMap || typeof entityMap !== "object") return [];
  if (_entityKeyCache.has(entityMap)) return _entityKeyCache.get(entityMap);

  // Store pairs of { orig, norm } and sort longest-first so more specific phrases win
  const pairs = Object.keys(entityMap)
    .map((orig) => ({ orig, norm: norm(orig).trim() }))
    .filter((x) => x.norm)
    .sort((a, b) => b.norm.length - a.norm.length);

  _entityKeyCache.set(entityMap, pairs);
  return pairs;
}

function entityMapLookup(entityMap, anchorText) {
  if (!entityMap || typeof entityMap !== "object") return { ents: [], matchedKey: null };

  // 1) Exact normalized key lookup
  const baseKey = norm(anchorText).trim();
  if (baseKey && Array.isArray(entityMap[baseKey]) && entityMap[baseKey].length) {
    return { ents: entityMap[baseKey], matchedKey: baseKey };
  }

  // 2) Variant lookup (hyphen/space/plural tail)
  const vars = variantsForPhrase(anchorText);
  for (const v of vars) {
    const k = norm(v).trim();
    if (k && Array.isArray(entityMap[k]) && entityMap[k].length) {
      return { ents: entityMap[k], matchedKey: k };
    }
  }

  // 3) Span lookup (entity key is contained as whole words inside anchor)
  const aNorm = norm(anchorText).trim();
  if (!aNorm) return { ents: [], matchedKey: null };
  const padded = ` ${aNorm} `;

  const pairs = _getEntityMapKeyPairs(entityMap); // uses your existing cache helper
  for (const p of pairs) {
    if (!p.norm) continue;
    if (p.norm.length < 3) continue;
    if (padded.includes(` ${p.norm} `)) {
      const ents = entityMap[p.orig];
      if (Array.isArray(ents) && ents.length) {
        // Use the original key for human-readable painting, but keep it normalized via norm() later
        return { ents, matchedKey: p.orig };
      }
    }
  }

  return { ents: [], matchedKey: null };
}




function isSubsetOfTitle(anchorText, titleText) {
  const aToks = tokenize(anchorText);
  const tSet = tokenSet(titleText);
  if (!aToks.length || !tSet.size) return false;
  return aToks.every((t) => tSet.has(t));
}

// ------------------------------ Sectionizing ------------------------------
// Prefer rb2Doc paragraphs when provided.
export function splitSectionsFromRb2Doc(rb2Doc, minSectionLen = RB2_DEFAULTS.minSectionLen) {
  const sections = [];
  const paras = rb2Doc && Array.isArray(rb2Doc.paragraphs) ? rb2Doc.paragraphs : [];

  for (const p of paras) {
    const text = String(p?.text || "").trim();
    const len = text.length;
    if (len < minSectionLen) continue;

    sections.push({
      type: "P",
      text,
      len,
      isHeading: false,
      idx: sections.length,

      // rb2Doc mapping metadata (preserved)
      paraIndex: Number(p?.i ?? sections.length),
      charStart: Number(p?.charStart ?? 0),
      charEnd: Number(p?.charEnd ?? 0),
      headingCtx: p?.headingCtx || { h1: null, h2: null, h3: null, h4: null },

      // carry tokens if present (not required by current miner but reserved)
      tokens: Array.isArray(p?.tokens) ? p.tokens : null
    });
  }

  return sections;
}

export function splitSections({ html, text, minSectionLen = RB2_DEFAULTS.minSectionLen }) {
  const sections = [];

  if (html) {
    const container =
      (typeof document !== "undefined" && document.createElement)
        ? document.createElement("div")
        : null;

    if (!container) {
      const raw = String(text || html || "").replace(/\r\n/g, "\n");
      const parts = raw.split(/\n{2,}/).map((s) => s.trim()).filter(Boolean);
      parts.forEach((p) => {
        if (p.length >= minSectionLen) sections.push({ type: "P", text: p, len: p.length, isHeading: false });
      });
      return sections.map((s, i) => ({ ...s, idx: i }));
    }

    container.innerHTML = String(html || "");

    const blocks = Array.from(container.querySelectorAll("p, li, td, blockquote, pre"));
    for (const el of blocks) {
      const t = el.textContent || "";
      const len = t.trim().length;
      if (len >= minSectionLen) sections.push({ type: el.tagName, text: t, len, isHeading: false });
    }

    Array.from(container.querySelectorAll("h1,h2,h3,h4,h5,h6")).forEach((h) => {
      const t = h.textContent || "";
      const len = t.trim().length;
      if (len >= minSectionLen) sections.push({ type: h.tagName, text: t, len, isHeading: true });
    });

  } else {
    const raw = String(text || "").replace(/\r\n/g, "\n");
    const parts = raw.split(/\n{2,}/).map((s) => s.trim()).filter(Boolean);
    parts.forEach((p) => {
      if (p.length >= minSectionLen) sections.push({ type: "P", text: p, len: p.length, isHeading: false });
    });
  }

  return sections.map((s, i) => ({ ...s, idx: i }));
}

// ------------------------------ Anchor mining -----------------------------
export function extractAnchorsFromSection(section, cfg = RB2_DEFAULTS) {
  const toks = tokenize(section.text);
  const out = new Set();

  for (let n = cfg.ngramMin; n <= cfg.ngramMax; n++) {
    for (let i = 0; i <= toks.length - n; i++) {
      const gram = toks.slice(i, i + n);
      const content = gram.filter((t) => !cfg.STOPWORDS.has(t) && !cfg.CONNECTORS.has(t));
      if (content.length < cfg.minContentTokens) continue;
      out.add(gram.join(" "));
    }
  }

  return Array.from(out);
}

// ---------------------------- Targets & aliases ----------------------------
export function buildTargets(rawTargets) {
  const clean = [];
  for (const t of (rawTargets || [])) {
    if (!t || !(t.url || t.title)) continue;
    const url = t.url || "";
    const title = t.title || "";
    const aliases = uniq([title, ...(t.aliases || [])]).filter(Boolean);
    clean.push({ url, title, aliases, inboundLinks: Number(t.inboundLinks || 0) });
  }
  return clean;
}

// Build a BM25 index over URL tokens only (host/path)
function buildUrlBM25(targets) {
  const docs = targets.map((t) => urlTokens(t.url || ""));
  const N = docs.length || 1;
  const dfs = new Map();
  const lens = docs.map((d) => d.length);
  const avgdl = lens.reduce((a, b) => a + b, 0) / N;

  for (const d of docs) {
    const seen = new Set();
    for (const tok of d) {
      if (!seen.has(tok)) {
        seen.add(tok);
        dfs.set(tok, (dfs.get(tok) || 0) + 1);
      }
    }
  }

  const idf = (tok) => {
    const df = dfs.get(tok) || 0;
    return Math.log((N - df + 0.5) / (df + 0.5) + 1);
  };

  return { docs, idf, lens, avgdl };
}

function bm25Score(queryTokens, docTokens, idf, dl, avgdl, k1 = 1.2, b = 0.75) {
  if (!docTokens.length) return 0;

  const tf = new Map();
  for (const t of docTokens) tf.set(t, (tf.get(t) || 0) + 1);

  let s = 0;
  const q = uniq(queryTokens);

  for (const t of q) {
    const f = tf.get(t) || 0;
    if (!f) continue;
    const _idf = idf(t);
    const denom = f + k1 * (1 - b + b * (dl / avgdl));
    s += _idf * (f * (k1 + 1)) / denom;
  }

  return clamp01(s / 8);
}

// ------------------------------ Bucketing helpers -------------------------
function isLiteralStrong(anchorText, targetTitle, targetAliases) {
  const a = String(anchorText || "");
  const title = String(targetTitle || "");
  const aliases = Array.isArray(targetAliases) ? targetAliases : [];

  if (!a.trim() || !title.trim()) return false;

  const aNorm = norm(a).trim();
  const tNorm = norm(title).trim();

  if (aNorm && tNorm && aNorm === tNorm) return true;

  for (const al of aliases) {
    const alNorm = norm(al).trim();
    if (alNorm && aNorm === alNorm) return true;
  }

  const aVars = variantsForPhrase(a);
  const aVarNorms = aVars.map((v) => norm(v).trim()).filter(Boolean);

  if (aVarNorms.includes(tNorm)) return true;
  for (const al of aliases) {
    const alNorm = norm(al).trim();
    if (alNorm && aVarNorms.includes(alNorm)) return true;
  }

  return false;
}

function passesOptionalEvidenceGate(c, cfg, synonyms) {
  const via = String(c?.via || "");
  const phrase = String(c?.anchor?.text || "");
  const tTitle = String(c?.target?.title || "");

  // Always allow include mappings (manual/memory)
  if (via === "include") return true;

  // ✅ Step 5: allow entityMap semantic evidence
  if (via === "entityMap") return true;

  // Allow synonym-driven semantic links (fallback placeholder)
  if (via === "synonyms") return true;

  // Block title fragments for semantic/optional meaning
  if (isSubsetOfTitle(phrase, tTitle)) return false;

  // If synonyms map provided, allow only if explicitly maps phrase -> target title
  if (synonyms && typeof synonyms === "object") {
    const key = norm(phrase).trim();
    const syn = synonyms[key];

    if (typeof syn === "string") {
      return norm(syn).trim() === norm(tTitle).trim();
    }
    if (Array.isArray(syn)) {
      const t = norm(tTitle).trim();
      return syn.map((x) => norm(x).trim()).includes(t);
    }
  }

  return false;
}

// ------------------------------ Mapping & Scoring -------------------------
export function mapAndScore({
  sections,
  targets,
  cfg = RB2_DEFAULTS,
  include = {},
  block = [],
  synonyms = {},
  entityMap = {}
}) {

  const W = cfg.W;
  const urlIndex = buildUrlBM25(targets);

  // Precompute rarity (IDF-ish) across doc for anchors
  const anchorDf = new Map();
  const sectionAnchors = sections.map((sec) => extractAnchorsFromSection(sec, cfg));

  for (const arr of sectionAnchors) {
    const seen = new Set(arr);
    for (const a of seen) anchorDf.set(a, (anchorDf.get(a) || 0) + 1);
  }

  // Build alias tokens for quick title matching
  const targetAliasTokens = targets.map((t) => uniq([t.title, ...(t.aliases || [])]).map(tokenize));

  const candidates = [];

  for (let sidx = 0; sidx < sections.length; sidx++) {
    const sec = sections[sidx];

    if (sec.isHeading && cfg.headingPlacement === false) continue;

    for (const anchor of sectionAnchors[sidx]) {
      if (Array.isArray(block) && block.some((b) => anchor === b)) continue;

      const variants = variantsForPhrase(anchor);

      // 1) Force-include / Memory accepted direct map
      const directUrl = include[anchor] || include[variants.find((v) => include[v])];

      let mapped = [];

            if (directUrl) {
        const tgt = targets.find((t) => t.url === directUrl);
        if (tgt) {
          mapped.push({
            t: tgt,
            titleMatch: 1,
            urlCoverage: urlCoverage(anchor, tgt.url),
            bm25Url: 1,
            via: "include"
          });
        }
      }

      // 2) Title/Alias lexical match
      if (mapped.length === 0) {
        for (let i = 0; i < targets.length; i++) {
          const t = targets[i];
          const aliasLists = targetAliasTokens[i];
          let tm = 0;

          for (const toks of aliasLists) {
            const aliasStr = toks.join(" ");
            tm = Math.max(tm, jaccard(anchor, aliasStr));
          }

          if (tm >= 0.45) {
            mapped.push({
              t,
              titleMatch: tm,
              urlCoverage: urlCoverage(anchor, t.url),
              bm25Url: 0,
              via: "title"
            });
          }
        }
      }

      // 2.25) EntityMap hook (semantic equivalence placeholder)
      // entityMap example:
      // {
      //   "high blood pressure": [{ id:"E:HTN", type:"DISEASE", label:"Hypertension" }]
      // }
      if (mapped.length === 0 && entityMap && typeof entityMap === "object") {
        const em = entityMapLookup(entityMap, anchor);
        const ents = em.ents;
        const matchedKey = em.matchedKey;

        // collect labels from entities
        const labels = [];
        for (const e of ents) {
          const lab = (e && (e.label || e.name || e.text)) ? String(e.label || e.name || e.text) : "";
          if (lab && lab.trim()) labels.push(lab);
        }

        // ✅ attach IDs + labels as clean string arrays
        const entityIds = ents.map((e) => String((e && e.id) || "")).filter(Boolean);
        const semanticLabels = labels.map((x) => String(x || "")).filter(Boolean);

        // ✅ Step 7.1: paint with matched key, preserve raw mined anchor
        const paintAnchor = matchedKey ? String(matchedKey) : anchor;

        if (semanticLabels.length) {
          const wantNorm = new Set(semanticLabels.map((s) => norm(s).trim()).filter(Boolean));

          for (const t of targets) {
            const tTitleNorm = norm(t.title).trim();

            // A) entity label matches target title
            if (tTitleNorm && wantNorm.has(tTitleNorm)) {
              mapped.push({
                t,
                titleMatch: 0.65,
                urlCoverage: urlCoverage(anchor, t.url),
                bm25Url: 0,
                via: "entityMap",
                entityMatch: 1,

                // ✅ Step 5.3 + 7.1: semantic meta + paint anchor
                entityIds,
                semanticLabels,
                paintAnchor,
                rawAnchor: anchor
              });
              continue;
            }

            // B) entity label matches one of target aliases
            const als = Array.isArray(t.aliases) ? t.aliases : [];
            for (const al of als) {
              const alNorm = norm(al).trim();
              if (alNorm && wantNorm.has(alNorm)) {
                mapped.push({
                  t,
                  titleMatch: 0.65,
                  urlCoverage: urlCoverage(anchor, t.url),
                  bm25Url: 0,
                  via: "entityMap",
                  entityMatch: 1,

                  // ✅ Step 5.3 + 7.1: semantic meta + paint anchor
                  entityIds,
                  semanticLabels,
                  paintAnchor,
                  rawAnchor: anchor
                });
                break;
              }
            }
          }
        }
      }

      // 2.5) Synonyms hook (fallback placeholder)
      // ✅ Step 5.3: entityMap wins — if entityMap has entries for this anchor, skip synonyms mapping
      if (
        mapped.length === 0 &&
        synonyms && typeof synonyms === "object" &&
        !(entityMap && typeof entityMap === "object" && Array.isArray(entityMap[norm(anchor).trim()]) && entityMap[norm(anchor).trim()].length)
      ) {
        const key = norm(anchor).trim();
        const synVal = synonyms[key];

        const wantTitles = [];
        if (typeof synVal === "string" && synVal.trim()) {
          wantTitles.push(synVal);
        } else if (Array.isArray(synVal)) {
          for (const s of synVal) if (typeof s === "string" && s.trim()) wantTitles.push(s);
        }

        if (wantTitles.length) {
          const wantNorm = new Set(wantTitles.map((s) => norm(s).trim()).filter(Boolean));

          for (const t of targets) {
            const tTitleNorm = norm(t.title).trim();
            if (!tTitleNorm) continue;

            if (wantNorm.has(tTitleNorm)) {
              mapped.push({
                t,
                titleMatch: 0.65,
                urlCoverage: urlCoverage(anchor, t.url),
                bm25Url: 0,
                via: "synonyms",
                synonymMatch: 1,
                entityIds: [],
                semanticLabels: wantTitles
              });
              continue;
            }

            const als = Array.isArray(t.aliases) ? t.aliases : [];
            for (const al of als) {
              const alNorm = norm(al).trim();
              if (alNorm && wantNorm.has(alNorm)) {
                mapped.push({
                  t,
                  titleMatch: 0.65,
                  urlCoverage: urlCoverage(anchor, t.url),
                  bm25Url: 0,
                  via: "synonyms",
                  synonymMatch: 1,
                  entityIds: [],
                  semanticLabels: wantTitles
                });
                break;
              }
            }
          }
        }
      }

      // 3) URL tokens fallback BM25 (Top-K 20)
      if (mapped.length === 0) {
        const q = tokenize(anchor);
        const scored = targets.map((t, i) => ({
          i,
          s: bm25Score(q, urlIndex.docs[i], urlIndex.idf, urlIndex.lens[i], urlIndex.avgdl)
        }));

        scored.sort((a, b) => b.s - a.s);

        for (const it of scored.slice(0, 20)) {
          if (it.s < 0.10) break;
          const t = targets[it.i];
          mapped.push({
            t,
            titleMatch: 0,
            urlCoverage: urlCoverage(anchor, t.url),
            bm25Url: it.s,
            via: "urlBM25"
          });
        }
      }



      // Build candidates with scoring
      for (const m of mapped) {
        const echo = jaccard(anchor, m.t.title || "");
        const titleEcho = echo >= 0.80 ? cfg.titleEchoPenalty : 0;

        const prominence = clamp01(1 - (sidx / Math.max(1, sections.length - 1)));

        const df = anchorDf.get(anchor) || 1;
        const rarity = clamp01(1 / (1 + Math.log(1 + df)));

        const hubs = Number(m.t.inboundLinks || 0);
        const hubPen = hubs > cfg.hubPenaltyThreshold ? cfg.hubPenalty : 0;
        const orphanBoost = hubs === 0 ? cfg.orphanBoost : 0;

        const score = clamp01(
          W.titleMatch * (m.titleMatch || 0) +
          W.urlCoverage * (m.urlCoverage || 0) +
          W.bm25Url * (m.bm25Url || 0) +
          W.prominence * prominence +
          W.rarity * rarity +
          orphanBoost - hubPen - titleEcho
        );

        candidates.push({
          section: sidx,


    anchor: (() => {
  // Always populate these fields for painter consistency
  const isEM = (m.via === "entityMap");

  const textVal = isEM && m.paintAnchor ? String(m.paintAnchor) : String(anchor);
  const rawVal  = isEM && m.rawAnchor   ? String(m.rawAnchor)   : String(anchor);

  // Painter-safe default: paint = text if present in paragraph, else paint = raw
  const secText = String(sections[sidx]?.text || "");
  const paintVal = secText.toLowerCase().includes(textVal.toLowerCase())
    ? textVal
    : rawVal;

  return { text: textVal, raw: rawVal, paint: paintVal };
})(),
      



          // paragraph metadata (if present)
          rb2: {
            paraIndex: sec.paraIndex ?? null,
            charStart: sec.charStart ?? null,
            charEnd: sec.charEnd ?? null,
            headingCtx: sec.headingCtx ?? null
          },

          // target + aliases
          target: {
            url: m.t.url,
            title: m.t.title,
            aliases: m.t.aliases || []
          },

          // scoring signals
          signals: {
            titleMatch: m.titleMatch || 0,
            urlCoverage: m.urlCoverage || 0,
            bm25Url: m.bm25Url || 0,
            prominence,
            rarity
          },

          penalties: { titleEcho: titleEcho ? echo : 0, hub: hubPen },
          boosts: { orphan: orphanBoost },

          score,
          via: m.via,

          // ✅ Step 5.3: semantic explanation payload (only for entityMap/synonyms)
          semantic: (m.via === "entityMap" || m.via === "synonyms")
            ? {
                source: m.via,
                entityIds: Array.isArray(m.entityIds) ? m.entityIds : [],
                labels: Array.isArray(m.semanticLabels) ? m.semanticLabels : []
              }
            : null
        });
      }
    }
  }

  // Adaptive floor (percentile)
  const scores = candidates.map((c) => c.score).sort((a, b) => a - b);
  const pIdx = Math.floor(scores.length * cfg.adaptivePercentile);
  const adaptiveFloor = scores.length ? scores[pIdx] : 0;

  const kept = candidates.filter((c) => c.score >= Math.max(0.20, adaptiveFloor));

  // ---- Caps enforcement ----
  // 1) per-target across doc
  const perTarget = new Map();
  kept.sort((a, b) => b.score - a.score);

  const kept1 = [];
  for (const c of kept) {
    const key = c.target.url;
    const cnt = perTarget.get(key) || 0;
    if (cnt >= cfg.perTargetMax) continue;
    perTarget.set(key, cnt + 1);
    kept1.push(c);
  }

  // 2) per-section
  const perSection = new Map();
  const kept2 = [];
  for (const c of kept1) {
    const s = c.section;
    const cnt = perSection.get(s) || 0;
    if (cnt >= cfg.perSectionMax) continue;
    perSection.set(s, cnt + 1);
    kept2.push(c);
  }

  // 3) per-200 words (rolling) - approximate positions
  const wordOffsets = cumulativeWordOffsets(sections);

  function anchorWordIndex(sectionIdx, anchorText) {
    const secText = sections[sectionIdx].text;
    const a = anchorText.toLowerCase();
    const pos = secText.toLowerCase().indexOf(a);
    if (pos < 0) return wordOffsets[sectionIdx];

    const before = secText.slice(0, pos);
    const wordsBefore = (before.match(/\b[\p{L}\p{N}'-]+\b/gu) || []).length;
    return wordOffsets[sectionIdx] + wordsBefore;
  }

  const placed = [];
  for (const c of kept2) {
    const idx = anchorWordIndex(c.section, c.anchor.text);
    const wStart = idx - 199, wEnd = idx + 199;

    const inWindow = placed.filter((p) => p.idx >= wStart && p.idx <= wEnd);
    if (inWindow.length >= cfg.per200WordsMax) continue;

    placed.push({ idx, c });
  }

  // Bucketize based on placed items
  const placedSorted = placed
    .sort((a, b) => b.c.score - a.c.score)
    .map((p) => p.c);

  // ✅ Step 4.1: Deduplicate by normalized phrase (anchor text)
  const seenPhrase = new Set();
  const dedupedPlaced = [];
  let dedupDropped = 0;

  for (const c of placedSorted) {
    const phrase = c?.anchor?.text || "";
    const key = norm(phrase).trim();
    if (!key) continue;
    if (seenPhrase.has(key)) {
      dedupDropped++;
      continue;
    }
    seenPhrase.add(key);
    dedupedPlaced.push(c);
  }

  const strongCut = Math.max(0.70, Math.max(0.20, adaptiveFloor) + 0.20);
  const midCut = Math.max(0.50, Math.max(0.20, adaptiveFloor) + 0.08);

  // ✅ Step 4.2 + 4.3:
  // Strong-first (literal) + Optional must pass semantic evidence gate (synonyms/include/entityMap placeholder)
  const recommended = [];
  const optional = [];

   let strongCount = 0;
  let optionalCount = 0;
  let optionalDroppedByGate = 0;

  // ✅ Step 6.3: dedup optional entityMap by entityId (one per entity per doc)
  const seenEntityIds = new Set();
  let optionalDroppedByEntityDedup = 0;

  for (const c of dedupedPlaced) {
    const isStrong = isLiteralStrong(
      c?.anchor?.text,
      c?.target?.title,
      c?.target?.aliases
    );

    if (isStrong) {
      strongCount++;
      recommended.push({ ...c, bucket: "strong" });
      continue;
    }

    // ✅ Step 4.3: Optional must pass evidence gate
    if (!passesOptionalEvidenceGate(c, cfg, synonyms)) {
      optionalDroppedByGate++;
      continue;
    }

    // ✅ Step 6.3: if optional is powered by entityMap, keep only one per entityId
    const src = c?.semantic?.source || c?.via;
    const ids = Array.isArray(c?.semantic?.entityIds) ? c.semantic.entityIds : [];

    if (src === "entityMap" && ids.length) {
      // if any id already used, skip this highlight
      let already = false;
      for (const id of ids) {
        const key = String(id || "").trim();
        if (!key) continue;
        if (seenEntityIds.has(key)) {
          already = true;
          break;
        }
      }
      if (already) {
        optionalDroppedByEntityDedup++;
        continue;
      }
      // mark all ids as used
      for (const id of ids) {
        const key = String(id || "").trim();
        if (key) seenEntityIds.add(key);
      }
    }

    optionalCount++;
    optional.push({ ...c, bucket: "optional" });
  }



  const placedSet = new Set(placedSorted);
  const hidden = candidates.filter((c) => !placedSet.has(c));

  const diagnostics = {
    sections: sections.length,
    anchorsFound: sectionAnchors.reduce((a, b) => a + b.length, 0),
    mappedCandidates: candidates.length,
    keptAfterFloor: kept.length,
    placed: (recommended.length + optional.length),
    dedupDropped,
    strongCount,
    optionalCount,
    optionalDroppedByGate,
    optionalDroppedByEntityDedup,
    adaptiveFloor,
    thresholds: { strongCut, midCut }
  };

  return { recommended, optional, hidden, meta: diagnostics };
}

// cumulative word offsets per section start
function cumulativeWordOffsets(sections) {
  const offs = [];
  let acc = 0;
  for (const s of sections) {
    offs.push(acc);
    acc += (s.text.match(/\b[\p{L}\p{N}'-]+\b/gu) || []).length;
  }
  return offs;
}

// ------------------------------ Runner API -------------------------------
/**
 * runRulebookV2 - main entry
 * @param {Object} opts
 * @param {string} [opts.html] - raw HTML of the article body (preferred)
 * @param {string} [opts.text] - fallback plain text if HTML not available
 * @param {Object} [opts.rb2Doc] - rb2.extract.v1 contract (preferred when present)
 * @param {Array}  opts.targets - [{url, title, aliases?, inboundLinks?}]
 * @param {Object} [opts.include] - force include map: {anchor -> url}
 * @param {Array}  [opts.block] - phrases to block completely
 * @param {Object} [opts.synonyms] - alias dictionary (placeholder semantic input)
 * @param {Object} [opts.entityMap] - entity map for semantic equivalence
 * @param {Object} [opts.config] - override RB2_DEFAULTS
 */
export function runRulebookV2(opts) {
  const cfg = { ...RB2_DEFAULTS, ...(opts?.config || {}) };

  let sections = [];
  if (opts?.rb2Doc && Array.isArray(opts.rb2Doc.paragraphs)) {
    sections = splitSectionsFromRb2Doc(opts.rb2Doc, cfg.minSectionLen);
  } else {
    sections = splitSections({ html: opts?.html, text: opts?.text, minSectionLen: cfg.minSectionLen });
  }

  const targets = buildTargets(opts?.targets || []);
  return mapAndScore({
    sections,
    targets,
    cfg,
    include: opts?.include || {},
    block: opts?.block || [],
    synonyms: opts?.synonyms || {},
    entityMap: opts?.entityMap || {}
  });
}

/**
Example Console usage (no DOM changes):

import { runRulebookV2 } from "./rulebook_v2_core.js";

// 1) Gather targets from your app (example using TITLE_INDEX persisted in localStorage)
const tiRaw = localStorage.getItem("linkcraftor_title_index_v2");
const ti = tiRaw ? JSON.parse(tiRaw) : null;
const targets = (ti?.entries || []).map(([key, val]) => ({
  url: val?.url || "",
  title: val?.title || "",
  aliases: [],
  inboundLinks: 0
}));

// 2) Grab the current article body
const bodyEl = document.getElementById("doc-content");
const html = bodyEl?.innerHTML || "";

// 3) Optional editor rules
const include = { "bmi for children": "/children-bmi-calculator/" };
const block = ["drink water"];

// 4) Run
const out = runRulebookV2({ html, targets, include, block });
console.log(out);
*/
