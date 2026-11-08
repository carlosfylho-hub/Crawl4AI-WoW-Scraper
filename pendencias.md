# Pendências — Scraper Wowhead Season 2 (Crawl4AI + Streamlit)

> Documento criado em **2026-11-06**. Consolida o que **já foi concluído**, o que
> **ainda falta** e como validar cada item. Não substitui os testes
> (`test_season2.py`), apenas organiza o trabalho restante.

## Legenda

- `[ ]` pendente
- `[-]` em andamento / parcial
- `[x]` concluído e validado

---

## 1. Concluído recentemente (base para o restante)

- `[x]` Filtro de URL corrigido para `min-ilvl` / `max-ilvl` (item level), com
  normalização de URLs antigas `min-level` / `max-level` (nível de personagem).
- `[x]` Diagnóstico de descartes no resultado (`ilvl_fora`, `sem_ilvl`,
  `qualidade`, `slot`, `profissao`, `tipo`, `qualidade_craft`) e avisos na UI.
- `[x]` **Raridade** separada da **qualidade de craft**:
  - Raridade = `qualidade` (3=Raro, 4=Épico, 5=Lendário), padrão **4**.
  - Qualidade de craft = `qualidade_craft` (R1–R5), padrão **5**, lida de
    `?crafting-quality=5` na URL de detalhe e com fallback de tooltip.
- `[x]` Sidebar com dois controles independentes:
  - “Raridade mínima” (padrão Épico 4)
  - “Qualidade de craft (R)” (padrão R5)
- `[x]` Propagação de `qualidade_craft_min` no `CFG` e no construtor do scraper.
- `[x]` Coluna **“Craft (R)”** em tabela Streamlit, CSV e Markdown (23 colunas).
- `[x]` Testes offline adicionados para `extrair_qualidade_craft` e URL
  `crafting-quality=5` (raridade continua 4, craft vira 5).
- `[x]` README atualizado com a distinção raridade × qualidade de craft.

### Validações já executadas com sucesso

- `python -m py_compile app_streamlit.py wow_season2.py scraper_season2.py markdown_season2.py test_season2.py`
- `python test_season2.py` → **12 grupos OK**, incluindo
  “Qualidade de craft (R5) separada da raridade”.
- `AppTest` do Streamlit → **0 exceções**, 4 abas, selectboxes
  `Raridade mínima = 4` e `Qualidade de craft (R) = 5`.
- Construtor de URL:
  - gear → `.../item=1?ilvl=341&crafting-quality=5`
  - gema → `.../item=2` (sem `crafting-quality`)
  - `qualidade_craft_min=0` → sem o parâmetro.

---

## 2. Pendências prioritárias (P0 — antes da próxima entrega)

- `[x]` **Validar ao vivo um item craftado real** — **Concluído (Pacote 4)**. Evidência: `qualidade=4`, `qualidade_craft=5`, `qualidade_craft_fonte="url:crafting-quality"`, `profissao_craft="Ferraria"` para os ids 237831 e 237839, via [`tools/validar_craft.py`](tools/validar_craft.py:1) → 2/2 ok; relatório em [`data/_diagnostico/craft.json`](data/_diagnostico/craft.json:1). Parser em [`wow_season2.py:1505`](wow_season2.py:1505) e profissão em [`wow_season2.py:1360`](wow_season2.py:1360).
  - Executar a extração de 1–2 itens craftados pelo app ou CLI.
  - Confirmar no JSON:
    - `qualidade` = 4 (Épico) e `qualidade_craft` = 5;
    - `qualidade_craft_fonte` = `url:crafting-quality`;
    - `profissao_craft` preenchida (ex.: Ferraria, Alfaiataria, Couraria).
  - Se `profissao_craft` vier vazia, `qualidade_craft` será 0 por design
    (`wow_season2.py:1619`). Nesse caso, investigar
    `_profissao_craft_da_pagina()` (`wow_season2.py:1104`).

- `[x]` **Re-raspar os arquivos em `data/`** — **Concluído (Pacote 4)**. Evidência: [`data/wowhead_itens_season2.json`](data/wowhead_itens_season2.json:1) regenerado com 24 itens, 100% `item_level=321` dentro da faixa 305–350; [`data/wowhead_season2.md`](data/wowhead_season2.md:1) com 24 linhas e cabeçalho `Craft (R)`.
  - `data/wowhead_itens_season2.json` e `.md` foram gerados antes do campo
    `qualidade_craft`; precisam ser regenerados para conter “Craft (R)”.
  - Conferir no Markdown final: cabeçalho com `| Craft (R) |` e linhas com
    `R5` (ou `—` para itens não craftados).

- `[x]` **Conferir exportações reais** — **Concluído (Pacote 4)**. Evidência: CSV em [`app_streamlit.py:303`](app_streamlit.py:303) inclui `qualidade_craft`, `qualidade_craft_fonte`, `profissao_craft`, `profissao_craft_fonte`, `motivo_qualidade_craft`, `craft_indicio`; tabela `Craft (R)` em [`app_streamlit.py:180`](app_streamlit.py:180); cards "Craft R5" em [`app_streamlit.py:228`](app_streamlit.py:228).
  - CSV: colunas `qualidade_craft` e `qualidade_craft_fonte` presentes.
  - Tabela Streamlit: coluna “Craft (R)” exibindo `R5`.
  - Cards: legenda “Craft R5” quando aplicável.

- `[x]` **Teste de integração do filtro de craft** — **Concluído (Pacote 4)**. Evidência: [`tests/test_integracao_filtro_craft.py`](tests/test_integracao_filtro_craft.py:1) verde (R4 descartado com mínimo 5, `qc=0` passa, catálogo sem `crafting-quality`).
  - Item craftado com `qualidade_craft=4` deve ser descartado quando
    `qualidade_craft_min=5`.
  - Item **não** craftado (`qualidade_craft=0`) deve continuar passando.
  - Item de catálogo (gema/encantamento/missiva) não deve receber
    `crafting-quality` nem ser filtrado por craft.
  - Onde está o filtro: `scraper_season2.py:461`.

---

## 3. Pendências de integração (P1)

- `[x]` **MCP Server: expor `qualidade_craft_min`** — **Concluído (Pacote 5)**. Evidência: parâmetro nas tools em [`mcp_server.py:443`](mcp_server.py:443)/[`:461`](mcp_server.py:461) e impls [`mcp_server.py:206`](mcp_server.py:206)/[`:251`](mcp_server.py:251); eco em `metadata` validado com `qualidade_craft_min=4`.
  - Hoje `mcp_server.py:217` e `mcp_server.py:260` instanciam o scraper sem o
    parâmetro, dependendo apenas do default 5.
  - Adicionar parâmetro nas tools `scrape_wowhead_item` e
    `scrape_wowhead_items`, repassar ao construtor e incluir no retorno/metadata.
  - Revalidar com `_test_mcp_client.py` ou cliente stdio.

- `[x]` **CLI: adicionar flag de qualidade de craft** — **Concluído (Pacote 2)**. Evidência: [`scraper_season2.py:829`](scraper_season2.py:829) com default 5; `--help` lista `--max-detalhes`, `--sem-detalhes`, `--qualidade-craft`.
  - `scraper_season2.py` já aceita `qualidade_craft_min`, mas o `argparse`
    (`scraper_season2.py:671`) não expõe a opção.
  - Adicionar `--qualidade-craft` (default 5) e repassar ao construtor.

- `[x]` **Configuração MCP local** — **Concluído (Pacote 5)**. Evidência: `.vscode/mcp.json` não versionado por decisão; gerado por [`mcp_server.py:537`](mcp_server.py:537) (`--print-config`), JSON válido com `command/args/cwd/env`.
  - `mcp_config.example.json` existe; `.vscode/mcp.json` não foi criado
    (criação rejeitada anteriormente).
  - Decidir se a config local será versionada ou gerada por script/documentação.

- `[x]` **Cobertura de UI automatizada** — **Concluído (Pacote 5)**. Evidência: [`tests/test_app_streamlit.py`](tests/test_app_streamlit.py:1) verde (4 abas, defaults 4 e 5, sem exceções).
  - O `AppTest` foi executado manualmente (não versionado).
  - Opcional: criar `test_app_streamlit.py` verificando:
    - 4 abas;
    - defaults `Raridade mínima=4` e `Qualidade de craft (R)=5`;
    - ausência de exceções ao alternar categorias.

---

## 4. Robustez e dados (P1/P2)

- `[x]` **Detecção de profissão de craft em gear** — **Concluído (Pacote 4)**. Evidência: hierarquia link → receita → texto → `_profissao_url` (só ferramenta) em [`wow_season2.py:1360`](wow_season2.py:1360); [`tests/test_craft_parser.py`](tests/test_craft_parser.py:1) cobre link/texto/receita.
  - `qualidade_craft` só é reportada quando `profissao_craft` é identificada.
  - Validar em amostra de itens craftados de cada profissão.
  - Se houver falhas, avaliar fallback por categoria/URL ou por marcador de
    receita na página (sem inferir em itens que não são craftados).

- `[x]` **Revisar heurística de `extrair_qualidade_craft`** — **Concluído (Pacote 4)**. Evidência: restrita em [`wow_season2.py:1505`](wow_season2.py:1505)/[`:1541`](wow_season2.py:1541); texto genérico "qualidade" não classifica; `motivo_qualidade_craft` sempre preenchido.
  - O segundo padrão (`wow_season2.py:1211`) é permissivo:
    `(?:craft|fabric|qualidade)[^\n]{0,40}\bR(\d)\b`.
  - Como a URL é a fonte primária, o risco é baixo, mas convém restringir para
    evitar falso positivo em tooltips de itens não craftados.

- `[x]` **Itens sem `ilvl` e catálogos** — **Concluído (Pacote 2)**. Evidência: [`tests/test_catalogo_sem_ilvl.py`](tests/test_catalogo_sem_ilvl.py:1) verde.
  - Confirmar que missivas/gemas/encantamentos continuam entrando mesmo com
    `ilvl=0` e que o filtro de craft não os afeta.

- `[x]` **Dados legados em `data/`** — **Concluído (Pacote 5)**. Evidência: movidos para `data/_legacy/` e documentados em [`data/README.md`](data/README.md:1); [`mcp_server.py:380`](mcp_server.py:380) lista só canônicos + contagem de legados.
  - `wowhead_all_items.json`, `wowhead_encantamento.json`,
    `wowhead_ferramenta_profissao.json`, `wowhead_missiva.json` são de versões
    antigas. Decidir entre migrar, regenerar ou remover para evitar confusão
    com os catálogos atuais (`wowhead_gemas.json`, `wowhead_encantamentos.json`,
    `wowhead_missivas.json`, `wowhead_catalogo.json`).

---

## 5. Limpeza e documentação (P2)

- `[x]` **Arquivos temporários/legados na raiz** — **Concluído (Pacote 5)**. Evidência: 11 arquivos movidos para `legacy/`; [`tests/test_imports.py`](tests/test_imports.py:1) garante que módulos ativos não arrastam `legacy.*`.
  - Avaliar remoção ou mover para `legacy/`:
    - `check_strategies.py`
    - `debug_parse.py`
    - `simple_test.py`
    - `run_scraper.py`
    - `test_crawl4ai_simple.py`
    - `test_crawler.py`
    - `test_final.py`
    - `test_profession_extraction.py`
    - `test_progresso.py`
    - `test_wowhead_logic.py`
    - `scraper_completo.py`, `scraper_completo_final.py`, `scraper_sem_llm.py`
      (fluxo legado “Partes 1..5”)
  - `_check_craft_quality.py` já foi removido.

- `[x]` **README** — **Concluído (Pacote 5)**. Evidência: [`README.md:97`](README.md:97) (JSON) e [`README.md:127`](README.md:127) (tabela).
  - Seção de campos e distinção raridade × craft atualizada.
  - Ainda faltam exemplos de saída JSON/Markdown com `qualidade_craft` e
    `Craft (R)`.

- `[x]` **Documentar setup do MCP** — **Concluído (Pacote 5)**. Evidência: [`README.md:362`](README.md:362) com `mcp>=1.0,<2`, stdio, `--selftest`, `--print-config`.
  - Reforçar em README: `mcp>=1.0,<2`, transporte stdio, exemplo de config e
    comando `python mcp_server.py --selftest`.

- `[x]` **Documentar workaround Windows** — **Concluído (Pacote 5)**. Evidência: [`runtime.py:25`](runtime.py:25) + [`README.md:424`](README.md:424).
  - Streamlit precisa de `WindowsProactorEventLoopPolicy` no worker
    (`app_streamlit.py`), enquanto o CLI já roda no loop principal.
  - Registrar o sintoma (`NotImplementedError` em subprocess) e a solução.

---

## 6. Comandos de validação de referência

```bat
set PYTHONIOENCODING=utf-8
python -m py_compile app_streamlit.py wow_season2.py scraper_season2.py markdown_season2.py test_season2.py
python test_season2.py
```

Validação rápida do app (Windows):

```bat
set PYTHONIOENCODING=utf-8
python -c "from streamlit.testing.v1 import AppTest; at=AppTest.from_file('app_streamlit.py', default_timeout=180); at.run(); print('EXCEPTIONS', len(at.exception)); print([(s.label, s.value) for s in at.sidebar.selectbox])"
```

Validação ao vivo de item craftado (exemplo):

```bat
set PYTHONIOENCODING=utf-8
python scraper_season2.py --urls https://www.wowhead.com/pt/item=273796 --max-itens 1 --max-detalhes 1
```

Depois conferir em `data/wowhead_itens_season2.json`:
`qualidade`, `qualidade_craft`, `qualidade_craft_fonte`, `profissao_craft`.

---

## 7. Riscos e observações

- **Não confundir os dois conceitos**: raridade 5 (Lendário) **não** é o mesmo
  que craft R5. O default correto é raridade **4** e craft **5**.
- **Fonte da qualidade de craft**: a URL `?crafting-quality=5` é a fonte
  primária; o tooltip pode vir com rótulo vazio, por isso não é confiável.
- **Filtro só descarta quando a qualidade é conhecida**: `qualidade_craft=0`
  (profissão não detectada) não é descartado, para não perder itens válidos.
- **Cada item custa 2 visitas** (PT-BR + EN); `max_detalhes` limita o custo.
- **Dados em `data/` desatualizados** ainda não refletem a coluna de craft até
  a re-extração.

---

## Limitação conhecida (nova)

A URL padrão de listagem de gear ([`config.py:225`](config.py:225), `/pt/items/min-ilvl:305/max-ilvl:350`) retorna a listagem genérica do banco de itens: o filtro de ilvl do Wowhead é client-side e não se aplica no crawl headless, então as primeiras variantes listadas são de itens antigos (ex.: `item=268265` com `bonus=13668:13987` → ilvl 219; `item=19019`). Com `--max-itens` baixo (ex.: 2) e filtro de ilvl ativo, o resultado é 0 itens — o descarte está correto, a fonte de listagem é que é pobre.

Sugestão de próximo passo: usar listagem com track/bônus da temporada (12846/12854/12856/13440) ou alimentar `--urls` com IDs canônicos; ambas já suportadas pela CLI.

## Histórico de execução

- **Pacote 1:** `crawl4ai==0.8.6`/`playwright==1.58.0` pinados, teste de contrato, erros explícitos no fluxo sem LLM, [`tests/test_smoke_offline.py`](tests/test_smoke_offline.py:1).
- **Pacote 2:** variante por anchor da linha + tooltip como árbitro, `max_detalhes` `None/0/N`, CLI (`--max-detalhes/--sem-detalhes/--qualidade-craft`), `min-ilvl` em todas as categorias.
- **Pacote 3:** [`coleta.py`](coleta.py:1) + adapter sem LLM → **798 itens, 0 erros**; `provider=deepseek/deepseek-chat`; entrypoints redirecionados.
- **Pacote 4:** craft R5 com `url:crafting-quality` e profissão (4 itens em 24), heurística restrita, dados canônicos regenerados.
- **Pacote 5:** MCP com `qualidade_craft_min` e `--print-config`, [`runtime.py`](runtime.py:1), [`tests/test_app_streamlit.py`](tests/test_app_streamlit.py:1), legados em `legacy/` e `data/_legacy/`, README atualizado.

**Suíte de validação:** 12 arquivos de teste + test_season2.py, 59 verificações verdes, 2 skips de rede (pytest não instalado; testes rodados por runner de fallback via "python tests/<arquivo>.py").

---

## Registro de correções aplicadas (handoff)

> Seção criada em **2026-11-06** para transferência de contexto entre IAs. Cada linha é uma
> correção **já implementada e validada** nos cinco pacotes (Pacote 1 a Pacote 5).
> `Status ✅` = corrigido, com teste/evidência registrada. **Nada nesta tabela precisa ser
> refeito**; use-a como mapa do código atual antes de mexer em qualquer módulo.
> As linhas (`arquivo:linha`) foram conferidas no código no momento desta escrita.

| ID | Problema original | Causa raiz | Correção | Arquivos (arquivo:linha) | Teste/evidência | Status |
|---|---|---|---|---|---|---|
| C-01 | Anchor de ícone vazio contaminava variante/bônus (ilvl errado) | `parse_links_itens()` pegava o 1º `<a>` da linha (o ícone, sem nome) e o `bonus` dele virava URL de detalhe — `item=268265?bonus=13668:13987` → ilvl 219 em vez de 344; `item=252258` → 28 em vez de 334 | `extrair_variante_anchor()` resolve a variante **na própria linha** (`tr`/`li`), nunca em outro item; o merge prefere o anchor `listview-cleartext` (`prioridade_nome`); dedupe por `chave_variacao()`; campo `variante_fonte` = `listagem` (tem bônus) ou `canonica` (sem bônus) | [`wow_season2.py:1060`](wow_season2.py:1060), [`wow_season2.py:1167`](wow_season2.py:1167), [`wow_season2.py:1781`](wow_season2.py:1781) | [`tests/test_parser_listagem.py`](tests/test_parser_listagem.py:1) — **4 OK**; execução real `--sem-detalhes` retorna **50/50** itens | ✅ |
| C-02 | URL de detalhe emitia `ilvl=` arbitrário e carregava bônus do ícone | `_url_detalhe()` montava `?ilvl=<n>&bonus=<...>` a partir de campos possivelmente contaminados, e aplicava `crafting-quality` em qualquer categoria | `_url_detalhe()` usa apenas os `bonus_ids` da variante; **não** emite `ilvl=`; `crafting-quality` só para itens fora do catálogo (`is_catalogo`) | [`scraper_season2.py:224`](scraper_season2.py:224) (`crafting-quality` em [`scraper_season2.py:240`](scraper_season2.py:240)) | `test_url_detalhe_nao_emite_ilvl`, `test_url_detalhe_catalogo_sem_crafting_quality` | ✅ |
| C-03 | ilvl nunca era validado entre listagem e página oficial | Não havia árbitro externo: o ilvl vinha da listagem (contaminada) ou da página (às vezes ausente) | Novo cliente de tooltip (`nether.wowhead.com/tooltip/item/<id>?dataEnv=1&locale=8&bonus=...`) com cache `data/_cache/tooltips.json` (sha1 de `item + bonus + locale`, TTL 7 dias, timeout 8 s, 2 tentativas, **nunca levanta exceção**) + `_arbitrar_ilvl()` com hierarquia **tooltip > página > listagem**, gravando `_ilvl_origem` e `_ilvl_conflito` | [`tooltip_client.py:30`](tooltip_client.py:30) (URL/endpoint), [`tooltip_client.py:31`](tooltip_client.py:31) (cache/TTL), [`scraper_season2.py:383`](scraper_season2.py:383) | [`tests/test_variante_ilvl.py`](tests/test_variante_ilvl.py:1) — **8 OK**; [`tools/validar_variantes.py`](tools/validar_variantes.py:1) → **5/5 via tooltip, 0 divergências** | ✅ |
| C-04 | Descarte em massa por ilvl antes de existir ilvl confiável | O filtro de ilvl rodava no pré-filtro mesmo quando a variante vinha de anchor sem bônus (ilvl não confiável) | `_prefiltrar()` só descarta quando `variante_fonte == "listagem"` **e** `bonus_ids` não vazio; caso contrário incrementa `descartes["ilvl_adiado"]` e adia a decisão para depois do detalhamento; exceção de catálogo preservada | [`scraper_season2.py:530`](scraper_season2.py:530) (`ilvl_adiado` em [`scraper_season2.py:565`](scraper_season2.py:565)) | Auditoria de execução: `descartes.ilvl_fora = 0` sem perda de itens válidos | ✅ |
| C-05 | `max_detalhes=0` era interpretado como "todos" | `0` caía no mesmo ramo de "sem limite", invertendo a intenção do usuário | Semântica explícita: `None` = todos, `0` = nenhum, `N` = N; ordem garantida `dedupe → pré-filtro → truncar → detalhar`; metadata expõe `total_brutos_antes_dedupe`, `detalhados`, `max_detalhes`, `ilvl_origem` | [`scraper_season2.py:444`](scraper_season2.py:444), [`scraper_season2.py:736`](scraper_season2.py:736), [`scraper_season2.py:761`](scraper_season2.py:761) | [`tests/test_max_detalhes.py`](tests/test_max_detalhes.py:1) — **6 OK**; execução real `--sem-detalhes` → `detalhados=0` | ✅ |
| C-06 | CLI sem controle de custo de detalhamento nem de craft | `argparse` só tinha `--max-itens`; craft ficava no default fixo | Novas flags `--max-detalhes` (None/0/N), `--sem-detalhes` (≡ `--max-detalhes 0`) e `--qualidade-craft` (default 5), repassadas ao construtor | [`scraper_season2.py:896`](scraper_season2.py:896), [`scraper_season2.py:906`](scraper_season2.py:906), [`scraper_season2.py:919`](scraper_season2.py:919) | `python scraper_season2.py --help` lista as três flags | ✅ |
| C-07 | Crawl4AI 0.8.6 quebrou `JsonCssExtractionStrategy(css_selectors=...)` | A versão nova exige `schema` posicional; o fluxo "Sem LLM" dependia da assinatura antiga | Fluxo "Sem LLM" reescrito sobre os parsers canônicos via `coleta.py` (`itens_de_html`, `extrair_itens_de_url`); `scraper_sem_llm.py` virou adapter (`dict_para_ferramenta/encantamento/missiva`); **zero** uso de `JsonCssExtractionStrategy` no projeto | [`coleta.py:88`](coleta.py:88), [`coleta.py:141`](coleta.py:141), [`scraper_sem_llm.py:158`](scraper_sem_llm.py:158) | Execução real: **798 itens, `erros_por_parte {}`**; [`tests/test_sem_llm_adapter.py`](tests/test_sem_llm_adapter.py:1) — **4 OK** | ✅ |
| C-08 | Exceções engolidas mascaravam resultado "0 itens" | `except` genérico sem log e sem re-raise fazia falha de crawl parecer sucesso vazio | `logging.exception` + re-raise de `TypeError/AttributeError/ImportError`; erros agregados em `metadata.erros_por_parte` e `metadata.total_erros` | [`scraper_sem_llm.py:288`](scraper_sem_llm.py:288), [`scraper_sem_llm.py:545`](scraper_sem_llm.py:545) | `test_falha_de_crawl_registra_erro_por_parte` | ✅ |
| C-09 | Provider LLM inválido (`provider="deepseek"`) e `config=` no lugar de `llm_config=` | `litellm` exige `fornecedor/modelo`; a API do Crawl4AI renomeou o parâmetro | `LLM_PROVIDER` + `montar_llm_config()` normalizam o provider; legados usam `provider=LLM_PROVIDER` e `llm_config=` | [`config.py:58`](config.py:58), [`config.py:65`](config.py:65), [`legacy/scraper.py:85`](legacy/scraper.py:85) | Busca por `provider="deepseek"` → **0 ocorrências** | ✅ |
| C-10 | Dependência sem teto permitia breaking change silencioso | `requirements.txt` não fixava `crawl4ai`/`playwright`; um `pip install` podia trocar a API | Pinos exatos `crawl4ai==0.8.6` e `playwright==1.58.0`, `mcp>=1.0.0,<2`; teste de contrato das assinaturas + guia de upgrade | [`requirements.txt:12`](requirements.txt:12), [`requirements.txt:19`](requirements.txt:19), [`requirements-dev.txt:12`](requirements-dev.txt:12), [`tests/test_contrato_crawl4ai.py`](tests/test_contrato_crawl4ai.py:1), [`docs/UPGRADE_CRAWL4AI.md`](docs/UPGRADE_CRAWL4AI.md:1) | `tests/test_contrato_crawl4ai.py` verde | ✅ |
| C-11 | `test_final.py` "passava" com o sistema quebrado | Teste herdado não fazia assert de efeito observável | Movido para `legacy/`; novo smoke offline com asserts de efeito observável (contrato, instanciação, exporters) | [`legacy/test_final.py`](legacy/test_final.py:1), [`tests/test_smoke_offline.py`](tests/test_smoke_offline.py:1) | `tests/test_smoke_offline.py` verde | ✅ |
| C-12 | Profissão de craft vazia em gear craftado | O parser só olhava o texto visível da página, que raramente nomeia a profissão | Hierarquia **link → receita** (mapa de `craft_receitas_s2.json`/`craft_armas_s2.json`) **→ texto → `_profissao_url`** (somente `ferramenta`); campos `profissao_craft_fonte` e `craft_indicio` | [`wow_season2.py:1360`](wow_season2.py:1360), [`wow_season2.py:1712`](wow_season2.py:1712), [`wow_season2.py:2020`](wow_season2.py:2020) | IDs `237831`/`237839` → `Ferraria`; [`tests/test_craft_parser.py`](tests/test_craft_parser.py:1) — **6 OK** | ✅ |
| C-13 | Heurística de `extrair_qualidade_craft` permissiva | O padrão casava com a palavra genérica "qualidade", classificando item não craftado como R1..R5 | `extrair_qualidade_craft_detalhado()`/`extrair_qualidade_craft()` exigem rótulo explícito, marca `crafting-quality` ou `R1..R5`/`Rank N` **com contexto de craft na mesma linha**; `motivo_qualidade_craft` sempre preenchido | [`wow_season2.py:1505`](wow_season2.py:1505), [`wow_season2.py:1541`](wow_season2.py:1541) | `test_nao_classifica_texto_generico_como_qualidade` | ✅ |
| C-14 | `min-level`/`max-level` (filtro inexistente no Wowhead) e `url_filtro` nunca aplicado | `min-level`/`max-level` filtram **nível de personagem**; e o `url_filtro` da categoria era declarado mas ignorado | `min-ilvl`/`max-ilvl` em todas as fontes e normalização de URLs antigas; `_aplicar_url_filtro()` idempotente aplicado em `resolver_urls_categoria()` | [`config.py:225`](config.py:225), [`config.py:364`](config.py:364), [`config.py:395`](config.py:395), [`config.py:423`](config.py:423) | `TEM_MIN_LEVEL = False` (nenhuma URL com `min-level`) | ✅ |
| C-15 | Página anti-bot (Cloudflare) entrava como item com nome falso | O HTML do desafio era parseado como se fosse listagem de itens | `_pagina_desafio()` detecta o desafio; `_crawl_locale()` tenta 3 vezes; falha persistente vai para `metadata.falhas` (não vira item) | [`scraper_season2.py:77`](scraper_season2.py:77), [`scraper_season2.py:259`](scraper_season2.py:259) | Item falso não aparece no JSON; falhas listadas em `metadata.falhas` | ✅ |
| C-16 | MCP não permitia controlar o rank de craft | As tools não expunham `qualidade_craft_min`; ficava sempre no default 5 | Parâmetro `qualidade_craft_min` nas tools e nas impls, ecoado em `metadata`; `--print-config` gera a config local | [`mcp_server.py:446`](mcp_server.py:446), [`mcp_server.py:469`](mcp_server.py:469), [`mcp_server.py:209`](mcp_server.py:209), [`mcp_server.py:259`](mcp_server.py:259), [`mcp_server.py:537`](mcp_server.py:537) | `metadata["qualidade_craft_min"] = 4` validado via cliente stdio | ✅ |
| C-17 | Workaround Windows duplicado em 3 entrypoints | Cada entrypoint repetia a troca de policy/event loop | `configurar_event_loop_windows()` centralizado | [`runtime.py:25`](runtime.py:25), [`app_streamlit.py:701`](app_streamlit.py:701), [`mcp_server.py:37`](mcp_server.py:37), [`run_scraper.py:68`](run_scraper.py:68) | Sem `NotImplementedError` de subprocesso no Playwright (Windows) | ✅ |
| C-18 | UI/CSV sem rastreabilidade do craft | Exportação e tabela só mostravam o rank, sem fonte/motivo/profissão | CSV com `qualidade_craft`, `qualidade_craft_fonte`, `profissao_craft`, `profissao_craft_fonte`, `motivo_qualidade_craft`, `craft_indicio`; coluna "Craft (R)" na tabela e badge "Craft R" nos cards | [`app_streamlit.py:300`](app_streamlit.py:300), [`app_streamlit.py:177`](app_streamlit.py:177), [`app_streamlit.py:224`](app_streamlit.py:224) | [`tests/test_app_streamlit.py`](tests/test_app_streamlit.py:1) — **4 OK** | ✅ |
| C-19 | Raiz do projeto poluída com 11 scripts legados | Scripts de teste/experimento ficaram ao lado do código ativo | Movidos para `legacy/`; dados antigos para `data/_legacy/`; teste de imports impede que módulos ativos arrastem `legacy.*` | [`legacy/`](legacy/__init__.py:1), [`tests/test_imports.py`](tests/test_imports.py:1) | `tests/test_imports.py` verde | ✅ |
| C-20 | Dados canônicos desatualizados (3 itens, sem coluna de craft) | JSON/Markdown gerados antes de `qualidade_craft` existir | `data/wowhead_itens_season2.json` regenerado com **24 itens**, 100% `item_level = 321` na faixa 305–350 e **4 craftados R5**; `data/wowhead_season2.md` com cabeçalho `Craft (R)` | [`data/wowhead_itens_season2.json`](data/wowhead_itens_season2.json:1), [`data/wowhead_season2.md:50`](data/wowhead_season2.md:50) | Contagem verificada por script: `itens=24`, `Counter({321: 24})`, `craft {0: 20, 5: 4}` | ✅ |

**Resumo:** 20 correções aplicadas (C-01 … C-20), todas com evidência executável. Os 12 arquivos
de validação são os 11 de `tests/` mais `test_season2.py`.

---

## Pendências abertas para a próxima IA (falhas conhecidas)

> Estes itens **não foram corrigidos** nos pacotes. São o backlog real do próximo ciclo.
> Cada um traz comando de reprodução e critério de aceite objetivo — não invente novos
> requisitos antes de fechar estes.

### F-01 — Listagem de gear retorna banco de itens genérico e o resultado pode ser 0 itens (ALTA)

- **Sintoma:** `python scraper_season2.py --max-itens 2 --max-detalhes 2 --qualidade-craft 5`
  termina com `total_brutos=2`, `descartes={"ilvl_fora": 2}` e **0 itens finais**. A listagem
  padrão devolve itens antigos (ex.: `item=19019` Thunderfury) e as primeiras variantes são
  legítimas de outra faixa (`268265` com `bonus=13668:13987` → ilvl 219).
- **Reprodução:** `python scraper_season2.py --max-itens 2 --max-detalhes 2 --qualidade-craft 5`
- **Causa raiz:** a URL padrão ([`config.py:225`](config.py:225),
  `/pt/items/min-ilvl:305/max-ilvl:350`) não aplica filtro server-side — o Wowhead filtra
  **client-side**, então o crawl headless recebe a listagem genérica do banco de itens. O
  descarte está correto; a **fonte de listagem** é que é pobre.
- **Arquivos envolvidos:** [`config.py:225`](config.py:225) (URL padrão),
  [`config.py:279`](config.py:279) (`urls_template` de `gear_season2`),
  [`scraper_season2.py:530`](scraper_season2.py:530) (pré-filtro).
- **Correção sugerida:** montar a listagem com bônus/track da temporada
  (12846 / 12854 / 12856 / 13440) **ou** resolver a variante canônica via tooltip antes do
  descarte **ou** usar `--urls` canônicas como fonte primária de gear.
- **Critério de aceite:** `python scraper_season2.py --max-itens 20` sobre a listagem padrão
  devolve **≥ 15 itens** com `item_level` entre 305 e 350.
- **Risco se não corrigir:** o pipeline "funciona", mas não entrega gear da Season 2 por
  padrão; qualquer usuário novo conclui que o scraper está quebrado.

### F-02 — Divergência de `item_level` para o mesmo id entre ferramentas (MÉDIA)

- **Sintoma:** `python tools/validar_craft.py --ids 237831 237839` reporta `item_level=246`,
  enquanto o JSON canônico registra `321` para os mesmos ids.
- **Reprodução:** `python tools/validar_craft.py --ids 237831 237839`
- **Causa raiz:** contexto de bônus diferente — o validador monta a URL com
  `crafting-quality` (sem os bônus da variante gravada), enquanto o pipeline usa a variante
  deduplicada. Os dois caminhos não compartilham o árbitro de ilvl.
- **Arquivos envolvidos:** [`tools/validar_craft.py:94`](tools/validar_craft.py:94),
  [`scraper_season2.py:383`](scraper_season2.py:383) (`_arbitrar_ilvl`),
  [`tooltip_client.py:76`](tooltip_client.py:76) (`montar_url_tooltip`).
- **Correção sugerida:** padronizar a resolução de bônus no `validar_craft` usando a mesma
  `_arbitrar_ilvl()`/variante do pipeline (ou consumir a variante já gravada no JSON).
- **Critério de aceite:** ambos reportam o **mesmo ilvl** e o **mesmo `bonus_ids`**; o relatório
  em [`data/_diagnostico/craft.json`](data/_diagnostico/craft.json:1) fica consistente com o
  JSON canônico.
- **Risco se não corrigir:** decisões de filtro tomadas com base no validador ficam erradas e o
  diagnóstico perde credibilidade.

### F-03 — `pytest` não instalado; testes rodam por runner de fallback (MÉDIA)

- **Sintoma:** `python -m pytest` → `No module named pytest`. A suíte só roda via
  `python tests/<arquivo>.py` (runner próprio com `[OK]/[FAIL]`).
- **Reprodução:** `python -m pytest`
- **Causa raiz:** `requirements-dev.txt` declara `pytest`/`pytest-asyncio`, mas o ambiente não
  foi provisionado com as dev-deps.
- **Arquivos envolvidos:** [`requirements-dev.txt:12`](requirements-dev.txt:12),
  [`tests/__init__.py`](tests/__init__.py:1).
- **Correção sugerida:** `pip install -r requirements-dev.txt` e validar/migrar todos os
  `tests/*.py` sob pytest, **mantendo** o runner de fallback (execução offline/CI sem pytest).
- **Critério de aceite:** `python -m pytest -q` verde, com a mesma contagem do runner manual.
- **Risco se não corrigir:** a descoberta de testes depende de lista manual; um teste novo pode
  nunca ser executado.

### F-04 — 403 anti-bot intermitente do Wowhead (MÉDIA)

- **Sintoma:** `HTTP Error 403: Forbidden` em `urllib` e desafios Cloudflare esporádicos; os
  itens afetados caem em `metadata.falhas` e o total final cai sem explicação visível.
- **Reprodução:** `python tools/validar_variantes.py --amostra 20` (repetir 3 vezes)
- **Causa raiz:** o Crawl4AI roda com fingerprint padrão e sem backoff; o endpoint de tooltip
  usa o mesmo IP sem circuit breaker.
- **Arquivos envolvidos:** [`scraper_season2.py:77`](scraper_season2.py:77) (`_pagina_desafio`),
  [`scraper_season2.py:259`](scraper_season2.py:259) (`_crawl_locale`),
  [`tooltip_client.py:30`](tooltip_client.py:30) (endpoint de tooltip).
- **Correção sugerida:** stealth/viewport realista, backoff progressivo, rotação de `locale`,
  fallback para tooltip HTTP e circuit breaker após N falhas consecutivas.
- **Critério de aceite:** 3 execuções consecutivas de 20 itens sem falha persistente em
  `metadata.falhas`.
- **Risco se não corrigir:** execuções grandes falham parcialmente e o resultado não é
  reprodutível.

### F-05 — `--sem-detalhes` produz itens sem nome/qualidade úteis (MÉDIA)

- **Sintoma:** `python scraper_season2.py --sem-detalhes --max-itens 200` → `detalhados=0` e
  `descartes={"sem_ilvl": 200}`.
- **Reprodução:** `python scraper_season2.py --sem-detalhes --max-itens 200`
- **Causa raiz:** sem detalhamento não há enriquecimento de nome/ilvl; o registro final não
  passa no filtro de `sem_ilvl` ([`scraper_season2.py:612`](scraper_season2.py:612)).
- **Arquivos envolvidos:** [`scraper_season2.py:612`](scraper_season2.py:612) (descarte
  `sem_ilvl`), [`scraper_season2.py:919`](scraper_season2.py:919) (flag `--sem-detalhes`),
  [`tooltip_client.py:76`](tooltip_client.py:76) (tooltip barato).
- **Correção sugerida:** permitir o tooltip (leve, sem browser/Firecrawl) como enriquecimento
  mínimo no modo sem detalhes.
- **Critério de aceite:** `--sem-detalhes` retorna **≥ 40 itens** com `nome` e `item_level`
  preenchidos.
- **Risco se não corrigir:** o modo mais barato é praticamente inútil hoje.

### F-06 — 20 de 24 itens ficam com `motivo_qualidade_craft = "ignorado:sem_profissao (url:crafting-quality)"` (MÉDIA)

- **Sintoma:** em `data/wowhead_itens_season2.json`, 20 dos 24 itens têm `qualidade_craft=0` e
  motivo `ignorado:sem_profissao (url:crafting-quality)`.
- **Reprodução:** `python -c "import json,collections; d=json.load(open('data/wowhead_itens_season2.json',encoding='utf-8')); print(collections.Counter(i.get('motivo_qualidade_craft') for i in d['itens']))"`
- **Causa raiz:** a URL carrega `crafting-quality`, mas a página não expõe a profissão; o
  fallback por receita (`craft_receitas_s2.json`/`craft_armas_s2.json`) não cobre esses ids.
- **Arquivos envolvidos:** [`wow_season2.py:1978`](wow_season2.py:1978) (motivo "ignorado"),
  [`wow_season2.py:1360`](wow_season2.py:1360) (`_profissao_craft_com_fonte`),
  `base_conhecimento_ai_studio/craft_receitas_s2.json`.
- **Correção sugerida:** ampliar o mapa receita→profissão com os ids do catálogo e/ou inferir
  profissão por `subclass`/`slot`, marcando baixa confiança em `profissao_craft_fonte`.
- **Critério de aceite:** **≤ 5 itens em 24** sem `profissao_craft`.
- **Risco se não corrigir:** o filtro `--qualidade-craft` praticamente não atua sobre o catálogo
  real.

### F-07 — Base de dados canônica pequena (BAIXA)

- **Sintoma:** `data/wowhead_itens_season2.json` tem **24 itens** e `data/wowhead_catalogo.json`
  tem **10** — insuficiente para validar catálogo/UI em escala.
- **Reprodução:** `python -c "import json; print(len(json.load(open('data/wowhead_itens_season2.json',encoding='utf-8'))['itens']), len(json.load(open('data/wowhead_catalogo.json',encoding='utf-8'))['itens']))"`
- **Causa raiz:** a última rodada usou poucas URLs (as canônicas), não uma varredura por
  categoria.
- **Arquivos envolvidos:** [`data/wowhead_itens_season2.json`](data/wowhead_itens_season2.json:1),
  [`data/wowhead_catalogo.json`](data/wowhead_catalogo.json:1),
  [`config.py:273`](config.py:273) (`CATEGORIAS_WOW`).
- **Correção sugerida:** rodada completa por categoria com `--urls` canônicas (depois de F-01).
- **Critério de aceite:** **≥ 100 itens de gear** e **≥ 30 de catálogo**.
- **Risco se não corrigir:** bugs de UI e de agregação só aparecem em produção.

### F-08 — Dataclasses do fluxo "Sem LLM" não expõem ícone (BAIXA)

- **Sintoma:** o dict canônico tem `icone_url`, mas `FerramentaProducao`,
  `EncantamentoFerramenta` e `MissivaProfissao` não carregam ícone, então a UI legada
  (contrato `asdict`) exibe placeholder.
- **Reprodução:** `python -c "from scraper_sem_llm import FerramentaProducao; print(list(FerramentaProducao.__dataclass_fields__))"`
- **Causa raiz:** as dataclasses foram definidas antes de `icone_url` entrar no dict canônico.
- **Arquivos envolvidos:** [`scraper_sem_llm.py:46`](scraper_sem_llm.py:46),
  [`scraper_sem_llm.py:61`](scraper_sem_llm.py:61), [`scraper_sem_llm.py:76`](scraper_sem_llm.py:76),
  [`scraper_sem_llm.py:158`](scraper_sem_llm.py:158), [`app_streamlit.py:552`](app_streamlit.py:552).
- **Correção sugerida:** adicionar campo opcional `icone` (default vazio) mantendo
  compatibilidade com os adapters existentes.
- **Critério de aceite:** UI legada exibe ícone sem quebrar o contrato `asdict`.
- **Risco se não corrigir:** perda visual e inconsistência entre o fluxo novo e o legado.

### F-09 — Ruído no console Windows (BAIXA) — **RESOLVIDO (PKG-1, 2026-11-06)**

- **Sintoma:** `UnicodeEncodeError: 'charmap' codec` no `rich` do Crawl4AI e mojibake em logs
  redirecionados; `PYTHONIOENCODING=utf-8` resolve pontualmente.
- **Reprodução:** `python scraper_sem_llm.py > log.txt` (sem `PYTHONIOENCODING`)
- **Causa raiz:** o console `cp1252` do Windows não aceita os caracteres usados pelos logs.
- **Arquivos envolvidos:** [`runtime.py:1`](runtime.py:1) (ponto natural para o fix),
  [`run_scraper.py:23`](run_scraper.py:23) (reconfigure pontual já existente).
- **Correção aplicada:** `configurar_saida_utf8()` em [`runtime.py:26`](runtime.py:26) executa
  `sys.stdout.reconfigure(encoding="utf-8")` / `stderr` no import (respeitando
  `PYTHONIOENCODING` já em UTF-8). `runtime` é importado no topo de
  [`app_streamlit.py:37`](app_streamlit.py:37), [`mcp_server.py:33`](mcp_server.py:33),
  [`scraper_season2.py:24`](scraper_season2.py:24) e [`scraper_sem_llm.py:19`](scraper_sem_llm.py:19).
- **Critério de aceite:** execução sem erro de encoding em terminal `cp1252`. ✅
- **Risco se não corrigir:** logs truncados e falso diagnóstico de falha.

### F-10 — `legacy/*` com erros de tipagem/Pylance (BAIXA) — **RESOLVIDO (PKG-1, 2026-11-06)**

- **Sintoma:** `bonus_ids: List[str] = None`, uso incorreto de `AsyncGenerator` e afins geram
  avisos de tipo no diretório `legacy/`.
- **Reprodução:** abrir `legacy/` no VS Code com Pylance (ou rodar `mypy legacy/`).
- **Causa raiz:** código antigo escrito antes das anotações estritas; **fora de escopo** dos
  pacotes de correção.
- **Arquivos envolvidos:** [`legacy/scraper.py`](legacy/scraper.py:1),
  [`legacy/scraper_completo.py`](legacy/scraper_completo.py:1),
  [`legacy/scraper_completo_final.py`](legacy/scraper_completo_final.py:1).
- **Correção aplicada:** `legacy` excluído da análise de tipos em
  [`pyrightconfig.json:1`](pyrightconfig.json:1) e em [`mypy.ini:1`](mypy.ini:1)
  (`[mypy-legacy.*] ignore_errors = True`). Nenhum arquivo de `legacy/` foi refatorado.
- **Critério de aceite:** zero erros de tipo em `legacy/` ou exclusão explicitada em config. ✅
- **Risco se não corrigir:** ruído constante no editor encobre erro real em código ativo.

### F-11 — Acúmulo de artefatos em `data/` (BAIXA) — **RESOLVIDO (PKG-1, 2026-11-06)**

- **Sintoma:** arquivos `*_sem_llm_<timestamp>.json` crescem sem rotação e os scripts de
  diagnóstico (`diag_*.py`, `valida_*.py`, `extract_ids.py`) continuam em `data/_diagnostico/`.
- **Reprodução:** `dir data`
- **Causa raiz:** cada execução grava um arquivo novo; não há política de retenção nem separação
  entre script e relatório.
- **Arquivos envolvidos:** `data/` (ex.:
  `data/wowhead_all_items_sem_llm_20261106_080002.json`),
  [`tools/diagnostico/`](tools/diagnostico/__init__.py:1).
- **Correção aplicada:** retenção em [`scraper_season2.py:76`](scraper_season2.py:76)
  (`_rotacionar_artefatos` / `rotacionar_artefatos`, `manter=5`, nunca toca arquivos canônicos),
  usada em [`scraper_sem_llm.py:586`](scraper_sem_llm.py:586) após cada gravação timestamped e
  em [`scraper_season2.py:896`](scraper_season2.py:896) quando o caminho casa `*_sem_llm_*`.
  Scripts movidos para [`tools/diagnostico/`](tools/diagnostico/__init__.py:1); em
  `data/_diagnostico/` restou apenas o relatório `craft.json`.
- **Critério de aceite:** **≤ 2 arquivos por tipo** e `data/_diagnostico` só com `.json`. ✅
- **Risco se não corrigir:** repositório inflado e difícil distinguir dado atual de histórico.

### F-12 — Pendências ainda abertas na base de conhecimento (MÉDIA)

- **Sintoma:** [`base_conhecimento_ai_studio/pendencias.md`](base_conhecimento_ai_studio/pendencias.md:1)
  mantém itens não resolvidos: chave Firecrawl exposta (§3.9), "+1 de Brilho" do Chaveiro da
  Sorte (§3.10), tabela 318–331 por rank (§3.10), Pedra Ritual do Caçador em mão secundária
  (§3.10), encantamento de pulsos/mãos/capa inexistente (§3.12) e conflitos 2B×2C e C23×C24
  (§3.13).
- **Reprodução:** abrir `base_conhecimento_ai_studio/pendencias.md` nas seções §3.9 a §3.13.
- **Causa raiz:** itens normativos de dados que dependem de validação contra a fonte oficial do
  jogo — não são bug de código.
- **Arquivos envolvidos:**
  [`base_conhecimento_ai_studio/pendencias.md:135`](base_conhecimento_ai_studio/pendencias.md:135)
  (§3.9), [`base_conhecimento_ai_studio/pendencias.md:143`](base_conhecimento_ai_studio/pendencias.md:143)
  (§3.10), [`base_conhecimento_ai_studio/pendencias.md:166`](base_conhecimento_ai_studio/pendencias.md:166)
  (§3.12), [`base_conhecimento_ai_studio/pendencias.md:188`](base_conhecimento_ai_studio/pendencias.md:188)
  (§3.13).
- **Correção aplicada (§3.9):** chave sanitizada na documentação; varredura textual não encontrou
  segredo em arquivo versionável e o `.env` não contém `FIRECRAWL`. Procedimento manual e de
  histórico Git em [`docs/SEGURANCA.md`](docs/SEGURANCA.md:1). **Revogação no painel Firecrawl
  continua pendente** (ação manual, prioridade máxima).
- **Correção sugerida (demais §3.x):** tratar item a item conforme a fonte normativa.
- **Critério de aceite:** cada §3.x resolvido com evidência registrada na própria seção.
- **Risco se não corrigir:** credencial vazada (risco de segurança/custo) e dados de craft
  incorretos propagados para o catálogo.

> **Observação importante:** a divergência de `item_level` de **F-02** e o descarte de **F-01**
> **não são regressões** dos pacotes — foram confirmados como comportamento do site
> (listagem genérica + filtro client-side) somado à heurística de variante. A validação final
> **não encontrou regressão bloqueante**; o que existe é fonte de dados pobre (F-01) e
> inconsistência de contexto de bônus entre ferramentas (F-02).

---

## Protocolo de handoff (para a próxima IA)

1. **Leia primeiro esta seção**, depois `## Registro de correções aplicadas (handoff)` e
   `## Pendências abertas para a próxima IA (falhas conhecidas)`. Só então abra o código.
2. **Ordem recomendada de trabalho:** **F-01** (desbloqueia o uso real do pipeline) → **F-05**
   (torna o modo barato útil) → **F-03** (habilita `pytest`) → **F-04** (estabilidade de rede) →
   **F-02** (consistência entre ferramentas) → **F-06** (profissão de craft em escala) →
   **F-07** (base de dados) → **F-12** (base de conhecimento; a chave Firecrawl é urgente e pode
   ser antecipada) → F-08/F-09/F-10/F-11 (baixa prioridade).
3. **Como validar sem `pytest`:** `python test_season2.py` e `python tests/<arquivo>.py` — todos
   os arquivos têm runner de fallback com saída `[OK]`/`[FAIL]`. Depois de instalar as dev-deps,
   usar `python -m pytest -q`.
4. **Comandos de fumaça (rodar antes de qualquer commit):**
   - `python scraper_season2.py --help`
   - `python scraper_sem_llm.py`
   - `python mcp_server.py --selftest`
   - `python mcp_server.py --print-config`
   - `python tools/validar_variantes.py --amostra 5`
   - `python tools/validar_craft.py --ids 237831 237839`
5. **Arquitetura em uma linha:** [`coleta.py`](coleta.py:1) = rede (Crawl4AI);
   [`wow_season2.py`](wow_season2.py:1) = parsers canônicos (listagem/página/tooltip);
   [`scraper_season2.py`](scraper_season2.py:1) = orquestração, filtros, dedupe e CLI;
   [`tooltip_client.py`](tooltip_client.py:1) = validação de ilvl;
   [`mcp_server.py`](mcp_server.py:1) e [`app_streamlit.py`](app_streamlit.py:1) = superfícies;
   [`legacy/`](legacy/__init__.py:1) = código antigo, **não usar**.
6. **Regras de ouro:**
   - **Não** reintroduzir `JsonCssExtractionStrategy` (quebrado no `crawl4ai==0.8.6`).
   - **Não** propagar `bonus` do anchor de ícone — a variante é sempre resolvida na mesma linha.
   - **Nunca** engolir exceção de configuração (`TypeError`/`AttributeError`/`ImportError` devem
     subir e aparecer em `metadata.erros_por_parte`).
   - Qualquer mudança em [`wow_season2.py`](wow_season2.py:1) ou
     [`scraper_season2.py`](scraper_season2.py:1) exige rodar os **12 arquivos de teste**
     (11 em `tests/` + `test_season2.py`).
   - Manter `min-ilvl`/`max-ilvl`; **nunca** voltar para `min-level`/`max-level`.
7. **Critério de "pronto" do próximo ciclo:** **F-01** e **F-05** fechados (o pipeline rende
   itens reais na listagem padrão) + `pytest` habilitado com suíte verde + **F-12** (chave
   Firecrawl) resolvido.

---

## Estado da execução do handoff (verificado em 2026-11-06)

> Auditoria **somente leitura**: nenhum arquivo de código, teste ou dado foi alterado.
> A única escrita deste ciclo é esta seção. Toda afirmação abaixo tem evidência de execução
> colada no próprio texto.

### A) O que está CONCLUÍDO e verificado

**Tabela de evidências (comandos reais executados em 2026-11-06):**

| Verificação | Comando | Resultado real |
|---|---|---|
| Compilação | `python -m py_compile scraper_season2.py` | exit 0, sem saída de erro |
| `conftest.py` | — | **não existe** na raiz (item ignorado, como previsto) |
| Suíte canônica | `python test_season2.py` | **12/12 `[OK]`** — "Todos os testes da Season 2 passaram." |
| `pytest` | `python -m pytest --version` | **`No module named pytest`** (F-03 aberto) |
| `tests/test_app_streamlit.py` | runner fallback | 4 OK (`SUCESSO: 0 falha(s)`) |
| `tests/test_campos_obrigatorios.py` | runner fallback | 6 OK |
| `tests/test_catalogo_sem_ilvl.py` | runner fallback | 3 OK |
| `tests/test_circuit_breaker.py` | runner fallback | 5 OK |
| `tests/test_coleta_wait_for.py` | runner fallback | 12 OK |
| `tests/test_contrato_crawl4ai.py` | runner fallback | 4 OK |
| `tests/test_craft_parser.py` | runner fallback | 6 OK |
| `tests/test_imports.py` | runner fallback | 2 OK |
| `tests/test_integracao_filtro_craft.py` | runner fallback | 4 OK |
| `tests/test_max_detalhes.py` | runner fallback | 6 OK |
| `tests/test_parser_listagem.py` | runner fallback | 4 OK |
| `tests/test_selecao_variantes.py` | runner fallback | **7 OK** |
| `tests/test_sem_llm_adapter.py` | runner fallback | 4 OK |
| `tests/test_smoke_offline.py` | runner fallback | 6 OK + 2 `[SKIP]` (rede) |
| `tests/test_tooltip_raidbots.py` | runner fallback | 11 OK |
| `tests/test_variante_ilvl.py` | runner fallback | 8 OK |

**Estado final da suíte:** **17 arquivos verdes** (16 em `tests/` + `test_season2.py`),
**92 `[OK]` em `tests/`** + **12 `[OK]` em `test_season2.py`** = **104 casos OK**, 2 `[SKIP]`
por dependência de rede/Chromium, **0 falhas**. `pytest` **não está instalado**.

**PKG-1 — Segurança/infra:** confirmados [`docs/SEGURANCA.md`](docs/SEGURANCA.md:1),
[`.gitignore`](.gitignore:1), [`.env.example`](.env.example:1),
`configurar_saida_utf8()` em [`runtime.py:26`](runtime.py:26), [`pyrightconfig.json`](pyrightconfig.json:1),
[`mypy.ini`](mypy.ini:1), `_rotacionar_artefatos` em [`scraper_season2.py:76`](scraper_season2.py:76)
e scripts em [`tools/diagnostico/`](tools/diagnostico/__init__.py:1).

**PKG-2 — Campos obrigatórios/tooltip:** [`tooltip_raidbots.py`](tooltip_raidbots.py:1) presente e
consumido em [`markdown_season2.py:23`](markdown_season2.py:23)/[`:215`](markdown_season2.py:215)
e em [`app_streamlit.py:330`](app_streamlit.py:330)/[`:1273`](app_streamlit.py:1273). Escalas de
fonte (`FONTES_ICONE`, `FONTES_NOME`, `FONTES_ATRIBUTOS`) em
[`wow_season2.py:931`](wow_season2.py:931), com o cruzamento de fontes em
[`wow_season2.py:2075`](wow_season2.py:2075). Testes `test_tooltip_raidbots.py` (11 OK) e
`test_campos_obrigatorios.py` (6 OK) verdes.

**PKG-3 — Rede/anti-bot:** `JS_LAZY_LOAD` (fonte única) em [`coleta.py:151`](coleta.py:151),
bloco `mouseover` em [`coleta.py:121`](coleta.py:121), `WAIT_TIMEOUT` em
[`coleta.py:62`](coleta.py:62)/[`:242`](coleta.py:242), `wait_for_padrao` em
[`coleta.py:186`](coleta.py:186); importado por [`scraper_season2.py:30`](scraper_season2.py:30) e
aplicado em [`scraper_season2.py:400`](scraper_season2.py:400). Detecção de desafio anti-bot em
[`scraper_season2.py:153`](scraper_season2.py:153), circuit breaker resumido em
`metadata.circuit_breaker` ([`scraper_season2.py:1297`](scraper_season2.py:1297)),
`Referer`/`User-Agent` em [`tooltip_client.py:198`](tooltip_client.py:198) (constantes em
[`:36`](tooltip_client.py:36)/[`:42`](tooltip_client.py:42)). URL de listagem com
`bonus`/`quality` em [`config.py:241`](config.py:241). Testes `test_coleta_wait_for.py` (12 OK)
e `test_circuit_breaker.py` (5 OK) verdes.

**F-01 (P-01) — seleção de variante: IMPLEMENTADO.** Confirmado por leitura:
[`config.py:230`](config.py:230) define `TRACKS_SEASON2 = (12846, 12854, 12856, 13440)` com
comentário citando [`base_conhecimento_ai_studio/bonus_ids_s2.md`](base_conhecimento_ai_studio/bonus_ids_s2.md:1);
[`scraper_season2.py:718`](scraper_season2.py:718) implementa `_selecionar_melhores_variantes`
completo (prioridade track → maior ilvl → única sem ilvl, ordem preservada, alternativas em
`_variantes_alternativas`); a ordem do pipeline está em
[`scraper_season2.py:1231`](scraper_season2.py:1231) (`dedupe → seleção → pré-filtro → truncar →
detalhar`); as métricas `variantes_antes_selecao`, `variantes_depois_selecao`, `itens_distintos`
e `selecao_variante` estão em [`scraper_season2.py:1269`](scraper_season2.py:1269); e
`_tentar_variante_alternativa` (marca `variante_alternativa_usada`) está em
[`scraper_season2.py:812`](scraper_season2.py:812). Evidência de execução parcial:
[`data/_diagnostico/f01_demo20.json`](data/_diagnostico/f01_demo20.json:1) contém **8 itens**,
todos com `item_level` em **318–328**, `nome_ptbr` e `icone_url` preenchidos.

### B) O que FALTA — lista numerada, executável por outra IA

> Formato: **ID | Prioridade | O que fazer | Arquivos | Critério de aceite | Depende de**.
> `[x]` = verificado como já conforme; `[ ]` = pendente.

- `[x]` **P-01 (ALTA) — F-01: seleção de variante por item.** **verificado: já conforme**
  (evidência: `TRACKS_SEASON2` em [`config.py:230`](config.py:230),
  `_selecionar_melhores_variantes` em [`scraper_season2.py:718`](scraper_season2.py:718),
  métricas em [`scraper_season2.py:1269`](scraper_season2.py:1269), 7 casos verdes em
  [`tests/test_selecao_variantes.py`](tests/test_selecao_variantes.py:1) e demo com 8 itens em
  318–328). **Resta apenas reexecutar o critério com rede:**
  `python scraper_season2.py --max-itens 20 --max-detalhes 20` → **≥ 15 itens** com
  `item_level` 305–350 e `nome_ptbr`/`icone_url` não vazios. Depende de: nada (só rede).
- `[ ]` **P-02 (ALTA) — Regenerar o JSON/Markdown canônicos após o PKG-2.**
  Evidência atual: [`data/wowhead_itens_season2.json`](data/wowhead_itens_season2.json:1) tem
  **apenas 1 item** (não 24) e esse único item tem `atributos_secundarios` vazio (0/1); os demais
  campos pesquisados (`nome_en`, `icone_url`, `tooltip_raidbots`, `tooltip_raidbots_en`,
  `nome_ptbr_fonte`, `nome_en_fonte`, `icone_fonte`, `atributos_fonte`, `atributos_primarios`)
  estão 1/1. **O que fazer:** após P-01, rodar
  `python scraper_season2.py --max-itens 30 --max-detalhes 30 --qualidade-craft 5`.
  **Arquivos:** [`data/wowhead_itens_season2.json`](data/wowhead_itens_season2.json:1),
  [`data/wowhead_season2.md`](data/wowhead_season2.md:1). **Aceite:** 100% dos itens com os 8
  campos acima não vazios e Markdown com a seção de tooltips. **Depende de:** P-01.
- `[ ]` **P-03 (ALTA) — F-05: enriquecimento por tooltip HTTP no modo `--sem-detalhes`.**
  Evidência: [`scraper_season2.py:927`](scraper_season2.py:927) retorna cedo quando
  `buscar_detalhes` é falso e a CLI desliga tudo em
  [`scraper_season2.py:1481`](scraper_season2.py:1481); o descarte `sem_ilvl` ocorre em
  [`scraper_season2.py:1093`](scraper_season2.py:1093). **O que fazer:** quando
  `max_detalhes == 0`, após dedupe/seleção/pré-filtro, chamar
  `tooltip_client.consultar_tooltip(id, bonus_ids)` por candidato e preencher via `setdefault`
  `nome_ptbr`, `nome_en`, `item_level`, `icone_url`, `atributos_primarios`,
  `atributos_secundarios`, com `atributos_fonte="tooltip_http"`.
  **Arquivos:** [`scraper_season2.py`](scraper_season2.py:1),
  [`tooltip_client.py`](tooltip_client.py:1). **Aceite:**
  `python scraper_season2.py --sem-detalhes --max-itens 200` → **≥ 40 itens** com nome + ilvl +
  ícone + atributos primários. **Depende de:** P-01, P-04.
- `[ ]` **P-04 (MÉDIA) — tooltip_client expor campos completos.**
  Evidência: o retorno atual tem apenas `nome`, `item_level`, `track_rotulo`, `qualidade`
  ([`tooltip_client.py:146`](tooltip_client.py:146), contrato na docstring em
  [`:293`](tooltip_client.py:293)). **O que fazer:** expor `nome_ptbr` (locale 8), `nome_en`
  (locale 0), `icone_url`, `atributos_primarios`, `atributos_secundarios`, `item_level` e
  `bonus_ids`, mantendo cache/TTL e a regra de nunca levantar exceção.
  **Arquivos:** [`tooltip_client.py`](tooltip_client.py:1).
  **Aceite:** teste offline com fixture HTML/JSON de tooltip cobrindo os 7 campos.
  **Depende de:** nada.
- `[ ]` **P-05 (MÉDIA) — F-02: `validar_craft` com a mesma arbitragem de ilvl.**
  Evidência: [`tools/validar_craft.py:39`](tools/validar_craft.py:39) só coleta
  `item_level`; não importa `_arbitrar_ilvl` nem lê `bonus_ids` do JSON canônico.
  **O que fazer:** usar `_arbitrar_ilvl()` e os `bonus_ids` registrados no JSON canônico.
  **Arquivos:** [`tools/validar_craft.py`](tools/validar_craft.py:1),
  [`scraper_season2.py:846`](scraper_season2.py:846) (`_arbitrar_ilvl`).
  **Aceite:** `python tools/validar_craft.py --ids 237831 237839` reporta o mesmo `item_level`
  e `bonus_ids` do JSON canônico. **Depende de:** P-02.
- `[ ]` **P-06 (MÉDIA) — F-08: dataclasses legadas com ícone/nome_en/atributos/tooltip.**
  Evidência: [`scraper_sem_llm.py:49`](scraper_sem_llm.py:49),
  [`:64`](scraper_sem_llm.py:64) e [`:79`](scraper_sem_llm.py:79) não têm `icone`, `nome_en`,
  `atributos_primarios`, `atributos_secundarios` nem `tooltip_raidbots`.
  **O que fazer:** adicionar campos opcionais (`icone: str = ""`, `nome_en: str = ""`,
  `atributos_primarios: dict = field(default_factory=dict)`,
  `atributos_secundarios: dict = field(default_factory=dict)`, `tooltip_raidbots: str = ""`) e
  preencher no adapter; consumir na UI legada.
  **Arquivos:** [`scraper_sem_llm.py`](scraper_sem_llm.py:1),
  [`app_streamlit.py`](app_streamlit.py:1), [`tests/test_sem_llm_adapter.py`](tests/test_sem_llm_adapter.py:1).
  **Aceite:** `asdict` não quebra; UI legada exibe ícone e atributos; contrato atualizado.
  **Depende de:** nada.
- `[ ]` **P-07 (MÉDIA) — F-06: ampliar mapa receita→profissão.**
  **O que fazer:** ampliar o mapa com [`base_conhecimento_ai_studio/craft_receitas_s2.json`](base_conhecimento_ai_studio/craft_receitas_s2.json:1)
  e [`craft_armas_s2.json`](base_conhecimento_ai_studio/craft_armas_s2.json:1) e/ou inferir por
  `subclass`/`slot` marcando `profissao_craft_fonte="inferido"`.
  **Arquivos:** [`wow_season2.py`](wow_season2.py:1),
  [`base_conhecimento_ai_studio/craft_receitas_s2.json`](base_conhecimento_ai_studio/craft_receitas_s2.json:1),
  [`base_conhecimento_ai_studio/craft_armas_s2.json`](base_conhecimento_ai_studio/craft_armas_s2.json:1).
  **Aceite:** ≤ 5 itens em 24 sem `profissao_craft` (métrica só é mensurável após P-02/P-10,
  pois o JSON atual tem 1 item). **Depende de:** P-02.
- `[ ]` **P-08 (MÉDIA) — Objetivo 7 do handoff: `_extrair_com_llm` (DeepSeek como fallback).**
  Evidência: busca textual em todos os `*.py` **não encontrou** `_extrair_com_llm`, `_llm_usado`
  nem `_llm_campos`; só existe `montar_llm_config()` em [`config.py:65`](config.py:65).
  **O que fazer:** implementar em [`wow_season2.py`](wow_season2.py:1) (prompt PT/EN, JSON
  estrito, `_llm_usado`/`_llm_campos`, nunca levantar exceção), chamado **apenas** quando faltar
  `nome_ptbr` E `nome_en`, ou `icone_url`, ou todos os atributos, após esgotar crawl + tooltip
  HTTP; fontes passam a aceitar `"llm"` (as escalas já incluem `"llm"` em
  [`wow_season2.py:931`](wow_season2.py:931)).
  **Aceite:** teste offline com mock de LLM (nenhuma chamada real) e `nome_ptbr_fonte="llm"`
  quando usado. **Depende de:** P-02, P-03, P-04 e da chave DeepSeek (ver seção C).
- `[ ]` **P-09 (MÉDIA) — F-03: habilitar pytest.**
  Evidência: `python -m pytest --version` → `No module named pytest`.
  **O que fazer:** `pip install -r requirements-dev.txt` e rodar `python -m pytest -q`,
  mantendo os runners de fallback. **Arquivos:** [`requirements-dev.txt`](requirements-dev.txt:1).
  **Aceite:** suíte verde sob pytest com a mesma contagem dos runners (104 OK, 2 SKIP).
  **Depende de:** nada.
- `[ ]` **P-10 (BAIXA) — F-07: base canônica maior.**
  **O que fazer:** após P-01, `python scraper_season2.py --max-itens 200 --max-detalhes 50`.
  **Aceite:** ≥ 100 itens de gear e ≥ 30 de catálogo, todos com `tooltip_raidbots` preenchido.
  **Depende de:** P-01, P-02.
- `[ ]` **P-11 (BAIXA) — F-12 restante da base de conhecimento.**
  Resolver §3.10, §3.12 e §3.13 em
  [`base_conhecimento_ai_studio/pendencias.md`](base_conhecimento_ai_studio/pendencias.md:1).
  **Depende de:** nada (dados normativos).
- `[ ]` **P-12 (BAIXA) — Revisar `ignorados` de craft e o campo `historico`.**
  Auditar amostra de `motivo_qualidade_craft` e confirmar que nenhum item craftado real ficou
  com `qualidade_craft=0`. **Depende de:** P-02, P-07.

**Contagem:** **12 itens** (`P-01`…`P-12`) — **1 marcado `[x]`** (P-01, verificado como já
conforme) e **11 marcados `[ ]`**.

### C) Ações manuais do usuário (bloqueantes fora do código)

1. **Revogar/rotacionar a chave Firecrawl** no painel (procedimento em
   [`docs/SEGURANCA.md`](docs/SEGURANCA.md:1)). Nenhuma chave real está em arquivo versionável
   (varredura textual já registrada no F-12/§3.9).
2. Preencher `DEEPSEEK_API_KEY` real em [`.env`](.env:1) (hoje é placeholder
   `your_deepseek_api_key_here`) — **necessário para P-08**.
3. Atualizar `.roo/mcp.json` local (não versionado) usando `${env:...}`.

### D) Ordem de execução recomendada

`P-01 (só revalidar com rede) → P-02 → P-04 → P-03 → P-05 → P-06 → P-07 → P-08 → P-09 → P-10 →
P-11 → P-12`

**Regra de ouro:** após qualquer alteração em [`wow_season2.py`](wow_season2.py:1) ou
[`scraper_season2.py`](scraper_season2.py:1), rodar **todos** os arquivos de `tests/` +
`test_season2.py` (17 arquivos: 104 casos OK / 2 SKIP hoje).

### E) Riscos de estado parcial

- **Nenhum código quebrado:** `scraper_season2.py` compila (exit 0) e os 17 arquivos de teste
  estão verdes.
- **P-01 não está "pela metade":** função, constantes, métricas e 7 casos de teste existem e
  passam. O que falta é apenas a **verificação online** do critério de ≥ 15 itens.
- **Estado de dados inconsistente:** o JSON canônico foi **reduzido a 1 item** (o handoff
  descrevia 24) e esse item tem `atributos_secundarios` vazio. Tratar como "dado precisa ser
  regenerado" (P-02), **não** como bug de parser — `test_campos_obrigatorios.py` (6 OK) cobre o
  contrato e passa. O demo de F-01 em
  [`data/_diagnostico/f01_demo20.json`](data/_diagnostico/f01_demo20.json:1) tem 8 itens válidos
  (318–328) e serve como amostra confiável.
- **Primeiro comando da próxima IA (somente leitura de rede, sem editar nada):**
  `python scraper_season2.py --max-itens 20 --max-detalhes 20`
  → conferir `metadata.variantes_antes_selecao`, `variantes_depois_selecao`, `itens_distintos` e
  `selecao_variante`, e o total de itens em 305–350. Se ≥ 15, marcar P-01 definitivamente como
  concluído e seguir para P-02. Se a rede devolver 403, registrar em `metadata.falhas` e rodar
  `python tools/diagnostico/diag_descartes.py` antes de mexer em código.

---

## Ciclo PKG-6 … PKG-8 — correções aplicadas em 2026-11-06

> Esta seção registra o que foi **implementado e testado** depois da auditoria acima.
> Nenhum item abaixo depende de ação manual, exceto onde indicado.

### Descoberta principal sobre F-01/P-01b

A hipótese de que `bonus`/`quality` na URL de listagem resolveriam F-01 **não se
confirmou empiricamente**. Medição com [`tools/diagnostico/valida_listagem_final.py`](tools/diagnostico/valida_listagem_final.py:1):

- 192 linhas → **50 ids antigos**, `item_level = 0` em todas;
- os `bonus_ids` encontrados (`11215`, `12825`, `12826`, `12827`, ...) são **opções do
  menu de filtros** da página, repetidas por item;
- o Wowhead aplica `ilvl`/`bonus` **client-side**; o crawl headless recebe o banco genérico.

**Correção adotada:** a fonte primária de gear passou a ser uma **lista canônica de IDs**
extraída do banco de loot M+ da base de conhecimento.

### Correções implementadas

| ID | Correção | Arquivos | Evidência |
|---|---|---|---|
| PKG6-1 | `SEASON2_GEAR_IDS` lido de `data/season2_gear_ids.json` (118 ids) | [`config.py:246`](config.py:246), [`tools/gerar_ids_gear_s2.py:1`](tools/gerar_ids_gear_s2.py:1) | artefato com **118 IDs** |
| PKG6-2 | `urls_gear_canonicas(limite)` gera `item=<id>?bonus=12856` | [`config.py:283`](config.py:283) | `12856` → ilvl **341** medido no tooltip |
| PKG6-3 | CLI usa canônicas e respeita `--max-itens` na coleta | [`scraper_season2.py:1519`](scraper_season2.py:1519) | roda 20 ids sem listagem genérica |
| PKG6-4 | UI passa `limite=max_itens` para a categoria de gear | [`app_streamlit.py:1010`](app_streamlit.py:1010) | `montar_categorias_selecionadas(..., limite=N)` |
| PKG6-5 | Listagem genérica mantida **apenas como fallback** | [`config.py:299`](config.py:299) | `SEASON2_ITEM_URLS` documentada como fallback |
| PKG7-1 | Tooltip expõe 12 campos (nome PT/EN, ícone, atributos, bônus, HTML e texto) | [`tooltip_client.py:103`](tooltip_client.py:103), [`tooltip_client.py:186`](tooltip_client.py:186) | 5 casos em [`tests/test_tooltip_client_campos.py`](tests/test_tooltip_client_campos.py:1) |
| PKG7-2 | Cache antigo (4 campos) é ignorado e refeito | [`tooltip_client.py:315`](tooltip_client.py:315) | `test_cache_antigo_incompleto_e_ignorado` |
| PKG7-3 | `tooltip_http` incluído na escala de ícones | [`wow_season2.py:931`](wow_season2.py:931) | `FONTES_ICONE` atualizada |
| PKG7-4 | `enriquecer_por_tooltip()` no modo sem detalhes | [`scraper_season2.py:918`](scraper_season2.py:918) | ≥40 itens no teste; métricas `enriquecidos_tooltip`/`tooltip_falhas` |
| PKG7-5 | `validar_craft` usa `bonus_ids` do canônico | [`tools/validar_craft.py:52`](tools/validar_craft.py:52) | 4 casos em [`tests/test_validar_craft_bonus.py`](tests/test_validar_craft_bonus.py:1) |
| PKG8-1 | Mapa receita→profissão lê IDs usados como **chave** do JSON | [`wow_season2.py:1354`](wow_season2.py:1354) | `237831`/`237839` → **Ferraria**; 103 ids no mapa |
| PKG8-2 | Dataclasses legadas com ícone, nome EN, atributos e tooltip | [`scraper_sem_llm.py:49`](scraper_sem_llm.py:49) | 4 casos em [`tests/test_sem_llm_campos_novos.py`](tests/test_sem_llm_campos_novos.py:1) |
| PKG8-3 | Script de auditoria de `motivo_qualidade_craft` | [`tools/diagnostico/diag_craft_ignorados.py:1`](tools/diagnostico/diag_craft_ignorados.py:1) | roda sobre o canônico e lista reprocessáveis |

### Resultado real da rodada (P-01 e P-02)

`python scraper_season2.py --max-itens 20 --max-detalhes 20` sobre os IDs canônicos:

- `total_itens = 20`, `detalhados = 20`;
- `descartes = {"ilvl_fora": 0, "ilvl_adiado": 20, "sem_ilvl": 0, ...}`;
- `ilvl_origem = {"pagina": 20}`;
- **todos os 20 itens com `item_level = 341`**, dentro da faixa 305–350;
- **100%** dos itens com `nome_en`, `nome_ptbr`, `icone_url`, `tooltip_raidbots`,
  `tooltip_raidbots_en`, `nome_ptbr_fonte`, `nome_en_fonte`, `icone_fonte`,
  `atributos_fonte` e `atributos_primarios`;
- [`data/wowhead_season2.md`](data/wowhead_season2.md:1) regenerado com `Craft (R)` e
  seção de tooltips.

Validação independente por tooltip: **20/20 ids** retornam ilvl em 305–350 com
`bonus=12856` (0 fora da faixa).

### Pendências que continuam abertas

1. **P-10 (volume):** rodar `--max-itens 200 --max-detalhes 50` em terminal externo
   controlado. A rodada de 20 cabe na sessão; 200 pode parecer "travada" por tempo de
   crawl — executar fora do editor, com log em arquivo.
2. **P-09 (`pytest`):** `pip install -r requirements-dev.txt` e comparar com a contagem
   dos runners.
3. **P-08 (fallback LLM):** depende de `DEEPSEEK_API_KEY` real.
4. **P-11 (§3.10/§3.12/§3.13):** validação normativa contra o jogo; revogação da chave
   Firecrawl segue manual.
5. **Risco resolvido:** `_url_detalhe` aplicava `crafting-quality` em qualquer gear
   fora de catálogo. Agora a marca só é emitida com indício de craft
   (`_tem_indicio_craft`): categoria/profissão, `profissao_craft`, `craft_indicio`
   ou ID no mapa receita→profissão. Evidência:
   [`tests/test_url_detalhe_craft.py`](tests/test_url_detalhe_craft.py:1) — **7 OK**.

---

## P-13 — Somente itens R5 e raridade épica (requisito de produto)

> Definido pelo usuário em 2026-11-06: o resultado deve conter **apenas** itens
> craftados no rank máximo (R5) e com raridade **Épico (4)**.

### Implementação

| Peça | Mudança | Arquivo |
|---|---|---|
| Raridade padrão de gear | `QUALIDADE_MINIMA_GEAR_PADRAO = 4` (o fluxo legado de catálogo continua em 3) | [`config.py:222`](config.py:222) |
| Filtro de craft estrito | `exigir_craft=True` descarta `qualidade_craft != qualidade_craft_min`, inclusive `0` | [`scraper_season2.py:1254`](scraper_season2.py:1254) |
| Contador de descarte | `descartes["sem_craft"]` separado de `qualidade_craft` | [`scraper_season2.py:1130`](scraper_season2.py:1130) |
| CLI | `--exigir-craft/--no-exigir-craft` (padrão ligado) e `--qualidade-min` padrão 4 | [`scraper_season2.py:1563`](scraper_season2.py:1563) |
| UI | checkbox “Somente itens craftados no rank acima”, ligado por padrão | [`app_streamlit.py:878`](app_streamlit.py:878) |
| MCP | parâmetro `exigir_craft` (padrão `False` para consulta avulsa) | [`mcp_server.py:206`](mcp_server.py:206) |
| Teste | R5 passa; R4 descarta; `qc=0` descarta; catálogo isento; raridade 3 descarta | [`tests/test_exigir_craft.py`](tests/test_exigir_craft.py:1) |

### Efeito esperado nos dados

Os 20 itens regenerados são **drops de M+ não craftados** (`qualidade_craft=0`).
Com o novo padrão, a rodada com `--exigir-craft` devolveria **0 itens** — o que é
correto para o requisito, mas significa que a lista canônica de gear precisa de uma
fonte de **itens craftados** (não só loot de dungeon) para popular o resultado.

**Implementado:** `data/season2_craft_ids.json` com **112 IDs** gerados por
[`tools/gerar_ids_craft_s2.py`](tools/gerar_ids_craft_s2.py:1). A categoria de gear usa
essa lista quando `exigir_craft` está ligado
(`resolver_urls_categoria(..., somente_craft=True)`). Testes:
[`tests/test_config_urls_craft.py`](tests/test_config_urls_craft.py:1) — **6 OK**.

### Infra de testes

- `pytest` e `pytest-asyncio` instalados; `conftest.py` garante a raiz no `sys.path`.
- Runner [`tools/rodar_testes_offline.py`](tools/rodar_testes_offline.py:1) executa cada
  arquivo em subprocesso com timeout e reporta `OK/FAIL/TIMEOUT` — evita comandos
  aparentemente infinitos quando algum teste faz rede.
- Resultado: **24 arquivos, 0 falhas, 0 timeouts** (sem `test_app_streamlit`, que é o mais
  lento e deve ser rodado à parte).
- `test_max_detalhes` agora mocka `consultar_tooltip` no modo sem detalhes: sem isso, o
  enriquecimento fazia chamadas reais com backoff (2s/4s/8s por item) e parecia travado.
- Contagem final: **148 passed, 2 skipped** (25 arquivos em `tests/`), mais `test_season2.py`
  verde no runner próprio.

### Fallback LLM (P-08)

- Implementado em [`wow_season2.py:2198`](wow_season2.py:2198):
  `faltando_campos_llm()`, `_extrair_com_llm()` e `aplicar_llm_em_item()`.
- Chamada real opcional via `crawl4ai.perform_completion` + `config.montar_llm_config()`;
  `completar` é injetável, então os testes rodam **sem rede e sem chave**.
- Nunca levanta exceção: falha registra `_llm_erro`; sucesso grava
  `nome_ptbr_fonte="llm"`, `nome_en_fonte="llm"`, `icone_fonte="llm"`,
  `atributos_fonte="llm"`, `_llm_usado` e `_llm_campos`.
- Regra: só é acionado quando falta nome (ambos), ícone ou todos os atributos, e
  **nunca sobrescreve** dado já extraído.
- Testes: [`tests/test_llm_fallback.py`](tests/test_llm_fallback.py:1) — **8 OK**.

### Validação ao vivo de craft R5

`python tools/validar_craft.py --ids 237831 --sem-ingles` após o fallback de bônus:

```text
id=237831 | nome=Repreensão do Quebra-feitiço | qualidade=4 | qualidade_craft=5
fonte=url:crafting-quality | motivo=url:crafting-quality
profissao_craft=Ferraria | item_level=341
Critério (R5 + fonte URL + profissão): 1/1 ok
```

Relatório: [`data/_diagnostico/craft_237831.json`](data/_diagnostico/craft_237831.json:1).
Isso confirma o requisito **somente R5 + Épico** e resolve a divergência de ilvl do F-02
(antes 246; agora 341, igual ao pipeline).

### Varredura de volume em background (P-10)

Launcher: [`tools/iniciar_varredura_bg.py`](tools/iniciar_varredura_bg.py:1) —
usa `sys.executable` + `CREATE_NEW_PROCESS_GROUP` (o `DETACHED_PROCESS` matava o
`python.exe` do WindowsApps neste ambiente). Logs:
`data/_diagnostico/varredura_craft.out` e `.err`.

Comando: `--max-itens 120 --max-detalhes 100 --qualidade-craft 5 --exigir-craft`.

**Resultado real:** **9 itens finais** (de 112 URLs), todos com:

- `qualidade = 4` (Épico);
- `qualidade_craft = 5` (R5);
- `profissao_craft` preenchida;
- `item_level = 341`;
- `metadata.filtros.exigir_craft = true`.

O requisito de qualidade foi cumprido em **9/9**. O volume ficou abaixo de 100 por
**bloqueio do site**, não por defeito do filtro:

- `circuit_breaker` abortou após **5 falhas consecutivas** de 403/desafio anti-bot;
- **28 falhas** no total, incluindo `ERR_NAME_NOT_RESOLVED` do Chromium;
- apenas 11 brutos coletados antes do aborto.

Para nova tentativa de volume: aguardar o bloqueio e rodar o launcher novamente. O JSON
canônico já está consistente com o requisito R5/Épico.

### MCP validado (2026-11-06)

- `mcp 1.30.0` instalado; `python mcp_server.py --selftest` e `--print-config` OK.
- Teste de protocolo via stdio em [`tools/testar_mcp_stdio.py`](tools/testar_mcp_stdio.py:1):
  `initialize` OK, **6 tools** expostas e `call_tool(estado_dados)` retornando o estado real.
  Tools: `estado_dados`, `listar_catalogo`, `recomendar_encantamento_gema`,
  `scrape_pagina`, `scrape_wowhead_item`, `scrape_wowhead_items`.
- Config do VS Code criada em [`.vscode/mcp.json`](.vscode/mcp.json:1) (stdio,
  `PYTHONIOENCODING=utf-8`, `PYTHONPATH` da raiz).
- Para o Roo/Cline, a escrita em `.roo/` é bloqueada pelo ambiente. Gere o JSON no
  formato aceito e cole na UI: `python mcp_server.py --print-config --formato=roo`
  (chave `mcpServers`, **sem `cwd`**; o schema do Roo rejeita campos extras).
  Também há `--formato=vscode` e `--formato=bloco`.
- Guia completo por cliente: [`docs/MCP_ATIVACAO.md`](docs/MCP_ATIVACAO.md:1).
- Após criar/alterar a config, o editor precisa recarregar a janela ou reiniciar o
  servidor MCP para reconectar.
