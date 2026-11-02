# Installation and first use

[简体中文](INSTALL.zh-CN.md) | **English**

## Ask an agent to install it

Send “Install” plus the repository URL to an agent that supports Skill installation and local command execution:

```text
Install https://github.com/wjason/xcoze-search
```

For explicit requirements:

```text
Install this Skill: https://github.com/wjason/xcoze-search
Check that Python 3.10+ is available and install it in the current assistant's skills directory.
```

After installation, start a new chat or reload the assistant if instructed. Then say “Configure xcoze search with DeepSeek. Reply in English.” Yuanbao, Tavily, Exa, Brave, and Bocha are also available. See [setup](references/setup.en.md). Installation does not require a key; never send keys through chat.

If the agent cannot install Skills or execute local scripts, follow the manual steps below.

## Manual installation and first use

1. Install Python 3.10+. Windows can use `py -3`; macOS/Linux usually use `python3`.
2. Install from the repository with the Skills CLI, or download the [v0.3.0 package](https://github.com/wjason/xcoze-search/releases/tag/v0.3.0) and place the xcoze-search folder in the host's skills directory.
3. Confirm a single directory level: `<skills>/xcoze-search/SKILL.md`. Codex defaults to `~/.codex/skills/xcoze-search/`, or the corresponding skills subdirectory when CODEX_HOME is set.
4. Start a new chat and ask “Configure Tavily for xcoze search.” Reload the assistant if it has not discovered the Skill. Choose DeepSeek, Yuanbao, Tavily, Exa, Brave, or Bocha; one configured provider is sufficient.
5. The assistant provides an official key-console link. Open it yourself; no browser page opens automatically. Once you have the key, say “Ready to enter the key.” If you already have a key, say so.
6. Paste it into the local hidden-input dialog and save. Verification makes one potentially billable search. Only `search_verified:true` for the target provider establishes access for that check. Cancellation leaves configuration unchanged; failed verification leaves the saved key in place.
7. Ask “Use xcoze search to research this public topic and cite sources.” Keep keys out of chat.

## Runtime environment

Local dialogs use macOS system dialogs, Windows PowerShell/WinForms, or an existing Zenity installation on a Linux desktop. In remote or headless environments, use hidden input in your own visible terminal or managed environment variables. The assistant should supply the actual script path:

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider exa --verify
```

Python is still required. This is not a standalone application, and a chat-only host without local script execution cannot run it. The source ZIP additionally includes tests and regression tools; the Skill ZIP contains runtime files and user documentation.

Required directory structure includes:

```text
xcoze-search/
  SKILL.md
  agents/openai.yaml
  scripts/xcoze_search.py
  scripts/search_common.py
  scripts/search_providers.py
  references/setup.md
```

## Updates, migration, and removal

Replace the program directory to update. Credentials live in the user's configuration directory and are not overwritten by the package. v0.3.0 reads v1 configuration without rewriting it during queries. Explicit `migrate-config`, or saving after successful key input, first creates a backup and then upgrades to v2. Existing keys, the default provider, and extension fields are retained. Unknown formats or migration failures do not overwrite the original credentials.

Older releases such as v0.2.0 cannot read v2. To downgrade, inspect and restore the private v1 backup locally. It does not include keys added or replaced after the upgrade. See [setup](references/setup.en.md) for paths, permissions, and failure handling.

Remove the Skill directory to uninstall. To remove credentials, separately remove the local configuration, private backup, and relevant environment variables, and revoke keys on the official platforms. Uninstalling does not revoke provider keys.
