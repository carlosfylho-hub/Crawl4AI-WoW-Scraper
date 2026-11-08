#!/usr/bin/env python3
"""
Testes offline do mapa receita→profissão por ID (P-07/F-06).

Regressão: em `craft_armas_s2.json` os IDs são as **chaves** do mapa
(`"237831": {"profissao": ...}`), não campos `id`. O scanner antigo só lia
campos, então armas craftadas ficavam sem profissão e `qualidade_craft=0`.

Execução:
    python -m pytest -q tests/test_mapa_craft_ids.py
    python tests/test_mapa_craft_ids.py     # fallback sem pytest
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


def test_mapa_tem_ids_como_chave() -> None:
    from wow_season2 import _mapa_craft

    mapa = _mapa_craft()
    assert len(mapa.get("id") or {}) >= 50, len(mapa.get("id") or {})


def test_armas_craftadas_resolvem_profissao() -> None:
    from wow_season2 import profissao_por_receita

    assert profissao_por_receita("237831") == "Ferraria"
    assert profissao_por_receita("237839") == "Ferraria"


def test_id_desconhecido_retorna_vazio() -> None:
    from wow_season2 import profissao_por_receita

    assert profissao_por_receita("999999") == ""
    assert profissao_por_receita("") == ""


def test_varrer_mapa_registra_chave_numerica() -> None:
    from wow_season2 import _varrer_mapa_craft

    mapas: dict = {}
    _varrer_mapa_craft(
        {"armas": {"123456": {"profissao": "Ferraria", "nome": "X"}}},
        "",
        mapas,
    )
    assert mapas["id"]["123456"] == "Ferraria", mapas


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
