<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Lisensi MIT (lihat berkas LICENSE) -->
<div align="center">
  <img src="../../assets/omega-track.png" alt="Omega-Track" width="386">
</div>

# 🛰️ OMEGA-TRACK

**Pemrofilan identitas digital dan pengamatan jalur jaringan**

> Dibuat oleh [kraynux](https://github.com/kraynux) untuk [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Halaman resmi: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; Pratinjau: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Antarmuka dan laporan ekspor tersedia dalam **17 bahasa** — lihat [Bahasa antarmuka](#bahasa-antarmuka).  
**Bahasa:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track** adalah alat TUI + CLI yang membangun, dari sebuah IP, alamat IPv6, atau domain, identitas digital selengkap mungkin: siapa yang menjawab di balik target ini, bagaimana lalu lintas sampai ke sana, dan seberapa besar keyakinan yang layak diberikan pada setiap informasi. Ini adalah alat dari rangkaian `omega-`, disusun dengan Clean Architecture — lihat `docs/PRODUCT_SCOPE.md` dan `docs/DATA_SOURCES.md` untuk detail lengkapnya.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/id/omega-track/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/id/omega-track/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/id/omega-track/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/id/omega-track/D.png" width="24%" />
</p>

## 1. Visi dan cakupan

Omega-track menjawab dua pertanyaan: "siapa target ini?" (identitas RDAP/DNS/sertifikat/reputasi) dan "bagaimana cara sampai ke sana?" (jalur jaringan NeoTrace, GeoIP, ASN). Alat ini melengkapi `omega-check` (keterpaparan jaringan), `omega-scan` (kebersihan HTTP/HTTPS), dan `omega-deep` (analisis arsitektur terbatas), tanpa menduplikasinya.

### Yang dilakukan Omega-track

- Menerima target berupa IP, IPv6, atau nama domain, yang disimpan dan opsional disematkan (otorisasi berkelanjutan).
- Menghimpun informasi publik, pasif atau diaktifkan secara eksplisit oleh profil (RDAP, DNS, Certificate Transparency, arsip Wayback, pengumuman BGP).
- Menjalankan traceroute yang diperkaya bergaya NeoTrace (satu-satunya aksi jaringan aktif di inti produk).
- Memperkaya setiap IP yang relevan dengan basis data GeoIP lokal (DB-IP Lite tanpa kunci, MaxMind GeoLite2 opsional dengan kunci).
- Menanyai sumber reputasi (VirusTotal, HIBP) dengan kunci dari pengguna, selalu mengungkapkan kuota dan data yang dikirim sebelum aktivasi apa pun.
- Menghubungkan data yang diamati menjadi profil yang konsisten, dengan tingkat keyakinan eksplisit pada setiap data.
- Menyimpan target, eksekusi, hasil, galat, dan ekspor secara lokal (SQLite, `./var/`).
- Menyediakan TUI Textual dan CLI yang benar-benar setara fungsinya.
- Menghasilkan laporan HTML (5 tema, grafik relasi Mermaid tertanam), JSON, Markdown, CSV, serta berkas DOT dan Mermaid mandiri.

### Yang tidak dilakukan Omega-track

| Fungsi | Alat yang bertanggung jawab |
|---|---|
| Pemindaian port, identifikasi layanan dan banner | OMEGA-CHECK |
| Pemeriksaan HTTP/HTTPS, header, TLS, kebersihan web | OMEGA-SCAN |
| Crawl, penelusuran arsitektur, dan turun ke target terkait | OMEGA-DEEP |
| Crawl jarak jauh halaman demi halaman (tautan, berkas) | OMEGA-FOLD |
| Uji beban | OMEGA-STRESS |
| Fuzzing dan uji ketahanan aplikasi | OMEGA-FUZZ |

Yang perlu dihindari, termasuk di luar MVP: brute-force subdomain, pemindaian port, crawl web, pengumpulan data pribadi yang invasif, otomatisasi untuk mengakali perlindungan, scraping rapuh pada platform yang mewajibkan autentikasi, pencarian orang/jejaring sosial/pastebin-kebocoran, pemantauan berkala/berulang terhadap target (lihat `docs/PRODUCT_SCOPE.md` §7 "Sengaja ditunda").

### Peringatan penggunaan terotorisasi

Omega-track adalah alat investigasi jaringan untuk penggunaan yang sah: audit infrastruktur Anda sendiri, penanganan insiden, pengawasan cakupan yang berhak Anda dokumentasikan. Pengumpulan tetap hampir sepenuhnya pasif/publik (RDAP, DNS, log CT — data yang sudah dipublikasikan oleh target atau registrarnya), kecuali traceroute (aktif ringan, selalu terlihat di profil yang dipakai).

**Tidak ada pengamatan yang dimulai pada target yang belum disematkan tanpa konfirmasi eksplisit** (`--authorize` di CLI, konfirmasi di TUI). Anda sendiri yang bertanggung jawab memastikan penggunaan Anda mematuhi hukum yang berlaku serta ketentuan penggunaan sumber pihak ketiga yang ditanyai.

## 2. Instalasi

### Prasyarat

- Python 3.10+
- Koneksi Internet, untuk dependensi dan sumber pasif yang ditanyai
- `traceroute` atau `tracepath` terpasang (modul NeoTrace) — jika tidak ada, fungsinya dikurangi dengan rapi dan bagian lain alat tetap berjalan normal

### Instalasi

```bash
[ -d omega-track ] && echo "ℹ️ Sudah diekstrak di sini, langkah dilewati." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Membuat lingkungan virtual `.venv` jika belum ada.
2. Memasang dependensi (`pip install -e .`, `pyproject.toml` tetap menjadi satu-satunya sumber kebenaran).
3. Menjadikan `omega-track.sh` dan `install.sh` dapat dieksekusi.
4. Menambahkan alias `track` ke `~/.bashrc` dan `~/.zshrc` (tanpa duplikat jika sudah ada).

### Dependensi

Dideklarasikan di `pyproject.toml` (tanpa `requirements.txt` terpisah):
- `omega-lib`: pustaka bersama rangkaian (`ConfidenceLevel`, tema, deteksi terminal)
- `textual`: antarmuka TUI, tema, penyesuaian otomatis dengan terminal
- `dnspython`: resolusi DNS maju dan balik
- `httpx`: probe RDAP/CT/arsip/BGP/VirusTotal/HIBP
- `maxminddb`: membaca basis data GeoIP lokal (DB-IP Lite, MaxMind GeoLite2)
- `jinja2`: templat untuk ekspor HTML
- Dependensi pengembangan (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Penggunaan

### Mode interaktif (TUI)

Disarankan untuk penggunaan sehari-hari — dijalankan tanpa argumen:

```bash
./omega-track.sh
```
jika Anda sudah membuat alias, cukup ketik `track` di terminal:
```bash
track
```

Alur: layar pembuka (tertutup dengan menekan tombol atau klik) → menu utama (Target / Tracker / Hasil / Riwayat / Dasbor / GeoIP / Sumber berkunci / Pengaturan / Bantuan) → mengetik atau memilih target (konfirmasi eksplisit jika belum disematkan) dan memilih modul pengumpulan → pengamatan (indikator dan jalannya operasi secara langsung, dapat dibatalkan) → hasil terperinci per tab (Identitas/DNS/Jaringan / ASN/NeoTrace/Sertifikat/Arsip/Relasi/Diagnostik, ekspor) → riwayat/dasbor/pengaturan dari menu utama. Penyesuaian dengan terminal (warna, ukuran, penyederhanaan struktur) berlangsung otomatis.

#### Pintasan keyboard

| Tombol | Aksi |
|---|---|
| `↑` / `↓` | Berpindah antarelemen layar |
| `Tab` / `Shift+Tab` | Berpindah antarkolom formulir |
| `Esc` | Kembali ke layar sebelumnya (konfirmasi keluar di layar utama) |
| `t` | Tema berikutnya (langsung diterapkan, tanpa konfirmasi) |
| `r` | Menyegarkan deteksi terminal |
| `a` | Menampilkan bantuan |
| `q` | Keluar (dengan konfirmasi) |

### Bahasa antarmuka

Antarmuka tersedia dalam 17 bahasa: Prancis, Inggris, Spanyol, Portugis (Brasil), Italia, Jerman, Belanda, Polandia, Rusia, Tionghoa Sederhana, Vietnam, Thai, Indonesia, Jepang, Korea, Hindi, dan Arab. Pilihan dibuat di Pengaturan ("Langue / Language") dan berlaku setelah antarmuka dimulai ulang; variabel `OMEGA_TRACK_LANG` (misalnya `OMEGA_TRACK_LANG=id ./omega-track.sh`) memaksakan bahasa untuk satu sesi. Jika dijalankan dari omega-suite, omega-track memakai bahasa rangkaian. Di konsol teks Linux (TTY), bahasa beraksara non-Latin ditampilkan dalam bahasa Inggris selama sesi itu. Baris perintah tetap berbahasa Prancis.

### Kontak dan dukungan

Bantuan (tombol `a`) menyediakan layar **Kontak dan dukungan**: *Traktir kopi* (halaman PayPal pengembang), *Hubungi dukungan* (alamat email dan formulir kontak situs, ditampilkan apa adanya), *Daftarkan saya sebagai pengguna (anonim)*, dan *Periksa pembaruan*. Pendaftaran bersifat sukarela, nonaktif secara bawaan, dan dikirim hanya sekali: hanya digunakan untuk menghitung pengguna dan, jika Anda mau, benua atau negara mereka (daftar tertutup, tidak pernah teks bebas). Yang dikirim adalah kunci yang diambil secara acak, nama perangkat lunak (`omega-track`), dan versinya; tidak pernah nama, nama mesin, pengaturan, target, maupun hasil. Alamat IP tidak disimpan dalam pendaftaran, tetapi, seperti setiap kunjungan, melewati pemeriksaan keamanan dan log server penerima. Penarikan kapan saja dari layar yang sama (*Jangan daftarkan saya lagi*). Pemeriksaan pembaruan hanya membaca daftar versi yang dipublikasikan di situs, dan tidak pernah tanpa klik.

### Mode skrip (CLI)

Subperintah apa pun memicu mode CLI:

```bash
# Target
./omega-track.sh target add example.org --alias "situs etalase" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# Memulai dan mengikuti sebuah pengamatan
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# Riwayat
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# Ekspor — 6 format, 5 tema untuk HTML
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# Sumber reputasi berkunci (pengungkapan ditampilkan sebelum penyimpanan apa pun)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <kunci_api>

# Pengaturan dan pembersihan
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# Diagnostik lokal (versi, kapabilitas, jalur, status GeoIP)
./omega-track.sh diagnostics
```

Setiap subperintah menerima `--json` untuk keluaran yang benar-benar dapat dibaca mesin.

#### Kode keluar

| Kode | Arti |
|---:|---|
| `0` | Berhasil (pengamatan selesai, `COMPLETED`) |
| `1` | Galat validasi (target tidak valid, format ekspor tidak dikenal, transisi status tidak valid, kunci API tidak ada...) |
| `2` | Target tidak terotorisasi (tidak disematkan dan tanpa `--authorize`) |
| `3` | Sumber daya tidak ditemukan atau sumber tidak tersedia (target/eksekusi tidak dikenal, unduhan GeoIP gagal) |
| `4` | Pengamatan sebagian (`PARTIAL`) — bukan kegagalan, hanya sebagian modul yang berhasil |
| `5` | Galat internal tak terduga |
| `130` | Dihentikan oleh pengguna (`Ctrl+C`) |

### Format target yang diterima

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 Domain
```

## 4. Modul pengumpulan

| Modul | Mode pengumpulan | Aktif secara bawaan | Perlu kunci |
|---|---|:---:|:---:|
| `dns` | Aktif ringan (resolusi maju) | ya | tidak |
| `reverse_dns` | Aktif ringan (PTR) | ya | tidak |
| `rdap` | Pasif publik | ya | tidak |
| `neotrace` | Aktif ringan (traceroute/tracepath) | ya | tidak |
| `certificate_transparency` | Pasif publik (`crt.sh`) | tidak | tidak |
| `archives` | Pasif publik (Wayback Machine) | tidak | tidak |
| `bgp` | Pasif publik (RIPEstat) | tidak | tidak |
| `virustotal` | Dengan kunci pengguna | tidak | ya (gratis) |
| `hibp` | Dengan kunci pengguna | tidak | ya (**berbayar** sejak 2022) |

Empat modul pertama membentuk dasar MVP (`dns`/`reverse_dns`/`rdap`/`neotrace`) dan tercentang secara bawaan di formulir peluncuran; lima berikutnya opsional dan harus diaktifkan secara eksplisit. Sumber tanpa kunci yang dikonfigurasi tidak pernah menggagalkan pengamatan: modul terkait hanya beralih ke `SKIPPED` ("tidak dijalankan"). Detail per sumber, kuota, dan lisensi: `docs/DATA_SOURCES.md`.

## 5. Arsitektur

Omega-track disusun dengan **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), selaras dengan templat rangkaian `omega-` (lihat `omega-check`/`omega-fold`) dan diperiksa oleh `import-linter` pada setiap perubahan.

```text
src/omega_track/
├── domain/          Logika bisnis murni (target, TrackRun/ModuleRun, findings, relasi, profil...)
├── application/     Kasus penggunaan (commands/queries/orkestrator fase/kebijakan)
├── ports/           Kontrak yang diharapkan aplikasi (pengumpul, repositori, pengekspor...)
├── infrastructure/  Implementasi konkret (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) dan cli/ (untuk skrip), dengan kesetaraan fungsi yang ketat
├── app/             Perakitan (DependencyContainer, bootstrap, siklus hidup)
├── core/            Kosakata lintas bagian (versi, ekspor ulang dari omega-lib)
└── plugins/         Modul opsional bersumber tunggal (CT, arsip, BGP, VirusTotal, HIBP)
```

Aturan desain:
- `domain/` tidak pernah melakukan jaringan atau I/O; `infrastructure/` melakukan jaringan dan I/O, tetapi tidak pernah menilai.
- `interfaces/` menampilkan dan tidak berisi logika bisnis apa pun — CLI dan TUI memanggil kasus penggunaan yang persis sama.
- 1 modul pengumpulan = 1 sumber = 1 status (`ModuleRun`): tidak pernah dua sumber digabung di bawah satu status yang ambigu.
- Tidak adanya satu kolom bukanlah galat; hanya ketidaktersediaan total sebuah sumber yang memicu `SKIPPED`/`FAILED`.

## 6. Sumber data

| Sumber | Penyedia | Kunci | Mode |
|---|---|:---:|---|
| DNS maju/balik | Resolver sistem | tidak | Aktif ringan |
| RDAP | Bootstrap IANA → RIR/registrar | tidak | Pasif publik |
| Certificate Transparency | `crt.sh` (Sectigo) | tidak | Pasif publik |
| Arsip web | Wayback Machine (Internet Archive) | tidak | Pasif publik |
| BGP / pengumuman jaringan | RIPEstat (RIPE NCC) | tidak | Pasif publik |
| GeoIP | DB-IP Lite (bawaan) atau MaxMind GeoLite2 | tidak / ya | Luring (basis data lokal) |
| NeoTrace | `traceroute`/`tracepath` lokal | tidak | Aktif ringan |
| Reputasi | VirusTotal | ya (gratis) | Dengan kunci |
| Reputasi | Have I Been Pwned | ya (berbayar) | Dengan kunci |

Kuota, lisensi, dan cadangan yang tepat untuk setiap sumber: `docs/DATA_SOURCES.md`. Tidak ada kunci API yang pernah muncul di log, ekspor, atau layar diagnostik.

## 7. Kebijakan keyakinan

Setiap kolom yang dikumpulkan membawa salah satu tingkat berikut (dipakai bersama seluruh rangkaian melalui `omega-lib`):

| Tingkat | Arti |
|---|---|
| `VERIFIED` | Fakta protokol yang diamati langsung, tidak dapat dipalsukan oleh target (mis.: jawaban DNS langsung, pengukuran traceroute lokal). |
| `DECLARED` | Nilai yang diumumkan sendiri oleh sumber dalam kolom yang sepenuhnya ia kendalikan (mis.: data RDAP yang ditampilkan registrar) — masuk akal tetapi dapat dipalsukan sesuka hati. |
| `CORROBORATED` | Nilai `DECLARED` yang dikonfirmasi oleh petunjuk independen (mis.: domain yang terlihat di setidaknya dua log Certificate Transparency yang berbeda). |
| `INFERRED` | Disimpulkan dari pola/heuristik, tanpa pernyataan eksplisit (mis.: ASN bersama yang dipakai untuk menyiratkan relasi, tidak pernah dinaikkan otomatis). |
| `UNKNOWN` | Tidak ada petunjuk yang dapat dipakai, atau disembunyikan secara aktif oleh target. |

Skor keyakinan keseluruhan sebuah pengamatan adalah alat bantu membaca, tidak pernah putusan keamanan.

## 8. Tingkat pengumpulan, otorisasi, dan penyamaran

Setiap profil menjelaskan sifat aksinya secara eksplisit (`CollectionMode`):

- **Luring**: validasi target, pembacaan GeoIP lokal, korelasi pada data yang sudah tersimpan, ekspor — tanpa jaringan.
- **Pasif publik**: RDAP, DNS publik, log CT, arsip, BGP — hanya target yang ditanyai yang dikirim ke pihak ketiga, sifat bawaan protokol.
- **Aktif ringan**: resolusi DNS, reverse DNS, traceroute — resolver yang dikonfigurasi di mesin dan setiap router perantara di jalur melihat permintaan.
- **Dengan kunci pengguna**: penyedia yang mewajibkan kunci atau menerapkan kuota, hanya diaktifkan setelah konfigurasi eksplisit dan pengungkapan yang ditampilkan (kuota, data yang dikirim).

**Pengaman otorisasi**: tidak ada pengamatan yang dimulai pada target yang belum disematkan tanpa konfirmasi eksplisit (`--authorize` di CLI, kotak centang di TUI). Menyematkan target mengotorisasinya secara berkelanjutan untuk pengamatan berikutnya.

**Penyamaran ekspor**: setiap ekspor menerima kebijakan (`none`/`contacts_only`/`sensitive_only`/`strict`) yang menyamarkan kolom sensitif (terutama kontak RDAP) dalam hasil ekspor — sementara penyimpanan lokal selalu menyimpan data lengkap yang dikumpulkan. Detail: `docs/PRIVACY.md`.

## 9. Kompatibilitas terminal

TUI (Textual) mendeteksi kapabilitas terminal secara otomatis (emulator, ukuran) dan menyesuaikan lembar gaya strukturalnya (`complete`/`standard`/`reduced`/`mono`), tanpa flag manual. Mode CLI selalu berupa teks biasa, tidak bergantung pada terminal. Kebijakan ini dipakai bersama seluruh rangkaian `omega-` (`omega-lib`, `terminal/policies.py`).

### Profil menurut emulator yang terdeteksi

| Emulator | Profil awal |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH modern | `reduced` |
| TTY Linux, SSH lama | `mono` |
| Emulator tidak dikenal | `reduced` (cadangan bawaan) |

### Profil menurut ukuran terminal

| Ukuran minimum (kolom × baris) | Batas atas profil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| di bawahnya | `mono` |

Profil akhir yang dipakai adalah **yang lebih ketat di antara keduanya** (emulator dan ukuran). Dapat disegarkan langsung dengan tombol `r`.

## 10. Ekspor

Laporan Markdown dan HTML ditulis dalam bahasa yang dipilih di Pengaturan ("Bahasa ekspor", bawaannya sama dengan antarmuka); JSON, CSV, DOT, dan Mermaid tetap berupa data dan tidak diterjemahkan. Laporan dibuat di `var/exports/` secara bawaan (jalur runtime yang berpatokan pada folder proyek, `$OMEGA_TRACK_VAR_DIR` untuk menggantinya), atau di jalur yang ditentukan (`--output` di CLI, kotak dialog di TUI). Nama berkas unik dengan stempel waktu: `{stempel_waktu}_{target}_{id_pendek}.{ekstensi}`.

| Format | Isi |
|---|---|
| `json` | Struktur lengkap pengamatan (`TrackRun` + findings + relasi), sumber kebenaran, dapat diserialisasi JSON secara ketat |
| `markdown` | Laporan ringkas untuk manusia, dapat dibaca di luar terminal |
| `html` | Laporan web mandiri, 5 tema pilihan (`--theme`), grafik relasi Mermaid tertanam inline |
| `csv` | Satu tabel per kategori finding |
| `dot` | Grafik relasi Graphviz, berkas mandiri |
| `mermaid` | Grafik relasi Mermaid, berkas mandiri |

## 11. Riwayat, pembersihan, dan pengulangan

Setiap pengamatan disimpan (SQLite, `var/db/omega-track.db`): riwayat yang dapat dilihat dan disaring (target/status/tag/periode), dasbor ringkasan (sebaran per status, keandalan per modul, tipologi findings terbaru), pengulangan pengamatan pada target yang sama tanpa mengetik ulang (`track replay`), dan pembersihan riwayat lama dengan pratinjau wajib sebelum penghapusan apa pun (`cleanup preview` sebelum `cleanup run --yes`).

## 12. Pengujian

```bash
source .venv/bin/activate
lint-imports        # memeriksa Dependency Rule
pytest -q           # 485 pengujian
ruff check .
mypy src
```

Struktur: `tests/unit/` (domain dan aplikasi, tanpa I/O nyata), `tests/integration/` (SQLite/berkas nyata, server HTTP tiruan `pytest-httpserver`, TUI tanpa jendela melalui API `Pilot` dari Textual).

## 13. Di luar cakupan

- Riwayat WHOIS/DNS lengkap, passive DNS komersial
- Pencarian orang, jejaring sosial, pastebin/kebocoran
- Pemindaian port, identifikasi layanan dan banner (`omega-check`)
- Pemeriksaan HTTP/HTTPS, header, TLS (`omega-scan`)
- Crawl dan penelusuran arsitektur (`omega-deep`/`omega-fold`)
- Uji beban (`omega-stress`), fuzzing (`omega-fuzz`)
- Peta TUI interaktif (khusus untuk laporan HTML yang diekspor)
- MTR berkelanjutan, multiprobe, dan dari banyak titik pengamatan
- Mode batch/berkala/pemantauan berulang terhadap target — sebuah `TrackRun` selalu tetap menjadi aksi manual yang eksplisit
- Mesin migrasi skema SQLite (skema aditif, praktik yang sama dengan bagian lain rangkaian)

---

> Omega-track — Mengamati, menghubungkan, menilai, melaporkan.
> Identitas digital dengan keyakinan eksplisit pada setiap data, tidak pernah kepastian yang disamarkan.
