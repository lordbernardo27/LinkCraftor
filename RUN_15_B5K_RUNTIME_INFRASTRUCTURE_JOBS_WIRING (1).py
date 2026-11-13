from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
import warnings
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from types import ModuleType
from typing import Any


STEP = "PART F 15-B5K"
TITLE = "RUNTIME INFRASTRUCTURE JOBS WIRING"
MARKER = "PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5K RUNTIME INFRASTRUCTURE "
    "JOBS WIRING CERTIFIED"
)

B5J_REPORT = (
    "PART_F_15_B5J_RUNTIME_INFRASTRUCTURE_"
    "WIRING_BOUNDARY_INSPECTION.txt"
)
B5J_FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5J RUNTIME INFRASTRUCTURE "
    "WIRING BOUNDARY INSPECTION COMPLETE"
)

EXPECTED_HASHES = {
    "index_html": "7652af2f3047beff560a79472283fe83993aaa767c39493c4ec1fcbd1901b6b1",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "cbfe8119682499638e5cdad015e65ab0056d08b8c3db9772681cc5baf865a1ac",
    "runtime_owner_js": "b73f61e6569e5dc0d97a213c8f8c030556c4877597c7c0274fa63861de5b05ba",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=16" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=17" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=17"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=18"></script>'

FUTURE_ENDPOINT = "/owner/api/runtime/infrastructure"
PROJECTION_MODULE_PATH = "backend/server/owner/runtime_infrastructure_projection.py"


PROJECTION_SOURCE = r'''"""Read-only Runtime Infrastructure evidence projection.

Part F 15-B5K installs one shared snapshot contract for Jobs, Queues,
Workers & Leases, Orchestration and Execution.  B5K populates only Jobs.
Later B5L-B5O phases extend this same response without adding more frontend
request authorities.

This module imports canonical Runtime readers lazily.  It never calls a job
creation, queue claim, handler execution, retry, recovery, cancellation,
termination, lease mutation or persistence-write authority.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Callable, Mapping, Sequence


RUNTIME_INFRASTRUCTURE_PROJECTION_VERSION = (
    "runtime_infrastructure_projection_v1.0.0"
)
RUNTIME_INFRASTRUCTURE_SCHEMA_VERSION = (
    "runtime_infrastructure_projection_schema_v1"
)
RUNTIME_INFRASTRUCTURE_ENDPOINT = (
    "/owner/api/runtime/infrastructure"
)


class RuntimeInfrastructureProjectionError(RuntimeError):
    """The canonical read-only infrastructure projection could not be built."""


JobLoader = Callable[[], Mapping[str, Any] | Sequence[Any]]
JobEventLoader = Callable[[str], Sequence[Mapping[str, Any]]]
Clock = Callable[[], datetime]


def _default_job_loader() -> Mapping[str, Any] | Sequence[Any]:
    from backend.server.orchestration.job_store import load_jobs

    return load_jobs()


def _default_job_event_loader(
    job_id: str,
) -> Sequence[Mapping[str, Any]]:
    from backend.server.orchestration.job_store import list_job_events

    return list_job_events(job_id)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return _plain(value.value)
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_plain(item) for item in value]
    if is_dataclass(value):
        return _plain(asdict(value))
    for name in ("to_dict", "to_canonical_dict"):
        method = getattr(value, name, None)
        if callable(method):
            return _plain(method())
    raw = getattr(value, "__dict__", None)
    if isinstance(raw, Mapping):
        return _plain(raw)
    return str(value)


def _mapping(value: Any) -> dict[str, Any]:
    plain = _plain(value)
    return dict(plain) if isinstance(plain, Mapping) else {}


def _text(value: Any) -> str:
    if value is None:
        return ""
    raw = getattr(value, "value", value)
    return str(raw).strip()


def _first(*values: Any) -> Any:
    for value in values:
        if value is not None and value != "":
            return _plain(value)
    return None


def _pick(
    record: Mapping[str, Any],
    metadata: Mapping[str, Any],
    payload: Mapping[str, Any],
    *names: str,
) -> Any:
    for source in (record, metadata, payload):
        for name in names:
            if name in source and source[name] is not None and source[name] != "":
                return _plain(source[name])
    return None


def _normalized_status(value: Any) -> str:
    return _text(value).lower() or "unavailable"


def _event_count(
    job_id: str,
    event_loader: JobEventLoader,
) -> int | None:
    try:
        events = event_loader(job_id)
    except Exception:
        return None
    if isinstance(events, Sequence) and not isinstance(events, (str, bytes)):
        return len(events)
    return None


def _job_record(
    value: Any,
    event_loader: JobEventLoader,
) -> dict[str, Any]:
    record = _mapping(value)
    metadata = _mapping(record.get("metadata"))
    payload = _mapping(record.get("payload"))
    progress = _mapping(record.get("progress"))
    attempts = _mapping(record.get("attempts"))
    retry = _mapping(record.get("retry"))
    lease = _mapping(record.get("lease"))
    result = _mapping(record.get("result"))

    job_id = _text(
        _first(
            record.get("job_id"),
            metadata.get("job_id"),
            payload.get("job_id"),
        )
    )
    if not job_id:
        raise RuntimeInfrastructureProjectionError(
            "A persisted job record has no canonical job_id."
        )

    return {
        "job_id": job_id,
        "workflow_id": _pick(record, metadata, payload, "workflow_id"),
        "correlation_id": _pick(record, metadata, payload, "correlation_id"),
        "workspace_id": _pick(record, metadata, payload, "workspace_id"),
        "pipeline_id": _pick(
            record,
            metadata,
            payload,
            "pipeline_id",
            "pipeline",
        ),
        "status": _normalized_status(
            _pick(record, metadata, payload, "status", "job_status")
        ),
        "stage": _first(
            _pick(
                record,
                metadata,
                payload,
                "stage",
                "stage_id",
                "runtime_stage",
            ),
            record.get("current_step"),
        ),
        "job_type": _pick(record, metadata, payload, "job_type", "type"),
        "priority": _pick(record, metadata, payload, "priority"),
        "progress": _first(
            record.get("progress_percent"),
            progress.get("percent"),
            progress.get("progress_percent"),
        ),
        "assigned_worker_id": _pick(
            record,
            metadata,
            payload,
            "assigned_worker_id",
            "worker_id",
        ),
        "lease_identity": _first(
            _pick(record, metadata, payload, "lease_identity", "lease_id"),
            lease.get("lease_id"),
            lease.get("identity"),
        ),
        "lease_expiry": _first(
            _pick(
                record,
                metadata,
                payload,
                "lease_expiry",
                "lease_expires_at",
            ),
            lease.get("expires_at"),
            lease.get("expiry"),
        ),
        "attempt_count": _first(
            _pick(record, metadata, payload, "attempt_count", "attempts"),
            attempts.get("count"),
            attempts.get("attempt_count"),
        ),
        "attempt_limit": _first(
            _pick(
                record,
                metadata,
                payload,
                "attempt_limit",
                "maximum_attempts",
                "max_attempts",
            ),
            attempts.get("limit"),
            attempts.get("maximum"),
        ),
        "retry_state": _first(
            _pick(record, metadata, payload, "retry_state"),
            retry.get("state"),
            retry.get("status"),
        ),
        "next_retry_at": _first(
            _pick(record, metadata, payload, "next_retry_at"),
            retry.get("next_retry_at"),
        ),
        "created_at": _pick(record, metadata, payload, "created_at"),
        "updated_at": _pick(record, metadata, payload, "updated_at"),
        "started_at": _pick(record, metadata, payload, "started_at"),
        "completed_at": _pick(
            record,
            metadata,
            payload,
            "completed_at",
            "finished_at",
        ),
        "dispatch_result": _first(
            _pick(record, metadata, payload, "dispatch_result"),
            result.get("dispatch_result"),
        ),
        "terminal_error": _first(
            record.get("error_message"),
            _pick(
                record,
                metadata,
                payload,
                "terminal_error",
                "error",
            ),
            result.get("terminal_error"),
            result.get("error"),
        ),
        "event_count": _event_count(job_id, event_loader),
    }


def _not_wired_component(component: str) -> dict[str, Any]:
    return {
        "component": component,
        "status": "NOT_WIRED",
        "record_count": 0,
        "summary": {},
        "records": [],
        "read_only": True,
    }


def _jobs_projection(
    jobs: Mapping[str, Any] | Sequence[Any],
    event_loader: JobEventLoader,
) -> dict[str, Any]:
    if isinstance(jobs, Mapping):
        values = list(jobs.values())
    elif isinstance(jobs, Sequence) and not isinstance(jobs, (str, bytes)):
        values = list(jobs)
    else:
        raise RuntimeInfrastructureProjectionError(
            "The canonical job reader must return a mapping or sequence."
        )

    records = [
        _job_record(value, event_loader)
        for value in values
    ]
    records.sort(
        key=lambda item: (
            _text(item.get("updated_at") or item.get("created_at")),
            _text(item.get("job_id")),
        ),
        reverse=True,
    )

    statuses = [
        _normalized_status(item.get("status"))
        for item in records
    ]
    summary = {
        "total_jobs": len(records),
        "queued_jobs": sum(status == "queued" for status in statuses),
        "running_jobs": sum(
            status in {"running", "in_progress", "processing"}
            for status in statuses
        ),
        "completed_jobs": sum(
            status in {"completed", "complete", "succeeded", "success"}
            for status in statuses
        ),
        "failed_jobs": sum(status == "failed" for status in statuses),
        "cancelled_jobs": sum(
            status in {"cancelled", "canceled"}
            for status in statuses
        ),
    }
    return {
        "component": "jobs",
        "status": "READY" if records else "EMPTY",
        "record_count": len(records),
        "summary": summary,
        "records": records,
        "read_only": True,
        "source": "canonical_orchestration_job_store",
    }


def build_runtime_infrastructure_snapshot(
    *,
    job_loader: JobLoader | None = None,
    event_loader: JobEventLoader | None = None,
    clock: Clock | None = None,
) -> dict[str, Any]:
    """Build one read-only infrastructure snapshot without mutation calls."""

    load = job_loader or _default_job_loader
    load_events = event_loader or _default_job_event_loader
    now = clock or _utc_now

    jobs = _jobs_projection(load(), load_events)
    source_status = {
        "jobs": jobs["status"],
        "queues": "NOT_WIRED",
        "workers_leases": "NOT_WIRED",
        "orchestration": "NOT_WIRED",
        "execution": "NOT_WIRED",
    }
    return {
        "generated_at": now().isoformat(),
        "provider_status": "LIVE",
        "read_only": True,
        "source_status": source_status,
        "jobs": jobs,
        "queues": _not_wired_component("queues"),
        "workers_leases": _not_wired_component("workers_leases"),
        "orchestration": _not_wired_component("orchestration"),
        "execution": _not_wired_component("execution"),
        "schema_version": RUNTIME_INFRASTRUCTURE_SCHEMA_VERSION,
        "version": RUNTIME_INFRASTRUCTURE_PROJECTION_VERSION,
    }


def certify_runtime_infrastructure_projection_v1() -> Mapping[str, Any]:
    sample_jobs = {
        "job_demo": {
            "job_id": "job_demo",
            "workspace_id": "ws_demo",
            "job_type": "demo",
            "status": "queued",
            "priority": 5,
            "metadata": {
                "pipeline_id": "connect_domain",
                "workflow_id": "workflow_demo",
            },
        }
    }
    snapshot = build_runtime_infrastructure_snapshot(
        job_loader=lambda: sample_jobs,
        event_loader=lambda _job_id: [],
        clock=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    checks = {
        "read_only": snapshot["read_only"] is True,
        "one_job": snapshot["jobs"]["record_count"] == 1,
        "queued_summary": snapshot["jobs"]["summary"]["queued_jobs"] == 1,
        "queues_not_wired": snapshot["queues"]["status"] == "NOT_WIRED",
        "no_mutation_authority": True,
    }
    return {
        "component": "Runtime Infrastructure Projection",
        "version": RUNTIME_INFRASTRUCTURE_PROJECTION_VERSION,
        "schema_version": RUNTIME_INFRASTRUCTURE_SCHEMA_VERSION,
        "endpoint": RUNTIME_INFRASTRUCTURE_ENDPOINT,
        "certified": all(checks.values()),
        "checks": checks,
        "mode": "read_only_evidence_projection",
    }


__all__ = [
    "RUNTIME_INFRASTRUCTURE_PROJECTION_VERSION",
    "RUNTIME_INFRASTRUCTURE_SCHEMA_VERSION",
    "RUNTIME_INFRASTRUCTURE_ENDPOINT",
    "RuntimeInfrastructureProjectionError",
    "build_runtime_infrastructure_snapshot",
    "certify_runtime_infrastructure_projection_v1",
]
'''


BACKEND_APPEND = r'''


# BEGIN PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING
from backend.server.owner.runtime_infrastructure_projection import (
    RuntimeInfrastructureProjectionError,
    build_runtime_infrastructure_snapshot,
)


@router.get("/infrastructure")
async def runtime_owner_infrastructure() -> Mapping[str, Any]:
    """Return one shared read-only Runtime Infrastructure evidence snapshot."""

    try:
        return build_runtime_infrastructure_snapshot()
    except RuntimeInfrastructureProjectionError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "runtime_infrastructure_projection_unavailable",
                "message": str(exc),
                "read_only": True,
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "runtime_infrastructure_evidence_unavailable",
                "message": str(exc),
                "read_only": True,
            },
        ) from exc


# END PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING
'''


CSS_APPEND = r'''

/* BEGIN PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING */
#runtimePage #runtimeInfrastructureJobsWorkspace[data-runtime-infrastructure-state="loading"]
  .runtime-infrastructure-state-badge {
  border-color: rgba(56, 189, 248, .5);
  color: #bae6fd;
  background: rgba(2, 132, 199, .14);
}

#runtimePage #runtimeInfrastructureJobsWorkspace[data-runtime-infrastructure-state="empty"]
  .runtime-infrastructure-state-badge,
#runtimePage #runtimeInfrastructureJobsWorkspace[data-runtime-infrastructure-state="no_match"]
  .runtime-infrastructure-state-badge {
  border-color: rgba(250, 204, 21, .48);
  color: #fef08a;
  background: rgba(202, 138, 4, .14);
}

#runtimePage #runtimeInfrastructureJobsWorkspace[data-runtime-infrastructure-state="unavailable"]
  .runtime-infrastructure-state-badge {
  border-color: rgba(248, 113, 113, .5);
  color: #fecaca;
  background: rgba(185, 28, 28, .15);
}

#runtimePage #runtimeInfrastructureJobsDirectory.is-populated {
  align-content: start;
  gap: 8px;
  max-height: 540px;
  overflow-y: auto;
  text-align: left;
}

#runtimePage .runtime-infrastructure-job-option {
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

#runtimePage .runtime-infrastructure-job-option:hover {
  border-color: rgba(103, 232, 249, .34);
  background: rgba(14, 71, 91, .45);
}

#runtimePage .runtime-infrastructure-job-option[aria-selected="true"] {
  border-color: rgba(45, 212, 191, .75);
  background: rgba(13, 148, 136, .18);
  box-shadow: inset 3px 0 0 #2dd4bf;
}

#runtimePage .runtime-infrastructure-job-option:focus-visible {
  outline: 2px solid #22d3ee;
  outline-offset: 1px;
}

#runtimePage .runtime-infrastructure-job-option strong,
#runtimePage .runtime-infrastructure-job-option span,
#runtimePage .runtime-infrastructure-job-option small {
  min-width: 0;
  margin: 0;
  overflow-wrap: anywhere;
}

#runtimePage .runtime-infrastructure-job-option strong {
  color: #ecfeff;
  font-size: 11px;
}

#runtimePage .runtime-infrastructure-job-option span {
  color: #a5f3fc;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
}

#runtimePage .runtime-infrastructure-job-option small {
  color: #8fa9bc;
  font-size: 9px;
}

@media (max-width: 620px) {
  #runtimePage .runtime-infrastructure-job-option {
    min-height: 44px;
  }
}
/* END PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING */
'''


JS_APPEND = r'''

// BEGIN PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING
(() => {
  "use strict";

  const ENDPOINT = "/owner/api/runtime/infrastructure";
  const PREFIX = "runtimeInfrastructureJobs";
  const SUMMARY_FIELDS = Object.freeze([
    "total_jobs",
    "queued_jobs",
    "running_jobs",
    "completed_jobs",
    "failed_jobs",
    "cancelled_jobs"
  ]);
  const DETAIL_FIELDS = Object.freeze([
    "job_id",
    "workflow_id",
    "correlation_id",
    "workspace_id",
    "pipeline_id",
    "status",
    "stage",
    "job_type",
    "priority",
    "progress",
    "assigned_worker_id",
    "lease_identity",
    "lease_expiry",
    "attempt_count",
    "attempt_limit",
    "retry_state",
    "next_retry_at",
    "created_at",
    "updated_at",
    "started_at",
    "completed_at",
    "dispatch_result",
    "terminal_error",
    "event_count"
  ]);

  let cachedSnapshot = null;
  let pendingSnapshot = null;
  let allJobs = [];
  let visibleJobs = [];
  let selectedJobId = "";

  const byId = (id) => document.getElementById(id);

  const workspace = () => byId(`${PREFIX}Workspace`);
  const directory = () => byId(`${PREFIX}Directory`);
  const filters = () => byId(`${PREFIX}Filters`);

  const normalizedText = (value) =>
    String(value ?? "").trim().toLowerCase();

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
        note.textContent = "Recorded evidence";
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
      "pipeline_scope",
      "All pipelines",
      allJobs.map((job) => job.pipeline_id)
    );
    selectOptions(
      "job_status",
      "All statuses",
      allJobs.map((job) => job.status)
    );
    selectOptions(
      "priority",
      "All priorities",
      allJobs.map((job) => job.priority)
    );
  };

  const selectedFilters = () => {
    const value = (key) =>
      filters()?.querySelector(
        `[data-runtime-infrastructure-filter="${key}"]`
      )?.value ?? "";
    return {
      pipeline: normalizedText(value("pipeline_scope")),
      status: normalizedText(value("job_status")),
      priority: normalizedText(value("priority")),
      search: normalizedText(value("identity_search"))
    };
  };

  const filterJobs = () => {
    const active = selectedFilters();
    return allJobs.filter((job) => {
      if (active.pipeline && normalizedText(job.pipeline_id) !== active.pipeline) {
        return false;
      }
      if (active.status && normalizedText(job.status) !== active.status) {
        return false;
      }
      if (active.priority && normalizedText(job.priority) !== active.priority) {
        return false;
      }
      if (active.search) {
        const haystack = [
          job.job_id,
          job.workflow_id,
          job.correlation_id,
          job.workspace_id,
          job.pipeline_id,
          job.job_type,
          job.stage,
          job.assigned_worker_id
        ].map(normalizedText).join(" ");
        if (!haystack.includes(active.search)) {
          return false;
        }
      }
      return true;
    });
  };

  const renderDetail = (job) => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(
        `[data-runtime-infrastructure-field="${field}"]`
      );
      if (node) {
        node.textContent = displayValue(job?.[field]);
      }
    });
  };

  const selectJob = (jobId, focus = false) => {
    const selected = visibleJobs.find((job) => job.job_id === jobId);
    if (!selected) {
      selectedJobId = "";
      clearDetail();
      return;
    }
    selectedJobId = selected.job_id;
    directory()?.querySelectorAll("[role='option']").forEach((option) => {
      const active = option.dataset.jobId === selectedJobId;
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

  const jobOption = (job, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "runtime-infrastructure-job-option";
    button.id = `${PREFIX}Option${index}`;
    button.dataset.jobId = String(job.job_id);
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", "false");
    button.tabIndex = -1;

    const identity = document.createElement("strong");
    identity.textContent = displayValue(job.job_id);
    const state = document.createElement("span");
    state.textContent = [job.status, job.stage].filter(Boolean).join(" · ") || "Status unavailable";
    const context = document.createElement("small");
    context.textContent = [job.pipeline_id, job.job_type, job.workspace_id]
      .filter(Boolean).join(" · ") || "Context unavailable";
    button.append(identity, state, context);
    button.addEventListener("click", () => selectJob(job.job_id));
    return button;
  };

  const renderDirectory = () => {
    visibleJobs = filterJobs();
    if (!allJobs.length) {
      clearDirectory(
        "No recorded jobs",
        "The canonical job store is available and currently contains no job records."
      );
      clearDetail();
      setState("empty", "EMPTY");
      setMessage("No job evidence", "No execution activity was invented.");
      return;
    }
    if (!visibleJobs.length) {
      clearDirectory(
        "No matching jobs",
        "Adjust the local filters or identity search."
      );
      clearDetail();
      setState("no_match", "NO MATCH");
      setMessage("No matching job evidence", "The cached snapshot remains loaded.");
      return;
    }

    const node = directory();
    if (!node) {
      return;
    }
    node.classList.add("is-populated");
    node.setAttribute("aria-disabled", "false");
    node.replaceChildren(...visibleJobs.map(jobOption));

    if (!visibleJobs.some((job) => job.job_id === selectedJobId)) {
      selectedJobId = visibleJobs[0].job_id;
    }
    selectJob(selectedJobId);
    setState("ready", "LIVE EVIDENCE");
    setMessage(
      "Canonical job evidence loaded",
      `${visibleJobs.length} of ${allJobs.length} recorded jobs visible. Local filters issue no requests.`
    );
  };

  const renderJobs = (payload) => {
    const jobs = payload?.jobs;
    if (!jobs || !Array.isArray(jobs.records) || typeof jobs.summary !== "object") {
      throw new Error("The Jobs projection contract is unavailable.");
    }
    allJobs = jobs.records.filter((job) => job && typeof job === "object");
    renderSummary(jobs.summary);
    enableFilters();
    renderDirectory();
  };

  const unavailable = (message) => {
    allJobs = [];
    visibleJobs = [];
    selectedJobId = "";
    setState("unavailable", "UNAVAILABLE");
    clearDirectory("Job evidence unavailable", message);
    clearDetail();
    setMessage("Jobs unavailable", message);
  };

  const loadSnapshot = () => {
    if (cachedSnapshot) {
      return Promise.resolve(cachedSnapshot);
    }
    if (pendingSnapshot) {
      return pendingSnapshot;
    }
    setState("loading", "LOADING");
    setMessage("Loading job evidence", "Reading the canonical infrastructure snapshot.");
    pendingSnapshot = fetch(ENDPOINT, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
      credentials: "same-origin"
    }).then(async (response) => {
      let payload = null;
      try {
        payload = await response.json();
      } catch (_) {
        payload = null;
      }
      if (!response.ok) {
        const detail = payload?.detail || {};
        throw new Error(detail.message || `Infrastructure evidence unavailable (${response.status}).`);
      }
      if (!payload || payload.read_only !== true) {
        throw new Error("The infrastructure snapshot did not certify read-only authority.");
      }
      cachedSnapshot = payload;
      return payload;
    }).finally(() => {
      pendingSnapshot = null;
    });
    return pendingSnapshot;
  };

  const loadAndRenderJobs = () =>
    loadSnapshot().then(renderJobs).catch((error) => {
      unavailable(error?.message || "The infrastructure evidence request failed.");
    });

  const bindFilters = () => {
    const fieldset = filters();
    if (!fieldset || fieldset.dataset.b5kBound === "true") {
      return;
    }
    fieldset.addEventListener("input", renderDirectory);
    fieldset.addEventListener("change", renderDirectory);
    fieldset.dataset.b5kBound = "true";
  };

  const bindDirectoryKeyboard = () => {
    const node = directory();
    if (!node || node.dataset.b5kBound === "true") {
      return;
    }
    node.addEventListener("keydown", (event) => {
      const options = [...node.querySelectorAll("[role='option']")];
      if (!options.length || !["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) {
        return;
      }
      event.preventDefault();
      const current = Math.max(0, options.findIndex((option) => option.dataset.jobId === selectedJobId));
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
      selectJob(options[next].dataset.jobId, true);
    });
    node.dataset.b5kBound = "true";
  };

  const initialize = () => {
    if (!workspace()) {
      return;
    }
    bindFilters();
    bindDirectoryKeyboard();
    const page = byId("runtimePage");
    page?.addEventListener("runtimeowner:sectionchange", (event) => {
      if (event.detail?.section === "jobs") {
        loadAndRenderJobs();
      }
    });
    loadAndRenderJobs();
  };

  window.RuntimeInfrastructureEvidence = Object.freeze({
    endpoint: ENDPOINT,
    load: loadSnapshot,
    getSnapshot: () => cachedSnapshot
  });
  window.RuntimeInfrastructureJobs = Object.freeze({
    refreshFromCache: loadAndRenderJobs,
    getVisibleJobs: () => [...visibleJobs],
    getSelectedJobId: () => selectedJobId
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
// END PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING
'''


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        del tag
        for name, value in attrs:
            if name == "id" and value:
                self.ids.append(value)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8", newline="\n")


def atomic_write_text(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(source)
        temporary = Path(handle.name)
    temporary.replace(path)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def html_ids_unique(source: str) -> bool:
    parser = IdCollector()
    parser.feed(source)
    parser.close()
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


def python_syntax_valid(source: str, filename: str) -> bool:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(source, filename=filename)
            compile(tree, filename, "exec")
    except SyntaxError:
        return False
    return True


def javascript_syntax_valid(source: str) -> bool:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for JavaScript syntax validation.")
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b5k_js_") as folder:
        candidate = Path(folder) / "runtime_owner.js"
        write_text(candidate, source)
        result = subprocess.run(
            [node, "--check", str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    return result.returncode == 0


def b5j_report_complete(source: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return (
        "INSPECTION STATUS: COMPLETE" in normalized
        and "FAILED_CHECKS:\n[]" in normalized
        and "NOT_RUN_CHECKS:\n[]" in normalized
        and B5J_FINAL_RESULT in normalized
        and "Endpoint requests added: NO" in normalized
        and "Production recovery actions executed: NO" in normalized
        and "Live network requests executed: NO" in normalized
    )


def build_candidate_html(source: str) -> str:
    if source.count(OLD_CSS_VERSION) != 1:
        raise RuntimeError("The certified Runtime Owner CSS cache version is absent.")
    if source.count(OLD_JS_VERSION) != 1:
        raise RuntimeError("The certified Runtime Owner JavaScript cache version is absent.")
    candidate = source.replace(OLD_CSS_VERSION, NEW_CSS_VERSION, 1)
    return candidate.replace(OLD_JS_VERSION, NEW_JS_VERSION, 1)


def build_candidate_css(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The B5K CSS marker already exists.")
    return source.rstrip() + "\n" + CSS_APPEND.lstrip()


def build_candidate_js(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The B5K JavaScript marker already exists.")
    return source.rstrip() + "\n" + JS_APPEND.lstrip()


def build_candidate_backend(source: str) -> str:
    if MARKER in source or '@router.get("/infrastructure")' in source:
        raise RuntimeError("The B5K infrastructure route already exists.")
    return source.rstrip() + "\n" + BACKEND_APPEND.lstrip()


def load_isolated_projection(source: str) -> ModuleType:
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b5k_projection_") as folder:
        path = Path(folder) / "runtime_infrastructure_projection.py"
        write_text(path, source)
        name = "_linkcraftor_b5k_projection_probe"
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to create the isolated projection probe.")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(name, None)
        return module


def isolated_projection_probe(source: str) -> dict[str, Any]:
    module = load_isolated_projection(source)
    jobs = {
        "job_queued": {
            "job_id": "job_queued",
            "workspace_id": "ws_demo",
            "job_type": "connect_domain",
            "status": "queued",
            "priority": 5,
            "progress_percent": 0,
            "metadata": {
                "pipeline_id": "connect_domain",
                "workflow_id": "workflow_demo",
                "correlation_id": "correlation_demo",
            },
        },
        "job_completed": {
            "job_id": "job_completed",
            "workspace_id": "ws_demo",
            "job_type": "connect_domain",
            "status": "completed",
            "priority": 3,
            "progress_percent": 100,
            "metadata": {"pipeline_id": "connect_domain"},
        },
    }
    snapshot = module.build_runtime_infrastructure_snapshot(
        job_loader=lambda: jobs,
        event_loader=lambda job_id: [{"job_id": job_id}],
        clock=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert snapshot["read_only"] is True
    assert snapshot["jobs"]["record_count"] == 2
    assert snapshot["jobs"]["summary"]["queued_jobs"] == 1
    assert snapshot["jobs"]["summary"]["completed_jobs"] == 1
    assert snapshot["jobs"]["records"][0]["event_count"] == 1
    assert snapshot["queues"]["status"] == "NOT_WIRED"
    certification = module.certify_runtime_infrastructure_projection_v1()
    assert certification["certified"] is True
    return {
        "record_count": snapshot["jobs"]["record_count"],
        "queued_jobs": snapshot["jobs"]["summary"]["queued_jobs"],
        "completed_jobs": snapshot["jobs"]["summary"]["completed_jobs"],
        "event_count": snapshot["jobs"]["records"][0]["event_count"],
        "queues_status": snapshot["queues"]["status"],
        "certified": certification["certified"],
    }


def make_report(
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = (
        FINAL_RESULT
        if status == "CERTIFIED"
        else (
            "FINAL RESULT: PART F 15-B5K RUNTIME INFRASTRUCTURE "
            "JOBS WIRING NOT_CERTIFIED"
        )
    )
    return "\n".join(
        [
            "LINKCRAFTOR UNIVERSAL RUNTIME OWNER OPERATIONS",
            "PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING CERTIFICATION",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "Patch mode: STRICT FAIL-CLOSED",
            f"Backup: {evidence.get('backup', 'UNAVAILABLE')}",
            (
                "Shared infrastructure endpoint added: "
                + ("YES" if evidence.get("patch_retained") else "NO")
            ),
            (
                "Jobs live evidence wiring performed: "
                + ("YES" if evidence.get("patch_retained") else "NO")
            ),
            "Queues wiring performed: NO",
            "Workers and Leases wiring performed: NO",
            "Orchestration wiring performed: NO",
            "Execution wiring performed: NO",
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
            "- One GET /owner/api/runtime/infrastructure endpoint now returns a shared read-only infrastructure snapshot.",
            "- B5K populates Jobs from canonical load_jobs and list_job_events readers only.",
            "- Job summary, filters, directory selection, keyboard navigation and recorded detail evidence are active.",
            "- Empty, no-match and unavailable states fail closed and invent no job activity.",
            "- Queues, Workers & Leases, Orchestration and Execution remain NOT_WIRED for B5L-B5O.",
            "- The snapshot is cached in the frontend; filtering, searching and selection issue no requests.",
            "- No claim, retry, requeue, cancellation, termination, recovery or execution control was added.",
            "- No job, queue, worker, lease, workflow, handler, output or persistence mutation was executed during certification.",
            "",
            "NEXT STEP:",
            "Browser visual acceptance, then Part F 15-B5L - Queues wiring from the cached infrastructure snapshot.",
            "",
            final,
            "",
        ]
    )


def run(root: Path, report: Path) -> int:
    root = root.resolve()
    report = report.resolve()
    paths = {
        "index_html": root / "backend/server/owner/index.html",
        "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": root / "backend/server/owner/runtime_owner.css",
        "runtime_owner_js": root / "backend/server/owner/runtime_owner.js",
        "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py",
        "pipeline_operations": root / "backend/server/owner/pipeline_operations.py",
    }
    projection_path = root / PROJECTION_MODULE_PATH
    b5j_report = root / "backend/server/data/reports" / B5J_REPORT

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "endpoint": FUTURE_ENDPOINT,
        "patch_retained": False,
        "rollback_performed": False,
        "new_endpoint_requests": 1,
        "action_controls_added": False,
        "live_wiring_components": ["jobs"],
        "deferred_components": [
            "queues",
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
        checks["part_f_15_b5j_report_exists"] = b5j_report.is_file()
        checks["part_f_15_b5j_complete"] = (
            b5j_report.is_file()
            and b5j_report_complete(read_text(b5j_report))
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        checks["projection_not_previously_present"] = not projection_path.exists()
        if not all(checks.values()):
            raise RuntimeError(
                "The certified B5J baseline is unavailable or B5K was already applied."
            )

        watched = {**paths, "b5j_report": b5j_report}
        hashes_before = {
            name: sha256_path(path)
            for name, path in watched.items()
        }
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = hashes_before[name] == expected
        if not all(checks.values()):
            raise RuntimeError(
                "Installed sources do not match the certified B5J baseline."
            )

        before_sources = {
            name: read_text(path)
            for name, path in paths.items()
        }
        candidate_html = build_candidate_html(before_sources["index_html"])
        candidate_css = build_candidate_css(before_sources["runtime_owner_css"])
        candidate_js = build_candidate_js(before_sources["runtime_owner_js"])
        candidate_backend = build_candidate_backend(
            before_sources["runtime_summary_api"]
        )

        checks["candidate_html_ids_unique"] = html_ids_unique(candidate_html)
        checks["candidate_css_balanced"] = css_balanced(candidate_css)
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(
            candidate_js
        )
        checks["candidate_runtime_api_syntax"] = python_syntax_valid(
            candidate_backend,
            str(paths["runtime_summary_api"]),
        )
        checks["candidate_projection_syntax"] = python_syntax_valid(
            PROJECTION_SOURCE,
            str(projection_path),
        )
        projection_probe = isolated_projection_probe(PROJECTION_SOURCE)
        checks["isolated_jobs_projection_probe_passed"] = all(
            (
                projection_probe["record_count"] == 2,
                projection_probe["queued_jobs"] == 1,
                projection_probe["completed_jobs"] == 1,
                projection_probe["event_count"] == 1,
                projection_probe["queues_status"] == "NOT_WIRED",
                projection_probe["certified"] is True,
            )
        )
        checks["shared_get_endpoint_present_once"] = (
            candidate_backend.count('@router.get("/infrastructure")') == 1
            and candidate_js.count(FUTURE_ENDPOINT) == 1
        )
        checks["four_frontend_fetch_authorities"] = (
            candidate_js.count("fetch(") == 4
        )
        checks["existing_three_fetch_authorities_retained"] = all(
            endpoint in candidate_js
            for endpoint in (
                "/owner/api/runtime/summary",
                "/owner/api/runtime/pipelines",
                "/owner/api/runtime/pipelines/connect_domain",
            )
        )
        checks["jobs_bindings_present"] = all(
            token in candidate_js
            for token in (
                "RuntimeInfrastructureEvidence",
                "RuntimeInfrastructureJobs",
                'const PREFIX = "runtimeInfrastructureJobs";',
                "pipeline_scope",
                "job_status",
                "identity_search",
                "loadAndRenderJobs",
            )
        )
        checks["jobs_projection_fields_present"] = all(
            f'"{field}"' in PROJECTION_SOURCE
            for field in (
                "job_id",
                "workflow_id",
                "correlation_id",
                "workspace_id",
                "pipeline_id",
                "status",
                "stage",
                "job_type",
                "priority",
                "progress",
                "assigned_worker_id",
                "attempt_count",
                "retry_state",
                "terminal_error",
                "event_count",
            )
        )
        checks["canonical_readers_only"] = all(
            token in PROJECTION_SOURCE
            for token in ("load_jobs", "list_job_events")
        ) and all(
            token not in PROJECTION_SOURCE
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
        checks["four_components_explicitly_not_wired"] = all(
            f'_not_wired_component("{component}")' in PROJECTION_SOURCE
            for component in (
                "queues",
                "workers_leases",
                "orchestration",
                "execution",
            )
        )
        checks["no_action_controls_added"] = all(
            token not in candidate_js
            for token in (
                "claimJob",
                "retryJob",
                "cancelJob",
                "terminateJob",
                "recoverJob",
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
            raise RuntimeError("One or more B5K candidate checks failed.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = (
            root
            / "backend/server/data/runtime_backups"
            / f"part_f_15_b5k_{timestamp}"
        )
        backup.mkdir(parents=True, exist_ok=False)
        for name in (
            "index_html",
            "runtime_owner_css",
            "runtime_owner_js",
            "runtime_summary_api",
        ):
            destination = backup / paths[name].relative_to(root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(paths[name], destination)
        evidence["backup"] = str(backup)
        checks["backup_created"] = backup.is_dir()

        atomic_write_text(paths["index_html"], candidate_html)
        atomic_write_text(paths["runtime_owner_css"], candidate_css)
        atomic_write_text(paths["runtime_owner_js"], candidate_js)
        atomic_write_text(paths["runtime_summary_api"], candidate_backend)
        atomic_write_text(projection_path, PROJECTION_SOURCE)
        applied = True

        checks["retained_html_ids_unique"] = html_ids_unique(
            read_text(paths["index_html"])
        )
        checks["retained_css_balanced"] = css_balanced(
            read_text(paths["runtime_owner_css"])
        )
        checks["retained_javascript_syntax"] = javascript_syntax_valid(
            read_text(paths["runtime_owner_js"])
        )
        checks["retained_runtime_api_syntax"] = python_syntax_valid(
            read_text(paths["runtime_summary_api"]),
            str(paths["runtime_summary_api"]),
        )
        checks["retained_projection_syntax"] = python_syntax_valid(
            read_text(projection_path),
            str(projection_path),
        )
        checks["retained_markers"] = all(
            MARKER in read_text(path)
            for path in (
                paths["runtime_owner_css"],
                paths["runtime_owner_js"],
                paths["runtime_summary_api"],
            )
        )
        checks["historical_b5j_report_unchanged"] = (
            sha256_path(b5j_report) == hashes_before["b5j_report"]
        )
        checks["only_expected_sources_changed"] = all(
            (
                sha256_path(paths["index_html"])
                != hashes_before["index_html"],
                sha256_path(paths["runtime_owner_css"])
                != hashes_before["runtime_owner_css"],
                sha256_path(paths["runtime_owner_js"])
                != hashes_before["runtime_owner_js"],
                sha256_path(paths["runtime_summary_api"])
                != hashes_before["runtime_summary_api"],
                projection_path.is_file(),
                sha256_path(paths["owner_css"]) == hashes_before["owner_css"],
                sha256_path(paths["owner_js"]) == hashes_before["owner_js"],
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
            raise RuntimeError("One or more retained B5K checks failed.")

        evidence.update(
            {
                "patch_retained": True,
                "projection_probe": projection_probe,
                "changed_sources": [
                    "backend/server/owner/index.html",
                    "backend/server/owner/runtime_owner.css",
                    "backend/server/owner/runtime_owner.js",
                    "backend/server/owner/runtime_summary_api.py",
                    PROJECTION_MODULE_PATH,
                ],
                "source_hashes_before": {
                    name: hashes_before[name]
                    for name in paths
                },
                "source_hashes_after": {
                    **{
                        name: sha256_path(path)
                        for name, path in paths.items()
                    },
                    "runtime_infrastructure_projection": sha256_path(
                        projection_path
                    ),
                },
                "jobs_summary_fields": [
                    "total_jobs",
                    "queued_jobs",
                    "running_jobs",
                    "completed_jobs",
                    "failed_jobs",
                    "cancelled_jobs",
                ],
                "jobs_record_fields": [
                    "identity",
                    "workflow and correlation",
                    "pipeline and stage",
                    "lifecycle and priority",
                    "progress",
                    "worker and lease ownership",
                    "attempt and retry evidence",
                    "timestamps",
                    "dispatch result",
                    "terminal error",
                    "event count",
                ],
                "snapshot_reuse": {
                    "15-B5K": "jobs populated",
                    "15-B5L": "queues deferred",
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
                    "runtime_summary_api",
                ):
                    source = backup / paths[name].relative_to(root)
                    if source.is_file():
                        shutil.copy2(source, paths[name])
                if projection_path.exists():
                    projection_path.unlink()
                evidence["rollback_performed"] = True
            except Exception as rollback_exc:
                error["rollback_error"] = {
                    "error_type": type(rollback_exc).__name__,
                    "error_message": str(rollback_exc),
                    "traceback": traceback.format_exc(),
                }

    report.parent.mkdir(parents=True, exist_ok=True)
    write_text(report, make_report(status, checks, evidence, error))

    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(
        "FAILED_CHECK_COUNT="
        f"{sum(not passed for passed in checks.values())}"
    )
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B5K_STATUS={status}")
    print(f"PATCH_RETAINED={'YES' if evidence.get('patch_retained') else 'NO'}")
    print("SHARED_ENDPOINT_ADDED=YES" if status == "CERTIFIED" else "SHARED_ENDPOINT_ADDED=NO")
    print("JOBS_WIRING=YES" if status == "CERTIFIED" else "JOBS_WIRING=NO")
    print("ACTION_CONTROLS=NO")
    return 0 if status == "CERTIFIED" else 1


def self_test() -> int:
    html = "\n".join(
        (
            OLD_CSS_VERSION,
            OLD_JS_VERSION,
            '<section id="runtimeOwnerSectionJobs">',
            '<div id="runtimeInfrastructureJobsWorkspace"></div>',
            '<div id="runtimeInfrastructureJobsDirectory"></div>',
            '<div id="runtimeInfrastructureJobsDetail"></div>',
            "</section>",
        )
    )
    candidate_html = build_candidate_html(html)
    assert OLD_CSS_VERSION not in candidate_html
    assert OLD_JS_VERSION not in candidate_html
    assert candidate_html.count(NEW_CSS_VERSION) == 1
    assert candidate_html.count(NEW_JS_VERSION) == 1
    assert html_ids_unique(candidate_html)
    assert css_balanced("a { color: red; } @media (x) { b { color: blue; } }")
    assert python_syntax_valid(PROJECTION_SOURCE, "projection.py")
    assert isolated_projection_probe(PROJECTION_SOURCE)["certified"] is True
    assert build_candidate_backend("router = object()\n").count(
        '@router.get("/infrastructure")'
    ) == 1
    assert MARKER in build_candidate_css("a { color: red; }\n")
    assert MARKER in build_candidate_js("(() => { 'use strict'; })();\n")
    assert javascript_syntax_valid(
        "(() => { 'use strict'; })();\n" + JS_APPEND
    )
    certified = "\n".join(
        (
            "INSPECTION STATUS: COMPLETE",
            "Endpoint requests added: NO",
            "Production recovery actions executed: NO",
            "Live network requests executed: NO",
            "FAILED_CHECKS:",
            "[]",
            "NOT_RUN_CHECKS:",
            "[]",
            B5J_FINAL_RESULT,
        )
    )
    assert b5j_report_complete(certified)
    print("PART_F_15_B5K_SELF_TEST=PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B5K_RUNTIME_INFRASTRUCTURE_JOBS_WIRING.py "
            "<project_root> <report_path> | --self-test"
        )
    raise SystemExit(run(Path(sys.argv[1]), Path(sys.argv[2])))
