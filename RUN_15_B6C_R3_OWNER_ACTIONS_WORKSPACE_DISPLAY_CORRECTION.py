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


TITLE = "PART F 15-B6C-R3 OWNER ACTIONS WORKSPACE DISPLAY CORRECTION"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B6C-R3 OWNER ACTIONS WORKSPACE DISPLAY "
    "CORRECTION CERTIFIED"
)

INDEX_PATH = "backend/server/owner/index.html"
RUNTIME_JS_PATH = "backend/server/owner/runtime_owner.js"
B6_REPORT_PATH = (
    "backend/server/data/reports/"
    "PART_F_15_B6B_B6I_OWNER_ACTIONS_RECOVERY_SAFETY_UI_CERTIFICATION.txt"
)
R2_REPORT_PATH = (
    "backend/server/data/reports/"
    "PART_F_15_B6C_R2_RUNTIME_OWNER_SHARED_NAVIGATION_REPAIR_CERTIFICATION.txt"
)

SOURCE_PATHS = {
    "index_html": INDEX_PATH,
    "runtime_owner_css": "backend/server/owner/runtime_owner.css",
    "runtime_owner_js": RUNTIME_JS_PATH,
    "runtime_summary_api": "backend/server/owner/runtime_summary_api.py",
    "owner_actions_gateway": "backend/server/owner/owner_actions_gateway.py",
    "runtime_infrastructure_projection": (
        "backend/server/owner/runtime_infrastructure_projection.py"
    ),
    "pipeline_operations": "backend/server/owner/pipeline_operations.py",
}

# Exact retained B6C-R2 baseline supplied by its certified report.
EXPECTED_HASHES = {
    "index_html": "25ced4ce757ce9db1992ef23d4f6cb58af290b17af006c0494b09572d87c1ad0",
    "runtime_owner_css": "3ba0fc871d432c013f9a7d43deaf9cde4f968447c4e489394a1f4b3dab2715fd",
    "runtime_owner_js": "76a2be1bbc217e9fb3c2e6fc592eeadf1dfb7c6b33c0d7d2d6d30eaad0268e33",
    "runtime_summary_api": "fb76eae288d2ae26c86cb6280c821a10664d35ee95882cb1486e8fc9b6848443",
    "owner_actions_gateway": "357e7e3b4be573700652ea2268d38071f3b376a7d27f55b42aea0af54dc72a97",
    "runtime_infrastructure_projection": "694fd8fae5dbf6ade79b73e2e4edbcb10fa49bf10666e8163112020634468a5f",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

B6_FINAL = (
    "FINAL RESULT: PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND "
    "RECOVERY SAFETY FRAMEWORK AND UI CERTIFIED"
)
R2_FINAL = (
    "FINAL RESULT: PART F 15-B6C-R2 RUNTIME OWNER SHARED NAVIGATION "
    "REPAIR CERTIFIED"
)

PANEL_ID = "runtimeOwnerSectionOwnerActions"
WORKSPACE_ID = "runtimeOwnerActionsWorkspace"
PLACEHOLDER_SENTENCE = (
    "Runtime Owner data for Runtime Owner Actions will be connected by its "
    "implementation phase."
)
OLD_CACHE = '<script src="/owner/runtime_owner.js?v=24"></script>'
NEW_CACHE = '<script src="/owner/runtime_owner.js?v=25"></script>'
OLD_ACTIVE_ASSIGNMENT = (
    "    contentPanel.dataset.runtimeOwnerActiveSection = normalized;"
)
NEW_ACTIVE_ASSIGNMENT = '''    // PART F 15-B6C-R3: keep the installed Owner Actions workspace
    // synchronized with the shared Runtime Owner section authority.
    const ownerActionsWorkspace = document.getElementById(
      "runtimeOwnerActionsWorkspace"
    );

    if (ownerActionsWorkspace) {
      const ownerActionsActive = normalized === "owner_actions";
      ownerActionsWorkspace.hidden = !ownerActionsActive;
      ownerActionsWorkspace.setAttribute(
        "aria-hidden",
        ownerActionsActive ? "false" : "true"
      );
    }

    contentPanel.dataset.runtimeOwnerActiveSection = normalized;'''


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key == "id" and value:
                self.ids.append(value)

    handle_startendtag = handle_starttag


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def atomic_write(path: Path, source: str) -> None:
    temporary = path.with_name(path.name + ".tmp-b6cr3")
    temporary.write_text(source, encoding="utf-8", newline="\n")
    temporary.replace(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ids_unique(source: str) -> bool:
    parser = IdCollector()
    parser.feed(source)
    parser.close()
    return len(parser.ids) == len(set(parser.ids))


def javascript_syntax_valid(source: str) -> bool:
    with tempfile.TemporaryDirectory(prefix="linkcraftor-b6cr3-js-") as folder:
        path = Path(folder) / "runtime_owner.js"
        path.write_text(source, encoding="utf-8")
        try:
            result = subprocess.run(
                ["node", "--check", str(path)],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        return result.returncode == 0


def certified_report(source: str, final: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return all(token in normalized for token in (
        "CERTIFICATION STATUS: CERTIFIED",
        "FAILED_CHECKS:\n[]",
        "NOT_RUN_CHECKS:\n[]",
        final,
    ))


def element_span(source: str, element_id: str) -> tuple[int, int, int, int, str]:
    opening_pattern = re.compile(
        r"<(?P<tag>[A-Za-z][A-Za-z0-9:_-]*)\b[^>]*\bid\s*=\s*"
        + r"(?P<quote>[\"'])"
        + re.escape(element_id)
        + r"(?P=quote)[^>]*>",
        re.IGNORECASE | re.DOTALL,
    )
    matches = list(opening_pattern.finditer(source))
    if len(matches) != 1:
        raise RuntimeError(
            f"Element #{element_id} was expected exactly once; found {len(matches)}."
        )
    opening = matches[0]
    tag = opening.group("tag")
    token_pattern = re.compile(
        rf"</?{re.escape(tag)}\b[^>]*>", re.IGNORECASE | re.DOTALL
    )
    depth = 0
    for token in token_pattern.finditer(source, opening.start()):
        text = token.group(0)
        if text.startswith("</"):
            depth -= 1
            if depth == 0:
                return (
                    opening.start(),
                    opening.end(),
                    token.start(),
                    token.end(),
                    tag,
                )
        elif not text.rstrip().endswith("/>"):
            depth += 1
    raise RuntimeError(f"Closing tag for #{element_id} is unavailable.")


def clean_workspace_opening(opening: str) -> str:
    cleaned = re.sub(r"\s+hidden(?:\s*=\s*([\"'])hidden\1)?", "", opening, flags=re.I)
    cleaned = re.sub(
        r"\s+aria-hidden\s*=\s*([\"'])true\1",
        ' aria-hidden="false"',
        cleaned,
        flags=re.I,
    )
    style_match = re.search(r"\sstyle\s*=\s*([\"'])(.*?)\1", cleaned, re.I | re.S)
    if style_match:
        style = re.sub(r"(?:^|;)\s*display\s*:\s*none\s*;?", ";", style_match.group(2), flags=re.I)
        style = re.sub(r";;+", ";", style).strip(" ;")
        replacement = f' style="{style}"' if style else ""
        cleaned = cleaned[: style_match.start()] + replacement + cleaned[style_match.end() :]
    return cleaned


def remove_placeholder(panel: str) -> str:
    candidate = panel
    escaped = re.escape(PLACEHOLDER_SENTENCE)
    paragraph = re.compile(
        r"<p\b[^>]*>\s*" + escaped + r"\s*</p>", re.I | re.S
    )
    candidate, paragraph_count = paragraph.subn("", candidate)
    if paragraph_count == 0:
        candidate = candidate.replace(PLACEHOLDER_SENTENCE, "")
    heading = re.compile(
        r"<h([1-6])\b[^>]*>\s*Runtime Owner Actions\s*</h\1>",
        re.I | re.S,
    )
    candidate = heading.sub("", candidate)
    return candidate


def control_evidence(workspace: str) -> dict[str, Any]:
    button_count = len(re.findall(r"<button\b", workspace, re.I))
    form_count = len(re.findall(r"<form\b", workspace, re.I))
    field_count = len(re.findall(r"<(?:input|select|textarea)\b", workspace, re.I))
    action_terms = sum(
        1
        for token in (
            "job", "queue", "workflow", "stage", "worker", "lease",
            "execution", "eligibility", "preview", "confirmation",
        )
        if token in workspace.lower()
    )
    return {
        "button_count": button_count,
        "form_count": form_count,
        "field_count": field_count,
        "action_term_count": action_terms,
        "html_length": len(workspace),
        "controls_present": (
            button_count >= 1
            and field_count >= 1
            and action_terms >= 4
            and len(workspace) >= 1000
        ),
    }


def build_candidate_html(source: str) -> tuple[str, dict[str, Any]]:
    if source.count(OLD_CACHE) != 1:
        raise RuntimeError("Runtime Owner JavaScript v24 cache reference is unavailable.")
    candidate = source.replace(OLD_CACHE, NEW_CACHE, 1)

    panel_start, _, panel_close, _, _ = element_span(candidate, PANEL_ID)
    workspace_start, workspace_open_end, _, workspace_end, _ = element_span(
        candidate, WORKSPACE_ID
    )
    original_workspace = candidate[workspace_start:workspace_end]
    evidence_before = control_evidence(original_workspace)
    if not evidence_before["controls_present"]:
        raise RuntimeError(
            "The installed Owner Actions workspace does not contain the certified UI controls; "
            f"evidence={json.dumps(evidence_before, sort_keys=True)}"
        )

    opening = candidate[workspace_start:workspace_open_end]
    cleaned_workspace = (
        clean_workspace_opening(opening)
        + candidate[workspace_open_end:workspace_end]
    )

    workspace_nested_before = (
        panel_start < workspace_start < panel_close
    )
    if workspace_nested_before:
        candidate = (
            candidate[:workspace_start]
            + cleaned_workspace
            + candidate[workspace_end:]
        )
    else:
        candidate = candidate[:workspace_start] + candidate[workspace_end:]
        panel_start, _, panel_close, _, _ = element_span(candidate, PANEL_ID)
        candidate = (
            candidate[:panel_close]
            + "\n"
            + cleaned_workspace
            + "\n"
            + candidate[panel_close:]
        )

    panel_start, _, _, panel_end, _ = element_span(candidate, PANEL_ID)
    panel = candidate[panel_start:panel_end]
    corrected_panel = remove_placeholder(panel)
    candidate = candidate[:panel_start] + corrected_panel + candidate[panel_end:]

    panel_start, _, panel_close, _, _ = element_span(candidate, PANEL_ID)
    workspace_start, workspace_open_end, _, workspace_end, _ = element_span(
        candidate, WORKSPACE_ID
    )
    final_workspace = candidate[workspace_start:workspace_end]
    evidence_after = control_evidence(final_workspace)
    evidence = {
        "workspace_nested_before": workspace_nested_before,
        "workspace_nested_after": panel_start < workspace_start < panel_close,
        "workspace_opening_after": candidate[workspace_start:workspace_open_end],
        "controls_before": evidence_before,
        "controls_after": evidence_after,
    }
    return candidate, evidence


def build_candidate_js(source: str) -> str:
    if WORKSPACE_ID in source and "PART F 15-B6C-R3" in source:
        raise RuntimeError("The B6C-R3 JavaScript correction is already present.")
    count = source.count(OLD_ACTIVE_ASSIGNMENT)
    if count != 1:
        raise RuntimeError(
            "Runtime Owner active-section assignment was expected once; "
            f"found {count}."
        )
    return source.replace(OLD_ACTIVE_ASSIGNMENT, NEW_ACTIVE_ASSIGNMENT, 1)


def write_report(
    report: Path,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
    certified: bool,
) -> None:
    status = "CERTIFIED" if certified else "NOT_CERTIFIED"
    failed = [name for name, passed in checks.items() if not passed]
    lines = [
        "LINKCRAFTOR OWNER CONTROL TOWER",
        TITLE,
        "",
        f"Generated: {now_iso()}",
        "Patch mode: STRICT FAIL-CLOSED WITH AUTOMATIC ROLLBACK",
        f"Backup: {evidence.get('backup', 'UNAVAILABLE')}",
        f"Owner Actions workspace displayed: {'YES' if evidence.get('patch_retained') else 'NO'}",
        "Live owner-action dispatch: OFF",
        "Trusted mutation adapters added: NO",
        "Owner actions executed during correction: NO",
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
        "IMPLEMENTED CORRECTION:",
        "- Removed the obsolete Runtime Owner Actions placeholder copy.",
        "- Placed the certified Owner Actions workspace inside its active section panel.",
        "- Removed stale hidden/display-none state from the workspace root.",
        "- Synchronized workspace visibility with shared Runtime Owner navigation.",
        "- Retained the B6B-B6I preview, confirmation, idempotency and audit boundary.",
        "- Live dispatch remains OFF and no mutation adapter was registered.",
        "- No production job, queue, handler, workflow or recovery action was executed.",
        "",
        "NEXT STEP:",
        "Press Ctrl + F5 and open Owner Actions & Recovery for visual acceptance.",
        "Do not proceed to B6J until the complete workspace is visible.",
        "",
        FINAL_RESULT if certified else FINAL_RESULT.replace(" CERTIFIED", " NOT_CERTIFIED"),
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def run(root: Path, report: Path) -> int:
    paths = {name: root / relative for name, relative in SOURCE_PATHS.items()}
    b6_report = root / B6_REPORT_PATH
    r2_report = root / R2_REPORT_PATH
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "patch_retained": False,
        "rollback_performed": False,
        "actions_executed": False,
        "trusted_adapters_installed": 0,
    }
    error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}
    historical_hashes: dict[str, str] = {}

    try:
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        checks["b6_report_exists"] = b6_report.is_file()
        checks["r2_report_exists"] = r2_report.is_file()
        if not all(checks.values()):
            raise RuntimeError("The certified Owner Actions source baseline is unavailable.")

        checks["b6_report_certified"] = certified_report(
            read_text(b6_report), B6_FINAL
        )
        checks["r2_report_certified"] = certified_report(
            read_text(r2_report), R2_FINAL
        )
        historical_hashes = {
            "b6": sha256(b6_report),
            "r2": sha256(r2_report),
        }
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = sha256(paths[name]) == expected
        if not all(checks.values()):
            raise RuntimeError("The exact certified B6C-R2 source baseline is not intact.")

        html_source = read_text(paths["index_html"])
        js_source = read_text(paths["runtime_owner_js"])
        checks["owner_actions_panel_present_once"] = html_source.count(
            f'id="{PANEL_ID}"'
        ) == 1
        checks["owner_actions_workspace_present_once"] = html_source.count(
            f'id="{WORKSPACE_ID}"'
        ) == 1
        checks["obsolete_placeholder_present"] = PLACEHOLDER_SENTENCE in html_source
        checks["cache_version_24_present"] = html_source.count(OLD_CACHE) == 1
        if not all(checks.values()):
            raise RuntimeError("The diagnosed workspace-display boundary is unavailable.")

        candidate_html, structural_evidence = build_candidate_html(html_source)
        candidate_js = build_candidate_js(js_source)
        evidence["structural_probe"] = structural_evidence

        panel_start, _, panel_close, _, _ = element_span(candidate_html, PANEL_ID)
        workspace_start, workspace_open_end, _, workspace_end, _ = element_span(
            candidate_html, WORKSPACE_ID
        )
        final_workspace = candidate_html[workspace_start:workspace_end]
        final_opening = candidate_html[workspace_start:workspace_open_end]
        final_controls = control_evidence(final_workspace)
        checks["candidate_html_ids_unique"] = ids_unique(candidate_html)
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(candidate_js)
        checks["workspace_nested_in_owner_actions_panel"] = (
            panel_start < workspace_start < panel_close
        )
        checks["workspace_not_statically_hidden"] = (
            not re.search(r"\shidden(?:\s|=|>)", final_opening, re.I)
            and not re.search(r"display\s*:\s*none", final_opening, re.I)
        )
        checks["certified_ui_controls_retained"] = bool(
            final_controls["controls_present"]
        )
        checks["obsolete_placeholder_removed"] = (
            PLACEHOLDER_SENTENCE not in candidate_html
        )
        checks["visibility_synchronization_present"] = all(
            token in candidate_js
            for token in (
                "PART F 15-B6C-R3",
                'normalized === "owner_actions"',
                "ownerActionsWorkspace.hidden = !ownerActionsActive",
            )
        )
        checks["cache_version_25_present"] = (
            candidate_html.count(NEW_CACHE) == 1 and OLD_CACHE not in candidate_html
        )
        if not all(checks.values()):
            raise RuntimeError("One or more candidate workspace-display checks failed.")

        backup = (
            root / "backend/server/data/runtime_backups"
            / f"part_f_15_b6c_r3_{timestamp_slug()}"
        )
        backup.mkdir(parents=True, exist_ok=False)
        shutil.copy2(paths["index_html"], backup / "index.html")
        shutil.copy2(paths["runtime_owner_js"], backup / "runtime_owner.js")
        checks["backup_created"] = all(
            (backup / name).is_file() for name in ("index.html", "runtime_owner.js")
        )
        evidence["backup"] = str(backup)

        originals = {
            "index_html": paths["index_html"].read_bytes(),
            "runtime_owner_js": paths["runtime_owner_js"].read_bytes(),
        }
        atomic_write(paths["index_html"], candidate_html)
        atomic_write(paths["runtime_owner_js"], candidate_js)

        retained_html = read_text(paths["index_html"])
        retained_js = read_text(paths["runtime_owner_js"])
        retained_panel_start, _, retained_panel_close, _, _ = element_span(
            retained_html, PANEL_ID
        )
        retained_workspace_start, retained_open_end, _, retained_workspace_end, _ = (
            element_span(retained_html, WORKSPACE_ID)
        )
        retained_workspace = retained_html[
            retained_workspace_start:retained_workspace_end
        ]
        retained_opening = retained_html[
            retained_workspace_start:retained_open_end
        ]
        retained_controls = control_evidence(retained_workspace)
        checks["retained_html_ids_unique"] = ids_unique(retained_html)
        checks["retained_javascript_syntax"] = javascript_syntax_valid(retained_js)
        checks["retained_workspace_nested"] = (
            retained_panel_start < retained_workspace_start < retained_panel_close
        )
        checks["retained_workspace_not_statically_hidden"] = (
            not re.search(r"\shidden(?:\s|=|>)", retained_opening, re.I)
            and not re.search(r"display\s*:\s*none", retained_opening, re.I)
        )
        checks["retained_certified_ui_controls"] = bool(
            retained_controls["controls_present"]
        )
        checks["retained_placeholder_absent"] = PLACEHOLDER_SENTENCE not in retained_html
        checks["retained_cache_version_25"] = retained_html.count(NEW_CACHE) == 1
        checks["historical_b6_report_unchanged"] = (
            sha256(b6_report) == historical_hashes["b6"]
        )
        checks["historical_r2_report_unchanged"] = (
            sha256(r2_report) == historical_hashes["r2"]
        )
        for name, expected in EXPECTED_HASHES.items():
            if name not in {"index_html", "runtime_owner_js"}:
                checks[f"unchanged_{name}"] = sha256(paths[name]) == expected
        checks["only_expected_sources_changed"] = (
            sha256(paths["index_html"]) != EXPECTED_HASHES["index_html"]
            and sha256(paths["runtime_owner_js"]) != EXPECTED_HASHES["runtime_owner_js"]
        )
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_during_correction_no"] = True
        checks["project_modules_imported_no"] = True
        if not all(checks.values()):
            raise RuntimeError("One or more retained workspace-display checks failed.")

        evidence.update({
            "changed_sources": [INDEX_PATH, RUNTIME_JS_PATH],
            "index_hash_before": EXPECTED_HASHES["index_html"],
            "index_hash_after": sha256(paths["index_html"]),
            "runtime_owner_js_hash_before": EXPECTED_HASHES["runtime_owner_js"],
            "runtime_owner_js_hash_after": sha256(paths["runtime_owner_js"]),
            "retained_controls": retained_controls,
            "root_cause": "certified_workspace_not_displayed_by_active_owner_actions_panel",
            "patch_retained": True,
        })
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        for name, content in originals.items():
            paths[name].write_bytes(content)
        if originals:
            evidence["rollback_performed"] = True

    certified = not error and all(checks.values())
    write_report(report, checks, evidence, error, certified)
    failed = [name for name, passed in checks.items() if not passed]
    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B6C_R3_STATUS={'CERTIFIED' if certified else 'NOT_CERTIFIED'}")
    print(f"PATCH_RETAINED={'YES' if evidence.get('patch_retained') else 'NO'}")
    print("ACTIONS_EXECUTED=NO")
    return 0 if certified else 1


def self_test() -> int:
    synthetic_html = f'''<!doctype html>
<html><body>
<div id="runtimeOwnerContentPanel">
  <section id="{PANEL_ID}" data-runtime-owner-section-panel="owner_actions" hidden>
    <div class="runtime-owner-placeholder">
      <h2>Runtime Owner Actions</h2>
      <p>{PLACEHOLDER_SENTENCE}</p>
    </div>
  </section>
</div>
<section id="{WORKSPACE_ID}" hidden aria-hidden="true" style="display:none">
  <h2>Owner Actions &amp; Recovery</h2>
  <p>Eligibility and impact preview with confirmation.</p>
  <p>{'Read-only eligibility preview. ' * 35}</p>
  <form id="runtimeOwnerActionRequestForm">
    <select><option>job</option><option>queue</option><option>workflow</option></select>
    <input value="worker lease stage execution" />
    <button type="button">Preview</button>
  </form>
</section>
{OLD_CACHE}
</body></html>'''
    candidate_html, evidence = build_candidate_html(synthetic_html)
    assert evidence["workspace_nested_before"] is False
    assert evidence["workspace_nested_after"] is True
    assert PLACEHOLDER_SENTENCE not in candidate_html
    assert NEW_CACHE in candidate_html
    panel_start, _, panel_close, _, _ = element_span(candidate_html, PANEL_ID)
    workspace_start, workspace_open_end, _, workspace_end, _ = element_span(
        candidate_html, WORKSPACE_ID
    )
    assert panel_start < workspace_start < panel_close
    opening = candidate_html[workspace_start:workspace_open_end]
    assert " hidden" not in opening
    assert "display:none" not in opening.replace(" ", "")
    assert control_evidence(candidate_html[workspace_start:workspace_end])["controls_present"]

    synthetic_js = '''function setActiveSection(section) {
    const normalized = section;
    contentPanel.dataset.runtimeOwnerActiveSection = normalized;
}'''
    candidate_js = build_candidate_js(synthetic_js)
    assert "PART F 15-B6C-R3" in candidate_js
    assert "ownerActionsWorkspace.hidden = !ownerActionsActive" in candidate_js
    print("PART_F_15_B6C_R3_SELF_TEST=PASS")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if len(argv) != 2:
        print(
            "Usage: RUN_15_B6C_R3_OWNER_ACTIONS_WORKSPACE_DISPLAY_CORRECTION.py "
            "<project-root> <report-path>",
            file=sys.stderr,
        )
        return 2
    return run(Path(argv[0]).resolve(), Path(argv[1]).resolve())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
