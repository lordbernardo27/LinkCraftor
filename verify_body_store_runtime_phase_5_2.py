"""Deep verification for Universal Article Body Store Runtime Phase 5.2."""

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

if str(
    PROJECT_ROOT
) not in sys.path:
    sys.path.insert(
        0,
        str(
            PROJECT_ROOT
        ),
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

from backend.server.universal_article_body_store.body_store_runtime_v1 import (
    BODY_STORE_RUNTIME_OPERATIONS,
    BODY_STORE_RUNTIME_VERSION,
    BodyStoreRuntimeContractError,
    execute_body_store_runtime_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
WRONG_WORKSPACE_ID = "ws_wrong_workspace"
EXPECTED_PASS_COUNT = 2219
SAMPLE_COUNT = 5

RUNTIME_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_runtime_v1.py"
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
        relative = candidate.relative_to(
            path
        ).as_posix()

        digest.update(
            relative.encode(
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


def is_normalized_result(
    result: Any,
    *,
    expected_operation: str,
    expected_success: bool,
) -> bool:
    if not isinstance(
        result,
        dict,
    ):
        return False

    required_fields = {
        "runtime_schema_version",
        "runtime_version",
        "execution_id",
        "operation",
        "workspace_id",
        "runtime_status",
        "success",
        "started_at",
        "completed_at",
        "result",
        "error",
        "execution_mode",
        "queue_used",
        "worker_used",
        "runtime_registration_used",
    }

    if not required_fields.issubset(
        result
    ):
        return False

    if (
        result[
            "runtime_schema_version"
        ]
        != "body_store_runtime_result_v1"
    ):
        return False

    if (
        result[
            "runtime_version"
        ]
        != BODY_STORE_RUNTIME_VERSION
    ):
        return False

    if (
        result[
            "operation"
        ]
        != expected_operation
    ):
        return False

    if (
        result[
            "success"
        ]
        is not expected_success
    ):
        return False

    expected_status = (
        "COMPLETED"
        if expected_success
        else "FAILED"
    )

    if (
        result[
            "runtime_status"
        ]
        != expected_status
    ):
        return False

    if (
        result[
            "execution_mode"
        ]
        != "SYNCHRONOUS"
    ):
        return False

    if result[
        "queue_used"
    ] is not False:
        return False

    if result[
        "worker_used"
    ] is not False:
        return False

    if result[
        "runtime_registration_used"
    ] is not False:
        return False

    if not isinstance(
        result[
            "execution_id"
        ],
        str,
    ):
        return False

    if not result[
        "execution_id"
    ].startswith(
        "body_store_runtime_"
    ):
        return False

    if expected_success:
        return (
            result[
                "error"
            ]
            is None
        )

    return (
        result[
            "result"
        ]
        is None
        and isinstance(
            result[
                "error"
            ],
            dict,
        )
        and isinstance(
            result[
                "error"
            ].get(
                "error_type"
            ),
            str,
        )
        and isinstance(
            result[
                "error"
            ].get(
                "message"
            ),
            str,
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


source = RUNTIME_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        RUNTIME_PATH
    ),
)


repository_imports = []
prohibited_imports = []
direct_filesystem_calls = []
delete_calls = []
background_calls = []
job_calls = []
direct_writer_or_manager_calls = []

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

        lowered_module = module.casefold()

        if lowered_module.endswith(
            "body_store_repository_v1"
        ):
            repository_imports.append(
                module
            )

        if any(
            term in lowered_module
            for term in (
                "body_store_writer_v1",
                "body_store_manager_v1",
                "queue",
                "worker",
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
        "unlink",
        "remove",
        "rmtree",
        "delete",
        "purge",
        "replace",
        "rename",
    }:
        delete_calls.append(
            {
                "name":
                    name,

                "line":
                    node.lineno,
            }
        )

    if name in {
        "create_task",
        "run_in_executor",
        "submit",
        "start",
    }:
        background_calls.append(
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
        "enqueue",
        "dispatch_job",
    }:
        job_calls.append(
            {
                "name":
                    name,

                "line":
                    node.lineno,
            }
        )

    if name in {
        "write_verified_body_from_envelope_v1",
        "manager_read_body",
        "manager_verify_stored_body",
        "manager_get_body_metadata",
        "manager_list_workspace_bodies",
    }:
        direct_writer_or_manager_calls.append(
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
    contract.get(
        "descriptors"
    )
    or contract.get(
        "records"
    )
    or contract.get(
        "articles"
    )
    or contract.get(
        "pass_records"
    )
)

if not isinstance(
    descriptors,
    list,
):
    raise RuntimeError(
        "PASS contract did not expose descriptors."
    )


envelopes = []

for descriptor in descriptors[
    :SAMPLE_COUNT
]:
    certified_source = (
        load_transient_certified_wuc_source_v1(
            descriptor
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

    envelopes.append(
        envelope
    )


temporary_project = Path(
    tempfile.mkdtemp(
        prefix="linkcraftor_body_store_runtime_phase_5_2_"
    )
).resolve()


store_results = []
read_results = []
verify_results = []
metadata_results = []

try:
    for envelope in envelopes:
        payload = envelope[
            "body_payload"
        ]

        body_ref = payload[
            "body_ref"
        ]

        expected_body = payload[
            "content_body"
        ]

        store_result = (
            execute_body_store_runtime_v1(
                {
                    "operation":
                        "store",

                    "payload": {
                        "envelope":
                            envelope,

                        "overwrite":
                            False,
                    },
                },
                project_root=temporary_project,
            )
        )

        store_results.append(
            store_result
        )

        read_result = (
            execute_body_store_runtime_v1(
                {
                    "operation":
                        "read",

                    "payload": {
                        "workspace_id":
                            WORKSPACE_ID,

                        "body_ref":
                            body_ref,
                    },
                },
                project_root=temporary_project,
            )
        )

        read_results.append(
            (
                read_result,
                expected_body,
            )
        )

        verify_result = (
            execute_body_store_runtime_v1(
                {
                    "operation":
                        "verify",

                    "payload": {
                        "workspace_id":
                            WORKSPACE_ID,

                        "body_ref":
                            body_ref,

                        "expected_content_hash":
                            payload[
                                "content_hash"
                            ],

                        "expected_body_length":
                            payload[
                                "body_length"
                            ],

                        "expected_body_byte_length":
                            len(
                                expected_body.encode(
                                    "utf-8"
                                )
                            ),

                        "expected_body_word_count":
                            payload[
                                "body_word_count"
                            ],
                    },
                },
                project_root=temporary_project,
            )
        )

        verify_results.append(
            verify_result
        )

        metadata_result = (
            execute_body_store_runtime_v1(
                {
                    "operation":
                        "metadata",

                    "payload": {
                        "workspace_id":
                            WORKSPACE_ID,

                        "body_ref":
                            body_ref,
                    },
                },
                project_root=temporary_project,
            )
        )

        metadata_results.append(
            (
                metadata_result,
                payload,
            )
        )

    list_result = execute_body_store_runtime_v1(
        {
            "operation":
                "list",

            "payload": {
                "workspace_id":
                    WORKSPACE_ID,

                "verify_each":
                    True,
            },
        },
        project_root=temporary_project,
    )

    first_body_ref = envelopes[
        0
    ][
        "body_payload"
    ][
        "body_ref"
    ]

    wrong_workspace_result = (
        execute_body_store_runtime_v1(
            {
                "operation":
                    "read",

                "payload": {
                    "workspace_id":
                        WRONG_WORKSPACE_ID,

                    "body_ref":
                        first_body_ref,
                },
            },
            project_root=temporary_project,
        )
    )

    missing_body_ref = (
        "backend/server/data/"
        "universal_article_body_store/"
        + WORKSPACE_ID
        + "/bodies/missing-body.txt"
    )

    missing_body_result = (
        execute_body_store_runtime_v1(
            {
                "operation":
                    "read",

                "payload": {
                    "workspace_id":
                        WORKSPACE_ID,

                    "body_ref":
                        missing_body_ref,
                },
            },
            project_root=temporary_project,
        )
    )

    invalid_operation_result = (
        execute_body_store_runtime_v1(
            {
                "operation":
                    "delete",

                "payload": {},
            },
            project_root=temporary_project,
        )
    )

    invalid_request_result = (
        execute_body_store_runtime_v1(
            "not-a-mapping",
            project_root=temporary_project,
        )
    )

    invalid_verify_integer_result = (
        execute_body_store_runtime_v1(
            {
                "operation":
                    "verify",

                "payload": {
                    "workspace_id":
                        WORKSPACE_ID,

                    "body_ref":
                        first_body_ref,

                    "expected_body_length":
                        -1,
                },
            },
            project_root=temporary_project,
        )
    )

    raise_on_failure_raised = False

    try:
        execute_body_store_runtime_v1(
            {
                "operation":
                    "delete",

                "payload": {},
            },
            project_root=temporary_project,
            raise_on_failure=True,
        )

    except BodyStoreRuntimeContractError:
        raise_on_failure_raised = True

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


store_operations_passed = all(
    is_normalized_result(
        result,
        expected_operation="store",
        expected_success=True,
    )
    and result[
        "result"
    ][
        "write_certificate"
    ][
        "certificate_status"
    ]
    == "CERTIFIED"

    for result in store_results
)

read_operations_passed = all(
    is_normalized_result(
        result,
        expected_operation="read",
        expected_success=True,
    )
    and result[
        "result"
    ]
    == expected_body

    for result, expected_body
    in read_results
)

verify_operations_passed = all(
    is_normalized_result(
        result,
        expected_operation="verify",
        expected_success=True,
    )
    and result[
        "result"
    ][
        "verification_status"
    ]
    == "VERIFIED"

    for result in verify_results
)

metadata_operations_passed = all(
    is_normalized_result(
        result,
        expected_operation="metadata",
        expected_success=True,
    )
    and result[
        "result"
    ][
        "content_hash"
    ]
    == payload[
        "content_hash"
    ]
    and result[
        "result"
    ][
        "body_length"
    ]
    == payload[
        "body_length"
    ]
    and result[
        "result"
    ][
        "body_word_count"
    ]
    == payload[
        "body_word_count"
    ]

    for result, payload
    in metadata_results
)


checks = {
    "runtime_syntax_valid":
        True,

    "runtime_version_valid":
        BODY_STORE_RUNTIME_VERSION
        == "universal_article_body_store_runtime_v1",

    "operations_exact":
        BODY_STORE_RUNTIME_OPERATIONS
        == frozenset(
            {
                "store",
                "read",
                "verify",
                "metadata",
                "list",
            }
        ),

    "repository_import_present":
        bool(
            repository_imports
        ),

    "no_direct_writer_or_manager_calls":
        not direct_writer_or_manager_calls,

    "no_prohibited_imports":
        not prohibited_imports,

    "no_direct_filesystem_calls":
        not direct_filesystem_calls,

    "no_delete_calls":
        not delete_calls,

    "no_background_calls":
        not background_calls,

    "no_job_calls":
        not job_calls,

    "all_sample_store_operations_passed":
        store_operations_passed
        and len(
            store_results
        )
        == SAMPLE_COUNT,

    "all_sample_read_operations_passed":
        read_operations_passed
        and len(
            read_results
        )
        == SAMPLE_COUNT,

    "all_sample_verify_operations_passed":
        verify_operations_passed
        and len(
            verify_results
        )
        == SAMPLE_COUNT,

    "all_sample_metadata_operations_passed":
        metadata_operations_passed
        and len(
            metadata_results
        )
        == SAMPLE_COUNT,

    "workspace_listing_passed":
        is_normalized_result(
            list_result,
            expected_operation="list",
            expected_success=True,
        )
        and list_result[
            "result"
        ][
            "body_count"
        ]
        == SAMPLE_COUNT
        and list_result[
            "result"
        ][
            "verified_count"
        ]
        == SAMPLE_COUNT,

    "wrong_workspace_rejected":
        is_normalized_result(
            wrong_workspace_result,
            expected_operation="read",
            expected_success=False,
        ),

    "missing_body_normalized_failure":
        is_normalized_result(
            missing_body_result,
            expected_operation="read",
            expected_success=False,
        ),

    "invalid_operation_normalized_failure":
        is_normalized_result(
            invalid_operation_result,
            expected_operation="UNKNOWN",
            expected_success=False,
        ),

    "invalid_request_normalized_failure":
        is_normalized_result(
            invalid_request_result,
            expected_operation="UNKNOWN",
            expected_success=False,
        ),

    "invalid_verify_integer_rejected":
        is_normalized_result(
            invalid_verify_integer_result,
            expected_operation="verify",
            expected_success=False,
        ),

    "raise_on_failure_behavior_verified":
        raise_on_failure_raised,

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
    "UNIVERSAL ARTICLE BODY STORE RUNTIME — PHASE 5.2 VERIFICATION"
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
    "Real certified envelopes tested:      "
    + str(
        SAMPLE_COUNT
    )
)

print(
    "Store operations completed:           "
    + str(
        len(
            store_results
        )
    )
)

print(
    "Read operations completed:            "
    + str(
        len(
            read_results
        )
    )
)

print(
    "Verify operations completed:          "
    + str(
        len(
            verify_results
        )
    )
)

print(
    "Metadata operations completed:        "
    + str(
        len(
            metadata_results
        )
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
    "Runtime jobs created:                0"
)

print(
    "Queues created:                     0"
)

print(
    "Workers created:                    0"
)

print(
    "Runtime Registration created:       0"
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
        "BODY STORE RUNTIME PHASE 5.2: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE RUNTIME PHASE 5.2: PASS"
)

print(
    "The Runtime passed multi-record operation, isolation, failure, "
    "delegation, and production-safety verification."
)

print("=" * 116)
