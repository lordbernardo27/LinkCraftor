
from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


ATTACHMENT_DATA_DIR = Path("backend/server/data/tms")
ATTACHMENT_STORAGE_DIR = ATTACHMENT_DATA_DIR / "attachments"
ATTACHMENT_METADATA_PATH = ATTACHMENT_DATA_DIR / "attachments.jsonl"

MAX_ATTACHMENT_SIZE_BYTES = 25 * 1024 * 1024

ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "application/pdf",
    "text/plain",
    "text/csv",
    "application/json",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

BLOCKED_EXTENSIONS = {
    ".exe",
    ".bat",
    ".cmd",
    ".scr",
    ".js",
    ".vbs",
    ".ps1",
    ".sh",
    ".jar",
    ".msi",
    ".dll",
}


@dataclass(frozen=True)
class AttachmentMetadata:
    attachment_id: str
    filename: str
    source: str
    storage_path: str
    ticket_id: str | None = None
    message_id: str | None = None
    workspace_id: str | None = None
    content_type: str | None = None
    size_bytes: int = 0
    visibility: str = "customer_visible"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_attachment_store() -> None:
    ATTACHMENT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    if not ATTACHMENT_METADATA_PATH.exists():
        ATTACHMENT_METADATA_PATH.write_text("", encoding="utf-8")


def is_dangerous_filename(filename: str) -> bool:
    suffix = Path(filename).suffix.lower()
    return suffix in BLOCKED_EXTENSIONS


def validate_attachment_upload(
    filename: str,
    content_type: str | None,
    size_bytes: int,
) -> bool:
    if not filename.strip():
        raise ValueError("Attachment filename is required.")

    if is_dangerous_filename(filename):
        raise ValueError(f"Blocked dangerous attachment type: {filename}")

    if size_bytes <= 0:
        raise ValueError("Attachment file size must be greater than zero.")

    if size_bytes > MAX_ATTACHMENT_SIZE_BYTES:
        raise ValueError("Attachment exceeds maximum allowed size.")

    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Unsupported attachment MIME type: {content_type}")

    return True


def build_attachment_id(ticket_id: str | None, filename: str, size_bytes: int) -> str:
    safe_ticket = (ticket_id or "global").replace("/", "_").replace("\\", "_")
    safe_name = Path(filename).stem[:40].replace(" ", "_")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")

    return f"att_{safe_ticket}_{safe_name}_{size_bytes}_{timestamp}"


def save_attachment_metadata(metadata: AttachmentMetadata) -> None:
    _ensure_attachment_store()

    with ATTACHMENT_METADATA_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(metadata), ensure_ascii=False) + "\n")


def store_ticket_attachment(
    source_path: str,
    filename: str,
    content_type: str | None,
    ticket_id: str,
    workspace_id: str | None = None,
    visibility: str = "customer_visible",
) -> AttachmentMetadata:
    _ensure_attachment_store()

    source = Path(source_path)
    size_bytes = source.stat().st_size

    validate_attachment_upload(
        filename=filename,
        content_type=content_type,
        size_bytes=size_bytes,
    )

    attachment_id = build_attachment_id(ticket_id, filename, size_bytes)
    destination = ATTACHMENT_STORAGE_DIR / f"{attachment_id}_{filename}"

    shutil.copyfile(source, destination)

    metadata = AttachmentMetadata(
        attachment_id=attachment_id,
        filename=filename,
        source="ticket_upload",
        storage_path=str(destination),
        ticket_id=ticket_id,
        workspace_id=workspace_id,
        content_type=content_type,
        size_bytes=size_bytes,
        visibility=visibility,
    )

    save_attachment_metadata(metadata)
    return metadata


def store_email_attachment(
    source_path: str,
    filename: str,
    content_type: str | None,
    message_id: str,
    ticket_id: str | None = None,
    workspace_id: str | None = None,
) -> AttachmentMetadata:
    _ensure_attachment_store()

    source = Path(source_path)
    size_bytes = source.stat().st_size

    validate_attachment_upload(
        filename=filename,
        content_type=content_type,
        size_bytes=size_bytes,
    )

    attachment_id = build_attachment_id(ticket_id, filename, size_bytes)
    destination = ATTACHMENT_STORAGE_DIR / f"{attachment_id}_{filename}"

    shutil.copyfile(source, destination)

    metadata = AttachmentMetadata(
        attachment_id=attachment_id,
        filename=filename,
        source="email_attachment",
        storage_path=str(destination),
        ticket_id=ticket_id,
        message_id=message_id,
        workspace_id=workspace_id,
        content_type=content_type,
        size_bytes=size_bytes,
    )

    save_attachment_metadata(metadata)
    return metadata


def read_attachment_metadata(limit: int = 500) -> list[Dict[str, Any]]:
    _ensure_attachment_store()

    lines = ATTACHMENT_METADATA_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]
