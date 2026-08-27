from __future__ import annotations

import inspect

import backend.server.routes.files as files_route
import backend.server.pipelines.upload_document.coordinator as top_coordinator

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    coordinator as inner_coordinator,
)

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)

from backend.server.stores.upload_document_extractor import (
    SUPPORTED_UPLOAD_EXTENSIONS,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U3.15 STEP 2 — LIVE PHASE U3 CONTRACT ===")


# ------------------------------------------------------------
# A. Canonical route
# ------------------------------------------------------------

print()
print("=== A. CANONICAL ROUTE ===")

upload_routes = [
    route
    for route in files_route.router.routes
    if getattr(route, "path", "")
    == "/api/files/upload"
    and "POST"
    in set(
        getattr(route, "methods", set())
        or set()
    )
]

check(
    "EXACTLY_ONE_POST_API_FILES_UPLOAD",
    len(upload_routes) == 1,
)

endpoint = (
    upload_routes[0].endpoint
    if len(upload_routes) == 1
    else None
)

endpoint_source = (
    inspect.getsource(endpoint)
    if callable(endpoint)
    else ""
)

compact_endpoint = "".join(
    endpoint_source.split()
)

check(
    "ROUTE_DELEGATES_TO_RUN_UPLOAD_DOCUMENT",
    "run_upload_document("
    in endpoint_source,
)


# ------------------------------------------------------------
# B. Intake dependency contract
# ------------------------------------------------------------

print()
print("=== B. INTAKE DEPENDENCY CONTRACT ===")

expected_dependencies = {
    "guess_extension",
    "normalize_workspace_id",
    "extract_preview",
    "store_and_index",
    "rollback_committed_upload",
    "workspace_directory",
    "allowed_extensions",
}

dependency_fields = set(
    getattr(
        upload_intake.UploadIntakeDependencies,
        "__dataclass_fields__",
        {},
    ).keys()
)

check(
    "DEPENDENCY_FIELD_SET_EXACT",
    dependency_fields
    == expected_dependencies,
)

expected_wiring = {
    "GUESS_EXTENSION_WIRED":
        "guess_extension=_guess_ext",

    "NORMALIZE_WORKSPACE_WIRED":
        "normalize_workspace_id=_ws",

    "EXTRACT_PREVIEW_WIRED":
        "extract_preview=_extract_preview_from_bytes",

    "STORE_AND_INDEX_WIRED":
        "store_and_index=_store_and_index",

    "ROLLBACK_WIRED":
        "rollback_committed_upload=_rollback_committed_upload",

    "WORKSPACE_DIRECTORY_WIRED":
        "workspace_directory=_ws_dir",

    "ALLOWED_EXTENSIONS_WIRED":
        "allowed_extensions=ALLOWED_EXT",
}

for label, fragment in expected_wiring.items():
    check(
        label,
        "".join(fragment.split())
        in compact_endpoint,
    )


# ------------------------------------------------------------
# C. Canonical orchestration chain
# ------------------------------------------------------------

print()
print("=== C. CANONICAL ORCHESTRATION CHAIN ===")

inner_source = inspect.getsource(
    inner_coordinator
    .run_uploaded_document_to_uduc_pipeline
)

check(
    "INNER_COORDINATOR_CALLS_UPLOAD_INTAKE",
    "run_upload_intake("
    in inner_source,
)

top_source = inspect.getsource(
    top_coordinator.run_upload_document
)

stages = [
    "run_uploaded_document_to_uduc_pipeline(",
    "build_and_write_uduc_from_extraction_result(",
    "run_uploaded_document_to_highlight_pipeline(",
    "run_uploaded_document_registry_to_active_target_set_pipeline(",
]

positions = [
    top_source.find(stage)
    for stage in stages
]

check(
    "ALL_CANONICAL_TOP_STAGES_PRESENT",
    all(
        position >= 0
        for position in positions
    ),
)

check(
    "CANONICAL_TOP_STAGE_ORDER",
    all(
        position >= 0
        for position in positions
    )
    and positions
    == sorted(positions),
)


# ------------------------------------------------------------
# D. Format / size contract
# ------------------------------------------------------------

print()
print("=== D. FORMAT / SIZE CONTRACT ===")

expected_extensions = {
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
}

check(
    "ROUTE_ALLOWLIST_EXACT",
    set(files_route.ALLOWED_EXT)
    == expected_extensions,
)

check(
    "EXTRACTOR_ALLOWLIST_EXACT",
    set(
        SUPPORTED_UPLOAD_EXTENSIONS.keys()
    )
    == expected_extensions,
)

check(
    "ROUTE_AND_EXTRACTOR_ALLOWLISTS_MATCH",
    set(files_route.ALLOWED_EXT)
    == set(
        SUPPORTED_UPLOAD_EXTENSIONS.keys()
    ),
)

check(
    "UPLOAD_CEILING_250_MIB",
    upload_intake.MAX_UPLOAD_BYTES
    == 250 * 1024 * 1024,
)


# ------------------------------------------------------------
# E. Synchronous intake contract
# ------------------------------------------------------------

print()
print("=== E. SYNCHRONOUS EXECUTION CONTRACT ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
)

check(
    "JOB_ID_NONE_CONTRACT_PRESENT",
    '"job_id": None'
    in intake_source,
)

check(
    "PROCESSING_NOT_APPLICABLE_CONTRACT_PRESENT",
    '"processing_status": "not_applicable"'
    in intake_source,
)

forbidden_execution_terms = [
    "BackgroundTasks",
    "create_task",
    "run_in_executor",
    "upload_worker",
    "upload worker",
    "upload_job",
    "upload job",
]

combined_execution_source = (
    endpoint_source
    + "\n"
    + inner_source
    + "\n"
    + top_source
    + "\n"
    + intake_source
)

check(
    "NO_UPLOAD_WORKER_JOB_BACKGROUND_EXECUTION",
    all(
        term.lower()
        not in combined_execution_source.lower()
        for term in forbidden_execution_terms
    ),
)


# ------------------------------------------------------------
# F. Public response boundary
# ------------------------------------------------------------

print()
print("=== F. PUBLIC RESPONSE BOUNDARY ===")

required_public_fields = [
    '"ok"',
    '"workspace_id"',
    '"doc"',
    '"filename"',
    '"ext"',
    '"text"',
    '"html"',
    '"is_html"',
    '"truncated"',
    '"pipeline"',
    '"document_id"',
    '"status"',
    '"execution_started"',
    '"execution_completed"',
    '"job_id"',
    '"processing_status"',
]

for field in required_public_fields:
    check(
        "PUBLIC_FIELD_"
        + field.strip('"').upper(),
        field in endpoint_source,
    )

check(
    "INTERNAL_EXTRACTION_NOT_DIRECTLY_EXPOSED",
    '"extraction":'
    not in endpoint_source,
)

check(
    "INTERNAL_UDUC_NOT_DIRECTLY_EXPOSED",
    '"uduc":'
    not in endpoint_source,
)


# ------------------------------------------------------------
# G. Premature downstream boundary
# ------------------------------------------------------------

print()
print("=== G. PREMATURE INTEGRATION BOUNDARY ===")

forbidden_downstream_terms = [
    "uucd_engine",
    "uucd_persistence",
    "universal_unified_content_document",
    "semantic_runtime",
    "run_scorer",
    "register_runtime",
]

check(
    "NO_PREMATURE_UUCD_SEMANTIC_SCORER_RUNTIME",
    all(
        term.lower()
        not in combined_execution_source.lower()
        for term in forbidden_downstream_terms
    ),
)


# ------------------------------------------------------------
# H. Website isolation
# ------------------------------------------------------------

print()
print("=== H. WEBSITE BRANCH ISOLATION ===")

check(
    "NO_ARTICLE_BODY_CLEANING_ENGINE_REFERENCE",
    "article_body_cleaning_engine"
    not in combined_execution_source,
)

check(
    "NO_ARTICLE_CLEANING_PIPELINE_REFERENCE",
    "article_cleaning_pipeline"
    not in combined_execution_source,
)


# ------------------------------------------------------------
# Final result
# ------------------------------------------------------------

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U3.15_LIVE_PHASE_CONTRACT_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U3.15 live Phase U3 contract verification failed."
    )

print(
    "U3.15_LIVE_PHASE_CONTRACT_VERIFICATION: PASS"
)