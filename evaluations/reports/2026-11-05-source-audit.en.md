# Source availability check

[简体中文](2026-11-05-source-audit.md) | **English**

Checked on 2026-11-05 (Beijing time) with isolated temporary configuration and cache. No user API keys were read or sent. Each entry is one live request or browser search. Results describe the network and query at that time, not ongoing availability or a guarantee of search quality.

| Scope | Result |
|---|---|
| Public search | Exa MCP, GitHub, Hacker News, Wikipedia, Stack Exchange, arXiv, Crossref, npm, crates.io, GitLab.com, Europe PMC, Hugging Face and gov.cn returned results. The Bing RSS English sample failed the relevance check; DuckDuckGo returned a challenge (202). |
| Page and community reading | Exa MCP, GitHub README, a single Hacker News item, and Python and Rust community posts succeeded. Jina Reader returned 401; the V2EX topic endpoint returned 403. |
| News and trends | Both China News Service feeds and BBC World returned items. Zhihu and Bilibili trends returned items; V2EX trends returned 403. |
| Platform-scoped search | One Exa MCP query per platform returned links for Zhihu, Xiaohongshu, Weibo, YouTube, Bilibili, Reddit, V2EX and Douban. The X query returned no results. Links do not establish native search, full posts or comment access. |
| Browser search | With an existing local agent-browser, 360 returned results; Bing failed the sample relevance check, and Google returned a challenge. |
| New sources | Open Library, DataCite, Zenodo and Wikidata each returned three results through this project's adapters. These are book, research or entity metadata, not full-text retrieval. |
| Keyed services | DeepSeek, Yuanbao, Tavily, Exa API, Brave and Bocha were not called in this check. Configuration alone does not verify access. |

A separate anonymous request returned World Bank indicator data, but keyword search was not verified, so it is not integrated or listed as a supported search source. Previously researched candidates, including Microsoft Learn, MDN and Parallel, are documented in the [source research](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md); an earlier successful check does not mean they were checked here or integrated.

Requests stopped after access denials or challenges; no identity changes were used to evade them. Upstream access can change at any time. Content remains subject to each provider's terms.
