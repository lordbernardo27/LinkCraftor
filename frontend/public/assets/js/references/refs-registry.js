// Loads and exposes the frozen registry.
// Robust JSON loading via fetch to avoid JSON import assertion issues.

let _registry = null;

/**
 * @returns {Promise<any[]>} raw registry entries
 */
export async function loadRegistry() {
  if (Array.isArray(_registry)) return _registry;
  try {
    const res = await fetch(new URL("./reference-sources.json", import.meta.url));
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    _registry = Array.isArray(data) ? data : [];
  } catch (e) {
    console.error("[refs-registry] Failed to load registry:", e);
    _registry = [];
  }
  return _registry;
}

/**
 * @returns {Promise<any[]>}
 */
export async function listSources() {
  const reg = await loadRegistry();
  return reg.slice();
}

/**
 * @param {string} id
 * @returns {Promise<any|undefined>}
 */
export async function getSourceById(id) {
  const reg = await loadRegistry();
  return reg.find(s => s.id === id);
}
