"""Canonical Universal Article Body Store Repository.

The Repository is a thin facade over:

- Body Store Writer for persistence;
- Body Store Management Layer for reads and verification.

The Repository does not directly access the filesystem and does not
perform runtime, queue, worker, lifecycle, deletion, semantic, or UUCD
persistence operations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_manager_v1 import (
    body_exists as manager_body_exists,
    get_body_metadata as manager_get_body_metadata,
    list_workspace_bodies as manager_list_workspace_bodies,
    read_body as manager_read_body,
    verify_stored_body as manager_verify_stored_body,
)


BODY_STORE_REPOSITORY_VERSION = (
    "universal_article_body_store_repository_v1"
)


class BodyStoreRepositoryError(
    RuntimeError
):
    """Raised when the Repository contract is used incorrectly."""


def store_body(
    envelope: Mapping[str, Any],
    *,
    project_root: str | Path,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Store one verified body through the canonical Body Store Writer."""

    if not isinstance(
        envelope,
        Mapping,
    ):
        raise BodyStoreRepositoryError(
            "envelope must be a mapping."
        )

    from backend.server.universal_article_body_store.body_store_writer_v1 import (
        write_verified_body_from_envelope_v1,
    )

    return write_verified_body_from_envelope_v1(
        envelope,
        project_root=project_root,
        overwrite=overwrite,
    )


def read_body(
    *,
    project_root: str | Path,
    workspace_id: str,
    body_ref: str | Path,
) -> str:
    """Read one exact stored article body through the Manager."""

    return manager_read_body(
        project_root=project_root,
        workspace_id=workspace_id,
        body_ref=body_ref,
    )


def verify_body(
    *,
    project_root: str | Path,
    workspace_id: str,
    body_ref: str | Path,
    expected_content_hash: str | None = None,
    expected_body_length: int | None = None,
    expected_body_byte_length: int | None = None,
    expected_body_word_count: int | None = None,
) -> dict[str, Any]:
    """Verify one stored body through the Management Layer."""

    return manager_verify_stored_body(
        project_root=project_root,
        workspace_id=workspace_id,
        body_ref=body_ref,
        expected_content_hash=expected_content_hash,
        expected_body_length=expected_body_length,
        expected_body_byte_length=expected_body_byte_length,
        expected_body_word_count=expected_body_word_count,
    )


def body_exists(
    *,
    project_root: str | Path,
    workspace_id: str,
    body_ref: str | Path,
) -> bool:
    """Check body existence through the Management Layer."""

    return manager_body_exists(
        project_root=project_root,
        workspace_id=workspace_id,
        body_ref=body_ref,
    )


def get_metadata(
    *,
    project_root: str | Path,
    workspace_id: str,
    body_ref: str | Path,
) -> dict[str, Any]:
    """Return body metadata through the Management Layer."""

    return manager_get_body_metadata(
        project_root=project_root,
        workspace_id=workspace_id,
        body_ref=body_ref,
    )


def list_workspace_bodies(
    *,
    project_root: str | Path,
    workspace_id: str,
    verify_each: bool = False,
) -> dict[str, Any]:
    """List one workspace's stored bodies through the Manager."""

    return manager_list_workspace_bodies(
        project_root=project_root,
        workspace_id=workspace_id,
        verify_each=verify_each,
    )
