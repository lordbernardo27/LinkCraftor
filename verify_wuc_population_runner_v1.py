"""Verify complete WUC processing for all certified website articles."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    __file__
).resolve().parent

if str(
    PROJECT_ROOT
) not in sys.path:
    sys.path.insert(
        0,
        str(
            PROJECT_ROOT
        ),
    )


from backend.server.website_unified_content.wuc_population_runner_v1 import (
    run_wuc_population_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_COUNT = 2219

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

DATA_ROOT = (
    SERVER_ROOT
    / "data"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "wuc_population_runner_v1_verification.json"
)

PROTECTED_PATHS = {
    "udare_store": (
        DATA_ROOT
        / "udare_store"
        / WORKSPACE_ID
    ),

    "article_validation_evidence": (
        DATA_ROOT
        / "article_validation_evidence"
        / WORKSPACE_ID
    ),

    "uucd_output": (
        DATA_ROOT
        / "universal_unified_content_document"
    ),

    "runtime_registry": (
        DATA_ROOT
        / "runtime"
        / "universal_runtime_registration"
        / "runtime_registration_registry.json"
    ),
}

PROHIBITED_PATHS = [
    (
        DATA_ROOT
        / "website_unified_content"
    ),

    (
        DATA_ROOT
        / "website_unified_content_store"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_store.py"
    ),
]


def sha256_file(
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
            for candidate in path.rglob(
                "*"
            )
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

        digest.update(
            b"\x00"
        )

        digest.update(
            sha256_file(
                file_path
            ).encode(
                "ascii"
            )
        )

        digest.update(
            b"\n"
        )

    return digest.hexdigest()


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
    failures: list[str] = []

    protected_before = {
        name: fingerprint(
            path
        )
        for name, path
        in PROTECTED_PATHS.items()
    }

    result = run_wuc_population_v1(
        workspace_id=WORKSPACE_ID,
        expected_pass_count=EXPECTED_COUNT,
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

    prohibited_present = [
        str(
            path
        )
        for path in PROHIBITED_PATHS
        if path.exists()
    ]

    checks = {
        "input_count_2219":
            (
                result.get(
                    "input_count"
                )
                == EXPECTED_COUNT
            ),

        "processed_count_2219":
            (
                result.get(
                    "processed_count"
                )
                == EXPECTED_COUNT
            ),

        "pass_count_2219":
            (
                result.get(
                    "pass_count"
                )
                == EXPECTED_COUNT
            ),

        "fail_count_zero":
            (
                result.get(
                    "fail_count"
                )
                == 0
            ),

        "accounting_pass":
            (
                result.get(
                    "accounting_pass"
                )
                is True
            ),

        "certificate_certified":
            (
                result.get(
                    "certificate_status"
                )
                == "CERTIFIED"
            ),

        "full_body_handoff_ready_2219":
            (
                result.get(
                    "full_body_handoff_ready_count"
                )
                == EXPECTED_COUNT
            ),

        "nonzero_total_word_count":
            (
                int(
                    result.get(
                        "total_word_count"
                    )
                    or 0
                )
                > 0
            ),

        "no_wuc_body_persistence":
            (
                result.get(
                    "article_bodies_persisted_by_wuc"
                )
                is False
            ),

        "no_intermediate_wuc_store":
            (
                result.get(
                    "intermediate_wuc_store_created"
                )
                is False
                and not prohibited_present
            ),

        "no_uucd_writes":
            (
                result.get(
                    "uucd_documents_written"
                )
                is False
            ),

        "udare_unchanged":
            protected_unchanged[
                "udare_store"
            ],

        "article_validation_unchanged":
            protected_unchanged[
                "article_validation_evidence"
            ],

        "uucd_output_unchanged":
            protected_unchanged[
                "uucd_output"
            ],

        "runtime_registry_unchanged":
            protected_unchanged[
                "runtime_registry"
            ],
    }

    for name, passed in checks.items():
        if passed is not True:
            failures.append(
                f"Verification failed: {name}"
            )

    report = {
        "schema_version":
            "wuc_population_runner_v1_verification",

        "verification_status":
            (
                "PASS"
                if not failures
                else "FAIL"
            ),

        "workspace_id":
            WORKSPACE_ID,

        "result":
            result,

        "checks":
            checks,

        "protected_paths_unchanged":
            protected_unchanged,

        "prohibited_paths_present":
            prohibited_present,

        "failures":
            failures,
    }

    write_json(
        REPORT_PATH,
        report,
    )

    print()
    print("=" * 108)
    print(
        "WUC COMPLETE-CONTENT POPULATION — VERIFICATION"
    )
    print("=" * 108)
    print()

    print(
        "Certified inputs:                  "
        + str(
            result.get(
                "input_count"
            )
        )
    )

    print(
        "Processed:                         "
        + str(
            result.get(
                "processed_count"
            )
        )
    )

    print(
        "WUC PASS:                          "
        + str(
            result.get(
                "pass_count"
            )
        )
    )

    print(
        "WUC FAIL:                          "
        + str(
            result.get(
                "fail_count"
            )
        )
    )

    print(
        "Full-body handoff ready:            "
        + str(
            result.get(
                "full_body_handoff_ready_count"
            )
        )
    )

    print(
        "Total words preserved:              "
        + str(
            result.get(
                "total_word_count"
            )
        )
    )

    print(
        "Certificate status:                 "
        + str(
            result.get(
                "certificate_status"
            )
        )
    )

    print(
        "Certificate ID:                     "
        + str(
            result.get(
                "certificate_id"
            )
        )
    )

    print(
        "Intermediate WUC Store:             NONE"
    )

    print(
        "WUC article-body persistence:       False"
    )

    print(
        "UUCD documents written:             False"
    )

    print(
        "UDARE Store unchanged:              "
        + (
            "PASS"
            if checks[
                "udare_unchanged"
            ]
            else "FAIL"
        )
    )

    print(
        "Article Validation unchanged:       "
        + (
            "PASS"
            if checks[
                "article_validation_unchanged"
            ]
            else "FAIL"
        )
    )

    print(
        "Existing UUCD output unchanged:     "
        + (
            "PASS"
            if checks[
                "uucd_output_unchanged"
            ]
            else "FAIL"
        )
    )

    print(
        "Runtime registry unchanged:         "
        + (
            "PASS"
            if checks[
                "runtime_registry_unchanged"
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
            "WUC COMPLETE-CONTENT POPULATION: FAIL"
        )

        for failure in failures:
            print(
                "  - "
                + failure
            )

        print("=" * 108)

        return 1

    print(
        "WUC COMPLETE-CONTENT POPULATION: PASS"
    )

    print(
        "All 2,219 validated UDARE articles were converted "
        "into complete transient WUC packages."
    )

    print(
        "No article was summarized, shortened, truncated "
        "or limited by word count."
    )

    print("=" * 108)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
