# Open sources and local-tool cooperation

[简体中文](open-sources.md) | **English**

Local search here means the local Agent calls public services directly and still needs internet access. The base runtime uses Python's standard library without accounts, servers or browsers. Availability remains subject to upstream limits.

## Native indexes

See [publisher feeds, finite government policy and community originals](feeds.en.md) for commands, date semantics and limits. govcn adds native bounded index retrieval; community adds original-post reading. Three publisher feeds remain separate from ordinary keyword search.


### Community snapshots

`trending --platform bilibili|zhihu|v2ex --count 10` is separate from keyword search: one public endpoint, at most one HTTP attempt, an 8-second default timeout and no retries. Bilibili returns hotwords/search links/native heat; Zhihu returns question links/excerpts without reading answers; V2EX returns topic metadata without bodies/replies. Preserve source order, units and retrieval time. Unknown Bilibili/Zhihu publication times stay null. The catalog declares native_trending separately from native keyword-search coverage.

Bilibili and Zhihu use experimental public website endpoints, not stable open-platform APIs with an SLA. Follow the [V2EX API fair-use rules](https://www.v2ex.com/p/7v9TEc53). Each feed is serialized across local processes with a two-second interval. Access denials (401/403/412) pause that feed for 15 minutes; 429/503 honor Retry-After, defaulting to 60 seconds when absent. Do not rotate cookies, IPs or browsers to retry a blocked feed.

Weibo and Xiaohongshu are searched through public web indexes. Native Weibo trends and Xiaohongshu site search are not integrated. Results distinguish profiles from post links; existing authorized tools can provide additional site-specific search or comments.

### Keyword and specialist indexes


| platform | Task | Dates/languages | Boundary and official documentation |
|---|---|---|---|
| wikipedia | English/Chinese articles | --language en/zh; Chinese queries default to zh; edit timestamps are not publication dates | Article excerpts; [MediaWiki](https://www.mediawiki.org/wiki/API:Search) |
| stackexchange | Technical questions/error cases | Stack Overflow, Super User, Server Fault, Ask Ubuntu, Math/Stats/DataScience via --site; start/end filter UTC creation dates | Questions, not answers; retain owner/license; [API](https://api.stackexchange.com/docs/advanced-search) |
| arxiv | Preprints | start/end constrain submittedDate, not revision time | Abstracts/metadata, no PDF reading; [API](https://info.arxiv.org/help/api/user-manual.html) |
| crossref | DOI/publication metadata | from/until-pub-date; preserve original year/month/day precision | Check author/year, not title alone; [API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) |
| npm | JavaScript packages | Versions and registry dates stay metadata | No dependency/security audit; [API](https://api-docs.npmjs.com/) |
| crates | Rust packages | Keep max_version/max_stable_version separate; no article date from updates | Do not label prereleases stable; [policy](https://crates.io/data-access) |
| gitlab | GitLab.com public projects | Name/path/description matching, star-count sorting; no publication-date filter | No code/private search or official-identity proof; [Projects API](https://docs.gitlab.com/api/projects/) |
| europepmc | Biomedical literature | FIRST_PDATE; upstream may infer missing date parts | Abstracts, no full text or clinical validation; [API](https://europepmc.org/RestfulWebService) |
| huggingface | Public models | Download sorting; created/modified dates remain metadata | No full cards/downloads/inference; gated access is separate; [API](https://huggingface.co/docs/hub/api) |

New adapters cap results at 20, default search count 10, without pagination. Adapter limits may be stricter than upstream limits. Sites must match each source; Crossref uses stable doi.org record links. --provider can pin a native source. Disabled sources stay excluded. General queries are not broadcast to every platform; the Agent chooses from the original question.

```bash
python3 scripts/xcoze_search.py platforms
python3 scripts/xcoze_search.py platforms --platform bilibili
python3 scripts/xcoze_search.py search 'wind power' --platform wikipedia
python3 scripts/xcoze_search.py search 'asyncio TaskGroup' --platform stackexchange
python3 scripts/xcoze_search.py search 'all:"retrieval augmented generation"' --platform arxiv --start-date 2026-01-01
python3 scripts/xcoze_search.py search 'playwright' --platform npm
python3 scripts/xcoze_search.py search 'tokio' --platform crates
python3 scripts/xcoze_search.py search 'inkscape' --platform gitlab
python3 scripts/xcoze_search.py search 'Qwen' --platform huggingface
```

## Public indexes and existing tools

Zhihu, Xiaohongshu, Weibo, YouTube, Bilibili, Reddit, X, V2EX and Douban currently use scoped public-web indexes. The catalog does not claim native platform search. Page fetching does not establish retrieved comments or subtitles.

If Agent Reach is already installed, read its Skill and inspect `agent-reach channels` for actual actions, such as read URL, youtube subtitle or xiaohongshu comments. It is optional; there is no embedded execution bridge, automatic installation/update/login or session copying. Handle new setup according to user intent and deliver already-obtained public evidence. Do not evade PLATFORM_BLOCKED, RATE_LIMITED, NEED_LOGIN or BUSY by changing accounts/backends/browsers. Paid transcription is separate from free-search preferences.

Existing yt-dlp, gh and agent-browser can also help under the host's authorization. `platforms.local_tools.present` only checks PATH; it does not inspect sessions/browser profiles or establish live access.

## Pacing, state and long pages

New sources use an identifiable project User-Agent, per-source OS serialization and persisted spacing: arXiv 3 seconds, GitLab 2, others 1. Short waits up to 3 seconds reduce the remaining socket timeout. Longer waits return source_cooldown; occupied locks return source_busy, with zero HTTP attempts. Stack Exchange suppresses identical URL requests for one minute and respects backoff; zero remaining quota cools down until the next UTC day. Retry-After on 429/503 accepts seconds or HTTP dates. Independent index fallback does not repeat direct requests to the limited platform.

State lives under XDG_CACHE_HOME/xcoze-search/public-access, with LOCALAPPDATA fallback on Windows and ~/.cache otherwise. It stores timestamps and duplicate-request hashes, no query text, results, cookies or keys. Search answers are not cached. Other machines/tools sharing an IP are outside this lock's scope and still share upstream aggregate limits. Corrupt/unreadable state fails closed for that source instead of clearing a pause; the Agent locates and diagnoses it.

Reading defaults to 24000 characters. Use `fetch URL --max-characters 100000` only for missing sections; Jina/keyless Exa support 1000–200000. `truncated` indicates local clipping or possible upstream limit saturation. `completeness_verified:false` remains: length does not prove the full page was retrieved.

[Live checks and Agent Reach study](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-03-open-sources.en.md).

## Optional browser search

When API paths are unavailable, an existing agent-browser can perform an anonymous browser search. It defaults to 360; Bing or Google can also be selected. A successful API result does not automatically start the browser. This optional feature requires local tools and is subject to the website’s access rules.

```bash
python3 scripts/xcoze_search.py search 'Python asyncio TaskGroup' --strategy free
python3 scripts/xcoze_search.py preferences --browser off
python3 scripts/xcoze_search.py preferences --browser auto
python3 scripts/xcoze_search.py search 'Python asyncio TaskGroup' --provider browser --browser-engine 360
```

See [routing](routing.en.md) for source selection details.
