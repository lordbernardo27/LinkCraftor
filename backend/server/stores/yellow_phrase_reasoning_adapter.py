from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List

from backend.server.stores.yellow_semantic_phrase_registry import (
    transition_yellow_phrase_state_v1,
)

from backend.server.stores import semantic_linking_reasoning_engine
from backend.server.stores import semantic_confidence_engine


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _call_existing_engine_safely_v1(
    fn: Callable[..., Any],
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Adapter-safe call wrapper.

    This does not replace the existing reasoning engine.
    It only attempts to call existing reasoning functions using compatible arguments.
    """

    signature = inspect.signature(fn)
    params = signature.parameters

    kwargs = {}

    candidate_values = {
        "payload": payload,
        "input_payload": payload,
        "reasoning_payload": payload,
        "phrase_payload": payload,
        "workspace_id": payload.get("workspace_id"),
        "doc_id": payload.get("document_id"),
        "document_id": payload.get("document_id"),
        "phrase": payload.get("normalized_text"),
        "text": payload.get("normalized_text"),
        "anchor": payload.get("normalized_text"),
        "source_text": payload.get("normalized_text"),
        "context": payload.get("surrounding_context", {}),
    }

    for name, param in params.items():
        if name in candidate_values:
            kwargs[name] = candidate_values[name]

    try:
        result = fn(**kwargs)
        return {
            "called": True,
            "function": fn.__name__,
            "module": fn.__module__,
            "signature": str(signature),
            "kwargs_used": sorted(kwargs.keys()),
            "result": result,
            "error": None,
        }
    except TypeError as exc:
        return {
            "called": False,
            "function": fn.__name__,
            "module": fn.__module__,
            "signature": str(signature),
            "kwargs_used": sorted(kwargs.keys()),
            "result": None,
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "called": False,
            "function": fn.__name__,
            "module": fn.__module__,
            "signature": str(signature),
            "kwargs_used": sorted(kwargs.keys()),
            "result": None,
            "error": str(exc),
        }


def build_yellow_phrase_reasoning_payload_v1(
    yellow_phrase: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "workspace_id": yellow_phrase.get("workspace_id"),
        "document_id": yellow_phrase.get("document_id"),
        "phrase_id": yellow_phrase.get("phrase_id"),
        "surface_text": yellow_phrase.get("surface_text"),
        "normalized_text": yellow_phrase.get("normalized_text"),
        "editor_location": yellow_phrase.get("editor_location", {}),
        "surrounding_context": yellow_phrase.get("surrounding_context", {}),
        "semantic_identity": yellow_phrase.get("semantic_identity", {}),
        "processing_state": yellow_phrase.get("processing_state", {}),
        "resolver_lane": yellow_phrase.get("resolver_lane"),
    }


def adapt_yellow_phrase_to_existing_reasoning_v1(
    yellow_phrase: Dict[str, Any],
) -> Dict[str, Any]:
    working_phrase = transition_yellow_phrase_state_v1(
        yellow_phrase,
        "reasoning_pending",
        source="yellow_phrase_reasoning_adapter",
        note="Yellow phrase sent to existing semantic reasoning engines.",
    )

    payload = build_yellow_phrase_reasoning_payload_v1(working_phrase)

    existing_calls = []

    # Existing semantic linking reasoning engine.
    if hasattr(semantic_linking_reasoning_engine, "build_semantic_linking_reasoning_v1"):
        existing_calls.append(
            _call_existing_engine_safely_v1(
                semantic_linking_reasoning_engine.build_semantic_linking_reasoning_v1,
                payload,
            )
        )

    # Existing runtime semantic reasoning output from semantic confidence engine.
    if hasattr(semantic_confidence_engine, "produce_runtime_semantic_reasoning_output_v1"):
        existing_calls.append(
            _call_existing_engine_safely_v1(
                semantic_confidence_engine.produce_runtime_semantic_reasoning_output_v1,
                payload,
            )
        )

    successful_calls = [item for item in existing_calls if item.get("called")]

    adapter_result = {
        "adapter_schema_version": "yellow_phrase_reasoning_adapter_v1",
        "adapter_name": "Yellow Phrase Reasoning Adapter",
        "created_at": _now_iso(),
        "purpose": (
            "Connect yellow semantic phrase objects to the existing semantic reasoning engines. "
            "This adapter does not replace or duplicate the reasoning engine."
        ),
        "input_payload": payload,
        "existing_reasoning_calls": existing_calls,
        "successful_call_count": len(successful_calls),
        "failed_call_count": len(existing_calls) - len(successful_calls),
        "uses_existing_reasoning_engine": True,
        "creates_new_reasoning_engine": False,
        "boundary_rule": (
            "Yellow Phrase Reasoning Adapter only formats yellow phrase input for existing reasoning engines "
            "and attaches their output. It does not create a new reasoning engine, query target URLs, choose targets, "
            "create highlights, write memory, or generate explanations."
        ),
    }

    working_phrase["semantic_reasoning_adapter"] = adapter_result

    if successful_calls:
        working_phrase = transition_yellow_phrase_state_v1(
            working_phrase,
            "reasoned",
            source="yellow_phrase_reasoning_adapter",
            note="Existing semantic reasoning engine returned output.",
        )
        working_phrase["routing"]["requires_target_discovery"] = True
    else:
        # Do not reject the phrase yet. It means adapter wiring needs exact engine signature alignment.
        working_phrase = transition_yellow_phrase_state_v1(
            working_phrase,
            "reasoning_pending",
            source="yellow_phrase_reasoning_adapter",
            note="Existing reasoning engine call was attempted but no compatible call completed.",
        )
        working_phrase["routing"]["requires_target_discovery"] = False

    return working_phrase


def adapt_yellow_phrase_registry_to_existing_reasoning_v1(
    phrase_registry: Dict[str, Any],
) -> Dict[str, Any]:
    adapted_phrases = [
        adapt_yellow_phrase_to_existing_reasoning_v1(phrase)
        for phrase in phrase_registry.get("yellow_semantic_phrases", [])
    ]

    reasoned_count = sum(
        1
        for phrase in adapted_phrases
        if phrase.get("processing_state", {}).get("current_state") == "reasoned"
    )

    pending_count = sum(
        1
        for phrase in adapted_phrases
        if phrase.get("processing_state", {}).get("current_state") == "reasoning_pending"
    )

    return {
        "schema_version": "yellow_phrase_reasoning_adapter_model_v1",
        "phase": "semantic_linking_execution.step_2",
        "patch": "step_2_adapter_A",
        "name": "Yellow Phrase Reasoning Adapter",
        "created_at": _now_iso(),
        "workspace_id": phrase_registry.get("workspace_id"),
        "document": phrase_registry.get("document", {}),
        "source_registry": {
            "schema_version": phrase_registry.get("schema_version"),
            "phase": phrase_registry.get("phase"),
            "patch": phrase_registry.get("patch"),
        },
        "adapted_yellow_phrases": adapted_phrases,
        "metadata": {
            "input_phrase_count": len(phrase_registry.get("yellow_semantic_phrases", [])),
            "adapted_phrase_count": len(adapted_phrases),
            "reasoned_phrase_count": reasoned_count,
            "reasoning_pending_count": pending_count,
            "uses_existing_reasoning_engine": True,
            "creates_new_reasoning_engine": False,
        },
        "boundary_rule": (
            "This adapter connects yellow phrases to existing semantic reasoning engines only. "
            "It does not duplicate reasoning logic, query Active Target Set, perform resolving, create highlights, "
            "write memory, or generate explanations."
        ),
    }


def save_yellow_phrase_reasoning_adapter_v1(
    phrase_registry: Dict[str, Any],
    output_path: str | Path,
) -> Dict[str, Any]:
    model = adapt_yellow_phrase_registry_to_existing_reasoning_v1(phrase_registry)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(model, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return model


def explain_yellow_phrase_reasoning_adapter_v1() -> Dict[str, Any]:
    return {
        "step": "Step 2",
        "patch": "step_2_adapter_A",
        "name": "Yellow Phrase Reasoning Adapter",
        "purpose": "Bridge yellow semantic phrase objects into the existing semantic reasoning engines.",
        "input": "Yellow Semantic Phrase Registry Step 1D",
        "output": "Yellow phrases enriched with semantic_reasoning_adapter output",
        "uses_existing_files": [
            "backend/server/stores/semantic_linking_reasoning_engine.py",
            "backend/server/stores/semantic_confidence_engine.py",
        ],
        "does": [
            "receives yellow phrase objects",
            "builds reasoning payload",
            "calls existing semantic reasoning functions when signature-compatible",
            "attaches existing reasoning output under semantic_reasoning_adapter",
            "moves phrase lifecycle forward when existing reasoning succeeds",
            "keeps target discovery separate",
        ],
        "does_not": [
            "create a new reasoning engine",
            "replace semantic_linking_reasoning_engine.py",
            "query Active Target Set",
            "choose target URLs",
            "perform yellow resolving",
            "perform blue resolving",
            "create final highlights",
            "write memory",
            "generate explanations",
        ],
    }
