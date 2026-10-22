from __future__ import annotations

import ast
import py_compile
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


runner = Path(sys.argv[1]).resolve()
source = runner.read_text(encoding="utf-8")
tree = ast.parse(source, filename=str(runner))

matching_calls: list[ast.Call] = []

for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue

    labels = [
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant)
        and isinstance(child.value, str)
    ]

    if "RELOADED_TARGET_COUNT_MATCHES" in labels:
        matching_calls.append(node)

if len(matching_calls) != 1:
    raise RuntimeError(
        "Expected exactly one RELOADED_TARGET_COUNT_MATCHES "
        f"call, found {len(matching_calls)}."
    )

check_call = matching_calls[0]

label_positions = [
    index
    for index, argument in enumerate(check_call.args)
    if isinstance(argument, ast.Constant)
    and argument.value == "RELOADED_TARGET_COUNT_MATCHES"
]

if label_positions != [0]:
    raise RuntimeError(
        "The reloaded-count check does not use the expected "
        "label-first call contract."
    )

if len(check_call.args) < 2:
    raise RuntimeError(
        "The reloaded-count check has no Boolean condition."
    )

condition = check_call.args[1]

candidate_names = sorted({
    node.id
    for node in ast.walk(condition)
    if isinstance(node, ast.Name)
    and "load" in node.id.lower()
})

if len(candidate_names) != 1:
    call_source = ast.get_source_segment(source, check_call)

    raise RuntimeError(
        "Could not uniquely discover the reloaded payload variable. "
        f"Candidates: {candidate_names}. "
        f"Check source: {call_source!r}"
    )

reloaded_name = candidate_names[0]

replacement_condition = (
    f'isinstance({reloaded_name}.get("items"), list) '
    f'and len({reloaded_name}.get("items", [])) '
    f'== int({reloaded_name}.get("created_count", -1)) '
    f'== 2'
)

lines = source.splitlines(keepends=True)

def absolute_offset(line_number: int, column: int) -> int:
    prefix = "".join(lines[: line_number - 1])
    line = lines[line_number - 1]

    # AST columns are UTF-8 byte offsets.
    byte_prefix = line.encode("utf-8")[:column]
    character_column = len(
        byte_prefix.decode("utf-8")
    )

    return len(prefix) + character_column


start = absolute_offset(
    condition.lineno,
    condition.col_offset,
)

end = absolute_offset(
    condition.end_lineno,
    condition.end_col_offset,
)

old_condition = source[start:end]

if not old_condition.strip():
    raise RuntimeError(
        "The existing reloaded-count condition is empty."
    )

corrected = (
    source[:start]
    + replacement_condition
    + source[end:]
)

if corrected == source:
    raise RuntimeError(
        "The verifier source was not changed."
    )

timestamp = (
    datetime.now(timezone.utc)
    .strftime("%Y%m%dT%H%M%S%fZ")
)

backup = runner.with_name(
    runner.name
    + ".before_reloaded_count_ast_fix_"
    + timestamp
)

shutil.copy2(runner, backup)

runner.write_text(
    corrected,
    encoding="utf-8",
    newline="\n",
)

try:
    py_compile.compile(
        str(runner),
        doraise=True,
    )
except Exception:
    shutil.copy2(backup, runner)
    raise

print("RELOADED_COUNT_CHECK_DISCOVERED: PASS")
print("RELOADED_PAYLOAD_VARIABLE=" + reloaded_name)
print("OLD_CONDITION=" + old_condition.strip())
print("CANONICAL_COLLECTION_KEY=items")
print("CORRECTED_CONDITION=" + replacement_condition)
print("RUNNER_SYNTAX: PASS")
print("RUNNER_BACKUP=" + str(backup))