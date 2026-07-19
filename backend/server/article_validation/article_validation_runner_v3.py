"""Canonical Article Validation Runner v3.

Canonical pipeline:

UDARE Store
    -> Website Article Integrity verification
    -> Article Validation
    -> Website Unified Content

This runner creates evidence and control artifacts only.

It does not create:
- an Article Validation Store;
- a Certified Website Article Store;
- an intermediate article-body store;
- copied article documents;
- rewritten article content.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from uuid import uuid4

from backend.server.article_validation.article_validation_engine_v3 import (
    ARTICLE_VALIDATION_ENGINE_VERSION,
    extract_article_validation_document_v3,
    validate_certified_article_v3,
)

from backend.server.article_validation.certified_article_validation_input import (
    load_certified_article_payload,
    load_certified_article_validation_input,
)


RUNNER_VERSION = (
    "article_validation_runner_v3_"
    "integrity_verified_evidence_only"
)

ARTIFACT_SCHEMA_VERSION = (
    "article_validation_artifacts_v3"
)

DEFAULT_BATCH_SIZE = 100

MAXIMUM_VERIFICATION_SAMPLE_SIZE = 10

PROJECT_ROOT = (
    Path(__file__).resolve().parents[3]
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

PROHIBITED_BODY_FIELDS = {
    "article_body",
    "article_html",
    "content_body",
    "cleaned_article_text",
    "body_text",
    "raw_html",
    "selected_html",
    "full_text",
}


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _safe_name(
    value: str,
    *,
    field_name: str,
) -> str:
    text = str(
        value or ""
    ).strip()

    if not text:
        raise ValueError(
            f"{field_name} is required."
        )

    safe = "".join(
        character
        if (
            character.isalnum()
            or character in {"-", "_", "."}
        )
        else "_"
        for character in text
    ).strip("._")

    if not safe:
        raise ValueError(
            f"{field_name} is invalid."
        )

    return safe


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


def _sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def _atomic_write_json(
    path: Path,
    payload: Mapping[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.with_name(
        path.name
        + "."
        + uuid4().hex
        + ".tmp"
    )

    temporary_path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary_path.replace(
        path
    )


def _atomic_write_jsonl(
    path: Path,
    records: Iterable[
        Mapping[str, Any]
    ],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.with_name(
        path.name
        + "."
        + uuid4().hex
        + ".tmp"
    )

    with temporary_path.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        for record in records:
            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )

            handle.write("\n")

    temporary_path.replace(
        path
    )


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
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            value = json.loads(
                line
            )

            if not isinstance(
                value,
                dict,
            ):
                raise RuntimeError(
                    "JSONL record is not an object "
                    f"at line {line_number}: {path}"
                )

            records.append(
                value
            )

    return records


def _resolve_reference_path(
    raw_value: Any,
    *,
    reference_root: Path,
    required_root: Path,
) -> Path:
    text = str(
        raw_value or ""
    ).strip()

    if not text:
        raise RuntimeError(
            "Required evidence path is missing."
        )

    supplied = Path(text)

    candidates: list[Path] = []

    if supplied.is_absolute():
        candidates.append(
            supplied
        )

    else:
        candidates.extend(
            (
                PROJECT_ROOT / supplied,
                reference_root / supplied,
                DATA_ROOT / supplied,
            )
        )

    required_root = required_root.resolve()

    for candidate in candidates:
        resolved = candidate.resolve()

        if not resolved.is_file():
            continue

        try:
            resolved.relative_to(
                required_root
            )

        except ValueError:
            continue

        return resolved

    raise FileNotFoundError(
        "Unable to resolve required evidence path: "
        + text
    )


def _project_relative(
    path: Path,
) -> str:
    resolved = path.resolve()

    try:
        return resolved.relative_to(
            PROJECT_ROOT
        ).as_posix()

    except ValueError:
        return str(
            resolved
        )


def _normalize_headings(
    value: Any,
) -> list[str]:
    if not isinstance(
        value,
        list,
    ):
        return []

    headings: list[str] = []

    for item in value:
        if isinstance(
            item,
            Mapping,
        ):
            text = str(
                item.get("text")
                or item.get("heading")
                or item.get("title")
                or ""
            ).strip()

        else:
            text = str(
                item or ""
            ).strip()

        if text:
            headings.append(
                text
            )

    return headings


def _find_prohibited_fields(
    value: Any,
    *,
    prefix: str = "",
) -> list[str]:
    findings: list[str] = []

    if isinstance(
        value,
        Mapping,
    ):
        for key, item in value.items():
            key_text = str(key)

            field_path = (
                f"{prefix}.{key_text}"
                if prefix
                else key_text
            )

            if (
                key_text.casefold()
                in PROHIBITED_BODY_FIELDS
            ):
                findings.append(
                    field_path
                )

            findings.extend(
                _find_prohibited_fields(
                    item,
                    prefix=field_path,
                )
            )

    elif isinstance(
        value,
        list,
    ):
        for index, item in enumerate(
            value
        ):
            findings.extend(
                _find_prohibited_fields(
                    item,
                    prefix=(
                        f"{prefix}[{index}]"
                    ),
                )
            )

    return findings


def article_validation_artifact_paths_v3(
    *,
    workspace_id: str,
    run_id: str,
    artifact_root_override: str | Path | None = None,
) -> dict[str, Path]:
    workspace_id = _safe_name(
        workspace_id,
        field_name="workspace_id",
    )

    run_id = _safe_name(
        run_id,
        field_name="run_id",
    )

    if artifact_root_override is None:
        base_root = (
            DATA_ROOT
            / "article_validation_evidence"
        )

    else:
        base_root = Path(
            artifact_root_override
        ).resolve()

    root = (
        base_root
        / workspace_id
        / "runs"
        / run_id
    )

    return {
        "root":
            root,

        "pass_manifest":
            root
            / "article_validation_pass_manifest.jsonl",

        "failure_manifest":
            root
            / "article_validation_failure_manifest.jsonl",

        "execution_ledger":
            root
            / "article_validation_execution_ledger.json",

        "report":
            root
            / "article_validation_report.json",

        "certificate":
            root
            / "article_validation_certificate.json",

        "evidence_manifest":
            root
            / "article_validation_evidence_manifest.json",
    }


def _load_integrity_quarantine_ids(
    certified_input: Mapping[str, Any],
) -> tuple[set[str], str]:
    certificate_path = Path(
        str(
            certified_input.get(
                "certificate_path"
            )
            or ""
        )
    )

    if not certificate_path.is_file():
        raise FileNotFoundError(
            "Website Article Integrity certificate "
            "path is unavailable."
        )

    certificate = _load_json(
        certificate_path
    )

    quarantine_count = int(
        certified_input.get(
            "integrity_quarantined_count"
        )
        or 0
    )

    raw_quarantine_path = (
        certificate.get(
            "certified_quarantine_ledger_path"
        )
    )

    if (
        not raw_quarantine_path
        and quarantine_count == 0
    ):
        return set(), ""

    integrity_workspace_root = (
        DATA_ROOT
        / "website_article_integrity"
        / str(
            certified_input.get(
                "workspace_id"
            )
        )
    )

    quarantine_path = (
        _resolve_reference_path(
            raw_quarantine_path,
            reference_root=(
                certificate_path.parent
            ),
            required_root=(
                integrity_workspace_root
            ),
        )
    )

    quarantine_records = (
        _read_jsonl(
            quarantine_path
        )
    )

    if (
        len(quarantine_records)
        != quarantine_count
    ):
        raise RuntimeError(
            "Integrity quarantine count mismatch: "
            f"{len(quarantine_records)} != "
            f"{quarantine_count}"
        )

    quarantine_ids: set[str] = set()

    for record in quarantine_records:
        source_record_id = str(
            record.get(
                "source_record_id"
            )
            or ""
        ).strip()

        if not source_record_id:
            raise RuntimeError(
                "Integrity quarantine record is missing "
                "source_record_id."
            )

        if source_record_id in quarantine_ids:
            raise RuntimeError(
                "Duplicate Integrity quarantine identifier: "
                + source_record_id
            )

        quarantine_ids.add(
            source_record_id
        )

    return (
        quarantine_ids,
        _project_relative(
            quarantine_path
        ),
    )


def build_article_validation_decision_v3(
    *,
    certified_input: Mapping[str, Any],
    descriptor: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify Integrity evidence and validate one UDARE article."""

    source_record_id = str(
        descriptor.get(
            "source_record_id"
        )
        or ""
    ).strip()

    if not source_record_id:
        raise RuntimeError(
            "Certified descriptor has no source_record_id."
        )

    integrity_status = str(
        descriptor.get(
            "overall_integrity_status"
        )
        or ""
    ).strip().upper()

    if integrity_status != "PASS":
        raise RuntimeError(
            "Certified-active article does not have "
            "Integrity PASS status: "
            + source_record_id
        )

    payload = (
        load_certified_article_payload(
            descriptor
        )
    )

    metadata = payload.get(
        "metadata"
    )

    if not isinstance(
        metadata,
        Mapping,
    ):
        raise RuntimeError(
            "UDARE metadata is not an object: "
            + source_record_id
        )

    extracted = (
        extract_article_validation_document_v3(
            str(
                payload.get(
                    "article_html"
                )
                or ""
            )
        )
    )

    title = str(
        metadata.get(
            "title"
        )
        or payload.get(
            "display_title"
        )
        or extracted.get(
            "title"
        )
        or extracted.get(
            "h1"
        )
        or ""
    ).strip()

    h1 = str(
        metadata.get(
            "h1"
        )
        or extracted.get(
            "h1"
        )
        or ""
    ).strip()

    headings = (
        _normalize_headings(
            metadata.get(
                "headings"
            )
        )
        or _normalize_headings(
            extracted.get(
                "headings"
            )
        )
    )

    source_url = str(
        payload.get(
            "source_url"
        )
        or metadata.get(
            "source_url"
        )
        or metadata.get(
            "canonical_url"
        )
        or metadata.get(
            "url"
        )
        or ""
    ).strip()

    validation = (
        validate_certified_article_v3(
            article_text=str(
                extracted.get(
                    "article_text"
                )
                or ""
            ),
            title=title,
            h1=h1,
            headings=headings,
            source_record_id=(
                source_record_id
            ),
            source_url=source_url,
            article_sha256=str(
                payload.get(
                    "article_sha256"
                )
                or ""
            ),
            metadata_sha256=str(
                payload.get(
                    "metadata_sha256"
                )
                or ""
            ),
            integrity_certificate_id=str(
                certified_input.get(
                    "certificate_id"
                )
                or ""
            ),
            integrity_certification_status=str(
                certified_input.get(
                    "certificate_status"
                )
                or ""
            ),
            overall_integrity_status=(
                integrity_status
            ),
        )
    )

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

    decision = {
        "schema_version":
            "article_validation_decision_v3",

        "workspace_id":
            certified_input.get(
                "workspace_id"
            ),

        "source_record_id":
            source_record_id,

        "document_id":
            metadata.get(
                "document_id"
            ),

        "html_id":
            metadata.get(
                "html_id"
            ),

        "source_url":
            source_url,

        "title":
            title,

        "article_reference":
            _project_relative(
                article_path
            ),

        "metadata_reference":
            _project_relative(
                metadata_path
            ),

        "article_sha256":
            validation.get(
                "article_sha256"
            ),

        "metadata_sha256":
            validation.get(
                "metadata_sha256"
            ),

        "integrity_certificate_id":
            certified_input.get(
                "certificate_id"
            ),

        "integrity_certificate_status":
            certified_input.get(
                "certificate_status"
            ),

        "integrity_status":
            integrity_status,

        "integrity_verified":
            True,

        "article_validation_status":
            validation.get(
                "status"
            ),

        "passed":
            validation.get(
                "passed"
            ),

        "validation_version":
            validation.get(
                "validation_version"
            ),

        "validation_score":
            validation.get(
                "validation_score"
            ),

        "quality_grade":
            validation.get(
                "quality_grade"
            ),

        "checks":
            validation.get(
                "checks"
            ),

        "statistics":
            validation.get(
                "statistics"
            ),

        "warnings":
            validation.get(
                "warnings"
            ),

        "errors":
            validation.get(
                "errors"
            ),

        "rejection_reasons":
            validation.get(
                "rejection_reasons"
            ),

        "eligible_for_wuc":
            validation.get(
                "eligible_for_wuc"
            ),

        "runner_version":
            RUNNER_VERSION,

        "validated_at":
            _utc_now(),

        "article_body_included":
            False,

        "article_body_modified":
            False,

        "article_body_copied":
            False,
    }

    prohibited_fields = (
        _find_prohibited_fields(
            decision
        )
    )

    if prohibited_fields:
        raise RuntimeError(
            "Article Validation decision contains "
            "prohibited body fields: "
            + ", ".join(
                prohibited_fields
            )
        )

    return decision


def _write_validation_artifacts(
    *,
    workspace_id: str,
    run_id: str,
    certified_input: Mapping[str, Any],
    decisions: Sequence[
        Mapping[str, Any]
    ],
    quarantine_count: int,
    quarantine_ledger_reference: str,
    artifact_root_override: str | Path | None,
    certify: bool,
    verification_only: bool,
) -> dict[str, Any]:
    paths = (
        article_validation_artifact_paths_v3(
            workspace_id=workspace_id,
            run_id=run_id,
            artifact_root_override=(
                artifact_root_override
            ),
        )
    )

    if paths["root"].exists():
        raise FileExistsError(
            "Article Validation evidence run already exists: "
            + str(
                paths["root"]
            )
        )

    pass_records = [
        dict(decision)
        for decision in decisions
        if decision.get(
            "article_validation_status"
        )
        == "PASS"
    ]

    failure_records = [
        dict(decision)
        for decision in decisions
        if decision.get(
            "article_validation_status"
        )
        == "FAIL"
    ]

    processed_count = len(
        decisions
    )

    pass_count = len(
        pass_records
    )

    fail_count = len(
        failure_records
    )

    if (
        pass_count
        + fail_count
        != processed_count
    ):
        raise RuntimeError(
            "Article Validation PASS/FAIL accounting "
            "does not equal the processed population."
        )

    identifiers = [
        str(
            decision.get(
                "source_record_id"
            )
            or ""
        )
        for decision in decisions
    ]

    if (
        len(
            set(identifiers)
        )
        != len(identifiers)
    ):
        raise RuntimeError(
            "Duplicate Article Validation identifiers detected."
        )

    warning_counts: Counter[str] = Counter()
    rejection_counts: Counter[str] = Counter()
    grade_counts: Counter[str] = Counter()

    for decision in decisions:
        grade_counts[
            str(
                decision.get(
                    "quality_grade"
                )
                or "MISSING"
            )
        ] += 1

        for warning in (
            decision.get(
                "warnings"
            )
            or []
        ):
            warning_counts[
                str(warning)
            ] += 1

        for reason in (
            decision.get(
                "rejection_reasons"
            )
            or []
        ):
            rejection_counts[
                str(reason)
            ] += 1

    generated_at = _utc_now()

    execution_ledger = {
        "schema_version":
            ARTIFACT_SCHEMA_VERSION,

        "artifact_type":
            "article_validation_execution_ledger",

        "workspace_id":
            workspace_id,

        "run_id":
            run_id,

        "runner_version":
            RUNNER_VERSION,

        "engine_version":
            ARTICLE_VALIDATION_ENGINE_VERSION,

        "integrity_certificate_id":
            certified_input.get(
                "certificate_id"
            ),

        "integrity_certificate_status":
            certified_input.get(
                "certificate_status"
            ),

        "certified_active_count":
            certified_input.get(
                "certified_active_count"
            ),

        "processed_count":
            processed_count,

        "pass_count":
            pass_count,

        "fail_count":
            fail_count,

        "integrity_quarantined_count":
            quarantine_count,

        "deferred_upstream_count":
            certified_input.get(
                "deferred_upstream_count"
            ),

        "verification_only":
            verification_only,

        "article_bodies_stored":
            False,

        "article_bodies_modified":
            False,

        "article_bodies_copied":
            False,

        "status":
            "COMPLETED",

        "generated_at":
            generated_at,
    }

    report = {
        "schema_version":
            ARTIFACT_SCHEMA_VERSION,

        "artifact_type":
            "article_validation_report",

        "workspace_id":
            workspace_id,

        "run_id":
            run_id,

        "processed_count":
            processed_count,

        "pass_count":
            pass_count,

        "fail_count":
            fail_count,

        "eligible_for_wuc_count":
            pass_count,

        "quality_grade_counts":
            dict(
                grade_counts
            ),

        "warning_counts":
            dict(
                warning_counts
            ),

        "rejection_reason_counts":
            dict(
                rejection_counts
            ),

        "integrity_quarantine_ledger_reference":
            quarantine_ledger_reference,

        "pass_manifest_reference":
            _project_relative(
                paths[
                    "pass_manifest"
                ]
            ),

        "failure_manifest_reference":
            _project_relative(
                paths[
                    "failure_manifest"
                ]
            ),

        "verification_only":
            verification_only,

        "article_bodies_stored":
            False,

        "article_bodies_modified":
            False,

        "article_bodies_copied":
            False,

        "generated_at":
            generated_at,
    }

    _atomic_write_jsonl(
        paths[
            "pass_manifest"
        ],
        pass_records,
    )

    _atomic_write_jsonl(
        paths[
            "failure_manifest"
        ],
        failure_records,
    )

    _atomic_write_json(
        paths[
            "execution_ledger"
        ],
        execution_ledger,
    )

    _atomic_write_json(
        paths[
            "report"
        ],
        report,
    )

    certificate: dict[
        str,
        Any
    ] | None = None

    core_artifact_paths = {
        "pass_manifest":
            paths[
                "pass_manifest"
            ],

        "failure_manifest":
            paths[
                "failure_manifest"
            ],

        "execution_ledger":
            paths[
                "execution_ledger"
            ],

        "report":
            paths[
                "report"
            ],
    }

    core_hashes = {
        name: _sha256_file(path)
        for name, path
        in core_artifact_paths.items()
    }

    core_evidence_sha256 = (
        _sha256_text(
            json.dumps(
                core_hashes,
                sort_keys=True,
            )
        )
    )

    if certify:
        certificate_id = (
            "article_validation_certificate_"
            + _sha256_text(
                workspace_id
                + "|"
                + run_id
                + "|"
                + core_evidence_sha256
            )[:24]
        )

        certificate = {
            "schema_version":
                ARTIFACT_SCHEMA_VERSION,

            "artifact_type":
                "article_validation_certificate",

            "certificate_id":
                certificate_id,

            "workspace_id":
                workspace_id,

            "run_id":
                run_id,

            "certification_status":
                "CERTIFIED",

            "certification_outcome":
                (
                    "COMPLETE"
                    if fail_count == 0
                    else "COMPLETE_WITH_VALIDATION_FAILURES"
                ),

            "qualification":
                "ALL_CERTIFIED_ACTIVE_INPUTS_ACCOUNTED",

            "integrity_certificate_id":
                certified_input.get(
                    "certificate_id"
                ),

            "certified_active_input_count":
                certified_input.get(
                    "certified_active_count"
                ),

            "processed_count":
                processed_count,

            "pass_count":
                pass_count,

            "fail_count":
                fail_count,

            "eligible_for_wuc_count":
                pass_count,

            "integrity_quarantined_count":
                quarantine_count,

            "deferred_upstream_count":
                certified_input.get(
                    "deferred_upstream_count"
                ),

            "core_evidence_sha256":
                core_evidence_sha256,

            "article_bodies_stored":
                False,

            "article_bodies_modified":
                False,

            "article_bodies_copied":
                False,

            "certified_at":
                _utc_now(),
        }

        _atomic_write_json(
            paths[
                "certificate"
            ],
            certificate,
        )

    artifact_paths_for_evidence = dict(
        core_artifact_paths
    )

    if certificate is not None:
        artifact_paths_for_evidence[
            "certificate"
        ] = paths[
            "certificate"
        ]

    artifact_hashes = {
        name: {
            "path":
                _project_relative(
                    path
                ),

            "sha256":
                _sha256_file(
                    path
                ),
        }
        for name, path
        in artifact_paths_for_evidence.items()
    }

    evidence_root_sha256 = (
        _sha256_text(
            json.dumps(
                artifact_hashes,
                sort_keys=True,
            )
        )
    )

    evidence_manifest = {
        "schema_version":
            ARTIFACT_SCHEMA_VERSION,

        "artifact_type":
            "article_validation_evidence_manifest",

        "workspace_id":
            workspace_id,

        "run_id":
            run_id,

        "verification_only":
            verification_only,

        "artifacts":
            artifact_hashes,

        "evidence_root_sha256":
            evidence_root_sha256,

        "article_bodies_stored":
            False,

        "article_bodies_modified":
            False,

        "article_bodies_copied":
            False,

        "generated_at":
            _utc_now(),
    }

    _atomic_write_json(
        paths[
            "evidence_manifest"
        ],
        evidence_manifest,
    )

    return {
        "ok":
            True,

        "workspace_id":
            workspace_id,

        "run_id":
            run_id,

        "processed_count":
            processed_count,

        "pass_count":
            pass_count,

        "fail_count":
            fail_count,

        "eligible_for_wuc_count":
            pass_count,

        "verification_only":
            verification_only,

        "certificate_created":
            certificate is not None,

        "certificate_id":
            (
                certificate.get(
                    "certificate_id"
                )
                if certificate
                else None
            ),

        "artifact_paths":
            {
                name: str(path)
                for name, path
                in paths.items()
            },

        "article_bodies_stored":
            False,

        "article_bodies_modified":
            False,

        "article_bodies_copied":
            False,
    }


def _verify_integrity_population(
    certified_input: Mapping[str, Any],
    descriptors: Sequence[
        Mapping[str, Any]
    ],
) -> tuple[int, str]:
    if (
        certified_input.get(
            "certificate_status"
        )
        != "CERTIFIED"
    ):
        raise RuntimeError(
            "Website Article Integrity is not CERTIFIED."
        )

    certified_active_count = int(
        certified_input.get(
            "certified_active_count"
        )
        or 0
    )

    if (
        len(descriptors)
        != certified_active_count
    ):
        raise RuntimeError(
            "Certified active descriptor count mismatch: "
            f"{len(descriptors)} != "
            f"{certified_active_count}"
        )

    quarantine_ids, quarantine_reference = (
        _load_integrity_quarantine_ids(
            certified_input
        )
    )

    active_ids: set[str] = set()

    for descriptor in descriptors:
        source_record_id = str(
            descriptor.get(
                "source_record_id"
            )
            or ""
        ).strip()

        if not source_record_id:
            raise RuntimeError(
                "Certified-active descriptor is missing "
                "source_record_id."
            )

        if source_record_id in active_ids:
            raise RuntimeError(
                "Duplicate certified-active identifier: "
                + source_record_id
            )

        if source_record_id in quarantine_ids:
            raise RuntimeError(
                "Article exists in both certified-active "
                "and quarantine scopes: "
                + source_record_id
            )

        if str(
            descriptor.get(
                "overall_integrity_status"
            )
            or ""
        ).strip().upper() != "PASS":
            raise RuntimeError(
                "Certified-active article has non-PASS "
                "Integrity status: "
                + source_record_id
            )

        active_ids.add(
            source_record_id
        )

    return (
        len(quarantine_ids),
        quarantine_reference,
    )


def run_article_validation_population_v3(
    *,
    workspace_id: str,
    expected_active_count: int,
    run_id: str = "",
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> dict[str, Any]:
    """Validate the complete Integrity-certified active population."""

    workspace_id = _safe_name(
        workspace_id,
        field_name="workspace_id",
    )

    expected_active_count = int(
        expected_active_count
    )

    batch_size = int(
        batch_size
    )

    if expected_active_count < 1:
        raise ValueError(
            "expected_active_count must be positive."
        )

    if batch_size < 1:
        raise ValueError(
            "batch_size must be positive."
        )

    certified_input = (
        load_certified_article_validation_input(
            workspace_id,
            expected_active_count=(
                expected_active_count
            ),
        )
    )

    descriptors = certified_input.get(
        "records"
    )

    if not isinstance(
        descriptors,
        list,
    ):
        raise RuntimeError(
            "Certified active descriptors are invalid."
        )

    if len(descriptors) != expected_active_count:
        raise RuntimeError(
            "Complete population requirement failed: "
            f"{len(descriptors)} != "
            f"{expected_active_count}"
        )

    quarantine_count, quarantine_reference = (
        _verify_integrity_population(
            certified_input,
            descriptors,
        )
    )

    run_id = str(
        run_id or ""
    ).strip()

    if not run_id:
        run_id = (
            "article_validation_"
            + uuid4().hex
        )

    decisions: list[
        dict[str, Any]
    ] = []

    for batch_start in range(
        0,
        len(descriptors),
        batch_size,
    ):
        batch = descriptors[
            batch_start:
            batch_start + batch_size
        ]

        for descriptor in batch:
            decisions.append(
                build_article_validation_decision_v3(
                    certified_input=(
                        certified_input
                    ),
                    descriptor=descriptor,
                )
            )

    if len(decisions) != expected_active_count:
        raise RuntimeError(
            "Article Validation processed population "
            "is incomplete."
        )

    return _write_validation_artifacts(
        workspace_id=workspace_id,
        run_id=run_id,
        certified_input=certified_input,
        decisions=decisions,
        quarantine_count=(
            quarantine_count
        ),
        quarantine_ledger_reference=(
            quarantine_reference
        ),
        artifact_root_override=None,
        certify=True,
        verification_only=False,
    )


def run_article_validation_sample_v3(
    *,
    workspace_id: str,
    positions: Sequence[int],
    artifact_root_override: str | Path,
    run_id: str = "",
) -> dict[str, Any]:
    """Verify the runner using at most ten certified records."""

    workspace_id = _safe_name(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_positions = [
        int(position)
        for position in positions
    ]

    if not normalized_positions:
        raise ValueError(
            "At least one sample position is required."
        )

    if (
        len(normalized_positions)
        > MAXIMUM_VERIFICATION_SAMPLE_SIZE
    ):
        raise ValueError(
            "Verification sample exceeds the maximum "
            f"of {MAXIMUM_VERIFICATION_SAMPLE_SIZE}."
        )

    if (
        len(
            set(normalized_positions)
        )
        != len(normalized_positions)
    ):
        raise ValueError(
            "Verification positions must be unique."
        )

    certified_input = (
        load_certified_article_validation_input(
            workspace_id
        )
    )

    descriptors = certified_input.get(
        "records"
    )

    if not isinstance(
        descriptors,
        list,
    ):
        raise RuntimeError(
            "Certified active descriptors are invalid."
        )

    quarantine_count, quarantine_reference = (
        _verify_integrity_population(
            certified_input,
            descriptors,
        )
    )

    selected: list[
        Mapping[str, Any]
    ] = []

    for position in normalized_positions:
        if (
            position < 0
            or position >= len(
                descriptors
            )
        ):
            raise IndexError(
                "Sample position is outside the "
                f"certified population: {position}"
            )

        descriptor = descriptors[
            position
        ]

        if not isinstance(
            descriptor,
            Mapping,
        ):
            raise RuntimeError(
                "Certified descriptor is invalid."
            )

        selected.append(
            descriptor
        )

    decisions = [
        build_article_validation_decision_v3(
            certified_input=(
                certified_input
            ),
            descriptor=descriptor,
        )
        for descriptor in selected
    ]

    run_id = str(
        run_id or ""
    ).strip()

    if not run_id:
        run_id = (
            "article_validation_sample_"
            + uuid4().hex
        )

    return _write_validation_artifacts(
        workspace_id=workspace_id,
        run_id=run_id,
        certified_input=certified_input,
        decisions=decisions,
        quarantine_count=(
            quarantine_count
        ),
        quarantine_ledger_reference=(
            quarantine_reference
        ),
        artifact_root_override=(
            artifact_root_override
        ),
        certify=False,
        verification_only=True,
    )
