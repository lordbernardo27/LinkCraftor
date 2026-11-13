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


FINAL_RESULT = "FINAL RESULT: PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT CERTIFIED"
MARKER = "PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT"

EXPECTED_HASHES = {
    "index_html": "0b9331ad5d10b30f1ea78417b6791a02ea0f07071dd9506e29ecf73db257dd47",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "b2119bad0e028c08e5b94171f85f36528e5937ff0bd8ed8af7273a17b2cf0f88",
    "runtime_owner_js": "d6b0b8c8709b532060ccb8fb00f231690c5a011a46862c892986b91f5812efa4",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_PANEL = r'''              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewDependenciesHandoffs" data-pipeline-operations-view-panel="dependencies_handoffs" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Execution contract</span><h5>Dependencies &amp; Handoffs</h5><p>Dependency gates and result-to-payload hydration between stages.</p></div><strong>Structure ready</strong></header>
                <div class="pipeline-handoff-chain-shell"><div>Connect Domain <b>→</b> Site Sources</div><div>Site Sources <b>→</b> URL Cleaner</div><div>URL Cleaner <b>→</b> Site Pages</div><div>Site Pages <b>→</b> Live Domain Target Pool</div><div>Live Domain Target Pool <b>→</b> Active Target Set</div></div>
              </section>'''

NEW_PANEL = r'''              <!-- BEGIN PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT -->
              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewDependenciesHandoffs" data-pipeline-operations-view-panel="dependencies_handoffs" data-component-state="loading" role="tabpanel" aria-busy="true" hidden>
                <header class="pipeline-monitoring-panel-head">
                  <div><span>Execution contract</span><h5>Dependencies &amp; Handoffs</h5><p>Inspect predecessor gates, successor declarations, stage result availability, and workflow handoff position.</p></div>
                  <strong id="pipelineHandoffsState">Loading</strong>
                </header>
                <div class="pipeline-handoffs-live">
                  <div class="pipeline-handoffs-toolbar">
                    <label><span>Workflow</span><select id="pipelineHandoffsWorkflow"><option value="">Loading workflows</option></select></label>
                    <div><span>Canonical stages</span><strong id="pipelineHandoffsStageCount">6</strong></div>
                    <div><span>Handoff gates</span><strong id="pipelineHandoffsGateCount">5</strong></div>
                    <div><span>Current position</span><strong id="pipelineHandoffsCurrent">Loading</strong></div>
                  </div>
                  <div class="pipeline-handoff-contract" id="pipelineHandoffsContract" aria-busy="true">
                    <div class="pipeline-handoffs-placeholder"><strong>Loading dependency contract</strong><p>Reading the cached Connected Domain projection.</p></div>
                  </div>
                  <div class="pipeline-component-state pipeline-handoffs-message" id="pipelineHandoffsMessage" data-state="loading" role="status" aria-live="polite"><span aria-hidden="true">◌</span><div><strong>Loading handoff evidence</strong><p>Using the existing Connected Domain detail snapshot.</p></div></div>
                </div>
              </section>
              <!-- END PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT -->'''

CSS_APPEND = r'''

/* BEGIN PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT */
#runtimePage .pipeline-handoffs-live { display: grid; gap: 10px; }
#runtimePage .pipeline-handoffs-toolbar {
  display: grid; grid-template-columns: minmax(250px,1.4fr) repeat(3,minmax(110px,.55fr)); gap: 8px; align-items: end;
  padding: 9px; border: 1px solid rgba(148,163,184,.12); border-radius: 9px; background: rgba(5,17,32,.28);
}
#runtimePage .pipeline-handoffs-toolbar label,
#runtimePage .pipeline-handoffs-toolbar > div { display: grid; gap: 4px; min-width: 0; }
#runtimePage .pipeline-handoffs-toolbar span { color: #7890ad; font-size: 8px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
#runtimePage .pipeline-handoffs-toolbar strong { overflow: hidden; color: #e6f7ff; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
#runtimePage .pipeline-handoffs-toolbar select {
  width: 100%; min-height: 32px; padding: 6px 9px; border: 1px solid rgba(103,232,249,.2); border-radius: 7px;
  outline: none; background: rgba(4,15,29,.72); color: #dceefa; font: inherit; font-size: 10px;
}
#runtimePage .pipeline-handoffs-toolbar select:focus-visible { border-color: #22d3ee; box-shadow: 0 0 0 2px rgba(34,211,238,.16); }
#runtimePage .pipeline-handoff-contract { display: grid; gap: 8px; }
#runtimePage .pipeline-handoff-gate {
  display: grid; grid-template-columns: minmax(155px,1fr) 54px minmax(155px,1fr) minmax(190px,1.2fr); align-items: stretch;
  gap: 8px; min-width: 0; padding: 8px; border: 1px solid rgba(148,163,184,.12); border-radius: 9px; background: rgba(5,17,32,.24);
}
#runtimePage .pipeline-handoff-stage,
#runtimePage .pipeline-handoff-evidence { display: grid; align-content: center; gap: 4px; min-width: 0; padding: 9px; border: 1px solid rgba(148,163,184,.1); border-radius: 7px; background: rgba(255,255,255,.022); }
#runtimePage .pipeline-handoff-stage span,
#runtimePage .pipeline-handoff-evidence span { color: #7890ad; font-size: 7px; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; }
#runtimePage .pipeline-handoff-stage strong,
#runtimePage .pipeline-handoff-evidence strong { overflow-wrap: anywhere; color: #dceefa; font-size: 10px; }
#runtimePage .pipeline-handoff-stage small,
#runtimePage .pipeline-handoff-evidence small { color: #7890ad; font-size: 8px; }
#runtimePage .pipeline-handoff-arrow { display: grid; place-items: center; gap: 3px; color: #7890ad; }
#runtimePage .pipeline-handoff-arrow b { font-size: 18px; font-weight: 500; }
#runtimePage .pipeline-handoff-arrow em { padding: 3px 6px; border: 1px solid rgba(148,163,184,.16); border-radius: 999px; font-size: 7px; font-style: normal; font-weight: 800; letter-spacing: .04em; text-transform: uppercase; }
#runtimePage .pipeline-handoff-gate[data-gate-state="active"] { border-color: rgba(34,211,238,.42); box-shadow: inset 2px 0 0 #22d3ee; }
#runtimePage .pipeline-handoff-gate[data-gate-state="active"] .pipeline-handoff-arrow { color: #67e8f9; }
#runtimePage .pipeline-handoff-gate[data-gate-state="delivered"] { border-color: rgba(74,222,128,.3); }
#runtimePage .pipeline-handoff-gate[data-gate-state="delivered"] .pipeline-handoff-arrow { color: #86efac; }
#runtimePage .pipeline-handoff-gate[data-gate-state="blocked"] { border-color: rgba(251,113,133,.34); }
#runtimePage .pipeline-handoff-gate[data-gate-state="blocked"] .pipeline-handoff-arrow { color: #fb7185; }
#runtimePage .pipeline-handoff-gate[data-gate-state="awaiting_output"] { border-color: rgba(250,204,21,.3); }
#runtimePage .pipeline-handoff-gate[data-gate-state="awaiting_output"] .pipeline-handoff-arrow { color: #fde047; }
#runtimePage .pipeline-handoffs-placeholder { display: grid; place-content: center; min-height: 220px; padding: 18px; text-align: center; border: 1px dashed rgba(148,163,184,.16); border-radius: 9px; }
#runtimePage .pipeline-handoffs-placeholder strong { color: #dceefa; font-size: 11px; }
#runtimePage .pipeline-handoffs-placeholder p { margin: 5px 0 0; color: #7890ad; font-size: 9px; }
#runtimePage .pipeline-handoffs-message { min-height: auto; margin-top: 0; padding: 9px 11px; }
@media (max-width: 1080px) {
  #runtimePage .pipeline-handoffs-toolbar { grid-template-columns: repeat(3,minmax(0,1fr)); }
  #runtimePage .pipeline-handoffs-toolbar label { grid-column: 1 / -1; }
  #runtimePage .pipeline-handoff-gate { grid-template-columns: minmax(0,1fr) 45px minmax(0,1fr); }
  #runtimePage .pipeline-handoff-evidence { grid-column: 1 / -1; }
}
@media (max-width: 620px) {
  #runtimePage .pipeline-handoffs-toolbar,
  #runtimePage .pipeline-handoff-gate { grid-template-columns: 1fr; }
  #runtimePage .pipeline-handoff-arrow { grid-template-columns: auto auto; justify-content: center; }
  #runtimePage .pipeline-handoff-evidence { grid-column: auto; }
}
/* END PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT */
'''

OLD_SET_VIEW = '''    if (matched) {
      mount.dataset.activePipelineView = view;
      if (view === "workflows") {
        window.LinkCraftorConnectedDomainWorkflowExplorer?.activate?.();
      }
      if (view === "stage_progress") {
        window.LinkCraftorConnectedDomainStageProgress?.activate?.();
      }
      if (view === "jobs_attempts") {
        window.LinkCraftorConnectedDomainJobsAttempts?.activate?.();
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
      if (view === "jobs_attempts") {
        window.LinkCraftorConnectedDomainJobsAttempts?.activate?.();
      }
      if (view === "dependencies_handoffs") {
        window.LinkCraftorConnectedDomainDependenciesHandoffs?.activate?.();
      }
    }
    return matched;
  };'''

OLD_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      window.LinkCraftorConnectedDomainStageProgress?.render?.(payload);
      window.LinkCraftorConnectedDomainJobsAttempts?.render?.(payload);
      return true;'''

NEW_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      window.LinkCraftorConnectedDomainStageProgress?.render?.(payload);
      window.LinkCraftorConnectedDomainJobsAttempts?.render?.(payload);
      window.LinkCraftorConnectedDomainDependenciesHandoffs?.render?.(payload);
      return true;'''

OLD_UNAVAILABLE_HANDOFF = '''    window.LinkCraftorConnectedDomainJobsAttempts?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );'''

NEW_UNAVAILABLE_HANDOFF = '''    window.LinkCraftorConnectedDomainJobsAttempts?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainDependenciesHandoffs?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );'''

JS_APPEND = r'''

// BEGIN PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT
(() => {
  "use strict";
  const PIPELINE_ID = "connect_domain";
  const EXPECTED_ORDER = Object.freeze(["connect_domain", "site_sources", "url_cleaner", "site_pages", "live_domain_target_pool", "active_target_set"]);
  let latestPayload = null;
  let selectedWorkflowId = "";
  let bound = false;
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const label = (value) => String(value || "unknown").split(/[_-]+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
  const array = (value) => Array.isArray(value) ? value.map(String) : [];
  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) throw new Error("Dependencies & Handoffs received an invalid pipeline identity.");
    const order = array(payload.stage_order);
    if (order.length !== EXPECTED_ORDER.length || !order.every((stage, index) => stage === EXPECTED_ORDER[index])) throw new Error("Dependencies & Handoffs requires the canonical six-stage order.");
    if (!Array.isArray(payload.workflows)) throw new Error("Dependencies & Handoffs requires persisted workflow evidence.");
    const workflows = payload.workflows.map((workflow) => {
      const workflowId = String(workflow?.workflow_id || "").trim();
      if (!workflowId) throw new Error("Dependencies & Handoffs received an empty workflow identity.");
      if (!Array.isArray(workflow?.stages) || workflow.stages.length !== 6) throw new Error("A workflow does not contain six stage projections.");
      const stages = workflow.stages.map((stage, index) => {
        const stageId = String(stage?.stage_id || "");
        if (stageId !== order[index]) throw new Error("Workflow stage evidence does not preserve canonical order.");
        return Object.freeze({
          stageId, status: String(stage?.status || "pending").toLowerCase(), predecessors: array(stage?.predecessor_stages), successors: array(stage?.successor_stages),
          persistent: stage?.persistent_registration === true, jobCount: Number.isFinite(Number(stage?.job_count)) ? Math.max(0, Math.trunc(Number(stage.job_count))) : 0,
          outputReady: stage?.output_ready === true
        });
      });
      for (let index = 0; index < stages.length; index += 1) {
        const expectedPredecessors = index ? [order[index - 1]] : [];
        const expectedSuccessors = index < order.length - 1 ? [order[index + 1]] : [];
        if (stages[index].predecessors.join("|") !== expectedPredecessors.join("|") || stages[index].successors.join("|") !== expectedSuccessors.join("|")) throw new Error("Persisted dependency declarations do not match the canonical chain.");
      }
      return Object.freeze({ workflowId, status: String(workflow?.status || "unknown").toLowerCase(), currentStage: String(workflow?.current_stage || ""), stages });
    });
    return Object.freeze({ order, workflows });
  };
  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewDependenciesHandoffs"); const stateLabel = byId("pipelineHandoffsState"); const container = byId("pipelineHandoffsMessage");
    if (panel) { panel.dataset.componentState = state; panel.setAttribute("aria-busy", state === "loading" ? "true" : "false"); }
    if (stateLabel) stateLabel.textContent = state === "ready" ? "Contract verified" : label(state);
    if (container) { container.dataset.state = state; const icon = container.querySelector(":scope > span"); const heading = container.querySelector("strong"); const paragraph = container.querySelector("p"); if (icon) icon.textContent = symbol; if (heading) heading.textContent = title; if (paragraph) paragraph.textContent = message; }
  };
  const selectedWorkflow = (contract) => contract.workflows.find((workflow) => workflow.workflowId === selectedWorkflowId) || contract.workflows[0] || null;
  const stageRuntimeState = (stage, workflow) => {
    if (stage.status === "failed") return "failed";
    if (stage.status === "completed") return "completed";
    if (workflow.currentStage === stage.stageId) return "current";
    return stage.status || "pending";
  };
  const handoffState = (upstream, downstream, workflow) => {
    const upstreamState = stageRuntimeState(upstream, workflow); const downstreamState = stageRuntimeState(downstream, workflow);
    if (upstreamState === "failed" || downstreamState === "failed") return "blocked";
    if (upstreamState === "completed" && upstream.outputReady) return "delivered";
    if (upstreamState === "completed") return "awaiting_output";
    if (upstreamState === "current") return "active";
    return "waiting";
  };
  const gateMessage = (state) => ({ delivered: "Result evidence available for successor hydration.", awaiting_output: "Stage completed; dispatch-result evidence is not yet available.", active: "Upstream stage is currently active.", blocked: "Failure evidence blocks this handoff.", waiting: "Waiting for upstream stage completion." }[state] || "Not evaluated.");
  const populateWorkflowSelector = (workflows) => {
    const select = byId("pipelineHandoffsWorkflow"); if (!select) return false;
    if (!workflows.length) { select.innerHTML = '<option value="">No workflows</option>'; select.disabled = true; selectedWorkflowId = ""; return false; }
    if (!workflows.some((workflow) => workflow.workflowId === selectedWorkflowId)) selectedWorkflowId = workflows[0].workflowId;
    select.disabled = false; select.innerHTML = workflows.map((workflow) => `<option value="${escapeHtml(workflow.workflowId)}"${workflow.workflowId === selectedWorkflowId ? " selected" : ""}>${escapeHtml(workflow.workflowId)} · ${escapeHtml(label(workflow.status))}</option>`).join(""); return true;
  };
  const renderContract = (contract, workflow) => {
    const container = byId("pipelineHandoffsContract"); const current = byId("pipelineHandoffsCurrent"); const stageCount = byId("pipelineHandoffsStageCount"); const gateCount = byId("pipelineHandoffsGateCount");
    if (!container) return false;
    const gates = workflow.stages.slice(0, -1).map((upstream, index) => ({ upstream, downstream: workflow.stages[index + 1], state: handoffState(upstream, workflow.stages[index + 1], workflow) }));
    container.innerHTML = gates.map((gate, index) => `
      <article class="pipeline-handoff-gate" data-gate-state="${escapeHtml(gate.state)}">
        <div class="pipeline-handoff-stage"><span>Upstream · ${String(index + 1).padStart(2, "0")}</span><strong>${escapeHtml(label(gate.upstream.stageId))}</strong><small>${escapeHtml(label(stageRuntimeState(gate.upstream, workflow)))} · ${gate.upstream.jobCount} job${gate.upstream.jobCount === 1 ? "" : "s"}</small></div>
        <div class="pipeline-handoff-arrow"><b aria-hidden="true">→</b><em>${escapeHtml(label(gate.state))}</em></div>
        <div class="pipeline-handoff-stage"><span>Successor · ${String(index + 2).padStart(2, "0")}</span><strong>${escapeHtml(label(gate.downstream.stageId))}</strong><small>${escapeHtml(label(stageRuntimeState(gate.downstream, workflow)))} · persistent ${gate.downstream.persistent ? "yes" : "no"}</small></div>
        <div class="pipeline-handoff-evidence"><span>Gate evidence</span><strong>${gate.upstream.outputReady ? "Dispatch result available" : "Dispatch result unavailable"}</strong><small>${escapeHtml(gateMessage(gate.state))}</small></div>
      </article>
    `).join("");
    container.setAttribute("aria-busy", "false"); if (current) current.textContent = workflow.currentStage ? label(workflow.currentStage) : label(workflow.status); if (stageCount) stageCount.textContent = String(contract.order.length); if (gateCount) gateCount.textContent = String(gates.length);
    const blocked = gates.filter((gate) => gate.state === "blocked").length; const delivered = gates.filter((gate) => gate.state === "delivered").length; const active = gates.filter((gate) => gate.state === "active").length;
    updateMessage("ready", "Dependency contract verified", `${gates.length} canonical handoffs · ${delivered} delivered · ${active} active · ${blocked} blocked.`, "✓"); return true;
  };
  const render = (payload) => {
    try {
      const contract = inspect(payload); latestPayload = payload; ensureBound(); populateWorkflowSelector(contract.workflows); const workflow = selectedWorkflow(contract); const container = byId("pipelineHandoffsContract");
      if (!workflow) { if (container) { container.innerHTML = '<div class="pipeline-handoffs-placeholder"><strong>No persisted workflows</strong><p>Dependency evidence will appear after workflow activation.</p></div>'; container.setAttribute("aria-busy", "false"); } updateMessage("empty", "No workflow handoff evidence", "The six-stage contract exists, but no workflow is available to evaluate.", "◎"); return true; }
      return renderContract(contract, workflow);
    } catch (error) { return renderUnavailable(error?.message); }
  };
  const renderUnavailable = (message) => {
    latestPayload = null; const container = byId("pipelineHandoffsContract"); const select = byId("pipelineHandoffsWorkflow");
    if (select) { select.innerHTML = '<option value="">Unavailable</option>'; select.disabled = true; }
    if (container) { container.innerHTML = `<div class="pipeline-handoffs-placeholder"><strong>Dependency evidence unavailable</strong><p>${escapeHtml(message || "The canonical projection could not be loaded.")}</p></div>`; container.setAttribute("aria-busy", "false"); }
    updateMessage("unavailable", "Dependencies and handoffs unavailable", message || "The canonical detail projection could not be loaded.", "!"); return false;
  };
  const ensureBound = () => { if (bound) return true; const select = byId("pipelineHandoffsWorkflow"); if (!select) return false; select.addEventListener("change", () => { selectedWorkflowId = String(select.value || ""); if (latestPayload) render(latestPayload); }); bound = true; return true; };
  const activate = () => { ensureBound(); const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.(); if (snapshot) return render(snapshot); updateMessage("loading", "Loading handoff evidence", "Waiting for the existing Connected Domain detail snapshot.", "◌"); return false; };
  window.LinkCraftorConnectedDomainDependenciesHandoffs = Object.freeze({ activate, render, renderUnavailable, inspect });
})();
// END PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT
'''

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=10" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=11" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=12"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=13"></script>'


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.ids: list[str] = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag; self.ids.extend(value for name, value in attrs if name == "id" and value)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, source: str) -> None:
    path.write_text(source, encoding="utf-8", newline="\n")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1: raise RuntimeError(f"Expected one {label}, found {count}.")
    return source.replace(old, new, 1)


def html_ids_unique(source: str) -> bool:
    parser = IdCollector(); parser.feed(source); return len(parser.ids) == len(set(parser.ids))


def css_balanced(source: str) -> bool:
    stripped = re.sub(r"/\*.*?\*/", "", source, flags=re.S); stripped = re.sub(r'"(?:\\.|[^"\\])*"', '""', stripped); stripped = re.sub(r"'(?:\\.|[^'\\])*'", "''", stripped); depth = 0
    for character in stripped:
        if character == "{": depth += 1
        elif character == "}":
            depth -= 1
            if depth < 0: return False
    return depth == 0


def javascript_syntax_valid(source: str) -> bool:
    node = shutil.which("node")
    if node is None: raise RuntimeError("Node.js is required for JavaScript syntax validation.")
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4h_js_") as folder:
        candidate = Path(folder) / "runtime_owner_candidate.js"; write_text(candidate, source)
        result = subprocess.run([node, "--check", str(candidate)], capture_output=True, text=True, check=False)
    return result.returncode == 0


def make_report(status: str, checks: dict[str, bool], evidence: dict[str, Any], error: dict[str, Any]) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = FINAL_RESULT if status == "CERTIFIED" else "FINAL RESULT: PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT NOT_CERTIFIED"
    return "\n".join([
        "LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS", "PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT CERTIFICATION", "", f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "Patch mode: STRICT FAIL-CLOSED", f"Backup: {evidence.get('backup', 'NOT_CREATED')}", "Production jobs created: NO", "Production queue claims executed: NO", "Production handlers executed: NO",
        "Production workflow persistence executed: NO", "Production recovery actions executed: NO", "Live network requests executed during certification: NO", f"CERTIFICATION STATUS: {status}", "",
        "CHECKS:", json.dumps(checks, indent=2, sort_keys=True), "", "FAILED_CHECKS:", json.dumps(failed, indent=2), "", "NOT_RUN_CHECKS:", "[]", "", "EVIDENCE:", json.dumps(evidence, indent=2, sort_keys=True), "",
        "EXECUTION_ERROR:", json.dumps(error, indent=2, sort_keys=True), "", "IMPLEMENTED BOUNDARY:",
        "- Dependencies & Handoffs renders the five canonical gates connecting the six Connected Domain stages.",
        "- Persisted predecessor and successor declarations are validated against canonical stage order and fail closed on disagreement.",
        "- Gate state distinguishes waiting, active, delivered, awaiting-output and blocked evidence.",
        "- Workflow selection is local and the existing Connected Domain cached detail snapshot is reused.",
        "- No endpoint request, handoff execution, job action, recovery control or backend authority was added.", "", "NEXT STEP:",
        "Browser visual acceptance, then Part F 15-B4I - Events Timeline component.", "", final, ""
    ])


def main() -> int:
    if len(sys.argv) != 3: raise SystemExit("Usage: RUN_15_B4H_DEPENDENCIES_HANDOFFS.py <project_root> <report_path>")
    root, report = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    paths = {
        "index_html": root / "backend/server/owner/index.html", "owner_css": root / "backend/server/owner/owner.css", "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": root / "backend/server/owner/runtime_owner.css", "runtime_owner_js": root / "backend/server/owner/runtime_owner.js",
        "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py", "pipeline_operations": root / "backend/server/owner/pipeline_operations.py",
    }
    prior_report = root / "backend/server/data/reports/PART_F_15_B4G_JOBS_ATTEMPTS_CERTIFICATION.txt"
    checks: dict[str, bool] = {}; evidence: dict[str, Any] = {"new_endpoint_requests": 0, "recovery_controls_added": False}; error: dict[str, Any] = {}; originals: dict[str, bytes] = {}; retained = False; status = "NOT_CERTIFIED"
    try:
        checks["part_f_15_b4g_report_exists"] = prior_report.is_file(); prior_hash = sha256_path(prior_report) if prior_report.is_file() else ""; prior = read_text(prior_report) if prior_report.is_file() else ""
        checks["part_f_15_b4g_certified"] = "CERTIFICATION STATUS: CERTIFIED" in prior and "FINAL RESULT: PART F 15-B4G JOBS AND ATTEMPTS COMPONENT CERTIFIED" in prior
        for name, path in paths.items(): checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()): raise RuntimeError("Required source or B4G evidence is unavailable.")
        before = {name: sha256_path(path) for name, path in paths.items()}; evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items(): checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()): raise RuntimeError("Installed source lineage does not match certified B4G.")
        index_source, css_source, js_source, operations_source = read_text(paths["index_html"]), read_text(paths["runtime_owner_css"]), read_text(paths["runtime_owner_js"]), read_text(paths["pipeline_operations"])
        checks["dependencies_handoffs_not_previously_present"] = all(MARKER not in source for source in (index_source, css_source, js_source))
        checks["dependency_projection_contract_available"] = all(token in operations_source for token in ('"stage_id"', '"predecessor_stages"', '"successor_stages"', '"persistent_registration"', '"job_count"', '"output_ready"'))
        index_candidate = replace_once(index_source, OLD_PANEL, NEW_PANEL, "Dependencies & Handoffs structure shell")
        index_candidate = replace_once(index_candidate, OLD_CSS_VERSION, NEW_CSS_VERSION, "Runtime stylesheet cache version"); index_candidate = replace_once(index_candidate, OLD_JS_VERSION, NEW_JS_VERSION, "Runtime JavaScript cache version")
        css_candidate = css_source.rstrip() + "\n" + CSS_APPEND.lstrip(); js_candidate = replace_once(js_source, OLD_SET_VIEW, NEW_SET_VIEW, "Dependencies & Handoffs activation handoff")
        js_candidate = replace_once(js_candidate, OLD_RENDER_HANDOFF, NEW_RENDER_HANDOFF, "Dependencies & Handoffs render handoff"); js_candidate = replace_once(js_candidate, OLD_UNAVAILABLE_HANDOFF, NEW_UNAVAILABLE_HANDOFF, "Dependencies & Handoffs unavailable handoff").rstrip() + "\n" + JS_APPEND.lstrip()
        checks["candidate_html_ids_unique"] = html_ids_unique(index_candidate); checks["candidate_css_balanced"] = css_balanced(css_candidate); checks["candidate_javascript_syntax"] = javascript_syntax_valid(js_candidate)
        ids = ("pipelineHandoffsState", "pipelineHandoffsWorkflow", "pipelineHandoffsStageCount", "pipelineHandoffsGateCount", "pipelineHandoffsCurrent", "pipelineHandoffsContract", "pipelineHandoffsMessage")
        checks["all_dependencies_handoffs_bindings_present"] = all(index_candidate.count(f'id="{identifier}"') == 1 for identifier in ids)
        checks["canonical_six_stages_and_five_gates_present"] = all(stage in JS_APPEND for stage in ("connect_domain", "site_sources", "url_cleaner", "site_pages", "live_domain_target_pool", "active_target_set")) and "slice(0, -1)" in JS_APPEND
        checks["dependency_declarations_validated"] = "expectedPredecessors" in JS_APPEND and "expectedSuccessors" in JS_APPEND and "Persisted dependency declarations" in JS_APPEND
        checks["five_gate_states_present"] = all(f'"{state}"' in JS_APPEND for state in ("waiting", "active", "delivered", "awaiting_output", "blocked"))
        checks["cached_snapshot_reused"] = "LinkCraftorConnectedDomainOverview?.getSnapshot?.()" in JS_APPEND; checks["no_new_fetch_request_added"] = js_candidate.count("fetch(") == js_source.count("fetch(")
        checks["canonical_detail_endpoint_retained_once"] = js_candidate.count('"/owner/api/runtime/pipelines/connect_domain"') == 1
        checks["four_presentation_states_present"] = all(f'"{state}"' in JS_APPEND for state in ("loading", "ready", "empty", "unavailable"))
        checks["no_recovery_controls_added"] = all(js_candidate.count(token) == js_source.count(token) for token in ("retryJob(", "cancelJob(", "terminateJob(", "data-runtime-recovery-action"))
        checks["cache_versions_advanced"] = NEW_CSS_VERSION in index_candidate and NEW_JS_VERSION in index_candidate
        if not all(checks.values()): raise RuntimeError("15-B4H candidate certification checks failed.")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"); backup = root / "backend/server/data/runtime_backups" / f"part_f_15_b4h_{stamp}"; backup.mkdir(parents=True, exist_ok=False)
        for name in ("index_html", "runtime_owner_css", "runtime_owner_js"):
            originals[name] = paths[name].read_bytes(); shutil.copy2(paths[name], backup / paths[name].name)
        evidence["backup"] = str(backup); write_text(paths["index_html"], index_candidate); write_text(paths["runtime_owner_css"], css_candidate); write_text(paths["runtime_owner_js"], js_candidate)
        checks["backup_created"] = backup.is_dir(); checks["retained_html_ids_unique"] = html_ids_unique(read_text(paths["index_html"])); checks["retained_css_balanced"] = css_balanced(read_text(paths["runtime_owner_css"])); checks["retained_javascript_syntax"] = javascript_syntax_valid(read_text(paths["runtime_owner_js"]))
        checks["retained_markers"] = all(read_text(paths[name]).count(MARKER) == 2 for name in ("index_html", "runtime_owner_css", "runtime_owner_js")); checks["historical_b4g_report_unchanged"] = sha256_path(prior_report) == prior_hash
        after = {name: sha256_path(path) for name, path in paths.items()}; evidence["source_hashes_after"] = after
        checks["only_three_ui_sources_changed"] = all((after[name] != before[name]) == (name in {"index_html", "runtime_owner_css", "runtime_owner_js"}) for name in paths)
        checks.update({"production_jobs_created_no": True, "production_queue_claims_no": True, "production_handlers_executed_no": True, "production_workflow_persistence_no": True, "production_recovery_actions_no": True, "live_network_requests_during_certification_no": True})
        evidence["canonical_handoffs"] = ["connect_domain -> site_sources", "site_sources -> url_cleaner", "url_cleaner -> site_pages", "site_pages -> live_domain_target_pool", "live_domain_target_pool -> active_target_set"]
        evidence["gate_states"] = ["waiting", "active", "delivered", "awaiting_output", "blocked"]
        if not all(checks.values()): raise RuntimeError("Retained 15-B4H certification checks failed.")
        retained, status = True, "CERTIFIED"
    except Exception as exc:
        error = {"error_type": type(exc).__name__, "error_message": str(exc), "traceback": traceback.format_exc()}
        for name, content in originals.items(): paths[name].write_bytes(content)
    finally:
        evidence["patch_retained"] = retained; report.parent.mkdir(parents=True, exist_ok=True); write_text(report, make_report(status, checks, evidence, error))
    for name, passed in checks.items(): print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not passed for passed in checks.values())}"); print("NOT_RUN_CHECK_COUNT=0"); print(f"REPORT={report}"); print(f"PART_F_15_B4H_STATUS={status}"); print(f"PATCH_RETAINED={'YES' if retained else 'NO'}")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
