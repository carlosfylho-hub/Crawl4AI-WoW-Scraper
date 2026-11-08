#!/usr/bin/env python3
"""
Testes offline de integridade de variante/ilvl (Pacote 2).

Nenhum teste toca a rede: o tooltip é injetado/mockado e o cache usa um
diretório temporário.

Cobrem:
- `consultar_tooltip` lê o JSON, grava/lê cache e degrada para `None`;
- `_url_detalhe` usa `bonus_ids` e NÃO emite `ilvl=`;
- arbitragem tooltip > página > listagem em `detalhar_itens`;
- item 268265 -> 344 e item 252258 -> 334 (tooltip mockado).

Execução:
    python -m pytest -q tests/test_variante_ilvl.py
    python tests/test_variante_ilvl.py        # fallback sem pytest
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


def _html_item(nome: str, ilvl: int) -> str:
    return f"""
    <html><body>
      <h1 class="heading-size-1 q4">{nome}</h1>
      <div id="main-contents">
        <div class="wowhead-tooltip">
          <div class="text">{nome}
Nível do Item: {ilvl}</div>
        </div>
      </div>
    </body></html>
    """


def _scraper_com_pagina(ilvl_pagina: int, **kwargs):
    from scraper_season2 import WowheadSeason2Scraper

    opcoes = {
        "buscar_detalhes": True,
        "buscar_ingles": False,
        "max_detalhes": None,
        "qualidade_min": 0,
    }
    opcoes.update(kwargs)
    scraper = WowheadSeason2Scraper(**opcoes)

    async def fake_crawl(item, locale):
        nome = item.get("nome") or "Item"
        return ("https://www.wowhead.com/pt/item=" + str(item.get("id")), _html_item(nome, ilvl_pagina), [])

    scraper._crawl_locale = fake_crawl
    return scraper


# ---------------------------------------------------------------------------
# tooltip_client
# ---------------------------------------------------------------------------

def test_tooltip_json_direto_e_cache() -> None:
    from tooltip_client import TooltipCache, consultar_tooltip

    chamadas = {"n": 0}

    def fetch(url, timeout):
        chamadas["n"] += 1
        assert "nether.wowhead.com/tooltip/item/268265" in url, url
        assert "bonus=13668:13987" in url or "bonus=13987:13668" in url, url
        return json.dumps(
            {
                "name": "Relicário Aqiricida",
                "quality": 4,
                "itemLevel": 344,
                "tooltip": "<b>Relicário Aqiricida</b> Item Level 344 Myth 6/6",
            }
        )

    with tempfile.TemporaryDirectory() as tmp:
        caminho = os.path.join(tmp, "tooltips.json")
        cache = TooltipCache(caminho)
        dados = consultar_tooltip(
            "268265", ["13668", "13987"], cache=cache, fetch=fetch
        )
        assert dados is not None
        assert dados["item_level"] == 344, dados
        assert dados["nome"] == "Relicário Aqiricida"
        assert "Myth" in dados["track_rotulo"], dados
        assert chamadas["n"] == 1

        # Segunda consulta (bonus em outra ordem) deve sair do cache.
        cache2 = TooltipCache(caminho)
        dados2 = consultar_tooltip(
            "268265", ["13987", "13668"], cache=cache2, fetch=fetch
        )
        assert dados2 is not None and dados2["item_level"] == 344
        assert chamadas["n"] == 1, "cache não foi usado"


def test_tooltip_falha_retorna_none() -> None:
    from tooltip_client import TooltipCache, consultar_tooltip

    def fetch(url, timeout):
        raise RuntimeError("rede indisponível")

    with tempfile.TemporaryDirectory() as tmp:
        cache = TooltipCache(os.path.join(tmp, "tooltips.json"))
        assert consultar_tooltip("1", None, cache=cache, fetch=fetch) is None


def test_tooltip_html_fallback() -> None:
    from tooltip_client import TooltipCache, consultar_tooltip

    def fetch(url, timeout):
        return "<table><tr><td>Garra Talassiana</td></tr><tr><td>Item Level 334</td></tr></table>"

    with tempfile.TemporaryDirectory() as tmp:
        cache = TooltipCache(os.path.join(tmp, "tooltips.json"))
        dados = consultar_tooltip("252258", ["13668"], cache=cache, fetch=fetch)
        assert dados is not None
        assert dados["item_level"] == 334, dados


# ---------------------------------------------------------------------------
# URL de detalhe
# ---------------------------------------------------------------------------

def test_url_detalhe_nao_emite_ilvl() -> None:
    from scraper_season2 import WowheadSeason2Scraper

    scraper = WowheadSeason2Scraper(buscar_detalhes=False)
    url = scraper._url_detalhe(
        {
            "id": "268265",
            "item_level": 344,
            "bonus_ids": ["13668", "13987"],
            "_categoria": "gear",
        }
    )
    assert "ilvl=" not in url, url
    assert "bonus=13668:13987" in url, url
    # Item de drop sem indício de craft NÃO recebe crafting-quality.
    assert "crafting-quality=" not in url, url


def test_url_detalhe_catalogo_sem_crafting_quality() -> None:
    from scraper_season2 import WowheadSeason2Scraper

    scraper = WowheadSeason2Scraper(buscar_detalhes=False)
    url = scraper._url_detalhe(
        {"id": "999", "bonus_ids": [], "_categoria": "gema"}
    )
    assert "ilvl=" not in url, url
    assert "crafting-quality=" not in url, url


# ---------------------------------------------------------------------------
# Arbitragem tooltip > página > listagem
# ---------------------------------------------------------------------------

def test_arbitragem_item_268265_usa_tooltip() -> None:
    scraper = _scraper_com_pagina(ilvl_pagina=219)
    itens = [
        {
            "id": "268265",
            "nome": "Relicário Aqiricida",
            "item_level": 219,
            "bonus_ids": ["13668", "13987"],
            "variante_fonte": "listagem",
            "url": "",
            "_contexto": "",
        }
    ]
    tooltip = {
        "nome": "Relicário Aqiricida",
        "item_level": 344,
        "track_rotulo": "Myth 6/6",
        "qualidade": 4,
    }
    with patch("scraper_season2.consultar_tooltip", return_value=tooltip) as mock:
        resultado = asyncio.run(scraper.detalhar_itens(itens))

    assert resultado[0]["item_level"] == 344, resultado[0]
    assert resultado[0]["_ilvl_origem"] == "tooltip", resultado[0]
    assert resultado[0]["_ilvl_conflito"] is True, resultado[0]
    assert mock.called


def test_arbitragem_item_252258_usa_tooltip() -> None:
    scraper = _scraper_com_pagina(ilvl_pagina=28)
    itens = [
        {
            "id": "252258",
            "nome": "Garra Talassiana",
            "item_level": 28,
            "bonus_ids": ["13668"],
            "variante_fonte": "listagem",
            "url": "",
            "_contexto": "",
        }
    ]
    tooltip = {
        "nome": "Garra Talassiana",
        "item_level": 334,
        "track_rotulo": "Myth 6/6",
        "qualidade": 4,
    }
    with patch("scraper_season2.consultar_tooltip", return_value=tooltip):
        resultado = asyncio.run(scraper.detalhar_itens(itens))

    assert resultado[0]["item_level"] == 334, resultado[0]
    assert resultado[0]["_ilvl_origem"] == "tooltip"


def test_caminho_feliz_nao_consulta_tooltip() -> None:
    scraper = _scraper_com_pagina(ilvl_pagina=320)
    itens = [
        {
            "id": "123456",
            "nome": "Item Feliz",
            "item_level": 320,
            "bonus_ids": ["111"],
            "variante_fonte": "listagem",
            "url": "",
            "_contexto": "",
        }
    ]
    with patch("scraper_season2.consultar_tooltip") as mock:
        resultado = asyncio.run(scraper.detalhar_itens(itens))

    assert not mock.called, "tooltip não deveria ser chamado no caminho feliz"
    assert resultado[0]["item_level"] == 320
    assert resultado[0]["_ilvl_origem"] == "pagina"


if __name__ == "__main__":  # pragma: no cover - fallback sem pytest
    import traceback

    falhas = 0
    for nome, funcao in sorted(globals().items()):
        if not (nome.startswith("test_") and callable(funcao)):
            continue
        try:
            funcao()
        except Exception:  # noqa: BLE001 - relatório simples
            falhas += 1
            print(f"[FAIL] {nome}")
            traceback.print_exc()
        else:
            print(f"[OK] {nome}")
    print(f"\n{'FALHAS' if falhas else 'SUCESSO'}: {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
