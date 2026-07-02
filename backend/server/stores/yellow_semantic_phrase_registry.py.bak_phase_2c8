from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROCESSING_STATES = [
    "detected",
    "reasoning_pending",
    "reasoned",
    "target_discovery_pending",
    "target_candidates_found",
    "resolver_pending",
    "resolved",
    "rejected",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:12]}"


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]


def _known_semantic_terms() -> List[str]:
    return sorted({
        "hypertension",
        "high blood pressure",
        "blood pressure",
        "blood pressure monitoring",
        "gestational hypertension",
        "preeclampsia",
        "morning sickness",
        "nausea",
        "swelling",
        "headaches",
    }, key=len, reverse=True)


def _candidate_phrase_spans(sentence: str) -> List[Dict[str, Any]]:
    """
    Detect semantic phrase spans and keep longest non-overlapping matches.
    Example:
    - Keep "blood pressure monitoring"
    - Suppress embedded "blood pressure" inside it
    """
    lowered = _normalize(sentence)
    raw_spans = []

    for term in _known_semantic_terms():
        pattern = r"\b" + re.escape(term) + r"\b"

        for match in re.finditer(pattern, lowered):
            raw_spans.append({
                "surface_text": term,
                "normalized_text": term,
                "start_offset": match.start(),
                "end_offset": match.end(),
                "length": match.end() - match.start(),
            })

    raw_spans = sorted(
        raw_spans,
        key=lambda item: (
            item["length"],
            -item["start_offset"],
        ),
        reverse=True,
    )

    selected = []

    for span in raw_spans:
        overlaps = any(
            not (
                span["end_offset"] <= existing["start_offset"]
                or span["start_offset"] >= existing["end_offset"]
            )
            for existing in selected
        )

        if not overlaps:
            selected.append(span)

    return sorted(selected, key=lambda item: item["start_offset"])


def build_yellow_semantic_phrase_registry_v1(
    editor_document: Dict[str, Any],
) -> Dict[str, Any]:
    document_id = editor_document.get("document_id")
    workspace_id = editor_document.get("workspace_id")
    title = editor_document.get("title")
    text = editor_document.get("text", "")

    registry_items = []
    sentence_list = _sentences(text)

    for sentence_index, sentence in enumerate(sentence_list):
        spans = _candidate_phrase_spans(sentence)

        for span in spans:
            normalized_phrase = span["normalized_text"]
            start_offset = span["start_offset"]
            end_offset = span["end_offset"]

            phrase_id = _stable_id(
                "yellow_phrase",
                workspace_id,
                document_id,
                normalized_phrase,
                sentence_index,
                start_offset,
                end_offset,
            )

            registry_items.append({
                "phrase_id": phrase_id,
                "workspace_id": workspace_id,
                "document_id": document_id,
                "surface_text": span["surface_text"],
                "normalized_text": normalized_phrase,
                "highlight_type": "yellow_candidate",
                "resolver_lane": "semantic_yellow",
                "status": "detected",
                "processing_state": {
                    "current_state": "detected",
                    "allowed_states": PROCESSING_STATES,
                    "history": [
                        {
                            "state": "detected",
                            "created_at": _now_iso(),
                            "source": "yellow_semantic_phrase_registry",
                            "note": "Semantic phrase candidate detected in editor."
                        }
                    ],
                    "next_expected_engine": "semantic_reasoning_engine",
                },
                "editor_location": {
                    "sentence_index": sentence_index,
                    "start_offset": start_offset,
                    "end_offset": end_offset,
                },
                "surrounding_context": {
                    "sentence": sentence,
                    "document_title": title,
                },
                "span_policy": {
                    "policy": "longest_non_overlapping_semantic_span",
                    "embedded_shorter_phrases_suppressed": True,
                },
                "semantic_identity": {
                    "identity_status": "pending",
                    "semantic_object_id": None,
                    "canonical_concept": None,
                    "identity_confidence": None,
                    "identity_source": None,
                    "semantic_bridge": None,
                },
                "routing": {
                    "send_to_reasoning_engine": True,
                    "send_to_blue_resolver": False,
                    "send_to_yellow_resolver": False,
                    "requires_target_discovery": False,
                    "requires_explainability": False,
                },
                "boundary_rule": (
                    "Yellow Semantic Phrase Registry captures semantic candidate phrases from the editor using longest-span selection. "
                    "It does not resolve links, choose targets, create blue highlights, create final yellow highlights, "
                    "write memory, or generate explanations."
                ),
            })

    return {
        "schema_version": "yellow_semantic_phrase_registry_v1",
        "phase": "semantic_linking_execution.step_1",
        "patch": "step_1D",
        "name": "Yellow Semantic Phrase Registry",
        "created_at": _now_iso(),
        "workspace_id": workspace_id,
        "document": {
            "document_id": document_id,
            "title": title,
        },
        "yellow_semantic_phrases": registry_items,
        "metadata": {
            "yellow_phrase_count": len(registry_items),
            "sentence_count": len(sentence_list),
            "span_policy": "longest_non_overlapping_semantic_span",
            "processing_lifecycle_enabled": True,
        },
        "boundary_rule": (
            "This registry captures yellow semantic phrase candidates for the Reasoning Engine. "
            "It does not perform semantic reasoning, target discovery, resolving, explainability, or link insertion."
        ),
    }


def transition_yellow_phrase_state_v1(
    phrase: Dict[str, Any],
    new_state: str,
    *,
    source: str,
    note: str = "",
) -> Dict[str, Any]:
    if new_state not in PROCESSING_STATES:
        raise ValueError(f"Invalid yellow phrase processing state: {new_state}")

    updated = dict(phrase)
    processing_state = dict(updated.get("processing_state", {}))

    history = list(processing_state.get("history", []))
    history.append({
        "state": new_state,
        "created_at": _now_iso(),
        "source": source,
        "note": note,
    })

    processing_state["current_state"] = new_state
    processing_state["history"] = history

    if new_state == "reasoning_pending":
        processing_state["next_expected_engine"] = "semantic_reasoning_engine"
    elif new_state == "reasoned":
        processing_state["next_expected_engine"] = "semantic_target_discovery"
    elif new_state == "target_candidates_found":
        processing_state["next_expected_engine"] = "yellow_semantic_resolver"
    elif new_state == "resolved":
        processing_state["next_expected_engine"] = "explainability"
    elif new_state == "rejected":
        processing_state["next_expected_engine"] = None

    updated["processing_state"] = processing_state
    updated["status"] = new_state

    return updated


def save_yellow_semantic_phrase_registry_v1(
    editor_document: Dict[str, Any],
    output_path: str | Path,
) -> Dict[str, Any]:
    registry = build_yellow_semantic_phrase_registry_v1(editor_document)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    return registry


def explain_yellow_semantic_phrase_registry_v1() -> Dict[str, Any]:
    return {
        "name": "Yellow Semantic Phrase Registry",
        "patch": "step_1D",
        "purpose": "Capture semantic candidate phrases from the editor before reasoning, target discovery, and yellow resolving.",
        "input": "Editor document text",
        "output": "Yellow semantic phrase registry",
        "does": [
            "detects yellow semantic candidate phrases",
            "uses longest non-overlapping semantic span selection",
            "suppresses embedded shorter semantic phrases",
            "stores phrase_id",
            "stores surface_text",
            "stores normalized_text",
            "stores editor location",
            "stores surrounding sentence context",
            "marks phrase status as detected",
            "stores processing lifecycle state",
            "stores pending semantic identity for Reasoning Engine",
            "routes phrase to the Reasoning Engine",
            "keeps yellow semantic candidates separate from blue direct-link candidates",
        ],
        "does_not": [
            "perform blue internal resolving",
            "perform yellow semantic resolving",
            "choose target URLs",
            "query active target sets",
            "create final highlights",
            "write memory",
            "generate explanations",
        ],
    }
