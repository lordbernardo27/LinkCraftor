
# ============================================================================
# Part C 8-D2 - Execution-wave submission authority
# ============================================================================

from collections.abc import Iterable as _WaveIterable
from collections.abc import Mapping as _WaveMapping
from dataclasses import dataclass as _wave_dataclass
from dataclasses import replace as _wave_replace
from types import MappingProxyType as _WaveMappingProxyType

from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RuntimeJobMappingResult,
)


RUNTIME_EXECUTION_WAVE_GATEWAY_VERSION = (
    "runtime_execution_wave_gateway_v1.0.0"
)
RUNTIME_EXECUTION_WAVE_GATEWAY_CONTRACT_VERSION = (
    "runtime_execution_wave_gateway_contract_v1"
)


def _wave_freeze(value: Any) -> Any:
    if isinstance(value, _WaveMapping):
        return _WaveMappingProxyType(
            {
                str(key): _wave_freeze(item)
                for key, item in value.items()
            }
        )
    if isinstance(value, (list, tuple)):
        return tuple(_wave_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return tuple(
            sorted(
                (_wave_freeze(item) for item in value),
                key=repr,
            )
        )
    return value


def _wave_plain(value: Any) -> Any:
    if isinstance(value, _WaveMapping):
        return {
            str(key): _wave_plain(item)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        return [_wave_plain(item) for item in value]
    return value


class RuntimeExecutionWaveGatewayError(
    RuntimeExecutionGatewayError
):
    """Fail-closed execution-wave submission error."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        violations: tuple[str, ...] = (),
        submitted_results: tuple[
            RuntimeExecutionGatewayResult,
            ...,
        ] = (),
    ) -> None:
        super().__init__(
            message,
            code=code,
            violations=violations,
        )
        self.submitted_results = tuple(submitted_results)
        self.submitted_count = len(self.submitted_results)


@_wave_dataclass(frozen=True, slots=True)
class RuntimeExecutionWaveGatewayResult:
    contract_version: str
    workflow_id: str
    wave_index: int | None
    mapping_count: int
    submitted_count: int
    stage_ids: tuple[str, ...]
    job_ids: tuple[str, ...]
    results: tuple[RuntimeExecutionGatewayResult, ...]
    dependency_job_ids_by_stage: _WaveMapping[
        str,
        tuple[str, ...],
    ]
    evidence: _WaveMapping[str, Any]

    def __post_init__(self) -> None:
        if self.mapping_count != len(self.stage_ids):
            raise RuntimeExecutionWaveGatewayError(
                "mapping_count does not match stage_ids.",
                code="invalid_wave_result",
                violations=("mapping_count", "stage_ids"),
            )
        if self.submitted_count != len(self.results):
            raise RuntimeExecutionWaveGatewayError(
                "submitted_count does not match results.",
                code="invalid_wave_result",
                violations=("submitted_count", "results"),
            )
        if self.submitted_count != len(self.job_ids):
            raise RuntimeExecutionWaveGatewayError(
                "submitted_count does not match job_ids.",
                code="invalid_wave_result",
                violations=("submitted_count", "job_ids"),
            )
        object.__setattr__(
            self,
            "dependency_job_ids_by_stage",
            _wave_freeze(self.dependency_job_ids_by_stage),
        )
        object.__setattr__(
            self,
            "evidence",
            _wave_freeze(self.evidence),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "workflow_id": self.workflow_id,
            "wave_index": self.wave_index,
            "mapping_count": self.mapping_count,
            "submitted_count": self.submitted_count,
            "stage_ids": list(self.stage_ids),
            "job_ids": list(self.job_ids),
            "results": [
                result.to_dict()
                for result in self.results
            ],
            "dependency_job_ids_by_stage": _wave_plain(
                self.dependency_job_ids_by_stage
            ),
            "evidence": _wave_plain(self.evidence),
        }


def _normalize_wave_dependencies(
    value: _WaveMapping[
        str,
        _WaveIterable[str],
    ]
    | None,
    *,
    stage_ids: tuple[str, ...],
) -> dict[str, tuple[str, ...]]:
    if value is None:
        return {}
    if not isinstance(value, _WaveMapping):
        raise RuntimeExecutionWaveGatewayError(
            "dependency_job_ids_by_stage must be a mapping.",
            code="invalid_wave_dependencies",
            violations=("dependency_job_ids_by_stage",),
        )

    known = set(stage_ids)
    normalized: dict[str, tuple[str, ...]] = {}

    for raw_stage_id, raw_job_ids in value.items():
        stage_id = str(raw_stage_id or "").strip()
        if not stage_id or stage_id not in known:
            raise RuntimeExecutionWaveGatewayError(
                "Dependency mapping references an unknown stage.",
                code="invalid_wave_dependencies",
                violations=(f"unknown stage: {stage_id!r}",),
            )
        if isinstance(raw_job_ids, (str, bytes)) or not isinstance(
            raw_job_ids,
            _WaveIterable,
        ):
            raise RuntimeExecutionWaveGatewayError(
                "Stage dependency IDs must be an iterable of strings.",
                code="invalid_wave_dependencies",
                violations=(f"stage: {stage_id}",),
            )

        job_ids: list[str] = []
        for raw_job_id in raw_job_ids:
            job_id = str(raw_job_id or "").strip()
            if not job_id:
                raise RuntimeExecutionWaveGatewayError(
                    "Dependency job IDs must be non-empty strings.",
                    code="invalid_wave_dependencies",
                    violations=(f"stage: {stage_id}",),
                )
            if job_id in job_ids:
                raise RuntimeExecutionWaveGatewayError(
                    "Duplicate dependency job ID declared.",
                    code="invalid_wave_dependencies",
                    violations=(f"{stage_id}:{job_id}",),
                )
            job_ids.append(job_id)

        normalized[stage_id] = tuple(job_ids)

    return normalized


def _prepare_runtime_execution_wave(
    *,
    mapping_result: RuntimeJobMappingResult,
    dependency_job_ids_by_stage: _WaveMapping[
        str,
        _WaveIterable[str],
    ]
    | None,
) -> tuple[
    tuple[RuntimeJobMapping, ...],
    dict[str, tuple[str, ...]],
    int | None,
]:
    if not isinstance(mapping_result, RuntimeJobMappingResult):
        raise RuntimeExecutionWaveGatewayError(
            "mapping_result must be RuntimeJobMappingResult.",
            code="invalid_wave_mapping",
            violations=("mapping_result",),
        )

    mappings = tuple(mapping_result.mappings)
    stage_ids = tuple(mapping_result.stage_ids)

    if mapping_result.mapping_count != len(mappings):
        raise RuntimeExecutionWaveGatewayError(
            "mapping_count does not match mappings.",
            code="invalid_wave_mapping",
            violations=("mapping_count", "mappings"),
        )
    if stage_ids != tuple(mapping.stage_id for mapping in mappings):
        raise RuntimeExecutionWaveGatewayError(
            "stage_ids do not match mapping order.",
            code="invalid_wave_mapping",
            violations=("stage_ids", "mappings"),
        )
    if len(set(stage_ids)) != len(stage_ids):
        raise RuntimeExecutionWaveGatewayError(
            "Execution wave contains duplicate stage IDs.",
            code="invalid_wave_mapping",
            violations=("stage_ids",),
        )
    if any(
        mapping.workflow_id != mapping_result.workflow_id
        for mapping in mappings
    ):
        raise RuntimeExecutionWaveGatewayError(
            "Mapping workflow identity does not match mapping_result.",
            code="invalid_wave_mapping",
            violations=("workflow_id",),
        )

    wave_indexes = {
        mapping.wave_index
        for mapping in mappings
    }
    if len(wave_indexes) > 1:
        raise RuntimeExecutionWaveGatewayError(
            "One gateway call may submit only one execution wave.",
            code="mixed_execution_waves",
            violations=("wave_index",),
        )
    wave_index = next(iter(wave_indexes), None)

    normalized_dependencies = _normalize_wave_dependencies(
        dependency_job_ids_by_stage,
        stage_ids=stage_ids,
    )

    prepared: list[RuntimeJobMapping] = []

    for mapping in mappings:
        request = mapping.creation_request

        if request.idempotency_key is not None:
            raise RuntimeExecutionWaveGatewayError(
                "Part C 8-D must not establish idempotency_key.",
                code="idempotency_authority_reserved",
                violations=(mapping.stage_id,),
            )

        existing_dependencies = tuple(request.dependency_job_ids)
        supplied = normalized_dependencies.get(mapping.stage_id)

        if supplied is None:
            effective_dependencies = existing_dependencies
        elif existing_dependencies and existing_dependencies != supplied:
            raise RuntimeExecutionWaveGatewayError(
                "Dependency enrichment conflicts with the mapping.",
                code="dependency_conflict",
                violations=(mapping.stage_id,),
            )
        else:
            effective_dependencies = supplied

        effective_request = request
        if effective_dependencies != existing_dependencies:
            effective_request = _wave_replace(
                request,
                dependency_job_ids=effective_dependencies,
            )

        effective_mapping = mapping
        if effective_request is not request:
            effective_mapping = _wave_replace(
                mapping,
                creation_request=effective_request,
            )

        # Complete preflight occurs before the first submission.
        validated_request = _validate_mapping(effective_mapping)
        _resolve_registration(validated_request)
        prepared.append(effective_mapping)

    effective_by_stage = {
        mapping.stage_id: tuple(
            mapping.creation_request.dependency_job_ids
        )
        for mapping in prepared
    }

    return (
        tuple(prepared),
        effective_by_stage,
        wave_index,
    )


def submit_runtime_execution_wave(
    *,
    mapping_result: RuntimeJobMappingResult,
    dependency_job_ids_by_stage: _WaveMapping[
        str,
        _WaveIterable[str],
    ]
    | None = None,
    submitter: Callable[
        ...,
        _WaveMapping[str, Any],
    ] = submit_universal_job,
    correlation_registry: (
        WorkflowJobCorrelationRegistry
        | None
    ) = None,
) -> RuntimeExecutionWaveGatewayResult:
    """
    Submit one certified immediate execution wave.

    Mapping order is deterministic submission order only. It does not create
    dependencies between stages in the same parallel-eligible wave.
    """
    if not callable(submitter):
        raise RuntimeExecutionWaveGatewayError(
            "submitter must be callable.",
            code="wave_submission_failure",
            violations=("submitter",),
        )

    effective_registry = (
        correlation_registry
        if correlation_registry is not None
        else get_workflow_job_correlation_registry()
    )
    if not isinstance(
        effective_registry,
        WorkflowJobCorrelationRegistry,
    ):
        raise RuntimeExecutionWaveGatewayError(
            "correlation_registry must be WorkflowJobCorrelationRegistry.",
            code="wave_correlation_failure",
            violations=("correlation_registry",),
        )

    (
        prepared_mappings,
        effective_dependencies,
        wave_index,
    ) = _prepare_runtime_execution_wave(
        mapping_result=mapping_result,
        dependency_job_ids_by_stage=dependency_job_ids_by_stage,
    )

    results: list[RuntimeExecutionGatewayResult] = []

    for mapping in prepared_mappings:
        try:
            result = submit_runtime_job_mapping(
                mapping=mapping,
                submitter=submitter,
                correlation_registry=effective_registry,
            )
        except Exception as error:
            raise RuntimeExecutionWaveGatewayError(
                "Execution-wave submission did not complete.",
                code=(
                    "partial_wave_submission"
                    if results
                    else "wave_submission_failure"
                ),
                violations=(mapping.stage_id,),
                submitted_results=tuple(results),
            ) from error
        results.append(result)

    result_tuple = tuple(results)

    return RuntimeExecutionWaveGatewayResult(
        contract_version=(
            RUNTIME_EXECUTION_WAVE_GATEWAY_CONTRACT_VERSION
        ),
        workflow_id=mapping_result.workflow_id,
        wave_index=wave_index,
        mapping_count=mapping_result.mapping_count,
        submitted_count=len(result_tuple),
        stage_ids=tuple(mapping_result.stage_ids),
        job_ids=tuple(result.job_id for result in result_tuple),
        results=result_tuple,
        dependency_job_ids_by_stage=effective_dependencies,
        evidence={
            "gateway_version": RUNTIME_EXECUTION_WAVE_GATEWAY_VERSION,
            "single_mapping_gateway": "submit_runtime_job_mapping",
            "canonical_submitter": "submit_universal_job",
            "preflight_completed_before_submission": True,
            "submission_order": "mapping_result_order",
            "runtime_parallel_eligibility_preserved": True,
            "artificial_intra_wave_dependencies": False,
            "idempotency_authority": "part_c_8_e",
            "partial_submission_reconciliation": "part_c_8_e",
            "handler_dispatched": False,
        },
    )


def explain_runtime_execution_wave_gateway_v1() -> dict[str, Any]:
    return {
        "component": "Runtime Execution Wave Gateway",
        "version": RUNTIME_EXECUTION_WAVE_GATEWAY_VERSION,
        "contract_version": (
            RUNTIME_EXECUTION_WAVE_GATEWAY_CONTRACT_VERSION
        ),
        "canonical_input": "RuntimeJobMappingResult",
        "single_mapping_gateway": "submit_runtime_job_mapping",
        "dependency_enrichment": True,
        "artificial_intra_wave_dependencies": False,
        "idempotency_authority": "Part C 8-E",
        "direct_handler_dispatch": False,
    }

