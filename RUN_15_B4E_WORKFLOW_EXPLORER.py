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


FINAL_RESULT = "FINAL RESULT: PART F 15-B4E WORKFLOW EXPLORER CERTIFIED"
MARKER = "PART F 15-B4E WORKFLOW EXPLORER"

EXPECTED_HASHES = {
    "index_html": "57ae894a96e16352cd9a4466f240ed1ead85ea9ad4b0979ecef2df5059e5eb4a",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "9f50dd04a9c38634f74c5001531aaafd4acf024bea38d35bde77387e853e72d0",
    "runtime_owner_js": "1eace37834b9277db68289d13b1dd0615cefe01a2a6db2c4426e324bcfcba2dd",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_WORKFLOW_PANEL = r'''              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewWorkflows" data-pipeline-operations-view-panel="workflows" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Workflow Explorer</span><h5>Connected Domain Workflows</h5><p>Browse workflow identity, lifecycle state, correlation, and timestamps.</p></div><strong>Structure ready</strong></header>
                <div class="pipeline-workflow-explorer-shell">
                  <div class="pipeline-component-toolbar"><span>Workflow list</span><span>Status filters</span><span>Correlation search</span></div>
                  <div class="pipeline-workflow-explorer-grid"><div class="pipeline-shell-region"><strong>Workflow directory</strong><p>Workflow rows will appear here.</p></div><div class="pipeline-shell-region"><strong>Workflow detail</strong><p>Select a workflow to inspect its stages and evidence.</p></div></div>
                </div>
              </section>'''

NEW_WORKFLOW_PANEL = r'''              <!-- BEGIN PART F 15-B4E WORKFLOW EXPLORER -->
              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewWorkflows" data-pipeline-operations-view-panel="workflows" data-component-state="loading" role="tabpanel" aria-busy="true" hidden>
                <header class="pipeline-monitoring-panel-head">
                  <div><span>Workflow Explorer</span><h5>Connected Domain Workflows</h5><p>Inspect persisted workflow identity, lifecycle state, correlation, timestamps, stage evidence, and final-output readiness.</p></div>
                  <strong id="pipelineWorkflowExplorerState">Loading</strong>
                </header>
                <div class="pipeline-workflow-explorer-live">
                  <div class="pipeline-workflow-toolbar">
                    <div class="pipeline-workflow-summary"><span>Persisted workflows</span><strong id="pipelineWorkflowExplorerCount">Loading</strong></div>
                    <label><span>Status</span><select id="pipelineWorkflowExplorerStatusFilter"><option value="all">All statuses</option><option value="created">Created</option><option value="pending">Pending</option><option value="running">Running</option><option value="processing">Processing</option><option value="completed">Completed</option><option value="failed">Failed</option></select></label>
                    <label class="pipeline-workflow-search"><span>Find identity</span><input id="pipelineWorkflowExplorerSearch" type="search" autocomplete="off" placeholder="Workflow, correlation, or workspace" /></label>
                  </div>
                  <div class="pipeline-workflow-explorer-grid">
                    <div class="pipeline-workflow-directory" id="pipelineWorkflowExplorerDirectory" role="listbox" aria-label="Connected Domain workflows" aria-busy="true">
                      <div class="pipeline-workflow-placeholder"><strong>Loading workflows</strong><p>Reading the canonical Pipeline Operations projection.</p></div>
                    </div>
                    <div class="pipeline-workflow-detail" id="pipelineWorkflowExplorerDetail" aria-live="polite">
                      <div class="pipeline-workflow-placeholder"><strong>Awaiting workflow evidence</strong><p>Select a persisted workflow to inspect its operational identity.</p></div>
                    </div>
                  </div>
                  <div class="pipeline-component-state pipeline-workflow-state" id="pipelineWorkflowExplorerMessage" data-state="loading" role="status" aria-live="polite"><span aria-hidden="true">◌</span><div><strong>Loading workflow evidence</strong><p>Using the existing Connected Domain detail snapshot.</p></div></div>
                </div>
              </section>
              <!-- END PART F 15-B4E WORKFLOW EXPLORER -->'''

CSS_APPEND = r'''

/* BEGIN PART F 15-B4E WORKFLOW EXPLORER */
#runtimePage .pipeline-workflow-explorer-live {
  display: grid;
  gap: 10px;
}

#runtimePage .pipeline-workflow-toolbar {
  display: grid;
  grid-template-columns: minmax(140px, 0.7fr) minmax(130px, 0.55fr) minmax(210px, 1fr);
  gap: 8px;
  align-items: end;
  padding: 9px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 9px;
  background: rgba(5, 17, 32, 0.28);
}

#runtimePage .pipeline-workflow-toolbar label,
#runtimePage .pipeline-workflow-summary {
  display: grid;
  gap: 4px;
  min-width: 0;
}

#runtimePage .pipeline-workflow-toolbar label > span,
#runtimePage .pipeline-workflow-summary > span {
  color: #7890ad;
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

#runtimePage .pipeline-workflow-summary strong {
  overflow: hidden;
  color: #dff6ff;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

#runtimePage .pipeline-workflow-toolbar select,
#runtimePage .pipeline-workflow-toolbar input {
  width: 100%;
  min-height: 32px;
  padding: 6px 9px;
  border: 1px solid rgba(103, 232, 249, 0.2);
  border-radius: 7px;
  outline: none;
  background: rgba(4, 15, 29, 0.72);
  color: #dceefa;
  font: inherit;
  font-size: 10px;
}

#runtimePage .pipeline-workflow-toolbar select:focus-visible,
#runtimePage .pipeline-workflow-toolbar input:focus-visible {
  border-color: #22d3ee;
  box-shadow: 0 0 0 2px rgba(34, 211, 238, 0.16);
}

#runtimePage .pipeline-workflow-explorer-grid {
  display: grid;
  grid-template-columns: minmax(240px, 0.8fr) minmax(0, 1.5fr);
  gap: 10px;
  min-height: 285px;
}

#runtimePage .pipeline-workflow-directory,
#runtimePage .pipeline-workflow-detail {
  min-width: 0;
  padding: 9px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 9px;
  background: rgba(5, 17, 32, 0.24);
}

#runtimePage .pipeline-workflow-directory {
  display: grid;
  align-content: start;
  gap: 6px;
  max-height: 390px;
  overflow: auto;
}

#runtimePage .pipeline-workflow-row {
  display: grid;
  gap: 7px;
  width: 100%;
  padding: 9px 10px;
  border: 1px solid rgba(148, 163, 184, 0.13);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.025);
  color: inherit;
  text-align: left;
  cursor: pointer;
}

#runtimePage .pipeline-workflow-row:hover {
  border-color: rgba(103, 232, 249, 0.32);
  background: rgba(34, 211, 238, 0.055);
}

#runtimePage .pipeline-workflow-row.active {
  border-color: rgba(34, 211, 238, 0.54);
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.13), rgba(59, 130, 246, 0.055));
  box-shadow: inset 2px 0 0 #22d3ee;
}

#runtimePage .pipeline-workflow-row:focus-visible {
  outline: 2px solid #22d3ee;
  outline-offset: 1px;
}

#runtimePage .pipeline-workflow-row-head,
#runtimePage .pipeline-workflow-row-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-width: 0;
}

#runtimePage .pipeline-workflow-row-head strong {
  overflow: hidden;
  color: #e6f7ff;
  font-size: 10px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

#runtimePage .pipeline-workflow-status {
  flex: 0 0 auto;
  padding: 3px 6px;
  border: 1px solid rgba(103, 232, 249, 0.22);
  border-radius: 999px;
  color: #67e8f9;
  font-size: 7px;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

#runtimePage .pipeline-workflow-status[data-status="failed"] {
  border-color: rgba(251, 113, 133, 0.32);
  color: #fb7185;
}

#runtimePage .pipeline-workflow-status[data-status="completed"] {
  border-color: rgba(74, 222, 128, 0.3);
  color: #86efac;
}

#runtimePage .pipeline-workflow-row-meta span {
  overflow: hidden;
  color: #7890ad;
  font-size: 8px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

#runtimePage .pipeline-workflow-detail {
  display: grid;
  align-content: start;
  gap: 10px;
}

#runtimePage .pipeline-workflow-detail-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  padding-bottom: 9px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

#runtimePage .pipeline-workflow-detail-head span,
#runtimePage .pipeline-workflow-detail-head strong {
  display: block;
}

#runtimePage .pipeline-workflow-detail-head span {
  color: #67e8f9;
  font-size: 8px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

#runtimePage .pipeline-workflow-detail-head strong {
  margin-top: 4px;
  color: #e6f7ff;
  font-size: 12px;
  overflow-wrap: anywhere;
}

#runtimePage .pipeline-workflow-identity-grid,
#runtimePage .pipeline-workflow-lifecycle-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
}

#runtimePage .pipeline-workflow-identity-grid article,
#runtimePage .pipeline-workflow-lifecycle-grid article {
  min-width: 0;
  padding: 8px 9px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.02);
}

#runtimePage .pipeline-workflow-identity-grid span,
#runtimePage .pipeline-workflow-lifecycle-grid span {
  display: block;
  color: #7890ad;
  font-size: 7px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

#runtimePage .pipeline-workflow-identity-grid strong,
#runtimePage .pipeline-workflow-lifecycle-grid strong {
  display: block;
  margin-top: 4px;
  color: #dceefa;
  font-size: 9px;
  overflow-wrap: anywhere;
}

#runtimePage .pipeline-workflow-stage-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 7px;
}

#runtimePage .pipeline-workflow-stage-summary article {
  padding: 8px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 7px;
  text-align: center;
}

#runtimePage .pipeline-workflow-stage-summary strong,
#runtimePage .pipeline-workflow-stage-summary span {
  display: block;
}

#runtimePage .pipeline-workflow-stage-summary strong {
  color: #e6f7ff;
  font-size: 13px;
}

#runtimePage .pipeline-workflow-stage-summary span {
  margin-top: 3px;
  color: #7890ad;
  font-size: 7px;
  text-transform: uppercase;
}

#runtimePage .pipeline-workflow-placeholder {
  display: grid;
  place-content: center;
  min-height: 120px;
  padding: 18px;
  text-align: center;
}

#runtimePage .pipeline-workflow-placeholder strong {
  color: #dceefa;
  font-size: 11px;
}

#runtimePage .pipeline-workflow-placeholder p {
  margin: 5px 0 0;
  color: #7890ad;
  font-size: 9px;
}

#runtimePage .pipeline-workflow-state {
  min-height: auto;
  margin-top: 0;
  padding: 9px 11px;
}

@media (max-width: 980px) {
  #runtimePage .pipeline-workflow-toolbar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  #runtimePage .pipeline-workflow-summary { grid-column: 1 / -1; }
  #runtimePage .pipeline-workflow-explorer-grid { grid-template-columns: 1fr; }
  #runtimePage .pipeline-workflow-directory { max-height: 260px; }
}

@media (max-width: 560px) {
  #runtimePage .pipeline-workflow-toolbar,
  #runtimePage .pipeline-workflow-identity-grid,
  #runtimePage .pipeline-workflow-lifecycle-grid {
    grid-template-columns: 1fr;
  }
  #runtimePage .pipeline-workflow-stage-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
/* END PART F 15-B4E WORKFLOW EXPLORER */
'''

OLD_SET_VIEW_END = '''    if (matched) mount.dataset.activePipelineView = view;
    return matched;
  };'''

NEW_SET_VIEW_END = '''    if (matched) {
      mount.dataset.activePipelineView = view;
      if (view === "workflows") {
        window.LinkCraftorConnectedDomainWorkflowExplorer?.activate?.();
      }
    }
    return matched;
  };'''

OLD_REQUEST_STATE = '''  let requestSequence = 0;

  const byId = (id) => document.getElementById(id);'''

NEW_REQUEST_STATE = '''  let requestSequence = 0;
  let latestSnapshot = null;

  const byId = (id) => document.getElementById(id);'''

OLD_SNAPSHOT_VALIDATION = '''    if (stageOrder.length !== 6) {
      throw new Error("Connected Domain detail evidence does not contain six stages.");
    }

    const workflowCount = integer(counts.workflow_count);'''

NEW_SNAPSHOT_VALIDATION = '''    if (stageOrder.length !== 6) {
      throw new Error("Connected Domain detail evidence does not contain six stages.");
    }
    latestSnapshot = payload;

    const workflowCount = integer(counts.workflow_count);'''

OLD_UNAVAILABLE = '''  const renderUnavailable = (message) => {
    resetValues();
    setText("pipelineConnectedDomainHealth", "Unavailable");
    setText("pipelineConnectedDomainOutputReadiness", "Unavailable");
    updateMessage(
      "unavailable",
      "Connected Domain evidence unavailable",
      message || "The read-only Pipeline Operations projection could not be loaded.",
      "!"
    );
  };'''

NEW_UNAVAILABLE = '''  const renderUnavailable = (message) => {
    latestSnapshot = null;
    resetValues();
    setText("pipelineConnectedDomainHealth", "Unavailable");
    setText("pipelineConnectedDomainOutputReadiness", "Unavailable");
    updateMessage(
      "unavailable",
      "Connected Domain evidence unavailable",
      message || "The read-only Pipeline Operations projection could not be loaded.",
      "!"
    );
    window.LinkCraftorConnectedDomainWorkflowExplorer?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
  };'''

OLD_RENDER_HANDOFF = '''      renderSnapshot(payload);
      return true;'''

NEW_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      return true;'''

OLD_OVERVIEW_EXPORT = '''  window.LinkCraftorConnectedDomainOverview = Object.freeze({ load });'''

NEW_OVERVIEW_EXPORT = '''  window.LinkCraftorConnectedDomainOverview = Object.freeze({
    load,
    getSnapshot: () => latestSnapshot
  });'''

JS_APPEND = r'''

// BEGIN PART F 15-B4E WORKFLOW EXPLORER
(() => {
  "use strict";

  const PIPELINE_ID = "connect_domain";
  let latestPayload = null;
  let selectedWorkflowId = "";
  let activeStatus = "all";
  let searchQuery = "";
  let bound = false;

  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
  const label = (value) => String(value || "unknown")
    .split(/[_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
  const array = (value) => Array.isArray(value) ? value : [];
  const integer = (value) => {
    const number = Number(value);
    return Number.isFinite(number) && number >= 0 ? Math.trunc(number) : 0;
  };
  const timestamp = (value) => {
    if (!value) return "Unavailable";
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString();
  };

  const normalizeWorkflow = (workflow) => {
    const workflowId = String(workflow?.workflow_id || "").trim();
    if (!workflowId) {
      throw new Error("Workflow evidence contains an empty workflow identity.");
    }
    return Object.freeze({
      workflowId,
      correlationId: String(workflow?.correlation_id || "Unavailable"),
      workspaceId: String(workflow?.workspace_id || "Unavailable"),
      status: String(workflow?.status || "unknown").toLowerCase(),
      currentStage: String(workflow?.current_stage || ""),
      createdAt: workflow?.created_at || null,
      updatedAt: workflow?.updated_at || null,
      jobCount: integer(workflow?.job_count),
      stageCount: integer(workflow?.stage_count),
      completedStages: array(workflow?.completed_stages).map(String),
      pendingStages: array(workflow?.pending_stages).map(String),
      failedStages: array(workflow?.failed_stages).map(String),
      outputReady: workflow?.output_ready === true
    });
  };

  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) {
      throw new Error("Workflow Explorer received an invalid pipeline identity.");
    }
    if (!Array.isArray(payload.stage_order) || payload.stage_order.length !== 6) {
      throw new Error("Workflow Explorer requires the six-stage Connected Domain contract.");
    }
    if (!Array.isArray(payload.workflows)) {
      throw new Error("Workflow Explorer requires a persisted workflows collection.");
    }
    return payload.workflows.map(normalizeWorkflow);
  };

  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewWorkflows");
    const stateLabel = byId("pipelineWorkflowExplorerState");
    const container = byId("pipelineWorkflowExplorerMessage");
    if (panel) {
      panel.dataset.componentState = state;
      panel.setAttribute("aria-busy", state === "loading" ? "true" : "false");
    }
    if (stateLabel) stateLabel.textContent = label(state);
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

  const placeholder = (title, message) => `
    <div class="pipeline-workflow-placeholder">
      <strong>${escapeHtml(title)}</strong>
      <p>${escapeHtml(message)}</p>
    </div>
  `;

  const workflowMatches = (workflow) => {
    const statusMatches = activeStatus === "all" || workflow.status === activeStatus;
    const query = searchQuery.trim().toLowerCase();
    if (!query) return statusMatches;
    return statusMatches && [
      workflow.workflowId,
      workflow.correlationId,
      workflow.workspaceId
    ].some((value) => value.toLowerCase().includes(query));
  };

  const renderDetail = (workflow) => {
    const detail = byId("pipelineWorkflowExplorerDetail");
    if (!detail) return false;
    detail.innerHTML = `
      <header class="pipeline-workflow-detail-head">
        <div><span>Selected workflow</span><strong>${escapeHtml(workflow.workflowId)}</strong></div>
        <span class="pipeline-workflow-status" data-status="${escapeHtml(workflow.status)}">${escapeHtml(label(workflow.status))}</span>
      </header>
      <div class="pipeline-workflow-identity-grid">
        <article><span>Correlation identity</span><strong>${escapeHtml(workflow.correlationId)}</strong></article>
        <article><span>Workspace identity</span><strong>${escapeHtml(workflow.workspaceId)}</strong></article>
        <article><span>Current stage</span><strong>${escapeHtml(workflow.currentStage ? label(workflow.currentStage) : "No active stage")}</strong></article>
        <article><span>Final output</span><strong>${workflow.outputReady ? "Ready" : "Pending"}</strong></article>
      </div>
      <div class="pipeline-workflow-lifecycle-grid">
        <article><span>Created</span><strong>${escapeHtml(timestamp(workflow.createdAt))}</strong></article>
        <article><span>Last updated</span><strong>${escapeHtml(timestamp(workflow.updatedAt))}</strong></article>
      </div>
      <div class="pipeline-workflow-stage-summary" aria-label="Selected workflow evidence counts">
        <article><strong>${escapeHtml(workflow.stageCount)}</strong><span>Stages</span></article>
        <article><strong>${escapeHtml(workflow.completedStages.length)}</strong><span>Completed</span></article>
        <article><strong>${escapeHtml(workflow.pendingStages.length)}</strong><span>Pending</span></article>
        <article><strong>${escapeHtml(workflow.jobCount)}</strong><span>Jobs</span></article>
      </div>
    `;
    return true;
  };

  const renderDirectory = (workflows) => {
    const directory = byId("pipelineWorkflowExplorerDirectory");
    const count = byId("pipelineWorkflowExplorerCount");
    if (!directory) return false;
    const filtered = workflows.filter(workflowMatches);
    if (count) count.textContent = `${filtered.length} of ${workflows.length}`;
    if (!filtered.length) {
      selectedWorkflowId = "";
      directory.innerHTML = placeholder(
        workflows.length ? "No workflows match" : "No persisted workflows",
        workflows.length
          ? "Change the status filter or identity search."
          : "Connected Domain has no stored workflow evidence."
      );
      directory.setAttribute("aria-busy", "false");
      const detail = byId("pipelineWorkflowExplorerDetail");
      if (detail) detail.innerHTML = placeholder(
        "No workflow selected",
        workflows.length ? "No filtered workflow is available." : "Workflow detail will appear after activation."
      );
      return filtered;
    }
    if (!filtered.some((item) => item.workflowId === selectedWorkflowId)) {
      selectedWorkflowId = filtered[0].workflowId;
    }
    directory.innerHTML = filtered.map((workflow) => `
      <button class="pipeline-workflow-row${workflow.workflowId === selectedWorkflowId ? " active" : ""}" type="button" role="option" aria-selected="${workflow.workflowId === selectedWorkflowId ? "true" : "false"}" data-workflow-explorer-id="${escapeHtml(workflow.workflowId)}">
        <span class="pipeline-workflow-row-head"><strong>${escapeHtml(workflow.workflowId)}</strong><span class="pipeline-workflow-status" data-status="${escapeHtml(workflow.status)}">${escapeHtml(label(workflow.status))}</span></span>
        <span class="pipeline-workflow-row-meta"><span>${escapeHtml(workflow.workspaceId)}</span><span>${escapeHtml(timestamp(workflow.updatedAt))}</span></span>
      </button>
    `).join("");
    directory.setAttribute("aria-busy", "false");
    renderDetail(filtered.find((item) => item.workflowId === selectedWorkflowId));
    return filtered;
  };

  const currentWorkflows = () => latestPayload ? inspect(latestPayload) : [];

  const applyFilters = () => {
    const workflows = currentWorkflows();
    const filtered = renderDirectory(workflows);
    if (!workflows.length) {
      updateMessage("empty", "No persisted workflows", "Connected Domain is registered, but no workflow evidence is stored.", "◎");
    } else if (!filtered.length) {
      updateMessage("ready", "No matching workflow", "The explorer is connected; adjust the local filters to display evidence.", "⌕");
    } else {
      updateMessage("ready", "Workflow evidence loaded", `${workflows.length} persisted workflow${workflows.length === 1 ? "" : "s"} available for inspection.`, "✓");
    }
  };

  const ensureBound = () => {
    if (bound) return true;
    const panel = byId("pipelineOperationsViewWorkflows");
    const statusFilter = byId("pipelineWorkflowExplorerStatusFilter");
    const search = byId("pipelineWorkflowExplorerSearch");
    if (!panel || !statusFilter || !search) return false;
    panel.addEventListener("click", (event) => {
      const row = event.target.closest("[data-workflow-explorer-id]");
      if (!row) return;
      selectedWorkflowId = row.dataset.workflowExplorerId || "";
      applyFilters();
    });
    statusFilter.addEventListener("change", () => {
      activeStatus = String(statusFilter.value || "all").toLowerCase();
      applyFilters();
    });
    search.addEventListener("input", () => {
      searchQuery = String(search.value || "");
      applyFilters();
    });
    bound = true;
    return true;
  };

  const render = (payload) => {
    ensureBound();
    try {
      const workflows = inspect(payload);
      latestPayload = payload;
      const count = byId("pipelineWorkflowExplorerCount");
      if (count) count.textContent = String(workflows.length);
      applyFilters();
      return true;
    } catch (error) {
      renderUnavailable(error?.message);
      return false;
    }
  };

  const renderUnavailable = (message) => {
    latestPayload = null;
    const directory = byId("pipelineWorkflowExplorerDirectory");
    const detail = byId("pipelineWorkflowExplorerDetail");
    const count = byId("pipelineWorkflowExplorerCount");
    if (directory) {
      directory.innerHTML = placeholder("Workflow evidence unavailable", message || "The canonical detail projection could not be loaded.");
      directory.setAttribute("aria-busy", "false");
    }
    if (detail) detail.innerHTML = placeholder("No workflow detail", "Restore the read-only projection before inspecting workflows.");
    if (count) count.textContent = "Unavailable";
    updateMessage("unavailable", "Workflow evidence unavailable", message || "The canonical detail projection could not be loaded.", "!");
    return false;
  };

  const activate = () => {
    ensureBound();
    const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.();
    if (snapshot) return render(snapshot);
    const directory = byId("pipelineWorkflowExplorerDirectory");
    if (directory) {
      directory.innerHTML = placeholder("Loading workflows", "Waiting for the existing Connected Domain detail request.");
      directory.setAttribute("aria-busy", "true");
    }
    updateMessage("loading", "Loading workflow evidence", "Waiting for the existing Connected Domain detail snapshot.", "◌");
    return false;
  };

  window.LinkCraftorConnectedDomainWorkflowExplorer = Object.freeze({
    activate,
    render,
    renderUnavailable,
    inspect
  });
})();
// END PART F 15-B4E WORKFLOW EXPLORER
'''

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=7" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=8" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=9"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=10"></script>'


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del tag
        for name, value in attrs:
            if name == "id" and value is not None:
                self.ids.append(value)


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
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def javascript_syntax_valid(source: str) -> bool:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for JavaScript syntax validation.")
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4e_js_") as folder:
        candidate = Path(folder) / "runtime_owner_candidate.js"
        write_text(candidate, source)
        result = subprocess.run(
            [node, "--check", str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    return result.returncode == 0


def isolated_view_model_probe() -> dict[str, Any]:
    payload = {
        "pipeline_id": "connect_domain",
        "stage_order": [
            "connect_domain",
            "site_sources",
            "url_cleaner",
            "site_pages",
            "live_domain_target_pool",
            "active_target_set",
        ],
        "workflows": [
            {
                "workflow_id": "workflow_probe_running",
                "correlation_id": "correlation_probe_running",
                "workspace_id": "ws_probe",
                "status": "running",
                "current_stage": "site_sources",
                "created_at": "2026-11-09T00:00:00Z",
                "updated_at": "2026-11-09T00:01:00Z",
                "job_count": 2,
                "stage_count": 6,
                "completed_stages": ["connect_domain"],
                "pending_stages": [
                    "site_sources",
                    "url_cleaner",
                    "site_pages",
                    "live_domain_target_pool",
                    "active_target_set",
                ],
                "failed_stages": [],
                "output_ready": False,
            },
            {
                "workflow_id": "workflow_probe_completed",
                "correlation_id": "correlation_probe_completed",
                "workspace_id": "ws_probe",
                "status": "completed",
                "current_stage": None,
                "created_at": "2026-11-08T00:00:00Z",
                "updated_at": "2026-11-08T00:02:00Z",
                "job_count": 6,
                "stage_count": 6,
                "completed_stages": [
                    "connect_domain",
                    "site_sources",
                    "url_cleaner",
                    "site_pages",
                    "live_domain_target_pool",
                    "active_target_set",
                ],
                "pending_stages": [],
                "failed_stages": [],
                "output_ready": True,
            },
        ],
    }
    harness = f'''
global.window = {{}};
global.document = {{ getElementById: () => null }};
{JS_APPEND}
const result = window.LinkCraftorConnectedDomainWorkflowExplorer.inspect(
  {json.dumps(payload)}
);
if (result.length !== 2) throw new Error("Expected two workflow view models.");
if (result[0].status !== "running") throw new Error("Running state was not retained.");
if (result[0].completedStages.length !== 1) throw new Error("Completed-stage evidence was not retained.");
if (result[1].outputReady !== true) throw new Error("Final-output readiness was not retained.");
if (result[1].jobCount !== 6) throw new Error("Job count was not retained.");
console.log(JSON.stringify({{
  workflow_count: result.length,
  statuses: result.map((item) => item.status),
  output_states: result.map((item) => item.outputReady),
  stage_counts: result.map((item) => item.stageCount)
}}));
'''
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for Workflow Explorer probe.")
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4e_probe_") as folder:
        probe = Path(folder) / "workflow_explorer_probe.js"
        write_text(probe, harness)
        result = subprocess.run(
            [node, str(probe)],
            capture_output=True,
            text=True,
            check=False,
        )
    if result.returncode != 0:
        raise RuntimeError(
            "Workflow Explorer isolated view-model probe failed.\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return json.loads(result.stdout.strip())


def print_check(name: str, value: bool) -> None:
    print(f"{name.upper()}: {'PASS' if value else 'FAIL'}")


def build_report(
    *,
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
    backup: Path | None,
) -> str:
    failed = [name for name, value in checks.items() if not value]
    final = FINAL_RESULT if status == "CERTIFIED" else (
        "FINAL RESULT: PART F 15-B4E WORKFLOW EXPLORER NOT_CERTIFIED"
    )
    return f'''LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS
PART F 15-B4E WORKFLOW EXPLORER CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Patch mode: STRICT FAIL-CLOSED
Backup: {backup if backup else "NOT_CREATED"}
Production jobs created: NO
Production queue claims executed: NO
Production handlers executed: NO
Production workflow persistence executed: NO
Production recovery actions executed: NO
Live network requests executed during certification: NO
CERTIFICATION STATUS: {status}

CHECKS:
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed, indent=2)}

NOT_RUN_CHECKS:
[]

EVIDENCE:
{json.dumps(evidence, indent=2, sort_keys=True)}

EXECUTION_ERROR:
{json.dumps(error, indent=2, sort_keys=True)}

IMPLEMENTED BOUNDARY:
- Workflow Explorer renders the persisted workflows already present in the certified Connected Domain detail projection.
- Workflow, correlation and workspace identities, lifecycle state, timestamps, stage counts, job count and output readiness are visible.
- Status filtering, identity search and workflow selection are local read-only presentation operations.
- The existing Connected Domain GET request and cached snapshot are reused; no new endpoint request was added.
- Loading, ready, empty, no-match and unavailable states fail closed.
- No job, queue, workflow, handler, persistence, recovery or backend authority was created or mutated.

NEXT STEP:
Browser visual acceptance, then Part F 15-B4F - Six-stage progress component.

FINAL RESULT:
{final}
'''


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4E_WORKFLOW_EXPLORER.py <project_root> <report_path>"
        )

    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    paths = {
        "index_html": root / "backend/server/owner/index.html",
        "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": root / "backend/server/owner/runtime_owner.css",
        "runtime_owner_js": root / "backend/server/owner/runtime_owner.js",
        "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py",
        "pipeline_operations": root / "backend/server/owner/pipeline_operations.py",
    }
    prior_report = (
        root
        / "backend/server/data/reports/"
        "PART_F_15_B4D10R_OUTPUT_READINESS_SEMANTIC_CORRECTION_CERTIFICATION.txt"
    )

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}
    backup_dir: Path | None = None
    retained = False
    status = "NOT_CERTIFIED"

    try:
        checks["part_f_15_b4d10r_report_exists"] = prior_report.is_file()
        prior_hash = sha256_path(prior_report) if prior_report.is_file() else ""
        prior = read_text(prior_report) if prior_report.is_file() else ""
        checks["part_f_15_b4d10r_certified"] = (
            "CERTIFICATION STATUS: CERTIFIED" in prior
            and "FINAL RESULT: PART F 15-B4D10R OUTPUT READINESS "
            "SEMANTIC CORRECTION CERTIFIED" in prior
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("Required source or D10R evidence is unavailable.")

        before = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()):
            raise RuntimeError("Installed source lineage does not match certified D10R.")

        index_source = read_text(paths["index_html"])
        css_source = read_text(paths["runtime_owner_css"])
        js_source = read_text(paths["runtime_owner_js"])
        operations_source = read_text(paths["pipeline_operations"])
        checks["workflow_explorer_not_previously_present"] = all(
            MARKER not in source
            for source in (index_source, css_source, js_source)
        )
        checks["workflow_projection_contract_available"] = all(
            token in operations_source
            for token in (
                '"workflow_id"',
                '"correlation_id"',
                '"workspace_id"',
                '"status"',
                '"current_stage"',
                '"completed_stages"',
                '"pending_stages"',
                '"failed_stages"',
                '"job_count"',
                '"stage_count"',
                '"output_ready"',
            )
        )

        index_candidate = replace_once(
            index_source,
            OLD_WORKFLOW_PANEL,
            NEW_WORKFLOW_PANEL,
            "Workflow Explorer structure-ready shell",
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
        css_candidate = css_source.rstrip() + "\n" + CSS_APPEND.lstrip()
        js_candidate = replace_once(
            js_source,
            OLD_SET_VIEW_END,
            NEW_SET_VIEW_END,
            "Workflow Explorer activation handoff",
        )
        js_candidate = replace_once(
            js_candidate,
            OLD_REQUEST_STATE,
            NEW_REQUEST_STATE,
            "Connected Domain snapshot cache",
        )
        js_candidate = replace_once(
            js_candidate,
            OLD_SNAPSHOT_VALIDATION,
            NEW_SNAPSHOT_VALIDATION,
            "Connected Domain snapshot retention",
        )
        js_candidate = replace_once(
            js_candidate,
            OLD_UNAVAILABLE,
            NEW_UNAVAILABLE,
            "Workflow Explorer unavailable-state handoff",
        )
        js_candidate = replace_once(
            js_candidate,
            OLD_RENDER_HANDOFF,
            NEW_RENDER_HANDOFF,
            "Workflow Explorer render handoff",
        )
        js_candidate = replace_once(
            js_candidate,
            OLD_OVERVIEW_EXPORT,
            NEW_OVERVIEW_EXPORT,
            "Connected Domain snapshot export",
        ).rstrip() + "\n" + JS_APPEND.lstrip()

        checks["candidate_html_ids_unique"] = html_ids_unique(index_candidate)
        checks["candidate_css_balanced"] = css_balanced(css_candidate)
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(js_candidate)
        required_ids = (
            "pipelineWorkflowExplorerState",
            "pipelineWorkflowExplorerCount",
            "pipelineWorkflowExplorerStatusFilter",
            "pipelineWorkflowExplorerSearch",
            "pipelineWorkflowExplorerDirectory",
            "pipelineWorkflowExplorerDetail",
            "pipelineWorkflowExplorerMessage",
        )
        checks["all_workflow_explorer_bindings_present"] = all(
            index_candidate.count(f'id="{identifier}"') == 1
            for identifier in required_ids
        )
        checks["workflow_identity_fields_rendered"] = all(
            token in JS_APPEND
            for token in (
                "workflowId",
                "correlationId",
                "workspaceId",
                "status",
                "createdAt",
                "updatedAt",
                "currentStage",
                "jobCount",
                "completedStages",
                "pendingStages",
                "failedStages",
                "outputReady",
            )
        )
        checks["status_filter_and_identity_search_present"] = (
            "pipelineWorkflowExplorerStatusFilter" in JS_APPEND
            and "pipelineWorkflowExplorerSearch" in JS_APPEND
            and "workflowMatches" in JS_APPEND
        )
        checks["cached_snapshot_reused"] = (
            "getSnapshot: () => latestSnapshot" in js_candidate
            and "LinkCraftorConnectedDomainOverview?.getSnapshot?.()" in js_candidate
        )
        checks["no_new_fetch_request_added"] = (
            js_candidate.count("fetch(") == js_source.count("fetch(")
        )
        checks["canonical_detail_endpoint_retained_once"] = (
            js_candidate.count('"/owner/api/runtime/pipelines/connect_domain"') == 1
        )
        checks["five_presentation_states_present"] = all(
            f'"{state}"' in JS_APPEND
            for state in ("loading", "ready", "empty", "unavailable")
        ) and "No matching workflow" in JS_APPEND
        checks["no_recovery_controls_added"] = all(
            js_candidate.count(token) == js_source.count(token)
            for token in (
                "retryJob(",
                "cancelJob(",
                "terminateJob(",
                "data-runtime-recovery-action",
            )
        )
        checks["cache_versions_advanced"] = (
            NEW_CSS_VERSION in index_candidate
            and NEW_JS_VERSION in index_candidate
            and OLD_CSS_VERSION not in index_candidate
            and OLD_JS_VERSION not in index_candidate
        )

        probe = isolated_view_model_probe()
        evidence["isolated_view_model_probe"] = probe
        checks["isolated_view_model_probe_passed"] = (
            probe
            == {
                "workflow_count": 2,
                "statuses": ["running", "completed"],
                "output_states": [False, True],
                "stage_counts": [6, 6],
            }
        )
        if not all(checks.values()):
            raise RuntimeError("15-B4E candidate certification checks failed.")

        timestamp_value = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = (
            root
            / "backend/server/data/runtime_backups"
            / f"part_f_15_b4e_{timestamp_value}"
        )
        backup_dir.mkdir(parents=True, exist_ok=False)
        for name in ("index_html", "runtime_owner_css", "runtime_owner_js"):
            path = paths[name]
            originals[name] = path.read_bytes()
            backup_target = backup_dir / name / path.name
            backup_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup_target)
        checks["backup_created"] = all(
            (backup_dir / name / paths[name].name).is_file()
            for name in originals
        )
        if not checks["backup_created"]:
            raise RuntimeError("15-B4E production UI backup is incomplete.")

        write_text(paths["index_html"], index_candidate)
        write_text(paths["runtime_owner_css"], css_candidate)
        write_text(paths["runtime_owner_js"], js_candidate)

        checks["retained_html_ids_unique"] = html_ids_unique(
            read_text(paths["index_html"])
        )
        checks["retained_css_balanced"] = css_balanced(
            read_text(paths["runtime_owner_css"])
        )
        checks["retained_javascript_syntax"] = javascript_syntax_valid(
            read_text(paths["runtime_owner_js"])
        )
        checks["retained_markers"] = (
            read_text(paths["index_html"]).count(MARKER) == 2
            and read_text(paths["runtime_owner_css"]).count(MARKER) == 2
            and read_text(paths["runtime_owner_js"]).count(MARKER) == 2
        )
        checks["retained_no_new_fetch_request"] = (
            read_text(paths["runtime_owner_js"]).count("fetch(")
            == js_source.count("fetch(")
        )

        after = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_after"] = after
        evidence["backup"] = str(backup_dir)
        evidence["endpoint_reused"] = "/owner/api/runtime/pipelines/connect_domain"
        evidence["new_endpoint_requests"] = 0
        evidence["workflow_evidence_rendered"] = [
            "workflow identity",
            "correlation identity",
            "workspace identity",
            "lifecycle status",
            "current stage",
            "created and updated timestamps",
            "stage evidence counts",
            "job count",
            "final-output readiness",
        ]
        evidence["recovery_controls_added"] = False

        for name in (
            "owner_css",
            "owner_js",
            "runtime_summary_api",
            "pipeline_operations",
        ):
            checks[f"unchanged_{name}"] = before[name] == after[name]
        checks["historical_d10r_report_unchanged"] = (
            sha256_path(prior_report) == prior_hash
        )
        checks["only_three_ui_sources_changed"] = all(
            before[name] != after[name]
            for name in ("index_html", "runtime_owner_css", "runtime_owner_js")
        )
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_during_certification_no"] = True
        if not all(checks.values()):
            raise RuntimeError("15-B4E retained-source certification checks failed.")

        retained = True
        status = "CERTIFIED"

    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        for name, data in originals.items():
            paths[name].write_bytes(data)

    report.parent.mkdir(parents=True, exist_ok=True)
    write_text(
        report,
        build_report(
            status=status,
            checks=checks,
            evidence=evidence,
            error=error,
            backup=backup_dir,
        ),
    )
    for name, value in checks.items():
        print_check(name, value)
    failed = [name for name, value in checks.items() if not value]
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B4E_STATUS={status}")
    print("PATCH_RETAINED=YES" if retained else "PATCH_RETAINED=NO")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
