#!/usr/bin/env python3
"""Testes offline de `tooltip_raidbots.montar_tooltip_raidbots`.

Cobre:
(a) item completo PT-BR com todas as linhas na ordem exata;
(b) item completo EN com rótulos EN;
(c) ausência de `bonus_ids` omite a linha;
(d) ausência de efeito omite `Equipar:`;
(e) `qualidade_craft <= 0` omite a linha de craft;
(f) atributos vazios não geram linhas em branco;
(g) dict vazio retorna string sem exceção;
(h) nenhum percentual é inventado.

Execução:
    python -m pytest -q tests/test_tooltip_raidbots.py
    python tests/test_tooltip_raidbots.py       # fallback sem pytest
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from tooltip_raidbots import montar_tooltip_raidbots  # noqa: E402

ITEM_PT = {
    "nome_ptbr": "Lâmina do Vazio Forjado",
    "nome_en": "Voidforged Blade",
    "item_level": 341,
    "slot": "Arma de 2 Mãos",
    "tipo_armadura": "Placas",
    "atributos_primarios": {"Força": 1420, "Vigor": 2850},
    "atributos_secundarios": {"Acerto Crítico": 850, "Maestria": 620},
    "efeito_equip_uso_ptbr": "Seus golpes têm chance de liberar energia do Vazio.",
    "efeito_equip_uso_en": "Your strikes have a chance to unleash Void energy.",
    "bonus_ids": ["12838", "12839"],
    "qualidade_craft": 5,
    "profissao_craft": "Ferraria",
}

ESPERADO_PT = """Lâmina do Vazio Forjado (ilvl 341)
Arma de 2 Mãos / Placas
  +1420 Força
  +2850 Vigor
  +850 Acerto Crítico
  +620 Maestria
Equipar: Seus golpes têm chance de liberar energia do Vazio.
Bônus IDs: 12838:12839
Qualidade de craft: R5 (Ferraria)"""


def test_item_completo_ptbr_ordem_exata() -> None:
    """(a) Todas as linhas, na ordem e indentação exatas."""
    assert montar_tooltip_raidbots(ITEM_PT, "ptbr") == ESPERADO_PT


def test_item_completo_en_usa_rotulos_en() -> None:
    """(b) Rótulos EN para stats e nome/efeito da fonte EN."""
    obtido = montar_tooltip_raidbots(ITEM_PT, "en")
    assert "Voidforged Blade (ilvl 341)" in obtido
    assert "  +1420 Strength" in obtido
    assert "  +2850 Stamina" in obtido
    assert "  +850 Critical Strike" in obtido
    assert "  +620 Mastery" in obtido
    assert "Equipar: Your strikes have a chance to unleash Void energy." in obtido
    # Nome PT não pode ser usado no tooltip EN (e vice-versa).
    assert "Lâmina do Vazio Forjado" not in obtido


def test_sem_bonus_ids_omite_linha() -> None:
    """(c) Lista de Bonus IDs vazia não gera a linha."""
    item = dict(ITEM_PT)
    item["bonus_ids"] = []
    obtido = montar_tooltip_raidbots(item)
    assert "Bônus IDs" not in obtido


def test_sem_efeito_omite_equipar() -> None:
    """(d) Efeito vazio não gera `Equipar:`."""
    item = dict(ITEM_PT)
    item["efeito_equip_uso_ptbr"] = ""
    obtido = montar_tooltip_raidbots(item)
    assert "Equipar:" not in obtido


def test_qualidade_craft_zero_omite_linha() -> None:
    """(e) Sem qualidade de craft, a última linha é omitida."""
    item = dict(ITEM_PT)
    item["qualidade_craft"] = 0
    obtido = montar_tooltip_raidbots(item)
    assert "Qualidade de craft" not in obtido


def test_atributos_vazios_sem_linhas_em_branco() -> None:
    """(f) Dicts vazios não geram linhas vazias nem espaços à direita."""
    item = {
        "nome_ptbr": "Item Simples",
        "item_level": 305,
        "slot": "",
        "tipo_armadura": "",
        "atributos_primarios": {},
        "atributos_secundarios": {},
        "efeito_equip_uso_ptbr": "",
        "bonus_ids": [],
        "qualidade_craft": 0,
        "profissao_craft": "",
    }
    obtido = montar_tooltip_raidbots(item)
    assert obtido == "Item Simples (ilvl 305)"
    assert "\n\n" not in obtido
    assert not any(linha != linha.rstrip() for linha in obtido.splitlines())


def test_dict_vazio_nao_levanta_excecao() -> None:
    """(g) Entrada inválida/vazia retorna string vazia sem exceção."""
    assert montar_tooltip_raidbots({}) == ""
    assert montar_tooltip_raidbots({}, "en") == ""


def test_sem_percentual_inventado() -> None:
    """(h) Nunca adiciona `%` quando o valor não foi fornecido."""
    item = dict(ITEM_PT)
    item["atributos_secundarios"] = {"Acerto Crítico": 86, "Rapidez": 115}
    obtido = montar_tooltip_raidbots(item)
    assert "%" not in obtido
    assert "+86 Acerto Crítico" in obtido
    # Alias PT "Rapidez" é preservado no idioma PT-BR.
    assert "+115 Rapidez" in obtido


def test_alias_pt_mapeia_para_rotulos_canonicos() -> None:
    """Atributos crus do crawl PT (Aceleração/Crítico) viram rótulos pedidos."""
    item = dict(ITEM_PT)
    item["atributos_secundarios"] = {"Aceleração": 850, "Crítico": 620}
    pt = montar_tooltip_raidbots(item, "ptbr")
    en = montar_tooltip_raidbots(item, "en")
    assert "+850 Rapidez" in pt
    assert "+620 Acerto Crítico" in pt
    assert "+850 Haste" in en
    assert "+620 Critical Strike" in en


def test_rotulo_combinado_localizado() -> None:
    """Escolha combinada é traduzida parte a parte."""
    item = dict(ITEM_PT)
    item["atributos_primarios"] = {"Agilidade ou Intelecto": 189}
    pt = montar_tooltip_raidbots(item, "ptbr")
    en = montar_tooltip_raidbots(item, "en")
    assert "+189 Agilidade ou Intelecto" in pt
    assert "+189 Agility or Intellect" in en


def test_nunca_none_em_atributo() -> None:
    """Valores `None`/0 são omitidos em vez de virar `+0`."""
    item = dict(ITEM_PT)
    item["atributos_primarios"] = {"Força": None, "Vigor": 0}
    obtido = montar_tooltip_raidbots(item)
    assert "+0" not in obtido
    assert "Força" not in obtido


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
