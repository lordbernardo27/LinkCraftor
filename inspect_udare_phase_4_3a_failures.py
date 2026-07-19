from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


WORKSPACE_ID = "ws_whattoexpect_com"

PHASE43_REPORT = Path(
    "backend/server/data/runtime/"
    "udare_phase_4_3_controlled_execution/"
    "phase_4_3a_first_5_report.json"
)

DATA_ROOT = Path(
    "backend/server/data"
)

OUTPUT_DIR = Path(
    "backend/server/data/runtime/"
    "udare_phase_4_3_failure_inspection"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "phase_4_3a_first_5_failure_inspection.json"
)


def load_json(
    path: Path,
    default: Any,
) -> Any:
    if not path.is_file():
        return default

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        )

    except Exception as exc:
        return {
            "_read_error":
                f"{type(exc).__name__}: {exc}",

            "_path":
                str(
                    path
                ),
        }


def read_jsonl(
    path: Path,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    if not path.is_file():
        return rows

    for line_number, line in enumerate(
        path.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines(),
        start=1,
    ):
        if not line.strip():
            continue

        try:
            row = json.loads(
                line
            )

            if isinstance(
                row,
                dict,
            ):
                row[
                    "_line_number"
                ] = line_number

                rows.append(
                    row
                )

        except Exception:
            continue

    return rows


if not PHASE43_REPORT.is_file():
    raise RuntimeError(
        f"Missing Phase 4.3A report: {PHASE43_REPORT}"
    )


phase43 = load_json(
    PHASE43_REPORT,
    {},
)

runner_result = (
    phase43.get(
        "runner_result"
    )
    or {}
)

results = (
    runner_result.get(
        "results"
    )
    or []
)

failed_results = [
    result

    for result
    in results

    if isinstance(
        result,
        dict,
    )
    and result.get(
        "ok"
    )
    is not True
]


if len(
    failed_results
) != 5:
    raise RuntimeError(
        "Expected 5 failed runner results, "
        f"found {len(failed_results)}."
    )


job_ids = [
    str(
        result.get(
            "job_id"
        )
        or ""
    ).strip()

    for result
    in failed_results
]


if any(
    not job_id

    for job_id
    in job_ids
):
    raise RuntimeError(
        "One or more failed results contain no job_id."
    )


candidate_status_dirs = [
    DATA_ROOT
    / "universal_knowledge_jobs"
    / WORKSPACE_ID
    / "status",

    DATA_ROOT
    / "runtime"
    / "universal_knowledge_jobs"
    / WORKSPACE_ID
    / "status",

    DATA_ROOT
    / "job_status"
    / WORKSPACE_ID,

    DATA_ROOT
    / "runtime"
    / "job_status"
    / WORKSPACE_ID,
]


candidate_progress_dirs = [
    DATA_ROOT
    / "universal_knowledge_jobs"
    / WORKSPACE_ID
    / "progress",

    DATA_ROOT
    / "runtime"
    / "universal_knowledge_jobs"
    / WORKSPACE_ID
    / "progress",

    DATA_ROOT
    / "job_progress"
    / WORKSPACE_ID,

    DATA_ROOT
    / "runtime"
    / "job_progress"
    / WORKSPACE_ID,
]


candidate_failure_files = [
    DATA_ROOT
    / "universal_knowledge_jobs"
    / WORKSPACE_ID
    / "failures.jsonl",

    DATA_ROOT
    / "runtime"
    / "universal_knowledge_jobs"
    / WORKSPACE_ID
    / "failures.jsonl",

    DATA_ROOT
    / "job_failures"
    / f"{WORKSPACE_ID}.jsonl",

    DATA_ROOT
    / "runtime"
    / "job_failures"
    / f"{WORKSPACE_ID}.jsonl",
]


def find_job_file(
    job_id: str,
    directories: List[Path],
) -> Path | None:
    names = [
        f"{job_id}.json",
        f"job_{job_id}.json",
    ]

    for directory in directories:
        for name in names:
            candidate = (
                directory
                / name
            )

            if candidate.is_file():
                return candidate

    for root in [
        DATA_ROOT,
    ]:
        matches = list(
            root.rglob(
                f"*{job_id}*.json"
            )
        )

        for match in matches:
            lowered = str(
                match
            ).casefold()

            if (
                "status"
                in lowered
                or "progress"
                in lowered
            ):
                return match

    return None


all_failure_rows: List[Dict[str, Any]] = []

for failure_file in candidate_failure_files:
    all_failure_rows.extend(
        read_jsonl(
            failure_file
        )
    )


if not all_failure_rows:
    for path in DATA_ROOT.rglob(
        "*.jsonl"
    ):
        lowered = str(
            path
        ).casefold()

        if (
            "failure"
            in lowered
            and WORKSPACE_ID.casefold()
            in lowered
        ):
            all_failure_rows.extend(
                read_jsonl(
                    path
                )
            )


inspection_rows: List[Dict[str, Any]] = []


for result in failed_results:
    job_id = str(
        result.get(
            "job_id"
        )
        or ""
    ).strip()

    status_path = find_job_file(
        job_id,
        candidate_status_dirs,
    )

    progress_path = find_job_file(
        job_id,
        candidate_progress_dirs,
    )

    status_record = (
        load_json(
            status_path,
            {},
        )
        if status_path
        else {}
    )

    progress_record = (
        load_json(
            progress_path,
            {},
        )
        if progress_path
        else {}
    )

    failure_rows = [
        row

        for row
        in all_failure_rows

        if str(
            row.get(
                "job_id"
            )
            or ""
        )
        == job_id
    ]

    result_failure = result.get(
        "failure"
    )

    result_error = str(
        result.get(
            "error"
        )
        or (
            result_failure.get(
                "error"
            )
            if isinstance(
                result_failure,
                dict,
            )
            else ""
        )
        or ""
    )

    status_error = str(
        status_record.get(
            "error"
        )
        or status_record.get(
            "error_info"
        )
        or ""
    )

    registry_errors = [
        str(
            row.get(
                "error"
            )
            or row.get(
                "reason"
            )
            or ""
        )

        for row
        in failure_rows
    ]

    last_progress_step = ""

    steps = progress_record.get(
        "steps"
    )

    if isinstance(
        steps,
        list,
    ) and steps:
        last = steps[
            -1
        ]

        if isinstance(
            last,
            dict,
        ):
            last_progress_step = str(
                last.get(
                    "step"
                )
                or ""
            )

    likely_stage = "unknown"

    combined_error = " | ".join(
        value

        for value
        in (
            result_error,
            status_error,
            *registry_errors,
        )

        if value
    ).casefold()

    if (
        "raw html"
        in combined_error
        or "source record"
        in combined_error
        or "html_id"
        in combined_error
    ):
        likely_stage = (
            "raw_html_loading"
        )

    elif (
        "reconstruct"
        in combined_error
        or "engine"
        in combined_error
    ):
        likely_stage = (
            "udare_reconstruction"
        )

    elif (
        "builder"
        in combined_error
        or "article document"
        in combined_error
        or "content block"
        in combined_error
    ):
        likely_stage = (
            "article_document_builder"
        )

    elif (
        "persist"
        in combined_error
        or "store"
        in combined_error
        or "manifest"
        in combined_error
    ):
        likely_stage = (
            "udare_store_persistence"
        )

    elif last_progress_step:
        likely_stage = (
            "after_"
            + last_progress_step
        )

    inspection_rows.append({
        "job_id":
            job_id,

        "runner_result":
            result,

        "status_path":
            str(
                status_path
            )
            if status_path
            else "",

        "status_record":
            status_record,

        "progress_path":
            str(
                progress_path
            )
            if progress_path
            else "",

        "progress_record":
            progress_record,

        "failure_registry_rows":
            failure_rows,

        "result_error":
            result_error,

        "status_error":
            status_error,

        "registry_errors":
            registry_errors,

        "last_progress_step":
            last_progress_step,

        "likely_failure_stage":
            likely_stage,
    })


error_signatures: Dict[str, int] = {}

for row in inspection_rows:
    signature = (
        row.get(
            "result_error"
        )
        or row.get(
            "status_error"
        )
        or (
            row.get(
                "registry_errors"
            )
            or [""]
        )[0]
        or "NO_ERROR_TEXT_FOUND"
    )

    error_signatures[
        signature
    ] = (
        error_signatures.get(
            signature,
            0,
        )
        + 1
    )


report = {
    "schema_version":
        "udare_phase_4_3a_failure_inspection_v1",

    "workspace_id":
        WORKSPACE_ID,

    "phase_4_3_report":
        str(
            PHASE43_REPORT
        ),

    "failed_job_count":
        len(
            failed_results
        ),

    "job_ids":
        job_ids,

    "error_signatures":
        error_signatures,

    "jobs":
        inspection_rows,

    "source_modified":
        False,

    "queue_modified":
        False,

    "worker_invoked":
        False,

    "reconstruction_invoked":
        False,

    "udare_store_write":
        False,
}


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_PATH.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 112)
print(
    "PHASE 4.3A — FIRST 5 FAILURE INSPECTION"
)
print("=" * 112)

print(
    "Failed jobs:",
    len(
        inspection_rows
    ),
)

print()
print("ERROR SIGNATURES")

for signature, count in (
    error_signatures.items()
):
    print(
        f"  [{count}]",
        signature,
    )

print()
print("PER-JOB DETAILS")

for row in inspection_rows:
    print()
    print(
        "JOB:",
        row[
            "job_id"
        ],
    )

    print(
        "  Likely stage:",
        row[
            "likely_failure_stage"
        ],
    )

    print(
        "  Last progress step:",
        row[
            "last_progress_step"
        ]
        or "(none)",
    )

    print(
        "  Result error:",
        row[
            "result_error"
        ]
        or "(none)",
    )

    print(
        "  Status error:",
        row[
            "status_error"
        ]
        or "(none)",
    )

    print(
        "  Status path:",
        row[
            "status_path"
        ]
        or "(not found)",
    )

    print(
        "  Progress path:",
        row[
            "progress_path"
        ]
        or "(not found)",
    )

    if row[
        "registry_errors"
    ]:
        print(
            "  Registry errors:"
        )

        for error in row[
            "registry_errors"
        ]:
            print(
                "    -",
                error,
            )

print()
print(
    "Inspection report:",
    OUTPUT_PATH,
)

print()
print("=" * 112)
print(
    "PHASE 4.3A FAILURE INSPECTION: COMPLETE"
)
print("=" * 112)

print(
    "No queue was modified."
)

print(
    "No worker or reconstruction was invoked."
)

print(
    "No UDARE Store write was performed."
)
