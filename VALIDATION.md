# 验证记录

## v0.2.0 预览版 — 2026-11-02

- macOS 本地 33 项离线测试通过，新增 8 项配置窗口行为测试，使用合成密钥和临时配置目录，不读取或改动现有用户密钥，不发送真实 API 请求。
- 覆盖无 TTY 的窗口配置、取消保留原文件、失败/超时输出脱敏、空值/多行输入拒绝、有效环境变量优先、另一供应商配置保留，以及保存成功但验证失败的独立结果。
- macOS AppleScript 隐藏输入脚本通过 `osacompile` 编译检查；这只证明语法有效，不等于真实窗口输入验收。
- Skill 通过 `quick_validate.py` 检查；CLI 帮助和版本检查通过。
- 新增 3 项发布检查，验证版本不一致、缺少/空更新记录时会拒绝发布，以及发布说明只提取当前版本。合计 36 项本地离线测试通过。
- macOS、Windows、Linux 的真实桌面窗口输入/取消仍待人工验收。Windows/Linux CI 检查的是离线流程，不会打开窗口。
- v0.2.0 按预览版发布，标签工作流须通过 Windows/Linux、Python 3.10/3.12 四组测试，才创建包含安装包、源码包和 SHA-256 的 Release。v0.1.0 标签及附件保持不变；发布状态以 [Releases](https://github.com/wjason/xcoze-search/releases) 为准。

## v0.1.0 历史记录

日期：2026-10-24（接口研究与首次实测）；2026-11-02（GitHub 发布复核）。

发布复核：本地离线测试现为 25 项，包含显式 XDG_CONFIG_HOME 在用户主目录不可用时仍能生效的回归检查。跨平台运行结果见 [GitHub Actions](https://github.com/wjason/xcoze-search/actions/workflows/test.yml)，以下首次实测日期不代表持续在线监测。

## 已完成

- Python 3.10.4 / macOS：24 项 unittest 离线测试通过。测试使用自建合成响应和临时配置，不含真实 Key、真实搜索结果或生产请求。
- 独立场景验证：7 项行为检查通过。替换 urllib 传输层，保留真实 main/请求构建/配置/映射/退出码流程。
- Skill frontmatter 与完整目录通过 skill-creator quick_validate.py 校验。
- CLI 帮助、版本、无密钥 status 与缺密钥搜索、发布包提取后的入口检查通过。
- Markdown 本地链接、包文件清单、SHA-256、无缓存/OS 元数据/本地配置混入检查通过。

## 覆盖重点

固定官方端点/Bearer 构建、鉴权重定向拒绝、HTTP 401/402 不重试、429 有界重试、长 Retry-After 停止、元宝 HTTP 200 业务错误、异常/过大响应、Pages JSON 字符串解析、极速版可选字段缺失、摘要/全文区分、查询长度/过滤条件、both 专属参数联网前拒绝、默认源不静默切换、双源前置凭据检查、重复版本保留、单源空结果/双源部分失败区分、Fetch 边界、doctor 空结果不冒充成功、隐藏输入、环境变量优先、配置权限及符号链接拒绝。

独立场景重点：只配置元宝时自动路由及 Fetch 缺 DeepSeek Key；双源一家授权失败保留另一家证据并退出 4；setup 验证实际生效的环境变量凭据；status 不联网/不泄密。

## 真实账号实测

2026-10-24 16:10（北京时间）：使用用户在本机配置的 DeepSeek 凭据完成以下验证，未记录密钥或配置内容。

- Search：doctor 一次请求成功，返回 1 条有效结果，search_verified:true。
- Fetch：官方 Search & Fetch 文档页面抓取成功，返回非空 Markdown（10,282 字符），一次请求完成。
- 本次结果只证明该账号在本次调用时可用，不保证未来余额、配额、可访问性或所有查询的检索质量。

## 尚未验证
- 元宝真实服务 Key 的 SearchPro 在线成功响应、各账号服务版本的可选参数。
- Windows ACL 与终端隐藏输入的人工实测；Windows/Linux 的离线契约检查由 GitHub Actions 覆盖，结果以对应运行记录为准。
- 具体商城解析、审核、收录、认证和安装；商城尚未指定。
- 真实信息检索质量、研究结论的事实准确性。

因此本版本可供源码评审、离线验证和配置后试用，建议首次上传 GitHub 时标记 Pre-release。不能把合成响应测试称为“双服务已实测可用”。DeepSeek 状态已据本次实测更新；元宝需完成 doctor 后再更新相应状态，并验证版本相关选项。

## 复现

完整源码目录执行：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/xcoze_search.py --help
python3 scripts/xcoze_search.py --version
python3 scripts/build_release.py --output-dir ../release
```

独立评估临时脚本属于交付工作区证据，不是运行依赖或发行包内容；上述合约测试可在公开仓库复现。

## 在线验收建议

配置任意一家后分别执行 doctor，确认 search_verified:true；两家都有时再执行 both，确认每家返回有效结果；使用 DeepSeek Fetch 取得一个合法公开页面的非空 Markdown。仅记录供应商、脱敏 RequestId、条数、时间与成功/错误码，不记录密钥。服务版本相关参数按用户实际开通能力验证，不为通过测试自动升级或付费。
