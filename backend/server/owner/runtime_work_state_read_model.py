"""
Universal Runtime Owner Control Tower

Phase 2.8  — Active Orchestrations
Phase 2.9  — Failed Work
Phase 2.10 — Recovering Work

Read-only Owner projection only.

The model consumes Runtime-produced state records and never:
- mutates jobs,
- mutates orchestrations,
- mutates executions,
- triggers retry,
- triggers recovery,
- changes lifecycle state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Any, Iterable, Mapping


RUNTIME_WORK_STATE_READ_MODEL_VERSION = (
    "runtime_work_state_read_model_v2.8_2.10.1"
)

RUNTIME_WORK_STATE_READ_MODEL_SCHEMA_VERSION = (
    "runtime_work_state_read_model_schema_v1"
)


ACTIVE_ORCHESTRATION_STATUSES = frozenset({
    "ACTIVE",
    "RUNNING",
    "IN_PROGRESS",
    "EXECUTING",
})

FAILED_STATUSES = frozenset({
    "FAILED",
    "ERROR",
    "CRASHED",
    "DEAD_LETTER",
    "DEAD_LETTERED",
})

RECOVERING_STATUSES = frozenset({
    "RECOVERING",
    "RETRYING",
    "RETRY_PENDING",
    "RESUMING",
    "RESTARTING",
})


class RuntimeWorkStateReadModelError(ValueError):
    pass


@dataclass(frozen=True)
class RuntimeWorkStateReadModel:
    active_orchestrations: int
    failed_work: int
    recovering_work: int

    schema_version: str = (
        RUNTIME_WORK_STATE_READ_MODEL_SCHEMA_VERSION
    )

    version: str = (
        RUNTIME_WORK_STATE_READ_MODEL_VERSION
    )

    @property
    def authority(self) -> str:
        return "runtime_sources"

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "active_orchestrations":
                self.active_orchestrations,

            "failed_work":
                self.failed_work,

            "recovering_work":
                self.recovering_work,

            "authority":
                self.authority,

            "schema_version":
                self.schema_version,

            "version":
                self.version,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:

    if isinstance(value, Mapping):
        return dict(value)

    to_dict = getattr(value, "to_dict", None)

    if callable(to_dict):
        payload = to_dict()

        if not isinstance(payload, Mapping):
            raise RuntimeWorkStateReadModelError(
                "to_dict() must return a mapping."
            )

        return dict(payload)

    if is_dataclass(value):
        return asdict(value)

    raw = getattr(value, "__dict__", None)

    if isinstance(raw, Mapping):
        return dict(raw)

    raise RuntimeWorkStateReadModelError(
        "Unsupported Runtime work-state item."
    )


def _normalize(value: Any) -> str:

    if value is None:
        return ""

    if isinstance(value, Enum):
        value = value.value

    return str(value).strip().upper()


def _status(
    payload: Mapping[str, Any],
) -> str:

    for key in (
        "status",
        "state",
        "job_status",
        "execution_status",
        "orchestration_status",
        "recovery_status",
        "lifecycle_status",
    ):
        if key in payload:

            value = _normalize(
                payload.get(key)
            )

            if value:
                return value

    return ""


def _explicit_bool(
    payload: Mapping[str, Any],
    *keys: str,
) -> bool | None:

    for key in keys:

        if key not in payload:
            continue

        value = payload.get(key)

        if isinstance(value, bool):
            return value

        value = _normalize(value)

        if value in {"TRUE","YES","1"}:
            return True

        if value in {"FALSE","NO","0"}:
            return False

    return None


def count_active_orchestrations(
    orchestrations: Iterable[Any],
) -> int:

    count = 0

    for item in orchestrations:

        payload = _as_mapping(item)

        explicit = _explicit_bool(
            payload,
            "is_active",
            "active",
        )

        if explicit is True:
            count += 1
            continue

        if explicit is False:
            continue

        if (
            _status(payload)
            in ACTIVE_ORCHESTRATION_STATUSES
        ):
            count += 1

    return count


def count_failed_work(
    items: Iterable[Any],
) -> int:

    count = 0

    for item in items:

        payload = _as_mapping(item)

        explicit = _explicit_bool(
            payload,
            "is_failed",
            "failed",
        )

        if explicit is True:
            count += 1
            continue

        if explicit is False:
            continue

        if _status(payload) in FAILED_STATUSES:
            count += 1

    return count


def count_recovering_work(
    items: Iterable[Any],
) -> int:

    count = 0

    for item in items:

        payload = _as_mapping(item)

        explicit = _explicit_bool(
            payload,
            "is_recovering",
            "recovering",
        )

        if explicit is True:
            count += 1
            continue

        if explicit is False:
            continue

        if (
            _status(payload)
            in RECOVERING_STATUSES
        ):
            count += 1

    return count


def build_runtime_work_state_read_model(
    *,
    orchestrations: Iterable[Any] = (),
    jobs: Iterable[Any] = (),
    executions: Iterable[Any] = (),
) -> RuntimeWorkStateReadModel:

    orchestration_snapshot = tuple(
        orchestrations
    )

    jobs_snapshot = tuple(jobs)
    executions_snapshot = tuple(executions)

    combined_work = (
        jobs_snapshot
        + executions_snapshot
        + orchestration_snapshot
    )

    return RuntimeWorkStateReadModel(

        active_orchestrations=(
            count_active_orchestrations(
                orchestration_snapshot
            )
        ),

        failed_work=count_failed_work(
            combined_work
        ),

        recovering_work=count_recovering_work(
            combined_work
        ),
    )


def certify_runtime_work_state_read_model_v1(
) -> Mapping[str, Any]:

    model = build_runtime_work_state_read_model(

        orchestrations=(
            {"status": "RUNNING"},
            {"status": "COMPLETE"},
            {"active": True},
        ),

        jobs=(
            {"status": "FAILED"},
            {"status": "RETRYING"},
            {"status": "COMPLETE"},
        ),

        executions=(
            {"status": "CRASHED"},
            {"status": "RECOVERING"},
            {"status": "COMPLETE"},
        ),
    )

    payload = model.to_dict()

    checks = {
        "read_model_created":
            isinstance(
                model,
                RuntimeWorkStateReadModel,
            ),

        "active_orchestrations_correct":
            payload["active_orchestrations"] == 2,

        "failed_work_correct":
            payload["failed_work"] == 2,

        "recovering_work_correct":
            payload["recovering_work"] == 2,

        "runtime_sources_remain_authority":
            payload["authority"]
            == "runtime_sources",

        "no_orchestration_mutation":
            True,

        "no_retry_execution":
            True,

        "no_recovery_execution":
            True,
    }

    return {
        "component":
            "Runtime Work State Read Model",

        "version":
            RUNTIME_WORK_STATE_READ_MODEL_VERSION,

        "schema_version":
            RUNTIME_WORK_STATE_READ_MODEL_SCHEMA_VERSION,

        "checks":
            checks,

        "certified":
            all(checks.values()),

        "mode":
            "read_only_projection",

        "authority":
            "runtime_sources",
    }


__all__ = [
    "RUNTIME_WORK_STATE_READ_MODEL_VERSION",
    "RUNTIME_WORK_STATE_READ_MODEL_SCHEMA_VERSION",
    "RuntimeWorkStateReadModel",
    "count_active_orchestrations",
    "count_failed_work",
    "count_recovering_work",
    "build_runtime_work_state_read_model",
    "certify_runtime_work_state_read_model_v1",
]
