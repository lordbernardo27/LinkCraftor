"""Source-only Step 13-A inspection. No project module is imported or executed.

Usage: python _part_e_13_a_activation_boundary_inspection.py PROJECT_ROOT REPORT
Writes only its inspection report and an optional previous-report backup.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
import traceback
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

REPORT_NAME = "PART_E_13_A_COLLECTIVE_PIPELINE_ACTIVATION_BOUNDARY_INSPECTION.txt"
PART_D_REPORT_NAME = "PART_D_12_C_FINAL_CONNECTED_DOMAIN_PIPELINE_COORDINATION_CERTIFICATION.txt"
STAGES = (
    "connect_domain", "site_sources", "url_cleaner", "site_pages",
    "live_domain_target_pool", "active_target_set",
)
JOBS = tuple(stage + "_stage" for stage in STAGES)
HANDLERS = (
    "execute_connect_domain_stage", "execute_site_sources_stage", "execute_url_cleaner_stage",
    "build_site_pages", "build_live_domain_target_pool", "build_active_target_set",
)
AUTHORITY_SOURCES = {
    "coordinator": "backend/server/pipelines/connect_domain/coordinator.py",
    "manifest": "backend/server/pipelines/connect_domain/manifest.py",
    "runtime_coordination_gateway": "backend/server/runtime/runtime_coordination_gateway.py",
    "runtime_execution_gateway": "backend/server/coordination/runtime_integration/runtime_execution_gateway.py",
    "runtime_application_lifecycle": "backend/server/runtime/runtime_application_lifecycle.py",
    "runtime_registration": "backend/server/runtime/universal_runtime_registration.py",
    "coordinator_contract": "backend/server/coordination/pipeline_coordinators/contract.py",
    "workflow_contract": "backend/server/coordination/universal_workflows/contract.py",
    "workflow_repository": "backend/server/coordination/workflow_persistence/repository.py",
    "workflow_registry": "backend/server/coordination/workflow_registry/registry.py",
    "coordinator_registry": "backend/server/coordination/coordinator_registry/registry.py",
    "workflow_job_correlation": "backend/server/coordination/runtime_integration/workflow_job_correlation.py",
    "runtime_job_mapping": "backend/server/coordination/runtime_integration/runtime_job_mapping.py",
    "coordination_runtime_bridge": "backend/server/coordination/runtime_integration/coordination_runtime_bridge.py",
    "stage_result_processor": "backend/server/coordination/stage_handoff/stage_result_processor.py",
    "job_submission": "backend/server/runtime/universal_job_submission.py",
    "job_creation": "backend/server/runtime/universal_jobs/creation_engine.py",
    "job_store": "backend/server/orchestration/job_store.py",
    "runtime_worker": "backend/server/runtime/universal_runtime_worker_v1.py",
    "runtime_boot": "backend/server/runtime/runtime_boot_process.py",
}
WATCHED_CALLS = {
    "coordinate_connect_domain_pipeline", "connect_connected_domain_to_universal_coordination",
    "build_connected_domain_pipeline_manifest", "submit_workflow_execution",
    "apply_runtime_terminal_lifecycle", "intake_runtime_terminal_stage_result",
    "run_connect_domain", "save_workflow", "load_workflow", "UniversalWorkflow",
    "register_connected_domain_coordinator", "register_workflow",
}
CONTRACT_SOURCE_NAMES = WATCHED_CALLS | set(HANDLERS) | {
    "save_active_target_set", "load_active_target_set", "save_live_domain_target_pool",
    "load_live_domain_target_pool", "save_site_pages", "load_site_pages",
    "dispatch_registered_runtime_handler", "create_runtime_handoff_context",
    "map_runtime_handoffs_to_job_requests", "submit_runtime_execution_wave",
    "submit_runtime_job_mapping", "submit_universal_job", "to_dict", "to_canonical_dict",
    "load_workflow_record", "workflow_registry_snapshot", "coordinator_registry_snapshot",
    "get_orchestration_job", "list_job_events", "load_jobs", "process_stage_result",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section(text: str, name: str) -> Any:
    match = re.search(r"(?m)^" + re.escape(name) + r":?[ \t]*\n(?:=+[ \t]*\n)?", text)
    if match is None:
        raise ValueError("Missing report section: " + name)
    return json.JSONDecoder().raw_decode(text[match.end():].lstrip())[0]


def dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        left = dotted(node.value)
        return left + "." + node.attr if left else node.attr
    return ""


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    result = "(" + ast.unparse(node.args) + ")"
    if node.returns is not None:
        result += " -> " + ast.unparse(node.returns)
    return result


def imports(tree: ast.Module) -> dict[str, str]:
    result = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                result[alias.asname or alias.name] = (node.module or "") + "." + alias.name
        elif isinstance(node, ast.Import):
            for alias in node.names:
                result[alias.asname or alias.name] = alias.name
    return result


def calls(node: ast.AST, aliases: Mapping[str, str]) -> list[dict[str, Any]]:
    result = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        name = dotted(child.func)
        root, _, rest = name.partition(".")
        resolved = aliases.get(root, root) + (("." + rest) if rest else "")
        result.append({
            "name": name, "resolved": resolved, "line": child.lineno,
            "keyword_arguments": [kw.arg or "**kwargs" for kw in child.keywords],
        })
    return result


def inventory(path: Path) -> dict[str, Any]:
    source = read(path)
    tree = ast.parse(source, filename=str(path))
    aliases = imports(tree)
    functions = {}
    classes = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            entry = {"signature": signature(node), "calls": calls(node, aliases)}
            if node.name in CONTRACT_SOURCE_NAMES:
                entry["source"] = ast.get_source_segment(source, node)
            functions[node.name] = entry
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            class_fields = [
                {"name": child.target.id, "annotation": ast.unparse(child.annotation),
                 "default": ast.unparse(child.value) if child.value is not None else "<required>"}
                for child in node.body if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name)
            ]
            methods = {}
            for method in node.body:
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and not method.name.startswith("_"):
                    details = {"signature": signature(method), "calls": calls(method, aliases)}
                    if method.name in CONTRACT_SOURCE_NAMES:
                        details["source"] = ast.get_source_segment(source, method)
                    methods[method.name] = details
            classes[node.name] = {
                "bases": [ast.unparse(base) for base in node.bases], "fields": class_fields,
                "decorators": [ast.unparse(item) for item in node.decorator_list], "methods": methods,
            }
    return {"path": str(path), "sha256": sha(path), "imports": aliases, "functions": functions, "classes": classes}


def canonical_stage_path(root: Path, stage: str) -> Path:
    folder = root / "backend/server/pipelines/connect_domain"
    return folder / "stage.py" if stage == "connect_domain" else folder / "linking_target_pipeline" / stage / "stage.py"


def stage_input_evidence(entry: Mapping[str, Any], handler: str) -> Mapping[str, Any]:
    source = entry["functions"].get(handler, {}).get("source")
    if not source:
        return {"handler": handler, "available": False}
    node = ast.parse(source).body[0]
    positional = node.args.posonlyargs + node.args.args
    required_positional = positional[:len(positional) - len(node.args.defaults)]
    required_kwonly = [argument for argument, default in zip(node.args.kwonlyargs, node.args.kw_defaults) if default is None]
    return {
        "handler": handler, "available": True,
        "required_parameters": [argument.arg for argument in required_positional + required_kwonly],
        "all_parameters": [argument.arg for argument in positional + node.args.kwonlyargs],
        "signature": signature(node),
    }


class ReadOnlyGuard:
    def __init__(self, report: Path) -> None:
        self.report = report.resolve()
        self.output_paths = {self.report}
        self.writing_report = False
        self.active = True
        self.denied: list[dict[str, str]] = []

    def reject(self, event: str, detail: Any) -> None:
        self.denied.append({"event": event, "detail": str(detail)})
        raise RuntimeError("Source-only inspection denied " + event + ": " + str(detail))

    def audit(self, event: str, args: tuple[Any, ...]) -> None:
        if not self.active:
            return
        if event == "import" and str(args[0]).startswith("backend"):
            self.reject("project_import", args[0])
        elif event == "open":
            path, mode, flags = args
            writing = bool(
                isinstance(mode, str) and any(token in mode for token in "wax+")
                or isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
            )
            if writing:
                allowed = bool(self.writing_report and isinstance(path, (str, bytes, os.PathLike))
                               and Path(os.fsdecode(path)).resolve() in self.output_paths)
                if not allowed:
                    self.reject("file_write", path)
        elif event in {
            "os.mkdir", "os.remove", "os.rmdir", "os.rename", "os.link", "os.symlink", "os.truncate",
            "os.chmod", "os.utime", "shutil.copyfile", "socket.connect", "socket.bind",
            "socket.getaddrinfo", "socket.sendto", "subprocess.Popen", "os.system", "sqlite3.connect",
        }:
            self.reject(event, args[:2])


def candidates(root: Path) -> tuple[list[Path], list[str]]:
    server = root / "backend/server"
    selected: set[Path] = set()
    excluded = []
    archive_parts = {"data", "runtime_backups", "backups", "__pycache__", ".venv", ".git"}
    # Only API/route modules, this pipeline and runtime source are searched, not the data tree.
    if (server / "main.py").is_file():
        selected.add(server / "main.py")
    for scoped in ("api", "routes", "routers", "runtime", "pipelines/connect_domain"):
        base = server / scoped
        if not base.is_dir() or base.is_symlink():
            continue
        for parent, folders, filenames in os.walk(base, followlinks=False):
            directory = Path(parent)
            kept = []
            for folder in folders:
                child = directory / folder
                if folder in archive_parts or child.is_symlink():
                    excluded.append(str(child.relative_to(server)))
                else:
                    kept.append(folder)
            folders[:] = kept
            for filename in filenames:
                path = directory / filename
                if path.suffix != ".py":
                    continue
                if path.is_symlink() or "_before_" in path.stem:
                    excluded.append(str(path.relative_to(server)))
                else:
                    selected.add(path)
    return sorted(selected), excluded


def main(root: Path, report: Path) -> int:
    reports = root / "backend/server/data/reports"
    if report.resolve() != (reports / REPORT_NAME).resolve() or not reports.is_dir():
        print("Use the canonical reports directory and 13-A report filename.", file=sys.stderr)
        return 2
    checks: dict[str, bool | None] = dict.fromkeys((
        "part_d_report_exists", "part_d_collective_certification_valid", "part_d_sources_match_current",
        "all_required_authority_sources_read", "all_six_stage_sources_read", "all_six_handlers_found",
        "stage_contract_extraction_complete", "route_and_activation_source_search_complete",
        "published_runtime_registry_file_exists", "runtime_registry_json_valid",
        "six_stage_registration_contracts_available", "payload_handoff_matrix_created",
        "source_files_unchanged", "historical_certificate_unchanged", "registry_file_unchanged",
        "no_project_modules_imported", "no_forbidden_side_effects_attempted",
    ), None)
    evidence: dict[str, Any] = {}
    findings: list[dict[str, Any]] = []
    execution_error: dict[str, str] = {}
    hashes: dict[Path, str] = {}
    guard = ReadOnlyGuard(report)
    sys.addaudithook(guard.audit)
    prior_modules = {name for name in sys.modules if name == "backend" or name.startswith("backend.")}
    try:
        certificate = reports / PART_D_REPORT_NAME
        checks["part_d_report_exists"] = certificate.is_file()
        if not certificate.is_file():
            raise FileNotFoundError(str(certificate))
        certificate_sha = sha(certificate)
        text = read(certificate)
        prior_checks = section(text, "CHECKS")
        checks["part_d_collective_certification_valid"] = bool(
            re.search(r"(?m)^CERTIFICATION STATUS:\s*CERTIFIED\s*$", text)
            and re.search(r"(?m)^FINAL RESULT:\s*PART D CONNECTED DOMAIN PIPELINE COORDINATION CERTIFIED\s*$", text)
            and isinstance(prior_checks, dict) and prior_checks and all(value is True for value in prior_checks.values())
            and section(text, "FAILED_CHECKS") == [] and section(text, "NOT_RUN_CHECKS") == []
            and section(text, "EXECUTION_ERROR") == {}
        )
        prior = section(text, "COLLECTIVE EVIDENCE")
        evidence["part_d_certificate"] = {"path": str(certificate), "sha256": certificate_sha}
        mismatches = {}
        for name, expected in prior["source_hashes"].items():
            relative = AUTHORITY_SOURCES.get(name)
            if relative is None:
                raise ValueError("Unrecognized Part D source identity: " + name)
            path = root / relative
            actual = sha(path) if path.is_file() else None
            if actual != expected:
                mismatches[name] = {"expected": expected, "actual": actual}
        checks["part_d_sources_match_current"] = not mismatches
        evidence["part_d_source_mismatches"] = mismatches
        if not checks["part_d_collective_certification_valid"] or mismatches:
            raise RuntimeError("The certified Part D source boundary changed or its certificate is incomplete.")

        authorities = {}
        for name, relative in AUTHORITY_SOURCES.items():
            path = root / relative
            authorities[name] = inventory(path)
            hashes[path] = authorities[name]["sha256"]
        checks["all_required_authority_sources_read"] = True
        stages = {}
        for stage, handler in zip(STAGES, HANDLERS):
            path = canonical_stage_path(root, stage)
            entry = inventory(path)
            hashes[path] = entry["sha256"]
            repository = path.with_name("repository.py")
            repository_entry = inventory(repository) if repository.is_file() else None
            if repository_entry:
                hashes[repository] = repository_entry["sha256"]
            stages[stage] = {"stage": entry, "repository": repository_entry,
                             "input_contract": stage_input_evidence(entry, handler)}
        checks["all_six_stage_sources_read"] = len(stages) == 6
        checks["all_six_handlers_found"] = all(stages[stage]["input_contract"]["available"] for stage in STAGES)
        checks["stage_contract_extraction_complete"] = checks["all_six_handlers_found"]

        registry_path = Path(prior["registry_file_published"])
        if not registry_path.is_absolute():
            registry_path = root / registry_path
        registry_path = registry_path.resolve()
        if not registry_path.is_relative_to(root):
            raise RuntimeError("Published runtime registry is outside the selected project; not inspected.")
        checks["published_runtime_registry_file_exists"] = registry_path.is_file()
        registry_sha = sha(registry_path)
        registry_document = json.loads(read(registry_path))
        checks["runtime_registry_json_valid"] = isinstance(registry_document, (dict, list))
        found: dict[str, list[dict[str, Any]]] = {job: [] for job in JOBS}

        def visit(value: Any) -> None:
            if isinstance(value, dict):
                job = value.get("job_type")
                if isinstance(job, str) and job in found and "handler_ref" in value:
                    found[job].append(value)
                for item in value.values():
                    if isinstance(item, (dict, list)):
                        visit(item)
            elif isinstance(value, list):
                for item in value:
                    visit(item)

        visit(registry_document)
        prior_references = prior["connection_result"]["stage_references"]
        registration_contracts = {}
        for stage, job in zip(STAGES, JOBS):
            records = found[job]
            if len(records) == 1:
                registration_contracts[stage] = {
                    key: records[0].get(key) for key in (
                        "job_type", "pipeline", "stage", "handler_ref", "required_payload_fields",
                        "predecessor_stages", "successor_stages", "registration_fingerprint", "persistent",
                    )
                }
                registration_contracts[stage]["evidence_source"] = "current_persisted_registry"
            else:
                reference = prior_references[stage]
                registration_contracts[stage] = {
                    "job_type": job, "stage": stage,
                    "required_payload_fields": reference["required_payload_fields"],
                    "handler_ref": reference.get("metadata", {}).get("handler_ref"),
                    "evidence_source": "Part_D_certificate_snapshot",
                    "current_registry_candidate_count": len(records),
                }
                findings.append({"type": "registry_shape_requires_review", "stage": stage,
                                 "candidate_count": len(records), "is_activation_blocker": True})
        checks["six_stage_registration_contracts_available"] = len(registration_contracts) == 6

        intent_payloads = prior["connection_result"]["intent"]["payload_by_stage"]
        handoffs = []
        for index, stage in enumerate(STAGES):
            required = registration_contracts[stage].get("required_payload_fields") or []
            keys = sorted(intent_payloads.get(stage, {}))
            missing = [key for key in required if key not in intent_payloads.get(stage, {})]
            handoffs.append({
                "stage": stage, "predecessor": STAGES[index - 1] if index else None,
                "registered_required_payload_fields": required, "base_intent_payload_keys": keys,
                "required_fields_not_in_base_intent": missing,
                "stage_function_inputs": stages[stage]["input_contract"],
                "interpretation": "Missing downstream fields may be supplied by predecessor output or hydration; this is not proof of a defective stage.",
            })
            if missing:
                findings.append({"type": "runtime_payload_hydration_needs_proof", "stage": stage,
                                 "missing_from_base_intent": missing, "is_activation_blocker": True})
        checks["payload_handoff_matrix_created"] = len(handoffs) == 6

        files, excluded = candidates(root)
        call_sites = []
        route_sources = []
        syntax_findings = []
        for path in files:
            source = read(path)
            hashes.setdefault(path, sha(path))
            # Skip parsing modules with no relevant symbol or route string.
            if not any(word in source for word in WATCHED_CALLS) and "connect_domain" not in source:
                continue
            try:
                tree = ast.parse(source, filename=str(path))
            except SyntaxError as exc:
                syntax_findings.append({"path": str(path.relative_to(root)), "error": str(exc)})
                continue
            aliases = imports(tree)
            matched = [item for item in calls(tree, aliases)
                       if item["resolved"].rsplit(".", 1)[-1] in WATCHED_CALLS]
            for item in matched:
                call_sites.append({"path": str(path.relative_to(root)), **item})
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                decorators = [ast.unparse(item) for item in node.decorator_list]
                is_route = any(re.search(r"\.(get|post|put|patch|delete)\(", item) for item in decorators)
                if is_route and ("connect_domain" in ast.get_source_segment(source, node)
                                 or any("connect_domain" in item for item in decorators)):
                    route_sources.append({
                        "path": str(path.relative_to(root)), "function": node.name,
                        "signature": signature(node), "decorators": decorators,
                        "source": ast.get_source_segment(source, node), "calls": calls(node, aliases),
                    })
        checks["route_and_activation_source_search_complete"] = not syntax_findings
        if syntax_findings:
            findings.append({"type": "active_candidate_syntax_requires_review", "items": syntax_findings,
                             "is_activation_blocker": True})
        route_calls = {item["resolved"].rsplit(".", 1)[-1] for route in route_sources for item in route["calls"]}
        if "run_connect_domain" in route_calls:
            findings.append({"type": "legacy_entrypoint_present_in_route", "is_activation_blocker": True,
                             "interpretation": "The route calls the legacy entrypoint. Its complete delegation chain must be reviewed before activation."})
        findings.append({"type": "full_activation_chain_not_executed", "is_activation_blocker": True,
                         "interpretation": "This source-only inspection cannot establish execution readiness. Review persistence, hydration, scheduling and entrypoint findings before controlled validation."})

        checks["source_files_unchanged"] = all(path.is_file() and sha(path) == value for path, value in hashes.items())
        checks["historical_certificate_unchanged"] = sha(certificate) == certificate_sha
        checks["registry_file_unchanged"] = sha(registry_path) == registry_sha
        current_modules = {name for name in sys.modules if name == "backend" or name.startswith("backend.")}
        checks["no_project_modules_imported"] = current_modules == prior_modules
        checks["no_forbidden_side_effects_attempted"] = not guard.denied
        evidence.update({
            "authority_contracts": authorities, "stage_contracts": stages,
            "persisted_registry": {"path": str(registry_path), "sha256": registry_sha,
                                   "top_level_keys": sorted(registry_document) if isinstance(registry_document, dict) else "list"},
            "stage_registration_contracts": registration_contracts,
            "payload_handoff_matrix": handoffs, "activation_call_sites": call_sites,
            "connect_domain_route_sources": route_sources,
            "candidate_source_file_count": len(files), "excluded_archive_count": len(excluded),
            "source_hashes": {str(path.relative_to(root)): value for path, value in hashes.items()},
            "search_limitations": ["Static call-site candidates are not proof of an executable chain.",
                                   "Dynamic resolution and code outside the targeted source namespaces are not exhaustively analysed."],
            "inspection_decision": "REVIEW_FINDINGS_BEFORE_IMPLEMENTATION_OR_ACTIVATION",
            "activation_ready": False,
        })
    except Exception as exc:
        execution_error = {"error_type": type(exc).__name__, "error_message": str(exc), "traceback": traceback.format_exc()}

    failed = sorted(name for name, value in checks.items() if value is False)
    not_run = sorted(name for name, value in checks.items() if value is None)
    complete = not failed and not not_run and not execution_error and not guard.denied
    status = "COMPLETE" if complete else "NOT_COMPLETE"
    lines = [
        "LINKCRAFTOR PIPELINE VALIDATION AND ACTIVATION",
        "PART E 13-A COLLECTIVE PIPELINE ACTIVATION BOUNDARY INSPECTION", "",
        "Generated: " + datetime.now(timezone.utc).isoformat(), "Mode: READ-ONLY SOURCE AND CONTRACT INSPECTION",
        "Project modules imported or executed: NO", "Production activation: NOT PERFORMED",
        "Production Universal Jobs created: NO", "Production queue claims executed: NO",
        "Production handlers executed: NO", "Live network requests executed: NO",
        "INSPECTION STATUS: " + status, "",
        "Decision: REVIEW_FINDINGS_BEFORE_IMPLEMENTATION_OR_ACTIVATION",
        "Inspection completion does not mean the pipeline is ready or activated.", "",
        "=" * 110, "CHECKS", "=" * 110, json.dumps(checks, indent=2, sort_keys=True),
        "", "FAILED_CHECKS:", json.dumps(failed, indent=2), "", "NOT_RUN_CHECKS:", json.dumps(not_run, indent=2),
        "", "=" * 110, "FINDINGS", "=" * 110, json.dumps(findings, indent=2),
        "", "=" * 110, "BOUNDARY AND CONTRACT EVIDENCE", "=" * 110, json.dumps(evidence, indent=2, sort_keys=True),
        "", "EXECUTION_ERROR:", json.dumps(execution_error, indent=2),
        "", "DENIED_OPERATIONS:", json.dumps(guard.denied, indent=2),
        "", "NEXT STEP:", "Review this evidence and identify the smallest missing canonical connection before any patch or activation.",
        "", "FINAL RESULT: PART E 13-A " + status, "",
    ]
    guard.writing_report = True
    try:
        if report.exists():
            backup = report.with_name(report.name + ".before_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
            guard.output_paths.add(backup.resolve())
            with backup.open("xb") as handle:
                handle.write(report.read_bytes())
        report.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    finally:
        guard.writing_report = False
    for name, value in checks.items():
        print(name.upper() + ": " + ("PASS" if value is True else "FAIL" if value is False else "NOT_RUN"))
    print("FAILED_CHECK_COUNT=" + str(len(failed)))
    print("NOT_RUN_CHECK_COUNT=" + str(len(not_run)))
    print("FINDING_COUNT=" + str(len(findings)))
    print("ACTIVATION_PERFORMED=NO")
    print("REPORT=" + str(report))
    print("PART_E_13_A_STATUS=" + status)
    return 0 if complete else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python _part_e_13_a_activation_boundary_inspection.py PROJECT_ROOT REPORT")
    raise SystemExit(main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()))
