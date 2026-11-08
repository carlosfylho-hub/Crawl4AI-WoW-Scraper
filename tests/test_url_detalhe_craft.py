#!/usr/bin/env python3
"""
Testes offline da marca `crafting-quality` na URL de detalhe.

Regra: a marca só é emitida quando há **indício de craft**. Gear de drop
(M+/raid) não recebe a marca, para não gerar
``motivo_qualidade_craft = "ignorado:sem_profissao (url:crafting-quality)"``
em massa.

Execução:
    python -m pytest -q tests/test_url_detalhe_craft.py
    python tests/test_url_detalhe_craft.py     # fallback sem pytest
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

URL_BASE = "https://www.wowhead.com/pt/item=999999?bonus=12856"


def _scraper(qualidade_craft_min: int = 5):
    from scraper_season2 import WowheadSeason2Scraper

    return WowheadSeason2Scraper(
        qualidade_craft_min=qualidade_craft_min,
        gerar_markdown=False,
        buscar_detalhes=False,
    )


def _item(**extra):
    base = {
        "id": "999999",
        "bonus_ids": ["12856"],
        "_categoria": "Gear",
    }
    base.update(extra)
    return base


def test_gear_de_drop_nao_recebe_crafting_quality() -> None:
    url = _scraper()._url_detalhe(_item())
    assert url == URL_BASE, url
    assert "crafting-quality" not in url, url


def test_profissao_na_url_recebe_crafting_quality() -> None:
    url = _scraper()._url_detalhe(_item(_profissao_url="Ferraria"))
    assert "crafting-quality=5" in url, url


def test_id_no_mapa_de_receitas_recebe_crafting_quality() -> None:
    url = _scraper()._url_detalhe(
        {"id": "237831", "bonus_ids": [], "_categoria": "Gear"}
    )
    assert "crafting-quality=5" in url, url


def test_craft_indicio_recebe_crafting_quality() -> None:
    url = _scraper()._url_detalhe(_item(craft_indicio="receita:237831"))
    assert "crafting-quality=5" in url, url


def test_catalogo_nunca_recebe_crafting_quality() -> None:
    for categoria in ("encantamentos", "gemas", "missivas", "consumiveis"):
        url = _scraper()._url_detalhe(_item(_categoria=categoria))
        assert "crafting-quality" not in url, (categoria, url)


def test_qualidade_craft_zero_nao_emite_parametro() -> None:
    url = _scraper(qualidade_craft_min=0)._url_detalhe(
        _item(_profissao_url="Ferraria")
    )
    assert "crafting-quality" not in url, url


def test_bonus_continua_na_url() -> None:
    url = _scraper()._url_detalhe(_item(_profissao_url="Ferraria"))
    assert "bonus=12856" in url, url


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
