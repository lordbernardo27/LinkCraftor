from __future__ import annotations

import json
from pathlib import Path
from typing import Any


STORE_VERSION = (
    "article_validation_store_v2"
)


def _candidate_paths(
    workspace_id: str,
) -> list[Path]:
    """
    Candidate locations for the certified
    Article Validation results.

    The first existing file will be used.
    """

    root = Path("backend/server/data")

    return [

        root
        / "article_validation"
        / f"article_validation_{workspace_id}.json",

        root
        / "article_validation"
        / workspace_id
        / "article_validation.json",

        root
        / "runtime"
        / "final_website_pipeline_certification"
        / "article_validation_review"
        / "article_validation_v2_final_results.json",
    ]


def load_article_validation_store_v2(
    workspace_id: str,
) -> dict[str, Any]:

    for path in _candidate_paths(
        workspace_id
    ):

        if not path.exists():
            continue

        payload = json.loads(
            path.read_text(
                encoding="utf-8-sig"
            )
        )

        rows = (
            payload.get("results")
            or payload.get("articles")
            or []
        )

        articles: dict[str, Any] = {}

        for row in rows:

            if not isinstance(
                row,
                dict,
            ):
                continue

            html_id = str(
                row.get("html_id")
                or ""
            ).strip()

            if not html_id:
                continue

            articles[
                html_id
            ] = row

        return {
            "store_version":
                STORE_VERSION,

            "workspace_id":
                workspace_id,

            "source_path":
                str(path),

            "article_count":
                len(articles),

            "articles":
                articles,
        }

    raise FileNotFoundError(
        "Unable to locate a certified "
        "Article Validation store."
    )
