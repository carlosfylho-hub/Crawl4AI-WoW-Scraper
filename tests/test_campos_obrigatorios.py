#!/usr/bin/env python3
"""Testes dos campos obrigatórios e rastreadores de fonte do dict canônico.

Valida que `finalizar_item_bilingue` devolve TODAS as chaves obrigatórias,
com o tipo correto e sem `None`, além de preencher `tooltip_raidbots(-en)`.

Execução:
    python -m pytest -q tests/test_campos_obrigatorios.py
    python tests/test_campos_obrigatorios.py     # fallback sem pytest
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from wow_season2 import (  # noqa: E402
    FONTES_ATRIBUTOS,
    FONTES_ICONE,
    FONTES_NOME,
    finalizar_item_bilingue,
)

FIXTURE_TOOLTIP_PT = """
Lâmina do Vazio Forjado
Item Level 341
Arma de Duas Mãos
Épico
Força +1.420
Vigor +2.850
Aceleração +850
Maestria +620
Equip: Seus golpes têm chance de liberar energia do Vazio.
Voidforge 6/6
"""

FIXTURE_TOOLTIP_EN = """
Voidforged Blade
Item Level 341
Two-Hand
Sword
+1,420 Strength
+2,850 Stamina
+850 Haste
+620 Mastery
Equip: Your strikes have a chance to unleash Void energy.
Voidforge 6/6
"""

#: Campos obrigatórios e o tipo esperado de cada um.
CAMPOS_OBRIGATORIOS = {
    "nome_ptbr": str,
    "nome_en": str,
    "icone_url": str,
    "item_level": int,
    "slot": str,
    "tipo_armadura": str,
    "atributos_primarios": dict,
    "atributos_secundarios": dict,
    "efeito_equip_uso_ptbr": str,
    "efeito_equip_uso_en": str,
    "tooltip_raidbots": str,
    "tooltip_raidbots_en": str,
    "nome_ptbr_fonte": str,
    "nome_en_fonte": str,
    "icone_fonte": str,
    "atributos_fonte": str,
}


def _item_finalizado() -> dict:
    bruto = {
        "id": "250001",
        "nome": "Nome da listagem",
        "item_level": 341,
        "qualidade": 4,
        "icone_url": "inv_sword_2h_d_01",
        "bonus_ids": ["12838"],
        "url": "https://www.wowhead.com/pt/item=250001",
        "_pagina": "https://www.wowhead.com/pt/item=250001",
    }
    pt_bruto = {
        "nome": "Lâmina do Vazio Forjado",
        "item_level": 341,
        "qualidade": 4,
        "icone_url": "inv_sword_2h_d_01",
        "_contexto": FIXTURE_TOOLTIP_PT,
    }
    en_bruto = {
        "nome": "Voidforged Blade",
        "item_level": 341,
        "qualidade": 4,
        "icone_url": "inv_sword_2h_d_01",
        "_contexto": FIXTURE_TOOLTIP_EN,
    }
    return finalizar_item_bilingue(
        bruto,
        pt_bruto,
        en_bruto,
        "https://www.wowhead.com/pt/item=250001",
        "https://www.wowhead.com/item=250001",
    )


def test_campos_obrigatorios_presentes_e_tipados() -> None:
    """Toda chave obrigatória existe, tem o tipo certo e não é `None`."""
    item = _item_finalizado()
    for campo, tipo in CAMPOS_OBRIGATORIOS.items():
        assert campo in item, f"campo obrigatório ausente: {campo}"
        assert item[campo] is not None, f"campo obrigatório None: {campo}"
        assert isinstance(item[campo], tipo), (
            f"{campo}: esperado {tipo.__name__}, veio {type(item[campo]).__name__}"
        )


def test_fontes_usam_escalas_validas() -> None:
    """As fontes rastreadas pertencem às escalas documentadas."""
    item = _item_finalizado()
    assert item["nome_ptbr_fonte"] in FONTES_NOME, item["nome_ptbr_fonte"]
    assert item["nome_en_fonte"] in FONTES_NOME, item["nome_en_fonte"]
    assert item["icone_fonte"] in FONTES_ICONE, item["icone_fonte"]
    assert item["atributos_fonte"] in FONTES_ATRIBUTOS, item["atributos_fonte"]

    assert item["nome_ptbr_fonte"] == "crawl_ptbr"
    assert item["nome_en_fonte"] == "crawl_en"
    assert item["icone_fonte"] == "cdn_inferido"
    assert item["atributos_fonte"] == "tooltip_pagina"


def test_icone_usa_cdn_oficial() -> None:
    """`icone_url` normalizado para o CDN `wow.zamimg.com` em `/large/`."""
    item = _item_finalizado()
    assert item["icone_url"].startswith(
        "https://wow.zamimg.com/images/wow/icons/large/"
    ), item["icone_url"]
    assert item["icone_url"].endswith(".jpg")


def test_tooltips_gerados_por_idioma() -> None:
    """Tooltip PT usa nome PT; tooltip EN usa nome EN (sem tradução cruzada)."""
    item = _item_finalizado()
    assert item["tooltip_raidbots"].startswith("Lâmina do Vazio Forjado (ilvl 341)")
    assert item["tooltip_raidbots_en"].startswith("Voidforged Blade (ilvl 341)")
    assert "Lâmina do Vazio Forjado" not in item["tooltip_raidbots_en"]
    assert "Voidforged Blade" not in item["tooltip_raidbots"]
    assert "  +1420 Força" in item["tooltip_raidbots"]
    assert "  +1420 Strength" in item["tooltip_raidbots_en"]


def test_atributos_vazios_permanecem_dict_e_fonte_ausente() -> None:
    """Sem tooltip, atributos são `{}` (não zeros fictícios) e fonte ausente."""
    bruto = {
        "id": "250002",
        "nome": "Berloque Etéreo",
        "item_level": 318,
        "qualidade": 4,
        "icone_url": "",
        "bonus_ids": [],
        "url": "https://www.wowhead.com/pt/item=250002",
        "_pagina": "https://www.wowhead.com/pt/item=250002",
    }
    item = finalizar_item_bilingue(bruto, {}, {}, bruto["url"], "")
    assert item["atributos_primarios"] == {}
    assert item["atributos_secundarios"] == {}
    assert item["atributos_fonte"] == "ausente"
    assert item["icone_fonte"] == "ausente"
    assert item["efeito_equip_uso_ptbr"] == ""
    assert item["efeito_equip_uso_en"] == ""
    assert item["bonus_ids"] == []


def test_campos_de_craft_preservados() -> None:
    """Campos já existentes de craft continuam presentes e sem `None`."""
    item = _item_finalizado()
    for campo in (
        "qualidade_craft",
        "qualidade_craft_fonte",
        "profissao_craft",
        "profissao_craft_fonte",
        "craft_indicio",
        "motivo_qualidade_craft",
        "bonus_ids",
        "variante_fonte",
    ):
        assert campo in item, f"campo legado ausente: {campo}"
        if campo == "variante_fonte":
            # Preenchido por `scraper_season2._finalizar`; aqui pode faltar.
            continue
        assert item[campo] is not None, f"campo legado None: {campo}"


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
