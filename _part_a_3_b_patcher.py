from __future__ import annotations

import ast
import pathlib
import py_compile
import sys


root = pathlib.Path(sys.argv[1]).resolve()
backup_directory = pathlib.Path(sys.argv[2]).resolve()

runtime_directory = root / "backend" / "server" / "runtime"
gateway_path = runtime_directory / "runtime_registration_gateway.py"
lifecycle_path = runtime_directory / "runtime_application_lifecycle.py"

gateway_candidate = backup_directory / "runtime_registration_gateway.py.candidate"
lifecycle_candidate = backup_directory / "runtime_application_lifecycle.py.candidate"


gateway_source = '''"""Canonical Runtime Registration boot gateway.

This module does not create a second registration registry. It exposes
the existing Universal Runtime Registration authority to runtime boot,
the kernel and application-lifespan evidence.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping

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
'''


def fail(message: str) -> None:
    raise RuntimeError(message)


def locate_lifespan_function(tree: ast.Module) -> ast.AsyncFunctionDef:
    matches = [
        node
        for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "linkcraftor_runtime_lifespan"
    ]

    if len(matches) != 1:
        fail(
            "Expected exactly one linkcraftor_runtime_lifespan() "
            f"definition, found {len(matches)}."
        )

    return matches[0]


def locate_boot_call(
    function: ast.AsyncFunctionDef,
) -> ast.Call:
    matches: list[ast.Call] = []

    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue

        function_node = node.func

        if (
            isinstance(function_node, ast.Name)
            and function_node.id == "boot_runtime"
        ):
            matches.append(node)

    if len(matches) != 1:
        fail(
            "Expected exactly one boot_runtime() call in the canonical "
            f"lifespan, found {len(matches)}."
        )

    return matches[0]


def patch_lifecycle(source: str) -> str:
    if "register_runtime_registration_gateway" in source:
        fail(
            "Registration gateway wiring already appears in the "
            "application lifecycle. Refusing an ambiguous second patch."
        )

    import_marker = "\n@asynccontextmanager\n"

    if source.count(import_marker) != 1:
        fail(
            "Expected one @asynccontextmanager lifespan anchor, found "
            f"{source.count(import_marker)}."
        )

    import_block = '''
from backend.server.runtime.runtime_registration_gateway import (
    RUNTIME_REGISTRATION_GATEWAY_KEY,
    RuntimeRegistrationGateway,
    register_runtime_registration_gateway,
)
'''

    source = source.replace(
        import_marker,
        import_block + import_marker,
        1,
    )

    tree = ast.parse(source)
    lifespan = locate_lifespan_function(tree)
    boot_call = locate_boot_call(lifespan)

    registrar_keyword = next(
        (
            keyword
            for keyword in boot_call.keywords
            if keyword.arg == "service_registrars"
        ),
        None,
    )

    if registrar_keyword is None:
        fail(
            "The canonical boot_runtime() call does not expose "
            "service_registrars."
        )

    tuple_node = registrar_keyword.value

    if not isinstance(tuple_node, (ast.Tuple, ast.List)):
        fail(
            "service_registrars must be a literal tuple or list for "
            "fail-closed patching."
        )

    if tuple_node.end_lineno is None:
        fail("Unable to locate the service_registrars closing boundary.")

    lines = source.splitlines(keepends=True)
    closing_index = tuple_node.end_lineno - 1
    closing_line = lines[closing_index]
    closing_indent = closing_line[: len(closing_line) - len(closing_line.lstrip())]

    if tuple_node.elts:
        first_element = tuple_node.elts[0]

        if first_element.lineno is None:
            fail("Unable to locate the first service registrar.")

        first_line = lines[first_element.lineno - 1]
        element_indent = first_line[
            : len(first_line) - len(first_line.lstrip())
        ]
    else:
        element_indent = closing_indent + "    "

    lines.insert(
        closing_index,
        f"{element_indent}register_runtime_registration_gateway,\n",
    )

    source = "".join(lines)

    publication_matches = [
        index
        for index, line in enumerate(source.splitlines(keepends=True))
        if "application.state.runtime_boot_process = boot_process" in line
    ]

    if len(publication_matches) != 1:
        fail(
            "Expected one runtime_boot_process publication anchor, "
            f"found {len(publication_matches)}."
        )

    lines = source.splitlines(keepends=True)
    publication_index = publication_matches[0]
    anchor_line = lines[publication_index]
    indent = anchor_line[: len(anchor_line) - len(anchor_line.lstrip())]

    publication_block = f'''{indent}registration_gateway = boot_context.kernel.get_component(
{indent}    RUNTIME_REGISTRATION_GATEWAY_KEY,
{indent}    RuntimeRegistrationGateway,
{indent})
{indent}application.state.runtime_registration_gateway = (
{indent}    registration_gateway
{indent})
{indent}application.state.runtime_registration_evidence = _record_mapping(
{indent}    registration_gateway.evidence()
{indent})
{indent}application.state.runtime_registration_snapshot = _record_mapping(
{indent}    registration_gateway.snapshot()
{indent})

'''

    lines.insert(publication_index, publication_block)
    patched = "".join(lines)

    ast.parse(patched)

    return patched


lifecycle_source = lifecycle_path.read_text(encoding="utf-8-sig")
lifecycle_patched = patch_lifecycle(lifecycle_source)

gateway_candidate.write_text(gateway_source, encoding="utf-8")
lifecycle_candidate.write_text(lifecycle_patched, encoding="utf-8")

py_compile.compile(
    str(gateway_candidate),
    doraise=True,
)
py_compile.compile(
    str(lifecycle_candidate),
    doraise=True,
)

print("GATEWAY_CANDIDATE_CREATED: PASS")
print(f"  {gateway_candidate}")
print("LIFECYCLE_CANDIDATE_CREATED: PASS")
print(f"  {lifecycle_candidate}")
print("GATEWAY_CANDIDATE_SYNTAX: PASS")
print("LIFECYCLE_CANDIDATE_SYNTAX: PASS")
print("CANONICAL_BOOT_REGISTRAR_ADDED: PASS")
print("KERNEL_REGISTRATION_GATEWAY_PUBLICATION_ADDED: PASS")
print("APPLICATION_REGISTRATION_EVIDENCE_ADDED: PASS")