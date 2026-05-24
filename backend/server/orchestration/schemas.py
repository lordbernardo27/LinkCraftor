from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CreateJobRequest(BaseModel):
    workspace_id: str = Field(default="default")
    job_type: str = Field(default="test_job")
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)


class CreateJobResponse(BaseModel):
    ok: bool
    job_id: str
    status: str
    job_type: str
    workspace_id: str


class JobActionResponse(BaseModel):
    ok: bool
    data: Dict[str, Any]


class JobListResponse(BaseModel):
    ok: bool
    data: Dict[str, Any]


class JobDetailResponse(BaseModel):
    ok: bool
    data: Dict[str, Any]


class WorkerRunResponse(BaseModel):
    ok: bool
    data: Dict[str, Any]
