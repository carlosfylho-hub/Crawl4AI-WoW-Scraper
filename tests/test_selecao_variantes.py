#!/usr/bin/env python3
"""
Testes offline da seleção de variante por item (F-01).

Contexto: a listagem do Wowhead devolve **várias variantes do mesmo item**
(mesmo `item_id`, `bonus_ids`/`item_level` diferentes). O truncamento por
`max_itens` acontecia antes de qualquer seleção, então as vagas eram gastas
nas variantes de track baixo do primeiro item e nenhum item 305–350 chegava
ao funil.

Regras cobertas aqui (sem rede — nada é baixado):

a) variante cujo `bonus_ids` intersecta `TRACKS_SEASON2` tem prioridade;
b) sem track, escolhe a de maior `item_level` conhecido;
c) sem track e todas sem ilvl, mantém exatamente uma;
d) dois itens distintos com track são mantidos, na ordem original;
e) `metadata` expõe as três contagens de `selecao_variante`;
f) a ordem final preserva a sequência de `item_id` da listagem.

Execução:
    python -m pytest -q tests/test_selecao_variantes.py
    python tests/test_selecao_variantes.py        # fallback sem pytest
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


def _item(
    ident: object,
    ilvl: int,
    bonus: list | None = None,
    nome: str = "",
) -> dict:
    """Variante bruta no mesmo formato de `parse_links_itens`."""
    bonus_ids = [str(b) for b in (bonus or [])]
    return {
        "id": str(ident),
        "nome": nome or f"Item {ident}",
        "item_level": int(ilvl or 0),
        "qualidade": 4,
        "icone_url": "",
        "bonus_ids": bonus_ids,
        "variante_fonte": "listagem" if bonus_ids else "canonica",
        "url": "",
        "_contexto": "",
    }


def _scraper(**kwargs):
    from scraper_season2 import WowheadSeason2Scraper

    opcoes = {
        "buscar_detalhes": False,
        "buscar_ingles": False,
        "qualidade_min": 0,
    }
    opcoes.update(kwargs)
    return WowheadSeason2Scraper(**opcoes)


def _tracks() -> set:
    from config import TRACKS_SEASON2

    return set(TRACKS_SEASON2)


# ---------------------------------------------------------------------------
# a) variante com track da temporada
# ---------------------------------------------------------------------------


def test_variante_com_track_tem_prioridade() -> None:
    scraper = _scraper()
    itens = [
        _item(268265, 219, [6652]),
        _item(268265, 279, [6652, 1574]),
        _item(268265, 334, [12854, 6652]),
        _item(268265, 282, [6652, 41]),
        _item(268265, 285, [8960]),
    ]

    selecionados = scraper._selecionar_melhores_variantes(itens, _tracks())

    assert len(selecionados) == 1, selecionados
    assert selecionados[0]["item_level"] == 334, selecionados[0]
    assert "12854" in selecionados[0]["bonus_ids"], selecionados[0]
    assert scraper._selecao_variante_contagem == {
        "track_temporada": 1,
        "maior_ilvl": 0,
        "unica_sem_ilvl": 0,
    }


# ---------------------------------------------------------------------------
# b) nenhuma com track -> maior ilvl conhecido
# ---------------------------------------------------------------------------


def test_sem_track_escolhe_maior_ilvl() -> None:
    scraper = _scraper()
    itens = [
        _item(268265, 219, [6652]),
        _item(268265, 279, [6652, 1574]),
        _item(268265, 282, [6652, 41]),
        _item(268265, 285, [8960]),
    ]

    selecionados = scraper._selecionar_melhores_variantes(itens, _tracks())

    assert len(selecionados) == 1, selecionados
    assert selecionados[0]["item_level"] == 285, selecionados[0]
    assert scraper._selecao_variante_contagem == {
        "track_temporada": 0,
        "maior_ilvl": 1,
        "unica_sem_ilvl": 0,
    }
    # Nenhuma variante tinha track -> nada de alternativa para o fallback.
    assert selecionados[0]["_variantes_alternativas"] == []


# ---------------------------------------------------------------------------
# c) todas sem ilvl -> exatamente uma
# ---------------------------------------------------------------------------


def test_todas_sem_ilvl_mantem_apenas_uma() -> None:
    scraper = _scraper()
    itens = [
        _item(300001, 0, [6652]),
        _item(300001, 0, [6652, 1574]),
        _item(300001, 0, []),
        _item(300001, 0, [8960]),
    ]

    selecionados = scraper._selecionar_melhores_variantes(itens, _tracks())

    assert len(selecionados) == 1, selecionados
    assert selecionados[0] is itens[0]
    assert scraper._selecao_variante_contagem == {
        "track_temporada": 0,
        "maior_ilvl": 0,
        "unica_sem_ilvl": 1,
    }


# ---------------------------------------------------------------------------
# d) dois itens distintos com track
# ---------------------------------------------------------------------------


def test_dois_itens_distintos_com_track_sao_mantidos() -> None:
    scraper = _scraper()
    itens = [
        _item(111, 219, [6652]),
        _item(111, 321, [12846, 6652]),
        _item(222, 279, [6652]),
        _item(222, 334, [12854, 6652]),
    ]

    selecionados = scraper._selecionar_melhores_variantes(itens, _tracks())

    assert [i["id"] for i in selecionados] == ["111", "222"], selecionados
    assert [i["item_level"] for i in selecionados] == [321, 334]
    assert scraper._selecao_variante_contagem["track_temporada"] == 2


# ---------------------------------------------------------------------------
# e) metadata com as três contagens
# ---------------------------------------------------------------------------


def test_metadata_contem_contagens_de_selecao() -> None:
    scraper = _scraper()

    async def fake_coletar(url, categoria=""):
        return (
            [
                _item(1, 219, [6652]),
                _item(1, 334, [12854]),
                _item(2, 279, [6652]),
                _item(2, 285, [6652]),
                _item(3, 0, []),
                _item(3, 0, [6652]),
            ],
            None,
        )

    scraper.coletar_url = fake_coletar  # type: ignore[method-assign]
    resultado = asyncio.run(
        scraper.executar_por_categorias(
            {"Geral": ["https://www.wowhead.com/pt/items?bonus=12846"]}
        )
    )

    meta = resultado["metadata"]
    assert meta["variantes_antes_selecao"] == 6, meta
    assert meta["variantes_depois_selecao"] == 3, meta
    assert meta["itens_distintos"] == 3, meta

    selecao = meta["selecao_variante"]
    assert set(selecao) == {"track_temporada", "maior_ilvl", "unica_sem_ilvl"}
    assert selecao == {
        "track_temporada": 1,
        "maior_ilvl": 1,
        "unica_sem_ilvl": 1,
    }, selecao


# ---------------------------------------------------------------------------
# f) ordem original preservada
# ---------------------------------------------------------------------------


def test_ordem_final_preserva_sequencia_da_listagem() -> None:
    scraper = _scraper()
    itens = [
        _item(400001, 219, [6652]),
        _item(400002, 321, [12846]),
        _item(400001, 334, [12854]),
        _item(400003, 310, [12856]),
        _item(400002, 279, [6652]),
    ]

    selecionados = scraper._selecionar_melhores_variantes(itens, _tracks())

    assert [i["id"] for i in selecionados] == [
        "400001",
        "400002",
        "400003",
    ], selecionados
    assert [i["item_level"] for i in selecionados] == [334, 321, 310]


# ---------------------------------------------------------------------------
# B) fallback de variante alternativa no `_arbitrar_ilvl`
# ---------------------------------------------------------------------------


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


def test_arbitrar_ilvl_usa_uma_variante_alternativa_com_track() -> None:
    scraper = _scraper(buscar_detalhes=True, max_detalhes=None)

    async def fake_crawl(item, locale):
        return (
            "https://www.wowhead.com/pt/item=" + str(item.get("id")),
            _html_item(str(item.get("nome") or "Item"), 219),
            [],
        )

    scraper._crawl_locale = fake_crawl  # type: ignore[method-assign]

    itens = [
        {
            "id": "268265",
            "nome": "Relicário Aqiricida",
            "item_level": 219,
            "qualidade": 4,
            "bonus_ids": ["6652"],
            "variante_fonte": "listagem",
            "url": "",
            "_contexto": "",
            "_variantes_alternativas": [["12854", "6652"]],
        }
    ]

    chamadas: list = []

    def fake_tooltip(ident, bonus=None):
        bonus_str = [str(b) for b in (bonus or [])]
        chamadas.append(bonus_str)
        if "12854" in bonus_str:
            return {"item_level": 334, "track_rotulo": "Myth 6/6"}
        return {"item_level": 219}

    with patch("scraper_season2.consultar_tooltip", side_effect=fake_tooltip):
        resultado = asyncio.run(scraper.detalhar_itens(itens))

    assert resultado[0]["item_level"] == 334, resultado[0]
    assert resultado[0]["_variante_alternativa_usada"] is True, resultado[0]
    assert resultado[0]["variante_alternativa_usada"] is True, resultado[0]
    assert resultado[0]["bonus_ids"] == ["12854", "6652"], resultado[0]
    # 1 tooltip da variante atual + 1 da alternativa (nenhuma tentativa extra).
    assert len(chamadas) == 2, chamadas


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
