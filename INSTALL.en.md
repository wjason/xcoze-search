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

The Agent can check and update the installed Skill without locating configuration files. Preview releases are included by default; add `--stable` to check stable releases only. Version comparison does not downgrade a newer installation.

```bash
python3 "<skill_dir>/scripts/manage_skill.py" check
python3 "<skill_dir>/scripts/manage_skill.py" update
python3 "<skill_dir>/scripts/manage_skill.py" check --offline
```

An old installation without this manager can be updated from the new release ZIP. Validate the release checksum and use the new manager to install into the existing Skill directory:

```bash
python3 "<new_package>/scripts/manage_skill.py" install --source /path/xcoze-search-skill-v0.10.0.zip --target /path/to/skills/xcoze-search
```

The manager checks the archive and every manifest file before replacement, and preserves the old tree, including local edits, outside skill discovery. Keys and preferences in the configuration directory are not changed. The output identifies the backup; restore it with:

```bash
python3 "<skill_dir>/scripts/manage_skill.py" restore --source /path/to/backup --target /path/to/skills/xcoze-search
```

Reload the Agent or start a new session after updating. Network/rate-limit or integrity failures do not delete the previous installation; use a verified offline ZIP if GitHub downloads are unavailable. Do not update from an untrusted archive.



To upgrade, replace the Skill directory. This does not overwrite keys in your user configuration directory. Before downgrading, read the [configuration migration notes](references/setup.en.md#storage-and-migration): older versions may not read the current configuration, and migration backups do not contain keys changed afterward.

To uninstall, remove the Agent's Skill directory. To remove credentials as well, delete the local configuration and backups, clear the relevant environment variables, and revoke keys with their providers if needed.
