"""Required-component validation for reconstructed website articles.

Phase 4.4.2 validates the required components of every reader-ready HTML
article stored in the UDARE Store.

The validator is read-only with respect to the UDARE Store.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .website_article_structure_validator import ArticleHTMLParser


VALIDATOR_VERSION = "website_article_component_validator_v1"
PHASE = "4.4.2"
PHASE_NAME = "Validate Required Article Components"

RAW_HTML_ID_PATTERN = re.compile(
    r"raw_html_([0-9a-fA-F]{8,64})",
)

ARTICLE_SUFFIX_PATTERN = re.compile(
    r"_([0-9a-fA-F]{8,64})$",
)

SOURCE_ID_KEYS = {
    "source_record_id",
    "raw_html_id",
    "record_id",
    "source_id",
    "page_id",
    "document_id",
    "id",
}

SOURCE_URL_KEYS = {
    "source_url",
    "canonical_url",
    "url",
    "page_url",
    "requested_url",
    "final_url",
    "resolved_url",
}

ARTICLE_PATH_KEYS = {
    "article_path",
    "article_document_path",
    "html_path",
    "document_path",
    "relative_path",
    "article_filename",
    "filename",
}

TITLE_KEYS = {
    "title",
    "article_title",
    "page_title",
    "headline",
    "h1",
}

WORKSPACE_KEYS = {
    "workspace_id",
    "workspace",
}

SKIPPED_BODY_KEYS = {
    "html",
    "raw_html",
    "raw_html_content",
    "html_content",
    "page_html",
    "article_body",
    "content_body",
    "body",
    "body_text",
    "article_text",
    "markup",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalize_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    value = value.strip()

    if value.lower().startswith(("http://", "https://")):
        return value

    return None


def atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )

    temporary_path = Path(temporary_name)

    try:
        with os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(
            temporary_path,
            path,
        )
    finally:
        temporary_path.unlink(
            missing_ok=True,
        )


def atomic_write_json(
    path: Path,
    value: dict[str, Any],
) -> None:
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


def iter_named_values(
    value: Any,
    *,
    wanted_keys: set[str],
) -> Iterable[Any]:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()

            if key_text in wanted_keys:
                yield child

            if key_text in SKIPPED_BODY_KEYS:
                continue

            yield from iter_named_values(
                child,
                wanted_keys=wanted_keys,
            )

    elif isinstance(value, list):
        for child in value:
            yield from iter_named_values(
                child,
                wanted_keys=wanted_keys,
            )


def first_non_empty_string(
    value: Any,
    *,
    wanted_keys: set[str],
) -> str | None:
    for candidate in iter_named_values(
        value,
        wanted_keys=wanted_keys,
    ):
        if isinstance(candidate, str):
            candidate = candidate.strip()

            if candidate:
                return candidate

    return None


def first_url(
    value: Any,
) -> str | None:
    for candidate in iter_named_values(
        value,
        wanted_keys=SOURCE_URL_KEYS,
    ):
        normalized = normalize_url(candidate)

        if normalized:
            return normalized

    return None


def collect_article_path_values(
    value: Any,
) -> list[str]:
    paths: list[str] = []

    for candidate in iter_named_values(
        value,
        wanted_keys=ARTICLE_PATH_KEYS,
    ):
        if isinstance(candidate, str):
            candidate = candidate.strip()

            if candidate:
                paths.append(candidate.replace("\\", "/"))

    return paths


def extract_raw_hash_from_filename(
    path: Path,
) -> str | None:
    match = RAW_HTML_ID_PATTERN.search(
        path.stem,
    )

    if match is None:
        return None

    return match.group(1).lower()


def extract_article_suffix_hash(
    article_path: Path,
) -> str | None:
    match = ARTICLE_SUFFIX_PATTERN.search(
        article_path.stem,
    )

    if match is None:
        return None

    return match.group(1).lower()


@dataclass(frozen=True)
class MetadataEntry:
    metadata_path: Path
    raw_hash: str | None
    source_record_id: str | None
    source_url: str | None
    metadata_title: str | None
    workspace_id: str | None
    article_path_values: list[str]


@dataclass(frozen=True)
class ComponentValidationResult:
    result_id: str
    validator_version: str
    phase: str
    workspace_id: str
    source_record_id: str
    article_path: str
    metadata_path: str | None
    article_sha256: str
    validated_at: str
    status: str
    failure_reasons: list[str]
    checks: dict[str, bool]
    observations: dict[str, Any]


def build_metadata_entries(
    metadata_root: Path,
) -> list[MetadataEntry]:
    entries: list[MetadataEntry] = []

    metadata_paths = sorted(
        path
        for path in metadata_root.glob("*.json")
        if path.is_file()
    )

    for metadata_path in metadata_paths:
        try:
            metadata = json.loads(
                metadata_path.read_text(
                    encoding="utf-8-sig",
                )
            )
        except (OSError, json.JSONDecodeError):
            continue

        raw_hash = extract_raw_hash_from_filename(
            metadata_path,
        )

        source_record_id = first_non_empty_string(
            metadata,
            wanted_keys=SOURCE_ID_KEYS,
        )

        if source_record_id is None and raw_hash:
            source_record_id = f"raw_html_{raw_hash}"

        entries.append(
            MetadataEntry(
                metadata_path=metadata_path,
                raw_hash=raw_hash,
                source_record_id=source_record_id,
                source_url=first_url(metadata),
                metadata_title=first_non_empty_string(
                    metadata,
                    wanted_keys=TITLE_KEYS,
                ),
                workspace_id=first_non_empty_string(
                    metadata,
                    wanted_keys=WORKSPACE_KEYS,
                ),
                article_path_values=collect_article_path_values(
                    metadata,
                ),
            )
        )

    return entries


class MetadataResolver:
    def __init__(
        self,
        entries: list[MetadataEntry],
    ) -> None:
        self.entries = entries

        self.by_article_filename: dict[
            str,
            list[MetadataEntry],
        ] = defaultdict(list)

        self.by_article_stem: dict[
            str,
            list[MetadataEntry],
        ] = defaultdict(list)

        self.by_hash_prefix: dict[
            str,
            list[MetadataEntry],
        ] = defaultdict(list)

        for entry in entries:
            if entry.raw_hash:
                for prefix_length in range(
                    8,
                    min(len(entry.raw_hash), 32) + 1,
                ):
                    prefix = entry.raw_hash[:prefix_length]
                    self.by_hash_prefix[prefix].append(entry)

            for article_path_value in entry.article_path_values:
                article_name = Path(
                    article_path_value,
                ).name.lower()

                article_stem = Path(
                    article_path_value,
                ).stem.lower()

                if article_name:
                    self.by_article_filename[
                        article_name
                    ].append(entry)

                if article_stem:
                    self.by_article_stem[
                        article_stem
                    ].append(entry)

    def resolve(
        self,
        article_path: Path,
    ) -> tuple[MetadataEntry | None, str, int]:
        article_filename = article_path.name.lower()
        article_stem = article_path.stem.lower()

        filename_matches = self.by_article_filename.get(
            article_filename,
            [],
        )

        if len(filename_matches) == 1:
            return filename_matches[0], "article_filename", 1

        stem_matches = self.by_article_stem.get(
            article_stem,
            [],
        )

        if len(stem_matches) == 1:
            return stem_matches[0], "article_stem", 1

        article_hash = extract_article_suffix_hash(
            article_path,
        )

        if article_hash:
            hash_matches = self.by_hash_prefix.get(
                article_hash,
                [],
            )

            unique_matches = {
                entry.metadata_path: entry
                for entry in hash_matches
            }

            if len(unique_matches) == 1:
                return (
                    next(iter(unique_matches.values())),
                    "raw_hash_prefix",
                    1,
                )

            if len(unique_matches) > 1:
                return (
                    None,
                    "ambiguous_raw_hash_prefix",
                    len(unique_matches),
                )

        return None, "unresolved", 0


def validate_required_components(
    *,
    article_path: Path,
    articles_root: Path,
    metadata_root: Path,
    workspace_id: str,
    resolver: MetadataResolver,
) -> ComponentValidationResult:
    raw_bytes = article_path.read_bytes()

    try:
        html = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
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

    metadata_entry, resolution_method, match_count = (
        resolver.resolve(article_path)
    )

    metadata_exists = metadata_entry is not None

    document_title = parser.title_text
    body_text = parser.visible_body_text

    content_block_count = sum(
        parser.start_counts[tag]
        for tag in (
            "p",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "li",
            "blockquote",
            "pre",
            "table",
            "figure",
        )
    )

    source_identity = (
        metadata_entry.source_record_id
        if metadata_entry is not None
        else None
    )

    source_url = (
        metadata_entry.source_url
        if metadata_entry is not None
        else None
    )

    checks = {
        "metadata_record_resolved": metadata_exists,
        "metadata_match_is_unambiguous": (
            metadata_exists and match_count == 1
        ),
        "source_identity_present": bool(source_identity),
        "source_url_present": bool(source_url),
        "document_title_present": bool(document_title),
        "article_body_present": bool(body_text),
        "content_block_present": content_block_count > 0,
        "parser_completed": parser_error is None,
    }

    failure_reasons = [
        check_name
        for check_name, passed in checks.items()
        if not passed
    ]

    status = (
        "PASS"
        if not failure_reasons
        else "FAIL"
    )

    article_hash = sha256_bytes(raw_bytes)
    article_relative_path = article_path.relative_to(
        articles_root.parent,
    ).as_posix()

    source_record_id = (
        source_identity
        or article_path.stem
    )

    result_seed = (
        f"{workspace_id}|"
        f"{source_record_id}|"
        f"{article_relative_path}|"
        f"{article_hash}"
    )

    result_id = (
        "wai_components_"
        + hashlib.sha256(
            result_seed.encode("utf-8")
        ).hexdigest()[:24]
    )

    metadata_relative_path: str | None = None

    if metadata_entry is not None:
        metadata_relative_path = (
            metadata_entry.metadata_path.relative_to(
                metadata_root.parent,
            ).as_posix()
        )

    observations: dict[str, Any] = {
        "metadata_resolution_method": resolution_method,
        "metadata_match_count": match_count,
        "document_title": document_title,
        "document_title_length": len(document_title),
        "visible_body_text_length": len(body_text),
        "content_block_count": content_block_count,
        "paragraph_count": parser.start_counts["p"],
        "heading_count": sum(
            parser.start_counts[tag]
            for tag in (
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
            )
        ),
        "list_item_count": parser.start_counts["li"],
        "source_identity": source_identity,
        "source_url": source_url,
        "metadata_title": (
            metadata_entry.metadata_title
            if metadata_entry is not None
            else None
        ),
        "metadata_workspace_id": (
            metadata_entry.workspace_id
            if metadata_entry is not None
            else None
        ),
        "parser_error": parser_error,
    }

    return ComponentValidationResult(
        result_id=result_id,
        validator_version=VALIDATOR_VERSION,
        phase=PHASE,
        workspace_id=workspace_id,
        source_record_id=source_record_id,
        article_path=article_relative_path,
        metadata_path=metadata_relative_path,
        article_sha256=article_hash,
        validated_at=utc_now(),
        status=status,
        failure_reasons=failure_reasons,
        checks=checks,
        observations=observations,
    )


def write_jsonl(
    path: Path,
    records: Iterable[ComponentValidationResult],
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


def run_component_validation(
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

    articles_root = (
        udare_workspace_root
        / "articles"
    )

    metadata_root = (
        udare_workspace_root
        / "metadata"
    )

    if not articles_root.is_dir():
        raise FileNotFoundError(
            f"UDARE article directory missing: {articles_root}"
        )

    if not metadata_root.is_dir():
        raise FileNotFoundError(
            f"UDARE metadata directory missing: {metadata_root}"
        )

    article_paths = sorted(
        path
        for path in articles_root.rglob("*.html")
        if path.is_file()
    )

    metadata_entries = build_metadata_entries(
        metadata_root,
    )

    if len(article_paths) != expected_store_count:
        raise RuntimeError(
            "Unexpected article count. "
            f"Expected {expected_store_count}, "
            f"found {len(article_paths)}."
        )

    if len(metadata_entries) != expected_store_count:
        raise RuntimeError(
            "Unexpected metadata count. "
            f"Expected {expected_store_count}, "
            f"found {len(metadata_entries)}."
        )

    resolver = MetadataResolver(
        metadata_entries,
    )

    results: list[ComponentValidationResult] = []

    for index, article_path in enumerate(
        article_paths,
        start=1,
    ):
        results.append(
            validate_required_components(
                article_path=article_path,
                articles_root=articles_root,
                metadata_root=metadata_root,
                workspace_id=workspace_id,
                resolver=resolver,
            )
        )

        if index % 100 == 0:
            print(
                f"Validated components for {index} of "
                f"{len(article_paths)} articles..."
            )

    pass_count = sum(
        result.status == "PASS"
        for result in results
    )

    fail_count = len(results) - pass_count

    metadata_resolved_count = sum(
        result.checks["metadata_record_resolved"]
        for result in results
    )

    metadata_unresolved_count = (
        len(results) - metadata_resolved_count
    )

    failure_reason_counts: Counter[str] = Counter()

    resolution_method_counts: Counter[str] = Counter()

    for result in results:
        failure_reason_counts.update(
            result.failure_reasons
        )

        resolution_method_counts.update(
            [
                result.observations[
                    "metadata_resolution_method"
                ]
            ]
        )

    output_root = (
        data_root
        / "website_article_integrity"
        / workspace_id
        / "components"
    )

    results_path = (
        output_root
        / "component_results.jsonl"
    )

    summary_path = (
        output_root
        / "component_summary.json"
    )

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
        "expected_upstream_count": expected_upstream_count,
        "deferred_upstream_count": deferred_upstream_count,
        "expected_store_count": expected_store_count,
        "articles_discovered": len(article_paths),
        "metadata_records_discovered": len(metadata_entries),
        "articles_validated": len(results),
        "component_pass_count": pass_count,
        "component_fail_count": fail_count,
        "metadata_resolved_count": metadata_resolved_count,
        "metadata_unresolved_count": metadata_unresolved_count,
        "all_stored_articles_validated": (
            len(results) == expected_store_count
        ),
        "all_metadata_records_resolved": (
            metadata_unresolved_count == 0
        ),
        "failure_reason_counts": dict(
            sorted(
                failure_reason_counts.items()
            )
        ),
        "metadata_resolution_method_counts": dict(
            sorted(
                resolution_method_counts.items()
            )
        ),
        "results_path": str(results_path),
        "important_notes": [
            (
                "The three upstream pages absent from the UDARE "
                "Store remain deferred."
            ),
            (
                "This validation did not modify, delete, repair, "
                "or quarantine any UDARE article."
            ),
            (
                "Metadata was resolved through stored article paths "
                "or the raw HTML identity hash embedded in filenames."
            ),
        ],
    }

    atomic_write_json(
        summary_path,
        summary,
    )

    return summary
