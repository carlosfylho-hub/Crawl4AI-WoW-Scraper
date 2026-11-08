# PACOTE 3 — Plano de Implementação (Sem LLM, provider LLM e entrypoints)

## Diagnóstico a corrigir
- **RC-2**: `JsonCssExtractionStrategy(css_selectors=...)` (API 0.8.6 exige `schema`). Ocorre em `scraper_sem_llm.py` (3 pontos) → `TypeError` → "0 itens".
- **RC-3**: `provider="deepseek"` (litellm exige `deepseek/deepseek-chat`) e `config=` em vez de `llm_config=` em `scraper.py`.
- Fluxo "Sem LLM" retorna 0 itens; menu 2 e `run_scraper.py` usam scraper LLM legado quebrado.

## Decisões de arquitetura
1. **Novo módulo `coleta.py`** (em vez de alterar `wow_season2.py`):
   - `wow_season2.py` está com restrição de escopo (não alterar lógica de variante/ilvl já corrigida).
   - `coleta.py` concentra a fronteira de rede (Crawl4AI) e reutiliza os parsers canônicos, mantendo `wow_season2.py` como biblioteca pura de parsing.
2. **`scraper_sem_llm.py` como adapter fino**:
   - Mantém as assinaturas públicas atuais (`extrair_ferramentas_parte`, `extrair_encantamentos`, `extrair_missivas`, `executar_scraping_completo`, `salvar_resultados_completos`) e o formato `{parteN_*: [...]}` consumido por `app_streamlit.py`.
   - Converte os `dict` canônicos para as dataclasses existentes.
3. **Sem schema JSON-CSS novo**: reutilizar `parse_links_itens`, `parse_item_unico`, `extrair_detalhes_item`, `finalizar_item_bilingue`.

## Etapas de implementação

### 1) `config.py` — provider LLM
- `_PROVIDER_LLM_PADRAO = "deepseek/deepseek-chat"`.
- `normalizar_provider(valor)`: vazio → default; `deepseek` → `deepseek/deepseek-chat`; `fornecedor/modelo` → mantém.
- `LLM_PROVIDER = normalizar_provider(os.getenv("LLM_PROVIDER", default))`.
- `LLM_MODEL = os.getenv("LLM_MODEL", LLM_PROVIDER)`.
- `montar_llm_config(api_token=None, **kwargs)`: import tardio de `crawl4ai.LLMConfig`, lê `DEEPSEEK_API_KEY` do `.env`, **nunca imprime o token**.

### 2) `coleta.py` — nova fronteira de rede
- `itens_de_html(url, html, categoria="")` (puro, testável offline):
  - URL de item (`item=\d+`) → `parse_item_unico` + `extrair_detalhes_item`; fallback `parse_links_itens`.
  - Listagem/guia → `parse_links_itens`; fallback `parse_item_unico`.
  - Para cada bruto: injeta `_categoria`, `_pagina`, `url` e chama `finalizar_item_bilingue`.
- `extrair_itens_de_url(url, categoria="", crawler=None)`:
  - Usa `AsyncWebCrawler` + `CrawlerRunConfig` (com fallback de kwargs por `TypeError`, como em `scraper_season2.py`).
  - Se `crawler` for fornecido (adapter), reutiliza; senão abre contexto próprio.
  - `arun` **sem** `extraction_strategy`. Falha de crawl → `RuntimeError` (ruidoso).
  - Retorna `List[dict]`.

### 3) `scraper_sem_llm.py` — adapter fino
- Remover `JsonCssExtractionStrategy` e `css_selectors` (imports e usos).
- Conversores de dict → dataclass:
  - `dict_para_ferramenta(d, *, url="", profissao="")`
  - `dict_para_encantamento(d, *, url="", profissao="")`
  - `dict_para_missiva(d, *, url="", profissao="")`
  - Campos: `id_completo` (fallback `item=..&bonus=..`), `nome_ptbr`, `profissao_craft`, `qualidade_nome`/`qualidade`, `item_level`, `rank`, primeiro atributo (secundário > primário), `bonus_ids`, `url`.
- `extrair_ferramentas_parte(urls, parte_num)`: para cada URL chama `extrair_itens_de_url(..., crawler=self.crawler)`; converte; aplica filtro; conta erros por parte.
- `extrair_encantamentos` / `extrair_missivas`: idem, sem filtro de rank.
- Erros: `TypeError/AttributeError/ImportError` propagam (configuração); demais exceções → `logging.exception` + `_registrar_erro` (não fatal).
- Manter `_registrar_erro`, `_resumo_erros`, `_total_erros`, metadata `erros_por_parte` e `total_erros`.
- Filtro canônico (`_passa_filtros_dict`): qualidade ≥ `QUALIDADE_MIN` (default `QUALIDADE_MINIMA_PADRAO`), ilvl dentro de `ILVL_MIN..ILVL_MAX` quando conhecido, rank só quando informado.
- Atualizar textos de docstring/prints ("parsers canônicos", não "CSS selectors").

### 4) RC-3 — provider e `llm_config`
- `scraper.py`: `provider=LLM_PROVIDER` + `config=` → `llm_config=` nos 3 usos.
- `scraper_completo.py`, `scraper_completo_final.py`, `test_profession_extraction.py`: `provider=LLM_PROVIDER` (import de `config` com fallback para `deepseek/deepseek-chat`).
- Aceite: busca por `provider="deepseek"` → 0 ocorrências.

### 5) Entrypoints
- `iniciar_sistema.py` opção 2: subprocess `scraper_season2.py`.
- `iniciar_sistema.py` opção 3: mantém `scraper_sem_llm.py` (já corrigido); textos atualizados.
- `run_scraper.py`: importar e executar `WowheadSeason2Scraper.executar()` (pipeline S2), mantendo compatibilidade; remover imports de `scraper.py`.
- Atualizar `show_documentation` para apontar o pipeline S2.

### 6) Testes (pytest + fallback `__main__` com `[OK]/[FAIL]`)
- `tests/test_imports.py`: importa `app_streamlit`, `iniciar_sistema`, `scraper_season2`, `scraper_sem_llm`, `mcp_server`; asserta que `scraper`, `scraper_completo`, `scraper_completo_final` **não** estão em `sys.modules`.
- `tests/test_sem_llm_adapter.py`:
  - Fixtures HTML inline de listagem e de item.
  - Monkeypatch de `scraper_sem_llm.AsyncWebCrawler` (FakeCrawler) devolvendo `html`/`success`.
  - Spy em `crawl4ai.JsonCssExtractionStrategy` provando **0** instanciações.
  - Asserta que o fluxo usa `parse_links_itens`/`finalizar_item_bilingue` (resultado com `nome_ptbr`, `id_completo`).
  - Asserta contagem de erros por parte quando o crawler falha.

## Validação obrigatória (reportar saída real)
1. `python -m py_compile` nos arquivos alterados/criados.
2. `python test_season2.py` → "Todos os testes da Season 2 passaram."
3. `python tests/test_imports.py`.
4. `python tests/test_contrato_crawl4ai.py`.
5. Busca: `provider="deepseek"` → 0; `css_selectors=` → 0.
6. `python tests/test_sem_llm_adapter.py`.
7. Se a rede permitir: `python scraper_sem_llm.py` com limites mínimos; caso 403/anti-bot, registrar como limitação de rede.

## Restrições respeitadas
- Não alterar `wow_season2.py` (lógica de variante/ilvl), `scraper_season2.py`, `mcp_server.py`, README.
- Não instalar pacotes, não apagar arquivos, sem scraping obrigatório na validação.
