"""Canonical Active Target Set stage.

This module is pure and deterministic.

Responsibilities:
- accept source target-pool payloads
- normalize eligible target records
- preserve workspace isolation
- deduplicate targets
- produce authoritative ``items``
- derive compatibility membership indexes
- return counts and rejection evidence

Prohibitions:
- no filesystem access
- no crawling
- no phrase scoring
- no target ranking
- no semantic reasoning
- no link resolution
- no clustering
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Dict, Iterable, List, Mapping, Sequence
from urllib.parse import urlsplit, urlunsplit


SCHEMA_VERSION = "active_target_set_v1"

TARGET_TYPES = {
    "document",
    "draft",
    "imported",
    "live_domain",
}


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _canonical_url(value: Any) -> str:
    raw = _clean_text(value)

    if not raw:
        return ""

    try:
        parsed = urlsplit(raw)
    except Exception:
        return raw.rstrip("/")

    scheme = (parsed.scheme or "https").lower()
    hostname = (parsed.hostname or "").lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    if not hostname:
        return raw.rstrip("/")

    port = parsed.port

    if port and not (
        (scheme == "http" and port == 80)
        or (scheme == "https" and port == 443)
    ):
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname

    path = parsed.path or "/"

    if path != "/":
        path = path.rstrip("/")

    return urlunsplit(
        (
            scheme,
            netloc,
            path,
            parsed.query,
            "",
        )
    )


def _deterministic_target_id(
    *,
    workspace_id: str,
    target_type: str,
    source_id: str,
    canonical_url: str,
) -> str:
    identity = "|".join(
        [
            workspace_id,
            target_type,
            source_id,
            canonical_url,
        ]
    )

    digest = sha256(
        identity.encode("utf-8")
    ).hexdigest()[:32]

    return f"ats_{target_type}_{digest}"


@dataclass(frozen=True)
class ActiveTargetRecord:
    target_id: str
    workspace_id: str
    target_type: str
    source_pool: str
    source_id: str
    url: str
    canonical_url: str
    title: str
    target_status: str
    source_target_id: str
    source_metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "workspace_id": self.workspace_id,
            "target_type": self.target_type,
            "source_pool": self.source_pool,
            "source_id": self.source_id,
            "url": self.url,
            "canonical_url": self.canonical_url,
            "title": self.title,
            "target_status": self.target_status,
            "source_target_id": self.source_target_id,
            "source_metadata": dict(self.source_metadata),
        }


@dataclass(frozen=True)
class ActiveTargetSetResult:
    schema_version: str
    workspace_id: str
    source_counts: Dict[str, int]
    active_counts: Dict[str, int]
    active_document_ids: List[str]
    active_draft_ids: List[str]
    active_imported_urls: List[str]
    active_live_domain_urls: List[str]
    items: List[ActiveTargetRecord]
    rejected_count: int
    rejection_reason_counts: Dict[str, int]
    rejected_examples: List[Dict[str, Any]]

    def item_dicts(self) -> List[Dict[str, Any]]:
        return [
            item.to_dict()
            for item in self.items
        ]

    def to_dict(
        self,
        *,
        generated_at: str,
    ) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "workspace_id": self.workspace_id,
            "generated_at": generated_at,
            "updated_at": generated_at,
            "source_counts": dict(self.source_counts),
            "active_counts": dict(self.active_counts),
            "active_document_ids": list(
                self.active_document_ids
            ),
            "active_draft_ids": list(
                self.active_draft_ids
            ),
            "active_imported_urls": list(
                self.active_imported_urls
            ),
            "active_live_domain_urls": list(
                self.active_live_domain_urls
            ),
            "items": self.item_dicts(),
            "rejected_count": self.rejected_count,
            "rejection_reason_counts": dict(
                self.rejection_reason_counts
            ),
            "rejected_examples": list(
                self.rejected_examples
            ),
        }


def _payload_items(
    payload: Mapping[str, Any] | None,
) -> List[Mapping[str, Any]]:
    if not isinstance(payload, Mapping):
        return []

    raw = payload.get("items") or []

    if isinstance(raw, Mapping):
        values = list(raw.values())
    elif isinstance(raw, Sequence) and not isinstance(
        raw,
        (str, bytes),
    ):
        values = list(raw)
    else:
        values = []

    return [
        item
        for item in values
        if isinstance(item, Mapping)
    ]


def _source_id(
    *,
    target_type: str,
    item: Mapping[str, Any],
    canonical_url: str,
) -> str:
    candidates = {
        "document": [
            item.get("document_id"),
            item.get("source_document_id"),
            item.get("target_id"),
            item.get("url"),
        ],
        "draft": [
            item.get("draft_id"),
            item.get("document_id"),
            item.get("target_id"),
            item.get("url"),
        ],
        "imported": [
            item.get("target_id"),
            item.get("import_id"),
            item.get("url"),
        ],
        "live_domain": [
            item.get("target_id"),
            item.get("canonical_url"),
            item.get("url"),
        ],
    }

    for candidate in candidates[target_type]:
        cleaned = _clean_text(candidate)

        if cleaned:
            return cleaned

    return canonical_url


def _record_url(
    *,
    target_type: str,
    item: Mapping[str, Any],
) -> str:
    candidates: Iterable[Any]

    if target_type == "draft":
        candidates = (
            item.get("published_url"),
            item.get("planned_url"),
            item.get("placeholder_url"),
            item.get("url"),
        )
    else:
        candidates = (
            item.get("canonical_url"),
            item.get("url"),
            item.get("link_target"),
        )

    for candidate in candidates:
        cleaned = _clean_text(candidate)

        if cleaned:
            return cleaned

    return ""


def _record_title(
    item: Mapping[str, Any],
) -> str:
    for candidate in (
        item.get("title"),
        item.get("h1"),
        item.get("label"),
        item.get("topic"),
    ):
        cleaned = _clean_text(candidate)

        if cleaned:
            return cleaned

    return ""


def _normalize_source(
    *,
    workspace_id: str,
    target_type: str,
    source_pool: str,
    payload: Mapping[str, Any] | None,
    rejected_examples: List[Dict[str, Any]],
    rejection_reason_counts: Dict[str, int],
) -> List[ActiveTargetRecord]:
    output: List[ActiveTargetRecord] = []

    for index, item in enumerate(
        _payload_items(payload)
    ):
        item_workspace = _clean_text(
            item.get("workspace_id")
            or (
                payload.get("workspace_id")
                if isinstance(payload, Mapping)
                else ""
            )
        )

        if (
            item_workspace
            and item_workspace != workspace_id
        ):
            reason = "workspace_mismatch"
            rejection_reason_counts[reason] = (
                rejection_reason_counts.get(reason, 0)
                + 1
            )

            if len(rejected_examples) < 25:
                rejected_examples.append(
                    {
                        "target_type": target_type,
                        "index": index,
                        "reason": reason,
                        "workspace_id": item_workspace,
                    }
                )

            continue

        original_url = _record_url(
            target_type=target_type,
            item=item,
        )

        canonical_url = _canonical_url(
            original_url
        )

        if not canonical_url:
            reason = "missing_target_url"
            rejection_reason_counts[reason] = (
                rejection_reason_counts.get(reason, 0)
                + 1
            )

            if len(rejected_examples) < 25:
                rejected_examples.append(
                    {
                        "target_type": target_type,
                        "index": index,
                        "reason": reason,
                    }
                )

            continue

        source_id = _source_id(
            target_type=target_type,
            item=item,
            canonical_url=canonical_url,
        )

        source_target_id = _clean_text(
            item.get("target_id")
        )

        target_id = _deterministic_target_id(
            workspace_id=workspace_id,
            target_type=target_type,
            source_id=source_id,
            canonical_url=canonical_url,
        )

        source_metadata = {
            key: value
            for key, value in item.items()
            if key not in {
                "target_id",
                "workspace_id",
                "url",
                "canonical_url",
                "title",
            }
        }

        output.append(
            ActiveTargetRecord(
                target_id=target_id,
                workspace_id=workspace_id,
                target_type=target_type,
                source_pool=source_pool,
                source_id=source_id,
                url=original_url,
                canonical_url=canonical_url,
                title=_record_title(item),
                target_status="active",
                source_target_id=source_target_id,
                source_metadata=source_metadata,
            )
        )

    return output


def build_active_target_set(
    *,
    workspace_id: str,
    live_domain_payload: Mapping[str, Any] | None = None,
    document_payload: Mapping[str, Any] | None = None,
    imported_payload: Mapping[str, Any] | None = None,
    draft_payload: Mapping[str, Any] | None = None,
) -> ActiveTargetSetResult:
    workspace = _clean_text(workspace_id)

    if not workspace:
        raise ValueError(
            "workspace_id is required"
        )

    sources = [
        (
            "live_domain",
            "live_domain_target_pool",
            live_domain_payload,
        ),
        (
            "document",
            "document_registry_pool",
            document_payload,
        ),
        (
            "imported",
            "imported_target_pool",
            imported_payload,
        ),
        (
            "draft",
            "draft_target_pool",
            draft_payload,
        ),
    ]

    source_counts = {
        target_type: len(
            _payload_items(payload)
        )
        for target_type, _, payload in sources
    }

    rejected_examples: List[Dict[str, Any]] = []
    rejection_reason_counts: Dict[str, int] = {}

    normalized: List[ActiveTargetRecord] = []

    for target_type, source_pool, payload in sources:
        normalized.extend(
            _normalize_source(
                workspace_id=workspace,
                target_type=target_type,
                source_pool=source_pool,
                payload=payload,
                rejected_examples=rejected_examples,
                rejection_reason_counts=(
                    rejection_reason_counts
                ),
            )
        )

    deduplicated: Dict[
        tuple[str, str],
        ActiveTargetRecord,
    ] = {}

    for record in normalized:
        key = (
            record.target_type,
            record.canonical_url,
        )

        if key in deduplicated:
            reason = "duplicate_target"
            rejection_reason_counts[reason] = (
                rejection_reason_counts.get(reason, 0)
                + 1
            )
            continue

        deduplicated[key] = record

    items = sorted(
        deduplicated.values(),
        key=lambda item: (
            item.target_type,
            item.canonical_url,
            item.target_id,
        ),
    )

    active_document_ids = sorted(
        {
            item.source_id
            for item in items
            if item.target_type == "document"
        }
    )

    active_draft_ids = sorted(
        {
            item.source_id
            for item in items
            if item.target_type == "draft"
        }
    )

    active_imported_urls = sorted(
        {
            item.canonical_url
            for item in items
            if item.target_type == "imported"
        }
    )

    active_live_domain_urls = sorted(
        {
            item.canonical_url
            for item in items
            if item.target_type == "live_domain"
        }
    )

    active_counts = {
        "total": len(items),
        "document": len(active_document_ids),
        "draft": len(active_draft_ids),
        "imported": len(active_imported_urls),
        "live_domain": len(
            active_live_domain_urls
        ),
    }

    return ActiveTargetSetResult(
        schema_version=SCHEMA_VERSION,
        workspace_id=workspace,
        source_counts=source_counts,
        active_counts=active_counts,
        active_document_ids=active_document_ids,
        active_draft_ids=active_draft_ids,
        active_imported_urls=(
            active_imported_urls
        ),
        active_live_domain_urls=(
            active_live_domain_urls
        ),
        items=items,
        rejected_count=sum(
            rejection_reason_counts.values()
        ),
        rejection_reason_counts=(
            rejection_reason_counts
        ),
        rejected_examples=rejected_examples,
    )
