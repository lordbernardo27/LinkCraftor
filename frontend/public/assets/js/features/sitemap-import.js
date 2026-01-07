// assets/js/features/sitemap-import.js
import { showToast } from "../core/dom.js";
import { rebuildTitleIndex } from "../data/titles.js";
import { highlightKeywords } from "../editor/highlight.js";

const $ = (id) => document.getElementById(id);
const API_BASE = "http://127.0.0.1:8001";

export function wireSitemapImport(){
  const btn = $("btnImportMap");
  const file = $("sitemapFile");
  const errorBox = $("error");
  if (!btn || !file) return;

  btn.addEventListener("click", ()=>{ file.value = ""; file.click(); });

  file.addEventListener("change", async ()=>{
    const f = file.files && file.files[0];
    if (!f) return;

    try {
      const fd = new FormData();
      fd.append("file", f);

      const res = await fetch(`${API_BASE}/api/urls/import?workspace_id=default`, {
        method: "POST",
        body: fd,
      });

      if (!res.ok) {
        const msg = await res.text().catch(() => "");
        throw new Error(msg || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const added = Number(data.added || 0);
      console.log("[SitemapImport] backend response:", data);



      rebuildTitleIndex();
      highlightKeywords();
      showToast(errorBox, `Imported ${added} URL(s) from ${f.name}.`, 1500);
    } catch(e) {
      showToast(errorBox, `Import failed: ${e?.message || e}`, 2200);
    }
  });
}
