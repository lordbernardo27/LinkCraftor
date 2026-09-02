from pathlib import Path

path = Path(
    "backend/server/pipelines/upload_document/"
    "coordinator.py"
)

raw = path.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")

source = raw.decode("utf-8-sig")

# Normalize only inside the patching process.
# Production output will be written consistently afterward.
source = source.replace("\r\n", "\n")


# ============================================================
# 1. IMPORT
# ============================================================

uucd_import = '''from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    build_transient_uucd_from_uduc_v1,
)
'''

if (
    "build_transient_uucd_from_uduc_v1"
    not in source
):
    lines = source.splitlines()

    insert_after = None

    for index, line in enumerate(lines):
        if (
            "build_and_write_uduc_from_normalized_content,"
            in line
        ):
            # Expected next line closes this import block.
            if (
                index + 1 < len(lines)
                and lines[index + 1].strip() == ")"
            ):
                insert_after = index + 1
                break

    if insert_after is None:
        raise RuntimeError(
            "Could not locate UDUC import structurally."
        )

    import_lines = uucd_import.rstrip(
        "\n"
    ).splitlines()

    lines[
        insert_after + 1:
        insert_after + 1
    ] = import_lines

    source = "\n".join(lines) + "\n"


# ============================================================
# 2. U9 ENVELOPE BUILD
# ============================================================

if (
    "uucd_envelope = "
    "build_transient_uucd_from_uduc_v1("
    not in source
):
    lines = source.splitlines()

    uduc_assignment = None
    highlight_boundary = None

    for index, line in enumerate(lines):
        if (
            'uduc = uduc_result.get("uduc")'
            in line
        ):
            uduc_assignment = index

        if (
            uduc_assignment is not None
            and "# Highlight pipeline receives dedicated extracted text."
            in line
        ):
            highlight_boundary = index
            break

    if uduc_assignment is None:
        raise RuntimeError(
            "Could not locate serialized UDUC assignment."
        )

    if highlight_boundary is None:
        raise RuntimeError(
            "Could not locate Highlight branch boundary."
        )

    segment = "\n".join(
        lines[
            uduc_assignment:
            highlight_boundary
        ]
    )

    if "if not isinstance(uduc, dict):" not in segment:
        raise RuntimeError(
            "Canonical UDUC validation gate not found."
        )

    integration = '''    # ------------------------------------------------------------
    # Canonical U9 UDUC -> Current Canonical UUCD convergence.
    #
    # Produces only the transient Current Canonical Option-3
    # Universal Handoff Envelope.
    #
    # No Body Store write.
    # No finalized UUCD persistence.
    # No runtime.
    # No Semantic Intelligence.
    # No scorer.
    # ------------------------------------------------------------

    uucd_envelope = build_transient_uucd_from_uduc_v1(
        uduc
    )

    if not isinstance(
        uucd_envelope,
        dict,
    ):
        raise RuntimeError(
            "Uploaded Document U9 UUCD builder returned "
            "a non-dictionary envelope."
        )

    if (
        uucd_envelope.get(
            "envelope_status"
        )
        != "READY_FOR_BODY_STORE"
    ):
        raise RuntimeError(
            "Uploaded Document U9 UUCD envelope is not "
            "READY_FOR_BODY_STORE."
        )

'''

    integration_lines = integration.rstrip(
        "\n"
    ).splitlines()

    # Insert immediately before Highlight boundary comment.
    lines[
        highlight_boundary:
        highlight_boundary
    ] = integration_lines

    source = "\n".join(lines) + "\n"


# ============================================================
# 3. OVERALL SUCCESS
# ============================================================

if "and uucd_envelope.get(" not in source:
    lines = source.splitlines()

    insert_at = None

    for index, line in enumerate(lines):
        if (
            'and uduc_result.get("ok") is True'
            in line
        ):
            insert_at = index + 1
            break

    if insert_at is None:
        raise RuntimeError(
            "Could not locate overall_ok UDUC condition."
        )

    condition_lines = [
        "        and uucd_envelope.get(",
        '            "envelope_status"',
        '        ) == "READY_FOR_BODY_STORE"',
    ]

    lines[
        insert_at:
        insert_at
    ] = condition_lines

    source = "\n".join(lines) + "\n"


# ============================================================
# 4. EXECUTION ORDER
# ============================================================

execution_name = (
    '"uploaded_document_to_current_canonical_uucd"'
)

if execution_name not in source:
    lines = source.splitlines()

    insert_at = None

    for index, line in enumerate(lines):
        if (
            '"uploaded_document_to_uduc_pipeline",'
            in line
        ):
            # Only use the occurrence inside execution_order.
            nearby = "\n".join(
                lines[
                    max(0, index - 5):
                    index + 2
                ]
            )

            if '"execution_order"' in nearby:
                insert_at = index + 1
                break

    if insert_at is None:
        raise RuntimeError(
            "Could not locate execution_order insertion point."
        )

    lines.insert(
        insert_at,
        '            "uploaded_document_to_current_canonical_uucd",',
    )

    source = "\n".join(lines) + "\n"


# ============================================================
# 5. PIPELINE RESULT EXPOSURE
# ============================================================

result_marker = (
    '"uploaded_document_to_current_canonical_uucd": {'
)

if result_marker not in source:
    lines = source.splitlines()

    insert_at = None

    for index, line in enumerate(lines):
        if (
            '"uploaded_document_to_uduc_pipeline": pipeline_2,'
            in line
        ):
            # Select the successful final return block,
            # not Pipeline-2 failure handling.
            nearby = "\n".join(
                lines[
                    max(0, index - 8):
                    index + 3
                ]
            )

            if '"pipelines": {' in nearby:
                insert_at = index + 1

    if insert_at is None:
        raise RuntimeError(
            "Could not locate final pipelines result block."
        )

    result_lines = [
        '            "uploaded_document_to_current_canonical_uucd": {',
        '                "ok": True,',
        '                "status": "READY_FOR_BODY_STORE",',
        '                "envelope": uucd_envelope,',
        "            },",
    ]

    lines[
        insert_at:
        insert_at
    ] = result_lines

    source = "\n".join(lines) + "\n"


# ============================================================
# WRITE
# ============================================================

encoding = (
    "utf-8-sig"
    if had_bom
    else "utf-8"
)

path.write_text(
    source,
    encoding=encoding,
    newline="\n",
)

print(
    "U9.17_PATCH_STATUS="
    "CURRENT_CANONICAL_UUCD_INTEGRATED"
)

print(
    "TARGET="
    + str(path)
)