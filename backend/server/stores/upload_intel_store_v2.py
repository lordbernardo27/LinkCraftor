from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.server.stores.candidate_window_guard import candidate_window_guard
from backend.server.stores.phrase_strength_scorer import score_phrase_strength
from backend.server.stores.smart_phrase_extractor import extract_smart_phrases
from backend.server.stores.upload_normalizer import normalize_upload
from backend.server.stores.upload_phrase_selector import select_upload_phrases


WORD_RE = re.compile(r"[a-z0-9]{2,}", re.I)
H_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
LI_RE = re.compile(r"<li[^>]*>(.*?)</li>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")

MAX_EXAMPLES_PER_PHRASE = 5

STOPWORDS: Set[str] = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "you",
    "are", "was", "were", "will", "can", "could", "should", "would", "have",
    "has", "had", "about", "over", "under", "than", "then", "when", "what",
    "where", "which", "who", "whom", "why", "how", "a", "an", "to", "of",
    "in", "on", "at", "by", "or", "as", "is", "it", "be", "not", "no", "if",
    "but", "so", "because", "after", "before", "during", "while", "through",
    "up", "down", "out", "off", "too", "very", "also",
}

UI_JUNK_TERMS: Set[str] = {
    "faq", "skip", "menu", "share", "home", "read more", "previous", "next",
    "written by", "contact us", "about us", "privacy policy", "terms",
    "cookie", "login", "register", "subscribe", "follow us", "facebook",
    "instagram", "twitter", "youtube", "whatsapp", "telegram",
}

META_SENTENCE_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(long tail phrases?|helpful phrases?|phrases such as)\b"),
    re.compile(r"\b(guide|explains|explained|explaining)\b"),
    re.compile(r"\b(you will|you ll|you may|you might|you can)\b"),
    re.compile(r"\b(for example|example of|such as)\b"),
)

META_PHRASE_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(long tail phrases?|helpful phrases?|phrases such as)\b"),
    re.compile(r"\b(guide|explains|explained|explaining)\b"),
    re.compile(r"\b(you ll|you will|you may|you might|you can)\b"),
    re.compile(r"\b(such as|for example|example of)\b"),
    re.compile(r"\b(actual day|each one|small mystery)\b"),
)

INTENT_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"^how to [a-z0-9\s\-]+$"),
    re.compile(r"^when do [a-z0-9\s\-]+$"),
    re.compile(r"^what is [a-z0-9\s\-]+$"),
    re.compile(r"^what are [a-z0-9\s\-]+$"),
    re.compile(r"^signs of [a-z0-9\s\-]+$"),
    re.compile(r"^symptoms of [a-z0-9\s\-]+$"),
    re.compile(r"^causes of [a-z0-9\s\-]+$"),
    re.compile(r"^treatment for [a-z0-9\s\-]+$"),
    re.compile(r"^best time [a-z0-9\s\-]+$"),
    re.compile(r"^best way [a-z0-9\s\-]+$"),
)


def _ws_safe(ws: str) -> str:
    ws = (ws or "default").strip().lower()
    return re.sub(r"[^a-z0-9_\-]", "_", ws)[:80] or "default"


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", s or "")).strip()


def _canonical_phrase(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"^\s*(?:\d+[\.\)]\s+|[•\-–]\s+)", "", s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s).strip()
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _normalize_document_text(text: str) -> str:
    text = (text or "").lower()

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = re.sub(r"<[^>]+>", " ", text)

    text = re.sub(r"[^\w\s]", " ", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text


def _document_fingerprint(
    *,
    original_name: str,
    text: str,
) -> Dict[str, Any]:
    normalized = _normalize_document_text(text or "")

    words = normalized.split()

    first = " ".join(words[:120])
    middle_start = max(len(words) // 2 - 60, 0)
    middle = " ".join(words[middle_start:middle_start + 120])
    last = " ".join(words[-120:])

    title = _normalize_document_text(original_name or "")

    full_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    signature_source = f"{title}\n{first}\n{middle}\n{last}\n{len(words)}"

    signature_hash = hashlib.sha256(
        signature_source.encode("utf-8")
    ).hexdigest()

    return {
        "full_hash": full_hash,
        "signature_hash": signature_hash,
        "word_count": len(words),
        "normalized_title": title,
    }


def _is_duplicate_document(
    *,
    docs_store: Dict[str, Any],
    original_name: str,
    text: str,
) -> Optional[Dict[str, Any]]:
    incoming = _document_fingerprint(
        original_name=original_name,
        text=text,
    )

    incoming_full = incoming.get("full_hash")
    incoming_sig = incoming.get("signature_hash")

    for existing_doc_id, existing_doc in docs_store.items():
        if not isinstance(existing_doc, dict):
            continue

        existing_fp = existing_doc.get("fingerprint")
        if not isinstance(existing_fp, dict):
            continue

        existing_full = existing_fp.get("full_hash")
        existing_sig = existing_fp.get("signature_hash")

        if incoming_full and existing_full and incoming_full == existing_full:
            return {
                "duplicate": True,
                "reason": "exact_text_hash_match",
                "existing_doc_id": existing_doc_id,
            }

        if incoming_sig and existing_sig and incoming_sig == existing_sig:
            return {
                "duplicate": True,
                "reason": "content_signature_match",
                "existing_doc_id": existing_doc_id,
            }

    return None



def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def _content_tokens(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


def _looks_like_ui_junk(s: str) -> bool:
    s = _canonical_phrase(s)
    if not s:
        return True
    return any(x in s for x in UI_JUNK_TERMS)


def _split_paragraphs(html: str, text: str) -> List[str]:
    html = html or ""
    paras = [_strip_tags(x) for x in P_RE.findall(html)]
    paras = [p for p in paras if p]
    if paras:
        return paras

    txt = (text or "").replace("\r\n", "\n")
    return [x.strip() for x in re.split(r"\n\s*\n+", txt) if x.strip()]


def _extract_headings(html: str) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    found = [(int(lvl), _strip_tags(inner)) for lvl, inner in H_RE.findall(html or "")]
    h1 = next((txt for lvl, txt in found if lvl == 1 and txt), None)
    headings = [{"level": lvl, "text": txt} for lvl, txt in found if lvl in (2, 3) and txt]
    return h1, headings


def _extract_list_items(html: str) -> List[str]:
    return [_strip_tags(x) for x in LI_RE.findall(html or "") if _strip_tags(x)]


def _looks_like_intent_phrase(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    return any(rx.match(p) for rx in INTENT_PATTERNS)


def _fails_semantic_filter(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    if not p:
        return True

    if any(rx.search(p) for rx in META_PHRASE_PATTERNS):
        return True

    tokens = _tokenize(p)
    if not tokens:
        return True

    bad_starts = {
        "you", "your", "we", "this", "that", "these", "those",
        "explains", "guide", "helpful", "special", "actual",
    }
    if tokens[0] in bad_starts:
        return True

    bad_ends = {"small", "one", "such", "each", "actual"}
    if tokens[-1] in bad_ends:
        return True

    if len(_content_tokens(tokens)) < 2 and not _looks_like_intent_phrase(p):
        return True

    return False


def _accept_phrase(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    if not p:
        return False

    if _looks_like_ui_junk(p):
        return False

    if _fails_semantic_filter(p):
        return False

    tokens = _tokenize(p)

    if len(tokens) < 2 or len(tokens) > 10:
        return False

    content = _content_tokens(tokens)
    if len(content) < 2:
        return False

    bad_starts = {"the", "this", "that", "these", "those", "your"}
    narrative_verbs = {"is", "are", "was", "were", "can", "will", "would"}

    if len(tokens) >= 4:
        if tokens[0] in bad_starts:
            return False
        if len(tokens) > 1 and tokens[1] in narrative_verbs:
            return False

    weak_words = {"feel", "like", "make", "take", "get", "go", "come"}
    if any(t in weak_words for t in tokens):
        return False

    bad_endings = {"like", "such", "each", "one", "matter"}
    if tokens[-1] in bad_endings:
        return False

    return True


def _derive_alias_variants(phrase: str) -> List[str]:
    p = _canonical_phrase(phrase)
    toks = p.split()
    out: List[str] = []

    if len(toks) >= 3:
        out.append(" ".join(toks[-2:]))
        out.append(" ".join(toks[:2]))
    if len(toks) >= 4:
        out.append(" ".join(toks[1:]))
        out.append(" ".join(toks[:-1]))

    clean: List[str] = []
    seen: Set[str] = set()
    for x in out:
        x = _canonical_phrase(x)
        if x and x != p and x not in seen and _accept_phrase(x):
            clean.append(x)
            seen.add(x)
    return clean[:3]


def _read_json(fp: Path, default: Any) -> Any:
    try:
        if not fp.exists():
            return default
        return json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json_atomic(fp: Path, obj: Any) -> None:
    fp.parent.mkdir(parents=True, exist_ok=True)
    tmp = fp.with_suffix(fp.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, fp)


def _paths_for_ws(workspace_id: str) -> Dict[str, Path]:
    ws = _ws_safe(workspace_id)
    d = _data_dir()
    return {
        "struct": d / f"upload_struct_{ws}.json",
        "phrases": d / f"upload_phrase_index_{ws}.json",
        "entities": d / f"upload_entity_map_{ws}.json",
        "graph": d / f"upload_entity_graph_{ws}.json",
    }


def _tier_for_source(source_type: str) -> str:
    if source_type in {"title", "heading_h1", "heading_h2", "heading_h3", "list_item"}:
        return "A"
    if source_type in {"intent", "entity", "noun_phrase", "action_object", "condition_phrase"}:
        return "B"
    return "C"


def _quality_score_for(source_type: str, repeats: int = 1) -> float:
    base_map = {
        "title": 1.00,
        "heading_h1": 1.00,
        "heading_h2": 0.95,
        "heading_h3": 0.90,
        "list_item": 0.85,
        "intent": 0.80,
        "entity": 0.78,
        "noun_phrase": 0.76,
        "action_object": 0.74,
        "condition_phrase": 0.72,
        "sentence": 0.70,
        "alias": 0.60,
    }
    base = base_map.get(source_type, 0.65)
    bonus = min(max(repeats - 1, 0) * 0.05, 0.20)
    return round(min(base + bonus, 1.0), 3)


def _upsert_phrase_record(
    ph: Dict[str, Any],
    phrase: str,
    source_type: str,
    doc_id: str,
    section_id: str,
    snippet: str,
    item: Optional[Dict[str, Any]] = None,
) -> None:
    phrase = _canonical_phrase(phrase)

    if not phrase:
        return

    # Phrase has already passed Extractor → Guard → Scorer.
# At index-write stage, only reject empty/corrupt phrases.
    if len(_tokenize(phrase)) < 2:
      return

    now = _now_iso()
    tier = _tier_for_source(source_type)

    rec = ph.get(phrase)
    if not isinstance(rec, dict):
        rec = {
            "phrase": phrase,
            "canonical": _canonical_phrase(phrase),
            "source_type": source_type,
            "tier": tier,
            "count_total": 0,
            "quality_score": _quality_score_for(source_type, 1),
            "docs": {},
            "sections": [],
            "first_seen": now,
            "last_seen": now,
            "examples": [],
            "aliases": _derive_alias_variants(phrase),
        }
        ph[phrase] = rec

    rec["count_total"] = int(rec.get("count_total") or 0) + 1
    rec["last_seen"] = now

    docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
    rec["docs"] = docs
    docs[doc_id] = int(docs.get(doc_id) or 0) + 1

    sections = rec.get("sections") if isinstance(rec.get("sections"), list) else []
    rec["sections"] = sections
    if section_id and section_id not in sections:
        sections.append(section_id)

    rec["quality_score"] = _quality_score_for(source_type, int(rec["count_total"]))

    if isinstance(item, dict):
        for key in (
            "extractor_intelligence",
            "quality_gate",
            "selector_intelligence",
            "strength",
        ):
            if isinstance(item.get(key), dict):
                rec[key] = item.get(key) or {}

        if item.get("score") is not None:
            rec["score"] = item.get("score")

        if item.get("quality_score") is not None:
            rec["strength_score"] = item.get("quality_score")
            try:
                rec["quality_score"] = max(
                    float(rec.get("quality_score") or 0.0),
                    float(item.get("quality_score") or 0.0),
                )
            except Exception:
                pass

        if item.get("quality_reason"):
            rec["quality_reason"] = item.get("quality_reason")

    examples = rec.get("examples") if isinstance(rec.get("examples"), list) else []
    rec["examples"] = examples
    if len(examples) < MAX_EXAMPLES_PER_PHRASE:
        examples.append({
            "doc_id": doc_id,
            "section_id": section_id,
            "snippet": snippet[:160] + ("…" if len(snippet) > 160 else ""),
        })


def _remove_doc_phrases(ph: Dict[str, Any], doc_id: str) -> None:
    if not doc_id:
        return

    to_delete: List[str] = []

    for phrase, rec in list(ph.items()):
        if not isinstance(rec, dict):
            continue

        docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}

        if doc_id not in docs:
            continue

        docs.pop(doc_id, None)
        rec["docs"] = docs

        if not docs:
            to_delete.append(phrase)
            continue

        count_total = 0
        for c in docs.values():
            try:
                count_total += int(c or 0)
            except Exception:
                continue

        rec["count_total"] = count_total

        sections = rec.get("sections") if isinstance(rec.get("sections"), list) else []
        rec["sections"] = [
            s for s in sections
            if not str(s).startswith(f"{doc_id}:")
        ]

        examples = rec.get("examples") if isinstance(rec.get("examples"), list) else []
        rec["examples"] = [
            ex for ex in examples
            if not isinstance(ex, dict) or str(ex.get("doc_id") or "") != doc_id
        ][:MAX_EXAMPLES_PER_PHRASE]

    for phrase in to_delete:
        ph.pop(phrase, None)


def _selector_metadata_map(selected: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    phrases = selected.get("phrases") if isinstance(selected.get("phrases"), list) else []

    for item in phrases:
        if not isinstance(item, dict):
            continue

        phrase = _canonical_phrase(str(item.get("phrase") or ""))
        if not phrase:
            continue

        out[phrase] = item

    return out


def _build_quality_phrase_items(
    *,
    text: str,
    html: str,
    original_name: str,
    doc_id: str,
    selected: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    candidates = extract_smart_phrases(
        text=text or "",
        html=html or "",
        title=original_name or "",
        doc_id=doc_id or "",
        max_candidates=500,
    )

    selector_map = _selector_metadata_map(selected)

    quality_items: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    counts = {
        "extractor_candidate_count": len(candidates),
        "guard_kept_count": 0,
        "scorer_kept_count": 0,
        "selector_selected_count": int(selected.get("selected_count") or 0),
    }

    for c in candidates:
        if not isinstance(c, dict):
            continue

        phrase = _canonical_phrase(str(c.get("phrase") or ""))
        source_type = str(c.get("source_type") or "unknown")
        section_id = str(c.get("section_id") or "")
        snippet = str(c.get("snippet") or "")

        if not phrase:
            continue

        guard = candidate_window_guard(phrase, source_type=source_type)
        if isinstance(guard, dict) and not bool(guard.get("keep")):
            continue

        counts["guard_kept_count"] += 1

        guarded_phrase = _canonical_phrase(str(guard.get("phrase") or phrase)) if isinstance(guard, dict) else phrase
        if not guarded_phrase:
            continue

        scored = score_phrase_strength(
            phrase=guarded_phrase,
            source_type=source_type,
        )

        if not isinstance(scored, dict) or not bool(scored.get("keep")):
            continue

        counts["scorer_kept_count"] += 1

        final_phrase = _canonical_phrase(str(scored.get("phrase") or guarded_phrase))
        if not final_phrase or final_phrase in seen:
            continue

        seen.add(final_phrase)

        selector_item = selector_map.get(final_phrase, {})

        item: Dict[str, Any] = {
            "phrase": final_phrase,
            "canonical": final_phrase,
            "source_type": source_type,
            "section_id": section_id,
            "snippet": snippet,
            "score": scored.get("score"),
            "quality_score": scored.get("score"),
            "quality_reason": scored.get("reason"),
            "extractor_intelligence": (
                c.get("extractor_intelligence")
                if isinstance(c.get("extractor_intelligence"), dict)
                else {}
            ),
            "quality_gate": (
                guard.get("quality_gate")
                if isinstance(guard, dict) and isinstance(guard.get("quality_gate"), dict)
                else {}
            ),
            "strength": scored,
        }

        if isinstance(selector_item, dict):
            if isinstance(selector_item.get("selector_intelligence"), dict):
                item["selector_intelligence"] = selector_item.get("selector_intelligence") or {}
            if selector_item.get("quality_reason"):
                item["selector_quality_reason"] = selector_item.get("quality_reason")

        quality_items.append(item)

    return quality_items, counts


def build_upload_intelligence(
    workspace_id: str,
    doc_id: str,
    stored_path: str,
    original_name: str,
    html: str,
    text: str,
) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    if not doc_id:
        raise ValueError("doc_id required")

    normalized = normalize_upload(stored_path)
    if not normalized.get("ok"):
        return {
            "ok": False,
            "reason": normalized.get("reason", "normalize failed"),
            "doc_id": doc_id,
            "stored_path": stored_path,
        }

    html = normalized.get("html", "") or ""
    text = normalized.get("text", "") or ""

    paths = _paths_for_ws(ws)

    struct = _read_json(paths["struct"], {"workspace_id": ws, "updated_at": _now_iso(), "docs": {}})
    if not isinstance(struct, dict):
        struct = {"workspace_id": ws, "updated_at": _now_iso(), "docs": {}}
    docs_store = struct.get("docs") if isinstance(struct.get("docs"), dict) else {}
    struct["docs"] = docs_store

    duplicate_check = _is_duplicate_document(
    docs_store=docs_store,
    original_name=original_name,
    text=text or "",
)

    if (
    isinstance(duplicate_check, dict)
    and duplicate_check.get("duplicate")
    and str(duplicate_check.get("existing_doc_id") or "") != str(doc_id)
):
     return {
        "ok": False,
        "duplicate_detected": True,
        "duplicate_reason": duplicate_check.get("reason"),
        "existing_doc_id": duplicate_check.get("existing_doc_id"),
        "workspace_id": ws,
        "doc_id": doc_id,
        "message": "This document already exists in this session.",
    }

    phrase_index = _read_json(paths["phrases"], {"workspace_id": ws, "updated_at": _now_iso(), "phrases": {}})
    if not isinstance(phrase_index, dict):
        phrase_index = {"workspace_id": ws, "updated_at": _now_iso(), "phrases": {}}
    ph = phrase_index.get("phrases") if isinstance(phrase_index.get("phrases"), dict) else {}
    phrase_index["phrases"] = ph

    _remove_doc_phrases(ph, doc_id)

    h1, headings = _extract_headings(html or "")
    list_items = _extract_list_items(html or "")
    paragraphs = _split_paragraphs(html or "", text or "")

    docs_store[doc_id] = {
        "doc_id": doc_id,
        "stored_path": stored_path,
        "original_name": original_name,
        "updated_at": _now_iso(),

        "fingerprint": _document_fingerprint(
            original_name=original_name,
            text=text or "",
        ),

        "h1": {
            "text": h1 or "",
            "aliases": _derive_alias_variants(h1 or "") if h1 else [],
        },

        "headings": headings,

        "list_items": [
            {
                "text": x,
                "aliases": _derive_alias_variants(x),
            }
            for x in list_items[:200]
        ],

        "paragraphs": [
            {
                "pid": f"p{i}",
                "text": para,
            }
            for i, para in enumerate(paragraphs)
        ],
    }
    struct["updated_at"] = _now_iso()
    _write_json_atomic(paths["struct"], struct)

    selected = select_upload_phrases(
        workspace_id=ws,
        doc_id=doc_id,
        original_name=original_name,
        html=html or "",
        text=text or "",
    )

    quality_items, quality_counts = _build_quality_phrase_items(
        text=text or "",
        html=html or "",
        original_name=original_name,
        doc_id=doc_id,
        selected=selected,
    )

    for item in quality_items:
        phrase = str(item.get("phrase") or "").strip()
        source_type = str(item.get("source_type") or "quality_pipeline")
        section_id = str(item.get("section_id") or "")
        snippet = str(item.get("snippet") or "")

        if not phrase:
            continue

        _upsert_phrase_record(
            ph,
            phrase,
            source_type,
            doc_id,
            section_id,
            snippet,
            item=item,
        )

    phrase_index["updated_at"] = _now_iso()
    phrase_index["selector_pipeline"] = {
        "enabled": True,
        "mode": "quality_pipeline_preserves_all_scorer_approved_phrases",
        "candidate_count": int(selected.get("candidate_count") or 0),
        "selected_count": int(selected.get("selected_count") or 0),
        "vertical": selected.get("vertical") or "universal",
    }
    phrase_index["quality_pipeline"] = {
        "enabled": True,
        "mode": "extractor_guard_scorer_index_writer",
        "extractor_candidate_count": quality_counts["extractor_candidate_count"],
        "guard_kept_count": quality_counts["guard_kept_count"],
        "scorer_kept_count": quality_counts["scorer_kept_count"],
        "indexed_quality_items_count": len(quality_items),
    }

    _write_json_atomic(paths["phrases"], phrase_index)

    entity_map = _read_json(paths["entities"], {"workspace_id": ws, "updated_at": _now_iso(), "entities": {}})
    graph = _read_json(paths["graph"], {"workspace_id": ws, "updated_at": _now_iso(), "nodes": {}, "edges": []})
    entity_map["updated_at"] = _now_iso()
    graph["updated_at"] = _now_iso()
    _write_json_atomic(paths["entities"], entity_map)
    _write_json_atomic(paths["graph"], graph)

    return {
        "ok": True,
        "workspace_id": ws,
        "doc_id": doc_id,
        "written": {
            "upload_struct": str(paths["struct"]),
            "upload_phrase_index": str(paths["phrases"]),
            "upload_entity_map": str(paths["entities"]),
            "upload_entity_graph": str(paths["graph"]),
        },
        "counts": {
            "paragraphs": len(paragraphs),
            "headings_h2h3": len(headings),
            "list_items": len(list_items),
            "phrases_total": len(phrase_index["phrases"]),
            "selector_candidate_count": int(selected.get("candidate_count") or 0),
            "selector_selected_count": int(selected.get("selected_count") or 0),
            "quality_extractor_candidate_count": quality_counts["extractor_candidate_count"],
            "quality_guard_kept_count": quality_counts["guard_kept_count"],
            "quality_scorer_kept_count": quality_counts["scorer_kept_count"],
            "quality_indexed_count": len(quality_items),
        },
    }