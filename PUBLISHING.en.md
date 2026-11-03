# GitHub and marketplace publishing

[简体中文](PUBLISHING.zh-CN.md) | **English**

Repository: [wjason/xcoze-search](https://github.com/wjason/xcoze-search). This guide covers release maintenance and marketplace submissions. Actual state is determined by GitHub code/Releases; hosting source on GitHub does not imply marketplace acceptance.

## Before publishing

1. Confirm the XCoze maintainer identity and MIT license match the intended publication.
2. Use your own accounts to run DeepSeek/Yuanbao doctor, recording usable results. Further check real Fetch and tier-specific Yuanbao options. Offline mocks do not replace live validation.
3. Check README repository/install URLs and supply the repository/contact details to the marketplace.
4. Run tests and review validation records. Exclude config.json, keys, .env, logs, personal files, and caches.

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py --output-dir ../release
```

## GitHub

The repository root contains SKILL.md. Commit/push here rather than treating a surrounding outputs/release directory as the Skill root.

The current release is v0.4.1 preview. Pushing a v* tag triggers .github/workflows/release.yml and reuses four Windows/Linux, Python 3.10/3.12 test jobs. Publication waits for every job to pass.

Publishing checks the tag, runtime/Skill/package versions, and changelog; extracts current-version notes; builds Skill ZIP, source ZIP, and SHA256SUMS.txt; then verifies checksums. It creates a draft with complete assets before publishing a Pre-release, without overwriting existing Releases/assets.

GitHub Actions supplies a temporary GITHUB_TOKEN, with contents:write only on the publishing job. No personal GitHub token or search-provider keys are needed. Repository policies can reject permission; inspect Actions diagnostics and never treat a failed workflow as publication.

For the next version:

1. Update runtime/Skill/package versions and the dated changelog section; refresh download URLs and validation records.
2. Run the commands below and inspect package contents.
3. Commit/push, then create/push a matching version tag on that commit. Never move or reuse published tags.
4. Wait for publication to pass, then check the Pre-release marker, three assets, and checksums before confirming completion.

```bash
python3 scripts/prepare_release.py --tag v0.4.1 --output ../release-notes.md
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py --output-dir ../release
```

Retain v0.1.0/v0.2.0 tags/assets rather than replacing them. Keep Pre-release when live verification is incomplete and list outstanding checks. Passing tests does not establish accounts, balance, quota, or marketplace compatibility.

## Historical v0.1.0 release notes

v0.1.0 introduced official DeepSeek/Yuanbao search APIs, single-provider selection, explicit dual-provider retrieval, DeepSeek Markdown Fetch, hidden key input, and environment variables.

Results retain providers, sources, and native scores; Yuanbao summaries remain separate from page text. Partial failures retain available results and report errors. Runtime uses only the Python 3.10+ standard library.

See the same version's validation record. This is an independent XCoze integration, not an official DeepSeek/Tencent Skill. API charges may apply.

## Bilingual release notes

The default export is Chinese. Use --language en for English, or --language both for a Chinese body followed by a collapsed English section. The tag workflow uses both and requires matching dated version sections in both changelogs; a missing English record stops publication.

```bash
python3 scripts/prepare_release.py --tag v0.4.1 --language both --output ../release-notes.md
```

Both documentation/instruction languages are in future package manifests. Existing published tags/assets remain unchanged.

## General marketplaces

No marketplace is selected. Use the standard Agent Skills folder/ZIP and [marketplace copy](MARKETPLACE.en.md) for naming, descriptions, dependencies, data flow, examples, and repository links.

Some uploaders expect SKILL.md at the ZIP root; others accept xcoze-search/. Follow the actual uploader's requirements and avoid double nesting. Add marketplace-specific manifests, icons, signatures, privacy links, or CLIs only after checking its documentation. Do not invent certification fields.

The Skill package contains no marketplace keys and does not automatically log in, create repositories, push, or submit reviews.

## Maintenance

When provider APIs/tiers change, update references/providers.en.md and protocol tests, then validate and release. Runtime, Skill metadata, README, and asset versions must match. User credentials always stay outside distributions.
