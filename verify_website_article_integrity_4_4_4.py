"""Verification for Phase 4.4.4 Website Integrity Report."""

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
    generate_website_integrity_report,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_STORE_COUNT = 2222
EXPECTED_UPSTREAM_COUNT = 2225
DEFERRED_UPSTREAM_COUNT = 3
EXPECTED_OVERALL_PASS = 2219
EXPECTED_OVERALL_FAIL = 3

EXPECTED_FAILED_SOURCE_IDS = {
    "raw_html_fc8c43c9937f0809",
    "raw_html_14533594924ea9c1",
    "raw_html_98f22e0c526ac925",
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def directory_hashes(
    root: Path,
    pattern: str,
) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): file_sha256(path)
        for path in sorted(root.rglob(pattern))
        if path.is_file()
    }


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
        "PHASE 4.4.4 — WEBSITE INTEGRITY REPORT VERIFICATION"
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

    article_hashes_before = directory_hashes(
        articles_root,
        "*.html",
    )

    metadata_hashes_before = directory_hashes(
        metadata_root,
        "*.json",
    )

    report = generate_website_integrity_report(
        project_root=PROJECT_ROOT,
        workspace_id=WORKSPACE_ID,
        expected_store_count=EXPECTED_STORE_COUNT,
        expected_upstream_count=EXPECTED_UPSTREAM_COUNT,
        deferred_upstream_count=DEFERRED_UPSTREAM_COUNT,
    )

    article_hashes_after = directory_hashes(
        articles_root,
        "*.html",
    )

    metadata_hashes_after = directory_hashes(
        metadata_root,
        "*.json",
    )

    report_root = (
        data_root
        / "website_article_integrity"
        / WORKSPACE_ID
        / "report"
    )

    ledger_path = (
        report_root
        / "website_integrity_ledger.jsonl"
    )

    failures_path = (
        report_root
        / "website_integrity_failures.jsonl"
    )

    report_json_path = (
        report_root
        / "website_integrity_report.json"
    )

    report_html_path = (
        report_root
        / "website_integrity_report.html"
    )

    index_html_path = (
        report_root
        / "index.html"
    )

    failures: list[str] = []

    if article_hashes_before != article_hashes_after:
        failures.append(
            "One or more UDARE article documents changed."
        )

    if metadata_hashes_before != metadata_hashes_after:
        failures.append(
            "One or more UDARE metadata records changed."
        )

    for required_path in (
        ledger_path,
        failures_path,
        report_json_path,
        report_html_path,
        index_html_path,
    ):
        if not required_path.is_file():
            failures.append(
                f"Required report artifact missing: {required_path}"
            )

    ledger_records = (
        load_jsonl(ledger_path)
        if ledger_path.is_file()
        else []
    )

    failed_records = (
        load_jsonl(failures_path)
        if failures_path.is_file()
        else []
    )

    if len(ledger_records) != EXPECTED_STORE_COUNT:
        failures.append(
            "Expected 2,222 integrity ledger records, "
            f"found {len(ledger_records)}."
        )

    if len(failed_records) != EXPECTED_OVERALL_FAIL:
        failures.append(
            "Expected three failed-article records, "
            f"found {len(failed_records)}."
        )

    ledger_paths = [
        record.get("article_path")
        for record in ledger_records
    ]

    if len(set(ledger_paths)) != len(ledger_paths):
        failures.append(
            "Duplicate article paths exist in the integrity ledger."
        )

    ledger_source_ids = [
        record.get("source_record_id")
        for record in ledger_records
    ]

    if len(set(ledger_source_ids)) != len(
        ledger_source_ids
    ):
        failures.append(
            "Duplicate source identities exist in the integrity "
            "ledger."
        )

    invalid_statuses = [
        record.get("overall_status")
        for record in ledger_records
        if record.get("overall_status") not in {
            "PASS",
            "FAIL",
        }
    ]

    if invalid_statuses:
        failures.append(
            "Invalid overall statuses exist in the integrity ledger."
        )

    actual_pass_count = sum(
        record.get("overall_status") == "PASS"
        for record in ledger_records
    )

    actual_fail_count = sum(
        record.get("overall_status") == "FAIL"
        for record in ledger_records
    )

    if actual_pass_count != EXPECTED_OVERALL_PASS:
        failures.append(
            "Expected 2,219 overall PASS records, "
            f"found {actual_pass_count}."
        )

    if actual_fail_count != EXPECTED_OVERALL_FAIL:
        failures.append(
            "Expected three overall FAIL records, "
            f"found {actual_fail_count}."
        )

    actual_failed_source_ids = {
        record.get("source_record_id")
        for record in failed_records
    }

    if actual_failed_source_ids != EXPECTED_FAILED_SOURCE_IDS:
        failures.append(
            "The failed source-identity set does not match the "
            "three recorded validation failures."
        )

    summary = report.get("summary", {})

    if report.get("report_status") != "COMPLETE":
        failures.append(
            "Report status is not COMPLETE."
        )

    if (
        report.get("integrity_outcome")
        != "COMPLETE_WITH_FAILURES"
    ):
        failures.append(
            "Integrity outcome is not COMPLETE_WITH_FAILURES."
        )

    if (
        report.get("certification_status")
        != "NOT_YET_CERTIFIED"
    ):
        failures.append(
            "The report was prematurely marked certified."
        )

    if (
        report.get("quarantine_status")
        != "NOT_YET_EXECUTED"
    ):
        failures.append(
            "The report was prematurely marked quarantined."
        )

    if summary.get("stored_article_count") != (
        EXPECTED_STORE_COUNT
    ):
        failures.append(
            "Stored article count is not 2,222."
        )

    if summary.get("articles_assessed") != (
        EXPECTED_STORE_COUNT
    ):
        failures.append(
            "Assessed article count is not 2,222."
        )

    if summary.get("overall_pass_count") != (
        EXPECTED_OVERALL_PASS
    ):
        failures.append(
            "Report summary PASS count is not 2,219."
        )

    if summary.get("overall_fail_count") != (
        EXPECTED_OVERALL_FAIL
    ):
        failures.append(
            "Report summary FAIL count is not three."
        )

    if summary.get("distinct_failed_article_count") != 3:
        failures.append(
            "Distinct failed-article count is not three."
        )

    if summary.get("quarantine_candidate_count") != 3:
        failures.append(
            "Quarantine candidate count is not three."
        )

    if summary.get("deferred_upstream_count") != 3:
        failures.append(
            "Deferred upstream count is not three."
        )

    if summary.get("quarantine_executed") is not False:
        failures.append(
            "Quarantine was incorrectly marked executed."
        )

    if report_html_path.is_file():
        html_report = report_html_path.read_text(
            encoding="utf-8",
        )

        for source_id in EXPECTED_FAILED_SOURCE_IDS:
            if source_id not in html_report:
                failures.append(
                    "HTML report does not contain failed source "
                    f"identity: {source_id}"
                )

    print()
    print(
        f"Integrity ledger records:       "
        f"{len(ledger_records)}"
    )
    print(
        f"Overall PASS:                   "
        f"{actual_pass_count}"
    )
    print(
        f"Overall FAIL:                   "
        f"{actual_fail_count}"
    )
    print(
        f"Structure-stage failures:       "
        f"{summary.get('structure_fail_count')}"
    )
    print(
        f"Component-stage failures:       "
        f"{summary.get('component_fail_count')}"
    )
    print(
        f"Corruption/truncation failures: "
        f"{summary.get('corruption_truncation_fail_count')}"
    )
    print(
        f"Distinct failed articles:       "
        f"{summary.get('distinct_failed_article_count')}"
    )
    print(
        f"Quarantine candidates:          "
        f"{summary.get('quarantine_candidate_count')}"
    )
    print(
        f"Deferred upstream pages:        "
        f"{summary.get('deferred_upstream_count')}"
    )

    if failed_records:
        print()
        print("FAILED ARTICLE SET")

        for record in failed_records:
            print(
                "  "
                f"{record.get('source_record_id')} | "
                f"{', '.join(record.get('consolidated_failure_reasons', []))}"
            )

    print()
    print(f"JSON report:  {report_json_path}")
    print(f"HTML report:  {report_html_path}")
    print(f"Browser index: {index_html_path}")
    print(f"Full ledger:  {ledger_path}")
    print(f"Failures:     {failures_path}")
    print()

    if failures:
        print("PHASE 4.4.4 VERIFICATION: FAIL")

        for failure in failures:
            print(f"  - {failure}")

        print("=" * 76)
        return 1

    print("PHASE 4.4.4 VERIFICATION: PASS")
    print(
        "The Website Integrity Report contains all 2,222 "
        "stored UDARE articles."
    )
    print(
        "The report consolidated three distinct failed articles "
        "and 2,219 overall PASS articles."
    )
    print(
        "No UDARE article or metadata record was modified, "
        "deleted, or quarantined."
    )
    print("=" * 76)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
