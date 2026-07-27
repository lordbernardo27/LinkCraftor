"""Certified Article Validation input reader for fresh WUC."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping


INPUT_CONTRACT_VERSION = (
    "certified_wuc_input_v1_"
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


class CertifiedWucInputError(
    RuntimeError
):
    """Raised when certified WUC input evidence is invalid."""


def _safe_workspace_id(
    value: Any,
) -> str:
    workspace_id = str(
        value or ""
    ).strip()

    if not workspace_id:
        raise CertifiedWucInputError(
            "workspace_id is required."
        )

    if not re.fullmatch(
        r"[A-Za-z0-9_.:-]+",
        workspace_id,
    ):
        raise CertifiedWucInputError(
            "workspace_id contains unsupported characters."
        )

    return workspace_id


def _load_json(
    path: Path,
) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(
                encoding="utf-8-sig",
            )
        )

    except (
        OSError,
        json.JSONDecodeError,
    ) as exc:
        raise CertifiedWucInputError(
            f"Could not read JSON object: {path}"
        ) from exc

    if not isinstance(
        value,
        dict,
    ):
        raise CertifiedWucInputError(
            f"Expected JSON object: {path}"
        )

    return value


def _load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    records: list[
        dict[str, Any]
    ] = []

    try:
        handle = path.open(
            "r",
            encoding="utf-8-sig",
        )

    except OSError as exc:
        raise CertifiedWucInputError(
            f"Could not open JSONL file: {path}"
        ) from exc

    with handle:
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
                raise CertifiedWucInputError(
                    f"Invalid JSONL at {path}:{line_number}"
                ) from exc

            if not isinstance(
                value,
                dict,
            ):
                raise CertifiedWucInputError(
                    f"Expected object at {path}:{line_number}"
                )

            records.append(
                value
            )

    return records


def _resolve_reference(
    value: Any,
) -> Path:
    raw = str(
        value or ""
    ).strip()

    if not raw:
        raise CertifiedWucInputError(
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


def _authoritative_report_path(
    workspace_id: str,
) -> Path:
    return (
        DATA_ROOT
        / "article_validation_scan"
        / workspace_id
        / "article_validation_population_v3_verification.json"
    )


def _article_validation_evidence_root(
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


def _manifest_from_report(
    *,
    workspace_id: str,
    report: Mapping[str, Any],
) -> Path:
    mappings: list[
        Mapping[str, Any]
    ] = []

    artifact_paths = report.get(
        "artifact_paths"
    )

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

    run_id = str(
        report.get(
            "run_id"
        )
        or ""
    ).strip()

    roots: list[Path] = []

    if run_id:
        roots.append(
            _article_validation_evidence_root(
                workspace_id
            )
            / "runs"
            / run_id
        )

    roots.append(
        _article_validation_evidence_root(
            workspace_id
        )
    )

    candidates: list[
        Path
    ] = []

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
        raise CertifiedWucInputError(
            "Article Validation PASS manifest was not found."
        )

    return max(
        candidates,
        key=lambda path: (
            path.stat().st_mtime
        ),
    )


def load_article_validation_pass_contract_v1(
    workspace_id: str,
    *,
    expected_pass_count: int | None = None,
) -> dict[str, Any]:
    normalized_workspace_id = (
        _safe_workspace_id(
            workspace_id
        )
    )

    report_path = _authoritative_report_path(
        normalized_workspace_id
    )

    if not report_path.is_file():
        raise CertifiedWucInputError(
            "Authoritative Article Validation report is missing: "
            + str(
                report_path
            )
        )

    report = _load_json(
        report_path
    )

    verification_status = str(
        report.get(
            "verification_status"
        )
        or ""
    ).strip().upper()

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
        raise CertifiedWucInputError(
            "Article Validation verification is not PASS."
        )

    if pass_count <= 0:
        raise CertifiedWucInputError(
            "Article Validation PASS count is empty."
        )

    if fail_count != 0:
        raise CertifiedWucInputError(
            "Article Validation contains unresolved failures."
        )

    if (
        expected_pass_count is not None
        and pass_count
        != int(
            expected_pass_count
        )
    ):
        raise CertifiedWucInputError(
            "Article Validation PASS count mismatch: "
            f"{pass_count} != {expected_pass_count}"
        )

    manifest_path = _manifest_from_report(
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
        raise CertifiedWucInputError(
            "PASS manifest count does not match "
            "the authoritative validation report."
        )

    seen_ids: set[str] = set()
    descriptors: list[
        dict[str, Any]
    ] = []

    udare_root = _udare_articles_root(
        normalized_workspace_id
    )

    for index, record in enumerate(
        records,
        start=1,
    ):
        source_record_id = str(
            record.get(
                "source_record_id"
            )
            or record.get(
                "document_id"
            )
            or record.get(
                "article_id"
            )
            or ""
        ).strip()

        if not source_record_id:
            raise CertifiedWucInputError(
                f"PASS record {index} has no stable identifier."
            )

        if source_record_id in seen_ids:
            raise CertifiedWucInputError(
                "Duplicate PASS record identifier: "
                + source_record_id
            )

        seen_ids.add(
            source_record_id
        )

        article_reference = None

        for field in (
            "article_reference",
            "article_path",
            "source_article_path",
            "udare_article_path",
            "content_ref",
        ):
            value = record.get(
                field
            )

            if value:
                article_reference = value
                break

        if not article_reference:
            raise CertifiedWucInputError(
                "PASS record has no UDARE article reference: "
                + source_record_id
            )

        article_path = _resolve_reference(
            article_reference
        )

        try:
            article_path.relative_to(
                udare_root
            )

        except ValueError as exc:
            raise CertifiedWucInputError(
                "PASS record points outside the UDARE article directory: "
                + source_record_id
            ) from exc

        if not article_path.is_file():
            raise CertifiedWucInputError(
                "Referenced UDARE article is missing: "
                + str(
                    article_path
                )
            )

        expected_article_hash = str(
            record.get(
                "article_sha256"
            )
            or record.get(
                "article_hash"
            )
            or record.get(
                "content_hash"
            )
            or ""
        ).strip().lower()

        if not expected_article_hash:
            raise CertifiedWucInputError(
                "PASS record has no article hash: "
                + source_record_id
            )

        actual_article_hash = _sha256_file(
            article_path
        )

        if (
            actual_article_hash
            != expected_article_hash
        ):
            raise CertifiedWucInputError(
                "UDARE article hash mismatch: "
                + source_record_id
            )

        metadata_path = None
        expected_metadata_hash = ""

        if record.get(
            "metadata_path"
        ):
            metadata_path = _resolve_reference(
                record.get(
                    "metadata_path"
                )
            )

            if not metadata_path.is_file():
                raise CertifiedWucInputError(
                    "Referenced UDARE metadata is missing: "
                    + source_record_id
                )

            expected_metadata_hash = str(
                record.get(
                    "metadata_sha256"
                )
                or ""
            ).strip().lower()

            if (
                expected_metadata_hash
                and _sha256_file(
                    metadata_path
                )
                != expected_metadata_hash
            ):
                raise CertifiedWucInputError(
                    "UDARE metadata hash mismatch: "
                    + source_record_id
                )

        descriptors.append(
            {
                "source_record_id":
                    source_record_id,

                "workspace_id":
                    normalized_workspace_id,

                "article_path":
                    str(
                        article_path
                    ),

                "article_sha256":
                    actual_article_hash,

                "metadata_path":
                    (
                        str(
                            metadata_path
                        )
                        if metadata_path
                        else None
                    ),

                "metadata_sha256":
                    expected_metadata_hash
                    or None,

                "source_url":
                    record.get(
                        "source_url"
                    )
                    or record.get(
                        "canonical_url"
                    )
                    or record.get(
                        "url"
                    ),

                "display_title":
                    record.get(
                        "display_title"
                    )
                    or record.get(
                        "title"
                    ),

                "article_validation_status":
                    "PASS",

                "article_validation_run_id":
                    report.get(
                        "run_id"
                    ),

                "article_validation_certificate_id":
                    report.get(
                        "certificate_id"
                    ),
            }
        )

    return {
        "contract_version":
            INPUT_CONTRACT_VERSION,

        "workspace_id":
            normalized_workspace_id,

        "article_validation_run_id":
            report.get(
                "run_id"
            ),

        "article_validation_certificate_id":
            report.get(
                "certificate_id"
            ),

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

        "descriptors":
            descriptors,

        "article_bodies_loaded":
            False,

        "article_bodies_copied":
            False,

        "intermediate_wuc_store_created":
            False,
    }


def load_transient_certified_wuc_source_v1(
    descriptor: Mapping[str, Any],
) -> dict[str, Any]:
    article_path = _resolve_reference(
        descriptor.get(
            "article_path"
        )
    )

    expected_article_hash = str(
        descriptor.get(
            "article_sha256"
        )
        or ""
    ).strip().lower()

    actual_article_hash = _sha256_file(
        article_path
    )

    if (
        not expected_article_hash
        or actual_article_hash
        != expected_article_hash
    ):
        raise CertifiedWucInputError(
            "Transient UDARE article hash verification failed."
        )

    metadata: dict[str, Any] = {}

    metadata_value = descriptor.get(
        "metadata_path"
    )

    if metadata_value:
        metadata_path = _resolve_reference(
            metadata_value
        )

        expected_metadata_hash = str(
            descriptor.get(
                "metadata_sha256"
            )
            or ""
        ).strip().lower()

        if (
            expected_metadata_hash
            and _sha256_file(
                metadata_path
            )
            != expected_metadata_hash
        ):
            raise CertifiedWucInputError(
                "Transient UDARE metadata hash verification failed."
            )

        metadata = _load_json(
            metadata_path
        )

    html = article_path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    if not html.strip():
        raise CertifiedWucInputError(
            "Transient UDARE HTML is empty."
        )

    return {
        "descriptor":
            dict(
                descriptor
            ),

        "udare_html":
            html,

        "udare_metadata":
            metadata,

        "article_body_loaded_transiently":
            True,

        "article_body_persisted_by_wuc":
            False,

        "article_body_copied_to_intermediate_store":
            False,
    }
