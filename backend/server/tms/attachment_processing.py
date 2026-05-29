
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class AttachmentProcessingResult:
    attachment_id: str
    filename: str
    sha256_hash: str
    duplicate: bool
    malware_scan_status: str
    preview_available: bool
    preview_metadata: Dict[str, Any] = field(default_factory=dict)
    image_metadata: Dict[str, Any] = field(default_factory=dict)
    document_metadata: Dict[str, Any] = field(default_factory=dict)


def calculate_attachment_hash(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Attachment file not found: {file_path}")

    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def detect_duplicate_attachment(
    sha256_hash: str,
    existing_metadata: List[Dict[str, Any]],
) -> bool:
    for item in existing_metadata:
        metadata = item.get("metadata") or {}

        if metadata.get("sha256_hash") == sha256_hash:
            return True

    return False


def run_malware_scan_hook(file_path: str) -> Dict[str, Any]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Attachment file not found: {file_path}")

    return {
        "status": "scan_pending",
        "provider": "placeholder",
        "message": "Malware scan hook reserved for ClamAV or cloud scanning provider.",
    }


def build_attachment_preview_metadata(
    filename: str,
    content_type: str | None,
    size_bytes: int,
) -> Dict[str, Any]:
    suffix = Path(filename).suffix.lower()

    preview_available = bool(
        content_type in {
            "image/png",
            "image/jpeg",
            "image/webp",
            "application/pdf",
            "text/plain",
            "text/csv",
            "application/json",
        }
    )

    return {
        "filename": filename,
        "extension": suffix,
        "content_type": content_type,
        "size_bytes": size_bytes,
        "preview_available": preview_available,
    }


def extract_image_dimension_metadata(
    file_path: str,
    content_type: str | None,
) -> Dict[str, Any]:
    if content_type not in {"image/png", "image/jpeg", "image/webp"}:
        return {}

    try:
        from PIL import Image
    except Exception:
        return {
            "image_metadata_status": "pillow_unavailable",
        }

    path = Path(file_path)

    with Image.open(path) as img:
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
        }


def extract_document_metadata(
    file_path: str,
    content_type: str | None,
) -> Dict[str, Any]:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if content_type == "application/pdf" or suffix == ".pdf":
        return {
            "document_type": "pdf",
            "metadata_status": "basic_detected",
        }

    if suffix in {".docx", ".xlsx", ".txt", ".csv", ".json"}:
        return {
            "document_type": suffix.replace(".", ""),
            "metadata_status": "basic_detected",
        }

    return {}


def process_attachment_metadata(
    attachment: Dict[str, Any],
    existing_metadata: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    existing_metadata = existing_metadata or []

    file_path = str(attachment.get("storage_path") or "")
    filename = str(attachment.get("filename") or "")
    content_type = attachment.get("content_type")
    size_bytes = int(attachment.get("size_bytes") or 0)
    attachment_id = str(attachment.get("attachment_id") or "unknown")

    sha256_hash = calculate_attachment_hash(file_path)
    duplicate = detect_duplicate_attachment(sha256_hash, existing_metadata)
    malware_scan = run_malware_scan_hook(file_path)
    preview_metadata = build_attachment_preview_metadata(filename, content_type, size_bytes)
    image_metadata = extract_image_dimension_metadata(file_path, content_type)
    document_metadata = extract_document_metadata(file_path, content_type)

    result = AttachmentProcessingResult(
        attachment_id=attachment_id,
        filename=filename,
        sha256_hash=sha256_hash,
        duplicate=duplicate,
        malware_scan_status=str(malware_scan.get("status")),
        preview_available=bool(preview_metadata.get("preview_available")),
        preview_metadata=preview_metadata,
        image_metadata=image_metadata,
        document_metadata=document_metadata,
    )

    return asdict(result)
