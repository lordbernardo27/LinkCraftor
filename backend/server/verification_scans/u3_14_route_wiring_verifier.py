from __future__ import annotations

import inspect
from pathlib import Path

import backend.server.routes.files as files_route


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U3.14 ROUTE REGISTRATION ===")

upload_routes = []

router_prefix = str(
    getattr(files_route.router, "prefix", "") or ""
).rstrip("/")

expected_upload_path = (
    f"{router_prefix}/upload"
    if router_prefix
    else "/upload"
)

check(
    "FILES_ROUTER_PREFIX_IS_CANONICAL",
    router_prefix == "/api/files",
)

check(
    "EXPECTED_RUNTIME_UPLOAD_PATH_IS_CANONICAL",
    expected_upload_path == "/api/files/upload",
)

for route in files_route.router.routes:
    path = getattr(route, "path", "")
    methods = set(getattr(route, "methods", set()) or set())

    if (
        path == expected_upload_path
        and "POST" in methods
    ):
        upload_routes.append(route)


check(
    "EXACTLY_ONE_FILES_POST_UPLOAD_ROUTE",
    len(upload_routes) == 1,
)

if len(upload_routes) == 1:
    endpoint = upload_routes[0].endpoint

    check(
        "UPLOAD_ROUTE_ENDPOINT_CALLABLE",
        callable(endpoint),
    )

    endpoint_source = inspect.getsource(endpoint)

else:
    endpoint = None
    endpoint_source = ""


print()
print("=== U3.14 CANONICAL DELEGATION ===")

check(
    "ROUTE_DELEGATES_TO_RUN_UPLOAD_DOCUMENT",
    "run_upload_document(" in endpoint_source,
)


print()
print("=== U3.14 DEPENDENCY WIRING ===")

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

compact_source = "".join(
    endpoint_source.split()
)

for label, expected in expected_wiring.items():
    check(
        label,
        "".join(expected.split()) in compact_source,
    )


print()
print("=== U3.14 FORMAT CONTRACT ===")

expected_extensions = {
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
}

check(
    "FILES_ROUTE_ALLOWED_EXT_EXACT",
    set(files_route.ALLOWED_EXT)
    == expected_extensions,
)


from backend.server.stores.upload_document_extractor import (
    SUPPORTED_UPLOAD_EXTENSIONS,
)

check(
    "EXTRACTOR_EXTENSION_SET_EXACT",
    set(SUPPORTED_UPLOAD_EXTENSIONS.keys())
    == expected_extensions,
)

check(
    "ROUTE_AND_EXTRACTOR_EXTENSION_SETS_MATCH",
    set(files_route.ALLOWED_EXT)
    == set(SUPPORTED_UPLOAD_EXTENSIONS.keys()),
)


print()
print("=== U3.14 UPLOAD LIMIT ===")

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)

check(
    "UPLOAD_LIMIT_250_MIB",
    upload_intake.MAX_UPLOAD_BYTES
    == 250 * 1024 * 1024,
)


print()
print("=== U3.14 SOURCE ROUTE INVENTORY ===")

route_source_path = Path(
    "backend/server/routes/files.py"
)

route_source = route_source_path.read_text(
    encoding="utf-8"
)

canonical_route_declarations = (
    route_source.count(
        '@router.post("/upload")'
    )
)

check(
    "SOURCE_HAS_EXACTLY_ONE_DOCUMENT_UPLOAD_DECLARATION",
    canonical_route_declarations == 1,
)


print()
print("=== U3.14 OBSOLETE DOCUMENT-UPLOAD ALIASES ===")

obsolete_aliases = [
    '@router.post("/upload-document")',
    '@router.post("/upload_document")',
    '@router.post("/files/upload")',
    '@router.post("/document/upload")',
]

for alias in obsolete_aliases:
    check(
        "NO_ALIAS_" + (
            alias
            .replace('@router.post("', "")
            .replace('")', "")
            .replace("/", "_")
            .strip("_")
            .upper()
        ),
        alias not in route_source,
    )


print()
print("=== U3.14 INNER COORDINATOR WIRING ===")

inner_path = Path(
    "backend/server/pipelines/upload_document/"
    "uploaded_document_to_uduc_pipeline/coordinator.py"
)

inner_source = inner_path.read_text(
    encoding="utf-8"
)

check(
    "INNER_COORDINATOR_DELEGATES_TO_RUN_UPLOAD_INTAKE",
    "await run_upload_intake(" in inner_source,
)


print()
print("=== U3.14 TOP COORDINATOR WIRING ===")

top_path = Path(
    "backend/server/pipelines/upload_document/coordinator.py"
)

top_source = top_path.read_text(
    encoding="utf-8"
)

check(
    "TOP_COORDINATOR_CALLS_UDUC_PIPELINE_FIRST",
    "await run_uploaded_document_to_uduc_pipeline("
    in top_source,
)

check(
    "TOP_COORDINATOR_CALLS_UDUC_BUILDER",
    "build_and_write_uduc_from_extraction_result("
    in top_source,
)

check(
    "TOP_COORDINATOR_CALLS_HIGHLIGHT",
    "run_uploaded_document_to_highlight_pipeline("
    in top_source,
)

check(
    "TOP_COORDINATOR_CALLS_ACTIVE_TARGET_SET",
    "run_uploaded_document_registry_to_active_target_set_pipeline("
    in top_source,
)


uduc_pipeline_pos = top_source.find(
    "await run_uploaded_document_to_uduc_pipeline("
)

uduc_builder_pos = top_source.find(
    "build_and_write_uduc_from_extraction_result("
)

highlight_pos = top_source.find(
    "run_uploaded_document_to_highlight_pipeline("
)

active_target_pos = top_source.find(
    "run_uploaded_document_registry_to_active_target_set_pipeline("
)

check(
    "CANONICAL_ORCHESTRATION_ORDER",
    -1
    not in {
        uduc_pipeline_pos,
        uduc_builder_pos,
        highlight_pos,
        active_target_pos,
    }
    and uduc_pipeline_pos
    < uduc_builder_pos
    < highlight_pos
    < active_target_pos,
)


failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U3.14_ROUTE_WIRING_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U3.14 route/wiring verification failed."
    )

print(
    "U3.14_ROUTE_WIRING_VERIFICATION: PASS"
)