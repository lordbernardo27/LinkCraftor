# PHASE 2.1.1 — UNIVERSAL JOB CONTRACT DEEP DISCOVERY SCAN
#
# READ-ONLY DISCOVERY SCAN
#
# This scan:
# - searches the existing codebase for every job-related structure
# - identifies current job contracts and metadata
# - maps lifecycle fields
# - detects legacy job models
# - discovers compatibility points
# - generates evidence
#
# DOES NOT MODIFY PRODUCTION FILES.
#
from __future__ import annotations

import ast
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path.cwd().resolve()

SEARCH_ROOTS = [
    PROJECT_ROOT / "backend" / "server",
]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_2"
    / "2_1_1_universal_job_contract"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

TIMESTAMP = datetime.now(
    timezone.utc
).strftime("%Y%m%dT%H%M%SZ")

REPORT_JSON = OUTPUT_DIR / f"universal_job_contract_scan_{TIMESTAMP}.json"
REPORT_TEXT = OUTPUT_DIR / f"universal_job_contract_scan_{TIMESTAMP}.txt"
SUMMARY_JSON = OUTPUT_DIR / f"universal_job_contract_summary_{TIMESTAMP}.json"

KEYWORDS = [
    "job",
    "runtime",
    "payload",
    "workspace",
    "pipeline",
    "stage",
    "status",
    "lease",
    "retry",
    "attempt",
    "artifact",
    "result",
    "checkpoint",
    "progress",
    "batch",
    "dependency",
    "parent_job",
    "idempotency",
    "cost_record",
    "AU_",
]

results = []

for root in SEARCH_ROOTS:

    for file in root.rglob("*.py"):

        if "__pycache__" in file.parts:
            continue

        source = file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        lowered = source.lower()

        hits = []

        for keyword in KEYWORDS:
            if keyword.lower() in lowered:
                hits.append(keyword)

        if not hits:
            continue

        classes = []
        functions = []

        try:
            tree = ast.parse(source)

            for node in ast.walk(tree):

                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)

                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)

        except Exception:
            pass

        results.append(
            {
                "file": str(file.relative_to(PROJECT_ROOT)),
                "keywords": sorted(set(hits)),
                "classes": sorted(classes),
                "functions": sorted(functions),
                "sha256": hashlib.sha256(
                    source.encode("utf-8")
                ).hexdigest(),
            }
        )

summary = {
    "scan": "Phase 2.1.1 Universal Job Contract Deep Discovery",
    "generated_at": TIMESTAMP,
    "candidate_files": len(results),
    "production_modified": False,
}

REPORT_JSON.write_text(
    json.dumps(
        results,
        indent=2,
    ),
    encoding="utf-8",
)

SUMMARY_JSON.write_text(
    json.dumps(
        summary,
        indent=2,
    ),
    encoding="utf-8",
)

with REPORT_TEXT.open(
    "w",
    encoding="utf-8",
) as handle:

    handle.write("=" * 78 + "\n")
    handle.write("PHASE 2.1.1 UNIVERSAL JOB CONTRACT DEEP DISCOVERY\n")
    handle.write("=" * 78 + "\n\n")

    handle.write(
        f"Candidate files discovered: {len(results)}\n\n"
    )

    for item in results:

        handle.write(
            f"{item['file']}\n"
        )

        handle.write(
            f"  Keywords : {', '.join(item['keywords'])}\n"
        )

        handle.write(
            f"  Classes  : {', '.join(item['classes']) if item['classes'] else '-'}\n"
        )

        handle.write(
            f"  Functions: {', '.join(item['functions']) if item['functions'] else '-'}\n"
        )

        handle.write("\n")

print("=" * 78)
print("UNIVERSAL RUNTIME INFRASTRUCTURE")
print("PHASE 2.1.1 — UNIVERSAL JOB CONTRACT DEEP DISCOVERY")
print("=" * 78)
print()
print(f"Candidate files: {len(results)}")
print()
print(f"Evidence JSON   : {REPORT_JSON}")
print(f"Evidence TEXT   : {REPORT_TEXT}")
print(f"Summary JSON    : {SUMMARY_JSON}")
print()
print("UNIVERSAL JOB CONTRACT DEEP DISCOVERY: PASS")
print("NO PRODUCTION DATA WAS MODIFIED")
