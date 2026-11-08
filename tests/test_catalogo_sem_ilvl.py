#!/usr/bin/env python3
"""Testes offline de **catálogos com `ilvl=0`** (Pacote 4 / pendência 11).

Garante que missivas, gemas e encantamentos (que vêm sem item level) não são
descartados em [`scraper_season2.py`](../scraper_season2.py:576) nem entram no
filtro de craft, e que a URL de detalhe deles nunca recebe `crafting-quality`.

Execução:
    python -m pytest -q tests/test_catalogo_sem_ilvl.py
    python tests/test_catalogo_sem_ilvl.py        # fallback sem pytest
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from scraper_season2 import WowheadSeason2Scraper  # noqa: E402


def _bruto_catalogo(
    item_id: str, categoria: str, nome: str, contexto: str, url: str
) -> Dict[str, Any]:
    return {
        "id": item_id,
        "nome": nome,
        "item_level": 0,
        "qualidade": 3,
        "bonus_ids": [],
        "url": url,
        "_pagina": url,
        "_categoria": categoria,
        "_pt": {
            "nome": nome,
            "item_level": 0,
            "qualidade": 3,
            "_contexto": contexto,
        },
        "_en": {},
    }


def _catalogo() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Retorna (brutos como o scraper entrega, itens já finalizados)."""
    itens: List[Dict[str, Any]] = [
        _bruto_catalogo(
            "900001",
            "Gemas",
            "Gema de Teste",
            "Gema de Teste\nGema",
            "https://www.wowhead.com/pt/item=900001",
        ),
        _bruto_catalogo(
            "900002",
            "Missivas (tipos)",
            "Missiva de Teste",
            "Missiva de Teste\nMissiva",
            "https://www.wowhead.com/pt/item=900002",
        ),
        _bruto_catalogo(
            "900003",
            "Encantamentos",
            "Encantamento de Teste",
            "Encantamento de Teste\nEncantamento",
            "https://www.wowhead.com/pt/item=900003",
        ),
    ]
    return itens, [dict(item) for item in itens]


def _scraper() -> WowheadSeason2Scraper:
    return WowheadSeason2Scraper(
        qualidade_craft_min=5,
        ilvl_min=305,
        ilvl_max=350,
        qualidade_min=3,
        incluir_sem_ilvl=False,
        gerar_markdown=False,
    )


def test_prefiltrar_mantem_catalogo_sem_ilvl() -> None:
    scraper = _scraper()
    scraper._iniciar_descartes()
    _, itens = _catalogo()

    mantidos = scraper._prefiltrar(itens)

    assert len(mantidos) == 3, f"catálogo com ilvl=0 foi descartado: {mantidos}"
    assert scraper.descartes["sem_ilvl"] == 0, scraper.descartes
    assert scraper.descartes["ilvl_fora"] == 0, scraper.descartes


def test_finalizar_mantem_catalogo_sem_ilvl() -> None:
    scraper = _scraper()
    brutos, _ = _catalogo()

    finais = scraper._finalizar(brutos)

    assert len(finais) == 3, f"catálogo deveria sobreviver ao _finalizar: {finais}"
    assert {i["tipo_item"] for i in finais} == {"gema", "missiva", "encantamento"}
    assert all(int(i["item_level"]) == 0 for i in finais), finais
    assert all(int(i["qualidade_craft"]) == 0 for i in finais), finais
    assert scraper.descartes["qualidade_craft"] == 0, scraper.descartes
    assert scraper.descartes["sem_ilvl"] == 0, scraper.descartes


def test_url_detalhe_catalogo_sem_crafting_quality() -> None:
    scraper = _scraper()
    for categoria in ("Gemas", "Missivas (tipos)", "Encantamentos"):
        url = scraper._url_detalhe({"id": "900001", "_categoria": categoria}, "ptbr")
        assert "crafting-quality" not in url, f"{categoria}: {url}"

    # Contraste: gear COM indício de craft recebe o parâmetro.
    url_gear = scraper._url_detalhe(
        {"id": "250001", "_categoria": "Geral", "_profissao_url": "Ferraria"},
        "ptbr",
    )
    assert "crafting-quality=5" in url_gear, url_gear

    # Gear de drop (sem indício) não recebe a marca.
    url_drop = scraper._url_detalhe(
        {"id": "250001", "_categoria": "Geral"}, "ptbr"
    )
    assert "crafting-quality" not in url_drop, url_drop


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
