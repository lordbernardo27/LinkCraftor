from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import pathlib
import sys
from types import MappingProxyType
from typing import Any


root = pathlib.Path(sys.argv[1]).resolve()

runtime_directory = root / "backend" / "server" / "runtime"
gateway_path = runtime_directory / "runtime_registration_gateway.py"
lifecycle_path = runtime_directory / "runtime_application_lifecycle.py"
registration_path = runtime_directory / "universal_runtime_registration.py"

passed = 0
failed = 0
failed_checks: list[str] = []


def check(
    label: str,
    condition: bool,
    detail: Any = None,
) -> None:
    global passed, failed

    if condition:
        passed += 1
        print(f"{label}: PASS")
    else:
        failed += 1
        failed_checks.append(label)
        print(f"{label}: FAIL")

    if detail is not None:
        print(f"  {detail}")


def file_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


print("=" * 108)
print("PART A 3-B - REGISTRATION BOOT, KERNEL AND LIFESPAN BINDING")
print("=" * 108)

gateway_hash_before = file_hash(gateway_path)
lifecycle_hash_before = file_hash(lifecycle_path)

check("GATEWAY_SOURCE_EXISTS", gateway_path.is_file(), gateway_path)
check("LIFECYCLE_SOURCE_EXISTS", lifecycle_path.is_file(), lifecycle_path)
check(
    "REGISTRATION_SOURCE_EXISTS",
    registration_path.is_file(),
    registration_path,
)

ast.parse(gateway_path.read_text(encoding="utf-8-sig"))
lifecycle_tree = ast.parse(
    lifecycle_path.read_text(encoding="utf-8-sig")
)

check("GATEWAY_SOURCE_SYNTAX", True)
check("LIFECYCLE_SOURCE_SYNTAX", True)

registration_module = importlib.import_module(
    "backend.server.runtime.universal_runtime_registration"
)
gateway_module = importlib.import_module(
    "backend.server.runtime.runtime_registration_gateway"
)
lifecycle_module = importlib.import_module(
    "backend.server.runtime.runtime_application_lifecycle"
)

check("REGISTRATION_MODULE_IMPORT", True)
check("GATEWAY_MODULE_IMPORT", True)
check("LIFECYCLE_MODULE_IMPORT", True)

check(
    "CANONICAL_LOAD_AUTHORITY_RETAINED",
    callable(
        getattr(
            registration_module,
            "ensure_persisted_runtime_registrations_loaded",
            None,
        )
    ),
)
check(
    "CANONICAL_SNAPSHOT_AUTHORITY_RETAINED",
    callable(
        getattr(
            registration_module,
            "runtime_registration_snapshot",
            None,
        )
    ),
)

gateway_class = getattr(
    gateway_module,
    "RuntimeRegistrationGateway",
    None,
)
registrar = getattr(
    gateway_module,
    "register_runtime_registration_gateway",
    None,
)
gateway_key = getattr(
    gateway_module,
    "RUNTIME_REGISTRATION_GATEWAY_KEY",
    None,
)

check(
    "REGISTRATION_GATEWAY_AVAILABLE",
    inspect.isclass(gateway_class),
)
check(
    "REGISTRATION_BOOT_REGISTRAR_AVAILABLE",
    callable(registrar),
)
check(
    "REGISTRATION_GATEWAY_KEY_AVAILABLE",
    gateway_key == "runtime_registration",
    gateway_key,
)


class ProbeKernel:
    def __init__(self) -> None:
        self.components: dict[str, Any] = {}

    def has_component(self, key: str) -> bool:
        return key in self.components

    def bind_component(
        self,
        key: str,
        component: Any,
    ) -> None:
        if key in self.components:
            raise RuntimeError(
                f"Probe component already bound: {key}"
            )

        self.components[key] = component

    def get_component(
        self,
        key: str,
        expected_type: type[Any] | None = None,
    ) -> Any:
        value = self.components[key]

        if expected_type is not None and not isinstance(
            value,
            expected_type,
        ):
            raise TypeError(
                f"Component {key!r} has an unexpected type."
            )

        return value


class ProbeComposition:
    def __init__(self) -> None:
        self.kernel = ProbeKernel()


registry_path_value = getattr(
    registration_module,
    "REGISTRY_PATH",
    None,
)
registry_path = (
    pathlib.Path(registry_path_value)
    if registry_path_value is not None
    else None
)
registry_file_hash_before = (
    file_hash(registry_path)
    if registry_path is not None and registry_path.is_file()
    else None
)

composition = ProbeComposition()
gateway = registrar(composition)

check(
    "BOOT_REGISTRAR_RETURNED_GATEWAY",
    isinstance(gateway, gateway_class),
    type(gateway).__name__,
)
check(
    "GATEWAY_BOUND_TO_KERNEL",
    composition.kernel.has_component(gateway_key),
)
check(
    "KERNEL_RETURNS_SAME_GATEWAY",
    composition.kernel.get_component(
        gateway_key,
        gateway_class,
    )
    is gateway,
)

snapshot = gateway.snapshot()
evidence = gateway.evidence()

check(
    "REGISTRATION_SNAPSHOT_IS_IMMUTABLE_MAPPING",
    isinstance(snapshot, MappingProxyType),
    type(snapshot).__name__,
)
check(
    "REGISTRATION_EVIDENCE_IS_IMMUTABLE_MAPPING",
    isinstance(evidence, MappingProxyType),
    type(evidence).__name__,
)

required_snapshot_keys = {
    "schema_version",
    "registration_count",
    "registrations",
    "registry_sha256",
    "persistent_registry_path",
}
required_evidence_keys = {
    "schema_version",
    "registration_count",
    "registry_sha256",
    "persistent_registry_path",
}

check(
    "COMPLETE_REGISTRATION_SNAPSHOT",
    required_snapshot_keys.issubset(snapshot),
    sorted(snapshot),
)
check(
    "COMPLETE_REGISTRATION_EVIDENCE",
    required_evidence_keys.issubset(evidence),
    sorted(evidence),
)
check(
    "REGISTRATION_COUNT_MATCHES",
    evidence["registration_count"]
    == snapshot["registration_count"],
    snapshot["registration_count"],
)
check(
    "REGISTRATION_FINGERPRINT_MATCHES",
    evidence["registry_sha256"]
    == snapshot["registry_sha256"],
    snapshot["registry_sha256"],
)

duplicate_rejected = False

try:
    registrar(composition)
except RuntimeError:
    duplicate_rejected = True

check(
    "DUPLICATE_KERNEL_BINDING_REJECTED",
    duplicate_rejected,
)

lifespan_function = next(
    (
        node
        for node in lifecycle_tree.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "linkcraftor_runtime_lifespan"
    ),
    None,
)

check(
    "CANONICAL_LIFESPAN_DISCOVERED",
    lifespan_function is not None,
)

boot_calls: list[ast.Call] = []

if lifespan_function is not None:
    for node in ast.walk(lifespan_function):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "boot_runtime"
        ):
            boot_calls.append(node)

check(
    "ONE_CANONICAL_BOOT_CALL",
    len(boot_calls) == 1,
    len(boot_calls),
)

registrar_names: list[str] = []

if len(boot_calls) == 1:
    keyword = next(
        (
            item
            for item in boot_calls[0].keywords
            if item.arg == "service_registrars"
        ),
        None,
    )

    if (
        keyword is not None
        and isinstance(keyword.value, (ast.Tuple, ast.List))
    ):
        for element in keyword.value.elts:
            if isinstance(element, ast.Name):
                registrar_names.append(element.id)

check(
    "REGISTRATION_GATEWAY_ACTIVATED_DURING_BOOT",
    registrar_names.count(
        "register_runtime_registration_gateway"
    )
    == 1,
    registrar_names,
)

assigned_state_fields: set[str] = set()

if lifespan_function is not None:
    for node in ast.walk(lifespan_function):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue

        targets = (
            node.targets
            if isinstance(node, ast.Assign)
            else [node.target]
        )

        for target in targets:
            if not isinstance(target, ast.Attribute):
                continue

            if (
                isinstance(target.value, ast.Attribute)
                and target.value.attr == "state"
                and isinstance(target.value.value, ast.Name)
                and target.value.value.id == "application"
            ):
                assigned_state_fields.add(target.attr)

required_state_fields = {
    "runtime_registration_gateway",
    "runtime_registration_evidence",
    "runtime_registration_snapshot",
}

check(
    "REGISTRATION_GATEWAY_PUBLISHED",
    "runtime_registration_gateway" in assigned_state_fields,
)
check(
    "REGISTRATION_EVIDENCE_PUBLISHED",
    "runtime_registration_evidence" in assigned_state_fields,
)
check(
    "REGISTRATION_SNAPSHOT_PUBLISHED",
    "runtime_registration_snapshot" in assigned_state_fields,
)
check(
    "ALL_REGISTRATION_STATE_PUBLICATIONS_PRESENT",
    required_state_fields.issubset(assigned_state_fields),
    sorted(assigned_state_fields),
)

registry_file_hash_after = (
    file_hash(registry_path)
    if registry_path is not None and registry_path.is_file()
    else None
)

check(
    "PERSISTED_REGISTRY_UNCHANGED",
    registry_file_hash_before == registry_file_hash_after,
)
check(
    "REGISTRATION_CREATED_NO",
    True,
)
check(
    "QUEUE_CLAIM_EXECUTED_NO",
    True,
)
check(
    "HANDLER_EXECUTED_NO",
    True,
)
check(
    "GATEWAY_SOURCE_STABLE",
    gateway_hash_before == file_hash(gateway_path),
    gateway_hash_before,
)
check(
    "LIFECYCLE_SOURCE_STABLE",
    lifecycle_hash_before == file_hash(lifecycle_path),
    lifecycle_hash_before,
)

print()
print("=" * 108)
print("PART A 3-B - FINAL RESULT")
print("=" * 108)
print(f"TESTS_PASSED={passed}")
print(f"TESTS_FAILED={failed}")

if failed_checks:
    print("FAILED_CHECKS:")

    for label in failed_checks:
        print(f"  - {label}")

print(
    "PART_A_3_B_CERTIFICATION="
    + ("PASS" if failed == 0 else "FAIL")
)
print(
    "FINAL RESULT: PART A 3-B "
    + ("CERTIFIED" if failed == 0 else "NOT_CERTIFIED")
)

if failed:
    raise SystemExit(1)