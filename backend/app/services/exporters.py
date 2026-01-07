from pathlib import Path
from .textops import norm
from ..config import settings
import uuid

def export_docx(filename_base: str, html_body: str) -> Path:
    """
    Placeholder exporter: writes .html as a .docx-named file so your frontend flow works.
    Replace with real docx conversion (python-docx, pandoc, vendor/docx_maker.py).
    """
    base = (filename_base or "document").rsplit(".", 1)[0]
    out = Path(settings.export_dir) / f"{base}_{uuid.uuid4().hex[:8]}.docx"
    out.write_text(html_body or "", encoding="utf-8")
    return out
