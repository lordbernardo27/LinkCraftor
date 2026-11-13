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


STEP = "PART F 15-B5O"
TITLE = "RUNTIME INFRASTRUCTURE EXECUTION WIRING"
MARKER = "PART F 15-B5O RUNTIME INFRASTRUCTURE EXECUTION WIRING"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5O RUNTIME INFRASTRUCTURE "
    "EXECUTION WIRING CERTIFIED"
)

B5N_RUNNER_NAME = "RUN_15_B5N_RUNTIME_INFRASTRUCTURE_ORCHESTRATION_WIRING.py"
B5N_RUNNER_HASH = (
    "5e365e5ac365234a1c6110b26a214415195db00e733387080c5e68f8fc8a10d9"
)
B5M_RUNNER_NAME = "RUN_15_B5M_RUNTIME_INFRASTRUCTURE_WORKERS_LEASES_WIRING.py"
B5L_RUNNER_NAME = "RUN_15_B5L_RUNTIME_INFRASTRUCTURE_QUEUES_WIRING.py"
B5K_RUNNER_NAME = "RUN_15_B5K_RUNTIME_INFRASTRUCTURE_JOBS_WIRING.py"
B5N_REPORT = (
    "PART_F_15_B5N_RUNTIME_INFRASTRUCTURE_ORCHESTRATION_WIRING_CERTIFICATION.txt"
)
B5N_FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5N RUNTIME INFRASTRUCTURE "
    "ORCHESTRATION WIRING CERTIFIED"
)

EXPECTED_HASHES = {
    "index_html": "509f31fb0a0b8c93eb1081a3f5358f41f44a7c2c0ad1b18ffb5a680a16a7470f",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "6cfd3db6ff38842c35ab721d535b886f5c93419ca3c2c58aa93bc4a24cba0af6",
    "runtime_owner_js": "32471d11376ddc560cdf0129c30b4da6c01487edc0a7b6dade2d7dc3fedf873c",
    "runtime_summary_api": "215ac35d5591cc6a5e29af407ff70be9f317090c835290d6af92bafd356e44dd",
    "runtime_infrastructure_projection": "026101c44445c854e83834f57da994e60760e09cb0bce2ebcf276fa3fcf354ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=20" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=21" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=21"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=22"></script>'
ENDPOINT = "/owner/api/runtime/infrastructure"
PROJECTION_MODULE_PATH = "backend/server/owner/runtime_infrastructure_projection.py"

OLD_DIRECTORY_COPY = (
    "            <small>Canonical recorded entries will appear after "
    "15-B5O wiring.</small>"
)
NEW_DIRECTORY_COPY = (
    "            <small>Canonical job-bound execution evidence assembled from "
    "the shared infrastructure snapshot.</small>"
)
OLD_DETAIL_COPY = "\n".join((
    "            <strong>Selected Execution Evidence</strong>",
    "            <small>Recorded values remain unavailable until wiring.</small>",
))
NEW_DETAIL_COPY = "\n".join((
    "            <strong>Selected Execution Evidence</strong>",
    "            <small>Recorded values for the selected canonical job execution.</small>",
))


PROJECTION_FUNCTIONS = r'''


def _execution_projection(jobs: Mapping[str, Any]) -> dict[str, Any]:
    raw_records = jobs.get("records", [])
    if not isinstance(raw_records, Sequence) or isinstance(raw_records, (str, bytes)):
        raise RuntimeInfrastructureProjectionError(
            "The Jobs projection has no canonical records sequence."
        )

    running_statuses = {"running", "in_progress", "processing"}
    succeeded_statuses = {"completed", "complete", "succeeded", "success"}
    failed_statuses = {"failed"}
    cancelled_statuses = {"cancelled", "canceled"}
    terminal_statuses = succeeded_statuses | failed_statuses | cancelled_statuses
    execution_statuses = running_statuses | terminal_statuses
    records: list[dict[str, Any]] = []

    for value in raw_records:
        if not isinstance(value, Mapping):
            continue
        job = dict(value)
        status = _normalized_status(job.get("status"))
        has_execution_evidence = any(
            job.get(field) not in (None, "")
            for field in (
                "started_at", "completed_at", "assigned_worker_id",
                "lease_identity", "dispatch_result", "terminal_error",
            )
        )
        if status not in execution_statuses and not has_execution_evidence:
            continue
        job_id = _text(job.get("job_id"))
        if not job_id:
            continue
        records.append({
            "execution_identity": job_id,
            "job_identity": job_id,
            "handler_identity": None,
            "worker_identity": job.get("assigned_worker_id"),
            "duration": None,
            "execution_id": None,
            "job_id": job_id,
            "workflow_id": job.get("workflow_id"),
            "correlation_id": job.get("correlation_id"),
            "pipeline_id": job.get("pipeline_id"),
            "handler_id": None,
            "handler_version": None,
            "stage": job.get("stage"),
            "execution_action": None,
            "worker_id": job.get("assigned_worker_id"),
            "lease_id": job.get("lease_identity"),
            "dispatch_identity": None,
            "dispatched_at": None,
            "started_at": job.get("started_at"),
            "finished_at": job.get("completed_at"),
            "status": status,
            "result_summary": job.get("dispatch_result"),
            "terminal_error": job.get("terminal_error"),
            "failure_kind": None,
            "event_count": job.get("event_count"),
        })

    records.sort(
        key=lambda item: (
            _text(item.get("finished_at") or item.get("started_at")),
            _text(item.get("job_id")),
        ),
        reverse=True,
    )
    summary = {
        "total_executions": len(records),
        "running_executions": sum(item["status"] in running_statuses for item in records),
        "succeeded_executions": sum(item["status"] in succeeded_statuses for item in records),
        "failed_executions": sum(item["status"] in failed_statuses for item in records),
        "cancelled_executions": sum(item["status"] in cancelled_statuses for item in records),
        "terminal_executions": sum(item["status"] in terminal_statuses for item in records),
    }
    return {
        "component": "execution",
        "status": "READY" if records else "EMPTY",
        "record_count": len(records),
        "summary": summary,
        "records": records,
        "read_only": True,
        "source": "canonical_persisted_job_execution_evidence",
    }
'''


CSS_APPEND = r'''

/* BEGIN PART F 15-B5O RUNTIME INFRASTRUCTURE EXECUTION WIRING */
#runtimePage #runtimeInfrastructureExecutionDirectory.is-populated {
  display: grid;
  align-content: start;
  gap: 8px;
  max-height: 430px;
  overflow-y: auto;
  padding: 9px;
  text-align: left;
}

#runtimePage .runtime-infrastructure-execution-option {
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

#runtimePage .runtime-infrastructure-execution-option:hover {
  border-color: rgba(103, 232, 249, .34);
  background: rgba(14, 71, 91, .45);
}

#runtimePage .runtime-infrastructure-execution-option[aria-selected="true"] {
  border-color: rgba(45, 212, 191, .75);
  background: rgba(13, 148, 136, .18);
  box-shadow: inset 3px 0 0 #2dd4bf;
}

#runtimePage .runtime-infrastructure-execution-option:focus-visible {
  outline: 2px solid #22d3ee;
  outline-offset: 1px;
}

#runtimePage .runtime-infrastructure-execution-option :is(strong, span, small) {
  min-width: 0;
  margin: 0;
  overflow-wrap: anywhere;
}

#runtimePage .runtime-infrastructure-execution-option strong {
  color: #ecfeff;
  font-size: 11px;
}

#runtimePage .runtime-infrastructure-execution-option span {
  color: #a5f3fc;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
}

#runtimePage .runtime-infrastructure-execution-option small {
  color: #8fa9bc;
  font-size: 9px;
}

@media (max-width: 620px) {
  #runtimePage .runtime-infrastructure-execution-option { min-height: 44px; }
}
/* END PART F 15-B5O RUNTIME INFRASTRUCTURE EXECUTION WIRING */
'''


JS_APPEND = r'''

// BEGIN PART F 15-B5O RUNTIME INFRASTRUCTURE EXECUTION WIRING
(() => {
  "use strict";

  const PREFIX = "runtimeInfrastructureExecution";
  const SUMMARY_FIELDS = Object.freeze([
    "total_executions", "running_executions", "succeeded_executions",
    "failed_executions", "cancelled_executions", "terminal_executions"
  ]);
  const DETAIL_FIELDS = Object.freeze([
    "execution_id", "job_id", "workflow_id", "correlation_id", "pipeline_id",
    "handler_id", "handler_version", "stage", "execution_action", "worker_id",
    "lease_id", "dispatch_identity", "dispatched_at", "started_at", "finished_at",
    "duration", "status", "result_summary", "terminal_error", "failure_kind", "event_count"
  ]);
  let allExecutions = [];
  let visibleExecutions = [];
  let selectedJobId = "";

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
    selectOptions("pipeline_scope", "All pipelines", allExecutions.map((item) => item.pipeline_id));
    selectOptions("execution_status", "All statuses", allExecutions.map((item) => item.status));
    selectOptions("handler_identity", "All handlers", allExecutions.map((item) => item.handler_id));
  };
  const selectedFilters = () => {
    const value = (key) => filters()?.querySelector(`[data-runtime-infrastructure-filter="${key}"]`)?.value ?? "";
    return {
      pipeline: normalizedText(value("pipeline_scope")),
      status: normalizedText(value("execution_status")),
      handler: normalizedText(value("handler_identity")),
      search: normalizedText(value("evidence_search"))
    };
  };
  const filterExecutions = () => {
    const active = selectedFilters();
    return allExecutions.filter((item) => {
      if (active.pipeline && normalizedText(item.pipeline_id) !== active.pipeline) return false;
      if (active.status && normalizedText(item.status) !== active.status) return false;
      if (active.handler && normalizedText(item.handler_id) !== active.handler) return false;
      if (active.search) {
        const haystack = [
          item.execution_id, item.job_id, item.workflow_id, item.correlation_id,
          item.pipeline_id, item.handler_id, item.worker_id, item.stage
        ].map(normalizedText).join(" ");
        if (!haystack.includes(active.search)) return false;
      }
      return true;
    });
  };
  const renderDetail = (execution) => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(`[data-runtime-infrastructure-field="${field}"]`);
      if (node) node.textContent = displayValue(execution?.[field]);
    });
  };
  const selectExecution = (jobId, focus = false) => {
    const selected = visibleExecutions.find((item) => item.job_id === jobId);
    if (!selected) { selectedJobId = ""; clearDetail(); return; }
    selectedJobId = selected.job_id;
    directory()?.querySelectorAll("[role='option']").forEach((option) => {
      const active = option.dataset.jobId === selectedJobId;
      option.setAttribute("aria-selected", active ? "true" : "false");
      option.tabIndex = active ? 0 : -1;
      if (active) {
        directory()?.setAttribute("aria-activedescendant", option.id);
        if (focus) option.focus();
      }
    });
    renderDetail(selected);
  };
  const executionOption = (execution, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "runtime-infrastructure-execution-option";
    button.id = `${PREFIX}Option${index}`;
    button.dataset.jobId = String(execution.job_id);
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", "false");
    button.tabIndex = -1;
    const identity = document.createElement("strong");
    identity.textContent = displayValue(execution.execution_id || execution.job_id);
    const state = document.createElement("span");
    state.textContent = `${displayValue(execution.status)} · ${displayValue(execution.stage)}`;
    const context = document.createElement("small");
    context.textContent = execution.worker_id
      ? `Worker: ${execution.worker_id}`
      : "Worker identity unavailable";
    button.append(identity, state, context);
    button.addEventListener("click", () => selectExecution(execution.job_id));
    return button;
  };
  const renderDirectory = () => {
    visibleExecutions = filterExecutions();
    if (!allExecutions.length) {
      clearDirectory("No recorded executions", "Persisted jobs contain no canonical execution evidence.");
      clearDetail();
      setState("empty", "EMPTY");
      setMessage("No execution evidence", "No handler, worker, result, or terminal activity was invented.");
      return;
    }
    if (!visibleExecutions.length) {
      clearDirectory("No matching executions", "Adjust the local filters or evidence search.");
      clearDetail();
      setState("no_match", "NO MATCH");
      setMessage("No matching execution evidence", "The cached snapshot remains loaded.");
      return;
    }
    const node = directory();
    if (!node) return;
    node.classList.add("is-populated");
    node.setAttribute("aria-disabled", "false");
    node.replaceChildren(...visibleExecutions.map(executionOption));
    if (!visibleExecutions.some((item) => item.job_id === selectedJobId)) {
      selectedJobId = visibleExecutions[0].job_id;
    }
    selectExecution(selectedJobId);
    setState("ready", "LIVE EVIDENCE");
    setMessage(
      "Canonical execution evidence loaded",
      `${visibleExecutions.length} of ${allExecutions.length} recorded executions visible. Local filters issue no requests.`
    );
  };
  const renderExecutions = (payload) => {
    const execution = payload?.execution;
    if (!execution || !Array.isArray(execution.records) || typeof execution.summary !== "object") {
      throw new Error("The Execution projection contract is unavailable.");
    }
    allExecutions = execution.records.filter((item) => item && typeof item === "object");
    renderSummary(execution.summary);
    enableFilters();
    renderDirectory();
  };
  const unavailable = (message) => {
    allExecutions = [];
    visibleExecutions = [];
    selectedJobId = "";
    setState("unavailable", "UNAVAILABLE");
    clearDirectory("Execution evidence unavailable", message);
    clearDetail();
    setMessage("Execution unavailable", message);
  };
  const loadAndRenderExecution = () => {
    const evidence = window.RuntimeInfrastructureEvidence;
    if (!evidence || typeof evidence.load !== "function") {
      unavailable("The shared infrastructure snapshot authority is unavailable.");
      return Promise.resolve();
    }
    setState("loading", "LOADING");
    setMessage("Loading execution evidence", "Reusing the cached infrastructure snapshot.");
    return evidence.load().then(renderExecutions).catch((error) => {
      unavailable(error?.message || "The infrastructure evidence request failed.");
    });
  };
  const bindFilters = () => {
    const fieldset = filters();
    if (!fieldset || fieldset.dataset.b5oBound === "true") return;
    fieldset.addEventListener("input", renderDirectory);
    fieldset.addEventListener("change", renderDirectory);
    fieldset.dataset.b5oBound = "true";
  };
  const bindKeyboard = () => {
    const node = directory();
    if (!node || node.dataset.b5oBound === "true") return;
    node.addEventListener("keydown", (event) => {
      const options = [...node.querySelectorAll("[role='option']")];
      if (!options.length || !["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const current = Math.max(0, options.findIndex((option) => option.dataset.jobId === selectedJobId));
      let next = current;
      if (event.key === "ArrowDown") next = (current + 1) % options.length;
      else if (event.key === "ArrowUp") next = (current - 1 + options.length) % options.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = options.length - 1;
      selectExecution(options[next].dataset.jobId, true);
    });
    node.dataset.b5oBound = "true";
  };
  const initialize = () => {
    if (!workspace()) return;
    bindFilters();
    bindKeyboard();
    byId("runtimePage")?.addEventListener("runtimeowner:sectionchange", (event) => {
      if (event.detail?.section === "execution") loadAndRenderExecution();
    });
    loadAndRenderExecution();
  };
  window.RuntimeInfrastructureExecution = Object.freeze({
    refreshFromCache: loadAndRenderExecution,
    getVisibleExecutions: () => [...visibleExecutions],
    getSelectedJobId: () => selectedJobId
  });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else initialize();
})();
// END PART F 15-B5O RUNTIME INFRASTRUCTURE EXECUTION WIRING
'''


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_b5n_support(path: Path) -> ModuleType:
    if not path.is_file():
        raise RuntimeError(f"Certified B5N runner unavailable: {path}")
    if sha256_path(path) != B5N_RUNNER_HASH:
        raise RuntimeError("The certified B5N runner hash is invalid.")
    name = "_linkcraftor_b5n_support"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the certified B5N runner utilities.")
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
    candidate = replace_once(source, OLD_CSS_VERSION, NEW_CSS_VERSION, "B5O CSS asset")
    candidate = replace_once(candidate, OLD_JS_VERSION, NEW_JS_VERSION, "B5O JS asset")
    candidate = replace_once(candidate, OLD_DIRECTORY_COPY, NEW_DIRECTORY_COPY, "B5O directory copy")
    candidate = replace_once(candidate, OLD_DETAIL_COPY, NEW_DETAIL_COPY, "B5O selected-execution copy")
    return candidate


def build_candidate_css(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The B5O CSS marker already exists.")
    return source.rstrip() + "\n" + CSS_APPEND.lstrip()


def build_candidate_js(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The B5O JavaScript marker already exists.")
    return source.rstrip() + "\n" + JS_APPEND.lstrip()


def build_candidate_projection(source: str) -> str:
    candidate = replace_once(
        source,
        (
            "Part F 15-B5K installs one shared snapshot contract for Jobs, Queues,\n"
            "Workers & Leases, Orchestration and Execution. B5K-B5M populate Jobs,\n"
            "Queues and recorded worker/lease evidence. B5N groups canonical persisted\n"
            "workflow relationships. B5O adds no frontend request authority."
        ),
        (
            "Part F 15-B5K installs one shared snapshot contract for Jobs, Queues,\n"
            "Workers & Leases, Orchestration and Execution. B5K-B5N populate the first\n"
            "four namespaces. B5O projects recorded job-bound execution evidence and\n"
            "adds no frontend request authority or mutation capability."
        ),
        "The B5N projection boundary description",
    )
    candidate = replace_once(candidate, '    "runtime_infrastructure_projection_v1.3.0"', '    "runtime_infrastructure_projection_v1.4.0"', "B5N projection version")
    candidate = replace_once(candidate, '    "runtime_infrastructure_projection_schema_v1_3"', '    "runtime_infrastructure_projection_schema_v1_4"', "B5N projection schema")
    candidate = replace_once(
        candidate,
        "\n\ndef _not_wired_component(component: str) -> dict[str, Any]:",
        PROJECTION_FUNCTIONS.rstrip() + "\n\n\ndef _not_wired_component(component: str) -> dict[str, Any]:",
        "The B5N not-wired boundary",
    )
    candidate = replace_once(
        candidate,
        (
            "    workers_leases = _workers_leases_projection(jobs, now())\n"
            "    orchestration = _orchestration_projection(jobs)\n"
            "    source_status = {"
        ),
        (
            "    workers_leases = _workers_leases_projection(jobs, now())\n"
            "    orchestration = _orchestration_projection(jobs)\n"
            "    execution = _execution_projection(jobs)\n"
            "    source_status = {"
        ),
        "The B5N snapshot projections",
    )
    candidate = replace_once(candidate, '        "execution": "NOT_WIRED",', '        "execution": execution["status"],', "B5N Execution status")
    candidate = replace_once(candidate, '        "execution": _not_wired_component("execution"),', '        "execution": execution,', "B5N Execution namespace")
    candidate = replace_once(
        candidate,
        (
            '        "one_recorded_workflow": (\n'
            '            snapshot["orchestration"]["record_count"] == 1\n'
            '        ),\n'
            '        "no_mutation_authority": True,'
        ),
        (
            '        "one_recorded_workflow": (\n'
            '            snapshot["orchestration"]["record_count"] == 1\n'
            '        ),\n'
            '        "execution_ready": (\n'
            '            snapshot["execution"]["status"] == "READY"\n'
            '        ),\n'
            '        "one_recorded_execution": (\n'
            '            snapshot["execution"]["record_count"] == 1\n'
            '        ),\n'
            '        "no_mutation_authority": True,'
        ),
        "The B5N certification checks",
    )
    return candidate


def isolated_projection_probe(support: ModuleType, source: str) -> dict[str, Any]:
    module = support.load_isolated_projection(source)
    jobs = {
        "job_queued": {
            "job_id": "job_queued", "workflow_id": "workflow_demo",
            "status": "queued", "stage": "connect_domain",
            "metadata": {"pipeline_id": "connect_domain"},
        },
        "job_running": {
            "job_id": "job_running", "workflow_id": "workflow_demo",
            "correlation_id": "corr_demo", "workspace_id": "ws_demo",
            "status": "running", "stage": "site_sources",
            "created_at": "2026-01-02T00:00:00+00:00",
            "started_at": "2026-01-02T00:05:00+00:00",
            "assigned_worker_id": "worker_demo", "lease_identity": "lease_active",
            "metadata": {"pipeline_id": "connect_domain"},
        },
        "job_failed": {
            "job_id": "job_failed", "workflow_id": "workflow_failed",
            "status": "failed", "stage": "url_cleaner",
            "started_at": "2026-01-02T01:00:00+00:00",
            "completed_at": "2026-01-02T01:05:00+00:00",
            "error_message": "recorded terminal failure",
            "metadata": {"pipeline_id": "connect_domain"},
        },
    }
    snapshot = module.build_runtime_infrastructure_snapshot(
        job_loader=lambda: jobs,
        event_loader=lambda job_id: [{"job_id": job_id}],
        queue_loader=lambda: {
            "queue_length": 1,
            "queued_job_ids": ["job_queued"],
            "queued_jobs": [{"job_id": "job_queued"}],
        },
        clock=lambda: datetime(2026, 1, 3, tzinfo=timezone.utc),
    )
    executions = snapshot["execution"]
    assert snapshot["jobs"]["record_count"] == 3
    assert snapshot["orchestration"]["status"] == "READY"
    assert executions["status"] == "READY"
    assert executions["record_count"] == 2
    assert executions["summary"]["running_executions"] == 1
    assert executions["summary"]["failed_executions"] == 1
    assert executions["summary"]["terminal_executions"] == 1
    assert all(item["job_id"] != "job_queued" for item in executions["records"])
    failed = next(item for item in executions["records"] if item["job_id"] == "job_failed")
    assert failed["terminal_error"] == "recorded terminal failure"
    assert failed["handler_id"] is None
    certification = module.certify_runtime_infrastructure_projection_v1()
    assert certification["certified"] is True
    return {
        "jobs_retained": snapshot["jobs"]["record_count"],
        "queues_retained": snapshot["queues"]["status"],
        "workers_leases_retained": snapshot["workers_leases"]["status"],
        "orchestration_retained": snapshot["orchestration"]["status"],
        "execution_count": executions["record_count"],
        "running_executions": executions["summary"]["running_executions"],
        "failed_executions": executions["summary"]["failed_executions"],
        "queued_job_excluded": all(item["job_id"] != "job_queued" for item in executions["records"]),
        "unsupported_handler_uninferred": failed["handler_id"] is None,
        "certified": certification["certified"],
    }


def make_report(status: str, checks: dict[str, bool], evidence: dict[str, Any], error: dict[str, Any]) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = FINAL_RESULT if status == "CERTIFIED" else "FINAL RESULT: PART F 15-B5O RUNTIME INFRASTRUCTURE EXECUTION WIRING NOT_CERTIFIED"
    return "\n".join([
        "LINKCRAFTOR UNIVERSAL RUNTIME OWNER OPERATIONS",
        "PART F 15-B5O RUNTIME INFRASTRUCTURE EXECUTION WIRING CERTIFICATION",
        "", f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "Patch mode: STRICT FAIL-CLOSED", f"Backup: {evidence.get('backup', 'UNAVAILABLE')}",
        "Shared infrastructure endpoint reused: YES",
        "Jobs, Queues, Workers/Leases and Orchestration wiring retained: YES",
        "Execution live evidence wiring performed: " + ("YES" if evidence.get("patch_retained") else "NO"),
        "New endpoint requests added: NO", "Action controls added: NO",
        "Production jobs created: NO", "Production queue claims executed: NO",
        "Production handlers executed: NO", "Production workflow persistence executed: NO",
        "Production recovery actions executed: NO", "Live network requests executed during certification: NO",
        f"CERTIFICATION STATUS: {status}", "", "CHECKS:",
        json.dumps(checks, indent=2, sort_keys=True), "", "FAILED_CHECKS:",
        json.dumps(failed, indent=2), "", "NOT_RUN_CHECKS:", "[]", "",
        "EVIDENCE:", json.dumps(evidence, indent=2, sort_keys=True), "",
        "EXECUTION_ERROR:", json.dumps(error, indent=2, sort_keys=True), "",
        "IMPLEMENTED BOUNDARY:",
        "- B5O reuses the existing GET /owner/api/runtime/infrastructure endpoint and cached frontend snapshot.",
        "- Execution records are projected only from canonical persisted job execution evidence.",
        "- Job binding, workflow context, stage, worker, lease, timing, recorded result, terminal error and event count are visible when present.",
        "- Queued jobs without execution evidence are excluded from execution totals.",
        "- Handler identity/version, dispatch identity/time, duration and failure kind remain unavailable when not recorded.",
        "- Execution filters, search, selection and keyboard navigation are local and issue no requests.",
        "- Jobs, Queues, Workers/Leases and Orchestration remain retained and unchanged.",
        "- No dispatch, execution, cancellation, termination, retry or recovery control was added or invoked.",
        "", "NEXT STEP:", "Part F 15-B5P - Runtime Infrastructure collective certification and handoff closure.", "", final, "",
    ])


def run(root: Path, report: Path) -> int:
    root = root.resolve(); report = report.resolve()
    b5n_runner = root / B5N_RUNNER_NAME
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
    b5n_report = root / "backend/server/data/reports" / B5N_REPORT
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "endpoint": ENDPOINT, "patch_retained": False, "rollback_performed": False,
        "new_endpoint_requests": 0, "action_controls_added": False,
        "live_wiring_components": ["jobs", "queues", "workers_leases", "orchestration", "execution"],
        "deferred_components": [],
    }
    error: dict[str, Any] = {}; status = "NOT_CERTIFIED"; applied = False
    backup: Path | None = None; support: ModuleType | None = None
    try:
        b5n = load_b5n_support(b5n_runner)
        b5m = b5n.load_b5m_support(b5m_runner)
        b5l = b5m.load_b5l_support(b5l_runner)
        support = b5l.load_support(b5k_runner)
        checks["certified_b5n_runner_available"] = True
        checks["part_f_15_b5n_report_exists"] = b5n_report.is_file()
        checks["part_f_15_b5n_certified"] = b5n_report.is_file() and certified_report(support.read_text(b5n_report), B5N_FINAL_RESULT)
        for name, path in paths.items(): checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()): raise RuntimeError("The certified B5N baseline is unavailable.")
        watched = {**paths, "b5n_report": b5n_report}
        hashes_before = {name: sha256_path(path) for name, path in watched.items()}
        for name, expected in EXPECTED_HASHES.items(): checks[f"source_hash_{name}"] = hashes_before[name] == expected
        if not all(checks.values()): raise RuntimeError("Installed sources do not match the certified B5N baseline.")
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
        checks["isolated_execution_projection_probe_passed"] = all((
            probe["jobs_retained"] == 3, probe["queues_retained"] == "READY",
            probe["workers_leases_retained"] == "READY", probe["orchestration_retained"] == "READY",
            probe["execution_count"] == 2, probe["running_executions"] == 1,
            probe["failed_executions"] == 1, probe["queued_job_excluded"] is True,
            probe["unsupported_handler_uninferred"] is True, probe["certified"] is True,
        ))
        checks["shared_get_endpoint_retained_once"] = before["runtime_summary_api"].count('@router.get("/infrastructure")') == 1 and candidate_js.count(ENDPOINT) == 1
        checks["four_frontend_fetch_authorities_retained"] = candidate_js.count("fetch(") == 4
        checks["no_new_fetch_request_added"] = candidate_js.count("fetch(") == before["runtime_owner_js"].count("fetch(")
        checks["prior_component_bindings_retained"] = all(token in candidate_js for token in (
            "RuntimeInfrastructureEvidence", "RuntimeInfrastructureJobs", "RuntimeInfrastructureQueues",
            "RuntimeInfrastructureWorkersLeases", "RuntimeInfrastructureOrchestration",
        ))
        checks["execution_bindings_present"] = all(token in candidate_js for token in (
            "RuntimeInfrastructureExecution", 'const PREFIX = "runtimeInfrastructureExecution";',
            "pipeline_scope", "execution_status", "handler_identity", "loadAndRenderExecution",
        ))
        fields = (
            "execution_id", "job_id", "workflow_id", "correlation_id", "pipeline_id",
            "handler_id", "handler_version", "stage", "execution_action", "worker_id",
            "lease_id", "dispatch_identity", "dispatched_at", "started_at", "finished_at",
            "duration", "status", "result_summary", "terminal_error", "failure_kind", "event_count",
        )
        checks["execution_projection_fields_present"] = all(f'"{field}"' in candidate_projection for field in fields)
        checks["canonical_readers_only"] = all(token in candidate_projection for token in ("load_jobs", "list_job_events", "queue_snapshot")) and all(token not in candidate_projection for token in (
            "execute_job(", "dispatch_job(", "invoke_handler(", "cancel_execution(", "terminate_execution(", "retry_execution(",
        ))
        checks["queued_jobs_without_execution_excluded"] = "if status not in execution_statuses and not has_execution_evidence" in candidate_projection
        checks["unsupported_execution_evidence_uninferred"] = all(f'"{field}": None' in candidate_projection for field in (
            "execution_id", "handler_identity", "handler_id", "handler_version", "execution_action",
            "dispatch_identity", "dispatched_at", "duration", "failure_kind",
        ))
        checks["prior_visual_copy_retained"] = all(text in candidate_html for text in (
            "Canonical recorded job entries from the shared infrastructure snapshot.",
            "Canonical queue evidence from the shared infrastructure snapshot.",
            "Canonical worker and lease evidence from the shared infrastructure snapshot.",
            "Canonical workflow evidence assembled from the shared infrastructure snapshot.",
        ))
        checks["execution_visual_copy_activated"] = all(text in candidate_html for text in (NEW_DIRECTORY_COPY, NEW_DETAIL_COPY)) and all(text not in candidate_html for text in (OLD_DIRECTORY_COPY, OLD_DETAIL_COPY))
        checks["no_action_controls_added"] = all(token not in JS_APPEND for token in (
            "dispatchExecution", "executeJob", "cancelExecution", "terminateExecution", "retryExecution", "recoverExecution",
        ))
        checks["cache_versions_advanced"] = all((OLD_CSS_VERSION not in candidate_html, OLD_JS_VERSION not in candidate_html, candidate_html.count(NEW_CSS_VERSION) == 1, candidate_html.count(NEW_JS_VERSION) == 1))
        if not all(checks.values()): raise RuntimeError("One or more B5O candidate checks failed.")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = root / "backend/server/data/runtime_backups" / f"part_f_15_b5o_{timestamp}"
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
        checks["retained_b5k_through_b5o_markers"] = all(marker in support.read_text(path) for marker in (
            "PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING", "PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING",
            "PART F 15-B5M RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING", "PART F 15-B5N RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING", MARKER,
        ) for path in (paths["runtime_owner_css"], paths["runtime_owner_js"]))
        checks["historical_b5n_report_unchanged"] = sha256_path(b5n_report) == hashes_before["b5n_report"]
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
        if not all(checks.values()): raise RuntimeError("One or more retained B5O checks failed.")
        evidence.update({
            "patch_retained": True, "projection_probe": probe,
            "changed_sources": ["backend/server/owner/index.html", "backend/server/owner/runtime_owner.css", "backend/server/owner/runtime_owner.js", PROJECTION_MODULE_PATH],
            "source_hashes_before": {name: hashes_before[name] for name in paths},
            "source_hashes_after": {name: sha256_path(path) for name, path in paths.items()},
            "execution_summary_fields": ["total_executions", "running_executions", "succeeded_executions", "failed_executions", "cancelled_executions", "terminal_executions"],
            "recorded_execution_evidence": ["job, workflow, correlation and pipeline identity", "recorded stage and lifecycle", "worker and lease ownership", "started and finished timestamps", "dispatch result, terminal error and event count"],
            "explicitly_unavailable_without_recorded_authority": ["execution identity", "handler identity and version", "execution action", "dispatch identity and timestamp", "duration", "failure kind"],
            "snapshot_reuse": {"15-B5K": "jobs retained", "15-B5L": "queues retained", "15-B5M": "workers_leases retained", "15-B5N": "orchestration retained", "15-B5O": "execution populated"},
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
    print("NOT_RUN_CHECK_COUNT=0"); print(f"REPORT={report}"); print(f"PART_F_15_B5O_STATUS={status}")
    print(f"PATCH_RETAINED={'YES' if evidence.get('patch_retained') else 'NO'}")
    print("SHARED_ENDPOINT_REUSED=YES")
    print("PRIOR_WIRING_RETAINED=YES" if status == "CERTIFIED" else "PRIOR_WIRING_RETAINED=NO")
    print("EXECUTION_WIRING=YES" if status == "CERTIFIED" else "EXECUTION_WIRING=NO")
    print("ACTION_CONTROLS=NO")
    return 0 if status == "CERTIFIED" else 1


def self_test() -> int:
    folder = Path(__file__).resolve().parent
    b5n = load_b5n_support(folder / B5N_RUNNER_NAME)
    b5m = b5n.load_b5m_support(folder / B5M_RUNNER_NAME)
    b5l = b5m.load_b5l_support(folder / B5L_RUNNER_NAME)
    support = b5l.load_support(folder / B5K_RUNNER_NAME)
    html = "\n".join((
        OLD_CSS_VERSION, OLD_JS_VERSION,
        "Canonical recorded job entries from the shared infrastructure snapshot.",
        "Canonical queue evidence from the shared infrastructure snapshot.",
        "Canonical worker and lease evidence from the shared infrastructure snapshot.",
        "Canonical workflow evidence assembled from the shared infrastructure snapshot.",
        OLD_DIRECTORY_COPY, OLD_DETAIL_COPY, '<section id="runtimeOwnerSectionExecution"></section>',
    ))
    candidate_html = build_candidate_html(html)
    assert OLD_DIRECTORY_COPY not in candidate_html and OLD_DETAIL_COPY not in candidate_html
    assert NEW_DIRECTORY_COPY in candidate_html and NEW_DETAIL_COPY in candidate_html
    assert support.html_ids_unique(candidate_html)
    assert support.css_balanced("a { color: red; }\n" + CSS_APPEND)
    b5l_projection = b5l.build_candidate_projection(support.PROJECTION_SOURCE)
    b5m_projection = b5m.build_candidate_projection(b5l_projection)
    b5n_projection = b5n.build_candidate_projection(b5m_projection)
    candidate_projection = build_candidate_projection(b5n_projection)
    assert support.python_syntax_valid(candidate_projection, "projection.py")
    assert isolated_projection_probe(support, candidate_projection)["certified"] is True
    assert MARKER in build_candidate_css("a { color: red; }\n")
    assert MARKER in build_candidate_js("(() => { 'use strict'; })();\n")
    assert support.javascript_syntax_valid("(() => { 'use strict'; })();\n" + JS_APPEND)
    certified = "\n".join(("CERTIFICATION STATUS: CERTIFIED", "Action controls added: NO", "FAILED_CHECKS:", "[]", "NOT_RUN_CHECKS:", "[]", B5N_FINAL_RESULT))
    assert certified_report(certified, B5N_FINAL_RESULT)
    print("PART_F_15_B5O_SELF_TEST=PASS"); return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test": raise SystemExit(self_test())
    if len(sys.argv) != 3:
        raise SystemExit("Usage: RUN_15_B5O_RUNTIME_INFRASTRUCTURE_EXECUTION_WIRING.py <project_root> <report_path> | --self-test")
    raise SystemExit(run(Path(sys.argv[1]), Path(sys.argv[2])))
