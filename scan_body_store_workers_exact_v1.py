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

EXCLUDED_PARTS = {
    "__pycache__",
    "backups",
    "runtime_backups",
    ".venv",
    ".git",
    "node_modules",
}

EXACT_WORKER_MODULE_TERMS = {
    "body_store_worker",
    "universal_article_body_store_worker",
}

EXACT_WORKER_FUNCTIONS = {
    "execute_body_store_worker_v1",
    "run_body_store_worker_v1",
    "handle_body_store_worker",
    "process_body_store_job",
    "execute_universal_article_body_store_worker",
}

EXACT_WORKER_CLASSES = {
    "BodyStoreWorker",
    "UniversalArticleBodyStoreWorker",
}

EXACT_JOB_TYPES = {
    "universal_article_body_store.store",
    "universal_article_body_store.read",
    "universal_article_body_store.verify",
    "universal_article_body_store.metadata",
    "universal_article_body_store.list",
    "body_store_store",
    "body_store_read",
    "body_store_verify",
    "body_store_metadata",
    "body_store_list",
}

EXACT_RUNTIME_CALL = (
    "execute_body_store_runtime_v1"
)

worker_term_files = []
worker_functions = []
worker_classes = []
worker_job_types = []
runtime_dispatch_references = []
registration_references = []
queue_references = []
syntax_failures = []


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        PROJECT_ROOT
    ).as_posix()


for path in SERVER_ROOT.rglob(
    "*.py"
):
    if any(
        part in EXCLUDED_PARTS
        for part in path.parts
    ):
        continue

    try:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )

        tree = ast.parse(
            source,
            filename=str(
                path
            ),
        )

    except SyntaxError as exc:
        syntax_failures.append(
            relative(
                path
            )
            + ": "
            + str(
                exc
            )
        )

        continue

    lowered = source.casefold()

    if any(
        term in lowered
        for term in EXACT_WORKER_MODULE_TERMS
    ):
        worker_term_files.append(
            relative(
                path
            )
        )

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
            if node.name in EXACT_WORKER_FUNCTIONS:
                worker_functions.append(
                    relative(
                        path
                    )
                    + ":"
                    + str(
                        node.lineno
                    )
                    + ":"
                    + node.name
                )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            if node.name in EXACT_WORKER_CLASSES:
                worker_classes.append(
                    relative(
                        path
                    )
                    + ":"
                    + str(
                        node.lineno
                    )
                    + ":"
                    + node.name
                )

        elif isinstance(
            node,
            ast.Call,
        ):
            function_name = ""

            if isinstance(
                node.func,
                ast.Name,
            ):
                function_name = node.func.id

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                function_name = node.func.attr

            if function_name == EXACT_RUNTIME_CALL:
                runtime_dispatch_references.append(
                    relative(
                        path
                    )
                    + ":"
                    + str(
                        node.lineno
                    )
                )

            for argument in [
                *node.args,
                *[
                    keyword.value
                    for keyword in node.keywords
                ],
            ]:
                if not isinstance(
                    argument,
                    ast.Constant,
                ):
                    continue

                if not isinstance(
                    argument.value,
                    str,
                ):
                    continue

                value = argument.value

                if value in EXACT_JOB_TYPES:
                    worker_job_types.append(
                        relative(
                            path
                        )
                        + ":"
                        + str(
                            node.lineno
                        )
                        + ":"
                        + value
                    )

                    if "register" in function_name.casefold():
                        registration_references.append(
                            relative(
                                path
                            )
                            + ":"
                            + str(
                                node.lineno
                            )
                            + ":"
                            + function_name
                        )

            if function_name.casefold() in {
                "enqueue",
                "dequeue",
                "claim_job",
                "lease_job",
                "ack_job",
                "nack_job",
            }:
                queue_references.append(
                    relative(
                        path
                    )
                    + ":"
                    + str(
                        node.lineno
                    )
                    + ":"
                    + function_name
                )


worker_term_files = sorted(
    set(
        worker_term_files
    )
)

worker_functions = sorted(
    set(
        worker_functions
    )
)

worker_classes = sorted(
    set(
        worker_classes
    )
)

worker_job_types = sorted(
    set(
        worker_job_types
    )
)

runtime_dispatch_references = sorted(
    set(
        runtime_dispatch_references
    )
)

registration_references = sorted(
    set(
        registration_references
    )
)

queue_references = sorted(
    set(
        queue_references
    )
)


exact_worker_exists = any(
    (
        worker_term_files,
        worker_functions,
        worker_classes,
        worker_job_types,
        registration_references,
        queue_references,
    )
)

classification = (
    "EXACT_BODY_STORE_WORKERS_FOUND"
    if exact_worker_exists
    else "NO_EXACT_BODY_STORE_WORKERS_FOUND"
)


print()
print("=" * 116)
print(
    "UNIVERSAL ARTICLE BODY STORE WORKERS — EXACT READ-ONLY SCAN"
)
print("=" * 116)
print()

print(
    "Classification: "
    + classification
)

print()
print(
    "Exact worker-term files:          "
    + str(
        len(
            worker_term_files
        )
    )
)

for item in worker_term_files:
    print(
        "  "
        + item
    )

print()
print(
    "Exact worker functions:           "
    + str(
        len(
            worker_functions
        )
    )
)

for item in worker_functions:
    print(
        "  "
        + item
    )

print()
print(
    "Exact worker classes:             "
    + str(
        len(
            worker_classes
        )
    )
)

for item in worker_classes:
    print(
        "  "
        + item
    )

print()
print(
    "Exact Body Store job types:       "
    + str(
        len(
            worker_job_types
        )
    )
)

for item in worker_job_types:
    print(
        "  "
        + item
    )

print()
print(
    "Runtime dispatch references:      "
    + str(
        len(
            runtime_dispatch_references
        )
    )
)

for item in runtime_dispatch_references:
    print(
        "  "
        + item
    )

print()
print(
    "Runtime Registration references:  "
    + str(
        len(
            registration_references
        )
    )
)

for item in registration_references:
    print(
        "  "
        + item
    )

print()
print(
    "Queue-operation references:       "
    + str(
        len(
            queue_references
        )
    )
)

for item in queue_references:
    print(
        "  "
        + item
    )

print()
print(
    "Source files modified:            False"
)

print(
    "Production Body Store modified:   False"
)

print(
    "Runtime jobs created:             0"
)

print(
    "Queues created:                  0"
)

print(
    "Workers created:                 0"
)

print()
print(
    "Syntax failures"
)

if syntax_failures:
    for item in syntax_failures:
        print(
            "  "
            + item
        )

else:
    print(
        "  None"
    )

print()

if syntax_failures:
    print(
        "BODY STORE WORKERS EXACT SCAN: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE WORKERS EXACT SCAN: PASS"
)

print("=" * 116)
