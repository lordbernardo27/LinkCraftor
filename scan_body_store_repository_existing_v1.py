from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

BODY_STORE_PACKAGE = (
    SERVER_ROOT
    / "universal_article_body_store"
)

CANDIDATE_NAMES = {
    "body_store_repository.py",
    "body_store_repository_v1.py",
    "repository.py",
    "repository_v1.py",
    "universal_article_body_store_repository.py",
    "universal_article_body_store_repository_v1.py",
}

REPOSITORY_FUNCTIONS = {
    "store_body",
    "write_body",
    "read_body",
    "get_body",
    "verify_body",
    "body_exists",
    "get_metadata",
    "list_workspace_bodies",
}

WRITER_FUNCTIONS = {
    "write_verified_body_from_envelope_v1",
}

MANAGER_FUNCTIONS = {
    "locate_body",
    "read_body",
    "verify_stored_body",
    "body_exists",
    "get_body_metadata",
    "list_workspace_bodies",
}


def relative(
    path: Path,
) -> str:
    return path.resolve().relative_to(
        PROJECT_ROOT
    ).as_posix()


candidate_files = []

if BODY_STORE_PACKAGE.exists():
    for path in BODY_STORE_PACKAGE.rglob(
        "*.py"
    ):
        if path.name in CANDIDATE_NAMES:
            candidate_files.append(
                path
            )


for path in SERVER_ROOT.rglob(
    "*.py"
):
    if any(
        part in {
            ".venv",
            ".git",
            "__pycache__",
            "backups",
            "runtime_backups",
            "node_modules",
        }
        for part in path.parts
    ):
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    lowered = source.casefold()

    if (
        "body_store_repository"
        in lowered
        or "universal_article_body_store_repository"
        in lowered
    ):
        candidate_files.append(
            path
        )


candidate_files = sorted(
    set(
        candidate_files
    ),
    key=relative,
)

results = []
failures = []

for path in candidate_files:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

    try:
        tree = ast.parse(
            source,
            filename=str(
                path
            ),
        )

    except SyntaxError as exc:
        failures.append(
            relative(
                path
            )
            + ": "
            + str(
                exc
            )
        )

        continue

    functions = []
    imports = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            functions.append(
                {
                    "name":
                        node.name,

                    "line":
                        node.lineno,
                }
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            imports.append(
                {
                    "module":
                        node.module,

                    "names":
                        [
                            alias.name
                            for alias in node.names
                        ],

                    "line":
                        node.lineno,
                }
            )

    repository_functions = sorted(
        item[
            "name"
        ]
        for item in functions
        if item[
            "name"
        ]
        in REPOSITORY_FUNCTIONS
    )

    writer_imports = []

    manager_imports = []

    for item in imports:
        imported_names = set(
            item[
                "names"
            ]
        )

        if imported_names & WRITER_FUNCTIONS:
            writer_imports.append(
                item
            )

        if imported_names & MANAGER_FUNCTIONS:
            manager_imports.append(
                item
            )

    results.append(
        {
            "path":
                relative(
                    path
                ),

            "repository_functions":
                repository_functions,

            "writer_imports":
                writer_imports,

            "manager_imports":
                manager_imports,
        }
    )


if not candidate_files:
    classification = (
        "NO_BODY_STORE_REPOSITORY_FOUND"
    )

elif any(
    result[
        "repository_functions"
    ]
    for result in results
):
    classification = (
        "EXISTING_BODY_STORE_REPOSITORY_FOUND"
    )

else:
    classification = (
        "BODY_STORE_REPOSITORY_REFERENCES_ONLY"
    )


print()
print("=" * 108)
print(
    "UNIVERSAL ARTICLE BODY STORE REPOSITORY — READ-ONLY SCAN"
)
print("=" * 108)
print()

print(
    "Classification: "
    + classification
)

print()

print(
    "Candidate files found: "
    + str(
        len(
            candidate_files
        )
    )
)

print()

print(
    "CANDIDATE FILES"
)

if results:
    for result in results:
        print()
        print(
            "  Path: "
            + result[
                "path"
            ]
        )

        print(
            "  Repository functions: "
            + str(
                result[
                    "repository_functions"
                ]
            )
        )

        print(
            "  Writer imports: "
            + str(
                len(
                    result[
                        "writer_imports"
                    ]
                )
            )
        )

        print(
            "  Manager imports: "
            + str(
                len(
                    result[
                        "manager_imports"
                    ]
                )
            )
        )

else:
    print(
        "  None"
    )

print()
print(
    "Source files modified:          False"
)

print(
    "Production Body Store modified: False"
)

print(
    "UUCD records written:           0"
)

print(
    "Runtime jobs created:           0"
)

print()
print(
    "FAILURES"
)

if failures:
    for failure in failures:
        print(
            "  - "
            + failure
        )

else:
    print(
        "  None"
    )

print()

if failures:
    print(
        "BODY STORE REPOSITORY SCAN: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE REPOSITORY SCAN: PASS"
)

print("=" * 108)
