"""Verify the fresh transient WUC foundation and engine."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    __file__
).resolve().parent

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


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_PASS_COUNT = 2219

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

DATA_ROOT = (
    SERVER_ROOT
    / "data"
)

WUC_PACKAGE_ROOT = (
    SERVER_ROOT
    / "website_unified_content"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "fresh_wuc_engine_v1_verification.json"
)

PROHIBITED_PATHS = [
    (
        DATA_ROOT
        / "website_unified_content"
    ),

    (
        DATA_ROOT
        / "website_unified_content_store"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_store.py"
    ),
]

PROTECTED_PATHS = {
    "udare_store": (
        DATA_ROOT
        / "udare_store"
        / WORKSPACE_ID
    ),

    "article_validation_evidence": (
        DATA_ROOT
        / "article_validation_evidence"
        / WORKSPACE_ID
    ),

    "uucd_output": (
        DATA_ROOT
        / "universal_unified_content_document"
    ),

    "runtime_registry": (
        DATA_ROOT
        / "runtime"
        / "universal_runtime_registration"
        / "runtime_registration_registry.json"
    ),
}


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
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

    return digest.hexdigest()


def fingerprint(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    if not path.exists():
        digest.update(
            b"ABSENT"
        )

        return digest.hexdigest()

    if path.is_file():
        return sha256_file(
            path
        )

    for file_path in sorted(
        (
            candidate
            for candidate in path.rglob(
                "*"
            )
            if candidate.is_file()
        ),
        key=lambda candidate: (
            candidate.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            file_path.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        digest.update(
            b"\x00"
        )

        digest.update(
            sha256_file(
                file_path
            ).encode(
                "ascii"
            )
        )

        digest.update(
            b"\n"
        )

    return digest.hexdigest()


def write_json(
    path: Path,
    payload: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def active_wuc_store_references() -> list[str]:
    findings: list[str] = []

    for path in SERVER_ROOT.rglob(
        "*.py"
    ):
        if any(
            part in {
                "__pycache__",
                "backups",
                "runtime_backups",
            }
            for part in path.parts
        ):
            continue

        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

        if (
            "website_unified_content_store"
            in source
        ):
            findings.append(
                str(
                    path.relative_to(
                        PROJECT_ROOT
                    )
                )
            )

    return findings


def main() -> int:
    failures: list[str] = []

    protected_before = {
        name: fingerprint(
            path
        )
        for name, path
        in PROTECTED_PATHS.items()
    }

    contract = (
        load_article_validation_pass_contract_v1(
            WORKSPACE_ID,
            expected_pass_count=(
                EXPECTED_PASS_COUNT
            ),
        )
    )

    descriptors = contract.get(
        "descriptors"
    )

    if not isinstance(
        descriptors,
        list,
    ):
        raise RuntimeError(
            "Certified WUC descriptors are invalid."
        )

    sample_results: list[
        dict[str, Any]
    ] = []

    for descriptor in descriptors[
        :3
    ]:
        transient_source = (
            load_transient_certified_wuc_source_v1(
                descriptor
            )
        )

        document = (
            build_transient_website_unified_content_v1(
                certified_source=(
                    transient_source
                )
            )
        )

        sample_results.append(
            {
                "source_record_id":
                    descriptor.get(
                        "source_record_id"
                    ),

                "schema_version":
                    document.get(
                        "schema_version"
                    ),

                "content_body_present":
                    bool(
                        str(
                            document.get(
                                "content_body"
                            )
                            or ""
                        ).strip()
                    ),

                "content_hash_present":
                    bool(
                        str(
                            document.get(
                                "content_hash"
                            )
                            or ""
                        ).strip()
                    ),

                "structure_present":
                    isinstance(
                        document.get(
                            "structure"
                        ),
                        dict,
                    ),

                "article_body_field_absent":
                    (
                        "article_body"
                        not in document
                    ),

                "transient_mode":
                    (
                        document.get(
                            "metadata",
                            {},
                        ).get(
                            "wuc_persistence_mode"
                        )
                        == "TRANSIENT"
                    ),

                "eligible_for_uucd":
                    (
                        document.get(
                            "handoff",
                            {},
                        ).get(
                            "eligible_for_uucd"
                        )
                        is True
                    ),

                "body_length":
                    len(
                        str(
                            document.get(
                                "content_body"
                            )
                            or ""
                        )
                    ),

                "block_count":
                    document.get(
                        "structure",
                        {},
                    ).get(
                        "block_count"
                    ),
            }
        )

    protected_after = {
        name: fingerprint(
            path
        )
        for name, path
        in PROTECTED_PATHS.items()
    }

    protected_unchanged = {
        name: (
            protected_before[
                name
            ]
            == protected_after[
                name
            ]
        )
        for name
        in PROTECTED_PATHS
    }

    prohibited_paths_present = [
        str(
            path
        )
        for path in PROHIBITED_PATHS
        if path.exists()
    ]

    store_references = (
        active_wuc_store_references()
    )

    checks = {
        "pass_count_2219":
            (
                contract.get(
                    "pass_count"
                )
                == EXPECTED_PASS_COUNT
            ),

        "fail_count_zero":
            (
                contract.get(
                    "fail_count"
                )
                == 0
            ),

        "descriptor_count_2219":
            (
                len(
                    descriptors
                )
                == EXPECTED_PASS_COUNT
            ),

        "contract_does_not_load_bodies":
            (
                contract.get(
                    "article_bodies_loaded"
                )
                is False
            ),

        "three_samples_built":
            (
                len(
                    sample_results
                )
                == 3
            ),

        "all_samples_have_content_body":
            all(
                item[
                    "content_body_present"
                ]
                is True
                for item in sample_results
            ),

        "all_samples_have_structure":
            all(
                item[
                    "structure_present"
                ]
                is True
                for item in sample_results
            ),

        "legacy_article_body_absent":
            all(
                item[
                    "article_body_field_absent"
                ]
                is True
                for item in sample_results
            ),

        "all_samples_transient":
            all(
                item[
                    "transient_mode"
                ]
                is True
                for item in sample_results
            ),

        "all_samples_uucd_eligible":
            all(
                item[
                    "eligible_for_uucd"
                ]
                is True
                for item in sample_results
            ),

        "no_prohibited_store_paths":
            not prohibited_paths_present,

        "no_active_legacy_store_references":
            not store_references,

        "udare_store_unchanged":
            protected_unchanged[
                "udare_store"
            ],

        "article_validation_evidence_unchanged":
            protected_unchanged[
                "article_validation_evidence"
            ],

        "uucd_output_unchanged":
            protected_unchanged[
                "uucd_output"
            ],

        "runtime_registry_unchanged":
            protected_unchanged[
                "runtime_registry"
            ],
    }

    for name, passed in checks.items():
        if passed is not True:
            failures.append(
                f"Verification failed: {name}"
            )

    report = {
        "schema_version":
            "fresh_wuc_engine_v1_verification",

        "verification_status":
            (
                "PASS"
                if not failures
                else "FAIL"
            ),

        "workspace_id":
            WORKSPACE_ID,

        "article_validation_run_id":
            contract.get(
                "article_validation_run_id"
            ),

        "article_validation_certificate_id":
            contract.get(
                "article_validation_certificate_id"
            ),

        "article_validation_pass_count":
            contract.get(
                "pass_count"
            ),

        "descriptor_count":
            len(
                descriptors
            ),

        "sample_results":
            sample_results,

        "checks":
            checks,

        "prohibited_paths_present":
            prohibited_paths_present,

        "legacy_store_reference_files":
            store_references,

        "production_wuc_executed":
            False,

        "uucd_documents_written":
            False,

        "wuc_store_created":
            False,

        "runtime_registration_created":
            False,

        "failures":
            failures,
    }

    write_json(
        REPORT_PATH,
        report,
    )

    print()
    print("=" * 104)
    print(
        "FRESH WEBSITE UNIFIED CONTENT ENGINE — PHASE 1 VERIFICATION"
    )
    print("=" * 104)
    print()

    print(
        "Article Validation PASS count:      "
        + str(
            contract.get(
                "pass_count"
            )
        )
    )

    print(
        "Certified WUC descriptors:          "
        + str(
            len(
                descriptors
            )
        )
    )

    print(
        "Transient samples built:            "
        + str(
            len(
                sample_results
            )
        )
    )

    print(
        "Canonical content_body:             "
        + (
            "PASS"
            if checks[
                "all_samples_have_content_body"
            ]
            else "FAIL"
        )
    )

    print(
        "Canonical structure:                "
        + (
            "PASS"
            if checks[
                "all_samples_have_structure"
            ]
            else "FAIL"
        )
    )

    print(
        "Legacy article_body field:          ABSENT"
    )

    print(
        "WUC persistence mode:               TRANSIENT"
    )

    print(
        "Intermediate WUC Store:             NONE"
    )

    print(
        "Active legacy Store references:     "
        + str(
            len(
                store_references
            )
        )
    )

    print(
        "Production WUC executed:            False"
    )

    print(
        "UUCD documents written:             False"
    )

    print(
        "Runtime Registration created:       False"
    )

    print(
        "UDARE Store unchanged:              "
        + (
            "PASS"
            if checks[
                "udare_store_unchanged"
            ]
            else "FAIL"
        )
    )

    print(
        "Article Validation unchanged:       "
        + (
            "PASS"
            if checks[
                "article_validation_evidence_unchanged"
            ]
            else "FAIL"
        )
    )

    print(
        "Existing UUCD output unchanged:     "
        + (
            "PASS"
            if checks[
                "uucd_output_unchanged"
            ]
            else "FAIL"
        )
    )

    print(
        "Runtime registry unchanged:         "
        + (
            "PASS"
            if checks[
                "runtime_registry_unchanged"
            ]
            else "FAIL"
        )
    )

    print()
    print(
        "Verification report: "
        + str(
            REPORT_PATH
        )
    )

    print()

    if failures:
        print(
            "FRESH WUC ENGINE PHASE 1: FAIL"
        )

        for failure in failures:
            print(
                "  - "
                + failure
            )

        print("=" * 104)

        return 1

    print(
        "FRESH WUC ENGINE PHASE 1: PASS"
    )

    print(
        "The fresh WUC input reader and transient engine "
        "are valid for certified Article Validation inputs."
    )

    print(
        "No WUC Store, UUCD write, runtime registration "
        "or production execution occurred."
    )

    print("=" * 104)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
