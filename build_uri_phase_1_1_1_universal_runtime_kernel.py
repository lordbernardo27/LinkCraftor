from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import py_compile
import shutil
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BUILD_VERSION = "uri_phase_1_1_1_universal_runtime_kernel_v1"

PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_runtime_kernel.py"
)

EXISTING_RUNTIME_FACADE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_runtime_infrastructure.py"
)

MAIN_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "main.py"
)

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"uri_phase1_1_1_kernel_{TIMESTAMP}"
)

BACKUP_TARGET = (
    BACKUP_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_runtime_kernel.py"
)

EVIDENCE_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_1_universal_runtime_kernel"
)

EVIDENCE_JSON = (
    EVIDENCE_ROOT
    / f"kernel_build_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_ROOT
    / f"kernel_build_{TIMESTAMP}.txt"
)


KERNEL_SOURCE = r'''from __future__ import annotations

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
'''


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None

    return sha256_bytes(path.read_bytes())


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_kernel_module(path: Path) -> Any:
    module_name = (
        "_uri_phase_1_1_1_universal_runtime_kernel_test"
    )

    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )

    if spec is None or spec.loader is None:
        fail(
            "Could not create an import specification "
            "for the kernel module."
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)

    return module


def verify_ast_contract(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))

    classes: dict[str, set[str]] = {}

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        methods = {
            child.name
            for child in node.body
            if isinstance(
                child,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
        }

        classes[node.name] = methods

    required_classes = {
        "UniversalRuntimeKernel",
        "RuntimeKernelState",
        "RuntimeKernelSnapshot",
        "KernelComponentBinding",
        "RuntimeKernelError",
        "RuntimeKernelBindingError",
        "RuntimeKernelMissingComponentError",
        "RuntimeKernelStateError",
    }

    missing_classes = sorted(
        required_classes - set(classes)
    )

    required_kernel_methods = {
        "bind_component",
        "unbind_component",
        "has_component",
        "get_component",
        "require_components",
        "missing_foundation_components",
        "transition_state",
        "mark_failed",
        "snapshot",
    }

    kernel_methods = classes.get(
        "UniversalRuntimeKernel",
        set(),
    )

    missing_methods = sorted(
        required_kernel_methods - kernel_methods
    )

    if missing_classes:
        fail(
            "Kernel AST contract is missing classes: "
            + ", ".join(missing_classes)
        )

    if missing_methods:
        fail(
            "Kernel AST contract is missing methods: "
            + ", ".join(missing_methods)
        )

    forbidden_business_terms = (
        "udare",
        "website_article_integrity",
        "article_validation",
        "semantic_intelligence",
        "uploaded_document_unified_content",
        "universal_unified_content_document",
    )

    source_lower = text.lower()

    detected_forbidden_terms = [
        term
        for term in forbidden_business_terms
        if term in source_lower
    ]

    if detected_forbidden_terms:
        fail(
            "The kernel contains pipeline-specific business terms: "
            + ", ".join(detected_forbidden_terms)
        )

    return {
        "required_classes": sorted(required_classes),
        "missing_classes": missing_classes,
        "required_kernel_methods": sorted(
            required_kernel_methods
        ),
        "missing_kernel_methods": missing_methods,
        "pipeline_business_terms_detected": (
            detected_forbidden_terms
        ),
    }


def verify_runtime_behavior(module: Any) -> dict[str, Any]:
    Kernel = module.UniversalRuntimeKernel
    State = module.RuntimeKernelState

    BindingError = module.RuntimeKernelBindingError
    MissingError = (
        module.RuntimeKernelMissingComponentError
    )
    StateError = module.RuntimeKernelStateError

    kernel = Kernel(
        runtime_id="linkcraftor.primary",
        product_name="LinkCraftor",
    )

    assertions: dict[str, str] = {}

    if kernel.state is not State.CREATED:
        fail("Kernel did not begin in CREATED state.")

    assertions["initial_state"] = "PASS"

    configuration_v1 = {
        "source": "verification",
        "revision": 1,
    }

    first_binding = kernel.bind_component(
        "configuration",
        configuration_v1,
    )

    if first_binding.key != "configuration":
        fail("Configuration binding key is incorrect.")

    assertions["component_binding"] = "PASS"

    duplicate_rejected = False

    try:
        kernel.bind_component(
            "configuration",
            object(),
        )
    except BindingError:
        duplicate_rejected = True

    if not duplicate_rejected:
        fail(
            "Duplicate component binding was not rejected."
        )

    assertions["duplicate_binding_rejection"] = "PASS"

    configuration_v2 = {
        "source": "verification",
        "revision": 2,
    }

    replacement_binding = kernel.bind_component(
        "configuration",
        configuration_v2,
        replace=True,
    )

    if (
        replacement_binding.generation
        <= first_binding.generation
    ):
        fail(
            "Replacement binding did not advance "
            "the kernel generation."
        )

    assertions["explicit_replacement"] = "PASS"

    retrieved = kernel.get_component(
        "configuration",
        dict,
    )

    if retrieved is not configuration_v2:
        fail(
            "Typed component retrieval returned "
            "the wrong object."
        )

    assertions["typed_component_retrieval"] = "PASS"

    missing_rejected = False

    try:
        kernel.get_component("state_store")
    except MissingError:
        missing_rejected = True

    if not missing_rejected:
        fail(
            "Missing component retrieval was not rejected."
        )

    assertions["missing_component_rejection"] = "PASS"

    required_components = kernel.require_components(
        ["configuration"]
    )

    if required_components["configuration"] is not configuration_v2:
        fail(
            "Required component mapping is incorrect."
        )

    immutable_mapping = False

    try:
        required_components["illegal"] = object()
    except TypeError:
        immutable_mapping = True

    if not immutable_mapping:
        fail(
            "Required component mapping was mutable."
        )

    assertions["immutable_required_mapping"] = "PASS"

    kernel.transition_state(
        expected_state=State.CREATED,
        target_state=State.INITIALIZING,
    )

    kernel.transition_state(
        expected_state=State.INITIALIZING,
        target_state=State.READY,
    )

    kernel.transition_state(
        expected_state=State.READY,
        target_state=State.RUNNING,
    )

    assertions["legal_state_transitions"] = "PASS"

    stale_transition_rejected = False

    try:
        kernel.transition_state(
            expected_state=State.READY,
            target_state=State.STOPPING,
        )
    except StateError:
        stale_transition_rejected = True

    if not stale_transition_rejected:
        fail(
            "A stale expected-state transition "
            "was not rejected."
        )

    assertions["stale_transition_rejection"] = "PASS"

    illegal_transition_rejected = False

    try:
        kernel.transition_state(
            expected_state=State.RUNNING,
            target_state=State.CREATED,
        )
    except StateError:
        illegal_transition_rejected = True

    if not illegal_transition_rejected:
        fail(
            "An illegal kernel transition was not rejected."
        )

    assertions["illegal_transition_rejection"] = "PASS"

    thread_errors: list[str] = []
    thread_count = 12

    def bind_thread_component(index: int) -> None:
        try:
            kernel.bind_component(
                f"verification.component_{index}",
                {
                    "index": index,
                },
            )
        except Exception as exc:
            thread_errors.append(
                f"{type(exc).__name__}: {exc}"
            )

    threads = [
        threading.Thread(
            target=bind_thread_component,
            args=(index,),
            daemon=True,
        )
        for index in range(thread_count)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    if thread_errors:
        fail(
            "Concurrent component binding failed: "
            + "; ".join(thread_errors)
        )

    for index in range(thread_count):
        key = f"verification.component_{index}"

        if not kernel.has_component(key):
            fail(
                f"Concurrent binding {key!r} is missing."
            )

    assertions["thread_safe_component_binding"] = "PASS"

    running_snapshot = kernel.snapshot()

    if running_snapshot.state is not State.RUNNING:
        fail(
            "Runtime snapshot has the wrong state."
        )

    if (
        running_snapshot.component_count
        != kernel.component_count
    ):
        fail(
            "Runtime snapshot component count is inconsistent."
        )

    if (
        "configuration"
        not in {
            binding.key
            for binding in running_snapshot.components
        }
    ):
        fail(
            "Runtime snapshot omitted the configuration binding."
        )

    assertions["immutable_snapshot"] = "PASS"

    missing_foundation = (
        kernel.missing_foundation_components()
    )

    expected_missing = {
        "environment",
        "service_registry",
        "lifecycle_manager",
        "persistence",
        "state_store",
        "schema_manager",
    }

    if set(missing_foundation) != expected_missing:
        fail(
            "Foundation-component readiness result "
            "is incorrect."
        )

    assertions["foundation_readiness_detection"] = "PASS"

    kernel.transition_state(
        expected_state=State.RUNNING,
        target_state=State.DRAINING,
    )

    kernel.transition_state(
        expected_state=State.DRAINING,
        target_state=State.STOPPING,
    )

    kernel.transition_state(
        expected_state=State.STOPPING,
        target_state=State.STOPPED,
    )

    if kernel.state is not State.STOPPED:
        fail(
            "Kernel did not reach STOPPED state."
        )

    terminal_mutation_rejected = False

    try:
        kernel.bind_component(
            "verification.after_stop",
            object(),
        )
    except StateError:
        terminal_mutation_rejected = True

    if not terminal_mutation_rejected:
        fail(
            "Kernel accepted a component binding "
            "after stopping."
        )

    assertions["terminal_state_protection"] = "PASS"

    final_snapshot = kernel.snapshot()

    return {
        "assertions": assertions,
        "final_state": final_snapshot.state.value,
        "final_generation": final_snapshot.generation,
        "final_component_count": (
            final_snapshot.component_count
        ),
        "missing_foundation_components": list(
            final_snapshot.missing_foundation_components
        ),
    }


def rollback(
    *,
    target_existed: bool,
) -> None:
    if target_existed:
        if not BACKUP_TARGET.exists():
            raise RuntimeError(
                "Rollback backup is missing."
            )

        TARGET.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            BACKUP_TARGET,
            TARGET,
        )

    elif TARGET.exists():
        TARGET.unlink()


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("1.1.1 — UNIVERSAL RUNTIME KERNEL BUILD")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Kernel target: {TARGET}")
    print()

    if not MAIN_FILE.exists():
        fail(
            f"main.py does not exist: {MAIN_FILE}"
        )

    target_existed = TARGET.exists()
    target_original_hash = sha256_file(TARGET)

    facade_hash_before = sha256_file(
        EXISTING_RUNTIME_FACADE
    )

    if target_existed:
        BACKUP_TARGET.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            TARGET,
            BACKUP_TARGET,
        )

        print(
            "Existing kernel file backed up before replacement:"
        )
        print(BACKUP_TARGET)
        print()

    TARGET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        TARGET.write_text(
            KERNEL_SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        py_compile.compile(
            str(MAIN_FILE),
            doraise=True,
        )

        ast_contract = verify_ast_contract(TARGET)

        module = load_kernel_module(TARGET)
        behavioral_results = verify_runtime_behavior(
            module
        )

        facade_hash_after = sha256_file(
            EXISTING_RUNTIME_FACADE
        )

        if facade_hash_before != facade_hash_after:
            fail(
                "The existing universal runtime infrastructure "
                "facade changed unexpectedly."
            )

    except Exception:
        rollback(
            target_existed=target_existed,
        )

        print()
        print("ROLLBACK COMPLETE")
        print(
            "Kernel build verification failed. "
            "The previous filesystem state was restored."
        )
        raise

    target_final_hash = sha256_file(TARGET)

    evidence = {
        "build_version": BUILD_VERSION,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "target": str(TARGET),
        "target_existed_before_build": target_existed,
        "target_backup": (
            str(BACKUP_TARGET)
            if target_existed
            else None
        ),
        "target_original_sha256": (
            target_original_hash
        ),
        "target_final_sha256": target_final_hash,
        "existing_runtime_facade": str(
            EXISTING_RUNTIME_FACADE
        ),
        "existing_runtime_facade_sha256_before": (
            facade_hash_before
        ),
        "existing_runtime_facade_sha256_after": (
            facade_hash_after
        ),
        "verification": {
            "kernel_py_compile": "PASS",
            "main_py_compile": "PASS",
            "ast_contract": "PASS",
            "runtime_behavior": "PASS",
            "thread_safety_test": "PASS",
            "business_logic_agnostic_test": "PASS",
            "existing_runtime_facade_unchanged": "PASS",
            "automatic_rollback_required": False,
        },
        "ast_contract_details": ast_contract,
        "behavioral_results": behavioral_results,
        "phase_status": {
            "phase": "1",
            "item": "1.1.1",
            "name": "Universal Runtime Kernel",
            "implementation_status": "IMPLEMENTED",
            "verification_status": "PASS",
            "integration_status": "PENDING",
            "certification_status": "NOT_CERTIFIED",
        },
    }

    EVIDENCE_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assertions = behavioral_results[
        "assertions"
    ]

    evidence_lines = [
        "=" * 78,
        "UNIVERSAL RUNTIME INFRASTRUCTURE",
        "1.1.1 — UNIVERSAL RUNTIME KERNEL EVIDENCE",
        "=" * 78,
        "",
        f"Build version: {BUILD_VERSION}",
        f"Timestamp UTC: {evidence['timestamp_utc']}",
        f"Kernel target: {TARGET}",
        "",
        "VERIFICATION",
        "-" * 78,
        "Kernel Python compilation: PASS",
        "main.py compilation: PASS",
        "Kernel AST contract: PASS",
        "Business-logic-agnostic boundary: PASS",
        "Existing runtime facade unchanged: PASS",
        "",
        "BEHAVIORAL TESTS",
        "-" * 78,
    ]

    for name, status in assertions.items():
        evidence_lines.append(
            f"{name}: {status}"
        )

    evidence_lines.extend(
        [
            "",
            "FINAL TEST STATE",
            "-" * 78,
            (
                "State: "
                f"{behavioral_results['final_state']}"
            ),
            (
                "Generation: "
                f"{behavioral_results['final_generation']}"
            ),
            (
                "Component count: "
                f"{behavioral_results['final_component_count']}"
            ),
            "",
            "CHECKLIST POSITION",
            "-" * 78,
            "1.1.1 implementation: PASS",
            "1.1.1 isolated verification: PASS",
            "1.1.1 runtime integration: PENDING",
            "1.1.1 certification: NOT CERTIFIED",
            "Phase 1 certification: NOT CERTIFIED",
            "",
        ]
    )

    EVIDENCE_TEXT.write_text(
        "\n".join(evidence_lines),
        encoding="utf-8",
    )

    print("BUILD VERIFICATION")
    print("-" * 78)
    print("Kernel Python compilation:         PASS")
    print("main.py compilation:               PASS")
    print("Kernel AST contract:               PASS")
    print("Kernel behavioral contract:        PASS")
    print("Thread-safe component binding:      PASS")
    print("Business-logic-agnostic boundary:   PASS")
    print("Existing runtime facade unchanged:  PASS")
    print()

    print("FILES")
    print("-" * 78)
    print(f"Kernel:        {TARGET}")
    print(f"Evidence JSON: {EVIDENCE_JSON}")
    print(f"Evidence text: {EVIDENCE_TEXT}")
    print()

    print("1.1.1 UNIVERSAL RUNTIME KERNEL")
    print("IMPLEMENTATION: PASS")
    print("ISOLATED VERIFICATION: PASS")
    print("RUNTIME INTEGRATION: PENDING")
    print("CERTIFICATION: NOT CERTIFIED")
    print()
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
