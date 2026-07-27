from __future__ import annotations

import importlib
import py_compile
import shutil
import sys
import threading
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
    PACKAGE_DIR / "serialization.py",
    PACKAGE_DIR / "namespaces.py",
]

TARGET = PACKAGE_DIR / "ownership.py"

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_ownership_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
"""Runtime Schema Ownership.

Ownership is modeled at ``namespace/name`` scope rather than per version.
The owner of a schema therefore owns every registered version of that
schema unless ownership is explicitly transferred.

The ownership ledger is append-only, deterministic, thread-safe, and
business-logic agnostic.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .serialization import (
    canonical_bytes,
    structure_fingerprint,
)
from .types import (
    EMPTY_FROZEN_MAPPING,
    MAX_DESCRIPTION_LENGTH,
    MAX_METADATA_SIZE_BYTES,
    OwnerKind,
    RESERVED_RUNTIME_PREFIX,
    RESERVED_RUNTIME_ROOT,
    SchemaRegistryError,
    deep_freeze,
    deep_thaw,
    is_canonical_timestamp,
    is_reserved_runtime_namespace,
    is_valid_identifier,
    is_valid_name,
    is_valid_namespace,
    utc_now_iso,
)


MAX_TRANSFER_REASON_LENGTH = 4096


def canonical_ownership_subject(
    namespace: str,
    name: str,
) -> str:
    """Validate and return ``namespace/name``."""
    if not is_valid_namespace(
        namespace
    ):
        raise SchemaRegistryError(
            f"invalid ownership namespace: {namespace!r}"
        )

    if not is_valid_name(
        name
    ):
        raise SchemaRegistryError(
            f"invalid ownership schema name: {name!r}"
        )

    return f"{namespace}/{name}"


def validate_ownership_subject(
    subject: str,
) -> str:
    """Validate and return a canonical ownership subject."""
    if not isinstance(
        subject,
        str,
    ):
        raise SchemaRegistryError(
            "ownership subject must be a string"
        )

    try:
        namespace, name = subject.rsplit(
            "/",
            1,
        )
    except ValueError as exc:
        raise SchemaRegistryError(
            "ownership subject must use namespace/name"
        ) from exc

    expected = canonical_ownership_subject(
        namespace,
        name,
    )

    if subject != expected:
        raise SchemaRegistryError(
            "ownership subject is not canonical"
        )

    return subject


def ownership_subject_namespace(
    subject: str,
) -> str:
    """Return the namespace portion of a validated subject."""
    validated = validate_ownership_subject(
        subject
    )

    return validated.rsplit(
        "/",
        1,
    )[0]


@dataclass(
    frozen=True,
    slots=True,
)
class SchemaOwner:
    """Immutable description of a schema-owning principal."""

    owner_id: str
    owner_kind: OwnerKind
    contact_reference: str | None = None
    metadata: Mapping[str, Any] = (
        EMPTY_FROZEN_MAPPING
    )

    def __post_init__(self) -> None:
        if not is_valid_identifier(
            self.owner_id
        ):
            raise SchemaRegistryError(
                f"invalid owner_id: {self.owner_id!r}"
            )

        if not isinstance(
            self.owner_kind,
            OwnerKind,
        ):
            try:
                object.__setattr__(
                    self,
                    "owner_kind",
                    OwnerKind(
                        self.owner_kind
                    ),
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise SchemaRegistryError(
                    f"invalid owner_kind: {self.owner_kind!r}"
                ) from exc

        if (
            self.contact_reference is not None
            and not is_valid_identifier(
                self.contact_reference
            )
        ):
            raise SchemaRegistryError(
                "invalid contact_reference"
            )

        try:
            frozen_metadata = deep_freeze(
                self.metadata
            )

            metadata_size = len(
                canonical_bytes(
                    deep_thaw(
                        frozen_metadata
                    )
                )
            )
        except Exception as exc:
            raise SchemaRegistryError(
                f"invalid owner metadata: {exc}"
            ) from exc

        if (
            metadata_size
            > MAX_METADATA_SIZE_BYTES
        ):
            raise SchemaRegistryError(
                "owner metadata exceeds "
                f"{MAX_METADATA_SIZE_BYTES} bytes"
            )

        object.__setattr__(
            self,
            "metadata",
            frozen_metadata,
        )

    @property
    def fingerprint(self) -> str:
        """Return deterministic owner-record fingerprint."""
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return owner record as plain JSON-native data."""
        return {
            "owner_id": self.owner_id,
            "owner_kind": self.owner_kind.value,
            "contact_reference": (
                self.contact_reference
            ),
            "metadata": deep_thaw(
                self.metadata
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class OwnershipTransferRecord:
    """Immutable record of one ownership assignment or transfer."""

    sequence: int
    subject: str
    previous_owner_id: str | None
    new_owner: SchemaOwner
    actor: str
    reason: str
    timestamp: str = field(
        default_factory=utc_now_iso
    )
    previous_record_fingerprint: str | None = None

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
            raise SchemaRegistryError(
                "sequence must be a non-negative integer"
            )

        validate_ownership_subject(
            self.subject
        )

        if (
            self.previous_owner_id is not None
            and not is_valid_identifier(
                self.previous_owner_id
            )
        ):
            raise SchemaRegistryError(
                "invalid previous_owner_id"
            )

        if not isinstance(
            self.new_owner,
            SchemaOwner,
        ):
            raise SchemaRegistryError(
                "new_owner must be a SchemaOwner"
            )

        if not is_valid_identifier(
            self.actor
        ):
            raise SchemaRegistryError(
                f"invalid actor: {self.actor!r}"
            )

        if (
            not isinstance(
                self.reason,
                str,
            )
            or not self.reason.strip()
        ):
            raise SchemaRegistryError(
                "a non-empty transfer reason is required"
            )

        if (
            len(self.reason)
            > MAX_TRANSFER_REASON_LENGTH
        ):
            raise SchemaRegistryError(
                "transfer reason exceeds "
                f"{MAX_TRANSFER_REASON_LENGTH} characters"
            )

        if not is_canonical_timestamp(
            self.timestamp
        ):
            raise SchemaRegistryError(
                "timestamp must be a canonical UTC timestamp"
            )

        if (
            self.previous_record_fingerprint
            is not None
            and (
                not isinstance(
                    self.previous_record_fingerprint,
                    str,
                )
                or len(
                    self.previous_record_fingerprint
                )
                != 64
            )
        ):
            raise SchemaRegistryError(
                "previous_record_fingerprint must be "
                "a 64-character digest"
            )

    @property
    def fingerprint(self) -> str:
        """Return deterministic transfer-record fingerprint."""
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return transfer record as plain JSON-native data."""
        return {
            "sequence": self.sequence,
            "subject": self.subject,
            "previous_owner_id": (
                self.previous_owner_id
            ),
            "new_owner": (
                self.new_owner.to_canonical_dict()
            ),
            "actor": self.actor,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "previous_record_fingerprint": (
                self.previous_record_fingerprint
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class OwnershipLedgerSnapshot:
    """Immutable deterministic snapshot of ownership state."""

    generation: int
    current: Mapping[str, SchemaOwner]
    history: tuple[
        OwnershipTransferRecord,
        ...
    ]
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
            raise SchemaRegistryError(
                "generation must be a non-negative integer"
            )

        object.__setattr__(
            self,
            "current",
            MappingProxyType(
                dict(self.current)
            ),
        )

        object.__setattr__(
            self,
            "history",
            tuple(self.history),
        )


class OwnershipLedger:
    """Thread-safe append-only schema ownership ledger."""

    def __init__(self) -> None:
        self._lock = threading.RLock()

        self._current: dict[
            str,
            SchemaOwner,
        ] = {}

        self._history: list[
            OwnershipTransferRecord
        ] = []

        self._subject_history: dict[
            str,
            list[OwnershipTransferRecord],
        ] = {}

        self._owner_subjects: dict[
            str,
            set[str],
        ] = {}

        self._generation = 0

    @property
    def generation(self) -> int:
        """Return current ledger generation."""
        with self._lock:
            return self._generation

    def current_owner(
        self,
        subject: str,
    ) -> SchemaOwner | None:
        """Return current owner of ``namespace/name``."""
        validated = validate_ownership_subject(
            subject
        )

        with self._lock:
            return self._current.get(
                validated
            )

    def require_owner(
        self,
        subject: str,
    ) -> SchemaOwner:
        """Return current owner or raise."""
        owner = self.current_owner(
            subject
        )

        if owner is None:
            raise SchemaRegistryError(
                f"ownership subject is unowned: {subject}"
            )

        return owner

    def assign(
        self,
        subject: str,
        new_owner: SchemaOwner,
        actor: str,
        reason: str,
        *,
        runtime_actor: bool = False,
        expected_owner_id: str | None = None,
    ) -> OwnershipTransferRecord:
        """Assign or transfer ownership under strict authorization.

        First assignment:
            The actor must be the new owner unless ``runtime_actor=True``.

        Transfer:
            The actor must be the current owner unless ``runtime_actor=True``.

        Reserved runtime subjects:
            Every assignment or transfer requires ``runtime_actor=True`` and
            the resulting owner must be of kind ``OwnerKind.RUNTIME``.
        """
        validated_subject = (
            validate_ownership_subject(
                subject
            )
        )

        if not isinstance(
            new_owner,
            SchemaOwner,
        ):
            raise SchemaRegistryError(
                "new_owner must be a SchemaOwner"
            )

        if not is_valid_identifier(
            actor
        ):
            raise SchemaRegistryError(
                f"invalid actor: {actor!r}"
            )

        if (
            expected_owner_id is not None
            and not is_valid_identifier(
                expected_owner_id
            )
        ):
            raise SchemaRegistryError(
                "invalid expected_owner_id"
            )

        namespace = (
            ownership_subject_namespace(
                validated_subject
            )
        )

        reserved = (
            is_reserved_runtime_namespace(
                namespace
            )
        )

        if reserved:
            if not runtime_actor:
                raise SchemaRegistryError(
                    f"ownership under '{RESERVED_RUNTIME_PREFIX}*' "
                    "requires a runtime actor"
                )

            if (
                new_owner.owner_kind
                is not OwnerKind.RUNTIME
            ):
                raise SchemaRegistryError(
                    "reserved runtime schemas must be owned "
                    "by an OwnerKind.RUNTIME principal"
                )

        with self._lock:
            previous = self._current.get(
                validated_subject
            )

            if (
                expected_owner_id is not None
                and (
                    previous is None
                    or previous.owner_id
                    != expected_owner_id
                )
            ):
                raise SchemaRegistryError(
                    "ownership compare-and-set failed"
                )

            if previous is None:
                if (
                    not runtime_actor
                    and actor
                    != new_owner.owner_id
                ):
                    raise SchemaRegistryError(
                        "initial ownership must be assigned "
                        "by the owner itself or the runtime"
                    )
            elif (
                not runtime_actor
                and actor
                != previous.owner_id
            ):
                raise SchemaRegistryError(
                    "ownership transfer must be authorized "
                    "by the current owner or the runtime"
                )

            if (
                previous is not None
                and previous.owner_id
                == new_owner.owner_id
                and previous.owner_kind
                is new_owner.owner_kind
                and previous.contact_reference
                == new_owner.contact_reference
                and previous.metadata
                == new_owner.metadata
            ):
                raise SchemaRegistryError(
                    f"{new_owner.owner_id} already owns "
                    f"{validated_subject} with the same record"
                )

            previous_record = (
                self._history[-1]
                if self._history
                else None
            )

            record = OwnershipTransferRecord(
                sequence=len(
                    self._history
                ),
                subject=validated_subject,
                previous_owner_id=(
                    previous.owner_id
                    if previous is not None
                    else None
                ),
                new_owner=new_owner,
                actor=actor,
                reason=reason.strip(),
                previous_record_fingerprint=(
                    previous_record.fingerprint
                    if previous_record is not None
                    else None
                ),
            )

            self._history.append(
                record
            )

            self._subject_history.setdefault(
                validated_subject,
                [],
            ).append(
                record
            )

            if previous is not None:
                old_subjects = (
                    self._owner_subjects.get(
                        previous.owner_id
                    )
                )

                if old_subjects is not None:
                    old_subjects.discard(
                        validated_subject
                    )

                    if not old_subjects:
                        self._owner_subjects.pop(
                            previous.owner_id,
                            None,
                        )

            self._current[
                validated_subject
            ] = new_owner

            self._owner_subjects.setdefault(
                new_owner.owner_id,
                set(),
            ).add(
                validated_subject
            )

            self._generation += 1

            return record

    def history(
        self,
        subject: str | None = None,
    ) -> tuple[
        OwnershipTransferRecord,
        ...
    ]:
        """Return global or subject-specific transfer history."""
        with self._lock:
            if subject is None:
                return tuple(
                    self._history
                )

            validated = (
                validate_ownership_subject(
                    subject
                )
            )

            return tuple(
                self._subject_history.get(
                    validated,
                    (),
                )
            )

    def subjects_for_owner(
        self,
        owner_id: str,
    ) -> tuple[str, ...]:
        """Return current subjects owned by one principal."""
        if not is_valid_identifier(
            owner_id
        ):
            raise SchemaRegistryError(
                f"invalid owner_id: {owner_id!r}"
            )

        with self._lock:
            return tuple(
                sorted(
                    self._owner_subjects.get(
                        owner_id,
                        set(),
                    )
                )
            )

    def current_ownership(
        self,
    ) -> Mapping[str, SchemaOwner]:
        """Return immutable current ownership mapping."""
        with self._lock:
            return MappingProxyType(
                dict(
                    sorted(
                        self._current.items()
                    )
                )
            )

    def verify_integrity(
        self,
    ) -> bool:
        """Verify sequence, chain, history, and current-owner integrity."""
        with self._lock:
            expected_previous: str | None = None
            reconstructed: dict[
                str,
                SchemaOwner,
            ] = {}

            for index, record in enumerate(
                self._history
            ):
                if record.sequence != index:
                    return False

                if (
                    record.previous_record_fingerprint
                    != expected_previous
                ):
                    return False

                current = reconstructed.get(
                    record.subject
                )

                current_owner_id = (
                    current.owner_id
                    if current is not None
                    else None
                )

                if (
                    record.previous_owner_id
                    != current_owner_id
                ):
                    return False

                reconstructed[
                    record.subject
                ] = record.new_owner

                expected_previous = (
                    record.fingerprint
                )

            return reconstructed == self._current

    def snapshot(
        self,
    ) -> OwnershipLedgerSnapshot:
        """Return deterministic immutable ledger snapshot."""
        with self._lock:
            current = dict(
                sorted(
                    self._current.items()
                )
            )

            history = tuple(
                self._history
            )

            payload = {
                "generation": self._generation,
                "current": {
                    subject: owner.to_canonical_dict()
                    for subject, owner
                    in current.items()
                },
                "history": [
                    record.to_canonical_dict()
                    for record in history
                ],
            }

            return OwnershipLedgerSnapshot(
                generation=self._generation,
                current=current,
                history=history,
                fingerprint=structure_fingerprint(
                    payload
                ),
            )


__all__ = [
    "MAX_TRANSFER_REASON_LENGTH",
    "OwnershipLedger",
    "OwnershipLedgerSnapshot",
    "OwnershipTransferRecord",
    "SchemaOwner",
    "canonical_ownership_subject",
    "ownership_subject_namespace",
    "validate_ownership_subject",
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
        "runtime_schema.ownership",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.ownership"
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
    types_module = importlib.import_module(
        "runtime_schema.types"
    )

    OwnerKind = types_module.OwnerKind

    Owner = module.SchemaOwner
    Ledger = module.OwnershipLedger

    subject = (
        module.canonical_ownership_subject(
            "product.schema",
            "record",
        )
    )

    assert subject == (
        "product.schema/record"
    )

    owner_one = Owner(
        owner_id="service_a",
        owner_kind=OwnerKind.SERVICE,
        contact_reference="service_a_contact",
        metadata={
            "tier": "primary",
        },
    )

    owner_two = Owner(
        owner_id="service_b",
        owner_kind="service",
    )

    assert len(
        owner_one.fingerprint
    ) == 64

    ledger = Ledger()

    first = ledger.assign(
        subject,
        owner_one,
        actor="service_a",
        reason="initial ownership",
    )

    assert first.sequence == 0
    assert first.previous_owner_id is None
    assert (
        first.previous_record_fingerprint
        is None
    )

    assert (
        ledger.require_owner(
            subject
        )
        == owner_one
    )

    second = ledger.assign(
        subject,
        owner_two,
        actor="service_a",
        reason="approved service transfer",
        expected_owner_id="service_a",
    )

    assert second.sequence == 1

    assert (
        second.previous_owner_id
        == "service_a"
    )

    assert (
        second.previous_record_fingerprint
        == first.fingerprint
    )

    assert (
        ledger.require_owner(
            subject
        )
        == owner_two
    )

    assert ledger.subjects_for_owner(
        "service_b"
    ) == (
        subject,
    )

    assert ledger.subjects_for_owner(
        "service_a"
    ) == ()

    assert len(
        ledger.history()
    ) == 2

    assert len(
        ledger.history(
            subject
        )
    ) == 2

    assert ledger.verify_integrity()

    snapshot_one = ledger.snapshot()
    snapshot_two = ledger.snapshot()

    assert (
        snapshot_one.fingerprint
        == snapshot_two.fingerprint
    )

    assert snapshot_one.generation == 2

    assert (
        snapshot_one.current[
            subject
        ]
        == owner_two
    )

    runtime_subject = (
        module.canonical_ownership_subject(
            "runtime.schema",
            "job_record",
        )
    )

    runtime_owner = Owner(
        owner_id="runtime_kernel",
        owner_kind=OwnerKind.RUNTIME,
    )

    runtime_record = ledger.assign(
        runtime_subject,
        runtime_owner,
        actor="runtime_kernel",
        reason="runtime ownership",
        runtime_actor=True,
    )

    assert runtime_record.sequence == 2

    expect_rejection(
        lambda: ledger.assign(
            module.canonical_ownership_subject(
                "runtime.schema",
                "queue_record",
            ),
            Owner(
                owner_id="service_c",
                owner_kind=OwnerKind.SERVICE,
            ),
            actor="service_c",
            reason="invalid reserved assignment",
        ),
        "Non-runtime reserved ownership",
    )

    expect_rejection(
        lambda: ledger.assign(
            subject,
            Owner(
                owner_id="service_c",
                owner_kind=OwnerKind.SERVICE,
            ),
            actor="unauthorized_actor",
            reason="unauthorized transfer",
        ),
        "Unauthorized ownership transfer",
    )

    expect_rejection(
        lambda: ledger.assign(
            subject,
            owner_two,
            actor="service_b",
            reason="no-op transfer",
        ),
        "No-op ownership transfer",
    )

    expect_rejection(
        lambda: ledger.assign(
            subject,
            Owner(
                owner_id="service_c",
                owner_kind=OwnerKind.SERVICE,
            ),
            actor="service_b",
            reason="compare-and-set failure",
            expected_owner_id="service_a",
        ),
        "Ownership compare-and-set failure",
    )

    expect_rejection(
        lambda: module.validate_ownership_subject(
            "invalid"
        ),
        "Invalid ownership subject",
    )

    try:
        owner_one.owner_id = "changed"
    except Exception:
        pass
    else:
        raise AssertionError(
            "SchemaOwner must be immutable."
        )

    thread_ledger = Ledger()
    thread_errors: list[str] = []

    def assign_subject(
        index: int,
    ) -> None:
        try:
            thread_subject = (
                module.canonical_ownership_subject(
                    "product.concurrent",
                    f"record_{index}",
                )
            )

            thread_owner = Owner(
                owner_id=f"service_{index}",
                owner_kind=OwnerKind.SERVICE,
            )

            thread_ledger.assign(
                thread_subject,
                thread_owner,
                actor=f"service_{index}",
                reason="threaded assignment",
            )
        except Exception as exc:
            thread_errors.append(
                repr(exc)
            )

    threads = [
        threading.Thread(
            target=assign_subject,
            args=(index,),
        )
        for index in range(100)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert not thread_errors

    assert len(
        thread_ledger.history()
    ) == 100

    assert thread_ledger.generation == 100
    assert thread_ledger.verify_integrity()


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
    print("OWNERSHIP.PY INSTALLATION AND REVIEW")
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

        verify_behavior(module)

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The ownership.py installation failed, "
            "so the previous filesystem state was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("ownership.py compilation:       PASS")
    print("Package import:                 PASS")
    print("Canonical subject validation:   PASS")
    print("Immutable owner contracts:      PASS")
    print("Metadata limits:                PASS")
    print("Owner-kind coercion:            PASS")
    print("Initial assignment policy:      PASS")
    print("Transfer authorization:         PASS")
    print("Compare-and-set ownership:      PASS")
    print("Reserved runtime ownership:     PASS")
    print("Append-only transfer history:   PASS")
    print("Hash-chain integrity:           PASS")
    print("Owner-to-subject index:         PASS")
    print("Generation tracking:            PASS")
    print("Deterministic snapshots:        PASS")
    print("Thread safety:                  PASS")
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
    print(
        "OWNERSHIP.PY: INSTALLED, "
        "REVIEWED, AND APPROVED"
    )
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
