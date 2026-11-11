<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 许可证（参见 LICENSE 文件） -->
<div align="center">
  <img src="../../assets/omega-track.png" alt="Omega-Track" width="386">
</div>

# 🛰️ OMEGA-TRACK

**数字身份画像与网络路径观测**

> 由 [kraynux](https://github.com/kraynux) 为 [Omega-Server](https://kraynux.snake-mackarel.ts.net) 开发   

官方页面：[OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; 预览：[Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 界面和导出的报告提供 **17 种语言** —— 参见[界面语言](#界面语言)。  
**语言：**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track** 是一个 TUI + CLI 工具，它从一个 IP、一个 IPv6 地址或一个域名出发，构建尽可能完整的数字身份：这个目标背后是谁在应答，流量如何到达那里，以及每条信息可以被视为确定的置信程度。它是 `omega-` 套件中的一个工具，采用 Clean Architecture 结构 —— 完整细节参见 `docs/PRODUCT_SCOPE.md` 和 `docs/DATA_SOURCES.md`。

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/zh-CN/omega-track/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/zh-CN/omega-track/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/zh-CN/omega-track/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/zh-CN/omega-track/D.png" width="24%" />
</p>

## 1. 愿景与范围

Omega-track 回答两个问题：“这个目标是谁？”（RDAP/DNS/证书/信誉身份）以及“如何到达那里？”（NeoTrace 网络路径、GeoIP、ASN）。它补充了 `omega-check`（网络暴露面）、`omega-scan`（HTTP/HTTPS 卫生）和 `omega-deep`（有边界的架构分析），而不与它们重复。

### Omega-track 做什么

- 接受 IP、IPv6 或域名形式的目标，可保存并可选择固定（持久授权）。
- 汇集公开信息，被动获取或由配置文件明确启用（RDAP、DNS、Certificate Transparency、Wayback 存档、BGP 公告）。
- 执行增强的 NeoTrace 式 traceroute（产品核心中唯一的主动网络操作）。
- 借助本地 GeoIP 数据库丰富每个相关 IP（无需密钥的 DB-IP Lite，可选使用密钥的 MaxMind GeoLite2）。
- 使用用户提供的密钥查询信誉来源（VirusTotal、HIBP），在任何启用之前都会明确披露（配额、发送的数据）。
- 将观测到的数据关联起来，形成一致的画像，并为每项数据给出明确的置信等级。
- 在本地保存目标、执行、结果、错误和导出（SQLite，`./var/`）。
- 提供功能上严格等价的 Textual TUI 和 CLI。
- 生成 HTML 报告（5 种主题，内嵌 Mermaid 关系图）、JSON、Markdown、CSV，以及独立的 DOT 和 Mermaid 文件。

### Omega-track 不做什么

| 功能 | 负责的工具 |
|---|---|
| 端口扫描、服务与横幅识别 | OMEGA-CHECK |
| HTTP/HTTPS 检查、头部、TLS、Web 卫生 | OMEGA-SCAN |
| 爬取、架构遍历以及深入关联目标 | OMEGA-DEEP |
| 远程逐页爬取（链接、文件） | OMEGA-FOLD |
| 负载测试 | OMEGA-STRESS |
| 模糊测试与应用健壮性测试 | OMEGA-FUZZ |

应避免的事项，包括 MVP 之外：子域名暴力枚举、端口扫描、Web 爬取、侵入式收集个人数据、自动绕过防护、对需要身份验证的平台进行脆弱的抓取、搜索人员/社交网络/pastebin 泄露、对目标进行周期性/重复监控（参见 `docs/PRODUCT_SCOPE.md` §7 “有意推迟”）。

### 授权使用提示

Omega-track 是一个用于合法用途的网络调查工具：审计您自己的基础设施、事件响应、监视您有权记录的范围。收集几乎完全是被动/公开的（RDAP、DNS、CT 日志 —— 目标或其注册商已公开的数据），唯一的例外是 traceroute（轻度主动，始终在所用配置文件中可见）。

**任何观测都不会在未固定的目标上启动，除非有明确确认**（CLI 中为 `--authorize`，TUI 中为确认操作）。您独自负责核实您的使用符合适用法律以及所查询第三方来源的使用条款。

## 2. 安装

### 前提条件

- Python 3.10+
- 互联网连接，用于依赖项和所查询的被动来源
- 已安装 `traceroute` 或 `tracepath`（NeoTrace 模块）—— 缺少时会平稳降级，工具其余部分正常工作

### 安装

```bash
[ -d omega-track ] && echo "ℹ️ 已在此处解压，跳过此步骤。" || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`：

1. 如果虚拟环境 `.venv` 尚不存在，则创建它。
2. 安装依赖项（`pip install -e .`，`pyproject.toml` 仍是唯一的事实来源）。
3. 使 `omega-track.sh` 和 `install.sh` 可执行。
4. 将别名 `track` 添加到 `~/.bashrc` 和 `~/.zshrc`（如已存在则不重复添加）。

### 依赖项

在 `pyproject.toml` 中声明（没有单独的 `requirements.txt`）：
- `omega-lib`：套件的共享库（`ConfidenceLevel`、主题、终端检测）
- `textual`：TUI 界面、主题、自动适配终端
- `dnspython`：正向和反向 DNS 解析
- `httpx`：RDAP/CT/存档/BGP/VirusTotal/HIBP 探测
- `maxminddb`：读取本地 GeoIP 数据库（DB-IP Lite、MaxMind GeoLite2）
- `jinja2`：HTML 导出的模板
- 开发依赖项（`pip install -e ".[dev]"`）：`pytest`、`pytest-asyncio`、`pytest-cov`、`pytest-httpserver`、`ruff`、`mypy`、`import-linter`

## 3. 使用

### 交互模式（TUI）

推荐日常使用 —— 不带参数启动：

```bash
./omega-track.sh
```
如果您创建了别名，只需在终端中输入 `track`：
```bash
track
```

流程：启动画面（按任意键或点击关闭）→ 主菜单（目标 / Tracker / 结果 / 历史 / 仪表盘 / GeoIP / 密钥来源 / 设置 / 帮助）→ 输入或选择目标（如未固定需明确确认）并选择收集模块 → 观测（实时显示进度条和操作过程，可取消）→ 按标签页查看详细结果（身份/DNS/网络 / ASN/NeoTrace/证书/存档/关系/诊断，导出）→ 从主菜单进入历史/仪表盘/设置。终端适配（颜色、尺寸、结构降级）是自动的。

#### 键盘快捷键

| 按键 | 操作 |
|---|---|
| `↑` / `↓` | 在屏幕的各项之间移动 |
| `Tab` / `Shift+Tab` | 在表单字段之间移动 |
| `Esc` | 返回上一屏幕（在主屏幕上确认退出） |
| `t` | 下一个主题（立即应用，无需确认） |
| `r` | 刷新终端检测 |
| `a` | 显示帮助 |
| `q` | 退出（需确认） |

### 界面语言

界面提供 17 种语言：法语、英语、西班牙语、葡萄牙语（巴西）、意大利语、德语、荷兰语、波兰语、俄语、简体中文、越南语、泰语、印度尼西亚语、日语、韩语、印地语和阿拉伯语。在设置（“Langue / Language”）中选择，重启界面后生效；变量 `OMEGA_TRACK_LANG`（例如 `OMEGA_TRACK_LANG=zh_CN ./omega-track.sh`）可在一次会话中强制使用某种语言。从 omega-suite 启动时，omega-track 使用套件的语言。在 Linux 文本控制台（TTY）上，非拉丁文字的语言在该会话中以英语显示。命令行保持为法语。

### 联系与支持

帮助（`a` 键）提供 **联系与支持** 界面：*请我喝杯咖啡*（开发者的 PayPal 页面）、*联系支持*（明文显示的电子邮件地址和网站联系表单）、*登记为用户（匿名）* 和 *检查更新*。 登记是自愿的，默认关闭，且只发送一次：仅用于统计用户数量，以及（如您愿意）其所在的大洲或国家（封闭列表，绝无自由文本）。它发送一个随机生成的密钥、软件名称（`omega-track`）及其版本；绝不发送姓名、机器名称、设置、目标或结果。IP 地址不会记录在登记中，但与任何访问一样，会经过接收服务器的安全检查和日志。 可随时在同一界面撤回（*不再登记我*）。 检查更新仅读取网站上已发布版本的列表，且从不在未点击的情况下进行。

### 脚本模式（CLI）

任何子命令都会触发 CLI 模式：

```bash
# 目标
./omega-track.sh target add example.org --alias "展示网站" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# 启动并跟踪一次观测
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# 历史
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# 导出 —— 6 种格式，HTML 有 5 种主题
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# 带密钥的信誉来源（在任何保存之前显示披露信息）
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <api_密钥>

# 设置与清理
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# 本地诊断（版本、能力、路径、GeoIP 状态）
./omega-track.sh diagnostics
```

所有子命令都接受 `--json`，以输出严格的机器可读格式。

#### 退出码

| 代码 | 含义 |
|---:|---|
| `0` | 成功（观测完成，`COMPLETED`） |
| `1` | 验证错误（无效目标、未知导出格式、无效状态转换、缺少 API 密钥……） |
| `2` | 目标未授权（既未固定，也没有 `--authorize`） |
| `3` | 资源未找到或来源不可用（未知目标/执行、GeoIP 下载失败） |
| `4` | 部分观测（`PARTIAL`）—— 不是失败，只有部分模块成功 |
| `5` | 意外的内部错误 |
| `130` | 被用户中断（`Ctrl+C`） |

### 接受的目标格式

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 域名
```

## 4. 收集模块

| 模块 | 收集模式 | 默认启用 | 需要密钥 |
|---|---|:---:|:---:|
| `dns` | 轻度主动（正向解析） | 是 | 否 |
| `reverse_dns` | 轻度主动（PTR） | 是 | 否 |
| `rdap` | 公开被动 | 是 | 否 |
| `neotrace` | 轻度主动（traceroute/tracepath） | 是 | 否 |
| `certificate_transparency` | 公开被动（`crt.sh`） | 否 | 否 |
| `archives` | 公开被动（Wayback Machine） | 否 | 否 |
| `bgp` | 公开被动（RIPEstat） | 否 | 否 |
| `virustotal` | 使用用户密钥 | 否 | 是（免费） |
| `hibp` | 使用用户密钥 | 否 | 是（2022 年起**付费**） |

前四个模块构成 MVP 基础（`dns`/`reverse_dns`/`rdap`/`neotrace`），在启动表单中默认勾选；后五个是可选的，必须明确启用。未配置密钥的来源绝不会导致观测失败：对应模块只是变为 `SKIPPED`（“未执行”）。各来源详情、配额和许可：`docs/DATA_SOURCES.md`。

## 5. 架构

Omega-track 采用 **Clean Architecture** 结构（domain / application / infrastructure / interfaces / ports / core / app / plugins），与 `omega-` 套件的模板保持一致（参见 `omega-check`/`omega-fold`），并在每次修改时由 `import-linter` 检查。

```text
src/omega_track/
├── domain/          纯业务逻辑（目标、TrackRun/ModuleRun、findings、关系、画像……）
├── application/     用例（commands/queries/阶段编排器/策略）
├── ports/           应用所期望的契约（收集器、仓储、导出器……）
├── infrastructure/  具体实现（dnspython/httpx/subprocess/maxminddb、SQLite、jinja2）
├── interfaces/      tui/（Textual）和 cli/（可脚本化），功能严格对等
├── app/             组装（DependencyContainer、启动引导、生命周期）
├── core/            跨层词汇（版本、omega-lib 的再导出）
└── plugins/         单一来源的可选模块（CT、存档、BGP、VirusTotal、HIBP）
```

设计规则：
- `domain/` 从不进行网络或 I/O 操作；`infrastructure/` 负责网络和 I/O，但从不做判断。
- `interfaces/` 只负责显示，不含任何业务逻辑 —— CLI 和 TUI 严格调用相同的用例。
- 1 个收集模块 = 1 个来源 = 1 个状态（`ModuleRun`）：绝不把两个来源合并在一个含糊的状态下。
- 单个字段缺失绝不算错误；只有来源完全不可用才会触发 `SKIPPED`/`FAILED`。

## 6. 数据来源

| 来源 | 提供方 | 密钥 | 模式 |
|---|---|:---:|---|
| 正向/反向 DNS | 系统解析器 | 否 | 轻度主动 |
| RDAP | IANA 引导 → RIR/注册商 | 否 | 公开被动 |
| Certificate Transparency | `crt.sh`（Sectigo） | 否 | 公开被动 |
| Web 存档 | Wayback Machine（Internet Archive） | 否 | 公开被动 |
| BGP / 网络公告 | RIPEstat（RIPE NCC） | 否 | 公开被动 |
| GeoIP | DB-IP Lite（默认）或 MaxMind GeoLite2 | 否 / 是 | 离线（本地数据库） |
| NeoTrace | 本地 `traceroute`/`tracepath` | 否 | 轻度主动 |
| 信誉 | VirusTotal | 是（免费） | 使用密钥 |
| 信誉 | Have I Been Pwned | 是（付费） | 使用密钥 |

各来源的确切配额、许可和备用方案：`docs/DATA_SOURCES.md`。任何 API 密钥都不会出现在日志、导出或诊断屏幕中。

## 7. 置信策略

每个收集到的字段都带有以下等级之一（通过 `omega-lib` 与整个套件共享）：

| 等级 | 含义 |
|---|---|
| `VERIFIED` | 直接观测到的协议事实，目标无法伪造（例如：直接的 DNS 应答、本地 traceroute 测量）。 |
| `DECLARED` | 来源在其完全控制的字段中自行声明的值（例如：注册商显示的 RDAP 数据）—— 可信，但可随意伪造。 |
| `CORROBORATED` | 由独立线索证实的 `DECLARED` 值（例如：在至少两个不同的 Certificate Transparency 日志中观测到的域名）。 |
| `INFERRED` | 由模式/启发式推断，没有明确声明（例如：用共同 ASN 来暗示某种关系，绝不会自动提升等级）。 |
| `UNKNOWN` | 没有可用线索，或被目标主动隐藏。 |

一次观测的整体置信分数是阅读辅助，绝不是安全结论。

## 8. 收集级别、授权与脱敏

每个配置文件都会明确其操作的性质（`CollectionMode`）：

- **离线**：目标验证、本地 GeoIP 读取、对已存储数据的关联、导出 —— 不使用网络。
- **公开被动**：RDAP、公共 DNS、CT 日志、存档、BGP —— 只有所查询的目标会传给第三方，这是协议固有的特性。
- **轻度主动**：DNS 解析、反向 DNS、traceroute —— 本机配置的解析器以及路径上的每个中间路由器都能看到请求。
- **使用用户密钥**：要求密钥或实行配额的提供方，仅在明确配置并显示披露信息（配额、发送的数据）后启用。

**授权保护**：任何观测都不会在未固定的目标上启动，除非有明确确认（CLI 中为 `--authorize`，TUI 中为复选框）。固定一个目标即为其今后的观测授予持久授权。

**导出脱敏**：每次导出都可接受一种策略（`none`/`contacts_only`/`sensitive_only`/`strict`），在导出结果中隐藏敏感字段（尤其是 RDAP 联系人）—— 而本地存储始终保留收集到的完整数据。详情：`docs/PRIVACY.md`。

## 9. 终端兼容性

TUI（Textual）会自动检测终端的能力（模拟器、尺寸），并据此调整其结构样式表（`complete`/`standard`/`reduced`/`mono`），无需手动标志。CLI 模式始终保持纯文本，与终端无关。该策略由整个 `omega-` 套件共享（`omega-lib`，`terminal/policies.py`）。

### 按检测到的模拟器划分的配置

| 模拟器 | 初始配置 |
|---|---|
| Ghostty、Alacritty、WezTerm、Kitty | `complete` |
| Konsole、GNOME Terminal、Terminator、Xfce4 Terminal | `standard` |
| xterm、urxvt、现代 SSH | `reduced` |
| Linux TTY、旧式 SSH | `mono` |
| 无法识别的模拟器 | `reduced`（默认备用） |

### 按终端尺寸划分的配置

| 最小尺寸（列 × 行） | 配置上限 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| 更小 | `mono` |

最终采用的配置是**两者中更严格的那个**（模拟器和尺寸）。可用 `r` 键实时刷新。

## 10. 导出

Markdown 和 HTML 报告使用设置中选择的语言撰写（“导出语言”，默认与界面相同）；JSON、CSV、DOT 和 Mermaid 仍是数据，不会被翻译。报告默认生成在 `var/exports/`（运行时路径锚定在项目文件夹，可用 `$OMEGA_TRACK_VAR_DIR` 覆盖），或生成在指定路径（CLI 中为 `--output`，TUI 中为对话框）。带时间戳的唯一文件名：`{时间戳}_{目标}_{短id}.{扩展名}`。

| 格式 | 内容 |
|---|---|
| `json` | 观测的完整结构（`TrackRun` + findings + 关系），事实来源，严格可序列化为 JSON |
| `markdown` | 紧凑的人类可读报告，可在终端外阅读 |
| `html` | 独立的网页报告，5 种主题可选（`--theme`），内联嵌入 Mermaid 关系图 |
| `csv` | 每个 finding 类别一张表 |
| `dot` | Graphviz 关系图，独立文件 |
| `mermaid` | Mermaid 关系图，独立文件 |

## 11. 历史、清理与重放

每次观测都会持久保存（SQLite，`var/db/omega-track.db`）：可浏览和筛选的历史（目标/状态/标签/时段），汇总仪表盘（按状态分布、各模块可靠性、最新 findings 的类型），在同一目标上重放观测而无需重新输入（`track replay`），以及在任何删除之前都会先预览的旧历史清理（先 `cleanup preview` 再 `cleanup run --yes`）。

## 12. 测试

```bash
source .venv/bin/activate
lint-imports        # 检查 Dependency Rule
pytest -q           # 485 个测试
ruff check .
mypy src
```

结构：`tests/unit/`（领域与应用，无真实 I/O），`tests/integration/`（真实的 SQLite/文件、模拟 HTTP 服务器 `pytest-httpserver`、通过 Textual 的 `Pilot` API 进行的无界面 TUI）。

## 13. 范围之外

- 完整的 WHOIS/DNS 历史、商业 passive DNS
- 搜索人员、社交网络、pastebin/泄露
- 端口扫描、服务与横幅识别（`omega-check`）
- HTTP/HTTPS 检查、头部、TLS（`omega-scan`）
- 爬取与架构遍历（`omega-deep`/`omega-fold`）
- 负载测试（`omega-stress`）、模糊测试（`omega-fuzz`）
- 交互式 TUI 地图（仅保留在导出的 HTML 报告中）
- 连续、多探针、多观测点的 MTR
- 对目标的批处理/周期性模式或重复监控 —— `TrackRun` 始终是一次明确的手动操作
- SQLite 模式迁移引擎（增量式模式，与套件其余部分的做法相同）

---

> Omega-track —— 观测、关联、定性、报告。
> 对每项数据都给出明确置信度的数字身份，绝不是伪装的确定性。
