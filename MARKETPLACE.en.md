# Marketplace listing material

[简体中文](MARKETPLACE.zh-CN.md) | **English**

Name: **xcoze search**

Skill ID: `xcoze-search`

Version: `0.3.0` preview; use the actual submitted version.

Maintainer: XCoze

Short description: One Skill for official DeepSeek, Yuanbao, Tavily, Exa, Brave, and Bocha search APIs, using your own provider keys.

Suggested categories: Search / Research / Information retrieval

Suggested tags: search, research, deepseek, yuanbao, tavily, exa, brave, bocha, citations, web-fetch

## Description

xcoze search adds multi-provider public-source retrieval to Agent Skills hosts that can run local Python. Configure providers as needed, then choose single or explicit multi-provider retrieval. The legacy both command still means DeepSeek plus Yuanbao.

Results preserve source URLs, available dates, providers, and native fields for evidence review and cited answers. DeepSeek, Tavily, and Exa expose their content APIs; summaries and highlights remain distinct. Capabilities are inspectable offline, with actual HTTP-attempt budgets. Account access depends on each provider.

## Prerequisites and data

- Python 3.10+, no pip runtime dependencies, and local script execution by the host.
- Users activate official API services and provide their own keys. Yuanbao needs a Search Service API Key.
- Keys use local hidden input and must not be sent through chat. Queries go directly to selected providers.
- Conversational setup provides official links for users to open themselves, followed by local key input without locating config files. Dialogs depend on an accessible desktop; terminal setup remains available. See VALIDATION.en.md for desktop acceptance status.
- Calls may incur charges; provider pricing, quotas, and terms apply.
- This is an independent XCoze integration, not an official/certified DeepSeek or Tencent Skill.

## Example prompts

- “Use xcoze search to find current public technical documentation, preferring official sources.”
- “Use Yuanbao to find industry reports from the past seven days and cite originals.”
- “Cross-check this report using DeepSeek and Yuanbao.”

## Submission fields

Repository: [wjason/xcoze-search](https://github.com/wjason/xcoze-search)

Versions/assets: [GitHub Releases](https://github.com/wjason/xcoze-search/releases). Use actual published assets. Add maintainer contact details, icons/screenshots, and review fields when a marketplace is selected.

Validation basis: offline tests passed; DeepSeek Search/Fetch were live-tested on 2026-10-24. Yuanbao and the four added providers still require their respective test keys for live verification. If live checks are completed before submission, update VALIDATION.en.md with redacted metadata only. Marketplace listing, certification, or approval cannot be guaranteed by the package.
