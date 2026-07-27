"""Resolve authoritative upstream sources for legacy uploaded UUCD records."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
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

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "uploaded_uucd_authoritative_source_identity.json"
)

SOURCE_ROOT_CANDIDATES = [
    DATA_ROOT
    / "uploaded_document_unified_content",

    DATA_ROOT
    / "uploaded_documents",

    DATA_ROOT
    / "upload_extraction_results",

    DATA_ROOT
    / "upload_extraction_result",

    DATA_ROOT
    / "uploads",

    DATA_ROOT
    / "documents",

    SERVER_ROOT
    / "uploads",
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


def normalize(
    value: Any,
) -> str:
    return str(
        value or ""
    ).strip()


def normalize_key(
    value: Any,
) -> str:
    return normalize(
        value
    ).casefold()


def sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def canonical_text_hash(
    value: Any,
) -> str:
    text = " ".join(
        normalize(
            value
        ).split()
    )

    if not text:
        return ""

    return sha256_text(
        text
    )


def safe_json_load(
    path: Path,
) -> Any:
    try:
        return json.loads(
            path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        )

    except Exception:
        return None


def flatten_records(
    value: Any,
) -> list[dict[str, Any]]:
    if isinstance(
        value,
        dict,
    ):
        return [
            value
        ]

    if isinstance(
        value,
        list,
    ):
        return [
            item
            for item in value
            if isinstance(
                item,
                dict,
            )
        ]

    return []


def nested_mapping(
    record: dict[str, Any],
    field: str,
) -> dict[str, Any]:
    value = record.get(
        field
    )

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


def first_value(
    record: dict[str, Any],
    fields: tuple[str, ...],
) -> str:
    for field in fields:
        value = normalize(
            record.get(
                field
            )
        )

        if value:
            return value

    return ""


def collect_identity(
    record: dict[str, Any],
) -> dict[str, Any]:
    metadata = nested_mapping(
        record,
        "metadata",
    )

    source_identity = nested_mapping(
        record,
        "source_identity",
    )

    provenance = nested_mapping(
        record,
        "extraction_provenance",
    )

    document_id = (
        first_value(
            record,
            (
                "document_id",
                "doc_id",
            ),
        )
        or first_value(
            metadata,
            (
                "document_id",
                "doc_id",
            ),
        )
        or first_value(
            source_identity,
            (
                "document_id",
                "doc_id",
            ),
        )
    )

    source_id = (
        first_value(
            record,
            (
                "source_id",
                "source_record_id",
            ),
        )
        or first_value(
            metadata,
            (
                "source_id",
                "source_record_id",
            ),
        )
        or first_value(
            source_identity,
            (
                "source_id",
                "source_record_id",
            ),
        )
    )

    upload_id = (
        first_value(
            record,
            (
                "upload_id",
                "file_id",
            ),
        )
        or first_value(
            metadata,
            (
                "upload_id",
                "file_id",
            ),
        )
        or first_value(
            source_identity,
            (
                "upload_id",
                "file_id",
            ),
        )
    )

    filename = (
        first_value(
            record,
            (
                "filename",
                "source_name",
                "original_filename",
                "stored_filename",
            ),
        )
        or first_value(
            metadata,
            (
                "filename",
                "source_name",
                "original_filename",
                "stored_filename",
            ),
        )
        or first_value(
            source_identity,
            (
                "filename",
                "source_name",
                "original_filename",
                "stored_filename",
            ),
        )
        or first_value(
            provenance,
            (
                "filename",
                "source_name",
                "original_filename",
                "stored_filename",
            ),
        )
    )

    workspace_id = (
        first_value(
            record,
            (
                "workspace_id",
            ),
        )
        or first_value(
            metadata,
            (
                "workspace_id",
            ),
        )
        or first_value(
            source_identity,
            (
                "workspace_id",
            ),
        )
    )

    title = (
        first_value(
            record,
            (
                "title",
            ),
        )
        or first_value(
            metadata,
            (
                "title",
            ),
        )
    )

    content_body = first_value(
        record,
        (
            "content_body",
            "article_body",
            "body",
            "text",
            "content",
        ),
    )

    content_hash = (
        first_value(
            record,
            (
                "content_hash",
            ),
        )
        or first_value(
            metadata,
            (
                "content_hash",
            ),
        )
    )

    if not content_hash and content_body:
        content_hash = canonical_text_hash(
            content_body
        )

    return {
        "document_id":
            document_id,

        "source_id":
            source_id,

        "upload_id":
            upload_id,

        "filename":
            filename,

        "filename_name":
            (
                Path(
                    filename
                ).name
                if filename
                else ""
            ),

        "filename_stem":
            (
                Path(
                    filename
                ).stem
                if filename
                else ""
            ),

        "workspace_id":
            workspace_id,

        "title":
            title,

        "content_hash":
            content_hash,

        "content_body_present":
            bool(
                content_body
            ),
    }


def discover_source_files() -> list[Path]:
    paths: set[Path] = set()

    for root in SOURCE_ROOT_CANDIDATES:
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
                paths.add(
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
                "/uploads/",
                "\\uploads\\",
            )
        ):
            paths.add(
                path.resolve()
            )

    return sorted(
        paths,
        key=lambda item: (
            item.as_posix()
        ),
    )


def read_source_records(
    path: Path,
) -> list[dict[str, Any]]:
    suffix = path.suffix.casefold()

    if suffix == ".json":
        return flatten_records(
            safe_json_load(
                path
            )
        )

    if suffix == ".jsonl":
        records: list[
            dict[str, Any]
        ] = []

        try:
            lines = path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            ).splitlines()

        except Exception:
            return []

        for line in lines:
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

        return records

    # Preserve raw uploaded files as source candidates.
    return [
        {
            "filename":
                path.name,

            "stored_filename":
                path.name,

            "source_path":
                str(
                    path
                ),

            "workspace_id":
                (
                    WORKSPACE_ID
                    if WORKSPACE_ID
                    in path.as_posix()
                    else ""
                ),

            "raw_file_exists":
                True,

            "raw_file_size":
                path.stat().st_size,
        }
    ]


source_candidates: list[
    dict[str, Any]
] = []

for source_path in discover_source_files():
    records = read_source_records(
        source_path
    )

    for record_index, record in enumerate(
        records
    ):
        identity = collect_identity(
            record
        )

        source_candidates.append(
            {
                "candidate_id":
                    (
                        str(
                            source_path
                        )
                        + "#"
                        + str(
                            record_index
                        )
                    ),

                "path":
                    str(
                        source_path
                    ),

                "record_index":
                    record_index,

                "suffix":
                    source_path.suffix.casefold(),

                "identity":
                    identity,

                "has_rebuild_body":
                    bool(
                        identity[
                            "content_body_present"
                        ]
                        or (
                            source_path.suffix.casefold()
                            not in {
                                ".json",
                                ".jsonl",
                            }
                            and source_path.stat().st_size
                            > 0
                        )
                    ),
            }
        )


legacy_uploaded_records: list[
    dict[str, Any]
] = []

if UUCD_ROOT.is_dir():
    for path in sorted(
        UUCD_ROOT.rglob(
            "*.json"
        ),
        key=lambda item: (
            item.as_posix()
        ),
    ):
        value = safe_json_load(
            path
        )

        if not isinstance(
            value,
            dict,
        ):
            continue

        if normalize_key(
            value.get(
                "source_type"
            )
        ) != "uploaded_document":
            continue

        legacy_uploaded_records.append(
            {
                "path":
                    str(
                        path
                    ),

                "record":
                    value,

                "identity":
                    collect_identity(
                        value
                    ),
            }
        )


def add_reason(
    reasons: list[dict[str, Any]],
    *,
    method: str,
    confidence: str,
    score: int,
    value: str,
) -> None:
    reasons.append(
        {
            "method":
                method,

            "confidence":
                confidence,

            "score":
                score,

            "value":
                value,
        }
    )


def score_candidate(
    legacy_identity: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    candidate_identity = candidate[
        "identity"
    ]

    reasons: list[
        dict[str, Any]
    ] = []

    legacy_document_id = normalize_key(
        legacy_identity[
            "document_id"
        ]
    )

    candidate_document_id = normalize_key(
        candidate_identity[
            "document_id"
        ]
    )

    if (
        legacy_document_id
        and candidate_document_id
        and legacy_document_id
        == candidate_document_id
    ):
        add_reason(
            reasons,
            method="EXACT_DOCUMENT_ID",
            confidence="HIGH",
            score=1000,
            value=legacy_identity[
                "document_id"
            ],
        )

    legacy_upload_id = normalize_key(
        legacy_identity[
            "upload_id"
        ]
    )

    candidate_upload_id = normalize_key(
        candidate_identity[
            "upload_id"
        ]
    )

    if (
        legacy_upload_id
        and candidate_upload_id
        and legacy_upload_id
        == candidate_upload_id
    ):
        add_reason(
            reasons,
            method="EXACT_UPLOAD_OR_FILE_ID",
            confidence="HIGH",
            score=900,
            value=legacy_identity[
                "upload_id"
            ],
        )

    legacy_source_id = normalize_key(
        legacy_identity[
            "source_id"
        ]
    )

    candidate_source_id = normalize_key(
        candidate_identity[
            "source_id"
        ]
    )

    if (
        legacy_source_id
        and candidate_source_id
        and legacy_source_id
        == candidate_source_id
    ):
        add_reason(
            reasons,
            method="EXACT_SOURCE_ID",
            confidence="HIGH",
            score=850,
            value=legacy_identity[
                "source_id"
            ],
        )

    legacy_hash = normalize_key(
        legacy_identity[
            "content_hash"
        ]
    )

    candidate_hash = normalize_key(
        candidate_identity[
            "content_hash"
        ]
    )

    if (
        legacy_hash
        and candidate_hash
        and legacy_hash
        == candidate_hash
    ):
        add_reason(
            reasons,
            method="EXACT_CONTENT_HASH",
            confidence="HIGH",
            score=800,
            value=legacy_identity[
                "content_hash"
            ],
        )

    legacy_filename = normalize_key(
        legacy_identity[
            "filename_name"
        ]
    )

    candidate_filename = normalize_key(
        candidate_identity[
            "filename_name"
        ]
    )

    if (
        legacy_filename
        and candidate_filename
        and legacy_filename
        == candidate_filename
    ):
        add_reason(
            reasons,
            method="EXACT_FILENAME",
            confidence="MEDIUM",
            score=500,
            value=legacy_identity[
                "filename_name"
            ],
        )

    legacy_stem = normalize_key(
        legacy_identity[
            "filename_stem"
        ]
    )

    candidate_stem = normalize_key(
        candidate_identity[
            "filename_stem"
        ]
    )

    legacy_workspace = normalize_key(
        legacy_identity[
            "workspace_id"
        ]
    )

    candidate_workspace = normalize_key(
        candidate_identity[
            "workspace_id"
        ]
    )

    if (
        legacy_stem
        and candidate_stem
        and legacy_stem
        == candidate_stem
        and legacy_workspace
        and candidate_workspace
        and legacy_workspace
        == candidate_workspace
    ):
        add_reason(
            reasons,
            method="WORKSPACE_AND_FILENAME_STEM",
            confidence="MEDIUM",
            score=400,
            value=(
                legacy_identity[
                    "workspace_id"
                ]
                + " | "
                + legacy_identity[
                    "filename_stem"
                ]
            ),
        )

    legacy_title = normalize_key(
        legacy_identity[
            "title"
        ]
    )

    candidate_title = normalize_key(
        candidate_identity[
            "title"
        ]
    )

    if (
        legacy_title
        and candidate_title
        and legacy_title
        == candidate_title
    ):
        add_reason(
            reasons,
            method="EXACT_TITLE_ONLY",
            confidence="LOW",
            score=100,
            value=legacy_identity[
                "title"
            ],
        )

    highest_score = max(
        (
            reason[
                "score"
            ]
            for reason in reasons
        ),
        default=0,
    )

    if highest_score >= 800:
        confidence = "HIGH"

    elif highest_score >= 400:
        confidence = "MEDIUM"

    elif highest_score > 0:
        confidence = "LOW"

    else:
        confidence = "NONE"

    return {
        "candidate":
            candidate,

        "reasons":
            reasons,

        "highest_score":
            highest_score,

        "total_score":
            sum(
                reason[
                    "score"
                ]
                for reason in reasons
            ),

        "confidence":
            confidence,
    }


resolved_records: list[
    dict[str, Any]
] = []

for legacy in legacy_uploaded_records:
    legacy_identity = legacy[
        "identity"
    ]

    scored = [
        score_candidate(
            legacy_identity,
            candidate,
        )
        for candidate
        in source_candidates
    ]

    scored = [
        result
        for result in scored
        if (
            result[
                "highest_score"
            ]
            > 0
            and result[
                "candidate"
            ][
                "has_rebuild_body"
            ]
        )
    ]

    scored.sort(
        key=lambda result: (
            result[
                "highest_score"
            ],
            result[
                "total_score"
            ],
            result[
                "candidate"
            ][
                "path"
            ],
            result[
                "candidate"
            ][
                "record_index"
            ],
        ),
        reverse=True,
    )

    top_score = (
        scored[
            0
        ][
            "highest_score"
        ]
        if scored
        else 0
    )

    top_total = (
        scored[
            0
        ][
            "total_score"
        ]
        if scored
        else 0
    )

    top_matches = [
        result
        for result in scored
        if (
            result[
                "highest_score"
            ]
            == top_score
            and result[
                "total_score"
            ]
            == top_total
        )
    ]

    unique_match = (
        len(
            top_matches
        )
        == 1
    )

    selected = (
        top_matches[
            0
        ]
        if unique_match
        else None
    )

    selected_confidence = (
        selected[
            "confidence"
        ]
        if selected
        else (
            "AMBIGUOUS"
            if top_matches
            else "NONE"
        )
    )

    authoritative = bool(
        selected
        and selected[
            "confidence"
        ]
        in {
            "HIGH",
            "MEDIUM",
        }
    )

    resolved_records.append(
        {
            "legacy_uucd_path":
                legacy[
                    "path"
                ],

            "document_id":
                legacy_identity[
                    "document_id"
                ],

            "title":
                legacy_identity[
                    "title"
                ],

            "workspace_id":
                legacy_identity[
                    "workspace_id"
                ],

            "legacy_content_hash":
                legacy_identity[
                    "content_hash"
                ],

            "candidate_match_count":
                len(
                    scored
                ),

            "top_match_count":
                len(
                    top_matches
                ),

            "unique_match":
                unique_match,

            "authoritative_match":
                authoritative,

            "selected_confidence":
                selected_confidence,

            "selected_source_path":
                (
                    selected[
                        "candidate"
                    ][
                        "path"
                    ]
                    if selected
                    else None
                ),

            "selected_record_index":
                (
                    selected[
                        "candidate"
                    ][
                        "record_index"
                    ]
                    if selected
                    else None
                ),

            "selected_match_methods":
                (
                    [
                        reason[
                            "method"
                        ]
                        for reason
                        in selected[
                            "reasons"
                        ]
                    ]
                    if selected
                    else []
                ),

            "selected_match_reasons":
                (
                    selected[
                        "reasons"
                    ]
                    if selected
                    else []
                ),

            "top_candidates":
                [
                    {
                        "path":
                            result[
                                "candidate"
                            ][
                                "path"
                            ],

                        "record_index":
                            result[
                                "candidate"
                            ][
                                "record_index"
                            ],

                        "confidence":
                            result[
                                "confidence"
                            ],

                        "highest_score":
                            result[
                                "highest_score"
                            ],

                        "total_score":
                            result[
                                "total_score"
                            ],

                        "match_methods":
                            [
                                reason[
                                    "method"
                                ]
                                for reason
                                in result[
                                    "reasons"
                                ]
                            ],
                    }
                    for result in scored[
                        :10
                    ]
                ],
        }
    )


unique_count = sum(
    1
    for record in resolved_records
    if record[
        "unique_match"
    ]
)

authoritative_count = sum(
    1
    for record in resolved_records
    if record[
        "authoritative_match"
    ]
)

ambiguous_records = [
    record
    for record in resolved_records
    if (
        record[
            "top_match_count"
        ]
        > 1
    )
]

unmatched_records = [
    record
    for record in resolved_records
    if (
        record[
            "candidate_match_count"
        ]
        == 0
    )
]

low_confidence_records = [
    record
    for record in resolved_records
    if (
        record[
            "unique_match"
        ]
        and not record[
            "authoritative_match"
        ]
    )
]

if (
    len(
        resolved_records
    )
    == 53
    and authoritative_count
    == 53
    and not ambiguous_records
    and not unmatched_records
):
    final_outcome = (
        "UNIQUE_MATCH_FOR_ALL_RECORDS"
    )

elif authoritative_count > 0:
    final_outcome = (
        "PARTIAL_AMBIGUITY_REMAINS"
    )

else:
    final_outcome = (
        "NO_AUTHORITATIVE_SOURCE"
    )


confidence_distribution = defaultdict(
    int
)

for record in resolved_records:
    confidence_distribution[
        record[
            "selected_confidence"
        ]
    ] += 1


report = {
    "schema_version":
        "uploaded_uucd_authoritative_source_identity_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "legacy_uploaded_record_count":
        len(
            legacy_uploaded_records
        ),

    "source_candidate_record_count":
        len(
            source_candidates
        ),

    "unique_match_count":
        unique_count,

    "authoritative_match_count":
        authoritative_count,

    "ambiguous_record_count":
        len(
            ambiguous_records
        ),

    "unmatched_record_count":
        len(
            unmatched_records
        ),

    "low_confidence_record_count":
        len(
            low_confidence_records
        ),

    "confidence_distribution":
        dict(
            confidence_distribution
        ),

    "final_outcome":
        final_outcome,

    "records":
        resolved_records,

    "ambiguous_records":
        ambiguous_records,

    "unmatched_records":
        unmatched_records,

    "low_confidence_records":
        low_confidence_records,

    "safe_to_rebuild_uploaded_uucd":
        (
            final_outcome
            == "UNIQUE_MATCH_FOR_ALL_RECORDS"
        ),

    "safe_to_delete_legacy_uploaded_uucd":
        (
            final_outcome
            == "UNIQUE_MATCH_FOR_ALL_RECORDS"
        ),

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
    "UPLOADED UUCD — AUTHORITATIVE SOURCE IDENTITY SCAN"
)
print("=" * 108)
print()

print(
    "Legacy uploaded UUCD records:       "
    + str(
        len(
            legacy_uploaded_records
        )
    )
)

print(
    "Source candidate records:           "
    + str(
        len(
            source_candidates
        )
    )
)

print(
    "Unique source matches:              "
    + str(
        unique_count
    )
)

print(
    "Authoritative matches:              "
    + str(
        authoritative_count
    )
)

print(
    "Ambiguous records:                  "
    + str(
        len(
            ambiguous_records
        )
    )
)

print(
    "Unmatched records:                  "
    + str(
        len(
            unmatched_records
        )
    )
)

print(
    "Low-confidence unique matches:      "
    + str(
        len(
            low_confidence_records
        )
    )
)

print()
print(
    "CONFIDENCE DISTRIBUTION"
)

for confidence, count in sorted(
    confidence_distribution.items()
):
    print(
        "  "
        + confidence
        + ": "
        + str(
            count
        )
    )

print()
print(
    "FINAL OUTCOME"
)

print(
    "  "
    + final_outcome
)

print()
print(
    "Safe to rebuild uploaded UUCD:      "
    + str(
        report[
            "safe_to_rebuild_uploaded_uucd"
        ]
    )
)

print(
    "Safe to delete legacy uploaded UUCD:"
    + " "
    + str(
        report[
            "safe_to_delete_legacy_uploaded_uucd"
        ]
    )
)

if ambiguous_records:
    print()
    print(
        "AMBIGUOUS RECORDS — FIRST 20"
    )

    for record in ambiguous_records[
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
            + " | top matches: "
            + str(
                record[
                    "top_match_count"
                ]
            )
        )

if unmatched_records:
    print()
    print(
        "UNMATCHED RECORDS — FIRST 20"
    )

    for record in unmatched_records[
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

if low_confidence_records:
    print()
    print(
        "LOW-CONFIDENCE RECORDS — FIRST 20"
    )

    for record in low_confidence_records[
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
            + " | confidence: "
            + str(
                record[
                    "selected_confidence"
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
    "Identity report: "
    + str(
        REPORT_PATH
    )
)

print()
print(
    "UPLOADED UUCD AUTHORITATIVE SOURCE SCAN: PASS"
)

print(
    "The scan classified uploaded-document lineage without "
    "modifying UUCD, source documents, Body Store or runtime state."
)

print("=" * 108)
