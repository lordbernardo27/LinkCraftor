from backend.server.stores.phrase_quality_gate import classify_phrase_strength

samples = [
    "customer onboarding software",
    "api rate limiting",
    "cloud storage pricing",
    "user authentication flow",
    "database backup strategy",
    "product return policy",
    "shopify checkout optimization",
    "abandoned cart recovery",
    "customer lifetime value",
    "dividend yield",
    "mortgage interest rate",
    "cash flow forecast",
    "football transfer window",
    "player injury report",
    "match performance analysis",
    "routine rather than monthly",
    "whether your goal",
    "guesswork into predictable",
    "period tools do this",
    "cycle length end up",
    "the customer can",
    "from the platform",
    "this is important",
    "rather than before",
    "how to",
]

for p in samples:
    r = classify_phrase_strength(p, source_type="noun_phrase", vertical="general")
    print(f"{p:35} keep={r['keep']} strength={r['strength']} score={r['score']} reason={r['reason']}")
