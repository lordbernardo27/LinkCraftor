from __future__ import annotations

import inspect
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


from backend.server.jobs.universal_knowledge_orchestrator import (
    SUPPORTED_JOB_TYPES,
    create_universal_knowledge_job,
    job_status_path,
    queue_path,
    read_job_status,
    update_job_status,
)

from backend.server.runtime.udare_runtime_contract import (
    DEFAULT_PRODUCT_ID,
    UDARE_ARTICLE_DOCUMENT_FORMAT,
    UDARE_ENGINE_VERSION,
    UDARE_RECONSTRUCTION_STAGE,
    UDARE_SOURCE_STORE_VERSION,
    UDARE_TARGET_STORE,
    WEBSITE_RECONSTRUCTION_PIPELINE,
    build_udare_runtime_payload_v1,
    create_udare_reconstruction_job_v1,
)

from backend.server.stores.udare_store import (
    refresh_udare_store_manifest_v1,
    verify_udare_store_v1,
)


ROOT = Path(__file__).resolve().parent

REAL_WORKSPACE_ID = (
    "ws_whattoexpect_com"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "udare_runtime_phase_2c_verification"
    / "udare_runtime_phase_2c_verification.json"
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise RuntimeError(
            message
        )


print()
print("=" * 112)
print(
    "PHASE 2C — UNIVERSAL JOB "
    "ENVELOPE VERIFICATION"
)
print("=" * 112)


# ---------------------------------------------------------------------
# 1. Confirm backward-compatible creator signature.
# ---------------------------------------------------------------------

signature = inspect.signature(
    create_universal_knowledge_job
)

required_parameters = {
    "workspace_id":
        inspect.Parameter.empty,

    "job_type":
        inspect.Parameter.empty,

    "payload":
        None,

    "user_id":
        "system",

    "product_id":
        "linkcraftor",

    "pipeline":
        "",

    "stage":
        "",

    "payload_ref":
        "",

    "priority":
        5,

    "parent_job_id":
        "",

    "batch_id":
        "",

    "enqueue":
        True,
}


signature_checks: Dict[str, bool] = {}

for name, expected_default in (
    required_parameters.items()
):
    parameter = signature.parameters.get(
        name
    )

    signature_checks[
        name
    ] = (
        parameter is not None
        and parameter.default
        == expected_default
    )


# ---------------------------------------------------------------------
# 2. Confirm real UDARE Store remains empty.
# ---------------------------------------------------------------------

refresh_udare_store_manifest_v1(
    REAL_WORKSPACE_ID
)

store_before = verify_udare_store_v1(
    REAL_WORKSPACE_ID
)

require(
    store_before[
        "ok"
    ],
    "Real UDARE Store failed pre-verification.",
)

require(
    store_before[
        "counts"
    ][
        "metadata_records"
    ]
    == 0,
    "Real UDARE Store is not empty before Phase 2C.",
)

require(
    store_before[
        "counts"
    ][
        "article_documents"
    ]
    == 0,
    "Real UDARE article directory is not empty before Phase 2C.",
)


# ---------------------------------------------------------------------
# 3. Create a unique registered UDARE job without queue dispatch.
# ---------------------------------------------------------------------

token = (
    uuid.uuid4().hex
)

workspace_id = (
    "ws_udare_phase2c_"
    + token[:12]
)

source_record_id = (
    "raw_html_phase2c_"
    + token
)

payload = build_udare_runtime_payload_v1(
    workspace_id=
        workspace_id,

    source_record_id=
        source_record_id,

    html_id=
        source_record_id,

    source_url=(
        "https://phase2c.invalid/"
        + token
        + ".html"
    ),

    correlation_id=
        token,

    metadata={
        "verification":
            "phase_2c_complete_envelope",

        "must_not_execute":
            True,
    },
)

created = create_udare_reconstruction_job_v1(
    payload=
        payload,

    user_id=
        "phase_2c_verification",

    product_id=
        DEFAULT_PRODUCT_ID,

    priority=
        "normal",
)

raw_job = (
    created.get(
        "raw_result"
    )
    or {}
)

job_id = str(
    raw_job.get(
        "job_id"
    )
    or ""
)

require(
    bool(
        job_id
    ),
    "No job_id was returned for the Phase 2C test job.",
)


# Read the exact persisted status document.
status_file = job_status_path(
    workspace_id,
    job_id,
)

require(
    status_file.is_file(),
    f"Persisted status file is missing: {status_file}",
)

persisted = json.loads(
    status_file.read_text(
        encoding="utf-8-sig"
    )
)


# ---------------------------------------------------------------------
# 4. Verify all frozen envelope fields.
# ---------------------------------------------------------------------

required_envelope_fields = (
    "schema_version",
    "job_id",
    "workspace_id",
    "user_id",
    "product_id",
    "pipeline",
    "stage",
    "job_type",
    "payload",
    "payload_ref",
    "priority",
    "status",
    "attempts",
    "attempt_count",
    "max_attempts",
    "lease_owner",
    "progress",
    "au_usage",
    "cost_usage",
    "created_at",
    "started_at",
    "completed_at",
    "updated_at",
    "error",
    "error_info",
)

field_presence = {
    field:
        field in persisted

    for field
    in required_envelope_fields
}


value_checks = {
    "job_id":
        persisted.get(
            "job_id"
        )
        == job_id,

    "workspace_id":
        persisted.get(
            "workspace_id"
        )
        == workspace_id,

    "user_id":
        persisted.get(
            "user_id"
        )
        == "phase_2c_verification",

    "product_id":
        persisted.get(
            "product_id"
        )
        == DEFAULT_PRODUCT_ID,

    "pipeline":
        persisted.get(
            "pipeline"
        )
        == WEBSITE_RECONSTRUCTION_PIPELINE,

    "stage":
        persisted.get(
            "stage"
        )
        == UDARE_RECONSTRUCTION_STAGE,

    "job_type":
        persisted.get(
            "job_type"
        )
        == UDARE_RECONSTRUCTION_STAGE,

    "payload_ref":
        persisted.get(
            "payload_ref"
        )
        == source_record_id,

    "priority":
        persisted.get(
            "priority"
        )
        == 5,

    "status":
        persisted.get(
            "status"
        )
        == "registered",

    "attempts":
        persisted.get(
            "attempts"
        )
        == 0,

    "attempt_count":
        persisted.get(
            "attempt_count"
        )
        == 0,

    "lease_owner":
        persisted.get(
            "lease_owner"
        )
        is None,

    "progress":
        isinstance(
            persisted.get(
                "progress"
            ),
            dict,
        )
        and persisted[
            "progress"
        ].get(
            "percent"
        )
        == 0,

    "au_usage":
        persisted.get(
            "au_usage"
        )
        == 0,

    "cost_usage":
        persisted.get(
            "cost_usage"
        )
        == 0.0,

    "started_at":
        persisted.get(
            "started_at"
        )
        is None,

    "completed_at":
        persisted.get(
            "completed_at"
        )
        is None,

    "error":
        persisted.get(
            "error"
        )
        is None,

    "error_info":
        persisted.get(
            "error_info"
        )
        is None,

    "source_store":
        persisted[
            "payload"
        ].get(
            "source_store_version"
        )
        == UDARE_SOURCE_STORE_VERSION,

    "engine":
        persisted[
            "payload"
        ].get(
            "udare_engine"
        )
        == UDARE_ENGINE_VERSION,

    "target_store":
        persisted[
            "payload"
        ].get(
            "target_store"
        )
        == UDARE_TARGET_STORE,

    "article_format":
        persisted[
            "payload"
        ].get(
            "article_document_format"
        )
        == UDARE_ARTICLE_DOCUMENT_FORMAT,
}


# ---------------------------------------------------------------------
# 5. Confirm it never entered the execution queue.
# ---------------------------------------------------------------------

queue_file = queue_path(
    workspace_id
)

queue_contains_job = False

if queue_file.is_file():
    queue_text = queue_file.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    queue_contains_job = (
        job_id in queue_text
        or token in queue_text
    )


# ---------------------------------------------------------------------
# 6. Cancel the registered test job.
# ---------------------------------------------------------------------

update_job_status(
    workspace_id=
        workspace_id,

    job_id=
        job_id,

    status=
        "cancelled",

    message=(
        "phase_2c_verification_complete;"
        "execution_not_authorized"
    ),
)

cancelled = read_job_status(
    workspace_id=
        workspace_id,

    job_id=
        job_id,
)

cancelled_status = str(
    cancelled.get(
        "status"
    )
    or ""
).casefold()


# ---------------------------------------------------------------------
# 7. Confirm no UDARE Store population occurred.
# ---------------------------------------------------------------------

refresh_udare_store_manifest_v1(
    REAL_WORKSPACE_ID
)

store_after = verify_udare_store_v1(
    REAL_WORKSPACE_ID
)

store_unchanged = (
    store_before[
        "counts"
    ]
    == store_after[
        "counts"
    ]
)


checks = {
    "udare_job_type_registered":
        UDARE_RECONSTRUCTION_STAGE
        in SUPPORTED_JOB_TYPES,

    "creator_signature_complete":
        all(
            signature_checks.values()
        ),

    "all_envelope_fields_present":
        all(
            field_presence.values()
        ),

    "all_envelope_values_correct":
        all(
            value_checks.values()
        ),

    "test_job_not_in_queue":
        not queue_contains_job,

    "test_job_cancelled":
        cancelled_status
        in {
            "cancelled",
            "canceled",
        },

    "real_udare_store_unchanged":
        store_unchanged,

    "real_udare_store_still_empty":
        store_after[
            "counts"
        ][
            "metadata_records"
        ]
        == 0
        and store_after[
            "counts"
        ][
            "article_documents"
        ]
        == 0,
}


failed_checks = [
    name

    for name, result
    in checks.items()

    if not result
]


report = {
    "schema_version":
        "udare_runtime_phase_2c_verification_v1",

    "generated_at_utc":
        utc_now(),

    "status":
        (
            "PASS"
            if not failed_checks
            else "FAIL"
        ),

    "phase":
        "Phase 2C — Complete Universal Job Envelope",

    "test_job": {
        "job_id":
            job_id,

        "workspace_id":
            workspace_id,

        "status_file":
            str(
                status_file
            ),

        "queue_file":
            str(
                queue_file
            ),

        "queue_contains_job":
            queue_contains_job,

        "final_status":
            cancelled_status,
    },

    "signature_checks":
        signature_checks,

    "field_presence":
        field_presence,

    "value_checks":
        value_checks,

    "checks":
        checks,

    "failed_checks":
        failed_checks,

    "real_udare_store": {
        "before":
            store_before[
                "counts"
            ],

        "after":
            store_after[
                "counts"
            ],
    },

    "phase_boundaries": {
        "canonical_envelope_complete":
            not failed_checks,

        "queue_invoked":
            False,

        "worker_invoked":
            False,

        "article_reconstructed":
            False,

        "udare_store_populated":
            False,

        "phase_3_started":
            False,
    },

    "next_phase":
        "Phase 3 — UDARE Queue and Workers",
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
    )
    + "\n",
    encoding="utf-8",
)


print()
print("CANONICAL ENVELOPE FIELDS")

for field in required_envelope_fields:
    print(
        f"  {field}:",
        (
            "FOUND"
            if field_presence[
                field
            ]
            else "MISSING"
        ),
    )

print()
print("VALUE CHECKS")

for name, result in value_checks.items():
    print(
        f"  {name}:",
        (
            "PASS"
            if result
            else "FAIL"
        ),
    )

print()
print("PHASE CHECKS")

for name, result in checks.items():
    print(
        f"  {name}:",
        (
            "PASS"
            if result
            else "FAIL"
        ),
    )

print()
print(
    "Test job ID:",
    job_id,
)

print(
    "Test job final status:",
    cancelled_status,
)

print(
    "Queue contains test job:",
    queue_contains_job,
)

print(
    "UDARE Store records:",
    store_after[
        "counts"
    ][
        "metadata_records"
    ],
)

print(
    "UDARE article documents:",
    store_after[
        "counts"
    ][
        "article_documents"
    ],
)

print(
    "Report:",
    REPORT_PATH,
)

print()
print("=" * 112)

if failed_checks:
    print(
        "PHASE 2C — COMPLETE UNIVERSAL "
        "JOB ENVELOPE: FAIL"
    )

    print(
        "Failed checks:",
        ", ".join(
            failed_checks
        ),
    )

else:
    print(
        "PHASE 2C — COMPLETE UNIVERSAL "
        "JOB ENVELOPE: PASS"
    )

print("=" * 112)

print(
    "No queue runner or worker was invoked."
)

print(
    "No article was reconstructed or stored."
)

raise SystemExit(
    0
    if not failed_checks
    else 1
)
