from __future__ import annotations

from pathlib import Path

from backend.server.stores.source_lifecycle_control import (
    disconnect_source,
    editor_delete_source,
    explicit_purge_source,
    explain_source_lifecycle_control_v1,
    register_or_update_source,
    update_source_version,
)


def fail(msg: str):
    raise AssertionError(msg)


def main():
    workspace_id = "ws_verification_6f"
    source_type = "uploaded_document"
    source_id = "DOC_SOURCE_6F"

    registered = register_or_update_source(
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
        source_name="Verification Upload Source",
        document_ids=["DOC_6F_001"],
    )

    if not registered.get("ok"):
        fail("register_or_update_source failed")

    disconnected = disconnect_source(
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
        reason="verification disconnect",
    )

    if disconnected["source"].get("status") != "disconnected":
        fail("disconnect_source did not mark source disconnected")

    if disconnected["event"]["metadata"].get("delete_uucd") is not False:
        fail("disconnect_source must not delete UUCD")

    deleted = editor_delete_source(
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
        document_ids=["DOC_6F_001"],
        reason="verification editor delete",
    )

    if deleted["source"].get("status") != "deleted":
        fail("editor_delete_source did not mark source deleted")

    if deleted["event"]["metadata"].get("physical_delete") is not False:
        fail("editor delete must not physically delete files")

    updated = update_source_version(
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
        document_ids=["DOC_6F_001"],
        content_hash="abc123",
        reason="verification update",
    )

    if not updated.get("version"):
        fail("update_source_version did not create version record")

    purged = explicit_purge_source(
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
        reason="verification explicit purge",
    )

    purge_path = Path(purged.get("purge_ledger_path", ""))
    if not purge_path.exists():
        fail("purge ledger was not written")

    if purged["purge_event"].get("removes_uucd") is not True:
        fail("explicit purge must mark UUCD removal")

    explanation = explain_source_lifecycle_control_v1()

    print("VERIFICATION 6F SOURCE LIFECYCLE CONTROL PASSED")
    print("Component:", explanation.get("component"))
    print("Lifecycle path:", purged.get("lifecycle_control_path"))
    print("Purge ledger:", purged.get("purge_ledger_path"))
    print("Next stage:", explanation.get("next_stage"))


if __name__ == "__main__":
    main()
