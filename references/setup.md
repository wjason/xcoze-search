# 配置与排错

## Agent 引导配置（默认入口）

用户直接说“配置 xcoze search”“配置 DeepSeek”“更换元宝密钥”即可进入。由 Agent 从 SKILL.md 所在目录定位脚本，不要求用户查找安装目录或配置文件。

1. 用 `status` 检查配置状态，仅展示是否配置及凭据来源，不读取配置文件内容。用户未指定服务时，询问 DeepSeek 或元宝；两家可分别配置。
2. **在对话中输出对应的官方密钥申请链接，交由用户点击；不要自动打开浏览器、申请页面或充值页面。** 提醒使用正确服务的 Key，不让用户将 Key 回复到聊天。
3. 用户准备好输入后，说明本地会出现隐藏输入窗口，密钥以权限保护的明文保存；保存后执行一次可能计费的搜索。已有环境变量时先提醒其优先于本地保存值；配置不会替用户修改环境变量。
4. 运行以下命令启动输入窗口。密钥只从窗口进到本地配置脚本的内存中，不出现在 Agent 的 stdout/stderr、参数或聊天记录里。

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider deepseek --gui --verify
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider yuanbao --gui --verify
```

只执行目标服务的一条命令。只有用户要求更改默认源时才加 `--default`。`<skill_dir>` 替换为实际绝对路径；Windows 没有 python3 时用 `py -3`。

5. 等待用户完成窗口输入再读取结果。用户取消时不保存、不验证，也不自动重开窗口。验证成功需检查目标供应商 `search_verified:true`；保存成功不代表验证成功，验证失败时保存的配置仍在。报告服务、结果和可操作错误即可，不输出密钥。

窗口实现：macOS 使用 AppleScript 隐藏输入；Windows 使用系统 Windows PowerShell/WinForms 密码框；Linux 图形桌面使用已有 Zenity。输入窗口约 5 分钟后超时。无可用桌面/工具时返回 `gui_unavailable` 或 `gui_failed`，不自动安装依赖或转用明文输入。Agent 应解释原因并提供定位到实际脚本的可见终端命令或环境变量方式，不把用户带进 Agent 捕获的 PTY。当前仍需 Python 3.10+，并非独立可执行版本。

在远程 Agent 中，窗口显示在脚本实际运行的机器；只有用户能访问该桌面时才使用 `--gui`，否则走终端/部署凭据方式。

## 官方申请入口与手动配置

下面不带 `--gui` 的命令只在用户自己的可见终端执行。不通过 Agent 捕获的 PTY、聊天、参数或管道输入密钥；终端不能隐藏输入时拒绝继续。

## DeepSeek

在 [DeepSeek 平台](https://platform.deepseek.com/api_keys) 创建 API Key，确认账号可调用 Search / Fetch。聊天会员和 API 服务不是同一项权益。

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider deepseek --default --verify
```

## 元宝

在 [腾讯云元宝搜索控制台](https://console.cloud.tencent.com/wsapi/index) 开通搜索服务，然后在“概览 → 服务 API KEY 方式”创建服务密钥。这里需要的是 **元宝搜索服务 API Key**，不是腾讯云 SecretId/SecretKey、混元、TokenHub 或 Coding Plan 的 Key。资格、版本和额度以控制台为准。

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" setup --provider yuanbao --verify
```

两家可只配置一家，也可分别配置。只有 `--default` 才改变默认源。`--verify` 会执行一次可能计费的真实搜索；不加它只保存，不联网。setup 不打开网页、不读取剪贴板、不自动登录或充值。

## 环境变量与存储

优先级：对应环境变量 → 本技能专用配置文件。

| 供应商 | 首选环境变量 | 兼容变量 |
|---|---|---|
| DeepSeek | `DEEPSEEK_API_KEY` | 无 |
| 元宝 | `YUANBAO_API_KEY` | `TENCENTCLOUD_WSA_APIKEY` |

环境变量应由用户/密钥管理系统注入实际运行 agent 的进程。已有 agent 不会自动继承新终端变量。不读取 `.env`、浏览器登录态或其他 Skill 的凭据；迁移旧 Key 需用户自行在 setup 中输入。

保存位置为 `${XDG_CONFIG_HOME:-~/.config}/xcoze-search/config.json`（文中 shell 记法仅说明路径）。文件是**权限保护的明文**，不是加密保险箱。POSIX 专用目录 700、文件 600，拒绝专用目录/文件符号链接；XDG_CONFIG_HOME 必须为绝对路径。Windows 使用用户目录继承的 ACL；共享主机请用受控环境变量/密钥管理系统并核对 ACL。安装目录、仓库和 ZIP 不包含配置。

现有环境变量会覆盖 setup 新保存的值，setup 会提示，`--verify` 验证的是实际生效的凭据。

## 检查与清理

```bash
python3 "<skill_dir>/scripts/xcoze_search.py" status
python3 "<skill_dir>/scripts/xcoze_search.py" doctor --provider deepseek
python3 "<skill_dir>/scripts/xcoze_search.py" doctor --provider yuanbao
python3 "<skill_dir>/scripts/xcoze_search.py" doctor --provider both
```

status 不联网、不显示密钥，每次显示 `search_verified:false`；doctor 不持久缓存“成功”状态，每家一次搜索，无自动重试。doctor 非空结果才成功。返回 200 但空结果时，换实际主题再查，不能据此说搜索已验证。

卸载 Skill 只移除程序；要清理 Key，用户在自己的终端移除配置文件、清理相关环境变量，并在官方平台撤销密钥。卸载程序不会撤销平台 Key。

| 错误/现象 | 处理 |
|---|---|
| `missing_api_key` | 对目标供应商运行 setup，或向实际运行进程注入变量 |
| `interactive_required` | 改在自己的可见终端运行 setup |
| `gui_unavailable` / `gui_failed` | 当前桌面或窗口工具不可用，改用自己的可见终端/受控环境变量，不改成聊天或明文输入 |
| `cancelled` | 用户取消或输入超时，未保存本次输入；准备好后由用户决定是否重新配置 |
| `unsafe_config` | 核对专用目录 700、文件 600 和符号链接；不要放宽权限 |
| `invalid_config` | 在用户终端备份/修复本技能配置，或移除后重新 setup；不要贴出文件内容 |
| HTTP 401 / `UnauthorizedOperation` | 核对实际生效的密钥、开通状态及授权 |
| HTTP 402 / `ResourceUnavailable` | 在平台核对余额/服务状态，自行决定充值 |
| `ResourceNotFound` | 在腾讯云开通元宝搜索，等待生效 |
| `InvalidParameter*` | 检查服务版本与可选参数；先用无垂域/模式且 count<=10 的基线请求 |
| HTTP 429 / `RequestLimitExceeded` | 降低频率，稍后重试 |
| `invalid_response` | 保留错误码、时间和 RequestId（若已有），核对最新官方结构；不要提交 Key |
| `network_error` / `retry_later` | 检查网络/TLS/系统时钟；稍后重试 |
| DeepSeek Fetch 403/404 | 页面受限或无法提取，换公开来源，不绕过访问控制 |
| `--provider both` 参数错误 | 两家专属选项分开调用，不静默丢弃条件 |

完整错误输出经过收敛处理，不回显服务器原始错误正文或任意错误消息。
