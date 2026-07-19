from __future__ import annotations

from backend.server.stores.udare_article_document_builder import (
    BUILDER_NAME,
    SUPPORTED_BLOCK_TYPES,
    UdareArticleDocumentBuilderError,
    build_udare_article_reader_document_v1,
)

from backend.server.stores.udare_store import (
    ARTICLE_DOCUMENT_FORMAT,
    REQUIRED_UDARE_ENGINE,
    validate_udare_article_document_v1,
)


print()
print("=" * 112)
print(
    "PHASE 3C — UDARE ARTICLE-DOCUMENT "
    "BUILDER VERIFICATION"
)
print("=" * 112)


blocks = [
    {
        "index":
            0,

        "type":
            "heading",

        "level":
            1,

        "text":
            "Synthetic UDARE Article",
    },

    {
        "index":
            1,

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
    },

    {
        "index":
            2,

        "type":
            "unordered_list",

        "items": [
            "First list item",
            "Second list item",
        ],

        "text":
            "First list item\nSecond list item",
    },

    {
        "index":
            3,

        "type":
            "blockquote",

        "text":
            "A retained quotation appears here.",
    },

    {
        "index":
            4,

        "type":
            "ordered_list",

        "items": [
            "First ordered step",
            "Second ordered step",
        ],

        "text":
            "First ordered step\nSecond ordered step",
    },

    {
        "index":
            5,

        "type":
            "table",

        "rows": [
            [
                "Column one",
                "Column two",
            ],
            [
                "Value one",
                "Value two",
            ],
        ],

        "text":
            (
                "Column one Column two "
                "Value one Value two"
            ),
    },

    {
        "index":
            6,

        "type":
            "figure",

        "image": {
            "src":
                "https://example.com/image.jpg",

            "alt":
                "Synthetic image",
        },

        "caption":
            "Synthetic figure caption.",

        "text":
            "Synthetic figure caption.",
    },

    {
        "index":
            7,

        "type":
            "link_group",

        "heading":
            "Sources",

        "links": [
            {
                "text":
                    "Synthetic source",

                "href":
                    "https://example.com/source",
            },
        ],

        "text":
            "Sources Synthetic source",
    },
]


article_body = "\n\n".join(
    str(
        block.get(
            "text"
        )
        or ""
    ).strip()

    for block in blocks

    if str(
        block.get(
            "text"
        )
        or ""
    ).strip()
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
        "Synthetic UDARE Article",

    "article_body":
        article_body,

    "content_blocks":
        blocks,
}


built = build_udare_article_reader_document_v1(
    reconstruction=
        reconstruction,

    source_url=
        reconstruction[
            "url"
        ],

    document_id=
        "synthetic_udare_document",

    html_id=
        "raw_html_synthetic",
)


checks = {
    "builder_name":
        built.get(
            "builder"
        )
        == BUILDER_NAME,

    "document_format":
        built.get(
            "article_document_format"
        )
        == ARTICLE_DOCUMENT_FORMAT,

    "engine":
        built.get(
            "udare_engine"
        )
        == REQUIRED_UDARE_ENGINE,

    "complete_html":
        (
            built[
                "article_document"
            ].lower().startswith(
                "<!doctype html>"
            )
            and "<html"
            in built[
                "article_document"
            ].lower()
            and "<head"
            in built[
                "article_document"
            ].lower()
            and "<body"
            in built[
                "article_document"
            ].lower()
        ),

    "utf8_charset":
        '<meta charset="utf-8">'
        in built[
            "article_document"
        ].lower(),

    "block_count":
        built.get(
            "content_block_count"
        )
        == len(
            blocks
        ),

    "clickable_link":
        (
            '<a href="https://example.com/reference">'
            in built[
                "article_document"
            ]
        ),

    "image_retained":
        (
            '<img src="https://example.com/image.jpg"'
            in built[
                "article_document"
            ]
        ),

    "store_validator":
        built[
            "document_validation"
        ].get(
            "ok"
        )
        is True,

    "all_supported_types_present":
        {
            block[
                "type"
            ]
            for block in blocks
        }.issubset(
            SUPPORTED_BLOCK_TYPES
        ),
}


unknown_type_blocked = False

try:
    invalid = {
        **reconstruction,

        "content_blocks": [
            {
                "index":
                    0,

                "type":
                    "invented_type",

                "text":
                    "Invalid",
            },
        ],

        "article_body":
            "Invalid",
    }

    build_udare_article_reader_document_v1(
        reconstruction=
            invalid,
    )

except UdareArticleDocumentBuilderError:
    unknown_type_blocked = True


checks[
    "unknown_block_type_blocked"
] = unknown_type_blocked


failed = [
    name

    for name, result
    in checks.items()

    if not result
]


print()
print("BUILDER")

print(
    "  Name:",
    BUILDER_NAME,
)

print(
    "  Output format:",
    ARTICLE_DOCUMENT_FORMAT,
)

print(
    "  Supported block types:",
    sorted(
        SUPPORTED_BLOCK_TYPES
    ),
)

print()
print("CHECKS")

for name, result in checks.items():
    print(
        f"  {name}:",
        (
            "PASS"
            if result
            else "FAIL"
        ),
    )

print()
print(
    "Document bytes:",
    len(
        built[
            "article_document_bytes"
        ]
    ),
)

print(
    "Reader words:",
    built.get(
        "reader_body_word_count"
    ),
)

print(
    "Store write performed:",
    False,
)

print(
    "Worker invoked:",
    False,
)

print(
    "Queue invoked:",
    False,
)

print()
print("=" * 112)

if failed:
    print(
        "PHASE 3C — UDARE ARTICLE-DOCUMENT "
        "BUILDER: FAIL"
    )

    print(
        "Failed checks:",
        ", ".join(
            failed
        ),
    )

else:
    print(
        "PHASE 3C — UDARE ARTICLE-DOCUMENT "
        "BUILDER: PASS"
    )

print("=" * 112)

raise SystemExit(
    0
    if not failed
    else 1
)
