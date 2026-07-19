from __future__ import annotations

import ast
from pathlib import Path


ORCHESTRATOR_PATH = Path(
    "backend/server/jobs/universal_knowledge_orchestrator.py"
)

CONTRACT_PATH = Path(
    "backend/server/runtime/udare_runtime_contract.py"
)

UDARE_JOB_TYPE = "udare_reconstruction"


def line_offsets(text: str) -> list[int]:
    offsets = [0]

    for index, character in enumerate(
        text
    ):
        if character == "\n":
            offsets.append(
                index + 1
            )

    return offsets


def node_offsets(
    text: str,
    node: ast.AST,
) -> tuple[int, int]:
    offsets = line_offsets(
        text
    )

    start = (
        offsets[
            node.lineno - 1
        ]
        + node.col_offset
    )

    end = (
        offsets[
            node.end_lineno - 1
        ]
        + node.end_col_offset
    )

    return start, end


# =====================================================================
# 1. PATCH THE CANONICAL UNIVERSAL ORCHESTRATOR
# =====================================================================

orchestrator_text = (
    ORCHESTRATOR_PATH.read_text(
        encoding="utf-8-sig"
    )
)

orchestrator_tree = ast.parse(
    orchestrator_text,
    filename=str(
        ORCHESTRATOR_PATH
    ),
)


supported_assignment = None
creator_function = None


for node in orchestrator_tree.body:
    if isinstance(
        node,
        (
            ast.Assign,
            ast.AnnAssign,
        ),
    ):
        targets = (
            node.targets
            if isinstance(
                node,
                ast.Assign,
            )
            else [
                node.target
            ]
        )

        if any(
            isinstance(
                target,
                ast.Name,
            )
            and target.id
            == "SUPPORTED_JOB_TYPES"
            for target in targets
        ):
            supported_assignment = node

    if (
        isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name
        == "create_universal_knowledge_job"
    ):
        creator_function = node


if supported_assignment is None:
    raise RuntimeError(
        "SUPPORTED_JOB_TYPES was not found."
    )

if creator_function is None:
    raise RuntimeError(
        "create_universal_knowledge_job was not found."
    )


# ---------------------------------------------------------------------
# Add udare_reconstruction to SUPPORTED_JOB_TYPES.
# ---------------------------------------------------------------------

supported_value = (
    supported_assignment.value
)

existing_job_types = {
    element.value
    for element in supported_value.elts
    if (
        isinstance(
            element,
            ast.Constant,
        )
        and isinstance(
            element.value,
            str,
        )
    )
}


if UDARE_JOB_TYPE not in existing_job_types:
    lines = orchestrator_text.splitlines(
        keepends=True
    )

    closing_line_index = (
        supported_value.end_lineno - 1
    )

    element_indent = "    "

    for line_index in range(
        supported_value.lineno - 1,
        closing_line_index,
    ):
        stripped = lines[
            line_index
        ].lstrip()

        if stripped.startswith(
            (
                '"',
                "'",
            )
        ):
            element_indent = (
                lines[
                    line_index
                ][
                    :len(
                        lines[
                            line_index
                        ]
                    )
                    - len(
                        stripped
                    )
                ]
            )
            break

    lines.insert(
        closing_line_index,
        (
            f'{element_indent}'
            f'"{UDARE_JOB_TYPE}",\n'
        ),
    )

    orchestrator_text = "".join(
        lines
    )


# Reparse after registry insertion so line offsets are current.
orchestrator_tree = ast.parse(
    orchestrator_text,
    filename=str(
        ORCHESTRATOR_PATH
    ),
)

creator_function = next(
    node
    for node in orchestrator_tree.body
    if (
        isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name
        == "create_universal_knowledge_job"
    )
)

creator_start, creator_end = (
    node_offsets(
        orchestrator_text,
        creator_function,
    )
)

creator_source = (
    orchestrator_text[
        creator_start:
        creator_end
    ]
)


# ---------------------------------------------------------------------
# Add enqueue=True without changing existing caller behavior.
# ---------------------------------------------------------------------

if "enqueue: bool = True" not in creator_source:
    old_signature_end = '''    batch_id: str = "",
) -> Dict[str, Any]:'''

    new_signature_end = '''    batch_id: str = "",
    enqueue: bool = True,
) -> Dict[str, Any]:'''

    if old_signature_end not in creator_source:
        raise RuntimeError(
            "Expected creator signature ending was not found."
        )

    creator_source = creator_source.replace(
        old_signature_end,
        new_signature_end,
        1,
    )


# ---------------------------------------------------------------------
# Derive initial status from whether queue dispatch was requested.
# ---------------------------------------------------------------------

if (
    'initial_status = "queued" if enqueue else "registered"'
    not in creator_source
):
    old_payload_setup = '''    ws = safe_id(workspace_id)
    payload = payload or {}
    job_id = make_job_id(ws, job_type, payload)
'''

    new_payload_setup = '''    ws = safe_id(workspace_id)
    payload = payload or {}
    initial_status = "queued" if enqueue else "registered"
    job_id = make_job_id(ws, job_type, payload)
'''

    if old_payload_setup not in creator_source:
        raise RuntimeError(
            "Expected payload setup block was not found."
        )

    creator_source = creator_source.replace(
        old_payload_setup,
        new_payload_setup,
        1,
    )


queued_status_count = creator_source.count(
    '"status": "queued"'
)

if queued_status_count not in {
    0,
    2,
}:
    raise RuntimeError(
        "Unexpected number of queued status literals "
        f"inside creator: {queued_status_count}"
    )

if queued_status_count == 2:
    creator_source = creator_source.replace(
        '"status": "queued"',
        '"status": initial_status',
    )


# ---------------------------------------------------------------------
# Queue insertion is now conditional.
# Ledger/status/progress persistence remains unconditional.
# ---------------------------------------------------------------------

old_queue_write = '''    append_jsonl(queue_path(ws), job)
    append_jsonl(job_ledger_path(ws), {"event": "job_created", **job})
'''

new_queue_write = '''    if enqueue:
        append_jsonl(queue_path(ws), job)

    append_jsonl(job_ledger_path(ws), {"event": "job_created", **job})
'''

if old_queue_write in creator_source:
    creator_source = creator_source.replace(
        old_queue_write,
        new_queue_write,
        1,
    )
elif "if enqueue:" not in creator_source:
    raise RuntimeError(
        "Expected unconditional queue write was not found."
    )


old_progress_message = (
    '"message": "Job queued.",'
)

new_progress_message = '''"message": (
            "Job queued."
            if enqueue
            else "Job registered without queue dispatch."
        ),'''

if old_progress_message in creator_source:
    creator_source = creator_source.replace(
        old_progress_message,
        new_progress_message,
        1,
    )


orchestrator_text = (
    orchestrator_text[
        :creator_start
    ]
    + creator_source
    + orchestrator_text[
        creator_end:
    ]
)


# Validate before writing.
ast.parse(
    orchestrator_text,
    filename=str(
        ORCHESTRATOR_PATH
    ),
)

ORCHESTRATOR_PATH.write_text(
    orchestrator_text,
    encoding="utf-8",
)


# =====================================================================
# 2. PATCH UDARE PRIORITY MAPPING
# =====================================================================

contract_text = CONTRACT_PATH.read_text(
    encoding="utf-8-sig"
)


if "def _priority_value_v1(" not in contract_text:
    insertion_marker = (
        "def _creator_values_v1(\n"
    )

    priority_helper = '''
def _priority_value_v1(
    value: Any,
) -> int:
    """
    Convert user-facing priority names to the universal runtime's
    integer priority contract. Lower numbers represent higher priority.
    """

    if isinstance(
        value,
        bool,
    ):
        return DEFAULT_PRIORITY_VALUE

    if isinstance(
        value,
        int,
    ):
        return max(
            1,
            min(
                10,
                value,
            ),
        )

    text = str(
        value
        or ""
    ).strip().casefold()

    named_priorities = {
        "critical":
            1,

        "urgent":
            1,

        "high":
            3,

        "normal":
            5,

        "medium":
            5,

        "low":
            7,

        "background":
            9,
    }

    if text in named_priorities:
        return named_priorities[
            text
        ]

    try:
        parsed = int(
            text
        )

    except (
        TypeError,
        ValueError,
    ):
        return DEFAULT_PRIORITY_VALUE

    return max(
        1,
        min(
            10,
            parsed,
        ),
    )


'''

    if insertion_marker not in contract_text:
        raise RuntimeError(
            "_creator_values_v1 insertion marker was not found."
        )

    contract_text = contract_text.replace(
        insertion_marker,
        (
            priority_helper
            + insertion_marker
        ),
        1,
    )


if (
    "DEFAULT_PRIORITY_VALUE = 5"
    not in contract_text
):
    old_defaults = '''DEFAULT_PRODUCT_ID = "linkcraftor"
DEFAULT_PRIORITY = "normal"
DEFAULT_MAX_ATTEMPTS = 3
'''

    new_defaults = '''DEFAULT_PRODUCT_ID = "linkcraftor"
DEFAULT_PRIORITY = "normal"
DEFAULT_PRIORITY_VALUE = 5
DEFAULT_MAX_ATTEMPTS = 3
'''

    if old_defaults not in contract_text:
        raise RuntimeError(
            "UDARE runtime default constants were not found."
        )

    contract_text = contract_text.replace(
        old_defaults,
        new_defaults,
        1,
    )


old_priority_value = '''        "priority":
            priority,
'''

new_priority_value = '''        "priority":
            _priority_value_v1(
                priority
            ),
'''

if old_priority_value in contract_text:
    contract_text = contract_text.replace(
        old_priority_value,
        new_priority_value,
        1,
    )
elif "_priority_value_v1(" not in contract_text:
    raise RuntimeError(
        "UDARE adapter priority assignment was not found."
    )


ast.parse(
    contract_text,
    filename=str(
        CONTRACT_PATH
    ),
)

CONTRACT_PATH.write_text(
    contract_text,
    encoding="utf-8",
)


print(
    "PHASE 2B SOURCE PATCH: PASS"
)

print(
    "Registered universal job type:",
    UDARE_JOB_TYPE,
)

print(
    "Universal job creator now supports "
    "enqueue=False with status=registered."
)

print(
    "Existing callers retain enqueue=True behavior."
)

print(
    "UDARE named priorities now map to integer priorities."
)
