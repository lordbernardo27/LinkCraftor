"""Metadata-only Article Validation Store v3."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from uuid import uuid4


STORE_VERSION = (
    "article_validation_store_v3_metadata_only"
)

LEDGER_SCHEMA_VERSION = (
    "article_validation_ledger_v3"
)

REPORT_SCHEMA_VERSION = (
    "article_validation_report_v3"
)

PROJECT_ROOT = (
    Path(__file__).resolve().parents[3]
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

PROHIBITED_BODY_FIELDS = {
    "article_body",
    "article_html",
    "content_body",
    "cleaned_article_text",
    "body_text",
    "raw_html",
    "selected_html",
    "full_text",
}

REQUIRED_RESULT_FIELDS = {
    "source_record_id",
    "status",
    "passed",
    "validation_version",
    "article_sha256",
    "metadata_sha256",
    "eligible_for_wuc",
    "article_body_included",
    "article_body_modified",
}


def _utc_now(
) -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _safe_workspace_id(
    workspace_id: str,
) -> str:
    value = str(
        workspace_id or ""
    ).strip()

    if not value:
        raise ValueError(
            "workspace_id is required."
        )

    safe = "".join(
        character
        if (
            character.isalnum()
            or character in {"-", "_", "."}
        )
        else "_"
        for character in value
    ).strip("._")

    if not safe:
        raise ValueError(
            "workspace_id is invalid."
        )

    return safe


def _valid_sha256(
    value: Any,
) -> bool:
    return bool(
        re.fullmatch(
            r"[0-9a-fA-F]{64}",
            str(value or "").strip(),
        )
    )


def _find_prohibited_fields(
    value: Any,
    *,
    prefix: str = "",
) -> list[str]:
    findings: list[str] = []

    if isinstance(
        value,
        Mapping,
    ):
        for key, item in value.items():
            key_text = str(key)

            field_path = (
                f"{prefix}.{key_text}"
                if prefix
                else key_text
            )

            if (
                key_text.casefold()
                in PROHIBITED_BODY_FIELDS
            ):
                findings.append(
                    field_path
                )

            findings.extend(
                _find_prohibited_fields(
                    item,
                    prefix=field_path,
                )
            )

    elif isinstance(
        value,
        (list, tuple),
    ):
        for index, item in enumerate(
            value
        ):
            findings.extend(
                _find_prohibited_fields(
                    item,
                    prefix=(
                        f"{prefix}[{index}]"
                    ),
                )
            )

    return findings


def _atomic_write_json(
    path: Path,
    payload: Mapping[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.with_name(
        path.name
        + "."
        + uuid4().hex
        + ".tmp"
    )

    temporary_path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary_path.replace(
        path
    )


def _atomic_write_jsonl(
    path: Path,
    records: Iterable[
        Mapping[str, Any]
    ],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.with_name(
        path.name
        + "."
        + uuid4().hex
        + ".tmp"
    )

    with temporary_path.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        for record in records:
            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )

            handle.write("\n")

    temporary_path.replace(
        path
    )


def _load_json(
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


def _load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    if not path.is_file():
        return []

    records: list[
        dict[str, Any]
    ] = []

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

            try:
                value = json.loads(
                    line
                )

            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    "Invalid Article Validation JSONL "
                    f"at line {line_number}: {exc}"
                ) from exc

            if not isinstance(
                value,
                dict,
            ):
                raise RuntimeError(
                    "Article Validation record "
                    f"{line_number} is not an object."
                )

            records.append(
                value
            )

    return records


def article_validation_store_paths_v3(
    workspace_id: str,
) -> dict[str, Path]:
    workspace_id = _safe_workspace_id(
        workspace_id
    )

    root = (
        DATA_ROOT
        / "article_validation"
        / workspace_id
    )

    return {
        "root":
            root,

        "results":
            root
            / "results"
            / "article_validation_results.jsonl",

        "ledger":
            root
            / "ledger"
            / "article_validation_ledger.json",

        "report":
            root
            / "reports"
            / "article_validation_report.json",
    }


def validate_article_validation_result_v3(
    result: Mapping[str, Any],
) -> None:
    if not isinstance(
        result,
        Mapping,
    ):
        raise TypeError(
            "Article Validation result must be an object."
        )

    missing_fields = sorted(
        field
        for field in REQUIRED_RESULT_FIELDS
        if field not in result
    )

    if missing_fields:
        raise ValueError(
            "Article Validation result is missing fields: "
            + ", ".join(
                missing_fields
            )
        )

    prohibited_fields = (
        _find_prohibited_fields(
            result
        )
    )

    if prohibited_fields:
        raise ValueError(
            "Article Validation result contains "
            "prohibited article-body fields: "
            + ", ".join(
                prohibited_fields
            )
        )

    source_record_id = str(
        result.get(
            "source_record_id"
        )
        or ""
    ).strip()

    if not source_record_id:
        raise ValueError(
            "source_record_id is required."
        )

    status = str(
        result.get(
            "status"
        )
        or ""
    ).strip().upper()

    if status not in {
        "PASS",
        "FAIL",
    }:
        raise ValueError(
            f"Invalid validation status: {status}"
        )

    passed = result.get(
        "passed"
    )

    if not isinstance(
        passed,
        bool,
    ):
        raise ValueError(
            "passed must be Boolean."
        )

    if (
        passed
        != (status == "PASS")
    ):
        raise ValueError(
            "passed and status are inconsistent."
        )

    eligible_for_wuc = result.get(
        "eligible_for_wuc"
    )

    if not isinstance(
        eligible_for_wuc,
        bool,
    ):
        raise ValueError(
            "eligible_for_wuc must be Boolean."
        )

    if eligible_for_wuc != passed:
        raise ValueError(
            "eligible_for_wuc must match passed."
        )

    if (
        result.get(
            "article_body_included"
        )
        is not False
    ):
        raise ValueError(
            "article_body_included must be False."
        )

    if (
        result.get(
            "article_body_modified"
        )
        is not False
    ):
        raise ValueError(
            "article_body_modified must be False."
        )

    if not _valid_sha256(
        result.get(
            "article_sha256"
        )
    ):
        raise ValueError(
            "article_sha256 is invalid."
        )

    if not _valid_sha256(
        result.get(
            "metadata_sha256"
        )
    ):
        raise ValueError(
            "metadata_sha256 is invalid."
        )


def initialize_article_validation_store_v3(
    *,
    workspace_id: str,
    run_id: str,
    integrity_certificate_id: str,
    expected_input_count: int,
    overwrite: bool = False,
) -> dict[str, Any]:
    workspace_id = _safe_workspace_id(
        workspace_id
    )

    run_id = str(
        run_id or ""
    ).strip()

    integrity_certificate_id = str(
        integrity_certificate_id or ""
    ).strip()

    if not run_id:
        raise ValueError(
            "run_id is required."
        )

    if not integrity_certificate_id:
        raise ValueError(
            "integrity_certificate_id is required."
        )

    if int(
        expected_input_count
    ) < 0:
        raise ValueError(
            "expected_input_count cannot be negative."
        )

    paths = (
        article_validation_store_paths_v3(
            workspace_id
        )
    )

    if (
        paths["root"].exists()
        and not overwrite
    ):
        raise FileExistsError(
            "Article Validation store already exists: "
            f"{paths['root']}"
        )

    paths["results"].parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths["ledger"].parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths["report"].parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    _atomic_write_jsonl(
        paths["results"],
        [],
    )

    generated_at = _utc_now()

    ledger = {
        "schema_version":
            LEDGER_SCHEMA_VERSION,

        "store_version":
            STORE_VERSION,

        "workspace_id":
            workspace_id,

        "run_id":
            run_id,

        "integrity_certificate_id":
            integrity_certificate_id,

        "expected_input_count":
            int(
                expected_input_count
            ),

        "processed_count":
            0,

        "pass_count":
            0,

        "fail_count":
            0,

        "status":
            "INITIALIZED",

        "article_bodies_stored":
            False,

        "article_bodies_modified":
            False,

        "created_at":
            generated_at,

        "updated_at":
            generated_at,
    }

    _atomic_write_json(
        paths["ledger"],
        ledger,
    )

    return {
        "paths":
            {
                name: str(path)
                for name, path
                in paths.items()
            },

        "ledger":
            ledger,
    }


def append_article_validation_results_v3(
    *,
    workspace_id: str,
    run_id: str,
    results: Iterable[
        Mapping[str, Any]
    ],
    expected_previous_count: int | None = None,
) -> dict[str, Any]:
    paths = (
        article_validation_store_paths_v3(
            workspace_id
        )
    )

    if not paths["ledger"].is_file():
        raise FileNotFoundError(
            "Article Validation ledger does not exist."
        )

    ledger = _load_json(
        paths["ledger"]
    )

    if str(
        ledger.get(
            "run_id"
        )
        or ""
    ) != str(
        run_id or ""
    ):
        raise RuntimeError(
            "Article Validation run_id mismatch."
        )

    if ledger.get(
        "status"
    ) not in {
        "INITIALIZED",
        "RUNNING",
    }:
        raise RuntimeError(
            "Article Validation store is not writable: "
            + str(
                ledger.get(
                    "status"
                )
            )
        )

    existing_records = (
        _load_jsonl(
            paths["results"]
        )
    )

    if (
        expected_previous_count
        is not None
        and len(existing_records)
        != int(
            expected_previous_count
        )
    ):
        raise RuntimeError(
            "Previous result count mismatch: "
            f"{len(existing_records)} != "
            f"{int(expected_previous_count)}"
        )

    existing_identifiers = {
        str(
            record.get(
                "source_record_id"
            )
            or ""
        )
        for record in existing_records
    }

    new_records: list[
        dict[str, Any]
    ] = []

    new_identifiers: set[str] = set()

    for supplied_result in results:
        result = dict(
            supplied_result
        )

        validate_article_validation_result_v3(
            result
        )

        source_record_id = str(
            result[
                "source_record_id"
            ]
        )

        if source_record_id in existing_identifiers:
            raise RuntimeError(
                "Duplicate Article Validation result: "
                f"{source_record_id}"
            )

        if source_record_id in new_identifiers:
            raise RuntimeError(
                "Duplicate result inside appended batch: "
                f"{source_record_id}"
            )

        new_identifiers.add(
            source_record_id
        )

        result[
            "stored_at"
        ] = _utc_now()

        new_records.append(
            result
        )

    combined_records = (
        existing_records
        + new_records
    )

    expected_input_count = int(
        ledger.get(
            "expected_input_count"
        )
        or 0
    )

    if (
        len(combined_records)
        > expected_input_count
    ):
        raise RuntimeError(
            "Article Validation result count exceeds "
            "the expected input population."
        )

    _atomic_write_jsonl(
        paths["results"],
        combined_records,
    )

    status_counts = Counter(
        str(
            record.get(
                "status"
            )
            or ""
        ).upper()
        for record in combined_records
    )

    ledger[
        "processed_count"
    ] = len(
        combined_records
    )

    ledger[
        "pass_count"
    ] = status_counts.get(
        "PASS",
        0,
    )

    ledger[
        "fail_count"
    ] = status_counts.get(
        "FAIL",
        0,
    )

    ledger["status"] = "RUNNING"
    ledger["updated_at"] = _utc_now()

    _atomic_write_json(
        paths["ledger"],
        ledger,
    )

    return {
        "appended_count":
            len(
                new_records
            ),

        "processed_count":
            len(
                combined_records
            ),

        "expected_input_count":
            expected_input_count,

        "pass_count":
            ledger[
                "pass_count"
            ],

        "fail_count":
            ledger[
                "fail_count"
            ],
    }


def finalize_article_validation_store_v3(
    *,
    workspace_id: str,
    run_id: str,
) -> dict[str, Any]:
    paths = (
        article_validation_store_paths_v3(
            workspace_id
        )
    )

    ledger = _load_json(
        paths["ledger"]
    )

    if str(
        ledger.get(
            "run_id"
        )
        or ""
    ) != str(
        run_id or ""
    ):
        raise RuntimeError(
            "Article Validation run_id mismatch."
        )

    records = _load_jsonl(
        paths["results"]
    )

    expected_input_count = int(
        ledger.get(
            "expected_input_count"
        )
        or 0
    )

    if (
        len(records)
        != expected_input_count
    ):
        raise RuntimeError(
            "Cannot finalize an incomplete validation store: "
            f"{len(records)} != {expected_input_count}"
        )

    identifiers = [
        str(
            record.get(
                "source_record_id"
            )
            or ""
        )
        for record in records
    ]

    if len(
        set(identifiers)
    ) != len(identifiers):
        raise RuntimeError(
            "Duplicate identifiers exist in the final store."
        )

    status_counts = Counter(
        str(
            record.get(
                "status"
            )
            or ""
        ).upper()
        for record in records
    )

    grade_counts = Counter(
        str(
            record.get(
                "quality_grade"
            )
            or "MISSING"
        )
        for record in records
    )

    warning_counts: Counter[str] = Counter()
    rejection_counts: Counter[str] = Counter()

    for record in records:
        for warning in (
            record.get(
                "warnings"
            )
            or []
        ):
            warning_counts[
                str(warning)
            ] += 1

        for reason in (
            record.get(
                "rejection_reasons"
            )
            or []
        ):
            rejection_counts[
                str(reason)
            ] += 1

    generated_at = _utc_now()

    report = {
        "schema_version":
            REPORT_SCHEMA_VERSION,

        "store_version":
            STORE_VERSION,

        "workspace_id":
            ledger[
                "workspace_id"
            ],

        "run_id":
            ledger[
                "run_id"
            ],

        "integrity_certificate_id":
            ledger[
                "integrity_certificate_id"
            ],

        "expected_input_count":
            expected_input_count,

        "processed_count":
            len(records),

        "pass_count":
            status_counts.get(
                "PASS",
                0,
            ),

        "fail_count":
            status_counts.get(
                "FAIL",
                0,
            ),

        "quality_grade_counts":
            dict(
                grade_counts
            ),

        "warning_counts":
            dict(
                warning_counts
            ),

        "rejection_reason_counts":
            dict(
                rejection_counts
            ),

        "results_path":
            str(
                paths["results"]
            ),

        "article_bodies_stored":
            False,

        "article_bodies_modified":
            False,

        "eligible_for_wuc_count":
            sum(
                record.get(
                    "eligible_for_wuc"
                )
                is True
                for record in records
            ),

        "generated_at":
            generated_at,
    }

    _atomic_write_json(
        paths["report"],
        report,
    )

    ledger[
        "processed_count"
    ] = len(records)

    ledger[
        "pass_count"
    ] = report[
        "pass_count"
    ]

    ledger[
        "fail_count"
    ] = report[
        "fail_count"
    ]

    ledger["status"] = "COMPLETED"
    ledger["completed_at"] = generated_at
    ledger["updated_at"] = generated_at

    _atomic_write_json(
        paths["ledger"],
        ledger,
    )

    return report


def load_article_validation_store_v3(
    workspace_id: str,
) -> dict[str, Any]:
    paths = (
        article_validation_store_paths_v3(
            workspace_id
        )
    )

    if not paths["ledger"].is_file():
        raise FileNotFoundError(
            "Article Validation ledger does not exist."
        )

    ledger = _load_json(
        paths["ledger"]
    )

    records = _load_jsonl(
        paths["results"]
    )

    articles: dict[
        str,
        dict[str, Any],
    ] = {}

    for record in records:
        validate_article_validation_result_v3(
            record
        )

        source_record_id = str(
            record[
                "source_record_id"
            ]
        )

        if source_record_id in articles:
            raise RuntimeError(
                "Duplicate Article Validation result: "
                f"{source_record_id}"
            )

        articles[
            source_record_id
        ] = record

    report = (
        _load_json(
            paths["report"]
        )
        if paths["report"].is_file()
        else None
    )

    return {
        "store_version":
            STORE_VERSION,

        "workspace_id":
            ledger.get(
                "workspace_id"
            ),

        "ledger":
            ledger,

        "report":
            report,

        "article_count":
            len(articles),

        "articles":
            articles,

        "paths":
            {
                name: str(path)
                for name, path
                in paths.items()
            },

        "article_bodies_stored":
            False,
    }
