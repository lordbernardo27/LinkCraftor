from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

_SEED_SYNONYM_GROUPS: List[List[str]] = [
    ["high blood pressure", "hypertension", "elevated blood pressure"],
    ["heart attack", "myocardial infarction"],
    ["liver damage", "hepatotoxicity"],
    ["blood sugar", "glucose", "blood glucose"],
    ["acid reflux", "gerd", "heartburn"],
    ["kidney stones", "renal calculi"],
    ["scaling problems", "scalability issues", "system scalability", "system scalability issues", "difficult to scale"],
    ["website ranking", "google ranking", "search ranking", "rank on google"],
    ["cash flow problems", "negative cash flow", "cash flow issues"],
    ["data breach", "security incident", "data leak"],
    ["customer churn", "customer attrition", "user churn"],
]

_ONTOLOGY_RULES: Dict[str, Set[str]] = {
    "medical_condition": {"hypertension", "pressure", "diabetes", "disease", "condition", "osteoporosis", "fractures", "pain", "deficiency", "reflux", "gerd", "stones", "renal", "cardiac", "infarction", "hepatotoxicity"},
    "medication_topic": {"amlodipine", "medication", "medications", "drug", "drugs", "dose", "dosage", "therapy", "treatment"},
    "business_finance": {"cash", "flow", "revenue", "profit", "profits", "sales", "expenses", "costs", "capital", "financial", "finance", "budget", "forecast", "forecasts"},
    "legal_compliance": {"legal", "law", "laws", "regulation", "regulations", "compliance", "copyright", "trademark", "trademarks", "contract", "contracts", "liability", "lease", "agreement"},
    "seo_search": {"seo", "ranking", "rank", "google", "search", "traffic", "articles", "content", "keywords", "website", "websites", "backlinks"},
    "technology_scaling": {"system", "systems", "technology", "scaling", "scale", "scalability", "infrastructure", "performance", "latency", "architecture", "breach", "security", "incident"},
    "ecommerce_operations": {"ecommerce", "stores", "store", "inventory", "checkout", "conversion", "cart", "customers", "orders", "products", "churn"},
    "travel_topic": {"hotel", "flight", "flights", "booking", "itinerary", "destination", "visa", "rental", "trip", "travel"},
}

_CONFIDENCE_CURATED = 0.95
_OVERRIDE_GROUPS: Dict[str, List[List[str]]] = {}


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def _tokens(value: Any) -> Set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", str(value or "").lower()) if len(t) >= 3}


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    return here.parents[1] / "data"


def _map_path(workspace_id: str) -> Path:
    ws = str(workspace_id or "default").strip() or "default"
    return _data_dir() / "semantic" / f"semantic_map_{ws}.json"


def _seed_map() -> Dict[str, Any]:
    return {
        "version": "semantic_map_v1",
        "groups": [list(g) for g in _SEED_SYNONYM_GROUPS],
    }


def load_curated_map(workspace_id: str) -> List[List[str]]:
    fp = _map_path(workspace_id)

    if not fp.exists():
        try:
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(json.dumps(_seed_map(), indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        return [list(g) for g in _SEED_SYNONYM_GROUPS]

    try:
        obj = json.loads(fp.read_text(encoding="utf-8"))
        groups = obj.get("groups") if isinstance(obj, dict) else obj
        return [[_norm(x) for x in g] for g in groups if isinstance(g, list)]
    except Exception:
        return [list(g) for g in _SEED_SYNONYM_GROUPS]


def set_curated_groups(workspace_id: str, groups: List[List[str]]) -> None:
    _OVERRIDE_GROUPS[str(workspace_id)] = [[_norm(x) for x in g] for g in groups]


def _groups(workspace_id: str) -> List[List[str]]:
    if str(workspace_id) in _OVERRIDE_GROUPS:
        return _OVERRIDE_GROUPS[str(workspace_id)]
    return load_curated_map(workspace_id)


def ontology_categories(text: Any) -> Set[str]:
    toks = _tokens(text)
    return {cat for cat, terms in _ONTOLOGY_RULES.items() if toks & terms}


def same_ontology(a: Any, b: Any) -> bool:
    ca = ontology_categories(a)
    cb = ontology_categories(b)

    if not ca or not cb:
        return True

    return bool(ca & cb)


def get_semantic_links(workspace_id: str, phrase: str) -> List[Tuple[str, float, str]]:
    p = _norm(phrase)

    if not p:
        return []

    out: List[Tuple[str, float, str]] = []
    seen: Set[str] = set()

    for group in _groups(workspace_id):
        if p in group:
            for term in group:
                if term != p and term not in seen:
                    seen.add(term)
                    out.append((term, _CONFIDENCE_CURATED, "curated_synonym"))

    return out


def semantic_target_match(workspace_id: str, phrase: str, target_text: str) -> Dict[str, Any]:
    target_norm = _norm(target_text)
    target_tokens = _tokens(target_text)

    if not target_norm:
        return {
            "matched": False,
            "confidence": 0.0,
            "via": "",
            "reason": "empty_target",
        }

    for term, conf, reason in get_semantic_links(workspace_id, phrase):
        term_tokens = _tokens(term)
        literal = term in target_norm or bool(term_tokens and term_tokens <= target_tokens)

        if not literal:
            continue

        if not same_ontology(phrase, target_text):
            continue

        return {
            "matched": True,
            "confidence": round(conf, 4),
            "via": term,
            "reason": f"{reason}:{term}",
            "phrase_categories": sorted(ontology_categories(phrase)),
            "target_categories": sorted(ontology_categories(target_text)),
        }

    return {
        "matched": False,
        "confidence": 0.0,
        "via": "",
        "reason": "no_synonym_in_target",
    }


def semantic_source_healthcheck() -> Dict[str, Any]:
    return {
        "ok": True,
        "engine": "semantic_source",
        "version": "v1_real",
        "seed_groups": len(_SEED_SYNONYM_GROUPS),
        "ontology_categories": len(_ONTOLOGY_RULES),
    }
