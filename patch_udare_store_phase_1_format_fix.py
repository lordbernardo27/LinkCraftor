from pathlib import Path
import re


store_path = Path(
    "backend/server/stores/udare_store.py"
)

verification_path = Path(
    "verify_udare_store_phase_1.py"
)


# =====================================================================
# PATCH UDARE STORE MODULE
# =====================================================================

store_text = store_path.read_text(
    encoding="utf-8-sig"
)


if (
    "from html.parser import HTMLParser"
    not in store_text
):
    store_text = store_text.replace(
        "from html import unescape\n",
        (
            "from html import unescape\n"
            "from html.parser import HTMLParser\n"
        ),
        1,
    )


constant_pattern = re.compile(
    r"""
    REQUIRED_ARTICLE_DOCUMENT_MARKERS
    \s*=\s*
    \(
    .*?
    \)
    \s*
    \n
    \s*
    FORBIDDEN_OPERATIONAL_METADATA_KEYS
    """,
    re.DOTALL | re.VERBOSE,
)

constant_replacement = '''
REQUIRED_ARTICLE_DOCUMENT_MARKERS = (
    "<!doctype html",
    "<html",
    "<head",
    "<body",
)


FORBIDDEN_OPERATIONAL_METADATA_KEYS
'''.lstrip()


store_text, constant_count = (
    constant_pattern.subn(
        lambda match:
            constant_replacement,
        store_text,
        count=1,
    )
)

if constant_count != 1:
    raise RuntimeError(
        "Could not replace "
        "REQUIRED_ARTICLE_DOCUMENT_MARKERS."
    )


function_pattern = re.compile(
    r"""
    def\s+_extract_reader_body_v1
    \(
    .*?
    \n
    def\s+_default_article_filename_v1
    \(
    """,
    re.DOTALL | re.VERBOSE,
)


function_replacement = r'''
class _UdareArticleDocumentParserV1(
    HTMLParser
):
    """
    Structural parser for the permanent UDARE HTML document.

    Phase 1 validates the document as a complete readable HTML
    document. It does not require visual-review labels, CSS class
    names or an invented wrapper around the reconstructed article.
    """

    PREFERRED_BODY_CLASSES = {
        "article-body",
        "article-content",
        "article__body",
        "article__content",
        "content-body",
        "entry-content",
        "main-content",
        "post-content",
        "story-body",
    }

    def __init__(self) -> None:
        super().__init__(
            convert_charrefs=True
        )

        self.has_doctype = False
        self.has_html = False
        self.has_head = False
        self.has_body = False
        self.has_utf8_charset = False

        self.preferred_container = ""

        self._body_depth = 0
        self._skip_depth = 0

        self.visible_text_parts: List[str] = []

    def handle_decl(
        self,
        declaration: str,
    ) -> None:
        normalized = str(
            declaration or ""
        ).strip().casefold()

        if normalized.startswith(
            "doctype html"
        ):
            self.has_doctype = True

    def handle_starttag(
        self,
        tag: str,
        attrs: List[
            tuple[str, str | None]
        ],
    ) -> None:
        normalized_tag = str(
            tag or ""
        ).strip().casefold()

        attributes = {
            str(
                key or ""
            ).strip().casefold():
                str(
                    value or ""
                ).strip()

            for key, value
            in attrs
        }

        if normalized_tag == "html":
            self.has_html = True

        elif normalized_tag == "head":
            self.has_head = True

        elif normalized_tag == "body":
            self.has_body = True
            self._body_depth += 1

        elif normalized_tag == "meta":
            charset = attributes.get(
                "charset",
                "",
            ).casefold()

            content = attributes.get(
                "content",
                "",
            ).casefold()

            if (
                "utf-8" in charset
                or "utf8" in charset
                or "charset=utf-8" in content
                or "charset=utf8" in content
            ):
                self.has_utf8_charset = True

        if normalized_tag in {
            "script",
            "style",
            "template",
            "noscript",
            "svg",
        }:
            self._skip_depth += 1

        if not self.preferred_container:
            if normalized_tag == "article":
                self.preferred_container = (
                    "article"
                )

            elif normalized_tag == "main":
                self.preferred_container = (
                    "main"
                )

            else:
                class_tokens = {
                    token.casefold()

                    for token
                    in attributes.get(
                        "class",
                        "",
                    ).split()

                    if token.strip()
                }

                matching_classes = (
                    class_tokens
                    & self.PREFERRED_BODY_CLASSES
                )

                if matching_classes:
                    self.preferred_container = (
                        "class:"
                        + sorted(
                            matching_classes
                        )[0]
                    )

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        normalized_tag = str(
            tag or ""
        ).strip().casefold()

        if (
            normalized_tag
            in {
                "script",
                "style",
                "template",
                "noscript",
                "svg",
            }
            and self._skip_depth > 0
        ):
            self._skip_depth -= 1

        if (
            normalized_tag == "body"
            and self._body_depth > 0
        ):
            self._body_depth -= 1

    def handle_data(
        self,
        data: str,
    ) -> None:
        if (
            self._body_depth <= 0
            or self._skip_depth > 0
        ):
            return

        normalized = re.sub(
            r"\s+",
            " ",
            str(
                data or ""
            ),
        ).strip()

        if normalized:
            self.visible_text_parts.append(
                normalized
            )


def _extract_reader_body_v1(
    document_text: str,
) -> Dict[str, Any]:
    parser = (
        _UdareArticleDocumentParserV1()
    )

    try:
        parser.feed(
            document_text
        )

        parser.close()

    except Exception as exc:
        return {
            "parse_ok":
                False,

            "parse_error":
                str(
                    exc
                ),

            "has_doctype":
                False,

            "has_html":
                False,

            "has_head":
                False,

            "has_body":
                False,

            "has_utf8_charset":
                False,

            "body_container_found":
                False,

            "body_container":
                "",

            "visible_text":
                "",

            "visible_text_sha256":
                _sha256_text_v1(
                    ""
                ),

            "word_count":
                0,

            "character_count":
                0,
        }

    visible_text = " ".join(
        parser.visible_text_parts
    ).strip()

    body_container = (
        parser.preferred_container
        or (
            "body"
            if parser.has_body
            else ""
        )
    )

    return {
        "parse_ok":
            True,

        "parse_error":
            "",

        "has_doctype":
            parser.has_doctype,

        "has_html":
            parser.has_html,

        "has_head":
            parser.has_head,

        "has_body":
            parser.has_body,

        "has_utf8_charset":
            parser.has_utf8_charset,

        "body_container_found":
            bool(
                body_container
            ),

        "body_container":
            body_container,

        "visible_text":
            visible_text,

        "visible_text_sha256":
            _sha256_text_v1(
                visible_text
            ),

        "word_count":
            len(
                re.findall(
                    r"\S+",
                    visible_text,
                )
            ),

        "character_count":
            len(
                visible_text
            ),
    }


def validate_udare_article_document_v1(
    article_document: str | bytes,
) -> Dict[str, Any]:
    document_text, document_bytes = (
        _decode_article_document_v1(
            article_document
        )
    )

    document_structure = (
        _extract_reader_body_v1(
            document_text
        )
    )

    errors: List[str] = []

    if not document_text.strip():
        errors.append(
            "article_document_empty"
        )

    if not document_structure[
        "parse_ok"
    ]:
        errors.append(
            "html_parse_failed:"
            + document_structure[
                "parse_error"
            ]
        )

    if not document_structure[
        "has_doctype"
    ]:
        errors.append(
            "doctype_html_missing"
        )

    if not document_structure[
        "has_html"
    ]:
        errors.append(
            "html_element_missing"
        )

    if not document_structure[
        "has_head"
    ]:
        errors.append(
            "head_element_missing"
        )

    if not document_structure[
        "has_body"
    ]:
        errors.append(
            "body_element_missing"
        )

    if not document_structure[
        "has_utf8_charset"
    ]:
        errors.append(
            "utf8_charset_missing"
        )

    if not document_structure[
        "body_container_found"
    ]:
        errors.append(
            "readable_body_container_missing"
        )

    if not document_structure[
        "visible_text"
    ]:
        errors.append(
            "article_document_visible_text_empty"
        )

    missing_markers: List[str] = []

    if not document_structure[
        "has_doctype"
    ]:
        missing_markers.append(
            "<!doctype html"
        )

    if not document_structure[
        "has_html"
    ]:
        missing_markers.append(
            "<html"
        )

    if not document_structure[
        "has_head"
    ]:
        missing_markers.append(
            "<head"
        )

    if not document_structure[
        "has_body"
    ]:
        missing_markers.append(
            "<body"
        )

    return {
        "ok":
            not errors,

        "format":
            ARTICLE_DOCUMENT_FORMAT,

        "errors":
            errors,

        "missing_markers":
            missing_markers,

        "document_sha256":
            _sha256_bytes_v1(
                document_bytes
            ),

        "document_byte_length":
            len(
                document_bytes
            ),

        "body_container_found":
            document_structure[
                "body_container_found"
            ],

        "body_container":
            document_structure[
                "body_container"
            ],

        "has_doctype":
            document_structure[
                "has_doctype"
            ],

        "has_html":
            document_structure[
                "has_html"
            ],

        "has_head":
            document_structure[
                "has_head"
            ],

        "has_body":
            document_structure[
                "has_body"
            ],

        "has_utf8_charset":
            document_structure[
                "has_utf8_charset"
            ],

        "reader_body_text_sha256":
            document_structure[
                "visible_text_sha256"
            ],

        "reader_body_word_count":
            document_structure[
                "word_count"
            ],

        "reader_body_character_count":
            document_structure[
                "character_count"
            ],
    }


def _default_article_filename_v1(
'''.lstrip()


store_text, function_count = (
    function_pattern.subn(
        lambda match:
            function_replacement,
        store_text,
        count=1,
    )
)

if function_count != 1:
    raise RuntimeError(
        "Could not replace the UDARE "
        "article-document validator."
    )


store_path.write_text(
    store_text,
    encoding="utf-8",
)


# =====================================================================
# PATCH PHASE 1 VERIFICATION SCRIPT
# =====================================================================

verification_text = (
    verification_path.read_text(
        encoding="utf-8-sig"
    )
)


old_container_check = '''
    checks[
        "reference_contains_article_body_container"
    ] = (
        b'class="article-body"'
        in reference_bytes
    )
'''

new_container_check = '''
    checks[
        "reference_contains_article_body_container"
    ] = bool(
        reference_validation.get(
            "body_container_found"
        )
    )
'''

if (
    old_container_check
    not in verification_text
):
    raise RuntimeError(
        "Could not find the old hardcoded "
        "article-body container check."
    )

verification_text = (
    verification_text.replace(
        old_container_check,
        new_container_check,
        1,
    )
)


old_mutation = '''
    modified_bytes = (
        reference_bytes.replace(
            b"UDARE Visual Review",
            b"UDARE Visual Review ",
            1,
        )
    )
'''

new_mutation = '''
    modified_bytes = (
        reference_bytes
        + b"\\n"
    )
'''

if old_mutation not in verification_text:
    raise RuntimeError(
        "Could not find the old review-label "
        "immutability mutation."
    )

verification_text = (
    verification_text.replace(
        old_mutation,
        new_mutation,
        1,
    )
)


verification_path.write_text(
    verification_text,
    encoding="utf-8",
)


print(
    "PATCH STATUS: PASS"
)

print(
    "Removed invented review-wrapper requirements."
)

print(
    "UDARE article validation is now based on "
    "the real HTML document structure."
)
