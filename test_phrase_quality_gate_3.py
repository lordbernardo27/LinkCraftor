from backend.server.stores.phrase_quality_gate import classify_phrase_strength

samples = [
    # Different medical niches
    "eczema treatment cream",
    "asthma inhaler dosage",
    "kidney stone symptoms",
    "migraine prevention tips",
    "depression therapy options",
    "adhd medication side effects",
    "cholesterol lowering foods",
    "tooth infection antibiotics",

    # Real estate
    "home buying checklist",
    "rental property investment",
    "commercial lease agreement",
    "property tax calculator",

    # Legal
    "personal injury lawyer",
    "divorce settlement agreement",
    "employment contract review",
    "immigration visa application",

    # Food / restaurant
    "best pizza delivery",
    "vegan meal prep",
    "restaurant reservation system",
    "coffee shop menu pricing",

    # AI / software
    "ai chatbot integration",
    "machine learning pipeline",
    "crm automation software",
    "cybersecurity risk assessment",

    # Weak phrases
    "this can happen",
    "many users say",
    "the result depends",
    "with more things",
    "people often ask",
    "better for you",
]

for p in samples:
    r = classify_phrase_strength(p, source_type="noun_phrase", vertical="general")
    print(f"{p:35} keep={r['keep']} strength={r['strength']} score={r['score']} reason={r['reason']}")
