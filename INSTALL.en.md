# Installation and first use

[简体中文](INSTALL.zh-CN.md) | **English**

## Ask the Agent to install

```text
Install https://github.com/wjason/xcoze-search
```

The Agent checks Python 3.10+, installs into the host's skill directory, then follows host reload/new-session requirements. Base runtime uses only the Python standard library, without a browser or additional dependencies. No key is needed during installation; ask normal questions afterwards.

## CLI or manual installation

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

This optional method requires Node.js. Alternatively unpack the [v0.9.0 Skill ZIP](https://github.com/wjason/xcoze-search/releases/download/v0.9.0/xcoze-search-skill-v0.9.0.zip) into your host's skill directory; manual unpacking does not need Node.js.

Codex's default is `~/.codex/skills/xcoze-search/`, or the skills subdirectory of CODEX_HOME when set. Follow other hosts' discovery rules. This package needs local script execution; a standalone executable remains planned.

## First use

```text
Find open-source industrial vision projects and compare deployment requirements.
Find official updates on this topic from the past week.
```

No key selects keyless sources; configured enabled keys make the default quality-first. Anonymous limits, network and coverage still affect results; successful installation does not verify every backend. Mode selection is optional; see [routing](references/routing.en.md).

To add a commercial service, ask “Configure DeepSeek for xcoze search.” The Agent prints official links without opening them, then launches local hidden input when ready. Never paste keys into chat. On headless systems use the user's own visible terminal or controlled environment variables. See [setup](references/setup.en.md).

## Upgrade, compatibility and removal

Replacing the program folder does not overwrite user-directory credentials. v0.4.0 retains v1 reading, schema v2 and private-backup migration; search_preferences is optional. Searches never rewrite config; preferences/key saves migrate only when needed.

**Behavior changes:** auto now has bounded fallback and Fetch defaults to automatic routing. Pin `--provider deepseek` or another source for older deterministic behavior. Both still means DeepSeek plus Yuanbao. Preferences --reset restores defaults without deleting keys.

v0.2.0 cannot read v2. For downgrade inspect the private backup locally; it excludes later keys. Older versions also do not enforce new preferences. Removing the program does not revoke credentials; separately delete local config/backups, clear variables and revoke keys at their providers when required.
