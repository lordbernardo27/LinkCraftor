from pathlib import Path

path = Path(
    "backend/server/verification_scans/u3_13_intake_failure_rollback_verifier.py"
)

text = path.read_text(encoding="utf-8")

old = '''        workspace_cases = [
            ("BLANK_WORKSPACE", ""),
            ("INVALID_WORKSPACE", "../unsafe"),
        ]

        for label, workspace_value in workspace_cases:
            before_store = len(store_calls)
            before_rollback = len(rollback_calls)

            raised = False
            status_code = None

            try:
                await intake_module.run_upload_intake(
                    workspace_id=workspace_value,
                    file=make_upload(
                        "workspace.txt",
                        b"workspace validation",
                    ),
                    dependencies=deps,
                )
            except HTTPException as exc:
                raised = True
                status_code = exc.status_code

            check(
                f"{label}_REJECTED",
                raised,
            )

            check(
                f"{label}_STATUS_400",
                status_code == 400,
            )

            check(
                f"{label}_NO_STORAGE",
                len(store_calls) == before_store,
            )

            check(
                f"{label}_NO_ROLLBACK",
                len(rollback_calls) == before_rollback,
            )'''

new = '''        workspace_cases = [
            ("BLANK_WORKSPACE", ""),
            ("INVALID_WORKSPACE", "..."),
        ]

        for label, workspace_value in workspace_cases:
            before_store = len(store_calls)
            before_rollback = len(rollback_calls)

            raised = False
            status_code = None

            try:
                await intake_module.run_upload_intake(
                    workspace_id=workspace_value,
                    file=make_upload(
                        "workspace.txt",
                        b"workspace validation",
                    ),
                    dependencies=deps,
                )
            except HTTPException as exc:
                raised = True
                status_code = exc.status_code

            check(
                f"{label}_REJECTED",
                raised,
            )

            check(
                f"{label}_STATUS_400",
                status_code == 400,
            )

            check(
                f"{label}_NO_STORAGE",
                len(store_calls) == before_store,
            )

            check(
                f"{label}_NO_ROLLBACK",
                len(rollback_calls) == before_rollback,
            )

        # Traversal-shaped workspace input is intentionally
        # sanitized into a canonical safe workspace ID.
        traversal_result = await intake_module.run_upload_intake(
            workspace_id="../unsafe",
            file=make_upload(
                "workspace-sanitized.txt",
                b"workspace canonicalization",
            ),
            dependencies=deps,
        )

        check(
            "TRAVERSAL_WORKSPACE_SANITIZED",
            traversal_result.get("workspace_id") == "ws_unsafe",
        )

        check(
            "TRAVERSAL_WORKSPACE_INTAKE_OK",
            traversal_result.get("ok") is True,
        )

        traversal_doc = traversal_result.get("doc") or {}
        traversal_stored_name = str(
            traversal_doc.get("stored_name") or ""
        ).strip()

        traversal_path = (
            files_route._ws_dir("ws_unsafe")
            / traversal_stored_name
        )

        check(
            "TRAVERSAL_WORKSPACE_SOURCE_INSIDE_CANONICAL_DIRECTORY",
            traversal_path.is_file()
            and traversal_path.parent
            == files_route._ws_dir("ws_unsafe"),
        )'''

if old not in text:
    raise RuntimeError(
        "Expected workspace-verification block was not found."
    )

text = text.replace(old, new, 1)

path.write_text(
    text,
    encoding="utf-8",
)

print("U3.13_WORKSPACE_VERIFIER_ALIGNMENT: APPLIED")