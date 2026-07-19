from pathlib import Path
from backend.server.jobs.universal_knowledge_orchestrator import queue_path, read_queue

ws = "ws_whattoexpect_com"

print("=" * 90)
print("ACTIVE QUEUE INSPECTION")
print("=" * 90)

active = queue_path(ws)

print("queue_path()")
print(active)
print()

print("Exists:", active.exists())

if active.exists():
    print("Size:", active.stat().st_size)

rows = read_queue(ws, limit=100000)

print()
print("Rows returned:", len(rows))

udare = [
    r for r in rows
    if (r.get("job_type") or r.get("stage") or "") == "udare_reconstruction"
]

print("UDARE jobs:", len(udare))

print()
print("Possible queue.jsonl files:")

for p in Path("backend/server/data").rglob("queue*.jsonl"):
    print(" -", p)

print("=" * 90)
