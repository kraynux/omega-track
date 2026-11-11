<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - رخصة MIT (انظر ملف LICENSE) -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-track.png" alt="Omega-Track" width="512">
</div>

# 🛰️ OMEGA-TRACK

**تنميط الهوية الرقمية ومراقبة مسار الشبكة**

> طوّره [kraynux](https://github.com/kraynux) من أجل [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

الصفحة الرسمية: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; معاينة: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 الواجهة والتقارير المُصدَّرة متاحة بـ **17 لغة** — انظر [لغات الواجهة](#لغات-الواجهة).  
**اللغات:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](README.md)

---

**Omega-track** أداة TUI + CLI تبني، انطلاقًا من عنوان IP أو عنوان IPv6 أو نطاق، أكمل هوية رقمية ممكنة: من يجيب خلف هذا الهدف، وكيف يصل المرء إليه، وبأي مستوى ثقة يمكن اعتبار كل معلومة مؤكدة. إنها إحدى أدوات مجموعة `omega-`، ومبنية وفق Clean Architecture — انظر `docs/PRODUCT_SCOPE.md` و`docs/DATA_SOURCES.md` للتفاصيل الكاملة.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ar/omega-track/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ar/omega-track/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ar/omega-track/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/ar/omega-track/D.png" width="24%" />
</p>

## 1. الرؤية والنطاق

يجيب Omega-track عن سؤالين: «من هو هذا الهدف؟» (الهوية عبر RDAP/DNS/الشهادات/السمعة) و«كيف نصل إليه؟» (مسار الشبكة NeoTrace، GeoIP، ASN). وهو يكمّل `omega-check` (الانكشاف الشبكي) و`omega-scan` (سلامة HTTP/HTTPS) و`omega-deep` (تحليل بنية محدود)، دون أن يكرّرها.

### ما يفعله Omega-track

- يقبل هدفًا على شكل IP أو IPv6 أو اسم نطاق، يُحفظ ويمكن تثبيته اختياريًا (تفويض دائم).
- يجمع معلومات عامة، سلبية أو مفعّلة صراحةً عبر ملف التعريف (RDAP، DNS، Certificate Transparency، أرشيفات Wayback، إعلانات BGP).
- ينفّذ traceroute مُثرى على طريقة NeoTrace (الإجراء الشبكي النشط الوحيد في صميم المنتج).
- يُثري كل عنوان IP ذي صلة بقاعدة بيانات GeoIP محلية (DB-IP Lite دون مفتاح، وMaxMind GeoLite2 اختياريًا مع مفتاح).
- يستعلم، بمفتاح يقدّمه المستخدم، مصادر السمعة (VirusTotal، HIBP)، مع إفصاح منهجي (الحصة، البيانات المُرسلة) قبل أي تفعيل.
- يربط البيانات المرصودة لتكوين ملف متّسق، مع مستوى ثقة صريح لكل معلومة.
- يحفظ الأهداف والتنفيذات والنتائج والأخطاء والتصديرات محليًا (SQLite، `./var/`).
- يوفّر واجهة TUI مبنية على Textual وواجهة CLI متكافئتين وظيفيًا بشكل صارم.
- ينتج تقارير HTML (5 سمات، ورسم علاقات Mermaid مدمج)، وJSON، وMarkdown، وCSV، وملفات DOT وMermaid مستقلة.

### ما لا يفعله Omega-track

| الوظيفة | الأداة المسؤولة |
|---|---|
| فحص المنافذ، وتحديد الخدمات واللافتات | OMEGA-CHECK |
| فحوص HTTP/HTTPS، الترويسات، TLS، سلامة الويب | OMEGA-SCAN |
| الزحف، واجتياز البنية والنزول إلى الأهداف المرتبطة | OMEGA-DEEP |
| الزحف البعيد صفحةً بصفحة (الروابط، الملفات) | OMEGA-FOLD |
| اختبارات التحميل | OMEGA-STRESS |
| الاختبار العشوائي واختبارات متانة التطبيقات | OMEGA-FUZZ |

ما يجب تجنّبه، حتى خارج نطاق MVP: التخمين القسري للنطاقات الفرعية، فحص المنافذ، الزحف على الويب، الجمع المتطفّل للبيانات الشخصية، أتمتة الالتفاف على وسائل الحماية، الكشط الهشّ لمنصات تفرض المصادقة، البحث عن الأشخاص/الشبكات الاجتماعية/تسريبات pastebin، المراقبة الدورية/المتكررة لهدف ما (انظر `docs/PRODUCT_SCOPE.md` §7 "مؤجَّل عن قصد").

### تنبيه بشأن الاستخدام المصرَّح به

Omega-track أداة تحقيق شبكي مخصّصة للاستخدام المشروع: تدقيق بنيتك التحتية الخاصة، والاستجابة للحوادث، ومراقبة نطاق مصرَّح لك بتوثيقه. يبقى الجمع سلبيًا/عامًا بالكامل تقريبًا (RDAP، DNS، سجلات CT — بيانات يكشفها الهدف أو مسجّله علنًا أصلًا)، باستثناء traceroute (نشاط خفيف، ظاهر دائمًا في ملف التعريف المستخدَم).

**لا تبدأ أي مراقبة على هدف غير مثبّت دون تأكيد صريح** (`--authorize` في CLI، والتأكيد في TUI). أنت وحدك المسؤول عن التحقق من أن استخدامك يحترم القوانين المعمول بها وشروط استخدام مصادر الطرف الثالث المستعلَمة.

## 2. التثبيت

### المتطلبات المسبقة

- Python 3.10+
- اتصال بالإنترنت، من أجل التبعيات والمصادر السلبية المستعلَمة
- تثبيت `traceroute` أو `tracepath` (وحدة NeoTrace) — عند غيابه تتراجع الوظيفة بشكل نظيف، ويعمل باقي الأداة بشكل طبيعي

### التثبيت

```bash
[ -d omega-track ] && echo "ℹ️ مستخرج هنا مسبقًا، تم تخطّي الخطوة." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. ينشئ البيئة الافتراضية `.venv` إن لم تكن موجودة بعد.
2. يثبّت التبعيات (`pip install -e .`، ويبقى `pyproject.toml` المصدر الوحيد للحقيقة).
3. يجعل `omega-track.sh` و`install.sh` قابلين للتنفيذ.
4. يضيف الاسم المستعار `track` إلى `~/.bashrc` و`~/.zshrc` (دون تكرار إن كان موجودًا).

### التبعيات

مُعلنة في `pyproject.toml` (دون `requirements.txt` منفصل):
- `omega-lib`: المكتبة المشتركة للمجموعة (`ConfidenceLevel`، السمات، اكتشاف الطرفية)
- `textual`: واجهة TUI، السمات، التكيّف التلقائي مع الطرفية
- `dnspython`: استعلام DNS المباشر والعكسي
- `httpx`: مجسّات RDAP/CT/الأرشيفات/BGP/VirusTotal/HIBP
- `maxminddb`: قراءة قواعد بيانات GeoIP المحلية (DB-IP Lite، MaxMind GeoLite2)
- `jinja2`: القوالب لتصدير HTML
- تبعيات التطوير (`pip install -e ".[dev]"`): `pytest`، `pytest-asyncio`، `pytest-cov`، `pytest-httpserver`، `ruff`، `mypy`، `import-linter`

## 3. الاستخدام

### الوضع التفاعلي (TUI)

يُنصح به للاستخدام اليومي — يُشغَّل دون وسائط:

```bash
./omega-track.sh
```
إذا أنشأت الاسم المستعار، فاكتب ببساطة `track` في الطرفية:
```bash
track
```

المسار: شاشة البداية (تُغلق بضغطة مفتاح أو نقرة) ← القائمة الرئيسية (الأهداف / Tracker / النتائج / السجل / لوحة المعلومات / GeoIP / المصادر ذات المفاتيح / الإعدادات / مساعدة) ← إدخال الهدف أو اختياره (تأكيد صريح إن لم يكن مثبّتًا) واختيار وحدات الجمع ← المراقبة (مؤشر وسير العمليات مباشرة، قابلة للإلغاء) ← نتائج مفصّلة حسب التبويب (الهوية/DNS/الشبكة / ASN/NeoTrace/الشهادات/الأرشيفات/العلاقات/التشخيصات، التصدير) ← السجل/لوحة المعلومات/الإعدادات من القائمة الرئيسية. التكيّف مع الطرفية (الألوان، الحجم، التبسيط البنيوي) تلقائي.

#### اختصارات لوحة المفاتيح

| المفتاح | الإجراء |
|---|---|
| `↑` / `↓` | التنقل بين عناصر الشاشة |
| `Tab` / `Shift+Tab` | التنقل بين حقول النموذج |
| `Esc` | الرجوع إلى الشاشة السابقة (تأكيد الخروج في الشاشة الرئيسية) |
| `t` | السمة التالية (تُطبَّق فورًا، دون تأكيد) |
| `r` | تحديث اكتشاف الطرفية |
| `a` | عرض المساعدة |
| `q` | الخروج (مع تأكيد) |

### لغات الواجهة

الواجهة متاحة بـ 17 لغة: الفرنسية، الإنجليزية، الإسبانية، البرتغالية (البرازيل)، الإيطالية، الألمانية، الهولندية، البولندية، الروسية، الصينية المبسّطة، الفيتنامية، التايلاندية، الإندونيسية، اليابانية، الكورية، الهندية والعربية. يتم الاختيار في الإعدادات («Langue / Language») ويسري بعد إعادة تشغيل الواجهة؛ ويفرض المتغير `OMEGA_TRACK_LANG` (مثلًا `OMEGA_TRACK_LANG=ar ./omega-track.sh`) لغةً لجلسة واحدة. عند تشغيله من omega-suite، يعتمد omega-track لغة المجموعة. على وحدة التحكم النصية في Linux (TTY)، تُعرض اللغات ذات الكتابة غير اللاتينية بالإنجليزية طوال تلك الجلسة. يبقى سطر الأوامر بالفرنسية.

### التواصل والدعم

تتيح المساعدة (المفتاح `a`) شاشة **التواصل والدعم**: *ادفع ثمن قهوة* (صفحة PayPal الخاصة بالمطوّر)، و*التواصل مع الدعم* (عنوان البريد الإلكتروني ونموذج التواصل في الموقع، معروضان بوضوح)، و*تسجيلي كمستخدم (مجهول الهوية)* و*التحقق من التحديثات*. التسجيل اختياري، ومعطّل افتراضيًا، ويُرسل مرة واحدة فقط: يُستخدم فقط لإحصاء المستخدمين، وإن رغبت، قارتهم أو بلدهم (قوائم مغلقة، دون أي نص حر). يُرسل مفتاحًا مولَّدًا عشوائيًا واسم البرنامج (`omega-track`) وإصداره؛ ولا يُرسل أبدًا اسمًا أو اسم جهاز أو إعدادًا أو هدفًا أو نتيجة. لا يُحفظ عنوان IP في التسجيلات، لكنه، كأي زيارة، يمر عبر فحوص الأمان وسجل الخادم المستقبِل. يمكن السحب في أي وقت من الشاشة نفسها (*إلغاء تسجيلي*). يقرأ التحقق من التحديثات قائمة الإصدارات المنشورة على الموقع فقط، ولا يحدث أبدًا دون نقرة.

### الوضع القابل للبرمجة النصية (CLI)

أي أمر فرعي يفعّل وضع CLI:

```bash
# الأهداف
./omega-track.sh target add example.org --alias "موقع تعريفي" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# بدء مراقبة ومتابعتها
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# السجل
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# التصدير — 6 صيغ، و5 سمات لـ HTML
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# مصادر السمعة ذات المفاتيح (يُعرض الإفصاح قبل أي حفظ)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <مفتاح_api>

# الإعدادات والتنظيف
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# التشخيصات المحلية (الإصدارات، القدرات، المسارات، حالة GeoIP)
./omega-track.sh diagnostics
```

يقبل كل أمر فرعي `--json` لمخرجات قابلة للقراءة آليًا بشكل صارم.

#### رموز الخروج

| الرمز | المعنى |
|---:|---|
| `0` | نجاح (انتهت المراقبة، `COMPLETED`) |
| `1` | خطأ تحقق (هدف غير صالح، صيغة تصدير مجهولة، انتقال حالة غير صالح، مفتاح API غائب...) |
| `2` | هدف غير مفوَّض (غير مثبّت ودون `--authorize`) |
| `3` | مورد غير موجود أو مصدر غير متاح (هدف/تنفيذ مجهول، فشل تنزيل GeoIP) |
| `4` | مراقبة جزئية (`PARTIAL`) — ليست فشلًا، نجحت بعض الوحدات فقط |
| `5` | خطأ داخلي غير متوقع |
| `130` | أوقفه المستخدم (`Ctrl+C`) |

### صيغ الأهداف المقبولة

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 نطاق
```

## 4. وحدات الجمع

| الوحدة | نمط الجمع | مفعّلة افتراضيًا | مفتاح مطلوب |
|---|---|:---:|:---:|
| `dns` | نشط خفيف (استعلام مباشر) | نعم | لا |
| `reverse_dns` | نشط خفيف (PTR) | نعم | لا |
| `rdap` | سلبي عام | نعم | لا |
| `neotrace` | نشط خفيف (traceroute/tracepath) | نعم | لا |
| `certificate_transparency` | سلبي عام (`crt.sh`) | لا | لا |
| `archives` | سلبي عام (Wayback Machine) | لا | لا |
| `bgp` | سلبي عام (RIPEstat) | لا | لا |
| `virustotal` | بمفتاح المستخدم | لا | نعم (مجاني) |
| `hibp` | بمفتاح المستخدم | لا | نعم (**مدفوع** منذ 2022) |

تشكّل الوحدات الأربع الأولى أساس MVP (`dns`/`reverse_dns`/`rdap`/`neotrace`) وتكون محدّدة افتراضيًا في نموذج التشغيل؛ أما الخمس التالية فاختيارية ويجب تفعيلها صراحةً. المصدر الذي لم يُضبط له مفتاح لا يُفشل المراقبة أبدًا: تنتقل الوحدة المقابلة ببساطة إلى `SKIPPED` («لم يُنفَّذ»). التفاصيل لكل مصدر، والحصص والتراخيص: `docs/DATA_SOURCES.md`.

## 5. البنية

بُني Omega-track وفق **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins)، متوافقًا مع قالب مجموعة `omega-` (انظر `omega-check`/`omega-fold`)، ويُتحقَّق منه بواسطة `import-linter` عند كل تعديل.

```text
src/omega_track/
├── domain/          منطق أعمال خالص (الأهداف، TrackRun/ModuleRun، findings، العلاقات، ملفات التعريف...)
├── application/     حالات الاستخدام (commands/queries/منسّقو المراحل/السياسات)
├── ports/           العقود التي يتوقعها التطبيق (الجامعات، المستودعات، المصدِّرات...)
├── infrastructure/  تطبيقات فعلية (dnspython/httpx/subprocess/maxminddb، SQLite، jinja2)
├── interfaces/      tui/ (Textual) وcli/ (قابلة للبرمجة النصية)، بتكافؤ وظيفي صارم
├── app/             التجميع (DependencyContainer، الإقلاع، دورة الحياة)
├── core/            مفردات مشتركة (الإصدارات، إعادة تصدير من omega-lib)
└── plugins/         وحدات اختيارية بمصدر واحد (CT، الأرشيفات، BGP، VirusTotal، HIBP)
```

قواعد التصميم:
- لا يقوم `domain/` أبدًا بعمليات شبكة أو I/O؛ يقوم `infrastructure/` بالشبكة والـ I/O، ولا يحكم أبدًا.
- يعرض `interfaces/` ولا يحتوي أي منطق أعمال — تستدعي CLI وTUI حالات الاستخدام نفسها تمامًا.
- وحدة جمع واحدة = مصدر واحد = حالة واحدة (`ModuleRun`): لا يُجمع مصدران أبدًا تحت حالة واحدة ملتبسة.
- غياب حقل منفرد ليس خطأً أبدًا؛ وحده عدم توفر المصدر كليًا يؤدي إلى `SKIPPED`/`FAILED`.

## 6. مصادر البيانات

| المصدر | المزوّد | المفتاح | النمط |
|---|---|:---:|---|
| DNS مباشر/عكسي | محلّل النظام | لا | نشط خفيف |
| RDAP | تمهيد IANA ← RIR/المسجّل | لا | سلبي عام |
| Certificate Transparency | `crt.sh` (Sectigo) | لا | سلبي عام |
| أرشيفات الويب | Wayback Machine (Internet Archive) | لا | سلبي عام |
| BGP / إعلانات الشبكة | RIPEstat (RIPE NCC) | لا | سلبي عام |
| GeoIP | DB-IP Lite (افتراضيًا) أو MaxMind GeoLite2 | لا / نعم | دون اتصال (قاعدة محلية) |
| NeoTrace | `traceroute`/`tracepath` محلي | لا | نشط خفيف |
| السمعة | VirusTotal | نعم (مجاني) | بمفتاح |
| السمعة | Have I Been Pwned | نعم (مدفوع) | بمفتاح |

الحصة والترخيص والبديل الدقيق لكل مصدر: `docs/DATA_SOURCES.md`. لا يظهر أي مفتاح API أبدًا في السجلات أو التصديرات أو شاشات التشخيص.

## 7. سياسة الثقة

يحمل كل حقل مُجمَّع مستوى من المستويات التالية (مشترك مع المجموعة كلها عبر `omega-lib`):

| المستوى | المعنى |
|---|---|
| `VERIFIED` | حقيقة بروتوكولية مرصودة مباشرة، لا يستطيع الهدف تزويرها (مثال: استجابة DNS مباشرة، قياس traceroute محلي). |
| `DECLARED` | قيمة يعلنها المصدر بنفسه في حقل يتحكم فيه كليًا (مثال: بيانات RDAP التي يعرضها المسجّل) — معقولة لكن قابلة للتزوير كما يشاء. |
| `CORROBORATED` | قيمة `DECLARED` مؤكدة بقرينة مستقلة (مثال: نطاق رُصد في سجلّين مختلفين على الأقل من سجلات Certificate Transparency). |
| `INFERRED` | مستنتجة من نمط/استدلال تقريبي، دون إعلان صريح (مثال: ASN مشترك يُستخدم للإيحاء بعلاقة، ولا يُرقّى تلقائيًا أبدًا). |
| `UNKNOWN` | لا توجد قرينة قابلة للاستغلال، أو أخفاها الهدف عمدًا. |

درجة الثقة الإجمالية لمراقبة ما أداة مساعدة على القراءة، وليست حكمًا أمنيًا أبدًا.

## 8. مستويات الجمع والتفويض والحجب

يوضّح كل ملف تعريف طبيعة إجراءاته صراحةً (`CollectionMode`):

- **دون اتصال**: التحقق من الهدف، قراءة GeoIP المحلية، الربط بين بيانات مخزّنة مسبقًا، التصديرات — دون شبكة.
- **سلبي عام**: RDAP، DNS العام، سجلات CT، الأرشيفات، BGP — لا يُرسل إلى الطرف الثالث سوى الهدف المستعلَم عنه، وهي خاصية ملازمة للبروتوكول.
- **نشط خفيف**: استعلام DNS، DNS العكسي، traceroute — يرى الطلبَ المحلّلُ المضبوط على الجهاز وكلُّ موجّه وسيط على المسار.
- **بمفتاح المستخدم**: مزوّدون يشترطون مفتاحًا أو يفرضون حصصًا، لا يُفعَّلون إلا بعد إعداد صريح وإفصاح معروض (الحصة، البيانات المُرسلة).

**حماية التفويض**: لا تبدأ أي مراقبة على هدف غير مثبّت دون تأكيد صريح (`--authorize` في CLI، ومربع اختيار في TUI). تثبيت هدف يفوّضه بشكل دائم لمراقباته المستقبلية.

**حجب التصديرات**: يقبل كل تصدير سياسة (`none`/`contacts_only`/`sensitive_only`/`strict`) تُخفي الحقول الحساسة (ولا سيما جهات اتصال RDAP) في الناتج المُصدَّر — أما التخزين المحلي فيحتفظ دائمًا بالبيانات الكاملة المجمَّعة. التفاصيل: `docs/PRIVACY.md`.

## 9. التوافق مع الطرفيات

تكتشف واجهة TUI (Textual) تلقائيًا قدرات الطرفية (المحاكي، الحجم) وتكيّف ورقة أنماطها البنيوية وفقًا لذلك (`complete`/`standard`/`reduced`/`mono`)، دون علامة يدوية. يبقى وضع CLI نصًا بسيطًا دائمًا، مستقلًا عن الطرفية. وهي سياسة مشتركة بين كل مجموعة `omega-` (`omega-lib`، `terminal/policies.py`).

### ملف التعريف حسب المحاكي المكتشف

| المحاكي | ملف التعريف الأولي |
|---|---|
| Ghostty، Alacritty، WezTerm، Kitty | `complete` |
| Konsole، GNOME Terminal، Terminator، Xfce4 Terminal | `standard` |
| xterm، urxvt، SSH حديث | `reduced` |
| TTY في Linux، SSH قديم | `mono` |
| محاكي غير معروف | `reduced` (البديل الافتراضي) |

### ملف التعريف حسب حجم الطرفية

| الحجم الأدنى (أعمدة × أسطر) | سقف ملف التعريف |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| أقل من ذلك | `mono` |

ملف التعريف النهائي المعتمد هو **الأكثر تقييدًا بين الاثنين** (المحاكي والحجم). ويمكن تحديثه مباشرة بالمفتاح `r`.

## 10. التصديرات

تُكتب تقارير Markdown وHTML باللغة المختارة في الإعدادات («لغة التصدير»، وهي افتراضيًا لغة الواجهة)؛ يبقى JSON وCSV وDOT وMermaid بيانات ولا تُترجم. تُولَّد التقارير افتراضيًا في `var/exports/` (مسار تشغيل مرتبط بمجلد المشروع، ويُغيَّر عبر `$OMEGA_TRACK_VAR_DIR`)، أو في المسار المحدّد (`--output` في CLI، ومربع حوار في TUI). اسم ملف فريد يحمل طابعًا زمنيًا: `{الطابع_الزمني}_{الهدف}_{معرّف_قصير}.{الامتداد}`.

| الصيغة | المحتوى |
|---|---|
| `json` | البنية الكاملة للمراقبة (`TrackRun` + findings + العلاقات)، المصدر المرجعي، قابلة للتسلسل إلى JSON بصرامة |
| `markdown` | تقرير موجز للبشر، مقروء خارج الطرفية |
| `html` | تقرير ويب مستقل، 5 سمات للاختيار (`--theme`)، ورسم علاقات Mermaid مدمج inline |
| `csv` | جدول لكل فئة من فئات findings |
| `dot` | رسم علاقات Graphviz، ملف مستقل |
| `mermaid` | رسم علاقات Mermaid، ملف مستقل |

## 11. السجل والتنظيف وإعادة التشغيل

تُحفظ كل مراقبة (SQLite، `var/db/omega-track.db`): سجل قابل للتصفح والتصفية (الهدف/الحالة/الوسم/الفترة)، ولوحة معلومات موجزة (التوزيع حسب الحالة، موثوقية كل وحدة، أنواع آخر findings)، وإعادة تشغيل مراقبة على الهدف نفسه دون إعادة إدخاله (`track replay`)، وتنظيف السجل القديم مع معاينة منهجية قبل أي حذف (`cleanup preview` قبل `cleanup run --yes`).

## 12. الاختبارات

```bash
source .venv/bin/activate
lint-imports        # يتحقق من Dependency Rule
pytest -q           # 485 اختبارًا
ruff check .
mypy src
```

البنية: `tests/unit/` (المجال والتطبيق، دون I/O حقيقي)، `tests/integration/` (SQLite/ملفات حقيقية، خادم HTTP وهمي `pytest-httpserver`، واجهة TUI دون نافذة عبر واجهة `Pilot` البرمجية في Textual).

## 13. خارج النطاق

- سجل WHOIS/DNS كامل، passive DNS تجاري
- البحث عن الأشخاص، الشبكات الاجتماعية، pastebin/التسريبات
- فحص المنافذ، وتحديد الخدمات واللافتات (`omega-check`)
- فحوص HTTP/HTTPS، الترويسات، TLS (`omega-scan`)
- الزحف واجتياز البنية (`omega-deep`/`omega-fold`)
- اختبارات التحميل (`omega-stress`)، الاختبار العشوائي (`omega-fuzz`)
- خريطة تفاعلية في TUI (محجوزة لتقرير HTML المُصدَّر)
- MTR مستمر، متعدد المجسّات ونقاط الرصد
- وضع الدُفعات/الدوري/المراقبة المتكررة لهدف ما — يبقى `TrackRun` دائمًا إجراءً يدويًا صريحًا
- محرك ترحيل مخطط SQLite (مخطط إضافي، الممارسة نفسها في بقية المجموعة)

---

> Omega-track — رصد، ربط، توصيف، إبلاغ.
> هوية رقمية بثقة صريحة في كل معلومة، لا يقينًا متنكّرًا أبدًا.
