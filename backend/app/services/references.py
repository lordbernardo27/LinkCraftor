# Simple stub that returns Wikipedia heuristics.
# Replace later with your real providers (SerpAPI, Bing, custom index, etc.)
from typing import List, Dict

def wikipedia_hint(title: str) -> Dict:
    slug = title.strip().replace(" ", "_")
    return {
        "title": title,
        "url": f"https://en.wikipedia.org/wiki/{slug}",
        "provider": "Wikipedia",
        "score": 0.7
    }

def get_external_references(anchor: str, limit: int = 8) -> List[Dict]:
    # TODO: plug real search here
    return [wikipedia_hint(anchor)]
