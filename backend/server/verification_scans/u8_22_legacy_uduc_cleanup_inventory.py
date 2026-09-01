from pathlib import Path
import ast
import py_compile


print("=== U8.22 LEGACY UDUC CLEANUP INVENTORY ===")


# ------------------------------------------------------------
# A. Canonical module
# ------------------------------------------------------------

uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

print()
print("=== A. CANONICAL UDUC MODULE ===")
print(f"UDUC_MODULE={uduc_path}")

if not uduc_path.exists():
    raise RuntimeError(
        "Canonical UDUC module not found."
    )

py_compile.compile(
    str(uduc_path),
    doraise=True,
)

print("UDUC_MODULE_COMPILES: PASS")


source = uduc_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

tree = ast.parse(
    source
)


# ------------------------------------------------------------
# B. Top-level UDUC functions/classes/constants
# ------------------------------------------------------------

print()
print("=== B. CANONICAL MODULE INVENTORY ===")

for node in tree.body:
    if isinstance(
        node,
        ast.ClassDef,
    ):
        print(
            f"CLASS: {node.name}"
        )

    elif isinstance(
        node,
        ast.FunctionDef,
    ):
        print(
            f"FUNCTION: {node.name}"
        )

    elif isinstance(
        node,
        ast.Assign,
    ):
        for target in node.targets:
            if isinstance(
                target,
                ast.Name,
            ):
                name = target.id

                if (
                    "UDUC" in name.upper()
                    or "SCHEMA" in name.upper()
                    or "PIPELINE" in name.upper()
                ):
                    print(
                        f"CONSTANT: {name}"
                    )


# ------------------------------------------------------------
# C. Exact compatibility wrapper implementations
# ------------------------------------------------------------

print()
print("=== C. COMPATIBILITY WRAPPERS ===")


def function_source(name: str) -> str:
    node = next(
        (
            n
            for n in tree.body
            if isinstance(
                n,
                ast.FunctionDef,
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


for name in [
    "build_uduc_from_extraction_result",
    "build_and_write_uduc_from_extraction_result",
]:
    body = function_source(
        name
    )

    if body:
        print()
        print(
            f"--- {name} ---"
        )
        print(
            body
        )
    else:
        print(
            f"{name}: NOT_PRESENT"
        )


# ------------------------------------------------------------
# D. Production caller scan
# ------------------------------------------------------------

print()
print("=== D. PRODUCTION CALLER SCAN ===")

search_roots = [
    Path("backend/server"),
]

excluded_parts = {
    "backups",
    "verification_scans",
    "__pycache__",
}

targets = [
    "build_uduc_from_normalized_content",
    "build_and_write_uduc_from_normalized_content",
    "build_uduc_from_extraction_result",
    "build_and_write_uduc_from_extraction_result",
    "write_uduc",
    "read_uduc",
]

hits = {
    target: []
    for target in targets
}


for root in search_roots:
    for path in root.rglob(
        "*.py"
    ):
        if any(
            part in excluded_parts
            for part in path.parts
        ):
            continue

        if path == uduc_path:
            continue

        text = path.read_text(
            encoding="utf-8-sig",
            errors="ignore",
        )

        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):
            for target in targets:
                if target in line:
                    hits[target].append(
                        (
                            str(path),
                            line_number,
                            line.strip(),
                        )
                    )


for target in targets:
    print()
    print(
        f"TARGET={target}"
    )

    print(
        f"PRODUCTION_HIT_COUNT={len(hits[target])}"
    )

    for path, line_number, line in hits[target]:
        print(
            f"HIT: {path}:{line_number}: {line}"
        )


# ------------------------------------------------------------
# E. Legacy schema/pipeline/version strings
# ------------------------------------------------------------

print()
print("=== E. LEGACY VERSION STRING INVENTORY ===")

legacy_markers = [
    "uploaded_document_unified_content_v1",
    "uploaded_document_uduc_pipeline_v1",
    "uduc_structure_v1",
    "uduc_structure_v1_1",
]

legacy_hits = []

for path in Path(
    "backend/server"
).rglob(
    "*.py"
):
    if any(
        part in excluded_parts
        for part in path.parts
    ):
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        lower = line.lower()

        for marker in legacy_markers:
            if marker.lower() in lower:
                legacy_hits.append(
                    (
                        marker,
                        str(path),
                        line_number,
                        line.strip(),
                    )
                )


print(
    f"LEGACY_VERSION_HIT_COUNT={len(legacy_hits)}"
)

for marker, path, line_number, line in legacy_hits:
    print(
        f"LEGACY_VERSION_HIT: {marker}: "
        f"{path}:{line_number}: {line}"
    )


# ------------------------------------------------------------
# F. Preview/pseudo-UDUC remnants
# ------------------------------------------------------------

print()
print("=== F. PREVIEW / PSEUDO-UDUC REMNANT INVENTORY ===")

pseudo_markers = [
    "pseudo-unified-content",
    "preview-derived",
    "preview_derived",
    "pseudo_uduc",
    "hand-built",
    "hand_built",
]

pseudo_hits = []

for path in Path(
    "backend/server/pipelines/upload_document"
).rglob(
    "*.py"
):
    if any(
        part in excluded_parts
        for part in path.parts
    ):
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        lower = line.lower()

        if any(
            marker in lower
            for marker in pseudo_markers
        ):
            pseudo_hits.append(
                (
                    str(path),
                    line_number,
                    line.strip(),
                )
            )


print(
    f"PSEUDO_UDUC_REFERENCE_COUNT={len(pseudo_hits)}"
)

for path, line_number, line in pseudo_hits:
    print(
        f"PSEUDO_UDUC_REFERENCE: "
        f"{path}:{line_number}: {line}"
    )


# ------------------------------------------------------------
# G. Potential duplicate UDUC implementations
# ------------------------------------------------------------

print()
print("=== G. DUPLICATE IMPLEMENTATION INVENTORY ===")

duplicate_candidates = []

for path in Path(
    "backend/server"
).rglob(
    "*.py"
):
    if any(
        part in excluded_parts
        for part in path.parts
    ):
        continue

    if path == uduc_path:
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    lower = text.lower()

    if (
        "uploadeddocumentunifiedcontent"
        in lower
        or "build_uduc"
        in lower
        or "write_uduc"
        in lower
        or "read_uduc"
        in lower
    ):
        duplicate_candidates.append(
            str(path)
        )


print(
    f"DUPLICATE_CANDIDATE_COUNT={len(duplicate_candidates)}"
)

for path in duplicate_candidates:
    print(
        f"DUPLICATE_CANDIDATE: {path}"
    )


# ------------------------------------------------------------
# H. Production data-path references
# ------------------------------------------------------------

print()
print("=== H. UDUC DATA PATH INVENTORY ===")

data_path_markers = [
    "uploaded_document_unified_content",
    "data/uploads",
]

data_path_hits = []

for path in Path(
    "backend/server"
).rglob(
    "*.py"
):
    if any(
        part in excluded_parts
        for part in path.parts
    ):
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        lower = line.lower()

        if any(
            marker in lower
            for marker in data_path_markers
        ):
            data_path_hits.append(
                (
                    str(path),
                    line_number,
                    line.strip(),
                )
            )


print(
    f"UDUC_DATA_PATH_REFERENCE_COUNT={len(data_path_hits)}"
)

for path, line_number, line in data_path_hits:
    print(
        f"UDUC_DATA_PATH_REFERENCE: "
        f"{path}:{line_number}: {line}"
    )


# ------------------------------------------------------------
# I. Summary classification
# ------------------------------------------------------------

print()
print("=== I. U8.22 INVENTORY SUMMARY ===")

print(
    "CANONICAL_NORMALIZED_BUILDER_CALLERS="
    + str(
        len(
            hits[
                "build_uduc_from_normalized_content"
            ]
        )
    )
)

print(
    "CANONICAL_NORMALIZED_BUILD_WRITE_CALLERS="
    + str(
        len(
            hits[
                "build_and_write_uduc_from_normalized_content"
            ]
        )
    )
)

print(
    "LEGACY_EXTRACTION_BUILDER_CALLERS="
    + str(
        len(
            hits[
                "build_uduc_from_extraction_result"
            ]
        )
    )
)

print(
    "LEGACY_EXTRACTION_BUILD_WRITE_CALLERS="
    + str(
        len(
            hits[
                "build_and_write_uduc_from_extraction_result"
            ]
        )
    )
)

print(
    "U8.22_PATCH_DECISION: PENDING_CLASSIFICATION"
)

print(
    "U8.22_NEXT_STEP: REVIEW_INVENTORY_BEFORE_ANY_REMOVAL"
)