"""Canonical text-statistics utilities.

All content-pipeline components must use these functions when
calculating article-body statistics.

Canonical word-count rule:
- Count non-empty tokens separated by Unicode whitespace.
- Preserve punctuation inside tokens.
- Do not modify or normalize the source text.
"""

from __future__ import annotations


TEXT_STATISTICS_VERSION = (
    "canonical_text_statistics_v1"
)


class TextStatisticsError(
    ValueError
):
    """Raised when text-statistics input is invalid."""


def _require_text(
    value: object,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise TextStatisticsError(
            field_name
            + " must be a string."
        )

    return value


def count_words(
    value: str,
) -> int:
    """Return the canonical whitespace-token word count.

    The input text is not normalized or modified.
    """

    text = _require_text(
        value,
        field_name="value",
    )

    return len(
        text.split()
    )


def count_characters(
    value: str,
) -> int:
    """Return the exact Python character count."""

    text = _require_text(
        value,
        field_name="value",
    )

    return len(
        text
    )


def count_utf8_bytes(
    value: str,
) -> int:
    """Return the exact UTF-8 byte count."""

    text = _require_text(
        value,
        field_name="value",
    )

    return len(
        text.encode(
            "utf-8"
        )
    )


def calculate_text_statistics(
    value: str,
) -> dict[str, int | str]:
    """Return all canonical statistics for one exact text body."""

    text = _require_text(
        value,
        field_name="value",
    )

    return {
        "statistics_version":
            TEXT_STATISTICS_VERSION,

        "word_count":
            count_words(
                text
            ),

        "character_count":
            count_characters(
                text
            ),

        "utf8_byte_count":
            count_utf8_bytes(
                text
            ),
    }
