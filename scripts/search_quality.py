"""Conservative mismatch detection for experimental scraped search responses.

Zero topic overlap is a fallback signal, never a quality score or fact check.
Only experimental HTML/RSS backends use it; semantic APIs may return synonyms.
"""
import re

STOP = frozenset("a an the and or of to in on for from by with is are was were be how what which when "
                 "does do can will would should as at it its this that these those find search web "
                 "official latest current documentation docs version release stable "
                 "january february march april may june july august september october november december".split())


def topic_terms(query):
    query = re.sub(r"(?:-?site|after|before|lang):\S+", " ", query, flags=re.I)
    words = re.findall(r"[a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)*", query.casefold())
    words = {w for w in words if len(w) >= 3 and w not in STOP}
    return words


def obvious_mismatch(query, rows):
    terms = topic_terms(query)
    if len(terms) < 2 or not rows:
        return False
    text = " ".join(str(row.get(k) or "") for row in rows
                    for k in ("title", "url", "snippet", "summary", "content"))
    found = set(re.findall(r"[a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)*", text.casefold()))
    compact = {word.replace(".", "") for word in found}
    return not any(term in found or term.replace(".", "") in compact for term in terms)
