from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path


from backend.server.stores import (
    udare_article_document_builder
    as builder
)

from backend.server.stores.udare_store import (
    REQUIRED_UDARE_ENGINE,
)


ROOT = Path(__file__).resolve().parent

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "udare_phase_3c_clickable_link_inspection"
    / "udare_phase_3c_clickable_link_inspection.json"
)


paragraph_block = {
    "index":
        0,

    "type":
        "paragraph",

    "text":
        "This paragraph contains a safe example link.",

    "inline_content": [
        {
            "type":
                "text",

            "text":
                "This paragraph contains a safe ",
        },
        {
            "type":
                "link",

            "text":
                "example link",

            "href":
                "https://example.com/reference",
        },
        {
            "type":
                "text",

            "text":
                ".",
        },
    ],
}


expected_text = str(
    paragraph_block[
        "text"
    ]
)


inline_html = (
    builder._render_inline_segments(
        paragraph_block[
            "inline_content"
        ],
        expected_text,
    )
)


inline_visible_text = (
    builder._visible_fragment_text(
        inline_html
    )
)


normalized_expected = (
    builder._normalized_text(
        expected_text
    )
)


normalized_inline_visible = (
    builder._normalized_text(
        inline_visible_text
    )
)


paragraph_html = (
    builder._render_paragraph(
        paragraph_block
    )
)


paragraph_visible_text = (
    builder._visible_fragment_text(
        paragraph_html
    )
)


rendered_block_html = (
    builder._render_block(
        paragraph_block
    )
)


rendered_block_visible_text = (
    builder._visible_fragment_text(
        rendered_block_html
    )
)


reconstruction = {
    "ok":
        True,

    "engine":
        REQUIRED_UDARE_ENGINE,

    "url":
        "https://example.com/synthetic-article",

    "title":
        "Synthetic UDARE Article",

    "h1":
        "",

    "article_body":
        expected_text,

    "content_blocks": [
        paragraph_block
    ],
}


build_error = ""
built = None

try:
    built = (
        builder.build_udare_article_reader_document_v1(
            reconstruction=
                reconstruction,

            source_url=
                reconstruction[
                    "url"
                ],

            document_id=
                "link_failure_inspection",

            html_id=
                "raw_html_link_failure_inspection",
        )
    )

except Exception as exc:
    build_error = (
        f"{type(exc).__name__}: {exc}"
    )


article_document = (
    str(
        built.get(
            "article_document"
        )
        or ""
    )
    if isinstance(
        built,
        dict,
    )
    else ""
)


anchor_literal = (
    '<a href="https://example.com/reference">'
)


checks = {
    "inline_renderer_returned_anchor":
        anchor_literal
        in inline_html,

    "paragraph_renderer_returned_anchor":
        anchor_literal
        in paragraph_html,

    "block_renderer_returned_anchor":
        anchor_literal
        in rendered_block_html,

    "final_document_returned_anchor":
        anchor_literal
        in article_document,

    "inline_visible_matches_expected":
        normalized_inline_visible
        == normalized_expected,

    "paragraph_visible_matches_expected":
        builder._normalized_text(
            paragraph_visible_text
        )
        == normalized_expected,

    "block_visible_matches_expected":
        builder._normalized_text(
            rendered_block_visible_text
        )
        == normalized_expected,

    "full_build_succeeded":
        built is not None,

    "store_document_validation_passed":
        (
            bool(
                built[
                    "document_validation"
                ].get(
                    "ok"
                )
            )
            if isinstance(
                built,
                dict,
            )
            else False
        ),
}


diagnosis = []

if (
    anchor_literal
    not in inline_html
):
    diagnosis.append(
        "inline_renderer_removed_anchor"
    )

if (
    anchor_literal
    in inline_html
    and anchor_literal
    not in paragraph_html
):
    diagnosis.append(
        "paragraph_renderer_removed_anchor"
    )

if (
    anchor_literal
    in paragraph_html
    and anchor_literal
    not in rendered_block_html
):
    diagnosis.append(
        "block_wording_guard_removed_anchor"
    )

if (
    normalized_inline_visible
    != normalized_expected
):
    diagnosis.append(
        "inline_visible_text_comparison_mismatch"
    )

if (
    "link ." in normalized_inline_visible
    and "link." in normalized_expected
):
    diagnosis.append(
        "punctuation_spacing_mismatch_after_html_parsing"
    )

if not diagnosis:
    diagnosis.append(
        "cause_not_resolved_by_current_inspection"
    )


report = {
    "schema_version":
        "udare_phase_3c_clickable_link_inspection_v1",

    "generated_at_utc":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "expected_text":
        expected_text,

    "normalized_expected":
        normalized_expected,

    "inline_html":
        inline_html,

    "inline_visible_text":
        inline_visible_text,

    "normalized_inline_visible":
        normalized_inline_visible,

    "paragraph_html":
        paragraph_html,

    "paragraph_visible_text":
        paragraph_visible_text,

    "rendered_block_html":
        rendered_block_html,

    "rendered_block_visible_text":
        rendered_block_visible_text,

    "article_document":
        article_document,

    "build_error":
        build_error,

    "checks":
        checks,

    "diagnosis":
        diagnosis,

    "relevant_source": {
        "_render_inline_segments":
            inspect.getsource(
                builder._render_inline_segments
            ),

        "_render_paragraph":
            inspect.getsource(
                builder._render_paragraph
            ),

        "_render_block":
            inspect.getsource(
                builder._render_block
            ),

        "_visible_fragment_text":
            inspect.getsource(
                builder._visible_fragment_text
            ),

        "_normalized_text":
            inspect.getsource(
                builder._normalized_text
            ),
    },

    "source_modified":
        False,

    "worker_invoked":
        False,

    "queue_invoked":
        False,

    "udare_store_write_performed":
        False,
}


REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_PATH.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)


print()
print("EXPECTED TEXT")

print(
    repr(
        expected_text
    )
)

print()
print("INLINE RENDERER")

print(
    "  HTML:",
    repr(
        inline_html
    ),
)

print(
    "  Visible text:",
    repr(
        inline_visible_text
    ),
)

print(
    "  Normalized expected:",
    repr(
        normalized_expected
    ),
)

print(
    "  Normalized visible:",
    repr(
        normalized_inline_visible
    ),
)

print(
    "  Anchor retained:",
    checks[
        "inline_renderer_returned_anchor"
    ],
)

print()
print("PARAGRAPH RENDERER")

print(
    "  HTML:",
    repr(
        paragraph_html
    ),
)

print(
    "  Visible text:",
    repr(
        paragraph_visible_text
    ),
)

print(
    "  Anchor retained:",
    checks[
        "paragraph_renderer_returned_anchor"
    ],
)

print()
print("BLOCK WORDING GUARD")

print(
    "  HTML:",
    repr(
        rendered_block_html
    ),
)

print(
    "  Visible text:",
    repr(
        rendered_block_visible_text
    ),
)

print(
    "  Anchor retained:",
    checks[
        "block_renderer_returned_anchor"
    ],
)

print()
print("FINAL DOCUMENT")

print(
    "  Build succeeded:",
    checks[
        "full_build_succeeded"
    ],
)

print(
    "  Anchor retained:",
    checks[
        "final_document_returned_anchor"
    ],
)

print(
    "  Validation passed:",
    checks[
        "store_document_validation_passed"
    ],
)

if build_error:
    print(
        "  Build error:",
        build_error,
    )

print()
print("DIAGNOSIS")

for item in diagnosis:
    print(
        "  -",
        item,
    )

print()
print(
    "Report:",
    REPORT_PATH,
)

print()
print("=" * 112)
print(
    "CLICKABLE-LINK FAILURE INSPECTION: COMPLETE"
)
print("=" * 112)

print(
    "No source file was modified."
)

print(
    "No queue, worker, reconstruction engine "
    "or UDARE Store write was invoked."
)
