"""Canonical transient WUC batch worker with direct UUCD convergence."""

from __future__ import annotations

from typing import Any, Iterable

from backend.server.stores.universal_unified_content_document_convergence import (
    build_and_write_uucd_from_wuc_v1,
)
from backend.server.stores.website_unified_content_builder_v2 import (
    build_website_unified_content_document_v2,
)
from backend.server.stores.website_unified_content_certifier_v2 import (
    certify_website_unified_content_document_v2,
)
from backend.server.stores.website_unified_content_handoff_v2 import (
    load_article_validation_pass_contract_v2,
    load_transient_wuc_source_v2,
    select_article_validation_pass_records_v2,
)
from backend.server.stores.website_unified_content_verifier_v2 import (
    verify_website_unified_content_document_v2,
)


WORKER_VERSION = (
    "website_unified_content_batch_worker_v2_"
    "article_validation_pass_direct_uucd"
)


def run_website_unified_content_batch_v2(
    *,
    workspace_id: str,
    batch_id: str = "",
    batch_index: int = 0,
    batch_count: int = 1,
    assigned_html_ids: Iterable[str] | None = None,
    assigned_article_ids: Iterable[str] | None = None,
    **_: Any,
) -> dict[str, Any]:
    requested_ids = (
        assigned_article_ids
        if assigned_article_ids is not None
        else assigned_html_ids
    )

    contract = (
        load_article_validation_pass_contract_v2(
            workspace_id
        )
    )

    records = (
        select_article_validation_pass_records_v2(
            contract=contract,
            assigned_article_ids=requested_ids,
        )
    )

    attempted = 0
    succeeded = 0
    failed = 0

    successes: list[
        dict[str, Any]
    ] = []

    errors: list[
        dict[str, Any]
    ] = []

    for record in records:
        attempted += 1

        record_id = str(
            record.get(
                "source_record_id"
            )
            or record.get(
                "html_id"
            )
            or record.get(
                "document_id"
            )
            or ""
        )

        try:
            transient_source = (
                load_transient_wuc_source_v2(
                    workspace_id=workspace_id,
                    pass_record=record,
                    article_validation_contract=contract,
                )
            )

            document = (
                build_website_unified_content_document_v2(
                    certified_article=(
                        transient_source
                    )
                )
            )

            verification = (
                verify_website_unified_content_document_v2(
                    document=document
                )
            )

            if (
                verification.get(
                    "passed"
                )
                is not True
            ):
                raise ValueError(
                    "WUC verification failed: "
                    + ", ".join(
                        str(
                            value
                        )
                        for value in (
                            verification.get(
                                "errors"
                            )
                            or []
                        )
                    )
                )

            certified_document = (
                certify_website_unified_content_document_v2(
                    document=document,
                    verification_result=(
                        verification
                    ),
                )
            )

            convergence = (
                build_and_write_uucd_from_wuc_v1(
                    certified_document
                )
            )

            if (
                convergence.get(
                    "ok"
                )
                is not True
            ):
                raise RuntimeError(
                    "UUCD convergence did not return ok=True."
                )

            uucd = convergence.get(
                "uucd"
            )

            if not isinstance(
                uucd,
                dict,
            ):
                raise RuntimeError(
                    "UUCD convergence returned an invalid document."
                )

            succeeded += 1

            successes.append(
                {
                    "source_record_id":
                        record_id,

                    "document_id":
                        uucd.get(
                            "document_id"
                        ),

                    "url":
                        certified_document.get(
                            "canonical_url"
                        )
                        or certified_document.get(
                            "url"
                        ),

                    "uucd_path":
                        convergence.get(
                            "uucd_path"
                        ),

                    "wuc_persistence_mode":
                        "TRANSIENT",

                    "intermediate_wuc_store_created":
                        False,
                }
            )

        except Exception as exc:
            failed += 1

            errors.append(
                {
                    "source_record_id":
                        record_id,

                    "error_type":
                        type(
                            exc
                        ).__name__,

                    "error":
                        str(
                            exc
                        ),
                }
            )

    return {
        "ok":
            failed == 0,

        "worker_version":
            WORKER_VERSION,

        "workspace_id":
            workspace_id,

        "batch_id":
            batch_id,

        "batch_index":
            int(
                batch_index
            ),

        "batch_count":
            int(
                batch_count
            ),

        "article_validation_run_id":
            contract.get(
                "run_id"
            ),

        "article_validation_certificate_id":
            contract.get(
                "certificate_id"
            ),

        "input_pass_manifest":
            contract.get(
                "pass_manifest_path"
            ),

        "processing": {
            "assigned":
                len(
                    records
                ),

            "attempted":
                attempted,

            "succeeded":
                succeeded,

            "failed":
                failed,
        },

        "success_sample":
            successes[:10],

        "error_sample":
            errors[:25],

        "wuc_persistence_mode":
            "TRANSIENT",

        "legacy_article_validation_store_used":
            False,

        "legacy_wuc_store_used":
            False,

        "direct_uucd_convergence":
            True,

        "intermediate_wuc_store_created":
            False,
    }
