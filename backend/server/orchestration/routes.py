from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from .schemas import (
    CreateJobRequest,
    CreateJobResponse,
    JobActionResponse,
    JobDetailResponse,
    JobListResponse,
    WorkerRunResponse,
)
from .service import (
    cancel_job,
    create_orchestration_job,
    get_orchestration_job,
    list_orchestration_jobs,
    service_health,
)
from .worker import run_one_job, worker_health


router = APIRouter(prefix="/api/jobs", tags=["orchestration"])


@router.get("/health")
def orchestration_health() -> Dict[str, Any]:
    return service_health()


@router.get("/worker/health")
def orchestration_worker_health() -> Dict[str, Any]:
    return worker_health()


@router.post("/test", response_model=CreateJobResponse)
def create_test_job(payload: CreateJobRequest) -> CreateJobResponse:
    job = create_orchestration_job(
        workspace_id=payload.workspace_id,
        job_type=payload.job_type,
        payload=payload.payload,
        metadata=payload.metadata,
        priority=payload.priority,
    )

    return CreateJobResponse(
        ok=True,
        job_id=job.job_id,
        status=job.status,
        job_type=job.job_type,
        workspace_id=job.workspace_id,
    )


@router.get("", response_model=JobListResponse)
def list_jobs() -> JobListResponse:
    return JobListResponse(ok=True, data=list_orchestration_jobs())


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job_detail(job_id: str) -> JobDetailResponse:
    data = get_orchestration_job(job_id)

    if data is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    return JobDetailResponse(ok=True, data=data)


@router.post("/{job_id}/cancel", response_model=JobActionResponse)
def cancel_job_route(job_id: str) -> JobActionResponse:
    try:
        job = cancel_job(job_id, metadata={"reason": "manual_cancel"})
        return JobActionResponse(ok=True, data={"job": asdict(job)})
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")


@router.post("/worker/run-one", response_model=WorkerRunResponse)
def run_one_worker_job() -> WorkerRunResponse:
    result = run_one_job()
    return WorkerRunResponse(ok=bool(result.get("ok", False)), data=result)
