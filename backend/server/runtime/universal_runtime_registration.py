"""Universal Runtime Registration.

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

from backend.server.runtime.runtime_registration_package import (
    RuntimeRegistrationPackage,
    create_runtime_registration_package,
)


LEGACY_REGISTRATION_SCHEMA_VERSION = (
    "universal_runtime_registration_v1"
)

REGISTRATION_SCHEMA_VERSION = (
    "universal_runtime_registration_v2"
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
    required_worker_capabilities: Iterable[Any] | None = None,
    predecessor_stages: Iterable[Any] | None = None,
    successor_stages: Iterable[Any] | None = None,
    idempotency_fields: Iterable[Any] | None = None,
    retry_policy: Mapping[str, Any] | None = None,
    concurrency_policy: Mapping[str, Any] | None = None,
    lifecycle_policy: Mapping[str, Any] | None = None,
    configuration_requirements: Mapping[str, Any] | None = None,
    feature_flag_key: str | None = None,
    runtime_version_requirements: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    replace: bool = False,
    persist: bool = False,
    _loaded_from_persistence: bool = False,
    _registered_at: str = "",
    _registration_fingerprint: str | None = None,
    _persistent: bool | None = None,
) -> dict[str, Any]:
    """
    Register one handler through the canonical package factory.

    Complete persistence rehydration remains in A2.2-I.
    """

    canonical_job_type = _normalize_name(
        job_type,
        field_name="job_type",
    )

    canonical_pipeline = _normalize_optional_name(
        pipeline,
        fallback="universal_knowledge",
        field_name="pipeline",
    )

    canonical_stage = _normalize_optional_name(
        stage,
        fallback=canonical_job_type,
        field_name="stage",
    )

    resolved_handler, handler_ref = _resolve_handler(
        handler
    )

    if (
        persist
        and "<locals>" in handler_ref
    ):
        raise ValueError(
            "Persistent handlers must be importable top-level "
            "functions."
        )

    if (
        _persistent is not None
        and not isinstance(_persistent, bool)
    ):
        raise TypeError(
            "_persistent must be a Boolean or None."
        )

    persistent = bool(
        _persistent
        if _persistent is not None
        else (
            persist
            or _loaded_from_persistence
        )
    )

    canonical_registered_at = (
        str(_registered_at or "").strip()
        or utc_now()
    )

    registration = create_runtime_registration_package(
        job_type=canonical_job_type,
        handler_ref=handler_ref,
        handler=resolved_handler,
        pipeline=canonical_pipeline,
        stage=canonical_stage,
        description=description,
        required_payload_fields=(
            required_payload_fields
        ),
        required_worker_capabilities=(
            required_worker_capabilities
        ),
        predecessor_stages=predecessor_stages,
        successor_stages=successor_stages,
        idempotency_fields=idempotency_fields,
        retry_policy=retry_policy,
        concurrency_policy=concurrency_policy,
        lifecycle_policy=lifecycle_policy,
        configuration_requirements=(
            configuration_requirements
        ),
        feature_flag_key=feature_flag_key,
        runtime_version_requirements=(
            runtime_version_requirements
        ),
        metadata=metadata,
        persistent=persistent,
        registered_at=canonical_registered_at,
        registration_fingerprint=(
            _registration_fingerprint
        ),
    )

    with _REGISTRY_LOCK:
        existing = _RUNTIME_HANDLER_REGISTRY.get(
            canonical_job_type
        )

        if (
            existing is not None
            and not replace
        ):
            raise ValueError(
                "Runtime handler already registered for "
                f"job_type: {canonical_job_type}"
            )

        had_existing = existing is not None

        _RUNTIME_HANDLER_REGISTRY[
            canonical_job_type
        ] = registration

        if persist:
            try:
                _persist_registry_snapshot()
            except Exception:
                if had_existing:
                    _RUNTIME_HANDLER_REGISTRY[
                        canonical_job_type
                    ] = existing
                else:
                    _RUNTIME_HANDLER_REGISTRY.pop(
                        canonical_job_type,
                        None,
                    )

                raise

    return registration.to_public_dict()


def runtime_handler(
    *,
    job_type: str,
    pipeline: str = "",
    stage: str = "",
    description: str = "",
    required_payload_fields: Iterable[Any] | None = None,
    required_worker_capabilities: Iterable[Any] | None = None,
    predecessor_stages: Iterable[Any] | None = None,
    successor_stages: Iterable[Any] | None = None,
    idempotency_fields: Iterable[Any] | None = None,
    retry_policy: Mapping[str, Any] | None = None,
    concurrency_policy: Mapping[str, Any] | None = None,
    lifecycle_policy: Mapping[str, Any] | None = None,
    configuration_requirements: Mapping[str, Any] | None = None,
    feature_flag_key: str | None = None,
    runtime_version_requirements: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    replace: bool = False,
    persist: bool = False,
) -> Callable[
    [Callable[..., Any]],
    Callable[..., Any],
]:
    """
    Declare and register a handler using the full package contract.
    """

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
            required_worker_capabilities=(
                required_worker_capabilities
            ),
            predecessor_stages=predecessor_stages,
            successor_stages=successor_stages,
            idempotency_fields=idempotency_fields,
            retry_policy=retry_policy,
            concurrency_policy=concurrency_policy,
            lifecycle_policy=lifecycle_policy,
            configuration_requirements=(
                configuration_requirements
            ),
            feature_flag_key=feature_flag_key,
            runtime_version_requirements=(
                runtime_version_requirements
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
            try:
                _persist_registry_snapshot()
            except Exception:
                if registration is not None:
                    _RUNTIME_HANDLER_REGISTRY[
                        canonical_job_type
                    ] = registration

                raise

    if registration is None:
        return None

    return registration.to_public_dict()


def clear_runtime_registration_memory() -> None:
    global _PERSISTED_REGISTRY_LOADED

    with _REGISTRY_LOCK:
        _RUNTIME_HANDLER_REGISTRY.clear()
        _PERSISTED_REGISTRY_LOADED = False


def _registration_from_persisted_record(
    *,
    record: Mapping[str, Any],
    document_schema: str,
) -> RuntimeRegistrationPackage:
    """
    Construct one persisted package without mutating registry state.
    """

    if not isinstance(record, Mapping):
        raise RuntimeError(
            "Runtime registration record must be a JSON object."
        )

    canonical_job_type = _normalize_name(
        record.get("job_type", ""),
        field_name="job_type",
    )

    canonical_pipeline = _normalize_optional_name(
        record.get("pipeline", ""),
        fallback="universal_knowledge",
        field_name="pipeline",
    )

    canonical_stage = _normalize_optional_name(
        record.get("stage", ""),
        fallback=canonical_job_type,
        field_name="stage",
    )

    handler_reference = str(
        record.get("handler_ref", "")
        or ""
    ).strip()

    resolved_handler, resolved_reference = _resolve_handler(
        handler_reference
    )

    if resolved_reference != handler_reference:
        raise RuntimeError(
            "Persisted handler reference changed during resolution."
        )

    persisted_fingerprint: str | None = None

    if document_schema == REGISTRATION_SCHEMA_VERSION:
        persisted_fingerprint = str(
            record.get(
                "registration_fingerprint",
                "",
            )
            or ""
        ).strip()

        if not persisted_fingerprint:
            raise RuntimeError(
                "Schema-v2 registration records require "
                "registration_fingerprint."
            )

    return create_runtime_registration_package(
        job_type=canonical_job_type,
        handler_ref=resolved_reference,
        handler=resolved_handler,
        pipeline=canonical_pipeline,
        stage=canonical_stage,
        description=record.get(
            "description",
            "",
        ),
        required_payload_fields=record.get(
            "required_payload_fields",
            [],
        ),
        required_worker_capabilities=record.get(
            "required_worker_capabilities",
            [],
        ),
        predecessor_stages=record.get(
            "predecessor_stages",
            [],
        ),
        successor_stages=record.get(
            "successor_stages",
            [],
        ),
        idempotency_fields=record.get(
            "idempotency_fields",
            [],
        ),
        retry_policy=record.get(
            "retry_policy",
            {},
        ),
        concurrency_policy=record.get(
            "concurrency_policy",
            {},
        ),
        lifecycle_policy=record.get(
            "lifecycle_policy",
            {},
        ),
        configuration_requirements=record.get(
            "configuration_requirements",
            {},
        ),
        feature_flag_key=record.get(
            "feature_flag_key",
            None,
        ),
        runtime_version_requirements=record.get(
            "runtime_version_requirements",
            {},
        ),
        metadata=record.get(
            "metadata",
            {},
        ),
        persistent=True,
        registered_at=record.get(
            "registered_at",
            "",
        ),
        registration_fingerprint=(
            persisted_fingerprint
        ),
    )


def load_persisted_runtime_registrations(
    *,
    force: bool = False,
) -> dict[str, Any]:
    """
    Load registry evidence atomically.

    Every record is validated and reconstructed before live registry
    state is replaced.
    """

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

        document_schema = str(
            document.get(
                "schema_version",
                "",
            )
            or ""
        ).strip()

        if document_schema not in {
            LEGACY_REGISTRATION_SCHEMA_VERSION,
            REGISTRATION_SCHEMA_VERSION,
        }:
            raise RuntimeError(
                "Unsupported runtime registration schema: "
                f"{document_schema!r}."
            )

        records = document.get(
            "registrations",
            [],
        )

        if not isinstance(records, list):
            raise RuntimeError(
                "Runtime registration records must be a list."
            )

        declared_count = document.get(
            "registration_count",
            len(records),
        )

        if (
            not isinstance(declared_count, int)
            or isinstance(declared_count, bool)
            or declared_count != len(records)
        ):
            raise RuntimeError(
                "Runtime registration_count does not match "
                "the registration records."
            )

        loaded_records: dict[
            str,
            RuntimeRegistrationPackage,
        ] = {}

        for record in records:
            registration = (
                _registration_from_persisted_record(
                    record=record,
                    document_schema=document_schema,
                )
            )

            if registration.job_type in loaded_records:
                raise RuntimeError(
                    "Duplicate persisted runtime registration: "
                    f"{registration.job_type}"
                )

            loaded_records[
                registration.job_type
            ] = registration

        # Mutation starts only after every record has passed.
        staged_registry = dict(
            _RUNTIME_HANDLER_REGISTRY
        )

        if force:
            staged_registry = {
                job_type: registration
                for job_type, registration
                in staged_registry.items()
                if not registration.persistent
            }

        staged_registry.update(
            loaded_records
        )

        _RUNTIME_HANDLER_REGISTRY.clear()
        _RUNTIME_HANDLER_REGISTRY.update(
            staged_registry
        )

        _PERSISTED_REGISTRY_LOADED = True

        return {
            "ok": True,
            "loaded": True,
            "reason": "registry_loaded",
            "schema_version": document_schema,
            "registration_count": len(
                loaded_records
            ),
            "job_types": sorted(
                loaded_records
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

    # Preserve the canonical legacy job-aware contract.
    if "job" in parameters:
        return handler(
            job=job
        )

    payload = job.get(
        "payload",
        {},
    )

    if not isinstance(
        payload,
        Mapping,
    ):
        raise TypeError(
            "Universal runtime job payload must be a mapping."
        )

    keyword_parameter_names = {
        name
        for name, parameter in parameters.items()
        if parameter.kind
        in {
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        }
    }

    keyword_only_parameters = [
        parameter
        for parameter in parameters.values()
        if parameter.kind
        == inspect.Parameter.KEYWORD_ONLY
    ]

    payload_arguments = {
        name: payload[name]
        for name in keyword_parameter_names
        if name in payload
    }

    # Registered stage handlers consume canonical payload fields
    # through named positional-or-keyword or keyword-only parameters.
    if (
        payload_arguments
        or keyword_only_parameters
    ):
        if accepts_var_keyword:
            payload_arguments.update(
                {
                    name: value
                    for name, value in payload.items()
                    if name not in payload_arguments
                }
            )

        return handler(
            **payload_arguments
        )

    # Preserve handlers whose only declared contract is **kwargs.
    if accepts_var_keyword:
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

    # Preserve legacy unnamed single-job positional handlers.
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
