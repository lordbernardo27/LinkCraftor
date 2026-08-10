"""
LinkCraftor Pipeline Coordinator Contract
=========================================

Canonical immutable declaration for one pipeline coordinator.

The contract describes coordinator identity, workflow ownership,
capabilities, entrypoint, and Universal Runtime integration policy.

It does not execute pipeline stages.
"""

from __future__ import annotations

import enum
import hashlib
import json
from dataclasses import dataclass, field, fields
from types import MappingProxyType
from typing import Any, Final, Mapping, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)


PIPELINE_COORDINATOR_CONTRACT_ID: Final[str] = (
    "urn:linkcraftor:coordination:pipeline-coordinator-contract"
)

PIPELINE_COORDINATOR_CONTRACT_VERSION: Final[str] = (
    "pipeline_coordinator_contract_v1.2.0"
)

PIPELINE_COORDINATOR_SCHEMA_VERSION: Final[str] = (
    "pipeline_coordinator_schema_v1"
)


class PipelineCoordinatorContractError(ValueError):
    """Raised when a Pipeline Coordinator contract is invalid."""

    def __init__(
        self,
        message: str,
        *,
        violations: Tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.violations = tuple(violations)


class CoordinatorExecutionModel(str, enum.Enum):
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"

    @classmethod
    def coerce(cls, value: Any) -> "CoordinatorExecutionModel":
        if isinstance(value, cls):
            return value

        if not isinstance(value, str):
            raise PipelineCoordinatorContractError(
                "execution_model must be a string"
            )

        try:
            return cls(value.strip().lower())
        except ValueError as exc:
            raise PipelineCoordinatorContractError(
                f"unsupported execution_model: {value!r}"
            ) from exc


class CoordinatorRuntimePolicy(str, enum.Enum):
    UNIVERSAL_RUNTIME_REQUIRED = "universal_runtime_required"
    TRANSITIONAL_DIRECT_EXECUTION = "transitional_direct_execution"
    NO_RUNTIME_EXECUTION = "no_runtime_execution"

    @classmethod
    def coerce(cls, value: Any) -> "CoordinatorRuntimePolicy":
        if isinstance(value, cls):
            return value

        if not isinstance(value, str):
            raise PipelineCoordinatorContractError(
                "runtime_policy must be a string"
            )

        try:
            return cls(value.strip().lower())
        except ValueError as exc:
            raise PipelineCoordinatorContractError(
                f"unsupported runtime_policy: {value!r}"
            ) from exc


CANONICAL_COORDINATOR_CAPABILITIES: Final[frozenset[str]] = frozenset(
    {
        "start",
        "advance",
        "stage_completed",
        "stage_failed",
        "pause",
        "resume",
        "cancel",
        "recover",
        "inspect",
    }
)

REQUIRED_COORDINATOR_CAPABILITIES: Final[frozenset[str]] = frozenset(
    {
        "start",
    }
)


REQUIRED_PIPELINE_COORDINATOR_FIELDS: Final[Tuple[str, ...]] = (
    "coordinator_id",
    "coordinator_version",
    "workflow_type",
    "workflow_version",
    "workflow_contract_version",
    "entrypoint",
    "execution_model",
    "runtime_policy",
    "capabilities",
    "stage_job_types",
    "responsibilities",
    "excluded_responsibilities",
    "metadata",
    "contract_version",
)


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
        return [
            _thaw(item)
            for item in value
        ]

    return value


def _require_string(
    value: Any,
    *,
    name: str,
    violations: list[str],
) -> str:
    if not isinstance(value, str):
        violations.append(
            f"{name} must be a string"
        )
        return ""

    value = value.strip()

    if not value:
        violations.append(
            f"{name} must be non-empty"
        )

    return value


def _string_tuple(
    value: Any,
    *,
    name: str,
    violations: list[str],
    allow_empty: bool = True,
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

        if item not in result:
            result.append(item)

    if not allow_empty and not result:
        violations.append(
            f"{name} must contain at least one entry"
        )

    return tuple(result)


def _mapping(
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


@dataclass(frozen=True, slots=True)
class PipelineCoordinatorValidationReport:
    is_valid: bool
    violations: Tuple[str, ...] = ()
    contract_version: str = PIPELINE_COORDINATOR_CONTRACT_VERSION
    checked_field_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "violations": list(self.violations),
            "contract_version": self.contract_version,
            "checked_field_count": self.checked_field_count,
        }


@dataclass(frozen=True, slots=True)
class PipelineCoordinatorContract:

    coordinator_id: str
    coordinator_version: str

    workflow_type: str
    workflow_version: str
    workflow_contract_version: str

    entrypoint: str

    execution_model: CoordinatorExecutionModel
    runtime_policy: CoordinatorRuntimePolicy

    capabilities: Tuple[str, ...]
    stage_job_types: Tuple[str, ...]

    responsibilities: Tuple[str, ...]
    excluded_responsibilities: Tuple[str, ...]

    metadata: Mapping[str, Any] = field(default_factory=dict)

    contract_version: str = PIPELINE_COORDINATOR_CONTRACT_VERSION

    def __post_init__(self) -> None:
        violations: list[str] = []

        coordinator_id = _require_string(
            self.coordinator_id,
            name="coordinator_id",
            violations=violations,
        )

        coordinator_version = _require_string(
            self.coordinator_version,
            name="coordinator_version",
            violations=violations,
        )

        workflow_type = _require_string(
            self.workflow_type,
            name="workflow_type",
            violations=violations,
        )

        workflow_version = _require_string(
            self.workflow_version,
            name="workflow_version",
            violations=violations,
        )

        workflow_contract_version = _require_string(
            self.workflow_contract_version,
            name="workflow_contract_version",
            violations=violations,
        )

        entrypoint = _require_string(
            self.entrypoint,
            name="entrypoint",
            violations=violations,
        )

        try:
            execution_model = CoordinatorExecutionModel.coerce(
                self.execution_model
            )
        except PipelineCoordinatorContractError as exc:
            violations.extend(
                exc.violations or (str(exc),)
            )
            execution_model = CoordinatorExecutionModel.SYNCHRONOUS

        try:
            runtime_policy = CoordinatorRuntimePolicy.coerce(
                self.runtime_policy
            )
        except PipelineCoordinatorContractError as exc:
            violations.extend(
                exc.violations or (str(exc),)
            )
            runtime_policy = (
                CoordinatorRuntimePolicy.UNIVERSAL_RUNTIME_REQUIRED
            )

        capabilities = _string_tuple(
            self.capabilities,
            name="capabilities",
            violations=violations,
            allow_empty=False,
        )

        stage_job_types = _string_tuple(
            self.stage_job_types,
            name="stage_job_types",
            violations=violations,
        )

        responsibilities = _string_tuple(
            self.responsibilities,
            name="responsibilities",
            violations=violations,
            allow_empty=False,
        )

        excluded_responsibilities = _string_tuple(
            self.excluded_responsibilities,
            name="excluded_responsibilities",
            violations=violations,
        )

        metadata = _mapping(
            self.metadata,
            name="metadata",
            violations=violations,
        )

        contract_version = _require_string(
            self.contract_version,
            name="contract_version",
            violations=violations,
        )

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
            != PIPELINE_COORDINATOR_CONTRACT_VERSION
        ):
            violations.append(
                "contract_version must be "
                + PIPELINE_COORDINATOR_CONTRACT_VERSION
            )

        unsupported = sorted(
            set(capabilities)
            - CANONICAL_COORDINATOR_CAPABILITIES
        )

        if unsupported:
            violations.append(
                "unsupported coordinator capabilities: "
                + ", ".join(unsupported)
            )

        missing = sorted(
            REQUIRED_COORDINATOR_CAPABILITIES
            - set(capabilities)
        )

        if missing:
            violations.append(
                "missing required coordinator capabilities: "
                + ", ".join(missing)
            )

        if ":" not in entrypoint:
            violations.append(
                "entrypoint must use module.path:function_name format"
            )
        else:
            module_name, function_name = entrypoint.rsplit(":", 1)

            if not module_name.strip():
                violations.append(
                    "entrypoint module path must be non-empty"
                )

            if not function_name.strip():
                violations.append(
                    "entrypoint function name must be non-empty"
                )

        if (
            runtime_policy
            == CoordinatorRuntimePolicy.UNIVERSAL_RUNTIME_REQUIRED
            and not stage_job_types
        ):
            violations.append(
                "stage_job_types must not be empty when "
                "runtime_policy is universal_runtime_required"
            )

        if (
            runtime_policy
            == CoordinatorRuntimePolicy.NO_RUNTIME_EXECUTION
            and stage_job_types
        ):
            violations.append(
                "stage_job_types must be empty when "
                "runtime_policy is no_runtime_execution"
            )

        overlap = (
            set(responsibilities)
            & set(excluded_responsibilities)
        )

        if overlap:
            violations.append(
                "responsibilities and excluded_responsibilities "
                "cannot overlap: "
                + ", ".join(sorted(overlap))
            )

        if violations:
            raise PipelineCoordinatorContractError(
                "Pipeline Coordinator Contract validation failed",
                violations=tuple(violations),
            )

        object.__setattr__(
            self,
            "coordinator_id",
            coordinator_id,
        )

        object.__setattr__(
            self,
            "coordinator_version",
            coordinator_version,
        )

        object.__setattr__(
            self,
            "workflow_type",
            workflow_type,
        )

        object.__setattr__(
            self,
            "workflow_version",
            workflow_version,
        )

        object.__setattr__(
            self,
            "workflow_contract_version",
            workflow_contract_version,
        )

        object.__setattr__(
            self,
            "entrypoint",
            entrypoint,
        )

        object.__setattr__(
            self,
            "execution_model",
            execution_model,
        )

        object.__setattr__(
            self,
            "runtime_policy",
            runtime_policy,
        )

        object.__setattr__(
            self,
            "capabilities",
            capabilities,
        )

        object.__setattr__(
            self,
            "stage_job_types",
            stage_job_types,
        )

        object.__setattr__(
            self,
            "responsibilities",
            responsibilities,
        )

        object.__setattr__(
            self,
            "excluded_responsibilities",
            excluded_responsibilities,
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

    def supports(self, capability: str) -> bool:
        return (
            str(capability or "").strip()
            in self.capabilities
        )

    @property
    def uses_universal_runtime(self) -> bool:
        return (
            self.runtime_policy
            == CoordinatorRuntimePolicy.UNIVERSAL_RUNTIME_REQUIRED
        )

    @property
    def is_transitional(self) -> bool:
        return (
            self.runtime_policy
            == CoordinatorRuntimePolicy.TRANSITIONAL_DIRECT_EXECUTION
        )

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "coordinator_id": self.coordinator_id,
            "coordinator_version": self.coordinator_version,
            "workflow_type": self.workflow_type,
            "workflow_version": self.workflow_version,
            "workflow_contract_version": self.workflow_contract_version,
            "entrypoint": self.entrypoint,
            "execution_model": self.execution_model.value,
            "runtime_policy": self.runtime_policy.value,
            "capabilities": list(self.capabilities),
            "stage_job_types": list(self.stage_job_types),
            "responsibilities": list(self.responsibilities),
            "excluded_responsibilities": list(
                self.excluded_responsibilities
            ),
            "metadata": _thaw(self.metadata),
            "contract_version": self.contract_version,
        }

    def to_dict(self) -> dict[str, Any]:
        return self.to_canonical_dict()

    def to_canonical_json(self) -> str:
        return _canonical_json(
            self.to_canonical_dict()
        )

    @classmethod
    def required_fields(cls) -> Tuple[str, ...]:
        return REQUIRED_PIPELINE_COORDINATOR_FIELDS

    @classmethod
    def schema(cls) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "contract_id": PIPELINE_COORDINATOR_CONTRACT_ID,
                "contract_version": PIPELINE_COORDINATOR_CONTRACT_VERSION,
                "schema_version": PIPELINE_COORDINATOR_SCHEMA_VERSION,
                "workflow_contract_version": (
                    UNIVERSAL_WORKFLOW_CONTRACT_VERSION
                ),
                "required_fields": (
                    REQUIRED_PIPELINE_COORDINATOR_FIELDS
                ),
                "canonical_capabilities": tuple(
                    sorted(
                        CANONICAL_COORDINATOR_CAPABILITIES
                    )
                ),
            }
        )

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "PipelineCoordinatorContract":

        if not isinstance(data, Mapping):
            raise PipelineCoordinatorContractError(
                "coordinator contract data must be a mapping"
            )

        unknown_fields = sorted(
            set(data)
            - _CONTRACT_CONSTRUCTOR_FIELDS
        )

        if unknown_fields:
            raise PipelineCoordinatorContractError(
                "unknown pipeline coordinator fields: "
                + ", ".join(unknown_fields),
                violations=tuple(
                    "unknown field: " + name
                    for name in unknown_fields
                ),
            )

        missing_fields = tuple(
            name
            for name in REQUIRED_PIPELINE_COORDINATOR_FIELDS
            if name not in data
        )

        if missing_fields:
            raise PipelineCoordinatorContractError(
                "missing required pipeline coordinator fields: "
                + ", ".join(missing_fields),
                violations=tuple(
                    "missing required field: " + name
                    for name in missing_fields
                ),
            )

        kwargs = dict(data)

        kwargs["execution_model"] = (
            CoordinatorExecutionModel.coerce(
                kwargs["execution_model"]
            )
        )

        kwargs["runtime_policy"] = (
            CoordinatorRuntimePolicy.coerce(
                kwargs["runtime_policy"]
            )
        )

        return cls(**kwargs)

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "PipelineCoordinatorContract":

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise PipelineCoordinatorContractError(
                "coordinator contract json is not decodable: "
                + str(exc)
            ) from exc

        return cls.from_dict(data)

    @classmethod
    def reconstruct(
        cls,
        data: Mapping[str, Any],
    ) -> "PipelineCoordinatorContract":
        return cls.from_dict(data)

    def identity_fingerprint(self) -> str:
        material = {
            "contract_id": PIPELINE_COORDINATOR_CONTRACT_ID,
            "contract_version": self.contract_version,
            "coordinator_id": self.coordinator_id,
            "coordinator_version": self.coordinator_version,
            "workflow_type": self.workflow_type,
            "workflow_version": self.workflow_version,
            "entrypoint": self.entrypoint,
        }

        return _fingerprint(
            _canonical_json(material)
        )

    def content_fingerprint(self) -> str:
        return _fingerprint(
            self.to_canonical_json()
        )

    def validate(
        self,
    ) -> "PipelineCoordinatorValidationReport":
        return validate_pipeline_coordinator_contract(
            self
        )


_CONTRACT_CONSTRUCTOR_FIELDS: Final[frozenset[str]] = frozenset(
    item.name
    for item in fields(
        PipelineCoordinatorContract
    )
)


def validate_pipeline_coordinator_contract(
    candidate: Any,
) -> PipelineCoordinatorValidationReport:

    if isinstance(
        candidate,
        PipelineCoordinatorContract,
    ):
        return PipelineCoordinatorValidationReport(
            is_valid=True,
            violations=_EMPTY_TUPLE,
            contract_version=candidate.contract_version,
            checked_field_count=len(
                REQUIRED_PIPELINE_COORDINATOR_FIELDS
            ),
        )

    if not isinstance(candidate, Mapping):
        return PipelineCoordinatorValidationReport(
            is_valid=False,
            violations=(
                "candidate must be a PipelineCoordinatorContract "
                "or mapping",
            ),
            checked_field_count=0,
        )

    try:
        reconstructed = PipelineCoordinatorContract.from_dict(
            candidate
        )
    except PipelineCoordinatorContractError as exc:
        return PipelineCoordinatorValidationReport(
            is_valid=False,
            violations=tuple(exc.violations) or (str(exc),),
            checked_field_count=len(
                REQUIRED_PIPELINE_COORDINATOR_FIELDS
            ),
        )

    return PipelineCoordinatorValidationReport(
        is_valid=True,
        violations=_EMPTY_TUPLE,
        contract_version=reconstructed.contract_version,
        checked_field_count=len(
            REQUIRED_PIPELINE_COORDINATOR_FIELDS
        ),
    )


__all__ = [
    "PIPELINE_COORDINATOR_CONTRACT_ID",
    "PIPELINE_COORDINATOR_CONTRACT_VERSION",
    "PIPELINE_COORDINATOR_SCHEMA_VERSION",
    "REQUIRED_PIPELINE_COORDINATOR_FIELDS",
    "CANONICAL_COORDINATOR_CAPABILITIES",
    "REQUIRED_COORDINATOR_CAPABILITIES",
    "CoordinatorExecutionModel",
    "CoordinatorRuntimePolicy",
    "PipelineCoordinatorContract",
    "PipelineCoordinatorValidationReport",
    "PipelineCoordinatorContractError",
    "validate_pipeline_coordinator_contract",
]
