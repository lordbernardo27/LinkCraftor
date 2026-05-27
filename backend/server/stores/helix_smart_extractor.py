from __future__ import annotations

import re
from typing import Any, Dict, List, Set

try:
    from backend.server.stores.dis_pipeline_learning import learn_from_pipeline_rejection
except Exception:
    def learn_from_pipeline_rejection(**kwargs):
        return None


WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9\.\-_/]*")
TAG_RE = re.compile(r"<[^>]+>")
H_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
LI_RE = re.compile(r"<li[^>]*>(.*?)</li>", re.IGNORECASE | re.DOTALL)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")

STOPWORDS: Set[str] = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your",
    "you", "are", "was", "were", "will", "can", "could", "should",
    "would", "have", "has", "had", "about", "over", "under", "than",
    "then", "when", "what", "where", "which", "who", "why", "how",
    "a", "an", "to", "of", "in", "on", "at", "by", "or", "as", "is",
    "it", "be", "not", "no", "if", "but", "so", "because", "after",
    "before", "during", "while", "through", "up", "down", "out", "off",
    "too", "very", "also",
}

BAD_STARTS = {
    "and", "or", "but", "so", "then", "this", "that", "these", "those",
    "your", "you", "because", "whether", "rather", "without", "with",
    "into", "from", "for", "to", "at", "on", "by", "if", "while",
}

BAD_ENDINGS = {
    "and", "or", "but", "so", "then", "this", "that", "your", "because",
    "about", "before", "after", "during", "through", "with", "without",
    "than", "rather", "into", "from", "for", "to", "by", "if", "when",
    "while", "at", "on", "a", "an", "the", "of",
}

AUTHORITY_HEADS = {
    "framework", "standard", "standards", "specification", "protocol",
    "policy", "regulation", "compliance", "governance", "audit",
    "certification", "guideline", "model", "methodology", "method",
    "architecture", "schema", "algorithm", "analysis", "trial", "study",
    "review", "report", "survey", "index", "rate", "ratio", "risk",
    "yield", "token", "api", "sla", "encryption", "dosage", "regimen",
}

PROTOCOL_TERMS = {
    "oauth", "openid", "jwt", "saml", "graphql", "grpc", "openapi",
    "rest", "http", "https", "websocket", "json", "xml", "yaml",
}

GOVERNANCE_TERMS = {
    "hipaa", "gdpr", "ccpa", "soc", "pci", "dss", "nist", "iso",
    "fips", "sox", "ferpa", "coppa", "compliance", "audit",
    "privacy", "governance", "regulation", "policy",
}

TECH_TERMS = {
    "kubernetes", "docker", "redis", "postgresql", "mysql", "mongodb",
    "tensorflow", "pytorch", "react", "angular", "vue", "django",
    "flask", "fastapi", "kafka", "rabbitmq", "terraform", "ansible",
}

EVIDENCE_TERMS = {
    "study", "report", "survey", "data", "statistics", "journal",
    "paper", "whitepaper", "case", "findings", "published",
    "according", "source", "sample", "trial", "meta-analysis",
}

ORG_SUFFIXES = {
    "inc", "ltd", "llc", "university", "agency", "association",
    "institute", "foundation", "committee", "board", "authority",
    "bank", "school", "hospital", "organization", "centre", "center",
}

SCIENTIFIC_SUFFIX_RE = re.compile(
    r"\b[A-Za-z]{5,}(itis|osis|emia|algia|ectomy|opathy|genesis|omics|cyte|phagia|necrosis)\b",
    re.I,
)
GENE_RE = re.compile(r"\b[A-Z]{2,}\d+(?:-\d+)?\b")
CRISPR_RE = re.compile(r"\bCRISPR[-–]?[A-Za-z0-9]+\b", re.I)
SPEC_RE = re.compile(r"\b(?:ISO(?:/IEC)?|IEC|NIST|PCI\s*DSS|SOC\s*2|SOC\s*1|RFC|IEEE|WCAG|FIPS|EN|BSI|ETSI)\s*[-:]?\s*\d{1,6}(?:[:\-.]\d+)?\b", re.I)
VERSION_RE = re.compile(r"\b(?:v(?:er(?:sion)?)?\.?\s*)?\d+(?:\.\d+)+\b", re.I)
MEASUREMENT_RE = re.compile(r"\b\d+(?:\.\d+)?(?:\s|-)?(?:mg|mcg|g|kg|ml|l|mmhg|ms|gb|mb|tb|bit|bits|day|days|week|weeks|month|months|year|years|%)\b", re.I)
FORMAL_REF_RE = re.compile(r"\b(?:section|clause|article|policy|case\s+no\.?|model|version)\s*\d+(?:\.\d+)*\b", re.I)
ACRONYM_RE = re.compile(r"\b[A-Z]{2,}(?:\s*\d+)?\b")
ACRONYM_EXPANSION_RE = re.compile(r"\b(?:[A-Z]{2,}\s*\([A-Za-z][A-Za-z0-9&\-\s]{2,}\)|[A-Za-z][A-Za-z0-9&\-\s]{2,}\s*\([A-Z]{2,}\))\b")


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(float(value), 4)))


def strip_tags(text: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", text or "")).strip()


def canonical_phrase(text: str) -> str:
    s = str(text or "").strip()
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"^\s*(?:\d+[\.\)]\s+|[•\-]\s+)", "", s)
    s = re.sub(r"^[\"'“”‘’\(\[\{]+|[\"'“”‘’\)\]\}:;,\.\!\?]+$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalized_phrase(text: str) -> str:
    s = canonical_phrase(text).lower()
    s = re.sub(r"\b(rfc|iso|nist|soc|pci|oauth|openapi)\s*[-:]?\s*(\d)", r"\1 \2", s)
    s = re.sub(r"(\d)\s*[-]?\s*(mg|mcg|g|kg|ml|l|mmhg|ms|gb|mb|tb|bit|bits|days?|weeks?|months?|years?|%)\b", r"\1 \2", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokenize(text: str) -> List[str]:
    return WORD_RE.findall(text or "")


def token_lc(text: str) -> List[str]:
    return [t.lower() for t in tokenize(text)]


def split_sentences(text: str) -> List[str]:
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(text or "") if s and s.strip()]


def extract_paragraphs(html: str = "", text: str = "") -> List[str]:
    paras = [strip_tags(x) for x in P_RE.findall(html or "")]
    paras = [p for p in paras if p]
    if paras:
        return paras
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    return [x.strip() for x in re.split(r"\n\s*\n+", raw) if x.strip()]


def extract_headings_and_lists(html: str = "") -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for lvl, inner in H_RE.findall(html or ""):
        txt = strip_tags(inner)
        if not txt:
            continue
        level = int(lvl)
        if level > 4:
            continue
        out.append({
            "phrase": canonical_phrase(txt),
            "source_type": f"heading_h{level}",
            "section_id": f"heading_h{level}_{len(out)}",
            "snippet": txt,
            "heading_level": level,
        })

    for li in [strip_tags(x) for x in LI_RE.findall(html or "")]:
        if li:
            out.append({
                "phrase": canonical_phrase(li),
                "source_type": "list_item",
                "section_id": f"list_item_{len(out)}",
                "snippet": li,
                "heading_level": None,
            })

    return out


def _content_ratio(tokens: List[str]) -> float:
    if not tokens:
        return 0.0
    content = [t for t in [x.lower() for x in tokens] if t not in STOPWORDS]
    return len(content) / max(1, len(tokens))


def _has_bad_edges(tokens: List[str]) -> bool:
    low = [t.lower() for t in tokens]
    if not low:
        return True
    return low[0] in BAD_STARTS or low[-1] in BAD_ENDINGS


def _proper_named_entity_score(phrase: str) -> float:
    toks = tokenize(phrase)
    if len(toks) < 2:
        return 0.0

    lower = [t.lower().strip(".") for t in toks]
    org_hit = any(t in ORG_SUFFIXES for t in lower)
    acronym_hit = any(re.fullmatch(r"[A-Z]{2,}\d*", t) for t in toks)
    title_words = [t for t in toks if re.fullmatch(r"[A-Z][a-z][A-Za-z0-9&.\-]*", t)]

    # Avoid treating ordinary title/headline phrases as named entities.
    weak_title_heads = {
        "calculate", "pregnancy", "due", "date", "guide", "common",
        "method", "methods", "calculator", "period", "cycle"
    }
    if not org_hit and not acronym_hit:
        if any(t in weak_title_heads for t in lower):
            return 0.0

    score = 0.0
    if org_hit:
        score += 0.55
    if acronym_hit:
        score += 0.30
    if len(title_words) >= 2 and org_hit:
        score += 0.25
    elif len(title_words) >= 3 and not any(t in STOPWORDS for t in lower):
        score += 0.20

    return _clamp(score)


def _canonical_concept_score(phrase: str) -> float:
    toks = token_lc(phrase)
    if len(toks) < 2:
        return 0.0

    content = [t for t in toks if t not in STOPWORDS]
    has_authority_head = toks[-1] in AUTHORITY_HEADS or any(t in AUTHORITY_HEADS for t in toks)
    has_formal_signal = bool(
        SPEC_RE.search(phrase)
        or FORMAL_REF_RE.search(phrase)
        or VERSION_RE.search(phrase)
        or MEASUREMENT_RE.search(phrase)
        or ACRONYM_RE.search(phrase)
    )
    has_vertical_signal = any(t in PROTOCOL_TERMS or t in GOVERNANCE_TERMS or t in TECH_TERMS for t in toks)

    # Canonical collocation must be authority-like, not just any content-heavy phrase.
    if not (has_authority_head or has_formal_signal or has_vertical_signal):
        return 0.0

    score = 0.0
    if len(content) >= 2 and _content_ratio(toks) >= 0.65:
        score += 0.22
    if has_authority_head:
        score += 0.32
    if has_formal_signal:
        score += 0.25
    if has_vertical_signal:
        score += 0.18
    if " vs " in f" {phrase.lower()} " or " compared to " in phrase.lower():
        score += 0.16

    return _clamp(score)


def _evidence_intent_score(phrase: str, snippet: str) -> float:
    window = f"{phrase} {snippet}".lower()
    hits = sum(1 for t in EVIDENCE_TERMS if t in window)
    score = min(0.60, hits * 0.12)
    if re.search(r"\b(19|20)\d{2}\b", window):
        score += 0.12
    if "%" in window or re.search(r"\bn\s*=\s*\d+\b", window):
        score += 0.12
    return _clamp(score)


def _formal_reference_score(phrase: str) -> float:
    score = 0.0
    if SPEC_RE.search(phrase):
        score += 0.55
    if FORMAL_REF_RE.search(phrase):
        score += 0.45
    if VERSION_RE.search(phrase):
        score += 0.20
    if re.search(r"\b[A-Z]{2,}[-_/]?\d{2,}\b", phrase):
        score += 0.35
    return _clamp(score)


def _specificity_score(phrase: str) -> float:
    toks = tokenize(phrase)
    if not toks:
        return 0.0
    long_tokens = [t for t in toks if len(t) >= 8]
    mixed = [t for t in toks if re.search(r"[A-Z]", t) and re.search(r"\d", t)]
    hyphenated = [t for t in toks if "-" in t]
    score = 0.0
    score += min(0.35, len(long_tokens) * 0.10)
    score += min(0.30, len(mixed) * 0.15)
    score += min(0.20, len(hyphenated) * 0.10)
    if len(toks) >= 3 and _content_ratio(toks) >= 0.70:
        score += 0.15
    return _clamp(score)


def _anchor_stability_score(source_type: str, phrase: str, full_text: str) -> float:
    score = 0.0
    if source_type.startswith("heading_h"):
        level = int(source_type.replace("heading_h", "") or "4")
        score += max(0.10, 0.35 - ((level - 1) * 0.05))
    try:
        count = len(re.findall(re.escape(phrase), full_text, flags=re.I))
        if count >= 2:
            score += 0.20
    except Exception:
        pass
    return _clamp(score)


def detect_authority_clues(phrase: str, snippet: str = "", source_type: str = "", full_text: str = "") -> Dict[str, Any]:
    matched: List[str] = []
    low = phrase.lower()
    toks = token_lc(phrase)

    if _proper_named_entity_score(phrase) >= 0.35:
        matched.append("proper_named_entity")
    if SPEC_RE.search(phrase):
        matched.append("standards_spec_id")
    if any(t in TECH_TERMS for t in toks) or re.search(r"\b[A-Za-z]+(?:\.js|DB|SQL)\b", phrase):
        matched.append("library_tool_product")
    if any(t in PROTOCOL_TERMS for t in toks) or re.search(r"\bHTTP/[23]\b", phrase, re.I):
        matched.append("protocol_format")
    if SCIENTIFIC_SUFFIX_RE.search(phrase) or GENE_RE.search(phrase) or CRISPR_RE.search(phrase):
        matched.append("scientific_medical_morphology")
    if _canonical_concept_score(phrase) >= 0.35:
        matched.append("canonical_collocation")
    if ACRONYM_EXPANSION_RE.search(phrase):
        matched.append("acronym_expansion")
    if any(t in GOVERNANCE_TERMS for t in toks):
        matched.append("regulatory_governance")
    if _evidence_intent_score(phrase, snippet) >= 0.24:
        matched.append("evidence_citation_intent")
    if _formal_reference_score(phrase) >= 0.35:
        matched.append("formal_identifier")
    if MEASUREMENT_RE.search(phrase):
        matched.append("measurement_authority")
    if any(t in {"certification", "certified", "accreditation", "accredited"} for t in toks):
        matched.append("certification_accreditation")
    if any(t in {"section", "clause", "article", "case", "statute", "act"} for t in toks) or FORMAL_REF_RE.search(phrase):
        matched.append("legal_case_reference")
    if any(t in {"yield", "inflation", "gdp", "cpi", "interest", "revenue", "margin", "volatility"} for t in toks):
        matched.append("financial_economic_metric")
    if any(t in {"trial", "study", "review", "meta-analysis", "cohort", "survey"} for t in toks):
        matched.append("research_study_trial")
    if _proper_named_entity_score(phrase) >= 0.55:
        matched.append("institution_organization")
    if any(t in {"framework", "methodology", "model", "architecture", "protocol"} for t in toks):
        matched.append("methodology_framework")
    if "%" in phrase or re.search(r"\bn\s*=\s*\d+\b", f"{phrase} {snippet}", re.I):
        matched.append("statistical_data_pattern")
    if any(t in {"architecture", "gateway", "cluster", "schema", "engine", "pipeline", "controller"} for t in toks):
        matched.append("technical_architecture")
    if _specificity_score(phrase) >= 0.35:
        matched.append("rare_specific_terminology")

    universal_scores = {
        "proper_named_entity": _proper_named_entity_score(phrase),
        "canonical_concept": _canonical_concept_score(phrase),
        "evidence_intent": _evidence_intent_score(phrase, snippet),
        "formal_reference": _formal_reference_score(phrase),
        "specificity": _specificity_score(phrase),
        "anchor_stability": _anchor_stability_score(source_type, phrase, full_text),
    }

    authority_score = _clamp(
        0.16 * universal_scores["proper_named_entity"] +
        0.18 * universal_scores["canonical_concept"] +
        0.16 * universal_scores["evidence_intent"] +
        0.20 * universal_scores["formal_reference"] +
        0.16 * universal_scores["specificity"] +
        0.14 * universal_scores["anchor_stability"] +
        min(0.25, len(set(matched)) * 0.035)
    )

    primary = "general_authority"
    if "standards_spec_id" in matched:
        primary = "standards_spec"
    elif "protocol_format" in matched:
        primary = "technical_protocol"
    elif "regulatory_governance" in matched:
        primary = "governance_framework"
    elif "scientific_medical_morphology" in matched:
        primary = "scientific_entity"
    elif "measurement_authority" in matched:
        primary = "measurement_authority"
    elif "proper_named_entity" in matched:
        primary = "proper_named_entity"

    return {
        "authority_candidate": bool(matched) and authority_score >= 0.22,
        "matched_clues": sorted(set(matched)),
        "authority_clue_count": len(set(matched)),
        "primary_authority_category": primary,
        "authority_confidence": authority_score,
        "universal_authority_scores": universal_scores,
    }


def _helix_basic_reject(phrase: str, authority: Dict[str, Any]) -> bool:
    p = canonical_phrase(phrase)
    toks = token_lc(p)

    if not p or len(toks) < 2 or len(toks) > 10:
        return True

    if _has_bad_edges(toks):
        if not authority.get("matched_clues"):
            return True

    if _content_ratio(toks) < 0.45:
        if authority.get("authority_confidence", 0.0) < 0.50:
            return True

    if any(t in {"thing", "things", "something", "anything", "everything"} for t in toks):
        return True

    if re.search(r"\b(and|or|but)\s+(and|or|but)\b", p, re.I):
        return True

    return False


def _source_type_from_category(primary: str, fallback: str) -> str:
    return {
        "standards_spec": "standards_spec",
        "technical_protocol": "technical_protocol",
        "governance_framework": "governance_framework",
        "scientific_entity": "scientific_entity",
        "measurement_authority": "measurement_authority",
        "proper_named_entity": "proper_named_entity",
        "general_authority": fallback,
    }.get(primary or "", fallback)


def _add_helix_candidate(
    out: List[Dict[str, Any]],
    seen: Set[str],
    phrase: str,
    source_type: str,
    section_id: str,
    snippet: str,
    *,
    doc_id: str = "",
    workspace_id: str = "default",
    vertical: str = "general",
    full_text: str = "",
    heading_level: int | None = None,
) -> None:
    raw = canonical_phrase(phrase)
    norm = normalized_phrase(raw)
    authority = detect_authority_clues(raw, snippet, source_type, full_text)

    if _helix_basic_reject(raw, authority):
        learn_from_pipeline_rejection(
            workspace_id=workspace_id,
            document_id=doc_id,
            vertical=vertical,
            pipeline_stage="helix_smart_extractor",
            candidate={"phrase": raw, "source_type": source_type, "section_id": section_id},
            rejection_reason="helix_smart_extractor_basic_reject",
        )
        return

    if not authority.get("authority_candidate"):
        learn_from_pipeline_rejection(
            workspace_id=workspace_id,
            document_id=doc_id,
            vertical=vertical,
            pipeline_stage="helix_smart_extractor",
            candidate={"phrase": raw, "source_type": source_type, "section_id": section_id},
            rejection_reason="helix_smart_extractor_no_authority_cue",
        )
        return

    key = f"{norm}:{section_id}"
    if key in seen:
        return
    seen.add(key)

    final_source_type = _source_type_from_category(authority.get("primary_authority_category", ""), source_type)
    toks = tokenize(raw)

    out.append({
        "phrase": raw,
        "normalized_phrase": norm,
        "source_type": final_source_type,
        "section_id": section_id,
        "doc_id": doc_id,
        "workspace_id": workspace_id,
        "vertical": vertical,
        "snippet": snippet,
        "metadata": {
            "engine": "HELIX_AUTH",
            "pipeline_stage": "helix_smart_extractor",
            "source_type": final_source_type,
            "section_id": section_id,
            "heading_level": heading_level,
        },
        "extraction_source": {
            "from_heading": source_type.startswith("heading_h"),
            "from_paragraph": source_type == "paragraph_window",
            "from_list": source_type == "list_item",
            "from_table": False,
            "heading_text": snippet if source_type.startswith("heading_h") else "",
            "snippet": snippet,
        },
        "authority_extraction": authority,
        "structure_metadata": {
            "token_count": len(toks),
            "contains_acronym": bool(ACRONYM_RE.search(raw)),
            "contains_measurement": bool(MEASUREMENT_RE.search(raw)),
            "contains_version": bool(VERSION_RE.search(raw)),
            "contains_hyphenation": "-" in raw,
            "contains_spec_identifier": bool(SPEC_RE.search(raw)),
        },
        "runtime_metadata": {
            "eligible_for_green_highlight": True,
            "eligible_for_selection_engine": True,
            "eligible_for_density_engine": True,
        },
    })


def _candidate_windows(sentence: str) -> List[str]:
    toks = tokenize(sentence)
    windows: List[str] = []

    # Initial extractor should avoid very long stitched windows.
    # Guard/scorer can later decide if longer phrases are valid.
    for n in (5, 4, 3, 2):
        if len(toks) < n:
            continue
        for i in range(0, len(toks) - n + 1):
            chunk = toks[i:i + n]
            low = [t.lower() for t in chunk]

            if _has_bad_edges(low):
                continue
            if _content_ratio(low) < 0.50:
                continue

            phrase = " ".join(chunk)

            # Avoid obvious cross-entity stitching before Guard.
            if any(t in {"and", "or", "but", "are", "is", "was", "were"} for t in low[1:-1]):
                continue

            auth = detect_authority_clues(phrase, sentence, "paragraph_window", sentence)
            if not auth.get("authority_candidate"):
                continue

            # Require one hard authority signal OR strong authority confidence.
            hard = {
                "standards_spec_id", "protocol_format", "regulatory_governance",
                "measurement_authority", "formal_identifier",
                "scientific_medical_morphology", "library_tool_product",
                "evidence_citation_intent", "technical_architecture",
                "research_study_trial"
            }
            if not (hard.intersection(set(auth.get("matched_clues", []))) or auth.get("authority_confidence", 0.0) >= 0.45):
                continue

            windows.append(phrase)

    return windows


def extract_helix_authority_phrases(
    *,
    text: str = "",
    html: str = "",
    title: str = "",
    doc_id: str = "",
    max_candidates: int = 500,
    workspace_id: str = "default",
    vertical: str = "general",
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    full_text = strip_tags(html) if html else text

    if title:
        _add_helix_candidate(
            out, seen, title, "title", "title_0", title,
            doc_id=doc_id, workspace_id=workspace_id, vertical=vertical,
            full_text=full_text, heading_level=None,
        )

    for h in extract_headings_and_lists(html):
        _add_helix_candidate(
            out, seen,
            h.get("phrase") or "",
            h.get("source_type") or "heading",
            h.get("section_id") or "heading_0",
            h.get("snippet") or "",
            doc_id=doc_id, workspace_id=workspace_id, vertical=vertical,
            full_text=full_text, heading_level=h.get("heading_level"),
        )

    paragraphs = extract_paragraphs(html=html, text=text)

    for pi, para in enumerate(paragraphs):
        for si, sent in enumerate(split_sentences(para)):
            section_id = f"p{pi}_s{si}"
            for win in _candidate_windows(sent):
                _add_helix_candidate(
                    out, seen, win, "paragraph_window", section_id, sent,
                    doc_id=doc_id, workspace_id=workspace_id, vertical=vertical,
                    full_text=full_text, heading_level=None,
                )
                if len(out) >= max_candidates:
                    return out[:max_candidates]

    return out[:max_candidates]
