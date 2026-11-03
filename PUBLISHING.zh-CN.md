# GitHub 与通用商城发布

**简体中文** | [English](PUBLISHING.en.md)

仓库：[wjason/xcoze-search](https://github.com/wjason/xcoze-search)。本文件说明后续版本维护与商城提交流程；实际上传状态以 GitHub 代码及 Release 页面为准，GitHub 上有源码不等于商城已审核收录。

## 发布前准备

1. 确认 XCoze 维护方名称与 MIT 授权符合你的发布意图。
2. 用自己的账号分别运行 DeepSeek/元宝 doctor，记录是否得到有效结果；进一步验证真实 Fetch 和元宝账号版本相关参数。不能以离线 mock 测试替代真实服务验证。
3. 核对 README 的仓库和安装地址；在商城填入仓库地址和联系方式。
4. 执行测试并核对验证记录；确认仓库中没有 config.json、Key、.env、日志、个人文件或缓存。

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py --output-dir ../release
```

## GitHub

本仓库根目录直接含 SKILL.md。后续修改在此仓库提交并推送，不要把最外层的 outputs 或 release 文件夹作为 Skill 根目录。

当前版本为 `v0.4.0` 预览版。推送 `v*` 标签会触发 `.github/workflows/release.yml`，复用 Windows/Linux、Python 3.10/3.12 四组离线测试；全部通过后才进入发布步骤。

发布步骤会核对标签、程序版本、Skill 元数据、打包版本和 CHANGELOG，提取当前版本的发布说明，生成 Skill ZIP、源码 ZIP 和 SHA256SUMS.txt，再核对校验值。先创建带完整附件的草稿，再公开为 Pre-release；不覆盖已有 Release 或旧附件。

发布使用 GitHub Actions 提供的临时 `GITHUB_TOKEN`，仅发布作业申请 `contents: write`，不需要配置个人 GitHub Token，也不使用搜索服务的密钥。若仓库策略拒绝写权限，工作流会失败，需先检查 Actions 诊断；不能把失败视为已发布。

维护者发布下一版本时：

1. 更新程序、Skill 元数据和构建脚本中的版本，补齐 CHANGELOG 的同版本日期段落，并更新下载链接与验证记录。
2. 本地运行下列命令，确认版本检查、测试及包内容通过。
3. 提交并推送代码，然后为该提交创建并推送新版本标签。标签应与程序版本一致，不移动或重用已发布标签。
4. 等待标签发布工作流成功，检查 Release 的 Pre-release 标记、三个附件及校验值，再确认发布完成。

```bash
python3 scripts/prepare_release.py --tag v0.4.0 --output ../release-notes.md
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py --output-dir ../release
```

旧版 `v0.1.0`、`v0.2.0` 的标签与附件保留，不用新版本文件覆盖。

若未完成真实账号验证，保留 Pre-release 标记，并在 Release 中声明待验证项。测试通过不代表供应商账号、余额、配额或商城兼容性已通过验收。

## v0.1.0 Release 说明（历史）

xcoze search v0.1.0 增加 DeepSeek 与腾讯元宝官方 API 搜索集成，支持单源选择、显式双源检索、DeepSeek 网页 Markdown 抓取、隐藏输入密钥和环境变量配置。

统一结果保留供应商、来源和原生评分，区分元宝动态摘要与网页正文；双源部分失败时保留已有结果并明确报错。仅依赖 Python 3.10+ 标准库。

验证状态以同版本 VALIDATION.md 为准。该项目为 XCoze 独立集成，非 DeepSeek/腾讯官方 Skill。API 可能计费。

## 双语发布说明

默认导出中文。`--language en` 导出英文；`--language both` 将中文放在正文，英文放入可展开的 English 区域。标签工作流使用 both，并核对中英文 CHANGELOG 都包含同版本日期段落；缺少英文记录时停止发布。

```bash
python3 scripts/prepare_release.py --tag v0.4.0 --language both --output ../release-notes.md
```

中英文文档及 Agent 指令已加入后续打包清单；现有已发布版本的标签和附件保持不变。

## 通用技能商城

本次尚未指定商城，先提供标准 Agent Skills 目录/ZIP。参考 MARKETPLACE.zh-CN.md 填写名称、介绍、依赖、数据流、示例和仓库。

商店可能要求根目录直接是 SKILL.md，也可能接受包含 xcoze-search/ 的 ZIP；按实际上传器要求解压选择目录，避免嵌套两层。若平台要求 manifest、图标、签名、隐私政策链接或专有 CLI，应在确认该平台文档后补齐，不伪造通用认证字段。

本包不包含商城密钥，不自动登录、创建远程仓库、推送或提交审核。

## 维护

供应商接口/服务版本变化后，先更新 references/providers.md 和协议测试，再实测并发布新版本。程序、SKILL metadata、README、打包资产版本需一致。用户密钥始终保存在发行包之外。
