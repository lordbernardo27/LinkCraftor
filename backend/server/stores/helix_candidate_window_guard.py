from __future__ import annotations

import re
from typing import Any, Dict, List, Set

try:
    from backend.server.stores.dis_pipeline_learning import learn_from_pipeline_rejection
except Exception:
    def learn_from_pipeline_rejection(**kwargs):
        return None


WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9\.\-_/]*")

STOPWORDS: Set[str] = {
    "the","and","for","with","that","this","from","into","your","you",
    "are","was","were","will","can","could","should","would","have",
    "has","had","about","over","under","than","then","when","what",
    "where","which","who","why","how","a","an","to","of","in","on",
    "at","by","or","as","is","it","be","not","no","if","but","so",
    "because","after","before","during","while","through","up","down",
    "out","off","too","very","also"
}

BAD_STARTS = {
    "same","another","many","several","various","different","this","that",
    "these","those","keep","using","during","around","about","because",
    "unless","while","before","after","with","without","for","to","from",
    "into","a","an","the"
}

BAD_ENDS = {
    "around","during","before","after","unless","because","using","used",
    "show","shows","help","helps","determine","determines","improve",
    "improves","minus","plus","with","for","to","from","into","are","is",
    "was","were","be","been","being","and","or","but","a","an","the","of"
}

NARRATIVE_TAILS = {
    "show","shows","help","helps","determine","determines","improve",
    "improves","using","used","because","unless","around","during",
    "before","after","while","minus","plus","conversation","example",
    "examples","tends","often","may","land","lands","fall","falls",
    "happen","happens"
}

WEAK_GENERIC_TERMS = {
    "healthy","simple","basic","easy","common","general","regular","normal",
    "different","important","helpful","shared","plain","english","guide",
    "timeline","care","routine","method","methods","way","ways"
}

AUTHORITY_HEADS = {
    "framework","standard","standards","specification","protocol","policy",
    "regulation","compliance","governance","audit","certification","guideline",
    "model","methodology","architecture","schema","algorithm","analysis",
    "trial","study","review","report","survey","index","rate","ratio","risk",
    "yield","token","api","sla","encryption","dosage","regimen","phase",
    "cycle","count","length","semantics","calculator","transfer","lmp",
    "ovulation"
}

MEASUREMENT_RE = re.compile(
    r"\b\d+(?:\.\d+)?(?:\s|-)?(?:mg|mcg|g|kg|ml|l|mmhg|ms|gb|mb|tb|bit|bits|day|days|week|weeks|month|months|year|years|%)\b",
    re.I,
)
SPEC_RE = re.compile(
    r"\b(?:ISO(?:/IEC)?|IEC|NIST|PCI\s*DSS|SOC\s*2|SOC\s*1|RFC|IEEE|WCAG|FIPS|EN|BSI|ETSI)\s*[-:]?\s*\d{1,6}(?:[:\-.]\d+)?\b",
    re.I,
)
ACRONYM_RE = re.compile(r"\b[A-Z]{2,}(?:\s*\d+)?\b")
VERSION_RE = re.compile(r"\b(?:v(?:er(?:sion)?)?\.?\s*)?\d+(?:\.\d+)+\b", re.I)

QUALITY_GATE_WEIGHTS = {
    "logical_structure": 0.25,
    "authority_integrity": 0.25,
    "boundary_quality": 0.20,
    "canonical_span": 0.20,
    "noise_control": 0.10,
}


def tokenize(text: str) -> List[str]:
    return WORD_RE.findall(str(text or ""))


def _clamp(v: float) -> float:
    return max(0.0, min(1.0, round(float(v), 4)))


def _content_ratio(tokens: List[str]) -> float:
    if not tokens:
        return 0.0
    return len([t for t in tokens if t.lower() not in STOPWORDS]) / max(1, len(tokens))


def _quality(signals: Dict[str, float]) -> Dict[str, Any]:
    score = 0.0
    for k, w in QUALITY_GATE_WEIGHTS.items():
        score += float(signals.get(k, 0.0)) * w
    score = _clamp(score)
    return {
        "quality_gate_score": score,
        "decision": "ACCEPT" if score >= 0.75 else "REVIEW" if score >= 0.60 else "REJECT",
        "signals": signals,
    }


def _reject(
    phrase: str,
    reason: str,
    *,
    workspace_id: str = "default",
    document_id: str = "",
    vertical: str = "general",
    authority: Dict[str, Any] | None = None,
    signals: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    learn_from_pipeline_rejection(
        workspace_id=workspace_id,
        document_id=document_id,
        vertical=vertical,
        pipeline_stage="helix_candidate_window_guard",
        candidate={"phrase": phrase, "authority": authority or {}},
        rejection_reason=reason,
    )
    return {
        "keep": False,
        "phrase": phrase,
        "reason": reason,
        "quality_gate": _quality(signals or {
            "logical_structure": 0.25,
            "authority_integrity": 0.25,
            "boundary_quality": 0.20,
            "canonical_span": 0.20,
            "noise_control": 0.20,
        }),
    }


def _accept(phrase: str, reason: str = "helix_guard_pass") -> Dict[str, Any]:
    return {
        "keep": True,
        "phrase": phrase,
        "reason": reason,
        "quality_gate": _quality({
            "logical_structure": 0.90,
            "authority_integrity": 0.90,
            "boundary_quality": 0.85,
            "canonical_span": 0.85,
            "noise_control": 0.85,
        }),
    }


def _hard_authority_clues(authority: Dict[str, Any]) -> Set[str]:
    return set(authority.get("matched_clues") or []).intersection({
        "standards_spec_id",
        "protocol_format",
        "regulatory_governance",
        "measurement_authority",
        "formal_identifier",
        "scientific_medical_morphology",
        "library_tool_product",
        "technical_architecture",
        "research_study_trial",
        "certification_accreditation",
        "legal_case_reference",
        "statistical_data_pattern",
    })


def _has_bad_boundary(tokens: List[str]) -> str:
    if not tokens:
        return "helix_empty_candidate"
    low = [t.lower() for t in tokens]
    if low[0] in BAD_STARTS:
        return "helix_bad_start_boundary"

    if low[0] in {"assuming", "calculate"}:
        return "helix_calculation_wrapper"
    if low[-1] in BAD_ENDS:
        return "helix_bad_end_boundary"

    if low[-1] in {"subtract", "calculate", "assuming", "expected"}:
        return "helix_calculation_tail_leak"

    if any(t in {"because", "unless"} for t in low[1:-1]):
        return "helix_clause_connector_leak"

    if any(t in {"subtract", "expected"} for t in low[1:-1]):
        return "helix_calculation_phrase_leak"
    if low[-1] in NARRATIVE_TAILS:
        return "helix_narrative_tail"
    if any(t in {"are","is","was","were","helps","shows","reveals","contains","depends"} for t in low[1:-1]):
        return "helix_clause_boundary_leak"
    return ""


def _is_weak_generic_phrase(tokens: List[str], authority: Dict[str, Any]) -> bool:
    low = [t.lower() for t in tokens]
    if _hard_authority_clues(authority):
        return False
    if authority.get("authority_confidence", 0.0) >= 0.50:
        return False
    hits = sum(1 for t in low if t in WEAK_GENERIC_TERMS)
    return hits >= 2 or (len(low) <= 3 and hits >= 1)


def _has_authority_collision(tokens: List[str], authority: Dict[str, Any]) -> bool:
    phrase = " ".join(tokens)
    low_phrase = phrase.lower()
    clues = set(authority.get("matched_clues") or [])

    if len(clues.intersection({"standards_spec_id", "measurement_authority", "regulatory_governance", "protocol_format"})) >= 2:
        if any(x in low_phrase for x in [" and ", " with ", " before ", " after ", " during "]):
            return True

    if len(MEASUREMENT_RE.findall(phrase)) >= 2:
        return True

    if len(ACRONYM_RE.findall(phrase)) >= 3:
        return True

    return False


def _is_incomplete_measurement_structure(phrase: str, tokens: List[str]) -> bool:
    low = [t.lower() for t in tokens]
    if not MEASUREMENT_RE.search(phrase):
        return False

    if len(tokens) <= 2:
        return True

    if low[-1] in {"minus","plus","around","tends","often","may","land","lands","fall","falls","happens"}:
        return True

    valid_heads = {"phase","cycle","count","length","regimen","dosage","sla","rate","ratio","yield","lmp","ovulation"}
    if not any(t in valid_heads for t in low):
        return True

    return False


def _is_incomplete_standard_structure(phrase: str, tokens: List[str]) -> bool:
    if not SPEC_RE.search(phrase):
        return False
    low = [t.lower() for t in tokens]
    if low[-1] in {"http","type","compliance","wireless","cybersecurity"}:
        return True
    return False


def _canonical_trim_candidate(phrase: str) -> str:
    s = str(phrase or "").strip()
    trim_patterns = [
        (r"^\b(?:same|the same|a|an|the)\s+", ""),
        (r"\s+\b(?:minus|plus|around|often|tends|may|land|lands|fall|falls|happens|show|shows)$", ""),
        (r"\s+\b(?:unless later|a conversation)$", ""),
    ]
    for pat, repl in trim_patterns:
        s = re.sub(pat, repl, s, flags=re.I).strip()
    return s


def helix_candidate_window_guard(
    candidate: str | Dict[str, Any],
    *,
    source_type: str = "",
    workspace_id: str = "default",
    document_id: str = "",
    vertical: str = "general",
) -> Dict[str, Any]:
    if isinstance(candidate, dict):
        raw_phrase = str(candidate.get("phrase") or "")
        authority = dict(candidate.get("authority_extraction") or {})
        source_type = source_type or str(candidate.get("source_type") or "")
        document_id = document_id or str(candidate.get("doc_id") or "")
        workspace_id = workspace_id or str(candidate.get("workspace_id") or "default")
        vertical = vertical or str(candidate.get("vertical") or "general")
    else:
        raw_phrase = str(candidate or "")
        authority = {}

    raw_phrase = " ".join(tokenize(raw_phrase))
    if not raw_phrase:
        return _reject("", "helix_empty_candidate", workspace_id=workspace_id, document_id=document_id, vertical=vertical, authority=authority)

    trimmed = _canonical_trim_candidate(raw_phrase)
    tokens = tokenize(trimmed)

    if len(tokens) < 2:
        return _reject(trimmed, "helix_too_short", workspace_id=workspace_id, document_id=document_id, vertical=vertical, authority=authority)

    if len(tokens) > 8:
        return _reject(trimmed, "helix_too_long", workspace_id=workspace_id, document_id=document_id, vertical=vertical, authority=authority)

    boundary_reason = _has_bad_boundary(tokens)
    if boundary_reason:
        return _reject(trimmed, boundary_reason, workspace_id=workspace_id, document_id=document_id, vertical=vertical, authority=authority)

    if _is_incomplete_measurement_structure(trimmed, tokens):
        return _reject(trimmed, "helix_incomplete_measurement_structure", workspace_id=workspace_id, document_id=document_id, vertical=vertical, authority=authority)

    if _is_incomplete_standard_structure(trimmed, tokens):
        return _reject(trimmed, "helix_incomplete_standard_structure", workspace_id=workspace_id, document_id=document_id, vertical=vertical, authority=authority)

    if _has_authority_collision(tokens, authority):
        return _reject(trimmed, "helix_authority_collision", workspace_id=workspace_id, document_id=document_id, vertical=vertical, authority=authority)

    if _is_weak_generic_phrase(tokens, authority):
        return _reject(trimmed, "helix_generic_information_phrase", workspace_id=workspace_id, document_id=document_id, vertical=vertical, authority=authority)

    low = [t.lower() for t in tokens]
    if _content_ratio(low) < 0.45 and not _hard_authority_clues(authority):
        return _reject(trimmed, "helix_low_content_ratio", workspace_id=workspace_id, document_id=document_id, vertical=vertical, authority=authority)

    if not _hard_authority_clues(authority) and authority.get("authority_confidence", 0.0) < 0.30:
        return _reject(trimmed, "helix_low_authority_confidence", workspace_id=workspace_id, document_id=document_id, vertical=vertical, authority=authority)

    return _accept(trimmed)
