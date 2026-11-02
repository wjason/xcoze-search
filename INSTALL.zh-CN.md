# 安装与首次验证

1. 安装 Python 3.10 或更高版本，执行 `python3 --version`（Windows 可用 `py -3 --version`）。
2. 解压 Skill 发布 ZIP，将其中的 `xcoze-search` 文件夹复制到助手的技能目录。
3. 确认入口只有一层：`<skills>/xcoze-search/SKILL.md`。
4. 新建一轮对话，输入“帮我配置 xcoze search”；宿主未发现技能时重启/重新载入。
5. 选择 DeepSeek 或元宝。助手在对话中给出官方密钥申请链接，不自动打开网页。自行点击链接取得 Key 后回复“准备好了，开始输入”；已有 Key 时可直接说明。
6. 助手启动本地隐藏输入窗口，用户粘贴 Key 并保存，随后执行一次可能计费的搜索验证。助手根据实际结果报告是否可用。

无需查找安装目录或配置文件，也不要把 Key 发到聊天中。只用一家就只配置一家。取消输入不改动已有配置；验证失败时密钥已保存，但服务尚未通过验证。密钥获取入口和具体服务要求见 [配置说明](references/setup.md)。

上述对话配置与窗口入口包含在 `main` 的 v0.2.0 开发版中，尚未发布新的 Release；请用 Skills CLI 安装当前仓库或下载 `main` 源码。v0.1.0 发布包需使用终端配置。

## 无图形界面时配置

本地窗口使用 macOS 系统对话框、Windows PowerShell/WinForms，或已安装 Zenity 的 Linux 图形桌面。远程、无桌面或工具不可用时，助手应说明原因，提供已定位到实际脚本路径的命令，由用户在自己的可见终端隐藏输入，也可使用受控环境变量。

手动配置命令（在安装目录执行）：

```bash
python3 scripts/xcoze_search.py setup --provider deepseek --default --verify
python3 scripts/xcoze_search.py setup --provider yuanbao --verify
```

`--verify` 会执行一次可能计费的搜索；输出 `search_verified:true` 才表示本次实测通过。之后直接输入“用 xcoze search 搜索一个公开主题，附来源”。

## Codex 目录示例

macOS/Linux 可使用 `~/.codex/skills/xcoze-search/`。如果设置过 CODEX_HOME，按对应目录的 skills 子目录安装。其他支持 Agent Skills 的宿主需查其技能目录及执行权限。

目录应包含：

```text
xcoze-search/
  SKILL.md
  agents/openai.yaml
  scripts/xcoze_search.py
  scripts/setup.command
  references/setup.md
  references/providers.md
  references/output.md
  README.md
  INSTALL.zh-CN.md
  LICENSE
```

不支持运行本地命令的纯聊天环境无法使用本包 Python 执行器。本包不是远程 MCP 服务，也不是独立网页 App。

## 升级与卸载

升级时用新 Skill 文件替换程序目录；密钥配置在用户目录外置保存，无需随包迁移。不要把旧目录内意外存在的私密文件带进发布包。

卸载时移除安装的 xcoze-search 文件夹即可。需要撤销 Key 时，另行在供应商控制台撤销并删除本机专用配置/相关环境变量；卸载程序本身不撤销密钥。
