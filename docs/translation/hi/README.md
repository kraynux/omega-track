<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT लाइसेंस (LICENSE फ़ाइल देखें) -->
<div align="center">
  <img src="../../assets/omega-track.png" alt="Omega-Track" width="386">
</div>

# 🛰️ OMEGA-TRACK

**डिजिटल पहचान की प्रोफ़ाइलिंग और नेटवर्क पथ का अवलोकन**

> [kraynux](https://github.com/kraynux) द्वारा [Omega-Server](https://kraynux.snake-mackarel.ts.net) के लिए विकसित   

आधिकारिक पेज: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; झलक: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 इंटरफ़ेस और एक्सपोर्ट की गई रिपोर्टें **17 भाषाओं** में उपलब्ध हैं — [इंटरफ़ेस की भाषाएँ](#इंटरफ़ेस-की-भाषाएँ) देखें।  
**भाषाएँ:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track** एक TUI + CLI टूल है जो किसी IP, IPv6 पते या डोमेन से यथासंभव पूर्ण डिजिटल पहचान बनाता है: इस लक्ष्य के पीछे कौन उत्तर देता है, वहाँ तक कैसे पहुँचा जाता है, और हर जानकारी को किस स्तर के भरोसे से पक्का माना जा सकता है। यह `omega-` सूट का एक टूल है, जो Clean Architecture में संरचित है — पूरे विवरण के लिए `docs/PRODUCT_SCOPE.md` और `docs/DATA_SOURCES.md` देखें।

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/hi/omega-track/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/hi/omega-track/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/hi/omega-track/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/hi/omega-track/D.png" width="24%" />
</p>

## 1. दृष्टि और दायरा

Omega-track दो प्रश्नों का उत्तर देता है: "यह लक्ष्य कौन है?" (RDAP/DNS/प्रमाणपत्र/प्रतिष्ठा से पहचान) और "वहाँ कैसे पहुँचें?" (NeoTrace नेटवर्क पथ, GeoIP, ASN)। यह `omega-check` (नेटवर्क खुलापन), `omega-scan` (HTTP/HTTPS स्वच्छता) और `omega-deep` (सीमित आर्किटेक्चर विश्लेषण) का पूरक है, उन्हें दोहराए बिना।

### Omega-track क्या करता है

- IP, IPv6 या डोमेन नाम वाला लक्ष्य स्वीकार करता है, जिसे सहेजा जाता है और चाहें तो पिन किया जा सकता है (स्थायी अनुमति)।
- सार्वजनिक जानकारी इकट्ठा करता है, निष्क्रिय या प्रोफ़ाइल द्वारा स्पष्ट रूप से चालू की गई (RDAP, DNS, Certificate Transparency, Wayback संग्रह, BGP घोषणाएँ)।
- NeoTrace शैली का समृद्ध traceroute चलाता है (उत्पाद के मूल में एकमात्र सक्रिय नेटवर्क क्रिया)।
- हर प्रासंगिक IP को स्थानीय GeoIP डेटाबेस से समृद्ध करता है (बिना कुंजी DB-IP Lite, कुंजी के साथ वैकल्पिक MaxMind GeoLite2)।
- उपयोगकर्ता द्वारा दी गई कुंजी से प्रतिष्ठा स्रोतों (VirusTotal, HIBP) से पूछताछ करता है, किसी भी सक्रियण से पहले हमेशा कोटा और भेजे जाने वाले डेटा का खुलासा करता है।
- देखे गए डेटा को जोड़कर एक सुसंगत प्रोफ़ाइल बनाता है, हर डेटा पर स्पष्ट भरोसे के स्तर के साथ।
- लक्ष्य, निष्पादन, परिणाम, त्रुटियाँ और एक्सपोर्ट स्थानीय रूप से रखता है (SQLite, `./var/`)।
- कार्यक्षमता में पूरी तरह समतुल्य Textual TUI और CLI देता है।
- HTML रिपोर्टें (5 थीम, अंतर्निहित Mermaid संबंध ग्राफ़), JSON, Markdown, CSV, और स्वतंत्र DOT तथा Mermaid फ़ाइलें बनाता है।

### Omega-track क्या नहीं करता

| कार्य | ज़िम्मेदार टूल |
|---|---|
| पोर्ट स्कैन, सेवाओं और बैनरों की पहचान | OMEGA-CHECK |
| HTTP/HTTPS जाँच, हेडर, TLS, वेब स्वच्छता | OMEGA-SCAN |
| क्रॉल, आर्किटेक्चर में भ्रमण और जुड़े लक्ष्यों तक उतरना | OMEGA-DEEP |
| पेज-दर-पेज दूरस्थ क्रॉल (लिंक, फ़ाइलें) | OMEGA-FOLD |
| लोड परीक्षण | OMEGA-STRESS |
| फ़ज़िंग और एप्लिकेशन की मज़बूती के परीक्षण | OMEGA-FUZZ |

MVP से बाहर भी बचने योग्य: सबडोमेन का ब्रूट-फ़ोर्स, पोर्ट स्कैन, वेब क्रॉल, व्यक्तिगत डेटा का दख़लअंदाज़ संग्रह, सुरक्षा उपायों को दरकिनार करने का स्वचालन, प्रमाणीकरण माँगने वाले प्लेटफ़ॉर्म की नाज़ुक स्क्रैपिंग, लोगों/सोशल नेटवर्क/pastebin-लीक की खोज, किसी लक्ष्य की आवधिक/बार-बार निगरानी (`docs/PRODUCT_SCOPE.md` §7 "जानबूझकर टाला गया" देखें)।

### अधिकृत उपयोग की चेतावनी

Omega-track वैध उपयोग के लिए एक नेटवर्क जाँच टूल है: अपने स्वयं के इंफ़्रास्ट्रक्चर का ऑडिट, घटना-प्रतिक्रिया, ऐसे दायरे की निगरानी जिसे दर्ज करने का आपको अधिकार है। संग्रह लगभग पूरी तरह निष्क्रिय/सार्वजनिक रहता है (RDAP, DNS, CT लॉग — ऐसा डेटा जिसे लक्ष्य या उसका रजिस्ट्रार पहले से सार्वजनिक करता है), traceroute को छोड़कर (हल्का सक्रिय, उपयोग की गई प्रोफ़ाइल में हमेशा दिखाई देता है)।

**पिन न किए गए लक्ष्य पर स्पष्ट पुष्टि के बिना कोई अवलोकन शुरू नहीं होता** (CLI में `--authorize`, TUI में पुष्टि)। यह जाँचने की ज़िम्मेदारी केवल आपकी है कि आपका उपयोग लागू क़ानूनों और पूछे गए तृतीय-पक्ष स्रोतों की उपयोग शर्तों का पालन करता है।

## 2. इंस्टॉलेशन

### पूर्वापेक्षाएँ

- Python 3.10+
- इंटरनेट कनेक्शन, निर्भरताओं और पूछे जाने वाले निष्क्रिय स्रोतों के लिए
- `traceroute` या `tracepath` इंस्टॉल हो (NeoTrace मॉड्यूल) — न होने पर सुव्यवस्थित ढंग से सुविधा घटती है, टूल का बाक़ी हिस्सा सामान्य रूप से काम करता है

### इंस्टॉलेशन

```bash
[ -d omega-track ] && echo "ℹ️ यहाँ पहले से निकाला जा चुका है, यह चरण छोड़ा गया।" || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. वर्चुअल एनवायरनमेंट `.venv` अभी न हो तो बनाता है।
2. निर्भरताएँ इंस्टॉल करता है (`pip install -e .`, `pyproject.toml` ही सत्य का एकमात्र स्रोत रहता है)।
3. `omega-track.sh` और `install.sh` को निष्पादन योग्य बनाता है।
4. उपनाम `track` को `~/.bashrc` और `~/.zshrc` में जोड़ता है (पहले से हो तो दोहराता नहीं)।

### निर्भरताएँ

`pyproject.toml` में घोषित (अलग `requirements.txt` नहीं):
- `omega-lib`: सूट की साझा लाइब्रेरी (`ConfidenceLevel`, थीम, टर्मिनल पहचान)
- `textual`: TUI इंटरफ़ेस, थीम, टर्मिनल के अनुसार स्वचालित अनुकूलन
- `dnspython`: प्रत्यक्ष और उल्टा DNS रिज़ॉल्यूशन
- `httpx`: RDAP/CT/संग्रह/BGP/VirusTotal/HIBP प्रोब
- `maxminddb`: स्थानीय GeoIP डेटाबेस (DB-IP Lite, MaxMind GeoLite2) पढ़ना
- `jinja2`: HTML एक्सपोर्ट के लिए टेम्पलेट
- विकास निर्भरताएँ (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. उपयोग

### इंटरैक्टिव मोड (TUI)

रोज़मर्रा के उपयोग के लिए अनुशंसित — बिना तर्क के चलाएँ:

```bash
./omega-track.sh
```
अगर आपने उपनाम बनाया है, तो टर्मिनल में बस `track` टाइप करें:
```bash
track
```

प्रवाह: शुरुआती स्क्रीन (कोई कुंजी दबाने या क्लिक करने पर बंद) → मुख्य मेनू (लक्ष्य / Tracker / परिणाम / इतिहास / डैशबोर्ड / GeoIP / कुंजी वाले स्रोत / सेटिंग्स / सहायता) → लक्ष्य दर्ज करना या चुनना (पिन न हो तो स्पष्ट पुष्टि) और संग्रह मॉड्यूल चुनना → अवलोकन (गेज और कार्यों का सजीव क्रम, रद्द करने योग्य) → टैब के अनुसार विस्तृत परिणाम (पहचान/DNS/नेटवर्क / ASN/NeoTrace/प्रमाणपत्र/संग्रह/संबंध/निदान, एक्सपोर्ट) → मुख्य मेनू से इतिहास/डैशबोर्ड/सेटिंग्स। टर्मिनल के अनुसार अनुकूलन (रंग, आकार, संरचनात्मक सरलीकरण) स्वचालित है।

#### कीबोर्ड शॉर्टकट

| कुंजी | क्रिया |
|---|---|
| `↑` / `↓` | स्क्रीन के तत्वों के बीच जाना |
| `Tab` / `Shift+Tab` | फ़ॉर्म के फ़ील्डों के बीच जाना |
| `Esc` | पिछली स्क्रीन पर लौटना (मुख्य स्क्रीन पर बाहर निकलने की पुष्टि) |
| `t` | अगली थीम (तुरंत लागू, बिना पुष्टि) |
| `r` | टर्मिनल पहचान ताज़ा करना |
| `a` | सहायता दिखाना |
| `q` | बाहर निकलना (पुष्टि के साथ) |

### इंटरफ़ेस की भाषाएँ

इंटरफ़ेस 17 भाषाओं में उपलब्ध है: फ़्रेंच, अंग्रेज़ी, स्पेनिश, पुर्तगाली (ब्राज़ील), इतालवी, जर्मन, डच, पोलिश, रूसी, सरलीकृत चीनी, वियतनामी, थाई, इंडोनेशियाई, जापानी, कोरियाई, हिंदी और अरबी। चयन सेटिंग्स ("Langue / Language") में होता है और इंटरफ़ेस दोबारा शुरू करने के बाद लागू होता है; चर `OMEGA_TRACK_LANG` (उदाहरण: `OMEGA_TRACK_LANG=hi ./omega-track.sh`) एक सत्र के लिए भाषा तय करता है। omega-suite से चलाने पर omega-track सूट की भाषा अपनाता है। Linux के टेक्स्ट कंसोल (TTY) पर, गैर-लैटिन लिपि वाली भाषाएँ उस सत्र के दौरान अंग्रेज़ी में दिखती हैं। कमांड लाइन फ़्रेंच में ही रहती है।

### संपर्क और सहायता

सहायता (`a` कुंजी) में **संपर्क और सहायता** स्क्रीन है: *एक कॉफ़ी पिलाएँ* (डेवलपर का PayPal पेज), *सहायता से संपर्क करें* (ईमेल पता और साइट का संपर्क फ़ॉर्म, साफ़ दिखाए गए), *उपयोगकर्ता के रूप में पंजीकरण करें (अनाम)* और *अपडेट जाँचें*। पंजीकरण स्वैच्छिक है, डिफ़ॉल्ट रूप से बंद है और केवल एक बार भेजा जाता है: इसका उपयोग केवल उपयोगकर्ताओं की गिनती के लिए होता है और, यदि आप चाहें, उनके महाद्वीप या देश के लिए (बंद सूचियाँ, कभी मुक्त पाठ नहीं)। यह एक यादृच्छिक रूप से बनी कुंजी, सॉफ़्टवेयर का नाम (`omega-track`) और उसका संस्करण भेजता है; कभी कोई नाम, मशीन का नाम, सेटिंग, लक्ष्य या परिणाम नहीं। IP पता पंजीकरणों में सहेजा नहीं जाता, लेकिन हर विज़िट की तरह यह प्राप्त करने वाले सर्वर की सुरक्षा जाँचों और लॉग से होकर गुज़रता है। उसी स्क्रीन से कभी भी वापस लिया जा सकता है (*अब मेरा पंजीकरण न करें*)। अपडेट जाँच केवल साइट पर प्रकाशित संस्करणों की सूची पढ़ती है, और कभी बिना क्लिक के नहीं।

### स्क्रिप्ट मोड (CLI)

कोई भी उप-कमांड CLI मोड शुरू करता है:

```bash
# लक्ष्य
./omega-track.sh target add example.org --alias "परिचय साइट" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# अवलोकन शुरू करना और उस पर नज़र रखना
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# इतिहास
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# एक्सपोर्ट — 6 प्रारूप, HTML के लिए 5 थीम
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# कुंजी वाले प्रतिष्ठा स्रोत (किसी भी सहेजने से पहले खुलासा दिखाया जाता है)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <api_कुंजी>

# सेटिंग्स और सफ़ाई
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# स्थानीय निदान (संस्करण, क्षमताएँ, पथ, GeoIP स्थिति)
./omega-track.sh diagnostics
```

हर उप-कमांड पूरी तरह मशीन-पठनीय आउटपुट के लिए `--json` स्वीकार करता है।

#### निकास कोड

| कोड | अर्थ |
|---:|---|
| `0` | सफलता (अवलोकन पूरा, `COMPLETED`) |
| `1` | सत्यापन त्रुटि (अमान्य लक्ष्य, अज्ञात एक्सपोर्ट प्रारूप, अमान्य स्थिति परिवर्तन, API कुंजी अनुपस्थित...) |
| `2` | लक्ष्य अधिकृत नहीं (न पिन किया गया, न `--authorize`) |
| `3` | संसाधन नहीं मिला या स्रोत अनुपलब्ध (अज्ञात लक्ष्य/निष्पादन, GeoIP डाउनलोड विफल) |
| `4` | आंशिक अवलोकन (`PARTIAL`) — विफलता नहीं, केवल कुछ मॉड्यूल सफल हुए |
| `5` | अप्रत्याशित आंतरिक त्रुटि |
| `130` | उपयोगकर्ता द्वारा बाधित (`Ctrl+C`) |

### स्वीकृत लक्ष्य प्रारूप

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 डोमेन
```

## 4. संग्रह मॉड्यूल

| मॉड्यूल | संग्रह मोड | डिफ़ॉल्ट रूप से सक्रिय | कुंजी आवश्यक |
|---|---|:---:|:---:|
| `dns` | हल्का सक्रिय (प्रत्यक्ष रिज़ॉल्यूशन) | हाँ | नहीं |
| `reverse_dns` | हल्का सक्रिय (PTR) | हाँ | नहीं |
| `rdap` | सार्वजनिक निष्क्रिय | हाँ | नहीं |
| `neotrace` | हल्का सक्रिय (traceroute/tracepath) | हाँ | नहीं |
| `certificate_transparency` | सार्वजनिक निष्क्रिय (`crt.sh`) | नहीं | नहीं |
| `archives` | सार्वजनिक निष्क्रिय (Wayback Machine) | नहीं | नहीं |
| `bgp` | सार्वजनिक निष्क्रिय (RIPEstat) | नहीं | नहीं |
| `virustotal` | उपयोगकर्ता कुंजी के साथ | नहीं | हाँ (मुफ़्त) |
| `hibp` | उपयोगकर्ता कुंजी के साथ | नहीं | हाँ (2022 से **सशुल्क**) |

पहले चार मॉड्यूल MVP का आधार हैं (`dns`/`reverse_dns`/`rdap`/`neotrace`) और लॉन्च फ़ॉर्म में डिफ़ॉल्ट रूप से चिह्नित होते हैं; अगले पाँच वैकल्पिक हैं और उन्हें स्पष्ट रूप से चालू करना होता है। बिना कॉन्फ़िगर की गई कुंजी वाला स्रोत अवलोकन को कभी विफल नहीं करता: संबंधित मॉड्यूल बस `SKIPPED` ("नहीं चलाया गया") हो जाता है। हर स्रोत का विवरण, कोटा और लाइसेंस: `docs/DATA_SOURCES.md`।

## 5. आर्किटेक्चर

Omega-track **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins) में संरचित है, `omega-` सूट के ढाँचे (`omega-check`/`omega-fold` देखें) के अनुरूप है और हर बदलाव पर `import-linter` से जाँचा जाता है।

```text
src/omega_track/
├── domain/          शुद्ध व्यावसायिक तर्क (लक्ष्य, TrackRun/ModuleRun, findings, संबंध, प्रोफ़ाइल...)
├── application/     उपयोग-मामले (commands/queries/चरण ऑर्केस्ट्रेटर/नीतियाँ)
├── ports/           एप्लिकेशन द्वारा अपेक्षित अनुबंध (कलेक्टर, रिपॉज़िटरी, एक्सपोर्टर...)
├── infrastructure/  ठोस कार्यान्वयन (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) और cli/ (स्क्रिप्ट योग्य), कड़ी कार्यात्मक समानता के साथ
├── app/             संयोजन (DependencyContainer, बूटस्ट्रैप, जीवन-चक्र)
├── core/            साझा शब्दावली (संस्करण, omega-lib से पुनर्निर्यात)
└── plugins/         एकल स्रोत वाले वैकल्पिक मॉड्यूल (CT, संग्रह, BGP, VirusTotal, HIBP)
```

डिज़ाइन नियम:
- `domain/` कभी नेटवर्क या I/O नहीं करता; `infrastructure/` नेटवर्क और I/O करता है, पर कभी निर्णय नहीं देता।
- `interfaces/` केवल दिखाता है, उसमें कोई व्यावसायिक तर्क नहीं — CLI और TUI बिल्कुल वही उपयोग-मामले बुलाते हैं।
- 1 संग्रह मॉड्यूल = 1 स्रोत = 1 स्थिति (`ModuleRun`): दो स्रोतों को कभी एक अस्पष्ट स्थिति के तहत नहीं मिलाया जाता।
- किसी अकेले फ़ील्ड का न होना कभी त्रुटि नहीं; केवल स्रोत की पूर्ण अनुपलब्धता `SKIPPED`/`FAILED` करती है।

## 6. डेटा स्रोत

| स्रोत | प्रदाता | कुंजी | मोड |
|---|---|:---:|---|
| प्रत्यक्ष/उल्टा DNS | सिस्टम रिज़ॉल्वर | नहीं | हल्का सक्रिय |
| RDAP | IANA बूटस्ट्रैप → RIR/रजिस्ट्रार | नहीं | सार्वजनिक निष्क्रिय |
| Certificate Transparency | `crt.sh` (Sectigo) | नहीं | सार्वजनिक निष्क्रिय |
| वेब संग्रह | Wayback Machine (Internet Archive) | नहीं | सार्वजनिक निष्क्रिय |
| BGP / नेटवर्क घोषणाएँ | RIPEstat (RIPE NCC) | नहीं | सार्वजनिक निष्क्रिय |
| GeoIP | DB-IP Lite (डिफ़ॉल्ट) या MaxMind GeoLite2 | नहीं / हाँ | ऑफ़लाइन (स्थानीय डेटाबेस) |
| NeoTrace | स्थानीय `traceroute`/`tracepath` | नहीं | हल्का सक्रिय |
| प्रतिष्ठा | VirusTotal | हाँ (मुफ़्त) | कुंजी के साथ |
| प्रतिष्ठा | Have I Been Pwned | हाँ (सशुल्क) | कुंजी के साथ |

हर स्रोत का सटीक कोटा, लाइसेंस और वैकल्पिक व्यवस्था: `docs/DATA_SOURCES.md`। कोई भी API कुंजी लॉग, एक्सपोर्ट या निदान स्क्रीन में कभी नहीं दिखती।

## 7. भरोसे की नीति

हर एकत्रित फ़ील्ड पर इनमें से एक स्तर होता है (`omega-lib` के माध्यम से पूरे सूट में साझा):

| स्तर | अर्थ |
|---|---|
| `VERIFIED` | सीधे देखा गया प्रोटोकॉल तथ्य, जिसे लक्ष्य नकली नहीं बना सकता (उदा.: सीधा DNS उत्तर, स्थानीय traceroute माप)। |
| `DECLARED` | स्रोत द्वारा स्वयं घोषित मान, ऐसे फ़ील्ड में जिसे वह पूरी तरह नियंत्रित करता है (उदा.: रजिस्ट्रार द्वारा दिखाया गया RDAP डेटा) — विश्वसनीय लगता है पर मनचाहे ढंग से नकली बनाया जा सकता है। |
| `CORROBORATED` | किसी स्वतंत्र संकेत से पुष्ट `DECLARED` मान (उदा.: कम से कम दो अलग-अलग Certificate Transparency लॉग में देखा गया डोमेन)। |
| `INFERRED` | किसी पैटर्न/अनुमान-पद्धति से निकाला गया, बिना स्पष्ट घोषणा के (उदा.: संबंध का संकेत देने के लिए साझा ASN, कभी स्वचालित रूप से ऊपर नहीं किया जाता)। |
| `UNKNOWN` | कोई उपयोगी संकेत नहीं, या लक्ष्य द्वारा सक्रिय रूप से छिपाया गया। |

किसी अवलोकन का समग्र भरोसा स्कोर पढ़ने में सहायता है, कभी सुरक्षा निर्णय नहीं।

## 8. संग्रह स्तर, अनुमति और छिपाव

हर प्रोफ़ाइल अपनी क्रियाओं की प्रकृति स्पष्ट करती है (`CollectionMode`):

- **ऑफ़लाइन**: लक्ष्य का सत्यापन, स्थानीय GeoIP पढ़ना, पहले से सहेजे गए डेटा पर सहसंबंध, एक्सपोर्ट — कोई नेटवर्क नहीं।
- **सार्वजनिक निष्क्रिय**: RDAP, सार्वजनिक DNS, CT लॉग, संग्रह, BGP — तृतीय पक्ष को केवल पूछा गया लक्ष्य भेजा जाता है, जो प्रोटोकॉल का अंतर्निहित गुण है।
- **हल्का सक्रिय**: DNS रिज़ॉल्यूशन, उल्टा DNS, traceroute — मशीन पर कॉन्फ़िगर किया गया रिज़ॉल्वर और पथ का हर मध्यवर्ती राउटर अनुरोध देखता है।
- **उपयोगकर्ता कुंजी के साथ**: कुंजी माँगने वाले या कोटा लगाने वाले प्रदाता, जो केवल स्पष्ट कॉन्फ़िगरेशन और दिखाए गए खुलासे (कोटा, भेजा गया डेटा) के बाद चालू होते हैं।

**अनुमति सुरक्षा**: पिन न किए गए लक्ष्य पर स्पष्ट पुष्टि के बिना कोई अवलोकन शुरू नहीं होता (CLI में `--authorize`, TUI में चेकबॉक्स)। किसी लक्ष्य को पिन करने से उसके भविष्य के अवलोकनों के लिए स्थायी अनुमति मिल जाती है।

**एक्सपोर्ट में छिपाव**: हर एक्सपोर्ट एक नीति (`none`/`contacts_only`/`sensitive_only`/`strict`) स्वीकार करता है जो एक्सपोर्ट किए गए परिणाम में संवेदनशील फ़ील्ड (विशेष रूप से RDAP संपर्क) छिपाती है — जबकि स्थानीय भंडार हमेशा पूरा एकत्रित डेटा रखता है। विवरण: `docs/PRIVACY.md`।

## 9. टर्मिनल संगतता

TUI (Textual) टर्मिनल की क्षमताएँ (एमुलेटर, आकार) स्वचालित रूप से पहचानता है और उसी अनुसार अपनी संरचनात्मक स्टाइलशीट (`complete`/`standard`/`reduced`/`mono`) समायोजित करता है, बिना किसी मैन्युअल फ़्लैग के। CLI मोड हमेशा सादा टेक्स्ट रहता है, टर्मिनल से स्वतंत्र। यह नीति पूरे `omega-` सूट में साझा है (`omega-lib`, `terminal/policies.py`)।

### पहचाने गए एमुलेटर के अनुसार प्रोफ़ाइल

| एमुलेटर | प्रारंभिक प्रोफ़ाइल |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, आधुनिक SSH | `reduced` |
| Linux TTY, पुराना SSH | `mono` |
| अपरिचित एमुलेटर | `reduced` (डिफ़ॉल्ट विकल्प) |

### टर्मिनल के आकार के अनुसार प्रोफ़ाइल

| न्यूनतम आकार (स्तंभ × पंक्तियाँ) | प्रोफ़ाइल की सीमा |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| इससे कम | `mono` |

अंतिम रूप से अपनाई गई प्रोफ़ाइल **दोनों में से अधिक सख़्त** होती है (एमुलेटर और आकार)। इसे `r` कुंजी से सजीव रूप में ताज़ा किया जा सकता है।

## 10. एक्सपोर्ट

Markdown और HTML रिपोर्टें सेटिंग्स में चुनी गई भाषा में लिखी जाती हैं ("एक्सपोर्ट की भाषा", डिफ़ॉल्ट रूप से इंटरफ़ेस वाली); JSON, CSV, DOT और Mermaid डेटा ही रहते हैं और अनुवादित नहीं होते। रिपोर्टें डिफ़ॉल्ट रूप से `var/exports/` में बनती हैं (प्रोजेक्ट फ़ोल्डर पर आधारित रनटाइम पथ, बदलने के लिए `$OMEGA_TRACK_VAR_DIR`), या बताए गए पथ पर (CLI में `--output`, TUI में संवाद बॉक्स)। समय-मुहर वाला अद्वितीय फ़ाइल नाम: `{समय_मुहर}_{लक्ष्य}_{छोटा_id}.{एक्सटेंशन}`।

| प्रारूप | सामग्री |
|---|---|
| `json` | अवलोकन की पूरी संरचना (`TrackRun` + findings + संबंध), सत्य का स्रोत, पूरी तरह JSON में क्रमबद्ध करने योग्य |
| `markdown` | मनुष्यों के लिए संक्षिप्त रिपोर्ट, टर्मिनल के बाहर पढ़ने योग्य |
| `html` | स्वतंत्र वेब रिपोर्ट, 5 थीम में से चुनें (`--theme`), Mermaid संबंध ग्राफ़ इनलाइन अंतर्निहित |
| `csv` | हर finding श्रेणी के लिए एक तालिका |
| `dot` | Graphviz संबंध ग्राफ़, स्वतंत्र फ़ाइल |
| `mermaid` | Mermaid संबंध ग्राफ़, स्वतंत्र फ़ाइल |

## 11. इतिहास, सफ़ाई और दोबारा चलाना

हर अवलोकन सहेजा जाता है (SQLite, `var/db/omega-track.db`): देखने और छानने योग्य इतिहास (लक्ष्य/स्थिति/टैग/अवधि), सारांश डैशबोर्ड (स्थिति के अनुसार वितरण, हर मॉड्यूल की विश्वसनीयता, हाल के findings के प्रकार), उसी लक्ष्य पर बिना दोबारा दर्ज किए अवलोकन दोबारा चलाना (`track replay`), और किसी भी हटाने से पहले अनिवार्य पूर्वावलोकन के साथ पुराने इतिहास की सफ़ाई (`cleanup run --yes` से पहले `cleanup preview`)।

## 12. परीक्षण

```bash
source .venv/bin/activate
lint-imports        # Dependency Rule की जाँच करता है
pytest -q           # 485 परीक्षण
ruff check .
mypy src
```

संरचना: `tests/unit/` (डोमेन और एप्लिकेशन, बिना वास्तविक I/O), `tests/integration/` (वास्तविक SQLite/फ़ाइलें, नकली HTTP सर्वर `pytest-httpserver`, Textual के `Pilot` API से बिना विंडो वाला TUI)।

## 13. दायरे से बाहर

- पूरा WHOIS/DNS इतिहास, व्यावसायिक passive DNS
- लोगों, सोशल नेटवर्क, pastebin/लीक की खोज
- पोर्ट स्कैन, सेवाओं और बैनरों की पहचान (`omega-check`)
- HTTP/HTTPS जाँच, हेडर, TLS (`omega-scan`)
- क्रॉल और आर्किटेक्चर में भ्रमण (`omega-deep`/`omega-fold`)
- लोड परीक्षण (`omega-stress`), फ़ज़िंग (`omega-fuzz`)
- इंटरैक्टिव TUI मानचित्र (एक्सपोर्ट की गई HTML रिपोर्ट के लिए आरक्षित)
- सतत, बहु-प्रोब और बहु-अवलोकन-बिंदु MTR
- किसी लक्ष्य का बैच/आवधिक मोड या बार-बार निगरानी — `TrackRun` हमेशा एक स्पष्ट मैन्युअल क्रिया रहता है
- SQLite स्कीमा माइग्रेशन इंजन (जोड़ने वाला स्कीमा, सूट के बाक़ी हिस्से जैसी ही पद्धति)

---

> Omega-track — देखें, जोड़ें, आँकें, रिपोर्ट करें।
> हर डेटा पर स्पष्ट भरोसे वाली डिजिटल पहचान, कभी छिपी हुई निश्चितता नहीं।
