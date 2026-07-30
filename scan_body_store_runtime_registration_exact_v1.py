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
    ".git",
    ".venv",
    "node_modules",
    "backups",
    "runtime_backups",
}

BODY_STORE_JOB_TYPES = {
    "body_store.store",
    "body_store.read",
    "body_store.verify",
    "body_store.metadata",
    "body_store.list",
}

REGISTRATION_MODULE_TERMS = {
    "body_store_runtime_registration",
    "universal_article_body_store_runtime_registration",
}

REGISTRATION_FUNCTION_NAMES = {
    "register_body_store_runtime",
    "register_body_store_runtime_v1",
    "register_universal_article_body_store_runtime",
    "install_body_store_runtime_registration",
}

HANDLER_FUNCTION_NAMES = {
    "handle_body_store_job",
    "handle_body_store_job_v1",
    "execute_body_store_registered_job_v1",
    "dispatch_body_store_runtime_job",
}

EXPECTED_WORKER_CALL = (
    "execute_body_store_worker_v1"
)

EXPECTED_RUNTIME_CALL = (
    "execute_body_store_runtime_v1"
)


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        PROJECT_ROOT
    ).as_posix()


registration_term_files = []
registration_functions = []
handler_functions = []
registered_job_types = []
worker_dispatch_calls = []
runtime_dispatch_calls = []
universal_registration_imports = []
queue_imports = []
syntax_failures = []


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

    lowered_source = source.casefold()

    if any(
        term in lowered_source
        for term in REGISTRATION_MODULE_TERMS
    ):
        registration_term_files.append(
            relative(
                path
            )
        )

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.ImportFrom,
        ):
            module = str(
                node.module
                or ""
            )

            lowered_module = module.casefold()

            if (
                "universal_runtime_registration"
                in lowered_module
                or "universal_knowledge_orchestrator"
                in lowered_module
            ):
                universal_registration_imports.append(
                    {
                        "path":
                            relative(
                                path
                            ),

                        "line":
                            node.lineno,

                        "module":
                            module,

                        "names": [
                            alias.name
                            for alias in node.names
                        ],
                    }
                )

            if (
                "body_store_queue_v1"
                in lowered_module
            ):
                queue_imports.append(
                    {
                        "path":
                            relative(
                                path
                            ),

                        "line":
                            node.lineno,

                        "module":
                            module,
                    }
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            if (
                node.name
                in REGISTRATION_FUNCTION_NAMES
            ):
                registration_functions.append(
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

            if (
                node.name
                in HANDLER_FUNCTION_NAMES
            ):
                handler_functions.append(
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

            if (
                function_name
                == EXPECTED_WORKER_CALL
            ):
                worker_dispatch_calls.append(
                    relative(
                        path
                    )
                    + ":"
                    + str(
                        node.lineno
                    )
                )

            if (
                function_name
                == EXPECTED_RUNTIME_CALL
            ):
                runtime_dispatch_calls.append(
                    relative(
                        path
                    )
                    + ":"
                    + str(
                        node.lineno
                    )
                )

            call_is_registration = (
                "register"
                in function_name.casefold()
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

                if (
                    argument.value
                    in BODY_STORE_JOB_TYPES
                ):
                    registered_job_types.append(
                        {
                            "path":
                                relative(
                                    path
                                ),

                            "line":
                                node.lineno,

                            "job_type":
                                argument.value,

                            "call":
                                function_name,

                            "registration_call":
                                call_is_registration,
                        }
                    )


registration_term_files = sorted(
    set(
        registration_term_files
    )
)

registration_functions = sorted(
    set(
        registration_functions
    )
)

handler_functions = sorted(
    set(
        handler_functions
    )
)

worker_dispatch_calls = sorted(
    set(
        worker_dispatch_calls
    )
)

runtime_dispatch_calls = sorted(
    set(
        runtime_dispatch_calls
    )
)

registered_job_type_names = sorted(
    {
        item[
            "job_type"
        ]
        for item in registered_job_types
        if item[
            "registration_call"
        ]
    }
)


all_job_types_registered = (
    set(
        registered_job_type_names
    )
    == BODY_STORE_JOB_TYPES
)

registration_exists = any(
    (
        registration_term_files,
        registration_functions,
        handler_functions,
        registered_job_type_names,
    )
)


if (
    registration_functions
    and handler_functions
    and all_job_types_registered
    and worker_dispatch_calls
):
    classification = (
        "COMPLETE_BODY_STORE_RUNTIME_REGISTRATION_FOUND"
    )

elif registration_exists:
    classification = (
        "PARTIAL_BODY_STORE_RUNTIME_REGISTRATION_FOUND"
    )

else:
    classification = (
        "NO_BODY_STORE_RUNTIME_REGISTRATION_FOUND"
    )


print()
print("=" * 120)
print(
    "UNIVERSAL ARTICLE BODY STORE RUNTIME REGISTRATION — EXACT READ-ONLY SCAN"
)
print("=" * 120)
print()

print(
    "Classification: "
    + classification
)

print()
print(
    "Registration-term files:          "
    + str(
        len(
            registration_term_files
        )
    )
)

for item in registration_term_files:
    print(
        "  "
        + item
    )

print()
print(
    "Registration functions:           "
    + str(
        len(
            registration_functions
        )
    )
)

for item in registration_functions:
    print(
        "  "
        + item
    )

print()
print(
    "Registered handler functions:     "
    + str(
        len(
            handler_functions
        )
    )
)

for item in handler_functions:
    print(
        "  "
        + item
    )

print()
print(
    "Registered Body Store job types:  "
    + str(
        len(
            registered_job_type_names
        )
    )
)

for item in registered_job_type_names:
    print(
        "  "
        + item
    )

print()
print(
    "All five job types registered:    "
    + str(
        all_job_types_registered
    )
)

print()
print(
    "Worker dispatch calls:            "
    + str(
        len(
            worker_dispatch_calls
        )
    )
)

for item in worker_dispatch_calls:
    print(
        "  "
        + item
    )

print()
print(
    "Direct Runtime dispatch calls:    "
    + str(
        len(
            runtime_dispatch_calls
        )
    )
)

for item in runtime_dispatch_calls:
    print(
        "  "
        + item
    )

print()
print(
    "Universal registration imports:   "
    + str(
        len(
            universal_registration_imports
        )
    )
)

for item in universal_registration_imports:
    print(
        "  "
        + item[
            "path"
        ]
        + ":"
        + str(
            item[
                "line"
            ]
        )
        + ":"
        + item[
            "module"
        ]
    )

print()
print(
    "Body Store Queue imports:         "
    + str(
        len(
            queue_imports
        )
    )
)

for item in queue_imports:
    print(
        "  "
        + item[
            "path"
        ]
        + ":"
        + str(
            item[
                "line"
            ]
        )
        + ":"
        + item[
            "module"
        ]
    )

print()
print(
    "Source files modified:            False"
)

print(
    "Production queue modified:        False"
)

print(
    "Production Body Store modified:   False"
)

print(
    "Runtime handlers registered:      0"
)

print(
    "Runtime jobs created:             0"
)

print(
    "Worker executions started:        0"
)

print()
print(
    "SYNTAX FAILURES"
)

if syntax_failures:
    for failure in syntax_failures:
        print(
            "  "
            + failure
        )

else:
    print(
        "  None"
    )

print()

if syntax_failures:
    print(
        "BODY STORE RUNTIME REGISTRATION SCAN: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE RUNTIME REGISTRATION SCAN: PASS"
)

print("=" * 120)
