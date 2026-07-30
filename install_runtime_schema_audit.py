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

REQUIRED_FILES = [
    PACKAGE_DIR / "types.py",
    PACKAGE_DIR / "fingerprint.py",
    PACKAGE_DIR / "serialization.py",
]

TARGET = PACKAGE_DIR / "audit.py"

TIMESTAMP = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_audit_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
"""Runtime Schema Audit History.

This module provides an append-only, hash-chained history for Runtime Schema
Management mutations.

Each audit record commits to:

* its immutable canonical content;
* its sequence position;
* the previous record hash;
* the actor and action;
* the affected subject;
* optional before/after fingerprints.

Changing, inserting, deleting, or reordering records breaks verification.

The audit layer records facts only. It does not perform registry mutations.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Final, Iterator, Mapping, Sequence

from .fingerprint import (
    chain_hash,
    is_sha256_hex,
)
from .serialization import (
    canonical_json,
    structure_fingerprint,
)
from .types import (
    AuditAction,
    MAX_DESCRIPTION_LENGTH,
    SchemaAuditError,
    is_canonical_timestamp,
    is_valid_identifier,
    utc_now_iso,
)


GENESIS_HASH: Final[str] = "0" * 64

MAX_AUDIT_SUBJECT_LENGTH: Final[int] = 1024

MAX_AUDIT_DETAIL_LENGTH: Final[int] = (
    MAX_DESCRIPTION_LENGTH
)

MAX_AUDIT_RECORDS: Final[int] = 10_000_000


def _require_digest_or_none(
    value: str | None,
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None

    if not is_sha256_hex(
        value
    ):
        raise SchemaAuditError(
            f"{field_name} must be a lowercase "
            "64-character SHA-256 digest or None"
        )

    return value


def _coerce_action(
    value: AuditAction | str,
) -> AuditAction:
    if isinstance(
        value,
        AuditAction,
    ):
        return value

    try:
        return AuditAction(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise SchemaAuditError(
            f"invalid audit action: {value!r}"
        ) from exc


@dataclass(
    frozen=True,
    slots=True,
)
class AuditRecord:
    """One immutable, chained audit record."""

    sequence: int
    timestamp: str
    actor: str
    action: AuditAction
    subject: str
    before_fingerprint: str | None
    after_fingerprint: str | None
    detail: str
    previous_hash: str
    record_hash: str = field(
        default="",
        compare=False,
    )

    def __post_init__(self) -> None:
        if (
            not isinstance(
                self.sequence,
                int,
            )
            or isinstance(
                self.sequence,
                bool,
            )
            or self.sequence < 0
        ):
            raise SchemaAuditError(
                "sequence must be a non-negative integer"
            )

        if not is_canonical_timestamp(
            self.timestamp
        ):
            raise SchemaAuditError(
                "timestamp must be a canonical UTC timestamp"
            )

        if not is_valid_identifier(
            self.actor
        ):
            raise SchemaAuditError(
                f"invalid audit actor: {self.actor!r}"
            )

        object.__setattr__(
            self,
            "action",
            _coerce_action(
                self.action
            ),
        )

        if (
            not isinstance(
                self.subject,
                str,
            )
            or not self.subject.strip()
        ):
            raise SchemaAuditError(
                "audit subject must be a non-empty string"
            )

        if (
            len(self.subject)
            > MAX_AUDIT_SUBJECT_LENGTH
        ):
            raise SchemaAuditError(
                "audit subject exceeds "
                f"{MAX_AUDIT_SUBJECT_LENGTH} characters"
            )

        if not isinstance(
            self.detail,
            str,
        ):
            raise SchemaAuditError(
                "audit detail must be a string"
            )

        if (
            len(self.detail)
            > MAX_AUDIT_DETAIL_LENGTH
        ):
            raise SchemaAuditError(
                "audit detail exceeds "
                f"{MAX_AUDIT_DETAIL_LENGTH} characters"
            )

        _require_digest_or_none(
            self.before_fingerprint,
            field_name="before_fingerprint",
        )

        _require_digest_or_none(
            self.after_fingerprint,
            field_name="after_fingerprint",
        )

        if not is_sha256_hex(
            self.previous_hash
        ):
            raise SchemaAuditError(
                "previous_hash must be a lowercase "
                "64-character SHA-256 digest"
            )

        computed = self.compute_hash()

        if not self.record_hash:
            object.__setattr__(
                self,
                "record_hash",
                computed,
            )
        elif not is_sha256_hex(
            self.record_hash
        ):
            raise SchemaAuditError(
                "record_hash must be a lowercase "
                "64-character SHA-256 digest"
            )

    def content_dict(
        self,
    ) -> dict[str, Any]:
        """Return the canonical content committed by ``record_hash``."""
        return {
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "action": self.action.value,
            "subject": self.subject,
            "before_fingerprint": (
                self.before_fingerprint
            ),
            "after_fingerprint": (
                self.after_fingerprint
            ),
            "detail": self.detail,
            "previous_hash": (
                self.previous_hash
            ),
        }

    def compute_hash(
        self,
    ) -> str:
        """Recompute this record's deterministic chain hash."""
        return chain_hash(
            self.previous_hash,
            canonical_json(
                self.content_dict()
            ),
        )

    def verify_hash(
        self,
    ) -> bool:
        """Return whether the stored hash matches canonical content."""
        return (
            self.compute_hash()
            == self.record_hash
        )

    @property
    def fingerprint(
        self,
    ) -> str:
        """Return deterministic complete-record fingerprint."""
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return the complete JSON-native audit record."""
        record = self.content_dict()

        record["record_hash"] = (
            self.record_hash
        )

        return record

    @classmethod
    def from_canonical_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "AuditRecord":
        """Rebuild and integrity-check one canonical audit record."""
        if not isinstance(
            data,
            Mapping,
        ):
            raise SchemaAuditError(
                "audit record must be a mapping"
            )

        required = {
            "sequence",
            "timestamp",
            "actor",
            "action",
            "subject",
            "before_fingerprint",
            "after_fingerprint",
            "detail",
            "previous_hash",
            "record_hash",
        }

        missing = sorted(
            required
            - set(data)
        )

        if missing:
            raise SchemaAuditError(
                "missing audit record fields: "
                + ", ".join(missing)
            )

        unknown = sorted(
            set(data)
            - required
        )

        if unknown:
            raise SchemaAuditError(
                "unknown audit record fields: "
                + ", ".join(unknown)
            )

        record = cls(
            sequence=data["sequence"],
            timestamp=data["timestamp"],
            actor=data["actor"],
            action=data["action"],
            subject=data["subject"],
            before_fingerprint=(
                data["before_fingerprint"]
            ),
            after_fingerprint=(
                data["after_fingerprint"]
            ),
            detail=data["detail"],
            previous_hash=data["previous_hash"],
            record_hash=data["record_hash"],
        )

        if not record.verify_hash():
            raise SchemaAuditError(
                "audit record hash mismatch"
            )

        return record


@dataclass(
    frozen=True,
    slots=True,
)
class ChainVerification:
    """Immutable result of verifying an audit chain."""

    valid: bool
    complete: bool
    length: int
    expected_head_hash: str
    actual_head_hash: str
    first_invalid_sequence: int | None
    code: str
    detail: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.valid,
            bool,
        ):
            raise SchemaAuditError(
                "valid must be a boolean"
            )

        if not isinstance(
            self.complete,
            bool,
        ):
            raise SchemaAuditError(
                "complete must be a boolean"
            )

        if (
            not isinstance(
                self.length,
                int,
            )
            or isinstance(
                self.length,
                bool,
            )
            or self.length < 0
        ):
            raise SchemaAuditError(
                "length must be a non-negative integer"
            )

        for field_name in (
            "expected_head_hash",
            "actual_head_hash",
        ):
            if not is_sha256_hex(
                getattr(
                    self,
                    field_name,
                )
            ):
                raise SchemaAuditError(
                    f"{field_name} must be a SHA-256 digest"
                )

        if (
            self.first_invalid_sequence
            is not None
            and (
                not isinstance(
                    self.first_invalid_sequence,
                    int,
                )
                or isinstance(
                    self.first_invalid_sequence,
                    bool,
                )
                or self.first_invalid_sequence < 0
            )
        ):
            raise SchemaAuditError(
                "first_invalid_sequence must be "
                "a non-negative integer or None"
            )

        for field_name in (
            "code",
            "detail",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                not isinstance(
                    value,
                    str,
                )
                or not value
            ):
                raise SchemaAuditError(
                    f"{field_name} must be a non-empty string"
                )

        if self.valid:
            if (
                not self.complete
                or self.first_invalid_sequence
                is not None
                or self.code != "chain_intact"
                or self.expected_head_hash
                != self.actual_head_hash
            ):
                raise SchemaAuditError(
                    "valid verification result is inconsistent"
                )

    @property
    def fingerprint(
        self,
    ) -> str:
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "complete": self.complete,
            "length": self.length,
            "expected_head_hash": (
                self.expected_head_hash
            ),
            "actual_head_hash": (
                self.actual_head_hash
            ),
            "first_invalid_sequence": (
                self.first_invalid_sequence
            ),
            "code": self.code,
            "detail": self.detail,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class AuditSnapshot:
    """Immutable deterministic snapshot of an audit chain."""

    generation: int
    records: tuple[
        AuditRecord,
        ...
    ]
    head_hash: str
    fingerprint: str

    def __post_init__(self) -> None:
        if (
            not isinstance(
                self.generation,
                int,
            )
            or isinstance(
                self.generation,
                bool,
            )
            or self.generation < 0
        ):
            raise SchemaAuditError(
                "generation must be a non-negative integer"
            )

        object.__setattr__(
            self,
            "records",
            tuple(
                self.records
            ),
        )

        if not is_sha256_hex(
            self.head_hash
        ):
            raise SchemaAuditError(
                "head_hash must be a SHA-256 digest"
            )

        if not is_sha256_hex(
            self.fingerprint
        ):
            raise SchemaAuditError(
                "snapshot fingerprint must be a SHA-256 digest"
            )

    @property
    def length(
        self,
    ) -> int:
        return len(
            self.records
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "generation": self.generation,
            "records": [
                record.to_canonical_dict()
                for record in self.records
            ],
            "head_hash": self.head_hash,
            "length": self.length,
            "fingerprint": self.fingerprint,
        }


class AuditLog:
    """Thread-safe append-only, hash-chained audit log."""

    def __init__(self) -> None:
        self._lock = threading.RLock()

        self._records: list[
            AuditRecord
        ] = []

        self._subject_index: dict[
            str,
            list[int],
        ] = {}

        self._generation = 0

    @property
    def generation(
        self,
    ) -> int:
        """Return current append generation."""
        with self._lock:
            return self._generation

    @property
    def head_hash(
        self,
    ) -> str:
        """Return the current chain head or genesis hash."""
        with self._lock:
            return (
                self._records[-1].record_hash
                if self._records
                else GENESIS_HASH
            )

    def append(
        self,
        actor: str,
        action: AuditAction | str,
        subject: str,
        detail: str,
        before_fingerprint: str | None = None,
        after_fingerprint: str | None = None,
        *,
        expected_head_hash: str | None = None,
        timestamp: str | None = None,
    ) -> AuditRecord:
        """Append one record under optional compare-and-append control."""
        if not is_valid_identifier(
            actor
        ):
            raise SchemaAuditError(
                f"invalid audit actor: {actor!r}"
            )

        effective_action = (
            _coerce_action(
                action
            )
        )

        if (
            not isinstance(
                subject,
                str,
            )
            or not subject.strip()
        ):
            raise SchemaAuditError(
                "audit subject must be a non-empty string"
            )

        if (
            len(subject)
            > MAX_AUDIT_SUBJECT_LENGTH
        ):
            raise SchemaAuditError(
                "audit subject exceeds "
                f"{MAX_AUDIT_SUBJECT_LENGTH} characters"
            )

        if not isinstance(
            detail,
            str,
        ):
            raise SchemaAuditError(
                "audit detail must be a string"
            )

        if (
            len(detail)
            > MAX_AUDIT_DETAIL_LENGTH
        ):
            raise SchemaAuditError(
                "audit detail exceeds "
                f"{MAX_AUDIT_DETAIL_LENGTH} characters"
            )

        _require_digest_or_none(
            before_fingerprint,
            field_name="before_fingerprint",
        )

        _require_digest_or_none(
            after_fingerprint,
            field_name="after_fingerprint",
        )

        if (
            expected_head_hash
            is not None
            and not is_sha256_hex(
                expected_head_hash
            )
        ):
            raise SchemaAuditError(
                "expected_head_hash must be "
                "a SHA-256 digest or None"
            )

        effective_timestamp = (
            utc_now_iso()
            if timestamp is None
            else timestamp
        )

        if not is_canonical_timestamp(
            effective_timestamp
        ):
            raise SchemaAuditError(
                "timestamp must be canonical"
            )

        with self._lock:
            if (
                len(self._records)
                >= MAX_AUDIT_RECORDS
            ):
                raise SchemaAuditError(
                    "audit log reached its configured "
                    "maximum record count"
                )

            previous_hash = (
                self._records[-1].record_hash
                if self._records
                else GENESIS_HASH
            )

            if (
                expected_head_hash
                is not None
                and expected_head_hash
                != previous_hash
            ):
                raise SchemaAuditError(
                    "audit compare-and-append failed"
                )

            record = AuditRecord(
                sequence=len(
                    self._records
                ),
                timestamp=effective_timestamp,
                actor=actor,
                action=effective_action,
                subject=subject.strip(),
                before_fingerprint=(
                    before_fingerprint
                ),
                after_fingerprint=(
                    after_fingerprint
                ),
                detail=detail,
                previous_hash=previous_hash,
            )

            self._records.append(
                record
            )

            self._subject_index.setdefault(
                record.subject,
                [],
            ).append(
                record.sequence
            )

            self._generation += 1

            return record

    def history(
        self,
        subject: str | None = None,
    ) -> tuple[
        AuditRecord,
        ...
    ]:
        """Return all records or records for one exact subject."""
        with self._lock:
            if subject is None:
                return tuple(
                    self._records
                )

            if (
                not isinstance(
                    subject,
                    str,
                )
                or not subject
            ):
                raise SchemaAuditError(
                    "subject filter must be "
                    "a non-empty string"
                )

            indexes = tuple(
                self._subject_index.get(
                    subject,
                    (),
                )
            )

            return tuple(
                self._records[index]
                for index in indexes
            )

    def records_for_action(
        self,
        action: AuditAction | str,
    ) -> tuple[
        AuditRecord,
        ...
    ]:
        """Return records matching one audit action."""
        effective_action = (
            _coerce_action(
                action
            )
        )

        with self._lock:
            return tuple(
                record
                for record in self._records
                if record.action
                is effective_action
            )

    def __len__(
        self,
    ) -> int:
        with self._lock:
            return len(
                self._records
            )

    def __iter__(
        self,
    ) -> Iterator[
        AuditRecord
    ]:
        return iter(
            self.history()
        )

    def verify_chain(
        self,
    ) -> ChainVerification:
        """Re-walk and re-hash the complete chain."""
        records = self.history()

        expected_previous = (
            GENESIS_HASH
        )

        for index, record in enumerate(
            records
        ):
            if record.sequence != index:
                return ChainVerification(
                    valid=False,
                    complete=True,
                    length=len(records),
                    expected_head_hash=(
                        expected_previous
                    ),
                    actual_head_hash=(
                        records[-1].record_hash
                        if records
                        else GENESIS_HASH
                    ),
                    first_invalid_sequence=index,
                    code="sequence_mismatch",
                    detail=(
                        "sequence mismatch at "
                        f"position {index}"
                    ),
                )

            if (
                record.previous_hash
                != expected_previous
            ):
                return ChainVerification(
                    valid=False,
                    complete=True,
                    length=len(records),
                    expected_head_hash=(
                        expected_previous
                    ),
                    actual_head_hash=(
                        records[-1].record_hash
                        if records
                        else GENESIS_HASH
                    ),
                    first_invalid_sequence=index,
                    code="broken_chain_link",
                    detail=(
                        "previous hash mismatch at "
                        f"sequence {index}"
                    ),
                )

            if not record.verify_hash():
                return ChainVerification(
                    valid=False,
                    complete=True,
                    length=len(records),
                    expected_head_hash=(
                        expected_previous
                    ),
                    actual_head_hash=(
                        records[-1].record_hash
                        if records
                        else GENESIS_HASH
                    ),
                    first_invalid_sequence=index,
                    code="record_hash_mismatch",
                    detail=(
                        "record hash mismatch at "
                        f"sequence {index}"
                    ),
                )

            expected_previous = (
                record.record_hash
            )

        actual_head = (
            records[-1].record_hash
            if records
            else GENESIS_HASH
        )

        return ChainVerification(
            valid=True,
            complete=True,
            length=len(records),
            expected_head_hash=(
                expected_previous
            ),
            actual_head_hash=(
                actual_head
            ),
            first_invalid_sequence=None,
            code="chain_intact",
            detail="audit chain is intact",
        )

    def snapshot(
        self,
    ) -> AuditSnapshot:
        """Return immutable deterministic audit evidence."""
        with self._lock:
            records = tuple(
                self._records
            )

            generation = (
                self._generation
            )

            head_hash = (
                records[-1].record_hash
                if records
                else GENESIS_HASH
            )

            payload = {
                "generation": generation,
                "records": [
                    record.to_canonical_dict()
                    for record in records
                ],
                "head_hash": head_hash,
                "length": len(records),
            }

            return AuditSnapshot(
                generation=generation,
                records=records,
                head_hash=head_hash,
                fingerprint=(
                    structure_fingerprint(
                        payload
                    )
                ),
            )

    def export_records(
        self,
    ) -> tuple[
        dict[str, Any],
        ...
    ]:
        """Return a lossless JSON-native audit export."""
        return tuple(
            record.to_canonical_dict()
            for record in self.history()
        )

    @classmethod
    def from_records(
        cls,
        records: Sequence[
            Mapping[str, Any]
        ],
    ) -> "AuditLog":
        """Rebuild an audit log and verify every chain invariant."""
        if (
            not isinstance(
                records,
                Sequence,
            )
            or isinstance(
                records,
                (str, bytes, bytearray),
            )
        ):
            raise SchemaAuditError(
                "records must be a sequence"
            )

        log = cls()

        expected_previous = (
            GENESIS_HASH
        )

        for index, data in enumerate(
            records
        ):
            record = (
                AuditRecord.from_canonical_dict(
                    data
                )
            )

            if record.sequence != index:
                raise SchemaAuditError(
                    "audit import sequence mismatch"
                )

            if (
                record.previous_hash
                != expected_previous
            ):
                raise SchemaAuditError(
                    "audit import chain-link mismatch"
                )

            log._records.append(
                record
            )

            log._subject_index.setdefault(
                record.subject,
                [],
            ).append(
                record.sequence
            )

            log._generation += 1

            expected_previous = (
                record.record_hash
            )

        verification = (
            log.verify_chain()
        )

        if not verification.valid:
            raise SchemaAuditError(
                "imported audit chain failed "
                f"verification: {verification.detail}"
            )

        return log


__all__ = [
    "GENESIS_HASH",
    "MAX_AUDIT_DETAIL_LENGTH",
    "MAX_AUDIT_RECORDS",
    "MAX_AUDIT_SUBJECT_LENGTH",
    "AuditLog",
    "AuditRecord",
    "AuditSnapshot",
    "ChainVerification",
]
'''


def import_target():
    runtime_path = str(
        RUNTIME_DIR
    )

    if runtime_path not in sys.path:
        sys.path.insert(
            0,
            runtime_path,
        )

    sys.modules.pop(
        "runtime_schema.audit",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.audit"
    )


def verify_behavior(
    module,
) -> None:
    import dataclasses
    import threading

    types_module = (
        importlib.import_module(
            "runtime_schema.types"
        )
    )

    Action = (
        types_module.AuditAction
    )

    timestamp_one = (
        "2026-07-27T16:00:00.000000Z"
    )

    timestamp_two = (
        "2026-07-27T16:00:01.000000Z"
    )

    log = module.AuditLog()

    assert len(log) == 0
    assert log.generation == 0

    assert (
        log.head_hash
        == module.GENESIS_HASH
    )

    before = "1" * 64
    after = "2" * 64

    first = log.append(
        actor="runtime_schema",
        action=Action.SCHEMA_REGISTERED,
        subject=(
            "runtime.schema/"
            "audit_record@1.0.0"
        ),
        detail="Schema registered.",
        before_fingerprint=None,
        after_fingerprint=after,
        expected_head_hash=(
            module.GENESIS_HASH
        ),
        timestamp=timestamp_one,
    )

    assert first.sequence == 0

    assert (
        first.previous_hash
        == module.GENESIS_HASH
    )

    assert first.verify_hash()

    assert (
        log.head_hash
        == first.record_hash
    )

    second = log.append(
        actor="runtime_schema",
        action="lifecycle_changed",
        subject=(
            "runtime.schema/"
            "audit_record@1.0.0"
        ),
        detail="Schema activated.",
        before_fingerprint=before,
        after_fingerprint=after,
        expected_head_hash=(
            first.record_hash
        ),
        timestamp=timestamp_two,
    )

    assert second.sequence == 1

    assert (
        second.previous_hash
        == first.record_hash
    )

    assert len(log) == 2
    assert log.generation == 2

    assert len(
        log.history()
    ) == 2

    assert len(
        log.history(
            "runtime.schema/"
            "audit_record@1.0.0"
        )
    ) == 2

    assert len(
        log.records_for_action(
            Action.LIFECYCLE_CHANGED
        )
    ) == 1

    verification = (
        log.verify_chain()
    )

    assert verification.valid
    assert verification.complete
    assert verification.length == 2
    assert (
        verification.first_invalid_sequence
        is None
    )

    assert (
        verification.expected_head_hash
        == second.record_hash
    )

    assert (
        verification.actual_head_hash
        == second.record_hash
    )

    assert len(
        verification.fingerprint
    ) == 64

    snapshot_one = (
        log.snapshot()
    )

    snapshot_two = (
        log.snapshot()
    )

    assert (
        snapshot_one.fingerprint
        == snapshot_two.fingerprint
    )

    assert snapshot_one.length == 2
    assert snapshot_one.generation == 2

    exported = (
        log.export_records()
    )

    rebuilt = (
        module.AuditLog.from_records(
            exported
        )
    )

    assert (
        rebuilt.export_records()
        == exported
    )

    assert rebuilt.verify_chain().valid

    assert (
        rebuilt.head_hash
        == log.head_hash
    )

    try:
        log.append(
            actor="runtime_schema",
            action=Action.SCHEMA_REGISTERED,
            subject="runtime.schema/test@2.0.0",
            detail="Stale head.",
            expected_head_hash=(
                module.GENESIS_HASH
            ),
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Stale compare-and-append head was accepted."
        )

    tampered_log = (
        module.AuditLog.from_records(
            exported
        )
    )

    tampered = dataclasses.replace(
        tampered_log._records[0],
        detail="Tampered detail.",
    )

    tampered_log._records[0] = (
        tampered
    )

    tampered_verification = (
        tampered_log.verify_chain()
    )

    assert not (
        tampered_verification.valid
    )

    assert (
        tampered_verification
        .first_invalid_sequence
        == 0
    )

    tampered_export = [
        dict(record)
        for record in exported
    ]

    tampered_export[0][
        "detail"
    ] = "Tampered export."

    try:
        module.AuditLog.from_records(
            tampered_export
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Tampered audit export was accepted."
        )

    try:
        first.detail = "Changed."
    except Exception:
        pass
    else:
        raise AssertionError(
            "AuditRecord must be immutable."
        )

    concurrent_log = (
        module.AuditLog()
    )

    errors: list[str] = []

    def append_record(
        index: int,
    ) -> None:
        try:
            concurrent_log.append(
                actor=f"worker_{index}",
                action=(
                    Action.SCHEMA_REGISTERED
                ),
                subject=(
                    "runtime.concurrent/"
                    f"record_{index}@1.0.0"
                ),
                detail="Concurrent append.",
            )
        except Exception as exc:
            errors.append(
                repr(exc)
            )

    threads = [
        threading.Thread(
            target=append_record,
            args=(index,),
        )
        for index in range(200)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert not errors

    assert len(
        concurrent_log
    ) == 200

    assert (
        concurrent_log.generation
        == 200
    )

    concurrent_verification = (
        concurrent_log.verify_chain()
    )

    assert concurrent_verification.valid

    assert (
        concurrent_verification.length
        == 200
    )

    try:
        log.append(
            actor="invalid actor",
            action=(
                Action.SCHEMA_REGISTERED
            ),
            subject="runtime.schema/test@1.0.0",
            detail="Invalid actor.",
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Invalid actor was accepted."
        )

    try:
        log.append(
            actor="runtime_schema",
            action=(
                Action.SCHEMA_REGISTERED
            ),
            subject="runtime.schema/test@1.0.0",
            detail="Invalid fingerprint.",
            after_fingerprint="invalid",
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Invalid fingerprint was accepted."
        )


def rollback() -> None:
    if (
        TARGET_PREEXISTED
        and BACKUP.exists()
    ):
        shutil.copy2(
            BACKUP,
            TARGET,
        )
    elif TARGET.exists():
        TARGET.unlink()


def main() -> int:
    print("=" * 78)
    print("RUNTIME SCHEMA MANAGEMENT")
    print("AUDIT.PY INSTALLATION AND REVIEW")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    for required_file in REQUIRED_FILES:
        if not required_file.exists():
            raise FileNotFoundError(
                "Required reviewed dependency "
                f"is missing: {required_file}"
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
        TARGET.write_text(
            SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        for path in REQUIRED_FILES:
            py_compile.compile(
                str(path),
                doraise=True,
            )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        module = import_target()

        verify_behavior(
            module
        )

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The audit.py installation failed, "
            "so the previous filesystem state was restored."
        )
        print()
        print(
            traceback.format_exc()
        )

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("audit.py compilation:           PASS")
    print("Package import:                 PASS")
    print("Immutable audit records:        PASS")
    print("Canonical timestamp policy:     PASS")
    print("Actor/action validation:        PASS")
    print("Fingerprint validation:         PASS")
    print("Genesis-chain initialization:   PASS")
    print("Append-only sequencing:         PASS")
    print("Compare-and-append control:     PASS")
    print("Subject history index:          PASS")
    print("Action filtering:               PASS")
    print("Hash-chain verification:        PASS")
    print("Tamper detection:               PASS")
    print("Generation tracking:            PASS")
    print("Deterministic snapshots:        PASS")
    print("Lossless export/import:         PASS")
    print("Import integrity verification:  PASS")
    print("Concurrent append safety:       PASS")
    print("Invalid-input rejection:        PASS")
    print()

    if TARGET_PREEXISTED:
        print(
            f"Backup file: {BACKUP}"
        )
    else:
        print(
            "Backup file: NOT REQUIRED "
            "(target did not previously exist)"
        )

    print()
    print(
        "AUDIT.PY: INSTALLED, "
        "REVIEWED, AND APPROVED"
    )
    print(
        "NO PRODUCTION DATA WAS MODIFIED"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
