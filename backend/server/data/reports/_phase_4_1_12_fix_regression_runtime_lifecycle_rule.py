from pathlib import Path

path = Path(
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\data\reports\_phase_4_1_12_worker_drain_regression_runner.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)

old = '''for forbidden_symbol in (
    "runtimelifecyclephase",
    "runtimekernelstate",
    "queue_drain",
    "drain_queue",
    "shutdown_requested:",
    "lease_id:",
    "job_id:",
    "pool_id:",
    "workspace_id:",
    "health_state:",
    "stale_threshold",
    "max_concurrency:",
):

    check(
        "no_hidden_policy_"
        + forbidden_symbol.replace(
            " ",
            "_"
        ),
        forbidden_symbol
        not in source_lower,
    )
'''

new = '''# RuntimeLifecyclePhase may be named in explanatory boundary
# documentation. What is forbidden is actual code coupling to the
# runtime lifecycle authority, not a documentation reference.

runtime_lifecycle_code_coupling = []


for node in ast.walk(
    tree
):

    if isinstance(
        node,
        ast.Name,
    ) and node.id == "RuntimeLifecyclePhase":

        runtime_lifecycle_code_coupling.append(
            (
                "Name",
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )

    elif isinstance(
        node,
        ast.Attribute,
    ) and node.attr == "RuntimeLifecyclePhase":

        runtime_lifecycle_code_coupling.append(
            (
                "Attribute",
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )

    elif isinstance(
        node,
        ast.ImportFrom,
    ):

        for alias in node.names:

            if alias.name == "RuntimeLifecyclePhase":

                runtime_lifecycle_code_coupling.append(
                    (
                        "ImportFrom",
                        getattr(
                            node,
                            "lineno",
                            0,
                        ),
                    )
                )

    elif isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            if (
                "runtime_lifecycle_manager"
                in alias.name
            ):

                runtime_lifecycle_code_coupling.append(
                    (
                        "Import",
                        getattr(
                            node,
                            "lineno",
                            0,
                        ),
                    )
                )


check(
    "no_hidden_policy_runtimelifecyclephase",
    not runtime_lifecycle_code_coupling,
    runtime_lifecycle_code_coupling,
)


for forbidden_symbol in (
    "runtimekernelstate",
    "queue_drain",
    "drain_queue",
    "shutdown_requested:",
    "lease_id:",
    "job_id:",
    "pool_id:",
    "workspace_id:",
    "health_state:",
    "stale_threshold",
    "max_concurrency:",
):

    check(
        "no_hidden_policy_"
        + forbidden_symbol.replace(
            " ",
            "_"
        ),
        forbidden_symbol
        not in source_lower,
    )
'''

if old not in text:

    raise SystemExit(
        "Expected hidden-policy regression block was not found."
    )


text = text.replace(
    old,
    new,
    1,
)


path.write_text(
    text,
    encoding="utf-8",
)

print(
    "4.1.12 regression RuntimeLifecyclePhase rule corrected."
)
