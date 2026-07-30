from __future__ import annotations

import ast
import inspect
import sys
from pathlib import Path


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


TARGET_FILES = [
    PROJECT_ROOT
    / "backend/server/runtime/universal_runtime_registration.py",

    PROJECT_ROOT
    / "backend/server/article_validation/"
      "article_validation_runtime_registration.py",

    PROJECT_ROOT
    / "backend/server/integrity/website_article_integrity/"
      "website_article_integrity_runtime_registration.py",
]


TARGET_FUNCTION_NAMES = {
    "register_runtime_handler",
    "unregister_runtime_handler",
    "dispatch_registered_runtime_handler",
    "is_runtime_handler_registered",
    "list_runtime_registrations",
}


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        PROJECT_ROOT
    ).as_posix()


def render_signature(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> str:
    arguments = []

    positional = [
        *node.args.posonlyargs,
        *node.args.args,
    ]

    default_offset = (
        len(
            positional
        )
        - len(
            node.args.defaults
        )
    )

    for index, argument in enumerate(
        positional
    ):
        item = argument.arg

        if index >= default_offset:
            default = node.args.defaults[
                index
                - default_offset
            ]

            try:
                item += (
                    "="
                    + ast.unparse(
                        default
                    )
                )

            except Exception:
                item += "=<default>"

        arguments.append(
            item
        )

    if node.args.vararg:
        arguments.append(
            "*"
            + node.args.vararg.arg
        )

    elif node.args.kwonlyargs:
        arguments.append(
            "*"
        )

    for index, argument in enumerate(
        node.args.kwonlyargs
    ):
        item = argument.arg

        default = node.args.kw_defaults[
            index
        ]

        if default is not None:
            try:
                item += (
                    "="
                    + ast.unparse(
                        default
                    )
                )

            except Exception:
                item += "=<default>"

        arguments.append(
            item
        )

    if node.args.kwarg:
        arguments.append(
            "**"
            + node.args.kwarg.arg
        )

    return (
        node.name
        + "("
        + ", ".join(
            arguments
        )
        + ")"
    )


print()
print("=" * 120)
print(
    "BODY STORE RUNTIME REGISTRATION — INSTALL CONTRACT DISCOVERY"
)
print("=" * 120)
print()


syntax_failures = []
canonical_functions = []
registration_calls = []
handler_functions = []
module_imports = []


for path in TARGET_FILES:
    print(
        "FILE: "
        + relative(
            path
        )
    )

    print(
        "-" * 120
    )

    if not path.is_file():
        print(
            "MISSING"
        )

        print()
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

    except Exception as exc:
        syntax_failures.append(
            relative(
                path
            )
            + ": "
            + str(
                exc
            )
        )

        print(
            "PARSE FAILURE: "
            + str(
                exc
            )
        )

        print()
        continue

    lines = source.splitlines()

    for node in tree.body:
        if isinstance(
            node,
            ast.ImportFrom,
        ):
            module = str(
                node.module
                or ""
            )

            if (
                "universal_runtime_registration"
                in module
                or "universal_knowledge_orchestrator"
                in module
            ):
                names = [
                    alias.name
                    for alias in node.names
                ]

                item = {
                    "path":
                        relative(
                            path
                        ),

                    "line":
                        node.lineno,

                    "module":
                        module,

                    "names":
                        names,
                }

                module_imports.append(
                    item
                )

                print(
                    "IMPORT "
                    + module
                    + " -> "
                    + ", ".join(
                        names
                    )
                )

        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        signature = render_signature(
            node
        )

        if node.name in TARGET_FUNCTION_NAMES:
            canonical_functions.append(
                {
                    "path":
                        relative(
                            path
                        ),

                    "line":
                        node.lineno,

                    "signature":
                        signature,
                }
            )

            print(
                "CANONICAL FUNCTION "
                + str(
                    node.lineno
                )
                + ": "
                + signature
            )

        lowered_name = node.name.casefold()

        if (
            "handler"
            in lowered_name
            or "register"
            in lowered_name
            or "install"
            in lowered_name
        ):
            handler_functions.append(
                {
                    "path":
                        relative(
                            path
                        ),

                    "line":
                        node.lineno,

                    "signature":
                        signature,
                }
            )

            print(
                "REGISTRATION/HANDLER FUNCTION "
                + str(
                    node.lineno
                )
                + ": "
                + signature
            )

    for node in ast.walk(
        tree
    ):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

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

        if function_name != "register_runtime_handler":
            continue

        try:
            rendered_call = ast.unparse(
                node
            )

        except Exception:
            rendered_call = (
                "register_runtime_handler(<unavailable>)"
            )

        registration_calls.append(
            {
                "path":
                    relative(
                        path
                    ),

                "line":
                    node.lineno,

                "call":
                    rendered_call,
            }
        )

        print()
        print(
            "REGISTRATION CALL AT LINE "
            + str(
                node.lineno
            )
        )

        print(
            rendered_call
        )

        start = max(
            0,
            node.lineno
            - 4
        )

        end = min(
            len(
                lines
            ),
            (
                getattr(
                    node,
                    "end_lineno",
                    node.lineno,
                )
                + 3
            ),
        )

        print(
            "CONTEXT"
        )

        for index in range(
            start,
            end,
        ):
            print(
                f"{index + 1:5}: "
                + lines[
                    index
                ]
            )

    print()


print("=" * 120)
print(
    "SUMMARY"
)
print("=" * 120)

print(
    "Canonical registration functions: "
    + str(
        len(
            canonical_functions
        )
    )
)

print(
    "Existing registration calls:      "
    + str(
        len(
            registration_calls
        )
    )
)

print(
    "Handler/install functions:         "
    + str(
        len(
            handler_functions
        )
    )
)

print(
    "Registration imports:              "
    + str(
        len(
            module_imports
        )
    )
)

print()

print(
    "Source files modified:             False"
)

print(
    "Runtime handlers registered:       0"
)

print(
    "Runtime jobs created:              0"
)

print(
    "Production queue modified:         False"
)

print(
    "Production Body Store modified:    False"
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
        "BODY STORE REGISTRATION INSTALL CONTRACT SCAN: FAIL"
    )

    raise SystemExit(1)

if not canonical_functions:
    print(
        "BODY STORE REGISTRATION INSTALL CONTRACT SCAN: FAIL"
    )

    print(
        "Canonical register_runtime_handler API was not found."
    )

    raise SystemExit(1)

if not registration_calls:
    print(
        "BODY STORE REGISTRATION INSTALL CONTRACT SCAN: FAIL"
    )

    print(
        "No proven registration implementation was found."
    )

    raise SystemExit(1)

print(
    "BODY STORE REGISTRATION INSTALL CONTRACT SCAN: PASS"
)

print(
    "The exact canonical registration API and proven installation "
    "pattern are available for the Body Store registration patch."
)

print("=" * 120)
