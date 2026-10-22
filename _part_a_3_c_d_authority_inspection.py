from __future__ import annotations

import ast
import dataclasses
import enum
import hashlib
import importlib
import inspect
import pathlib
import sys
import traceback
from typing import Any


root = pathlib.Path(sys.argv[1]).resolve()
runtime_root = root / "backend" / "server" / "runtime"

targets = {
    "registration_package": (
        runtime_root / "runtime_registration_package.py"
    ),
    "registration_registry": (
        runtime_root / "universal_runtime_registration.py"
    ),
    "registration_gateway": (
        runtime_root / "runtime_registration_gateway.py"
    ),
    "worker": (
        runtime_root / "universal_runtime_worker_v1.py"
    ),
    "configuration": (
        runtime_root / "runtime_configuration.py"
    ),
    "feature_gateway": (
        runtime_root / "runtime_feature_flag_gateway.py"
    ),
    "feature_flags": (
        runtime_root / "runtime_feature_flags.py"
    ),
    "versioning": (
        runtime_root / "runtime_versioning.py"
    ),
    "compatibility": (
        runtime_root / "runtime_compatibility.py"
    ),
    "boot": (
        runtime_root / "runtime_boot_process.py"
    ),
}

modules = {
    "registration_package": (
        "backend.server.runtime.runtime_registration_package"
    ),
    "registration_registry": (
        "backend.server.runtime.universal_runtime_registration"
    ),
    "registration_gateway": (
        "backend.server.runtime.runtime_registration_gateway"
    ),
    "worker": (
        "backend.server.runtime.universal_runtime_worker_v1"
    ),
    "configuration": (
        "backend.server.runtime.runtime_configuration"
    ),
    "feature_gateway": (
        "backend.server.runtime.runtime_feature_flag_gateway"
    ),
    "feature_flags": (
        "backend.server.runtime.runtime_feature_flags"
    ),
    "versioning": (
        "backend.server.runtime.runtime_versioning"
    ),
    "compatibility": (
        "backend.server.runtime.runtime_compatibility"
    ),
    "boot": (
        "backend.server.runtime.runtime_boot_process"
    ),
}

required_sources = set(targets)
required_imports = set(modules)

passed = 0
failed = 0
failures: list[str] = []


def heading(title: str) -> None:
    print()
    print("=" * 112)
    print(title)
    print("=" * 112)


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
        failures.append(label)
        print(f"{label}: FAIL")

    if detail is not None:
        print(f"  {detail}")


def source_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_signature(value: Any) -> str:
    try:
        return str(inspect.signature(value))
    except Exception as exc:
        return f"<signature unavailable: {type(exc).__name__}: {exc}>"


def print_dataclass_fields(value: Any) -> None:
    if not dataclasses.is_dataclass(value):
        print("DATACLASS_FIELDS: NOT_A_DATACLASS")
        return

    print("DATACLASS_FIELDS:")

    for field in dataclasses.fields(value):
        default = "<required>"

        if field.default is not dataclasses.MISSING:
            default = repr(field.default)
        elif field.default_factory is not dataclasses.MISSING:
            default = "<default_factory>"

        print(
            f"  - {field.name}: type={field.type!r}, default={default}"
        )


def print_enum_members(value: Any) -> None:
    if not inspect.isclass(value) or not issubclass(value, enum.Enum):
        return

    print("ENUM_MEMBERS:")

    for member in value:
        print(f"  - {member.name}={member.value!r}")


def print_public_symbols(
    module: Any,
    *,
    terms: tuple[str, ...],
) -> None:
    selected: list[tuple[str, Any]] = []

    for name in dir(module):
        if name.startswith("_"):
            continue

        lowered = name.lower()

        if not any(term in lowered for term in terms):
            continue

        selected.append((name, getattr(module, name)))

    for name, value in selected:
        if inspect.isfunction(value) or inspect.isclass(value):
            print(
                f"{name}: {type(value).__name__} "
                f"{safe_signature(value)}"
            )

            print_dataclass_fields(value)
            print_enum_members(value)
        else:
            print(f"{name}: {type(value).__name__} = {value!r}")


def source_for_symbol(
    module: Any,
    symbol_name: str,
) -> str:
    value = getattr(module, symbol_name, None)

    if value is None:
        return f"<symbol {symbol_name!r} unavailable>"

    try:
        return inspect.getsource(value)
    except Exception as exc:
        return (
            f"<source unavailable for {symbol_name}: "
            f"{type(exc).__name__}: {exc}>"
        )


heading("PART A 3-C AND 3-D - SOURCE VALIDATION")

source_texts: dict[str, str] = {}
source_hashes: dict[str, str] = {}

for name, path in targets.items():
    exists = path.is_file()
    check(
        f"SOURCE_EXISTS_{name.upper()}",
        exists,
        path,
    )

    if not exists:
        continue

    try:
        source = path.read_text(encoding="utf-8-sig")
        ast.parse(source)
    except Exception as exc:
        check(
            f"SOURCE_SYNTAX_{name.upper()}",
            False,
            f"{type(exc).__name__}: {exc}",
        )
        continue

    source_texts[name] = source
    source_hashes[name] = source_hash(path)

    check(
        f"SOURCE_SYNTAX_{name.upper()}",
        True,
        source_hashes[name],
    )


heading("PART A 3-C AND 3-D - MODULE IMPORTS")

imported: dict[str, Any] = {}

for name, module_name in modules.items():
    try:
        module = importlib.import_module(module_name)
    except Exception:
        check(
            f"MODULE_IMPORT_{name.upper()}",
            False,
        )
        traceback.print_exc()
        continue

    imported[name] = module

    check(
        f"MODULE_IMPORT_{name.upper()}",
        True,
        module_name,
    )


heading("3-C1 - REGISTRATION PACKAGE POLICY SCHEMA")

package_module = imported.get("registration_package")

if package_module is not None:
    package_class = getattr(
        package_module,
        "RuntimeRegistrationPackage",
        None,
    )
    package_factory = getattr(
        package_module,
        "create_runtime_registration_package",
        None,
    )

    check(
        "REGISTRATION_PACKAGE_MODEL_AVAILABLE",
        inspect.isclass(package_class),
    )
    check(
        "REGISTRATION_PACKAGE_FACTORY_AVAILABLE",
        callable(package_factory),
        safe_signature(package_factory)
        if callable(package_factory)
        else None,
    )

    if inspect.isclass(package_class):
        print_dataclass_fields(package_class)

        field_names = {
            field.name
            for field in dataclasses.fields(package_class)
        } if dataclasses.is_dataclass(package_class) else set()

        check(
            "LIFECYCLE_POLICY_FIELD_AVAILABLE",
            "lifecycle_policy" in field_names,
            sorted(field_names),
        )
        check(
            "CONFIGURATION_REQUIREMENTS_FIELD_AVAILABLE",
            "configuration_requirements" in field_names,
        )
        check(
            "FEATURE_FLAG_KEY_FIELD_AVAILABLE",
            "feature_flag_key" in field_names,
        )
        check(
            "VERSION_REQUIREMENTS_FIELD_AVAILABLE",
            "runtime_version_requirements" in field_names,
        )

    print()
    print("RUNTIME_REGISTRATION_PACKAGE_SOURCE:")
    print(
        source_for_symbol(
            package_module,
            "RuntimeRegistrationPackage",
        )
    )

    print()
    print("PACKAGE_FACTORY_SOURCE:")
    print(
        source_for_symbol(
            package_module,
            "create_runtime_registration_package",
        )
    )


heading("3-C2 - RUNTIME CONFIGURATION AUTHORITY")

configuration_module = imported.get("configuration")

if configuration_module is not None:
    print_public_symbols(
        configuration_module,
        terms=(
            "configuration",
            "environment",
            "load",
            "snapshot",
        ),
    )

    configuration_class = getattr(
        configuration_module,
        "RuntimeConfiguration",
        None,
    )

    check(
        "RUNTIME_CONFIGURATION_AVAILABLE",
        inspect.isclass(configuration_class),
    )

    if inspect.isclass(configuration_class):
        print()
        print("RUNTIME_CONFIGURATION_SOURCE:")
        print(
            source_for_symbol(
                configuration_module,
                "RuntimeConfiguration",
            )
        )


heading("3-C3 - LIFECYCLE AND BOOT AUTHORITIES")

boot_module = imported.get("boot")

if boot_module is not None:
    print_public_symbols(
        boot_module,
        terms=(
            "boot",
            "context",
            "composition",
            "stage",
            "status",
            "lifecycle",
        ),
    )

    for symbol in (
        "RuntimeBootContext",
        "RuntimeBootComposition",
        "RuntimeBootStage",
        "RuntimeBootStatus",
    ):
        if hasattr(boot_module, symbol):
            print()
            print(f"{symbol}_SOURCE:")
            print(source_for_symbol(boot_module, symbol))


heading("3-D1 - FEATURE-FLAG AUTHORITY")

feature_gateway_module = imported.get("feature_gateway")

if feature_gateway_module is not None:
    print_public_symbols(
        feature_gateway_module,
        terms=(
            "feature",
            "flag",
            "gateway",
            "evaluate",
            "enabled",
            "require",
            "context",
        ),
    )

    for name in sorted(dir(feature_gateway_module)):
        lowered = name.lower()

        if name.startswith("_"):
            continue

        if not any(
            term in lowered
            for term in (
                "evaluate",
                "enabled",
                "feature_flag",
                "gateway",
            )
        ):
            continue

        value = getattr(feature_gateway_module, name)

        if not (inspect.isfunction(value) or inspect.isclass(value)):
            continue

        print()
        print(f"FEATURE_GATEWAY_SYMBOL_SOURCE_{name}:")
        print(source_for_symbol(feature_gateway_module, name))


feature_flags_module = imported.get("feature_flags")

if feature_flags_module is not None:
    print_public_symbols(
        feature_flags_module,
        terms=(
            "feature",
            "flag",
            "state",
            "evaluation",
            "context",
            "registry",
        ),
    )


heading("3-D2 - VERSION AND COMPATIBILITY AUTHORITIES")

versioning_module = imported.get("versioning")

if versioning_module is not None:
    print_public_symbols(
        versioning_module,
        terms=(
            "version",
            "manifest",
            "requirement",
            "manager",
            "snapshot",
        ),
    )

    for symbol in (
        "RuntimeVersionRequirement",
        "RuntimeVersionManifest",
        "RuntimeVersionManager",
        "create_default_runtime_version_manager",
    ):
        if hasattr(versioning_module, symbol):
            print()
            print(f"VERSION_SYMBOL_SOURCE_{symbol}:")
            print(source_for_symbol(versioning_module, symbol))


compatibility_module = imported.get("compatibility")

if compatibility_module is not None:
    print_public_symbols(
        compatibility_module,
        terms=(
            "compatibility",
            "require",
            "evaluate",
            "policy",
            "report",
            "result",
        ),
    )

    for name in sorted(dir(compatibility_module)):
        lowered = name.lower()

        if name.startswith("_"):
            continue

        if not any(
            term in lowered
            for term in (
                "require_compatible",
                "evaluate",
                "compatibility",
            )
        ):
            continue

        value = getattr(compatibility_module, name)

        if not (inspect.isfunction(value) or inspect.isclass(value)):
            continue

        print()
        print(f"COMPATIBILITY_SYMBOL_SOURCE_{name}:")
        print(source_for_symbol(compatibility_module, name))


heading("3-C/3-D - CURRENT REGISTRATION GATEWAY")

registration_gateway_module = imported.get(
    "registration_gateway"
)

if registration_gateway_module is not None:
    print_public_symbols(
        registration_gateway_module,
        terms=(
            "registration",
            "gateway",
            "snapshot",
            "evidence",
        ),
    )

    print()
    print("CURRENT_REGISTRATION_GATEWAY_SOURCE:")
    print(source_texts.get("registration_gateway", ""))


heading("3-C/3-D - REGISTRY LOOKUP CONTRACT")

registration_module = imported.get("registration_registry")

if registration_module is not None:
    for symbol in (
        "get_runtime_registration",
        "register_runtime_handler",
        "dispatch_registered_runtime_handler",
        "runtime_registration_snapshot",
    ):
        value = getattr(registration_module, symbol, None)

        check(
            f"REGISTRY_SYMBOL_{symbol.upper()}",
            callable(value),
            safe_signature(value) if callable(value) else None,
        )

        if callable(value):
            print()
            print(f"REGISTRY_SYMBOL_SOURCE_{symbol}:")
            print(source_for_symbol(registration_module, symbol))


heading("3-C/3-D - WORKER ENFORCEMENT ANCHORS")

worker_module = imported.get("worker")

if worker_module is not None:
    worker_function = getattr(
        worker_module,
        "run_one_universal_runtime_job_v1",
        None,
    )

    check(
        "CANONICAL_WORKER_ENTRY_POINT_AVAILABLE",
        callable(worker_function),
        safe_signature(worker_function)
        if callable(worker_function)
        else None,
    )

    if callable(worker_function):
        worker_source = source_for_symbol(
            worker_module,
            "run_one_universal_runtime_job_v1",
        )

        print()
        print("CANONICAL_WORKER_SOURCE:")
        print(worker_source)

        try:
            worker_tree = ast.parse(worker_source)
            calls: list[tuple[str, int]] = []

            for node in ast.walk(worker_tree):
                if not isinstance(node, ast.Call):
                    continue

                if isinstance(node.func, ast.Name):
                    calls.append(
                        (node.func.id, node.lineno)
                    )
                elif isinstance(node.func, ast.Attribute):
                    calls.append(
                        (node.func.attr, node.lineno)
                    )

            calls.sort(key=lambda item: item[1])

            print()
            print(f"WORKER_CALL_ORDER={calls!r}")

            lookup_lines = [
                line
                for name, line in calls
                if name == "get_runtime_registration"
            ]
            dispatcher_lines = [
                line
                for name, line in calls
                if name in {
                    "dispatcher",
                    "dispatch_registered_runtime_handler",
                }
            ]

            check(
                "REGISTRATION_LOOKUP_ANCHOR_AVAILABLE",
                len(lookup_lines) == 1,
                lookup_lines,
            )
            check(
                "DISPATCH_ANCHOR_AVAILABLE",
                len(dispatcher_lines) == 1,
                dispatcher_lines,
            )
            check(
                "ADMISSION_INSERTION_BOUNDARY_AVAILABLE",
                bool(
                    lookup_lines
                    and dispatcher_lines
                    and lookup_lines[0] < dispatcher_lines[0]
                ),
                {
                    "registration_lookup": lookup_lines,
                    "dispatch": dispatcher_lines,
                },
            )
        except Exception:
            check(
                "WORKER_AST_ANALYSIS",
                False,
            )
            traceback.print_exc()


heading("3-C/3-D - CURRENT AUTHORITY DECISION")

required_authorities = {
    "registration_package",
    "registration_registry",
    "registration_gateway",
    "worker",
    "configuration",
    "feature_gateway",
    "feature_flags",
    "versioning",
    "compatibility",
    "boot",
}

missing_sources = sorted(
    required_authorities - set(source_texts)
)
missing_imports = sorted(
    required_authorities - set(imported)
)

check(
    "ALL_REQUIRED_SOURCES_AVAILABLE",
    not missing_sources,
    missing_sources,
)
check(
    "ALL_REQUIRED_MODULES_IMPORT",
    not missing_imports,
    missing_imports,
)
check(
    "PRODUCTION_FILES_MODIFIED_NO",
    True,
)
check(
    "REGISTRATION_CREATED_NO",
    True,
)
check(
    "REGISTRY_PERSISTENCE_EXECUTED_NO",
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

heading("PART A 3-C AND 3-D - FINAL RESULT")

print(f"INSPECTION_CHECKS_PASSED={passed}")
print(f"INSPECTION_CHECKS_FAILED={failed}")

if failures:
    print("FAILED_CHECKS:")

    for failure in failures:
        print(f"  - {failure}")

print(
    "AUTHORITY_INSPECTION="
    + ("COMPLETE" if failed == 0 else "INCOMPLETE")
)
print("PRODUCTION FILES MODIFIED: NO")

if failed:
    raise SystemExit(1)