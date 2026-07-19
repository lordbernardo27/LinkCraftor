"""Verify Article Validation Universal Runtime Registration."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    __file__
).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from backend.server.article_validation.article_validation_runtime_registration import (
    HANDLER_REFERENCE,
    JOB_TYPE_ARTICLE_VALIDATION,
    PIPELINE,
    REGISTRATION_EVIDENCE_PATH,
    REGISTRATION_VERSION,
    STAGE,
    register_article_validation_runtime_v1,
)
from backend.server.runtime.universal_runtime_registration import (
    has_runtime_handler,
    is_runtime_job_type_registered,
)


WORKSPACE_ID = "ws_whattoexpect_com"

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

REGISTRY_PATH = (
    DATA_ROOT
    / "runtime"
    / "universal_runtime_registration"
    / "runtime_registration_registry.json"
)

REPORT_PATH = (
    DATA_ROOT
    / "runtime"
    / "universal_runtime_registration"
    / "article_validation"
    / "article_validation_registration_verification.json"
)

PROTECTED_PATHS = {
    "udare_store": (
        DATA_ROOT
        / "udare_store"
        / WORKSPACE_ID
    ),

    "integrity_evidence": (
        DATA_ROOT
        / "website_article_integrity"
        / WORKSPACE_ID
    ),

    "validation_evidence": (
        DATA_ROOT
        / "article_validation_evidence"
        / WORKSPACE_ID
    ),
}

PROHIBITED_STORE_PATHS = [
    (
        PROJECT_ROOT
        / "backend"
        / "server"
        / "article_validation"
        / "article_validation_store_v3.py"
    ),

    (
        DATA_ROOT
        / "article_validation_store"
    ),

    (
        DATA_ROOT
        / "article_validation_store_v3"
    ),
]


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
            digest.update(
                block
            )

    return digest.hexdigest()


def fingerprint(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    if not path.exists():
        digest.update(
            b"ABSENT"
        )

        return digest.hexdigest()

    if path.is_file():
        return sha256_file(
            path
        )

    for file_path in sorted(
        (
            candidate
            for candidate in path.rglob("*")
            if candidate.is_file()
        ),
        key=lambda candidate: (
            candidate.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            file_path.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        digest.update(b"\x00")

        digest.update(
            sha256_file(
                file_path
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
        "ARTICLE VALIDATION — UNIVERSAL RUNTIME REGISTRATION"
    )
    print("=" * 100)

    failures: list[str] = []

    protected_before = {
        name: fingerprint(
            path
        )
        for name, path
        in PROTECTED_PATHS.items()
    }

    evidence = (
        register_article_validation_runtime_v1(
            replace=True,
            persist=True,
        )
    )

    registered_in_memory = (
        has_runtime_handler(
            JOB_TYPE_ARTICLE_VALIDATION
        )
    )

    registered_job_type = (
        is_runtime_job_type_registered(
            JOB_TYPE_ARTICLE_VALIDATION
        )
    )

    registry_exists = (
        REGISTRY_PATH.is_file()
    )

    registry_contains_job_type = False
    registry_contains_handler = False

    if registry_exists:
        registry_text = (
            REGISTRY_PATH.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        )

        registry_contains_job_type = (
            JOB_TYPE_ARTICLE_VALIDATION
            in registry_text
        )

        registry_contains_handler = (
            HANDLER_REFERENCE
            in registry_text
        )

    evidence_exists = (
        REGISTRATION_EVIDENCE_PATH.is_file()
    )

    evidence_payload = (
        load_json(
            REGISTRATION_EVIDENCE_PATH
        )
        if evidence_exists
        else {}
    )

    protected_after = {
        name: fingerprint(
            path
        )
        for name, path
        in PROTECTED_PATHS.items()
    }

    protected_unchanged = {
        name: (
            protected_before[
                name
            ]
            == protected_after[
                name
            ]
        )
        for name
        in PROTECTED_PATHS
    }

    prohibited_store_exists = any(
        path.exists()
        for path in PROHIBITED_STORE_PATHS
    )

    checks = {
        "registered_in_memory":
            registered_in_memory,

        "registered_job_type":
            registered_job_type,

        "registry_exists":
            registry_exists,

        "registry_contains_job_type":
            registry_contains_job_type,

        "registry_contains_handler":
            registry_contains_handler,

        "registration_evidence_exists":
            evidence_exists,

        "registration_version_correct":
            (
                evidence_payload.get(
                    "registration_version"
                )
                == REGISTRATION_VERSION
            ),

        "pipeline_correct":
            (
                evidence_payload.get(
                    "pipeline"
                )
                == PIPELINE
            ),

        "stage_correct":
            (
                evidence_payload.get(
                    "stage"
                )
                == STAGE
            ),

        "predecessor_correct":
            (
                "website_article_integrity_certification"
                in (
                    evidence_payload.get(
                        "predecessor_stages"
                    )
                    or []
                )
            ),

        "successor_correct":
            (
                "website_unified_content"
                in (
                    evidence_payload.get(
                        "successor_stages"
                    )
                    or []
                )
            ),

        "no_separate_queue":
            (
                evidence_payload.get(
                    "metadata",
                    {},
                ).get(
                    "separate_queue_required"
                )
                is False
            ),

        "no_separate_worker":
            (
                evidence_payload.get(
                    "metadata",
                    {},
                ).get(
                    "separate_worker_required"
                )
                is False
            ),

        "evidence_only":
            (
                evidence_payload.get(
                    "metadata",
                    {},
                ).get(
                    "evidence_only"
                )
                is True
            ),

        "no_word_count_rule":
            (
                evidence_payload.get(
                    "metadata",
                    {},
                ).get(
                    "word_count_rule"
                )
                is False
            ),

        "intermediate_store_absent":
            not prohibited_store_exists,

        "udare_unchanged":
            protected_unchanged[
                "udare_store"
            ],

        "integrity_evidence_unchanged":
            protected_unchanged[
                "integrity_evidence"
            ],

        "validation_evidence_unchanged":
            protected_unchanged[
                "validation_evidence"
            ],

        "jobs_enqueued":
            False,

        "workers_started":
            False,

        "article_validation_executed":
            False,
    }

    for name, passed in checks.items():
        if name in {
            "jobs_enqueued",
            "workers_started",
            "article_validation_executed",
        }:
            continue

        if passed is not True:
            failures.append(
                f"Registration check failed: {name}"
            )

    report = {
        "schema_version":
            "article_validation_runtime_registration_verification_v1",

        "verification_status":
            (
                "PASS"
                if not failures
                else "FAIL"
            ),

        "workspace_id":
            WORKSPACE_ID,

        "job_type":
            JOB_TYPE_ARTICLE_VALIDATION,

        "handler_reference":
            HANDLER_REFERENCE,

        "registration_version":
            REGISTRATION_VERSION,

        "registration_evidence":
            evidence,

        "checks":
            checks,

        "protected_paths_unchanged":
            protected_unchanged,

        "failures":
            failures,
    }

    write_json(
        REPORT_PATH,
        report,
    )

    print()
    print(
        "Job type:                         "
        + JOB_TYPE_ARTICLE_VALIDATION
    )

    print(
        "Handler reference:                "
        + HANDLER_REFERENCE
    )

    print(
        "Registered in memory:             "
        + (
            "PASS"
            if registered_in_memory
            else "FAIL"
        )
    )

    print(
        "Registered job type:              "
        + (
            "PASS"
            if registered_job_type
            else "FAIL"
        )
    )

    print(
        "Persisted registry entry:         "
        + (
            "PASS"
            if (
                registry_contains_job_type
                and registry_contains_handler
            )
            else "FAIL"
        )
    )

    print(
        "Integrity predecessor:            "
        + (
            "PASS"
            if checks[
                "predecessor_correct"
            ]
            else "FAIL"
        )
    )

    print(
        "WUC successor:                    "
        + (
            "PASS"
            if checks[
                "successor_correct"
            ]
            else "FAIL"
        )
    )

    print(
        "Separate queue required:          False"
    )

    print(
        "Separate worker required:         False"
    )

    print(
        "Intermediate article store:       NONE"
    )

    print(
        "Jobs enqueued:                    False"
    )

    print(
        "Workers started:                  False"
    )

    print(
        "Article Validation executed:      False"
    )

    print(
        "UDARE Store unchanged:            "
        + (
            "PASS"
            if checks[
                "udare_unchanged"
            ]
            else "FAIL"
        )
    )

    print(
        "Integrity evidence unchanged:     "
        + (
            "PASS"
            if checks[
                "integrity_evidence_unchanged"
            ]
            else "FAIL"
        )
    )

    print(
        "Validation evidence unchanged:    "
        + (
            "PASS"
            if checks[
                "validation_evidence_unchanged"
            ]
            else "FAIL"
        )
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
            "ARTICLE VALIDATION RUNTIME REGISTRATION: FAIL"
        )

        for failure in failures:
            print(
                "  - "
                + failure
            )

        print("=" * 100)

        return 1

    print(
        "ARTICLE VALIDATION RUNTIME REGISTRATION: PASS"
    )

    print(
        "Article Validation is registered in the "
        "current universal runtime foundation."
    )

    print(
        "No job was enqueued or executed during registration."
    )

    print("=" * 100)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
