// public/assets/js/modules/engine-api.js
const BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");

async function fetchJson(url, opts) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} — ${text}`);
  }
  return res.json();
}

/** External (local) references — returns an array of {title, url, domain, abstract, year, score, provider, id} */
export async function getExternalLocal(anchor, { context = "", limit = 8 } = {}) {
  const params = new URLSearchParams({
    anchor: String(anchor || ""),
    context: String(context || ""),
    limit: String(limit || 8),
  });

  // Try GET first (cheap), then POST fallback
  try {
    const j = await fetchJson(`${BASE}/engine/external/local?${params.toString()}`);
    return Array.isArray(j?.items) ? j.items : [];
  } catch {
    const j = await fetchJson(`${BASE}/engine/external/local`, {
      method: "POST",
      body: JSON.stringify({ anchor, context, limit }),
    });
    return Array.isArray(j?.items) ? j.items : [];
  }
}

/** Internal engine — echoes a deterministic demo payload for now */
export async function runInternalEngine({ html = "", text = "" } = {}) {
  return await fetchJson(`${BASE}/engine/internal`, {
    method: "POST",
    body: JSON.stringify({ html, text }),
  });
}

/** Optional: simple health/ping */
export async function health() {
  return await fetchJson(`${BASE}/health`);
}
