#!/usr/bin/env python3
"""
Testes offline do contrato ampliado de `tooltip_client` (P-04).

Cobrem os 11 campos do contrato, a separação nome PT-BR/EN por locale, a
invalidação de cache antigo (4 campos) e o fallback HTML. Nenhuma chamada de
rede: `fetch` é injetado.

Execução:
    python -m pytest -q tests/test_tooltip_client_campos.py
    python tests/test_tooltip_client_campos.py     # fallback sem pytest
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

FIXTURE_JSON = json.dumps(
    {
        "name": "Feixe de Presas Protetoras",
        "quality": "4",
        "icon": "inv_121_jewelry_neck03_teal",
        "spells": "[]",
        "tooltip": (
            "<b>Feixe de Presas Protetoras</b><br>"
            "Nível do Item: 341<br>"
            "+ 1.234 Intelecto<br>"
            "+ 500 Aceleração<br>"
            "Herói 6/6"
        ),
    },
    ensure_ascii=False,
)


def _consultar(fetch, locale=8):
    from tooltip_client import TooltipCache, consultar_tooltip

    with tempfile.TemporaryDirectory() as tmp:
        cache = TooltipCache(os.path.join(tmp, "tooltips.json"))
        return consultar_tooltip(
            "273781", ["12856"], locale=locale, cache=cache, fetch=fetch
        )


def _fetch_fixo(texto):
    def fetch(url, timeout):  # noqa: ARG001 - assinatura do cliente
        return texto

    return fetch


def test_contrato_completo_locale_ptbr() -> None:
    from tooltip_client import CHAVES_CONTRATO_TOOLTIP

    dados = _consultar(_fetch_fixo(FIXTURE_JSON), locale=8)

    assert dados is not None
    faltando = [c for c in CHAVES_CONTRATO_TOOLTIP if c not in dados]
    assert not faltando, faltando
    assert dados["nome"] == "Feixe de Presas Protetoras"
    assert dados["nome_ptbr"] == "Feixe de Presas Protetoras"
    assert dados["nome_en"] == ""
    assert dados["item_level"] == 341
    assert dados["qualidade"] == 4
    assert dados["track_rotulo"]
    assert dados["icone_url"].endswith("inv_121_jewelry_neck03_teal.jpg")
    assert dados["atributos_primarios"] == {"Intelecto": 1234}
    assert dados["atributos_secundarios"] == {"Aceleração": 500}
    assert dados["bonus_ids"] == ["12856"]
    assert "Nível do Item: 341" in dados["tooltip_html"]


def test_locale_en_preenche_nome_en() -> None:
    dados = _consultar(_fetch_fixo(FIXTURE_JSON), locale=0)

    assert dados is not None
    assert dados["nome_en"] == "Feixe de Presas Protetoras"
    assert dados["nome_ptbr"] == ""


def test_cache_antigo_incompleto_e_ignorado() -> None:
    from tooltip_client import TooltipCache, consultar_tooltip

    with tempfile.TemporaryDirectory() as tmp:
        cache = TooltipCache(os.path.join(tmp, "tooltips.json"))
        cache.gravar(
            "273781",
            ["12856"],
            {"nome": "velho", "item_level": 1, "track_rotulo": "", "qualidade": 0},
            locale=8,
        )

        chamadas = {"n": 0}

        def fetch(url, timeout):  # noqa: ARG001
            chamadas["n"] += 1
            return FIXTURE_JSON

        dados = consultar_tooltip(
            "273781", ["12856"], locale=8, cache=cache, fetch=fetch
        )

    assert chamadas["n"] == 1, chamadas
    assert dados is not None and dados["item_level"] == 341


def test_fallback_html_sem_json() -> None:
    html = (
        "<b>Item Mock</b><br>Nível do Item: 320<br>"
        "+ 100 Intelecto<br>+ 40 Maestria"
    )
    dados = _consultar(_fetch_fixo(html))

    assert dados is not None
    assert dados["nome"] == "Item Mock"
    assert dados["item_level"] == 320
    assert dados["atributos_primarios"] == {"Intelecto": 100}
    assert dados["atributos_secundarios"] == {"Maestria": 40}
    assert dados["icone_url"] == ""
    assert dados["bonus_ids"] == ["12856"]


def test_sem_icone_nao_quebra() -> None:
    payload = json.loads(FIXTURE_JSON)
    payload.pop("icon")
    dados = _consultar(_fetch_fixo(json.dumps(payload, ensure_ascii=False)))

    assert dados is not None
    assert dados["icone_url"] == ""


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
