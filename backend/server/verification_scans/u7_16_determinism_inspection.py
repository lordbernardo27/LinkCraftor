from pathlib import Path
import ast

target = Path(
    "backend/server/stores/upload_document_normalizer.py"
)

source = target.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)

print("=== U7.16 DETERMINISM INSPECTION ===")
print("FILE=", target)

print()
print("=== IMPORTS ===")

for node in tree.body:
    if isinstance(
        node,
        (
            ast.Import,
            ast.ImportFrom,
        ),
    ):
        print(
            ast.get_source_segment(
                source,
                node,
            )
        )


forbidden_import_roots = {
    "random",
    "secrets",
    "uuid",
    "requests",
    "httpx",
    "socket",
    "subprocess",
    "sqlite3",
    "sqlalchemy",
    "os",
}

found_forbidden_imports = []

for node in tree.body:
    if isinstance(node, ast.Import):
        for alias in node.names:
            root = alias.name.split(".")[0]

            if root in forbidden_import_roots:
                found_forbidden_imports.append(
                    alias.name
                )

    elif isinstance(node, ast.ImportFrom):
        module = node.module or ""
        root = module.split(".")[0]

        if root in forbidden_import_roots:
            found_forbidden_imports.append(
                module
            )

print()
print(
    "FORBIDDEN_NONDETERMINISTIC_IMPORT_COUNT=",
    len(found_forbidden_imports),
)

for value in found_forbidden_imports:
    print(
        "FORBIDDEN_IMPORT=",
        value,
    )


print()
print("=== NONDETERMINISTIC / EXTERNAL CALLS ===")

external_calls = []

for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue

    call = (
        ast.get_source_segment(
            source,
            node,
        )
        or ""
    )

    lowered = call.lower()

    forbidden_terms = (
        "random.",
        "secrets.",
        "uuid.",
        "requests.",
        "httpx.",
        "socket.",
        "subprocess.",
        "sqlite3.",
        "sqlalchemy.",
        "os.getenv",
        "os.environ",
        "read_text(",
        "read_bytes(",
        "open(",
    )

    if any(
        term in lowered
        for term in forbidden_terms
    ):
        external_calls.append(
            (
                getattr(
                    node,
                    "lineno",
                    None,
                ),
                call,
            )
        )

for line, call in external_calls:
    print(
        f"LINE {line}: {call}"
    )

print(
    "NONDETERMINISTIC_EXTERNAL_CALL_COUNT=",
    len(external_calls),
)


print()
print("=== CURRENT-TIME USAGE ===")

time_calls = []

for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue

    call = (
        ast.get_source_segment(
            source,
            node,
        )
        or ""
    )

    if (
        "datetime.now" in call
        or "datetime.utcnow" in call
        or "time.time" in call
    ):
        time_calls.append(
            (
                getattr(
                    node,
                    "lineno",
                    None,
                ),
                call,
            )
        )

for line, call in time_calls:
    print(
        f"LINE {line}: {call}"
    )

print(
    "CURRENT_TIME_CALL_COUNT=",
    len(time_calls),
)


print()
print("=== CONTENT TRANSFORM TIME DEPENDENCY ===")

fn = next(
    node
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
    and node.name
    == "normalize_uploaded_document_v1"
)

fn_source = (
    ast.get_source_segment(
        source,
        fn,
    )
    or ""
)

content_time_dependency = (
    "datetime.now" in fn_source
    or "datetime.utcnow" in fn_source
    or "time.time" in fn_source
)

print(
    "CONTENT_TRANSFORM_TIME_DEPENDENCY=",
    "YES"
    if content_time_dependency
    else "NO",
)


print()
print("=== DETERMINISM INSPECTION DECISION ===")

print(
    "U7.16_FORBIDDEN_RANDOMNESS_DEPENDENCY:",
    "NO"
    if not found_forbidden_imports
    else "YES",
)

print(
    "U7.16_EXTERNAL_STATE_CONTENT_DEPENDENCY:",
    "NO"
    if not external_calls
    else "YES",
)

print(
    "U7.16_NORMALIZED_AT_PROVENANCE_TIME_ALLOWED:",
    "YES",
)

print(
    "U7.16_CONTENT_TRANSFORM_TIME_DEPENDENCY:",
    "NO"
    if not content_time_dependency
    else "YES",
)