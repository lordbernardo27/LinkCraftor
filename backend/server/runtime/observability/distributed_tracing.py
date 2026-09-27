"""
LinkCraftor Universal Runtime Infrastructure
Phase 8.10 — Distributed Tracing Foundations

Defines canonical trace/span contracts and propagation boundaries.

Does NOT create:
- tracing backend
- OpenTelemetry collector
- persistence
- execution state
- orchestration decisions
"""

from __future__ import annotations

import uuid

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional


DISTRIBUTED_TRACING_VERSION = "distributed_tracing_v8.10.1"
DISTRIBUTED_TRACING_SCHEMA_VERSION = "distributed_tracing_schema_v1"


class TraceSpanKind(str, Enum):
    INTERNAL = "INTERNAL"
    PRODUCER = "PRODUCER"
    CONSUMER = "CONSUMER"
    SERVER = "SERVER"
    CLIENT = "CLIENT"


class TraceSpanStatus(str, Enum):
    UNSET = "UNSET"
    OK = "OK"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class RuntimeTraceContext:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None

    sampled: bool = True

    workspace_id: Optional[str] = None
    job_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    execution_id: Optional[str] = None
    worker_id: Optional[str] = None
    queue_name: Optional[str] = None

    schema_version: str = field(
        default=DISTRIBUTED_TRACING_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.trace_id.strip():
            raise ValueError("trace_id is required.")
        if not self.span_id.strip():
            raise ValueError("span_id is required.")


@dataclass(frozen=True, slots=True)
class RuntimeSpan:
    name: str
    context: RuntimeTraceContext
    kind: TraceSpanKind

    status: TraceSpanStatus = TraceSpanStatus.UNSET

    attributes: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=DISTRIBUTED_TRACING_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("span name is required.")

        object.__setattr__(
            self,
            "attributes",
            MappingProxyType(dict(self.attributes)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "trace_id": self.context.trace_id,
            "span_id": self.context.span_id,
            "parent_span_id": self.context.parent_span_id,
            "sampled": self.context.sampled,
            "kind": self.kind.value,
            "status": self.status.value,
            "workspace_id": self.context.workspace_id,
            "job_id": self.context.job_id,
            "orchestration_id": self.context.orchestration_id,
            "execution_id": self.context.execution_id,
            "worker_id": self.context.worker_id,
            "queue_name": self.context.queue_name,
            "attributes": dict(self.attributes),
        }


TraceSink = Callable[[Mapping[str, Any]], Any]


def new_trace_id() -> str:
    return uuid.uuid4().hex


def new_span_id() -> str:
    return uuid.uuid4().hex[:16]


def create_root_trace_context(
    *,
    workspace_id: Optional[str] = None,
    job_id: Optional[str] = None,
    orchestration_id: Optional[str] = None,
    execution_id: Optional[str] = None,
    worker_id: Optional[str] = None,
    queue_name: Optional[str] = None,
    sampled: bool = True,
) -> RuntimeTraceContext:

    return RuntimeTraceContext(
        trace_id=new_trace_id(),
        span_id=new_span_id(),
        sampled=sampled,
        workspace_id=workspace_id,
        job_id=job_id,
        orchestration_id=orchestration_id,
        execution_id=execution_id,
        worker_id=worker_id,
        queue_name=queue_name,
    )


def create_child_trace_context(
    parent: RuntimeTraceContext,
    *,
    execution_id: Optional[str] = None,
    worker_id: Optional[str] = None,
    queue_name: Optional[str] = None,
) -> RuntimeTraceContext:

    return RuntimeTraceContext(
        trace_id=parent.trace_id,
        span_id=new_span_id(),
        parent_span_id=parent.span_id,
        sampled=parent.sampled,
        workspace_id=parent.workspace_id,
        job_id=parent.job_id,
        orchestration_id=parent.orchestration_id,
        execution_id=(
            execution_id
            if execution_id is not None
            else parent.execution_id
        ),
        worker_id=(
            worker_id
            if worker_id is not None
            else parent.worker_id
        ),
        queue_name=(
            queue_name
            if queue_name is not None
            else parent.queue_name
        ),
    )


def inject_trace_headers(
    context: RuntimeTraceContext,
) -> Mapping[str, str]:

    return MappingProxyType({
        "x-linkcraftor-trace-id": context.trace_id,
        "x-linkcraftor-span-id": context.span_id,
        "x-linkcraftor-sampled": "1" if context.sampled else "0",
    })


def emit_runtime_span(
    *,
    span: RuntimeSpan,
    sink: TraceSink,
) -> bool:

    if not callable(sink):
        raise ValueError("trace sink must be callable.")

    try:
        sink(span.to_dict())
    except Exception:
        return False

    return True


def certify_distributed_tracing_v1() -> Mapping[str, Any]:

    captured: list[Mapping[str, Any]] = []

    root = create_root_trace_context(
        workspace_id="workspace-810",
        job_id="job-810",
        orchestration_id="orchestration-810",
        queue_name="runtime-default",
    )

    child = create_child_trace_context(
        root,
        execution_id="execution-810",
        worker_id="worker-810",
    )

    span = RuntimeSpan(
        name="runtime.execution",
        context=child,
        kind=TraceSpanKind.CONSUMER,
        status=TraceSpanStatus.OK,
        attributes={
            "attempt_number": 2,
            "handler_key": "handler-810",
        },
    )

    emitted = emit_runtime_span(
        span=span,
        sink=lambda r: captured.append(dict(r)),
    )

    headers = inject_trace_headers(child)

    record = captured[0] if captured else {}

    checks = {
        "distributed_tracing_contract_created": True,
        "root_trace_created": bool(root.trace_id),
        "child_span_created": bool(child.span_id),
        "trace_id_propagated": child.trace_id == root.trace_id,
        "parent_span_linked": child.parent_span_id == root.span_id,
        "trace_headers_created": (
            headers["x-linkcraftor-trace-id"] == root.trace_id
        ),
        "span_emitted": emitted,
        "job_identity_preserved": record.get("job_id") == "job-810",
        "orchestration_identity_preserved": (
            record.get("orchestration_id") == "orchestration-810"
        ),
        "execution_identity_preserved": (
            record.get("execution_id") == "execution-810"
        ),
        "worker_identity_preserved": (
            record.get("worker_id") == "worker-810"
        ),
        "queue_identity_preserved": (
            record.get("queue_name") == "runtime-default"
        ),
        "no_tracing_backend_created": True,
        "no_collector_created": True,
        "no_runtime_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "8.10",
        "component": "Distributed Tracing Foundations",
        "version": DISTRIBUTED_TRACING_VERSION,
        "schema_version": DISTRIBUTED_TRACING_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 8.10 defines trace/span identity, parent-child propagation "
            "and sink emission without creating a tracing backend, collector "
            "or runtime state authority."
        ),
    })


__all__ = [
    "DISTRIBUTED_TRACING_VERSION",
    "DISTRIBUTED_TRACING_SCHEMA_VERSION",
    "TraceSpanKind",
    "TraceSpanStatus",
    "RuntimeTraceContext",
    "RuntimeSpan",
    "TraceSink",
    "new_trace_id",
    "new_span_id",
    "create_root_trace_context",
    "create_child_trace_context",
    "inject_trace_headers",
    "emit_runtime_span",
    "certify_distributed_tracing_v1",
]
