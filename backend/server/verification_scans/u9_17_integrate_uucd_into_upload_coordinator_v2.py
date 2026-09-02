from pathlib import Path

path = Path(
    "backend/server/pipelines/upload_document/"
    "coordinator.py"
)

raw = path.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
source = raw.decode("utf-8-sig")


# ------------------------------------------------------------
# 1. Add Current Canonical UUCD builder import
# ------------------------------------------------------------

import_marker = (
    "from backend.server.universal_unified_content_document."
    "uucd_engine_v1 import"
)

if import_marker not in source:

    anchor = (
        "from backend.server.stores.uploaded_document_unified_content "
        "import (\n"
        "    build_and_write_uduc_from_normalized_content,\n"
        ")\n"
    )

    addition = (
        anchor
        + "from backend.server.universal_unified_content_document."
        "uucd_engine_v1 import (\n"
        "    build_transient_uucd_from_uduc_v1,\n"
        ")\n"
    )

    if anchor not in source:
        raise RuntimeError(
            "Could not locate actual UDUC import block."
        )

    source = source.replace(
        anchor,
        addition,
        1,
    )


# ------------------------------------------------------------
# 2. Insert U9 after canonical serialized UDUC success gate
# ------------------------------------------------------------

integration_marker = (
    "uucd_envelope = build_transient_uucd_from_uduc_v1("
)

if integration_marker not in source:

    gate_marker = (
        '    uduc = uduc_result.get("uduc")\n'
    )

    gate_start = source.find(
        gate_marker
    )

    if gate_start == -1:
        raise RuntimeError(
            "Could not locate serialized UDUC assignment."
        )

    highlight_marker = (
        "    # Highlight pipeline receives dedicated extracted text."
    )

    highlight_start = source.find(
        highlight_marker,
        gate_start,
    )

    if highlight_start == -1:
        raise RuntimeError(
            "Could not locate Highlight branch boundary."
        )

    existing_segment = source[
        gate_start:highlight_start
    ]

    if (
        'if not isinstance(uduc, dict):'
        not in existing_segment
    ):
        raise RuntimeError(
            "Could not verify canonical UDUC success gate."
        )

    integration = '''    # ------------------------------------------------------------
    # Canonical U9 UDUC -> Current Canonical UUCD convergence.
    #
    # Produces only the transient Current Canonical Option-3
    # Universal Handoff Envelope.
    #
    # Does not:
    # - write Universal Article Body Store
    # - persist finalized UUCD
    # - execute runtime
    # - execute Semantic Intelligence
    # - execute scorer
    # - alter Highlight or Registry -> ATS branches
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

    source = (
        source[:highlight_start]
        + integration
        + source[highlight_start:]
    )


# ------------------------------------------------------------
# 3. Add U9 to overall success contract
# ------------------------------------------------------------

if (
    'and uucd_envelope.get('
    not in source
):

    old = '''    overall_ok = (
        pipeline_2.get("ok") is True
        and uduc_result.get("ok") is True
        and pipeline_1.get("ok") is True
        and pipeline_3.get("ok") is True
    )
'''

    new = '''    overall_ok = (
        pipeline_2.get("ok") is True
        and uduc_result.get("ok") is True
        and uucd_envelope.get(
            "envelope_status"
        ) == "READY_FOR_BODY_STORE"
        and pipeline_1.get("ok") is True
        and pipeline_3.get("ok") is True
    )
'''

    if old not in source:
        raise RuntimeError(
            "Could not locate overall_ok block."
        )

    source = source.replace(
        old,
        new,
        1,
    )


# ------------------------------------------------------------
# 4. Add U9 to execution_order
# ------------------------------------------------------------

execution_name = (
    '"uploaded_document_to_current_canonical_uucd"'
)

if execution_name not in source:

    old = '''            "uploaded_document_to_uduc_pipeline",
            "uploaded_document_to_highlight_pipeline",
'''

    new = '''            "uploaded_document_to_uduc_pipeline",
            "uploaded_document_to_current_canonical_uucd",
            "uploaded_document_to_highlight_pipeline",
'''

    if old not in source:
        raise RuntimeError(
            "Could not locate execution_order block."
        )

    source = source.replace(
        old,
        new,
        1,
    )


# ------------------------------------------------------------
# 5. Expose U9 result alongside existing pipeline results
# ------------------------------------------------------------

result_key = (
    '"uploaded_document_to_current_canonical_uucd": {'
)

if result_key not in source:

    old = '''            "uploaded_document_to_uduc_pipeline": pipeline_2,
            "uploaded_document_to_highlight_pipeline": pipeline_1,
'''

    new = '''            "uploaded_document_to_uduc_pipeline": pipeline_2,
            "uploaded_document_to_current_canonical_uucd": {
                "ok": True,
                "status": "READY_FOR_BODY_STORE",
                "envelope": uucd_envelope,
            },
            "uploaded_document_to_highlight_pipeline": pipeline_1,
'''

    if old not in source:
        raise RuntimeError(
            "Could not locate pipeline result block."
        )

    source = source.replace(
        old,
        new,
        1,
    )


# ------------------------------------------------------------
# Write
# ------------------------------------------------------------

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