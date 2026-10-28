
"""PT2C.5.5J ? Composed read-only signed entitlement resolver.

This component is not provisioned into production runtime.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from backend.server.runtime.security.semantic_memory_membership_integrity import (
    OPERATION,
    MembershipIntegrityVerifier,
)
from backend.server.runtime.security.semantic_memory_membership_revision import (
    ProvisionedMembershipRevisionAuthority,
)


WORKSPACE_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


class VerifiedMembershipUnavailable(RuntimeError):
    pass


class VerifiedWorkspaceMembershipResolver:
    def __init__(
        self,
        *,
        workspace_root,
        membership_root,
        integrity_verifier: MembershipIntegrityVerifier,
        revision_authority: ProvisionedMembershipRevisionAuthority,
    ):
        if not isinstance(
            integrity_verifier, MembershipIntegrityVerifier
        ):
            raise VerifiedMembershipUnavailable(
                "Integrity verifier required"
            )
        if not isinstance(
            revision_authority,
            ProvisionedMembershipRevisionAuthority,
        ):
            raise VerifiedMembershipUnavailable(
                "Revision authority required"
            )

        self.workspace_root = Path(workspace_root)
        self.membership_root = Path(membership_root)
        self.integrity = integrity_verifier
        self.revisions = revision_authority

    @staticmethod
    def _load(path, root):
        try:
            root = root.resolve(strict=True)
            resolved = path.resolve(strict=True)
            resolved.relative_to(root)

            # Reject symlinks in every path component below root.
            relative = path.relative_to(root)
            current = root
            for part in relative.parts:
                current = current / part
                if current.is_symlink():
                    raise ValueError("Symlink path rejected")

            if not resolved.is_file():
                raise ValueError("Record is not a file")

            data = json.loads(
                resolved.read_text(encoding="utf-8")
            )
            if type(data) is not dict:
                raise ValueError("Record is not an object")
            return data
        except Exception as exc:
            raise VerifiedMembershipUnavailable(
                "Required record unavailable"
            ) from exc

    def __call__(self, *, principal_id, workspace_id, operation):
        if (
            type(principal_id) is not str
            or not principal_id.strip()
            or principal_id != principal_id.strip()
            or type(workspace_id) is not str
            or not WORKSPACE_RE.fullmatch(workspace_id)
            or operation != OPERATION
        ):
            raise VerifiedMembershipUnavailable(
                "Invalid authorization request"
            )

        try:
            profile = self._load(
                self.workspace_root
                / workspace_id
                / "workspace_profile.json",
                self.workspace_root,
            )

            if (
                profile.get("schema_version") != "workspace_profile_v2"
                or profile.get("workspace_id") != workspace_id
                or profile.get("connection_status") != "connected"
            ):
                raise ValueError("Workspace is not connected")

            record_id = hashlib.sha256(
                json.dumps(
                    [workspace_id, principal_id],
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()

            envelope = self._load(
                self.membership_root / (record_id + ".json"),
                self.membership_root,
            )

            verified = self.integrity.verify(
                envelope=envelope,
                principal_id=principal_id,
                workspace_id=workspace_id,
            )

            self.revisions.verify(
                principal_id=principal_id,
                workspace_id=workspace_id,
                revision=verified["revision"],
            )

            return {
                "principal_id": principal_id,
                "workspace_id": workspace_id,
                "operation": OPERATION,
                "access_granted": True,
                "authorization_source":
                    "signed_membership_revision_checked_v1",
                "authorization_reference":
                    verified["authorization_reference"],
            }

        except Exception as exc:
            raise VerifiedMembershipUnavailable(
                "Trusted workspace entitlement not established"
            ) from exc
