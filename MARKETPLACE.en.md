# Generic marketplace materials

[简体中文](MARKETPLACE.zh-CN.md) | **English**

Name: **xcoze search**
ID: `xcoze-search`
Version: `0.4.1` preview
Maintainer: XCoze
Repository: [wjason/xcoze-search](https://github.com/wjason/xcoze-search)

## Short description

Automatically select keyless and commercial sources for Agent web search, page reading and traceable citations.

## Description

Ask normally after installation. No keys use public routes; configured keys default to quality-first. Balanced/free/default-source preferences are optional. Source/HTTP/time budgets bound automatic fallback; the Agent assesses evidence gaps and checks originals.

Keyless routes: Bing RSS, DuckDuckGo HTML, Exa hosted MCP, GitHub public repositories and Hacker News; Jina Reader extracts pages. BYOK: DeepSeek, Yuanbao, Tavily, Exa, Brave and Bocha. Zhihu/Xiaohongshu/Weibo have scoped public-index search, not guaranteed native search, complete text or comments.

## Installation and requirements

```text
Install https://github.com/wjason/xcoze-search
```

Python 3.10+, no pip/browser runtime dependency; a host with Agent Skills and local execution. Optional Skills CLI installation requires Node.js. Keys use local hidden input, never chat; signup links are printed without opening pages. See [installation](INSTALL.en.md), [setup](references/setup.en.md).

## Data and boundaries

Queries/URLs go to the selected source without an XCoze relay. Keyless still uses external services and their limits. Credentials are permission-protected plaintext without OS credential-store integration. Search success is not factual verification; live retrieval does not promise immediate indexing. Self-hosted search, enterprise documents and full-site crawling are outside scope.

See [validation](VALIDATION.en.md) for offline/live evidence and unverified items. No marketplace is selected; this file does not establish listing, certification or approval. Suggested tags: search, agent, keyless, research, citations, web-fetch.
