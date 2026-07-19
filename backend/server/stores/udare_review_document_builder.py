from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote


BUILDER_NAME = "udare_review_document_builder_v1"

REVIEW_FORMAT = (
    "udare_visual_review_document_v1"
)

DATA_ROOT = Path(
    "backend/server/data/udare_store"
)


class UdareReviewDocumentError(
    RuntimeError
):
    pass


def _safe_workspace_id(
    workspace_id: str,
) -> str:
    value = str(
        workspace_id
        or ""
    ).strip()

    if not value:
        raise UdareReviewDocumentError(
            "workspace_id is required."
        )

    safe = "".join(
        character
        if (
            character.isalnum()
            or character in "-_."
        )
        else "_"

        for character
        in value
    ).strip(
        "._"
    )

    if not safe:
        raise UdareReviewDocumentError(
            "workspace_id contains no usable characters."
        )

    return safe


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _load_json(
    path: Path,
) -> Dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(
                encoding="utf-8",
                errors="strict",
            )
        )

    except Exception as exc:
        raise UdareReviewDocumentError(
            f"Could not read metadata file {path}: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    if not isinstance(
        value,
        dict,
    ):
        raise UdareReviewDocumentError(
            f"Metadata file is not a JSON object: {path}"
        )

    return value


def _write_json_atomic(
    path: Path,
    value: Dict[str, Any],
) -> None:
    temporary = path.with_name(
        path.name + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary.replace(
        path
    )


def _sha256_bytes(
    value: bytes,
) -> str:
    return hashlib.sha256(
        value
    ).hexdigest()


def _extract_article_markup(
    article_html: str,
) -> str:
    match = re.search(
        r"<article\b[^>]*>.*?</article>",
        article_html,
        flags=(
            re.IGNORECASE
            | re.DOTALL
        ),
    )

    if match:
        return match.group(
            0
        )

    body_match = re.search(
        r"<body\b[^>]*>(.*?)</body>",
        article_html,
        flags=(
            re.IGNORECASE
            | re.DOTALL
        ),
    )

    if body_match:
        return body_match.group(
            1
        )

    raise UdareReviewDocumentError(
        "Reader document contains no article or body markup."
    )


def _extract_images(
    article_markup: str,
) -> List[Dict[str, str]]:
    images: List[
        Dict[str, str]
    ] = []

    for match in re.finditer(
        r"<img\b([^>]*)>",
        article_markup,
        flags=re.IGNORECASE,
    ):
        attributes = match.group(
            1
        )

        src_match = re.search(
            r'''(?:src|data-src)\s*=\s*
                ["']([^"']+)["']''',
            attributes,
            flags=(
                re.IGNORECASE
                | re.VERBOSE
            ),
        )

        alt_match = re.search(
            r'''alt\s*=\s*
                ["']([^"']*)["']''',
            attributes,
            flags=(
                re.IGNORECASE
                | re.VERBOSE
            ),
        )

        source = (
            src_match.group(
                1
            ).strip()
            if src_match
            else ""
        )

        alternative = (
            alt_match.group(
                1
            ).strip()
            if alt_match
            else ""
        )

        if source:
            images.append({
                "src":
                    source,

                "alt":
                    alternative,
            })

    return images


def _render_heading_sequence(
    headings: List[Any],
) -> str:
    if not headings:
        return (
            '<p class="empty-value">'
            'No headings were recorded.'
            '</p>'
        )

    items = []

    for index, heading in enumerate(
        headings,
        start=1,
    ):
        value = html.escape(
            str(
                heading
                or ""
            ).strip()
        )

        items.append(
            f"<li>"
            f"<span>{index}</span>"
            f"<div>{value}</div>"
            f"</li>"
        )

    return (
        '<ol class="heading-list">'
        + "".join(
            items
        )
        + "</ol>"
    )


def _render_image_evidence(
    images: List[
        Dict[str, str]
    ],
) -> str:
    if not images:
        return """
<div class="empty-state">
    No image elements were retained in this reconstructed article.
</div>
""".strip()

    cards = []

    for index, image in enumerate(
        images,
        start=1,
    ):
        source = html.escape(
            image[
                "src"
            ],
            quote=True,
        )

        alternative = html.escape(
            image[
                "alt"
            ]
            or f"Image {index}"
        )

        cards.append(
            f"""
<article class="image-card">
    <div class="image-preview">
        <img
            src="{source}"
            alt="{alternative}"
            loading="lazy"
        >
    </div>

    <div class="image-details">
        <strong>Image {index}</strong>
        <span>{alternative}</span>
        <a
            href="{source}"
            target="_blank"
            rel="noopener noreferrer"
        >
            Open image source
        </a>
    </div>
</article>
""".strip()
        )

    return "\n".join(
        cards
    )


def _render_review_document(
    *,
    record: Dict[str, Any],
    metadata_path: Path,
    article_relative_path: str,
    article_markup: str,
    image_evidence: List[Dict[str, str]],
) -> str:
    title = html.escape(
        str(
            record.get(
                "title"
            )
            or ""
        )
    )

    h1 = html.escape(
        str(
            record.get(
                "h1"
            )
            or ""
        )
    )

    source_url = str(
        record.get(
            "source_url"
        )
        or ""
    ).strip()

    source_url_text = html.escape(
        source_url
    )

    source_url_href = html.escape(
        source_url,
        quote=True,
    )

    workspace_id = html.escape(
        str(
            record.get(
                "workspace_id"
            )
            or ""
        )
    )

    document_id = html.escape(
        str(
            record.get(
                "document_id"
            )
            or ""
        )
    )

    html_id = html.escape(
        str(
            record.get(
                "html_id"
            )
            or ""
        )
    )

    engine = html.escape(
        str(
            record.get(
                "udare_engine"
            )
            or ""
        )
    )

    selected_tag = html.escape(
        str(
            record.get(
                "selected_tag"
            )
            or ""
        )
    )

    reconstruction_status = html.escape(
        str(
            record.get(
                "reconstruction_status"
            )
            or ""
        )
    )

    created_at = html.escape(
        str(
            record.get(
                "created_at_utc"
            )
            or ""
        )
    )

    content_integrity = (
        record.get(
            "content_integrity"
        )
        or {}
    )

    if not isinstance(
        content_integrity,
        dict,
    ):
        content_integrity = {}

    word_count = int(
        content_integrity.get(
            "reader_body_word_count"
        )
        or 0
    )

    character_count = int(
        content_integrity.get(
            "reader_body_character_count"
        )
        or 0
    )

    block_count = int(
        content_integrity.get(
            "content_block_count"
        )
        or 0
    )

    headings = record.get(
        "headings"
    )

    if not isinstance(
        headings,
        list,
    ):
        headings = []

    heading_sequence = (
        _render_heading_sequence(
            headings
        )
    )

    image_section = (
        _render_image_evidence(
            image_evidence
        )
    )

    reader_href = quote(
        "../"
        + article_relative_path.replace(
            "\\",
            "/",
        ),
        safe="/._-",
    )

    source_link = (
        f"""
<a
    href="{source_url_href}"
    target="_blank"
    rel="noopener noreferrer"
>
    {source_url_text}
</a>
""".strip()
        if source_url
        else (
            '<span class="empty-value">'
            'No source URL recorded.'
            '</span>'
        )
    )

    metadata_filename = html.escape(
        metadata_path.name
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>
<title>UDARE Visual Review — {title}</title>

<style>
:root {{
    color-scheme: light;
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}}

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: #eef1f6;
    color: #172033;
}}

a {{
    color: #175bb7;
}}

.review-page {{
    width: min(1500px, calc(100% - 32px));
    margin: 0 auto;
    padding: 30px 0 70px;
}}

.review-header {{
    padding: 30px;
    border-radius: 20px;
    background: #17233b;
    color: #ffffff;
}}

.review-header h1 {{
    margin: 0 0 10px;
    font-size: clamp(28px, 4vw, 46px);
}}

.review-header p {{
    margin: 6px 0;
    color: #d9e1ef;
}}

.review-actions {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 20px;
}}

.button {{
    display: inline-flex;
    min-height: 42px;
    align-items: center;
    padding: 9px 15px;
    border-radius: 10px;
    background: #ffffff;
    color: #17233b;
    font-weight: 750;
    text-decoration: none;
}}

.grid {{
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(260px, 1fr));
    gap: 14px;
    margin: 22px 0;
}}

.panel {{
    padding: 20px;
    border: 1px solid #d9dfeb;
    border-radius: 16px;
    background: #ffffff;
}}

.panel h2 {{
    margin: 0 0 16px;
    font-size: 20px;
}}

.fact-list {{
    display: grid;
    gap: 12px;
    margin: 0;
}}

.fact {{
    display: grid;
    grid-template-columns: 150px minmax(0, 1fr);
    gap: 10px;
}}

.fact dt {{
    color: #667188;
    font-weight: 750;
}}

.fact dd {{
    margin: 0;
    overflow-wrap: anywhere;
}}

.heading-list {{
    display: grid;
    gap: 8px;
    margin: 0;
    padding: 0;
    list-style: none;
}}

.heading-list li {{
    display: grid;
    grid-template-columns: 34px minmax(0, 1fr);
    gap: 10px;
    align-items: start;
    padding: 10px;
    border-radius: 10px;
    background: #f3f6fb;
}}

.heading-list li span {{
    display: inline-flex;
    width: 28px;
    height: 28px;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: #dce7f8;
    font-size: 12px;
    font-weight: 800;
}}

.checklist {{
    display: grid;
    gap: 10px;
}}

.check-item {{
    display: grid;
    grid-template-columns: 24px minmax(0, 1fr);
    gap: 9px;
    align-items: start;
    padding: 10px;
    border: 1px solid #dce2ec;
    border-radius: 10px;
}}

.checkbox {{
    width: 18px;
    height: 18px;
    border: 2px solid #8a96aa;
    border-radius: 4px;
}}

.image-grid {{
    display: grid;
    grid-template-columns:
        repeat(auto-fill, minmax(260px, 1fr));
    gap: 15px;
}}

.image-card {{
    overflow: hidden;
    border: 1px solid #dce2ec;
    border-radius: 13px;
    background: #ffffff;
}}

.image-preview {{
    min-height: 190px;
    background: #f3f5f9;
}}

.image-preview img {{
    display: block;
    width: 100%;
    height: 220px;
    object-fit: contain;
}}

.image-details {{
    display: grid;
    gap: 6px;
    padding: 13px;
    font-size: 13px;
    overflow-wrap: anywhere;
}}

.article-review {{
    margin-top: 22px;
    padding: 22px;
    border: 1px solid #d8deea;
    border-radius: 18px;
    background: #ffffff;
}}

.article-review > h2 {{
    margin: 0 0 8px;
    font-size: 27px;
}}

.article-review-note {{
    margin: 0 0 22px;
    color: #677187;
}}

.article-body {{
    padding: 25px;
    border: 1px solid #e0e5ee;
    border-radius: 14px;
    background: #ffffff;
    line-height: 1.65;
}}

.article-body img {{
    max-width: 100%;
    height: auto;
}}

.article-body table {{
    display: block;
    max-width: 100%;
    overflow-x: auto;
}}

.empty-state,
.empty-value {{
    color: #778197;
}}

footer {{
    margin-top: 28px;
    color: #687389;
    text-align: center;
    font-size: 13px;
}}

@media (max-width: 700px) {{
    .fact {{
        grid-template-columns: 1fr;
    }}

    .article-body {{
        padding: 14px;
    }}
}}
</style>
</head>

<body>
<main class="review-page">
    <header class="review-header">
        <h1>UDARE Visual Review</h1>

        <p>
            Certification and visual inspection document for:
            <strong>{title}</strong>
        </p>

        <p>
            Reader document and review document are separate,
            permanent UDARE Store artifacts.
        </p>

        <div class="review-actions">
            <a
                class="button"
                href="{reader_href}"
            >
                Open Reader Article
            </a>

            {
                f'<a class="button" href="{source_url_href}" '
                f'target="_blank" rel="noopener noreferrer">'
                f'Open Original Source</a>'
                if source_url
                else ""
            }
        </div>
    </header>

    <section class="grid">
        <article class="panel">
            <h2>Article Identity</h2>

            <dl class="fact-list">
                <div class="fact">
                    <dt>Workspace</dt>
                    <dd>{workspace_id}</dd>
                </div>

                <div class="fact">
                    <dt>Document ID</dt>
                    <dd>{document_id}</dd>
                </div>

                <div class="fact">
                    <dt>HTML ID</dt>
                    <dd>{html_id}</dd>
                </div>

                <div class="fact">
                    <dt>Metadata</dt>
                    <dd>{metadata_filename}</dd>
                </div>

                <div class="fact">
                    <dt>Source URL</dt>
                    <dd>{source_link}</dd>
                </div>
            </dl>
        </article>

        <article class="panel">
            <h2>Reconstruction Evidence</h2>

            <dl class="fact-list">
                <div class="fact">
                    <dt>Engine</dt>
                    <dd>{engine}</dd>
                </div>

                <div class="fact">
                    <dt>Status</dt>
                    <dd>{reconstruction_status}</dd>
                </div>

                <div class="fact">
                    <dt>Selected tag</dt>
                    <dd>{selected_tag}</dd>
                </div>

                <div class="fact">
                    <dt>Created</dt>
                    <dd>{created_at}</dd>
                </div>

                <div class="fact">
                    <dt>Content blocks</dt>
                    <dd>{block_count:,}</dd>
                </div>
            </dl>
        </article>

        <article class="panel">
            <h2>Content Measurements</h2>

            <dl class="fact-list">
                <div class="fact">
                    <dt>Title</dt>
                    <dd>{title}</dd>
                </div>

                <div class="fact">
                    <dt>H1</dt>
                    <dd>{h1}</dd>
                </div>

                <div class="fact">
                    <dt>Headings</dt>
                    <dd>{len(headings):,}</dd>
                </div>

                <div class="fact">
                    <dt>Words</dt>
                    <dd>{word_count:,}</dd>
                </div>

                <div class="fact">
                    <dt>Characters</dt>
                    <dd>{character_count:,}</dd>
                </div>

                <div class="fact">
                    <dt>Images retained</dt>
                    <dd>{len(image_evidence):,}</dd>
                </div>
            </dl>
        </article>
    </section>

    <section class="panel">
        <h2>Extracted Heading Sequence</h2>
        {heading_sequence}
    </section>

    <section class="panel">
        <h2>Manual Review Checklist</h2>

        <div class="checklist">
            <div class="check-item">
                <span class="checkbox"></span>
                <span>Title matches the source article.</span>
            </div>

            <div class="check-item">
                <span class="checkbox"></span>
                <span>H1 is correct and appears once.</span>
            </div>

            <div class="check-item">
                <span class="checkbox"></span>
                <span>Heading sequence is complete and correctly ordered.</span>
            </div>

            <div class="check-item">
                <span class="checkbox"></span>
                <span>Paragraphs, lists, tables and quotations are retained.</span>
            </div>

            <div class="check-item">
                <span class="checkbox"></span>
                <span>Images are present, relevant and correctly positioned.</span>
            </div>

            <div class="check-item">
                <span class="checkbox"></span>
                <span>Clickable links open the expected destinations.</span>
            </div>

            <div class="check-item">
                <span class="checkbox"></span>
                <span>No navigation, ads or unrelated boilerplate remain.</span>
            </div>

            <div class="check-item">
                <span class="checkbox"></span>
                <span>The reconstructed article body is complete.</span>
            </div>
        </div>
    </section>

    <section class="panel">
        <h2>Image Evidence</h2>

        <div class="image-grid">
            {image_section}
        </div>
    </section>

    <section class="article-review">
        <h2>Reconstructed Article Body</h2>

        <p class="article-review-note">
            This section displays the complete reader article
            inside the certification document.
        </p>

        <div class="article-body">
            {article_markup}
        </div>
    </section>

    <footer>
        Generated by {BUILDER_NAME}.
    </footer>
</main>
</body>
</html>
"""


def build_udare_review_document_v1(
    *,
    workspace_id: str,
    metadata_path: str | Path,
) -> Dict[str, Any]:
    workspace = _safe_workspace_id(
        workspace_id
    )

    workspace_root = (
        DATA_ROOT
        / workspace
    )

    metadata_file = Path(
        metadata_path
    )

    if not metadata_file.is_absolute():
        metadata_file = Path(
            metadata_path
        )

    if not metadata_file.is_file():
        raise UdareReviewDocumentError(
            "UDARE metadata file does not exist: "
            f"{metadata_file}"
        )

    record = _load_json(
        metadata_file
    )

    article_document = (
        record.get(
            "article_document"
        )
        or {}
    )

    if not isinstance(
        article_document,
        dict,
    ):
        raise UdareReviewDocumentError(
            "Metadata article_document is invalid."
        )

    article_relative_path = str(
        article_document.get(
            "relative_path"
        )
        or ""
    ).replace(
        "\\",
        "/",
    ).strip()

    if not article_relative_path:
        raise UdareReviewDocumentError(
            "Metadata contains no reader article path."
        )

    article_path = (
        workspace_root
        / article_relative_path
    )

    if not article_path.is_file():
        raise UdareReviewDocumentError(
            "Reader article does not exist: "
            f"{article_path}"
        )

    article_html = article_path.read_text(
        encoding="utf-8",
        errors="strict",
    )

    article_markup = _extract_article_markup(
        article_html
    )

    images = _extract_images(
        article_markup
    )

    reviews_dir = (
        workspace_root
        / "reviews"
    )

    reviews_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    reader_filename = article_path.stem

    review_filename = (
        reader_filename
        + "_review.html"
    )

    review_relative_path = (
        "reviews/"
        + review_filename
    )

    review_path = (
        reviews_dir
        / review_filename
    )

    review_html = _render_review_document(
        record=
            record,

        metadata_path=
            metadata_file,

        article_relative_path=
            article_relative_path,

        article_markup=
            article_markup,

        image_evidence=
            images,
    )

    review_bytes = review_html.encode(
        "utf-8"
    )

    temporary_review_path = (
        review_path.with_name(
            review_path.name
            + ".tmp"
        )
    )

    temporary_review_path.write_bytes(
        review_bytes
    )

    temporary_review_path.replace(
        review_path
    )

    now = _utc_now()

    record[
        "review_document"
    ] = {
        "format":
            REVIEW_FORMAT,

        "media_type":
            "text/html",

        "encoding":
            "utf-8",

        "filename":
            review_filename,

        "relative_path":
            review_relative_path,

        "sha256":
            _sha256_bytes(
                review_bytes
            ),

        "byte_length":
            len(
                review_bytes
            ),

        "image_count":
            len(
                images
            ),

        "heading_count":
            len(
                record.get(
                    "headings"
                )
                or []
            ),

        "builder":
            BUILDER_NAME,

        "generated_at_utc":
            now,
    }

    record[
        "updated_at_utc"
    ] = now

    _write_json_atomic(
        metadata_file,
        record,
    )

    return {
        "ok":
            True,

        "builder":
            BUILDER_NAME,

        "format":
            REVIEW_FORMAT,

        "workspace_id":
            workspace,

        "document_id":
            str(
                record.get(
                    "document_id"
                )
                or ""
            ),

        "review_path":
            str(
                review_path
            ),

        "review_relative_path":
            review_relative_path,

        "review_sha256":
            _sha256_bytes(
                review_bytes
            ),

        "review_byte_length":
            len(
                review_bytes
            ),

        "image_count":
            len(
                images
            ),

        "heading_count":
            len(
                record.get(
                    "headings"
                )
                or []
            ),

        "metadata_path":
            str(
                metadata_file
            ),
    }


def build_all_udare_review_documents_v1(
    workspace_id: str,
) -> Dict[str, Any]:
    workspace = _safe_workspace_id(
        workspace_id
    )

    metadata_dir = (
        DATA_ROOT
        / workspace
        / "metadata"
    )

    if not metadata_dir.is_dir():
        raise UdareReviewDocumentError(
            "UDARE metadata directory does not exist: "
            f"{metadata_dir}"
        )

    results = []

    for metadata_path in sorted(
        metadata_dir.glob(
            "*.json"
        )
    ):
        results.append(
            build_udare_review_document_v1(
                workspace_id=
                    workspace,

                metadata_path=
                    metadata_path,
            )
        )

    return {
        "ok":
            True,

        "workspace_id":
            workspace,

        "review_count":
            len(
                results
            ),

        "results":
            results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Build UDARE visual review documents."
        )
    )

    parser.add_argument(
        "--workspace-id",
        required=True,
    )

    parser.add_argument(
        "--metadata-path",
        default="",
    )

    arguments = parser.parse_args()

    if arguments.metadata_path:
        output = (
            build_udare_review_document_v1(
                workspace_id=
                    arguments.workspace_id,

                metadata_path=
                    arguments.metadata_path,
            )
        )

    else:
        output = (
            build_all_udare_review_documents_v1(
                arguments.workspace_id
            )
        )

    print(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        )
    )
