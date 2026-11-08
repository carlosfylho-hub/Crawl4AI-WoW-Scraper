# Scraper WoWhead Midnight

Scraper de dados do WoWhead (expansão Midnight) usando Crawl4AI. O foco atual é
a **pipeline Season 2** (gear com nomes EN/PT-BR, atributos, ícones e qualidade
de craft) e o fluxo **Sem LLM** para as partes 1–5 (ferramentas de profissão,
encantamentos e missivas). Inclui interface Streamlit, CLI, geração de Markdown
e um **servidor MCP** (stdio). Os scrapers LLM antigos foram preservados em
[`legacy/`](legacy/) e não são mais usados pela UI/CLI.

## 🚀 Funcionalidades

- **Extração Assíncrona**: Usa `AsyncWebCrawler` para navegação eficiente
- **Evitação de Detecção**: Configuração `BrowserConfig` com `headless=True` e `enable_stealth=True`
- **Dois modos ativos** (sem chave de API):
  - **Season 2**: parsers canônicos de `wow_season2.py` (gear, EN/PT-BR, craft)
  - **Sem LLM**: partes 1–5 (ferramentas, encantamentos e missivas)
- **Faixas da Season 2 (Midnight)**: Herói `305–321` (Voidforge `328`), Mito `318–334`
  (Voidforge `341`) e Very Rare até `344`; piso/teto configuráveis (`ILVL_MIN`/`ILVL_MAX`,
  padrão `305–350`)
- **Lógica de Variações**: Identifica variações de atributos (Bonus IDs) e gera entradas separadas
- **Schemas JSON**: Estrutura de dados padronizada para cada tipo de item
- **Interface Streamlit**: Filtros por categoria/profissão/slot, miniaturas de ícones, badges
  Hero/Mito/Voidforge e exportação CSV/JSON/Markdown
- **Extração de mídia**: captura `src`/ícones CSS e normaliza para
  `https://wow.zamimg.com/images/wow/icons/large/{icon}.jpg`
- **Geração de Markdown**: Cria banco de dados formatado em Markdown automaticamente

## 🌌 Season 2 (Midnight)

A pipeline principal é [`scraper_season2.py`](scraper_season2.py), apoiada por
[`wow_season2.py`](wow_season2.py) (parsers puros e testáveis).

- **Crawl4AI**: `AsyncWebCrawler` com `js_code` (lazy-load/scroll infinito) e
  `wait_for` explícito (`css:a[href*='item=']`) antes de ler o DOM.
- **Nomes oficiais EN + PT-BR**: cada item é aberto duas vezes
  (`/item=...` e `/pt/item=...`). O campo `nome_en` vem exclusivamente da
  página EN e `nome_ptbr` exclusivamente da página PT-BR — sem tradução
  automática.
- **Atributos localizados**: nomes e valores exatos dos tooltips, com
  `atributos_primarios_ptbr`/`_en` e `atributos_secundarios_ptbr`/`_en`.
  Formatos reais suportados: `+2 Agilidade`, `+ 86 Critical Strike`,
  `Aumenta o seu índice de acerto crítico em + 86` e escolhas como
  `[Agilidade ou Intelecto]`.
- **Variações por Bonus ID**: a chave de unicidade inclui `id + ilvl +
  Bonus IDs + stage`, mantendo cada variação real em uma linha separada.
- **Campos extraídos por item**: `id`, `id_completo`, `nome_en`, `nome_ptbr`,
  `slot`, `slot_fonte_pt/en`, `tipo_armadura`, `qualidade`, `qualidade_craft`,
  `item_level`, `track`, `track_stage`, `voidforged`, atributos PT/EN,
  `efeito_equip_uso`, `icone_url`, `bonus_ids`, `url` e `url_en`.
- **Raridade ≠ qualidade de craft**: `qualidade` é a raridade do item
  (3=Raro, 4=Épico, 5=Lendário). Já `qualidade_craft` é o R1–R5 da fabricação
  (obtido via `?crafting-quality=5` nas páginas de detalhe). No app há dois
  controles separados: **Raridade mínima** (padrão Épico 4) e **Qualidade de
  craft (R)** (padrão R5). Itens craftados da Season 2 usam R5
  independentemente de a raridade ser Épica.
- **API DeepSeek (modos com LLM)**: campo `password` persistido em
  `st.session_state["deepseek_api_key"]` e aplicado via
  `config.configurar_deepseek_api_key()`. A chave é validada (mínimo 20
  caracteres, sem espaços) antes de habilitar a execução com LLM.
- **Markdown final**: [`markdown_season2.py`](markdown_season2.py) gera
  `data/wowhead_season2.md` com ícones (`<img>`), tabelas agrupadas por slot,
  nomes EN/PT-BR, atributos, efeitos, Bonus IDs e links.
- **CLI**:
  ```bash
  python scraper_season2.py --urls https://www.wowhead.com/pt/item=273791 \
    --ilvl-min 305 --ilvl-max 350 --max-itens 10
  ```
- **Saídas**:
  - `data/wowhead_itens_season2.json` / `.md` — gear da Season 2.
  - `data/wowhead_gemas.json`, `data/wowhead_encantamentos.json`,
    `data/wowhead_missivas.json` — catálogos raspados.
  - `data/wowhead_catalogo.json` / `.md` — catálogo consolidado.
- **Recomendações**: aba “💎 Recomendações” no app; usa classe,
  especialidade, prioridade de atributos e o catálogo raspado para indicar
  melhor encantamento/gema, com justificativa e alternativas. Sem catálogo,
  o status é explicitamente “indisponível”.
- **Validação**: `python test_season2.py` (offline) e checagem dos JSONs de
  gemas/encantamentos (tipo, slot-alvo e atributos).

### Flags da CLI (`scraper_season2.py`)

| Flag | Efeito |
| --- | --- |
| `--urls ...` | URLs de listas/guias/itens (padrão: `SEASON2_ITEM_URLS`). |
| `--max-itens N` | Limite de itens retornados. |
| `--max-detalhes N` | Detalha no máximo `N` itens; `None` = todos; `0` = nenhum. |
| `--sem-detalhes` | Não visita páginas individuais (equivale a `--max-detalhes 0`). |
| `--qualidade-craft N` | Rank mínimo de craft (1–5); `0` desativa o filtro. Padrão `5`. |
| `--qualidade-min N` | Raridade mínima (`3`=Raro, `4`=Épico, `5`=Lendário). |
| `--exigir-craft` / `--no-exigir-craft` | Aceita somente itens craftados no rank de `--qualidade-craft` (padrão: ligado). `--no-exigir-craft` mantém itens não craftados. |
| `--incluir-sem-ilvl` | Mantém itens sem item level (gemas/missivas). |
| `--sem-ingles` | Não visita a página EN (perde `nome_en`). |
| `--sem-markdown` | Não gera o `.md` final. |

> **Padrão de entrega:** raridade mínima **4 (Épico)** e somente itens
> **craftados no rank pedido** (`R5`). Isso descarta drops de M+/raid sem
> qualidade de craft. Use `--no-exigir-craft` para incluí-los.

> `--sem-detalhes` e `--max-detalhes 0` têm o mesmo efeito. `--max-detalhes`
> limita o custo (cada item detalhado custa duas visitas: EN + PT-BR).

### Exemplo real de saída JSON

Trecho de `data/wowhead_itens_season2.json` (item craftado R5):

```json
{
  "id": 237834,
  "id_completo": "item=237834&bonus=12846&ilvl=321",
  "nome_ptbr": "Braçadeiras do Quebra-feitiço",
  "nome_en": "",
  "slot": "Pulso",
  "tipo_item": "gear",
  "tipo_armadura": "Placas",
  "qualidade": 4,
  "qualidade_nome": "Épico",
  "qualidade_craft": 5,
  "qualidade_craft_fonte": "url:crafting-quality",
  "profissao_craft": "Ferraria",
  "item_level": 321,
  "track": "Herói",
  "track_stage": "6/6",
  "voidforged": false,
  "url": "https://www.wowhead.com/pt/item=237834?bonus=12846&crafting-quality=5"
}
```

- `qualidade` (raridade) = `4` (Épico) enquanto `qualidade_craft` = `5` (R5).
- `qualidade_craft_fonte` documenta a origem (`url:crafting-quality`).
- `profissao_craft` é necessária para reportar a qualidade de craft.

### Exemplo de tabela Markdown (`data/wowhead_season2.md`)

| Nome (PT-BR) | Qualidade | Craft (R) | ilvl | Profissão Craft |
| --- | --- | --- | --- | --- |
| Braçadeiras do Quebra-feitiço | Épico (Epic) | R5 | 321 | Ferraria |
| Amarras Adulteradas | Épico (Epic) | — | 321 | — |

Itens não craftados exibem `—` na coluna **Craft (R)**.

## 📁 Estrutura do Projeto

```
Crawl4AI/
├── app_streamlit.py        # Interface web (S2 + Sem LLM + Demonstração)
├── scraper_season2.py      # Pipeline Season 2 (EN/PT-BR + ícones + MD)
├── scraper_sem_llm.py      # Fluxo Sem LLM por partes 1–5 (adapter)
├── coleta.py               # Fronteira de rede + parsers do fluxo Sem LLM
├── wow_season2.py          # Parsers puros: ilvl, track, craft, tooltips
├── markdown_season2.py     # Markdown final (tabelas por slot, coluna Craft (R))
├── recomendacoes.py        # Recomendações de gema/encantamento
├── tooltip_client.py       # Cliente de tooltips do Wowhead (+ cache)
├── config.py               # Categorias, URLs e configurações
├── runtime.py              # Workaround de event loop no Windows (Playwright)
├── mcp_server.py           # Servidor MCP (stdio) + --selftest/--print-config
├── iniciar_sistema.py/.bat # Menu interativo
├── run_scraper.py          # Atalho de execução da Season 2
├── test_season2.py         # Testes offline da Season 2
├── tests/                  # Suíte offline (imports, parsers, UI, contrato)
├── data/                   # Saídas canônicas (ver data/README.md)
├── legacy/                 # Scrapers/testes antigos (não usados)
├── docs/                   # Documentação auxiliar
├── requirements.txt
└── README.md
```

## 🛠️ Instalação

1. **Clone o repositório** (ou crie a estrutura de arquivos)

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Instale os navegadores do Playwright**:
   ```bash
   python -m playwright install chromium
   ```

4. **Configure as variáveis de ambiente**:
   - Copie o arquivo `.env.example` para `.env` (se existir)
   - Edite `.env` com sua chave da API DeepSeek:
     ```
     DEEPSEEK_API_KEY=sua_chave_aqui
     ```

5. **Configure as URLs**:
   - Edite `config.py` com as URLs reais de encantamentos e missivas
   - As URLs de ferramentas de profissão já estão configuradas

## 🔄 Modos de Extração

O projeto tem **dois modos ativos**. Os scrapers LLM antigos vivem em
[`legacy/`](legacy/) e não são usados pela UI/CLI.

### 1. Season 2 — gear (Recomendado)
- **Pipeline**: [`scraper_season2.py`](scraper_season2.py)
- **Parsers puros**: [`wow_season2.py`](wow_season2.py)
- Coleta EN + PT-BR, atributos localizados, ícones, `qualidade_craft` e Markdown.
- **Não** requer chave de API.

### 2. Sem LLM (partes 1–5)
- **Pipeline**: [`scraper_sem_llm.py`](scraper_sem_llm.py) sobre
  [`coleta.py`](coleta.py), usando os mesmos parsers canônicos.
- Cobre ferramentas de profissão, encantamentos e missivas por partes.
- **Não** requer chave de API.

> O modo **“Com LLM (legado)”** foi removido da interface. Ele dependia de
> `scraper_completo_final.py`, agora em
> [`legacy/scraper_completo_final.py`](legacy/scraper_completo_final.py).

### Comparação Rápida

| Característica | Season 2 | Sem LLM (partes) |
|----------------|----------|------------------|
| Foco | Gear da Season 2 | Ferramentas/consumíveis |
| Nomes EN/PT-BR | Sim | Parcial |
| `qualidade_craft` | Sim | Não |
| Requer API | Não | Não |

## 🛠️ Instalação

1. **Clone o repositório** (ou crie a estrutura de arquivos)

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Instale os navegadores do Playwright**:
   ```bash
   python -m playwright install chromium
   ```

4. **Variáveis de ambiente** (opcional):
   - Copie `.env.example` para `.env` apenas se precisar de ajustes locais.
   - Os modos ativos (**Season 2** e **Sem LLM**) **não** exigem API key.

5. **Configure as URLs**:
   - Edite `config.py` com as URLs reais de encantamentos e missivas
   - As URLs de ferramentas de profissão já estão configuradas

## 📊 Schemas de Dados

### Ferramentas de Profissão
```json
{
  "id": "string",
  "nome_ptbr": "string",
  "profissao": "string",
  "atributos_secundarios": {"atributo": "valor"},
  "qualidade": 5,
  "item_level": 232,
  "bonus_ids": ["123", "456"],
  "url": "string"
}
```

### Encantamentos
```json
{
  "id": "string",
  "nome_ptbr": "string",
  "atributo_conferido": "string",
  "valor": "string",
  "qualidade": 5,
  "item_level": 250
}
```

### Missivas
```json
{
  "id": "string",
  "nome_ptbr": "string",
  "atributo_adicionado": "string",
  "valor_base": "string",
  "qualidade": 5,
  "item_level": 250
}
```

## 🎯 Uso

### Pipeline Season 2 (CLI)
```bash
python scraper_season2.py --urls https://www.wowhead.com/pt/item=237834 \
  --ilvl-min 305 --ilvl-max 350 --max-itens 10 --max-detalhes 5 \
  --qualidade-craft 5
```

### Fluxo Sem LLM (partes 1–5)
```bash
python scraper_sem_llm.py
```

### Interface web
```bash
python -m streamlit run app_streamlit.py
```

3. **Verifique os resultados**:
   - Saídas canônicas em `./data/` (ver [`data/README.md`](data/README.md))
   - `wowhead_itens_season2.json` / `.md` para gear
   - `wowhead_catalogo.json` / `.md` para o catálogo consolidado

## 🎯 Uso do Aplicativo Streamlit

### Interface Visual
O projeto inclui um aplicativo Streamlit completo com as seguintes funcionalidades:

1. **Dashboard**: Visualização de estatísticas e dados existentes
2. **Execução Controlada**: Interface para configurar e executar o scraping
3. **Exportação**: Geração de JSON, CSV e Markdown

### Como Executar

#### Método 1: Script de Inicialização (Recomendado para Windows)
```bash
# Clique duas vezes no arquivo:
iniciar_sistema.bat
```
Ou execute no terminal:
```cmd
.\iniciar_sistema.bat
```

#### Método 2: Interface Web
```bash
# Instale o Streamlit (já incluído no requirements.txt)
pip install streamlit

# Execute o aplicativo
python -m streamlit run app_streamlit.py
```

#### Método 3: Scraper Direto (Season 2)
```bash
python scraper_season2.py
```

### Funcionalidades da Interface

#### 📊 Dashboard
- Visualização de estatísticas dos dados extraídos
- Tabelas interativas com filtros
- Gráficos de distribuição por profissão e qualidade

#### ⚡ Executar Scraping
- Seleção de partes específicas para extrair
- Configuração de filtros de qualidade
- Controle de modo headless e stealth
- Monitoramento em tempo real do progresso

#### 📁 Resultados e Exportação
- Download de dados em JSON, CSV e Markdown
- Geração automática de banco de dados Markdown
- Visualização prévia dos dados extraídos

### Geração de Banco de Dados Markdown
O aplicativo gera automaticamente um arquivo `database_midnight.md` com:
- Tabelas formatadas para cada parte
- Estatísticas de extração
- Metadados completos dos itens

## 🔌 Servidor MCP

O [`mcp_server.py`](mcp_server.py) expõe as ferramentas de scraping/consulta a
qualquer cliente MCP (VS Code, Claude Desktop, Cursor etc.).

- **Dependência**: `mcp>=1.0.0,<2` (já pinada em `requirements.txt`).
- **Transporte padrão**: `stdio` (`MCP_TRANSPORT=sse` para HTTP/SSE, se suportado).
- **Ferramentas**: `scrape_pagina`, `scrape_wowhead_item`,
  `scrape_wowhead_items`, `listar_catalogo`,
  `recomendar_encantamento_gema`, `estado_dados`.
- **Qualidade de craft**: `scrape_wowhead_item` e `scrape_wowhead_items`
  aceitam `qualidade_craft_min` (default `5`; `0` desativa o filtro). O valor
  efetivo é ecoado em `metadata["qualidade_craft_min"]`.
- **Somente R5/Épico**: `exigir_craft=true` exige item craftado no rank pedido
  (descarta `qualidade_craft=0`); a raridade padrão de gear é **4 (Épico)**.
- **Passo a passo por cliente** (VS Code, Roo/Cline, Claude, Cursor, Windsurf):
  [`docs/MCP_ATIVACAO.md`](docs/MCP_ATIVACAO.md:1).
- **Teste rápido do protocolo stdio**:
  `python tools/testar_mcp_stdio.py --tool estado_dados`.

### Config local (não versionar `.vscode/mcp.json`)

O caminho do interpretador/projeto varia por máquina. Gere o JSON no formato do
seu cliente:

```bash
python mcp_server.py --print-config --formato=roo     # Roo/Cline, Claude, Cursor
python mcp_server.py --print-config --formato=vscode  # VS Code nativo
python mcp_server.py --print-config --formato=bloco   # command/args/cwd/env
```

> O Roo valida o schema e rejeita campos extras como `cwd`; use o formato `roo`.

Saída (exemplo):

```json
{
  "command": "C:\\...\\python.exe",
  "args": ["C:\\...\\Crawl4AI\\mcp_server.py"],
  "cwd": "C:\\...\\Crawl4AI",
  "env": {
    "PYTHONIOENCODING": "utf-8",
    "PYTHONPATH": "C:\\...\\Crawl4AI",
    "MCP_TRANSPORT": "stdio"
  }
}
```

Cole dentro de `mcpServers` no seu cliente:

```json
{
  "mcpServers": {
    "crawl4ai-wow": {
      "command": "<CAMINHO_DO_PYTHON>",
      "args": ["<CAMINHO_ABSOLUTO>/mcp_server.py"],
      "cwd": "<CAMINHO_ABSOLUTO_DO_PROJETO>",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "<CAMINHO_ABSOLUTO_DO_PROJETO>",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Validação rápida:

```bash
python mcp_server.py --selftest
```

## 🪟 Windows: `NotImplementedError` em subprocess

**Sintoma**: ao rodar a extração pelo Streamlit no Windows, o Playwright falha
com `NotImplementedError` ao iniciar o navegador (subprocesso). O mesmo código
funciona no CLI.

**Causa**: o Streamlit/Tornado usa `SelectorEventLoop` no Windows, que **não
suporta subprocessos** — e o Playwright precisa deles.

**Solução**: [`runtime.py`](runtime.py) centraliza o workaround em
`configurar_event_loop_windows()`, que aplica
`WindowsProactorEventLoopPolicy` quando `sys.platform == "win32"`. É chamado em:

- [`app_streamlit.py`](app_streamlit.py) — cria um Proactor loop no worker;
- [`mcp_server.py`](mcp_server.py) — define a policy no processo principal.

Em Linux/macOS a função é um no-op (o comportamento não muda).

## ⚙️ Configuração Avançada

### Variáveis de Ambiente (.env)
```env
# API Keys
DEEPSEEK_API_KEY=sua_chave_aqui

# Crawl4AI Configuration
CRAWL4AI_BROWSER_HEADLESS=true
CRAWL4AI_MAGIC_MODE=true
CRAWL4AI_MAX_CONCURRENT=3

# WoWhead Configuration
WOWHEAD_BASE_URL=https://www.wowhead.com
WOWHEAD_LANGUAGE=pt
WOWHEAD_EXPANSION=midnight

# Quality Filters
QUALITY_RANK=5
RARE_ITEM_LEVEL=232
EPIC_ITEM_LEVEL_MIN=250

# Output Settings
OUTPUT_FORMAT=json
OUTPUT_DIR=./data
```

### URLs (config.py)
```python
# Ferramentas de Profissão (PARTE 3)
PROFESSION_TOOLS_URLS = [
    "https://www.wowhead.com/pt/guide/midnight/professions/mining-overview-trainer-locations-ores-tools#accessories-tools",
    "https://www.wowhead.com/pt/guide/midnight/professions/skinning-overview-trainer-locations-hides-tracking-tools#accessories-tools",
    "https://www.wowhead.com/pt/guide/midnight/professions/tailoring-overview-trainer-locations-recipes-tools#accessories-tools"
]

# Encantamentos (PARTE 4) - Adicionar URLs reais
ENCHANTMENT_URLS = [
    # URLs dos encantamentos
]

# Missivas (PARTE 5) - Adicionar URLs reais
MISSIVE_URLS = [
    # URLs das missivas
]
```

## 🔧 Lógica de Variações

O scraper identifica automaticamente variações de atributos através dos parâmetros de URL:

- **Bonus IDs**: Parâmetros `&bonus=...` na URL
- **Gems IDs**: Parâmetros `&gems=...`
- **Enchant IDs**: Parâmetros `&ench=...`

**Exemplo**: Se um item tem 5 variações de atributos que resultam em 5 IDs diferentes, o script gera 5 entradas separadas no JSON final.

## 🧪 Testes

Todos os testes são **offline** (pytest é opcional; cada arquivo tem runner
próprio com `[OK]/[FAIL]`). Executados pela raiz do projeto:

```bash
python test_season2.py
python tests/test_smoke_offline.py
python tests/test_parser_listagem.py
python tests/test_variante_ilvl.py
python tests/test_max_detalhes.py
python tests/test_sem_llm_adapter.py
python tests/test_imports.py
python tests/test_contrato_crawl4ai.py
python tests/test_craft_parser.py
python tests/test_integracao_filtro_craft.py
python tests/test_catalogo_sem_ilvl.py
python tests/test_app_streamlit.py
```

- `tests/test_app_streamlit.py` usa `streamlit.testing.v1.AppTest` (sem rede).
- Testes e scrapers antigos ficam em [`legacy/`](legacy/)
  (ex.: `python legacy/test_final.py`).

## 📈 Resultados Esperados

- **Ferramentas de Profissão**: 3 categorias (Mineração, Esfolamento, Alfaiataria)
- **Encantamentos**: Lista completa da expansão Midnight
- **Missivas**: Todas as missivas disponíveis
- **Filtros Aplicados**: Apenas itens de qualidade Rank 5 com Item Levels específicos

## 🐛 Solução de Problemas

### Problema: Erro de codificação Unicode no Windows
**Solução**: Configure o encoding do sistema:
```python
import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')
```

### Problema: Navegador não encontrado
**Solução**: Instale os navegadores do Playwright:
```bash
python -m playwright install chromium
```

### Problema: `NotImplementedError` no Windows
**Solução**: use o workaround centralizado em [`runtime.py`](runtime.py), já
aplicado em [`app_streamlit.py`](app_streamlit.py) e
[`mcp_server.py`](mcp_server.py). Veja a seção **Windows** acima.

### Problema: URLs vazias
**Solução**: Adicione as URLs reais no arquivo `config.py`

## 📄 Licença

Este projeto é para fins educacionais e de demonstração. Use com responsabilidade e respeite os termos de serviço do WoWhead.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
1. Reportar issues
2. Sugerir melhorias
3. Enviar pull requests

## 📞 Suporte

Para questões técnicas:
- Verifique a documentação
- Execute os testes de diagnóstico
- Consulte os exemplos fornecidos

---

**Nota**: Este scraper foi desenvolvido seguindo as diretrizes técnicas fornecidas, com foco em robustez, eficiência e qualidade dos dados extraídos.
