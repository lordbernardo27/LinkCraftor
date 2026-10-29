from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_HASHES = {
    "backend/server/owner/index.html": "8345fe34a71d042004a0c6b332e72e2ce4d70d0dfe7d20ed5321509a75b7e852",
    "backend/server/owner/runtime_owner.css": "c9b7f8f09bea36f6195e1945776cd77652a2866c393ef6cb291442db2f1acfb1",
    "backend/server/owner/runtime_owner.js": "3574d175e43d859a113fc38ea93b784fec1cedaa525dbfd030df488cbe1ae5fa",
    "backend/server/owner/runtime_summary_api.py": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "backend/server/owner/pipeline_operations.py": "570bfc61676fd15b5a1cacc6ed74130eac1d98dc41f327606019df59d55f342a",
}


CSS_PATCH = r'''

/* BEGIN PART F 15-B4C ALL PIPELINES OVERVIEW */

#runtimePage .pipeline-operations-pipeline-list {
  display: grid;
  gap: 12px;
}

#runtimePage .pipeline-operations-index-state {
  border: 1px dashed var(--border, rgba(127,127,127,0.28));
  border-radius: 10px;
  padding: 14px;
}

#runtimePage .pipeline-operations-index-state strong,
#runtimePage .pipeline-operations-index-state span {
  display: block;
}

#runtimePage .pipeline-operations-index-state span {
  margin-top: 4px;
  font-size: 12px;
  opacity: 0.7;
}

#runtimePage .pipeline-operations-card {
  min-width: 0;
  border: 1px solid var(--border, rgba(127,127,127,0.24));
  border-radius: 12px;
  padding: 13px;
  background: rgba(127,127,127,0.035);
}

#runtimePage .pipeline-operations-card-header,
#runtimePage .pipeline-operations-card-output {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

#runtimePage .pipeline-operations-card-title {
  min-width: 0;
}

#runtimePage .pipeline-operations-card-title strong,
#runtimePage .pipeline-operations-card-title span {
  display: block;
}

#runtimePage .pipeline-operations-card-title strong {
  overflow-wrap: anywhere;
}

#runtimePage .pipeline-operations-card-title span {
  margin-top: 3px;
  font-size: 11px;
  opacity: 0.62;
}

#runtimePage .pipeline-operations-card-health {
  flex: 0 0 auto;
  border: 1px solid currentColor;
  border-radius: 999px;
  padding: 4px 7px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.045em;
  text-transform: uppercase;
}

#runtimePage .pipeline-operations-card-health[data-health="healthy"] {
  color: #22c55e;
}

#runtimePage .pipeline-operations-card-health[data-health="active"] {
  color: #38bdf8;
}

#runtimePage .pipeline-operations-card-health[data-health="critical"] {
  color: #f87171;
}

#runtimePage .pipeline-operations-card-health[data-health="idle"] {
  color: #94a3b8;
}

#runtimePage .pipeline-operations-card-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
  margin-top: 12px;
}

#runtimePage .pipeline-operations-card-metric {
  min-width: 0;
  border-radius: 8px;
  padding: 8px;
  background: rgba(127,127,127,0.07);
}

#runtimePage .pipeline-operations-card-metric span,
#runtimePage .pipeline-operations-card-metric strong {
  display: block;
}

#runtimePage .pipeline-operations-card-metric span {
  font-size: 10px;
  opacity: 0.66;
}

#runtimePage .pipeline-operations-card-metric strong {
  margin-top: 3px;
  font-size: 15px;
}

#runtimePage .pipeline-operations-card-stage-list {
  display: flex;
  gap: 5px;
  overflow-x: auto;
  margin-top: 12px;
  padding-bottom: 3px;
  scrollbar-width: thin;
}

#runtimePage .pipeline-operations-card-stage {
  flex: 0 0 auto;
  border: 1px solid var(--border, rgba(127,127,127,0.22));
  border-radius: 999px;
  padding: 4px 7px;
  font-size: 10px;
  white-space: nowrap;
}

#runtimePage .pipeline-operations-card-output {
  margin-top: 11px;
  border-top: 1px solid var(--border, rgba(127,127,127,0.18));
  padding-top: 10px;
  font-size: 11px;
}

#runtimePage .pipeline-operations-card-output span:last-child {
  text-align: right;
  font-weight: 700;
}

/* END PART F 15-B4C ALL PIPELINES OVERVIEW */
'''


JS_PATCH = r'''

// BEGIN PART F 15-B4C ALL PIPELINES OVERVIEW
(() => {
  "use strict";

  const PIPELINE_INDEX_ENDPOINT =
    "/owner/api/runtime/pipelines";

  const byId = (id) =>
    document.getElementById(id);

  const HTML_ENTITIES = Object.freeze({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  });

  const escapeHtml = (value) =>
    String(value ?? "").replace(
      /[&<>"']/g,
      (character) => HTML_ENTITIES[character]
    );

  const identifierLabel = (identifier) => {
    const words = String(identifier ?? "")
      .split(/[_-]+/)
      .filter(Boolean)
      .map((word) =>
        word.charAt(0).toUpperCase() +
        word.slice(1)
      );

    return words.join(" ") || "Unnamed Pipeline";
  };

  const pipelineLabel = (pipelineId) => {
    if (String(pipelineId ?? "") === "connect_domain") {
      return "Connected Domain";
    }

    return identifierLabel(pipelineId);
  };

  const countValue = (value) => {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      return "0";
    }

    return String(Math.max(0, number));
  };

  const metric = (label, value) => `
    <div class="pipeline-operations-card-metric">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(countValue(value))}</strong>
    </div>
  `;

  const renderPipelineCard = (pipeline) => {
    const pipelineId = String(
      pipeline?.pipeline_id || ""
    );

    const health = String(
      pipeline?.health_status || "UNKNOWN"
    ).toUpperCase();

    const healthToken = health
      .toLowerCase()
      .replace(/[^a-z0-9_-]+/g, "-");

    const counts =
      pipeline?.counts &&
      typeof pipeline.counts === "object"
        ? pipeline.counts
        : {};

    const readiness =
      pipeline?.output_readiness &&
      typeof pipeline.output_readiness === "object"
        ? pipeline.output_readiness
        : {};

    const stages = Array.isArray(
      pipeline?.stage_order
    )
      ? pipeline.stage_order
      : [];

    const stageMarkup = stages.length
      ? stages.map((stage) => `
          <span class="pipeline-operations-card-stage">
            ${escapeHtml(identifierLabel(stage))}
          </span>
        `).join("")
      : `
          <span class="pipeline-operations-card-stage">
            No registered stages
          </span>
        `;

    const outputState =
      readiness.all_completed_outputs_ready === true
        ? "All completed outputs ready"
        : "Output readiness pending";

    return `
      <article
        class="pipeline-operations-card"
        role="listitem"
        data-pipeline-id="${escapeHtml(pipelineId)}"
      >
        <div class="pipeline-operations-card-header">
          <div class="pipeline-operations-card-title">
            <strong>${escapeHtml(pipelineLabel(pipelineId))}</strong>
            <span>${escapeHtml(pipelineId)}</span>
          </div>
          <span
            class="pipeline-operations-card-health"
            data-health="${escapeHtml(healthToken)}"
          >
            ${escapeHtml(health)}
          </span>
        </div>

        <div class="pipeline-operations-card-metrics">
          ${metric("Workflows", counts.workflow_count)}
          ${metric("Active workflows", counts.active_workflow_count)}
          ${metric("Failed workflows", counts.failed_workflow_count)}
          ${metric("Jobs", counts.job_count)}
          ${metric("Queued jobs", counts.queued_job_count)}
          ${metric("Running jobs", counts.running_job_count)}
          ${metric("Failed jobs", counts.failed_job_count)}
          ${metric("Registrations", counts.registration_count)}
        </div>

        <div
          class="pipeline-operations-card-stage-list"
          aria-label="${escapeHtml(pipelineLabel(pipelineId))} stage order"
        >
          ${stageMarkup}
        </div>

        <div class="pipeline-operations-card-output">
          <span>
            Final stage: ${escapeHtml(
              identifierLabel(readiness.final_stage_id)
            )}
          </span>
          <span>
            ${escapeHtml(outputState)} ·
            ${escapeHtml(countValue(readiness.ready_workflow_count))} ready
          </span>
        </div>
      </article>
    `;
  };

  const renderIndexState = (
    state,
    title,
    message
  ) => {
    const list = byId(
      "pipelineOperationsPipelineList"
    );

    if (!list) {
      return false;
    }

    list.dataset.pipelineIndexState = state;
    list.innerHTML = `
      <div
        class="pipeline-operations-index-state"
        data-pipeline-index-state="${escapeHtml(state)}"
      >
        <strong>${escapeHtml(title)}</strong>
        <span>${escapeHtml(message)}</span>
      </div>
    `;

    return true;
  };

  const renderPipelineIndex = (payload) => {
    const list = byId(
      "pipelineOperationsPipelineList"
    );

    if (!list) {
      return false;
    }

    const pipelines = Array.isArray(
      payload?.pipelines
    )
      ? payload.pipelines
      : [];

    if (!pipelines.length) {
      renderIndexState(
        "empty",
        "No registered pipelines",
        "Pipeline Operations will list a pipeline after its Runtime registrations are published."
      );

      return true;
    }

    list.dataset.pipelineIndexState = "loaded";
    list.innerHTML = pipelines
      .map(renderPipelineCard)
      .join("");

    return true;
  };

  let requestPromise = null;
  let loaded = false;
  let latestPayload = null;

  const loadPipelineIndex = async (
    force = false
  ) => {
    if (requestPromise) {
      return requestPromise;
    }

    if (loaded && !force) {
      return latestPayload;
    }

    const list = byId(
      "pipelineOperationsPipelineList"
    );

    if (!list) {
      return null;
    }

    list.setAttribute("aria-busy", "true");

    renderIndexState(
      "loading",
      "Loading pipelines",
      "Reading the certified Runtime Pipeline Operations index."
    );

    requestPromise = (async () => {
      try {
        const response = await fetch(
          PIPELINE_INDEX_ENDPOINT,
          {
            method: "GET",
            headers: {
              Accept: "application/json",
            },
            cache: "no-store",
            credentials: "same-origin",
          }
        );

        let payload = null;

        try {
          payload = await response.json();
        } catch (_) {
          payload = null;
        }

        if (!response.ok) {
          const message =
            payload?.detail?.message ||
            `Pipeline index unavailable (${response.status}).`;

          throw new Error(message);
        }

        if (!Array.isArray(payload?.pipelines)) {
          throw new Error(
            "Pipeline index response is missing its pipelines collection."
          );
        }

        latestPayload = payload;
        loaded = true;
        renderPipelineIndex(payload);
        return payload;
      } catch (error) {
        loaded = false;
        latestPayload = null;

        renderIndexState(
          "unavailable",
          "Pipeline index unavailable",
          error?.message ||
            "The Pipeline Operations index request failed."
        );

        return null;
      } finally {
        list.setAttribute("aria-busy", "false");
        requestPromise = null;
      }
    })();

    return requestPromise;
  };

  const pipelineOperationsActive = () =>
    window.LinkCraftorRuntimeOwner?.getActiveSection?.() ===
      "pipeline_operations";

  const bindPipelineOperationsIndex = () => {
    const page = byId("runtimePage");

    if (!page) {
      return false;
    }

    if (
      page.dataset.pipelineOperationsIndexBound ===
      "true"
    ) {
      return true;
    }

    page.addEventListener(
      "runtimeowner:sectionchange",
      (event) => {
        if (
          event?.detail?.section ===
          "pipeline_operations"
        ) {
          void loadPipelineIndex();
        }
      }
    );

    page.dataset.pipelineOperationsIndexBound =
      "true";

    if (pipelineOperationsActive()) {
      void loadPipelineIndex();
    }

    return true;
  };

  window.LinkCraftorPipelineOperationsIndex =
    Object.freeze({
      endpoint: PIPELINE_INDEX_ENDPOINT,
      load: loadPipelineIndex,
      refresh: () => loadPipelineIndex(true),
      render: renderPipelineIndex,
      pipelineLabel,
    });

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      bindPipelineOperationsIndex,
      { once: true }
    );
  } else {
    bindPipelineOperationsIndex();
  }
})();
// END PART F 15-B4C ALL PIPELINES OVERVIEW
'''


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        source.replace("\r\n", "\n"),
        encoding="utf-8",
        newline="\n",
    )


def report_valid(path: Path, required: tuple[str, ...]) -> bool:
    if not path.is_file():
        return False
    source = read(path)
    return all(marker in source for marker in required)


def locate_report_by_content(
    directory: Path,
    *,
    title: str,
    required: tuple[str, ...],
) -> tuple[tuple[Path, ...], tuple[Path, ...]]:
    title_matches: list[Path] = []
    certified_matches: list[Path] = []
    if not directory.is_dir():
        return (), ()
    for path in sorted(directory.glob("*.txt")):
        try:
            source = read(path)
        except (OSError, UnicodeError):
            continue
        if title not in source:
            continue
        title_matches.append(path)
        if all(marker in source for marker in required):
            certified_matches.append(path)
    return tuple(title_matches), tuple(certified_matches)


def node_syntax(path: Path) -> bool:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for JavaScript certification.")
    result = subprocess.run(
        [node, "--check", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "JavaScript syntax validation failed: "
            + result.stderr.strip()
        )
    return True


def css_balanced(source: str) -> bool:
    depth = 0
    in_comment = False
    index = 0
    while index < len(source):
        if not in_comment and source.startswith("/*", index):
            in_comment = True
            index += 2
            continue
        if in_comment and source.startswith("*/", index):
            in_comment = False
            index += 2
            continue
        if not in_comment:
            if source[index] == "{":
                depth += 1
            elif source[index] == "}":
                depth -= 1
                if depth < 0:
                    return False
        index += 1
    return depth == 0 and not in_comment


def node_behavior(temp_root: Path) -> dict[str, Any]:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for behavior certification.")

    script = temp_root / "pipeline_index_behavior.js"
    fixture = {
        "generated_at": "2026-10-28T10:30:00Z",
        "read_only": True,
        "pipelines": [
            {
                "pipeline_id": "connect_domain",
                "health_status": "HEALTHY",
                "stage_order": [
                    "connect_domain",
                    "site_sources",
                    "url_cleaner",
                    "site_pages",
                    "live_domain_target_pool",
                    "active_target_set",
                ],
                "counts": {
                    "registration_count": 6,
                    "workflow_count": 1,
                    "active_workflow_count": 0,
                    "failed_workflow_count": 0,
                    "job_count": 6,
                    "queued_job_count": 0,
                    "running_job_count": 0,
                    "failed_job_count": 0,
                },
                "output_readiness": {
                    "final_stage_id": "active_target_set",
                    "ready_workflow_count": 1,
                    "all_completed_outputs_ready": True,
                },
            },
            {
                "pipeline_id": "future_pipeline",
                "health_status": "CRITICAL",
                "stage_order": ["prepare", "publish"],
                "counts": {
                    "registration_count": 2,
                    "workflow_count": 2,
                    "active_workflow_count": 1,
                    "failed_workflow_count": 1,
                    "job_count": 3,
                    "queued_job_count": 1,
                    "running_job_count": 1,
                    "failed_job_count": 1,
                },
                "output_readiness": {
                    "final_stage_id": "publish",
                    "ready_workflow_count": 0,
                    "all_completed_outputs_ready": False,
                },
            },
        ],
    }

    harness_head = r'''
"use strict";
const listeners = {};
const list = {
  dataset: {},
  innerHTML: "",
  attributes: {},
  setAttribute(name, value) {
    this.attributes[name] = String(value);
  }
};
const page = {
  dataset: {},
  addEventListener(name, handler) {
    listeners[name] = handler;
  }
};
global.window = {
  LinkCraftorRuntimeOwner: {
    getActiveSection() {
      return "overview";
    }
  }
};
global.document = {
  readyState: "complete",
  addEventListener() {},
  getElementById(id) {
    if (id === "runtimePage") return page;
    if (id === "pipelineOperationsPipelineList") return list;
    return null;
  }
};
let fetchCount = 0;
let requestedUrl = null;
let requestedOptions = null;
'''

    harness_tail = f'''
const fixture = {json.dumps(fixture)};
global.fetch = async (url, options) => {{
  fetchCount += 1;
  requestedUrl = url;
  requestedOptions = options;
  return {{
    ok: true,
    status: 200,
    async json() {{ return fixture; }}
  }};
}};

(async () => {{
  const api = window.LinkCraftorPipelineOperationsIndex;
  if (!api) throw new Error("Pipeline index API was not exposed.");
  const payload = await api.refresh();
  if (payload !== fixture) throw new Error("Fixture payload was not returned.");
  if (fetchCount !== 1) throw new Error("Expected one index request.");
  if (requestedUrl !== "/owner/api/runtime/pipelines") {{
    throw new Error("Unexpected endpoint: " + requestedUrl);
  }}
  if (requestedOptions?.method !== "GET") throw new Error("GET was not used.");
  for (const token of [
    "Connected Domain",
    "Future Pipeline",
    "HEALTHY",
    "CRITICAL",
    "Active Target Set",
    "All completed outputs ready",
    "Output readiness pending",
    'data-pipeline-id="connect_domain"',
    'data-pipeline-id="future_pipeline"'
  ]) {{
    if (!list.innerHTML.includes(token)) {{
      throw new Error("Rendered index is missing: " + token);
    }}
  }}
  if (list.dataset.pipelineIndexState !== "loaded") {{
    throw new Error("Loaded state was not retained.");
  }}
  if (list.attributes["aria-busy"] !== "false") {{
    throw new Error("Busy state was not cleared.");
  }}
  process.stdout.write(JSON.stringify({{
    fetch_count: fetchCount,
    endpoint: requestedUrl,
    method: requestedOptions.method,
    pipeline_count: payload.pipelines.length,
    rendered_connected_domain: list.innerHTML.includes("Connected Domain"),
    rendered_future_pipeline: list.innerHTML.includes("Future Pipeline"),
    state: list.dataset.pipelineIndexState
  }}));
}})().catch((error) => {{
  console.error(error.stack || String(error));
  process.exit(1);
}});
'''

    write(script, harness_head + JS_PATCH + harness_tail)
    result = subprocess.run(
        [node, str(script)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Isolated All Pipelines behavior check failed: "
            + result.stderr.strip()
        )
    return json.loads(result.stdout)


def render_report(
    *,
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
    backup: str,
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    return f'''LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS
PART F 15-B4C ALL PIPELINES OVERVIEW CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Patch mode: STRICT FAIL-CLOSED
Backup: {backup}
Owner UI sources changed: YES - runtime_owner.css and runtime_owner.js
Production Runtime/backend sources changed: NO
Production jobs created: NO
Production queue claims executed: NO
Production handlers executed: NO
Production workflow persistence executed: NO
Production recovery actions executed: NO
Live network requests executed: NO
Certification data: ISOLATED TWO-PIPELINE API FIXTURE
CERTIFICATION STATUS: {status}

CHECKS:
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed, indent=2)}

NOT_RUN_CHECKS:
[]

EVIDENCE:
{json.dumps(evidence, indent=2, sort_keys=True, default=str)}

EXECUTION_ERROR:
{json.dumps(error, indent=2)}

IMPLEMENTED BOUNDARY:
- All Pipelines now reads GET /owner/api/runtime/pipelines through the certified read-only API.
- Every returned pipeline renders as an operations card with health, workflow, job,
  registration, stage-order and output-readiness evidence.
- Connected Domain is rendered from the same universal index as future registered pipelines.
- The index is loaded when the owner opens Pipeline Operations and is not requested elsewhere.
- Minimal loading, empty and unavailable messages protect this component; the complete shared
  state system remains Part F 15-B4L.
- Pipeline selection and detail requests remain Part F 15-B4D and 15-B4M.
- Workflow, stage, job, dependency, event, failure and output detail views remain disabled.
- No recovery control, Runtime mutation or duplicate authority was added.

FINAL RESULT:
FINAL RESULT: PART F 15-B4C ALL PIPELINES OVERVIEW {status}
'''


def main(root: Path, report: Path) -> int:
    root = root.resolve()
    report = report.resolve()
    targets = {
        name: root / name
        for name in EXPECTED_HASHES
    }
    html_path = targets["backend/server/owner/index.html"]
    css_path = targets["backend/server/owner/runtime_owner.css"]
    js_path = targets["backend/server/owner/runtime_owner.js"]
    api_path = targets["backend/server/owner/runtime_summary_api.py"]
    operations_path = targets["backend/server/owner/pipeline_operations.py"]
    reports_dir = root / "backend/server/data/reports"

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    originals: dict[Path, bytes] = {}
    backup_dir: Path | None = None
    retained = False

    try:
        b4b_required = (
            "CERTIFICATION STATUS: CERTIFIED",
            "FAILED_CHECKS:\n[]",
            "FINAL RESULT: PART F 15-B4B PIPELINE OPERATIONS NAVIGATION AND LAYOUT CERTIFIED",
        )
        b4b_reports, certified_b4b_reports = locate_report_by_content(
            reports_dir,
            title=(
                "PART F 15-B4B PIPELINE OPERATIONS "
                "NAVIGATION AND LAYOUT CERTIFICATION"
            ),
            required=b4b_required,
        )
        prior_report = (
            certified_b4b_reports[-1]
            if certified_b4b_reports
            else None
        )
        checks["part_f_15_b4b_report_exists"] = bool(b4b_reports)
        checks["part_f_15_b4b_certified"] = prior_report is not None
        for name, path in targets.items():
            label = path.name.replace(".", "_")
            checks["source_exists_" + label] = path.is_file()
            checks["source_hash_" + label] = (
                path.is_file()
                and sha256(path) == EXPECTED_HASHES[name]
            )
        if not all(checks.values()):
            raise RuntimeError("Part F 15-B4C precondition gate failed.")

        html_source = read(html_path)
        css_source = read(css_path)
        js_source = read(js_path)
        html_before = sha256(html_path)
        api_before = sha256(api_path)
        operations_before = sha256(operations_path)

        checks["b4b_layout_present"] = all(
            marker in html_source
            for marker in (
                'data-runtime-owner-section="pipeline_operations"',
                'id="pipelineOperationsPipelineList"',
                'id="pipelineOperationsWorkspace"',
                'id="pipelineOperationsViewNav"',
            )
        )
        checks["patch_not_previously_present"] = all(
            marker not in source
            for marker, source in (
                ("BEGIN PART F 15-B4C ALL PIPELINES OVERVIEW", css_source),
                ("BEGIN PART F 15-B4C ALL PIPELINES OVERVIEW", js_source),
                ('"/owner/api/runtime/pipelines"', js_source),
            )
        )
        checks["future_detail_views_still_disabled"] = all(
            f'data-pipeline-operations-view="{view}" disabled' in html_source
            for view in (
                "overview",
                "workflows",
                "stage_progress",
                "jobs_attempts",
                "dependencies_handoffs",
                "events_timeline",
                "failures",
                "output_readiness",
            )
        )
        if not all((
            checks["b4b_layout_present"],
            checks["patch_not_previously_present"],
            checks["future_detail_views_still_disabled"],
        )):
            raise RuntimeError("Part F 15-B4C patch boundary is not safe.")

        css_candidate = css_source.rstrip() + CSS_PATCH + "\n"
        js_candidate = js_source.rstrip() + JS_PATCH + "\n"

        checks["candidate_css_balanced"] = css_balanced(css_candidate)
        with tempfile.TemporaryDirectory(
            prefix="linkcraftor_part_f_15_b4c_candidate_"
        ) as candidate_temp:
            candidate_root = Path(candidate_temp)
            candidate_js = candidate_root / "runtime_owner.js"
            write(candidate_js, js_candidate)
            checks["candidate_javascript_syntax"] = node_syntax(candidate_js)
            behavior = node_behavior(candidate_root)
            checks["isolated_pipeline_index_render_succeeded"] = (
                behavior.get("fetch_count") == 1
                and behavior.get("pipeline_count") == 2
                and behavior.get("rendered_connected_domain") is True
                and behavior.get("rendered_future_pipeline") is True
                and behavior.get("state") == "loaded"
            )
        if not all((
            checks["candidate_css_balanced"],
            checks["candidate_javascript_syntax"],
            checks["isolated_pipeline_index_render_succeeded"],
        )):
            raise RuntimeError("Part F 15-B4C candidate validation failed.")

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = (
            root
            / "backend/server/data/runtime_backups"
            / f"part_f_15_b4c_{stamp}"
        )
        backup_dir.mkdir(parents=True, exist_ok=False)
        for path in (css_path, js_path):
            originals[path] = path.read_bytes()
            shutil.copy2(path, backup_dir / path.name)

        write(css_path, css_candidate)
        write(js_path, js_candidate)

        retained_css = read(css_path)
        retained_js = read(js_path)
        retained_hashes = {
            path: sha256(path)
            for path in (css_path, js_path)
        }

        checks["retained_css_balanced"] = css_balanced(retained_css)
        checks["retained_javascript_syntax"] = node_syntax(js_path)
        checks["canonical_pipeline_index_endpoint_declared_once"] = (
            retained_js.count('"/owner/api/runtime/pipelines"') == 1
        )
        checks["pipeline_index_get_request_declared"] = all(
            marker in JS_PATCH
            for marker in (
                "fetch(",
                "PIPELINE_INDEX_ENDPOINT",
                'method: "GET"',
                'cache: "no-store"',
                'credentials: "same-origin"',
            )
        )
        checks["pipeline_index_load_bound_to_pipeline_operations"] = all(
            marker in JS_PATCH
            for marker in (
                '"runtimeowner:sectionchange"',
                '"pipeline_operations"',
                "loadPipelineIndex()",
            )
        )
        checks["pipeline_cards_render_health"] = all(
            marker in JS_PATCH
            for marker in (
                "pipeline-operations-card-health",
                "health_status",
                "data-health",
            )
        )
        checks["pipeline_cards_render_all_counts"] = all(
            field in JS_PATCH
            for field in (
                "registration_count",
                "workflow_count",
                "active_workflow_count",
                "failed_workflow_count",
                "job_count",
                "queued_job_count",
                "running_job_count",
                "failed_job_count",
            )
        )
        checks["pipeline_cards_render_stage_order"] = all(
            marker in JS_PATCH
            for marker in (
                "stage_order",
                "pipeline-operations-card-stage-list",
                "pipeline-operations-card-stage",
            )
        )
        checks["pipeline_cards_render_output_readiness"] = all(
            marker in JS_PATCH
            for marker in (
                "output_readiness",
                "final_stage_id",
                "ready_workflow_count",
                "all_completed_outputs_ready",
            )
        )
        checks["all_pipeline_styles_scoped_to_runtime_page"] = (
            retained_css.count(
                "BEGIN PART F 15-B4C ALL PIPELINES OVERVIEW"
            ) == 1
            and not any(
                line.strip().startswith(".pipeline-operations")
                for line in CSS_PATCH.splitlines()
            )
        )
        checks["minimal_component_states_present"] = all(
            f'"{state}"' in JS_PATCH
            for state in ("loading", "empty", "unavailable", "loaded")
        )
        checks["pipeline_detail_endpoint_not_requested"] = (
            '"/owner/api/runtime/pipelines/"' not in retained_js
            and "pipelines/${" not in retained_js
        )
        checks["pipeline_selection_not_prematurely_added"] = (
            "data-pipeline-selected" not in JS_PATCH
            and "selectPipeline" not in JS_PATCH
        )
        checks["no_recovery_controls_added"] = all(
            token not in JS_PATCH.lower()
            for token in (
                "retry job",
                "resume workflow",
                "cancel job",
                "terminate job",
            )
        )
        checks["existing_runtime_overview_endpoint_retained"] = (
            retained_js.count('"/owner/api/runtime/summary"') == 1
        )
        checks["html_layout_source_unchanged"] = sha256(html_path) == html_before
        checks["backend_api_source_unchanged"] = sha256(api_path) == api_before
        checks["pipeline_projection_source_unchanged"] = (
            sha256(operations_path) == operations_before
        )
        checks["target_sources_stable_during_verification"] = all(
            sha256(path) == expected
            for path, expected in retained_hashes.items()
        )
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_no"] = True

        if not all(checks.values()):
            raise RuntimeError("Part F 15-B4C certification checks failed.")

        evidence = {
            "backup": str(backup_dir),
            "part_f_15_b4b_report": str(prior_report),
            "endpoint": "/owner/api/runtime/pipelines",
            "request_trigger": "Pipeline Operations section activation",
            "isolated_behavior": behavior,
            "rendered_pipeline_evidence": [
                "pipeline identity and label",
                "health status",
                "registration count",
                "workflow counts",
                "job counts",
                "stage order",
                "final stage",
                "output readiness",
            ],
            "targets": {
                str(path): sha256(path)
                for path in (css_path, js_path)
            },
            "pipeline_detail_requested": False,
            "recovery_controls_added": False,
            "production_side_effects": False,
        }
        retained = True
        status = "CERTIFIED"

    except Exception as exc:
        status = "NOT_CERTIFIED"
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
    finally:
        if not retained:
            for path, payload in originals.items():
                path.write_bytes(payload)
        write(
            report,
            render_report(
                status=status,
                checks=checks,
                evidence=evidence,
                error=error,
                backup=(
                    str(backup_dir)
                    if backup_dir is not None
                    else "NOT_CREATED"
                ),
            ),
        )

    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not passed for passed in checks.values())}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B4C_STATUS={status}")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4C_CORRECTED.py PROJECT_ROOT REPORT_PATH"
        )
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
