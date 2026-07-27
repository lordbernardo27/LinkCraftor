from __future__ import annotations

"""
Universal Knowledge Queue Runner — Phase 3E (UDARE pipeline).

Scope
-----
Local, single-process queue draining only:

    Raw HTML Store -> UDARE Runtime Stage -> UDARE Queue -> UDARE Worker -> UDARE Store

This module reads the per-workspace JSONL queue, selects queued jobs
(optionally filtered by job_type, ordered by priority), executes up to
``max_jobs`` of them through the existing worker contract, and rewrites the
queue with the untouched remainder.

This is NOT the future enterprise scheduler. No distributed orchestration,
no cross-process locking, no worker pools.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from backend.server.jobs.universal_knowledge_orchestrator import (
    queue_path,
    read_queue,    safe_id,
)
from backend.server.workers.universal_knowledge_worker import (
    execute_universal_knowledge_job_v1,
)

DEFAULT_PRIORITY = 1000


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _queue_priority(job: Dict[str, Any]) -> int:
    """Lower value runs first. Jobs without a usable priority sort last."""
    try:
        return int(job.get("priority", DEFAULT_PRIORITY))
    except (TypeError, ValueError):
        return DEFAULT_PRIORITY


def _sort_queue(queue: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Stable priority sort: FIFO order is preserved within a priority."""
    return sorted(queue, key=_queue_priority)


def _claim_lease(job: Dict[str, Any], runner_id: str) -> None:
    job["lease_owner"] = runner_id
    job["lease_started_at"] = _now_iso()


def _release_lease(job: Dict[str, Any]) -> None:
    job["lease_owner"] = None
    job["lease_finished_at"] = _now_iso()


def _write_remaining_queue_v1(workspace_id: str, jobs: List[Dict[str, Any]]) -> None:
    """Rewrite the workspace queue file with the jobs that were not executed."""
    path = queue_path(workspace_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(job, ensure_ascii=False) for job in jobs)
        + ("\n" if jobs else ""),
        encoding="utf-8",
    )


def _partition_queue(
    queued: List[Dict[str, Any]],
    *,
    job_type: Optional[str],
    max_jobs: int,
    order_by_priority: bool,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Split the queue into (pending-to-run, remaining-in-queue)."""
    eligible: List[Dict[str, Any]] = []
    remaining: List[Dict[str, Any]] = []

    for job in queued:
        if job.get("status") != "queued":
            remaining.append(job)
            continue
        if job_type and job.get("job_type") != job_type:
            remaining.append(job)
            continue
        eligible.append(job)

    if order_by_priority:
        eligible = _sort_queue(eligible)

    pending = eligible[: max(0, int(max_jobs))]
    overflow = eligible[max(0, int(max_jobs)):]

    # Overflow keeps its queued status and stays in the queue file.
    remaining.extend(overflow)
    return pending, remaining


def _execute_one(job: Dict[str, Any], runner_id: str) -> Dict[str, Any]:
    """Execute a single job through the existing worker contract."""
    ws = safe_id(job.get("workspace_id") or "default")
    job_id = str(job.get("job_id") or "")
    jt = str(job.get("job_type") or "")

    _claim_lease(job, runner_id)

    try:
        result = execute_universal_knowledge_job_v1(job)
    except Exception as e:
        result = {
            "ok": False,
            "job_id": job_id,
            "workspace_id": ws,
            "job_type": jt,
            "error": str(e),
        }
    finally:

        _release_lease(job)

    result["lease_owner"] = runner_id
    result["lease_started_at"] = job.get("lease_started_at")
    result["lease_finished_at"] = job.get("lease_finished_at")
    return result


def run_universal_knowledge_queue_v1(
    *,
    workspace_id: str,
    max_jobs: int = 20,
    job_type: str | None = None,
) -> Dict[str, Any]:
    ws = safe_id(workspace_id)
    queued = read_queue(
        ws,
        limit=10000,
    )

    pending = []
    remaining = []

    for job in queued:
        if job.get("status") != "queued":
            remaining.append(job)
            continue

        if (
            job_type
            and job.get("job_type")
            != job_type
        ):
            remaining.append(job)
            continue

        if len(pending) < int(max_jobs):
            pending.append(job)
        else:
            remaining.append(job)

    results = []

    for job in pending:
        result = execute_universal_knowledge_job_v1(
            job
        )

        results.append(result)

    pending_job_ids = {
        str(
            job.get("job_id")
            or ""
        )
        for job in pending
        if str(
            job.get("job_id")
            or ""
        ).strip()
    }

    latest_queue = read_queue(
        ws,
        limit=100000,
    )

    final_remaining = []
    seen_job_ids = set()

    for job in [
        *remaining,
        *latest_queue,
    ]:
        current_job_id = str(
            job.get("job_id")
            or ""
        ).strip()

        if (
            current_job_id
            and current_job_id
            in pending_job_ids
        ):
            continue

        deduplication_key = (
            current_job_id
            or repr(job)
        )

        if (
            deduplication_key
            in seen_job_ids
        ):
            continue

        seen_job_ids.add(
            deduplication_key
        )

        final_remaining.append(
            job
        )

    _write_remaining_queue_v1(
        ws,
        final_remaining,
    )

    from backend.server.runtime.website_article_integrity_automation import (
        maybe_trigger_website_article_integrity_after_udare_queue_drain,
    )

    post_run_automation = (
        maybe_trigger_website_article_integrity_after_udare_queue_drain(
            workspace_id=ws,
            processed_jobs=pending,
            execution_results=results,
            remaining_jobs=final_remaining,
        )
    )

    return {
        "ok": True,
        "workspace_id": ws,
        "max_jobs": int(max_jobs),
        "job_type_filter": job_type,
        "jobs_selected": len(pending),
        "jobs_executed": len(results),
        "jobs_remaining": len(
            final_remaining
        ),
        "results": results,
        "post_run_automation": (
            post_run_automation
        ),
    }



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the local universal knowledge queue for a workspace."
    )
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--max-jobs", type=int, default=20)
    parser.add_argument("--job-type", default=None)
    parser.add_argument(
        "--no-priority",
        action="store_true",
        help="Preserve raw FIFO queue order instead of priority ordering.",
    )

    args = parser.parse_args()

    output = run_universal_knowledge_queue_v1(
        workspace_id=args.workspace_id,
        max_jobs=args.max_jobs,
        job_type=args.job_type,
        order_by_priority=not args.no_priority,
    )

    print(json.dumps(output, indent=2, ensure_ascii=False))