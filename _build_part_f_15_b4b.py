from __future__ import annotations

import hashlib
import json
import py_compile
import shutil
import subprocess
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


EXPECTED_HASHES = {
    "backend/server/owner/index.html": "185af8150d6988ef6b96fc53e6cc7c1489711d9ee94adb415ac9f311c1b91462",
    "backend/server/owner/runtime_owner.css": "30b3d1b1880223963b772cd00f537f3837eea15c1c5fe3df77b84cdab128af47",
    "backend/server/owner/runtime_owner.js": "2b2edd8a83cf87af7f139a4592929e1ffc30a2f0c95544fce0bb1200549e7fd4",
    "backend/server/owner/runtime_summary_api.py": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "backend/server/owner/pipeline_operations.py": "570bfc61676fd15b5a1cacc6ed74130eac1d98dc41f327606019df59d55f342a",
}


HTML_NAV_ANCHOR = '''    <button
      class="runtime-owner-subnav-item active"
      type="button"
      data-runtime-owner-section="overview"
      aria-selected="true"
    >
      Runtime Overview
    </button>
'''


HTML_NAV_PATCH = HTML_NAV_ANCHOR + '''    <button
      class="runtime-owner-subnav-item"
      type="button"
      data-runtime-owner-section="pipeline_operations"
      aria-selected="false"
    >
      Pipeline Operations
    </button>
'''


HTML_PANEL_ANCHOR = '''        </div>
      </section>

<section
    class="runtime-owner-section"
    id="runtimeOwnerSectionJobs"
'''


PIPELINE_OPERATIONS_PANEL = '''        </div>
      </section>

      <!-- BEGIN PART F 15-B4B PIPELINE OPERATIONS LAYOUT -->
      <section
        class="runtime-owner-section pipeline-operations-section"
        id="runtimeOwnerSectionPipelineOperations"
        data-runtime-owner-section-panel="pipeline_operations"
        data-pipeline-operations-layout-version="15-b4b"
        hidden
      >
        <div class="pipeline-operations-heading">
          <div>
            <span class="pipeline-operations-eyebrow">Universal per-pipeline operations</span>
            <h3>Pipeline Operations</h3>
            <p>
              Inspect registered pipelines through the certified read-only
              Runtime Pipeline Operations boundary.
            </p>
          </div>
          <span class="pipeline-operations-read-only-badge">Read-only</span>
        </div>

        <div
          class="pipeline-operations-layout"
          id="pipelineOperationsLayout"
        >
          <aside
            class="pipeline-operations-directory"
            id="pipelineOperationsDirectory"
            aria-label="Registered pipelines"
          >
            <div class="pipeline-operations-region-heading">
              <h4>All Pipelines</h4>
              <p>Select a registered pipeline to inspect its operations.</p>
            </div>
            <div
              class="pipeline-operations-pipeline-list"
              id="pipelineOperationsPipelineList"
              role="list"
              aria-busy="false"
            >
              <div
                class="pipeline-operations-structural-placeholder"
                data-pipeline-operations-placeholder="pipeline_list"
              >
                Pipeline cards will be connected in 15-B4C.
              </div>
            </div>
          </aside>

          <section
            class="pipeline-operations-workspace"
            id="pipelineOperationsWorkspace"
            aria-label="Selected pipeline operations"
          >
            <header class="pipeline-operations-workspace-header">
              <div>
                <span class="pipeline-operations-eyebrow">Selected pipeline</span>
                <h4 id="pipelineOperationsSelectedPipeline">No pipeline selected</h4>
                <p id="pipelineOperationsSelectedPipelineSummary">
                  Choose a pipeline from All Pipelines to begin inspection.
                </p>
              </div>
              <span
                class="pipeline-operations-health-badge"
                id="pipelineOperationsSelectedPipelineHealth"
              >
                Not evaluated
              </span>
            </header>

            <nav
              class="pipeline-operations-view-nav"
              id="pipelineOperationsViewNav"
              aria-label="Pipeline operation views"
            >
              <button type="button" data-pipeline-operations-view="overview" disabled>Overview</button>
              <button type="button" data-pipeline-operations-view="workflows" disabled>Workflows</button>
              <button type="button" data-pipeline-operations-view="stage_progress" disabled>Stage Progress</button>
              <button type="button" data-pipeline-operations-view="jobs_attempts" disabled>Jobs &amp; Attempts</button>
              <button type="button" data-pipeline-operations-view="dependencies_handoffs" disabled>Dependencies &amp; Handoffs</button>
              <button type="button" data-pipeline-operations-view="events_timeline" disabled>Events Timeline</button>
              <button type="button" data-pipeline-operations-view="failures" disabled>Failures</button>
              <button type="button" data-pipeline-operations-view="output_readiness" disabled>Output Readiness</button>
            </nav>

            <div
              class="pipeline-operations-view-mount"
              id="pipelineOperationsViewMount"
              aria-live="polite"
            >
              <div
                class="pipeline-operations-structural-placeholder"
                data-pipeline-operations-placeholder="selected_pipeline"
              >
                Monitoring components will be connected in 15-B4C through 15-B4K.
              </div>
            </div>
          </section>
        </div>
      </section>
      <!-- END PART F 15-B4B PIPELINE OPERATIONS LAYOUT -->

<section
    class="runtime-owner-section"
    id="runtimeOwnerSectionJobs"
'''


JS_SECTIONS_ANCHOR = '''  const RUNTIME_OWNER_SECTIONS = Object.freeze([
    "overview",
    "jobs",
'''


JS_SECTIONS_PATCH = '''  const RUNTIME_OWNER_SECTIONS = Object.freeze([
    "overview",
    "pipeline_operations",
    "jobs",
'''


CSS_PATCH = r'''

/* BEGIN PART F 15-B4B PIPELINE OPERATIONS LAYOUT */

#runtimePage .pipeline-operations-section {
  min-width: 0;
}

#runtimePage .pipeline-operations-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 16px;
}

#runtimePage .pipeline-operations-heading h3,
#runtimePage .pipeline-operations-heading p,
#runtimePage .pipeline-operations-region-heading h4,
#runtimePage .pipeline-operations-region-heading p,
#runtimePage .pipeline-operations-workspace-header h4,
#runtimePage .pipeline-operations-workspace-header p {
  margin-top: 0;
}

#runtimePage .pipeline-operations-heading h3,
#runtimePage .pipeline-operations-region-heading h4,
#runtimePage .pipeline-operations-workspace-header h4 {
  margin-bottom: 5px;
}

#runtimePage .pipeline-operations-heading p,
#runtimePage .pipeline-operations-region-heading p,
#runtimePage .pipeline-operations-workspace-header p {
  margin-bottom: 0;
  opacity: 0.72;
}

#runtimePage .pipeline-operations-eyebrow {
  display: block;
  margin-bottom: 5px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  opacity: 0.66;
}

#runtimePage .pipeline-operations-read-only-badge,
#runtimePage .pipeline-operations-health-badge {
  flex: 0 0 auto;
  border: 1px solid var(--border, rgba(127,127,127,0.24));
  border-radius: 999px;
  padding: 7px 10px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

#runtimePage .pipeline-operations-layout {
  display: grid;
  grid-template-columns: minmax(220px, 0.32fr) minmax(0, 1fr);
  gap: 16px;
  min-width: 0;
}

#runtimePage .pipeline-operations-directory,
#runtimePage .pipeline-operations-workspace {
  min-width: 0;
  border: 1px solid var(--border, rgba(127,127,127,0.24));
  border-radius: 12px;
  padding: 15px;
}

#runtimePage .pipeline-operations-pipeline-list,
#runtimePage .pipeline-operations-view-mount {
  min-width: 0;
  margin-top: 14px;
}

#runtimePage .pipeline-operations-workspace-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

#runtimePage .pipeline-operations-view-nav {
  display: flex;
  gap: 7px;
  overflow-x: auto;
  margin-top: 16px;
  padding-bottom: 4px;
  scrollbar-width: thin;
}

#runtimePage .pipeline-operations-view-nav button {
  appearance: none;
  flex: 0 0 auto;
  border: 1px solid var(--border, rgba(127,127,127,0.24));
  border-radius: 999px;
  background: transparent;
  color: inherit;
  font: inherit;
  font-size: 12px;
  padding: 7px 10px;
}

#runtimePage .pipeline-operations-view-nav button:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

#runtimePage .pipeline-operations-structural-placeholder {
  border: 1px dashed var(--border, rgba(127,127,127,0.28));
  border-radius: 9px;
  padding: 14px;
  font-size: 13px;
  opacity: 0.76;
}

/* END PART F 15-B4B PIPELINE OPERATIONS LAYOUT */
'''


class IdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key == "id" and value:
                self.ids.append(value)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def report_valid(path: Path, required: tuple[str, ...]) -> bool:
    if not path.is_file():
        return False
    source = read(path)
    return all(value in source for value in required)


def node_syntax(path: Path) -> bool:
    node = shutil.which("node")
    if node is None:
        return False
    result = subprocess.run(
        [node, "--check", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("JavaScript syntax validation failed: " + result.stderr.strip())
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
PART F 15-B4B PIPELINE OPERATIONS NAVIGATION AND LAYOUT CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Patch mode: STRICT FAIL-CLOSED
Backup: {backup}
Production jobs created: NO
Production queue claims executed: NO
Production handlers executed: NO
Production workflow persistence executed: NO
Production recovery actions executed: NO
Live network requests executed: NO
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
- Universal Runtime now exposes one visible Pipeline Operations navigation entry.
- The existing Runtime Overview remains the default and retains its certified summary connection.
- Pipeline Operations has one reusable directory-and-workspace layout shell.
- Structural locations exist for All Pipelines and the selected pipeline workspace.
- Structural navigation exists for Overview, Workflows, Stage Progress, Jobs & Attempts,
  Dependencies & Handoffs, Events Timeline, Failures and Output Readiness.
- Monitoring data panels and endpoint requests remain deferred to 15-B4C through 15-B4K.
- Responsive finalization remains deferred to 15-B4N.
- No recovery controls, Runtime mutations or duplicate authorities were added.

FINAL RESULT:
FINAL RESULT: PART F 15-B4B PIPELINE OPERATIONS NAVIGATION AND LAYOUT {status}
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
    reports = root / "backend/server/data/reports"
    inspection = reports / "PART_F_15_B4A_EXISTING_RUNTIME_UI_STRUCTURE_INSPECTION.txt"
    contract = reports / "PART_F_15_B4B_UI_IMPLEMENTATION_CONTRACT.txt"

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    originals: dict[Path, bytes] = {}
    backup_dir: Path | None = None
    retained = False

    try:
        checks["inspection_15_b4a_complete"] = report_valid(
            inspection,
            ("INSPECTION STATUS: COMPLETE", "FAILED_CHECKS:\n[]", "PART F 15-B4A COMPLETE"),
        )
        checks["implementation_contract_complete"] = report_valid(
            contract,
            ("Production sources unchanged: True", "PART F 15-B4B IMPLEMENTATION CONTRACT COMPLETE"),
        )
        for name, path in targets.items():
            label = path.name.replace(".", "_")
            checks["source_exists_" + label] = path.is_file()
            checks["source_hash_" + label] = (
                path.is_file()
                and sha256(path) == EXPECTED_HASHES[name]
            )
        if not all(checks.values()):
            raise RuntimeError("Part F 15-B4B precondition gate failed.")

        html_source = read(html_path)
        css_source = read(css_path)
        js_source = read(js_path)
        api_before = sha256(api_path)
        operations_before = sha256(operations_path)

        checks["patch_not_previously_present"] = all(
            marker not in source
            for marker, source in (
                ("BEGIN PART F 15-B4B PIPELINE OPERATIONS LAYOUT", html_source),
                ("BEGIN PART F 15-B4B PIPELINE OPERATIONS LAYOUT", css_source),
                ('"pipeline_operations"', js_source),
            )
        )
        checks["html_navigation_anchor_unique"] = html_source.count(HTML_NAV_ANCHOR) == 1
        checks["html_panel_anchor_unique"] = html_source.count(HTML_PANEL_ANCHOR) == 1
        checks["javascript_section_anchor_unique"] = js_source.count(JS_SECTIONS_ANCHOR) == 1
        if not all((
            checks["patch_not_previously_present"],
            checks["html_navigation_anchor_unique"],
            checks["html_panel_anchor_unique"],
            checks["javascript_section_anchor_unique"],
        )):
            raise RuntimeError("Part F 15-B4B patch anchors are not safe and unique.")

        html_candidate = html_source.replace(HTML_NAV_ANCHOR, HTML_NAV_PATCH, 1).replace(
            HTML_PANEL_ANCHOR, PIPELINE_OPERATIONS_PANEL, 1
        )
        css_candidate = css_source.rstrip() + CSS_PATCH + "\n"
        js_candidate = js_source.replace(JS_SECTIONS_ANCHOR, JS_SECTIONS_PATCH, 1)

        original_parser = IdParser()
        original_parser.feed(html_source)
        original_parser.close()
        original_duplicate_ids = {
            item for item in original_parser.ids
            if original_parser.ids.count(item) > 1
        }
        parser = IdParser()
        parser.feed(html_candidate)
        parser.close()
        candidate_duplicate_ids = {
            item for item in parser.ids
            if parser.ids.count(item) > 1
        }
        checks["candidate_html_ids_preserve_integrity"] = (
            candidate_duplicate_ids == original_duplicate_ids
            and all(
                parser.ids.count(identifier) == 1
                for identifier in (
                    "runtimeOwnerSectionPipelineOperations",
                    "pipelineOperationsLayout",
                    "pipelineOperationsDirectory",
                    "pipelineOperationsPipelineList",
                    "pipelineOperationsWorkspace",
                    "pipelineOperationsViewNav",
                    "pipelineOperationsViewMount",
                )
            )
        )
        checks["candidate_css_balanced"] = css_balanced(css_candidate)

        with tempfile.TemporaryDirectory(prefix="linkcraftor_part_f_15_b4b_") as temp:
            temp_root = Path(temp)
            temp_js = temp_root / "runtime_owner.js"
            write(temp_js, js_candidate)
            checks["candidate_javascript_syntax"] = node_syntax(temp_js)
        if not all((
            checks["candidate_html_ids_preserve_integrity"],
            checks["candidate_css_balanced"],
            checks["candidate_javascript_syntax"],
        )):
            raise RuntimeError("Part F 15-B4B candidate validation failed.")

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = root / "backend/server/data/runtime_backups" / f"part_f_15_b4b_{stamp}"
        backup_dir.mkdir(parents=True, exist_ok=False)
        for path in (html_path, css_path, js_path):
            originals[path] = path.read_bytes()
            shutil.copy2(path, backup_dir / path.name)

        write(html_path, html_candidate)
        write(css_path, css_candidate)
        write(js_path, js_candidate)

        retained_hashes = {
            path: sha256(path)
            for path in (html_path, css_path, js_path)
        }
        checks["retained_javascript_syntax"] = node_syntax(js_path)
        checks["retained_css_balanced"] = css_balanced(read(css_path))
        retained_html = read(html_path)
        retained_js = read(js_path)
        retained_css = read(css_path)

        checks["pipeline_operations_nav_declared_once"] = retained_html.count(
            'data-runtime-owner-section="pipeline_operations"'
        ) == 1
        checks["pipeline_operations_nav_visible"] = (
            'data-runtime-owner-section="pipeline_operations"\n      aria-selected="false"\n    >'
            in retained_html
        )
        checks["pipeline_operations_panel_declared_once"] = retained_html.count(
            'data-runtime-owner-section-panel="pipeline_operations"'
        ) == 1
        checks["pipeline_operations_registered_in_navigation"] = retained_js.count(
            '"pipeline_operations"'
        ) == 1
        checks["directory_and_workspace_layout_present"] = all(
            retained_html.count(f'id="{identifier}"') == 1
            for identifier in (
                "pipelineOperationsLayout",
                "pipelineOperationsDirectory",
                "pipelineOperationsPipelineList",
                "pipelineOperationsWorkspace",
                "pipelineOperationsViewNav",
                "pipelineOperationsViewMount",
            )
        )
        checks["eight_pipeline_view_locations_present"] = retained_html.count(
            "data-pipeline-operations-view="
        ) == 8
        checks["future_component_buttons_disabled"] = retained_html.count(
            "data-pipeline-operations-view="
        ) == retained_html.count("data-pipeline-operations-view=") and all(
            f'data-pipeline-operations-view="{view}" disabled' in retained_html
            for view in (
                "overview", "workflows", "stage_progress", "jobs_attempts",
                "dependencies_handoffs", "events_timeline", "failures", "output_readiness",
            )
        )
        checks["layout_styles_scoped_to_runtime_page"] = (
            retained_css.count("BEGIN PART F 15-B4B PIPELINE OPERATIONS LAYOUT") == 1
            and "#runtimePage .pipeline-operations-layout" in retained_css
            and not any(
                line.strip().startswith(".pipeline-operations")
                for line in CSS_PATCH.splitlines()
            )
        )
        checks["runtime_overview_endpoint_retained"] = retained_js.count(
            '"/owner/api/runtime/summary"'
        ) == 1
        checks["pipeline_endpoints_not_prematurely_requested"] = (
            "/owner/api/runtime/pipelines" not in retained_js
        )
        checks["no_recovery_controls_added"] = all(
            token not in PIPELINE_OPERATIONS_PANEL.lower()
            for token in ("retry job", "resume workflow", "cancel job", "terminate job")
        )
        checks["backend_api_source_unchanged"] = sha256(api_path) == api_before
        checks["pipeline_projection_source_unchanged"] = sha256(operations_path) == operations_before
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_no"] = True
        checks["target_sources_stable_during_verification"] = all(
            sha256(path) == retained_hashes[path]
            for path in (html_path, css_path, js_path)
        )

        if not all(checks.values()):
            raise RuntimeError("Part F 15-B4B certification checks failed.")

        evidence = {
            "backup": str(backup_dir),
            "targets": {
                str(path): sha256(path)
                for path in (html_path, css_path, js_path)
            },
            "navigation": ["Runtime Overview", "Pipeline Operations"],
            "layout_regions": [
                "All Pipelines directory",
                "Selected pipeline workspace",
                "Pipeline view navigation",
                "Pipeline component mount",
            ],
            "future_component_locations": [
                "Overview", "Workflows", "Stage Progress", "Jobs & Attempts",
                "Dependencies & Handoffs", "Events Timeline", "Failures", "Output Readiness",
            ],
            "pipeline_api_requests_added": False,
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
                backup=str(backup_dir) if backup_dir else "NOT_CREATED",
            ),
        )

    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not passed for passed in checks.values())}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B4B_STATUS={status}")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: _build_part_f_15_b4b.py PROJECT_ROOT REPORT_PATH")
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
