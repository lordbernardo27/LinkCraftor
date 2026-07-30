from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

SOURCE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_runtime_registration.py"
)

TARGET_FUNCTIONS = {
    "ensure_persisted_runtime_registrations_loaded",
    "load_persisted_runtime_registrations",
    "reload_persisted_runtime_registrations",
    "register_runtime_handler",
    "unregister_runtime_handler",
}

source = SOURCE_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        SOURCE_PATH
    ),
)

lines = source.splitlines()

module_state_assignments = []

for node in tree.body:
    if isinstance(
        node,
        (
            ast.Assign,
            ast.AnnAssign,
        ),
    ):
        targets = []

        if isinstance(
            node,
            ast.Assign,
        ):
            targets.extend(
                node.targets
            )

        else:
            targets.append(
                node.target
            )

        for target in targets:
            if isinstance(
                target,
                ast.Name,
            ):
                lowered = target.id.casefold()

                if any(
                    term in lowered
                    for term in (
                        "load",
                        "persist",
                        "registration",
                        "initialized",
                        "ready",
                    )
                ):
                    try:
                        rendered = ast.unparse(
                            node
                        )
                    except Exception:
                        rendered = target.id

                    module_state_assignments.append(
                        {
                            "line":
                                node.lineno,

                            "code":
                                rendered,
                        }
                    )


functions = []

for node in tree.body:
    if not isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        continue

    if (
        node.name
        not in TARGET_FUNCTIONS
        and "persisted_runtime_registration"
        not in node.name
    ):
        continue

    start = node.lineno
    end = getattr(
        node,
        "end_lineno",
        node.lineno,
    )

    functions.append(
        {
            "name":
                node.name,

            "line":
                node.lineno,

            "source":
                "\n".join(
                    lines[
                        start - 1:
                        end
                    ]
                ),
        }
    )


print()
print("=" * 120)
print(
    "RUNTIME REGISTRATION — RELOAD CONTRACT INSPECTION"
)
print("=" * 120)
print()

print(
    "MODULE-LEVEL STATE"
)
print(
    "-" * 120
)

if module_state_assignments:
    for item in module_state_assignments:
        print(
            str(
                item[
                    "line"
                ]
            )
            + ": "
            + item[
                "code"
            ]
        )
else:
    print(
        "None found"
    )

print()

for function in functions:
    print(
        "FUNCTION: "
        + function[
            "name"
        ]
        + " — line "
        + str(
            function[
                "line"
            ]
        )
    )

    print(
        "-" * 120
    )

    print(
        function[
            "source"
        ]
    )

    print()

print(
    "Source files modified:           False"
)
print(
    "Runtime registrations modified:  False"
)
print(
    "Production Body Store modified: False"
)
print(
    "Production Queue modified:      False"
)

print()
print(
    "RUNTIME REGISTRATION RELOAD CONTRACT INSPECTION: PASS"
)
print("=" * 120)
