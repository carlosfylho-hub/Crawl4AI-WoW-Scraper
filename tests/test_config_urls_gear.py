#!/usr/bin/env python3
"""
Testes offline da fonte de gear da Season 2 (F-01/P-01b).

Contexto: o Wowhead **não** aplica filtro de `ilvl`/`bonus` server-side na
listagem (`/items?...`), então o crawl headless recebe o banco genérico de
itens. A fonte primária passou a ser `data/season2_gear_ids.json`, extraído do
banco de loot M+, com `bonus=12856` (ilvl 341 medido via tooltip).

Execução:
    python -m pytest -q tests/test_config_urls_gear.py
    python tests/test_config_urls_gear.py        # fallback sem pytest
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


def test_artefato_de_ids_carregado() -> None:
    from config import SEASON2_GEAR_IDS

    assert len(SEASON2_GEAR_IDS) >= 100, len(SEASON2_GEAR_IDS)
    assert all(ident.isdigit() for ident in SEASON2_GEAR_IDS)
    assert len(set(SEASON2_GEAR_IDS)) == len(SEASON2_GEAR_IDS)


def test_urls_gear_canonicas_formato() -> None:
    from config import SEASON2_GEAR_BONUS, SEASON2_GEAR_IDS, urls_gear_canonicas

    urls = urls_gear_canonicas()

    assert len(urls) == len(SEASON2_GEAR_IDS), len(urls)
    for url, ident in zip(urls, SEASON2_GEAR_IDS):
        assert url.startswith("https://www.wowhead.com/pt/item="), url
        assert f"item={ident}" in url, url
        assert url.endswith(f"?bonus={SEASON2_GEAR_BONUS}"), url
        assert "min-level" not in url, url
        assert "min-ilvl" not in url, url


def test_urls_gear_canonicas_respeita_limite() -> None:
    from config import urls_gear_canonicas

    assert len(urls_gear_canonicas(0)) == 0
    assert len(urls_gear_canonicas(5)) == 5
    assert len(urls_gear_canonicas(None)) >= 100


def test_bonus_nao_usa_marcador_13440() -> None:
    from config import SEASON2_GEAR_BONUS, urls_gear_canonicas

    assert SEASON2_GEAR_BONUS == "12856"
    assert SEASON2_GEAR_BONUS != "13440"
    for url in urls_gear_canonicas(3):
        assert "13440" not in url, url


def test_resolver_gear_usa_ids_canonicos() -> None:
    from config import resolver_urls_categoria

    urls = resolver_urls_categoria("gear_season2", 305, 350, limite=10)

    assert len(urls) == 10, urls
    for url in urls:
        assert "/pt/item=" in url, url
        assert "bonus=12856" in url, url
        assert "quality=" not in url, url


def test_listagem_generica_fica_como_fallback() -> None:
    from config import SEASON2_ITEM_URLS

    assert SEASON2_ITEM_URLS, "o fallback de listagem não pode sumir"
    for url in SEASON2_ITEM_URLS:
        assert "/items?" in url, url
        assert "bonus=12846:12854:12856:13440" in url, url
        assert "quality=4" in url, url
        assert "min-ilvl=305" in url, url
        assert "max-ilvl=350" in url, url
        assert "min-level" not in url, url


def test_artefato_ausente_degrada_para_lista_vazia(tmp_path) -> None:
    from config import _carregar_ids_gear_s2

    assert _carregar_ids_gear_s2(str(tmp_path / "nao_existe.json")) == []


def test_montar_categorias_repassa_limite() -> None:
    from config import CATEGORIAS_WOW, montar_categorias_selecionadas

    nome = CATEGORIAS_WOW["gear_season2"]["nome"]
    selecionadas = montar_categorias_selecionadas(
        ["gear_season2"], 305, 350, limite=7
    )

    assert nome in selecionadas, selecionadas
    assert len(selecionadas[nome]) == 7, selecionadas[nome]


if __name__ == "__main__":  # pragma: no cover - fallback sem pytest
    import traceback

    falhas = 0
    for nome, funcao in sorted(globals().items()):
        if not (nome.startswith("test_") and callable(funcao)):
            continue
        try:
            if nome == "test_artefato_ausente_degrada_para_lista_vazia":
                import tempfile

                with tempfile.TemporaryDirectory() as tmp:
                    funcao(Path(tmp))
            else:
                funcao()
        except Exception:  # noqa: BLE001 - relatório simples
            falhas += 1
            print(f"[FAIL] {nome}")
            traceback.print_exc()
        else:
            print(f"[OK] {nome}")
    print(f"\n{'FALHAS' if falhas else 'SUCESSO'}: {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
