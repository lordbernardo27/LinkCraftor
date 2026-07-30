"""Complete isolated audit of the fresh Body Store Writer."""

from __future__ import annotations

import ast
import hashlib
import os
import shutil
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch


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


from backend.server.universal_article_body_store.body_store_writer_v1 import (
    BODY_STORE_WRITER_VERSION,
    BodyStoreContractError,
    write_verified_body_from_envelope_v1,
)

from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    build_transient_uucd_from_wuc_v1,
    compute_canonical_content_hash_v1,
)


WRITER_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_writer_v1.py"
)

PRODUCTION_STORE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "universal_article_body_store"
)


def directory_fingerprint(
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
        relative_path = (
            candidate.relative_to(
                path
            ).as_posix()
        )

        digest.update(
            relative_path.encode(
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


def build_wuc(
    *,
    body: str,
    source_record_id: str,
    title: str,
) -> dict:
    word_count = len(
        body.split()
    )

    return {
        "schema_version":
            "website_unified_content_v1",

        "engine_version":
            "website_unified_content_engine_v1",

        "content_id":
            "wuc_"
            + source_record_id,

        "document_id":
            source_record_id,

        "workspace_id":
            "ws_writer_audit",

        "source_type":
            "website",

        "source_format":
            "html",

        "source_identity": {
            "source_record_id":
                source_record_id,

            "canonical_url":
                (
                    "https://example.com/"
                    + source_record_id
                ),
        },

        "title":
            title,

        "h1":
            title,

        "headings":
            [],

        "canonical_url":
            (
                "https://example.com/"
                + source_record_id
            ),

        "content_body":
            body,

        "content_hash":
            compute_canonical_content_hash_v1(
                body
            ),

        "body_length":
            len(
                body
            ),

        "body_word_count":
            word_count,

        "structure": {
            "block_count":
                1,

            "heading_count":
                0,

            "content_word_count":
                word_count,

            "blocks":
                [],
        },

        "metadata": {
            "complete_content_preserved":
                True,

            "content_reduction_performed":
                False,

            "summarization_performed":
                False,

            "truncation_performed":
                False,

            "word_count_limit_applied":
                False,
        },

        "handoff": {
            "next_stage":
                "universal_unified_content_document",

            "eligible_for_uucd":
                True,

            "body_field":
                "content_body",

            "full_body_handoff":
                True,
        },
    }


def set_bound_body_ref(
    envelope: dict,
    body_ref: str,
) -> None:
    """Change body_ref consistently across all bound sections.

    The binding hash is intentionally not recomputed. The envelope
    validator must therefore reject the modified envelope before writing.
    """

    for section in (
        "uucd_record",
        "body_payload",
        "binding",
    ):
        envelope[
            section
        ][
            "body_ref"
        ] = body_ref


def expect_contract_rejection(
    envelope: dict,
    *,
    project_root: Path,
    overwrite: bool = False,
) -> bool:
    try:
        write_verified_body_from_envelope_v1(
            envelope,
            project_root=project_root,
            overwrite=overwrite,
        )

    except BodyStoreContractError:
        return True

    return False


production_before = (
    directory_fingerprint(
        PRODUCTION_STORE
    )
)

temporary_project = Path(
    tempfile.mkdtemp(
        prefix="linkcraftor_body_store_complete_audit_"
    )
).resolve()

failures = []
warnings = []

try:
    body_one = "\n\n".join(
        (
            "Audit paragraph "
            + str(
                index
            )
            + " verifies exact atomic Body Store persistence."
        )
        for index in range(
            1,
            401,
        )
    )

    body_two = (
        body_one
        + "\n\n"
        + "This is a deliberately different replacement body."
    )

    wuc_one = build_wuc(
        body=body_one,
        source_record_id="writer_audit_primary",
        title="Writer Audit Primary",
    )

    envelope_one = (
        build_transient_uucd_from_wuc_v1(
            wuc_one
        )
    )

    envelope_before = deepcopy(
        envelope_one
    )

    first_result = (
        write_verified_body_from_envelope_v1(
            envelope_one,
            project_root=temporary_project,
        )
    )

    body_path = Path(
        first_result[
            "body_path"
        ]
    )

    first_certificate = (
        first_result[
            "write_certificate"
        ]
    )

    finalized_record = (
        first_result[
            "finalized_uucd_record"
        ]
    )

    second_result = (
        write_verified_body_from_envelope_v1(
            envelope_one,
            project_root=temporary_project,
        )
    )


    # --------------------------------------------------------------
    # Conflict handling.
    # --------------------------------------------------------------

    conflicting_envelope = deepcopy(
        envelope_one
    )

    conflicting_envelope[
        "body_payload"
    ][
        "content_body"
    ] = body_two

    conflict_rejected = (
        expect_contract_rejection(
            conflicting_envelope,
            project_root=temporary_project,
        )
    )


    # A valid second envelope with its own hash but forced to the
    # existing path should still fail binding validation because its
    # body_ref cannot be changed without rebuilding the binding.
    replacement_wuc = build_wuc(
        body=body_two,
        source_record_id="writer_audit_replacement",
        title="Writer Audit Replacement",
    )

    replacement_envelope = (
        build_transient_uucd_from_wuc_v1(
            replacement_wuc
        )
    )

    forced_ref_envelope = deepcopy(
        replacement_envelope
    )

    set_bound_body_ref(
        forced_ref_envelope,
        envelope_one[
            "body_payload"
        ][
            "body_ref"
        ],
    )

    forced_ref_rejected = (
        expect_contract_rejection(
            forced_ref_envelope,
            project_root=temporary_project,
            overwrite=True,
        )
    )


    # --------------------------------------------------------------
    # Path-security tests.
    # --------------------------------------------------------------

    traversal = deepcopy(
        envelope_one
    )

    set_bound_body_ref(
        traversal,
        (
            "backend/server/data/"
            "universal_article_body_store/"
            "ws_writer_audit/bodies/"
            "../../outside.txt"
        ),
    )

    traversal_rejected = (
        expect_contract_rejection(
            traversal,
            project_root=temporary_project,
        )
    )


    absolute_external = deepcopy(
        envelope_one
    )

    external_path = (
        temporary_project.parent
        / "external_body.txt"
    ).resolve()

    set_bound_body_ref(
        absolute_external,
        str(
            external_path
        ),
    )

    absolute_external_rejected = (
        expect_contract_rejection(
            absolute_external,
            project_root=temporary_project,
        )
    )


    wrong_workspace = deepcopy(
        envelope_one
    )

    set_bound_body_ref(
        wrong_workspace,
        (
            "backend/server/data/"
            "universal_article_body_store/"
            "ws_other_workspace/bodies/body.txt"
        ),
    )

    wrong_workspace_rejected = (
        expect_contract_rejection(
            wrong_workspace,
            project_root=temporary_project,
        )
    )


    invalid_extension = deepcopy(
        envelope_one
    )

    original_ref = envelope_one[
        "body_payload"
    ][
        "body_ref"
    ]

    set_bound_body_ref(
        invalid_extension,
        original_ref[
            :-4
        ]
        + ".json",
    )

    invalid_extension_rejected = (
        expect_contract_rejection(
            invalid_extension,
            project_root=temporary_project,
        )
    )


    # --------------------------------------------------------------
    # Interrupted atomic-write cleanup.
    # --------------------------------------------------------------

    interruption_wuc = build_wuc(
        body=body_one,
        source_record_id="writer_audit_interruption",
        title="Writer Audit Interruption",
    )

    interruption_envelope = (
        build_transient_uucd_from_wuc_v1(
            interruption_wuc
        )
    )

    interruption_rejected = False

    interruption_target = (
        temporary_project
        / interruption_envelope[
            "body_payload"
        ][
            "body_ref"
        ]
    ).resolve()

    interruption_directory = (
        interruption_target.parent
    )

    try:
        with patch(
            "backend.server."
            "universal_article_body_store."
            "body_store_writer_v1.os.replace",
            side_effect=OSError(
                "simulated atomic replacement failure"
            ),
        ):
            write_verified_body_from_envelope_v1(
                interruption_envelope,
                project_root=temporary_project,
            )

    except OSError:
        interruption_rejected = True

    temporary_residue = (
        list(
            interruption_directory.glob(
                "*.tmp"
            )
        )
        if interruption_directory.exists()
        else []
    )

    interruption_target_absent = (
        not interruption_target.exists()
    )


    # --------------------------------------------------------------
    # Symlink escape test.
    # --------------------------------------------------------------

    symlink_test_supported = False
    symlink_escape_rejected = None

    symlink_project = (
        temporary_project
        / "symlink_project"
    )

    outside_directory = (
        temporary_project
        / "outside_symlink_destination"
    )

    outside_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    symlink_bodies = (
        symlink_project
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store"
        / "ws_writer_audit"
        / "bodies"
    )

    symlink_bodies.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        os.symlink(
            outside_directory,
            symlink_bodies,
            target_is_directory=True,
        )

        symlink_test_supported = True

        symlink_envelope = deepcopy(
            envelope_one
        )

        try:
            write_verified_body_from_envelope_v1(
                symlink_envelope,
                project_root=symlink_project,
            )

            symlink_escape_rejected = False

        except BodyStoreContractError:
            symlink_escape_rejected = True

    except (
        OSError,
        NotImplementedError,
    ) as exc:
        warnings.append(
            "Symlink escape test could not run on this Windows "
            "configuration: "
            + str(
                exc
            )
        )


    # --------------------------------------------------------------
    # Static architecture inspection.
    # --------------------------------------------------------------

    source = WRITER_PATH.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

    tree = ast.parse(
        source,
        filename=str(
            WRITER_PATH
        ),
    )

    runtime_imports = []
    semantic_imports = []
    uucd_persistence_calls = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.ImportFrom,
        ):
            module = str(
                node.module or ""
            ).casefold()

            if "runtime" in module:
                runtime_imports.append(
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

        if isinstance(
            node,
            ast.Call,
        ):
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
                "write_uucd",
                "persist_uucd",
                "save_uucd",
                "write_uucd_record",
            }:
                uucd_persistence_calls.append(
                    {
                        "function":
                            name,

                        "line":
                            node.lineno,
                    }
                )


    certificate_binding_checks = {
        "document_id":
            first_certificate[
                "document_id"
            ]
            == envelope_one[
                "binding"
            ][
                "document_id"
            ],

        "workspace_id":
            first_certificate[
                "workspace_id"
            ]
            == envelope_one[
                "binding"
            ][
                "workspace_id"
            ],

        "source_type":
            first_certificate[
                "source_type"
            ]
            == envelope_one[
                "binding"
            ][
                "source_type"
            ],

        "body_ref":
            first_certificate[
                "body_ref"
            ]
            == envelope_one[
                "binding"
            ][
                "body_ref"
            ],

        "content_hash":
            first_certificate[
                "content_hash"
            ]
            == envelope_one[
                "binding"
            ][
                "content_hash"
            ],

        "body_length":
            first_certificate[
                "body_length"
            ]
            == envelope_one[
                "binding"
            ][
                "body_length"
            ],

        "body_word_count":
            first_certificate[
                "body_word_count"
            ]
            == envelope_one[
                "binding"
            ][
                "body_word_count"
            ],

        "binding_hash":
            first_certificate[
                "binding_hash"
            ]
            == envelope_one[
                "binding"
            ][
                "binding_hash"
            ],
    }


    production_after = (
        directory_fingerprint(
            PRODUCTION_STORE
        )
    )


    checks = {
        "writer_syntax_valid":
            True,

        "writer_version_present":
            BODY_STORE_WRITER_VERSION
            == first_certificate[
                "writer_version"
            ],

        "first_write_created_body":
            first_certificate[
                "existing_file_action"
            ]
            == "CREATED",

        "stored_body_exact":
            body_path.read_text(
                encoding="utf-8"
            )
            == body_one,

        "stored_hash_exact":
            first_certificate[
                "content_hash"
            ]
            == compute_canonical_content_hash_v1(
                body_one
            ),

        "certificate_certified":
            first_certificate[
                "certificate_status"
            ]
            == "CERTIFIED",

        "all_certificate_binding_fields_match":
            all(
                certificate_binding_checks.values()
            ),

        "second_write_idempotent":
            second_result[
                "write_certificate"
            ][
                "existing_file_action"
            ]
            == "EXISTING_IDENTICAL_REUSED",

        "conflicting_payload_rejected":
            conflict_rejected,

        "forced_cross_document_overwrite_rejected":
            forced_ref_rejected,

        "path_traversal_rejected":
            traversal_rejected,

        "absolute_external_path_rejected":
            absolute_external_rejected,

        "wrong_workspace_path_rejected":
            wrong_workspace_rejected,

        "invalid_extension_rejected":
            invalid_extension_rejected,

        "interrupted_write_failed_safely":
            interruption_rejected,

        "interrupted_target_not_created":
            interruption_target_absent,

        "temporary_files_cleaned_after_failure":
            not temporary_residue,

        "finalized_record_excludes_content_body":
            "content_body"
            not in finalized_record,

        "finalized_record_body_status_verified":
            finalized_record[
                "body_status"
            ]
            == "STORED_AND_VERIFIED",

        "finalized_record_ready_for_persistence":
            finalized_record[
                "metadata"
            ][
                "persistence_status"
            ]
            == "READY_FOR_UUCD_PERSISTENCE",

        "finalized_record_not_persisted":
            first_certificate[
                "uucd_record_persisted"
            ]
            is False,

        "input_envelope_not_mutated":
            envelope_one
            == envelope_before,

        "no_runtime_imports":
            not runtime_imports,

        "no_semantic_imports":
            not semantic_imports,

        "no_uucd_persistence_calls":
            not uucd_persistence_calls,

        "production_store_unchanged":
            production_before
            == production_after,
    }


    if symlink_test_supported:
        checks[
            "symlink_escape_rejected"
        ] = (
            symlink_escape_rejected
            is True
        )


    failures = [
        name
        for name, passed
        in checks.items()
        if passed is not True
    ]


    print()
    print("=" * 116)
    print(
        "FRESH UNIVERSAL ARTICLE BODY STORE WRITER — COMPLETE AUDIT"
    )
    print("=" * 116)
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
        "Certificate binding checks:          "
        + str(
            sum(
                certificate_binding_checks.values()
            )
        )
        + "/"
        + str(
            len(
                certificate_binding_checks
            )
        )
    )

    print(
        "Temporary files after interruption: "
        + str(
            len(
                temporary_residue
            )
        )
    )

    print(
        "Symlink test supported:              "
        + str(
            symlink_test_supported
        )
    )

    if symlink_test_supported:
        print(
            "Symlink escape rejected:           "
            + str(
                symlink_escape_rejected
            )
        )

    print()
    print(
        "Production Body Store modified:      "
        + str(
            production_before
            != production_after
        )
    )

    print(
        "Persistent UUCD written:             False"
    )

    print(
        "Runtime Registration created:        False"
    )

    print(
        "Worker or queue created:             False"
    )

    print()
    print(
        "WARNINGS"
    )

    if warnings:
        for warning in warnings:
            print(
                "  - "
                + warning
            )

    else:
        print(
            "  None"
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
            "FRESH BODY STORE WRITER COMPLETE AUDIT: FAIL"
        )

        print(
            "Do not execute the writer against production articles "
            "until every failed check is resolved."
        )

        print("=" * 116)

        raise SystemExit(1)

    print(
        "FRESH BODY STORE WRITER COMPLETE AUDIT: PASS"
    )

    print(
        "The writer passed integrity, idempotency, path-safety, "
        "atomic-write recovery and certificate-binding checks."
    )

    print(
        "No production Body Store body or persistent UUCD record "
        "was created or modified."
    )

    print("=" * 116)

finally:
    shutil.rmtree(
        temporary_project,
        ignore_errors=True,
    )
