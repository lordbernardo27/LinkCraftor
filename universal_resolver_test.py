from backend.server.engine.intelligence_target_resolver import (
    _phrase_evidence_score,
    _intent_match_score,
    _concept_alignment_score,
)

tests = [
    ("internal linking opportunities", "Advanced Internal Linking Optimization Guide"),
    ("topic cluster generator", "AI Topic Cluster Builder"),
    ("mortgage payment calculator", "Home Mortgage Calculator"),
    ("retirement savings planning", "Retirement Planning Guide"),
    ("python api integration", "Python REST API Integration Tutorial"),
    ("cloud deployment guide", "Cloud Infrastructure Deployment Guide"),
    ("product comparison guide", "Product Comparison Framework"),
    ("shipping cost calculator", "International Shipping Calculator"),
    ("machine learning tutorial", "Machine Learning Beginner Tutorial"),
    ("exam preparation checklist", "Ultimate Exam Preparation Checklist"),
]

for phrase, target in tests:
    pe = _phrase_evidence_score(phrase, target, [])
    intent = _intent_match_score(phrase, target, "")
    concept = _concept_alignment_score(phrase, target)

    print("\\n" + "=" * 80)
    print("PHRASE :", phrase)
    print("TARGET :", target)
    print("PHRASE_EVIDENCE:", pe.get("phrase_evidence_score"))
    print("OVERLAP_COUNT :", pe.get("phrase_overlap_count"))
    print("INTENT_SCORE :", intent)
    print("CONCEPT_ALIGNMENT :", concept.get("concept_alignment_score"))
    print("OVERLAP_TERMS :", concept.get("concept_overlap_terms"))
