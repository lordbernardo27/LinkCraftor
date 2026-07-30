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

EXCLUDED = {
    "__pycache__",
    ".git",
    ".venv",
    "node_modules",
    "backups",
    "runtime_backups",
}

QUEUE_MODULE_TERMS = {
    "body_store_queue",
    "universal_article_body_store_queue",
}

QUEUE_CLASSES = {
    "BodyStoreQueue",
    "UniversalArticleBodyStoreQueue",
}

QUEUE_FUNCTIONS = {
    "enqueue_body_store_job",
    "dequeue_body_store_job",
    "claim_body_store_job",
    "lease_body_store_job",
    "ack_body_store_job",
    "nack_body_store_job",
}

BODY_STORE_JOB_TYPES = {
    "universal_article_body_store.store",
    "universal_article_body_store.read",
    "universal_article_body_store.verify",
    "universal_article_body_store.metadata",
    "universal_article_body_store.list",
}

candidate_files = []
queue_classes = []
queue_functions = []
queue_job_types = []
queue_operations = []
registration_refs = []
syntax_failures = []

for path in SERVER_ROOT.rglob("*.py"):

    if any(
        part in EXCLUDED
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
            filename=str(path),
        )

    except Exception as exc:
        syntax_failures.append(
            f"{path.relative_to(PROJECT_ROOT)} : {exc}"
        )
        continue

    lowered = source.casefold()

    matched = False

    if any(
        term in lowered
        for term in QUEUE_MODULE_TERMS
    ):
        candidate_files.append(
            path.relative_to(PROJECT_ROOT).as_posix()
        )
        matched = True

    for node in ast.walk(tree):

        if isinstance(node, ast.ClassDef):

            if node.name in QUEUE_CLASSES:
                queue_classes.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}:{node.name}"
                )
                matched = True

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            if node.name in QUEUE_FUNCTIONS:
                queue_functions.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}:{node.name}"
                )
                matched = True

        elif isinstance(node, ast.Call):

            func = ""

            if isinstance(node.func, ast.Name):
                func = node.func.id

            elif isinstance(node.func, ast.Attribute):
                func = node.func.attr

            if func.casefold() in {
                "enqueue",
                "dequeue",
                "claim_job",
                "lease_job",
                "ack_job",
                "nack_job",
            }:
                queue_operations.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}:{func}"
                )
                matched = True

            if "register" in func.casefold():
                registration_refs.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}:{func}"
                )

            for arg in [
                *node.args,
                *[
                    keyword.value
                    for keyword in node.keywords
                ],
            ]:

                if (
                    isinstance(arg, ast.Constant)
                    and isinstance(arg.value, str)
                    and arg.value in BODY_STORE_JOB_TYPES
                ):
                    queue_job_types.append(
                        f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}:{arg.value}"
                    )
                    matched = True

    if matched:
        candidate_files.append(
            path.relative_to(PROJECT_ROOT).as_posix()
        )

candidate_files = sorted(set(candidate_files))
queue_classes = sorted(set(queue_classes))
queue_functions = sorted(set(queue_functions))
queue_job_types = sorted(set(queue_job_types))
queue_operations = sorted(set(queue_operations))
registration_refs = sorted(set(registration_refs))

classification = (
    "BODY_STORE_QUEUE_EXISTS"
    if (
        queue_classes
        or queue_functions
        or queue_job_types
        or queue_operations
    )
    else "NO_BODY_STORE_QUEUE_FOUND"
)

print()
print("=" * 112)
print("BODY STORE QUEUE — EXACT READ-ONLY SCAN")
print("=" * 112)
print()

print("Classification :", classification)
print()

print("Candidate files :", len(candidate_files))
for item in candidate_files:
    print("  ", item)

print()

print("Queue classes :", len(queue_classes))
for item in queue_classes:
    print("  ", item)

print()

print("Queue functions :", len(queue_functions))
for item in queue_functions:
    print("  ", item)

print()

print("Queue job types :", len(queue_job_types))
for item in queue_job_types:
    print("  ", item)

print()

print("Queue operations :", len(queue_operations))
for item in queue_operations:
    print("  ", item)

print()

print("Registration references :", len(registration_refs))
for item in registration_refs:
    print("  ", item)

print()

print("Production files modified : False")
print("Runtime jobs created      : 0")
print("Queues created            : 0")
print("Workers created           : 0")

print()
print("Syntax failures")

if syntax_failures:
    for item in syntax_failures:
        print("  ", item)
else:
    print("  None")

print()
print("BODY STORE QUEUE SCAN: PASS")
print("=" * 112)
