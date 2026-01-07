# server/main.py
from io import BytesIO
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mammoth  # pip install mammoth

app = FastAPI(title="LinkCraftor API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"ok": True}

# POST /api/convert/docx using python-mammoth
@app.post("/api/convert/docx")
async def convert_docx(file: UploadFile = File(...)):
    name = (file.filename or "").lower()
    if not name.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx is supported")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        html = mammoth.convert_to_html(BytesIO(data)).value or ""
        text = mammoth.extract_raw_text(BytesIO(data)).value or ""
        return {"filename": file.filename, "ext": ".docx", "html": html, "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mammoth conversion failed: {e}")
