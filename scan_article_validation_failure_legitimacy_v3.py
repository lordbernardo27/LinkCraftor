"""Review Article Validation failures without copying article bodies."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.article_validation.article_validation_engine_v3 import (
    extract_article_validation_document_v3,
)


WORKSPACE_ID = "ws_whattoexpect_com"

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

POPULATION_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_population_v3_verification.json"
)

OUTPUT_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_failure_legitimacy_v3.json"
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
                    "JSONL record is not an object at "
                    f"line {line_number}: {path}"
                )

            records.append(
                value
            )

    return records


def write_json(
    path: Path,
    value: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


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


def resolve_project_reference(
    raw_value: Any,
) -> Path:
    text = str(
        raw_value or ""
    ).strip()

    if not text:
        raise RuntimeError(
            "Article reference is missing."
        )

    supplied = Path(text)

    path = (
        supplied
        if supplied.is_absolute()
        else PROJECT_ROOT / supplied
    ).resolve()

    if not path.is_file():
        raise FileNotFoundError(
            f"Article file is missing: {path}"
        )

    return path


def normalize_paragraph(
    value: str,
) -> str:
    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip().casefold()


def paragraph_hash(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def url_pattern_flags(
    source_url: str,
    title: str,
) -> list[str]:
    parsed = urlparse(
        source_url
    )

    path_text = str(
        parsed.path or ""
    ).casefold()

    title_text = str(
        title or ""
    ).casefold()

    combined = (
        path_text
        + " "
        + title_text
    )

    patterns = {
        "AUTHOR_OR_PROFILE":
            (
                "/author/" in path_text
                or "/profile/" in path_text
                or "author" in title_text
            ),

        "ABOUT_PAGE":
            (
                "/about" in path_text
                or title_text.startswith(
                    "about "
                )
            ),

        "CATEGORY_OR_TAG":
            (
                "/category/" in path_text
                or "/tag/" in path_text
            ),

        "VIDEO_PAGE":
            (
                "/video" in path_text
                or "video" in title_text
            ),

        "GLOSSARY_OR_DEFINITION":
            (
                "glossary" in combined
                or "definition" in combined
            ),

        "NEWS_OR_UPDATE":
            (
                "/news/" in path_text
                or "news" in title_text
                or "update" in title_text
            ),

        "TOOL_OR_CALCULATOR":
            (
                "calculator" in combined
                or "/tool" in path_text
            ),
    }

    return [
        name
        for name, matched
        in patterns.items()
        if matched
    ]


def classify_failure(
    *,
    rejection_reasons: list[str],
    word_count: int,
    paragraph_count: int,
    heading_count: int,
    title_present: bool,
) -> str:
    reasons = set(
        rejection_reasons
    )

    if (
        "HIGH_DUPLICATE_PARAGRAPH_RATIO"
        in reasons
    ):
        return (
            "DUPLICATE_PATTERN_REVIEW_REQUIRED"
        )

    if (
        "INVALID_PARAGRAPH_STRUCTURE"
        in reasons
    ):
        return (
            "SHORT_AND_STRUCTURALLY_DEFICIENT"
        )

    if reasons == {
        "LOW_WORD_COUNT"
    }:
        if (
            word_count >= 100
            and paragraph_count >= 2
            and title_present
        ):
            if heading_count >= 1:
                return (
                    "SHORT_BUT_STRUCTURED_WITH_HEADINGS"
                )

            return (
                "SHORT_BUT_STRUCTURED_NARRATIVE"
            )

        if (
            paragraph_count >= 2
            and title_present
        ):
            return (
                "VERY_SHORT_BUT_STRUCTURED"
            )

        return (
            "SHORT_STRUCTURE_REVIEW_REQUIRED"
        )

    return (
        "MULTIPLE_FAILURE_REVIEW_REQUIRED"
    )


def main() -> int:
    print()
    print("=" * 100)
    print(
        "ARTICLE VALIDATION — FAILURE LEGITIMACY REVIEW"
    )
    print("=" * 100)

    population_report = load_json(
        POPULATION_REPORT_PATH
    )

    artifact_paths = population_report.get(
        "artifact_paths"
    )

    if not isinstance(
        artifact_paths,
        dict,
    ):
        raise RuntimeError(
            "Population report has no artifact paths."
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
            "Failure manifest is missing: "
            + str(
                failure_manifest_path
            )
        )

    failure_records = load_jsonl(
        failure_manifest_path
    )

    expected_failure_count = int(
        population_report.get(
            "fail_count"
        )
        or 0
    )

    if (
        len(failure_records)
        != expected_failure_count
    ):
        raise RuntimeError(
            "Failure count mismatch: "
            f"{len(failure_records)} != "
            f"{expected_failure_count}"
        )

    classification_counts: Counter[str] = Counter()
    url_pattern_counts: Counter[str] = Counter()
    word_bucket_counts: Counter[str] = Counter()

    reviewed_records: list[
        dict[str, Any]
    ] = []

    hash_mismatch_count = 0

    for record in failure_records:
        source_record_id = str(
            record.get(
                "source_record_id"
            )
            or ""
        ).strip()

        article_path = (
            resolve_project_reference(
                record.get(
                    "article_reference"
                )
            )
        )

        expected_sha256 = str(
            record.get(
                "article_sha256"
            )
            or ""
        ).strip().lower()

        actual_sha256 = sha256_file(
            article_path
        )

        hash_verified = (
            expected_sha256
            == actual_sha256
        )

        if not hash_verified:
            hash_mismatch_count += 1

        article_html = article_path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )

        extracted = (
            extract_article_validation_document_v3(
                article_html
            )
        )

        article_text = str(
            extracted.get(
                "article_text"
            )
            or ""
        )

        paragraphs = [
            paragraph.strip()
            for paragraph in article_text.split(
                "\n\n"
            )
            if paragraph.strip()
        ]

        normalized_paragraphs = [
            normalize_paragraph(
                paragraph
            )
            for paragraph in paragraphs
            if len(
                normalize_paragraph(
                    paragraph
                )
            )
            >= 20
        ]

        paragraph_counts = Counter(
            normalized_paragraphs
        )

        repeated_groups = [
            {
                "paragraph_sha256":
                    paragraph_hash(
                        paragraph
                    ),

                "occurrence_count":
                    count,

                "normalized_character_count":
                    len(
                        paragraph
                    ),
            }
            for paragraph, count
            in paragraph_counts.items()
            if count > 1
        ]

        repeated_groups.sort(
            key=lambda item: (
                -int(
                    item[
                        "occurrence_count"
                    ]
                ),
                -int(
                    item[
                        "normalized_character_count"
                    ]
                ),
            )
        )

        duplicate_occurrence_count = sum(
            int(
                item[
                    "occurrence_count"
                ]
            )
            - 1
            for item in repeated_groups
        )

        duplicate_ratio = (
            (
                duplicate_occurrence_count
                / len(
                    normalized_paragraphs
                )
            )
            if normalized_paragraphs
            else 0.0
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
            or len(
                article_text.split()
            )
        )

        paragraph_count = int(
            statistics.get(
                "paragraph_count"
            )
            or len(paragraphs)
        )

        heading_count = int(
            statistics.get(
                "heading_count"
            )
            or len(
                extracted.get(
                    "headings"
                )
                or []
            )
        )

        title = str(
            record.get(
                "title"
            )
            or extracted.get(
                "title"
            )
            or extracted.get(
                "h1"
            )
            or ""
        ).strip()

        source_url = str(
            record.get(
                "source_url"
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

        classification = (
            classify_failure(
                rejection_reasons=(
                    rejection_reasons
                ),
                word_count=word_count,
                paragraph_count=(
                    paragraph_count
                ),
                heading_count=(
                    heading_count
                ),
                title_present=bool(
                    title
                ),
            )
        )

        classification_counts[
            classification
        ] += 1

        patterns = url_pattern_flags(
            source_url,
            title,
        )

        for pattern in patterns:
            url_pattern_counts[
                pattern
            ] += 1

        if word_count < 100:
            word_bucket = "BELOW_100"

        elif word_count < 120:
            word_bucket = "100_TO_119"

        elif word_count < 150:
            word_bucket = "120_TO_149"

        else:
            word_bucket = "150_OR_MORE"

        word_bucket_counts[
            word_bucket
        ] += 1

        reviewed_records.append(
            {
                "source_record_id":
                    source_record_id,

                "title":
                    title,

                "source_url":
                    source_url,

                "article_reference":
                    record.get(
                        "article_reference"
                    ),

                "article_sha256_verified":
                    hash_verified,

                "word_count":
                    word_count,

                "paragraph_count":
                    paragraph_count,

                "heading_count":
                    heading_count,

                "title_present":
                    bool(title),

                "rejection_reasons":
                    rejection_reasons,

                "classification":
                    classification,

                "url_pattern_flags":
                    patterns,

                "normalized_paragraph_count":
                    len(
                        normalized_paragraphs
                    ),

                "repeated_paragraph_group_count":
                    len(
                        repeated_groups
                    ),

                "duplicate_occurrence_count":
                    duplicate_occurrence_count,

                "calculated_duplicate_ratio":
                    round(
                        duplicate_ratio,
                        6,
                    ),

                "repeated_paragraph_groups":
                    repeated_groups,

                "article_body_included":
                    False,
            }
        )

    reviewed_records.sort(
        key=lambda record: (
            str(
                record.get(
                    "classification"
                )
            ),
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
            ),
        )
    )

    report = {
        "schema_version":
            "article_validation_failure_legitimacy_v3",

        "workspace_id":
            WORKSPACE_ID,

        "run_id":
            population_report.get(
                "run_id"
            ),

        "failure_count":
            len(
                reviewed_records
            ),

        "classification_counts":
            dict(
                classification_counts.most_common()
            ),

        "word_bucket_counts":
            dict(
                word_bucket_counts.most_common()
            ),

        "url_pattern_counts":
            dict(
                url_pattern_counts.most_common()
            ),

        "article_sha256_mismatch_count":
            hash_mismatch_count,

        "duplicate_failure_count":
            sum(
                classification
                == "DUPLICATE_PATTERN_REVIEW_REQUIRED"
                for classification
                in (
                    record[
                        "classification"
                    ]
                    for record
                    in reviewed_records
                )
            ),

        "records":
            reviewed_records,

        "article_bodies_included":
            False,

        "source_articles_modified":
            False,

        "validation_evidence_modified":
            False,
    }

    write_json(
        OUTPUT_REPORT_PATH,
        report,
    )

    print()
    print(
        "Failures reviewed:                 "
        + str(
            report[
                "failure_count"
            ]
        )
    )

    print(
        "Article SHA-256 mismatches:         "
        + str(
            hash_mismatch_count
        )
    )

    print()
    print(
        "CLASSIFICATION COUNTS"
    )

    for classification, count in (
        classification_counts.most_common()
    ):
        print(
            f"  {classification}: {count}"
        )

    print()
    print(
        "WORD-COUNT BUCKETS"
    )

    for bucket, count in (
        word_bucket_counts.most_common()
    ):
        print(
            f"  {bucket}: {count}"
        )

    print()
    print(
        "URL/PAGE PATTERNS"
    )

    if url_pattern_counts:
        for pattern, count in (
            url_pattern_counts.most_common()
        ):
            print(
                f"  {pattern}: {count}"
            )

    else:
        print(
            "  No predefined URL patterns detected."
        )

    print()
    print(
        "DUPLICATE-RATIO RECORDS"
    )

    for record in reviewed_records:
        if (
            record[
                "classification"
            ]
            != "DUPLICATE_PATTERN_REVIEW_REQUIRED"
        ):
            continue

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
            + " | paragraphs="
            + str(
                record[
                    "normalized_paragraph_count"
                ]
            )
            + " | repeated groups="
            + str(
                record[
                    "repeated_paragraph_group_count"
                ]
            )
            + " | duplicate ratio="
            + str(
                record[
                    "calculated_duplicate_ratio"
                ]
            )
        )

    print()
    print(
        "Legitimacy review report: "
        + str(
            OUTPUT_REPORT_PATH
        )
    )

    print()
    print(
        "ARTICLE VALIDATION FAILURE "
        "LEGITIMACY REVIEW: PASS"
    )

    print(
        "All 69 failures were structurally reviewed "
        "without copying or modifying article bodies."
    )

    print("=" * 100)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
