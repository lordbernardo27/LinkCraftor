from __future__ import annotations

import json
import re
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _data_dir() -> Path:
    return Path("backend/server/data")


def _ws_safe(workspace_id: str) -> str:
    s = str(workspace_id or "workspace").strip()
    s = re.sub(r"[^a-zA-Z0-9_\-]+", "_", s)
    if not s.startswith("ws_"):
        s = f"ws_{s}"
    return s[:100]


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json_atomic(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _norm_text(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9\s\-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _upload_phrase_pool_path(workspace_id: str) -> Path:
    ws = _ws_safe(workspace_id)
    return _data_dir() / "phrase_pools" / "upload" / f"upload_phrase_pool_{ws}.json"


def _entity_ownership_path(workspace_id: str) -> Path:
    ws = _ws_safe(workspace_id)
    return _data_dir() / "entity_graph_v2" / f"entity_ownership_{ws}.json"


def _is_entity_candidate(phrase: str) -> bool:
    words = phrase.split()

    if len(words) < 2:
        return False

    if len(words) > 6:
        return False

    weak_starts = {
        "how",
        "what",
        "why",
        "when",
        "where",
        "which",
        "this",
        "that",
        "these",
        "those",
        "during",
        "after",
        "before",
        "with",
        "without",
        "from",
        "into",
    }

    weak_ends = {
        "and",
        "or",
        "of",
        "to",
        "for",
        "with",
        "from",
        "in",
        "on",
        "during",
        "after",
        "before",
    }

    if words[0] in weak_starts:
        return False

    if words[-1] in weak_ends:
        return False

    return True


def build_entity_ownership_v2(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)

    pool_path = _upload_phrase_pool_path(ws)
    pool = _read_json(pool_path, {"workspace_id": ws, "phrases": {}})

    phrases = pool.get("phrases", {})
    if not isinstance(phrases, dict):
        phrases = {}

    entities: Dict[str, Dict[str, Any]] = {}

    for phrase_key, payload in phrases.items():
        if not isinstance(payload, dict):
            continue

        phrase = _norm_text(payload.get("phrase") or phrase_key)

        if not phrase or not _is_entity_candidate(phrase):
            continue

        docs = payload.get("docs", {})
        if not isinstance(docs, dict):
            docs = {}

        examples = payload.get("examples", [])
        if not isinstance(examples, list):
            examples = []

        entity = phrase

        rec = entities.get(entity)
        if not isinstance(rec, dict):
            rec = {
                "entity": entity,
                "source": "derived_from_upload_phrase_pool_v2",
                "docs": {},
                "phrases": [],
                "examples": [],
                "mentions_total": 0,
                "first_seen": payload.get("first_seen") or _now_iso(),
                "last_seen": payload.get("last_seen") or _now_iso(),
            }
            entities[entity] = rec

        if phrase not in rec["phrases"]:
            rec["phrases"].append(phrase)

        for doc_id, count in docs.items():
            did = str(doc_id or "").strip()
            if not did:
                continue

            c = int(count or 0)
            rec["docs"][did] = int(rec["docs"].get(did) or 0) + c
            rec["mentions_total"] = int(rec.get("mentions_total") or 0) + c

        for ex in examples[:3]:
            if isinstance(ex, dict) and len(rec["examples"]) < 5:
                rec["examples"].append(ex)

    output = {
        "workspace_id": ws,
        "type": "entity_ownership_v2",
        "generated_at": _now_iso(),
        "source_file": str(pool_path),
        "source_file_exists": pool_path.exists(),
        "entity_count": len(entities),
        "entities": entities,
        "runtime_effect": "read_only_no_runtime_injection",
        "layer": "1.6.2.4_entity_ownership_v2",
    }

    _write_json_atomic(_entity_ownership_path(ws), output)

    return output

def build_entity_document_mapping_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    ownership = build_entity_ownership_v2(
        workspace_id
    )

    entities = ownership.get(
        "entities",
        {}
    )

    entity_document_map = {}

    for entity_name, rec in entities.items():

        docs = rec.get("docs", {})

        if not isinstance(docs, dict):
            continue

        total_mentions = sum(
            int(v or 0)
            for v in docs.values()
        )

        if total_mentions <= 0:
            continue

        mapped_docs = []

        dominant_document = None
        dominant_mentions = 0

        for doc_id, mentions in docs.items():

            m = int(mentions or 0)

            ownership_strength = round(
                m / total_mentions,
                4,
            )

            mapped_docs.append({
                "document_id": doc_id,
                "mentions": m,
                "ownership_strength":
                    ownership_strength,
            })

            if m > dominant_mentions:
                dominant_mentions = m
                dominant_document = doc_id

        mapped_docs.sort(
            key=lambda x: x.get(
                "mentions",
                0,
            ),
            reverse=True,
        )

        entity_document_map[entity_name] = {
            "entity": entity_name,

            "documents":
                mapped_docs,

            "documents_count":
                len(mapped_docs),

            "total_mentions":
                total_mentions,

            "dominant_document":
                dominant_document,

            "dominant_mentions":
                dominant_mentions,

            "entity_scope":
                (
                    "cross_document"
                    if len(mapped_docs) > 1
                    else "single_document"
                ),
        }

    output = {
        "workspace_id":
            ownership["workspace_id"],

        "generated_at":
            _now_iso(),

        "entity_count":
            len(entity_document_map),

        "entity_document_map":
            entity_document_map,

        "runtime_effect":
            "read_only_no_runtime_injection",

        "layer":
            "1.6.2.5_entity_document_mapping_v2",
    }

    return output


def build_entity_phrase_support_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    mapping = build_entity_document_mapping_v2(
        workspace_id
    )

    entity_map = mapping.get(
        "entity_document_map",
        {}
    )

    phrase_support_map = {}

    for entity_name, rec in entity_map.items():

        ownership = build_entity_ownership_v2(
            workspace_id
        )

        entities = ownership.get(
            "entities",
            {}
        )

        entity_rec = entities.get(
            entity_name,
            {}
        )

        phrases = entity_rec.get(
            "phrases",
            []
        )

        if not isinstance(
            phrases,
            list,
        ):
            phrases = []

        normalized = []

        seen = set()

        for phrase in phrases:

            p = _norm_text(phrase)

            if not p:
                continue

            if p in seen:
                continue

            seen.add(p)

            normalized.append({
                "phrase": p,
                "phrase_length":
                    len(p.split()),
            })

        normalized.sort(
            key=lambda x: (
                x["phrase_length"],
                x["phrase"],
            )
        )

        phrase_support_map[
            entity_name
        ] = {

            "entity":
                entity_name,

            "supporting_phrases":
                normalized,

            "supporting_phrase_count":
                len(normalized),

            "documents_count":
                rec.get(
                    "documents_count",
                    0,
                ),

            "entity_scope":
                rec.get(
                    "entity_scope",
                    "unknown",
                ),
        }

    output = {

        "workspace_id":
            mapping["workspace_id"],

        "generated_at":
            _now_iso(),

        "entity_count":
            len(phrase_support_map),

        "entity_phrase_support":
            phrase_support_map,

        "runtime_effect":
            "read_only_no_runtime_injection",

        "layer":
            "1.6.2.6_entity_phrase_support_v2",
    }

    return output


def build_cross_document_entity_overlap_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    mapping = build_entity_document_mapping_v2(
        workspace_id
    )

    entity_map = mapping.get(
        "entity_document_map",
        {}
    )

    document_entities = {}

    for entity_name, rec in entity_map.items():

        docs = rec.get(
            "documents",
            []
        )

        for d in docs:

            doc_id = str(
                d.get(
                    "document_id",
                    ""
                )
            ).strip()

            if not doc_id:
                continue

            document_entities.setdefault(
                doc_id,
                set(),
            ).add(entity_name)

    overlap_map = {}

    doc_ids = sorted(
        document_entities.keys()
    )

    for i, doc_a in enumerate(doc_ids):

        overlap_map.setdefault(
            doc_a,
            {}
        )

        ents_a = document_entities.get(
            doc_a,
            set(),
        )

        for doc_b in doc_ids[i + 1:]:

            ents_b = document_entities.get(
                doc_b,
                set(),
            )

            shared = sorted(
                ents_a.intersection(
                    ents_b
                )
            )

            if not shared:
                continue

            union_total = len(
                ents_a.union(
                    ents_b
                )
            )

            relationship_strength = 0.0

            if union_total > 0:
                relationship_strength = round(
                    len(shared) / union_total,
                    4,
                )

            rel = {
                "shared_entities":
                    shared,

                "shared_count":
                    len(shared),

                "relationship_strength":
                    relationship_strength,
            }

            overlap_map[
                doc_a
            ][doc_b] = rel

            overlap_map.setdefault(
                doc_b,
                {}
            )[doc_a] = rel

    output = {

        "workspace_id":
            mapping["workspace_id"],

        "generated_at":
            _now_iso(),

        "document_count":
            len(doc_ids),

        "cross_document_overlap":
            overlap_map,

        "runtime_effect":
            "read_only_no_runtime_injection",

        "layer":
            "1.6.2.7_cross_document_entity_overlap_v2",
    }

    return output


def build_entity_relationship_summary_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    ownership = build_entity_ownership_v2(
        workspace_id
    )

    overlap = build_cross_document_entity_overlap_v2(
        workspace_id
    )

    entities = ownership.get(
        "entities",
        {}
    )

    overlap_map = overlap.get(
        "cross_document_overlap",
        {}
    )

    top_entities = []

    for entity_name, rec in entities.items():

        docs = rec.get(
            "docs",
            {}
        )

        total_mentions = sum(
            int(v or 0)
            for v in docs.values()
        )

        top_entities.append({
            "entity":
                entity_name,

            "documents_count":
                len(docs),

            "total_mentions":
                total_mentions,
        })

    top_entities.sort(
        key=lambda x: (
            x["documents_count"],
            x["total_mentions"],
        ),
        reverse=True,
    )

    strongest_relationships = []

    seen_pairs = set()

    for doc_a, rels in overlap_map.items():

        for doc_b, rel in rels.items():

            pair = tuple(
                sorted([doc_a, doc_b])
            )

            if pair in seen_pairs:
                continue

            seen_pairs.add(pair)

            strongest_relationships.append({

                "doc_a":
                    doc_a,

                "doc_b":
                    doc_b,

                "shared_count":
                    rel.get(
                        "shared_count",
                        0,
                    ),

                "relationship_strength":
                    rel.get(
                        "relationship_strength",
                        0.0,
                    ),

                "top_shared_entities":
                    rel.get(
                        "shared_entities",
                        []
                    )[:10],
            })

    strongest_relationships.sort(
        key=lambda x: (
            x["relationship_strength"],
            x["shared_count"],
        ),
        reverse=True,
    )

    output = {

        "workspace_id":
            ownership["workspace_id"],

        "generated_at":
            _now_iso(),

        "top_workspace_entities":
            top_entities[:50],

        "strongest_document_relationships":
            strongest_relationships[:50],

        "workspace_entity_count":
            len(entities),

        "workspace_document_count":
            overlap.get(
                "document_count",
                0,
            ),

        "runtime_effect":
            "read_only_no_runtime_injection",

        "layer":
            "1.6.2.8_entity_relationship_summary_v2",
    }

    return output

