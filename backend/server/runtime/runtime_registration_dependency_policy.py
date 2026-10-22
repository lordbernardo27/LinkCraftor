"""
Registration stage-dependency enforcement.

This authority consumes persisted dependency_job_ids and the canonical
Runtime Registration registry. It creates no second coordinator,
dependency graph, queue, registry, lock or persistence store.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping


SCHEMA_VERSION = "runtime_registration_dependency_policy_v1"


class RuntimeRegistrationDependencyPolicyError(RuntimeError):
    pass


class RuntimeRegistrationDependencyAction(str, Enum):
    ADMIT = "admit"
    DEFER = "defer"


@dataclass(frozen=True, slots=True)
class RuntimeRegistrationDependencyAdmission:
    action: RuntimeRegistrationDependencyAction
    reason: str
    job_type: str
    stage: str
    required_predecessor_stages: tuple[str, ...] = ()
    satisfied_predecessor_stages: tuple[str, ...] = ()
    dependency_job_ids: tuple[str, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evidence",
            MappingProxyType(dict(self.evidence)),
        )

    def to_metadata(self) -> dict[str, Any]:
        return {
            "runtime_registration_dependency_schema_version":
                self.schema_version,
            "runtime_registration_dependency_action":
                self.action.value,
            "runtime_registration_dependency_reason":
                self.reason,
            "runtime_registration_stage":
                self.stage,
            "runtime_registration_required_predecessors":
                list(self.required_predecessor_stages),
            "runtime_registration_satisfied_predecessors":
                list(self.satisfied_predecessor_stages),
            "runtime_registration_dependency_job_ids":
                list(self.dependency_job_ids),
            "runtime_registration_dependency_evidence":
                dict(self.evidence),
        }


def _read(
    value: Any,
    name: str,
    default: Any = None,
) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)

    return getattr(value, name, default)


def _text(value: Any) -> str:
    return str(
        value if value is not None else ""
    ).strip()


def _collection(
    value: Any,
    field_name: str,
) -> tuple[str, ...]:
    if value is None:
        return ()

    if isinstance(value, (str, bytes)):
        raise RuntimeRegistrationDependencyPolicyError(
            f"{field_name} must be a collection."
        )

    result: list[str] = []

    for item in value:
        normalized = _text(item)

        if not normalized:
            raise RuntimeRegistrationDependencyPolicyError(
                f"{field_name} contains an empty value."
            )

        if normalized in result:
            raise RuntimeRegistrationDependencyPolicyError(
                f"{field_name} contains a duplicate: "
                + normalized
            )

        result.append(normalized)

    return tuple(result)


def _registration(
    value: Any,
) -> Mapping[str, Any] | None:
    if value is None:
        return None

    if isinstance(value, Mapping):
        return value

    public = getattr(
        value,
        "to_public_dict",
        None,
    )

    if callable(public):
        result = public()

        if isinstance(result, Mapping):
            return result

    raise RuntimeRegistrationDependencyPolicyError(
        "Registration must be a mapping or expose "
        "to_public_dict()."
    )


def _metadata(job: Any) -> Mapping[str, Any]:
    value = _read(job, "metadata", {})

    return value if isinstance(value, Mapping) else {}


def _canonical_job(
    job: Any,
) -> Mapping[str, Any] | None:
    projections = [
        value.get("canonical_job")
        for value in _metadata(job).values()
        if (
            isinstance(value, Mapping)
            and "canonical_job" in value
        )
    ]

    if not projections:
        return None

    if len(projections) != 1:
        raise RuntimeRegistrationDependencyPolicyError(
            "Expected exactly one canonical job projection."
        )

    projection = projections[0]

    if not isinstance(projection, Mapping):
        raise RuntimeRegistrationDependencyPolicyError(
            "Canonical job projection is malformed."
        )

    projected_id = _text(
        projection.get("job_id")
    )

    actual_id = _text(
        _read(job, "job_id")
    )

    if projected_id != actual_id:
        raise RuntimeRegistrationDependencyPolicyError(
            "Canonical and orchestration job identities differ."
        )

    return projection


def _dependency_ids(
    job: Any,
) -> tuple[str, ...]:
    projection = _canonical_job(job)

    if projection is None:
        return ()

    raw = projection.get(
        "dependency_job_ids",
        (),
    )

    return _collection(
        raw,
        "dependency_job_ids",
    )


def _status(job: Any) -> str:
    status = _text(
        _read(job, "status")
    ).lower()

    if status == "completed":
        return "succeeded"

    return status


def _defer(
    *,
    reason: str,
    job_type: str,
    stage: str,
    required: tuple[str, ...],
    satisfied: tuple[str, ...],
    dependency_ids: tuple[str, ...],
    evidence: Mapping[str, Any],
) -> RuntimeRegistrationDependencyAdmission:
    return RuntimeRegistrationDependencyAdmission(
        action=RuntimeRegistrationDependencyAction.DEFER,
        reason=reason,
        job_type=job_type,
        stage=stage,
        required_predecessor_stages=required,
        satisfied_predecessor_stages=satisfied,
        dependency_job_ids=dependency_ids,
        evidence=evidence,
    )


def evaluate_runtime_registration_stage_dependencies(
    *,
    candidate: Any,
    existing_jobs: Iterable[Any],
    registration: Any,
    registration_resolver: Callable[[str], Any],
) -> RuntimeRegistrationDependencyAdmission:
    public = _registration(registration)

    job_type = _text(
        _read(candidate, "job_type")
    )

    workspace_id = _text(
        _read(candidate, "workspace_id")
    )

    if not job_type or not workspace_id:
        raise RuntimeRegistrationDependencyPolicyError(
            "Candidate job_type and workspace_id are required."
        )

    if public is None:
        return RuntimeRegistrationDependencyAdmission(
            action=RuntimeRegistrationDependencyAction.ADMIT,
            reason="no_runtime_registration",
            job_type=job_type,
            stage="",
        )

    registered_type = _text(
        public.get("job_type")
    )

    if registered_type and registered_type != job_type:
        raise RuntimeRegistrationDependencyPolicyError(
            "Registration job_type does not match candidate."
        )

    stage = _text(
        public.get("stage")
    )

    pipeline = _text(
        public.get("pipeline")
    )

    required = _collection(
        public.get("predecessor_stages", ()),
        "predecessor_stages",
    )

    successors = _collection(
        public.get("successor_stages", ()),
        "successor_stages",
    )

    if (required or successors) and not stage:
        raise RuntimeRegistrationDependencyPolicyError(
            "A registration declaring stage dependencies "
            "must declare its own stage."
        )

    dependency_ids = _dependency_ids(candidate)

    if not required:
        return RuntimeRegistrationDependencyAdmission(
            action=RuntimeRegistrationDependencyAction.ADMIT,
            reason="no_predecessor_stages_declared",
            job_type=job_type,
            stage=stage,
            dependency_job_ids=dependency_ids,
            evidence={
                "successor_stages": list(successors),
            },
        )

    if not dependency_ids:
        return _defer(
            reason="required_dependency_job_ids_missing",
            job_type=job_type,
            stage=stage,
            required=required,
            satisfied=(),
            dependency_ids=(),
            evidence={},
        )

    jobs_by_id = {
        _text(_read(job, "job_id")): job
        for job in existing_jobs
        if _text(_read(job, "job_id"))
    }

    satisfied: list[str] = []
    stage_evidence: dict[str, Any] = {}

    for dependency_id in dependency_ids:
        dependency = jobs_by_id.get(
            dependency_id
        )

        if dependency is None:
            return _defer(
                reason="dependency_job_missing",
                job_type=job_type,
                stage=stage,
                required=required,
                satisfied=tuple(satisfied),
                dependency_ids=dependency_ids,
                evidence={
                    "missing_dependency_job_id":
                        dependency_id,
                },
            )

        dependency_workspace = _text(
            _read(dependency, "workspace_id")
        )

        if dependency_workspace != workspace_id:
            return _defer(
                reason="dependency_workspace_mismatch",
                job_type=job_type,
                stage=stage,
                required=required,
                satisfied=tuple(satisfied),
                dependency_ids=dependency_ids,
                evidence={
                    "dependency_job_id": dependency_id,
                },
            )

        if _status(dependency) != "succeeded":
            return _defer(
                reason="dependency_not_succeeded",
                job_type=job_type,
                stage=stage,
                required=required,
                satisfied=tuple(satisfied),
                dependency_ids=dependency_ids,
                evidence={
                    "dependency_job_id": dependency_id,
                    "dependency_status":
                        _status(dependency),
                },
            )

        dependency_job_type = _text(
            _read(dependency, "job_type")
        )

        try:
            dependency_registration = _registration(
                registration_resolver(
                    dependency_job_type
                )
            )
        except (KeyError, ValueError):
            dependency_registration = None

        if dependency_registration is None:
            return _defer(
                reason="dependency_registration_missing",
                job_type=job_type,
                stage=stage,
                required=required,
                satisfied=tuple(satisfied),
                dependency_ids=dependency_ids,
                evidence={
                    "dependency_job_id": dependency_id,
                    "dependency_job_type":
                        dependency_job_type,
                },
            )

        dependency_stage = _text(
            dependency_registration.get("stage")
        )

        dependency_pipeline = _text(
            dependency_registration.get("pipeline")
        )

        declared_successors = _collection(
            dependency_registration.get(
                "successor_stages",
                (),
            ),
            "successor_stages",
        )

        if (
            pipeline
            and dependency_pipeline
            and pipeline != dependency_pipeline
        ):
            return _defer(
                reason="dependency_pipeline_mismatch",
                job_type=job_type,
                stage=stage,
                required=required,
                satisfied=tuple(satisfied),
                dependency_ids=dependency_ids,
                evidence={
                    "dependency_job_id": dependency_id,
                    "dependency_pipeline":
                        dependency_pipeline,
                    "candidate_pipeline": pipeline,
                },
            )

        stage_evidence[dependency_stage] = {
            "job_id": dependency_id,
            "job_type": dependency_job_type,
            "successor_stages":
                list(declared_successors),
        }

        if dependency_stage not in required:
            continue

        if stage not in declared_successors:
            return _defer(
                reason="successor_stage_not_reciprocal",
                job_type=job_type,
                stage=stage,
                required=required,
                satisfied=tuple(satisfied),
                dependency_ids=dependency_ids,
                evidence={
                    "dependency_stage":
                        dependency_stage,
                    "declared_successors":
                        list(declared_successors),
                },
            )

        if dependency_stage not in satisfied:
            satisfied.append(
                dependency_stage
            )

    missing_stages = tuple(
        predecessor
        for predecessor in required
        if predecessor not in satisfied
    )

    if missing_stages:
        return _defer(
            reason="required_predecessor_stage_missing",
            job_type=job_type,
            stage=stage,
            required=required,
            satisfied=tuple(satisfied),
            dependency_ids=dependency_ids,
            evidence={
                "missing_predecessor_stages":
                    list(missing_stages),
                "dependency_stages":
                    stage_evidence,
            },
        )

    return RuntimeRegistrationDependencyAdmission(
        action=RuntimeRegistrationDependencyAction.ADMIT,
        reason="stage_dependencies_satisfied",
        job_type=job_type,
        stage=stage,
        required_predecessor_stages=required,
        satisfied_predecessor_stages=tuple(satisfied),
        dependency_job_ids=dependency_ids,
        evidence={
            "pipeline": pipeline,
            "successor_stages": list(successors),
            "dependency_stages": stage_evidence,
        },
    )
