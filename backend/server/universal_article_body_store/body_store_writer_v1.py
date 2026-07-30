"""Canonical Universal Article Body Store Writer.

This writer consumes one validated Universal Handoff Envelope and
persists only the exact content body carried by body_payload.

It does not:
- persist the UUCD Record;
- perform semantic processing;
- create runtime jobs or queues;
- summarize, truncate, normalize, or rewrite article content.
"""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


from backend.server.common.text_statistics import count_words

from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    UUCDContractError,
    compute_canonical_content_hash_v1,
    validate_universal_handoff_envelope_v1,
)


BODY_STORE_WRITER_VERSION = (
    "universal_article_body_store_writer_v1"
)

BODY_STORE_ROOT_RELATIVE = (
    Path("backend")
    / "server"
    / "data"
    / "universal_article_body_store"
)

WORKSPACE_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$"
)

DOCUMENT_ID_PATTERN = re.compile(
    r"^uucd_[a-f0-9]{32}$"
)


class BodyStoreContractError(
    ValueError
):
    """Raised when a Body Store write contract is invalid."""


def _utc_now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(
        value,
        Mapping,
    ):
        raise BodyStoreContractError(
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
        raise BodyStoreContractError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise BodyStoreContractError(
            field_name
            + " must not be empty."
        )

    return normalized


def _count_words(
    content_body: str,
) -> int:
    return count_words(
        content_body
    )


def _utf8_byte_length(
    content_body: str,
) -> int:
    return len(
        content_body.encode(
            "utf-8"
        )
    )


def _sha256_bytes(
    payload: bytes,
) -> str:
    return hashlib.sha256(
        payload
    ).hexdigest()


def _is_inside(
    candidate: Path,
    parent: Path,
) -> bool:
    try:
        candidate.relative_to(
            parent
        )

        return True

    except ValueError:
        return False


def _canonical_body_ref(
    *,
    project_root: Path,
    workspace_id: str,
    supplied_body_ref: str,
) -> tuple[Path, Path]:
    project_root_resolved = (
        project_root.resolve()
    )

    canonical_store_root = (
        project_root_resolved
        / BODY_STORE_ROOT_RELATIVE
    ).resolve()

    workspace_body_root = (
        canonical_store_root
        / workspace_id
        / "bodies"
    ).resolve()

    supplied_path = Path(
        supplied_body_ref
    )

    if supplied_path.is_absolute():
        resolved_body_path = (
            supplied_path.resolve()
        )

    else:
        resolved_body_path = (
            project_root_resolved
            / supplied_path
        ).resolve()

    if not _is_inside(
        resolved_body_path,
        workspace_body_root,
    ):
        raise BodyStoreContractError(
            "body_ref escapes the canonical workspace Body Store."
        )

    if (
        resolved_body_path.parent
        != workspace_body_root
    ):
        raise BodyStoreContractError(
            "body_ref must point directly inside the workspace bodies directory."
        )

    if (
        resolved_body_path.suffix.casefold()
        != ".txt"
    ):
        raise BodyStoreContractError(
            "Body Store files must use the .txt extension."
        )

    return (
        workspace_body_root,
        resolved_body_path,
    )


def _validate_body_payload(
    envelope: Mapping[str, Any],
    *,
    project_root: Path,
) -> dict[str, Any]:
    try:
        validate_universal_handoff_envelope_v1(
            envelope
        )

    except UUCDContractError as exc:
        raise BodyStoreContractError(
            "Universal Handoff Envelope validation failed: "
            + str(
                exc
            )
        ) from exc

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

    workspace_id = _require_non_empty_string(
        body_payload.get(
            "workspace_id"
        ),
        field_name="body_payload.workspace_id",
    )

    if not WORKSPACE_PATTERN.fullmatch(
        workspace_id
    ):
        raise BodyStoreContractError(
            "workspace_id contains invalid characters."
        )

    document_id = _require_non_empty_string(
        body_payload.get(
            "document_id"
        ),
        field_name="body_payload.document_id",
    )

    if not DOCUMENT_ID_PATTERN.fullmatch(
        document_id
    ):
        raise BodyStoreContractError(
            "document_id does not match the canonical UUCD format."
        )

    source_type = _require_non_empty_string(
        body_payload.get(
            "source_type"
        ),
        field_name="body_payload.source_type",
    )

    content_body = body_payload.get(
        "content_body"
    )

    if not isinstance(
        content_body,
        str,
    ):
        raise BodyStoreContractError(
            "body_payload.content_body must be a string."
        )

    if not content_body:
        raise BodyStoreContractError(
            "body_payload.content_body must not be empty."
        )

    content_encoding = _require_non_empty_string(
        body_payload.get(
            "content_encoding"
        ),
        field_name="body_payload.content_encoding",
    ).casefold()

    if content_encoding not in {
        "utf-8",
        "utf8",
    }:
        raise BodyStoreContractError(
            "Only UTF-8 body payloads are supported."
        )

    supplied_content_hash = (
        _require_non_empty_string(
            body_payload.get(
                "content_hash"
            ),
            field_name="body_payload.content_hash",
        )
    )

    calculated_content_hash = (
        compute_canonical_content_hash_v1(
            content_body
        )
    )

    if (
        supplied_content_hash
        != calculated_content_hash
    ):
        raise BodyStoreContractError(
            "Body payload content_hash does not match content_body."
        )

    supplied_body_length = (
        body_payload.get(
            "body_length"
        )
    )

    if (
        not isinstance(
            supplied_body_length,
            int,
        )
        or supplied_body_length
        != len(
            content_body
        )
    ):
        raise BodyStoreContractError(
            "Body payload body_length is invalid."
        )

    supplied_word_count = (
        body_payload.get(
            "body_word_count"
        )
    )

    calculated_word_count = (
        _count_words(
            content_body
        )
    )

    if (
        not isinstance(
            supplied_word_count,
            int,
        )
        or supplied_word_count
        != calculated_word_count
    ):
        raise BodyStoreContractError(
            "Body payload body_word_count is invalid."
        )

    body_ref = _require_non_empty_string(
        body_payload.get(
            "body_ref"
        ),
        field_name="body_payload.body_ref",
    )

    (
        workspace_body_root,
        body_path,
    ) = _canonical_body_ref(
        project_root=project_root,
        workspace_id=workspace_id,
        supplied_body_ref=body_ref,
    )

    if (
        uucd_record.get(
            "body_status"
        )
        != "PENDING_BODY_STORE_WRITE"
    ):
        raise BodyStoreContractError(
            "UUCD Record is not pending a Body Store write."
        )

    if (
        uucd_record.get(
            "handoff",
            {},
        ).get(
            "eligible_for_body_store"
        )
        is not True
    ):
        raise BodyStoreContractError(
            "UUCD Record is not eligible for the Body Store."
        )

    if (
        envelope_mapping.get(
            "envelope_status"
        )
        != "READY_FOR_BODY_STORE"
    ):
        raise BodyStoreContractError(
            "Envelope status is not READY_FOR_BODY_STORE."
        )

    if (
        binding.get(
            "binding_status"
        )
        != "BOUND_AND_VERIFIED"
    ):
        raise BodyStoreContractError(
            "Envelope binding is not verified."
        )

    return {
        "uucd_record":
            uucd_record,

        "body_payload":
            body_payload,

        "binding":
            binding,

        "workspace_id":
            workspace_id,

        "document_id":
            document_id,

        "source_type":
            source_type,

        "content_body":
            content_body,

        "content_hash":
            calculated_content_hash,

        "body_length":
            supplied_body_length,

        "body_word_count":
            calculated_word_count,

        "body_byte_length":
            _utf8_byte_length(
                content_body
            ),

        "body_ref":
            body_ref,

        "workspace_body_root":
            workspace_body_root,

        "body_path":
            body_path,
    }


def _write_body_atomically(
    *,
    body_path: Path,
    content_body: str,
) -> None:
    body_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            delete=False,
            dir=str(
                body_path.parent
            ),
            prefix=(
                "."
                + body_path.name
                + "."
            ),
            suffix=".tmp",
        ) as temporary_file:
            temporary_file.write(
                content_body
            )

            temporary_file.flush()

            os.fsync(
                temporary_file.fileno()
            )

            temporary_path = Path(
                temporary_file.name
            )

        os.replace(
            temporary_path,
            body_path,
        )

        temporary_path = None

    finally:
        if (
            temporary_path is not None
            and temporary_path.exists()
        ):
            temporary_path.unlink()


def write_verified_body_from_envelope_v1(
    envelope: Mapping[str, Any],
    *,
    project_root: str | Path,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Persist and verify one exact body from a handoff envelope.

    The returned finalized_uucd_record exists only in memory. This
    function does not persist the UUCD Record.
    """

    root = Path(
        project_root
    ).resolve()

    validated = _validate_body_payload(
        envelope,
        project_root=root,
    )

    body_path: Path = validated[
        "body_path"
    ]

    expected_body = validated[
        "content_body"
    ]

    expected_hash = validated[
        "content_hash"
    ]

    expected_length = validated[
        "body_length"
    ]

    expected_word_count = validated[
        "body_word_count"
    ]

    expected_byte_length = validated[
        "body_byte_length"
    ]

    existing_file_action = (
        "CREATED"
    )

    if body_path.exists():
        existing_bytes = (
            body_path.read_bytes()
        )

        existing_hash = (
            _sha256_bytes(
                existing_bytes
            )
        )

        expected_bytes = (
            expected_body.encode(
                "utf-8"
            )
        )

        if existing_bytes == expected_bytes:
            existing_file_action = (
                "EXISTING_IDENTICAL_REUSED"
            )

        elif not overwrite:
            raise BodyStoreContractError(
                "A different body already exists at body_ref."
            )

        else:
            existing_file_action = (
                "OVERWRITTEN"
            )

    if (
        existing_file_action
        != "EXISTING_IDENTICAL_REUSED"
    ):
        _write_body_atomically(
            body_path=body_path,
            content_body=expected_body,
        )

    if not body_path.is_file():
        raise BodyStoreContractError(
            "Body Store write did not create the expected file."
        )

    stored_bytes = (
        body_path.read_bytes()
    )

    try:
        stored_body = (
            stored_bytes.decode(
                "utf-8"
            )
        )

    except UnicodeDecodeError as exc:
        raise BodyStoreContractError(
            "Stored body is not valid UTF-8."
        ) from exc

    stored_hash = (
        _sha256_bytes(
            stored_bytes
        )
    )

    stored_character_length = len(
        stored_body
    )

    stored_byte_length = len(
        stored_bytes
    )

    stored_word_count = (
        _count_words(
            stored_body
        )
    )

    exact_content_match = (
        stored_body
        == expected_body
    )

    hash_verified = (
        stored_hash
        == expected_hash
    )

    character_length_verified = (
        stored_character_length
        == expected_length
    )

    byte_length_verified = (
        stored_byte_length
        == expected_byte_length
    )

    word_count_verified = (
        stored_word_count
        == expected_word_count
    )

    if not all(
        (
            exact_content_match,
            hash_verified,
            character_length_verified,
            byte_length_verified,
            word_count_verified,
        )
    ):
        raise BodyStoreContractError(
            "Stored body failed post-write verification."
        )

    finalized_uucd_record = deepcopy(
        dict(
            validated[
                "uucd_record"
            ]
        )
    )

    finalized_uucd_record[
        "body_status"
    ] = "STORED_AND_VERIFIED"

    finalized_uucd_record[
        "metadata"
    ] = deepcopy(
        dict(
            finalized_uucd_record.get(
                "metadata"
            )
            or {}
        )
    )

    finalized_uucd_record[
        "metadata"
    ].update(
        {
            "body_store_writer_version":
                BODY_STORE_WRITER_VERSION,

            "body_store_write_verified":
                True,

            "body_store_write_timestamp":
                _utc_now_iso(),

            "persistence_status":
                "READY_FOR_UUCD_PERSISTENCE",
        }
    )

    finalized_uucd_record[
        "handoff"
    ] = deepcopy(
        dict(
            finalized_uucd_record.get(
                "handoff"
            )
            or {}
        )
    )

    finalized_uucd_record[
        "handoff"
    ].update(
        {
            "next_stage":
                "uucd_persistence",

            "eligible_for_body_store":
                False,

            "eligible_for_uucd_persistence":
                True,

            "body_store_verified":
                True,
        }
    )

    write_certificate = {
        "certificate_schema_version":
            "body_store_write_certificate_v1",

        "writer_version":
            BODY_STORE_WRITER_VERSION,

        "certificate_status":
            "CERTIFIED",

        "document_id":
            validated[
                "document_id"
            ],

        "workspace_id":
            validated[
                "workspace_id"
            ],

        "source_type":
            validated[
                "source_type"
            ],

        "body_ref":
            validated[
                "body_ref"
            ],

        "stored_path":
            str(
                body_path
            ),

        "content_hash":
            expected_hash,

        "body_length":
            expected_length,

        "body_byte_length":
            expected_byte_length,

        "body_word_count":
            expected_word_count,

        "binding_hash":
            validated[
                "binding"
            ][
                "binding_hash"
            ],

        "existing_file_action":
            existing_file_action,

        "exact_content_match":
            exact_content_match,

        "hash_verified":
            hash_verified,

        "character_length_verified":
            character_length_verified,

        "byte_length_verified":
            byte_length_verified,

        "word_count_verified":
            word_count_verified,

        "written_at":
            _utc_now_iso(),

        "uucd_record_persisted":
            False,

        "runtime_executed":
            False,

        "semantic_processing_performed":
            False,
    }

    return {
        "write_status":
            "STORED_AND_VERIFIED",

        "body_path":
            str(
                body_path
            ),

        "write_certificate":
            write_certificate,

        "finalized_uucd_record":
            finalized_uucd_record,
    }

