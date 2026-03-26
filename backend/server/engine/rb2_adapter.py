# backend/server/engine/rb2_adapter.py
from __future__ import annotations
from typing import Any, Dict, Optional

from .extract_rb2 import extract_rb2_contract_from_html, extract_rb2_contract_from_plaintext


def build_rb2_phrase_contexts(
    doc_id: str,
    *,
    html: Optional[str] = None,
    text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Phase 2 adapter:
    - Produces rb2.extract.v1 contract
    - Returns a scanner-facing payload RB2 can iterate.
    NOTE: No scoring, no bucket logic here.
    """
    if html:
        contract = extract_rb2_contract_from_html(doc_id, html)
    else:
        contract = extract_rb2_contract_from_plaintext(doc_id, text or "")

    return {
        "docId": contract["docId"],
        "version": contract["version"],
        "docH1": contract.get("docH1") or {"text": "", "norm": ""},
        "headings": contract.get("headings") or [],
        "paragraphs": contract.get("paragraphs") or [],
        "joinedText": contract.get("joinedText") or "",
    }
