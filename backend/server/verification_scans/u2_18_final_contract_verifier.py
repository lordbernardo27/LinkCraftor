from pathlib import Path
import inspect
import re
import traceback

ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")

try:
    import backend.server.routes.files as files
    import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as intake

    FILES_PY = ROOT / "backend/server/routes/files.py"
    INTAKE_PY = ROOT / "backend/server/pipelines/upload_document/uploaded_document_to_uduc_pipeline/upload_intake.py"
    TOP_COORD = ROOT / "backend/server/pipelines/upload_document/coordinator.py"
    UDUC_COORD = ROOT / "backend/server/pipelines/upload_document/uploaded_document_to_uduc_pipeline/coordinator.py"
    EXTRACTOR = ROOT / "backend/server/stores/upload_document_extractor.py"
    UDUC_STORE = ROOT / "backend/server/stores/uploaded_document_unified_content.py"

    APP_JS = ROOT / "frontend/public/assets/js/app.js"
    API_JS = ROOT / "frontend/public/assets/js/app/api.js"
    INDEX_HTML = ROOT / "frontend/public/index.html"

    def read(path):
        return path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )

    def require(condition, message):
        if not condition:
            raise AssertionError(message)

    files_src = read(FILES_PY)
    intake_src = read(INTAKE_PY)
    top_src = read(TOP_COORD)
    uduc_coord_src = read(UDUC_COORD)
    extractor_src = read(EXTRACTOR)
    uduc_store_src = read(UDUC_STORE)

    app_src = read(APP_JS)
    api_src = read(API_JS)
    index_src = read(INDEX_HTML)

    print("=== U2.18 ROUTE CONTRACT ===")

    upload_route_count = len(
        re.findall(
            r'@router\.post\(\s*["\']/upload["\']\s*\)',
            files_src,
        )
    )

    require(
        upload_route_count == 1,
        f"Expected exactly one files.py upload route, found {upload_route_count}",
    )

    upload_fn = inspect.getsource(files.upload_file)

    require(
        re.search(
            r'workspace_id\s*:\s*str\s*=\s*Query\(',
            upload_fn,
        ),
        "workspace_id query contract missing.",
    )

    require(
        re.search(
            r'file\s*:\s*UploadFile\s*=\s*File\(',
            upload_fn,
        ),
        'Multipart field "file" contract missing.',
    )

    print("CANONICAL_UPLOAD_ROUTE: PASS")
    print("WORKSPACE_QUERY_CONTRACT: PASS")
    print("MULTIPART_FILE_FIELD: PASS")

    print("")
    print("=== U2.18 FORMAT CONTRACT ===")

    expected_ext = {
        ".docx",
        ".txt",
        ".md",
        ".markdown",
        ".html",
        ".htm",
    }

    actual_ext = set(files.ALLOWED_EXT)

    require(
        actual_ext == expected_ext,
        f"Unexpected ALLOWED_EXT: {sorted(actual_ext)}",
    )

    print("SIX_FORMAT_BACKEND_CONTRACT: PASS")
    print("ALLOWED_EXTENSIONS:", ",".join(sorted(actual_ext)))

    print("")
    print("=== U2.18 REQUEST VALIDATION ===")

    run_intake_src = inspect.getsource(
        intake.run_upload_intake
    )

    require(
        hasattr(intake, "MAX_UPLOAD_BYTES"),
        "MAX_UPLOAD_BYTES missing.",
    )

    require(
        intake.MAX_UPLOAD_BYTES == 250 * 1024 * 1024,
        f"Unexpected upload limit: {intake.MAX_UPLOAD_BYTES}",
    )

    require(
        "MAX_UPLOAD_BYTES + 1" in run_intake_src,
        "Upload read is not bounded at MAX + 1.",
    )

    require(
        "413" in run_intake_src,
        "HTTP 413 oversized-file rejection missing.",
    )

    require(
        "Uploaded file is empty." in run_intake_src,
        "Empty upload rejection missing.",
    )

    require(
        "if extension not in allowed_extensions:" in run_intake_src
        and "File type not allowed:" in run_intake_src,
        "Unsupported-format rejection contract missing.",
    )

    print("UPLOAD_LIMIT_250_MIB: PASS")
    print("BOUNDED_UPLOAD_READ: PASS")
    print("EMPTY_FILE_REJECTION: PASS")
    print("OVERSIZE_413_CONTRACT: PASS")
    print("FORMAT_REJECTION_CONTRACT: PASS")

    print("")
    print("=== U2.18 DOCUMENT IDENTITY ===")

    store_src = inspect.getsource(
        files._store_and_index
    )

    require(
        store_src.count("uuid.uuid4().hex") == 1,
        "Canonical upload storage must create exactly one document UUID.",
    )

    require(
        "uuid.uuid4()" not in (
            top_src + "\n" + uduc_coord_src
        ),
        "Downstream upload pipeline creates a competing UUID.",
    )

    print("SINGLE_CANONICAL_DOCUMENT_UUID: PASS")
    print("NO_DOWNSTREAM_COMPETING_UUID: PASS")

    print("")
    print("=== U2.18 STORAGE CONTRACT ===")

    require(
        "_safe_upload_filename" in store_src,
        "Safe filename contract missing.",
    )

    require(
        'stored_name = f"{doc_id}__{safe_name}"' in store_src,
        "Server-generated stored filename missing.",
    )

    require(
        "ws_dir = _ws_dir(workspace_id)" in store_src,
        "Workspace-confined storage missing.",
    )

    require(
        "stored_path.write_bytes(raw)" in store_src,
        "Source persistence missing.",
    )

    print("SAFE_FILENAME_CONTRACT: PASS")
    print("SERVER_GENERATED_STORED_NAME: PASS")
    print("WORKSPACE_CONFINED_STORAGE: PASS")
    print("SOURCE_PERSISTENCE: PASS")

    print("")
    print("=== U2.18 REGISTRY INTEGRITY ===")

    strict_src = inspect.getsource(
        files._strict_read_index_for_update
    )

    h1_src = inspect.getsource(
        files._update_index_h1
    )

    require(
        "_strict_read_index_for_update(idx_path)" in store_src,
        "Upload mutation does not use strict registry reader.",
    )

    require(
        "_safe_read_index(" not in store_src,
        "Upload mutation still uses tolerant reader.",
    )

    require(
        "with _index_lock(idx_path):" in store_src,
        "Upload mutation is not locked.",
    )

    require(
        "stored_path.unlink(missing_ok=True)" in store_src,
        "Failed index commit lacks source rollback.",
    )

    require(
        "with _index_lock(idxp):" in h1_src,
        "H1 mutation is not locked.",
    )

    require(
        "_strict_read_index_for_update(idxp)" in h1_src,
        "H1 mutation is not fail-closed.",
    )

    require(
        "if not isinstance(data, list)" in strict_src,
        "Registry root validation missing.",
    )

    require(
        "any(not isinstance(item, dict) for item in data)"
        in strict_src,
        "Registry record validation missing.",
    )

    print("REGISTRY_FAIL_CLOSED_CONTRACT: PASS")
    print("REGISTRY_UPLOAD_LOCK: PASS")
    print("REGISTRY_H1_LOCK: PASS")
    print("FAILED_COMMIT_SOURCE_ROLLBACK: PASS")
    print("STRICT_REGISTRY_STRUCTURE_VALIDATION: PASS")

    print("")
    print("=== U2.18 EXTRACTION / UDUC ===")

    require(
        "extract_upload_document_v1" in intake_src,
        "Dedicated Upload Extractor not wired.",
    )

    require(
        "article_body_cleaning_engine" not in intake_src
        and "article_cleaning_pipeline" not in intake_src,
        "Website cleaning leaked into Uploaded Document.",
    )

    require(
        "UploadExtractionResult" in extractor_src,
        "UploadExtractionResult missing.",
    )

    require(
        "build_uduc_from_upload_extraction_result"
        in uduc_store_src,
        "UDUC extraction-result builder missing.",
    )

    require(
        "run_upload_intake" in uduc_coord_src,
        "UDUC pipeline does not consume canonical intake.",
    )

    print("DEDICATED_UPLOAD_EXTRACTOR: PASS")
    print("WEBSITE_CLEANER_ISOLATION: PASS")
    print("UPLOAD_EXTRACTION_RESULT_CONTRACT: PASS")
    print("UDUC_FROM_DEDICATED_EXTRACTION: PASS")

    print("")
    print("=== U2.18 DOWNSTREAM STOP BOUNDARY ===")

    upload_branch = (
        top_src
        + "\n"
        + uduc_coord_src
        + "\n"
        + intake_src
    )

    for forbidden in (
        "document_upload_job",
        "create_orchestration_job",
        "uucd_engine_v1",
        "build_transient_uucd_from_wuc_v1",
        "semantic_runtime",
        "resolver_runtime",
        "/api/jobs",
    ):
        require(
            forbidden not in upload_branch,
            f"Premature downstream reference: {forbidden}",
        )

    require(
        '"job_id": None' in upload_fn,
        "job_id is not explicitly None.",
    )

    require(
        '"processing_status": "not_applicable"' in upload_fn,
        "processing_status contract missing.",
    )

    print("NO_PREMATURE_JOB_EXECUTION: PASS")
    print("NO_PREMATURE_UUCD_EXECUTION: PASS")
    print("NO_PREMATURE_RUNTIME_EXECUTION: PASS")
    print("JOB_ID_NONE: PASS")
    print("PROCESSING_STATUS_NOT_APPLICABLE: PASS")

    print("")
    print("=== U2.18 PUBLIC RESPONSE ===")

    require(
        "public_response = {" in upload_fn,
        "Explicit response whitelist missing.",
    )

    for forbidden_public in (
        '"pipelines"',
        '"source_path"',
        '"extraction_result"',
    ):
        require(
            forbidden_public not in upload_fn,
            f"Internal response field exposed: {forbidden_public}",
        )

    require(
        "Upload processing failed." in upload_fn,
        "Generic upload exception response missing.",
    )

    require(
        "Upload processing did not complete successfully."
        in upload_fn,
        "Generic coordinator failure response missing.",
    )

    for field in (
        '"filename"',
        '"ext"',
        '"text"',
        '"html"',
        '"workspace_id"',
        '"doc"',
    ):
        require(
            field in upload_fn,
            f"Frontend response field missing: {field}",
        )

    print("PUBLIC_RESPONSE_WHITELIST: PASS")
    print("NO_INTERNAL_PATH_EXPOSURE: PASS")
    print("SANITIZED_PUBLIC_ERRORS: PASS")
    print("FRONTEND_REQUIRED_RESPONSE_FIELDS: PASS")

    print("")
    print("=== U2.18 FRONTEND CONTRACT ===")

    require(
        '".docx,.md,.markdown,.html,.htm,.txt"'
        in app_src,
        "Six-format frontend accept list missing.",
    )

    require(
        'if (value === ".markdown") return ".md";'
        in app_src,
        ".markdown → .md family mapping missing.",
    )

    require(
        'if (value === ".htm") return ".html";'
        in app_src,
        ".htm → .html family mapping missing.",
    )

    require(
        'data-accept=".md,.markdown"' in index_src,
        "Markdown aliases missing from menu.",
    )

    require(
        'data-accept=".html,.htm"' in index_src,
        "HTML aliases missing from menu.",
    )

    require(
        'fd.append("file", file);' in api_src,
        "Original physical File is not forwarded.",
    )

    require(
        "/api/files/upload?workspace_id=" in api_src,
        "Canonical frontend upload endpoint missing.",
    )

    require(
        "/api/upload" not in api_src,
        "Legacy frontend upload endpoint remains.",
    )

    print("FRONTEND_SIX_FORMAT_PICKER: PASS")
    print("MARKDOWN_FAMILY_ALIAS: PASS")
    print("HTM_FAMILY_ALIAS: PASS")
    print("ORIGINAL_FILE_FORWARDED: PASS")
    print("FRONTEND_CANONICAL_ENDPOINT: PASS")

    print("")
    print("=== U2.18 LEGACY CLEANUP ===")

    obsolete_files = (
        ROOT / "backend/server/stores/upload_normalizer.py",
        ROOT / "backend/server/stores/upload_intel_store_v2.py",
        ROOT / "backend/server/stores/upload_intel_store_old.py",
        ROOT / "backend/server/stores/upload_phrase_pool_builder_backup_before_v2.py",
        ROOT / "server.py",
        ROOT / "start_server.pre_u1_2_fastapi.ps1",
    )

    for path in obsolete_files:
        require(
            not path.exists(),
            f"Obsolete production file exists: {path}",
        )

    active_source_parts = []

    for path in (
        ROOT / "backend/server"
    ).rglob("*.py"):

        normalized = str(path).replace("\\", "/")

        if "/backups/" in normalized:
            continue

        if "/runtime_backups/" in normalized:
            continue

        if "/verification_scans/" in normalized:
            continue

        active_source_parts.append(
            read(path)
        )

    active_source = "\n".join(
        active_source_parts
    )

    for forbidden in (
        "document_upload_job",
        "upload_normalizer",
        "upload_intel_store_v2",
        "upload_intel_store_old",
        "upload_phrase_pool_builder_backup_before_v2",
        "legacy_upload",
    ):
        require(
            forbidden not in active_source,
            f"Legacy live-source reference remains: {forbidden}",
        )

    print("OBSOLETE_UPLOAD_FILES_ABSENT: PASS")
    print("LEGACY_UPLOAD_REFERENCES_ZERO: PASS")

    print("")
    print("============================================")
    print("U2.18_BACKEND_AND_FRONTEND_CONTRACTS: PASS")
    print("============================================")

except Exception:
    print("")
    print("============================================")
    print("U2.18_BACKEND_AND_FRONTEND_CONTRACTS: FAIL")
    print("============================================")
    traceback.print_exc()
