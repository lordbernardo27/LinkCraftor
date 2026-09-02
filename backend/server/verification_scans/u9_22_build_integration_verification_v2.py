from __future__ import annotations

import ast
import importlib
import py_compile
from pathlib import Path

print("=== U9.22 BUILD / INTEGRATION VERIFICATION V2 ===")

checks: list[tuple[str, bool]] = []


def check(name: str, condition: bool) -> None:
    value = bool(condition)
    checks.append((name, value))
    print(f"{name}={value}")


def import_check(name: str, module_name: str) -> None:
    try:
        importlib.import_module(module_name)
        ok = True
    except Exception as exc:
        ok = False
        print(f"{name}_ERROR_TYPE={type(exc).__name__}")
        print(f"{name}_ERROR={exc}")

    check(name, ok)


print()
print("=== A. COMPILE U9 PRODUCTION MODULES ===")

compile_targets = [
    "backend/server/pipelines/upload_document/coordinator.py",
    "backend/server/stores/uploaded_document_unified_content.py",
    "backend/server/universal_unified_content_document/uucd_engine_v1.py",
    "backend/server/universal_unified_content_document/uucd_persistence_v1.py",
    "backend/server/universal_unified_content_document/__init__.py",
    "backend/server/universal_article_body_store/body_store_writer_v1.py",
    "backend/server/universal_article_body_store/body_store_repository_v1.py",
    "backend/server/runtime/uucd_runtime_handoff_v1.py",
    "backend/server/runtime/uucd_runtime_handoff_registration_v1.py",
    "backend/server/jobs/universal_knowledge_orchestrator.py",
    "backend/server/website_unified_content/website_unified_content_engine_v1.py",
]

for target in compile_targets:
    name = (
        "COMPILE_OK__"
        + target.replace("/", "__").replace("\\", "__").replace(".", "_")
    )

    try:
        py_compile.compile(target, doraise=True)
        ok = True
    except Exception as exc:
        ok = False
        print(f"{name}_ERROR_TYPE={type(exc).__name__}")
        print(f"{name}_ERROR={exc}")

    check(name, ok)


print()
print("=== B. PROTECTED MODULE IMPORTS ===")

imports = {
    "UDUC_IMPORT_OK":
        "backend.server.stores.uploaded_document_unified_content",

    "UUCD_ENGINE_IMPORT_OK":
        "backend.server.universal_unified_content_document.uucd_engine_v1",

    "UUCD_PERSISTENCE_IMPORT_OK":
        "backend.server.universal_unified_content_document.uucd_persistence_v1",

    "UUCD_PACKAGE_IMPORT_OK":
        "backend.server.universal_unified_content_document",

    "BODY_STORE_WRITER_IMPORT_OK":
        "backend.server.universal_article_body_store.body_store_writer_v1",

    "BODY_STORE_REPOSITORY_IMPORT_OK":
        "backend.server.universal_article_body_store.body_store_repository_v1",

    "RUNTIME_HANDOFF_IMPORT_OK":
        "backend.server.runtime.uucd_runtime_handoff_v1",

    "RUNTIME_REGISTRATION_IMPORT_OK":
        "backend.server.runtime.uucd_runtime_handoff_registration_v1",

    "UPLOAD_COORDINATOR_IMPORT_OK":
        "backend.server.pipelines.upload_document.coordinator",

    "UNIVERSAL_KNOWLEDGE_ORCHESTRATOR_IMPORT_OK":
        "backend.server.jobs.universal_knowledge_orchestrator",

    "WEBSITE_UNIFIED_CONTENT_IMPORT_OK":
        "backend.server.website_unified_content.website_unified_content_engine_v1",
}

for name, module_name in imports.items():
    import_check(name, module_name)


print()
print("=== C. UPLOADED DOCUMENT COORDINATOR AST WIRING ===")

coordinator_path = Path(
    "backend/server/pipelines/upload_document/coordinator.py"
)

coordinator_source = coordinator_path.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(coordinator_source)

builder_name = "build_transient_uucd_from_uduc_v1"

builder_calls = [
    node
    for node in ast.walk(tree)
    if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Name)
    and node.func.id == builder_name
]

check(
    "UUCD_BUILDER_IMPORT_PRESENT",
    builder_name in coordinator_source,
)

check(
    "UUCD_BUILDER_CALL_COUNT_EXACTLY_ONE",
    len(builder_calls) == 1,
)

check(
    "UUCD_BUILDER_RECEIVES_CANONICAL_UDUC",
    (
        len(builder_calls) == 1
        and len(builder_calls[0].args) >= 1
        and isinstance(builder_calls[0].args[0], ast.Name)
        and builder_calls[0].args[0].id == "uduc"
    ),
)

builder_line = (
    builder_calls[0].lineno
    if len(builder_calls) == 1
    else -1
)

uduc_assignment_lines = []

for node in ast.walk(tree):
    if not isinstance(node, ast.Assign):
        continue

    if not any(
        isinstance(target, ast.Name)
        and target.id == "uduc"
        for target in node.targets
    ):
        continue

    uduc_assignment_lines.append(node.lineno)

uduc_line = (
    min(uduc_assignment_lines)
    if uduc_assignment_lines
    else -1
)

check(
    "UDUC_BEFORE_UUCD",
    (
        uduc_line > 0
        and builder_line > uduc_line
    ),
)


def call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id

    if isinstance(node.func, ast.Attribute):
        return node.func.attr

    return ""


call_entries = [
    (
        node.lineno,
        call_name(node),
    )
    for node in ast.walk(tree)
    if isinstance(node, ast.Call)
]

post_builder_calls = [
    (
        line,
        name,
    )
    for line, name in call_entries
    if line > builder_line
]

highlight_candidates = [
    line
    for line, name in post_builder_calls
    if "highlight" in name.lower()
]

registry_candidates = [
    line
    for line, name in post_builder_calls
    if (
        "registry" in name.lower()
        or "active_target" in name.lower()
        or "ats" == name.lower()
    )
]

check(
    "UUCD_BEFORE_HIGHLIGHT",
    (
        builder_line > 0
        and bool(highlight_candidates)
        and min(highlight_candidates) > builder_line
    ),
)

check(
    "UUCD_BEFORE_REGISTRY",
    (
        builder_line > 0
        and bool(registry_candidates)
        and min(registry_candidates) > builder_line
    ),
)

check(
    "READY_FOR_BODY_STORE_GATE_PRESENT",
    '"READY_FOR_BODY_STORE"' in coordinator_source,
)

check(
    "U9_EXECUTION_ORDER_ENTRY_PRESENT",
    "uploaded_document_to_current_canonical_uucd"
    in coordinator_source,
)


print()
print("=== D. INGESTION ENDPOINT BOUNDARY ===")

forbidden_tokens = {
    "COORDINATOR_BODY_STORE_WRITE_PRESENT":
        "write_verified_body_from_envelope_v1",

    "COORDINATOR_UUCD_PERSISTENCE_PRESENT":
        "persist_finalized_uucd_v1",

    "COORDINATOR_RUNTIME_HANDOFF_PRESENT":
        "handoff_persisted_uucd_to_runtime_v1",

    "COORDINATOR_RUNTIME_PAYLOAD_BUILD_PRESENT":
        "build_uucd_runtime_payload_v1",

    "COORDINATOR_UNIVERSAL_JOB_CREATION_PRESENT":
        "create_universal_job",

    "COORDINATOR_ORCHESTRATION_JOB_CREATION_PRESENT":
        "create_orchestration_job",

    "COORDINATOR_SEMANTIC_RUNTIME_PRESENT":
        "semantic_intelligence_runtime_reader",

    "COORDINATOR_SCORER_PRESENT":
        "scorer.py",
}

for name, token in forbidden_tokens.items():
    present = token in coordinator_source

    print(f"{name}={present}")

    check(
        name + "_MUST_BE_FALSE",
        present is False,
    )


print()
print("=== E. REGISTRY / ATS STILL USES UDUC ===")

uduc_passed_to_post_uucd_call = False

for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue

    if node.lineno <= builder_line:
        continue

    name = call_name(node).lower()

    if not (
        "registry" in name
        or "active_target" in name
        or name == "ats"
    ):
        continue

    if any(
        isinstance(arg, ast.Name)
        and arg.id == "uduc"
        for arg in node.args
    ):
        uduc_passed_to_post_uucd_call = True

    for keyword in node.keywords:
        if (
            isinstance(keyword.value, ast.Name)
            and keyword.value.id == "uduc"
        ):
            uduc_passed_to_post_uucd_call = True

check(
    "REGISTRY_ATS_RECEIVES_CANONICAL_UDUC",
    uduc_passed_to_post_uucd_call,
)


print()
print("=== F. LEGACY UUCD CLEANUP STATE ===")

legacy_cert = Path(
    "backend/server/stores/uucd_body_store_certification.py"
)

legacy_rebuild = Path(
    "backend/server/runtime/canonical_environment_rebuild_manager.py"
)

legacy_data = Path(
    "backend/server/data/uucd_body_store_certifications"
)

check(
    "LEGACY_CERT_MODULE_ABSENT",
    not legacy_cert.exists(),
)

check(
    "LEGACY_REBUILD_MANAGER_ABSENT",
    not legacy_rebuild.exists(),
)

check(
    "HISTORICAL_LEGACY_CERT_DATA_PRESERVED",
    legacy_data.exists(),
)


print()
print("=== G. STALE LEGACY PRODUCTION REFERENCES ===")

legacy_patterns = (
    "backend.server.stores.uucd_body_store_certification",
    "certify_uucd_body_store_v1",
    "explain_uucd_body_store_certification_v1",
    "backend.server.runtime.canonical_environment_rebuild_manager",
    "clear_generated_environment",
    "run_canonical_environment_rebuild",
)

stale_matches = []

for path in Path("backend/server").rglob("*.py"):
    rel = path.as_posix()

    if "/backups/" in rel:
        continue
    if "/verification_scans/" in rel:
        continue
    if "/data/" in rel:
        continue
    if "/__pycache__/" in rel:
        continue

    try:
        text = path.read_text(
            encoding="utf-8-sig"
        )
    except UnicodeDecodeError:
        continue

    for pattern in legacy_patterns:
        if pattern in text:
            stale_matches.append(
                f"{rel}::{pattern}"
            )

check(
    "STALE_LEGACY_PRODUCTION_REFERENCE_COUNT_ZERO",
    len(stale_matches) == 0,
)

print(
    "STALE_LEGACY_PRODUCTION_REFERENCES="
    + repr(stale_matches)
)


print()
print("=== H. CIRCULAR IMPORT REGRESSION ===")

repository_path = Path(
    "backend/server/universal_article_body_store/body_store_repository_v1.py"
)

repository_source = repository_path.read_text(
    encoding="utf-8-sig"
)

repository_tree = ast.parse(
    repository_source
)

top_level_writer_import = False
local_writer_import = False

for node in repository_tree.body:
    if isinstance(node, ast.ImportFrom):
        if (
            node.module
            == "backend.server.universal_article_body_store.body_store_writer_v1"
        ):
            top_level_writer_import = True

for node in ast.walk(repository_tree):
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue

    for child in ast.walk(node):
        if (
            isinstance(child, ast.ImportFrom)
            and child.module
            == "backend.server.universal_article_body_store.body_store_writer_v1"
        ):
            local_writer_import = True

check(
    "BODY_STORE_REPOSITORY_NO_TOP_LEVEL_WRITER_IMPORT",
    top_level_writer_import is False,
)

check(
    "BODY_STORE_REPOSITORY_LAZY_WRITER_IMPORT_PRESENT",
    local_writer_import is True,
)


print()
print("=== I. WEBSITE BRANCH PROTECTION ===")

website_path = Path(
    "backend/server/website_unified_content/website_unified_content_engine_v1.py"
)

check(
    "WEBSITE_ENGINE_EXISTS",
    website_path.exists(),
)

check(
    "WEBSITE_ENGINE_NONEMPTY",
    (
        website_path.exists()
        and website_path.stat().st_size > 0
    ),
)


print()
print("=== J. VERIFIER WRITE BOUNDARY ===")

verifier_source = Path(__file__).read_text(
    encoding="utf-8-sig"
)

verifier_tree = ast.parse(
    verifier_source
)

dangerous_runtime_calls = []

dangerous_names = {
    "write_verified_body_from_envelope_v1",
    "persist_finalized_uucd_v1",
    "unlink",
    "rmtree",
}

for node in ast.walk(verifier_tree):
    if not isinstance(node, ast.Call):
        continue

    name = call_name(node)

    if name in dangerous_names:
        dangerous_runtime_calls.append(
            (
                node.lineno,
                name,
            )
        )

check(
    "VERIFIER_HAS_NO_PRODUCTION_DATA_MUTATION_CALLS",
    len(dangerous_runtime_calls) == 0,
)

print(
    "VERIFIER_MUTATION_CALLS="
    + repr(dangerous_runtime_calls)
)


print()
print("=== K. FINAL U9.22 DECISION ===")

passed = sum(
    1
    for _,
    value in checks
    if value
)

failed = [
    name
    for name,
    value in checks
    if not value
]

print(
    "TOTAL_U9_22_CHECKS="
    + str(len(checks))
)

print(
    "TOTAL_U9_22_CHECKS_PASSED="
    + str(passed)
)

print(
    "ALL_U9_22_CHECKS_PASSED="
    + str(not failed)
)

print(
    "FAILED_U9_22_CHECKS="
    + repr(failed)
)

if not failed:
    print(
        "U9.22_NEXT_STEP=CERTIFY_BUILD_INTEGRATION"
    )
else:
    print(
        "U9.22_NEXT_STEP=INVESTIGATE_FAILED_CHECKS"
    )