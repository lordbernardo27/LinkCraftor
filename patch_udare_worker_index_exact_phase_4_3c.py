from __future__ import annotations

import ast
from pathlib import Path


path = Path(
    "backend/server/workers/"
    "udare_reconstruction_worker.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)


IMPORT_LINE = (
    "from backend.server.stores."
    "udare_store_index_builder "
    "import build_udare_store_index_v1"
)


# ---------------------------------------------------------------------
# 1. Add the index-builder import before the first function definition.
# ---------------------------------------------------------------------

if IMPORT_LINE not in text:
    lines = text.splitlines(
        keepends=True
    )

    insertion_index = None

    for index, line in enumerate(
        lines
    ):
        stripped = line.lstrip()

        if (
            stripped.startswith("def ")
            or stripped.startswith("class ")
        ):
            insertion_index = index
            break

    if insertion_index is None:
        raise RuntimeError(
            "Could not locate the worker import boundary."
        )

    lines.insert(
        insertion_index,
        IMPORT_LINE + "\n\n",
    )

    text = "".join(lines)


# ---------------------------------------------------------------------
# 2. Insert index generation after manifest validation and before the
#    result_summary dictionary.
# ---------------------------------------------------------------------

if "index_result = build_udare_store_index_v1(" not in text:
    marker = '''        if manifest.get(
            "ok"
        ) is not True:
            raise UdareWorkerError(
                "UDARE Store manifest refresh failed."
            )

        result_summary = {
'''

    replacement = '''        if manifest.get(
            "ok"
        ) is not True:
            raise UdareWorkerError(
                "UDARE Store manifest refresh failed."
            )

        index_result = build_udare_store_index_v1(
            workspace_id
        )

        if (
            not isinstance(
                index_result,
                dict,
            )
            or index_result.get(
                "ok"
            )
            is not True
        ):
            raise UdareWorkerError(
                "UDARE Store index generation failed."
            )

        result_summary = {
'''

    if marker not in text:
        raise RuntimeError(
            "Confirmed manifest-success insertion point "
            "was not found."
        )

    text = text.replace(
        marker,
        replacement,
        1,
    )


# ---------------------------------------------------------------------
# 3. Add index evidence to the successful worker result.
# ---------------------------------------------------------------------

if '"index_path":' not in text:
    marker = '''            "manifest_record_count":
                int(
                    manifest.get(
                        "record_count"
                    )
                    or 0
                ),

            "completed_at":
'''

    replacement = '''            "manifest_record_count":
                int(
                    manifest.get(
                        "record_count"
                    )
                    or 0
                ),

            "index_path":
                str(
                    index_result.get(
                        "index_path"
                    )
                    or ""
                ),

            "index_article_count":
                int(
                    index_result.get(
                        "article_count"
                    )
                    or 0
                ),

            "completed_at":
'''

    if marker not in text:
        raise RuntimeError(
            "Confirmed result-summary insertion point "
            "was not found."
        )

    text = text.replace(
        marker,
        replacement,
        1,
    )


ast.parse(
    text,
    filename=str(path),
)

path.write_text(
    text,
    encoding="utf-8",
)

print("UDARE WORKER INDEX INTEGRATION: PASS")
