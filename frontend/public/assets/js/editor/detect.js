// assets/js/editor/detect.js
import { state } from "../core/state.js";
import { normalizeWord, isAlphaNumWord, normalizePhrase, escapeRegExp } from "../core/utils.js";
import { STOPWORDS } from "../data/stopwords.js";
import { INTERNAL_SET, EXTERNAL_SET, SEMANTIC_SET } from "../data/buckets.js";

export function computeWordCounts(text) {
  const counts = new Map();
  const S = state.settings;
  for (const raw of (text || "").split(/\s+/)) {
    const w = normalizeWord(raw);
    if (!w || !isAlphaNumWord(w)) continue;
    if (!S.includeNums && /^\d+([\.,]\d+)?$/.test(w)) continue;
    if (w.length < S.minLen) continue;
    if (STOPWORDS.has(w)) continue;
    counts.set(w, (counts.get(w) || 0) + 1);
  }
  return counts;
}
export function computeLongTailCounts(text) {
  const words = [];
  const S = state.settings;
  for (const raw of (text || "").split(/\s+/)) {
    const w = normalizeWord(raw);
    if (!w || !isAlphaNumWord(w)) continue;
    if (!S.includeNums && /^\d+([\.,]\d+)?$/.test(w)) continue;
    if (w.length < S.minLen) continue;
    if (STOPWORDS.has(w)) continue;
    words.push(w);
  }
  const counts = new Map();
  const maxN = 10;
  const minN = Math.max(2, Math.min(S.longtailMin, maxN));
  for (let n = minN; n <= maxN; n++) {
    for (let i = 0; i + n <= words.length; i++) {
      const phrase = words.slice(i, i + n).join(" ");
      const chars = phrase.replace(/\s+/g, "").length;
      if (chars < S.minPhraseLen) continue;
      counts.set(phrase, (counts.get(phrase) || 0) + 1);
    }
  }
  return counts;
}
export function countPhrase(text, phrase) {
  const safe = (text||"").toLowerCase();
  const pattern = escapeRegExp(phrase).replace(/\s+/g, "\\s+");
  const rx = new RegExp(`\\b(${pattern})\\b`, "g");
  let c = 0; while (rx.exec(safe)) c++;
  return c;
}
export function getClassForWordToken(tok){
  const n = normalizePhrase(tok);
  if (INTERNAL_SET.has(n)) return "kwd-int";
  if (EXTERNAL_SET.has(n)) return "kwd-ext";
  if (SEMANTIC_SET.has(n)) return "kwd-sem";
  return "kwd-sem";
}
export function getKeywords(text){
  const wordCounts = computeWordCounts(text);
  const ltCounts = computeLongTailCounts(text);
  const S = state.settings;
  const cap = (n)=> Math.min(S.maxCount, n);

  const semanticSingles = Array.from(wordCounts.entries()).map(([word, count]) => ({ word, count: cap(count), kind: "sem" }));
  const semanticLongs   = Array.from(ltCounts.entries()).map(([word, count]) => ({ word, count: cap(count), kind: "sem" }));

  function phraseItems(setLike, kind){
    const out=[];
    for (const p of setLike){
      const np = normalizePhrase(p);
      const cnt = countPhrase(text, np);
      if (cnt > 0) out.push({ word: np, count: cap(cnt), kind });
    }
    return out;
  }
  const internals = phraseItems(INTERNAL_SET, "int");
  const externals = phraseItems(EXTERNAL_SET, "ext");
  const semBucket = phraseItems(SEMANTIC_SET, "sem");

  const sortFn = (a,b)=> (b.count-a.count)||a.word.localeCompare(b.word);
  internals.sort(sortFn); externals.sort(sortFn);
  semanticSingles.sort(sortFn); semanticLongs.sort(sortFn); semBucket.sort(sortFn);

  const semantic = [...semBucket, ...semanticLongs, ...semanticSingles];
  const combined = [...internals, ...externals, ...semantic];
  const seen = new Set(); const final=[];
  for (const k of combined){ if (seen.has(k.word)) continue; seen.add(k.word); final.push(k); }
  return final;
}
