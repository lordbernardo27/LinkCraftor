from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.parse import urlsplit


# =====================================================================
# UDARE STORE V1 — PHASE 1
# =====================================================================
#
# Scope:
#   - Permanent store schema
#   - Directory creation
#   - Atomic HTML-document persistence
#   - Operational metadata persistence
#   - Loading
#   - Manifest refresh
#   - Schema and persistence verification
#
# Explicitly excluded:
#   - Runtime integration
#   - Job creation
#   - Queues
#   - Workers
#   - Retry / resume / dead-letter
#   - Population of the 2,225 articles
#   - Website Article Integrity Validator
#   - Article Validation
#   - Certified Website Article Store
#
# Frozen content rule:
#   The reconstructed article is stored as a complete HTML reader
#   document. JSON contains identity, paths, hashes and operational
#   metadata only. JSON must not contain the article body.
# =====================================================================


SERVER_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = SERVER_ROOT / "data"

STORE_ROOT = DATA_ROOT / "udare_store"

STORE_VERSION = "udare_store_v1"
RECORD_SCHEMA_VERSION = "udare_store_record_v1"
MANIFEST_SCHEMA_VERSION = "udare_store_manifest_v1"

ARTICLE_DOCUMENT_FORMAT = (
    "udare_article_reader_document_v1"
)

REQUIRED_UDARE_ENGINE = (
    "universal_dom_article_reconstruction_engine_v1_8"
)

SOURCE_STORE_VERSION = "raw_website_html_store_v1"


REQUIRED_ARTICLE_DOCUMENT_MARKERS = (
    "<!doctype html",
    "<html",
    "<head",
    "<body",
)


FORBIDDEN_OPERATIONAL_METADATA_KEYS = {
    "article_body",
    "raw_article_text",
    "content_blocks",
    "article_html",
    "article_document_html",
    "selected_html",
    "raw_main_html",
    "raw_html",
    "html",
    "primary_content",
    "body_text",
    "article_text",
}


UDARE_STORE_SCHEMA_V1: Dict[str, Any] = {
    "store_version":
        STORE_VERSION,

    "record_schema_version":
        RECORD_SCHEMA_VERSION,

    "manifest_schema_version":
        MANIFEST_SCHEMA_VERSION,

    "article_document": {
        "format":
            ARTICLE_DOCUMENT_FORMAT,

        "media_type":
            "text/html",

        "encoding":
            "utf-8",

        "primary_content_location":
            "articles/*.html",

        "stored_without_mutation":
            True,
    },

    "json_metadata": {
        "location":
            "metadata/*.json",

        "contains_article_body":
            False,

        "allowed_purpose": [
            "identity",
            "source mapping",
            "file paths",
            "content hashes",
            "runtime references",
            "reconstruction statistics",
            "timestamps",
            "operational state",
        ],
    },

    "required_record_fields": [
        "schema_version",
        "store_version",
        "workspace_id",
        "document_id",
        "html_id",
        "source_url",
        "source_store_version",
        "source_record_id",
        "title",
        "h1",
        "headings",
        "udare_engine",
        "reconstruction_status",
        "article_document",
        "content_integrity",
        "runtime_context",
        "persisted_at_utc",
        "persistence_status",
    ],

    "required_directories": [
        "articles",
        "metadata",
        "indexes",
        "manifests",
        "certification",
    ],

    "phase_1_exclusions": [
        "runtime integration",
        "queue",
        "worker",
        "population",
        "integrity validation",
        "article validation",
        "certified website article store",
    ],
}


class UdareStoreError(RuntimeError):
    """Base exception for UDARE Store operations."""


class UdareStoreSchemaError(UdareStoreError):
    """The supplied record violates the frozen store schema."""


class UdareStoreConflict(UdareStoreError):
    """An immutable stored document would be replaced implicitly."""


def _utc_now_v1() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _safe_component_v1(
    value: str,
    *,
    fallback: str,
) -> str:
    cleaned = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        str(value or "").strip(),
    )

    cleaned = cleaned.strip(
        "._-"
    )

    return (
        cleaned
        or fallback
    )[:180]


def _safe_workspace_id_v1(
    workspace_id: str,
) -> str:
    return _safe_component_v1(
        workspace_id,
        fallback="default",
    )


def _safe_document_id_v1(
    document_id: str,
) -> str:
    return _safe_component_v1(
        document_id,
        fallback="document",
    )


def _sha256_bytes_v1(
    value: bytes,
) -> str:
    return hashlib.sha256(
        value
    ).hexdigest()


def _sha256_text_v1(
    value: str,
) -> str:
    return _sha256_bytes_v1(
        str(value or "").encode(
            "utf-8"
        )
    )


def _atomic_write_bytes_v1(
    path: Path,
    payload: bytes,
) -> Path:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_descriptor, temporary_name = (
        tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=str(path.parent),
        )
    )

    try:
        with os.fdopen(
            file_descriptor,
            "wb",
        ) as handle:
            handle.write(
                payload
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        os.replace(
            temporary_name,
            path,
        )

    except Exception:
        try:
            os.unlink(
                temporary_name
            )

        except FileNotFoundError:
            pass

        raise

    return path


def _atomic_write_json_v1(
    path: Path,
    value: Dict[str, Any],
) -> Path:
    payload = (
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    ).encode(
        "utf-8"
    )

    return _atomic_write_bytes_v1(
        path,
        payload,
    )


def _read_json_v1(
    path: Path,
) -> Dict[str, Any]:
    result = json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )

    if not isinstance(
        result,
        dict,
    ):
        raise UdareStoreSchemaError(
            f"Expected a JSON object: {path}"
        )

    return result


def _workspace_paths_v1(
    workspace_id: str,
) -> Dict[str, Path]:
    safe_workspace_id = (
        _safe_workspace_id_v1(
            workspace_id
        )
    )

    root = (
        STORE_ROOT
        / safe_workspace_id
    )

    return {
        "root":
            root,

        "articles":
            root / "articles",

        "metadata":
            root / "metadata",

        "indexes":
            root / "indexes",

        "manifests":
            root / "manifests",

        "certification":
            root / "certification",

        "manifest":
            (
                root
                / "manifests"
                / "udare_store_manifest.json"
            ),
    }


def get_udare_store_paths_v1(
    workspace_id: str,
) -> Dict[str, str]:
    return {
        key:
            str(value)

        for key, value
        in _workspace_paths_v1(
            workspace_id
        ).items()
    }


def get_udare_store_schema_v1() -> Dict[str, Any]:
    return json.loads(
        json.dumps(
            UDARE_STORE_SCHEMA_V1
        )
    )


def _relative_path_v1(
    path: Path,
    workspace_root: Path,
) -> str:
    return (
        path.resolve()
        .relative_to(
            workspace_root.resolve()
        )
        .as_posix()
    )


def _check_operational_metadata_v1(
    value: Any,
    *,
    location: str = "operational_metadata",
) -> None:
    if isinstance(
        value,
        dict,
    ):
        for key, child in value.items():
            normalized_key = str(
                key or ""
            ).strip().casefold()

            if (
                normalized_key
                in FORBIDDEN_OPERATIONAL_METADATA_KEYS
            ):
                raise UdareStoreSchemaError(
                    f"{location}.{key} is forbidden. "
                    "Article content belongs only in "
                    "the HTML article document."
                )

            _check_operational_metadata_v1(
                child,
                location=(
                    f"{location}.{key}"
                ),
            )

    elif isinstance(
        value,
        list,
    ):
        for index, child in enumerate(
            value
        ):
            _check_operational_metadata_v1(
                child,
                location=(
                    f"{location}[{index}]"
                ),
            )


def _decode_article_document_v1(
    article_document: str | bytes,
) -> tuple[str, bytes]:
    if isinstance(
        article_document,
        bytes,
    ):
        document_bytes = (
            article_document
        )

        try:
            document_text = (
                document_bytes.decode(
                    "utf-8-sig"
                )
            )

        except UnicodeDecodeError as exc:
            raise UdareStoreSchemaError(
                "The article document must use UTF-8."
            ) from exc

        return (
            document_text,
            document_bytes,
        )

    document_text = str(
        article_document or ""
    )

    return (
        document_text,
        document_text.encode(
            "utf-8"
        ),
    )


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

    *,
    source_url: str,
    html_id: str,
    document_id: str,
) -> str:
    url_path = urlsplit(
        str(source_url or "")
    ).path.strip(
        "/"
    )

    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        url_path.casefold(),
    ).strip(
        "-"
    )

    slug = (
        slug[:120].rstrip("-")
        or "article"
    )

    html_token = re.sub(
        r"^raw_html_",
        "",
        str(html_id or "").strip(),
        flags=re.IGNORECASE,
    )

    html_token = re.sub(
        r"[^a-fA-F0-9]",
        "",
        html_token,
    )[:8].casefold()

    if not html_token:
        html_token = (
            _sha256_text_v1(
                source_url
                or document_id
            )[:8]
        )

    return (
        f"{slug}_{html_token}.html"
    )


def _validate_article_filename_v1(
    article_filename: str,
) -> str:
    filename = str(
        article_filename or ""
    ).strip()

    if not filename:
        raise UdareStoreSchemaError(
            "article_filename is empty"
        )

    if Path(filename).name != filename:
        raise UdareStoreSchemaError(
            "article_filename must not contain "
            "directory traversal."
        )

    if not filename.casefold().endswith(
        ".html"
    ):
        raise UdareStoreSchemaError(
            "article_filename must end in .html"
        )

    if filename in {
        ".",
        "..",
    }:
        raise UdareStoreSchemaError(
            "Invalid article filename."
        )

    return filename


def create_udare_store_v1(
    workspace_id: str,
) -> Dict[str, Any]:
    if not str(
        workspace_id or ""
    ).strip():
        raise UdareStoreSchemaError(
            "workspace_id is required"
        )

    paths = _workspace_paths_v1(
        workspace_id
    )

    for directory_name in (
        "articles",
        "metadata",
        "indexes",
        "manifests",
        "certification",
    ):
        paths[
            directory_name
        ].mkdir(
            parents=True,
            exist_ok=True,
        )

    manifest_path = paths[
        "manifest"
    ]

    created = False

    if manifest_path.exists():
        manifest = _read_json_v1(
            manifest_path
        )

        if (
            manifest.get(
                "schema_version"
            )
            != MANIFEST_SCHEMA_VERSION
        ):
            raise UdareStoreSchemaError(
                "Existing manifest has an "
                "unexpected schema version."
            )

        if (
            manifest.get(
                "workspace_id"
            )
            != workspace_id
        ):
            raise UdareStoreSchemaError(
                "Existing manifest workspace mismatch."
            )

    else:
        now = _utc_now_v1()

        manifest = {
            "schema_version":
                MANIFEST_SCHEMA_VERSION,

            "store_version":
                STORE_VERSION,

            "store_name":
                "UDARE Store",

            "workspace_id":
                workspace_id,

            "article_document_format":
                ARTICLE_DOCUMENT_FORMAT,

            "required_udare_engine":
                REQUIRED_UDARE_ENGINE,

            "source_store_version":
                SOURCE_STORE_VERSION,

            "created_at_utc":
                now,

            "updated_at_utc":
                now,

            "population_status":
                "empty",

            "record_count":
                0,

            "article_document_count":
                0,

            "metadata_record_count":
                0,

            "phase":
                "phase_1_schema_and_persistence",

            "runtime_integrated":
                False,

            "queue_created":
                False,

            "workers_created":
                False,

            "population_started":
                False,

            "certification_status":
                "NOT_STARTED",

            "paths": {
                "articles":
                    "articles",

                "metadata":
                    "metadata",

                "indexes":
                    "indexes",

                "manifests":
                    "manifests",

                "certification":
                    "certification",
            },
        }

        _atomic_write_json_v1(
            manifest_path,
            manifest,
        )

        created = True

    return {
        "ok":
            True,

        "created":
            created,

        "workspace_id":
            workspace_id,

        "store_root":
            str(
                paths["root"]
            ),

        "manifest_path":
            str(
                manifest_path
            ),

        "manifest":
            manifest,
    }


def persist_udare_article_document_v1(
    *,
    workspace_id: str,
    document_id: str,
    html_id: str,
    source_url: str,
    title: str,
    h1: str,
    headings: Iterable[str] | None,
    article_document: str | bytes,
    article_filename: str | None = None,
    udare_engine: str = REQUIRED_UDARE_ENGINE,
    source_store_version: str = SOURCE_STORE_VERSION,
    source_record_id: str | None = None,
    reconstruction_status: str = "completed",
    selected_tag: str = "",
    udare_article_body_sha256: str = "",
    content_block_count: int | None = None,
    job_id: str | None = None,
    batch_id: str | None = None,
    attempt: int | None = None,
    operational_metadata: Dict[str, Any] | None = None,
    expected_document_sha256: str | None = None,
    allow_replace: bool = False,
) -> Dict[str, Any]:
    required_values = {
        "workspace_id":
            workspace_id,

        "document_id":
            document_id,

        "html_id":
            html_id,

        "source_url":
            source_url,

        "udare_engine":
            udare_engine,
    }

    missing_fields = [
        key

        for key, value
        in required_values.items()

        if not str(
            value or ""
        ).strip()
    ]

    if missing_fields:
        raise UdareStoreSchemaError(
            "Missing required fields: "
            + ", ".join(
                missing_fields
            )
        )

    if (
        udare_engine
        != REQUIRED_UDARE_ENGINE
    ):
        raise UdareStoreSchemaError(
            "UDARE Store accepts only "
            f"{REQUIRED_UDARE_ENGINE}."
        )

    if (
        source_store_version
        != SOURCE_STORE_VERSION
    ):
        raise UdareStoreSchemaError(
            "UDARE Store Phase 1 accepts only "
            f"{SOURCE_STORE_VERSION} as its source."
        )

    extra_metadata = (
        operational_metadata
        or {}
    )

    if not isinstance(
        extra_metadata,
        dict,
    ):
        raise UdareStoreSchemaError(
            "operational_metadata must be a dictionary."
        )

    _check_operational_metadata_v1(
        extra_metadata
    )

    document_text, document_bytes = (
        _decode_article_document_v1(
            article_document
        )
    )

    document_validation = (
        validate_udare_article_document_v1(
            document_bytes
        )
    )

    if not document_validation[
        "ok"
    ]:
        raise UdareStoreSchemaError(
            "Invalid UDARE article document: "
            + ", ".join(
                document_validation[
                    "errors"
                ]
            )
        )

    document_sha256 = (
        document_validation[
            "document_sha256"
        ]
    )

    if (
        expected_document_sha256
        and expected_document_sha256
        != document_sha256
    ):
        raise UdareStoreSchemaError(
            "Expected article-document hash "
            "does not match the supplied document."
        )

    create_udare_store_v1(
        workspace_id
    )

    paths = _workspace_paths_v1(
        workspace_id
    )

    final_article_filename = (
        _validate_article_filename_v1(
            article_filename
        )
        if article_filename
        else _default_article_filename_v1(
            source_url=
                source_url,

            html_id=
                html_id,

            document_id=
                document_id,
        )
    )

    safe_document_id = (
        _safe_document_id_v1(
            document_id
        )
    )

    article_path = (
        paths["articles"]
        / final_article_filename
    )

    metadata_path = (
        paths["metadata"]
        / f"{safe_document_id}.json"
    )

    existing_record: Dict[str, Any] | None = None

    if metadata_path.exists():
        existing_record = (
            _read_json_v1(
                metadata_path
            )
        )

        if (
            existing_record.get(
                "document_id"
            )
            != document_id
        ):
            raise UdareStoreConflict(
                "Sanitized document ID collision: "
                f"{metadata_path}"
            )

        existing_article_info = (
            existing_record.get(
                "article_document"
            )
            or {}
        )

        existing_hash = (
            existing_article_info.get(
                "sha256"
            )
        )

        existing_relative_path = str(
            existing_article_info.get(
                "relative_path"
            )
            or ""
        )

        existing_article_path = (
            paths["root"]
            / existing_relative_path
        )

        if (
            existing_hash
            == document_sha256
            and existing_article_path.exists()
        ):
            stored_hash = (
                _sha256_bytes_v1(
                    existing_article_path.read_bytes()
                )
            )

            if (
                stored_hash
                != document_sha256
            ):
                raise UdareStoreConflict(
                    "Stored metadata hash matches, "
                    "but stored HTML bytes do not."
                )

            return {
                "ok":
                    True,

                "status":
                    "unchanged",

                "workspace_id":
                    workspace_id,

                "document_id":
                    document_id,

                "article_path":
                    str(
                        existing_article_path
                    ),

                "metadata_path":
                    str(
                        metadata_path
                    ),

                "document_sha256":
                    document_sha256,

                "record":
                    existing_record,
            }

        if not allow_replace:
            raise UdareStoreConflict(
                "An immutable UDARE article already "
                "exists with different content: "
                f"{metadata_path}"
            )

    elif (
        article_path.exists()
        and not allow_replace
    ):
        raise UdareStoreConflict(
            "An unindexed article file already exists: "
            f"{article_path}"
        )

    now = _utc_now_v1()

    created_at = (
        str(
            existing_record.get(
                "created_at_utc"
            )
        )
        if (
            existing_record
            and existing_record.get(
                "created_at_utc"
            )
        )
        else now
    )

    heading_values = [
        str(
            heading
        )

        for heading
        in (
            headings
            or []
        )
    ]

    record = {
        "schema_version":
            RECORD_SCHEMA_VERSION,

        "store_version":
            STORE_VERSION,

        "record_type":
            "udare_reconstructed_article",

        "workspace_id":
            workspace_id,

        "document_id":
            document_id,

        "html_id":
            html_id,

        "source_url":
            source_url,

        "source_store_version":
            source_store_version,

        "source_record_id":
            (
                source_record_id
                or html_id
            ),

        "title":
            str(
                title or ""
            ),

        "h1":
            str(
                h1 or ""
            ),

        "headings":
            heading_values,

        "heading_count":
            len(
                heading_values
            ),

        "udare_engine":
            udare_engine,

        "reconstruction_status":
            str(
                reconstruction_status
                or ""
            ),

        "selected_tag":
            str(
                selected_tag
                or ""
            ),

        "article_document": {
            "format":
                ARTICLE_DOCUMENT_FORMAT,

            "media_type":
                "text/html",

            "encoding":
                "utf-8",

            "filename":
                final_article_filename,

            "relative_path":
                _relative_path_v1(
                    article_path,
                    paths["root"],
                ),

            "sha256":
                document_sha256,

            "byte_length":
                len(
                    document_bytes
                ),

            "stored_without_mutation":
                True,
        },

        "content_integrity": {
            "udare_article_body_sha256":
                str(
                    udare_article_body_sha256
                    or ""
                ),

            "reader_body_text_sha256":
                document_validation[
                    "reader_body_text_sha256"
                ],

            "reader_body_word_count":
                document_validation[
                    "reader_body_word_count"
                ],

            "reader_body_character_count":
                document_validation[
                    "reader_body_character_count"
                ],

            "content_block_count":
                (
                    int(
                        content_block_count
                    )
                    if (
                        content_block_count
                        is not None
                    )
                    else None
                ),
        },

        "runtime_context": {
            "job_id":
                job_id,

            "batch_id":
                batch_id,

            "attempt":
                (
                    int(
                        attempt
                    )
                    if attempt is not None
                    else None
                ),
        },

        "created_at_utc":
            created_at,

        "updated_at_utc":
            now,

        "persisted_at_utc":
            now,

        "persistence_status":
            "stored",

        "operational_metadata":
            extra_metadata,
    }

    # The HTML file is written exactly as supplied.
    # It is not parsed, normalized, reformatted or reconstructed here.
    _atomic_write_bytes_v1(
        article_path,
        document_bytes,
    )

    _atomic_write_json_v1(
        metadata_path,
        record,
    )

    return {
        "ok":
            True,

        "status":
            (
                "replaced"
                if existing_record
                else "created"
            ),

        "workspace_id":
            workspace_id,

        "document_id":
            document_id,

        "article_path":
            str(
                article_path
            ),

        "metadata_path":
            str(
                metadata_path
            ),

        "document_sha256":
            document_sha256,

        "record":
            record,
    }


def load_udare_article_document_v1(
    *,
    workspace_id: str,
    document_id: str,
) -> Dict[str, Any] | None:
    paths = _workspace_paths_v1(
        workspace_id
    )

    metadata_path = (
        paths["metadata"]
        / (
            _safe_document_id_v1(
                document_id
            )
            + ".json"
        )
    )

    if not metadata_path.exists():
        return None

    record = _read_json_v1(
        metadata_path
    )

    if (
        record.get(
            "document_id"
        )
        != document_id
    ):
        raise UdareStoreSchemaError(
            "Stored document ID does not match "
            "the requested document ID."
        )

    article_info = (
        record.get(
            "article_document"
        )
        or {}
    )

    relative_path = str(
        article_info.get(
            "relative_path"
        )
        or ""
    )

    article_path = (
        paths["root"]
        / relative_path
    ).resolve()

    try:
        article_path.relative_to(
            paths["root"].resolve()
        )

    except ValueError as exc:
        raise UdareStoreSchemaError(
            "Stored article path escapes the "
            "workspace store."
        ) from exc

    if not article_path.exists():
        raise UdareStoreSchemaError(
            f"Stored article file is missing: {article_path}"
        )

    article_bytes = (
        article_path.read_bytes()
    )

    actual_sha256 = (
        _sha256_bytes_v1(
            article_bytes
        )
    )

    expected_sha256 = str(
        article_info.get(
            "sha256"
        )
        or ""
    )

    if (
        actual_sha256
        != expected_sha256
    ):
        raise UdareStoreSchemaError(
            "Stored article-document hash mismatch."
        )

    return {
        "ok":
            True,

        "workspace_id":
            workspace_id,

        "document_id":
            document_id,

        "record":
            record,

        "article_document_bytes":
            article_bytes,

        "article_document_html":
            article_bytes.decode(
                "utf-8-sig"
            ),

        "article_path":
            str(
                article_path
            ),

        "metadata_path":
            str(
                metadata_path
            ),
    }


def refresh_udare_store_manifest_v1(
    workspace_id: str,
) -> Dict[str, Any]:
    create_udare_store_v1(
        workspace_id
    )

    paths = _workspace_paths_v1(
        workspace_id
    )

    metadata_count = len(
        list(
            paths["metadata"].glob(
                "*.json"
            )
        )
    )

    article_count = len(
        list(
            paths["articles"].glob(
                "*.html"
            )
        )
    )

    manifest = _read_json_v1(
        paths["manifest"]
    )

    manifest[
        "updated_at_utc"
    ] = _utc_now_v1()

    manifest[
        "record_count"
    ] = metadata_count

    manifest[
        "metadata_record_count"
    ] = metadata_count

    manifest[
        "article_document_count"
    ] = article_count

    manifest[
        "population_status"
    ] = (
        "empty"
        if metadata_count == 0
        else "populated_not_certified"
    )

    _atomic_write_json_v1(
        paths["manifest"],
        manifest,
    )

    return {
        "ok":
            metadata_count
            == article_count,

        "workspace_id":
            workspace_id,

        "record_count":
            metadata_count,

        "article_document_count":
            article_count,

        "manifest_path":
            str(
                paths["manifest"]
            ),
    }


def verify_udare_store_v1(
    workspace_id: str,
) -> Dict[str, Any]:
    paths = _workspace_paths_v1(
        workspace_id
    )

    checks: Dict[str, bool] = {}
    errors: List[str] = []

    for directory_name in (
        "root",
        "articles",
        "metadata",
        "indexes",
        "manifests",
        "certification",
    ):
        checks[
            f"directory_exists:{directory_name}"
        ] = paths[
            directory_name
        ].is_dir()

    checks[
        "manifest_exists"
    ] = paths[
        "manifest"
    ].is_file()

    manifest: Dict[str, Any] = {}

    if checks[
        "manifest_exists"
    ]:
        try:
            manifest = _read_json_v1(
                paths["manifest"]
            )

            checks[
                "manifest_schema"
            ] = (
                manifest.get(
                    "schema_version"
                )
                == MANIFEST_SCHEMA_VERSION
            )

            checks[
                "manifest_store_version"
            ] = (
                manifest.get(
                    "store_version"
                )
                == STORE_VERSION
            )

            checks[
                "manifest_workspace"
            ] = (
                manifest.get(
                    "workspace_id"
                )
                == workspace_id
            )

            checks[
                "manifest_document_format"
            ] = (
                manifest.get(
                    "article_document_format"
                )
                == ARTICLE_DOCUMENT_FORMAT
            )

            checks[
                "manifest_engine"
            ] = (
                manifest.get(
                    "required_udare_engine"
                )
                == REQUIRED_UDARE_ENGINE
            )

            checks[
                "phase_1_runtime_not_integrated"
            ] = (
                manifest.get(
                    "runtime_integrated"
                )
                is False
            )

            checks[
                "phase_1_queue_not_created"
            ] = (
                manifest.get(
                    "queue_created"
                )
                is False
            )

            checks[
                "phase_1_workers_not_created"
            ] = (
                manifest.get(
                    "workers_created"
                )
                is False
            )

            checks[
                "phase_1_population_not_started"
            ] = (
                manifest.get(
                    "population_started"
                )
                is False
            )

        except Exception as exc:
            errors.append(
                f"manifest_error:{exc}"
            )

            checks[
                "manifest_schema"
            ] = False

    metadata_paths = sorted(
        paths["metadata"].glob(
            "*.json"
        )
    ) if paths[
        "metadata"
    ].exists() else []

    article_paths = sorted(
        paths["articles"].glob(
            "*.html"
        )
    ) if paths[
        "articles"
    ].exists() else []

    document_ids: List[str] = []
    html_ids: List[str] = []
    source_urls: List[str] = []

    referenced_articles: set[Path] = set()

    for metadata_path in metadata_paths:
        try:
            record = _read_json_v1(
                metadata_path
            )

            if (
                record.get(
                    "schema_version"
                )
                != RECORD_SCHEMA_VERSION
            ):
                raise UdareStoreSchemaError(
                    "record schema mismatch"
                )

            if (
                record.get(
                    "workspace_id"
                )
                != workspace_id
            ):
                raise UdareStoreSchemaError(
                    "record workspace mismatch"
                )

            if (
                record.get(
                    "udare_engine"
                )
                != REQUIRED_UDARE_ENGINE
            ):
                raise UdareStoreSchemaError(
                    "record UDARE engine mismatch"
                )

            if (
                record.get(
                    "source_store_version"
                )
                != SOURCE_STORE_VERSION
            ):
                raise UdareStoreSchemaError(
                    "record source store mismatch"
                )

            operational_metadata = (
                record.get(
                    "operational_metadata"
                )
                or {}
            )

            _check_operational_metadata_v1(
                operational_metadata
            )

            document_id = str(
                record.get(
                    "document_id"
                )
                or ""
            )

            html_id = str(
                record.get(
                    "html_id"
                )
                or ""
            )

            source_url = str(
                record.get(
                    "source_url"
                )
                or ""
            )

            if not all(
                (
                    document_id,
                    html_id,
                    source_url,
                )
            ):
                raise UdareStoreSchemaError(
                    "record identity is incomplete"
                )

            document_ids.append(
                document_id
            )

            html_ids.append(
                html_id
            )

            source_urls.append(
                source_url
            )

            article_info = (
                record.get(
                    "article_document"
                )
                or {}
            )

            if (
                article_info.get(
                    "format"
                )
                != ARTICLE_DOCUMENT_FORMAT
            ):
                raise UdareStoreSchemaError(
                    "article document format mismatch"
                )

            relative_path = str(
                article_info.get(
                    "relative_path"
                )
                or ""
            )

            article_path = (
                paths["root"]
                / relative_path
            ).resolve()

            article_path.relative_to(
                paths["root"].resolve()
            )

            referenced_articles.add(
                article_path
            )

            if not article_path.is_file():
                raise UdareStoreSchemaError(
                    "article document is missing"
                )

            article_bytes = (
                article_path.read_bytes()
            )

            if (
                _sha256_bytes_v1(
                    article_bytes
                )
                != article_info.get(
                    "sha256"
                )
            ):
                raise UdareStoreSchemaError(
                    "article document hash mismatch"
                )

            article_validation = (
                validate_udare_article_document_v1(
                    article_bytes
                )
            )

            if not article_validation[
                "ok"
            ]:
                raise UdareStoreSchemaError(
                    "invalid article document: "
                    + ", ".join(
                        article_validation[
                            "errors"
                        ]
                    )
                )

        except Exception as exc:
            errors.append(
                f"{metadata_path.name}:{exc}"
            )

    orphan_articles = [
        str(
            article_path
        )

        for article_path
        in article_paths

        if (
            article_path.resolve()
            not in referenced_articles
        )
    ]

    duplicate_document_ids = sorted({
        value

        for value
        in document_ids

        if document_ids.count(
            value
        ) > 1
    })

    duplicate_html_ids = sorted({
        value

        for value
        in html_ids

        if html_ids.count(
            value
        ) > 1
    })

    duplicate_source_urls = sorted({
        value

        for value
        in source_urls

        if source_urls.count(
            value
        ) > 1
    })

    checks[
        "metadata_article_count_match"
    ] = (
        len(
            metadata_paths
        )
        == len(
            article_paths
        )
    )

    checks[
        "manifest_metadata_count_match"
    ] = (
        int(
            manifest.get(
                "metadata_record_count"
            )
            or 0
        )
        == len(
            metadata_paths
        )
    )

    checks[
        "manifest_article_count_match"
    ] = (
        int(
            manifest.get(
                "article_document_count"
            )
            or 0
        )
        == len(
            article_paths
        )
    )

    checks[
        "no_orphan_articles"
    ] = not orphan_articles

    checks[
        "no_duplicate_document_ids"
    ] = not duplicate_document_ids

    checks[
        "no_duplicate_html_ids"
    ] = not duplicate_html_ids

    checks[
        "no_duplicate_source_urls"
    ] = not duplicate_source_urls

    checks[
        "all_records_valid"
    ] = not errors

    passed = (
        all(
            checks.values()
        )
        and not errors
    )

    return {
        "ok":
            passed,

        "status":
            (
                "PASS"
                if passed
                else "FAIL"
            ),

        "workspace_id":
            workspace_id,

        "store_root":
            str(
                paths["root"]
            ),

        "checks":
            checks,

        "counts": {
            "metadata_records":
                len(
                    metadata_paths
                ),

            "article_documents":
                len(
                    article_paths
                ),
        },

        "duplicates": {
            "document_ids":
                duplicate_document_ids,

            "html_ids":
                duplicate_html_ids,

            "source_urls":
                duplicate_source_urls,
        },

        "orphan_articles":
            orphan_articles,

        "errors":
            errors,
    }


def explain_udare_store_v1() -> Dict[str, Any]:
    return {
        "name":
            "UDARE Store",

        "store_version":
            STORE_VERSION,

        "record_schema_version":
            RECORD_SCHEMA_VERSION,

        "manifest_schema_version":
            MANIFEST_SCHEMA_VERSION,

        "pipeline_stage":
            "UDARE Store",

        "input_stage":
            "UDARE v1.7 Reconstruction",

        "required_udare_engine":
            REQUIRED_UDARE_ENGINE,

        "source_store_version":
            SOURCE_STORE_VERSION,

        "article_document_format":
            ARTICLE_DOCUMENT_FORMAT,

        "article_storage":
            "UTF-8 HTML reader documents under articles/",

        "json_storage":
            (
                "Identity, source mapping, paths, hashes, "
                "runtime references and operational metadata only"
            ),

        "article_body_in_json":
            False,

        "stored_without_mutation":
            True,

        "downstream_stage":
            "Website Article Integrity Validator",

        "runtime_integration_included":
            False,

        "queue_or_worker_included":
            False,

        "population_included":
            False,
    }
