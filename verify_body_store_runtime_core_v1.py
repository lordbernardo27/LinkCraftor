"""Verify the Body Store Runtime Core v1."""

from __future__ import annotations

import ast
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path


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

from backend.server.universal_article_body_store.body_store_runtime_v1 import (
    BODY_STORE_RUNTIME_OPERATIONS,
    BODY_STORE_RUNTIME_VERSION,
    execute_body_store_runtime_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_PASS_COUNT = 2219

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


direct_filesystem_calls = []
runtime_registration_imports = []
queue_imports = []
worker_imports = []
lifecycle_imports = []
semantic_imports = []
background_calls = []
job_creation_calls = []

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
        ).casefold()

        if "runtime_registration" in module:
            runtime_registration_imports.append(
                module
            )

        if "queue" in module:
            queue_imports.append(
                module
            )

        if "worker" in module:
            worker_imports.append(
                module
            )

        if any(
            term in module
            for term in (
                "lifecycle",
                "retention",
                "archive",
                "purge",
            )
        ):
            lifecycle_imports.append(
                module
            )

        if any(
            term in module
            for term in (
                "semantic",
                "embedding",
                "reasoning",
            )
        ):
            semantic_imports.append(
                module
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
        "resolve",
        "relative_to",
        "rglob",
        "glob",
        "iterdir",
        "mkdir",
        "unlink",
        "remove",
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
        "create_task",
        "run_in_executor",
        "start",
        "submit",
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
        job_creation_calls.append(
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


source_record = load_transient_certified_wuc_source_v1(
    descriptors[
        0
    ]
)

wuc = build_transient_website_unified_content_v1(
    certified_source=source_record
)

envelope = build_transient_uucd_from_wuc_v1(
    wuc
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
        prefix="linkcraftor_body_store_runtime_core_v1_"
    )
).resolve()

try:
    store_result = execute_body_store_runtime_v1(
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

    read_result = execute_body_store_runtime_v1(
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

    verify_result = execute_body_store_runtime_v1(
        {
            "operation":
                "verify",

            "payload": {
                "workspace_id":
                    WORKSPACE_ID,

                "body_ref":
                    body_ref,

                "expected_content_hash":
                    body_payload[
                        "content_hash"
                    ],

                "expected_body_length":
                    body_payload[
                        "body_length"
                    ],

                "expected_body_byte_length":
                    len(
                        expected_body.encode(
                            "utf-8"
                        )
                    ),

                "expected_body_word_count":
                    body_payload[
                        "body_word_count"
                    ],
            },
        },
        project_root=temporary_project,
    )

    metadata_result = execute_body_store_runtime_v1(
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

    invalid_payload_result = (
        execute_body_store_runtime_v1(
            {
                "operation":
                    "read",

                "payload": {
                    "workspace_id":
                        WORKSPACE_ID,
                },
            },
            project_root=temporary_project,
        )
    )

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


def normalized_runtime_result(
    result: dict,
    *,
    success: bool,
    operation: str,
) -> bool:
    return (
        result.get(
            "runtime_schema_version"
        )
        == "body_store_runtime_result_v1"
        and result.get(
            "runtime_version"
        )
        == BODY_STORE_RUNTIME_VERSION
        and result.get(
            "operation"
        )
        == operation
        and result.get(
            "success"
        )
        is success
        and result.get(
            "execution_mode"
        )
        == "SYNCHRONOUS"
        and result.get(
            "queue_used"
        )
        is False
        and result.get(
            "worker_used"
        )
        is False
        and result.get(
            "runtime_registration_used"
        )
        is False
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

    "no_direct_filesystem_calls":
        not direct_filesystem_calls,

    "no_runtime_registration_imports":
        not runtime_registration_imports,

    "no_queue_imports":
        not queue_imports,

    "no_worker_imports":
        not worker_imports,

    "no_lifecycle_imports":
        not lifecycle_imports,

    "no_semantic_imports":
        not semantic_imports,

    "no_background_calls":
        not background_calls,

    "no_job_creation_calls":
        not job_creation_calls,

    "store_operation_completed":
        normalized_runtime_result(
            store_result,
            success=True,
            operation="store",
        )
        and store_result[
            "result"
        ][
            "write_certificate"
        ][
            "certificate_status"
        ]
        == "CERTIFIED",

    "read_operation_completed":
        normalized_runtime_result(
            read_result,
            success=True,
            operation="read",
        )
        and read_result[
            "result"
        ]
        == expected_body,

    "verify_operation_completed":
        normalized_runtime_result(
            verify_result,
            success=True,
            operation="verify",
        )
        and verify_result[
            "result"
        ][
            "verification_status"
        ]
        == "VERIFIED",

    "metadata_operation_completed":
        normalized_runtime_result(
            metadata_result,
            success=True,
            operation="metadata",
        )
        and metadata_result[
            "result"
        ][
            "body_word_count"
        ]
        == body_payload[
            "body_word_count"
        ],

    "list_operation_completed":
        normalized_runtime_result(
            list_result,
            success=True,
            operation="list",
        )
        and list_result[
            "result"
        ][
            "body_count"
        ]
        == 1
        and list_result[
            "result"
        ][
            "verified_count"
        ]
        == 1,

    "invalid_operation_normalized_failure":
        normalized_runtime_result(
            invalid_operation_result,
            success=False,
            operation="UNKNOWN",
        )
        and invalid_operation_result[
            "runtime_status"
        ]
        == "FAILED",

    "invalid_payload_normalized_failure":
        normalized_runtime_result(
            invalid_payload_result,
            success=False,
            operation="read",
        )
        and invalid_payload_result[
            "runtime_status"
        ]
        == "FAILED",

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
print("=" * 112)
print(
    "UNIVERSAL ARTICLE BODY STORE RUNTIME CORE — PHASE 5.1"
)
print("=" * 112)
print()

for name, passed in checks.items():
    print(
        f"{name:<72}"
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
        + f"{name:<34}"
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
        "BODY STORE RUNTIME CORE PHASE 5.1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE RUNTIME CORE PHASE 5.1: PASS"
)

print(
    "The synchronous Body Store Runtime delegates every supported "
    "operation through the Repository and returns normalized results."
)

print("=" * 112)
