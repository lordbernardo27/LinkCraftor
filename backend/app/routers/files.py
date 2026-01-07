from fastapi import APIRouter, UploadFile, File, Response
from ..models.schemas import UploadResponse
from ..config import settings
from pathlib import Path
import shutil
import mimetypes
import uuid

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    # store original
    uid = uuid.uuid4().hex[:8]
    dst = Path(settings.upload_dir) / f"{uid}_{file.filename}"
    with dst.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    ext = (Path(file.filename).suffix or "").lower()
    # note: in your real pipeline you’ll extract text & html server-side
    text = (await file.read()).decode(errors="ignore") if ext in [".txt",".md",".html",".htm"] else ""
    html = text if ext in [".html",".htm"] else ""
    return UploadResponse(filename=file.filename, ext=ext, text=text if ext != ".html" else "", html=html)

@router.get("/download/{name}")
def download_original(name: str):
    p = Path(settings.upload_dir) / name
    if not p.exists():
        return Response(status_code=404)
    mt = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
    return Response(p.read_bytes(), media_type=mt, headers={"Content-Disposition": f'attachment; filename="{p.name}"'})

from ..services.exporters import export_docx

@router.post("/export/docx")
def export_docx_route(filename: str, body: str):
    path = export_docx(filename, body)
    return {"file": path.name}
