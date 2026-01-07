# backend/app/routers/convert.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import mammoth
import io

router = APIRouter()

@router.post("/docx")
async def convert_docx(file: UploadFile = File(...)):
    # Basic validations
    filename = (file.filename or "").strip()
    if not filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Please upload a .docx file.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="File appears empty.")

    # Convert to HTML using mammoth (in-memory)
    try:
        with io.BytesIO(raw) as docx_stream:
            result = mammoth.convert_to_html(docx_stream)
            html = (result.value or "").strip()       # The generated HTML
            messages = [m.message for m in result.messages]  # Warnings/notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")

    if not html:
        # Fallback: try plain text if HTML is empty (rare)
        try:
            with io.BytesIO(raw) as docx_stream:
                text_result = mammoth.extract_raw_text(docx_stream)
                text = (text_result.value or "").strip()
        except Exception:
            text = ""
        if not text:
            raise HTTPException(status_code=422, detail="Could not extract content from DOCX.")
        # Wrap plain text in minimal HTML so the editor can still display something
        html = f"<pre>{text}</pre>"

    # Return normalized payload your frontend can use
    return JSONResponse({
        "ok": True,
        "filename": filename,
        "html": html,
        "messages": messages,   # can show in a non-blocking “warnings” area
        "engine_version": "0.1.0"
    })
