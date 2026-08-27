from __future__ import annotations

from pathlib import Path


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print(
    "=== U3.15 STEP 4 — STRUCTURAL SAFETY / CLEANUP ==="
)


files_path = Path(
    "backend/server/routes/files.py"
)

uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

extractor_path = Path(
    "backend/server/stores/"
    "upload_document_extractor.py"
)


files_text = files_path.read_text(
    encoding="utf-8",
    errors="replace",
)

uduc_text = uduc_path.read_text(
    encoding="utf-8",
    errors="replace",
)

extractor_text = extractor_path.read_text(
    encoding="utf-8",
    errors="replace",
)


# ------------------------------------------------------------
# A. Concurrency / atomic registry mutation
# ------------------------------------------------------------

print()
print("=== A. CONCURRENCY / ATOMIC INDEX CONTRACT ===")

check(
    "INDEX_LOCK_GUARD_PRESENT",
    "_INDEX_LOCKS_GUARD = threading.Lock()"
    in files_text,
)

check(
    "PER_INDEX_RLOCK_PRESENT",
    "threading.RLock()"
    in files_text,
)

check(
    "INDEX_LOCK_HELPER_PRESENT",
    "def _index_lock("
    in files_text,
)

check(
    "STORE_AND_INDEX_USES_INDEX_LOCK",
    "with _index_lock(idx_path):"
    in files_text,
)

check(
    "ATOMIC_TEMP_REPLACE_PRESENT",
    ".replace("
    in files_text,
)

check(
    "UUID_TEMP_FILE_SUPPORT_PRESENT",
    "uuid.uuid4"
    in files_text.lower()
    or "uuid4"
    in files_text.lower(),
)


# ------------------------------------------------------------
# B. Canonical UDUC handoff
# ------------------------------------------------------------

print()
print("=== B. UDUC HANDOFF BOUNDARY ===")

check(
    "UDUC_BUILDER_ACCEPTS_EXTRACTION_RESULT",
    "build_uduc_from_upload_extraction_result"
    in uduc_text,
)

check(
    "UDUC_BUILD_AND_WRITE_FROM_EXTRACTION_RESULT_PRESENT",
    "build_and_write_uduc_from_extraction_result"
    in uduc_text,
)

legacy_uduc_terms = [
    "_read_upload_index_hit",
    "index_hit.get",
    "data/uploads",
    "data\\uploads",
]

for term in legacy_uduc_terms:
    check(
        "NO_LEGACY_UDUC_"
        + term
        .replace("_", "")
        .replace("/", "")
        .replace("\\", "")
        .replace(".", "")
        .upper(),
        term.lower()
        not in uduc_text.lower(),
    )


# ------------------------------------------------------------
# C. Markdown correction remains canonical
# ------------------------------------------------------------

print()
print("=== C. MARKDOWN CORRECTIVE CONTRACT ===")

check(
    "STAR_CODE_REGEX_PRESENT",
    "_MD_STAR_OR_CODE_RE"
    in extractor_text,
)

check(
    "BOUNDARY_UNDERSCORE_REGEX_PRESENT",
    "_MD_UNDERSCORE_EMPHASIS_RE"
    in extractor_text,
)

check(
    "OLD_COMBINED_EMPHASIS_REGEX_ABSENT",
    "_MD_EMPHASIS_RE = re.compile"
    not in extractor_text,
)


# ------------------------------------------------------------
# D. Legacy worker/intake residue
# ------------------------------------------------------------

print()
print("=== D. LEGACY WORKER / INTAKE RESIDUE ===")

production_targets = [
    Path("backend/server/routes/files.py"),
    Path(
        "backend/server/pipelines/upload_document/"
        "coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/"
        "coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/"
        "upload_intake.py"
    ),
    Path(
        "backend/server/stores/"
        "upload_document_extractor.py"
    ),
    Path(
        "backend/server/stores/"
        "uploaded_document_unified_content.py"
    ),
]

combined = "\n".join(
    path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    for path in production_targets
)

legacy_terms = [
    "upload_worker",
    "upload worker",
    "upload_job",
    "upload job",
    "BackgroundTasks",
    "create_task",
    "run_in_executor",
    "data/uploads",
    "data\\uploads",
    "_read_upload_index_hit",
    "index_hit.get",
]

for term in legacy_terms:
    check(
        "NO_LEGACY_"
        + term
        .replace("_", "")
        .replace(" ", "")
        .replace("/", "")
        .replace("\\", "")
        .replace(".", "")
        .upper(),
        term.lower()
        not in combined.lower(),
    )


# ------------------------------------------------------------
# E. Live synthetic artifact sweep
# ------------------------------------------------------------

print()
print("=== E. LIVE U3 SYNTHETIC ARTIFACT SWEEP ===")

roots = [
    Path("backend/server/data/docs"),
    Path(
        "backend/server/data/"
        "uploaded_document_unified_content"
    ),
    Path(
        "backend/server/data/dis/"
        "rejection_patterns"
    ),
    Path(
        "backend/server/data/phrase_pools"
    ),
    Path(
        "backend/server/data/topic_clusters"
    ),
]

synthetic_markers = [
    "u3_13",
    "u3_14",
    "u3_15",
    "ws_phase2_worker_test",
]

hits = []

for root in roots:
    if not root.exists():
        continue

    for path in root.rglob("*"):
        name = path.name.lower()

        if any(
            marker in name
            for marker in synthetic_markers
        ):
            hits.append(path)


for hit in hits:
    print(
        "LIVE_SYNTHETIC_HIT:",
        hit,
    )

check(
    "LIVE_U3_SYNTHETIC_ARTIFACT_COUNT_ZERO",
    len(hits) == 0,
)


# ------------------------------------------------------------
# Final
# ------------------------------------------------------------

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U3.15_STRUCTURAL_SAFETY_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U3.15 structural safety verification failed."
    )

print(
    "U3.15_STRUCTURAL_SAFETY_VERIFICATION: PASS"
)