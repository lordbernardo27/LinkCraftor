from backend.server.stores.phrase_quality_gate import classify_phrase_strength

samples = [
    # 1 Fitness
    "weight loss workout plan",
    "muscle recovery supplements",

    # 2 Beauty
    "acne skincare routine",
    "hair growth serum",

    # 3 Parenting
    "newborn sleep schedule",
    "toddler behavior tips",

    # 4 Automotive
    "car insurance quotes",
    "engine oil change interval",

    # 5 Gaming
    "gaming laptop performance",
    "fps settings guide",

    # 6 Crypto
    "bitcoin price prediction",
    "crypto tax reporting",

    # 7 Fashion
    "summer dress trends",
    "men sneaker collection",

    # 8 Agriculture
    "organic fertilizer benefits",
    "maize farming guide",

    # 9 Construction
    "roof repair estimate",
    "home renovation contractor",

    # 10 HR / Careers
    "resume writing service",
    "job interview questions",

    # Weak phrases
    "this works well",
    "many buyers think",
    "the answer changes",
    "with your system",
    "people can use",
    "after this step",
]

for p in samples:
    r = classify_phrase_strength(p, source_type="noun_phrase", vertical="general")
    print(f"{p:35} keep={r['keep']} strength={r['strength']} score={r['score']} reason={r['reason']}")
