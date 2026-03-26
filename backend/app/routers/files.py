
from fastapi import APIRouter, UploadFile, File, Response, HTTPException
from ..models.schemas import UploadResponse
from ..config import settings
from pathlib import Path
import shutil
import mimetypes
import uuid

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    # 1) Store original bytes (source of truth)
    uid = uuid.uuid4().hex[:8]
    stored_name = f"{uid}_{file.filename}"
    dst = Path(settings.upload_dir) / stored_name

    dst.parent.mkdir(parents=True, exist_ok=True)

    with dst.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # 2) Normalize ext
    ext = (Path(file.filename).suffix or "").lower().lstrip(".")

    # 3) Backend-owned URLs (frontend must only use these)
    original_url = f"/api/files/download/{stored_name}"

    # For Step 1 we keep preview_url same as original_url.
    # Step 2 will introduce a true /preview endpoint that can render safely.
    preview_url = original_url

    # 4) Preview hints (still backend-defined; frontend just renders)
    preview_mime = mimetypes.guess_type(str(dst))[0] or "application/octet-stream"

    if ext in ("html", "htm"):
        preview_kind = "html"
    elif ext in ("txt", "md"):
        preview_kind = "text"
    elif ext in ("png", "jpg", "jpeg", "webp", "gif", "svg"):
        preview_kind = "image"
    elif ext == "pdf":
        preview_kind = "pdf"
    else:
        # docx, zip, etc. will download/open externally until Step 2 adds conversions
        preview_kind = "download"

    # 5) Keep your current simple extracted text/html behavior,
    # but read from the saved file (NOT from file.read()).
    text = ""
    html = ""

    if ext in ("txt", "md", "html", "htm"):
        raw = dst.read_bytes()
        decoded = raw.decode(errors="ignore")
        if ext in ("html", "htm"):
            html = decoded
        else:
            text = decoded

    return UploadResponse(
        doc_id=stored_name,
        filename=file.filename,
        ext=ext,
        text=text,
        html=html,
        original_url=original_url,
        preview_url=preview_url,
        preview_mime=preview_mime,
        preview_kind=preview_kind,
    )
