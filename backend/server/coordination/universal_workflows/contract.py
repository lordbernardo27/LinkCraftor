"""
LinkCraftor Universal Workflow Contract
=======================================

Canonical immutable contract representing one complete coordinated workflow
execution.

This module belongs to the Universal Coordination Framework.

It is intentionally pure:
- no I/O
- no queue access
- no worker access
- no Runtime Registration
- no pipeline-specific business logic
- no mutable global workflow state

A Universal Workflow may coordinate many Universal Runtime jobs, but it does
not execute those jobs itself.
"""

from __future__ import annotations

import enum
import hashlib
import json
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Final, Mapping, Optional, Tuple


# ============================================================================
# 1. Contract identity
# ============================================================================

UNIVERSAL_WORKFLOW_CONTRACT_ID: Final[str] = (
    "urn:linkcraftor:coordination:universal-workflow-contract"
)

UNIVERSAL_WORKFLOW_CONTRACT_VERSION: Final[str] = (
    "universal_workflow_contract_v1.1.0"
)

UNIVERSAL_WORKFLOW_SCHEMA_VERSION: Final[str] = (
    "universal_workflow_schema_v1"
)


# ============================================================================
# 2. Canonical required fields
# ============================================================================

REQUIRED_UNIVERSAL_WORKFLOW_FIELDS: Final[Tuple[str, ...]] = (
    # Identity
    "workflow_id",
    "workflow_type",
    "workflow_version",
    "workspace_id",

    # Ownership / coordination
    "coordinator_id",
    "coordinator_version",

    # Correlation
    "correlation_id",
    "parent_workflow_id",
    "root_workflow_id",

    # Lifecycle
    "status",

    # Workflow data
    "input_reference",
    "context",
    "metadata",

    # Stage-state summaries
    "current_stage",
    "completed_stages",
    "pending_stages",
    "failed_stages",
    "skipped_stages",

    # Results / evidence
    "result_reference",
    "artifact_references",

    # Idempotency
    "idempotency_key",

    # Timestamps
    "created_at",
    "started_at",
    "updated_at",
    "completed_at",
    "failed_at",
    "cancelled_at",

    # Failure
    "failure_code",
    "failure_message",
    "failure_details",

    # Contract identity
    "contract_version",
)


# ============================================================================
# 3. Errors
# ============================================================================

class UniversalWorkflowContractError(ValueError):
    """Raised when a Universal Workflow violates the canonical contract."""

    def __init__(
        self,
        message: str,
        *,
        violations: Tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.violations = tuple(violations)


# ============================================================================
# 4. Workflow lifecycle status
# ============================================================================

class UniversalWorkflowStatus(str, enum.Enum):
    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    PAUSED = "PAUSED"
    RECOVERING = "RECOVERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"

    @classmethod
    def coerce(cls, value: Any) -> "UniversalWorkflowStatus":
        if isinstance(value, cls):
            return value

        if not isinstance(value, str):
            raise UniversalWorkflowContractError(
                "workflow status must be a string or UniversalWorkflowStatus"
            )

        normalized = value.strip().upper()

        try:
            return cls(normalized)
        except ValueError as exc:
            raise UniversalWorkflowContractError(
                f"unknown workflow status: {value!r}"
            ) from exc


TERMINAL_WORKFLOW_STATUSES: Final[frozenset[UniversalWorkflowStatus]] = (
    frozenset(
        {
            UniversalWorkflowStatus.COMPLETED,
            UniversalWorkflowStatus.FAILED,
            UniversalWorkflowStatus.CANCELLED,
            UniversalWorkflowStatus.ABORTED,
        }
    )
)


# ============================================================================
# 5. Immutable mapping helpers
# ============================================================================

_EMPTY_MAPPING: Final[Mapping[str, Any]] = MappingProxyType({})
_EMPTY_TUPLE: Final[Tuple[str, ...]] = ()


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                str(key): _freeze(item)
                for key, item in value.items()
            }
        )

    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)

    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)

    if isinstance(value, set):
        return tuple(
            sorted(
                (_freeze(item) for item in value),
                key=repr,
            )
        )

    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _thaw(item)
            for key, item in value.items()
        }

    if isinstance(value, tuple):
        return [_thaw(item) for item in value]

    return value


# ============================================================================
# 6. Validation helpers
# ============================================================================

def _require_nonempty_string(
    value: Any,
    *,
    name: str,
    violations: list[str],
) -> str:
    if not isinstance(value, str):
        violations.append(f"{name} must be a string")
        return ""

    normalized = value.strip()

    if not normalized:
        violations.append(f"{name} must be non-empty")

    return normalized


def _optional_string(
    value: Any,
    *,
    name: str,
    violations: list[str],
) -> Optional[str]:
    if value is None:
        return None

    if not isinstance(value, str):
        violations.append(f"{name} must be a string or None")
        return None

    normalized = value.strip()

    return normalized or None


def _normalize_string_tuple(
    value: Any,
    *,
    name: str,
    violations: list[str],
) -> Tuple[str, ...]:
    if value is None:
        return ()

    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        violations.append(f"{name} must be a list or tuple of strings")
        return ()

    normalized: list[str] = []

    for index, item in enumerate(value):
        if not isinstance(item, str):
            violations.append(
                f"{name}[{index}] must be a string"
            )
            continue

        item = item.strip()

        if not item:
            violations.append(
                f"{name}[{index}] must be non-empty"
            )
            continue

        if item not in normalized:
            normalized.append(item)

    return tuple(normalized)


def _normalize_mapping(
    value: Any,
    *,
    name: str,
    violations: list[str],
) -> Mapping[str, Any]:
    if value is None:
        return _EMPTY_MAPPING

    if not isinstance(value, Mapping):
        violations.append(f"{name} must be a mapping")
        return _EMPTY_MAPPING

    return _freeze(value)


def _normalize_timestamp(
    value: Any,
    *,
    name: str,
    required: bool,
    violations: list[str],
) -> Optional[str]:
    if value is None:
        if required:
            violations.append(f"{name} is required")
        return None

    if not isinstance(value, str):
        violations.append(f"{name} must be an ISO-8601 string or None")
        return None

    normalized = value.strip()

    if not normalized:
        if required:
            violations.append(f"{name} must be non-empty")
        return None

    candidate = normalized

    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        violations.append(
            f"{name} must be a valid ISO-8601 timestamp"
        )
        return normalized

    if parsed.tzinfo is None:
        violations.append(
            f"{name} must include timezone information"
        )
        return normalized

    utc_value = parsed.astimezone(timezone.utc)

    return utc_value.isoformat().replace("+00:00", "Z")


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _fingerprint(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ============================================================================
# 7. Validation report
# ============================================================================

@dataclass(frozen=True, slots=True)
class UniversalWorkflowValidationReport:
    is_valid: bool
    violations: Tuple[str, ...] = ()
    contract_version: str = UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    checked_field_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "violations": list(self.violations),
            "contract_version": self.contract_version,
            "checked_field_count": self.checked_field_count,
        }


# ============================================================================
# 8. Universal Workflow
# ============================================================================

@dataclass(frozen=True, slots=True)
class UniversalWorkflow:
    """
    Canonical immutable representation of one coordinated workflow execution.

    This object describes workflow identity and coordination state. It does not
    execute stages or runtime jobs.
    """

    # Identity
    workflow_id: str
    workflow_type: str
    workflow_version: str
    workspace_id: str

    # Coordinator identity
    coordinator_id: str
    coordinator_version: str

    # Correlation
    correlation_id: str
    parent_workflow_id: Optional[str]
    root_workflow_id: str

    # Lifecycle
    status: UniversalWorkflowStatus

    # Workflow input/context
    input_reference: Optional[str]
    context: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    # Stage summaries
    current_stage: Optional[str] = None
    completed_stages: Tuple[str, ...] = ()
    pending_stages: Tuple[str, ...] = ()
    failed_stages: Tuple[str, ...] = ()
    skipped_stages: Tuple[str, ...] = ()

    # Result/evidence
    result_reference: Optional[str] = None
    artifact_references: Tuple[str, ...] = ()

    # Duplicate protection
    idempotency_key: Optional[str] = None

    # Timestamps
    created_at: str = ""
    started_at: Optional[str] = None
    updated_at: str = ""
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    cancelled_at: Optional[str] = None

    # Failure
    failure_code: Optional[str] = None
    failure_message: Optional[str] = None
    failure_details: Mapping[str, Any] = field(default_factory=dict)

    # Contract
    contract_version: str = UNIVERSAL_WORKFLOW_CONTRACT_VERSION

    def __post_init__(self) -> None:
        violations: list[str] = []

        workflow_id = _require_nonempty_string(
            self.workflow_id,
            name="workflow_id",
            violations=violations,
        )

        workflow_type = _require_nonempty_string(
            self.workflow_type,
            name="workflow_type",
            violations=violations,
        )

        workflow_version = _require_nonempty_string(
            self.workflow_version,
            name="workflow_version",
            violations=violations,
        )

        workspace_id = _require_nonempty_string(
            self.workspace_id,
            name="workspace_id",
            violations=violations,
        )

        coordinator_id = _require_nonempty_string(
            self.coordinator_id,
            name="coordinator_id",
            violations=violations,
        )

        coordinator_version = _require_nonempty_string(
            self.coordinator_version,
            name="coordinator_version",
            violations=violations,
        )

        correlation_id = _require_nonempty_string(
            self.correlation_id,
            name="correlation_id",
            violations=violations,
        )

        parent_workflow_id = _optional_string(
            self.parent_workflow_id,
            name="parent_workflow_id",
            violations=violations,
        )

        root_workflow_id = _require_nonempty_string(
            self.root_workflow_id,
            name="root_workflow_id",
            violations=violations,
        )

        try:
            status = UniversalWorkflowStatus.coerce(
                self.status
            )
        except UniversalWorkflowContractError as exc:
            violations.extend(
                exc.violations or (str(exc),)
            )
            status = UniversalWorkflowStatus.CREATED

        input_reference = _optional_string(
            self.input_reference,
            name="input_reference",
            violations=violations,
        )

        current_stage = _optional_string(
            self.current_stage,
            name="current_stage",
            violations=violations,
        )

        result_reference = _optional_string(
            self.result_reference,
            name="result_reference",
            violations=violations,
        )

        idempotency_key = _optional_string(
            self.idempotency_key,
            name="idempotency_key",
            violations=violations,
        )

        failure_code = _optional_string(
            self.failure_code,
            name="failure_code",
            violations=violations,
        )

        failure_message = _optional_string(
            self.failure_message,
            name="failure_message",
            violations=violations,
        )

        context = _normalize_mapping(
            self.context,
            name="context",
            violations=violations,
        )

        metadata = _normalize_mapping(
            self.metadata,
            name="metadata",
            violations=violations,
        )

        failure_details = _normalize_mapping(
            self.failure_details,
            name="failure_details",
            violations=violations,
        )

        completed_stages = _normalize_string_tuple(
            self.completed_stages,
            name="completed_stages",
            violations=violations,
        )

        pending_stages = _normalize_string_tuple(
            self.pending_stages,
            name="pending_stages",
            violations=violations,
        )

        failed_stages = _normalize_string_tuple(
            self.failed_stages,
            name="failed_stages",
            violations=violations,
        )

        skipped_stages = _normalize_string_tuple(
            self.skipped_stages,
            name="skipped_stages",
            violations=violations,
        )

        artifact_references = _normalize_string_tuple(
            self.artifact_references,
            name="artifact_references",
            violations=violations,
        )

        created_at = _normalize_timestamp(
            self.created_at,
            name="created_at",
            required=True,
            violations=violations,
        )

        updated_at = _normalize_timestamp(
            self.updated_at,
            name="updated_at",
            required=True,
            violations=violations,
        )

        started_at = _normalize_timestamp(
            self.started_at,
            name="started_at",
            required=False,
            violations=violations,
        )

        completed_at = _normalize_timestamp(
            self.completed_at,
            name="completed_at",
            required=False,
            violations=violations,
        )

        failed_at = _normalize_timestamp(
            self.failed_at,
            name="failed_at",
            required=False,
            violations=violations,
        )

        cancelled_at = _normalize_timestamp(
            self.cancelled_at,
            name="cancelled_at",
            required=False,
            violations=violations,
        )

        contract_version = _require_nonempty_string(
            self.contract_version,
            name="contract_version",
            violations=violations,
        )

        if contract_version != UNIVERSAL_WORKFLOW_CONTRACT_VERSION:
            violations.append(
                "contract_version must be "
                + UNIVERSAL_WORKFLOW_CONTRACT_VERSION
            )

        # ------------------------------------------------------------------
        # Cross-field invariants
        # ------------------------------------------------------------------

        if parent_workflow_id is None:
            if root_workflow_id != workflow_id:
                violations.append(
                    "a root workflow must have root_workflow_id equal to workflow_id"
                )
        else:
            if parent_workflow_id == workflow_id:
                violations.append(
                    "parent_workflow_id cannot equal workflow_id"
                )

        stage_sets = {
            "completed": set(completed_stages),
            "pending": set(pending_stages),
            "failed": set(failed_stages),
            "skipped": set(skipped_stages),
        }

        names = tuple(stage_sets)

        for index, left_name in enumerate(names):
            for right_name in names[index + 1:]:
                overlap = (
                    stage_sets[left_name]
                    & stage_sets[right_name]
                )

                if overlap:
                    violations.append(
                        f"stages cannot be both {left_name} and "
                        f"{right_name}: {', '.join(sorted(overlap))}"
                    )

        if (
            current_stage is not None
            and current_stage in set(completed_stages)
        ):
            violations.append(
                "current_stage cannot already be completed"
            )

        if (
            current_stage is not None
            and current_stage in set(failed_stages)
        ):
            violations.append(
                "current_stage cannot already be failed"
            )

        if (
            status == UniversalWorkflowStatus.COMPLETED
            and completed_at is None
        ):
            violations.append(
                "completed_at is required when status is COMPLETED"
            )

        if (
            status == UniversalWorkflowStatus.FAILED
            and failed_at is None
        ):
            violations.append(
                "failed_at is required when status is FAILED"
            )

        if (
            status == UniversalWorkflowStatus.CANCELLED
            and cancelled_at is None
        ):
            violations.append(
                "cancelled_at is required when status is CANCELLED"
            )

        if (
            status == UniversalWorkflowStatus.FAILED
            and failure_code is None
        ):
            violations.append(
                "failure_code is required when status is FAILED"
            )

        if (
            status == UniversalWorkflowStatus.COMPLETED
            and failed_stages
        ):
            violations.append(
                "COMPLETED workflow cannot contain failed_stages"
            )

        if (
            created_at is not None
            and updated_at is not None
        ):
            created_dt = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            )
            updated_dt = datetime.fromisoformat(
                updated_at.replace("Z", "+00:00")
            )

            if updated_dt < created_dt:
                violations.append(
                    "updated_at cannot be earlier than created_at"
                )

        if violations:
            raise UniversalWorkflowContractError(
                "Universal Workflow Contract validation failed",
                violations=tuple(violations),
            )

        object.__setattr__(self, "workflow_id", workflow_id)
        object.__setattr__(self, "workflow_type", workflow_type)
        object.__setattr__(self, "workflow_version", workflow_version)
        object.__setattr__(self, "workspace_id", workspace_id)
        object.__setattr__(self, "coordinator_id", coordinator_id)
        object.__setattr__(self, "coordinator_version", coordinator_version)
        object.__setattr__(self, "correlation_id", correlation_id)
        object.__setattr__(self, "parent_workflow_id", parent_workflow_id)
        object.__setattr__(self, "root_workflow_id", root_workflow_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "input_reference", input_reference)
        object.__setattr__(self, "context", context)
        object.__setattr__(self, "metadata", metadata)
        object.__setattr__(self, "current_stage", current_stage)
        object.__setattr__(self, "completed_stages", completed_stages)
        object.__setattr__(self, "pending_stages", pending_stages)
        object.__setattr__(self, "failed_stages", failed_stages)
        object.__setattr__(self, "skipped_stages", skipped_stages)
        object.__setattr__(self, "result_reference", result_reference)
        object.__setattr__(self, "artifact_references", artifact_references)
        object.__setattr__(self, "idempotency_key", idempotency_key)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "started_at", started_at)
        object.__setattr__(self, "updated_at", updated_at)
        object.__setattr__(self, "completed_at", completed_at)
        object.__setattr__(self, "failed_at", failed_at)
        object.__setattr__(self, "cancelled_at", cancelled_at)
        object.__setattr__(self, "failure_code", failure_code)
        object.__setattr__(self, "failure_message", failure_message)
        object.__setattr__(self, "failure_details", failure_details)
        object.__setattr__(self, "contract_version", contract_version)

    # ======================================================================
    # Serialization
    # ======================================================================

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "workflow_version": self.workflow_version,
            "workspace_id": self.workspace_id,
            "coordinator_id": self.coordinator_id,
            "coordinator_version": self.coordinator_version,
            "correlation_id": self.correlation_id,
            "parent_workflow_id": self.parent_workflow_id,
            "root_workflow_id": self.root_workflow_id,
            "status": self.status.value,
            "input_reference": self.input_reference,
            "context": _thaw(self.context),
            "metadata": _thaw(self.metadata),
            "current_stage": self.current_stage,
            "completed_stages": list(self.completed_stages),
            "pending_stages": list(self.pending_stages),
            "failed_stages": list(self.failed_stages),
            "skipped_stages": list(self.skipped_stages),
            "result_reference": self.result_reference,
            "artifact_references": list(self.artifact_references),
            "idempotency_key": self.idempotency_key,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "failed_at": self.failed_at,
            "cancelled_at": self.cancelled_at,
            "failure_code": self.failure_code,
            "failure_message": self.failure_message,
            "failure_details": _thaw(self.failure_details),
            "contract_version": self.contract_version,
        }

    def to_dict(self) -> dict[str, Any]:
        return self.to_canonical_dict()

    def to_canonical_json(self) -> str:
        return _canonical_json(
            self.to_canonical_dict()
        )

    # ======================================================================
    # Schema
    # ======================================================================

    @classmethod
    def required_fields(cls) -> Tuple[str, ...]:
        return REQUIRED_UNIVERSAL_WORKFLOW_FIELDS

    @classmethod
    def schema(cls) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "contract_id": UNIVERSAL_WORKFLOW_CONTRACT_ID,
                "contract_version": UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
                "schema_version": UNIVERSAL_WORKFLOW_SCHEMA_VERSION,
                "required_fields": REQUIRED_UNIVERSAL_WORKFLOW_FIELDS,
            }
        )

    # ======================================================================
    # Reconstruction
    # ======================================================================

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "UniversalWorkflow":
        if not isinstance(data, Mapping):
            raise UniversalWorkflowContractError(
                "workflow data must be a mapping"
            )

        unknown_fields = sorted(
            set(data) - _CONTRACT_CONSTRUCTOR_FIELDS
        )

        if unknown_fields:
            raise UniversalWorkflowContractError(
                "unknown universal workflow fields: "
                + ", ".join(unknown_fields),
                violations=tuple(
                    "unknown field: " + name
                    for name in unknown_fields
                ),
            )

        missing_fields = tuple(
            name
            for name in REQUIRED_UNIVERSAL_WORKFLOW_FIELDS
            if name not in data
        )

        if missing_fields:
            raise UniversalWorkflowContractError(
                "missing required universal workflow fields: "
                + ", ".join(missing_fields),
                violations=tuple(
                    "missing required field: " + name
                    for name in missing_fields
                ),
            )

        kwargs = dict(data)

        kwargs["status"] = UniversalWorkflowStatus.coerce(
            kwargs["status"]
        )

        return cls(**kwargs)

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "UniversalWorkflow":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise UniversalWorkflowContractError(
                "workflow json is not decodable: "
                + str(exc)
            ) from exc

        return cls.from_dict(data)

    @classmethod
    def reconstruct(
        cls,
        data: Mapping[str, Any],
    ) -> "UniversalWorkflow":
        return cls.from_dict(data)

    # ======================================================================
    # Identity / evidence
    # ======================================================================

    def identity_fingerprint(self) -> str:
        material = {
            "contract_id": UNIVERSAL_WORKFLOW_CONTRACT_ID,
            "contract_version": self.contract_version,
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "workflow_version": self.workflow_version,
            "workspace_id": self.workspace_id,
            "root_workflow_id": self.root_workflow_id,
            "correlation_id": self.correlation_id,
        }

        return _fingerprint(
            _canonical_json(material)
        )

    def content_fingerprint(self) -> str:
        return _fingerprint(
            self.to_canonical_json()
        )

    def validate(self) -> UniversalWorkflowValidationReport:
        return validate_universal_workflow(self)


_CONTRACT_CONSTRUCTOR_FIELDS: Final[frozenset[str]] = frozenset(
    item.name
    for item in fields(UniversalWorkflow)
)


# ============================================================================
# 9. Standalone validation
# ============================================================================

def validate_universal_workflow(
    candidate: Any,
) -> UniversalWorkflowValidationReport:

    if isinstance(candidate, UniversalWorkflow):
        return UniversalWorkflowValidationReport(
            is_valid=True,
            violations=_EMPTY_TUPLE,
            contract_version=candidate.contract_version,
            checked_field_count=len(
                REQUIRED_UNIVERSAL_WORKFLOW_FIELDS
            ),
        )

    if not isinstance(candidate, Mapping):
        return UniversalWorkflowValidationReport(
            is_valid=False,
            violations=(
                "candidate must be a UniversalWorkflow or mapping",
            ),
            checked_field_count=0,
        )

    try:
        reconstructed = UniversalWorkflow.from_dict(candidate)
    except UniversalWorkflowContractError as exc:
        return UniversalWorkflowValidationReport(
            is_valid=False,
            violations=(
                tuple(exc.violations)
                or (str(exc),)
            ),
            checked_field_count=len(
                REQUIRED_UNIVERSAL_WORKFLOW_FIELDS
            ),
        )

    return UniversalWorkflowValidationReport(
        is_valid=True,
        violations=_EMPTY_TUPLE,
        contract_version=reconstructed.contract_version,
        checked_field_count=len(
            REQUIRED_UNIVERSAL_WORKFLOW_FIELDS
        ),
    )


__all__ = [
    "UNIVERSAL_WORKFLOW_CONTRACT_ID",
    "UNIVERSAL_WORKFLOW_CONTRACT_VERSION",
    "UNIVERSAL_WORKFLOW_SCHEMA_VERSION",
    "REQUIRED_UNIVERSAL_WORKFLOW_FIELDS",
    "TERMINAL_WORKFLOW_STATUSES",
    "UniversalWorkflow",
    "UniversalWorkflowStatus",
    "UniversalWorkflowValidationReport",
    "UniversalWorkflowContractError",
    "validate_universal_workflow",
]
