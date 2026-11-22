# 安装与首次使用

**简体中文** | [English](INSTALL.en.md)

## 让 Agent 安装

将下面的话发送给你的 Agent：

```text
帮我安装这个 Skill：https://github.com/wjason/xcoze-search
```

需要支持 Skill 安装和本地脚本执行的 Agent，以及 Python 3.10 或更高版本。基础功能只使用 Python 标准库，无需 API Key。安装后如果没有识别到 Skill，请按 Agent 提示重新加载或新建会话。

## 其他安装方式

使用 Skills CLI 安装需要 Node.js：

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

也可以从 [GitHub Releases](https://github.com/wjason/xcoze-search/releases) 下载 Skill ZIP，解压到 Agent 的技能目录。Codex 默认目录为 `~/.codex/skills/xcoze-search/`；如果设置了 `CODEX_HOME`，则使用该目录下的 `skills`。其他 Agent 请参考各自的安装说明。

## 开始搜索

安装完成后，直接向 Agent 提问，例如：

```text
在 GitHub 找几个开源工业视觉项目，对比部署要求，并给出项目链接。
```

没有 Key 时使用公开来源；配置 Key 后，默认也会考虑已启用的搜索服务。你可以随时让 Agent 切换免费、平衡或默认模式，详见[搜索方式](references/routing.md)。

如果希望使用 DeepSeek 等服务，可以说“帮我配置 xcoze search 的 DeepSeek 搜索”。Agent 会提供官方申请链接，并引导你通过本机隐藏输入窗口填写 Key。没有图形界面时，可以使用自己的终端或环境变量。请勿将 Key 发到聊天中。[配置与排错](references/setup.md)提供详细步骤。

## 升级与卸载

可以让 Agent 检查并更新已安装的 Skill，无需寻找配置文件。默认包含已发布的预览版；加 `--stable` 只查稳定版，不会自动降级较新的安装。

```bash
python3 "<skill_dir>/scripts/manage_skill.py" check
python3 "<skill_dir>/scripts/manage_skill.py" update
python3 "<skill_dir>/scripts/manage_skill.py" check --offline
```

旧版如果还没有更新工具，由 Agent 从新 Release 获取 Skill ZIP，核对 `SHA256SUMS.txt` 后，使用新包中的工具更新原目录：

```bash
python3 "<new_package>/scripts/manage_skill.py" install --source /path/xcoze-search-skill-v0.10.0.zip --target /path/to/skills/xcoze-search
```

更新工具在替换前校验包内每个文件，并把旧目录及本地修改备份到技能发现目录之外；配置目录中的 Key 和偏好不变。输出会给出备份路径，可以恢复：

```bash
python3 "<skill_dir>/scripts/manage_skill.py" restore --source /path/to/backup --target /path/to/skills/xcoze-search
```

更新后重新加载 Agent 或新建会话。网络、限流或校验失败不会删除原安装；GitHub 下载受限时可以使用已核验的离线 ZIP。不要安装不可信来源的压缩包。



升级时替换 Skill 目录，不会覆盖用户配置目录中的 Key。若需要降级旧版本，请先阅读[配置迁移说明](references/setup.md#存储与迁移)：旧版本可能无法读取新配置，迁移备份也不包含之后更换的 Key。

卸载时删除 Agent 的 Skill 目录。如需同时清理凭据，还需删除本地配置及备份、清除相应环境变量，并按需在服务商处撤销 Key。
