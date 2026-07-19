from __future__ import annotations

from pathlib import Path
import re
import sys

path = Path(
    "backend/server/workers/"
    "universal_knowledge_queue_runner.py"
)

text = path.read_text(
    encoding="utf-8-sig",
)

original = text

# ---------------------------------------------------------
# 1. Remove only the import-list line containing
#    update_job_progress.
# ---------------------------------------------------------
text, import_count = re.subn(
    r"(?m)^[ \t]*update_job_progress,[ \t]*\r?\n",
    "",
    text,
)

if import_count != 1:
    print(
        "ERROR: Expected exactly one "
        "update_job_progress import line, found "
        f"{import_count}."
    )
    sys.exit(1)

# ---------------------------------------------------------
# 2. Remove the runner_dequeued progress block.
#    The pattern consumes only the block itself and one
#    following blank line.
# ---------------------------------------------------------
dequeued_pattern = re.compile(
    r"""
^[ \t]{4}update_job_progress\(\r?\n
^[ \t]{8}workspace_id=ws,\r?\n
^[ \t]{8}job_id=job_id,\r?\n
^[ \t]{8}percent=5,\r?\n
^[ \t]{8}message="Runner\ dequeued\ job\.",\r?\n
^[ \t]{8}step="runner_dequeued",\r?\n
^[ \t]{4}\)\r?\n
(?:^[ \t]*\r?\n)?
""",
    re.MULTILINE | re.VERBOSE,
)

text, dequeued_count = dequeued_pattern.subn(
    "",
    text,
)

if dequeued_count != 1:
    print(
        "ERROR: Expected exactly one runner_dequeued "
        f"block, found {dequeued_count}."
    )
    sys.exit(1)

# ---------------------------------------------------------
# 3. Remove the runner_finished progress block.
# ---------------------------------------------------------
finished_pattern = re.compile(
    r"""
^[ \t]{4}update_job_progress\(\r?\n
^[ \t]{8}workspace_id=ws,\r?\n
^[ \t]{8}job_id=job_id,\r?\n
^[ \t]{8}percent=100,\r?\n
^[ \t]{8}message="Queue\ runner\ finished\.",\r?\n
^[ \t]{8}step="runner_finished",\r?\n
^[ \t]{4}\)\r?\n
(?:^[ \t]*\r?\n)?
""",
    re.MULTILINE | re.VERBOSE,
)

text, finished_count = finished_pattern.subn(
    "",
    text,
)

if finished_count != 1:
    print(
        "ERROR: Expected exactly one runner_finished "
        f"block, found {finished_count}."
    )
    sys.exit(1)

# ---------------------------------------------------------
# 4. Safety checks.
# ---------------------------------------------------------
if "update_job_progress" in text:
    print(
        "ERROR: update_job_progress still exists in "
        "the queue runner after patching."
    )
    sys.exit(1)

if text == original:
    print("ERROR: Patch produced no changes.")
    sys.exit(1)

path.write_text(
    text,
    encoding="utf-8",
    newline="\n",
)

print("PATCH_WRITE_OK")
print(f"Removed import lines: {import_count}")
print(f"Removed dequeue blocks: {dequeued_count}")
print(f"Removed finish blocks: {finished_count}")
