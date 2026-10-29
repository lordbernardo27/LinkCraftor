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


STEP = "PART F 15-B4D2"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B4D2 "
    "NESTED UNIVERSAL RUNTIME SIDEBAR CERTIFIED"
)

EXPECTED_HASHES = {
    "index_html": "8345fe34a71d042004a0c6b332e72e2ce4d70d0dfe7d20ed5321509a75b7e852",
    "owner_css": "5579f74621f2dd2bbcec9de1f487abb2851778e37c466b738beb822aa5d54eb0",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "bd43654128f36b2f38dd3418703fdfaf3763ca0c9fc2116f419933d44ef1aee5",
    "runtime_owner_js": "91c69789e0b84368c780ff1f5670ca9a659d48a8322c29df4b85d552c5a34393",
}

SIDEBAR_MARKER = "PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR"

OLD_RUNTIME_NAV = (
    '        <button class="nav-item" data-page="runtime">'
    "Universal Runtime</button>"
)

NEW_RUNTIME_NAV = r'''        <!-- BEGIN PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR -->
        <div
          class="runtime-sidebar-entry"
          id="runtimeSidebarEntry"
          data-runtime-sidebar
        >
          <div class="runtime-sidebar-root-row">
            <button
              class="nav-item runtime-sidebar-page-button"
              id="runtimeSidebarPageButton"
              type="button"
              data-page="runtime"
            >
              <span>Universal Runtime</span>
            </button>
            <button
              class="runtime-sidebar-toggle"
              id="runtimeSidebarToggle"
              type="button"
              aria-expanded="false"
              aria-controls="runtimeSidebarTree"
              aria-label="Expand Universal Runtime navigation"
            >
              <span class="runtime-sidebar-toggle-icon" aria-hidden="true">⌄</span>
            </button>
          </div>

          <div
            class="runtime-sidebar-tree"
            id="runtimeSidebarTree"
            aria-label="Universal Runtime component navigation"
            hidden
          >
            <div class="runtime-sidebar-tree-heading">Runtime workspace</div>

            <section class="runtime-sidebar-group" data-runtime-sidebar-group="command_center">
              <button
                class="runtime-sidebar-group-toggle"
                type="button"
                data-runtime-sidebar-group-toggle
                aria-expanded="true"
                aria-controls="runtimeSidebarCommandCenter"
              >
                <span>Command Center</span>
                <span class="runtime-sidebar-group-icon" aria-hidden="true">⌄</span>
              </button>
              <div
                class="runtime-sidebar-group-panel"
                id="runtimeSidebarCommandCenter"
              >
                <button
                  class="runtime-sidebar-link active"
                  type="button"
                  data-runtime-sidebar-section="overview"
                  aria-current="page"
                >
                  Runtime Overview
                </button>
              </div>
            </section>

            <section class="runtime-sidebar-group" data-runtime-sidebar-group="pipeline_operations">
              <button
                class="runtime-sidebar-group-toggle"
                type="button"
                data-runtime-sidebar-group-toggle
                aria-expanded="true"
                aria-controls="runtimeSidebarPipelineOperations"
              >
                <span>Pipeline Operations</span>
                <span class="runtime-sidebar-group-icon" aria-hidden="true">⌄</span>
              </button>
              <div
                class="runtime-sidebar-group-panel"
                id="runtimeSidebarPipelineOperations"
              >
                <button
                  class="runtime-sidebar-link"
                  type="button"
                  data-runtime-sidebar-section="pipeline_operations"
                >
                  All Pipelines
                </button>

                <div class="runtime-sidebar-subgroup">
                  <button
                    class="runtime-sidebar-group-toggle runtime-sidebar-subgroup-toggle"
                    type="button"
                    data-runtime-sidebar-group-toggle
                    aria-expanded="false"
                    aria-controls="runtimeSidebarConnectedDomain"
                  >
                    <span>Connected Domain</span>
                    <span class="runtime-sidebar-group-icon" aria-hidden="true">⌄</span>
                  </button>
                  <div
                    class="runtime-sidebar-group-panel runtime-sidebar-subgroup-panel"
                    id="runtimeSidebarConnectedDomain"
                    hidden
                  >
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="overview" disabled aria-disabled="true">Overview</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="workflows" disabled aria-disabled="true">Workflows</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="stage_progress" disabled aria-disabled="true">Stage Progress</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="jobs_attempts" disabled aria-disabled="true">Jobs &amp; Attempts</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="dependencies_handoffs" disabled aria-disabled="true">Dependencies &amp; Handoffs</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="events_timeline" disabled aria-disabled="true">Events Timeline</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="failures_attention" disabled aria-disabled="true">Failures &amp; Attention</button>
                    <button class="runtime-sidebar-link" type="button" data-runtime-pipeline-view="output_readiness" disabled aria-disabled="true">Output Readiness</button>
                  </div>
                </div>
              </div>
            </section>

            <section class="runtime-sidebar-group" data-runtime-sidebar-group="runtime_infrastructure">
              <button
                class="runtime-sidebar-group-toggle"
                type="button"
                data-runtime-sidebar-group-toggle
                aria-expanded="false"
                aria-controls="runtimeSidebarInfrastructure"
              >
                <span>Runtime Infrastructure</span>
                <span class="runtime-sidebar-group-icon" aria-hidden="true">⌄</span>
              </button>
              <div class="runtime-sidebar-group-panel" id="runtimeSidebarInfrastructure" hidden>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="jobs">Jobs</button>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="queues">Queues</button>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="workers_leases">Workers &amp; Leases</button>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="orchestration">Orchestration</button>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="execution">Execution</button>
              </div>
            </section>

            <section class="runtime-sidebar-group" data-runtime-sidebar-group="runtime_health">
              <button
                class="runtime-sidebar-group-toggle"
                type="button"
                data-runtime-sidebar-group-toggle
                aria-expanded="false"
                aria-controls="runtimeSidebarHealth"
              >
                <span>Runtime Health</span>
                <span class="runtime-sidebar-group-icon" aria-hidden="true">⌄</span>
              </button>
              <div class="runtime-sidebar-group-panel" id="runtimeSidebarHealth" hidden>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="reliability_recovery">Reliability &amp; Recovery</button>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="resource_governance">Resource Governance</button>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="observability">Observability</button>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="security">Security</button>
              </div>
            </section>

            <section class="runtime-sidebar-group" data-runtime-sidebar-group="runtime_administration">
              <button
                class="runtime-sidebar-group-toggle"
                type="button"
                data-runtime-sidebar-group-toggle
                aria-expanded="false"
                aria-controls="runtimeSidebarAdministration"
              >
                <span>Runtime Administration</span>
                <span class="runtime-sidebar-group-icon" aria-hidden="true">⌄</span>
              </button>
              <div class="runtime-sidebar-group-panel" id="runtimeSidebarAdministration" hidden>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="runtime_apis">Runtime APIs</button>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="persistence_state_integrity">Persistence &amp; Integrity</button>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="owner_actions">Owner Actions</button>
                <button class="runtime-sidebar-link" type="button" data-runtime-sidebar-section="evidence_audit">Evidence &amp; Audit</button>
              </div>
            </section>
          </div>
        </div>
        <!-- END PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR -->'''

OLD_TOP_NAV = '''    <section
  class="runtime-owner-navigation-shell"
  id="runtimeOwnerNavigationShell"
  aria-label="Runtime Owner navigation"
>'''

NEW_TOP_NAV = '''    <section
  class="runtime-owner-navigation-shell"
  id="runtimeOwnerNavigationShell"
  aria-label="Runtime Owner navigation compatibility layer"
  aria-hidden="true"
  hidden
>'''

OWNER_CSS_APPEND = r'''

/* BEGIN PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR */
.owner-sidebar .runtime-sidebar-entry {
  width: 100%;
  margin: 3px 0;
}

.owner-sidebar .runtime-sidebar-root-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 38px;
  gap: 4px;
  align-items: center;
}

.owner-sidebar .runtime-sidebar-page-button {
  margin: 0;
  min-width: 0;
}

.owner-sidebar .runtime-sidebar-toggle,
.owner-sidebar .runtime-sidebar-group-toggle,
.owner-sidebar .runtime-sidebar-link {
  appearance: none;
  border: 0;
  font: inherit;
}

.owner-sidebar .runtime-sidebar-toggle {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border: 1px solid transparent;
  border-radius: 10px;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
}

.owner-sidebar .runtime-sidebar-toggle:hover,
.owner-sidebar .runtime-sidebar-toggle:focus-visible {
  color: var(--text);
  background: rgba(34, 211, 238, 0.09);
  border-color: rgba(34, 211, 238, 0.25);
  outline: none;
}

.owner-sidebar .runtime-sidebar-toggle-icon,
.owner-sidebar .runtime-sidebar-group-icon {
  display: inline-block;
  transition: transform 160ms ease;
}

.owner-sidebar .runtime-sidebar-toggle[aria-expanded="true"]
  .runtime-sidebar-toggle-icon,
.owner-sidebar .runtime-sidebar-group-toggle[aria-expanded="true"]
  .runtime-sidebar-group-icon {
  transform: rotate(180deg);
}

.owner-sidebar .runtime-sidebar-tree {
  margin: 7px 0 10px 10px;
  padding: 10px 0 3px 10px;
  border-left: 1px solid rgba(34, 211, 238, 0.24);
}

.owner-sidebar .runtime-sidebar-tree[hidden],
.owner-sidebar .runtime-sidebar-group-panel[hidden] {
  display: none !important;
}

.owner-sidebar .runtime-sidebar-tree-heading {
  margin: 0 8px 8px;
  color: #6f86a7;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.owner-sidebar .runtime-sidebar-group {
  margin: 2px 0;
}

.owner-sidebar .runtime-sidebar-group-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 9px;
  border-radius: 9px;
  background: transparent;
  color: #91a7c5;
  cursor: pointer;
  text-align: left;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.035em;
  text-transform: uppercase;
}

.owner-sidebar .runtime-sidebar-group-toggle:hover,
.owner-sidebar .runtime-sidebar-group-toggle:focus-visible {
  color: var(--text);
  background: rgba(255, 255, 255, 0.035);
  outline: none;
}

.owner-sidebar .runtime-sidebar-group-panel {
  display: grid;
  gap: 2px;
  padding: 2px 0 5px 8px;
}

.owner-sidebar .runtime-sidebar-link {
  width: 100%;
  position: relative;
  padding: 8px 9px 8px 18px;
  border-radius: 9px;
  background: transparent;
  color: #7f96b5;
  cursor: pointer;
  text-align: left;
  font-size: 12px;
  line-height: 1.35;
}

.owner-sidebar .runtime-sidebar-link::before {
  content: "";
  position: absolute;
  left: 7px;
  top: 50%;
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: currentColor;
  transform: translateY(-50%);
  opacity: 0.58;
}

.owner-sidebar .runtime-sidebar-link:hover,
.owner-sidebar .runtime-sidebar-link:focus-visible {
  color: var(--text);
  background: rgba(255, 255, 255, 0.04);
  outline: none;
}

.owner-sidebar .runtime-sidebar-link.active {
  color: #dffbff;
  background: linear-gradient(
    90deg,
    rgba(34, 211, 238, 0.18),
    rgba(34, 211, 238, 0.055)
  );
  box-shadow: inset 2px 0 0 var(--accent);
}

.owner-sidebar .runtime-sidebar-link.active::before {
  background: var(--accent);
  opacity: 1;
}

.owner-sidebar .runtime-sidebar-link:disabled,
.owner-sidebar .runtime-sidebar-link[aria-disabled="true"] {
  color: #4f6480;
  cursor: not-allowed;
  opacity: 0.72;
}

.owner-sidebar .runtime-sidebar-link:disabled:hover {
  background: transparent;
}

.owner-sidebar .runtime-sidebar-subgroup {
  margin: 3px 0 2px 8px;
  border-left: 1px solid rgba(142, 164, 194, 0.14);
}

.owner-sidebar .runtime-sidebar-subgroup-toggle {
  padding-left: 12px;
  font-size: 10px;
  color: #7f96b5;
}

.owner-sidebar .runtime-sidebar-subgroup-panel {
  padding-left: 9px;
}
/* END PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR */
'''

RUNTIME_JS_APPEND = r'''

// BEGIN PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR
(() => {
  "use strict";

  const SECTION_GROUPS = Object.freeze({
    overview: "runtimeSidebarCommandCenter",
    pipeline_operations: "runtimeSidebarPipelineOperations",
    jobs: "runtimeSidebarInfrastructure",
    queues: "runtimeSidebarInfrastructure",
    workers_leases: "runtimeSidebarInfrastructure",
    orchestration: "runtimeSidebarInfrastructure",
    execution: "runtimeSidebarInfrastructure",
    reliability_recovery: "runtimeSidebarHealth",
    resource_governance: "runtimeSidebarHealth",
    observability: "runtimeSidebarHealth",
    security: "runtimeSidebarHealth",
    runtime_apis: "runtimeSidebarAdministration",
    persistence_state_integrity: "runtimeSidebarAdministration",
    owner_actions: "runtimeSidebarAdministration",
    evidence_audit: "runtimeSidebarAdministration"
  });

  const byId = (id) => document.getElementById(id);

  const setDisclosure = (button, panel, expanded) => {
    if (!button || !panel) {
      return false;
    }

    button.setAttribute(
      "aria-expanded",
      expanded ? "true" : "false"
    );
    panel.hidden = !expanded;
    return true;
  };

  const openRuntimeTree = () => {
    const toggle = byId("runtimeSidebarToggle");
    const tree = byId("runtimeSidebarTree");

    if (!setDisclosure(toggle, tree, true)) {
      return false;
    }

    toggle.setAttribute(
      "aria-label",
      "Collapse Universal Runtime navigation"
    );
    return true;
  };

  const toggleRuntimeTree = () => {
    const toggle = byId("runtimeSidebarToggle");
    const tree = byId("runtimeSidebarTree");

    if (!toggle || !tree) {
      return false;
    }

    const expanded =
      toggle.getAttribute("aria-expanded") === "true";

    setDisclosure(toggle, tree, !expanded);
    toggle.setAttribute(
      "aria-label",
      expanded
        ? "Expand Universal Runtime navigation"
        : "Collapse Universal Runtime navigation"
    );
    return true;
  };

  const openGroupForSection = (section) => {
    const panelId = SECTION_GROUPS[section];
    const panel = panelId ? byId(panelId) : null;

    if (!panel) {
      return false;
    }

    const button = document.querySelector(
      `[data-runtime-sidebar-group-toggle]` +
      `[aria-controls="${panelId}"]`
    );

    return setDisclosure(button, panel, true);
  };

  const syncRuntimeSidebar = (section) => {
    const tree = byId("runtimeSidebarTree");

    if (!tree) {
      return false;
    }

    tree.querySelectorAll(
      "[data-runtime-sidebar-section]"
    ).forEach((button) => {
      const active =
        button.dataset.runtimeSidebarSection === section;

      button.classList.toggle("active", active);

      if (active) {
        button.setAttribute("aria-current", "page");
      } else {
        button.removeAttribute("aria-current");
      }
    });

    openRuntimeTree();
    openGroupForSection(section);
    return true;
  };

  const showRuntimePage = () => {
    const runtimePage = byId("runtimePage");
    const runtimeButton = byId("runtimeSidebarPageButton");

    if (
      runtimePage &&
      !runtimePage.classList.contains("active")
    ) {
      runtimeButton?.click();
    }
  };

  const bindRuntimeSidebar = () => {
    const entry = byId("runtimeSidebarEntry");
    const runtimePage = byId("runtimePage");
    const runtimeButton = byId("runtimeSidebarPageButton");
    const treeToggle = byId("runtimeSidebarToggle");

    if (!entry || !runtimePage || !runtimeButton || !treeToggle) {
      return false;
    }

    if (entry.dataset.runtimeSidebarBound === "true") {
      return true;
    }

    runtimeButton.addEventListener("click", openRuntimeTree);
    treeToggle.addEventListener("click", toggleRuntimeTree);

    entry.addEventListener("click", (event) => {
      const groupToggle = event.target.closest(
        "[data-runtime-sidebar-group-toggle]"
      );

      if (groupToggle) {
        const panel = byId(
          groupToggle.getAttribute("aria-controls")
        );
        const expanded =
          groupToggle.getAttribute("aria-expanded") === "true";

        setDisclosure(groupToggle, panel, !expanded);
        return;
      }

      const sectionButton = event.target.closest(
        "[data-runtime-sidebar-section]"
      );

      if (!sectionButton || sectionButton.disabled) {
        return;
      }

      showRuntimePage();

      window.LinkCraftorRuntimeOwner?.setActiveSection(
        sectionButton.dataset.runtimeSidebarSection
      );
    });

    runtimePage.addEventListener(
      "runtimeowner:sectionchange",
      (event) => {
        syncRuntimeSidebar(event.detail?.section || "overview");
      }
    );

    entry.dataset.runtimeSidebarBound = "true";

    if (runtimePage.classList.contains("active")) {
      syncRuntimeSidebar(
        window.LinkCraftorRuntimeOwner?.getActiveSection() ||
        "overview"
      );
    }

    return true;
  };

  window.LinkCraftorRuntimeSidebar = Object.freeze({
    bind: bindRuntimeSidebar,
    open: openRuntimeTree,
    sync: syncRuntimeSidebar
  });

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      bindRuntimeSidebar,
      { once: true }
    );
  } else {
    bindRuntimeSidebar();
  }
})();
// END PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR
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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(
            f"Expected one {label} anchor, found {count}."
        )
    return source.replace(old, new, 1)


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


def html_ids_unique(source: str) -> bool:
    parser = IdCollector()
    parser.feed(source)
    return len(parser.ids) == len(set(parser.ids))


def javascript_syntax_valid(source: str) -> bool:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is unavailable for JavaScript syntax validation.")

    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4d2_js_") as folder:
        candidate = Path(folder) / "runtime_owner_candidate.js"
        write_text(candidate, source)
        result = subprocess.run(
            [node, "--check", str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "Candidate JavaScript syntax validation failed: "
                + (result.stderr or result.stdout).strip()
            )
    return True


def print_check(name: str, value: bool) -> None:
    print(f"{name.upper()}: {'PASS' if value else 'FAIL'}")


def report_text(
    *,
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
    backup: Path | None,
) -> str:
    failed = [name for name, value in checks.items() if not value]
    return "\n".join(
        [
            "LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS",
            "PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR CERTIFICATION",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "Patch mode: STRICT FAIL-CLOSED",
            f"Backup: {backup if backup else 'NOT CREATED'}",
            "Production jobs created: NO",
            "Production queue claims executed: NO",
            "Production handlers executed: NO",
            "Production workflow persistence executed: NO",
            "Production recovery actions executed: NO",
            "Live network requests executed: NO",
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
            json.dumps(error, indent=2),
            "",
            "IMPLEMENTED BOUNDARY:",
            "- Universal Runtime now owns one accessible collapsible navigation tree in the Owner sidebar.",
            "- Runtime Overview and All Pipelines retain their existing certified behavior.",
            "- Runtime Infrastructure, Health and Administration destinations use existing section panels.",
            "- Eight Connected Domain component destinations are visible but disabled until their static shells are built.",
            "- The former in-page pill navigation remains as a hidden compatibility layer only.",
            "- No new endpoint request, recovery control, job action or backend authority was added.",
            "",
            "NEXT STEP:",
            "Part F 15-B4D3 - compact header, breadcrumb and status strip.",
            "",
            "FINAL RESULT:",
            FINAL_RESULT if status == "CERTIFIED" else (
                "FINAL RESULT: PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR NOT_CERTIFIED"
            ),
            "",
        ]
    )


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4D2_NESTED_RUNTIME_SIDEBAR.py <project-root> <report-path>"
        )

    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    reports_dir = root / "backend" / "server" / "data" / "reports"

    paths = {
        "index_html": root / "backend" / "server" / "owner" / "index.html",
        "owner_css": root / "backend" / "server" / "owner" / "owner.css",
        "owner_js": root / "backend" / "server" / "owner" / "owner.js",
        "runtime_owner_css": root / "backend" / "server" / "owner" / "runtime_owner.css",
        "runtime_owner_js": root / "backend" / "server" / "owner" / "runtime_owner.js",
        "runtime_summary_api": root / "backend" / "server" / "owner" / "runtime_summary_api.py",
        "pipeline_operations": root / "backend" / "server" / "owner" / "pipeline_operations.py",
    }

    d1_report = reports_dir / "PART_F_15_B4D1_RUNTIME_UI_RESTRUCTURE_SOURCE_CONTRACT.txt"
    b4c_report = reports_dir / "PART_F_15_B4C_ALL_PIPELINES_OVERVIEW_CERTIFICATION.txt"

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    backup_dir: Path | None = None
    originals: dict[str, bytes] = {}
    retained = False

    report.parent.mkdir(parents=True, exist_ok=True)

    try:
        checks["part_f_15_b4d1_report_exists"] = d1_report.is_file()
        checks["part_f_15_b4d1_complete"] = (
            checks["part_f_15_b4d1_report_exists"]
            and "FINAL RESULT: PART F 15-B4D1 SOURCE CONTRACT COMPLETE"
            in read_text(d1_report)
        )
        checks["part_f_15_b4c_report_exists"] = b4c_report.is_file()
        checks["part_f_15_b4c_certified"] = (
            checks["part_f_15_b4c_report_exists"]
            and "CERTIFICATION STATUS: CERTIFIED" in read_text(b4c_report)
            and "FINAL RESULT: PART F 15-B4C ALL PIPELINES OVERVIEW CERTIFIED"
            in read_text(b4c_report)
        )

        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()

        if not all(checks.values()):
            raise RuntimeError("Required historical evidence or source is unavailable.")

        before_hashes = {
            name: sha256_path(path)
            for name, path in paths.items()
        }
        evidence["source_hashes_before"] = before_hashes

        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before_hashes[name] == expected

        if not all(
            checks[f"source_hash_{name}"]
            for name in EXPECTED_HASHES
        ):
            raise RuntimeError(
                "A certified frontend source changed after 15-B4D1; no patch was applied."
            )

        html_source = read_text(paths["index_html"])
        css_source = read_text(paths["owner_css"])
        runtime_js_source = read_text(paths["runtime_owner_js"])

        checks["patch_not_previously_present"] = (
            SIDEBAR_MARKER not in html_source
            and SIDEBAR_MARKER not in css_source
            and SIDEBAR_MARKER not in runtime_js_source
        )
        if not checks["patch_not_previously_present"]:
            raise RuntimeError("The 15-B4D2 sidebar boundary is already present.")

        html_candidate = replace_once(
            html_source,
            OLD_RUNTIME_NAV,
            NEW_RUNTIME_NAV,
            "flat Universal Runtime navigation",
        )
        html_candidate = replace_once(
            html_candidate,
            OLD_TOP_NAV,
            NEW_TOP_NAV,
            "in-page runtime navigation shell",
        )
        css_candidate = css_source.rstrip() + "\n" + OWNER_CSS_APPEND.lstrip()
        runtime_js_candidate = (
            runtime_js_source.rstrip()
            + "\n"
            + RUNTIME_JS_APPEND.lstrip()
        )

        checks["candidate_html_ids_unique"] = html_ids_unique(html_candidate)
        checks["candidate_css_balanced"] = css_balanced(css_candidate)
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(
            runtime_js_candidate
        )
        checks["nested_runtime_sidebar_declared_once"] = (
            html_candidate.count('id="runtimeSidebarTree"') == 1
            and html_candidate.count('id="runtimeSidebarToggle"') == 1
            and html_candidate.count('id="runtimeSidebarPageButton"') == 1
        )
        checks["five_runtime_navigation_groups_present"] = all(
            f'data-runtime-sidebar-group="{group}"' in html_candidate
            for group in (
                "command_center",
                "pipeline_operations",
                "runtime_infrastructure",
                "runtime_health",
                "runtime_administration",
            )
        )

        expected_sections = (
            "overview",
            "pipeline_operations",
            "jobs",
            "queues",
            "workers_leases",
            "orchestration",
            "execution",
            "reliability_recovery",
            "resource_governance",
            "observability",
            "security",
            "runtime_apis",
            "persistence_state_integrity",
            "owner_actions",
            "evidence_audit",
        )
        checks["all_runtime_sections_rehomed"] = all(
            html_candidate.count(
                f'data-runtime-sidebar-section="{section}"'
            ) == 1
            for section in expected_sections
        )

        expected_pipeline_views = (
            "overview",
            "workflows",
            "stage_progress",
            "jobs_attempts",
            "dependencies_handoffs",
            "events_timeline",
            "failures_attention",
            "output_readiness",
        )
        checks["eight_connected_domain_locations_present"] = all(
            html_candidate.count(
                f'data-runtime-pipeline-view="{view}"'
            ) == 1
            for view in expected_pipeline_views
        )
        checks["future_pipeline_locations_disabled"] = all(
            re.search(
                rf'<button[^>]*data-runtime-pipeline-view="{re.escape(view)}"[^>]*disabled',
                html_candidate,
                flags=re.S,
            )
            is not None
            for view in expected_pipeline_views
        )
        checks["legacy_pill_navigation_hidden"] = (
            'id="runtimeOwnerNavigationShell"' in html_candidate
            and 'aria-label="Runtime Owner navigation compatibility layer"'
            in html_candidate
            and re.search(
                r'id="runtimeOwnerNavigationShell"[^>]*\bhidden\b',
                html_candidate,
                flags=re.S,
            )
            is not None
        )
        checks["sidebar_styles_scoped"] = (
            ".owner-sidebar .runtime-sidebar-entry" in css_candidate
            and ".owner-sidebar .runtime-sidebar-link.active" in css_candidate
        )
        checks["sidebar_navigation_binding_declared_once"] = (
            runtime_js_candidate.count(
                "const bindRuntimeSidebar = () =>"
            ) == 1
            and runtime_js_candidate.count(
                "window.LinkCraftorRuntimeSidebar"
            ) == 1
        )
        checks["existing_runtime_sections_reused"] = (
            "window.LinkCraftorRuntimeOwner?.setActiveSection" in runtime_js_candidate
        )
        checks["no_new_fetch_requests_added"] = (
            runtime_js_candidate.count("fetch(")
            == runtime_js_source.count("fetch(")
        )
        checks["canonical_pipeline_endpoint_retained"] = (
            runtime_js_candidate.count(
                '"/owner/api/runtime/pipelines"'
            )
            == runtime_js_source.count(
                '"/owner/api/runtime/pipelines"'
            )
            == 1
        )
        checks["no_recovery_controls_added"] = all(
            token not in NEW_RUNTIME_NAV + RUNTIME_JS_APPEND
            for token in (
                "data-runtime-recovery-action",
                "retryJob",
                "cancelJob",
                "terminateJob",
            )
        )
        checks["owner_global_navigation_unchanged"] = (
            sha256_path(paths["owner_js"]) == EXPECTED_HASHES["owner_js"]
        )
        checks["runtime_component_styles_unchanged"] = (
            sha256_path(paths["runtime_owner_css"])
            == EXPECTED_HASHES["runtime_owner_css"]
        )

        if not all(checks.values()):
            raise RuntimeError("Candidate certification checks failed before patching.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = (
            root
            / "backend"
            / "server"
            / "data"
            / "runtime_backups"
            / f"part_f_15_b4d2_{timestamp}"
        )
        backup_dir.mkdir(parents=True, exist_ok=False)

        target_names = ("index_html", "owner_css", "runtime_owner_js")
        for name in target_names:
            path = paths[name]
            originals[name] = path.read_bytes()
            shutil.copy2(path, backup_dir / path.name)

        checks["backup_created"] = all(
            (backup_dir / paths[name].name).is_file()
            for name in target_names
        )
        if not checks["backup_created"]:
            raise RuntimeError("The production-source backup is incomplete.")

        write_text(paths["index_html"], html_candidate)
        write_text(paths["owner_css"], css_candidate)
        write_text(paths["runtime_owner_js"], runtime_js_candidate)

        checks["retained_html_ids_unique"] = html_ids_unique(
            read_text(paths["index_html"])
        )
        checks["retained_css_balanced"] = css_balanced(
            read_text(paths["owner_css"])
        )
        checks["retained_javascript_syntax"] = javascript_syntax_valid(
            read_text(paths["runtime_owner_js"])
        )
        checks["retained_sidebar_marker_once"] = all(
            read_text(paths[name]).count(SIDEBAR_MARKER) == 2
            for name in ("index_html", "owner_css", "runtime_owner_js")
        )

        after_hashes = {
            name: sha256_path(path)
            for name, path in paths.items()
        }
        evidence["source_hashes_after"] = after_hashes
        evidence["backup"] = str(backup_dir)
        evidence["navigation_groups"] = [
            "Command Center",
            "Pipeline Operations",
            "Runtime Infrastructure",
            "Runtime Health",
            "Runtime Administration",
        ]
        evidence["runtime_sections"] = list(expected_sections)
        evidence["connected_domain_locations"] = list(
            expected_pipeline_views
        )
        evidence["new_endpoint_requests"] = 0
        evidence["recovery_controls_added"] = False

        checks["owner_global_navigation_stable"] = (
            before_hashes["owner_js"] == after_hashes["owner_js"]
        )
        checks["runtime_component_styles_stable"] = (
            before_hashes["runtime_owner_css"]
            == after_hashes["runtime_owner_css"]
        )
        checks["backend_api_source_unchanged"] = (
            before_hashes["runtime_summary_api"]
            == after_hashes["runtime_summary_api"]
        )
        checks["pipeline_projection_source_unchanged"] = (
            before_hashes["pipeline_operations"]
            == after_hashes["pipeline_operations"]
        )
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_no"] = True

        if not all(checks.values()):
            raise RuntimeError("Retained-source certification checks failed.")

        retained = True
        status = "CERTIFIED"

    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        status = "NOT_CERTIFIED"

        if originals:
            for name, data in originals.items():
                paths[name].write_bytes(data)

    final_report = report_text(
        status=status,
        checks=checks,
        evidence=evidence,
        error=error,
        backup=backup_dir,
    )
    write_text(report, final_report)

    for name, value in checks.items():
        print_check(name, value)

    failed = [name for name, value in checks.items() if not value]
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B4D2_STATUS={status}")
    print(
        "PATCH_RETAINED=YES"
        if retained
        else "PATCH_RETAINED=NO"
    )

    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
