"""Certify the Universal Article Body Store Runtime."""

from __future__ import annotations

import ast
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
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

from backend.server.universal_article_body_store.body_store_runtime_v1 import (
    BODY_STORE_RUNTIME_OPERATIONS,
    BODY_STORE_RUNTIME_VERSION,
    execute_body_store_runtime_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_PASS_COUNT = 2219
CERTIFICATION_SAMPLE_COUNT = 10

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

DATA_ROOT = (
    SERVER_ROOT
    / "data"
)

PACKAGE_ROOT = (
    SERVER_ROOT
    / "universal_article_body_store"
)

RUNTIME_PATH = (
    PACKAGE_ROOT
    / "body_store_runtime_v1.py"
)

REPOSITORY_PATH = (
    PACKAGE_ROOT
    / "body_store_repository_v1.py"
)

WRITER_PATH = (
    PACKAGE_ROOT
    / "body_store_writer_v1.py"
)

MANAGER_PATH = (
    PACKAGE_ROOT
    / "body_store_manager_v1.py"
)

EVIDENCE_ROOT = (
    DATA_ROOT
    / "universal_article_body_store_runtime"
)

VERIFICATION_PATH = (
    EVIDENCE_ROOT
    / "verification"
    / "body_store_runtime_verification_report_v1.json"
)

CERTIFICATE_PATH = (
    EVIDENCE_ROOT
    / "certification"
    / "body_store_runtime_certificate_v1.json"
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


def now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def sha256_bytes(
    value: bytes,
) -> str:
    return hashlib.sha256(
        value
    ).hexdigest()


def sha256_file(
    path: Path,
) -> str:
    return sha256_bytes(
        path.read_bytes()
    )


def canonical_json_hash(
    value: Any,
) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    ).encode(
        "utf-8"
    )

    return sha256_bytes(
        encoded
    )


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
            with candidate.open(
                "rb"
            ) as handle:
                for block in iter(
                    lambda: handle.read(
                        1024 * 1024
                    ),
                    b"",
                ):
                    digest.update(
                        block
                    )

        digest.update(
            b"\n"
        )

    return digest.hexdigest()


def parse_file(
    path: Path,
) -> tuple[str, ast.Module]:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

    return (
        source,
        ast.parse(
            source,
            filename=str(
                path
            ),
        ),
    )


def import_modules(
    tree: ast.Module,
) -> list[str]:
    modules = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.ImportFrom,
        ):
            modules.append(
                str(
                    node.module
                    or ""
                )
            )

        elif isinstance(
            node,
            ast.Import,
        ):
            modules.extend(
                alias.name
                for alias in node.names
            )

    return sorted(
        set(
            modules
        )
    )


def called_names(
    tree: ast.Module,
) -> list[dict[str, Any]]:
    results = []

    for node in ast.walk(
        tree
    ):
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

        results.append(
            {
                "name":
                    name,

                "line":
                    node.lineno,
            }
        )

    return results


def is_normalized_result(
    result: Any,
    *,
    operation: str,
    success: bool,
) -> bool:
    if not isinstance(
        result,
        dict,
    ):
        return False

    required = {
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

    if not required.issubset(
        result
    ):
        return False

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
            "runtime_status"
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
            "worker_used"
        )
        is False
        and result.get(
            "runtime_registration_used"
        )
        is False
    )


for required_path in (
    RUNTIME_PATH,
    REPOSITORY_PATH,
    WRITER_PATH,
    MANAGER_PATH,
):
    if not required_path.is_file():
        raise RuntimeError(
            "Required Body Store component missing: "
            + str(
                required_path
            )
        )


protected_before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}


runtime_source, runtime_tree = parse_file(
    RUNTIME_PATH
)

repository_source, repository_tree = parse_file(
    REPOSITORY_PATH
)

writer_source, writer_tree = parse_file(
    WRITER_PATH
)

manager_source, manager_tree = parse_file(
    MANAGER_PATH
)


runtime_imports = import_modules(
    runtime_tree
)

repository_imports = import_modules(
    repository_tree
)

runtime_calls = called_names(
    runtime_tree
)

repository_calls = called_names(
    repository_tree
)


runtime_repository_imports = [
    module
    for module in runtime_imports
    if module.endswith(
        "body_store_repository_v1"
    )
]

runtime_writer_or_manager_imports = [
    module
    for module in runtime_imports
    if module.endswith(
        (
            "body_store_writer_v1",
            "body_store_manager_v1",
        )
    )
]

repository_writer_imports = [
    module
    for module in repository_imports
    if module.endswith(
        "body_store_writer_v1"
    )
]

repository_manager_imports = [
    module
    for module in repository_imports
    if module.endswith(
        "body_store_manager_v1"
    )
]


direct_filesystem_names = {
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
}

queue_worker_job_names = {
    "enqueue",
    "dequeue",
    "create_job",
    "create_universal_knowledge_job",
    "dispatch_job",
    "create_task",
    "run_in_executor",
    "submit",
    "start",
}

lifecycle_names = {
    "delete",
    "purge",
    "archive",
    "retain",
    "expire",
    "overwrite_policy",
}

uucd_persistence_names = {
    "persist_uucd",
    "write_uucd",
    "save_uucd",
    "write_uucd_record",
}


runtime_direct_filesystem_calls = [
    item
    for item in runtime_calls
    if item[
        "name"
    ]
    in direct_filesystem_names
]

runtime_queue_worker_job_calls = [
    item
    for item in runtime_calls
    if item[
        "name"
    ]
    in queue_worker_job_names
]

runtime_lifecycle_calls = [
    item
    for item in runtime_calls
    if item[
        "name"
    ]
    in lifecycle_names
]

runtime_uucd_persistence_calls = [
    item
    for item in runtime_calls
    if item[
        "name"
    ]
    in uucd_persistence_names
]


repository_direct_filesystem_calls = [
    item
    for item in repository_calls
    if item[
        "name"
    ]
    in direct_filesystem_names
]

repository_queue_worker_job_calls = [
    item
    for item in repository_calls
    if item[
        "name"
    ]
    in queue_worker_job_names
]

repository_lifecycle_calls = [
    item
    for item in repository_calls
    if item[
        "name"
    ]
    in lifecycle_names
]

repository_uucd_persistence_calls = [
    item
    for item in repository_calls
    if item[
        "name"
    ]
    in uucd_persistence_names
]


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

if len(
    descriptors
) < CERTIFICATION_SAMPLE_COUNT:
    raise RuntimeError(
        "Insufficient certified descriptors for certification."
    )


envelopes = []

for descriptor in descriptors[
    :CERTIFICATION_SAMPLE_COUNT
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
        prefix="linkcraftor_body_store_runtime_certification_"
    )
).resolve()


operation_results = {
    "store":
        [],

    "read":
        [],

    "verify":
        [],

    "metadata":
        [],
}

try:
    for envelope in envelopes:
        payload = envelope[
            "body_payload"
        ]

        expected_body = payload[
            "content_body"
        ]

        body_ref = payload[
            "body_ref"
        ]

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

        operation_results[
            "store"
        ].append(
            store_result
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

        operation_results[
            "read"
        ].append(
            {
                "runtime_result":
                    read_result,

                "body_matches":
                    read_result.get(
                        "result"
                    )
                    == expected_body,
            }
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

        operation_results[
            "verify"
        ].append(
            verify_result
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

        operation_results[
            "metadata"
        ].append(
            {
                "runtime_result":
                    metadata_result,

                "metadata_matches":
                    (
                        metadata_result.get(
                            "result",
                            {},
                        ).get(
                            "content_hash"
                        )
                        == payload[
                            "content_hash"
                        ]
                        and metadata_result.get(
                            "result",
                            {},
                        ).get(
                            "body_length"
                        )
                        == payload[
                            "body_length"
                        ]
                        and metadata_result.get(
                            "result",
                            {},
                        ).get(
                            "body_word_count"
                        )
                        == payload[
                            "body_word_count"
                        ]
                    ),
            }
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

    invalid_result = execute_body_store_runtime_v1(
        {
            "operation":
                "delete",

            "payload": {},
        },
        project_root=temporary_project,
    )

finally:
    shutil.rmtree(
        temporary_project,
        ignore_errors=True,
    )


protected_after = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}

protected_unchanged = {
    name:
        protected_before[
            name
        ]
        == protected_after[
            name
        ]

    for name
    in PROTECTED_PATHS
}


store_certified = all(
    is_normalized_result(
        result,
        operation="store",
        success=True,
    )
    and result.get(
        "result",
        {},
    ).get(
        "write_certificate",
        {},
    ).get(
        "certificate_status"
    )
    == "CERTIFIED"

    for result in operation_results[
        "store"
    ]
)

read_certified = all(
    is_normalized_result(
        item[
            "runtime_result"
        ],
        operation="read",
        success=True,
    )
    and item[
        "body_matches"
    ]
    is True

    for item in operation_results[
        "read"
    ]
)

verify_certified = all(
    is_normalized_result(
        result,
        operation="verify",
        success=True,
    )
    and result.get(
        "result",
        {},
    ).get(
        "verification_status"
    )
    == "VERIFIED"

    for result in operation_results[
        "verify"
    ]
)

metadata_certified = all(
    is_normalized_result(
        item[
            "runtime_result"
        ],
        operation="metadata",
        success=True,
    )
    and item[
        "metadata_matches"
    ]
    is True

    for item in operation_results[
        "metadata"
    ]
)

list_certified = (
    is_normalized_result(
        list_result,
        operation="list",
        success=True,
    )
    and list_result.get(
        "result",
        {},
    ).get(
        "body_count"
    )
    == CERTIFICATION_SAMPLE_COUNT
    and list_result.get(
        "result",
        {},
    ).get(
        "verified_count"
    )
    == CERTIFICATION_SAMPLE_COUNT
)

invalid_operation_certified = (
    is_normalized_result(
        invalid_result,
        operation="UNKNOWN",
        success=False,
    )
)


checks = {
    "runtime_version_certified":
        BODY_STORE_RUNTIME_VERSION
        == "universal_article_body_store_runtime_v1",

    "runtime_operations_certified":
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

    "runtime_imports_repository":
        len(
            runtime_repository_imports
        )
        == 1,

    "runtime_does_not_import_writer_or_manager":
        not runtime_writer_or_manager_imports,

    "repository_imports_writer":
        bool(
            repository_writer_imports
        ),

    "repository_imports_manager":
        bool(
            repository_manager_imports
        ),

    "runtime_no_direct_filesystem":
        not runtime_direct_filesystem_calls,

    "runtime_no_queue_worker_or_job":
        not runtime_queue_worker_job_calls,

    "runtime_no_lifecycle_logic":
        not runtime_lifecycle_calls,

    "runtime_no_uucd_persistence":
        not runtime_uucd_persistence_calls,

    "repository_no_direct_filesystem":
        not repository_direct_filesystem_calls,

    "repository_no_queue_worker_or_job":
        not repository_queue_worker_job_calls,

    "repository_no_lifecycle_logic":
        not repository_lifecycle_calls,

    "repository_no_uucd_persistence":
        not repository_uucd_persistence_calls,

    "store_operation_certified":
        store_certified
        and len(
            operation_results[
                "store"
            ]
        )
        == CERTIFICATION_SAMPLE_COUNT,

    "read_operation_certified":
        read_certified
        and len(
            operation_results[
                "read"
            ]
        )
        == CERTIFICATION_SAMPLE_COUNT,

    "verify_operation_certified":
        verify_certified
        and len(
            operation_results[
                "verify"
            ]
        )
        == CERTIFICATION_SAMPLE_COUNT,

    "metadata_operation_certified":
        metadata_certified
        and len(
            operation_results[
                "metadata"
            ]
        )
        == CERTIFICATION_SAMPLE_COUNT,

    "list_operation_certified":
        list_certified,

    "failure_normalization_certified":
        invalid_operation_certified,

    "production_outputs_unchanged":
        all(
            protected_unchanged.values()
        ),
}


failed_checks = [
    name
    for name, passed
    in checks.items()
    if passed is not True
]


component_hashes = {
    "runtime_sha256":
        sha256_file(
            RUNTIME_PATH
        ),

    "repository_sha256":
        sha256_file(
            REPOSITORY_PATH
        ),

    "writer_sha256":
        sha256_file(
            WRITER_PATH
        ),

    "manager_sha256":
        sha256_file(
            MANAGER_PATH
        ),
}


verification_report = {
    "schema_version":
        "body_store_runtime_verification_report_v1",

    "generated_at":
        now_iso(),

    "runtime_version":
        BODY_STORE_RUNTIME_VERSION,

    "workspace_id":
        WORKSPACE_ID,

    "verification_mode":
        "ISOLATED_SYNCHRONOUS",

    "certification_sample_count":
        CERTIFICATION_SAMPLE_COUNT,

    "certified_input_count_available":
        len(
            descriptors
        ),

    "supported_operations":
        sorted(
            BODY_STORE_RUNTIME_OPERATIONS
        ),

    "checks":
        checks,

    "failed_checks":
        failed_checks,

    "component_hashes":
        component_hashes,

    "protected_outputs_unchanged":
        protected_unchanged,

    "runtime_jobs_created":
        0,

    "queues_created":
        0,

    "workers_created":
        0,

    "runtime_registrations_created":
        0,

    "production_body_store_files_written":
        0,

    "persistent_uucd_records_written":
        0,

    "persistent_wuc_packages_written":
        0,
}


verification_hash = canonical_json_hash(
    verification_report
)


certificate_core = {
    "schema_version":
        "body_store_runtime_certificate_v1",

    "issued_at":
        now_iso(),

    "certificate_scope":
        "UNIVERSAL_ARTICLE_BODY_STORE_RUNTIME",

    "runtime_version":
        BODY_STORE_RUNTIME_VERSION,

    "certificate_status":
        (
            "CERTIFIED"
            if not failed_checks
            else "NOT_CERTIFIED"
        ),

    "frozen_contract": {
        "placement":
            (
                "Caller -> Body Store Runtime -> Body Store Repository "
                "-> Writer/Management Layer -> Persistent Body Store"
            ),

        "execution_mode":
            "SYNCHRONOUS",

        "queue_free":
            True,

        "worker_free":
            True,

        "runtime_registration_free":
            True,

        "repository_only_delegation":
            True,

        "direct_filesystem_access":
            False,

        "uucd_persistence":
            False,

        "lifecycle_logic":
            False,

        "semantic_processing":
            False,

        "background_execution":
            False,
    },

    "certified_operations":
        sorted(
            BODY_STORE_RUNTIME_OPERATIONS
        ),

    "certification_sample_count":
        CERTIFICATION_SAMPLE_COUNT,

    "all_checks_passed":
        not failed_checks,

    "failed_checks":
        failed_checks,

    "verification_report_sha256":
        verification_hash,

    "component_hashes":
        component_hashes,
}


certificate_id = (
    "body_store_runtime_certificate_"
    + canonical_json_hash(
        certificate_core
    )[
        :24
    ]
)

certificate = {
    **certificate_core,

    "certificate_id":
        certificate_id,
}


VERIFICATION_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

CERTIFICATE_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

VERIFICATION_PATH.write_text(
    json.dumps(
        verification_report,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)

CERTIFICATE_PATH.write_text(
    json.dumps(
        certificate,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


written_verification = json.loads(
    VERIFICATION_PATH.read_text(
        encoding="utf-8-sig"
    )
)

written_certificate = json.loads(
    CERTIFICATE_PATH.read_text(
        encoding="utf-8-sig"
    )
)


evidence_checks = {
    "verification_report_written":
        VERIFICATION_PATH.is_file(),

    "certificate_written":
        CERTIFICATE_PATH.is_file(),

    "verification_report_hash_matches":
        canonical_json_hash(
            written_verification
        )
        == verification_hash,

    "certificate_status_certified":
        written_certificate.get(
            "certificate_status"
        )
        == "CERTIFIED",

    "certificate_id_matches":
        written_certificate.get(
            "certificate_id"
        )
        == certificate_id,

    "certificate_verification_hash_matches":
        written_certificate.get(
            "verification_report_sha256"
        )
        == verification_hash,
}


evidence_failures = [
    name
    for name, passed
    in evidence_checks.items()
    if passed is not True
]


print()
print("=" * 118)
print(
    "UNIVERSAL ARTICLE BODY STORE RUNTIME — PHASE 5.3 CERTIFICATION"
)
print("=" * 118)
print()

print(
    "ARCHITECTURE CHECKS"
)

for name, passed in checks.items():
    print(
        f"{name:<80}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "EVIDENCE CHECKS"
)

for name, passed in evidence_checks.items():
    print(
        f"{name:<80}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Certification sample count:          "
    + str(
        CERTIFICATION_SAMPLE_COUNT
    )
)

print(
    "Available certified articles:        "
    + str(
        len(
            descriptors
        )
    )
)

print(
    "Certificate status:                  "
    + str(
        certificate[
            "certificate_status"
        ]
    )
)

print(
    "Certificate ID:                      "
    + certificate_id
)

print()
print(
    "Verification report:"
)

print(
    "  "
    + str(
        VERIFICATION_PATH
    )
)

print()
print(
    "Certificate:"
)

print(
    "  "
    + str(
        CERTIFICATE_PATH
    )
)

print()
print(
    "PROTECTED PRODUCTION OUTPUTS"
)

for name, unchanged in protected_unchanged.items():
    print(
        "  "
        + f"{name:<36}"
        + (
            "UNCHANGED"
            if unchanged
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
    "Runtime Registrations created:      0"
)

print()
print(
    "FAILURES"
)

all_failures = [
    *failed_checks,
    *evidence_failures,
]

if all_failures:
    for failure in all_failures:
        print(
            "  - "
            + failure
        )

else:
    print(
        "  None"
    )

print()

if all_failures:
    print(
        "BODY STORE RUNTIME PHASE 5.3: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE RUNTIME PHASE 5.3: CERTIFIED"
)

print(
    "The synchronous Body Store Runtime conforms to the frozen "
    "Repository-only, queue-free, worker-free execution contract."
)

print("=" * 118)
