from __future__ import annotations

import ast
import importlib
from pathlib import Path


print("=== U9.23 PHASE U9 FINAL CERTIFICATION ===")

checks: list[tuple[str, bool]] = []


def check(name: str, condition: bool) -> None:
    value = bool(condition)
    checks.append((name, value))
    print(f"{name}={value}")


def read_text(path: Path) -> str:
    raw = path.read_bytes()

    if raw.startswith(b"\xff\xfe"):
        return raw.decode("utf-16-le").lstrip("\ufeff")

    if raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16-be").lstrip("\ufeff")

    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")

    return raw.decode("utf-8")


print()
print("=== A. FINAL VERIFICATION EVIDENCE ===")

u9_21_log = Path(
    "backend/server/verification_scans/"
    "u9_21_behavioral_uucd_verification.txt"
)

u9_22_log = Path(
    "backend/server/verification_scans/"
    "u9_22_build_integration_verification_v2.txt"
)

check(
    "U9_21_LOG_EXISTS",
    u9_21_log.exists(),
)

check(
    "U9_22_LOG_EXISTS",
    u9_22_log.exists(),
)

u9_21_text = (
    read_text(u9_21_log)
    if u9_21_log.exists()
    else ""
)

u9_22_text = (
    read_text(u9_22_log)
    if u9_22_log.exists()
    else ""
)

check(
    "U9_21_72_OF_72_CERTIFIED",
    (
        "TOTAL_U9_21_CHECKS=72"
        in u9_21_text
        and
        "TOTAL_U9_21_CHECKS_PASSED=72"
        in u9_21_text
        and
        "ALL_U9_21_CHECKS_PASSED=True"
        in u9_21_text
    ),
)

check(
    "U9_22_48_OF_48_CERTIFIED",
    (
        "TOTAL_U9_22_CHECKS=48"
        in u9_22_text
        and
        "TOTAL_U9_22_CHECKS_PASSED=48"
        in u9_22_text
        and
        "ALL_U9_22_CHECKS_PASSED=True"
        in u9_22_text
    ),
)


print()
print("=== B. CURRENT CANONICAL COMPONENTS ===")

paths = {
    "UDUC_MODULE_PRESENT":
        Path(
            "backend/server/stores/"
            "uploaded_document_unified_content.py"
        ),

    "UUCD_ENGINE_PRESENT":
        Path(
            "backend/server/"
            "universal_unified_content_document/"
            "uucd_engine_v1.py"
        ),

    "UUCD_PERSISTENCE_PRESENT":
        Path(
            "backend/server/"
            "universal_unified_content_document/"
            "uucd_persistence_v1.py"
        ),

    "BODY_STORE_WRITER_PRESENT":
        Path(
            "backend/server/"
            "universal_article_body_store/"
            "body_store_writer_v1.py"
        ),

    "BODY_STORE_REPOSITORY_PRESENT":
        Path(
            "backend/server/"
            "universal_article_body_store/"
            "body_store_repository_v1.py"
        ),

    "RUNTIME_HANDOFF_PRESENT":
        Path(
            "backend/server/runtime/"
            "uucd_runtime_handoff_v1.py"
        ),

    "UPLOAD_COORDINATOR_PRESENT":
        Path(
            "backend/server/pipelines/"
            "upload_document/coordinator.py"
        ),

    "WEBSITE_ENGINE_PRESENT":
        Path(
            "backend/server/"
            "website_unified_content/"
            "website_unified_content_engine_v1.py"
        ),
}

for name, path in paths.items():
    check(
        name,
        path.exists(),
    )


print()
print("=== C. CANONICAL UUCD CONTRACT ===")

engine_source = read_text(
    paths[
        "UUCD_ENGINE_PRESENT"
    ]
)

required_engine_tokens = (
    "uploaded_document_unified_content_v2",
    "uploaded_document_uduc_pipeline_v2",
    "universal_unified_content_document_v2",
    "PENDING_BODY_STORE_WRITE",
    "READY_FOR_BODY_STORE",
    "BOUND_AND_VERIFIED",
    "universal_article_body_store",
    "body_payload",
    "build_transient_uucd_from_uduc_v1",
)

for token in required_engine_tokens:
    check(
        "UUCD_ENGINE_TOKEN__"
        + token.upper().replace("-", "_"),
        token in engine_source,
    )

check(
    "UUCD_RECORD_BODYLESS_CONTRACT_PRESENT",
    (
        '"content_body_in_uucd_record"'
        in engine_source
        and
        "False"
        in engine_source
    ),
)

check(
    "NO_WUC_CONVERSION_IN_UDUC_BUILDER_DOCSTRING",
    "convert UDUC into WUC"
    in engine_source,
)


print()
print("=== D. BODY STORE BOUNDARY ===")

body_writer_source = read_text(
    paths[
        "BODY_STORE_WRITER_PRESENT"
    ]
)

for token in (
    "STORED_AND_VERIFIED",
    "READY_FOR_UUCD_PERSISTENCE",
    "body_store_write_verified",
    "uucd_persistence",
    "runtime_executed",
    "semantic_processing_performed",
):
    check(
        "BODY_STORE_TOKEN__"
        + token.upper(),
        token in body_writer_source,
    )


print()
print("=== E. PERSISTENCE BOUNDARY ===")

persistence_source = read_text(
    paths[
        "UUCD_PERSISTENCE_PRESENT"
    ]
)

for token in (
    "PERSISTED_AND_VERIFIED",
    "runtime_queue_handoff",
    "uucd_persisted",
    "content_body_persisted_in_uucd",
    "queue_job_created",
    "semantic_processing_performed",
):
    check(
        "PERSISTENCE_TOKEN__"
        + token.upper(),
        token in persistence_source,
    )


print()
print("=== F. RUNTIME BOUNDARY ===")

runtime_source = read_text(
    paths[
        "RUNTIME_HANDOFF_PRESENT"
    ]
)

for token in (
    "body_status",
    "STORED_AND_VERIFIED",
    "PERSISTED_AND_VERIFIED",
    "runtime_queue_handoff",
    "content_ref",
    "body_ref",
    "persistence_fingerprint",
):
    check(
        "RUNTIME_TOKEN__"
        + token.upper(),
        token in runtime_source,
    )

check(
    "RUNTIME_REJECTS_CONTENT_BODY",
    (
        '"content_body"'
        in runtime_source
        and
        "must not contain content_body"
        in runtime_source
    ),
)


print()
print("=== G. UPLOADED DOCUMENT INGESTION ENDPOINT ===")

coordinator_source = read_text(
    paths[
        "UPLOAD_COORDINATOR_PRESENT"
    ]
)

coordinator_tree = ast.parse(
    coordinator_source
)

builder_calls = [
    node
    for node in ast.walk(
        coordinator_tree
    )
    if isinstance(
        node,
        ast.Call,
    )
    and isinstance(
        node.func,
        ast.Name,
    )
    and node.func.id
    == "build_transient_uucd_from_uduc_v1"
]

check(
    "COORDINATOR_UUCD_BUILDER_CALLED_ONCE",
    len(builder_calls) == 1,
)

check(
    "COORDINATOR_UUCD_BUILDER_RECEIVES_UDUC",
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

check(
    "COORDINATOR_READY_FOR_BODY_STORE_GATE",
    '"READY_FOR_BODY_STORE"'
    in coordinator_source,
)

for name, forbidden in {
    "NO_BODY_STORE_WRITE_IN_INGESTION":
        "write_verified_body_from_envelope_v1",

    "NO_UUCD_PERSISTENCE_IN_INGESTION":
        "persist_finalized_uucd_v1",

    "NO_RUNTIME_HANDOFF_IN_INGESTION":
        "handoff_persisted_uucd_to_runtime_v1",

    "NO_RUNTIME_PAYLOAD_BUILD_IN_INGESTION":
        "build_uucd_runtime_payload_v1",

    "NO_UNIVERSAL_JOB_CREATION_IN_INGESTION":
        "create_universal_job",

    "NO_ORCHESTRATION_JOB_CREATION_IN_INGESTION":
        "create_orchestration_job",

    "NO_SEMANTIC_RUNTIME_IN_INGESTION":
        "semantic_intelligence_runtime_reader",

    "NO_SCORER_IN_INGESTION":
        "scorer.py",
}.items():

    check(
        name,
        forbidden
        not in coordinator_source,
    )


print()
print("=== H. LEGACY UUCD CLEANUP ===")

legacy_cert = Path(
    "backend/server/stores/"
    "uucd_body_store_certification.py"
)

legacy_rebuild = Path(
    "backend/server/runtime/"
    "canonical_environment_rebuild_manager.py"
)

legacy_data = Path(
    "backend/server/data/"
    "uucd_body_store_certifications"
)

check(
    "LEGACY_CERT_MODULE_REMOVED",
    not legacy_cert.exists(),
)

check(
    "LEGACY_REBUILD_MANAGER_REMOVED",
    not legacy_rebuild.exists(),
)

check(
    "LEGACY_HISTORICAL_DATA_PRESERVED",
    legacy_data.exists(),
)


print()
print("=== I. CIRCULAR IMPORT FIX ===")

repository_source = read_text(
    paths[
        "BODY_STORE_REPOSITORY_PRESENT"
    ]
)

repository_tree = ast.parse(
    repository_source
)

top_level_writer_import = False
local_writer_import = False

for node in repository_tree.body:
    if (
        isinstance(
            node,
            ast.ImportFrom,
        )
        and node.module
        == (
            "backend.server."
            "universal_article_body_store."
            "body_store_writer_v1"
        )
    ):
        top_level_writer_import = True

for node in ast.walk(
    repository_tree
):
    if not isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        continue

    for child in ast.walk(
        node
    ):
        if (
            isinstance(
                child,
                ast.ImportFrom,
            )
            and child.module
            == (
                "backend.server."
                "universal_article_body_store."
                "body_store_writer_v1"
            )
        ):
            local_writer_import = True

check(
    "NO_TOP_LEVEL_BODY_WRITER_IMPORT",
    top_level_writer_import is False,
)

check(
    "LAZY_BODY_WRITER_IMPORT_PRESENT",
    local_writer_import is True,
)


print()
print("=== J. FINAL IMPORT CERTIFICATION ===")

modules = {
    "FINAL_UDUC_IMPORT":
        "backend.server.stores."
        "uploaded_document_unified_content",

    "FINAL_UUCD_ENGINE_IMPORT":
        "backend.server."
        "universal_unified_content_document."
        "uucd_engine_v1",

    "FINAL_UUCD_PERSISTENCE_IMPORT":
        "backend.server."
        "universal_unified_content_document."
        "uucd_persistence_v1",

    "FINAL_BODY_STORE_IMPORT":
        "backend.server."
        "universal_article_body_store."
        "body_store_writer_v1",

    "FINAL_BODY_REPOSITORY_IMPORT":
        "backend.server."
        "universal_article_body_store."
        "body_store_repository_v1",

    "FINAL_RUNTIME_IMPORT":
        "backend.server.runtime."
        "uucd_runtime_handoff_v1",

    "FINAL_UPLOAD_COORDINATOR_IMPORT":
        "backend.server.pipelines."
        "upload_document.coordinator",

    "FINAL_WEBSITE_ENGINE_IMPORT":
        "backend.server."
        "website_unified_content."
        "website_unified_content_engine_v1",
}

for name, module_name in modules.items():

    try:
        importlib.import_module(
            module_name
        )
        ok = True

    except Exception as exc:
        ok = False
        print(
            f"{name}_ERROR_TYPE="
            f"{type(exc).__name__}"
        )
        print(
            f"{name}_ERROR={exc}"
        )

    check(
        name,
        ok,
    )


print()
print("=== K. FINAL U9.23 DECISION ===")

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
    "TOTAL_U9_23_CHECKS="
    + str(
        len(checks)
    )
)

print(
    "TOTAL_U9_23_CHECKS_PASSED="
    + str(
        passed
    )
)

print(
    "ALL_U9_23_CHECKS_PASSED="
    + str(
        not failed
    )
)

print(
    "FAILED_U9_23_CHECKS="
    + repr(
        failed
    )
)

if not failed:
    print(
        "U9_PHASE_STATUS=CERTIFIED_AND_COMPLETE"
    )
    print(
        "UPLOADED_DOCUMENT_PIPELINE_ENDPOINT="
        "CURRENT_CANONICAL_UUCD_READY_FOR_BODY_STORE"
    )
    print(
        "NEXT_STEP="
        "POST_U9_REAL_UI_10_DOCUMENT_VALIDATION"
    )
else:
    print(
        "U9_PHASE_STATUS=NOT_CERTIFIED"
    )
    print(
        "NEXT_STEP="
        "INVESTIGATE_FAILED_CERTIFICATION_CHECKS"
    )