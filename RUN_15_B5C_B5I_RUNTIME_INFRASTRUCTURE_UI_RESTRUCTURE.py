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


STEP = "PART F 15-B5C THROUGH 15-B5I"
TITLE = "RUNTIME INFRASTRUCTURE UI RESTRUCTURING"
MARKER = "PART F 15-B5C-B5I RUNTIME INFRASTRUCTURE UI RESTRUCTURING"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5C THROUGH 15-B5I RUNTIME "
    "INFRASTRUCTURE UI RESTRUCTURING CERTIFIED"
)

EXPECTED_HASHES = {
    "index_html": "6d252cf36d56b9de643efc87d09c92f6e0c49d49098c6924d1457f6afc331de9",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "b87a76c5ddc17446c573ddbc2dea09f32600321738aeb15a74a269933a1145e4",
    "runtime_owner_js": "b73f61e6569e5dc0d97a213c8f8c030556c4877597c7c0274fa63861de5b05ba",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

B5B_REPORT = "PART_F_15_B5B_RUNTIME_INFRASTRUCTURE_UI_BLUEPRINT.txt"
B5B_FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5B RUNTIME INFRASTRUCTURE "
    "MISSING-COMPONENT SCAN AND UI BLUEPRINT COMPLETE"
)

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=15" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=16" />'

PRESENTATION_STATES = (
    "loading",
    "ready",
    "empty",
    "no_match",
    "unavailable",
)


def contract(
    *,
    label: str,
    singular: str,
    panel_id: str,
    prefix: str,
    description: str,
    wiring_phase: str,
    summaries: list[str],
    filters: list[tuple[str, str, str]],
    directory_fields: list[str],
    detail_groups: dict[str, list[str]],
) -> dict[str, Any]:
    return {
        "label": label,
        "singular": singular,
        "panel_id": panel_id,
        "prefix": prefix,
        "description": description,
        "wiring_phase": wiring_phase,
        "summaries": summaries,
        "filters": filters,
        "directory_fields": directory_fields,
        "detail_groups": detail_groups,
    }


COMPONENTS: dict[str, dict[str, Any]] = {
    "jobs": contract(
        label="Jobs",
        singular="job",
        panel_id="runtimeOwnerSectionJobs",
        prefix="runtimeInfrastructureJobs",
        description=(
            "Inspect canonical Universal Job identity, lifecycle, ownership, "
            "progress, attempts, retry evidence and terminal outcome."
        ),
        wiring_phase="15-B5K",
        summaries=[
            "total_jobs",
            "queued_jobs",
            "running_jobs",
            "completed_jobs",
            "failed_jobs",
            "cancelled_jobs",
        ],
        filters=[
            ("pipeline_scope", "Pipeline", "All pipelines"),
            ("job_status", "Status", "All statuses"),
            ("priority", "Priority", "All priorities"),
            ("identity_search", "Find job", "Job, workflow, correlation, or workspace"),
        ],
        directory_fields=[
            "job_identity",
            "pipeline",
            "job_type",
            "stage",
            "status",
            "priority",
            "progress",
        ],
        detail_groups={
            "Identity": [
                "job_id",
                "workflow_id",
                "correlation_id",
                "workspace_id",
                "pipeline_id",
            ],
            "Lifecycle": [
                "status",
                "stage",
                "job_type",
                "priority",
                "progress",
            ],
            "Ownership": [
                "assigned_worker_id",
                "lease_identity",
                "lease_expiry",
            ],
            "Attempts & Retry": [
                "attempt_count",
                "attempt_limit",
                "retry_state",
                "next_retry_at",
            ],
            "Timing & Result": [
                "created_at",
                "updated_at",
                "started_at",
                "completed_at",
                "dispatch_result",
                "terminal_error",
                "event_count",
            ],
        },
    ),
    "queues": contract(
        label="Queues",
        singular="queue",
        panel_id="runtimeOwnerSectionQueues",
        prefix="runtimeInfrastructureQueues",
        description=(
            "Inspect canonical queue backlog, priority distribution, claimable "
            "work, reservations, delay and pressure evidence."
        ),
        wiring_phase="15-B5L",
        summaries=[
            "queued_items",
            "claimable_items",
            "reserved_items",
            "delayed_items",
            "blocked_items",
            "queue_pressure",
        ],
        filters=[
            ("queue_scope", "Queue", "All queues"),
            ("item_status", "Status", "All statuses"),
            ("priority", "Priority", "All priorities"),
            ("identity_search", "Find evidence", "Queue, job, workflow, or workspace"),
        ],
        directory_fields=[
            "queue_identity",
            "queued_count",
            "claimable_count",
            "reserved_count",
            "oldest_item_age",
            "pressure_state",
        ],
        detail_groups={
            "Identity": ["queue_id", "queue_name", "pipeline_scope"],
            "Backlog": [
                "queued_count",
                "claimable_count",
                "delayed_count",
                "blocked_count",
                "oldest_item_at",
            ],
            "Priority Distribution": [
                "critical_count",
                "high_count",
                "normal_count",
                "low_count",
            ],
            "Reservation Evidence": [
                "reserved_count",
                "active_claim_count",
                "reservation_expiry_evidence",
            ],
            "Pressure": [
                "pressure_state",
                "capacity_evidence",
                "throughput_evidence",
                "last_updated_at",
            ],
        },
    ),
    "workers_leases": contract(
        label="Workers & Leases",
        singular="worker",
        panel_id="runtimeOwnerSectionWorkersLeases",
        prefix="runtimeInfrastructureWorkersLeases",
        description=(
            "Inspect worker identity, lifecycle, health, heartbeat and the "
            "authoritative leases currently associated with runtime work."
        ),
        wiring_phase="15-B5M",
        summaries=[
            "total_workers",
            "active_workers",
            "idle_workers",
            "busy_workers",
            "stale_workers",
            "active_leases",
        ],
        filters=[
            ("worker_lifecycle", "Lifecycle", "All lifecycle states"),
            ("worker_health", "Health", "All health states"),
            ("lease_state", "Lease", "All lease states"),
            ("identity_search", "Find worker", "Worker, lease, job, or workflow"),
        ],
        directory_fields=[
            "worker_identity",
            "lifecycle",
            "health",
            "current_work",
            "active_lease_count",
            "last_heartbeat_at",
        ],
        detail_groups={
            "Identity": [
                "worker_id",
                "worker_kind",
                "runtime_identity",
                "environment",
            ],
            "Lifecycle & Health": [
                "lifecycle",
                "health",
                "availability",
                "last_heartbeat_at",
                "staleness_reason",
            ],
            "Work Ownership": [
                "current_job_id",
                "current_workflow_id",
                "current_stage",
            ],
            "Lease Evidence": [
                "lease_id",
                "lease_owner",
                "lease_status",
                "acquired_at",
                "expires_at",
                "renewed_at",
            ],
            "Capacity": [
                "concurrency_limit",
                "active_execution_count",
                "available_capacity",
            ],
        },
    ),
    "orchestration": contract(
        label="Orchestration",
        singular="workflow",
        panel_id="runtimeOwnerSectionOrchestration",
        prefix="runtimeInfrastructureOrchestration",
        description=(
            "Inspect workflow identity, correlation, lifecycle, current stage, "
            "dependencies, handoffs, completion and failure evidence."
        ),
        wiring_phase="15-B5N",
        summaries=[
            "total_workflows",
            "active_workflows",
            "completed_workflows",
            "failed_workflows",
            "blocked_workflows",
            "pending_handoffs",
        ],
        filters=[
            ("pipeline_scope", "Pipeline", "All pipelines"),
            ("workflow_lifecycle", "Lifecycle", "All lifecycle states"),
            ("current_stage", "Stage", "All stages"),
            ("identity_search", "Find workflow", "Workflow, correlation, or workspace"),
        ],
        directory_fields=[
            "workflow_identity",
            "pipeline",
            "lifecycle",
            "current_stage",
            "completion",
            "failure_state",
        ],
        detail_groups={
            "Identity": [
                "workflow_id",
                "correlation_id",
                "workspace_id",
                "pipeline_id",
            ],
            "Lifecycle": [
                "status",
                "current_stage",
                "created_at",
                "updated_at",
                "completed_at",
            ],
            "Stage Progress": [
                "stage_count",
                "completed_stage_count",
                "pending_stage_count",
                "failed_stage_count",
            ],
            "Dependencies & Handoffs": [
                "predecessor_evidence",
                "successor_evidence",
                "handoff_state",
                "blocked_reason",
            ],
            "Work Evidence": [
                "job_count",
                "active_job_count",
                "failed_job_count",
                "final_output_state",
            ],
        },
    ),
    "execution": contract(
        label="Execution",
        singular="execution",
        panel_id="runtimeOwnerSectionExecution",
        prefix="runtimeInfrastructureExecution",
        description=(
            "Inspect canonical handler execution identity, job binding, worker "
            "and lease ownership, timing, outcome and terminal evidence."
        ),
        wiring_phase="15-B5O",
        summaries=[
            "total_executions",
            "running_executions",
            "succeeded_executions",
            "failed_executions",
            "cancelled_executions",
            "terminal_executions",
        ],
        filters=[
            ("pipeline_scope", "Pipeline", "All pipelines"),
            ("execution_status", "Status", "All statuses"),
            ("handler_identity", "Handler", "All handlers"),
            ("evidence_search", "Find execution", "Execution, job, handler, or worker"),
        ],
        directory_fields=[
            "execution_identity",
            "job_identity",
            "handler_identity",
            "status",
            "worker_identity",
            "duration",
        ],
        detail_groups={
            "Identity": [
                "execution_id",
                "job_id",
                "workflow_id",
                "correlation_id",
                "pipeline_id",
            ],
            "Handler Binding": [
                "handler_id",
                "handler_version",
                "stage",
                "execution_action",
            ],
            "Ownership": [
                "worker_id",
                "lease_id",
                "dispatch_identity",
            ],
            "Timing": [
                "dispatched_at",
                "started_at",
                "finished_at",
                "duration",
            ],
            "Outcome": [
                "status",
                "result_summary",
                "terminal_error",
                "failure_kind",
                "event_count",
            ],
        },
    ),
}


CSS_APPEND = r'''

/* BEGIN PART F 15-B5C-B5I RUNTIME INFRASTRUCTURE UI RESTRUCTURING */
#runtimePage .runtime-infrastructure-workspace,
#runtimePage .runtime-infrastructure-workspace * {
  box-sizing: border-box;
}

#runtimePage .runtime-infrastructure-workspace {
  display: grid;
  gap: 14px;
  min-width: 0;
  width: 100%;
  padding: 14px;
  border: 1px solid rgba(103, 232, 249, .18);
  border-radius: 14px;
  background:
    linear-gradient(145deg, rgba(8, 47, 73, .34), rgba(8, 32, 55, .18)),
    rgba(5, 25, 45, .24);
  overflow-x: hidden;
  overflow-x: clip;
}

#runtimePage .runtime-infrastructure-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  min-width: 0;
}

#runtimePage .runtime-infrastructure-head > div {
  min-width: 0;
}

#runtimePage .runtime-infrastructure-eyebrow {
  display: block;
  margin-bottom: 3px;
  color: #2dd4bf;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
}

#runtimePage .runtime-infrastructure-head h3 {
  margin: 0;
  color: #f8fafc;
  font-size: 20px;
  line-height: 1.2;
}

#runtimePage .runtime-infrastructure-head p {
  max-width: 820px;
  margin: 5px 0 0;
  color: #a9bed0;
  font-size: 12px;
  line-height: 1.5;
}

#runtimePage .runtime-infrastructure-state-badge {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 5px 10px;
  border: 1px solid rgba(45, 212, 191, .5);
  border-radius: 999px;
  color: #99f6e4;
  background: rgba(13, 148, 136, .14);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .04em;
  white-space: nowrap;
}

#runtimePage .runtime-infrastructure-summary {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 9px;
  min-width: 0;
}

#runtimePage .runtime-infrastructure-summary-card {
  min-width: 0;
  padding: 11px;
  border: 1px solid rgba(148, 163, 184, .14);
  border-radius: 10px;
  background: rgba(15, 42, 64, .54);
}

#runtimePage .runtime-infrastructure-summary-card span,
#runtimePage .runtime-infrastructure-summary-card small {
  display: block;
  color: #8fa9bc;
  font-size: 9px;
  line-height: 1.35;
}

#runtimePage .runtime-infrastructure-summary-card span {
  font-weight: 750;
  letter-spacing: .04em;
  text-transform: uppercase;
}

#runtimePage .runtime-infrastructure-summary-card strong {
  display: block;
  margin: 5px 0 2px;
  color: #f8fafc;
  font-size: 18px;
  line-height: 1;
}

#runtimePage .runtime-infrastructure-toolbar {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 9px;
  min-width: 0;
  margin: 0;
  padding: 0;
  border: 0;
}

#runtimePage .runtime-infrastructure-toolbar label {
  display: grid;
  gap: 5px;
  min-width: 0;
  color: #8fa9bc;
  font-size: 9px;
  font-weight: 750;
  letter-spacing: .04em;
  text-transform: uppercase;
}

#runtimePage .runtime-infrastructure-toolbar :is(input, select) {
  width: 100%;
  min-width: 0;
  min-height: 38px;
  padding: 7px 10px;
  border: 1px solid rgba(103, 232, 249, .2);
  border-radius: 8px;
  color: #cbd5e1;
  background: rgba(7, 30, 50, .72);
  font: inherit;
  font-size: 11px;
  text-transform: none;
}

#runtimePage .runtime-infrastructure-toolbar[disabled] :is(input, select) {
  cursor: not-allowed;
  opacity: .68;
}

#runtimePage .runtime-infrastructure-split {
  display: grid;
  grid-template-columns: minmax(240px, .82fr) minmax(0, 1.55fr);
  min-width: 0;
  min-height: 360px;
  border: 1px solid rgba(148, 163, 184, .14);
  border-radius: 12px;
  background: rgba(6, 29, 49, .36);
  overflow: hidden;
}

#runtimePage .runtime-infrastructure-pane {
  min-width: 0;
  padding: 12px;
}

#runtimePage .runtime-infrastructure-pane + .runtime-infrastructure-pane {
  border-left: 1px solid rgba(148, 163, 184, .14);
}

#runtimePage .runtime-infrastructure-pane-head {
  margin-bottom: 10px;
}

#runtimePage .runtime-infrastructure-pane-head strong {
  display: block;
  color: #e2e8f0;
  font-size: 12px;
}

#runtimePage .runtime-infrastructure-pane-head small {
  display: block;
  margin-top: 3px;
  color: #7f9aaf;
  font-size: 10px;
}

#runtimePage .runtime-infrastructure-directory {
  display: grid;
  align-content: center;
  min-height: 278px;
  padding: 14px;
  border: 1px dashed rgba(103, 232, 249, .17);
  border-radius: 9px;
  color: #8fa9bc;
  background: rgba(7, 35, 57, .34);
  text-align: center;
}

#runtimePage .runtime-infrastructure-directory:focus-visible,
#runtimePage .runtime-infrastructure-workspace :is(input, select):focus-visible {
  outline: 2px solid #22d3ee;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(34, 211, 238, .13);
}

#runtimePage .runtime-infrastructure-directory strong {
  color: #dbeafe;
  font-size: 12px;
}

#runtimePage .runtime-infrastructure-directory span {
  display: block;
  margin-top: 4px;
  font-size: 10px;
  line-height: 1.45;
}

#runtimePage .runtime-infrastructure-detail {
  min-width: 0;
}

#runtimePage .runtime-infrastructure-detail-groups {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
  min-width: 0;
}

#runtimePage .runtime-infrastructure-detail-group {
  min-width: 0;
  padding: 11px;
  border: 1px solid rgba(148, 163, 184, .13);
  border-radius: 9px;
  background: rgba(15, 42, 64, .42);
}

#runtimePage .runtime-infrastructure-detail-group h4 {
  margin: 0 0 9px;
  color: #dbeafe;
  font-size: 11px;
}

#runtimePage .runtime-infrastructure-facts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
  margin: 0;
}

#runtimePage .runtime-infrastructure-facts > div {
  min-width: 0;
  padding: 7px;
  border-radius: 7px;
  background: rgba(8, 37, 59, .55);
}

#runtimePage .runtime-infrastructure-facts dt,
#runtimePage .runtime-infrastructure-facts dd {
  margin: 0;
  overflow-wrap: anywhere;
}

#runtimePage .runtime-infrastructure-facts dt {
  color: #7f9aaf;
  font-size: 8px;
  font-weight: 750;
  letter-spacing: .035em;
  text-transform: uppercase;
}

#runtimePage .runtime-infrastructure-facts dd {
  margin-top: 3px;
  color: #dbeafe;
  font-size: 10px;
}

#runtimePage .runtime-infrastructure-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-width: 0;
  padding: 10px 12px;
  border: 1px dashed rgba(45, 212, 191, .25);
  border-radius: 10px;
  color: #99f6e4;
  background: rgba(13, 148, 136, .08);
  text-align: center;
}

#runtimePage .runtime-infrastructure-message strong,
#runtimePage .runtime-infrastructure-message span {
  overflow-wrap: anywhere;
}

#runtimePage .runtime-infrastructure-message strong {
  font-size: 11px;
}

#runtimePage .runtime-infrastructure-message span {
  color: #8fa9bc;
  font-size: 10px;
}

@media (max-width: 1180px) {
  #runtimePage .runtime-infrastructure-summary {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  #runtimePage .runtime-infrastructure-toolbar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 940px) {
  #runtimePage .runtime-infrastructure-split {
    grid-template-columns: 1fr;
  }

  #runtimePage .runtime-infrastructure-pane + .runtime-infrastructure-pane {
    border-top: 1px solid rgba(148, 163, 184, .14);
    border-left: 0;
  }

  #runtimePage .runtime-infrastructure-directory {
    min-height: 180px;
  }
}

@media (max-width: 700px) {
  #runtimePage .runtime-infrastructure-head {
    display: grid;
    grid-template-columns: 1fr;
  }

  #runtimePage .runtime-infrastructure-state-badge {
    justify-self: start;
  }

  #runtimePage .runtime-infrastructure-toolbar,
  #runtimePage .runtime-infrastructure-detail-groups {
    grid-template-columns: 1fr;
  }

  #runtimePage .runtime-infrastructure-toolbar :is(input, select),
  #runtimePage .runtime-infrastructure-directory {
    min-height: 44px;
  }
}

@media (max-width: 480px) {
  #runtimePage .runtime-infrastructure-workspace {
    gap: 10px;
    padding: 9px;
  }

  #runtimePage .runtime-infrastructure-summary,
  #runtimePage .runtime-infrastructure-facts {
    grid-template-columns: 1fr;
  }

  #runtimePage .runtime-infrastructure-pane {
    padding: 9px;
  }

  #runtimePage .runtime-infrastructure-message {
    align-items: flex-start;
    flex-direction: column;
    gap: 3px;
    text-align: left;
  }
}

@media (prefers-reduced-motion: reduce) {
  #runtimePage .runtime-infrastructure-workspace,
  #runtimePage .runtime-infrastructure-workspace * {
    scroll-behavior: auto !important;
    animation: none !important;
    transition-duration: .01ms !important;
  }
}
/* END PART F 15-B5C-B5I RUNTIME INFRASTRUCTURE UI RESTRUCTURING */
'''


class ElementCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str]]] = []
        self.ids: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        normalized = {
            str(name): "" if value is None else str(value)
            for name, value in attrs
        }
        self.elements.append((tag, normalized))
        identifier = normalized.get("id")
        if identifier:
            self.ids.append(identifier)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8", newline="\n")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def html_ids_unique(source: str) -> bool:
    parser = ElementCollector()
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


def javascript_syntax_valid(source: str) -> bool:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for JavaScript syntax validation.")
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b5ci_js_") as folder:
        candidate = Path(folder) / "runtime_owner.js"
        write_text(candidate, source)
        result = subprocess.run(
            [node, "--check", str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    return result.returncode == 0


def b5b_report_complete(source: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return (
        "BLUEPRINT STATUS: COMPLETE" in normalized
        and "FAILED_CHECKS:\n[]" in normalized
        and "NOT_RUN_CHECKS:\n[]" in normalized
        and B5B_FINAL_RESULT in normalized
        and "Production recovery actions executed: NO" in normalized
        and "Live network requests executed: NO" in normalized
    )


def humanize(value: str) -> str:
    return " ".join(word.capitalize() for word in value.split("_"))


def panel_span(source: str, panel_id: str) -> tuple[int, int]:
    start_pattern = re.compile(
        rf"<section\b[^>]*\bid=[\"']{re.escape(panel_id)}[\"'][^>]*>",
        flags=re.I,
    )
    start_match = start_pattern.search(source)
    if start_match is None:
        raise RuntimeError(f"Panel unavailable: {panel_id}")
    token_pattern = re.compile(r"</?section\b[^>]*>", flags=re.I)
    depth = 0
    for token in token_pattern.finditer(source, start_match.start()):
        closing = token.group(0).lstrip().startswith("</")
        depth += -1 if closing else 1
        if depth == 0:
            return start_match.start(), token.end()
    raise RuntimeError(f"Panel is not balanced: {panel_id}")


def summary_html(contract_data: dict[str, Any]) -> str:
    cards = []
    for metric in contract_data["summaries"]:
        cards.append(
            "\n".join(
                [
                    (
                        "        <article class=\"runtime-infrastructure-"
                        "summary-card\" "
                        f"data-runtime-infrastructure-metric=\"{metric}\">"
                    ),
                    f"          <span>{humanize(metric)}</span>",
                    "          <strong>—</strong>",
                    "          <small>Awaiting evidence</small>",
                    "        </article>",
                ]
            )
        )
    return "\n".join(cards)


def filters_html(contract_data: dict[str, Any]) -> str:
    fields = []
    for key, label, placeholder in contract_data["filters"]:
        if "search" in key:
            control = (
                f'<input type="search" data-runtime-infrastructure-filter="{key}" '
                f'placeholder="{placeholder}" disabled />'
            )
        else:
            control = "\n".join(
                [
                    (
                        f'<select data-runtime-infrastructure-filter="{key}" '
                        "disabled>"
                    ),
                    f"              <option>{placeholder}</option>",
                    "            </select>",
                ]
            )
        fields.append(
            "\n".join(
                [
                    "        <label>",
                    f"          <span>{label}</span>",
                    f"          {control}",
                    "        </label>",
                ]
            )
        )
    return "\n".join(fields)


def details_html(contract_data: dict[str, Any]) -> str:
    groups = []
    for group_label, fields in contract_data["detail_groups"].items():
        facts = []
        for field in fields:
            facts.extend(
                [
                    "              <div>",
                    f"                <dt>{humanize(field)}</dt>",
                    (
                        "                <dd "
                        f"data-runtime-infrastructure-field=\"{field}\">—</dd>"
                    ),
                    "              </div>",
                ]
            )
        groups.append(
            "\n".join(
                [
                    '          <article class="runtime-infrastructure-detail-group">',
                    f"            <h4>{group_label}</h4>",
                    '            <dl class="runtime-infrastructure-facts">',
                    *facts,
                    "            </dl>",
                    "          </article>",
                ]
            )
        )
    return "\n".join(groups)


def workspace_html(component: str, contract_data: dict[str, Any]) -> str:
    label = str(contract_data["label"])
    singular = str(contract_data["singular"])
    prefix = str(contract_data["prefix"])
    states = " ".join(PRESENTATION_STATES)
    return "\n".join(
        [
            "<section",
            '    class="runtime-owner-section"',
            f'    id="{contract_data["panel_id"]}"',
            f'    data-runtime-owner-section-panel="{component}"',
            "    hidden",
            "  >",
            "    <!-- BEGIN PART F 15-B5C-B5I RUNTIME INFRASTRUCTURE UI RESTRUCTURING -->",
            "    <div",
            '      class="runtime-infrastructure-workspace"',
            f'      id="{prefix}Workspace"',
            f'      data-runtime-infrastructure-component="{component}"',
            '      data-runtime-infrastructure-state="unavailable"',
            f'      data-runtime-infrastructure-states="{states}"',
            "    >",
            '      <header class="runtime-infrastructure-head">',
            "        <div>",
            '          <span class="runtime-infrastructure-eyebrow">Runtime Infrastructure</span>',
            f"          <h3>{label}</h3>",
            f"          <p>{contract_data['description']}</p>",
            "        </div>",
            "        <strong",
            '          class="runtime-infrastructure-state-badge"',
            f'          id="{prefix}StateBadge"',
            "        >STRUCTURE READY</strong>",
            "      </header>",
            "",
            "      <div",
            '        class="runtime-infrastructure-summary"',
            f'        id="{prefix}Summary"',
            f'        aria-label="{label} summary"',
            "      >",
            summary_html(contract_data),
            "      </div>",
            "",
            "      <fieldset",
            '        class="runtime-infrastructure-toolbar"',
            f'        id="{prefix}Filters"',
            f'        aria-label="{label} filters"',
            "        disabled",
            "      >",
            filters_html(contract_data),
            "      </fieldset>",
            "",
            '      <div class="runtime-infrastructure-split">',
            "        <section",
            '          class="runtime-infrastructure-pane"',
            f'          aria-label="{label} directory"',
            "        >",
            '          <header class="runtime-infrastructure-pane-head">',
            f"            <strong>{label} Directory</strong>",
            (
                "            <small>Canonical recorded entries will appear "
                f"after {contract_data['wiring_phase']} wiring.</small>"
            ),
            "          </header>",
            "          <div",
            '            class="runtime-infrastructure-directory"',
            f'            id="{prefix}Directory"',
            '            role="listbox"',
            f'            aria-label="{label} directory"',
            '            aria-disabled="true"',
            '            tabindex="0"',
            "          >",
            f"            <strong>No {singular} evidence loaded</strong>",
            (
                "            <span>The directory is intentionally empty until "
                "the approved live-evidence wiring phase.</span>"
            ),
            "          </div>",
            "        </section>",
            "",
            "        <section",
            '          class="runtime-infrastructure-pane"',
            f'          aria-label="Selected {singular} evidence"',
            "        >",
            '          <header class="runtime-infrastructure-pane-head">',
            f"            <strong>Selected {singular.capitalize()} Evidence</strong>",
            "            <small>Recorded values remain unavailable until wiring.</small>",
            "          </header>",
            "          <div",
            '            class="runtime-infrastructure-detail"',
            f'            id="{prefix}Detail"',
            "          >",
            '            <div class="runtime-infrastructure-detail-groups">',
            details_html(contract_data),
            "            </div>",
            "          </div>",
            "        </section>",
            "      </div>",
            "",
            "      <div",
            '        class="runtime-infrastructure-message"',
            f'        id="{prefix}Message"',
            '        role="status"',
            '        aria-live="polite"',
            "      >",
            "        <strong>UI structure ready</strong>",
            (
                "        <span>Live evidence wiring is deferred to Part F "
                f"{contract_data['wiring_phase']}.</span>"
            ),
            "      </div>",
            "    </div>",
            "    <!-- END PART F 15-B5C-B5I RUNTIME INFRASTRUCTURE UI RESTRUCTURING -->",
            "  </section>",
        ]
    )


def build_candidate_html(source: str) -> str:
    candidate = source
    if MARKER in candidate:
        raise RuntimeError("The B5C-B5I UI restructuring marker already exists.")
    fragments: dict[str, tuple[int, int, str]] = {}
    for component, contract_data in COMPONENTS.items():
        start, end = panel_span(candidate, str(contract_data["panel_id"]))
        fragment = candidate[start:end]
        placeholder = f'data-runtime-owner-placeholder="{component}"'
        if placeholder not in fragment:
            raise RuntimeError(
                f"The certified placeholder is absent for {component}."
            )
        fragments[component] = (start, end, workspace_html(component, contract_data))
    for _component, (start, end, replacement) in sorted(
        fragments.items(),
        key=lambda item: item[1][0],
        reverse=True,
    ):
        candidate = candidate[:start] + replacement + candidate[end:]
    if candidate.count(OLD_CSS_VERSION) != 1:
        raise RuntimeError(
            "Expected exactly one certified Runtime stylesheet cache reference."
        )
    return candidate.replace(OLD_CSS_VERSION, NEW_CSS_VERSION, 1)


def component_structure_valid(
    html_source: str,
    component: str,
    contract_data: dict[str, Any],
) -> bool:
    prefix = str(contract_data["prefix"])
    required_ids = (
        f"{prefix}Workspace",
        f"{prefix}StateBadge",
        f"{prefix}Summary",
        f"{prefix}Filters",
        f"{prefix}Directory",
        f"{prefix}Detail",
        f"{prefix}Message",
    )
    start, end = panel_span(html_source, str(contract_data["panel_id"]))
    fragment = html_source[start:end]
    return (
        all(f'id="{identifier}"' in fragment for identifier in required_ids)
        and f'data-runtime-infrastructure-component="{component}"' in fragment
        and 'data-runtime-infrastructure-state="unavailable"' in fragment
        and (
            'data-runtime-infrastructure-states="loading ready empty '
            'no_match unavailable"'
        ) in fragment
        and fragment.count('class="runtime-infrastructure-summary-card"')
        == len(contract_data["summaries"])
        and fragment.count("data-runtime-infrastructure-filter=")
        == len(contract_data["filters"])
        and 'role="listbox"' in fragment
        and 'aria-live="polite"' in fragment
        and "<button" not in fragment.lower()
        and f'data-runtime-owner-placeholder="{component}"' not in fragment
    )


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
            "FINAL RESULT: PART F 15-B5C THROUGH 15-B5I RUNTIME "
            "INFRASTRUCTURE UI RESTRUCTURING NOT_CERTIFIED"
        )
    )
    return "\n".join(
        [
            "LINKCRAFTOR UNIVERSAL RUNTIME OWNER OPERATIONS",
            f"{STEP} {TITLE} CERTIFICATION",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "Patch mode: STRICT FAIL-CLOSED",
            f"Backup: {evidence.get('backup', 'NOT_CREATED')}",
            "Live evidence wiring performed: NO",
            "Endpoint requests added: NO",
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
            "- B5C installs one shared Runtime Infrastructure presentation shell.",
            "- B5D installs the complete Jobs monitoring structure.",
            "- B5E installs the complete Queues monitoring structure.",
            "- B5F installs the complete Workers & Leases monitoring structure.",
            "- B5G installs the complete Orchestration monitoring structure.",
            "- B5H installs the complete Execution monitoring structure.",
            "- B5I closes responsive, keyboard-focus, touch-target, long-identity and reduced-motion presentation requirements.",
            "- All filters and directories remain explicitly unavailable until B5J-B5O evidence wiring.",
            "- No retry, claim, cancel, recovery, termination, execution or other mutation control was added.",
            "- Existing Runtime Owner navigation, three GET requests and all Connected Domain authorities remain unchanged.",
            "",
            "NEXT STEP:",
            "Browser visual acceptance, then Part F 15-B5J - read-only wiring boundary inspection.",
            "",
            final,
            "",
        ]
    )


def run_patch(root: Path, report: Path) -> int:
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
    b5b_report = root / "backend/server/data/reports" / B5B_REPORT

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "changed_sources": [
            "backend/server/owner/index.html",
            "backend/server/owner/runtime_owner.css",
        ],
        "components": list(COMPONENTS),
        "presentation_states": list(PRESENTATION_STATES),
        "new_endpoint_requests": 0,
        "live_wiring_performed": False,
        "action_controls_added": False,
        "patch_retained": False,
        "rollback_performed": False,
    }
    error: dict[str, Any] = {}
    status = "NOT_CERTIFIED"
    originals: dict[str, str] = {}
    hashes_before: dict[str, str] = {}
    backup: Path | None = None
    wrote_sources = False

    try:
        checks["part_f_15_b5b_report_exists"] = b5b_report.is_file()
        checks["part_f_15_b5b_complete"] = (
            b5b_report.is_file()
            and b5b_report_complete(read_text(b5b_report))
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError(
                "The complete B5B blueprint or a required production source is unavailable."
            )

        watched = {**paths, "b5b_report": b5b_report}
        hashes_before = {
            name: sha256_path(path)
            for name, path in watched.items()
        }
        originals = {
            name: read_text(path)
            for name, path in paths.items()
        }
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = hashes_before[name] == expected
        if not all(
            checks[f"source_hash_{name}"]
            for name in EXPECTED_HASHES
        ):
            raise RuntimeError(
                "The certified B5B production-source baseline has changed."
            )

        checks["ui_restructuring_not_previously_present"] = (
            MARKER not in originals["index_html"]
            and MARKER not in originals["runtime_owner_css"]
        )
        checks["five_certified_placeholders_present"] = all(
            f'data-runtime-owner-placeholder="{component}"'
            in originals["index_html"]
            for component in COMPONENTS
        )
        if not all(
            checks[name]
            for name in (
                "ui_restructuring_not_previously_present",
                "five_certified_placeholders_present",
            )
        ):
            raise RuntimeError(
                "The certified B5B placeholder boundary is unavailable."
            )

        candidate_html = build_candidate_html(originals["index_html"])
        candidate_css = originals["runtime_owner_css"].rstrip() + CSS_APPEND
        candidate_js = originals["runtime_owner_js"]

        checks["candidate_html_ids_unique"] = html_ids_unique(candidate_html)
        checks["candidate_css_balanced"] = css_balanced(candidate_css)
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(
            candidate_js
        )
        checks["candidate_javascript_unchanged"] = (
            candidate_js == originals["runtime_owner_js"]
        )
        checks["all_five_component_structures_present"] = all(
            component_structure_valid(candidate_html, component, contract_data)
            for component, contract_data in COMPONENTS.items()
        )
        checks["all_five_placeholders_removed"] = all(
            f'data-runtime-owner-placeholder="{component}"'
            not in candidate_html
            for component in COMPONENTS
        )
        checks["shared_shell_present"] = all(
            token in candidate_html
            for token in (
                "runtime-infrastructure-workspace",
                "runtime-infrastructure-summary",
                "runtime-infrastructure-toolbar",
                "runtime-infrastructure-split",
                "runtime-infrastructure-message",
            )
        )
        checks["five_presentation_states_present"] = all(
            state in candidate_html
            for state in PRESENTATION_STATES
        )
        checks["responsive_contract_present"] = all(
            token in candidate_css
            for token in (
                "@media (max-width: 1180px)",
                "@media (max-width: 940px)",
                "@media (max-width: 700px)",
                "@media (max-width: 480px)",
            )
        )
        checks["accessibility_contract_present"] = all(
            token in candidate_html + candidate_css
            for token in (
                'role="listbox"',
                'aria-live="polite"',
                'aria-disabled="true"',
                ":focus-visible",
                "min-height: 44px",
                "overflow-wrap: anywhere",
            )
        )
        checks["reduced_motion_contract_present"] = (
            "@media (prefers-reduced-motion: reduce)" in candidate_css
        )
        checks["all_filters_disabled_until_wiring"] = (
            candidate_html.count(
                'class="runtime-infrastructure-toolbar"'
            ) == 5
            and candidate_html.count("<fieldset") >= 5
            and candidate_html.count("        disabled") >= 5
        )
        checks["no_action_controls_added"] = all(
            "<button" not in candidate_html[
                panel_span(candidate_html, str(contract_data["panel_id"]))[0]:
                panel_span(candidate_html, str(contract_data["panel_id"]))[1]
            ].lower()
            for contract_data in COMPONENTS.values()
        )
        checks["no_new_fetch_request_added"] = (
            candidate_js.count("fetch(")
            == originals["runtime_owner_js"].count("fetch(")
            == 3
        )
        checks["stylesheet_cache_version_advanced"] = (
            OLD_CSS_VERSION not in candidate_html
            and candidate_html.count(NEW_CSS_VERSION) == 1
        )

        prewrite_checks = (
            "candidate_html_ids_unique",
            "candidate_css_balanced",
            "candidate_javascript_syntax",
            "candidate_javascript_unchanged",
            "all_five_component_structures_present",
            "all_five_placeholders_removed",
            "shared_shell_present",
            "five_presentation_states_present",
            "responsive_contract_present",
            "accessibility_contract_present",
            "reduced_motion_contract_present",
            "all_filters_disabled_until_wiring",
            "no_action_controls_added",
            "no_new_fetch_request_added",
            "stylesheet_cache_version_advanced",
        )
        if not all(checks[name] for name in prewrite_checks):
            raise RuntimeError(
                "One or more B5C-B5I candidate-integrity checks failed."
            )

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = (
            root
            / "backend/server/data/runtime_backups"
            / f"part_f_15_b5c_b5i_{stamp}"
        )
        backup.mkdir(parents=True, exist_ok=False)
        for name, path in paths.items():
            destination = backup / path.relative_to(root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        evidence["backup"] = str(backup)
        checks["backup_created"] = backup.is_dir()

        write_text(paths["index_html"], candidate_html)
        write_text(paths["runtime_owner_css"], candidate_css)
        wrote_sources = True

        retained_html = read_text(paths["index_html"])
        retained_css = read_text(paths["runtime_owner_css"])
        retained_js = read_text(paths["runtime_owner_js"])
        checks["retained_html_ids_unique"] = html_ids_unique(retained_html)
        checks["retained_css_balanced"] = css_balanced(retained_css)
        checks["retained_javascript_syntax"] = javascript_syntax_valid(
            retained_js
        )
        checks["retained_markers"] = (
            retained_html.count(f"BEGIN {MARKER}") == 5
            and retained_html.count(f"END {MARKER}") == 5
            and retained_css.count(f"BEGIN {MARKER}") == 1
            and retained_css.count(f"END {MARKER}") == 1
        )
        checks["retained_component_structures"] = all(
            component_structure_valid(retained_html, component, contract_data)
            for component, contract_data in COMPONENTS.items()
        )
        checks["unchanged_owner_css"] = (
            sha256_path(paths["owner_css"]) == hashes_before["owner_css"]
        )
        checks["unchanged_owner_js"] = (
            sha256_path(paths["owner_js"]) == hashes_before["owner_js"]
        )
        checks["unchanged_runtime_owner_js"] = (
            sha256_path(paths["runtime_owner_js"])
            == hashes_before["runtime_owner_js"]
        )
        checks["unchanged_runtime_summary_api"] = (
            sha256_path(paths["runtime_summary_api"])
            == hashes_before["runtime_summary_api"]
        )
        checks["unchanged_pipeline_operations"] = (
            sha256_path(paths["pipeline_operations"])
            == hashes_before["pipeline_operations"]
        )
        checks["historical_b5b_report_unchanged"] = (
            sha256_path(b5b_report) == hashes_before["b5b_report"]
        )

        hashes_after = {
            name: sha256_path(path)
            for name, path in paths.items()
        }
        changed = [
            name
            for name in paths
            if hashes_after[name] != hashes_before[name]
        ]
        checks["only_two_ui_sources_changed"] = (
            changed == ["index_html", "runtime_owner_css"]
        )
        checks.update(
            {
                "production_jobs_created_no": True,
                "production_queue_claims_no": True,
                "production_handlers_executed_no": True,
                "production_workflow_persistence_no": True,
                "production_recovery_actions_no": True,
                "live_network_requests_during_certification_no": True,
            }
        )
        if not all(checks.values()):
            raise RuntimeError(
                "One or more retained B5C-B5I certification checks failed."
            )

        status = "CERTIFIED"
        evidence["patch_retained"] = True
        evidence["source_hashes_before"] = {
            name: hashes_before[name]
            for name in paths
        }
        evidence["source_hashes_after"] = hashes_after
        evidence["component_contracts"] = {
            component: {
                "label": contract_data["label"],
                "panel_id": contract_data["panel_id"],
                "workspace_id": f"{contract_data['prefix']}Workspace",
                "summary_metric_count": len(contract_data["summaries"]),
                "filter_count": len(contract_data["filters"]),
                "detail_group_count": len(contract_data["detail_groups"]),
                "wiring_phase": contract_data["wiring_phase"],
            }
            for component, contract_data in COMPONENTS.items()
        }
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        if wrote_sources and originals:
            for name in ("index_html", "runtime_owner_css"):
                if backup is not None:
                    stored = backup / paths[name].relative_to(root)
                    if stored.is_file():
                        shutil.copy2(stored, paths[name])
                        continue
                write_text(paths[name], originals[name])
            evidence["rollback_performed"] = True
            evidence["patch_retained"] = False

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
    print(f"PART_F_15_B5C_B5I_STATUS={status}")
    print(
        "PATCH_RETAINED="
        f"{'YES' if evidence.get('patch_retained') else 'NO'}"
    )
    print("LIVE_WIRING=NO")
    print("ACTION_CONTROLS=NO")
    return 0 if status == "CERTIFIED" else 1


def self_test() -> int:
    panels = "\n".join(
        "\n".join(
            [
                "<section",
                f'  id="{contract_data["panel_id"]}"',
                f'  data-runtime-owner-section-panel="{component}"',
                "  hidden",
                ">",
                f"  <h3>{contract_data['label']}</h3>",
                f'  <p data-runtime-owner-placeholder="{component}">Placeholder</p>',
                "</section>",
            ]
        )
        for component, contract_data in COMPONENTS.items()
    )
    mock = "\n".join(
        [
            '<!doctype html><html><head>',
            OLD_CSS_VERSION,
            "</head><body>",
            panels,
            "</body></html>",
        ]
    )
    candidate = build_candidate_html(mock)
    assert html_ids_unique(candidate)
    assert css_balanced(CSS_APPEND)
    assert OLD_CSS_VERSION not in candidate
    assert candidate.count(NEW_CSS_VERSION) == 1
    assert all(
        component_structure_valid(candidate, component, contract_data)
        for component, contract_data in COMPONENTS.items()
    )
    assert all(
        f'data-runtime-owner-placeholder="{component}"' not in candidate
        for component in COMPONENTS
    )
    print("PART_F_15_B5C_B5I_SELF_TEST=PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B5C_B5I_RUNTIME_INFRASTRUCTURE_UI_RESTRUCTURE.py "
            "<project_root> <report_path> | --self-test"
        )
    raise SystemExit(run_patch(Path(sys.argv[1]), Path(sys.argv[2])))
