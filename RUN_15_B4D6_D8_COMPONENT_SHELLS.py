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


FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B4D6 THROUGH 15-B4D8 "
    "COMPONENT SHELLS NAVIGATION AND STATES CERTIFIED"
)
MARKER = "PART F 15-B4D6-D8 COMPONENT SHELLS NAVIGATION AND STATES"

EXPECTED_HASHES = {
    "index_html": "c00afec08056319f3dc0057331a05e70e3da6c90b9b545381e564e86f0c9121a",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "255cf8ed09436bdc69816cb37cc64be63d2fc99a8a59bd2da6b4bc5b0637f1de",
    "runtime_owner_js": "f0e3f5cf9346cd9cf343ffd86e051901937d4b64e5db6998fc39d4ebb44652c2",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "570bfc61676fd15b5a1cacc6ed74130eac1d98dc41f327606019df59d55f342a",
}

OLD_SIDEBAR_DESTINATIONS = r'''                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="overview" disabled aria-disabled="true">Overview</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="workflows" disabled aria-disabled="true">Workflows</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="stage_progress" disabled aria-disabled="true">Stage Progress</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="jobs_attempts" disabled aria-disabled="true">Jobs &amp; Attempts</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="dependencies_handoffs" disabled aria-disabled="true">Dependencies &amp; Handoffs</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="events_timeline" disabled aria-disabled="true">Events Timeline</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="failures_attention" disabled aria-disabled="true">Failures &amp; Attention</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="output_readiness" disabled aria-disabled="true">Output Readiness</button>'''

NEW_SIDEBAR_DESTINATIONS = r'''                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-id="connect_domain" data-runtime-pipeline-view="overview">Overview</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-id="connect_domain" data-runtime-pipeline-view="workflows">Workflows</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-id="connect_domain" data-runtime-pipeline-view="stage_progress">Stage Progress</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-id="connect_domain" data-runtime-pipeline-view="jobs_attempts">Jobs &amp; Attempts</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-id="connect_domain" data-runtime-pipeline-view="dependencies_handoffs">Dependencies &amp; Handoffs</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-id="connect_domain" data-runtime-pipeline-view="events_timeline">Events Timeline</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-id="connect_domain" data-runtime-pipeline-view="failures_attention">Failures &amp; Attention</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-id="connect_domain" data-runtime-pipeline-view="output_readiness">Output Readiness</button>'''

OLD_VIEW_NAV = r'''            <nav
              class="pipeline-operations-view-nav"
              id="pipelineOperationsViewNav"
              aria-label="Pipeline operation views"
            >
              <button type="button" data-pipeline-operations-view="overview" disabled>Overview</button>
              <button type="button" data-pipeline-operations-view="workflows" disabled>Workflows</button>
              <button type="button" data-pipeline-operations-view="stage_progress" disabled>Stage Progress</button>
              <button type="button" data-pipeline-operations-view="jobs_attempts" disabled>Jobs &amp; Attempts</button>
              <button type="button" data-pipeline-operations-view="dependencies_handoffs" disabled>Dependencies &amp; Handoffs</button>
              <button type="button" data-pipeline-operations-view="events_timeline" disabled>Events Timeline</button>
              <button type="button" data-pipeline-operations-view="failures" disabled>Failures</button>
              <button type="button" data-pipeline-operations-view="output_readiness" disabled>Output Readiness</button>
            </nav>'''

NEW_VIEW_NAV = r'''            <nav
              class="pipeline-operations-view-nav"
              id="pipelineOperationsViewNav"
              aria-label="Pipeline operation views"
              role="tablist"
            >
              <button type="button" role="tab" aria-selected="true" data-pipeline-operations-view="overview">Overview</button>
              <button type="button" role="tab" aria-selected="false" data-pipeline-operations-view="workflows">Workflows</button>
              <button type="button" role="tab" aria-selected="false" data-pipeline-operations-view="stage_progress">Stage Progress</button>
              <button type="button" role="tab" aria-selected="false" data-pipeline-operations-view="jobs_attempts">Jobs &amp; Attempts</button>
              <button type="button" role="tab" aria-selected="false" data-pipeline-operations-view="dependencies_handoffs">Dependencies &amp; Handoffs</button>
              <button type="button" role="tab" aria-selected="false" data-pipeline-operations-view="events_timeline">Events Timeline</button>
              <button type="button" role="tab" aria-selected="false" data-pipeline-operations-view="failures">Failures</button>
              <button type="button" role="tab" aria-selected="false" data-pipeline-operations-view="output_readiness">Output Readiness</button>
            </nav>'''

OLD_VIEW_MOUNT = r'''            <div
              class="pipeline-operations-view-mount"
              id="pipelineOperationsViewMount"
              aria-live="polite"
            >
              <div
                class="pipeline-operations-structural-placeholder"
                data-pipeline-operations-placeholder="selected_pipeline"
              >
                Monitoring components will be connected in 15-B4C through 15-B4K.
              </div>
            </div>'''

NEW_VIEW_MOUNT = r'''            <!-- BEGIN PART F 15-B4D6-D8 COMPONENT SHELLS NAVIGATION AND STATES -->
            <div
              class="pipeline-operations-view-mount pipeline-monitoring-mount"
              id="pipelineOperationsViewMount"
              data-pipeline-component-shell-version="15-b4d8"
              aria-live="polite"
            >
              <section class="pipeline-monitoring-panel active" id="pipelineOperationsViewOverview" data-pipeline-operations-view-panel="overview" data-component-state="structure_ready" role="tabpanel">
                <header class="pipeline-monitoring-panel-head">
                  <div><span>Connected Domain</span><h5>Operations Overview</h5><p>Pipeline identity, health, workflow activity, and readiness summary.</p></div>
                  <strong>Structure ready</strong>
                </header>
                <div class="pipeline-monitoring-summary-grid">
                  <article><span>Pipeline health</span><strong>Awaiting detail wiring</strong></article>
                  <article><span>Active workflow</span><strong>Awaiting selection</strong></article>
                  <article><span>Output readiness</span><strong>Awaiting evidence</strong></article>
                </div>
                <div class="pipeline-component-state" data-state="empty"><span aria-hidden="true">◎</span><div><strong>Select Connected Domain</strong><p>The overview shell is ready for certified pipeline-detail evidence.</p></div></div>
              </section>

              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewWorkflows" data-pipeline-operations-view-panel="workflows" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Workflow Explorer</span><h5>Connected Domain Workflows</h5><p>Browse workflow identity, lifecycle state, correlation, and timestamps.</p></div><strong>Structure ready</strong></header>
                <div class="pipeline-workflow-explorer-shell">
                  <div class="pipeline-component-toolbar"><span>Workflow list</span><span>Status filters</span><span>Correlation search</span></div>
                  <div class="pipeline-workflow-explorer-grid"><div class="pipeline-shell-region"><strong>Workflow directory</strong><p>Workflow rows will appear here.</p></div><div class="pipeline-shell-region"><strong>Workflow detail</strong><p>Select a workflow to inspect its stages and evidence.</p></div></div>
                </div>
              </section>

              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewStageProgress" data-pipeline-operations-view-panel="stage_progress" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Six-stage execution</span><h5>Stage Progress</h5><p>Canonical stage order and per-stage runtime state.</p></div><strong>Structure ready</strong></header>
                <ol class="pipeline-stage-progress-shell">
                  <li><span>01</span><div><strong>Connect Domain</strong><small>Awaiting workflow</small></div></li>
                  <li><span>02</span><div><strong>Site Sources</strong><small>Awaiting predecessor</small></div></li>
                  <li><span>03</span><div><strong>URL Cleaner</strong><small>Awaiting predecessor</small></div></li>
                  <li><span>04</span><div><strong>Site Pages</strong><small>Awaiting predecessor</small></div></li>
                  <li><span>05</span><div><strong>Live Domain Target Pool</strong><small>Awaiting predecessor</small></div></li>
                  <li><span>06</span><div><strong>Active Target Set</strong><small>Awaiting predecessor</small></div></li>
                </ol>
              </section>

              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewJobsAttempts" data-pipeline-operations-view-panel="jobs_attempts" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Runtime execution</span><h5>Jobs &amp; Attempts</h5><p>Universal Jobs, attempts, queue state, worker ownership, and terminal results.</p></div><strong>Structure ready</strong></header>
                <div class="pipeline-table-shell"><div><span>Stage / Job</span><span>Status</span><span>Attempt</span><span>Worker</span><span>Updated</span></div><p>No workflow selected. Job evidence will appear here.</p></div>
              </section>

              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewDependenciesHandoffs" data-pipeline-operations-view-panel="dependencies_handoffs" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Execution contract</span><h5>Dependencies &amp; Handoffs</h5><p>Dependency gates and result-to-payload hydration between stages.</p></div><strong>Structure ready</strong></header>
                <div class="pipeline-handoff-chain-shell"><div>Connect Domain <b>→</b> Site Sources</div><div>Site Sources <b>→</b> URL Cleaner</div><div>URL Cleaner <b>→</b> Site Pages</div><div>Site Pages <b>→</b> Live Domain Target Pool</div><div>Live Domain Target Pool <b>→</b> Active Target Set</div></div>
              </section>

              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewEventsTimeline" data-pipeline-operations-view-panel="events_timeline" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Runtime evidence</span><h5>Events Timeline</h5><p>Chronological workflow, job, queue, handler, and lifecycle evidence.</p></div><strong>Structure ready</strong></header>
                <div class="pipeline-events-shell"><i></i><div><strong>Timeline waiting for workflow selection</strong><p>Canonical events will be ordered by recorded occurrence time.</p></div></div>
              </section>

              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewFailures" data-pipeline-operations-view-panel="failures" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Owner attention</span><h5>Failures &amp; Attention</h5><p>Failed jobs, terminal evidence, retries, and items requiring review.</p></div><strong>Structure ready</strong></header>
                <div class="pipeline-component-state" data-state="empty"><span aria-hidden="true">✓</span><div><strong>No selected failure context</strong><p>Failure evidence and governed recovery eligibility will appear here.</p></div></div>
              </section>

              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewOutputReadiness" data-pipeline-operations-view-panel="output_readiness" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Final pipeline output</span><h5>Output Readiness</h5><p>Final-stage completion, evidence integrity, and Active Target Set availability.</p></div><strong>Structure ready</strong></header>
                <div class="pipeline-output-readiness-shell"><article><span>Final stage</span><strong>Active Target Set</strong></article><article><span>Completion evidence</span><strong>Awaiting workflow</strong></article><article><span>Output state</span><strong>Not evaluated</strong></article></div>
              </section>
            </div>
            <!-- END PART F 15-B4D6-D8 COMPONENT SHELLS NAVIGATION AND STATES -->'''

CSS_APPEND = r'''

/* BEGIN PART F 15-B4D6-D8 COMPONENT SHELLS NAVIGATION AND STATES */
#runtimePage .pipeline-monitoring-mount {
  display: block;
  min-height: 330px;
}

#runtimePage .pipeline-monitoring-panel[hidden] {
  display: none !important;
}

#runtimePage .pipeline-monitoring-panel {
  min-height: 300px;
  animation: pipelinePanelIn 150ms ease-out;
}

@keyframes pipelinePanelIn {
  from { opacity: 0; transform: translateY(3px); }
  to { opacity: 1; transform: translateY(0); }
}

#runtimePage .pipeline-monitoring-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.13);
}

#runtimePage .pipeline-monitoring-panel-head span,
#runtimePage .pipeline-monitoring-panel-head h5,
#runtimePage .pipeline-monitoring-panel-head p {
  display: block;
  margin: 0;
}

#runtimePage .pipeline-monitoring-panel-head span {
  color: #67e8f9;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

#runtimePage .pipeline-monitoring-panel-head h5 {
  margin-top: 4px;
  color: #f0fbff;
  font-size: 16px;
}

#runtimePage .pipeline-monitoring-panel-head p {
  margin-top: 4px;
  color: #8399b5;
  font-size: 11px;
}

#runtimePage .pipeline-monitoring-panel-head > strong {
  flex: 0 0 auto;
  padding: 5px 8px;
  border: 1px solid rgba(34, 211, 238, 0.24);
  border-radius: 999px;
  background: rgba(34, 211, 238, 0.07);
  color: #a5f3fc;
  font-size: 9px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

#runtimePage .pipeline-monitoring-summary-grid,
#runtimePage .pipeline-output-readiness-shell {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 12px;
}

#runtimePage .pipeline-monitoring-summary-grid article,
#runtimePage .pipeline-output-readiness-shell article {
  padding: 11px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.025);
}

#runtimePage .pipeline-monitoring-summary-grid span,
#runtimePage .pipeline-monitoring-summary-grid strong,
#runtimePage .pipeline-output-readiness-shell span,
#runtimePage .pipeline-output-readiness-shell strong {
  display: block;
}

#runtimePage .pipeline-monitoring-summary-grid span,
#runtimePage .pipeline-output-readiness-shell span {
  color: #7288a5;
  font-size: 9px;
  text-transform: uppercase;
}

#runtimePage .pipeline-monitoring-summary-grid strong,
#runtimePage .pipeline-output-readiness-shell strong {
  margin-top: 5px;
  color: #dceefa;
  font-size: 11px;
  overflow-wrap: anywhere;
}

#runtimePage .pipeline-component-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 145px;
  margin-top: 12px;
  padding: 20px;
  border: 1px dashed rgba(56, 189, 248, 0.2);
  border-radius: 10px;
  background: radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.07), transparent 66%);
  color: #8399b5;
  text-align: left;
}

#runtimePage .pipeline-component-state > span {
  display: grid;
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  place-items: center;
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 50%;
  color: #67e8f9;
  font-size: 17px;
}

#runtimePage .pipeline-component-state strong,
#runtimePage .pipeline-component-state p {
  display: block;
  margin: 0;
}

#runtimePage .pipeline-component-state strong { color: #dceefa; font-size: 12px; }
#runtimePage .pipeline-component-state p { margin-top: 4px; font-size: 10px; }

#runtimePage .pipeline-component-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}

#runtimePage .pipeline-component-toolbar span {
  padding: 6px 8px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 7px;
  color: #8298b3;
  font-size: 9px;
}

#runtimePage .pipeline-workflow-explorer-grid {
  display: grid;
  grid-template-columns: minmax(180px, 0.4fr) minmax(0, 1fr);
  gap: 8px;
  margin-top: 8px;
}

#runtimePage .pipeline-shell-region {
  min-height: 155px;
  padding: 12px;
  border: 1px dashed rgba(148, 163, 184, 0.16);
  border-radius: 9px;
  color: #7f96b3;
  font-size: 10px;
}

#runtimePage .pipeline-shell-region strong { color: #d9ebf7; font-size: 11px; }

#runtimePage .pipeline-stage-progress-shell {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
}

#runtimePage .pipeline-stage-progress-shell li {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
  padding: 11px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.025);
}

#runtimePage .pipeline-stage-progress-shell li > span {
  display: grid;
  width: 27px;
  height: 27px;
  flex: 0 0 27px;
  place-items: center;
  border-radius: 8px;
  background: rgba(34, 211, 238, 0.09);
  color: #67e8f9;
  font-size: 9px;
  font-weight: 800;
}

#runtimePage .pipeline-stage-progress-shell strong,
#runtimePage .pipeline-stage-progress-shell small { display: block; }
#runtimePage .pipeline-stage-progress-shell strong { color: #dceefa; font-size: 10px; }
#runtimePage .pipeline-stage-progress-shell small { margin-top: 3px; color: #7187a3; font-size: 9px; }

#runtimePage .pipeline-table-shell { margin-top: 13px; border: 1px solid rgba(148, 163, 184, 0.12); border-radius: 9px; overflow: hidden; }
#runtimePage .pipeline-table-shell > div { display: grid; grid-template-columns: 1.5fr repeat(4, 0.75fr); gap: 8px; padding: 9px 11px; background: rgba(255, 255, 255, 0.035); color: #7890ad; font-size: 9px; text-transform: uppercase; }
#runtimePage .pipeline-table-shell > p { min-height: 145px; margin: 0; padding: 50px 12px; color: #7f96b3; font-size: 10px; text-align: center; }

#runtimePage .pipeline-handoff-chain-shell { display: grid; gap: 7px; margin-top: 13px; }
#runtimePage .pipeline-handoff-chain-shell > div { display: flex; justify-content: space-between; gap: 12px; padding: 10px 12px; border-left: 2px solid rgba(56, 189, 248, 0.45); border-radius: 7px; background: rgba(255, 255, 255, 0.025); color: #cfe3f2; font-size: 10px; }
#runtimePage .pipeline-handoff-chain-shell b { color: #67e8f9; }

#runtimePage .pipeline-events-shell { display: flex; gap: 12px; min-height: 180px; margin-top: 13px; padding: 17px; border: 1px dashed rgba(148, 163, 184, 0.16); border-radius: 9px; color: #7f96b3; }
#runtimePage .pipeline-events-shell i { width: 2px; align-self: stretch; background: linear-gradient(#22d3ee, transparent); }
#runtimePage .pipeline-events-shell strong { color: #dceefa; font-size: 11px; }
#runtimePage .pipeline-events-shell p { margin: 4px 0 0; font-size: 10px; }

#runtimePage .pipeline-operations-view-nav button:not(:disabled) { cursor: pointer; }
#runtimePage .pipeline-operations-view-nav button[aria-selected="true"] { border-color: rgba(34, 211, 238, 0.42); background: rgba(34, 211, 238, 0.12); color: #dffbff; }
#runtimePage .pipeline-operations-card[data-component-selectable="true"] { cursor: pointer; }
#runtimePage .pipeline-operations-card[data-component-selectable="true"]:focus-visible { outline: 2px solid #22d3ee; outline-offset: 2px; }

@media (max-width: 760px) {
  #runtimePage .pipeline-monitoring-summary-grid,
  #runtimePage .pipeline-output-readiness-shell,
  #runtimePage .pipeline-stage-progress-shell { grid-template-columns: 1fr; }
  #runtimePage .pipeline-workflow-explorer-grid { grid-template-columns: 1fr; }
  #runtimePage .pipeline-monitoring-panel-head { flex-direction: column; }
  #runtimePage .pipeline-table-shell > div { grid-template-columns: 1fr 0.7fr 0.7fr; }
  #runtimePage .pipeline-table-shell > div span:nth-child(n + 4) { display: none; }
}
/* END PART F 15-B4D6-D8 COMPONENT SHELLS NAVIGATION AND STATES */
'''

JS_APPEND = r'''

// BEGIN PART F 15-B4D6-D8 COMPONENT SHELLS NAVIGATION AND STATES
(() => {
  "use strict";

  const VIEW_ALIASES = Object.freeze({
    failures_attention: "failures"
  });

  const normalizeView = (view) =>
    VIEW_ALIASES[view] || view || "overview";

  const pipelineLabel = (pipelineId) => {
    if (pipelineId === "connect_domain") {
      return "Connected Domain";
    }

    return String(pipelineId || "")
      .split(/[_-]+/)
      .filter(Boolean)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ") || "Selected Pipeline";
  };

  const setSelectedPipeline = (pipelineId) => {
    const name = document.getElementById("pipelineOperationsSelectedPipeline");
    const summary = document.getElementById("pipelineOperationsSelectedPipelineSummary");
    const health = document.getElementById("pipelineOperationsSelectedPipelineHealth");
    const workspace = document.getElementById("pipelineOperationsWorkspace");
    const label = pipelineLabel(pipelineId);

    if (name) name.textContent = label;
    if (summary) {
      summary.textContent = pipelineId === "connect_domain"
        ? "Six-stage Connected Domain monitoring workspace."
        : "Universal monitoring shell for the selected registered pipeline.";
    }
    if (health) health.textContent = "Structure ready";
    if (workspace) workspace.dataset.selectedPipelineId = pipelineId;
    return true;
  };

  const setPipelineView = (requestedView) => {
    const view = normalizeView(requestedView);
    const mount = document.getElementById("pipelineOperationsViewMount");
    const nav = document.getElementById("pipelineOperationsViewNav");

    if (!mount || !nav) return false;

    let matched = false;
    mount.querySelectorAll("[data-pipeline-operations-view-panel]").forEach((panel) => {
      const active = panel.dataset.pipelineOperationsViewPanel === view;
      panel.hidden = !active;
      panel.classList.toggle("active", active);
      if (active) matched = true;
    });

    nav.querySelectorAll("[data-pipeline-operations-view]").forEach((button) => {
      const active = button.dataset.pipelineOperationsView === view;
      button.classList.toggle("active", active);
      button.setAttribute("aria-selected", active ? "true" : "false");
    });

    document.querySelectorAll("[data-runtime-pipeline-view]").forEach((button) => {
      const active = normalizeView(button.dataset.runtimePipelineView) === view;
      button.classList.toggle("active", active);
      if (active) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    });

    if (matched) mount.dataset.activePipelineView = view;
    return matched;
  };

  const openPipelineWorkspace = (pipelineId, view = "overview") => {
    window.LinkCraftorRuntimeOwner?.setActiveSection?.("pipeline_operations");
    setSelectedPipeline(pipelineId);
    setPipelineView(view);
    return true;
  };

  const decoratePipelineCards = () => {
    document.querySelectorAll(".pipeline-operations-card[data-pipeline-id]").forEach((card) => {
      card.tabIndex = 0;
      card.setAttribute("role", "button");
      card.setAttribute("data-component-selectable", "true");
      card.setAttribute("aria-label", `Open ${pipelineLabel(card.dataset.pipelineId)} operations`);
    });
  };

  const initializePipelineComponentShells = () => {
    const page = document.getElementById("runtimePage");
    const nav = document.getElementById("pipelineOperationsViewNav");
    const list = document.getElementById("pipelineOperationsPipelineList");

    if (!page || !nav || !list || page.dataset.pipelineComponentShellsBound === "true") {
      return false;
    }

    nav.addEventListener("click", (event) => {
      const button = event.target.closest("[data-pipeline-operations-view]");
      if (button) setPipelineView(button.dataset.pipelineOperationsView);
    });

    page.addEventListener("click", (event) => {
      const destination = event.target.closest("[data-runtime-pipeline-view]");
      if (destination) {
        openPipelineWorkspace(
          destination.dataset.runtimePipelineId || "connect_domain",
          destination.dataset.runtimePipelineView
        );
        return;
      }

      const card = event.target.closest(".pipeline-operations-card[data-pipeline-id]");
      if (card) openPipelineWorkspace(card.dataset.pipelineId, "overview");
    });

    list.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      const card = event.target.closest(".pipeline-operations-card[data-pipeline-id]");
      if (!card) return;
      event.preventDefault();
      openPipelineWorkspace(card.dataset.pipelineId, "overview");
    });

    new MutationObserver(decoratePipelineCards).observe(list, { childList: true, subtree: true });
    decoratePipelineCards();
    setPipelineView("overview");
    page.dataset.pipelineComponentShellsBound = "true";
    return true;
  };

  window.LinkCraftorPipelineComponentShells = Object.freeze({
    open: openPipelineWorkspace,
    selectPipeline: setSelectedPipeline,
    setView: setPipelineView
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializePipelineComponentShells, { once: true });
  } else {
    initializePipelineComponentShells();
  }
})();
// END PART F 15-B4D6-D8 COMPONENT SHELLS NAVIGATION AND STATES
'''


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        for name, value in attrs:
            if name == "id" and value is not None:
                self.ids.append(value)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label} anchor, found {count}.")
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
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4d6_d8_js_") as folder:
        candidate = Path(folder) / "runtime_owner_candidate.js"
        write_text(candidate, source)
        completed = subprocess.run(
            [node, "--check", str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    return completed.returncode == 0


def print_check(name: str, value: bool) -> None:
    print(f"{name.upper()}: {'PASS' if value else 'FAIL'}")


def build_report(
    *, status: str, checks: dict[str, bool], evidence: dict[str, Any],
    error: dict[str, Any], backup: Path | None,
) -> str:
    failed = [name for name, value in checks.items() if not value]
    final = FINAL_RESULT if status == "CERTIFIED" else (
        "FINAL RESULT: PART F 15-B4D6 THROUGH 15-B4D8 "
        "COMPONENT SHELLS NAVIGATION AND STATES NOT_CERTIFIED"
    )
    return f'''LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS
PART F 15-B4D6 THROUGH 15-B4D8 COMPONENT SHELLS NAVIGATION AND STATES CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Patch mode: STRICT FAIL-CLOSED
Backup: {backup if backup else "NOT_CREATED"}
Production jobs created: NO
Production queue claims executed: NO
Production handlers executed: NO
Production workflow persistence executed: NO
Production recovery actions executed: NO
Live network requests executed: NO
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
- 15-B4D6 installs static shells for all eight Connected Domain monitoring components.
- 15-B4D7 enables accessible UI-only navigation from the sidebar, pipeline cards and workspace tabs.
- 15-B4D8 supplies consistent structure-ready, empty and awaiting-evidence presentation states.
- Existing Runtime Summary and All Pipelines requests remain unchanged.
- No pipeline-detail request, recovery mutation or new backend authority was added.

NEXT STEP:
Part F 15-B4D9 - component-shell visual acceptance and wiring boundary closure.

FINAL RESULT:
{final}
'''


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4D6_D8_COMPONENT_SHELLS.py <project_root> <report_path>"
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
        root / "backend/server/data/reports/"
        "PART_F_15_B4D3_D5_RUNTIME_UI_REDESIGN_CERTIFICATION.txt"
    )

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}
    backup_dir: Path | None = None
    retained = False
    status = "NOT_CERTIFIED"

    try:
        checks["part_f_15_b4d3_d5_report_exists"] = prior_report.is_file()
        checks["part_f_15_b4d3_d5_certified"] = (
            checks["part_f_15_b4d3_d5_report_exists"]
            and "CERTIFICATION STATUS: CERTIFIED" in read_text(prior_report)
            and "FINAL RESULT: PART F 15-B4D3 THROUGH 15-B4D5 RUNTIME UI REDESIGN CERTIFIED"
            in read_text(prior_report)
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("Required source or 15-B4D3-D5 evidence is unavailable.")

        before = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()):
            raise RuntimeError("Installed UI source lineage does not match 15-B4D3-D5.")

        html_source = read_text(paths["index_html"])
        css_source = read_text(paths["runtime_owner_css"])
        js_source = read_text(paths["runtime_owner_js"])
        checks["combined_boundary_not_previously_present"] = (
            MARKER not in html_source and MARKER not in css_source and MARKER not in js_source
        )

        html_candidate = replace_once(
            html_source, OLD_SIDEBAR_DESTINATIONS, NEW_SIDEBAR_DESTINATIONS,
            "Connected Domain sidebar destinations",
        )
        html_candidate = replace_once(
            html_candidate, OLD_VIEW_NAV, NEW_VIEW_NAV,
            "Pipeline Operations component navigation",
        )
        html_candidate = replace_once(
            html_candidate, OLD_VIEW_MOUNT, NEW_VIEW_MOUNT,
            "Pipeline Operations component mount",
        )
        html_candidate = replace_once(
            html_candidate,
            '<link rel="stylesheet" href="/owner/runtime_owner.css?v=5" />',
            '<link rel="stylesheet" href="/owner/runtime_owner.css?v=6" />',
            "Runtime stylesheet cache version",
        )
        html_candidate = replace_once(
            html_candidate,
            '<script src="/owner/runtime_owner.js?v=5"></script>',
            '<script src="/owner/runtime_owner.js?v=6"></script>',
            "Runtime JavaScript cache version",
        )
        css_candidate = css_source.rstrip() + "\n" + CSS_APPEND.lstrip()
        js_candidate = js_source.rstrip() + "\n" + JS_APPEND.lstrip()

        checks["candidate_html_ids_unique"] = html_ids_unique(html_candidate)
        checks["candidate_css_balanced"] = css_balanced(css_candidate)
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(js_candidate)

        views = (
            "overview", "workflows", "stage_progress", "jobs_attempts",
            "dependencies_handoffs", "events_timeline", "failures", "output_readiness",
        )
        checks["eight_component_panels_present"] = all(
            html_candidate.count(f'data-pipeline-operations-view-panel="{view}"') == 1
            for view in views
        )
        checks["eight_workspace_tabs_enabled"] = (
            len(re.findall(r'data-pipeline-operations-view="[^"]+"', NEW_VIEW_NAV)) == 8
            and " disabled" not in NEW_VIEW_NAV
        )
        checks["eight_sidebar_destinations_enabled"] = (
            len(re.findall(r'data-runtime-pipeline-view="[^"]+"', NEW_SIDEBAR_DESTINATIONS)) == 8
            and " disabled" not in NEW_SIDEBAR_DESTINATIONS
        )
        checks["six_stage_shell_complete"] = all(
            stage in NEW_VIEW_MOUNT
            for stage in (
                "Connect Domain", "Site Sources", "URL Cleaner", "Site Pages",
                "Live Domain Target Pool", "Active Target Set",
            )
        )
        checks["component_state_architecture_present"] = (
            html_candidate.count('data-component-state="structure_ready"') == 8
            and 'data-state="empty"' in html_candidate
        )
        checks["sidebar_workspace_and_card_navigation_present"] = all(
            token in js_candidate
            for token in (
                'event.target.closest("[data-runtime-pipeline-view]")',
                'event.target.closest(".pipeline-operations-card[data-pipeline-id]")',
                "setPipelineView",
                "setSelectedPipeline",
            )
        )
        checks["keyboard_pipeline_card_navigation_present"] = (
            'event.key !== "Enter" && event.key !== " "' in js_candidate
            and 'card.tabIndex = 0' in js_candidate
        )
        checks["runtime_summary_endpoint_retained"] = (
            js_candidate.count('"/owner/api/runtime/summary"')
            == js_source.count('"/owner/api/runtime/summary"') == 1
        )
        checks["pipeline_index_endpoint_retained"] = (
            js_candidate.count('"/owner/api/runtime/pipelines"')
            == js_source.count('"/owner/api/runtime/pipelines"') == 1
        )
        checks["no_pipeline_detail_request_added"] = (
            "/owner/api/runtime/pipelines/" not in JS_APPEND
        )
        checks["no_new_fetch_requests_added"] = (
            js_candidate.count("fetch(") == js_source.count("fetch(")
        )
        checks["no_recovery_controls_added"] = all(
            token not in NEW_VIEW_MOUNT + JS_APPEND
            for token in (
                "data-runtime-recovery-action", "retryJob(", "cancelJob(", "terminateJob("
            )
        )
        checks["cache_versions_advanced"] = (
            '/owner/runtime_owner.css?v=6' in html_candidate
            and '/owner/runtime_owner.js?v=6' in html_candidate
        )
        if not all(checks.values()):
            raise RuntimeError("Combined component-shell candidate checks failed before patching.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = (
            root / "backend/server/data/runtime_backups"
            / f"part_f_15_b4d6_d8_{timestamp}"
        )
        backup_dir.mkdir(parents=True, exist_ok=False)
        for name in ("index_html", "runtime_owner_css", "runtime_owner_js"):
            path = paths[name]
            originals[name] = path.read_bytes()
            shutil.copy2(path, backup_dir / path.name)
        checks["backup_created"] = all(
            (backup_dir / paths[name].name).is_file() for name in originals
        )
        if not checks["backup_created"]:
            raise RuntimeError("Production UI backup is incomplete.")

        write_text(paths["index_html"], html_candidate)
        write_text(paths["runtime_owner_css"], css_candidate)
        write_text(paths["runtime_owner_js"], js_candidate)

        checks["retained_html_ids_unique"] = html_ids_unique(read_text(paths["index_html"]))
        checks["retained_css_balanced"] = css_balanced(read_text(paths["runtime_owner_css"]))
        checks["retained_javascript_syntax"] = javascript_syntax_valid(
            read_text(paths["runtime_owner_js"])
        )
        checks["retained_combined_markers"] = (
            read_text(paths["index_html"]).count(MARKER) == 2
            and read_text(paths["runtime_owner_css"]).count(MARKER) == 2
            and read_text(paths["runtime_owner_js"]).count(MARKER) == 2
        )

        after = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_after"] = after
        evidence["backup"] = str(backup_dir)
        evidence["completed_steps"] = ["15-B4D6", "15-B4D7", "15-B4D8"]
        evidence["monitoring_components"] = list(views)
        evidence["new_endpoint_requests"] = 0
        evidence["pipeline_detail_wiring_added"] = False
        evidence["recovery_controls_added"] = False

        for name in ("owner_css", "owner_js", "runtime_summary_api", "pipeline_operations"):
            checks[f"unchanged_{name}"] = before[name] == after[name]
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_no"] = True
        if not all(checks.values()):
            raise RuntimeError("Retained-source combined certification checks failed.")

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
            status=status, checks=checks, evidence=evidence,
            error=error, backup=backup_dir,
        ),
    )
    for name, value in checks.items():
        print_check(name, value)
    failed = [name for name, value in checks.items() if not value]
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B4D6_D8_STATUS={status}")
    print("PATCH_RETAINED=YES" if retained else "PATCH_RETAINED=NO")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
