from __future__ import annotations

import ast
import inspect
import hashlib
import importlib
from pathlib import Path


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "coordination_runtime_bridge_phase_5_1_runtime_entry_resolution.txt"
)


MODULE_NAMES = (
    "backend.server.runtime.universal_jobs.creation_engine",
    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.universal_runtime_infrastructure",
    "backend.server.runtime.universal_runtime_kernel",
)


TARGET_FUNCTIONS = {
    "backend.server.runtime.universal_jobs.creation_engine": (
        "normalize_universal_job_creation_request",
        "create_universal_job",
        "explain_universal_job_creation_engine_v1",
    ),

    "backend.server.runtime.universal_runtime_registration": (
        "register_runtime_handler",
        "has_runtime_handler",
        "is_runtime_job_type_registered",
        "get_runtime_registration",
        "dispatch_registered_runtime_handler",
        "execute_registered_runtime_job_v1",
    ),

    "backend.server.runtime.universal_runtime_infrastructure": (
        "*",
    ),

    "backend.server.runtime.universal_runtime_kernel": (
        "*",
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def module_file(module):
    path = Path(
        inspect.getfile(
            module
        )
    ).resolve()

    return path


def safe_signature(obj):
    try:
        return str(
            inspect.signature(
                obj
            )
        )

    except Exception as exc:
        return (
            "<SIGNATURE ERROR: "
            + repr(
                exc
            )
            + ">"
        )


def public_functions_from_ast(path: Path):
    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    functions = []

    for node in tree.body:

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            if not node.name.startswith(
                "_"
            ):
                functions.append(
                    (
                        node.name,
                        node.lineno,
                        node.end_lineno,
                    )
                )

    return source, tree, functions


def source_excerpt(
    source: str,
    start: int,
    end: int,
    padding: int = 2,
):
    lines = source.splitlines()

    lo = max(
        0,
        start - 1 - padding,
    )

    hi = min(
        len(
            lines
        ),
        end + padding,
    )

    return "\n".join(
        f"{index + 1:05d}: {lines[index]}"
        for index
        in range(
            lo,
            hi,
        )
    )


report = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.1 — RUNTIME ENTRY-POINT RESOLUTION",
    "=" * 120,
]


for module_name in MODULE_NAMES:

    report.extend(
        (
            "",
            "=" * 120,
            f"MODULE: {module_name}",
            "=" * 120,
        )
    )

    try:
        module = importlib.import_module(
            module_name
        )

    except Exception as exc:

        report.append(
            "IMPORT FAILED: "
            + repr(
                exc
            )
        )

        continue


    path = module_file(
        module
    )

    report.append(
        "FILE: "
        + str(
            path.relative_to(
                ROOT
            )
        )
    )

    report.append(
        "SHA256: "
        + sha256(
            path
        )
    )


    source, tree, ast_functions = (
        public_functions_from_ast(
            path
        )
    )


    configured = TARGET_FUNCTIONS[
        module_name
    ]


    if configured == (
        "*",
    ):
        names = tuple(
            name
            for name, _, _
            in ast_functions
        )

    else:
        names = configured


    report.append("")
    report.append(
        "PUBLIC / TARGET FUNCTION SIGNATURES"
    )


    for name in names:

        obj = getattr(
            module,
            name,
            None,
        )

        report.append("")
        report.append(
            f"{name}"
        )

        report.append(
            "  exists: "
            + str(
                obj
                is not None
            )
        )

        if obj is not None:

            report.append(
                "  signature: "
                + safe_signature(
                    obj
                )
            )


        ast_match = next(
            (
                item
                for item
                in ast_functions
                if item[
                    0
                ]
                == name
            ),
            None,
        )

        if ast_match is not None:

            _, start, end = ast_match

            report.append(
                f"  lines: {start}-{end}"
            )

            report.append(
                "  source:"
            )

            report.append(
                source_excerpt(
                    source,
                    start,
                    end,
                )
            )


    # ---------------------------------------------------------------------
    # Discover classes and constructor signatures
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "PUBLIC CLASSES"
    )

    for node in tree.body:

        if not isinstance(
            node,
            ast.ClassDef,
        ):
            continue

        if node.name.startswith(
            "_"
        ):
            continue

        obj = getattr(
            module,
            node.name,
            None,
        )

        report.append("")
        report.append(
            f"{node.name}"
        )

        report.append(
            "  lines: "
            f"{node.lineno}-{node.end_lineno}"
        )

        if obj is not None:

            report.append(
                "  signature: "
                + safe_signature(
                    obj
                )
            )


    # ---------------------------------------------------------------------
    # Detect calls related to job creation / submission / dispatch
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "RUNTIME-RELATED CALL SITES"
    )

    interesting_names = {
        "create_universal_job",
        "dispatch_registered_runtime_handler",
        "execute_registered_runtime_job_v1",
        "get_runtime_registration",
        "is_runtime_job_type_registered",
        "register_runtime_handler",
        "enqueue",
        "enqueue_job",
        "submit",
        "submit_job",
        "dispatch",
        "dispatch_job",
        "execute",
        "execute_job",
        "create_job",
    }


    hits = []

    for node in ast.walk(
        tree
    ):

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        func = node.func

        if isinstance(
            func,
            ast.Name,
        ):
            call_name = func.id

        elif isinstance(
            func,
            ast.Attribute,
        ):
            call_name = func.attr

        else:
            continue


        if call_name in interesting_names:

            hits.append(
                (
                    node.lineno,
                    call_name,
                )
            )


    if hits:

        for line_number, call_name in sorted(
            hits
        ):

            report.append(
                f"  line {line_number}: "
                f"{call_name}(...)"
            )

    else:

        report.append(
            "  NONE"
        )


# =============================================================================
# Cross-module import direction
# =============================================================================

report.extend(
    (
        "",
        "=" * 120,
        "CROSS-MODULE RUNTIME DEPENDENCY DIRECTION",
        "=" * 120,
    )
)


for module_name in MODULE_NAMES:

    try:
        module = importlib.import_module(
            module_name
        )

    except Exception:
        continue


    path = module_file(
        module
    )

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    imports = []

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ImportFrom,
        ):

            imported = (
                node.module
                or ""
            )

            if imported.startswith(
                "backend.server.runtime"
            ):
                imports.append(
                    imported
                )

        elif isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:

                if alias.name.startswith(
                    "backend.server.runtime"
                ):

                    imports.append(
                        alias.name
                    )


    report.append("")
    report.append(
        module_name
    )

    for imported in sorted(
        set(
            imports
        )
    ):

        report.append(
            "  -> "
            + imported
        )

    if not imports:

        report.append(
            "  -> NONE"
        )


# =============================================================================
# Resolution questions
# =============================================================================

report.extend(
    (
        "",
        "=" * 120,
        "PHASE 5.1 ENTRY-POINT RESOLUTION QUESTIONS",
        "=" * 120,
        "",
        "- Which function is the canonical top-level Runtime submission boundary?",
        "- Does the top-level Runtime accept UniversalJob or a creation request?",
        "- Is create_universal_job() creation-only, or does it also enqueue/dispatch?",
        "- Does execute_registered_runtime_job_v1() expect an existing UniversalJob?",
        "- Does universal_runtime_infrastructure.py call Runtime Registration internally?",
        "- Does universal_runtime_kernel.py own execution lifecycle beyond registration dispatch?",
        "- Which component owns job persistence/queue insertion?",
        "- Which component owns handler lookup?",
        "- Which component owns actual handler execution?",
        "- Can 5.1 hand directly to Runtime without importing Runtime Registration?",
        "- Should 5.1 know nothing about handlers?",
        "- Should 5.1 expose intent only and leave UniversalJob creation to 5.2?",
    )
)


REPORT.write_text(
    "\n".join(
        report
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.1 — RUNTIME ENTRY-POINT RESOLUTION COMPLETE")
print("=" * 120)

for module_name in MODULE_NAMES:

    try:
        module = importlib.import_module(
            module_name
        )

        path = module_file(
            module
        )

        print(
            module_name
        )

        print(
            "  ",
            path.relative_to(
                ROOT
            ),
        )

        print(
            "  SHA256:",
            sha256(
                path
            ),
        )

    except Exception as exc:

        print(
            module_name
        )

        print(
            "  IMPORT FAILED:",
            repr(
                exc
            ),
        )


print()
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)
