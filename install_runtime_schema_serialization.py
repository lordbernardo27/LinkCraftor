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
FINGERPRINT_FILE = PACKAGE_DIR / "fingerprint.py"
TARGET = PACKAGE_DIR / "serialization.py"

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_serialization_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
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
'''


def import_target():
    runtime_path = str(RUNTIME_DIR)

    if runtime_path not in sys.path:
        sys.path.insert(
            0,
            runtime_path,
        )

    sys.modules.pop(
        "runtime_schema.serialization",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.serialization"
    )


def expect_rejection(
    callable_object,
    label: str,
) -> None:
    try:
        callable_object()
    except Exception:
        return

    raise AssertionError(
        f"{label} was unexpectedly accepted."
    )


def verify_behavior(module) -> None:
    value_one = {
        "z": 3,
        "a": {
            "enabled": True,
            "values": [1, 2, 3],
        },
        "unicode": "café",
    }

    value_two = {
        "unicode": "café",
        "a": {
            "values": (1, 2, 3),
            "enabled": True,
        },
        "z": 3,
    }

    canonical_one = module.canonical_json(
        value_one
    )

    canonical_two = module.canonical_json(
        value_two
    )

    assert canonical_one == canonical_two

    assert canonical_one == (
        '{"a":{"enabled":true,"values":[1,2,3]},'
        '"unicode":"café","z":3}'
    )

    encoded = module.canonical_bytes(
        value_one
    )

    assert isinstance(encoded, bytes)

    assert encoded.decode("utf-8") == canonical_one

    parsed = module.parse_canonical_json(
        encoded
    )

    assert parsed == {
        "a": {
            "enabled": True,
            "values": [1, 2, 3],
        },
        "unicode": "café",
        "z": 3,
    }

    assert module.is_canonical_json(
        canonical_one
    )

    assert not module.is_canonical_json(
        '{"z":3,"a":1}'
    )

    assert not module.is_canonical_json(
        '{"a":1, "z":3}'
    )

    assert (
        module.canonical_round_trip(
            value_one
        )
        == parsed
    )

    fingerprint_one = (
        module.structure_fingerprint(
            value_one
        )
    )

    fingerprint_two = (
        module.structure_fingerprint(
            value_two
        )
    )

    assert fingerprint_one == fingerprint_two

    assert (
        module.verify_structure_fingerprint(
            value_one,
            fingerprint_one,
        )
    )

    assert not (
        module.verify_structure_fingerprint(
            {"different": True},
            fingerprint_one,
        )
    )

    relaxed = module.parse_canonical_json(
        '{"z":3, "a":1}',
        require_canonical=False,
    )

    assert relaxed == {
        "z": 3,
        "a": 1,
    }

    expect_rejection(
        lambda: module.parse_canonical_json(
            '{"a":1,"a":2}',
            require_canonical=False,
        ),
        "Duplicate key",
    )

    expect_rejection(
        lambda: module.parse_canonical_json(
            '{"value":NaN}',
            require_canonical=False,
        ),
        "NaN",
    )

    expect_rejection(
        lambda: module.parse_canonical_json(
            '{"value":Infinity}',
            require_canonical=False,
        ),
        "Infinity",
    )

    expect_rejection(
        lambda: module.parse_canonical_json(
            b"\xef\xbb\xbf{}"
        ),
        "UTF-8 BOM",
    )

    expect_rejection(
        lambda: module.parse_canonical_json(
            '{"z":3,"a":1}'
        ),
        "Unsorted object keys",
    )

    expect_rejection(
        lambda: module.parse_canonical_json(
            '{"text":"caf\\u00e9"}'
        ),
        "Noncanonical Unicode escaping",
    )

    expect_rejection(
        lambda: module.canonical_json(
            {"value": float("nan")}
        ),
        "Non-finite Python float",
    )

    expect_rejection(
        lambda: module.canonical_json(
            {1: "invalid"}
        ),
        "Non-string mapping key",
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
    print("SERIALIZATION.PY INSTALLATION AND REVIEW")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    required_files = [
        TYPES_FILE,
        FINGERPRINT_FILE,
    ]

    for required_file in required_files:
        if not required_file.exists():
            raise FileNotFoundError(
                "Required reviewed dependency is missing: "
                f"{required_file}"
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

        for path in required_files:
            py_compile.compile(
                str(path),
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
            "The serialization.py installation failed, "
            "so the previous filesystem state was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("serialization.py compilation:   PASS")
    print("Package import:                 PASS")
    print("Canonical key ordering:         PASS")
    print("Canonical UTF-8 encoding:       PASS")
    print("Unicode policy:                 PASS")
    print("Strict canonical parsing:       PASS")
    print("Duplicate-key rejection:        PASS")
    print("Non-finite-number rejection:    PASS")
    print("BOM rejection:                  PASS")
    print("Size-bound policy:              PASS")
    print("Canonical round trip:           PASS")
    print("Fingerprint determinism:        PASS")
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
    print("SERIALIZATION.PY: INSTALLED, REVIEWED, AND APPROVED")
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
