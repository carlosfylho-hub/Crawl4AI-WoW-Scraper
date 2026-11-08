#!/usr/bin/env python3
"""
Testes offline do contexto de bônus em `tools/validar_craft.py` (P-05/F-02).

O validador precisa usar os `bonus_ids` registrados no JSON canônico; sem eles
a variante muda e o `item_level` diverge do pipeline.

Execução:
    python -m pytest -q tests/test_validar_craft_bonus.py
    python tests/test_validar_craft_bonus.py     # fallback sem pytest
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


def _canonico(caminho: Path) -> Path:
    caminho.write_text(
        json.dumps(
            {
                "metadata": {"total_itens": 3},
                "itens": [
                    {"id": 237831, "bonus_ids": ["12856"]},
                    {"id": "237839", "bonus_ids": []},
                    {"id": 273781, "bonus_ids": ["12856", "13440"]},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return caminho


def test_carregar_bonus_por_id(tmp_path) -> None:
    from tools.validar_craft import carregar_bonus_por_id

    mapa = carregar_bonus_por_id(str(_canonico(tmp_path / "canonico.json")))

    assert mapa == {
        "237831": ["12856"],
        "273781": ["12856", "13440"],
    }, mapa


def test_canonico_ausente_retorna_vazio(tmp_path) -> None:
    from tools.validar_craft import carregar_bonus_por_id

    assert carregar_bonus_por_id(str(tmp_path / "nao_existe.json")) == {}


def test_montar_urls_usa_bonus_do_canonico() -> None:
    from tools.validar_craft import montar_urls_itens

    urls = montar_urls_itens(
        ["237831", "237839", "999999"],
        {"237831": ["12856"], "273781": ["12856", "13440"]},
    )

    assert urls[0] == "https://www.wowhead.com/pt/item=237831?bonus=12856", urls
    assert urls[1] == "https://www.wowhead.com/pt/item=237839", urls
    assert urls[2] == "https://www.wowhead.com/pt/item=999999", urls


def test_montar_urls_usa_bonus_padrao_quando_ausente() -> None:
    from tools.validar_craft import montar_urls_itens

    urls = montar_urls_itens(["237831", "999999"], {}, bonus_padrao="12856")

    assert urls[0] == "https://www.wowhead.com/pt/item=237831?bonus=12856", urls
    assert urls[1] == "https://www.wowhead.com/pt/item=999999?bonus=12856", urls


def test_bonus_do_canonico_tem_prioridade_sobre_padrao() -> None:
    from tools.validar_craft import montar_urls_itens

    urls = montar_urls_itens(
        ["237831"], {"237831": ["12854"]}, bonus_padrao="12856"
    )

    assert urls[0].endswith("bonus=12854"), urls


def test_campos_do_relatorio_incluem_contexto() -> None:
    from tools.validar_craft import CAMPOS_RELATORIO

    assert "bonus_ids" in CAMPOS_RELATORIO
    assert "ilvl_origem" in CAMPOS_RELATORIO


if __name__ == "__main__":  # pragma: no cover - fallback sem pytest
    import tempfile
    import traceback

    falhas = 0
    for nome, funcao in sorted(globals().items()):
        if not (nome.startswith("test_") and callable(funcao)):
            continue
        try:
            if "tmp_path" in funcao.__code__.co_varnames:
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
