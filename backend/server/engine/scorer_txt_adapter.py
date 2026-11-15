"""Conservative TXT adapter for the LinkCraftor Original Scorer.

Plain text has no native hyperlink or verified section structure.
Content is preserved, but automatic placement is not authorized.
"""

from __future__ import annotations

import hashlib
import re

from backend.server.engine.scorer_document_contract import (
    SCORER_DOCUMENT_CONTRACT_VERSION,
    validate_scorer_document_contract,
)


class ScorerTxtAdapterError(ValueError):
    pass


def adapt_txt_for_scorer(
    *,
    text: str,
    workspace_id: str,
    document_id: str,
    content_version: str,
):
    if not isinstance(text, str) or not text.strip():
        raise ScorerTxtAdapterError(
            "nonempty TXT source required"
        )

    # Initial restricted profile: exact LF paragraph boundaries.
    # No silent normalization or fabricated source positions.
    if (
        "\r" in text
        or "\t" in text
        or "\x00" in text
        or text != text.strip()
    ):
        raise ScorerTxtAdapterError(
            "unsupported TXT whitespace or control characters"
        )

    if any(
        ord(character) < 32 and character != "\n"
        for character in text
    ):
        raise ScorerTxtAdapterError(
            "unsupported TXT control character"
        )

    if "\n\n\n" in text:
        raise ScorerTxtAdapterError(
            "ambiguous TXT paragraph separators"
        )

    blocks = text.split("\n\n")

    if any(not block.strip() for block in blocks):
        raise ScorerTxtAdapterError(
            "empty TXT paragraph block"
        )

    regions = []
    offset = 0

    for index, block in enumerate(blocks):
        # Keep paragraph content exact, including internal LF.
        # Without a trusted structural manifest, none of the
        # paragraphs can be declared safe editorial-body prose.
        if block != block.strip():
            raise ScorerTxtAdapterError(
                "unsupported paragraph boundary whitespace"
            )

        regions.append({
            "region_id": f"txt_block_{index}",
            "region_type": "unknown",
            "eligible_for_linking": False,
            "source_mapping_verified": False,
            "source_node_id": f"txt_block_{index}",
            "section_id": "unverified",
            "text": block,
            "char_start": offset,
            "char_end": offset + len(block),
            "word_count": len(block.split()),
            "exclusion_reason": "unverified_txt_structure",
        })

        offset += len(block) + 2

    document = {
        "schema_version": SCORER_DOCUMENT_CONTRACT_VERSION,
        "workspace_id": workspace_id,
        "document_id": document_id,
        "content_version": content_version,
        "source_format": "txt",
        "canonical_text": text,
        "content_sha256": hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest(),
        "source_txt_sha256": hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest(),
        "structure_complete": True,
        "regions": regions,
        "eligible_body_word_count": 0,
        "protected_spans_complete": True,
        "protected_spans": [],
        "native_hyperlink_inventory_complete": True,
        "source_mapping_scope": "exact_txt_text",
        "original_source_insertion_verified": False,
        "placement_eligibility_status": "blocked_unverified_structure",
        "source_adapter": "scorer_txt_adapter_i2_d1",
    }

    # This is structural inventory completeness, not
    # certification that any block is editorial-body prose.
    return validate_scorer_document_contract(document)
