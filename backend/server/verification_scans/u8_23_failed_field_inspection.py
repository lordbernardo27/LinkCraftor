from pprint import pprint

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

from backend.server.stores.uploaded_document_unified_content import (
    build_uduc_from_normalized_content,
    serialize_uduc,
)


normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u8_23.txt",
    source_type="txt",
    title="Canonical Title",
    text=(
        "Heading One\n\n"
        "Paragraph alpha beta.\n\n"
        "Heading One\n\n"
        "Paragraph gamma.\n\n"
        "Trailing paragraph."
    ),
    headings=[
        "Heading One",
        "Heading One",
        "Missing Heading",
    ],
    metadata={
        "filename": "u8_23.txt",
        "extension": ".txt",
        "file_size": 0,
        "extraction_method": "txt_upload_v1",
        "custom": {
            "alpha": 1,
            "beta": "two",
        },
    },
    extraction_status="success",
    extraction_confidence=0.95,
    extraction_created_at="2026-09-01T01:15:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T01:15:01+00:00",
)

source_metadata = {
    "source_system": "u8_23_test",
    "external_flag": True,
}

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_23",
    document_id="doc_u8_23",
    original_filename="u8_23.txt",
    stored_filename="stored_u8_23.txt",
    stored_path="C:/persisted/ws_u8_23/stored_u8_23.txt",
    source_metadata=source_metadata,
)

data = serialize_uduc(uduc)

print("=== U8.23 FAILED FIELD INSPECTION ===")

print()
print("SOURCE_TYPE=")
pprint(data.get("source_type"))

print()
print("SOURCE_FORMAT=")
pprint(data.get("source_format"))

print()
print("METADATA=")
pprint(data.get("metadata"))

print()
print("STRUCTURE_SUMMARY=")
pprint(
    data.get(
        "structure",
        {},
    ).get(
        "summary"
    )
)

print()
print("STRUCTURE_KEYS=")
pprint(
    list(
        data.get(
            "structure",
            {}
        ).keys()
    )
)

print()
print("PARAGRAPH_COUNT_ACTUAL=")
print(
    len(
        data.get(
            "structure",
            {}
        ).get(
            "paragraphs",
            []
        )
    )
)

print()
print("HEADING_COUNT_ACTUAL=")
print(
    len(
        data.get(
            "structure",
            {}
        ).get(
            "heading_map",
            []
        )
    )
)

print()
print("CONTENT_CHARACTER_COUNT_ACTUAL=")
print(
    len(
        data.get(
            "content_body",
            ""
        )
    )
)

print()
print("CONTENT_WORD_COUNT_ACTUAL=")
print(
    len(
        data.get(
            "content_body",
            ""
        ).split()
    )
)