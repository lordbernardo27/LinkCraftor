from pathlib import Path

WORKER = Path(
    "backend/server/workers/udare_reconstruction_worker.py"
)

if not WORKER.is_file():
    raise RuntimeError(f"Worker not found: {WORKER}")

lines = WORKER.read_text(
    encoding="utf-8-sig",
    errors="replace",
).splitlines()

start = None
end = None

for i, line in enumerate(lines, start=1):
    if line.startswith("def run_udare_reconstruction_job_v1"):
        start = i
        break

if start is None:
    raise RuntimeError(
        "run_udare_reconstruction_job_v1() not found."
    )

for i in range(start, len(lines) + 1):
    if "_call_by_signature_v1(" in lines[i - 1]:
        end = min(len(lines), i + 25)
        break

if end is None:
    end = min(len(lines), start + 250)

print()
print("=" * 112)
print("UDARE WORKER INITIALIZATION TRACE")
print("=" * 112)
print("FILE:", WORKER)
print(f"LINES: {start}-{end}")
print("-" * 112)

for i in range(start, end + 1):
    print(f"{i:5}: {lines[i-1]}")

print()
print("=" * 112)
print("END OF TRACE")
print("=" * 112)
print("Read-only inspection complete.")
