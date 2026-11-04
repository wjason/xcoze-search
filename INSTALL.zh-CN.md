# 安装与首次使用

**简体中文** | [English](INSTALL.en.md)

## 让 Agent 安装

```text
安装 https://github.com/wjason/xcoze-search
```

Agent 检查 Python 3.10+，把 Skill 装到当前宿主技能目录，再按宿主要求重新加载或新建会话。基础运行只用 Python 标准库，不安装浏览器或其他运行依赖。安装时无需 Key；完成后直接正常提问即可。

## 命令行或手动安装

```bash
npx skills add wjason/xcoze-search --skill xcoze-search
```

这条可选安装方式需要 Node.js。也可下载 [v0.9.0 Skill ZIP](https://github.com/wjason/xcoze-search/releases/download/v0.9.0/xcoze-search-skill-v0.9.0.zip)，解压 xcoze-search 文件夹到技能目录；手动解压不需要 Node.js。

Codex 默认目录为 `~/.codex/skills/xcoze-search/`；设置 CODEX_HOME 时使用其 skills 子目录。其他宿主按其技能发现规则安装。本包不适用于无法执行本地脚本的纯聊天环境，独立可执行安装包仍在计划中。

## 首次使用

```text
找几个开源工业视觉项目，对比部署要求。
查一下最近一周这个主题有哪些官方更新。
```

没有 Key 使用免 Key 来源；有已配置且未禁用 Key 时默认效果优先。匿名限流、网络和搜索覆盖仍影响结果，安装成功不代表所有后端都在线。用户无需每次选择模式，偏好和指定来源见 [调度](references/routing.md)。

需要商用服务时再说“帮我配置 xcoze search 的 DeepSeek 搜索”。Agent 提供官方申请链接，不自动打开网页；用户准备好后使用本机隐藏输入窗口，不把密钥发到聊天中。图形桌面不可用时提供用户自己的可见终端隐藏输入或受控环境变量方式。见 [配置与排错](references/setup.md)。

## 升级、兼容与卸载

替换程序目录不会覆盖用户目录中的 Key。v0.4.0 保留 v1 读取、v2 格式和私有备份迁移；新增 search_preferences 是可选字段。普通查询不改写配置，保存偏好或成功保存 Key 时才按需迁移。

**行为变化**：auto 现在有限备用，默认 fetch 现在自动选路。需要旧版固定来源的调用方显式指定 `--provider deepseek` 等；both 仍只表示 DeepSeek＋元宝。恢复默认策略使用 preferences --reset，保留 Key。

v0.2.0 等程序不能读取 v2。降级需用户本机核对私有备份，该备份不包含后来新增/更换的 Key；旧版也不会执行新偏好。卸载只移除程序目录；如需清除凭据，应另行删除本地配置/备份、清理环境变量并在服务商撤销 Key。
