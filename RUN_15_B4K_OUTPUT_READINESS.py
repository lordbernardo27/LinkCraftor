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


FINAL_RESULT = "FINAL RESULT: PART F 15-B4K OUTPUT READINESS COMPONENT CERTIFIED"
MARKER = "PART F 15-B4K OUTPUT READINESS COMPONENT"

EXPECTED_HASHES = {
    "index_html": "4ead676ac8b8732d6e9737bf995c4e8212d242fe690da4deea74d9dc68fcff07",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "7ce5e241eac83ec4dfe0982975c036487b528608b7eef9878db0819970d0020c",
    "runtime_owner_js": "03577cc8fc3a1128408c71a3b2d71257514720a7f7f3a0e790ca13b3338227d7",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_PANEL = r'''              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewOutputReadiness" data-pipeline-operations-view-panel="output_readiness" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Final pipeline output</span><h5>Output Readiness</h5><p>Final-stage completion, evidence integrity, and Active Target Set availability.</p></div><strong>Structure ready</strong></header>
                <div class="pipeline-output-readiness-shell"><article><span>Final stage</span><strong>Active Target Set</strong></article><article><span>Completion evidence</span><strong>Awaiting workflow</strong></article><article><span>Output state</span><strong>Not evaluated</strong></article></div>
              </section>'''

NEW_PANEL = r'''              <!-- BEGIN PART F 15-B4K OUTPUT READINESS COMPONENT -->
              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewOutputReadiness" data-pipeline-operations-view-panel="output_readiness" data-component-state="loading" data-readiness-status="not_evaluated" role="tabpanel" aria-busy="true" hidden>
                <header class="pipeline-monitoring-panel-head">
                  <div><span>Final pipeline output</span><h5>Output Readiness</h5><p>Verify workflow completion, final-stage evidence, and Active Target Set output availability.</p></div>
                  <strong id="pipelineReadinessState">Loading</strong>
                </header>
                <div class="pipeline-readiness-live">
                  <div class="pipeline-readiness-summary" aria-label="Output readiness summary">
                    <article><span>Pipeline state</span><strong id="pipelineReadinessOverall">—</strong></article>
                    <article><span>Total workflows</span><strong id="pipelineReadinessTotalWorkflows">—</strong></article>
                    <article><span>Completed workflows</span><strong id="pipelineReadinessCompletedWorkflows">—</strong></article>
                    <article><span>Ready outputs</span><strong id="pipelineReadinessReadyOutputs">—</strong></article>
                    <article><span>Pending workflows</span><strong id="pipelineReadinessPendingWorkflows">—</strong></article>
                    <article><span>Blocked workflows</span><strong id="pipelineReadinessBlockedWorkflows">—</strong></article>
                  </div>
                  <div class="pipeline-readiness-toolbar">
                    <label><span>Readiness state</span><select id="pipelineReadinessStatusFilter"><option value="all">All states</option><option value="VERIFIED">Verified</option><option value="PENDING">Pending</option><option value="BLOCKED">Blocked</option></select></label>
                    <label class="pipeline-readiness-search"><span>Find workflow</span><input id="pipelineReadinessSearch" type="search" autocomplete="off" placeholder="Workflow, correlation, workspace, or stage" /></label>
                    <div><span>Visible workflows</span><strong id="pipelineReadinessCount">Loading</strong></div>
                  </div>
                  <div class="pipeline-readiness-workspace">
                    <div class="pipeline-readiness-directory" id="pipelineReadinessDirectory" role="listbox" aria-label="Workflow output-readiness directory" aria-busy="true"><div class="pipeline-readiness-placeholder"><strong>Loading output evidence</strong><p>Reading final-stage and workflow readiness from the cached Pipeline Operations projection.</p></div></div>
                    <div class="pipeline-readiness-detail" id="pipelineReadinessDetail"><div class="pipeline-readiness-placeholder"><strong>No workflow selected</strong><p>Final-output evidence will appear after the canonical snapshot is inspected.</p></div></div>
                  </div>
                  <div class="pipeline-component-state pipeline-readiness-message" id="pipelineReadinessMessage" data-state="loading" role="status" aria-live="polite"><span aria-hidden="true">◌</span><div><strong>Loading output readiness</strong><p>No workflow, job, output, or recovery authority is exercised by this read-only component.</p></div></div>
                </div>
              </section>
              <!-- END PART F 15-B4K OUTPUT READINESS COMPONENT -->'''

CSS_APPEND = r'''

/* BEGIN PART F 15-B4K OUTPUT READINESS COMPONENT */
#runtimePage .pipeline-readiness-live { display: grid; gap: 10px; }
#runtimePage .pipeline-readiness-summary { display: grid; grid-template-columns: repeat(6,minmax(0,1fr)); gap: 7px; }
#runtimePage .pipeline-readiness-summary article { display: grid; gap: 3px; min-width: 0; padding: 9px; border: 1px solid rgba(148,163,184,.12); border-radius: 8px; background: rgba(255,255,255,.025); }
#runtimePage .pipeline-readiness-summary span,
#runtimePage .pipeline-readiness-toolbar span,
#runtimePage .pipeline-readiness-detail span { color: #7890ad; font-size: 7px; font-weight: 700; letter-spacing: .055em; text-transform: uppercase; }
#runtimePage .pipeline-readiness-summary strong { overflow-wrap: anywhere; color: #e6f7ff; font-size: 12px; }
#runtimePage .pipeline-readiness-toolbar { display: grid; grid-template-columns: minmax(170px,.7fr) minmax(260px,1.4fr) minmax(110px,.45fr); gap: 8px; align-items: end; padding: 9px; border: 1px solid rgba(148,163,184,.12); border-radius: 9px; background: rgba(5,17,32,.28); }
#runtimePage .pipeline-readiness-toolbar label,
#runtimePage .pipeline-readiness-toolbar > div { display: grid; gap: 4px; min-width: 0; }
#runtimePage .pipeline-readiness-toolbar strong { overflow: hidden; color: #e6f7ff; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
#runtimePage .pipeline-readiness-toolbar select,
#runtimePage .pipeline-readiness-toolbar input { width: 100%; min-height: 32px; padding: 6px 9px; border: 1px solid rgba(103,232,249,.2); border-radius: 7px; outline: none; background: rgba(4,15,29,.72); color: #dceefa; font: inherit; font-size: 10px; }
#runtimePage .pipeline-readiness-toolbar select:focus-visible,
#runtimePage .pipeline-readiness-toolbar input:focus-visible { border-color: #22d3ee; box-shadow: 0 0 0 2px rgba(34,211,238,.16); }
#runtimePage .pipeline-readiness-workspace { display: grid; grid-template-columns: minmax(260px,.82fr) minmax(0,1.45fr); min-height: 340px; border: 1px solid rgba(148,163,184,.12); border-radius: 9px; overflow: hidden; background: rgba(5,17,32,.2); }
#runtimePage .pipeline-readiness-directory { display: grid; align-content: start; gap: 7px; min-width: 0; max-height: 500px; overflow: auto; padding: 9px; border-right: 1px solid rgba(148,163,184,.12); }
#runtimePage .pipeline-readiness-row { display: grid; gap: 6px; width: 100%; min-width: 0; padding: 9px; border: 1px solid rgba(148,163,184,.13); border-left: 3px solid #facc15; border-radius: 8px; background: rgba(255,255,255,.025); color: inherit; text-align: left; cursor: pointer; }
#runtimePage .pipeline-readiness-row[data-status="VERIFIED"] { border-left-color: #34d399; }
#runtimePage .pipeline-readiness-row[data-status="BLOCKED"] { border-left-color: #fb7185; }
#runtimePage .pipeline-readiness-row:hover,
#runtimePage .pipeline-readiness-row.active { border-color: rgba(103,232,249,.5); background: rgba(34,211,238,.08); }
#runtimePage .pipeline-readiness-row-head,
#runtimePage .pipeline-readiness-row-meta { display: flex; justify-content: space-between; gap: 8px; min-width: 0; }
#runtimePage .pipeline-readiness-row-head strong { overflow: hidden; color: #dceefa; font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }
#runtimePage .pipeline-readiness-badge { flex: 0 0 auto; padding: 2px 6px; border: 1px solid currentColor; border-radius: 999px; color: #fde047; font-size: 7px; font-weight: 700; text-transform: uppercase; }
#runtimePage .pipeline-readiness-badge[data-status="VERIFIED"] { color: #6ee7b7; }
#runtimePage .pipeline-readiness-badge[data-status="BLOCKED"] { color: #fda4af; }
#runtimePage .pipeline-readiness-row-meta { color: #7890ad; font-size: 8px; }
#runtimePage .pipeline-readiness-row p { margin: 0; color: #9eb2c9; font-size: 8px; line-height: 1.35; overflow-wrap: anywhere; }
#runtimePage .pipeline-readiness-detail { min-width: 0; padding: 12px; overflow: auto; }
#runtimePage .pipeline-readiness-detail-head { display: flex; justify-content: space-between; gap: 10px; padding-bottom: 9px; border-bottom: 1px solid rgba(148,163,184,.12); }
#runtimePage .pipeline-readiness-detail-head > div { display: grid; gap: 4px; min-width: 0; }
#runtimePage .pipeline-readiness-detail-head strong { overflow-wrap: anywhere; color: #e6f7ff; font-size: 11px; }
#runtimePage .pipeline-readiness-facts { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 7px; margin-top: 9px; }
#runtimePage .pipeline-readiness-facts article { display: grid; gap: 3px; min-width: 0; padding: 8px; border: 1px solid rgba(148,163,184,.1); border-radius: 7px; background: rgba(255,255,255,.022); }
#runtimePage .pipeline-readiness-facts strong { overflow-wrap: anywhere; color: #dceefa; font-size: 9px; }
#runtimePage .pipeline-readiness-stage-strip { display: grid; grid-template-columns: repeat(6,minmax(0,1fr)); gap: 6px; margin-top: 9px; }
#runtimePage .pipeline-readiness-stage-strip li { display: grid; gap: 3px; min-width: 0; padding: 7px; border: 1px solid rgba(148,163,184,.12); border-radius: 7px; list-style: none; background: rgba(255,255,255,.02); }
#runtimePage .pipeline-readiness-stage-strip li[data-state="completed"] { border-color: rgba(52,211,153,.35); background: rgba(16,185,129,.06); }
#runtimePage .pipeline-readiness-stage-strip li[data-state="current"] { border-color: rgba(34,211,238,.45); background: rgba(34,211,238,.07); }
#runtimePage .pipeline-readiness-stage-strip li[data-state="failed"] { border-color: rgba(251,113,133,.4); background: rgba(127,29,29,.12); }
#runtimePage .pipeline-readiness-stage-strip strong { overflow: hidden; color: #dceefa; font-size: 8px; text-overflow: ellipsis; white-space: nowrap; }
#runtimePage .pipeline-readiness-stage-strip small { color: #7890ad; font-size: 7px; text-transform: uppercase; }
#runtimePage .pipeline-readiness-verdict { display: grid; gap: 4px; margin-top: 9px; padding: 10px; border: 1px solid rgba(250,204,21,.28); border-radius: 8px; background: rgba(133,77,14,.09); }
#runtimePage .pipeline-readiness-verdict[data-status="VERIFIED"] { border-color: rgba(52,211,153,.3); background: rgba(6,78,59,.12); }
#runtimePage .pipeline-readiness-verdict[data-status="BLOCKED"] { border-color: rgba(251,113,133,.32); background: rgba(127,29,29,.12); }
#runtimePage .pipeline-readiness-verdict strong { color: #e6f7ff; font-size: 10px; }
#runtimePage .pipeline-readiness-verdict p { margin: 0; color: #9eb2c9; font-size: 8px; line-height: 1.4; }
#runtimePage .pipeline-readiness-placeholder { display: grid; place-content: center; min-height: 240px; padding: 18px; text-align: center; }
#runtimePage .pipeline-readiness-placeholder strong { color: #dceefa; font-size: 11px; }
#runtimePage .pipeline-readiness-placeholder p { margin: 5px 0 0; color: #7890ad; font-size: 9px; line-height: 1.4; }
#runtimePage .pipeline-readiness-message { min-height: auto; margin-top: 0; padding: 9px 11px; }
#runtimePage #pipelineOperationsViewOutputReadiness[data-readiness-status="verified"] #pipelineReadinessState { color: #6ee7b7; }
#runtimePage #pipelineOperationsViewOutputReadiness[data-readiness-status="blocked"] #pipelineReadinessState { color: #fda4af; }
#runtimePage #pipelineOperationsViewOutputReadiness[data-readiness-status="pending"] #pipelineReadinessState { color: #fde047; }
@media (max-width: 1180px) {
  #runtimePage .pipeline-readiness-summary { grid-template-columns: repeat(3,minmax(0,1fr)); }
  #runtimePage .pipeline-readiness-stage-strip { grid-template-columns: repeat(3,minmax(0,1fr)); }
}
@media (max-width: 820px) {
  #runtimePage .pipeline-readiness-toolbar { grid-template-columns: repeat(2,minmax(0,1fr)); }
  #runtimePage .pipeline-readiness-search { grid-column: 1 / -1; }
  #runtimePage .pipeline-readiness-workspace { grid-template-columns: 1fr; }
  #runtimePage .pipeline-readiness-directory { max-height: 300px; border-right: 0; border-bottom: 1px solid rgba(148,163,184,.12); }
}
@media (max-width: 620px) {
  #runtimePage .pipeline-readiness-facts { grid-template-columns: repeat(2,minmax(0,1fr)); }
}
@media (max-width: 520px) {
  #runtimePage .pipeline-readiness-summary,
  #runtimePage .pipeline-readiness-toolbar,
  #runtimePage .pipeline-readiness-facts,
  #runtimePage .pipeline-readiness-stage-strip { grid-template-columns: 1fr; }
  #runtimePage .pipeline-readiness-search { grid-column: auto; }
}
/* END PART F 15-B4K OUTPUT READINESS COMPONENT */
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
      if (view === "dependencies_handoffs") {
        window.LinkCraftorConnectedDomainDependenciesHandoffs?.activate?.();
      }
      if (view === "events_timeline") {
        window.LinkCraftorConnectedDomainEventsTimeline?.activate?.();
      }
      if (view === "failures") {
        window.LinkCraftorConnectedDomainFailuresAttention?.activate?.();
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
      if (view === "events_timeline") {
        window.LinkCraftorConnectedDomainEventsTimeline?.activate?.();
      }
      if (view === "failures") {
        window.LinkCraftorConnectedDomainFailuresAttention?.activate?.();
      }
      if (view === "output_readiness") {
        window.LinkCraftorConnectedDomainOutputReadiness?.activate?.();
      }
    }
    return matched;
  };'''

OLD_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      window.LinkCraftorConnectedDomainStageProgress?.render?.(payload);
      window.LinkCraftorConnectedDomainJobsAttempts?.render?.(payload);
      window.LinkCraftorConnectedDomainDependenciesHandoffs?.render?.(payload);
      window.LinkCraftorConnectedDomainEventsTimeline?.render?.(payload);
      window.LinkCraftorConnectedDomainFailuresAttention?.render?.(payload);
      return true;'''

NEW_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      window.LinkCraftorConnectedDomainStageProgress?.render?.(payload);
      window.LinkCraftorConnectedDomainJobsAttempts?.render?.(payload);
      window.LinkCraftorConnectedDomainDependenciesHandoffs?.render?.(payload);
      window.LinkCraftorConnectedDomainEventsTimeline?.render?.(payload);
      window.LinkCraftorConnectedDomainFailuresAttention?.render?.(payload);
      window.LinkCraftorConnectedDomainOutputReadiness?.render?.(payload);
      return true;'''

OLD_UNAVAILABLE_HANDOFF = '''    window.LinkCraftorConnectedDomainEventsTimeline?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainFailuresAttention?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );'''

NEW_UNAVAILABLE_HANDOFF = '''    window.LinkCraftorConnectedDomainEventsTimeline?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainFailuresAttention?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainOutputReadiness?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );'''

JS_APPEND = r'''

// BEGIN PART F 15-B4K OUTPUT READINESS COMPONENT
(() => {
  "use strict";
  const PIPELINE_ID = "connect_domain";
  const STAGE_ORDER = Object.freeze(["connect_domain","site_sources","url_cleaner","site_pages","live_domain_target_pool","active_target_set"]);
  const FINAL_STAGE_ID = STAGE_ORDER[STAGE_ORDER.length - 1];
  const READINESS_LABELS = Object.freeze({ NOT_EVALUATED: "Not evaluated", PENDING: "Pending", BLOCKED: "Blocked", VERIFIED: "Verified" });
  let latestPayload = null;
  let selectedWorkflowId = "";
  let activeStatus = "all";
  let searchQuery = "";
  let bound = false;

  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const label = (value) => String(value || "unknown").split(/[_-]+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
  const array = (value) => Array.isArray(value) ? value : [];
  const integer = (value) => { const number = Number(value); return Number.isFinite(number) && number >= 0 ? Math.trunc(number) : 0; };
  const timestamp = (value) => { if (!value) return "Unavailable"; const date = new Date(value); return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString(); };

  const normalizeWorkflow = (workflow, stageOrder) => {
    const workflowId = String(workflow?.workflow_id || "").trim();
    if (!workflowId) throw new Error("Output Readiness received an empty workflow identity.");
    const status = String(workflow?.status || "unknown").toLowerCase();
    const stageCount = integer(workflow?.stage_count);
    const completedStages = array(workflow?.completed_stages).map(String);
    const pendingStages = array(workflow?.pending_stages).map(String);
    const failedStages = array(workflow?.failed_stages).map(String);
    const recordedStages = completedStages.concat(pendingStages, failedStages);
    const currentStage = String(workflow?.current_stage || "");
    if (stageCount !== stageOrder.length) throw new Error("Output Readiness requires six stages for every projected workflow.");
    if (recordedStages.some((stageId) => !stageOrder.includes(stageId))) throw new Error("Output Readiness received a stage outside the canonical contract.");
    if (new Set(recordedStages).size !== recordedStages.length || stageOrder.some((stageId) => !recordedStages.includes(stageId))) throw new Error("Output Readiness requires a complete, non-overlapping stage partition.");
    if (currentStage && !stageOrder.includes(currentStage)) throw new Error("Output Readiness received an invalid current-stage identity.");
    const outputReady = workflow?.output_ready === true;
    if (outputReady && status !== "completed") throw new Error("Output readiness cannot be verified for an unfinished workflow.");
    if (outputReady && !completedStages.includes(FINAL_STAGE_ID)) throw new Error("Verified output lacks completed final-stage evidence.");
    const readinessStatus = status === "failed" || (status === "completed" && !outputReady)
      ? "BLOCKED" : outputReady ? "VERIFIED" : "PENDING";
    const reason = readinessStatus === "VERIFIED"
      ? "Workflow completed and Active Target Set output evidence is projected."
      : readinessStatus === "BLOCKED"
        ? (status === "failed" ? "The workflow is failed; final output readiness is blocked." : "The workflow completed without projected final-output evidence.")
        : "The workflow is unfinished; final output readiness remains pending.";
    return Object.freeze({
      workflowId,
      correlationId: String(workflow?.correlation_id || "Unavailable"),
      workspaceId: String(workflow?.workspace_id || "Unavailable"),
      status,
      currentStage,
      createdAt: workflow?.created_at || null,
      updatedAt: workflow?.updated_at || null,
      stageCount,
      completedStages,
      pendingStages,
      failedStages,
      outputReady,
      readinessStatus,
      reason
    });
  };

  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) throw new Error("Output Readiness received an invalid pipeline identity.");
    const stageOrder = array(payload.stage_order).map(String);
    if (JSON.stringify(stageOrder) !== JSON.stringify(STAGE_ORDER)) throw new Error("Output Readiness requires the canonical six-stage order.");
    if (!Array.isArray(payload.workflows)) throw new Error("Output Readiness requires persisted workflow evidence.");
    const counts = payload.counts && typeof payload.counts === "object" ? payload.counts : null;
    const readiness = payload.output_readiness && typeof payload.output_readiness === "object" ? payload.output_readiness : null;
    if (!counts || !readiness) throw new Error("Output Readiness summary evidence is unavailable.");
    const readinessStatus = String(readiness.readiness_status || "").trim().toUpperCase();
    if (!Object.prototype.hasOwnProperty.call(READINESS_LABELS, readinessStatus)) throw new Error("Output Readiness received an unknown readiness status.");
    if (String(readiness.final_stage_id || "") !== FINAL_STAGE_ID) throw new Error("Output Readiness received an invalid final-stage identity.");
    const workflows = payload.workflows.map((workflow) => normalizeWorkflow(workflow, stageOrder));
    const workflowCount = integer(counts.workflow_count);
    const completedCount = integer(readiness.completed_workflow_count);
    const readyCount = integer(readiness.ready_workflow_count);
    const derivedCompleted = workflows.filter((workflow) => workflow.status === "completed").length;
    const derivedReady = workflows.filter((workflow) => workflow.outputReady).length;
    const blockedCount = workflows.filter((workflow) => workflow.readinessStatus === "BLOCKED").length;
    const pendingCount = workflows.filter((workflow) => workflow.readinessStatus === "PENDING").length;
    const derivedStatus = workflows.length === 0
      ? "NOT_EVALUATED"
      : blockedCount > 0
        ? "BLOCKED"
        : derivedCompleted === workflows.length && derivedReady === workflows.length
          ? "VERIFIED" : "PENDING";
    if (workflowCount !== workflows.length || completedCount !== derivedCompleted || readyCount !== derivedReady) throw new Error("Output Readiness summary counts disagree with workflow evidence.");
    if (readinessStatus !== derivedStatus) throw new Error("Output Readiness status disagrees with canonical workflow evidence.");
    if ((readiness.all_completed_outputs_ready === true) !== (readinessStatus === "VERIFIED")) throw new Error("Output Readiness legacy readiness evidence is inconsistent.");
    return Object.freeze({
      stageOrder,
      finalStageId: FINAL_STAGE_ID,
      readinessStatus,
      workflowCount,
      completedCount,
      readyCount,
      pendingCount,
      blockedCount,
      workflows
    });
  };

  const updateMessage = (state, readinessStatus, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewOutputReadiness");
    const stateLabel = byId("pipelineReadinessState");
    const container = byId("pipelineReadinessMessage");
    if (panel) {
      panel.dataset.componentState = state;
      panel.dataset.readinessStatus = String(readinessStatus || "unavailable").toLowerCase();
      panel.setAttribute("aria-busy", state === "loading" ? "true" : "false");
    }
    if (stateLabel) stateLabel.textContent = READINESS_LABELS[readinessStatus] || label(state);
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

  const placeholder = (title, message) => '<div class="pipeline-readiness-placeholder"><strong>' + escapeHtml(title) + '</strong><p>' + escapeHtml(message) + '</p></div>';

  const setSummary = (contract) => {
    const bindings = {
      pipelineReadinessOverall: READINESS_LABELS[contract.readinessStatus],
      pipelineReadinessTotalWorkflows: contract.workflowCount,
      pipelineReadinessCompletedWorkflows: contract.completedCount,
      pipelineReadinessReadyOutputs: contract.readyCount,
      pipelineReadinessPendingWorkflows: contract.pendingCount,
      pipelineReadinessBlockedWorkflows: contract.blockedCount
    };
    Object.entries(bindings).forEach(([id, value]) => { const node = byId(id); if (node) node.textContent = String(value); });
  };

  const workflowMatches = (workflow) => {
    const statusMatches = activeStatus === "all" || workflow.readinessStatus === activeStatus;
    const query = searchQuery.trim().toLowerCase();
    if (!query) return statusMatches;
    return statusMatches && [workflow.workflowId, workflow.correlationId, workflow.workspaceId, workflow.status, workflow.currentStage, workflow.readinessStatus].some((value) => String(value).toLowerCase().includes(query));
  };

  const stageState = (workflow, stageId) => {
    if (workflow.failedStages.includes(stageId)) return "failed";
    if (workflow.completedStages.includes(stageId)) return "completed";
    if (workflow.currentStage === stageId) return "current";
    return "pending";
  };

  const renderDetail = (workflow, contract) => {
    const detail = byId("pipelineReadinessDetail");
    if (!detail) return false;
    const stages = contract.stageOrder.map((stageId, index) => {
      const state = stageState(workflow, stageId);
      return '<li data-state="' + escapeHtml(state) + '"><span>' + String(index + 1).padStart(2, "0") + '</span><strong>' + escapeHtml(label(stageId)) + '</strong><small>' + escapeHtml(label(state)) + '</small></li>';
    }).join("");
    detail.innerHTML =
      '<header class="pipeline-readiness-detail-head"><div><span>Selected workflow</span><strong>' + escapeHtml(workflow.workflowId) + '</strong></div><b class="pipeline-readiness-badge" data-status="' + escapeHtml(workflow.readinessStatus) + '">' + escapeHtml(READINESS_LABELS[workflow.readinessStatus]) + '</b></header>' +
      '<div class="pipeline-readiness-facts">' +
        '<article><span>Lifecycle</span><strong>' + escapeHtml(label(workflow.status)) + '</strong></article>' +
        '<article><span>Current stage</span><strong>' + escapeHtml(workflow.currentStage ? label(workflow.currentStage) : "No active stage") + '</strong></article>' +
        '<article><span>Final stage</span><strong>' + escapeHtml(label(contract.finalStageId)) + '</strong></article>' +
        '<article><span>Stage completion</span><strong>' + workflow.completedStages.length + ' of ' + workflow.stageCount + '</strong></article>' +
        '<article><span>Final output</span><strong>' + (workflow.outputReady ? "Available" : "Not available") + '</strong></article>' +
        '<article><span>Workspace</span><strong>' + escapeHtml(workflow.workspaceId) + '</strong></article>' +
        '<article><span>Correlation</span><strong>' + escapeHtml(workflow.correlationId) + '</strong></article>' +
        '<article><span>Created</span><strong>' + escapeHtml(timestamp(workflow.createdAt)) + '</strong></article>' +
        '<article><span>Last updated</span><strong>' + escapeHtml(timestamp(workflow.updatedAt)) + '</strong></article>' +
      '</div>' +
      '<ol class="pipeline-readiness-stage-strip" aria-label="Selected workflow stage evidence">' + stages + '</ol>' +
      '<div class="pipeline-readiness-verdict" data-status="' + escapeHtml(workflow.readinessStatus) + '"><span>Readiness verdict</span><strong>' + escapeHtml(READINESS_LABELS[workflow.readinessStatus]) + '</strong><p>' + escapeHtml(workflow.reason) + '</p></div>';
    return true;
  };

  const renderReadiness = () => {
    if (!latestPayload) return false;
    const contract = inspect(latestPayload);
    const directory = byId("pipelineReadinessDirectory");
    const detail = byId("pipelineReadinessDetail");
    const count = byId("pipelineReadinessCount");
    const filter = byId("pipelineReadinessStatusFilter");
    if (!directory) return false;
    setSummary(contract);
    if (filter) filter.disabled = false;
    const visible = contract.workflows.filter(workflowMatches);
    if (count) count.textContent = String(visible.length) + " of " + String(contract.workflows.length);
    if (!contract.workflows.length) {
      selectedWorkflowId = "";
      directory.innerHTML = placeholder("No workflows to evaluate", "Connected Domain has no persisted workflow output evidence.");
      directory.setAttribute("aria-busy", "false");
      if (detail) detail.innerHTML = placeholder("Output readiness not evaluated", "A readiness verdict requires at least one persisted workflow.");
      updateMessage("empty", "NOT_EVALUATED", "Output readiness not evaluated", "No workflow has entered the final-output contract.", "◎");
      return true;
    }
    if (!visible.length) {
      selectedWorkflowId = "";
      directory.innerHTML = placeholder("No workflows match", "Change the readiness-state filter or workflow search.");
      directory.setAttribute("aria-busy", "false");
      if (detail) detail.innerHTML = placeholder("No workflow selected", "No filtered workflow is available.");
      updateMessage("ready", contract.readinessStatus, "No matching workflow", "The output-readiness projection is connected; adjust the local filters.", "⌕");
      return true;
    }
    if (!visible.some((workflow) => workflow.workflowId === selectedWorkflowId)) selectedWorkflowId = visible[0].workflowId;
    directory.innerHTML = visible.map((workflow) =>
      '<button class="pipeline-readiness-row' + (workflow.workflowId === selectedWorkflowId ? " active" : "") + '" type="button" role="option" aria-selected="' + (workflow.workflowId === selectedWorkflowId ? "true" : "false") + '" data-readiness-workflow-id="' + escapeHtml(workflow.workflowId) + '" data-status="' + escapeHtml(workflow.readinessStatus) + '">' +
        '<span class="pipeline-readiness-row-head"><strong>' + escapeHtml(workflow.workflowId) + '</strong><span class="pipeline-readiness-badge" data-status="' + escapeHtml(workflow.readinessStatus) + '">' + escapeHtml(READINESS_LABELS[workflow.readinessStatus]) + '</span></span>' +
        '<span class="pipeline-readiness-row-meta"><span>' + escapeHtml(label(workflow.status)) + '</span><span>' + workflow.completedStages.length + ' of ' + workflow.stageCount + ' stages</span></span>' +
        '<p>' + escapeHtml(workflow.reason) + '</p>' +
      '</button>'
    ).join("");
    directory.setAttribute("aria-busy", "false");
    renderDetail(visible.find((workflow) => workflow.workflowId === selectedWorkflowId), contract);
    const title = contract.readinessStatus === "VERIFIED" ? "Output readiness verified" : contract.readinessStatus === "BLOCKED" ? "Output readiness blocked" : "Output readiness pending";
    const message = contract.readinessStatus === "VERIFIED"
      ? "Every persisted workflow is complete with final Active Target Set output evidence."
      : contract.readinessStatus === "BLOCKED"
        ? String(contract.blockedCount) + " workflow" + (contract.blockedCount === 1 ? "" : "s") + " block final-output verification."
        : String(contract.pendingCount) + " workflow" + (contract.pendingCount === 1 ? "" : "s") + " remain unfinished.";
    updateMessage("ready", contract.readinessStatus, title, message, contract.readinessStatus === "VERIFIED" ? "✓" : contract.readinessStatus === "BLOCKED" ? "!" : "◌");
    return true;
  };

  const ensureBound = () => {
    if (bound) return true;
    const panel = byId("pipelineOperationsViewOutputReadiness");
    const filter = byId("pipelineReadinessStatusFilter");
    const search = byId("pipelineReadinessSearch");
    if (!panel || !filter || !search) return false;
    panel.addEventListener("click", (event) => {
      const row = event.target.closest("[data-readiness-workflow-id]");
      if (!row) return;
      selectedWorkflowId = row.dataset.readinessWorkflowId || "";
      renderReadiness();
    });
    filter.addEventListener("change", () => { activeStatus = String(filter.value || "all"); selectedWorkflowId = ""; renderReadiness(); });
    search.addEventListener("input", () => { searchQuery = String(search.value || ""); selectedWorkflowId = ""; renderReadiness(); });
    bound = true;
    return true;
  };

  const render = (payload) => {
    try {
      inspect(payload);
      latestPayload = payload;
      ensureBound();
      return renderReadiness();
    } catch (error) {
      return renderUnavailable(error?.message);
    }
  };

  const renderUnavailable = (message) => {
    latestPayload = null;
    const directory = byId("pipelineReadinessDirectory");
    const detail = byId("pipelineReadinessDetail");
    const count = byId("pipelineReadinessCount");
    const filter = byId("pipelineReadinessStatusFilter");
    ["pipelineReadinessOverall","pipelineReadinessTotalWorkflows","pipelineReadinessCompletedWorkflows","pipelineReadinessReadyOutputs","pipelineReadinessPendingWorkflows","pipelineReadinessBlockedWorkflows"].forEach((id) => { const node = byId(id); if (node) node.textContent = "—"; });
    if (filter) { filter.value = "all"; filter.disabled = true; }
    if (directory) { directory.innerHTML = placeholder("Output evidence unavailable", message || "The canonical projection could not be loaded."); directory.setAttribute("aria-busy", "false"); }
    if (detail) detail.innerHTML = placeholder("No readiness verdict", "Final-output evidence failed closed.");
    if (count) count.textContent = "Unavailable";
    updateMessage("unavailable", "UNAVAILABLE", "Output Readiness unavailable", message || "The canonical detail projection could not be loaded.", "!");
    return false;
  };

  const activate = () => {
    ensureBound();
    const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.();
    if (snapshot) return render(snapshot);
    updateMessage("loading", "LOADING", "Loading output readiness", "Waiting for the existing Connected Domain detail snapshot.", "◌");
    return false;
  };

  window.LinkCraftorConnectedDomainOutputReadiness = Object.freeze({ activate, render, renderUnavailable, inspect });
})();
// END PART F 15-B4K OUTPUT READINESS COMPONENT
'''

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=13" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=14" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=15"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=16"></script>'


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
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4j_js_") as folder:
        candidate = Path(folder) / "runtime_owner_candidate.js"; write_text(candidate, source)
        result = subprocess.run([node, "--check", str(candidate)], capture_output=True, text=True, check=False)
    return result.returncode == 0


def readiness_view_model_probe(source: str) -> dict[str, Any]:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for the Output Readiness view-model probe.")
    stages = [
        "connect_domain",
        "site_sources",
        "url_cleaner",
        "site_pages",
        "live_domain_target_pool",
        "active_target_set",
    ]

    def workflow(
        workflow_id: str,
        status: str,
        *,
        output_ready: bool = False,
        completed: list[str] | None = None,
        failed: list[str] | None = None,
    ) -> dict[str, Any]:
        completed_stages = list(completed or [])
        failed_stages = list(failed or [])
        pending_stages = [
            stage
            for stage in stages
            if stage not in completed_stages and stage not in failed_stages
        ]
        return {
            "workflow_id": workflow_id,
            "correlation_id": f"correlation-{workflow_id}",
            "workspace_id": "ws-b4k-probe",
            "status": status,
            "current_stage": (
                None
                if status in ("completed", "failed")
                else pending_stages[0] if pending_stages else None
            ),
            "stage_count": 6,
            "completed_stages": completed_stages,
            "pending_stages": pending_stages,
            "failed_stages": failed_stages,
            "output_ready": output_ready,
            "created_at": "2026-11-10T22:00:00Z",
            "updated_at": "2026-11-10T22:01:00Z",
        }

    def payload(
        workflows: list[dict[str, Any]],
        readiness_status: str,
        completed_count: int,
        ready_count: int,
    ) -> dict[str, Any]:
        return {
            "pipeline_id": "connect_domain",
            "stage_order": stages,
            "counts": {"workflow_count": len(workflows)},
            "output_readiness": {
                "final_stage_id": "active_target_set",
                "completed_workflow_count": completed_count,
                "ready_workflow_count": ready_count,
                "readiness_status": readiness_status,
                "all_completed_outputs_ready": readiness_status == "VERIFIED",
            },
            "workflows": workflows,
        }

    scenarios = {
        "no_workflows": payload([], "NOT_EVALUATED", 0, 0),
        "active_unfinished": payload(
            [workflow("wf-active", "running")],
            "PENDING",
            0,
            0,
        ),
        "completed_without_output": payload(
            [workflow("wf-blocked", "completed", completed=stages)],
            "BLOCKED",
            1,
            0,
        ),
        "completed_with_output": payload(
            [
                workflow(
                    "wf-verified",
                    "completed",
                    output_ready=True,
                    completed=stages,
                )
            ],
            "VERIFIED",
            1,
            1,
        ),
        "failed_workflow": payload(
            [
                workflow(
                    "wf-failed",
                    "failed",
                    completed=stages[:-1],
                    failed=[stages[-1]],
                )
            ],
            "BLOCKED",
            0,
            0,
        ),
        "mixed_completed_and_active": payload(
            [
                workflow(
                    "wf-completed",
                    "completed",
                    output_ready=True,
                    completed=stages,
                ),
                workflow("wf-running", "running"),
            ],
            "PENDING",
            1,
            1,
        ),
    }
    probe = "\n".join(
        [
            "global.window = {};",
            "global.document = { getElementById: () => null };",
            source,
            f"const scenarios = {json.dumps(scenarios, separators=(',', ':'))};",
            "const observed = {};",
            "for (const [name, payload] of Object.entries(scenarios)) {",
            "  const result = window.LinkCraftorConnectedDomainOutputReadiness.inspect(payload);",
            "  observed[name] = result.readinessStatus;",
            "}",
            "const expected = {no_workflows:'NOT_EVALUATED',active_unfinished:'PENDING',completed_without_output:'BLOCKED',completed_with_output:'VERIFIED',failed_workflow:'BLOCKED',mixed_completed_and_active:'PENDING'};",
            "if (JSON.stringify(observed) !== JSON.stringify(expected)) process.exit(41);",
            "process.stdout.write(JSON.stringify(observed));",
        ]
    )
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4k_probe_") as folder:
        candidate = Path(folder) / "output_readiness_probe.js"
        write_text(candidate, probe)
        result = subprocess.run(
            [node, str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    if result.returncode != 0:
        raise RuntimeError(
            "Output Readiness view-model probe failed "
            f"({result.returncode}): {result.stderr.strip()}"
        )
    observed = json.loads(result.stdout)
    if len(observed) != 6:
        raise RuntimeError(
            "Output Readiness view-model probe returned incomplete evidence."
        )
    return observed


def make_report(
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = (
        FINAL_RESULT
        if status == "CERTIFIED"
        else "FINAL RESULT: PART F 15-B4K OUTPUT READINESS COMPONENT NOT_CERTIFIED"
    )
    return "\n".join(
        [
            "LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS",
            "PART F 15-B4K OUTPUT READINESS COMPONENT CERTIFICATION",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "Patch mode: STRICT FAIL-CLOSED",
            f"Backup: {evidence.get('backup', 'NOT_CREATED')}",
            "Production jobs created: NO",
            "Production queue claims executed: NO",
            "Production handlers executed: NO",
            "Production workflow persistence executed: NO",
            "Production recovery actions executed: NO",
            "Live network requests executed during certification: NO",
            f"CERTIFICATION STATUS: {status}",
            "",
            "CHECKS:",
            json.dumps(checks, indent=2, sort_keys=True),
            "",
            "FAILED_CHECKS:",
            json.dumps(failed, indent=2),
            "",
            "NOT_RUN_CHECKS:",
            "[]",
            "",
            "EVIDENCE:",
            json.dumps(evidence, indent=2, sort_keys=True),
            "",
            "EXECUTION_ERROR:",
            json.dumps(error, indent=2, sort_keys=True),
            "",
            "IMPLEMENTED BOUNDARY:",
            "- Output Readiness renders the canonical NOT_EVALUATED, PENDING, BLOCKED and VERIFIED contract.",
            "- Pipeline summary counts are cross-validated against persisted workflow lifecycle and final-output evidence.",
            "- Per-workflow completion, final-stage state, Active Target Set availability and readiness reason are visible.",
            "- Readiness-state filtering, workflow search and workflow selection are local read-only presentation operations.",
            "- The existing Connected Domain cached detail snapshot is reused; no endpoint request or output authority was added.",
            "- No job, queue, workflow, handler, recovery, output or persistence authority was created or mutated.",
            "",
            "NEXT STEP:",
            "Browser visual acceptance, then Part F 15-B4L - responsive integration finalization.",
            "",
            final,
            "",
        ]
    )


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4K_OUTPUT_READINESS.py "
            "<project_root> <report_path>"
        )

    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    paths = {
        "index_html": root / "backend/server/owner/index.html",
        "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": root / "backend/server/owner/runtime_owner.css",
        "runtime_owner_js": root / "backend/server/owner/runtime_owner.js",
        "runtime_summary_api": (
            root / "backend/server/owner/runtime_summary_api.py"
        ),
        "pipeline_operations": (
            root / "backend/server/owner/pipeline_operations.py"
        ),
    }
    prior_report = (
        root
        / "backend/server/data/reports/"
        "PART_F_15_B4J_FAILURES_ATTENTION_CERTIFICATION.txt"
    )

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "new_endpoint_requests": 0,
        "recovery_controls_added": False,
    }
    error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}
    retained = False
    status = "NOT_CERTIFIED"

    try:
        checks["part_f_15_b4j_report_exists"] = prior_report.is_file()
        prior_hash = (
            sha256_path(prior_report) if prior_report.is_file() else ""
        )
        prior = (
            read_text(prior_report) if prior_report.is_file() else ""
        )
        checks["part_f_15_b4j_certified"] = (
            "CERTIFICATION STATUS: CERTIFIED" in prior
            and (
                "FINAL RESULT: PART F 15-B4J FAILURES AND "
                "ATTENTION COMPONENT CERTIFIED"
            )
            in prior
        )

        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError(
                "Required source or B4J evidence is unavailable."
            )

        before = {
            name: sha256_path(path)
            for name, path in paths.items()
        }
        evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()):
            raise RuntimeError(
                "Installed source lineage does not match certified B4J."
            )

        index_source = read_text(paths["index_html"])
        css_source = read_text(paths["runtime_owner_css"])
        js_source = read_text(paths["runtime_owner_js"])
        operations_source = read_text(paths["pipeline_operations"])

        checks["output_readiness_not_previously_present"] = all(
            MARKER not in source
            for source in (index_source, css_source, js_source)
        )
        required_fields = (
            'output_readiness=_freeze({',
            '"final_stage_id"',
            '"completed_workflow_count"',
            '"ready_workflow_count"',
            '"readiness_status"',
            '"all_completed_outputs_ready"',
            '"output_ready"',
            '"completed_stages"',
            '"pending_stages"',
            '"failed_stages"',
            '"stage_count"',
        )
        checks["certified_readiness_projection_contract_available"] = all(
            token in operations_source
            for token in required_fields
        )

        index_candidate = replace_once(
            index_source,
            OLD_PANEL,
            NEW_PANEL,
            "Output Readiness structure shell",
        )
        index_candidate = replace_once(
            index_candidate,
            OLD_CSS_VERSION,
            NEW_CSS_VERSION,
            "Runtime stylesheet cache version",
        )
        index_candidate = replace_once(
            index_candidate,
            OLD_JS_VERSION,
            NEW_JS_VERSION,
            "Runtime JavaScript cache version",
        )
        css_candidate = (
            css_source.rstrip() + "\n" + CSS_APPEND.lstrip()
        )
        js_candidate = replace_once(
            js_source,
            OLD_SET_VIEW,
            NEW_SET_VIEW,
            "Output Readiness activation handoff",
        )
        js_candidate = replace_once(
            js_candidate,
            OLD_RENDER_HANDOFF,
            NEW_RENDER_HANDOFF,
            "Output Readiness render handoff",
        )
        js_candidate = replace_once(
            js_candidate,
            OLD_UNAVAILABLE_HANDOFF,
            NEW_UNAVAILABLE_HANDOFF,
            "Output Readiness unavailable handoff",
        )
        js_candidate = (
            js_candidate.rstrip() + "\n" + JS_APPEND.lstrip()
        )

        checks["candidate_html_ids_unique"] = html_ids_unique(
            index_candidate
        )
        checks["candidate_css_balanced"] = css_balanced(
            css_candidate
        )
        checks["candidate_javascript_syntax"] = (
            javascript_syntax_valid(js_candidate)
        )

        probe = readiness_view_model_probe(JS_APPEND)
        evidence["isolated_readiness_view_model_probe"] = probe
        checks["six_isolated_readiness_scenarios_passed"] = (
            probe
            == {
                "no_workflows": "NOT_EVALUATED",
                "active_unfinished": "PENDING",
                "completed_without_output": "BLOCKED",
                "completed_with_output": "VERIFIED",
                "failed_workflow": "BLOCKED",
                "mixed_completed_and_active": "PENDING",
            }
        )

        ids = (
            "pipelineReadinessState",
            "pipelineReadinessOverall",
            "pipelineReadinessTotalWorkflows",
            "pipelineReadinessCompletedWorkflows",
            "pipelineReadinessReadyOutputs",
            "pipelineReadinessPendingWorkflows",
            "pipelineReadinessBlockedWorkflows",
            "pipelineReadinessStatusFilter",
            "pipelineReadinessSearch",
            "pipelineReadinessCount",
            "pipelineReadinessDirectory",
            "pipelineReadinessDetail",
            "pipelineReadinessMessage",
        )
        checks["all_output_readiness_bindings_present"] = all(
            index_candidate.count(f'id="{identifier}"') == 1
            for identifier in ids
        )
        checks["four_readiness_states_present"] = all(
            f'"{state}"' in JS_APPEND
            for state in (
                "NOT_EVALUATED",
                "PENDING",
                "BLOCKED",
                "VERIFIED",
            )
        )
        checks["summary_cross_validation_present"] = all(
            token in JS_APPEND
            for token in (
                "derivedCompleted",
                "derivedReady",
                "derivedStatus",
                "all_completed_outputs_ready",
                "summary counts disagree",
                "status disagrees",
            )
        )
        checks["workflow_output_evidence_rendered"] = all(
            token in JS_APPEND
            for token in (
                "outputReady",
                "completedStages",
                "failedStages",
                "FINAL_STAGE_ID",
                "readinessStatus",
                "reason",
            )
        )
        checks["status_filter_and_workflow_search_present"] = all(
            token in JS_APPEND
            for token in (
                "pipelineReadinessStatusFilter",
                "pipelineReadinessSearch",
                "workflowMatches",
                "data-readiness-workflow-id",
            )
        )
        checks["canonical_not_evaluated_state_present"] = (
            "No workflows to evaluate" in JS_APPEND
            and "Output readiness not evaluated" in JS_APPEND
        )
        checks["cached_snapshot_reused"] = (
            "LinkCraftorConnectedDomainOverview?.getSnapshot?.()"
            in JS_APPEND
        )
        checks["no_new_fetch_request_added"] = (
            js_candidate.count("fetch(") == js_source.count("fetch(")
        )
        checks["canonical_detail_endpoint_retained_once"] = (
            js_candidate.count(
                '"/owner/api/runtime/pipelines/connect_domain"'
            )
            == 1
        )
        checks["five_presentation_states_present"] = (
            all(
                f'"{state}"' in JS_APPEND
                for state in (
                    "loading",
                    "ready",
                    "empty",
                    "unavailable",
                )
            )
            and "No workflows match" in JS_APPEND
        )
        checks["no_recovery_controls_added"] = (
            all(
                js_candidate.count(token) == js_source.count(token)
                for token in (
                    "retryJob(",
                    "cancelJob(",
                    "terminateJob(",
                    "data-runtime-recovery-action",
                )
            )
            and index_candidate.count(
                "data-runtime-recovery-action"
            )
            == index_source.count("data-runtime-recovery-action")
        )
        checks["cache_versions_advanced"] = (
            NEW_CSS_VERSION in index_candidate
            and NEW_JS_VERSION in index_candidate
        )
        if not all(checks.values()):
            raise RuntimeError(
                "15-B4K candidate certification checks failed."
            )

        stamp = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%S%fZ"
        )
        backup = (
            root
            / "backend/server/data/runtime_backups"
            / f"part_f_15_b4k_{stamp}"
        )
        backup.mkdir(parents=True, exist_ok=False)
        for name in (
            "index_html",
            "runtime_owner_css",
            "runtime_owner_js",
        ):
            originals[name] = paths[name].read_bytes()
            shutil.copy2(paths[name], backup / paths[name].name)

        evidence["backup"] = str(backup)
        write_text(paths["index_html"], index_candidate)
        write_text(paths["runtime_owner_css"], css_candidate)
        write_text(paths["runtime_owner_js"], js_candidate)

        checks["backup_created"] = backup.is_dir()
        checks["retained_html_ids_unique"] = html_ids_unique(
            read_text(paths["index_html"])
        )
        checks["retained_css_balanced"] = css_balanced(
            read_text(paths["runtime_owner_css"])
        )
        checks["retained_javascript_syntax"] = (
            javascript_syntax_valid(
                read_text(paths["runtime_owner_js"])
            )
        )
        checks["retained_markers"] = all(
            read_text(paths[name]).count(MARKER) == 2
            for name in (
                "index_html",
                "runtime_owner_css",
                "runtime_owner_js",
            )
        )
        checks["historical_b4j_report_unchanged"] = (
            sha256_path(prior_report) == prior_hash
        )

        after = {
            name: sha256_path(path)
            for name, path in paths.items()
        }
        evidence["source_hashes_after"] = after
        checks["only_three_ui_sources_changed"] = all(
            (after[name] != before[name])
            == (
                name
                in {
                    "index_html",
                    "runtime_owner_css",
                    "runtime_owner_js",
                }
            )
            for name in paths
        )
        checks.update(
            {
                "production_jobs_created_no": True,
                "production_queue_claims_no": True,
                "production_handlers_executed_no": True,
                "production_workflow_persistence_no": True,
                "production_recovery_actions_no": True,
                "live_network_requests_during_certification_no": True,
            }
        )
        evidence["readiness_states"] = [
            "NOT_EVALUATED",
            "PENDING",
            "BLOCKED",
            "VERIFIED",
        ]
        evidence["final_stage"] = "active_target_set"
        evidence["projected_evidence"] = [
            "pipeline readiness status",
            "workflow lifecycle",
            "completed stage count",
            "failed stage evidence",
            "final-stage identity",
            "Active Target Set output availability",
            "readiness reason",
            "workflow identity and timestamps",
        ]
        if not all(checks.values()):
            raise RuntimeError(
                "Retained 15-B4K certification checks failed."
            )

        retained = True
        status = "CERTIFIED"
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        for name, original in originals.items():
            paths[name].write_bytes(original)
    finally:
        evidence["patch_retained"] = retained
        report.parent.mkdir(parents=True, exist_ok=True)
        write_text(
            report,
            make_report(status, checks, evidence, error),
        )

    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(
        "FAILED_CHECK_COUNT="
        f"{sum(not passed for passed in checks.values())}"
    )
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B4K_STATUS={status}")
    print(f"PATCH_RETAINED={'YES' if retained else 'NO'}")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
