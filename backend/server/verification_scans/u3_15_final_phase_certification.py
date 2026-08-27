from __future__ import annotations

from pathlib import Path


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def read_log(path: Path) -> str:
    if not path.is_file():
        return ""

    for encoding in (
        "utf-8-sig",
        "utf-16",
        "utf-8",
    ):
        try:
            return path.read_text(
                encoding=encoding
            )
        except UnicodeError:
            continue

    return ""


print(
    "=== U3.15 FINAL PHASE U3 CERTIFICATION ==="
)


# ------------------------------------------------------------
# A. Required Phase U3 certification evidence
# ------------------------------------------------------------

print()
print("=== A. REQUIRED CERTIFICATION EVIDENCE ===")

required_logs = {
    "U3_15_EVIDENCE": (
        Path(
            "backend/server/verification_scans/"
            "u3_15_certification_evidence_verification.txt"
        ),
        "U3.15_CERTIFICATION_EVIDENCE_VERIFICATION: PASS",
    ),

    "U3_15_LIVE_CONTRACT": (
        Path(
            "backend/server/verification_scans/"
            "u3_15_live_phase_contract_verification.txt"
        ),
        "U3.15_LIVE_PHASE_CONTRACT_VERIFICATION: PASS",
    ),

    "U3_15_BEHAVIORAL": (
        Path(
            "backend/server/verification_scans/"
            "u3_15_behavioral_contract_certification.txt"
        ),
        "U3.15_BEHAVIORAL_CONTRACT_CERTIFICATION: PASS",
    ),

    "U3_15_STRUCTURAL": (
        Path(
            "backend/server/verification_scans/"
            "u3_15_structural_safety_verification.txt"
        ),
        "U3.15_STRUCTURAL_SAFETY_VERIFICATION: PASS",
    ),

    "U3_14_INTEGRATION": (
        Path(
            "backend/server/verification_scans/"
            "u3_14_final_certification.txt"
        ),
        "U3.14_FINAL_CERTIFICATION: PASS",
    ),

    "U3_14_SMOKE": (
        Path(
            "backend/server/verification_scans/"
            "u3_14_full_integration_smoke_verification.txt"
        ),
        "U3.14_FULL_INTEGRATION_SMOKE_VERIFICATION: PASS",
    ),
}


for label, (path, marker) in required_logs.items():
    check(
        f"{label}_LOG_EXISTS",
        path.is_file(),
    )

    content = read_log(path)

    check(
        f"{label}_PASS_MARKER",
        marker in content,
    )


check(
    "ALL_FINAL_CERTIFICATION_EVIDENCE_PRESENT",
    all(
        path.is_file()
        for path, _marker
        in required_logs.values()
    ),
)

check(
    "ALL_FINAL_CERTIFICATION_EVIDENCE_PASS",
    all(
        marker in read_log(path)
        for path, marker
        in required_logs.values()
    ),
)


# ------------------------------------------------------------
# B. Canonical Phase U3 production boundary
# ------------------------------------------------------------

print()
print("=== B. CANONICAL PHASE U3 BOUNDARY ===")

import backend.server.routes.files as files_route

routes = [
    route
    for route in files_route.router.routes
    if getattr(route, "path", "")
    == "/api/files/upload"
    and "POST"
    in set(
        getattr(route, "methods", set())
        or set()
    )
]

check(
    "ONE_CANONICAL_UPLOAD_ROUTE",
    len(routes) == 1,
)


top_path = Path(
    "backend/server/pipelines/"
    "upload_document/coordinator.py"
)

top_text = top_path.read_text(
    encoding="utf-8",
    errors="replace",
)

stages = [
    "run_uploaded_document_to_uduc_pipeline(",
    "build_and_write_uduc_from_extraction_result(",
    "run_uploaded_document_to_highlight_pipeline(",
    "run_uploaded_document_registry_to_active_target_set_pipeline(",
]

positions = [
    top_text.find(stage)
    for stage in stages
]

check(
    "PHASE_U3_STAGE_CHAIN_COMPLETE",
    all(
        position >= 0
        for position in positions
    ),
)

check(
    "PHASE_U3_STAGE_CHAIN_ORDERED",
    all(
        position >= 0
        for position in positions
    )
    and positions
    == sorted(positions),
)


print()
print("CANONICAL_PHASE_U3_BOUNDARY:")
print("Uploaded Document")
print("  -> POST /api/files/upload")
print("  -> Upload Route")
print("  -> Upload Intake")
print("  -> Dedicated Upload Extractor")
print("  -> UploadExtractionResult")
print("  -> UDUC")
print("  -> Highlight")
print("  -> Registry -> Active Target Set Pre-validation")
print("  -> STOP")


# ------------------------------------------------------------
# C. Current approved stop boundary
# ------------------------------------------------------------

print()
print("=== C. PHASE U3 STOP BOUNDARY ===")

production_targets = [
    Path("backend/server/routes/files.py"),
    Path(
        "backend/server/pipelines/"
        "upload_document/coordinator.py"
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

forbidden = [
    "BackgroundTasks",
    "create_task",
    "run_in_executor",
    "upload_worker",
    "upload worker",
    "upload_job",
    "upload job",
    "uucd_engine",
    "uucd_persistence",
    "universal_unified_content_document",
    "semantic_runtime",
    "run_scorer",
    "register_runtime",
]

check(
    "NO_PREMATURE_EXECUTION_BEYOND_PHASE_U3",
    all(
        term.lower()
        not in combined.lower()
        for term in forbidden
    ),
)


check(
    "WEBSITE_CLEANER_ISOLATION_RETAINED",
    "article_body_cleaning_engine"
    not in combined
    and "article_cleaning_pipeline"
    not in combined,
)


# ------------------------------------------------------------
# D. Exact upload format / synchronous contract
# ------------------------------------------------------------

print()
print("=== D. UPLOAD CONTRACT ===")

expected_extensions = {
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
}

check(
    "PHASE_U3_SIX_FORMAT_ALLOWLIST",
    set(files_route.ALLOWED_EXT)
    == expected_extensions,
)


from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
    upload_intake,
)

check(
    "PHASE_U3_250_MIB_CEILING",
    upload_intake.MAX_UPLOAD_BYTES
    == 250 * 1024 * 1024,
)


intake_path = Path(
    "backend/server/pipelines/upload_document/"
    "uploaded_document_to_uduc_pipeline/"
    "upload_intake.py"
)

intake_text = intake_path.read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "PHASE_U3_JOB_ID_NONE",
    intake_text.count(
        '"job_id": None'
    ) == 1,
)

check(
    "PHASE_U3_PROCESSING_NOT_APPLICABLE",
    intake_text.count(
        '"processing_status": "not_applicable"'
    ) == 1,
)


# ------------------------------------------------------------
# E. Legacy UDUC / Markdown protections
# ------------------------------------------------------------

print()
print("=== E. UDUC / MARKDOWN PROTECTIONS ===")

uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

uduc_text = uduc_path.read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "NO_UDUC_REGISTRY_REREAD",
    "_read_upload_index_hit"
    not in uduc_text
    and "index_hit.get"
    not in uduc_text,
)

check(
    "NO_LEGACY_DATA_UPLOADS_FALLBACK",
    "data/uploads"
    not in uduc_text.lower()
    and "data\\uploads"
    not in uduc_text.lower(),
)


extractor_path = Path(
    "backend/server/stores/"
    "upload_document_extractor.py"
)

extractor_text = extractor_path.read_text(
    encoding="utf-8",
    errors="replace",
)

check(
    "MARKDOWN_INTRAWORD_UNDERSCORE_FIX_PRESENT",
    "_MD_UNDERSCORE_EMPHASIS_RE"
    in extractor_text,
)

check(
    "MARKDOWN_STAR_CODE_FIX_PRESENT",
    "_MD_STAR_OR_CODE_RE"
    in extractor_text,
)


# ------------------------------------------------------------
# F. Live synthetic artifact sweep
# ------------------------------------------------------------

print()
print("=== F. LIVE SYNTHETIC ARTIFACT SWEEP ===")

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
        "backend/server/data/"
        "phrase_pools"
    ),
    Path(
        "backend/server/data/"
        "topic_clusters"
    ),
]

markers = [
    "u3_13",
    "u3_14",
    "u3_15",
    "ws_phase2_worker_test",
]

live_hits = []

for root in roots:
    if not root.exists():
        continue

    for path in root.rglob("*"):
        name = path.name.lower()

        if any(
            marker in name
            for marker in markers
        ):
            live_hits.append(path)


for path in live_hits:
    print(
        "LIVE_SYNTHETIC_HIT:",
        path,
    )

check(
    "ZERO_LIVE_U3_SYNTHETIC_ARTIFACTS",
    len(live_hits) == 0,
)


# ------------------------------------------------------------
# G. Phase status
# ------------------------------------------------------------

print()
print("=== G. PHASE U3 STATUS ===")

check(
    "U3_1_THROUGH_U3_14_EVIDENCE_COMPLETE",
    all(
        marker in read_log(path)
        for path, marker
        in required_logs.values()
    ),
)


failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "PHASE_U3_DOCUMENT_UPLOAD_WORKER_INTAKE_REALIGNMENT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "Phase U3 final certification failed."
    )


print(
    "PHASE_U3_DOCUMENT_UPLOAD_WORKER_INTAKE_REALIGNMENT: CERTIFIED"
)

print(
    "PHASE_U3_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "PHASE_U4_FORMAT_DETECTION_TRANSITION: AUTHORIZED"
)

print(
    "U3.15_FINAL_PHASE_CERTIFICATION: PASS"
)