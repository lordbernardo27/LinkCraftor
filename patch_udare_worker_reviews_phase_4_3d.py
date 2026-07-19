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
    "udare_review_document_builder "
    "import build_udare_review_document_v1"
)


if IMPORT_LINE not in text:
    existing_import = (
        "from backend.server.stores."
        "udare_store_index_builder "
        "import build_udare_store_index_v1"
    )

    if existing_import not in text:
        raise RuntimeError(
            "UDARE index-builder import was not found."
        )

    text = text.replace(
        existing_import,
        existing_import
        + "\n"
        + IMPORT_LINE,
        1,
    )


if "review_result = build_udare_review_document_v1(" not in text:
    marker = '''        index_result = build_udare_store_index_v1(
            workspace_id
        )
'''

    replacement = '''        review_result = build_udare_review_document_v1(
            workspace_id=
                workspace_id,

            metadata_path=
                str(
                    persisted.get(
                        "metadata_path"
                    )
                    or ""
                ),
        )

        if (
            not isinstance(
                review_result,
                dict,
            )
            or review_result.get(
                "ok"
            )
            is not True
        ):
            raise UdareWorkerError(
                "UDARE visual review document generation failed."
            )

        index_result = build_udare_store_index_v1(
            workspace_id
        )
'''

    if marker not in text:
        raise RuntimeError(
            "Worker index-refresh insertion point was not found."
        )

    text = text.replace(
        marker,
        replacement,
        1,
    )


if '"review_path":' not in text:
    marker = '''            "index_path":
                str(
                    index_result.get(
                        "index_path"
                    )
                    or ""
                ),
'''

    replacement = '''            "review_path":
                str(
                    review_result.get(
                        "review_path"
                    )
                    or ""
                ),

            "review_format":
                str(
                    review_result.get(
                        "format"
                    )
                    or ""
                ),

            "review_image_count":
                int(
                    review_result.get(
                        "image_count"
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
'''

    if marker not in text:
        raise RuntimeError(
            "Worker result-summary review insertion point "
            "was not found."
        )

    text = text.replace(
        marker,
        replacement,
        1,
    )


ast.parse(
    text,
    filename=str(
        path
    ),
)

path.write_text(
    text,
    encoding="utf-8",
)

print(
    "UDARE WORKER REVIEW INTEGRATION: PASS"
)
