from pathlib import Path
import ast
import py_compile


print("=== U9.1 CURRENT CANONICAL UUCD CONTRACT DISCOVERY ===")


# ------------------------------------------------------------
# A. Canonical files
# ------------------------------------------------------------

print()
print("=== A. CANONICAL UUCD FILES ===")

engine_path = Path(
    "backend/server/"
    "universal_unified_content_document/"
    "uucd_engine_v1.py"
)

persistence_path = Path(
    "backend/server/"
    "universal_unified_content_document/"
    "uucd_persistence_v1.py"
)

for label, path in [
    ("UUCD_ENGINE", engine_path),
    ("UUCD_PERSISTENCE", persistence_path),
]:
    print(
        f"{label}_PATH={path}"
    )
    print(
        f"{label}_EXISTS={path.exists()}"
    )

    if path.exists():
        try:
            py_compile.compile(
                str(path),
                doraise=True,
            )
            print(
                f"{label}_COMPILES=PASS"
            )
        except Exception as exc:
            print(
                f"{label}_COMPILES=FAIL"
            )
            print(
                f"{label}_COMPILE_ERROR="
                f"{type(exc).__name__}: {exc}"
            )


# ------------------------------------------------------------
# B. Engine top-level inventory
# ------------------------------------------------------------

print()
print("=== B. UUCD ENGINE INVENTORY ===")

if engine_path.exists():
    engine_source = engine_path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    engine_tree = ast.parse(
        engine_source
    )

    for node in engine_tree.body:
        if isinstance(
            node,
            ast.ClassDef,
        ):
            print(
                f"ENGINE_CLASS: {node.name}"
            )

        elif isinstance(
            node,
            ast.FunctionDef,
        ):
            print(
                f"ENGINE_FUNCTION: {node.name}"
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

                    if any(
                        marker
                        in name.upper()
                        for marker in [
                            "UUCD",
                            "SCHEMA",
                            "VERSION",
                            "PIPELINE",
                        ]
                    ):
                        print(
                            f"ENGINE_CONSTANT: {name}"
                        )


# ------------------------------------------------------------
# C. Persistence top-level inventory
# ------------------------------------------------------------

print()
print("=== C. UUCD PERSISTENCE INVENTORY ===")

if persistence_path.exists():
    persistence_source = (
        persistence_path.read_text(
            encoding="utf-8-sig",
            errors="ignore",
        )
    )

    persistence_tree = ast.parse(
        persistence_source
    )

    for node in persistence_tree.body:
        if isinstance(
            node,
            ast.ClassDef,
        ):
            print(
                f"PERSISTENCE_CLASS: {node.name}"
            )

        elif isinstance(
            node,
            ast.FunctionDef,
        ):
            print(
                f"PERSISTENCE_FUNCTION: {node.name}"
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

                    if any(
                        marker
                        in name.upper()
                        for marker in [
                            "UUCD",
                            "PATH",
                            "DIR",
                            "SCHEMA",
                            "VERSION",
                        ]
                    ):
                        print(
                            f"PERSISTENCE_CONSTANT: {name}"
                        )


# ------------------------------------------------------------
# D. Dataclass / class field discovery
# ------------------------------------------------------------

print()
print("=== D. UUCD OUTPUT FIELD DISCOVERY ===")


def print_class_fields(
    source,
    tree,
    prefix,
):
    for node in tree.body:
        if not isinstance(
            node,
            ast.ClassDef,
        ):
            continue

        print()
        print(
            f"--- {prefix}_CLASS {node.name} ---"
        )

        annotated = []

        for item in node.body:
            if isinstance(
                item,
                ast.AnnAssign,
            ) and isinstance(
                item.target,
                ast.Name,
            ):
                annotated.append(
                    item.target.id
                )

        print(
            f"ANNOTATED_FIELD_COUNT="
            f"{len(annotated)}"
        )

        for index, name in enumerate(
            annotated,
            start=1,
        ):
            print(
                f"FIELD_{index}: {name}"
            )


if engine_path.exists():
    print_class_fields(
        engine_source,
        engine_tree,
        "ENGINE",
    )

if persistence_path.exists():
    print_class_fields(
        persistence_source,
        persistence_tree,
        "PERSISTENCE",
    )


# ------------------------------------------------------------
# E. Exact likely builder / serializer sources
# ------------------------------------------------------------

print()
print("=== E. LIKELY UUCD BUILDER / SERIALIZER FUNCTIONS ===")


def function_source(
    source,
    tree,
    name,
):
    node = next(
        (
            item
            for item in tree.body
            if isinstance(
                item,
                ast.FunctionDef,
            )
            and item.name == name
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


if engine_path.exists():
    for node in engine_tree.body:
        if not isinstance(
            node,
            ast.FunctionDef,
        ):
            continue

        lower = node.name.lower()

        if any(
            marker in lower
            for marker in [
                "build",
                "create",
                "convert",
                "uucd",
                "serialize",
            ]
        ):
            print()
            print(
                f"--- ENGINE FUNCTION {node.name} ---"
            )
            print(
                function_source(
                    engine_source,
                    engine_tree,
                    node.name,
                )
            )


# ------------------------------------------------------------
# F. Exact persistence functions
# ------------------------------------------------------------

print()
print("=== F. LIKELY UUCD PERSISTENCE FUNCTIONS ===")

if persistence_path.exists():
    for node in persistence_tree.body:
        if not isinstance(
            node,
            ast.FunctionDef,
        ):
            continue

        lower = node.name.lower()

        if any(
            marker in lower
            for marker in [
                "write",
                "read",
                "save",
                "load",
                "persist",
                "path",
                "uucd",
            ]
        ):
            print()
            print(
                f"--- PERSISTENCE FUNCTION {node.name} ---"
            )
            print(
                function_source(
                    persistence_source,
                    persistence_tree,
                    node.name,
                )
            )


# ------------------------------------------------------------
# G. Production caller scan
# ------------------------------------------------------------

print()
print("=== G. PRODUCTION UUCD CALLER SCAN ===")

excluded_parts = {
    "backups",
    "runtime_backups",
    "verification_scans",
    "__pycache__",
}

markers = [
    "uucd_engine_v1",
    "uucd_persistence_v1",
    "build_uucd",
    "write_uucd",
    "persist_uucd",
    "read_uucd",
    "load_uucd",
    "universal_unified_content_document",
]

hits = []

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

    if path in {
        engine_path,
        persistence_path,
    }:
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

        for marker in markers:
            if marker.lower() in lower:
                hits.append(
                    (
                        marker,
                        str(path),
                        line_number,
                        line.strip(),
                    )
                )


print(
    "PRODUCTION_UUCD_REFERENCE_COUNT="
    + str(len(hits))
)

for marker, path, line_number, line in hits:
    print(
        f"UUCD_REFERENCE: {marker}: "
        f"{path}:{line_number}: {line}"
    )


# ------------------------------------------------------------
# H. Persistence/data path references
# ------------------------------------------------------------

print()
print("=== H. UUCD DATA PATH REFERENCES ===")

path_markers = [
    "universal_unified_content_documents",
    "uucd",
]

path_hits = []

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
            for marker in path_markers
        ):
            path_hits.append(
                (
                    str(path),
                    line_number,
                    line.strip(),
                )
            )


print(
    "UUCD_DATA_PATH_REFERENCE_COUNT="
    + str(len(path_hits))
)

for path, line_number, line in path_hits:
    print(
        f"UUCD_DATA_PATH_REFERENCE: "
        f"{path}:{line_number}: {line}"
    )


# ------------------------------------------------------------
# I. Legacy / competing UUCD candidates
# ------------------------------------------------------------

print()
print("=== I. LEGACY / COMPETING UUCD CANDIDATES ===")

candidates = []

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

    if path in {
        engine_path,
        persistence_path,
    }:
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    lower = text.lower()

    if (
        "universalunifiedcontentdocument"
        in lower
        or "build_uucd"
        in lower
        or "write_uucd"
        in lower
        or "persist_uucd"
        in lower
    ):
        candidates.append(
            str(path)
        )


print(
    "UUCD_COMPETING_CANDIDATE_COUNT="
    + str(len(candidates))
)

for path in candidates:
    print(
        f"UUCD_COMPETING_CANDIDATE: {path}"
    )


# ------------------------------------------------------------
# J. U9.1 discovery decision
# ------------------------------------------------------------

print()
print("=== J. U9.1 DISCOVERY SUMMARY ===")

print(
    "U9.1_CURRENT_CANONICAL_UUCD_ENGINE="
    + str(engine_path)
)

print(
    "U9.1_CURRENT_CANONICAL_UUCD_PERSISTENCE="
    + str(persistence_path)
)

print(
    "U9.1_PRODUCTION_REFERENCE_COUNT="
    + str(len(hits))
)

print(
    "U9.1_COMPETING_CANDIDATE_COUNT="
    + str(len(candidates))
)

print(
    "U9.1_PATCH_DECISION: PENDING_CONTRACT_CLASSIFICATION"
)

print(
    "U9.1_NEXT_STEP: REVIEW_DISCOVERED_CURRENT_CANONICAL_UUCD_CONTRACT"
)