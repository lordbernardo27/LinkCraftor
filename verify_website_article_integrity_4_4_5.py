"""Verification for Phase 4.4.5 failed-article quarantine."""

from __future__ import annotations

import hashlib
import json
import re
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
    execute_quarantine,
)


WORKSPACE_ID = "ws_whattoexpect_com"

EXPECTED_STORE_COUNT_BEFORE = 2222
EXPECTED_ACTIVE_COUNT_AFTER = 2219
EXPECTED_QUARANTINE_COUNT = 3
DEFERRED_UPSTREAM_COUNT = 3

EXPECTED_QUARANTINED_SOURCE_IDS = {
    "raw_html_fc8c43c9937f0809",
    "raw_html_14533594924ea9c1",
    "raw_html_98f22e0c526ac925",
}


def sha256_file(path: Path) -> str:
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
        "PHASE 4.4.5 — FAILED ARTICLE QUARANTINE VERIFICATION"
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

    active_articles_root = (
        udare_root
        / "articles"
    )

    active_metadata_root = (
        udare_root
        / "metadata"
    )

    udare_manifest_path = (
        udare_root
        / "manifests"
        / "udare_store_manifest.json"
    )

    udare_index_path = (
        udare_root
        / "index.html"
    )

    integrity_root = (
        data_root
        / "website_article_integrity"
        / WORKSPACE_ID
    )

    report_root = (
        integrity_root
        / "report"
    )

    report_json_path = (
        report_root
        / "website_integrity_report.json"
    )

    report_html_path = (
        report_root
        / "website_integrity_report.html"
    )

    report_failures_path = (
        report_root
        / "website_integrity_failures.jsonl"
    )

    report_hashes_before = {
        "json": sha256_file(
            report_json_path
        ),
        "html": sha256_file(
            report_html_path
        ),
        "failures": sha256_file(
            report_failures_path
        ),
    }

    pass_article_hashes_before: dict[str, str] = {}

    ledger_path = (
        report_root
        / "website_integrity_ledger.jsonl"
    )

    ledger_records = load_jsonl(
        ledger_path
    )

    pass_records = [
        record
        for record in ledger_records
        if record.get("overall_status") == "PASS"
    ]

    failed_records = [
        record
        for record in ledger_records
        if record.get("overall_status") == "FAIL"
    ]

    for record in pass_records:
        active_path = (
            udare_root
            / record["article_path"]
        )

        if active_path.is_file():
            pass_article_hashes_before[
                record["article_path"]
            ] = sha256_file(
                active_path
            )

    manifest = execute_quarantine(
        project_root=PROJECT_ROOT,
        workspace_id=WORKSPACE_ID,
        expected_store_count_before=(
            EXPECTED_STORE_COUNT_BEFORE
        ),
        expected_active_count_after=(
            EXPECTED_ACTIVE_COUNT_AFTER
        ),
        expected_quarantine_count=(
            EXPECTED_QUARANTINE_COUNT
        ),
        deferred_upstream_count=(
            DEFERRED_UPSTREAM_COUNT
        ),
    )

    quarantine_root = (
        integrity_root
        / "quarantine"
    )

    quarantine_articles_root = (
        quarantine_root
        / "articles"
    )

    quarantine_metadata_root = (
        quarantine_root
        / "metadata"
    )

    quarantine_manifest_path = (
        quarantine_root
        / "manifests"
        / "quarantine_manifest.json"
    )

    quarantine_records_path = (
        quarantine_root
        / "quarantine_records.jsonl"
    )

    quarantine_execution_path = (
        quarantine_root
        / "quarantine_execution.json"
    )

    quarantine_index_path = (
        quarantine_root
        / "index.html"
    )

    active_article_paths = sorted(
        path
        for path in active_articles_root.rglob(
            "*.html"
        )
        if path.is_file()
    )

    active_metadata_paths = sorted(
        path
        for path in active_metadata_root.glob(
            "*.json"
        )
        if path.is_file()
    )

    quarantine_article_paths = sorted(
        path
        for path in quarantine_articles_root.rglob(
            "*.html"
        )
        if path.is_file()
    )

    quarantine_metadata_paths = sorted(
        path
        for path in quarantine_metadata_root.glob(
            "*.json"
        )
        if path.is_file()
    )

    quarantine_records = (
        load_jsonl(
            quarantine_records_path
        )
        if quarantine_records_path.is_file()
        else []
    )

    failures: list[str] = []

    if (
        len(active_article_paths)
        != EXPECTED_ACTIVE_COUNT_AFTER
    ):
        failures.append(
            "Active UDARE article count is not 2,219."
        )

    if (
        len(active_metadata_paths)
        != EXPECTED_ACTIVE_COUNT_AFTER
    ):
        failures.append(
            "Active UDARE metadata count is not 2,219."
        )

    if (
        len(quarantine_article_paths)
        != EXPECTED_QUARANTINE_COUNT
    ):
        failures.append(
            "Quarantine article count is not three."
        )

    if (
        len(quarantine_metadata_paths)
        != EXPECTED_QUARANTINE_COUNT
    ):
        failures.append(
            "Quarantine metadata count is not three."
        )

    if (
        len(active_article_paths)
        + len(quarantine_article_paths)
        != EXPECTED_STORE_COUNT_BEFORE
    ):
        failures.append(
            "Active plus quarantined article counts do not "
            "equal 2,222."
        )

    if (
        len(active_metadata_paths)
        + len(quarantine_metadata_paths)
        != EXPECTED_STORE_COUNT_BEFORE
    ):
        failures.append(
            "Active plus quarantined metadata counts do not "
            "equal 2,222."
        )

    required_artifacts = (
        quarantine_manifest_path,
        quarantine_records_path,
        quarantine_execution_path,
        quarantine_index_path,
        udare_manifest_path,
        udare_index_path,
    )

    for path in required_artifacts:
        if not path.is_file():
            failures.append(
                f"Required quarantine artifact missing: {path}"
            )

    if len(quarantine_records) != 3:
        failures.append(
            "Quarantine ledger does not contain three records."
        )

    actual_quarantined_source_ids = {
        record.get("source_record_id")
        for record in quarantine_records
    }

    if (
        actual_quarantined_source_ids
        != EXPECTED_QUARANTINED_SOURCE_IDS
    ):
        failures.append(
            "The quarantined source-identity set is incorrect."
        )

    for failed_record in failed_records:
        active_article_path = (
            udare_root
            / failed_record["article_path"]
        )

        active_metadata_path = (
            udare_root
            / failed_record["metadata_path"]
        )

        if active_article_path.exists():
            failures.append(
                "A failed article remains in the active UDARE "
                f"Store: {active_article_path}"
            )

        if active_metadata_path.exists():
            failures.append(
                "Failed metadata remains in the active UDARE "
                f"Store: {active_metadata_path}"
            )

    for record in quarantine_records:
        article_path = Path(
            record["quarantine_article_path"]
        )

        metadata_path = Path(
            record["quarantine_metadata_path"]
        )

        if not article_path.is_file():
            failures.append(
                "Quarantined article is missing: "
                f"{article_path}"
            )
        elif (
            sha256_file(article_path)
            != record.get("article_sha256")
        ):
            failures.append(
                "Quarantined article hash mismatch: "
                f"{article_path}"
            )

        if not metadata_path.is_file():
            failures.append(
                "Quarantined metadata is missing: "
                f"{metadata_path}"
            )
        elif (
            sha256_file(metadata_path)
            != record.get("metadata_sha256")
        ):
            failures.append(
                "Quarantined metadata hash mismatch: "
                f"{metadata_path}"
            )

    for pass_record in pass_records:
        active_path = (
            udare_root
            / pass_record["article_path"]
        )

        if not active_path.is_file():
            failures.append(
                "A PASS article was removed from the active "
                f"UDARE Store: {active_path}"
            )

            continue

        before_hash = pass_article_hashes_before.get(
            pass_record["article_path"]
        )

        if (
            before_hash is not None
            and sha256_file(active_path) != before_hash
        ):
            failures.append(
                "A PASS article changed during quarantine: "
                f"{active_path}"
            )

    report_hashes_after = {
        "json": sha256_file(
            report_json_path
        ),
        "html": sha256_file(
            report_html_path
        ),
        "failures": sha256_file(
            report_failures_path
        ),
    }

    if report_hashes_before != report_hashes_after:
        failures.append(
            "One or more Phase 4.4.4 report artifacts changed."
        )

    if udare_manifest_path.is_file():
        udare_manifest = json.loads(
            udare_manifest_path.read_text(
                encoding="utf-8-sig",
            )
        )

        if udare_manifest.get("record_count") != 2219:
            failures.append(
                "UDARE manifest record_count is not 2,219."
            )

        if (
            udare_manifest.get(
                "article_document_count"
            )
            != 2219
        ):
            failures.append(
                "UDARE manifest article_document_count is "
                "not 2,219."
            )

        if (
            udare_manifest.get(
                "metadata_record_count"
            )
            != 2219
        ):
            failures.append(
                "UDARE manifest metadata_record_count is "
                "not 2,219."
            )

        quarantine_state = udare_manifest.get(
            "website_article_integrity_quarantine",
            {},
        )

        if quarantine_state.get("status") != "EXECUTED":
            failures.append(
                "UDARE manifest quarantine status is not "
                "EXECUTED."
            )

        if (
            quarantine_state.get(
                "quarantined_record_count"
            )
            != 3
        ):
            failures.append(
                "UDARE manifest quarantined count is not three."
            )

    if udare_index_path.is_file():
        active_index = udare_index_path.read_text(
            encoding="utf-8",
        )

        active_links = re.findall(
            r'href="articles/[^"]+\.html"',
            active_index,
            flags=re.IGNORECASE,
        )

        if len(active_links) != 2219:
            failures.append(
                "UDARE index does not contain 2,219 article links."
            )

        for record in failed_records:
            failed_filename = Path(
                record["article_path"]
            ).name

            if failed_filename in active_index:
                failures.append(
                    "A quarantined article remains in the active "
                    f"UDARE index: {failed_filename}"
                )

    if quarantine_index_path.is_file():
        quarantine_index = (
            quarantine_index_path.read_text(
                encoding="utf-8",
            )
        )

        for source_id in (
            EXPECTED_QUARANTINED_SOURCE_IDS
        ):
            if source_id not in quarantine_index:
                failures.append(
                    "Quarantine index does not contain source "
                    f"identity: {source_id}"
                )

    if manifest.get("execution_status") != "COMPLETE":
        failures.append(
            "Quarantine manifest execution status is not COMPLETE."
        )

    if manifest.get("active_record_count_after") != 2219:
        failures.append(
            "Quarantine manifest active count is not 2,219."
        )

    if manifest.get("quarantined_record_count") != 3:
        failures.append(
            "Quarantine manifest quarantined count is not three."
        )

    if manifest.get("deferred_upstream_count") != 3:
        failures.append(
            "Quarantine manifest deferred upstream count is "
            "not three."
        )

    print()
    print(
        f"Active UDARE articles:          "
        f"{len(active_article_paths)}"
    )
    print(
        f"Active UDARE metadata:          "
        f"{len(active_metadata_paths)}"
    )
    print(
        f"Quarantined articles:           "
        f"{len(quarantine_article_paths)}"
    )
    print(
        f"Quarantined metadata:           "
        f"{len(quarantine_metadata_paths)}"
    )
    print(
        f"Quarantine ledger records:      "
        f"{len(quarantine_records)}"
    )
    print(
        f"Deferred upstream pages:        "
        f"{manifest.get('deferred_upstream_count')}"
    )

    print()
    print("QUARANTINED ARTICLE SET")

    for record in quarantine_records:
        print(
            "  "
            f"{record.get('source_record_id')} | "
            f"{', '.join(record.get('consolidated_failure_reasons', []))}"
        )

    print()
    print(
        f"Quarantine manifest: {quarantine_manifest_path}"
    )
    print(
        f"Quarantine index:    {quarantine_index_path}"
    )
    print(
        f"Active UDARE index:  {udare_index_path}"
    )
    print()

    if failures:
        print("PHASE 4.4.5 VERIFICATION: FAIL")

        for failure in failures:
            print(f"  - {failure}")

        print("=" * 76)
        return 1

    print("PHASE 4.4.5 VERIFICATION: PASS")
    print(
        "All three failed article and metadata pairs were moved "
        "into the reversible quarantine store."
    )
    print(
        "The active UDARE Store now contains 2,219 PASS articles "
        "and 2,219 metadata records."
    )
    print(
        "No PASS article was modified, removed, or quarantined."
    )
    print("=" * 76)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
