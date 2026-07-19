from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil
import time


PATH = Path(
    "backend/server/stores/raw_website_html_store.py"
)

if not PATH.is_file():
    raise RuntimeError(f"File not found: {PATH}")

timestamp = datetime.now(
    timezone.utc
).strftime("%Y%m%dT%H%M%SZ")

backup = PATH.with_name(
    PATH.name
    + f".before_safe_io_repair_{timestamp}.bak"
)

shutil.copy2(PATH, backup)

source = PATH.read_text(
    encoding="utf-8-sig"
)


# ------------------------------------------------------------------
# 1. Add required imports.
# ------------------------------------------------------------------

if "import os\n" not in source:
    source = source.replace(
        "import json\n",
        "import json\nimport os\n",
        1,
    )

if "import tempfile\n" not in source:
    source = source.replace(
        "import os\n",
        "import os\nimport tempfile\n",
        1,
    )

if "import time\n" not in source:
    source = source.replace(
        "import tempfile\n",
        "import tempfile\nimport time\n",
        1,
    )


# ------------------------------------------------------------------
# 2. Replace unsafe loader.
# ------------------------------------------------------------------

old_loader = '''def load_raw_website_html_store_v1(workspace_id: str) -> Dict[str, Any]:
    path = _store_path_v1(workspace_id)

    if not path.exists():
        return {
            "version": "raw_website_html_store_v1",
            "workspace_id": workspace_id,
            "pages": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "version": "raw_website_html_store_v1",
            "workspace_id": workspace_id,
            "pages": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "recovered_from_error": True,
        }
'''

new_loader = '''def load_raw_website_html_store_v1(workspace_id: str) -> Dict[str, Any]:
    path = _store_path_v1(workspace_id)

    if not path.exists():
        return {
            "version": "raw_website_html_store_v1",
            "workspace_id": workspace_id,
            "pages": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    last_error: Exception | None = None

    for attempt in range(1, 4):
        try:
            raw_text = path.read_text(
                encoding="utf-8"
            )

            store = json.loads(
                raw_text
            )

            if not isinstance(store, dict):
                raise ValueError(
                    "Raw HTML store root must be a JSON object."
                )

            pages = store.get("pages")

            if not isinstance(pages, dict):
                raise ValueError(
                    "Raw HTML store pages field must be a JSON object."
                )

            return store

        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            ValueError,
        ) as exc:
            last_error = exc

            if attempt < 3:
                time.sleep(
                    0.05 * attempt
                )

    raise RuntimeError(
        "Unable to read a valid Raw HTML store after "
        f"3 attempts: {path}. "
        f"Underlying error: "
        f"{type(last_error).__name__}: {last_error}"
    ) from last_error
'''

if old_loader not in source:
    raise RuntimeError(
        "Expected loader block was not found. "
        "No changes were written."
    )

source = source.replace(
    old_loader,
    new_loader,
    1,
)


# ------------------------------------------------------------------
# 3. Replace non-atomic save.
# ------------------------------------------------------------------

old_save = '''def save_raw_website_html_store_v1(
    workspace_id: str,
    store: Dict[str, Any],
) -> Path:
    path = _store_path_v1(workspace_id)
    store["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
'''

new_save = '''def save_raw_website_html_store_v1(
    workspace_id: str,
    store: Dict[str, Any],
) -> Path:
    path = _store_path_v1(workspace_id)

    store["updated_at_utc"] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    serialized = json.dumps(
        store,
        indent=2,
        ensure_ascii=False,
    )

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(path.parent),
            prefix=path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(
                serialized
            )
            temporary_file.flush()
            os.fsync(
                temporary_file.fileno()
            )

            temporary_path = Path(
                temporary_file.name
            )

        os.replace(
            temporary_path,
            path,
        )

    except Exception:
        if (
            temporary_path is not None
            and temporary_path.exists()
        ):
            temporary_path.unlink(
                missing_ok=True
            )

        raise

    return path
'''

if old_save not in source:
    raise RuntimeError(
        "Expected save block was not found. "
        "No changes were written."
    )

source = source.replace(
    old_save,
    new_save,
    1,
)


PATH.write_text(
    source,
    encoding="utf-8",
)

print("=" * 88)
print("RAW HTML STORE SAFE I/O REPAIR APPLIED")
print("=" * 88)
print("Modified:", PATH)
print("Backup:  ", backup)
print()
print("Changes:")
print("  1. Read failures are no longer converted into an empty store.")
print("  2. Store reads retry three times.")
print("  3. Underlying read/JSON errors are preserved.")
print("  4. Store writes now use atomic temporary-file replacement.")
