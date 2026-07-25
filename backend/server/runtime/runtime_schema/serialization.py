# -*- coding: utf-8 -*-
"""Canonical serialization policy for Runtime Schema Management.

This module defines the single deterministic wire form used by schema
definitions, diffs, migration plans, snapshots, audit records, and
certification evidence.

Canonical rules:

* UTF-8 without a byte-order mark.
* JSON objects with lexicographically sorted keys.
* Compact separators and no insignificant whitespace.
* Unicode emitted directly rather than ASCII escape substitution.
* Mapping keys must be strings.
* Duplicate object keys are rejected during parsing.
* NaN, Infinity, and negative Infinity are rejected.
* Unsupported Python objects are rejected.
* Strict parsing verifies that input is already in canonical form.
* Serialized input is subject to a bounded size limit.

Equal logical structures therefore produce identical bytes and identical
fingerprints regardless of original mapping order or mutable container type.
"""

from __future__ import annotations

import json
from typing import Any, Final, Iterable

from .fingerprint import sha256_hex
from .types import (
    SchemaSerializationError,
    deep_freeze,
    deep_thaw,
)


SERIALIZATION_FORMAT_VERSION: Final[str] = "1.0.0"

CANONICAL_ENCODING: Final[str] = "utf-8"

CANONICAL_MEDIA_TYPE: Final[str] = (
    "application/json"
)

MAX_CANONICAL_DOCUMENT_BYTES: Final[int] = (
    16 * 1024 * 1024
)

_UTF8_BOM: Final[bytes] = b"\xef\xbb\xbf"


def _reject_nonfinite_constant(
    value: str,
) -> None:
    raise SchemaSerializationError(
        f"non-finite JSON number is not permitted: {value}"
    )


def _object_without_duplicates(
    pairs: Iterable[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for key, value in pairs:
        if key in result:
            raise SchemaSerializationError(
                f"duplicate JSON object key: {key!r}"
            )

        result[key] = value

    return result


def canonical_json(
    value: Any,
) -> str:
    """Return deterministic canonical JSON text for *value*."""
    normalized = deep_thaw(
        deep_freeze(value)
    )

    try:
        encoded = json.dumps(
            normalized,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (
        TypeError,
        ValueError,
        RecursionError,
    ) as exc:
        raise SchemaSerializationError(
            f"value cannot be canonically serialized: {exc}"
        ) from exc

    encoded_size = len(
        encoded.encode(CANONICAL_ENCODING)
    )

    if encoded_size > MAX_CANONICAL_DOCUMENT_BYTES:
        raise SchemaSerializationError(
            "canonical JSON exceeds the maximum "
            f"size of {MAX_CANONICAL_DOCUMENT_BYTES} bytes"
        )

    return encoded


def canonical_bytes(
    value: Any,
) -> bytes:
    """Return canonical JSON encoded as UTF-8 bytes."""
    return canonical_json(value).encode(
        CANONICAL_ENCODING
    )


def parse_canonical_json(
    text: str | bytes | bytearray,
    *,
    require_canonical: bool = True,
) -> Any:
    """Parse canonical JSON into plain JSON-native Python structures.

    When ``require_canonical`` is true, the original input must exactly match
    the subsystem's canonical encoding. This rejects insignificant
    whitespace, unsorted keys, alternate Unicode escaping, and other
    semantically equivalent but noncanonical representations.
    """
    if isinstance(text, (bytes, bytearray)):
        raw = bytes(text)

        if raw.startswith(_UTF8_BOM):
            raise SchemaSerializationError(
                "canonical JSON must not contain a UTF-8 BOM"
            )

        if len(raw) > MAX_CANONICAL_DOCUMENT_BYTES:
            raise SchemaSerializationError(
                "canonical JSON exceeds the maximum "
                f"size of {MAX_CANONICAL_DOCUMENT_BYTES} bytes"
            )

        try:
            decoded = raw.decode(
                CANONICAL_ENCODING,
                errors="strict",
            )
        except UnicodeDecodeError as exc:
            raise SchemaSerializationError(
                f"canonical JSON must be valid UTF-8: {exc}"
            ) from exc
    elif isinstance(text, str):
        decoded = text

        if decoded.startswith("\ufeff"):
            raise SchemaSerializationError(
                "canonical JSON must not contain a Unicode BOM"
            )

        if (
            len(decoded.encode(CANONICAL_ENCODING))
            > MAX_CANONICAL_DOCUMENT_BYTES
        ):
            raise SchemaSerializationError(
                "canonical JSON exceeds the maximum "
                f"size of {MAX_CANONICAL_DOCUMENT_BYTES} bytes"
            )
    else:
        raise SchemaSerializationError(
            "expected str, bytes, or bytearray containing JSON"
        )

    try:
        parsed = json.loads(
            decoded,
            object_pairs_hook=_object_without_duplicates,
            parse_constant=_reject_nonfinite_constant,
        )
    except SchemaSerializationError:
        raise
    except (
        json.JSONDecodeError,
        RecursionError,
        ValueError,
    ) as exc:
        raise SchemaSerializationError(
            f"malformed JSON: {exc}"
        ) from exc

    try:
        normalized = deep_thaw(
            deep_freeze(parsed)
        )
    except SchemaSerializationError:
        raise
    except Exception as exc:
        raise SchemaSerializationError(
            f"parsed JSON contains unsupported content: {exc}"
        ) from exc

    if require_canonical:
        expected = canonical_json(
            normalized
        )

        if decoded != expected:
            raise SchemaSerializationError(
                "JSON is valid but is not in canonical form"
            )

    return normalized


def is_canonical_json(
    text: object,
) -> bool:
    """Return whether *text* is valid strict canonical JSON."""
    if not isinstance(
        text,
        (str, bytes, bytearray),
    ):
        return False

    try:
        parse_canonical_json(
            text,
            require_canonical=True,
        )
    except SchemaSerializationError:
        return False

    return True


def structure_fingerprint(
    value: Any,
) -> str:
    """Return a deterministic SHA-256 fingerprint of *value*."""
    return sha256_hex(
        canonical_bytes(value)
    )


def verify_structure_fingerprint(
    value: Any,
    expected_fingerprint: str,
) -> bool:
    """Return whether *value* matches an expected content fingerprint."""
    if not isinstance(
        expected_fingerprint,
        str,
    ):
        return False

    return (
        structure_fingerprint(value)
        == expected_fingerprint
    )


def canonical_round_trip(
    value: Any,
) -> Any:
    """Serialize and strictly parse *value* using the canonical policy."""
    return parse_canonical_json(
        canonical_bytes(value),
        require_canonical=True,
    )


__all__ = [
    "CANONICAL_ENCODING",
    "CANONICAL_MEDIA_TYPE",
    "MAX_CANONICAL_DOCUMENT_BYTES",
    "SERIALIZATION_FORMAT_VERSION",
    "canonical_bytes",
    "canonical_json",
    "canonical_round_trip",
    "is_canonical_json",
    "parse_canonical_json",
    "structure_fingerprint",
    "verify_structure_fingerprint",
]
