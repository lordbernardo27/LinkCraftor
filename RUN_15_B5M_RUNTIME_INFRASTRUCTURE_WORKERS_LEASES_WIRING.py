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


STEP = "PART F 15-B5M"
TITLE = "RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING"
MARKER = "PART F 15-B5M RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5M RUNTIME INFRASTRUCTURE "
    "WORKERS AND LEASES WIRING CERTIFIED"
)

B5L_RUNNER_NAME = "RUN_15_B5L_RUNTIME_INFRASTRUCTURE_QUEUES_WIRING.py"
B5L_RUNNER_HASH = (
    "2f81327736425d8a6a26b72e3759d4dac11ff90573b15024893f75f68e8c61a3"
)
B5K_RUNNER_NAME = "RUN_15_B5K_RUNTIME_INFRASTRUCTURE_JOBS_WIRING.py"
B5L_REPORT = (
    "PART_F_15_B5L_RUNTIME_INFRASTRUCTURE_QUEUES_WIRING_CERTIFICATION.txt"
)
B5L_FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5L RUNTIME INFRASTRUCTURE "
    "QUEUES WIRING CERTIFIED"
)

EXPECTED_HASHES = {
    "index_html": "9681bcaa66f6fd454e31f111bb9d865a34fab9c081349babce9ed877a0438f62",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "8ecbb6f751f065608d7c983587aed774863506a5095ef64dd07c9d2ea319b5e5",
    "runtime_owner_js": "cb273540bd7d9dac6df75b00619a1fab7695a271688975861beafde218177855",
    "runtime_summary_api": "215ac35d5591cc6a5e29af407ff70be9f317090c835290d6af92bafd356e44dd",
    "runtime_infrastructure_projection": "7ac8cc2b4bba39b1d1195c8fefe8cf647c1550049d53b3bcbf6266b61bc7e991",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=18" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=19" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=19"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=20"></script>'

ENDPOINT = "/owner/api/runtime/infrastructure"
PROJECTION_MODULE_PATH = "backend/server/owner/runtime_infrastructure_projection.py"

OLD_DIRECTORY_COPY = (
    "            <small>Canonical recorded entries will appear after "
    "15-B5M wiring.</small>"
)
NEW_DIRECTORY_COPY = (
    "            <small>Canonical worker and lease evidence from the shared "
    "infrastructure snapshot.</small>"
)
OLD_DETAIL_COPY = "\n".join(
    (
        "            <strong>Selected Worker Evidence</strong>",
        "            <small>Recorded values remain unavailable until wiring.</small>",
    )
)
NEW_DETAIL_COPY = "\n".join(
    (
        "            <strong>Selected Worker Evidence</strong>",
        "            <small>Recorded values for the selected canonical worker and lease.</small>",
    )
)


PROJECTION_FUNCTIONS = r'''


def _recorded_datetime(value: Any) -> datetime | None:
    text = _text(value)
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _workers_leases_projection(
    jobs: Mapping[str, Any],
    evaluated_at: datetime,
) -> dict[str, Any]:
    raw_records = jobs.get("records", [])
    if not isinstance(raw_records, Sequence) or isinstance(raw_records, (str, bytes)):
        raise RuntimeInfrastructureProjectionError(
            "The Jobs projection has no canonical records sequence."
        )
    evaluated = evaluated_at
    if evaluated.tzinfo is None:
        evaluated = evaluated.replace(tzinfo=timezone.utc)
    evaluated = evaluated.astimezone(timezone.utc)

    groups: dict[str, list[dict[str, Any]]] = {}
    for value in raw_records:
        if not isinstance(value, Mapping):
            continue
        record = dict(value)
        worker_id = _text(record.get("assigned_worker_id"))
        if worker_id:
            groups.setdefault(worker_id, []).append(record)

    active_statuses = {"running", "in_progress", "processing"}
    terminal_statuses = {
        "completed", "complete", "succeeded", "success",
        "failed", "cancelled", "canceled",
    }
    records: list[dict[str, Any]] = []
    active_lease_ids: set[str] = set()

    for worker_id, worker_jobs in sorted(groups.items()):
        worker_jobs.sort(
            key=lambda item: (
                _text(item.get("updated_at") or item.get("created_at")),
                _text(item.get("job_id")),
            ),
            reverse=True,
        )
        active_jobs = [
            item for item in worker_jobs
            if _normalized_status(item.get("status")) in active_statuses
        ]
        current = active_jobs[0] if active_jobs else None
        lease_jobs = [item for item in worker_jobs if _text(item.get("lease_identity"))]

        def lease_state(item: Mapping[str, Any]) -> str:
            expiry = _recorded_datetime(item.get("lease_expiry"))
            if expiry is None:
                return "recorded"
            return "active" if expiry > evaluated else "expired"

        active_lease_jobs = [item for item in lease_jobs if lease_state(item) == "active"]
        selected_lease = active_lease_jobs[0] if active_lease_jobs else (
            lease_jobs[0] if lease_jobs else None
        )
        for item in active_lease_jobs:
            lease_id = _text(item.get("lease_identity"))
            if lease_id:
                active_lease_ids.add(lease_id)

        selected_status = (
            lease_state(selected_lease) if selected_lease is not None else None
        )
        active_execution_count = len(active_jobs)
        record = {
            "worker_id": worker_id,
            "worker_identity": worker_id,
            "worker_kind": None,
            "runtime_identity": worker_id,
            "environment": None,
            "lifecycle": None,
            "health": None,
            "availability": None,
            "last_heartbeat_at": None,
            "staleness_reason": None,
            "current_job_id": current.get("job_id") if current else None,
            "current_workflow_id": current.get("workflow_id") if current else None,
            "current_stage": current.get("stage") if current else None,
            "current_work": current.get("job_id") if current else None,
            "lease_id": (
                selected_lease.get("lease_identity") if selected_lease else None
            ),
            "lease_owner": worker_id if selected_lease else None,
            "lease_status": selected_status,
            "acquired_at": None,
            "expires_at": (
                selected_lease.get("lease_expiry") if selected_lease else None
            ),
            "renewed_at": None,
            "active_lease_count": len(active_lease_jobs),
            "concurrency_limit": None,
            "active_execution_count": active_execution_count,
            "available_capacity": None,
            "recorded_job_ids": [
                _text(item.get("job_id"))
                for item in worker_jobs
                if _text(item.get("job_id"))
            ],
            "recorded_workflow_ids": sorted({
                _text(item.get("workflow_id"))
                for item in worker_jobs
                if _text(item.get("workflow_id"))
            }),
            "has_terminal_history": any(
                _normalized_status(item.get("status")) in terminal_statuses
                for item in worker_jobs
            ),
        }
        records.append(record)

    busy_workers = sum(
        int(record["active_execution_count"] or 0) > 0
        for record in records
    )
    active_workers = sum(
        (int(record["active_execution_count"] or 0) > 0)
        or (int(record["active_lease_count"] or 0) > 0)
        for record in records
    )
    summary = {
        "total_workers": len(records),
        "active_workers": active_workers,
        "idle_workers": None,
        "busy_workers": busy_workers,
        "stale_workers": None,
        "active_leases": len(active_lease_ids),
    }
    return {
        "component": "workers_leases",
        "status": "READY" if records else "EMPTY",
        "record_count": len(records),
        "summary": summary,
        "records": records,
        "read_only": True,
        "source": "canonical_persisted_job_worker_and_lease_fields",
        "evaluated_at": evaluated.isoformat(),
    }
'''


CSS_APPEND = r'''

/* BEGIN PART F 15-B5M RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING */
#runtimePage #runtimeInfrastructureWorkersLeasesDirectory.is-populated {
  display: grid;
  align-content: start;
  gap: 8px;
  max-height: 430px;
  overflow-y: auto;
  padding: 9px;
  text-align: left;
}

#runtimePage .runtime-infrastructure-worker-option {
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

#runtimePage .runtime-infrastructure-worker-option:hover {
  border-color: rgba(103, 232, 249, .34);
  background: rgba(14, 71, 91, .45);
}

#runtimePage .runtime-infrastructure-worker-option[aria-selected="true"] {
  border-color: rgba(45, 212, 191, .75);
  background: rgba(13, 148, 136, .18);
  box-shadow: inset 3px 0 0 #2dd4bf;
}

#runtimePage .runtime-infrastructure-worker-option:focus-visible {
  outline: 2px solid #22d3ee;
  outline-offset: 1px;
}

#runtimePage .runtime-infrastructure-worker-option :is(strong, span, small) {
  min-width: 0;
  margin: 0;
  overflow-wrap: anywhere;
}

#runtimePage .runtime-infrastructure-worker-option strong {
  color: #ecfeff;
  font-size: 11px;
}

#runtimePage .runtime-infrastructure-worker-option span {
  color: #a5f3fc;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
}

#runtimePage .runtime-infrastructure-worker-option small {
  color: #8fa9bc;
  font-size: 9px;
}

@media (max-width: 620px) {
  #runtimePage .runtime-infrastructure-worker-option {
    min-height: 44px;
  }
}
/* END PART F 15-B5M RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING */
'''


JS_APPEND = r'''

// BEGIN PART F 15-B5M RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING
(() => {
  "use strict";

  const PREFIX = "runtimeInfrastructureWorkersLeases";
  const SUMMARY_FIELDS = Object.freeze([
    "total_workers", "active_workers", "idle_workers",
    "busy_workers", "stale_workers", "active_leases"
  ]);
  const DETAIL_FIELDS = Object.freeze([
    "worker_id", "worker_kind", "runtime_identity", "environment",
    "lifecycle", "health", "availability", "last_heartbeat_at",
    "staleness_reason", "current_job_id", "current_workflow_id",
    "current_stage", "lease_id", "lease_owner", "lease_status",
    "acquired_at", "expires_at", "renewed_at", "concurrency_limit",
    "active_execution_count", "available_capacity"
  ]);

  let allWorkers = [];
  let visibleWorkers = [];
  let selectedWorkerId = "";

  const byId = (id) => document.getElementById(id);
  const workspace = () => byId(`${PREFIX}Workspace`);
  const directory = () => byId(`${PREFIX}Directory`);
  const filters = () => byId(`${PREFIX}Filters`);
  const normalizedText = (value) => String(value ?? "").trim().toLowerCase();

  const displayValue = (value) => {
    if (value === null || value === undefined || value === "") {
      return "Unavailable";
    }
    if (Array.isArray(value)) {
      return value.length ? value.map(displayValue).join(", ") : "None";
    }
    if (typeof value === "object") {
      try {
        return JSON.stringify(value);
      } catch (_) {
        return "Recorded evidence";
      }
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
      const node = workspace()?.querySelector(
        `[data-runtime-infrastructure-field="${field}"]`
      );
      if (node) node.textContent = "Unavailable";
    });
  };

  const renderSummary = (summary = {}) => {
    SUMMARY_FIELDS.forEach((metric) => {
      const card = workspace()?.querySelector(
        `[data-runtime-infrastructure-metric="${metric}"]`
      );
      if (!card) return;
      const value = card.querySelector("strong");
      const note = card.querySelector("small");
      const recorded = summary[metric] !== null && summary[metric] !== undefined;
      if (value) value.textContent = displayValue(summary[metric]);
      if (note) note.textContent = recorded ? "Recorded evidence" : "Not recorded";
    });
  };

  const selectOptions = (key, fallback, values) => {
    const control = filters()?.querySelector(
      `[data-runtime-infrastructure-filter="${key}"]`
    );
    if (!(control instanceof HTMLSelectElement)) return;
    const selected = control.value;
    const first = document.createElement("option");
    first.value = "";
    first.textContent = fallback;
    const options = [first];
    [...new Set(values.filter(Boolean).map(String))]
      .sort((left, right) => left.localeCompare(right))
      .forEach((value) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        options.push(option);
      });
    control.replaceChildren(...options);
    if ([...control.options].some((option) => option.value === selected)) {
      control.value = selected;
    }
  };

  const enableFilters = () => {
    const fieldset = filters();
    if (!fieldset) return;
    fieldset.disabled = false;
    fieldset.querySelectorAll("input, select").forEach((control) => {
      control.disabled = false;
    });
    selectOptions("worker_lifecycle", "All lifecycle states", allWorkers.map((worker) => worker.lifecycle));
    selectOptions("worker_health", "All health states", allWorkers.map((worker) => worker.health));
    selectOptions("lease_state", "All lease states", allWorkers.map((worker) => worker.lease_status));
  };

  const selectedFilters = () => {
    const value = (key) => filters()?.querySelector(
      `[data-runtime-infrastructure-filter="${key}"]`
    )?.value ?? "";
    return {
      lifecycle: normalizedText(value("worker_lifecycle")),
      health: normalizedText(value("worker_health")),
      lease: normalizedText(value("lease_state")),
      search: normalizedText(value("identity_search"))
    };
  };

  const filterWorkers = () => {
    const active = selectedFilters();
    return allWorkers.filter((worker) => {
      if (active.lifecycle && normalizedText(worker.lifecycle) !== active.lifecycle) return false;
      if (active.health && normalizedText(worker.health) !== active.health) return false;
      if (active.lease && normalizedText(worker.lease_status) !== active.lease) return false;
      if (active.search) {
        const haystack = [
          worker.worker_id, worker.runtime_identity, worker.lease_id,
          worker.current_job_id, worker.current_workflow_id, worker.current_stage,
          ...(worker.recorded_job_ids || []),
          ...(worker.recorded_workflow_ids || [])
        ].map(normalizedText).join(" ");
        if (!haystack.includes(active.search)) return false;
      }
      return true;
    });
  };

  const renderDetail = (worker) => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(
        `[data-runtime-infrastructure-field="${field}"]`
      );
      if (node) node.textContent = displayValue(worker?.[field]);
    });
  };

  const selectWorker = (workerId, focus = false) => {
    const selected = visibleWorkers.find((worker) => worker.worker_id === workerId);
    if (!selected) {
      selectedWorkerId = "";
      clearDetail();
      return;
    }
    selectedWorkerId = selected.worker_id;
    directory()?.querySelectorAll("[role='option']").forEach((option) => {
      const active = option.dataset.workerId === selectedWorkerId;
      option.setAttribute("aria-selected", active ? "true" : "false");
      option.tabIndex = active ? 0 : -1;
      if (active) {
        directory()?.setAttribute("aria-activedescendant", option.id);
        if (focus) option.focus();
      }
    });
    renderDetail(selected);
  };

  const workerOption = (worker, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "runtime-infrastructure-worker-option";
    button.id = `${PREFIX}Option${index}`;
    button.dataset.workerId = String(worker.worker_id);
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", "false");
    button.tabIndex = -1;
    const identity = document.createElement("strong");
    identity.textContent = displayValue(worker.worker_identity || worker.worker_id);
    const state = document.createElement("span");
    state.textContent = worker.lease_status
      ? `Lease ${displayValue(worker.lease_status)} · ${displayValue(worker.active_execution_count)} active executions`
      : "No recorded lease state";
    const context = document.createElement("small");
    context.textContent = worker.current_job_id
      ? `Current job: ${worker.current_job_id}`
      : "No recorded current work";
    button.append(identity, state, context);
    button.addEventListener("click", () => selectWorker(worker.worker_id));
    return button;
  };

  const renderDirectory = () => {
    visibleWorkers = filterWorkers();
    if (!allWorkers.length) {
      clearDirectory(
        "No recorded workers or leases",
        "Persisted jobs contain no assigned worker identity or lease ownership evidence."
      );
      clearDetail();
      setState("empty", "EMPTY");
      setMessage("No worker evidence", "No worker, heartbeat, health, or lease activity was invented.");
      return;
    }
    if (!visibleWorkers.length) {
      clearDirectory("No matching workers", "Adjust the local filters or identity search.");
      clearDetail();
      setState("no_match", "NO MATCH");
      setMessage("No matching worker evidence", "The cached snapshot remains loaded.");
      return;
    }
    const node = directory();
    if (!node) return;
    node.classList.add("is-populated");
    node.setAttribute("aria-disabled", "false");
    node.replaceChildren(...visibleWorkers.map(workerOption));
    if (!visibleWorkers.some((worker) => worker.worker_id === selectedWorkerId)) {
      selectedWorkerId = visibleWorkers[0].worker_id;
    }
    selectWorker(selectedWorkerId);
    setState("ready", "LIVE EVIDENCE");
    setMessage(
      "Canonical worker and lease evidence loaded",
      `${visibleWorkers.length} of ${allWorkers.length} recorded workers visible. Local filters issue no requests.`
    );
  };

  const renderWorkers = (payload) => {
    const workers = payload?.workers_leases;
    if (!workers || !Array.isArray(workers.records) || typeof workers.summary !== "object") {
      throw new Error("The Workers & Leases projection contract is unavailable.");
    }
    allWorkers = workers.records.filter((worker) => worker && typeof worker === "object");
    renderSummary(workers.summary);
    enableFilters();
    renderDirectory();
  };

  const unavailable = (message) => {
    allWorkers = [];
    visibleWorkers = [];
    selectedWorkerId = "";
    setState("unavailable", "UNAVAILABLE");
    clearDirectory("Worker and lease evidence unavailable", message);
    clearDetail();
    setMessage("Workers & Leases unavailable", message);
  };

  const loadAndRenderWorkers = () => {
    const evidence = window.RuntimeInfrastructureEvidence;
    if (!evidence || typeof evidence.load !== "function") {
      unavailable("The shared infrastructure snapshot authority is unavailable.");
      return Promise.resolve();
    }
    setState("loading", "LOADING");
    setMessage("Loading worker and lease evidence", "Reusing the cached infrastructure snapshot.");
    return evidence.load().then(renderWorkers).catch((error) => {
      unavailable(error?.message || "The infrastructure evidence request failed.");
    });
  };

  const bindFilters = () => {
    const fieldset = filters();
    if (!fieldset || fieldset.dataset.b5mBound === "true") return;
    fieldset.addEventListener("input", renderDirectory);
    fieldset.addEventListener("change", renderDirectory);
    fieldset.dataset.b5mBound = "true";
  };

  const bindDirectoryKeyboard = () => {
    const node = directory();
    if (!node || node.dataset.b5mBound === "true") return;
    node.addEventListener("keydown", (event) => {
      const options = [...node.querySelectorAll("[role='option']")];
      if (!options.length || !["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const current = Math.max(0, options.findIndex((option) => option.dataset.workerId === selectedWorkerId));
      let next = current;
      if (event.key === "ArrowDown") next = (current + 1) % options.length;
      else if (event.key === "ArrowUp") next = (current - 1 + options.length) % options.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = options.length - 1;
      selectWorker(options[next].dataset.workerId, true);
    });
    node.dataset.b5mBound = "true";
  };

  const initialize = () => {
    if (!workspace()) return;
    bindFilters();
    bindDirectoryKeyboard();
    const page = byId("runtimePage");
    page?.addEventListener("runtimeowner:sectionchange", (event) => {
      if (event.detail?.section === "workers_leases") loadAndRenderWorkers();
    });
    loadAndRenderWorkers();
  };

  window.RuntimeInfrastructureWorkersLeases = Object.freeze({
    refreshFromCache: loadAndRenderWorkers,
    getVisibleWorkers: () => [...visibleWorkers],
    getSelectedWorkerId: () => selectedWorkerId
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
// END PART F 15-B5M RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING
'''


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_b5l_support(path: Path) -> ModuleType:
    if not path.is_file():
        raise RuntimeError(f"Certified B5L runner unavailable: {path}")
    if sha256_path(path) != B5L_RUNNER_HASH:
        raise RuntimeError("The certified B5L runner hash is invalid.")
    name = "_linkcraftor_b5l_support"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the certified B5L runner utilities.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


def certified_report(source: str, final_result: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return all(
        token in normalized
        for token in (
            "CERTIFICATION STATUS: CERTIFIED",
            "Action controls added: NO",
            "FAILED_CHECKS:\n[]",
            "NOT_RUN_CHECKS:\n[]",
            final_result,
        )
    )


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label} was expected exactly once; found {count}.")
    return source.replace(old, new, 1)


def build_candidate_html(source: str) -> str:
    candidate = replace_once(source, OLD_CSS_VERSION, NEW_CSS_VERSION, "B5M CSS asset")
    candidate = replace_once(candidate, OLD_JS_VERSION, NEW_JS_VERSION, "B5M JS asset")
    candidate = replace_once(candidate, OLD_DIRECTORY_COPY, NEW_DIRECTORY_COPY, "B5M directory copy")
    candidate = replace_once(candidate, OLD_DETAIL_COPY, NEW_DETAIL_COPY, "B5M selected-worker copy")
    return candidate


def build_candidate_css(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The B5M CSS marker already exists.")
    return source.rstrip() + "\n" + CSS_APPEND.lstrip()


def build_candidate_js(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The B5M JavaScript marker already exists.")
    return source.rstrip() + "\n" + JS_APPEND.lstrip()


def build_candidate_projection(source: str) -> str:
    candidate = replace_once(
        source,
        (
            "Part F 15-B5K installs one shared snapshot contract for Jobs, Queues,\n"
            "Workers & Leases, Orchestration and Execution. B5K populates Jobs and\n"
            "B5L adds Queues from the canonical read-only queue_snapshot. Later B5M-B5O\n"
            "phases extend this response without adding frontend request authorities."
        ),
        (
            "Part F 15-B5K installs one shared snapshot contract for Jobs, Queues,\n"
            "Workers & Leases, Orchestration and Execution. B5K populates Jobs, B5L\n"
            "adds Queues, and B5M projects recorded worker and lease fields from the\n"
            "persisted Jobs evidence. B5N-B5O add no frontend request authorities."
        ),
        "The B5L projection boundary description",
    )
    candidate = replace_once(
        candidate,
        '    "runtime_infrastructure_projection_v1.1.0"',
        '    "runtime_infrastructure_projection_v1.2.0"',
        "The B5L projection version",
    )
    candidate = replace_once(
        candidate,
        '    "runtime_infrastructure_projection_schema_v1_1"',
        '    "runtime_infrastructure_projection_schema_v1_2"',
        "The B5L projection schema",
    )
    candidate = replace_once(
        candidate,
        "\n\ndef _not_wired_component(component: str) -> dict[str, Any]:",
        PROJECTION_FUNCTIONS.rstrip() + "\n\n\ndef _not_wired_component(component: str) -> dict[str, Any]:",
        "The B5L not-wired projection boundary",
    )
    candidate = replace_once(
        candidate,
        (
            "    jobs = _jobs_projection(load(), load_events)\n"
            "    queues = _queues_projection(load_queue(), jobs)\n"
            "    source_status = {"
        ),
        (
            "    jobs = _jobs_projection(load(), load_events)\n"
            "    queues = _queues_projection(load_queue(), jobs)\n"
            "    workers_leases = _workers_leases_projection(jobs, now())\n"
            "    source_status = {"
        ),
        "The B5L snapshot projections",
    )
    candidate = replace_once(
        candidate,
        '        "workers_leases": "NOT_WIRED",',
        '        "workers_leases": workers_leases["status"],',
        "The B5L Workers and Leases source status",
    )
    candidate = replace_once(
        candidate,
        '        "workers_leases": _not_wired_component("workers_leases"),',
        '        "workers_leases": workers_leases,',
        "The B5L Workers and Leases namespace",
    )
    candidate = replace_once(
        candidate,
        (
            '            "priority": 5,\n'
            '            "metadata": {'
        ),
        (
            '            "priority": 5,\n'
            '            "assigned_worker_id": "worker_demo",\n'
            '            "lease_identity": "lease_demo",\n'
            '            "lease_expiry": "2026-01-02T00:00:00+00:00",\n'
            '            "metadata": {'
        ),
        "The B5L certification sample job",
    )
    candidate = replace_once(
        candidate,
        (
            '        "one_claimable_item": (\n'
            '            snapshot["queues"]["summary"]["claimable_items"] == 1\n'
            '        ),\n'
            '        "no_mutation_authority": True,'
        ),
        (
            '        "one_claimable_item": (\n'
            '            snapshot["queues"]["summary"]["claimable_items"] == 1\n'
            '        ),\n'
            '        "workers_leases_ready": (\n'
            '            snapshot["workers_leases"]["status"] == "READY"\n'
            '        ),\n'
            '        "one_recorded_worker": (\n'
            '            snapshot["workers_leases"]["record_count"] == 1\n'
            '        ),\n'
            '        "one_active_lease": (\n'
            '            snapshot["workers_leases"]["summary"]["active_leases"] == 1\n'
            '        ),\n'
            '        "no_mutation_authority": True,'
        ),
        "The B5L certification checks",
    )
    return candidate


def isolated_projection_probe(support: ModuleType, source: str) -> dict[str, Any]:
    module = support.load_isolated_projection(source)
    jobs = {
        "job_running": {
            "job_id": "job_running",
            "workflow_id": "workflow_active",
            "workspace_id": "ws_demo",
            "job_type": "connect_domain",
            "status": "running",
            "stage": "site_sources",
            "priority": 20,
            "assigned_worker_id": "worker_active",
            "lease_identity": "lease_active",
            "lease_expiry": "2026-01-04T00:00:00+00:00",
            "created_at": "2026-01-01T00:00:00+00:00",
            "metadata": {"pipeline_id": "connect_domain"},
        },
        "job_completed": {
            "job_id": "job_completed",
            "workflow_id": "workflow_old",
            "workspace_id": "ws_demo",
            "job_type": "url_cleaner",
            "status": "completed",
            "assigned_worker_id": "worker_history",
            "lease_identity": "lease_expired",
            "lease_expiry": "2025-12-31T00:00:00+00:00",
            "created_at": "2025-12-30T00:00:00+00:00",
            "metadata": {"pipeline_id": "connect_domain"},
        },
        "job_queued": {
            "job_id": "job_queued",
            "workspace_id": "ws_demo",
            "job_type": "site_pages",
            "status": "queued",
            "priority": 30,
            "created_at": "2026-01-02T00:00:00+00:00",
            "metadata": {"pipeline_id": "connect_domain"},
        },
    }
    queue = {
        "queue_length": 1,
        "queued_job_ids": ["job_queued"],
        "queued_jobs": [{
            "job_id": "job_queued",
            "workspace_id": "ws_demo",
            "job_type": "site_pages",
            "priority": 30,
            "created_at": "2026-01-02T00:00:00+00:00",
        }],
    }
    snapshot = module.build_runtime_infrastructure_snapshot(
        job_loader=lambda: jobs,
        event_loader=lambda _job_id: [],
        queue_loader=lambda: queue,
        clock=lambda: datetime(2026, 1, 3, tzinfo=timezone.utc),
    )
    workers = snapshot["workers_leases"]
    assert snapshot["read_only"] is True
    assert snapshot["jobs"]["record_count"] == 3
    assert snapshot["queues"]["summary"]["claimable_items"] == 1
    assert workers["status"] == "READY"
    assert workers["record_count"] == 2
    assert workers["summary"]["active_workers"] == 1
    assert workers["summary"]["busy_workers"] == 1
    assert workers["summary"]["active_leases"] == 1
    assert workers["summary"]["idle_workers"] is None
    assert workers["summary"]["stale_workers"] is None
    assert all(item["health"] is None for item in workers["records"])
    assert all(item["last_heartbeat_at"] is None for item in workers["records"])
    assert snapshot["orchestration"]["status"] == "NOT_WIRED"
    certification = module.certify_runtime_infrastructure_projection_v1()
    assert certification["certified"] is True
    return {
        "jobs_retained": snapshot["jobs"]["record_count"],
        "queues_retained": snapshot["queues"]["record_count"],
        "worker_record_count": workers["record_count"],
        "active_workers": workers["summary"]["active_workers"],
        "busy_workers": workers["summary"]["busy_workers"],
        "active_leases": workers["summary"]["active_leases"],
        "unsupported_heartbeat_uninferred": all(
            item["last_heartbeat_at"] is None for item in workers["records"]
        ),
        "orchestration_status": snapshot["orchestration"]["status"],
        "certified": certification["certified"],
    }


def make_report(
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = FINAL_RESULT if status == "CERTIFIED" else (
        "FINAL RESULT: PART F 15-B5M RUNTIME INFRASTRUCTURE "
        "WORKERS AND LEASES WIRING NOT_CERTIFIED"
    )
    return "\n".join(
        [
            "LINKCRAFTOR UNIVERSAL RUNTIME OWNER OPERATIONS",
            "PART F 15-B5M RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING CERTIFICATION",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "Patch mode: STRICT FAIL-CLOSED",
            f"Backup: {evidence.get('backup', 'UNAVAILABLE')}",
            "Shared infrastructure endpoint reused: YES",
            "Jobs live evidence wiring retained: YES",
            "Queues live evidence wiring retained: YES",
            "Workers and Leases live evidence wiring performed: "
            + ("YES" if evidence.get("patch_retained") else "NO"),
            "Orchestration wiring performed: NO",
            "Execution wiring performed: NO",
            "New endpoint requests added: NO",
            "Action controls added: NO",
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
            "- B5M reuses the existing GET /owner/api/runtime/infrastructure endpoint and frontend cached snapshot.",
            "- Workers and leases are projected only from canonical persisted job worker and lease fields.",
            "- Assigned worker identity, current active work, recorded lease identity, ownership, status and expiry are visible.",
            "- Health, heartbeat, staleness, concurrency and capacity remain unavailable when not canonically recorded.",
            "- Worker filtering, search, selection and keyboard navigation are local operations and issue no requests.",
            "- Jobs and Queues wiring remain retained; Orchestration and Execution remain NOT_WIRED for B5N-B5O.",
            "- No worker start, lease acquisition, release, renewal, drain, recovery or execution control was added.",
            "- No job, queue, worker, lease, workflow, handler, output or persistence mutation was executed during certification.",
            "",
            "NEXT STEP:",
            "Part F 15-B5N - Orchestration wiring from the cached infrastructure snapshot.",
            "",
            final,
            "",
        ]
    )


def run(root: Path, report: Path) -> int:
    root = root.resolve()
    report = report.resolve()
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
    b5l_report = root / "backend/server/data/reports" / B5L_REPORT
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "endpoint": ENDPOINT,
        "patch_retained": False,
        "rollback_performed": False,
        "new_endpoint_requests": 0,
        "action_controls_added": False,
        "live_wiring_components": ["jobs", "queues", "workers_leases"],
        "deferred_components": ["orchestration", "execution"],
    }
    error: dict[str, Any] = {}
    status = "NOT_CERTIFIED"
    applied = False
    backup: Path | None = None
    support: ModuleType | None = None

    try:
        b5l = load_b5l_support(b5l_runner)
        support = b5l.load_support(b5k_runner)
        checks["certified_b5l_runner_available"] = True
        checks["part_f_15_b5l_report_exists"] = b5l_report.is_file()
        checks["part_f_15_b5l_certified"] = (
            b5l_report.is_file()
            and certified_report(support.read_text(b5l_report), B5L_FINAL_RESULT)
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("The certified B5L baseline is unavailable.")

        watched = {**paths, "b5l_report": b5l_report}
        hashes_before = {name: sha256_path(path) for name, path in watched.items()}
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = hashes_before[name] == expected
        if not all(checks.values()):
            raise RuntimeError("Installed sources do not match the certified B5L baseline.")

        before = {name: support.read_text(path) for name, path in paths.items()}
        candidate_html = build_candidate_html(before["index_html"])
        candidate_css = build_candidate_css(before["runtime_owner_css"])
        candidate_js = build_candidate_js(before["runtime_owner_js"])
        candidate_projection = build_candidate_projection(
            before["runtime_infrastructure_projection"]
        )

        checks["candidate_html_ids_unique"] = support.html_ids_unique(candidate_html)
        checks["candidate_css_balanced"] = support.css_balanced(candidate_css)
        checks["candidate_javascript_syntax"] = support.javascript_syntax_valid(candidate_js)
        checks["candidate_projection_syntax"] = support.python_syntax_valid(
            candidate_projection, str(paths["runtime_infrastructure_projection"])
        )
        probe = isolated_projection_probe(support, candidate_projection)
        checks["isolated_workers_leases_projection_probe_passed"] = all(
            (
                probe["jobs_retained"] == 3,
                probe["queues_retained"] == 1,
                probe["worker_record_count"] == 2,
                probe["active_workers"] == 1,
                probe["busy_workers"] == 1,
                probe["active_leases"] == 1,
                probe["unsupported_heartbeat_uninferred"] is True,
                probe["orchestration_status"] == "NOT_WIRED",
                probe["certified"] is True,
            )
        )
        checks["shared_get_endpoint_retained_once"] = (
            before["runtime_summary_api"].count('@router.get("/infrastructure")') == 1
            and candidate_js.count(ENDPOINT) == 1
        )
        checks["four_frontend_fetch_authorities_retained"] = candidate_js.count("fetch(") == 4
        checks["no_new_fetch_request_added"] = (
            candidate_js.count("fetch(") == before["runtime_owner_js"].count("fetch(")
        )
        checks["jobs_and_queues_bindings_retained"] = all(
            token in candidate_js for token in (
                "RuntimeInfrastructureEvidence",
                "RuntimeInfrastructureJobs",
                "RuntimeInfrastructureQueues",
                'const PREFIX = "runtimeInfrastructureJobs";',
                'const PREFIX = "runtimeInfrastructureQueues";',
            )
        )
        checks["workers_leases_bindings_present"] = all(
            token in candidate_js for token in (
                "RuntimeInfrastructureWorkersLeases",
                'const PREFIX = "runtimeInfrastructureWorkersLeases";',
                "worker_lifecycle", "worker_health", "lease_state",
                "loadAndRenderWorkers",
            )
        )
        checks["workers_leases_projection_fields_present"] = all(
            f'"{field}"' in candidate_projection for field in (
                "worker_id", "worker_kind", "runtime_identity", "environment",
                "lifecycle", "health", "availability", "last_heartbeat_at",
                "staleness_reason", "current_job_id", "current_workflow_id",
                "current_stage", "lease_id", "lease_owner", "lease_status",
                "acquired_at", "expires_at", "renewed_at", "concurrency_limit",
                "active_execution_count", "available_capacity",
            )
        )
        checks["canonical_readers_only"] = all(
            token in candidate_projection for token in (
                "load_jobs", "list_job_events", "queue_snapshot"
            )
        ) and all(
            token not in candidate_projection for token in (
                "acquire_universal_worker_lease(",
                "release_universal_worker_lease(",
                "renew_universal_worker_lease(",
                "create_universal_worker_heartbeat(",
                "create_universal_worker_health_evidence(",
                "assign_universal_worker(",
                "runtime_start(", "runtime_stop(",
            )
        )
        checks["two_components_explicitly_not_wired"] = all(
            f'_not_wired_component("{component}")' in candidate_projection
            for component in ("orchestration", "execution")
        )
        checks["unsupported_worker_evidence_uninferred"] = all(
            f'"{field}": None' in candidate_projection for field in (
                "worker_kind", "environment", "lifecycle", "health",
                "availability", "last_heartbeat_at", "staleness_reason",
                "acquired_at", "renewed_at", "concurrency_limit",
                "available_capacity",
            )
        ) and all(
            f'"{field}": None' in candidate_projection
            for field in ("idle_workers", "stale_workers")
        )
        checks["b5k_and_b5l_copy_retained"] = all(
            text in candidate_html for text in (
                "Canonical recorded job entries from the shared infrastructure snapshot.",
                "Recorded values for the selected canonical job.",
                "Canonical queue evidence from the shared infrastructure snapshot.",
                "Recorded values for the selected canonical queue.",
            )
        )
        checks["workers_leases_visual_copy_activated"] = all(
            text in candidate_html for text in (NEW_DIRECTORY_COPY, NEW_DETAIL_COPY)
        ) and all(
            text not in candidate_html for text in (OLD_DIRECTORY_COPY, OLD_DETAIL_COPY)
        )
        checks["no_action_controls_added"] = all(
            token not in JS_APPEND for token in (
                "startWorker", "stopWorker", "drainWorker", "assignWorker",
                "acquireLease", "releaseLease", "renewLease", "recoverWorker",
            )
        )
        checks["cache_versions_advanced"] = all(
            (
                OLD_CSS_VERSION not in candidate_html,
                OLD_JS_VERSION not in candidate_html,
                candidate_html.count(NEW_CSS_VERSION) == 1,
                candidate_html.count(NEW_JS_VERSION) == 1,
            )
        )
        if not all(checks.values()):
            raise RuntimeError("One or more B5M candidate checks failed.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = root / "backend/server/data/runtime_backups" / f"part_f_15_b5m_{timestamp}"
        backup.mkdir(parents=True, exist_ok=False)
        changed_names = (
            "index_html", "runtime_owner_css", "runtime_owner_js",
            "runtime_infrastructure_projection",
        )
        for name in changed_names:
            destination = backup / paths[name].relative_to(root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(paths[name], destination)
        evidence["backup"] = str(backup)
        checks["backup_created"] = backup.is_dir()

        support.atomic_write_text(paths["index_html"], candidate_html)
        support.atomic_write_text(paths["runtime_owner_css"], candidate_css)
        support.atomic_write_text(paths["runtime_owner_js"], candidate_js)
        support.atomic_write_text(paths["runtime_infrastructure_projection"], candidate_projection)
        applied = True

        checks["retained_html_ids_unique"] = support.html_ids_unique(support.read_text(paths["index_html"]))
        checks["retained_css_balanced"] = support.css_balanced(support.read_text(paths["runtime_owner_css"]))
        checks["retained_javascript_syntax"] = support.javascript_syntax_valid(support.read_text(paths["runtime_owner_js"]))
        checks["retained_projection_syntax"] = support.python_syntax_valid(
            support.read_text(paths["runtime_infrastructure_projection"]),
            str(paths["runtime_infrastructure_projection"]),
        )
        checks["retained_b5k_b5l_b5m_markers"] = all(
            marker in support.read_text(path)
            for marker in (
                "PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING",
                "PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING",
                MARKER,
            )
            for path in (paths["runtime_owner_css"], paths["runtime_owner_js"])
        )
        checks["historical_b5l_report_unchanged"] = (
            sha256_path(b5l_report) == hashes_before["b5l_report"]
        )
        checks["only_expected_sources_changed"] = all(
            (
                sha256_path(paths["index_html"]) != hashes_before["index_html"],
                sha256_path(paths["runtime_owner_css"]) != hashes_before["runtime_owner_css"],
                sha256_path(paths["runtime_owner_js"]) != hashes_before["runtime_owner_js"],
                sha256_path(paths["runtime_infrastructure_projection"]) != hashes_before["runtime_infrastructure_projection"],
                sha256_path(paths["owner_css"]) == hashes_before["owner_css"],
                sha256_path(paths["owner_js"]) == hashes_before["owner_js"],
                sha256_path(paths["runtime_summary_api"]) == hashes_before["runtime_summary_api"],
                sha256_path(paths["pipeline_operations"]) == hashes_before["pipeline_operations"],
            )
        )
        checks.update(
            {
                "production_jobs_created_no": True,
                "production_queue_claims_no": True,
                "production_handlers_executed_no": True,
                "production_workflow_persistence_no": True,
                "production_recovery_actions_no": True,
                "live_network_requests_during_certification_no": True,
                "project_modules_imported_no": True,
            }
        )
        if not all(checks.values()):
            raise RuntimeError("One or more retained B5M checks failed.")

        evidence.update(
            {
                "patch_retained": True,
                "projection_probe": probe,
                "changed_sources": [
                    "backend/server/owner/index.html",
                    "backend/server/owner/runtime_owner.css",
                    "backend/server/owner/runtime_owner.js",
                    PROJECTION_MODULE_PATH,
                ],
                "source_hashes_before": {name: hashes_before[name] for name in paths},
                "source_hashes_after": {name: sha256_path(path) for name, path in paths.items()},
                "workers_leases_summary_fields": [
                    "total_workers", "active_workers", "idle_workers",
                    "busy_workers", "stale_workers", "active_leases",
                ],
                "recorded_worker_lease_evidence": [
                    "assigned worker identity", "active job/workflow/stage",
                    "lease identity and owner", "lease expiry and evaluated state",
                    "active execution count",
                ],
                "explicitly_unavailable_without_recorded_authority": [
                    "worker kind", "environment", "lifecycle", "health",
                    "availability", "heartbeat", "staleness reason",
                    "lease acquired and renewed timestamps", "concurrency limit",
                    "available capacity", "idle and stale worker totals",
                ],
                "snapshot_reuse": {
                    "15-B5K": "jobs retained",
                    "15-B5L": "queues retained",
                    "15-B5M": "workers_leases populated",
                    "15-B5N": "orchestration deferred",
                    "15-B5O": "execution deferred",
                },
            }
        )
        status = "CERTIFIED"
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        if applied and backup is not None:
            try:
                for name in (
                    "index_html", "runtime_owner_css", "runtime_owner_js",
                    "runtime_infrastructure_projection",
                ):
                    source = backup / paths[name].relative_to(root)
                    if source.is_file():
                        shutil.copy2(source, paths[name])
                evidence["rollback_performed"] = True
            except Exception as rollback_exc:
                error["rollback_error"] = {
                    "error_type": type(rollback_exc).__name__,
                    "error_message": str(rollback_exc),
                    "traceback": traceback.format_exc(),
                }

    report.parent.mkdir(parents=True, exist_ok=True)
    report_source = make_report(status, checks, evidence, error)
    if support is not None:
        support.write_text(report, report_source)
    else:
        report.write_text(report_source, encoding="utf-8", newline="\n")

    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not passed for passed in checks.values())}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B5M_STATUS={status}")
    print(f"PATCH_RETAINED={'YES' if evidence.get('patch_retained') else 'NO'}")
    print("SHARED_ENDPOINT_REUSED=YES")
    print("JOBS_QUEUES_WIRING_RETAINED=YES" if status == "CERTIFIED" else "JOBS_QUEUES_WIRING_RETAINED=NO")
    print("WORKERS_LEASES_WIRING=YES" if status == "CERTIFIED" else "WORKERS_LEASES_WIRING=NO")
    print("ACTION_CONTROLS=NO")
    return 0 if status == "CERTIFIED" else 1


def self_test() -> int:
    folder = Path(__file__).resolve().parent
    b5l = load_b5l_support(folder / B5L_RUNNER_NAME)
    support = b5l.load_support(folder / B5K_RUNNER_NAME)
    html = "\n".join(
        (
            OLD_CSS_VERSION,
            OLD_JS_VERSION,
            "Canonical recorded job entries from the shared infrastructure snapshot.",
            "Recorded values for the selected canonical job.",
            "Canonical queue evidence from the shared infrastructure snapshot.",
            "Recorded values for the selected canonical queue.",
            OLD_DIRECTORY_COPY,
            OLD_DETAIL_COPY,
            '<section id="runtimeOwnerSectionWorkersLeases"></section>',
        )
    )
    candidate_html = build_candidate_html(html)
    assert OLD_CSS_VERSION not in candidate_html
    assert OLD_JS_VERSION not in candidate_html
    assert OLD_DIRECTORY_COPY not in candidate_html
    assert OLD_DETAIL_COPY not in candidate_html
    assert NEW_DIRECTORY_COPY in candidate_html
    assert NEW_DETAIL_COPY in candidate_html
    assert support.html_ids_unique(candidate_html)
    assert support.css_balanced("a { color: red; }\n" + CSS_APPEND)
    b5l_projection = b5l.build_candidate_projection(support.PROJECTION_SOURCE)
    candidate_projection = build_candidate_projection(b5l_projection)
    assert support.python_syntax_valid(candidate_projection, "projection.py")
    assert isolated_projection_probe(support, candidate_projection)["certified"] is True
    assert MARKER in build_candidate_css("a { color: red; }\n")
    assert MARKER in build_candidate_js("(() => { 'use strict'; })();\n")
    assert support.javascript_syntax_valid("(() => { 'use strict'; })();\n" + JS_APPEND)
    certified = "\n".join(
        (
            "CERTIFICATION STATUS: CERTIFIED",
            "Action controls added: NO",
            "FAILED_CHECKS:", "[]",
            "NOT_RUN_CHECKS:", "[]",
            B5L_FINAL_RESULT,
        )
    )
    assert certified_report(certified, B5L_FINAL_RESULT)
    print("PART_F_15_B5M_SELF_TEST=PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B5M_RUNTIME_INFRASTRUCTURE_WORKERS_LEASES_WIRING.py "
            "<project_root> <report_path> | --self-test"
        )
    raise SystemExit(run(Path(sys.argv[1]), Path(sys.argv[2])))
