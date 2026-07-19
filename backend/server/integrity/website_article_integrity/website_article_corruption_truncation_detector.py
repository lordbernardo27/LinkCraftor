"""Website article corruption and truncation detection.

Phase 4.4.3 examines reader-ready HTML documents in the UDARE Store.
It records corruption and truncation evidence without changing the source
article or its metadata.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .website_article_structure_validator import ArticleHTMLParser


VALIDATOR_VERSION = (
    "website_article_corruption_truncation_detector_v1"
)

PHASE = "4.4.3"
PHASE_NAME = "Detect Corruption and Truncation"

DOCTYPE_PATTERN = re.compile(
    r"<!doctype\s+html(?:\s+[^>]*)?>",
    flags=re.IGNORECASE,
)

HTML_CLOSE_PATTERN = re.compile(
    r"</html\s*>",
    flags=re.IGNORECASE,
)

BODY_CLOSE_PATTERN = re.compile(
    r"</body\s*>",
    flags=re.IGNORECASE,
)

HEAD_CLOSE_PATTERN = re.compile(
    r"</head\s*>",
    flags=re.IGNORECASE,
)

FINAL_HTML_CLOSE_PATTERN = re.compile(
    r"</html\s*>\s*$",
    flags=re.IGNORECASE,
)

REPLACEMENT_CHARACTER = "\ufffd"

ALLOWED_CONTROL_CHARACTERS = {
    "\t",
    "\n",
    "\r",
    "\f",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def atomic_write_text(
    path: Path,
    value: str,
) -> None:
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


def load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Invalid JSONL in {path} at line "
                    f"{line_number}: {exc}"
                ) from exc

            if not isinstance(record, dict):
                raise RuntimeError(
                    f"Expected an object in {path} at line "
                    f"{line_number}."
                )

            records.append(record)

    return records


def build_identity_index(
    component_results_path: Path,
) -> dict[str, str]:
    records = load_jsonl(
        component_results_path,
    )

    identity_index: dict[str, str] = {}

    for record in records:
        article_path = record.get("article_path")
        source_record_id = record.get("source_record_id")

        if (
            not isinstance(article_path, str)
            or not article_path
        ):
            continue

        if (
            not isinstance(source_record_id, str)
            or not source_record_id
        ):
            continue

        if article_path in identity_index:
            raise RuntimeError(
                "Duplicate article path in component results: "
                f"{article_path}"
            )

        identity_index[article_path] = source_record_id

    return identity_index


def count_disallowed_control_characters(
    value: str,
) -> int:
    count = 0

    for character in value:
        codepoint = ord(character)

        if (
            codepoint < 32
            and character not in ALLOWED_CONTROL_CHARACTERS
        ):
            count += 1

    return count


def has_incomplete_final_tag(
    value: str,
) -> bool:
    stripped = value.rstrip()

    last_open = stripped.rfind("<")
    last_close = stripped.rfind(">")

    return last_open > last_close


def has_unclosed_comment(
    value: str,
) -> bool:
    return value.count("<!--") != value.count("-->")


def non_whitespace_after_final_html_close(
    value: str,
) -> bool:
    matches = list(
        HTML_CLOSE_PATTERN.finditer(value)
    )

    if not matches:
        return False

    final_match = matches[-1]
    remainder = value[final_match.end():]

    return bool(remainder.strip())


@dataclass(frozen=True)
class CorruptionTruncationResult:
    result_id: str
    validator_version: str
    phase: str
    workspace_id: str
    source_record_id: str
    article_path: str
    article_sha256: str
    file_size_bytes: int
    validated_at: str
    status: str
    corruption_detected: bool
    truncation_detected: bool
    corruption_reasons: list[str]
    truncation_reasons: list[str]
    warning_reasons: list[str]
    checks: dict[str, bool]
    observations: dict[str, Any]


def inspect_article(
    *,
    article_path: Path,
    articles_root: Path,
    workspace_id: str,
    source_record_id: str,
) -> CorruptionTruncationResult:
    raw_bytes = article_path.read_bytes()
    article_hash = sha256_bytes(raw_bytes)

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
        parser_error = (
            f"{type(exc).__name__}: {exc}"
        )

    visible_body_text = parser.visible_body_text

    replacement_character_count = html.count(
        REPLACEMENT_CHARACTER
    )

    null_byte_count = raw_bytes.count(b"\x00")

    control_character_count = (
        count_disallowed_control_characters(html)
    )

    incomplete_final_tag = has_incomplete_final_tag(
        html,
    )

    unclosed_comment = has_unclosed_comment(
        html,
    )

    html_closing_markup_present = bool(
        HTML_CLOSE_PATTERN.search(html)
    )

    body_closing_markup_present = bool(
        BODY_CLOSE_PATTERN.search(html)
    )

    head_closing_markup_present = bool(
        HEAD_CLOSE_PATTERN.search(html)
    )

    file_ends_with_html_close = bool(
        FINAL_HTML_CLOSE_PATTERN.search(html)
    )

    trailing_content_after_html = (
        non_whitespace_after_final_html_close(html)
    )

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

    tiny_incomplete_document = (
        len(raw_bytes) < 256
        and len(visible_body_text) < 40
        and content_block_count == 0
    )

    checks = {
        "file_is_not_empty": len(raw_bytes) > 0,
        "utf8_decodable": utf8_decodable,
        "contains_no_null_bytes": null_byte_count == 0,
        "contains_no_replacement_characters": (
            replacement_character_count == 0
        ),
        "contains_no_disallowed_control_characters": (
            control_character_count == 0
        ),
        "html_parser_completed": parser_error is None,
        "html_root_is_balanced": (
            parser.start_counts["html"] == 1
            and parser.end_counts["html"] == 1
        ),
        "head_is_balanced": (
            parser.start_counts["head"] == 1
            and parser.end_counts["head"] == 1
        ),
        "body_is_balanced": (
            parser.start_counts["body"] == 1
            and parser.end_counts["body"] == 1
        ),
        "head_closing_markup_present": (
            head_closing_markup_present
        ),
        "body_closing_markup_present": (
            body_closing_markup_present
        ),
        "html_closing_markup_present": (
            html_closing_markup_present
        ),
        "final_markup_is_complete": (
            not incomplete_final_tag
        ),
        "html_comment_is_balanced": (
            not unclosed_comment
        ),
        "document_is_not_tiny_and_incomplete": (
            not tiny_incomplete_document
        ),
    }

    corruption_reasons: list[str] = []
    truncation_reasons: list[str] = []
    warning_reasons: list[str] = []

    if not utf8_decodable:
        corruption_reasons.append(
            "utf8_decode_failure"
        )

    if null_byte_count > 0:
        corruption_reasons.append(
            "null_bytes_present"
        )

    if replacement_character_count > 0:
        corruption_reasons.append(
            "replacement_characters_present"
        )

    if control_character_count > 0:
        corruption_reasons.append(
            "disallowed_control_characters_present"
        )

    if parser_error is not None:
        corruption_reasons.append(
            "html_parser_failure"
        )

    if len(raw_bytes) == 0:
        truncation_reasons.append(
            "empty_article_file"
        )

    if parser.start_counts["html"] != 1:
        truncation_reasons.append(
            "invalid_html_open_count"
        )

    if parser.end_counts["html"] != 1:
        truncation_reasons.append(
            "invalid_html_close_count"
        )

    if parser.start_counts["head"] != 1:
        truncation_reasons.append(
            "invalid_head_open_count"
        )

    if parser.end_counts["head"] != 1:
        truncation_reasons.append(
            "invalid_head_close_count"
        )

    if parser.start_counts["body"] != 1:
        truncation_reasons.append(
            "invalid_body_open_count"
        )

    if parser.end_counts["body"] != 1:
        truncation_reasons.append(
            "invalid_body_close_count"
        )

    if not head_closing_markup_present:
        truncation_reasons.append(
            "missing_head_closing_markup"
        )

    if not body_closing_markup_present:
        truncation_reasons.append(
            "missing_body_closing_markup"
        )

    if not html_closing_markup_present:
        truncation_reasons.append(
            "missing_html_closing_markup"
        )

    if incomplete_final_tag:
        truncation_reasons.append(
            "incomplete_markup_at_end_of_file"
        )

    if unclosed_comment:
        truncation_reasons.append(
            "unclosed_html_comment"
        )

    if tiny_incomplete_document:
        truncation_reasons.append(
            "tiny_incomplete_document"
        )

    if not DOCTYPE_PATTERN.search(html):
        warning_reasons.append(
            "doctype_missing"
        )

    if (
        html_closing_markup_present
        and not file_ends_with_html_close
    ):
        warning_reasons.append(
            "document_does_not_end_at_html_close"
        )

    if trailing_content_after_html:
        warning_reasons.append(
            "content_present_after_html_close"
        )

    corruption_detected = bool(
        corruption_reasons
    )

    truncation_detected = bool(
        truncation_reasons
    )

    status = (
        "FAIL"
        if corruption_detected or truncation_detected
        else "PASS"
    )

    article_relative_path = article_path.relative_to(
        articles_root.parent,
    ).as_posix()

    result_seed = (
        f"{workspace_id}|"
        f"{source_record_id}|"
        f"{article_relative_path}|"
        f"{article_hash}"
    )

    result_id = (
        "wai_corruption_truncation_"
        + hashlib.sha256(
            result_seed.encode("utf-8")
        ).hexdigest()[:24]
    )

    observations: dict[str, Any] = {
        "doctype_present": bool(
            DOCTYPE_PATTERN.search(html)
        ),
        "visible_body_text_length": len(
            visible_body_text
        ),
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
        "html_start_count": parser.start_counts["html"],
        "html_end_count": parser.end_counts["html"],
        "head_start_count": parser.start_counts["head"],
        "head_end_count": parser.end_counts["head"],
        "body_start_count": parser.start_counts["body"],
        "body_end_count": parser.end_counts["body"],
        "replacement_character_count": (
            replacement_character_count
        ),
        "null_byte_count": null_byte_count,
        "disallowed_control_character_count": (
            control_character_count
        ),
        "incomplete_final_tag": incomplete_final_tag,
        "unclosed_comment": unclosed_comment,
        "file_ends_with_html_close": (
            file_ends_with_html_close
        ),
        "content_after_html_close": (
            trailing_content_after_html
        ),
        "tiny_incomplete_document": (
            tiny_incomplete_document
        ),
        "parser_error": parser_error,
    }

    return CorruptionTruncationResult(
        result_id=result_id,
        validator_version=VALIDATOR_VERSION,
        phase=PHASE,
        workspace_id=workspace_id,
        source_record_id=source_record_id,
        article_path=article_relative_path,
        article_sha256=article_hash,
        file_size_bytes=len(raw_bytes),
        validated_at=utc_now(),
        status=status,
        corruption_detected=corruption_detected,
        truncation_detected=truncation_detected,
        corruption_reasons=corruption_reasons,
        truncation_reasons=truncation_reasons,
        warning_reasons=warning_reasons,
        checks=checks,
        observations=observations,
    )


def write_jsonl(
    path: Path,
    records: Iterable[CorruptionTruncationResult],
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


def run_corruption_truncation_detection(
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

    udare_root = (
        data_root
        / "udare_store"
        / workspace_id
    )

    articles_root = udare_root / "articles"

    component_results_path = (
        data_root
        / "website_article_integrity"
        / workspace_id
        / "components"
        / "component_results.jsonl"
    )

    if not articles_root.is_dir():
        raise FileNotFoundError(
            f"UDARE article directory missing: {articles_root}"
        )

    if not component_results_path.is_file():
        raise FileNotFoundError(
            "Phase 4.4.2 component results missing: "
            f"{component_results_path}"
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

    identity_index = build_identity_index(
        component_results_path,
    )

    if len(identity_index) != expected_store_count:
        raise RuntimeError(
            "Unexpected component identity count. "
            f"Expected {expected_store_count}, "
            f"found {len(identity_index)}."
        )

    results: list[CorruptionTruncationResult] = []

    unresolved_identity_paths: list[str] = []

    for index, article_path in enumerate(
        article_paths,
        start=1,
    ):
        article_relative_path = article_path.relative_to(
            articles_root.parent,
        ).as_posix()

        source_record_id = identity_index.get(
            article_relative_path,
        )

        if source_record_id is None:
            unresolved_identity_paths.append(
                article_relative_path
            )

            source_record_id = article_path.stem

        results.append(
            inspect_article(
                article_path=article_path,
                articles_root=articles_root,
                workspace_id=workspace_id,
                source_record_id=source_record_id,
            )
        )

        if index % 100 == 0:
            print(
                "Checked corruption and truncation for "
                f"{index} of {len(article_paths)} articles..."
            )

    pass_count = sum(
        result.status == "PASS"
        for result in results
    )

    fail_count = len(results) - pass_count

    corruption_count = sum(
        result.corruption_detected
        for result in results
    )

    truncation_count = sum(
        result.truncation_detected
        for result in results
    )

    warning_count = sum(
        bool(result.warning_reasons)
        for result in results
    )

    corruption_reason_counts: Counter[str] = Counter()
    truncation_reason_counts: Counter[str] = Counter()
    warning_reason_counts: Counter[str] = Counter()

    for result in results:
        corruption_reason_counts.update(
            result.corruption_reasons
        )

        truncation_reason_counts.update(
            result.truncation_reasons
        )

        warning_reason_counts.update(
            result.warning_reasons
        )

    output_root = (
        data_root
        / "website_article_integrity"
        / workspace_id
        / "corruption_truncation"
    )

    results_path = (
        output_root
        / "corruption_truncation_results.jsonl"
    )

    summary_path = (
        output_root
        / "corruption_truncation_summary.json"
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
        "articles_checked": len(results),
        "integrity_pass_count": pass_count,
        "integrity_fail_count": fail_count,
        "corruption_detected_count": corruption_count,
        "truncation_detected_count": truncation_count,
        "warning_article_count": warning_count,
        "identity_reference_count": len(identity_index),
        "identity_unresolved_count": len(
            unresolved_identity_paths
        ),
        "identity_unresolved_paths": (
            unresolved_identity_paths
        ),
        "corruption_reason_counts": dict(
            sorted(corruption_reason_counts.items())
        ),
        "truncation_reason_counts": dict(
            sorted(truncation_reason_counts.items())
        ),
        "warning_reason_counts": dict(
            sorted(warning_reason_counts.items())
        ),
        "results_path": str(results_path),
        "important_notes": [
            (
                "The three upstream pages absent from the UDARE "
                "Store remain deferred."
            ),
            (
                "Warnings do not cause an article to fail unless "
                "corruption or truncation evidence is also present."
            ),
            (
                "No UDARE article or metadata record was modified, "
                "deleted, repaired, or quarantined."
            ),
        ],
    }

    atomic_write_json(
        summary_path,
        summary,
    )

    return summary
