from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path.cwd().resolve()

TARGET = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "uucd_runtime_handoff_v1.py"
)

print("=" * 92)
print("STAGE 10.10E - IDEMPOTENCY KEY FORMAT SCAN")
print("=" * 92)

print("TARGET:", TARGET)
print("TARGET_EXISTS:", TARGET.exists())

if not TARGET.exists():
    raise SystemExit("Target runtime handoff file not found.")

text = TARGET.read_text(encoding="utf-8")
lines = text.splitlines()


# ============================================================
# A. EXACT BUILDER
# ============================================================

print()
print("=" * 92)
print("A. EXACT IDEMPOTENCY BUILDER")
print("=" * 92)

start = None

for i, line in enumerate(lines):
    if line.startswith(
        "def build_uucd_runtime_idempotency_key_v1("
    ):
        start = i
        break

if start is None:
    print("BUILDER_NOT_FOUND")
else:
    end = len(lines)

    for i in range(start + 1, len(lines)):
        if (
            lines[i].startswith("def ")
            or lines[i].startswith("class ")
        ):
            end = i
            break

    for i in range(start, end):
        print(f"{i + 1:04d}: {lines[i]}")


# ============================================================
# B. TARGET REFERENCES
# ============================================================

print()
print("=" * 92)
print("B. IDEMPOTENCY REFERENCES IN HANDOFF")
print("=" * 92)

for i, line in enumerate(lines, start=1):
    lower = line.lower()

    if (
        "idempotency" in lower
        or "uucd_runtime_" in line
        or "sha256" in lower
    ):
        print(f"{i:04d}: {line}")


# ============================================================
# C. REPOSITORY REFERENCES
# ============================================================

print()
print("=" * 92)
print("C. REPOSITORY REFERENCES")
print("=" * 92)

patterns = (
    "uucd_runtime_handoff_",
    "uucd_runtime_",
    "build_uucd_runtime_idempotency_key_v1",
)

extensions = {
    ".py",
    ".json",
    ".md",
    ".txt",
}

skip_dirs = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    "tmp",
}

matches = []

for path in ROOT.rglob("*"):

    if not path.is_file():
        continue

    if path.suffix.lower() not in extensions:
        continue

    if any(
        part in skip_dirs
        for part in path.parts
    ):
        continue

    try:
        candidate = path.read_text(
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        try:
            candidate = path.read_text(
                encoding="utf-16"
            )
        except Exception:
            continue
    except Exception:
        continue

    for line_number, line in enumerate(
        candidate.splitlines(),
        start=1,
    ):
        if any(
            pattern in line
            for pattern in patterns
        ):
            matches.append(
                (
                    path,
                    line_number,
                    line.strip(),
                )
            )

print("TOTAL_MATCHES:", len(matches))

for path, line_number, line in matches:

    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        relative = path

    print()
    print("FILE:", relative)
    print("LINE:", line_number)
    print("TEXT:", line)


# ============================================================
# D. DISCOVER ACTUAL ORCHESTRATION JOB STORES
# ============================================================

print()
print("=" * 92)
print("D. ORCHESTRATION JOB STORE INVENTORY")
print("=" * 92)

candidate_stores = []

for path in (
    ROOT / "backend/server/data"
).rglob("*.json"):

    name = path.name.lower()
    full = str(path).lower()

    if (
        "job" in name
        or "orchestration" in full
    ):
        candidate_stores.append(path)

print(
    "CANDIDATE_JSON_STORES:",
    len(candidate_stores),
)

old_style_total = 0
frozen_style_total = 0

for path in candidate_stores:

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        continue

    if isinstance(data, dict):
        records = list(data.values())

    elif isinstance(data, list):
        records = data

    else:
        continue

    old_style = []
    frozen_style = []

    for record in records:

        if not isinstance(record, dict):
            continue

        metadata = record.get("metadata")

        if not isinstance(metadata, dict):
            continue

        key = metadata.get(
            "idempotency_key"
        )

        if not isinstance(key, str):
            continue

        summary = {
            "job_id":
                record.get("job_id"),

            "job_type":
                record.get("job_type"),

            "status":
                record.get("status"),

            "idempotency_key":
                key,
        }

        if re.fullmatch(
            r"uucd_runtime_[0-9a-f]{32}",
            key,
        ):
            old_style.append(summary)

        if re.fullmatch(
            r"uucd_runtime_handoff_[0-9a-f]{64}",
            key,
        ):
            frozen_style.append(summary)

    if old_style or frozen_style:

        print()
        print("STORE:", path)

        print(
            "OLD_STYLE_32_COUNT:",
            len(old_style),
        )

        print(
            "FROZEN_STYLE_64_COUNT:",
            len(frozen_style),
        )

        old_style_total += len(old_style)
        frozen_style_total += len(frozen_style)

        for item in old_style:
            print(
                "OLD_STYLE_JOB:",
                item,
            )

        for item in frozen_style:
            print(
                "FROZEN_STYLE_JOB:",
                item,
            )


# ============================================================
# E. SUMMARY
# ============================================================

print()
print("=" * 92)
print("E. SUMMARY")
print("=" * 92)

print(
    "EXPECTED_FROZEN_FORMAT:",
    "uucd_runtime_handoff_<64 lowercase sha256>",
)

print(
    "OBSERVED_TEST_FORMAT:",
    "uucd_runtime_<32 lowercase hex>",
)

print(
    "OLD_STYLE_PRODUCTION_COUNT:",
    old_style_total,
)

print(
    "FROZEN_STYLE_PRODUCTION_COUNT:",
    frozen_style_total,
)

print("PATCH_PERFORMED: False")
print("FILES_MODIFIED: False")
print("JOBS_CREATED: False")
print("JOBS_DEQUEUED: False")
print("JOB_STATUS_CHANGED: False")
print("RUNTIME_REGISTRATION_MODIFIED: False")

print("=" * 92)
print("SCAN COMPLETE")
print("=" * 92)
