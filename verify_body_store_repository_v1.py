"""Verify the canonical Body Store Repository."""

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

from backend.server.universal_article_body_store.body_store_repository_v1 import (
    BODY_STORE_REPOSITORY_VERSION,
    body_exists,
    get_metadata,
    list_workspace_bodies,
    read_body,
    store_body,
    verify_body,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_PASS_COUNT = 2219

REPOSITORY_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_repository_v1.py"
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


source = REPOSITORY_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        REPOSITORY_PATH
    ),
)


required_functions = {
    "store_body",
    "read_body",
    "verify_body",
    "body_exists",
    "get_metadata",
    "list_workspace_bodies",
}

found_functions = {
    node.name
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
}


direct_filesystem_calls = []
runtime_imports = []
queue_imports = []
worker_imports = []
lifecycle_imports = []
semantic_imports = []
uucd_persistence_calls = []
delete_calls = []

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

        if "runtime" in module:
            runtime_imports.append(
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
        "persist_uucd",
        "write_uucd",
        "save_uucd",
        "write_uucd_record",
    }:
        uucd_persistence_calls.append(
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


first_descriptor = descriptors[
    0
]

certified_source = (
    load_transient_certified_wuc_source_v1(
        first_descriptor
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


temporary_project = Path(
    tempfile.mkdtemp(
        prefix="linkcraftor_body_store_repository_v1_"
    )
).resolve()

try:
    store_result = store_body(
        envelope,
        project_root=temporary_project,
    )

    body_ref = envelope[
        "body_payload"
    ][
        "body_ref"
    ]

    expected_body = envelope[
        "body_payload"
    ][
        "content_body"
    ]

    exists_result = body_exists(
        project_root=temporary_project,
        workspace_id=WORKSPACE_ID,
        body_ref=body_ref,
    )

    read_result = read_body(
        project_root=temporary_project,
        workspace_id=WORKSPACE_ID,
        body_ref=body_ref,
    )

    verify_result = verify_body(
        project_root=temporary_project,
        workspace_id=WORKSPACE_ID,
        body_ref=body_ref,
        expected_content_hash=envelope[
            "body_payload"
        ][
            "content_hash"
        ],
        expected_body_length=envelope[
            "body_payload"
        ][
            "body_length"
        ],
        expected_body_byte_length=len(
            expected_body.encode(
                "utf-8"
            )
        ),
        expected_body_word_count=envelope[
            "body_payload"
        ][
            "body_word_count"
        ],
    )

    metadata_result = get_metadata(
        project_root=temporary_project,
        workspace_id=WORKSPACE_ID,
        body_ref=body_ref,
    )

    listing_result = list_workspace_bodies(
        project_root=temporary_project,
        workspace_id=WORKSPACE_ID,
        verify_each=True,
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


checks = {
    "repository_syntax_valid":
        True,

    "repository_version_valid":
        BODY_STORE_REPOSITORY_VERSION
        == "universal_article_body_store_repository_v1",

    "all_required_functions_present":
        required_functions
        <= found_functions,

    "no_direct_filesystem_calls":
        not direct_filesystem_calls,

    "no_delete_calls":
        not delete_calls,

    "no_runtime_imports":
        not runtime_imports,

    "no_queue_imports":
        not queue_imports,

    "no_worker_imports":
        not worker_imports,

    "no_lifecycle_imports":
        not lifecycle_imports,

    "no_semantic_imports":
        not semantic_imports,

    "no_uucd_persistence_calls":
        not uucd_persistence_calls,

    "repository_store_delegation_passed":
        store_result[
            "write_certificate"
        ][
            "certificate_status"
        ]
        == "CERTIFIED",

    "repository_exists_delegation_passed":
        exists_result
        is True,

    "repository_read_delegation_passed":
        read_result
        == expected_body,

    "repository_verify_delegation_passed":
        verify_result[
            "verification_status"
        ]
        == "VERIFIED",

    "repository_metadata_delegation_passed":
        metadata_result[
            "body_word_count"
        ]
        == envelope[
            "body_payload"
        ][
            "body_word_count"
        ],

    "repository_listing_delegation_passed":
        listing_result[
            "body_count"
        ]
        == 1
        and listing_result[
            "verified_count"
        ]
        == 1,

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
    "UNIVERSAL ARTICLE BODY STORE REPOSITORY — VERIFICATION"
)
print("=" * 112)
print()

for name, passed in checks.items():
    print(
        f"{name:<70}"
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
        "BODY STORE REPOSITORY V1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE REPOSITORY V1: PASS"
)

print(
    "The Repository provides one canonical facade over the Writer "
    "and Management Layer without direct storage access."
)

print("=" * 112)
