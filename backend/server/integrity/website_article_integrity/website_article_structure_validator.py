"""Website reconstructed-article structure validation.

Phase 4.4.1 validates the structure of reader-ready HTML documents stored
in the UDARE Store. It does not alter, repair, quarantine, or delete articles.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable


VALIDATOR_VERSION = "website_article_structure_validator_v1"
PHASE = "4.4.1"
PHASE_NAME = "Validate Reconstructed Article Structure"

DOCTYPE_PATTERN = re.compile(
    r"<!doctype\s+html(?:\s+[^>]*)?>",
    flags=re.IGNORECASE,
)

CLOSING_HTML_PATTERN = re.compile(
    r"</html\s*>",
    flags=re.IGNORECASE,
)

CLOSING_BODY_PATTERN = re.compile(
    r"</body\s*>",
    flags=re.IGNORECASE,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalize_visible_text(value: str) -> str:
    return " ".join(value.split())


class ArticleHTMLParser(HTMLParser):
    """Collect structural observations without changing the document."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)

        self.start_counts: Counter[str] = Counter()
        self.end_counts: Counter[str] = Counter()

        self.body_depth = 0
        self.title_depth = 0

        self.body_text_parts: list[str] = []
        self.title_parts: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        del attrs

        normalized_tag = tag.lower()
        self.start_counts[normalized_tag] += 1

        if normalized_tag == "body":
            self.body_depth += 1

        if normalized_tag == "title":
            self.title_depth += 1

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        del attrs
        self.start_counts[tag.lower()] += 1

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.lower()
        self.end_counts[normalized_tag] += 1

        if normalized_tag == "title" and self.title_depth > 0:
            self.title_depth -= 1

        if normalized_tag == "body" and self.body_depth > 0:
            self.body_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth > 0:
            self.title_parts.append(data)

        if self.body_depth > 0:
            self.body_text_parts.append(data)

    @property
    def title_text(self) -> str:
        return normalize_visible_text(" ".join(self.title_parts))

    @property
    def visible_body_text(self) -> str:
        return normalize_visible_text(" ".join(self.body_text_parts))


@dataclass(frozen=True)
class StructureValidationResult:
    result_id: str
    validator_version: str
    phase: str
    workspace_id: str
    source_record_id: str
    article_path: str
    metadata_path: str | None
    metadata_exists: bool
    file_size_bytes: int
    file_sha256: str
    validated_at: str
    status: str
    failure_reasons: list[str]
    checks: dict[str, bool]
    observations: dict[str, Any]


def atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )

    temporary_path = Path(temporary_name)

    try:
        with os.fdopen(
            file_descriptor,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink(missing_ok=True)


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(
        path,
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
    )


def validate_article_structure(
    *,
    article_path: Path,
    metadata_root: Path,
    workspace_id: str,
    articles_root: Path,
) -> StructureValidationResult:
    raw_bytes = article_path.read_bytes()

    utf8_decodable = True

    try:
        html = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        utf8_decodable = False
        html = raw_bytes.decode(
            "utf-8",
            errors="replace",
        )

    parser = ArticleHTMLParser()
    parser_error: str | None = None

    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:
        parser_error = f"{type(exc).__name__}: {exc}"

    source_record_id = article_path.stem

    metadata_path = metadata_root / f"{source_record_id}.json"
    metadata_exists = metadata_path.is_file()

    file_size_bytes = len(raw_bytes)
    visible_body_text = parser.visible_body_text
    title_text = parser.title_text

    checks = {
        "file_extension_is_html": article_path.suffix.lower() == ".html",
        "file_is_not_empty": file_size_bytes > 0,
        "utf8_decodable": utf8_decodable,
        "contains_no_null_bytes": b"\x00" not in raw_bytes,
        "doctype_present": bool(DOCTYPE_PATTERN.search(html)),
        "single_html_root_open": parser.start_counts["html"] == 1,
        "single_html_root_close": parser.end_counts["html"] == 1,
        "single_head_open": parser.start_counts["head"] == 1,
        "single_head_close": parser.end_counts["head"] == 1,
        "single_body_open": parser.start_counts["body"] == 1,
        "single_body_close": parser.end_counts["body"] == 1,
        "title_element_present": parser.start_counts["title"] >= 1,
        "title_text_present": bool(title_text),
        "closing_body_markup_present": bool(
            CLOSING_BODY_PATTERN.search(html)
        ),
        "closing_html_markup_present": bool(
            CLOSING_HTML_PATTERN.search(html)
        ),
        "visible_body_text_present": bool(visible_body_text),
        "html_parser_completed": parser_error is None,
    }

    failure_reasons = [
        check_name
        for check_name, passed in checks.items()
        if not passed
    ]

    status = "PASS" if not failure_reasons else "FAIL"

    relative_article_path = article_path.relative_to(
        articles_root.parent
    ).as_posix()

    result_seed = (
        f"{workspace_id}|{source_record_id}|"
        f"{relative_article_path}|{sha256_bytes(raw_bytes)}"
    )

    result_id = (
        "wai_structure_"
        + hashlib.sha256(
            result_seed.encode("utf-8")
        ).hexdigest()[:24]
    )

    observations: dict[str, Any] = {
        "title_text_length": len(title_text),
        "visible_body_text_length": len(visible_body_text),
        "html_start_count": parser.start_counts["html"],
        "html_end_count": parser.end_counts["html"],
        "head_start_count": parser.start_counts["head"],
        "head_end_count": parser.end_counts["head"],
        "body_start_count": parser.start_counts["body"],
        "body_end_count": parser.end_counts["body"],
        "title_start_count": parser.start_counts["title"],
        "title_end_count": parser.end_counts["title"],
        "h1_count": parser.start_counts["h1"],
        "h2_count": parser.start_counts["h2"],
        "h3_count": parser.start_counts["h3"],
        "article_element_count": parser.start_counts["article"],
        "main_element_count": parser.start_counts["main"],
        "paragraph_count": parser.start_counts["p"],
        "list_item_count": parser.start_counts["li"],
        "anchor_count": parser.start_counts["a"],
        "image_count": parser.start_counts["img"],
        "parser_error": parser_error,
    }

    return StructureValidationResult(
        result_id=result_id,
        validator_version=VALIDATOR_VERSION,
        phase=PHASE,
        workspace_id=workspace_id,
        source_record_id=source_record_id,
        article_path=relative_article_path,
        metadata_path=(
            metadata_path.relative_to(
                metadata_root.parent
            ).as_posix()
            if metadata_exists
            else None
        ),
        metadata_exists=metadata_exists,
        file_size_bytes=file_size_bytes,
        file_sha256=sha256_bytes(raw_bytes),
        validated_at=utc_now(),
        status=status,
        failure_reasons=failure_reasons,
        checks=checks,
        observations=observations,
    )


def write_jsonl(
    path: Path,
    records: Iterable[StructureValidationResult],
) -> None:
    lines = [
        json.dumps(
            asdict(record),
            ensure_ascii=False,
            sort_keys=True,
        )
        for record in records
    ]

    atomic_write_text(
        path,
        "\n".join(lines) + ("\n" if lines else ""),
    )


def run_structure_validation(
    *,
    project_root: Path,
    workspace_id: str,
    expected_store_count: int,
    expected_upstream_count: int,
    deferred_upstream_count: int,
) -> dict[str, Any]:
    data_root = (
        project_root
        / "backend"
        / "server"
        / "data"
    )

    udare_workspace_root = (
        data_root
        / "udare_store"
        / workspace_id
    )

    articles_root = udare_workspace_root / "articles"
    metadata_root = udare_workspace_root / "metadata"

    if not articles_root.is_dir():
        raise FileNotFoundError(
            f"UDARE articles directory not found: {articles_root}"
        )

    article_paths = sorted(
        path
        for path in articles_root.rglob("*.html")
        if path.is_file()
    )

    if len(article_paths) != expected_store_count:
        raise RuntimeError(
            "Unexpected UDARE article count. "
            f"Expected {expected_store_count}, "
            f"found {len(article_paths)}."
        )

    results: list[StructureValidationResult] = []

    for index, article_path in enumerate(
        article_paths,
        start=1,
    ):
        results.append(
            validate_article_structure(
                article_path=article_path,
                metadata_root=metadata_root,
                workspace_id=workspace_id,
                articles_root=articles_root,
            )
        )

        if index % 100 == 0:
            print(
                f"Validated {index} of "
                f"{len(article_paths)} articles..."
            )

    pass_count = sum(
        result.status == "PASS"
        for result in results
    )

    fail_count = len(results) - pass_count

    failure_reason_counts: Counter[str] = Counter()

    for result in results:
        failure_reason_counts.update(
            result.failure_reasons
        )

    metadata_missing_count = sum(
        not result.metadata_exists
        for result in results
    )

    output_root = (
        data_root
        / "website_article_integrity"
        / workspace_id
        / "structure"
    )

    results_path = output_root / "structure_results.jsonl"
    summary_path = output_root / "structure_summary.json"

    write_jsonl(
        results_path,
        results,
    )

    summary: dict[str, Any] = {
        "schema_version": "1.0",
        "validator_version": VALIDATOR_VERSION,
        "phase": PHASE,
        "phase_name": PHASE_NAME,
        "workspace_id": workspace_id,
        "generated_at": utc_now(),
        "execution_status": "COMPLETE",
        "certification_status": "NOT_YET_CERTIFIED",
        "source_store": "UDARE Store",
        "source_articles_directory": str(articles_root),
        "expected_upstream_count": expected_upstream_count,
        "deferred_upstream_count": deferred_upstream_count,
        "expected_store_count": expected_store_count,
        "articles_discovered": len(article_paths),
        "articles_validated": len(results),
        "structural_pass_count": pass_count,
        "structural_fail_count": fail_count,
        "metadata_missing_count": metadata_missing_count,
        "all_stored_articles_validated": (
            len(results) == expected_store_count
        ),
        "all_stored_articles_structurally_valid": (
            fail_count == 0
        ),
        "failure_reason_counts": dict(
            sorted(failure_reason_counts.items())
        ),
        "results_path": str(results_path),
        "important_notes": [
            (
                "The three upstream pages absent from the UDARE Store "
                "are deferred and were not counted as integrity failures."
            ),
            (
                "This phase performed read-only validation and did not "
                "modify or quarantine any UDARE article."
            ),
            (
                "H1, ARTICLE, and MAIN elements are recorded as "
                "observations but are not mandatory structural rules."
            ),
        ],
    }

    atomic_write_json(
        summary_path,
        summary,
    )

    return summary


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate reconstructed UDARE article structure."
        )
    )

    parser.add_argument(
        "--project-root",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--workspace-id",
        required=True,
    )

    parser.add_argument(
        "--expected-store-count",
        required=True,
        type=int,
    )

    parser.add_argument(
        "--expected-upstream-count",
        required=True,
        type=int,
    )

    parser.add_argument(
        "--deferred-upstream-count",
        required=True,
        type=int,
    )

    return parser


def main() -> int:
    arguments = build_argument_parser().parse_args()

    summary = run_structure_validation(
        project_root=arguments.project_root.resolve(),
        workspace_id=arguments.workspace_id,
        expected_store_count=arguments.expected_store_count,
        expected_upstream_count=arguments.expected_upstream_count,
        deferred_upstream_count=arguments.deferred_upstream_count,
    )

    print()
    print("=" * 68)
    print("PHASE 4.4.1 STRUCTURE VALIDATION COMPLETE")
    print("=" * 68)
    print(
        f"Workspace:                 "
        f"{summary['workspace_id']}"
    )
    print(
        f"Articles discovered:       "
        f"{summary['articles_discovered']}"
    )
    print(
        f"Articles validated:        "
        f"{summary['articles_validated']}"
    )
    print(
        f"Structural PASS:           "
        f"{summary['structural_pass_count']}"
    )
    print(
        f"Structural FAIL:           "
        f"{summary['structural_fail_count']}"
    )
    print(
        f"Deferred upstream pages:   "
        f"{summary['deferred_upstream_count']}"
    )
    print(
        f"Metadata missing:          "
        f"{summary['metadata_missing_count']}"
    )
    print(
        f"Execution status:          "
        f"{summary['execution_status']}"
    )
    print(
        f"Certification status:      "
        f"{summary['certification_status']}"
    )
    print("=" * 68)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
