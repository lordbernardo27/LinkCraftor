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

    print()
    print("=" * 82)
    print(
        "WEBSITE ARTICLE INTEGRITY — RUNTIME REGISTRATION"
    )
    print("=" * 82)
    print(
        f"Pipeline:                    "
        f"{result['pipeline']}"
    )
    print(
        f"Handlers registered:         "
        f"{result['registered_count']}"
    )

    for job_type in result[
        "registered_job_types"
    ]:
        print(
            f"  - {job_type}"
        )

    print(
        f"Persistent registry:         "
        f"{result['persistent_registry_path']}"
    )
    print(
        f"Registry SHA-256:            "
        f"{result['registry "registered_job_types"
    ]:
        print(
            f"  - {job_type}"
        )

    print(
        f"Persistent registry:         "
        f"{result['persistent_registry_path']}"
    )
    print(
_sha256']}"
    )
    print(
        "Automatic UDARE trigger:     "
        "NOT INCLUDED IN THIS STEP"
    )
    print(
        f"Registration report:         "
        f"{REPORT_PATH}"
    )
    print("=" * 82)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
