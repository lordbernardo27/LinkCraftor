"""Verification for Phase 4.4.2 Required Article Components."""

from __future__ import annotations

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
    run_component_validation,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_STORE_COUNT = 2222
EXPECTED_UPSTREAM_COUNT = 2225
DEFERRED_UPSTREAM_COUNT = 3


def main() -> int:
    print()
    print("=" * 72)
    print(
        "PHASE 4.4.2 — REQUIRED ARTICLE COMPONENT VERIFICATION"
    )
    print("=" * 72)

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
        path.name: path.stat().st_size
        for path in article_paths_before
    }

    summary = run_component_validation(
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
        path.name: path.stat().st_size
        for path in article_paths_after
    }

    output_root = (
        data_root
        / "website_article_integrity"
        / WORKSPACE_ID
        / "components"
    )

    results_path = (
        output_root
        / "component_results.jsonl"
    )

    summary_path = (
        output_root
        / "component_summary.json"
    )

    failures: list[str] = []

    if len(article_paths_before) != EXPECTED_STORE_COUNT:
        failures.append(
            "UDARE did not contain 2,222 articles before validation."
        )

    if len(article_paths_after) != EXPECTED_STORE_COUNT:
        failures.append(
            "UDARE did not contain 2,222 articles after validation."
        )

    if len(metadata_paths_before) != EXPECTED_STORE_COUNT:
        failures.append(
            "UDARE did not contain 2,222 metadata records "
            "before validation."
        )

    if len(metadata_paths_after) != EXPECTED_STORE_COUNT:
        failures.append(
            "UDARE did not contain 2,222 metadata records "
            "after validation."
        )

    if article_hashes_before != article_hashes_after:
        failures.append(
            "One or more UDARE article files changed."
        )

    if not results_path.is_file():
        failures.append(
            "Component results JSONL was not created."
        )

    if not summary_path.is_file():
        failures.append(
            "Component summary JSON was not created."
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
                        f"Invalid JSONL line {line_number}: {exc}"
                    )

    if len(result_records) != EXPECTED_STORE_COUNT:
        failures.append(
            "Expected 2,222 component-result records, "
            f"found {len(result_records)}."
        )

    source_record_ids = [
        record.get("source_record_id")
        for record in result_records
    ]

    if len(set(source_record_ids)) != len(source_record_ids):
        failures.append(
            "Duplicate source identities exist in component results."
        )

    invalid_statuses = [
        record.get("status")
        for record in result_records
        if record.get("status") not in {
            "PASS",
            "FAIL",
        }
    ]

    if invalid_statuses:
        failures.append(
            "Invalid component-validation statuses were found."
        )

    if summary.get("articles_validated") != EXPECTED_STORE_COUNT:
        failures.append(
            "Summary does not report 2,222 validated articles."
        )

    if (
        summary.get("component_pass_count", 0)
        + summary.get("component_fail_count", 0)
        != EXPECTED_STORE_COUNT
    ):
        failures.append(
            "Component PASS and FAIL totals do not equal 2,222."
        )

    if summary.get("metadata_resolved_count") != EXPECTED_STORE_COUNT:
        failures.append(
            "Not all 2,222 article metadata records were resolved."
        )

    if summary.get("metadata_unresolved_count") != 0:
        failures.append(
            "One or more article metadata records remain unresolved."
        )

    if summary.get("deferred_upstream_count") != 3:
        failures.append(
            "The three deferred upstream pages were not preserved."
        )

    if summary.get("execution_status") != "COMPLETE":
        failures.append(
            "Component validation is not marked COMPLETE."
        )

    failed_records = [
        record
        for record in result_records
        if record.get("status") == "FAIL"
    ]

    print()
    print(
        f"UDARE articles before:       "
        f"{len(article_paths_before)}"
    )
    print(
        f"UDARE articles after:        "
        f"{len(article_paths_after)}"
    )
    print(
        f"Metadata before:             "
        f"{len(metadata_paths_before)}"
    )
    print(
        f"Metadata after:              "
        f"{len(metadata_paths_after)}"
    )
    print(
        f"Component result records:    "
        f"{len(result_records)}"
    )
    print(
        f"Component PASS:              "
        f"{summary.get('component_pass_count')}"
    )
    print(
        f"Component FAIL:              "
        f"{summary.get('component_fail_count')}"
    )
    print(
        f"Metadata resolved:           "
        f"{summary.get('metadata_resolved_count')}"
    )
    print(
        f"Metadata unresolved:         "
        f"{summary.get('metadata_unresolved_count')}"
    )
    print(
        f"Deferred upstream pages:     "
        f"{summary.get('deferred_upstream_count')}"
    )

    failure_reason_counts = summary.get(
        "failure_reason_counts",
        {},
    )

    if failure_reason_counts:
        print()
        print("COMPONENT FAILURE REASONS")

        for reason, count in failure_reason_counts.items():
            print(f"  {reason}: {count}")

    resolution_counts = summary.get(
        "metadata_resolution_method_counts",
        {},
    )

    if resolution_counts:
        print()
        print("METADATA RESOLUTION METHODS")

        for method, count in resolution_counts.items():
            print(f"  {method}: {count}")

    if failed_records:
        print()
        print("FIRST 20 COMPONENT FAILURES")

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
        print("PHASE 4.4.2 VERIFICATION: FAIL")

        for failure in failures:
            print(f"  - {failure}")

        print("=" * 72)
        return 1

    print("PHASE 4.4.2 VERIFICATION: PASS")
    print(
        "All 2,222 stored articles were checked for required "
        "components."
    )
    print(
        "All 2,222 article documents were linked to their "
        "metadata records."
    )

    if failed_records:
        print(
            "Articles with missing required components were "
            "recorded for later reporting and quarantine."
        )

    print(
        "No UDARE article or metadata record was modified, "
        "deleted, or quarantined."
    )
    print("=" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
