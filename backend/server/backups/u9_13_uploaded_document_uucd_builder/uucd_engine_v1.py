"""Canonical UUCD Option 3 engine.

The engine converts one frozen WUC package into a Universal Handoff
Envelope containing:

1. A canonical UUCD record without content_body.
2. A transient Universal Body Payload containing the exact full body.
3. A binding record proving both components belong together.

No persistence, Body Store writing, runtime execution, queueing,
semantic processing, truncation, or summarization occurs here.
"""

from __future__ import annotations

import hashlib
import re
from copy import deepcopy
from typing import Any, Mapping


UUCD_SCHEMA_VERSION = (
    "universal_unified_content_document_v2"
)

BODY_PAYLOAD_SCHEMA_VERSION = (
    "universal_body_payload_v1"
)

HANDOFF_ENVELOPE_SCHEMA_VERSION = (
    "universal_handoff_envelope_v1"
)

UUCD_ENGINE_VERSION = (
    "uucd_engine_v1_option3_bound_body_payload"
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

REQUIRED_UUCD_RECORD_FIELDS = {
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

REQUIRED_BODY_PAYLOAD_FIELDS = {
    "payload_schema_version",
    "document_id",
    "workspace_id",
    "source_type",
    "content_body",
    "content_hash",
    "body_length",
    "body_word_count",
    "body_ref",
    "content_encoding",
}

REQUIRED_BINDING_FIELDS = {
    "document_id",
    "workspace_id",
    "source_type",
    "content_hash",
    "body_length",
    "body_word_count",
    "body_ref",
    "binding_hash",
    "binding_status",
}

BINDING_FIELD_NAMES = (
    "document_id",
    "workspace_id",
    "source_type",
    "content_hash",
    "body_length",
    "body_word_count",
    "body_ref",
)


class UUCDContractError(
    ValueError
):
    """Raised when a WUC package or handoff envelope is invalid."""


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

    return str(
        value
    ).strip()


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
    """Hash the exact body without normalization."""

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
    identity = "\x00".join(
        (
            workspace_id,
            source_type,
            source_record_id,
        )
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


def _binding_hash(
    values: Mapping[str, Any],
) -> str:
    serialized = "\x00".join(
        str(
            values[
                field
            ]
        )
        for field in BINDING_FIELD_NAMES
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()


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
            "WUC package is missing fields: "
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

    missing_handoff = sorted(
        REQUIRED_WUC_HANDOFF_FIELDS
        - set(
            handoff
        )
    )

    if missing_handoff:
        raise UUCDContractError(
            "WUC handoff is missing fields: "
            + ", ".join(
                missing_handoff
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
            "WUC does not certify full-body handoff."
        )

    if handoff.get(
        "body_field"
    ) != "content_body":
        raise UUCDContractError(
            "WUC handoff body_field must be content_body."
        )

    if metadata.get(
        "complete_content_preserved"
    ) is not True:
        raise UUCDContractError(
            "WUC does not certify complete content."
        )

    for field in (
        "content_reduction_performed",
        "summarization_performed",
        "truncation_performed",
        "word_count_limit_applied",
    ):
        if metadata.get(
            field
        ) is not False:
            raise UUCDContractError(
                "WUC metadata violates frozen rule: "
                + field
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
            "WUC content_hash does not match content_body."
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
            "WUC body_length is invalid."
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
            "WUC body_word_count is invalid."
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

        "content_hash":
            calculated_hash,

        "body_length":
            body_length,

        "body_word_count":
            body_word_count,

        "source_identity":
            source_identity,

        "source_record_id":
            source_record_id,

        "structure":
            structure,

        "metadata":
            metadata,
    }


def build_transient_uucd_from_wuc_v1(
    wuc_package: Mapping[str, Any],
) -> dict[str, Any]:
    """Create the frozen Option 3 Universal Handoff Envelope."""

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

    content_hash = validated[
        "content_hash"
    ]

    body_length = validated[
        "body_length"
    ]

    body_word_count = validated[
        "body_word_count"
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

    uucd_record = {
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
            _optional_string(
                wuc.get(
                    "canonical_url"
                )
            ),

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
            body_length,

        "body_word_count":
            body_word_count,

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

            "complete_content_preserved":
                True,

            "content_body_in_uucd_record":
                False,

            "body_transport":
                "UNIVERSAL_BODY_PAYLOAD",

            "content_reduction_performed":
                False,

            "summarization_performed":
                False,

            "truncation_performed":
                False,

            "word_count_limit_applied":
                False,

            "semantic_processing_performed":
                False,

            "persistence_status":
                "NOT_PERSISTED",
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

            "full_body_received_from_wuc":
                True,

            "full_body_moved_to_body_payload":
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

            "body_transport":
                "body_payload",

            "body_ref":
                body_ref,

            "content_ref":
                content_ref,

            "requires_verified_body_before_persistence":
                True,
        },
    }

    body_payload = {
        "payload_schema_version":
            BODY_PAYLOAD_SCHEMA_VERSION,

        "document_id":
            document_id,

        "workspace_id":
            workspace_id,

        "source_type":
            source_type,

        "content_body":
            validated[
                "content_body"
            ],

        "content_hash":
            content_hash,

        "body_length":
            body_length,

        "body_word_count":
            body_word_count,

        "body_ref":
            body_ref,

        "content_encoding":
            "utf-8",
    }

    binding_values = {
        field:
            uucd_record[
                field
            ]
        for field in BINDING_FIELD_NAMES
    }

    binding = {
        **binding_values,

        "binding_hash":
            _binding_hash(
                binding_values
            ),

        "binding_status":
            "BOUND_AND_VERIFIED",
    }

    envelope = {
        "envelope_schema_version":
            HANDOFF_ENVELOPE_SCHEMA_VERSION,

        "engine_version":
            UUCD_ENGINE_VERSION,

        "uucd_record":
            uucd_record,

        "body_payload":
            body_payload,

        "binding":
            binding,

        "envelope_status":
            "READY_FOR_BODY_STORE",
    }

    validate_universal_handoff_envelope_v1(
        envelope
    )

    return envelope


def validate_universal_handoff_envelope_v1(
    envelope: Mapping[str, Any],
) -> bool:
    """Validate the UUCD record, body payload, and binding."""

    envelope_mapping = _require_mapping(
        envelope,
        field_name="envelope",
    )

    uucd_record = _require_mapping(
        envelope_mapping.get(
            "uucd_record"
        ),
        field_name="uucd_record",
    )

    body_payload = _require_mapping(
        envelope_mapping.get(
            "body_payload"
        ),
        field_name="body_payload",
    )

    binding = _require_mapping(
        envelope_mapping.get(
            "binding"
        ),
        field_name="binding",
    )

    missing_record_fields = sorted(
        REQUIRED_UUCD_RECORD_FIELDS
        - set(
            uucd_record
        )
    )

    if missing_record_fields:
        raise UUCDContractError(
            "UUCD record is missing fields: "
            + ", ".join(
                missing_record_fields
            )
        )

    if "content_body" in uucd_record:
        raise UUCDContractError(
            "UUCD record must not contain content_body."
        )

    missing_payload_fields = sorted(
        REQUIRED_BODY_PAYLOAD_FIELDS
        - set(
            body_payload
        )
    )

    if missing_payload_fields:
        raise UUCDContractError(
            "Body payload is missing fields: "
            + ", ".join(
                missing_payload_fields
            )
        )

    missing_binding_fields = sorted(
        REQUIRED_BINDING_FIELDS
        - set(
            binding
        )
    )

    if missing_binding_fields:
        raise UUCDContractError(
            "Binding is missing fields: "
            + ", ".join(
                missing_binding_fields
            )
        )

    for field in BINDING_FIELD_NAMES:
        record_value = uucd_record.get(
            field
        )

        payload_value = body_payload.get(
            field
        )

        binding_value = binding.get(
            field
        )

        if not (
            record_value
            == payload_value
            == binding_value
        ):
            raise UUCDContractError(
                "Envelope binding mismatch for field: "
                + field
            )

    calculated_body_hash = (
        compute_canonical_content_hash_v1(
            body_payload[
                "content_body"
            ]
        )
    )

    if calculated_body_hash != body_payload[
        "content_hash"
    ]:
        raise UUCDContractError(
            "Body payload content_hash is invalid."
        )

    if len(
        body_payload[
            "content_body"
        ]
    ) != body_payload[
        "body_length"
    ]:
        raise UUCDContractError(
            "Body payload body_length is invalid."
        )

    expected_binding_hash = _binding_hash(
        {
            field:
                binding[
                    field
                ]
            for field in BINDING_FIELD_NAMES
        }
    )

    if binding.get(
        "binding_hash"
    ) != expected_binding_hash:
        raise UUCDContractError(
            "Binding hash is invalid."
        )

    if binding.get(
        "binding_status"
    ) != "BOUND_AND_VERIFIED":
        raise UUCDContractError(
            "Binding status is invalid."
        )

    if uucd_record.get(
        "body_status"
    ) != "PENDING_BODY_STORE_WRITE":
        raise UUCDContractError(
            "UUCD body_status must be PENDING_BODY_STORE_WRITE."
        )

    return True
