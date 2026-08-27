from __future__ import annotations

from pathlib import Path


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


root = Path("backend/server")

production_files = [
    Path("backend/server/routes/files.py"),
    Path("backend/server/stores/upload_document_extractor.py"),
    Path("backend/server/stores/uploaded_document_unified_content.py"),
    Path("backend/server/pipelines/upload_document/coordinator.py"),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/upload_intake.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_highlight_pipeline/coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_registry_to_active_target_set_pipeline/coordinator.py"
    ),
]

check(
    "ALL_SCAN_TARGETS_EXIST",
    all(path.is_file() for path in production_files),
)


forbidden_terms = {
    "BACKGROUND_TASKS": "BackgroundTasks",
    "CREATE_TASK": "create_task",
    "RUN_IN_EXECUTOR": "run_in_executor",
    "UPLOAD_WORKER": "upload_worker",
    "UPLOAD_WORKER_TEXT": "upload worker",
    "UPLOAD_JOB": "upload_job",
    "UPLOAD_JOB_TEXT": "upload job",
    "CURRENT_CANONICAL_UUCD": "current canonical uucd",
    "UUCD_ENGINE": "uucd_engine",
    "UUCD_PERSISTENCE": "uucd_persistence",
    "UNIVERSAL_UUCD_MODULE": "universal_unified_content_document",
    "SEMANTIC_RUNTIME": "semantic_runtime",
    "SCORER_MODULE": "scorer.py",
    "RUN_SCORER": "run_scorer",
    "REGISTER_RUNTIME": "register_runtime",
}


print()
print("=== FORBIDDEN PREMATURE INTEGRATION TERMS ===")

all_hits = []

for label, term in forbidden_terms.items():
    hits = []

    for path in production_files:
        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        for line_no, line in enumerate(
            text.splitlines(),
            start=1,
        ):
            if term.lower() in line.lower():
                hits.append(
                    (
                        str(path),
                        line_no,
                        line.strip(),
                    )
                )

    check(
        f"NO_{label}",
        len(hits) == 0,
    )

    for path, line_no, line in hits:
        all_hits.append(
            (label, path, line_no, line)
        )

        print(
            f"HIT {label}: "
            f"{path}:{line_no}: {line}"
        )


print()
print("=== EXPECTED SYNCHRONOUS COMPATIBILITY FIELDS ===")

intake_path = Path(
    "backend/server/pipelines/upload_document/"
    "uploaded_document_to_uduc_pipeline/upload_intake.py"
)

intake_text = intake_path.read_text(
    encoding="utf-8"
)

check(
    "JOB_ID_NONE_PRESENT_ONCE",
    intake_text.count('"job_id": None') == 1,
)

check(
    "PROCESSING_NOT_APPLICABLE_PRESENT_ONCE",
    intake_text.count(
        '"processing_status": "not_applicable"'
    ) == 1,
)


print()
print("=== PIPELINE STOP-BOUNDARY CONTRACT ===")

top_path = Path(
    "backend/server/pipelines/upload_document/coordinator.py"
)

top_text = top_path.read_text(
    encoding="utf-8"
)

check(
    "UDUC_LAYER_PRESENT",
    "build_and_write_uduc_from_extraction_result("
    in top_text,
)

check(
    "HIGHLIGHT_BRANCH_PRESENT",
    "run_uploaded_document_to_highlight_pipeline("
    in top_text,
)

check(
    "ACTIVE_TARGET_SET_BRANCH_PRESENT",
    "run_uploaded_document_registry_to_active_target_set_pipeline("
    in top_text,
)

check(
    "NO_FORBIDDEN_PREMATURE_INTEGRATION_HITS",
    len(all_hits) == 0,
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
        "U3.14_PREMATURE_INTEGRATION_BOUNDARY_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U3.14 premature-integration boundary verification failed."
    )

print(
    "U3.14_PREMATURE_INTEGRATION_BOUNDARY_VERIFICATION: PASS"
)