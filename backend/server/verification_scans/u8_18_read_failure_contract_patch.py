from pathlib import Path
import shutil


path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

backup = Path(
    "backend/server/backups/"
    "u8_18_read_failure_contract/"
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
    "U8.18_BACKUP_CREATED: YES"
)


source = path.read_text(
    encoding="utf-8-sig",
)


old_block = '''def read_uduc(workspace_id: str, document_id: str) -> Dict[str, Any]:
    path = uduc_output_path(workspace_id, document_id)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}
'''


new_block = '''def read_uduc(workspace_id: str, document_id: str) -> Dict[str, Any]:
    path = uduc_output_path(workspace_id, document_id)

    if not path.exists():
        return {}

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            "Persisted UDUC must be a JSON object."
        )

    return data
'''


if old_block not in source:
    raise RuntimeError(
        "U8.18 could not locate exact read_uduc block."
    )


source = source.replace(
    old_block,
    new_block,
    1,
)


path.write_text(
    source,
    encoding="utf-8",
)


patched = path.read_text(
    encoding="utf-8-sig",
)


if new_block not in patched:
    raise RuntimeError(
        "U8.18 read_uduc failure-contract patch not installed."
    )


if "except Exception" in new_block:
    raise RuntimeError(
        "U8.18 broad read exception swallowing still present."
    )


print(
    "U8.18_MISSING_READ_RETURNS_EMPTY_DICT: YES"
)

print(
    "U8.18_MALFORMED_JSON_EXCEPTION_SURFACES: YES"
)

print(
    "U8.18_NON_OBJECT_JSON_REJECTED: YES"
)

print(
    "U8.18_BROAD_READ_EXCEPTION_SWALLOWING_REMOVED: YES"
)

print(
    "U8.18_READ_FAILURE_CONTRACT_PATCH: COMPLETE"
)

print(
    "U8.18_NEXT_STEP: FAILURE_CONTRACT_REGRESSION_VERIFICATION"
)