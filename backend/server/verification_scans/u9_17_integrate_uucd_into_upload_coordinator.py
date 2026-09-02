from pathlib import Path

path = Path(
    "backend/server/pipelines/upload_document/"
    "coordinator.py"
)

raw = path.read_bytes()

had_bom = raw.startswith(
    b"\xef\xbb\xbf"
)

source = raw.decode(
    "utf-8-sig"
)


# ------------------------------------------------------------
# 1. Add Current Canonical UUCD builder import
# ------------------------------------------------------------

import_block = '''from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    build_transient_uucd_from_uduc_v1,
)
'''

import_anchor = '''from backend.server.stores.uploaded_document_unified_content import (
    build_and_write_uduc_from_normalized_content,
)
'''

if import_block not in source:
    if import_anchor not in source:
        raise RuntimeError(
            "Could not locate UDUC import anchor."
        )

    source = source.replace(
        import_anchor,
        import_anchor
        + "\n"
        + import_block,
        1,
    )


# ------------------------------------------------------------
# 2. Insert U9 immediately after canonical UDUC success gate
# ------------------------------------------------------------

integration_marker = (
    "uucd_envelope = "
    "build_transient_uucd_from_uduc_v1("
)

if integration_marker not in source:

    anchor = '''    if not isinstance(uduc, dict):
        raise RuntimeError(
            "UDUC builder/writer result does not contain "
            "serialized UDUC."
        )

'''

    integration = '''    if not isinstance(uduc, dict):
        raise RuntimeError(
            "UDUC builder/writer result does not contain "
            "serialized UDUC."
        )

    # ------------------------------------------------------------
    # Canonical U9 UDUC -> Current Canonical UUCD convergence.
    #
    # This produces only the transient Option-3 Universal Handoff
    # Envelope. It does not write the Body Store, persist the UUCD,
    # execute runtime, semantic intelligence, scorer, or highlights.
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

    if anchor not in source:
        raise RuntimeError(
            "Could not locate canonical UDUC success gate."
        )

    source = source.replace(
        anchor,
        integration,
        1,
    )


# ------------------------------------------------------------
# 3. Add U9 to overall success contract
# ------------------------------------------------------------

old_overall = '''    overall_ok = (
        pipeline_2.get("ok") is True
        and uduc_result.get("ok") is True
        and pipeline_1.get("ok") is True
        and pipeline_3.get("ok") is True
    )
'''

new_overall = '''    overall_ok = (
        pipeline_2.get("ok") is True
        and uduc_result.get("ok") is True
        and uucd_envelope.get(
            "envelope_status"
        ) == "READY_FOR_BODY_STORE"
        and pipeline_1.get("ok") is True
        and pipeline_3.get("ok") is True
    )
'''

if old_overall in source:
    source = source.replace(
        old_overall,
        new_overall,
        1,
    )
elif new_overall not in source:
    raise RuntimeError(
        "Could not locate overall_ok contract."
    )


# ------------------------------------------------------------
# 4. Add U9 to execution order
# ------------------------------------------------------------

old_order = '''            "uploaded_document_to_uduc_pipeline",
            "uploaded_document_to_highlight_pipeline",
'''

new_order = '''            "uploaded_document_to_uduc_pipeline",
            "uploaded_document_to_current_canonical_uucd",
            "uploaded_document_to_highlight_pipeline",
'''

if old_order in source:
    source = source.replace(
        old_order,
        new_order,
        1,
    )
elif new_order not in source:
    raise RuntimeError(
        "Could not locate execution_order insertion point."
    )


# ------------------------------------------------------------
# 5. Expose U9 result in orchestration metadata
# ------------------------------------------------------------

old_pipelines = '''            "uploaded_document_to_uduc_pipeline": pipeline_2,
            "uploaded_document_to_highlight_pipeline": pipeline_1,
'''

new_pipelines = '''            "uploaded_document_to_uduc_pipeline": pipeline_2,
            "uploaded_document_to_current_canonical_uucd": {
                "ok": True,
                "status": "READY_FOR_BODY_STORE",
                "envelope": uucd_envelope,
            },
            "uploaded_document_to_highlight_pipeline": pipeline_1,
'''

if old_pipelines in source:
    source = source.replace(
        old_pipelines,
        new_pipelines,
        1,
    )
elif new_pipelines not in source:
    raise RuntimeError(
        "Could not locate pipelines result insertion point."
    )


# ------------------------------------------------------------
# Write production file
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