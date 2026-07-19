from pathlib import Path

path = Path(
    "backend/server/workers/"
    "udare_reconstruction_worker.py"
)

text = path.read_text(
    encoding="utf-8",
    errors="replace",
)

matches = []

for line_number, line in enumerate(
    text.splitlines(),
    start=1,
):
    if "build_udare_store_index" in line:
        matches.append(
            (
                line_number,
                line,
            )
        )

print()
print("=" * 90)
print("UDARE INDEX WORKER CALL INSPECTION")
print("=" * 90)

if not matches:
    print("No index-builder reference found.")
    raise SystemExit(1)

for line_number, line in matches:
    print(
        f"{line_number}: {line}"
    )

print()
print("INDEX BUILDER REFERENCES FOUND:", len(matches))
print("=" * 90)
