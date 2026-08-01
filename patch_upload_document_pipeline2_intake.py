from __future__ import annotations

from pathlib import Path


root = Path(r"C:\Users\HP\Documents\LinkCraftor")
path = root / "backend/server/routes/files.py"

source = path.read_text(encoding="utf-8-sig")

start_marker = '@router.post("/upload")'
end_marker = '@router.post("/clear_session")'

start = source.find(start_marker)
end = source.find(end_marker, start)

if start < 0:
    raise RuntimeError(
        "Canonical /api/files/upload route was not found."
    )

if end < 0:
    raise RuntimeError(
        "clear_session route marker was not found after upload route."
    )

replacement = '''@router.post("/upload")
async def upload_file(
    workspace_id: str = Query("ws_betterhealthcheck_com"),
    file: UploadFile = File(...),
):
    """
    Canonical Upload Document API entry point.

    The HTTP route performs no Pipeline 2 implementation directly.
    It delegates the upload-intake workflow to the canonical
    Ingestion and Unified Content Pipeline.
    """

    from backend.server.pipelines.upload_document.ingestion_unified_content_pipeline.upload_intake import (
        UploadIntakeDependencies,
        run_upload_intake,
    )

    dependencies = UploadIntakeDependencies(
        guess_extension=_guess_ext,
        normalize_workspace_id=_ws,
        extract_preview=_extract_preview_from_bytes,
        store_and_index=_store_and_index,
        workspace_directory=_ws_dir,
        allowed_extensions=ALLOWED_EXT,
    )

    return await run_upload_intake(
        workspace_id=workspace_id,
        file=file,
        dependencies=dependencies,
    )


'''

updated = source[:start] + replacement + source[end:]

path.write_text(
    updated,
    encoding="utf-8",
)

print("UPLOAD_DOCUMENT_PIPELINE2_INTAKE_ROUTE_PATCHED")
print(f"FILE={path}")
