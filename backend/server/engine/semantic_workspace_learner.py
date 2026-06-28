from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SEMANTIC_SOURCES: List[str] = [
    "core_knowledge",
    "workspace_synonyms",
    "topic_clusters",
    "section_clusters",
    "page_index",
    "uploaded_documents",
    "article_body",
    "external_resolver",
    "feedback_memory",
]


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def _semantic_dir() -> Path:
    path = _data_dir() / "semantic"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _workspace_map_path(workspace_id: str) -> Path:
    ws = str(workspace_id or "default").strip() or "default"
    return _semantic_dir() / f"semantic_map_v2_{ws}.json"


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def load_semantic_map(workspace_id: str) -> Dict[str, Any]:
    path = _workspace_map_path(workspace_id)

    if path.exists():
        try:
            obj = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass

    now = datetime.now(timezone.utc).isoformat()

    return {
        "version": "semantic_map_v2",
        "workspace_id": workspace_id,
        "created_at_utc": now,
        "updated_at_utc": now,
        "workspace_synonym_groups": [],
        "page_semantic_index": [],
        "article_content_index": [],
        "uploaded_document_index": [],
        "external_resolver_index": {
            "manual": [],
            "automatic": []
        },
        "feedback_memory": {
            "accepted_pairs": [],
            "rejected_pairs": [],
            "blocked_pairs": []
        },
        "concept_graph": [],
        "semantic_learner": {
            "version": "semantic_workspace_learner_v1",
            "last_rebuilt_at_utc": "",
            "sources": SEMANTIC_SOURCES,
            "concept_count": 0,
            "evidence_count": 0
        }
    }


def save_semantic_map(workspace_id: str, data: Dict[str, Any]) -> Path:
    path = _workspace_map_path(workspace_id)
    data["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path




def _read_json(path: Path, fallback: Any = None) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return fallback


def _core_knowledge_path() -> Path:
    return _semantic_dir() / "semantic_core_knowledge.json"


def load_core_knowledge_evidence(workspace_id: str) -> List[Dict[str, Any]]:
    obj = _read_json(_core_knowledge_path(), {})
    groups = obj.get("synonym_groups") if isinstance(obj, dict) else []

    evidence: List[Dict[str, Any]] = []

    for group in groups or []:
        if not isinstance(group, list):
            continue

        cleaned = [_norm(x) for x in group if _norm(x)]
        if len(cleaned) < 2:
            continue

        canonical = cleaned[0]

        for related in cleaned[1:]:
            evidence.append({
                "concept": canonical,
                "related_phrase": related,
                "relation_type": "synonym",
                "source": "core_knowledge",
                "confidence": 0.95,
                "evidence": {
                    "group": cleaned
                }
            })

    return evidence


def load_workspace_synonym_evidence(workspace_id: str) -> List[Dict[str, Any]]:
    obj = load_semantic_map(workspace_id)
    groups = obj.get("workspace_synonym_groups") or []

    evidence: List[Dict[str, Any]] = []

    for group in groups:
        if not isinstance(group, list):
            continue

        cleaned = [_norm(x) for x in group if _norm(x)]
        if len(cleaned) < 2:
            continue

        canonical = cleaned[0]

        for related in cleaned[1:]:
            evidence.append({
                "concept": canonical,
                "related_phrase": related,
                "relation_type": "synonym",
                "source": "workspace_synonyms",
                "confidence": 0.94,
                "evidence": {
                    "group": cleaned
                }
            })

    return evidence


def load_page_index_evidence(workspace_id: str) -> List[Dict[str, Any]]:
    obj = load_semantic_map(workspace_id)
    pages = obj.get("page_semantic_index") or []

    evidence: List[Dict[str, Any]] = []

    for page in pages:
        if not isinstance(page, dict):
            continue

        url = page.get("url") or ""
        title = _norm(page.get("title") or page.get("h1") or "")

        if not title:
            continue

        terms = page.get("surface_terms") or []
        phrases = page.get("important_phrases") or []

        evidence.append({
            "concept": title,
            "related_phrase": title,
            "relation_type": "page_topic",
            "source": "page_index",
            "confidence": 0.85,
            "evidence": {
                "url": url,
                "title": page.get("title") or page.get("h1") or "",
                "surface_terms": terms[:50] if isinstance(terms, list) else [],
                "important_phrases": phrases[:50] if isinstance(phrases, list) else []
            }
        })

    return evidence




def _workspace_safe_names(workspace_id: str) -> List[str]:
    ws = str(workspace_id or "default").strip() or "default"
    return [
        ws,
        ws.replace(".", "_"),
        ws.replace("-", "_"),
    ]


def _load_upload_json_candidates(workspace_id: str) -> List[Path]:
    data = _data_dir()
    names = _workspace_safe_names(workspace_id)

    candidates: List[Path] = []

    for ws in names:
        candidates.extend([
            data / f"upload_phrase_index_{ws}.json",
            data / f"upload_entity_graph_{ws}.json",
            data / f"upload_entity_map_{ws}.json",
            data / f"upload_struct_{ws}.json",
        ])

    phrase_pool_dir = data / "phrase_pools" / "upload"
    if phrase_pool_dir.exists():
        for ws in names:
            candidates.extend(sorted(phrase_pool_dir.glob(f"upload_phrase_pool_{ws}*.json")))

    seen = set()
    out: List[Path] = []

    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        if path.exists() and path.is_file():
            out.append(path)

    return out


def _walk_strings(obj: Any, limit: int = 2000) -> List[str]:
    found: List[str] = []

    def walk(x: Any) -> None:
        if len(found) >= limit:
            return

        if isinstance(x, str):
            value = _norm(x)
            if 3 <= len(value) <= 120:
                found.append(value)
            return

        if isinstance(x, dict):
            for key, value in x.items():
                if str(key).lower() in {
                    "phrase", "anchor", "text", "title", "term", "entity",
                    "label", "name", "canonical", "canonical_phrase",
                    "keyword", "topic", "heading"
                }:
                    walk(value)
                elif isinstance(value, (dict, list)):
                    walk(value)
            return

        if isinstance(x, list):
            for item in x:
                walk(item)

    walk(obj)

    seen = set()
    unique = []

    for item in found:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    return unique[:limit]




_UPLOAD_NOISE_TERMS = {
    "guard_pass",
    "debug",
    "test",
    "tmp",
    "none",
    "null",
    "true",
    "false",
    "unknown",
    "resolved",
    "unresolved",
    "default",
    "workspace",
    "workspace_id",
    "source",
    "target",
    "score",
    "confidence",
}


def _looks_like_noise_phrase(value: Any) -> bool:
    text = _norm(value)

    if not text:
        return True

    if text in _UPLOAD_NOISE_TERMS:
        return True

    # paragraph/sentence IDs like p1_s2
    if re.fullmatch(r"p\d+_s\d+", text):
        return True

    # hashes / ids
    if re.fullmatch(r"[a-f0-9]{16,}", text):
        return True

    # uuid-like chunks
    if re.fullmatch(r"[a-f0-9]{8,}[-_][a-f0-9]{4,}.*", text):
        return True

    # mostly punctuation / underscores / digits
    letters = re.findall(r"[a-z]", text)
    if len(letters) < 3:
        return True

    # single technical token with underscore
    if " " not in text and "_" in text:
        return True

    # too URL/file-like
    if any(x in text for x in [".json", ".py", ".html", ".docx", "\\", "/"]):
        return True

    return False




def _uploaded_phrase_quality_score(value: Any) -> float:
    text = _norm(value)
    words = re.findall(r"[a-z0-9]+", text)

    if not words:
        return 0.0

    score = 0.0

    if len(words) >= 2:
        score += 0.45

    if len(words) >= 3:
        score += 0.20

    if 8 <= len(text) <= 80:
        score += 0.20

    if any(len(w) >= 7 for w in words):
        score += 0.10

    if len(words) == 1:
        score -= 0.30

    if text.endswith(("tion", "ity", "ment", "ness")) and len(words) == 1:
        score -= 0.15

    return round(max(0.0, min(1.0, score)), 4)


def _passes_uploaded_quality_filter(value: Any) -> bool:
    text = _norm(value)

    if _looks_like_noise_phrase(text):
        return False

    words = re.findall(r"[a-z0-9]+", text)

    if len(words) >= 2:
        return _uploaded_phrase_quality_score(text) >= 0.45

    # Keep single-token terms only if strong enough.
    # Later entity/type support can promote more single-token concepts.
    return _uploaded_phrase_quality_score(text) >= 0.65


def load_uploaded_document_evidence(workspace_id: str) -> List[Dict[str, Any]]:
    evidence: List[Dict[str, Any]] = []

    files = _load_upload_json_candidates(workspace_id)

    for path in files:
        obj = _read_json(path, None)
        if obj is None:
            continue

        phrases = _walk_strings(obj, limit=1500)

        for phrase in phrases:
            if not phrase or not _passes_uploaded_quality_filter(phrase):
                continue

            quality = _uploaded_phrase_quality_score(phrase)

            evidence.append({
                "concept": phrase,
                "related_phrase": phrase,
                "relation_type": "uploaded_document_phrase",
                "source": "uploaded_documents",
                "confidence": round(0.70 + (quality * 0.10), 4),
                "evidence": {
                    "file": str(path),
                    "kind": path.name,
                    "quality_score": quality,
                }
            })

    return evidence




def _article_body_index_path(workspace_id: str) -> Path:
    ws = str(workspace_id or "default").strip() or "default"
    return _semantic_dir() / f"article_body_index_{ws}.json"




_SITEWIDE_ARTICLE_NOISE = {
    "whattoexpect com",
    "what to expect",
    "expect digital",
    "amazon prime day",
    "app amazon prime day",
    "registry product",
    "family baby names registry product",
    "topics top baby names",
    "baby names topics",
    "top baby names",
    "pregnant topics",
    "community groups",
    "expect community",
    "advertising policy",
    "editorial policy",
}


def _is_sitewide_article_noise(value: Any) -> bool:
    text = _norm(value)

    if not text:
        return True

    if text in _SITEWIDE_ARTICLE_NOISE:
        return True

    html_residue_terms = {
        "nbsp", "amp", "copy", "raquo", "laquo", "quot",
        "mdash", "ndash", "rsquo", "lsquo", "rdquo", "ldquo",
    }

    parts = set(text.split())

    if parts & html_residue_terms:
        return True

    if "whattoexpect com" in text:
        return True

    if "amazon prime day" in text:
        return True

    if "registry product" in text:
        return True

    if text.endswith("topics") and "baby names" in text:
        return True

    if text.startswith("topics ") and "baby names" in text:
        return True

    if text in {"about what to expect", "about heidi murkoff"}:
        return True

    return False


def load_article_body_evidence(workspace_id: str) -> List[Dict[str, Any]]:
    obj = _read_json(_article_body_index_path(workspace_id), {})
    articles = obj.get("articles") if isinstance(obj, dict) else []

    evidence: List[Dict[str, Any]] = []

    if not isinstance(articles, list):
        return evidence

    for article in articles:
        if not isinstance(article, dict):
            continue

        status = str(article.get("status") or "").strip()

        if status != "parsed":
            continue

        url = article.get("url") or ""
        title = _norm(article.get("title") or article.get("h1") or "")
        headings = article.get("headings") if isinstance(article.get("headings"), list) else []
        key_phrases = article.get("key_phrases") if isinstance(article.get("key_phrases"), list) else []
        entities = article.get("entities") if isinstance(article.get("entities"), list) else []
        related_concepts = article.get("related_concepts") if isinstance(article.get("related_concepts"), list) else []

        if title and not _is_sitewide_article_noise(title):
            evidence.append({
                "concept": title,
                "related_phrase": title,
                "relation_type": "article_topic",
                "source": "article_body",
                "confidence": 0.75,
                "evidence": {
                    "url": url,
                    "title": article.get("title") or article.get("h1") or "",
                }
            })

        for phrase in key_phrases[:150]:
            phrase = _norm(phrase)
            if not phrase or _looks_like_noise_phrase(phrase) or _is_sitewide_article_noise(phrase):
                continue

            evidence.append({
                "concept": phrase,
                "related_phrase": phrase,
                "relation_type": "article_key_phrase",
                "source": "article_body",
                "confidence": 0.75,
                "evidence": {
                    "url": url,
                    "title": article.get("title") or "",
                }
            })

        for heading in headings[:50]:
            heading = _norm(heading)
            if not heading or _looks_like_noise_phrase(heading):
                continue

            evidence.append({
                "concept": heading,
                "related_phrase": heading,
                "relation_type": "article_heading",
                "source": "article_body",
                "confidence": 0.78,
                "evidence": {
                    "url": url,
                    "title": article.get("title") or "",
                }
            })

        for entity in entities[:100]:
            if isinstance(entity, dict):
                phrase = _norm(entity.get("text") or entity.get("name") or entity.get("label") or "")
                entity_type = _norm(entity.get("type") or entity.get("entity_type") or "")
            else:
                phrase = _norm(entity)
                entity_type = ""

            if not phrase or _looks_like_noise_phrase(phrase) or _is_sitewide_article_noise(phrase):
                continue

            evidence.append({
                "concept": phrase,
                "related_phrase": phrase,
                "relation_type": "article_entity",
                "source": "article_body",
                "confidence": 0.78,
                "evidence": {
                    "url": url,
                    "title": article.get("title") or "",
                    "entity_type": entity_type,
                }
            })

        for item in related_concepts[:150]:
            if isinstance(item, dict):
                concept = _norm(item.get("concept") or item.get("source") or "")
                related = _norm(item.get("related") or item.get("target") or item.get("related_phrase") or "")
            else:
                concept = title
                related = _norm(item)

            if not concept or not related:
                continue

            if (
                _looks_like_noise_phrase(concept)
                or _looks_like_noise_phrase(related)
                or _is_sitewide_article_noise(concept)
                or _is_sitewide_article_noise(related)
            ):
                continue

            evidence.append({
                "concept": concept,
                "related_phrase": related,
                "relation_type": "article_related_concept",
                "source": "article_body",
                "confidence": 0.72,
                "evidence": {
                    "url": url,
                    "title": article.get("title") or "",
                }
            })

    return evidence


SOURCE_LOADERS = {
    "core_knowledge": load_core_knowledge_evidence,
    "workspace_synonyms": load_workspace_synonym_evidence,
    "page_index": load_page_index_evidence,
    "uploaded_documents": load_uploaded_document_evidence,
    "article_body": load_article_body_evidence,
}


def load_source_evidence(workspace_id: str, source_name: str) -> List[Dict[str, Any]]:
    loader = SOURCE_LOADERS.get(source_name)
    if loader is None:
        return []

    try:
        return loader(workspace_id)
    except Exception as exc:
        return [{
            "concept": "",
            "related_phrase": "",
            "relation_type": "loader_error",
            "source": source_name,
            "confidence": 0.0,
            "evidence": {
                "error": str(exc)
            }
        }]


def collect_source_evidence(workspace_id: str) -> List[Dict[str, Any]]:
    evidence: List[Dict[str, Any]] = []

    for source_name in SEMANTIC_SOURCES:
        evidence.extend(load_source_evidence(workspace_id, source_name))

    return evidence






SOURCE_CONFIDENCE_RULES: Dict[str, Dict[str, Any]] = {
    "core_knowledge": {
        "base": 0.95,
        "can_create_synonym": True,
        "role": "authority",
    },
    "workspace_synonyms": {
        "base": 0.94,
        "can_create_synonym": True,
        "role": "workspace_authority",
    },
    "topic_clusters": {
        "base": 0.90,
        "can_create_synonym": False,
        "role": "support",
    },
    "section_clusters": {
        "base": 0.88,
        "can_create_synonym": False,
        "role": "support",
    },
    "page_index": {
        "base": 0.85,
        "can_create_synonym": False,
        "role": "target_support",
    },
    "uploaded_documents": {
        "base": 0.80,
        "can_create_synonym": False,
        "role": "candidate",
    },
    "article_body": {
        "base": 0.75,
        "can_create_synonym": False,
        "role": "candidate",
    },
    "external_resolver": {
        "base": 0.90,
        "can_create_synonym": False,
        "role": "validation",
    },
    "feedback_memory": {
        "base": 0.0,
        "can_create_synonym": False,
        "role": "confidence_adjustment",
    },
}


def source_confidence_rule(source: str) -> Dict[str, Any]:
    return SOURCE_CONFIDENCE_RULES.get(str(source or ""), {
        "base": 0.50,
        "can_create_synonym": False,
        "role": "unknown",
    })


def apply_source_confidence(item: Dict[str, Any]) -> Dict[str, Any]:
    source = str(item.get("source") or "")
    rule = source_confidence_rule(source)

    try:
        incoming = float(item.get("confidence") or 0.0)
    except Exception:
        incoming = 0.0

    base = float(rule.get("base") or 0.0)
    confidence = max(incoming, base)

    out = dict(item)
    out["confidence"] = round(min(0.99, confidence), 4)
    out["source_role"] = rule.get("role")
    out["can_create_synonym"] = bool(rule.get("can_create_synonym"))

    return out


def apply_confidence_rules(evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [apply_source_confidence(item) for item in evidence]




def _logical_upload_doc_id(path_value: Any) -> str:
    raw = str(path_value or "").replace("\\", "/")
    name = raw.split("/")[-1]

    # Strip common upload-pool prefixes.
    name = re.sub(r"^upload_phrase_pool_", "", name)
    name = re.sub(r"^upload_phrase_index_", "", name)
    name = re.sub(r"^upload_entity_map_", "", name)
    name = re.sub(r"^upload_entity_graph_", "", name)
    name = re.sub(r"^upload_struct_", "", name)

    # Remove extension.
    name = re.sub(r"\.json$", "", name)

    # Collapse timestamp snapshots.
    name = re.sub(r"_20\d{6}_\d{6}", "", name)

    # Collapse trailing UUID/hash-like run IDs.
    name = re.sub(r"_[a-f0-9]{16,}$", "", name)

    return _norm(name) or "unknown_upload_document"


def build_concepts_from_evidence(evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    concepts: Dict[str, Dict[str, Any]] = {}

    for item in evidence:
        concept_key = _norm(item.get("concept"))
        if not concept_key:
            continue

        related = _norm(item.get("related_phrase"))
        relation_type = str(item.get("relation_type") or "related").strip()
        source = str(item.get("source") or "unknown").strip()

        try:
            confidence = float(item.get("confidence") or 0.0)
        except Exception:
            confidence = 0.0

        if concept_key not in concepts:
            concepts[concept_key] = {
                "canonical_phrase": concept_key,
                "synonyms": [],
                "related_concepts": [],
                "page_topics": [],
                "preferred_targets": [],

                "cluster_topics": [],
                "section_topics": [],

                "accepted_feedback": {
                    "count": 0,
                    "pairs": [],
                    "confidence_boost": 0.0,
                },
                "rejected_feedback": {
                    "count": 0,
                    "pairs": [],
                    "confidence_penalty": 0.0,
                },

                "entity_types": [],
                "intent": {
                    "primary_intent": "unknown",
                    "intent_terms": [],
                    "confidence": 0.0,
                },

                "popularity": {
                    "active_phrase_frequency": 0,
                    "page_count": 0,
                    "document_count": 0,
                    "score": 0.0,
                },

                "freshness": {
                    "last_seen_at_utc": "",
                    "latest_source": "",
                    "score": 0.0,
                },

                "cross_workspace_support": {
                    "enabled": False,
                    "support_count": 0,
                    "domain_tags": [],
                    "privacy_safe": False,
                },

                "sources": [],
                "evidence": [],
                "confidence": 0.0,
            }

        concept = concepts[concept_key]

        if source and source not in concept["sources"]:
            concept["sources"].append(source)

        evidence_record = {
            "source": source,
            "source_role": item.get("source_role"),
            "can_create_synonym": bool(item.get("can_create_synonym")),
            "relation_type": relation_type,
            "related_phrase": related,
            "confidence": confidence,
            "evidence": item.get("evidence") or {},
        }

        concept["evidence"].append(evidence_record)

        if relation_type == "uploaded_document_phrase":
            concept["popularity"]["active_phrase_frequency"] += 1

            doc_file = str((item.get("evidence") or {}).get("file") or "")
            logical_doc_id = _logical_upload_doc_id(doc_file)

            if logical_doc_id:
                existing_docs = concept["popularity"].setdefault("document_ids", [])
                if logical_doc_id not in existing_docs:
                    existing_docs.append(logical_doc_id)
                    concept["popularity"]["document_count"] += 1

            if doc_file:
                existing_files = concept["popularity"].setdefault("document_files", [])
                if doc_file not in existing_files:
                    existing_files.append(doc_file)

        elif relation_type == "synonym" and related and related != concept_key:
            if related not in concept["synonyms"]:
                concept["synonyms"].append(related)

        elif relation_type == "page_topic":
            page_title = (item.get("evidence") or {}).get("title") or related or concept_key
            page_url = (item.get("evidence") or {}).get("url") or ""

            page_topic = {
                "title": page_title,
                "url": page_url,
                "confidence": confidence,
            }

            if page_topic not in concept["page_topics"]:
                concept["page_topics"].append(page_topic)

            concept["popularity"]["page_count"] += 1

            if page_url:
                target = {
                    "url": page_url,
                    "title": page_title,
                    "confidence": confidence,
                    "source": source,
                }
                if target not in concept["preferred_targets"]:
                    concept["preferred_targets"].append(target)

        elif related and related != concept_key:
            if related not in concept["related_concepts"]:
                concept["related_concepts"].append(related)

        concept["confidence"] = max(float(concept.get("confidence") or 0.0), confidence)

    out = list(concepts.values())

    for concept in out:
        concept["synonyms"] = sorted(concept.get("synonyms") or [])
        concept["related_concepts"] = sorted(concept.get("related_concepts") or [])
        concept["cluster_topics"] = sorted(concept.get("cluster_topics") or [])
        concept["section_topics"] = sorted(concept.get("section_topics") or [])
        concept["entity_types"] = sorted(concept.get("entity_types") or [])
        concept["sources"] = sorted(concept.get("sources") or [])

        document_ids = sorted(
            concept["popularity"].get("document_ids") or []
        )[:25]

        concept["popularity"]["document_ids"] = document_ids

        concept["popularity"]["documents"] = [
            {
                "document_id": doc_id,
                "document_type": "uploaded_workspace",
            }
            for doc_id in document_ids
        ]

        # Remove implementation details from semantic memory.
        concept["popularity"].pop("document_files", None)

        concept["popularity"]["score"] = round(
            min(
                1.0,
                (float(concept["popularity"].get("active_phrase_frequency") or 0) / 500.0)
                + (float(concept["popularity"].get("page_count") or 0) * 0.05)
                + (float(concept["popularity"].get("document_count") or 0) * 0.03)
            ),
            4,
        )

        concept["evidence_count"] = len(concept.get("evidence") or [])
        concept["confidence"] = round(float(concept.get("confidence") or 0.0), 4)

    out.sort(key=lambda x: (float(x.get("confidence") or 0.0), x.get("evidence_count") or 0), reverse=True)

    return out




def calculate_fused_confidence(concept: Dict[str, Any]) -> Dict[str, Any]:
    evidence = concept.get("evidence") or []

    authority_scores = []
    support_scores = []
    candidate_scores = []
    validation_scores = []

    for item in evidence:
        role = str(item.get("source_role") or "")
        try:
            score = float(item.get("confidence") or 0.0)
        except Exception:
            score = 0.0

        if role in ("authority", "workspace_authority"):
            authority_scores.append(score)
        elif role in ("support", "target_support"):
            support_scores.append(score)
        elif role == "candidate":
            candidate_scores.append(score)
        elif role == "validation":
            validation_scores.append(score)

    base = max(authority_scores or support_scores or candidate_scores or [0.0])

    support_boost = min(0.08, len(support_scores) * 0.02)
    validation_boost = min(0.06, len(validation_scores) * 0.03)
    popularity_boost = min(0.04, float((concept.get("popularity") or {}).get("score") or 0.0) * 0.04)

    # Candidate-only concepts should not become high-confidence synonyms.
    candidate_only = bool(candidate_scores and not authority_scores and not support_scores and not validation_scores)

    fused = base + support_boost + validation_boost + popularity_boost

    if candidate_only:
        fused = min(fused, 0.72)

    fused = round(min(0.99, max(0.0, fused)), 4)

    return {
        "score": fused,
        "base": round(base, 4),
        "authority_sources": len(authority_scores),
        "support_sources": len(support_scores),
        "candidate_sources": len(candidate_scores),
        "validation_sources": len(validation_scores),
        "support_boost": round(support_boost, 4),
        "validation_boost": round(validation_boost, 4),
        "popularity_boost": round(popularity_boost, 4),
        "candidate_only": candidate_only,
        "method": "semantic_fusion_v1",
    }


def apply_evidence_fusion(concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for concept in concepts:
        fusion = calculate_fused_confidence(concept)
        concept["confidence_fusion"] = fusion
        concept["confidence"] = fusion["score"]

    concepts.sort(
        key=lambda x: (
            float(x.get("confidence") or 0.0),
            int(x.get("evidence_count") or 0),
        ),
        reverse=True,
    )

    return concepts




def apply_conflict_resolution(concept: Dict[str, Any]) -> Dict[str, Any]:
    fusion = concept.get("confidence_fusion") or {}

    accepted = concept.get("accepted_feedback") or {}
    rejected = concept.get("rejected_feedback") or {}

    accepted_count = int(accepted.get("count") or 0)
    rejected_count = int(rejected.get("count") or 0)

    blocked_pairs = []
    for item in rejected.get("pairs") or []:
        if isinstance(item, dict) and item.get("blocked"):
            blocked_pairs.append(item)

    base_score = float(fusion.get("score") or concept.get("confidence") or 0.0)

    accepted_boost = min(0.05, accepted_count * 0.005)
    rejected_penalty = min(0.35, rejected_count * 0.02)

    hard_blocked = bool(blocked_pairs)

    candidate_only = bool(fusion.get("candidate_only"))

    final_score = base_score + accepted_boost - rejected_penalty

    if candidate_only:
        final_score = min(final_score, 0.72)

    if hard_blocked:
        final_score = 0.0

    final_score = round(min(0.99, max(0.0, final_score)), 4)

    concept["conflict_resolution"] = {
        "method": "semantic_conflict_resolution_v1",
        "base_score": round(base_score, 4),
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "accepted_boost": round(accepted_boost, 4),
        "rejected_penalty": round(rejected_penalty, 4),
        "hard_blocked": hard_blocked,
        "candidate_only": candidate_only,
        "final_score": final_score,
        "rules": [
            "blocked_pairs_override_all",
            "rejected_pairs_penalize_confidence",
            "accepted_pairs_boost_confidence",
            "candidate_only_capped_at_0_72",
            "cooccurrence_cannot_create_authority_synonym_without_support",
        ],
    }

    concept["confidence"] = final_score

    return concept


def apply_conflict_resolution_to_graph(concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = [apply_conflict_resolution(concept) for concept in concepts]

    out.sort(
        key=lambda x: (
            float(x.get("confidence") or 0.0),
            int(x.get("evidence_count") or 0),
        ),
        reverse=True,
    )

    return out




def build_graph_indexes(concepts: List[Dict[str, Any]]) -> Dict[str, Any]:
    canonical_lookup: Dict[str, int] = {}
    synonym_lookup: Dict[str, str] = {}
    target_lookup: Dict[str, List[str]] = {}

    for idx, concept in enumerate(concepts):
        canonical = _norm(concept.get("canonical_phrase"))

        if canonical:
            canonical_lookup[canonical] = idx

        for synonym in concept.get("synonyms") or []:
            synonym_key = _norm(synonym)
            if synonym_key and canonical:
                synonym_lookup[synonym_key] = canonical

        urls: List[str] = []
        for target in concept.get("preferred_targets") or []:
            if isinstance(target, dict):
                url = str(target.get("url") or "").strip()
                if url:
                    urls.append(url)

        if canonical:
            target_lookup[canonical] = sorted(set(urls))

    return {
        "canonical_lookup": canonical_lookup,
        "synonym_lookup": synonym_lookup,
        "target_lookup": target_lookup,
    }


def graph_statistics(concepts: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "concepts": len(concepts),
        "synonyms": sum(len(c.get("synonyms") or []) for c in concepts),
        "targets": sum(len(c.get("preferred_targets") or []) for c in concepts),
        "evidence": sum(len(c.get("evidence") or []) for c in concepts),
    }


def build_concept_graph(workspace_id: str) -> Dict[str, Any]:
    data = load_semantic_map(workspace_id)
    evidence = apply_confidence_rules(collect_source_evidence(workspace_id))
    concept_graph = apply_conflict_resolution_to_graph(
        apply_evidence_fusion(build_concepts_from_evidence(evidence))
    )

    indexes = build_graph_indexes(concept_graph)
    stats = graph_statistics(concept_graph)

    data["concept_graph"] = concept_graph
    data["graph_indexes"] = indexes
    data["semantic_learner"] = {
        "version": "semantic_workspace_learner_v1",
        "last_rebuilt_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": SEMANTIC_SOURCES,
        "concept_count": len(concept_graph),
        "evidence_count": len(evidence),
        "statistics": stats,
        "graph_indexes": {
            "canonical_lookup": len(indexes.get("canonical_lookup") or {}),
            "synonym_lookup": len(indexes.get("synonym_lookup") or {}),
            "target_lookup": len(indexes.get("target_lookup") or {}),
        },
        "status": "graph_writer_completed"
    }

    out = save_semantic_map(workspace_id, data)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "output_path": str(out),
        "concept_count": len(concept_graph),
        "evidence_count": len(evidence),
        "sources": SEMANTIC_SOURCES,
        "status": "graph_writer_completed"
    }




def seed_article_body_index(workspace_id: str) -> Dict[str, Any]:
    article_path = _article_body_index_path(workspace_id)
    article_obj = _read_json(article_path, {})

    if not isinstance(article_obj, dict):
        article_obj = {}

    article_obj.setdefault("version", "article_body_index_v1")
    article_obj.setdefault("workspace_id", workspace_id)
    article_obj.setdefault("articles", [])
    article_obj.setdefault("stats", {})

    existing = {}

    for item in article_obj.get("articles", []):
        if isinstance(item, dict):
            url = str(item.get("url") or "").strip()
            if url:
                existing[url] = item

    site_pages_path = _data_dir() / f"site_pages_{workspace_id}.json"
    site_obj = _read_json(site_pages_path, {})

    pages = site_obj.get("pages") if isinstance(site_obj, dict) else {}

    if isinstance(pages, dict):
        pages = list(pages.values())

    if not isinstance(pages, list):
        pages = []

    added = 0

    for page in pages:
        if not isinstance(page, dict):
            continue

        url = str(page.get("url") or "").strip()

        if not url:
            continue

        if url in existing:
            continue

        existing[url] = {
            "url": url,
            "title": page.get("title") or "",
            "h1": page.get("h1") or "",
            "description": page.get("description") or "",
            "headings": [],
            "body_text": "",
            "key_phrases": [],
            "entities": [],
            "related_concepts": [],
            "source": page.get("source") or "",
            "source_type": page.get("source_type") or "",
            "status": "seeded",
        }

        added += 1

    articles = sorted(
        existing.values(),
        key=lambda x: str(x.get("url") or "")
    )

    stats = {
        "article_count": len(articles),
        "with_body_text": sum(bool(a.get("body_text")) for a in articles),
        "with_headings": sum(bool(a.get("headings")) for a in articles),
        "with_entities": sum(bool(a.get("entities")) for a in articles),
        "with_related_concepts": sum(bool(a.get("related_concepts")) for a in articles),
    }

    article_obj["articles"] = articles
    article_obj["stats"] = stats
    article_obj["updated_at_utc"] = datetime.now(timezone.utc).isoformat()

    article_path.write_text(
        json.dumps(article_obj, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "ok": True,
        "added": added,
        "total_articles": len(articles),
        "path": str(article_path),
    }


def semantic_workspace_learner_healthcheck() -> Dict[str, Any]:
    return {
        "ok": True,
        "engine": "semantic_workspace_learner",
        "version": "v1_shell",
        "sources": SEMANTIC_SOURCES
    }
