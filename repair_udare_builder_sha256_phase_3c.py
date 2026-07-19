from pathlib import Path
import re


path = Path(
    "backend/server/stores/udare_article_document_builder.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)


pattern = re.compile(
    r"""
    ^def[ \t]+_sha256_text
    \(
    .*?
    (?=
        ^def[ \t]+_normalized_text
        \(
    )
    """,
    re.MULTILINE | re.DOTALL | re.VERBOSE,
)


replacement = '''def _sha256_text(
    value: str,
) -> str:
    normalized = str(
        value or ""
    )

    return hashlib.sha256(
        normalized.encode(
            "utf-8"
        )
    ).hexdigest()


'''


updated, count = pattern.subn(
    replacement,
    text,
    count=1,
)


if count != 1:
    raise RuntimeError(
        "Expected _sha256_text function block "
        "was not found exactly once."
    )


path.write_text(
    updated,
    encoding="utf-8",
)


print(
    "UDARE BUILDER SHA256 REPAIR: PASS"
)
