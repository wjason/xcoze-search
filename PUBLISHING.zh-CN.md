# GitHub 与通用商城发布

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

推荐首次发布：tag `v0.1.0`，标题 `xcoze search v0.1.0`。GitHub Release 上传打包脚本生成的 Skill ZIP、源码 ZIP 和 SHA256SUMS.txt。CI 会运行 Python 3.10/3.12 的离线测试。

若未完成真实账号验证，保留 Pre-release 标记，并在 Release 中声明待验证项。测试通过不代表供应商账号、余额、配额或商城兼容性已通过验收。

## 可直接使用的 Release 说明

xcoze search v0.1.0 增加 DeepSeek 与腾讯元宝官方 API 搜索集成，支持单源选择、显式双源检索、DeepSeek 网页 Markdown 抓取、隐藏输入密钥和环境变量配置。

统一结果保留供应商、来源和原生评分，区分元宝动态摘要与网页正文；双源部分失败时保留已有结果并明确报错。仅依赖 Python 3.10+ 标准库。

验证状态以同版本 VALIDATION.md 为准。该项目为 XCoze 独立集成，非 DeepSeek/腾讯官方 Skill。API 可能计费。

## 通用技能商城

本次尚未指定商城，先提供标准 Agent Skills 目录/ZIP。参考 MARKETPLACE.zh-CN.md 填写名称、介绍、依赖、数据流、示例和仓库。

商店可能要求根目录直接是 SKILL.md，也可能接受包含 xcoze-search/ 的 ZIP；按实际上传器要求解压选择目录，避免嵌套两层。若平台要求 manifest、图标、签名、隐私政策链接或专有 CLI，应在确认该平台文档后补齐，不伪造通用认证字段。

本包不包含商城密钥，不自动登录、创建远程仓库、推送或提交审核。

## 维护

供应商接口/服务版本变化后，先更新 references/providers.md 和协议测试，再实测并发布新版本。程序、SKILL metadata、README、打包资产版本需一致。用户密钥始终保存在发行包之外。
