"""Fresh canonical UUCD engine.

This module performs only transient WUC-to-UUCD conversion.

It does not:
- write UUCD JSON files;
- write Universal Article Body Store files;
- create queues or jobs;
- register runtime handlers;
- read a WUC Store;
- truncate, summarize, or reduce article content.
"""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from typing import Any, Mapping


UUCD_SCHEMA_VERSION = (
    "universal_unified_content_document_v2"
)

UUCD_ENGINE_VERSION = (
    "uucd_engine_v1_frozen_wuc_full_body"
)

SUPPORTED_SOURCE_TYPES = {
    "website",
    "uploaded_document",
    "pdf",
    "api",
    "database",
}

REQUIRED_WUC_FIELDS = {
    "schema_version",
    "engine_version",
    "content_id",
    "document_id",
    "workspace_id",
    "source_type",
    "source_format",
    "source_identity",
    "title",
    "h1",
    "headings",
    "canonical_url",
    "content_body",
    "content_hash",
    "body_length",
    "body_word_count",
    "structure",
    "metadata",
    "handoff",
}

REQUIRED_WUC_HANDOFF_FIELDS = {
    "next_stage",
    "eligible_for_uucd",
    "body_field",
    "full_body_handoff",
}

REQUIRED_WUC_SOURCE_IDENTITY_FIELDS = {
    "source_record_id",
}

REQUIRED_UUCD_FIELDS = {
    "schema_version",
    "engine_version",
    "document_id",
    "workspace_id",
    "source_id",
    "source_type",
    "source_name",
    "source_format",
    "source_identity",
    "title",
    "h1",
    "headings",
    "canonical_url",
    "content_body",
    "structure",
    "content_hash",
    "content_ref",
    "body_ref",
    "body_status",
    "body_length",
    "body_word_count",
    "metadata",
    "lifecycle",
    "versioning",
    "provenance",
    "handoff",
}


class UUCDContractError(
    ValueError
):
    """Raised when a WUC package violates the frozen UUCD input contract."""


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(
        value,
        Mapping,
    ):
        raise UUCDContractError(
            field_name
            + " must be a mapping."
        )

    return value


def _require_non_empty_string(
    value: Any,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise UUCDContractError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise UUCDContractError(
            field_name
            + " must not be empty."
        )

    return normalized


def _optional_string(
    value: Any,
) -> str:
    if value is None:
        return ""

    if not isinstance(
        value,
        str,
    ):
        return str(
            value
        ).strip()

    return value.strip()


def _slugify(
    value: str,
) -> str:
    slug = re.sub(
        r"[^a-zA-Z0-9]+",
        "-",
        value,
    ).strip(
        "-"
    ).lower()

    return (
        slug[
            :100
        ]
        or "document"
    )


def compute_canonical_content_hash_v1(
    content_body: str,
) -> str:
    """Hash the exact complete body received from WUC.

    No whitespace normalization is performed. This allows exact body
    preservation checks between WUC, UUCD, and the Body Store.
    """

    if not isinstance(
        content_body,
        str,
    ):
        raise UUCDContractError(
            "content_body must be a string."
        )

    if not content_body:
        raise UUCDContractError(
            "content_body must not be empty."
        )

    return hashlib.sha256(
        content_body.encode(
            "utf-8"
        )
    ).hexdigest()


def _stable_document_id(
    *,
    workspace_id: str,
    source_type: str,
    source_record_id: str,
) -> str:
    identity = (
        workspace_id
        + "\x00"
        + source_type
        + "\x00"
        + source_record_id
    )

    digest = hashlib.sha256(
        identity.encode(
            "utf-8"
        )
    ).hexdigest()

    return (
        "uucd_"
        + digest[
            :32
        ]
    )


def _stable_body_ref(
    *,
    workspace_id: str,
    document_id: str,
    title: str,
) -> str:
    filename = (
        _slugify(
            title
        )
        + "_"
        + document_id[
            -12:
        ]
        + ".txt"
    )

    return (
        "backend/server/data/"
        "universal_article_body_store/"
        + workspace_id
        + "/bodies/"
        + filename
    )


def _stable_content_ref(
    *,
    workspace_id: str,
    document_id: str,
) -> str:
    return (
        "backend/server/data/"
        "universal_unified_content_documents/"
        + workspace_id
        + "/documents/"
        + document_id
        + ".json"
    )


def _validate_wuc_contract(
    wuc_package: Mapping[str, Any],
) -> dict[str, Any]:
    missing_fields = sorted(
        REQUIRED_WUC_FIELDS
        - set(
            wuc_package
        )
    )

    if missing_fields:
        raise UUCDContractError(
            "WUC package is missing required fields: "
            + ", ".join(
                missing_fields
            )
        )

    workspace_id = _require_non_empty_string(
        wuc_package.get(
            "workspace_id"
        ),
        field_name="workspace_id",
    )

    source_type = _require_non_empty_string(
        wuc_package.get(
            "source_type"
        ),
        field_name="source_type",
    ).casefold()

    if source_type not in SUPPORTED_SOURCE_TYPES:
        raise UUCDContractError(
            "Unsupported source_type: "
            + source_type
        )

    source_format = _require_non_empty_string(
        wuc_package.get(
            "source_format"
        ),
        field_name="source_format",
    )

    content_id = _require_non_empty_string(
        wuc_package.get(
            "content_id"
        ),
        field_name="content_id",
    )

    title = _require_non_empty_string(
        wuc_package.get(
            "title"
        ),
        field_name="title",
    )

    content_body = _require_non_empty_string(
        wuc_package.get(
            "content_body"
        ),
        field_name="content_body",
    )

    source_identity = _require_mapping(
        wuc_package.get(
            "source_identity"
        ),
        field_name="source_identity",
    )

    missing_identity_fields = sorted(
        REQUIRED_WUC_SOURCE_IDENTITY_FIELDS
        - set(
            source_identity
        )
    )

    if missing_identity_fields:
        raise UUCDContractError(
            "source_identity is missing fields: "
            + ", ".join(
                missing_identity_fields
            )
        )

    source_record_id = _require_non_empty_string(
        source_identity.get(
            "source_record_id"
        ),
        field_name=(
            "source_identity.source_record_id"
        ),
    )

    structure = _require_mapping(
        wuc_package.get(
            "structure"
        ),
        field_name="structure",
    )

    metadata = _require_mapping(
        wuc_package.get(
            "metadata"
        ),
        field_name="metadata",
    )

    handoff = _require_mapping(
        wuc_package.get(
            "handoff"
        ),
        field_name="handoff",
    )

    missing_handoff_fields = sorted(
        REQUIRED_WUC_HANDOFF_FIELDS
        - set(
            handoff
        )
    )

    if missing_handoff_fields:
        raise UUCDContractError(
            "handoff is missing fields: "
            + ", ".join(
                missing_handoff_fields
            )
        )

    if handoff.get(
        "eligible_for_uucd"
    ) is not True:
        raise UUCDContractError(
            "WUC package is not eligible for UUCD."
        )

    if handoff.get(
        "full_body_handoff"
    ) is not True:
        raise UUCDContractError(
            "WUC package does not certify full-body handoff."
        )

    if handoff.get(
        "body_field"
    ) != "content_body":
        raise UUCDContractError(
            "WUC handoff body_field must be content_body."
        )

    next_stage = _optional_string(
        handoff.get(
            "next_stage"
        )
    ).casefold()

    if (
        "universal"
        not in next_stage
        or "content"
        not in next_stage
    ):
        raise UUCDContractError(
            "WUC handoff next_stage does not identify UUCD."
        )

    if metadata.get(
        "complete_content_preserved"
    ) is not True:
        raise UUCDContractError(
            "WUC metadata does not certify complete content."
        )

    if metadata.get(
        "content_reduction_performed"
    ) is not False:
        raise UUCDContractError(
            "WUC metadata reports content reduction."
        )

    if metadata.get(
        "summarization_performed"
    ) is not False:
        raise UUCDContractError(
            "WUC metadata reports summarization."
        )

    if metadata.get(
        "truncation_performed"
    ) is not False:
        raise UUCDContractError(
            "WUC metadata reports truncation."
        )

    if metadata.get(
        "word_count_limit_applied"
    ) is not False:
        raise UUCDContractError(
            "WUC metadata reports a word-count limit."
        )

    supplied_hash = _require_non_empty_string(
        wuc_package.get(
            "content_hash"
        ),
        field_name="content_hash",
    )

    calculated_hash = (
        compute_canonical_content_hash_v1(
            content_body
        )
    )

    if supplied_hash != calculated_hash:
        raise UUCDContractError(
            "WUC content_hash does not match the exact content_body."
        )

    body_length = wuc_package.get(
        "body_length"
    )

    if (
        not isinstance(
            body_length,
            int,
        )
        or body_length
        != len(
            content_body
        )
    ):
        raise UUCDContractError(
            "WUC body_length does not match the complete content_body."
        )

    body_word_count = wuc_package.get(
        "body_word_count"
    )

    if (
        not isinstance(
            body_word_count,
            int,
        )
        or body_word_count
        <= 0
    ):
        raise UUCDContractError(
            "WUC body_word_count must be a positive integer."
        )

    return {
        "workspace_id":
            workspace_id,

        "source_type":
            source_type,

        "source_format":
            source_format,

        "content_id":
            content_id,

        "title":
            title,

        "content_body":
            content_body,

        "source_identity":
            source_identity,

        "source_record_id":
            source_record_id,

        "structure":
            structure,

        "metadata":
            metadata,

        "handoff":
            handoff,

        "content_hash":
            calculated_hash,

        "body_length":
            body_length,

        "body_word_count":
            body_word_count,
    }


def build_transient_uucd_from_wuc_v1(
    wuc_package: Mapping[str, Any],
) -> dict[str, Any]:
    """Create one complete transient UUCD package from frozen WUC.

    The complete content_body is copied exactly once into the returned
    in-memory UUCD dictionary. No persistence occurs here.
    """

    wuc = _require_mapping(
        wuc_package,
        field_name="wuc_package",
    )

    validated = _validate_wuc_contract(
        wuc
    )

    workspace_id = validated[
        "workspace_id"
    ]

    source_type = validated[
        "source_type"
    ]

    source_identity = deepcopy(
        dict(
            validated[
                "source_identity"
            ]
        )
    )

    source_record_id = validated[
        "source_record_id"
    ]

    title = validated[
        "title"
    ]

    document_id = _stable_document_id(
        workspace_id=workspace_id,
        source_type=source_type,
        source_record_id=source_record_id,
    )

    content_ref = _stable_content_ref(
        workspace_id=workspace_id,
        document_id=document_id,
    )

    body_ref = _stable_body_ref(
        workspace_id=workspace_id,
        document_id=document_id,
        title=title,
    )

    content_body = validated[
        "content_body"
    ]

    content_hash = validated[
        "content_hash"
    ]

    source_name = (
        _optional_string(
            source_identity.get(
                "canonical_url"
            )
        )
        or _optional_string(
            source_identity.get(
                "original_filename"
            )
        )
        or _optional_string(
            source_identity.get(
                "filename"
            )
        )
        or source_record_id
    )

    canonical_url = _optional_string(
        wuc.get(
            "canonical_url"
        )
    )

    uucd = {
        "schema_version":
            UUCD_SCHEMA_VERSION,

        "engine_version":
            UUCD_ENGINE_VERSION,

        "document_id":
            document_id,

        "workspace_id":
            workspace_id,

        "source_id":
            source_record_id,

        "source_type":
            source_type,

        "source_name":
            source_name,

        "source_format":
            validated[
                "source_format"
            ],

        "source_identity":
            source_identity,

        "title":
            title,

        "h1":
            _optional_string(
                wuc.get(
                    "h1"
                )
            ),

        "headings":
            deepcopy(
                list(
                    wuc.get(
                        "headings"
                    )
                    or []
                )
            ),

        "canonical_url":
            canonical_url,

        "content_body":
            content_body,

        "structure":
            deepcopy(
                dict(
                    validated[
                        "structure"
                    ]
                )
            ),

        "content_hash":
            content_hash,

        "content_ref":
            content_ref,

        "body_ref":
            body_ref,

        "body_status":
            "PENDING_BODY_STORE_WRITE",

        "body_length":
            validated[
                "body_length"
            ],

        "body_word_count":
            validated[
                "body_word_count"
            ],

        "metadata": {
            "wuc_schema_version":
                wuc.get(
                    "schema_version"
                ),

            "wuc_engine_version":
                wuc.get(
                    "engine_version"
                ),

            "wuc_content_id":
                validated[
                    "content_id"
                ],

            "wuc_document_id":
                wuc.get(
                    "document_id"
                ),

            "complete_content_preserved":
                True,

            "content_reduction_performed":
                False,

            "summarization_performed":
                False,

            "truncation_performed":
                False,

            "word_count_limit_applied":
                False,

            "uucd_persistence_mode":
                "TRANSIENT",

            "body_store_write_performed":
                False,

            "semantic_processing_performed":
                False,

            "source_metadata":
                deepcopy(
                    dict(
                        validated[
                            "metadata"
                        ]
                    )
                ),
        },

        "lifecycle": {
            "authorization_status":
                "PENDING_SOURCE_AUTHORIZATION",

            "lifecycle_status":
                "ACTIVE_PENDING_REGISTRY_ALIGNMENT",

            "disconnect_behavior":
                "PENDING_LIFECYCLE_POLICY",

            "purge_status":
                "NOT_REQUESTED",
        },

        "versioning": {
            "source_snapshot_reference":
                _optional_string(
                    source_identity.get(
                        "source_snapshot_reference"
                    )
                ),

            "version_asset_reference":
                _optional_string(
                    source_identity.get(
                        "version_asset_reference"
                    )
                ),

            "version_status":
                "PENDING_VERSION_REGISTRY_ALIGNMENT",
        },

        "provenance": {
            "input_stage":
                "website_unified_content",

            "input_content_id":
                validated[
                    "content_id"
                ],

            "source_record_id":
                source_record_id,

            "wuc_content_hash":
                content_hash,

            "full_body_received":
                True,

            "body_hash_verified":
                True,

            "body_length_verified":
                True,
        },

        "handoff": {
            "next_stage":
                "universal_article_body_store",

            "eligible_for_body_store":
                True,

            "body_field":
                "content_body",

            "body_ref":
                body_ref,

            "content_ref":
                content_ref,

            "full_body_handoff":
                True,
        },
    }

    missing_uucd_fields = sorted(
        REQUIRED_UUCD_FIELDS
        - set(
            uucd
        )
    )

    if missing_uucd_fields:
        raise UUCDContractError(
            "Generated UUCD is missing required fields: "
            + ", ".join(
                missing_uucd_fields
            )
        )

    if (
        uucd[
            "content_body"
        ]
        != wuc[
            "content_body"
        ]
    ):
        raise UUCDContractError(
            "UUCD content_body does not exactly match WUC."
        )

    if (
        compute_canonical_content_hash_v1(
            uucd[
                "content_body"
            ]
        )
        != uucd[
            "content_hash"
        ]
    ):
        raise UUCDContractError(
            "Generated UUCD content hash verification failed."
        )

    return uucd


def serialize_uucd_for_verification_v1(
    uucd: Mapping[str, Any],
) -> str:
    """Serialize transient UUCD deterministically for tests only."""

    return json.dumps(
        dict(
            uucd
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )
