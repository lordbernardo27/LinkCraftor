# placeholder for your server-side category sets / recognizers
EXTERNAL_CATEGORY_WHITELIST = [
    "standards", "regulatory", "protocols", "libraries", "products", "medical"
]
EXTERNAL_CATEGORY_SET = set(s.lower() for s in EXTERNAL_CATEGORY_WHITELIST)
