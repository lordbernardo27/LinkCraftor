from pathlib import Path
import shutil


path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

backup = Path(
    "backend/server/backups/"
    "u8_11_strict_workspace_identity/"
    "uploaded_document_unified_content.py"
)

backup.parent.mkdir(
    parents=True,
    exist_ok=True,
)

shutil.copy2(
    path,
    backup,
)

print(
    "U8.11_BACKUP_CREATED: YES"
)


source = path.read_text(
    encoding="utf-8-sig",
)


old_fn = '''def _safe_workspace_id(workspace_id: str | None) -> str:
    raw = str(workspace_id or "default").strip()
    if not raw:
        raw = "default"
    raw = re.sub(r"[^a-zA-Z0-9_\\-]", "_", raw)
    return raw[:100]
'''

new_fn = '''def _safe_workspace_id(workspace_id: str | None) -> str:
    if workspace_id is None:
        raise ValueError(
            "workspace_id is required."
        )

    raw = str(workspace_id).strip()

    if not raw:
        raise ValueError(
            "workspace_id must be non-blank."
        )

    raw = re.sub(
        r"[^a-zA-Z0-9_\\-]",
        "_",
        raw,
    )

    if not raw:
        raise ValueError(
            "workspace_id is invalid after sanitization."
        )

    return raw[:100]
'''

if old_fn not in source:
    raise RuntimeError(
        "U8.11 could not locate current _safe_workspace_id implementation."
    )

source = source.replace(
    old_fn,
    new_fn,
    1,
)


path.write_text(
    source,
    encoding="utf-8",
)


patched = path.read_text(
    encoding="utf-8-sig",
)


if 'workspace_id or "default"' in patched:
    raise RuntimeError(
        "Silent default workspace fallback still exists."
    )

if 'raw = "default"' in patched:
    raise RuntimeError(
        "Legacy default workspace assignment still exists."
    )

if "workspace_id is None" not in patched:
    raise RuntimeError(
        "None workspace rejection was not installed."
    )

if "workspace_id must be non-blank." not in patched:
    raise RuntimeError(
        "Blank workspace rejection was not installed."
    )

if 're.sub(' not in patched:
    raise RuntimeError(
        "Filesystem-safe workspace sanitization was unexpectedly removed."
    )


print(
    "U8.11_SILENT_DEFAULT_WORKSPACE_REMOVED: YES"
)

print(
    "U8.11_NONE_WORKSPACE_REJECTED: YES"
)

print(
    "U8.11_BLANK_WORKSPACE_REJECTED: YES"
)

print(
    "U8.11_EXTERNAL_WORKSPACE_REQUIRED: YES"
)

print(
    "U8.11_PATH_SAFETY_SANITIZATION_PRESERVED: YES"
)

print(
    "U8.11_PATCH_APPLICATION: COMPLETE"
)

print(
    "U8.11_NEXT_STEP: WORKSPACE_IDENTITY_REGRESSION_VERIFICATION"
)