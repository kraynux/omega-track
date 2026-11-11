<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Giấy phép MIT (xem tệp LICENSE) -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-track.png" alt="Omega-Track" width="512">
</div>

# 🛰️ OMEGA-TRACK

**Lập hồ sơ danh tính số và quan sát đường đi mạng**

> Được phát triển bởi [kraynux](https://github.com/kraynux) cho [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Trang chính thức: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; Xem trước: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Giao diện và báo cáo xuất có sẵn bằng **17 ngôn ngữ** — xem [Ngôn ngữ giao diện](#ngôn-ngữ-giao-diện).  
**Ngôn ngữ:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track** là công cụ TUI + CLI xây dựng, từ một IP, một địa chỉ IPv6 hoặc một tên miền, danh tính số đầy đủ nhất có thể: ai trả lời phía sau mục tiêu này, đường đi đến đó ra sao, và mỗi thông tin đáng tin cậy đến mức nào. Đây là một công cụ của bộ `omega-`, được tổ chức theo Clean Architecture — xem `docs/PRODUCT_SCOPE.md` và `docs/DATA_SOURCES.md` để biết đầy đủ chi tiết.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/vi/omega-track/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/vi/omega-track/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/vi/omega-track/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/vi/omega-track/D.png" width="24%" />
</p>

## 1. Tầm nhìn và phạm vi

Omega-track trả lời hai câu hỏi: “mục tiêu này là ai?” (danh tính RDAP/DNS/chứng chỉ/danh tiếng) và “làm sao để đến được đó?” (đường đi mạng NeoTrace, GeoIP, ASN). Nó bổ sung cho `omega-check` (mức độ phơi bày mạng), `omega-scan` (vệ sinh HTTP/HTTPS) và `omega-deep` (phân tích kiến trúc có giới hạn), mà không trùng lặp với chúng.

### Những gì Omega-track làm

- Nhận mục tiêu là IP, IPv6 hoặc tên miền, được lưu lại và có thể ghim (ủy quyền lâu dài).
- Tập hợp thông tin công khai, thụ động hoặc được hồ sơ bật rõ ràng (RDAP, DNS, Certificate Transparency, kho lưu trữ Wayback, thông báo BGP).
- Chạy traceroute nâng cao kiểu NeoTrace (hành động mạng chủ động duy nhất trong lõi sản phẩm).
- Làm giàu thông tin cho mỗi IP liên quan bằng cơ sở dữ liệu GeoIP cục bộ (DB-IP Lite không cần khóa, MaxMind GeoLite2 tùy chọn có khóa).
- Truy vấn, bằng khóa do người dùng cung cấp, các nguồn danh tiếng (VirusTotal, HIBP), luôn công bố hạn mức và dữ liệu được gửi trước mọi lần kích hoạt.
- Liên kết các dữ liệu quan sát được thành một hồ sơ nhất quán, với mức tin cậy rõ ràng cho từng dữ liệu.
- Lưu mục tiêu, lần chạy, kết quả, lỗi và bản xuất ở máy cục bộ (SQLite, `./var/`).
- Cung cấp TUI Textual và CLI tương đương nghiêm ngặt về tính năng.
- Tạo báo cáo HTML (5 chủ đề, đồ thị quan hệ Mermaid nhúng sẵn), JSON, Markdown, CSV, cùng các tệp DOT và Mermaid độc lập.

### Những gì Omega-track không làm

| Chức năng | Công cụ phụ trách |
|---|---|
| Quét cổng, nhận diện dịch vụ và banner | OMEGA-CHECK |
| Kiểm tra HTTP/HTTPS, header, TLS, vệ sinh web | OMEGA-SCAN |
| Thu thập, duyệt kiến trúc và đi sâu vào các mục tiêu liên kết | OMEGA-DEEP |
| Thu thập từ xa từng trang (liên kết, tệp) | OMEGA-FOLD |
| Kiểm thử tải | OMEGA-STRESS |
| Fuzzing và kiểm thử độ bền ứng dụng | OMEGA-FUZZ |

Cần tránh, kể cả ngoài MVP: dò tên miền con bằng brute-force, quét cổng, thu thập web, thu thập xâm phạm dữ liệu cá nhân, tự động hóa việc vượt qua cơ chế bảo vệ, scraping mong manh trên các nền tảng yêu cầu xác thực, tìm kiếm người/mạng xã hội/pastebin-rò rỉ, giám sát định kỳ/lặp lại một mục tiêu (xem `docs/PRODUCT_SCOPE.md` §7 "Cố ý hoãn lại").

### Lưu ý về việc sử dụng được ủy quyền

Omega-track là công cụ điều tra mạng dành cho mục đích hợp pháp: kiểm tra hạ tầng của chính bạn, ứng phó sự cố, theo dõi một phạm vi mà bạn được phép ghi nhận. Việc thu thập gần như hoàn toàn thụ động/công khai (RDAP, DNS, nhật ký CT — dữ liệu mà mục tiêu hoặc nhà đăng ký của nó đã công khai), ngoại trừ traceroute (chủ động nhẹ, luôn hiển thị trong hồ sơ được dùng).

**Không có lần quan sát nào bắt đầu trên mục tiêu chưa ghim nếu không có xác nhận rõ ràng** (`--authorize` trong CLI, xác nhận trong TUI). Chỉ mình bạn chịu trách nhiệm kiểm tra rằng việc sử dụng tuân thủ pháp luật hiện hành và điều khoản sử dụng của các nguồn bên thứ ba được truy vấn.

## 2. Cài đặt

### Yêu cầu

- Python 3.10+
- Kết nối Internet, cho các phụ thuộc và các nguồn thụ động được truy vấn
- Đã cài `traceroute` hoặc `tracepath` (mô-đun NeoTrace) — nếu thiếu thì giảm cấp gọn gàng, phần còn lại của công cụ vẫn hoạt động bình thường

### Cài đặt

```bash
[ -d omega-track ] && echo "ℹ️ Đã giải nén ở đây, bỏ qua bước này." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Tạo môi trường ảo `.venv` nếu chưa có.
2. Cài các phụ thuộc (`pip install -e .`, `pyproject.toml` vẫn là nguồn sự thật duy nhất).
3. Cấp quyền thực thi cho `omega-track.sh` và `install.sh`.
4. Thêm bí danh `track` vào `~/.bashrc` và `~/.zshrc` (không trùng lặp nếu đã có).

### Phụ thuộc

Khai báo trong `pyproject.toml` (không có `requirements.txt` riêng):
- `omega-lib`: thư viện dùng chung của bộ công cụ (`ConfidenceLevel`, chủ đề, nhận diện terminal)
- `textual`: giao diện TUI, chủ đề, tự động thích ứng với terminal
- `dnspython`: phân giải DNS thuận và ngược
- `httpx`: các đầu dò RDAP/CT/kho lưu trữ/BGP/VirusTotal/HIBP
- `maxminddb`: đọc cơ sở dữ liệu GeoIP cục bộ (DB-IP Lite, MaxMind GeoLite2)
- `jinja2`: khuôn mẫu cho bản xuất HTML
- Phụ thuộc phát triển (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Sử dụng

### Chế độ tương tác (TUI)

Khuyên dùng hằng ngày — khởi chạy không có đối số:

```bash
./omega-track.sh
```
nếu bạn đã tạo bí danh, chỉ cần gõ `track` trong terminal:
```bash
track
```

Luồng sử dụng: màn hình khởi động (đóng khi nhấn phím hoặc nhấp chuột) → menu chính (Mục tiêu / Tracker / Kết quả / Lịch sử / Bảng điều khiển / GeoIP / Nguồn có khóa / Thiết lập / Trợ giúp) → nhập hoặc chọn mục tiêu (xác nhận rõ ràng nếu chưa ghim) và chọn các mô-đun thu thập → quan sát (thanh tiến trình và diễn biến các thao tác trực tiếp, có thể hủy) → kết quả chi tiết theo thẻ (Danh tính/DNS/Mạng / ASN/NeoTrace/Chứng chỉ/Kho lưu trữ/Quan hệ/Chẩn đoán, xuất) → lịch sử/bảng điều khiển/thiết lập từ menu chính. Việc thích ứng với terminal (màu sắc, kích thước, giảm cấp cấu trúc) diễn ra tự động.

#### Phím tắt

| Phím | Hành động |
|---|---|
| `↑` / `↓` | Di chuyển giữa các mục trên màn hình |
| `Tab` / `Shift+Tab` | Di chuyển giữa các trường của biểu mẫu |
| `Esc` | Quay lại màn hình trước (xác nhận thoát ở màn hình chính) |
| `t` | Chủ đề tiếp theo (áp dụng ngay, không cần xác nhận) |
| `r` | Làm mới việc nhận diện terminal |
| `a` | Hiện trợ giúp |
| `q` | Thoát (có xác nhận) |

### Ngôn ngữ giao diện

Giao diện có sẵn bằng 17 ngôn ngữ: tiếng Pháp, tiếng Anh, tiếng Tây Ban Nha, tiếng Bồ Đào Nha (Brazil), tiếng Ý, tiếng Đức, tiếng Hà Lan, tiếng Ba Lan, tiếng Nga, tiếng Trung giản thể, tiếng Việt, tiếng Thái, tiếng Indonesia, tiếng Nhật, tiếng Hàn, tiếng Hindi và tiếng Ả Rập. Lựa chọn được thực hiện trong Thiết lập (“Langue / Language”) và có hiệu lực sau khi khởi động lại giao diện; biến `OMEGA_TRACK_LANG` (ví dụ `OMEGA_TRACK_LANG=vi ./omega-track.sh`) buộc dùng một ngôn ngữ trong một phiên. Khi khởi chạy từ omega-suite, omega-track dùng ngôn ngữ của bộ công cụ. Trên console văn bản Linux (TTY), tiếng Việt và các ngôn ngữ không dùng chữ Latinh được hiển thị bằng tiếng Anh trong suốt phiên đó. Dòng lệnh vẫn bằng tiếng Pháp.

### Liên hệ và hỗ trợ

Phần trợ giúp (phím `a`) có màn hình **Liên hệ và hỗ trợ**: *Mời một ly cà phê* (trang PayPal của nhà phát triển), *Liên hệ hỗ trợ* (địa chỉ email và biểu mẫu liên hệ của trang web, hiển thị rõ ràng), *Khai báo là người dùng (ẩn danh)* và *Kiểm tra cập nhật*. Việc khai báo là tự nguyện, tắt theo mặc định và chỉ gửi một lần: nó chỉ dùng để đếm số người dùng và, nếu bạn muốn, châu lục hoặc quốc gia của họ (danh sách đóng, không bao giờ là văn bản tự do). Nó gửi một khóa được tạo ngẫu nhiên, tên phần mềm (`omega-track`) và phiên bản của nó; không bao giờ gửi tên, tên máy, thiết lập, mục tiêu hay kết quả. Địa chỉ IP không được lưu trong các khai báo, nhưng, như mọi lượt truy cập, nó đi qua các kiểm tra bảo mật và nhật ký của máy chủ nhận. Có thể rút lại bất cứ lúc nào từ cùng màn hình (*Không khai báo tôi nữa*). Việc kiểm tra cập nhật chỉ đọc danh sách các phiên bản đã phát hành trên trang web, và không bao giờ khi chưa nhấp.

### Chế độ viết script (CLI)

Bất kỳ lệnh con nào cũng kích hoạt chế độ CLI:

```bash
# Mục tiêu
./omega-track.sh target add example.org --alias "trang giới thiệu" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# Khởi chạy và theo dõi một lần quan sát
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# Lịch sử
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# Xuất — 6 định dạng, 5 chủ đề cho HTML
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# Nguồn danh tiếng có khóa (thông tin công bố hiển thị trước mọi lần lưu)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <khoa_api>

# Thiết lập và dọn dẹp
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# Chẩn đoán cục bộ (phiên bản, khả năng, đường dẫn, trạng thái GeoIP)
./omega-track.sh diagnostics
```

Mọi lệnh con đều chấp nhận `--json` để có đầu ra máy đọc được nghiêm ngặt.

#### Mã thoát

| Mã | Ý nghĩa |
|---:|---|
| `0` | Thành công (quan sát hoàn tất, `COMPLETED`) |
| `1` | Lỗi xác thực (mục tiêu không hợp lệ, định dạng xuất không xác định, chuyển trạng thái không hợp lệ, thiếu khóa API...) |
| `2` | Mục tiêu chưa được ủy quyền (không ghim, cũng không có `--authorize`) |
| `3` | Không tìm thấy tài nguyên hoặc nguồn không khả dụng (mục tiêu/lần chạy không xác định, tải GeoIP thất bại) |
| `4` | Quan sát một phần (`PARTIAL`) — không phải thất bại, chỉ một số mô-đun thành công |
| `5` | Lỗi nội bộ không mong muốn |
| `130` | Bị người dùng ngắt (`Ctrl+C`) |

### Định dạng mục tiêu được chấp nhận

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 Tên miền
```

## 4. Mô-đun thu thập

| Mô-đun | Chế độ thu thập | Bật mặc định | Cần khóa |
|---|---|:---:|:---:|
| `dns` | Chủ động nhẹ (phân giải thuận) | có | không |
| `reverse_dns` | Chủ động nhẹ (PTR) | có | không |
| `rdap` | Thụ động công khai | có | không |
| `neotrace` | Chủ động nhẹ (traceroute/tracepath) | có | không |
| `certificate_transparency` | Thụ động công khai (`crt.sh`) | không | không |
| `archives` | Thụ động công khai (Wayback Machine) | không | không |
| `bgp` | Thụ động công khai (RIPEstat) | không | không |
| `virustotal` | Có khóa người dùng | không | có (miễn phí) |
| `hibp` | Có khóa người dùng | không | có (**trả phí** từ 2022) |

Bốn mô-đun đầu tạo thành nền tảng MVP (`dns`/`reverse_dns`/`rdap`/`neotrace`) và được đánh dấu sẵn trong biểu mẫu khởi chạy; năm mô-đun tiếp theo là tùy chọn và phải được bật rõ ràng. Một nguồn chưa cấu hình khóa không bao giờ làm lần quan sát thất bại: mô-đun tương ứng chỉ đơn giản chuyển sang `SKIPPED` (“không chạy”). Chi tiết từng nguồn, hạn mức và giấy phép: `docs/DATA_SOURCES.md`.

## 5. Kiến trúc

Omega-track được tổ chức theo **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), bám theo khuôn mẫu của bộ `omega-` (xem `omega-check`/`omega-fold`) và được `import-linter` kiểm tra ở mỗi lần sửa đổi.

```text
src/omega_track/
├── domain/          Logic nghiệp vụ thuần (mục tiêu, TrackRun/ModuleRun, findings, quan hệ, hồ sơ...)
├── application/     Ca sử dụng (commands/queries/bộ điều phối giai đoạn/chính sách)
├── ports/           Hợp đồng mà ứng dụng mong đợi (bộ thu thập, kho dữ liệu, bộ xuất...)
├── infrastructure/  Triển khai cụ thể (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) và cli/ (viết script), tương đương tính năng nghiêm ngặt
├── app/             Lắp ráp (DependencyContainer, khởi động, vòng đời)
├── core/            Từ vựng dùng chung (phiên bản, tái xuất từ omega-lib)
└── plugins/         Mô-đun tùy chọn một nguồn (CT, kho lưu trữ, BGP, VirusTotal, HIBP)
```

Quy tắc thiết kế:
- `domain/` không bao giờ làm việc với mạng hay I/O; `infrastructure/` làm việc với mạng và I/O, nhưng không bao giờ phán xét.
- `interfaces/` chỉ hiển thị, không chứa logic nghiệp vụ nào — CLI và TUI gọi đúng cùng các ca sử dụng.
- 1 mô-đun thu thập = 1 nguồn = 1 trạng thái (`ModuleRun`): không bao giờ gộp hai nguồn dưới một trạng thái mơ hồ duy nhất.
- Việc thiếu một trường riêng lẻ không bao giờ là lỗi; chỉ khi một nguồn hoàn toàn không khả dụng mới dẫn đến `SKIPPED`/`FAILED`.

## 6. Nguồn dữ liệu

| Nguồn | Nhà cung cấp | Khóa | Chế độ |
|---|---|:---:|---|
| DNS thuận/ngược | Bộ phân giải hệ thống | không | Chủ động nhẹ |
| RDAP | Bootstrap IANA → RIR/nhà đăng ký | không | Thụ động công khai |
| Certificate Transparency | `crt.sh` (Sectigo) | không | Thụ động công khai |
| Kho lưu trữ web | Wayback Machine (Internet Archive) | không | Thụ động công khai |
| BGP / thông báo mạng | RIPEstat (RIPE NCC) | không | Thụ động công khai |
| GeoIP | DB-IP Lite (mặc định) hoặc MaxMind GeoLite2 | không / có | Ngoại tuyến (cơ sở dữ liệu cục bộ) |
| NeoTrace | `traceroute`/`tracepath` cục bộ | không | Chủ động nhẹ |
| Danh tiếng | VirusTotal | có (miễn phí) | Có khóa |
| Danh tiếng | Have I Been Pwned | có (trả phí) | Có khóa |

Hạn mức, giấy phép và phương án dự phòng chính xác cho từng nguồn: `docs/DATA_SOURCES.md`. Không khóa API nào xuất hiện trong nhật ký, bản xuất hay màn hình chẩn đoán.

## 7. Chính sách tin cậy

Mỗi trường được thu thập mang một trong các mức sau (dùng chung với toàn bộ bộ công cụ qua `omega-lib`):

| Mức | Ý nghĩa |
|---|---|
| `VERIFIED` | Sự kiện giao thức quan sát trực tiếp, mục tiêu không thể giả mạo (vd: phản hồi DNS trực tiếp, đo traceroute cục bộ). |
| `DECLARED` | Giá trị do nguồn tự khai báo trong một trường mà nó kiểm soát hoàn toàn (vd: dữ liệu RDAP do nhà đăng ký hiển thị) — hợp lý nhưng có thể giả mạo tùy ý. |
| `CORROBORATED` | Một giá trị `DECLARED` được xác nhận bởi một dấu hiệu độc lập (vd: tên miền được thấy trong ít nhất hai nhật ký Certificate Transparency khác nhau). |
| `INFERRED` | Suy ra từ một mẫu/kinh nghiệm, không có khai báo rõ ràng (vd: ASN chung được dùng để gợi ý một quan hệ, không bao giờ tự động nâng mức). |
| `UNKNOWN` | Không có dấu hiệu nào khai thác được, hoặc bị mục tiêu chủ động che giấu. |

Điểm tin cậy tổng thể của một lần quan sát là công cụ hỗ trợ đọc, không bao giờ là phán quyết bảo mật.

## 8. Mức thu thập, ủy quyền và che giấu thông tin

Mỗi hồ sơ nêu rõ bản chất các hành động của nó (`CollectionMode`):

- **Ngoại tuyến**: xác thực mục tiêu, đọc GeoIP cục bộ, liên kết trên dữ liệu đã lưu, xuất — không dùng mạng.
- **Thụ động công khai**: RDAP, DNS công khai, nhật ký CT, kho lưu trữ, BGP — chỉ mục tiêu được truy vấn được gửi cho bên thứ ba, đặc tính vốn có của giao thức.
- **Chủ động nhẹ**: phân giải DNS, DNS ngược, traceroute — bộ phân giải được cấu hình trên máy và mọi bộ định tuyến trung gian trên đường đi đều thấy yêu cầu.
- **Có khóa người dùng**: nhà cung cấp yêu cầu khóa hoặc áp dụng hạn mức, chỉ được bật sau khi cấu hình rõ ràng và hiển thị thông tin công bố (hạn mức, dữ liệu được gửi).

**Bảo vệ ủy quyền**: không có lần quan sát nào bắt đầu trên mục tiêu chưa ghim nếu không có xác nhận rõ ràng (`--authorize` trong CLI, ô đánh dấu trong TUI). Ghim một mục tiêu sẽ ủy quyền lâu dài cho các lần quan sát sau này của nó.

**Che giấu thông tin trong bản xuất**: mỗi bản xuất chấp nhận một chính sách (`none`/`contacts_only`/`sensitive_only`/`strict`) để che các trường nhạy cảm (đặc biệt là liên hệ RDAP) trong kết quả xuất — còn bộ lưu trữ cục bộ thì luôn giữ dữ liệu đầy đủ đã thu thập. Chi tiết: `docs/PRIVACY.md`.

## 9. Tương thích terminal

TUI (Textual) tự động phát hiện khả năng của terminal (trình giả lập, kích thước) và điều chỉnh bảng kiểu cấu trúc tương ứng (`complete`/`standard`/`reduced`/`mono`), không cần cờ thủ công. Chế độ CLI luôn là văn bản thuần, không phụ thuộc terminal. Chính sách dùng chung cho toàn bộ bộ `omega-` (`omega-lib`, `terminal/policies.py`).

### Hồ sơ theo trình giả lập được phát hiện

| Trình giả lập | Hồ sơ ban đầu |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH hiện đại | `reduced` |
| TTY Linux, SSH cũ | `mono` |
| Trình giả lập không nhận ra | `reduced` (dự phòng mặc định) |

### Hồ sơ theo kích thước terminal

| Kích thước tối thiểu (cột × dòng) | Mức trần hồ sơ |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| nhỏ hơn | `mono` |

Hồ sơ cuối cùng được chọn là **hồ sơ hạn chế hơn trong hai** (trình giả lập và kích thước). Có thể làm mới trực tiếp bằng phím `r`.

## 10. Xuất

Báo cáo Markdown và HTML được viết bằng ngôn ngữ đã chọn trong Thiết lập (“Ngôn ngữ bản xuất”, mặc định là ngôn ngữ giao diện); JSON, CSV, DOT và Mermaid vẫn là dữ liệu và không được dịch. Báo cáo mặc định được tạo trong `var/exports/` (đường dẫn thời gian chạy gắn với thư mục dự án, `$OMEGA_TRACK_VAR_DIR` để ghi đè), hoặc tại đường dẫn được chỉ định (`--output` trong CLI, hộp thoại trong TUI). Tên tệp duy nhất có dấu thời gian: `{dau_thoi_gian}_{muc_tieu}_{id_ngan}.{phan_mo_rong}`.

| Định dạng | Nội dung |
|---|---|
| `json` | Cấu trúc đầy đủ của lần quan sát (`TrackRun` + findings + quan hệ), nguồn sự thật, tuần tự hóa JSON nghiêm ngặt |
| `markdown` | Báo cáo gọn cho người đọc, đọc được ngoài terminal |
| `html` | Báo cáo web độc lập, 5 chủ đề tùy chọn (`--theme`), đồ thị quan hệ Mermaid nhúng inline |
| `csv` | Mỗi loại finding một bảng |
| `dot` | Đồ thị quan hệ Graphviz, tệp độc lập |
| `mermaid` | Đồ thị quan hệ Mermaid, tệp độc lập |

## 11. Lịch sử, dọn dẹp và chạy lại

Mỗi lần quan sát được lưu lại (SQLite, `var/db/omega-track.db`): lịch sử có thể xem và lọc (mục tiêu/trạng thái/nhãn/khoảng thời gian), bảng điều khiển tổng hợp (phân bố theo trạng thái, độ tin cậy theo mô-đun, loại hình các findings gần nhất), chạy lại một lần quan sát trên cùng mục tiêu mà không cần nhập lại (`track replay`), và dọn dẹp lịch sử cũ với bản xem trước bắt buộc trước mọi lần xóa (`cleanup preview` trước `cleanup run --yes`).

## 12. Kiểm thử

```bash
source .venv/bin/activate
lint-imports        # kiểm tra Dependency Rule
pytest -q           # 485 bài kiểm thử
ruff check .
mypy src
```

Cấu trúc: `tests/unit/` (miền và ứng dụng, không có I/O thật), `tests/integration/` (SQLite/tệp thật, máy chủ HTTP giả `pytest-httpserver`, TUI không giao diện qua API `Pilot` của Textual).

## 13. Ngoài phạm vi

- Lịch sử WHOIS/DNS đầy đủ, passive DNS thương mại
- Tìm kiếm người, mạng xã hội, pastebin/rò rỉ
- Quét cổng, nhận diện dịch vụ và banner (`omega-check`)
- Kiểm tra HTTP/HTTPS, header, TLS (`omega-scan`)
- Thu thập và duyệt kiến trúc (`omega-deep`/`omega-fold`)
- Kiểm thử tải (`omega-stress`), fuzzing (`omega-fuzz`)
- Bản đồ TUI tương tác (dành riêng cho báo cáo HTML được xuất)
- MTR liên tục, nhiều đầu dò và nhiều điểm quan sát
- Chế độ hàng loạt/định kỳ/giám sát lặp lại một mục tiêu — một `TrackRun` luôn là một hành động thủ công rõ ràng
- Công cụ di chuyển lược đồ SQLite (lược đồ cộng dồn, cùng cách làm như phần còn lại của bộ công cụ)

---

> Omega-track — Quan sát, liên kết, đánh giá, báo cáo.
> Một danh tính số với mức tin cậy rõ ràng cho từng dữ liệu, không bao giờ là sự chắc chắn ngụy trang.
