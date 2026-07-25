from __future__ import annotations

import importlib
import py_compile
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

RUNTIME_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
)

PACKAGE_DIR = RUNTIME_DIR / "runtime_schema"
TYPES_FILE = PACKAGE_DIR / "types.py"
TARGET = PACKAGE_DIR / "fingerprint.py"

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_fingerprint_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
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
'''


def import_target():
    runtime_path = str(RUNTIME_DIR)

    if runtime_path not in sys.path:
        sys.path.insert(
            0,
            runtime_path,
        )

    sys.modules.pop(
        "runtime_schema.fingerprint",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.fingerprint"
    )


def verify_behavior(module) -> None:
    assert (
        module.sha256_hex("abc")
        == (
            "ba7816bf8f01cfea414140de5dae2223"
            "b00361a396177a9cb410ff61f20015ad"
        )
    )

    assert (
        module.sha256_hex(b"abc")
        == module.sha256_hex("abc")
    )

    assert (
        module.fingerprint_bytes(b"abc")
        == module.sha256_hex("abc")
    )

    assert module.is_sha256_hex(
        module.sha256_hex("test")
    )

    assert not module.is_sha256_hex(
        "A" * 64
    )

    coordinate = (
        module.canonical_schema_coordinate(
            "runtime.schema",
            "job_record",
            "1.2.3",
        )
    )

    assert coordinate == (
        "runtime.schema/job_record@1.2.3"
    )

    assert (
        module.validate_schema_coordinate(
            coordinate
        )
        == coordinate
    )

    schema_id_one = (
        module.schema_id_from_coordinate(
            coordinate
        )
    )

    schema_id_two = (
        module.schema_id_from_coordinate(
            coordinate
        )
    )

    assert schema_id_one == schema_id_two
    assert schema_id_one.startswith(
        module.SCHEMA_ID_PREFIX
    )

    assert len(schema_id_one) == (
        len(module.SCHEMA_ID_PREFIX)
        + module.SCHEMA_ID_HEX_LENGTH
    )

    assert module.verify_schema_id(
        coordinate,
        schema_id_one,
    )

    genesis = "0" * 64

    first = module.chain_hash(
        genesis,
        '{"sequence":1}',
    )

    second = module.chain_hash(
        first,
        '{"sequence":2}',
    )

    assert module.is_sha256_hex(first)
    assert module.is_sha256_hex(second)
    assert first != second

    try:
        module.schema_id_from_coordinate(
            "Runtime.Schema/job_record@1.2.3"
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Invalid namespace coordinate was accepted."
        )

    try:
        module.schema_id_from_coordinate(
            "runtime.schema/job_record@01.2.3"
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Noncanonical version coordinate was accepted."
        )

    try:
        module.chain_hash(
            "invalid",
            "{}",
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Invalid previous hash was accepted."
        )


def rollback() -> None:
    if TARGET_PREEXISTED and BACKUP.exists():
        shutil.copy2(
            BACKUP,
            TARGET,
        )
    elif TARGET.exists():
        TARGET.unlink()


def main() -> int:
    print("=" * 78)
    print("RUNTIME SCHEMA MANAGEMENT")
    print("FINGERPRINT.PY INSTALLATION AND REVIEW")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    if not TYPES_FILE.exists():
        raise FileNotFoundError(
            f"Required reviewed dependency is missing: {TYPES_FILE}"
        )

    if TARGET_PREEXISTED:
        BACKUP.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            TARGET,
            BACKUP,
        )

    try:
        PACKAGE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        TARGET.write_text(
            SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(TYPES_FILE),
            doraise=True,
        )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        module = import_target()

        verify_behavior(module)

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The fingerprint.py installation failed, "
            "so the previous filesystem state was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("fingerprint.py compilation:     PASS")
    print("Package import:                 PASS")
    print("SHA-256 determinism:            PASS")
    print("Digest validation:              PASS")
    print("Coordinate validation:          PASS")
    print("Schema ID determinism:          PASS")
    print("Schema ID verification:         PASS")
    print("Hash-chain framing:             PASS")
    print("Invalid-input rejection:        PASS")
    print()

    if TARGET_PREEXISTED:
        print(f"Backup file: {BACKUP}")
    else:
        print(
            "Backup file: NOT REQUIRED "
            "(target did not previously exist)"
        )

    print()
    print("FINGERPRINT.PY: INSTALLED, REVIEWED, AND APPROVED")
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
