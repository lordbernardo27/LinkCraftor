"""
LinkCraftor Universal Stage Result Contract
===========================================

Canonical immutable coordination result for one stage execution.

UniversalStageResult normalizes the outcome of a workflow stage so
the Universal Coordination Framework and pipeline coordinators can
reason about completion, failure, artifacts, and handoff without
interpreting stage-specific business output.

Authority boundaries
--------------------
This contract owns:
- stage-result identity;
- workflow / correlation identity;
- stage identity;
- execution-target identity;
- runtime job correlation;
- terminal stage-result status;
- opaque business output;
- result and artifact references;
- execution timestamps;
- normalized failure information;
- immutable metadata.

This contract does NOT own:
- stage execution;
- handler execution;
- Runtime Registration;
- queue or worker state;
- retry decisions;
- recovery decisions;
- dependency planning;
- next-stage selection;
- business-output interpretation;
- persistence.
"""

from __future__ import annotations

import enum
import hashlib
import json
import re

from dataclasses import (
    dataclass,
    field,
    fields,
)

from datetime import datetime

from types import MappingProxyType

from typing import (
    Any,
    Final,
    Mapping,
    Tuple,
)

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

from backend.server.coordination.universal_stages.contract import (
    UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION,
    StageExecutionTarget,
)


# ============================================================================
# 1. Contract identity
# ============================================================================

UNIVERSAL_STAGE_RESULT_CONTRACT_ID: Final[str] = (
    "urn:linkcraftor:coordination:universal-stage-result-contract"
)

UNIVERSAL_STAGE_RESULT_CONTRACT_VERSION: Final[str] = (
    "universal_stage_result_contract_v1.4.0"
)

UNIVERSAL_STAGE_RESULT_SCHEMA_VERSION: Final[str] = (
    "universal_stage_result_schema_v1"
)


# ============================================================================
# 2. Result status
# ============================================================================

class UniversalStageResultStatus(
    str,
    enum.Enum,
):
    """
    Terminal coordination outcome for one stage attempt.

    COMPLETED
        Stage execution completed successfully.

    FAILED
        Stage execution terminated unsuccessfully.

    SKIPPED
        Coordination deliberately did not execute the stage.

    CANCELLED
        Stage execution / coordination was cancelled.
    """

    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

    @classmethod
    def coerce(
        cls,
        value: Any,
    ) -> "UniversalStageResultStatus":

        if isinstance(
            value,
            cls,
        ):
            return value

        if not isinstance(
            value,
            str,
        ):
            raise UniversalStageResultContractError(
                "status must be a string or "
                "UniversalStageResultStatus"
            )

        normalized = (
            value.strip().lower()
        )

        try:
            return cls(
                normalized
            )

        except ValueError as exc:
            raise UniversalStageResultContractError(
                f"unsupported stage result status: {value!r}"
            ) from exc


# ============================================================================
# 3. Canonical fields
# ============================================================================

REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS: Final[
    Tuple[str, ...]
] = (
    "result_id",
    "workflow_id",
    "correlation_id",
    "stage_id",
    "stage_version",
    "pipeline_id",
    "workflow_type",
    "workspace_id",
    "execution_target",
    "job_id",
    "job_type",
    "status",
    "output",
    "result_reference",
    "artifact_references",
    "started_at",
    "finished_at",
    "failure_code",
    "failure_message",
    "failure_details",
    "metadata",
    "workflow_contract_version",
    "stage_reference_contract_version",
    "contract_version",
)


# ============================================================================
# 4. Validation rules
# ============================================================================

_NAME_PATTERN: Final[
    re.Pattern[str]
] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
)


# ============================================================================
# 5. Error
# ============================================================================

class UniversalStageResultContractError(
    ValueError
):
    """Raised when a Universal Stage Result is invalid."""

    def __init__(
        self,
        message: str,
        *,
        violations: Tuple[str, ...] = (),
    ) -> None:

        super().__init__(
            message
        )

        self.violations = tuple(
            violations
        )


# ============================================================================
# 6. Immutable helpers
# ============================================================================

_EMPTY_MAPPING: Final[
    Mapping[str, Any]
] = MappingProxyType({})

_EMPTY_TUPLE: Final[
    Tuple[str, ...]
] = ()


def _freeze(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):
        return MappingProxyType(
            {
                str(key): _freeze(
                    item
                )
                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(
        value,
        (set, frozenset),
    ):
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


def _thaw(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(key): _thaw(
                item
            )
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        tuple,
    ):
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

    if not isinstance(
        value,
        str,
    ):
        violations.append(
            f"{name} must be a string"
        )
        return ""

    normalized = (
        value.strip()
    )

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


def _require_text(
    value: Any,
    *,
    name: str,
    violations: list[str],
    allow_empty: bool = True,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        violations.append(
            f"{name} must be a string"
        )
        return ""

    normalized = (
        value.strip()
    )

    if (
        not normalized
        and not allow_empty
    ):
        violations.append(
            f"{name} must be non-empty"
        )

    return normalized


def _normalize_mapping(
    value: Any,
    *,
    name: str,
    violations: list[str],
) -> Mapping[str, Any]:

    if value is None:
        return _EMPTY_MAPPING

    if not isinstance(
        value,
        Mapping,
    ):
        violations.append(
            f"{name} must be a mapping"
        )
        return _EMPTY_MAPPING

    return _freeze(
        value
    )


def _normalize_reference_tuple(
    value: Any,
    *,
    name: str,
    violations: list[str],
) -> Tuple[str, ...]:

    if (
        isinstance(value, str)
        or not isinstance(
            value,
            (
                list,
                tuple,
                set,
                frozenset,
            ),
        )
    ):
        violations.append(
            f"{name} must be a collection of strings"
        )
        return ()

    result: list[str] = []

    for index, item in enumerate(
        value
    ):

        if not isinstance(
            item,
            str,
        ):
            violations.append(
                f"{name}[{index}] must be a string"
            )
            continue

        normalized = (
            item.strip()
        )

        if not normalized:
            violations.append(
                f"{name}[{index}] must be non-empty"
            )
            continue

        if normalized not in result:
            result.append(
                normalized
            )

    return tuple(
        result
    )


def _require_timestamp(
    value: Any,
    *,
    name: str,
    violations: list[str],
) -> str:

    if not isinstance(
        value,
        str,
    ):
        violations.append(
            f"{name} must be an ISO-8601 string"
        )
        return ""

    normalized = (
        value.strip()
    )

    if not normalized:
        violations.append(
            f"{name} must be non-empty"
        )
        return ""

    try:
        parsed = datetime.fromisoformat(
            normalized.replace(
                "Z",
                "+00:00",
            )
        )

    except ValueError:
        violations.append(
            f"{name} must be a valid ISO-8601 timestamp"
        )
        return normalized

    if parsed.tzinfo is None:
        violations.append(
            f"{name} must be timezone-aware"
        )

    return normalized


def _timestamp_value(
    value: str,
) -> datetime:

    return datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00",
        )
    )


def _canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


def _fingerprint(
    text: str,
) -> str:

    return hashlib.sha256(
        text.encode(
            "utf-8"
        )
    ).hexdigest()


# ============================================================================
# 7. Validation report
# ============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class UniversalStageResultValidationReport:

    is_valid: bool

    violations: Tuple[
        str,
        ...
    ] = ()

    contract_version: str = (
        UNIVERSAL_STAGE_RESULT_CONTRACT_VERSION
    )

    checked_field_count: int = 0

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "is_valid":
                self.is_valid,

            "violations":
                list(
                    self.violations
                ),

            "contract_version":
                self.contract_version,

            "checked_field_count":
                self.checked_field_count,
        }


# ============================================================================
# 8. Universal Stage Result
# ============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class UniversalStageResult:
    """
    Immutable normalized coordination result for one stage.

    Business-specific results remain opaque inside ``output``.

    ``status`` is the sole canonical coordination success/failure
    authority. A business handler's historical ``ok`` field, if any,
    belongs inside ``output`` and does not override this status.
    """

    result_id: str

    workflow_id: str
    correlation_id: str

    stage_id: str
    stage_version: str

    pipeline_id: str
    workflow_type: str
    workspace_id: str

    execution_target: StageExecutionTarget

    job_id: str
    job_type: str

    status: UniversalStageResultStatus

    output: Mapping[
        str,
        Any,
    ]

    result_reference: str

    artifact_references: Tuple[
        str,
        ...
    ]

    started_at: str
    finished_at: str

    failure_code: str
    failure_message: str

    failure_details: Mapping[
        str,
        Any,
    ]

    metadata: Mapping[
        str,
        Any,
    ]

    workflow_contract_version: str = (
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    )

    stage_reference_contract_version: str = (
        UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
    )

    contract_version: str = (
        UNIVERSAL_STAGE_RESULT_CONTRACT_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        violations: list[str] = []

        result_id = _require_name(
            self.result_id,
            name="result_id",
            violations=violations,
        )

        workflow_id = _require_name(
            self.workflow_id,
            name="workflow_id",
            violations=violations,
        )

        correlation_id = _require_name(
            self.correlation_id,
            name="correlation_id",
            violations=violations,
        )

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

        workspace_id = _require_name(
            self.workspace_id,
            name="workspace_id",
            violations=violations,
        )

        try:
            execution_target = (
                StageExecutionTarget.coerce(
                    self.execution_target
                )
            )

        except Exception as exc:

            violations.append(
                str(exc)
            )

            execution_target = (
                StageExecutionTarget.UNIVERSAL_RUNTIME
            )

        job_id = _require_name(
            self.job_id,
            name="job_id",
            violations=violations,
            allow_empty=True,
        )

        job_type = _require_name(
            self.job_type,
            name="job_type",
            violations=violations,
            allow_empty=True,
        )

        try:
            status = (
                UniversalStageResultStatus.coerce(
                    self.status
                )
            )

        except UniversalStageResultContractError as exc:

            violations.extend(
                exc.violations
                or (
                    str(exc),
                )
            )

            status = (
                UniversalStageResultStatus.FAILED
            )

        output = _normalize_mapping(
            self.output,
            name="output",
            violations=violations,
        )

        result_reference = _require_text(
            self.result_reference,
            name="result_reference",
            violations=violations,
            allow_empty=True,
        )

        artifact_references = (
            _normalize_reference_tuple(
                self.artifact_references,
                name="artifact_references",
                violations=violations,
            )
        )

        started_at = _require_timestamp(
            self.started_at,
            name="started_at",
            violations=violations,
        )

        finished_at = _require_timestamp(
            self.finished_at,
            name="finished_at",
            violations=violations,
        )

        failure_code = _require_name(
            self.failure_code,
            name="failure_code",
            violations=violations,
            allow_empty=True,
        )

        failure_message = _require_text(
            self.failure_message,
            name="failure_message",
            violations=violations,
            allow_empty=True,
        )

        failure_details = _normalize_mapping(
            self.failure_details,
            name="failure_details",
            violations=violations,
        )

        metadata = _normalize_mapping(
            self.metadata,
            name="metadata",
            violations=violations,
        )

        workflow_contract_version = _require_name(
            self.workflow_contract_version,
            name="workflow_contract_version",
            violations=violations,
        )

        stage_reference_contract_version = (
            _require_name(
                self.stage_reference_contract_version,
                name="stage_reference_contract_version",
                violations=violations,
            )
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
            stage_reference_contract_version
            != UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
        ):
            violations.append(
                "stage_reference_contract_version must be "
                + UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION
            )

        if (
            contract_version
            != UNIVERSAL_STAGE_RESULT_CONTRACT_VERSION
        ):
            violations.append(
                "contract_version must be "
                + UNIVERSAL_STAGE_RESULT_CONTRACT_VERSION
            )


        # ------------------------------------------------------------------
        # Runtime correlation invariants
        # ------------------------------------------------------------------

        if (
            execution_target
            == StageExecutionTarget.UNIVERSAL_RUNTIME
        ):

            if not job_id:
                violations.append(
                    "job_id is required when "
                    "execution_target is universal_runtime"
                )

            if not job_type:
                violations.append(
                    "job_type is required when "
                    "execution_target is universal_runtime"
                )

        if (
            execution_target
            == StageExecutionTarget.COORDINATION_ONLY
        ):

            if job_id:
                violations.append(
                    "job_id must be empty when "
                    "execution_target is coordination_only"
                )

            if job_type:
                violations.append(
                    "job_type must be empty when "
                    "execution_target is coordination_only"
                )


        # ------------------------------------------------------------------
        # Failure invariants
        # ------------------------------------------------------------------

        if (
            status
            == UniversalStageResultStatus.FAILED
        ):

            if not failure_code:
                violations.append(
                    "failure_code is required when status is failed"
                )

            if not failure_message:
                violations.append(
                    "failure_message is required when status is failed"
                )

        else:

            if failure_code:
                violations.append(
                    "failure_code must be empty when status is not failed"
                )

            if failure_message:
                violations.append(
                    "failure_message must be empty when status is not failed"
                )

            if failure_details:
                violations.append(
                    "failure_details must be empty when status is not failed"
                )


        # ------------------------------------------------------------------
        # Timestamp ordering
        # ------------------------------------------------------------------

        if (
            started_at
            and finished_at
        ):

            try:

                started_dt = _timestamp_value(
                    started_at
                )

                finished_dt = _timestamp_value(
                    finished_at
                )

                if (
                    started_dt.tzinfo is not None
                    and finished_dt.tzinfo is not None
                    and finished_dt < started_dt
                ):
                    violations.append(
                        "finished_at cannot be earlier than started_at"
                    )

            except ValueError:
                pass


        if violations:

            raise UniversalStageResultContractError(
                "Universal Stage Result validation failed",
                violations=tuple(
                    violations
                ),
            )


        object.__setattr__(
            self,
            "result_id",
            result_id,
        )

        object.__setattr__(
            self,
            "workflow_id",
            workflow_id,
        )

        object.__setattr__(
            self,
            "correlation_id",
            correlation_id,
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
            "workspace_id",
            workspace_id,
        )

        object.__setattr__(
            self,
            "execution_target",
            execution_target,
        )

        object.__setattr__(
            self,
            "job_id",
            job_id,
        )

        object.__setattr__(
            self,
            "job_type",
            job_type,
        )

        object.__setattr__(
            self,
            "status",
            status,
        )

        object.__setattr__(
            self,
            "output",
            output,
        )

        object.__setattr__(
            self,
            "result_reference",
            result_reference,
        )

        object.__setattr__(
            self,
            "artifact_references",
            artifact_references,
        )

        object.__setattr__(
            self,
            "started_at",
            started_at,
        )

        object.__setattr__(
            self,
            "finished_at",
            finished_at,
        )

        object.__setattr__(
            self,
            "failure_code",
            failure_code,
        )

        object.__setattr__(
            self,
            "failure_message",
            failure_message,
        )

        object.__setattr__(
            self,
            "failure_details",
            failure_details,
        )

        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

        object.__setattr__(
            self,
            "workflow_contract_version",
            workflow_contract_version,
        )

        object.__setattr__(
            self,
            "stage_reference_contract_version",
            stage_reference_contract_version,
        )

        object.__setattr__(
            self,
            "contract_version",
            contract_version,
        )


    # ======================================================================
    # Status properties
    # ======================================================================

    @property
    def completed(
        self,
    ) -> bool:

        return (
            self.status
            == UniversalStageResultStatus.COMPLETED
        )


    @property
    def failed(
        self,
    ) -> bool:

        return (
            self.status
            == UniversalStageResultStatus.FAILED
        )


    @property
    def skipped(
        self,
    ) -> bool:

        return (
            self.status
            == UniversalStageResultStatus.SKIPPED
        )


    @property
    def cancelled(
        self,
    ) -> bool:

        return (
            self.status
            == UniversalStageResultStatus.CANCELLED
        )


    @property
    def terminal(
        self,
    ) -> bool:
        """
        Every UniversalStageResult represents a terminal stage outcome.
        """

        return True


    # ======================================================================
    # Serialization
    # ======================================================================

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "result_id":
                self.result_id,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "stage_id":
                self.stage_id,

            "stage_version":
                self.stage_version,

            "pipeline_id":
                self.pipeline_id,

            "workflow_type":
                self.workflow_type,

            "workspace_id":
                self.workspace_id,

            "execution_target":
                self.execution_target.value,

            "job_id":
                self.job_id,

            "job_type":
                self.job_type,

            "status":
                self.status.value,

            "output":
                _thaw(
                    self.output
                ),

            "result_reference":
                self.result_reference,

            "artifact_references":
                list(
                    self.artifact_references
                ),

            "started_at":
                self.started_at,

            "finished_at":
                self.finished_at,

            "failure_code":
                self.failure_code,

            "failure_message":
                self.failure_message,

            "failure_details":
                _thaw(
                    self.failure_details
                ),

            "metadata":
                _thaw(
                    self.metadata
                ),

            "workflow_contract_version":
                self.workflow_contract_version,

            "stage_reference_contract_version":
                self.stage_reference_contract_version,

            "contract_version":
                self.contract_version,
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
            REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS
        )


    @classmethod
    def schema(
        cls,
    ) -> Mapping[str, Any]:

        return MappingProxyType(
            {
                "contract_id":
                    UNIVERSAL_STAGE_RESULT_CONTRACT_ID,

                "contract_version":
                    UNIVERSAL_STAGE_RESULT_CONTRACT_VERSION,

                "schema_version":
                    UNIVERSAL_STAGE_RESULT_SCHEMA_VERSION,

                "workflow_contract_version":
                    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,

                "stage_reference_contract_version":
                    UNIVERSAL_STAGE_REFERENCE_CONTRACT_VERSION,

                "required_fields":
                    REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS,

                "terminal_statuses":
                    tuple(
                        status.value
                        for status
                        in UniversalStageResultStatus
                    ),

                "coordination_status_authority":
                    "status",

                "business_output_authority":
                    "output",
            }
        )


    # ======================================================================
    # Reconstruction
    # ======================================================================

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "UniversalStageResult":

        if not isinstance(
            data,
            Mapping,
        ):
            raise UniversalStageResultContractError(
                "stage result data must be a mapping"
            )

        unknown_fields = sorted(
            set(data)
            - _CONTRACT_CONSTRUCTOR_FIELDS
        )

        if unknown_fields:
            raise UniversalStageResultContractError(
                "unknown Universal Stage Result fields: "
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
            in REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS
            if name not in data
        )

        if missing_fields:
            raise UniversalStageResultContractError(
                "missing required Universal Stage Result fields: "
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

        kwargs[
            "execution_target"
        ] = StageExecutionTarget.coerce(
            kwargs[
                "execution_target"
            ]
        )

        kwargs[
            "status"
        ] = UniversalStageResultStatus.coerce(
            kwargs[
                "status"
            ]
        )

        return cls(
            **kwargs
        )


    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "UniversalStageResult":

        try:

            data = json.loads(
                text
            )

        except json.JSONDecodeError as exc:

            raise UniversalStageResultContractError(
                "stage result json is not decodable: "
                + str(exc)
            ) from exc

        return cls.from_dict(
            data
        )


    @classmethod
    def reconstruct(
        cls,
        data: Mapping[str, Any],
    ) -> "UniversalStageResult":

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
            "contract_id":
                UNIVERSAL_STAGE_RESULT_CONTRACT_ID,

            "contract_version":
                self.contract_version,

            "result_id":
                self.result_id,

            "workflow_id":
                self.workflow_id,

            "stage_id":
                self.stage_id,

            "stage_version":
                self.stage_version,

            "pipeline_id":
                self.pipeline_id,

            "execution_target":
                self.execution_target.value,

            "job_id":
                self.job_id,

            "job_type":
                self.job_type,
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
    ) -> "UniversalStageResultValidationReport":

        return validate_universal_stage_result(
            self
        )


_CONTRACT_CONSTRUCTOR_FIELDS: Final[
    frozenset[str]
] = frozenset(
    item.name
    for item
    in fields(
        UniversalStageResult
    )
)


# ============================================================================
# 9. Standalone validation
# ============================================================================

def validate_universal_stage_result(
    candidate: Any,
) -> UniversalStageResultValidationReport:

    if isinstance(
        candidate,
        UniversalStageResult,
    ):

        return UniversalStageResultValidationReport(
            is_valid=True,
            violations=_EMPTY_TUPLE,
            contract_version=(
                candidate.contract_version
            ),
            checked_field_count=len(
                REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS
            ),
        )

    if not isinstance(
        candidate,
        Mapping,
    ):

        return UniversalStageResultValidationReport(
            is_valid=False,
            violations=(
                "candidate must be a UniversalStageResult "
                "or mapping",
            ),
            checked_field_count=0,
        )

    try:

        reconstructed = (
            UniversalStageResult.from_dict(
                candidate
            )
        )

    except UniversalStageResultContractError as exc:

        return UniversalStageResultValidationReport(
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
                REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS
            ),
        )

    return UniversalStageResultValidationReport(
        is_valid=True,
        violations=_EMPTY_TUPLE,
        contract_version=(
            reconstructed.contract_version
        ),
        checked_field_count=len(
            REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS
        ),
    )


__all__ = [
    "UNIVERSAL_STAGE_RESULT_CONTRACT_ID",
    "UNIVERSAL_STAGE_RESULT_CONTRACT_VERSION",
    "UNIVERSAL_STAGE_RESULT_SCHEMA_VERSION",
    "REQUIRED_UNIVERSAL_STAGE_RESULT_FIELDS",
    "UniversalStageResultStatus",
    "UniversalStageResult",
    "UniversalStageResultValidationReport",
    "UniversalStageResultContractError",
    "validate_universal_stage_result",
]

