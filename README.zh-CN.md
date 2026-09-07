<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 许可证（见 LICENSE 文件） -->
<div align="center">
  <img src="docs/assets/omega-track.png" alt="Omega-Track" width="386">
</div>

# 🛰️ OMEGA-TRACK

**数字身份画像与网络路径观测**

> 由 **kraynux** 为 **Omega-server** 开发  
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

官方页面：[OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; 预览：[Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

**语言：**  
[Français](README.md) · [English](README.en.md) · [Español](README.es.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md)

---

**Omega-track** 是一款 TUI + CLI 工具，从一个 IP、IPv6 或域名出发，构建尽可能完整的数字身份：这个目标背后是谁、如何到达它，以及每条信息可以被视为确定事实的置信程度。它是 `omega-` 系列的第六款工具（继 `omega-fire`、`omega-stress`、`omega-scan`、`omega-check` 和 `omega-deep`/`omega-fold` 之后），采用 Clean Architecture 构建；完整细节见 `docs/PRODUCT_SCOPE.md` 与 `docs/DATA_SOURCES.md`。

## 1. 定位与范围

Omega-track 回答两个问题：「这个目标是谁？」（通过 RDAP/DNS/证书/信誉进行身份识别）以及「如何到达它？」（通过 NeoTrace、GeoIP、ASN 观测网络路径）。它与 `omega-check`（网络暴露面）、`omega-scan`（HTTP/HTTPS 卫生检查）和 `omega-deep`（有边界的架构分析）互补，而不重复它们的功能。

### Omega-track 的功能

- 接受 IP、IPv6 或域名作为目标，注册并可选择固定（长期授权）。
- 汇集公开、被动或经明确启用的信息（RDAP、DNS、证书透明度、Wayback 归档、BGP 通告)。
- 执行 NeoTrace 风格的增强 traceroute（核心产品中唯一的主动网络行为）。
- 通过本地 GeoIP 数据库丰富每个相关 IP（默认无需密钥的 DB-IP Lite，可选带密钥的 MaxMind GeoLite2）。
- 在用户提供密钥的情况下查询信誉来源（VirusTotal、HIBP），并在启用前始终展示披露信息（配额、发送的数据)。
- 将观测到的数据相互关联，形成一致的画像，每条数据都带有明确的置信等级。
- 在本地保存目标、执行记录、结果、错误与导出文件（SQLite，`./var/`)。
- 提供功能上严格等价的 Textual TUI 与 CLI。
- 生成 HTML（5 种主题，内嵌 Mermaid 关系图)、JSON、Markdown、CSV 报告，以及独立的 DOT 与 Mermaid 图。

### Omega-track 不做的事

| 功能 | 负责的工具 |
|---|---|
| 端口扫描、服务与横幅识别 | OMEGA-CHECK |
| HTTP/HTTPS 检查、请求头、TLS、网页卫生检查 | OMEGA-SCAN |
| 架构遍历与爬取、深入相关目标 | OMEGA-DEEP |
| 逐页远程爬取（链接、文件） | OMEGA-FOLD |
| 负载测试 | OMEGA-STRESS |
| 模糊测试与应用健壮性测试 | OMEGA-FUZZ |

即便超出 MVP 范围也应避免：子域名暴力枚举、端口扫描、网页爬取、侵入式个人数据采集、绕过防护机制的自动化、对需要身份验证的平台进行脆弱的抓取、人物/社交网络/pastebin 泄露信息搜索、对目标的周期性/重复性监控（见 `docs/PRODUCT_SCOPE.md` §7「刻意推迟」）。

### 授权使用警告

Omega-track 是一款面向合法用途的网络调查工具：审计自己的基础设施、事件响应、监控你被授权记录的范围。数据采集几乎完全是被动/公开的（RDAP、DNS、CT 日志——这些数据已由目标或其注册商公开披露），traceroute 除外（轻量主动行为，始终在所用配置文件中可见）。

**未经明确确认，任何观测都不会针对未固定的目标启动**（CLI 中的 `--authorize`，TUI 中的确认操作）。您独自负责确保您的使用符合适用法律以及所查询第三方来源的使用条款。

## 2. 安装

### 前置条件

- Python 3.10+
- 互联网连接，用于依赖项及被查询的被动数据源
- 已安装 `traceroute` 或 `tracepath`（NeoTrace 模块）——缺失时会优雅降级，工具其余部分照常运行

### 安装

```bash
[ -d omega-track ] && echo "ℹ️ 此处已解压，跳过该步骤。" || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`：

1. 若尚不存在则创建虚拟环境 `.venv`。
2. 安装依赖项（`pip install -e .`，`pyproject.toml` 始终是唯一真实来源）。
3. 使 `omega-track.sh` 与 `install.sh` 可执行。
4. 将别名 `track` 添加到 `~/.bashrc` 与 `~/.zshrc`（若已存在则不重复添加）。

### 依赖项

在 `pyproject.toml` 中声明（不再单独维护 `requirements.txt`）：
- `omega-lib`：套件共享库（`ConfidenceLevel`、主题、终端检测）
- `textual`：TUI 界面、主题、自动适配终端
- `dnspython`：正向与反向 DNS 解析
- `httpx`：RDAP/CT/归档/BGP/VirusTotal/HIBP 探测
- `maxminddb`：读取本地 GeoIP 数据库（DB-IP Lite、MaxMind GeoLite2）
- `jinja2`：HTML 导出模板引擎
- 开发依赖项（`pip install -e ".[dev]"`）：`pytest`、`pytest-asyncio`、`pytest-cov`、`pytest-httpserver`、`ruff`、`mypy`、`import-linter`

## 3. 使用方法

### 交互模式（TUI）

推荐用于日常使用——不带任何参数启动：

```bash
./omega-track.sh
```
如果您已创建别名，只需在终端中输入 `track`：
```bash
track
```

流程：启动画面（按任意键或点击即可关闭）→ 主菜单（目标 / 追踪器 / 结果 / 历史 / 仪表盘 / GeoIP / 密钥来源 / 设置 / 帮助）→ 输入或选择目标（若未固定则需明确确认）并选择采集模块 → 观测执行（不确定进度条与实时网络操作日志，可取消）→ 按标签页展示详细结果（身份/DNS/网络-ASN/NeoTrace/证书/归档/关系/诊断，导出）→ 从主菜单进入历史/仪表盘/设置。终端适配（颜色、尺寸、结构降级）自动完成。

#### 键盘快捷键

| 按键 | 操作 |
|---|---|
| `↑` / `↓` | 在屏幕元素间导航 |
| `Tab` / `Shift+Tab` | 在表单字段间导航 |
| `Esc` | 返回上一屏幕（主屏幕上为退出确认） |
| `t` | 切换到下一个主题（立即生效，无需确认） |
| `r` | 刷新终端检测 |
| `a` | 显示帮助 |
| `q` | 退出（需确认） |

### 脚本模式（CLI）

任何子命令都会触发 CLI 模式：

```bash
# 目标
./omega-track.sh target add example.org --alias "展示站点" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# 启动并跟踪一次观测
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# 历史
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# 导出 —— 6 种格式，HTML 可选 5 种主题
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# 需密钥的信誉来源（保存前始终展示披露信息）
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

任何子命令都可加 `--json` 获得严格机器可读的输出。

#### 退出码

| 代码 | 含义 |
|---:|---|
| `0` | 成功（观测完成，`COMPLETED`） |
| `1` | 校验错误（目标无效、导出格式未知、状态转换无效、缺少 API 密钥……） |
| `2` | 目标未获授权（既未固定，也未使用 `--authorize`） |
| `3` | 资源未找到或来源不可用（未知目标/运行记录、GeoIP 下载失败） |
| `4` | 部分完成的观测（`PARTIAL`）——并非失败，只是部分模块成功 |
| `5` | 意外的内部错误 |
| `130` | 被用户中断（`Ctrl+C`） |

### 支持的目标格式

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 域名
```

## 4. 采集模块

| 模块 | 采集模式 | 默认启用 | 需要密钥 |
|---|---|:---:|:---:|
| `dns` | 轻量主动（直接解析） | 是 | 否 |
| `reverse_dns` | 轻量主动（PTR） | 是 | 否 |
| `rdap` | 被动公开 | 是 | 否 |
| `neotrace` | 轻量主动（traceroute/tracepath） | 是 | 否 |
| `certificate_transparency` | 被动公开（`crt.sh`） | 否 | 否 |
| `archives` | 被动公开（Wayback Machine） | 否 | 否 |
| `bgp` | 被动公开（RIPEstat） | 否 | 否 |
| `virustotal` | 需用户密钥 | 否 | 是（免费） |
| `hibp` | 需用户密钥 | 否 | 是（自 2022 年起**付费**） |

前四个模块构成 MVP 核心（`dns`/`reverse_dns`/`rdap`/`neotrace`），在启动表单中默认勾选；后五个为可选项，须显式启用。未配置密钥的来源永远不会导致观测失败：对应模块只会变为 `SKIPPED`（未执行）。各来源详情、配额与许可协议：`docs/DATA_SOURCES.md`。

## 5. 架构

Omega-track 采用 **Clean Architecture** 分层结构（domain / application / infrastructure / interfaces / ports / core / app / plugins），与 `omega-` 套件模板保持一致（参见 `omega-check`/`omega-fold`），并在每次修改时由 `import-linter` 验证。

```text
src/omega_track/
├── domain/          纯业务逻辑（目标、TrackRun/ModuleRun、findings、关系、配置文件……）
├── application/     用例（commands/queries/阶段编排器/策略）
├── ports/           应用层期望的契约（采集器、仓储、导出器……）
├── infrastructure/  具体实现（dnspython/httpx/subprocess/maxminddb、SQLite、jinja2）
├── interfaces/      tui/（Textual）与 cli/（脚本化），严格功能对等
├── app/             组装层（DependencyContainer、bootstrap、生命周期）
├── core/            横切词汇（版本号、omega-lib 再导出）
└── plugins/         单一来源的可选模块（CT、归档、BGP、VirusTotal、HIBP）
```

设计规则：
- `domain/` 从不触碰网络或 I/O；`infrastructure/` 负责网络与 I/O，从不做判断。
- `interfaces/` 只负责展示，不包含业务逻辑——CLI 与 TUI 严格调用相同的用例。
- 1 个采集模块 = 1 个来源 = 1 个状态（`ModuleRun`）：绝不将两个来源聚合成一个含糊的状态。
- 单个字段缺失从不视为错误；只有来源完全不可用才会触发 `SKIPPED`/`FAILED`。

## 6. 数据来源

| 来源 | 提供方 | 密钥 | 模式 |
|---|---|:---:|---|
| 正向/反向 DNS | 系统解析器 | 否 | 轻量主动 |
| RDAP | IANA 引导 → RIR/注册商 | 否 | 被动公开 |
| 证书透明度 | `crt.sh`（Sectigo） | 否 | 被动公开 |
| 网页归档 | Wayback Machine（Internet Archive） | 否 | 被动公开 |
| BGP / 网络通告 | RIPEstat（RIPE NCC） | 否 | 被动公开 |
| GeoIP | DB-IP Lite（默认）或 MaxMind GeoLite2 | 否 / 是 | 离线（本地数据库） |
| NeoTrace | 本地 `traceroute`/`tracepath` | 否 | 轻量主动 |
| 信誉 | VirusTotal | 是（免费） | 需密钥 |
| 信誉 | Have I Been Pwned | 是（付费） | 需密钥 |

各来源的具体配额、许可协议与降级方案：`docs/DATA_SOURCES.md`。任何 API 密钥都绝不会出现在日志、导出文件或诊断界面中。

## 7. 置信度策略

每个采集到的字段都带有以下等级之一（通过 `omega-lib` 在整个套件间共享）：

| 等级 | 含义 |
|---|---|
| `VERIFIED`（已验证） | 直接观测到的协议事实，目标无法伪造（例如直接的 DNS 响应、本地 traceroute 测量结果）。 |
| `DECLARED`（自称） | 来源在其完全可控的字段中自行声明的值（例如注册商展示的 RDAP 数据）——貌似合理但可被随意伪造。 |
| `CORROBORATED`（已佐证） | 一个 `DECLARED` 值经独立线索确认（例如至少被两个不同的证书透明度日志观察到的域名）。 |
| `INFERRED`（推断） | 基于模式/启发式推导得出，没有明确声明（例如共用 ASN 用于暗示某种关联，永远不会自动升级）。 |
| `UNKNOWN`（未知） | 没有可用线索，或被目标主动隐藏。 |

一次观测的总体置信度评分只是阅读辅助，绝不是安全判定。

## 8. 采集级别、授权与脱敏

每个配置文件都明确说明其操作性质（`CollectionMode`）：

- **离线（Offline）**：目标校验、本地 GeoIP 查询、基于已存储数据的关联分析、导出——不涉及网络。
- **被动公开**：RDAP、公开 DNS、CT 日志、归档、BGP——仅向第三方传输被查询的目标本身，这是协议本身固有的属性。
- **轻量主动**：DNS 解析、反向 DNS、traceroute——配置的解析器与路径上的每个中间路由器都会看到该请求。
- **需用户密钥**：要求密钥或实施配额的提供方，只有在明确配置并展示披露信息（配额、发送的数据）后才会启用。

**授权门槛**：未经明确确认，任何观测都不会针对未固定的目标启动（CLI 中的 `--authorize`，TUI 中的复选框）。固定一个目标即为其未来的观测提供长期授权。

**导出脱敏**：每次导出都可选择一种策略（`none`/`contacts_only`/`sensitive_only`/`strict`），用于在导出结果中屏蔽敏感字段（尤其是 RDAP 联系方式）——本地存储始终保留完整采集到的数据。详情：`docs/PRIVACY.md`。

## 9. 终端兼容性

TUI（Textual）会自动检测终端能力（模拟器、尺寸），并相应地调整其结构性样式表（`complete`/`standard`/`reduced`/`mono`），无需手动指定参数。CLI 模式则始终为纯文本，不依赖终端。此策略在整个 `omega-` 套件中共享（`omega-lib`、`terminal/policies.py`）。

### 按检测到的模拟器划分的档位

| 模拟器 | 初始档位 |
|---|---|
| Ghostty、Alacritty、WezTerm、Kitty | `complete` |
| Konsole、GNOME Terminal、Terminator、Xfce4 Terminal | `standard` |
| xterm、urxvt、现代 SSH | `reduced` |
| Linux TTY、老旧 SSH | `mono` |
| 未识别的模拟器 | `reduced`（默认回退） |

### 按终端尺寸划分的档位

| 最小尺寸（列 × 行） | 档位上限 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| 更小 | `mono` |

最终采用的档位是**两者中更保守的一个**（模拟器与尺寸）。可通过 `r` 键实时刷新。

## 10. 导出

报告默认生成于 `var/exports/`（运行时路径锚定在项目目录下，可通过 `$OMEGA_TRACK_VAR_DIR` 覆盖），或生成于指定路径（CLI 中的 `--output`，TUI 中的对话框）。文件名带时间戳且唯一：`{时间戳}_{目标}_{短ID}.{扩展名}`。

| 格式 | 内容 |
|---|---|
| `json` | 完整的观测结构（`TrackRun` + findings + 关系），真实来源，严格可 JSON 序列化 |
| `markdown` | 简洁的人类可读报告，适合在终端之外阅读 |
| `html` | 独立的网页报告，可选 5 种主题（`--theme`），内嵌 Mermaid 关系图 |
| `csv` | 每个 finding 类别一张表 |
| `dot` | Graphviz 关系图，独立文件 |
| `mermaid` | Mermaid 关系图，独立文件 |

## 11. 历史、清理与重放

每次观测都会被持久化保存（SQLite，`var/db/omega-track.db`）：可浏览、可筛选的历史记录（目标/状态/标签/时间段）、汇总仪表盘（按状态分布、按模块可靠性、最近 findings 类型分布）、针对同一目标无需重新输入即可重放的观测（`track replay`），以及在任何删除操作前都会先展示预览的历史清理功能（先 `cleanup preview` 后 `cleanup run --yes`）。

## 12. 测试

```bash
source .venv/bin/activate
lint-imports        # 检查依赖规则（Dependency Rule）
pytest -q           # 478 个测试
ruff check .
mypy src
```

结构：`tests/unit/`（领域与应用层，无真实 I/O）、`tests/integration/`（真实 SQLite/文件、伪造 HTTP 服务器 `pytest-httpserver`、通过 Textual `Pilot` API 的无头 TUI 测试）。

## 13. 范围之外

- 完整的 WHOIS/DNS 历史、商业化被动 DNS
- 人物搜索、社交网络、pastebin 泄露信息
- 端口扫描、服务与横幅识别（`omega-check`）
- HTTP/HTTPS 检查、请求头、TLS（`omega-scan`）
- 架构爬取与遍历（`omega-deep`/`omega-fold`）
- 负载测试（`omega-stress`）、模糊测试（`omega-fuzz`）
- 交互式 TUI 地图（保留给导出的 HTML 报告）
- 连续、多探测点、多观测视角的 MTR
- 针对目标的批量/周期性/重复性监控模式——`TrackRun` 始终是一次明确的手动操作
- v1.0 之前的 SQLite 架构迁移引擎（增量式架构，与套件其余部分做法一致）

---

> Omega-track —— 观测、关联、评估、报告。
> 每条数据都带有明确置信度的数字身份，绝非伪装成确定性的猜测。
