from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from backend.server.jobs.universal_knowledge_orchestrator import (
    queue_path,
    read_queue,
    safe_id,
)
from backend.server.workers.universal_knowledge_worker import execute_universal_knowledge_job_v1


def _write_remaining_queue_v1(workspace_id: str, jobs: List[Dict[str, Any]]) -> None:
    path = queue_path(workspace_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(job, ensure_ascii=False) for job in jobs) + ("\n" if jobs else ""),
        encoding="utf-8",
    )


def run_universal_knowledge_queue_v1(
    *,
    workspace_id: str,
    max_jobs: int = 20,
    job_type: str | None = None,
) -> Dict[str, Any]:
    ws = safe_id(workspace_id)
    queued = read_queue(ws, limit=10000)

    pending = []
    remaining = []

    for job in queued:
        if job.get("status") != "queued":
            remaining.append(job)
            continue

        if job_type and job.get("job_type") != job_type:
            remaining.append(job)
            continue

        if len(pending) < int(max_jobs):
            pending.append(job)
        else:
            remaining.append(job)

    results = []

    for job in pending:
        result = execute_universal_knowledge_job_v1(job)
        results.append(result)

    _write_remaining_queue_v1(ws, remaining)

    return {
        "ok": True,
        "workspace_id": ws,
        "max_jobs": int(max_jobs),
        "job_type_filter": job_type,
        "executed_count": len(results),
        "remaining_count": len(remaining),
        "results": results,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--max-jobs", type=int, default=20)
    parser.add_argument("--job-type", default=None)

    args = parser.parse_args()

    output = run_universal_knowledge_queue_v1(
        workspace_id=args.workspace_id,
        max_jobs=args.max_jobs,
        job_type=args.job_type,
    )

    print(json.dumps(output, indent=2, ensure_ascii=False))
