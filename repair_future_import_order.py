from pathlib import Path

path = Path(
    "backend/server/workers/universal_knowledge_queue_runner.py"
)

lines = path.read_text(
    encoding="utf-8-sig"
).splitlines()

future_line = None
datetime_line = None
uuid_line = None

for i, line in enumerate(lines):
    s = line.strip()

    if s == "from __future__ import annotations":
        future_line = i

    elif s == "from datetime import datetime, timezone":
        datetime_line = i

    elif s == "import uuid":
        uuid_line = i

if future_line is None:
    raise RuntimeError(
        "__future__ import not found."
    )

extra = []

if datetime_line is not None:
    extra.append(
        lines[datetime_line]
    )

if uuid_line is not None:
    extra.append(
        lines[uuid_line]
    )

remove = {
    i
    for i in (
        datetime_line,
        uuid_line,
    )
    if i is not None
}

clean = [
    line
    for index, line in enumerate(lines)
    if index not in remove
]

future_index = clean.index(
    "from __future__ import annotations"
)

insert_at = future_index + 1

for value in reversed(extra):
    clean.insert(
        insert_at,
        value,
    )

path.write_text(
    "\n".join(clean) + "\n",
    encoding="utf-8",
)

print("IMPORT ORDER REPAIRED")
