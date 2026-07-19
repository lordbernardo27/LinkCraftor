from __future__ import annotations

import ast
from pathlib import Path


path = Path(
    "backend/server/stores/"
    "udare_store_index_builder.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)


if '"review_relative_path":' not in text:
    marker = '''    href = quote(
        relative_path,
        safe="/._-",
    )

    return {
'''

    replacement = '''    href = quote(
        relative_path,
        safe="/._-",
    )

    review_document = (
        record.get(
            "review_document"
        )
        or {}
    )

    if not isinstance(
        review_document,
        dict,
    ):
        review_document = {}

    review_relative_path = str(
        review_document.get(
            "relative_path"
        )
        or ""
    ).replace(
        "\\\\",
        "/",
    ).strip()

    review_path = (
        workspace_root
        / review_relative_path
        if review_relative_path
        else None
    )

    review_href = (
        quote(
            review_relative_path,
            safe="/._-",
        )
        if (
            review_path is not None
            and review_path.is_file()
        )
        else ""
    )

    return {
'''

    if marker not in text:
        raise RuntimeError(
            "Index article-row insertion point not found."
        )

    text = text.replace(
        marker,
        replacement,
        1,
    )


if '"review_href":' not in text:
    marker = '''        "href":
            href,

        "metadata_path":
'''

    replacement = '''        "href":
            href,

        "review_relative_path":
            review_relative_path,

        "review_href":
            review_href,

        "metadata_path":
'''

    if marker not in text:
        raise RuntimeError(
            "Index return-row insertion point not found."
        )

    text = text.replace(
        marker,
        replacement,
        1,
    )


if "Open Review" not in text:
    marker = '''    article_href = html.escape(
        str(
            article[
                "href"
            ]
        ),
        quote=True,
    )

    engine = html.escape(
'''

    replacement = '''    article_href = html.escape(
        str(
            article[
                "href"
            ]
        ),
        quote=True,
    )

    review_href = html.escape(
        str(
            article.get(
                "review_href"
            )
            or ""
        ),
        quote=True,
    )

    review_button = (
        f'<a class="review-button" '
        f'href="{review_href}">'
        f'Open Review</a>'
        if review_href
        else ""
    )

    engine = html.escape(
'''

    if marker not in text:
        raise RuntimeError(
            "Index review-button preparation point not found."
        )

    text = text.replace(
        marker,
        replacement,
        1,
    )


if '{review_button}' not in text:
    marker = '''        <a
            class="open-button"
            href="{article_href}"
        >
            Open Article
        </a>
    </div>
</article>
'''

    replacement = '''        <a
            class="open-button"
            href="{article_href}"
        >
            Open Article
        </a>

        {review_button}
    </div>
</article>
'''

    if marker not in text:
        raise RuntimeError(
            "Index article action block not found."
        )

    text = text.replace(
        marker,
        replacement,
        1,
    )


if ".review-button" not in text:
    marker = '''.open-button:hover {{
    background: #124894;
}}
'''

    replacement = '''.open-button:hover {{
    background: #124894;
}}

.article-action {{
    display: grid;
    gap: 9px;
}}

.review-button {{
    display: inline-flex;
    min-height: 42px;
    align-items: center;
    justify-content: center;
    padding: 8px 15px;
    border: 1px solid #1858b8;
    border-radius: 10px;
    background: #ffffff;
    color: #1858b8;
    font-weight: 750;
    text-decoration: none;
    white-space: nowrap;
}}

.review-button:hover {{
    background: #eaf1fb;
}}
'''

    if marker not in text:
        raise RuntimeError(
            "Index button stylesheet insertion point not found."
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
    "UDARE INDEX REVIEW LINKS PATCH: PASS"
)
