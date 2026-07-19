"""Verification for Phase 4.4.1 Website Article Structure Validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SERVER_ROOT = PROJECT_ROOT / "backend" / "server"

if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from integrity.website_article_integrity import (  # noqa: E402
    run_structure_validation,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_STORE_COUNT = 2222
EXPECTED_UPSTREAM_COUNT = 2225
DEFERRED_UPSTREAM_COUNT = 3


def main() -> int:
    print()
    print("=" * 72)
    print("PHASE 4.4.1 — WEBSITE ARTICLE STRUCTURE VERIFICATION")
    print("=" * 72)

    data_root = (
        PROJECT_ROOT
        / "backend"
        / "server"
        / "data"
    )

    articles_root = (
        data_root
        / "udare_store"
        / WORKSPACE_ID
        / "articles"
    )

    article_paths = sorted(
        path
        for path in articles_root.rglob("*.html")
        if path.is_file()
    )

    before_count = len(article_paths)

    summary = run_structure_validation(
        project_root=PROJECT_ROOT,
        workspace_id=WORKSPACE_ID,
        expected_store_count=EXPECTED_STORE_COUNT,
        expected_upstream_count=EXPECTED_UPSTREAM_COUNT,
        deferred_upstream_count=DEFERRED_UPSTREAM_COUNT,
    )

    after_article_paths = sorted(
        path
        for path in articles_root.rglob("*.html")
        if path.is_file()
    )

    after_count = len(after_article_paths)

    output_root = (
        data_root
        / "website_article_integrity"
        / WORKSPACE_ID
        / "structure"
    )

    results_path = output_root / "structure_results.jsonl"
    summary_path = output_root / "structure_summary.json"

    failures: list[str] = []

    if before_count != EXPECTED_STORE_COUNT:
        failures.append(
            "UDARE article count before validation was not 2,222."
        )

    if after_count != EXPECTED_STORE_COUNT:
        failures.append(
            "UDARE article count after validation was not 2,222."
        )

    if before_count != after_count:
        failures.append(
            "UDARE article count changed during validation."
        )

    if not results_path.is_file():
        failures.append(
            "Structure results JSONL was not generated."
        )

    if not summary_path.is_file():
        failures.append(
            "Structure summary JSON was not generated."
        )

    result_records: list[dict] = []

    if results_path.is_file():
        with results_path.open(
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
                    result_records.append(
                        json.loads(line)
                    )
                except json.JSONDecodeError as exc:
                    failures.append(
                        "Invalid JSONL at line "
                        f"{line_number}: {exc}"
                    )

    if len(result_records) != EXPECTED_STORE_COUNT:
        failures.append(
            "Expected 2,222 structure-result records, "
            f"found {len(result_records)}."
        )

    source_record_ids = [
        record.get("source_record_id")
        for record in result_records
    ]

    if len(set(source_record_ids)) != len(source_record_ids):
        failures.append(
            "Duplicate source_record_id values exist in results."
        )

    invalid_statuses = [
        record.get("status")
        for record in result_records
        if record.get("status") not in {"PASS", "FAIL"}
    ]

    if invalid_statuses:
        failures.append(
            "One or more results contain an invalid status."
        )

    if summary.get("articles_validated") != EXPECTED_STORE_COUNT:
        failures.append(
            "Summary does not report 2,222 validated articles."
        )

    if (
        summary.get("structural_pass_count", 0)
        + summary.get("structural_fail_count", 0)
        != EXPECTED_STORE_COUNT
    ):
        failures.append(
            "Summary PASS and FAIL counts do not total 2,222."
        )

    if summary.get("deferred_upstream_count") != 3:
        failures.append(
            "Summary does not preserve the three deferred pages."
        )

    if summary.get("execution_status") != "COMPLETE":
        failures.append(
            "Structure-validation execution is not COMPLETE."
        )

    failed_records = [
        record
        for record in result_records
        if record.get("status") == "FAIL"
    ]

    print()
    print(f"UDARE articles before:       {before_count}")
    print(f"UDARE articles after:        {after_count}")
    print(
        "Result records:             "
        f"{len(result_records)}"
    )
    print(
        "Structural PASS:            "
        f"{summary.get('structural_pass_count')}"
    )
    print(
        "Structural FAIL:            "
        f"{summary.get('structural_fail_count')}"
    )
    print(
        "Deferred upstream pages:    "
        f"{summary.get('deferred_upstream_count')}"
    )
    print(
        "Metadata missing:           "
        f"{summary.get('metadata_missing_count')}"
    )

    failure_reason_counts = summary.get(
        "failure_reason_counts",
        {},
    )

    if failure_reason_counts:
        print()
        print("STRUCTURAL FAILURE REASONS")

        for reason, count in failure_reason_counts.items():
            print(f"  {reason}: {count}")

    if failed_records:
        print()
        print("FIRST 20 STRUCTURAL FAILURES")

        for record in failed_records[:20]:
            print(
                "  "
                f"{record.get('source_record_id')} | "
                f"{', '.join(record.get('failure_reasons', []))}"
            )

    print()
    print(f"Results: {results_path}")
    print(f"Summary: {summary_path}")
    print()

    if failures:
        print("PHASE 4.4.1 VERIFICATION: FAIL")

        for failure in failures:
            print(f"  - {failure}")

        print("=" * 72)
        return 1

    print("PHASE 4.4.1 VERIFICATION: PASS")
    print(
        "All 2,222 stored UDARE articles were structurally "
        "validated."
    )

    if failed_records:
        print(
            "Articles with structural failures were recorded for "
            "later integrity reporting and quarantine."
        )

    print(
        "No UDARE article was modified, deleted, or quarantined."
    )
    print("=" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
