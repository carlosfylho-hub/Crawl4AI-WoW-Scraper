#!/usr/bin/env python3
"""
Testes offline do fallback LLM (P-08).

Nenhuma chamada real: `completar` é injetado. Cobrem campos, normalização,
JSON inválido, exceção e a regra de não sobrescrever dados já extraídos.

Execução:
    python -m pytest -q tests/test_llm_fallback.py
    python tests/test_llm_fallback.py     # fallback sem pytest
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

RESPOSTA_OK = json.dumps(
    {
        "nome_ptbr": "Elmo de Teste",
        "nome_en": "Test Helm",
        "icone": "inv_helm_cloth",
        "atributos_primarios": {"Intelecto": 1234},
        "atributos_secundarios": {"Aceleração": 500},
    },
    ensure_ascii=False,
)


def _completar_fixo(texto: str):
    return lambda prompt, conteudo: texto  # noqa: ARG005


def test_faltando_campos_llm() -> None:
    from wow_season2 import faltando_campos_llm

    completo = {
        "nome_ptbr": "X",
        "nome_en": "Y",
        "icone_url": "https://x/y.jpg",
        "atributos_primarios": {"A": 1},
        "atributos_secundarios": {},
    }
    assert faltando_campos_llm(completo) is False

    # Um nome em qualquer idioma basta (regra: faltar nome_ptbr E nome_en).
    apenas_en = dict(completo)
    apenas_en["nome_ptbr"] = ""
    assert faltando_campos_llm(apenas_en) is False

    sem_nome = dict(completo)
    sem_nome["nome_ptbr"] = ""
    sem_nome["nome_en"] = ""
    assert faltando_campos_llm(sem_nome) is True

    for campo in ("icone_url", "atributos_primarios"):
        parcial = dict(completo)
        parcial[campo] = "" if campo != "atributos_primarios" else {}
        assert faltando_campos_llm(parcial) is True, campo


def test_extrair_com_llm_mock() -> None:
    from wow_season2 import _extrair_com_llm

    dados = _extrair_com_llm("texto", {}, _completar_fixo(RESPOSTA_OK))

    assert dados["_llm_usado"] is True, dados
    assert dados["_llm_erro"] == "", dados
    assert dados["nome_ptbr"] == "Elmo de Teste", dados
    assert dados["nome_en"] == "Test Helm", dados
    assert dados["icone_url"].endswith("inv_helm_cloth.jpg"), dados
    assert dados["atributos_primarios"] == {"Intelecto": 1234}, dados
    assert dados["atributos_secundarios"] == {"Aceleração": 500}, dados
    assert set(dados["_llm_campos"]) == {
        "nome_ptbr",
        "nome_en",
        "icone_url",
        "atributos_primarios",
        "atributos_secundarios",
    }, dados["_llm_campos"]


def test_llm_json_invalido_nao_quebra() -> None:
    from wow_season2 import _extrair_com_llm

    dados = _extrair_com_llm("texto", {}, _completar_fixo("{nao-json"))

    assert dados["_llm_usado"] is False
    assert dados["_llm_erro"], dados


def test_llm_excecao_nao_quebra() -> None:
    from wow_season2 import _extrair_com_llm

    def explode(prompt, texto):  # noqa: ARG001
        raise RuntimeError("sem chave")

    dados = _extrair_com_llm("texto", {}, explode)

    assert dados["_llm_usado"] is False
    assert "sem chave" in dados["_llm_erro"], dados


def test_atributos_invalidos_sao_ignorados() -> None:
    from wow_season2 import _extrair_com_llm

    resposta = json.dumps(
        {
            "nome_ptbr": "X",
            "atributos_primarios": {"Intelecto": "abc", "Aceleração": 10},
        }
    )
    dados = _extrair_com_llm("texto", {}, _completar_fixo(resposta))

    assert dados["atributos_primarios"] == {"Aceleração": 10}, dados


def test_aplicar_llm_preenche_com_fontes() -> None:
    from wow_season2 import aplicar_llm_em_item

    item = {"nome_ptbr": "", "icone_url": "", "atributos_primarios": {}}
    aplicar_llm_em_item(item, "texto", _completar_fixo(RESPOSTA_OK))

    assert item["nome_ptbr"] == "Elmo de Teste", item
    assert item["nome_ptbr_fonte"] == "llm", item
    assert item["nome_en_fonte"] == "llm", item
    assert item["icone_fonte"] == "llm", item
    assert item["atributos_fonte"] == "llm", item
    assert item["_llm_usado"] is True, item


def test_aplicar_llm_nao_sobrescreve_nem_chama_quando_completo() -> None:
    from wow_season2 import aplicar_llm_em_item

    chamadas = {"n": 0}

    def contar(prompt, texto):  # noqa: ARG001
        chamadas["n"] += 1
        return RESPOSTA_OK

    item = {
        "nome_ptbr": "Existente",
        "nome_en": "Existing",
        "icone_url": "https://x/existente.jpg",
        "atributos_primarios": {"A": 1},
    }
    aplicar_llm_em_item(item, "texto", contar)

    assert chamadas["n"] == 0, chamadas
    assert item["nome_ptbr"] == "Existente", item
    assert item["icone_url"] == "https://x/existente.jpg", item


def test_aplicar_llm_nao_sobrescreve_campos_parciais() -> None:
    from wow_season2 import aplicar_llm_em_item

    item = {"nome_ptbr": "Existente"}
    aplicar_llm_em_item(item, "texto", _completar_fixo(RESPOSTA_OK))

    assert item["nome_ptbr"] == "Existente", item
    assert "nome_ptbr_fonte" not in item, item
    assert item["nome_en"] == "Test Helm", item


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
