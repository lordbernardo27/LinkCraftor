from backend.server.engine.intelligence_target_resolver import resolve_intelligent_targets
import json

ws = "ws_whattoexpect_com"

phrases = [
    "cervical mucus for ovulation",
    "reverse to avoid pregnancy",
    "period up to ovulation",
    "fertile window begins",
]

for phrase in phrases:
    print("\n" + "="*90)
    print("PHRASE:", phrase)
    print("="*90)

    results = resolve_intelligent_targets(
        ws,
        phrase,
        limit=10,
    )

    print(json.dumps(results, indent=2, ensure_ascii=False))
