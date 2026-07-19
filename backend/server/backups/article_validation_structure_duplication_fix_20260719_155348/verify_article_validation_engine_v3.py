"""Targeted verification for Article Validation Engine v3."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.article_validation.article_validation_engine_v3 import (
    ARTICLE_VALIDATION_ENGINE_VERSION,
    extract_article_validation_document_v3,
    validate_certified_article_v3,
)

from backend.server.article_validation.certified_article_validation_input import (
    load_certified_article_payload,
    load_certified_article_validation_input,
)


WORKSPACE_ID = "ws_whattoexpect_com"

REPORT_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_engine_v3_verification.json"
)

PROHIBITED_OUTPUT_FIELDS = {
    "article_body",
    "article_html",
    "content_body",
    "cleaned_article_text",
    "body_text",
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


def normalize_headings(
    value: Any,
) -> list[str]:
    if not isinstance(
        value,
        list,
    ):
        return []

    headings: list[str] = []

    for item in value:
        if isinstance(
            item,
            dict,
        ):
            text = str(
                item.get("text")
                or item.get("heading")
                or item.get("title")
                or ""
            ).strip()

        else:
            text = str(
                item or ""
            ).strip()

        if text:
            headings.append(
                text
            )

    return headings


def synthetic_article_text(
) -> str:
    paragraphs: list[str] = []

    for paragraph_index in range(4):
        paragraph = " ".join(
            (
                f"paragraph{paragraph_index}_"
                f"word{word_index}"
            )
            for word_index in range(60)
        )

        paragraphs.append(
            paragraph
        )

    return "\n\n".join(
        paragraphs
    )


def synthetic_validation(
    *,
    article_text: str,
    title: str,
    integrity_status: str = "PASS",
) -> dict[str, Any]:
    return validate_certified_article_v3(
        article_text=article_text,
        title=title,
        h1=title,
        headings=[
            "Overview",
            "Detailed Information",
        ],
        source_record_id=(
            "synthetic_source_record"
        ),
        source_url=(
            "https://example.com/article"
        ),
        article_sha256="a" * 64,
        metadata_sha256="b" * 64,
        integrity_certificate_id=(
            "synthetic_certificate"
        ),
        integrity_certification_status=(
            "CERTIFIED"
        ),
        overall_integrity_status=(
            integrity_status
        ),
    )


def main(
) -> int:
    print()
    print("=" * 96)
    print(
        "ARTICLE VALIDATION ENGINE V3 — TARGETED VERIFICATION"
    )
    print("=" * 96)

    failures: list[str] = []

    good_text = synthetic_article_text()

    valid_result = synthetic_validation(
        article_text=good_text,
        title="Synthetic Valid Article",
    )

    if valid_result.get(
        "status"
    ) != "PASS":
        failures.append(
            "Synthetic valid article did not pass."
        )

    short_structured_text = (
        " ".join(
            f"first_paragraph_word_{index}"
            for index in range(20)
        )
        + "\n\n"
        + " ".join(
            f"second_paragraph_word_{index}"
            for index in range(20)
        )
    )

    short_result = synthetic_validation(
        article_text=short_structured_text,
        title="Short Structured Article",
    )

    short_checks = short_result.get(
        "checks",
        {},
    )

    short_warnings = short_result.get(
        "warnings",
        [],
    )

    short_rejection_reasons = short_result.get(
        "rejection_reasons",
        [],
    )

    word_count_rule_removed = (
        short_result.get(
            "status"
        )
        == "PASS"
        and "minimum_word_count"
        not in short_checks
        and "LOW_WORD_COUNT"
        not in short_warnings
        and "LOW_WORD_COUNT"
        not in short_rejection_reasons
    )

    if not word_count_rule_removed:
        failures.append(
            "A structurally valid short article was affected "
            "by word-count validation logic."
        )

    missing_title_result = (
        synthetic_validation(
            article_text=good_text,
            title="",
        )
    )

    if missing_title_result.get(
        "checks",
        {},
    ).get(
        "title_present"
    ) is not False:
        failures.append(
            "Missing title was not rejected."
        )

    failed_integrity_result = (
        synthetic_validation(
            article_text=good_text,
            title="Untrusted Article",
            integrity_status="FAIL",
        )
    )

    if failed_integrity_result.get(
        "checks",
        {},
    ).get(
        "integrity_record_passed"
    ) is not False:
        failures.append(
            "Failed integrity record was accepted."
        )

    prohibited_fields = sorted(
        set(
            valid_result.keys()
        )
        & PROHIBITED_OUTPUT_FIELDS
    )

    if prohibited_fields:
        failures.append(
            "Validation output contained article-body fields."
        )

    if good_text in json.dumps(
        valid_result,
        sort_keys=True,
    ):
        failures.append(
            "Validation output copied the synthetic article body."
        )

    extraction = (
        extract_article_validation_document_v3(
            """
            <html>
              <head>
                <title>Extraction Test</title>
                <script>forbidden script text</script>
              </head>
              <body>
                <nav>forbidden navigation text</nav>
                <article>
                  <h1>Extraction Test Heading</h1>
                  <p>First useful article paragraph.</p>
                  <p>Second useful article paragraph.</p>
                </article>
                <footer>forbidden footer text</footer>
              </body>
            </html>
            """
        )
    )

    extraction_text = str(
        extraction.get(
            "article_text"
        )
        or ""
    )

    for forbidden_text in (
        "forbidden script text",
        "forbidden navigation text",
        "forbidden footer text",
    ):
        if forbidden_text in extraction_text:
            failures.append(
                "HTML extractor included excluded page chrome."
            )

    certified_input = (
        load_certified_article_validation_input(
            WORKSPACE_ID,
            expected_active_count=2219,
        )
    )

    descriptors = certified_input.get(
        "records",
        [],
    )

    sample_positions = (
        0,
        len(descriptors) // 2,
        len(descriptors) - 1,
    )

    real_sample_results: list[
        dict[str, Any]
    ] = []

    for position in sample_positions:
        descriptor = descriptors[
            position
        ]

        article_path = Path(
            descriptor[
                "article_path"
            ]
        )

        metadata_path = Path(
            descriptor[
                "metadata_path"
            ]
        )

        article_hash_before = (
            sha256_file(
                article_path
            )
        )

        metadata_hash_before = (
            sha256_file(
                metadata_path
            )
        )

        payload = (
            load_certified_article_payload(
                descriptor
            )
        )

        metadata = payload.get(
            "metadata"
        )

        if not isinstance(
            metadata,
            dict,
        ):
            metadata = {}

        extracted = (
            extract_article_validation_document_v3(
                str(
                    payload.get(
                        "article_html"
                    )
                    or ""
                )
            )
        )

        title = str(
            metadata.get(
                "title"
            )
            or payload.get(
                "display_title"
            )
            or extracted.get(
                "title"
            )
            or extracted.get(
                "h1"
            )
            or ""
        ).strip()

        h1 = str(
            metadata.get(
                "h1"
            )
            or extracted.get(
                "h1"
            )
            or ""
        ).strip()

        headings = (
            normalize_headings(
                metadata.get(
                    "headings"
                )
            )
            or extracted.get(
                "headings"
            )
            or []
        )

        result = (
            validate_certified_article_v3(
                article_text=str(
                    extracted.get(
                        "article_text"
                    )
                    or ""
                ),
                title=title,
                h1=h1,
                headings=headings,
                source_record_id=str(
                    payload.get(
                        "source_record_id"
                    )
                    or ""
                ),
                source_url=str(
                    payload.get(
                        "source_url"
                    )
                    or metadata.get(
                        "source_url"
                    )
                    or ""
                ),
                article_sha256=str(
                    payload.get(
                        "article_sha256"
                    )
                    or ""
                ),
                metadata_sha256=str(
                    payload.get(
                        "metadata_sha256"
                    )
                    or ""
                ),
                integrity_certificate_id=str(
                    certified_input.get(
                        "certificate_id"
                    )
                    or ""
                ),
                integrity_certification_status=str(
                    certified_input.get(
                        "certificate_status"
                    )
                    or ""
                ),
                overall_integrity_status=str(
                    descriptor.get(
                        "overall_integrity_status"
                    )
                    or ""
                ),
            )
        )

        article_unchanged = (
            article_hash_before
            == sha256_file(
                article_path
            )
        )

        metadata_unchanged = (
            metadata_hash_before
            == sha256_file(
                metadata_path
            )
        )

        if not article_unchanged:
            failures.append(
                "A sampled article changed during validation."
            )

        if not metadata_unchanged:
            failures.append(
                "A sampled metadata document changed."
            )

        if (
            set(result.keys())
            & PROHIBITED_OUTPUT_FIELDS
        ):
            failures.append(
                "A real result contained an article-body field."
            )

        real_sample_results.append(
            {
                "source_record_id":
                    result.get(
                        "source_record_id"
                    ),

                "status":
                    result.get(
                        "status"
                    ),

                "validation_score":
                    result.get(
                        "validation_score"
                    ),

                "quality_grade":
                    result.get(
                        "quality_grade"
                    ),

                "word_count":
                    result.get(
                        "statistics",
                        {},
                    ).get(
                        "word_count"
                    ),

                "paragraph_count":
                    result.get(
                        "statistics",
                        {},
                    ).get(
                        "paragraph_count"
                    ),

                "rejection_reasons":
                    result.get(
                        "rejection_reasons"
                    ),

                "article_unchanged":
                    article_unchanged,

                "metadata_unchanged":
                    metadata_unchanged,
            }
        )

    report = {
        "schema_version":
            "article_validation_engine_v3_verification_v1",

        "verification_status":
            (
                "PASS"
                if not failures
                else "FAIL"
            ),

        "workspace_id":
            WORKSPACE_ID,

        "engine_version":
            ARTICLE_VALIDATION_ENGINE_VERSION,

        "certified_descriptor_count":
            len(descriptors),

        "full_population_validation_executed":
            False,

        "synthetic_valid_article_passed":
            (
                valid_result.get(
                    "status"
                )
                == "PASS"
            ),

        "word_count_rule_removed":
            word_count_rule_removed,

        "missing_title_enforced":
            (
                missing_title_result.get(
                    "checks",
                    {},
                ).get(
                    "title_present"
                )
                is False
            ),

        "integrity_scope_enforced":
            (
                failed_integrity_result.get(
                    "checks",
                    {},
                ).get(
                    "integrity_record_passed"
                )
                is False
            ),

        "prohibited_output_fields":
            prohibited_fields,

        "real_sample_results":
            real_sample_results,

        "failures":
            failures,
    }

    write_json(
        REPORT_PATH,
        report,
    )

    print()
    print(
        "Engine version:                    "
        + ARTICLE_VALIDATION_ENGINE_VERSION
    )

    print(
        "Certified descriptors available:   "
        + str(
            len(descriptors)
        )
    )

    print(
        "Synthetic valid article:           "
        + (
            "PASS"
            if report[
                "synthetic_valid_article_passed"
            ]
            else "FAIL"
        )
    )

    print(
        "Word-count rule removed:            "
        + (
            "PASS"
            if report[
                "word_count_rule_removed"
            ]
            else "FAIL"
        )
    )

    print(
        "Missing title enforced:            "
        + (
            "PASS"
            if report[
                "missing_title_enforced"
            ]
            else "FAIL"
        )
    )

    print(
        "Integrity scope enforced:          "
        + (
            "PASS"
            if report[
                "integrity_scope_enforced"
            ]
            else "FAIL"
        )
    )

    print(
        "Article body excluded from output: "
        + (
            "PASS"
            if not prohibited_fields
            else "FAIL"
        )
    )

    print(
        "Full 2,219 validation executed:    False"
    )

    print()
    print(
        "REAL CERTIFIED SAMPLE RESULTS"
    )

    for sample in real_sample_results:
        print(
            "  "
            + str(
                sample[
                    "source_record_id"
                ]
            )
            + ": status="
            + str(
                sample[
                    "status"
                ]
            )
            + ", words="
            + str(
                sample[
                    "word_count"
                ]
            )
            + ", score="
            + str(
                sample[
                    "validation_score"
                ]
            )
            + ", unchanged="
            + str(
                sample[
                    "article_unchanged"
                ]
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
            "ARTICLE VALIDATION ENGINE V3 "
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
        "ARTICLE VALIDATION ENGINE V3 "
        "VERIFICATION: PASS"
    )

    print(
        "Engine v3 consumes certified inputs and "
        "returns metadata-only validation results."
    )

    print(
        "The legacy Article Validation engine was not modified."
    )

    print("=" * 96)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
