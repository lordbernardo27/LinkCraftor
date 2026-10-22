from __future__ import annotations

import ast
import pathlib
import py_compile
import sys


root = pathlib.Path(sys.argv[1]).resolve()
backup_directory = pathlib.Path(sys.argv[2]).resolve()
gateway_source_path = pathlib.Path(sys.argv[3]).resolve()

lifecycle_path = (
    root
    / "backend"
    / "server"
    / "runtime"
    / "runtime_application_lifecycle.py"
)

gateway_candidate = (
    backup_directory
    / "runtime_registration_gateway.py.candidate"
)
lifecycle_candidate = (
    backup_directory
    / "runtime_application_lifecycle.py.candidate"
)


def fail(message: str) -> None:
    raise RuntimeError(message)


def absolute_offset(
    source: str,
    line_number: int,
    column_number: int,
) -> int:
    lines = source.splitlines(keepends=True)

    if line_number < 1 or line_number > len(lines):
        fail(f"Invalid source line: {line_number}")

    return (
        sum(len(line) for line in lines[: line_number - 1])
        + column_number
    )


def find_lifespan(tree: ast.Module) -> ast.AsyncFunctionDef:
    matches = [
        node
        for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "linkcraftor_runtime_lifespan"
    ]

    if len(matches) != 1:
        fail(
            "Expected one linkcraftor_runtime_lifespan(), "
            f"found {len(matches)}."
        )

    return matches[0]


def find_boot_call(
    lifespan: ast.AsyncFunctionDef,
) -> ast.Call:
    matches = [
        node
        for node in ast.walk(lifespan)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "boot_runtime"
    ]

    if len(matches) != 1:
        fail(
            "Expected one boot_runtime() call, "
            f"found {len(matches)}."
        )

    return matches[0]


def registrar_names(
    source: str,
) -> list[str]:
    tree = ast.parse(source)
    lifespan = find_lifespan(tree)
    boot_call = find_boot_call(lifespan)

    keyword = next(
        (
            item
            for item in boot_call.keywords
            if item.arg == "service_registrars"
        ),
        None,
    )

    if keyword is None:
        fail("service_registrars was not found.")

    if not isinstance(keyword.value, (ast.Tuple, ast.List)):
        fail("service_registrars is not a literal tuple or list.")

    names: list[str] = []

    for element in keyword.value.elts:
        if isinstance(element, ast.Name):
            names.append(element.id)

    return names


def patch_lifecycle(source: str) -> str:
    if "register_runtime_registration_gateway" in source:
        fail(
            "Registration gateway wiring already exists in the "
            "current lifecycle source."
        )

    decorator_anchor = "\n@asynccontextmanager\n"

    if source.count(decorator_anchor) != 1:
        fail(
            "Expected exactly one async-context-manager anchor, "
            f"found {source.count(decorator_anchor)}."
        )

    import_block = '''
from backend.server.runtime.runtime_registration_gateway import (
    RUNTIME_REGISTRATION_GATEWAY_KEY,
    RuntimeRegistrationGateway,
    register_runtime_registration_gateway,
)
'''

    source = source.replace(
        decorator_anchor,
        import_block + decorator_anchor,
        1,
    )

    tree = ast.parse(source)
    lifespan = find_lifespan(tree)
    boot_call = find_boot_call(lifespan)

    keyword = next(
        (
            item
            for item in boot_call.keywords
            if item.arg == "service_registrars"
        ),
        None,
    )

    if keyword is None:
        fail("The boot call does not contain service_registrars.")

    tuple_node = keyword.value

    if not isinstance(tuple_node, (ast.Tuple, ast.List)):
        fail("service_registrars is not a tuple or list.")

    if (
        tuple_node.lineno is None
        or tuple_node.end_lineno is None
        or tuple_node.col_offset is None
        or tuple_node.end_col_offset is None
    ):
        fail("Unable to determine the registrar tuple boundary.")

    end_offset = absolute_offset(
        source,
        tuple_node.end_lineno,
        tuple_node.end_col_offset,
    )

    closing_character = source[end_offset - 1]

    if closing_character not in {")", "]"}:
        fail(
            "The calculated service_registrars boundary is invalid."
        )

    if tuple_node.lineno == tuple_node.end_lineno:
        insertion = "register_runtime_registration_gateway, "
    else:
        closing_line = source.splitlines()[
            tuple_node.end_lineno - 1
        ]
        closing_indent = closing_line[
            : len(closing_line) - len(closing_line.lstrip())
        ]
        insertion = (
            "register_runtime_registration_gateway,\n"
            + closing_indent
        )

    source = (
        source[: end_offset - 1]
        + insertion
        + source[end_offset - 1 :]
    )

    discovered = registrar_names(source)

    if discovered.count(
        "register_runtime_registration_gateway"
    ) != 1:
        fail(
            "The corrected registrar was not inserted inside "
            f"service_registrars: {discovered!r}"
        )

    publication_lines = source.splitlines(keepends=True)
    publication_matches = [
        index
        for index, line in enumerate(publication_lines)
        if "application.state.runtime_boot_process = boot_process"
        in line
    ]

    if len(publication_matches) != 1:
        fail(
            "Expected one runtime_boot_process publication anchor, "
            f"found {len(publication_matches)}."
        )

    publication_index = publication_matches[0]
    anchor_line = publication_lines[publication_index]
    indent = anchor_line[
        : len(anchor_line) - len(anchor_line.lstrip())
    ]

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

    publication_lines.insert(
        publication_index,
        publication_block,
    )
    source = "".join(publication_lines)

    ast.parse(source)

    final_registrars = registrar_names(source)

    if final_registrars.count(
        "register_runtime_registration_gateway"
    ) != 1:
        fail(
            "Final lifecycle verification could not find exactly one "
            "registration registrar."
        )

    return source


gateway_source = gateway_source_path.read_text(
    encoding="utf-8-sig"
)
lifecycle_source = lifecycle_path.read_text(
    encoding="utf-8-sig"
)

patched_lifecycle = patch_lifecycle(lifecycle_source)

gateway_candidate.write_text(
    gateway_source,
    encoding="utf-8",
)
lifecycle_candidate.write_text(
    patched_lifecycle,
    encoding="utf-8",
)

py_compile.compile(
    str(gateway_candidate),
    doraise=True,
)
py_compile.compile(
    str(lifecycle_candidate),
    doraise=True,
)

names = registrar_names(patched_lifecycle)

print("PREVIOUS_GATEWAY_CANDIDATE_RETAINED: PASS")
print(f"  {gateway_source_path}")
print("CORRECTED_LIFECYCLE_CANDIDATE_CREATED: PASS")
print(f"  {lifecycle_candidate}")
print("GATEWAY_CANDIDATE_SYNTAX: PASS")
print("LIFECYCLE_CANDIDATE_SYNTAX: PASS")
print("SINGLE_LINE_TUPLE_HANDLING_CORRECTED: PASS")
print("REGISTRAR_INSERTED_INSIDE_BOOT_TUPLE: PASS")
print(f"  {names!r}")
print("APPLICATION_EVIDENCE_PUBLICATION_RETAINED: PASS")