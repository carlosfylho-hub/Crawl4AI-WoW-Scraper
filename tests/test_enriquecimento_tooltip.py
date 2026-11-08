#!/usr/bin/env python3
"""
Testes offline do enriquecimento por tooltip no modo sem detalhes (P-03/F-05).

Sem rede e sem browser: `coletar_url` e `consultar_tooltip` são mockados. O
critério é o mesmo da pendência: `--sem-detalhes` deve devolver itens com nome,
item level, ícone e atributos primários (em vez de descarte em massa).

Execução:
    python -m pytest -q tests/test_enriquecimento_tooltip.py
    python tests/test_enriquecimento_tooltip.py    # fallback sem pytest
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

TOTAL = 45


def _bruto(i: int) -> dict:
    ident = str(300000 + i)
    return {
        "id": ident,
        "nome": "",
        "item_level": 0,
        "bonus_ids": [],
        "variante_fonte": "canonica",
        "url": f"https://www.wowhead.com/pt/item={ident}",
        "_pagina": f"https://www.wowhead.com/pt/item={ident}",
        "_categoria": "Gear",
        "_contexto": "",
    }


def _tooltip(i: int) -> dict:
    nome = f"Item Mock {i}"
    return {
        "nome": nome,
        "nome_ptbr": nome,
        "nome_en": "",
        "item_level": 341,
        "track_rotulo": "Herói 6/6",
        "qualidade": 4,
        "icone_url": (
            "https://wow.zamimg.com/images/wow/icons/large/inv_helm_cloth.jpg"
        ),
        "atributos_primarios": {"Intelecto": 1234},
        "atributos_secundarios": {"Aceleração": 500},
        "bonus_ids": ["12856"],
        "tooltip_html": f"<b>{nome}</b>",
        "tooltip_texto": (
            f"{nome}\nNível do Item: 341\nCabeça\nArmadura de Tecido\n"
            "+ 1.234 Intelecto\n+ 500 Aceleração"
        ),
    }


def _novo_scraper(**kwargs):
    from scraper_season2 import WowheadSeason2Scraper

    opcoes = {
        "buscar_detalhes": False,
        "buscar_ingles": False,
        "max_itens": 50,
        "max_detalhes": 0,
        "qualidade_min": 0,
        "ilvl_min": 305,
        "ilvl_max": 350,
        "gerar_markdown": False,
    }
    opcoes.update(kwargs)
    return WowheadSeason2Scraper(**opcoes)


def _executar(scraper):
    async def fake_coletar(url, categoria=""):  # noqa: ARG001
        return [_bruto(i) for i in range(TOTAL)], None

    scraper.coletar_url = fake_coletar
    return asyncio.run(
        scraper.executar_por_categorias({"Gear": ["https://example.com/gear"]})
    )


def test_sem_detalhes_retorna_itens_enriquecidos() -> None:
    scraper = _novo_scraper()

    def fake_tooltip(ident, bonus):  # noqa: ARG001
        return _tooltip(int(ident) - 300000)

    with patch("scraper_season2.consultar_tooltip", side_effect=fake_tooltip):
        resultado = _executar(scraper)

    itens = resultado["itens"]
    meta = resultado["metadata"]

    assert len(itens) >= 40, len(itens)
    assert meta["enriquecidos_tooltip"] == TOTAL, meta
    assert meta["tooltip_falhas"] == 0, meta
    assert meta["descartes"]["sem_ilvl"] == 0, meta["descartes"]

    for item in itens:
        assert item.get("nome_ptbr"), item
        assert item.get("item_level") == 341, item
        assert item.get("icone_url"), item
        assert item.get("atributos_primarios") == {"Intelecto": 1234}, item
        assert item.get("atributos_fonte") == "tooltip_http", item
        assert item.get("icone_fonte") == "tooltip_http", item
        assert item.get("nome_ptbr_fonte") == "tooltip_http", item


def test_tooltip_indisponivel_nao_quebra() -> None:
    scraper = _novo_scraper()

    with patch("scraper_season2.consultar_tooltip", return_value=None):
        resultado = _executar(scraper)

    meta = resultado["metadata"]
    assert meta["enriquecidos_tooltip"] == 0, meta
    assert meta["tooltip_falhas"] == TOTAL, meta
    assert meta["descartes"]["sem_ilvl"] == TOTAL, meta["descartes"]
    assert resultado["itens"] == []


def test_com_detalhes_nao_chama_tooltip_de_enriquecimento() -> None:
    scraper = _novo_scraper(buscar_detalhes=True, max_detalhes=5)

    with patch("scraper_season2.consultar_tooltip") as mock:
        with patch.object(
            scraper, "_crawl_locale", return_value=("", "<html></html>", [])
        ):
            _executar(scraper)

    mock.assert_not_called()


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
