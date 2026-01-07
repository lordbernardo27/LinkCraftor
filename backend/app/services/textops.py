import re
from typing import List

RX_WORD = re.compile(r"[\w’'-]+", re.UNICODE)

def norm(s: str) -> str:
    return " ".join((s or "").lower().split())

def tokens(s: str) -> List[str]:
    return RX_WORD.findall((s or "").lower())

def content_ratio(tok: List[str]) -> float:
    if not tok: return 0.0
    stops = {"the","a","an","to","of","in","on","for","and","or","by","with","vs"}
    good = [t for t in tok if t not in stops and len(t) >= 4]
    return len(good) / max(1, len(tok))

def boundary_rx(phrase: str) -> re.Pattern:
    esc = re.escape(phrase).replace(r"\ ", r"\s+")
    return re.compile(rf"(^|[^\w])({esc})(?=$|[^\w])", re.IGNORECASE | re.UNICODE)
