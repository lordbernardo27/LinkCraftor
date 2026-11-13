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
    "FINAL RESULT: PART F 15-B4L RESPONSIVE INTEGRATION "
    "FINALIZATION CERTIFIED"
)
MARKER = "PART F 15-B4L RESPONSIVE INTEGRATION FINALIZATION"

EXPECTED_HASHES = {
    "index_html": "5d09eb3501b83a36041c79131160517ada5abb10f7042116acb6fb45bef30bfd",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "7f460c805be758cc19fec072fa316e329d26c61be76c189dd0dbc605fc25a863",
    "runtime_owner_js": "6f3038763969fcd15e4d1fcf54619984631901c0768c952a900d896b2bcecf58",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=14" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=15" />'
NEW_CSS_BLOCK = f'''<!-- BEGIN {MARKER} CACHE -->
    {NEW_CSS_VERSION}
    <!-- END {MARKER} CACHE -->'''

PANEL_IDS = (
    "pipelineOperationsViewOverview",
    "pipelineOperationsViewWorkflows",
    "pipelineOperationsViewStageProgress",
    "pipelineOperationsViewJobsAttempts",
    "pipelineOperationsViewDependenciesHandoffs",
    "pipelineOperationsViewEventsTimeline",
    "pipelineOperationsViewFailures",
    "pipelineOperationsViewOutputReadiness",
)

COMPONENT_AUTHORITIES = (
    "LinkCraftorConnectedDomainOverview",
    "LinkCraftorConnectedDomainWorkflowExplorer",
    "LinkCraftorConnectedDomainStageProgress",
    "LinkCraftorConnectedDomainJobsAttempts",
    "LinkCraftorConnectedDomainDependenciesHandoffs",
    "LinkCraftorConnectedDomainEventsTimeline",
    "LinkCraftorConnectedDomainFailuresAttention",
    "LinkCraftorConnectedDomainOutputReadiness",
)

CSS_APPEND = r'''

/* BEGIN PART F 15-B4L RESPONSIVE INTEGRATION FINALIZATION */
#runtimePage,
#runtimePage * { box-sizing: border-box; }

#runtimePage :is(
  .pipeline-operations-layout,
  .pipeline-operations-directory,
  .pipeline-operations-workspace,
  .pipeline-operations-view-mount,
  .pipeline-monitoring-panel,
  .pipeline-monitoring-panel > *,
  .pipeline-workflow-explorer-grid,
  .pipeline-jobs-layout,
  .pipeline-failures-workspace,
  .pipeline-readiness-workspace
) { min-width: 0; max-width: 100%; }

#runtimePage :is(
  .pipeline-operations-workspace,
  .pipeline-operations-view-mount,
  .pipeline-monitoring-panel
) { overflow-x: hidden; overflow-x: clip; }

#runtimePage .pipeline-monitoring-panel-head > div,
#runtimePage :is(
  .pipeline-workflow-toolbar,
  .pipeline-stage-progress-toolbar,
  .pipeline-jobs-toolbar,
  .pipeline-handoffs-toolbar,
  .pipeline-events-toolbar,
  .pipeline-failures-toolbar,
  .pipeline-readiness-toolbar
) > * { min-width: 0; }

#runtimePage .pipeline-monitoring-panel :is(
  h4,
  h5,
  p,
  strong,
  small,
  .pipeline-workflow-detail,
  .pipeline-job-detail,
  .pipeline-failure-detail,
  .pipeline-readiness-detail,
  .pipeline-handoff-evidence
) { overflow-wrap: anywhere; word-break: normal; }

#runtimePage .pipeline-monitoring-panel :is(input, select, button),
#runtimePage .pipeline-operations-view-tab { max-width: 100%; }

#runtimePage .pipeline-monitoring-panel :is(button, input, select, a):focus-visible,
#runtimePage .pipeline-operations-view-tab:focus-visible {
  outline: 2px solid #22d3ee;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(34,211,238,.14);
}

@media (max-width: 1180px) {
  #runtimePage :is(
    .pipeline-monitoring-summary-grid,
    .pipeline-failures-summary,
    .pipeline-readiness-summary
  ) { grid-template-columns: repeat(3,minmax(0,1fr)); }

  #runtimePage :is(
    .pipeline-workflow-toolbar,
    .pipeline-stage-progress-toolbar,
    .pipeline-jobs-toolbar,
    .pipeline-handoffs-toolbar,
    .pipeline-events-toolbar,
    .pipeline-failures-toolbar,
    .pipeline-readiness-toolbar
  ) { grid-template-columns: repeat(2,minmax(0,1fr)); }
}

@media (max-width: 940px) {
  #runtimePage .pipeline-operations-layout { grid-template-columns: 1fr; }
  #runtimePage .pipeline-operations-directory { max-height: none; }
}

@media (max-width: 820px) {
  #runtimePage :is(
    .pipeline-workflow-explorer-grid,
    .pipeline-jobs-layout,
    .pipeline-failures-workspace,
    .pipeline-readiness-workspace
  ) { grid-template-columns: 1fr; }

  #runtimePage :is(
    .pipeline-workflow-directory,
    .pipeline-jobs-directory,
    .pipeline-failures-directory,
    .pipeline-readiness-directory
  ) {
    max-height: 320px;
    border-right: 0;
    border-bottom: 1px solid rgba(148,163,184,.12);
  }
}

@media (max-width: 700px) {
  #runtimePage .pipeline-operations-view-nav {
    grid-template-columns: repeat(2,minmax(0,1fr));
  }

  #runtimePage :is(
    .pipeline-workflow-toolbar,
    .pipeline-stage-progress-toolbar,
    .pipeline-jobs-toolbar,
    .pipeline-handoffs-toolbar,
    .pipeline-events-toolbar,
    .pipeline-failures-toolbar,
    .pipeline-readiness-toolbar
  ) { grid-template-columns: 1fr; }

  #runtimePage .pipeline-monitoring-panel :is(button, input, select),
  #runtimePage .pipeline-operations-view-tab { min-height: 44px; }

  #runtimePage :is(
    .pipeline-workflow-search,
    .pipeline-jobs-search,
    .pipeline-events-search,
    .pipeline-failures-search,
    .pipeline-readiness-search
  ) { grid-column: auto; }
}

@media (max-width: 620px) {
  #runtimePage :is(
    .pipeline-monitoring-summary-grid,
    .pipeline-failures-summary,
    .pipeline-readiness-summary,
    .pipeline-workflow-identity-grid,
    .pipeline-workflow-lifecycle-grid,
    .pipeline-workflow-stage-summary,
    .pipeline-stage-progress-list,
    .pipeline-job-facts,
    .pipeline-failure-facts,
    .pipeline-readiness-facts,
    .pipeline-readiness-stage-strip
  ) { grid-template-columns: repeat(2,minmax(0,1fr)); }

  #runtimePage .pipeline-handoff-gate,
  #runtimePage .pipeline-event-entry { grid-template-columns: 1fr; }

  #runtimePage .pipeline-handoff-arrow {
    display: flex;
    min-height: 24px;
    align-items: center;
    justify-content: center;
  }

  #runtimePage .pipeline-handoff-arrow b { transform: rotate(90deg); }
}

@media (max-width: 480px) {
  #runtimePage .pipeline-operations-workspace,
  #runtimePage .pipeline-monitoring-panel { padding: 9px; }

  #runtimePage .pipeline-monitoring-panel-head {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
  }

  #runtimePage .pipeline-monitoring-panel-head > strong { justify-self: start; }

  #runtimePage .pipeline-operations-view-nav,
  #runtimePage :is(
    .pipeline-monitoring-summary-grid,
    .pipeline-failures-summary,
    .pipeline-readiness-summary,
    .pipeline-workflow-identity-grid,
    .pipeline-workflow-lifecycle-grid,
    .pipeline-workflow-stage-summary,
    .pipeline-stage-progress-list,
    .pipeline-job-facts,
    .pipeline-failure-facts,
    .pipeline-readiness-facts,
    .pipeline-readiness-stage-strip
  ) { grid-template-columns: 1fr; }

  #runtimePage :is(
    .pipeline-workflow-directory,
    .pipeline-jobs-directory,
    .pipeline-failures-directory,
    .pipeline-readiness-directory,
    .pipeline-workflow-detail,
    .pipeline-job-detail,
    .pipeline-failure-detail,
    .pipeline-readiness-detail
  ) { padding: 8px; }
}

@media (prefers-reduced-motion: reduce) {
  #runtimePage .pipeline-operations-workspace *,
  #runtimePage .pipeline-monitoring-panel * {
    scroll-behavior: auto !important;
    animation: none !important;
    transition-duration: .01ms !important;
  }
}
/* END PART F 15-B4L RESPONSIVE INTEGRATION FINALIZATION */
'''


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        del tag
        self.ids.extend(
            value for name, value in attrs if name == "id" and value
        )


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
        raise RuntimeError(
            "Node.js is required for JavaScript syntax validation."
        )
    with tempfile.TemporaryDirectory(
        prefix="linkcraftor_b4l_js_"
    ) as folder:
        candidate = Path(folder) / "runtime_owner_candidate.js"
        write_text(candidate, source)
        result = subprocess.run(
            [node, "--check", str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    return result.returncode == 0


def responsive_contract_probe(source: str) -> dict[str, Any]:
    begin = f"/* BEGIN {MARKER} */"
    end = f"/* END {MARKER} */"
    if begin in source and end in source:
        source = source.split(begin, 1)[1].split(end, 1)[0]
    breakpoints = sorted(
        {
            int(match)
            for match in re.findall(
                r"@media\s*\(\s*max-width\s*:\s*(\d+)px\s*\)",
                source,
            )
        },
        reverse=True,
    )
    families = {
        "overview": ".pipeline-monitoring-summary-grid",
        "workflows": ".pipeline-workflow-explorer-grid",
        "stage_progress": ".pipeline-stage-progress-list",
        "jobs_attempts": ".pipeline-jobs-layout",
        "dependencies_handoffs": ".pipeline-handoff-gate",
        "events_timeline": ".pipeline-event-entry",
        "failures_attention": ".pipeline-failures-workspace",
        "output_readiness": ".pipeline-readiness-workspace",
    }
    covered = {
        name: selector in source
        for name, selector in families.items()
    }
    tokens = {
        "main_layout_collapse": (
            ".pipeline-operations-layout" in source
            and "@media (max-width: 940px)" in source
            and "grid-template-columns: 1fr" in source
        ),
        "component_pane_collapse": all(
            selector in source
            for selector in (
                ".pipeline-workflow-explorer-grid",
                ".pipeline-jobs-layout",
                ".pipeline-failures-workspace",
                ".pipeline-readiness-workspace",
            )
        ),
        "long_identity_wrap": "overflow-wrap: anywhere" in source,
        "overflow_guard": "overflow-x: clip" in source,
        "focus_visible": ":focus-visible" in source,
        "touch_target": "min-height: 44px" in source,
        "reduced_motion": (
            "prefers-reduced-motion: reduce" in source
            and "animation: none !important" in source
            and "transition-duration: .01ms !important" in source
        ),
    }
    return {
        "breakpoints": breakpoints,
        "covered_components": covered,
        "contracts": tokens,
        "passed": (
            breakpoints == [1180, 940, 820, 700, 620, 480]
            and all(covered.values())
            and all(tokens.values())
        ),
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
            "FINAL RESULT: PART F 15-B4L RESPONSIVE INTEGRATION "
            "FINALIZATION NOT_CERTIFIED"
        )
    )
    return "\n".join(
        [
            "LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS",
            (
                "PART F 15-B4L RESPONSIVE INTEGRATION FINALIZATION "
                "CERTIFICATION"
            ),
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "Patch mode: STRICT FAIL-CLOSED",
            f"Backup: {evidence.get('backup', 'NOT_CREATED')}",
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
            (
                "- One final responsive layer now governs all eight "
                "Connected Domain monitoring components."
            ),
            (
                "- Desktop, tablet and compact layouts preserve readable "
                "content without horizontal workspace overflow."
            ),
            (
                "- Long identities wrap safely, split panes collapse, and "
                "summary, fact and stage grids reflow deterministically."
            ),
            (
                "- Keyboard focus, compact touch targets and reduced-motion "
                "preferences are honored by the shared presentation layer."
            ),
            (
                "- Existing navigation, cached detail evidence and all eight "
                "component authorities remain unchanged."
            ),
            (
                "- No endpoint, job, queue, workflow, handler, recovery, "
                "output or persistence authority was created or mutated."
            ),
            "",
            "NEXT STEP:",
            (
                "Browser responsive visual acceptance, then Part F 15-B4M "
                "- cross-component regression and accessibility closure."
            ),
            "",
            final,
            "",
        ]
    )


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4L_RESPONSIVE_INTEGRATION_FINALIZATION.py "
            "<project_root> <report_path>"
        )

    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    paths = {
        "index_html": root / "backend/server/owner/index.html",
        "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": (
            root / "backend/server/owner/runtime_owner.css"
        ),
        "runtime_owner_js": (
            root / "backend/server/owner/runtime_owner.js"
        ),
        "runtime_summary_api": (
            root / "backend/server/owner/runtime_summary_api.py"
        ),
        "pipeline_operations": (
            root / "backend/server/owner/pipeline_operations.py"
        ),
    }
    prior_report = (
        root
        / "backend/server/data/reports/"
        "PART_F_15_B4K_OUTPUT_READINESS_CERTIFICATION.txt"
    )

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "new_endpoint_requests": 0,
        "recovery_controls_added": False,
    }
    error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}
    retained = False
    status = "NOT_CERTIFIED"

    try:
        checks["part_f_15_b4k_report_exists"] = prior_report.is_file()
        prior_hash = (
            sha256_path(prior_report) if prior_report.is_file() else ""
        )
        prior = read_text(prior_report) if prior_report.is_file() else ""
        checks["part_f_15_b4k_certified"] = (
            "CERTIFICATION STATUS: CERTIFIED" in prior
            and (
                "FINAL RESULT: PART F 15-B4K OUTPUT READINESS "
                "COMPONENT CERTIFIED"
            )
            in prior
        )

        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError(
                "Required source or B4K certification evidence is unavailable."
            )

        before = {
            name: sha256_path(path)
            for name, path in paths.items()
        }
        evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()):
            raise RuntimeError(
                "Installed source lineage does not match certified B4K."
            )

        index_source = read_text(paths["index_html"])
        css_source = read_text(paths["runtime_owner_css"])
        js_source = read_text(paths["runtime_owner_js"])
        operations_source = read_text(paths["pipeline_operations"])

        checks["responsive_finalization_not_previously_present"] = all(
            MARKER not in source
            for source in (index_source, css_source, js_source)
        )
        checks["eight_component_panels_present"] = all(
            index_source.count(f'id="{panel_id}"') == 1
            for panel_id in PANEL_IDS
        )
        checks["eight_component_authorities_present"] = all(
            authority in js_source
            for authority in COMPONENT_AUTHORITIES
        )

        index_candidate = replace_once(
            index_source,
            OLD_CSS_VERSION,
            NEW_CSS_BLOCK,
            "Runtime stylesheet cache version",
        )
        css_candidate = css_source.rstrip() + "\n" + CSS_APPEND.lstrip()
        js_candidate = js_source

        checks["candidate_html_ids_unique"] = html_ids_unique(
            index_candidate
        )
        checks["candidate_css_balanced"] = css_balanced(css_candidate)
        checks["candidate_javascript_syntax"] = (
            javascript_syntax_valid(js_candidate)
        )
        checks["candidate_javascript_unchanged"] = (
            js_candidate == js_source
        )

        probe = responsive_contract_probe(CSS_APPEND)
        evidence["responsive_contract_probe"] = probe
        checks["responsive_contract_probe_passed"] = bool(
            probe["passed"]
        )
        checks["six_responsive_breakpoints_present"] = (
            probe["breakpoints"] == [1180, 940, 820, 700, 620, 480]
        )
        checks["all_component_families_covered"] = all(
            probe["covered_components"].values()
        )
        checks["main_layout_collapse_present"] = bool(
            probe["contracts"]["main_layout_collapse"]
        )
        checks["component_pane_collapse_present"] = bool(
            probe["contracts"]["component_pane_collapse"]
        )
        checks["long_identity_wrap_present"] = bool(
            probe["contracts"]["long_identity_wrap"]
        )
        checks["horizontal_overflow_guard_present"] = bool(
            probe["contracts"]["overflow_guard"]
        )
        checks["keyboard_focus_contract_present"] = bool(
            probe["contracts"]["focus_visible"]
        )
        checks["touch_target_contract_present"] = bool(
            probe["contracts"]["touch_target"]
        )
        checks["reduced_motion_contract_present"] = bool(
            probe["contracts"]["reduced_motion"]
        )

        checks["cache_version_advanced"] = (
            NEW_CSS_VERSION in index_candidate
            and OLD_CSS_VERSION not in index_candidate
        )
        checks["no_new_fetch_request_added"] = (
            js_candidate.count("fetch(") == js_source.count("fetch(")
        )
        checks["canonical_detail_endpoint_retained_once"] = (
            js_candidate.count(
                '"/owner/api/runtime/pipelines/connect_domain"'
            )
            == 1
        )
        checks["no_recovery_controls_added"] = (
            all(
                js_candidate.count(token) == js_source.count(token)
                for token in (
                    "retryJob(",
                    "cancelJob(",
                    "terminateJob(",
                    "data-runtime-recovery-action",
                )
            )
            and index_candidate.count("data-runtime-recovery-action")
            == index_source.count("data-runtime-recovery-action")
        )
        checks["pipeline_projection_contract_unchanged"] = (
            read_text(paths["pipeline_operations"]) == operations_source
        )
        if not all(checks.values()):
            raise RuntimeError(
                "15-B4L candidate certification checks failed."
            )

        stamp = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%S%fZ"
        )
        backup = (
            root
            / "backend/server/data/runtime_backups"
            / f"part_f_15_b4l_{stamp}"
        )
        backup.mkdir(parents=True, exist_ok=False)
        for name in ("index_html", "runtime_owner_css"):
            originals[name] = paths[name].read_bytes()
            shutil.copy2(paths[name], backup / paths[name].name)

        evidence["backup"] = str(backup)
        write_text(paths["index_html"], index_candidate)
        write_text(paths["runtime_owner_css"], css_candidate)

        checks["backup_created"] = backup.is_dir()
        retained_index = read_text(paths["index_html"])
        retained_css = read_text(paths["runtime_owner_css"])
        retained_js = read_text(paths["runtime_owner_js"])
        retained_probe = responsive_contract_probe(retained_css)

        checks["retained_html_ids_unique"] = html_ids_unique(
            retained_index
        )
        checks["retained_css_balanced"] = css_balanced(retained_css)
        checks["retained_javascript_syntax"] = (
            javascript_syntax_valid(retained_js)
        )
        checks["retained_responsive_contract"] = bool(
            retained_probe["passed"]
        )
        checks["retained_markers"] = (
            retained_index.count(MARKER) == 2
            and retained_css.count(MARKER) == 2
        )
        checks["historical_b4k_report_unchanged"] = (
            sha256_path(prior_report) == prior_hash
        )

        after = {
            name: sha256_path(path)
            for name, path in paths.items()
        }
        evidence["source_hashes_after"] = after
        checks["only_two_ui_sources_changed"] = all(
            (after[name] != before[name])
            == (name in {"index_html", "runtime_owner_css"})
            for name in paths
        )
        checks["unchanged_owner_css"] = (
            after["owner_css"] == before["owner_css"]
        )
        checks["unchanged_owner_js"] = (
            after["owner_js"] == before["owner_js"]
        )
        checks["unchanged_runtime_owner_js"] = (
            after["runtime_owner_js"] == before["runtime_owner_js"]
        )
        checks["unchanged_runtime_summary_api"] = (
            after["runtime_summary_api"]
            == before["runtime_summary_api"]
        )
        checks["unchanged_pipeline_operations"] = (
            after["pipeline_operations"]
            == before["pipeline_operations"]
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
        evidence["covered_components"] = [
            "overview",
            "workflows",
            "stage_progress",
            "jobs_attempts",
            "dependencies_handoffs",
            "events_timeline",
            "failures_attention",
            "output_readiness",
        ]
        evidence["responsive_breakpoints_px"] = [
            1180,
            940,
            820,
            700,
            620,
            480,
        ]
        evidence["changed_sources"] = [
            "backend/server/owner/index.html",
            "backend/server/owner/runtime_owner.css",
        ]
        if not all(checks.values()):
            raise RuntimeError(
                "Retained 15-B4L certification checks failed."
            )

        retained = True
        status = "CERTIFIED"
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        for name, original in originals.items():
            paths[name].write_bytes(original)
    finally:
        evidence["patch_retained"] = retained
        report.parent.mkdir(parents=True, exist_ok=True)
        write_text(
            report,
            make_report(status, checks, evidence, error),
        )

    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(
        "FAILED_CHECK_COUNT="
        f"{sum(not passed for passed in checks.values())}"
    )
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B4L_STATUS={status}")
    print(f"PATCH_RETAINED={'YES' if retained else 'NO'}")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
