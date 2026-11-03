# 参与贡献

**简体中文** | [English](CONTRIBUTING.en.md)

欢迎提交缺陷修复、文档改进、测试样例和搜索源适配。

## 免 Key 与路由贡献

免 Key 适配器位于 scripts/public_providers.py，使用 PUBLIC_REGISTRY；共用 Provider 契约，requires_key:false，不能读取其他服务凭据。请求解码通过 decode_response 区分 JSON、SSE、RSS 或 HTML，验证页不得视为空结果成功。scripts/search_routing.py 只做离线能力与偏好规划，Agent 负责语义判断。路由改动需覆盖免费模式不发送 Key、显式覆盖、条件不丢失、预算停止及失败备用。新增运行文件和测试同时加入 build_release.py 允许列表，并同步中英文文档。

## 提交问题

在 [GitHub Issues](https://github.com/wjason/xcoze-search/issues) 说明使用环境、版本、命令、期望结果和实际结果。排错材料仅提供错误码、脱敏 RequestId 和必要输出，不要上传 API Key、配置文件或私密查询。

新搜索源建议请附官方文档、需要的功能和鉴权方式，并参考 [开发计划](TODO.md) 中已有候选。涉及命令、配置或输出格式变更时，建议先在 Issue 中讨论兼容方案。

## 本地开发

要求 Python 3.10+，运行和离线测试只依赖标准库。

```bash
git clone https://github.com/wjason/xcoze-search.git
cd xcoze-search
python3 -m unittest discover -s tests -v
```

创建自己的分支后提交修改，再向 `main` 发起 Pull Request。说明修改解决的问题、用户可观察的行为及验证方式。

## 新搜索源适配

实现入口为 `scripts/search_providers.py`：继承 Provider，定义 name/label、固定官方端点、env_keys/key_url、鉴权头、能力和限制，实现 build_search、normalize；有提取接口时再实现 fetch_payload、normalize_fetch。最后把实例加入 REGISTRY。Brave 提供 GET 与专用鉴权头样例，Tavily/Exa 提供搜索和提取样例。

主搜索流程按注册表执行，无需新增服务分支。共享错误、URL/字段校验和 HTTP 预算位于 search_common.py；密钥读取、请求传输和 CLI 位于 xcoze_search.py。新增服务必须在联网前拒绝不支持选项，不能通过任意 URL 替代固定鉴权目标。

新增协议测试可参照 `tests/test_providers.py`：使用合成响应验证原生请求、鉴权、内容类型、空结果、业务错误、未知字段和逐 URL 失败；使用 QueueTransport 覆盖真实 request_api/规范化流程，不只 mock 主函数返回值。质量回归入口和语料位于 evaluations/，默认不联网。

扩展时仍需：

- 按当前官方接口实现，附文档地址和核对日期；官方 API、第三方代理和自建实例分别标明。
- 声明实际支持的搜索、正文、片段、过滤和分页能力；不支持的选项不得静默忽略。
- 保留来源、日期、供应商字段和评分语义，测试空结果、失败、限流和异常结构。
- 密钥存放在用户配置或进程环境中，测试使用合成凭据和临时目录；真实账号验证不进入默认 CI。
- 新增对外功能时同步更新 SKILL、README、接口参考、测试与 CHANGELOG。配置迁移需说明向后兼容和失败处理。

完整完成条件见 [TODO](TODO.md#新供应商的完成条件)。

## 双语文档维护

README.md 和现有中文文件保留为默认入口，英文对应文件使用 .en.md。修改说明时同步两种语言的命令、限制、验证状态、版本和链接。Agent 的默认中文/英文切换规则维护在 SKILL.md 和 SKILL.en.md。每份文档顶部须保留互相切换的链接；修改发行文件时同时更新打包清单。

## 文档与发布

README 面向使用者介绍项目和操作；规划写入 TODO，研究依据写入 references，版本差异写入 CHANGELOG。未实现的功能明确标为计划，离线测试和真实账号验证分别记录。

文档修正检查链接、示例和事实是否一致；运行时代码变更应运行相关测试。新增发行文件时检查打包清单，避免安装包中的文档链接失效。

Release 对应不可变标签与源码提交。已发布附件不原地替换；需要更新发行内容时使用新版本。`CHANGELOG.md` 的 Unreleased 部分描述尚未发布的变更。

提交贡献表示同意以本项目 [MIT License](LICENSE) 分发该贡献。
