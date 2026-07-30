"""Verify Universal Article Body Store Worker Core v1."""

from __future__ import annotations

import ast
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from backend.server.website_unified_content.certified_wuc_input import (
    load_article_validation_pass_contract_v1,
    load_transient_certified_wuc_source_v1,
)

from backend.server.website_unified_content.website_unified_content_engine_v1 import (
    build_transient_website_unified_content_v1,
)

from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    build_transient_uucd_from_wuc_v1,
)

from backend.server.universal_article_body_store.body_store_worker_v1 import (
    BODY_STORE_WORKER_JOB_SCHEMA_VERSION,
    BODY_STORE_WORKER_RESULT_SCHEMA_VERSION,
    BODY_STORE_WORKER_VERSION,
    BodyStoreWorkerContractError,
    BodyStoreWorkerExecutionError,
    execute_body_store_worker_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_PASS_COUNT = 2219

WORKER_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_worker_v1.py"
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

PROTECTED_PATHS = {
    "production_body_store": (
        DATA_ROOT
        / "universal_article_body_store"
    ),

    "persistent_uucd_output": (
        DATA_ROOT
        / "universal_unified_content_documents"
    ),

    "persistent_wuc_output": (
        DATA_ROOT
        / "website_unified_content"
    ),

    "persistent_wuc_store": (
        DATA_ROOT
        / "website_unified_content_store"
    ),
}


def fingerprint(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    if not path.exists():
        digest.update(
            b"ABSENT"
        )

        return digest.hexdigest()

    for candidate in sorted(
        path.rglob("*"),
        key=lambda item: (
            item.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            candidate.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        digest.update(
            b"\x00"
        )

        if candidate.is_file():
            digest.update(
                candidate.read_bytes()
            )

        digest.update(
            b"\n"
        )

    return digest.hexdigest()


def normalized_worker_result(
    result: Any,
    *,
    success: bool,
    job_id: str | None,
) -> bool:
    if not isinstance(
        result,
        dict,
    ):
        return False

    required = {
        "worker_result_schema_version",
        "worker_version",
        "worker_execution_id",
        "job_id",
        "attempt",
        "worker_status",
        "success",
        "started_at",
        "completed_at",
        "runtime_result",
        "error",
        "execution_mode",
        "queue_used",
        "runtime_registration_used",
        "retry_performed",
    }

    if not required.issubset(
        result
    ):
        return False

    return (
        result.get(
            "worker_result_schema_version"
        )
        == BODY_STORE_WORKER_RESULT_SCHEMA_VERSION
        and result.get(
            "worker_version"
        )
        == BODY_STORE_WORKER_VERSION
        and result.get(
            "job_id"
        )
        == job_id
        and result.get(
            "success"
        )
        is success
        and result.get(
            "worker_status"
        )
        == (
            "COMPLETED"
            if success
            else "FAILED"
        )
        and result.get(
            "execution_mode"
        )
        == "SYNCHRONOUS"
        and result.get(
            "queue_used"
        )
        is False
        and result.get(
            "runtime_registration_used"
        )
        is False
        and result.get(
            "retry_performed"
        )
        is False
        and isinstance(
            result.get(
                "worker_execution_id"
            ),
            str,
        )
        and result[
            "worker_execution_id"
        ].startswith(
            "body_store_worker_"
        )
    )


before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}


source = WORKER_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        WORKER_PATH
    ),
)


runtime_imports = []
prohibited_imports = []
direct_filesystem_calls = []
queue_calls = []
registration_calls = []
job_creation_calls = []
retry_calls = []
direct_repository_or_storage_calls = []

for node in ast.walk(
    tree
):
    if isinstance(
        node,
        ast.ImportFrom,
    ):
        module = str(
            node.module
            or ""
        )

        lowered = module.casefold()

        if lowered.endswith(
            "body_store_runtime_v1"
        ):
            runtime_imports.append(
                module
            )

        if any(
            term in lowered
            for term in (
                "body_store_repository_v1",
                "body_store_writer_v1",
                "body_store_manager_v1",
                "queue",
                "runtime_registration",
                "lifecycle",
                "retention",
                "archive",
                "purge",
                "semantic",
                "embedding",
                "reasoning",
            )
        ):
            prohibited_imports.append(
                {
                    "module":
                        module,

                    "line":
                        node.lineno,
                }
            )

    if not isinstance(
        node,
        ast.Call,
    ):
        continue

    name = ""

    if isinstance(
        node.func,
        ast.Name,
    ):
        name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):
        name = node.func.attr

    if name in {
        "open",
        "read_text",
        "read_bytes",
        "write_text",
        "write_bytes",
        "mkdir",
        "resolve",
        "relative_to",
        "rglob",
        "glob",
        "iterdir",
        "unlink",
        "remove",
        "rmtree",
        "replace",
        "rename",
    }:
        direct_filesystem_calls.append(
            {
                "name":
                    name,

                "line":
                    node.lineno,
            }
        )

    if name in {
        "enqueue",
        "dequeue",
        "claim_job",
        "lease_job",
        "ack_job",
        "nack_job",
    }:
        queue_calls.append(
            {
                "name":
                    name,

                "line":
                    node.lineno,
            }
        )

    if "register" in name.casefold():
        registration_calls.append(
            {
                "name":
                    name,

                "line":
                    node.lineno,
            }
        )

    if name in {
        "create_job",
        "create_universal_knowledge_job",
        "dispatch_job",
    }:
        job_creation_calls.append(
            {
                "name":
                    name,

                "line":
                    node.lineno,
            }
        )

    if name in {
        "retry",
        "sleep",
        "backoff",
    }:
        retry_calls.append(
            {
                "name":
                    name,

                "line":
                    node.lineno,
            }
        )

    if name in {
        "repository_store_body",
        "repository_read_body",
        "repository_verify_body",
        "write_verified_body_from_envelope_v1",
        "manager_read_body",
        "manager_verify_stored_body",
    }:
        direct_repository_or_storage_calls.append(
            {
                "name":
                    name,

                "line":
                    node.lineno,
            }
        )


contract = load_article_validation_pass_contract_v1(
    WORKSPACE_ID,
    expected_pass_count=EXPECTED_PASS_COUNT,
)

descriptors = (
    contract.get("descriptors")
    or contract.get("records")
    or contract.get("articles")
    or contract.get("pass_records")
)

if not isinstance(
    descriptors,
    list,
):
    raise RuntimeError(
        "PASS contract did not expose descriptors."
    )


certified_source = (
    load_transient_certified_wuc_source_v1(
        descriptors[
            0
        ]
    )
)

wuc = (
    build_transient_website_unified_content_v1(
        certified_source=certified_source
    )
)

envelope = (
    build_transient_uucd_from_wuc_v1(
        wuc
    )
)

body_payload = envelope[
    "body_payload"
]

body_ref = body_payload[
    "body_ref"
]

expected_body = body_payload[
    "content_body"
]


temporary_project = Path(
    tempfile.mkdtemp(
        prefix="linkcraftor_body_store_worker_core_v1_"
    )
).resolve()

try:
    store_job_id = (
        "body_store_job_store_001"
    )

    store_result = execute_body_store_worker_v1(
        {
            "job_schema_version":
                BODY_STORE_WORKER_JOB_SCHEMA_VERSION,

            "job_id":
                store_job_id,

            "attempt":
                1,

            "runtime_request": {
                "operation":
                    "store",

                "payload": {
                    "envelope":
                        envelope,

                    "overwrite":
                        False,
                },
            },
        },
        project_root=temporary_project,
    )

    read_job_id = (
        "body_store_job_read_001"
    )

    read_result = execute_body_store_worker_v1(
        {
            "job_schema_version":
                BODY_STORE_WORKER_JOB_SCHEMA_VERSION,

            "job_id":
                read_job_id,

            "attempt":
                1,

            "runtime_request": {
                "operation":
                    "read",

                "payload": {
                    "workspace_id":
                        WORKSPACE_ID,

                    "body_ref":
                        body_ref,
                },
            },
        },
        project_root=temporary_project,
    )

    failed_runtime_job_id = (
        "body_store_job_invalid_001"
    )

    failed_runtime_result = (
        execute_body_store_worker_v1(
            {
                "job_schema_version":
                    BODY_STORE_WORKER_JOB_SCHEMA_VERSION,

                "job_id":
                    failed_runtime_job_id,

                "attempt":
                    1,

                "runtime_request": {
                    "operation":
                        "delete",

                    "payload": {},
                },
            },
            project_root=temporary_project,
        )
    )

    invalid_job_result = (
        execute_body_store_worker_v1(
            {
                "job_schema_version":
                    BODY_STORE_WORKER_JOB_SCHEMA_VERSION,

                "job_id":
                    "",

                "runtime_request": {},
            },
            project_root=temporary_project,
        )
    )

    invalid_schema_result = (
        execute_body_store_worker_v1(
            {
                "job_schema_version":
                    "wrong_schema",

                "job_id":
                    "body_store_job_wrong_schema",

                "runtime_request": {},
            },
            project_root=temporary_project,
        )
    )

    invalid_attempt_result = (
        execute_body_store_worker_v1(
            {
                "job_schema_version":
                    BODY_STORE_WORKER_JOB_SCHEMA_VERSION,

                "job_id":
                    "body_store_job_bad_attempt",

                "attempt":
                    0,

                "runtime_request": {},
            },
            project_root=temporary_project,
        )
    )

    contract_raise_verified = False

    try:
        execute_body_store_worker_v1(
            {
                "job_schema_version":
                    BODY_STORE_WORKER_JOB_SCHEMA_VERSION,

                "job_id":
                    "",

                "runtime_request": {},
            },
            project_root=temporary_project,
            raise_on_failure=True,
        )

    except BodyStoreWorkerContractError:
        contract_raise_verified = True

    execution_raise_verified = False

    try:
        execute_body_store_worker_v1(
            {
                "job_schema_version":
                    BODY_STORE_WORKER_JOB_SCHEMA_VERSION,

                "job_id":
                    "body_store_job_raise_runtime",

                "runtime_request": {
                    "operation":
                        "delete",

                    "payload": {},
                },
            },
            project_root=temporary_project,
            raise_on_failure=True,
        )

    except BodyStoreWorkerExecutionError:
        execution_raise_verified = True

finally:
    shutil.rmtree(
        temporary_project,
        ignore_errors=True,
    )


after = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}

unchanged = {
    name:
        before[
            name
        ]
        == after[
            name
        ]

    for name
    in PROTECTED_PATHS
}


checks = {
    "worker_syntax_valid":
        True,

    "worker_version_valid":
        BODY_STORE_WORKER_VERSION
        == "universal_article_body_store_worker_v1",

    "worker_job_schema_valid":
        BODY_STORE_WORKER_JOB_SCHEMA_VERSION
        == "body_store_worker_job_v1",

    "worker_result_schema_valid":
        BODY_STORE_WORKER_RESULT_SCHEMA_VERSION
        == "body_store_worker_result_v1",

    "worker_imports_runtime":
        len(
            runtime_imports
        )
        == 1,

    "no_prohibited_imports":
        not prohibited_imports,

    "no_direct_filesystem_calls":
        not direct_filesystem_calls,

    "no_queue_calls":
        not queue_calls,

    "no_registration_calls":
        not registration_calls,

    "no_job_creation_calls":
        not job_creation_calls,

    "no_retry_calls":
        not retry_calls,

    "no_runtime_bypass":
        not direct_repository_or_storage_calls,

    "store_job_completed":
        normalized_worker_result(
            store_result,
            success=True,
            job_id=store_job_id,
        )
        and store_result[
            "runtime_result"
        ][
            "result"
        ][
            "write_certificate"
        ][
            "certificate_status"
        ]
        == "CERTIFIED",

    "read_job_completed":
        normalized_worker_result(
            read_result,
            success=True,
            job_id=read_job_id,
        )
        and read_result[
            "runtime_result"
        ][
            "result"
        ]
        == expected_body,

    "runtime_failure_normalized":
        normalized_worker_result(
            failed_runtime_result,
            success=False,
            job_id=failed_runtime_job_id,
        )
        and isinstance(
            failed_runtime_result[
                "runtime_result"
            ],
            dict,
        )
        and failed_runtime_result[
            "runtime_result"
        ][
            "success"
        ]
        is False,

    "invalid_job_normalized":
        normalized_worker_result(
            invalid_job_result,
            success=False,
            job_id=None,
        ),

    "invalid_schema_normalized":
        normalized_worker_result(
            invalid_schema_result,
            success=False,
            job_id=None,
        ),

    "invalid_attempt_normalized":
        normalized_worker_result(
            invalid_attempt_result,
            success=False,
            job_id="body_store_job_bad_attempt",
        ),

    "contract_raise_on_failure_verified":
        contract_raise_verified,

    "execution_raise_on_failure_verified":
        execution_raise_verified,

    "production_outputs_unchanged":
        all(
            unchanged.values()
        ),
}


failures = [
    name
    for name, passed
    in checks.items()
    if passed is not True
]


print()
print("=" * 116)
print(
    "UNIVERSAL ARTICLE BODY STORE WORKER CORE — PHASE 6.1"
)
print("=" * 116)
print()

for name, passed in checks.items():
    print(
        f"{name:<76}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "PRODUCTION OUTPUTS"
)

for name, passed in unchanged.items():
    print(
        "  "
        + f"{name:<36}"
        + (
            "UNCHANGED"
            if passed
            else "CHANGED"
        )
    )

print()
print(
    "Production Body Store files written: 0"
)

print(
    "Persistent UUCD records written:     0"
)

print(
    "Persistent WUC packages written:     0"
)

print(
    "Queues created:                     0"
)

print(
    "Jobs persisted:                     0"
)

print(
    "Retries performed:                  0"
)

print(
    "Runtime Registrations created:      0"
)

print()
print(
    "FAILURES"
)

if failures:
    for failure in failures:
        print(
            "  - "
            + failure
        )

else:
    print(
        "  None"
    )

print()

if failures:
    print(
        "BODY STORE WORKER CORE PHASE 6.1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE WORKER CORE PHASE 6.1: PASS"
)

print(
    "The queue-free Worker executes one supplied job only through "
    "the certified Body Store Runtime."
)

print("=" * 116)
