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

target = None

for i, line in enumerate(lines, start=1):
    if "raw_result = _call_by_signature_v1(" in line:
        target = i
        break

if target is None:
    raise RuntimeError(
        "The raw_result loader call was not found."
    )

start = max(1, target - 25)
end = min(len(lines), target + 110)

print()
print("=" * 112)
print("UDARE RAW HTML LOAD BLOCK INSPECTION")
print("=" * 112)
print("FILE:", WORKER)
print(f"LINES: {start}-{end}")
print("-" * 112)

for i in range(start, end + 1):
    marker = ">>> " if i == target else "    "
    print(f"{marker}{i:5}: {lines[i - 1]}")

print()
print("=" * 112)
print("END OF RAW HTML LOAD BLOCK")
print("=" * 112)
print("Read-only inspection complete.")
