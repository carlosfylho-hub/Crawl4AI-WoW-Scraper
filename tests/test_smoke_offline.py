#!/usr/bin/env python3
"""Testes de fumaça **offline** (sem rede) do projeto.

Diferente do antigo `test_final.py` (movido para `legacy/`), estes testes
exercitam efeito observável do código real de produção:

a) importar os módulos de produção `wow_season2` e `scraper_season2`;
b) `normalizar_url_gear` gera URLs com `min-ilvl`/`max-ilvl` (não `min-level`);
c) `extrair_qualidade_craft` reconhece `R5`/`crafting-quality` e **não**
   confunde texto genérico "qualidade" com qualidade de craft;
d) o construtor de `WowheadSeason2Scraper` aceita `max_detalhes` e
   `qualidade_craft_min` (apenas instanciação, sem abrir browser).

Testes que dependem de rede são marcados como *skip* — nenhum teste de rede é
obrigatório para a suíte passar.

Execução:
    python -m pytest -q tests/test_smoke_offline.py
    python tests/test_smoke_offline.py        # fallback sem pytest
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Garante import dos módulos de produção mesmo no fallback sem pytest.
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


# ---------------------------------------------------------------------------
# (a) Importação dos módulos de produção
# ---------------------------------------------------------------------------

def test_importa_modulos_de_producao() -> None:
    """`wow_season2` e `scraper_season2` devem importar sem erro."""
    import wow_season2  # noqa: F401
    import scraper_season2  # noqa: F401

    assert hasattr(wow_season2, "extrair_qualidade_craft"), (
        "wow_season2 importou, mas não expõe extrair_qualidade_craft"
    )
    assert hasattr(scraper_season2, "WowheadSeason2Scraper"), (
        "scraper_season2 importou, mas não expõe WowheadSeason2Scraper"
    )


# ---------------------------------------------------------------------------
# (b) normalizar_url_gear usa min-ilvl / max-ilvl
# ---------------------------------------------------------------------------

def test_normalizar_url_gear_usa_min_ilvl() -> None:
    """Filtros de item level devem virar `min-ilvl`/`max-ilvl`."""
    from config import normalizar_url_gear

    entrada = (
        "https://www.wowhead.com/pt/items/min-level:305/max-level:350"
    )
    urls = normalizar_url_gear(entrada)

    assert urls, "normalizar_url_gear devolveu lista vazia"
    for url in urls:
        assert "min-ilvl:305" in url, f"URL sem min-ilvl correto: {url}"
        assert "max-ilvl:350" in url, f"URL sem max-ilvl correto: {url}"
        assert "min-level" not in url, f"URL manteve min-level (errado): {url}"
        assert "max-level" not in url, f"URL manteve max-level (errado): {url}"

    # A URL genérica é expandida para armor + weapons.
    assert len(urls) == 2, f"esperava 2 URLs (armor/weapons), veio: {urls}"
    assert any("/armor/min-ilvl:305" in url for url in urls), urls
    assert any("/weapons/min-ilvl:305" in url for url in urls), urls


def test_normalizar_url_gear_preserva_url_sem_items() -> None:
    """URL que não é de `/items/` deve passar intacta."""
    from config import normalizar_url_gear

    url = "https://www.wowhead.com/pt/guide/midnight/professions/alchemy"
    assert normalizar_url_gear(url) == [url]


# ---------------------------------------------------------------------------
# (c) extrair_qualidade_craft
# ---------------------------------------------------------------------------

#: Fixture mínima de HTML com qualidade de craft (R5).
HTML_CRAFT_R5 = """
<div class="item-tooltip">
  <span class="crafting-quality" data-value="5">R5</span>
  <div class="q1">Qualidade de criação: 5</div>
</div>
"""

#: Texto genérico que NÃO é qualidade de craft.
TEXTO_GENERICO = "Item de qualidade superior, sem indicacao de rank de craft."


def test_extrai_qualidade_craft_de_html_com_crafting_quality() -> None:
    """`R5` + `crafting-quality` devem resultar em qualidade 5."""
    from wow_season2 import extrair_qualidade_craft

    assert extrair_qualidade_craft(HTML_CRAFT_R5) == 5, (
        "não reconheceu R5/crafting-quality no HTML de fixture"
    )


def test_extrai_qualidade_craft_por_texto_explicito() -> None:
    """Rótulo explícito "Qualidade de criação: 4" deve resultar em 4."""
    from wow_season2 import extrair_qualidade_craft

    assert extrair_qualidade_craft("Qualidade de criação: 4") == 4
    assert extrair_qualidade_craft("Crafting Quality: 3") == 3


def test_nao_classifica_texto_generico_como_qualidade() -> None:
    """Texto genérico com a palavra "qualidade" não pode virar qualidade craft."""
    from wow_season2 import extrair_qualidade_craft

    assert extrair_qualidade_craft(TEXTO_GENERICO) == 0
    assert extrair_qualidade_craft("Item de qualidade 5") == 0
    assert extrair_qualidade_craft("") == 0


# ---------------------------------------------------------------------------
# (d) Construtor do scraper aceita os parâmetros do Pacote 3
# ---------------------------------------------------------------------------

def test_construtor_aceita_max_detalhes_e_qualidade_craft_min() -> None:
    """Instanciação apenas (não abre browser) com os novos parâmetros."""
    from scraper_season2 import WowheadSeason2Scraper

    scraper = WowheadSeason2Scraper(max_detalhes=7, qualidade_craft_min=4)

    assert scraper.max_detalhes == 7, (
        f"max_detalhes não foi aplicado: {scraper.max_detalhes}"
    )
    assert scraper.qualidade_craft_min == 4, (
        f"qualidade_craft_min não foi aplicado: {scraper.qualidade_craft_min}"
    )


# ---------------------------------------------------------------------------
# Testes dependentes de rede — sempre SKIP
# ---------------------------------------------------------------------------

def _pular(motivo: str) -> None:
    """Marca o teste como skip tanto no pytest quanto no runner de fallback.

    `unittest.SkipTest` é reconhecido pelo pytest e pelo runner
    `python tests/<arquivo>.py`, evitando que o script aborte com exit 1.
    """
    raise unittest.SkipTest(motivo)


def test_smoke_real_wowhead_requer_rede() -> None:
    """Smoke real (2 itens) exige rede; fica fora da suíte offline."""
    _pular("Requer rede. Rode manualmente: python scraper_season2.py --max-itens 2")


def test_healthcheck_httpbin_requer_rede() -> None:
    """Verificação do browser/Playwright exige rede e Chromium instalado."""
    _pular(
        "Requer rede + Chromium. Rode manualmente quando precisar validar o browser."
    )


if __name__ == "__main__":  # pragma: no cover - fallback sem pytest
    import traceback

    falhas = 0
    for nome, funcao in sorted(globals().items()):
        if not (nome.startswith("test_") and callable(funcao)):
            continue
        try:
            funcao()
        except unittest.SkipTest as motivo:
            print(f"[SKIP] {nome}: {motivo}")
        except Exception:  # noqa: BLE001 - relatório simples
            falhas += 1
            print(f"[FALHOU] {nome}")
            traceback.print_exc()
        else:
            print(f"[OK] {nome}")
    print(f"\n{'FALHAS' if falhas else 'SUCESSO'}: {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
