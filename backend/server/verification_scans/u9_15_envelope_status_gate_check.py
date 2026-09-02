from copy import deepcopy

import backend.server.stores.uploaded_document_unified_content as u
import backend.server.universal_unified_content_document.uucd_engine_v1 as e

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

body = (
    "Heading A\n\n"
    "Envelope status gate test.\n"
)

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u9_15_gate.txt",
    source_type="txt",
    title="U9.15 Gate Test",
    text=body,
    headings=["Heading A"],
    metadata={
        "filename": "u9_15_gate.txt",
        "extension": ".txt",
        "file_size": len(body.encode("utf-8")),
        "extraction_method": "txt_upload_v1",
    },
    extraction_status="success",
    extraction_confidence=1.0,
    extraction_created_at="2026-09-01T18:20:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T18:20:01+00:00",
)

uduc = u.serialize_uduc(
    u.build_uduc_from_normalized_content(
        normalized_content=normalized,
        workspace_id="ws_u9_15_gate",
        document_id="upload_doc_u9_15_gate",
        original_filename="u9_15_gate.txt",
        stored_filename="stored_u9_15_gate.txt",
        stored_path="C:/persisted/ws_u9_15_gate/stored_u9_15_gate.txt",
        source_metadata={
            "origin_system": "linkcraftor_ui",
        },
    )
)

envelope = e.build_transient_uucd_from_uduc_v1(
    uduc
)

print(
    "VALID_STATUS_RESULT=",
    e.validate_universal_handoff_envelope_v1(
        envelope
    ),
)

bad = deepcopy(
    envelope
)

bad["envelope_status"] = "INVALID"

try:
    e.validate_universal_handoff_envelope_v1(
        bad
    )

    print(
        "INVALID_STATUS_REJECTED=False"
    )

except Exception as exc:
    print(
        "INVALID_STATUS_REJECTED=True"
    )

    print(
        "ERROR_TYPE=",
        type(exc).__name__,
    )

    print(
        "ERROR=",
        str(exc),
    )