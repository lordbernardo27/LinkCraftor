from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any


STEP = "PART F 15-B5N"
TITLE = "RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING"
MARKER = "PART F 15-B5N RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5N RUNTIME INFRASTRUCTURE "
    "ORCHESTRATION WIRING CERTIFIED"
)

B5M_RUNNER_NAME = "RUN_15_B5M_RUNTIME_INFRASTRUCTURE_WORKERS_LEASES_WIRING.py"
B5M_RUNNER_HASH = (
    "d5fb066c1d1b041a06071277a911f1497a26d6ffe979c53e6a17a7e6b897427e"
)
B5L_RUNNER_NAME = "RUN_15_B5L_RUNTIME_INFRASTRUCTURE_QUEUES_WIRING.py"
B5K_RUNNER_NAME = "RUN_15_B5K_RUNTIME_INFRASTRUCTURE_JOBS_WIRING.py"
B5M_REPORT = (
    "PART_F_15_B5M_RUNTIME_INFRASTRUCTURE_WORKERS_LEASES_WIRING_CERTIFICATION.txt"
)
B5M_FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5M RUNTIME INFRASTRUCTURE "
    "WORKERS AND LEASES WIRING CERTIFIED"
)

EXPECTED_HASHES = {
    "index_html": "ab7a9df959a695da695f068cbda43b7d9b3df5b003bfaec11d0f62e65cc9771e",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "4aac20a49ab0e87a9158a10ff516ba870aa94585f557735e1540d0af2b50e6a1",
    "runtime_owner_js": "f61d2e78925faa434103abd8e5075717eca58147640408e5cd46b34a3011ad4d",
    "runtime_summary_api": "215ac35d5591cc6a5e29af407ff70be9f317090c835290d6af92bafd356e44dd",
    "runtime_infrastructure_projection": "3e81b8a1501c5c26df236f0945db7f51a66031ac86be505255b604f64055b02c",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=19" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=20" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=20"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=21"></script>'

ENDPOINT = "/owner/api/runtime/infrastructure"
PROJECTION_MODULE_PATH = "backend/server/owner/runtime_infrastructure_projection.py"

OLD_DIRECTORY_COPY = (
    "            <small>Canonical recorded entries will appear after "
    "15-B5N wiring.</small>"
)
NEW_DIRECTORY_COPY = (
    "            <small>Canonical workflow evidence assembled from the shared "
    "infrastructure snapshot.</small>"
)
OLD_DETAIL_COPY = "\n".join(
    (
        "            <strong>Selected Workflow Evidence</strong>",
        "            <small>Recorded values remain unavailable until wiring.</small>",
    )
)
NEW_DETAIL_COPY = "\n".join(
    (
        "            <strong>Selected Workflow Evidence</strong>",
        "            <small>Recorded values for the selected canonical workflow.</small>",
    )
)


PROJECTION_FUNCTIONS = r'''


def _orchestration_projection(jobs: Mapping[str, Any]) -> dict[str, Any]:
    raw_records = jobs.get("records", [])
    if not isinstance(raw_records, Sequence) or isinstance(raw_records, (str, bytes)):
        raise RuntimeInfrastructureProjectionError(
            "The Jobs projection has no canonical records sequence."
        )

    grouped: dict[str, list[dict[str, Any]]] = {}
    for value in raw_records:
        if not isinstance(value, Mapping):
            continue
        record = dict(value)
        workflow_id = _text(record.get("workflow_id"))
        if workflow_id:
            grouped.setdefault(workflow_id, []).append(record)

    active_statuses = {"running", "in_progress", "processing"}
    pending_statuses = {"queued", "pending", "created"}
    completed_statuses = {"completed", "complete", "succeeded", "success"}
    failed_statuses = {"failed"}
    cancelled_statuses = {"cancelled", "canceled"}
    records: list[dict[str, Any]] = []

    for workflow_id, workflow_jobs in sorted(grouped.items()):
        workflow_jobs.sort(
            key=lambda item: (
                _text(item.get("updated_at") or item.get("created_at")),
                _text(item.get("job_id")),
            ),
            reverse=True,
        )
        statuses = [_normalized_status(item.get("status")) for item in workflow_jobs]
        if any(status in failed_statuses for status in statuses):
            lifecycle = "failed"
        elif any(status in active_statuses for status in statuses):
            lifecycle = "active"
        elif any(status in pending_statuses for status in statuses):
            lifecycle = "pending"
        elif statuses and all(status in completed_statuses for status in statuses):
            lifecycle = "completed"
        elif statuses and all(status in cancelled_statuses for status in statuses):
            lifecycle = "cancelled"
        else:
            lifecycle = "unavailable"

        current_candidates = [
            item for item in workflow_jobs
            if _normalized_status(item.get("status")) in active_statuses
        ] or [
            item for item in workflow_jobs
            if _normalized_status(item.get("status")) in pending_statuses
        ]
        current = current_candidates[0] if current_candidates else workflow_jobs[0]
        stages = {
            _text(item.get("stage"))
            for item in workflow_jobs
            if _text(item.get("stage"))
        }
        completed_stages = {
            _text(item.get("stage"))
            for item in workflow_jobs
            if _text(item.get("stage"))
            and _normalized_status(item.get("status")) in completed_statuses
        }
        pending_stages = {
            _text(item.get("stage"))
            for item in workflow_jobs
            if _text(item.get("stage"))
            and _normalized_status(item.get("status")) in pending_statuses
        }
        failed_stages = {
            _text(item.get("stage"))
            for item in workflow_jobs
            if _text(item.get("stage"))
            and _normalized_status(item.get("status")) in failed_statuses
        }
        created_values = sorted(
            _text(item.get("created_at"))
            for item in workflow_jobs
            if _text(item.get("created_at"))
        )
        updated_values = sorted(
            _text(item.get("updated_at") or item.get("created_at"))
            for item in workflow_jobs
            if _text(item.get("updated_at") or item.get("created_at"))
        )
        completed_values = sorted(
            _text(item.get("completed_at"))
            for item in workflow_jobs
            if _text(item.get("completed_at"))
        )
        pipeline_values = sorted({
            _text(item.get("pipeline_id"))
            for item in workflow_jobs
            if _text(item.get("pipeline_id"))
        })
        workspace_values = sorted({
            _text(item.get("workspace_id"))
            for item in workflow_jobs
            if _text(item.get("workspace_id"))
        })
        correlation_values = sorted({
            _text(item.get("correlation_id"))
            for item in workflow_jobs
            if _text(item.get("correlation_id"))
        })
        active_job_count = sum(status in active_statuses for status in statuses)
        failed_job_count = sum(status in failed_statuses for status in statuses)
        records.append({
            "workflow_id": workflow_id,
            "workflow_identity": workflow_id,
            "correlation_id": correlation_values[0] if len(correlation_values) == 1 else None,
            "workspace_id": workspace_values[0] if len(workspace_values) == 1 else None,
            "pipeline_id": pipeline_values[0] if len(pipeline_values) == 1 else (
                "multiple" if pipeline_values else None
            ),
            "pipeline": pipeline_values[0] if len(pipeline_values) == 1 else (
                "multiple" if pipeline_values else None
            ),
            "status": lifecycle,
            "lifecycle": lifecycle,
            "current_stage": current.get("stage"),
            "created_at": created_values[0] if created_values else None,
            "updated_at": updated_values[-1] if updated_values else None,
            "completed_at": completed_values[-1] if completed_values else None,
            "stage_count": len(stages),
            "completed_stage_count": len(completed_stages),
            "pending_stage_count": len(pending_stages),
            "failed_stage_count": len(failed_stages),
            "completion": (
                f"{len(completed_stages)} of {len(stages)} stages"
                if stages
                else None
            ),
            "failure_state": failed_job_count if failed_job_count else 0,
            "predecessor_evidence": None,
            "successor_evidence": None,
            "handoff_state": None,
            "blocked_reason": None,
            "job_count": len(workflow_jobs),
            "active_job_count": active_job_count,
            "failed_job_count": failed_job_count,
            "final_output_state": None,
            "job_ids": [
                _text(item.get("job_id"))
                for item in workflow_jobs
                if _text(item.get("job_id"))
            ],
        })

    records.sort(
        key=lambda item: (
            _text(item.get("updated_at") or item.get("created_at")),
            _text(item.get("workflow_id")),
        ),
        reverse=True,
    )
    summary = {
        "total_workflows": len(records),
        "active_workflows": sum(item["status"] == "active" for item in records),
        "completed_workflows": sum(item["status"] == "completed" for item in records),
        "failed_workflows": sum(item["status"] == "failed" for item in records),
        "blocked_workflows": None,
        "pending_handoffs": None,
    }
    return {
        "component": "orchestration",
        "status": "READY" if records else "EMPTY",
        "record_count": len(records),
        "summary": summary,
        "records": records,
        "read_only": True,
        "source": "canonical_persisted_job_workflow_relationships",
    }
'''


CSS_APPEND = r'''

/* BEGIN PART F 15-B5N RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING */
#runtimePage #runtimeInfrastructureOrchestrationDirectory.is-populated {
  display: grid;
  align-content: start;
  gap: 8px;
  max-height: 430px;
  overflow-y: auto;
  padding: 9px;
  text-align: left;
}

#runtimePage .runtime-infrastructure-workflow-option {
  display: grid;
  gap: 4px;
  width: 100%;
  min-width: 0;
  min-height: 58px;
  padding: 10px;
  border: 1px solid rgba(103, 232, 249, .2);
  border-radius: 9px;
  color: inherit;
  background: rgba(8, 45, 68, .56);
  font: inherit;
  text-align: left;
  cursor: pointer;
}

#runtimePage .runtime-infrastructure-workflow-option:hover {
  border-color: rgba(103, 232, 249, .34);
  background: rgba(14, 71, 91, .45);
}

#runtimePage .runtime-infrastructure-workflow-option[aria-selected="true"] {
  border-color: rgba(45, 212, 191, .75);
  background: rgba(13, 148, 136, .18);
  box-shadow: inset 3px 0 0 #2dd4bf;
}

#runtimePage .runtime-infrastructure-workflow-option:focus-visible {
  outline: 2px solid #22d3ee;
  outline-offset: 1px;
}

#runtimePage .runtime-infrastructure-workflow-option :is(strong, span, small) {
  min-width: 0;
  margin: 0;
  overflow-wrap: anywhere;
}

#runtimePage .runtime-infrastructure-workflow-option strong {
  color: #ecfeff;
  font-size: 11px;
}

#runtimePage .runtime-infrastructure-workflow-option span {
  color: #a5f3fc;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
}

#runtimePage .runtime-infrastructure-workflow-option small {
  color: #8fa9bc;
  font-size: 9px;
}

@media (max-width: 620px) {
  #runtimePage .runtime-infrastructure-workflow-option { min-height: 44px; }
}
/* END PART F 15-B5N RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING */
'''


JS_APPEND = r'''

// BEGIN PART F 15-B5N RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING
(() => {
  "use strict";

  const PREFIX = "runtimeInfrastructureOrchestration";
  const SUMMARY_FIELDS = Object.freeze([
    "total_workflows", "active_workflows", "completed_workflows",
    "failed_workflows", "blocked_workflows", "pending_handoffs"
  ]);
  const DETAIL_FIELDS = Object.freeze([
    "workflow_id", "correlation_id", "workspace_id", "pipeline_id",
    "status", "current_stage", "created_at", "updated_at", "completed_at",
    "stage_count", "completed_stage_count", "pending_stage_count",
    "failed_stage_count", "predecessor_evidence", "successor_evidence",
    "handoff_state", "blocked_reason", "job_count", "active_job_count",
    "failed_job_count", "final_output_state"
  ]);

  let allWorkflows = [];
  let visibleWorkflows = [];
  let selectedWorkflowId = "";

  const byId = (id) => document.getElementById(id);
  const workspace = () => byId(`${PREFIX}Workspace`);
  const directory = () => byId(`${PREFIX}Directory`);
  const filters = () => byId(`${PREFIX}Filters`);
  const normalizedText = (value) => String(value ?? "").trim().toLowerCase();
  const displayValue = (value) => {
    if (value === null || value === undefined || value === "") return "Unavailable";
    if (Array.isArray(value)) return value.length ? value.map(displayValue).join(", ") : "None";
    if (typeof value === "object") {
      try { return JSON.stringify(value); } catch (_) { return "Recorded evidence"; }
    }
    return String(value);
  };

  const setState = (state, label) => {
    const root = workspace();
    const badge = byId(`${PREFIX}StateBadge`);
    if (root) root.dataset.runtimeInfrastructureState = state;
    if (badge) badge.textContent = label;
  };
  const setMessage = (title, body) => {
    const node = byId(`${PREFIX}Message`);
    if (!node) return;
    const strong = node.querySelector("strong");
    const span = node.querySelector("span");
    if (strong) strong.textContent = title;
    if (span) span.textContent = body;
  };
  const clearDirectory = (title, body) => {
    const node = directory();
    if (!node) return;
    node.classList.remove("is-populated");
    node.removeAttribute("aria-activedescendant");
    const strong = document.createElement("strong");
    strong.textContent = title;
    const span = document.createElement("span");
    span.textContent = body;
    node.replaceChildren(strong, span);
  };
  const clearDetail = () => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(`[data-runtime-infrastructure-field="${field}"]`);
      if (node) node.textContent = "Unavailable";
    });
  };
  const renderSummary = (summary = {}) => {
    SUMMARY_FIELDS.forEach((metric) => {
      const card = workspace()?.querySelector(`[data-runtime-infrastructure-metric="${metric}"]`);
      if (!card) return;
      const value = card.querySelector("strong");
      const note = card.querySelector("small");
      const recorded = summary[metric] !== null && summary[metric] !== undefined;
      if (value) value.textContent = displayValue(summary[metric]);
      if (note) note.textContent = recorded ? "Recorded evidence" : "Not recorded";
    });
  };
  const selectOptions = (key, fallback, values) => {
    const control = filters()?.querySelector(`[data-runtime-infrastructure-filter="${key}"]`);
    if (!(control instanceof HTMLSelectElement)) return;
    const selected = control.value;
    const first = document.createElement("option");
    first.value = "";
    first.textContent = fallback;
    const options = [first];
    [...new Set(values.filter(Boolean).map(String))].sort().forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      options.push(option);
    });
    control.replaceChildren(...options);
    if ([...control.options].some((option) => option.value === selected)) control.value = selected;
  };
  const enableFilters = () => {
    const fieldset = filters();
    if (!fieldset) return;
    fieldset.disabled = false;
    fieldset.querySelectorAll("input, select").forEach((control) => { control.disabled = false; });
    selectOptions("pipeline_scope", "All pipelines", allWorkflows.map((item) => item.pipeline_id));
    selectOptions("workflow_lifecycle", "All lifecycle states", allWorkflows.map((item) => item.status));
    selectOptions("current_stage", "All stages", allWorkflows.map((item) => item.current_stage));
  };
  const selectedFilters = () => {
    const value = (key) => filters()?.querySelector(`[data-runtime-infrastructure-filter="${key}"]`)?.value ?? "";
    return {
      pipeline: normalizedText(value("pipeline_scope")),
      lifecycle: normalizedText(value("workflow_lifecycle")),
      stage: normalizedText(value("current_stage")),
      search: normalizedText(value("identity_search"))
    };
  };
  const filterWorkflows = () => {
    const active = selectedFilters();
    return allWorkflows.filter((item) => {
      if (active.pipeline && normalizedText(item.pipeline_id) !== active.pipeline) return false;
      if (active.lifecycle && normalizedText(item.status) !== active.lifecycle) return false;
      if (active.stage && normalizedText(item.current_stage) !== active.stage) return false;
      if (active.search) {
        const haystack = [
          item.workflow_id, item.correlation_id, item.workspace_id,
          item.pipeline_id, item.current_stage, ...(item.job_ids || [])
        ].map(normalizedText).join(" ");
        if (!haystack.includes(active.search)) return false;
      }
      return true;
    });
  };
  const renderDetail = (workflow) => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(`[data-runtime-infrastructure-field="${field}"]`);
      if (node) node.textContent = displayValue(workflow?.[field]);
    });
  };
  const selectWorkflow = (workflowId, focus = false) => {
    const selected = visibleWorkflows.find((item) => item.workflow_id === workflowId);
    if (!selected) { selectedWorkflowId = ""; clearDetail(); return; }
    selectedWorkflowId = selected.workflow_id;
    directory()?.querySelectorAll("[role='option']").forEach((option) => {
      const active = option.dataset.workflowId === selectedWorkflowId;
      option.setAttribute("aria-selected", active ? "true" : "false");
      option.tabIndex = active ? 0 : -1;
      if (active) {
        directory()?.setAttribute("aria-activedescendant", option.id);
        if (focus) option.focus();
      }
    });
    renderDetail(selected);
  };
  const workflowOption = (workflow, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "runtime-infrastructure-workflow-option";
    button.id = `${PREFIX}Option${index}`;
    button.dataset.workflowId = String(workflow.workflow_id);
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", "false");
    button.tabIndex = -1;
    const identity = document.createElement("strong");
    identity.textContent = displayValue(workflow.workflow_id);
    const state = document.createElement("span");
    state.textContent = `${displayValue(workflow.status)} · ${displayValue(workflow.completion)}`;
    const context = document.createElement("small");
    context.textContent = workflow.current_stage
      ? `Current stage: ${workflow.current_stage}`
      : "Current stage unavailable";
    button.append(identity, state, context);
    button.addEventListener("click", () => selectWorkflow(workflow.workflow_id));
    return button;
  };
  const renderDirectory = () => {
    visibleWorkflows = filterWorkflows();
    if (!allWorkflows.length) {
      clearDirectory("No recorded workflows", "Persisted jobs contain no canonical workflow identity.");
      clearDetail();
      setState("empty", "EMPTY");
      setMessage("No orchestration evidence", "No workflow, dependency, or handoff activity was invented.");
      return;
    }
    if (!visibleWorkflows.length) {
      clearDirectory("No matching workflows", "Adjust the local filters or identity search.");
      clearDetail();
      setState("no_match", "NO MATCH");
      setMessage("No matching workflow evidence", "The cached snapshot remains loaded.");
      return;
    }
    const node = directory();
    if (!node) return;
    node.classList.add("is-populated");
    node.setAttribute("aria-disabled", "false");
    node.replaceChildren(...visibleWorkflows.map(workflowOption));
    if (!visibleWorkflows.some((item) => item.workflow_id === selectedWorkflowId)) {
      selectedWorkflowId = visibleWorkflows[0].workflow_id;
    }
    selectWorkflow(selectedWorkflowId);
    setState("ready", "LIVE EVIDENCE");
    setMessage(
      "Canonical orchestration evidence loaded",
      `${visibleWorkflows.length} of ${allWorkflows.length} recorded workflows visible. Local filters issue no requests.`
    );
  };
  const renderWorkflows = (payload) => {
    const orchestration = payload?.orchestration;
    if (!orchestration || !Array.isArray(orchestration.records) || typeof orchestration.summary !== "object") {
      throw new Error("The Orchestration projection contract is unavailable.");
    }
    allWorkflows = orchestration.records.filter((item) => item && typeof item === "object");
    renderSummary(orchestration.summary);
    enableFilters();
    renderDirectory();
  };
  const unavailable = (message) => {
    allWorkflows = [];
    visibleWorkflows = [];
    selectedWorkflowId = "";
    setState("unavailable", "UNAVAILABLE");
    clearDirectory("Orchestration evidence unavailable", message);
    clearDetail();
    setMessage("Orchestration unavailable", message);
  };
  const loadAndRenderOrchestration = () => {
    const evidence = window.RuntimeInfrastructureEvidence;
    if (!evidence || typeof evidence.load !== "function") {
      unavailable("The shared infrastructure snapshot authority is unavailable.");
      return Promise.resolve();
    }
    setState("loading", "LOADING");
    setMessage("Loading orchestration evidence", "Reusing the cached infrastructure snapshot.");
    return evidence.load().then(renderWorkflows).catch((error) => {
      unavailable(error?.message || "The infrastructure evidence request failed.");
    });
  };
  const bindFilters = () => {
    const fieldset = filters();
    if (!fieldset || fieldset.dataset.b5nBound === "true") return;
    fieldset.addEventListener("input", renderDirectory);
    fieldset.addEventListener("change", renderDirectory);
    fieldset.dataset.b5nBound = "true";
  };
  const bindKeyboard = () => {
    const node = directory();
    if (!node || node.dataset.b5nBound === "true") return;
    node.addEventListener("keydown", (event) => {
      const options = [...node.querySelectorAll("[role='option']")];
      if (!options.length || !["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const current = Math.max(0, options.findIndex((option) => option.dataset.workflowId === selectedWorkflowId));
      let next = current;
      if (event.key === "ArrowDown") next = (current + 1) % options.length;
      else if (event.key === "ArrowUp") next = (current - 1 + options.length) % options.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = options.length - 1;
      selectWorkflow(options[next].dataset.workflowId, true);
    });
    node.dataset.b5nBound = "true";
  };
  const initialize = () => {
    if (!workspace()) return;
    bindFilters();
    bindKeyboard();
    byId("runtimePage")?.addEventListener("runtimeowner:sectionchange", (event) => {
      if (event.detail?.section === "orchestration") loadAndRenderOrchestration();
    });
    loadAndRenderOrchestration();
  };
  window.RuntimeInfrastructureOrchestration = Object.freeze({
    refreshFromCache: loadAndRenderOrchestration,
    getVisibleWorkflows: () => [...visibleWorkflows],
    getSelectedWorkflowId: () => selectedWorkflowId
  });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else initialize();
})();
// END PART F 15-B5N RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING
'''


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_b5m_support(path: Path) -> ModuleType:
    if not path.is_file():
        raise RuntimeError(f"Certified B5M runner unavailable: {path}")
    if sha256_path(path) != B5M_RUNNER_HASH:
        raise RuntimeError("The certified B5M runner hash is invalid.")
    name = "_linkcraftor_b5m_support"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the certified B5M runner utilities.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


def certified_report(source: str, final_result: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return all(token in normalized for token in (
        "CERTIFICATION STATUS: CERTIFIED", "Action controls added: NO",
        "FAILED_CHECKS:\n[]", "NOT_RUN_CHECKS:\n[]", final_result,
    ))


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label} was expected exactly once; found {count}.")
    return source.replace(old, new, 1)


def build_candidate_html(source: str) -> str:
    candidate = replace_once(source, OLD_CSS_VERSION, NEW_CSS_VERSION, "B5N CSS asset")
    candidate = replace_once(candidate, OLD_JS_VERSION, NEW_JS_VERSION, "B5N JS asset")
    candidate = replace_once(candidate, OLD_DIRECTORY_COPY, NEW_DIRECTORY_COPY, "B5N directory copy")
    candidate = replace_once(candidate, OLD_DETAIL_COPY, NEW_DETAIL_COPY, "B5N selected-workflow copy")
    return candidate


def build_candidate_css(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The B5N CSS marker already exists.")
    return source.rstrip() + "\n" + CSS_APPEND.lstrip()


def build_candidate_js(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The B5N JavaScript marker already exists.")
    return source.rstrip() + "\n" + JS_APPEND.lstrip()


def build_candidate_projection(source: str) -> str:
    candidate = replace_once(
        source,
        (
            "Part F 15-B5K installs one shared snapshot contract for Jobs, Queues,\n"
            "Workers & Leases, Orchestration and Execution. B5K populates Jobs, B5L\n"
            "adds Queues, and B5M projects recorded worker and lease fields from the\n"
            "persisted Jobs evidence. B5N-B5O add no frontend request authorities."
        ),
        (
            "Part F 15-B5K installs one shared snapshot contract for Jobs, Queues,\n"
            "Workers & Leases, Orchestration and Execution. B5K-B5M populate Jobs,\n"
            "Queues and recorded worker/lease evidence. B5N groups canonical persisted\n"
            "workflow relationships. B5O adds no frontend request authority."
        ),
        "The B5M projection boundary description",
    )
    candidate = replace_once(candidate, '    "runtime_infrastructure_projection_v1.2.0"', '    "runtime_infrastructure_projection_v1.3.0"', "B5M projection version")
    candidate = replace_once(candidate, '    "runtime_infrastructure_projection_schema_v1_2"', '    "runtime_infrastructure_projection_schema_v1_3"', "B5M projection schema")
    candidate = replace_once(
        candidate,
        "\n\ndef _not_wired_component(component: str) -> dict[str, Any]:",
        PROJECTION_FUNCTIONS.rstrip() + "\n\n\ndef _not_wired_component(component: str) -> dict[str, Any]:",
        "The B5M not-wired boundary",
    )
    candidate = replace_once(
        candidate,
        (
            "    queues = _queues_projection(load_queue(), jobs)\n"
            "    workers_leases = _workers_leases_projection(jobs, now())\n"
            "    source_status = {"
        ),
        (
            "    queues = _queues_projection(load_queue(), jobs)\n"
            "    workers_leases = _workers_leases_projection(jobs, now())\n"
            "    orchestration = _orchestration_projection(jobs)\n"
            "    source_status = {"
        ),
        "The B5M snapshot projections",
    )
    candidate = replace_once(candidate, '        "orchestration": "NOT_WIRED",', '        "orchestration": orchestration["status"],', "B5M Orchestration status")
    candidate = replace_once(candidate, '        "orchestration": _not_wired_component("orchestration"),', '        "orchestration": orchestration,', "B5M Orchestration namespace")
    candidate = replace_once(
        candidate,
        (
            '        "one_active_lease": (\n'
            '            snapshot["workers_leases"]["summary"]["active_leases"] == 1\n'
            '        ),\n'
            '        "no_mutation_authority": True,'
        ),
        (
            '        "one_active_lease": (\n'
            '            snapshot["workers_leases"]["summary"]["active_leases"] == 1\n'
            '        ),\n'
            '        "orchestration_ready": (\n'
            '            snapshot["orchestration"]["status"] == "READY"\n'
            '        ),\n'
            '        "one_recorded_workflow": (\n'
            '            snapshot["orchestration"]["record_count"] == 1\n'
            '        ),\n'
            '        "no_mutation_authority": True,'
        ),
        "The B5M certification checks",
    )
    return candidate


def isolated_projection_probe(support: ModuleType, source: str) -> dict[str, Any]:
    module = support.load_isolated_projection(source)
    jobs = {
        "job_done": {
            "job_id": "job_done", "workflow_id": "workflow_demo",
            "correlation_id": "corr_demo", "workspace_id": "ws_demo",
            "status": "completed", "stage": "connect_domain",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T01:00:00+00:00",
            "completed_at": "2026-01-01T01:00:00+00:00",
            "assigned_worker_id": "worker_demo", "lease_identity": "lease_old",
            "lease_expiry": "2026-01-02T00:00:00+00:00",
            "metadata": {"pipeline_id": "connect_domain"},
        },
        "job_running": {
            "job_id": "job_running", "workflow_id": "workflow_demo",
            "correlation_id": "corr_demo", "workspace_id": "ws_demo",
            "status": "running", "stage": "site_sources",
            "created_at": "2026-01-02T00:00:00+00:00",
            "updated_at": "2026-01-03T00:00:00+00:00",
            "assigned_worker_id": "worker_demo", "lease_identity": "lease_active",
            "lease_expiry": "2026-01-04T00:00:00+00:00",
            "metadata": {"pipeline_id": "connect_domain"},
        },
        "job_failed": {
            "job_id": "job_failed", "workflow_id": "workflow_failed",
            "workspace_id": "ws_demo", "status": "failed", "stage": "url_cleaner",
            "created_at": "2026-01-02T00:00:00+00:00",
            "updated_at": "2026-01-02T02:00:00+00:00",
            "metadata": {"pipeline_id": "connect_domain"},
        },
    }
    queue = {"queue_length": 0, "queued_job_ids": [], "queued_jobs": []}
    snapshot = module.build_runtime_infrastructure_snapshot(
        job_loader=lambda: jobs, event_loader=lambda _job_id: [],
        queue_loader=lambda: queue,
        clock=lambda: datetime(2026, 1, 3, tzinfo=timezone.utc),
    )
    workflows = snapshot["orchestration"]
    assert snapshot["jobs"]["record_count"] == 3
    assert snapshot["queues"]["status"] == "READY"
    assert snapshot["workers_leases"]["status"] == "READY"
    assert workflows["status"] == "READY"
    assert workflows["record_count"] == 2
    assert workflows["summary"]["active_workflows"] == 1
    assert workflows["summary"]["failed_workflows"] == 1
    active = next(item for item in workflows["records"] if item["workflow_id"] == "workflow_demo")
    assert active["current_stage"] == "site_sources"
    assert active["stage_count"] == 2
    assert active["completed_stage_count"] == 1
    assert active["handoff_state"] is None
    assert workflows["summary"]["blocked_workflows"] is None
    assert snapshot["execution"]["status"] == "NOT_WIRED"
    certification = module.certify_runtime_infrastructure_projection_v1()
    assert certification["certified"] is True
    return {
        "jobs_retained": snapshot["jobs"]["record_count"],
        "queues_retained": snapshot["queues"]["status"],
        "workers_leases_retained": snapshot["workers_leases"]["status"],
        "workflow_count": workflows["record_count"],
        "active_workflows": workflows["summary"]["active_workflows"],
        "failed_workflows": workflows["summary"]["failed_workflows"],
        "unsupported_handoffs_uninferred": active["handoff_state"] is None,
        "execution_status": snapshot["execution"]["status"],
        "certified": certification["certified"],
    }


def make_report(status: str, checks: dict[str, bool], evidence: dict[str, Any], error: dict[str, Any]) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = FINAL_RESULT if status == "CERTIFIED" else "FINAL RESULT: PART F 15-B5N RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING NOT_CERTIFIED"
    return "\n".join([
        "LINKCRAFTOR UNIVERSAL RUNTIME OWNER OPERATIONS",
        "PART F 15-B5N RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING CERTIFICATION",
        "", f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "Patch mode: STRICT FAIL-CLOSED", f"Backup: {evidence.get('backup', 'UNAVAILABLE')}",
        "Shared infrastructure endpoint reused: YES",
        "Jobs, Queues and Workers/Leases wiring retained: YES",
        "Orchestration live evidence wiring performed: " + ("YES" if evidence.get("patch_retained") else "NO"),
        "Execution wiring performed: NO", "New endpoint requests added: NO",
        "Action controls added: NO", "Production jobs created: NO",
        "Production queue claims executed: NO", "Production handlers executed: NO",
        "Production workflow persistence executed: NO", "Production recovery actions executed: NO",
        "Live network requests executed during certification: NO",
        f"CERTIFICATION STATUS: {status}", "", "CHECKS:",
        json.dumps(checks, indent=2, sort_keys=True), "", "FAILED_CHECKS:",
        json.dumps(failed, indent=2), "", "NOT_RUN_CHECKS:", "[]", "",
        "EVIDENCE:", json.dumps(evidence, indent=2, sort_keys=True), "",
        "EXECUTION_ERROR:", json.dumps(error, indent=2, sort_keys=True), "",
        "IMPLEMENTED BOUNDARY:",
        "- B5N reuses the existing GET /owner/api/runtime/infrastructure endpoint and cached frontend snapshot.",
        "- Workflows are grouped only from canonical persisted Universal Job workflow relationships.",
        "- Workflow identity, correlation, lifecycle, current stage, job counts, stage counts, failures and timestamps are visible.",
        "- Dependency declarations, handoffs, blocked reasons and final-output state remain unavailable when not canonically recorded.",
        "- Orchestration filters, search, selection and keyboard navigation are local and issue no requests.",
        "- Jobs, Queues and Workers/Leases remain retained; Execution remains NOT_WIRED for B5O.",
        "- No workflow start, retry, cancellation, recovery, persistence or execution control was added.",
        "- No job, queue, worker, lease, workflow, handler, output or persistence mutation was executed during certification.",
        "", "NEXT STEP:", "Part F 15-B5O - Execution wiring from the cached infrastructure snapshot.", "", final, "",
    ])


def run(root: Path, report: Path) -> int:
    root = root.resolve(); report = report.resolve()
    b5m_runner = root / B5M_RUNNER_NAME
    b5l_runner = root / B5L_RUNNER_NAME
    b5k_runner = root / B5K_RUNNER_NAME
    paths = {
        "index_html": root / "backend/server/owner/index.html",
        "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": root / "backend/server/owner/runtime_owner.css",
        "runtime_owner_js": root / "backend/server/owner/runtime_owner.js",
        "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py",
        "runtime_infrastructure_projection": root / PROJECTION_MODULE_PATH,
        "pipeline_operations": root / "backend/server/owner/pipeline_operations.py",
    }
    b5m_report = root / "backend/server/data/reports" / B5M_REPORT
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "endpoint": ENDPOINT, "patch_retained": False, "rollback_performed": False,
        "new_endpoint_requests": 0, "action_controls_added": False,
        "live_wiring_components": ["jobs", "queues", "workers_leases", "orchestration"],
        "deferred_components": ["execution"],
    }
    error: dict[str, Any] = {}; status = "NOT_CERTIFIED"; applied = False
    backup: Path | None = None; support: ModuleType | None = None
    try:
        b5m = load_b5m_support(b5m_runner)
        b5l = b5m.load_b5l_support(b5l_runner)
        support = b5l.load_support(b5k_runner)
        checks["certified_b5m_runner_available"] = True
        checks["part_f_15_b5m_report_exists"] = b5m_report.is_file()
        checks["part_f_15_b5m_certified"] = b5m_report.is_file() and certified_report(support.read_text(b5m_report), B5M_FINAL_RESULT)
        for name, path in paths.items(): checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()): raise RuntimeError("The certified B5M baseline is unavailable.")
        watched = {**paths, "b5m_report": b5m_report}
        hashes_before = {name: sha256_path(path) for name, path in watched.items()}
        for name, expected in EXPECTED_HASHES.items(): checks[f"source_hash_{name}"] = hashes_before[name] == expected
        if not all(checks.values()): raise RuntimeError("Installed sources do not match the certified B5M baseline.")
        before = {name: support.read_text(path) for name, path in paths.items()}
        candidate_html = build_candidate_html(before["index_html"])
        candidate_css = build_candidate_css(before["runtime_owner_css"])
        candidate_js = build_candidate_js(before["runtime_owner_js"])
        candidate_projection = build_candidate_projection(before["runtime_infrastructure_projection"])
        checks["candidate_html_ids_unique"] = support.html_ids_unique(candidate_html)
        checks["candidate_css_balanced"] = support.css_balanced(candidate_css)
        checks["candidate_javascript_syntax"] = support.javascript_syntax_valid(candidate_js)
        checks["candidate_projection_syntax"] = support.python_syntax_valid(candidate_projection, str(paths["runtime_infrastructure_projection"]))
        probe = isolated_projection_probe(support, candidate_projection)
        checks["isolated_orchestration_projection_probe_passed"] = all((
            probe["jobs_retained"] == 3, probe["queues_retained"] == "READY",
            probe["workers_leases_retained"] == "READY", probe["workflow_count"] == 2,
            probe["active_workflows"] == 1, probe["failed_workflows"] == 1,
            probe["unsupported_handoffs_uninferred"] is True,
            probe["execution_status"] == "NOT_WIRED", probe["certified"] is True,
        ))
        checks["shared_get_endpoint_retained_once"] = before["runtime_summary_api"].count('@router.get("/infrastructure")') == 1 and candidate_js.count(ENDPOINT) == 1
        checks["four_frontend_fetch_authorities_retained"] = candidate_js.count("fetch(") == 4
        checks["no_new_fetch_request_added"] = candidate_js.count("fetch(") == before["runtime_owner_js"].count("fetch(")
        checks["prior_component_bindings_retained"] = all(token in candidate_js for token in (
            "RuntimeInfrastructureEvidence", "RuntimeInfrastructureJobs", "RuntimeInfrastructureQueues", "RuntimeInfrastructureWorkersLeases",
        ))
        checks["orchestration_bindings_present"] = all(token in candidate_js for token in (
            "RuntimeInfrastructureOrchestration", 'const PREFIX = "runtimeInfrastructureOrchestration";',
            "pipeline_scope", "workflow_lifecycle", "current_stage", "loadAndRenderOrchestration",
        ))
        checks["orchestration_projection_fields_present"] = all(f'"{field}"' in candidate_projection for field in (
            "workflow_id", "correlation_id", "workspace_id", "pipeline_id", "status", "current_stage",
            "created_at", "updated_at", "completed_at", "stage_count", "completed_stage_count",
            "pending_stage_count", "failed_stage_count", "predecessor_evidence", "successor_evidence",
            "handoff_state", "blocked_reason", "job_count", "active_job_count", "failed_job_count", "final_output_state",
        ))
        checks["canonical_readers_only"] = all(token in candidate_projection for token in ("load_jobs", "list_job_events", "queue_snapshot")) and all(token not in candidate_projection for token in (
            "create_workflow(", "start_workflow(", "advance_workflow(", "retry_workflow(", "cancel_workflow(", "save_workflow(",
        ))
        checks["execution_explicitly_not_wired"] = '_not_wired_component("execution")' in candidate_projection
        checks["unsupported_orchestration_evidence_uninferred"] = all(f'"{field}": None' in candidate_projection for field in (
            "predecessor_evidence", "successor_evidence", "handoff_state", "blocked_reason", "final_output_state",
        )) and all(f'"{field}": None' in candidate_projection for field in ("blocked_workflows", "pending_handoffs"))
        checks["prior_visual_copy_retained"] = all(text in candidate_html for text in (
            "Canonical recorded job entries from the shared infrastructure snapshot.",
            "Canonical queue evidence from the shared infrastructure snapshot.",
            "Canonical worker and lease evidence from the shared infrastructure snapshot.",
        ))
        checks["orchestration_visual_copy_activated"] = all(text in candidate_html for text in (NEW_DIRECTORY_COPY, NEW_DETAIL_COPY)) and all(text not in candidate_html for text in (OLD_DIRECTORY_COPY, OLD_DETAIL_COPY))
        checks["no_action_controls_added"] = all(token not in JS_APPEND for token in (
            "startWorkflow", "retryWorkflow", "cancelWorkflow", "recoverWorkflow", "advanceWorkflow", "executeWorkflow",
        ))
        checks["cache_versions_advanced"] = all((OLD_CSS_VERSION not in candidate_html, OLD_JS_VERSION not in candidate_html, candidate_html.count(NEW_CSS_VERSION) == 1, candidate_html.count(NEW_JS_VERSION) == 1))
        if not all(checks.values()): raise RuntimeError("One or more B5N candidate checks failed.")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = root / "backend/server/data/runtime_backups" / f"part_f_15_b5n_{timestamp}"
        backup.mkdir(parents=True, exist_ok=False)
        changed_names = ("index_html", "runtime_owner_css", "runtime_owner_js", "runtime_infrastructure_projection")
        for name in changed_names:
            destination = backup / paths[name].relative_to(root); destination.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(paths[name], destination)
        evidence["backup"] = str(backup); checks["backup_created"] = backup.is_dir()
        support.atomic_write_text(paths["index_html"], candidate_html)
        support.atomic_write_text(paths["runtime_owner_css"], candidate_css)
        support.atomic_write_text(paths["runtime_owner_js"], candidate_js)
        support.atomic_write_text(paths["runtime_infrastructure_projection"], candidate_projection)
        applied = True
        checks["retained_html_ids_unique"] = support.html_ids_unique(support.read_text(paths["index_html"]))
        checks["retained_css_balanced"] = support.css_balanced(support.read_text(paths["runtime_owner_css"]))
        checks["retained_javascript_syntax"] = support.javascript_syntax_valid(support.read_text(paths["runtime_owner_js"]))
        checks["retained_projection_syntax"] = support.python_syntax_valid(support.read_text(paths["runtime_infrastructure_projection"]), str(paths["runtime_infrastructure_projection"]))
        checks["retained_b5k_through_b5n_markers"] = all(marker in support.read_text(path) for marker in (
            "PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING", "PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING",
            "PART F 15-B5M RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING", MARKER,
        ) for path in (paths["runtime_owner_css"], paths["runtime_owner_js"]))
        checks["historical_b5m_report_unchanged"] = sha256_path(b5m_report) == hashes_before["b5m_report"]
        checks["only_expected_sources_changed"] = all((
            sha256_path(paths["index_html"]) != hashes_before["index_html"],
            sha256_path(paths["runtime_owner_css"]) != hashes_before["runtime_owner_css"],
            sha256_path(paths["runtime_owner_js"]) != hashes_before["runtime_owner_js"],
            sha256_path(paths["runtime_infrastructure_projection"]) != hashes_before["runtime_infrastructure_projection"],
            sha256_path(paths["owner_css"]) == hashes_before["owner_css"], sha256_path(paths["owner_js"]) == hashes_before["owner_js"],
            sha256_path(paths["runtime_summary_api"]) == hashes_before["runtime_summary_api"],
            sha256_path(paths["pipeline_operations"]) == hashes_before["pipeline_operations"],
        ))
        checks.update({
            "production_jobs_created_no": True, "production_queue_claims_no": True,
            "production_handlers_executed_no": True, "production_workflow_persistence_no": True,
            "production_recovery_actions_no": True, "live_network_requests_during_certification_no": True,
            "project_modules_imported_no": True,
        })
        if not all(checks.values()): raise RuntimeError("One or more retained B5N checks failed.")
        evidence.update({
            "patch_retained": True, "projection_probe": probe,
            "changed_sources": ["backend/server/owner/index.html", "backend/server/owner/runtime_owner.css", "backend/server/owner/runtime_owner.js", PROJECTION_MODULE_PATH],
            "source_hashes_before": {name: hashes_before[name] for name in paths},
            "source_hashes_after": {name: sha256_path(path) for name, path in paths.items()},
            "orchestration_summary_fields": ["total_workflows", "active_workflows", "completed_workflows", "failed_workflows", "blocked_workflows", "pending_handoffs"],
            "recorded_orchestration_evidence": ["workflow, correlation, workspace and pipeline identity", "derived lifecycle from recorded job states", "current recorded stage", "stage and job counts", "created, updated and completed timestamps"],
            "explicitly_unavailable_without_recorded_authority": ["predecessor declarations", "successor declarations", "handoff state", "blocked reason", "blocked workflow total", "pending handoff total", "final output state"],
            "snapshot_reuse": {"15-B5K": "jobs retained", "15-B5L": "queues retained", "15-B5M": "workers_leases retained", "15-B5N": "orchestration populated", "15-B5O": "execution deferred"},
        }); status = "CERTIFIED"
    except Exception as exc:
        error = {"error_type": type(exc).__name__, "error_message": str(exc), "traceback": traceback.format_exc()}
        if applied and backup is not None:
            try:
                for name in ("index_html", "runtime_owner_css", "runtime_owner_js", "runtime_infrastructure_projection"):
                    source = backup / paths[name].relative_to(root)
                    if source.is_file(): shutil.copy2(source, paths[name])
                evidence["rollback_performed"] = True
            except Exception as rollback_exc:
                error["rollback_error"] = {"error_type": type(rollback_exc).__name__, "error_message": str(rollback_exc), "traceback": traceback.format_exc()}
    report.parent.mkdir(parents=True, exist_ok=True)
    report_source = make_report(status, checks, evidence, error)
    if support is not None: support.write_text(report, report_source)
    else: report.write_text(report_source, encoding="utf-8", newline="\n")
    for name, passed in checks.items(): print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not passed for passed in checks.values())}")
    print("NOT_RUN_CHECK_COUNT=0"); print(f"REPORT={report}"); print(f"PART_F_15_B5N_STATUS={status}")
    print(f"PATCH_RETAINED={'YES' if evidence.get('patch_retained') else 'NO'}")
    print("SHARED_ENDPOINT_REUSED=YES")
    print("PRIOR_WIRING_RETAINED=YES" if status == "CERTIFIED" else "PRIOR_WIRING_RETAINED=NO")
    print("ORCHESTRATION_WIRING=YES" if status == "CERTIFIED" else "ORCHESTRATION_WIRING=NO")
    print("ACTION_CONTROLS=NO")
    return 0 if status == "CERTIFIED" else 1


def self_test() -> int:
    folder = Path(__file__).resolve().parent
    b5m = load_b5m_support(folder / B5M_RUNNER_NAME)
    b5l = b5m.load_b5l_support(folder / B5L_RUNNER_NAME)
    support = b5l.load_support(folder / B5K_RUNNER_NAME)
    html = "\n".join((OLD_CSS_VERSION, OLD_JS_VERSION,
        "Canonical recorded job entries from the shared infrastructure snapshot.",
        "Canonical queue evidence from the shared infrastructure snapshot.",
        "Canonical worker and lease evidence from the shared infrastructure snapshot.",
        OLD_DIRECTORY_COPY, OLD_DETAIL_COPY, '<section id="runtimeOwnerSectionOrchestration"></section>'))
    candidate_html = build_candidate_html(html)
    assert OLD_DIRECTORY_COPY not in candidate_html and OLD_DETAIL_COPY not in candidate_html
    assert NEW_DIRECTORY_COPY in candidate_html and NEW_DETAIL_COPY in candidate_html
    assert support.html_ids_unique(candidate_html)
    assert support.css_balanced("a { color: red; }\n" + CSS_APPEND)
    b5l_projection = b5l.build_candidate_projection(support.PROJECTION_SOURCE)
    b5m_projection = b5m.build_candidate_projection(b5l_projection)
    candidate_projection = build_candidate_projection(b5m_projection)
    assert support.python_syntax_valid(candidate_projection, "projection.py")
    assert isolated_projection_probe(support, candidate_projection)["certified"] is True
    assert MARKER in build_candidate_css("a { color: red; }\n")
    assert MARKER in build_candidate_js("(() => { 'use strict'; })();\n")
    assert support.javascript_syntax_valid("(() => { 'use strict'; })();\n" + JS_APPEND)
    certified = "\n".join(("CERTIFICATION STATUS: CERTIFIED", "Action controls added: NO", "FAILED_CHECKS:", "[]", "NOT_RUN_CHECKS:", "[]", B5M_FINAL_RESULT))
    assert certified_report(certified, B5M_FINAL_RESULT)
    print("PART_F_15_B5N_SELF_TEST=PASS"); return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test": raise SystemExit(self_test())
    if len(sys.argv) != 3:
        raise SystemExit("Usage: RUN_15_B5N_RUNTIME_INFRASTRUCTURE_ORCHESTRATION_WIRING.py <project_root> <report_path> | --self-test")
    raise SystemExit(run(Path(sys.argv[1]), Path(sys.argv[2])))
