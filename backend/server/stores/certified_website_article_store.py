from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


STORE_SCHEMA_VERSION = (
    "certified_website_article_store.v1"
)

DATA_ROOT = Path(
    "backend/server/data"
)

STORE_ROOT = (
    DATA_ROOT
    / "certified_website_articles"
)


def _utc_now() -> str:
    return datetime.now(
        UTC
    ).isoformat()


def _content_hash(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def _store_path_v1(
    workspace_id: str,
) -> Path:
    normalized_workspace_id = str(
        workspace_id or ""
    ).strip()

    if not normalized_workspace_id:
        raise ValueError(
            "workspace_id is required"
        )

    return (
        STORE_ROOT
        / (
            "certified_website_articles_"
            f"{normalized_workspace_id}.json"
        )
    )


def _empty_store_v1(
    workspace_id: str,
) -> dict[str, Any]:
    now = _utc_now()

    return {
        "schema_version":
            STORE_SCHEMA_VERSION,

        "workspace_id":
            workspace_id,

        "created_at":
            now,

        "updated_at":
            now,

        "article_count":
            0,

        "articles":
            {},
    }


def load_certified_website_article_store_v1(
    workspace_id: str,
) -> dict[str, Any]:
    path = _store_path_v1(
        workspace_id
    )

    if not path.exists():
        return _empty_store_v1(
            workspace_id
        )

    payload = json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise RuntimeError(
            "Certified Website Article Store "
            "must be a dictionary."
        )

    articles = payload.get(
        "articles"
    )

    if not isinstance(
        articles,
        dict,
    ):
        raise RuntimeError(
            "Certified Website Article Store "
            "articles must be a dictionary."
        )

    payload[
        "article_count"
    ] = len(
        articles
    )

    return payload


def save_certified_website_article_store_v1(
    workspace_id: str,
    store: dict[str, Any],
) -> Path:
    if not isinstance(
        store,
        dict,
    ):
        raise TypeError(
            "store must be a dictionary"
        )

    articles = store.get(
        "articles"
    )

    if not isinstance(
        articles,
        dict,
    ):
        raise ValueError(
            "store['articles'] must be "
            "a dictionary"
        )

    path = _store_path_v1(
        workspace_id
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    now = _utc_now()

    store[
        "schema_version"
    ] = STORE_SCHEMA_VERSION

    store[
        "workspace_id"
    ] = workspace_id

    store.setdefault(
        "created_at",
        now,
    )

    store[
        "updated_at"
    ] = now

    store[
        "article_count"
    ] = len(
        articles
    )

    temporary = path.with_suffix(
        path.suffix + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            store,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    temporary.replace(
        path
    )

    return path


def build_certified_website_article_v1(
    *,
    workspace_id: str,
    html_id: str,
    url: str,
    title: str,
    h1: str,
    headings: list[Any],
    content_blocks: list[dict[str, Any]],
    article_body: str,
    reconstruction: dict[str, Any],
    integrity: dict[str, Any],
    validation: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    workspace_id = str(
        workspace_id or ""
    ).strip()

    html_id = str(
        html_id or ""
    ).strip()

    url = str(
        url or ""
    ).strip()

    title = str(
        title or ""
    ).strip()

    h1 = str(
        h1 or ""
    ).strip()

    article_body = str(
        article_body or ""
    )

    if not workspace_id:
        raise ValueError(
            "workspace_id is required"
        )

    if not html_id:
        raise ValueError(
            "html_id is required"
        )

    if not url:
        raise ValueError(
            "url is required"
        )

    if not title:
        raise ValueError(
            "title is required"
        )

    if not article_body.strip():
        raise ValueError(
            "article_body is required"
        )

    if not isinstance(
        headings,
        list,
    ):
        raise TypeError(
            "headings must be a list"
        )

    if not isinstance(
        content_blocks,
        list,
    ):
        raise TypeError(
            "content_blocks must be a list"
        )

    if not isinstance(
        reconstruction,
        dict,
    ):
        raise TypeError(
            "reconstruction must be "
            "a dictionary"
        )

    if not isinstance(
        integrity,
        dict,
    ):
        raise TypeError(
            "integrity must be "
            "a dictionary"
        )

    if not isinstance(
        validation,
        dict,
    ):
        raise TypeError(
            "validation must be "
            "a dictionary"
        )

    integrity_passed = (
        integrity.get(
            "passed"
        )
        is True
    )

    validation_passed = (
        validation.get(
            "passed"
        )
        is True
    )

    eligible_for_wuc = bool(
        validation.get(
            "eligible_for_unified_content_document"
        )
        or validation.get(
            "eligible_for_wuc"
        )
    )

    if not integrity_passed:
        raise ValueError(
            "integrity result is not PASS"
        )

    if not validation_passed:
        raise ValueError(
            "article validation is not PASS"
        )

    if not eligible_for_wuc:
        raise ValueError(
            "article is not eligible for WUC"
        )

    now = _utc_now()

    return {
        "schema_version":
            STORE_SCHEMA_VERSION,

        "workspace_id":
            workspace_id,

        "html_id":
            html_id,

        "url":
            url,

        "title":
            title,

        "h1":
            h1,

        "headings":
            headings,

        "content_blocks":
            content_blocks,

        "article_body":
            article_body,

        "content_body":
            article_body,

        "article_body_hash":
            _content_hash(
                article_body
            ),

        "article_word_count":
            len(
                article_body.split()
            ),

        "reconstruction":
            reconstruction,

        "integrity":
            integrity,

        "validation":
            validation,

        "certification": {
            "status":
                "PASS",

            "integrity_passed":
                True,

            "article_validation_passed":
                True,

            "eligible_for_wuc":
                True,

            "certified_at":
                now,
        },

        "metadata":
            dict(
                metadata or {}
            ),

        "created_at":
            now,

        "updated_at":
            now,
    }


def upsert_certified_website_article_v1(
    *,
    workspace_id: str,
    article: dict[str, Any],
    save: bool = True,
) -> dict[str, Any]:
    if not isinstance(
        article,
        dict,
    ):
        raise TypeError(
            "article must be a dictionary"
        )

    html_id = str(
        article.get(
            "html_id"
        )
        or ""
    ).strip()

    if not html_id:
        raise ValueError(
            "article html_id is required"
        )

    if str(
        article.get(
            "workspace_id"
        )
        or ""
    ).strip() != str(
        workspace_id
    ).strip():
        raise ValueError(
            "article workspace_id does not "
            "match the target workspace"
        )

    store = (
        load_certified_website_article_store_v1(
            workspace_id
        )
    )

    articles = store[
        "articles"
    ]

    previous = articles.get(
        html_id
    )

    now = _utc_now()

    stored_article = dict(
        article
    )

    if isinstance(
        previous,
        dict,
    ):
        stored_article[
            "created_at"
        ] = previous.get(
            "created_at"
        ) or stored_article.get(
            "created_at"
        ) or now

    else:
        stored_article.setdefault(
            "created_at",
            now,
        )

    stored_article[
        "updated_at"
    ] = now

    articles[
        html_id
    ] = stored_article

    store[
        "article_count"
    ] = len(
        articles
    )

    if save:
        save_certified_website_article_store_v1(
            workspace_id,
            store,
        )

    return stored_article


def get_certified_website_article_v1(
    *,
    workspace_id: str,
    html_id: str,
) -> dict[str, Any] | None:
    store = (
        load_certified_website_article_store_v1(
            workspace_id
        )
    )

    article = store[
        "articles"
    ].get(
        str(
            html_id or ""
        ).strip()
    )

    return (
        dict(
            article
        )
        if isinstance(
            article,
            dict,
        )
        else None
    )
