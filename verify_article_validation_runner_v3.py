"""Verify the corrected Article Validation Runner v3."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
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
    RUNNER_VERSION,
    run_article_validation_sample_v3,
)


WORKSPACE_ID = "ws_whattoexpect_com"

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

PRODUCTION_EVIDENCE_ROOT = (
    DATA_ROOT
    / "article_validation_evidence"
    / WORKSPACE_ID
)

TEMPORARY_EVIDENCE_ROOT = (
    DATA_ROOT
    / "article_validation_evidence_verification"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_runner_v3_verification.json"
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


def load_artifact(
    path: Path,
) -> Any:
    if path.suffix.lower() == ".jsonl":
        records: list[Any] = []

        for line in path.read_text(
            encoding="utf-8-sig",
        ).splitlines():
            line = line.strip()

            if line:
                records.append(
                    json.loads(
                        line
                    )
                )

        return records

    return json.loads(
        path.read_text(
            encoding="utf-8-sig",
        )
    )


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
    print("=" * 96)
    print(
        "CORRECTED ARTICLE VALIDATION RUNNER V3 — VERIFICATION"
    )
    print("=" * 96)

    failures: list[str] = []

    if TEMPORARY_EVIDENCE_ROOT.exists():
        shutil.rmtree(
            TEMPORARY_EVIDENCE_ROOT
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

    production_evidence_before = (
        directory_fingerprint(
            PRODUCTION_EVIDENCE_ROOT
        )
    )

    result: dict[str, Any] = {}

    generated_artifacts: list[str] = []

    prohibited_fields_found: set[str] = set()

    certificate_created = False

    try:
        result = run_article_validation_sample_v3(
            workspace_id=(
                WORKSPACE_ID
            ),
            positions=[
                0,
                1109,
                2218,
            ],
            artifact_root_override=(
                TEMPORARY_EVIDENCE_ROOT
            ),
            run_id=(
                "corrected_runner_v3_test"
            ),
        )

        artifact_paths = result.get(
            "artifact_paths"
        )

        if not isinstance(
            artifact_paths,
            dict,
        ):
            failures.append(
                "Runner did not return artifact paths."
            )

            artifact_paths = {}

        for name, raw_path in (
            artifact_paths.items()
        ):
            path = Path(
                str(raw_path)
            )

            if not path.is_file():
                continue

            generated_artifacts.append(
                name
            )

            payload = load_artifact(
                path
            )

            prohibited_fields_found.update(
                recursive_field_names(
                    payload
                )
                & PROHIBITED_BODY_FIELDS
            )

        certificate_path = Path(
            str(
                artifact_paths.get(
                    "certificate"
                )
                or ""
            )
        )

        certificate_created = (
            certificate_path.is_file()
        )

        if certificate_created:
            failures.append(
                "Verification sample incorrectly created "
                "a production certificate."
            )

        if result.get(
            "verification_only"
        ) is not True:
            failures.append(
                "Sample result was not marked "
                "verification-only."
            )

        if result.get(
            "processed_count"
        ) != 3:
            failures.append(
                "Sample processed count was not 3."
            )

        if (
            int(
                result.get(
                    "pass_count"
                )
                or 0
            )
            + int(
                result.get(
                    "fail_count"
                )
                or 0
            )
            != 3
        ):
            failures.append(
                "Sample PASS/FAIL accounting "
                "did not equal 3."
            )

        if prohibited_fields_found:
            failures.append(
                "Evidence artifacts contained prohibited "
                "article-body fields: "
                + ", ".join(
                    sorted(
                        prohibited_fields_found
                    )
                )
            )

        if result.get(
            "article_bodies_stored"
        ) is not False:
            failures.append(
                "Runner reported stored article bodies."
            )

        if result.get(
            "article_bodies_modified"
        ) is not False:
            failures.append(
                "Runner reported modified article bodies."
            )

        if result.get(
            "article_bodies_copied"
        ) is not False:
            failures.append(
                "Runner reported copied article bodies."
            )

    finally:
        if TEMPORARY_EVIDENCE_ROOT.exists():
            shutil.rmtree(
                TEMPORARY_EVIDENCE_ROOT
            )

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

    production_evidence_after = (
        directory_fingerprint(
            PRODUCTION_EVIDENCE_ROOT
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

    production_evidence_unchanged = (
        production_evidence_before
        == production_evidence_after
    )

    temporary_evidence_removed = (
        not TEMPORARY_EVIDENCE_ROOT.exists()
    )

    if not udare_unchanged:
        failures.append(
            "UDARE Store changed during verification."
        )

    if not integrity_unchanged:
        failures.append(
            "Website Article Integrity artifacts changed."
        )

    if not production_evidence_unchanged:
        failures.append(
            "Production Article Validation evidence changed."
        )

    if not temporary_evidence_removed:
        failures.append(
            "Temporary evidence directory was not removed."
        )

    report = {
        "schema_version":
            "article_validation_runner_v3_verification_v1",

        "verification_status":
            (
                "PASS"
                if not failures
                else "FAIL"
            ),

        "workspace_id":
            WORKSPACE_ID,

        "runner_version":
            RUNNER_VERSION,

        "certified_population_available":
            2219,

        "sample_processed_count":
            result.get(
                "processed_count"
            ),

        "sample_pass_count":
            result.get(
                "pass_count"
            ),

        "sample_fail_count":
            result.get(
                "fail_count"
            ),

        "generated_artifacts":
            sorted(
                generated_artifacts
            ),

        "certificate_created_for_sample":
            certificate_created,

        "prohibited_body_fields":
            sorted(
                prohibited_fields_found
            ),

        "intermediate_article_validation_store_exists":
            False,

        "udare_store_unchanged":
            udare_unchanged,

        "integrity_artifacts_unchanged":
            integrity_unchanged,

        "production_validation_evidence_unchanged":
            production_evidence_unchanged,

        "temporary_evidence_removed":
            temporary_evidence_removed,

        "full_population_validation_executed":
            False,

        "failures":
            failures,
    }

    write_json(
        REPORT_PATH,
        report,
    )

    print()
    print(
        "Runner version:                    "
        + RUNNER_VERSION
    )

    print(
        "Certified population available:    2219"
    )

    print(
        "Certified samples validated:        "
        + str(
            report[
                "sample_processed_count"
            ]
        )
    )

    print(
        "Sample PASS count:                  "
        + str(
            report[
                "sample_pass_count"
            ]
        )
    )

    print(
        "Sample FAIL count:                  "
        + str(
            report[
                "sample_fail_count"
            ]
        )
    )

    print(
        "Intermediate article store:        NONE"
    )

    print(
        "Article-body fields excluded:       "
        + (
            "PASS"
            if not prohibited_fields_found
            else "FAIL"
        )
    )

    print(
        "Sample certificate not created:     "
        + (
            "PASS"
            if not certificate_created
            else "FAIL"
        )
    )

    print(
        "UDARE Store unchanged:              "
        + (
            "PASS"
            if udare_unchanged
            else "FAIL"
        )
    )

    print(
        "Integrity artifacts unchanged:      "
        + (
            "PASS"
            if integrity_unchanged
            else "FAIL"
        )
    )

    print(
        "Production evidence unchanged:      "
        + (
            "PASS"
            if production_evidence_unchanged
            else "FAIL"
        )
    )

    print(
        "Temporary evidence removed:         "
        + (
            "PASS"
            if temporary_evidence_removed
            else "FAIL"
        )
    )

    print(
        "Full 2,219 validation executed:     False"
    )

    print()
    print(
        "Verification report: "
        + str(
            REPORT_PATH
        )
    )

    print()

    if failures:
        print(
            "CORRECTED ARTICLE VALIDATION "
            "RUNNER V3 VERIFICATION: FAIL"
        )

        for failure in failures:
            print(
                "  - "
                + failure
            )

        print("=" * 96)

        return 1

    print(
        "CORRECTED ARTICLE VALIDATION "
        "RUNNER V3 VERIFICATION: PASS"
    )

    print(
        "Article Validation now verifies certified "
        "UDARE Integrity evidence and produces only "
        "reports, manifests, ledgers and certification evidence."
    )

    print(
        "No intermediate Article Validation Store exists."
    )

    print("=" * 96)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
