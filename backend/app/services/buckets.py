from typing import Dict, Set
from .textops import norm

def normalize_buckets(buckets: Dict) -> Dict[str, Set[str]]:
    out = {"strong": set(), "optional": set(), "external": set()}
    for k in out.keys():
        for w in buckets.get(k, []) or []:
            n = norm(w)
            if n: out[k].add(n)
    return out
