"""Verify the metadata-only Article Validation Store v3."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.article_validation.article_validation_store_v3 import (
    append_article_validation_results_v3,
    article_validation_store_paths_v3,
    finalize_article_validation_store_v3,
    initialize_article_validation_store_v3,
    load_article_validation_store_v3,
)


PRODUCTION_WORKSPACE_ID = (
    "ws_whattoexpect_com"
)

TEST_WORKSPACE_ID = (
    "ws_article_validation_store_v3_test"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "article_validation_scan"
    / PRODUCTION_WORKSPACE_ID
    / "article_validation_store_v3_verification.json"
)

PROHIBITED_FIELDS = {
    "article_body",
    "article_html",
    "content_body",
    "cleaned_article_text",
    "body_text",
    "raw_html",
}


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def directory_fingerprint(
    root: Path,
) -> str:
    digest = hashlib.sha256()

    if not root.exists():
        digest.update(
            b"ABSENT"
        )

        return digest.hexdigest()

    for path in sorted(
        (
            candidate
            for candidate in root.rglob("*")
            if candidate.is_file()
        ),
        key=lambda candidate: (
            candidate.as_posix()
        ),
    ):
        digest.update(
            path.relative_to(
                root
            ).as_posix().encode(
                "utf-8"
            )
        )

        digest.update(
            sha256_file(
                path
            ).encode(
                "ascii"
            )
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


def result_record(
    source_record_id: str,
    *,
    passed: bool,
) -> dict[str, Any]:
    return {
        "source_record_id":
            source_record_id,

        "source_url":
            (
                "https://example.com/"
                + source_record_id
            ),

        "status":
            (
                "PASS"
                if passed
                else "FAIL"
            ),

        "passed":
            passed,

        "validation_version":
            "article_validation_engine_v3_test",

        "integrity_certificate_id":
            "integrity_certificate_test",

        "article_sha256":
            "a" * 64,

        "metadata_sha256":
            "b" * 64,

        "validation_score":
            (
                100.0
                if passed
                else 80.0
            ),

        "quality_grade":
            (
                "A+"
                if passed
                else "B"
            ),

        "checks":
            {
                "test_check":
                    passed,
            },

        "statistics":
            {
                "word_count":
                    500,
            },

        "warnings":
            (
                []
                if passed
                else [
                    "TEST_WARNING"
                ]
            ),

        "errors":
            [],

        "rejection_reasons":
            (
                []
                if passed
                else [
                    "TEST_REJECTION"
                ]
            ),

        "eligible_for_wuc":
            passed,

        "eligible_for_unified_content_document":
            passed,

        "article_body_included":
            False,

        "article_body_modified":
            False,
    }


def recursive_field_names(
    value: Any,
) -> set[str]:
    names: set[str] = set()

    if isinstance(
        value,
        dict,
    ):
        for key, item in value.items():
            names.add(
                str(key).casefold()
            )

            names.update(
                recursive_field_names(
                    item
                )
            )

    elif isinstance(
        value,
        list,
    ):
        for item in value:
            names.update(
                recursive_field_names(
                    item
                )
            )

    return names


def main(
) -> int:
    print()
    print("=" * 96)
    print(
        "ARTICLE VALIDATION STORE V3 — TARGETED VERIFICATION"
    )
    print("=" * 96)

    failures: list[str] = []

    production_paths = (
        article_validation_store_paths_v3(
            PRODUCTION_WORKSPACE_ID
        )
    )

    test_paths = (
        article_validation_store_paths_v3(
            TEST_WORKSPACE_ID
        )
    )

    production_before = (
        directory_fingerprint(
            production_paths[
                "root"
            ]
        )
    )

    if test_paths[
        "root"
    ].exists():
        shutil.rmtree(
            test_paths[
                "root"
            ]
        )

    try:
        initialize_article_validation_store_v3(
            workspace_id=(
                TEST_WORKSPACE_ID
            ),
            run_id="test_run_v3",
            integrity_certificate_id=(
                "integrity_certificate_test"
            ),
            expected_input_count=3,
        )

        append_article_validation_results_v3(
            workspace_id=(
                TEST_WORKSPACE_ID
            ),
            run_id="test_run_v3",
            results=[
                result_record(
                    "record_1",
                    passed=True,
                ),
                result_record(
                    "record_2",
                    passed=True,
                ),
            ],
            expected_previous_count=0,
        )

        append_article_validation_results_v3(
            workspace_id=(
                TEST_WORKSPACE_ID
            ),
            run_id="test_run_v3",
            results=[
                result_record(
                    "record_3",
                    passed=False,
                ),
            ],
            expected_previous_count=2,
        )

        duplicate_rejected = False

        try:
            append_article_validation_results_v3(
                workspace_id=(
                    TEST_WORKSPACE_ID
                ),
                run_id="test_run_v3",
                results=[
                    result_record(
                        "record_1",
                        passed=True,
                    ),
                ],
            )

        except RuntimeError:
            duplicate_rejected = True

        if not duplicate_rejected:
            failures.append(
                "Duplicate source_record_id was not rejected."
            )

        body_record = result_record(
            "record_body",
            passed=True,
        )

        body_record[
            "article_body"
        ] = "This must never be stored."

        body_field_rejected = False

        try:
            append_article_validation_results_v3(
                workspace_id=(
                    TEST_WORKSPACE_ID
                ),
                run_id="test_run_v3",
                results=[
                    body_record
                ],
            )

        except ValueError:
            body_field_rejected = True

        if not body_field_rejected:
            failures.append(
                "Article-body field was not rejected."
            )

        final_report = (
            finalize_article_validation_store_v3(
                workspace_id=(
                    TEST_WORKSPACE_ID
                ),
                run_id="test_run_v3",
            )
        )

        loaded = (
            load_article_validation_store_v3(
                TEST_WORKSPACE_ID
            )
        )

        if loaded.get(
            "article_count"
        ) != 3:
            failures.append(
                "Stored result count was not 3."
            )

        if final_report.get(
            "pass_count"
        ) != 2:
            failures.append(
                "Final pass count was not 2."
            )

        if final_report.get(
            "fail_count"
        ) != 1:
            failures.append(
                "Final fail count was not 1."
            )

        if final_report.get(
            "eligible_for_wuc_count"
        ) != 2:
            failures.append(
                "WUC eligibility count was not 2."
            )

        if loaded.get(
            "article_bodies_stored"
        ) is not False:
            failures.append(
                "Store reported article bodies as stored."
            )

        stored_field_names = (
            recursive_field_names(
                loaded
            )
        )

        prohibited_present = sorted(
            stored_field_names
            & PROHIBITED_FIELDS
        )

        if prohibited_present:
            failures.append(
                "Stored payload contained prohibited fields: "
                + ", ".join(
                    prohibited_present
                )
            )

        ledger_status = str(
            loaded.get(
                "ledger",
                {},
            ).get(
                "status"
            )
            or ""
        )

        if ledger_status != "COMPLETED":
            failures.append(
                "Final ledger status was not COMPLETED."
            )

    finally:
        if test_paths[
            "root"
        ].exists():
            shutil.rmtree(
                test_paths[
                    "root"
                ]
            )

    production_after = (
        directory_fingerprint(
            production_paths[
                "root"
            ]
        )
    )

    production_unchanged = (
        production_before
        == production_after
    )

    if not production_unchanged:
        failures.append(
            "Production Article Validation store changed."
        )

    test_store_cleaned = (
        not test_paths[
            "root"
        ].exists()
    )

    if not test_store_cleaned:
        failures.append(
            "Temporary verification store was not removed."
        )

    report = {
        "schema_version":
            "article_validation_store_v3_verification_v1",

        "verification_status":
            (
                "PASS"
                if not failures
                else "FAIL"
            ),

        "production_workspace_id":
            PRODUCTION_WORKSPACE_ID,

        "full_population_validation_executed":
            False,

        "synthetic_results_stored":
            3,

        "synthetic_pass_count":
            2,

        "synthetic_fail_count":
            1,

        "duplicate_rejected":
            duplicate_rejected,

        "article_body_field_rejected":
            body_field_rejected,

        "production_store_unchanged":
            production_unchanged,

        "temporary_store_cleaned":
            test_store_cleaned,

        "failures":
            failures,
    }

    write_json(
        REPORT_PATH,
        report,
    )

    print()
    print(
        "Synthetic metadata results stored: 3"
    )

    print(
        "Synthetic PASS results:            2"
    )

    print(
        "Synthetic FAIL results:            1"
    )

    print(
        "Duplicate identifiers rejected:    "
        + (
            "PASS"
            if duplicate_rejected
            else "FAIL"
        )
    )

    print(
        "Article-body fields rejected:      "
        + (
            "PASS"
            if body_field_rejected
            else "FAIL"
        )
    )

    print(
        "Production store unchanged:        "
        + (
            "PASS"
            if production_unchanged
            else "FAIL"
        )
    )

    print(
        "Temporary test store removed:      "
        + (
            "PASS"
            if test_store_cleaned
            else "FAIL"
        )
    )

    print(
        "Full 2,219 validation executed:    False"
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
            "ARTICLE VALIDATION STORE V3 "
            "VERIFICATION: FAIL"
        )

        for failure in failures:
            print(
                "  - "
                + failure
            )

        print("=" * 96)

        return 1

    print(
        "ARTICLE VALIDATION STORE V3 "
        "VERIFICATION: PASS"
    )

    print(
        "The store accepts metadata-only validation "
        "results and rejects article-body content."
    )

    print(
        "No production Article Validation results "
        "were created."
    )

    print("=" * 96)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
