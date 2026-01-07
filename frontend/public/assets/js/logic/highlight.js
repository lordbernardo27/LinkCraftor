// public/assets/js/logic/highlight.js
// Highlight engine: find phrases that match ≥85% with other docs' titles/topics,
// then insert <mark> nodes. Highlights appear only when invoked by Auto Link.

import { escapeRegExp } from "../core/dom.js";
import { getKeywords } from "./keywords.js";

/** -------- Token helpers (phrase ↔ title coverage) -------- **/

function normalizeWord(w) {
  return (w || "").toLowerCase().trim().replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, "");
}

function tokenizeForMatch(s, settings, stopwords) {
  const text = (s || "")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]+/gu, " ");
  const raw = text.split(/\s+/).map(normalizeWord).filter(Boolean);
  const out = [];
  for (const w of raw) {
    if (!settings?.includeNums && /^\d+([\.,]\d+)?$/.test(w)) continue;
    if (stopwords?.has?.(w)) continue;
    if ((settings?.minLen ?? 3) > 1 && w.length < settings.minLen) continue;
    out.push(w);
  }
  return out;
}

/**
 * Compute coverage of candidate phrase tokens against a title/topic tokens.
 * We count a token as matched if title token includes phrase token or vice-versa.
 * @returns {number} 0..1
 */
export function phraseCoverageInTitle(phrase, title, settings, stopwords) {
  const pTokens = tokenizeForMatch(phrase, settings, stopwords);
  if (pTokens.length === 0) return 0;
  const tTokens = tokenizeForMatch(title, settings, stopwords);
  if (tTokens.length === 0) return 0;

  let hit = 0;
  for (const w of pTokens) {
    const ok = tTokens.some(tok => tok.includes(w) || w.includes(tok));
    if (ok) hit++;
  }
  return hit / pTokens.length;
}

/** -------- Highlight generation (triggered by Auto Link) -------- **/

/**
 * Find phrases in the document that match ≥minCoverage with OTHER docs' titles.
 * Candidate phrases are:
 *  - long-tail and single-word items produced by getKeywords()
 *  - optional Internal bucket entries (merged in by getKeywords args)
 *
 * @param {Object} args
 * @param {HTMLElement} args.viewerEl            - the editable viewer
 * @param {Map} args.titleIndex                  - Map<canonicalKey, {title, urls?}>
 * @param {string} args.currentTitle             - raw title of current doc (exclude)
 * @param {Object} args.settings                 - KW_SETTINGS
 * @param {Set<string>} args.stopwords           - STOPWORDS Set
 * @param {string[]} args.internalList           - bucket (optional/additive)
 * @param {number} args.minCoverage              - default 0.85
 * @returns {{phrases: string[], matches: Map<string, Array<{key:string,title:string,score:number}>>}}
 */
export function computePhrasesByTitleMatch({
  viewerEl,
  titleIndex,
  currentTitle,
  settings,
  stopwords,
  internalList = [],
  minCoverage = 0.85,
}) {
  const text = viewerEl?.textContent || "";
  const currentTitleNorm = (currentTitle || "").toLowerCase().trim().replace(/\s+/g, " ");

  // Collect candidate phrases via keyword engine (includes internalList as "internals")
  const kws = getKeywords(
    text,
    settings,
    stopwords,
    internalList,    // internal list
    [],              // external list (not used for matching)
    []               // semantic overrides (not needed here)
  );

  const candidates = [];
  const seen = new Set();
  for (const k of kws) {
    const p = (k.word || "").toLowerCase().trim().replace(/\s+/g, " ");
    if (!p) continue;
    if (seen.has(p)) continue;
    seen.add(p);
    candidates.push(p);
  }

  // Evaluate coverage for each phrase against all OTHER titles
  const phrases = [];
  const matches = new Map(); // phrase -> [{key,title,score}, ...]

  for (const phrase of candidates) {
    let bestList = [];
    titleIndex.forEach((val, key) => {
      const t = val?.title || "";
      if (!t) return;
      if (key === currentTitleNorm) return; // exclude current doc title
      const score = phraseCoverageInTitle(phrase, t, settings, stopwords);
      if (score >= minCoverage) {
        bestList.push({ key, title: t, score });
      }
    });

    if (bestList.length) {
      // sort high to low score, then title asc
      bestList.sort((a, b) => (b.score - a.score) || a.title.localeCompare(b.title));
      phrases.push(phrase);
      matches.set(phrase, bestList);
    }
  }

  // Sort phrases longest-first to help avoid partial overlaps during marking
  phrases.sort((a, b) => b.length - a.length);

  return { phrases, matches };
}

/** -------- DOM helpers for mark insertion & counting -------- **/

/**
 * Remove existing highlight marks (<mark class="kwd-int">) in the viewer.
 * @param {HTMLElement} viewerEl
 */
export function unwrapMarks(viewerEl) {
  if (!viewerEl) return;
  const marks = viewerEl.querySelectorAll("mark.kwd-int");
  marks.forEach((m) => {
    const t = document.createTextNode(m.textContent || "");
    m.parentNode.replaceChild(t, m);
  });
}

/**
 * Insert <mark> wrappers for the provided phrases.
 * Skips text inside existing <A> or <MARK>.
 * Attaches a data-matches attribute with the matched title keys (JSON).
 *
 * @param {HTMLElement} viewerEl
 * @param {string[]} phrases
 * @param {Set<string>} linkedSet
 * @param {Map<string,Array<{key:string,title:string,score:number}>>} matches
 * @returns {number} total marks added
 */
export function highlightInViewer(viewerEl, phrases = [], linkedSet = new Set(), matches = new Map()) {
  if (!viewerEl || phrases.length === 0) return 0;

  const walker = document.createTreeWalker(viewerEl, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      let p = node.parentNode;
      while (p && p !== viewerEl) {
        if (p.nodeType === 1 && (p.tagName === "A" || p.tagName === "MARK")) return NodeFilter.FILTER_REJECT;
        p = p.parentNode;
      }
      return NodeFilter.FILTER_ACCEPT;
    },
  });

  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);

  let added = 0;
  for (const tn of nodes) {
    let text = tn.nodeValue;
    let changed = false;

    for (const phrase of phrases) {
      if (linkedSet.has(phrase)) continue; // don't re-highlight linked phrases
      const escaped = escapeRegExp(phrase).replace(/\s+/g, "\\s+");
      const rx = new RegExp(`\\b(${escaped})\\b`, "gi");
      if (!rx.test(text)) continue;

      const matchMeta = matches.get(phrase) || [];
      const dataAttr = encodeURIComponent(JSON.stringify(matchMeta.map(m => m.key)));

      text = text.replace(
        rx,
        (m) => `<mark class="kwd-int" data-phrase="${encodeURIComponent(phrase)}" data-matches="${dataAttr}" tabindex="0">${m}</mark>`
      );
      changed = true;
    }

    if (changed) {
      const frag = document.createElement("span");
      frag.innerHTML = text;
      added += frag.querySelectorAll("mark.kwd-int").length;
      tn.parentNode.replaceChild(frag, tn);
    }
  }
  return added;
}

/**
 * Count current highlight marks in the viewer.
 * @param {HTMLElement} viewerEl
 * @returns {number}
 */
export function countHighlights(viewerEl) {
  if (!viewerEl) return 0;
  return viewerEl.querySelectorAll("mark.kwd-int").length;
}

/**
 * Update a small badge element with the current count of highlight marks.
 * @param {HTMLElement} viewerEl
 * @param {HTMLElement} badgeEl
 */
export function updateHighlightBadge(viewerEl, badgeEl) {
  if (!badgeEl) return;
  const count = viewerEl ? countHighlights(viewerEl) : 0;
  badgeEl.textContent = String(count);
}
