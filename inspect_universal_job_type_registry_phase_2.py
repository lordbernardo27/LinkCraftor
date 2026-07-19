from __future__ import annotations

import ast
from pathlib import Path


path = Path(
    "backend/server/jobs/universal_knowledge_orchestrator.py"
)

source = path.read_text(
    encoding="utf-8-sig",
    errors="replace",
)

tree = ast.parse(
    source,
    filename=str(path),
)


print()
print("MODULE-LEVEL COLLECTIONS CONTAINING JOB/TYPE/STAGE/PIPELINE")
print("-" * 100)


for node in tree.body:
    if not isinstance(
        node,
        (
            ast.Assign,
            ast.AnnAssign,
        ),
    ):
        continue

    targets = []

    if isinstance(
        node,
        ast.Assign,
    ):
        targets = node.targets
        value_node = node.value
    else:
        targets = [
            node.target
        ]
        value_node = node.value

    names = []

    for target in targets:
        if isinstance(
            target,
            ast.Name,
        ):
            names.append(
                target.id
            )

    for name in names:
        lowered = name.casefold()

        if not any(
            token in lowered
            for token in (
                "job",
                "type",
                "stage",
                "pipeline",
                "supported",
                "allowed",
            )
        ):
            continue

        try:
            rendered = ast.unparse(
                value_node
            )
        except Exception:
            rendered = "<unparse failed>"

        print(
            f"{name} — line {node.lineno}"
        )
        print(
            rendered
        )
        print()


print()
print("CREATE_UNIVERSAL_KNOWLEDGE_JOB SOURCE")
print("-" * 100)


for node in tree.body:
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ) and node.name == "create_universal_knowledge_job":
        print(
            ast.get_source_segment(
                source,
                node,
            )
        )
        break
else:
    raise RuntimeError(
        "create_universal_knowledge_job was not found."
    )
