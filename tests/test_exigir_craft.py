#!/usr/bin/env python3
"""
Testes offline do filtro `exigir_craft` (requisito: só itens R5 épicos).

Regras:
- `exigir_craft=True` aceita apenas `qualidade_craft == qualidade_craft_min`;
- `qualidade_craft=0` (não craftado) é descartado em `descartes["sem_craft"]`;
- catálogos (gema/encantamento/missiva) ficam isentos;
- `exigir_craft=False` preserva o comportamento antigo (qc=0 passa);
- a raridade padrão de gear é **4 (Épico)**.

Execução:
    python -m pytest -q tests/test_exigir_craft.py
    python tests/test_exigir_craft.py     # fallback sem pytest
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from scraper_season2 import WowheadSeason2Scraper  # noqa: E402
from wow_season2 import extrair_detalhes_item  # noqa: E402


def _html(raridade: int, linha_craft: str = "", profissao: bool = False) -> str:
    link = (
        '<a href="/pt/professions/blacksmithing">Ferraria</a>'
        if profissao
        else ""
    )
    return f"""
<html><body>
  <h1 class="heading-size-1 q{raridade}">Item de Teste</h1>
  <div class="wowhead-tooltip">
    <div>Nível do Item: 341</div>
    <div>Cabeça</div>
    <div>Armadura de Placa</div>
    <div>{linha_craft}</div>
    {link}
  </div>
</body></html>
"""


HTML_R5 = _html(4, "Qualidade de criação: 5", profissao=True)
HTML_R4 = _html(4, "Qualidade de criação: 4", profissao=True)
HTML_SEM_CRAFT = _html(4)
HTML_RARO_R5 = _html(3, "Qualidade de criação: 5", profissao=True)


def _bruto(html: str, item_id: str, categoria: str = "Geral") -> Dict[str, Any]:
    url = f"https://www.wowhead.com/pt/item={item_id}"
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


def _scraper(**kwargs) -> WowheadSeason2Scraper:
    opcoes = {
        "qualidade_craft_min": 5,
        "ilvl_min": 305,
        "ilvl_max": 350,
        "gerar_markdown": False,
        "buscar_detalhes": True,
    }
    opcoes.update(kwargs)
    return WowheadSeason2Scraper(**opcoes)


def test_raridade_padrao_de_gear_e_epica() -> None:
    assert _scraper().qualidade_min == 4


def test_exigir_craft_aceita_r5() -> None:
    scraper = _scraper(exigir_craft=True)
    finais = scraper._finalizar([_bruto(HTML_R5, "410001")])

    assert len(finais) == 1, finais
    assert finais[0]["qualidade_craft"] == 5, finais[0]
    assert finais[0]["qualidade"] == 4, finais[0]
    assert scraper.descartes["sem_craft"] == 0, scraper.descartes


def test_exigir_craft_descarta_r4() -> None:
    scraper = _scraper(exigir_craft=True)
    finais = scraper._finalizar([_bruto(HTML_R4, "410002")])

    assert finais == [], finais
    assert scraper.descartes["sem_craft"] == 1, scraper.descartes


def test_exigir_craft_descarta_nao_craftado() -> None:
    scraper = _scraper(exigir_craft=True)
    finais = scraper._finalizar([_bruto(HTML_SEM_CRAFT, "410003")])

    assert finais == [], finais
    assert scraper.descartes["sem_craft"] == 1, scraper.descartes


def test_sem_exigir_craft_mantem_nao_craftado() -> None:
    scraper = _scraper(exigir_craft=False)
    finais = scraper._finalizar([_bruto(HTML_SEM_CRAFT, "410004")])

    assert len(finais) == 1, finais
    assert finais[0]["qualidade_craft"] == 0, finais[0]
    assert scraper.descartes["sem_craft"] == 0, scraper.descartes


def test_catalogo_fica_isento_de_exigir_craft() -> None:
    scraper = _scraper(exigir_craft=True)
    finais = scraper._finalizar(
        [_bruto(HTML_SEM_CRAFT, "410005", categoria="gemas")]
    )

    assert len(finais) == 1, finais
    assert scraper.descartes["sem_craft"] == 0, scraper.descartes


def test_raridade_abaixo_de_epico_e_descartada() -> None:
    scraper = _scraper(exigir_craft=True)
    finais = scraper._finalizar([_bruto(HTML_RARO_R5, "410006")])

    assert finais == [], finais
    assert scraper.descartes["qualidade"] == 1, scraper.descartes


def test_metadata_expoe_exigir_craft() -> None:
    assert _scraper(exigir_craft=True).exigir_craft is True
    assert _scraper(exigir_craft=False).exigir_craft is False


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
