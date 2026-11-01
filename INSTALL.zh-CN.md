# 安装与首次验证

1. 安装 Python 3.10 或更高版本，执行 `python3 --version`（Windows 可用 `py -3 --version`）。
2. 解压 Skill 发布 ZIP，将其中的 `xcoze-search` 文件夹复制到助手的技能目录。
3. 确认入口只有一层：`<skills>/xcoze-search/SKILL.md`。
4. 在该目录打开自己的终端，运行以下任意一个配置命令，隐藏输入对应服务 API Key：

```bash
python3 scripts/xcoze_search.py setup --provider deepseek --default --verify
python3 scripts/xcoze_search.py setup --provider yuanbao --verify
```

只用一家就只配置一家。`--verify` 会执行一次可能计费的搜索；输出 `search_verified:true` 才表示本次实测通过。密钥获取入口和具体服务要求见 [配置说明](references/setup.md)。

5. 新建一轮对话，输入“用 xcoze search 搜索一个公开主题，附来源”；宿主未发现技能时重启/重新载入。

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
