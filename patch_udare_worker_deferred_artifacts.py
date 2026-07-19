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


# ---------------------------------------------------------------
# Add os import.
# ---------------------------------------------------------------

if "\nimport os\n" not in text:
    future_line = (
        "from __future__ import annotations\n"
    )

    if future_line not in text:
        raise RuntimeError(
            "__future__ import was not found."
        )

    text = text.replace(
        future_line,
        future_line + "\nimport os\n",
        1,
    )


# ---------------------------------------------------------------
# Replace the global-artifact section after article persistence.
#
# Per job:
#   - reader article remains written
#   - metadata remains written
#   - visual review remains written
#
# Deferred during full population:
#   - manifest refresh
#   - index rebuild
# ---------------------------------------------------------------

start_marker = (
    "        manifest_result = _call_by_signature_v1(\n"
)

end_marker = (
    "        result_summary = {\n"
)

start_index = text.find(
    start_marker
)

if start_index < 0:
    raise RuntimeError(
        "Worker manifest-refresh block was not found."
    )

end_index = text.find(
    end_marker,
    start_index,
)

if end_index < 0:
    raise RuntimeError(
        "Worker result_summary block was not found."
    )


replacement = '''        defer_global_artifacts = (
            str(
                os.environ.get(
                    "UDARE_DEFER_GLOBAL_ARTIFACTS",
                    "",
                )
            ).strip().casefold()
            in {
                "1",
                "true",
                "yes",
                "on",
            }
        )

        review_result = build_udare_review_document_v1(
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

        if defer_global_artifacts:
            manifest = {
                "ok":
                    True,

                "record_count":
                    0,

                "deferred":
                    True,
            }

            index_result = {
                "ok":
                    True,

                "index_path":
                    "",

                "article_count":
                    0,

                "deferred":
                    True,
            }

        else:
            manifest_result = _call_by_signature_v1(
                manifest_refresher,
                {
                    "workspace_id":
                        workspace_id,

                    "tenant_id":
                        workspace_id,
                },
            )

            manifest = _as_mapping_v1(
                manifest_result,
                name="UDARE manifest refresh result",
            )

            if manifest.get(
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

'''

text = (
    text[:start_index]
    + replacement
    + text[end_index:]
)


# ---------------------------------------------------------------
# Add deferred-artifact evidence to result summary.
# ---------------------------------------------------------------

if '"global_artifacts_deferred":' not in text:
    marker = '''            "index_article_count":
                int(
                    index_result.get(
                        "article_count"
                    )
                    or 0
                ),

            "completed_at":
'''

    replacement = '''            "index_article_count":
                int(
                    index_result.get(
                        "article_count"
                    )
                    or 0
                ),

            "global_artifacts_deferred":
                defer_global_artifacts,

            "completed_at":
'''

    if marker not in text:
        raise RuntimeError(
            "Worker result-summary insertion point "
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

print(
    "UDARE WORKER GLOBAL-ARTIFACT DEFERRAL: PASS"
)
