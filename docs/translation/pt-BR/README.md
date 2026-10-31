<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licença MIT (ver arquivo LICENSE) -->
<div align="center">
  <img src="../../assets/omega-track.png" alt="Omega-Track" width="386">
</div>

# 🛰️ OMEGA-TRACK

**Perfilamento de identidade digital e observação de rota de rede**

> Desenvolvido por [kraynux](https://github.com/kraynux) para o [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Página oficial: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; Prévia: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface e relatórios exportados disponíveis em **17 idiomas** — veja [Idiomas da interface](#idiomas-da-interface).  
**Idiomas:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track** é uma ferramenta TUI + CLI que constrói, a partir de um IP, um endereço IPv6 ou um domínio, a identidade digital mais completa possível: quem responde por trás deste alvo, como se chega até ele e com que nível de confiança cada informação pode ser tida como certa. É uma ferramenta da suíte `omega-`, estruturada em Clean Architecture — veja `docs/PRODUCT_SCOPE.md` e `docs/DATA_SOURCES.md` para o detalhe completo.

## 1. Visão e escopo

Omega-track responde a duas perguntas: "quem é este alvo?" (identidade RDAP/DNS/certificados/reputação) e "como se chega até ele?" (rota de rede NeoTrace, GeoIP, ASN). Ele complementa o `omega-check` (exposição de rede), o `omega-scan` (higiene HTTP/HTTPS) e o `omega-deep` (análise de arquitetura delimitada), sem duplicá-los.

### O que o Omega-track faz

- Aceita um alvo IP, IPv6 ou nome de domínio, registrado e opcionalmente fixado (autorização duradoura).
- Centraliza informações públicas, passivas ou ativadas explicitamente pelo perfil (RDAP, DNS, Certificate Transparency, arquivos Wayback, anúncios BGP).
- Executa um traceroute enriquecido do tipo NeoTrace (a única ação de rede ativa do núcleo do produto).
- Enriquece cada IP relevante por meio de uma base GeoIP local (DB-IP Lite sem chave, MaxMind GeoLite2 opcional com chave).
- Consulta, com chave fornecida pelo usuário, fontes de reputação (VirusTotal, HIBP), com divulgação sistemática (cota, dados enviados) antes de qualquer ativação.
- Relaciona os dados observados para formar um perfil coerente, com um nível de confiança explícito em cada dado.
- Mantém alvos, execuções, resultados, erros e exportações localmente (SQLite, `./var/`).
- Oferece uma TUI Textual e uma CLI estritamente equivalentes em funcionalidades.
- Gera relatórios HTML (5 temas, grafo de relações Mermaid embutido), JSON, Markdown, CSV, e arquivos DOT e Mermaid autônomos.

### O que o Omega-track não faz

| Função | Ferramenta responsável |
|---|---|
| Varredura de portas, identificação de serviços e banners | OMEGA-CHECK |
| Verificações HTTP/HTTPS, cabeçalhos, TLS, higiene web | OMEGA-SCAN |
| Rastreamento, travessia de arquitetura e descida em alvos vinculados | OMEGA-DEEP |
| Rastreamento remoto página por página (links, arquivos) | OMEGA-FOLD |
| Testes de carga | OMEGA-STRESS |
| Fuzzing e testes de robustez de aplicações | OMEGA-FUZZ |

A evitar, inclusive fora do MVP: força bruta de subdomínios, varredura de portas, rastreamento web, coleta intrusiva de dados pessoais, automação para contornar proteções, scraping frágil de plataformas que exigem autenticação, busca de pessoas/redes sociais/pastebins-vazamentos, monitoramento periódico/recorrente de um alvo (veja `docs/PRODUCT_SCOPE.md` §7 "Adiado voluntariamente").

### Aviso de uso autorizado

Omega-track é uma ferramenta de investigação de rede destinada a uso legítimo: auditoria da sua própria infraestrutura, resposta a incidentes, vigilância de um perímetro que você está autorizado a documentar. A coleta permanece quase inteiramente passiva/pública (RDAP, DNS, CT logs — dados que o alvo ou seu registrador já expõem publicamente), com exceção do traceroute (ativo leve, sempre visível no perfil usado).

**Nenhuma observação começa em um alvo não fixado sem confirmação explícita** (`--authorize` na CLI, confirmação na TUI). Você é o único responsável por verificar se seu uso respeita as leis aplicáveis e os termos de uso das fontes de terceiros consultadas.

## 2. Instalação

### Pré-requisitos

- Python 3.10+
- Conexão com a Internet, para as dependências e as fontes passivas consultadas
- `traceroute` ou `tracepath` instalado (módulo NeoTrace) — degrada de forma limpa se ausente, o resto da ferramenta funciona normalmente

### Instalação

```bash
[ -d omega-track ] && echo "ℹ️ Já extraído aqui, etapa ignorada." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Cria o ambiente virtual `.venv` se ele ainda não existir.
2. Instala as dependências (`pip install -e .`, `pyproject.toml` continua sendo a única fonte de verdade).
3. Torna `omega-track.sh` e `install.sh` executáveis.
4. Adiciona o alias `track` a `~/.bashrc` e `~/.zshrc` (sem duplicar se já existir).

### Dependências

Declaradas em `pyproject.toml` (sem `requirements.txt` separado):
- `omega-lib`: biblioteca compartilhada da suíte (`ConfidenceLevel`, temas, detecção de terminal)
- `textual`: interface TUI, temas, adaptação automática ao terminal
- `dnspython`: resolução DNS direta e reversa
- `httpx`: sondas RDAP/CT/arquivos/BGP/VirusTotal/HIBP
- `maxminddb`: leitura das bases GeoIP locais (DB-IP Lite, MaxMind GeoLite2)
- `jinja2`: templates para a exportação HTML
- Dependências de desenvolvimento (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Uso

### Modo interativo (TUI)

Recomendado para o uso diário — iniciado sem argumentos:

```bash
./omega-track.sh
```
se você criou o alias, basta digitar `track` no terminal:
```bash
track
```

Percurso: tela inicial (fecha com uma tecla ou um clique) → menu principal (Alvos / Tracker / Resultados / Histórico / Painel / GeoIP / Fontes com chave / Configurações / Ajuda) → digitação ou seleção do alvo (confirmação explícita se não estiver fixado) e escolha dos módulos de coleta → observação (indicador e andamento das operações ao vivo, cancelável) → resultados detalhados por aba (Identidade/DNS/Rede / ASN/NeoTrace/Certificados/Arquivos/Relações/Diagnósticos, exportação) → histórico/painel/configurações a partir do menu principal. A adaptação ao terminal (cores, tamanho, degradação estrutural) é automática.

#### Atalhos de teclado

| Tecla | Ação |
|---|---|
| `↑` / `↓` | Navegar entre os elementos de uma tela |
| `Tab` / `Shift+Tab` | Navegar entre os campos de um formulário |
| `Esc` | Voltar à tela anterior (confirmação de saída na tela inicial) |
| `t` | Próximo tema (aplicado imediatamente, sem confirmação) |
| `r` | Atualizar a detecção do terminal |
| `a` | Mostrar a ajuda |
| `q` | Sair (com confirmação) |

### Idiomas da interface

A interface está disponível em 17 idiomas: francês, inglês, espanhol, português (Brasil), italiano, alemão, neerlandês, polonês, russo, chinês simplificado, vietnamita, tailandês, indonésio, japonês, coreano, hindi e árabe. A escolha é feita nas Configurações ("Langue / Language") e se aplica após reiniciar a interface; a variável `OMEGA_TRACK_LANG` (por exemplo `OMEGA_TRACK_LANG=pt_BR ./omega-track.sh`) força um idioma durante uma sessão. Iniciado a partir do omega-suite, o omega-track adota o idioma da suíte. Em um console de texto Linux (TTY), os idiomas de escrita não latina são exibidos em inglês durante a sessão. A linha de comando permanece em francês.

### Modo scriptável (CLI)

Qualquer subcomando aciona o modo CLI:

```bash
# Alvos
./omega-track.sh target add example.org --alias "site institucional" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# Iniciar e acompanhar uma observação
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# Histórico
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# Exportação — 6 formatos, 5 temas para o HTML
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# Fontes de reputação com chave (divulgação exibida antes de qualquer registro)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <chave_api>

# Configurações e limpeza
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# Diagnósticos locais (versões, capacidades, caminhos, estado do GeoIP)
./omega-track.sh diagnostics
```

Todo subcomando aceita `--json` para uma saída estritamente legível por máquina.

#### Códigos de saída

| Código | Significado |
|---:|---|
| `0` | Sucesso (observação concluída, `COMPLETED`) |
| `1` | Erro de validação (alvo inválido, formato de exportação desconhecido, transição de estado inválida, chave de API ausente...) |
| `2` | Alvo não autorizado (nem fixado, nem `--authorize`) |
| `3` | Recurso não encontrado ou fonte indisponível (alvo/execução desconhecidos, falha no download do GeoIP) |
| `4` | Observação parcial (`PARTIAL`) — não é uma falha, só alguns módulos tiveram sucesso |
| `5` | Erro interno inesperado |
| `130` | Interrompido pelo usuário (`Ctrl+C`) |

### Formatos de alvo aceitos

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 Domínio
```

## 4. Módulos de coleta

| Módulo | Modo de coleta | Ativo por padrão | Chave exigida |
|---|---|:---:|:---:|
| `dns` | Ativo leve (resolução direta) | sim | não |
| `reverse_dns` | Ativo leve (PTR) | sim | não |
| `rdap` | Passivo público | sim | não |
| `neotrace` | Ativo leve (traceroute/tracepath) | sim | não |
| `certificate_transparency` | Passivo público (`crt.sh`) | não | não |
| `archives` | Passivo público (Wayback Machine) | não | não |
| `bgp` | Passivo público (RIPEstat) | não | não |
| `virustotal` | Com chave do usuário | não | sim (gratuita) |
| `hibp` | Com chave do usuário | não | sim (**paga** desde 2022) |

Os quatro primeiros módulos formam a base do MVP (`dns`/`reverse_dns`/`rdap`/`neotrace`) e vêm marcados por padrão no formulário de início; os cinco seguintes são opcionais e devem ser ativados explicitamente. Uma fonte sem chave configurada nunca faz a observação falhar: o módulo correspondente simplesmente passa a `SKIPPED` ("não executado"). Detalhe por fonte, cotas e licenças: `docs/DATA_SOURCES.md`.

## 5. Arquitetura

Omega-track é estruturado em **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), alinhado ao modelo da suíte `omega-` (veja `omega-check`/`omega-fold`) e verificado pelo `import-linter` a cada alteração.

```text
src/omega_track/
├── domain/          Lógica de negócio pura (alvos, TrackRun/ModuleRun, findings, relações, perfis...)
├── application/     Casos de uso (commands/queries/orquestradores de fase/políticas)
├── ports/           Contratos esperados pela aplicação (coletores, repositórios, exportadores...)
├── infrastructure/  Implementações concretas (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) e cli/ (scriptável), com paridade funcional estrita
├── app/             Montagem (DependencyContainer, bootstrap, ciclo de vida)
├── core/            Vocabulário transversal (versões, reexportações do omega-lib)
└── plugins/         Módulos opcionais de fonte única (CT, arquivos, BGP, VirusTotal, HIBP)
```

Regras de design:
- `domain/` nunca faz rede nem I/O; `infrastructure/` faz a rede e a I/O, e nunca julga.
- `interfaces/` exibe e não contém nenhuma lógica de negócio — CLI e TUI chamam estritamente os mesmos casos de uso.
- 1 módulo de coleta = 1 fonte = 1 status (`ModuleRun`): nunca duas fontes agregadas sob um único status ambíguo.
- A ausência de um campo isolado nunca é um erro; somente a indisponibilidade total de uma fonte aciona `SKIPPED`/`FAILED`.

## 6. Fontes de dados

| Fonte | Provedor | Chave | Modo |
|---|---|:---:|---|
| DNS direto/reverso | Resolvedor do sistema | não | Ativo leve |
| RDAP | Bootstrap IANA → RIR/registrador | não | Passivo público |
| Certificate Transparency | `crt.sh` (Sectigo) | não | Passivo público |
| Arquivos web | Wayback Machine (Internet Archive) | não | Passivo público |
| BGP / anúncios de rede | RIPEstat (RIPE NCC) | não | Passivo público |
| GeoIP | DB-IP Lite (padrão) ou MaxMind GeoLite2 | não / sim | Offline (base local) |
| NeoTrace | `traceroute`/`tracepath` local | não | Ativo leve |
| Reputação | VirusTotal | sim (gratuita) | Com chave |
| Reputação | Have I Been Pwned | sim (paga) | Com chave |

Cota, licença e alternativa exatas para cada fonte: `docs/DATA_SOURCES.md`. Nenhuma chave de API aparece jamais nos logs, nas exportações ou nas telas de diagnóstico.

## 7. Política de confiança

Cada campo coletado carrega um nível entre os seguintes (compartilhado com toda a suíte via `omega-lib`):

| Nível | Significado |
|---|---|
| `VERIFIED` | Fato de protocolo observado diretamente, que o alvo não pode falsificar (ex.: resposta DNS direta, medição traceroute local). |
| `DECLARED` | Valor autodeclarado pela fonte em um campo que ela controla totalmente (ex.: dado RDAP exibido pelo registrador) — plausível, mas falsificável à vontade. |
| `CORROBORATED` | Um valor `DECLARED` confirmado por um indício independente (ex.: um domínio observado em pelo menos dois logs de Certificate Transparency distintos). |
| `INFERRED` | Deduzido de um padrão/heurística, sem declaração explícita (ex.: ASN comum usado para sugerir uma relação, nunca promovido automaticamente). |
| `UNKNOWN` | Nenhum indício aproveitável, ou ativamente ocultado pelo alvo. |

A pontuação de confiança global de uma observação é uma ajuda de leitura, nunca um veredito de segurança.

## 8. Níveis de coleta, autorização e redação

Cada perfil torna explícita a natureza de suas ações (`CollectionMode`):

- **Offline**: validação do alvo, leitura GeoIP local, correlações sobre dados já armazenados, exportações — sem rede.
- **Passivo público**: RDAP, DNS público, CT logs, arquivos, BGP — somente o alvo consultado é transmitido ao terceiro, propriedade inerente ao protocolo.
- **Ativo leve**: resolução DNS, DNS reverso, traceroute — o resolvedor configurado na máquina e cada roteador intermediário da rota veem a requisição.
- **Com chave do usuário**: provedores que exigem uma chave ou aplicam cotas, ativados somente após configuração explícita e divulgação exibida (cota, dados enviados).

**Proteção de autorização**: nenhuma observação começa em um alvo não fixado sem confirmação explícita (`--authorize` na CLI, caixa de seleção na TUI). Fixar um alvo o autoriza de forma duradoura para suas futuras observações.

**Redação das exportações**: cada exportação aceita uma política (`none`/`contacts_only`/`sensitive_only`/`strict`) que mascara os campos sensíveis (sobretudo os contatos RDAP) no resultado exportado — o armazenamento local, por sua vez, sempre mantém o dado completo coletado. Detalhe: `docs/PRIVACY.md`.

## 9. Compatibilidade de terminais

A TUI (Textual) detecta automaticamente as capacidades do terminal (emulador, tamanho) e adapta sua folha de estilo estrutural de acordo (`complete`/`standard`/`reduced`/`mono`), sem flag manual. O modo CLI permanece sempre em texto simples, independente do terminal. Política compartilhada por toda a suíte `omega-` (`omega-lib`, `terminal/policies.py`).

### Perfil conforme o emulador detectado

| Emulador | Perfil inicial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH legado | `mono` |
| Emulador não reconhecido | `reduced` (alternativa padrão) |

### Perfil conforme o tamanho do terminal

| Tamanho mínimo (colunas × linhas) | Teto de perfil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| abaixo | `mono` |

O perfil final adotado é **o mais restritivo dos dois** (emulador e tamanho). Pode ser atualizado ao vivo com a tecla `r`.

## 10. Exportações

Os relatórios Markdown e HTML são escritos no idioma escolhido nas Configurações ("Idioma das exportações", por padrão o da interface); JSON, CSV, DOT e Mermaid continuam sendo dados e não são traduzidos. Os relatórios são gerados em `var/exports/` por padrão (caminho de execução ancorado na pasta do projeto, `$OMEGA_TRACK_VAR_DIR` para sobrescrevê-lo), ou no caminho indicado (`--output` na CLI, caixa de diálogo na TUI). Nome de arquivo com data e hora e único: `{data_hora}_{alvo}_{id_curto}.{extensão}`.

| Formato | Conteúdo |
|---|---|
| `json` | Estrutura completa da observação (`TrackRun` + findings + relações), fonte de verdade, estritamente serializável em JSON |
| `markdown` | Relatório humano compacto, legível fora do terminal |
| `html` | Relatório web autônomo, 5 temas à escolha (`--theme`), grafo de relações Mermaid embutido inline |
| `csv` | Uma tabela por categoria de finding |
| `dot` | Grafo de relações Graphviz, arquivo autônomo |
| `mermaid` | Grafo de relações Mermaid, arquivo autônomo |

## 11. Histórico, limpeza e repetição

Cada observação é persistida (SQLite, `var/db/omega-track.db`): histórico consultável e filtrável (alvo/status/tag/período), painel de síntese (distribuição por status, confiabilidade por módulo, tipologia dos últimos findings), repetição de uma observação no mesmo alvo sem redigitá-lo (`track replay`), e limpeza do histórico antigo com prévia sistemática antes de qualquer exclusão (`cleanup preview` antes de `cleanup run --yes`).

## 12. Testes

```bash
source .venv/bin/activate
lint-imports        # verifica a Dependency Rule
pytest -q           # 485 testes
ruff check .
mypy src
```

Estrutura: `tests/unit/` (domínio e aplicação, sem I/O real), `tests/integration/` (SQLite/arquivos reais, servidor HTTP fictício `pytest-httpserver`, TUI headless via a API `Pilot` do Textual).

## 13. Fora do escopo

- Histórico WHOIS/DNS completo, passive DNS comercial
- Busca de pessoas, redes sociais, pastebins/vazamentos
- Varredura de portas, identificação de serviços e banners (`omega-check`)
- Verificações HTTP/HTTPS, cabeçalhos, TLS (`omega-scan`)
- Rastreamento e travessia de arquitetura (`omega-deep`/`omega-fold`)
- Testes de carga (`omega-stress`), fuzzing (`omega-fuzz`)
- Mapa TUI interativo (reservado ao relatório HTML exportado)
- MTR contínuo, multissonda e com múltiplos pontos de observação
- Modo em lote/periódico/monitoramento recorrente de um alvo — um `TrackRun` continua sempre sendo uma ação manual explícita
- Motor de migração de esquema SQLite (esquema aditivo, mesma prática que o resto da suíte)

---

> Omega-track — Observar, correlacionar, qualificar, relatar.
> Uma identidade digital com confiança explícita em cada dado, nunca uma certeza disfarçada.
