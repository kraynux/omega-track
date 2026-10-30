<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT 라이선스 (LICENSE 파일 참조) -->
<div align="center">
  <img src="../../assets/omega-track.png" alt="Omega-Track" width="386">
</div>

# 🛰️ OMEGA-TRACK

**디지털 신원 프로파일링과 네트워크 경로 관측**

> **kraynux**가 **Omega-server**를 위해 개발 
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

공식 페이지: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; 미리 보기: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 인터페이스와 내보낸 보고서는 **17개 언어**로 제공됩니다 — [인터페이스 언어](#인터페이스-언어)를 참조하세요.  
**언어:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track**은 IP, IPv6 주소 또는 도메인에서 출발해 가능한 한 완전한 디지털 신원을 구성하는 TUI + CLI 도구입니다: 이 대상 뒤에서 누가 응답하는지, 그곳까지 어떻게 도달하는지, 그리고 각 정보를 어느 정도의 신뢰도로 확실하다고 볼 수 있는지. `omega-` 스위트의 도구이며, Clean Architecture로 구성되어 있습니다 — 자세한 내용은 `docs/PRODUCT_SCOPE.md`와 `docs/DATA_SOURCES.md`를 참조하세요.

## 1. 비전과 범위

Omega-track은 두 가지 질문에 답합니다: "이 대상은 누구인가?"(RDAP/DNS/인증서/평판 기반 신원)와 "어떻게 그곳에 도달하는가?"(NeoTrace 네트워크 경로, GeoIP, ASN). `omega-check`(네트워크 노출), `omega-scan`(HTTP/HTTPS 위생), `omega-deep`(범위가 제한된 아키텍처 분석)을 보완하며, 이들과 중복되지 않습니다.

### Omega-track이 하는 일

- IP, IPv6 또는 도메인 이름 형태의 대상을 받아 저장하고, 필요하면 고정합니다(지속적인 권한).
- 공개 정보를 모읍니다. 수동적이거나 프로필에서 명시적으로 활성화한 정보입니다(RDAP, DNS, Certificate Transparency, Wayback 아카이브, BGP 공지).
- NeoTrace 방식의 확장 traceroute를 실행합니다(제품 핵심에서 유일한 능동적 네트워크 동작).
- 관련된 각 IP를 로컬 GeoIP 데이터베이스로 보강합니다(키가 필요 없는 DB-IP Lite, 키가 있으면 선택적으로 MaxMind GeoLite2).
- 사용자가 제공한 키로 평판 소스(VirusTotal, HIBP)를 조회하며, 활성화 전에는 항상 할당량과 전송 데이터를 공개합니다.
- 관측한 데이터를 서로 연결해 일관된 프로필을 만들고, 각 데이터에 명시적인 신뢰 수준을 부여합니다.
- 대상, 실행, 결과, 오류, 내보내기를 로컬에 보관합니다(SQLite, `./var/`).
- 기능이 엄격히 동등한 Textual TUI와 CLI를 제공합니다.
- HTML 보고서(테마 5개, Mermaid 관계 그래프 내장), JSON, Markdown, CSV, 독립 실행형 DOT 및 Mermaid 파일을 생성합니다.

### Omega-track이 하지 않는 일

| 기능 | 담당 도구 |
|---|---|
| 포트 스캔, 서비스와 배너 식별 | OMEGA-CHECK |
| HTTP/HTTPS 점검, 헤더, TLS, 웹 위생 | OMEGA-SCAN |
| 크롤링, 아키텍처 순회, 연결된 대상으로의 탐색 | OMEGA-DEEP |
| 페이지 단위 원격 크롤링(링크, 파일) | OMEGA-FOLD |
| 부하 테스트 | OMEGA-STRESS |
| 퍼징과 애플리케이션 견고성 테스트 | OMEGA-FUZZ |

MVP 밖에서도 피해야 할 것: 서브도메인 무차별 대입, 포트 스캔, 웹 크롤링, 개인 정보의 침해적 수집, 보호 장치 우회 자동화, 인증이 필요한 플랫폼의 불안정한 스크래핑, 사람/소셜 네트워크/pastebin-유출 검색, 대상의 주기적/반복적 감시(`docs/PRODUCT_SCOPE.md` §7 "의도적으로 연기" 참조).

### 허가된 사용에 관한 안내

Omega-track은 정당한 용도를 위한 네트워크 조사 도구입니다: 자신의 인프라 감사, 사고 대응, 기록할 권한이 있는 범위의 감시. 수집은 거의 전부 수동적/공개적입니다(RDAP, DNS, CT 로그 — 대상이나 그 등록 기관이 이미 공개한 데이터). 예외는 traceroute(가벼운 능동 동작이며, 사용하는 프로필에 항상 표시됨)뿐입니다.

**고정되지 않은 대상에 대해서는 명시적인 확인 없이 관측이 시작되지 않습니다**(CLI에서는 `--authorize`, TUI에서는 확인). 사용 방식이 관련 법률과 조회하는 제3자 소스의 이용 약관을 준수하는지 확인할 책임은 전적으로 사용자에게 있습니다.

## 2. 설치

### 사전 요구 사항

- Python 3.10+
- 인터넷 연결(의존성과 조회하는 수동 소스용)
- `traceroute` 또는 `tracepath` 설치(NeoTrace 모듈) — 없으면 깔끔하게 기능이 축소되며, 도구의 나머지 부분은 정상 동작합니다

### 설치

```bash
[ -d omega-track ] && echo "ℹ️ 이미 여기에 압축이 풀려 있어 이 단계를 건너뜁니다." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. 가상 환경 `.venv`가 아직 없으면 만듭니다.
2. 의존성을 설치합니다(`pip install -e .`, `pyproject.toml`이 유일한 기준 정보입니다).
3. `omega-track.sh`와 `install.sh`를 실행 가능하게 합니다.
4. 별칭 `track`을 `~/.bashrc`와 `~/.zshrc`에 추가합니다(이미 있으면 중복하지 않음).

### 의존성

`pyproject.toml`에 선언(별도의 `requirements.txt` 없음):
- `omega-lib`: 스위트 공유 라이브러리(`ConfidenceLevel`, 테마, 터미널 감지)
- `textual`: TUI 인터페이스, 테마, 터미널 자동 적응
- `dnspython`: 정방향 및 역방향 DNS 조회
- `httpx`: RDAP/CT/아카이브/BGP/VirusTotal/HIBP 프로브
- `maxminddb`: 로컬 GeoIP 데이터베이스(DB-IP Lite, MaxMind GeoLite2) 읽기
- `jinja2`: HTML 내보내기용 템플릿
- 개발 의존성(`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. 사용법

### 대화형 모드(TUI)

일상적인 사용에 권장 — 인수 없이 실행합니다:

```bash
./omega-track.sh
```
별칭을 만들었다면 터미널에서 `track`만 입력하면 됩니다:
```bash
track
```

흐름: 시작 화면(키를 누르거나 클릭하면 닫힘) → 메인 메뉴(대상 / Tracker / 결과 / 기록 / 대시보드 / GeoIP / 키 소스 / 설정 / 도움말) → 대상 입력 또는 선택(고정되지 않았다면 명시적 확인)과 수집 모듈 선택 → 관측(게이지와 작업 진행을 실시간 표시, 취소 가능) → 탭별 상세 결과(신원/DNS/네트워크 / ASN/NeoTrace/인증서/아카이브/관계/진단, 내보내기) → 메인 메뉴에서 기록/대시보드/설정. 터미널 적응(색상, 크기, 구조 단순화)은 자동입니다.

#### 키보드 단축키

| 키 | 동작 |
|---|---|
| `↑` / `↓` | 화면의 항목 사이 이동 |
| `Tab` / `Shift+Tab` | 양식 입력란 사이 이동 |
| `Esc` | 이전 화면으로 돌아가기(홈 화면에서는 종료 확인) |
| `t` | 다음 테마(확인 없이 즉시 적용) |
| `r` | 터미널 감지 새로 고침 |
| `a` | 도움말 표시 |
| `q` | 종료(확인 있음) |

### 인터페이스 언어

인터페이스는 17개 언어로 제공됩니다: 프랑스어, 영어, 스페인어, 포르투갈어(브라질), 이탈리아어, 독일어, 네덜란드어, 폴란드어, 러시아어, 중국어 간체, 베트남어, 태국어, 인도네시아어, 일본어, 한국어, 힌디어, 아랍어. 설정("Langue / Language")에서 선택하며 인터페이스를 다시 시작한 뒤 적용됩니다. 변수 `OMEGA_TRACK_LANG`(예: `OMEGA_TRACK_LANG=ko ./omega-track.sh`)으로 한 세션 동안 언어를 강제할 수 있습니다. omega-suite에서 실행하면 omega-track은 스위트의 언어를 따릅니다. Linux 텍스트 콘솔(TTY)에서는 라틴 문자가 아닌 언어가 그 세션 동안 영어로 표시됩니다. 명령줄은 프랑스어로 유지됩니다.

### 스크립트 모드(CLI)

어떤 하위 명령이든 CLI 모드를 실행합니다:

```bash
# 대상
./omega-track.sh target add example.org --alias "홍보 사이트" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# 관측 시작 및 추적
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# 기록
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# 내보내기 — 6가지 형식, HTML은 테마 5개
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# 키가 필요한 평판 소스(저장 전에 공개 내용 표시)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <api_키>

# 설정과 정리
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# 로컬 진단(버전, 기능, 경로, GeoIP 상태)
./omega-track.sh diagnostics
```

모든 하위 명령은 엄격히 기계가 읽을 수 있는 출력을 위해 `--json`을 받습니다.

#### 종료 코드

| 코드 | 의미 |
|---:|---|
| `0` | 성공(관측 완료, `COMPLETED`) |
| `1` | 검증 오류(잘못된 대상, 알 수 없는 내보내기 형식, 잘못된 상태 전환, API 키 없음...) |
| `2` | 허가되지 않은 대상(고정도 `--authorize`도 없음) |
| `3` | 리소스를 찾을 수 없거나 소스를 사용할 수 없음(알 수 없는 대상/실행, GeoIP 다운로드 실패) |
| `4` | 부분 관측(`PARTIAL`) — 실패가 아니며, 일부 모듈만 성공 |
| `5` | 예기치 않은 내부 오류 |
| `130` | 사용자에 의해 중단됨(`Ctrl+C`) |

### 허용되는 대상 형식

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 도메인
```

## 4. 수집 모듈

| 모듈 | 수집 방식 | 기본 활성 | 키 필요 |
|---|---|:---:|:---:|
| `dns` | 가벼운 능동(정방향 조회) | 예 | 아니요 |
| `reverse_dns` | 가벼운 능동(PTR) | 예 | 아니요 |
| `rdap` | 공개 수동 | 예 | 아니요 |
| `neotrace` | 가벼운 능동(traceroute/tracepath) | 예 | 아니요 |
| `certificate_transparency` | 공개 수동(`crt.sh`) | 아니요 | 아니요 |
| `archives` | 공개 수동(Wayback Machine) | 아니요 | 아니요 |
| `bgp` | 공개 수동(RIPEstat) | 아니요 | 아니요 |
| `virustotal` | 사용자 키 사용 | 아니요 | 예(무료) |
| `hibp` | 사용자 키 사용 | 아니요 | 예(2022년부터 **유료**) |

처음 네 모듈은 MVP 기반(`dns`/`reverse_dns`/`rdap`/`neotrace`)이며 실행 양식에서 기본으로 체크되어 있습니다. 다음 다섯 모듈은 선택 사항이며 명시적으로 활성화해야 합니다. 키가 설정되지 않은 소스는 관측을 실패시키지 않습니다: 해당 모듈은 단순히 `SKIPPED`("실행 안 됨")가 됩니다. 소스별 상세, 할당량, 라이선스: `docs/DATA_SOURCES.md`.

## 5. 아키텍처

Omega-track은 **Clean Architecture**(domain / application / infrastructure / interfaces / ports / core / app / plugins)로 구성되며, `omega-` 스위트의 템플릿(`omega-check`/`omega-fold` 참조)을 따르고 변경할 때마다 `import-linter`로 검증됩니다.

```text
src/omega_track/
├── domain/          순수 업무 로직(대상, TrackRun/ModuleRun, findings, 관계, 프로필...)
├── application/     사용 사례(commands/queries/단계 오케스트레이터/정책)
├── ports/           애플리케이션이 기대하는 계약(수집기, 저장소, 내보내기...)
├── infrastructure/  구체 구현(dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/(Textual)와 cli/(스크립트 가능), 기능 엄격히 동등
├── app/             조립(DependencyContainer, 부트스트랩, 수명 주기)
├── core/            공통 어휘(버전, omega-lib 재내보내기)
└── plugins/         단일 소스 선택 모듈(CT, 아카이브, BGP, VirusTotal, HIBP)
```

설계 규칙:
- `domain/`은 네트워크나 I/O를 절대 하지 않습니다. `infrastructure/`는 네트워크와 I/O를 하지만 절대 판단하지 않습니다.
- `interfaces/`는 표시만 하며 업무 로직을 담지 않습니다 — CLI와 TUI는 엄격히 같은 사용 사례를 호출합니다.
- 수집 모듈 1개 = 소스 1개 = 상태 1개(`ModuleRun`): 두 소스를 하나의 모호한 상태로 묶는 일은 없습니다.
- 개별 필드가 없는 것은 오류가 아닙니다. 소스 전체를 사용할 수 없을 때만 `SKIPPED`/`FAILED`가 됩니다.

## 6. 데이터 소스

| 소스 | 제공자 | 키 | 방식 |
|---|---|:---:|---|
| 정방향/역방향 DNS | 시스템 리졸버 | 아니요 | 가벼운 능동 |
| RDAP | IANA 부트스트랩 → RIR/등록 기관 | 아니요 | 공개 수동 |
| Certificate Transparency | `crt.sh`(Sectigo) | 아니요 | 공개 수동 |
| 웹 아카이브 | Wayback Machine(Internet Archive) | 아니요 | 공개 수동 |
| BGP / 네트워크 공지 | RIPEstat(RIPE NCC) | 아니요 | 공개 수동 |
| GeoIP | DB-IP Lite(기본) 또는 MaxMind GeoLite2 | 아니요 / 예 | 오프라인(로컬 데이터베이스) |
| NeoTrace | 로컬 `traceroute`/`tracepath` | 아니요 | 가벼운 능동 |
| 평판 | VirusTotal | 예(무료) | 키 사용 |
| 평판 | Have I Been Pwned | 예(유료) | 키 사용 |

소스별 정확한 할당량, 라이선스, 대체 수단: `docs/DATA_SOURCES.md`. API 키는 로그, 내보내기, 진단 화면에 절대 나타나지 않습니다.

## 7. 신뢰 정책

수집된 각 필드에는 다음 수준 중 하나가 붙습니다(`omega-lib`를 통해 스위트 전체가 공유):

| 수준 | 의미 |
|---|---|
| `VERIFIED` | 직접 관측한 프로토콜상의 사실로, 대상이 위조할 수 없음(예: 직접 받은 DNS 응답, 로컬 traceroute 측정). |
| `DECLARED` | 소스가 완전히 통제하는 필드에 스스로 밝힌 값(예: 등록 기관이 표시한 RDAP 데이터) — 그럴듯하지만 마음대로 위조할 수 있음. |
| `CORROBORATED` | 독립적인 단서로 확인된 `DECLARED` 값(예: 서로 다른 Certificate Transparency 로그 두 곳 이상에서 관측된 도메인). |
| `INFERRED` | 패턴/휴리스틱으로 추론했으며 명시적 신고는 없음(예: 공통 ASN으로 관계를 암시, 자동으로 격상되지 않음). |
| `UNKNOWN` | 활용할 단서가 없거나, 대상이 적극적으로 숨김. |

관측 전체의 신뢰 점수는 읽기를 돕는 도구일 뿐, 보안 판정이 아닙니다.

## 8. 수집 수준, 권한, 가림 처리

각 프로필은 동작의 성격을 명시합니다(`CollectionMode`):

- **오프라인**: 대상 검증, 로컬 GeoIP 읽기, 이미 저장된 데이터의 상관 분석, 내보내기 — 네트워크 없음.
- **공개 수동**: RDAP, 공개 DNS, CT 로그, 아카이브, BGP — 제3자에게는 조회한 대상만 전달되며, 이는 프로토콜 고유의 특성입니다.
- **가벼운 능동**: DNS 조회, 역방향 DNS, traceroute — 머신에 설정된 리졸버와 경로상의 모든 중간 라우터가 요청을 봅니다.
- **사용자 키 사용**: 키를 요구하거나 할당량을 적용하는 제공자로, 명시적 설정과 공개 내용(할당량, 전송 데이터) 표시 후에만 활성화됩니다.

**권한 보호**: 고정되지 않은 대상에 대해서는 명시적인 확인 없이 관측이 시작되지 않습니다(CLI에서는 `--authorize`, TUI에서는 체크박스). 대상을 고정하면 이후의 관측에 대해 지속적으로 허가됩니다.

**내보내기 가림 처리**: 각 내보내기는 정책(`none`/`contacts_only`/`sensitive_only`/`strict`)을 받아 내보낸 결과에서 민감한 필드(특히 RDAP 연락처)를 가립니다 — 반면 로컬 저장소는 수집한 전체 데이터를 항상 보존합니다. 상세: `docs/PRIVACY.md`.

## 9. 터미널 호환성

TUI(Textual)는 터미널의 기능(에뮬레이터, 크기)을 자동으로 감지하고 그에 맞게 구조 스타일시트(`complete`/`standard`/`reduced`/`mono`)를 조정하며, 수동 플래그가 필요 없습니다. CLI 모드는 항상 일반 텍스트이며 터미널과 무관합니다. `omega-` 스위트 전체가 공유하는 정책입니다(`omega-lib`, `terminal/policies.py`).

### 감지된 에뮬레이터에 따른 프로필

| 에뮬레이터 | 초기 프로필 |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, 최신 SSH | `reduced` |
| Linux TTY, 구형 SSH | `mono` |
| 인식되지 않은 에뮬레이터 | `reduced`(기본 대체값) |

### 터미널 크기에 따른 프로필

| 최소 크기(열 × 행) | 프로필 상한 |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| 그 미만 | `mono` |

최종적으로 적용되는 프로필은 **둘 중 더 엄격한 쪽**(에뮬레이터와 크기)입니다. `r` 키로 실시간 새로 고칠 수 있습니다.

## 10. 내보내기

Markdown과 HTML 보고서는 설정에서 선택한 언어("내보내기 언어", 기본값은 인터페이스 언어)로 작성됩니다. JSON, CSV, DOT, Mermaid는 데이터로 남아 번역되지 않습니다. 보고서는 기본적으로 `var/exports/`에 생성되며(프로젝트 폴더를 기준으로 한 실행 경로, `$OMEGA_TRACK_VAR_DIR`로 재정의 가능), 지정한 경로(CLI의 `--output`, TUI의 대화 상자)에 생성할 수도 있습니다. 타임스탬프가 붙은 고유한 파일 이름: `{타임스탬프}_{대상}_{짧은_id}.{확장자}`.

| 형식 | 내용 |
|---|---|
| `json` | 관측의 전체 구조(`TrackRun` + findings + 관계), 기준 정보, 엄격히 JSON 직렬화 가능 |
| `markdown` | 사람이 읽는 간결한 보고서, 터미널 밖에서도 읽기 쉬움 |
| `html` | 독립 실행형 웹 보고서, 테마 5개 중 선택(`--theme`), Mermaid 관계 그래프 인라인 내장 |
| `csv` | finding 범주마다 표 하나 |
| `dot` | Graphviz 관계 그래프, 독립 파일 |
| `mermaid` | Mermaid 관계 그래프, 독립 파일 |

## 11. 기록, 정리, 재실행

모든 관측은 저장됩니다(SQLite, `var/db/omega-track.db`): 보고 필터링할 수 있는 기록(대상/상태/태그/기간), 요약 대시보드(상태별 분포, 모듈별 신뢰성, 최근 findings 유형), 다시 입력하지 않고 같은 대상에서 관측 재실행(`track replay`), 삭제 전에 항상 미리 보기를 거치는 오래된 기록 정리(`cleanup run --yes` 전에 `cleanup preview`).

## 12. 테스트

```bash
source .venv/bin/activate
lint-imports        # Dependency Rule 검증
pytest -q           # 테스트 485개
ruff check .
mypy src
```

구조: `tests/unit/`(도메인과 애플리케이션, 실제 I/O 없음), `tests/integration/`(실제 SQLite/파일, 가짜 HTTP 서버 `pytest-httpserver`, Textual의 `Pilot` API를 통한 헤드리스 TUI).

## 13. 범위 밖

- 전체 WHOIS/DNS 기록, 상용 passive DNS
- 사람, 소셜 네트워크, pastebin/유출 검색
- 포트 스캔, 서비스와 배너 식별(`omega-check`)
- HTTP/HTTPS 점검, 헤더, TLS(`omega-scan`)
- 크롤링과 아키텍처 순회(`omega-deep`/`omega-fold`)
- 부하 테스트(`omega-stress`), 퍼징(`omega-fuzz`)
- 대화형 TUI 지도(내보낸 HTML 보고서 전용)
- 연속, 다중 프로브, 다중 관측 지점 MTR
- 대상의 일괄/주기 실행 또는 반복 감시 — `TrackRun`은 항상 명시적인 수동 작업으로 남습니다
- SQLite 스키마 마이그레이션 엔진(추가형 스키마, 스위트의 다른 부분과 같은 방식)

---

> Omega-track — 관측하고, 연결하고, 평가하고, 보고한다.
> 모든 데이터에 명시적인 신뢰도를 담은 디지털 신원이며, 결코 위장된 확실성이 아닙니다.
