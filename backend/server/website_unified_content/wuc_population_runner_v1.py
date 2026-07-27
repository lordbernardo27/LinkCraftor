"""Run all certified website articles through the transient WUC engine.

Only evidence is persisted. Complete WUC article bodies remain transient and
are not written to a WUC Store. UUCD is not written by this runner.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


from backend.server.website_unified_content.certified_wuc_input import (
    load_article_validation_pass_contract_v1,
    load_transient_certified_wuc_source_v1,
)
from backend.server.website_unified_content.website_unified_content_engine_v1 import (
    WUC_ENGINE_VERSION,
    build_transient_website_unified_content_v1,
)


RUNNER_VERSION = (
    "wuc_population_runner_v1_"
    "complete_content_preservation_evidence_only"
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


class WucPopulationRunnerError(
    RuntimeError
):
    """Raised when the WUC population run cannot be completed."""


def _utc_now() -> str:
    return datetime.now(
        UTC
    ).isoformat()


def _run_id() -> str:
    return (
        "wuc_"
        + datetime.now(
            UTC
        ).strftime(
            "%Y%m%dT%H%M%SZ"
        )
    )


def _sha256_json(
    value: Any,
) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    ).encode(
        "utf-8"
    )

    return hashlib.sha256(
        encoded
    ).hexdigest()


def _write_json(
    path: Path,
    payload: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_jsonl(
    path: Path,
    records: list[
        dict[str, Any]
    ],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
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
                + "\n"
            )


def run_wuc_population_v1(
    *,
    workspace_id: str,
    expected_pass_count: int | None = None,
    run_id: str = "",
) -> dict[str, Any]:
    normalized_run_id = (
        str(
            run_id or ""
        ).strip()
        or _run_id()
    )

    contract = (
        load_article_validation_pass_contract_v1(
            workspace_id,
            expected_pass_count=(
                expected_pass_count
            ),
        )
    )

    descriptors = contract.get(
        "descriptors"
    )

    if not isinstance(
        descriptors,
        list,
    ):
        raise WucPopulationRunnerError(
            "Certified WUC descriptors are invalid."
        )

    evidence_root = (
        DATA_ROOT
        / "website_unified_content_evidence"
        / workspace_id
        / "runs"
        / normalized_run_id
    )

    pass_manifest_path = (
        evidence_root
        / "wuc_pass_manifest.jsonl"
    )

    fail_manifest_path = (
        evidence_root
        / "wuc_fail_manifest.jsonl"
    )

    ledger_path = (
        evidence_root
        / "wuc_execution_ledger.json"
    )

    report_path = (
        evidence_root
        / "wuc_report.json"
    )

    certificate_path = (
        evidence_root
        / "wuc_certificate.json"
    )

    started_at = _utc_now()

    pass_records: list[
        dict[str, Any]
    ] = []

    fail_records: list[
        dict[str, Any]
    ] = []

    processed_ids: set[str] = set()

    total_body_length = 0
    total_word_count = 0
    total_block_count = 0
    total_heading_count = 0

    for descriptor in descriptors:
        source_record_id = str(
            descriptor.get(
                "source_record_id"
            )
            or ""
        ).strip()

        if not source_record_id:
            fail_records.append(
                {
                    "source_record_id":
                        None,

                    "status":
                        "FAIL",

                    "reason":
                        "MISSING_SOURCE_RECORD_ID",
                }
            )

            continue

        if source_record_id in processed_ids:
            fail_records.append(
                {
                    "source_record_id":
                        source_record_id,

                    "status":
                        "FAIL",

                    "reason":
                        "DUPLICATE_PROCESSING_ATTEMPT",
                }
            )

            continue

        processed_ids.add(
            source_record_id
        )

        try:
            certified_source = (
                load_transient_certified_wuc_source_v1(
                    descriptor
                )
            )

            document = (
                build_transient_website_unified_content_v1(
                    certified_source=(
                        certified_source
                    )
                )
            )

            content_body = str(
                document.get(
                    "content_body"
                )
                or ""
            )

            if not content_body:
                raise WucPopulationRunnerError(
                    "WUC content_body is empty."
                )

            if "article_body" in document:
                raise WucPopulationRunnerError(
                    "Legacy article_body field is present."
                )

            metadata = document.get(
                "metadata"
            )

            if not isinstance(
                metadata,
                dict,
            ):
                raise WucPopulationRunnerError(
                    "WUC metadata is invalid."
                )

            if (
                metadata.get(
                    "complete_content_preserved"
                )
                is not True
            ):
                raise WucPopulationRunnerError(
                    "Complete-content preservation was not certified."
                )

            if (
                metadata.get(
                    "truncation_performed"
                )
                is not False
            ):
                raise WucPopulationRunnerError(
                    "WUC reports content truncation."
                )

            if (
                metadata.get(
                    "summarization_performed"
                )
                is not False
            ):
                raise WucPopulationRunnerError(
                    "WUC reports summarization."
                )

            body_length = int(
                document.get(
                    "body_length"
                )
                or len(
                    content_body
                )
            )

            body_word_count = int(
                document.get(
                    "body_word_count"
                )
                or 0
            )

            structure = document.get(
                "structure"
            )

            if not isinstance(
                structure,
                dict,
            ):
                raise WucPopulationRunnerError(
                    "WUC structure is invalid."
                )

            block_count = int(
                structure.get(
                    "block_count"
                )
                or 0
            )

            heading_count = int(
                structure.get(
                    "heading_count"
                )
                or 0
            )

            if body_length <= 0:
                raise WucPopulationRunnerError(
                    "WUC body length is invalid."
                )

            if body_word_count <= 0:
                raise WucPopulationRunnerError(
                    "WUC body word count is invalid."
                )

            if block_count <= 0:
                raise WucPopulationRunnerError(
                    "WUC block count is invalid."
                )

            total_body_length += (
                body_length
            )

            total_word_count += (
                body_word_count
            )

            total_block_count += (
                block_count
            )

            total_heading_count += (
                heading_count
            )

            # Evidence only. The full content_body is intentionally excluded.
            pass_records.append(
                {
                    "source_record_id":
                        source_record_id,

                    "document_id":
                        document.get(
                            "document_id"
                        ),

                    "content_id":
                        document.get(
                            "content_id"
                        ),

                    "workspace_id":
                        document.get(
                            "workspace_id"
                        ),

                    "canonical_url":
                        document.get(
                            "canonical_url"
                        ),

                    "title":
                        document.get(
                            "title"
                        ),

                    "h1":
                        document.get(
                            "h1"
                        ),

                    "content_hash":
                        document.get(
                            "content_hash"
                        ),

                    "body_length":
                        body_length,

                    "body_word_count":
                        body_word_count,

                    "block_count":
                        block_count,

                    "heading_count":
                        heading_count,

                    "udare_article_path":
                        descriptor.get(
                            "article_path"
                        ),

                    "udare_article_sha256":
                        descriptor.get(
                            "article_sha256"
                        ),

                    "article_validation_run_id":
                        descriptor.get(
                            "article_validation_run_id"
                        ),

                    "article_validation_certificate_id":
                        descriptor.get(
                            "article_validation_certificate_id"
                        ),

                    "complete_content_preserved":
                        True,

                    "content_reduction_performed":
                        False,

                    "summarization_performed":
                        False,

                    "truncation_performed":
                        False,

                    "word_count_limit_applied":
                        False,

                    "full_body_handoff_ready":
                        True,

                    "status":
                        "PASS",
                }
            )

        except Exception as exc:
            fail_records.append(
                {
                    "source_record_id":
                        source_record_id,

                    "workspace_id":
                        workspace_id,

                    "status":
                        "FAIL",

                    "error_type":
                        type(
                            exc
                        ).__name__,

                    "reason":
                        str(
                            exc
                        ),
                }
            )

    completed_at = _utc_now()

    input_count = len(
        descriptors
    )

    pass_count = len(
        pass_records
    )

    fail_count = len(
        fail_records
    )

    processed_count = (
        pass_count
        + fail_count
    )

    accounting_pass = (
        processed_count
        == input_count
    )

    unique_pass_ids = len(
        {
            str(
                record.get(
                    "source_record_id"
                )
            )
            for record in pass_records
        }
    )

    unique_fail_ids = len(
        {
            str(
                record.get(
                    "source_record_id"
                )
            )
            for record in fail_records
        }
    )

    certificate_status = (
        "CERTIFIED"
        if (
            accounting_pass
            and fail_count == 0
            and pass_count == input_count
        )
        else "NOT_CERTIFIED"
    )

    _write_jsonl(
        pass_manifest_path,
        pass_records,
    )

    _write_jsonl(
        fail_manifest_path,
        fail_records,
    )

    ledger = {
        "schema_version":
            "wuc_execution_ledger_v1",

        "runner_version":
            RUNNER_VERSION,

        "engine_version":
            WUC_ENGINE_VERSION,

        "run_id":
            normalized_run_id,

        "workspace_id":
            workspace_id,

        "started_at":
            started_at,

        "completed_at":
            completed_at,

        "input_count":
            input_count,

        "processed_count":
            processed_count,

        "pass_count":
            pass_count,

        "fail_count":
            fail_count,

        "accounting_pass":
            accounting_pass,

        "unique_pass_ids":
            unique_pass_ids,

        "unique_fail_ids":
            unique_fail_ids,

        "article_bodies_persisted":
            False,

        "intermediate_wuc_store_created":
            False,

        "uucd_documents_written":
            False,

        "runtime_registration_created":
            False,
    }

    report = {
        "schema_version":
            "wuc_population_report_v1",

        **ledger,

        "article_validation_run_id":
            contract.get(
                "article_validation_run_id"
            ),

        "article_validation_certificate_id":
            contract.get(
                "article_validation_certificate_id"
            ),

        "article_validation_pass_manifest":
            contract.get(
                "pass_manifest_path"
            ),

        "total_body_length":
            total_body_length,

        "total_word_count":
            total_word_count,

        "total_block_count":
            total_block_count,

        "total_heading_count":
            total_heading_count,

        "complete_content_preservation_rule":
            True,

        "content_reduction_allowed":
            False,

        "summarization_allowed":
            False,

        "truncation_allowed":
            False,

        "word_count_limit":
            None,

        "full_body_handoff_ready_count":
            pass_count,

        "evidence_paths": {
            "pass_manifest":
                str(
                    pass_manifest_path
                ),

            "fail_manifest":
                str(
                    fail_manifest_path
                ),

            "execution_ledger":
                str(
                    ledger_path
                ),

            "report":
                str(
                    report_path
                ),

            "certificate":
                str(
                    certificate_path
                ),
        },
    }

    certificate_core = {
        "schema_version":
            "wuc_certificate_v1",

        "certificate_status":
            certificate_status,

        "run_id":
            normalized_run_id,

        "workspace_id":
            workspace_id,

        "input_count":
            input_count,

        "pass_count":
            pass_count,

        "fail_count":
            fail_count,

        "accounting_pass":
            accounting_pass,

        "complete_content_preserved":
            (
                certificate_status
                == "CERTIFIED"
            ),

        "full_body_handoff_ready_count":
            pass_count,

        "article_bodies_persisted_by_wuc":
            False,

        "intermediate_wuc_store_created":
            False,

        "uucd_documents_written":
            False,

        "article_validation_certificate_id":
            contract.get(
                "article_validation_certificate_id"
            ),

        "runner_version":
            RUNNER_VERSION,

        "engine_version":
            WUC_ENGINE_VERSION,
    }

    certificate = {
        **certificate_core,

        "certificate_id":
            (
                "wuc_certificate_"
                + _sha256_json(
                    certificate_core
                )[
                    :24
                ]
            ),
    }

    _write_json(
        ledger_path,
        ledger,
    )

    _write_json(
        report_path,
        report,
    )

    _write_json(
        certificate_path,
        certificate,
    )

    return {
        "run_id":
            normalized_run_id,

        "workspace_id":
            workspace_id,

        "input_count":
            input_count,

        "processed_count":
            processed_count,

        "pass_count":
            pass_count,

        "fail_count":
            fail_count,

        "accounting_pass":
            accounting_pass,

        "certificate_status":
            certificate_status,

        "certificate_id":
            certificate[
                "certificate_id"
            ],

        "total_word_count":
            total_word_count,

        "full_body_handoff_ready_count":
            pass_count,

        "evidence_paths":
            report[
                "evidence_paths"
            ],

        "article_bodies_persisted_by_wuc":
            False,

        "intermediate_wuc_store_created":
            False,

        "uucd_documents_written":
            False,
    }
