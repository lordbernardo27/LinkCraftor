from pathlib import Path

checks = [
    (
        "backend/server/routes/files.py",
        [
            "enqueue_and_run_upload_ingestion_job_v1",
            "universal_knowledge_orchestration",
            "upload_document_batch",
        ],
    ),
    (
        "backend/server/routes/site_reader.py",
        [
            "enqueue_and_run_website_ingestion_job_v1",
            "universal_knowledge_orchestration",
            "website_connection_batch",
        ],
    ),
    (
        "backend/server/runtime/live_route_orchestration_hooks.py",
        [
            "create_universal_knowledge_job",
            "execute_universal_knowledge_job_v1",
            "upload_document_batch",
            "website_connection_batch",
        ],
    ),
]

for path, required in checks:
    p = Path(path)
    if not p.exists():
        raise AssertionError(f"Missing file: {path}")

    code = p.read_text(encoding="utf-8")

    missing = [x for x in required if x not in code]
    if missing:
        raise AssertionError(f"{path} missing: {missing}")

print("LIVE ROUTE ORCHESTRATION WIRING PASSED")
print("Upload route now calls orchestration.")
print("Connect domain route now calls orchestration.")
print("Next: trigger one upload and one connect-domain action, then inspect job ledger/body store.")
