# 安装与首次使用

**简体中文** | [English](INSTALL.en.md)

## 让 Agent 帮忙安装（推荐）

将“安装＋仓库地址”直接发给支持 Skill 安装和本地命令执行的 Agent：

```text
安装 https://github.com/wjason/xcoze-search
```

需要明确安装要求时，可以发送：

```text
帮我安装这个 Skill：https://github.com/wjason/xcoze-search
请检查 Python 3.10+ 是否可用，并安装到当前助手的技能目录。
```

安装完成后，按助手提示新建会话或重新载入，再发送“帮我配置 xcoze search 的 DeepSeek 搜索”。也可以选择元宝、Tavily、Exa、Brave 或博查。配置流程见 [配置说明](references/setup.md)，安装时不用提供 Key，密钥不要发到聊天中。

如果当前 Agent 不支持安装或执行本地脚本，按下面的手动步骤操作。

## 手动安装与首次使用

1. 安装 Python 3.10+；Windows 可使用 `py -3`，macOS/Linux 通常为 `python3`。
2. 用 Skills CLI 安装仓库，或下载 [v0.3.0 安装包](https://github.com/wjason/xcoze-search/releases/tag/v0.3.0)，将 xcoze-search 文件夹放进助手技能目录。
3. 确认入口只有一层：`<skills>/xcoze-search/SKILL.md`。Codex 默认 `~/.codex/skills/xcoze-search/`；设置过 CODEX_HOME 时按对应 skills 子目录。
4. 新建对话，输入“帮我配置 xcoze search 的 Tavily”；未识别时重启/重新载入助手。可选择 DeepSeek、元宝、Tavily、Exa、Brave 或博查，只配置一家即可使用。
5. 助手提供官方申请链接，由用户自行点击，不自动打开网页。拿到 Key 后回复“准备好了，开始输入”；已有 Key 可直接说明。
6. 在本地隐藏输入窗口粘贴并保存。验证会执行一次可能计费的搜索，只有目标服务 search_verified:true 才说明该次可用；取消不改配置，验证失败时保存值仍在。
7. 直接说“用 xcoze search 搜索这个公开主题，附来源”。不要把 Key 发到聊天中。

## 运行环境

本地窗口使用 macOS 系统对话框、Windows PowerShell/WinForms、或已有 Zenity 的 Linux 图形桌面。远程/无桌面环境使用自己的可见终端隐藏输入或受控环境变量，助手应提供已定位实际脚本路径的命令。

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider exa --verify
```

当前仍依赖 Python，不是独立应用；不支持执行本地脚本的纯聊天环境无法运行本包。源码包额外包含测试和回归工具，安装包只包含运行文件与使用说明。

目录至少包含：

```text
xcoze-search/
  SKILL.md
  agents/openai.yaml
  scripts/xcoze_search.py
  scripts/search_common.py
  scripts/search_providers.py
  references/setup.md
```

## 升级、迁移与卸载

升级时替换程序目录，凭据位于用户配置目录，不随包覆盖。v0.3.0 可读取 v1 配置，普通查询不改写它；显式 migrate-config，或成功输入后保存新配置时，先备份再升级至 v2。新程序保留原 Key、默认源和扩展字段。未知格式或迁移失败不覆盖原始密钥。

v0.2.0 等旧程序不能读取 v2；降级需用户在本机核对并恢复 v1 私有备份，该备份不含升级后新增或更换的 Key。详细路径、权限和失败处理见 [配置说明](references/setup.md)。

卸载移除程序目录即可。需要清理密钥时，另行移除本机配置、私有备份及相关环境变量，并到官方平台撤销 Key；卸载程序不会撤销平台密钥。
