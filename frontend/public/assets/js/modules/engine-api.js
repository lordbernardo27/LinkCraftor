// public/assets/js/modules/engine-api.js
const BASE = (window.LINKCRAFTOR_API_BASE || "http://127.0.0.1:8001").replace(/\/+$/, "");

async function fetchJson(url, opts) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} â€” ${text}`);
  }
  return res.json();
}

/** External references — uses the real external resolver at /api/external/resolve */
export async function getExternalLocal(anchor, { context = "", limit = 8 } = {}) {
  const params = new URLSearchParams({
    phrase: String(anchor || ""),
    lang: "en",
  });

  const j = await fetchJson(`${BASE}/api/external/resolve?${params.toString()}`);
  const items = Array.isArray(j) ? j : (Array.isArray(j?.items) ? j.items : []);
  return items.slice(0, Math.max(1, Number(limit || 8)));
}

/** Internal engine â€” echoes a deterministic demo payload for now */
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


