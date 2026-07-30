"""Read-only Universal Article Body Store Management Layer.

This module locates, reads, lists, and verifies bodies already written
to the Universal Article Body Store.

It does not:
- write or modify article bodies;
- delete or purge article bodies;
- persist UUCD records;
- perform semantic processing;
- create jobs, queues, workers, or Runtime Registration.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from backend.server.common.text_statistics import count_words
from typing import Any, Mapping


BODY_STORE_MANAGER_VERSION = (
    "universal_article_body_store_manager_v1"
)

BODY_STORE_ROOT_RELATIVE = (
    Path("backend")
    / "server"
    / "data"
    / "universal_article_body_store"
)

WORKSPACE_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$"
)

DOCUMENT_ID_PATTERN = re.compile(
    r"^uucd_[a-f0-9]{32}$"
)

SHA256_PATTERN = re.compile(
    r"^[a-f0-9]{64}$"
)


class BodyStoreAccessError(
    ValueError
):
    """Raised when a Body Store path or access request is invalid."""


class BodyStoreMissingError(
    FileNotFoundError
):
    """Raised when a requested stored body does not exist."""


class BodyStoreCorruptionError(
    RuntimeError
):
    """Raised when a stored body fails integrity verification."""


def _require_non_empty_string(
    value: Any,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise BodyStoreAccessError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise BodyStoreAccessError(
            field_name
            + " must not be empty."
        )

    return normalized


def _require_workspace_id(
    workspace_id: Any,
) -> str:
    normalized = _require_non_empty_string(
        workspace_id,
        field_name="workspace_id",
    )

    if not WORKSPACE_PATTERN.fullmatch(
        normalized
    ):
        raise BodyStoreAccessError(
            "workspace_id contains invalid characters."
        )

    return normalized


def _require_document_id(
    document_id: Any,
) -> str:
    normalized = _require_non_empty_string(
        document_id,
        field_name="document_id",
    )

    if not DOCUMENT_ID_PATTERN.fullmatch(
        normalized
    ):
        raise BodyStoreAccessError(
            "document_id does not match the canonical UUCD format."
        )

    return normalized


def _project_root(
    project_root: str | Path,
) -> Path:
    root = Path(
        project_root
    ).resolve()

    if not root.exists():
        raise BodyStoreAccessError(
            "project_root does not exist."
        )

    if not root.is_dir():
        raise BodyStoreAccessError(
            "project_root must be a directory."
        )

    return root


def _store_root(
    *,
    project_root: Path,
) -> Path:
    return (
        project_root
        / BODY_STORE_ROOT_RELATIVE
    ).resolve()


def _workspace_body_root(
    *,
    project_root: Path,
    workspace_id: str,
) -> Path:
    return (
        _store_root(
            project_root=project_root,
        )
        / workspace_id
        / "bodies"
    ).resolve()


def _is_inside(
    candidate: Path,
    parent: Path,
) -> bool:
    try:
        candidate.relative_to(
            parent
        )

        return True

    except ValueError:
        return False


def _validate_body_path(
    *,
    project_root: Path,
    workspace_id: str,
    body_ref: str | Path,
) -> tuple[Path, Path]:
    workspace_root = (
        _workspace_body_root(
            project_root=project_root,
            workspace_id=workspace_id,
        )
    )

    supplied_path = Path(
        body_ref
    )

    if supplied_path.is_absolute():
        body_path = supplied_path.resolve()

    else:
        body_path = (
            project_root
            / supplied_path
        ).resolve()

    if not _is_inside(
        body_path,
        workspace_root,
    ):
        raise BodyStoreAccessError(
            "body_ref escapes the canonical workspace Body Store."
        )

    if body_path.parent != workspace_root:
        raise BodyStoreAccessError(
            "body_ref must point directly inside the workspace bodies directory."
        )

    if body_path.suffix.casefold() != ".txt":
        raise BodyStoreAccessError(
            "Body Store files must use the .txt extension."
        )

    return (
        workspace_root,
        body_path,
    )


def _body_ref_from_path(
    *,
    project_root: Path,
    body_path: Path,
) -> str:
    return body_path.relative_to(
        project_root
    ).as_posix()


def _sha256_bytes(
    payload: bytes,
) -> str:
    return hashlib.sha256(
        payload
    ).hexdigest()


def _count_words(
    content_body: str,
) -> int:
    return count_words(
        content_body
    )


def _read_utf8_body(
    body_path: Path,
) -> tuple[bytes, str]:
    if not body_path.exists():
        raise BodyStoreMissingError(
            "Stored article body does not exist: "
            + str(
                body_path
            )
        )

    if not body_path.is_file():
        raise BodyStoreAccessError(
            "Body Store path is not a file."
        )

    if body_path.is_symlink():
        raise BodyStoreAccessError(
            "Symbolic-link Body Store files are not allowed."
        )

    stored_bytes = body_path.read_bytes()

    try:
        stored_body = stored_bytes.decode(
            "utf-8"
        )

    except UnicodeDecodeError as exc:
        raise BodyStoreCorruptionError(
            "Stored article body is not valid UTF-8."
        ) from exc

    return (
        stored_bytes,
        stored_body,
    )


def locate_body(
    *,
    project_root: str | Path,
    workspace_id: str,
    body_ref: str | Path,
    require_exists: bool = True,
) -> Path:
    """Return the canonical absolute path for one workspace body."""

    root = _project_root(
        project_root
    )

    workspace = _require_workspace_id(
        workspace_id
    )

    (
        workspace_body_root,
        body_path,
    ) = _validate_body_path(
        project_root=root,
        workspace_id=workspace,
        body_ref=body_ref,
    )

    if workspace_body_root.is_symlink():
        raise BodyStoreAccessError(
            "Workspace Body Store directory must not be a symbolic link."
        )

    if require_exists:
        if not body_path.exists():
            raise BodyStoreMissingError(
                "Stored article body does not exist: "
                + str(
                    body_path
                )
            )

        if not body_path.is_file():
            raise BodyStoreAccessError(
                "Located Body Store path is not a file."
            )

        if body_path.is_symlink():
            raise BodyStoreAccessError(
                "Symbolic-link Body Store files are not allowed."
            )

    return body_path


def body_exists(
    *,
    project_root: str | Path,
    workspace_id: str,
    body_ref: str | Path,
) -> bool:
    """Return True only when the canonical body exists as a regular file."""

    try:
        body_path = locate_body(
            project_root=project_root,
            workspace_id=workspace_id,
            body_ref=body_ref,
            require_exists=False,
        )

    except BodyStoreAccessError:
        raise

    return (
        body_path.exists()
        and body_path.is_file()
        and not body_path.is_symlink()
    )


def read_body(
    *,
    project_root: str | Path,
    workspace_id: str,
    body_ref: str | Path,
) -> str:
    """Read and return one exact UTF-8 article body."""

    body_path = locate_body(
        project_root=project_root,
        workspace_id=workspace_id,
        body_ref=body_ref,
        require_exists=True,
    )

    (
        _stored_bytes,
        stored_body,
    ) = _read_utf8_body(
        body_path
    )

    return stored_body


def verify_stored_body(
    *,
    project_root: str | Path,
    workspace_id: str,
    body_ref: str | Path,
    expected_content_hash: str | None = None,
    expected_body_length: int | None = None,
    expected_body_byte_length: int | None = None,
    expected_body_word_count: int | None = None,
) -> dict[str, Any]:
    """Verify one stored body against optional UUCD/certificate values."""

    body_path = locate_body(
        project_root=project_root,
        workspace_id=workspace_id,
        body_ref=body_ref,
        require_exists=True,
    )

    (
        stored_bytes,
        stored_body,
    ) = _read_utf8_body(
        body_path
    )

    content_hash = _sha256_bytes(
        stored_bytes
    )

    body_length = len(
        stored_body
    )

    body_byte_length = len(
        stored_bytes
    )

    body_word_count = _count_words(
        stored_body
    )

    checks: dict[str, bool] = {
        "file_exists":
            True,

        "regular_file":
            body_path.is_file(),

        "not_symlink":
            not body_path.is_symlink(),

        "utf8_valid":
            True,
    }

    if expected_content_hash is not None:
        normalized_hash = _require_non_empty_string(
            expected_content_hash,
            field_name="expected_content_hash",
        ).casefold()

        if not SHA256_PATTERN.fullmatch(
            normalized_hash
        ):
            raise BodyStoreAccessError(
                "expected_content_hash must be a lowercase SHA-256 digest."
            )

        checks[
            "content_hash_verified"
        ] = (
            content_hash
            == normalized_hash
        )

    if expected_body_length is not None:
        if (
            not isinstance(
                expected_body_length,
                int,
            )
            or expected_body_length < 0
        ):
            raise BodyStoreAccessError(
                "expected_body_length must be a non-negative integer."
            )

        checks[
            "body_length_verified"
        ] = (
            body_length
            == expected_body_length
        )

    if expected_body_byte_length is not None:
        if (
            not isinstance(
                expected_body_byte_length,
                int,
            )
            or expected_body_byte_length < 0
        ):
            raise BodyStoreAccessError(
                "expected_body_byte_length must be a non-negative integer."
            )

        checks[
            "body_byte_length_verified"
        ] = (
            body_byte_length
            == expected_body_byte_length
        )

    if expected_body_word_count is not None:
        if (
            not isinstance(
                expected_body_word_count,
                int,
            )
            or expected_body_word_count < 0
        ):
            raise BodyStoreAccessError(
                "expected_body_word_count must be a non-negative integer."
            )

        checks[
            "body_word_count_verified"
        ] = (
            body_word_count
            == expected_body_word_count
        )

    failed_checks = sorted(
        name
        for name, passed
        in checks.items()
        if passed is not True
    )

    if failed_checks:
        raise BodyStoreCorruptionError(
            "Stored body failed integrity verification: "
            + ", ".join(
                failed_checks
            )
        )

    root = _project_root(
        project_root
    )

    return {
        "verification_schema_version":
            "stored_body_verification_v1",

        "manager_version":
            BODY_STORE_MANAGER_VERSION,

        "verification_status":
            "VERIFIED",

        "workspace_id":
            workspace_id,

        "body_ref":
            _body_ref_from_path(
                project_root=root,
                body_path=body_path,
            ),

        "stored_path":
            str(
                body_path
            ),

        "content_hash":
            content_hash,

        "body_length":
            body_length,

        "body_byte_length":
            body_byte_length,

        "body_word_count":
            body_word_count,

        "checks":
            checks,

        "body_returned":
            False,

        "body_modified":
            False,
    }


def get_body_metadata(
    *,
    project_root: str | Path,
    workspace_id: str,
    body_ref: str | Path,
) -> dict[str, Any]:
    """Return calculated metadata without returning the body content."""

    verification = verify_stored_body(
        project_root=project_root,
        workspace_id=workspace_id,
        body_ref=body_ref,
    )

    body_path = Path(
        verification[
            "stored_path"
        ]
    )

    stat = body_path.stat()

    return {
        "metadata_schema_version":
            "stored_body_metadata_v1",

        "manager_version":
            BODY_STORE_MANAGER_VERSION,

        "workspace_id":
            workspace_id,

        "body_ref":
            verification[
                "body_ref"
            ],

        "stored_path":
            verification[
                "stored_path"
            ],

        "filename":
            body_path.name,

        "file_extension":
            body_path.suffix.casefold(),

        "content_hash":
            verification[
                "content_hash"
            ],

        "body_length":
            verification[
                "body_length"
            ],

        "body_byte_length":
            verification[
                "body_byte_length"
            ],

        "body_word_count":
            verification[
                "body_word_count"
            ],

        "modified_timestamp":
            stat.st_mtime,

        "body_included":
            False,
    }


def list_workspace_bodies(
    *,
    project_root: str | Path,
    workspace_id: str,
    verify_each: bool = False,
) -> dict[str, Any]:
    """List regular .txt bodies directly inside one workspace store."""

    root = _project_root(
        project_root
    )

    workspace = _require_workspace_id(
        workspace_id
    )

    workspace_body_root = (
        _workspace_body_root(
            project_root=root,
            workspace_id=workspace,
        )
    )

    if workspace_body_root.is_symlink():
        raise BodyStoreAccessError(
            "Workspace Body Store directory must not be a symbolic link."
        )

    if not workspace_body_root.exists():
        return {
            "listing_schema_version":
                "workspace_body_listing_v1",

            "manager_version":
                BODY_STORE_MANAGER_VERSION,

            "workspace_id":
                workspace,

            "workspace_body_root":
                str(
                    workspace_body_root
                ),

            "workspace_store_exists":
                False,

            "body_count":
                0,

            "verified_count":
                0,

            "corrupted_count":
                0,

            "bodies":
                [],

            "body_content_included":
                False,
        }

    if not workspace_body_root.is_dir():
        raise BodyStoreAccessError(
            "Workspace Body Store path is not a directory."
        )

    bodies: list[dict[str, Any]] = []

    verified_count = 0
    corrupted_count = 0

    for candidate in sorted(
        workspace_body_root.iterdir(),
        key=lambda item: item.name.casefold(),
    ):
        if candidate.is_symlink():
            continue

        if not candidate.is_file():
            continue

        if candidate.suffix.casefold() != ".txt":
            continue

        body_ref = _body_ref_from_path(
            project_root=root,
            body_path=candidate,
        )

        item: dict[str, Any] = {
            "filename":
                candidate.name,

            "body_ref":
                body_ref,

            "stored_path":
                str(
                    candidate
                ),

            "verified":
                None,

            "corrupted":
                None,
        }

        if verify_each:
            try:
                verification = verify_stored_body(
                    project_root=root,
                    workspace_id=workspace,
                    body_ref=body_ref,
                )

                item.update(
                    {
                        "verified":
                            True,

                        "corrupted":
                            False,

                        "content_hash":
                            verification[
                                "content_hash"
                            ],

                        "body_length":
                            verification[
                                "body_length"
                            ],

                        "body_byte_length":
                            verification[
                                "body_byte_length"
                            ],

                        "body_word_count":
                            verification[
                                "body_word_count"
                            ],
                    }
                )

                verified_count += 1

            except (
                BodyStoreAccessError,
                BodyStoreCorruptionError,
                BodyStoreMissingError,
            ) as exc:
                item.update(
                    {
                        "verified":
                            False,

                        "corrupted":
                            True,

                        "error":
                            str(
                                exc
                            ),
                    }
                )

                corrupted_count += 1

        bodies.append(
            item
        )

    return {
        "listing_schema_version":
            "workspace_body_listing_v1",

        "manager_version":
            BODY_STORE_MANAGER_VERSION,

        "workspace_id":
            workspace,

        "workspace_body_root":
            str(
                workspace_body_root
            ),

        "workspace_store_exists":
            True,

        "body_count":
            len(
                bodies
            ),

        "verified_count":
            verified_count,

        "corrupted_count":
            corrupted_count,

        "bodies":
            bodies,

        "body_content_included":
            False,
    }

