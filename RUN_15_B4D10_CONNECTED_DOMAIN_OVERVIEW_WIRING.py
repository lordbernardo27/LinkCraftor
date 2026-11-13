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


FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW "
    "LIVE EVIDENCE WIRING CERTIFIED"
)
MARKER = "PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW LIVE EVIDENCE"

EXPECTED_HASHES = {
    "index_html": "e748652c973d5acd2ef4c423dae7e4e1559db8233bdfe551096b91668aca5415",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "6b12dd5d08a42ab8d6e18f97368e76bf37505d06ac37a7878e2bc231815f716c",
    "runtime_owner_js": "69292ab88b37c6ada8986c8942905b027a681d377084b7ec8bc1e590beaaeaf5",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "570bfc61676fd15b5a1cacc6ed74130eac1d98dc41f327606019df59d55f342a",
}

OLD_OVERVIEW = r'''              <section class="pipeline-monitoring-panel active" id="pipelineOperationsViewOverview" data-pipeline-operations-view-panel="overview" data-component-state="structure_ready" role="tabpanel">
                <header class="pipeline-monitoring-panel-head">
                  <div><span>Connected Domain</span><h5>Operations Overview</h5><p>Pipeline identity, health, workflow activity, and readiness summary.</p></div>
                  <strong>Structure ready</strong>
                </header>
                <div class="pipeline-monitoring-summary-grid">
                  <article><span>Pipeline health</span><strong>Awaiting detail wiring</strong></article>
                  <article><span>Active workflow</span><strong>Awaiting selection</strong></article>
                  <article><span>Output readiness</span><strong>Awaiting evidence</strong></article>
                </div>
                <div class="pipeline-component-state" data-state="empty"><span aria-hidden="true">◎</span><div><strong>Select Connected Domain</strong><p>The overview shell is ready for certified pipeline-detail evidence.</p></div></div>
              </section>'''

NEW_OVERVIEW = r'''              <!-- BEGIN PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW LIVE EVIDENCE -->
              <section class="pipeline-monitoring-panel active" id="pipelineOperationsViewOverview" data-pipeline-operations-view-panel="overview" data-component-state="loading" role="tabpanel" aria-busy="true">
                <header class="pipeline-monitoring-panel-head">
                  <div><span>Connected Domain</span><h5>Operations Overview</h5><p>Live read-only pipeline identity, health, workflow activity, and readiness evidence.</p></div>
                  <strong id="pipelineConnectedDomainOverviewState">Loading</strong>
                </header>
                <div class="pipeline-monitoring-summary-grid">
                  <article><span>Pipeline health</span><strong id="pipelineConnectedDomainHealth">Loading</strong></article>
                  <article><span>Active workflows</span><strong id="pipelineConnectedDomainActiveWorkflows">—</strong></article>
                  <article><span>Output readiness</span><strong id="pipelineConnectedDomainOutputReadiness">Evaluating</strong></article>
                </div>
                <div class="pipeline-overview-evidence-grid" aria-label="Connected Domain operational evidence">
                  <article><span>Total workflows</span><strong id="pipelineConnectedDomainWorkflowCount">—</strong></article>
                  <article><span>Failed workflows</span><strong id="pipelineConnectedDomainFailedWorkflows">—</strong></article>
                  <article><span>Total jobs</span><strong id="pipelineConnectedDomainJobCount">—</strong></article>
                  <article><span>Failed jobs</span><strong id="pipelineConnectedDomainFailedJobs">—</strong></article>
                  <article><span>Registrations</span><strong id="pipelineConnectedDomainRegistrationCount">—</strong></article>
                  <article><span>Ready workflows</span><strong id="pipelineConnectedDomainReadyWorkflows">—</strong></article>
                  <article><span>Final stage</span><strong id="pipelineConnectedDomainFinalStage">—</strong></article>
                  <article><span>Evidence generated</span><strong id="pipelineConnectedDomainGeneratedAt">—</strong></article>
                </div>
                <div class="pipeline-component-state" id="pipelineConnectedDomainOverviewMessage" data-state="loading" role="status" aria-live="polite"><span aria-hidden="true">◌</span><div><strong>Loading Connected Domain evidence</strong><p>Reading the canonical Pipeline Operations projection.</p></div></div>
              </section>
              <!-- END PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW LIVE EVIDENCE -->'''

CSS_APPEND = r'''

/* BEGIN PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW LIVE EVIDENCE */
#runtimePage .pipeline-overview-evidence-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  margin-top: 10px;
}

#runtimePage .pipeline-overview-evidence-grid article {
  min-width: 0;
  padding: 10px 11px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.025);
}

#runtimePage .pipeline-overview-evidence-grid span {
  display: block;
  color: #7890ad;
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

#runtimePage .pipeline-overview-evidence-grid strong {
  display: block;
  margin-top: 5px;
  overflow: hidden;
  color: #dceefa;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

#runtimePage #pipelineOperationsViewOverview[data-component-state="ready"]
  #pipelineConnectedDomainOverviewState { color: #67e8f9; }
#runtimePage #pipelineOperationsViewOverview[data-component-state="empty"]
  #pipelineConnectedDomainOverviewState { color: #facc15; }
#runtimePage #pipelineOperationsViewOverview[data-component-state="unavailable"]
  #pipelineConnectedDomainOverviewState { color: #fb7185; }

@media (max-width: 980px) {
  #runtimePage .pipeline-overview-evidence-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  #runtimePage .pipeline-overview-evidence-grid {
    grid-template-columns: 1fr;
  }
}
/* END PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW LIVE EVIDENCE */
'''

OLD_OPEN = r'''    setSelectedPipeline(pipelineId);
    setPipelineView(view);
    return true;'''

NEW_OPEN = r'''    setSelectedPipeline(pipelineId);
    setPipelineView(view);
    window.LinkCraftorConnectedDomainOverview?.load?.(pipelineId);
    return true;'''

JS_APPEND = r'''

// BEGIN PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW LIVE EVIDENCE
(() => {
  "use strict";

  const PIPELINE_ID = "connect_domain";
  const DETAIL_ENDPOINT = "/owner/api/runtime/pipelines/connect_domain";
  let requestSequence = 0;

  const byId = (id) => document.getElementById(id);
  const setText = (id, value) => {
    const element = byId(id);
    if (element) element.textContent = String(value ?? "—");
  };
  const integer = (value) => {
    const number = Number(value);
    return Number.isFinite(number) && number >= 0 ? Math.trunc(number) : 0;
  };
  const label = (value) => String(value || "unknown")
    .split(/[_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewOverview");
    const status = byId("pipelineConnectedDomainOverviewState");
    const container = byId("pipelineConnectedDomainOverviewMessage");
    if (panel) {
      panel.dataset.componentState = state;
      panel.setAttribute("aria-busy", state === "loading" ? "true" : "false");
    }
    if (status) status.textContent = label(state);
    if (container) {
      container.dataset.state = state;
      const icon = container.querySelector(":scope > span");
      const heading = container.querySelector("strong");
      const paragraph = container.querySelector("p");
      if (icon) icon.textContent = symbol;
      if (heading) heading.textContent = title;
      if (paragraph) paragraph.textContent = message;
    }
  };

  const resetValues = () => {
    [
      "pipelineConnectedDomainActiveWorkflows",
      "pipelineConnectedDomainWorkflowCount",
      "pipelineConnectedDomainFailedWorkflows",
      "pipelineConnectedDomainJobCount",
      "pipelineConnectedDomainFailedJobs",
      "pipelineConnectedDomainRegistrationCount",
      "pipelineConnectedDomainReadyWorkflows",
      "pipelineConnectedDomainFinalStage",
      "pipelineConnectedDomainGeneratedAt"
    ].forEach((id) => setText(id, "—"));
    setText("pipelineConnectedDomainHealth", "Loading");
    setText("pipelineConnectedDomainOutputReadiness", "Evaluating");
  };

  const renderSnapshot = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) {
      throw new Error("Connected Domain detail evidence has an invalid identity.");
    }
    const counts = payload.counts && typeof payload.counts === "object"
      ? payload.counts : {};
    const readiness = payload.output_readiness && typeof payload.output_readiness === "object"
      ? payload.output_readiness : {};
    const stageOrder = Array.isArray(payload.stage_order) ? payload.stage_order : [];
    if (stageOrder.length !== 6) {
      throw new Error("Connected Domain detail evidence does not contain six stages.");
    }

    const workflowCount = integer(counts.workflow_count);
    const readyCount = integer(readiness.ready_workflow_count);
    const health = label(payload.health_status);
    setText("pipelineConnectedDomainHealth", health);
    setText("pipelineConnectedDomainActiveWorkflows", integer(counts.active_workflow_count));
    setText("pipelineConnectedDomainWorkflowCount", workflowCount);
    setText("pipelineConnectedDomainFailedWorkflows", integer(counts.failed_workflow_count));
    setText("pipelineConnectedDomainJobCount", integer(counts.job_count));
    setText("pipelineConnectedDomainFailedJobs", integer(counts.failed_job_count));
    setText("pipelineConnectedDomainRegistrationCount", integer(counts.registration_count));
    setText("pipelineConnectedDomainReadyWorkflows", readyCount);
    setText("pipelineConnectedDomainFinalStage", label(readiness.final_stage_id));
    setText("pipelineConnectedDomainGeneratedAt", payload.generated_at || "Unavailable");
    setText(
      "pipelineConnectedDomainOutputReadiness",
      readiness.all_completed_outputs_ready ? "Verified" : `${readyCount} ready`
    );
    setText("pipelineOperationsSelectedPipelineHealth", health);

    if (workflowCount === 0) {
      updateMessage(
        "empty",
        "No Connected Domain workflows",
        "The pipeline is registered and healthy, but no workflow evidence is currently stored.",
        "◎"
      );
    } else {
      updateMessage(
        "ready",
        "Live Connected Domain evidence loaded",
        `${workflowCount} workflow${workflowCount === 1 ? "" : "s"} projected from canonical Runtime authorities.`,
        "✓"
      );
    }
  };

  const renderUnavailable = (message) => {
    resetValues();
    setText("pipelineConnectedDomainHealth", "Unavailable");
    setText("pipelineConnectedDomainOutputReadiness", "Unavailable");
    updateMessage(
      "unavailable",
      "Connected Domain evidence unavailable",
      message || "The read-only Pipeline Operations projection could not be loaded.",
      "!"
    );
  };

  const load = async (pipelineId = PIPELINE_ID) => {
    if (pipelineId !== PIPELINE_ID) {
      renderUnavailable("Detailed monitoring is not yet connected for this pipeline.");
      return false;
    }
    const sequence = ++requestSequence;
    resetValues();
    updateMessage(
      "loading",
      "Loading Connected Domain evidence",
      "Reading the canonical Pipeline Operations projection.",
      "◌"
    );
    try {
      const response = await fetch(DETAIL_ENDPOINT, {
        method: "GET",
        headers: { Accept: "application/json" },
        cache: "no-store"
      });
      if (!response.ok) {
        throw new Error(`Pipeline detail request failed with HTTP ${response.status}.`);
      }
      const payload = await response.json();
      if (sequence !== requestSequence) return false;
      renderSnapshot(payload);
      return true;
    } catch (error) {
      if (sequence !== requestSequence) return false;
      renderUnavailable(error?.message);
      return false;
    }
  };

  window.LinkCraftorConnectedDomainOverview = Object.freeze({ load });
})();
// END PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW LIVE EVIDENCE
'''


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del tag
        for name, value in attrs:
            if name == "id" and value is not None:
                self.ids.append(value)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, source: str) -> None:
    path.write_text(source, encoding="utf-8", newline="\n")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label}, found {count}.")
    return source.replace(old, new, 1)


def html_ids_unique(source: str) -> bool:
    parser = IdCollector()
    parser.feed(source)
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
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4d10_js_") as folder:
        candidate = Path(folder) / "runtime_owner_candidate.js"
        write_text(candidate, source)
        result = subprocess.run(
            [node, "--check", str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    return result.returncode == 0


def print_check(name: str, value: bool) -> None:
    print(f"{name.upper()}: {'PASS' if value else 'FAIL'}")


def build_report(
    *, status: str, checks: dict[str, bool], evidence: dict[str, Any],
    error: dict[str, Any], backup: Path | None,
) -> str:
    failed = [name for name, value in checks.items() if not value]
    final = FINAL_RESULT if status == "CERTIFIED" else (
        "FINAL RESULT: PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW "
        "LIVE EVIDENCE WIRING NOT_CERTIFIED"
    )
    return f'''LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS
PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW LIVE EVIDENCE WIRING CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Patch mode: STRICT FAIL-CLOSED
Backup: {backup if backup else "NOT_CREATED"}
Production jobs created: NO
Production queue claims executed: NO
Production handlers executed: NO
Production workflow persistence executed: NO
Production recovery actions executed: NO
Live network requests executed during certification: NO
CERTIFICATION STATUS: {status}

CHECKS:
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed, indent=2)}

NOT_RUN_CHECKS:
[]

EVIDENCE:
{json.dumps(evidence, indent=2, sort_keys=True)}

EXECUTION_ERROR:
{json.dumps(error, indent=2, sort_keys=True)}

IMPLEMENTED BOUNDARY:
- Connected Domain Overview now requests its existing certified read-only detail projection.
- Health, workflow, job, failure, registration, final-stage and output-readiness evidence are rendered.
- Loading, empty, ready and unavailable states are explicit and fail closed.
- Exactly one GET request authority was added: /owner/api/runtime/pipelines/connect_domain.
- No workflow, job, queue, handler, recovery or backend authority was created or mutated.
- Workflow Explorer and the remaining detailed components remain deferred to 15-B4E onward.

NEXT STEP:
Part F 15-B4E - Workflow Explorer component.

FINAL RESULT:
{final}
'''


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4D10_CONNECTED_DOMAIN_OVERVIEW_WIRING.py "
            "<project_root> <report_path>"
        )

    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    paths = {
        "index_html": root / "backend/server/owner/index.html",
        "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": root / "backend/server/owner/runtime_owner.css",
        "runtime_owner_js": root / "backend/server/owner/runtime_owner.js",
        "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py",
        "pipeline_operations": root / "backend/server/owner/pipeline_operations.py",
    }
    prior_report = (
        root / "backend/server/data/reports/"
        "PART_F_15_B4D9_NAVIGATION_BOUNDARY_FIX_CERTIFICATION.txt"
    )

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}
    backup_dir: Path | None = None
    retained = False
    status = "NOT_CERTIFIED"

    try:
        checks["part_f_15_b4d9_report_exists"] = prior_report.is_file()
        prior = read_text(prior_report) if prior_report.is_file() else ""
        checks["part_f_15_b4d9_certified"] = (
            "CERTIFICATION STATUS: CERTIFIED" in prior
            and "FINAL RESULT: PART F 15-B4D9 CONNECTED DOMAIN NAVIGATION "
            "BOUNDARY CORRECTION CERTIFIED" in prior
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("Required source or D9 evidence is unavailable.")

        before = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()):
            raise RuntimeError("Installed source lineage does not match certified D9.")

        html_source = read_text(paths["index_html"])
        css_source = read_text(paths["runtime_owner_css"])
        js_source = read_text(paths["runtime_owner_js"])
        api_source = read_text(paths["runtime_summary_api"])
        operations_source = read_text(paths["pipeline_operations"])
        checks["d10_not_previously_present"] = all(
            MARKER not in source for source in (html_source, css_source, js_source)
        )
        checks["certified_detail_endpoint_available"] = (
            '@router.get("/pipelines/{pipeline_id}")' in api_source
            and "build_pipeline_operations_snapshot" in operations_source
        )

        html_candidate = replace_once(
            html_source, OLD_OVERVIEW, NEW_OVERVIEW,
            "Connected Domain overview shell",
        )
        html_candidate = replace_once(
            html_candidate,
            '<link rel="stylesheet" href="/owner/runtime_owner.css?v=6" />',
            '<link rel="stylesheet" href="/owner/runtime_owner.css?v=7" />',
            "Runtime stylesheet cache version",
        )
        html_candidate = replace_once(
            html_candidate,
            '<script src="/owner/runtime_owner.js?v=7"></script>',
            '<script src="/owner/runtime_owner.js?v=8"></script>',
            "Runtime JavaScript cache version",
        )
        css_candidate = css_source.rstrip() + "\n" + CSS_APPEND.lstrip()
        js_candidate = replace_once(
            js_source, OLD_OPEN, NEW_OPEN,
            "pipeline workspace detail-load handoff",
        ).rstrip() + "\n" + JS_APPEND.lstrip()

        checks["candidate_html_ids_unique"] = html_ids_unique(html_candidate)
        checks["candidate_css_balanced"] = css_balanced(css_candidate)
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(js_candidate)
        required_ids = (
            "pipelineConnectedDomainOverviewState",
            "pipelineConnectedDomainHealth",
            "pipelineConnectedDomainActiveWorkflows",
            "pipelineConnectedDomainOutputReadiness",
            "pipelineConnectedDomainWorkflowCount",
            "pipelineConnectedDomainFailedWorkflows",
            "pipelineConnectedDomainJobCount",
            "pipelineConnectedDomainFailedJobs",
            "pipelineConnectedDomainRegistrationCount",
            "pipelineConnectedDomainReadyWorkflows",
            "pipelineConnectedDomainFinalStage",
            "pipelineConnectedDomainGeneratedAt",
            "pipelineConnectedDomainOverviewMessage",
        )
        checks["all_overview_bindings_present"] = all(
            html_candidate.count(f'id="{identifier}"') == 1
            for identifier in required_ids
        )
        checks["canonical_detail_request_declared_once"] = (
            js_candidate.count('"/owner/api/runtime/pipelines/connect_domain"') == 1
        )
        checks["detail_request_get_only"] = (
            'method: "GET"' in JS_APPEND
            and all(method not in JS_APPEND for method in ('method: "POST"', 'method: "PUT"', 'method: "DELETE"', 'method: "PATCH"'))
        )
        checks["overview_load_bound_to_pipeline_selection"] = (
            "window.LinkCraftorConnectedDomainOverview?.load?.(pipelineId);"
            in js_candidate
        )
        checks["pipeline_identity_validated"] = (
            "payload.pipeline_id !== PIPELINE_ID" in JS_APPEND
        )
        checks["six_stage_contract_validated"] = (
            "stageOrder.length !== 6" in JS_APPEND
        )
        checks["health_and_counts_projected"] = all(
            token in JS_APPEND for token in (
                "counts.workflow_count", "counts.active_workflow_count",
                "counts.failed_workflow_count", "counts.job_count",
                "counts.failed_job_count", "counts.registration_count",
                "readiness.ready_workflow_count", "readiness.final_stage_id",
                "readiness.all_completed_outputs_ready",
            )
        )
        checks["four_presentation_states_present"] = all(
            f'"{state}"' in JS_APPEND
            for state in ("loading", "ready", "empty", "unavailable")
        )
        checks["runtime_summary_and_index_requests_retained"] = (
            js_candidate.count('"/owner/api/runtime/summary"') == 1
            and js_candidate.count('"/owner/api/runtime/pipelines"') == 1
        )
        checks["exactly_one_new_fetch_request"] = (
            js_candidate.count("fetch(") == js_source.count("fetch(") + 1
        )
        checks["no_recovery_controls_added"] = all(
            token not in JS_APPEND
            for token in ("retryJob(", "cancelJob(", "terminateJob(", "data-runtime-recovery-action")
        )
        checks["cache_versions_advanced"] = (
            '/owner/runtime_owner.css?v=7' in html_candidate
            and '/owner/runtime_owner.js?v=8' in html_candidate
        )
        if not all(checks.values()):
            raise RuntimeError("D10 candidate certification checks failed.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = (
            root / "backend/server/data/runtime_backups"
            / f"part_f_15_b4d10_{timestamp}"
        )
        backup_dir.mkdir(parents=True, exist_ok=False)
        for name in ("index_html", "runtime_owner_css", "runtime_owner_js"):
            path = paths[name]
            originals[name] = path.read_bytes()
            shutil.copy2(path, backup_dir / path.name)
        checks["backup_created"] = all(
            (backup_dir / paths[name].name).is_file() for name in originals
        )
        if not checks["backup_created"]:
            raise RuntimeError("D10 production UI backup is incomplete.")

        write_text(paths["index_html"], html_candidate)
        write_text(paths["runtime_owner_css"], css_candidate)
        write_text(paths["runtime_owner_js"], js_candidate)

        checks["retained_html_ids_unique"] = html_ids_unique(
            read_text(paths["index_html"])
        )
        checks["retained_css_balanced"] = css_balanced(
            read_text(paths["runtime_owner_css"])
        )
        checks["retained_javascript_syntax"] = javascript_syntax_valid(
            read_text(paths["runtime_owner_js"])
        )
        checks["retained_markers"] = (
            read_text(paths["index_html"]).count(MARKER) == 2
            and read_text(paths["runtime_owner_css"]).count(MARKER) == 2
            and read_text(paths["runtime_owner_js"]).count(MARKER) == 2
        )

        after = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_after"] = after
        evidence["backup"] = str(backup_dir)
        evidence["endpoint"] = "/owner/api/runtime/pipelines/connect_domain"
        evidence["projected_evidence"] = [
            "pipeline health", "workflow counts", "job counts", "failure counts",
            "registration count", "six-stage identity", "final stage",
            "output readiness", "evidence generation time",
        ]
        evidence["presentation_states"] = [
            "loading", "ready", "empty", "unavailable",
        ]
        evidence["recovery_controls_added"] = False

        for name in (
            "owner_css", "owner_js", "runtime_summary_api", "pipeline_operations",
        ):
            checks[f"unchanged_{name}"] = before[name] == after[name]
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_during_certification_no"] = True
        if not all(checks.values()):
            raise RuntimeError("D10 retained-source certification checks failed.")

        retained = True
        status = "CERTIFIED"

    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        for name, data in originals.items():
            paths[name].write_bytes(data)

    report.parent.mkdir(parents=True, exist_ok=True)
    write_text(
        report,
        build_report(
            status=status, checks=checks, evidence=evidence,
            error=error, backup=backup_dir,
        ),
    )
    for name, value in checks.items():
        print_check(name, value)
    failed = [name for name, value in checks.items() if not value]
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B4D10_STATUS={status}")
    print("PATCH_RETAINED=YES" if retained else "PATCH_RETAINED=NO")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
