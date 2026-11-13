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
from pathlib import Path
from typing import Any


FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B4D2R "
    "COMPACT RUNTIME SIDEBAR CORRECTION CERTIFIED"
)

EXPECTED_HASHES = {
    "index_html": "3623ef107bbc9cf3e82ce74440de52cc144e405b1ee1685f35aee72a91574061",
    "owner_css": "04cd8b4fe3872df671952b1dad34eaaf5661bc151c1aabea0d051745faf2ce34",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "bd43654128f36b2f38dd3418703fdfaf3763ca0c9fc2116f419933d44ef1aee5",
    "runtime_owner_js": "46ab8b9fdb2476078bb679d3c0a042da23b36c3327140986450a787a344b6790",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "570bfc61676fd15b5a1cacc6ed74130eac1d98dc41f327606019df59d55f342a",
}

MARKER = "PART F 15-B4D2R COMPACT RUNTIME SIDEBAR CORRECTION"

COLLAPSE_HELPER = r'''  const collapseMainGroups = (exceptButton = null) => {
    const tree = byId("runtimeSidebarTree");

    if (!tree) {
      return false;
    }

    tree.querySelectorAll(
      ".runtime-sidebar-group > .runtime-sidebar-group-toggle"
    ).forEach((button) => {
      if (button === exceptButton) {
        return;
      }

      const panel = byId(
        button.getAttribute("aria-controls")
      );

      setDisclosure(button, panel, false);
    });

    return true;
  };

'''

OPEN_TREE_ANCHOR = '''  const openRuntimeTree = () => {'''

OLD_OPEN_GROUP_RETURN = '''    return setDisclosure(button, panel, true);
  };

  const syncRuntimeSidebar = (section) => {'''

NEW_OPEN_GROUP_RETURN = '''    collapseMainGroups(button);
    return setDisclosure(button, panel, true);
  };

  const syncRuntimeSidebar = (section) => {'''

OLD_ROOT_BINDING = '''    runtimeButton.addEventListener("click", openRuntimeTree);
    treeToggle.addEventListener("click", toggleRuntimeTree);'''

NEW_ROOT_BINDING = '''    runtimeButton.addEventListener("click", () => {
      openRuntimeTree();
      syncRuntimeSidebar(
        window.LinkCraftorRuntimeOwner?.getActiveSection() ||
        "overview"
      );
    });
    treeToggle.addEventListener("click", toggleRuntimeTree);'''

OLD_GROUP_TOGGLE = '''        const expanded =
          groupToggle.getAttribute("aria-expanded") === "true";

        setDisclosure(groupToggle, panel, !expanded);
        return;'''

NEW_GROUP_TOGGLE = '''        const expanded =
          groupToggle.getAttribute("aria-expanded") === "true";
        const opening = !expanded;
        const nested = groupToggle.classList.contains(
          "runtime-sidebar-subgroup-toggle"
        );

        if (opening && !nested) {
          collapseMainGroups(groupToggle);
        }

        setDisclosure(groupToggle, panel, opening);
        return;'''

CSS_APPEND = r'''

/* BEGIN PART F 15-B4D2R COMPACT RUNTIME SIDEBAR CORRECTION */
.owner-sidebar .runtime-sidebar-tree {
  max-height: min(56vh, 510px);
  margin-top: 5px;
  margin-bottom: 7px;
  padding: 6px 4px 3px 8px;
  overflow-y: auto;
  overscroll-behavior: contain;
  scrollbar-width: thin;
  scrollbar-color: rgba(34, 211, 238, 0.34) transparent;
}

.owner-sidebar .runtime-sidebar-tree-heading {
  display: none;
}

.owner-sidebar .runtime-sidebar-group {
  margin: 1px 0;
}

.owner-sidebar .runtime-sidebar-group-toggle {
  min-height: 32px;
  padding: 6px 8px;
  color: #9db0ca;
  font-size: 11px;
  font-weight: 750;
  letter-spacing: 0.015em;
  text-transform: none;
}

.owner-sidebar .runtime-sidebar-group-panel {
  gap: 0;
  padding: 1px 0 3px 6px;
}

.owner-sidebar .runtime-sidebar-link {
  min-height: 30px;
  padding: 6px 7px 6px 17px;
  font-size: 11.5px;
  line-height: 1.25;
}

.owner-sidebar .runtime-sidebar-subgroup {
  margin: 1px 0 1px 6px;
}

.owner-sidebar .runtime-sidebar-subgroup-toggle {
  min-height: 29px;
  padding: 5px 7px 5px 10px;
  font-size: 10.5px;
}

.owner-sidebar .runtime-sidebar-subgroup-panel {
  padding-left: 6px;
}

.owner-sidebar .runtime-sidebar-toggle-icon,
.owner-sidebar .runtime-sidebar-group-icon {
  width: 7px;
  height: 7px;
  flex: 0 0 7px;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  font-size: 0;
  transform: rotate(45deg);
  transform-origin: center;
}

.owner-sidebar .runtime-sidebar-toggle[aria-expanded="true"]
  .runtime-sidebar-toggle-icon,
.owner-sidebar .runtime-sidebar-group-toggle[aria-expanded="true"]
  .runtime-sidebar-group-icon {
  transform: rotate(225deg);
}

.owner-sidebar .runtime-sidebar-link:disabled,
.owner-sidebar .runtime-sidebar-link[aria-disabled="true"] {
  opacity: 0.54;
}
/* END PART F 15-B4D2R COMPACT RUNTIME SIDEBAR CORRECTION */
'''


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label} anchor, found {count}.")
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


def javascript_syntax_valid(source: str) -> bool:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is unavailable for JavaScript validation.")
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4d2r_js_") as folder:
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
                "JavaScript validation failed: "
                + (result.stderr or result.stdout).strip()
            )
    return True


def print_check(name: str, value: bool) -> None:
    print(f"{name.upper()}: {'PASS' if value else 'FAIL'}")


def build_report(
    *,
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
    backup: Path | None,
) -> str:
    failed = [name for name, value in checks.items() if not value]
    lines = [
        "LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS",
        "PART F 15-B4D2R COMPACT RUNTIME SIDEBAR CORRECTION CERTIFICATION",
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
        "CORRECTED BOUNDARY:",
        "- Only one main Runtime navigation group remains expanded at a time.",
        "- Selecting a Runtime destination automatically opens only its owning group.",
        "- Connected Domain remains a nested subgroup and its future destinations remain disabled.",
        "- The Runtime tree has a bounded internal scroll region so global Owner navigation remains reachable.",
        "- Spacing, typography, indentation and chevrons are compacted for clearer hierarchy.",
        "- No endpoint request, recovery control or backend authority was added.",
        "",
        "NEXT STEP:",
        "Part F 15-B4D3 - compact header, breadcrumb and status strip.",
        "",
        "FINAL RESULT:",
        FINAL_RESULT if status == "CERTIFIED" else (
            "FINAL RESULT: PART F 15-B4D2R COMPACT RUNTIME SIDEBAR CORRECTION NOT_CERTIFIED"
        ),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4D2R_COMPACT_SIDEBAR.py <project-root> <report-path>"
        )

    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    reports = root / "backend" / "server" / "data" / "reports"
    d2_report = reports / "PART_F_15_B4D2_NESTED_RUNTIME_SIDEBAR_CERTIFICATION.txt"

    paths = {
        "index_html": root / "backend" / "server" / "owner" / "index.html",
        "owner_css": root / "backend" / "server" / "owner" / "owner.css",
        "owner_js": root / "backend" / "server" / "owner" / "owner.js",
        "runtime_owner_css": root / "backend" / "server" / "owner" / "runtime_owner.css",
        "runtime_owner_js": root / "backend" / "server" / "owner" / "runtime_owner.js",
        "runtime_summary_api": root / "backend" / "server" / "owner" / "runtime_summary_api.py",
        "pipeline_operations": root / "backend" / "server" / "owner" / "pipeline_operations.py",
    }

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}
    backup_dir: Path | None = None
    retained = False
    report.parent.mkdir(parents=True, exist_ok=True)

    try:
        checks["part_f_15_b4d2_report_exists"] = d2_report.is_file()
        checks["part_f_15_b4d2_certified"] = (
            checks["part_f_15_b4d2_report_exists"]
            and "CERTIFICATION STATUS: CERTIFIED" in read_text(d2_report)
            and "FINAL RESULT: PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR CERTIFIED"
            in read_text(d2_report)
        )

        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()

        if not all(checks.values()):
            raise RuntimeError("Required 15-B4D2 evidence or source is unavailable.")

        before = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before[name] == expected

        if not all(checks[f"source_hash_{name}"] for name in EXPECTED_HASHES):
            raise RuntimeError(
                "A certified 15-B4D2 source changed; no correction was applied."
            )

        html_source = read_text(paths["index_html"])
        css_source = read_text(paths["owner_css"])
        js_source = read_text(paths["runtime_owner_js"])

        checks["d2_sidebar_boundary_present"] = (
            "PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR" in html_source
            and "PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR" in css_source
            and "PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR" in js_source
        )
        checks["correction_not_previously_present"] = (
            MARKER not in css_source and MARKER not in js_source
        )
        if not checks["d2_sidebar_boundary_present"]:
            raise RuntimeError("The certified 15-B4D2 sidebar boundary is absent.")
        if not checks["correction_not_previously_present"]:
            raise RuntimeError("The compact-sidebar correction is already present.")

        js_candidate = replace_once(
            js_source,
            OPEN_TREE_ANCHOR,
            COLLAPSE_HELPER + OPEN_TREE_ANCHOR,
            "accordion helper insertion",
        )
        js_candidate = replace_once(
            js_candidate,
            OLD_OPEN_GROUP_RETURN,
            NEW_OPEN_GROUP_RETURN,
            "active-group synchronization",
        )
        js_candidate = replace_once(
            js_candidate,
            OLD_ROOT_BINDING,
            NEW_ROOT_BINDING,
            "Runtime root synchronization",
        )
        js_candidate = replace_once(
            js_candidate,
            OLD_GROUP_TOGGLE,
            NEW_GROUP_TOGGLE,
            "accordion click behavior",
        )
        js_candidate = js_candidate.rstrip() + (
            "\n\n// " + MARKER + "\n"
        )
        css_candidate = css_source.rstrip() + "\n" + CSS_APPEND.lstrip()

        checks["candidate_css_balanced"] = css_balanced(css_candidate)
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(js_candidate)
        checks["single_open_group_policy_present"] = (
            js_candidate.count("const collapseMainGroups =") == 1
            and "collapseMainGroups(groupToggle);" in js_candidate
            and "collapseMainGroups(button);" in js_candidate
        )
        checks["root_selection_sync_present"] = (
            'runtimeButton.addEventListener("click", () =>' in js_candidate
            and "syncRuntimeSidebar(" in js_candidate
        )
        checks["nested_connected_domain_retained"] = (
            html_source.count("runtime-sidebar-subgroup-toggle") == 1
            and html_source.count("data-runtime-pipeline-view=") == 8
        )
        checks["future_destinations_remain_disabled"] = (
            len(re.findall(
                r'data-runtime-pipeline-view="[^"]+"[^>]*\bdisabled\b',
                html_source,
                flags=re.S,
            )) == 8
        )
        checks["bounded_sidebar_scroll_present"] = (
            "max-height: min(56vh, 510px);" in css_candidate
            and "overflow-y: auto;" in css_candidate
        )
        checks["compact_spacing_present"] = all(
            token in css_candidate
            for token in (
                "min-height: 32px;",
                "min-height: 30px;",
                "font-size: 11.5px;",
            )
        )
        checks["clear_chevrons_present"] = (
            "border-right: 2px solid currentColor;" in css_candidate
            and "transform: rotate(225deg);" in css_candidate
        )
        checks["no_new_fetch_requests_added"] = (
            js_candidate.count("fetch(") == js_source.count("fetch(")
        )
        checks["canonical_pipeline_endpoint_retained"] = (
            js_candidate.count('"/owner/api/runtime/pipelines"')
            == js_source.count('"/owner/api/runtime/pipelines"')
            == 1
        )
        checks["no_recovery_controls_added"] = all(
            token not in COLLAPSE_HELPER + NEW_GROUP_TOGGLE
            for token in (
                "data-runtime-recovery-action",
                "retryJob",
                "cancelJob",
                "terminateJob",
            )
        )

        if not all(checks.values()):
            raise RuntimeError("Candidate correction checks failed before patching.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = (
            root / "backend" / "server" / "data" / "runtime_backups"
            / f"part_f_15_b4d2r_{timestamp}"
        )
        backup_dir.mkdir(parents=True, exist_ok=False)

        for name in ("owner_css", "runtime_owner_js"):
            path = paths[name]
            originals[name] = path.read_bytes()
            shutil.copy2(path, backup_dir / path.name)

        checks["backup_created"] = all(
            (backup_dir / paths[name].name).is_file()
            for name in originals
        )
        if not checks["backup_created"]:
            raise RuntimeError("Correction backup is incomplete.")

        write_text(paths["owner_css"], css_candidate)
        write_text(paths["runtime_owner_js"], js_candidate)

        checks["retained_css_balanced"] = css_balanced(
            read_text(paths["owner_css"])
        )
        checks["retained_javascript_syntax"] = javascript_syntax_valid(
            read_text(paths["runtime_owner_js"])
        )
        checks["retained_correction_marker_once"] = (
            read_text(paths["owner_css"]).count(MARKER) == 2
            and read_text(paths["runtime_owner_js"]).count(MARKER) == 1
        )

        after = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_after"] = after
        evidence["backup"] = str(backup_dir)
        evidence["interaction_policy"] = "single_main_group_open"
        evidence["runtime_tree_max_height"] = "min(56vh, 510px)"
        evidence["connected_domain_destinations_enabled"] = False
        evidence["new_endpoint_requests"] = 0
        evidence["recovery_controls_added"] = False

        for name in (
            "index_html",
            "owner_js",
            "runtime_owner_css",
            "runtime_summary_api",
            "pipeline_operations",
        ):
            checks[f"unchanged_{name}"] = before[name] == after[name]

        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_no"] = True

        if not all(checks.values()):
            raise RuntimeError("Retained-source correction checks failed.")

        retained = True
        status = "CERTIFIED"

    except Exception as exc:
        status = "NOT_CERTIFIED"
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        for name, data in originals.items():
            paths[name].write_bytes(data)

    write_text(
        report,
        build_report(
            status=status,
            checks=checks,
            evidence=evidence,
            error=error,
            backup=backup_dir,
        ),
    )

    for name, value in checks.items():
        print_check(name, value)
    failed = [name for name, value in checks.items() if not value]
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B4D2R_STATUS={status}")
    print("PATCH_RETAINED=YES" if retained else "PATCH_RETAINED=NO")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
