# xcoze search

[简体中文](README.md) | **English**

[![Tests](https://github.com/wjason/xcoze-search/actions/workflows/test.yml/badge.svg)](https://github.com/wjason/xcoze-search/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

xcoze search is a web search Skill for Agents. It brings together public search sources, specialist databases, and optional search APIs to help Agents find information, locate original sources, and read web pages.

Ask a question after installation to get started. No API key is required for public sources. You can add your own keys to use other services, choose a source for a request, or save a search preference.

[Install](#install) · [Usage](#usage) · [Supported sources](#supported-sources) · [Configure API keys](#configure-api-keys) · [Contributing](#contributing)

## Install

### Ask your Agent

Send this message to your Agent:

```text
Please install this Skill: https://github.com/wjason/xcoze-search
```

Follow its installation instructions. If the Skill is not recognized afterward, reload the Agent or start a new session, then try:

```text
Use xcoze search to find microsoft/markitdown on GitHub. Tell me what it does and give me the repository link.
```

You need an Agent that supports Skills and can run local scripts, plus Python 3.10 or newer. The base features use only the Python standard library. Installation and public-source searches do not require an API key.

### Other installation methods

If Node.js is installed, you can also use the Skills CLI:

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

Alternatively, download the Skill package from [GitHub Releases](https://github.com/wjason/xcoze-search/releases). See the [installation guide](INSTALL.en.md) for details.

## Usage

Once installed, ask your Agent a question, for example:

```text
Find official announcements about offshore wind policy from the past week. Include publication dates and links to the original sources.
```

```text
Check the official Python asyncio documentation and explain how TaskGroup handles exceptions. Include the documentation link.
```

```text
Find open-source industrial vision projects on GitHub and compare their purposes, licenses, and deployment requirements.
```

The Agent selects a suitable search or reading method for the task. You can also say “use xcoze search” or specify a source for a particular request.

### Search preferences

The default is **Smart**: use keyless sources when no key is configured; when keys are configured and enabled, prioritize search quality while also using appropriate public sources.

| What you want | What to tell your Agent |
|---|---|
| Always use keyless sources | Set xcoze search to free mode for future searches. |
| Try keyless sources first, then configured services if needed | Set xcoze search to balanced mode. |
| Restore the default | Reset xcoze search preferences to Smart and keep my keys. |
| Choose a source for one request | Use DeepSeek for this search: … |
| Use keyless sources for one request | Use free mode for this search: … |

A preference for future searches is saved; a request for “this search” applies only once. Free mode does not call services that require your API key. Configure a service before selecting it.

## Supported sources

These sources are currently integrated. Public services may have access restrictions, rate limits, or regional differences. The use of results and content is subject to each source's terms.

### Keyless search and reading

| Source | What you can do |
|---|---|
| Bing RSS | Search public web pages |
| DuckDuckGo HTML | Search public web pages |
| Exa hosted MCP | Search and read web pages |
| Jina Reader | Read web pages |
| GitHub | Search public repositories and read their READMEs |
| GitLab.com | Search public projects |
| Hacker News | Search stories and read individual stories or comments |
| Wikipedia | Search English and Chinese articles |
| Stack Exchange | Search questions across Stack Overflow and six other communities |
| arXiv | Search preprints, abstracts, and paper metadata |
| Crossref | Search DOIs, authors, and publication metadata |
| Europe PMC | Search biomedical literature and abstracts |
| npm | Search JavaScript packages and version metadata |
| crates.io | Search Rust packages and version metadata |
| Hugging Face | Search public model metadata |
| gov.cn | Search China's latest-policy listing |
| Python and Rust community forums, V2EX | Read public topic posts |

Access to Bing RSS, DuckDuckGo HTML, and some community endpoints can change with the website or network. GitHub support covers repositories, not code search or private repositories. Abstracts and community search results do not imply that a full paper or discussion has been read. The gov.cn listing does not cover all announcements in China.

### News and community trends

| Source | What you can do |
|---|---|
| China News Service | Read latest-news and finance feeds |
| BBC | Read the World news feed |
| Zhihu | View trending questions and excerpts |
| Bilibili | View trending search terms |
| V2EX | View trending topics |

News feeds cover each publisher's current feed window. Trend lists contain what each platform provides; they do not include complete answers, videos, or comments.

### Platform-scoped search

Public web searches can be scoped to **Zhihu, Xiaohongshu, Weibo, YouTube, Bilibili, Reddit, X, V2EX, and Douban**. Results depend on what the web index has indexed; this differs from searching within a platform or reading signed-in content and complete comment threads.

### Bring your own API key

| Service | Supported features |
|---|---|
| DeepSeek | Search, Fetch |
| Tencent Yuanbao | SearchPro search and summaries |
| Tavily | Search, Extract |
| Exa | Search, Contents |
| Brave Search | Web Search |
| Bocha | Web Search |

Each service must be enabled separately, and its provider sets the applicable limits and charges. Exa's keyless MCP and keyed API are separate endpoints. See the [provider reference](references/providers.en.md) for options and limits.

### Browser fallback

When other available search paths cannot return results, the Skill can use an existing local [agent-browser](https://github.com/vercel-labs/agent-browser) and browser to search. It defaults to 360 Search; Bing and Google can also be selected. This is optional: the base installation does not install a browser or use your browser login state. You can also ask your Agent to turn browser fallback off.

See [public sources and platforms](references/open-sources.en.md), [news and community content](references/feeds.en.md), and [search routing](references/routing.en.md) for details. The [full source research directory](research/free-sources-2026-11.en.md) also includes sources that are not yet integrated.

## Configure API keys

You can search without a key. To add a service, tell your Agent:

```text
Help me configure DeepSeek search for xcoze search.
```

The Agent provides the official link for obtaining a key. Once you are ready, enter it in the local masked-input window. **Do not send keys in chat.** If no graphical desktop is available, use hidden terminal input or an environment variable instead; see [setup and troubleshooting](references/setup.en.md).

Keys are stored in a permission-protected local configuration file as plaintext. Environment variables take precedence for the same service. Key verification makes a real search request and may incur a charge. Yuanbao requires its search service key; Tencent Cloud SecretId/SecretKey cannot be used in its place.

## Privacy and use

Queries and page URLs are sent to the search or reading services used for the request. Keyless use still requires a network connection. Avoid submitting sensitive information or URLs containing access credentials. API keys are used only in requests to their corresponding services.

Search results can be outdated, incomplete, or inaccurate. Check original sources for important information, including publication dates and applicability.

## Development and documentation

Run offline tests from the repository:

```bash
python3 -m unittest discover -s tests -v
```

See the [provider reference](references/providers.en.md), [Agent instructions](SKILL.en.md), [roadmap](TODO.en.md), and [changelog](CHANGELOG.en.md). To run commands manually, use `python3 scripts/xcoze_search.py --help` from the repository.

## Contributing

Issues and pull requests are welcome, whether they improve documentation, fix a bug, or add a search source. For source suggestions, please include the API documentation and the capabilities you would like to see. Remove keys and other sensitive information from bug reports.

Please read the [contribution guide](CONTRIBUTING.en.md) before contributing.

## References and acknowledgments

Thank you to the projects and services that helped shape xcoze search:

- [Agent Reach](https://github.com/Panniantong/Agent-Reach), for ideas on organizing platform capabilities and search and reading workflows.
- [DDGS](https://github.com/deedy5/ddgs) and [open-webSearch](https://github.com/Aas-ee/open-webSearch), for reference designs around public search endpoints and multiple sources.
- [LiteLLM](https://github.com/BerriAI/litellm), [OpenRouter](https://openrouter.ai/), and [Tavily Skills](https://github.com/tavily-ai/skills), for ideas on unified interfaces and Agent search workflows.
- [agent-browser](https://github.com/vercel-labs/agent-browser), which supports the optional local browser search.
- The maintainers of the search services and public data sources for their interfaces and documentation, and everyone who has contributed or shared feedback.

These projects have their own licenses; third-party content and APIs are subject to their respective terms. See the [search service research](references/search-services.en.md) and [provider reference](references/providers.en.md) for details.

## License

This project is distributed under the [MIT License](LICENSE). xcoze search is independently maintained by its community and is not an official product of the search service providers listed above.
