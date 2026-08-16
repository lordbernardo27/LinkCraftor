"""
LinkCraftor Universal Stage Reference Contract
==============================================

Canonical immutable reference describing one workflow stage.

A UniversalStageReference identifies a stage for the Universal
Coordination Framework without importing or embedding the stage's
handler or business implementation.

Authority boundaries
--------------------
This contract owns:
- coordination-stage identity;
- pipeline identity;
- workflow identity;
- execution-target declaration;
- Universal Runtime job type reference;
- Runtime Registration stage identity;
- required payload field declaration.

This contract does NOT own:
- handler functions;
- handler imports;
- Runtime Registration;
- runtime dispatch;
- retry policies;
- concurrency policies;
- idempotency policies;
- queues;
- workers;
- stage business logic;
- dependency graph authority.

For Universal Runtime-backed stages, ``job_type`` is the stable
lookup key used to resolve the corresponding Runtime Registration.
"""

from __future__ import annotations

import enum
import hashlib
import json
import re
from dataclasses import dataclass, field, fields
from types import MappingProxyType
from typing import Any, Final, Mapping, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)


# ============================================================================
# 1. Contract identity
# ============================================================================

UNIVERSAL_STAGE_REFERENCE_CONTRACT_ID: Final[str] = (
    "urn:linkcraftor:coordination:universal-stage-reference-contract"
)

UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION: Final[str] = (
    "universal_stage_reference_contract_v1.3.0"
)

UNIVERSAL_STAGE_REFERENCE_SCHEMA_VERSION: Final[str] = (
    "universal_stage_reference_schema_v1"
)


# ============================================================================
# 2. Name rules
# ============================================================================

_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
)


# ============================================================================
# 3. Execution target
# ============================================================================

class StageExecutionTarget(str, enum.Enum):
    """
    Declares where execution responsibility belongs.

    UNIVERSAL_RUNTIME:
        Execution must resolve through Universal Runtime /
        Runtime Registration.

    COORDINATION_ONLY:
        The reference represents a coordination operation that does
        not dispatch a Universal Runtime business-stage job.

    The second value is reserved so the contract can represent future
    coordination-only workflow nodes without pretending they are
    runtime business stages.
    """

    UNIVERSAL_RUNTIME = "universal_runtime"
    COORDINATION_ONLY = "coordination_only"

    @classmethod
    def coerce(
        cls,
        value: Any,
    ) -> "StageExecutionTarget":

        if isinstance(value, cls):
            return value

        if not isinstance(value, str):
            raise UniversalStageReferenceContractError(
                "execution_target must be a string or StageExecutionTarget"
            )

        normalized = value.strip().lower()

        try:
            return cls(normalized)
        except ValueError as exc:
            raise UniversalStageReferenceContractError(
                f"unsupported execution_target: {value!r}"
            ) from exc


# ============================================================================
# 4. Required fields
# ============================================================================

REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS: Final[
    Tuple[str, ...]
] = (
    "stage_id",
    "stage_version",
    "pipeline_id",
    "workflow_type",
    "workflow_contract_version",
    "execution_target",
    "job_type",
    "runtime_stage",
    "required_payload_fields",
    "metadata",
    "contract_version",
)


# ============================================================================
# 5. Error
# ============================================================================

class UniversalStageReferenceContractError(ValueError):
    """Raised when a Universal Stage Reference is invalid."""

    def __init__(
        self,
        message: str,
        *,
        violations: Tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.violations = tuple(violations)


# ============================================================================
# 6. Immutable helpers
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
        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(value, tuple):
        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(value, (set, frozenset)):
        return tuple(
            sorted(
                (
                    _freeze(item)
                    for item in value
                ),
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
        return [
            _thaw(item)
            for item in value
        ]

    return value


def _require_name(
    value: Any,
    *,
    name: str,
    violations: list[str],
    allow_empty: bool = False,
) -> str:

    if not isinstance(value, str):
        violations.append(
            f"{name} must be a string"
        )
        return ""

    normalized = value.strip()

    if not normalized:

        if not allow_empty:
            violations.append(
                f"{name} must be non-empty"
            )

        return ""

    if not _NAME_PATTERN.fullmatch(
        normalized
    ):
        violations.append(
            f"{name} contains unsupported characters"
        )

    return normalized


def _normalize_string_tuple(
    value: Any,
    *,
    name: str,
    violations: list[str],
) -> Tuple[str, ...]:

    if isinstance(value, str) or not isinstance(
        value,
        (list, tuple, set, frozenset),
    ):
        violations.append(
            f"{name} must be a collection of strings"
        )
        return ()

    result: list[str] = []

    for index, item in enumerate(value):

        normalized = _require_name(
            item,
            name=f"{name}[{index}]",
            violations=violations,
        )

        if (
            normalized
            and normalized not in result
        ):
            result.append(normalized)

    return tuple(result)


def _normalize_mapping(
    value: Any,
    *,
    name: str,
    violations: list[str],
) -> Mapping[str, Any]:

    if value is None:
        return _EMPTY_MAPPING

    if not isinstance(value, Mapping):
        violations.append(
            f"{name} must be a mapping"
        )
        return _EMPTY_MAPPING

    return _freeze(value)


def _canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _fingerprint(
    text: str,
) -> str:

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ============================================================================
# 7. Validation report
# ============================================================================

@dataclass(frozen=True, slots=True)
class UniversalStageReferenceValidationReport:

    is_valid: bool
    violations: Tuple[str, ...] = ()

    contract_version: str = (
        UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
    )

    checked_field_count: int = 0

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "is_valid": self.is_valid,
            "violations": list(
                self.violations
            ),
            "contract_version": (
                self.contract_version
            ),
            "checked_field_count": (
                self.checked_field_count
            ),
        }


# ============================================================================
# 8. Universal Stage Reference
# ============================================================================

@dataclass(frozen=True, slots=True)
class UniversalStageReference:
    """
    Immutable coordination reference for one workflow stage.

    ``stage_id`` is the coordination identity.

    ``runtime_stage`` is the stage identity expected in the
    corresponding Runtime Registration.

    ``job_type`` is the Universal Runtime Registration lookup /
    dispatch key for UNIVERSAL_RUNTIME stages.
    """

    stage_id: str
    stage_version: str

    pipeline_id: str
    workflow_type: str
    workflow_contract_version: str

    execution_target: StageExecutionTarget

    job_type: str
    runtime_stage: str

    required_payload_fields: Tuple[str, ...]

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    contract_version: str = (
        UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        violations: list[str] = []

        stage_id = _require_name(
            self.stage_id,
            name="stage_id",
            violations=violations,
        )

        stage_version = _require_name(
            self.stage_version,
            name="stage_version",
            violations=violations,
        )

        pipeline_id = _require_name(
            self.pipeline_id,
            name="pipeline_id",
            violations=violations,
        )

        workflow_type = _require_name(
            self.workflow_type,
            name="workflow_type",
            violations=violations,
        )

        workflow_contract_version = (
            _require_name(
                self.workflow_contract_version,
                name="workflow_contract_version",
                violations=violations,
            )
        )

        try:
            execution_target = (
                StageExecutionTarget.coerce(
                    self.execution_target
                )
            )
        except UniversalStageReferenceContractError as exc:

            violations.extend(
                exc.violations
                or (str(exc),)
            )

            execution_target = (
                StageExecutionTarget.UNIVERSAL_RUNTIME
            )

        job_type = _require_name(
            self.job_type,
            name="job_type",
            violations=violations,
            allow_empty=True,
        )

        runtime_stage = _require_name(
            self.runtime_stage,
            name="runtime_stage",
            violations=violations,
            allow_empty=True,
        )

        required_payload_fields = (
            _normalize_string_tuple(
                self.required_payload_fields,
                name="required_payload_fields",
                violations=violations,
            )
        )

        metadata = _normalize_mapping(
            self.metadata,
            name="metadata",
            violations=violations,
        )

        contract_version = _require_name(
            self.contract_version,
            name="contract_version",
            violations=violations,
        )

        # ------------------------------------------------------------------
        # Contract compatibility
        # ------------------------------------------------------------------

        if (
            workflow_contract_version
            != UNIVERSAL_WORKFLOW_CONTRACT_VERSION
        ):
            violations.append(
                "workflow_contract_version must be "
                + UNIVERSAL_WORKFLOW_CONTRACT_VERSION
            )

        if (
            contract_version
            != UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
        ):
            violations.append(
                "contract_version must be "
                + UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
            )

        # ------------------------------------------------------------------
        # Execution-target invariants
        # ------------------------------------------------------------------

        if (
            execution_target
            == StageExecutionTarget.UNIVERSAL_RUNTIME
        ):

            if not job_type:
                violations.append(
                    "job_type is required when "
                    "execution_target is universal_runtime"
                )

            if not runtime_stage:
                violations.append(
                    "runtime_stage is required when "
                    "execution_target is universal_runtime"
                )

        if (
            execution_target
            == StageExecutionTarget.COORDINATION_ONLY
        ):

            if job_type:
                violations.append(
                    "job_type must be empty when "
                    "execution_target is coordination_only"
                )

            if runtime_stage:
                violations.append(
                    "runtime_stage must be empty when "
                    "execution_target is coordination_only"
                )

            if required_payload_fields:
                violations.append(
                    "required_payload_fields must be empty when "
                    "execution_target is coordination_only"
                )

        if violations:
            raise UniversalStageReferenceContractError(
                "Universal Stage Reference validation failed",
                violations=tuple(
                    violations
                ),
            )

        object.__setattr__(
            self,
            "stage_id",
            stage_id,
        )

        object.__setattr__(
            self,
            "stage_version",
            stage_version,
        )

        object.__setattr__(
            self,
            "pipeline_id",
            pipeline_id,
        )

        object.__setattr__(
            self,
            "workflow_type",
            workflow_type,
        )

        object.__setattr__(
            self,
            "workflow_contract_version",
            workflow_contract_version,
        )

        object.__setattr__(
            self,
            "execution_target",
            execution_target,
        )

        object.__setattr__(
            self,
            "job_type",
            job_type,
        )

        object.__setattr__(
            self,
            "runtime_stage",
            runtime_stage,
        )

        object.__setattr__(
            self,
            "required_payload_fields",
            required_payload_fields,
        )

        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

        object.__setattr__(
            self,
            "contract_version",
            contract_version,
        )

    # ======================================================================
    # Runtime properties
    # ======================================================================

    @property
    def uses_universal_runtime(
        self,
    ) -> bool:

        return (
            self.execution_target
            == StageExecutionTarget.UNIVERSAL_RUNTIME
        )

    @property
    def is_coordination_only(
        self,
    ) -> bool:

        return (
            self.execution_target
            == StageExecutionTarget.COORDINATION_ONLY
        )

    @property
    def runtime_lookup_key(
        self,
    ) -> str | None:
        """
        Return the Universal Runtime Registration lookup key.

        Runtime Registration is keyed by job_type.
        """

        if not self.uses_universal_runtime:
            return None

        return self.job_type

    # ======================================================================
    # Serialization
    # ======================================================================

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "stage_id": self.stage_id,
            "stage_version": self.stage_version,
            "pipeline_id": self.pipeline_id,
            "workflow_type": self.workflow_type,
            "workflow_contract_version": (
                self.workflow_contract_version
            ),
            "execution_target": (
                self.execution_target.value
            ),
            "job_type": self.job_type,
            "runtime_stage": self.runtime_stage,
            "required_payload_fields": list(
                self.required_payload_fields
            ),
            "metadata": _thaw(
                self.metadata
            ),
            "contract_version": (
                self.contract_version
            ),
        }

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return self.to_canonical_dict()

    def to_canonical_json(
        self,
    ) -> str:

        return _canonical_json(
            self.to_canonical_dict()
        )

    # ======================================================================
    # Schema
    # ======================================================================

    @classmethod
    def required_fields(
        cls,
    ) -> Tuple[str, ...]:

        return (
            REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS
        )

    @classmethod
    def schema(
        cls,
    ) -> Mapping[str, Any]:

        return MappingProxyType(
            {
                "contract_id": (
                    UNIVERSAL_STAGE_REFERENCE_CONTRACT_ID
                ),
                "contract_version": (
                    UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
                ),
                "schema_version": (
                    UNIVERSAL_STAGE_REFERENCE_SCHEMA_VERSION
                ),
                "workflow_contract_version": (
                    UNIVERSAL_WORKFLOW_CONTRACT_VERSION
                ),
                "required_fields": (
                    REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS
                ),
                "execution_targets": tuple(
                    target.value
                    for target
                    in StageExecutionTarget
                ),
                "runtime_lookup_authority": (
                    "job_type"
                ),
            }
        )

    # ======================================================================
    # Reconstruction
    # ======================================================================

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "UniversalStageReference":

        if not isinstance(
            data,
            Mapping,
        ):
            raise UniversalStageReferenceContractError(
                "stage reference data must be a mapping"
            )

        unknown_fields = sorted(
            set(data)
            - _CONTRACT_CONSTRUCTOR_FIELDS
        )

        if unknown_fields:
            raise UniversalStageReferenceContractError(
                "unknown Universal Stage Reference fields: "
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
            for name
            in REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS
            if name not in data
        )

        if missing_fields:
            raise UniversalStageReferenceContractError(
                "missing required Universal Stage Reference fields: "
                + ", ".join(
                    missing_fields
                ),
                violations=tuple(
                    "missing required field: " + name
                    for name in missing_fields
                ),
            )

        kwargs = dict(
            data
        )

        kwargs["execution_target"] = (
            StageExecutionTarget.coerce(
                kwargs[
                    "execution_target"
                ]
            )
        )

        return cls(
            **kwargs
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "UniversalStageReference":

        try:
            data = json.loads(
                text
            )

        except json.JSONDecodeError as exc:
            raise UniversalStageReferenceContractError(
                "stage reference json is not decodable: "
                + str(exc)
            ) from exc

        return cls.from_dict(
            data
        )

    @classmethod
    def reconstruct(
        cls,
        data: Mapping[str, Any],
    ) -> "UniversalStageReference":

        return cls.from_dict(
            data
        )

    # ======================================================================
    # Fingerprints
    # ======================================================================

    def identity_fingerprint(
        self,
    ) -> str:

        material = {
            "contract_id": (
                UNIVERSAL_STAGE_REFERENCE_CONTRACT_ID
            ),
            "contract_version": (
                self.contract_version
            ),
            "stage_id": self.stage_id,
            "stage_version": (
                self.stage_version
            ),
            "pipeline_id": (
                self.pipeline_id
            ),
            "workflow_type": (
                self.workflow_type
            ),
            "execution_target": (
                self.execution_target.value
            ),
            "job_type": (
                self.job_type
            ),
            "runtime_stage": (
                self.runtime_stage
            ),
        }

        return _fingerprint(
            _canonical_json(
                material
            )
        )

    def content_fingerprint(
        self,
    ) -> str:

        return _fingerprint(
            self.to_canonical_json()
        )

    def validate(
        self,
    ) -> "UniversalStageReferenceValidationReport":

        return validate_universal_stage_reference(
            self
        )


_CONTRACT_CONSTRUCTOR_FIELDS: Final[
    frozenset[str]
] = frozenset(
    item.name
    for item in fields(
        UniversalStageReference
    )
)


# ============================================================================
# 9. Standalone validation
# ============================================================================

def validate_universal_stage_reference(
    candidate: Any,
) -> UniversalStageReferenceValidationReport:

    if isinstance(
        candidate,
        UniversalStageReference,
    ):

        return UniversalStageReferenceValidationReport(
            is_valid=True,
            violations=_EMPTY_TUPLE,
            contract_version=(
                candidate.contract_version
            ),
            checked_field_count=len(
                REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS
            ),
        )

    if not isinstance(
        candidate,
        Mapping,
    ):

        return UniversalStageReferenceValidationReport(
            is_valid=False,
            violations=(
                "candidate must be a UniversalStageReference "
                "or mapping",
            ),
            checked_field_count=0,
        )

    try:
        reconstructed = (
            UniversalStageReference.from_dict(
                candidate
            )
        )

    except UniversalStageReferenceContractError as exc:

        return UniversalStageReferenceValidationReport(
            is_valid=False,
            violations=(
                tuple(
                    exc.violations
                )
                or (
                    str(exc),
                )
            ),
            checked_field_count=len(
                REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS
            ),
        )

    return UniversalStageReferenceValidationReport(
        is_valid=True,
        violations=_EMPTY_TUPLE,
        contract_version=(
            reconstructed.contract_version
        ),
        checked_field_count=len(
            REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS
        ),
    )


__all__ = [
    "UNIVERSAL_STAGE_REFERENCE_CONTRACT_ID",
    "UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION",
    "UNIVERSAL_STAGE_REFERENCE_SCHEMA_VERSION",
    "REQUIRED_UNIVERSAL_STAGE_REFERENCE_FIELDS",
    "StageExecutionTarget",
    "UniversalStageReference",
    "UniversalStageReferenceValidationReport",
    "UniversalStageReferenceContractError",
    "validate_universal_stage_reference",
]
