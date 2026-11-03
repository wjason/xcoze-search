# 配置与排错

**简体中文** | [English](setup.en.md)

## 无 Key 开始与可选偏好

普通搜索无需配置 Key，安装后直接提问。仅在用户需要添加/更换商用服务时进入下面的配置流程。配置并启用 Key 后默认 Smart 采用效果优先；已保存的 free/balanced 等偏好继续优先，不因新增 Key 被覆盖。

由 Agent 执行 `preferences --strategy free|balanced|quality` 保存偏好；仅本次调整使用 search/fetch 的同名参数。`preferences --reset` 恢复 Smart 并清除默认源，保留密钥。`preferences --disable <ID>` 排除自动来源，`--enable` 恢复。详情见 [调度](routing.md)。这些命令不回显 Key、不联网，用户不用寻找配置文件。

## 对话配置（默认入口）

用户说“配置 xcoze search”“配置 Exa”“更换元宝密钥”即可进入。Agent 从 SKILL.md 所在目录定位脚本，不要求用户找安装目录或配置文件。

1. 用 status 检查配置和凭据来源，不读取/展示文件内容。用户未指定服务时确认目标；使用 capabilities 查看该服务 key_url 和环境变量。
2. **在对话中提供对应官方密钥申请链接，由用户自行点击；不自动打开浏览器、申请或充值页面。** 已有 Key 时无需重复申请；不让用户把密钥回复到聊天。
3. 用户准备好后，说明本地会显示隐藏输入窗口、当前采用权限保护的明文存储，以及验证会执行一次可能计费的搜索。若已有环境变量，先提醒它优先于保存值，不替用户改环境变量。
4. 执行目标服务的一条配置命令；路径替换为实际绝对路径，provider 可为 deepseek/yuanbao/tavily/exa/brave/bocha。

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" capabilities --provider tavily
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider tavily --gui --verify
```

只有用户要求改变默认源时才加 `--default`。等待输入完成；用户取消时不保存、不迁移、不验证，也不自动重开。只依据目标服务 search_verified:true 报告本次验证成功。验证失败时配置已经保存，需按具体原因处理，不能把保存当作可用。

macOS 使用 AppleScript 隐藏输入；Windows 使用 PowerShell/WinForms 密码框；Linux 图形桌面使用已有 Zenity。约五分钟后超时。工具不读取剪贴板，也不把子进程中的输入/错误正文回传给 Agent。窗口显示在脚本实际运行的机器；远程环境只有用户可访问该桌面时才用 `--gui`。

无可用窗口时报告 gui_unavailable/gui_failed，不自动安装桌面依赖、不改用明文或聊天输入。提供已定位实际路径的命令，让用户在自己的可见终端隐藏输入，或使用受控部署环境变量。不使用 Agent 捕获的 PTY 收集 Key。当前仍需 Python 3.10+。

## 官方入口和凭据类型

| 服务 | 官方入口 | 环境变量 |
|---|---|---|
| DeepSeek | [API Keys](https://platform.deepseek.com/api_keys) | DEEPSEEK_API_KEY |
| 元宝 | [搜索控制台](https://console.cloud.tencent.com/wsapi/index) | YUANBAO_API_KEY；兼容 TENCENTCLOUD_WSA_APIKEY |
| Tavily | [控制台](https://app.tavily.com/home) | TAVILY_API_KEY |
| Exa | [控制台](https://dashboard.exa.ai/api-keys) | EXA_API_KEY |
| Brave | [控制台](https://api-dashboard.search.brave.com/app/keys) | BRAVE_API_KEY |
| 博查 | [开放平台](https://open.bochaai.com/) | BOCHA_API_KEY |

元宝须先开通搜索，再在“概览 → 服务 API KEY 方式”创建搜索服务 Key。不能使用腾讯云 SecretId/SecretKey、混元或其他产品的 Key。聊天会员和 API 权益不等同；各家账号权限、额度与版本以官方平台为准。

## 手动终端配置

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider exa --verify
```

不带 `--gui` 时仅在用户自己的可见终端隐藏输入；输入无法隐藏时拒绝继续。Windows 可用 `py -3`。`--verify` 会执行可能计费的搜索，不加则只保存。macOS `scripts/setup.command` 保留六家服务的终端配置入口。

## 存储与迁移

凭据优先级：该服务环境变量 → 本技能专用配置文件。环境变量须注入实际运行 Agent 的进程；新终端变量不会自动进入已运行的助手。不读取 .env、其他 Skill、浏览器或应用凭据。

路径为 `${XDG_CONFIG_HOME:-~/.config}/xcoze-search/config.json`（此处 shell 写法仅说明路径）。当前为**权限保护的明文**；POSIX 专用目录 700、文件 600，拒绝专用目录/文件符号链接。XDG_CONFIG_HOME 必须是绝对路径。Windows 继承用户目录 ACL，未做人工 ACL 验收。配置和备份均不进入仓库或安装包。

v0.4.0 沿用 schema_version:2；可以直接读取 v1，status/搜索/doctor 不会改写它。需要显式升级时运行：

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" migrate-config
```

迁移先独占创建同目录的私有 `config.v1.backup.json`，再原子替换配置。保留原 Key、默认源和扩展字段，包括暂未注册服务的非默认配置。既有备份不被覆盖；格式未知、权限不安全或迁移失败时拒绝继续，保留原始密钥文件。输入成功后保存新配置也会先备份升级 v1；取消输入不会触发迁移。已是 v2 时迁移是无改动操作。

旧版程序不支持 v2；需要降级时由用户在自己的终端确认并恢复 v1 备份，核对密钥仍有效。备份是升级前的快照，不包含升级后新配或更换的 Key，不自动回退/撤销平台密钥。不要把备份内容发到聊天。

## 检查与清理

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" status
python3 "<skill_dir>/scripts/xcoze_search.py" doctor --provider exa
python3 "<skill_dir>/scripts/xcoze_search.py" doctor --provider deepseek,tavily --max-requests 2
```

status 不联网，显示配置来源、schema 和是否可迁移；search_verified 始终 false。doctor 每家一次真实搜索，零重试，不持久缓存成功；取得非空有效结果才通过。API 返回空结果时不能说已验证。

卸载只移除程序。清理密钥需用户在自己的终端移除本技能配置及备份，清理相关环境变量，并在对应平台撤销 Key；移除本地文件不会撤销平台密钥。

| 现象或错误码 | 处理 |
|---|---|
| missing_api_key / invalid_key | 为目标服务配置正确类型的 Key；不借用其他服务凭据 |
| interactive_required | 使用自己的可见终端，或在有桌面的环境选择 --gui |
| gui_unavailable / gui_failed | 改用可见终端或受控环境变量；不使用聊天/明文输入 |
| cancelled | 用户取消或超时，未保存本次输入，准备好后再发起 |
| unsafe_config / invalid_config | 在本机核对权限、符号链接、格式和备份；不要展示文件内容或放宽权限 |
| unsupported_option / unsupported_operation | 先看 capabilities；不同服务的条件分开调用，不丢弃条件或自动换源 |
| budget_exhausted | 预算已用尽或不足每家一次；由用户/任务预算决定是否增加，不自行无限重试 |
| HTTP 401/403 / UnauthorizedOperation | 核对生效凭据、授权和开通状态 |
| HTTP 402/432/433 / ResourceUnavailable | 到官方平台核对余额、额度和服务；用户自行决定充值 |
| HTTP 429/434 / RequestLimitExceeded | 降低频率，按有限重试和预算处理 |
| ResourceNotFound | 在腾讯云开通元宝搜索并等待生效 |
| InvalidParameter* / HTTP 400/422 | 核对字段及账号版本；元宝先用无垂域/模式且 count<=10 的基线 |
| constraint_not_applied | Exa 报告有字段被忽略，应调整选项，不能声称筛选已生效 |
| extraction_failed | 服务没有成功返回所请求页面；换公开来源，不绕过访问控制 |
| invalid_response / response_too_large | 记录服务、错误码、时间和已有脱敏 RequestId；不上传 Key 或原始错误正文 |
| network_error / retry_later | 核对网络/TLS/时钟；稍后重试 |

错误消息收敛处理，不回显服务商原始错误正文或任意错误消息。
