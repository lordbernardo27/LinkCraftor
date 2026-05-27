from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import json
import re


DATA_DIR = Path(
    "backend/server/data/target_pools"
)


def _now_iso() -> str:
    return (
        datetime.utcnow()
        .isoformat() + "Z"
    )


def _norm_text(
    text: str,
) -> str:

    text = str(text or "")

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s\-]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def _normalize_slug(
    text: str,
) -> str:

    text = _norm_text(text)

    text = text.replace(
        "-",
        " ",
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def _safe_read_json(
    path: Path,
):

    try:

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return None


def _extract_title_candidates(
    item: Dict[str, Any],
) -> List[str]:

    candidates = []

    for key in [
        "title",
        "target_title",
        "label",
        "slug_label",
        "url_label",
    ]:

        value = item.get(key)

        if (
            isinstance(value, str)
            and value.strip()
        ):
            candidates.append(
                value.strip()
            )

    url = str(
        item.get("url", "")
    ).strip()

    if url:

        slug = (
            url.rstrip("/")
            .split("/")[-1]
        )

        slug = _normalize_slug(slug)

        if slug:
            candidates.append(slug)

    deduped = []

    seen = set()

    for c in candidates:

        n = _normalize_slug(c)

        if not n:
            continue

        if n in seen:
            continue

        seen.add(n)

        deduped.append(n)

    return deduped


def load_workspace_target_titles_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    collected = []

    scanned_files = []

    for path in DATA_DIR.rglob(
        f"*{workspace_id}*.json"
    ):

        scanned_files.append(
            str(path)
        )

        data = _safe_read_json(path)

        if not data:
            continue

        items = []

        if isinstance(data, dict):

            if isinstance(
                data.get("targets"),
                list,
            ):
                items.extend(
                    data["targets"]
                )

            elif isinstance(
                data.get("items"),
                list,
            ):
                items.extend(
                    data["items"]
                )

        elif isinstance(data, list):
            items.extend(data)

        for item in items:

            if not isinstance(
                item,
                dict,
            ):
                continue

            titles = (
                _extract_title_candidates(
                    item
                )
            )

            for title in titles:

                if not _is_valid_sitemap_title(
                    title
                ):
                    continue

                collected.append({

                    "normalized_title":
                        title,

                    "url":
                        item.get(
                            "url",
                            "",
                        ),

                    "source_file":
                        str(path),
                })

    grouped = defaultdict(list)

    for rec in collected:

        grouped[
            rec[
                "normalized_title"
            ]
        ].append(rec)

    return {

        "workspace_id":
            workspace_id,

        "generated_at":
            _now_iso(),

        "normalized_title_count":
            len(grouped),

        "target_title_map":
            dict(grouped),

        "scanned_files":
            scanned_files,

        "runtime_effect":
            "read_only_no_runtime_injection",

        "layer":
            "1.7.5.1_existing_target_pool_reader",
    }


def _looks_like_internal_id(
    text: str,
) -> bool:

    text = str(text or "").strip().lower()

    if not text:
        return True

    compact = text.replace(
        "-",
        ""
    ).replace(
        "_",
        ""
    )

    # Long hexadecimal/hash-like ids
    if re.fullmatch(
        r"[a-f0-9]{12,}",
        compact,
    ):
        return True

    # UUID-ish patterns
    if re.fullmatch(
        r"[a-z0-9\-_]{20,}",
        text,
    ):
        token_count = len(
            text.split()
        )

        if token_count <= 1:
            return True

    # Mostly numeric ids
    if re.fullmatch(
        r"[0-9]{8,}",
        compact,
    ):
        return True

    return False


def _is_valid_sitemap_title(
    text: str,
) -> bool:

    text = _normalize_slug(text)

    if not text:
        return False

    if _looks_like_internal_id(
        text
    ):
        return False

    tokens = text.split()

    if len(tokens) < 2:
        return False

    weak_tokens = {
        "page",
        "post",
        "article",
        "document",
        "item",
        "untitled",
    }

    weak_ratio = sum(
        1 for t in tokens
        if t in weak_tokens
    ) / max(len(tokens), 1)

    if weak_ratio >= 0.8:
        return False

    alpha_count = sum(
        1 for c in text
        if c.isalpha()
    )

    if alpha_count < 4:
        return False

    return True


def _extract_slug_from_url(
    url: str,
) -> str:

    url = str(url or "").strip()

    if not url:
        return ""

    slug = (
        url.rstrip("/")
        .split("/")[-1]
    )

    slug = slug.split("?")[0]

    slug = slug.split("#")[0]

    slug = _normalize_slug(slug)

    return slug.strip()


def build_slug_normalization_map_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    titles = (
        load_workspace_target_titles_v2(
            workspace_id
        )
    )

    slug_map = {}

    for normalized_title, recs in (
        titles.get(
            "target_title_map",
            {}
        ).items()
    ):

        for rec in recs:

            url = str(
                rec.get(
                    "url",
                    ""
                )
            ).strip()

            if not url:
                continue

            slug = (
                _extract_slug_from_url(
                    url
                )
            )

            if not slug:
                continue

            if not _is_valid_semantic_slug(
                slug
            ):
                continue

            slug_map[slug] = {

                "normalized_slug":
                    slug,

                "normalized_title":
                    normalized_title,

                "url":
                    url,

                "source_file":
                    rec.get(
                        "source_file",
                        ""
                    ),

                "generated_at":
                    _now_iso(),
            }

    return {

        "workspace_id":
            workspace_id,

        "generated_at":
            _now_iso(),

        "slug_count":
            len(slug_map),

        "slug_normalization_map":
            slug_map,

        "runtime_effect":
            "read_only_no_runtime_injection",

        "layer":
            "1.7.5.3_url_slug_normalization",
    }


def _is_valid_semantic_slug(
    slug: str,
) -> bool:

    slug = _normalize_slug(slug)

    if not slug:
        return False

    if _looks_like_internal_id(
        slug
    ):
        return False

    tokens = slug.split()

    if len(tokens) < 2:
        return False

    alpha_count = sum(
        1 for c in slug
        if c.isalpha()
    )

    if alpha_count < 4:
        return False

    weak_tokens = {
        "documents",
        "drafts",
        "posts",
        "article",
        "item",
        "page",
    }

    weak_ratio = sum(
        1 for t in tokens
        if t in weak_tokens
    ) / max(len(tokens), 1)

    if weak_ratio >= 0.7:
        return False

    return True

