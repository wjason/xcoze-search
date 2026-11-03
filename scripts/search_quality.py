"""Conservative mismatch detection for experimental scraped search responses.

Zero topic overlap is a fallback signal, never a quality score or fact check.
Experimental HTML/RSS/browser backends use it; semantic APIs may return synonyms.
Strict literal checks apply only to experimental public search, never semantic APIs.
"""
import re

STOP = frozenset("a an the and or of to in on for from by with is are was were be how what which when "
                 "does do can will would should as at it its this that these those find search web "
                 "official latest current documentation docs version release stable "
                 "january february march april may june july august september october november december".split())


def topic_terms(query):
    query = re.sub(r"(?:-?site|after|before|lang):\S+", " ", query, flags=re.I)
    words = re.findall(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*", query.casefold())
    words = {w for w in words if len(w) >= 3 and w not in STOP}
    return words


def focus_terms(query):
    query = re.sub(r"(?:-?site|after|before|lang):\S+", " ", query, flags=re.I)
    words = re.findall(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)*", query)
    return {w.casefold() for w in words if '_' in w or '.' in w or
            re.search(r"[a-z][A-Z][a-z]|[A-Za-z][0-9]", w)}


def obvious_mismatch(query, rows, *, include_cjk=False, require_focus=False):
    terms = topic_terms(query)
    if not rows: return False
    text = " ".join(str(row.get(k) or "") for row in rows
                    for k in ("title", "url", "snippet", "summary", "content"))
    if require_focus:
        focus = focus_terms(query)
        compact_text = re.sub(r"[._]", "", text.casefold())
        if focus and not any(re.sub(r"[._]", "", term) in compact_text for term in focus): return True
        # Reject an explicit conflicting year in a single-year Chinese request.
        # Missing dates remain unknown; ranges/operators are not reinterpreted.
        years = set(re.findall(r"(20\d{2})年", query))
        observed = set(re.findall(r"(?<!\d)(20\d{2})(?!\d)", text))
        # Common public-release paths use /YYYYMM/ or /YYYYMMDD/.
        observed.update(re.findall(r"/(20\d{2})(?:0[1-9]|1[0-2])(?:[0-3]\d)?(?:[/_]|$)", text))
        if len(years) == 1 and observed and years.isdisjoint(observed): return True
        months = set(re.findall(r"20\d{2}年(\d{1,2})月", query))
        dated_months = set(re.findall(r"20\d{2}年(\d{1,2})月", text))
        if len(months) == 1 and dated_months and months.isdisjoint(dated_months):
            wanted = next(iter(months))
            if not re.search(r"(?<!\d)" + wanted + r"月份?", text): return True
        if '前三季度' in query and '前三季度' not in text and re.search(r'上半年|前两季度|第一季度|一季度', text): return True
    if len(terms) < 2:
        if not include_cjk: return False
        # Literal fallback signal, not semantic ranking. Remove common task
        # instructions before looking for any literal Chinese topic bigram.
        topic = re.sub(r"最新|最近|近期|官方|公告|报告|搜索|查找|查询|帮我|请问|是什么|怎么样|多少|第[一二三四]季度|年度|月份", " ", query)
        groups = re.findall(r"[\u3400-\u9fff]{2,}", topic)
        bigrams = {g[i:i+2] for g in groups for i in range(len(g)-1)}
        return len(bigrams) >= 2 and not any(term in text for term in bigrams)
    found = set(re.findall(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*", text.casefold()))
    compact = {re.sub(r"[._]", "", word) for word in found}
    return not any(term in found or re.sub(r"[._]", "", term) in compact for term in terms)


def filter_experimental(query, rows):
    kept = [row for row in rows if not obvious_mismatch(query, [row], include_cjk=True, require_focus=True)]
    return kept, len(rows) - len(kept)
