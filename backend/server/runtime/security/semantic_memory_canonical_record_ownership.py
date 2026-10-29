
"""PT3 ? Canonical Semantic Memory record ownership.

A fail-closed validation boundary for certification consumers.

This module does not authenticate users, grant workspace access,
migrate storage, or enable production certification consumption.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from types import MappingProxyType


WORKSPACE_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9_-]{1,128}$"
)

RECORD_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9_.:-]{1,256}$"
)


class CanonicalRecordOwnershipDenied(RuntimeError):
    """Canonical record ownership could not be established."""


def validate_workspace_id(workspace_id: object) -> str:
    """Require an exact, unambiguous workspace identifier."""

    if (
        type(workspace_id) is not str
        or WORKSPACE_ID_PATTERN.fullmatch(workspace_id) is None
    ):
        raise CanonicalRecordOwnershipDenied(
            "Invalid canonical workspace identifier"
        )

    return workspace_id


def validate_record_id(record_id: object) -> str:
    """Require a stable, nonempty record identifier."""

    if (
        type(record_id) is not str
        or RECORD_ID_PATTERN.fullmatch(record_id) is None
    ):
        raise CanonicalRecordOwnershipDenied(
            "Invalid canonical record identifier"
        )

    return record_id


def certify_record_ownership(
    *,
    record: Mapping,
    expected_workspace_id: str,
    expected_record_id: str,
) -> Mapping:
    """Validate exact ownership without modifying the record.

    The expected identifiers must originate from independently
    established certification context, not from untrusted
    record contents.
    """

    workspace_id = validate_workspace_id(
        expected_workspace_id
    )
    record_id = validate_record_id(
        expected_record_id
    )

    if not isinstance(record, Mapping):
        raise CanonicalRecordOwnershipDenied(
            "Canonical record unavailable"
        )

    if (
        record.get("workspace_id") != workspace_id
        or type(record.get("workspace_id")) is not str
    ):
        raise CanonicalRecordOwnershipDenied(
            "Canonical record workspace mismatch"
        )

    if (
        record.get("record_id") != record_id
        or type(record.get("record_id")) is not str
    ):
        raise CanonicalRecordOwnershipDenied(
            "Canonical record identity mismatch"
        )

    return MappingProxyType({
        "record_id": record_id,
        "workspace_id": workspace_id,
        "ownership_verified": True,
        "consumption_authorized": False,
        "fully_certified": False,
    })


def certify_record_collection_ownership(
    *,
    records: object,
    expected_workspace_id: str,
) -> tuple[Mapping, ...]:
    """Reject an entire collection if any record is unowned.

    No partial certification is returned.
    """

    workspace_id = validate_workspace_id(
        expected_workspace_id
    )

    if type(records) not in (list, tuple):
        raise CanonicalRecordOwnershipDenied(
            "Invalid canonical record collection"
        )

    seen = set()
    results = []

    for record in records:
        if not isinstance(record, Mapping):
            raise CanonicalRecordOwnershipDenied(
                "Invalid canonical record"
            )

        record_id = record.get("record_id")

        result = certify_record_ownership(
            record=record,
            expected_workspace_id=workspace_id,
            expected_record_id=record_id,
        )

        if record_id in seen:
            raise CanonicalRecordOwnershipDenied(
                "Duplicate canonical record identity"
            )

        seen.add(record_id)
        results.append(result)

    return tuple(results)
