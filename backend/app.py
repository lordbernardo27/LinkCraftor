# backend/app.py
import os
from flask import Flask, send_from_directory
from backend.routes.files import bp as files_bp

# --- absolute paths so Windows pathing is reliable ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path="")
app.register_blueprint(files_bp, url_prefix="/api")

# ---- Frontend routes (serve /public) ----
@app.route("/")
def index():
    return send_from_directory(PUBLIC_DIR, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    full = os.path.join(PUBLIC_DIR, path)
    if os.path.isfile(full):
        return send_from_directory(PUBLIC_DIR, path)
    # SPA fallback
    return send_from_directory(PUBLIC_DIR, "index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
