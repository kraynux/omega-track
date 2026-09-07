<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licencia MIT (ver archivo LICENSE) -->
<div align="center">
  <img src="docs/assets/omega-track.png" alt="Omega-Track" width="386">
</div>

# 🛰️ OMEGA-TRACK

**Perfilado de identidad digital y observación de ruta de red**

> Desarrollado por **kraynux** para **Omega-server**  
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Página oficial: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; Vista previa: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

**Idiomas:**  
[Français](README.md) · [English](README.en.md) · [Español](README.es.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md)

---

**Omega-track** es una herramienta TUI + CLI que construye, a partir de una IP, IPv6 o dominio, la identidad digital más completa posible: quién responde detrás de ese objetivo, cómo llegar hasta él, y con qué nivel de confianza puede darse por cierta cada información. Es la sexta herramienta de la suite `omega-` (tras `omega-fire`, `omega-stress`, `omega-scan`, `omega-check` y `omega-deep`/`omega-fold`), estructurada según Clean Architecture; consulte `docs/PRODUCT_SCOPE.md` y `docs/DATA_SOURCES.md` para el detalle completo.

## 1. Visión y alcance

Omega-track responde a dos preguntas: «¿quién es este objetivo?» (identidad vía RDAP/DNS/certificados/reputación) y «¿cómo se llega hasta él?» (ruta de red vía NeoTrace, GeoIP, ASN). Complementa `omega-check` (exposición de red), `omega-scan` (higiene HTTP/HTTPS) y `omega-deep` (análisis de arquitectura acotado), sin duplicarlos.

### Qué hace Omega-track

- Acepta un objetivo IP, IPv6 o dominio, registrado y opcionalmente fijado (autorización duradera).
- Centraliza información pública, pasiva o explícitamente activada (RDAP, DNS, Certificate Transparency, archivos Wayback, anuncios BGP).
- Ejecuta un traceroute enriquecido de tipo NeoTrace (la única acción de red activa del núcleo del producto).
- Enriquece cada IP relevante mediante una base GeoIP local (DB-IP Lite sin clave, MaxMind GeoLite2 opcional con clave).
- Consulta, con una clave proporcionada por el usuario, fuentes de reputación (VirusTotal, HIBP), con divulgación sistemática (cuota, datos enviados) antes de cualquier activación.
- Correlaciona los datos observados para formar un perfil coherente, con un nivel de confianza explícito en cada dato.
- Conserva objetivos, ejecuciones, resultados, errores y exportaciones localmente (SQLite, `./var/`).
- Ofrece una TUI Textual y una CLI estrictamente equivalentes funcionalmente.
- Genera informes HTML (5 temas, grafo de relaciones Mermaid incrustado), JSON, Markdown, CSV y grafos DOT y Mermaid independientes.

### Qué no hace Omega-track

| Función | Herramienta responsable |
|---|---|
| Escaneo de puertos, identificación de servicios y banners | OMEGA-CHECK |
| Comprobaciones HTTP/HTTPS, cabeceras, TLS, higiene web | OMEGA-SCAN |
| Rastreo y recorrido de arquitectura, descenso a objetivos relacionados | OMEGA-DEEP |
| Rastreo remoto página a página (enlaces, archivos) | OMEGA-FOLD |
| Pruebas de carga | OMEGA-STRESS |
| Fuzzing y pruebas de robustez de aplicaciones | OMEGA-FUZZ |

A evitar, incluso fuera del MVP: fuerza bruta de subdominios, escaneo de puertos, rastreo web, recolección intrusiva de datos personales, automatización de elusión de protecciones, scraping frágil de plataformas que exigen autenticación, búsqueda de personas/redes sociales/pastebins-leaks, vigilancia periódica/recurrente de un objetivo (ver `docs/PRODUCT_SCOPE.md` §7 "Diferido deliberadamente").

### Advertencia de uso autorizado

Omega-track es una herramienta de investigación de red destinada a un uso legítimo: auditoría de su propia infraestructura, respuesta a incidentes, vigilancia de un ámbito que usted está autorizado a documentar. La recolección sigue siendo casi enteramente pasiva/pública (RDAP, DNS, logs CT — datos ya expuestos públicamente por el objetivo o su registrador), a excepción del traceroute (activo ligero, siempre visible en el perfil utilizado).

**Ninguna observación se inicia sobre un objetivo no fijado sin confirmación explícita** (`--authorize` en la CLI, confirmación en la TUI). Usted es el único responsable de verificar que su uso cumple con las leyes aplicables y las condiciones de uso de las fuentes de terceros consultadas.

## 2. Instalación

### Requisitos previos

- Python 3.10+
- Conexión a Internet, para las dependencias y las fuentes pasivas consultadas
- `traceroute` o `tracepath` instalado (módulo NeoTrace) — se degrada correctamente en su ausencia, el resto de la herramienta funciona con normalidad

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
4. Añade el alias `track` a `~/.bashrc` y `~/.zshrc` (sin duplicados si ya está presente).

### Dependencias

Declaradas en `pyproject.toml` (sin `requirements.txt` separado):
- `omega-lib`: biblioteca compartida de la suite (`ConfidenceLevel`, temas, detección de terminal)
- `textual`: interfaz TUI, temas, adaptación automática al terminal
- `dnspython`: resolución DNS directa e inversa
- `httpx`: sondas RDAP/CT/archivos/BGP/VirusTotal/HIBP
- `maxminddb`: lectura de bases GeoIP locales (DB-IP Lite, MaxMind GeoLite2)
- `jinja2`: plantillas para la exportación HTML
- Dependencias de desarrollo (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Uso

### Modo interactivo (TUI)

Recomendado para el uso diario — se lanza sin argumentos:

```bash
./omega-track.sh
```
si ha creado el alias, escriba simplemente `track` en la terminal:
```bash
track
```

Flujo: pantalla de inicio (se cierra con cualquier tecla o clic) → menú principal (Objetivos / Tracker / Resultados / Historial / Dashboard / GeoIP / Fuentes con clave / Ajustes / Ayuda) → introducción o selección del objetivo (confirmación explícita si no está fijado) y elección de los módulos de recolección → observación (indicador y registro de operaciones de red en vivo, cancelable) → resultados detallados por pestaña (Identidad/DNS/Red-ASN/NeoTrace/Certificados/Archivos/Relaciones/Diagnósticos, exportación) → historial/dashboard/ajustes desde el menú principal. La adaptación al terminal (colores, tamaño, degradación estructural) es automática.

#### Atajos de teclado

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Navegar entre los elementos de una pantalla |
| `Tab` / `Mayús+Tab` | Navegar entre los campos de un formulario |
| `Esc` | Volver a la pantalla anterior (confirmación de salida en el inicio) |
| `t` | Siguiente tema (aplicado de inmediato, sin confirmación) |
| `r` | Actualizar la detección del terminal |
| `a` | Mostrar la ayuda |
| `q` | Salir (con confirmación) |

### Modo scriptable (CLI)

Cualquier subcomando activa el modo CLI:

```bash
# Objetivos
./omega-track.sh target add example.org --alias "sitio vitrina" --tag prod
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

# Fuentes de reputación con clave (divulgación mostrada antes de guardar nada)
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

Cualquier subcomando acepta `--json` para una salida estrictamente legible por máquina.

#### Códigos de salida

| Código | Significado |
|---:|---|
| `0` | Éxito (observación terminada, `COMPLETED`) |
| `1` | Error de validación (objetivo inválido, formato de exportación desconocido, transición de estado inválida, clave API ausente...) |
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

## 4. Módulos de recolección

| Módulo | Modo de recolección | Activo por defecto | Clave requerida |
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

Los cuatro primeros módulos forman el núcleo MVP (`dns`/`reverse_dns`/`rdap`/`neotrace`) y están marcados por defecto en el formulario de lanzamiento; los cinco siguientes son opcionales y deben activarse explícitamente. Una fuente sin clave configurada nunca hace fallar la observación: el módulo correspondiente simplemente pasa a `SKIPPED`. Detalle por fuente, cuotas y licencias: `docs/DATA_SOURCES.md`.

## 5. Arquitectura

Omega-track está estructurado en **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), alineada con la plantilla de la suite `omega-` (ver `omega-check`/`omega-fold`) y verificada por `import-linter` en cada modificación.

```text
src/omega_track/
├── domain/          Lógica de negocio pura (objetivos, TrackRun/ModuleRun, findings, relaciones, perfiles...)
├── application/     Casos de uso (commands/queries/orquestadores de fase/políticas)
├── ports/           Contratos esperados por la aplicación (colectores, repositorios, exportadores...)
├── infrastructure/  Implementaciones concretas (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) y cli/ (scriptable), con paridad funcional estricta
├── app/             Ensamblaje (DependencyContainer, bootstrap, ciclo de vida)
├── core/            Vocabulario transversal (versiones, reexportaciones de omega-lib)
└── plugins/         Módulos opcionales de fuente única (CT, archivos, BGP, VirusTotal, HIBP)
```

Reglas de diseño:
- `domain/` nunca hace red ni E/S; `infrastructure/` hace la red y la E/S, nunca juzga.
- `interfaces/` muestra, no contiene lógica de negocio — CLI y TUI llaman estrictamente a los mismos casos de uso.
- 1 módulo de recolección = 1 fuente = 1 estado (`ModuleRun`): nunca dos fuentes agregadas bajo un único estado ambiguo.
- Un campo aislado ausente nunca es un error; solo la indisponibilidad total de una fuente activa `SKIPPED`/`FAILED`.

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

Cuota, licencia y repliegue exactos por fuente: `docs/DATA_SOURCES.md`. Ninguna clave API aparece nunca en los logs, exportaciones o pantallas de diagnóstico.

## 7. Política de confianza

Cada campo recolectado lleva uno de los siguientes niveles (compartidos por toda la suite vía `omega-lib`):

| Nivel | Significado |
|---|---|
| `VERIFIED` | Hecho protocolar observado directamente, no falsificable por el objetivo (ej.: respuesta DNS directa, medición local de traceroute). |
| `DECLARED` | Valor autodeclarado por la fuente en un campo que controla totalmente (ej.: dato RDAP mostrado por el registrador) — plausible pero falsificable a voluntad. |
| `CORROBORATED` | Un valor `DECLARED` confirmado por un indicio independiente (ej.: un dominio observado por al menos dos logs Certificate Transparency distintos). |
| `INFERRED` | Deducido de un patrón/heurística, sin declaración explícita (ej.: un ASN común usado para sugerir una relación, nunca promovido automáticamente). |
| `UNKNOWN` | Ningún indicio explotable, o ocultado activamente por el objetivo. |

El puntaje de confianza global de una observación es una ayuda de lectura, nunca un veredicto de seguridad.

## 8. Niveles de recolección, autorización y redacción

Cada perfil hace explícita la naturaleza de sus acciones (`CollectionMode`):

- **Offline**: validación de objetivo, lectura GeoIP local, correlaciones sobre datos ya almacenados, exportaciones — sin red.
- **Pasivo público**: RDAP, DNS público, logs CT, archivos, BGP — solo el objetivo consultado se transmite al tercero, propiedad inherente al protocolo.
- **Activo ligero**: resolución DNS, DNS inverso, traceroute — el resolvedor configurado en la máquina y cada router intermedio de la ruta ven la solicitud.
- **Con clave de usuario**: proveedores que exigen una clave o aplican cuotas, activados solo tras configuración explícita y divulgación mostrada (cuota, datos enviados).

**Guardia de autorización**: ninguna observación se inicia sobre un objetivo no fijado sin confirmación explícita (`--authorize` en la CLI, casilla en la TUI). Fijar un objetivo lo autoriza de forma duradera para sus futuras observaciones.

**Redacción de exportaciones**: cada exportación acepta una política (`none`/`contacts_only`/`sensitive_only`/`strict`) que enmascara los campos sensibles (contactos RDAP en particular) en el resultado exportado — el almacenamiento local, por su parte, siempre conserva el dato completo recolectado. Detalle: `docs/PRIVACY.md`.

## 9. Compatibilidad con terminales

La TUI (Textual) detecta automáticamente las capacidades del terminal (emulador, tamaño) y adapta su hoja de estilo estructural en consecuencia (`complete`/`standard`/`reduced`/`mono`), sin bandera manual. El modo CLI permanece siempre en texto plano, independiente del terminal. Política compartida por toda la suite `omega-` (`omega-lib`, `terminal/policies.py`).

### Perfil según el emulador detectado

| Emulador | Perfil inicial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH heredado | `mono` |
| Emulador no reconocido | `reduced` (repliegue por defecto) |

### Perfil según el tamaño del terminal

| Tamaño mínimo (columnas × filas) | Techo de perfil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| por debajo | `mono` |

El perfil final retenido es **el más restrictivo de los dos** (emulador y tamaño). Actualizable en vivo con la tecla `r`.

## 10. Exportaciones

Los informes se generan en `var/exports/` por defecto (ruta de runtime anclada al directorio del proyecto, `$OMEGA_TRACK_VAR_DIR` para sobrescribirla), o en la ruta indicada (`--output` en la CLI, diálogo en la TUI). Nombre de archivo con marca de tiempo y único: `{marca_tiempo}_{objetivo}_{id_corto}.{extensión}`.

| Formato | Contenido |
|---|---|
| `json` | Estructura completa de la observación (`TrackRun` + findings + relaciones), fuente de verdad, estrictamente serializable a JSON |
| `markdown` | Informe humano compacto, legible fuera del terminal |
| `html` | Informe web independiente, 5 temas a elegir (`--theme`), grafo de relaciones Mermaid incrustado |
| `csv` | Una tabla por categoría de finding |
| `dot` | Grafo de relaciones Graphviz, archivo independiente |
| `mermaid` | Grafo de relaciones Mermaid, archivo independiente |

## 11. Historial, purga y repetición

Cada observación se persiste (SQLite, `var/db/omega-track.db`): historial navegable y filtrable (objetivo/estado/etiqueta/período), dashboard de síntesis (desglose por estado, fiabilidad por módulo, tipología de los últimos findings), repetición de una observación sobre el mismo objetivo sin volver a introducir datos (`track replay`), y purga del historial antiguo con vista previa sistemática antes de cualquier eliminación (`cleanup preview` antes de `cleanup run --yes`).

## 12. Pruebas

```bash
source .venv/bin/activate
lint-imports        # verifica la Dependency Rule
pytest -q           # 478 pruebas
ruff check .
mypy src
```

Estructura: `tests/unit/` (dominio y aplicación, sin E/S real), `tests/integration/` (SQLite/archivos reales, servidor HTTP falso `pytest-httpserver`, TUI headless vía la API `Pilot` de Textual).

## 13. Fuera de alcance

- Historial WHOIS/DNS completo, passive DNS comercial
- Búsqueda de personas, redes sociales, pastebins/leaks
- Escaneo de puertos, identificación de servicios y banners (`omega-check`)
- Comprobaciones HTTP/HTTPS, cabeceras, TLS (`omega-scan`)
- Rastreo y recorrido de arquitectura (`omega-deep`/`omega-fold`)
- Pruebas de carga (`omega-stress`), fuzzing (`omega-fuzz`)
- Mapa TUI interactivo (reservado para el informe HTML exportado)
- MTR continuo, multi-sonda y multi-punto de observación
- Modo por lotes/periódico/vigilancia recurrente de un objetivo — un `TrackRun` siempre sigue siendo una acción manual explícita
- Motor de migración de esquema SQLite antes de la v1.0 (esquema aditivo, misma práctica que el resto de la suite)

---

> Omega-track — Observar, correlacionar, calificar, informar.
> Una identidad digital con confianza explícita en cada dato, nunca una certeza disfrazada.
