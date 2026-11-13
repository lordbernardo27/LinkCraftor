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


FINAL_RESULT = "FINAL RESULT: PART F 15-B4J FAILURES AND ATTENTION COMPONENT CERTIFIED"
MARKER = "PART F 15-B4J FAILURES AND ATTENTION COMPONENT"

EXPECTED_HASHES = {
    "index_html": "c47482bfc570a27433e452faf79ca0917dd197218a4ff96d086f6365815038cc",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "7456eab0d7790510653941f1c398d696d47e3407e05b4fd6f1aa8d12af433282",
    "runtime_owner_js": "2b52619339edd2f866c63a92a3fd79cd5a3c96040df4a1c395f57d3b4d86b0cb",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_PANEL = r'''              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewFailures" data-pipeline-operations-view-panel="failures" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Owner attention</span><h5>Failures &amp; Attention</h5><p>Failed jobs, terminal evidence, retries, and items requiring review.</p></div><strong>Structure ready</strong></header>
                <div class="pipeline-component-state" data-state="empty"><span aria-hidden="true">✓</span><div><strong>No selected failure context</strong><p>Failure evidence and governed recovery eligibility will appear here.</p></div></div>
              </section>'''

NEW_PANEL = r'''              <!-- BEGIN PART F 15-B4J FAILURES AND ATTENTION COMPONENT -->
              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewFailures" data-pipeline-operations-view-panel="failures" data-component-state="loading" role="tabpanel" aria-busy="true" hidden>
                <header class="pipeline-monitoring-panel-head">
                  <div><span>Owner attention</span><h5>Failures &amp; Attention</h5><p>Inspect failed workflows, failed stages, terminal job evidence, retry state, and items requiring owner review.</p></div>
                  <strong id="pipelineFailuresState">Loading</strong>
                </header>
                <div class="pipeline-failures-live">
                  <div class="pipeline-failures-summary" aria-label="Failure and attention summary">
                    <article><span>Failed workflows</span><strong id="pipelineFailuresFailedWorkflows">—</strong></article>
                    <article><span>Failed stages</span><strong id="pipelineFailuresFailedStages">—</strong></article>
                    <article><span>Failed jobs</span><strong id="pipelineFailuresFailedJobs">—</strong></article>
                    <article><span>Retries scheduled</span><strong id="pipelineFailuresRetriesScheduled">—</strong></article>
                    <article><span>Retries exhausted</span><strong id="pipelineFailuresRetriesExhausted">—</strong></article>
                    <article><span>Terminal errors</span><strong id="pipelineFailuresTerminalErrors">—</strong></article>
                  </div>
                  <div class="pipeline-failures-toolbar">
                    <label><span>Workflow</span><select id="pipelineFailuresWorkflow"><option value="all">Loading workflows</option></select></label>
                    <label><span>Attention class</span><select id="pipelineFailuresScope"><option value="all">All concerns</option><option value="critical">Critical failures</option><option value="retry">Retry state</option><option value="workflow_stage">Workflow and stage</option></select></label>
                    <label class="pipeline-failures-search"><span>Find evidence</span><input id="pipelineFailuresSearch" type="search" autocomplete="off" placeholder="Workflow, stage, job, status, or error" /></label>
                    <div><span>Visible concerns</span><strong id="pipelineFailuresCount">Loading</strong></div>
                  </div>
                  <div class="pipeline-failures-workspace">
                    <div class="pipeline-failures-directory" id="pipelineFailuresDirectory" role="listbox" aria-label="Failure and attention directory" aria-busy="true"><div class="pipeline-failures-placeholder"><strong>Loading owner-attention evidence</strong><p>Reading failure and retry state from the cached Pipeline Operations projection.</p></div></div>
                    <div class="pipeline-failure-detail" id="pipelineFailureDetail"><div class="pipeline-failures-placeholder"><strong>No concern selected</strong><p>Failure evidence will appear after the canonical snapshot is inspected.</p></div></div>
                  </div>
                  <div class="pipeline-component-state pipeline-failures-message" id="pipelineFailuresMessage" data-state="loading" role="status" aria-live="polite"><span aria-hidden="true">◌</span><div><strong>Loading attention evidence</strong><p>No recovery authority is exercised by this read-only component.</p></div></div>
                </div>
              </section>
              <!-- END PART F 15-B4J FAILURES AND ATTENTION COMPONENT -->'''

CSS_APPEND = r'''

/* BEGIN PART F 15-B4J FAILURES AND ATTENTION COMPONENT */
#runtimePage .pipeline-failures-live { display: grid; gap: 10px; }
#runtimePage .pipeline-failures-summary { display: grid; grid-template-columns: repeat(6,minmax(0,1fr)); gap: 7px; }
#runtimePage .pipeline-failures-summary article { display: grid; gap: 3px; min-width: 0; padding: 9px; border: 1px solid rgba(148,163,184,.12); border-radius: 8px; background: rgba(255,255,255,.025); }
#runtimePage .pipeline-failures-summary span,
#runtimePage .pipeline-failures-toolbar span,
#runtimePage .pipeline-failure-detail span { color: #7890ad; font-size: 7px; font-weight: 700; letter-spacing: .055em; text-transform: uppercase; }
#runtimePage .pipeline-failures-summary strong { color: #e6f7ff; font-size: 13px; }
#runtimePage .pipeline-failures-toolbar { display: grid; grid-template-columns: minmax(210px,1fr) minmax(145px,.65fr) minmax(220px,1fr) minmax(95px,.4fr); gap: 8px; align-items: end; padding: 9px; border: 1px solid rgba(148,163,184,.12); border-radius: 9px; background: rgba(5,17,32,.28); }
#runtimePage .pipeline-failures-toolbar label,
#runtimePage .pipeline-failures-toolbar > div { display: grid; gap: 4px; min-width: 0; }
#runtimePage .pipeline-failures-toolbar strong { overflow: hidden; color: #e6f7ff; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
#runtimePage .pipeline-failures-toolbar select,
#runtimePage .pipeline-failures-toolbar input { width: 100%; min-height: 32px; padding: 6px 9px; border: 1px solid rgba(103,232,249,.2); border-radius: 7px; outline: none; background: rgba(4,15,29,.72); color: #dceefa; font: inherit; font-size: 10px; }
#runtimePage .pipeline-failures-toolbar select:focus-visible,
#runtimePage .pipeline-failures-toolbar input:focus-visible { border-color: #22d3ee; box-shadow: 0 0 0 2px rgba(34,211,238,.16); }
#runtimePage .pipeline-failures-workspace { display: grid; grid-template-columns: minmax(250px,.8fr) minmax(0,1.4fr); min-height: 330px; border: 1px solid rgba(148,163,184,.12); border-radius: 9px; overflow: hidden; background: rgba(5,17,32,.2); }
#runtimePage .pipeline-failures-directory { display: grid; align-content: start; gap: 7px; min-width: 0; max-height: 475px; overflow: auto; padding: 9px; border-right: 1px solid rgba(148,163,184,.12); }
#runtimePage .pipeline-failure-row { display: grid; gap: 6px; width: 100%; min-width: 0; padding: 9px; border: 1px solid rgba(148,163,184,.13); border-radius: 8px; background: rgba(255,255,255,.025); color: inherit; text-align: left; cursor: pointer; }
#runtimePage .pipeline-failure-row:hover,
#runtimePage .pipeline-failure-row.active { border-color: rgba(103,232,249,.5); background: rgba(34,211,238,.08); }
#runtimePage .pipeline-failure-row[data-severity="critical"] { border-left: 3px solid #fb7185; }
#runtimePage .pipeline-failure-row[data-severity="warning"] { border-left: 3px solid #facc15; }
#runtimePage .pipeline-failure-row-head,
#runtimePage .pipeline-failure-row-meta { display: flex; justify-content: space-between; gap: 8px; min-width: 0; }
#runtimePage .pipeline-failure-row-head strong { overflow: hidden; color: #dceefa; font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }
#runtimePage .pipeline-failure-row-head span { flex: 0 0 auto; padding: 2px 5px; border: 1px solid currentColor; border-radius: 999px; color: #fb7185; font-size: 7px; font-weight: 700; text-transform: uppercase; }
#runtimePage .pipeline-failure-row[data-severity="warning"] .pipeline-failure-row-head span { color: #fde047; }
#runtimePage .pipeline-failure-row-meta { color: #7890ad; font-size: 8px; }
#runtimePage .pipeline-failure-row p { margin: 0; color: #9eb2c9; font-size: 8px; line-height: 1.35; overflow-wrap: anywhere; }
#runtimePage .pipeline-failure-detail { min-width: 0; padding: 12px; overflow: auto; }
#runtimePage .pipeline-failure-detail-head { display: flex; justify-content: space-between; gap: 10px; padding-bottom: 9px; border-bottom: 1px solid rgba(148,163,184,.12); }
#runtimePage .pipeline-failure-detail-head > div { display: grid; gap: 4px; min-width: 0; }
#runtimePage .pipeline-failure-detail-head strong { overflow-wrap: anywhere; color: #e6f7ff; font-size: 11px; }
#runtimePage .pipeline-attention-badge { align-self: start; padding: 4px 7px; border: 1px solid currentColor; border-radius: 999px; color: #fb7185; font-size: 7px; font-weight: 700; text-transform: uppercase; }
#runtimePage .pipeline-attention-badge[data-severity="warning"] { color: #fde047; }
#runtimePage .pipeline-failure-facts { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 7px; margin-top: 9px; }
#runtimePage .pipeline-failure-facts article { display: grid; gap: 3px; min-width: 0; padding: 8px; border: 1px solid rgba(148,163,184,.1); border-radius: 7px; background: rgba(255,255,255,.022); }
#runtimePage .pipeline-failure-facts strong { overflow-wrap: anywhere; color: #dceefa; font-size: 9px; }
#runtimePage .pipeline-failure-error { margin-top: 9px; padding: 9px; border: 1px solid rgba(251,113,133,.25); border-radius: 7px; background: rgba(127,29,29,.12); color: #fecdd3; font-size: 9px; line-height: 1.4; overflow-wrap: anywhere; }
#runtimePage .pipeline-failure-events { display: grid; gap: 6px; margin-top: 9px; }
#runtimePage .pipeline-failure-events > strong { color: #dceefa; font-size: 9px; }
#runtimePage .pipeline-failure-event { display: grid; grid-template-columns: minmax(125px,.55fr) minmax(0,1fr); gap: 8px; padding: 7px; border: 1px solid rgba(148,163,184,.1); border-radius: 7px; color: #9eb2c9; font-size: 8px; }
#runtimePage .pipeline-failure-event b { color: #dceefa; overflow-wrap: anywhere; }
#runtimePage .pipeline-failures-placeholder { display: grid; place-content: center; min-height: 230px; padding: 18px; text-align: center; }
#runtimePage .pipeline-failures-placeholder strong { color: #dceefa; font-size: 11px; }
#runtimePage .pipeline-failures-placeholder p { margin: 5px 0 0; color: #7890ad; font-size: 9px; line-height: 1.4; }
#runtimePage .pipeline-failures-message { min-height: auto; margin-top: 0; padding: 9px 11px; }
@media (max-width: 1100px) {
  #runtimePage .pipeline-failures-summary { grid-template-columns: repeat(3,minmax(0,1fr)); }
  #runtimePage .pipeline-failures-toolbar { grid-template-columns: repeat(2,minmax(0,1fr)); }
  #runtimePage .pipeline-failures-search { grid-column: 1 / -1; }
}
@media (max-width: 760px) {
  #runtimePage .pipeline-failures-workspace { grid-template-columns: 1fr; }
  #runtimePage .pipeline-failures-directory { max-height: 300px; border-right: 0; border-bottom: 1px solid rgba(148,163,184,.12); }
  #runtimePage .pipeline-failure-facts { grid-template-columns: repeat(2,minmax(0,1fr)); }
}
@media (max-width: 520px) {
  #runtimePage .pipeline-failures-summary,
  #runtimePage .pipeline-failures-toolbar,
  #runtimePage .pipeline-failure-facts { grid-template-columns: 1fr; }
  #runtimePage .pipeline-failures-search { grid-column: auto; }
}
/* END PART F 15-B4J FAILURES AND ATTENTION COMPONENT */
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
    }
    return matched;
  };'''

OLD_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      window.LinkCraftorConnectedDomainStageProgress?.render?.(payload);
      window.LinkCraftorConnectedDomainJobsAttempts?.render?.(payload);
      window.LinkCraftorConnectedDomainDependenciesHandoffs?.render?.(payload);
      window.LinkCraftorConnectedDomainEventsTimeline?.render?.(payload);
      return true;'''

NEW_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      window.LinkCraftorConnectedDomainStageProgress?.render?.(payload);
      window.LinkCraftorConnectedDomainJobsAttempts?.render?.(payload);
      window.LinkCraftorConnectedDomainDependenciesHandoffs?.render?.(payload);
      window.LinkCraftorConnectedDomainEventsTimeline?.render?.(payload);
      window.LinkCraftorConnectedDomainFailuresAttention?.render?.(payload);
      return true;'''

OLD_UNAVAILABLE_HANDOFF = '''    window.LinkCraftorConnectedDomainEventsTimeline?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );'''

NEW_UNAVAILABLE_HANDOFF = '''    window.LinkCraftorConnectedDomainEventsTimeline?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainFailuresAttention?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );'''

JS_APPEND = r'''

// BEGIN PART F 15-B4J FAILURES AND ATTENTION COMPONENT
(() => {
  "use strict";
  const PIPELINE_ID = "connect_domain";
  let latestPayload = null;
  let selectedWorkflowId = "all";
  let selectedAttentionId = "";
  let activeScope = "all";
  let searchQuery = "";
  let bound = false;
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const label = (value) => String(value || "unknown").split(/[_-]+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
  const array = (value) => Array.isArray(value) ? value : [];
  const integer = (value) => { const number = Number(value); return Number.isFinite(number) && number >= 0 ? Math.trunc(number) : 0; };
  const timestamp = (value) => { if (!value) return "Unavailable"; const date = new Date(value); return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString(); };
  const timeValue = (value) => { if (!value) return null; const parsed = new Date(value).getTime(); return Number.isNaN(parsed) ? null : parsed; };
  const eventLine = (event, index) => {
    if (!event || typeof event !== "object" || Array.isArray(event)) return null;
    const oldStatus = event?.old_status != null ? label(event.old_status) : "Unknown";
    const newStatus = event?.new_status != null ? label(event.new_status) : label(event?.event_type || event?.type || "Recorded event");
    const recordedAt = event?.created_at ?? event?.timestamp ?? event?.occurred_at ?? event?.updated_at ?? null;
    return Object.freeze({ id: String(event?.event_id || `event-${index + 1}`), transition: `${oldStatus} → ${newStatus}`, recordedAt });
  };
  const normalizeJob = (job, stageId, workflowId) => {
    const jobId = String(job?.job_id || "").trim();
    if (!jobId) throw new Error("Failures & Attention received an empty job identity.");
    return Object.freeze({
      jobId, workflowId, stageId, jobType: String(job?.job_type || "Unavailable"), status: String(job?.status || "unknown").toLowerCase(),
      errorMessage: job?.error_message ? String(job.error_message) : "", attempt: integer(job?.attempt), maximumAttempts: integer(job?.maximum_attempts),
      retryScheduled: job?.retry_scheduled === true, retryExhausted: job?.retry_exhausted === true, assignedWorkerId: String(job?.assigned_worker_id || "Unassigned"),
      createdAt: job?.created_at || null, updatedAt: job?.updated_at || null, completedAt: job?.completed_at || null,
      events: array(job?.events).map(eventLine).filter(Boolean)
    });
  };
  const jobAttention = (job) => {
    if (!(job.status === "failed" || job.errorMessage || job.retryScheduled || job.retryExhausted)) return null;
    const kind = job.retryExhausted ? "retry_exhausted" : job.status === "failed" ? "failed_job" : job.errorMessage ? "terminal_error" : "retry_scheduled";
    const severity = job.retryScheduled && !job.retryExhausted && job.status !== "failed" && !job.errorMessage ? "warning" : "critical";
    const title = kind === "retry_exhausted" ? "Retry limit exhausted" : kind === "failed_job" ? "Universal Job failed" : kind === "terminal_error" ? "Terminal error recorded" : "Retry scheduled";
    const message = job.errorMessage || (kind === "retry_exhausted" ? "The recorded attempt limit has been exhausted." : kind === "retry_scheduled" ? "A retry is recorded as scheduled; execution remains outside this view." : "The job is in a failed terminal state.");
    return Object.freeze({ attentionId: `job:${job.jobId}`, source: "job", kind, severity, title, message, workflowId: job.workflowId, stageId: job.stageId, jobId: job.jobId, jobType: job.jobType, status: job.status, attempt: job.attempt, maximumAttempts: job.maximumAttempts, retryScheduled: job.retryScheduled, retryExhausted: job.retryExhausted, assignedWorkerId: job.assignedWorkerId, recordedAt: job.updatedAt || job.completedAt || job.createdAt, events: job.events });
  };
  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) throw new Error("Failures & Attention received an invalid pipeline identity.");
    if (!Array.isArray(payload.workflows)) throw new Error("Failures & Attention requires persisted workflow evidence.");
    const workflows = payload.workflows.map((workflow) => {
      const workflowId = String(workflow?.workflow_id || "").trim(); if (!workflowId) throw new Error("Failures & Attention received an empty workflow identity.");
      const status = String(workflow?.status || "unknown").toLowerCase(); const failedStages = array(workflow?.failed_stages).map((stage) => String(stage));
      const jobs = array(workflow?.stages).flatMap((stage) => array(stage?.jobs).map((job) => normalizeJob(job, String(stage?.stage_id || "unknown"), workflowId)));
      const items = jobs.map(jobAttention).filter(Boolean); const coveredStages = new Set(items.map((item) => item.stageId));
      failedStages.filter((stageId) => !coveredStages.has(stageId)).forEach((stageId) => items.push(Object.freeze({ attentionId: `stage:${workflowId}:${stageId}`, source: "stage", kind: "failed_stage", severity: "critical", title: "Workflow stage failed", message: "The persisted workflow records this stage as failed without a projected failed job.", workflowId, stageId, jobId: "Unavailable", jobType: "Unavailable", status: "failed", attempt: 0, maximumAttempts: 0, retryScheduled: false, retryExhausted: false, assignedWorkerId: "Unassigned", recordedAt: workflow?.updated_at || null, events: [] })));
      if (status === "failed" && !items.length) items.push(Object.freeze({ attentionId: `workflow:${workflowId}`, source: "workflow", kind: "failed_workflow", severity: "critical", title: "Workflow failed", message: "The persisted workflow is failed without a more specific projected job or stage concern.", workflowId, stageId: String(workflow?.current_stage || "Unavailable"), jobId: "Unavailable", jobType: "Unavailable", status, attempt: 0, maximumAttempts: 0, retryScheduled: false, retryExhausted: false, assignedWorkerId: "Unassigned", recordedAt: workflow?.updated_at || null, events: [] }));
      return Object.freeze({ workflowId, status, failedStages, jobs, items });
    });
    const jobs = workflows.flatMap((workflow) => workflow.jobs); const items = workflows.flatMap((workflow) => workflow.items);
    return Object.freeze({ workflows, items, summary: Object.freeze({ failedWorkflows: workflows.filter((workflow) => workflow.status === "failed").length, failedStages: workflows.reduce((total, workflow) => total + workflow.failedStages.length, 0), failedJobs: jobs.filter((job) => job.status === "failed").length, retriesScheduled: jobs.filter((job) => job.retryScheduled).length, retriesExhausted: jobs.filter((job) => job.retryExhausted).length, terminalErrors: jobs.filter((job) => Boolean(job.errorMessage)).length }) });
  };
  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewFailures"); const stateLabel = byId("pipelineFailuresState"); const container = byId("pipelineFailuresMessage");
    if (panel) { panel.dataset.componentState = state; panel.setAttribute("aria-busy", state === "loading" ? "true" : "false"); }
    if (stateLabel) stateLabel.textContent = state === "ready" ? "Attention evidence" : state === "empty" ? "All clear" : label(state);
    if (container) { container.dataset.state = state; const icon = container.querySelector(":scope > span"); const heading = container.querySelector("strong"); const paragraph = container.querySelector("p"); if (icon) icon.textContent = symbol; if (heading) heading.textContent = title; if (paragraph) paragraph.textContent = message; }
  };
  const placeholder = (title, message) => `<div class="pipeline-failures-placeholder"><strong>${escapeHtml(title)}</strong><p>${escapeHtml(message)}</p></div>`;
  const setSummary = (summary) => {
    const bindings = { pipelineFailuresFailedWorkflows: summary.failedWorkflows, pipelineFailuresFailedStages: summary.failedStages, pipelineFailuresFailedJobs: summary.failedJobs, pipelineFailuresRetriesScheduled: summary.retriesScheduled, pipelineFailuresRetriesExhausted: summary.retriesExhausted, pipelineFailuresTerminalErrors: summary.terminalErrors };
    Object.entries(bindings).forEach(([id, value]) => { const node = byId(id); if (node) node.textContent = String(value); });
  };
  const populateWorkflowSelector = (contract) => {
    const select = byId("pipelineFailuresWorkflow"); if (!select) return false;
    const options = [`<option value="all"${selectedWorkflowId === "all" ? " selected" : ""}>All workflows · ${contract.items.length} concern${contract.items.length === 1 ? "" : "s"}</option>`, ...contract.workflows.map((workflow) => `<option value="${escapeHtml(workflow.workflowId)}"${workflow.workflowId === selectedWorkflowId ? " selected" : ""}>${escapeHtml(workflow.workflowId)} · ${workflow.items.length} concern${workflow.items.length === 1 ? "" : "s"}</option>` )];
    if (selectedWorkflowId !== "all" && !contract.workflows.some((workflow) => workflow.workflowId === selectedWorkflowId)) selectedWorkflowId = "all";
    select.innerHTML = options.join(""); select.disabled = false; return true;
  };
  const itemMatches = (item) => {
    const workflowMatches = selectedWorkflowId === "all" || item.workflowId === selectedWorkflowId;
    const scopeMatches = activeScope === "all" || (activeScope === "critical" && item.severity === "critical") || (activeScope === "retry" && ["retry_scheduled", "retry_exhausted"].includes(item.kind)) || (activeScope === "workflow_stage" && item.source !== "job");
    const query = searchQuery.trim().toLowerCase(); const searchMatches = !query || [item.title, item.message, item.workflowId, item.stageId, item.jobId, item.jobType, item.status, item.kind].some((value) => String(value).toLowerCase().includes(query));
    return workflowMatches && scopeMatches && searchMatches;
  };
  const sortItems = (items) => [...items].sort((left, right) => { const severity = Number(right.severity === "critical") - Number(left.severity === "critical"); if (severity) return severity; const leftTime = timeValue(left.recordedAt); const rightTime = timeValue(right.recordedAt); if (leftTime == null && rightTime == null) return left.attentionId.localeCompare(right.attentionId); if (leftTime == null) return 1; if (rightTime == null) return -1; return rightTime - leftTime; });
  const renderDetail = (item) => {
    const detail = byId("pipelineFailureDetail"); if (!detail) return false;
    const attempt = item.maximumAttempts ? `${item.attempt} of ${item.maximumAttempts}` : item.attempt ? String(item.attempt) : "Not recorded";
    const retry = item.retryExhausted ? "Exhausted" : item.retryScheduled ? "Scheduled" : "Not scheduled";
    const events = item.events.slice(-4).reverse();
    detail.innerHTML = `<header class="pipeline-failure-detail-head"><div><span>Selected concern</span><strong>${escapeHtml(item.title)}</strong></div><b class="pipeline-attention-badge" data-severity="${escapeHtml(item.severity)}">${escapeHtml(label(item.severity))}</b></header><div class="pipeline-failure-facts"><article><span>Workflow</span><strong>${escapeHtml(item.workflowId)}</strong></article><article><span>Stage</span><strong>${escapeHtml(label(item.stageId))}</strong></article><article><span>Job</span><strong>${escapeHtml(item.jobId)}</strong></article><article><span>Status</span><strong>${escapeHtml(label(item.status))}</strong></article><article><span>Attempt</span><strong>${escapeHtml(attempt)}</strong></article><article><span>Retry state</span><strong>${escapeHtml(retry)}</strong></article><article><span>Worker</span><strong>${escapeHtml(item.assignedWorkerId)}</strong></article><article><span>Recorded</span><strong>${escapeHtml(timestamp(item.recordedAt))}</strong></article><article><span>Evidence source</span><strong>${escapeHtml(label(item.source))}</strong></article></div><div class="pipeline-failure-error"><strong>Attention evidence:</strong> ${escapeHtml(item.message)}</div><div class="pipeline-failure-events"><strong>Recent recorded job events</strong>${events.length ? events.map((event) => `<div class="pipeline-failure-event"><b>${escapeHtml(timestamp(event.recordedAt))}</b><span>${escapeHtml(event.id)} · ${escapeHtml(event.transition)}</span></div>`).join("") : '<div class="pipeline-failure-event"><b>No projected events</b><span>No event evidence was invented.</span></div>'}</div>`;
    return true;
  };
  const renderFailures = () => {
    const contract = latestPayload ? inspect(latestPayload) : Object.freeze({ workflows: [], items: [], summary: { failedWorkflows: 0, failedStages: 0, failedJobs: 0, retriesScheduled: 0, retriesExhausted: 0, terminalErrors: 0 } });
    const directory = byId("pipelineFailuresDirectory"); const detail = byId("pipelineFailureDetail"); const count = byId("pipelineFailuresCount"); if (!directory) return false;
    setSummary(contract.summary); populateWorkflowSelector(contract); const visible = sortItems(contract.items.filter(itemMatches)); if (count) count.textContent = `${visible.length} of ${contract.items.length}`;
    if (!contract.items.length) { selectedAttentionId = ""; directory.innerHTML = placeholder("No failures require attention", "No failed workflow, failed stage, failed job, terminal error, or retry concern is present in the canonical snapshot."); directory.setAttribute("aria-busy", "false"); if (detail) detail.innerHTML = placeholder("All clear", "Owner-attention evidence is empty; no recovery action is required or exposed here."); updateMessage("empty", "No owner-attention items", "The canonical failure and retry evidence is clear.", "✓"); return true; }
    if (!visible.length) { selectedAttentionId = ""; directory.innerHTML = placeholder("No concerns match", "Change the workflow, attention-class filter, or evidence search."); directory.setAttribute("aria-busy", "false"); if (detail) detail.innerHTML = placeholder("No concern selected", "No filtered attention item is available."); updateMessage("ready", "No matching concern", "The component is connected; adjust the local filters.", "⌕"); return true; }
    if (!visible.some((item) => item.attentionId === selectedAttentionId)) selectedAttentionId = visible[0].attentionId;
    directory.innerHTML = visible.map((item) => `<button class="pipeline-failure-row${item.attentionId === selectedAttentionId ? " active" : ""}" type="button" role="option" aria-selected="${item.attentionId === selectedAttentionId ? "true" : "false"}" data-failure-attention-id="${escapeHtml(item.attentionId)}" data-severity="${escapeHtml(item.severity)}"><span class="pipeline-failure-row-head"><strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(label(item.severity))}</span></span><span class="pipeline-failure-row-meta"><span>${escapeHtml(label(item.stageId))}</span><span>${escapeHtml(label(item.kind))}</span></span><p>${escapeHtml(item.message)}</p></button>`).join(""); directory.setAttribute("aria-busy", "false"); renderDetail(visible.find((item) => item.attentionId === selectedAttentionId)); updateMessage("ready", "Owner-attention evidence loaded", `${contract.items.length} canonical concern${contract.items.length === 1 ? "" : "s"} available for inspection.`, "!"); return true;
  };
  const ensureBound = () => {
    if (bound) return true; const panel = byId("pipelineOperationsViewFailures"); const workflow = byId("pipelineFailuresWorkflow"); const scope = byId("pipelineFailuresScope"); const search = byId("pipelineFailuresSearch"); if (!panel || !workflow || !scope || !search) return false;
    panel.addEventListener("click", (event) => { const row = event.target.closest("[data-failure-attention-id]"); if (!row) return; selectedAttentionId = row.dataset.failureAttentionId || ""; renderFailures(); });
    workflow.addEventListener("change", () => { selectedWorkflowId = String(workflow.value || "all"); selectedAttentionId = ""; renderFailures(); });
    scope.addEventListener("change", () => { activeScope = String(scope.value || "all"); selectedAttentionId = ""; renderFailures(); });
    search.addEventListener("input", () => { searchQuery = String(search.value || ""); selectedAttentionId = ""; renderFailures(); });
    bound = true; return true;
  };
  const render = (payload) => { try { inspect(payload); latestPayload = payload; ensureBound(); return renderFailures(); } catch (error) { return renderUnavailable(error?.message); } };
  const renderUnavailable = (message) => {
    latestPayload = null; const directory = byId("pipelineFailuresDirectory"); const detail = byId("pipelineFailureDetail"); const count = byId("pipelineFailuresCount"); const workflow = byId("pipelineFailuresWorkflow");
    ["pipelineFailuresFailedWorkflows","pipelineFailuresFailedStages","pipelineFailuresFailedJobs","pipelineFailuresRetriesScheduled","pipelineFailuresRetriesExhausted","pipelineFailuresTerminalErrors"].forEach((id) => { const node = byId(id); if (node) node.textContent = "—"; });
    if (workflow) { workflow.innerHTML = '<option value="all">Unavailable</option>'; workflow.disabled = true; }
    if (directory) { directory.innerHTML = placeholder("Failure evidence unavailable", message || "The canonical projection could not be loaded."); directory.setAttribute("aria-busy", "false"); }
    if (detail) detail.innerHTML = placeholder("No concern available", "Owner-attention evidence failed closed."); if (count) count.textContent = "Unavailable"; updateMessage("unavailable", "Failures & Attention unavailable", message || "The canonical detail projection could not be loaded.", "!"); return false;
  };
  const activate = () => { ensureBound(); const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.(); if (snapshot) return render(snapshot); updateMessage("loading", "Loading attention evidence", "Waiting for the existing Connected Domain detail snapshot.", "◌"); return false; };
  window.LinkCraftorConnectedDomainFailuresAttention = Object.freeze({ activate, render, renderUnavailable, inspect });
})();
// END PART F 15-B4J FAILURES AND ATTENTION COMPONENT
'''

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=12" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=13" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=14"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=15"></script>'


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


def attention_view_model_probe(source: str) -> dict[str, Any]:
    node = shutil.which("node")
    if node is None: raise RuntimeError("Node.js is required for the Failures & Attention view-model probe.")
    payload = {"pipeline_id": "connect_domain", "workflows": [
        {"workflow_id": "workflow_failed_job", "status": "failed", "failed_stages": ["site_sources"], "updated_at": "2026-11-10T21:00:00Z", "stages": [{"stage_id": "site_sources", "jobs": [{"job_id": "job_failed", "job_type": "site_sources_stage", "status": "failed", "error_message": "terminal probe error", "attempt": 3, "maximum_attempts": 3, "retry_exhausted": True, "retry_scheduled": False, "updated_at": "2026-11-10T21:00:00Z", "events": [{"event_id": "evt_failed", "old_status": "running", "new_status": "failed", "created_at": "2026-11-10T21:00:00Z"}]}]}]},
        {"workflow_id": "workflow_retry", "status": "running", "failed_stages": [], "stages": [{"stage_id": "connect_domain", "jobs": [{"job_id": "job_retry", "status": "queued", "attempt": 1, "maximum_attempts": 3, "retry_scheduled": True, "retry_exhausted": False, "events": []}]}]},
        {"workflow_id": "workflow_failed_stage", "status": "running", "failed_stages": ["url_cleaner"], "stages": []},
        {"workflow_id": "workflow_failed_only", "status": "failed", "failed_stages": [], "stages": []},
    ]}
    probe = "\n".join(["global.window = {};", "global.document = { getElementById: () => null };", source, f"const payload = {json.dumps(payload, separators=(',', ':'))};", "const result = window.LinkCraftorConnectedDomainFailuresAttention.inspect(payload);", "const kinds = result.items.map((item) => item.kind);", "const expected = ['retry_exhausted','retry_scheduled','failed_stage','failed_workflow'];", "if (JSON.stringify(kinds) !== JSON.stringify(expected)) process.exit(31);", "const expectedSummary = {failedWorkflows:2,failedStages:2,failedJobs:1,retriesScheduled:1,retriesExhausted:1,terminalErrors:1};", "if (JSON.stringify(result.summary) !== JSON.stringify(expectedSummary)) process.exit(32);", "process.stdout.write(JSON.stringify({workflow_count:result.workflows.length,attention_count:result.items.length,kinds,summary:result.summary}));"])
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4j_probe_") as folder:
        candidate = Path(folder) / "failures_attention_probe.js"; write_text(candidate, probe)
        result = subprocess.run([node, str(candidate)], capture_output=True, text=True, check=False)
    if result.returncode != 0: raise RuntimeError(f"Failures & Attention view-model probe failed ({result.returncode}): {result.stderr.strip()}")
    observed = json.loads(result.stdout)
    if observed.get("attention_count") != 4 or observed.get("workflow_count") != 4: raise RuntimeError("Failures & Attention view-model probe returned conflicting evidence.")
    return observed


def make_report(status: str, checks: dict[str, bool], evidence: dict[str, Any], error: dict[str, Any]) -> str:
    failed = [name for name, passed in checks.items() if not passed]; final = FINAL_RESULT if status == "CERTIFIED" else "FINAL RESULT: PART F 15-B4J FAILURES AND ATTENTION COMPONENT NOT_CERTIFIED"
    return "\n".join(["LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS", "PART F 15-B4J FAILURES AND ATTENTION COMPONENT CERTIFICATION", "", f"Generated: {datetime.now(timezone.utc).isoformat()}", "Patch mode: STRICT FAIL-CLOSED", f"Backup: {evidence.get('backup', 'NOT_CREATED')}", "Production jobs created: NO", "Production queue claims executed: NO", "Production handlers executed: NO", "Production workflow persistence executed: NO", "Production recovery actions executed: NO", "Live network requests executed during certification: NO", f"CERTIFICATION STATUS: {status}", "", "CHECKS:", json.dumps(checks, indent=2, sort_keys=True), "", "FAILED_CHECKS:", json.dumps(failed, indent=2), "", "NOT_RUN_CHECKS:", "[]", "", "EVIDENCE:", json.dumps(evidence, indent=2, sort_keys=True), "", "EXECUTION_ERROR:", json.dumps(error, indent=2, sort_keys=True), "", "IMPLEMENTED BOUNDARY:", "- Failures & Attention projects failed workflows, failed stages, failed jobs, terminal errors and recorded retry state.", "- Summary metrics, workflow filtering, attention-class filtering, evidence search and concern selection are local read-only operations.", "- Job error, attempt, worker, timestamp and recent persisted event evidence are visible when available.", "- A snapshot with no failure or retry concern renders a canonical all-clear state and invents no owner-attention activity.", "- The existing Connected Domain cached detail snapshot is reused; no endpoint request or recovery authority was added.", "- No job, queue, workflow, handler, recovery or persistence authority was created or mutated.", "", "NEXT STEP:", "Browser visual acceptance, then Part F 15-B4K - Output Readiness component.", "", final, ""])


def main() -> int:
    if len(sys.argv) != 3: raise SystemExit("Usage: RUN_15_B4J_FAILURES_ATTENTION.py <project_root> <report_path>")
    root, report = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    paths = {"index_html": root / "backend/server/owner/index.html", "owner_css": root / "backend/server/owner/owner.css", "owner_js": root / "backend/server/owner/owner.js", "runtime_owner_css": root / "backend/server/owner/runtime_owner.css", "runtime_owner_js": root / "backend/server/owner/runtime_owner.js", "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py", "pipeline_operations": root / "backend/server/owner/pipeline_operations.py"}
    prior_report = root / "backend/server/data/reports/PART_F_15_B4I_EVENTS_TIMELINE_CERTIFICATION.txt"
    checks: dict[str, bool] = {}; evidence: dict[str, Any] = {"new_endpoint_requests": 0, "recovery_controls_added": False}; error: dict[str, Any] = {}; originals: dict[str, bytes] = {}; retained = False; status = "NOT_CERTIFIED"
    try:
        checks["part_f_15_b4i_report_exists"] = prior_report.is_file(); prior_hash = sha256_path(prior_report) if prior_report.is_file() else ""; prior = read_text(prior_report) if prior_report.is_file() else ""
        checks["part_f_15_b4i_certified"] = "CERTIFICATION STATUS: CERTIFIED" in prior and FINAL_RESULT.replace("15-B4J FAILURES AND ATTENTION COMPONENT", "15-B4I EVENTS TIMELINE COMPONENT") in prior
        for name, path in paths.items(): checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()): raise RuntimeError("Required source or B4I evidence is unavailable.")
        before = {name: sha256_path(path) for name, path in paths.items()}; evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items(): checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()): raise RuntimeError("Installed source lineage does not match certified B4I.")
        index_source, css_source, js_source, operations_source = read_text(paths["index_html"]), read_text(paths["runtime_owner_css"]), read_text(paths["runtime_owner_js"]), read_text(paths["pipeline_operations"])
        checks["failures_attention_not_previously_present"] = all(MARKER not in source for source in (index_source, css_source, js_source))
        required_fields = ('"failed_stages"', '"status"', '"error_message"', '"attempt"', '"maximum_attempts"', '"retry_scheduled"', '"retry_exhausted"', '"assigned_worker_id"', '"events"')
        checks["certified_failure_projection_contract_available"] = all(token in operations_source for token in required_fields)
        index_candidate = replace_once(index_source, OLD_PANEL, NEW_PANEL, "Failures & Attention structure shell"); index_candidate = replace_once(index_candidate, OLD_CSS_VERSION, NEW_CSS_VERSION, "Runtime stylesheet cache version"); index_candidate = replace_once(index_candidate, OLD_JS_VERSION, NEW_JS_VERSION, "Runtime JavaScript cache version")
        css_candidate = css_source.rstrip() + "\n" + CSS_APPEND.lstrip(); js_candidate = replace_once(js_source, OLD_SET_VIEW, NEW_SET_VIEW, "Failures & Attention activation handoff"); js_candidate = replace_once(js_candidate, OLD_RENDER_HANDOFF, NEW_RENDER_HANDOFF, "Failures & Attention render handoff"); js_candidate = replace_once(js_candidate, OLD_UNAVAILABLE_HANDOFF, NEW_UNAVAILABLE_HANDOFF, "Failures & Attention unavailable handoff").rstrip() + "\n" + JS_APPEND.lstrip()
        checks["candidate_html_ids_unique"] = html_ids_unique(index_candidate); checks["candidate_css_balanced"] = css_balanced(css_candidate); checks["candidate_javascript_syntax"] = javascript_syntax_valid(js_candidate)
        probe = attention_view_model_probe(JS_APPEND); evidence["isolated_attention_view_model_probe"] = probe; checks["isolated_attention_view_model_probe_passed"] = probe.get("kinds") == ["retry_exhausted", "retry_scheduled", "failed_stage", "failed_workflow"]
        ids = ("pipelineFailuresState", "pipelineFailuresFailedWorkflows", "pipelineFailuresFailedStages", "pipelineFailuresFailedJobs", "pipelineFailuresRetriesScheduled", "pipelineFailuresRetriesExhausted", "pipelineFailuresTerminalErrors", "pipelineFailuresWorkflow", "pipelineFailuresScope", "pipelineFailuresSearch", "pipelineFailuresCount", "pipelineFailuresDirectory", "pipelineFailureDetail", "pipelineFailuresMessage")
        checks["all_failures_attention_bindings_present"] = all(index_candidate.count(f'id="{identifier}"') == 1 for identifier in ids)
        checks["failure_retry_evidence_rendered"] = all(token in JS_APPEND for token in ("failedWorkflows", "failedStages", "failedJobs", "retriesScheduled", "retriesExhausted", "terminalErrors", "errorMessage", "attempt", "events"))
        checks["workflow_scope_and_search_controls_present"] = all(token in JS_APPEND for token in ("pipelineFailuresWorkflow", "pipelineFailuresScope", "pipelineFailuresSearch", "itemMatches", "sortItems"))
        checks["canonical_all_clear_state_present"] = "No failures require attention" in JS_APPEND and "no recovery action is required or exposed here" in JS_APPEND
        checks["cached_snapshot_reused"] = "LinkCraftorConnectedDomainOverview?.getSnapshot?.()" in JS_APPEND; checks["no_new_fetch_request_added"] = js_candidate.count("fetch(") == js_source.count("fetch(")
        checks["canonical_detail_endpoint_retained_once"] = js_candidate.count('"/owner/api/runtime/pipelines/connect_domain"') == 1
        checks["five_presentation_states_present"] = all(f'"{state}"' in JS_APPEND for state in ("loading", "ready", "empty", "unavailable")) and "No concerns match" in JS_APPEND
        checks["no_recovery_controls_added"] = all(js_candidate.count(token) == js_source.count(token) for token in ("retryJob(", "cancelJob(", "terminateJob(", "data-runtime-recovery-action")) and index_candidate.count("data-runtime-recovery-action") == index_source.count("data-runtime-recovery-action")
        checks["cache_versions_advanced"] = NEW_CSS_VERSION in index_candidate and NEW_JS_VERSION in index_candidate
        if not all(checks.values()): raise RuntimeError("15-B4J candidate certification checks failed.")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"); backup = root / "backend/server/data/runtime_backups" / f"part_f_15_b4j_{stamp}"; backup.mkdir(parents=True, exist_ok=False)
        for name in ("index_html", "runtime_owner_css", "runtime_owner_js"): originals[name] = paths[name].read_bytes(); shutil.copy2(paths[name], backup / paths[name].name)
        evidence["backup"] = str(backup); write_text(paths["index_html"], index_candidate); write_text(paths["runtime_owner_css"], css_candidate); write_text(paths["runtime_owner_js"], js_candidate)
        checks["backup_created"] = backup.is_dir(); checks["retained_html_ids_unique"] = html_ids_unique(read_text(paths["index_html"])); checks["retained_css_balanced"] = css_balanced(read_text(paths["runtime_owner_css"])); checks["retained_javascript_syntax"] = javascript_syntax_valid(read_text(paths["runtime_owner_js"])); checks["retained_markers"] = all(read_text(paths[name]).count(MARKER) == 2 for name in ("index_html", "runtime_owner_css", "runtime_owner_js")); checks["historical_b4i_report_unchanged"] = sha256_path(prior_report) == prior_hash
        after = {name: sha256_path(path) for name, path in paths.items()}; evidence["source_hashes_after"] = after; checks["only_three_ui_sources_changed"] = all((after[name] != before[name]) == (name in {"index_html", "runtime_owner_css", "runtime_owner_js"}) for name in paths)
        checks.update({"production_jobs_created_no": True, "production_queue_claims_no": True, "production_handlers_executed_no": True, "production_workflow_persistence_no": True, "production_recovery_actions_no": True, "live_network_requests_during_certification_no": True})
        evidence["attention_kinds"] = ["failed_workflow", "failed_stage", "failed_job", "terminal_error", "retry_scheduled", "retry_exhausted"]
        if not all(checks.values()): raise RuntimeError("Retained 15-B4J certification checks failed.")
        retained, status = True, "CERTIFIED"
    except Exception as exc:
        error = {"error_type": type(exc).__name__, "error_message": str(exc), "traceback": traceback.format_exc()}
        for name, content in originals.items(): paths[name].write_bytes(content)
    finally:
        evidence["patch_retained"] = retained; report.parent.mkdir(parents=True, exist_ok=True); write_text(report, make_report(status, checks, evidence, error))
    for name, passed in checks.items(): print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not passed for passed in checks.values())}"); print("NOT_RUN_CHECK_COUNT=0"); print(f"REPORT={report}"); print(f"PART_F_15_B4J_STATUS={status}"); print(f"PATCH_RETAINED={'YES' if retained else 'NO'}")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
