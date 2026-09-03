from __future__ import annotations

from typing import Any, Mapping

from backend.server.stores.source_lifecycle_control import (
    _event_id,
    _now_iso,
    _record_event,
    authorize_semantic_processing,
    authorize_source,
    load_lifecycle_control,
    register_or_update_source,
    save_lifecycle_control,
    update_source_version,
)


PERSISTED_UUCD_SOURCE_GOVERNANCE_VERSION = (
    "persisted_uucd_source_governance_v1"
)


class PersistedUUCDSourceGovernanceError(ValueError):
    """Raised when a persisted UUCD cannot enter source governance."""


def _require_string(
    record: Mapping[str, Any],
    field: str,
) -> str:
    value = str(
        record.get(field) or ""
    ).strip()

    if not value:
        raise PersistedUUCDSourceGovernanceError(
            f"{field} is required."
        )

    return value


def _source_key(
    source_type: str,
    source_id: str,
) -> str:
    return f"{source_type}::{source_id}"


def _matching_version(
    source: Mapping[str, Any],
    *,
    document_id: str,
    content_hash: str,
) -> Mapping[str, Any] | None:
    versions = source.get("versions")

    if not isinstance(versions, list):
        return None

    for version in versions:
        if not isinstance(version, Mapping):
            continue

        if (
            str(
                version.get("content_hash") or ""
            ).strip()
            != content_hash
        ):
            continue

        document_ids = version.get(
            "document_ids"
        )

        if (
            isinstance(document_ids, list)
            and document_id in document_ids
        ):
            return version

    return None


def govern_persisted_uucd_source_v1(
    persisted_uucd_record: Mapping[str, Any],
    *,
    authorized_by: str = "system",
) -> dict[str, Any]:
    """
    Register and authorize one PERSISTED_AND_VERIFIED UUCD source.

    Repeated processing of the same document_id + content_hash reuses
    the existing source version instead of appending a duplicate version.
    """

    if not isinstance(
        persisted_uucd_record,
        Mapping,
    ):
        raise PersistedUUCDSourceGovernanceError(
            "persisted_uucd_record must be a mapping."
        )

    if (
        persisted_uucd_record.get("schema_version")
        != "universal_unified_content_document_v2"
    ):
        raise PersistedUUCDSourceGovernanceError(
            "Unsupported persisted UUCD schema."
        )

    if (
        persisted_uucd_record.get("body_status")
        != "STORED_AND_VERIFIED"
    ):
        raise PersistedUUCDSourceGovernanceError(
            "UUCD body is not STORED_AND_VERIFIED."
        )

    persistence = persisted_uucd_record.get(
        "persistence"
    )

    if not isinstance(
        persistence,
        Mapping,
    ):
        raise PersistedUUCDSourceGovernanceError(
            "UUCD persistence evidence is missing."
        )

    if (
        persistence.get("persistence_status")
        != "PERSISTED_AND_VERIFIED"
    ):
        raise PersistedUUCDSourceGovernanceError(
            "UUCD is not PERSISTED_AND_VERIFIED."
        )

    if (
        persistence.get(
            "content_body_stored_here"
        )
        is not False
    ):
        raise PersistedUUCDSourceGovernanceError(
            "Persisted UUCD must remain bodyless."
        )

    handoff = persisted_uucd_record.get(
        "handoff"
    )

    if (
        not isinstance(handoff, Mapping)
        or handoff.get("uucd_persisted") is not True
        or handoff.get("body_store_verified") is not True
    ):
        raise PersistedUUCDSourceGovernanceError(
            "Persisted UUCD handoff evidence is incomplete."
        )

    workspace_id = _require_string(
        persisted_uucd_record,
        "workspace_id",
    )
    source_type = _require_string(
        persisted_uucd_record,
        "source_type",
    )
    source_id = _require_string(
        persisted_uucd_record,
        "source_id",
    )
    document_id = _require_string(
        persisted_uucd_record,
        "document_id",
    )
    content_hash = _require_string(
        persisted_uucd_record,
        "content_hash",
    )
    content_ref = _require_string(
        persisted_uucd_record,
        "content_ref",
    )
    body_ref = _require_string(
        persisted_uucd_record,
        "body_ref",
    )

    source_name = str(
        persisted_uucd_record.get(
            "source_name"
        )
        or persisted_uucd_record.get(
            "title"
        )
        or source_id
    ).strip()

    key = _source_key(
        source_type,
        source_id,
    )

    desired_metadata = {
        "content_ref":
            content_ref,
        "body_ref":
            body_ref,
        "content_hash":
            content_hash,
        "registration_basis":
            "persisted_and_verified_uucd",
    }

    registry = load_lifecycle_control(
        workspace_id
    )

    existing = (
        registry.get("sources", {})
        .get(key)
    )

    registration_action = "REUSED"

    registration_needed = (
        not isinstance(existing, Mapping)
        or existing.get("status") != "active"
        or document_id
        not in (
            existing.get("document_ids")
            if isinstance(
                existing.get("document_ids"),
                list,
            )
            else []
        )
        or any(
            (
                existing.get("metadata")
                if isinstance(
                    existing.get("metadata"),
                    Mapping,
                )
                else {}
            ).get(metadata_key)
            != metadata_value
            for metadata_key, metadata_value
            in desired_metadata.items()
        )
    )

    if registration_needed:
        register_or_update_source(
            workspace_id=workspace_id,
            source_type=source_type,
            source_id=source_id,
            source_name=source_name,
            document_ids=[document_id],
            metadata=desired_metadata,
        )
        registration_action = (
            "REGISTERED_OR_UPDATED"
        )

    registry = load_lifecycle_control(
        workspace_id
    )
    source = (
        registry.get("sources", {})
        .get(key)
    )

    if not isinstance(source, Mapping):
        raise PersistedUUCDSourceGovernanceError(
            "Source registration did not produce a lifecycle record."
        )

    authorization_action = "REUSED"

    if (
        source.get("authorization_status")
        != "AUTHORIZED"
        or source.get(
            "workspace_authorized"
        )
        is not True
    ):
        authorize_source(
            workspace_id=workspace_id,
            source_type=source_type,
            source_id=source_id,
            authorization_basis=(
                "persisted_uucd_workspace_identity_verified"
            ),
            authorized_by=authorized_by,
            reason=(
                "Canonical persisted UUCD source governance handoff."
            ),
        )
        authorization_action = "AUTHORIZED"

    registry = load_lifecycle_control(
        workspace_id
    )
    source = (
        registry.get("sources", {})
        .get(key)
    )

    if not isinstance(source, Mapping):
        raise PersistedUUCDSourceGovernanceError(
            "Authorized source record is unavailable."
        )

    matching_version = _matching_version(
        source,
        document_id=document_id,
        content_hash=content_hash,
    )

    version_action = "REUSED"

    if matching_version is None:
        version_result = update_source_version(
            workspace_id=workspace_id,
            source_type=source_type,
            source_id=source_id,
            document_ids=[document_id],
            content_hash=content_hash,
            reason=(
                "Canonical persisted UUCD version alignment."
            ),
        )
        matching_version = version_result.get(
            "version"
        )
        version_action = "VERSION_REGISTERED"

    registry = load_lifecycle_control(
        workspace_id
    )
    source = (
        registry.get("sources", {})
        .get(key)
    )

    if not isinstance(source, Mapping):
        raise PersistedUUCDSourceGovernanceError(
            "Version-aligned source record is unavailable."
        )

    semantic_action = "REUSED"

    if (
        source.get(
            "semantic_processing_authorized"
        )
        is not True
        or source.get(
            "semantic_authorization_status"
        )
        != "AUTHORIZED"
        or source.get(
            "active_semantic_processing"
        )
        is not True
    ):
        authorize_semantic_processing(
            workspace_id=workspace_id,
            source_type=source_type,
            source_id=source_id,
            authorized_by=authorized_by,
            reason=(
                "Canonical persisted UUCD semantic authorization."
            ),
        )
        semantic_action = (
            "SEMANTIC_PROCESSING_AUTHORIZED"
        )

    registry = load_lifecycle_control(
        workspace_id
    )
    source = (
        registry.get("sources", {})
        .get(key)
    )

    if not isinstance(source, Mapping):
        raise PersistedUUCDSourceGovernanceError(
            "Final governed source record is unavailable."
        )

    return {
        "schema_version":
            "persisted_uucd_source_governance_result_v1",
        "governance_version":
            PERSISTED_UUCD_SOURCE_GOVERNANCE_VERSION,
        "status":
            "SOURCE_GOVERNANCE_COMPLETE",
        "workspace_id":
            workspace_id,
        "source_key":
            key,
        "source_type":
            source_type,
        "source_id":
            source_id,
        "document_id":
            document_id,
        "content_hash":
            content_hash,
        "registration_action":
            registration_action,
        "authorization_action":
            authorization_action,
        "version_action":
            version_action,
        "semantic_authorization_action":
            semantic_action,
        "snapshot_id":
            source.get(
                "latest_snapshot_id"
            ),
        "asset_version_id":
            source.get(
                "latest_asset_version_id"
            ),
        "version_status":
            source.get(
                "version_status"
            ),
        "workspace_authorized":
            source.get(
                "workspace_authorized"
            ),
        "semantic_processing_authorized":
            source.get(
                "semantic_processing_authorized"
            ),
        "next_stage":
            "semantic_readiness_gate",
    }


def backfill_persisted_uucd_sources_v1(
    persisted_uucd_records: list[Mapping[str, Any]],
    *,
    workspace_id: str,
    source_type: str = "website",
    authorized_by: str = "system",
) -> dict[str, Any]:
    """
    Transactionally govern a legacy corpus of already-persisted UUCD records.

    The lifecycle registry is loaded once, mutated in memory, and saved once.
    Existing equivalent governance state is reused without duplicate versions
    or duplicate governance events.
    """

    normalized_workspace_id = str(
        workspace_id or ""
    ).strip()

    normalized_source_type = str(
        source_type or ""
    ).strip()

    if not normalized_workspace_id:
        raise PersistedUUCDSourceGovernanceError(
            "workspace_id is required."
        )

    if not normalized_source_type:
        raise PersistedUUCDSourceGovernanceError(
            "source_type is required."
        )

    if not isinstance(
        persisted_uucd_records,
        list,
    ):
        raise PersistedUUCDSourceGovernanceError(
            "persisted_uucd_records must be a list."
        )

    registry = load_lifecycle_control(
        normalized_workspace_id
    )

    sources = registry.setdefault(
        "sources",
        {},
    )

    if not isinstance(sources, dict):
        raise PersistedUUCDSourceGovernanceError(
            "Lifecycle sources registry is invalid."
        )

    seen_source_keys: set[str] = set()
    seen_document_ids: set[str] = set()

    counts = {
        "input_records": 0,
        "registered_or_updated": 0,
        "registration_reused": 0,
        "authorized": 0,
        "authorization_reused": 0,
        "versions_registered": 0,
        "versions_reused": 0,
        "semantic_authorized": 0,
        "semantic_authorization_reused": 0,
    }

    governed_sources: list[dict[str, Any]] = []

    for record in persisted_uucd_records:

        counts["input_records"] += 1

        if not isinstance(record, Mapping):
            raise PersistedUUCDSourceGovernanceError(
                "Every backfill record must be a mapping."
            )

        if (
            record.get("schema_version")
            != "universal_unified_content_document_v2"
        ):
            raise PersistedUUCDSourceGovernanceError(
                "Backfill encountered unsupported UUCD schema."
            )

        if (
            record.get("body_status")
            != "STORED_AND_VERIFIED"
        ):
            raise PersistedUUCDSourceGovernanceError(
                "Backfill encountered unverified Body Store state."
            )

        persistence = record.get(
            "persistence"
        )

        if (
            not isinstance(persistence, Mapping)
            or persistence.get(
                "persistence_status"
            )
            != "PERSISTED_AND_VERIFIED"
            or persistence.get(
                "content_body_stored_here"
            )
            is not False
        ):
            raise PersistedUUCDSourceGovernanceError(
                "Backfill encountered invalid persistence state."
            )

        handoff = record.get(
            "handoff"
        )

        if (
            not isinstance(handoff, Mapping)
            or handoff.get(
                "uucd_persisted"
            )
            is not True
            or handoff.get(
                "body_store_verified"
            )
            is not True
        ):
            raise PersistedUUCDSourceGovernanceError(
                "Backfill encountered invalid handoff evidence."
            )

        record_workspace_id = _require_string(
            record,
            "workspace_id",
        )
        record_source_type = _require_string(
            record,
            "source_type",
        )
        source_id = _require_string(
            record,
            "source_id",
        )
        document_id = _require_string(
            record,
            "document_id",
        )
        content_hash = _require_string(
            record,
            "content_hash",
        )
        content_ref = _require_string(
            record,
            "content_ref",
        )
        body_ref = _require_string(
            record,
            "body_ref",
        )

        if (
            record_workspace_id
            != normalized_workspace_id
        ):
            raise PersistedUUCDSourceGovernanceError(
                "Backfill workspace identity mismatch."
            )

        if (
            record_source_type
            != normalized_source_type
        ):
            raise PersistedUUCDSourceGovernanceError(
                "Backfill source_type mismatch."
            )

        key = _source_key(
            record_source_type,
            source_id,
        )

        if key in seen_source_keys:
            raise PersistedUUCDSourceGovernanceError(
                f"Duplicate source identity in backfill: {key}"
            )

        if document_id in seen_document_ids:
            raise PersistedUUCDSourceGovernanceError(
                "Duplicate document_id in backfill: "
                + document_id
            )

        seen_source_keys.add(key)
        seen_document_ids.add(document_id)

        source_name = str(
            record.get("source_name")
            or record.get("title")
            or source_id
        ).strip()

        desired_metadata = {
            "content_ref":
                content_ref,
            "body_ref":
                body_ref,
            "content_hash":
                content_hash,
            "registration_basis":
                "persisted_and_verified_uucd",
        }

        existing = sources.get(
            key
        )

        existing_metadata = (
            existing.get("metadata")
            if isinstance(
                existing,
                Mapping,
            )
            and isinstance(
                existing.get("metadata"),
                Mapping,
            )
            else {}
        )

        existing_document_ids = (
            existing.get("document_ids")
            if isinstance(
                existing,
                Mapping,
            )
            and isinstance(
                existing.get("document_ids"),
                list,
            )
            else []
        )

        registration_needed = (
            not isinstance(existing, Mapping)
            or existing.get("status")
            != "active"
            or document_id
            not in existing_document_ids
            or any(
                existing_metadata.get(
                    metadata_key
                )
                != metadata_value
                for (
                    metadata_key,
                    metadata_value,
                )
                in desired_metadata.items()
            )
        )

        if registration_needed:

            now = _now_iso()

            current = (
                dict(existing)
                if isinstance(
                    existing,
                    Mapping,
                )
                else {}
            )

            current_document_ids = (
                current.get(
                    "document_ids"
                )
                if isinstance(
                    current.get(
                        "document_ids"
                    ),
                    list,
                )
                else []
            )

            current_metadata = (
                current.get("metadata")
                if isinstance(
                    current.get(
                        "metadata"
                    ),
                    Mapping,
                )
                else {}
            )

            source = {
                **current,
                "source_key":
                    key,
                "source_type":
                    record_source_type,
                "source_id":
                    source_id,
                "source_name":
                    source_name
                    or current.get(
                        "source_name",
                        "",
                    ),
                "status":
                    "active",
                "document_ids":
                    sorted(
                        set(
                            current_document_ids
                            + [document_id]
                        )
                    ),
                "metadata": {
                    **current_metadata,
                    **desired_metadata,
                },
                "updated_at":
                    now,
            }

            source.setdefault(
                "created_at",
                now,
            )

            sources[key] = source

            _record_event(
                registry,
                event_type=(
                    "source_registered_or_updated"
                ),
                source_type=(
                    record_source_type
                ),
                source_id=source_id,
                document_ids=[
                    document_id
                ],
                metadata=(
                    desired_metadata
                ),
            )

            counts[
                "registered_or_updated"
            ] += 1

        else:
            source = existing
            counts[
                "registration_reused"
            ] += 1

        if not isinstance(
            source,
            dict,
        ):
            raise PersistedUUCDSourceGovernanceError(
                "Backfill source registration failed."
            )

        if (
            source.get(
                "authorization_status"
            )
            != "AUTHORIZED"
            or source.get(
                "workspace_authorized"
            )
            is not True
        ):
            now = _now_iso()

            source[
                "authorization_status"
            ] = "AUTHORIZED"
            source[
                "workspace_authorized"
            ] = True
            source[
                "authorization_basis"
            ] = (
                "persisted_uucd_"
                "workspace_identity_verified"
            )
            source[
                "authorized_by"
            ] = str(
                authorized_by
                or "system"
            )
            source[
                "authorized_at"
            ] = now
            source[
                "updated_at"
            ] = now

            _record_event(
                registry,
                event_type=(
                    "source_authorized"
                ),
                source_type=(
                    record_source_type
                ),
                source_id=source_id,
                document_ids=source.get(
                    "document_ids",
                    [],
                ),
                reason=(
                    "Canonical persisted UUCD "
                    "source governance backfill."
                ),
                metadata={
                    "authorization_status":
                        "AUTHORIZED",
                    "workspace_authorized":
                        True,
                    "authorization_basis":
                        source[
                            "authorization_basis"
                        ],
                    "authorized_by":
                        source[
                            "authorized_by"
                        ],
                },
            )

            counts[
                "authorized"
            ] += 1

        else:
            counts[
                "authorization_reused"
            ] += 1

        matching_version = _matching_version(
            source,
            document_id=document_id,
            content_hash=content_hash,
        )

        if matching_version is None:

            now = _now_iso()

            version_record = {
                "snapshot_id":
                    _event_id(
                        "snapshot",
                        record_source_type,
                        source_id,
                        content_hash,
                    ),
                "asset_version_id":
                    _event_id(
                        "asset",
                        record_source_type,
                        source_id,
                        content_hash,
                    ),
                "content_hash":
                    content_hash,
                "document_ids": [
                    document_id
                ],
                "created_at":
                    now,
            }

            versions = source.setdefault(
                "versions",
                [],
            )

            if not isinstance(
                versions,
                list,
            ):
                raise PersistedUUCDSourceGovernanceError(
                    "Source versions registry is invalid."
                )

            versions.append(
                version_record
            )

            source[
                "status"
            ] = "active"
            source[
                "sync_allowed"
            ] = True
            source[
                "latest_snapshot_id"
            ] = version_record[
                "snapshot_id"
            ]
            source[
                "latest_asset_version_id"
            ] = version_record[
                "asset_version_id"
            ]
            source[
                "version_status"
            ] = (
                "VERSION_REGISTRY_ALIGNED"
            )
            source[
                "updated_at"
            ] = now

            _record_event(
                registry,
                event_type=(
                    "source_updated"
                ),
                source_type=(
                    record_source_type
                ),
                source_id=source_id,
                document_ids=[
                    document_id
                ],
                reason=(
                    "Canonical persisted UUCD "
                    "version backfill."
                ),
                metadata=version_record,
            )

            matching_version = (
                version_record
            )

            counts[
                "versions_registered"
            ] += 1

        else:
            counts[
                "versions_reused"
            ] += 1

            source[
                "latest_snapshot_id"
            ] = matching_version.get(
                "snapshot_id"
            )
            source[
                "latest_asset_version_id"
            ] = matching_version.get(
                "asset_version_id"
            )
            source[
                "version_status"
            ] = (
                "VERSION_REGISTRY_ALIGNED"
            )

        if (
            source.get(
                "semantic_processing_authorized"
            )
            is not True
            or source.get(
                "semantic_authorization_status"
            )
            != "AUTHORIZED"
            or source.get(
                "active_semantic_processing"
            )
            is not True
        ):
            now = _now_iso()

            source[
                "active_semantic_processing"
            ] = True
            source[
                "semantic_processing_authorized"
            ] = True
            source[
                "semantic_authorization_status"
            ] = "AUTHORIZED"
            source[
                "semantic_authorized_by"
            ] = str(
                authorized_by
                or "system"
            )
            source[
                "semantic_authorized_at"
            ] = now
            source[
                "updated_at"
            ] = now

            _record_event(
                registry,
                event_type=(
                    "semantic_processing_authorized"
                ),
                source_type=(
                    record_source_type
                ),
                source_id=source_id,
                document_ids=source.get(
                    "document_ids",
                    [],
                ),
                reason=(
                    "Canonical persisted UUCD "
                    "semantic authorization backfill."
                ),
                metadata={
                    "semantic_processing_authorized":
                        True,
                    "semantic_authorization_status":
                        "AUTHORIZED",
                    "authorized_by":
                        source[
                            "semantic_authorized_by"
                        ],
                },
            )

            counts[
                "semantic_authorized"
            ] += 1

        else:
            counts[
                "semantic_authorization_reused"
            ] += 1

        governed_sources.append({
            "source_key":
                key,
            "document_id":
                document_id,
            "content_hash":
                content_hash,
            "snapshot_id":
                source.get(
                    "latest_snapshot_id"
                ),
            "asset_version_id":
                source.get(
                    "latest_asset_version_id"
                ),
        })

    save_path = save_lifecycle_control(
        normalized_workspace_id,
        registry,
    )

    return {
        "schema_version":
            "persisted_uucd_source_governance_backfill_result_v1",
        "governance_version":
            PERSISTED_UUCD_SOURCE_GOVERNANCE_VERSION,
        "status":
            "SOURCE_GOVERNANCE_BACKFILL_COMPLETE",
        "workspace_id":
            normalized_workspace_id,
        "source_type":
            normalized_source_type,
        "counts":
            counts,
        "governed_source_count":
            len(governed_sources),
        "registry_path":
            str(save_path),
        "saved_once":
            True,
        "next_stage":
            "semantic_readiness_gate",
    }


__all__ = [
    "PERSISTED_UUCD_SOURCE_GOVERNANCE_VERSION",
    "PersistedUUCDSourceGovernanceError",
    "govern_persisted_uucd_source_v1",
    "backfill_persisted_uucd_sources_v1",
]
