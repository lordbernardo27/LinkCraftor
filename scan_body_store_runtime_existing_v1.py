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

RUNTIME_KEYWORDS = (
    "body_store_runtime",
    "body store runtime",
    "universal_article_body_store_runtime",
)

JOB_TYPES = (
    "body_store",
    "body_write",
    "body_read",
    "body_verify",
)

candidate_files = []
runtime_references = []
job_type_references = []
handler_references = []
coordinator_references = []
registration_references = []
syntax_failures = []

for path in SERVER_ROOT.rglob("*.py"):

    if any(
        part in {
            "__pycache__",
            "backups",
            "runtime_backups",
            ".venv",
            "node_modules",
        }
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

    for keyword in RUNTIME_KEYWORDS:
        if keyword in lowered:
            runtime_references.append(
                path.relative_to(PROJECT_ROOT).as_posix()
            )
            matched = True
            break

    for job in JOB_TYPES:
        if job in lowered:
            job_type_references.append(
                path.relative_to(PROJECT_ROOT).as_posix()
            )
            matched = True

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            name = node.name.casefold()

            if "body" in name and "handler" in name:
                handler_references.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}"
                )
                matched = True

            if "body" in name and "coordinator" in name:
                coordinator_references.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}"
                )
                matched = True

        elif isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                func = node.func.id.casefold()

                if (
                    "register" in func
                    and "runtime" in func
                ):
                    registration_references.append(
                        f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}"
                    )
                    matched = True

    if matched:
        candidate_files.append(
            path.relative_to(PROJECT_ROOT).as_posix()
        )

candidate_files = sorted(set(candidate_files))
runtime_references = sorted(set(runtime_references))
job_type_references = sorted(set(job_type_references))
handler_references = sorted(set(handler_references))
coordinator_references = sorted(set(coordinator_references))
registration_references = sorted(set(registration_references))

if runtime_references:
    classification = "BODY_STORE_RUNTIME_EXISTS"
elif (
    job_type_references
    or handler_references
    or coordinator_references
    or registration_references
):
    classification = "PARTIAL_RUNTIME_REFERENCES_FOUND"
else:
    classification = "NO_BODY_STORE_RUNTIME_FOUND"

print()
print("=" * 108)
print("BODY STORE RUNTIME — READ-ONLY SCAN")
print("=" * 108)
print()

print("Classification :", classification)
print()

print("Candidate files :", len(candidate_files))
for item in candidate_files:
    print("  ", item)

print()
print("Runtime references      :", len(runtime_references))
print("Job-type references     :", len(job_type_references))
print("Handler references      :", len(handler_references))
print("Coordinator references  :", len(coordinator_references))
print("Registration references :", len(registration_references))

print()
print("Production files modified : False")
print("Runtime jobs created      : 0")
print("Persistent writes         : 0")

print()
print("Syntax failures")

if syntax_failures:
    for item in syntax_failures:
        print("  ", item)
else:
    print("  None")

print()
print("BODY STORE RUNTIME SCAN: PASS")
print("=" * 108)
