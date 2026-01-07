# backend/app/engine/entity_map.py
from __future__ import annotations
from typing import Dict
from .entity_detection import build_entity_map as _build, normalize_entity as _norm
from .entity_fallback import wikipedia_fallback as _wk

def build_entity_map(html: str = "", text: str = "") -> Dict:
    return _build(html=html, text=text)

def normalize_entity(text: str) -> str:
    return _norm(text)

def wikipedia_fallback(anchor: str) -> Dict:
    return _wk(anchor)
