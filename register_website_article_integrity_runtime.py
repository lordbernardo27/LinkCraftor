"""Persist Website Article Integrity runtime registrations."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.integrity.website_article_integrity.website_article_integrity_runtime_registration import (
    register_website_article_integrity_runtime_handlers,
)


REPORT_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "universal_runtime_registration"
    / "website_article_integrity"
    / "website_article_integrity_registration.json"
)


def main() -> int:
    result = (
        register_website_article_integrity_runtime_handlers(
            persist=True,
            replace=True,
        )
    )

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    registered_job_types = result.get(
        "registered_job_types",
        [],
    )

    persistent_registry_path = result.get(
        "persistent_registry_path",
        "",
    )

    registry_sha256 = result.get(
        "registry_sha256",
        "",
    )

    print()
    print("=" * 82)
    print(
        "WEBSITE ARTICLE INTEGRITY — RUNTIME REGISTRATION"
    )
    print("=" * 82)

    print(
        "Pipeline:                    "
        + str(
            result.get(
                "pipeline",
                "",
            )
        )
    )

    print(
        "Handlers registered:         "
        + str(
            result.get(
                "registered_count",
                0,
            )
        )
    )

    for job_type in registered_job_types:
        print(
            "  - "
            + str(job_type)
        )

    print(
        "Persistent registry:         "
        + str(
            persistent_registry_path
        )
    )

    print(
        "Registry SHA-256:            "
        + str(
            registry_sha256
        )
    )

    print(
        "Automatic UDARE trigger:     "
        "NOT INCLUDED IN THIS STEP"
    )

    print(
        "Registration report:         "
        + str(
            REPORT_PATH
        )
    )

    print("=" * 82)

    if (
        result.get("ok") is not True
        or result.get(
            "registered_count"
        )
        != 6
        or len(
            registered_job_types
        )
        != 6
    ):
        print(
            "WEBSITE ARTICLE INTEGRITY "
            "RUNTIME REGISTRATION: FAIL"
        )

        return 1

    print(
        "WEBSITE ARTICLE INTEGRITY "
        "RUNTIME REGISTRATION: PASS"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
