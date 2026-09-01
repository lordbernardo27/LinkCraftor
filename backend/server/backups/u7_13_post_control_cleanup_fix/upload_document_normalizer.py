from __future__ import annotations

"""
Canonical Uploaded Document normalization authority.

Phase U7 boundary:

    UploadExtractionResult
        ->
    normalize_uploaded_document_v1(...)
        ->
    NormalizedUploadedDocumentContent

Current implementation scope:
- U7.5 Unicode normalization only.

Later U7 substages extend this same canonical authority with:
- line-ending normalization,
- whitespace normalization,
- paragraph-boundary normalization,
- heading normalization,
- title normalization,
- control-character handling.

Boundary rules:
- Does not reread the persisted source file.
- Does not parse TXT / Markdown / HTML / DOCX.
- Does not perform Website cleaning.
- Does not build or persist UDUC.
- Does not build or persist UUCD.
- Does not perform Highlight / Active Target Set mutation.
- Does not perform semantic analysis, scoring, or ranking.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
import unicodedata


NORMALIZATION_VERSION = "uploaded_document_normalization_v1"

NORMALIZATION_STATUS_SUCCESS = "success"
NORMALIZATION_STATUS_INVALID_INPUT = "invalid_input"
NORMALIZATION_STATUS_INELIGIBLE_EXTRACTION = "ineligible_extraction"
NORMALIZATION_STATUS_ERROR = "normalization_error"

_ALLOWED_NORMALIZATION_STATUSES = {
    NORMALIZATION_STATUS_SUCCESS,
    NORMALIZATION_STATUS_INVALID_INPUT,
    NORMALIZATION_STATUS_INELIGIBLE_EXTRACTION,
    NORMALIZATION_STATUS_ERROR,
}


@dataclass
class NormalizedUploadedDocumentContent:
    source_path: str
    source_type: str
    title: str
    text: str
    headings: List[str]
    metadata: Dict[str, Any]
    extraction_status: str
    extraction_confidence: float
    extraction_created_at: str
    normalization_status: str
    normalization_version: str
    normalized_at: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_unicode_nfc(value: str) -> str:
    """
    Normalize Unicode to canonical NFC form.

    This intentionally does NOT:
    - use NFKC/NFKD compatibility folding,
    - transliterate to ASCII,
    - remove accents,
    - guess/fix mojibake,
    - remove zero-width or other format characters,
    - perform whitespace normalization.

    Those operations are either prohibited by the U7 contract or owned
    by later U7 substages.
    """
    return unicodedata.normalize("NFC", value)


def _normalize_line_endings_lf(value: str) -> str:
    """
    Normalize all line endings to LF.

    Contract:
    - CRLF -> LF
    - lone CR -> LF
    - existing LF preserved
    - does not collapse blank lines
    - does not normalize tabs or inline whitespace
    """
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _normalize_horizontal_whitespace(value: str) -> str:
    """
    Normalize ordinary horizontal whitespace while preserving line structure.

    Contract:
    - tab -> single ordinary space
    - repeated ordinary spaces -> one ordinary space
    - leading/trailing ordinary spaces on each line -> removed
    - LF boundaries preserved exactly
    - blank-line count preserved
    - NBSP and other Unicode spacing are not rewritten here
    """
    lines = value.split("\n")
    normalized_lines = []

    for line in lines:
        line = line.replace("\t", " ")
        line = " ".join(
            part
            for part in line.split(" ")
            if part != ""
        )
        normalized_lines.append(line)

    return "\n".join(normalized_lines)


def _normalize_paragraph_boundaries(value: str) -> str:
    """
    Normalize uploaded-document paragraph boundaries.

    Contract:
    - canonical paragraph separator is exactly one blank line ("\\n\\n")
    - runs of 3+ LF characters collapse to exactly 2 LF
    - existing 2-LF paragraph boundaries are preserved
    - single LF is preserved as an intra-paragraph line break
    - leading and trailing LF-only document-edge blank lines are removed
    - does not create paragraph objects, offsets, counts, or UDUC structure
    """
    value = value.strip("\n")

    while "\n\n\n" in value:
        value = value.replace("\n\n\n", "\n\n")

    return value


def _normalize_headings(headings: List[str]) -> List[str]:
    """
    Normalize extracted headings without adding structural interpretation.

    Contract:
    - NFC Unicode normalization
    - LF line endings
    - horizontal whitespace normalization
    - remove empty headings after normalization
    - preserve heading order
    - preserve duplicate headings
    - preserve intentional multi-line headings
    - no heading-level inference
    - no hierarchy construction
    - no body-position mapping
    """
    normalized: List[str] = []

    for heading in headings:
        value = _normalize_horizontal_whitespace(
            _normalize_line_endings_lf(
                _normalize_unicode_nfc(
                    heading
                )
            )
        )

        if value:
            normalized.append(value)

    return normalized


def _normalize_title(value: str) -> str:
    """
    Normalize the extractor-provided title without deriving a replacement.

    Contract:
    - NFC Unicode normalization
    - LF line endings
    - horizontal whitespace normalization
    - intentional LF structure is preserved
    - empty title remains empty
    - no filename fallback
    - no first-heading fallback
    - no body-derived fallback
    - no paragraph-boundary normalization
    - no title re-extraction
    """
    return _normalize_horizontal_whitespace(
        _normalize_line_endings_lf(
            _normalize_unicode_nfc(
                value
            )
        )
    )


def _remove_unsafe_control_characters(value: str) -> str:
    """
    Remove unsafe control artifacts while preserving semantic Unicode formatting.

    Contract:
    - preserve LF
    - remove C0 controls except LF
    - remove DEL
    - remove C1 controls
    - remove embedded U+FEFF artifacts
    - preserve NBSP
    - preserve ZWJ and ZWNJ
    - do not blanket-remove Unicode format characters
    """
    cleaned = []

    for char in value:
        codepoint = ord(char)

        if char == "\n":
            cleaned.append(char)
            continue

        if 0x0000 <= codepoint <= 0x001F:
            continue

        if codepoint == 0x007F:
            continue

        if 0x0080 <= codepoint <= 0x009F:
            continue

        if codepoint == 0xFEFF:
            continue

        cleaned.append(char)

    return "".join(cleaned)


def _copy_metadata(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        return {}

    return dict(value)


def _result_from_input(
    extraction_result: Any,
    *,
    title: str,
    text: str,
    headings: List[str],
    normalization_status: str,
    metadata: Dict[str, Any],
) -> NormalizedUploadedDocumentContent:
    return NormalizedUploadedDocumentContent(
        source_path=str(
            getattr(
                extraction_result,
                "source_path",
                "",
            )
        ),
        source_type=str(
            getattr(
                extraction_result,
                "source_type",
                "",
            )
        ),
        title=title,
        text=text,
        headings=headings,
        metadata=metadata,
        extraction_status=str(
            getattr(
                extraction_result,
                "extraction_status",
                "",
            )
        ),
        extraction_confidence=float(
            getattr(
                extraction_result,
                "extraction_confidence",
                0.0,
            )
            or 0.0
        ),
        extraction_created_at=str(
            getattr(
                extraction_result,
                "created_at",
                "",
            )
        ),
        normalization_status=normalization_status,
        normalization_version=NORMALIZATION_VERSION,
        normalized_at=_now_iso(),
    )


def normalize_uploaded_document_v1(
    extraction_result: Any,
) -> NormalizedUploadedDocumentContent:
    """
    Normalize successfully extracted uploaded-document content.

    Canonical input:
        UploadExtractionResult

    Current U7.5 transformation:
        Unicode canonical composition (NFC) across:
        - title
        - text
        - headings

    Source identity and extraction provenance are preserved.
    """

    try:
        required_attributes = (
            "source_path",
            "source_type",
            "title",
            "text",
            "headings",
            "metadata",
            "extraction_status",
            "extraction_confidence",
            "created_at",
        )

        if extraction_result is None or any(
            not hasattr(
                extraction_result,
                attribute,
            )
            for attribute in required_attributes
        ):
            raise TypeError(
                "Expected UploadExtractionResult-compatible input."
            )

        metadata = _copy_metadata(
            extraction_result.metadata
        )

        extraction_status = str(
            extraction_result.extraction_status
            or ""
        )

        raw_title = extraction_result.title
        raw_text = extraction_result.text
        raw_headings = extraction_result.headings

        if not isinstance(raw_title, str):
            raise TypeError(
                "UploadExtractionResult.title must be a string."
            )

        if not isinstance(raw_text, str):
            raise TypeError(
                "UploadExtractionResult.text must be a string."
            )

        if not isinstance(raw_headings, list):
            raise TypeError(
                "UploadExtractionResult.headings must be a list."
            )

        if not all(
            isinstance(
                heading,
                str,
            )
            for heading in raw_headings
        ):
            raise TypeError(
                "UploadExtractionResult.headings must contain only strings."
            )

        if extraction_status != "success":
            metadata["normalization"] = {
                "version": NORMALIZATION_VERSION,
                "status": NORMALIZATION_STATUS_INELIGIBLE_EXTRACTION,
                "unicode_form": "NFC",
                "operations": [],
            }

            return _result_from_input(
                extraction_result,
                title=raw_title,
                text=raw_text,
                headings=list(raw_headings),
                normalization_status=(
                    NORMALIZATION_STATUS_INELIGIBLE_EXTRACTION
                ),
                metadata=metadata,
            )

        normalized_title = _remove_unsafe_control_characters(
            _normalize_title(
                raw_title
            )
        )

        normalized_text = _remove_unsafe_control_characters(
            _normalize_paragraph_boundaries(
                _normalize_horizontal_whitespace(
                    _normalize_line_endings_lf(
                        _normalize_unicode_nfc(
                            raw_text
                        )
                    )
                )
            )
        )

        normalized_headings = [
            value
            for value in (
                _remove_unsafe_control_characters(
                    heading
                )
                for heading in _normalize_headings(
                    raw_headings
                )
            )
            if value
        ]

        metadata["normalization"] = {
            "version": NORMALIZATION_VERSION,
            "status": NORMALIZATION_STATUS_SUCCESS,
            "unicode_form": "NFC",
            "operations": [
                "unicode_nfc",
                "line_endings_lf",
                "horizontal_whitespace",
                "paragraph_boundaries",
                "heading_normalization",
                "title_normalization",
                "control_character_handling",
            ],
        }

        return _result_from_input(
            extraction_result,
            title=normalized_title,
            text=normalized_text,
            headings=normalized_headings,
            normalization_status=(
                NORMALIZATION_STATUS_SUCCESS
            ),
            metadata=metadata,
        )

    except (
        TypeError,
        ValueError,
        AttributeError,
    ):
        raise

    except Exception as exc:
        metadata = {}

        if extraction_result is not None:
            metadata = _copy_metadata(
                getattr(
                    extraction_result,
                    "metadata",
                    {},
                )
            )

        metadata["normalization"] = {
            "version": NORMALIZATION_VERSION,
            "status": NORMALIZATION_STATUS_ERROR,
            "unicode_form": "NFC",
            "operations": [],
            "error_type": type(exc).__name__,
        }

        return _result_from_input(
            extraction_result,
            title=str(
                getattr(
                    extraction_result,
                    "title",
                    "",
                )
            ),
            text=str(
                getattr(
                    extraction_result,
                    "text",
                    "",
                )
            ),
            headings=list(
                getattr(
                    extraction_result,
                    "headings",
                    [],
                )
                or []
            ),
            normalization_status=(
                NORMALIZATION_STATUS_ERROR
            ),
            metadata=metadata,
        )