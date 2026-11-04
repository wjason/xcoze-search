# Publisher feeds, government policy and community originals: live checks

[简体中文](2026-11-05-feeds-community.md) | **English**

2026-11-05, Asia/Shanghai; runtime/release v0.9.0. Real tasks connect discovery to original reading. Nonempty transport is not factual verification. Single local observations do not establish cross-network success rates or latency percentiles.

| Task/operation | Observation | Time | Actual path |
|---|---|---:|---|
| Find CIIE reports in the CNS finance feed | Three literal matches in the current window | 0.157 s | cns-finance, one HTTP |
| Find Nov 5 Beijing-day items in CNS latest RSS | One match at retrieval time, not all news that day | 0.151 s | cns-scroll, one HTTP |
| Inspect current BBC World items | First three entries with source publication dates | 0.944 s | bbc-world, one HTTP |
| Find registration-related policy on gov.cn | Located the public-institution registration regulation without relaxing dates | 0.437 s | govcn, one HTTP |
| Read a Python forum original about spelling suggestions | 885 characters of question/background, without answer replies | 0.759 s | community, one HTTP |
| Read Rust forum code-formatting instructions | 1261 characters, preserving backtick examples and indentation | 1.272 s | community, one HTTP |
| Read a known V2EX original | 403; stopped reader fan-out and paused that site | 0.437 s | community, one HTTP |
| Read the first retrieved CIIE article | 2942 characters containing the requested topic | 1.192 s | Jina 401 → keyless Exa, two HTTP |
| Read the retrieved policy original | 4982 characters, separating publication/document/effective dates | 1.141 s | Jina 401 → keyless Exa, two HTTP |

Initial nine operations used 11 observable API HTTP attempts: eight successes, one blocked. Zero keyed calls or browser launches. Success does not establish answered questions: the Python original asks a question; causal conclusions would still need actual replies or official documentation.

## Windows, dates and originals

CNS feed URLs come from its [official RSS directory](https://www.chinanews.com.cn/rss/). BBC uses its [World RSS](https://feeds.bbci.co.uk/news/world/rss.xml). Filtering covers only current entries, without historical pagination. Date constraints use inclusive Beijing calendar days. Atom updated is not publication, and unknown dates are never replaced by retrieval time. URL deduplication strips fragments within the window, without claiming cross-publisher independence.

The [gov.cn latest-policy page](https://www.gov.cn/zhengce/zuixin/) uses public ZUIXINZHENGCE.json. The observed window had 1109 rows with newest publication 2026-11-01, before retrieval day; it is not a real-time complete notice database. The [located policy original](https://www.gov.cn/zhengce/content/202610/content_7084279.htm) was read separately. Portal publication is not effective date. No match may trigger bounded search under existing preferences, not a claim that no policy exists.

## Community evidence boundaries

Native community supports fixed public endpoints on V2EX, discuss.python.org and users.rust-lang.org, without user sessions. Discourse's [Topic API](https://docs.discourse.org/#tag/Topics/operation/getTopic) may attach initial replies; the adapter exposes post_number:1 only. comments_fetched/source_attached_replies accurately describes that transfer, while comments_included:false means reply bodies were not exposed and thread_complete remains false. No reply pagination. An early check incorrectly used comments_fetched:false for unexposed replies; this was corrected and verified by two more real reads, recorded separately from the initial nine operations.

Root and reply URLs are distinct: /t/123/2 is not topic 2 and cannot silently become the original. HTML conversion preserves code indentation/link targets without claiming byte-exact markup. Default 24000 characters with explicit truncation, not thread completeness.

V2EX 403 does not establish a missing topic. No cookie/proxy/browser/reader switching was used to retry it. Pacing/pauses are per site. Follow [V2EX API fair-use rules](https://www.v2ex.com/p/7v9TEc53); post bodies are not republished here.

## Validation and limits

170 offline tests pass: RSS/Atom/DOCTYPE handling, literal/date/unknown-date/deduplication semantics, policy scope, free isolation, root/reply identities, text links/code, truncation, per-site pauses and stop-on-denial. Incomplete HTTP bodies become redacted network failures; anonymous 401/403 no longer blames the user's key.

The structured record publishes status, times, counts, character lengths, hashes, request accounting and bounded window metadata, without article/post bodies, credentials or profiles. Installed acceptance is separate. Endpoint discovery/documentation is outside the initial 11 attempts; reply-accounting rechecks add two HTTP attempts. Cross-network/OS access, a complete notice corpus, arbitrary feed URLs, historical news and complete comment trees remain unverified/unimplemented.

[Usage](https://github.com/wjason/xcoze-search/blob/main/references/feeds.en.md) · [Per-operation data](2026-11-05-feeds-community.data.json)
