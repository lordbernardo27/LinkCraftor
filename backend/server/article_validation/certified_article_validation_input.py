"""Certified, read-only Article Validation input loader.

This module consumes the Website Article Integrity certified-active ledger.

It does not:
- read Raw HTML;
- reconstruct articles;
- rerun Website Article Integrity;
- modify UDARE articles;
- copy article bodies into another store.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


LOADER_VERSION = (
    "certified_article_validation_input_v1"
)

PROJECT_ROOT = (
    Path(__file__).resolve().parents[3]
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

CERTIFICATION_STATUS_REQUIRED = (
    "CERTIFIED"
)

INVALID_ACTIVE_STATUSES = {
    "FAIL",
    "FAILED",
    "QUARANTINED",
    "REJECTED",
    "BLOCKED",
}

CANDIDATE_METADATA_FIELDS = (
    "workspace_id",
    "document_id",
    "html_id",
    "source_record_id",
    "source_url",
    "canonical_url",
    "url",
    "title",
    "display_title",
    "h1",
    "headings",
    "article_filename",
    "article_path",
    "udare_article_body_sha256",
    "article_body_sha256",
    "article_document_sha256",
    "content_block_count",
    "reconstruction_status",
    "udare_engine",
)


def _safe_workspace_id(
    workspace_id: str,
) -> str:
    value = str(
        workspace_id or ""
    ).strip()

    if not value:
        raise ValueError(
            "workspace_id is required."
        )

    safe = "".join(
        character
        if (
            character.isalnum()
            or character in {"-", "_", "."}
        )
        else "_"
        for character in value
    ).strip("._")

    if not safe:
        raise ValueError(
            "workspace_id is invalid."
        )

    return safe


def _load_json(
    path: Path,
) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


def _read_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    records: list[
        dict[str, Any]
    ] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        errors="strict",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            try:
                value = json.loads(
                    line
                )

            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    "Invalid certified-active JSONL "
                    f"at line {line_number}: {exc}"
                ) from exc

            if not isinstance(
                value,
                dict,
            ):
                raise RuntimeError(
                    "Certified-active ledger record "
                    f"{line_number} is not an object."
                )

            records.append(
                value
            )

    return records


def _sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def _is_within(
    path: Path,
    root: Path,
) -> bool:
    try:
        path.relative_to(root)
        return True

    except ValueError:
        return False


def _resolve_certified_path(
    value: Any,
    *,
    reference_root: Path,
    required_root: Path,
    field_name: str,
) -> Path:
    text = str(
        value or ""
    ).strip()

    if not text:
        raise RuntimeError(
            f"Certified ledger field is empty: {field_name}"
        )

    supplied = Path(text)

    candidates: list[Path] = []

    if supplied.is_absolute():
        candidates.append(
            supplied
        )

    else:
        workspace_root = (
            required_root.parent
        )

        candidates.extend(
            (
                required_root / supplied,
                workspace_root / supplied,
                PROJECT_ROOT / supplied,
                reference_root / supplied,
                DATA_ROOT / supplied,
            )
        )

    selected: Path | None = None

    for candidate in candidates:
        resolved = candidate.resolve()

        if resolved.is_file():
            selected = resolved
            break

    if selected is None:
        raise FileNotFoundError(
            "Unable to resolve certified ledger "
            f"{field_name}: {text}"
        )

    required_resolved = required_root.resolve()

    if not _is_within(
        selected,
        required_resolved,
    ):
        raise RuntimeError(
            f"Certified {field_name} escaped its "
            f"required workspace directory: {selected}"
        )

    return selected


def _certificate_path(
    workspace_id: str,
) -> Path:
    return (
        DATA_ROOT
        / "website_article_integrity"
        / workspace_id
        / "certification"
        / "website_article_integrity_certificate.json"
    )


def _resolve_active_ledger_path(
    certificate: Mapping[str, Any],
    certificate_path: Path,
) -> Path:
    raw_path = str(
        certificate.get(
            "certified_active_ledger_path"
        )
        or ""
    ).strip()

    if not raw_path:
        raise RuntimeError(
            "Integrity certificate does not provide "
            "certified_active_ledger_path."
        )

    supplied = Path(raw_path)

    candidates: list[Path] = []

    if supplied.is_absolute():
        candidates.append(
            supplied
        )

    else:
        candidates.extend(
            (
                PROJECT_ROOT / supplied,
                certificate_path.parent
                / supplied,
                DATA_ROOT / supplied,
            )
        )

    for candidate in candidates:
        resolved = candidate.resolve()

        if resolved.is_file():
            return resolved

    raise FileNotFoundError(
        "Unable to resolve certified active ledger: "
        f"{raw_path}"
    )


def _nonempty(
    value: Any,
) -> bool:
    if value is None:
        return False

    if isinstance(
        value,
        str,
    ):
        return bool(
            value.strip()
        )

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
            dict,
        ),
    ):
        return bool(value)

    return True


def load_certified_article_validation_input(
    workspace_id: str,
    *,
    expected_active_count: int | None = None,
) -> dict[str, Any]:
    """Load and verify all certified active Article Validation inputs."""

    workspace_id = _safe_workspace_id(
        workspace_id
    )

    certificate_path = (
        _certificate_path(
            workspace_id
        )
    )

    if not certificate_path.is_file():
        raise FileNotFoundError(
            "Website Article Integrity certificate "
            f"does not exist: {certificate_path}"
        )

    certificate = _load_json(
        certificate_path
    )

    certificate_workspace = str(
        certificate.get(
            "workspace_id"
        )
        or ""
    ).strip()

    if (
        certificate_workspace
        and certificate_workspace
        != workspace_id
    ):
        raise RuntimeError(
            "Integrity certificate workspace mismatch: "
            f"{certificate_workspace} != {workspace_id}"
        )

    certification_status = str(
        certificate.get(
            "certification_status"
        )
        or ""
    ).strip().upper()

    if (
        certification_status
        != CERTIFICATION_STATUS_REQUIRED
    ):
        raise RuntimeError(
            "Website Article Integrity is not certified: "
            f"{certification_status or 'MISSING'}"
        )

    coverage = certificate.get(
        "coverage",
        {},
    )

    if not isinstance(
        coverage,
        Mapping,
    ):
        raise RuntimeError(
            "Integrity certificate coverage is invalid."
        )

    certified_active_count = int(
        coverage.get(
            "active_certified_count"
        )
        or 0
    )

    if expected_active_count is not None:
        if (
            certified_active_count
            != int(expected_active_count)
        ):
            raise RuntimeError(
                "Certified active count mismatch: "
                f"{certified_active_count} != "
                f"{int(expected_active_count)}"
            )

    active_ledger_path = (
        _resolve_active_ledger_path(
            certificate,
            certificate_path,
        )
    )

    ledger_records = _read_jsonl(
        active_ledger_path
    )

    if (
        len(ledger_records)
        != certified_active_count
    ):
        raise RuntimeError(
            "Certified active ledger count mismatch: "
            f"{len(ledger_records)} != "
            f"{certified_active_count}"
        )

    udare_workspace_root = (
        DATA_ROOT
        / "udare_store"
        / workspace_id
    )

    article_root = (
        udare_workspace_root
        / "articles"
    )

    metadata_root = (
        udare_workspace_root
        / "metadata"
    )

    if not article_root.is_dir():
        raise FileNotFoundError(
            f"UDARE article directory is missing: {article_root}"
        )

    if not metadata_root.is_dir():
        raise FileNotFoundError(
            f"UDARE metadata directory is missing: {metadata_root}"
        )

    seen_identifiers: set[str] = set()

    verified_records: list[
        dict[str, Any]
    ] = []

    metadata_key_coverage: Counter[str] = (
        Counter()
    )

    candidate_field_coverage: Counter[
        str
    ] = Counter()

    integrity_status_counts: Counter[
        str
    ] = Counter()

    for position, ledger_record in enumerate(
        ledger_records,
        start=1,
    ):
        source_record_id = str(
            ledger_record.get(
                "source_record_id"
            )
            or ""
        ).strip()

        if not source_record_id:
            raise RuntimeError(
                "Certified active record has no "
                f"source_record_id at position {position}."
            )

        if source_record_id in seen_identifiers:
            raise RuntimeError(
                "Duplicate certified source_record_id: "
                f"{source_record_id}"
            )

        seen_identifiers.add(
            source_record_id
        )

        ledger_workspace = str(
            ledger_record.get(
                "workspace_id"
            )
            or ""
        ).strip()

        if (
            ledger_workspace
            and ledger_workspace
            != workspace_id
        ):
            raise RuntimeError(
                "Certified active ledger workspace mismatch "
                f"for {source_record_id}: {ledger_workspace}"
            )

        integrity_status = str(
            ledger_record.get(
                "overall_integrity_status"
            )
            or ""
        ).strip().upper()

        integrity_status_counts[
            integrity_status or "MISSING"
        ] += 1

        if integrity_status in (
            INVALID_ACTIVE_STATUSES
        ):
            raise RuntimeError(
                "Invalid integrity status in certified "
                f"active ledger for {source_record_id}: "
                f"{integrity_status}"
            )

        article_path = (
            _resolve_certified_path(
                ledger_record.get(
                    "article_path"
                ),
                reference_root=(
                    active_ledger_path.parent
                ),
                required_root=article_root,
                field_name="article_path",
            )
        )

        metadata_path = (
            _resolve_certified_path(
                ledger_record.get(
                    "metadata_path"
                ),
                reference_root=(
                    active_ledger_path.parent
                ),
                required_root=metadata_root,
                field_name="metadata_path",
            )
        )

        expected_article_sha256 = str(
            ledger_record.get(
                "article_sha256"
            )
            or ""
        ).strip().lower()

        expected_metadata_sha256 = str(
            ledger_record.get(
                "metadata_sha256"
            )
            or ""
        ).strip().lower()

        if len(expected_article_sha256) != 64:
            raise RuntimeError(
                "Invalid article SHA-256 for "
                f"{source_record_id}."
            )

        if len(expected_metadata_sha256) != 64:
            raise RuntimeError(
                "Invalid metadata SHA-256 for "
                f"{source_record_id}."
            )

        actual_article_sha256 = (
            _sha256_file(
                article_path
            )
        )

        actual_metadata_sha256 = (
            _sha256_file(
                metadata_path
            )
        )

        if (
            actual_article_sha256
            != expected_article_sha256
        ):
            raise RuntimeError(
                "Certified article hash mismatch for "
                f"{source_record_id}."
            )

        if (
            actual_metadata_sha256
            != expected_metadata_sha256
        ):
            raise RuntimeError(
                "Certified metadata hash mismatch for "
                f"{source_record_id}."
            )

        metadata = _load_json(
            metadata_path
        )

        metadata_workspace = str(
            metadata.get(
                "workspace_id"
            )
            or ""
        ).strip()

        if (
            metadata_workspace
            and metadata_workspace
            != workspace_id
        ):
            raise RuntimeError(
                "UDARE metadata workspace mismatch "
                f"for {source_record_id}: "
                f"{metadata_workspace}"
            )

        metadata_source_record_id = str(
            metadata.get(
                "source_record_id"
            )
            or ""
        ).strip()

        if (
            metadata_source_record_id
            and metadata_source_record_id
            != source_record_id
        ):
            raise RuntimeError(
                "UDARE metadata source_record_id mismatch "
                f"for {source_record_id}: "
                f"{metadata_source_record_id}"
            )

        for key in metadata:
            metadata_key_coverage[
                str(key)
            ] += 1

        for field in (
            CANDIDATE_METADATA_FIELDS
        ):
            if (
                field in metadata
                and _nonempty(
                    metadata.get(field)
                )
            ):
                candidate_field_coverage[
                    field
                ] += 1

        verified_records.append(
            {
                "position": position,
                "workspace_id": workspace_id,
                "source_record_id": (
                    source_record_id
                ),
                "source_url": str(
                    ledger_record.get(
                        "source_url"
                    )
                    or ""
                ).strip(),
                "display_title": str(
                    ledger_record.get(
                        "display_title"
                    )
                    or ""
                ).strip(),
                "article_path": str(
                    article_path
                ),
                "metadata_path": str(
                    metadata_path
                ),
                "article_sha256": (
                    actual_article_sha256
                ),
                "metadata_sha256": (
                    actual_metadata_sha256
                ),
                "overall_integrity_status": (
                    integrity_status
                ),
                "certificate_scope": (
                    ledger_record.get(
                        "certificate_scope"
                    )
                ),
                "stage_statuses": (
                    ledger_record.get(
                        "stage_statuses"
                    )
                ),
            }
        )

    return {
        "loader_version": LOADER_VERSION,
        "workspace_id": workspace_id,
        "certificate_status": (
            certification_status
        ),
        "certificate_id": (
            certificate.get(
                "certificate_id"
            )
        ),
        "certificate_path": str(
            certificate_path
        ),
        "active_ledger_path": str(
            active_ledger_path
        ),
        "certified_active_count": (
            certified_active_count
        ),
        "integrity_quarantined_count": int(
            coverage.get(
                "quarantined_count"
            )
            or 0
        ),
        "deferred_upstream_count": int(
            coverage.get(
                "deferred_upstream_count"
            )
            or 0
        ),
        "verified_record_count": len(
            verified_records
        ),
        "integrity_status_counts": dict(
            integrity_status_counts
        ),
        "metadata_key_coverage": dict(
            metadata_key_coverage.most_common()
        ),
        "candidate_metadata_field_coverage": dict(
            candidate_field_coverage
        ),
        "records": verified_records,
        "article_bodies_loaded": False,
        "article_bodies_copied": False,
        "source_files_modified": [],
    }


def load_certified_article_payload(
    descriptor: Mapping[str, Any],
) -> dict[str, Any]:
    """Load one verified article body transiently for validation."""

    source_record_id = str(
        descriptor.get(
            "source_record_id"
        )
        or ""
    ).strip()

    article_path = Path(
        str(
            descriptor.get(
                "article_path"
            )
            or ""
        )
    )

    metadata_path = Path(
        str(
            descriptor.get(
                "metadata_path"
            )
            or ""
        )
    )

    if not source_record_id:
        raise ValueError(
            "descriptor source_record_id is required."
        )

    if not article_path.is_file():
        raise FileNotFoundError(
            f"Article file is missing: {article_path}"
        )

    if not metadata_path.is_file():
        raise FileNotFoundError(
            f"Metadata file is missing: {metadata_path}"
        )

    expected_article_sha256 = str(
        descriptor.get(
            "article_sha256"
        )
        or ""
    ).strip().lower()

    expected_metadata_sha256 = str(
        descriptor.get(
            "metadata_sha256"
        )
        or ""
    ).strip().lower()

    if (
        _sha256_file(article_path)
        != expected_article_sha256
    ):
        raise RuntimeError(
            "Article changed after certified-input load: "
            f"{source_record_id}"
        )

    if (
        _sha256_file(metadata_path)
        != expected_metadata_sha256
    ):
        raise RuntimeError(
            "Metadata changed after certified-input load: "
            f"{source_record_id}"
        )

    article_html = article_path.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

    metadata = _load_json(
        metadata_path
    )

    return {
        "workspace_id": descriptor.get(
            "workspace_id"
        ),
        "source_record_id": (
            source_record_id
        ),
        "source_url": descriptor.get(
            "source_url"
        ),
        "display_title": descriptor.get(
            "display_title"
        ),
        "article_path": str(
            article_path
        ),
        "metadata_path": str(
            metadata_path
        ),
        "article_sha256": (
            expected_article_sha256
        ),
        "metadata_sha256": (
            expected_metadata_sha256
        ),
        "article_html": article_html,
        "metadata": metadata,
    }

