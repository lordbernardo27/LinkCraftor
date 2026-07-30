"""Canonical immutable Universal Job Contract (Phase 2.1.1).

This module is the single source of truth for the shape, validation,
serialization and identity of a Universal Job. It is intentionally pure:
it performs no I/O, holds no mutable global state, and depends on nothing
outside the Python standard library. Creation, queueing, leasing, execution,
persistence and orchestration all live in later phases and must never be
imported here.
"""

from __future__ import annotations

import dataclasses
import enum
import hashlib
import json
import re
from datetime import datetime, timezone
from dataclasses import dataclass, field, fields, replace
from types import MappingProxyType
from typing import (
    Any,
    Dict,
    Final,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

# ---------------------------------------------------------------------------
# Contract version
# ---------------------------------------------------------------------------

UNIVERSAL_JOB_CONTRACT_ID: Final[str] = (
    "urn:linkcraftor:runtime:universal-job-contract"
)

UNIVERSAL_JOB_CONTRACT_VERSION: Final[str] = (
    "universal_job_contract_v2.1.1-r1"
)

# The canonical field set, in canonical order. This tuple is authoritative:
# serialization, the required-field check and the field inventory all derive
# from it, so the contract can never silently drift from this declaration.
REQUIRED_UNIVERSAL_JOB_FIELDS: Final[Tuple[str, ...]] = (
    "job_id",
    "workspace_id",
    "user_id",
    "product_id",
    "pipeline",
    "stage",
    "job_type",
    "payload_reference",
    "priority",
    "status",
    "attempts",
    "maximum_attempts",
    "lease_owner",
    "lease_id",
    "lease_started_at",
    "lease_expires_at",
    "parent_job_id",
    "dependency_job_ids",
    "batch_id",
    "pipeline_run_id",
    "progress",
    "checkpoint_reference",
    "result_reference",
    "artifact_references",
    "idempotency_key",
    "AU_reserved",
    "AU_consumed",
    "cost_record",
    "created_at",
    "scheduled_at",
    "started_at",
    "completed_at",
    "failed_at",
    "cancelled_at",
    "error_code",
    "error_message",
    "error_details",
    "contract_version",
)

JSON_PrimitiveT = Union[str, int, float, bool, None]
JSONValueT = Union[JSON_PrimitiveT, Sequence[Any], Mapping[str, Any]]

_EMPTY_MAP: Final[Mapping[str, Any]] = MappingProxyType({})
_EMPTY_TUPLE: Final[Tuple[str, ...]] = ()

_MAX_IDENTIFIER_LENGTH: Final[int] = 512
_MAX_TEXT_LENGTH: Final[int] = 16384
_MAX_REFERENCE_LENGTH: Final[int] = 4096
_MAX_COLLECTION_ITEMS: Final[int] = 4096
_INT_MAX: Final[int] = 9223372036854775807

_IDENTIFIER_RE: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@/+\-]{0,511}$")
_TIMESTAMP_RE: Final = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d{1,9})?(Z|[+-]\d{2}:\d{2})$"
)

# Canonical order of lifecycle timestamps used for consistency checks.
_TIMESTAMP_ORDER: Final[Tuple[str, ...]] = (
    "created_at",
    "scheduled_at",
    "started_at",
    "completed_at",
)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class UniversalJobContractError(ValueError):
    """Raised when a value violates the Universal Job Contract.

    ``violations`` carries the full ordered list of problems discovered during
    validation so callers do not have to re-run validation to enumerate them.
    """

    def __init__(
        self,
        message: str,
        *,
        violations: Optional[Sequence[str]] = None,
    ) -> None:
        super().__init__(message)
        self.violations: Tuple[str, ...] = tuple(violations or ())


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class UniversalJobStatus(str, enum.Enum):
    """Canonical lifecycle states. Transition rules belong to a later phase."""

    CREATED = "created"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    LEASED = "leased"
    RUNNING = "running"
    SUSPENDED = "suspended"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DEAD_LETTER = "dead_letter"
    EXPIRED = "expired"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def coerce(cls, value: Any) -> "UniversalJobStatus":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            text = value.strip().lower()
            for member in cls:
                if member.value == text:
                    return member
        raise UniversalJobContractError(
            "invalid job status: " + repr(value),
            violations=("status must be one of " + ", ".join(m.value for m in cls),),
        )


class UniversalJobPriority(enum.IntEnum):
    """Canonical priority classes.

    Backed by integers so ordering is well defined without implying any
    scheduling behaviour; lower numeric value denotes higher urgency.
    """

    CRITICAL = 10
    HIGH = 20
    NORMAL = 30
    LOW = 40
    BACKGROUND = 50

    def __str__(self) -> str:
        return self.name.lower()

    @classmethod
    def coerce(cls, value: Any) -> "UniversalJobPriority":
        if isinstance(value, cls):
            return value
        if isinstance(value, bool):
            raise UniversalJobContractError("priority must not be a boolean")
        if isinstance(value, int):
            for member in cls:
                if int(member) == value:
                    return member
        if isinstance(value, str):
            text = value.strip().lower()
            for member in cls:
                if member.name.lower() == text:
                    return member
            if text.isdigit():
                return cls.coerce(int(text))
        raise UniversalJobContractError(
            "invalid job priority: " + repr(value),
            violations=(
                "priority must be one of " + ", ".join(m.name.lower() for m in cls),
            ),
        )


# ---------------------------------------------------------------------------
# Low-level normalization helpers (pure)
# ---------------------------------------------------------------------------

def _freeze(value: Any) -> Any:
    """Recursively convert containers into immutable, JSON-safe equivalents."""
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float):
            if value != value or value in (float("inf"), float("-inf")):
                raise UniversalJobContractError(
                    "non-finite float values are not permitted in the contract"
                )
        return value
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                _require_str_key(key): _freeze(item)
                for key, item in value.items()
            }
        )
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted((_freeze(item) for item in value), key=_stable_sort_key))
    if isinstance(value, enum.Enum):
        return _freeze(value.value)
    raise UniversalJobContractError(
        "unsupported value type in contract data: " + type(value).__name__
    )


def _require_str_key(key: Any) -> str:
    if not isinstance(key, str):
        raise UniversalJobContractError(
            "mapping keys must be strings, got " + type(key).__name__
        )
    return key


def _stable_sort_key(value: Any) -> str:
    return json.dumps(_thaw(value), sort_keys=True, ensure_ascii=False, default=str)


def _thaw(value: Any) -> Any:
    """Convert frozen contract data back into plain JSON-safe structures."""
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _thaw(value),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )


def _fingerprint(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalize_optional_text(
    value: Any,
    *,
    name: str,
    violations: list,
    max_length: int = _MAX_REFERENCE_LENGTH,
) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        violations.append(name + " must be a string or null")
        return None
    text = value.strip()
    if not text:
        return None
    if len(text) > max_length:
        violations.append(name + " exceeds maximum length of " + str(max_length))
        return text[:max_length]
    return text


def _normalize_identifier(
    value: Any,
    *,
    name: str,
    violations: list,
    required: bool,
) -> Optional[str]:
    text = _normalize_optional_text(
        value, name=name, violations=violations, max_length=_MAX_IDENTIFIER_LENGTH
    )
    if text is None:
        if required:
            violations.append(name + " is required")
        return None
    if not _IDENTIFIER_RE.match(text):
        violations.append(name + " is not a valid identifier: " + text)
    return text


def _normalize_timestamp(
    value: Any,
    *,
    name: str,
    violations: list,
) -> Optional[str]:
    """Validate and normalize an ISO-8601 timestamp to canonical UTC."""
    if value is None:
        return None

    if not isinstance(value, str):
        violations.append(
            name + " must be an ISO-8601 string or null"
        )
        return None

    text = value.strip()

    if not text:
        return None

    if not _TIMESTAMP_RE.match(text):
        violations.append(
            name + " must be an ISO-8601 timestamp: " + text
        )
        return text

    parse_text = text

    if parse_text.endswith("Z"):
        parse_text = (
            parse_text[:-1]
            + "+00:00"
        )

    try:
        parsed = datetime.fromisoformat(
            parse_text
        )
    except ValueError:
        violations.append(
            name + " is not a valid calendar timestamp: " + text
        )
        return text

    if parsed.tzinfo is None:
        violations.append(
            name + " must include a timezone offset"
        )
        return text

    normalized = (
        parsed
        .astimezone(timezone.utc)
        .isoformat(
            timespec="microseconds"
        )
        .replace(
            "+00:00",
            "Z",
        )
    )

    return normalized


def _normalize_non_negative_int(
    value: Any,
    *,
    name: str,
    violations: list,
    default: int = 0,
) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int):
        violations.append(name + " must be a non-negative integer")
        return default
    if value < 0:
        violations.append(name + " must not be negative")
        return default
    if value > _INT_MAX:
        violations.append(name + " exceeds the maximum permitted integer")
        return _INT_MAX
    return value


def _normalize_identifier_tuple(
    value: Any,
    *,
    name: str,
    violations: list,
) -> Tuple[str, ...]:
    if value is None:
        return _EMPTY_TUPLE
    if isinstance(value, (str, bytes)) or isinstance(value, Mapping):
        violations.append(name + " must be a sequence of identifiers")
        return _EMPTY_TUPLE
    try:
        items = list(value)
    except TypeError:
        violations.append(name + " must be an iterable of identifiers")
        return _EMPTY_TUPLE
    if len(items) > _MAX_COLLECTION_ITEMS:
        violations.append(name + " exceeds the maximum item count")
        items = items[:_MAX_COLLECTION_ITEMS]
    seen: Dict[str, None] = {}
    for item in items:
        identifier = _normalize_identifier(
            item, name=name + "[]", violations=violations, required=True
        )
        if identifier is not None:
            seen.setdefault(identifier, None)
    return tuple(sorted(seen))


def _normalize_reference_tuple(
    value: Any,
    *,
    name: str,
    violations: list,
) -> Tuple[str, ...]:
    if value is None:
        return _EMPTY_TUPLE
    if isinstance(value, (str, bytes)) or isinstance(value, Mapping):
        violations.append(name + " must be a sequence of references")
        return _EMPTY_TUPLE
    try:
        items = list(value)
    except TypeError:
        violations.append(name + " must be an iterable of references")
        return _EMPTY_TUPLE
    if len(items) > _MAX_COLLECTION_ITEMS:
        violations.append(name + " exceeds the maximum item count")
        items = items[:_MAX_COLLECTION_ITEMS]
    references = []
    for item in items:
        reference = _normalize_optional_text(
            item, name=name + "[]", violations=violations
        )
        if reference is None:
            violations.append(name + " must not contain empty references")
            continue
        references.append(reference)
    return tuple(references)


def _normalize_mapping(value: Any, *, name: str, violations: list) -> Mapping[str, Any]:
    if value is None:
        return _EMPTY_MAP
    if not isinstance(value, Mapping):
        violations.append(name + " must be a mapping")
        return _EMPTY_MAP
    if len(value) > _MAX_COLLECTION_ITEMS:
        violations.append(name + " exceeds the maximum entry count")
    try:
        return _freeze(value)
    except UniversalJobContractError as exc:
        violations.append(name + ": " + str(exc))
        return _EMPTY_MAP


# ---------------------------------------------------------------------------
# Validation report
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class UniversalJobValidationReport:
    """Immutable result of validating a candidate Universal Job."""

    is_valid: bool
    violations: Tuple[str, ...] = _EMPTY_TUPLE
    contract_version: str = UNIVERSAL_JOB_CONTRACT_VERSION
    checked_field_count: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "violations", tuple(self.violations))

    def raise_for_status(self) -> None:
        if not self.is_valid:
            raise UniversalJobContractError(
                "universal job failed contract validation: "
                + "; ".join(self.violations),
                violations=self.violations,
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "violations": list(self.violations),
            "contract_version": self.contract_version,
            "checked_field_count": self.checked_field_count,
        }


# ---------------------------------------------------------------------------
# Composed value objects
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class UniversalJobProgress:
    """Immutable progress snapshot. Carries no scheduling behaviour."""

    percent: int = 0
    step: str = ""
    message: str = ""
    total_units: Optional[int] = None
    completed_units: Optional[int] = None
    updated_at: Optional[str] = None

    def __post_init__(self) -> None:
        violations: list = []
        set_ = object.__setattr__

        percent = _normalize_non_negative_int(
            self.percent, name="progress.percent", violations=violations
        )
        if percent > 100:
            violations.append("progress.percent must not exceed 100")
            percent = 100
        set_(self, "percent", percent)

        step = _normalize_optional_text(
            self.step, name="progress.step", violations=violations,
            max_length=_MAX_IDENTIFIER_LENGTH,
        )
        set_(self, "step", step or "")

        message = _normalize_optional_text(
            self.message, name="progress.message", violations=violations,
            max_length=_MAX_TEXT_LENGTH,
        )
        set_(self, "message", message or "")

        total = (
            None
            if self.total_units is None
            else _normalize_non_negative_int(
                self.total_units, name="progress.total_units", violations=violations
            )
        )
        completed = (
            None
            if self.completed_units is None
            else _normalize_non_negative_int(
                self.completed_units,
                name="progress.completed_units",
                violations=violations,
            )
        )
        if total is not None and completed is not None and completed > total:
            violations.append(
                "progress.completed_units must not exceed progress.total_units"
            )
        set_(self, "total_units", total)
        set_(self, "completed_units", completed)

        set_(
            self,
            "updated_at",
            _normalize_timestamp(
                self.updated_at, name="progress.updated_at", violations=violations
            ),
        )

        if violations:
            raise UniversalJobContractError(
                "invalid progress: " + "; ".join(violations),
                violations=violations,
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "percent": self.percent,
            "step": self.step,
            "message": self.message,
            "total_units": self.total_units,
            "completed_units": self.completed_units,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_value(cls, value: Any) -> "UniversalJobProgress":
        if isinstance(value, cls):
            return value
        if value is None:
            return cls()
        if isinstance(value, Mapping):
            known = {f.name for f in fields(cls)}
            return cls(**{key: value[key] for key in value if key in known})
        raise UniversalJobContractError(
            "progress must be a mapping or UniversalJobProgress"
        )


@dataclass(frozen=True)
class UniversalJobCostRecord:
    """Immutable accounting record. Pure data; performs no metering."""

    currency: str = "USD"
    estimated_micros: int = 0
    actual_micros: int = 0
    au_rate_micros: int = 0
    breakdown: Mapping[str, Any] = _EMPTY_MAP

    def __post_init__(self) -> None:
        violations: list = []
        set_ = object.__setattr__

        currency = _normalize_optional_text(
            self.currency, name="cost_record.currency", violations=violations,
            max_length=16,
        )
        currency = (currency or "USD").upper()
        if not re.match(r"^[A-Z]{3,10}$", currency):
            violations.append("cost_record.currency must be a currency code")
        set_(self, "currency", currency)

        set_(self, "estimated_micros", _normalize_non_negative_int(
            self.estimated_micros, name="cost_record.estimated_micros",
            violations=violations,
        ))
        set_(self, "actual_micros", _normalize_non_negative_int(
            self.actual_micros, name="cost_record.actual_micros",
            violations=violations,
        ))
        set_(self, "au_rate_micros", _normalize_non_negative_int(
            self.au_rate_micros, name="cost_record.au_rate_micros",
            violations=violations,
        ))
        set_(self, "breakdown", _normalize_mapping(
            self.breakdown, name="cost_record.breakdown", violations=violations,
        ))

        if violations:
            raise UniversalJobContractError(
                "invalid cost record: " + "; ".join(violations),
                violations=violations,
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "currency": self.currency,
            "estimated_micros": self.estimated_micros,
            "actual_micros": self.actual_micros,
            "au_rate_micros": self.au_rate_micros,
            "breakdown": _thaw(self.breakdown),
        }

    @classmethod
    def from_value(cls, value: Any) -> "UniversalJobCostRecord":
        if isinstance(value, cls):
            return value
        if value is None:
            return cls()
        if isinstance(value, Mapping):
            known = {f.name for f in fields(cls)}
            return cls(**{key: value[key] for key in value if key in known})
        raise UniversalJobContractError(
            "cost_record must be a mapping or UniversalJobCostRecord"
        )


# ---------------------------------------------------------------------------
# The canonical Universal Job
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class UniversalJob:
    """The canonical, immutable Universal Job Contract.

    Every field is normalized and validated at construction. Instances are
    deeply immutable: nested mappings are read-only proxies and nested
    sequences are tuples. Construction raises ``UniversalJobContractError``
    when the data cannot satisfy the contract.
    """

    # Identity and ownership
    job_id: str
    workspace_id: str
    user_id: str = "system"
    product_id: str = "linkcraftor"

    # Classification
    pipeline: str = ""
    stage: str = ""
    job_type: str = ""

    # Payload
    payload_reference: Optional[str] = None

    # Scheduling inputs
    priority: UniversalJobPriority = UniversalJobPriority.NORMAL
    status: UniversalJobStatus = UniversalJobStatus.CREATED

    # Attempts
    attempts: int = 0
    maximum_attempts: int = 1

    # Lease (declared shape only; no lease operations here)
    lease_owner: Optional[str] = None
    lease_id: Optional[str] = None
    lease_started_at: Optional[str] = None
    lease_expires_at: Optional[str] = None

    # Relationships
    parent_job_id: Optional[str] = None
    dependency_job_ids: Tuple[str, ...] = _EMPTY_TUPLE
    batch_id: Optional[str] = None
    pipeline_run_id: Optional[str] = None

    # Progress and checkpointing
    progress: UniversalJobProgress = field(default_factory=UniversalJobProgress)
    checkpoint_reference: Optional[str] = None

    # Results
    result_reference: Optional[str] = None
    artifact_references: Tuple[str, ...] = _EMPTY_TUPLE

    # Idempotency
    idempotency_key: Optional[str] = None

    # Accounting
    AU_reserved: int = 0
    AU_consumed: int = 0
    cost_record: UniversalJobCostRecord = field(
        default_factory=UniversalJobCostRecord
    )

    # Lifecycle timestamps
    created_at: Optional[str] = None
    scheduled_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    cancelled_at: Optional[str] = None

    # Diagnostics
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Mapping[str, Any] = _EMPTY_MAP

    # Contract version stamped onto every instance
    contract_version: str = UNIVERSAL_JOB_CONTRACT_VERSION

    def __post_init__(self) -> None:
        violations: list = []
        set_ = object.__setattr__

        set_(self, "job_id", _normalize_identifier(
            self.job_id, name="job_id", violations=violations, required=True) or "")
        set_(self, "workspace_id", _normalize_identifier(
            self.workspace_id, name="workspace_id", violations=violations,
            required=True) or "")
        set_(self, "user_id", _normalize_identifier(
            self.user_id, name="user_id", violations=violations, required=False)
            or "system")
        set_(self, "product_id", _normalize_identifier(
            self.product_id, name="product_id", violations=violations,
            required=False) or "linkcraftor")

        for name in ("pipeline", "stage"):
            value = _normalize_optional_text(
                getattr(self, name), name=name, violations=violations,
                max_length=_MAX_IDENTIFIER_LENGTH,
            )
            set_(self, name, value or "")

        job_type = _normalize_optional_text(
            self.job_type,
            name="job_type",
            violations=violations,
            max_length=_MAX_IDENTIFIER_LENGTH,
        )
        if job_type is None:
            violations.append("job_type is required")
        set_(self, "job_type", job_type or "")

        set_(self, "payload_reference", _normalize_optional_text(
            self.payload_reference, name="payload_reference", violations=violations))

        try:
            set_(self, "priority", UniversalJobPriority.coerce(self.priority))
        except UniversalJobContractError as exc:
            violations.extend(exc.violations or (str(exc),))
            set_(self, "priority", UniversalJobPriority.NORMAL)

        try:
            set_(self, "status", UniversalJobStatus.coerce(self.status))
        except UniversalJobContractError as exc:
            violations.extend(exc.violations or (str(exc),))
            set_(self, "status", UniversalJobStatus.CREATED)

        set_(self, "attempts", _normalize_non_negative_int(
            self.attempts, name="attempts", violations=violations))
        maximum_attempts = _normalize_non_negative_int(
            self.maximum_attempts, name="maximum_attempts", violations=violations,
            default=1,
        )
        if maximum_attempts < 1:
            violations.append("maximum_attempts must be at least 1")
            maximum_attempts = 1
        set_(self, "maximum_attempts", maximum_attempts)
        if self.attempts > maximum_attempts:
            violations.append("attempts must not exceed maximum_attempts")

        for name in ("lease_owner", "lease_id"):
            set_(self, name, _normalize_identifier(
                getattr(self, name), name=name, violations=violations,
                required=False))
        set_(self, "lease_started_at", _normalize_timestamp(
            self.lease_started_at, name="lease_started_at", violations=violations))
        set_(self, "lease_expires_at", _normalize_timestamp(
            self.lease_expires_at, name="lease_expires_at", violations=violations))
        if self.lease_started_at and self.lease_expires_at:
            if self.lease_expires_at < self.lease_started_at:
                violations.append(
                    "lease_expires_at must not precede lease_started_at")

        set_(self, "parent_job_id", _normalize_identifier(
            self.parent_job_id, name="parent_job_id", violations=violations,
            required=False))
        set_(self, "dependency_job_ids", _normalize_identifier_tuple(
            self.dependency_job_ids, name="dependency_job_ids",
            violations=violations))
        if self.job_id and self.job_id in self.dependency_job_ids:
            violations.append("dependency_job_ids must not contain job_id")
        set_(self, "batch_id", _normalize_identifier(
            self.batch_id, name="batch_id", violations=violations, required=False))
        set_(self, "pipeline_run_id", _normalize_identifier(
            self.pipeline_run_id, name="pipeline_run_id", violations=violations,
            required=False))

        try:
            set_(self, "progress", UniversalJobProgress.from_value(self.progress))
        except UniversalJobContractError as exc:
            violations.extend(exc.violations or (str(exc),))
            set_(self, "progress", UniversalJobProgress())

        set_(self, "checkpoint_reference", _normalize_optional_text(
            self.checkpoint_reference, name="checkpoint_reference",
            violations=violations))
        set_(self, "result_reference", _normalize_optional_text(
            self.result_reference, name="result_reference", violations=violations))
        set_(self, "artifact_references", _normalize_reference_tuple(
            self.artifact_references, name="artifact_references",
            violations=violations))

        set_(self, "idempotency_key", _normalize_identifier(
            self.idempotency_key, name="idempotency_key", violations=violations,
            required=False))

        set_(self, "AU_reserved", _normalize_non_negative_int(
            self.AU_reserved, name="AU_reserved", violations=violations))
        set_(self, "AU_consumed", _normalize_non_negative_int(
            self.AU_consumed, name="AU_consumed", violations=violations))

        try:
            set_(self, "cost_record", UniversalJobCostRecord.from_value(
                self.cost_record))
        except UniversalJobContractError as exc:
            violations.extend(exc.violations or (str(exc),))
            set_(self, "cost_record", UniversalJobCostRecord())

        for name in _TIMESTAMP_ORDER + ("failed_at", "cancelled_at"):
            set_(self, name, _normalize_timestamp(
                getattr(self, name), name=name, violations=violations))

        if self.created_at is None:
            violations.append("created_at is required")

        self._check_timestamp_ordering(violations)

        set_(self, "error_code", _normalize_identifier(
            self.error_code, name="error_code", violations=violations,
            required=False))
        set_(self, "error_message", _normalize_optional_text(
            self.error_message, name="error_message", violations=violations,
            max_length=_MAX_TEXT_LENGTH))
        set_(self, "error_details", _normalize_mapping(
            self.error_details, name="error_details", violations=violations))

        version = _normalize_optional_text(
            self.contract_version, name="contract_version", violations=violations,
            max_length=_MAX_IDENTIFIER_LENGTH,
        )
        if version != UNIVERSAL_JOB_CONTRACT_VERSION:
            violations.append(
                "contract_version must be " + UNIVERSAL_JOB_CONTRACT_VERSION)
        set_(self, "contract_version", version or UNIVERSAL_JOB_CONTRACT_VERSION)

        if violations:
            raise UniversalJobContractError(
                "invalid universal job: " + "; ".join(violations),
                violations=violations,
            )

    def _check_timestamp_ordering(self, violations: list) -> None:
        present = [
            (name, getattr(self, name))
            for name in _TIMESTAMP_ORDER
            if getattr(self, name) is not None
        ]
        for (earlier_name, earlier), (later_name, later) in zip(present, present[1:]):
            if later < earlier:
                violations.append(
                    later_name + " must not precede " + earlier_name)

    # -- derived views ------------------------------------------------------

    @property
    def is_terminal(self) -> bool:
        return self.status in _TERMINAL_STATUSES

    @property
    def is_leased(self) -> bool:
        return self.lease_owner is not None and self.status == UniversalJobStatus.LEASED

    # -- immutable evolution ------------------------------------------------

    def evolve(self, **changes: Any) -> "UniversalJob":
        """Return a new validated job with the given fields replaced.

        This never mutates ``self``; it is a pure constructor for a derived
        contract instance and applies the full validation pass again.
        """
        unknown = set(changes) - _CONTRACT_CONSTRUCTOR_FIELDS
        if unknown:
            raise UniversalJobContractError(
                "unknown fields for evolve: " + ", ".join(sorted(unknown))
            )
        return replace(self, **changes)

    # -- serialization ------------------------------------------------------

    def to_canonical_dict(self) -> Dict[str, Any]:
        """Return a plain, JSON-safe dict in canonical field order."""
        return {
            "job_id": self.job_id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "pipeline": self.pipeline,
            "stage": self.stage,
            "job_type": self.job_type,
            "payload_reference": self.payload_reference,
            "priority": str(self.priority),
            "status": self.status.value,
            "attempts": self.attempts,
            "maximum_attempts": self.maximum_attempts,
            "lease_owner": self.lease_owner,
            "lease_id": self.lease_id,
            "lease_started_at": self.lease_started_at,
            "lease_expires_at": self.lease_expires_at,
            "parent_job_id": self.parent_job_id,
            "dependency_job_ids": list(self.dependency_job_ids),
            "batch_id": self.batch_id,
            "pipeline_run_id": self.pipeline_run_id,
            "progress": self.progress.to_dict(),
            "checkpoint_reference": self.checkpoint_reference,
            "result_reference": self.result_reference,
            "artifact_references": list(self.artifact_references),
            "idempotency_key": self.idempotency_key,
            "AU_reserved": self.AU_reserved,
            "AU_consumed": self.AU_consumed,
            "cost_record": self.cost_record.to_dict(),
            "created_at": self.created_at,
            "scheduled_at": self.scheduled_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "failed_at": self.failed_at,
            "cancelled_at": self.cancelled_at,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "error_details": _thaw(self.error_details),
            "contract_version": self.contract_version,
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.to_canonical_dict()

    def to_canonical_json(self) -> str:
        return _canonical_json(
            self.to_canonical_dict()
        )

    @classmethod
    def required_fields(
        cls,
    ) -> Tuple[str, ...]:
        """Return the immutable canonical required-field roster."""
        return REQUIRED_UNIVERSAL_JOB_FIELDS

    @classmethod
    def schema(
        cls,
    ) -> Mapping[str, Any]:
        """Return the immutable canonical contract schema identity."""
        return MappingProxyType(
            {
                "contract_id": (
                    UNIVERSAL_JOB_CONTRACT_ID
                ),
                "contract_version": (
                    UNIVERSAL_JOB_CONTRACT_VERSION
                ),
                "required_fields": (
                    REQUIRED_UNIVERSAL_JOB_FIELDS
                ),
            }
        )

    # -- deserialization / reconstruction -----------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "UniversalJob":
        if not isinstance(
            data,
            Mapping,
        ):
            raise UniversalJobContractError(
                "job data must be a mapping"
            )

        unknown_fields = sorted(
            set(data)
            - _CONTRACT_CONSTRUCTOR_FIELDS
        )

        if unknown_fields:
            raise UniversalJobContractError(
                "unknown universal job fields: "
                + ", ".join(
                    unknown_fields
                ),
                violations=tuple(
                    "unknown field: " + name
                    for name in unknown_fields
                ),
            )

        missing_fields = tuple(
            name
            for name in REQUIRED_UNIVERSAL_JOB_FIELDS
            if name not in data
        )

        if missing_fields:
            raise UniversalJobContractError(
                "missing required universal job fields: "
                + ", ".join(
                    missing_fields
                ),
                violations=tuple(
                    "missing required field: " + name
                    for name in missing_fields
                ),
            )

        kwargs = {
            key: data[key]
            for key in data
        }

        if "priority" in kwargs:
            kwargs["priority"] = (
                UniversalJobPriority.coerce(
                    kwargs["priority"]
                )
            )

        if "status" in kwargs:
            kwargs["status"] = (
                UniversalJobStatus.coerce(
                    kwargs["status"]
                )
            )

        if "progress" in kwargs:
            kwargs["progress"] = (
                UniversalJobProgress.from_value(
                    kwargs["progress"]
                )
            )

        if "cost_record" in kwargs:
            kwargs["cost_record"] = (
                UniversalJobCostRecord.from_value(
                    kwargs["cost_record"]
                )
            )

        return cls(
            **kwargs
        )

    @classmethod
    def from_json(cls, text: str) -> "UniversalJob":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise UniversalJobContractError(
                "job json is not decodable: " + str(exc)) from exc
        return cls.from_dict(data)

    @classmethod
    def reconstruct(cls, data: Mapping[str, Any]) -> "UniversalJob":
        """Alias for :meth:`from_dict` for reconstruction call sites."""
        return cls.from_dict(data)

    # -- identity and hashing -----------------------------------------------

    def identity_fingerprint(self) -> str:
        """Stable across mutable state; depends only on identity inputs."""
        material = {
            "job_id": self.job_id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "pipeline": self.pipeline,
            "stage": self.stage,
            "job_type": self.job_type,
            "idempotency_key": self.idempotency_key,
            "contract_version": self.contract_version,
        }
        return _fingerprint(_canonical_json(material))

    def contract_fingerprint(self) -> str:
        """Fingerprint the frozen canonical contract field set."""
        canonical = self.to_canonical_dict()

        material = {
            "contract_id": (
                UNIVERSAL_JOB_CONTRACT_ID
            ),
            "contract_version": (
                self.contract_version
            ),
            "fields": {
                name: canonical[name]
                for name
                in REQUIRED_UNIVERSAL_JOB_FIELDS
            },
        }

        return _fingerprint(
            _canonical_json(
                material
            )
        )

    def content_fingerprint(self) -> str:
        """Cover every canonical serialized field of this job."""
        return _fingerprint(
            self.to_canonical_json()
        )

    def __hash__(self) -> int:
        """Return a deterministic hash independent of Python hash seeding."""
        digest = hashlib.sha256(
            self.to_canonical_json().encode(
                "utf-8"
            )
        ).digest()

        return int.from_bytes(
            digest[:8],
            byteorder="big",
            signed=True,
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, UniversalJob):
            return NotImplemented
        return self.to_canonical_dict() == other.to_canonical_dict()

    # -- validation ---------------------------------------------------------

    def validate(self) -> UniversalJobValidationReport:
        """Re-run structural validation and return a report.

        Construction already guarantees a valid instance; this method exists so
        callers can obtain a report (for example after :meth:`from_dict`)
        without catching exceptions.
        """
        return validate_universal_job(self)


_TERMINAL_STATUSES: Final[frozenset] = frozenset(
    {
        UniversalJobStatus.SUCCEEDED,
        UniversalJobStatus.FAILED,
        UniversalJobStatus.CANCELLED,
        UniversalJobStatus.DEAD_LETTER,
        UniversalJobStatus.EXPIRED,
    }
)

_CONTRACT_CONSTRUCTOR_FIELDS: Final[frozenset] = frozenset(
    f.name for f in fields(UniversalJob)
)


# ---------------------------------------------------------------------------
# Standalone validation
# ---------------------------------------------------------------------------

def validate_universal_job(candidate: Any) -> UniversalJobValidationReport:
    """Validate a job or candidate mapping without raising.

    A :class:`UniversalJob` instance is valid by construction. A mapping is
    validated by attempting reconstruction and capturing any contract
    violations. Returns an immutable :class:`UniversalJobValidationReport`.
    """
    if isinstance(candidate, UniversalJob):
        return UniversalJobValidationReport(
            is_valid=True,
            violations=_EMPTY_TUPLE,
            contract_version=candidate.contract_version,
            checked_field_count=len(REQUIRED_UNIVERSAL_JOB_FIELDS),
        )

    if not isinstance(candidate, Mapping):
        return UniversalJobValidationReport(
            is_valid=False,
            violations=("candidate must be a UniversalJob or mapping",),
            checked_field_count=0,
        )

    missing = tuple(
        name
        for name in REQUIRED_UNIVERSAL_JOB_FIELDS
        if name not in candidate
    )
    try:
        UniversalJob.from_dict(candidate)
    except UniversalJobContractError as exc:
        violations = tuple(exc.violations) or (str(exc),)
        return UniversalJobValidationReport(
            is_valid=False,
            violations=violations,
            checked_field_count=len(REQUIRED_UNIVERSAL_JOB_FIELDS),
        )

    if missing:
        return UniversalJobValidationReport(
            is_valid=False,
            violations=tuple(
                "missing required field: " + name
                for name in missing
            ),
            checked_field_count=(
                len(
                    REQUIRED_UNIVERSAL_JOB_FIELDS
                )
            ),
        )

    return UniversalJobValidationReport(
        is_valid=True,
        violations=_EMPTY_TUPLE,
        checked_field_count=(
            len(
                REQUIRED_UNIVERSAL_JOB_FIELDS
            )
        ),
    )


__all__ = [
    "UNIVERSAL_JOB_CONTRACT_ID",
    "UNIVERSAL_JOB_CONTRACT_VERSION",
    "REQUIRED_UNIVERSAL_JOB_FIELDS",
    "UniversalJob",
    "UniversalJobValidationReport",
    "UniversalJobContractError",
    "UniversalJobStatus",
    "UniversalJobPriority",
    "UniversalJobProgress",
    "UniversalJobCostRecord",
    "validate_universal_job",
]