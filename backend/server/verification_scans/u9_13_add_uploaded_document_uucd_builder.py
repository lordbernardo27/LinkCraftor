from pathlib import Path


path = Path(
    "backend/server/universal_unified_content_document/"
    "uucd_engine_v1.py"
)

raw = path.read_bytes()

had_bom = raw.startswith(
    b"\xef\xbb\xbf"
)

source = raw.decode(
    "utf-8-sig"
)

function_name = (
    "def build_transient_uucd_from_uduc_v1("
)

if function_name in source:
    print(
        "U9.13_PATCH_STATUS="
        "BUILDER_ALREADY_PRESENT"
    )
else:
    marker = (
        "def build_transient_uucd_from_wuc_v1("
    )

    if marker not in source:
        raise RuntimeError(
            "Could not locate canonical WUC builder "
            "insertion point."
        )

    block = r'''
def _validate_uduc_contract_v1(
    uduc_package: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Validate the canonical Uploaded Document UDUC input
    before convergence into the Current Canonical
    Option-3 UUCD handoff envelope.

    This validator does not reread the source file,
    rerun extraction, rerun normalization, or mutate
    the supplied UDUC mapping.
    """

    uduc = _require_mapping(
        uduc_package,
        field_name="uduc_package",
    )

    expected_schema = (
        "uploaded_document_unified_content_v2"
    )

    expected_pipeline = (
        "uploaded_document_uduc_pipeline_v2"
    )

    if uduc.get(
        "schema_version"
    ) != expected_schema:
        raise UUCDContractError(
            "UDUC schema_version is invalid."
        )

    if uduc.get(
        "pipeline_version"
    ) != expected_pipeline:
        raise UUCDContractError(
            "UDUC pipeline_version is invalid."
        )

    if uduc.get(
        "source_type"
    ) != "uploaded_document":
        raise UUCDContractError(
            "UDUC source_type must be "
            "'uploaded_document'."
        )

    required_strings = (
        "workspace_id",
        "document_id",
        "source_format",
        "original_filename",
        "stored_filename",
        "stored_path",
        "title",
        "content_body",
        "extraction_status",
        "extraction_created_at",
        "normalization_status",
        "normalization_version",
        "normalized_at",
        "created_at",
    )

    for field in required_strings:
        value = uduc.get(
            field
        )

        if (
            not isinstance(
                value,
                str,
            )
            or not value
        ):
            raise UUCDContractError(
                f"UDUC {field} must be a "
                "non-empty string."
            )

    confidence = uduc.get(
        "extraction_confidence"
    )

    if (
        not isinstance(
            confidence,
            (int, float),
        )
        or isinstance(
            confidence,
            bool,
        )
    ):
        raise UUCDContractError(
            "UDUC extraction_confidence must "
            "be numeric."
        )

    headings = uduc.get(
        "headings"
    )

    if not isinstance(
        headings,
        list,
    ):
        raise UUCDContractError(
            "UDUC headings must be a list."
        )

    if not all(
        isinstance(
            heading,
            str,
        )
        for heading in headings
    ):
        raise UUCDContractError(
            "UDUC headings must contain "
            "strings only."
        )

    h1 = uduc.get(
        "h1"
    )

    if not isinstance(
        h1,
        str,
    ):
        raise UUCDContractError(
            "UDUC h1 must be a string."
        )

    structure = _require_mapping(
        uduc.get(
            "structure"
        ),
        field_name="uduc.structure",
    )

    metadata = _require_mapping(
        uduc.get(
            "metadata"
        ),
        field_name="uduc.metadata",
    )

    expected_structure_version = (
        "uduc_structure_v1_2"
    )

    if structure.get(
        "structure_version"
    ) != expected_structure_version:
        raise UUCDContractError(
            "UDUC structure_version is invalid."
        )

    return dict(
        uduc
    )


def build_transient_uucd_from_uduc_v1(
    uduc_package: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the Current Canonical Option-3 UUCD
    Universal Handoff Envelope from canonical
    Uploaded Document UDUC.

    Boundary:
        canonical UDUC
        -> transient UUCD record
        -> body payload
        -> binding
        -> READY_FOR_BODY_STORE envelope

    This function does not:
        - reread the uploaded source file
        - rerun extraction
        - rerun normalization
        - convert UDUC into WUC
        - execute semantic intelligence
        - execute scorer/highlight/runtime logic
        - write the Body Store
        - persist the finalized UUCD
    """

    from copy import deepcopy

    validated = _validate_uduc_contract_v1(
        uduc_package
    )

    workspace_id = validated[
        "workspace_id"
    ]

    source_type = (
        "uploaded_document"
    )

    source_record_id = validated[
        "document_id"
    ]

    title = validated[
        "title"
    ]

    content_body = validated[
        "content_body"
    ]

    source_format = validated[
        "source_format"
    ]

    metadata_in = _require_mapping(
        validated[
            "metadata"
        ],
        field_name="uduc.metadata",
    )

    structure_in = _require_mapping(
        validated[
            "structure"
        ],
        field_name="uduc.structure",
    )

    source_metadata = _require_mapping(
        metadata_in.get(
            "source_metadata",
            {},
        ),
        field_name=(
            "uduc.metadata.source_metadata"
        ),
    )

    normalization_details = (
        metadata_in.get(
            "normalization",
            {},
        )
    )

    if not isinstance(
        normalization_details,
        Mapping,
    ):
        raise UUCDContractError(
            "UDUC metadata.normalization must "
            "be a mapping."
        )

    metadata_boundary = (
        metadata_in.get(
            "boundary",
            {},
        )
    )

    if not isinstance(
        metadata_boundary,
        Mapping,
    ):
        raise UUCDContractError(
            "UDUC metadata.boundary must "
            "be a mapping."
        )

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

    content_hash = (
        compute_canonical_content_hash_v1(
            content_body
        )
    )

    body_length = len(
        content_body
    )

    body_word_count = len(
        content_body.split()
    )

    original_filename = validated[
        "original_filename"
    ]

    stored_filename = validated[
        "stored_filename"
    ]

    source_name = (
        original_filename
        or stored_filename
        or source_record_id
    )

    source_identity = {
        "source_record_id":
            source_record_id,

        "original_filename":
            original_filename,

        "stored_filename":
            stored_filename,

        "stored_path":
            validated[
                "stored_path"
            ],
    }

    for optional_key in (
        "source_snapshot_reference",
        "version_asset_reference",
    ):
        optional_value = (
            source_metadata.get(
                optional_key
            )
        )

        if (
            isinstance(
                optional_value,
                str,
            )
            and optional_value.strip()
        ):
            source_identity[
                optional_key
            ] = optional_value

    uucd_metadata = {
        "uduc_schema_version":
            validated[
                "schema_version"
            ],

        "uduc_pipeline_version":
            validated[
                "pipeline_version"
            ],

        "uduc_created_at":
            validated[
                "created_at"
            ],

        "uduc_structure_version":
            structure_in.get(
                "structure_version"
            ),

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

        "source_metadata":
            deepcopy(
                dict(
                    source_metadata
                )
            ),

        "extraction": {
            "status":
                validated[
                    "extraction_status"
                ],

            "confidence":
                validated[
                    "extraction_confidence"
                ],

            "created_at":
                validated[
                    "extraction_created_at"
                ],

            "method":
                metadata_in.get(
                    "extraction_method"
                ),

            "timestamp":
                metadata_in.get(
                    "extraction_timestamp"
                ),

            "source_format":
                source_format,

            "extension":
                metadata_in.get(
                    "extension"
                ),

            "file_size":
                metadata_in.get(
                    "file_size"
                ),

            "source_metadata":
                deepcopy(
                    dict(
                        source_metadata
                    )
                ),
        },

        "normalization": {
            "status":
                validated[
                    "normalization_status"
                ],

            "version":
                validated[
                    "normalization_version"
                ],

            "normalized_at":
                validated[
                    "normalized_at"
                ],

            "details":
                deepcopy(
                    dict(
                        normalization_details
                    )
                ),

            "boundary":
                deepcopy(
                    dict(
                        metadata_boundary
                    )
                ),
        },
    }

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
            source_format,

        "source_identity":
            source_identity,

        "title":
            title,

        "h1":
            validated[
                "h1"
            ],

        "headings":
            deepcopy(
                validated[
                    "headings"
                ]
            ),

        "canonical_url":
            "",

        "structure":
            deepcopy(
                dict(
                    structure_in
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

        "metadata":
            uucd_metadata,

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
                "uploaded_document_unified_content",

            "input_content_id":
                source_record_id,

            "source_record_id":
                source_record_id,

            "full_body_received_from_uduc":
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
            content_body,

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

    if (
        compute_canonical_content_hash_v1(
            body_payload[
                "content_body"
            ]
        )
        != content_hash
    ):
        raise UUCDContractError(
            "UDUC body hash verification failed."
        )

    if (
        len(
            body_payload[
                "content_body"
            ]
        )
        != body_length
    ):
        raise UUCDContractError(
            "UDUC body length verification failed."
        )

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


'''

    source = source.replace(
        marker,
        block + marker,
        1,
    )

    encoding = (
        "utf-8-sig"
        if had_bom
        else "utf-8"
    )

    path.write_text(
        source,
        encoding=encoding,
        newline="\n",
    )

    print(
        "U9.13_PATCH_STATUS="
        "UPLOADED_DOCUMENT_BUILDER_ADDED"
    )

print(
    "TARGET="
    + str(path)
)