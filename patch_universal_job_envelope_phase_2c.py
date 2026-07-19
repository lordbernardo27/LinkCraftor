from __future__ import annotations

import ast
from pathlib import Path


path = Path(
    "backend/server/jobs/universal_knowledge_orchestrator.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)


def source_offsets(
    value: str,
) -> list[int]:
    offsets = [0]

    for index, character in enumerate(
        value
    ):
        if character == "\n":
            offsets.append(
                index + 1
            )

    return offsets


def node_range(
    value: str,
    node: ast.AST,
) -> tuple[int, int]:
    offsets = source_offsets(
        value
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


tree = ast.parse(
    text,
    filename=str(
        path
    ),
)

creator = next(
    (
        node

        for node
        in tree.body

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
    ),
    None,
)

if creator is None:
    raise RuntimeError(
        "create_universal_knowledge_job was not found."
    )

start, end = node_range(
    text,
    creator,
)

function_source = text[
    start:end
]


# =====================================================================
# 1. ADD BACKWARD-COMPATIBLE CANONICAL PARAMETERS
# =====================================================================

if "user_id: str = " not in function_source:
    old_signature = '''    payload: Dict[str, Any] | None = None,
    priority: int = 5,
'''

    new_signature = '''    payload: Dict[str, Any] | None = None,
    user_id: str = "system",
    product_id: str = "linkcraftor",
    pipeline: str = "",
    stage: str = "",
    payload_ref: str = "",
    priority: int = 5,
'''

    if old_signature not in function_source:
        raise RuntimeError(
            "Expected creator signature marker was not found."
        )

    function_source = function_source.replace(
        old_signature,
        new_signature,
        1,
    )


# =====================================================================
# 2. BUILD CANONICAL ENVELOPE VALUES
# =====================================================================

canonical_marker = (
    "    canonical_user_id = str(\n"
)

if canonical_marker not in function_source:
    old_setup = '''    ws = safe_id(workspace_id)
    payload = payload or {}
    initial_status = "queued" if enqueue else "registered"
    job_id = make_job_id(ws, job_type, payload)
'''

    new_setup = '''    ws = safe_id(workspace_id)
    payload = payload or {}
    initial_status = "queued" if enqueue else "registered"

    canonical_user_id = str(
        user_id
        or payload.get("user_id")
        or "system"
    ).strip() or "system"

    canonical_product_id = str(
        product_id
        or payload.get("product_id")
        or "linkcraftor"
    ).strip() or "linkcraftor"

    canonical_pipeline = str(
        pipeline
        or payload.get("pipeline")
        or payload.get("pipeline_name")
        or "universal_knowledge"
    ).strip() or "universal_knowledge"

    canonical_stage = str(
        stage
        or payload.get("stage")
        or payload.get("stage_name")
        or job_type
    ).strip() or job_type

    canonical_payload_ref = str(
        payload_ref
        or payload.get("payload_ref")
        or payload.get("payload_reference")
        or payload.get("source_record_id")
        or payload.get("html_id")
        or ""
    ).strip()

    initial_progress = {
        "percent": 0,
        "message": (
            "Job queued."
            if enqueue
            else "Job registered without queue dispatch."
        ),
        "steps": [],
    }

    job_id = make_job_id(ws, job_type, payload)
'''

    if old_setup not in function_source:
        raise RuntimeError(
            "Expected creator setup block was not found."
        )

    function_source = function_source.replace(
        old_setup,
        new_setup,
        1,
    )


# =====================================================================
# 3. ADD THE FROZEN CANONICAL JOB ENVELOPE
# =====================================================================

if '"user_id": canonical_user_id' not in function_source:
    old_job_identity = '''        "job_id": job_id,
        "workspace_id": ws,
        "job_type": job_type,
        "priority": int(priority),
'''

    new_job_identity = '''        "job_id": job_id,
        "workspace_id": ws,
        "user_id": canonical_user_id,
        "product_id": canonical_product_id,
        "pipeline": canonical_pipeline,
        "stage": canonical_stage,
        "job_type": job_type,
        "payload_ref": canonical_payload_ref,
        "priority": int(priority),
'''

    if old_job_identity not in function_source:
        raise RuntimeError(
            "Expected job identity block was not found."
        )

    function_source = function_source.replace(
        old_job_identity,
        new_job_identity,
        1,
    )


if '"attempt_count": 0' not in function_source:
    old_execution_fields = '''        "attempts": 0,
        "max_attempts": int(payload.get("max_attempts") or 3),
        "created_at": now_iso(),
        "updated_at": now_iso(),
'''

    new_execution_fields = '''        "attempts": 0,
        "attempt_count": 0,
        "max_attempts": int(payload.get("max_attempts") or 3),
        "lease_owner": None,
        "progress": initial_progress,
        "au_usage": 0,
        "cost_usage": 0.0,
        "created_at": now_iso(),
        "started_at": None,
        "completed_at": None,
        "updated_at": now_iso(),
        "error": None,
        "error_info": None,
'''

    if old_execution_fields not in function_source:
        raise RuntimeError(
            "Expected job execution field block was not found."
        )

    function_source = function_source.replace(
        old_execution_fields,
        new_execution_fields,
        1,
    )


# Keep the separate progress asset aligned with the job envelope.
old_progress_record = '''        "status": initial_status,
        "percent": 0,
        "message": (
            "Job queued."
            if enqueue
            else "Job registered without queue dispatch."
        ),
        "steps": [],
        "updated_at": now_iso(),
'''

new_progress_record = '''        "status": initial_status,
        "percent": initial_progress["percent"],
        "message": initial_progress["message"],
        "steps": initial_progress["steps"],
        "updated_at": now_iso(),
'''

if old_progress_record in function_source:
    function_source = function_source.replace(
        old_progress_record,
        new_progress_record,
        1,
    )


updated_text = (
    text[
        :start
    ]
    + function_source
    + text[
        end:
    ]
)


# Verify syntax before writing.
ast.parse(
    updated_text,
    filename=str(
        path
    ),
)

path.write_text(
    updated_text,
    encoding="utf-8",
)


print(
    "PHASE 2C SOURCE PATCH: PASS"
)

print(
    "Canonical universal job envelope fields added."
)

print(
    "Existing callers remain compatible through defaults."
)
