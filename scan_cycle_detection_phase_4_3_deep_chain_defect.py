from __future__ import annotations

import ast
import hashlib
from pathlib import Path


ROOT = Path.cwd()

FILE = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/cycle_detection.py"
)

REPORT = ROOT / (
    "cycle_detection_phase_4_3_deep_chain_defect_source_scan.txt"
)

EXPECTED_SHA = (
    "BC4A40999FEE0540D2254D9F99E12C1D"
    "97D25662953026ADDDABC429B42212B1"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


source = FILE.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)

actual_sha = sha256(
    FILE
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 4.3 — DEEP-CHAIN DEFECT SOURCE SCAN",
    "=" * 108,
    "",
    f"File: {FILE.relative_to(ROOT)}",
    f"Current SHA256: {actual_sha}",
    (
        "Frozen SHA exact: "
        + str(
            actual_sha == EXPECTED_SHA
        )
    ),
    "",
    "PROVEN DEFECT:",
    "2500-stage acyclic chain raises RecursionError",
    "Python default recursion limit observed: 1000",
    "",
]


target_names = {
    "detect_dependency_cycles",
    "require_acyclic_dependency_graph",
    "cycle_detection_snapshot",
    "explain_cycle_detection_v4_3",
}


def source_segment(
    node: ast.AST,
) -> str:
    if not hasattr(
        node,
        "lineno",
    ):
        return ""

    start = node.lineno - 1
    end = getattr(
        node,
        "end_lineno",
        node.lineno,
    )

    return "\n".join(
        source.splitlines()[
            start:end
        ]
    )


lines.append(
    "=" * 108
)

lines.append(
    "TOP-LEVEL FUNCTIONS"
)

lines.append(
    "=" * 108
)

for node in tree.body:

    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        lines.append(
            f"{node.name} "
            f"(lines {node.lineno}-{node.end_lineno})"
        )


lines.append("")
lines.append(
    "=" * 108
)
lines.append(
    "DETECT / GUARD IMPLEMENTATION"
)
lines.append(
    "=" * 108
)


for node in tree.body:

    if not isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        continue

    if node.name in target_names:

        lines.append("")
        lines.append(
            "-" * 108
        )
        lines.append(
            f"{node.name} "
            f"(lines {node.lineno}-{node.end_lineno})"
        )
        lines.append(
            "-" * 108
        )

        lines.append(
            source_segment(
                node
            )
        )


lines.append("")
lines.append(
    "=" * 108
)
lines.append(
    "NESTED FUNCTIONS INSIDE detect_dependency_cycles"
)
lines.append(
    "=" * 108
)


detect_node = None

for node in tree.body:

    if isinstance(
        node,
        ast.FunctionDef,
    ) and node.name == "detect_dependency_cycles":
        detect_node = node
        break


if detect_node is None:

    lines.append(
        "detect_dependency_cycles NOT FOUND"
    )

else:

    found_nested = False

    for node in ast.walk(
        detect_node
    ):

        if not isinstance(
            node,
            ast.FunctionDef,
        ):
            continue

        if node is detect_node:
            continue

        found_nested = True

        lines.append("")
        lines.append(
            "-" * 108
        )
        lines.append(
            f"{node.name} "
            f"(lines {node.lineno}-{node.end_lineno})"
        )
        lines.append(
            "-" * 108
        )

        lines.append(
            source_segment(
                node
            )
        )

    if not found_nested:
        lines.append(
            "NONE"
        )


lines.append("")
lines.append(
    "=" * 108
)
lines.append(
    "RECURSION EVIDENCE"
)
lines.append(
    "=" * 108
)


recursive_calls = []

if detect_node is not None:

    for node in ast.walk(
        detect_node
    ):

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        if isinstance(
            node.func,
            ast.Name,
        ):
            recursive_calls.append(
                (
                    node.func.id,
                    node.lineno,
                )
            )

        elif isinstance(
            node.func,
            ast.Attribute,
        ):
            recursive_calls.append(
                (
                    node.func.attr,
                    node.lineno,
                )
            )


for name, lineno in recursive_calls:
    lines.append(
        f"call: {name} @ line {lineno}"
    )


lines.append("")
lines.append(
    "=" * 108
)
lines.append(
    "CURRENT PUBLIC CLASSES / FUNCTIONS"
)
lines.append(
    "=" * 108
)


for node in tree.body:

    if isinstance(
        node,
        (
            ast.ClassDef,
            ast.FunctionDef,
        ),
    ):

        if not node.name.startswith(
            "_"
        ):
            lines.append(
                node.name
            )


lines.append("")
lines.append(
    "=" * 108
)
lines.append(
    "SOURCE MARKERS"
)
lines.append(
    "=" * 108
)


markers = (
    "deterministic DFS",
    "active-stack",
    "cycle witness",
    "cycle_witness_count",
    "topological",
    "runtime",
    "dependency_validation",
)

for marker in markers:

    lines.append(
        f"{marker}: "
        + str(
            marker.lower()
            in source.lower()
        )
    )


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 108)
print("PHASE 4.3 DEEP-CHAIN DEFECT SOURCE SCAN COMPLETE")
print("=" * 108)
print(
    "FILE:",
    FILE.relative_to(ROOT),
)
print(
    "SHA256:",
    actual_sha,
)
print(
    "FROZEN SHA EXACT:",
    actual_sha == EXPECTED_SHA,
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 108)
