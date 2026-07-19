from __future__ import annotations

import hashlib
import json
from pathlib import Path


WORKSPACE_ID = "ws_whattoexpect_com"

STORE_PATH = Path(
    "backend/server/data/raw_website_html/"
    "raw_website_html_ws_whattoexpect_com.json"
)

REPORT_DIR = Path(
    "backend/server/data/runtime/"
    "udare_population_readiness"
)

MANIFEST_PATH = (
    REPORT_DIR
    / "population_manifest.json"
)

REPORT_PATH = (
    REPORT_DIR
    / "phase_4_1_readiness_report.json"
)


if not STORE_PATH.is_file():
    raise RuntimeError(
        f"Canonical Raw HTML Store not found: {STORE_PATH}"
    )


store = json.loads(
    STORE_PATH.read_text(
        encoding="utf-8",
        errors="replace",
    )
)


pages = store.get(
    "pages"
)


if not isinstance(
    pages,
    dict,
):
    raise RuntimeError(
        "Raw HTML Store field 'pages' is not a dictionary."
    )


manifest = []

missing_workspace = []
missing_identifier = []
missing_html = []
missing_url = []
workspace_mismatch = []
duplicate_identifiers = []

seen_identifiers = set()


for html_id, record in pages.items():
    if not isinstance(
        record,
        dict,
    ):
        missing_identifier.append(
            str(
                html_id
            )
        )
        continue

    identifier = str(
        record.get(
            "html_id"
        )
        or record.get(
            "page_id"
        )
        or record.get(
            "content_id"
        )
        or record.get(
            "url_hash"
        )
        or html_id
        or ""
    ).strip()

    workspace_id = str(
        record.get(
            "workspace_id"
        )
        or store.get(
            "workspace_id"
        )
        or ""
    ).strip()

    source_url = str(
        record.get(
            "source_url"
        )
        or record.get(
            "url"
        )
        or record.get(
            "canonical_url"
        )
        or record.get(
            "final_url"
        )
        or ""
    ).strip()

    raw_html = str(
        record.get(
            "raw_html"
        )
        or record.get(
            "html"
        )
        or record.get(
            "html_text"
        )
        or record.get(
            "source_html"
        )
        or ""
    )

    if not workspace_id:
        missing_workspace.append(
            identifier
            or str(
                html_id
            )
        )

    elif workspace_id != WORKSPACE_ID:
        workspace_mismatch.append({
            "identifier":
                identifier,

            "workspace_id":
                workspace_id,
        })

    if not identifier:
        missing_identifier.append(
            str(
                html_id
            )
        )

    elif identifier in seen_identifiers:
        duplicate_identifiers.append(
            identifier
        )

    seen_identifiers.add(
        identifier
    )

    if not source_url:
        missing_url.append(
            identifier
            or str(
                html_id
            )
        )

    if not raw_html.strip():
        missing_html.append(
            identifier
            or str(
                html_id
            )
        )

    raw_bytes = raw_html.encode(
        "utf-8",
        errors="replace",
    )

    manifest.append({
        "workspace_id":
            workspace_id,

        "html_id":
            str(
                html_id
            ),

        "identifier":
            identifier,

        "source_url":
            source_url,

        "raw_html_sha256":
            hashlib.sha256(
                raw_bytes
            ).hexdigest(),

        "raw_html_bytes":
            len(
                raw_bytes
            ),

        "raw_html_present":
            bool(
                raw_html.strip()
            ),
    })


checks = {
    "canonical_store_exists":
        STORE_PATH.is_file(),

    "store_version_present":
        bool(
            store.get(
                "version"
            )
        ),

    "workspace_matches":
        str(
            store.get(
                "workspace_id"
            )
            or ""
        )
        == WORKSPACE_ID,

    "pages_is_dictionary":
        isinstance(
            pages,
            dict,
        ),

    "records_found":
        len(
            pages
        )
        > 0,

    "expected_2225_records":
        len(
            pages
        )
        == 2225,

    "missing_workspace":
        len(
            missing_workspace
        )
        == 0,

    "workspace_mismatch":
        len(
            workspace_mismatch
        )
        == 0,

    "missing_identifier":
        len(
            missing_identifier
        )
        == 0,

    "duplicate_identifiers":
        len(
            duplicate_identifiers
        )
        == 0,

    "missing_source_url":
        len(
            missing_url
        )
        == 0,

    "missing_raw_html":
        len(
            missing_html
        )
        == 0,

    "manifest_count_matches_pages":
        len(
            manifest
        )
        == len(
            pages
        ),
}


failed = [
    name

    for name, passed
    in checks.items()

    if not passed
]


REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


MANIFEST_PATH.write_text(
    json.dumps(
        manifest,
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)


report = {
    "schema_version":
        "udare_population_readiness_v2",

    "workspace_id":
        WORKSPACE_ID,

    "raw_html_store_path":
        str(
            STORE_PATH
        ),

    "raw_html_store_version":
        store.get(
            "version"
        ),

    "raw_html_record_count":
        len(
            pages
        ),

    "manifest_count":
        len(
            manifest
        ),

    "checks":
        checks,

    "failed_checks":
        failed,

    "counts": {
        "missing_workspace":
            len(
                missing_workspace
            ),

        "workspace_mismatch":
            len(
                workspace_mismatch
            ),

        "missing_identifier":
            len(
                missing_identifier
            ),

        "duplicate_identifiers":
            len(
                duplicate_identifiers
            ),

        "missing_source_url":
            len(
                missing_url
            ),

        "missing_raw_html":
            len(
                missing_html
            ),
    },

    "samples": {
        "missing_workspace":
            missing_workspace[:20],

        "workspace_mismatch":
            workspace_mismatch[:20],

        "missing_identifier":
            missing_identifier[:20],

        "duplicate_identifiers":
            duplicate_identifiers[:20],

        "missing_source_url":
            missing_url[:20],

        "missing_raw_html":
            missing_html[:20],
    },

    "population_manifest_path":
        str(
            MANIFEST_PATH
        ),

    "jobs_created":
        False,

    "worker_executed":
        False,

    "udare_store_population_performed":
        False,

    "decision":
        (
            "READY_FOR_PHASE_4_2_JOB_CREATION"
            if not failed
            else "BLOCKED"
        ),
}


REPORT_PATH.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 100)
print(
    "PHASE 4.1 — UDARE POPULATION READINESS"
)
print("=" * 100)

print(
    "Raw HTML Store:",
    STORE_PATH,
)

print(
    "Store version:",
    store.get(
        "version"
    ),
)

print(
    "Raw HTML records:",
    len(
        pages
    ),
)

print(
    "Manifest records:",
    len(
        manifest
    ),
)

print()
print("CHECKS")

for name, passed in checks.items():
    print(
        f"  {name}:",
        (
            "PASS"
            if passed
            else "FAIL"
        ),
    )

print()
print(
    "Report:",
    REPORT_PATH,
)

print(
    "Manifest:",
    MANIFEST_PATH,
)

print()
print("=" * 100)
print(
    "PHASE 4.1 DECISION:",
    report[
        "decision"
    ],
)
print("=" * 100)

print(
    "No jobs created."
)

print(
    "No worker executed."
)

print(
    "No UDARE Store population performed."
)

raise SystemExit(
    0
    if not failed
    else 1
)
