from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

REGISTRY_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_runtime_registration.py"
)

ORCHESTRATOR_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "jobs"
    / "universal_knowledge_orchestrator.py"
)

WORKER_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "workers"
    / "universal_knowledge_worker.py"
)


REGISTRY_SOURCE = r'''"""Universal Runtime Registration.

This module provides the reusable registration mechanism used to connect
LinkCraftor business-logic handlers to the Universal Runtime Infrastructure.

It does not create a second runtime, queue, worker system or scheduler.
Registered handlers execute through the existing universal worker contract.
"""

from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import os
import re
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Iterable, Mapping


REGISTRATION_SCHEMA_VERSION = (
    "universal_runtime_registration_v1"
)

REGISTRY_ROOT = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "runtime"
    / "universal_runtime_registration"
)

REGISTRY_PATH = (
    REGISTRY_ROOT
    / "runtime_registration_registry.json"
)

_NAME_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
)

_REGISTRY_LOCK = RLock()

_RUNTIME_HANDLER_REGISTRY: dict[
    str,
    "RuntimeHandlerRegistration",
] = {}

_PERSISTED_REGISTRY_LOADED = False


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_name(
    value: Any,
    *,
    field_name: str,
) -> str:
    normalized = str(
        value or ""
    ).strip()

    if not normalized:
        raise ValueError(
            f"{field_name} is required."
        )

    if not _NAME_PATTERN.fullmatch(
        normalized
    ):
        raise ValueError(
            f"{field_name} contains unsupported characters: "
            f"{normalized}"
        )

    return normalized


def _normalize_optional_name(
    value: Any,
    *,
    fallback: str,
    field_name: str,
) -> str:
    normalized = str(
        value or fallback
    ).strip()

    return _normalize_name(
        normalized,
        field_name=field_name,
    )


def _normalize_string_tuple(
    values: Iterable[Any] | None,
) -> tuple[str, ...]:
    if values is None:
        return ()

    normalized: list[str] = []

    for value in values:
        item = str(
            value or ""
        ).strip()

        if not item:
            continue

        if item not in normalized:
            normalized.append(item)

    return tuple(normalized)


def _normalize_mapping(
    value: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if value is None:
        return {}

    if not isinstance(value, Mapping):
        raise TypeError(
            "Registration metadata must be a mapping."
        )

    return {
        str(key): item
        for key, item in value.items()
    }


def _handler_reference(
    handler: Callable[..., Any],
) -> str:
    module_name = str(
        getattr(
            handler,
            "__module__",
            "",
        )
        or ""
    ).strip()

    qualified_name = str(
        getattr(
            handler,
            "__qualname__",
            "",
        )
        or getattr(
            handler,
            "__name__",
            "",
        )
        or ""
    ).strip()

    if not module_name or not qualified_name:
        raise ValueError(
            "Unable to determine handler import reference."
        )

    return (
        f"{module_name}:{qualified_name}"
    )


def _resolve_handler_reference(
    reference: str,
) -> Callable[..., Any]:
    normalized = str(
        reference or ""
    ).strip()

    if ":" not in normalized:
        raise ValueError(
            "Handler references must use module:attribute format."
        )

    module_name, qualified_name = (
        normalized.split(
            ":",
            1,
        )
    )

    module_name = module_name.strip()
    qualified_name = qualified_name.strip()

    if not module_name or not qualified_name:
        raise ValueError(
            f"Invalid handler reference: {reference}"
        )

    module = importlib.import_module(
        module_name
    )

    value: Any = module

    for attribute in qualified_name.split("."):
        if attribute == "<locals>":
            raise ValueError(
                "Local functions cannot be loaded from a "
                "persistent runtime registration."
            )

        value = getattr(
            value,
            attribute,
        )

    if not callable(value):
        raise TypeError(
            f"Registered handler is not callable: {reference}"
        )

    return value


def _resolve_handler(
    handler: Callable[..., Any] | str,
) -> tuple[Callable[..., Any], str]:
    if callable(handler):
        return (
            handler,
            _handler_reference(handler),
        )

    if isinstance(handler, str):
        return (
            _resolve_handler_reference(
                handler
            ),
            handler.strip(),
        )

    raise TypeError(
        "handler must be callable or a module:attribute string."
    )


def _atomic_write_text(
    path: Path,
    value: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )

    temporary_path = Path(
        temporary_name
    )

    try:
        with os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            handle.write(value)
            handle.flush()
            os.fsync(
                handle.fileno()
            )

        os.replace(
            temporary_path,
            path,
        )
    finally:
        temporary_path.unlink(
            missing_ok=True,
        )


@dataclass(frozen=True)
class RuntimeHandlerRegistration:
    job_type: str
    pipeline: str
    stage: str
    handler_ref: str
    handler: Callable[..., Any] = field(
        repr=False,
        compare=False,
    )
    description: str = ""
    required_payload_fields: tuple[str, ...] = ()
    predecessor_stages: tuple[str, ...] = ()
    successor_stages: tuple[str, ...] = ()
    idempotency_fields: tuple[str, ...] = ()
    retry_policy: dict[str, Any] = field(
        default_factory=dict
    )
    concurrency_policy: dict[str, Any] = field(
        default_factory=dict
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )
    persistent: bool = False
    registered_at: str = ""

    def to_public_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "schema_version": (
                REGISTRATION_SCHEMA_VERSION
            ),
            "job_type": self.job_type,
            "pipeline": self.pipeline,
            "stage": self.stage,
            "handler_ref": self.handler_ref,
            "description": self.description,
            "required_payload_fields": list(
                self.required_payload_fields
            ),
            "predecessor_stages": list(
                self.predecessor_stages
            ),
            "successor_stages": list(
                self.successor_stages
            ),
            "idempotency_fields": list(
                self.idempotency_fields
            ),
            "retry_policy": dict(
                self.retry_policy
            ),
            "concurrency_policy": dict(
                self.concurrency_policy
            ),
            "metadata": dict(
                self.metadata
            ),
            "persistent": self.persistent,
            "registered_at": self.registered_at,
        }


def _persist_registry_snapshot() -> None:
    persistent_records = [
        registration.to_public_dict()
        for registration in sorted(
            _RUNTIME_HANDLER_REGISTRY.values(),
            key=lambda item: item.job_type,
        )
        if registration.persistent
    ]

    document = {
        "schema_version": (
            REGISTRATION_SCHEMA_VERSION
        ),
        "updated_at": utc_now(),
        "registration_count": len(
            persistent_records
        ),
        "registrations": persistent_records,
    }

    _atomic_write_text(
        REGISTRY_PATH,
        json.dumps(
            document,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
    )


def register_runtime_handler(
    *,
    job_type: str,
    handler: Callable[..., Any] | str,
    pipeline: str = "",
    stage: str = "",
    description: str = "",
    required_payload_fields: Iterable[Any] | None = None,
    predecessor_stages: Iterable[Any] | None = None,
    successor_stages: Iterable[Any] | None = None,
    idempotency_fields: Iterable[Any] | None = None,
    retry_policy: Mapping[str, Any] | None = None,
    concurrency_policy: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    replace: bool = False,
    persist: bool = False,
    _loaded_from_persistence: bool = False,
) -> dict[str, Any]:
    canonical_job_type = _normalize_name(
        job_type,
        field_name="job_type",
    )

    canonical_pipeline = (
        _normalize_optional_name(
            pipeline,
            fallback="universal_knowledge",
            field_name="pipeline",
        )
    )

    canonical_stage = (
        _normalize_optional_name(
            stage,
            fallback=canonical_job_type,
            field_name="stage",
        )
    )

    resolved_handler, handler_ref = (
        _resolve_handler(
            handler
        )
    )

    if (
        persist
        and "<locals>" in handler_ref
    ):
        raise ValueError(
            "Persistent handlers must be importable top-level "
            "functions."
        )

    persistent = bool(
        persist
        or _loaded_from_persistence
    )

    registration = RuntimeHandlerRegistration(
        job_type=canonical_job_type,
        pipeline=canonical_pipeline,
        stage=canonical_stage,
        handler_ref=handler_ref,
        handler=resolved_handler,
        description=str(
            description or ""
        ).strip(),
        required_payload_fields=(
            _normalize_string_tuple(
                required_payload_fields
            )
        ),
        predecessor_stages=(
            _normalize_string_tuple(
                predecessor_stages
            )
        ),
        successor_stages=(
            _normalize_string_tuple(
                successor_stages
            )
        ),
        idempotency_fields=(
            _normalize_string_tuple(
                idempotency_fields
            )
        ),
        retry_policy=_normalize_mapping(
            retry_policy
        ),
        concurrency_policy=(
            _normalize_mapping(
                concurrency_policy
            )
        ),
        metadata=_normalize_mapping(
            metadata
        ),
        persistent=persistent,
        registered_at=utc_now(),
    )

    with _REGISTRY_LOCK:
        existing = (
            _RUNTIME_HANDLER_REGISTRY.get(
                canonical_job_type
            )
        )

        if (
            existing is not None
            and not replace
        ):
            raise ValueError(
                "Runtime handler already registered for "
                f"job_type: {canonical_job_type}"
            )

        _RUNTIME_HANDLER_REGISTRY[
            canonical_job_type
        ] = registration

        if persist:
            _persist_registry_snapshot()

    return registration.to_public_dict()


def runtime_handler(
    *,
    job_type: str,
    pipeline: str = "",
    stage: str = "",
    description: str = "",
    required_payload_fields: Iterable[Any] | None = None,
    predecessor_stages: Iterable[Any] | None = None,
    successor_stages: Iterable[Any] | None = None,
    idempotency_fields: Iterable[Any] | None = None,
    retry_policy: Mapping[str, Any] | None = None,
    concurrency_policy: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    replace: bool = False,
    persist: bool = False,
) -> Callable[
    [Callable[..., Any]],
    Callable[..., Any],
]:
    def decorator(
        handler: Callable[..., Any],
    ) -> Callable[..., Any]:
        register_runtime_handler(
            job_type=job_type,
            handler=handler,
            pipeline=pipeline,
            stage=stage,
            description=description,
            required_payload_fields=(
                required_payload_fields
            ),
            predecessor_stages=(
                predecessor_stages
            ),
            successor_stages=(
                successor_stages
            ),
            idempotency_fields=(
                idempotency_fields
            ),
            retry_policy=retry_policy,
            concurrency_policy=(
                concurrency_policy
            ),
            metadata=metadata,
            replace=replace,
            persist=persist,
        )

        return handler

    return decorator


def unregister_runtime_handler(
    job_type: str,
    *,
    persist: bool = False,
) -> dict[str, Any] | None:
    canonical_job_type = _normalize_name(
        job_type,
        field_name="job_type",
    )

    with _REGISTRY_LOCK:
        registration = (
            _RUNTIME_HANDLER_REGISTRY.pop(
                canonical_job_type,
                None,
            )
        )

        if persist:
            _persist_registry_snapshot()

    if registration is None:
        return None

    return registration.to_public_dict()


def clear_runtime_registration_memory() -> None:
    global _PERSISTED_REGISTRY_LOADED

    with _REGISTRY_LOCK:
        _RUNTIME_HANDLER_REGISTRY.clear()
        _PERSISTED_REGISTRY_LOADED = False


def load_persisted_runtime_registrations(
    *,
    force: bool = False,
) -> dict[str, Any]:
    global _PERSISTED_REGISTRY_LOADED

    with _REGISTRY_LOCK:
        if (
            _PERSISTED_REGISTRY_LOADED
            and not force
        ):
            return {
                "ok": True,
                "loaded": False,
                "reason": "already_loaded",
                "registration_count": len(
                    _RUNTIME_HANDLER_REGISTRY
                ),
            }

        if force:
            persistent_job_types = [
                job_type
                for job_type, registration
                in _RUNTIME_HANDLER_REGISTRY.items()
                if registration.persistent
            ]

            for job_type in persistent_job_types:
                _RUNTIME_HANDLER_REGISTRY.pop(
                    job_type,
                    None,
                )

        if not REGISTRY_PATH.is_file():
            _PERSISTED_REGISTRY_LOADED = True

            return {
                "ok": True,
                "loaded": True,
                "reason": "registry_file_absent",
                "registration_count": 0,
            }

        document = json.loads(
            REGISTRY_PATH.read_text(
                encoding="utf-8-sig",
            )
        )

        if not isinstance(document, dict):
            raise RuntimeError(
                "Runtime registration registry root "
                "must be a JSON object."
            )

        records = document.get(
            "registrations",
            [],
        )

        if not isinstance(records, list):
            raise RuntimeError(
                "Runtime registration records must be a list."
            )

        loaded_job_types: list[str] = []

        for record in records:
            if not isinstance(record, dict):
                raise RuntimeError(
                    "Runtime registration record must be "
                    "a JSON object."
                )

            public_record = register_runtime_handler(
                job_type=record.get(
                    "job_type",
                    "",
                ),
                handler=record.get(
                    "handler_ref",
                    "",
                ),
                pipeline=record.get(
                    "pipeline",
                    "",
                ),
                stage=record.get(
                    "stage",
                    "",
                ),
                description=record.get(
                    "description",
                    "",
                ),
                required_payload_fields=(
                    record.get(
                        "required_payload_fields",
                        [],
                    )
                ),
                predecessor_stages=(
                    record.get(
                        "predecessor_stages",
                        [],
                    )
                ),
                successor_stages=(
                    record.get(
                        "successor_stages",
                        [],
                    )
                ),
                idempotency_fields=(
                    record.get(
                        "idempotency_fields",
                        [],
                    )
                ),
                retry_policy=record.get(
                    "retry_policy",
                    {},
                ),
                concurrency_policy=(
                    record.get(
                        "concurrency_policy",
                        {},
                    )
                ),
                metadata=record.get(
                    "metadata",
                    {},
                ),
                replace=True,
                persist=False,
                _loaded_from_persistence=True,
            )

            loaded_job_types.append(
                public_record["job_type"]
            )

        _PERSISTED_REGISTRY_LOADED = True

        return {
            "ok": True,
            "loaded": True,
            "reason": "registry_loaded",
            "registration_count": len(
                loaded_job_types
            ),
            "job_types": sorted(
                loaded_job_types
            ),
        }


def ensure_persisted_runtime_registrations_loaded() -> None:
    load_persisted_runtime_registrations(
        force=False
    )


def has_runtime_handler(
    job_type: Any,
) -> bool:
    ensure_persisted_runtime_registrations_loaded()

    normalized = str(
        job_type or ""
    ).strip()

    if not normalized:
        return False

    with _REGISTRY_LOCK:
        return (
            normalized
            in _RUNTIME_HANDLER_REGISTRY
        )


def is_runtime_job_type_registered(
    job_type: Any,
) -> bool:
    return has_runtime_handler(
        job_type
    )


def get_runtime_registration(
    job_type: str,
) -> dict[str, Any] | None:
    ensure_persisted_runtime_registrations_loaded()

    canonical_job_type = _normalize_name(
        job_type,
        field_name="job_type",
    )

    with _REGISTRY_LOCK:
        registration = (
            _RUNTIME_HANDLER_REGISTRY.get(
                canonical_job_type
            )
        )

    if registration is None:
        return None

    return registration.to_public_dict()


def list_runtime_registrations() -> list[
    dict[str, Any]
]:
    ensure_persisted_runtime_registrations_loaded()

    with _REGISTRY_LOCK:
        registrations = sorted(
            _RUNTIME_HANDLER_REGISTRY.values(),
            key=lambda item: item.job_type,
        )

    return [
        registration.to_public_dict()
        for registration in registrations
    ]


def runtime_registration_snapshot() -> dict[str, Any]:
    registrations = (
        list_runtime_registrations()
    )

    canonical_json = json.dumps(
        registrations,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    return {
        "schema_version": (
            REGISTRATION_SCHEMA_VERSION
        ),
        "registration_count": len(
            registrations
        ),
        "registrations": registrations,
        "registry_sha256": hashlib.sha256(
            canonical_json.encode("utf-8")
        ).hexdigest(),
        "persistent_registry_path": str(
            REGISTRY_PATH
        ),
    }


def _validate_required_payload_fields(
    *,
    registration: RuntimeHandlerRegistration,
    payload: Mapping[str, Any],
) -> None:
    missing_fields = [
        field_name
        for field_name
        in registration.required_payload_fields
        if (
            field_name not in payload
            or payload.get(field_name) is None
            or payload.get(field_name) == ""
        )
    ]

    if missing_fields:
        raise ValueError(
            "Runtime handler payload is missing required "
            "fields: "
            + ", ".join(
                missing_fields
            )
        )


def _invoke_handler(
    handler: Callable[..., Any],
    job: Mapping[str, Any],
) -> Any:
    try:
        handler_signature = (
            inspect.signature(
                handler
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        return handler(job)

    parameters = (
        handler_signature.parameters
    )

    accepts_var_keyword = any(
        parameter.kind
        == inspect.Parameter.VAR_KEYWORD
        for parameter in parameters.values()
    )

    if (
        "job" in parameters
        or accepts_var_keyword
    ):
        return handler(
            job=job
        )

    positional_parameters = [
        parameter
        for parameter in parameters.values()
        if parameter.kind
        in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        }
    ]

    if positional_parameters:
        return handler(job)

    return handler()


def dispatch_registered_runtime_handler(
    job: Mapping[str, Any],
) -> dict[str, Any]:
    ensure_persisted_runtime_registrations_loaded()

    if not isinstance(job, Mapping):
        raise TypeError(
            "Universal runtime job must be a mapping."
        )

    job_type = str(
        job.get("job_type")
        or job.get("stage")
        or ""
    ).strip()

    if not job_type:
        raise ValueError(
            "Universal runtime job has no job_type."
        )

    with _REGISTRY_LOCK:
        registration = (
            _RUNTIME_HANDLER_REGISTRY.get(
                job_type
            )
        )

    if registration is None:
        raise ValueError(
            f"No runtime handler registered for: {job_type}"
        )

    payload = job.get(
        "payload",
        {},
    )

    if not isinstance(payload, Mapping):
        raise TypeError(
            "Universal runtime job payload must be a mapping."
        )

    _validate_required_payload_fields(
        registration=registration,
        payload=payload,
    )

    handler_result = _invoke_handler(
        registration.handler,
        job,
    )

    if handler_result is None:
        handler_result = {}

    if not isinstance(
        handler_result,
        dict,
    ):
        handler_result = {
            "value": handler_result,
        }

    return {
        "handled": True,
        "dispatch_mode": (
            "universal_runtime_registration"
        ),
        "job_type": job_type,
        "pipeline": registration.pipeline,
        "stage": registration.stage,
        "handler_ref": (
            registration.handler_ref
        ),
        "handler_result": handler_result,
    }


def execute_registered_runtime_job_v1(
    job: Mapping[str, Any],
) -> dict[str, Any]:
    from backend.server.jobs.universal_knowledge_orchestrator import (
        record_job_failure,
        update_job_progress,
        update_job_status,
    )

    workspace_id = str(
        job.get("workspace_id")
        or "default"
    ).strip() or "default"

    job_id = str(
        job.get("job_id")
        or ""
    ).strip()

    job_type = str(
        job.get("job_type")
        or job.get("stage")
        or ""
    ).strip()

    payload = job.get(
        "payload",
        {},
    )

    if not isinstance(payload, Mapping):
        payload = {}

    try:
        update_job_status(
            workspace_id=workspace_id,
            job_id=job_id,
            status="running",
            message=(
                f"Running registered runtime handler "
                f"for {job_type}."
            ),
        )

        update_job_progress(
            workspace_id=workspace_id,
            job_id=job_id,
            percent=10,
            message=(
                "Universal Runtime Registration "
                "accepted the job."
            ),
            step="runtime_registration_dispatch",
        )

        result = (
            dispatch_registered_runtime_handler(
                job
            )
        )

        update_job_progress(
            workspace_id=workspace_id,
            job_id=job_id,
            percent=100,
            message=(
                "Registered runtime handler completed."
            ),
            step="runtime_registration_completed",
        )

        update_job_status(
            workspace_id=workspace_id,
            job_id=job_id,
            status="completed",
            message=(
                "Registered runtime handler completed."
            ),
            result=result,
        )

        return {
            "ok": True,
            "job_id": job_id,
            "workspace_id": workspace_id,
            "job_type": job_type,
            "dispatch_mode": (
                "universal_runtime_registration"
            ),
            "result": result,
        }

    except Exception as exc:
        failure = record_job_failure(
            workspace_id=workspace_id,
            job_id=job_id,
            job_type=job_type,
            error=str(exc),
            payload=dict(payload),
        )

        return {
            "ok": False,
            "job_id": job_id,
            "workspace_id": workspace_id,
            "job_type": job_type,
            "dispatch_mode": (
                "universal_runtime_registration"
            ),
            "failure": failure,
        }
'''


ORCHESTRATOR_IMPORT = '''from backend.server.runtime.universal_runtime_registration import (
    get_runtime_registration,
    is_runtime_job_type_registered,
    list_runtime_registrations,
    register_runtime_handler,
    runtime_registration_snapshot,
    unregister_runtime_handler,
)
'''


ORCHESTRATOR_WRAPPERS = r'''

def register_universal_runtime_handler(
    *,
    job_type: str,
    handler: Any,
    pipeline: str = "",
    stage: str = "",
    description: str = "",
    required_payload_fields=None,
    predecessor_stages=None,
    successor_stages=None,
    idempotency_fields=None,
    retry_policy=None,
    concurrency_policy=None,
    metadata=None,
    replace: bool = False,
    persist: bool = False,
) -> Dict[str, Any]:
    """Register business logic with the Universal Runtime Infrastructure."""

    return register_runtime_handler(
        job_type=job_type,
        handler=handler,
        pipeline=pipeline,
        stage=stage,
        description=description,
        required_payload_fields=required_payload_fields,
        predecessor_stages=predecessor_stages,
        successor_stages=successor_stages,
        idempotency_fields=idempotency_fields,
        retry_policy=retry_policy,
        concurrency_policy=concurrency_policy,
        metadata=metadata,
        replace=replace,
        persist=persist,
    )


def unregister_universal_runtime_handler(
    job_type: str,
    *,
    persist: bool = False,
) -> Dict[str, Any] | None:
    return unregister_runtime_handler(
        job_type,
        persist=persist,
    )


def read_universal_runtime_registration(
    job_type: str,
) -> Dict[str, Any] | None:
    return get_runtime_registration(
        job_type
    )


def list_universal_runtime_registrations() -> List[
    Dict[str, Any]
]:
    return list_runtime_registrations()


def explain_universal_runtime_registration_v1() -> Dict[str, Any]:
    snapshot = runtime_registration_snapshot()

    return {
        "schema_version": (
            "universal_runtime_registration_explanation_v1"
        ),
        "static_supported_job_type_count": len(
            SUPPORTED_JOB_TYPES
        ),
        "static_supported_job_types": sorted(
            SUPPORTED_JOB_TYPES
        ),
        "dynamic_registration_count": snapshot[
            "registration_count"
        ],
        "dynamic_registrations": snapshot[
            "registrations"
        ],
        "registry_sha256": snapshot[
            "registry_sha256"
        ],
        "persistent_registry_path": snapshot[
            "persistent_registry_path"
        ],
        "execution_model": (
            "Registered handlers execute through the existing "
            "universal worker, queue, job-status, progress and "
            "failure contracts."
        ),
    }
'''


WORKER_EXECUTOR = r'''def execute_universal_knowledge_job_v1(
    job: Dict[str, Any],
) -> Dict[str, Any]:
    from backend.server.runtime.universal_runtime_registration import (
        ensure_persisted_runtime_registrations_loaded,
        execute_registered_runtime_job_v1,
        has_runtime_handler,
    )

    ensure_persisted_runtime_registrations_loaded()

    registered_job_type = str(
        job.get("job_type")
        or job.get("stage")
        or ""
    ).strip()

    if has_runtime_handler(
        registered_job_type
    ):
        return execute_registered_runtime_job_v1(
            job
        )

    _udare_job = job

    if (
        isinstance(_udare_job, dict)
        and str(
            _udare_job.get("job_type")
            or _udare_job.get("stage")
            or ""
        ).strip()
        == "udare_reconstruction"
    ):
        from backend.server.workers.udare_reconstruction_worker import (
            run_udare_reconstruction_job_v1,
        )

        return run_udare_reconstruction_job_v1(
            job=_udare_job,
        )

    return _execute_universal_knowledge_job_without_udare_v1(
        job
    )
'''


def replace_function(
    source: str,
    *,
    function_name: str,
    replacement: str,
) -> str:
    tree = ast.parse(source)

    target = None

    for node in tree.body:
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name == function_name
        ):
            target = node
            break

    if target is None:
        raise RuntimeError(
            f"Function not found: {function_name}"
        )

    lines = source.splitlines(
        keepends=True
    )

    start_index = target.lineno - 1
    end_index = target.end_lineno

    replacement_text = (
        replacement.rstrip()
        + "\n\n"
    )

    return "".join(
        [
            *lines[:start_index],
            replacement_text,
            *lines[end_index:],
        ]
    )


def add_orchestrator_import(
    source: str,
) -> str:
    if (
        "from backend.server.runtime."
        "universal_runtime_registration import"
        in source
    ):
        return source

    future_line = (
        "from __future__ import annotations\n"
    )

    if future_line in source:
        return source.replace(
            future_line,
            future_line
            + "\n"
            + ORCHESTRATOR_IMPORT
            + "\n",
            1,
        )

    return (
        ORCHESTRATOR_IMPORT
        + "\n"
        + source
    )


def patch_orchestrator(
    source: str,
) -> str:
    source = add_orchestrator_import(
        source
    )

    old_condition = (
        "if job_type not in SUPPORTED_JOB_TYPES:"
    )

    new_condition = (
        "if (\n"
        "        job_type not in SUPPORTED_JOB_TYPES\n"
        "        and not is_runtime_job_type_registered(job_type)\n"
        "    ):"
    )

    if new_condition not in source:
        occurrence_count = source.count(
            old_condition
        )

        if occurrence_count != 1:
            raise RuntimeError(
                "Expected exactly one static job-type "
                "validation condition; found "
                f"{occurrence_count}."
            )

        source = source.replace(
            old_condition,
            new_condition,
            1,
        )

    if (
        "def register_universal_runtime_handler("
        not in source
    ):
        source = (
            source.rstrip()
            + ORCHESTRATOR_WRAPPERS
            + "\n"
        )

    return source


def main() -> int:
    for required_path in (
        ORCHESTRATOR_PATH,
        WORKER_PATH,
    ):
        if not required_path.is_file():
            raise FileNotFoundError(
                f"Required source file missing: {required_path}"
            )

    REGISTRY_PATH.write_text(
        REGISTRY_SOURCE,
        encoding="utf-8",
    )

    orchestrator_source = (
        ORCHESTRATOR_PATH.read_text(
            encoding="utf-8-sig",
        )
    )

    patched_orchestrator = (
        patch_orchestrator(
            orchestrator_source
        )
    )

    ast.parse(
        patched_orchestrator,
        filename=str(
            ORCHESTRATOR_PATH
        ),
    )

    ORCHESTRATOR_PATH.write_text(
        patched_orchestrator,
        encoding="utf-8",
    )

    worker_source = (
        WORKER_PATH.read_text(
            encoding="utf-8-sig",
        )
    )

    patched_worker = replace_function(
        worker_source,
        function_name=(
            "execute_universal_knowledge_job_v1"
        ),
        replacement=WORKER_EXECUTOR,
    )

    ast.parse(
        patched_worker,
        filename=str(
            WORKER_PATH
        ),
    )

    WORKER_PATH.write_text(
        patched_worker,
        encoding="utf-8",
    )

    for source_path in (
        REGISTRY_PATH,
        ORCHESTRATOR_PATH,
        WORKER_PATH,
    ):
        ast.parse(
            source_path.read_text(
                encoding="utf-8-sig",
            ),
            filename=str(
                source_path
            ),
        )

    print(
        "UNIVERSAL RUNTIME REGISTRATION "
        "SOURCE PATCH: PASS"
    )

    print(
        "Created:",
        REGISTRY_PATH,
    )

    print(
        "Patched:",
        ORCHESTRATOR_PATH,
    )

    print(
        "Patched:",
        WORKER_PATH,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
