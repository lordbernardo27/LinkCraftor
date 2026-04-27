# test_phrase_quality_gate_passage.py

from backend.server.stores.phrase_quality_gate import classify_phrase_strength

passages = {
    "health": """
    Blood pressure medication can help manage hypertension. Some people ask whether the answer depends on age.
    A strong article may discuss type 2 diabetes symptoms, chest pain causes, and cholesterol lowering foods.
    This can happen when the topic is broad, but weak fragments should not pass.
    """,

    "saas": """
    Customer onboarding software improves activation. API rate limiting protects the platform.
    A product team may compare user authentication flow, database backup strategy, and cloud storage pricing.
    Many users say the result depends, but those are weak fragments.
    """,

    "finance": """
    Dividend yield helps investors compare income stocks. Mortgage interest rate affects monthly payments.
    A finance guide may include cash flow forecast, property tax calculator, and crypto tax reporting.
    Better than before is not a useful anchor phrase.
    """,

    "legal": """
    A personal injury lawyer may review a divorce settlement agreement.
    Legal content can cover employment contract review and immigration visa application.
    People often ask broad questions, but vague fragments should fail.
    """,

    "travel": """
    Airport transfer service and travel insurance coverage are useful travel topics.
    A local guide may include best hotel deals, car rental prices, and Accra restaurants near airport.
    With your system is not a meaningful phrase.
    """
}

for niche, text in passages.items():
    print(f"\n===== {niche.upper()} =====")

    # simple phrase candidates for testing only
    candidates = [
        "blood pressure medication",
        "type 2 diabetes symptoms",
        "chest pain causes",
        "cholesterol lowering foods",
        "answer depends on age",
        "this can happen",

        "customer onboarding software",
        "api rate limiting",
        "user authentication flow",
        "database backup strategy",
        "cloud storage pricing",
        "many users say",

        "dividend yield",
        "mortgage interest rate",
        "cash flow forecast",
        "property tax calculator",
        "crypto tax reporting",
        "better than before",

        "personal injury lawyer",
        "divorce settlement agreement",
        "employment contract review",
        "immigration visa application",
        "people often ask",

        "airport transfer service",
        "travel insurance coverage",
        "best hotel deals",
        "car rental prices",
        "accra restaurants near airport",
        "with your system",
    ]

    for phrase in candidates:
        if phrase.lower() in text.lower():
            r = classify_phrase_strength(
                phrase,
                source_type="noun_phrase",
                vertical=niche,
                context=text,
            )
            print(f"{phrase:35} keep={r['keep']} score={r['score']} reason={r['reason']}")
