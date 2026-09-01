from pathlib import Path
import ast
import py_compile


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U8.20 UDUC VS HIGHLIGHT / ATS BOUNDARY VERIFICATION ===")


# ------------------------------------------------------------
# A. Canonical file inventory
# ------------------------------------------------------------

print()
print("=== A. FILE INVENTORY ===")

uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

coordinator_path = Path(
    "backend/server/pipelines/upload_document/"
    "uploaded_document_to_uduc_pipeline/"
    "coordinator.py"
)

check(
    "UDUC_MODULE_EXISTS",
    uduc_path.exists(),
)

check(
    "UPLOAD_TO_UDUC_COORDINATOR_EXISTS",
    coordinator_path.exists(),
)


# ------------------------------------------------------------
# B. Compile
# ------------------------------------------------------------

print()
print("=== B. COMPILE ===")

for label, path in [
    ("UDUC_MODULE", uduc_path),
    ("UPLOAD_TO_UDUC_COORDINATOR", coordinator_path),
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
# C. Source extraction
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

legacy_build_write_source = function_source(
    uduc_tree,
    uduc_source,
    "build_and_write_uduc_from_extraction_result",
)


for label, source_value in [
    ("BUILDER", builder_source),
    ("WRITE", write_source),
    ("READ", read_source),
    ("BUILD_AND_WRITE", build_write_source),
]:
    check(
        f"{label}_SOURCE_EXTRACTED",
        bool(
            source_value
        ),
    )


# ------------------------------------------------------------
# D. Canonical UDUC scope: no Highlight
# ------------------------------------------------------------

print()
print("=== D. CANONICAL UDUC HAS NO HIGHLIGHT EXECUTION ===")

uduc_scope = "\n".join(
    [
        builder_source,
        write_source,
        read_source,
        build_write_source,
    ]
)

highlight_markers = [
    "run_highlight",
    "highlight_document",
    "highlight_pipeline",
    "highlight_engine",
    "uploaded_document_highlight",
]

for marker in highlight_markers:
    check(
        "UDUC_SCOPE_NO_"
        + marker.upper(),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# E. Canonical UDUC scope: no ATS
# ------------------------------------------------------------

print()
print("=== E. CANONICAL UDUC HAS NO ATS EXECUTION ===")

ats_markers = [
    "active_target_set",
    "run_active_target_set",
    "build_active_target_set",
    "refresh_active_target_set",
    "update_active_target_set",
]

for marker in ats_markers:
    check(
        "UDUC_SCOPE_NO_"
        + marker.upper(),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# F. No registry ownership inside UDUC core
# ------------------------------------------------------------

print()
print("=== F. UDUC CORE DOES NOT OWN REGISTRY UPDATE ===")

registry_markers = [
    "registry",
    "register_document",
    "update_registry",
    "write_registry",
]

for marker in registry_markers:
    check(
        "UDUC_SCOPE_NO_REGISTRY_MARKER_"
        + marker.upper(),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# G. Coordinator branch inventory
# ------------------------------------------------------------

print()
print("=== G. COORDINATOR BRANCH INVENTORY ===")

coordinator_lower = coordinator_source.lower()

print(
    "COORDINATOR_HAS_NORMALIZER="
    + str(
        "normalize_uploaded_document_v1"
        in coordinator_lower
    )
)

print(
    "COORDINATOR_HAS_UDUC_BUILD_WRITE="
    + str(
        "build_and_write_uduc_from_normalized_content"
        in coordinator_lower
    )
)

print(
    "COORDINATOR_HAS_HIGHLIGHT_MARKER="
    + str(
        "highlight"
        in coordinator_lower
    )
)

print(
    "COORDINATOR_HAS_ACTIVE_TARGET_SET_MARKER="
    + str(
        "active_target_set"
        in coordinator_lower
    )
)

print(
    "COORDINATOR_HAS_REGISTRY_MARKER="
    + str(
        "registry"
        in coordinator_lower
    )
)


check(
    "COORDINATOR_CALLS_U7_NORMALIZER",
    "normalize_uploaded_document_v1"
    in coordinator_lower,
)

check(
    "COORDINATOR_CALLS_CANONICAL_UDUC_BUILD_WRITE",
    "build_and_write_uduc_from_normalized_content"
    in coordinator_lower,
)


# ------------------------------------------------------------
# H. Coordinator ordering evidence
# ------------------------------------------------------------

print()
print("=== H. COORDINATOR ORDERING EVIDENCE ===")

normalizer_pos = coordinator_lower.find(
    "normalize_uploaded_document_v1"
)

uduc_pos = coordinator_lower.find(
    "build_and_write_uduc_from_normalized_content"
)

highlight_pos = coordinator_lower.find(
    "highlight"
)

registry_pos = coordinator_lower.find(
    "registry"
)

ats_pos = coordinator_lower.find(
    "active_target_set"
)

print(
    f"NORMALIZER_POS={normalizer_pos}"
)

print(
    f"UDUC_POS={uduc_pos}"
)

print(
    f"HIGHLIGHT_POS={highlight_pos}"
)

print(
    f"REGISTRY_POS={registry_pos}"
)

print(
    f"ATS_POS={ats_pos}"
)


check(
    "U7_PRECEDES_UDUC",
    normalizer_pos
    != -1
    and uduc_pos
    != -1
    and normalizer_pos
    < uduc_pos,
)


# ------------------------------------------------------------
# I. Highlight separation
# ------------------------------------------------------------

print()
print("=== I. HIGHLIGHT BRANCH SEPARATION ===")

if highlight_pos == -1:
    print(
        "HIGHLIGHT_CLASSIFICATION=NOT_PRESENT_IN_THIS_COORDINATOR"
    )

    check(
        "HIGHLIGHT_NOT_EMBEDDED_IN_UDUC_CORE",
        True,
    )

else:
    print(
        "HIGHLIGHT_CLASSIFICATION=COORDINATOR_LEVEL_OR_IMPORTED_BRANCH"
    )

    check(
        "HIGHLIGHT_NOT_EMBEDDED_IN_UDUC_CORE",
        all(
            marker.lower()
            not in uduc_scope.lower()
            for marker in highlight_markers
        ),
    )


# ------------------------------------------------------------
# J. ATS / registry separation
# ------------------------------------------------------------

print()
print("=== J. ATS / REGISTRY BRANCH SEPARATION ===")

if (
    registry_pos == -1
    and ats_pos == -1
):
    print(
        "ATS_REGISTRY_CLASSIFICATION="
        "NOT_PRESENT_IN_THIS_COORDINATOR"
    )

    check(
        "ATS_NOT_EMBEDDED_IN_UDUC_CORE",
        True,
    )

else:
    print(
        "ATS_REGISTRY_CLASSIFICATION="
        "COORDINATOR_LEVEL_OR_DOWNSTREAM_BRANCH"
    )

    check(
        "ATS_NOT_EMBEDDED_IN_UDUC_CORE",
        all(
            marker.lower()
            not in uduc_scope.lower()
            for marker in ats_markers
        ),
    )


# ------------------------------------------------------------
# K. Serialized UDUC handoff probe
# ------------------------------------------------------------

print()
print("=== K. SERIALIZED UDUC HANDOFF PROBE ===")

serialization_markers = [
    "serialize_uduc",
    "serialized_uduc",
    "uduc_payload",
    "uduc_data",
]

serialization_hits = [
    marker
    for marker in serialization_markers
    if marker.lower()
    in coordinator_lower
]

print(
    "COORDINATOR_UDUC_SERIALIZATION_MARKERS="
    + repr(
        serialization_hits
    )
)

check(
    "UDUC_SERIALIZATION_DOES_NOT_EXECUTE_ATS_INSIDE_UDUC_CORE",
    all(
        marker.lower()
        not in uduc_scope.lower()
        for marker in ats_markers
    ),
)


# ------------------------------------------------------------
# L. No circular import from UDUC core to coordinator
# ------------------------------------------------------------

print()
print("=== L. CIRCULAR DEPENDENCY CHECK ===")

check(
    "UDUC_MODULE_DOES_NOT_IMPORT_UPLOAD_COORDINATOR",
    "uploaded_document_to_uduc_pipeline"
    not in uduc_source.lower(),
)

check(
    "UDUC_MODULE_DOES_NOT_IMPORT_HIGHLIGHT_BRANCH",
    "highlight"
    not in uduc_source.lower(),
)

check(
    "UDUC_MODULE_DOES_NOT_IMPORT_ACTIVE_TARGET_SET",
    "active_target_set"
    not in uduc_source.lower(),
)


# ------------------------------------------------------------
# M. Legacy wrapper boundary
# ------------------------------------------------------------

print()
print("=== M. LEGACY WRAPPER BOUNDARY ===")

if legacy_build_write_source:
    print(
        "LEGACY_BUILD_WRITE_WRAPPER_PRESENT=YES"
    )

    check(
        "LEGACY_WRAPPER_NO_HIGHLIGHT_EXECUTION",
        "highlight"
        not in legacy_build_write_source.lower(),
    )

    check(
        "LEGACY_WRAPPER_NO_ATS_EXECUTION",
        "active_target_set"
        not in legacy_build_write_source.lower(),
    )

else:
    print(
        "LEGACY_BUILD_WRITE_WRAPPER_PRESENT=NO"
    )

    check(
        "LEGACY_WRAPPER_BOUNDARY_NOT_APPLICABLE",
        True,
    )


# ------------------------------------------------------------
# N. Failure does not trigger downstream work
# ------------------------------------------------------------

print()
print("=== N. FAILURE DOES NOT TRIGGER DOWNSTREAM WORK ===")

builder_has_try_downstream = False

for node in ast.walk(
    ast.parse(
        builder_source
    )
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
            builder_has_try_downstream = True


check(
    "UDUC_FAILURE_PATH_HAS_NO_HIGHLIGHT_FALLBACK",
    not builder_has_try_downstream,
)

check(
    "UDUC_FAILURE_PATH_HAS_NO_ATS_FALLBACK",
    not builder_has_try_downstream,
)


# ------------------------------------------------------------
# O. No semantic / scorer / UUCD work
# ------------------------------------------------------------

print()
print("=== O. UDUC DOWNSTREAM BOUNDARY ===")

for marker in [
    "run_semantic",
    "semantic_runtime",
    "scorer",
    "build_uucd",
    "write_uucd",
    "current_canonical_uucd",
]:
    check(
        "UDUC_SCOPE_NO_"
        + marker.upper(),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# P. Narrow source evidence around branch markers
# ------------------------------------------------------------

print()
print("=== P. COORDINATOR BRANCH CONTEXT ===")

coord_lines = coordinator_source.splitlines()

interesting = []

for i, line in enumerate(
    coord_lines
):
    lower = line.lower()

    if (
        "normalize_uploaded_document_v1"
        in lower
        or "build_and_write_uduc_from_normalized_content"
        in lower
        or "highlight"
        in lower
        or "registry"
        in lower
        or "active_target_set"
        in lower
    ):
        interesting.append(
            i
        )


printed = set()

for i in interesting:
    start = max(
        0,
        i - 3,
    )

    end = min(
        len(
            coord_lines
        ),
        i + 5,
    )

    key = (
        start,
        end,
    )

    if key in printed:
        continue

    printed.add(
        key
    )

    print(
        "---"
    )

    for j in range(
        start,
        end,
    ):
        print(
            f"{j + 1}: {coord_lines[j]}"
        )


# ------------------------------------------------------------
# Q. Final decision
# ------------------------------------------------------------

print()
print("=== Q. U8.20 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.20_UDUC_VS_HIGHLIGHT_ATS_BOUNDARY: REVIEW_REQUIRED"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    print(
        "U8.20_PATCH_DECISION_REQUIRED: REVIEW_EVIDENCE"
    )

else:
    print(
        "U8.20_UDUC_VS_HIGHLIGHT_ATS_BOUNDARY: CERTIFIED"
    )

    print(
        "U8.20_UDUC_OWNS: STRUCTURE_AND_UDUC_PERSISTENCE_ONLY"
    )

    print(
        "U8.20_HIGHLIGHT_EXECUTION_INSIDE_UDUC: NO"
    )

    print(
        "U8.20_ATS_EXECUTION_INSIDE_UDUC: NO"
    )

    print(
        "U8.20_REGISTRY_OWNERSHIP_INSIDE_UDUC: NO"
    )

    print(
        "U8.20_HIGHLIGHT_BRANCH: SEPARATE"
    )

    print(
        "U8.20_ATS_REGISTRY_BRANCH: SEPARATE"
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