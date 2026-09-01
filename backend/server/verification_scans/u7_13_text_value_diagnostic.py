from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)

from backend.server.stores.upload_document_normalizer import (
    normalize_uploaded_document_v1,
)

x = UploadExtractionResult(
    source_path="C:/immutable/source.txt",
    source_type="txt",
    title="  Cafe\u0301\t Title  ",
    text="\n\n A   B \r\n\r\n\r\n C\tD \u0000 \n\n",
    headings=[
        "  First\t Heading  ",
        "",
        "  First\t Heading  ",
        "Multi\r\nLine",
    ],
    metadata={
        "custom": "preserve-me",
    },
    extraction_status="success",
    extraction_confidence=0.95,
    created_at="2026-08-31T00:00:00+00:00",
)

r = normalize_uploaded_document_v1(x)

print("NORMALIZED_TEXT_REPR=", repr(r.text))
print("NORMALIZED_TEXT_LENGTH=", len(r.text))
print("EXPECTED_TEXT_REPR=", repr("A B\n\nC D"))
print("EXPECTED_TEXT_LENGTH=", len("A B\n\nC D"))
print("TEXT_EQUALS_EXPECTED=", r.text == "A B\n\nC D")