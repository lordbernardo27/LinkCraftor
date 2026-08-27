from __future__ import annotations

import importlib
import py_compile
from pathlib import Path


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


production_files = [
    Path("backend/server/routes/files.py"),
    Path("backend/server/stores/upload_document_extractor.py"),
    Path("backend/server/stores/uploaded_document_unified_content.py"),
    Path("backend/server/pipelines/upload_document/coordinator.py"),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/upload_intake.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_highlight_pipeline/coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_registry_to_active_target_set_pipeline/coordinator.py"
    ),
]

modules = [
    (
        "FILES_ROUTE",
        "backend.server.routes.files",
    ),
    (
        "UPLOAD_EXTRACTOR",
        "backend.server.stores.upload_document_extractor",
    ),
    (
        "UDUC_STORE",
        "backend.server.stores.uploaded_document_unified_content",
    ),
    (
        "UPLOAD_TOP_COORDINATOR",
        "backend.server.pipelines.upload_document.coordinator",
    ),
    (
        "UPLOAD_TO_UDUC_COORDINATOR",
        "backend.server.pipelines.upload_document."
        "uploaded_document_to_uduc_pipeline.coordinator",
    ),
    (
        "UPLOAD_INTAKE",
        "backend.server.pipelines.upload_document."
        "uploaded_document_to_uduc_pipeline.upload_intake",
    ),
    (
        "UPLOAD_HIGHLIGHT_COORDINATOR",
        "backend.server.pipelines.upload_document."
        "uploaded_document_to_highlight_pipeline.coordinator",
    ),
    (
        "UPLOAD_REGISTRY_ATS_COORDINATOR",
        "backend.server.pipelines.upload_document."
        "uploaded_document_registry_to_active_target_set_pipeline.coordinator",
    ),
]


print("=== U3.14 PRODUCTION SYNTAX ===")

for path in production_files:
    try:
        py_compile.compile(
            str(path),
            doraise=True,
        )
        check(
            f"SYNTAX_{path.name}_{abs(hash(str(path)))}",
            True,
        )
    except Exception as exc:
        print(
            f"SYNTAX_ERROR {path}: "
            f"{type(exc).__name__}: {exc}"
        )
        check(
            f"SYNTAX_{path.name}_{abs(hash(str(path)))}",
            False,
        )


print()
print("=== U3.14 MODULE IMPORTS ===")

imported = {}

for label, module_name in modules:
    try:
        imported[label] = importlib.import_module(
            module_name
        )

        check(
            f"{label}_IMPORT",
            True,
        )
    except Exception as exc:
        print(
            f"{label}_IMPORT_ERROR: "
            f"{type(exc).__name__}: {exc}"
        )

        check(
            f"{label}_IMPORT",
            False,
        )


print()
print("=== U3.14 REQUIRED SYMBOLS ===")

required_symbols = {
    "FILES_ROUTE": [
        "router",
        "_guess_ext",
        "_ws",
        "_extract_preview_from_bytes",
        "_store_and_index",
        "_rollback_committed_upload",
        "_ws_dir",
        "ALLOWED_EXT",
    ],
    "UPLOAD_EXTRACTOR": [
        "extract_upload_document_v1",
        "SUPPORTED_UPLOAD_EXTENSIONS",
    ],
    "UDUC_STORE": [
        "build_and_write_uduc_from_extraction_result",
    ],
    "UPLOAD_TOP_COORDINATOR": [
        "run_upload_document",
    ],
    "UPLOAD_TO_UDUC_COORDINATOR": [
        "run_uploaded_document_to_uduc_pipeline",
    ],
    "UPLOAD_INTAKE": [
        "UploadIntakeDependencies",
        "run_upload_intake",
        "MAX_UPLOAD_BYTES",
    ],
    "UPLOAD_HIGHLIGHT_COORDINATOR": [
        "run_uploaded_document_to_highlight_pipeline",
    ],
    "UPLOAD_REGISTRY_ATS_COORDINATOR": [
        "run_uploaded_document_registry_to_active_target_set_pipeline",
    ],
}

for label, names in required_symbols.items():
    module = imported.get(label)

    for name in names:
        check(
            f"{label}_SYMBOL_{name}",
            module is not None
            and hasattr(module, name),
        )


print()
print("=== U3.14 IMPORT CONTRACT ===")

check(
    "ALL_PRODUCTION_FILES_PRESENT",
    all(path.is_file() for path in production_files),
)

check(
    "ALL_REQUIRED_MODULES_IMPORTED",
    len(imported) == len(modules),
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
        "U3.14_IMPORT_BUILD_SURFACE_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U3.14 import/build surface verification failed."
    )

print(
    "U3.14_IMPORT_BUILD_SURFACE_VERIFICATION: PASS"
)