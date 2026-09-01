from pathlib import Path
import ast
import py_compile


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U8.20 CORRECTED UDUC VS HIGHLIGHT / ATS BOUNDARY VERIFICATION ===")


# ------------------------------------------------------------
# A. Canonical files
# ------------------------------------------------------------

print()
print("=== A. FILE INVENTORY ===")

uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

coordinator_path = Path(
    "backend/server/pipelines/upload_document/"
    "coordinator.py"
)

check(
    "UDUC_MODULE_EXISTS",
    uduc_path.exists(),
)

check(
    "LIVE_UPLOAD_COORDINATOR_EXISTS",
    coordinator_path.exists(),
)


# ------------------------------------------------------------
# B. Compile
# ------------------------------------------------------------

print()
print("=== B. COMPILE ===")

for label, path in [
    ("UDUC_MODULE", uduc_path),
    ("LIVE_UPLOAD_COORDINATOR", coordinator_path),
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

coordinator_source = coordinator_path.read_text(
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
            and n.name
            == name
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

check(
    "CANONICAL_UDUC_BUILDER_FOUND",
    bool(builder_source),
)

check(
    "CANONICAL_UDUC_WRITER_FOUND",
    bool(write_source),
)

check(
    "CANONICAL_UDUC_READER_FOUND",
    bool(read_source),
)

check(
    "CANONICAL_BUILD_WRITE_FOUND",
    bool(build_write_source),
)


# ------------------------------------------------------------
# D. UDUC core owns no Highlight
# ------------------------------------------------------------

print()
print("=== D. UDUC CORE VS HIGHLIGHT ===")

uduc_scope = "\n".join(
    [
        builder_source,
        write_source,
        read_source,
        build_write_source,
    ]
)

for marker in [
    "run_uploaded_document_to_highlight_pipeline",
    "run_highlight",
    "highlight_document",
    "highlight_engine",
]:
    check(
        "UDUC_CORE_NO_"
        + marker.upper(),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# E. UDUC core owns no ATS / registry
# ------------------------------------------------------------

print()
print("=== E. UDUC CORE VS ATS / REGISTRY ===")

for marker in [
    "run_uploaded_document_registry_to_active_target_set_pipeline",
    "active_target_set",
    "register_document",
    "update_registry",
    "write_registry",
]:
    check(
        "UDUC_CORE_NO_"
        + marker.upper(),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# F. Live coordinator inventory
# ------------------------------------------------------------

print()
print("=== F. LIVE COORDINATOR INVENTORY ===")

coordinator_lower = coordinator_source.lower()

check(
    "LIVE_COORDINATOR_HAS_U7_NORMALIZER",
    "normalize_uploaded_document_v1"
    in coordinator_lower,
)

check(
    "LIVE_COORDINATOR_HAS_CANONICAL_UDUC_BUILD_WRITE",
    "build_and_write_uduc_from_normalized_content"
    in coordinator_lower,
)

check(
    "LIVE_COORDINATOR_HAS_HIGHLIGHT_BRANCH",
    "run_uploaded_document_to_highlight_pipeline"
    in coordinator_lower,
)

check(
    "LIVE_COORDINATOR_HAS_REGISTRY_ATS_BRANCH",
    "run_uploaded_document_registry_to_active_target_set_pipeline"
    in coordinator_lower,
)


# ------------------------------------------------------------
# G. Live sequence ordering
# ------------------------------------------------------------

print()
print("=== G. LIVE SEQUENCE ORDER ===")

normalizer_pos = coordinator_lower.find(
    "normalize_uploaded_document_v1("
)

uduc_pos = coordinator_lower.find(
    "build_and_write_uduc_from_normalized_content("
)

highlight_pos = coordinator_lower.find(
    "run_uploaded_document_to_highlight_pipeline("
)

registry_ats_pos = coordinator_lower.find(
    "run_uploaded_document_registry_to_active_target_set_pipeline("
)

print(
    f"NORMALIZER_CALL_POS={normalizer_pos}"
)

print(
    f"UDUC_CALL_POS={uduc_pos}"
)

print(
    f"HIGHLIGHT_CALL_POS={highlight_pos}"
)

print(
    f"REGISTRY_ATS_CALL_POS={registry_ats_pos}"
)

check(
    "U7_PRECEDES_UDUC",
    normalizer_pos != -1
    and uduc_pos != -1
    and normalizer_pos < uduc_pos,
)

check(
    "UDUC_PRECEDES_HIGHLIGHT",
    uduc_pos != -1
    and highlight_pos != -1
    and uduc_pos < highlight_pos,
)

check(
    "UDUC_PRECEDES_REGISTRY_ATS",
    uduc_pos != -1
    and registry_ats_pos != -1
    and uduc_pos < registry_ats_pos,
)


# ------------------------------------------------------------
# H. UDUC success gate precedes downstream branches
# ------------------------------------------------------------

print()
print("=== H. UDUC SUCCESS GATE ===")

success_gate_pos = coordinator_lower.find(
    'if uduc_result.get("ok") is not true'
)

serialized_uduc_pos = coordinator_lower.find(
    'uduc = uduc_result.get("uduc")'
)

check(
    "UDUC_SUCCESS_GATE_PRESENT",
    success_gate_pos != -1,
)

check(
    "UDUC_SERIALIZED_PAYLOAD_VALIDATION_PRESENT",
    serialized_uduc_pos != -1,
)

check(
    "UDUC_SUCCESS_GATE_PRECEDES_HIGHLIGHT",
    success_gate_pos != -1
    and highlight_pos != -1
    and success_gate_pos < highlight_pos,
)

check(
    "UDUC_SUCCESS_GATE_PRECEDES_REGISTRY_ATS",
    success_gate_pos != -1
    and registry_ats_pos != -1
    and success_gate_pos < registry_ats_pos,
)


# ------------------------------------------------------------
# I. Highlight consumes extraction-derived content
# ------------------------------------------------------------

print()
print("=== I. HIGHLIGHT INPUT AUTHORITY ===")

check(
    "HIGHLIGHT_INPUT_DICTIONARY_PRESENT",
    "highlight_extraction_result = {"
    in coordinator_lower,
)

for marker in [
    '"title": extraction_title',
    '"text": extraction_text',
    '"source_format": extraction_source_format',
]:
    check(
        "HIGHLIGHT_USES_EXTRACTION_DERIVED_"
        + marker.split(":")[0]
        .replace('"', "")
        .upper(),
        marker.lower()
        in coordinator_lower,
    )

check(
    "HIGHLIGHT_RECEIVES_DEDICATED_EXTRACTION_RESULT",
    "extraction_result=highlight_extraction_result"
    in coordinator_lower,
)


# ------------------------------------------------------------
# J. ATS receives serialized UDUC
# ------------------------------------------------------------

print()
print("=== J. ATS INPUT AUTHORITY ===")

check(
    "REGISTRY_ATS_RECEIVES_UDUC",
    "unified_content=uduc"
    in coordinator_lower,
)

check(
    "UDUC_SERIALIZED_OBJECT_EXTRACTED_BEFORE_ATS",
    serialized_uduc_pos != -1
    and registry_ats_pos != -1
    and serialized_uduc_pos < registry_ats_pos,
)


# ------------------------------------------------------------
# K. Branch independence from UDUC core
# ------------------------------------------------------------

print()
print("=== K. BRANCH INDEPENDENCE ===")

check(
    "UDUC_MODULE_DOES_NOT_IMPORT_HIGHLIGHT_PIPELINE",
    "uploaded_document_to_highlight_pipeline"
    not in uduc_source.lower(),
)

check(
    "UDUC_MODULE_DOES_NOT_IMPORT_REGISTRY_ATS_PIPELINE",
    "uploaded_document_registry_to_active_target_set_pipeline"
    not in uduc_source.lower(),
)

check(
    "UDUC_MODULE_DOES_NOT_IMPORT_UPLOAD_COORDINATOR",
    "pipelines.upload_document.coordinator"
    not in uduc_source.lower(),
)


# ------------------------------------------------------------
# L. Legacy wrapper boundary
# ------------------------------------------------------------

print()
print("=== L. LEGACY WRAPPER BOUNDARY ===")

if legacy_wrapper_source:
    check(
        "LEGACY_WRAPPER_NO_HIGHLIGHT_EXECUTION",
        "highlight"
        not in legacy_wrapper_source.lower(),
    )

    check(
        "LEGACY_WRAPPER_NO_ATS_EXECUTION",
        "active_target_set"
        not in legacy_wrapper_source.lower(),
    )
else:
    check(
        "LEGACY_WRAPPER_NOT_PRESENT",
        True,
    )


# ------------------------------------------------------------
# M. No downstream semantic / scorer / UUCD
# ------------------------------------------------------------

print()
print("=== M. UDUC DOWNSTREAM BOUNDARY ===")

for marker in [
    "run_semantic",
    "semantic_runtime",
    "scorer",
    "build_uucd",
    "write_uucd",
    "current_canonical_uucd",
]:
    check(
        "UDUC_CORE_NO_"
        + marker.upper(),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# N. Failure cannot trigger Highlight / ATS inside UDUC
# ------------------------------------------------------------

print()
print("=== N. UDUC FAILURE BOUNDARY ===")

builder_tree = ast.parse(
    builder_source
)

downstream_in_builder_try = False

for node in ast.walk(
    builder_tree
):
    if isinstance(
        node,
        ast.Try,
    ):
        segment = (
            ast.get_source_segment(
                builder_source,
                node,
            )
            or ""
        ).lower()

        if (
            "highlight"
            in segment
            or "active_target_set"
            in segment
        ):
            downstream_in_builder_try = True

check(
    "UDUC_FAILURE_HAS_NO_HIGHLIGHT_FALLBACK",
    not downstream_in_builder_try,
)

check(
    "UDUC_FAILURE_HAS_NO_ATS_FALLBACK",
    not downstream_in_builder_try,
)


# ------------------------------------------------------------
# O. Final decision
# ------------------------------------------------------------

print()
print("=== O. U8.20 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.20_UDUC_VS_HIGHLIGHT_ATS_BOUNDARY: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.20 corrected boundary verification failed."
    )


print(
    "U8.20_UDUC_VS_HIGHLIGHT_ATS_BOUNDARY: CERTIFIED"
)

print(
    "U8.20_UDUC_OWNS: STRUCTURE_AND_PERSISTENCE_ONLY"
)

print(
    "U8.20_LIVE_SEQUENCE: U7_THEN_UDUC_THEN_SEPARATE_BRANCHES"
)

print(
    "U8.20_HIGHLIGHT_INPUT_AUTHORITY: EXTRACTION_DERIVED"
)

print(
    "U8.20_HIGHLIGHT_EXECUTION_INSIDE_UDUC: NO"
)

print(
    "U8.20_ATS_INPUT: SERIALIZED_CANONICAL_UDUC"
)

print(
    "U8.20_ATS_EXECUTION_INSIDE_UDUC: NO"
)

print(
    "U8.20_REGISTRY_OWNERSHIP_INSIDE_UDUC: NO"
)

print(
    "U8.20_UDUC_FAILURE_DOWNSTREAM_FALLBACK: NO"
)

print(
    "U8.20_SEMANTIC_SCORER_UUCD_EXECUTION: NO"
)

print(
    "U8.20_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U8.21_UDUC_VS_CURRENT_CANONICAL_UUCD_BOUNDARY_TRANSITION: AUTHORIZED"
)

print(
    "U8.20_FINAL_BOUNDARY_VERIFICATION: PASS"
)