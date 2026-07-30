from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

FILES = [
    PROJECT_ROOT
    / "backend/server/jobs/universal_knowledge_orchestrator.py",

    PROJECT_ROOT
    / "backend/server/runtime/universal_jobs/contract.py",

    PROJECT_ROOT
    / "backend/server/runtime/runtime_state_store.py",

    PROJECT_ROOT
    / "backend/server/runtime/runtime_persistence.py",

    PROJECT_ROOT
    / "backend/server/runtime/universal_runtime_kernel.py",

    PROJECT_ROOT
    / "backend/server/runtime/universal_runtime_infrastructure.py",
]

REPORT_PATH = (
    PROJECT_ROOT
    / "backend/server/data/runtime_scans"
    / "universal_queue_exact_callable_state_v2.json"
)

EXACT_CAPABILITIES = {
    "job_creation": {
        "create_job",
        "create_universal_job",
        "create_universal_knowledge_job",
        "build_job",
        "submit_job",
        "enqueue_job",
    },

    "claim": {
        "claim_job",
        "claim_next_job",
        "claim_next_eligible_job",
        "acquire_job",
        "dequeue_job",
    },

    "lease": {
        "lease_job",
        "renew_lease",
        "release_lease",
        "expire_lease",
        "is_leased",
    },

    "completion": {
        "complete_job",
        "mark_completed",
        "mark_job_completed",
        "record_job_completion",
        "ack_job",
        "acknowledge_job",
    },

    "failure": {
        "fail_job",
        "mark_failed",
        "mark_job_failed",
        "record_job_failure",
        "nack_job",
    },

    "retry_requeue": {
        "retry_job",
        "requeue_job",
        "schedule_retry",
        "return_to_queue",
    },

    "cancel": {
        "cancel_job",
        "mark_cancelled",
        "mark_job_cancelled",
    },

    "list_filter": {
        "list_jobs",
        "list_queued_jobs",
        "list_runtime_jobs",
        "find_jobs",
        "search_jobs",
        "get_jobs",
    },

    "persistence": {
        "save_job",
        "persist_job",
        "write_job",
        "store_job",
        "update_job",
        "load_job",
        "delete_job",
    },

    "worker_assignment": {
        "assign_worker",
        "set_worker",
        "bind_worker",
        "claim_for_worker",
    },
}

STATE_VALUES = {
    "NEW",
    "QUEUED",
    "PENDING",
    "LEASED",
    "RUNNING",
    "IN_PROGRESS",
    "COMPLETED",
    "SUCCEEDED",
    "FAILED",
    "CANCELLED",
    "RETRYING",
    "DEAD_LETTER",
}

STATE_FIELD_NAMES = {
    "status",
    "state",
    "job_status",
    "runtime_status",
}

LEASE_FIELD_NAMES = {
    "lease_id",
    "leased_at",
    "lease_expiration",
    "lease_expires_at",
    "lease_owner",
    "worker_id",
    "claimed_at",
}

PRIORITY_FIELD_NAMES = {
    "priority",
    "priority_rank",
    "queue_priority",
}

WORKSPACE_FIELD_NAMES = {
    "workspace_id",
    "tenant_id",
    "account_id",
}

PERSISTENCE_CALL_NAMES = {
    "write_text",
    "write_bytes",
    "open",
    "replace",
    "rename",
    "commit",
    "put",
    "save",
    "persist",
    "upsert",
    "update",
}

TRANSITION_VERBS = {
    "mark",
    "set",
    "transition",
    "complete",
    "fail",
    "cancel",
    "lease",
    "claim",
    "retry",
    "requeue",
}


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        PROJECT_ROOT
    ).as_posix()


def dotted_name(
    node: ast.AST,
) -> str:
    if isinstance(
        node,
        ast.Name,
    ):
        return node.id

    if isinstance(
        node,
        ast.Attribute,
    ):
        parent = dotted_name(
            node.value
        )

        if parent:
            return (
                parent
                + "."
                + node.attr
            )

        return node.attr

    return ""


def function_signature(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> dict[str, Any]:
    positional = [
        argument.arg
        for argument in [
            *node.args.posonlyargs,
            *node.args.args,
        ]
    ]

    keyword_only = [
        argument.arg
        for argument in node.args.kwonlyargs
    ]

    defaults_count = len(
        node.args.defaults
    )

    required_positional_count = (
        len(
            positional
        )
        - defaults_count
    )

    return {
        "name":
            node.name,

        "async":
            isinstance(
                node,
                ast.AsyncFunctionDef,
            ),

        "positional_arguments":
            positional,

        "required_positional_arguments":
            positional[
                :required_positional_count
            ],

        "keyword_only_arguments":
            keyword_only,

        "vararg":
            (
                node.args.vararg.arg
                if node.args.vararg
                else None
            ),

        "kwarg":
            (
                node.args.kwarg.arg
                if node.args.kwarg
                else None
            ),

        "line":
            node.lineno,
    }


def constant_strings(
    tree: ast.AST,
) -> set[str]:
    values = set()

    for node in ast.walk(
        tree
    ):
        if (
            isinstance(
                node,
                ast.Constant,
            )
            and isinstance(
                node.value,
                str,
            )
        ):
            values.add(
                node.value
            )

    return values


def assigned_names(
    tree: ast.AST,
) -> set[str]:
    names = set()

    for node in ast.walk(
        tree
    ):
        targets: list[ast.AST] = []

        if isinstance(
            node,
            ast.Assign,
        ):
            targets.extend(
                node.targets
            )

        elif isinstance(
            node,
            ast.AnnAssign,
        ):
            targets.append(
                node.target
            )

        for target in targets:
            if isinstance(
                target,
                ast.Name,
            ):
                names.add(
                    target.id
                )

            elif isinstance(
                target,
                ast.Attribute,
            ):
                names.add(
                    target.attr
                )

    return names


def dictionary_keys(
    tree: ast.AST,
) -> set[str]:
    keys = set()

    for node in ast.walk(
        tree
    ):
        if not isinstance(
            node,
            ast.Dict,
        ):
            continue

        for key in node.keys:
            if (
                isinstance(
                    key,
                    ast.Constant,
                )
                and isinstance(
                    key.value,
                    str,
                )
            ):
                keys.add(
                    key.value
                )

    return keys


def function_capabilities(
    function_name: str,
) -> list[str]:
    normalized = function_name.casefold()

    matches = []

    for capability, exact_names in (
        EXACT_CAPABILITIES.items()
    ):
        if normalized in {
            name.casefold()
            for name in exact_names
        }:
            matches.append(
                capability
            )

    return matches


file_reports = []
syntax_failures = []

all_capabilities: dict[str, list[dict[str, Any]]] = {
    capability: []
    for capability in EXACT_CAPABILITIES
}

all_states = set()
all_lease_fields = set()
all_priority_fields = set()
all_workspace_fields = set()
all_transition_functions = []
all_persistence_calls = []


for path in FILES:
    if not path.is_file():
        file_reports.append(
            {
                "path":
                    relative(
                        path
                    ),

                "exists":
                    False,
            }
        )

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

        continue

    strings = constant_strings(
        tree
    )

    names = assigned_names(
        tree
    )

    dict_keys = dictionary_keys(
        tree
    )

    discovered_fields = (
        names
        | dict_keys
        | {
            value
            for value in strings
            if value.isidentifier()
        }
    )

    state_values = sorted(
        {
            value.upper()
            for value in strings
            if value.upper()
            in STATE_VALUES
        }
    )

    lease_fields = sorted(
        discovered_fields
        & LEASE_FIELD_NAMES
    )

    priority_fields = sorted(
        discovered_fields
        & PRIORITY_FIELD_NAMES
    )

    workspace_fields = sorted(
        discovered_fields
        & WORKSPACE_FIELD_NAMES
    )

    state_fields = sorted(
        discovered_fields
        & STATE_FIELD_NAMES
    )

    functions = []
    classes = []
    persistence_calls = []
    transition_functions = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            signature = function_signature(
                node
            )

            capabilities = (
                function_capabilities(
                    node.name
                )
            )

            signature[
                "capabilities"
            ] = capabilities

            functions.append(
                signature
            )

            for capability in capabilities:
                all_capabilities[
                    capability
                ].append(
                    {
                        "path":
                            relative(
                                path
                            ),

                        **signature,
                    }
                )

            lowered_name = (
                node.name.casefold()
            )

            if any(
                verb in lowered_name
                for verb in TRANSITION_VERBS
            ):
                item = {
                    "path":
                        relative(
                            path
                        ),

                    "name":
                        node.name,

                    "line":
                        node.lineno,
                }

                transition_functions.append(
                    item
                )

                all_transition_functions.append(
                    item
                )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            methods = []

            for child in node.body:
                if isinstance(
                    child,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                ):
                    method = function_signature(
                        child
                    )

                    capabilities = (
                        function_capabilities(
                            child.name
                        )
                    )

                    method[
                        "capabilities"
                    ] = capabilities

                    methods.append(
                        method
                    )

                    for capability in capabilities:
                        all_capabilities[
                            capability
                        ].append(
                            {
                                "path":
                                    relative(
                                        path
                                    ),

                                "class":
                                    node.name,

                                **method,
                            }
                        )

            classes.append(
                {
                    "name":
                        node.name,

                    "line":
                        node.lineno,

                    "methods":
                        methods,
                }
            )

        elif isinstance(
            node,
            ast.Call,
        ):
            call_name = dotted_name(
                node.func
            )

            final_name = (
                call_name.rsplit(
                    ".",
                    1,
                )[
                    -1
                ].casefold()
                if call_name
                else ""
            )

            if final_name in {
                name.casefold()
                for name in PERSISTENCE_CALL_NAMES
            }:
                item = {
                    "path":
                        relative(
                            path
                        ),

                    "call":
                        call_name,

                    "line":
                        node.lineno,
                }

                persistence_calls.append(
                    item
                )

                all_persistence_calls.append(
                    item
                )

    all_states.update(
        state_values
    )

    all_lease_fields.update(
        lease_fields
    )

    all_priority_fields.update(
        priority_fields
    )

    all_workspace_fields.update(
        workspace_fields
    )

    file_reports.append(
        {
            "path":
                relative(
                    path
                ),

            "exists":
                True,

            "functions":
                sorted(
                    functions,
                    key=lambda item: (
                        item[
                            "line"
                        ]
                    ),
                ),

            "classes":
                sorted(
                    classes,
                    key=lambda item: (
                        item[
                            "line"
                        ]
                    ),
                ),

            "state_values":
                state_values,

            "state_fields":
                state_fields,

            "lease_fields":
                lease_fields,

            "priority_fields":
                priority_fields,

            "workspace_fields":
                workspace_fields,

            "transition_functions":
                transition_functions,

            "persistence_calls":
                persistence_calls,
        }
    )


capability_summary = {
    capability: {
        "present":
            bool(
                records
            ),

        "count":
            len(
                records
            ),

        "records":
            records,
    }

    for capability, records
    in all_capabilities.items()
}


required_for_body_store_queue = {
    "job_creation",
    "claim",
    "lease",
    "completion",
    "failure",
    "retry_requeue",
    "cancel",
    "list_filter",
    "persistence",
    "worker_assignment",
}


exact_core_ready = all(
    capability_summary[
        capability
    ][
        "present"
    ]

    for capability
    in required_for_body_store_queue
)

state_machine_ready = {
    "queued":
        "QUEUED"
        in all_states,

    "leased":
        "LEASED"
        in all_states,

    "completed":
        (
            "COMPLETED"
            in all_states
            or "SUCCEEDED"
            in all_states
        ),

    "failed":
        "FAILED"
        in all_states,

    "cancelled":
        "CANCELLED"
        in all_states,
}

state_machine_complete = all(
    state_machine_ready.values()
)

lease_contract_present = bool(
    all_lease_fields
)

priority_contract_present = bool(
    all_priority_fields
)

workspace_isolation_present = bool(
    all_workspace_fields
)

persistent_backend_evidence = bool(
    all_persistence_calls
)


if (
    exact_core_ready
    and state_machine_complete
    and lease_contract_present
    and workspace_isolation_present
    and persistent_backend_evidence
):
    classification = (
        "UNIVERSAL_QUEUE_EXACTLY_REUSABLE"
    )

elif (
    capability_summary[
        "job_creation"
    ][
        "present"
    ]
    and capability_summary[
        "completion"
    ][
        "present"
    ]
    and capability_summary[
        "failure"
    ][
        "present"
    ]
):
    classification = (
        "UNIVERSAL_JOB_FOUNDATION_REQUIRES_QUEUE_EXTENSION"
    )

else:
    classification = (
        "NO_COMPLETE_REUSABLE_QUEUE_INTERFACE"
    )


report = {
    "schema_version":
        "universal_queue_exact_callable_state_v2",

    "classification":
        classification,

    "files":
        file_reports,

    "capabilities":
        capability_summary,

    "state_values":
        sorted(
            all_states
        ),

    "state_machine_ready":
        state_machine_ready,

    "state_machine_complete":
        state_machine_complete,

    "lease_fields":
        sorted(
            all_lease_fields
        ),

    "priority_fields":
        sorted(
            all_priority_fields
        ),

    "workspace_fields":
        sorted(
            all_workspace_fields
        ),

    "lease_contract_present":
        lease_contract_present,

    "priority_contract_present":
        priority_contract_present,

    "workspace_isolation_present":
        workspace_isolation_present,

    "persistence_call_count":
        len(
            all_persistence_calls
        ),

    "persistent_backend_evidence":
        persistent_backend_evidence,

    "transition_functions":
        all_transition_functions,

    "syntax_failures":
        syntax_failures,

    "read_only":
        True,

    "source_files_modified":
        False,

    "queues_created":
        0,

    "jobs_created":
        0,

    "persistent_runtime_writes":
        0,
}


REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_PATH.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print(
    "UNIVERSAL QUEUE — EXACT CALLABLE AND STATE-TRANSITION DISCOVERY"
)
print("=" * 120)
print()

print(
    "Classification: "
    + classification
)

print()
print(
    "EXACT CALLABLE CAPABILITIES"
)

for capability in sorted(
    capability_summary
):
    item = capability_summary[
        capability
    ]

    print(
        f"{capability:<24}"
        + (
            "PRESENT"
            if item[
                "present"
            ]
            else "MISSING"
        )
        + "  "
        + str(
            item[
                "count"
            ]
        )
    )

    for record in item[
        "records"
    ]:
        owner = (
            record.get(
                "class",
                "",
            )
        )

        owner_prefix = (
            owner
            + "."
            if owner
            else ""
        )

        print(
            "  "
            + record[
                "path"
            ]
            + ":"
            + str(
                record[
                    "line"
                ]
            )
            + ":"
            + owner_prefix
            + record[
                "name"
            ]
            + "("
            + ", ".join(
                record[
                    "positional_arguments"
                ]
                + record[
                    "keyword_only_arguments"
                ]
            )
            + ")"
        )

print()
print(
    "STATE MACHINE"
)

for state, present in (
    state_machine_ready.items()
):
    print(
        f"{state:<24}"
        + (
            "PRESENT"
            if present
            else "MISSING"
        )
    )

print()
print(
    "LEASE FIELDS"
)

if all_lease_fields:
    for field in sorted(
        all_lease_fields
    ):
        print(
            "  "
            + field
        )

else:
    print(
        "  None"
    )

print()
print(
    "PRIORITY FIELDS"
)

if all_priority_fields:
    for field in sorted(
        all_priority_fields
    ):
        print(
            "  "
            + field
        )

else:
    print(
        "  None"
    )

print()
print(
    "WORKSPACE ISOLATION FIELDS"
)

if all_workspace_fields:
    for field in sorted(
        all_workspace_fields
    ):
        print(
            "  "
            + field
        )

else:
    print(
        "  None"
    )

print()
print(
    "PERSISTENCE CALL EVIDENCE: "
    + str(
        len(
            all_persistence_calls
        )
    )
)

for item in all_persistence_calls[
    :50
]:
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
            "call"
        ]
    )

print()
print(
    "TRANSITION FUNCTIONS: "
    + str(
        len(
            all_transition_functions
        )
    )
)

for item in all_transition_functions[
    :100
]:
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
            "name"
        ]
    )

print()
print(
    "DECISION FLAGS"
)

print(
    f"{'Exact core ready':<34}"
    + str(
        exact_core_ready
    )
)

print(
    f"{'State machine complete':<34}"
    + str(
        state_machine_complete
    )
)

print(
    f"{'Lease contract present':<34}"
    + str(
        lease_contract_present
    )
)

print(
    f"{'Priority contract present':<34}"
    + str(
        priority_contract_present
    )
)

print(
    f"{'Workspace isolation present':<34}"
    + str(
        workspace_isolation_present
    )
)

print(
    f"{'Persistent backend evidence':<34}"
    + str(
        persistent_backend_evidence
    )
)

print()
print(
    "Report:"
)

print(
    "  "
    + str(
        REPORT_PATH
    )
)

print()
print(
    "Source files modified:     False"
)

print(
    "Queues created:            0"
)

print(
    "Jobs created:              0"
)

print(
    "Persistent runtime writes: 0"
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
        "UNIVERSAL QUEUE EXACT CALLABLE SCAN: FAIL"
    )

    raise SystemExit(1)

print(
    "UNIVERSAL QUEUE EXACT CALLABLE SCAN: PASS"
)

print("=" * 120)
