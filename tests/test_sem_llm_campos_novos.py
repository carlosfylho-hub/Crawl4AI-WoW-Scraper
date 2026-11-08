#!/usr/bin/env python3
"""
Testes offline dos campos novos das dataclasses legadas (P-06/F-08).

Garante que `asdict` continua funcionando e que os adapters preenchem ícone,
nome EN, atributos e tooltip Raidbots.

Execução:
    python -m pytest -q tests/test_sem_llm_campos_novos.py
    python tests/test_sem_llm_campos_novos.py     # fallback sem pytest
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

CAMPOS_NOVOS = (
    "icone",
    "nome_en",
    "atributos_primarios",
    "atributos_secundarios",
    "tooltip_raidbots",
)

DADO = {
    "id": 273781,
    "nome_ptbr": "Feixe de Presas Protetoras",
    "nome_en": "Bundle of Protective Fangs",
    "icone_url": (
        "https://wow.zamimg.com/images/wow/icons/large/"
        "inv_121_jewelry_neck03_teal.jpg"
    ),
    "atributos_primarios": {"Intelecto": 1234},
    "atributos_secundarios": {"Aceleração": 500},
    "item_level": 341,
    "qualidade": 4,
    "bonus_ids": ["12856"],
    "url": "https://www.wowhead.com/pt/item=273781?bonus=12856",
    "slot": "Colar",
}


def _classes():
    from scraper_sem_llm import (
        EncantamentoFerramenta,
        FerramentaProducao,
        MissivaProfissao,
    )

    return (FerramentaProducao, EncantamentoFerramenta, MissivaProfissao)


def test_dataclasses_expoem_campos_novos() -> None:
    for cls in _classes():
        campos = cls.__dataclass_fields__
        for nome in CAMPOS_NOVOS:
            assert nome in campos, (cls.__name__, nome)


def test_asdict_com_defaults_nao_quebra() -> None:
    for cls in _classes():
        obj = cls(
            id_item_completo="item=273781",
            nome_ptbr="X",
            profissao="P",
            qualidade="4",
            item_level=341,
            rank=5,
            atributo_tipo="",
            atributo_valor=0,
            bonus_ids=["12856"],
            url="https://www.wowhead.com/pt/item=273781",
        )
        dados = asdict(obj)
        assert dados["icone"] == "", dados
        assert dados["nome_en"] == "", dados
        assert dados["atributos_primarios"] == {}, dados
        assert dados["atributos_secundarios"] == {}, dados
        assert isinstance(dados["tooltip_raidbots"], str), dados


def test_adapters_preenchem_campos_novos() -> None:
    from scraper_sem_llm import (
        dict_para_encantamento,
        dict_para_ferramenta,
        dict_para_missiva,
    )

    for funcao in (dict_para_ferramenta, dict_para_encantamento, dict_para_missiva):
        obj = funcao(dict(DADO))
        assert obj.icone == DADO["icone_url"], (funcao.__name__, obj.icone)
        assert obj.nome_en == DADO["nome_en"], funcao.__name__
        assert obj.atributos_primarios == {"Intelecto": 1234}, funcao.__name__
        assert obj.atributos_secundarios == {"Aceleração": 500}, funcao.__name__
        assert isinstance(obj.tooltip_raidbots, str), funcao.__name__

        dados = asdict(obj)
        for nome in CAMPOS_NOVOS:
            assert nome in dados, (funcao.__name__, nome)


def test_icone_ausente_fica_vazio() -> None:
    from scraper_sem_llm import dict_para_ferramenta

    dado = dict(DADO)
    dado.pop("icone_url")
    obj = dict_para_ferramenta(dado)
    assert obj.icone == ""


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
