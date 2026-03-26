import re, urllib.request
from backend.app.routers.site_reader import ARTICLE_EXCLUDE_RE, _parse_sitemap_urls

sm = "https://prettiereveryday.com/sitemap.xml"
req = urllib.request.Request(sm, headers={"User-Agent":"LinkCraftorSiteSync/1.0"})
xml_main = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")

locs = _parse_sitemap_urls(xml_main)
child = [u for u in locs if str(u).lower().endswith(".xml")]

final = []
if child:
    seen=set()
    for sm2 in child:
        sm2 = (sm2 or "").strip()
        if not sm2 or sm2 in seen: 
            continue
        seen.add(sm2)
        try:
            req2 = urllib.request.Request(sm2, headers={"User-Agent":"LinkCraftorSiteSync/1.0"})
            xml_child = urllib.request.urlopen(req2, timeout=30).read().decode("utf-8", errors="replace")
            final += _parse_sitemap_urls(xml_child)
        except Exception:
            pass
else:
    final = locs

kept=[]
excluded=[]
for u in final:
    u = (u or "").strip()
    if not u: 
        continue
    u = u.split("#",1)[0]
    if ARTICLE_EXCLUDE_RE.search(u):
        excluded.append(u)
    else:
        kept.append(u)

print("TOTAL", len(final))
print("KEPT", len(kept))
print("EXCLUDED", len(excluded))
print("\nEXCLUDED_SAMPLE")
for u in excluded[:30]:
    print(u)
print("\nKEPT_SAMPLE")
for u in kept[:30]:
    print(u)
