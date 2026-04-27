from backend.server.stores.phrase_quality_gate import classify_phrase_strength

samples = [
    # Health
    "blood pressure medication",
    "type 2 diabetes symptoms",
    "ovulation predictor kits",
    "fertility treatment options",
    "chest pain causes",

    # Local business / travel
    "best hotel deals",
    "airport transfer service",
    "accra restaurants near airport",
    "car rental prices",
    "travel insurance coverage",

    # Marketing / SEO
    "keyword research tool",
    "backlink audit software",
    "conversion rate optimization",
    "seo content strategy",
    "landing page design",

    # Education
    "online math tutoring",
    "study time management",
    "science fair project ideas",
    "coding interview practice",

    # Weak phrases
    "this helps you",
    "can be useful",
    "the answer depends",
    "with the system",
    "after that it",
    "many people ask",
    "thing for users",
    "better than before",
]

for p in samples:
    r = classify_phrase_strength(p, source_type="noun_phrase", vertical="general")
    print(f"{p:35} keep={r['keep']} strength={r['strength']} score={r['score']} reason={r['reason']}")
