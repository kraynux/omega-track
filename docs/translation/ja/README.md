<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT ライセンス（LICENSE ファイルを参照） -->
<div align="center">
  <img src="../../assets/omega-track.png" alt="Omega-Track" width="386">
</div>

# 🛰️ OMEGA-TRACK

**デジタルアイデンティティのプロファイリングとネットワーク経路の観測**

> **kraynux** が **Omega-server** のために開発 
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

公式ページ: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; プレビュー: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 インターフェースとエクスポートされるレポートは **17 言語** に対応しています — [インターフェースの言語](#インターフェースの言語) を参照してください。  
**言語：**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track** は TUI + CLI のツールで、IP、IPv6 アドレス、またはドメインから、できる限り完全なデジタルアイデンティティを組み立てます: このターゲットの背後で誰が応答しているのか、そこへどう到達するのか、そして各情報をどの程度の信頼度で確かなものとみなせるのか。`omega-` スイートのツールで、Clean Architecture で構成されています — 詳細は `docs/PRODUCT_SCOPE.md` と `docs/DATA_SOURCES.md` を参照してください。

## 1. ビジョンと範囲

Omega-track は 2 つの問いに答えます: 「このターゲットは誰か？」（RDAP/DNS/証明書/評判によるアイデンティティ）と「どうやってそこへ到達するか？」（NeoTrace のネットワーク経路、GeoIP、ASN）。`omega-check`（ネットワークの露出）、`omega-scan`（HTTP/HTTPS の衛生）、`omega-deep`（範囲を限定したアーキテクチャ分析）を補完し、それらと重複しません。

### Omega-track がすること

- IP、IPv6、またはドメイン名のターゲットを受け付け、保存し、必要に応じてピン留めします（永続的な許可）。
- 公開情報を集約します。パッシブなもの、またはプロファイルで明示的に有効にしたもの（RDAP、DNS、Certificate Transparency、Wayback アーカイブ、BGP アナウンス）。
- NeoTrace 型の拡張 traceroute を実行します（製品の中核で唯一のアクティブなネットワーク操作）。
- 関連する各 IP をローカルの GeoIP データベースで補強します（キー不要の DB-IP Lite、キー付きで任意の MaxMind GeoLite2）。
- ユーザーが提供するキーで評判ソース（VirusTotal、HIBP）に問い合わせます。有効化の前には必ずクォータと送信データを開示します。
- 観測したデータを関連付けて一貫したプロファイルにまとめ、各データに明示的な信頼度を付けます。
- ターゲット、実行、結果、エラー、エクスポートをローカルに保存します（SQLite、`./var/`）。
- 機能が厳密に同等な Textual の TUI と CLI を提供します。
- HTML レポート（5 テーマ、Mermaid の関係グラフを埋め込み）、JSON、Markdown、CSV、単独の DOT と Mermaid ファイルを生成します。

### Omega-track がしないこと

| 機能 | 担当ツール |
|---|---|
| ポートスキャン、サービスとバナーの識別 | OMEGA-CHECK |
| HTTP/HTTPS の確認、ヘッダー、TLS、Web の衛生 | OMEGA-SCAN |
| クロール、アーキテクチャの走査、関連ターゲットへの掘り下げ | OMEGA-DEEP |
| ページ単位のリモートクロール（リンク、ファイル） | OMEGA-FOLD |
| 負荷テスト | OMEGA-STRESS |
| ファジングとアプリケーションの堅牢性テスト | OMEGA-FUZZ |

MVP の範囲外も含めて避けること: サブドメインの総当たり、ポートスキャン、Web クロール、個人データの侵襲的な収集、保護の回避の自動化、認証を必要とするプラットフォームの脆いスクレイピング、人物/SNS/pastebin-リークの検索、ターゲットの定期的/継続的な監視（`docs/PRODUCT_SCOPE.md` §7「意図的に延期」を参照）。

### 許可された利用に関する注意

Omega-track は正当な利用のためのネットワーク調査ツールです: 自身のインフラの監査、インシデント対応、記録する権限のある範囲の監視。収集はほぼ完全にパッシブ/公開情報のままです（RDAP、DNS、CT ログ — ターゲットやそのレジストラがすでに公開しているデータ）。例外は traceroute（軽いアクティブ操作で、使用するプロファイルに常に表示されます）だけです。

**ピン留めされていないターゲットに対しては、明示的な確認なしに観測が始まることはありません**（CLI では `--authorize`、TUI では確認）。利用が適用法令と、問い合わせるサードパーティソースの利用規約に従っていることを確認する責任は、あなただけにあります。

## 2. インストール

### 前提条件

- Python 3.10+
- インターネット接続（依存関係と、問い合わせるパッシブソースのため）
- `traceroute` または `tracepath` がインストール済み（NeoTrace モジュール）— ない場合はきれいに機能を縮退し、ツールの他の部分は通常どおり動作します

### インストール

```bash
[ -d omega-track ] && echo "ℹ️ すでにここに展開済みのため、この手順を省略します。" || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. 仮想環境 `.venv` がまだなければ作成します。
2. 依存関係をインストールします（`pip install -e .`、`pyproject.toml` が唯一の正となる情報源です）。
3. `omega-track.sh` と `install.sh` を実行可能にします。
4. エイリアス `track` を `~/.bashrc` と `~/.zshrc` に追加します（すでにあれば重複させません）。

### 依存関係

`pyproject.toml` で宣言（別の `requirements.txt` はありません）:
- `omega-lib`: スイート共有のライブラリ（`ConfidenceLevel`、テーマ、ターミナル検出）
- `textual`: TUI インターフェース、テーマ、ターミナルへの自動適応
- `dnspython`: 正引きと逆引きの DNS 解決
- `httpx`: RDAP/CT/アーカイブ/BGP/VirusTotal/HIBP のプローブ
- `maxminddb`: ローカルの GeoIP データベース（DB-IP Lite、MaxMind GeoLite2）の読み取り
- `jinja2`: HTML エクスポートのテンプレート
- 開発用の依存関係（`pip install -e ".[dev]"`）: `pytest`、`pytest-asyncio`、`pytest-cov`、`pytest-httpserver`、`ruff`、`mypy`、`import-linter`

## 3. 使い方

### 対話モード（TUI）

日常の利用に推奨 — 引数なしで起動します:

```bash
./omega-track.sh
```
エイリアスを作成済みなら、ターミナルで `track` と入力するだけです:
```bash
track
```

流れ: スプラッシュ画面（キー入力かクリックで閉じる）→ メインメニュー（ターゲット / Tracker / 結果 / 履歴 / ダッシュボード / GeoIP / キー付きソース / 設定 / ヘルプ）→ ターゲットの入力または選択（ピン留めされていなければ明示的な確認）と収集モジュールの選択 → 観測（ゲージと操作の進行をリアルタイム表示、キャンセル可能）→ タブごとの詳細な結果（識別/DNS/ネットワーク / ASN/NeoTrace/証明書/アーカイブ/関係/診断、エクスポート）→ メインメニューから履歴/ダッシュボード/設定。ターミナルへの適応（色、サイズ、構造の縮退）は自動です。

#### キーボードショートカット

| キー | 操作 |
|---|---|
| `↑` / `↓` | 画面の要素間を移動 |
| `Tab` / `Shift+Tab` | フォームの欄の間を移動 |
| `Esc` | 前の画面に戻る（ホーム画面では終了の確認） |
| `t` | 次のテーマ（確認なしですぐに適用） |
| `r` | ターミナル検出を更新 |
| `a` | ヘルプを表示 |
| `q` | 終了（確認あり） |

### インターフェースの言語

インターフェースは 17 言語で利用できます: フランス語、英語、スペイン語、ポルトガル語（ブラジル）、イタリア語、ドイツ語、オランダ語、ポーランド語、ロシア語、簡体字中国語、ベトナム語、タイ語、インドネシア語、日本語、韓国語、ヒンディー語、アラビア語。設定（「Langue / Language」）で選択し、インターフェースの再起動後に反映されます。変数 `OMEGA_TRACK_LANG`（例: `OMEGA_TRACK_LANG=ja ./omega-track.sh`）で 1 セッションだけ言語を指定できます。omega-suite から起動した場合、omega-track はスイートの言語を使います。Linux のテキストコンソール（TTY）では、ラテン文字以外の言語はそのセッションの間、英語で表示されます。コマンドラインはフランス語のままです。

### スクリプトモード（CLI）

どのサブコマンドでも CLI モードになります:

```bash
# ターゲット
./omega-track.sh target add example.org --alias "紹介サイト" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# 観測を開始して追跡する
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# 履歴
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# エクスポート — 6 形式、HTML は 5 テーマ
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# キー付きの評判ソース（保存の前に開示内容を表示）
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <api_キー>

# 設定と消去
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# ローカル診断（バージョン、能力、パス、GeoIP の状態）
./omega-track.sh diagnostics
```

すべてのサブコマンドは、厳密に機械可読な出力のために `--json` を受け付けます。

#### 終了コード

| コード | 意味 |
|---:|---|
| `0` | 成功（観測完了、`COMPLETED`） |
| `1` | 検証エラー（無効なターゲット、不明なエクスポート形式、無効な状態遷移、API キーなし...） |
| `2` | 許可されていないターゲット（ピン留めも `--authorize` もない） |
| `3` | リソースが見つからない、またはソースが利用不可（不明なターゲット/実行、GeoIP のダウンロード失敗） |
| `4` | 部分的な観測（`PARTIAL`）— 失敗ではなく、一部のモジュールだけが成功 |
| `5` | 予期しない内部エラー |
| `130` | ユーザーによる中断（`Ctrl+C`） |

### 受け付けるターゲット形式

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 ドメイン
```

## 4. 収集モジュール

| モジュール | 収集モード | 既定で有効 | キーが必要 |
|---|---|:---:|:---:|
| `dns` | 軽いアクティブ（正引き） | はい | いいえ |
| `reverse_dns` | 軽いアクティブ（PTR） | はい | いいえ |
| `rdap` | 公開パッシブ | はい | いいえ |
| `neotrace` | 軽いアクティブ（traceroute/tracepath） | はい | いいえ |
| `certificate_transparency` | 公開パッシブ（`crt.sh`） | いいえ | いいえ |
| `archives` | 公開パッシブ（Wayback Machine） | いいえ | いいえ |
| `bgp` | 公開パッシブ（RIPEstat） | いいえ | いいえ |
| `virustotal` | ユーザーキー使用 | いいえ | はい（無料） |
| `hibp` | ユーザーキー使用 | いいえ | はい（2022 年から**有料**） |

最初の 4 つのモジュールは MVP の基盤（`dns`/`reverse_dns`/`rdap`/`neotrace`）で、起動フォームで既定でチェックされています。続く 5 つは任意で、明示的に有効にする必要があります。キーが設定されていないソースが観測を失敗させることはありません: 該当モジュールは単に `SKIPPED`（「未実行」）になります。ソースごとの詳細、クォータ、ライセンス: `docs/DATA_SOURCES.md`。

## 5. アーキテクチャ

Omega-track は **Clean Architecture**（domain / application / infrastructure / interfaces / ports / core / app / plugins）で構成され、`omega-` スイートのテンプレート（`omega-check`/`omega-fold` を参照）に沿っており、変更のたびに `import-linter` で検証されます。

```text
src/omega_track/
├── domain/          純粋な業務ロジック（ターゲット、TrackRun/ModuleRun、findings、関係、プロファイル...）
├── application/     ユースケース（commands/queries/フェーズのオーケストレーター/ポリシー）
├── ports/           アプリケーションが期待する契約（コレクター、リポジトリ、エクスポーター...）
├── infrastructure/  具体的な実装（dnspython/httpx/subprocess/maxminddb、SQLite、jinja2）
├── interfaces/      tui/（Textual）と cli/（スクリプト可能）、機能は厳密に同等
├── app/             組み立て（DependencyContainer、ブートストラップ、ライフサイクル）
├── core/            横断的な語彙（バージョン、omega-lib の再エクスポート）
└── plugins/         単一ソースの任意モジュール（CT、アーカイブ、BGP、VirusTotal、HIBP）
```

設計ルール:
- `domain/` はネットワークも I/O も決して行いません。`infrastructure/` はネットワークと I/O を行いますが、判断は決してしません。
- `interfaces/` は表示するだけで業務ロジックを持ちません — CLI と TUI は厳密に同じユースケースを呼び出します。
- 1 収集モジュール = 1 ソース = 1 状態（`ModuleRun`）: 2 つのソースを 1 つのあいまいな状態にまとめることは決してありません。
- 単独のフィールドが欠けていてもエラーにはなりません。ソース全体が利用できない場合にのみ `SKIPPED`/`FAILED` になります。

## 6. データソース

| ソース | 提供元 | キー | モード |
|---|---|:---:|---|
| DNS 正引き/逆引き | システムのリゾルバー | いいえ | 軽いアクティブ |
| RDAP | IANA ブートストラップ → RIR/レジストラ | いいえ | 公開パッシブ |
| Certificate Transparency | `crt.sh`（Sectigo） | いいえ | 公開パッシブ |
| Web アーカイブ | Wayback Machine（Internet Archive） | いいえ | 公開パッシブ |
| BGP / ネットワークアナウンス | RIPEstat（RIPE NCC） | いいえ | 公開パッシブ |
| GeoIP | DB-IP Lite（既定）または MaxMind GeoLite2 | いいえ / はい | オフライン（ローカルデータベース） |
| NeoTrace | ローカルの `traceroute`/`tracepath` | いいえ | 軽いアクティブ |
| 評判 | VirusTotal | はい（無料） | キー使用 |
| 評判 | Have I Been Pwned | はい（有料） | キー使用 |

各ソースの正確なクォータ、ライセンス、代替手段: `docs/DATA_SOURCES.md`。API キーがログ、エクスポート、診断画面に現れることは決してありません。

## 7. 信頼度ポリシー

収集された各フィールドには次のいずれかのレベルが付きます（`omega-lib` を通じてスイート全体で共有）:

| レベル | 意味 |
|---|---|
| `VERIFIED` | 直接観測したプロトコル上の事実で、ターゲットが偽装できないもの（例: 直接の DNS 応答、ローカルの traceroute 測定）。 |
| `DECLARED` | ソースが完全に管理するフィールドで自己申告した値（例: レジストラが表示する RDAP データ）— もっともらしいが、自由に偽装できる。 |
| `CORROBORATED` | 独立した手がかりで裏付けられた `DECLARED` の値（例: 異なる 2 つ以上の Certificate Transparency ログで観測されたドメイン）。 |
| `INFERRED` | パターン/ヒューリスティックから推定し、明示的な申告がないもの（例: 共通の ASN から関係を示唆する。自動で格上げされることはない）。 |
| `UNKNOWN` | 使える手がかりがない、またはターゲットが積極的に隠している。 |

観測全体の信頼スコアは読み取りの補助であり、セキュリティ上の判定ではありません。

## 8. 収集レベル、許可、秘匿化

各プロファイルは、その操作の性質を明示します（`CollectionMode`）:

- **オフライン**: ターゲットの検証、ローカル GeoIP の読み取り、保存済みデータでの相関付け、エクスポート — ネットワークなし。
- **公開パッシブ**: RDAP、公開 DNS、CT ログ、アーカイブ、BGP — 第三者に送られるのは問い合わせたターゲットだけで、これはプロトコル固有の性質です。
- **軽いアクティブ**: DNS 解決、逆引き DNS、traceroute — マシンに設定されたリゾルバーと経路上の各中継ルーターがリクエストを目にします。
- **ユーザーキー使用**: キーを要求する、またはクォータを課す提供元で、明示的な設定と開示（クォータ、送信データ）の表示後にのみ有効になります。

**許可の保護**: ピン留めされていないターゲットに対しては、明示的な確認なしに観測が始まることはありません（CLI では `--authorize`、TUI ではチェックボックス）。ターゲットをピン留めすると、今後の観測について永続的に許可されます。

**エクスポートの秘匿化**: 各エクスポートはポリシー（`none`/`contacts_only`/`sensitive_only`/`strict`）を受け付け、エクスポート結果の機微なフィールド（特に RDAP の連絡先）を隠します — 一方、ローカルの保存領域は収集したデータを常に完全に保持します。詳細: `docs/PRIVACY.md`。

## 9. ターミナルの互換性

TUI（Textual）はターミナルの能力（エミュレーター、サイズ）を自動で検出し、それに応じて構造的なスタイルシート（`complete`/`standard`/`reduced`/`mono`）を調整します。手動のフラグは不要です。CLI モードは常にプレーンテキストで、ターミナルに依存しません。`omega-` スイート全体で共有するポリシーです（`omega-lib`、`terminal/policies.py`）。

### 検出したエミュレーターによるプロファイル

| エミュレーター | 初期プロファイル |
|---|---|
| Ghostty、Alacritty、WezTerm、Kitty | `complete` |
| Konsole、GNOME Terminal、Terminator、Xfce4 Terminal | `standard` |
| xterm、urxvt、最新の SSH | `reduced` |
| Linux の TTY、古い SSH | `mono` |
| 認識できないエミュレーター | `reduced`（既定の代替） |

### ターミナルのサイズによるプロファイル

| 最小サイズ（列 × 行） | プロファイルの上限 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| それ未満 | `mono` |

最終的に採用されるプロファイルは **2 つのうちより厳しい方**（エミュレーターとサイズ）です。`r` キーでリアルタイムに更新できます。

## 10. エクスポート

Markdown と HTML のレポートは設定で選んだ言語（「エクスポートの言語」、既定ではインターフェースと同じ）で書かれます。JSON、CSV、DOT、Mermaid はデータのままで、翻訳されません。レポートは既定で `var/exports/` に生成されます（プロジェクトフォルダーを基準とする実行時パス。`$OMEGA_TRACK_VAR_DIR` で上書き可能）。または指定したパス（CLI では `--output`、TUI ではダイアログボックス）に生成されます。タイムスタンプ付きの一意のファイル名: `{タイムスタンプ}_{ターゲット}_{短縮id}.{拡張子}`。

| 形式 | 内容 |
|---|---|
| `json` | 観測の完全な構造（`TrackRun` + findings + 関係）、正となる情報源、厳密に JSON シリアライズ可能 |
| `markdown` | 人が読むコンパクトなレポート、ターミナル外でも読める |
| `html` | 単独の Web レポート、5 テーマから選択（`--theme`）、Mermaid の関係グラフをインラインで埋め込み |
| `csv` | finding のカテゴリーごとに 1 つの表 |
| `dot` | Graphviz の関係グラフ、単独ファイル |
| `mermaid` | Mermaid の関係グラフ、単独ファイル |

## 11. 履歴、消去、再実行

すべての観測は保存されます（SQLite、`var/db/omega-track.db`）: 閲覧と絞り込みができる履歴（ターゲット/状態/タグ/期間）、集計ダッシュボード（状態別の内訳、モジュールごとの信頼性、最新 findings の種類）、同じターゲットでの観測の再実行（再入力不要、`track replay`）、削除の前に必ずプレビューする古い履歴の消去（`cleanup run --yes` の前に `cleanup preview`）。

## 12. テスト

```bash
source .venv/bin/activate
lint-imports        # Dependency Rule を検証
pytest -q           # 485 テスト
ruff check .
mypy src
```

構成: `tests/unit/`（ドメインとアプリケーション、実際の I/O なし）、`tests/integration/`（実際の SQLite/ファイル、偽の HTTP サーバー `pytest-httpserver`、Textual の `Pilot` API によるヘッドレス TUI）。

## 13. 範囲外

- 完全な WHOIS/DNS 履歴、商用の passive DNS
- 人物、SNS、pastebin/リークの検索
- ポートスキャン、サービスとバナーの識別（`omega-check`）
- HTTP/HTTPS の確認、ヘッダー、TLS（`omega-scan`）
- クロールとアーキテクチャの走査（`omega-deep`/`omega-fold`）
- 負荷テスト（`omega-stress`）、ファジング（`omega-fuzz`）
- 対話的な TUI マップ（エクスポートした HTML レポート専用）
- 継続的、複数プローブ、複数観測地点の MTR
- ターゲットのバッチ/定期実行/継続的な監視 — `TrackRun` は常に明示的な手動操作のままです
- SQLite スキーマ移行エンジン（追加型のスキーマ、スイートの他の部分と同じ方針）

---

> Omega-track — 観測し、関連付け、評価し、報告する。
> 各データに明示的な信頼度を持つデジタルアイデンティティであり、偽装された確実性では決してない。
