from __future__ import annotations

import importlib
from collections.abc import Mapping
from typing import Any


RUNTIME_PAYLOAD_HYDRATOR_KEY = "__runtime_payload_hydrator_ref__"
RUNTIME_PAYLOAD_HYDRATION_VERSION = "runtime_payload_hydration_v1.0.0"


class RuntimePayloadHydrationError(RuntimeError):
    pass


def _resolve_hydrator(reference: str):
    module_name, separator, attribute_name = reference.partition(":")
    if (
        separator != ":"
        or not module_name.startswith("backend.server.pipelines.")
        or not attribute_name
    ):
        raise RuntimePayloadHydrationError(
            "Runtime payload hydrator reference is invalid."
        )
    module = importlib.import_module(module_name)
    hydrator = getattr(module, attribute_name, None)
    if not callable(hydrator):
        raise RuntimePayloadHydrationError(
            "Runtime payload hydrator is unavailable: " + reference
        )
    return hydrator


def hydrate_runtime_job_payload(job: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(job, Mapping):
        raise RuntimePayloadHydrationError(
            "Runtime job must be a mapping before payload hydration."
        )
    hydrated_job = dict(job)
    payload = hydrated_job.get("payload", {})
    if not isinstance(payload, Mapping):
        raise RuntimePayloadHydrationError(
            "Runtime job payload must be a mapping before hydration."
        )
    hydrated_payload = dict(payload)
    reference = str(
        hydrated_payload.pop(RUNTIME_PAYLOAD_HYDRATOR_KEY, "") or ""
    ).strip()
    hydrated_job["payload"] = hydrated_payload
    if not reference:
        return hydrated_job
    result = _resolve_hydrator(reference)(hydrated_job)
    if not isinstance(result, Mapping):
        raise RuntimePayloadHydrationError(
            "Runtime payload hydrator must return a job mapping."
        )
    resolved = dict(result)
    resolved_payload = resolved.get("payload", {})
    if not isinstance(resolved_payload, Mapping):
        raise RuntimePayloadHydrationError(
            "Hydrated runtime job payload must be a mapping."
        )
    clean_payload = dict(resolved_payload)
    clean_payload.pop(RUNTIME_PAYLOAD_HYDRATOR_KEY, None)
    resolved["payload"] = clean_payload
    return resolved
