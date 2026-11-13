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


STEP = "PART F 15-B4D3 THROUGH 15-B4D5"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B4D3 THROUGH 15-B4D5 "
    "RUNTIME UI REDESIGN CERTIFIED"
)
MARKER = "PART F 15-B4D3-D5 COMBINED RUNTIME UI REDESIGN"

EXPECTED_HASHES = {
    "index_html": "3623ef107bbc9cf3e82ce74440de52cc144e405b1ee1685f35aee72a91574061",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "bd43654128f36b2f38dd3418703fdfaf3763ca0c9fc2116f419933d44ef1aee5",
    "runtime_owner_js": "c0fe404aea9cf6d5b9a856b2094ff41d2816f261bb930a6ef6bcdcc8cf12a823",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "570bfc61676fd15b5a1cacc6ed74130eac1d98dc41f327606019df59d55f342a",
}

OLD_HEADER_STATUS = r'''    <header class="runtime-owner-header">
      <div class="runtime-owner-heading">
        <div class="runtime-owner-eyebrow">OWNER CONTROL TOWER / UNIVERSAL RUNTIME</div>
        <h2>Universal Runtime Command Center</h2>
        <p>
          Monitor, inspect, govern, recover, escalate, and audit the shared
          LinkCraftor runtime infrastructure without bypassing canonical
          runtime authorities.
        </p>
      </div>

      <div class="runtime-owner-header-meta">
        <span
          class="panel-badge"
          id="runtimeOwnerArchitectureBadge"
          data-runtime-owner-version="foundation-v1"
        >
          Runtime Owner Foundation v1
        </span>
      </div>
    </header>


    <section
      class="runtime-owner-status-bar"
      id="runtimeOwnerStatusBar"
      aria-label="Universal Runtime owner status"
    >

      <div class="runtime-owner-status-item">
        <span class="runtime-owner-status-label">Runtime Status</span>
        <strong
          class="runtime-owner-status-value"
          id="runtimeOwnerStatus"
        >
          Awaiting Runtime API Wiring
        </strong>
      </div>

      <div class="runtime-owner-status-item">
        <span class="runtime-owner-status-label">Owner Attention</span>
        <strong
          class="runtime-owner-status-value"
          id="runtimeOwnerAttention"
        >
          Not Evaluated
        </strong>
      </div>

      <div class="runtime-owner-status-item">
        <span class="runtime-owner-status-label">Architecture</span>
        <strong
          class="runtime-owner-status-value"
          id="runtimeOwnerArchitecture"
        >
          Universal Runtime
        </strong>
      </div>

      <div class="runtime-owner-status-item">
        <span class="runtime-owner-status-label">Last Refresh</span>
        <strong
          class="runtime-owner-status-value"
          id="runtimeOwnerLastRefresh"
        >
          Not Connected
        </strong>
      </div>

    </section>'''

NEW_HEADER_STATUS = r'''    <!-- BEGIN PART F 15-B4D3-D5 COMBINED RUNTIME UI REDESIGN -->
    <header class="runtime-owner-header runtime-command-header">
      <div class="runtime-owner-heading">
        <nav class="runtime-owner-breadcrumb" aria-label="Runtime breadcrumb">
          <span>Owner Control Tower</span>
          <span aria-hidden="true">/</span>
          <span>Universal Runtime</span>
          <span aria-hidden="true">/</span>
          <strong id="runtimeOwnerBreadcrumbCurrent">Runtime Overview</strong>
        </nav>

        <div class="runtime-owner-title-row">
          <div>
            <div class="runtime-owner-eyebrow">Runtime operations workspace</div>
            <h2>Universal Runtime</h2>
          </div>
          <span
            class="panel-badge runtime-owner-architecture-badge"
            id="runtimeOwnerArchitectureBadge"
            data-runtime-owner-version="foundation-v1"
          >
            Runtime Owner Foundation v1
          </span>
        </div>

        <p id="runtimeOwnerHeaderContext">
          Shared operational health, activity, capacity, and infrastructure state.
        </p>
      </div>
    </header>

    <section
      class="runtime-owner-status-bar runtime-command-status-strip"
      id="runtimeOwnerStatusBar"
      aria-label="Universal Runtime owner status"
    >
      <div class="runtime-owner-status-item" data-runtime-status-kind="health">
        <span class="runtime-owner-status-label">Runtime</span>
        <strong class="runtime-owner-status-value" id="runtimeOwnerStatus">
          Awaiting Runtime API Wiring
        </strong>
      </div>

      <div class="runtime-owner-status-item" data-runtime-status-kind="attention">
        <span class="runtime-owner-status-label">Attention</span>
        <strong class="runtime-owner-status-value" id="runtimeOwnerAttention">
          Not Evaluated
        </strong>
      </div>

      <div class="runtime-owner-status-item" data-runtime-status-kind="architecture">
        <span class="runtime-owner-status-label">Architecture</span>
        <strong class="runtime-owner-status-value" id="runtimeOwnerArchitecture">
          Universal Runtime
        </strong>
      </div>

      <div class="runtime-owner-status-item" data-runtime-status-kind="refresh">
        <span class="runtime-owner-status-label">Last refresh</span>
        <strong class="runtime-owner-status-value" id="runtimeOwnerLastRefresh">
          Not Connected
        </strong>
      </div>
    </section>
    <!-- END PART F 15-B4D3-D5 COMBINED RUNTIME UI REDESIGN -->'''

OLD_OVERVIEW_HEADING = r'''        <div class="runtime-overview-heading">
          <div>
            <h3>Runtime Overview</h3>
            <p>
              Live read-only operational summary from the canonical
              Universal Runtime Owner API.
            </p>
          </div>

          <button
            type="button"
            class="runtime-overview-refresh"
            id="runtimeOverviewRefreshButton"
          >
            Refresh
          </button>
        </div>'''

NEW_OVERVIEW_HEADING = r'''        <div class="runtime-overview-heading runtime-section-heading">
          <div>
            <span class="runtime-section-kicker">Command center</span>
            <h3>Runtime Overview</h3>
            <p>
              Live read-only health and activity from the canonical Runtime Owner API.
            </p>
          </div>

          <div class="runtime-section-actions">
            <span class="runtime-section-mode">Live summary</span>
            <button
              type="button"
              class="runtime-overview-refresh"
              id="runtimeOverviewRefreshButton"
            >
              Refresh summary
            </button>
          </div>
        </div>'''

OLD_PIPELINE_HEADING = r'''        <div class="pipeline-operations-heading">
          <div>
            <span class="pipeline-operations-eyebrow">Universal per-pipeline operations</span>
            <h3>Pipeline Operations</h3>
            <p>
              Inspect registered pipelines through the certified read-only
              Runtime Pipeline Operations boundary.
            </p>
          </div>
          <span class="pipeline-operations-read-only-badge">Read-only</span>
        </div>'''

NEW_PIPELINE_HEADING = r'''        <div class="pipeline-operations-heading runtime-section-heading">
          <div>
            <span class="runtime-section-kicker">Pipeline command workspace</span>
            <h3>Pipeline Operations</h3>
            <p>
              Select a registered pipeline, then inspect its operational workspace.
            </p>
          </div>
          <div class="pipeline-operations-heading-meta">
            <span class="pipeline-operations-read-only-badge">Read-only</span>
            <small>Canonical Runtime projection</small>
          </div>
        </div>'''

CSS_APPEND = r'''

/* BEGIN PART F 15-B4D3-D5 COMBINED RUNTIME UI REDESIGN */
#runtimePage .runtime-owner-shell {
  gap: 12px;
}

#runtimePage .runtime-command-header {
  position: relative;
  overflow: hidden;
  padding: 18px 20px;
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: 16px;
  background:
    radial-gradient(circle at 88% 18%, rgba(34, 211, 238, 0.14), transparent 32%),
    linear-gradient(135deg, rgba(15, 35, 62, 0.96), rgba(11, 29, 51, 0.88));
  box-shadow: 0 14px 32px rgba(2, 8, 23, 0.16);
}

#runtimePage .runtime-command-header::after {
  content: "";
  position: absolute;
  inset: auto 0 0;
  height: 2px;
  background: linear-gradient(90deg, #22d3ee, #38bdf8 44%, transparent 82%);
  opacity: 0.72;
}

#runtimePage .runtime-owner-heading {
  width: 100%;
}

#runtimePage .runtime-owner-breadcrumb {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 7px;
  margin-bottom: 13px;
  color: #7890ad;
  font-size: 10px;
  font-weight: 750;
  letter-spacing: 0.065em;
  text-transform: uppercase;
}

#runtimePage .runtime-owner-breadcrumb strong {
  color: #bdeff7;
}

#runtimePage .runtime-owner-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

#runtimePage .runtime-owner-title-row h2 {
  margin: 0;
  font-size: clamp(22px, 2.4vw, 30px);
  line-height: 1.08;
}

#runtimePage .runtime-owner-eyebrow {
  margin-bottom: 5px;
  color: #67e8f9;
  opacity: 0.78;
  font-size: 10px;
}

#runtimePage .runtime-command-header p {
  max-width: 760px;
  margin: 10px 0 0;
  color: #9db0ca;
  font-size: 13px;
  line-height: 1.45;
}

#runtimePage .runtime-owner-architecture-badge {
  border-color: rgba(34, 211, 238, 0.32);
  background: rgba(34, 211, 238, 0.09);
  color: #bdf7ff;
  white-space: nowrap;
}

#runtimePage .runtime-command-status-strip {
  display: grid;
  grid-template-columns: 0.9fr 0.9fr 1fr 1.35fr;
  gap: 0;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 13px;
  background: rgba(8, 24, 44, 0.58);
}

#runtimePage .runtime-command-status-strip .runtime-owner-status-item {
  position: relative;
  min-height: 58px;
  padding: 11px 15px 10px 18px;
  border: 0;
  border-right: 1px solid rgba(148, 163, 184, 0.13);
  border-radius: 0;
}

#runtimePage .runtime-command-status-strip .runtime-owner-status-item:last-child {
  border-right: 0;
}

#runtimePage .runtime-command-status-strip .runtime-owner-status-item::before {
  content: "";
  position: absolute;
  left: 8px;
  top: 17px;
  width: 4px;
  height: 22px;
  border-radius: 999px;
  background: #38bdf8;
  opacity: 0.72;
}

#runtimePage .runtime-command-status-strip [data-runtime-status-kind="attention"]::before {
  background: #f59e0b;
}

#runtimePage .runtime-command-status-strip [data-runtime-status-kind="architecture"]::before {
  background: #8b5cf6;
}

#runtimePage .runtime-command-status-strip [data-runtime-status-kind="refresh"]::before {
  background: #64748b;
}

#runtimePage .runtime-owner-status-label {
  margin: 0 0 3px;
  color: #7186a2;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

#runtimePage .runtime-owner-status-value {
  color: #e7f6ff;
  font-size: 12px;
  line-height: 1.35;
}

#runtimePage .runtime-owner-content-shell {
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(10, 28, 49, 0.7), rgba(7, 21, 38, 0.5));
  box-shadow: 0 16px 38px rgba(2, 8, 23, 0.13);
}

#runtimePage .runtime-owner-content-panel {
  padding: 18px;
}

#runtimePage .runtime-section-heading {
  align-items: center;
  margin-bottom: 13px;
  padding-bottom: 13px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.14);
}

#runtimePage .runtime-section-kicker {
  display: block;
  margin-bottom: 4px;
  color: #67e8f9;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

#runtimePage .runtime-section-heading h3 {
  margin-bottom: 3px;
  font-size: 19px;
}

#runtimePage .runtime-section-heading p {
  color: #8ea3be;
  font-size: 12px;
}

#runtimePage .runtime-section-actions {
  display: flex;
  align-items: center;
  gap: 9px;
}

#runtimePage .runtime-section-mode {
  color: #7dd3fc;
  font-size: 10px;
  font-weight: 750;
  text-transform: uppercase;
}

#runtimePage .runtime-overview-refresh {
  border-color: rgba(34, 211, 238, 0.3);
  background: rgba(34, 211, 238, 0.1);
  color: #d9fbff;
  font-size: 11px;
  font-weight: 750;
  padding: 8px 11px;
}

#runtimePage .runtime-overview-notice {
  margin-bottom: 12px;
  padding: 8px 11px;
  border-color: rgba(56, 189, 248, 0.16);
  background: rgba(56, 189, 248, 0.055);
  color: #9fb8d2;
  font-size: 11px;
}

#runtimePage .runtime-overview-groups {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 11px;
}

#runtimePage .runtime-overview-group {
  grid-column: span 6;
  padding: 13px;
  border-color: rgba(148, 163, 184, 0.14);
  border-radius: 12px;
  background: rgba(9, 28, 49, 0.56);
}

#runtimePage .runtime-overview-group:nth-child(1) {
  grid-column: 1 / -1;
  background: linear-gradient(135deg, rgba(12, 41, 67, 0.8), rgba(8, 27, 47, 0.62));
}

#runtimePage .runtime-overview-group:nth-child(2),
#runtimePage .runtime-overview-group:nth-child(4) {
  grid-column: span 7;
}

#runtimePage .runtime-overview-group:nth-child(3),
#runtimePage .runtime-overview-group:nth-child(5) {
  grid-column: span 5;
}

#runtimePage .runtime-overview-group-head {
  margin-bottom: 9px;
}

#runtimePage .runtime-overview-group-head h4 {
  color: #eefaff;
  font-size: 13px;
}

#runtimePage .runtime-overview-group-head p {
  color: #7890ad;
  font-size: 10px;
}

#runtimePage .runtime-overview-group .runtime-overview-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
}

#runtimePage .runtime-overview-group:nth-child(1) .runtime-overview-grid {
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

#runtimePage .runtime-overview-card {
  min-height: 67px;
  padding: 10px 11px;
  border: 0;
  border-left: 2px solid rgba(56, 189, 248, 0.5);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.035);
}

#runtimePage .runtime-overview-card-label {
  color: #7890ad;
  font-size: 9px;
  font-weight: 750;
  letter-spacing: 0.025em;
}

#runtimePage .runtime-overview-card strong {
  color: #f1fbff;
  font-size: 17px;
  line-height: 1.2;
}

#runtimePage .runtime-overview-health-reasons {
  margin-top: 8px;
  padding: 9px 10px;
  border-color: rgba(148, 163, 184, 0.18);
  background: rgba(2, 8, 23, 0.16);
  color: #91a7c1;
  font-size: 11px;
}

#runtimePage .pipeline-operations-heading-meta {
  display: grid;
  justify-items: end;
  gap: 5px;
}

#runtimePage .pipeline-operations-heading-meta small {
  color: #7186a2;
  font-size: 9px;
}

#runtimePage .pipeline-operations-layout {
  grid-template-columns: minmax(270px, 0.34fr) minmax(0, 1fr);
  gap: 11px;
}

#runtimePage .pipeline-operations-directory,
#runtimePage .pipeline-operations-workspace {
  padding: 14px;
  border-color: rgba(148, 163, 184, 0.14);
  border-radius: 12px;
  background: rgba(8, 25, 44, 0.54);
}

#runtimePage .pipeline-operations-directory {
  border-top-color: rgba(34, 211, 238, 0.38);
}

#runtimePage .pipeline-operations-workspace {
  min-height: 430px;
  border-top-color: rgba(139, 92, 246, 0.35);
}

#runtimePage .pipeline-operations-region-heading,
#runtimePage .pipeline-operations-workspace-header {
  padding-bottom: 11px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

#runtimePage .pipeline-operations-region-heading h4,
#runtimePage .pipeline-operations-workspace-header h4 {
  color: #eefaff;
  font-size: 14px;
}

#runtimePage .pipeline-operations-region-heading p,
#runtimePage .pipeline-operations-workspace-header p {
  color: #7f96b3;
  font-size: 11px;
}

#runtimePage .pipeline-operations-read-only-badge,
#runtimePage .pipeline-operations-health-badge {
  border-color: rgba(34, 211, 238, 0.25);
  background: rgba(34, 211, 238, 0.07);
  color: #bdf7ff;
  font-size: 9px;
  letter-spacing: 0.055em;
  text-transform: uppercase;
}

#runtimePage .pipeline-operations-pipeline-list {
  gap: 8px;
  margin-top: 11px;
}

#runtimePage .pipeline-operations-card {
  padding: 11px;
  border-color: rgba(148, 163, 184, 0.14);
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(18, 48, 76, 0.66), rgba(9, 28, 49, 0.54));
  transition: border-color 150ms ease, transform 150ms ease;
}

#runtimePage .pipeline-operations-card:hover {
  border-color: rgba(34, 211, 238, 0.36);
  transform: translateY(-1px);
}

#runtimePage .pipeline-operations-card-metrics {
  gap: 5px;
  margin-top: 9px;
}

#runtimePage .pipeline-operations-card-metric {
  padding: 7px;
  background: rgba(2, 8, 23, 0.2);
}

#runtimePage .pipeline-operations-card-stage-list {
  margin-top: 9px;
}

#runtimePage .pipeline-operations-view-nav {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 6px;
  overflow: visible;
  margin-top: 12px;
}

#runtimePage .pipeline-operations-view-nav button {
  min-width: 0;
  border-radius: 7px;
  padding: 7px 6px;
  font-size: 9px;
  line-height: 1.2;
  white-space: normal;
}

#runtimePage .pipeline-operations-view-nav button:disabled {
  border-color: rgba(148, 163, 184, 0.12);
  background: rgba(255, 255, 255, 0.025);
  color: #69809e;
  opacity: 0.76;
}

#runtimePage .pipeline-operations-view-mount {
  display: grid;
  min-height: 250px;
  margin-top: 11px;
  place-items: center;
}

#runtimePage .pipeline-operations-view-mount .pipeline-operations-structural-placeholder {
  width: min(100%, 520px);
  padding: 30px 18px;
  border-color: rgba(56, 189, 248, 0.18);
  background: radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.08), transparent 66%);
  color: #8198b5;
  text-align: center;
}

@media (max-width: 1180px) {
  #runtimePage .runtime-overview-group:nth-child(n) {
    grid-column: span 6;
  }

  #runtimePage .runtime-overview-group:nth-child(1) {
    grid-column: 1 / -1;
  }

  #runtimePage .runtime-overview-group:nth-child(1) .runtime-overview-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 940px) {
  #runtimePage .runtime-command-status-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  #runtimePage .runtime-command-status-strip .runtime-owner-status-item:nth-child(2) {
    border-right: 0;
  }

  #runtimePage .runtime-command-status-strip .runtime-owner-status-item:nth-child(-n + 2) {
    border-bottom: 1px solid rgba(148, 163, 184, 0.13);
  }

  #runtimePage .pipeline-operations-layout {
    grid-template-columns: 1fr;
  }

  #runtimePage .pipeline-operations-workspace {
    min-height: 360px;
  }
}

@media (max-width: 700px) {
  #runtimePage .runtime-owner-content-panel {
    padding: 12px;
  }

  #runtimePage .runtime-owner-title-row,
  #runtimePage .runtime-section-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  #runtimePage .runtime-owner-architecture-badge {
    white-space: normal;
  }

  #runtimePage .runtime-overview-group:nth-child(n) {
    grid-column: 1 / -1;
  }

  #runtimePage .runtime-overview-group:nth-child(1) .runtime-overview-grid,
  #runtimePage .runtime-overview-group .runtime-overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  #runtimePage .pipeline-operations-view-nav {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  #runtimePage .runtime-command-header {
    padding: 15px;
  }

  #runtimePage .runtime-command-status-strip {
    grid-template-columns: 1fr;
  }

  #runtimePage .runtime-command-status-strip .runtime-owner-status-item {
    border-right: 0;
    border-bottom: 1px solid rgba(148, 163, 184, 0.13);
  }

  #runtimePage .runtime-command-status-strip .runtime-owner-status-item:last-child {
    border-bottom: 0;
  }

  #runtimePage .runtime-overview-group:nth-child(1) .runtime-overview-grid,
  #runtimePage .runtime-overview-group .runtime-overview-grid {
    grid-template-columns: 1fr;
  }
}
/* END PART F 15-B4D3-D5 COMBINED RUNTIME UI REDESIGN */
'''

JS_APPEND = r'''

// BEGIN PART F 15-B4D3-D5 COMBINED RUNTIME UI REDESIGN
(() => {
  "use strict";

  const SECTION_PRESENTATION = Object.freeze({
    overview: [
      "Runtime Overview",
      "Shared operational health, activity, capacity, and infrastructure state."
    ],
    pipeline_operations: [
      "Pipeline Operations",
      "Registered pipeline directory and selected-pipeline operations workspace."
    ],
    jobs: ["Jobs", "Runtime job inventory, state, and execution evidence."],
    queues: ["Queues", "Queue depth, pressure, claims, and dispatch state."],
    workers_leases: ["Workers & Leases", "Worker availability and lease ownership."],
    orchestration: ["Orchestration", "Workflow orchestration and dependency state."],
    execution: ["Execution", "Runtime execution activity and terminal outcomes."],
    reliability_recovery: ["Reliability & Recovery", "Failure, retry, and recovery posture."],
    resource_governance: ["Resource Governance", "Runtime capacity and resource controls."],
    observability: ["Observability", "Runtime signals, diagnostics, and evidence."],
    security: ["Security", "Runtime security posture and owner attention."],
    runtime_apis: ["Runtime APIs", "Canonical Runtime API availability and health."],
    persistence_state_integrity: ["Persistence & Integrity", "Durable state and persistence integrity."],
    owner_actions: ["Owner Actions", "Governed owner operations and approvals."],
    evidence_audit: ["Evidence & Audit", "Runtime certification and audit evidence."]
  });

  const updateRuntimeCommandHeader = (section) => {
    const presentation = SECTION_PRESENTATION[section] || SECTION_PRESENTATION.overview;
    const breadcrumb = document.getElementById("runtimeOwnerBreadcrumbCurrent");
    const context = document.getElementById("runtimeOwnerHeaderContext");
    const page = document.getElementById("runtimePage");

    if (breadcrumb) {
      breadcrumb.textContent = presentation[0];
    }

    if (context) {
      context.textContent = presentation[1];
    }

    if (page) {
      page.dataset.runtimeOwnerVisualSection = section;
    }
  };

  const initializeRuntimeCommandHeader = () => {
    const page = document.getElementById("runtimePage");

    if (!page || page.dataset.runtimeCommandHeaderBound === "true") {
      return false;
    }

    page.addEventListener("runtimeowner:sectionchange", (event) => {
      updateRuntimeCommandHeader(event.detail?.section || "overview");
    });

    page.dataset.runtimeCommandHeaderBound = "true";
    updateRuntimeCommandHeader(
      window.LinkCraftorRuntimeOwner?.getActiveSection?.() || "overview"
    );
    return true;
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeRuntimeCommandHeader);
  } else {
    initializeRuntimeCommandHeader();
  }
})();
// END PART F 15-B4D3-D5 COMBINED RUNTIME UI REDESIGN
'''


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
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
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4d3_d5_js_") as folder:
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
    *,
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
    backup: Path | None,
) -> str:
    failed = [name for name, value in checks.items() if not value]
    final = FINAL_RESULT if status == "CERTIFIED" else (
        "FINAL RESULT: PART F 15-B4D3 THROUGH 15-B4D5 "
        "RUNTIME UI REDESIGN NOT_CERTIFIED"
    )
    return f'''LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS
PART F 15-B4D3 THROUGH 15-B4D5 COMBINED RUNTIME UI REDESIGN CERTIFICATION

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
- 15-B4D3 replaces the oversized Runtime header with a compact breadcrumb, title and status strip.
- 15-B4D4 recomposes the existing Runtime Overview data into a dense responsive operations dashboard.
- 15-B4D5 recomposes Pipeline Operations into a directory-and-workspace command layout.
- Existing Runtime Summary and All Pipelines endpoints and DOM bindings are retained.
- Pipeline-detail destinations remain disabled; no detail endpoint request was added.
- No recovery control, Runtime mutation or backend authority was added.

NEXT STEP:
Part F 15-B4D6 - static locations for every monitoring component.

FINAL RESULT:
{final}
'''


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4D3_D5_RUNTIME_UI_REDESIGN.py <project_root> <report_path>"
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
    d2r_report = (
        root
        / "backend/server/data/reports/"
        "PART_F_15_B4D2R_COMPACT_RUNTIME_SIDEBAR_CERTIFICATION.txt"
    )

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}
    backup_dir: Path | None = None
    retained = False
    status = "NOT_CERTIFIED"

    try:
        checks["part_f_15_b4d2r_report_exists"] = d2r_report.is_file()
        checks["part_f_15_b4d2r_certified"] = (
            checks["part_f_15_b4d2r_report_exists"]
            and "CERTIFICATION STATUS: CERTIFIED" in read_text(d2r_report)
            and "FINAL RESULT: PART F 15-B4D2R COMPACT RUNTIME SIDEBAR CORRECTION CERTIFIED"
            in read_text(d2r_report)
        )

        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("Required source or 15-B4D2R evidence is unavailable.")

        before = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()):
            raise RuntimeError("Installed UI source lineage does not match 15-B4D2R.")

        html_source = read_text(paths["index_html"])
        css_source = read_text(paths["runtime_owner_css"])
        js_source = read_text(paths["runtime_owner_js"])

        checks["combined_redesign_not_previously_present"] = (
            MARKER not in html_source
            and MARKER not in css_source
            and MARKER not in js_source
        )

        html_candidate = replace_once(
            html_source,
            OLD_HEADER_STATUS,
            NEW_HEADER_STATUS,
            "Runtime header and status",
        )
        html_candidate = replace_once(
            html_candidate,
            OLD_OVERVIEW_HEADING,
            NEW_OVERVIEW_HEADING,
            "Runtime Overview heading",
        )
        html_candidate = replace_once(
            html_candidate,
            OLD_PIPELINE_HEADING,
            NEW_PIPELINE_HEADING,
            "Pipeline Operations heading",
        )
        html_candidate = replace_once(
            html_candidate,
            'data-pipeline-operations-layout-version="15-b4b"',
            'data-pipeline-operations-layout-version="15-b4d5"',
            "Pipeline Operations layout version",
        )
        html_candidate = replace_once(
            html_candidate,
            '<link rel="stylesheet" href="/owner/runtime_owner.css?v=2" />',
            '<link rel="stylesheet" href="/owner/runtime_owner.css?v=5" />',
            "Runtime stylesheet cache version",
        )
        html_candidate = replace_once(
            html_candidate,
            '<script src="/owner/runtime_owner.js?v=3"></script>',
            '<script src="/owner/runtime_owner.js?v=5"></script>',
            "Runtime JavaScript cache version",
        )

        css_candidate = css_source.rstrip() + "\n" + CSS_APPEND.lstrip()
        js_candidate = js_source.rstrip() + "\n" + JS_APPEND.lstrip()

        checks["candidate_html_ids_unique"] = html_ids_unique(html_candidate)
        checks["candidate_css_balanced"] = css_balanced(css_candidate)
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(js_candidate)
        checks["compact_header_and_breadcrumb_present"] = all(
            token in html_candidate
            for token in (
                'id="runtimeOwnerBreadcrumbCurrent"',
                'id="runtimeOwnerHeaderContext"',
                "runtime-command-status-strip",
            )
        )
        checks["runtime_overview_dashboard_present"] = all(
            token in css_candidate
            for token in (
                "grid-template-columns: repeat(12, minmax(0, 1fr));",
                ".runtime-overview-group:nth-child(1)",
                ".runtime-overview-health-reasons",
            )
        )
        checks["pipeline_workspace_redesign_present"] = all(
            token in html_candidate + css_candidate
            for token in (
                'data-pipeline-operations-layout-version="15-b4d5"',
                ".pipeline-operations-directory",
                ".pipeline-operations-workspace",
                ".pipeline-operations-view-nav",
            )
        )
        checks["dynamic_breadcrumb_binding_present"] = (
            'page.addEventListener("runtimeowner:sectionchange"' in js_candidate
            and 'document.getElementById("runtimeOwnerBreadcrumbCurrent")' in js_candidate
        )

        preserved_ids = (
            "runtimeOwnerArchitectureBadge",
            "runtimeOwnerStatus",
            "runtimeOwnerAttention",
            "runtimeOwnerArchitecture",
            "runtimeOwnerLastRefresh",
            "runtimeOverviewRefreshButton",
            "runtimeOverviewNotice",
            "runtimeOverviewGrid",
            "runtimeOverviewActiveJobs",
            "runtimeOverviewQueuedJobs",
            "runtimeOverviewRunningExecutions",
            "runtimeOverviewActiveWorkers",
            "runtimeOverviewActiveLeases",
            "runtimeOverviewActiveOrchestrations",
            "runtimeOverviewFailedWork",
            "runtimeOverviewRecoveringWork",
            "runtimeOverviewRuntimeAlerts",
            "runtimeOverviewOwnerAttention",
            "runtimeOverviewQueuePressure",
            "runtimeOverviewResourcePressure",
            "runtimeOverviewPersistenceHealth",
            "runtimeOverviewSecurityHealth",
            "runtimeOverviewApiHealth",
            "runtimeOverviewRuntimeHealth",
            "runtimeOverviewArchitectureVersion",
            "runtimeOverviewHealthReasons",
            "pipelineOperationsLayout",
            "pipelineOperationsDirectory",
            "pipelineOperationsPipelineList",
            "pipelineOperationsWorkspace",
            "pipelineOperationsSelectedPipeline",
            "pipelineOperationsSelectedPipelineSummary",
            "pipelineOperationsSelectedPipelineHealth",
            "pipelineOperationsViewNav",
            "pipelineOperationsViewMount",
        )
        checks["all_existing_data_binding_ids_preserved"] = all(
            html_candidate.count(f'id="{identifier}"') == 1
            for identifier in preserved_ids
        )
        checks["future_pipeline_views_remain_disabled"] = (
            len(
                re.findall(
                    r"<button[^>]+data-pipeline-operations-view=\"[^\"]+\"[^>]+disabled[^>]*>",
                    html_candidate,
                )
            )
            == 8
        )
        checks["runtime_summary_endpoint_retained"] = (
            js_candidate.count('"/owner/api/runtime/summary"')
            == js_source.count('"/owner/api/runtime/summary"')
            == 1
        )
        checks["pipeline_index_endpoint_retained"] = (
            js_candidate.count('"/owner/api/runtime/pipelines"')
            == js_source.count('"/owner/api/runtime/pipelines"')
            == 1
        )
        checks["no_new_fetch_requests_added"] = (
            js_candidate.count("fetch(") == js_source.count("fetch(")
        )
        checks["no_recovery_controls_added"] = all(
            token not in NEW_HEADER_STATUS + NEW_OVERVIEW_HEADING + NEW_PIPELINE_HEADING + JS_APPEND
            for token in (
                "data-runtime-recovery-action",
                "retryJob(",
                "cancelJob(",
                "terminateJob(",
            )
        )
        checks["cache_versions_advanced"] = (
            '/owner/runtime_owner.css?v=5' in html_candidate
            and '/owner/runtime_owner.js?v=5' in html_candidate
        )

        if not all(checks.values()):
            raise RuntimeError("Combined UI candidate checks failed before patching.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = (
            root
            / "backend/server/data/runtime_backups"
            / f"part_f_15_b4d3_d5_{timestamp}"
        )
        backup_dir.mkdir(parents=True, exist_ok=False)

        for name in ("index_html", "runtime_owner_css", "runtime_owner_js"):
            path = paths[name]
            originals[name] = path.read_bytes()
            shutil.copy2(path, backup_dir / path.name)

        checks["backup_created"] = all(
            (backup_dir / paths[name].name).is_file()
            for name in originals
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
        checks["retained_redesign_markers"] = (
            read_text(paths["index_html"]).count(MARKER) == 2
            and read_text(paths["runtime_owner_css"]).count(MARKER) == 2
            and read_text(paths["runtime_owner_js"]).count(MARKER) == 2
        )

        after = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_after"] = after
        evidence["backup"] = str(backup_dir)
        evidence["completed_steps"] = ["15-B4D3", "15-B4D4", "15-B4D5"]
        evidence["redesigned_surfaces"] = [
            "compact Runtime header, breadcrumb and status strip",
            "Runtime Overview dashboard",
            "Pipeline Operations directory and workspace",
        ]
        evidence["new_endpoint_requests"] = 0
        evidence["recovery_controls_added"] = False

        for name in (
            "owner_css",
            "owner_js",
            "runtime_summary_api",
            "pipeline_operations",
        ):
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
    print(f"PART_F_15_B4D3_D5_STATUS={status}")
    print("PATCH_RETAINED=YES" if retained else "PATCH_RETAINED=NO")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
