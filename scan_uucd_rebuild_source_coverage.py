"""Read-only UUCD rebuild source-coverage and deletion-safety scan."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

WORKSPACE_ID = "ws_whattoexpect_com"

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

DATA_ROOT = (
    SERVER_ROOT
    / "data"
)

UUCD_ROOT = (
    DATA_ROOT
    / "universal_unified_content_documents"
)

WUC_VERIFICATION_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "wuc_population_runner_v1_verification.json"
)

ARTICLE_VALIDATION_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_population_v3_verification.json"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "uucd_rebuild_source_coverage.json"
)

UPLOAD_SOURCE_ROOT_CANDIDATES = [
    DATA_ROOT / "uploaded_document_unified_content",
    DATA_ROOT / "uploaded_documents",
    DATA_ROOT / "uploads",
    DATA_ROOT / "documents",
    DATA_ROOT / "upload_extraction_results",
    DATA_ROOT / "upload_extraction_result",
    SERVER_ROOT / "uploads",
]

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "node_modules",
}


def excluded(
    path: Path,
) -> bool:
    return any(
        part in EXCLUDED_PARTS
        for part in path.parts
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


def safe_load_json(
    path: Path,
) -> dict[str, Any] | None:
    try:
        return load_json(
            path
        )

    except Exception:
        return None


def normalize(
    value: Any,
) -> str:
    return str(
        value or ""
    ).strip()


def collect_aliases(
    record: dict[str, Any],
) -> set[str]:
    aliases: set[str] = set()

    for field in (
        "document_id",
        "source_id",
        "source_record_id",
        "upload_id",
        "file_id",
        "content_id",
        "doc_id",
        "html_id",
        "filename",
        "source_name",
    ):
        value = normalize(
            record.get(
                field
            )
        )

        if value:
            aliases.add(
                value.casefold()
            )

            aliases.add(
                Path(
                    value
                ).stem.casefold()
            )

    metadata = record.get(
        "metadata"
    )

    if isinstance(
        metadata,
        dict,
    ):
        for field in (
            "document_id",
            "source_id",
            "source_record_id",
            "upload_id",
            "file_id",
            "doc_id",
            "filename",
            "original_filename",
            "stored_filename",
        ):
            value = normalize(
                metadata.get(
                    field
                )
            )

            if value:
                aliases.add(
                    value.casefold()
                )

                aliases.add(
                    Path(
                        value
                    ).stem.casefold()
                )

    source_identity = record.get(
        "source_identity"
    )

    if isinstance(
        source_identity,
        dict,
    ):
        for value in source_identity.values():
            if isinstance(
                value,
                (
                    str,
                    int,
                ),
            ):
                normalized = normalize(
                    value
                )

                if normalized:
                    aliases.add(
                        normalized.casefold()
                    )

                    aliases.add(
                        Path(
                            normalized
                        ).stem.casefold()
                    )

    return aliases


def discover_upload_source_files() -> list[Path]:
    candidates: set[Path] = set()

    for root in UPLOAD_SOURCE_ROOT_CANDIDATES:
        if not root.exists():
            continue

        for path in root.rglob(
            "*"
        ):
            if (
                path.is_file()
                and not excluded(
                    path
                )
            ):
                candidates.add(
                    path.resolve()
                )

    for path in SERVER_ROOT.rglob(
        "*"
    ):
        if (
            not path.is_file()
            or excluded(
                path
            )
        ):
            continue

        lowered = path.as_posix().casefold()

        if any(
            term in lowered
            for term in (
                "uploaded_document_unified_content",
                "upload_extraction_result",
                "uploaded_documents",
                "/uploads/",
                "\\uploads\\",
            )
        ):
            candidates.add(
                path.resolve()
            )

    return sorted(
        candidates,
        key=lambda value: (
            value.as_posix()
        ),
    )


def inspect_upload_source_file(
    path: Path,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path":
            str(
                path
            ),

        "suffix":
            path.suffix.casefold(),

        "aliases":
            set(),

        "has_content_body":
            False,

        "has_article_body":
            False,

        "has_text_content":
            False,

        "has_title":
            False,

        "workspace_ids":
            set(),

        "readable":
            True,
    }

    result[
        "aliases"
    ].add(
        path.name.casefold()
    )

    result[
        "aliases"
    ].add(
        path.stem.casefold()
    )

    if path.suffix.casefold() not in {
        ".json",
        ".jsonl",
    }:
        result[
            "has_text_content"
        ] = (
            path.stat().st_size
            > 0
        )

        return result

    try:
        text = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

    except Exception:
        result[
            "readable"
        ] = False

        return result

    records: list[
        dict[str, Any]
    ] = []

    if path.suffix.casefold() == ".json":
        try:
            value = json.loads(
                text
            )

        except Exception:
            result[
                "readable"
            ] = False

            return result

        if isinstance(
            value,
            dict,
        ):
            records.append(
                value
            )

        elif isinstance(
            value,
            list,
        ):
            records.extend(
                item
                for item in value
                if isinstance(
                    item,
                    dict,
                )
            )

    else:
        for line in text.splitlines():
            stripped = line.strip()

            if not stripped:
                continue

            try:
                value = json.loads(
                    stripped
                )

            except Exception:
                continue

            if isinstance(
                value,
                dict,
            ):
                records.append(
                    value
                )

    for record in records:
        result[
            "aliases"
        ].update(
            collect_aliases(
                record
            )
        )

        workspace_id = normalize(
            record.get(
                "workspace_id"
            )
        )

        if workspace_id:
            result[
                "workspace_ids"
            ].add(
                workspace_id
            )

        content_body = normalize(
            record.get(
                "content_body"
            )
        )

        article_body = normalize(
            record.get(
                "article_body"
            )
        )

        text_content = normalize(
            record.get(
                "text"
            )
            or record.get(
                "content"
            )
            or record.get(
                "body"
            )
        )

        title = normalize(
            record.get(
                "title"
            )
        )

        if content_body:
            result[
                "has_content_body"
            ] = True

        if article_body:
            result[
                "has_article_body"
            ] = True

        if text_content:
            result[
                "has_text_content"
            ] = True

        if title:
            result[
                "has_title"
            ] = True

    return result


wuc_status: dict[str, Any] = {
    "verification_exists":
        WUC_VERIFICATION_PATH.is_file(),

    "verification_status":
        None,

    "input_count":
        None,

    "pass_count":
        None,

    "fail_count":
        None,

    "full_body_handoff_ready_count":
        None,

    "certificate_status":
        None,

    "website_rebuild_source_complete":
        False,
}

if WUC_VERIFICATION_PATH.is_file():
    wuc_report = load_json(
        WUC_VERIFICATION_PATH
    )

    result = wuc_report.get(
        "result"
    )

    if not isinstance(
        result,
        dict,
    ):
        result = {}

    wuc_status.update(
        {
            "verification_status":
                wuc_report.get(
                    "verification_status"
                ),

            "input_count":
                result.get(
                    "input_count"
                ),

            "pass_count":
                result.get(
                    "pass_count"
                ),

            "fail_count":
                result.get(
                    "fail_count"
                ),

            "full_body_handoff_ready_count":
                result.get(
                    "full_body_handoff_ready_count"
                ),

            "certificate_status":
                result.get(
                    "certificate_status"
                ),
        }
    )

    wuc_status[
        "website_rebuild_source_complete"
    ] = (
        wuc_report.get(
            "verification_status"
        )
        == "PASS"
        and result.get(
            "input_count"
        )
        == 2219
        and result.get(
            "pass_count"
        )
        == 2219
        and result.get(
            "fail_count"
        )
        == 0
        and result.get(
            "full_body_handoff_ready_count"
        )
        == 2219
        and result.get(
            "certificate_status"
        )
        == "CERTIFIED"
    )


legacy_website_records: list[
    dict[str, Any]
] = []

legacy_uploaded_records: list[
    dict[str, Any]
] = []

legacy_unknown_records: list[
    dict[str, Any]
] = []

parse_failures: list[
    str
] = []

if UUCD_ROOT.is_dir():
    for path in sorted(
        UUCD_ROOT.rglob(
            "*.json"
        ),
        key=lambda value: (
            value.as_posix()
        ),
    ):
        record = safe_load_json(
            path
        )

        if record is None:
            parse_failures.append(
                str(
                    path
                )
            )

            continue

        source_type = normalize(
            record.get(
                "source_type"
            )
        ).casefold()

        item = {
            "path":
                str(
                    path
                ),

            "document_id":
                record.get(
                    "document_id"
                ),

            "workspace_id":
                record.get(
                    "workspace_id"
                ),

            "title":
                record.get(
                    "title"
                ),

            "source_type":
                source_type,

            "aliases":
                sorted(
                    collect_aliases(
                        record
                    )
                ),

            "has_content_body":
                bool(
                    normalize(
                        record.get(
                            "content_body"
                        )
                    )
                ),

            "has_content_hash":
                bool(
                    normalize(
                        record.get(
                            "content_hash"
                        )
                    )
                ),

            "has_body_ref":
                bool(
                    normalize(
                        record.get(
                            "body_ref"
                        )
                    )
                ),
        }

        if source_type == "website":
            legacy_website_records.append(
                item
            )

        elif source_type == "uploaded_document":
            legacy_uploaded_records.append(
                item
            )

        else:
            legacy_unknown_records.append(
                item
            )


upload_source_files = (
    discover_upload_source_files()
)

upload_source_inspections = [
    inspect_upload_source_file(
        path
    )
    for path in upload_source_files
]

alias_to_sources: dict[
    str,
    list[dict[str, Any]],
] = defaultdict(
    list
)

for source in upload_source_inspections:
    for alias in source[
        "aliases"
    ]:
        alias_to_sources[
            alias
        ].append(
            source
        )


uploaded_coverage: list[
    dict[str, Any]
] = []

for record in legacy_uploaded_records:
    matches: dict[
        str,
        dict[str, Any]
    ] = {}

    for alias in record[
        "aliases"
    ]:
        for source in alias_to_sources.get(
            alias,
            [],
        ):
            matches[
                source[
                    "path"
                ]
            ] = source

    matched_sources = list(
        matches.values()
    )

    sources_with_body = [
        source
        for source in matched_sources
        if (
            source[
                "has_content_body"
            ]
            or source[
                "has_article_body"
            ]
            or source[
                "has_text_content"
            ]
        )
    ]

    uploaded_coverage.append(
        {
            "document_id":
                record[
                    "document_id"
                ],

            "title":
                record[
                    "title"
                ],

            "workspace_id":
                record[
                    "workspace_id"
                ],

            "matched_source_count":
                len(
                    matched_sources
                ),

            "matched_body_source_count":
                len(
                    sources_with_body
                ),

            "recoverable":
                bool(
                    sources_with_body
                ),

            "matched_source_paths":
                [
                    source[
                        "path"
                    ]
                    for source in matched_sources[
                        :20
                    ]
                ],

            "matched_body_source_paths":
                [
                    source[
                        "path"
                    ]
                    for source in sources_with_body[
                        :20
                    ]
                ],
        }
    )


recoverable_uploaded_count = sum(
    1
    for record in uploaded_coverage
    if record[
        "recoverable"
    ]
)

unrecoverable_uploaded = [
    record
    for record in uploaded_coverage
    if not record[
        "recoverable"
    ]
]

ambiguous_uploaded = [
    record
    for record in uploaded_coverage
    if record[
        "matched_body_source_count"
    ]
    > 1
]


website_safe_to_rebuild = (
    wuc_status[
        "website_rebuild_source_complete"
    ]
)

uploaded_safe_to_rebuild = (
    len(
        legacy_uploaded_records
    )
    > 0
    and recoverable_uploaded_count
    == len(
        legacy_uploaded_records
    )
)

all_legacy_uucd_safe_to_delete = (
    website_safe_to_rebuild
    and uploaded_safe_to_rebuild
    and not legacy_unknown_records
    and not parse_failures
)


if all_legacy_uucd_safe_to_delete:
    deletion_decision = (
        "SAFE_TO_DELETE_ALL_LEGACY_UUCD_AND_BODY_STORE_OUTPUTS"
    )

elif (
    website_safe_to_rebuild
    and not uploaded_safe_to_rebuild
):
    deletion_decision = (
        "WEBSITE_REBUILD_SAFE_UPLOAD_REBUILD_NOT_YET_SAFE"
    )

elif (
    not website_safe_to_rebuild
    and uploaded_safe_to_rebuild
):
    deletion_decision = (
        "UPLOAD_REBUILD_SAFE_WEBSITE_REBUILD_NOT_YET_SAFE"
    )

else:
    deletion_decision = (
        "NOT_SAFE_TO_DELETE_LEGACY_OUTPUTS"
    )


report = {
    "schema_version":
        "uucd_rebuild_source_coverage_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "website_source_coverage":
        wuc_status,

    "legacy_uucd": {
        "website_count":
            len(
                legacy_website_records
            ),

        "uploaded_document_count":
            len(
                legacy_uploaded_records
            ),

        "unknown_count":
            len(
                legacy_unknown_records
            ),

        "parse_failure_count":
            len(
                parse_failures
            ),
    },

    "upload_source_discovery": {
        "candidate_file_count":
            len(
                upload_source_files
            ),

        "readable_candidate_count":
            sum(
                1
                for item
                in upload_source_inspections
                if item[
                    "readable"
                ]
            ),

        "candidate_with_body_count":
            sum(
                1
                for item
                in upload_source_inspections
                if (
                    item[
                        "has_content_body"
                    ]
                    or item[
                        "has_article_body"
                    ]
                    or item[
                        "has_text_content"
                    ]
                )
            ),
    },

    "uploaded_document_coverage": {
        "legacy_record_count":
            len(
                legacy_uploaded_records
            ),

        "recoverable_count":
            recoverable_uploaded_count,

        "unrecoverable_count":
            len(
                unrecoverable_uploaded
            ),

        "ambiguous_count":
            len(
                ambiguous_uploaded
            ),

        "records":
            uploaded_coverage,

        "unrecoverable_records":
            unrecoverable_uploaded,

        "ambiguous_records":
            ambiguous_uploaded,
    },

    "website_safe_to_rebuild":
        website_safe_to_rebuild,

    "uploaded_safe_to_rebuild":
        uploaded_safe_to_rebuild,

    "all_legacy_uucd_safe_to_delete":
        all_legacy_uucd_safe_to_delete,

    "deletion_decision":
        deletion_decision,

    "source_files_modified":
        False,

    "data_files_modified":
        False,

    "runtime_state_modified":
        False,
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
print("=" * 108)
print(
    "UUCD REBUILD — SOURCE COVERAGE AND DELETION-SAFETY SCAN"
)
print("=" * 108)
print()

print(
    "Legacy website UUCD records:          "
    + str(
        len(
            legacy_website_records
        )
    )
)

print(
    "Legacy uploaded UUCD records:         "
    + str(
        len(
            legacy_uploaded_records
        )
    )
)

print(
    "Unknown legacy UUCD records:          "
    + str(
        len(
            legacy_unknown_records
        )
    )
)

print(
    "UUCD parse failures:                  "
    + str(
        len(
            parse_failures
        )
    )
)

print()
print(
    "WEBSITE REBUILD SOURCE"
)

print(
    "  WUC verification exists:           "
    + str(
        wuc_status[
            "verification_exists"
        ]
    )
)

print(
    "  WUC verification status:           "
    + str(
        wuc_status[
            "verification_status"
        ]
    )
)

print(
    "  WUC PASS count:                    "
    + str(
        wuc_status[
            "pass_count"
        ]
    )
)

print(
    "  Full-body handoff ready:           "
    + str(
        wuc_status[
            "full_body_handoff_ready_count"
        ]
    )
)

print(
    "  WUC certificate status:            "
    + str(
        wuc_status[
            "certificate_status"
        ]
    )
)

print(
    "  Website safe to rebuild:           "
    + str(
        website_safe_to_rebuild
    )
)

print()
print(
    "UPLOADED-DOCUMENT REBUILD SOURCE"
)

print(
    "  Candidate source files discovered: "
    + str(
        len(
            upload_source_files
        )
    )
)

print(
    "  Legacy uploaded records:           "
    + str(
        len(
            legacy_uploaded_records
        )
    )
)

print(
    "  Recoverable uploaded records:      "
    + str(
        recoverable_uploaded_count
    )
)

print(
    "  Unrecoverable uploaded records:    "
    + str(
        len(
            unrecoverable_uploaded
        )
    )
)

print(
    "  Ambiguous uploaded records:        "
    + str(
        len(
            ambiguous_uploaded
        )
    )
)

print(
    "  Uploaded side safe to rebuild:     "
    + str(
        uploaded_safe_to_rebuild
    )
)

print()
print(
    "DELETION DECISION"
)

print(
    "  "
    + deletion_decision
)

print()
print(
    "Safe to delete all legacy UUCD and Body Store outputs: "
    + str(
        all_legacy_uucd_safe_to_delete
    )
)

if unrecoverable_uploaded:
    print()
    print(
        "UNRECOVERABLE UPLOADED RECORDS — FIRST 20"
    )

    for record in unrecoverable_uploaded[
        :20
    ]:
        print(
            "  "
            + str(
                record[
                    "document_id"
                ]
            )
            + " | "
            + str(
                record[
                    "title"
                ]
            )
        )

print()
print(
    "Source files modified:  False"
)

print(
    "Data files modified:    False"
)

print(
    "Runtime state modified: False"
)

print()
print(
    "Coverage report: "
    + str(
        REPORT_PATH
    )
)

print()
print(
    "UUCD REBUILD SOURCE-COVERAGE SCAN: PASS"
)

print(
    "No UUCD, Body Store, upload source, WUC evidence "
    "or runtime state was modified."
)

print("=" * 108)
