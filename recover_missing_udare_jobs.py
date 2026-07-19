from __future__ import annotations

import json
from pathlib import Path

from backend.server.jobs.universal_knowledge_orchestrator import (
    read_queue,
)

WORKSPACE = "ws_whattoexpect_com"

runtime_root = Path("backend/server/data")

queue = read_queue(
    WORKSPACE,
    limit=100000,
)

current_job_ids = {
    str(j.get("job_id"))
    for j in queue
    if j.get("job_id")
}

print("=" * 100)
print("RECOVER MISSING UDARE JOBS")
print("=" * 100)
print()

print("Current queue rows:", len(queue))
print("Current queue job ids:", len(current_job_ids))
print()

locations = []

for path in runtime_root.rglob("*"):
    if not path.is_file():
        continue

    if path.suffix.lower() not in (
        ".json",
        ".jsonl",
    ):
        continue

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        continue

    found = []

    if path.suffix.lower() == ".json":
        try:
            obj = json.loads(text)

            if isinstance(obj, dict):
                job_id = obj.get("job_id")

                if job_id and job_id not in current_job_ids:
                    found.append(job_id)

            elif isinstance(obj, list):
                for row in obj:
                    if isinstance(row, dict):
                        job_id = row.get("job_id")
                        if job_id and job_id not in current_job_ids:
                            found.append(job_id)

        except Exception:
            pass

    else:
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                if isinstance(row, dict):
                    job_id = row.get("job_id")
                    if job_id and job_id not in current_job_ids:
                        found.append(job_id)
            except Exception:
                pass

    if found:
        locations.append(
            (
                path,
                sorted(set(found)),
            )
        )

print("FILES CONTAINING JOBS NOT IN ACTIVE QUEUE")
print("-" * 100)

total = 0

for path, jobs in locations:
    print()
    print(path)

    for job in jobs:
        print("   ", job)

    total += len(jobs)

print()
print("-" * 100)
print("Recovered job references:", total)
print("=" * 100)
