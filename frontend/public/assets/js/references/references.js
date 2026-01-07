// assets/js/references/references.js
// Free-sources external reference aggregator (compatible with your providers.json schema)
//
// Exports: getExternalReferences(query: string, { limit = 8 } = {}): Promise<Array<Ref>>
// Ref = { id, title, url, provider, score }
//
// Notes
// - Reads providers from ./providers.json (your pasted list).
// - Uses known endpoint adapters for common providers (Wikipedia family, Crossref, OpenAlex, etc).
// - Honors optional window.LC_PROXY(url) for CORS (e.g., `${API_BASE}/api/proxy?url=...`).
// - Honors optional window.LC_KEYS = { PROVIDER_ID: "key", ... } for key-based providers.
// - Gracefully ignores providers that fail or lack CORS; returns top-N by score.

const DEFAULT_TIMEOUT_MS = 6000;

function norm(s){ return String(s||"").toLowerCase().trim(); }
function tokens(s){ return norm(s).split(/\s+/).filter(Boolean); }
function uniqBy(arr, keyFn){ const out=[]; const seen=new Set(); for(const it of arr){ const k=keyFn(it); if(seen.has(k)) continue; seen.add(k); out.push(it);} return out; }
function clamp01(x){ return x<0?0:x>1?1:x; }

function withTimeout(promise, ms = DEFAULT_TIMEOUT_MS){
  return new Promise((resolve) => {
    const t = setTimeout(() => resolve({ ok:false, data:null, err:"timeout" }), ms);
    promise.then(
      data => { clearTimeout(t); resolve({ ok:true, data }); },
      err  => { clearTimeout(t); resolve({ ok:false, data:null, err:String(err) }); }
    );
  });
}

async function fetchJSON(url, init){
  try{
    const u = (typeof window.LC_PROXY === "function") ? window.LC_PROXY(url) : url;
    const res = await fetch(u, { ...init, headers: { Accept: "application/json", ...(init?.headers||{}) }});
    if(!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }catch(e){ throw e; }
}

async function fetchTEXT(url, init){
  try{
    const u = (typeof window.LC_PROXY === "function") ? window.LC_PROXY(url) : url;
    const res = await fetch(u, init);
    if(!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.text();
  }catch(e){ throw e; }
}

function getKey(providerId){
  // Optional client-side key registry
  // e.g., window.LC_KEYS = { SEMANTIC_SCHOLAR_KEY: "...", ... }
  try{
    const k = window.LC_KEYS || {};
    // accept both the exact id and UPPER_SNAKE id
    return k[providerId] || k[String(providerId||"").toUpperCase()];
  }catch{ return ""; }
}

function scoreByOverlap(query, text, base = 0){
  if(!query || !text) return base;
  const q = new Set(tokens(query));
  const t = new Set(tokens(text));
  if(!q.size || !t.size) return base;
  let inter = 0; q.forEach(w => { if(t.has(w)) inter++; });
  const ratio = inter / Math.max(1, q.size, t.size);
  return base + Math.min(1, ratio * 1.2);
}

function weightTrust(score, trust){ return score + clamp01(Number(trust||0)) * 0.25; } // small trust bump

/* ---------------------------------------------
   Adapters (by provider id or family)
--------------------------------------------- */

// MediaWiki search (Wikipedia, Wiktionary, Wikiquote, Commons, Wikisource)
async function mediaWikiSearch(baseUrl, q, providerName){
  const url = `${baseUrl.replace(/\/$/,'')}/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(q)}&utf8=&format=json&origin=*`;
  const j = await fetchJSON(url);
  const items = (j?.query?.search || []).slice(0, 12);
  return items.map(s => {
    const title = s?.title || "";
    const page = `${baseUrl.replace(/\/$/,'')}/wiki/${encodeURIComponent(title.replace(/\s+/g,'_'))}`;
    const sScore = scoreByOverlap(q, `${title} ${s?.snippet||""}`, 0.25);
    return { id:`mw:${title}`, title, url:page, provider: providerName, score: sScore };
  });
}

// Wikidata SPARQL label contains query
async function wikidataSparql(q){
  const endpoint = "https://query.wikidata.org/sparql";
  const sparql = `
    SELECT ?item ?itemLabel WHERE {
      ?item rdfs:label ?label .
      FILTER(CONTAINS(LCASE(?label), LCASE("${q.replace(/"/g,'\\"')}")))
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    } LIMIT 12
  `.trim();
  const url = `${endpoint}?format=json&query=${encodeURIComponent(sparql)}`;
  const j = await fetchJSON(url);
  const items = (j?.results?.bindings || []).slice(0, 12);
  return items.map(b => {
    const id  = (b?.item?.value||"").split("/").pop();
    const lbl = b?.itemLabel?.value || id;
    const url = `https://www.wikidata.org/wiki/${id}`;
    const sScore = scoreByOverlap(q, lbl, 0.20);
    return { id:`wd:${id}`, title: lbl, url, provider: "Wikidata", score: sScore };
  });
}

// DBpedia SPARQL label contains query
async function dbpediaSparql(q){
  const endpoint = "https://dbpedia.org/sparql";
  const sparql = `
    SELECT ?s ?label WHERE {
      ?s rdfs:label ?label .
      FILTER ( lang(?label) = "en" && CONTAINS(LCASE(?label), LCASE("${q.replace(/"/g,'\\"')}")) )
    } LIMIT 12
  `.trim();
  const url = `${endpoint}?format=application%2Fsparql-results%2Bjson&query=${encodeURIComponent(sparql)}`;
  const j = await fetchJSON(url);
  const items = (j?.results?.bindings || []).slice(0, 12);
  return items.map(b => {
    const url = b?.s?.value || "";
    const title = b?.label?.value || url;
    const sScore = scoreByOverlap(q, title, 0.18);
    return { id:`dbp:${title}`, title, url, provider: "DBpedia", score: sScore };
  }).filter(x => x.url);
}

// Crossref
async function crossrefSearch(baseUrl, q){
  const url = `${baseUrl.replace(/\/$/,'')}/works?query=${encodeURIComponent(q)}&rows=8`;
  const j = await fetchJSON(url);
  const items = (j?.message?.items || []).slice(0, 8);
  return items.map(s => {
    const title = Array.isArray(s?.title) ? s.title[0] : (s?.title || "");
    const url = s?.URL || s?.link?.[0]?.URL || "";
    const sScore = scoreByOverlap(q, `${title} ${s?.container_title||""}`, 0.22);
    return { id:`cr:${s?.DOI||title}`, title, url, provider: "Crossref", score: sScore };
  }).filter(x => x.url);
}

// OpenAlex
async function openalexSearch(baseUrl, q){
  const url = `${baseUrl.replace(/\/$/,'')}/works?search=${encodeURIComponent(q)}&per_page=8`;
  const j = await fetchJSON(url);
  const items = (j?.results || []).slice(0, 8);
  return items.map(s => {
    const title = s?.title || "";
    const url = s?.primary_location?.landing_page_url || s?.open_access?.oa_url || s?.doi || s?.id || "";
    const sScore = scoreByOverlap(q, title, 0.20);
    return { id:`ox:${s?.id||title}`, title, url, provider: "OpenAlex", score: sScore };
  }).filter(x => x.url);
}

// OpenLibrary
async function openlibrarySearch(baseUrl, q){
  const url = `${baseUrl.replace(/\/$/,'')}/search.json?q=${encodeURIComponent(q)}&limit=8`;
  const j = await fetchJSON(url);
  const docs = (j?.docs || []).slice(0, 8);
  return docs.map(s => {
    const title = s?.title || "";
    const key = s?.key ? `https://openlibrary.org${s.key}` : "";
    const by = Array.isArray(s?.author_name) ? s.author_name.join(", ") : (s?.author_name || "");
    const sScore = scoreByOverlap(q, `${title} ${by}`, 0.15);
    return { id:`ol:${s?.key||title}`, title, url:key, provider:"OpenLibrary", score: sScore };
  }).filter(x => x.url);
}

// Internet Archive (advancedsearch)
async function internetArchiveSearch(baseUrl, q){
  const url = `${baseUrl.replace(/\/$/,'')}/advancedsearch.php?q=${encodeURIComponent(q)}&output=json&rows=8&fl[]=identifier&fl[]=title`;
  const j = await fetchJSON(url);
  const docs = (j?.response?.docs || []).slice(0, 8);
  return docs.map(d => {
    const title = d?.title || d?.identifier || "";
    const url = `https://archive.org/details/${encodeURIComponent(d?.identifier||"")}`;
    const sScore = scoreByOverlap(q, title, 0.12);
    return { id:`ia:${d?.identifier||title}`, title, url, provider:"Internet Archive", score: sScore };
  }).filter(x => x.url);
}

// GutenDEX (Project Gutenberg)
async function gutendexSearch(baseUrl, q){
  const url = `${baseUrl.replace(/\/$/,'')}/books?search=${encodeURIComponent(q)}`;
  const j = await fetchJSON(url);
  const items = (j?.results || []).slice(0, 8);
  return items.map(b => {
    const title = b?.title || "";
    const url = (b?.formats?.["text/html"] || b?.formats?.["application/epub+zip"] || b?.formats?.["application/x-mobipocket-ebook"] || "");
    const sScore = scoreByOverlap(q, `${title} ${Array.isArray(b?.authors)?b.authors.map(a=>a.name).join(", "):""}`, 0.12);
    return { id:`gd:${b?.id||title}`, title, url, provider:"GutenDEX", score: sScore };
  }).filter(x => x.url);
}

// StackExchange (Stack Overflow)
async function stackexchangeSearch(baseUrl, q){
  const url = `${baseUrl.replace(/\/$/,'')}/2.3/search/advanced?order=desc&sort=relevance&q=${encodeURIComponent(q)}&site=stackoverflow`;
  const j = await fetchJSON(url);
  const items = (j?.items || []).slice(0, 8);
  return items.map(s => {
    const title = s?.title || "";
    const url = s?.link || "";
    const votes = Number(s?.score||0);
    const sScore = scoreByOverlap(q, title, 0.10) + votes*0.02;
    return { id:`se:${s?.question_id||title}`, title, url, provider:"StackExchange", score: sScore };
  }).filter(x => x.url);
}

// ArXiv (Atom XML → pick id + title) — may require proxy for CORS
async function arxivSearch(baseUrl, q){
  const url = `${baseUrl.replace(/\/$/,'')}/api/query?search_query=all:${encodeURIComponent(q)}&start=0&max_results=8`;
  const txt = await fetchTEXT(url);
  const items = [];
  // Very light XML parsing for <entry><id>, <title>
  const re = /<entry>[\s\S]*?<id>(.*?)<\/id>[\s\S]*?<title>([\s\S]*?)<\/title>[\s\S]*?<\/entry>/gim;
  let m; let i=0;
  while((m = re.exec(txt)) && i<8){
    const id = (m[1]||"").trim();
    const t  = (m[2]||"").replace(/\s+/g," ").trim();
    if(id && t){ items.push({ id, title:t, url:id }); i++; }
  }
  return items.map(s => ({ id:`ax:${s.id}`, title:s.title, url:s.url, provider:"arXiv", score: scoreByOverlap(q, s.title, 0.18) }));
}

// Europe PMC
async function europePmcSearch(baseUrl, q){
  const url = `${baseUrl.replace(/\/$/,'')}/webservices/rest/search?query=${encodeURIComponent(q)}&format=json&pageSize=8`;
  const j = await fetchJSON(url);
  const items = (j?.resultList?.result || []).slice(0, 8);
  return items.map(s => {
    const title = s?.title || "";
    const url = s?.fullTextUrlList?.fullTextUrl?.[0]?.url || s?.doi ? `https://doi.org/${s.doi}` : (s?.pmcid ? `https://europepmc.org/article/PMC/${s.pmcid}` : "");
    const sScore = scoreByOverlap(q, `${title} ${s?.journalTitle||""}`, 0.18);
    return { id:`epmc:${s?.id||title}`, title, url, provider:"Europe PMC", score: sScore };
  }).filter(x => x.url);
}

// DOAJ
async function doajSearch(baseUrl, q){
  const url = `https://doaj.org/api/search/articles/${encodeURIComponent(q)}?page=1&pageSize=8`;
  const j = await fetchJSON(url);
  const items = (j?.results || []).slice(0, 8);
  return items.map(s => {
    const bib = s?.bibjson || {};
    const title = bib?.title || "";
    const url = (bib?.link||[]).find(l=>l?.url)?.url || s?.id || "";
    const sScore = scoreByOverlap(q, `${title} ${bib?.journal?.title||""}`, 0.15);
    return { id:`doaj:${s?.id||title}`, title, url, provider:"DOAJ", score: sScore };
  }).filter(x => x.url);
}

/* ---------------------------------------------
   Provider router
--------------------------------------------- */

const ID_HANDLERS = {
  // General / Wikimedia family
  ref_wikipedia     : (p,q)=> mediaWikiSearch("https://en.wikipedia.org", q, "Wikipedia"),
  ref_wiktionary    : (p,q)=> mediaWikiSearch("https://en.wiktionary.org", q, "Wiktionary"),
  ref_commons       : (p,q)=> mediaWikiSearch("https://commons.wikimedia.org", q, "Wikimedia Commons"),
  ref_wikisource    : (p,q)=> mediaWikiSearch("https://en.wikisource.org", q, "Wikisource"),
  ref_wikiquote     : (p,q)=> mediaWikiSearch("https://en.wikiquote.org", q, "Wikiquote"),
  ref_wikidata      : (p,q)=> wikidataSparql(q),
  ref_dbpedia       : (p,q)=> dbpediaSparql(q),

  // Books / archives
  ref_openlibrary   : (p,q)=> openlibrarySearch(p.baseUrl, q),
  ref_internet_archive_meta: (p,q)=> internetArchiveSearch(p.baseUrl, q),
  ref_gutendex      : (p,q)=> gutendexSearch(p.baseUrl, q),

  // Scholarly
  ref_crossref      : (p,q)=> crossrefSearch(p.baseUrl, q),
  ref_openalex      : (p,q)=> openalexSearch(p.baseUrl, q),
  ref_arxiv         : (p,q)=> arxivSearch(p.baseUrl, q),
  ref_europe_pmc    : (p,q)=> europePmcSearch(p.baseUrl, q),
  ref_doaj          : (p,q)=> doajSearch(p.baseUrl, q),

  // Dev / Q&A
  ref_stackexchange : (p,q)=> stackexchangeSearch(p.baseUrl, q),
};

async function loadProvidersList(){
  try{
    const url = new URL("./providers.json", import.meta.url).toString();
    const res = await withTimeout(fetchJSON(url));
    if(!res.ok) return [];
    const arr = Array.isArray(res.data) ? res.data : [];
    // Keep only enabled-ish providers; you can add a "disabled" flag to prune at source
    return arr.filter(p => p && p.id && p.baseUrl);
  }catch{ return []; }
}

/* ---------------------------------------------
   Main export
--------------------------------------------- */
export async function getExternalReferences(query, { limit = 8 } = {}){
  const q = String(query||"").trim();
  if(!q) return [];

  // Load providers.json
  const providers = await loadProvidersList();

  // Choose a focused subset by category / trust (fast and relevant)
  // You can adjust this selection logic to include everything.
  const pick = providers.filter(p =>
    (
      p.id in ID_HANDLERS ||               // supported adapter
      /wikipedia|wiktionary|wikisource|wikiquote|commons|wikidata|dbpedia/i.test(p.name) ||
      /crossref|openalex|arxiv|europe\s*pmc|doaj/i.test(p.name) ||
      /openlibrary|archive|guten/i.test(p.name) ||
      /stack\s*exchange/i.test(p.name)
    )
  );

  // Kick off queries (guard timeouts)
  const jobs = pick.map(p =>
    withTimeout(
      Promise.resolve()
        .then(() => {
          const fn = ID_HANDLERS[p.id];
          if (fn) return fn(p, q);
          // Fallback heuristics for MediaWiki-base sites if not matched above
          if (/wikipedia\.org|wiktionary\.org|wikisource\.org|wikiquote\.org|wikimedia\.org/i.test(p.baseUrl||"")){
            return mediaWikiSearch(p.baseUrl, q, p.name || "Wiki");
          }
          // If no adapter, skip
          return [];
        })
        .then(rows => {
          // Apply trust bump from providers.json
          const trust = Number(p.trust || 0);
          return (rows||[]).map(r => ({
            ...r,
            provider: r.provider || p.name || p.id,
            score: weightTrust(Number(r.score||0), trust)
          }));
        })
    )
  );

  const settled = await Promise.allSettled(jobs);
  let rows = [];
  for(const s of settled){
    const v = s?.value;
    if(v && v.ok && Array.isArray(v.data)) rows = rows.concat(v.data);
  }

  // Fallback seed if *everything* failed
  if(!rows.length){
    rows = [
      { id:"seed:seo",  provider:"Wikipedia", title:"Search engine optimization", url:"https://en.wikipedia.org/wiki/Search_engine_optimization", score:0.25 },
      { id:"seed:ir",   provider:"Wikipedia", title:"Information retrieval",     url:"https://en.wikipedia.org/wiki/Information_retrieval",     score:0.20 },
    ];
  }

  // Rank and dedupe by URL (keep highest score)
  rows.sort((a,b)=> Number(b.score||0) - Number(a.score||0));
  rows = uniqBy(rows, it => String(it.url || it.title).toLowerCase());

  return rows.slice(0, Math.max(1, limit)).map(r => ({
    id: r.id, title: r.title, url: r.url, provider: r.provider, score: Number(r.score||0)
  }));
}
