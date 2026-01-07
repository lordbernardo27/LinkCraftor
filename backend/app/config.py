from pydantic_settings import BaseSettings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data_store"
UPLOAD_DIR = DATA_DIR / "uploads"
EXPORT_DIR = DATA_DIR / "exports"

class Settings(BaseSettings):
    debug: bool = True
    upload_dir: str = str(UPLOAD_DIR)
    export_dir: str = str(EXPORT_DIR)

settings = Settings()

# ensure dirs
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
