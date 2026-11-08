# Dados do projeto

Este diretório guarda as saídas do scraper. Para evitar confusão entre a
pipeline **Season 2** (atual) e os scrapers **legados** (partes 1–5), os
arquivos foram separados em canônicos, gerados pelo fluxo "Sem LLM" e legados.

## Canônicos (usados pelo app, CLI e MCP)

| Arquivo | Conteúdo |
| --- | --- |
| `season2_gear_ids.json` | IDs canônicos de gear da Season 2 (fonte primária de coleta, gerada por [`tools/gerar_ids_gear_s2.py`](../tools/gerar_ids_gear_s2.py:1)). |
| `season2_craft_ids.json` | IDs de **itens craftados** da Season 2 (usado quando `exigir_craft` está ligado; gerado por [`tools/gerar_ids_craft_s2.py`](../tools/gerar_ids_craft_s2.py:1)). |
| `wowhead_itens_season2.json` | Gear da Season 2 com `qualidade_craft`, `qualidade_craft_fonte` e `profissao_craft`. |
| `wowhead_season2.md` | Mesmo gear em Markdown, com a coluna `Craft (R)` (`R5` ou `—`). |
| `wowhead_catalogo.json` | Catálogo consolidado (gemas, encantamentos, missivas e consumíveis). |
| `wowhead_catalogo.md` | Catálogo consolidado em Markdown. |
| `wowhead_gemas.json` | Gemas raspadas. |
| `wowhead_encantamentos.json` | Encantamentos raspados. |
| `wowhead_missivas.json` | Missivas raspadas. |

## Saídas do fluxo "Sem LLM" (mantidas para diagnóstico)

Arquivos com timestamp, gerados por `scraper_sem_llm.py`:

- `wowhead_all_items_sem_llm_*.json`
- `wowhead_ferramenta_profissao_sem_llm_*.json`
- `wowhead_encantamento_sem_llm_*.json`
- `wowhead_missiva_sem_llm_*.json`

Podem ser úteis para comparar diffs entre execuções. Não são lidos pelo app.

**Retenção (F-11):** após cada gravação, [`scraper_sem_llm.py`](../scraper_sem_llm.py:586)
chama `rotacionar_artefatos` ([`scraper_season2.py:76`](../scraper_season2.py:76)), que mantém
os **5** arquivos mais recentes de cada padrão e nunca remove os canônicos listados acima.
Para uma limpeza pontual mais agressiva, rode:

```python
from scraper_season2 import rotacionar_artefatos
rotacionar_artefatos("*_sem_llm_*.json", manter=2)
```

## Legados (`data/_legacy/`)

Arquivos de versões antigas dos scrapers com LLM. **Não** são lidos pelos
entrypoints ativos; ficam preservados apenas para consulta histórica:

- `wowhead_all_items.json`
- `wowhead_encantamento.json`
- `wowhead_ferramenta_profissao.json`
- `wowhead_missiva.json`

## Outros diretórios

- `_cache/` — cache de tooltips (`tooltips.json`).
- `_diagnostico/` — apenas **relatórios** de diagnóstico (ex.: `craft.json`). Os scripts
  (`diag_*.py`, `valida_*.py`, `extract_ids.py`) foram movidos para
  [`tools/diagnostico/`](../tools/diagnostico/__init__.py:1) e gravam suas saídas aqui.
  Nenhum `.py` deve ficar nesta pasta.
