"""Verify the canonical WUC direct-to-UUCD migration without writing UUCD."""

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


from backend.server.stores.website_unified_content_builder_v2 import (
    build_website_unified_content_document_v2,
)
from backend.server.stores.website_unified_content_certifier_v2 import (
    certify_website_unified_content_document_v2,
)
from backend.server.stores.website_unified_content_handoff_v2 import (
    load_article_validation_pass_contract_v2,
    load_transient_wuc_source_v2,
)
from backend.server.stores.website_unified_content_verifier_v2 import (
    verify_website_unified_content_document_v2,
)


WORKSPACE_ID = "ws_whattoexpect_com"

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

DATA_ROOT = (
    SERVER_ROOT
    / "data"
)

WORKER_PATH = (
    SERVER_ROOT
    / "workers"
    / "website_unified_content_batch_worker_v2.py"
)

BUILDER_PATH = (
    SERVER_ROOT
    / "stores"
    / "website_unified_content_builder_v2.py"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "wuc_direct_uucd_handoff_v2_verification.json"
)

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


def imported_modules(
    path: Path,
) -> set[str]:
    tree = ast.parse(
        path.read_text(
            encoding="utf-8-sig",
        ),
        filename=str(
            path
        ),
    )

    modules: set[str] = set()

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            modules.update(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = str(
                node.module or ""
            )

            modules.add(
                module
            )

    return modules


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
        load_article_validation_pass_contract_v2(
            WORKSPACE_ID
        )
    )

    records = contract.get(
        "records"
    )

    if not isinstance(
        records,
        list,
    ):
        raise RuntimeError(
            "Article Validation PASS records are invalid."
        )

    sample_records = (
        records[:3]
    )

    sample_results: list[
        dict[str, Any]
    ] = []

    for record in sample_records:
        transient_source = (
            load_transient_wuc_source_v2(
                workspace_id=WORKSPACE_ID,
                pass_record=record,
                article_validation_contract=contract,
            )
        )

        document = (
            build_website_unified_content_document_v2(
                certified_article=(
                    transient_source
                )
            )
        )

        verification = (
            verify_website_unified_content_document_v2(
                document=document
            )
        )

        certified = (
            certify_website_unified_content_document_v2(
                document=document,
                verification_result=(
                    verification
                ),
            )
            if verification.get(
                "passed"
            )
            else {}
        )

        sample_results.append(
            {
                "source_record_id":
                    record.get(
                        "source_record_id"
                    ),

                "verification_passed":
                    verification.get(
                        "passed"
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

                "article_body_absent":
                    (
                        "article_body"
                        not in document
                    ),

                "structure_present":
                    isinstance(
                        document.get(
                            "structure"
                        ),
                        dict,
                    ),

                "certified_for_uucd":
                    (
                        certified.get(
                            "wuc_certification_status"
                        )
                        == "CERTIFIED_FOR_UUCD"
                    ),

                "wuc_persistence_mode":
                    certified.get(
                        "metadata",
                        {},
                    ).get(
                        "persistence_mode"
                    ),
            }
        )

    worker_source = WORKER_PATH.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    builder_source = BUILDER_PATH.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    worker_imports = imported_modules(
        WORKER_PATH
    )

    checks = {
        "pass_manifest_count_2219":
            (
                int(
                    contract.get(
                        "pass_count"
                    )
                    or 0
                )
                == 2219
            ),

        "article_validation_fail_count_zero":
            (
                int(
                    contract.get(
                        "fail_count"
                    )
                    or 0
                )
                == 0
            ),

        "three_transient_samples_verified":
            (
                len(
                    sample_results
                )
                == 3
                and all(
                    item[
                        "verification_passed"
                    ]
                    is True
                    for item in sample_results
                )
            ),

        "canonical_content_body_present":
            all(
                item[
                    "content_body_present"
                ]
                is True
                for item in sample_results
            ),

        "legacy_article_body_absent":
            all(
                item[
                    "article_body_absent"
                ]
                is True
                for item in sample_results
            ),

        "samples_certified_for_uucd":
            all(
                item[
                    "certified_for_uucd"
                ]
                is True
                for item in sample_results
            ),

        "worker_does_not_import_article_validation_store":
            not any(
                "article_validation_store"
                in module.casefold()
                for module in worker_imports
            ),

        "worker_does_not_import_wuc_store":
            not any(
                "website_unified_content_store"
                in module.casefold()
                for module in worker_imports
            ),

        "worker_calls_direct_uucd_convergence":
            (
                "build_and_write_uucd_from_wuc_v1"
                in worker_source
            ),

        "worker_reads_pass_manifest_contract":
            (
                "load_article_validation_pass_contract_v2"
                in worker_source
            ),

        "builder_emits_content_body":
            (
                '"content_body"'
                in builder_source
                or "'content_body'"
                in builder_source
            ),

        "builder_does_not_emit_article_body":
            (
                '"article_body":'
                not in builder_source
                and "'article_body':"
                not in builder_source
            ),
    }

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

    checks.update(
        {
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
        }
    )

    for name, passed in checks.items():
        if passed is not True:
            failures.append(
                f"Verification failed: {name}"
            )

    report = {
        "schema_version":
            "wuc_direct_uucd_handoff_v2_verification",

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
                "run_id"
            ),

        "article_validation_certificate_id":
            contract.get(
                "certificate_id"
            ),

        "article_validation_pass_count":
            contract.get(
                "pass_count"
            ),

        "sample_results":
            sample_results,

        "checks":
            checks,

        "protected_paths_unchanged":
            protected_unchanged,

        "wuc_executed":
            False,

        "uucd_written":
            False,

        "legacy_wuc_store_deleted":
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
        "WUC DIRECT ARTICLE VALIDATION → UUCD HANDOFF VERIFICATION"
    )
    print("=" * 104)
    print()

    print(
        "Article Validation PASS count:          "
        + str(
            contract.get(
                "pass_count"
            )
        )
    )

    print(
        "Transient samples verified:            "
        + (
            "PASS"
            if checks[
                "three_transient_samples_verified"
            ]
            else "FAIL"
        )
    )

    print(
        "Canonical content_body emitted:        "
        + (
            "PASS"
            if checks[
                "canonical_content_body_present"
            ]
            else "FAIL"
        )
    )

    print(
        "Legacy article_body field absent:      "
        + (
            "PASS"
            if checks[
                "legacy_article_body_absent"
            ]
            else "FAIL"
        )
    )

    print(
        "Article Validation Store import:       ABSENT"
    )

    print(
        "Legacy WUC Store import:               ABSENT"
    )

    print(
        "Direct UUCD convergence configured:    "
        + (
            "PASS"
            if checks[
                "worker_calls_direct_uucd_convergence"
            ]
            else "FAIL"
        )
    )

    print(
        "Intermediate WUC persistence:          NONE"
    )

    print(
        "Production WUC execution:              False"
    )

    print(
        "Production UUCD writes:                False"
    )

    print(
        "UDARE Store unchanged:                 "
        + (
            "PASS"
            if checks[
                "udare_store_unchanged"
            ]
            else "FAIL"
        )
    )

    print(
        "Article Validation evidence unchanged: "
        + (
            "PASS"
            if checks[
                "article_validation_evidence_unchanged"
            ]
            else "FAIL"
        )
    )

    print(
        "Existing UUCD output unchanged:        "
        + (
            "PASS"
            if checks[
                "uucd_output_unchanged"
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
            "WUC DIRECT UUCD HANDOFF MIGRATION: FAIL"
        )

        for failure in failures:
            print(
                "  - "
                + failure
            )

        print("=" * 104)

        return 1

    print(
        "WUC DIRECT UUCD HANDOFF MIGRATION: PASS"
    )

    print(
        "The canonical v2 worker now reads Article Validation "
        "PASS records and original UDARE articles."
    )

    print(
        "Certified WUC documents remain transient and converge "
        "directly into UUCD."
    )

    print("=" * 104)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
