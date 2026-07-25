# -*- coding: utf-8 -*-
"""Deterministic hashing primitives for Runtime Schema Management.

This module owns schema identifiers, integrity fingerprints, and hash-chain
links. It depends only on :mod:`runtime_schema.types`, preserving the strict
package dependency graph.

``schema_id`` and content fingerprints are deliberately different:

* ``schema_id`` identifies ``namespace/name@version``.
* A content fingerprint verifies serialized content integrity.
"""

from __future__ import annotations

import hashlib
import re
from typing import Final

from .types import (
    SchemaSerializationError,
    is_valid_name,
    is_valid_namespace,
)


FINGERPRINT_ALGORITHM: Final[str] = "sha256"

SHA256_HEX_LENGTH: Final[int] = 64

SCHEMA_ID_PREFIX: Final[str] = "sch_"

SCHEMA_ID_HEX_LENGTH: Final[int] = 32

MAX_COORDINATE_LENGTH: Final[int] = 512

_SHA256_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{64}$"
)

_VERSION_RE: Final[re.Pattern[str]] = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)$"
)


def sha256_hex(
    data: str | bytes | bytearray,
) -> str:
    """Return the lowercase SHA-256 hexadecimal digest of *data*."""
    if isinstance(data, str):
        encoded = data.encode("utf-8")
    elif isinstance(data, (bytes, bytearray)):
        encoded = bytes(data)
    else:
        raise SchemaSerializationError(
            "sha256_hex expects str, bytes, or bytearray"
        )

    return hashlib.sha256(encoded).hexdigest()


def fingerprint_bytes(
    data: bytes | bytearray,
) -> str:
    """Return the SHA-256 fingerprint of an explicit byte sequence."""
    if not isinstance(data, (bytes, bytearray)):
        raise SchemaSerializationError(
            "fingerprint_bytes expects bytes or bytearray"
        )

    return hashlib.sha256(
        bytes(data)
    ).hexdigest()


def is_sha256_hex(
    value: object,
) -> bool:
    """Return whether *value* is a canonical lowercase SHA-256 digest."""
    return (
        isinstance(value, str)
        and _SHA256_RE.fullmatch(value) is not None
    )


def require_sha256_hex(
    value: object,
    *,
    field_name: str = "fingerprint",
) -> str:
    """Validate and return a canonical SHA-256 hexadecimal digest."""
    if not is_sha256_hex(value):
        raise SchemaSerializationError(
            f"{field_name} must be a 64-character lowercase SHA-256 digest"
        )

    return value


def chain_hash(
    previous_hash: str,
    canonical_text: str,
) -> str:
    """Create a tamper-evident hash-chain link.

    A length-delimited encoding prevents ambiguous concatenation between the
    previous hash and current canonical record.
    """
    require_sha256_hex(
        previous_hash,
        field_name="previous_hash",
    )

    if not isinstance(canonical_text, str):
        raise SchemaSerializationError(
            "canonical_text must be a string"
        )

    framed = (
        f"{len(previous_hash)}:"
        f"{previous_hash}"
        f"{len(canonical_text.encode('utf-8'))}:"
        f"{canonical_text}"
    )

    return sha256_hex(framed)


def canonical_schema_coordinate(
    namespace: str,
    name: str,
    version: str,
) -> str:
    """Validate and build ``namespace/name@MAJOR.MINOR.PATCH``."""
    if not is_valid_namespace(namespace):
        raise SchemaSerializationError(
            f"invalid schema namespace: {namespace!r}"
        )

    if not is_valid_name(name):
        raise SchemaSerializationError(
            f"invalid schema name: {name!r}"
        )

    if (
        not isinstance(version, str)
        or _VERSION_RE.fullmatch(version) is None
    ):
        raise SchemaSerializationError(
            f"invalid semantic schema version: {version!r}"
        )

    coordinate = f"{namespace}/{name}@{version}"

    if len(coordinate) > MAX_COORDINATE_LENGTH:
        raise SchemaSerializationError(
            "schema coordinate exceeds maximum length"
        )

    return coordinate


def validate_schema_coordinate(
    coordinate: str,
) -> str:
    """Validate and return an existing canonical schema coordinate."""
    if not isinstance(coordinate, str):
        raise SchemaSerializationError(
            "schema coordinate must be a string"
        )

    if len(coordinate) > MAX_COORDINATE_LENGTH:
        raise SchemaSerializationError(
            "schema coordinate exceeds maximum length"
        )

    try:
        subject, version = coordinate.rsplit("@", 1)
        namespace, name = subject.rsplit("/", 1)
    except ValueError as exc:
        raise SchemaSerializationError(
            "schema coordinate must use namespace/name@version"
        ) from exc

    expected = canonical_schema_coordinate(
        namespace,
        name,
        version,
    )

    if coordinate != expected:
        raise SchemaSerializationError(
            "schema coordinate is not canonical"
        )

    return coordinate


def schema_id_from_coordinate(
    coordinate: str,
) -> str:
    """Return the deterministic identifier for one schema coordinate."""
    canonical = validate_schema_coordinate(
        coordinate
    )

    digest = sha256_hex(
        canonical
    )

    return (
        SCHEMA_ID_PREFIX
        + digest[:SCHEMA_ID_HEX_LENGTH]
    )


def verify_schema_id(
    coordinate: str,
    schema_id: str,
) -> bool:
    """Return whether *schema_id* correctly identifies *coordinate*."""
    if not isinstance(schema_id, str):
        return False

    return schema_id == schema_id_from_coordinate(
        coordinate
    )


__all__ = [
    "FINGERPRINT_ALGORITHM",
    "MAX_COORDINATE_LENGTH",
    "SCHEMA_ID_HEX_LENGTH",
    "SCHEMA_ID_PREFIX",
    "SHA256_HEX_LENGTH",
    "canonical_schema_coordinate",
    "chain_hash",
    "fingerprint_bytes",
    "is_sha256_hex",
    "require_sha256_hex",
    "schema_id_from_coordinate",
    "sha256_hex",
    "validate_schema_coordinate",
    "verify_schema_id",
]
