// public/assets/js/logic/autoLink.js
// Detect candidate phrases and prepare suggestions (titles & urls) for the IL modal.
// NOTE: No aliasToCanonical import; we only use phraseCoverageInTitle now.

import { normalizePhrase, getKeywords } from "./keywords.js";
import { phraseCoverageInTitle } from "../data/titleIndex.js";

/**
 * Analyze the editor text for candidate phrases and match them against other titles.
 * Returns { phrasesToHighlight: string[], suggestMap: Map<phrase, {titles:string[], urls:string[]}> }
 */
export function analyzeForHighlights({
  text,
  settings,
  stopwords,
  internalList = [],
  titleCatalog = [],       // [{ key, raw, docIndex, code }]
  currentDocIndex = -1,
  titleToUrls = new Map(), // Map<titleKey, { raw, urls:string[] }>
  minCoverage = 0.85,
}) {
  const candidates = new Set();

  // Derive candidate phrases from the current text:
  // - singles
  // - long-tail n-grams
  // - optional internal bucket entries (they still must match ≥85% to titles)
  const kws = getKeywords(text, settings, stopwords, internalList, [], []);
  for (const k of kws) {
    const p = normalizePhrase(k.word);
    if (p) candidates.add(p);
  }

  const phrasesToHighlight = [];
  const suggestMap = new Map(); // phrase -> { titles:string[], urls:string[] }

  const options = {
    includeNums: !!settings?.includeNums,
    minLen: settings?.minLen ?? 1,
    minPhraseLen: settings?.minPhraseLen ?? 2,
    stopwords: stopwords || new Set(),
  };

  for (const phrase of candidates) {
    let matchedTitles = [];
    const matchedUrlsSet = new Set();

    for (const t of titleCatalog) {
      if (t.docIndex === currentDocIndex) continue; // exclude current doc’s title/topic
      const s = phraseCoverageInTitle(phrase, t.raw, options);
      if (s >= minCoverage) {
        matchedTitles.push(t.raw);
        const pair = titleToUrls.get(t.key);
        if (pair && Array.isArray(pair.urls)) {
          for (const u of pair.urls) matchedUrlsSet.add(u);
        }
      }
    }

    if (matchedTitles.length > 0) {
      // De-dupe and keep a stable order
      matchedTitles = Array.from(new Set(matchedTitles));
      phrasesToHighlight.push(phrase);
      suggestMap.set(phrase, { titles: matchedTitles, urls: Array.from(matchedUrlsSet) });
    }
  }

  // Longest-first to minimize nested wrapping issues
  phrasesToHighlight.sort((a, b) => b.length - a.length);

  return { phrasesToHighlight, suggestMap };
}
