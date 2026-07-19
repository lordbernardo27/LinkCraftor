from __future__ import annotations

from backend.server.stores import (
    udare_article_document_builder
    as builder
)

from backend.server.stores.udare_store import (
    REQUIRED_UDARE_ENGINE,
)


anchor = (
    '<a href="https://example.com/reference">'
)

expected_text = (
    "This paragraph contains a safe example link."
)

block = {
    "index":
        0,

    "type":
        "paragraph",

    "text":
        expected_text,

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


inline_html = (
    builder._render_inline_segments(
        block[
            "inline_content"
        ],
        expected_text,
    )
)

paragraph_html = (
    builder._render_paragraph(
        block
    )
)

block_html = (
    builder._render_block(
        block
    )
)


reconstruction = {
    "ok":
        True,

    "engine":
        REQUIRED_UDARE_ENGINE,

    "url":
        "https://example.com/article",

    "title":
        "Clickable Link Test",

    "h1":
        "",

    "article_body":
        expected_text,

    "content_blocks": [
        block
    ],
}


built = (
    builder.build_udare_article_reader_document_v1(
        reconstruction=
            reconstruction,

        document_id=
            "clickable_link_test",

        html_id=
            "raw_html_clickable_link_test",
    )
)


checks = {
    "inline_anchor_retained":
        anchor in inline_html,

    "paragraph_anchor_retained":
        anchor in paragraph_html,

    "block_anchor_retained":
        anchor in block_html,

    "final_document_anchor_retained":
        anchor
        in built[
            "article_document"
        ],

    "inline_visible_wording_preserved":
        builder._comparison_text(
            builder._visible_fragment_text(
                inline_html
            )
        )
        == builder._comparison_text(
            expected_text
        ),

    "block_visible_wording_preserved":
        builder._comparison_text(
            builder._visible_fragment_text(
                block_html
            )
        )
        == builder._comparison_text(
            expected_text
        ),

    "store_document_validation":
        built[
            "document_validation"
        ].get(
            "ok"
        )
        is True,
}


failed = [
    name

    for name, passed
    in checks.items()

    if not passed
]


print()
print("CLICKABLE-LINK REGRESSION CHECKS")

for name, passed in checks.items():
    print(
        f"  {name}:",
        (
            "PASS"
            if passed
            else "FAIL"
        ),
    )

print()
print(
    "Inline HTML:",
    inline_html,
)

print(
    "Final anchor retained:",
    anchor
    in built[
        "article_document"
    ],
)

print()
print("=" * 112)

if failed:
    print(
        "CLICKABLE-LINK REGRESSION: FAIL"
    )

    print(
        "Failed checks:",
        ", ".join(
            failed
        ),
    )

else:
    print(
        "CLICKABLE-LINK REGRESSION: PASS"
    )

print("=" * 112)

raise SystemExit(
    0
    if not failed
    else 1
)
