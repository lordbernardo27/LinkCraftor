from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from typing import Any, Callable

from backend.server.orchestration.job_store import get_job, load_jobs


CONNECTED_DOMAIN_HYDRATOR_VERSION = "connected_domain_runtime_hydrator_v1.0.0"
CONNECTED_DOMAIN_HYDRATOR_REF = (
    "backend.server.pipelines.connect_domain.runtime_hydration:"
    "hydrate_connected_domain_runtime_job"
)

_PREDECESSOR_BY_STAGE = {
    "url_cleaner": "site_sources",
    "site_pages": "url_cleaner",
    "live_domain_target_pool": "site_pages",
    "active_target_set": "live_domain_target_pool",
}


class ConnectedDomainRuntimeHydrationError(RuntimeError):
    pass


def _value(source: Any, name: str, default: Any = None) -> Any:
    if isinstance(source, Mapping):
        return source.get(name, default)
    return getattr(source, name, default)


def _plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_plain(item) for item in value]
    for method_name in ("to_payload", "to_dict", "to_canonical_dict"):
        method = getattr(value, method_name, None)
        if callable(method):
            try:
                return _plain(method())
            except TypeError:
                continue
    if dataclasses.is_dataclass(value):
        return _plain(dataclasses.asdict(value))
    if hasattr(value, "__dict__"):
        return _plain(vars(value))
    raise ConnectedDomainRuntimeHydrationError(
        "Predecessor result cannot be converted to canonical payload evidence."
    )


def _job_metadata(job: Any) -> Mapping[str, Any]:
    metadata = _value(job, "metadata", {})
    return metadata if isinstance(metadata, Mapping) else {}


def _job_stage(job: Any) -> str:
    direct = str(_value(job, "stage", "") or "").strip()
    if direct:
        return direct.removesuffix("_stage")
    metadata = _job_metadata(job)
    universal = metadata.get("universal_job", {})
    if isinstance(universal, Mapping):
        return str(universal.get("stage") or "").strip().removesuffix("_stage")
    return ""


def _dependency_ids(job: Mapping[str, Any]) -> tuple[str, ...]:
    candidates: list[Any] = [job.get("dependency_job_ids")]
    metadata = _job_metadata(job)
    candidates.append(metadata.get("dependency_job_ids"))
    universal = metadata.get("universal_job", {})
    if isinstance(universal, Mapping):
        candidates.append(universal.get("dependency_job_ids"))
    for candidate in candidates:
        if candidate is None:
            continue
        if isinstance(candidate, str):
            candidate = (candidate,)
        try:
            normalized = tuple(
                str(item or "").strip() for item in candidate if str(item or "").strip()
            )
        except TypeError:
            continue
        if normalized:
            return normalized
    return ()


def _workflow_id(job: Mapping[str, Any]) -> str:
    metadata = _job_metadata(job)
    for source in (job, metadata, metadata.get("coordination", {}), metadata.get("universal_job", {})):
        if isinstance(source, Mapping):
            value = str(source.get("workflow_id") or source.get("pipeline_run_id") or "").strip()
            if value:
                return value
    return ""


def _find_predecessor(
    job: Mapping[str, Any],
    *,
    predecessor_stage: str,
    job_reader: Callable[[str], Any],
    jobs_reader: Callable[[], Mapping[str, Any]],
) -> Any:
    dependencies = _dependency_ids(job)
    candidates = [job_reader(job_id) for job_id in dependencies]
    candidates = [candidate for candidate in candidates if candidate is not None]
    matching = [candidate for candidate in candidates if _job_stage(candidate) == predecessor_stage]
    # Explicit predecessor identities are authoritative.
    # Workflow-stage discovery is permitted only for legacy jobs
    # without declared dependency IDs.
    if not matching and not dependencies:
        workflow_id = _workflow_id(job)
        loaded = jobs_reader()
        if not isinstance(loaded, Mapping):
            raise ConnectedDomainRuntimeHydrationError(
                "Canonical job reader returned a non-mapping."
            )
        matching = [
            candidate
            for candidate in loaded.values()
            if _job_stage(candidate) == predecessor_stage
            and (not workflow_id or _workflow_id(_plain(candidate)) == workflow_id)
        ]
    if len(matching) != 1:
        raise ConnectedDomainRuntimeHydrationError(
            f"Expected one {predecessor_stage} predecessor job; found {len(matching)}."
        )
    predecessor = matching[0]

    # A predecessor must belong to the same workspace and
    # workflow as the job consuming its output.
    requested_workspace = str(
        _value(job, "workspace_id", "") or ""
    ).strip()
    predecessor_workspace = str(
        _value(predecessor, "workspace_id", "") or ""
    ).strip()

    if (
        not requested_workspace
        or not predecessor_workspace
        or predecessor_workspace != requested_workspace
    ):
        raise ConnectedDomainRuntimeHydrationError(
            "Predecessor workspace identity mismatch."
        )

    requested_workflow = _workflow_id(job)
    predecessor_workflow = _workflow_id(_plain(predecessor))

    if (
        not requested_workflow
        or not predecessor_workflow
        or predecessor_workflow != requested_workflow
    ):
        raise ConnectedDomainRuntimeHydrationError(
            "Predecessor workflow identity mismatch."
        )

    status = str(_value(predecessor, "status", "") or "").strip().lower()
    if status != "completed":
        raise ConnectedDomainRuntimeHydrationError(
            f"Predecessor {predecessor_stage} is not completed."
        )
    return predecessor


def _handler_result(predecessor: Any) -> Mapping[str, Any]:
    metadata = _job_metadata(predecessor)
    dispatch = metadata.get("runtime_dispatch_result")
    if not isinstance(dispatch, Mapping):
        raise ConnectedDomainRuntimeHydrationError(
            "Completed predecessor has no runtime_dispatch_result."
        )
    result: Any = dispatch.get("handler_result")
    if isinstance(result, Mapping) and set(result) == {"value"}:
        result = result["value"]
    result = _plain(result)
    if not isinstance(result, Mapping):
        raise ConnectedDomainRuntimeHydrationError(
            "Predecessor handler result must resolve to a mapping."
        )
    return result


def _cleaner_records(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    cleaned = tuple(str(item).strip() for item in result.get("cleaned_urls", ()) if str(item).strip())
    explicit = {str(item).strip() for item in result.get("explicit_urls", ()) if str(item).strip()}
    uncertain = {str(item).strip() for item in result.get("uncertain_urls", ()) if str(item).strip()}
    records = []
    for url in cleaned:
        confidence = "explicit" if url in explicit else "uncertain"
        if url not in explicit and url not in uncertain:
            raise ConnectedDomainRuntimeHydrationError(
                "Cleaned URL has no explicit or uncertain confidence evidence."
            )
        records.append(
            {
                "url": url,
                "canonical": url,
                "confidence": confidence,
                "accepted": True,
            }
        )
    if not records:
        raise ConnectedDomainRuntimeHydrationError(
            "URL Cleaner produced no accepted records for Site Pages."
        )
    return records


def hydrate_connected_domain_runtime_job(
    job: Mapping[str, Any],
    *,
    job_reader: Callable[[str], Any] = get_job,
    jobs_reader: Callable[[], Mapping[str, Any]] = load_jobs,
) -> dict[str, Any]:
    if not isinstance(job, Mapping):
        raise ConnectedDomainRuntimeHydrationError("Runtime job must be a mapping.")
    hydrated = dict(job)
    payload = hydrated.get("payload", {})
    if not isinstance(payload, Mapping):
        raise ConnectedDomainRuntimeHydrationError("Runtime job payload must be a mapping.")
    resolved_payload = dict(payload)
    stage = _job_stage(hydrated)
    predecessor_stage = _PREDECESSOR_BY_STAGE.get(stage)
    if predecessor_stage is None:
        hydrated["payload"] = resolved_payload
        return hydrated

    target_field = {
        "url_cleaner": "source_urls",
        "site_pages": "cleaner_records",
        "live_domain_target_pool": "site_pages",
        "active_target_set": "live_domain_payload",
    }[stage]
    if target_field in resolved_payload and resolved_payload[target_field] not in (None, (), [], {}):
        hydrated["payload"] = resolved_payload
        return hydrated

    predecessor = _find_predecessor(
        hydrated,
        predecessor_stage=predecessor_stage,
        job_reader=job_reader,
        jobs_reader=jobs_reader,
    )
    result = _handler_result(predecessor)
    if stage == "url_cleaner":
        value = list(result.get("discovered_urls", ()))
    elif stage == "site_pages":
        value = _cleaner_records(result)
    elif stage == "live_domain_target_pool":
        value = list(result.get("pages", result.get("items", ())))
    else:
        targets = list(result.get("targets", result.get("items", ())))
        value = {**dict(result), "items": targets}
    if value in (None, (), [], {}):
        raise ConnectedDomainRuntimeHydrationError(
            f"Predecessor {predecessor_stage} produced no value for {target_field}."
        )
    resolved_payload[target_field] = value
    hydrated["payload"] = resolved_payload
    return hydrated
