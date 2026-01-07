// Lightweight loader + resolver for Entity Map (fallbacks-only friendly)
export async function loadEntityMap() {
  const res = await fetch("/assets/data/entity_map.json", { cache: "no-store" });
  const raw = await res.json();
  return buildIndex(raw);
}

function buildIndex(entities) {
  const byId = new Map();
  const aliasToId = new Map();
  const regexes = []; // [{re: RegExp, id}]

  for (const e of entities) {
    byId.set(e.id, e);
    (e.aliases || []).forEach(a => aliasToId.set(String(a||"").toLowerCase(), e.id));
    (e.patterns || []).forEach(p => { try { regexes.push({ re: new RegExp(p, "i"), id: e.id }); } catch {} });
  }
  return { byId, aliasToId, regexes };
}

export function resolveEntity(text, idx) {
  if (!idx || !text) return null;
  const t = String(text).toLowerCase().trim();
  const id1 = idx.aliasToId.get(t);
  if (id1) return idx.byId.get(id1);
  for (const { re, id } of idx.regexes) { try { if (re.test(text)) return idx.byId.get(id); } catch {} }
  return null;
}

export function getInternalTarget(entity) {
  return entity?.internal?.url
    ? { url: entity.internal.url, anchor: entity.internal.anchor || entity.labels?.canonical || "" }
    : null;
}

export function getExternalSeeds(entity, regionCode = "GH") {
  const reg = entity?.external?.region_overrides?.[regionCode] || [];
  const pref = entity?.external?.preferred || [];
  return [...reg, ...pref]; // [{domain,url}]
}

export function shouldSuppress(entity, ctx = {}) {
  const s = entity?.suppress || {};
  if (s.in_titles && ctx.inTitle) return true;
  if (typeof s.max_links_per_page === "number" && (ctx.entityLinkCounts?.[entity.id] || 0) >= s.max_links_per_page) return true;
  return false;
}
