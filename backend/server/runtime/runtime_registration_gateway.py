"""Canonical Runtime Registration boot gateway.

This module does not create a second registration registry. It exposes
the existing Universal Runtime Registration authority to runtime boot,
the kernel and application-lifespan evidence.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.runtime_registration_admission import (
    bind_runtime_registration_admission,
)

from backend.server.runtime.universal_runtime_registration import (
    ensure_persisted_runtime_registrations_loaded,
    runtime_registration_snapshot,
)


RUNTIME_REGISTRATION_GATEWAY_KEY = "runtime_registration"


class RuntimeRegistrationGateway:
    """Read-only boot gateway for the canonical registration authority."""

    __slots__ = ()

    def snapshot(self) -> Mapping[str, Any]:
        ensure_persisted_runtime_registrations_loaded()

        return MappingProxyType(
            dict(runtime_registration_snapshot())
        )

    def evidence(self) -> Mapping[str, Any]:
        snapshot = self.snapshot()

        return MappingProxyType(
            {
                "schema_version": snapshot.get("schema_version"),
                "registration_count": snapshot.get(
                    "registration_count",
                    0,
                ),
                "registry_sha256": snapshot.get("registry_sha256"),
                "persistent_registry_path": snapshot.get(
                    "persistent_registry_path"
                ),
            }
        )


def register_runtime_registration_gateway(
    composition: Any,
) -> RuntimeRegistrationGateway:
    """Activate and bind the canonical registration authority at boot."""

    kernel = getattr(composition, "kernel", None)

    if kernel is None:
        raise RuntimeError(
            "Runtime registration gateway requires a boot composition "
            "with a kernel."
        )

    if kernel.has_component(RUNTIME_REGISTRATION_GATEWAY_KEY):
        raise RuntimeError(
            "Runtime registration gateway is already bound to the kernel."
        )

    ensure_persisted_runtime_registrations_loaded()

    bind_runtime_registration_admission(
        configuration=composition.configuration,
        kernel=kernel,
    )

    gateway = RuntimeRegistrationGateway()

    kernel.bind_component(
        RUNTIME_REGISTRATION_GATEWAY_KEY,
        gateway,
    )

    return gateway


__all__ = [
    "RUNTIME_REGISTRATION_GATEWAY_KEY",
    "RuntimeRegistrationGateway",
    "register_runtime_registration_gateway",
]
