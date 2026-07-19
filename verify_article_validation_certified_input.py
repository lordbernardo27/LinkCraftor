"""Verify the certified Article Validation input loader."""

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

from backend.server.article_validation.certified_article_validation_input import (
    load_certified_article_payload,
    load_certified_article_validation_input,
)


WORKSPACE_ID = "ws_whattoexpect_com"

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

UDARE_ROOT = (
    DATA_ROOT
    / "udare_store"
    / WORKSPACE_ID
)

INTEGRITY_ROOT = (
    DATA_ROOT
    / "website_article_integrity"
    / WORKSPACE_ID
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_certified_input_verification.json"
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
            item
            for item in root.rglob("*")
            if item.is_file()
        ),
        key=lambda item: item.as_posix(),
    ):
        digest.update(
            path.relative_to(
                root
            ).as_posix().encode(
                "utf-8"
            )
        )

        digest.update(b"\x00")

        digest.update(
            sha256_file(path).encode(
                "ascii"
            )
        )

        digest.update(b"\n")

    return digest.hexdigest()


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


def main() -> int:
    print()
    print("=" * 96)
    print(
        "ARTICLE VALIDATION — CERTIFIED INPUT LOADER VERIFICATION"
    )
    print("=" * 96)

    failures: list[str] = []

    udare_before = (
        directory_fingerprint(
            UDARE_ROOT
        )
    )

    integrity_before = (
        directory_fingerprint(
            INTEGRITY_ROOT
        )
    )

    loaded = (
        load_certified_article_validation_input(
            WORKSPACE_ID,
            expected_active_count=2219,
        )
    )

    records = loaded.get(
        "records",
        [],
    )

    if loaded.get(
        "certificate_status"
    ) != "CERTIFIED":
        failures.append(
            "Integrity certificate was not CERTIFIED."
        )

    if loaded.get(
        "certified_active_count"
    ) != 2219:
        failures.append(
            "Certified active count was not 2,219."
        )

    if loaded.get(
        "verified_record_count"
    ) != 2219:
        failures.append(
            "Verified record count was not 2,219."
        )

    if len(records) != 2219:
        failures.append(
            "Returned descriptor count was not 2,219."
        )

    identifiers = [
        str(
            record.get(
                "source_record_id"
            )
            or ""
        )
        for record in records
        if isinstance(
            record,
            dict,
        )
    ]

    if len(
        set(identifiers)
    ) != 2219:
        failures.append(
            "Certified descriptors were not uniquely identified."
        )

    if loaded.get(
        "article_bodies_loaded"
    ) is not False:
        failures.append(
            "Bulk loader unexpectedly loaded article bodies."
        )

    if loaded.get(
        "article_bodies_copied"
    ) is not False:
        failures.append(
            "Bulk loader unexpectedly copied article bodies."
        )

    payload_samples: list[
        dict[str, Any]
    ] = []

    sample_positions = (
        0,
        len(records) // 2,
        len(records) - 1,
    )

    for position in sample_positions:
        descriptor = records[
            position
        ]

        payload = (
            load_certified_article_payload(
                descriptor
            )
        )

        article_html = str(
            payload.get(
                "article_html"
            )
            or ""
        )

        metadata = payload.get(
            "metadata"
        )

        if not article_html.strip():
            failures.append(
                "A sampled certified article body was empty: "
                + str(
                    payload.get(
                        "source_record_id"
                    )
                )
            )

        if not isinstance(
            metadata,
            dict,
        ):
            failures.append(
                "A sampled metadata payload was not an object."
            )

            metadata_keys: list[str] = []

        else:
            metadata_keys = sorted(
                str(key)
                for key in metadata.keys()
            )

        payload_samples.append(
            {
                "source_record_id": (
                    payload.get(
                        "source_record_id"
                    )
                ),
                "article_character_count": len(
                    article_html
                ),
                "article_sha256": (
                    payload.get(
                        "article_sha256"
                    )
                ),
                "metadata_sha256": (
                    payload.get(
                        "metadata_sha256"
                    )
                ),
                "metadata_keys": (
                    metadata_keys
                ),
            }
        )

    udare_after = (
        directory_fingerprint(
            UDARE_ROOT
        )
    )

    integrity_after = (
        directory_fingerprint(
            INTEGRITY_ROOT
        )
    )

    udare_unchanged = (
        udare_before
        == udare_after
    )

    integrity_unchanged = (
        integrity_before
        == integrity_after
    )

    if not udare_unchanged:
        failures.append(
            "UDARE Store changed during input verification."
        )

    if not integrity_unchanged:
        failures.append(
            "Website Article Integrity artifacts changed "
            "during input verification."
        )

    report = {
        "schema_version": (
            "article_validation_"
            "certified_input_verification_v1"
        ),
        "verification_status": (
            "PASS"
            if not failures
            else "FAIL"
        ),
        "workspace_id": WORKSPACE_ID,
        "certificate_id": loaded.get(
            "certificate_id"
        ),
        "certificate_status": loaded.get(
            "certificate_status"
        ),
        "certified_active_count": loaded.get(
            "certified_active_count"
        ),
        "verified_record_count": loaded.get(
            "verified_record_count"
        ),
        "integrity_quarantined_count": loaded.get(
            "integrity_quarantined_count"
        ),
        "deferred_upstream_count": loaded.get(
            "deferred_upstream_count"
        ),
        "integrity_status_counts": loaded.get(
            "integrity_status_counts"
        ),
        "metadata_key_coverage": loaded.get(
            "metadata_key_coverage"
        ),
        "candidate_metadata_field_coverage": loaded.get(
            "candidate_metadata_field_coverage"
        ),
        "sample_payloads": payload_samples,
        "bulk_article_bodies_loaded": loaded.get(
            "article_bodies_loaded"
        ),
        "article_bodies_copied": loaded.get(
            "article_bodies_copied"
        ),
        "udare_store_unchanged": (
            udare_unchanged
        ),
        "integrity_artifacts_unchanged": (
            integrity_unchanged
        ),
        "failures": failures,
    }

    write_json(
        REPORT_PATH,
        report,
    )

    print()
    print(
        "Certificate status:                 "
        + str(
            report[
                "certificate_status"
            ]
        )
    )

    print(
        "Certified active count:             "
        + str(
            report[
                "certified_active_count"
            ]
        )
    )

    print(
        "Verified certified descriptors:     "
        + str(
            report[
                "verified_record_count"
            ]
        )
    )

    print(
        "Bulk article bodies loaded:         "
        + str(
            report[
                "bulk_article_bodies_loaded"
            ]
        )
    )

    print(
        "Article bodies copied:              "
        + str(
            report[
                "article_bodies_copied"
            ]
        )
    )

    print(
        "UDARE Store unchanged:              "
        + (
            "PASS"
            if udare_unchanged
            else "FAIL"
        )
    )

    print(
        "Integrity artifacts unchanged:      "
        + (
            "PASS"
            if integrity_unchanged
            else "FAIL"
        )
    )

    print()
    print(
        "INTEGRITY STATUS COUNTS"
    )

    for status, count in (
        report.get(
            "integrity_status_counts",
            {}
        ).items()
    ):
        print(
            f"  {status}: {count}"
        )

    print()
    print(
        "CANDIDATE METADATA FIELD COVERAGE"
    )

    for field, count in (
        report.get(
            "candidate_metadata_field_coverage",
            {}
        ).items()
    ):
        print(
            f"  {field}: {count}"
        )

    print()
    print(
        "SAMPLED PAYLOADS"
    )

    for sample in payload_samples:
        print(
            "  "
            + str(
                sample[
                    "source_record_id"
                ]
            )
            + ": "
            + str(
                sample[
                    "article_character_count"
                ]
            )
            + " characters"
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
            "ARTICLE VALIDATION CERTIFIED "
            "INPUT LOADER VERIFICATION: FAIL"
        )

        for failure in failures:
            print(
                "  - "
                + failure
            )

        print("=" * 96)

        return 1

    print(
        "ARTICLE VALIDATION CERTIFIED "
        "INPUT LOADER VERIFICATION: PASS"
    )

    print(
        "All 2,219 certified active article and metadata "
        "files matched their certified SHA-256 hashes."
    )

    print(
        "No Raw HTML was read, no article was reconstructed, "
        "and no integrity stage was rerun."
    )

    print(
        "No article body was copied or modified."
    )

    print("=" * 96)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
