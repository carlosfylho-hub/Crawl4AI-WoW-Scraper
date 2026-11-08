#!/usr/bin/env python3
"""
Testes offline da semântica de `max_detalhes` e da ordem dedupe/filtro/truncar
(Pacote 2). Sem rede: o coletor e o crawler são mockados.

Cobrem:
- `max_detalhes`: None -> todos; 0 -> nenhum; 5 -> 5;
- `buscar_detalhes=False` -> nenhum detalhamento;
- truncamento por `max_itens` ocorre DEPOIS do dedupe;
- listagem de 50 itens com `--sem-detalhes` (buscar_detalhes=False) -> >= 40.

Execução:
    python -m pytest -q tests/test_max_detalhes.py
    python tests/test_max_detalhes.py        # fallback sem pytest
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


HTML_PAGINA_320 = """
<html><body>
  <h1 class="heading-size-1 q4">Item Mock</h1>
  <div id="main-contents">
    <div class="wowhead-tooltip"><div class="text">Item Mock
Nível do Item: 320</div></div>
  </div>
</body></html>
"""


def _item_fake(i: int) -> dict:
    return {
        "id": str(100000 + i),
        "nome": f"Item {i}",
        "item_level": 320,
        "qualidade": 4,
        "icone_url": "",
        "bonus_ids": [],
        "variante_fonte": "canonica",
        "url": "",
        "_contexto": "",
    }


def _novo_scraper(**kwargs):
    from scraper_season2 import WowheadSeason2Scraper

    opcoes = {
        "buscar_detalhes": True,
        "buscar_ingles": False,
        "max_itens": 200,
        "max_detalhes": None,
        "qualidade_min": 0,
    }
    opcoes.update(kwargs)
    return WowheadSeason2Scraper(**opcoes)


def _html_lista_50() -> str:
    linhas = []
    for i in range(50):
        item_id = 300000 + i
        linhas.append(
            f"""
    <tr>
      <td><a href="https://www.wowhead.com/pt/item={item_id}/i?bonus=100:{200 + i}"
             tabindex="-1"></a></td>
      <td><a class="q4 listview-cleartext"
             data-wowhead="item={item_id}&ilvl=320"
             href="https://www.wowhead.com/pt/item={item_id}/i">Item {i}</a></td>
    </tr>
"""
        )
    return "<html><body><table>" + "".join(linhas) + "</table></body></html>"


def _detalhados(max_detalhes, total=8, buscar_detalhes=True) -> tuple:
    scraper = _novo_scraper(
        max_detalhes=max_detalhes, buscar_detalhes=buscar_detalhes
    )
    chamadas = {"n": 0}

    async def fake_crawl(item, locale):
        chamadas["n"] += 1
        return ("https://www.wowhead.com/pt/item=" + str(item["id"]), HTML_PAGINA_320, [])

    scraper._crawl_locale = fake_crawl
    itens = [_item_fake(i) for i in range(total)]
    resultado = asyncio.run(scraper.detalhar_itens(itens))
    detalhados = sum(1 for item in resultado if item.get("_pt") is not None)
    return detalhados, chamadas["n"]


def test_max_detalhes_none_detalha_todos() -> None:
    detalhados, chamadas = _detalhados(None, total=8)
    assert detalhados == 8, detalhados
    assert chamadas == 8, chamadas


def test_max_detalhes_zero_nao_detalha() -> None:
    detalhados, chamadas = _detalhados(0, total=8)
    assert detalhados == 0, detalhados
    assert chamadas == 0, chamadas


def test_max_detalhes_cinco_detalha_cinco() -> None:
    detalhados, chamadas = _detalhados(5, total=8)
    assert detalhados == 5, detalhados
    assert chamadas == 5, chamadas


def test_buscar_detalhes_false_nao_detalha() -> None:
    detalhados, chamadas = _detalhados(None, total=8, buscar_detalhes=False)
    assert detalhados == 0, detalhados
    assert chamadas == 0, chamadas


def test_truncamento_acontece_apos_dedupe() -> None:
    """10 brutos com 6 duplicatas do mesmo item -> 5 únicos após dedupe."""
    scraper = _novo_scraper(
        buscar_detalhes=False, max_itens=6, max_detalhes=0
    )
    indices = [0, 0, 0, 0, 0, 0, 1, 2, 3, 4]
    brutos = [_item_fake(i) for i in indices]

    async def fake_coletar(url, categoria=""):
        return brutos, None

    scraper.coletar_url = fake_coletar
    scraper._finalizar = lambda lista: lista  # isola a fase de ordenação

    # P-03: o modo sem detalhes enriquece por tooltip HTTP. Sem mock, o teste
    # faria chamadas reais com backoff (2s/4s/8s por item) e pareceria travado.
    with patch("scraper_season2.consultar_tooltip", return_value=None):
        resultado = asyncio.run(
            scraper.executar_por_categorias(
                {"Gear": ["https://example.com/lista"]}
            )
        )

    assert resultado["metadata"]["total_brutos_antes_dedupe"] == 10, resultado["metadata"]
    assert len(resultado["itens"]) == 5, resultado["itens"]
    assert resultado["metadata"]["detalhados"] == 0


def test_listagem_50_sem_detalhes_retorna_mais_de_40() -> None:
    from wow_season2 import parse_links_itens

    scraper = _novo_scraper(
        buscar_detalhes=False, max_itens=50, max_detalhes=0
    )
    brutos = parse_links_itens(
        _html_lista_50(), "https://www.wowhead.com/pt/items/armor"
    )
    assert len(brutos) == 50, len(brutos)

    async def fake_coletar(url, categoria=""):
        return list(brutos), None

    scraper.coletar_url = fake_coletar
    scraper._finalizar = lambda lista: lista

    with patch("scraper_season2.consultar_tooltip", return_value=None):
        resultado = asyncio.run(
            scraper.executar_por_categorias(
                {"Gear": ["https://example.com/armor"]}
            )
        )

    assert len(resultado["itens"]) >= 40, len(resultado["itens"])
    assert resultado["metadata"]["descartes"].get("ilvl_adiado", 0) >= 0
    assert "ilvl_adiado" in resultado["metadata"]["descartes"]


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
