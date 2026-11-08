#!/usr/bin/env python3
"""Teste de integração offline do **filtro de qualidade de craft** (Pacote 4).

Cobre a pendência 4 sobre o filtro real em
[`scraper_season2.py`](../scraper_season2.py:613):

a) item craftado com `qualidade_craft=4` e `qualidade_craft_min=5` é
   descartado, incrementando `descartes["qualidade_craft"]`;
b) item **não** craftado (`qualidade_craft=0`) continua passando com
   `qualidade_craft_min=5`;
c) item de catálogo (gema/missiva/encantamento) nunca recebe
   `crafting-quality` na URL de detalhe e não é filtrado por craft.

O teste usa o pipeline de produção: `extrair_detalhes_item` (HTML fixture) →
`_finalizar` (filtros) → `_url_detalhe` (URL de detalhe).

Execução:
    python -m pytest -q tests/test_integracao_filtro_craft.py
    python tests/test_integracao_filtro_craft.py     # fallback sem pytest
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from scraper_season2 import WowheadSeason2Scraper  # noqa: E402
from wow_season2 import extrair_detalhes_item  # noqa: E402


HTML_GEAR_CRAFTADO = """
<html><body>
  <h1 class="heading-size-1 q4">Elmo de Teste</h1>
  <div class="wowhead-tooltip">
    <div>Nível do Item: 341</div>
    <div>Cabeça</div>
    <div>Armadura de Placa</div>
    <div>Qualidade de criação: 4</div>
    <a href="/pt/professions/blacksmithing">Ferraria</a>
  </div>
</body></html>
"""

HTML_GEAR_NAO_CRAFTADO = """
<html><body>
  <h1 class="heading-size-1 q4">Peitoral de Teste</h1>
  <div class="wowhead-tooltip">
    <div>Nível do Item: 341</div>
    <div>Peito</div>
    <div>Armadura de Placa</div>
    <div>Item de qualidade superior, sem indicação de craft.</div>
  </div>
</body></html>
"""


def _bruto(html: str, item_id: str, url: str, categoria: str = "Geral") -> Dict[str, Any]:
    """Monta o bruto como o scraper entrega a `_finalizar`."""
    base = {
        "id": item_id,
        "nome": "",
        "item_level": 0,
        "qualidade": 0,
        "bonus_ids": [],
        "url": url,
        "_pagina": url,
        "_categoria": categoria,
    }
    pt = extrair_detalhes_item(html, base)
    bruto = dict(base)
    bruto["_pt"] = pt
    bruto["_en"] = {}
    bruto["url_en"] = ""
    return bruto


def _scraper() -> WowheadSeason2Scraper:
    return WowheadSeason2Scraper(
        qualidade_craft_min=5,
        ilvl_min=305,
        ilvl_max=350,
        qualidade_min=3,
        gerar_markdown=False,
        buscar_detalhes=True,
    )


def test_craftado_r4_descartado_com_minimo_5() -> None:
    scraper = _scraper()
    bruto = _bruto(
        HTML_GEAR_CRAFTADO,
        "250101",
        "https://www.wowhead.com/pt/item=250101?crafting-quality=4",
    )

    finais = scraper._finalizar([bruto])

    assert finais == [], f"item R4 deveria ser descartado com mínimo 5: {finais}"
    assert scraper.descartes["qualidade_craft"] == 1, scraper.descartes


def test_nao_craftado_passa_com_minimo_5() -> None:
    scraper = _scraper()
    bruto = _bruto(
        HTML_GEAR_NAO_CRAFTADO,
        "250102",
        "https://www.wowhead.com/pt/item=250102",
    )

    finais = scraper._finalizar([bruto])

    assert len(finais) == 1, f"item não craftado deveria passar: {finais}"
    assert finais[0]["qualidade_craft"] == 0, finais[0]
    assert scraper.descartes["qualidade_craft"] == 0, scraper.descartes


def test_filtro_com_os_dois_itens_juntos() -> None:
    scraper = _scraper()
    brutos = [
        _bruto(
            HTML_GEAR_CRAFTADO,
            "250101",
            "https://www.wowhead.com/pt/item=250101?crafting-quality=4",
        ),
        _bruto(
            HTML_GEAR_NAO_CRAFTADO,
            "250102",
            "https://www.wowhead.com/pt/item=250102",
        ),
    ]

    finais = scraper._finalizar(brutos)

    assert len(finais) == 1, finais
    assert str(finais[0]["id"]) == "250102", finais[0]
    assert scraper.descartes["qualidade_craft"] == 1, scraper.descartes


def test_catalogo_sem_crafting_quality_e_sem_filtro_craft() -> None:
    scraper = _scraper()
    casos: List[Dict[str, Any]] = [
        {"id": "2", "_categoria": "Gemas"},
        {"id": "3", "_categoria": "Missivas (tipos)"},
        {"id": "4", "_categoria": "Encantamentos"},
    ]

    for caso in casos:
        url = scraper._url_detalhe(caso, "ptbr")
        assert "crafting-quality" not in url, f"{caso['_categoria']}: {url}"

    # Catálogo entra em `_finalizar` sem ser filtrado por craft nem por ilvl.
    itens_catalogo: List[Dict[str, Any]] = [
        {
            "id": "900001",
            "nome": "Gema de Teste",
            "item_level": 0,
            "qualidade": 3,
            "bonus_ids": [],
            "url": "https://www.wowhead.com/pt/item=900001",
            "_pagina": "https://www.wowhead.com/pt/item=900001",
            "_categoria": "Gemas",
            "_pt": {
                "nome": "Gema de Teste",
                "item_level": 0,
                "qualidade": 3,
                "_contexto": "Gema de Teste\nGema",
            },
            "_en": {},
        },
        {
            "id": "900002",
            "nome": "Missiva de Teste",
            "item_level": 0,
            "qualidade": 3,
            "bonus_ids": [],
            "url": "https://www.wowhead.com/pt/item=900002",
            "_pagina": "https://www.wowhead.com/pt/item=900002",
            "_categoria": "Missivas (tipos)",
            "_pt": {
                "nome": "Missiva de Teste",
                "item_level": 0,
                "qualidade": 3,
                "_contexto": "Missiva de Teste\nMissiva",
            },
            "_en": {},
        },
        {
            "id": "900003",
            "nome": "Encantamento de Teste",
            "item_level": 0,
            "qualidade": 3,
            "bonus_ids": [],
            "url": "https://www.wowhead.com/pt/item=900003",
            "_pagina": "https://www.wowhead.com/pt/item=900003",
            "_categoria": "Encantamentos",
            "_pt": {
                "nome": "Encantamento de Teste",
                "item_level": 0,
                "qualidade": 3,
                "_contexto": "Encantamento de Teste\nEncantamento",
            },
            "_en": {},
        },
    ]

    finais = scraper._finalizar(itens_catalogo)

    assert len(finais) == 3, f"catálogo deveria passar inteiro: {finais}"
    assert scraper.descartes["qualidade_craft"] == 0, scraper.descartes
    assert all(i["qualidade_craft"] == 0 for i in finais), finais


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
            print(f"[FALHOU] {nome}")
            traceback.print_exc()
        else:
            print(f"[OK] {nome}")
    print(f"\n{'FALHAS' if falhas else 'SUCESSO'}: {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
