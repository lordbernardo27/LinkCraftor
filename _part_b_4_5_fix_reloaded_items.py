from __future__ import annotations

import py_compile
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


runner = Path(sys.argv[1]).resolve()
source = runner.read_text(encoding="utf-8")

pattern = re.compile(
    r'(?P<variable>[A-Za-z_][A-Za-z0-9_]*)'
    r'\.get\(\s*(?P<quote>["\'])targets(?P=quote)'
    r'\s*,\s*\[\]\s*\)'
)

matches = [
    match
    for match in pattern.finditer(source)
    if "load" in match.group("variable").lower()
]

if len(matches) != 1:
    raise RuntimeError(
        "Expected exactly one reloaded-payload targets lookup, "
        f"found {len(matches)}."
    )

match = matches[0]
line_start = source.rfind("\n", 0, match.start()) + 1
context_start = max(0, source.rfind("\n", 0, line_start - 1))
context_end = source.find("\n", match.end())

if context_end < 0:
    context_end = len(source)

context = source[context_start:context_end]

if "RELOADED_TARGET_COUNT_MATCHES" not in context:
    extended_start = max(0, match.start() - 500)
    extended_end = min(len(source), match.end() + 500)

    if (
        "RELOADED_TARGET_COUNT_MATCHES"
        not in source[extended_start:extended_end]
    ):
        raise RuntimeError(
            "The targets lookup is not associated with "
            "RELOADED_TARGET_COUNT_MATCHES."
        )

replacement = (
    f'{match.group("variable")}.get('
    f'{match.group("quote")}items{match.group("quote")}, [])'
)

corrected = (
    source[:match.start()]
    + replacement
    + source[match.end():]
)

timestamp = (
    datetime.now(timezone.utc)
    .strftime("%Y%m%dT%H%M%S%fZ")
)

backup = runner.with_name(
    runner.name
    + ".before_reloaded_items_fix_"
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

print("RELOADED_COLLECTION_KEY_CORRECTED: PASS")
print("OLD_KEY=targets")
print("CANONICAL_KEY=items")
print("RUNNER_SYNTAX: PASS")
print("RUNNER_BACKUP=" + str(backup))