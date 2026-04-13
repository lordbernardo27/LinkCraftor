from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


WORD_RE = re.compile(r"[a-z0-9]{2,}", re.I)
H_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
LI_RE = re.compile(r"<li[^>]*>(.*?)</li>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
CLAUSE_SPLIT_RE = re.compile(r"[,;:\-\u2013\u2014]\s+|\s+\bor\b\s+|\s+\band\b\s+")

NGRAM_MIN_N = 2
NGRAM_MAX_N = 5
MAX_NGRAMS_PER_SENTENCE = 120
MAX_EXAMPLES_PER_PHRASE = 5

STOPWORDS: Set[str] = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "you", "are", "was", "were",
    "will", "can", "could", "should", "would", "have", "has", "had", "about", "over", "under", "than",
    "then", "when", "what", "where", "which", "who", "whom", "why", "how", "a", "an", "to", "of", "in",
    "on", "at", "by", "or", "as", "is", "it", "be", "not", "no", "if", "but", "so", "because", "after",
    "before", "during", "while", "through", "up", "down", "out", "off", "too", "very", "also"
}

UI_JUNK_TERMS: Set[str] = {
    "faq", "skip", "menu", "share", "home", "read more", "previous", "next", "written by", "contact us",
    "about us", "privacy policy", "terms", "cookie", "login", "register", "subscribe", "follow us",
    "facebook", "instagram", "twitter", "youtube", "whatsapp", "telegram"
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

ENTITY_SEEDS: List[str] = [
    "lmp",
    "ovulation",
    "basal body temperature",
    "bbt",
    "ultrasound",
    "gestational age",
    "conception date",
    "due date",
    "fertile window",
    "cervical mucus",
    "morning sickness",
    "first trimester",
    "postpartum",
    "breastfeeding",
    "newborn",
]


def _ws_safe(ws: str) -> str:
    ws = (ws or "default").strip().lower()
    ws = re.sub(r"[^a-z0-9_\-]", "_", ws)[:80] or "default"
    return ws


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


def _split_sentences(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    return [p.strip() for p in SENTENCE_SPLIT_RE.split(text) if p and p.strip()]


def _extract_headings(html: str) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    found = [(int(lvl), _strip_tags(inner)) for lvl, inner in H_RE.findall(html or "")]
    h1 = next((txt for lvl, txt in found if lvl == 1 and txt), None)
    headings = [{"level": lvl, "text": txt} for lvl, txt in found if lvl in (2, 3) and txt]
    return h1, headings


def _extract_list_items(html: str) -> List[str]:
    return [_strip_tags(x) for x in LI_RE.findall(html or "") if _strip_tags(x)]


def _extract_canonical_core_phrase(s: str) -> str:
    s = _canonical_phrase(s)
    if not s:
        return ""

    markers = [
        "how to ", "when do ", "what is ", "what are ",
        "signs of ", "symptoms of ", "causes of ", "treatment for ",
        "best time ", "best way ",
    ]
    starts = [s.find(m) for m in markers if s.find(m) != -1]
    if starts:
        s = s[min(starts):].strip()

    lead_patterns = [
        r"^people often ask\s+",
        r"^many people ask\s+",
        r"^many women ask\s+",
        r"^women often ask\s+",
        r"^doctors are often asked\s+",
        r"^you may wonder\s+",
        r"^you might wonder\s+",
        r"^you may ask\s+",
        r"^you might ask\s+",
        r"^you may be asking\s+",
        r"^often ask\s+",
    ]
    for pat in lead_patterns:
        s = re.sub(pat, "", s).strip()

    return _canonical_phrase(s)


def _is_valid_content_sentence(text: str) -> bool:
    t = _canonical_phrase(text)
    if not t or _looks_like_ui_junk(t):
        return False
    return not any(p.search(t) for p in META_SENTENCE_PATTERNS)


def _fails_semantic_filter(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    if not p:
        return True

    if any(rx.search(p) for rx in META_PHRASE_PATTERNS):
        return True

    tokens = _tokenize(p)
    if not tokens:
        return True

    if len(tokens) <= 3 and p in {
        "clinic or app",
        "can search deeper",
        "do you turn",
        "actual day",
        "each one",
    }:
        return True

    bad_starts = {
        "you", "your", "we", "this", "that", "these", "those",
        "explains", "guide", "helpful", "special", "actual"
    }
    if tokens[0] in bad_starts:
        return True

    bad_ends = {"small", "one", "such", "each", "actual"}
    if tokens[-1] in bad_ends:
        return True

    if len(_content_tokens(tokens)) < 2 and not _looks_like_intent_phrase(p):
        return True

    return False


def _looks_like_intent_phrase(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    return any(rx.match(p) for rx in INTENT_PATTERNS)


def _looks_like_entity_phrase(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    if p in ENTITY_SEEDS:
        return True
    return any(seed in p for seed in ENTITY_SEEDS)


def _accept_phrase(phrase: str) -> bool:
    p = _canonical_phrase(phrase)
    if not p:
        return False
    if _looks_like_ui_junk(p):
        return False
    if _fails_semantic_filter(p):
        return False

    tokens = _tokenize(p)
    if len(tokens) < NGRAM_MIN_N or len(tokens) > NGRAM_MAX_N:
        return False

    if _looks_like_intent_phrase(p):
        return True

    if _looks_like_entity_phrase(p) and len(_content_tokens(tokens)) >= 2:
        return True

    if len(_content_tokens(tokens)) >= 2:
        return True

    return False


def _generate_sentence_candidates(sentence: str) -> List[str]:
    s = _canonical_phrase(sentence)
    if not s or not _is_valid_content_sentence(s):
        return []

    clause_parts = [
        _canonical_phrase(x)
        for x in CLAUSE_SPLIT_RE.split(s)
        if _canonical_phrase(x)
    ]

    out: List[str] = []
    seen: Set[str] = set()
    made = 0

    for part in clause_parts:
        if not _is_valid_content_sentence(part):
            continue

        tokens = _tokenize(part)
        if len(tokens) < NGRAM_MIN_N:
            continue

        for n in range(NGRAM_MIN_N, NGRAM_MAX_N + 1):
            if n > len(tokens):
                break

            for i in range(0, len(tokens) - n + 1):
                cand = " ".join(tokens[i:i + n]).strip()

                if _fails_semantic_filter(cand):
                    continue

                cand = _extract_canonical_core_phrase(cand) or _canonical_phrase(cand)

                if _fails_semantic_filter(cand):
                    continue

                if not _accept_phrase(cand):
                    continue

                if cand not in seen:
                    out.append(cand)
                    seen.add(cand)
                    made += 1
                    if made >= MAX_NGRAMS_PER_SENTENCE:
                        return out

    return out


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
    if source_type == "sentence":
        return "B"
    return "C"


def _quality_score_for(source_type: str, repeats: int = 1) -> float:
    base_map = {
        "title": 1.00,
        "heading_h1": 1.00,
        "heading_h2": 0.95,
        "heading_h3": 0.90,
        "list_item": 0.85,
        "sentence": 0.70,
        "alias": 0.60,
    }
    base = base_map.get(source_type, 0.50)
    bonus = min(max(repeats - 1, 0) * 0.05, 0.20)
    return round(min(base + bonus, 1.0), 3)


def _upsert_phrase_record(
    ph: Dict[str, Any],
    phrase: str,
    source_type: str,
    doc_id: str,
    section_id: str,
    snippet: str,
) -> None:
    phrase = _extract_canonical_core_phrase(phrase) or _canonical_phrase(phrase)
    if not _accept_phrase(phrase):
        return

    now = _now_iso()
    tier = _tier_for_source(source_type)

    rec = ph.get(phrase)
    if not isinstance(rec, dict):
        rec = {
            "phrase": phrase,
            "canonical": phrase,
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

    examples = rec.get("examples") if isinstance(rec.get("examples"), list) else []
    rec["examples"] = examples
    if len(examples) < MAX_EXAMPLES_PER_PHRASE:
        examples.append({
            "doc_id": doc_id,
            "section_id": section_id,
            "snippet": snippet[:160] + ("…" if len(snippet) > 160 else ""),
        })


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

    # BLOCK NON-HTML FILES
    if not stored_path.lower().endswith((".html", ".htm")):
        return {
            "ok": False,
            "reason": "non-html file skipped",
            "doc_id": doc_id,
        }

    # BLOCK BINARY / DOCX-LIKE CONTENT
    html_preview = (html or "")[:200].lower()
    if "pk" in html_preview and "xml" in (html or "").lower():
        return {
            "ok": False,
            "reason": "binary/zip-like content skipped",
            "doc_id": doc_id,
        }

    paths = _paths_for_ws(ws)

    struct = _read_json(paths["struct"], {"workspace_id": ws, "updated_at": _now_iso(), "docs": {}})
    if not isinstance(struct, dict):
        struct = {"workspace_id": ws, "updated_at": _now_iso(), "docs": {}}
    docs_store = struct.get("docs") if isinstance(struct.get("docs"), dict) else {}
    struct["docs"] = docs_store

    phrase_index = _read_json(paths["phrases"], {"workspace_id": ws, "updated_at": _now_iso(), "phrases": {}})
    if not isinstance(phrase_index, dict):
        phrase_index = {"workspace_id": ws, "updated_at": _now_iso(), "phrases": {}}
    ph = phrase_index.get("phrases") if isinstance(phrase_index.get("phrases"), dict) else {}
    phrase_index["phrases"] = ph

    h1, headings = _extract_headings(html or "")
    list_items = _extract_list_items(html or "")
    paragraphs = _split_paragraphs(html or "", text or "")

    docs_store[doc_id] = {
        "doc_id": doc_id,
        "stored_path": stored_path,
        "original_name": original_name,
        "updated_at": _now_iso(),
        "h1": {"text": h1 or "", "aliases": _derive_alias_variants(h1 or "") if h1 else []},
        "headings": headings,
        "list_items": [{"text": x, "aliases": _derive_alias_variants(x)} for x in list_items[:200]],
        "paragraphs": [{"pid": f"p{i}", "text": para} for i, para in enumerate(paragraphs)],
    }
    struct["updated_at"] = _now_iso()
    _write_json_atomic(paths["struct"], struct)

    structured_candidates: List[Tuple[str, str, str, str]] = []

    if h1:
        structured_candidates.append((h1, "heading_h1", "h1", h1))

    for idx, h in enumerate(headings):
        txt = str(h.get("text") or "").strip()
        lvl = int(h.get("level") or 0)
        if txt:
            structured_candidates.append((txt, f"heading_h{lvl}", f"h{lvl}_{idx}", txt))

    for idx, li in enumerate(list_items[:200]):
        structured_candidates.append((li, "list_item", f"li_{idx}", li))

    if original_name:
        title_like = Path(original_name).stem.replace("_", " ").replace("-", " ")
        structured_candidates.append((title_like, "title", "title_0", title_like))

    for raw_text, source_type, section_id, snippet in structured_candidates:
        phrase = _extract_canonical_core_phrase(raw_text) or _canonical_phrase(raw_text)
        _upsert_phrase_record(ph, phrase, source_type, doc_id, section_id, snippet)

    for i, para in enumerate(paragraphs):
        pid = f"p{i}"
        sentence_candidates_all: List[str] = []

        for sentence in _split_sentences(para):
            if not _is_valid_content_sentence(sentence):
                continue
            sentence_candidates_all.extend(_generate_sentence_candidates(sentence))

        seen_in_para: Set[str] = set()
        for candidate in sentence_candidates_all:
            if candidate in seen_in_para:
                continue
            seen_in_para.add(candidate)
            _upsert_phrase_record(ph, candidate, "sentence", doc_id, pid, para)

    phrase_index["updated_at"] = _now_iso()
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
        },
    }