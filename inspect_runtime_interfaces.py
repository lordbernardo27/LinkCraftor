import ast
from pathlib import Path

FILES = [
    "backend/server/jobs/universal_knowledge_orchestrator.py",
    "backend/server/runtime/universal_runtime_infrastructure.py",
]

TARGETS = {
    "create_universal_knowledge_job",
    "update_job_status",
    "update_job_progress",
    "record_job_failure",
    "read_queue",
    "workspace_concurrency_decision",
    "retry_job",
    "move_to_dead_letter",
}

for filename in FILES:

    print()
    print("=" * 120)
    print(filename)
    print("=" * 120)

    path = Path(filename)

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    tree = ast.parse(source)

    for node in tree.body:

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ) and node.name in TARGETS:

            print()
            print("-" * 80)
            print(node.name)
            print("-" * 80)
            print(ast.get_source_segment(source, node))
