"""Canonical Universal Article Body Store package."""

from .body_store_manager_v1 import (
    BODY_STORE_MANAGER_VERSION,
    BodyStoreAccessError,
    BodyStoreCorruptionError,
    BodyStoreMissingError,
    body_exists,
    get_body_metadata,
    list_workspace_bodies,
    locate_body,
    read_body,
    verify_stored_body,
)

from .body_store_writer_v1 import (
    BODY_STORE_WRITER_VERSION,
    BodyStoreContractError,
    write_verified_body_from_envelope_v1,
)

__all__ = [
    "BODY_STORE_MANAGER_VERSION",
    "BODY_STORE_WRITER_VERSION",
    "BodyStoreAccessError",
    "BodyStoreContractError",
    "BodyStoreCorruptionError",
    "BodyStoreMissingError",
    "body_exists",
    "get_body_metadata",
    "list_workspace_bodies",
    "locate_body",
    "read_body",
    "verify_stored_body",
    "write_verified_body_from_envelope_v1",
]
