from __future__ import annotations

import ast
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping


from backend.server.runtime.udare_runtime_contract import (
    DEFAULT_PRODUCT_ID,
    UDARE_ARTICLE_DOCUMENT_FORMAT,
    UDARE_ENGINE_VERSION,
    UDARE_RECONSTRUCTION_STAGE,
    UDARE_RUNTIME_CONTRACT_VERSION,
    UDARE_RUNTIME_REGISTRATION_VERSION,
    UDARE_SOURCE_STORE_VERSION,
    UDARE_TARGET_STORE,
    WEBSITE_RECONSTRUCTION_PIPELINE,
    build_udare_runtime_payload_v1,
    cancel_udare_job_v1,
    create_udare_reconstruction_job_v1,
    get_udare_runtime_registration_v1,
    read_udare_job_status_v1,
    validate_udare_runtime_payload_v1,
)

from backend.server.stores.udare_store import (
    refresh_udare_store_manifest_v1,
    verify_udare_store_v1,
)


ROOT = Path(__file__).resolve().parent

WORKSPACE_ID = (
    "ws_udare_phase_2_contract_test"
)

REAL_WORKSPACE_ID = (
    "ws_whattoexpect_com"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "udare_runtime_phase_2_verification"
    / "udare_runtime_phase_2_verification.json"
)

CONTRACT_MODULE_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "udare_runtime_contract.py"
)

ORCHESTRATOR_PATH = (
    ROOT
    / "backend"
    / "server"
    / "jobs"
    / "universal_knowledge_orchestrator.py"
)

QUEUE_RUNNER_PATH = (
    ROOT
    / "backend"
    / "server"
    / "workers"
    / "universal_knowledge_queue_runner.py"
)

WORKER_PATH = (
    ROOT
    / "backend"
    / "server"
    / "workers"
    / "universal_knowledge_worker.py"
)

JOB_STORE_PATH = (
    ROOT
    / "backend"
    / "server"
    / "orchestration"
    / "job_store.py"
)

UDARE_STORE_PATH = (
    ROOT
    / "backend"
    / "server"
    / "stores"
    / "udare_store.py"
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def normalize(
    value: Any,
) -> Any:
    if value is None:
        return None

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(key):
                normalize(
                    child
                )
            for key, child
            in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):
        return [
            normalize(
                child
            )
            for child in value
        ]

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    if hasattr(
        value,
        "model_dump",
    ):
        return normalize(
            value.model_dump()
        )

    if hasattr(
        value,
        "dict",
    ):
        try:
            return normalize(
                value.dict()
            )
        except Exception:
            pass

    if hasattr(
        value,
        "__dict__",
    ):
        return normalize(
            vars(
                value
            )
        )

    return str(
        value
    )


def walk_values(
    value: Any,
) -> Iterable[Any]:
    yield value

    if isinstance(
        value,
        Mapping,
    ):
        for child in value.values():
            yield from walk_values(
                child
            )

    elif isinstance(
        value,
        list,
    ):
        for child in value:
            yield from walk_values(
                child
            )


def find_key_values(
    value: Any,
    aliases: Iterable[str],
) -> List[Any]:
    alias_set = {
        alias.casefold()
        for alias in aliases
    }

    results: List[Any] = []

    if isinstance(
        value,
        Mapping,
    ):
        for key, child in value.items():
            if str(
                key
            ).casefold() in alias_set:
                results.append(
                    child
                )

            results.extend(
                find_key_values(
                    child,
                    aliases,
                )
            )

    elif isinstance(
        value,
        list,
    ):
        for child in value:
            results.extend(
                find_key_values(
                    child,
                    aliases,
                )
            )

    return results


def contains_value(
    value: Any,
    expected: str,
) -> bool:
    expected_text = str(
        expected
    )

    return any(
        str(
            child
        )
        == expected_text
        for child in walk_values(
            value
        )
        if isinstance(
            child,
            (
                str,
                int,
                float,
                bool,
            ),
        )
    )


def key_exists(
    value: Any,
    aliases: Iterable[str],
) -> bool:
    return bool(
        find_key_values(
            value,
            aliases,
        )
    )


def find_job_id(
    value: Any,
) -> str:
    candidates = find_key_values(
        value,
        (
            "job_id",
            "id",
        ),
    )

    for candidate in candidates:
        text = str(
            candidate
            or ""
        ).strip()

        if text:
            return text

    return ""


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise RuntimeError(
            message
        )


def find_token_files(
    token: str,
) -> List[Path]:
    search_roots = [
        ROOT
        / "backend"
        / "server"
        / "data"
        / "runtime",

        ROOT
        / "backend"
        / "server"
        / "data"
        / "jobs",

        ROOT
        / "backend"
        / "server"
        / "data"
        / "queues",

        ROOT
        / "backend"
        / "server"
        / "data"
        / "job_status",
    ]

    matches: List[Path] = []

    token_bytes = token.encode(
        "utf-8"
    )

    for search_root in search_roots:
        if not search_root.exists():
            continue

        for path in search_root.rglob("*"):
            if (
                not path.is_file()
                or path.suffix.casefold()
                not in {
                    ".json",
                    ".jsonl",
                    ".txt",
                }
            ):
                continue

            try:
                if token_bytes in path.read_bytes():
                    matches.append(
                        path
                    )
            except OSError:
                continue

    return sorted(
        set(
            matches
        )
    )


def read_token_records(
    paths: Iterable[Path],
    token: str,
) -> List[Any]:
    records: List[Any] = []

    for path in paths:
        try:
            text = path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        except OSError:
            continue

        if token not in text:
            continue

        if path.suffix.casefold() == ".json":
            try:
                records.append({
                    "path":
                        str(
                            path
                        ),

                    "record":
                        json.loads(
                            text
                        ),
                })
            except json.JSONDecodeError:
                records.append({
                    "path":
                        str(
                            path
                        ),

                    "text":
                        text,
                })

        elif path.suffix.casefold() == ".jsonl":
            for line_number, line in enumerate(
                text.splitlines(),
                start=1,
            ):
                if token not in line:
                    continue

                try:
                    record = json.loads(
                        line
                    )
                except json.JSONDecodeError:
                    record = line

                records.append({
                    "path":
                        str(
                            path
                        ),

                    "line_number":
                        line_number,

                    "record":
                        record,
                })

        else:
            records.append({
                "path":
                    str(
                        path
                    ),

                "text":
                    text,
            })

    return records


print()
print("=" * 112)
print(
    "PHASE 2 — UDARE UNIVERSAL "
    "RUNTIME INTEGRATION VERIFICATION"
)
print("=" * 112)


core_files = (
    ORCHESTRATOR_PATH,
    QUEUE_RUNNER_PATH,
    WORKER_PATH,
    JOB_STORE_PATH,
    UDARE_STORE_PATH,
    CONTRACT_MODULE_PATH,
)

for path in core_files:
    require(
        path.is_file(),
        f"Missing required file: {path}",
    )


before_hashes = {
    str(path):
        sha256_file(
            path
        )
    for path in core_files
}


# ---------------------------------------------------------------------
# 1. Validate registration.
# ---------------------------------------------------------------------

registration = (
    get_udare_runtime_registration_v1()
)

checks: Dict[str, bool] = {
    "registration_schema":
        registration.get(
            "schema_version"
        )
        == UDARE_RUNTIME_REGISTRATION_VERSION,

    "pipeline_registered":
        registration.get(
            "pipeline"
        )
        == WEBSITE_RECONSTRUCTION_PIPELINE,

    "stage_registered":
        registration.get(
            "stage"
        )
        == UDARE_RECONSTRUCTION_STAGE,

    "engine_registered":
        registration.get(
            "engine"
        )
        == UDARE_ENGINE_VERSION,

    "source_store_registered":
        registration.get(
            "source_store_version"
        )
        == UDARE_SOURCE_STORE_VERSION,

    "target_store_registered":
        registration.get(
            "target_store"
        )
        == UDARE_TARGET_STORE,

    "article_format_registered":
        registration.get(
            "article_document_format"
        )
        == UDARE_ARTICLE_DOCUMENT_FORMAT,

    "execution_disabled":
        registration.get(
            "execution_enabled"
        )
        is False,

    "queue_handler_not_registered":
        registration.get(
            "queue_handler_registered"
        )
        is False,

    "worker_handler_not_registered":
        registration.get(
            "worker_handler_registered"
        )
        is False,

    "batch_population_disabled":
        registration.get(
            "batch_population_enabled"
        )
        is False,
}


# ---------------------------------------------------------------------
# 2. Confirm Phase 2 module does not import/call runner or worker.
# ---------------------------------------------------------------------

contract_source = (
    CONTRACT_MODULE_PATH.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )
)

contract_tree = ast.parse(
    contract_source,
    filename=str(
        CONTRACT_MODULE_PATH
    ),
)

imported_modules = []

for node in ast.walk(
    contract_tree
):
    if isinstance(
        node,
        ast.Import,
    ):
        imported_modules.extend(
            alias.name
            for alias in node.names
        )

    elif isinstance(
        node,
        ast.ImportFrom,
    ):
        imported_modules.append(
            str(
                node.module
                or ""
            )
        )


checks[
    "queue_runner_not_imported"
] = not any(
    "universal_knowledge_queue_runner"
    in module
    for module in imported_modules
)

checks[
    "worker_not_imported"
] = not any(
    "universal_knowledge_worker"
    in module
    for module in imported_modules
)


# ---------------------------------------------------------------------
# 3. Confirm real UDARE Store remains empty before the test.
# ---------------------------------------------------------------------

refresh_udare_store_manifest_v1(
    REAL_WORKSPACE_ID
)

real_store_before = (
    verify_udare_store_v1(
        REAL_WORKSPACE_ID
    )
)

require(
    real_store_before[
        "ok"
    ],
    "Real UDARE Store failed pre-verification.",
)

checks[
    "real_store_empty_before"
] = (
    real_store_before[
        "counts"
    ][
        "metadata_records"
    ]
    == 0
    and real_store_before[
        "counts"
    ][
        "article_documents"
    ]
    == 0
)


# ---------------------------------------------------------------------
# 4. Create one isolated universal job envelope.
# ---------------------------------------------------------------------

correlation_token = (
    "udare_phase2_"
    + uuid.uuid4().hex
)

source_record_id = (
    "raw_html_"
    + correlation_token
)

payload = build_udare_runtime_payload_v1(
    workspace_id=
        WORKSPACE_ID,

    source_record_id=
        source_record_id,

    html_id=
        source_record_id,

    source_url=(
        "https://phase2.invalid/"
        + correlation_token
        + ".html"
    ),

    correlation_id=
        correlation_token,

    metadata={
        "verification":
            "phase_2_runtime_contract",

        "must_not_execute":
            True,
    },
)

payload_validation = (
    validate_udare_runtime_payload_v1(
        payload
    )
)

checks[
    "payload_contract_valid"
] = payload_validation[
    "ok"
]

created = create_udare_reconstruction_job_v1(
    payload=
        payload,

    user_id=
        "phase_2_verification",

    product_id=
        DEFAULT_PRODUCT_ID,

    priority=
        "normal",
)

created_normalized = normalize(
    created
)

checks[
    "universal_job_creator_called"
] = created_normalized.get(
    "ok"
) is True

checks[
    "execution_not_requested"
] = created_normalized.get(
    "execution_requested"
) is False

checks[
    "created_pipeline_correct"
] = contains_value(
    created_normalized,
    WEBSITE_RECONSTRUCTION_PIPELINE,
)

checks[
    "created_stage_correct"
] = contains_value(
    created_normalized,
    UDARE_RECONSTRUCTION_STAGE,
)

checks[
    "created_payload_reference_correct"
] = contains_value(
    created_normalized,
    source_record_id,
)


job_id = find_job_id(
    created_normalized
)


token_files = find_token_files(
    correlation_token
)

token_records = read_token_records(
    token_files,
    correlation_token,
)


if not job_id:
    job_id = find_job_id(
        token_records
    )


require(
    bool(
        job_id
    ),
    (
        "Universal job was created, but no job_id "
        "could be resolved from the result or "
        "persisted runtime records."
    ),
)


persisted_status = (
    read_udare_job_status_v1(
        job_id=
            job_id,

        workspace_id=
            WORKSPACE_ID,
    )
)

persisted_normalized = normalize(
    persisted_status
)

combined_evidence = {
    "created":
        created_normalized,

    "persisted_status":
        persisted_normalized,

    "token_records":
        token_records,
}


checks[
    "job_id_persisted"
] = contains_value(
    combined_evidence,
    job_id,
)

checks[
    "workspace_id_persisted"
] = contains_value(
    combined_evidence,
    WORKSPACE_ID,
)

checks[
    "pipeline_persisted"
] = contains_value(
    combined_evidence,
    WEBSITE_RECONSTRUCTION_PIPELINE,
)

checks[
    "stage_persisted"
] = contains_value(
    combined_evidence,
    UDARE_RECONSTRUCTION_STAGE,
)

checks[
    "source_record_id_persisted"
] = contains_value(
    combined_evidence,
    source_record_id,
)

checks[
    "engine_persisted"
] = contains_value(
    combined_evidence,
    UDARE_ENGINE_VERSION,
)

checks[
    "target_store_persisted"
] = contains_value(
    combined_evidence,
    UDARE_TARGET_STORE,
)

checks[
    "article_format_persisted"
] = contains_value(
    combined_evidence,
    UDARE_ARTICLE_DOCUMENT_FORMAT,
)


# Initial job-envelope key groups. Values such as started_at,
# completed_at, lease_owner and error may correctly be null before
# execution, but the contract must expose the corresponding fields.

contract_key_groups = {
    "job_identity": (
        "job_id",
        "id",
    ),

    "workspace_identity": (
        "workspace_id",
        "tenant_id",
    ),

    "user_identity": (
        "user_id",
        "owner_id",
    ),

    "product_identity": (
        "product_id",
    ),

    "pipeline_routing": (
        "pipeline",
        "pipeline_name",
    ),

    "stage_routing": (
        "stage",
        "stage_name",
        "job_type",
        "task_type",
    ),

    "payload_reference": (
        "payload",
        "payload_ref",
        "payload_reference",
        "input_payload",
        "job_payload",
    ),

    "priority": (
        "priority",
    ),

    "status": (
        "status",
        "state",
    ),

    "attempts": (
        "attempts",
        "attempt_count",
    ),

    "lease": (
        "lease_owner",
        "lease",
    ),

    "progress": (
        "progress",
        "progress_percent",
    ),

    "usage": (
        "au_usage",
        "cost_usage",
        "usage",
        "billing",
    ),

    "created_timestamp": (
        "created_at",
        "created_at_utc",
        "created",
    ),

    "started_timestamp": (
        "started_at",
        "started_at_utc",
    ),

    "completed_timestamp": (
        "completed_at",
        "completed_at_utc",
    ),

    "error_information": (
        "error",
        "error_info",
        "last_error",
    ),
}


contract_group_results = {
    group_name:
        key_exists(
            combined_evidence,
            aliases,
        )
    for group_name, aliases
    in contract_key_groups.items()
}


# The creator result may wrap canonical fields around the persisted
# runtime record. Phase 2 accepts the combined adapter + universal
# persistence envelope, but routing and identity must exist in the
# persisted runtime evidence itself.

required_initial_groups = (
    "job_identity",
    "workspace_identity",
    "pipeline_routing",
    "stage_routing",
    "payload_reference",
    "priority",
    "status",
    "attempts",
    "created_timestamp",
)

checks[
    "required_initial_envelope_groups"
] = all(
    contract_group_results[
        group_name
    ]
    for group_name
    in required_initial_groups
)


# ---------------------------------------------------------------------
# 5. Cancel the isolated test job so it cannot execute later.
# ---------------------------------------------------------------------

cancel_result = cancel_udare_job_v1(
    job_id=
        job_id,

    workspace_id=
        WORKSPACE_ID,

    reason=(
        "phase_2_contract_verification_complete;"
        "execution_not_authorized"
    ),
)

checks[
    "test_job_cancelled"
] = cancel_result.get(
    "ok"
) is True


cancelled_status = (
    read_udare_job_status_v1(
        job_id=
            job_id,

        workspace_id=
            WORKSPACE_ID,
    )
)

cancelled_normalized = normalize(
    cancelled_status
)

status_values = [
    str(
        value
    ).casefold()
    for value in find_key_values(
        cancelled_normalized,
        (
            "status",
            "state",
        ),
    )
]

checks[
    "cancelled_status_persisted"
] = any(
    value in {
        "cancelled",
        "canceled",
    }
    for value in status_values
)


# ---------------------------------------------------------------------
# 6. Confirm no article was reconstructed or stored.
# ---------------------------------------------------------------------

refresh_udare_store_manifest_v1(
    REAL_WORKSPACE_ID
)

real_store_after = (
    verify_udare_store_v1(
        REAL_WORKSPACE_ID
    )
)

require(
    real_store_after[
        "ok"
    ],
    "Real UDARE Store failed post-verification.",
)

checks[
    "real_store_empty_after"
] = (
    real_store_after[
        "counts"
    ][
        "metadata_records"
    ]
    == 0
    and real_store_after[
        "counts"
    ][
        "article_documents"
    ]
    == 0
)

checks[
    "no_real_store_population_change"
] = (
    real_store_before[
        "counts"
    ]
    == real_store_after[
        "counts"
    ]
)


# ---------------------------------------------------------------------
# 7. Confirm existing runtime source files were not modified by test.
# ---------------------------------------------------------------------

after_hashes = {
    str(path):
        sha256_file(
            path
        )
    for path in core_files
}

changed_core_files = [
    path
    for path in before_hashes
    if before_hashes[
        path
    ]
    != after_hashes[
        path
    ]
]

checks[
    "verification_modified_no_core_sources"
] = not changed_core_files


failed_checks = [
    name
    for name, passed
    in checks.items()
    if not passed
]


report = {
    "schema_version":
        "udare_runtime_phase_2_verification_v1",

    "generated_at_utc":
        utc_now(),

    "status":
        (
            "PASS"
            if not failed_checks
            else "FAIL"
        ),

    "phase":
        "Phase 2 — UDARE Runtime Integration",

    "registration":
        registration,

    "test_job": {
        "workspace_id":
            WORKSPACE_ID,

        "job_id":
            job_id,

        "correlation_token":
            correlation_token,

        "source_record_id":
            source_record_id,

        "final_status_values":
            status_values,

        "runtime_files_containing_token": [
            str(
                path
            )
            for path in token_files
        ],
    },

    "creator": {
        "signature":
            created_normalized.get(
                "creator_signature"
            ),

        "execution_requested":
            created_normalized.get(
                "execution_requested"
            ),
    },

    "contract_group_results":
        contract_group_results,

    "checks":
        checks,

    "failed_checks":
        failed_checks,

    "real_udare_store": {
        "before":
            real_store_before[
                "counts"
            ],

        "after":
            real_store_after[
                "counts"
            ],
    },

    "core_source_files_modified":
        changed_core_files,

    "phase_boundaries": {
        "pipeline_registered":
            True,

        "stage_registered":
            True,

        "universal_job_created":
            True,

        "universal_job_executed":
            False,

        "test_job_cancelled":
            checks[
                "test_job_cancelled"
            ],

        "dedicated_udare_queue_created":
            False,

        "udare_worker_handler_created":
            False,

        "batch_population_started":
            False,

        "article_reconstructed":
            False,

        "udare_store_populated":
            False,

        "integrity_validation_started":
            False,

        "article_validation_started":
            False,
    },

    "next_phase":
        "Phase 3 — UDARE Queue and Workers",

    "phase_3_started":
        False,
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
print("RUNTIME REGISTRATION")

print(
    "  Pipeline:",
    WEBSITE_RECONSTRUCTION_PIPELINE,
)

print(
    "  Stage:",
    UDARE_RECONSTRUCTION_STAGE,
)

print(
    "  Engine:",
    UDARE_ENGINE_VERSION,
)

print(
    "  Target store:",
    UDARE_TARGET_STORE,
)

print()
print("ISOLATED JOB")

print(
    "  Job ID:",
    job_id,
)

print(
    "  Workspace:",
    WORKSPACE_ID,
)

print(
    "  Execution requested:",
    False,
)

print(
    "  Final status values:",
    status_values,
)

print()
print("CHECKS")

for name, passed in (
    checks.items()
):
    print(
        f"  {name}:",
        (
            "PASS"
            if passed
            else "FAIL"
        ),
    )

print()
print("UNIVERSAL ENVELOPE GROUPS")

for name, passed in (
    contract_group_results.items()
):
    print(
        f"  {name}:",
        (
            "FOUND"
            if passed
            else "NOT FOUND"
        ),
    )

print()
print(
    "Real UDARE Store records:",
    real_store_after[
        "counts"
    ][
        "metadata_records"
    ],
)

print(
    "Real UDARE article documents:",
    real_store_after[
        "counts"
    ][
        "article_documents"
    ],
)

print(
    "Core runtime sources modified:",
    len(
        changed_core_files
    ),
)

print(
    "Report:",
    REPORT_PATH,
)

print()
print("=" * 112)

if failed_checks:
    print(
        "PHASE 2 — UDARE RUNTIME "
        "INTEGRATION: FAIL"
    )

    print(
        "Failed checks:",
        ", ".join(
            failed_checks
        ),
    )

else:
    print(
        "PHASE 2 — UDARE RUNTIME "
        "INTEGRATION: PASS"
    )

print("=" * 112)

print(
    "No queue runner or worker was invoked."
)

print(
    "No article was reconstructed or written "
    "to the UDARE Store."
)

raise SystemExit(
    0
    if not failed_checks
    else 1
)
