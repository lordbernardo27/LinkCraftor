/**
 * Rulebook v2 — Step 1: JSON-only engine (no DOM writes)
 * 
 * What this module does:
 *  - Parses the current article (HTML or plain text) into sections.
 *  - Extracts candidate anchors (2–4 token n-grams; connectors allowed).
 *  - Maps anchors to targets using lexical signals (titles/aliases + URL slugs).
 *  - Scores, filters with adaptive floor, and enforces caps:
 *      per-target (<=2), per-section (<=3), per-200 words rolling (<=4).
 *  - Returns JSON with {recommended, optional, hidden, meta, diagnostics}.
 *
 * Nothing is inserted into the DOM at this step.
 */

// --------------------------- Config (Balanced) ---------------------------
export const RB2_DEFAULTS = {
  mode: 'balanced',                 // 'strict' | 'balanced' | 'exploratory'
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
  // weights
  W: { titleMatch: 0.40, urlCoverage: 0.25, bm25Url: 0.20, prominence: 0.10, rarity: 0.05 },
  // connectors allowed inside anchors
  CONNECTORS: new Set(['of','for','in','on','to','and','with','vs','&','or','the','a','an','by','from']),
  // minimal stopwords (can be overridden)
  STOPWORDS: new Set(['the','a','an','and','or','for','to','of','in','on','with','by','from','at','as','is','are','was','were','be','been','being'])
};

// ------------------------------- Utilities -------------------------------
const clamp01 = (x)=> x<0?0:(x>1?1:x);
const uniq = (arr)=> Array.from(new Set(arr));
const foldAccents = (s)=> String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
const norm = (s)=> foldAccents(String(s||'').toLowerCase().replace(/[\u2018\u2019]/g,"'").replace(/[\u201C\u201D]/g,'"'));
const tokenize = (s)=> norm(s).replace(/[^\p{L}\p{N}\-']+/gu,' ').trim().split(/\s+/).filter(Boolean);
const isHeadingTag = (tag)=> /^(H1|H2|H3|H4|H5|H6)$/.test(tag);

function tokenSet(s){ return new Set(tokenize(s)); }
function jaccard(a,b){
  const A = tokenSet(a), B = tokenSet(b);
  if (!A.size || !B.size) return 0;
  let inter = 0; for (const t of A) if (B.has(t)) inter++;
  return inter / Math.max(A.size, B.size);
}
function urlTokens(u){
  try{
    const x = new URL(u);
    const host=(x.hostname||'').replace(/^www\./,'');
    const hostParts=host.split(/[.\-]+/).filter(Boolean);
    const pathParts=(x.pathname||'').split(/[\/_\-]+/).filter(Boolean);
    return hostParts.concat(pathParts).map(t=>t.toLowerCase());
  }catch{ return []; }
}
function urlCoverage(anchor, url){
  const a = tokenize(anchor);
  const u = urlTokens(url);
  if (!a.length || !u.length) return 0;
  let hit = 0; for (const t of a){ if (u.some(z=> z.includes(t) || t.includes(z))) hit++; }
  return clamp01(hit / a.length);
}
function simplePluralVariants(w){
  if (w.endsWith('ies')) return [w, w.slice(0,-3)+'y'];
  if (w.endsWith('es')) return [w, w.slice(0,-2)];
  if (w.endsWith('s')) return [w, w.slice(0,-1)];
  return [w, w+'s'];
}
function variantsForPhrase(s){
  const base = norm(s).trim();
  const hy2sp = base.replace(/\-/g,' ');
  const sp2hy = base.replace(/\s+/g,'-');
  const toks = tokenize(base);
  // naive plural/singular for last token
  const last = toks[toks.length-1]||'';
  const pluralV = simplePluralVariants(last).map(v=> toks.slice(0,-1).concat(v).join(' '));
  return uniq([base, hy2sp, sp2hy, ...pluralV]);
}

// ------------------------------ Sectionizing ------------------------------
export function splitSections({ html, text, minSectionLen = RB2_DEFAULTS.minSectionLen }){
  const sections = [];
  if (html) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(String(html), 'text/html');
    const blocks = Array.from(doc.body.querySelectorAll('p, li, td, blockquote, pre'));
    for (const el of blocks){
      const t = el.textContent||''; const len=t.trim().length;
      if (len >= minSectionLen) sections.push({ type: el.tagName, text: t, len, isHeading: false });
    }
    // capture headings (for prominence but avoid placement in Balanced)
    Array.from(doc.body.querySelectorAll('h1,h2,h3,h4,h5,h6')).forEach(h=>{
      const t = h.textContent||''; const len=t.trim().length;
      if (len >= minSectionLen) sections.push({ type: h.tagName, text: t, len, isHeading: true });
    });
  } else {
    const raw = String(text||'').replace(/\r\n/g,'\n');
    const parts = raw.split(/\n{2,}/).map(s=>s.trim()).filter(Boolean);
    parts.forEach(p=>{ if (p.length>=minSectionLen) sections.push({ type: 'P', text: p, len: p.length, isHeading: false }); });
  }
  // Keep stable order by original appearance (DOM order mostly preserved)
  return sections.map((s,i)=>({ ...s, idx: i }));
}

// ------------------------------ Anchor mining -----------------------------
export function extractAnchorsFromSection(section, cfg=RB2_DEFAULTS){
  const toks = tokenize(section.text);
  const out = new Set();
  for (let n=cfg.ngramMin;n<=cfg.ngramMax;n++){
    for (let i=0;i<=toks.length-n;i++){
      const gram = toks.slice(i,i+n);
      const content = gram.filter(t=> !cfg.STOPWORDS.has(t) && !cfg.CONNECTORS.has(t) );
      if (content.length < cfg.minContentTokens) continue;
      out.add(gram.join(' '));
    }
  }
  return Array.from(out);
}

// ---------------------------- Targets & aliases ----------------------------
export function buildTargets(rawTargets){
  // rawTargets: [{url, title, aliases?, inboundLinks?}]
  const clean = [];
  for (const t of (rawTargets||[])){
    if (!t || !(t.url || t.title)) continue;
    const url = t.url||''; const title = t.title||'';
    const aliases = uniq([title, ...(t.aliases||[])]).filter(Boolean);
    clean.push({ url, title, aliases, inboundLinks: Number(t.inboundLinks||0) });
  }
  return clean;
}

// Build a BM25 index over URL tokens only (host/path)
function buildUrlBM25(targets){
  const docs = targets.map(t=> urlTokens(t.url||'') );
  const N = docs.length||1;
  const dfs = new Map();
  const lens = docs.map(d=>d.length);
  const avgdl = lens.reduce((a,b)=>a+b,0)/N;
  for (const d of docs){ const seen=new Set(); for (const tok of d){ if(!seen.has(tok)){ seen.add(tok); dfs.set(tok,(dfs.get(tok)||0)+1); } } }
  const idf = (tok)=>{ const df = dfs.get(tok)||0; return Math.log( (N - df + 0.5) / (df + 0.5) + 1 ); };
  return { docs, idf, lens, avgdl };
}
function bm25Score(queryTokens, docTokens, idf, dl, avgdl, k1=1.2, b=0.75){
  if (!docTokens.length) return 0;
  const tf = new Map(); for (const t of docTokens) tf.set(t,(tf.get(t)||0)+1);
  let s = 0; const q = uniq(queryTokens);
  for (const t of q){ const f=tf.get(t)||0; if(!f) continue; const _idf=idf(t); const denom = f + k1*(1 - b + b*(dl/avgdl)); s += _idf * (f*(k1+1))/denom; }
  return clamp01(s/8);
}

// ------------------------------ Mapping & Scoring -------------------------
export function mapAndScore({ sections, targets, cfg=RB2_DEFAULTS, include={}, block=[], synonyms={} }){
  const W = cfg.W;
  const urlIndex = buildUrlBM25(targets);

  // Precompute rarity (IDF-ish) across doc for anchors
  const anchorDf = new Map();
  const sectionAnchors = sections.map(sec=> extractAnchorsFromSection(sec, cfg));
  for (const arr of sectionAnchors){ const seen=new Set(arr); for (const a of seen) anchorDf.set(a, (anchorDf.get(a)||0)+1); }

  // Build alias map for quick title matching
  const targetAliasTokens = targets.map(t=> uniq([t.title, ...(t.aliases||[])]).map(tokenize));

  const candidates = [];

  for (let sidx=0; sidx<sections.length; sidx++){
    const sec = sections[sidx];
    if (sec.isHeading && cfg.headingPlacement===false) continue; // we still score, but won't place in Balanced; we treat as low prominence

    for (const anchor of sectionAnchors[sidx]){
      if (Array.isArray(block) && block.some(b=> anchor===b)) continue;

      const variants = variantsForPhrase(anchor);

      // 1) Force-include / Memory accepted direct map
      const directUrl = include[anchor] || include[variants.find(v=> include[v])];

      let mapped = [];
      if (directUrl){
        const tgt = targets.find(t=> t.url===directUrl);
        if (tgt){ mapped.push({ t: tgt, titleMatch: 1, urlCoverage: urlCoverage(anchor, tgt.url), bm25Url: 1, via: 'include' }); }
      }

      // 2) Title/Alias lexical match
      if (mapped.length===0){
        for (let i=0;i<targets.length;i++){
          const t = targets[i];
          const aliasLists = targetAliasTokens[i]; // array of token arrays
          let tm = 0;
          for (const toks of aliasLists){
            const aliasStr = toks.join(' ');
            tm = Math.max(tm, jaccard(anchor, aliasStr));
          }
          if (tm >= 0.45){ // threshold for lexical grounding
            mapped.push({ t, titleMatch: tm, urlCoverage: urlCoverage(anchor, t.url), bm25Url: 0, via: 'title' });
          }
        }
      }

      // 3) URL tokens fallback BM25 (Top-K 20)
      if (mapped.length===0){
        const q = tokenize(anchor);
        const scored = targets.map((t,i)=> ({ i, s: bm25Score(q, urlIndex.docs[i], urlIndex.idf, urlIndex.lens[i], urlIndex.avgdl) }));
        scored.sort((a,b)=> b.s - a.s);
        for (const it of scored.slice(0,20)){
          if (it.s < 0.10) break; // weak grounding → skip
          const t = targets[it.i];
          mapped.push({ t, titleMatch: 0, urlCoverage: urlCoverage(anchor, t.url), bm25Url: it.s, via: 'urlBM25' });
        }
      }

      // Build candidates with scoring
      for (const m of mapped){
        // title echo penalty
        const echo = jaccard(anchor, m.t.title||'');
        const titleEcho = echo >= 0.80 ? cfg.titleEchoPenalty : 0;
        // prominence: earlier sections get more
        const prominence = clamp01( 1 - (sidx / Math.max(1, sections.length-1)) );
        // rarity: inverse of DF across sections
        const df = anchorDf.get(anchor)||1; const rarity = clamp01(1 / (1 + Math.log(1+df)));
        // hub/orphan
        const hubs = Number(m.t.inboundLinks||0);
        const hubPen = hubs > cfg.hubPenaltyThreshold ? cfg.hubPenalty : 0;
        const orphanBoost = hubs === 0 ? cfg.orphanBoost : 0;

        const score = clamp01(
          W.titleMatch*m.titleMatch +
          W.urlCoverage*m.urlCoverage +
          W.bm25Url*m.bm25Url +
          W.prominence*prominence +
          W.rarity*rarity +
          orphanBoost - hubPen - titleEcho
        );

        candidates.push({
          section: sidx,
          anchor: { text: anchor },
          target: { url: m.t.url, title: m.t.title },
          signals: { titleMatch: m.titleMatch, urlCoverage: m.urlCoverage, bm25Url: m.bm25Url, prominence, rarity },
          penalties: { titleEcho: titleEcho?echo:0, hub: hubPen },
          boosts: { orphan: orphanBoost },
          score, via: m.via
        });
      }
    }
  }

  // Adaptive floor (percentile)
  const scores = candidates.map(c=>c.score).sort((a,b)=>a-b);
  const pIdx = Math.floor(scores.length * cfg.adaptivePercentile);
  const adaptiveFloor = scores.length ? scores[pIdx] : 0;
  let kept = candidates.filter(c=> c.score >= Math.max(0.20, adaptiveFloor) );

  // ---- Caps enforcement ----
  // 1) per-target across doc
  const perTarget = new Map();
  kept.sort((a,b)=> b.score - a.score);
  const kept1 = [];
  for (const c of kept){
    const key = c.target.url;
    const cnt = perTarget.get(key)||0;
    if (cnt >= cfg.perTargetMax) continue;
    perTarget.set(key, cnt+1); kept1.push(c);
  }
  // 2) per-section
  const perSection = new Map();
  const kept2 = [];
  for (const c of kept1){
    const s = c.section; const cnt=perSection.get(s)||0; if (cnt>=cfg.perSectionMax) continue; perSection.set(s,cnt+1); kept2.push(c);
  }
  // 3) per-200 words (rolling) — approximate positions
  const wordOffsets = cumulativeWordOffsets(sections);
  function anchorWordIndex(sectionIdx, anchorText){
    // naive: find first match; compute word index by splitting up to pos
    const secText = sections[sectionIdx].text;
    const a = anchorText.toLowerCase();
    const pos = secText.toLowerCase().indexOf(a);
    if (pos < 0) return wordOffsets[sectionIdx];
    const before = secText.slice(0,pos);
    const wordsBefore = (before.match(/\b[\p{L}\p{N}'-]+\b/gu)||[]).length;
    return wordOffsets[sectionIdx] + wordsBefore;
  }
  const placed = [];
  for (const c of kept2){
    const idx = anchorWordIndex(c.section, c.anchor.text);
    const wStart = idx - 199, wEnd = idx + 199; // 200-word window centered
    const inWindow = placed.filter(p=> p.idx>=wStart && p.idx<=wEnd);
    if (inWindow.length >= cfg.per200WordsMax){
      // skip this placement (JSON step: we don't reshuffle existing ones)
      continue;
    }
    placed.push({ idx, c });
  }

  // Bucketize into recommended/optional based on distribution
  const placedSorted = placed.sort((a,b)=> b.c.score - a.c.score).map(p=>p.c);
  const strongCut = Math.max(0.70, Math.max(0.20, adaptiveFloor) + 0.20);
  const midCut = Math.max(0.50, Math.max(0.20, adaptiveFloor) + 0.08);
  const recommended = placedSorted.filter(c=> c.score >= strongCut);
  const optional    = placedSorted.filter(c=> c.score < strongCut && c.score >= midCut);
  const hidden      = candidates.filter(c=> !placedSorted.includes(c));

  // Diagnostics
  const diagnostics = {
    sections: sections.length,
    anchorsFound: sectionAnchors.reduce((a,b)=>a+b.length,0),
    mappedCandidates: candidates.length,
    keptAfterFloor: kept.length,
    placed: placedSorted.length,
    adaptiveFloor,
    thresholds: { strongCut, midCut },
  };

  return { recommended, optional, hidden, meta: diagnostics };
}

// cumulative word offsets per section start
function cumulativeWordOffsets(sections){
  const offs = []; let acc=0;
  for (const s of sections){ offs.push(acc); acc += (s.text.match(/\b[\p{L}\p{N}'-]+\b/gu)||[]).length; }
  return offs;
}

// ------------------------------ Runner API -------------------------------
/**
 * runRulebookV2 — main entry
 * @param {Object} opts
 * @param {string} [opts.html] - raw HTML of the article body (preferred)
 * @param {string} [opts.text] - fallback plain text if HTML not available
 * @param {Array}  opts.targets - [{url, title, aliases?, inboundLinks?}]
 * @param {Object} [opts.include] - force include map: {anchor -> url}
 * @param {Array}  [opts.block] - phrases to block completely
 * @param {Object} [opts.synonyms] - alias dictionary (unused in step 1 but reserved)
 * @param {Object} [opts.config] - override RB2_DEFAULTS
 */
export function runRulebookV2(opts){
  const cfg = { ...RB2_DEFAULTS, ...(opts?.config||{}) };
  const sections = splitSections({ html: opts?.html, text: opts?.text, minSectionLen: cfg.minSectionLen });
  const targets  = buildTargets(opts?.targets||[]);
  return mapAndScore({ sections, targets, cfg, include: opts?.include||{}, block: opts?.block||[], synonyms: opts?.synonyms||{} });
}

// ------------------------------ How to use -------------------------------
/**
Example Console usage (no DOM changes):

import { runRulebookV2 } from './rulebook_v2_core.js';

// 1) Gather targets from your app (example using TITLE_INDEX persisted in localStorage)
const tiRaw = localStorage.getItem('linkcraftor_title_index_v2');
const ti = tiRaw ? JSON.parse(tiRaw) : null;
const targets = (ti?.entries||[]).map(([key, val])=> ({ url: val?.url||'', title: val?.title||'', aliases: [], inboundLinks: 0 }));

// 2) Grab the current article body
const bodyEl = document.getElementById('doc-content');
const html = bodyEl?.innerHTML || '';

// 3) Optional editor rules
const include = { 'bmi for children': '/children-bmi-calculator/' };
const block = ['drink water'];

// 4) Run
const out = runRulebookV2({ html, targets, include, block });
console.log(out);
*/
