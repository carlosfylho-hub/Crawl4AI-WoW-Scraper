#!/usr/bin/env python3
"""
Testes offline da fonte de itens **craftados** (P-13).

Quando `exigir_craft` está ligado, o pipeline deve listar os IDs de craft
(`data/season2_craft_ids.json`), não os drops de M+.

Execução:
    python -m pytest -q tests/test_config_urls_craft.py
    python tests/test_config_urls_craft.py     # fallback sem pytest
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


def test_artefato_de_craft_carregado() -> None:
    from config import SEASON2_CRAFT_IDS

    assert len(SEASON2_CRAFT_IDS) >= 50, len(SEASON2_CRAFT_IDS)
    assert all(ident.isdigit() for ident in SEASON2_CRAFT_IDS)
    assert len(set(SEASON2_CRAFT_IDS)) == len(SEASON2_CRAFT_IDS)
    assert "237831" in SEASON2_CRAFT_IDS


def test_urls_craft_canonicas_formato() -> None:
    from config import SEASON2_CRAFT_IDS, urls_craft_canonicas

    urls = urls_craft_canonicas()

    assert len(urls) == len(SEASON2_CRAFT_IDS), len(urls)
    for url in urls:
        assert "/pt/item=" in url, url
        assert "bonus=12856" in url, url
        assert "crafting-quality" not in url, url


def test_urls_craft_respeita_limite() -> None:
    from config import urls_craft_canonicas

    assert len(urls_craft_canonicas(0)) == 0
    assert len(urls_craft_canonicas(7)) == 7


def test_resolver_gear_com_somente_craft_usa_ids_de_craft() -> None:
    from config import SEASON2_CRAFT_IDS, resolver_urls_categoria

    urls = resolver_urls_categoria(
        "gear_season2", 305, 350, limite=5, somente_craft=True
    )

    assert len(urls) == 5, urls
    for url in urls:
        assert "/pt/item=" in url, url


def test_resolver_gear_sem_somente_craft_usa_ids_de_loot() -> None:
    from config import (
        SEASON2_CRAFT_IDS,
        SEASON2_GEAR_IDS,
        resolver_urls_categoria,
    )

    urls = resolver_urls_categoria("gear_season2", 305, 350, limite=5)
    ids = [url.split("item=")[1].split("?")[0] for url in urls]

    assert ids == SEASON2_GEAR_IDS[:5], ids
    if SEASON2_CRAFT_IDS != SEASON2_GEAR_IDS:
        assert ids != SEASON2_CRAFT_IDS[:5], ids


def test_montar_categorias_repassa_somente_craft() -> None:
    from config import CATEGORIAS_WOW, montar_categorias_selecionadas

    nome = CATEGORIAS_WOW["gear_season2"]["nome"]
    selecionadas = montar_categorias_selecionadas(
        ["gear_season2"], 305, 350, limite=4, somente_craft=True
    )

    assert nome in selecionadas, selecionadas
    assert len(selecionadas[nome]) == 4, selecionadas[nome]


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
