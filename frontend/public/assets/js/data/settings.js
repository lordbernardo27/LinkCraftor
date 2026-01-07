// public/assets/js/data/settings.js
// Centralized settings/stopwords/buckets storage + defaults

import { KEYS, lsGet, lsSet, lsDel } from "../core/storage.js";

/** Keyword settings defaults */
export const defaultSettings = {
  maxPerToken: 3,
  maxCount: 3,
  minLen: 3,
  minPhraseLen: 4,
  includeNums: false,
  longtailMin: 2,
};

/** Built-in stopwords (base list; user additions are merged on load) */
export const DEFAULT_STOPWORDS = [
  "the","a","an","and","or","but","if","then","else","for","to","of","in","on","at","by",
  "with","as","from","into","over","under","up","down","out","than","so","no","not",
  "i","me","my","mine","we","our","ours","you","your","yours","he","him","his","she","her","hers",
  "they","them","their","theirs","it","its","is","are","was","were","be","been","being","do","does","did","done","can","could",
  "should","would","will","just","very","too","also","even","like","more","such","people","that","this","might","isn’t","still"
];

/* ---------- Settings ---------- */
export function loadSettings() {
  const saved = lsGet(KEYS.SETTINGS, null);
  return saved ? { ...defaultSettings, ...saved } : { ...defaultSettings };
}
export function saveSettings(settings) {
  lsSet(KEYS.SETTINGS, settings);
}
export function resetSettings() {
  lsDel(KEYS.SETTINGS);
  return { ...defaultSettings };
}

/* ---------- Stopwords ---------- */
export function loadStopwords() {
  const arr = lsGet(KEYS.STOPWORDS, []);
  return Array.isArray(arr) ? arr : [];
}
export function saveStopwords(list) {
  lsSet(KEYS.STOPWORDS, list || []);
}
export function resetStopwords() {
  lsDel(KEYS.STOPWORDS);
}

/* ---------- Buckets (internal/external/semantic) ---------- */
export function loadBuckets() {
  const internal = lsGet(KEYS.INTERNAL, []);
  const external = lsGet(KEYS.EXTERNAL, []);
  const semantic = lsGet(KEYS.SEMANTIC, []);
  return {
    internal: Array.isArray(internal) ? internal : [],
    external: Array.isArray(external) ? external : [],
    semantic: Array.isArray(semantic) ? semantic : [],
  };
}
export function saveBuckets({ internal = [], external = [], semantic = [] } = {}) {
  lsSet(KEYS.INTERNAL, internal);
  lsSet(KEYS.EXTERNAL, external);
  lsSet(KEYS.SEMANTIC, semantic);
}
export function resetBuckets() {
  lsDel(KEYS.INTERNAL);
  lsDel(KEYS.EXTERNAL);
  lsDel(KEYS.SEMANTIC);
}
