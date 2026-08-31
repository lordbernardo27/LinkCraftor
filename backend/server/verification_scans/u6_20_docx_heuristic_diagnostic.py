from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED

import backend.server.stores.upload_document_extractor as m


with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "heuristic.docx"

    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>'
        '<w:p><w:r><w:t>THIS LOOKS LIKE A HEADING</w:t></w:r></w:p>'
        '<w:p><w:r><w:t>Normal body paragraph.</w:t></w:r></w:p>'
        '</w:body>'
        '</w:document>'
    )

    with ZipFile(
        path,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "word/document.xml",
            xml,
        )

    result = m.extract_docx_upload_v1(path)

    print("STATUS=", repr(result.extraction_status))
    print("TITLE=", repr(result.title))
    print("HEADINGS=", repr(result.headings))
    print(
        "HEADING_METHOD=",
        repr(result.metadata.get("heading_method")),
    )
    print(
        "CONFIDENCE=",
        repr(result.extraction_confidence),
    )
    print("TEXT=", repr(result.text))