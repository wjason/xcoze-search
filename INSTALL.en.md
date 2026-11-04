# Installation and first use

[简体中文](INSTALL.zh-CN.md) | **English**

## Ask your Agent

Send this message to your Agent:

```text
Please install this Skill: https://github.com/wjason/xcoze-search
```

You need an Agent that supports Skill installation and local script execution, plus Python 3.10 or newer. Base features use only the Python standard library and do not require an API key. If the Skill is not recognized after installation, follow your Agent's instructions to reload it or start a new session.

## Other installation methods

The Skills CLI requires Node.js:

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

Alternatively, download the Skill ZIP from [GitHub Releases](https://github.com/wjason/xcoze-search/releases) and extract it into your Agent's skills directory. Codex defaults to `~/.codex/skills/xcoze-search/`; when `CODEX_HOME` is set, use its `skills` directory. For other Agents, follow their installation instructions.

## Start searching

Once installed, ask your Agent a question, for example:

```text
Find open-source industrial vision projects on GitHub, compare their deployment requirements, and give me the repository links.
```

Without a key, the Skill uses public sources. After you configure keys, the default also considers enabled search services. You can ask your Agent to switch between free, balanced, and default modes; see [search routing](references/routing.en.md).

To add a service such as DeepSeek, ask “Help me configure DeepSeek for xcoze search.” The Agent will provide the official signup link and guide you through entering the key in a local masked-input window. Without a desktop, you can use your own terminal or an environment variable. Do not send keys in chat. See [setup and troubleshooting](references/setup.en.md) for details.

## Upgrade and uninstall

To upgrade, replace the Skill directory. This does not overwrite keys in your user configuration directory. Before downgrading, read the [configuration migration notes](references/setup.en.md#storage-and-migration): older versions may not read the current configuration, and migration backups do not contain keys changed afterward.

To uninstall, remove the Agent's Skill directory. To remove credentials as well, delete the local configuration and backups, clear the relevant environment variables, and revoke keys with their providers if needed.
