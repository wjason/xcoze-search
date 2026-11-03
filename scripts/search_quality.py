"""Conservative mismatch detection for experimental scraped search responses.

Zero topic overlap is a fallback signal, never a quality score or fact check.
Experimental HTML/RSS/browser backends use it; semantic APIs may return synonyms.
Chinese literal-overlap checks are opt-in for browser results only.
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


def obvious_mismatch(query, rows, *, include_cjk=False):
    terms = topic_terms(query)
    if not rows: return False
    text = " ".join(str(row.get(k) or "") for row in rows
                    for k in ("title", "url", "snippet", "summary", "content"))
    if len(terms) < 2:
        if not include_cjk: return False
        # Browser-only fallback signal, not semantic ranking. Remove common task
        # instructions before looking for any literal Chinese topic bigram.
        topic = re.sub(r"最新|最近|近期|官方|公告|报告|搜索|查找|查询|帮我|请问|是什么|怎么样|多少|第[一二三四]季度|年度|月份", " ", query)
        groups = re.findall(r"[\u3400-\u9fff]{2,}", topic)
        bigrams = {g[i:i+2] for g in groups for i in range(len(g)-1)}
        return len(bigrams) >= 2 and not any(term in text for term in bigrams)
    found = set(re.findall(r"[a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)*", text.casefold()))
    compact = {word.replace(".", "") for word in found}
    return not any(term in found or term.replace(".", "") in compact for term in terms)
