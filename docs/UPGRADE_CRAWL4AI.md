# Upgrade do Crawl4AI — checklist de migração

Documento de referência citado por [`tests/test_contrato_crawl4ai.py`](../tests/test_contrato_crawl4ai.py:1).

## Versão validada

| Componente | Versão | Onde está fixado |
| --- | --- | --- |
| Python | 3.12.x | — |
| Crawl4AI | **0.8.6** (pin exato) | [`requirements.txt`](../requirements.txt:1) |
| Playwright | **1.58.0** (pin exato) | [`requirements.txt`](../requirements.txt:1) |
| Chromium (Playwright) | build baixado por `playwright install chromium` | — |
| beautifulsoup4 | 4.13.x (`>=4.12,<5`) | [`requirements.txt`](../requirements.txt:1) |
| lxml | 5.4.x (transitivo) | — |
| pandas | 2.3.x (`>=2.0,<3`) | [`requirements.txt`](../requirements.txt:1) |

> **Por que pin exato em `crawl4ai` e `playwright`?**
> O teto antigo (`crawl4ai>=0.5.0`, sem limite superior) permitiu que o ambiente
> derivasse para 0.8.6, onde `JsonCssExtractionStrategy` passou a exigir
> `schema` como 1º argumento posicional. O projeto usava `css_selectors=`,
> recebia `TypeError: __init__() missing 1 required positional argument: 'schema'`
> e a exceção era engolida — o usuário só via "0 itens".

## Contrato de API atual (0.8.6)

```python
from crawl4ai import JsonCssExtractionStrategy, LLMExtractionStrategy, CrawlerRunConfig

JsonCssExtractionStrategy(schema: dict, **kwargs)          # schema é OBRIGATÓRIO e 1º
LLMExtractionStrategy(llm_config=..., instruction=..., ...) # llm_config aceito
CrawlerRunConfig(wait_for=..., js_code=..., page_timeout=...)  # campos disponíveis
```

Verificado automaticamente por:

- `test_versao_crawl4ai_pinada` — `crawl4ai.__version__` (string) == `0.8.6`;
- `test_json_css_exige_schema_e_nao_aceita_css_selectors` — `schema` é o 1º
  parâmetro, obrigatório, posicional; `css_selectors` não existe na assinatura;
  instanciar só com `css_selectors` levanta `TypeError`;
- `test_llm_extraction_aceita_llm_config` — `llm_config` presente;
- `test_crawler_run_config_aceita_campos_do_pipeline` — `wait_for`, `js_code`,
  `page_timeout` presentes.

> Detalhe: em 0.8.x `crawl4ai.__version__` é o **módulo** `crawl4ai/__version__.py`.
> A string está em `crawl4ai.__version__.__version__`. O teste trata os dois casos.

## Checklist de migração (executar em ordem)

### 1. Diagnóstico antes de mexer

- [ ] `python -c "import crawl4ai, sys; print(getattr(crawl4ai.__version__, '__version__', crawl4ai.__version__)); print(sys.version)"`
- [ ] `python -m pip list | findstr /I "crawl4ai playwright beautifulsoup4 lxml pandas"`
- [ ] `python -m pytest -q tests/test_contrato_crawl4ai.py` (deve estar **verde** antes do upgrade também — é a linha de base)

### 2. Ajustar pinos

- [ ] Atualizar `crawl4ai==<nova versão>` em [`requirements.txt`](../requirements.txt:1)
- [ ] Atualizar `playwright==<nova versão>` **casando com a versão exigida pelo crawl4ai**
- [ ] Manter tetos de próxima major nas dependências já presentes
- [ ] Conferir `requirements-dev.txt` aponta para o principal (`-r requirements.txt`)

### 3. Reinstalar browser do Playwright

- [ ] `python -m playwright install chromium`
- [ ] (CI/Linux) `python -m playwright install --with-deps chromium`
- [ ] Validar: `python -c "import playwright; print(playwright.__version__)"`
  (a versão do pacote deve ser a pinada; o build do Chromium vem do `install`)

### 4. Migrar assinaturas de estratégias

- [ ] `JsonCssExtractionStrategy(css_selectors={...})` → `JsonCssExtractionStrategy({"name": ..., "baseSelector": ..., "fields": [...]})`
- [ ] Substituir seletores "planos" por `fields` com `selector`/`type` (`text`, `attribute`, `nested`, ...)
- [ ] Trocar `provider`/`api_token` por `LLMConfig(provider=..., api_token=...)` em `LLMExtractionStrategy(llm_config=...)`
- [ ] `AsyncWebCrawler.arun(...)` deve receber configuração em `CrawlerRunConfig`, não como kwargs soltos
- [ ] Verificar renomeações de flags: `verbose`, `magic`, `wait_for`, `js_code`, `scan_full_page`, `page_timeout`

### 5. Rodar a suíte

- [ ] `python -m pytest -q tests/test_contrato_crawl4ai.py`
- [ ] `python -m pytest -q tests/test_smoke_offline.py`
- [ ] `python -m pytest -q test_season2.py` (ou `python test_season2.py`)
- [ ] `python -m py_compile scraper_sem_llm.py scraper_season2.py wow_season2.py config.py`

### 6. Smoke real (obrigatório antes de commitar o bump)

- [ ] Rodar o pipeline real e confirmar **pelo menos 2 itens extraídos** com
      `id`, `nome`, `ilvl` e `qualidade` preenchidos:

```bash
python scraper_season2.py --max-itens 2
```

- [ ] Conferir no JSON gerado em `data/` que `metadata.total_itens >= 2`
- [ ] Conferir que não há traceback em `stderr` e que o exit code é `0`

## Critério de aceite

**Só subir a versão com:**

1. `tests/test_contrato_crawl4ai.py` **verde** na versão nova; **e**
2. **smoke real de 2 itens** válidos (não basta teste offline).

Se qualquer um dos dois falhar, voltar o pin para `crawl4ai==0.8.6` /
`playwright==1.58.0` e reabrir a análise — não deixar a versão "meio migrada".

## Erros conhecidos e onde aparecem

| Erro | Causa | Onde |
| --- | --- | --- |
| `TypeError: __init__() missing 1 required positional argument: 'schema'` | `JsonCssExtractionStrategy(css_selectors=...)` na API antiga | [`scraper_sem_llm.py`](../scraper_sem_llm.py:180) |
| `Executable doesn't exist at ...chromium...` | browser do Playwright não instalado / versão divergente | ambiente |
| `0 itens` sem traceback | exceção de configuração engolida em `except Exception` | corrigido pelo Pacote 1 (agora `logging.exception` + re-raise + exit != 0) |
