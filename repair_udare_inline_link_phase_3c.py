from __future__ import annotations

import ast
from pathlib import Path


path = Path(
    "backend/server/stores/udare_article_document_builder.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)


# =====================================================================
# 1. ADD COMPARISON-ONLY PUNCTUATION NORMALIZATION
# =====================================================================

if "def _comparison_text(" not in text:
    marker = '''def _visible_text(
    html_text: str,
) -> str:
'''

    helper = '''def _comparison_text(
    value: Any,
) -> str:
    """
    Normalize text only for wording-integrity comparisons.

    HTML parsing can split inline markup into separate text nodes and
    introduce an artificial space before punctuation, for example:

        link</a>.  ->  link .

    This helper removes only those parser-created punctuation spaces.
    It does not change the rendered or stored article document.
    """

    normalized = _normalized_text(
        value
    )

    normalized = re.sub(
        r"\\s+([,.;:!?%…\\)\\]\\}])",
        r"\\1",
        normalized,
    )

    normalized = re.sub(
        r"([\\(\\[\\{])\\s+",
        r"\\1",
        normalized,
    )

    return normalized


'''

    if marker not in text:
        raise RuntimeError(
            "_visible_text insertion marker was not found."
        )

    text = text.replace(
        marker,
        helper + marker,
        1,
    )


# =====================================================================
# 2. REPAIR INLINE-SEGMENT WORDING COMPARISON
# =====================================================================

old_inline_comparison = '''    if (
        _normalized_text(
            rendered_visible
        )
        != _normalized_text(
            fallback_text
        )
    ):
'''

new_inline_comparison = '''    if (
        _comparison_text(
            rendered_visible
        )
        != _comparison_text(
            fallback_text
        )
    ):
'''

if old_inline_comparison in text:
    text = text.replace(
        old_inline_comparison,
        new_inline_comparison,
        1,
    )

elif new_inline_comparison not in text:
    raise RuntimeError(
        "Inline wording comparison block was not found."
    )


# =====================================================================
# 3. REPAIR BLOCK-LEVEL WORDING COMPARISON
# =====================================================================

old_expected_block_text = '''    expected_text = _normalized_text(
        block.get(
            "text"
        )
    )
'''

new_expected_block_text = '''    expected_text = _comparison_text(
        block.get(
            "text"
        )
    )
'''

if old_expected_block_text in text:
    text = text.replace(
        old_expected_block_text,
        new_expected_block_text,
        1,
    )

elif new_expected_block_text not in text:
    raise RuntimeError(
        "Block expected-text comparison was not found."
    )


old_actual_block_comparison = '''            _normalized_text(
                actual_text
            )
            != expected_text
'''

new_actual_block_comparison = '''            _comparison_text(
                actual_text
            )
            != expected_text
'''

if old_actual_block_comparison in text:
    text = text.replace(
        old_actual_block_comparison,
        new_actual_block_comparison,
        1,
    )

elif new_actual_block_comparison not in text:
    raise RuntimeError(
        "Block actual-text comparison was not found."
    )


# =====================================================================
# 4. REPAIR FINAL DOCUMENT WORDING COMPARISON
# =====================================================================

old_article_body_comparison = '''    expected_article_body = (
        _normalized_text(
            reconstruction.get(
                "article_body"
            )
        )
    )
'''

new_article_body_comparison = '''    expected_article_body = (
        _comparison_text(
            reconstruction.get(
                "article_body"
            )
        )
    )
'''

if old_article_body_comparison in text:
    text = text.replace(
        old_article_body_comparison,
        new_article_body_comparison,
        1,
    )

elif new_article_body_comparison not in text:
    raise RuntimeError(
        "Final expected article-body comparison was not found."
    )


old_final_condition = '''        expected_article_body
        and rendered_visible_text
        != expected_article_body
'''

new_final_condition = '''        expected_article_body
        and _comparison_text(
            rendered_visible_text
        )
        != expected_article_body
'''

if old_final_condition in text:
    text = text.replace(
        old_final_condition,
        new_final_condition,
        1,
    )

elif new_final_condition not in text:
    raise RuntimeError(
        "Final rendered-text comparison was not found."
    )


# =====================================================================
# 5. VERIFY SYNTAX BEFORE WRITING
# =====================================================================

ast.parse(
    text,
    filename=str(
        path
    ),
)

path.write_text(
    text,
    encoding="utf-8",
)


print(
    "INLINE PUNCTUATION COMPARISON REPAIR: PASS"
)

print(
    "Rendered HTML remains unchanged."
)

print(
    "Only wording-integrity comparisons were corrected."
)
