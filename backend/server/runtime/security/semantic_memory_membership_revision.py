
"""PT2C.5.5I ? Independent membership revision verification."""

from __future__ import annotations

from collections.abc import Callable, Mapping


class MembershipRevisionDenied(RuntimeError):
    pass


class ProvisionedMembershipRevisionAuthority:
    def __init__(self, *, revision_resolver: Callable):
        if not callable(revision_resolver):
            raise MembershipRevisionDenied(
                "Trusted revision resolver required"
            )
        self._resolver = revision_resolver

    def verify(self, *, principal_id, workspace_id, revision):
        try:
            current = self._resolver(
                principal_id=principal_id,
                workspace_id=workspace_id,
            )
        except Exception as exc:
            raise MembershipRevisionDenied(
                "Revision authority unavailable"
            ) from exc

        if (
            not isinstance(current, Mapping)
            or set(current) != {
                "principal_id",
                "workspace_id",
                "revision",
                "status",
            }
            or type(current["principal_id"]) is not str
            or type(current["workspace_id"]) is not str
            or current["principal_id"] != principal_id
            or current["workspace_id"] != workspace_id
            or type(current["revision"]) is not int
            or type(revision) is not int
            or current["revision"] != revision
            or current["status"] != "ACTIVE"
        ):
            raise MembershipRevisionDenied(
                "Membership revoked, stale or mismatched"
            )

        return True
