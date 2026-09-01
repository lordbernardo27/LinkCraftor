from pathlib import Path
import ast
import py_compile


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U8.21 UDUC VS CURRENT CANONICAL UUCD BOUNDARY VERIFICATION ===")


# ------------------------------------------------------------
# A. Canonical files
# ------------------------------------------------------------

print()
print("=== A. FILE INVENTORY ===")

uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

upload_coordinator_path = Path(
    "backend/server/pipelines/upload_document/"
    "coordinator.py"
)

current_uucd_engine_path = Path(
    "backend/server/universal_unified_content_document/"
    "uucd_engine_v1.py"
)

current_uucd_persistence_path = Path(
    "backend/server/universal_unified_content_document/"
    "uucd_persistence_v1.py"
)

check(
    "UDUC_MODULE_EXISTS",
    uduc_path.exists(),
)

check(
    "LIVE_UPLOAD_COORDINATOR_EXISTS",
    upload_coordinator_path.exists(),
)

check(
    "CURRENT_CANONICAL_UUCD_ENGINE_EXISTS",
    current_uucd_engine_path.exists(),
)

check(
    "CURRENT_CANONICAL_UUCD_PERSISTENCE_EXISTS",
    current_uucd_persistence_path.exists(),
)


# ------------------------------------------------------------
# B. Compile U8 production files
# ------------------------------------------------------------

print()
print("=== B. U8 PRODUCTION COMPILE ===")

for label, path in [
    ("UDUC_MODULE", uduc_path),
    ("LIVE_UPLOAD_COORDINATOR", upload_coordinator_path),
]:
    ok = True

    try:
        py_compile.compile(
            str(path),
            doraise=True,
        )
    except Exception as exc:
        ok = False
        print(
            f"{label}_COMPILE_ERROR="
            f"{type(exc).__name__}: {exc}"
        )

    check(
        f"{label}_COMPILES",
        ok,
    )


# ------------------------------------------------------------
# C. Parse source
# ------------------------------------------------------------

print()
print("=== C. SOURCE EXTRACTION ===")

uduc_source = uduc_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

coordinator_source = upload_coordinator_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

uduc_tree = ast.parse(
    uduc_source
)

coordinator_tree = ast.parse(
    coordinator_source
)


def function_source(
    tree,
    source,
    name,
):
    node = next(
        (
            n
            for n in tree.body
            if isinstance(
                n,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and n.name == name
        ),
        None,
    )

    if node is None:
        return ""

    return (
        ast.get_source_segment(
            source,
            node,
        )
        or ""
    )


builder_source = function_source(
    uduc_tree,
    uduc_source,
    "build_uduc_from_normalized_content",
)

serializer_source = function_source(
    uduc_tree,
    uduc_source,
    "serialize_uduc",
)

write_source = function_source(
    uduc_tree,
    uduc_source,
    "write_uduc",
)

read_source = function_source(
    uduc_tree,
    uduc_source,
    "read_uduc",
)

build_write_source = function_source(
    uduc_tree,
    uduc_source,
    "build_and_write_uduc_from_normalized_content",
)

legacy_wrapper_source = function_source(
    uduc_tree,
    uduc_source,
    "build_and_write_uduc_from_extraction_result",
)

for label, value in [
    ("BUILDER", builder_source),
    ("SERIALIZER", serializer_source),
    ("WRITER", write_source),
    ("READER", read_source),
    ("CANONICAL_BUILD_WRITE", build_write_source),
]:
    check(
        f"{label}_SOURCE_FOUND",
        bool(value),
    )


# ------------------------------------------------------------
# D. UDUC core has no Current Canonical UUCD execution
# ------------------------------------------------------------

print()
print("=== D. UDUC CORE VS CURRENT CANONICAL UUCD ===")

uduc_scope = "\n".join(
    [
        builder_source,
        serializer_source,
        write_source,
        read_source,
        build_write_source,
    ]
)

uucd_execution_markers = [
    "build_uucd",
    "write_uucd",
    "persist_uucd",
    "uucd_engine_v1",
    "uucd_persistence_v1",
    "current_canonical_uucd",
]

for marker in uucd_execution_markers:
    check(
        "UDUC_CORE_NO_"
        + marker.upper(),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# E. UDUC module imports no Current Canonical UUCD engine/persistence
# ------------------------------------------------------------

print()
print("=== E. UDUC IMPORT BOUNDARY ===")

uduc_lower = uduc_source.lower()

for marker in [
    "universal_unified_content_document",
    "uucd_engine_v1",
    "uucd_persistence_v1",
]:
    check(
        "UDUC_MODULE_NO_IMPORT_"
        + marker.upper(),
        marker.lower()
        not in uduc_lower,
    )


# ------------------------------------------------------------
# F. Live upload coordinator has no premature UUCD execution
# ------------------------------------------------------------

print()
print("=== F. LIVE UPLOAD COORDINATOR VS UUCD ===")

coordinator_lower = coordinator_source.lower()

for marker in [
    "build_uucd",
    "write_uucd",
    "persist_uucd",
    "uucd_engine_v1",
    "uucd_persistence_v1",
    "current_canonical_uucd",
]:
    check(
        "LIVE_COORDINATOR_NO_"
        + marker.upper(),
        marker.lower()
        not in coordinator_lower,
    )


# ------------------------------------------------------------
# G. U8 ends at UDUC construction/persistence
# ------------------------------------------------------------

print()
print("=== G. U8 OWNERSHIP BOUNDARY ===")

check(
    "UDUC_BUILDER_PRESENT",
    bool(builder_source),
)

check(
    "UDUC_SERIALIZER_PRESENT",
    bool(serializer_source),
)

check(
    "UDUC_WRITER_PRESENT",
    bool(write_source),
)

check(
    "CANONICAL_UDUC_BUILD_WRITE_PRESENT",
    bool(build_write_source),
)

check(
    "U8_HAS_NO_CURRENT_CANONICAL_UUCD_BUILD",
    "build_uucd"
    not in uduc_scope.lower(),
)

check(
    "U8_HAS_NO_CURRENT_CANONICAL_UUCD_WRITE",
    "write_uucd"
    not in uduc_scope.lower(),
)


# ------------------------------------------------------------
# H. Canonical UDUC handoff sufficiency
# ------------------------------------------------------------

print()
print("=== H. UDUC HANDOFF SUFFICIENCY ===")

required_uduc_fields = [
    "schema_version",
    "pipeline_version",
    "workspace_id",
    "document_id",
    "source_type",
    "source_format",
    "original_filename",
    "stored_filename",
    "stored_path",
    "title",
    "h1",
    "headings",
    "content_body",
    "structure",
    "metadata",
    "extraction_status",
    "extraction_confidence",
    "extraction_created_at",
    "normalization_status",
    "normalization_version",
    "normalized_at",
    "created_at",
]

for field in required_uduc_fields:
    check(
        "UDUC_HANDOFF_FIELD_"
        + field.upper()
        + "_PRESENT_IN_SERIALIZER",
        field
        in serializer_source,
    )


# ------------------------------------------------------------
# I. No source reread / extraction / normalization rerun in U8
# ------------------------------------------------------------

print()
print("=== I. U8 REPROCESSING BOUNDARY ===")

for marker in [
    "extract_upload_document",
    "detect_upload_source_type",
    "normalize_uploaded_document_v1",
    "_normalize_title",
    "_normalize_headings",
    "unicodedata.normalize",
    "read_bytes(",
]:
    check(
        "UDUC_CORE_NO_"
        + marker.upper()
        .replace(".", "_")
        .replace("(", ""),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# J. No body store/runtime/semantic/scorer work
# ------------------------------------------------------------

print()
print("=== J. UNIVERSAL RUNTIME BOUNDARY ===")

for marker in [
    "body_store",
    "semantic_runtime",
    "run_semantic",
    "scorer",
    "runtime_reader",
    "route_dispatcher",
]:
    check(
        "UDUC_CORE_NO_"
        + marker.upper(),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# K. Legacy UDUC wrapper does not execute Current Canonical UUCD
# ------------------------------------------------------------

print()
print("=== K. LEGACY UDUC WRAPPER BOUNDARY ===")

if legacy_wrapper_source:
    for marker in [
        "build_uucd",
        "write_uucd",
        "uucd_engine_v1",
        "uucd_persistence_v1",
        "current_canonical_uucd",
    ]:
        check(
            "LEGACY_UDUC_WRAPPER_NO_"
            + marker.upper(),
            marker.lower()
            not in legacy_wrapper_source.lower(),
        )
else:
    check(
        "LEGACY_UDUC_WRAPPER_NOT_PRESENT",
        True,
    )


# ------------------------------------------------------------
# L. Narrow repository inventory for UUCD references
# ------------------------------------------------------------

print()
print("=== L. NARROW UPLOADED-DOCUMENT UUCD REFERENCE INVENTORY ===")

search_root = Path(
    "backend/server/pipelines/upload_document"
)

production_uucd_hits = []

for path in search_root.rglob(
    "*.py"
):
    if (
        "verification_scans"
        in path.parts
        or "backups"
        in path.parts
    ):
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    lower = text.lower()

    if "uucd" in lower:
        lines = text.splitlines()

        for index, line in enumerate(
            lines,
            start=1,
        ):
            if "uucd" in line.lower():
                production_uucd_hits.append(
                    (
                        str(path),
                        index,
                        line.strip(),
                    )
                )


print(
    "UPLOADED_DOCUMENT_PRODUCTION_UUCD_REFERENCE_COUNT="
    + str(
        len(
            production_uucd_hits
        )
    )
)

for path, line_number, line in production_uucd_hits:
    print(
        f"UUCD_REFERENCE: {path}:{line_number}: {line}"
    )


# ------------------------------------------------------------
# M. Classify authoritative U8 execution references
# ------------------------------------------------------------

print()
print("=== M. AUTHORITATIVE EXECUTION CLASSIFICATION ===")

authoritative_execution_hits = []

execution_terms = [
    "build_uucd(",
    "write_uucd(",
    "persist_uucd(",
    "run_uucd(",
]

for path, line_number, line in production_uucd_hits:
    lower = line.lower()

    if any(
        term in lower
        for term in execution_terms
    ):
        authoritative_execution_hits.append(
            (
                path,
                line_number,
                line,
            )
        )


print(
    "UPLOADED_DOCUMENT_AUTHORITATIVE_UUCD_EXECUTION_HIT_COUNT="
    + str(
        len(
            authoritative_execution_hits
        )
    )
)

for path, line_number, line in authoritative_execution_hits:
    print(
        f"AUTHORITATIVE_UUCD_EXECUTION_HIT: "
        f"{path}:{line_number}: {line}"
    )


check(
    "NO_AUTHORITATIVE_UUCD_EXECUTION_IN_UPLOADED_DOCUMENT_PIPELINE",
    len(
        authoritative_execution_hits
    )
    == 0,
)


# ------------------------------------------------------------
# N. Current Canonical UUCD infrastructure remains separate
# ------------------------------------------------------------

print()
print("=== N. CURRENT CANONICAL UUCD INFRASTRUCTURE SEPARATION ===")

check(
    "CURRENT_CANONICAL_UUCD_ENGINE_IS_OUTSIDE_UPLOAD_PIPELINE",
    "pipelines/upload_document"
    not in str(
        current_uucd_engine_path
    ).replace(
        "\\",
        "/",
    ),
)

check(
    "CURRENT_CANONICAL_UUCD_PERSISTENCE_IS_OUTSIDE_UPLOAD_PIPELINE",
    "pipelines/upload_document"
    not in str(
        current_uucd_persistence_path
    ).replace(
        "\\",
        "/",
    ),
)


# ------------------------------------------------------------
# O. Explicit U9 handoff classification
# ------------------------------------------------------------

print()
print("=== O. U9 HANDOFF CLASSIFICATION ===")

check(
    "U8_OUTPUT_ARTIFACT_IS_CANONICAL_UDUC",
    "build_and_write_uduc_from_normalized_content"
    in coordinator_lower,
)

check(
    "U9_CONVERGENCE_NOT_IMPLEMENTED_INSIDE_U8_CORE",
    "build_uucd"
    not in uduc_scope.lower()
    and "write_uucd"
    not in uduc_scope.lower(),
)

print(
    "U8_TO_U9_HANDOFF="
    "CANONICAL_UDUC_TO_CURRENT_CANONICAL_UUCD"
)


# ------------------------------------------------------------
# P. Final decision
# ------------------------------------------------------------

print()
print("=== P. U8.21 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.21_UDUC_VS_CURRENT_CANONICAL_UUCD_BOUNDARY: REVIEW_REQUIRED"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    print(
        "U8.21_PATCH_DECISION_REQUIRED: REVIEW_EVIDENCE"
    )

else:
    print(
        "U8.21_UDUC_VS_CURRENT_CANONICAL_UUCD_BOUNDARY: CERTIFIED"
    )

    print(
        "U8.21_U8_ENDS_AT: CANONICAL_UDUC_PERSISTENCE"
    )

    print(
        "U8.21_CURRENT_CANONICAL_UUCD_BUILD_INSIDE_U8: NO"
    )

    print(
        "U8.21_CURRENT_CANONICAL_UUCD_PERSISTENCE_INSIDE_U8: NO"
    )

    print(
        "U8.21_U9_OWNS: UDUC_TO_CURRENT_CANONICAL_UUCD_CONVERGENCE"
    )

    print(
        "U8.21_U9_HANDOFF_ARTIFACT: CANONICAL_UDUC"
    )

    print(
        "U8.21_SOURCE_REREAD: NO"
    )

    print(
        "U8.21_EXTRACTION_RERUN: NO"
    )

    print(
        "U8.21_NORMALIZATION_RERUN: NO"
    )

    print(
        "U8.21_BODY_STORE_RUNTIME_EXECUTION: NO"
    )

    print(
        "U8.21_SEMANTIC_SCORER_EXECUTION: NO"
    )

    print(
        "U8.21_PRODUCTION_PATCH_REQUIRED: NO"
    )

    print(
        "U8.22_LEGACY_UDUC_CLEANUP_TRANSITION: AUTHORIZED"
    )

    print(
        "U8.21_FINAL_BOUNDARY_VERIFICATION: PASS"
    )