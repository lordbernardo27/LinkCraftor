from __future__ import annotations

import re


def fix_mojibake_text(s: str) -> str:
    s = str(s or "")
    if not s:
        return ""

    replacements = {
        "â€™": "'",
        "â€˜": "'",
        "â€œ": '"',
        "â€": '"',
        "â€“": "-",
        "â€”": "-",
        "â€¦": "...",
        "Â ": " ",
        "Â": "",
        "Ã©": "é",
        "Ã¨": "è",
        "Ãª": "ê",
        "Ã«": "ë",
        "Ã¡": "á",
        "Ã ": "à",
        "Ã¢": "â",
        "Ã¤": "ä",
        "Ã­": "í",
        "Ã¬": "ì",
        "Ã®": "î",
        "Ã¯": "ï",
        "Ã³": "ó",
        "Ã²": "ò",
        "Ã´": "ô",
        "Ã¶": "ö",
        "Ãº": "ú",
        "Ã¹": "ù",
        "Ã»": "û",
        "Ã¼": "ü",
        "Ã±": "ñ",
        "Ã§": "ç",
        "\u2019": "'",
        "\u2018": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }

    for bad, good in replacements.items():
        s = s.replace(bad, good)

    try:
        if any(x in s for x in ("â", "Â", "Ã")):
            repaired = s.encode("latin1", errors="ignore").decode("utf-8", errors="ignore").strip()
            if repaired:
                s = repaired
    except Exception:
        pass

    s = s.replace("â€¦", "...")
    s = s.replace("â€“", "-")
    s = s.replace("â€”", "-")

    s = re.sub(r"\s+", " ", s).strip()
    return s