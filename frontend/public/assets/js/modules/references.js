// public/assets/js/modules/references.js
import { getExternalLocal } from "./engine-api.js";

/**
 * getExternalReferences(anchor, { context?, limit? })
 * Returns an array of { title, url, domain, abstract, year, score, provider, id }
 */
export async function getExternalReferences(anchor, opts = {}) {
  const { context = "", limit = 8 } = opts;
  const items = await getExternalLocal(anchor, { context, limit });
  return Array.isArray(items) ? items : [];
}
