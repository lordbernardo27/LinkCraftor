"""Read-only scan of the certified active ledger used by Article Validation."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


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

UDARE_ROOT = (
    DATA_ROOT
    / "udare_store"
    / WORKSPACE_ID
)

ARTICLE_ROOT = (
    UDARE_ROOT
    / "articles"
)

METADATA_ROOT = (
    UDARE_ROOT
    / "metadata"
)

CERTIFICATE_PATH = (
    DATA_ROOT
    / "website_article_integrity"
    / WORKSPACE_ID
    / "certification"
    / "website_article_integrity_certificate.json"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_certified_ledger_contract_scan.json"
)

IDENTIFIER_FIELDS = (
    "document_id",
    "html_id",
    "article_id",
    "record_id",
    "source_record_id",
)

PATH_FIELDS = (
    "article_document_path",
    "article_path",
    "document_path",
    "metadata_path",
    "article_filename",
)

HASH_FIELDS = (
    "article_body_sha256",
    "udare_article_body_sha256",
    "article_document_sha256",
    "document_sha256",
    "content_hash",
    "body_hash",
    "sha256",
)

URL_FIELDS = (
    "canonical_url",
    "source_url",
    "url",
)

COLLECTION_FIELDS = (
    "records",
    "articles",
    "entries",
    "ledger",
    "results",
    "certified_articles",
    "active_records",
    "certified_active_records",
)


def load_json(
    path: Path,
) -> Any:
    return json.loads(
        path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
    )


def resolve_reference_path(
    value: Any,
    *,
    reference_root: Path,
) -> Path:
    text = str(
        value or ""
    ).strip()

    if not text:
        return PROJECT_ROOT / "__missing_reference__"

    path = Path(text)

    if path.is_absolute():
        return path

    candidates = (
        PROJECT_ROOT / path,
        reference_root / path,
        DATA_ROOT / path,
    )

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    return (
        PROJECT_ROOT
        / path
    ).resolve()


def read_jsonl(
    path: Path,
) -> list[Any]:
    records: list[Any] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        errors="replace",
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
                    f"Invalid JSONL at line {line_number}: {exc}"
                ) from exc

    return records


def extract_records(
    value: Any,
) -> tuple[list[Any], str]:
    if isinstance(value, list):
        return value, "__root_list__"

    if not isinstance(value, dict):
        return [], "__unsupported_root__"

    for field in COLLECTION_FIELDS:
        candidate = value.get(field)

        if isinstance(candidate, list):
            return candidate, field

        if isinstance(candidate, dict):
            return list(
                candidate.values()
            ), field

    dictionary_values = list(
        value.values()
    )

    if (
        dictionary_values
        and all(
            isinstance(item, dict)
            for item in dictionary_values
        )
    ):
        return (
            dictionary_values,
            "__root_mapping_values__",
        )

    return [], "__no_collection_found__"


def load_ledger(
    path: Path,
) -> tuple[Any, list[Any], str]:
    if path.suffix.lower() == ".jsonl":
        records = read_jsonl(
            path
        )

        return (
            records,
            records,
            "__jsonl__",
        )

    value = load_json(
        path
    )

    records, collection_field = (
        extract_records(value)
    )

    return (
        value,
        records,
        collection_field,
    )


def first_nonempty(
    record: dict[str, Any],
    fields: Iterable[str],
) -> str:
    for field in fields:
        value = str(
            record.get(field)
            or ""
        ).strip()

        if value:
            return value

    return ""


def canonical_identifier(
    record: dict[str, Any],
) -> str:
    return first_nonempty(
        record,
        IDENTIFIER_FIELDS,
    )


def summarize_records(
    records: list[Any],
) -> dict[str, Any]:
    key_counts: Counter[str] = Counter()

    identifier_presence: Counter[str] = (
        Counter()
    )

    path_presence: Counter[str] = Counter()
    hash_presence: Counter[str] = Counter()
    url_presence: Counter[str] = Counter()

    identifiers: list[str] = []
    missing_identifier_count = 0
    object_record_count = 0

    for record in records:
        if not isinstance(
            record,
            dict,
        ):
            continue

        object_record_count += 1

        for key in record:
            key_counts[
                str(key)
            ] += 1

        for field in IDENTIFIER_FIELDS:
            if str(
                record.get(field)
                or ""
            ).strip():
                identifier_presence[
                    field
                ] += 1

        for field in PATH_FIELDS:
            if str(
                record.get(field)
                or ""
            ).strip():
                path_presence[
                    field
                ] += 1

        for field in HASH_FIELDS:
            if str(
                record.get(field)
                or ""
            ).strip():
                hash_presence[
                    field
                ] += 1

        for field in URL_FIELDS:
            if str(
                record.get(field)
                or ""
            ).strip():
                url_presence[
                    field
                ] += 1

        identifier = canonical_identifier(
            record
        )

        if identifier:
            identifiers.append(
                identifier
            )
        else:
            missing_identifier_count += 1

    identifier_counts = Counter(
        identifiers
    )

    duplicate_identifiers = {
        identifier: count
        for identifier, count
        in identifier_counts.items()
        if count > 1
    }

    return {
        "row_count": len(records),
        "object_record_count": (
            object_record_count
        ),
        "top_keys": dict(
            key_counts.most_common(100)
        ),
        "identifier_field_presence": dict(
            identifier_presence
        ),
        "path_field_presence": dict(
            path_presence
        ),
        "hash_field_presence": dict(
            hash_presence
        ),
        "url_field_presence": dict(
            url_presence
        ),
        "canonical_identifier_count": len(
            identifiers
        ),
        "unique_identifier_count": len(
            identifier_counts
        ),
        "missing_identifier_count": (
            missing_identifier_count
        ),
        "duplicate_identifier_count": len(
            duplicate_identifiers
        ),
        "duplicate_identifier_sample": dict(
            list(
                sorted(
                    duplicate_identifiers.items()
                )
            )[:20]
        ),
    }


def sample_records(
    records: list[Any],
    limit: int = 3,
) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []

    for record in records:
        if not isinstance(
            record,
            dict,
        ):
            continue

        samples.append(
            {
                "keys": sorted(
                    str(key)
                    for key in record.keys()
                ),
                "identifier_values": {
                    field: record.get(field)
                    for field in IDENTIFIER_FIELDS
                    if field in record
                },
                "path_values": {
                    field: record.get(field)
                    for field in PATH_FIELDS
                    if field in record
                },
                "hash_values": {
                    field: record.get(field)
                    for field in HASH_FIELDS
                    if field in record
                },
                "url_values": {
                    field: record.get(field)
                    for field in URL_FIELDS
                    if field in record
                },
            }
        )

        if len(samples) >= limit:
            break

    return samples


def record_identifier_set(
    records: list[Any],
) -> set[str]:
    return {
        identifier
        for record in records
        if isinstance(record, dict)
        for identifier in [
            canonical_identifier(record)
        ]
        if identifier
    }


def sample_udare_loads(
    records: list[Any],
) -> list[dict[str, Any]]:
    from backend.server.stores.udare_store import (
        load_udare_article_document_v1,
    )

    results: list[dict[str, Any]] = []

    for record in records:
        if not isinstance(
            record,
            dict,
        ):
            continue

        document_id = str(
            record.get("document_id")
            or ""
        ).strip()

        if not document_id:
            continue

        try:
            loaded = (
                load_udare_article_document_v1(
                    WORKSPACE_ID,
                    document_id,
                )
            )

            results.append(
                {
                    "document_id": document_id,
                    "load_status": "PASS",
                    "result_type": type(
                        loaded
                    ).__name__,
                    "top_level_keys": (
                        sorted(
                            str(key)
                            for key
                            in loaded.keys()
                        )
                        if isinstance(
                            loaded,
                            dict,
                        )
                        else []
                    ),
                }
            )

        except Exception as exc:
            results.append(
                {
                    "document_id": document_id,
                    "load_status": "FAIL",
                    "error": (
                        f"{type(exc).__name__}: {exc}"
                    ),
                }
            )

        if len(results) >= 3:
            break

    return results


def metadata_samples() -> list[dict[str, Any]]:
    if not METADATA_ROOT.is_dir():
        return []

    results: list[dict[str, Any]] = []

    for path in sorted(
        METADATA_ROOT.glob("*.json")
    )[:3]:
        try:
            value = load_json(
                path
            )

            results.append(
                {
                    "path": str(
                        path.relative_to(
                            PROJECT_ROOT
                        )
                    ),
                    "root_type": type(
                        value
                    ).__name__,
                    "top_level_keys": (
                        sorted(
                            str(key)
                            for key
                            in value.keys()
                        )
                        if isinstance(
                            value,
                            dict,
                        )
                        else []
                    ),
                }
            )

        except Exception as exc:
            results.append(
                {
                    "path": str(path),
                    "error": (
                        f"{type(exc).__name__}: {exc}"
                    ),
                }
            )

    return results


def main() -> int:
    print()
    print("=" * 96)
    print(
        "ARTICLE VALIDATION — CERTIFIED ACTIVE LEDGER CONTRACT SCAN"
    )
    print("=" * 96)

    if not CERTIFICATE_PATH.is_file():
        raise FileNotFoundError(
            f"Integrity certificate missing: {CERTIFICATE_PATH}"
        )

    certificate = load_json(
        CERTIFICATE_PATH
    )

    coverage = certificate.get(
        "coverage",
        {}
    )

    active_ledger_path = (
        resolve_reference_path(
            certificate.get(
                "certified_active_ledger_path"
            ),
            reference_root=(
                CERTIFICATE_PATH.parent
            ),
        )
    )

    quarantine_ledger_path = (
        resolve_reference_path(
            certificate.get(
                "certified_quarantine_ledger_path"
            ),
            reference_root=(
                CERTIFICATE_PATH.parent
            ),
        )
    )

    if not active_ledger_path.is_file():
        raise FileNotFoundError(
            "Certified active ledger missing: "
            f"{active_ledger_path}"
        )

    (
        active_root,
        active_records,
        active_collection_field,
    ) = load_ledger(
        active_ledger_path
    )

    active_summary = summarize_records(
        active_records
    )

    quarantine_records: list[Any] = []
    quarantine_collection_field = (
        "__missing__"
    )

    if quarantine_ledger_path.is_file():
        (
            _,
            quarantine_records,
            quarantine_collection_field,
        ) = load_ledger(
            quarantine_ledger_path
        )

    quarantine_summary = summarize_records(
        quarantine_records
    )

    active_identifiers = (
        record_identifier_set(
            active_records
        )
    )

    quarantine_identifiers = (
        record_identifier_set(
            quarantine_records
        )
    )

    overlap = sorted(
        active_identifiers
        & quarantine_identifiers
    )

    article_document_count = (
        len(
            list(
                ARTICLE_ROOT.glob(
                    "*.html"
                )
            )
        )
        if ARTICLE_ROOT.is_dir()
        else 0
    )

    metadata_document_count = (
        len(
            list(
                METADATA_ROOT.glob(
                    "*.json"
                )
            )
        )
        if METADATA_ROOT.is_dir()
        else 0
    )

    certified_active_count = (
        coverage.get(
            "active_certified_count"
        )
    )

    certified_quarantine_count = (
        coverage.get(
            "quarantined_count"
        )
    )

    contract_passed = all(
        (
            certificate.get(
                "certification_status"
            )
            == "CERTIFIED",

            certified_active_count
            == 2219,

            len(active_records)
            == 2219,

            article_document_count
            == 2219,

            active_summary[
                "missing_identifier_count"
            ]
            == 0,

            active_summary[
                "duplicate_identifier_count"
            ]
            == 0,

            len(overlap) == 0,
        )
    )

    report = {
        "schema_version": (
            "article_validation_"
            "certified_ledger_contract_scan_v1"
        ),
        "scan_mode": "READ_ONLY",
        "workspace_id": WORKSPACE_ID,
        "certificate_path": str(
            CERTIFICATE_PATH
        ),
        "certificate_status": (
            certificate.get(
                "certification_status"
            )
        ),
        "certificate_id": (
            certificate.get(
                "certificate_id"
            )
        ),
        "coverage": coverage,
        "active_ledger_path": str(
            active_ledger_path
        ),
        "active_ledger_root_type": type(
            active_root
        ).__name__,
        "active_collection_field": (
            active_collection_field
        ),
        "active_summary": active_summary,
        "active_record_samples": (
            sample_records(
                active_records
            )
        ),
        "quarantine_ledger_path": str(
            quarantine_ledger_path
        ),
        "quarantine_collection_field": (
            quarantine_collection_field
        ),
        "quarantine_summary": (
            quarantine_summary
        ),
        "active_quarantine_identifier_overlap_count": (
            len(overlap)
        ),
        "active_quarantine_identifier_overlap_sample": (
            overlap[:20]
        ),
        "active_html_document_count": (
            article_document_count
        ),
        "metadata_document_count": (
            metadata_document_count
        ),
        "metadata_samples": (
            metadata_samples()
        ),
        "udare_loader_samples": (
            sample_udare_loads(
                active_records
            )
        ),
        "contract_status": (
            "PASS"
            if contract_passed
            else "FAIL"
        ),
        "source_files_modified": [],
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        "Certificate status:                    "
        + str(
            certificate.get(
                "certification_status"
            )
        )
    )

    print(
        "Certified active count:                "
        + str(
            certified_active_count
        )
    )

    print(
        "Active ledger records:                 "
        + str(
            len(active_records)
        )
    )

    print(
        "Active UDARE HTML documents:           "
        + str(
            article_document_count
        )
    )

    print(
        "UDARE metadata documents:              "
        + str(
            metadata_document_count
        )
    )

    print(
        "Certified quarantine count:            "
        + str(
            certified_quarantine_count
        )
    )

    print(
        "Quarantine ledger records:             "
        + str(
            len(quarantine_records)
        )
    )

    print(
        "Active records missing identifiers:    "
        + str(
            active_summary[
                "missing_identifier_count"
            ]
        )
    )

    print(
        "Duplicate active identifiers:          "
        + str(
            active_summary[
                "duplicate_identifier_count"
            ]
        )
    )

    print(
        "Active/quarantine identifier overlap:  "
        + str(
            len(overlap)
        )
    )

    print()
    print(
        "ACTIVE LEDGER PATH"
    )

    print(
        "  "
        + str(
            active_ledger_path
        )
    )

    print(
        "  Collection field: "
        + active_collection_field
    )

    print()
    print(
        "IDENTIFIER FIELD COVERAGE"
    )

    for field, count in (
        active_summary[
            "identifier_field_presence"
        ].items()
    ):
        print(
            f"  {field}: {count}"
        )

    print()
    print(
        "HASH FIELD COVERAGE"
    )

    if active_summary[
        "hash_field_presence"
    ]:
        for field, count in (
            active_summary[
                "hash_field_presence"
            ].items()
        ):
            print(
                f"  {field}: {count}"
            )
    else:
        print(
            "  No direct hash fields found "
            "in the active ledger."
        )

    print()
    print(
        "PATH FIELD COVERAGE"
    )

    if active_summary[
        "path_field_presence"
    ]:
        for field, count in (
            active_summary[
                "path_field_presence"
            ].items()
        ):
            print(
                f"  {field}: {count}"
            )
    else:
        print(
            "  No direct path fields found "
            "in the active ledger."
        )

    print()
    print(
        "TOP ACTIVE LEDGER KEYS"
    )

    for field, count in list(
        active_summary[
            "top_keys"
        ].items()
    )[:50]:
        print(
            f"  {field}: {count}"
        )

    print()
    print(
        "UDARE LOADER SAMPLE"
    )

    loader_samples = report[
        "udare_loader_samples"
    ]

    if loader_samples:
        for sample in loader_samples:
            print(
                "  "
                + str(
                    sample.get(
                        "document_id"
                    )
                )
                + ": "
                + str(
                    sample.get(
                        "load_status"
                    )
                )
            )
    else:
        print(
            "  No document_id values were available "
            "for loader testing."
        )

    print()
    print(
        "CONTRACT STATUS: "
        + report[
            "contract_status"
        ]
    )

    print()
    print(
        "Report: "
        + str(
            REPORT_PATH
        )
    )

    print(
        "Source files modified: 0"
    )

    print("=" * 96)

    return (
        0
        if contract_passed
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
