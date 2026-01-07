// public/assets/js/logic/keywords.js
// Keyword + phrase detection utilities (counting, long-tail n-grams, etc.)

import { escapeRegExp } from "../core/dom.js";

/* ------------------------------ Local helpers ----------------------------- */

function normalizeWord(w) {
  return (w || "").toLowerCase().trim().replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, "");
}
function isAlphaNumWord(w){ return /^[\p{L}\p{N}]+$/u.test(w); }

/** Normalize phrases to lowercase + single spaces */
export function normalizePhrase(s) { return (s || "").toLowerCase().trim().replace(/\s+/g, " "); }

/* ------------------------------- API: counts ------------------------------- */

/**
 * Count single-word tokens respecting settings + stopwords.
 * @param {string} text
 * @param {{ includeNums: boolean, minLen: number }} settings
 * @param {Set<string>} stopwords
 */
export function computeWordCounts(text, settings, stopwords) {
  const counts = new Map();
  for (const raw of (text || "").split(/\s+/)) {
    const w = normalizeWord(raw);
    if (!w || !isAlphaNumWord(w)) continue;
    if (!settings?.includeNums && /^\d+([\.,]\d+)?$/.test(w)) continue;
    if (w.length < (settings?.minLen ?? 3)) continue;
    if (stopwords?.has?.(w)) continue;
    counts.set(w, (counts.get(w) || 0) + 1);
  }
  return counts;
}

/**
 * Count n-gram phrases (2..10) under long-tail rules.
 * @param {string} text
 * @param {{ includeNums: boolean, minLen: number, longtailMin: number, minPhraseLen: number }} settings
 * @param {Set<string>} stopwords
 */
export function computeLongTailCounts(text, settings, stopwords) {
  const words = [];
  for (const raw of (text || "").split(/\s+/)) {
    const w = normalizeWord(raw);
    if (!w || !isAlphaNumWord(w)) continue;
    if (!settings?.includeNums && /^\d+([\.,]\d+)?$/.test(w)) continue;
    if (w.length < (settings?.minLen ?? 3)) continue;
    if (stopwords?.has?.(w)) continue;
    words.push(w);
  }
  const counts = new Map();
  const maxN = 10;
  const minN = Math.max(2, Math.min(settings?.longtailMin ?? 2, maxN));
  for (let n = minN; n <= maxN; n++) {
    for (let i = 0; i + n <= words.length; i++) {
      const phrase = words.slice(i, i + n).join(" ");
      const chars = phrase.replace(/\s+/g, "").length;
      if (chars < (settings?.minPhraseLen ?? 4)) continue;
      counts.set(phrase, (counts.get(phrase) || 0) + 1);
    }
  }
  return counts;
}

/**
 * Count occurrences of a phrase in text with word-boundary tolerance for whitespace.
 * @param {string} text
 * @param {string} phrase
 */
export function countPhrase(text, phrase) {
  const safe = (text||"").toLowerCase();
  const pattern = escapeRegExp(phrase).replace(/\s+/g, "\\s+");
  const rx = new RegExp(`\\b(${pattern})\\b`, "g");
  let c = 0; while (rx.exec(safe)) c++;
  return c;
}

/* ------------------------------- API: kinds --------------------------------*/

/**
 * Decide visual class for a token based on membership in sets.
 * @param {string} token
 * @param {{ internalSet: Set<string>, externalSet: Set<string>, semanticSet: Set<string> }} sets
 */
export function getClassForWordToken(token, sets) {
  const n = normalizePhrase(token);
  if (sets?.internalSet?.has?.(n)) return "kwd-int";
  if (sets?.externalSet?.has?.(n)) return "kwd-ext";
  if (sets?.semanticSet?.has?.(n)) return "kwd-sem";
  return "kwd-sem";
}

/* ------------------------------- API: main ---------------------------------*/

/**
 * Qualify phrase with settings.
 * @param {string} phrase
 * @param {{ includeNums: boolean, minLen: number, minPhraseLen: number }} settings
 */
export function qualifiesPhrase(phrase, settings){
  const compactLen = (phrase || "").replace(/\s+/g,"").length;
  if (compactLen < (settings?.minPhraseLen ?? 4)) return false;
  if (!settings?.includeNums && /^\d+([\.,]\d+)?$/.test((phrase || "").replace(/\s+/g,""))) return false;
  const tokens = (phrase || "").split(/\s+/).map(normalizeWord).filter(Boolean);
  if (!tokens.length) return false;
  if (tokens.some(w => w.length < (settings?.minLen ?? 3))) return false;
  return true;
}

/**
 * Compute final keyword list combining buckets + long-tail + singles.
 * @param {string} text
 * @param {{ maxCount:number, includeNums:boolean, minLen:number, minPhraseLen:number, longtailMin:number }} settings
 * @param {Set<string>} stopwords  // IMPORTANT: must be normalized(lowercase) words
 * @param {string[]} internalList  // normalized phrases
 * @param {string[]} externalList  // normalized phrases
 * @param {string[]} semanticList  // normalized phrases
 * @returns {Array<{ word:string, count:number, kind:'int'|'ext'|'sem' }>}
 */
export function getKeywords(text, settings, stopwords, internalList=[], externalList=[], semanticList=[]) {
  const wordCounts = computeWordCounts(text, settings, stopwords);
  const ltCounts   = computeLongTailCounts(text, settings, stopwords);
  const cap = (n) => Math.min(settings?.maxCount ?? 3, n);

  const semanticSingles = Array.from(wordCounts.entries()).map(([word, count]) => ({ word, count: cap(count), kind: "sem" }));
  const semanticLongs   = Array.from(ltCounts.entries()).map(([word, count])  => ({ word, count: cap(count), kind: "sem" }));

  function phraseItems(list, kind) {
    const out = [];
    for (const p of list) {
      const np = normalizePhrase(p);
      if (!qualifiesPhrase(np, settings)) continue;
      const cnt = countPhrase(text, np);
      if (cnt > 0) out.push({ word: np, count: cap(cnt), kind });
    }
    return out;
  }

  const internals = phraseItems(internalList, "int");
  const externals = phraseItems(externalList, "ext");
  const semBucket = phraseItems(semanticList, "sem");

  const sortFn = (a,b)=> (b.count-a.count)||a.word.localeCompare(b.word);
  internals.sort(sortFn); externals.sort(sortFn);
  semanticSingles.sort(sortFn); semanticLongs.sort(sortFn); semBucket.sort(sortFn);

  const semantic = [...semBucket, ...semanticLongs, ...semanticSingles];
  const combined = [...internals, ...externals, ...semantic];
  const seen = new Set(); const final = [];
  for (const k of combined) { if (seen.has(k.word)) continue; seen.add(k.word); final.push(k); }
  return final;
}
