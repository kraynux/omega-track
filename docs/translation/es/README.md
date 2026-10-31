<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licencia MIT (ver archivo LICENSE) -->
<div align="center">
  <img src="../../assets/omega-track.png" alt="Omega-Track" width="386">
</div>

# 🛰️ OMEGA-TRACK

**Perfilado de identidad digital y observación de ruta de red**

> Desarrollado por [kraynux](https://github.com/kraynux) para [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Página oficial: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; Vista previa: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interfaz e informes exportados disponibles en **17 idiomas** — ver [Idiomas de la interfaz](#idiomas-de-la-interfaz).  
**Idiomas:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track** es una herramienta TUI + CLI que construye, a partir de una IP, una dirección IPv6 o un dominio, la identidad digital más completa posible: quién responde detrás de este objetivo, cómo se llega hasta él y con qué nivel de confianza puede darse por cierta cada información. Es una herramienta de la suite `omega-`, estructurada en Clean Architecture — ver `docs/PRODUCT_SCOPE.md` y `docs/DATA_SOURCES.md` para el detalle completo.

## 1. Visión y alcance

Omega-track responde a dos preguntas: «¿quién es este objetivo?» (identidad RDAP/DNS/certificados/reputación) y «¿cómo se llega hasta él?» (ruta de red NeoTrace, GeoIP, ASN). Complementa a `omega-check` (exposición de red), `omega-scan` (higiene HTTP/HTTPS) y `omega-deep` (análisis de arquitectura acotado), sin duplicarlos.

### Lo que hace Omega-track

- Acepta un objetivo IP, IPv6 o nombre de dominio, registrado y opcionalmente fijado (autorización duradera).
- Centraliza información pública, pasiva o activada explícitamente por el perfil (RDAP, DNS, Certificate Transparency, archivos Wayback, anuncios BGP).
- Ejecuta un traceroute enriquecido de tipo NeoTrace (la única acción de red activa del núcleo del producto).
- Enriquece cada IP relevante mediante una base GeoIP local (DB-IP Lite sin clave, MaxMind GeoLite2 opcional con clave).
- Consulta, con una clave proporcionada por el usuario, fuentes de reputación (VirusTotal, HIBP), con divulgación sistemática (cuota, datos enviados) antes de cualquier activación.
- Relaciona los datos observados para formar un perfil coherente, con un nivel de confianza explícito en cada dato.
- Conserva objetivos, ejecuciones, resultados, errores y exportaciones en local (SQLite, `./var/`).
- Ofrece una TUI Textual y una CLI estrictamente equivalentes en funciones.
- Genera informes HTML (5 temas, grafo de relaciones Mermaid integrado), JSON, Markdown, CSV, y archivos DOT y Mermaid autónomos.

### Lo que Omega-track no hace

| Función | Herramienta responsable |
|---|---|
| Escaneo de puertos, identificación de servicios y banners | OMEGA-CHECK |
| Controles HTTP/HTTPS, cabeceras, TLS, higiene web | OMEGA-SCAN |
| Rastreo, recorrido de arquitectura y descenso a objetivos vinculados | OMEGA-DEEP |
| Rastreo remoto página por página (enlaces, archivos) | OMEGA-FOLD |
| Pruebas de carga | OMEGA-STRESS |
| Fuzzing y pruebas de robustez de aplicaciones | OMEGA-FUZZ |

A evitar, también fuera del MVP: fuerza bruta de subdominios, escaneo de puertos, rastreo web, recopilación intrusiva de datos personales, automatización para eludir protecciones, scraping frágil de plataformas que exigen autenticación, búsqueda de personas/redes sociales/pastebins-filtraciones, vigilancia periódica/recurrente de un objetivo (ver `docs/PRODUCT_SCOPE.md` §7 "Aplazado voluntariamente").

### Aviso de uso autorizado

Omega-track es una herramienta de investigación de red destinada a un uso legítimo: auditoría de su propia infraestructura, respuesta a incidentes, vigilancia de un perímetro que usted está autorizado a documentar. La recopilación sigue siendo casi por completo pasiva/pública (RDAP, DNS, CT logs — datos que el objetivo o su registrador ya exponen públicamente), salvo el traceroute (activo ligero, siempre visible en el perfil utilizado).

**Ninguna observación comienza sobre un objetivo no fijado sin confirmación explícita** (`--authorize` en la CLI, confirmación en la TUI). Usted es el único responsable de verificar que su uso respeta las leyes aplicables y las condiciones de uso de las fuentes de terceros consultadas.

## 2. Instalación

### Requisitos previos

- Python 3.10+
- Conexión a Internet, para las dependencias y las fuentes pasivas consultadas
- `traceroute` o `tracepath` instalado (módulo NeoTrace) — se degrada limpiamente si falta, el resto de la herramienta funciona con normalidad

### Instalación

```bash
[ -d omega-track ] && echo "ℹ️ Ya extraído aquí, paso omitido." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Crea el entorno virtual `.venv` si aún no existe.
2. Instala las dependencias (`pip install -e .`, `pyproject.toml` sigue siendo la única fuente de verdad).
3. Hace ejecutables `omega-track.sh` e `install.sh`.
4. Añade el alias `track` a `~/.bashrc` y `~/.zshrc` (sin duplicado si ya existe).

### Dependencias

Declaradas en `pyproject.toml` (sin `requirements.txt` separado):
- `omega-lib`: biblioteca compartida de la suite (`ConfidenceLevel`, temas, detección de terminal)
- `textual`: interfaz TUI, temas, adaptación automática al terminal
- `dnspython`: resolución DNS directa e inversa
- `httpx`: sondas RDAP/CT/archivos/BGP/VirusTotal/HIBP
- `maxminddb`: lectura de las bases GeoIP locales (DB-IP Lite, MaxMind GeoLite2)
- `jinja2`: plantillas para la exportación HTML
- Dependencias de desarrollo (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Uso

### Modo interactivo (TUI)

Recomendado para el uso diario — se lanza sin argumentos:

```bash
./omega-track.sh
```
si ha creado el alias, escriba simplemente `track` en el terminal:
```bash
track
```

Recorrido: pantalla de inicio (se cierra con una tecla o un clic) → menú principal (Objetivos / Tracker / Resultados / Historial / Panel / GeoIP / Fuentes con clave / Ajustes / Ayuda) → introducción o selección del objetivo (confirmación explícita si no está fijado) y elección de los módulos de recopilación → observación (indicador y desarrollo de las operaciones en directo, cancelable) → resultados detallados por pestaña (Identidad/DNS/Red / ASN/NeoTrace/Certificados/Archivos/Relaciones/Diagnósticos, exportación) → historial/panel/ajustes desde el menú principal. La adaptación al terminal (colores, tamaño, degradación estructural) es automática.

#### Atajos de teclado

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Navegar entre los elementos de una pantalla |
| `Tab` / `Mayús+Tab` | Navegar entre los campos de un formulario |
| `Esc` | Volver a la pantalla anterior (confirmación de salida en la pantalla de inicio) |
| `t` | Tema siguiente (se aplica de inmediato, sin confirmación) |
| `r` | Refrescar la detección del terminal |
| `a` | Mostrar la ayuda |
| `q` | Salir (con confirmación) |

### Idiomas de la interfaz

La interfaz está disponible en 17 idiomas: francés, inglés, español, portugués (Brasil), italiano, alemán, neerlandés, polaco, ruso, chino simplificado, vietnamita, tailandés, indonesio, japonés, coreano, hindi y árabe. La elección se hace en Ajustes («Langue / Language») y se aplica tras reiniciar la interfaz; la variable `OMEGA_TRACK_LANG` (por ejemplo `OMEGA_TRACK_LANG=es ./omega-track.sh`) fuerza un idioma durante una sesión. Lanzado desde omega-suite, omega-track adopta el idioma de la suite. En una consola de texto Linux (TTY), los idiomas con escritura no latina se muestran en inglés durante la sesión. La línea de comandos sigue en francés.

### Modo scriptable (CLI)

Cualquier subcomando activa el modo CLI:

```bash
# Objetivos
./omega-track.sh target add example.org --alias "sitio escaparate" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# Lanzar y seguir una observación
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# Historial
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# Exportación — 6 formatos, 5 temas para el HTML
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# Fuentes de reputación con clave (divulgación mostrada antes de cualquier registro)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <clave_api>

# Ajustes y purga
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# Diagnósticos locales (versiones, capacidades, rutas, estado GeoIP)
./omega-track.sh diagnostics
```

Todo subcomando acepta `--json` para una salida estrictamente legible por máquina.

#### Códigos de salida

| Código | Significado |
|---:|---|
| `0` | Éxito (observación terminada, `COMPLETED`) |
| `1` | Error de validación (objetivo no válido, formato de exportación desconocido, transición de estado no válida, clave API ausente...) |
| `2` | Objetivo no autorizado (ni fijado, ni `--authorize`) |
| `3` | Recurso no encontrado o fuente no disponible (objetivo/ejecución desconocidos, fallo de descarga GeoIP) |
| `4` | Observación parcial (`PARTIAL`) — no es un fallo, solo algunos módulos tuvieron éxito |
| `5` | Error interno inesperado |
| `130` | Interrumpido por el usuario (`Ctrl+C`) |

### Formatos de objetivo aceptados

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 Dominio
```

## 4. Módulos de recopilación

| Módulo | Modo de recopilación | Activo por defecto | Clave requerida |
|---|---|:---:|:---:|
| `dns` | Activo ligero (resolución directa) | sí | no |
| `reverse_dns` | Activo ligero (PTR) | sí | no |
| `rdap` | Pasivo público | sí | no |
| `neotrace` | Activo ligero (traceroute/tracepath) | sí | no |
| `certificate_transparency` | Pasivo público (`crt.sh`) | no | no |
| `archives` | Pasivo público (Wayback Machine) | no | no |
| `bgp` | Pasivo público (RIPEstat) | no | no |
| `virustotal` | Con clave de usuario | no | sí (gratuita) |
| `hibp` | Con clave de usuario | no | sí (**de pago** desde 2022) |

Los cuatro primeros módulos forman la base del MVP (`dns`/`reverse_dns`/`rdap`/`neotrace`) y están marcados por defecto en el formulario de lanzamiento; los cinco siguientes son opcionales y deben activarse explícitamente. Una fuente sin clave configurada nunca hace fallar la observación: el módulo correspondiente pasa simplemente a `SKIPPED` («no ejecutado»). Detalle por fuente, cuotas y licencias: `docs/DATA_SOURCES.md`.

## 5. Arquitectura

Omega-track está estructurado en **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), alineado con la plantilla de la suite `omega-` (ver `omega-check`/`omega-fold`) y verificado por `import-linter` en cada modificación.

```text
src/omega_track/
├── domain/          Lógica de negocio pura (objetivos, TrackRun/ModuleRun, findings, relaciones, perfiles...)
├── application/     Casos de uso (commands/queries/orquestadores de fase/políticas)
├── ports/           Contratos esperados por la aplicación (recolectores, repositorios, exportadores...)
├── infrastructure/  Implementaciones concretas (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) y cli/ (scriptable), con paridad funcional estricta
├── app/             Ensamblaje (DependencyContainer, bootstrap, ciclo de vida)
├── core/            Vocabulario transversal (versiones, reexportaciones de omega-lib)
└── plugins/         Módulos opcionales de fuente única (CT, archivos, BGP, VirusTotal, HIBP)
```

Reglas de diseño:
- `domain/` nunca hace red ni I/O; `infrastructure/` hace la red y la I/O, y nunca juzga.
- `interfaces/` muestra y no contiene ninguna lógica de negocio — CLI y TUI llaman estrictamente a los mismos casos de uso.
- 1 módulo de recopilación = 1 fuente = 1 estado (`ModuleRun`): nunca dos fuentes agregadas bajo un único estado ambiguo.
- La ausencia de un campo aislado nunca es un error; solo la indisponibilidad total de una fuente provoca `SKIPPED`/`FAILED`.

## 6. Fuentes de datos

| Fuente | Proveedor | Clave | Modo |
|---|---|:---:|---|
| DNS directo/inverso | Resolvedor del sistema | no | Activo ligero |
| RDAP | Bootstrap IANA → RIR/registrador | no | Pasivo público |
| Certificate Transparency | `crt.sh` (Sectigo) | no | Pasivo público |
| Archivos web | Wayback Machine (Internet Archive) | no | Pasivo público |
| BGP / anuncios de red | RIPEstat (RIPE NCC) | no | Pasivo público |
| GeoIP | DB-IP Lite (por defecto) o MaxMind GeoLite2 | no / sí | Offline (base local) |
| NeoTrace | `traceroute`/`tracepath` local | no | Activo ligero |
| Reputación | VirusTotal | sí (gratuita) | Con clave |
| Reputación | Have I Been Pwned | sí (de pago) | Con clave |

Cuota, licencia y alternativa exactas para cada fuente: `docs/DATA_SOURCES.md`. Ninguna clave API aparece nunca en los registros, las exportaciones ni las pantallas de diagnóstico.

## 7. Política de confianza

Cada campo recopilado lleva un nivel entre los siguientes (compartido con toda la suite a través de `omega-lib`):

| Nivel | Significado |
|---|---|
| `VERIFIED` | Hecho de protocolo observado directamente, que el objetivo no puede falsificar (p. ej.: respuesta DNS directa, medición traceroute local). |
| `DECLARED` | Valor autodeclarado por la fuente en un campo que controla por completo (p. ej.: dato RDAP mostrado por el registrador) — plausible pero falsificable a voluntad. |
| `CORROBORATED` | Un valor `DECLARED` confirmado por un indicio independiente (p. ej.: un dominio observado en al menos dos logs de Certificate Transparency distintos). |
| `INFERRED` | Deducido de un patrón/heurística, sin declaración explícita (p. ej.: ASN común usado para sugerir una relación, nunca promovido automáticamente). |
| `UNKNOWN` | Ningún indicio aprovechable, o activamente ocultado por el objetivo. |

La puntuación de confianza global de una observación es una ayuda de lectura, nunca un veredicto de seguridad.

## 8. Niveles de recopilación, autorización y redacción

Cada perfil hace explícita la naturaleza de sus acciones (`CollectionMode`):

- **Offline**: validación del objetivo, lectura GeoIP local, correlaciones sobre datos ya almacenados, exportaciones — sin red.
- **Pasivo público**: RDAP, DNS público, CT logs, archivos, BGP — solo se transmite al tercero el objetivo consultado, propiedad inherente al protocolo.
- **Activo ligero**: resolución DNS, DNS inverso, traceroute — el resolvedor configurado en la máquina y cada router intermedio de la ruta ven la petición.
- **Con clave de usuario**: proveedores que exigen una clave o aplican cuotas, activados únicamente tras una configuración explícita y una divulgación mostrada (cuota, datos enviados).

**Control de autorización**: ninguna observación comienza sobre un objetivo no fijado sin confirmación explícita (`--authorize` en la CLI, casilla en la TUI). Fijar un objetivo lo autoriza de forma duradera para sus futuras observaciones.

**Redacción de las exportaciones**: cada exportación acepta una política (`none`/`contacts_only`/`sensitive_only`/`strict`) que oculta los campos sensibles (sobre todo los contactos RDAP) en el resultado exportado — el almacenamiento local, por su parte, conserva siempre el dato completo recopilado. Detalle: `docs/PRIVACY.md`.

## 9. Compatibilidad de terminales

La TUI (Textual) detecta automáticamente las capacidades del terminal (emulador, tamaño) y adapta su hoja de estilo estructural en consecuencia (`complete`/`standard`/`reduced`/`mono`), sin flag manual. El modo CLI sigue siempre en texto simple, independiente del terminal. Política compartida por toda la suite `omega-` (`omega-lib`, `terminal/policies.py`).

### Perfil según el emulador detectado

| Emulador | Perfil inicial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH antiguo | `mono` |
| Emulador no reconocido | `reduced` (alternativa por defecto) |

### Perfil según el tamaño del terminal

| Tamaño mínimo (columnas × líneas) | Techo de perfil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| por debajo | `mono` |

El perfil final retenido es **el más restrictivo de los dos** (emulador y tamaño). Se puede refrescar en directo con la tecla `r`.

## 10. Exportaciones

Los informes Markdown y HTML se escriben en el idioma elegido en Ajustes («Idioma de las exportaciones», por defecto el de la interfaz); JSON, CSV, DOT y Mermaid siguen siendo datos y no se traducen. Los informes se generan en `var/exports/` por defecto (ruta de ejecución anclada a la carpeta del proyecto, `$OMEGA_TRACK_VAR_DIR` para cambiarla), o en la ruta indicada (`--output` en la CLI, cuadro de diálogo en la TUI). Nombre de archivo con marca temporal y único: `{marca_temporal}_{objetivo}_{id_corto}.{extensión}`.

| Formato | Contenido |
|---|---|
| `json` | Estructura completa de la observación (`TrackRun` + findings + relaciones), fuente de verdad, estrictamente serializable en JSON |
| `markdown` | Informe humano compacto, legible fuera del terminal |
| `html` | Informe web autónomo, 5 temas a elegir (`--theme`), grafo de relaciones Mermaid integrado en línea |
| `csv` | Una tabla por categoría de finding |
| `dot` | Grafo de relaciones Graphviz, archivo autónomo |
| `mermaid` | Grafo de relaciones Mermaid, archivo autónomo |

## 11. Historial, purga y repetición

Cada observación se conserva (SQLite, `var/db/omega-track.db`): historial consultable y filtrable (objetivo/estado/etiqueta/periodo), panel de síntesis (reparto por estado, fiabilidad por módulo, tipología de los últimos findings), repetición de una observación sobre el mismo objetivo sin volver a introducirlo (`track replay`), y purga del historial antiguo con vista previa sistemática antes de cualquier borrado (`cleanup preview` antes de `cleanup run --yes`).

## 12. Pruebas

```bash
source .venv/bin/activate
lint-imports        # verifica la Dependency Rule
pytest -q           # 485 pruebas
ruff check .
mypy src
```

Estructura: `tests/unit/` (dominio y aplicación, sin I/O real), `tests/integration/` (SQLite/archivos reales, servidor HTTP ficticio `pytest-httpserver`, TUI headless mediante la API `Pilot` de Textual).

## 13. Fuera de alcance

- Historial WHOIS/DNS completo, passive DNS comercial
- Búsqueda de personas, redes sociales, pastebins/filtraciones
- Escaneo de puertos, identificación de servicios y banners (`omega-check`)
- Controles HTTP/HTTPS, cabeceras, TLS (`omega-scan`)
- Rastreo y recorrido de arquitectura (`omega-deep`/`omega-fold`)
- Pruebas de carga (`omega-stress`), fuzzing (`omega-fuzz`)
- Mapa TUI interactivo (reservado al informe HTML exportado)
- MTR continuo, multisonda y multipunto de observación
- Modo por lotes/periódico/vigilancia recurrente de un objetivo — un `TrackRun` sigue siendo siempre una acción manual explícita
- Motor de migración de esquema SQLite (esquema aditivo, misma práctica que el resto de la suite)

---

> Omega-track — Observar, correlacionar, calificar, informar.
> Una identidad digital con una confianza explícita en cada dato, nunca una certeza disfrazada.
