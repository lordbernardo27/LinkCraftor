from __future__ import annotations

import ast
import importlib
import py_compile
from pathlib import Path

print("=== U9.22 BUILD / INTEGRATION VERIFICATION ===")

ROOT = Path(".")
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
        print(
            f"{name}_ERROR_TYPE={type(exc).__name__}"
        )
        print(
            f"{name}_ERROR={exc}"
        )

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
        + target
        .replace("/", "__")
        .replace("\\", "__")
        .replace(".", "_")
    )

    try:
        py_compile.compile(
            target,
            doraise=True,
        )
        ok = True

    except Exception as exc:
        ok = False
        print(
            f"{name}_ERROR_TYPE={type(exc).__name__}"
        )
        print(
            f"{name}_ERROR={exc}"
        )

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
    import_check(
        name,
        module_name,
    )


print()
print("=== C. UPLOADED DOCUMENT COORDINATOR WIRING ===")

coordinator_path = Path(
    "backend/server/pipelines/upload_document/coordinator.py"
)

coordinator_source = coordinator_path.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    coordinator_source
)

builder_name = "build_transient_uucd_from_uduc_v1"

builder_import_present = (
    builder_name
    in coordinator_source
)

check(
    "UUCD_BUILDER_IMPORT_PRESENT",
    builder_import_present,
)

builder_calls = [
    node
    for node
    in ast.walk(tree)
    if isinstance(
        node,
        ast.Call,
    )
    and isinstance(
        node.func,
        ast.Name,
    )
    and node.func.id
    == builder_name
]

check(
    "UUCD_BUILDER_CALL_COUNT_EXACTLY_ONE",
    len(builder_calls) == 1,
)

check(
    "UUCD_BUILDER_RECEIVES_CANONICAL_UDUC",
    (
        len(builder_calls) == 1
        and len(
            builder_calls[0].args
        ) >= 1
        and isinstance(
            builder_calls[0].args[0],
            ast.Name,
        )
        and builder_calls[0].args[0].id
        == "uduc"
    ),
)


def position(token: str) -> int:
    return coordinator_source.find(
        token
    )


uduc_gate_pos = position(
    'uduc = uduc_result.get("uduc")'
)

uucd_build_pos = position(
    "uucd_envelope = build_transient_uucd_from_uduc_v1"
)

highlight_pos = position(
    "highlight"
)

registry_pos = position(
    "registry"
)

check(
    "UDUC_BEFORE_UUCD",
    (
        uduc_gate_pos >= 0
        and uucd_build_pos > uduc_gate_pos
    ),
)

check(
    "UUCD_BEFORE_HIGHLIGHT",
    (
        uucd_build_pos >= 0
        and highlight_pos > uucd_build_pos
    ),
)

check(
    "UUCD_BEFORE_REGISTRY",
    (
        uucd_build_pos >= 0
        and registry_pos > uucd_build_pos
    ),
)

check(
    "READY_FOR_BODY_STORE_GATE_PRESENT",
    (
        '"READY_FOR_BODY_STORE"'
        in coordinator_source
    ),
)

check(
    "U9_EXECUTION_ORDER_ENTRY_PRESENT",
    (
        "uploaded_document_to_current_canonical_uucd"
        in coordinator_source
    ),
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

    print(
        f"{name}={present}"
    )

    checks.append(
        (
            name + "_MUST_BE_FALSE",
            present is False,
        )
    )

    print(
        f"{name}_MUST_BE_FALSE="
        + str(
            present is False
        )
    )


print()
print("=== E. UDUC REMAINS REGISTRY / ATS INPUT ===")

uduc_usage_tokens = [
    "uduc",
    "registry",
]

check(
    "COORDINATOR_STILL_CONTAINS_UDUC_AND_REGISTRY",
    all(
        token
        in coordinator_source
        for token
        in uduc_usage_tokens
    ),
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

stale_matches: list[str] = []

server_root = Path(
    "backend/server"
)

for path in server_root.rglob(
    "*.py"
):
    rel = str(
        path.as_posix()
    )

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
    len(
        stale_matches
    ) == 0,
)

print(
    "STALE_LEGACY_PRODUCTION_REFERENCES="
    + repr(
        stale_matches
    )
)


print()
print("=== H. CIRCULAR IMPORT REGRESSION ===")

repository_path = Path(
    "backend/server/universal_article_body_store/body_store_repository_v1.py"
)

repository_source = repository_path.read_text(
    encoding="utf-8-sig"
)

top_level_writer_import = (
    "from backend.server.universal_article_body_store.body_store_writer_v1 import"
    in "\n".join(
        repository_source.splitlines()[:40]
    )
)

check(
    "BODY_STORE_REPOSITORY_NO_TOP_LEVEL_WRITER_IMPORT",
    top_level_writer_import is False,
)

check(
    "BODY_STORE_REPOSITORY_LAZY_WRITER_IMPORT_PRESENT",
    (
        "from backend.server.universal_article_body_store.body_store_writer_v1 import"
        in repository_source
    ),
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
print("=== J. NO PRODUCTION DATA WRITES BY VERIFIER ===")

production_write_calls_present = any(
    token
    in Path(__file__).read_text(
        encoding="utf-8-sig"
    )
    for token
    in (
        "write_verified_body_from_envelope_v1(",
        "persist_finalized_uucd_v1(",
        "open(",
        "write_text(",
        "write_bytes(",
        "unlink(",
        "rmtree(",
    )
)

check(
    "VERIFIER_HAS_NO_PRODUCTION_DATA_WRITE_CALLS",
    production_write_calls_present is False,
)


print()
print("=== K. FINAL U9.22 DECISION ===")

passed = sum(
    1
    for _,
    value
    in checks
    if value
)

failed = [
    name
    for name,
    value
    in checks
    if not value
]

print(
    "TOTAL_U9_22_CHECKS="
    + str(
        len(
            checks
        )
    )
)

print(
    "TOTAL_U9_22_CHECKS_PASSED="
    + str(
        passed
    )
)

print(
    "ALL_U9_22_CHECKS_PASSED="
    + str(
        not failed
    )
)

print(
    "FAILED_U9_22_CHECKS="
    + repr(
        failed
    )
)

if not failed:
    print(
        "U9.22_NEXT_STEP=CERTIFY_BUILD_INTEGRATION"
    )
else:
    print(
        "U9.22_NEXT_STEP=INVESTIGATE_FAILED_CHECKS"
    )