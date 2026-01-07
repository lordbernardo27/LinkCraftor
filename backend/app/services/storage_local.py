import os
from werkzeug.utils import secure_filename

class LocalStorage:
    def __init__(self, root: str):
        self.root = root
        self.uploads_dir = os.path.join(root, "uploads")
        self.exports_dir = os.path.join(root, "exports")
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.exports_dir, exist_ok=True)

    def _unique_name(self, filename: str) -> str:
        base = secure_filename(filename) or "file"
        name = base
        i = 1
        while os.path.exists(os.path.join(self.uploads_dir, name)):
            stem, ext = os.path.splitext(base)
            name = f"{stem}_{i}{ext}"
            i += 1
        return name

    def save_original(self, filename: str, data: bytes) -> str:
        """Save original uploaded bytes, returns stored filename (may be uniquified)."""
        safe_name = self._unique_name(filename)
        path = os.path.join(self.uploads_dir, safe_name)
        with open(path, "wb") as f:
            f.write(data)
        return safe_name

    def get_original_path(self, filename: str) -> str:
        safe = secure_filename(filename)
        return os.path.join(self.uploads_dir, safe)

    def iter_originals(self):
        for name in os.listdir(self.uploads_dir):
            p = os.path.join(self.uploads_dir, name)
            if os.path.isfile(p):
                yield p, name

    def export_path(self, filename: str) -> str:
        safe = secure_filename(filename) or "export.docx"
        return os.path.join(self.exports_dir, safe)
