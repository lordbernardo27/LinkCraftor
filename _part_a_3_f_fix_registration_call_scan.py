from __future__ import annotations

import py_compile
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


runner = Path(sys.argv[1]).resolve()

source = runner.read_text(
    encoding="utf-8",
)

old_scan = '''    registration_position = segment.find(
        "get_runtime_registration"
    )
'''

new_scan = '''    registration_position = segment.find(
        "runtime_registration = get_runtime_registration"
    )
'''

match_count = source.count(
    old_scan
)

if match_count != 1:
    raise RuntimeError(
        "Expected one registration-position scan, "
        f"found {match_count}."
    )

timestamp = (
    datetime.now(timezone.utc)
    .strftime("%Y%m%dT%H%M%S%fZ")
)

backup = runner.with_name(
    runner.name
    + ".before_registration_call_scan_fix_"
    + timestamp
)

shutil.copy2(
    runner,
    backup,
)

corrected = source.replace(
    old_scan,
    new_scan,
    1,
)

if old_scan in corrected:
    raise RuntimeError(
        "The inaccurate registration scan remains."
    )

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
    shutil.copy2(
        backup,
        runner,
    )
    raise

print(
    "PART_A_3_F_REGISTRATION_CALL_SCAN_CORRECTED: PASS"
)

print(
    "RUNNER_SYNTAX: PASS"
)

print(
    "RUNNER_BACKUP=" + str(backup)
)