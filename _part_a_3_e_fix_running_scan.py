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

old_candidate = '''    running_position = segment.find(
        "JOB_STATUS_RUNNING"
    )
'''

new_candidate = '''    running_position = segment.find(
        "JOB_STATUS_RUNNING",
        policy_position,
    )
'''

old_runtime = '''    queue_running_position = queue_source.find(
        "JOB_STATUS_RUNNING"
    )
'''

new_runtime = '''    queue_running_position = queue_source.find(
        "JOB_STATUS_RUNNING",
        queue_policy_position,
    )
'''

candidate_count = source.count(
    old_candidate
)

runtime_count = source.count(
    old_runtime
)

if candidate_count != 1:
    raise RuntimeError(
        "Expected one candidate RUNNING-position check, "
        f"found {candidate_count}."
    )

if runtime_count != 1:
    raise RuntimeError(
        "Expected one runtime RUNNING-position check, "
        f"found {runtime_count}."
    )

timestamp = (
    datetime.now(timezone.utc)
    .strftime("%Y%m%dT%H%M%S%fZ")
)

backup = runner.with_name(
    runner.name
    + ".before_running_scan_fix_"
    + timestamp
)

shutil.copy2(
    runner,
    backup,
)

corrected = source.replace(
    old_candidate,
    new_candidate,
    1,
)

corrected = corrected.replace(
    old_runtime,
    new_runtime,
    1,
)

if old_candidate in corrected:
    raise RuntimeError(
        "Old candidate scan remains."
    )

if old_runtime in corrected:
    raise RuntimeError(
        "Old runtime scan remains."
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
    "PART_A_3_E_RUNNING_SCAN_CORRECTED: PASS"
)

print(
    "RUNNER_SYNTAX: PASS"
)

print(
    "RUNNER_BACKUP=" + str(backup)
)