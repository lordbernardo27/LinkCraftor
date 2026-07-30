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
    "BODY_STORE_REPOSITORY_VERSION",
    "BodyStoreRepositoryError",
    "repository_body_exists",
    "repository_get_metadata",
    "repository_list_workspace_bodies",
    "repository_read_body",
    "repository_store_body",
    "repository_verify_body",
]

from .body_store_repository_v1 import (
    BODY_STORE_REPOSITORY_VERSION,
    BodyStoreRepositoryError,
    body_exists as repository_body_exists,
    get_metadata as repository_get_metadata,
    list_workspace_bodies as repository_list_workspace_bodies,
    read_body as repository_read_body,
    store_body as repository_store_body,
    verify_body as repository_verify_body,
)
