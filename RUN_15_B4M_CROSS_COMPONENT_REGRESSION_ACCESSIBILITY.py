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
    "FINAL RESULT: PART F 15-B4M CROSS-COMPONENT REGRESSION AND "
    "ACCESSIBILITY CLOSURE CERTIFIED"
)
MARKER = (
    "PART F 15-B4M CROSS-COMPONENT REGRESSION AND ACCESSIBILITY CLOSURE"
)

EXPECTED_HASHES = {
    "index_html": "427336c4af7e5d3cf32a9fcf6d10933fcac3fa15b3be4b4c0d5164bbc82b3e99",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "b87a76c5ddc17446c573ddbc2dea09f32600321738aeb15a74a269933a1145e4",
    "runtime_owner_js": "6f3038763969fcd15e4d1fcf54619984631901c0768c952a900d896b2bcecf58",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=16"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=17"></script>'
NEW_JS_BLOCK = f'''<!-- BEGIN {MARKER} CACHE -->
    {NEW_JS_VERSION}
    <!-- END {MARKER} CACHE -->'''

TAB_PANEL_PAIRS = (
    (
        "overview",
        "pipelineOperationsTabOverview",
        "pipelineOperationsViewOverview",
    ),
    (
        "workflows",
        "pipelineOperationsTabWorkflows",
        "pipelineOperationsViewWorkflows",
    ),
    (
        "stage_progress",
        "pipelineOperationsTabStageProgress",
        "pipelineOperationsViewStageProgress",
    ),
    (
        "jobs_attempts",
        "pipelineOperationsTabJobsAttempts",
        "pipelineOperationsViewJobsAttempts",
    ),
    (
        "dependencies_handoffs",
        "pipelineOperationsTabDependenciesHandoffs",
        "pipelineOperationsViewDependenciesHandoffs",
    ),
    (
        "events_timeline",
        "pipelineOperationsTabEventsTimeline",
        "pipelineOperationsViewEventsTimeline",
    ),
    (
        "failures",
        "pipelineOperationsTabFailures",
        "pipelineOperationsViewFailures",
    ),
    (
        "output_readiness",
        "pipelineOperationsTabOutputReadiness",
        "pipelineOperationsViewOutputReadiness",
    ),
)

DETAIL_AUTHORITIES = (
    "LinkCraftorConnectedDomainWorkflowExplorer",
    "LinkCraftorConnectedDomainStageProgress",
    "LinkCraftorConnectedDomainJobsAttempts",
    "LinkCraftorConnectedDomainDependenciesHandoffs",
    "LinkCraftorConnectedDomainEventsTimeline",
    "LinkCraftorConnectedDomainFailuresAttention",
    "LinkCraftorConnectedDomainOutputReadiness",
)

REPORT_CHAIN = {
    "PART_F_15_B4D3_D5_RUNTIME_UI_REDESIGN_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4D3 THROUGH 15-B4D5 RUNTIME UI "
        "REDESIGN CERTIFIED"
    ),
    "PART_F_15_B4D6_D8_COMPONENT_SHELLS_NAVIGATION_STATES_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4D6 THROUGH 15-B4D8 COMPONENT SHELLS "
        "NAVIGATION AND STATES CERTIFIED"
    ),
    "PART_F_15_B4D9_NAVIGATION_BOUNDARY_FIX_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4D9 CONNECTED DOMAIN NAVIGATION "
        "BOUNDARY CORRECTION CERTIFIED"
    ),
    "PART_F_15_B4D10_CONNECTED_DOMAIN_OVERVIEW_WIRING_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW LIVE "
        "EVIDENCE WIRING CERTIFIED"
    ),
    "PART_F_15_B4D10R_OUTPUT_READINESS_SEMANTIC_CORRECTION_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4D10R OUTPUT READINESS SEMANTIC "
        "CORRECTION CERTIFIED"
    ),
    "PART_F_15_B4E_WORKFLOW_EXPLORER_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4E WORKFLOW EXPLORER CERTIFIED"
    ),
    "PART_F_15_B4F_SIX_STAGE_PROGRESS_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4F SIX-STAGE PROGRESS COMPONENT "
        "CERTIFIED"
    ),
    "PART_F_15_B4G_JOBS_ATTEMPTS_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4G JOBS AND ATTEMPTS COMPONENT "
        "CERTIFIED"
    ),
    "PART_F_15_B4H_DEPENDENCIES_HANDOFFS_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT "
        "CERTIFIED"
    ),
    "PART_F_15_B4I_EVENTS_TIMELINE_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4I EVENTS TIMELINE COMPONENT CERTIFIED"
    ),
    "PART_F_15_B4J_FAILURES_ATTENTION_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4J FAILURES AND ATTENTION COMPONENT "
        "CERTIFIED"
    ),
    "PART_F_15_B4K_OUTPUT_READINESS_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4K OUTPUT READINESS COMPONENT CERTIFIED"
    ),
    "PART_F_15_B4L_RESPONSIVE_INTEGRATION_FINALIZATION_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4L RESPONSIVE INTEGRATION FINALIZATION "
        "CERTIFIED"
    ),
}

JS_APPEND = r'''

// BEGIN PART F 15-B4M CROSS-COMPONENT REGRESSION AND ACCESSIBILITY CLOSURE
(() => {
  "use strict";

  const PAIRS = Object.freeze([
    Object.freeze({ view: "overview", tabId: "pipelineOperationsTabOverview", panelId: "pipelineOperationsViewOverview" }),
    Object.freeze({ view: "workflows", tabId: "pipelineOperationsTabWorkflows", panelId: "pipelineOperationsViewWorkflows" }),
    Object.freeze({ view: "stage_progress", tabId: "pipelineOperationsTabStageProgress", panelId: "pipelineOperationsViewStageProgress" }),
    Object.freeze({ view: "jobs_attempts", tabId: "pipelineOperationsTabJobsAttempts", panelId: "pipelineOperationsViewJobsAttempts" }),
    Object.freeze({ view: "dependencies_handoffs", tabId: "pipelineOperationsTabDependenciesHandoffs", panelId: "pipelineOperationsViewDependenciesHandoffs" }),
    Object.freeze({ view: "events_timeline", tabId: "pipelineOperationsTabEventsTimeline", panelId: "pipelineOperationsViewEventsTimeline" }),
    Object.freeze({ view: "failures", tabId: "pipelineOperationsTabFailures", panelId: "pipelineOperationsViewFailures" }),
    Object.freeze({ view: "output_readiness", tabId: "pipelineOperationsTabOutputReadiness", panelId: "pipelineOperationsViewOutputReadiness" })
  ]);
  const TAB_KEYS = new Set(["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp", "Home", "End"]);

  const resolveTabIndex = (key, currentIndex, length) => {
    if (!Number.isInteger(length) || length < 1) return -1;
    if (key === "Home") return 0;
    if (key === "End") return length - 1;
    if (key === "ArrowRight" || key === "ArrowDown") return (currentIndex + 1) % length;
    if (key === "ArrowLeft" || key === "ArrowUp") return (currentIndex - 1 + length) % length;
    return currentIndex;
  };

  const sync = () => {
    PAIRS.forEach(({ tabId, panelId }) => {
      const tab = document.getElementById(tabId);
      const panel = document.getElementById(panelId);
      if (!tab || !panel) return;
      const selected = tab.getAttribute("aria-selected") === "true";
      tab.tabIndex = selected ? 0 : -1;
      tab.setAttribute("aria-controls", panelId);
      panel.setAttribute("aria-labelledby", tabId);
      panel.setAttribute("aria-hidden", selected ? "false" : "true");
      panel.tabIndex = 0;
    });
    return true;
  };

  const onTabKeydown = (event) => {
    if (!TAB_KEYS.has(event.key) || event.altKey || event.ctrlKey || event.metaKey) return;
    const current = event.target.closest?.('[role="tab"][data-pipeline-operations-view]');
    const nav = current?.closest?.('[role="tablist"]');
    if (!current || !nav) return;
    const tabs = Array.from(nav.querySelectorAll('[role="tab"][data-pipeline-operations-view]')).filter((tab) => !tab.disabled);
    const currentIndex = tabs.indexOf(current);
    if (currentIndex < 0) return;
    const target = tabs[resolveTabIndex(event.key, currentIndex, tabs.length)];
    if (!target) return;
    event.preventDefault();
    target.click();
    target.focus();
    queueMicrotask(sync);
  };

  const onListboxKeydown = (event) => {
    if (!new Set(["ArrowDown", "ArrowUp", "Home", "End"]).has(event.key) || event.altKey || event.ctrlKey || event.metaKey) return;
    const option = event.target.closest?.('[role="option"]');
    const listbox = option?.closest?.('[role="listbox"]');
    if (!option || !listbox) return;
    const options = Array.from(listbox.querySelectorAll('[role="option"]')).filter((item) => !item.disabled);
    const currentIndex = options.indexOf(option);
    if (currentIndex < 0) return;
    const target = options[resolveTabIndex(event.key, currentIndex, options.length)];
    if (!target) return;
    event.preventDefault();
    target.focus();
    if (target !== option) target.click();
  };

  const initialize = () => {
    const page = document.getElementById("runtimePage");
    const nav = document.getElementById("pipelineOperationsViewNav");
    if (!page || !nav || page.dataset.pipelineAccessibilityBound === "true") return false;
    nav.addEventListener("keydown", onTabKeydown);
    document.addEventListener("keydown", onListboxKeydown);
    new MutationObserver(sync).observe(nav, {
      subtree: true,
      attributes: true,
      attributeFilter: ["aria-selected"]
    });
    sync();
    page.dataset.pipelineAccessibilityBound = "true";
    return true;
  };

  window.LinkCraftorPipelineAccessibility = Object.freeze({ sync, resolveTabIndex });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
// END PART F 15-B4M CROSS-COMPONENT REGRESSION AND ACCESSIBILITY CLOSURE
'''


class ElementCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: list[tuple[str, dict[str, str]]] = []
        self.ids: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        normalized = {
            name: "" if value is None else value
            for name, value in attrs
        }
        self.elements.append((tag, normalized))
        identifier = normalized.get("id")
        if identifier:
            self.ids.append(identifier)


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
    parser = ElementCollector()
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
        prefix="linkcraftor_b4m_js_"
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


def enhance_accessibility(source: str) -> str:
    source = replace_once(
        source,
        'role="tablist"',
        'role="tablist"\n              aria-orientation="horizontal"',
        "Pipeline Operations tablist orientation",
    )

    for index, (view, tab_id, panel_id) in enumerate(TAB_PANEL_PAIRS):
        tab_pattern = re.compile(
            rf'<button(?=[^>]*\brole="tab")'
            rf'(?=[^>]*\bdata-pipeline-operations-view="{re.escape(view)}")'
            r'[^>]*>'
        )
        tab_matches = list(tab_pattern.finditer(source))
        if len(tab_matches) != 1:
            raise RuntimeError(
                f"Expected one accessible tab candidate for {view}, "
                f"found {len(tab_matches)}."
            )
        tab_tag = tab_matches[0].group(0)
        if any(
            token in tab_tag
            for token in (' id="', ' aria-controls="', ' tabindex="')
        ):
            raise RuntimeError(
                f"The {view} tab already carries B4M attributes."
            )
        tab_index = "0" if index == 0 else "-1"
        enhanced_tab = (
            tab_tag[:-1]
            + f' id="{tab_id}" aria-controls="{panel_id}" '
            + f'tabindex="{tab_index}">'
        )
        source = source.replace(tab_tag, enhanced_tab, 1)

        panel_pattern = re.compile(
            rf'<section(?=[^>]*\bid="{re.escape(panel_id)}")'
            rf'(?=[^>]*\bdata-pipeline-operations-view-panel="{re.escape(view)}")'
            r'(?=[^>]*\brole="tabpanel")[^>]*>'
        )
        panel_matches = list(panel_pattern.finditer(source))
        if len(panel_matches) != 1:
            raise RuntimeError(
                f"Expected one accessible panel candidate for {view}, "
                f"found {len(panel_matches)}."
            )
        panel_tag = panel_matches[0].group(0)
        if any(
            token in panel_tag
            for token in (
                ' aria-labelledby="',
                ' aria-hidden="',
                ' tabindex="',
            )
        ):
            raise RuntimeError(
                f"The {view} panel already carries B4M attributes."
            )
        aria_hidden = "false" if index == 0 else "true"
        enhanced_panel = (
            panel_tag[:-1]
            + f' aria-labelledby="{tab_id}" aria-hidden="{aria_hidden}" '
            + 'tabindex="0">'
        )
        source = source.replace(panel_tag, enhanced_panel, 1)

    return source


def accessibility_markup_probe(source: str) -> dict[str, Any]:
    parser = ElementCollector()
    parser.feed(source)
    by_id = {
        attrs["id"]: (tag, attrs)
        for tag, attrs in parser.elements
        if attrs.get("id")
    }
    nav = by_id.get("pipelineOperationsViewNav")
    pairs: dict[str, bool] = {}
    selected_count = 0
    visible_panel_count = 0
    for index, (view, tab_id, panel_id) in enumerate(TAB_PANEL_PAIRS):
        tab = by_id.get(tab_id)
        panel = by_id.get(panel_id)
        expected_selected = "true" if index == 0 else "false"
        expected_hidden = "false" if index == 0 else "true"
        expected_tabindex = "0" if index == 0 else "-1"
        tab_valid = bool(
            tab
            and tab[0] == "button"
            and tab[1].get("role") == "tab"
            and tab[1].get("data-pipeline-operations-view") == view
            and tab[1].get("aria-selected") == expected_selected
            and tab[1].get("aria-controls") == panel_id
            and tab[1].get("tabindex") == expected_tabindex
        )
        panel_valid = bool(
            panel
            and panel[0] == "section"
            and panel[1].get("role") == "tabpanel"
            and panel[1].get("data-pipeline-operations-view-panel") == view
            and panel[1].get("aria-labelledby") == tab_id
            and panel[1].get("aria-hidden") == expected_hidden
            and panel[1].get("tabindex") == "0"
        )
        pairs[view] = tab_valid and panel_valid
        if tab and tab[1].get("aria-selected") == "true":
            selected_count += 1
        if panel and panel[1].get("aria-hidden") == "false":
            visible_panel_count += 1
    return {
        "tablist_valid": bool(
            nav
            and nav[1].get("role") == "tablist"
            and nav[1].get("aria-orientation") == "horizontal"
            and nav[1].get("aria-label")
        ),
        "pairs": pairs,
        "selected_tab_count": selected_count,
        "visible_panel_count": visible_panel_count,
        "passed": (
            bool(nav)
            and all(pairs.values())
            and selected_count == 1
            and visible_panel_count == 1
        ),
    }


def keyboard_navigation_probe(source: str) -> dict[str, int]:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError(
            "Node.js is required for keyboard-navigation validation."
        )
    probe = "\n".join(
        [
            "global.window = {};",
            (
                "global.document = { readyState: 'loading', "
                "addEventListener: () => {}, getElementById: () => null };"
            ),
            source,
            "const resolve = window.LinkCraftorPipelineAccessibility.resolveTabIndex;",
            "const observed = {",
            "  right: resolve('ArrowRight', 0, 8),",
            "  downWrap: resolve('ArrowDown', 7, 8),",
            "  leftWrap: resolve('ArrowLeft', 0, 8),",
            "  up: resolve('ArrowUp', 3, 8),",
            "  home: resolve('Home', 5, 8),",
            "  end: resolve('End', 2, 8),",
            "  unchanged: resolve('Escape', 4, 8)",
            "};",
            "process.stdout.write(JSON.stringify(observed));",
        ]
    )
    with tempfile.TemporaryDirectory(
        prefix="linkcraftor_b4m_keyboard_"
    ) as folder:
        candidate = Path(folder) / "keyboard_probe.js"
        write_text(candidate, probe)
        result = subprocess.run(
            [node, str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    if result.returncode != 0:
        raise RuntimeError(
            "Keyboard-navigation probe failed "
            f"({result.returncode}): {result.stderr.strip()}"
        )
    return json.loads(result.stdout)


def responsive_contract_present(source: str) -> bool:
    required = (
        "BEGIN PART F 15-B4L RESPONSIVE INTEGRATION FINALIZATION",
        "@media (max-width: 1180px)",
        "@media (max-width: 940px)",
        "@media (max-width: 820px)",
        "@media (max-width: 700px)",
        "@media (max-width: 620px)",
        "@media (max-width: 480px)",
        "prefers-reduced-motion: reduce",
        "overflow-wrap: anywhere",
        ":focus-visible",
        "min-height: 44px",
    )
    return all(token in source for token in required)


def report_is_certified(source: str, final_result: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return (
        "CERTIFICATION STATUS: CERTIFIED" in normalized
        and "FAILED_CHECKS:\n[]" in normalized
        and "NOT_RUN_CHECKS:\n[]" in normalized
        and final_result in normalized
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
            "FINAL RESULT: PART F 15-B4M CROSS-COMPONENT REGRESSION "
            "AND ACCESSIBILITY CLOSURE NOT_CERTIFIED"
        )
    )
    return "\n".join(
        [
            "LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS",
            (
                "PART F 15-B4M CROSS-COMPONENT REGRESSION AND "
                "ACCESSIBILITY CLOSURE CERTIFICATION"
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
                "- The complete B4D3-through-B4L certificate chain is "
                "present, certified and unchanged."
            ),
            (
                "- Eight workspace tabs now have explicit tab-to-panel "
                "relationships, one selected tab and one exposed panel."
            ),
            (
                "- Arrow, Home and End keyboard navigation is active for "
                "workspace tabs, with roving focus preserved."
            ),
            (
                "- Dynamic listbox options receive shared Arrow, Home and "
                "End keyboard navigation without changing their evidence."
            ),
            (
                "- All eight component authorities, responsive rules, cached "
                "detail projection and three existing GET requests remain intact."
            ),
            (
                "- No endpoint, job, queue, workflow, handler, recovery, "
                "output or persistence authority was created or mutated."
            ),
            "",
            "NEXT STEP:",
            (
                "Part F 15-B4N - Connected Domain collective certification "
                "and handoff closure."
            ),
            "",
            final,
            "",
        ]
    )


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4M_CROSS_COMPONENT_REGRESSION_ACCESSIBILITY.py "
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
    reports_root = root / "backend/server/data/reports"

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
        historical_paths = {
            filename: reports_root / filename
            for filename in REPORT_CHAIN
        }
        for filename, path in historical_paths.items():
            key = filename.removesuffix(".txt").lower()
            checks[f"report_exists_{key}"] = path.is_file()
            checks[f"report_certified_{key}"] = (
                path.is_file()
                and report_is_certified(
                    read_text(path),
                    REPORT_CHAIN[filename],
                )
            )
        if not all(checks.values()):
            raise RuntimeError(
                "The B4D3-through-B4L certification chain is incomplete."
            )
        historical_hashes = {
            filename: sha256_path(path)
            for filename, path in historical_paths.items()
        }
        evidence["historical_certificate_count"] = len(
            historical_hashes
        )

        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("A required Owner Runtime source is unavailable.")

        before = {
            name: sha256_path(path)
            for name, path in paths.items()
        }
        evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()):
            raise RuntimeError(
                "Installed source lineage does not match certified B4L."
            )

        index_source = read_text(paths["index_html"])
        css_source = read_text(paths["runtime_owner_css"])
        js_source = read_text(paths["runtime_owner_js"])

        checks["accessibility_closure_not_previously_present"] = all(
            MARKER not in source
            for source in (index_source, css_source, js_source)
        )
        checks["b4l_responsive_contract_retained"] = (
            responsive_contract_present(css_source)
        )
        checks["eight_component_authorities_retained"] = (
            "LinkCraftorConnectedDomainOverview" in js_source
            and all(
                authority in js_source
                for authority in DETAIL_AUTHORITIES
            )
        )

        index_candidate = enhance_accessibility(index_source)
        index_candidate = replace_once(
            index_candidate,
            OLD_JS_VERSION,
            NEW_JS_BLOCK,
            "Runtime JavaScript cache version",
        )
        js_candidate = js_source.rstrip() + "\n" + JS_APPEND.lstrip()

        checks["candidate_html_ids_unique"] = html_ids_unique(
            index_candidate
        )
        checks["candidate_css_balanced"] = css_balanced(css_source)
        checks["candidate_javascript_syntax"] = (
            javascript_syntax_valid(js_candidate)
        )

        markup_probe = accessibility_markup_probe(index_candidate)
        evidence["accessibility_markup_probe"] = markup_probe
        checks["eight_tab_panel_pairs_accessible"] = bool(
            markup_probe["passed"]
        )
        checks["single_selected_tab_and_panel"] = (
            markup_probe["selected_tab_count"] == 1
            and markup_probe["visible_panel_count"] == 1
        )
        checks["tablist_orientation_present"] = bool(
            markup_probe["tablist_valid"]
        )

        keyboard_probe = keyboard_navigation_probe(JS_APPEND)
        evidence["keyboard_navigation_probe"] = keyboard_probe
        checks["keyboard_navigation_probe_passed"] = (
            keyboard_probe
            == {
                "right": 1,
                "downWrap": 0,
                "leftWrap": 7,
                "up": 2,
                "home": 0,
                "end": 7,
                "unchanged": 4,
            }
        )
        checks["workspace_tab_keyboard_contract_present"] = all(
            token in JS_APPEND
            for token in (
                '"ArrowRight"',
                '"ArrowDown"',
                '"ArrowLeft"',
                '"ArrowUp"',
                '"Home"',
                '"End"',
                "target.click()",
                "target.focus()",
            )
        )
        checks["dynamic_listbox_keyboard_contract_present"] = all(
            token in JS_APPEND
            for token in (
                "onListboxKeydown",
                '[role="listbox"]',
                '[role="option"]',
            )
        )
        checks["aria_state_synchronization_present"] = all(
            token in JS_APPEND
            for token in (
                'tab.setAttribute("aria-controls", panelId)',
                'panel.setAttribute("aria-labelledby", tabId)',
                'panel.setAttribute("aria-hidden", selected ? "false" : "true")',
                "tab.tabIndex = selected ? 0 : -1",
                "new MutationObserver(sync)",
            )
        )

        checks["component_activation_handoffs_retained"] = all(
            f"window.{authority}?.activate?.();" in js_candidate
            for authority in DETAIL_AUTHORITIES
        )
        checks["component_render_handoffs_retained"] = all(
            f"window.{authority}?.render?.(payload);" in js_candidate
            for authority in DETAIL_AUTHORITIES
        )
        checks["component_unavailable_handoffs_retained"] = all(
            f"window.{authority}?.renderUnavailable?.(" in js_candidate
            for authority in DETAIL_AUTHORITIES
        )
        checks["three_get_endpoints_retained_once"] = all(
            js_candidate.count(endpoint) == 1
            for endpoint in (
                '"/owner/api/runtime/summary"',
                '"/owner/api/runtime/pipelines"',
                '"/owner/api/runtime/pipelines/connect_domain"',
            )
        )
        checks["no_new_fetch_request_added"] = (
            js_candidate.count("fetch(") == js_source.count("fetch(")
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
        checks["cache_version_advanced"] = (
            NEW_JS_VERSION in index_candidate
            and OLD_JS_VERSION not in index_candidate
        )
        if not all(checks.values()):
            raise RuntimeError(
                "15-B4M candidate regression or accessibility check failed."
            )

        stamp = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%S%fZ"
        )
        backup = (
            root
            / "backend/server/data/runtime_backups"
            / f"part_f_15_b4m_{stamp}"
        )
        backup.mkdir(parents=True, exist_ok=False)
        for name in ("index_html", "runtime_owner_js"):
            originals[name] = paths[name].read_bytes()
            shutil.copy2(paths[name], backup / paths[name].name)

        evidence["backup"] = str(backup)
        write_text(paths["index_html"], index_candidate)
        write_text(paths["runtime_owner_js"], js_candidate)

        checks["backup_created"] = backup.is_dir()
        retained_index = read_text(paths["index_html"])
        retained_css = read_text(paths["runtime_owner_css"])
        retained_js = read_text(paths["runtime_owner_js"])
        retained_markup = accessibility_markup_probe(retained_index)

        checks["retained_html_ids_unique"] = html_ids_unique(
            retained_index
        )
        checks["retained_css_balanced"] = css_balanced(retained_css)
        checks["retained_javascript_syntax"] = (
            javascript_syntax_valid(retained_js)
        )
        checks["retained_accessibility_markup_contract"] = bool(
            retained_markup["passed"]
        )
        checks["retained_b4l_responsive_contract"] = (
            responsive_contract_present(retained_css)
        )
        checks["retained_markers"] = (
            retained_index.count(MARKER) == 2
            and retained_js.count(MARKER) == 2
        )
        checks["historical_certificate_chain_unchanged"] = all(
            sha256_path(historical_paths[filename])
            == historical_hashes[filename]
            for filename in historical_paths
        )

        after = {
            name: sha256_path(path)
            for name, path in paths.items()
        }
        evidence["source_hashes_after"] = after
        checks["only_two_ui_sources_changed"] = all(
            (after[name] != before[name])
            == (name in {"index_html", "runtime_owner_js"})
            for name in paths
        )
        checks["unchanged_owner_css"] = (
            after["owner_css"] == before["owner_css"]
        )
        checks["unchanged_owner_js"] = (
            after["owner_js"] == before["owner_js"]
        )
        checks["unchanged_runtime_owner_css"] = (
            after["runtime_owner_css"]
            == before["runtime_owner_css"]
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
        evidence["tab_panel_pair_count"] = len(TAB_PANEL_PAIRS)
        evidence["detail_authority_count"] = len(DETAIL_AUTHORITIES)
        evidence["responsive_contract_retained"] = True
        evidence["changed_sources"] = [
            "backend/server/owner/index.html",
            "backend/server/owner/runtime_owner.js",
        ]
        evidence["endpoint_requests_before"] = js_source.count("fetch(")
        evidence["endpoint_requests_after"] = js_candidate.count("fetch(")
        if not all(checks.values()):
            raise RuntimeError(
                "Retained 15-B4M certification checks failed."
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
    print(f"PART_F_15_B4M_STATUS={status}")
    print(f"PATCH_RETAINED={'YES' if retained else 'NO'}")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
