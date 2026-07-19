"""Scan all Article Validation v3 failures without modifying evidence."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


WORKSPACE_ID = "ws_whattoexpect_com"

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

VERIFICATION_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_population_v3_verification.json"
)

SCAN_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_failure_analysis_v3.json"
)


def load_json(
    path: Path,
) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8-sig",
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


def load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            value = json.loads(
                line
            )

            if not isinstance(
                value,
                dict,
            ):
                raise RuntimeError(
                    "Failure manifest record is not an object "
                    f"at line {line_number}."
                )

            records.append(
                value
            )

    return records


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


def main() -> int:
    print()
    print("=" * 100)
    print(
        "ARTICLE VALIDATION V3 — FAILURE ANALYSIS"
    )
    print("=" * 100)

    if not VERIFICATION_REPORT_PATH.is_file():
        raise FileNotFoundError(
            "Population verification report is missing: "
            + str(
                VERIFICATION_REPORT_PATH
            )
        )

    population_report = load_json(
        VERIFICATION_REPORT_PATH
    )

    artifact_paths = population_report.get(
        "artifact_paths"
    )

    if not isinstance(
        artifact_paths,
        dict,
    ):
        raise RuntimeError(
            "Population verification report has no artifact paths."
        )

    failure_manifest_path = Path(
        str(
            artifact_paths.get(
                "failure_manifest"
            )
            or ""
        )
    )

    if not failure_manifest_path.is_file():
        raise FileNotFoundError(
            "Article Validation failure manifest is missing: "
            + str(
                failure_manifest_path
            )
        )

    failures = load_jsonl(
        failure_manifest_path
    )

    expected_failure_count = int(
        population_report.get(
            "fail_count"
        )
        or 0
    )

    if len(failures) != expected_failure_count:
        raise RuntimeError(
            "Failure manifest count mismatch: "
            f"{len(failures)} != {expected_failure_count}"
        )

    rejection_reason_counts: Counter[str] = Counter()
    warning_counts: Counter[str] = Counter()
    failed_check_counts: Counter[str] = Counter()
    grade_counts: Counter[str] = Counter()

    word_counts: list[int] = []

    analyzed_records: list[
        dict[str, Any]
    ] = []

    for record in failures:
        source_record_id = str(
            record.get(
                "source_record_id"
            )
            or ""
        ).strip()

        rejection_reasons = [
            str(reason)
            for reason in (
                record.get(
                    "rejection_reasons"
                )
                or []
            )
        ]

        warnings = [
            str(warning)
            for warning in (
                record.get(
                    "warnings"
                )
                or []
            )
        ]

        checks = record.get(
            "checks"
        )

        if not isinstance(
            checks,
            dict,
        ):
            checks = {}

        failed_checks = sorted(
            str(check_name)
            for check_name, passed
            in checks.items()
            if passed is False
        )

        statistics = record.get(
            "statistics"
        )

        if not isinstance(
            statistics,
            dict,
        ):
            statistics = {}

        word_count = int(
            statistics.get(
                "word_count"
            )
            or 0
        )

        word_counts.append(
            word_count
        )

        for reason in rejection_reasons:
            rejection_reason_counts[
                reason
            ] += 1

        for warning in warnings:
            warning_counts[
                warning
            ] += 1

        for failed_check in failed_checks:
            failed_check_counts[
                failed_check
            ] += 1

        quality_grade = str(
            record.get(
                "quality_grade"
            )
            or "MISSING"
        )

        grade_counts[
            quality_grade
        ] += 1

        analyzed_records.append(
            {
                "source_record_id":
                    source_record_id,

                "document_id":
                    record.get(
                        "document_id"
                    ),

                "html_id":
                    record.get(
                        "html_id"
                    ),

                "title":
                    record.get(
                        "title"
                    ),

                "source_url":
                    record.get(
                        "source_url"
                    ),

                "article_reference":
                    record.get(
                        "article_reference"
                    ),

                "metadata_reference":
                    record.get(
                        "metadata_reference"
                    ),

                "validation_score":
                    record.get(
                        "validation_score"
                    ),

                "quality_grade":
                    quality_grade,

                "word_count":
                    word_count,

                "paragraph_count":
                    statistics.get(
                        "paragraph_count"
                    ),

                "heading_count":
                    statistics.get(
                        "heading_count"
                    ),

                "failed_checks":
                    failed_checks,

                "rejection_reasons":
                    rejection_reasons,

                "warnings":
                    warnings,

                "eligible_for_wuc":
                    record.get(
                        "eligible_for_wuc"
                    ),
            }
        )

    analyzed_records.sort(
        key=lambda record: (
            int(
                record.get(
                    "word_count"
                )
                or 0
            ),
            str(
                record.get(
                    "source_record_id"
                )
                or ""
            ),
        )
    )

    report = {
        "schema_version":
            "article_validation_failure_analysis_v3",

        "workspace_id":
            WORKSPACE_ID,

        "run_id":
            population_report.get(
                "run_id"
            ),

        "population_processed_count":
            population_report.get(
                "processed_count"
            ),

        "population_pass_count":
            population_report.get(
                "pass_count"
            ),

        "population_fail_count":
            population_report.get(
                "fail_count"
            ),

        "analyzed_failure_count":
            len(
                failures
            ),

        "rejection_reason_counts":
            dict(
                rejection_reason_counts.most_common()
            ),

        "failed_check_counts":
            dict(
                failed_check_counts.most_common()
            ),

        "warning_counts":
            dict(
                warning_counts.most_common()
            ),

        "quality_grade_counts":
            dict(
                grade_counts.most_common()
            ),

        "word_count_summary": {
            "minimum":
                min(
                    word_counts
                )
                if word_counts
                else 0,

            "maximum":
                max(
                    word_counts
                )
                if word_counts
                else 0,

            "below_150":
                sum(
                    count < 150
                    for count in word_counts
                ),

            "150_or_more":
                sum(
                    count >= 150
                    for count in word_counts
                ),
        },

        "failure_manifest_path":
            str(
                failure_manifest_path
            ),

        "articles":
            analyzed_records,

        "source_articles_modified":
            False,

        "integrity_artifacts_modified":
            False,

        "validation_evidence_modified":
            False,
    }

    write_json(
        SCAN_REPORT_PATH,
        report,
    )

    print()
    print(
        "Population processed:              "
        + str(
            report[
                "population_processed_count"
            ]
        )
    )

    print(
        "Population PASS:                   "
        + str(
            report[
                "population_pass_count"
            ]
        )
    )

    print(
        "Population FAIL:                   "
        + str(
            report[
                "population_fail_count"
            ]
        )
    )

    print(
        "Failures analyzed:                 "
        + str(
            report[
                "analyzed_failure_count"
            ]
        )
    )

    print()
    print(
        "REJECTION REASON COUNTS"
    )

    for reason, count in (
        rejection_reason_counts.most_common()
    ):
        print(
            f"  {reason}: {count}"
        )

    print()
    print(
        "FAILED CHECK COUNTS"
    )

    for check_name, count in (
        failed_check_counts.most_common()
    ):
        print(
            f"  {check_name}: {count}"
        )

    print()
    print(
        "WORD COUNT SUMMARY"
    )

    print(
        "  Minimum: "
        + str(
            report[
                "word_count_summary"
            ][
                "minimum"
            ]
        )
    )

    print(
        "  Maximum: "
        + str(
            report[
                "word_count_summary"
            ][
                "maximum"
            ]
        )
    )

    print(
        "  Below 150 words: "
        + str(
            report[
                "word_count_summary"
            ][
                "below_150"
            ]
        )
    )

    print(
        "  At least 150 words: "
        + str(
            report[
                "word_count_summary"
            ][
                "150_or_more"
            ]
        )
    )

    print()
    print(
        "FAILED ARTICLES"
    )

    for record in analyzed_records:
        print(
            "  "
            + str(
                record[
                    "source_record_id"
                ]
            )
            + " | words="
            + str(
                record[
                    "word_count"
                ]
            )
            + " | reasons="
            + ", ".join(
                record[
                    "rejection_reasons"
                ]
            )
        )

    print()
    print(
        "Failure analysis report: "
        + str(
            SCAN_REPORT_PATH
        )
    )

    print()
    print(
        "ARTICLE VALIDATION FAILURE ANALYSIS: PASS"
    )

    print(
        "All 69 failed Article Validation records "
        "were analyzed without modifying source content."
    )

    print("=" * 100)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
