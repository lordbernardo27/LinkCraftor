# server.py — SIMPLE, RELIABLE SERVER (FULL FILE)
# - Serves public/app.html
# - /api/upload returns BOTH plain text (for matching) and HTML (for display)
# - Handles .txt, .md, .html/.htm, .docx (docx via mammoth if installed)
# - Health check: /health

import os
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import re

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(
    __name__,
    static_folder=str(PUBLIC_DIR),
    static_url_path=""  # so /assets/... resolves
)
CORS(app)

# ---------- ROUTES ----------

@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.get("/")
def root():
    # Serve your main page (public/app.html)
    return send_from_directory(str(PUBLIC_DIR), "app.html")

# Serve any other static file under /public (assets, css, js, images, etc.)
@app.get("/<path:filename>")
def public_files(filename):
    return send_from_directory(str(PUBLIC_DIR), filename)

# ---------- UPLOAD + EXTRACT ----------

def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )

def _strip_tags(s: str) -> str:
    # very simple HTML -> text (for matching)
    return re.sub(r"<[^>]+>", " ", s)

@app.post("/api/upload")
def api_upload():
    """
    Expects form-data: file=<uploaded file>
    Returns JSON: { filename, ext, text, html, truncated }
      - text: plain text (ALWAYS a string)
      - html: best-effort HTML for faithful display
    """
    if "file" not in request.files:
        return jsonify({"error": "no file part"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "empty filename"}), 400

    from werkzeug.utils import secure_filename
    filename = secure_filename(f.filename)
    ext = Path(filename).suffix.lower()

    allowed = {".txt", ".md", ".html", ".htm", ".docx"}
    if ext not in allowed:
        return jsonify({"error": f"file type not allowed: {ext}"}), 400

    save_path = UPLOAD_DIR / filename
    f.save(save_path)

    text = ""
    html = ""

    try:
        if ext == ".txt":
            # read as utf-8 with ignore to avoid errors
            raw = save_path.read_text(encoding="utf-8", errors="ignore")
            text = raw
            html = f"<pre>{_html_escape(raw)}</pre>"

        elif ext == ".md":
            # Try markdown2 for nice HTML; fallback to <pre> if not installed
            try:
                import markdown2
                md = save_path.read_text(encoding="utf-8", errors="ignore")
                html = markdown2.markdown(md)
                text = _strip_tags(html)
            except Exception:
                md = save_path.read_text(encoding="utf-8", errors="ignore")
                text = md
                html = f"<pre>{_html_escape(md)}</pre>"

        elif ext in {".html", ".htm"}:
            raw = save_path.read_text(encoding="utf-8", errors="ignore")
            html = raw
            text = _strip_tags(raw)

        elif ext == ".docx":
            # Prefer mammoth for .docx -> HTML
            try:
                import mammoth
                with open(save_path, "rb") as docx_file:
                    result = mammoth.convert_to_html(docx_file)
                    html = result.value or ""
                text = _strip_tags(html) if html else ""
            except Exception:
                # fallback: raw bytes to text (not perfect but avoids crash)
                raw = save_path.read_bytes().decode("utf-8", errors="ignore")
                text = raw
                html = f"<pre>{_html_escape(raw)}</pre>"

        else:
            return jsonify({"error": f"unsupported ext {ext}"}), 400

    except Exception as e:
        return jsonify({"error": f"extract failed: {e}"}), 500

    # truncate text to keep client light (200k chars)
    def _truncate(s: str, limit=200000):
        s = s or ""
        return (s[:limit], len(s) > limit)

    text, was_trunc = _truncate(text, 200000)

    # IMPORTANT: always return strings to avoid `(text || '').split` crashes
    if not isinstance(text, str):
        text = str(text or "")
    if not isinstance(html, str):
        html = ""

    return jsonify({
        "filename": filename,
        "ext": ext,
        "text": text,   # PLAIN TEXT for matching (always string)
        "html": html,   # HTML for display (best effort)
        "truncated": was_trunc
    })

# ---------- MAIN ----------

if __name__ == "__main__":
    port = int(os.environ.get("LINKCRAFTOR_PORT", "8001"))
    # debug=True to see errors in console; change to False for quieter logs
    app.run(host="127.0.0.1", port=port, debug=True)
