// ------------------------------
// API endpoints
// ------------------------------
const API_LIST   = "/api/external/manual/list?limit=500";
const API_ADD    = "/api/external/manual/add";
const API_TOGGLE = "/api/external/manual/toggle";
const API_DELETE = "/api/external/manual/delete";

const API_IMPORT = "/api/external/owner/sitemap/import";

// Resolver test endpoint
const API_RESOLVE = "/api/external/resolve";

// Import runs + rollback (Queue 5.2)
const API_RUNS = "/api/external/owner/import/runs";
const API_ROLLBACK = "/api/external/owner/import/rollback";

function $(id){ return document.getElementById(id); }

function escapeHtml(s){
  return String(s||"").replace(/[&<>"']/g, (m)=>( {
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[m] ));
}
function escapeAttr(s){ return String(s||"").replace(/"/g,"&quot;"); }

// ✅ Login flow: if API returns 401, prompt for key and set cookie
async function ownerLoginFlow(){
  const probeUrl = "/api/external/manual/list?limit=1&_ts=" + Date.now();
  const probe = await fetch(probeUrl, { cache: "no-store" });
  if (probe.status !== 401) return true;

  const key = prompt("Enter Owner Key (LinkCraftor Control Tower):");
  if (!key) return false;

  const loginRes = await fetch("/owner-api/login", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ key })
  });

  const data = await loginRes.json().catch(()=>({}));
  if (!loginRes.ok || data.ok === false) {
    alert("Invalid Owner Key.");
    return false;
  }
  return true;
}

async function fetchJson(url, opts){
  const res = await fetch(url, opts);
  const data = await res.json().catch(()=> ({}));
  return { res, data };
}

// ------------------------------
// Manual dataset UI
// ------------------------------
async function loadManual(){
  const tbody = $("rows");
  const msg = $("msg");
  if(!tbody){
    if(msg) msg.textContent = "UI error: tbody#rows not found.";
    return;
  }

  try{
    if(msg) msg.textContent = "Fetching manual URLs...";
    const {res, data} = await fetchJson(API_LIST + "&_ts=" + Date.now(), { cache: "no-store" });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner login required. Refresh to login.";
      tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">Owner auth required.</td></tr>`;
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }

    const items = Array.isArray(data.items) ? data.items : [];
    if(!items.length){
      tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">No manual URLs yet.</td></tr>`;
      if(msg) msg.textContent = "Manual dataset is empty.";
      return;
    }

    tbody.innerHTML = items.slice().reverse().map((it)=>{
      const key = it.key || "";
      const phrase = it.phrase || "";
      const url = it.url || "";
      const source = it.source || "";
      const added = it.added_at || it.updated_at || "";
      const disabled = !!it.disabled;

      const btnLabel = disabled ? "Enable" : "Disable";
      const btnStyle = disabled
        ? "background:#065f46;border:1px solid #064e3b;color:#e5e7eb"
        : "background:#7c2d12;border:1px solid #431407;color:#e5e7eb";

      return `
        <tr>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(key)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(phrase)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">
            <a href="${escapeAttr(url)}" target="_blank" rel="noreferrer">${escapeHtml(url)}</a>
          </td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(source)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(added)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937;white-space:nowrap">
            <button data-act="toggle" data-url="${escapeAttr(url)}" data-disabled="${disabled ? "1":"0"}"
              style="padding:6px 10px;border-radius:10px;cursor:pointer;${btnStyle}">
              ${btnLabel}
            </button>
            <button data-act="delete" data-url="${escapeAttr(url)}"
              style="margin-left:8px;padding:6px 10px;border-radius:10px;cursor:pointer;background:#111827;border:1px solid #374151;color:#e5e7eb">
              Delete
            </button>
          </td>
        </tr>
      `;
    }).join("");

    tbody.querySelectorAll("button[data-act]").forEach(btn=>{
      btn.addEventListener("click", async ()=>{
        const act = btn.getAttribute("data-act");
        const url = btn.getAttribute("data-url");
        if(!url) return;

        if(act === "toggle"){
          const isDisabled = btn.getAttribute("data-disabled") === "1";
          await manualToggle(url, !isDisabled);
        } else if(act === "delete"){
          await manualDelete(url);
        }
      });
    });

    if(msg) msg.textContent = `Loaded ${items.length} manual URL(s).`;
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
    tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">Failed to load.</td></tr>`;
  }
}

async function saveManual(){
  const msg = $("msg");
  const phrase = ($("inPhrase")?.value || "").trim();
  const url = ($("inUrl")?.value || "").trim();
  const title = ($("inTitle")?.value || "").trim();

  if(!phrase || !url){
    if(msg) msg.textContent = "Phrase and URL are required.";
    return;
  }

  try{
    if(msg) msg.textContent = "Saving...";
    const {res, data} = await fetchJson(API_ADD, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ phrase, url, title: title || null }),
    });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner auth required. Refresh to login.";
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }

    if($("inPhrase")) $("inPhrase").value = "";
    if($("inUrl")) $("inUrl").value = "";
    if($("inTitle")) $("inTitle").value = "";

    if(msg) msg.textContent = "Saved. Refreshing...";
    await loadManual();
    if(msg) msg.textContent = "Done.";
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
  }
}

async function manualToggle(url, disabled){
  const msg = $("msg");
  try{
    const yes = confirm(disabled ? "Disable this manual URL?" : "Enable this manual URL?");
    if(!yes) return;

    const {res, data} = await fetchJson(API_TOGGLE, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ url, disabled: !!disabled }),
    });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner auth required. Refresh to login.";
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }
    await loadManual();
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
  }
}

async function manualDelete(url){
  const msg = $("msg");
  try{
    const yes = confirm("Delete this manual URL permanently?");
    if(!yes) return;

    const {res, data} = await fetchJson(API_DELETE, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ url }),
    });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner auth required. Refresh to login.";
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }
    await loadManual();
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
  }
}

// ------------------------------
// Authority Import UI
// ------------------------------
function buildSitemapImportPayload(commit){
  const domain = ($("smDomain")?.value || "").trim();
  const sitemap_url = ($("smUrl")?.value || "").trim();
  const source_label = ($("smLabel")?.value || "").trim();

  if(!source_label) throw new Error("Source label is required.");
  if(domain && sitemap_url) throw new Error("Provide only one: Domain OR Sitemap URL (not both).");

  const payload = { source_label, commit: !!commit };
  if(domain) payload.domain = domain;
  if(sitemap_url) payload.sitemap_url = sitemap_url;
  return payload;
}

async function runSitemapImport(commit){
  const msg = $("smMsg");
  const out = $("smOut");

  try{
    if(!out) return;

    if(msg) msg.textContent = commit ? "Running import (COMMIT)..." : "Running import (dry run)...";
    out.textContent = commit ? "Running commit...\n" : "Running dry run...\n";

    const payload = buildSitemapImportPayload(commit);

    const {res, data} = await fetchJson(API_IMPORT, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload),
    });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner auth required. Refresh to login.";
      out.textContent = "Owner auth required.";
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }

    out.textContent = JSON.stringify(data, null, 2);
    if(msg) msg.textContent = commit ? "Commit completed." : "Dry run completed.";
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
    if(out) out.textContent = `Error: ${e.message || e}`;
  }
}

// ------------------------------
// Resolver Test UI
// ------------------------------
async function runResolveTest(){
  const phrase = ($("rsPhrase")?.value || "").trim();
  const src = ($("rsSource")?.value || "").trim();

  const msg = $("rsMsg");
  const out = $("rsOut");

  if(!phrase){
    if(msg) msg.textContent = "Type a phrase first (e.g. syphilis).";
    return;
  }

  try{
    if(msg) msg.textContent = "Searching...";
    if(out) out.textContent = "Searching...\n";

    let url = `${API_RESOLVE}?phrase=${encodeURIComponent(phrase)}`;
    if(src) url += `&source_label=${encodeURIComponent(src)}`;

    const {res, data} = await fetchJson(url, { cache: "no-store" });

    if(!res.ok){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }

    if(out) out.textContent = JSON.stringify(data, null, 2);
    if(msg) msg.textContent = `Done. Found ${Array.isArray(data) ? data.length : 0} result(s).`;
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
    if(out) out.textContent = `Error: ${e.message || e}`;
  }
}

// ------------------------------
// Import Runs UI
// ------------------------------
function normalizeRunRow(r){
  // supports both older + newer audit formats
  return {
    ts: r.ts || "",
    run_id: r.import_run_id || "",
    source_label: r.source_label || "",
    auto_added: r.auto_added ?? "",
    auto_updated: r.auto_updated ?? "",
    event: r.event || "",
    snapshot_path: r.snapshot_path || "",
  };
}

async function loadImportRuns(){
  const tbody = $("runsRows");
  const msg = $("runsMsg");
  const limit = parseInt(($("runsLimit")?.value || "20"), 10) || 20;

  if(!tbody) return;

  try{
    if(msg) msg.textContent = "Loading runs...";
    tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">Loading…</td></tr>`;

    const url = `${API_RUNS}?limit=${encodeURIComponent(String(limit))}&_ts=${Date.now()}`;
    const {res, data} = await fetchJson(url, { cache: "no-store" });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner auth required. Refresh to login.";
      tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">Owner auth required.</td></tr>`;
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }

    const items = Array.isArray(data.items) ? data.items : [];
    if(!items.length){
      tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">No runs found.</td></tr>`;
      if(msg) msg.textContent = "No runs yet.";
      return;
    }

    // only show commit events (these contain run_id + snapshot)
    const commits = items.filter(x => String(x.event || "") === "owner_sitemap_commit_auto");
    const rows = commits.map(normalizeRunRow);

    tbody.innerHTML = rows.slice().reverse().map((r)=>{
      const ts = r.ts;
      const runId = r.run_id || "";
      const label = r.source_label || "";
      const added = String(r.auto_added ?? "");
      const updated = String(r.auto_updated ?? "");
      const note = r.snapshot_path ? "has snapshot" : "";

      const useBtn = runId
        ? `<button data-act="use-run" data-run="${escapeAttr(runId)}"
             style="padding:6px 10px;border-radius:10px;cursor:pointer;background:#0b1220;border:1px solid #1f2937;color:#e5e7eb">
             Use
           </button>`
        : "";

      return `
        <tr>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(ts)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937"><code>${escapeHtml(runId)}</code></td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(label)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(added)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937">${escapeHtml(updated)}</td>
          <td style="padding:10px;border-bottom:1px solid #1f2937;white-space:nowrap">
            ${useBtn}
            <span style="margin-left:10px;color:#94a3b8">${escapeHtml(note)}</span>
          </td>
        </tr>
      `;
    }).join("");

    // event delegation (faster)
    tbody.onclick = (ev)=>{
      const btn = ev.target.closest("button[data-act]");
      if(!btn) return;
      const act = btn.getAttribute("data-act");
      if(act === "use-run"){
        const runId = btn.getAttribute("data-run") || "";
        if($("rbRunId")) $("rbRunId").value = runId;
        if($("rbMsg")) $("rbMsg").textContent = "Run ID copied into rollback panel.";
      }
    };

    if(msg) msg.textContent = `Loaded ${rows.length} commit run(s).`;
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
    tbody.innerHTML = `<tr><td colspan="6" style="padding:10px">Failed to load.</td></tr>`;
  }
}

// ------------------------------
// Rollback Panel (B)
// ------------------------------
function getRollbackRunId(){
  return ($("rbRunId")?.value || "").trim();
}

async function rollbackPreviewOrRestore(preview){
  const runId = getRollbackRunId();
  const msg = $("rbMsg");
  const out = $("rbOut");

  if(!runId){
    if(msg) msg.textContent = "Paste a Run ID first.";
    return;
  }

  try{
    if(msg) msg.textContent = preview ? "Previewing..." : "Restoring (this writes)...";
    if(out) out.textContent = preview ? "Previewing...\n" : "Restoring...\n";

    if(!preview){
      const yes = confirm("Restore snapshot for this run? This will overwrite AUTO dataset.");
      if(!yes){
        if(msg) msg.textContent = "Cancelled.";
        return;
      }
    }

    const {res, data} = await fetchJson(API_ROLLBACK, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ import_run_id: runId, preview: !!preview }),
    });

    if(res.status === 401){
      if(msg) msg.textContent = "Owner auth required. Refresh to login.";
      if(out) out.textContent = "Owner auth required.";
      return;
    }
    if(!res.ok || data.ok === false){
      throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }

    if(out) out.textContent = JSON.stringify(data, null, 2);
    if(msg) msg.textContent = preview ? "Preview loaded." : "Restore completed.";

    // after restore, refresh runs list (optional but useful)
    if(!preview){
      await loadImportRuns();
    }
  }catch(e){
    console.error(e);
    if(msg) msg.textContent = `Error: ${e.message || e}`;
    if(out) out.textContent = `Error: ${e.message || e}`;
  }
}

function clearRollback(){
  if($("rbRunId")) $("rbRunId").value = "";
  if($("rbOut")) $("rbOut").textContent = "No rollback yet.";
  if($("rbMsg")) $("rbMsg").textContent = "";
}

// ------------------------------
// Boot
// ------------------------------
window.addEventListener("DOMContentLoaded", async ()=>{
  // manual
  $("btnSave")?.addEventListener("click", saveManual);
  $("btnRefresh")?.addEventListener("click", loadManual);

  // authority import
  $("btnSmDryRun")?.addEventListener("click", ()=> runSitemapImport(false));
  $("btnSmRun")?.addEventListener("click", ()=> runSitemapImport(true));
  $("btnSmClear")?.addEventListener("click", ()=>{
    if($("smOut")) $("smOut").textContent = "No import yet.";
    if($("smMsg")) $("smMsg").textContent = "";
  });

  // resolver test
  $("btnResolveTest")?.addEventListener("click", runResolveTest);
  $("btnResolveClear")?.addEventListener("click", ()=>{
    if($("rsOut")) $("rsOut").textContent = "No search yet.";
    if($("rsMsg")) $("rsMsg").textContent = "";
  });

  // runs
  $("btnRunsRefresh")?.addEventListener("click", loadImportRuns);

  // rollback panel
  $("btnRbPreview")?.addEventListener("click", ()=> rollbackPreviewOrRestore(true));
  $("btnRbRestore")?.addEventListener("click", ()=> rollbackPreviewOrRestore(false));
  $("btnRbClear")?.addEventListener("click", clearRollback);

  const ok = await ownerLoginFlow();
  if(!ok){
    const msg = $("msg");
    if(msg) msg.textContent = "Login cancelled.";
    return;
  }

  await loadManual();

  // placeholders
  if($("smOut")) $("smOut").textContent = "No import yet.";
  if($("rsOut")) $("rsOut").textContent = "No search yet.";
  if($("rbOut")) $("rbOut").textContent = "No rollback yet.";

  // load runs on page load
  await loadImportRuns();
});
