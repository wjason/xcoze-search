# 官方文档搜索

**简体中文** | [English](documentation.en.md)

查 API、参数和用法时，可以直接向官方文档检索。当前支持以下入口：

| 文档 | 平台参数 | 搜索方式 | 范围 |
|---|---|---|---|
| Python | `python-docs` | 下载官方 Sphinx 索引，在本机匹配关键词和 API 符号 | `/3/` 英文文档 |
| pandas | `pandas-docs` | 同上 | 当前 `/docs/` 英文文档 |
| SQLAlchemy | `sqlalchemy-docs` | 同上 | `/en/20/` 英文文档 |
| MDN Web Docs | `mdn` | 使用 MDN 公开站内搜索 | 英文文档 |

这些入口不依赖 Exa、Parallel、宿主搜索或用户 Key。普通提问由 Agent 选择；查询明确包含项目名和具体文档主题时，脚本也可识别上述已知官方范围。用户提供的站点或平台要求优先。

```bash
python3 scripts/xcoze_search.py search 'asyncio TaskGroup exception cancellation' --platform python-docs
python3 scripts/xcoze_search.py search 'merge validate one_to_one' --platform pandas-docs
python3 scripts/xcoze_search.py search 'select join' --platform sqlalchemy-docs
python3 scripts/xcoze_search.py search 'AbortSignal.timeout' --platform mdn
```

也可以使用 `--site docs.python.org`、`--site pandas.pydata.org`、`--site docs.sqlalchemy.org` 或 `--site developer.mozilla.org`，自动搜索时优先使用对应文档入口。指定 `--provider docs` 时须同时指定支持的 `--site`。

## 搜索结果与正文

Sphinx 搜索下载固定官方地址的 `searchindex.js`，以 JSON 读取，不执行其中的 JavaScript。匹配在本机完成，不向文档站发送查询词；没有自建服务器或索引部署步骤。每次检索会下载该站的索引，体积通常为数 MB。

结果类型为 `documentation_index`，包含标题、原文链接、可定位的 API 锚点和命中的词。它不包含正文摘要或发布日期。词形匹配仅覆盖有限英文后缀，不等同文档网站完整搜索算法。MDN 返回站点提供的摘要，类型为 `search_summary`。

需要解释行为、核对版本或引用具体段落时，Agent 仍须读取原文。缺少正文、发布日期或版本证据时，不能用索引命中替代。上述固定目录不会自动切换到用户指定的其他版本；暂不支持的日期、语言等参数会排除该入口或明确报错。

## 中文站点定向搜索

`so360` 使用 360 的公开 HTML 结果，不启动浏览器，也不使用用户登录状态：

```bash
python3 scripts/xcoze_search.py search '海上风电' --site nea.gov.cn --provider so360 --strategy free
```

适配器提取自然结果，使用页面中给出的目标地址，并再次检查域名。它会拒绝明显缺少主题、指定符号或年份的结果；短中文主题词也进行字面检查。检索不保证覆盖站内全部内容，结果不足时可继续使用当前模式允许的其他来源。

360 在本次批量测试中出现了验证码重定向，不能作为唯一备用。适配器不跟随验证链接、不处理验证码，识别后暂停 15 分钟。没有命中、出现验证和网络失败分别记录。详见[实测报告](../evaluations/reports/2026-11-16-keyless-search.md)。
