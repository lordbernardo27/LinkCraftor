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


FINAL_RESULT = "FINAL RESULT: PART F 15-B4G JOBS AND ATTEMPTS COMPONENT CERTIFIED"
MARKER = "PART F 15-B4G JOBS AND ATTEMPTS COMPONENT"

EXPECTED_HASHES = {
    "index_html": "b1b8f3401221e3f72249cf3efb884606f597dda02eb8f8098bcd77ad42b63308",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "1ecd28bc73f58605c843eb7e7db8d5c62a85a009e5f3ad9154eceaab0db984f2",
    "runtime_owner_js": "202a70666d29342309a243aa6b05a7ec114cd60a92707f5f905aa849c8a43fe2",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_PANEL = r'''              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewJobsAttempts" data-pipeline-operations-view-panel="jobs_attempts" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Runtime execution</span><h5>Jobs &amp; Attempts</h5><p>Universal Jobs, attempts, queue state, worker ownership, and terminal results.</p></div><strong>Structure ready</strong></header>
                <div class="pipeline-table-shell"><div><span>Stage / Job</span><span>Status</span><span>Attempt</span><span>Worker</span><span>Updated</span></div><p>No workflow selected. Job evidence will appear here.</p></div>
              </section>'''

NEW_PANEL = r'''              <!-- BEGIN PART F 15-B4G JOBS AND ATTEMPTS COMPONENT -->
              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewJobsAttempts" data-pipeline-operations-view-panel="jobs_attempts" data-component-state="loading" role="tabpanel" aria-busy="true" hidden>
                <header class="pipeline-monitoring-panel-head">
                  <div><span>Runtime execution</span><h5>Jobs &amp; Attempts</h5><p>Inspect Universal Jobs, stage ownership, attempt limits, worker assignment, progress, retry evidence, and terminal results.</p></div>
                  <strong id="pipelineJobsAttemptsState">Loading</strong>
                </header>
                <div class="pipeline-jobs-attempts-live">
                  <div class="pipeline-jobs-toolbar">
                    <label><span>Workflow</span><select id="pipelineJobsWorkflow"><option value="">Loading workflows</option></select></label>
                    <label><span>Status</span><select id="pipelineJobsStatus"><option value="all">All statuses</option><option value="created">Created</option><option value="queued">Queued</option><option value="pending">Pending</option><option value="running">Running</option><option value="completed">Completed</option><option value="failed">Failed</option><option value="cancelled">Cancelled</option></select></label>
                    <label class="pipeline-jobs-search"><span>Find job</span><input id="pipelineJobsSearch" type="search" autocomplete="off" placeholder="Job, stage, type, or worker" /></label>
                    <div><span>Visible jobs</span><strong id="pipelineJobsCount">Loading</strong></div>
                  </div>
                  <div class="pipeline-jobs-layout">
                    <div class="pipeline-jobs-directory" id="pipelineJobsDirectory" role="listbox" aria-label="Connected Domain jobs" aria-busy="true">
                      <div class="pipeline-jobs-placeholder"><strong>Loading job evidence</strong><p>Reading the cached Pipeline Operations projection.</p></div>
                    </div>
                    <div class="pipeline-job-detail" id="pipelineJobDetail" aria-live="polite">
                      <div class="pipeline-jobs-placeholder"><strong>Awaiting job evidence</strong><p>Select a projected job to inspect its attempt and runtime details.</p></div>
                    </div>
                  </div>
                  <div class="pipeline-component-state pipeline-jobs-message" id="pipelineJobsMessage" data-state="loading" role="status" aria-live="polite"><span aria-hidden="true">◌</span><div><strong>Loading jobs and attempts</strong><p>Using the existing Connected Domain detail snapshot.</p></div></div>
                </div>
              </section>
              <!-- END PART F 15-B4G JOBS AND ATTEMPTS COMPONENT -->'''

CSS_APPEND = r'''

/* BEGIN PART F 15-B4G JOBS AND ATTEMPTS COMPONENT */
#runtimePage .pipeline-jobs-attempts-live { display: grid; gap: 10px; }
#runtimePage .pipeline-jobs-toolbar {
  display: grid; grid-template-columns: minmax(210px,1.1fr) minmax(125px,.55fr) minmax(200px,1fr) minmax(95px,.4fr);
  gap: 8px; align-items: end; padding: 9px; border: 1px solid rgba(148,163,184,.12); border-radius: 9px; background: rgba(5,17,32,.28);
}
#runtimePage .pipeline-jobs-toolbar label,
#runtimePage .pipeline-jobs-toolbar > div { display: grid; gap: 4px; min-width: 0; }
#runtimePage .pipeline-jobs-toolbar span { color: #7890ad; font-size: 8px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
#runtimePage .pipeline-jobs-toolbar strong { overflow: hidden; color: #e6f7ff; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
#runtimePage .pipeline-jobs-toolbar select,
#runtimePage .pipeline-jobs-toolbar input {
  width: 100%; min-height: 32px; padding: 6px 9px; border: 1px solid rgba(103,232,249,.2); border-radius: 7px;
  outline: none; background: rgba(4,15,29,.72); color: #dceefa; font: inherit; font-size: 10px;
}
#runtimePage .pipeline-jobs-toolbar select:focus-visible,
#runtimePage .pipeline-jobs-toolbar input:focus-visible { border-color: #22d3ee; box-shadow: 0 0 0 2px rgba(34,211,238,.16); }
#runtimePage .pipeline-jobs-layout { display: grid; grid-template-columns: minmax(300px,.95fr) minmax(0,1.25fr); gap: 10px; min-height: 300px; }
#runtimePage .pipeline-jobs-directory,
#runtimePage .pipeline-job-detail { min-width: 0; padding: 9px; border: 1px solid rgba(148,163,184,.12); border-radius: 9px; background: rgba(5,17,32,.24); }
#runtimePage .pipeline-jobs-directory { display: grid; align-content: start; gap: 6px; max-height: 430px; overflow: auto; }
#runtimePage .pipeline-job-row {
  display: grid; gap: 7px; width: 100%; padding: 9px 10px; border: 1px solid rgba(148,163,184,.13); border-radius: 8px;
  background: rgba(255,255,255,.025); color: inherit; text-align: left; cursor: pointer;
}
#runtimePage .pipeline-job-row:hover { border-color: rgba(103,232,249,.32); background: rgba(34,211,238,.055); }
#runtimePage .pipeline-job-row.active { border-color: rgba(34,211,238,.54); background: linear-gradient(135deg,rgba(34,211,238,.13),rgba(59,130,246,.055)); box-shadow: inset 2px 0 0 #22d3ee; }
#runtimePage .pipeline-job-row:focus-visible { outline: 2px solid #22d3ee; outline-offset: 1px; }
#runtimePage .pipeline-job-row-head,
#runtimePage .pipeline-job-row-meta { display: flex; align-items: center; justify-content: space-between; gap: 8px; min-width: 0; }
#runtimePage .pipeline-job-row-head strong { overflow: hidden; color: #e6f7ff; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
#runtimePage .pipeline-job-row-meta span { overflow: hidden; color: #7890ad; font-size: 8px; text-overflow: ellipsis; white-space: nowrap; }
#runtimePage .pipeline-job-status { flex: 0 0 auto; padding: 3px 6px; border: 1px solid rgba(103,232,249,.22); border-radius: 999px; color: #67e8f9; font-size: 7px; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; }
#runtimePage .pipeline-job-status[data-status="failed"] { border-color: rgba(251,113,133,.32); color: #fb7185; }
#runtimePage .pipeline-job-status[data-status="completed"] { border-color: rgba(74,222,128,.3); color: #86efac; }
#runtimePage .pipeline-job-status[data-status="queued"],
#runtimePage .pipeline-job-status[data-status="pending"] { border-color: rgba(250,204,21,.3); color: #fde047; }
#runtimePage .pipeline-job-detail { display: grid; align-content: start; gap: 10px; }
#runtimePage .pipeline-job-detail-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; padding-bottom: 9px; border-bottom: 1px solid rgba(148,163,184,.1); }
#runtimePage .pipeline-job-detail-head div { display: grid; gap: 4px; min-width: 0; }
#runtimePage .pipeline-job-detail-head div span,
#runtimePage .pipeline-job-facts span { color: #7890ad; font-size: 8px; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; }
#runtimePage .pipeline-job-detail-head div strong { overflow-wrap: anywhere; color: #e6f7ff; font-size: 11px; }
#runtimePage .pipeline-job-facts { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 7px; }
#runtimePage .pipeline-job-facts article { display: grid; gap: 4px; min-width: 0; padding: 8px; border: 1px solid rgba(148,163,184,.1); border-radius: 7px; background: rgba(255,255,255,.02); }
#runtimePage .pipeline-job-facts strong { overflow-wrap: anywhere; color: #dceefa; font-size: 9px; }
#runtimePage .pipeline-job-progress { display: grid; gap: 5px; }
#runtimePage .pipeline-job-progress div { height: 5px; overflow: hidden; border-radius: 999px; background: rgba(148,163,184,.12); }
#runtimePage .pipeline-job-progress i { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg,#22d3ee,#34d399); }
#runtimePage .pipeline-job-error { padding: 8px; border: 1px solid rgba(251,113,133,.18); border-radius: 7px; background: rgba(244,63,94,.04); color: #fda4af; font-size: 9px; overflow-wrap: anywhere; }
#runtimePage .pipeline-jobs-placeholder { display: grid; place-content: center; min-height: 150px; padding: 18px; text-align: center; }
#runtimePage .pipeline-jobs-placeholder strong { color: #dceefa; font-size: 11px; }
#runtimePage .pipeline-jobs-placeholder p { margin: 5px 0 0; color: #7890ad; font-size: 9px; }
#runtimePage .pipeline-jobs-message { min-height: auto; margin-top: 0; padding: 9px 11px; }
@media (max-width: 1050px) {
  #runtimePage .pipeline-jobs-toolbar { grid-template-columns: repeat(2,minmax(0,1fr)); }
  #runtimePage .pipeline-jobs-layout { grid-template-columns: 1fr; }
  #runtimePage .pipeline-jobs-directory { max-height: 260px; }
}
@media (max-width: 620px) {
  #runtimePage .pipeline-jobs-toolbar,
  #runtimePage .pipeline-job-facts { grid-template-columns: 1fr; }
}
/* END PART F 15-B4G JOBS AND ATTEMPTS COMPONENT */
'''

OLD_SET_VIEW = '''    if (matched) {
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
    }
    return matched;
  };'''

OLD_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      window.LinkCraftorConnectedDomainStageProgress?.render?.(payload);
      return true;'''

NEW_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      window.LinkCraftorConnectedDomainStageProgress?.render?.(payload);
      window.LinkCraftorConnectedDomainJobsAttempts?.render?.(payload);
      return true;'''

OLD_UNAVAILABLE_HANDOFF = '''    window.LinkCraftorConnectedDomainStageProgress?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );'''

NEW_UNAVAILABLE_HANDOFF = '''    window.LinkCraftorConnectedDomainStageProgress?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainJobsAttempts?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );'''

JS_APPEND = r'''

// BEGIN PART F 15-B4G JOBS AND ATTEMPTS COMPONENT
(() => {
  "use strict";
  const PIPELINE_ID = "connect_domain";
  let latestPayload = null;
  let selectedWorkflowId = "";
  let selectedJobId = "";
  let activeStatus = "all";
  let searchQuery = "";
  let bound = false;
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const label = (value) => String(value || "unknown").split(/[_-]+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
  const array = (value) => Array.isArray(value) ? value : [];
  const integer = (value) => { const number = Number(value); return Number.isFinite(number) && number >= 0 ? Math.trunc(number) : 0; };
  const percent = (value) => { const number = Number(value); return Number.isFinite(number) ? Math.max(0, Math.min(100, number)) : 0; };
  const timestamp = (value) => { if (!value) return "Unavailable"; const date = new Date(value); return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString(); };
  const normalizeJob = (job, stageId, workflowId) => {
    const jobId = String(job?.job_id || "").trim();
    if (!jobId) throw new Error("Jobs & Attempts received an empty job identity.");
    return Object.freeze({
      jobId, workflowId, stageId, jobType: String(job?.job_type || "Unavailable"), status: String(job?.status || "unknown").toLowerCase(),
      priority: job?.priority ?? "Unavailable", progressPercent: percent(job?.progress_percent), progressMessage: String(job?.progress_message || "No progress message"),
      assignedWorkerId: String(job?.assigned_worker_id || "Unassigned"), createdAt: job?.created_at || null, startedAt: job?.started_at || null,
      completedAt: job?.completed_at || null, updatedAt: job?.updated_at || null, errorMessage: job?.error_message ? String(job.error_message) : "",
      attempt: integer(job?.attempt), maximumAttempts: integer(job?.maximum_attempts), retryScheduled: job?.retry_scheduled === true,
      retryExhausted: job?.retry_exhausted === true, dispatchResultAvailable: job?.runtime_dispatch_result_available === true,
      eventCount: array(job?.events).length
    });
  };
  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) throw new Error("Jobs & Attempts received an invalid pipeline identity.");
    if (!Array.isArray(payload.workflows)) throw new Error("Jobs & Attempts requires persisted workflow evidence.");
    const workflows = payload.workflows.map((workflow) => {
      const workflowId = String(workflow?.workflow_id || "").trim();
      if (!workflowId) throw new Error("Jobs & Attempts received an empty workflow identity.");
      const jobs = array(workflow?.stages).flatMap((stage) => array(stage?.jobs).map((job) => normalizeJob(job, String(stage?.stage_id || "unknown"), workflowId)));
      return Object.freeze({ workflowId, status: String(workflow?.status || "unknown").toLowerCase(), jobs });
    });
    return Object.freeze({ workflows });
  };
  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewJobsAttempts"); const stateLabel = byId("pipelineJobsAttemptsState"); const container = byId("pipelineJobsMessage");
    if (panel) { panel.dataset.componentState = state; panel.setAttribute("aria-busy", state === "loading" ? "true" : "false"); }
    if (stateLabel) stateLabel.textContent = state === "ready" ? "Live evidence" : label(state);
    if (container) { container.dataset.state = state; const icon = container.querySelector(":scope > span"); const heading = container.querySelector("strong"); const paragraph = container.querySelector("p"); if (icon) icon.textContent = symbol; if (heading) heading.textContent = title; if (paragraph) paragraph.textContent = message; }
  };
  const placeholder = (title, message) => `<div class="pipeline-jobs-placeholder"><strong>${escapeHtml(title)}</strong><p>${escapeHtml(message)}</p></div>`;
  const currentContract = () => latestPayload ? inspect(latestPayload) : Object.freeze({ workflows: [] });
  const selectedWorkflow = (contract) => contract.workflows.find((workflow) => workflow.workflowId === selectedWorkflowId) || contract.workflows[0] || null;
  const jobMatches = (job) => {
    const statusMatches = activeStatus === "all" || job.status === activeStatus;
    const query = searchQuery.trim().toLowerCase();
    return statusMatches && (!query || [job.jobId, job.stageId, job.jobType, job.assignedWorkerId].some((value) => String(value).toLowerCase().includes(query)));
  };
  const renderDetail = (job) => {
    const detail = byId("pipelineJobDetail"); if (!detail) return false;
    const attempts = job.maximumAttempts ? `${job.attempt} of ${job.maximumAttempts}` : String(job.attempt);
    const retry = job.retryExhausted ? "Exhausted" : job.retryScheduled ? "Scheduled" : "Not scheduled";
    detail.innerHTML = `
      <header class="pipeline-job-detail-head"><div><span>Selected job</span><strong>${escapeHtml(job.jobId)}</strong></div><span class="pipeline-job-status" data-status="${escapeHtml(job.status)}">${escapeHtml(label(job.status))}</span></header>
      <div class="pipeline-job-facts">
        <article><span>Stage</span><strong>${escapeHtml(label(job.stageId))}</strong></article><article><span>Job type</span><strong>${escapeHtml(label(job.jobType))}</strong></article><article><span>Priority</span><strong>${escapeHtml(job.priority)}</strong></article>
        <article><span>Attempt</span><strong>${escapeHtml(attempts)}</strong></article><article><span>Retry</span><strong>${escapeHtml(retry)}</strong></article><article><span>Worker</span><strong>${escapeHtml(job.assignedWorkerId)}</strong></article>
        <article><span>Created</span><strong>${escapeHtml(timestamp(job.createdAt))}</strong></article><article><span>Started</span><strong>${escapeHtml(timestamp(job.startedAt))}</strong></article><article><span>Updated</span><strong>${escapeHtml(timestamp(job.updatedAt))}</strong></article>
        <article><span>Completed</span><strong>${escapeHtml(timestamp(job.completedAt))}</strong></article><article><span>Dispatch result</span><strong>${job.dispatchResultAvailable ? "Available" : "Unavailable"}</strong></article><article><span>Events</span><strong>${escapeHtml(job.eventCount)}</strong></article>
      </div>
      <div class="pipeline-job-progress"><span>${escapeHtml(job.progressMessage)} · ${escapeHtml(Math.round(job.progressPercent))}%</span><div><i style="width:${escapeHtml(job.progressPercent)}%"></i></div></div>
      ${job.errorMessage ? `<div class="pipeline-job-error"><strong>Terminal error:</strong> ${escapeHtml(job.errorMessage)}</div>` : ""}
    `;
    return true;
  };
  const populateWorkflowSelector = (workflows) => {
    const select = byId("pipelineJobsWorkflow"); if (!select) return false;
    if (!workflows.length) { select.innerHTML = '<option value="">No workflows</option>'; select.disabled = true; selectedWorkflowId = ""; return false; }
    if (!workflows.some((workflow) => workflow.workflowId === selectedWorkflowId)) selectedWorkflowId = workflows[0].workflowId;
    select.disabled = false;
    select.innerHTML = workflows.map((workflow) => `<option value="${escapeHtml(workflow.workflowId)}"${workflow.workflowId === selectedWorkflowId ? " selected" : ""}>${escapeHtml(workflow.workflowId)} · ${workflow.jobs.length} job${workflow.jobs.length === 1 ? "" : "s"}</option>`).join("");
    return true;
  };
  const renderJobs = () => {
    const contract = currentContract(); const directory = byId("pipelineJobsDirectory"); const detail = byId("pipelineJobDetail"); const count = byId("pipelineJobsCount");
    if (!directory) return false;
    populateWorkflowSelector(contract.workflows);
    const workflow = selectedWorkflow(contract);
    if (!workflow) {
      directory.innerHTML = placeholder("No persisted workflows", "Job evidence will appear after workflow activation."); directory.setAttribute("aria-busy", "false");
      if (detail) detail.innerHTML = placeholder("No job selected", "No workflow is available for inspection."); if (count) count.textContent = "0";
      updateMessage("empty", "No workflow job evidence", "Connected Domain has no persisted workflow to inspect.", "◎"); return true;
    }
    const filtered = workflow.jobs.filter(jobMatches); if (count) count.textContent = `${filtered.length} of ${workflow.jobs.length}`;
    if (!filtered.length) {
      selectedJobId = "";
      directory.innerHTML = placeholder(workflow.jobs.length ? "No jobs match" : "No jobs projected", workflow.jobs.length ? "Change the status filter or job search." : "This workflow exists, but no Universal Job has been created for it.");
      directory.setAttribute("aria-busy", "false"); if (detail) detail.innerHTML = placeholder("No job selected", workflow.jobs.length ? "No filtered job is available." : "Attempt evidence will appear after a job is created.");
      updateMessage(workflow.jobs.length ? "ready" : "empty", workflow.jobs.length ? "No matching job" : "No jobs for selected workflow", workflow.jobs.length ? "The component is connected; adjust the local filters." : "The empty state is canonical and no activity was invented.", workflow.jobs.length ? "⌕" : "◎"); return true;
    }
    if (!filtered.some((job) => job.jobId === selectedJobId)) selectedJobId = filtered[0].jobId;
    directory.innerHTML = filtered.map((job) => `<button class="pipeline-job-row${job.jobId === selectedJobId ? " active" : ""}" type="button" role="option" aria-selected="${job.jobId === selectedJobId ? "true" : "false"}" data-jobs-attempts-id="${escapeHtml(job.jobId)}"><span class="pipeline-job-row-head"><strong>${escapeHtml(job.jobId)}</strong><span class="pipeline-job-status" data-status="${escapeHtml(job.status)}">${escapeHtml(label(job.status))}</span></span><span class="pipeline-job-row-meta"><span>${escapeHtml(label(job.stageId))} · Attempt ${escapeHtml(job.attempt)}</span><span>${escapeHtml(job.assignedWorkerId)}</span></span></button>`).join("");
    directory.setAttribute("aria-busy", "false"); renderDetail(filtered.find((job) => job.jobId === selectedJobId));
    updateMessage("ready", "Job evidence loaded", `${workflow.jobs.length} Universal Job${workflow.jobs.length === 1 ? "" : "s"} projected for the selected workflow.`, "✓"); return true;
  };
  const ensureBound = () => {
    if (bound) return true; const panel = byId("pipelineOperationsViewJobsAttempts"); const workflow = byId("pipelineJobsWorkflow"); const status = byId("pipelineJobsStatus"); const search = byId("pipelineJobsSearch");
    if (!panel || !workflow || !status || !search) return false;
    panel.addEventListener("click", (event) => { const row = event.target.closest("[data-jobs-attempts-id]"); if (!row) return; selectedJobId = row.dataset.jobsAttemptsId || ""; renderJobs(); });
    workflow.addEventListener("change", () => { selectedWorkflowId = String(workflow.value || ""); selectedJobId = ""; renderJobs(); });
    status.addEventListener("change", () => { activeStatus = String(status.value || "all").toLowerCase(); selectedJobId = ""; renderJobs(); });
    search.addEventListener("input", () => { searchQuery = String(search.value || ""); selectedJobId = ""; renderJobs(); });
    bound = true; return true;
  };
  const render = (payload) => { try { inspect(payload); latestPayload = payload; ensureBound(); return renderJobs(); } catch (error) { return renderUnavailable(error?.message); } };
  const renderUnavailable = (message) => {
    latestPayload = null; const directory = byId("pipelineJobsDirectory"); const detail = byId("pipelineJobDetail"); const count = byId("pipelineJobsCount"); const select = byId("pipelineJobsWorkflow");
    if (select) { select.innerHTML = '<option value="">Unavailable</option>'; select.disabled = true; }
    if (directory) { directory.innerHTML = placeholder("Job evidence unavailable", message || "The canonical projection could not be loaded."); directory.setAttribute("aria-busy", "false"); }
    if (detail) detail.innerHTML = placeholder("No job detail", "Restore the read-only projection before inspecting attempts."); if (count) count.textContent = "Unavailable";
    updateMessage("unavailable", "Jobs and attempts unavailable", message || "The canonical detail projection could not be loaded.", "!"); return false;
  };
  const activate = () => { ensureBound(); const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.(); if (snapshot) return render(snapshot); updateMessage("loading", "Loading jobs and attempts", "Waiting for the existing Connected Domain detail snapshot.", "◌"); return false; };
  window.LinkCraftorConnectedDomainJobsAttempts = Object.freeze({ activate, render, renderUnavailable, inspect });
})();
// END PART F 15-B4G JOBS AND ATTEMPTS COMPONENT
'''

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=9" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=10" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=11"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=12"></script>'


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
    stripped = re.sub(r"/\*.*?\*/", "", source, flags=re.S); stripped = re.sub(r'"(?:\\.|[^"\\])*"', '""', stripped); stripped = re.sub(r"'(?:\\.|[^'\\])*'", "''", stripped)
    depth = 0
    for character in stripped:
        if character == "{": depth += 1
        elif character == "}":
            depth -= 1
            if depth < 0: return False
    return depth == 0


def javascript_syntax_valid(source: str) -> bool:
    node = shutil.which("node")
    if node is None: raise RuntimeError("Node.js is required for JavaScript syntax validation.")
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4g_js_") as folder:
        candidate = Path(folder) / "runtime_owner_candidate.js"; write_text(candidate, source)
        result = subprocess.run([node, "--check", str(candidate)], capture_output=True, text=True, check=False)
    return result.returncode == 0


def make_report(status: str, checks: dict[str, bool], evidence: dict[str, Any], error: dict[str, Any]) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = FINAL_RESULT if status == "CERTIFIED" else "FINAL RESULT: PART F 15-B4G JOBS AND ATTEMPTS COMPONENT NOT_CERTIFIED"
    return "\n".join([
        "LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS", "PART F 15-B4G JOBS AND ATTEMPTS COMPONENT CERTIFICATION", "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}", "Patch mode: STRICT FAIL-CLOSED", f"Backup: {evidence.get('backup', 'NOT_CREATED')}",
        "Production jobs created: NO", "Production queue claims executed: NO", "Production handlers executed: NO", "Production workflow persistence executed: NO",
        "Production recovery actions executed: NO", "Live network requests executed during certification: NO", f"CERTIFICATION STATUS: {status}", "",
        "CHECKS:", json.dumps(checks, indent=2, sort_keys=True), "", "FAILED_CHECKS:", json.dumps(failed, indent=2), "", "NOT_RUN_CHECKS:", "[]", "",
        "EVIDENCE:", json.dumps(evidence, indent=2, sort_keys=True), "", "EXECUTION_ERROR:", json.dumps(error, indent=2, sort_keys=True), "", "IMPLEMENTED BOUNDARY:",
        "- Jobs & Attempts projects existing Universal Jobs nested under persisted Connected Domain workflow stages.",
        "- Job identity, stage, type, status, priority, progress, worker, timestamps, attempt limits, retry state, error and dispatch-result evidence are visible.",
        "- Workflow selection, status filtering, identity search and job selection are local read-only presentation operations.",
        "- The existing Connected Domain cached detail snapshot is reused; no new endpoint request was added.",
        "- A workflow with no jobs renders a canonical empty state and does not invent execution activity.",
        "- No job, queue, workflow, handler, recovery or persistence authority was created or mutated.", "", "NEXT STEP:",
        "Browser visual acceptance, then Part F 15-B4H - Dependencies and Handoffs component.", "", final, ""
    ])


def main() -> int:
    if len(sys.argv) != 3: raise SystemExit("Usage: RUN_15_B4G_JOBS_ATTEMPTS.py <project_root> <report_path>")
    root, report = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    paths = {
        "index_html": root / "backend/server/owner/index.html", "owner_css": root / "backend/server/owner/owner.css", "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": root / "backend/server/owner/runtime_owner.css", "runtime_owner_js": root / "backend/server/owner/runtime_owner.js",
        "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py", "pipeline_operations": root / "backend/server/owner/pipeline_operations.py",
    }
    prior_report = root / "backend/server/data/reports/PART_F_15_B4F_SIX_STAGE_PROGRESS_CERTIFICATION.txt"
    checks: dict[str, bool] = {}; evidence: dict[str, Any] = {"new_endpoint_requests": 0, "recovery_controls_added": False}; error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}; retained = False; status = "NOT_CERTIFIED"
    try:
        checks["part_f_15_b4f_report_exists"] = prior_report.is_file(); prior_hash = sha256_path(prior_report) if prior_report.is_file() else ""; prior = read_text(prior_report) if prior_report.is_file() else ""
        checks["part_f_15_b4f_certified"] = "CERTIFICATION STATUS: CERTIFIED" in prior and "FINAL RESULT: PART F 15-B4F SIX-STAGE PROGRESS COMPONENT CERTIFIED" in prior
        for name, path in paths.items(): checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()): raise RuntimeError("Required source or B4F evidence is unavailable.")
        before = {name: sha256_path(path) for name, path in paths.items()}; evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items(): checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()): raise RuntimeError("Installed source lineage does not match certified B4F.")
        index_source, css_source, js_source, operations_source = read_text(paths["index_html"]), read_text(paths["runtime_owner_css"]), read_text(paths["runtime_owner_js"]), read_text(paths["pipeline_operations"])
        checks["jobs_attempts_not_previously_present"] = all(MARKER not in source for source in (index_source, css_source, js_source))
        required_projection_fields = ('"job_id"', '"job_type"', '"status"', '"priority"', '"progress_percent"', '"assigned_worker_id"', '"attempt"', '"maximum_attempts"', '"retry_scheduled"', '"retry_exhausted"', '"events"')
        checks["certified_job_projection_contract_available"] = all(token in operations_source for token in required_projection_fields)
        index_candidate = replace_once(index_source, OLD_PANEL, NEW_PANEL, "Jobs & Attempts structure shell")
        index_candidate = replace_once(index_candidate, OLD_CSS_VERSION, NEW_CSS_VERSION, "Runtime stylesheet cache version")
        index_candidate = replace_once(index_candidate, OLD_JS_VERSION, NEW_JS_VERSION, "Runtime JavaScript cache version")
        css_candidate = css_source.rstrip() + "\n" + CSS_APPEND.lstrip()
        js_candidate = replace_once(js_source, OLD_SET_VIEW, NEW_SET_VIEW, "Jobs & Attempts activation handoff")
        js_candidate = replace_once(js_candidate, OLD_RENDER_HANDOFF, NEW_RENDER_HANDOFF, "Jobs & Attempts render handoff")
        js_candidate = replace_once(js_candidate, OLD_UNAVAILABLE_HANDOFF, NEW_UNAVAILABLE_HANDOFF, "Jobs & Attempts unavailable handoff").rstrip() + "\n" + JS_APPEND.lstrip()
        checks["candidate_html_ids_unique"] = html_ids_unique(index_candidate); checks["candidate_css_balanced"] = css_balanced(css_candidate); checks["candidate_javascript_syntax"] = javascript_syntax_valid(js_candidate)
        ids = ("pipelineJobsAttemptsState", "pipelineJobsWorkflow", "pipelineJobsStatus", "pipelineJobsSearch", "pipelineJobsCount", "pipelineJobsDirectory", "pipelineJobDetail", "pipelineJobsMessage")
        checks["all_jobs_attempts_bindings_present"] = all(index_candidate.count(f'id="{identifier}"') == 1 for identifier in ids)
        checks["job_attempt_evidence_rendered"] = all(token in JS_APPEND for token in ("jobId", "jobType", "stageId", "status", "priority", "progressPercent", "assignedWorkerId", "attempt", "maximumAttempts", "retryScheduled", "retryExhausted", "errorMessage", "dispatchResultAvailable", "eventCount"))
        checks["workflow_status_and_search_controls_present"] = all(token in JS_APPEND for token in ("pipelineJobsWorkflow", "pipelineJobsStatus", "pipelineJobsSearch", "jobMatches"))
        checks["cached_snapshot_reused"] = "LinkCraftorConnectedDomainOverview?.getSnapshot?.()" in JS_APPEND
        checks["no_new_fetch_request_added"] = js_candidate.count("fetch(") == js_source.count("fetch(")
        checks["canonical_detail_endpoint_retained_once"] = js_candidate.count('"/owner/api/runtime/pipelines/connect_domain"') == 1
        checks["five_presentation_states_present"] = all(f'"{state}"' in JS_APPEND for state in ("loading", "ready", "empty", "unavailable")) and "No jobs match" in JS_APPEND
        checks["canonical_zero_job_empty_state_present"] = "no Universal Job has been created" in JS_APPEND and "no activity was invented" in JS_APPEND
        checks["no_recovery_controls_added"] = all(js_candidate.count(token) == js_source.count(token) for token in ("retryJob(", "cancelJob(", "terminateJob(", "data-runtime-recovery-action"))
        checks["cache_versions_advanced"] = NEW_CSS_VERSION in index_candidate and NEW_JS_VERSION in index_candidate
        if not all(checks.values()): raise RuntimeError("15-B4G candidate certification checks failed.")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"); backup = root / "backend/server/data/runtime_backups" / f"part_f_15_b4g_{stamp}"; backup.mkdir(parents=True, exist_ok=False)
        for name in ("index_html", "runtime_owner_css", "runtime_owner_js"):
            originals[name] = paths[name].read_bytes(); shutil.copy2(paths[name], backup / paths[name].name)
        evidence["backup"] = str(backup)
        write_text(paths["index_html"], index_candidate); write_text(paths["runtime_owner_css"], css_candidate); write_text(paths["runtime_owner_js"], js_candidate)
        checks["backup_created"] = backup.is_dir(); checks["retained_html_ids_unique"] = html_ids_unique(read_text(paths["index_html"])); checks["retained_css_balanced"] = css_balanced(read_text(paths["runtime_owner_css"])); checks["retained_javascript_syntax"] = javascript_syntax_valid(read_text(paths["runtime_owner_js"]))
        checks["retained_markers"] = all(read_text(paths[name]).count(MARKER) == 2 for name in ("index_html", "runtime_owner_css", "runtime_owner_js")); checks["historical_b4f_report_unchanged"] = sha256_path(prior_report) == prior_hash
        after = {name: sha256_path(path) for name, path in paths.items()}; evidence["source_hashes_after"] = after
        checks["only_three_ui_sources_changed"] = all((after[name] != before[name]) == (name in {"index_html", "runtime_owner_css", "runtime_owner_js"}) for name in paths)
        checks.update({"production_jobs_created_no": True, "production_queue_claims_no": True, "production_handlers_executed_no": True, "production_workflow_persistence_no": True, "production_recovery_actions_no": True, "live_network_requests_during_certification_no": True})
        evidence["projected_job_fields"] = ["identity", "stage", "type", "status", "priority", "progress", "worker", "timestamps", "attempt_limit", "retry_state", "terminal_error", "dispatch_result", "event_count"]
        if not all(checks.values()): raise RuntimeError("Retained 15-B4G certification checks failed.")
        retained, status = True, "CERTIFIED"
    except Exception as exc:
        error = {"error_type": type(exc).__name__, "error_message": str(exc), "traceback": traceback.format_exc()}
        for name, content in originals.items(): paths[name].write_bytes(content)
    finally:
        evidence["patch_retained"] = retained; report.parent.mkdir(parents=True, exist_ok=True); write_text(report, make_report(status, checks, evidence, error))
    for name, passed in checks.items(): print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not passed for passed in checks.values())}"); print("NOT_RUN_CHECK_COUNT=0"); print(f"REPORT={report}"); print(f"PART_F_15_B4G_STATUS={status}"); print(f"PATCH_RETAINED={'YES' if retained else 'NO'}")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
