"""Read-only Semantic Memory workspace membership provider.

PT2C.5.5F: no membership provisioning, authentication, or live
certification grant is enabled by this module.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


OPERATION = "SEMANTIC_MEMORY_CERTIFICATION_CONTEXT_READ"
SOURCE = "security_workspace_membership_store_v1"
WORKSPACE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


class WorkspaceMembershipUnavailable(RuntimeError):
    """Canonical workspace or security membership cannot be verified."""


class ReadOnlyWorkspaceMembershipResolver:
    def __init__(
        self,
        *,
        workspace_root: Path,
        membership_root: Path,
    ):
        self.workspace_root = Path(workspace_root)
        self.membership_root = Path(membership_root)

    @staticmethod
    def _read_json(path: Path, root: Path):
        try:
            canonical_root = root.resolve(strict=True)
            if path.is_symlink():
                raise WorkspaceMembershipUnavailable(
                    "Symbolic-link records are not accepted"
                )
            resolved = path.resolve(strict=True)
            resolved.relative_to(canonical_root)
            if not resolved.is_file():
                raise ValueError("Not a regular file")
            data = json.loads(resolved.read_text(encoding="utf-8"))
            if type(data) is not dict:
                raise ValueError("Invalid record structure")
            return data
        except Exception as exc:
            raise WorkspaceMembershipUnavailable(
                "Required authoritative record unavailable"
            ) from exc

    def __call__(
        self,
        *,
        principal_id: str,
        workspace_id: str,
        operation: str,
    ):
        if (
            type(principal_id) is not str
            or not principal_id.strip()
            or principal_id != principal_id.strip()
            or type(workspace_id) is not str
            or not WORKSPACE_ID_RE.fullmatch(workspace_id)
            or type(operation) is not str
            or operation != OPERATION
        ):
            raise WorkspaceMembershipUnavailable(
                "Invalid principal, workspace, or operation"
            )

        profile_path = (
            self.workspace_root
            / workspace_id
            / "workspace_profile.json"
        )

        profile = self._read_json(
            profile_path, self.workspace_root
        )

        if (
            profile.get("schema_version") != "workspace_profile_v2"
            or profile.get("workspace_id") != workspace_id
            or profile.get("connection_status") != "connected"
        ):
            raise WorkspaceMembershipUnavailable(
                "Canonical workspace not verified"
            )

        record_id = hashlib.sha256(
            json.dumps(
                [workspace_id, principal_id],
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        record = self._read_json(
            self.membership_root / (record_id + ".json"),
            self.membership_root,
        )

        required = {
            "schema_version",
            "principal_id",
            "workspace_id",
            "status",
            "operations",
            "authorization_reference",
        }

        if set(record) != required:
            raise WorkspaceMembershipUnavailable(
                "Invalid membership record schema"
            )

        if (
            record["schema_version"] != "workspace_membership_v1"
            or type(record["principal_id"]) is not str
            or record["principal_id"] != principal_id
            or type(record["workspace_id"]) is not str
            or record["workspace_id"] != workspace_id
            or record["status"] != "ACTIVE"
            or type(record["operations"]) is not list
            or any(
                type(item) is not str
                for item in record["operations"]
            )
            or operation not in record["operations"]
            or type(record["authorization_reference"]) is not str
            or not record["authorization_reference"].strip()
            or record["authorization_reference"]
                != record["authorization_reference"].strip()
        ):
            raise WorkspaceMembershipUnavailable(
                "Membership inactive, mismatched, or unauthorized"
            )

        return {
            "principal_id": principal_id,
            "workspace_id": workspace_id,
            "operation": operation,
            "access_granted": True,
            "authorization_source": SOURCE,
            "authorization_reference": record[
                "authorization_reference"
            ],
        }
