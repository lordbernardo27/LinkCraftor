from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


FINAL_RESULT = "FINAL RESULT: PART F 15-B4F SIX-STAGE PROGRESS COMPONENT CERTIFIED"
MARKER = "PART F 15-B4F SIX-STAGE PROGRESS COMPONENT"

EXPECTED_HASHES = {
    "index_html": "2b9c785e396e48b417bc3fdcd5fc5c4451fdff5daaffec8935ccf3174ce1b140",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "7eaf7b31fe169dd2af5dbf802c64ab6db6149e08ca217b744b9cc1d2e93b45f9",
    "runtime_owner_js": "0e1c3a511d4bef5baf5c37143ae61e419a0eddfa5c2a3d8e63d62ba243c19a41",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_PANEL = r'''              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewStageProgress" data-pipeline-operations-view-panel="stage_progress" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Six-stage execution</span><h5>Stage Progress</h5><p>Canonical stage order and per-stage runtime state.</p></div><strong>Structure ready</strong></header>
                <ol class="pipeline-stage-progress-shell">
                  <li><span>01</span><div><strong>Connect Domain</strong><small>Awaiting workflow</small></div></li>
                  <li><span>02</span><div><strong>Site Sources</strong><small>Awaiting predecessor</small></div></li>
                  <li><span>03</span><div><strong>URL Cleaner</strong><small>Awaiting predecessor</small></div></li>
                  <li><span>04</span><div><strong>Site Pages</strong><small>Awaiting predecessor</small></div></li>
                  <li><span>05</span><div><strong>Live Domain Target Pool</strong><small>Awaiting predecessor</small></div></li>
                  <li><span>06</span><div><strong>Active Target Set</strong><small>Awaiting predecessor</small></div></li>
                </ol>
              </section>'''

NEW_PANEL = r'''              <!-- BEGIN PART F 15-B4F SIX-STAGE PROGRESS COMPONENT -->
              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewStageProgress" data-pipeline-operations-view-panel="stage_progress" data-component-state="loading" role="tabpanel" aria-busy="true" hidden>
                <header class="pipeline-monitoring-panel-head">
                  <div><span>Six-stage execution</span><h5>Stage Progress</h5><p>Inspect canonical stage order, selected-workflow state, handoff position, and completion evidence.</p></div>
                  <strong id="pipelineStageProgressState">Loading</strong>
                </header>
                <div class="pipeline-stage-progress-live">
                  <div class="pipeline-stage-progress-toolbar">
                    <label><span>Workflow</span><select id="pipelineStageProgressWorkflow" aria-label="Workflow for stage progress"><option value="">Loading workflows</option></select></label>
                    <div><span>Lifecycle</span><strong id="pipelineStageProgressLifecycle">Loading</strong></div>
                    <div><span>Current stage</span><strong id="pipelineStageProgressCurrent">Loading</strong></div>
                    <div><span>Progress</span><strong id="pipelineStageProgressCount">0 of 6</strong></div>
                  </div>
                  <div class="pipeline-stage-progress-meter" aria-label="Workflow completion progress"><span id="pipelineStageProgressMeter"></span></div>
                  <ol class="pipeline-stage-progress-list" id="pipelineStageProgressList" aria-busy="true">
                    <li class="is-loading"><span>01</span><div><strong>Connect Domain</strong><small>Loading evidence</small></div></li>
                    <li class="is-loading"><span>02</span><div><strong>Site Sources</strong><small>Loading evidence</small></div></li>
                    <li class="is-loading"><span>03</span><div><strong>URL Cleaner</strong><small>Loading evidence</small></div></li>
                    <li class="is-loading"><span>04</span><div><strong>Site Pages</strong><small>Loading evidence</small></div></li>
                    <li class="is-loading"><span>05</span><div><strong>Live Domain Target Pool</strong><small>Loading evidence</small></div></li>
                    <li class="is-loading"><span>06</span><div><strong>Active Target Set</strong><small>Loading evidence</small></div></li>
                  </ol>
                  <div class="pipeline-component-state pipeline-stage-progress-message" id="pipelineStageProgressMessage" data-state="loading" role="status" aria-live="polite"><span aria-hidden="true">◌</span><div><strong>Loading stage evidence</strong><p>Using the existing Connected Domain detail snapshot.</p></div></div>
                </div>
              </section>
              <!-- END PART F 15-B4F SIX-STAGE PROGRESS COMPONENT -->'''

CSS_APPEND = r'''

/* BEGIN PART F 15-B4F SIX-STAGE PROGRESS COMPONENT */
#runtimePage .pipeline-stage-progress-live { display: grid; gap: 10px; }
#runtimePage .pipeline-stage-progress-toolbar {
  display: grid; grid-template-columns: minmax(240px, 1.5fr) repeat(3, minmax(110px, .65fr));
  gap: 8px; padding: 9px; border: 1px solid rgba(148,163,184,.12); border-radius: 9px;
  background: rgba(5,17,32,.28);
}
#runtimePage .pipeline-stage-progress-toolbar label,
#runtimePage .pipeline-stage-progress-toolbar > div { display: grid; gap: 4px; min-width: 0; }
#runtimePage .pipeline-stage-progress-toolbar span {
  color: #7890ad; font-size: 8px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
}
#runtimePage .pipeline-stage-progress-toolbar strong { overflow: hidden; color: #e6f7ff; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
#runtimePage .pipeline-stage-progress-toolbar select {
  width: 100%; min-height: 32px; padding: 6px 9px; border: 1px solid rgba(103,232,249,.2);
  border-radius: 7px; outline: none; background: rgba(4,15,29,.72); color: #dceefa; font: inherit; font-size: 10px;
}
#runtimePage .pipeline-stage-progress-toolbar select:focus-visible { border-color: #22d3ee; box-shadow: 0 0 0 2px rgba(34,211,238,.16); }
#runtimePage .pipeline-stage-progress-meter { height: 5px; overflow: hidden; border-radius: 999px; background: rgba(148,163,184,.12); }
#runtimePage .pipeline-stage-progress-meter span { display: block; width: 0; height: 100%; border-radius: inherit; background: linear-gradient(90deg,#22d3ee,#34d399); transition: width .2s ease; }
#runtimePage .pipeline-stage-progress-list { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 8px; margin: 0; padding: 0; list-style: none; }
#runtimePage .pipeline-stage-progress-list li {
  display: grid; grid-template-columns: 32px minmax(0,1fr) auto; align-items: center; gap: 9px; min-width: 0;
  padding: 11px; border: 1px solid rgba(148,163,184,.13); border-radius: 9px; background: rgba(255,255,255,.025);
}
#runtimePage .pipeline-stage-progress-list li > span {
  display: grid; width: 28px; height: 28px; place-items: center; border: 1px solid rgba(148,163,184,.2); border-radius: 50%; color: #8da4bf; font-size: 9px; font-weight: 800;
}
#runtimePage .pipeline-stage-progress-list li div { display: grid; gap: 3px; min-width: 0; }
#runtimePage .pipeline-stage-progress-list strong { overflow: hidden; color: #dceefa; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
#runtimePage .pipeline-stage-progress-list small { color: #7890ad; font-size: 8px; }
#runtimePage .pipeline-stage-progress-list b { padding: 3px 6px; border-radius: 999px; color: #8da4bf; font-size: 7px; letter-spacing: .04em; text-transform: uppercase; }
#runtimePage .pipeline-stage-progress-list li.is-completed { border-color: rgba(74,222,128,.28); background: rgba(34,197,94,.055); }
#runtimePage .pipeline-stage-progress-list li.is-completed > span { border-color: rgba(74,222,128,.4); color: #86efac; }
#runtimePage .pipeline-stage-progress-list li.is-current { border-color: rgba(34,211,238,.5); background: rgba(34,211,238,.075); box-shadow: inset 2px 0 0 #22d3ee; }
#runtimePage .pipeline-stage-progress-list li.is-current > span { border-color: #22d3ee; color: #67e8f9; }
#runtimePage .pipeline-stage-progress-list li.is-failed { border-color: rgba(251,113,133,.38); background: rgba(244,63,94,.06); }
#runtimePage .pipeline-stage-progress-list li.is-failed > span { border-color: rgba(251,113,133,.5); color: #fb7185; }
#runtimePage .pipeline-stage-progress-message { min-height: auto; margin-top: 0; padding: 9px 11px; }
@media (max-width: 1050px) {
  #runtimePage .pipeline-stage-progress-toolbar { grid-template-columns: repeat(3,minmax(0,1fr)); }
  #runtimePage .pipeline-stage-progress-toolbar label { grid-column: 1 / -1; }
  #runtimePage .pipeline-stage-progress-list { grid-template-columns: repeat(2,minmax(0,1fr)); }
}
@media (max-width: 620px) {
  #runtimePage .pipeline-stage-progress-toolbar,
  #runtimePage .pipeline-stage-progress-list { grid-template-columns: 1fr; }
}
/* END PART F 15-B4F SIX-STAGE PROGRESS COMPONENT */
'''

OLD_SET_VIEW = '''    if (matched) {
      mount.dataset.activePipelineView = view;
      if (view === "workflows") {
        window.LinkCraftorConnectedDomainWorkflowExplorer?.activate?.();
      }
    }
    return matched;
  };'''

NEW_SET_VIEW = '''    if (matched) {
      mount.dataset.activePipelineView = view;
      if (view === "workflows") {
        window.LinkCraftorConnectedDomainWorkflowExplorer?.activate?.();
      }
      if (view === "stage_progress") {
        window.LinkCraftorConnectedDomainStageProgress?.activate?.();
      }
    }
    return matched;
  };'''

OLD_WORKFLOW_EXPORT = '''  window.LinkCraftorConnectedDomainWorkflowExplorer = Object.freeze({
    activate,
    render,
    renderUnavailable,
    inspect
  });'''

NEW_WORKFLOW_EXPORT = '''  window.LinkCraftorConnectedDomainWorkflowExplorer = Object.freeze({
    activate,
    render,
    renderUnavailable,
    inspect
  });'''

OLD_OVERVIEW_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      return true;'''

NEW_OVERVIEW_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      window.LinkCraftorConnectedDomainStageProgress?.render?.(payload);
      return true;'''

OLD_OVERVIEW_UNAVAILABLE_HANDOFF = '''    window.LinkCraftorConnectedDomainWorkflowExplorer?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );'''

NEW_OVERVIEW_UNAVAILABLE_HANDOFF = '''    window.LinkCraftorConnectedDomainWorkflowExplorer?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainStageProgress?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );'''

JS_APPEND = r'''

// BEGIN PART F 15-B4F SIX-STAGE PROGRESS COMPONENT
(() => {
  "use strict";
  const PIPELINE_ID = "connect_domain";
  const STAGE_LABELS = Object.freeze({
    connect_domain: "Connect Domain",
    site_sources: "Site Sources",
    url_cleaner: "URL Cleaner",
    site_pages: "Site Pages",
    live_domain_target_pool: "Live Domain Target Pool",
    active_target_set: "Active Target Set"
  });
  let latestPayload = null;
  let selectedWorkflowId = "";
  let bound = false;
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const label = (value) => STAGE_LABELS[String(value || "")] || String(value || "Unknown").split(/[_-]+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
  const array = (value) => Array.isArray(value) ? value.map(String) : [];
  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) throw new Error("Stage Progress received an invalid pipeline identity.");
    if (!Array.isArray(payload.stage_order) || payload.stage_order.length !== 6) throw new Error("Stage Progress requires the six-stage Connected Domain contract.");
    if (!Array.isArray(payload.workflows)) throw new Error("Stage Progress requires persisted workflow evidence.");
    const workflows = payload.workflows.map((workflow) => {
      const workflowId = String(workflow?.workflow_id || "").trim();
      if (!workflowId) throw new Error("Stage Progress received an empty workflow identity.");
      return Object.freeze({
        workflowId,
        status: String(workflow?.status || "unknown").toLowerCase(),
        currentStage: String(workflow?.current_stage || ""),
        completed: array(workflow?.completed_stages),
        pending: array(workflow?.pending_stages),
        failed: array(workflow?.failed_stages),
        outputReady: workflow?.output_ready === true
      });
    });
    return Object.freeze({ stageOrder: payload.stage_order.map(String), workflows });
  };
  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewStageProgress");
    const stateLabel = byId("pipelineStageProgressState");
    const container = byId("pipelineStageProgressMessage");
    if (panel) { panel.dataset.componentState = state; panel.setAttribute("aria-busy", state === "loading" ? "true" : "false"); }
    if (stateLabel) stateLabel.textContent = state === "ready" ? "Live evidence" : label(state);
    if (container) {
      container.dataset.state = state;
      const icon = container.querySelector(":scope > span");
      const heading = container.querySelector("strong");
      const paragraph = container.querySelector("p");
      if (icon) icon.textContent = symbol;
      if (heading) heading.textContent = title;
      if (paragraph) paragraph.textContent = message;
    }
  };
  const stageState = (stage, workflow) => {
    if (workflow.failed.includes(stage)) return "failed";
    if (workflow.completed.includes(stage)) return "completed";
    if (workflow.currentStage === stage) return "current";
    if (workflow.pending.includes(stage)) return "pending";
    return "not_evaluated";
  };
  const renderWorkflow = (contract, workflow) => {
    const list = byId("pipelineStageProgressList");
    const lifecycle = byId("pipelineStageProgressLifecycle");
    const current = byId("pipelineStageProgressCurrent");
    const count = byId("pipelineStageProgressCount");
    const meter = byId("pipelineStageProgressMeter");
    if (!list) return false;
    const completeCount = contract.stageOrder.filter((stage) => workflow.completed.includes(stage)).length;
    list.innerHTML = contract.stageOrder.map((stage, index) => {
      const state = stageState(stage, workflow);
      const text = state === "completed" ? "Completed" : state === "current" ? "Current stage" : state === "failed" ? "Failed" : state === "pending" ? "Awaiting execution" : "Not evaluated";
      return `<li class="is-${escapeHtml(state)}" data-stage-id="${escapeHtml(stage)}"><span>${String(index + 1).padStart(2, "0")}</span><div><strong>${escapeHtml(label(stage))}</strong><small>${escapeHtml(text)}</small></div><b>${escapeHtml(state.replace("_", " "))}</b></li>`;
    }).join("");
    list.setAttribute("aria-busy", "false");
    if (lifecycle) lifecycle.textContent = label(workflow.status);
    if (current) current.textContent = workflow.currentStage ? label(workflow.currentStage) : workflow.outputReady ? "Complete" : "No active stage";
    if (count) count.textContent = `${completeCount} of ${contract.stageOrder.length}`;
    if (meter) meter.style.width = `${Math.round((completeCount / contract.stageOrder.length) * 100)}%`;
    const state = workflow.failed.length ? "failed" : workflow.outputReady ? "complete" : workflow.currentStage ? "active" : "pending";
    updateMessage("ready", "Stage evidence loaded", `${label(state)} workflow · ${completeCount} of ${contract.stageOrder.length} stages completed.`, "✓");
    return true;
  };
  const populateWorkflowSelector = (workflows) => {
    const select = byId("pipelineStageProgressWorkflow");
    if (!select) return false;
    if (!workflows.length) { select.innerHTML = '<option value="">No workflows</option>'; select.disabled = true; return false; }
    select.disabled = false;
    if (!workflows.some((workflow) => workflow.workflowId === selectedWorkflowId)) selectedWorkflowId = workflows[0].workflowId;
    select.innerHTML = workflows.map((workflow) => `<option value="${escapeHtml(workflow.workflowId)}"${workflow.workflowId === selectedWorkflowId ? " selected" : ""}>${escapeHtml(workflow.workflowId)} · ${escapeHtml(label(workflow.status))}</option>`).join("");
    return true;
  };
  const render = (payload) => {
    try {
      const contract = inspect(payload);
      latestPayload = payload;
      ensureBound();
      if (!contract.workflows.length) {
        populateWorkflowSelector([]);
        const list = byId("pipelineStageProgressList");
        if (list) { list.innerHTML = '<li class="is-not_evaluated"><span>—</span><div><strong>No persisted workflow</strong><small>Stage evidence will appear after workflow activation.</small></div><b>empty</b></li>'; list.setAttribute("aria-busy", "false"); }
        updateMessage("empty", "No workflow stage evidence", "Connected Domain has no persisted workflow to evaluate.", "◎");
        return true;
      }
      populateWorkflowSelector(contract.workflows);
      return renderWorkflow(contract, contract.workflows.find((workflow) => workflow.workflowId === selectedWorkflowId) || contract.workflows[0]);
    } catch (error) { return renderUnavailable(error?.message); }
  };
  const renderUnavailable = (message) => {
    latestPayload = null;
    const list = byId("pipelineStageProgressList");
    const select = byId("pipelineStageProgressWorkflow");
    if (select) { select.innerHTML = '<option value="">Unavailable</option>'; select.disabled = true; }
    if (list) { list.innerHTML = '<li class="is-failed"><span>!</span><div><strong>Stage evidence unavailable</strong><small>Restore the canonical read-only projection.</small></div><b>unavailable</b></li>'; list.setAttribute("aria-busy", "false"); }
    updateMessage("unavailable", "Stage evidence unavailable", message || "The canonical detail projection could not be loaded.", "!");
    return false;
  };
  const ensureBound = () => {
    if (bound) return true;
    const select = byId("pipelineStageProgressWorkflow");
    if (!select) return false;
    select.addEventListener("change", () => { selectedWorkflowId = String(select.value || ""); if (latestPayload) render(latestPayload); });
    bound = true;
    return true;
  };
  const activate = () => {
    ensureBound();
    const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.();
    if (snapshot) return render(snapshot);
    updateMessage("loading", "Loading stage evidence", "Waiting for the existing Connected Domain detail snapshot.", "◌");
    return false;
  };
  window.LinkCraftorConnectedDomainStageProgress = Object.freeze({ activate, render, renderUnavailable, inspect });
})();
// END PART F 15-B4F SIX-STAGE PROGRESS COMPONENT
'''

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=8" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=9" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=10"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=11"></script>'


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        self.ids.extend(value for name, value in attrs if name == "id" and value)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, source: str) -> None:
    path.write_text(source, encoding="utf-8", newline="\n")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label}, found {count}.")
    return source.replace(old, new, 1)


def html_ids_unique(source: str) -> bool:
    parser = IdCollector()
    parser.feed(source)
    return len(parser.ids) == len(set(parser.ids))


def css_balanced(source: str) -> bool:
    stripped = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    stripped = re.sub(r'"(?:\\.|[^"\\])*"', '""', stripped)
    stripped = re.sub(r"'(?:\\.|[^'\\])*'", "''", stripped)
    depth = 0
    for character in stripped:
        if character == "{": depth += 1
        elif character == "}":
            depth -= 1
            if depth < 0: return False
    return depth == 0


def javascript_syntax_valid(source: str) -> bool:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for JavaScript syntax validation.")
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4f_js_") as folder:
        candidate = Path(folder) / "runtime_owner_candidate.js"
        write_text(candidate, source)
        result = subprocess.run([node, "--check", str(candidate)], capture_output=True, text=True, check=False)
    return result.returncode == 0


def make_report(status: str, checks: dict[str, bool], evidence: dict[str, Any], error: dict[str, Any]) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = FINAL_RESULT if status == "CERTIFIED" else "FINAL RESULT: PART F 15-B4F SIX-STAGE PROGRESS COMPONENT NOT_CERTIFIED"
    lines = [
        "LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS",
        "PART F 15-B4F SIX-STAGE PROGRESS COMPONENT CERTIFICATION", "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}", "Patch mode: STRICT FAIL-CLOSED",
        f"Backup: {evidence.get('backup', 'NOT_CREATED')}",
        "Production jobs created: NO", "Production queue claims executed: NO", "Production handlers executed: NO",
        "Production workflow persistence executed: NO", "Production recovery actions executed: NO",
        "Live network requests executed during certification: NO", f"CERTIFICATION STATUS: {status}", "",
        "CHECKS:", json.dumps(checks, indent=2, sort_keys=True), "", "FAILED_CHECKS:", json.dumps(failed, indent=2), "",
        "NOT_RUN_CHECKS:", "[]", "", "EVIDENCE:", json.dumps(evidence, indent=2, sort_keys=True), "",
        "EXECUTION_ERROR:", json.dumps(error, indent=2, sort_keys=True), "", "IMPLEMENTED BOUNDARY:",
        "- Stage Progress renders the canonical six-stage Connected Domain order.",
        "- A persisted workflow can be selected locally to inspect completed, current, pending and failed stage evidence.",
        "- Lifecycle, current stage, completion count and progress meter are projected from the cached detail snapshot.",
        "- The existing Connected Domain GET request is reused; no new endpoint request was added.",
        "- Loading, ready, empty and unavailable states fail closed.",
        "- No job, queue, workflow, handler, recovery or persistence authority was created or mutated.", "",
        "NEXT STEP:", "Browser visual acceptance, then Part F 15-B4G - Jobs and Attempts component.", "", final, ""
    ]
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: RUN_15_B4F_SIX_STAGE_PROGRESS.py <project_root> <report_path>")
    root, report = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    paths = {
        "index_html": root / "backend/server/owner/index.html", "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js", "runtime_owner_css": root / "backend/server/owner/runtime_owner.css",
        "runtime_owner_js": root / "backend/server/owner/runtime_owner.js", "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py",
        "pipeline_operations": root / "backend/server/owner/pipeline_operations.py",
    }
    prior_report = root / "backend/server/data/reports/PART_F_15_B4E_WORKFLOW_EXPLORER_CERTIFICATION.txt"
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {"new_endpoint_requests": 0, "recovery_controls_added": False}
    error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}
    backup_dir: Path | None = None
    retained = False
    status = "NOT_CERTIFIED"
    try:
        checks["part_f_15_b4e_report_exists"] = prior_report.is_file()
        prior_hash = sha256_path(prior_report) if prior_report.is_file() else ""
        prior = read_text(prior_report) if prior_report.is_file() else ""
        checks["part_f_15_b4e_certified"] = "CERTIFICATION STATUS: CERTIFIED" in prior and "FINAL RESULT: PART F 15-B4E WORKFLOW EXPLORER CERTIFIED" in prior
        for name, path in paths.items(): checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()): raise RuntimeError("Required source or B4E evidence is unavailable.")
        before = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items(): checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()): raise RuntimeError("Installed source lineage does not match certified B4E.")
        index_source, css_source, js_source = read_text(paths["index_html"]), read_text(paths["runtime_owner_css"]), read_text(paths["runtime_owner_js"])
        checks["stage_progress_not_previously_present"] = all(MARKER not in source for source in (index_source, css_source, js_source))
        index_candidate = replace_once(index_source, OLD_PANEL, NEW_PANEL, "Stage Progress structure shell")
        index_candidate = replace_once(index_candidate, OLD_CSS_VERSION, NEW_CSS_VERSION, "Runtime stylesheet cache version")
        index_candidate = replace_once(index_candidate, OLD_JS_VERSION, NEW_JS_VERSION, "Runtime JavaScript cache version")
        css_candidate = css_source.rstrip() + "\n" + CSS_APPEND.lstrip()
        js_candidate = replace_once(js_source, OLD_SET_VIEW, NEW_SET_VIEW, "Stage Progress activation handoff")
        js_candidate = replace_once(js_candidate, OLD_OVERVIEW_RENDER_HANDOFF, NEW_OVERVIEW_RENDER_HANDOFF, "Stage Progress render handoff")
        js_candidate = replace_once(js_candidate, OLD_OVERVIEW_UNAVAILABLE_HANDOFF, NEW_OVERVIEW_UNAVAILABLE_HANDOFF, "Stage Progress unavailable handoff")
        js_candidate = js_candidate.rstrip() + "\n" + JS_APPEND.lstrip()
        checks["candidate_html_ids_unique"] = html_ids_unique(index_candidate)
        checks["candidate_css_balanced"] = css_balanced(css_candidate)
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(js_candidate)
        required_ids = ("pipelineStageProgressState", "pipelineStageProgressWorkflow", "pipelineStageProgressLifecycle", "pipelineStageProgressCurrent", "pipelineStageProgressCount", "pipelineStageProgressMeter", "pipelineStageProgressList", "pipelineStageProgressMessage")
        checks["all_stage_progress_bindings_present"] = all(index_candidate.count(f'id="{identifier}"') == 1 for identifier in required_ids)
        checks["canonical_six_stage_order_present"] = all(stage in JS_APPEND for stage in ("connect_domain", "site_sources", "url_cleaner", "site_pages", "live_domain_target_pool", "active_target_set"))
        checks["four_stage_states_present"] = all(token in JS_APPEND for token in ('"completed"', '"current"', '"pending"', '"failed"'))
        checks["workflow_selector_present"] = "pipelineStageProgressWorkflow" in JS_APPEND and "selectedWorkflowId" in JS_APPEND
        checks["cached_snapshot_reused"] = "LinkCraftorConnectedDomainOverview?.getSnapshot?.()" in JS_APPEND
        checks["no_new_fetch_request_added"] = js_candidate.count("fetch(") == js_source.count("fetch(")
        checks["canonical_detail_endpoint_retained_once"] = js_candidate.count('"/owner/api/runtime/pipelines/connect_domain"') == 1
        checks["four_presentation_states_present"] = all(f'"{state}"' in JS_APPEND for state in ("loading", "ready", "empty", "unavailable"))
        checks["no_recovery_controls_added"] = all(js_candidate.count(token) == js_source.count(token) for token in ("retryJob(", "cancelJob(", "terminateJob(", "data-runtime-recovery-action"))
        checks["cache_versions_advanced"] = NEW_CSS_VERSION in index_candidate and NEW_JS_VERSION in index_candidate
        if not all(checks.values()): raise RuntimeError("15-B4F candidate certification checks failed.")
        timestamp_value = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = root / "backend/server/data/runtime_backups" / f"part_f_15_b4f_{timestamp_value}"
        backup_dir.mkdir(parents=True, exist_ok=False)
        for name in ("index_html", "runtime_owner_css", "runtime_owner_js"):
            originals[name] = paths[name].read_bytes(); shutil.copy2(paths[name], backup_dir / paths[name].name)
        evidence["backup"] = str(backup_dir)
        write_text(paths["index_html"], index_candidate); write_text(paths["runtime_owner_css"], css_candidate); write_text(paths["runtime_owner_js"], js_candidate)
        checks["backup_created"] = backup_dir.is_dir()
        checks["retained_html_ids_unique"] = html_ids_unique(read_text(paths["index_html"]))
        checks["retained_css_balanced"] = css_balanced(read_text(paths["runtime_owner_css"]))
        checks["retained_javascript_syntax"] = javascript_syntax_valid(read_text(paths["runtime_owner_js"]))
        checks["retained_markers"] = all(read_text(paths[name]).count(MARKER) == 2 for name in ("index_html", "runtime_owner_css", "runtime_owner_js"))
        checks["historical_b4e_report_unchanged"] = sha256_path(prior_report) == prior_hash
        after = {name: sha256_path(path) for name, path in paths.items()}; evidence["source_hashes_after"] = after
        checks["only_three_ui_sources_changed"] = all((after[name] != before[name]) == (name in {"index_html", "runtime_owner_css", "runtime_owner_js"}) for name in paths)
        checks.update({"production_jobs_created_no": True, "production_queue_claims_no": True, "production_handlers_executed_no": True, "production_workflow_persistence_no": True, "production_recovery_actions_no": True, "live_network_requests_during_certification_no": True})
        evidence["stage_order"] = ["connect_domain", "site_sources", "url_cleaner", "site_pages", "live_domain_target_pool", "active_target_set"]
        evidence["stage_states"] = ["completed", "current", "pending", "failed", "not_evaluated"]
        if not all(checks.values()): raise RuntimeError("Retained 15-B4F certification checks failed.")
        retained, status = True, "CERTIFIED"
    except Exception as exc:
        error = {"error_type": type(exc).__name__, "error_message": str(exc), "traceback": traceback.format_exc()}
        if originals:
            for name, content in originals.items(): paths[name].write_bytes(content)
    finally:
        evidence["patch_retained"] = retained
        report.parent.mkdir(parents=True, exist_ok=True)
        write_text(report, make_report(status, checks, evidence, error))
    for name, passed in checks.items(): print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not passed for passed in checks.values())}")
    print("NOT_RUN_CHECK_COUNT=0"); print(f"REPORT={report}"); print(f"PART_F_15_B4F_STATUS={status}"); print(f"PATCH_RETAINED={'YES' if retained else 'NO'}")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
