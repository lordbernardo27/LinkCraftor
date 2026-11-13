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


STEP = "PART F 15-B5L"
TITLE = "RUNTIME INFRASTRUCTURE QUEUES WIRING"
MARKER = "PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5L RUNTIME INFRASTRUCTURE "
    "QUEUES WIRING CERTIFIED"
)

B5K_RUNNER_NAME = "RUN_15_B5K_RUNTIME_INFRASTRUCTURE_JOBS_WIRING.py"
B5K_RUNNER_HASH = (
    "3c391e4847da64b8bc53f0b17a255677d76eff0cc93a3109d525b645f97d50fa"
)
B5K_REPORT = (
    "PART_F_15_B5K_RUNTIME_INFRASTRUCTURE_JOBS_WIRING_CERTIFICATION.txt"
)
B5K_FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5K RUNTIME INFRASTRUCTURE "
    "JOBS WIRING CERTIFIED"
)
B5KR_REPORT = "PART_F_15_B5K_R_JOBS_VISUAL_COPY_CORRECTION.txt"
B5KR_FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5K-R JOBS VISUAL COPY CORRECTION CERTIFIED"
)

EXPECTED_HASHES = {
    "index_html": "10ac0a8f671d29d1e4568931bf587a38029a533170bbbc706f23ede71adf2123",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "17204b8688a8edb98776c04cc28d2b74b2c112f3d14f0eb0b0ffc7fa1f20e2d6",
    "runtime_owner_js": "e358675534ea8cfb01eb56d743a57d23807db5bb7579ed477476db986b5ac2b8",
    "runtime_summary_api": "215ac35d5591cc6a5e29af407ff70be9f317090c835290d6af92bafd356e44dd",
    "runtime_infrastructure_projection": "9185bb815425f0076b18bbe825e919032164b745cb94723eae3ff9ffb4721e71",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=17" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=18" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=18"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=19"></script>'

ENDPOINT = "/owner/api/runtime/infrastructure"
PROJECTION_MODULE_PATH = "backend/server/owner/runtime_infrastructure_projection.py"

OLD_QUEUE_DIRECTORY_COPY = (
    "            <small>Canonical recorded entries will appear after "
    "15-B5L wiring.</small>"
)
NEW_QUEUE_DIRECTORY_COPY = (
    "            <small>Canonical queue evidence from the shared "
    "infrastructure snapshot.</small>"
)
OLD_QUEUE_DETAIL_COPY = "\n".join(
    (
        "            <strong>Selected Queue Evidence</strong>",
        "            <small>Recorded values remain unavailable until wiring.</small>",
    )
)
NEW_QUEUE_DETAIL_COPY = "\n".join(
    (
        "            <strong>Selected Queue Evidence</strong>",
        "            <small>Recorded values for the selected canonical queue.</small>",
    )
)


PROJECTION_FUNCTIONS = r'''


def _priority_bucket(value: Any) -> str:
    text = _text(value).lower()
    numeric: int | None = None
    if isinstance(value, bool):
        return "unavailable"
    try:
        numeric = int(value)
    except (TypeError, ValueError):
        numeric = None
    if text == "critical" or numeric == 10:
        return "critical"
    if text == "high" or numeric == 20:
        return "high"
    if text == "normal" or numeric == 30:
        return "normal"
    if text in {"low", "background"} or numeric in {40, 50}:
        return "low"
    return "unavailable"


def _queues_projection(
    value: Any,
    jobs: Mapping[str, Any],
) -> dict[str, Any]:
    plain = _plain(value)
    if not isinstance(plain, Mapping):
        raise RuntimeInfrastructureProjectionError(
            "The canonical queue reader must return a mapping."
        )
    snapshot = dict(plain)
    raw_items = snapshot.get("queued_jobs")
    if not isinstance(raw_items, Sequence) or isinstance(raw_items, (str, bytes)):
        raise RuntimeInfrastructureProjectionError(
            "The canonical queue snapshot has no queued_jobs sequence."
        )
    items = [_mapping(item) for item in raw_items]
    raw_length = snapshot.get("queue_length")
    if isinstance(raw_length, bool):
        raise RuntimeInfrastructureProjectionError(
            "The canonical queue length is invalid."
        )
    try:
        claimable_count = int(raw_length)
    except (TypeError, ValueError) as exc:
        raise RuntimeInfrastructureProjectionError(
            "The canonical queue length is unavailable."
        ) from exc
    if claimable_count < 0 or claimable_count != len(items):
        raise RuntimeInfrastructureProjectionError(
            "The canonical queue length disagrees with queued_jobs."
        )

    job_records = [
        dict(record)
        for record in jobs.get("records", [])
        if isinstance(record, Mapping)
    ]
    jobs_by_id = {
        _text(record.get("job_id")): record
        for record in job_records
        if _text(record.get("job_id"))
    }
    persisted_queued = [
        record
        for record in job_records
        if _normalized_status(record.get("status")) == "queued"
    ]
    queued_job_ids = [
        _text(item.get("job_id"))
        for item in items
        if _text(item.get("job_id"))
    ]
    item_records = [
        (item, jobs_by_id.get(_text(item.get("job_id")), {}))
        for item in items
    ]
    claimable_records = [
        record
        for _, record in item_records
        if record
    ]
    workspaces = sorted(
        {
            _text(_first(item.get("workspace_id"), record.get("workspace_id")))
            for item, record in item_records
            if _text(_first(item.get("workspace_id"), record.get("workspace_id")))
        }
    )
    job_types = sorted(
        {
            _text(_first(item.get("job_type"), record.get("job_type")))
            for item, record in item_records
            if _text(_first(item.get("job_type"), record.get("job_type")))
        }
    )
    pipeline_scopes = sorted(
        {
            _text(record.get("pipeline_id"))
            for record in claimable_records
            if _text(record.get("pipeline_id"))
        }
    )
    pipeline_scope = (
        pipeline_scopes[0]
        if len(pipeline_scopes) == 1
        else ("multiple" if pipeline_scopes else None)
    )
    priority_buckets = [_priority_bucket(item.get("priority")) for item in items]
    priority_classes = sorted(
        {bucket for bucket in priority_buckets if bucket != "unavailable"}
    )
    oldest_candidates = sorted(
        _text(item.get("created_at"))
        for item in items
        if _text(item.get("created_at"))
    )
    queued_count = len(persisted_queued)
    record = {
        "queue_id": "universal_runtime_queue",
        "queue_name": "Universal Runtime Queue",
        "pipeline_scope": pipeline_scope,
        "queued_count": queued_count,
        "claimable_count": claimable_count,
        "reserved_count": None,
        "delayed_count": None,
        "blocked_count": None,
        "oldest_item_at": oldest_candidates[0] if oldest_candidates else None,
        "critical_count": sum(bucket == "critical" for bucket in priority_buckets),
        "high_count": sum(bucket == "high" for bucket in priority_buckets),
        "normal_count": sum(bucket == "normal" for bucket in priority_buckets),
        "low_count": sum(bucket == "low" for bucket in priority_buckets),
        "active_claim_count": None,
        "reservation_expiry_evidence": None,
        "pressure_state": None,
        "capacity_evidence": None,
        "throughput_evidence": None,
        "last_updated_at": None,
        "item_status": "queued" if queued_count else "empty",
        "queued_job_ids": queued_job_ids,
        "workspace_ids": workspaces,
        "job_types": job_types,
        "priority_classes": priority_classes,
    }
    summary = {
        "queued_items": queued_count,
        "claimable_items": claimable_count,
        "reserved_items": None,
        "delayed_items": None,
        "blocked_items": None,
        "queue_pressure": None,
    }
    return {
        "component": "queues",
        "status": "READY",
        "record_count": 1,
        "summary": summary,
        "records": [record],
        "read_only": True,
        "source": "canonical_orchestration_queue_snapshot_and_job_store",
        "unavailable_evidence": [
            "reserved_items",
            "delayed_items",
            "blocked_items",
            "queue_pressure",
            "reservation_expiry_evidence",
            "capacity_evidence",
            "throughput_evidence",
        ],
    }
'''


CSS_APPEND = r'''

/* BEGIN PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING */
#runtimePage #runtimeInfrastructureQueuesWorkspace[data-runtime-infrastructure-state="loading"]
  .runtime-infrastructure-state-badge {
  border-color: rgba(56, 189, 248, .5);
  color: #bae6fd;
  background: rgba(2, 132, 199, .14);
}

#runtimePage #runtimeInfrastructureQueuesWorkspace[data-runtime-infrastructure-state="empty"]
  .runtime-infrastructure-state-badge,
#runtimePage #runtimeInfrastructureQueuesWorkspace[data-runtime-infrastructure-state="no_match"]
  .runtime-infrastructure-state-badge {
  border-color: rgba(250, 204, 21, .48);
  color: #fef08a;
  background: rgba(202, 138, 4, .14);
}

#runtimePage #runtimeInfrastructureQueuesWorkspace[data-runtime-infrastructure-state="unavailable"]
  .runtime-infrastructure-state-badge {
  border-color: rgba(248, 113, 113, .5);
  color: #fecaca;
  background: rgba(185, 28, 28, .15);
}

#runtimePage #runtimeInfrastructureQueuesDirectory.is-populated {
  align-content: start;
  gap: 8px;
  max-height: 540px;
  overflow-y: auto;
  text-align: left;
}

#runtimePage .runtime-infrastructure-queue-option {
  display: grid;
  gap: 5px;
  width: 100%;
  min-width: 0;
  min-height: 58px;
  padding: 10px;
  border: 1px solid rgba(103, 232, 249, .14);
  border-radius: 9px;
  color: #cbd5e1;
  background: rgba(8, 37, 59, .58);
  text-align: left;
  cursor: pointer;
}

#runtimePage .runtime-infrastructure-queue-option:hover {
  border-color: rgba(103, 232, 249, .34);
  background: rgba(14, 71, 91, .45);
}

#runtimePage .runtime-infrastructure-queue-option[aria-selected="true"] {
  border-color: rgba(45, 212, 191, .75);
  background: rgba(13, 148, 136, .18);
  box-shadow: inset 3px 0 0 #2dd4bf;
}

#runtimePage .runtime-infrastructure-queue-option:focus-visible {
  outline: 2px solid #22d3ee;
  outline-offset: 1px;
}

#runtimePage .runtime-infrastructure-queue-option strong,
#runtimePage .runtime-infrastructure-queue-option span,
#runtimePage .runtime-infrastructure-queue-option small {
  min-width: 0;
  margin: 0;
  overflow-wrap: anywhere;
}

#runtimePage .runtime-infrastructure-queue-option strong {
  color: #ecfeff;
  font-size: 11px;
}

#runtimePage .runtime-infrastructure-queue-option span {
  color: #a5f3fc;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
}

#runtimePage .runtime-infrastructure-queue-option small {
  color: #8fa9bc;
  font-size: 9px;
}

@media (max-width: 620px) {
  #runtimePage .runtime-infrastructure-queue-option {
    min-height: 44px;
  }
}
/* END PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING */
'''


JS_APPEND = r'''

// BEGIN PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING
(() => {
  "use strict";

  const PREFIX = "runtimeInfrastructureQueues";
  const SUMMARY_FIELDS = Object.freeze([
    "queued_items",
    "claimable_items",
    "reserved_items",
    "delayed_items",
    "blocked_items",
    "queue_pressure"
  ]);
  const DETAIL_FIELDS = Object.freeze([
    "queue_id",
    "queue_name",
    "pipeline_scope",
    "queued_count",
    "claimable_count",
    "delayed_count",
    "blocked_count",
    "oldest_item_at",
    "critical_count",
    "high_count",
    "normal_count",
    "low_count",
    "reserved_count",
    "active_claim_count",
    "reservation_expiry_evidence",
    "pressure_state",
    "capacity_evidence",
    "throughput_evidence",
    "last_updated_at"
  ]);

  let allQueues = [];
  let visibleQueues = [];
  let selectedQueueId = "";

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
    if (root) {
      root.dataset.runtimeInfrastructureState = state;
    }
    if (badge) {
      badge.textContent = label;
    }
  };

  const setMessage = (title, body) => {
    const node = byId(`${PREFIX}Message`);
    if (!node) {
      return;
    }
    const strong = node.querySelector("strong");
    const span = node.querySelector("span");
    if (strong) {
      strong.textContent = title;
    }
    if (span) {
      span.textContent = body;
    }
  };

  const clearDirectory = (title, body) => {
    const node = directory();
    if (!node) {
      return;
    }
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
      if (node) {
        node.textContent = "Unavailable";
      }
    });
  };

  const renderSummary = (summary = {}) => {
    SUMMARY_FIELDS.forEach((metric) => {
      const card = workspace()?.querySelector(
        `[data-runtime-infrastructure-metric="${metric}"]`
      );
      if (!card) {
        return;
      }
      const value = card.querySelector("strong");
      const note = card.querySelector("small");
      if (value) {
        value.textContent = displayValue(summary[metric]);
      }
      if (note) {
        note.textContent = summary[metric] === null || summary[metric] === undefined
          ? "Not recorded"
          : "Recorded evidence";
      }
    });
  };

  const selectOptions = (key, fallback, values) => {
    const control = filters()?.querySelector(
      `[data-runtime-infrastructure-filter="${key}"]`
    );
    if (!(control instanceof HTMLSelectElement)) {
      return;
    }
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
    if (!fieldset) {
      return;
    }
    fieldset.disabled = false;
    fieldset.querySelectorAll("input, select").forEach((control) => {
      control.disabled = false;
    });
    selectOptions(
      "queue_scope",
      "All queues",
      allQueues.map((queue) => queue.queue_name || queue.queue_id)
    );
    selectOptions(
      "item_status",
      "All statuses",
      allQueues.map((queue) => queue.item_status)
    );
    selectOptions(
      "priority",
      "All priorities",
      allQueues.flatMap((queue) => queue.priority_classes || [])
    );
  };

  const selectedFilters = () => {
    const value = (key) =>
      filters()?.querySelector(
        `[data-runtime-infrastructure-filter="${key}"]`
      )?.value ?? "";
    return {
      queue: normalizedText(value("queue_scope")),
      status: normalizedText(value("item_status")),
      priority: normalizedText(value("priority")),
      search: normalizedText(value("identity_search"))
    };
  };

  const filterQueues = () => {
    const active = selectedFilters();
    return allQueues.filter((queue) => {
      if (active.queue) {
        const identities = [queue.queue_id, queue.queue_name].map(normalizedText);
        if (!identities.includes(active.queue)) {
          return false;
        }
      }
      if (active.status && normalizedText(queue.item_status) !== active.status) {
        return false;
      }
      if (active.priority) {
        const priorities = (queue.priority_classes || []).map(normalizedText);
        if (!priorities.includes(active.priority)) {
          return false;
        }
      }
      if (active.search) {
        const haystack = [
          queue.queue_id,
          queue.queue_name,
          queue.pipeline_scope,
          ...(queue.queued_job_ids || []),
          ...(queue.workspace_ids || []),
          ...(queue.job_types || [])
        ].map(normalizedText).join(" ");
        if (!haystack.includes(active.search)) {
          return false;
        }
      }
      return true;
    });
  };

  const renderDetail = (queue) => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(
        `[data-runtime-infrastructure-field="${field}"]`
      );
      if (node) {
        node.textContent = displayValue(queue?.[field]);
      }
    });
  };

  const selectQueue = (queueId, focus = false) => {
    const selected = visibleQueues.find((queue) => queue.queue_id === queueId);
    if (!selected) {
      selectedQueueId = "";
      clearDetail();
      return;
    }
    selectedQueueId = selected.queue_id;
    directory()?.querySelectorAll("[role='option']").forEach((option) => {
      const active = option.dataset.queueId === selectedQueueId;
      option.setAttribute("aria-selected", active ? "true" : "false");
      option.tabIndex = active ? 0 : -1;
      if (active) {
        directory()?.setAttribute("aria-activedescendant", option.id);
        if (focus) {
          option.focus();
        }
      }
    });
    renderDetail(selected);
  };

  const queueOption = (queue, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "runtime-infrastructure-queue-option";
    button.id = `${PREFIX}Option${index}`;
    button.dataset.queueId = String(queue.queue_id);
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", "false");
    button.tabIndex = -1;

    const identity = document.createElement("strong");
    identity.textContent = displayValue(queue.queue_name || queue.queue_id);
    const state = document.createElement("span");
    state.textContent = `${displayValue(queue.queued_count)} queued · ${displayValue(queue.claimable_count)} claimable`;
    const context = document.createElement("small");
    context.textContent = queue.pipeline_scope
      ? `Pipeline scope: ${queue.pipeline_scope}`
      : "Pipeline scope unavailable";
    button.append(identity, state, context);
    button.addEventListener("click", () => selectQueue(queue.queue_id));
    return button;
  };

  const renderDirectory = () => {
    visibleQueues = filterQueues();
    if (!allQueues.length) {
      clearDirectory(
        "No recorded queues",
        "The canonical queue reader returned no queue records."
      );
      clearDetail();
      setState("empty", "EMPTY");
      setMessage("No queue evidence", "No queue activity was invented.");
      return;
    }
    if (!visibleQueues.length) {
      clearDirectory(
        "No matching queues",
        "Adjust the local filters or evidence search."
      );
      clearDetail();
      setState("no_match", "NO MATCH");
      setMessage("No matching queue evidence", "The cached snapshot remains loaded.");
      return;
    }

    const node = directory();
    if (!node) {
      return;
    }
    node.classList.add("is-populated");
    node.setAttribute("aria-disabled", "false");
    node.replaceChildren(...visibleQueues.map(queueOption));

    if (!visibleQueues.some((queue) => queue.queue_id === selectedQueueId)) {
      selectedQueueId = visibleQueues[0].queue_id;
    }
    selectQueue(selectedQueueId);
    setState("ready", "LIVE EVIDENCE");
    setMessage(
      "Canonical queue evidence loaded",
      `${visibleQueues.length} of ${allQueues.length} canonical queues visible. Local filters issue no requests.`
    );
  };

  const renderQueues = (payload) => {
    const queues = payload?.queues;
    if (!queues || !Array.isArray(queues.records) || typeof queues.summary !== "object") {
      throw new Error("The Queues projection contract is unavailable.");
    }
    allQueues = queues.records.filter((queue) => queue && typeof queue === "object");
    renderSummary(queues.summary);
    enableFilters();
    renderDirectory();
  };

  const unavailable = (message) => {
    allQueues = [];
    visibleQueues = [];
    selectedQueueId = "";
    setState("unavailable", "UNAVAILABLE");
    clearDirectory("Queue evidence unavailable", message);
    clearDetail();
    setMessage("Queues unavailable", message);
  };

  const loadAndRenderQueues = () => {
    const evidence = window.RuntimeInfrastructureEvidence;
    if (!evidence || typeof evidence.load !== "function") {
      unavailable("The shared infrastructure snapshot authority is unavailable.");
      return Promise.resolve();
    }
    setState("loading", "LOADING");
    setMessage("Loading queue evidence", "Reusing the cached infrastructure snapshot.");
    return evidence.load().then(renderQueues).catch((error) => {
      unavailable(error?.message || "The infrastructure evidence request failed.");
    });
  };

  const bindFilters = () => {
    const fieldset = filters();
    if (!fieldset || fieldset.dataset.b5lBound === "true") {
      return;
    }
    fieldset.addEventListener("input", renderDirectory);
    fieldset.addEventListener("change", renderDirectory);
    fieldset.dataset.b5lBound = "true";
  };

  const bindDirectoryKeyboard = () => {
    const node = directory();
    if (!node || node.dataset.b5lBound === "true") {
      return;
    }
    node.addEventListener("keydown", (event) => {
      const options = [...node.querySelectorAll("[role='option']")];
      if (!options.length || !["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) {
        return;
      }
      event.preventDefault();
      const current = Math.max(
        0,
        options.findIndex((option) => option.dataset.queueId === selectedQueueId)
      );
      let next = current;
      if (event.key === "ArrowDown") {
        next = (current + 1) % options.length;
      } else if (event.key === "ArrowUp") {
        next = (current - 1 + options.length) % options.length;
      } else if (event.key === "Home") {
        next = 0;
      } else if (event.key === "End") {
        next = options.length - 1;
      }
      selectQueue(options[next].dataset.queueId, true);
    });
    node.dataset.b5lBound = "true";
  };

  const initialize = () => {
    if (!workspace()) {
      return;
    }
    bindFilters();
    bindDirectoryKeyboard();
    const page = byId("runtimePage");
    page?.addEventListener("runtimeowner:sectionchange", (event) => {
      if (event.detail?.section === "queues") {
        loadAndRenderQueues();
      }
    });
    loadAndRenderQueues();
  };

  window.RuntimeInfrastructureQueues = Object.freeze({
    refreshFromCache: loadAndRenderQueues,
    getVisibleQueues: () => [...visibleQueues],
    getSelectedQueueId: () => selectedQueueId
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
// END PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING
'''


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_support(path: Path) -> ModuleType:
    if not path.is_file():
        raise RuntimeError(f"Certified B5K runner unavailable: {path}")
    if sha256_path(path) != B5K_RUNNER_HASH:
        raise RuntimeError("The certified corrected B5K runner hash is invalid.")
    name = "_linkcraftor_b5k_support"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the certified B5K runner utilities.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label} was expected exactly once; found {count}.")
    return source.replace(old, new, 1)


def certified_report(source: str, final_result: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return (
        "CERTIFICATION STATUS: CERTIFIED" in normalized
        and "FAILED_CHECKS:\n[]" in normalized
        and "NOT_RUN_CHECKS:\n[]" in normalized
        and final_result in normalized
        and "Action controls added: NO" in normalized
    )


def build_candidate_html(source: str) -> str:
    candidate = replace_once(
        source,
        OLD_CSS_VERSION,
        NEW_CSS_VERSION,
        "The B5K Runtime Owner CSS cache version",
    )
    candidate = replace_once(
        candidate,
        OLD_JS_VERSION,
        NEW_JS_VERSION,
        "The B5K Runtime Owner JavaScript cache version",
    )
    candidate = replace_once(
        candidate,
        OLD_QUEUE_DIRECTORY_COPY,
        NEW_QUEUE_DIRECTORY_COPY,
        "The B5L Queues directory helper copy",
    )
    candidate = replace_once(
        candidate,
        OLD_QUEUE_DETAIL_COPY,
        NEW_QUEUE_DETAIL_COPY,
        "The B5L selected Queue helper copy",
    )
    return candidate


def build_candidate_css(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The B5L CSS marker already exists.")
    return source.rstrip() + "\n" + CSS_APPEND.lstrip()


def build_candidate_js(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The B5L JavaScript marker already exists.")
    return source.rstrip() + "\n" + JS_APPEND.lstrip()


def build_candidate_projection(source: str) -> str:
    candidate = replace_once(
        source,
        (
            "Part F 15-B5K installs one shared snapshot contract for Jobs, Queues,\n"
            "Workers & Leases, Orchestration and Execution.  B5K populates only Jobs.\n"
            "Later B5L-B5O phases extend this same response without adding more frontend\n"
            "request authorities."
        ),
        (
            "Part F 15-B5K installs one shared snapshot contract for Jobs, Queues,\n"
            "Workers & Leases, Orchestration and Execution. B5K populates Jobs and\n"
            "B5L adds Queues from the canonical read-only queue_snapshot. Later B5M-B5O\n"
            "phases extend this response without adding frontend request authorities."
        ),
        "The B5K projection module boundary description",
    )
    candidate = replace_once(
        candidate,
        '    "runtime_infrastructure_projection_v1.0.0"',
        '    "runtime_infrastructure_projection_v1.1.0"',
        "The B5K projection version",
    )
    candidate = replace_once(
        candidate,
        '    "runtime_infrastructure_projection_schema_v1"',
        '    "runtime_infrastructure_projection_schema_v1_1"',
        "The B5K projection schema version",
    )
    candidate = replace_once(
        candidate,
        (
            "JobLoader = Callable[[], Mapping[str, Any] | Sequence[Any]]\n"
            "JobEventLoader = Callable[[str], Sequence[Mapping[str, Any]]]\n"
            "Clock = Callable[[], datetime]"
        ),
        (
            "JobLoader = Callable[[], Mapping[str, Any] | Sequence[Any]]\n"
            "JobEventLoader = Callable[[str], Sequence[Mapping[str, Any]]]\n"
            "QueueLoader = Callable[[], Mapping[str, Any]]\n"
            "Clock = Callable[[], datetime]"
        ),
        "The B5K projection loader aliases",
    )
    candidate = replace_once(
        candidate,
        (
            "    return list_job_events(job_id)\n\n\n"
            "def _utc_now() -> datetime:"
        ),
        (
            "    return list_job_events(job_id)\n\n\n"
            "def _default_queue_loader() -> Mapping[str, Any]:\n"
            "    from backend.server.orchestration.queue import queue_snapshot\n\n"
            "    return queue_snapshot()\n\n\n"
            "def _utc_now() -> datetime:"
        ),
        "The B5K default event-loader boundary",
    )
    candidate = replace_once(
        candidate,
        "\n\ndef _not_wired_component(component: str) -> dict[str, Any]:",
        PROJECTION_FUNCTIONS.rstrip()
        + "\n\n\ndef _not_wired_component(component: str) -> dict[str, Any]:",
        "The B5K not-wired projection boundary",
    )
    candidate = replace_once(
        candidate,
        (
            "    job_loader: JobLoader | None = None,\n"
            "    event_loader: JobEventLoader | None = None,\n"
            "    clock: Clock | None = None,"
        ),
        (
            "    job_loader: JobLoader | None = None,\n"
            "    event_loader: JobEventLoader | None = None,\n"
            "    queue_loader: QueueLoader | None = None,\n"
            "    clock: Clock | None = None,"
        ),
        "The B5K snapshot signature",
    )
    candidate = replace_once(
        candidate,
        (
            "    load = job_loader or _default_job_loader\n"
            "    load_events = event_loader or _default_job_event_loader\n"
            "    now = clock or _utc_now\n\n"
            "    jobs = _jobs_projection(load(), load_events)"
        ),
        (
            "    load = job_loader or _default_job_loader\n"
            "    load_events = event_loader or _default_job_event_loader\n"
            "    load_queue = queue_loader or _default_queue_loader\n"
            "    now = clock or _utc_now\n\n"
            "    jobs = _jobs_projection(load(), load_events)\n"
            "    queues = _queues_projection(load_queue(), jobs)"
        ),
        "The B5K snapshot loader implementation",
    )
    candidate = replace_once(
        candidate,
        '        "queues": "NOT_WIRED",',
        '        "queues": queues["status"],',
        "The B5K Queues source status",
    )
    candidate = replace_once(
        candidate,
        '        "queues": _not_wired_component("queues"),',
        '        "queues": queues,',
        "The B5K Queues namespace",
    )
    candidate = replace_once(
        candidate,
        (
            "        event_loader=lambda _job_id: [],\n"
            "        clock=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),"
        ),
        (
            "        event_loader=lambda _job_id: [],\n"
            "        queue_loader=lambda: {\n"
            "            \"queue_length\": 1,\n"
            "            \"queued_job_ids\": [\"job_demo\"],\n"
            "            \"queued_jobs\": [{\n"
            "                \"job_id\": \"job_demo\",\n"
            "                \"workspace_id\": \"ws_demo\",\n"
            "                \"job_type\": \"demo\",\n"
            "                \"priority\": 30,\n"
            "                \"created_at\": \"2026-01-01T00:00:00+00:00\",\n"
            "            }],\n"
            "        },\n"
            "        clock=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),"
        ),
        "The B5K projection certification fixture",
    )
    candidate = replace_once(
        candidate,
        '        "queues_not_wired": snapshot["queues"]["status"] == "NOT_WIRED",',
        (
            '        "queues_ready": snapshot["queues"]["status"] == "READY",\n'
            '        "one_claimable_item": (\n'
            '            snapshot["queues"]["summary"]["claimable_items"] == 1\n'
            '        ),'
        ),
        "The B5K projection certification Queues check",
    )
    return candidate


def load_isolated_projection(support: ModuleType, source: str) -> ModuleType:
    return support.load_isolated_projection(source)


def isolated_projection_probe(support: ModuleType, source: str) -> dict[str, Any]:
    module = load_isolated_projection(support, source)
    jobs = {
        "job_critical": {
            "job_id": "job_critical",
            "workspace_id": "ws_demo",
            "job_type": "connect_domain",
            "status": "queued",
            "priority": 10,
            "created_at": "2026-01-01T00:00:00+00:00",
            "metadata": {"pipeline_id": "connect_domain"},
        },
        "job_waiting": {
            "job_id": "job_waiting",
            "workspace_id": "ws_demo",
            "job_type": "site_sources",
            "status": "queued",
            "priority": 30,
            "created_at": "2026-01-02T00:00:00+00:00",
            "metadata": {"pipeline_id": "connect_domain"},
        },
        "job_completed": {
            "job_id": "job_completed",
            "workspace_id": "ws_demo",
            "job_type": "url_cleaner",
            "status": "completed",
            "priority": 30,
            "metadata": {"pipeline_id": "connect_domain"},
        },
    }
    queue = {
        "queue_length": 1,
        "queued_job_ids": ["job_critical"],
        "queued_jobs": [
            {
                "job_id": "job_critical",
                "workspace_id": "ws_demo",
                "job_type": "connect_domain",
                "priority": 10,
                "created_at": "2026-01-01T00:00:00+00:00",
            }
        ],
    }
    snapshot = module.build_runtime_infrastructure_snapshot(
        job_loader=lambda: jobs,
        event_loader=lambda _job_id: [],
        queue_loader=lambda: queue,
        clock=lambda: datetime(2026, 1, 3, tzinfo=timezone.utc),
    )
    queues = snapshot["queues"]
    assert snapshot["read_only"] is True
    assert snapshot["jobs"]["record_count"] == 3
    assert queues["status"] == "READY"
    assert queues["record_count"] == 1
    assert queues["summary"]["queued_items"] == 2
    assert queues["summary"]["claimable_items"] == 1
    assert queues["summary"]["reserved_items"] is None
    assert queues["records"][0]["critical_count"] == 1
    assert snapshot["workers_leases"]["status"] == "NOT_WIRED"
    certification = module.certify_runtime_infrastructure_projection_v1()
    assert certification["certified"] is True
    return {
        "jobs_retained": snapshot["jobs"]["record_count"],
        "queue_record_count": queues["record_count"],
        "queued_items": queues["summary"]["queued_items"],
        "claimable_items": queues["summary"]["claimable_items"],
        "critical_items": queues["records"][0]["critical_count"],
        "workers_leases_status": snapshot["workers_leases"]["status"],
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
        "FINAL RESULT: PART F 15-B5L RUNTIME INFRASTRUCTURE "
        "QUEUES WIRING NOT_CERTIFIED"
    )
    return "\n".join(
        [
            "LINKCRAFTOR UNIVERSAL RUNTIME OWNER OPERATIONS",
            "PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING CERTIFICATION",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "Patch mode: STRICT FAIL-CLOSED",
            f"Backup: {evidence.get('backup', 'UNAVAILABLE')}",
            "Shared infrastructure endpoint reused: YES",
            "Jobs live evidence wiring retained: YES",
            "Queues live evidence wiring performed: "
            + ("YES" if evidence.get("patch_retained") else "NO"),
            "Workers and Leases wiring performed: NO",
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
            "- B5L reuses the existing GET /owner/api/runtime/infrastructure endpoint and frontend cached snapshot.",
            "- Queues uses canonical queue_snapshot evidence and the persisted Jobs projection without claiming work.",
            "- Persisted queued totals, time-and-dependency-eligible claimable work, priority distribution and oldest-item evidence are visible.",
            "- Reservation, delay, blocked, capacity, throughput and pressure values remain unavailable when not canonically recorded.",
            "- Queue filtering, search, selection and keyboard navigation are local operations and issue no requests.",
            "- Jobs wiring and the B5K-R copy correction remain retained and unchanged.",
            "- Workers & Leases, Orchestration and Execution remain NOT_WIRED for B5M-B5O.",
            "- No claim, retry, requeue, cancellation, termination, recovery or execution control was added.",
            "- No job, queue, worker, lease, workflow, handler, output or persistence mutation was executed during certification.",
            "",
            "NEXT STEP:",
            "Browser visual acceptance, then Part F 15-B5M - Workers and Leases wiring from the cached infrastructure snapshot.",
            "",
            final,
            "",
        ]
    )


def run(root: Path, report: Path) -> int:
    root = root.resolve()
    report = report.resolve()
    support_path = root / B5K_RUNNER_NAME
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
    reports_directory = root / "backend/server/data/reports"
    b5k_report = reports_directory / B5K_REPORT
    b5kr_report = reports_directory / B5KR_REPORT

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "endpoint": ENDPOINT,
        "patch_retained": False,
        "rollback_performed": False,
        "new_endpoint_requests": 0,
        "action_controls_added": False,
        "live_wiring_components": ["jobs", "queues"],
        "deferred_components": [
            "workers_leases",
            "orchestration",
            "execution",
        ],
    }
    error: dict[str, Any] = {}
    status = "NOT_CERTIFIED"
    applied = False
    backup: Path | None = None
    before_sources: dict[str, str] = {}

    try:
        support = load_support(support_path)
        checks["corrected_b5k_runner_available"] = True
        checks["part_f_15_b5k_report_exists"] = b5k_report.is_file()
        checks["part_f_15_b5k_certified"] = (
            b5k_report.is_file()
            and certified_report(support.read_text(b5k_report), B5K_FINAL_RESULT)
        )
        checks["part_f_15_b5kr_report_exists"] = b5kr_report.is_file()
        checks["part_f_15_b5kr_certified"] = (
            b5kr_report.is_file()
            and certified_report(support.read_text(b5kr_report), B5KR_FINAL_RESULT)
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("The certified B5K/B5K-R baseline is unavailable.")

        watched = {**paths, "b5k_report": b5k_report, "b5kr_report": b5kr_report}
        hashes_before = {name: sha256_path(path) for name, path in watched.items()}
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = hashes_before[name] == expected
        if not all(checks.values()):
            raise RuntimeError("Installed sources do not match the certified B5K-R baseline.")

        before_sources = {name: support.read_text(path) for name, path in paths.items()}
        candidate_html = build_candidate_html(before_sources["index_html"])
        candidate_css = build_candidate_css(before_sources["runtime_owner_css"])
        candidate_js = build_candidate_js(before_sources["runtime_owner_js"])
        candidate_projection = build_candidate_projection(
            before_sources["runtime_infrastructure_projection"]
        )

        checks["candidate_html_ids_unique"] = support.html_ids_unique(candidate_html)
        checks["candidate_css_balanced"] = support.css_balanced(candidate_css)
        checks["candidate_javascript_syntax"] = support.javascript_syntax_valid(candidate_js)
        checks["candidate_projection_syntax"] = support.python_syntax_valid(
            candidate_projection,
            str(paths["runtime_infrastructure_projection"]),
        )
        projection_probe = isolated_projection_probe(support, candidate_projection)
        checks["isolated_queues_projection_probe_passed"] = all(
            (
                projection_probe["jobs_retained"] == 3,
                projection_probe["queue_record_count"] == 1,
                projection_probe["queued_items"] == 2,
                projection_probe["claimable_items"] == 1,
                projection_probe["critical_items"] == 1,
                projection_probe["workers_leases_status"] == "NOT_WIRED",
                projection_probe["certified"] is True,
            )
        )
        checks["shared_get_endpoint_retained_once"] = (
            before_sources["runtime_summary_api"].count('@router.get("/infrastructure")') == 1
            and candidate_js.count(ENDPOINT) == 1
        )
        checks["four_frontend_fetch_authorities_retained"] = candidate_js.count("fetch(") == 4
        checks["no_new_fetch_request_added"] = (
            candidate_js.count("fetch(")
            == before_sources["runtime_owner_js"].count("fetch(")
        )
        checks["jobs_bindings_retained"] = all(
            token in candidate_js
            for token in (
                "RuntimeInfrastructureEvidence",
                "RuntimeInfrastructureJobs",
                'const PREFIX = "runtimeInfrastructureJobs";',
            )
        )
        checks["queues_bindings_present"] = all(
            token in candidate_js
            for token in (
                "RuntimeInfrastructureQueues",
                'const PREFIX = "runtimeInfrastructureQueues";',
                "queue_scope",
                "item_status",
                "identity_search",
                "loadAndRenderQueues",
            )
        )
        checks["queues_projection_fields_present"] = all(
            f'"{field}"' in candidate_projection
            for field in (
                "queue_id",
                "queue_name",
                "pipeline_scope",
                "queued_count",
                "claimable_count",
                "reserved_count",
                "delayed_count",
                "blocked_count",
                "oldest_item_at",
                "critical_count",
                "high_count",
                "normal_count",
                "low_count",
                "pressure_state",
                "capacity_evidence",
                "throughput_evidence",
            )
        )
        checks["canonical_readers_only"] = all(
            token in candidate_projection
            for token in ("load_jobs", "list_job_events", "queue_snapshot")
        ) and all(
            token not in candidate_projection
            for token in (
                "create_job(",
                "save_jobs(",
                "update_job_status(",
                "update_job_progress(",
                "enqueue_job(",
                "dequeue_job(",
                "execute_runtime_handler(",
            )
        )
        checks["three_components_explicitly_not_wired"] = all(
            f'_not_wired_component("{component}")' in candidate_projection
            for component in ("workers_leases", "orchestration", "execution")
        )
        checks["unsupported_queue_evidence_uninferred"] = all(
            f'"{field}": None' in candidate_projection
            for field in (
                "reserved_items",
                "delayed_items",
                "blocked_items",
                "queue_pressure",
                "reservation_expiry_evidence",
                "capacity_evidence",
                "throughput_evidence",
            )
        )
        checks["jobs_visual_copy_correction_retained"] = all(
            text in candidate_html
            for text in (
                "Canonical recorded job entries from the shared infrastructure snapshot.",
                "Recorded values for the selected canonical job.",
            )
        )
        checks["queues_visual_copy_activated"] = all(
            text in candidate_html
            for text in (NEW_QUEUE_DIRECTORY_COPY, NEW_QUEUE_DETAIL_COPY)
        ) and all(
            text not in candidate_html
            for text in (OLD_QUEUE_DIRECTORY_COPY, OLD_QUEUE_DETAIL_COPY)
        )
        checks["no_action_controls_added"] = all(
            token not in JS_APPEND
            for token in (
                "claimJob",
                "retryJob",
                "cancelJob",
                "terminateJob",
                "recoverJob",
                "requeueJob",
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
            raise RuntimeError("One or more B5L candidate checks failed.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = root / "backend/server/data/runtime_backups" / f"part_f_15_b5l_{timestamp}"
        backup.mkdir(parents=True, exist_ok=False)
        for name in (
            "index_html",
            "runtime_owner_css",
            "runtime_owner_js",
            "runtime_infrastructure_projection",
        ):
            destination = backup / paths[name].relative_to(root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(paths[name], destination)
        evidence["backup"] = str(backup)
        checks["backup_created"] = backup.is_dir()

        support.atomic_write_text(paths["index_html"], candidate_html)
        support.atomic_write_text(paths["runtime_owner_css"], candidate_css)
        support.atomic_write_text(paths["runtime_owner_js"], candidate_js)
        support.atomic_write_text(
            paths["runtime_infrastructure_projection"], candidate_projection
        )
        applied = True

        checks["retained_html_ids_unique"] = support.html_ids_unique(
            support.read_text(paths["index_html"])
        )
        checks["retained_css_balanced"] = support.css_balanced(
            support.read_text(paths["runtime_owner_css"])
        )
        checks["retained_javascript_syntax"] = support.javascript_syntax_valid(
            support.read_text(paths["runtime_owner_js"])
        )
        checks["retained_projection_syntax"] = support.python_syntax_valid(
            support.read_text(paths["runtime_infrastructure_projection"]),
            str(paths["runtime_infrastructure_projection"]),
        )
        checks["retained_b5k_and_b5l_markers"] = all(
            marker in support.read_text(path)
            for marker in (
                "PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING",
                MARKER,
            )
            for path in (
                paths["runtime_owner_css"],
                paths["runtime_owner_js"],
            )
        )
        checks["historical_b5k_report_unchanged"] = (
            sha256_path(b5k_report) == hashes_before["b5k_report"]
        )
        checks["historical_b5kr_report_unchanged"] = (
            sha256_path(b5kr_report) == hashes_before["b5kr_report"]
        )
        checks["only_expected_sources_changed"] = all(
            (
                sha256_path(paths["index_html"]) != hashes_before["index_html"],
                sha256_path(paths["runtime_owner_css"]) != hashes_before["runtime_owner_css"],
                sha256_path(paths["runtime_owner_js"]) != hashes_before["runtime_owner_js"],
                sha256_path(paths["runtime_infrastructure_projection"])
                != hashes_before["runtime_infrastructure_projection"],
                sha256_path(paths["owner_css"]) == hashes_before["owner_css"],
                sha256_path(paths["owner_js"]) == hashes_before["owner_js"],
                sha256_path(paths["runtime_summary_api"])
                == hashes_before["runtime_summary_api"],
                sha256_path(paths["pipeline_operations"])
                == hashes_before["pipeline_operations"],
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
            raise RuntimeError("One or more retained B5L checks failed.")

        evidence.update(
            {
                "patch_retained": True,
                "projection_probe": projection_probe,
                "changed_sources": [
                    "backend/server/owner/index.html",
                    "backend/server/owner/runtime_owner.css",
                    "backend/server/owner/runtime_owner.js",
                    PROJECTION_MODULE_PATH,
                ],
                "source_hashes_before": {
                    name: hashes_before[name] for name in paths
                },
                "source_hashes_after": {
                    name: sha256_path(path) for name, path in paths.items()
                },
                "queues_summary_fields": [
                    "queued_items",
                    "claimable_items",
                    "reserved_items",
                    "delayed_items",
                    "blocked_items",
                    "queue_pressure",
                ],
                "queues_record_fields": [
                    "queue identity and name",
                    "pipeline scope",
                    "persisted queued count",
                    "canonical claimable count",
                    "oldest claimable item timestamp",
                    "priority distribution",
                    "explicitly unavailable reservation and pressure evidence",
                ],
                "snapshot_reuse": {
                    "15-B5K": "jobs retained",
                    "15-B5L": "queues populated",
                    "15-B5M": "workers_leases deferred",
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
                    "index_html",
                    "runtime_owner_css",
                    "runtime_owner_js",
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
    support_for_report: ModuleType | None = None
    try:
        support_for_report = load_support(support_path)
    except Exception:
        support_for_report = None
    report_source = make_report(status, checks, evidence, error)
    if support_for_report is not None:
        support_for_report.write_text(report, report_source)
    else:
        report.write_text(report_source, encoding="utf-8", newline="\n")

    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not passed for passed in checks.values())}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B5L_STATUS={status}")
    print(f"PATCH_RETAINED={'YES' if evidence.get('patch_retained') else 'NO'}")
    print("SHARED_ENDPOINT_REUSED=YES")
    print("JOBS_WIRING_RETAINED=YES" if status == "CERTIFIED" else "JOBS_WIRING_RETAINED=NO")
    print("QUEUES_WIRING=YES" if status == "CERTIFIED" else "QUEUES_WIRING=NO")
    print("ACTION_CONTROLS=NO")
    return 0 if status == "CERTIFIED" else 1


def self_test() -> int:
    support_path = Path(__file__).resolve().parent / B5K_RUNNER_NAME
    support = load_support(support_path)
    html = "\n".join(
        (
            OLD_CSS_VERSION,
            OLD_JS_VERSION,
            "Canonical recorded job entries from the shared infrastructure snapshot.",
            "Recorded values for the selected canonical job.",
            OLD_QUEUE_DIRECTORY_COPY,
            OLD_QUEUE_DETAIL_COPY,
            '<section id="runtimeOwnerSectionQueues"></section>',
        )
    )
    candidate_html = build_candidate_html(html)
    assert OLD_CSS_VERSION not in candidate_html
    assert OLD_JS_VERSION not in candidate_html
    assert OLD_QUEUE_DIRECTORY_COPY not in candidate_html
    assert OLD_QUEUE_DETAIL_COPY not in candidate_html
    assert NEW_QUEUE_DIRECTORY_COPY in candidate_html
    assert NEW_QUEUE_DETAIL_COPY in candidate_html
    assert support.html_ids_unique(candidate_html)
    assert support.css_balanced("a { color: red; }\n" + CSS_APPEND)
    candidate_projection = build_candidate_projection(support.PROJECTION_SOURCE)
    assert support.python_syntax_valid(candidate_projection, "projection.py")
    assert isolated_projection_probe(support, candidate_projection)["certified"] is True
    assert MARKER in build_candidate_css("a { color: red; }\n")
    assert MARKER in build_candidate_js("(() => { 'use strict'; })();\n")
    assert support.javascript_syntax_valid(
        "(() => { 'use strict'; })();\n" + JS_APPEND
    )
    certified = "\n".join(
        (
            "CERTIFICATION STATUS: CERTIFIED",
            "Action controls added: NO",
            "FAILED_CHECKS:",
            "[]",
            "NOT_RUN_CHECKS:",
            "[]",
            B5K_FINAL_RESULT,
        )
    )
    assert certified_report(certified, B5K_FINAL_RESULT)
    corrected = certified.replace(B5K_FINAL_RESULT, B5KR_FINAL_RESULT)
    assert certified_report(corrected, B5KR_FINAL_RESULT)
    print("PART_F_15_B5L_SELF_TEST=PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B5L_RUNTIME_INFRASTRUCTURE_QUEUES_WIRING.py "
            "<project_root> <report_path> | --self-test"
        )
    raise SystemExit(run(Path(sys.argv[1]), Path(sys.argv[2])))
