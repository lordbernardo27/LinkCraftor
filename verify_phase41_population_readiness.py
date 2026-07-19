from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path("backend/server/data")

candidate_files = []

for pattern in (
    "*raw*html*.json",
    "*raw*html*.jsonl",
    "*raw*website*.json",
    "*raw*website*.jsonl",
    "*html_store*.json",
    "*html_store*.jsonl",
):
    candidate_files.extend(ROOT.rglob(pattern))

candidate_files = sorted(set(candidate_files))

print()
print("RAW HTML STORE CANDIDATES")
print("-------------------------")

for f in candidate_files:
    print(f)

records = []

for file in candidate_files:
    try:
        if file.suffix == ".jsonl":
            for line in file.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        else:
            data = json.loads(file.read_text(encoding="utf-8", errors="replace"))
            if isinstance(data, list):
                records.extend(data)
            elif isinstance(data, dict):
                if isinstance(data.get("records"), list):
                    records.extend(data["records"])
                elif isinstance(data.get("items"), list):
                    records.extend(data["items"])
    except Exception:
        pass

print()
print(f"Total records discovered: {len(records)}")

workspace_counter = Counter()
ids = set()
duplicates = []
missing_html = 0
missing_workspace = 0
missing_identifier = 0

manifest = []

for r in records:

    workspace = (
        r.get("workspace_id")
        or r.get("workspace")
        or ""
    )

    if not workspace:
        missing_workspace += 1

    workspace_counter[workspace] += 1

    identifier = (
        r.get("page_id")
        or r.get("content_id")
        or r.get("url_hash")
        or r.get("id")
    )

    if not identifier:
        missing_identifier += 1
        identifier = "__missing__"

    if identifier in ids:
        duplicates.append(identifier)

    ids.add(identifier)

    html = (
        r.get("raw_html")
        or r.get("html")
        or ""
    )

    if not html:
        missing_html += 1

    manifest.append({
        "workspace_id": workspace,
        "identifier": identifier,
        "sha256": hashlib.sha256(
            html.encode("utf-8", errors="replace")
        ).hexdigest(),
        "bytes": len(
            html.encode("utf-8", errors="replace")
        ),
    })

report_dir = ROOT / "runtime" / "udare_population_readiness"
report_dir.mkdir(parents=True, exist_ok=True)

manifest_path = report_dir / "population_manifest.json"

manifest_path.write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

checks = {
    "records_found": len(records) > 0,
    "missing_workspace": missing_workspace == 0,
    "missing_identifier": missing_identifier == 0,
    "duplicate_identifiers": len(duplicates) == 0,
    "missing_html": missing_html == 0,
}

failed = [
    k for k,v in checks.items() if not v
]

print()
print("CHECKS")
print("------")

for k,v in checks.items():
    print(f"{k}: {'PASS' if v else 'FAIL'}")

print()
print("Workspace counts")
for ws,count in workspace_counter.items():
    print(f"  {ws}: {count}")

print()
print(f"Manifest: {manifest_path}")

print()

if failed:
    print("PHASE 4.1 READINESS: FAIL")
    print("Failed:", ", ".join(failed))
    raise SystemExit(1)

print("PHASE 4.1 READINESS: PASS")
print("No jobs created.")
print("No worker executed.")
print("No UDARE Store population performed.")
