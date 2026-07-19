"""Execute and verify Article Validation for the complete certified population."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.article_validation.article_validation_runner_v3 import (
    PROHIBITED_BODY_FIELDS,
    run_article_validation_population_v3,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_ACTIVE_COUNT = 2219

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

UDARE_ROOT = (
    DATA_ROOT
    / "udare_store"
    / WORKSPACE_ID
)

INTEGRITY_ROOT = (
    DATA_ROOT
    / "website_article_integrity"
    / WORKSPACE_ID
)

VERIFICATION_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_population_v3_verification.json"
)

INCORRECT_STORE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "article_validation"
    / "article_validation_store_v3.py"
)


def sha256_file(
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


def directory_fingerprint(
    root: Path,
) -> str:
    digest = hashlib.sha256()

    if not root.exists():
        digest.update(
            b"ABSENT"
        )

        return digest.hexdigest()

    for path in sorted(
        (
            candidate
            for candidate in root.rglob("*")
            if candidate.is_file()
        ),
        key=lambda candidate: (
            candidate.as_posix()
        ),
    ):
        digest.update(
            path.relative_to(
                root
            ).as_posix().encode(
                "utf-8"
            )
        )

        digest.update(b"\x00")

        digest.update(
            sha256_file(
                path
            ).encode(
                "ascii"
            )
        )

        digest.update(b"\n")

    return digest.hexdigest()


def load_json(
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


def load_jsonl(
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
                    "JSONL record is not an object at "
                    f"line {line_number}: {path}"
                )

            records.append(
                value
            )

    return records


def recursive_field_names(
    value: Any,
) -> set[str]:
    names: set[str] = set()

    if isinstance(
        value,
        dict,
    ):
        for key, item in value.items():
            names.add(
                str(key).casefold()
            )

            names.update(
                recursive_field_names(
                    item
                )
            )

    elif isinstance(
        value,
        list,
    ):
        for item in value:
            names.update(
                recursive_field_names(
                    item
                )
            )

    return names


def write_json(
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


def main() -> int:
    print()
    print("=" * 100)
    print(
        "ARTICLE VALIDATION — COMPLETE CERTIFIED POPULATION EXECUTION"
    )
    print("=" * 100)

    failures: list[str] = []

    if INCORRECT_STORE_PATH.exists():
        raise RuntimeError(
            "Rejected Article Validation Store v3 still exists."
        )

    udare_before = (
        directory_fingerprint(
            UDARE_ROOT
        )
    )

    integrity_before = (
        directory_fingerprint(
            INTEGRITY_ROOT
        )
    )

    run_id = (
        "article_validation_"
        + datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%dT%H%M%SZ"
        )
    )

    result = (
        run_article_validation_population_v3(
            workspace_id=(
                WORKSPACE_ID
            ),
            expected_active_count=(
                EXPECTED_ACTIVE_COUNT
            ),
            run_id=run_id,
            batch_size=100,
        )
    )

    artifact_paths_raw = result.get(
        "artifact_paths"
    )

    if not isinstance(
        artifact_paths_raw,
        dict,
    ):
        raise RuntimeError(
            "Runner did not return artifact paths."
        )

    artifact_paths = {
        name: Path(
            str(path)
        )
        for name, path
        in artifact_paths_raw.items()
    }

    required_artifacts = (
        "pass_manifest",
        "failure_manifest",
        "execution_ledger",
        "report",
        "certificate",
        "evidence_manifest",
    )

    missing_artifacts = [
        name
        for name in required_artifacts
        if (
            name not in artifact_paths
            or not artifact_paths[
                name
            ].is_file()
        )
    ]

    if missing_artifacts:
        failures.append(
            "Missing required evidence artifacts: "
            + ", ".join(
                missing_artifacts
            )
        )

    pass_records = (
        load_jsonl(
            artifact_paths[
                "pass_manifest"
            ]
        )
        if artifact_paths.get(
            "pass_manifest"
        )
        and artifact_paths[
            "pass_manifest"
        ].is_file()
        else []
    )

    failure_records = (
        load_jsonl(
            artifact_paths[
                "failure_manifest"
            ]
        )
        if artifact_paths.get(
            "failure_manifest"
        )
        and artifact_paths[
            "failure_manifest"
        ].is_file()
        else []
    )

    execution_ledger = (
        load_json(
            artifact_paths[
                "execution_ledger"
            ]
        )
        if artifact_paths.get(
            "execution_ledger"
        )
        and artifact_paths[
            "execution_ledger"
        ].is_file()
        else {}
    )

    validation_report = (
        load_json(
            artifact_paths[
                "report"
            ]
        )
        if artifact_paths.get(
            "report"
        )
        and artifact_paths[
            "report"
        ].is_file()
        else {}
    )

    certificate = (
        load_json(
            artifact_paths[
                "certificate"
            ]
        )
        if artifact_paths.get(
            "certificate"
        )
        and artifact_paths[
            "certificate"
        ].is_file()
        else {}
    )

    evidence_manifest = (
        load_json(
            artifact_paths[
                "evidence_manifest"
            ]
        )
        if artifact_paths.get(
            "evidence_manifest"
        )
        and artifact_paths[
            "evidence_manifest"
        ].is_file()
        else {}
    )

    processed_count = int(
        result.get(
            "processed_count"
        )
        or 0
    )

    pass_count = int(
        result.get(
            "pass_count"
        )
        or 0
    )

    fail_count = int(
        result.get(
            "fail_count"
        )
        or 0
    )

    if processed_count != EXPECTED_ACTIVE_COUNT:
        failures.append(
            "Processed count was not 2,219."
        )

    if (
        pass_count
        + fail_count
        != EXPECTED_ACTIVE_COUNT
    ):
        failures.append(
            "PASS/FAIL accounting did not equal 2,219."
        )

    if len(
        pass_records
    ) != pass_count:
        failures.append(
            "PASS manifest count does not match "
            "the reported PASS count."
        )

    if len(
        failure_records
    ) != fail_count:
        failures.append(
            "Failure manifest count does not match "
            "the reported FAIL count."
        )

    all_records = (
        pass_records
        + failure_records
    )

    identifiers = [
        str(
            record.get(
                "source_record_id"
            )
            or ""
        )
        for record in all_records
    ]

    if len(identifiers) != EXPECTED_ACTIVE_COUNT:
        failures.append(
            "Manifest record count was not 2,219."
        )

    if len(
        set(identifiers)
    ) != EXPECTED_ACTIVE_COUNT:
        failures.append(
            "Article Validation identifiers were not unique."
        )

    all_artifact_payloads = [
        pass_records,
        failure_records,
        execution_ledger,
        validation_report,
        certificate,
        evidence_manifest,
    ]

    prohibited_fields_found: set[str] = set()

    for payload in all_artifact_payloads:
        prohibited_fields_found.update(
            recursive_field_names(
                payload
            )
            & PROHIBITED_BODY_FIELDS
        )

    if prohibited_fields_found:
        failures.append(
            "Evidence contained prohibited article-body fields: "
            + ", ".join(
                sorted(
                    prohibited_fields_found
                )
            )
        )

    if certificate.get(
        "certification_status"
    ) != "CERTIFIED":
        failures.append(
            "Article Validation certificate status "
            "was not CERTIFIED."
        )

    if certificate.get(
        "processed_count"
    ) != EXPECTED_ACTIVE_COUNT:
        failures.append(
            "Certificate processed count was not 2,219."
        )

    if execution_ledger.get(
        "status"
    ) != "COMPLETED":
        failures.append(
            "Execution ledger status was not COMPLETED."
        )

    for record in pass_records:
        if record.get(
            "article_validation_status"
        ) != "PASS":
            failures.append(
                "PASS manifest contains a non-PASS record."
            )

            break

        if record.get(
            "eligible_for_wuc"
        ) is not True:
            failures.append(
                "PASS manifest contains a record not "
                "eligible for WUC."
            )

            break

    for record in failure_records:
        if record.get(
            "article_validation_status"
        ) != "FAIL":
            failures.append(
                "Failure manifest contains a non-FAIL record."
            )

            break

        if record.get(
            "eligible_for_wuc"
        ) is not False:
            failures.append(
                "Failure manifest contains a record "
                "eligible for WUC."
            )

            break

    udare_after = (
        directory_fingerprint(
            UDARE_ROOT
        )
    )

    integrity_after = (
        directory_fingerprint(
            INTEGRITY_ROOT
        )
    )

    udare_unchanged = (
        udare_before
        == udare_after
    )

    integrity_unchanged = (
        integrity_before
        == integrity_after
    )

    if not udare_unchanged:
        failures.append(
            "UDARE Store changed during Article Validation."
        )

    if not integrity_unchanged:
        failures.append(
            "Website Article Integrity artifacts changed "
            "during Article Validation."
        )

    verification_report = {
        "schema_version":
            "article_validation_population_v3_verification_v1",

        "verification_status":
            (
                "PASS"
                if not failures
                else "FAIL"
            ),

        "workspace_id":
            WORKSPACE_ID,

        "run_id":
            run_id,

        "expected_active_count":
            EXPECTED_ACTIVE_COUNT,

        "processed_count":
            processed_count,

        "pass_count":
            pass_count,

        "fail_count":
            fail_count,

        "pass_manifest_count":
            len(
                pass_records
            ),

        "failure_manifest_count":
            len(
                failure_records
            ),

        "unique_identifier_count":
            len(
                set(identifiers)
            ),

        "certificate_id":
            certificate.get(
                "certificate_id"
            ),

        "certificate_status":
            certificate.get(
                "certification_status"
            ),

        "evidence_root_sha256":
            evidence_manifest.get(
                "evidence_root_sha256"
            ),

        "udare_store_unchanged":
            udare_unchanged,

        "integrity_artifacts_unchanged":
            integrity_unchanged,

        "intermediate_article_store_created":
            False,

        "article_bodies_stored":
            False,

        "article_bodies_modified":
            False,

        "article_bodies_copied":
            False,

        "prohibited_body_fields":
            sorted(
                prohibited_fields_found
            ),

        "artifact_paths":
            {
                name: str(path)
                for name, path
                in artifact_paths.items()
            },

        "failures":
            failures,
    }

    write_json(
        VERIFICATION_REPORT_PATH,
        verification_report,
    )

    print()
    print(
        "Run ID:                           "
        + run_id
    )

    print(
        "Certified active input count:      "
        + str(
            EXPECTED_ACTIVE_COUNT
        )
    )

    print(
        "Processed count:                   "
        + str(
            processed_count
        )
    )

    print(
        "Article Validation PASS count:     "
        + str(
            pass_count
        )
    )

    print(
        "Article Validation FAIL count:     "
        + str(
            fail_count
        )
    )

    print(
        "PASS/FAIL accounting:              "
        + (
            "PASS"
            if (
                pass_count
                + fail_count
                == EXPECTED_ACTIVE_COUNT
            )
            else "FAIL"
        )
    )

    print(
        "Unique article identifiers:        "
        + str(
            len(
                set(identifiers)
            )
        )
    )

    print(
        "Article-body fields excluded:      "
        + (
            "PASS"
            if not prohibited_fields_found
            else "FAIL"
        )
    )

    print(
        "UDARE Store unchanged:             "
        + (
            "PASS"
            if udare_unchanged
            else "FAIL"
        )
    )

    print(
        "Integrity artifacts unchanged:     "
        + (
            "PASS"
            if integrity_unchanged
            else "FAIL"
        )
    )

    print(
        "Intermediate article store:        NONE"
    )

    print(
        "Certificate status:                "
        + str(
            certificate.get(
                "certification_status"
            )
        )
    )

    print(
        "Certificate ID:                    "
        + str(
            certificate.get(
                "certificate_id"
            )
        )
    )

    print()
    print(
        "Verification report: "
        + str(
            VERIFICATION_REPORT_PATH
        )
    )

    print()

    if failures:
        print(
            "ARTICLE VALIDATION COMPLETE "
            "POPULATION VERIFICATION: FAIL"
        )

        for failure in failures:
            print(
                "  - "
                + failure
            )

        print("=" * 100)

        return 1

    print(
        "ARTICLE VALIDATION COMPLETE "
        "POPULATION VERIFICATION: PASS"
    )

    print(
        "All 2,219 Integrity-certified active UDARE "
        "articles were verified and validated."
    )

    print(
        "Only evidence, manifests, reports and a certificate "
        "were created."
    )

    print(
        "No intermediate article store or article-body copy exists."
    )

    print("=" * 100)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
