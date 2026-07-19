"""Verification for Phase 4.4.3 corruption and truncation detection."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SERVER_ROOT = PROJECT_ROOT / "backend" / "server"

if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(SERVER_ROOT),
    )

from integrity.website_article_integrity import (  # noqa: E402
    run_corruption_truncation_detection,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_STORE_COUNT = 2222
EXPECTED_UPSTREAM_COUNT = 2225
DEFERRED_UPSTREAM_COUNT = 3


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            try:
                records.append(
                    json.loads(line)
                )
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Invalid JSONL line {line_number}: {exc}"
                ) from exc

    return records


def main() -> int:
    print()
    print("=" * 76)
    print(
        "PHASE 4.4.3 — CORRUPTION AND TRUNCATION VERIFICATION"
    )
    print("=" * 76)

    data_root = (
        PROJECT_ROOT
        / "backend"
        / "server"
        / "data"
    )

    udare_root = (
        data_root
        / "udare_store"
        / WORKSPACE_ID
    )

    articles_root = udare_root / "articles"
    metadata_root = udare_root / "metadata"

    article_paths_before = sorted(
        path
        for path in articles_root.rglob("*.html")
        if path.is_file()
    )

    metadata_paths_before = sorted(
        path
        for path in metadata_root.glob("*.json")
        if path.is_file()
    )

    article_hashes_before = {
        path.relative_to(articles_root).as_posix(): (
            file_sha256(path)
        )
        for path in article_paths_before
    }

    metadata_hashes_before = {
        path.name: file_sha256(path)
        for path in metadata_paths_before
    }

    summary = run_corruption_truncation_detection(
        project_root=PROJECT_ROOT,
        workspace_id=WORKSPACE_ID,
        expected_store_count=EXPECTED_STORE_COUNT,
        expected_upstream_count=EXPECTED_UPSTREAM_COUNT,
        deferred_upstream_count=DEFERRED_UPSTREAM_COUNT,
    )

    article_paths_after = sorted(
        path
        for path in articles_root.rglob("*.html")
        if path.is_file()
    )

    metadata_paths_after = sorted(
        path
        for path in metadata_root.glob("*.json")
        if path.is_file()
    )

    article_hashes_after = {
        path.relative_to(articles_root).as_posix(): (
            file_sha256(path)
        )
        for path in article_paths_after
    }

    metadata_hashes_after = {
        path.name: file_sha256(path)
        for path in metadata_paths_after
    }

    output_root = (
        data_root
        / "website_article_integrity"
        / WORKSPACE_ID
        / "corruption_truncation"
    )

    results_path = (
        output_root
        / "corruption_truncation_results.jsonl"
    )

    summary_path = (
        output_root
        / "corruption_truncation_summary.json"
    )

    failures: list[str] = []

    if len(article_paths_before) != EXPECTED_STORE_COUNT:
        failures.append(
            "UDARE did not contain 2,222 articles before detection."
        )

    if len(article_paths_after) != EXPECTED_STORE_COUNT:
        failures.append(
            "UDARE did not contain 2,222 articles after detection."
        )

    if len(metadata_paths_before) != EXPECTED_STORE_COUNT:
        failures.append(
            "UDARE did not contain 2,222 metadata records before "
            "detection."
        )

    if len(metadata_paths_after) != EXPECTED_STORE_COUNT:
        failures.append(
            "UDARE did not contain 2,222 metadata records after "
            "detection."
        )

    if article_hashes_before != article_hashes_after:
        failures.append(
            "One or more UDARE article files changed."
        )

    if metadata_hashes_before != metadata_hashes_after:
        failures.append(
            "One or more UDARE metadata records changed."
        )

    if not results_path.is_file():
        failures.append(
            "Corruption/truncation results were not created."
        )

    if not summary_path.is_file():
        failures.append(
            "Corruption/truncation summary was not created."
        )

    records: list[dict] = []

    if results_path.is_file():
        records = load_jsonl(
            results_path,
        )

    if len(records) != EXPECTED_STORE_COUNT:
        failures.append(
            "Expected 2,222 detection records, "
            f"found {len(records)}."
        )

    article_paths = [
        record.get("article_path")
        for record in records
    ]

    if len(set(article_paths)) != len(article_paths):
        failures.append(
            "Duplicate article paths exist in detection results."
        )

    source_record_ids = [
        record.get("source_record_id")
        for record in records
    ]

    if len(set(source_record_ids)) != len(
        source_record_ids
    ):
        failures.append(
            "Duplicate source identities exist in detection results."
        )

    invalid_statuses = [
        record.get("status")
        for record in records
        if record.get("status") not in {
            "PASS",
            "FAIL",
        }
    ]

    if invalid_statuses:
        failures.append(
            "Invalid detection statuses were found."
        )

    if summary.get("articles_checked") != EXPECTED_STORE_COUNT:
        failures.append(
            "Summary does not report 2,222 checked articles."
        )

    if (
        summary.get("integrity_pass_count", 0)
        + summary.get("integrity_fail_count", 0)
        != EXPECTED_STORE_COUNT
    ):
        failures.append(
            "Detection PASS and FAIL counts do not total 2,222."
        )

    if summary.get("identity_reference_count") != (
        EXPECTED_STORE_COUNT
    ):
        failures.append(
            "Not all source-identity references were loaded."
        )

    if summary.get("identity_unresolved_count") != 0:
        failures.append(
            "One or more article identities were unresolved."
        )

    if summary.get("deferred_upstream_count") != 3:
        failures.append(
            "The three deferred upstream pages were not preserved."
        )

    if summary.get("execution_status") != "COMPLETE":
        failures.append(
            "Corruption/truncation detection is not COMPLETE."
        )

    failed_records = [
        record
        for record in records
        if record.get("status") == "FAIL"
    ]

    warning_records = [
        record
        for record in records
        if record.get("warning_reasons")
    ]

    print()
    print(
        f"UDARE articles before:          "
        f"{len(article_paths_before)}"
    )
    print(
        f"UDARE articles after:           "
        f"{len(article_paths_after)}"
    )
    print(
        f"Metadata records before:        "
        f"{len(metadata_paths_before)}"
    )
    print(
        f"Metadata records after:         "
        f"{len(metadata_paths_after)}"
    )
    print(
        f"Detection records:              "
        f"{len(records)}"
    )
    print(
        f"Integrity PASS:                 "
        f"{summary.get('integrity_pass_count')}"
    )
    print(
        f"Integrity FAIL:                 "
        f"{summary.get('integrity_fail_count')}"
    )
    print(
        f"Corruption detected:            "
        f"{summary.get('corruption_detected_count')}"
    )
    print(
        f"Truncation detected:            "
        f"{summary.get('truncation_detected_count')}"
    )
    print(
        f"Articles with warnings:         "
        f"{summary.get('warning_article_count')}"
    )
    print(
        f"Identity references resolved:   "
        f"{summary.get('identity_reference_count')}"
    )
    print(
        f"Identity references unresolved: "
        f"{summary.get('identity_unresolved_count')}"
    )
    print(
        f"Deferred upstream pages:        "
        f"{summary.get('deferred_upstream_count')}"
    )

    corruption_reasons = summary.get(
        "corruption_reason_counts",
        {},
    )

    truncation_reasons = summary.get(
        "truncation_reason_counts",
        {},
    )

    warning_reasons = summary.get(
        "warning_reason_counts",
        {},
    )

    if corruption_reasons:
        print()
        print("CORRUPTION REASONS")

        for reason, count in corruption_reasons.items():
            print(f"  {reason}: {count}")

    if truncation_reasons:
        print()
        print("TRUNCATION REASONS")

        for reason, count in truncation_reasons.items():
            print(f"  {reason}: {count}")

    if warning_reasons:
        print()
        print("WARNING REASONS")

        for reason, count in warning_reasons.items():
            print(f"  {reason}: {count}")

    if failed_records:
        print()
        print("FIRST 20 FAILED ARTICLES")

        for record in failed_records[:20]:
            reasons = (
                record.get("corruption_reasons", [])
                + record.get("truncation_reasons", [])
            )

            print(
                "  "
                f"{record.get('source_record_id')} | "
                f"{', '.join(reasons)}"
            )

    if warning_records:
        print()
        print("FIRST 20 WARNING ARTICLES")

        for record in warning_records[:20]:
            print(
                "  "
                f"{record.get('source_record_id')} | "
                f"{', '.join(record.get('warning_reasons', []))}"
            )

    print()
    print(f"Results: {results_path}")
    print(f"Summary: {summary_path}")
    print()

    if failures:
        print("PHASE 4.4.3 VERIFICATION: FAIL")

        for failure in failures:
            print(f"  - {failure}")

        print("=" * 76)
        return 1

    print("PHASE 4.4.3 VERIFICATION: PASS")
    print(
        "All 2,222 stored UDARE articles were checked for "
        "corruption and truncation."
    )

    if failed_records:
        print(
            "Detected failures were recorded for the Website "
            "Integrity Report and quarantine stage."
        )

    print(
        "No UDARE article or metadata record was modified, "
        "deleted, repaired, or quarantined."
    )
    print("=" * 76)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
