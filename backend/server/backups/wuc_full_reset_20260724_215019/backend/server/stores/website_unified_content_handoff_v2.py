"""Canonical Article Validation PASS-manifest to transient WUC handoff."""

from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Mapping


HANDOFF_VERSION = (
    "website_unified_content_handoff_v2_"
    "article_validation_pass_udare_reference"
)

PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

EXPECTED_CERTIFICATE_STATUS = "CERTIFIED"


class WebsiteUnifiedContentHandoffError(
    RuntimeError
):
    """Raised when the Article Validation-to-WUC contract is invalid."""


class _ReaderArticleParser(
    HTMLParser
):
    BLOCK_TAGS = {
        "p",
        "li",
        "blockquote",
        "figcaption",
        "dd",
        "dt",
        "td",
        "th",
        "pre",
    }

    HEADING_TAGS = {
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }

    IGNORED_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "template",
    }

    def __init__(
        self,
    ) -> None:
        super().__init__(
            convert_charrefs=True,
        )

        self._ignored_depth = 0
        self._capture_stack: list[
            dict[str, Any]
        ] = []

        self.blocks: list[
            dict[str, Any]
        ] = []

        self.headings: list[str] = []
        self.h1 = ""
        self.title = ""
        self._inside_title = False
        self._title_parts: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[
            tuple[str, str | None]
        ],
    ) -> None:
        normalized = tag.casefold()

        if normalized in self.IGNORED_TAGS:
            self._ignored_depth += 1
            return

        if self._ignored_depth:
            return

        if normalized == "title":
            self._inside_title = True
            self._title_parts = []
            return

        if (
            normalized in self.BLOCK_TAGS
            or normalized in self.HEADING_TAGS
        ):
            self._capture_stack.append(
                {
                    "tag":
                        normalized,

                    "parts":
                        [],
                }
            )

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        normalized = tag.casefold()

        if normalized in self.IGNORED_TAGS:
            if self._ignored_depth:
                self._ignored_depth -= 1
            return

        if self._ignored_depth:
            return

        if normalized == "title":
            self._inside_title = False

            value = _normalize_text(
                " ".join(
                    self._title_parts
                )
            )

            if value:
                self.title = value

            return

        for index in range(
            len(
                self._capture_stack
            )
            - 1,
            -1,
            -1,
        ):
            capture = self._capture_stack[
                index
            ]

            if capture[
                "tag"
            ] != normalized:
                continue

            self._capture_stack.pop(
                index
            )

            value = _normalize_text(
                " ".join(
                    capture[
                        "parts"
                    ]
                )
            )

            if not value:
                return

            block = {
                "block_index":
                    len(
                        self.blocks
                    ),

                "block_type":
                    (
                        "heading"
                        if normalized
                        in self.HEADING_TAGS
                        else normalized
                    ),

                "tag":
                    normalized,

                "text":
                    value,
            }

            self.blocks.append(
                block
            )

            if normalized in self.HEADING_TAGS:
                self.headings.append(
                    value
                )

                if (
                    normalized == "h1"
                    and not self.h1
                ):
                    self.h1 = value

            return

    def handle_data(
        self,
        data: str,
    ) -> None:
        if self._ignored_depth:
            return

        if self._inside_title:
            self._title_parts.append(
                data
            )

        for capture in self._capture_stack:
            capture[
                "parts"
            ].append(
                data
            )


def _normalize_text(
    value: Any,
) -> str:
    return re.sub(
        r"\s+",
        " ",
        str(
            value or ""
        ),
    ).strip()


def _safe_workspace_id(
    value: Any,
) -> str:
    workspace_id = _normalize_text(
        value
    )

    if not workspace_id:
        raise WebsiteUnifiedContentHandoffError(
            "workspace_id is required."
        )

    if not re.fullmatch(
        r"[A-Za-z0-9_.:-]+",
        workspace_id,
    ):
        raise WebsiteUnifiedContentHandoffError(
            "workspace_id contains unsupported characters."
        )

    return workspace_id


def _load_json(
    path: Path,
) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8-sig",
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise WebsiteUnifiedContentHandoffError(
            f"Expected JSON object: {path}"
        )

    return value


def _load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    records: list[
        dict[str, Any]
    ] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            stripped = line.strip()

            if not stripped:
                continue

            try:
                value = json.loads(
                    stripped
                )

            except json.JSONDecodeError as exc:
                raise WebsiteUnifiedContentHandoffError(
                    f"Invalid JSONL: {path}:{line_number}"
                ) from exc

            if not isinstance(
                value,
                dict,
            ):
                raise WebsiteUnifiedContentHandoffError(
                    f"Expected JSON object: {path}:{line_number}"
                )

            records.append(
                value
            )

    return records


def _resolve_reference(
    value: Any,
) -> Path:
    raw = _normalize_text(
        value
    )

    if not raw:
        raise WebsiteUnifiedContentHandoffError(
            "A required file reference is empty."
        )

    path = Path(
        raw
    )

    if not path.is_absolute():
        path = (
            PROJECT_ROOT
            / path
        )

    return path.resolve()


def _sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                block
            )

    return digest.hexdigest()


def _population_report_path(
    workspace_id: str,
) -> Path:
    return (
        DATA_ROOT
        / "article_validation_scan"
        / workspace_id
        / "article_validation_population_v3_verification.json"
    )


def _evidence_root(
    workspace_id: str,
) -> Path:
    return (
        DATA_ROOT
        / "article_validation_evidence"
        / workspace_id
    )


def _udare_articles_root(
    workspace_id: str,
) -> Path:
    return (
        DATA_ROOT
        / "udare_store"
        / workspace_id
        / "articles"
    ).resolve()


def _find_manifest_from_report(
    *,
    workspace_id: str,
    report: Mapping[str, Any],
) -> Path:
    artifact_paths = report.get(
        "artifact_paths"
    )

    mappings: list[
        Mapping[str, Any]
    ] = []

    if isinstance(
        artifact_paths,
        Mapping,
    ):
        mappings.append(
            artifact_paths
        )

    mappings.append(
        report
    )

    for mapping in mappings:
        for key in (
            "pass_manifest",
            "article_validation_pass_manifest",
            "pass_manifest_path",
            "article_validation_pass_manifest_path",
        ):
            value = mapping.get(
                key
            )

            if not value:
                continue

            path = _resolve_reference(
                value
            )

            if path.is_file():
                return path

    run_id = _normalize_text(
        report.get(
            "run_id"
        )
    )

    roots: list[Path] = []

    if run_id:
        roots.append(
            _evidence_root(
                workspace_id
            )
            / "runs"
            / run_id
        )

    roots.append(
        _evidence_root(
            workspace_id
        )
    )

    candidates: list[Path] = []

    for root in roots:
        if not root.is_dir():
            continue

        candidates.extend(
            path.resolve()
            for path in root.rglob(
                "article_validation_pass_manifest.jsonl"
            )
            if path.is_file()
        )

    if not candidates:
        raise WebsiteUnifiedContentHandoffError(
            "Article Validation PASS manifest was not found."
        )

    return max(
        candidates,
        key=lambda path: (
            path.stat().st_mtime
        ),
    )


def load_article_validation_pass_contract_v2(
    workspace_id: str,
) -> dict[str, Any]:
    normalized_workspace_id = (
        _safe_workspace_id(
            workspace_id
        )
    )

    report_path = _population_report_path(
        normalized_workspace_id
    )

    if not report_path.is_file():
        raise WebsiteUnifiedContentHandoffError(
            "Authoritative Article Validation report is missing: "
            + str(
                report_path
            )
        )

    report = _load_json(
        report_path
    )

    verification_status = _normalize_text(
        report.get(
            "verification_status"
        )
    ).upper()

    certificate_status = _normalize_text(
        report.get(
            "certificate_status"
        )
        or report.get(
            "status"
        )
        or EXPECTED_CERTIFICATE_STATUS
    ).upper()

    pass_count = int(
        report.get(
            "pass_count"
        )
        or report.get(
            "article_validation_pass_count"
        )
        or 0
    )

    fail_count = int(
        report.get(
            "fail_count"
        )
        or report.get(
            "article_validation_fail_count"
        )
        or 0
    )

    if verification_status != "PASS":
        raise WebsiteUnifiedContentHandoffError(
            "Article Validation verification status is not PASS."
        )

    if certificate_status != EXPECTED_CERTIFICATE_STATUS:
        raise WebsiteUnifiedContentHandoffError(
            "Article Validation certificate is not CERTIFIED."
        )

    if pass_count <= 0:
        raise WebsiteUnifiedContentHandoffError(
            "Article Validation PASS count is empty."
        )

    if fail_count != 0:
        raise WebsiteUnifiedContentHandoffError(
            "Article Validation has unresolved failures."
        )

    manifest_path = _find_manifest_from_report(
        workspace_id=(
            normalized_workspace_id
        ),
        report=report,
    )

    records = _load_jsonl(
        manifest_path
    )

    if len(
        records
    ) != pass_count:
        raise WebsiteUnifiedContentHandoffError(
            "PASS-manifest count does not match the "
            "authoritative Article Validation report."
        )

    return {
        "workspace_id":
            normalized_workspace_id,

        "run_id":
            report.get(
                "run_id"
            ),

        "certificate_id":
            report.get(
                "certificate_id"
            ),

        "certificate_status":
            certificate_status,

        "pass_count":
            pass_count,

        "fail_count":
            fail_count,

        "population_report_path":
            str(
                report_path
            ),

        "pass_manifest_path":
            str(
                manifest_path
            ),

        "records":
            records,
    }


def _record_aliases(
    record: Mapping[str, Any],
) -> set[str]:
    aliases: set[str] = set()

    for field in (
        "source_record_id",
        "html_id",
        "article_id",
        "document_id",
        "content_id",
    ):
        value = _normalize_text(
            record.get(
                field
            )
        )

        if value:
            aliases.add(
                value
            )

    return aliases


def select_article_validation_pass_records_v2(
    *,
    contract: Mapping[str, Any],
    assigned_article_ids: Iterable[str] | None,
) -> list[dict[str, Any]]:
    records = contract.get(
        "records"
    )

    if not isinstance(
        records,
        list,
    ):
        raise WebsiteUnifiedContentHandoffError(
            "Article Validation PASS records are invalid."
        )

    if assigned_article_ids is None:
        return [
            dict(
                record
            )
            for record in records
            if isinstance(
                record,
                Mapping,
            )
        ]

    requested = {
        _normalize_text(
            value
        )
        for value in assigned_article_ids
        if _normalize_text(
            value
        )
    }

    if not requested:
        return []

    selected: list[
        dict[str, Any]
    ] = []

    found: set[str] = set()

    for record in records:
        if not isinstance(
            record,
            Mapping,
        ):
            continue

        aliases = _record_aliases(
            record
        )

        matches = aliases.intersection(
            requested
        )

        if not matches:
            continue

        selected.append(
            dict(
                record
            )
        )

        found.update(
            matches
        )

    missing = sorted(
        requested
        - found
    )

    if missing:
        raise WebsiteUnifiedContentHandoffError(
            "Assigned Article Validation PASS records "
            "were not found: "
            + ", ".join(
                missing[:20]
            )
        )

    return selected


def load_transient_wuc_source_v2(
    *,
    workspace_id: str,
    pass_record: Mapping[str, Any],
    article_validation_contract: Mapping[str, Any],
) -> dict[str, Any]:
    normalized_workspace_id = (
        _safe_workspace_id(
            workspace_id
        )
    )

    reference_value = None

    for field in (
        "article_reference",
        "article_path",
        "source_article_path",
        "udare_article_path",
        "content_ref",
    ):
        value = pass_record.get(
            field
        )

        if value:
            reference_value = value
            break

    if not reference_value:
        raise WebsiteUnifiedContentHandoffError(
            "PASS record has no UDARE article reference."
        )

    article_path = _resolve_reference(
        reference_value
    )

    try:
        article_path.relative_to(
            _udare_articles_root(
                normalized_workspace_id
            )
        )

    except ValueError as exc:
        raise WebsiteUnifiedContentHandoffError(
            "PASS record points outside the UDARE article directory."
        ) from exc

    if not article_path.is_file():
        raise WebsiteUnifiedContentHandoffError(
            "Referenced UDARE article does not exist: "
            + str(
                article_path
            )
        )

    expected_hash = _normalize_text(
        pass_record.get(
            "article_sha256"
        )
        or pass_record.get(
            "article_hash"
        )
        or pass_record.get(
            "content_hash"
        )
    ).lower()

    actual_hash = _sha256_file(
        article_path
    )

    if (
        expected_hash
        and expected_hash != actual_hash
    ):
        raise WebsiteUnifiedContentHandoffError(
            "Referenced UDARE article hash does not match "
            "Article Validation evidence."
        )

    metadata: dict[str, Any] = {}

    metadata_value = pass_record.get(
        "metadata_path"
    )

    if metadata_value:
        metadata_path = _resolve_reference(
            metadata_value
        )

        if metadata_path.is_file():
            metadata = _load_json(
                metadata_path
            )

            expected_metadata_hash = (
                _normalize_text(
                    pass_record.get(
                        "metadata_sha256"
                    )
                ).lower()
            )

            if (
                expected_metadata_hash
                and _sha256_file(
                    metadata_path
                )
                != expected_metadata_hash
            ):
                raise WebsiteUnifiedContentHandoffError(
                    "UDARE metadata hash does not match "
                    "Article Validation evidence."
                )

    html = article_path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    parser = _ReaderArticleParser()
    parser.feed(
        html
    )
    parser.close()

    ordered_text_blocks = [
        block[
            "text"
        ]
        for block in parser.blocks
        if (
            block[
                "block_type"
            ]
            != "heading"
        )
    ]

    if not ordered_text_blocks:
        ordered_text_blocks = [
            block[
                "text"
            ]
            for block in parser.blocks
        ]

    content_body = "\n\n".join(
        ordered_text_blocks
    ).strip()

    if not content_body:
        raise WebsiteUnifiedContentHandoffError(
            "Referenced UDARE article produced an empty content body."
        )

    source_record_id = _normalize_text(
        pass_record.get(
            "source_record_id"
        )
        or pass_record.get(
            "html_id"
        )
        or pass_record.get(
            "document_id"
        )
    )

    if not source_record_id:
        raise WebsiteUnifiedContentHandoffError(
            "PASS record has no stable source identifier."
        )

    title = _normalize_text(
        pass_record.get(
            "title"
        )
        or pass_record.get(
            "display_title"
        )
        or metadata.get(
            "title"
        )
        or parser.title
        or parser.h1
    )

    h1 = _normalize_text(
        pass_record.get(
            "h1"
        )
        or metadata.get(
            "h1"
        )
        or parser.h1
        or title
    )

    canonical_url = _normalize_text(
        pass_record.get(
            "canonical_url"
        )
        or pass_record.get(
            "source_url"
        )
        or pass_record.get(
            "url"
        )
        or metadata.get(
            "canonical_url"
        )
        or metadata.get(
            "source_url"
        )
        or metadata.get(
            "url"
        )
    )

    headings = list(
        dict.fromkeys(
            parser.headings
        )
    )

    return {
        "content_id":
            (
                "web_content_"
                + source_record_id.removeprefix(
                    "raw_html_"
                )
            ),

        "document_id":
            source_record_id,

        "workspace_id":
            normalized_workspace_id,

        "html_id":
            source_record_id,

        "source_record_id":
            source_record_id,

        "url":
            canonical_url,

        "canonical_url":
            canonical_url,

        "title":
            title,

        "h1":
            h1,

        "headings":
            headings,

        "content_body":
            content_body,

        "structure": {
            "block_count":
                len(
                    parser.blocks
                ),

            "heading_count":
                len(
                    headings
                ),

            "blocks":
                parser.blocks,
        },

        "metadata": {
            **metadata,

            "wuc_handoff_version":
                HANDOFF_VERSION,

            "source_stage":
                "article_validation",

            "source_pipeline":
                "udare_integrity_article_validation",

            "udare_article_path":
                str(
                    article_path
                ),

            "udare_article_sha256":
                actual_hash,

            "article_validation_run_id":
                article_validation_contract.get(
                    "run_id"
                ),

            "article_validation_certificate_id":
                article_validation_contract.get(
                    "certificate_id"
                ),

            "article_validation_pass_manifest":
                article_validation_contract.get(
                    "pass_manifest_path"
                ),

            "article_validation_source_record_id":
                source_record_id,

            "body_loaded_transiently":
                True,

            "intermediate_wuc_store_created":
                False,
        },

        "quality": {
            "article_validation_status":
                "PASS",

            "integrity_verified":
                True,

            "hash_verified":
                True,
        },

        "semantic_features": {
            "semantic_ready":
                True,

            "source_type":
                "website",
        },
    }
