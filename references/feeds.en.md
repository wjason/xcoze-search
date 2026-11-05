# Publisher feeds, government policy and community originals

[简体中文](feeds.md) | **English**

## News and policy windows

```bash
python3 scripts/xcoze_search.py feeds
python3 scripts/xcoze_search.py feed --source cns-scroll --start-date 2026-11-05 --end-date 2026-11-05
python3 scripts/xcoze_search.py feed --source cns-finance --query '进博会' --count 5
python3 scripts/xcoze_search.py feed --source bbc-world --count 5
python3 scripts/xcoze_search.py feed --source hk-data --count 5
python3 scripts/xcoze_search.py feed --source govcn --query '登记管理'
python3 scripts/xcoze_search.py search '登记管理' --platform govcn --strategy free
```

The catalog is offline. Feed reads one fixed source with an 8-second default timeout, one HTTP attempt and no retries, credential reading or browser. --query requires all whitespace-separated literal terms in title/excerpt; use short terms, not a semantic question. Dates are inclusive UTC+08:00 calendar days; unknown dates are excluded under date constraints. RSS pubDate/Atom published retains source publication semantics; Atom updated does not become publication. URL deduplication removes fragments and retains the first row/source rank, without cross-site independence claims.

Sources: CNS latest/finance RSS, BBC World RSS, DATA.GOV.HK dataset-update RSS and the gov.cn latest-policy JSON. The Hong Kong feed lists recent dataset updates in English. Only the returned window is read: no historical pagination or persistent subscription. Metadata reports source_row_count, matched_count, shown_count, newest/oldest publication, unknown_dates_excluded and duplicate_urls_removed; window_complete stays false. Latest publication is not source update time or proof of exhaustive coverage. BBC publication offsets are retained; date filtering converts to Beijing time.

GovCN also participates in native-first search with --platform govcn, respecting free mode, disabled sources and existing budgets. Its finite list includes policy documents and explainers, not all national/local notices. Verify publication, document and effective dates separately from originals. For no match or a stale window, the Agent can continue search under existing preferences, without claiming no relevant information exists.

Feed excerpts and official-policy indexes use separate content_kind values with empty content; they are not read articles. Read article URLs only when needed. Two-second per-source intervals and cross-process serialization apply. Honor Retry-After on 429/503. Failed/changed source formats remain errors, never successful empty feeds.

## Original community posts

```bash
python3 scripts/xcoze_search.py fetch 'https://discuss.python.org/t/109869' --strategy free
python3 scripts/xcoze_search.py fetch 'https://users.rust-lang.org/t/forum-code-formatting-and-syntax-highlighting/42214' --strategy free
python3 scripts/xcoze_search.py fetch 'https://www.v2ex.com/t/1254349' --provider community --strategy free
```

Automatic fetch prefers the native community reader on these three hosts. Accept canonical HTTPS topic-root URLs only, rejecting query parameters, fragments and reply targets to avoid silently reading another topic/original instead. Use existing host tools for exact reply links.

Python/Rust use public Discourse Topic JSON and select post_number:1; V2EX uses its public single-topic API. Results use community_original_post, default 24000 characters, adjustable with --max-characters 1000–200000, explicit truncation and character counts. Discourse cooked HTML becomes plain text with code indentation/link destinations; content_format explains the conversion, not byte-exact HTML/Markdown fidelity.

Only the original body is exposed. Discourse may attach initial replies in its response: comments_fetched/source_attached_replies describes that transfer, while comments_included:false means reply bodies are not exposed. No reply pagination. Thread/completeness verification stays false; this is not a complete discussion or independent fact verification.

Pacing and pauses are per community. HTTP 401/403/412 pauses for 15 minutes; automatic fetch stops reader fan-out after denial/cooldown, without identity/proxy/browser changes. V2EX access may be restricted by the network or platform. Other communities do not use this native adapter; existing authorized host tools may help.

[Live checks](https://github.com/wjason/xcoze-search/blob/main/evaluations/reports/2026-11-05-feeds-community.en.md) · [Output contract](output.en.md)
