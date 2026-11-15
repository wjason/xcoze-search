# Official documentation search

[简体中文](documentation.md) | **English**

For APIs, parameters and usage, search official documentation directly:

| Documentation | Platform | Method | Scope |
|---|---|---|---|
| Python | `python-docs` | Download its official Sphinx index and match keywords and API symbols locally | English `/3/` documentation |
| pandas | `pandas-docs` | Same | Current English `/docs/` |
| SQLAlchemy | `sqlalchemy-docs` | Same | English `/en/20/` |
| MDN Web Docs | `mdn` | MDN public site search | English documentation |

These routes require neither Exa, Parallel, host search nor a user key. The Agent can select them during ordinary questions. A named project with a concrete documentation topic can also select a known official scope automatically. Explicit user sites and platforms take precedence.

```bash
python3 scripts/xcoze_search.py search 'asyncio TaskGroup exception cancellation' --platform python-docs
python3 scripts/xcoze_search.py search 'merge validate one_to_one' --platform pandas-docs
python3 scripts/xcoze_search.py search 'select join' --platform sqlalchemy-docs
python3 scripts/xcoze_search.py search 'AbortSignal.timeout' --platform mdn
```

Alternatively use `--site docs.python.org`, `--site pandas.pydata.org`, `--site docs.sqlalchemy.org` or `--site developer.mozilla.org`; automatic search starts with the matching documentation route. Explicit `--provider docs` requires a supported `--site`.

## Results and page content

Sphinx search downloads `searchindex.js` from a fixed official URL and reads its JSON without executing JavaScript. Matching stays local; the query is not sent to the documentation site. No server or index deployment is needed. Each search downloads the site's index, typically a few MB.

The result kind is `documentation_index`, with titles, original links, available API anchors and matched terms. It has no body summaries or publication dates. Limited English suffix variants do not reproduce the website's complete search algorithm. MDN returns site-provided summaries as `search_summary`.

To explain behavior, verify versions or cite passages, the Agent still needs the original page. Index matches do not replace missing body, date or version evidence. Fixed directories do not automatically switch to another requested version. Unsupported date, language and other constraints exclude the route or produce an explicit error.

## Chinese scoped web search

`so360` reads 360 public HTML results without starting a browser or using a logged-in session:

```bash
python3 scripts/xcoze_search.py search '海上风电' --site nea.gov.cn --provider so360 --strategy free
```

It extracts organic results, uses page-provided destination URLs and checks their hostnames. Obvious topic, symbol and year mismatches are rejected; short Chinese topic terms receive literal checks. Coverage is limited to the public index. Other sources allowed by the current mode can fill gaps.

360 returned a CAPTCHA redirect during this batch test and cannot be the only fallback. The adapter does not follow or solve verification pages; detection pauses the source for 15 minutes. No hits, verification and network failures remain distinct. See the [live report](../evaluations/reports/2026-11-16-keyless-search.en.md).
