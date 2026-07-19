from __future__ import annotations

"""
Universal Runtime Kernel.

This module is the business-logic-agnostic composition root for the
Universal Runtime Infrastructure.

The kernel does not execute product pipelines, queue jobs, or worker
business logic. It coordinates runtime foundation components through
explicit bindings and guarded state transitions.
"""

import re
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, TypeVar, cast


__all__ = [
    "FOUNDATION_COMPONENT_KEYS",
    "KernelComponentBinding",
    "RuntimeKernelBindingError",
    "RuntimeKernelError",
    "RuntimeKernelMissingComponentError",
    "RuntimeKernelSnapshot",
    "RuntimeKernelState",
    "RuntimeKernelStateError",
    "UniversalRuntimeKernel",
]


T = TypeVar("T")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _qualified_type_name(value: object) -> str:
    value_type = type(value)
    return (
        f"{value_type.__module__}."
        f"{value_type.__qualname__}"
    )


class RuntimeKernelError(RuntimeError):
    """Base exception for Universal Runtime Kernel failures."""


class RuntimeKernelBindingError(RuntimeKernelError):
    """Raised when a kernel component binding is invalid."""


class RuntimeKernelMissingComponentError(RuntimeKernelError):
    """Raised when a required kernel component is unavailable."""


class RuntimeKernelStateError(RuntimeKernelError):
    """Raised when a kernel state transition is invalid."""


class RuntimeKernelState(str, Enum):
    """
    High-level kernel lifecycle states.

    Detailed boot, readiness, draining, and shutdown orchestration will
    be owned by the Runtime Lifecycle Manager. The kernel enforces the
    legal state boundary.
    """

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    DRAINING = "draining"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


FOUNDATION_COMPONENT_KEYS: tuple[str, ...] = (
    "configuration",
    "environment",
    "service_registry",
    "lifecycle_manager",
    "persistence",
    "state_store",
    "schema_manager",
)


_ALLOWED_TRANSITIONS: Mapping[
    RuntimeKernelState,
    frozenset[RuntimeKernelState],
] = MappingProxyType(
    {
        RuntimeKernelState.CREATED: frozenset(
            {
                RuntimeKernelState.INITIALIZING,
                RuntimeKernelState.FAILED,
            }
        ),
        RuntimeKernelState.INITIALIZING: frozenset(
            {
                RuntimeKernelState.READY,
                RuntimeKernelState.FAILED,
                RuntimeKernelState.STOPPING,
            }
        ),
        RuntimeKernelState.READY: frozenset(
            {
                RuntimeKernelState.RUNNING,
                RuntimeKernelState.STOPPING,
                RuntimeKernelState.FAILED,
            }
        ),
        RuntimeKernelState.RUNNING: frozenset(
            {
                RuntimeKernelState.DRAINING,
                RuntimeKernelState.STOPPING,
                RuntimeKernelState.FAILED,
            }
        ),
        RuntimeKernelState.DRAINING: frozenset(
            {
                RuntimeKernelState.RUNNING,
                RuntimeKernelState.STOPPING,
                RuntimeKernelState.FAILED,
            }
        ),
        RuntimeKernelState.STOPPING: frozenset(
            {
                RuntimeKernelState.STOPPED,
                RuntimeKernelState.FAILED,
            }
        ),
        RuntimeKernelState.STOPPED: frozenset(),
        RuntimeKernelState.FAILED: frozenset(
            {
                RuntimeKernelState.STOPPING,
                RuntimeKernelState.STOPPED,
            }
        ),
    }
)


_RUNTIME_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.:-]{2,127}$"
)

_COMPONENT_KEY_PATTERN = re.compile(
    r"^[a-z][a-z0-9_.-]{1,127}$"
)


@dataclass(frozen=True, slots=True)
class KernelComponentBinding:
    """
    Immutable description of one component bound to the kernel.

    The component object itself is intentionally excluded from snapshots
    so runtime inspection cannot accidentally expose internal objects.
    """

    key: str
    component_type: str
    bound_at: datetime
    generation: int


@dataclass(frozen=True, slots=True)
class RuntimeKernelSnapshot:
    """Immutable point-in-time kernel inspection record."""

    runtime_id: str
    product_name: str
    state: RuntimeKernelState
    generation: int
    created_at: datetime
    updated_at: datetime
    component_count: int
    components: tuple[KernelComponentBinding, ...]
    missing_foundation_components: tuple[str, ...]
    failure_reason: str | None


class UniversalRuntimeKernel:
    """
    Central composition root for the Universal Runtime Infrastructure.

    Responsibilities:

    - Own the runtime identity.
    - Hold references to runtime foundation components.
    - Prevent accidental duplicate component bindings.
    - Enforce legal high-level lifecycle transitions.
    - Provide immutable runtime inspection snapshots.
    - Remain independent from pipeline and product business logic.

    Non-responsibilities:

    - Executing queue jobs.
    - Running workers.
    - Implementing pipeline stages.
    - Persisting runtime records directly.
    - Loading environment configuration directly.
    """

    __slots__ = (
        "_runtime_id",
        "_product_name",
        "_state",
        "_generation",
        "_created_at",
        "_updated_at",
        "_components",
        "_bindings",
        "_failure_reason",
        "_lock",
    )

    def __init__(
        self,
        *,
        runtime_id: str,
        product_name: str,
    ) -> None:
        normalized_runtime_id = str(runtime_id or "").strip()
        normalized_product_name = str(product_name or "").strip()

        if not _RUNTIME_ID_PATTERN.fullmatch(
            normalized_runtime_id
        ):
            raise ValueError(
                "runtime_id must be 3-128 characters and contain "
                "only letters, numbers, dots, underscores, colons, "
                "or hyphens."
            )

        if not normalized_product_name:
            raise ValueError(
                "product_name must not be empty."
            )

        now = _utc_now()

        self._runtime_id = normalized_runtime_id
        self._product_name = normalized_product_name
        self._state = RuntimeKernelState.CREATED
        self._generation = 0
        self._created_at = now
        self._updated_at = now
        self._components: dict[str, object] = {}
        self._bindings: dict[
            str,
            KernelComponentBinding,
        ] = {}
        self._failure_reason: str | None = None
        self._lock = threading.RLock()

    @staticmethod
    def normalize_component_key(
        component_key: str,
    ) -> str:
        key = str(component_key or "").strip().lower()

        if not _COMPONENT_KEY_PATTERN.fullmatch(key):
            raise RuntimeKernelBindingError(
                "component_key must be 2-128 characters, begin "
                "with a lowercase letter, and contain only "
                "lowercase letters, numbers, dots, underscores, "
                "or hyphens."
            )

        return key

    @staticmethod
    def coerce_state(
        state: RuntimeKernelState | str,
    ) -> RuntimeKernelState:
        if isinstance(state, RuntimeKernelState):
            return state

        try:
            return RuntimeKernelState(
                str(state or "").strip().lower()
            )
        except ValueError as exc:
            raise RuntimeKernelStateError(
                f"Unknown runtime kernel state: {state!r}"
            ) from exc

    @property
    def runtime_id(self) -> str:
        return self._runtime_id

    @property
    def product_name(self) -> str:
        return self._product_name

    @property
    def state(self) -> RuntimeKernelState:
        with self._lock:
            return self._state

    @property
    def generation(self) -> int:
        with self._lock:
            return self._generation

    @property
    def component_count(self) -> int:
        with self._lock:
            return len(self._components)

    def _assert_mutable(self) -> None:
        if self._state in {
            RuntimeKernelState.STOPPING,
            RuntimeKernelState.STOPPED,
        }:
            raise RuntimeKernelStateError(
                "Kernel component bindings cannot be changed while "
                f"the runtime is {self._state.value!r}."
            )

    def _record_mutation(self) -> int:
        self._generation += 1
        self._updated_at = _utc_now()
        return self._generation

    def bind_component(
        self,
        component_key: str,
        component: object,
        *,
        replace: bool = False,
    ) -> KernelComponentBinding:
        """
        Bind one foundation component to the kernel.

        Components are stored by explicit logical key. Duplicate
        replacement is prohibited unless replace=True is supplied.
        """

        key = self.normalize_component_key(
            component_key
        )

        if component is None:
            raise RuntimeKernelBindingError(
                "A kernel component cannot be None."
            )

        with self._lock:
            self._assert_mutable()

            if key in self._components and not replace:
                raise RuntimeKernelBindingError(
                    f"Kernel component {key!r} is already bound."
                )

            generation = self._record_mutation()

            binding = KernelComponentBinding(
                key=key,
                component_type=_qualified_type_name(
                    component
                ),
                bound_at=self._updated_at,
                generation=generation,
            )

            self._components[key] = component
            self._bindings[key] = binding

            return binding

    def unbind_component(
        self,
        component_key: str,
    ) -> object:
        """Remove and return one bound component."""

        key = self.normalize_component_key(
            component_key
        )

        with self._lock:
            self._assert_mutable()

            if key not in self._components:
                raise RuntimeKernelMissingComponentError(
                    f"Kernel component {key!r} is not bound."
                )

            component = self._components.pop(key)
            self._bindings.pop(key, None)
            self._record_mutation()

            return component

    def has_component(
        self,
        component_key: str,
    ) -> bool:
        key = self.normalize_component_key(
            component_key
        )

        with self._lock:
            return key in self._components

    def get_component(
        self,
        component_key: str,
        expected_type: type[T] | None = None,
    ) -> T | object:
        """
        Retrieve a bound component.

        expected_type may be supplied to protect consumers against an
        incompatible binding.
        """

        key = self.normalize_component_key(
            component_key
        )

        with self._lock:
            if key not in self._components:
                raise RuntimeKernelMissingComponentError(
                    f"Kernel component {key!r} is not bound."
                )

            component = self._components[key]

        if (
            expected_type is not None
            and not isinstance(component, expected_type)
        ):
            raise RuntimeKernelBindingError(
                f"Kernel component {key!r} has type "
                f"{_qualified_type_name(component)!r}, not "
                f"{expected_type.__module__}."
                f"{expected_type.__qualname__!s}."
            )

        if expected_type is not None:
            return cast(T, component)

        return component

    def require_components(
        self,
        component_keys: tuple[str, ...] | list[str],
    ) -> Mapping[str, object]:
        """
        Return a read-only mapping of required components.

        The operation fails atomically when any requested component is
        missing.
        """

        normalized_keys = tuple(
            self.normalize_component_key(key)
            for key in component_keys
        )

        with self._lock:
            missing = tuple(
                key
                for key in normalized_keys
                if key not in self._components
            )

            if missing:
                raise RuntimeKernelMissingComponentError(
                    "Missing required kernel components: "
                    + ", ".join(missing)
                )

            selected = {
                key: self._components[key]
                for key in normalized_keys
            }

        return MappingProxyType(selected)

    def missing_foundation_components(
        self,
    ) -> tuple[str, ...]:
        with self._lock:
            return tuple(
                key
                for key in FOUNDATION_COMPONENT_KEYS
                if key not in self._components
            )

    def transition_state(
        self,
        *,
        expected_state: RuntimeKernelState | str,
        target_state: RuntimeKernelState | str,
        reason: str | None = None,
    ) -> RuntimeKernelState:
        """
        Perform one guarded kernel state transition.

        expected_state provides optimistic concurrency protection and
        prevents stale lifecycle actors from applying invalid changes.
        """

        expected = self.coerce_state(
            expected_state
        )
        target = self.coerce_state(
            target_state
        )

        with self._lock:
            if self._state is not expected:
                raise RuntimeKernelStateError(
                    "Kernel state transition rejected: expected "
                    f"{expected.value!r}, found "
                    f"{self._state.value!r}."
                )

            allowed = _ALLOWED_TRANSITIONS[
                self._state
            ]

            if target not in allowed:
                raise RuntimeKernelStateError(
                    "Illegal kernel state transition: "
                    f"{self._state.value!r} -> "
                    f"{target.value!r}."
                )

            self._state = target

            if target is RuntimeKernelState.FAILED:
                normalized_reason = str(
                    reason or "unspecified runtime failure"
                ).strip()

                self._failure_reason = (
                    normalized_reason
                    or "unspecified runtime failure"
                )

            self._record_mutation()

            return self._state

    def mark_failed(
        self,
        reason: str,
    ) -> RuntimeKernelState:
        normalized_reason = str(reason or "").strip()

        if not normalized_reason:
            raise ValueError(
                "A failure reason is required."
            )

        with self._lock:
            if self._state in {
                RuntimeKernelState.STOPPED,
                RuntimeKernelState.FAILED,
            }:
                raise RuntimeKernelStateError(
                    "A stopped or failed kernel cannot be marked "
                    "failed again."
                )

            if (
                RuntimeKernelState.FAILED
                not in _ALLOWED_TRANSITIONS[self._state]
            ):
                raise RuntimeKernelStateError(
                    "The current kernel state cannot transition "
                    "to failed."
                )

            current_state = self._state

        return self.transition_state(
            expected_state=current_state,
            target_state=RuntimeKernelState.FAILED,
            reason=normalized_reason,
        )

    def snapshot(self) -> RuntimeKernelSnapshot:
        """Return an immutable kernel inspection snapshot."""

        with self._lock:
            components = tuple(
                self._bindings[key]
                for key in sorted(self._bindings)
            )

            missing = tuple(
                key
                for key in FOUNDATION_COMPONENT_KEYS
                if key not in self._components
            )

            return RuntimeKernelSnapshot(
                runtime_id=self._runtime_id,
                product_name=self._product_name,
                state=self._state,
                generation=self._generation,
                created_at=self._created_at,
                updated_at=self._updated_at,
                component_count=len(self._components),
                components=components,
                missing_foundation_components=missing,
                failure_reason=self._failure_reason,
            )
