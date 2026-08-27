# backend/server/routes/files.py
from __future__ import annotations

import io
import os
import threading
import json
import uuid
import re
import html
import traceback
from backend.server.stores.rebuild_governance import queue_rebuild_event
from backend.server.pipelines.connect_domain.linking_target_pipeline.active_target_set import (
    active_target_set_path as canonical_active_target_set_path,
    build_active_target_set as build_canonical_active_target_set,
    load_active_target_set as load_canonical_active_target_set,
    load_optional_source_payload,
    save_active_target_set as save_canonical_active_target_set,
)
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Body
from fastapi.responses import FileResponse

import mammoth

# Strict DOCX style-based H1 extraction (no fallbacks)
try:
    from docx import Document as DocxDocument  # python-docx
except Exception:
    DocxDocument = None


router = APIRouter(prefix="/api/files", tags=["files"])
legacy_router = APIRouter(prefix="/api", tags=["legacy"])

ALLOWED_EXT = {".docx", ".txt", ".md", ".markdown", ".html", ".htm"}

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/server
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"

TEXT_LIMIT = 200_000

# Workspace-level files that must never be deleted by clear_session's
# uploaded-file sweep. Uploaded documents are stored as "{doc_id}__{name}".
_WS_PROTECTED_FILES = {"index.json", "work_index.json"}


def _utc_now_iso() -> str:
    """Timezone-aware UTC timestamp, formatted with a trailing 'Z'.

    Replaces deprecated datetime.utcnow() (removed-path in Python 3.12+).
    """
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _utc_from_timestamp_iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")


# -------------------------
# STRICT H1 extraction helpers (NO FALLBACKS)
# -------------------------
_H1_TAG_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
_TAG_STRIP_RE = re.compile(r"<[^>]+>")
_WS_SAFE_RE = re.compile(r"[^a-z0-9_]+", re.IGNORECASE)


def _strip_tags_basic(s: str) -> str:
    s = _TAG_STRIP_RE.sub(" ", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _quality_gate_h1(h: str) -> Tuple[bool, str]:
    t = (h or "").strip()
    if len(t) < 4:
        return False, "too_short"
    if len(t) > 140:
        return False, "too_long"

    letters_digits = sum(ch.isalnum() for ch in t)
    if letters_digits < max(3, int(len(t) * 0.35)):
        return False, "too_symbolic"

    low = t.lower()
    generic = {
        "introduction",
        "overview",
        "table of contents",
        "contents",
        "home",
        "welcome",
        "summary",
        "conclusion",
    }
    if low in generic:
        return False, "generic_heading"

    return True, ""


def _strict_h1_from_docx_file(stored_path: str) -> Tuple[str, str, str]:
    """
    Read DOCX title/H1 information without ever modifying the source file.

    Priority:
    1. Genuine Title / Heading 1 paragraph.
    2. First suitable non-empty paragraph before the first lower-level
       heading (Heading 2-6), using the existing H1 quality gate.

    This function is intentionally read-only.
    """
    if not stored_path:
        return "", "", "docx_missing_path"

    if DocxDocument is None:
        return "", "", "docx_reader_unavailable"

    try:
        doc = DocxDocument(stored_path)
    except Exception as e:
        return "", "", f"docx_read_failed:{str(e)[:120]}"

    paras = getattr(doc, "paragraphs", []) or []

    # First preference: a genuine structural Title / Heading 1.
    for p in paras:
        txt = (getattr(p, "text", "") or "").strip()

        if not txt:
            continue

        try:
            style_name = (p.style.name or "").strip()
        except Exception:
            style_name = ""

        if style_name in ("Heading 1", "Title"):
            ok, reason = _quality_gate_h1(txt)

            if not ok:
                return "", "", f"failed_quality_gate:{reason}"

            return txt, f"docx:{style_name}", ""

    # Fallback: infer a title from the first suitable paragraph
    # before the first lower-level heading. This preserves the
    # useful behavior of the former in-place normalizer without
    # changing or saving the uploaded DOCX.
    first_lower_heading_idx = None

    for i, p in enumerate(paras):
        try:
            style_name = (p.style.name or "").strip()
        except Exception:
            style_name = ""

        if style_name in (
            "Heading 2",
            "Heading 3",
            "Heading 4",
            "Heading 5",
            "Heading 6",
        ):
            first_lower_heading_idx = i
            break

    search_upto = (
        first_lower_heading_idx
        if first_lower_heading_idx is not None
        else len(paras)
    )

    for i in range(search_upto):
        p = paras[i]
        txt = (getattr(p, "text", "") or "").strip()

        if not txt:
            continue

        ok, reason = _quality_gate_h1(txt)

        if not ok:
            return "", "", f"failed_quality_gate:{reason}"

        return txt, "docx:inferred_first_paragraph", ""

    return "", "", "no_strict_h1_found"


def _strict_h1_from_html(preview_html: str) -> Tuple[str, str, str]:
    html_in = preview_html or ""
    m = _H1_TAG_RE.search(html_in)
    if not m:
        return "", "", "no_strict_h1_found"

    cand = _strip_tags_basic(m.group(1) or "")
    ok, reason = _quality_gate_h1(cand)
    if not ok:
        return "", "", f"failed_quality_gate:{reason}"
    return cand, "html:h1", ""


def _strict_h1_from_md(preview_text: str) -> Tuple[str, str, str]:
    txt = preview_text or ""
    for line in txt.splitlines():
        line = (line or "").strip()
        if line.startswith("# "):
            cand = line[2:].strip()
            ok, reason = _quality_gate_h1(cand)
            if not ok:
                return "", "", f"failed_quality_gate:{reason}"
            return cand, "md:#", ""
    return "", "", "no_strict_h1_found"


def _derive_h1_for_index(
    *,
    ext: str,
    preview_html: str,
    preview_text: str,
    stored_path: str | None = None,
) -> Tuple[str, str, str]:
    e = (ext or "").lower().strip()

    if e == ".docx":
        return _strict_h1_from_docx_file(stored_path or "")

    if e in (".html", ".htm"):
        return _strict_h1_from_html(preview_html or "")

    if e in (".md", ".markdown"):
        # FIX: when markdown2 is installed, preview_text is tag-stripped HTML
        # (no "# " lines survive), so the raw-markdown scan never matched and
        # md H1s were silently lost. Try the raw-md scan first (covers the
        # markdown2-missing fallback path), then the rendered <h1>.
        h1, src, err = _strict_h1_from_md(preview_text or "")
        if h1:
            return h1, src, err
        h1, src, err = _strict_h1_from_html(preview_html or "")
        if h1:
            return h1, "md:rendered_h1", err
        return "", "", "no_strict_h1_found"

    if e == ".txt":
        return "", "", "txt_no_structural_h1"

    return "", "", "no_strict_h1_found"


# -------------------------
# Workspace helpers (WS-only)
# -------------------------
def _ws(workspace_id: str) -> str:
    raw = str(workspace_id or "").strip().lower()

    if not raw:
        raise ValueError("workspace_id is required.")

    # Collapse accidental duplicate canonical prefix first.
    while raw.startswith("ws_ws_"):
        raw = raw[3:]

    # Remove one canonical prefix before sanitizing the identifier body.
    if raw.startswith("ws_"):
        raw = raw[3:]

    s = raw.replace(".", "_").replace("-", "_").replace(" ", "_")
    s = _WS_SAFE_RE.sub("_", s)
    s = re.sub(r"_+", "_", s).strip("_")

    if not s:
        raise ValueError("workspace_id is invalid.")

    return f"ws_{s}"[:80]


def _ws_dir(workspace_id: str) -> Path:
    return DOCS_DIR / _ws(workspace_id)


def _index_path(workspace_id: str) -> Path:
    return _ws_dir(workspace_id) / "index.json"


_INDEX_LOCKS_GUARD = threading.Lock()
_INDEX_LOCKS: Dict[str, threading.RLock] = {}


def _index_lock(path: Path) -> threading.RLock:
    key = str(path.resolve())

    with _INDEX_LOCKS_GUARD:
        lock = _INDEX_LOCKS.get(key)

        if lock is None:
            lock = threading.RLock()
            _INDEX_LOCKS[key] = lock

        return lock


def _safe_read_index(path: Path) -> List[Dict[str, Any]]:
    """
    Tolerant reader for read-only compatibility surfaces.

    Mutation paths MUST use _strict_read_index_for_update() so a malformed
    existing registry can never be silently interpreted as an empty registry.
    """
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [x for x in data if isinstance(x, dict)] if isinstance(data, list) else []
    except Exception:
        return []


def _strict_read_index_for_update(path: Path) -> List[Dict[str, Any]]:
    """
    Fail-closed registry reader for every read-modify-write transaction.

    A missing registry is a valid empty workspace. An existing registry must
    be valid JSON, must be a list, and every record must be an object.
    """
    if not path.exists():
        return []

    try:
        data = json.loads(
            path.read_text(encoding="utf-8")
        )
    except Exception as exc:
        raise RuntimeError(
            "Upload registry is unreadable and cannot be modified safely."
        ) from exc

    if not isinstance(data, list):
        raise RuntimeError(
            "Upload registry has an invalid root structure and "
            "cannot be modified safely."
        )

    if any(not isinstance(item, dict) for item in data):
        raise RuntimeError(
            "Upload registry contains malformed records and "
            "cannot be modified safely."
        )

    return data


def _safe_write_index(path: Path, items: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_name(
        f"{path.name}.{uuid.uuid4().hex}.tmp"
    )

    try:
        tmp.write_text(
            json.dumps(
                items,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        os.replace(tmp, path)

    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            pass


_WINDOWS_RESERVED_FILENAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


def _safe_upload_filename(filename: str) -> str:
    raw = str(filename or "").strip()

    if not raw:
        raise ValueError("Uploaded file must have a filename.")

    # Browsers/clients may supply either POSIX or Windows-style paths.
    basename = raw.replace("\\", "/").rsplit("/", 1)[-1].strip()

    if not basename or basename in {".", ".."}:
        raise ValueError("Uploaded filename is invalid.")

    # Remove control characters and characters forbidden by Windows.
    basename = re.sub(r"[\x00-\x1f<>:\"/\\|?*]", "_", basename)

    # Windows does not permit trailing spaces or periods.
    basename = basename.rstrip(" .")

    basename = re.sub(r"_+", "_", basename)

    if not basename:
        raise ValueError("Uploaded filename is invalid.")

    stem = Path(basename).stem.casefold()

    if stem in _WINDOWS_RESERVED_FILENAMES:
        basename = f"_{basename}"

    # Keep room for the document-id prefix in the stored filename.
    if len(basename) > 180:
        suffix = Path(basename).suffix
        stem_text = Path(basename).stem

        suffix_limit = min(len(suffix), 20)
        suffix = suffix[:suffix_limit]

        remaining = max(1, 180 - len(suffix))
        basename = stem_text[:remaining] + suffix

    return basename


def _guess_ext(filename: str) -> str:
    safe_name = _safe_upload_filename(filename)
    return (Path(safe_name).suffix or "").lower()


def _strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


# -------------------------
# Work Folder index (backend ledger)
# -------------------------
def _work_index_path(workspace_id: str) -> Path:
    return _ws_dir(workspace_id) / "work_index.json"


def _safe_read_work_index(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [x for x in data if isinstance(x, dict)] if isinstance(data, list) else []
    except Exception:
        return []


def _safe_write_work_index(path: Path, items: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _work_append(workspace_id: str, entry: Dict[str, Any]) -> None:
    p = _work_index_path(workspace_id)
    items = _safe_read_work_index(p)
    items.append(entry)
    _safe_write_work_index(p, items)


# -------------------------
# Save snapshots
# -------------------------
def _snapshot_dir(workspace_id: str) -> Path:
    p = _ws_dir(workspace_id) / "snapshots"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _safe_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content or "", encoding="utf-8")
    os.replace(tmp, path)


# -------------------------
# Preview helpers
# -------------------------
def _html_escape(s: str) -> str:
    return html.escape(s or "", quote=False)


def _decode_text_bytes(raw: bytes) -> str:
    try:
        s = raw.decode("utf-8")
    except Exception:
        try:
            s = raw.decode("utf-8", errors="ignore")
        except Exception:
            s = raw.decode(errors="ignore")
    return (s or "").lstrip("\ufeff")


def _extract_preview_from_bytes(filename: str, ext: str, raw: bytes) -> Dict[str, Any]:
    ext = (ext or "").lower().strip()

    text: str = ""
    html_out: str = ""
    is_html: bool = False
    truncated: bool = False

    if ext == ".txt":
        text = _decode_text_bytes(raw)
        html_out = "<pre>" + _html_escape(text) + "</pre>"
        is_html = False

    elif ext in (".md", ".markdown"):
        md = _decode_text_bytes(raw)
        try:
            import markdown2
            html_out = markdown2.markdown(md)
            text = _strip_tags(html_out)
            is_html = True
        except Exception:
            text = md
            html_out = "<pre>" + _html_escape(md) + "</pre>"
            is_html = False

    elif ext in (".html", ".htm"):
        html_raw = _decode_text_bytes(raw)
        html_out = html_raw
        text = _strip_tags(html_raw)
        is_html = True

    elif ext == ".docx":
        html_out = ""
        text = ""
        is_html = False

        try:
            with io.BytesIO(raw) as buff:
                result = mammoth.convert_to_html(buff)
                html_out = result.value or ""
            text = _strip_tags(html_out)
            is_html = True
        except Exception:
            try:
                text = raw.decode("utf-8", errors="ignore").strip()
            except Exception:
                text = ""
            html_out = "<pre>" + _html_escape(text) + "</pre>" if text else ""
            is_html = False

    else:
        try:
            text = _decode_text_bytes(raw)
            html_out = "<pre>" + _html_escape(text) + "</pre>"
            is_html = False
        except Exception:
            text = ""
            html_out = ""
            is_html = False

    if len(text) > TEXT_LIMIT:
        text = text[:TEXT_LIMIT]
        truncated = True

    return {
        "filename": Path(filename).name,
        "ext": ext,
        "text": text,
        "html": html_out,
        "is_html": bool(is_html),
        "truncated": bool(truncated),
    }


def _store_and_index(
    workspace_id: str,
    file: UploadFile,
    raw: bytes,
    *,
    preview_html: str,
    preview_text: str,
) -> Dict[str, Any]:
    safe_name = _safe_upload_filename(file.filename)
    ext = _guess_ext(safe_name)
    ws_dir = _ws_dir(workspace_id)
    ws_dir.mkdir(parents=True, exist_ok=True)

    doc_id = uuid.uuid4().hex
    stored_name = f"{doc_id}__{safe_name}"
    stored_path = ws_dir / stored_name
    idx_path = _index_path(workspace_id)

    with _index_lock(idx_path):
        # Validate the existing registry BEFORE creating a new source file.
        # A corrupt registry must fail closed rather than becoming [].
        items = _strict_read_index_for_update(idx_path)

        if any(
            str(item.get("doc_id") or "") == doc_id
            for item in items
        ):
            raise RuntimeError(
                f"Duplicate upload registry document_id: {doc_id}"
            )

        source_created = False

        try:
            stored_path.write_bytes(raw)
            source_created = True

            h1, h1_source, h1_error = _derive_h1_for_index(
                ext=ext,
                preview_html=preview_html or "",
                preview_text=preview_text or "",
                stored_path=str(stored_path),
            )

            # Record the byte size of the persisted immutable source file
            # plus the original upload size.
            try:
                stored_bytes = int(stored_path.stat().st_size)
            except Exception:
                stored_bytes = len(raw)

            meta = {
                "doc_id": doc_id,
                "filename": safe_name,
                "ext": ext,
                "bytes": stored_bytes,
                "original_bytes": len(raw),
                "content_type": file.content_type or "",
                "uploaded_at": _utc_now_iso(),
                "stored_name": stored_name,
                "h1": h1,
                "h1_source": h1_source,
                "h1_error": h1_error,
            }

            items.append(meta)
            _safe_write_index(idx_path, items)

        except Exception:
            # The registry commit did not complete. Remove only the source
            # created by this transaction so no orphan upload is left behind.
            if source_created:
                try:
                    stored_path.unlink(missing_ok=True)
                except Exception as rollback_exc:
                    raise RuntimeError(
                        "Upload registry commit failed and the newly "
                        "created source file could not be rolled back."
                    ) from rollback_exc
            raise

    return meta


def _update_index_h1(
    workspace_id: str,
    doc_id: str,
    *,
    ext: str,
    html_in: str,
    text_in: str,
) -> Dict[str, Any] | None:
    idxp = _index_path(workspace_id)
    ws_dir = _ws_dir(workspace_id)

    with _index_lock(idxp):
        items = _strict_read_index_for_update(idxp)

        for rec in items:
            if str(rec.get("doc_id") or "") == doc_id:
                stored_name = str(rec.get("stored_name") or "")
                stored_path = (
                    str(ws_dir / stored_name)
                    if stored_name
                    else None
                )

                h1, h1_source, h1_error = _derive_h1_for_index(
                    ext=ext,
                    preview_html=html_in or "",
                    preview_text=text_in or "",
                    stored_path=stored_path,
                )

                rec["h1"] = h1
                rec["h1_source"] = h1_source
                rec["h1_error"] = h1_error
                rec["h1_updated_at"] = _utc_now_iso()

                _safe_write_index(idxp, items)
                return rec

    return None

def _rollback_committed_upload(
    workspace_id: str,
    doc_id: str,
    *,
    expected_stored_name: str,
) -> None:
    """
    Compensate a committed upload-intake transaction that failed before
    run_upload_intake() could complete successfully.

    This rollback is deliberately document-scoped. It may remove only the
    registry record and persisted source belonging to the supplied doc_id
    and expected stored filename.

    Downstream UDUC/highlight/Active-Target-Set failures must not call this
    helper; once upload intake succeeds, the canonical uploaded source is
    retained for recovery/retry.
    """
    canonical_doc_id = str(doc_id or "").strip()
    canonical_stored_name = str(expected_stored_name or "").strip()

    if not canonical_doc_id:
        raise RuntimeError(
            "Committed upload rollback requires a document_id."
        )

    if not canonical_stored_name:
        raise RuntimeError(
            "Committed upload rollback requires a stored filename."
        )

    if (
        Path(canonical_stored_name).name != canonical_stored_name
        or canonical_stored_name in {".", ".."}
    ):
        raise RuntimeError(
            "Committed upload rollback received an invalid stored filename."
        )

    idx_path = _index_path(workspace_id)
    ws_dir = _ws_dir(workspace_id)
    stored_path = ws_dir / canonical_stored_name

    with _index_lock(idx_path):
        items = _strict_read_index_for_update(idx_path)

        matches = [
            rec
            for rec in items
            if str(rec.get("doc_id") or "").strip() == canonical_doc_id
        ]

        if len(matches) > 1:
            raise RuntimeError(
                "Committed upload rollback found duplicate registry records "
                f"for document_id: {canonical_doc_id}"
            )

        # Idempotent retry boundary: if the registry record has already been
        # removed, delete only the exact expected source if it still exists.
        if not matches:
            stored_path.unlink(missing_ok=True)
            return

        record = matches[0]
        registry_stored_name = str(
            record.get("stored_name") or ""
        ).strip()

        if registry_stored_name != canonical_stored_name:
            raise RuntimeError(
                "Committed upload rollback stored filename does not match "
                "the canonical registry record."
            )

        remaining = [
            rec
            for rec in items
            if str(rec.get("doc_id") or "").strip() != canonical_doc_id
        ]

        # Remove the registry record atomically first. If source deletion then
        # fails, restore the original registry so we do not leave a registered
        # document pointing at an intentionally deleted/missing source.
        _safe_write_index(idx_path, remaining)

        try:
            stored_path.unlink(missing_ok=True)
        except Exception as rollback_exc:
            try:
                _safe_write_index(idx_path, items)
            except Exception as restore_exc:
                raise RuntimeError(
                    "Committed upload rollback could not delete the source "
                    "and could not restore the original registry."
                ) from restore_exc

            raise RuntimeError(
                "Committed upload rollback could not delete the source; "
                "the original registry record was restored."
            ) from rollback_exc


# NOTE: The former _docs_index_path/_append_to_docs_index helpers were removed.
# They pointed at the exact same index.json as _index_path/_store_and_index and
# would have produced duplicate entries if ever called.


# -------------------------
# Active target set helpers (merge-safe)
# -------------------------
def _active_target_set_path(workspace_id: str) -> Path:
    """Compatibility wrapper around the canonical repository path."""
    return canonical_active_target_set_path(
        _ws(workspace_id)
    )


def _default_active_target_set(workspace_id: str) -> Dict[str, Any]:
    """Return an unsaved canonical empty Active Target Set payload."""
    ws_norm = _ws(workspace_id)

    result = build_canonical_active_target_set(
        workspace_id=ws_norm,
    )

    return result.to_dict(
        generated_at=_utc_now_iso()
    )


def _load_active_target_set(workspace_id: str) -> Dict[str, Any]:
    """Load the complete canonical Active Target Set."""
    ws_norm = _ws(workspace_id)
    fp = canonical_active_target_set_path(
        ws_norm
    )

    if not fp.exists():
        return _default_active_target_set(
            ws_norm
        )

    return load_canonical_active_target_set(
        ws_norm
    )


def _write_active_target_set(
    workspace_id: str,
    obj: Dict[str, Any],
) -> Dict[str, Any]:
    """Block obsolete membership-only persistence."""
    raise RuntimeError(
        "Direct Active Target Set writes are forbidden. "
        "Build from source target pools and persist through "
        "save_canonical_active_target_set()."
    )


def _merge_active_target_set(
    workspace_id: str,
    *,
    add_document_ids: List[str] | None = None,
    add_draft_ids: List[str] | None = None,
    add_imported_urls: List[str] | None = None,
    add_live_domain_urls: List[str] | None = None,
    add_upload_ids: List[str] | None = None,
) -> Dict[str, Any]:
    """Block obsolete membership-array mutation."""
    raise RuntimeError(
        "Membership-array Active Target Set merging is forbidden. "
        "Rebuild the canonical set from source target pools."
    )


# -------------------------
# API
# -------------------------

@router.post("/upload")
async def upload_file(
    workspace_id: str = Query(..., min_length=1),
    file: UploadFile = File(...),
):
    """
    Canonical Upload Document API entry point.

    The HTTP route performs no Pipeline 2 implementation directly.
    It delegates the upload-intake workflow to the canonical
    Ingestion and Unified Content Pipeline.
    """

    from backend.server.pipelines.upload_document import (
        run_upload_document,
    )
    from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline import (
        UploadIntakeDependencies,
    )

    dependencies = UploadIntakeDependencies(
        guess_extension=_guess_ext,
        normalize_workspace_id=_ws,
        extract_preview=_extract_preview_from_bytes,
        store_and_index=_store_and_index,
        rollback_committed_upload=_rollback_committed_upload,
        workspace_directory=_ws_dir,
        allowed_extensions=ALLOWED_EXT,
    )

    try:
        internal_result = await run_upload_document(
            workspace_id=workspace_id,
            file=file,
            dependencies=dependencies,
        )

        if not isinstance(internal_result, dict):
            raise RuntimeError(
                "Upload Document coordinator returned an invalid response."
            )

    except HTTPException:
        # Preserve intentional client-facing FastAPI errors unchanged.
        raise

    except Exception:
        # Keep detailed diagnostics server-side only.
        print("[UPLOAD_DOCUMENT_INTERNAL_ERROR]")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Upload processing failed.",
        ) from None

    # ------------------------------------------------------------
    # Canonical PUBLIC upload response boundary.
    #
    # The coordinator may retain rich internal pipeline diagnostics,
    # extraction records, filesystem source paths, UDUC details, etc.
    # None of those internal structures are returned directly to the
    # browser.
    # ------------------------------------------------------------

    raw_doc = internal_result.get("doc")

    if not isinstance(raw_doc, dict):
        raw_doc = {}

    public_doc_fields = (
        "doc_id",
        "filename",
        "ext",
        "bytes",
        "original_bytes",
        "content_type",
        "uploaded_at",
        "stored_name",
        "h1",
        "h1_source",
        "h1_error",
    )

    public_doc = {
        key: raw_doc.get(key)
        for key in public_doc_fields
        if key in raw_doc
    }

    document_id = str(
        internal_result.get("document_id")
        or public_doc.get("doc_id")
        or ""
    ).strip()

    public_response = {
        "ok": internal_result.get("ok") is True,
        "workspace_id": str(
            internal_result.get("workspace_id")
            or _ws(workspace_id)
        ),
        "doc": public_doc,
        "filename": str(
            internal_result.get("filename")
            or public_doc.get("filename")
            or ""
        ),
        "ext": str(
            internal_result.get("ext")
            or public_doc.get("ext")
            or ""
        ),
        "text": internal_result.get("text") or "",
        "html": internal_result.get("html") or "",
        "is_html": bool(
            internal_result.get("is_html", False)
        ),
        "truncated": bool(
            internal_result.get("truncated", False)
        ),
        "pipeline": "upload_document",
        "document_id": document_id,
        "status": str(
            internal_result.get("status") or ""
        ),
        "execution_started": bool(
            internal_result.get(
                "execution_started",
                True,
            )
        ),
        "execution_completed": bool(
            internal_result.get(
                "execution_completed",
                True,
            )
        ),
        "job_id": None,
        "processing_status": "not_applicable",
    }

    # Coordinator-level failure details may contain internal implementation
    # information. Expose only a stable, generic public failure message.
    if public_response["ok"] is not True:
        public_response["detail"] = (
            "Upload processing did not complete successfully."
        )

    return public_response


@router.post("/clear_session")
def clear_file_session(workspace_id: str = Query("ws_betterhealthcheck_com")):
    ws_norm = _ws(workspace_id)

    removed_files: List[str] = []

    paths_to_remove = [
        BASE_DIR / "data" / f"upload_struct_{ws_norm}.json",
        BASE_DIR / "data" / f"upload_phrase_index_{ws_norm}.json",
        BASE_DIR / "data" / "phrase_pools" / "upload" / f"upload_phrase_pool_{ws_norm}.json",
        BASE_DIR / "data" / "phrase_pools" / "active" / f"active_phrase_pool_{ws_norm}.json",
    ]

    for fp in paths_to_remove:
        try:
            if fp.exists():
                fp.unlink()
                removed_files.append(str(fp))
        except Exception as e:
            print("[CLEAR_FILE_SESSION_REMOVE_ERROR]", str(fp), repr(e))

    # Serialize document-file clearing and the authoritative index reset
    # against uploads, H1 mutations, and reindex operations.
    clear_idx_path = _index_path(ws_norm)

    with _index_lock(clear_idx_path):
        # Clear uploaded workspace document files for this session.
        # This prevents re-upload from being blocked as duplicate after Clear Session.
        # FIX: only remove stored upload files ("{doc_id}__{name}"); previously this
        # deleted EVERY file in the directory, wiping index.json and work_index.json.
        try:
            ws_dir = _ws_dir(ws_norm)
            if ws_dir.exists() and ws_dir.is_dir():
                for fp in ws_dir.iterdir():
                    try:
                        if not fp.is_file():
                            continue
                        if fp.name in _WS_PROTECTED_FILES:
                            continue
                        if fp.suffix == ".tmp" or "__" in fp.name:
                            fp.unlink()
                            removed_files.append(str(fp))
                    except Exception as e:
                        print(
                            "[CLEAR_FILE_SESSION_WORKSPACE_FILE_ERROR]",
                            str(fp),
                            repr(e),
                        )
        except Exception as e:
            print(
                "[CLEAR_FILE_SESSION_WORKSPACE_DIR_ERROR]",
                repr(e),
            )

        # Clear Session is an explicit authoritative reset. It intentionally
        # replaces the registry instead of requiring a valid prior index.
        try:
            _safe_write_index(clear_idx_path, [])
        except Exception as e:
            print(
                "[CLEAR_FILE_SESSION_INDEX_RESET_ERROR]",
                repr(e),
            )

    try:
        live_payload = load_optional_source_payload(
            BASE_DIR
            / "data"
            / "target_pools"
            / "live_domain"
            / f"live_domain_target_pool_{ws_norm}.json"
        )

        imported_payload = load_optional_source_payload(
            BASE_DIR
            / "data"
            / "target_pools"
            / "imported"
            / f"imported_target_pool_{ws_norm}.json"
        )

        draft_payload = load_optional_source_payload(
            BASE_DIR
            / "data"
            / "target_pools"
            / "draft"
            / f"draft_target_pool_{ws_norm}.json"
        )

        active_result = build_canonical_active_target_set(
            workspace_id=ws_norm,
            live_domain_payload=live_payload,
            document_payload={},
            imported_payload=imported_payload,
            draft_payload=draft_payload,
        )

        save_canonical_active_target_set(
            active_result
        )
    except Exception as e:
        print(
            "[CLEAR_FILE_SESSION_ACTIVE_SET_ERROR]",
            repr(e),
        )

    try:
        queue_rebuild_event(
            workspace_id=ws_norm,
            trigger="document_changed",
            metadata={
                "source": "clear_session",
                "reason": "session_cleared",
            },
        )
    except Exception as e:
        print("[CLEAR_SESSION_REBUILD_QUEUE_ERROR]", repr(e))

    return {
        "ok": True,
        "workspace_id": ws_norm,
        "cleared": {
            "upload_struct": True,
            "upload_phrase_index": True,
            "upload_phrase_pool": True,
            "active_phrase_pool": True,
            "document_index": True,
            "active_document_ids": True,
            "canonical_active_target_set_rebuilt": True,
        },
        "removed_files": removed_files,
        "preserved": [
            "work_index",
            "snapshots",
            "draft_intelligence",
            "imported_urls",
            "live_domain_intelligence",
        ],
    }


@router.get("/list")
def list_files(workspace_id: str = Query("ws_betterhealthcheck_com")):
    ws_norm = _ws(workspace_id)
    items = _safe_read_index(_index_path(ws_norm))
    items.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)

    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        out.append(
            {
                "doc_id": it.get("doc_id"),
                "filename": it.get("filename"),
                "stored_name": it.get("stored_name"),
                "uploaded_at": it.get("uploaded_at"),
                "h1": it.get("h1") or "",
                "h1_source": it.get("h1_source") or "",
                "h1_error": it.get("h1_error") or "",
            }
        )

    return {"ok": True, "workspace_id": ws_norm, "items": out}


@router.get("/h1s")
def list_h1s(workspace_id: str = Query("ws_betterhealthcheck_com")):
    ws_norm = _ws(workspace_id)
    items = _safe_read_index(_index_path(ws_norm))

    h1s: List[str] = []
    seen: set[str] = set()

    for it in items:
        if not isinstance(it, dict):
            continue
        h = str(it.get("h1") or "").strip()
        if not h:
            continue
        if h in seen:
            continue
        seen.add(h)
        h1s.append(h)

    return {"ok": True, "workspace_id": ws_norm, "h1s": h1s}


# FIX: this route previously lived on `router` (prefix /api/files) with a full
# path of "/api/site/target_pools/active_target_set", producing the URL
# /api/files/api/site/target_pools/active_target_set. It now lives on
# legacy_router (prefix /api) so the effective URL is
# /api/site/target_pools/active_target_set as intended.
@legacy_router.get("/site/target_pools/active_target_set")
def get_active_target_set(
    workspace_id: str | None = Query(None),
    workspaceId: str | None = Query(None),
):
    try:
        ws = _ws(workspace_id or workspaceId or "default")
        data = _load_active_target_set(ws)

        return {
            "ok": True,
            "workspace_id": ws,
            "workspaceId": ws,
            "exists": canonical_active_target_set_path(ws).exists(),
            "active_target_set": data,
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
        }


@router.post("/active_target_set/save")
async def save_active_target_set_api(
    payload: Dict[str, Any] = Body(...),
):
    workspace_id = _ws(
        str(
            payload.get("workspace_id")
            or "ws_betterhealthcheck_com"
        )
    )

    raise HTTPException(
        status_code=409,
        detail={
            "error": (
                "membership_only_active_target_set_write_forbidden"
            ),
            "workspace_id": workspace_id,
            "message": (
                "The canonical Active Target Set cannot be "
                "saved from membership arrays. Rebuild it "
                "from the source target pools."
            ),
        },
    )


@router.post("/reindex_h1s")
def reindex_h1s(workspace_id: str = Query("ws_betterhealthcheck_com")):
    ws_norm = _ws(workspace_id)
    ws_dir = _ws_dir(ws_norm)
    ws_dir.mkdir(parents=True, exist_ok=True)

    entries: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    idx_path = _index_path(ws_norm)

    # Reindex is an explicit authoritative reconstruction from persisted
    # source files. Hold the same lock for the complete scan + write so an
    # upload cannot appear between the scan and index replacement.
    with _index_lock(idx_path):
        for p in ws_dir.iterdir():
            if not p.is_file():
                continue
            name = p.name
            if name in _WS_PROTECTED_FILES:
                continue
            if name.endswith(".tmp"):
                continue
            if "__" not in name:
                continue

            doc_id, safe_name = name.split("__", 1)
            doc_id = (doc_id or "").strip()
            safe_name = (safe_name or "").strip()
            if not doc_id or len(doc_id) < 16:
                continue

            ext = _guess_ext(safe_name)
            if ext not in ALLOWED_EXT:
                continue

            try:
                raw = p.read_bytes()
            except Exception as e:
                errors.append(
                    {
                        "file": name,
                        "error": "read_failed",
                        "detail": str(e)[:120],
                    }
                )
                continue

            preview = _extract_preview_from_bytes(
                safe_name,
                ext,
                raw,
            )

            h1, h1_source, h1_error = _derive_h1_for_index(
                ext=ext,
                preview_html=str(preview.get("html") or ""),
                preview_text=str(preview.get("text") or ""),
                stored_path=str(p),
            )

            try:
                uploaded_at = _utc_from_timestamp_iso(
                    p.stat().st_mtime
                )
                size_bytes = int(p.stat().st_size)
            except Exception:
                uploaded_at = _utc_now_iso()
                size_bytes = len(raw)

            entries.append(
                {
                    "doc_id": doc_id,
                    "filename": safe_name,
                    "ext": ext,
                    "bytes": size_bytes,
                    "content_type": "",
                    "uploaded_at": uploaded_at,
                    "stored_name": name,
                    "h1": h1,
                    "h1_source": h1_source,
                    "h1_error": h1_error,
                }
            )

        entries.sort(
            key=lambda x: x.get("uploaded_at", ""),
            reverse=True,
        )

        _safe_write_index(
            idx_path,
            entries,
        )

    return {
        "ok": True,
        "workspace_id": ws_norm,
        "reindexed": len(entries),
        "with_h1": sum(1 for e in entries if (e.get("h1") or "").strip()),
        "missing_h1": sum(1 for e in entries if not (e.get("h1") or "").strip()),
        "errors": errors,
        "index_path": str(idx_path),
    }


@router.get("/docx_style_debug")
def docx_style_debug(
    workspace_id: str = Query("ws_betterhealthcheck_com"),
    doc_id: str = Query(...),
    limit: int = Query(40, ge=1, le=200),
):
    ws_norm = _ws(workspace_id)

    items = _safe_read_index(_index_path(ws_norm))
    hit = next((x for x in items if x.get("doc_id") == doc_id), None)
    if not hit:
        raise HTTPException(status_code=404, detail="doc_id not found")

    ext = str(hit.get("ext") or "").lower()
    if ext != ".docx":
        raise HTTPException(status_code=400, detail="docx_only")

    stored_name = str(hit.get("stored_name") or "")
    p = _ws_dir(ws_norm) / stored_name
    if not p.exists():
        raise HTTPException(status_code=404, detail="stored_file_missing")

    if DocxDocument is None:
        raise HTTPException(status_code=500, detail="python_docx_not_available")

    try:
        doc = DocxDocument(str(p))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"docx_read_failed:{str(e)[:160]}")

    out = []
    paras = getattr(doc, "paragraphs", []) or []
    for i, para in enumerate(paras[:limit]):
        txt = (getattr(para, "text", "") or "").strip()
        if not txt:
            continue
        try:
            style_name = (para.style.name or "").strip()
        except Exception:
            style_name = ""
        out.append({"i": i, "style": style_name, "text": txt[:200]})

    return {
        "ok": True,
        "workspace_id": ws_norm,
        "doc_id": doc_id,
        "filename": hit.get("filename"),
        "items": out,
    }


@router.post("/save")
async def save_doc(
    workspace_id: str = Query("ws_betterhealthcheck_com"),
    doc_id: str = Query(...),
    payload: Dict[str, Any] = Body(default_factory=dict),
):
    ws_norm = _ws(workspace_id)

    doc_id = (doc_id or "").strip()
    if not doc_id:
        raise HTTPException(status_code=400, detail="doc_id is required")

    items = _safe_read_index(_index_path(ws_norm))
    hit = next((x for x in items if x.get("doc_id") == doc_id), None)
    if not hit:
        raise HTTPException(status_code=404, detail="doc_id not found")

    html_in = str((payload or {}).get("html") or "").strip()
    text_in = str((payload or {}).get("text") or "")

    if not html_in:
        raise HTTPException(status_code=400, detail="html is required")

    ts_compact = _utc_now_iso().replace(":", "").replace("-", "")
    snap_name = f"{doc_id}__{ts_compact}.html"
    snap_path = _snapshot_dir(ws_norm) / snap_name
    _safe_write_text(snap_path, html_in)

    ext = str(hit.get("ext") or "").lower()
    updated_rec = _update_index_h1(ws_norm, doc_id, ext=ext, html_in=html_in, text_in=text_in)

    return {
        "ok": True,
        "workspace_id": ws_norm,
        "doc_id": doc_id,
        "snapshot": snap_name,
        "h1": (updated_rec.get("h1") if isinstance(updated_rec, dict) else ""),
        "h1_source": (updated_rec.get("h1_source") if isinstance(updated_rec, dict) else ""),
        "h1_error": (updated_rec.get("h1_error") if isinstance(updated_rec, dict) else ""),
    }


@router.get("/get")
def get_file(workspace_id: str = Query("ws_betterhealthcheck_com"), doc_id: str = Query(...)):
    ws_norm = _ws(workspace_id)

    doc_id = (doc_id or "").strip()
    if not doc_id:
        raise HTTPException(status_code=400, detail="doc_id is required")

    items = _safe_read_index(_index_path(ws_norm))
    hit = next((x for x in items if x.get("doc_id") == doc_id), None)
    if not hit:
        raise HTTPException(status_code=404, detail="doc_id not found")

    path = _ws_dir(ws_norm) / (hit.get("stored_name") or "")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored file missing on disk")

    return FileResponse(
        str(path),
        filename=hit.get("filename") or "document",
        media_type=hit.get("content_type") or "application/octet-stream",
    )


@router.get("/preview")
def preview_file(workspace_id: str = Query("ws_betterhealthcheck_com"), doc_id: str = Query(...)):
    ws_norm = _ws(workspace_id)

    doc_id = (doc_id or "").strip()
    if not doc_id:
        raise HTTPException(status_code=400, detail="doc_id is required")

    items = _safe_read_index(_index_path(ws_norm))
    hit = next((x for x in items if x.get("doc_id") == doc_id), None)
    if not hit:
        raise HTTPException(status_code=404, detail="doc_id not found")

    path = _ws_dir(ws_norm) / (hit.get("stored_name") or "")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored file missing on disk")

    raw = path.read_bytes()
    ext = str(hit.get("ext") or _guess_ext(hit.get("filename") or "")).lower()
    preview = _extract_preview_from_bytes(hit.get("filename") or "document", ext, raw)

    return {
        "ok": True,
        "workspace_id": ws_norm,
        "doc_id": hit.get("doc_id"),
        "filename": preview.get("filename"),
        "ext": preview.get("ext"),
        "text": preview.get("text"),
        "html": preview.get("html"),
        "is_html": bool(preview.get("is_html")),
        "truncated": bool(preview.get("truncated")),
        "job_id": None,
        "processing_status": "not_applicable",
        "h1": hit.get("h1") or "",
        "h1_source": hit.get("h1_source") or "",
        "h1_error": hit.get("h1_error") or "",
    }


