from __future__ import annotations

from typing import Any, Dict, List


BOILERPLATE_RULES_V1 = {

    "navigation":[
        "get the app",
        "topics",
        "see all",
        "community",
        "registry",
        "baby names",
        "product reviews",
    ],

    "recommended_reading":[
        "recommended reading",
        "you may also like",
        "related articles",
        "more articles",
        "read more",
    ],

    "tools":[
        "calculator",
        "due date calculator",
        "ovulation calculator",
        "conception calculator",
    ],

    "advertisement":[
        "advertisement",
        "sponsored",
        "ad choices",
    ],

    "footer":[
        "privacy policy",
        "terms of use",
        "copyright",
        "all rights reserved",
    ],

    "newsletter":[
        "sign up",
        "subscribe",
        "newsletter",
    ],
}


def detect_boilerplate_sections_v1(
    text: str,
) -> List[Dict[str, Any]]:

    findings = []

    lower = str(text or "").lower()

    for section_type, phrases in BOILERPLATE_RULES_V1.items():

        for phrase in phrases:

            idx = lower.find(phrase.lower())

            if idx >= 0:

                findings.append({

                    "section_type": section_type,

                    "trigger": phrase,

                    "offset": idx,

                })

    findings.sort(key=lambda x: x["offset"])

    return findings


def explain_boilerplate_detector_v1():

    return {

        "engine":"article_boilerplate_detector_v1",

        "detects":[
            "navigation",
            "recommended_reading",
            "tools",
            "advertisement",
            "footer",
            "newsletter",
        ],

        "result":"ordered_detection_list",

    }
