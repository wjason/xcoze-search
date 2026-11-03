# Routing and platform scope

[简体中文](routing.md) | **English**

## Defaults and overrides

Normal questions trigger the Skill without a mode choice. Search defaults to provider auto. Precedence: explicit current source/strategy, saved preferences, then Smart. A named source overrides a saved mode; an explicit free strategy together with a keyed source is rejected.

Smart selects quality when a syntactically valid, enabled key exists, otherwise free. Format does not establish network access, balance or permissions. Quality without keys still uses keyless sources. Preferences only update local configuration, never keys or remote state; unknown config fields are retained.

| Strategy | General search candidate order |
|---|---|
| quality | Configured default/other configured sources, followed by keyless general sources |
| balanced | Bing, configured sources, then remaining keyless sources |
| free | Keyless adapters only; all keyed adapters excluded |

GitHub repository/HN story targets prefer their platform adapters. A saved default may take priority; disabled sources stay excluded. Bootstrap order is transparent configuration policy, not a benchmark ranking. No persistent learned success history is implemented.

## Script and Agent responsibilities

The script preflights constraints. Incompatible auto candidates appear in skipped_incompatible without dropping time/site conditions. Explicit multi-source calls fail preflight if any selected source is incompatible. Native freshness expressions are not translated to another provider's different semantics; use supported start/end dates or separate Agent queries when appropriate.

Auto tries at most two sources (configurable 1–3) within 45 seconds by default. This is a scheduling budget, not a hard process deadline for DNS/network reads. Remaining time is checked before calls and each timeout is clipped accordingly; automatic sources have zero retries, and max-requests caps actual HTTP attempts. Nonempty usable results return immediately, preserving failure history. The Agent evaluates relevance, freshness, coverage and independence, then searches remaining compatible sources or revises queries only for evidence gaps. Script scores never replace fact checking.

The script does not accumulate time or currency across commands; the Agent must track task-wide calls. There is no quality guarantee, universal cross-provider score, real-time stock quote guarantee or index-delay promise. Successful fallback establishes access to results, not factual truth.

## Platform coverage

| Target | Implemented | Not promised |
|---|---|---|
| GitHub | Public repository search and default README | Code search, private repositories, full Issue/PR adapters |
| HN | Algolia story search and official single-item reads | Automatically fetched comment trees or read outbound articles |
| Zhihu | Scoped public-index search | Arbitrary full answers, native search or comments |
| Xiaohongshu | Scoped public-index search | Logged-in ranking, image understanding, complete notes or comments |
| Weibo | Scoped public-index search | Official live trends or complete comments |

Returned URL hosts are checked for site scope; a domain in a URL path is not a match. Public indexes may have no relevant records. Existing authorized platform tools such as Agent Reach can complement site-specific tasks, but they are not dependencies; this package does not copy sessions or install browsers automatically.

## Reading and cost

Fetch auto tries GitHub README for repository-root links and the official interface for HN items. General URLs start with Jina Reader; configured Fetch-capable services take fallback priority when allowed, followed by Exa keyless MCP. The same source-count cap applies; unattempted candidates have no live verification status. Skip the script when the host already reads the page successfully.

Keyless is not entirely local: Bing, DuckDuckGo, Exa, GitHub, Algolia/HN and Jina receive corresponding requests. Exa keyless and Jina Reader are limited-access commercial services. Free strategy guarantees no user-keyed service requests from this tool, not zero model/subscription/compute costs.

## Management examples

```bash
python3 scripts/xcoze_search.py preferences
python3 scripts/xcoze_search.py preferences --strategy free
python3 scripts/xcoze_search.py preferences --strategy balanced --max-sources 2
python3 scripts/xcoze_search.py preferences --provider deepseek
python3 scripts/xcoze_search.py preferences --disable duckduckgo
python3 scripts/xcoze_search.py preferences --enable duckduckgo
python3 scripts/xcoze_search.py preferences --reset
python3 scripts/xcoze_search.py plan 'industrial vision' --platform github
python3 scripts/xcoze_search.py search 'industrial vision' --provider yuanbao
```

Explicit sources never fall back outside their selection. Both and comma-list semantics remain. Auto and Fetch defaults changed in v0.4.0; pin a source to retain older deterministic behavior.
