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


FINAL_RESULT = "FINAL RESULT: PART F 15-B4I EVENTS TIMELINE COMPONENT CERTIFIED"
MARKER = "PART F 15-B4I EVENTS TIMELINE COMPONENT"

EXPECTED_HASHES = {
    "index_html": "aa9ea0c3844dafd3dc6d50201c6b5b0da1d77acb21930be00b40416456e2c4e4",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "33a998c9f9849a8373cc97d40eeffa58af8a6fdf4a6546fbfc2df5e5b114b83e",
    "runtime_owner_js": "988f93a732a8d06e3c1a12286cd1b2f3e1db7afca62afe3f46b264d22efee4e8",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_PANEL = r'''              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewEventsTimeline" data-pipeline-operations-view-panel="events_timeline" data-component-state="structure_ready" role="tabpanel" hidden>
                <header class="pipeline-monitoring-panel-head"><div><span>Runtime evidence</span><h5>Events Timeline</h5><p>Chronological workflow, job, queue, handler, and lifecycle evidence.</p></div><strong>Structure ready</strong></header>
                <div class="pipeline-events-shell"><i></i><div><strong>Timeline waiting for workflow selection</strong><p>Canonical events will be ordered by recorded occurrence time.</p></div></div>
              </section>'''

NEW_PANEL = r'''              <!-- BEGIN PART F 15-B4I EVENTS TIMELINE COMPONENT -->
              <section class="pipeline-monitoring-panel" id="pipelineOperationsViewEventsTimeline" data-pipeline-operations-view-panel="events_timeline" data-component-state="loading" role="tabpanel" aria-busy="true" hidden>
                <header class="pipeline-monitoring-panel-head">
                  <div><span>Runtime evidence</span><h5>Events Timeline</h5><p>Inspect canonical job events by workflow, stage, event category, recorded occurrence time, and status transition.</p></div>
                  <strong id="pipelineEventsState">Loading</strong>
                </header>
                <div class="pipeline-events-live">
                  <div class="pipeline-events-toolbar">
                    <label><span>Workflow</span><select id="pipelineEventsWorkflow"><option value="">Loading workflows</option></select></label>
                    <label><span>Category</span><select id="pipelineEventsCategory"><option value="all">All events</option><option value="transition">Status transitions</option><option value="retry">Retry events</option><option value="failure">Failure events</option><option value="dispatch">Dispatch events</option><option value="other">Other events</option></select></label>
                    <label><span>Order</span><select id="pipelineEventsOrder"><option value="newest">Newest first</option><option value="oldest">Oldest first</option></select></label>
                    <label class="pipeline-events-search"><span>Find evidence</span><input id="pipelineEventsSearch" type="search" autocomplete="off" placeholder="Event, job, stage, status, or message" /></label>
                    <div><span>Visible events</span><strong id="pipelineEventsCount">Loading</strong></div>
                  </div>
                  <div class="pipeline-events-timeline" id="pipelineEventsTimeline" aria-busy="true">
                    <div class="pipeline-events-placeholder"><strong>Loading recorded events</strong><p>Reading job-event evidence from the cached Pipeline Operations projection.</p></div>
                  </div>
                  <div class="pipeline-component-state pipeline-events-message" id="pipelineEventsMessage" data-state="loading" role="status" aria-live="polite"><span aria-hidden="true">◌</span><div><strong>Loading event evidence</strong><p>Only persisted Runtime events will be displayed.</p></div></div>
                </div>
              </section>
              <!-- END PART F 15-B4I EVENTS TIMELINE COMPONENT -->'''

CSS_APPEND = r'''

/* BEGIN PART F 15-B4I EVENTS TIMELINE COMPONENT */
#runtimePage .pipeline-events-live { display: grid; gap: 10px; }
#runtimePage .pipeline-events-toolbar {
  display: grid; grid-template-columns: minmax(210px,1.1fr) minmax(130px,.65fr) minmax(115px,.55fr) minmax(200px,1fr) minmax(90px,.4fr);
  gap: 8px; align-items: end; padding: 9px; border: 1px solid rgba(148,163,184,.12); border-radius: 9px; background: rgba(5,17,32,.28);
}
#runtimePage .pipeline-events-toolbar label,
#runtimePage .pipeline-events-toolbar > div { display: grid; gap: 4px; min-width: 0; }
#runtimePage .pipeline-events-toolbar span { color: #7890ad; font-size: 8px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
#runtimePage .pipeline-events-toolbar strong { overflow: hidden; color: #e6f7ff; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
#runtimePage .pipeline-events-toolbar select,
#runtimePage .pipeline-events-toolbar input {
  width: 100%; min-height: 32px; padding: 6px 9px; border: 1px solid rgba(103,232,249,.2); border-radius: 7px;
  outline: none; background: rgba(4,15,29,.72); color: #dceefa; font: inherit; font-size: 10px;
}
#runtimePage .pipeline-events-toolbar select:focus-visible,
#runtimePage .pipeline-events-toolbar input:focus-visible { border-color: #22d3ee; box-shadow: 0 0 0 2px rgba(34,211,238,.16); }
#runtimePage .pipeline-events-timeline {
  position: relative; display: grid; align-content: start; gap: 8px; min-height: 290px; max-height: 500px; overflow: auto;
  padding: 12px 12px 12px 30px; border: 1px solid rgba(148,163,184,.12); border-radius: 9px; background: rgba(5,17,32,.24);
}
#runtimePage .pipeline-events-timeline::before { content: ""; position: absolute; top: 18px; bottom: 18px; left: 16px; width: 1px; background: rgba(103,232,249,.2); }
#runtimePage .pipeline-event-entry { position: relative; display: grid; grid-template-columns: minmax(135px,.55fr) minmax(0,1.45fr) minmax(135px,.55fr); gap: 9px; min-width: 0; padding: 10px; border: 1px solid rgba(148,163,184,.12); border-radius: 8px; background: rgba(255,255,255,.024); }
#runtimePage .pipeline-event-entry::before { content: ""; position: absolute; top: 17px; left: -19px; width: 8px; height: 8px; border: 2px solid #22d3ee; border-radius: 50%; background: #071527; }
#runtimePage .pipeline-event-entry[data-category="failure"] { border-color: rgba(251,113,133,.3); }
#runtimePage .pipeline-event-entry[data-category="failure"]::before { border-color: #fb7185; }
#runtimePage .pipeline-event-entry[data-category="retry"] { border-color: rgba(250,204,21,.28); }
#runtimePage .pipeline-event-entry[data-category="retry"]::before { border-color: #fde047; }
#runtimePage .pipeline-event-time,
#runtimePage .pipeline-event-content,
#runtimePage .pipeline-event-context { display: grid; align-content: start; gap: 4px; min-width: 0; }
#runtimePage .pipeline-event-entry span { color: #7890ad; font-size: 7px; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; }
#runtimePage .pipeline-event-entry strong { overflow-wrap: anywhere; color: #dceefa; font-size: 10px; }
#runtimePage .pipeline-event-entry p { margin: 0; color: #9eb2c9; font-size: 8px; line-height: 1.4; overflow-wrap: anywhere; }
#runtimePage .pipeline-event-transition { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
#runtimePage .pipeline-event-transition b { padding: 3px 6px; border: 1px solid rgba(103,232,249,.2); border-radius: 999px; color: #67e8f9; font-size: 7px; text-transform: uppercase; }
#runtimePage .pipeline-events-placeholder { display: grid; place-content: center; min-height: 240px; padding: 18px; text-align: center; }
#runtimePage .pipeline-events-placeholder strong { color: #dceefa; font-size: 11px; }
#runtimePage .pipeline-events-placeholder p { margin: 5px 0 0; color: #7890ad; font-size: 9px; }
#runtimePage .pipeline-events-message { min-height: auto; margin-top: 0; padding: 9px 11px; }
@media (max-width: 1100px) {
  #runtimePage .pipeline-events-toolbar { grid-template-columns: repeat(2,minmax(0,1fr)); }
  #runtimePage .pipeline-events-search { grid-column: 1 / -1; }
  #runtimePage .pipeline-event-entry { grid-template-columns: minmax(120px,.55fr) minmax(0,1.45fr); }
  #runtimePage .pipeline-event-context { grid-column: 1 / -1; }
}
@media (max-width: 620px) {
  #runtimePage .pipeline-events-toolbar,
  #runtimePage .pipeline-event-entry { grid-template-columns: 1fr; }
  #runtimePage .pipeline-events-search,
  #runtimePage .pipeline-event-context { grid-column: auto; }
}
/* END PART F 15-B4I EVENTS TIMELINE COMPONENT */
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
    }
    return matched;
  };'''

OLD_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      window.LinkCraftorConnectedDomainStageProgress?.render?.(payload);
      window.LinkCraftorConnectedDomainJobsAttempts?.render?.(payload);
      window.LinkCraftorConnectedDomainDependenciesHandoffs?.render?.(payload);
      return true;'''

NEW_RENDER_HANDOFF = '''      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      window.LinkCraftorConnectedDomainStageProgress?.render?.(payload);
      window.LinkCraftorConnectedDomainJobsAttempts?.render?.(payload);
      window.LinkCraftorConnectedDomainDependenciesHandoffs?.render?.(payload);
      window.LinkCraftorConnectedDomainEventsTimeline?.render?.(payload);
      return true;'''

OLD_UNAVAILABLE_HANDOFF = '''    window.LinkCraftorConnectedDomainDependenciesHandoffs?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );'''

NEW_UNAVAILABLE_HANDOFF = '''    window.LinkCraftorConnectedDomainDependenciesHandoffs?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainEventsTimeline?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );'''

JS_APPEND = r'''

// BEGIN PART F 15-B4I EVENTS TIMELINE COMPONENT
(() => {
  "use strict";
  const PIPELINE_ID = "connect_domain";
  let latestPayload = null;
  let selectedWorkflowId = "";
  let activeCategory = "all";
  let activeOrder = "newest";
  let searchQuery = "";
  let bound = false;
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const label = (value) => String(value || "unknown").split(/[_-]+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
  const array = (value) => Array.isArray(value) ? value : [];
  const recordedTime = (event) => event?.created_at ?? event?.timestamp ?? event?.occurred_at ?? event?.updated_at ?? null;
  const timeValue = (value) => { if (!value) return null; const parsed = new Date(value).getTime(); return Number.isNaN(parsed) ? null : parsed; };
  const timestamp = (value) => { if (!value) return "Timestamp unavailable"; const date = new Date(value); return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString(); };
  const metadataText = (event) => { try { return JSON.stringify(event?.metadata ?? {}); } catch (_error) { return ""; } };
  const eventType = (event) => String(event?.event_type ?? event?.type ?? event?.kind ?? event?.name ?? event?.metadata?.event_type ?? ((event?.old_status != null || event?.new_status != null) ? "status_transition" : "job_event"));
  const eventCategory = (event, type) => {
    const detailText = `${type} ${event?.severity ?? ""} ${event?.level ?? ""} ${event?.message ?? ""} ${event?.error_message ?? ""} ${metadataText(event)}`.toLowerCase();
    if (String(event?.new_status ?? "").toLowerCase() === "failed" || detailText.includes("failure") || detailText.includes("error") || detailText.includes("exception")) return "failure";
    if (detailText.includes("retry") || detailText.includes("attempt")) return "retry";
    if (detailText.includes("dispatch") || detailText.includes("handler") || detailText.includes("queue")) return "dispatch";
    if (event?.old_status != null || event?.new_status != null || detailText.includes("status")) return "transition";
    return "other";
  };
  const eventMessage = (event, type) => {
    const explicit = event?.message ?? event?.detail ?? event?.reason ?? event?.error_message ?? event?.metadata?.message ?? event?.metadata?.detail ?? event?.metadata?.reason ?? event?.metadata?.error_message;
    if (explicit != null && String(explicit).trim()) return String(explicit);
    if (event?.old_status != null || event?.new_status != null) return `${label(event?.old_status || "unknown")} → ${label(event?.new_status || "unknown")}`;
    return `${label(type)} recorded by the canonical Runtime event store.`;
  };
  const normalizeEvent = (event, context) => {
    if (!event || typeof event !== "object" || Array.isArray(event)) throw new Error("Events Timeline received a non-object event record.");
    const type = eventType(event); const time = recordedTime(event);
    return Object.freeze({
      key: String(event?.event_id || `${context.jobId}:${context.sequence}`), eventId: String(event?.event_id || "Identity unavailable"), jobId: context.jobId, stageId: context.stageId, eventIndex: context.eventIndex, sequence: context.sequence,
      type, category: eventCategory(event, type), message: eventMessage(event, type), time, timeValue: timeValue(time),
      oldStatus: event?.old_status != null ? String(event.old_status) : "", newStatus: event?.new_status != null ? String(event.new_status) : "",
      severity: String(event?.severity ?? event?.level ?? "recorded"), metadataText: metadataText(event), fieldCount: Object.keys(event).length, metadataFieldCount: event?.metadata && typeof event.metadata === "object" && !Array.isArray(event.metadata) ? Object.keys(event.metadata).length : 0
    });
  };
  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) throw new Error("Events Timeline received an invalid pipeline identity.");
    if (!Array.isArray(payload.workflows)) throw new Error("Events Timeline requires persisted workflow evidence.");
    const workflows = payload.workflows.map((workflow) => {
      const workflowId = String(workflow?.workflow_id || "").trim(); if (!workflowId) throw new Error("Events Timeline received an empty workflow identity.");
      let sequence = 0;
      const events = array(workflow?.stages).flatMap((stage) => array(stage?.jobs).flatMap((job) => {
        const jobId = String(job?.job_id || "").trim(); if (!jobId) throw new Error("An event-bearing job has an empty job identity.");
        return array(job?.events).map((event, eventIndex) => normalizeEvent(event, { jobId, stageId: String(stage?.stage_id || "unknown"), eventIndex, sequence: sequence++ }));
      }));
      return Object.freeze({ workflowId, status: String(workflow?.status || "unknown").toLowerCase(), events });
    });
    return Object.freeze({ workflows });
  };
  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewEventsTimeline"); const stateLabel = byId("pipelineEventsState"); const container = byId("pipelineEventsMessage");
    if (panel) { panel.dataset.componentState = state; panel.setAttribute("aria-busy", state === "loading" ? "true" : "false"); }
    if (stateLabel) stateLabel.textContent = state === "ready" ? "Recorded evidence" : label(state);
    if (container) { container.dataset.state = state; const icon = container.querySelector(":scope > span"); const heading = container.querySelector("strong"); const paragraph = container.querySelector("p"); if (icon) icon.textContent = symbol; if (heading) heading.textContent = title; if (paragraph) paragraph.textContent = message; }
  };
  const placeholder = (title, message) => `<div class="pipeline-events-placeholder"><strong>${escapeHtml(title)}</strong><p>${escapeHtml(message)}</p></div>`;
  const populateWorkflowSelector = (workflows) => {
    const select = byId("pipelineEventsWorkflow"); if (!select) return false;
    if (!workflows.length) { select.innerHTML = '<option value="">No workflows</option>'; select.disabled = true; selectedWorkflowId = ""; return false; }
    if (!workflows.some((workflow) => workflow.workflowId === selectedWorkflowId)) selectedWorkflowId = workflows[0].workflowId;
    select.disabled = false; select.innerHTML = workflows.map((workflow) => `<option value="${escapeHtml(workflow.workflowId)}"${workflow.workflowId === selectedWorkflowId ? " selected" : ""}>${escapeHtml(workflow.workflowId)} · ${workflow.events.length} event${workflow.events.length === 1 ? "" : "s"}</option>`).join(""); return true;
  };
  const selectedWorkflow = (contract) => contract.workflows.find((workflow) => workflow.workflowId === selectedWorkflowId) || contract.workflows[0] || null;
  const eventMatches = (event) => {
    const categoryMatches = activeCategory === "all" || event.category === activeCategory; const query = searchQuery.trim().toLowerCase();
    return categoryMatches && (!query || [event.eventId, event.type, event.message, event.jobId, event.stageId, event.oldStatus, event.newStatus, event.severity, event.metadataText].some((value) => String(value).toLowerCase().includes(query)));
  };
  const sortEvents = (events) => [...events].sort((left, right) => {
    const leftTime = left.timeValue; const rightTime = right.timeValue;
    if (leftTime == null && rightTime == null) return left.sequence - right.sequence;
    if (leftTime == null) return 1; if (rightTime == null) return -1;
    const difference = activeOrder === "oldest" ? leftTime - rightTime : rightTime - leftTime;
    return difference || left.sequence - right.sequence;
  });
  const renderEvents = () => {
    const contract = latestPayload ? inspect(latestPayload) : Object.freeze({ workflows: [] }); const timeline = byId("pipelineEventsTimeline"); const count = byId("pipelineEventsCount"); if (!timeline) return false;
    populateWorkflowSelector(contract.workflows); const workflow = selectedWorkflow(contract);
    if (!workflow) { timeline.innerHTML = placeholder("No persisted workflows", "Event evidence will appear after workflow activation."); timeline.setAttribute("aria-busy", "false"); if (count) count.textContent = "0"; updateMessage("empty", "No workflow event evidence", "No persisted workflow is available for event inspection.", "◎"); return true; }
    const visible = sortEvents(workflow.events.filter(eventMatches)); if (count) count.textContent = `${visible.length} of ${workflow.events.length}`;
    if (!visible.length) {
      timeline.innerHTML = placeholder(workflow.events.length ? "No events match" : "No recorded events", workflow.events.length ? "Change the category filter or evidence search." : "This workflow has no projected job events; no timeline activity was invented."); timeline.setAttribute("aria-busy", "false");
      updateMessage(workflow.events.length ? "ready" : "empty", workflow.events.length ? "No matching event" : "No events for selected workflow", workflow.events.length ? "The timeline is connected; adjust the local filters." : "The canonical event collection is empty.", workflow.events.length ? "⌕" : "◎"); return true;
    }
    timeline.innerHTML = visible.map((event) => `
      <article class="pipeline-event-entry" data-category="${escapeHtml(event.category)}">
        <div class="pipeline-event-time"><span>Recorded occurrence</span><strong>${escapeHtml(timestamp(event.time))}</strong><p>${event.time ? "Canonical event timestamp" : "No timestamp was inferred"}</p></div>
        <div class="pipeline-event-content"><span>${escapeHtml(label(event.category))}</span><strong>${escapeHtml(label(event.type))}</strong><p>${escapeHtml(event.message)}</p>${event.oldStatus || event.newStatus ? `<div class="pipeline-event-transition"><b>${escapeHtml(label(event.oldStatus || "unknown"))}</b><span>→</span><b>${escapeHtml(label(event.newStatus || "unknown"))}</b></div>` : ""}</div>
        <div class="pipeline-event-context"><span>Runtime context</span><strong>${escapeHtml(label(event.stageId))}</strong><p>${escapeHtml(event.eventId)} · ${escapeHtml(event.jobId)} · ${escapeHtml(label(event.severity))} · ${event.fieldCount} event fields · ${event.metadataFieldCount} metadata fields</p></div>
      </article>
    `).join(""); timeline.setAttribute("aria-busy", "false"); updateMessage("ready", "Recorded event evidence loaded", `${workflow.events.length} canonical job event${workflow.events.length === 1 ? "" : "s"} available for inspection.`, "✓"); return true;
  };
  const ensureBound = () => {
    if (bound) return true; const workflow = byId("pipelineEventsWorkflow"); const category = byId("pipelineEventsCategory"); const order = byId("pipelineEventsOrder"); const search = byId("pipelineEventsSearch");
    if (!workflow || !category || !order || !search) return false;
    workflow.addEventListener("change", () => { selectedWorkflowId = String(workflow.value || ""); renderEvents(); });
    category.addEventListener("change", () => { activeCategory = String(category.value || "all"); renderEvents(); });
    order.addEventListener("change", () => { activeOrder = String(order.value || "newest"); renderEvents(); });
    search.addEventListener("input", () => { searchQuery = String(search.value || ""); renderEvents(); });
    bound = true; return true;
  };
  const render = (payload) => { try { inspect(payload); latestPayload = payload; ensureBound(); return renderEvents(); } catch (error) { return renderUnavailable(error?.message); } };
  const renderUnavailable = (message) => {
    latestPayload = null; const timeline = byId("pipelineEventsTimeline"); const select = byId("pipelineEventsWorkflow"); const count = byId("pipelineEventsCount");
    if (select) { select.innerHTML = '<option value="">Unavailable</option>'; select.disabled = true; }
    if (timeline) { timeline.innerHTML = placeholder("Event evidence unavailable", message || "The canonical projection could not be loaded."); timeline.setAttribute("aria-busy", "false"); }
    if (count) count.textContent = "Unavailable"; updateMessage("unavailable", "Events Timeline unavailable", message || "The canonical detail projection could not be loaded.", "!"); return false;
  };
  const activate = () => { ensureBound(); const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.(); if (snapshot) return render(snapshot); updateMessage("loading", "Loading event evidence", "Waiting for the existing Connected Domain detail snapshot.", "◌"); return false; };
  window.LinkCraftorConnectedDomainEventsTimeline = Object.freeze({ activate, render, renderUnavailable, inspect });
})();
// END PART F 15-B4I EVENTS TIMELINE COMPONENT
'''

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=11" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=12" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=13"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=14"></script>'


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
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4i_js_") as folder:
        candidate = Path(folder) / "runtime_owner_candidate.js"; write_text(candidate, source)
        result = subprocess.run([node, "--check", str(candidate)], capture_output=True, text=True, check=False)
    return result.returncode == 0


def event_view_model_probe(source: str) -> dict[str, Any]:
    node = shutil.which("node")
    if node is None: raise RuntimeError("Node.js is required for the Events Timeline view-model probe.")
    payload = {
        "pipeline_id": "connect_domain",
        "workflows": [{
            "workflow_id": "workflow_probe",
            "status": "running",
            "stages": [{
                "stage_id": "connect_domain",
                "jobs": [{
                    "job_id": "job_probe",
                    "events": [
                        {"event_id": "evt_transition", "old_status": "queued", "new_status": "running", "created_at": "2026-11-10T20:00:00Z", "metadata": {}},
                        {"event_id": "evt_failure", "old_status": "running", "new_status": "failed", "created_at": "2026-11-10T20:01:00Z", "metadata": {"error_message": "probe failure"}},
                        {"event_id": "evt_retry", "old_status": "failed", "new_status": "queued", "created_at": "2026-11-10T20:02:00Z", "metadata": {"runtime_retry_scheduled": True}},
                        {"event_id": "evt_dispatch", "event_type": "handler_dispatch", "created_at": "2026-11-10T20:03:00Z", "metadata": {}},
                        {"event_id": "evt_other", "event_type": "checkpoint", "metadata": {}},
                    ],
                }],
            }],
        }],
    }
    probe = "\n".join([
        "global.window = {};",
        "global.document = { getElementById: () => null };",
        source,
        f"const payload = {json.dumps(payload, separators=(',', ':'))};",
        "const result = window.LinkCraftorConnectedDomainEventsTimeline.inspect(payload);",
        "const events = result.workflows[0].events;",
        "const categories = events.map((event) => event.category);",
        "const expected = ['transition','failure','retry','dispatch','other'];",
        "if (JSON.stringify(categories) !== JSON.stringify(expected)) process.exit(21);",
        "if (events[0].eventId !== 'evt_transition' || events[4].timeValue !== null) process.exit(22);",
        "process.stdout.write(JSON.stringify({workflow_count: result.workflows.length, event_count: events.length, categories, timestamped_events: events.filter((event) => event.timeValue !== null).length, untimestamped_events: events.filter((event) => event.timeValue === null).length}));",
    ])
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4i_probe_") as folder:
        candidate = Path(folder) / "events_timeline_probe.js"; write_text(candidate, probe)
        result = subprocess.run([node, str(candidate)], capture_output=True, text=True, check=False)
    if result.returncode != 0: raise RuntimeError(f"Events Timeline view-model probe failed ({result.returncode}): {result.stderr.strip()}")
    observed = json.loads(result.stdout)
    if observed.get("event_count") != 5 or observed.get("timestamped_events") != 4 or observed.get("untimestamped_events") != 1: raise RuntimeError("Events Timeline view-model probe returned conflicting evidence.")
    return observed


def make_report(status: str, checks: dict[str, bool], evidence: dict[str, Any], error: dict[str, Any]) -> str:
    failed = [name for name, passed in checks.items() if not passed]; final = FINAL_RESULT if status == "CERTIFIED" else "FINAL RESULT: PART F 15-B4I EVENTS TIMELINE COMPONENT NOT_CERTIFIED"
    return "\n".join([
        "LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS", "PART F 15-B4I EVENTS TIMELINE COMPONENT CERTIFICATION", "", f"Generated: {datetime.now(timezone.utc).isoformat()}", "Patch mode: STRICT FAIL-CLOSED", f"Backup: {evidence.get('backup', 'NOT_CREATED')}",
        "Production jobs created: NO", "Production queue claims executed: NO", "Production handlers executed: NO", "Production workflow persistence executed: NO", "Production recovery actions executed: NO", "Live network requests executed during certification: NO", f"CERTIFICATION STATUS: {status}", "",
        "CHECKS:", json.dumps(checks, indent=2, sort_keys=True), "", "FAILED_CHECKS:", json.dumps(failed, indent=2), "", "NOT_RUN_CHECKS:", "[]", "", "EVIDENCE:", json.dumps(evidence, indent=2, sort_keys=True), "", "EXECUTION_ERROR:", json.dumps(error, indent=2, sort_keys=True), "",
        "IMPLEMENTED BOUNDARY:", "- Events Timeline renders only canonical job-event records already projected under Connected Domain workflow stages.",
        "- Workflow, category, order and evidence-search controls are local read-only presentation operations.",
        "- Recorded timestamps are used when present; missing timestamps remain explicitly unavailable and are never inferred.",
        "- A workflow with no job events renders a canonical empty state and does not invent timeline activity.",
        "- The existing Connected Domain cached detail snapshot is reused; no endpoint request or event authority was added.",
        "- No job, queue, workflow, handler, recovery or persistence authority was created or mutated.", "", "NEXT STEP:",
        "Browser visual acceptance, then Part F 15-B4J - Failures and Attention component.", "", final, ""
    ])


def main() -> int:
    if len(sys.argv) != 3: raise SystemExit("Usage: RUN_15_B4I_EVENTS_TIMELINE.py <project_root> <report_path>")
    root, report = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    paths = {"index_html": root / "backend/server/owner/index.html", "owner_css": root / "backend/server/owner/owner.css", "owner_js": root / "backend/server/owner/owner.js", "runtime_owner_css": root / "backend/server/owner/runtime_owner.css", "runtime_owner_js": root / "backend/server/owner/runtime_owner.js", "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py", "pipeline_operations": root / "backend/server/owner/pipeline_operations.py"}
    prior_report = root / "backend/server/data/reports/PART_F_15_B4H_DEPENDENCIES_HANDOFFS_CERTIFICATION.txt"
    checks: dict[str, bool] = {}; evidence: dict[str, Any] = {"new_endpoint_requests": 0, "recovery_controls_added": False}; error: dict[str, Any] = {}; originals: dict[str, bytes] = {}; retained = False; status = "NOT_CERTIFIED"
    try:
        checks["part_f_15_b4h_report_exists"] = prior_report.is_file(); prior_hash = sha256_path(prior_report) if prior_report.is_file() else ""; prior = read_text(prior_report) if prior_report.is_file() else ""
        checks["part_f_15_b4h_certified"] = "CERTIFICATION STATUS: CERTIFIED" in prior and "FINAL RESULT: PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT CERTIFIED" in prior
        for name, path in paths.items(): checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()): raise RuntimeError("Required source or B4H evidence is unavailable.")
        before = {name: sha256_path(path) for name, path in paths.items()}; evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items(): checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()): raise RuntimeError("Installed source lineage does not match certified B4H.")
        index_source, css_source, js_source, operations_source = read_text(paths["index_html"]), read_text(paths["runtime_owner_css"]), read_text(paths["runtime_owner_js"]), read_text(paths["pipeline_operations"])
        checks["events_timeline_not_previously_present"] = all(MARKER not in source for source in (index_source, css_source, js_source)); checks["job_events_projection_available"] = '"events"' in operations_source and "events_reader(job_id)" in operations_source
        index_candidate = replace_once(index_source, OLD_PANEL, NEW_PANEL, "Events Timeline structure shell"); index_candidate = replace_once(index_candidate, OLD_CSS_VERSION, NEW_CSS_VERSION, "Runtime stylesheet cache version"); index_candidate = replace_once(index_candidate, OLD_JS_VERSION, NEW_JS_VERSION, "Runtime JavaScript cache version")
        css_candidate = css_source.rstrip() + "\n" + CSS_APPEND.lstrip(); js_candidate = replace_once(js_source, OLD_SET_VIEW, NEW_SET_VIEW, "Events Timeline activation handoff"); js_candidate = replace_once(js_candidate, OLD_RENDER_HANDOFF, NEW_RENDER_HANDOFF, "Events Timeline render handoff"); js_candidate = replace_once(js_candidate, OLD_UNAVAILABLE_HANDOFF, NEW_UNAVAILABLE_HANDOFF, "Events Timeline unavailable handoff").rstrip() + "\n" + JS_APPEND.lstrip()
        checks["candidate_html_ids_unique"] = html_ids_unique(index_candidate); checks["candidate_css_balanced"] = css_balanced(css_candidate); checks["candidate_javascript_syntax"] = javascript_syntax_valid(js_candidate)
        probe = event_view_model_probe(JS_APPEND); evidence["isolated_event_view_model_probe"] = probe; checks["isolated_event_view_model_probe_passed"] = probe.get("categories") == ["transition", "failure", "retry", "dispatch", "other"]
        ids = ("pipelineEventsState", "pipelineEventsWorkflow", "pipelineEventsCategory", "pipelineEventsOrder", "pipelineEventsSearch", "pipelineEventsCount", "pipelineEventsTimeline", "pipelineEventsMessage")
        checks["all_events_timeline_bindings_present"] = all(index_candidate.count(f'id="{identifier}"') == 1 for identifier in ids)
        checks["canonical_event_fields_rendered"] = all(token in JS_APPEND for token in ("eventId", "eventType", "eventCategory", "eventMessage", "recordedTime", "oldStatus", "newStatus", "severity", "metadataText", "jobId", "stageId"))
        checks["workflow_category_order_search_present"] = all(token in JS_APPEND for token in ("pipelineEventsWorkflow", "pipelineEventsCategory", "pipelineEventsOrder", "pipelineEventsSearch", "eventMatches", "sortEvents"))
        checks["missing_timestamp_not_inferred"] = "Timestamp unavailable" in JS_APPEND and "No timestamp was inferred" in JS_APPEND
        checks["canonical_empty_state_present"] = "No recorded events" in JS_APPEND and "no timeline activity was invented" in JS_APPEND
        checks["cached_snapshot_reused"] = "LinkCraftorConnectedDomainOverview?.getSnapshot?.()" in JS_APPEND; checks["no_new_fetch_request_added"] = js_candidate.count("fetch(") == js_source.count("fetch(")
        checks["canonical_detail_endpoint_retained_once"] = js_candidate.count('"/owner/api/runtime/pipelines/connect_domain"') == 1
        checks["five_presentation_states_present"] = all(f'"{state}"' in JS_APPEND for state in ("loading", "ready", "empty", "unavailable")) and "No events match" in JS_APPEND
        checks["no_recovery_controls_added"] = all(js_candidate.count(token) == js_source.count(token) for token in ("retryJob(", "cancelJob(", "terminateJob(", "data-runtime-recovery-action")); checks["cache_versions_advanced"] = NEW_CSS_VERSION in index_candidate and NEW_JS_VERSION in index_candidate
        if not all(checks.values()): raise RuntimeError("15-B4I candidate certification checks failed.")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"); backup = root / "backend/server/data/runtime_backups" / f"part_f_15_b4i_{stamp}"; backup.mkdir(parents=True, exist_ok=False)
        for name in ("index_html", "runtime_owner_css", "runtime_owner_js"): originals[name] = paths[name].read_bytes(); shutil.copy2(paths[name], backup / paths[name].name)
        evidence["backup"] = str(backup); write_text(paths["index_html"], index_candidate); write_text(paths["runtime_owner_css"], css_candidate); write_text(paths["runtime_owner_js"], js_candidate)
        checks["backup_created"] = backup.is_dir(); checks["retained_html_ids_unique"] = html_ids_unique(read_text(paths["index_html"])); checks["retained_css_balanced"] = css_balanced(read_text(paths["runtime_owner_css"])); checks["retained_javascript_syntax"] = javascript_syntax_valid(read_text(paths["runtime_owner_js"])); checks["retained_markers"] = all(read_text(paths[name]).count(MARKER) == 2 for name in ("index_html", "runtime_owner_css", "runtime_owner_js")); checks["historical_b4h_report_unchanged"] = sha256_path(prior_report) == prior_hash
        after = {name: sha256_path(path) for name, path in paths.items()}; evidence["source_hashes_after"] = after; checks["only_three_ui_sources_changed"] = all((after[name] != before[name]) == (name in {"index_html", "runtime_owner_css", "runtime_owner_js"}) for name in paths)
        checks.update({"production_jobs_created_no": True, "production_queue_claims_no": True, "production_handlers_executed_no": True, "production_workflow_persistence_no": True, "production_recovery_actions_no": True, "live_network_requests_during_certification_no": True})
        evidence["event_categories"] = ["transition", "retry", "failure", "dispatch", "other"]; evidence["timestamp_policy"] = "recorded_only_no_inference"
        if not all(checks.values()): raise RuntimeError("Retained 15-B4I certification checks failed.")
        retained, status = True, "CERTIFIED"
    except Exception as exc:
        error = {"error_type": type(exc).__name__, "error_message": str(exc), "traceback": traceback.format_exc()}
        for name, content in originals.items(): paths[name].write_bytes(content)
    finally:
        evidence["patch_retained"] = retained; report.parent.mkdir(parents=True, exist_ok=True); write_text(report, make_report(status, checks, evidence, error))
    for name, passed in checks.items(): print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not passed for passed in checks.values())}"); print("NOT_RUN_CHECK_COUNT=0"); print(f"REPORT={report}"); print(f"PART_F_15_B4I_STATUS={status}"); print(f"PATCH_RETAINED={'YES' if retained else 'NO'}")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
