from ..services.textops import content_ratio, tokens

def score_anchor(anchor: str, full_text: str) -> float:
    t = tokens(anchor)
    cr = content_ratio(t)
    # simple TF bump
    tf = full_text.lower().count(anchor.lower())
    tf_norm = min(1.0, tf / 3.0)
    return 0.6 * cr + 0.4 * tf_norm
