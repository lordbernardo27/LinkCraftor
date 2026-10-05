from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Mapping

from backend.server.runtime.runtime_boot_process import (
    boot_runtime,
)
from backend.server.runtime.runtime_shutdown_process import (
    shutdown_runtime,
)


RUNTIME_APPLICATION_LIFECYCLE_VERSION = (
    "runtime_application_lifecycle_v1"
)


class RuntimeApplicationLifecycleError(RuntimeError):
    pass


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _record_mapping(value: Any) -> dict[str, Any]:
    """Convert record containers without copying live runtime services.

    This is an in-process evidence mapping, not a JSON serializer.
    Opaque service references remain references.
    """
    from dataclasses import fields, is_dataclass
    from collections.abc import Mapping

    active = set()

    def convert(item):
        record = is_dataclass(item) and not isinstance(item, type)
        container = record or isinstance(item, (Mapping, list, tuple))
        if not container:
            return item
        identity = id(item)
        if identity in active:
            raise RuntimeApplicationLifecycleError("Cyclic evidence container.")
        active.add(identity)
        try:
            if record:
                return {field.name: convert(getattr(item, field.name))
                        for field in fields(item)}
            if isinstance(item, Mapping):
                return {key: convert(child) for key, child in item.items()}
            if isinstance(item, tuple):
                return tuple(convert(child) for child in item)
            return [convert(child) for child in item]
        finally:
            active.remove(identity)

    if ((is_dataclass(value) and not isinstance(value, type))
            or isinstance(value, Mapping)):
        return convert(value)

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        converted = to_dict()
        if not isinstance(converted, Mapping):
            raise RuntimeApplicationLifecycleError(
                "Lifecycle to_dict() result must be a mapping.")
        return convert(converted)

    attributes = getattr(value, "__dict__", None)
    if isinstance(attributes, dict):
        return convert({key: child for key, child in attributes.items()
                        if not key.startswith("_")})

    raise RuntimeApplicationLifecycleError(
        "Lifecycle evidence is not serializable.")



from backend.server.runtime.runtime_feature_flag_gateway import (
    GATEWAY_KEY,
    RuntimeFeatureFlagGateway,
    register_runtime_feature_flag_gateway,
)
from backend.server.runtime.runtime_boot_process import (
    RUNTIME_COMPATIBILITY_COMPONENT_KEY,
    RUNTIME_COMPATIBILITY_REPORT_COMPONENT_KEY,
    RUNTIME_VERSION_MANAGER_COMPONENT_KEY,
)
from backend.server.runtime.runtime_compatibility import (
    RuntimeCompatibilityLayer,
    RuntimeCompatibilityReport,
)
from backend.server.runtime.runtime_versioning import (
    RuntimeVersionManager,
)

@asynccontextmanager
async def linkcraftor_runtime_lifespan(
    application: Any,
) -> AsyncIterator[None]:
    application.state.runtime_lifecycle_version = (
        RUNTIME_APPLICATION_LIFECYCLE_VERSION
    )
    application.state.runtime_lifecycle_status = "BOOTING"

    try:
        boot_process, boot_context = await boot_runtime(project_root=_project_root(), service_registrars=(register_runtime_feature_flag_gateway,))

    except Exception as exc:
        application.state.runtime_lifecycle_status = (
            "BOOT_FAILED"
        )
        application.state.runtime_boot_failure = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
        raise

    feature_flag_gateway = boot_context.kernel.get_component(
        GATEWAY_KEY, RuntimeFeatureFlagGateway
    )
    application.state.runtime_feature_flag_gateway = feature_flag_gateway
    application.state.runtime_feature_flag_evidence = feature_flag_gateway.evidence()
    application.state.runtime_feature_flag_snapshot = _record_mapping(
        feature_flag_gateway.snapshot()
    )

    runtime_version_manager = (
        boot_context.kernel.get_component(
            RUNTIME_VERSION_MANAGER_COMPONENT_KEY,
            RuntimeVersionManager,
        )
    )

    runtime_compatibility = (
        boot_context.kernel.get_component(
            RUNTIME_COMPATIBILITY_COMPONENT_KEY,
            RuntimeCompatibilityLayer,
        )
    )

    runtime_compatibility_report = (
        boot_context.kernel.get_component(
            RUNTIME_COMPATIBILITY_REPORT_COMPONENT_KEY,
            RuntimeCompatibilityReport,
        )
    )

    application.state.runtime_version_manifest = (
        _record_mapping(
            runtime_version_manager
            .manifest
            .to_dict()
        )
    )

    application.state.runtime_version_snapshot = (
        _record_mapping(
            runtime_version_manager.snapshot()
        )
    )

    application.state.runtime_compatibility_report = (
        _record_mapping(
            runtime_compatibility_report
        )
    )

    application.state.runtime_compatibility_snapshot = (
        _record_mapping(
            runtime_compatibility.snapshot()
        )
    )

    application.state.runtime_boot_process = boot_process
    application.state.runtime_boot_context = boot_context
    application.state.runtime_boot_evidence = (
        _record_mapping(boot_context)
    )
    application.state.runtime_lifecycle_status = "RUNNING"

    try:
        yield

    finally:
        application.state.runtime_lifecycle_status = (
            "SHUTTING_DOWN"
        )

        try:
            (
                shutdown_process,
                shutdown_context,
            ) = await shutdown_runtime(
                boot_process=boot_process,
                drain_before_stop=True,
                timeout_seconds=None,
                raise_on_failure=True,
            )

        except Exception as exc:
            application.state.runtime_lifecycle_status = (
                "SHUTDOWN_FAILED"
            )
            application.state.runtime_shutdown_failure = {
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            raise

        application.state.runtime_shutdown_process = (
            shutdown_process
        )
        application.state.runtime_shutdown_context = (
            shutdown_context
        )
        application.state.runtime_shutdown_evidence = (
            _record_mapping(shutdown_context)
        )
        application.state.runtime_shutdown_snapshot = (
            _record_mapping(
                shutdown_process.snapshot()
            )
        )
        application.state.runtime_lifecycle_status = "STOPPED"
