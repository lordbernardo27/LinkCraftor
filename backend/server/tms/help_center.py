
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/tms")

HELP_ARTICLES_PATH = DATA_DIR / "help_articles.jsonl"
HELP_CATEGORIES_PATH = DATA_DIR / "help_categories.jsonl"
HELP_CENTER_AUDIT_PATH = DATA_DIR / "help_center_audit.jsonl"


@dataclass(frozen=True)
class HelpCategory:
    category_id: str
    name: str
    slug: str
    description: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class HelpArticle:
    article_id: str
    title: str
    slug: str
    category_id: str
    summary: str = ""
    content: str = ""
    tags: List[str] = field(default_factory=list)
    status: str = "draft"
    author_id: str | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class HelpCenterAuditEvent:
    event_type: str
    object_id: str
    object_type: str
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for path in (
        HELP_ARTICLES_PATH,
        HELP_CATEGORIES_PATH,
        HELP_CENTER_AUDIT_PATH,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_store()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 1000) -> List[Dict[str, Any]]:
    _ensure_store()

    lines = path.read_text(encoding="utf-8").splitlines()

    return [
        json.loads(line)
        for line in lines[-limit:]
        if line.strip()
    ]


def _article_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"article_{ts}"


def _category_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"category_{ts}"


def log_help_center_audit(
    event: HelpCenterAuditEvent,
) -> Dict[str, Any]:

    payload = asdict(event)

    _append_jsonl(
        HELP_CENTER_AUDIT_PATH,
        payload,
    )

    return payload


# ============================================================
# 13.1.2 CATEGORY SYSTEM
# ============================================================

def create_category(
    *,
    name: str,
    slug: str,
    description: str = "",
) -> Dict[str, Any]:

    category = HelpCategory(
        category_id=_category_id(),
        name=name,
        slug=slug,
        description=description,
    )

    payload = asdict(category)

    _append_jsonl(
        HELP_CATEGORIES_PATH,
        payload,
    )

    log_help_center_audit(
        HelpCenterAuditEvent(
            event_type="category_created",
            object_id=category.category_id,
            object_type="category",
            message=f"Category created: {name}",
        )
    )

    return payload


def read_categories(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        HELP_CATEGORIES_PATH,
        limit,
    )


# ============================================================
# 13.1.1 HELP ARTICLE MODEL
# ============================================================

def create_article(
    *,
    title: str,
    slug: str,
    category_id: str,
    summary: str = "",
    content: str = "",
    tags: List[str] | None = None,
    status: str = "draft",
    author_id: str | None = None,
) -> Dict[str, Any]:

    article = HelpArticle(
        article_id=_article_id(),
        title=title,
        slug=slug,
        category_id=category_id,
        summary=summary,
        content=content,
        tags=tags or [],
        status=status,
        author_id=author_id,
    )

    payload = asdict(article)

    _append_jsonl(
        HELP_ARTICLES_PATH,
        payload,
    )

    log_help_center_audit(
        HelpCenterAuditEvent(
            event_type="article_created",
            object_id=article.article_id,
            object_type="article",
            message=f"Article created: {title}",
        )
    )

    return payload


def read_articles(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        HELP_ARTICLES_PATH,
        limit,
    )


# ============================================================
# 13.1.3 SEARCH ENGINE
# ============================================================

def search_articles(
    query: str,
    limit: int = 50,
) -> List[Dict[str, Any]]:

    q = str(query).lower().strip()

    results = []

    for article in read_articles(limit=100000):

        haystack = " ".join([
            str(article.get("title", "")),
            str(article.get("summary", "")),
            str(article.get("content", "")),
            " ".join(article.get("tags", [])),
        ]).lower()

        if q in haystack:
            results.append(article)

    return results[:limit]


# ============================================================
# 13.1.4 ARTICLE EDITOR
# ============================================================

def update_article(
    article: Dict[str, Any],
    **updates,
) -> Dict[str, Any]:

    updated = {
        **article,
        **updates,
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    log_help_center_audit(
        HelpCenterAuditEvent(
            event_type="article_updated",
            object_id=str(
                article.get("article_id")
            ),
            object_type="article",
            message="Article updated",
        )
    )

    return updated


# ============================================================
# 13.1.5 PUBLIC KB FRONTEND
# ============================================================

def build_public_kb_payload() -> Dict[str, Any]:

    categories = read_categories()
    articles = read_articles()

    published = [
        a for a in articles
        if a.get("status") == "published"
    ]

    return {
        "categories": categories,
        "articles": published,
        "article_count": len(published),
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def read_help_center_audit(
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    return _read_jsonl(
        HELP_CENTER_AUDIT_PATH,
        limit,
    )
