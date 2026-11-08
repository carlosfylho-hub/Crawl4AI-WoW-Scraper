#!/usr/bin/env python3
"""Teste automatizado (offline) da UI Streamlit — PACOTE 5, pendência 8.

Objetivo:
- garantir que ``app_streamlit.py`` renderiza sem exceção;
- confirmar as 4 abas (Dashboard, Extrair, Resultados, Recomendações);
- confirmar os defaults ``Raridade mínima = 4`` e ``Qualidade de craft (R) = 5``;
- alternar entre as categorias de extração sem disparar exceções.

Sem rede: o botão de scraping **não** é acionado. Apenas renderização/estado.

Execução:
    python -m pytest -q tests/test_app_streamlit.py
    python tests/test_app_streamlit.py        # fallback sem pytest

Limitação: se a versão instalada do Streamlit não fornecer
``streamlit.testing.v1.AppTest``, os testes de UI são pulados e roda-se um
teste alternativo (import do módulo + inspeção de ``CFG``).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, List

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

APP_PATH = RAIZ_PROJETO / "app_streamlit.py"

try:  # AppTest existe a partir do Streamlit 1.28
    from streamlit.testing.v1 import AppTest  # type: ignore

    APPTEST_DISPONIVEL = True
except Exception:  # pragma: no cover - depende da versão instalada
    AppTest = None  # type: ignore
    APPTEST_DISPONIVEL = False


def _novo_app() -> Any:
    """Cria e executa o app uma vez, sem interação (sem rede)."""
    assert AppTest is not None
    return AppTest.from_file(str(APP_PATH), default_timeout=180).run()


def _rotulo_excecoes(at: Any) -> List[str]:
    return [str(exc) for exc in at.exception]


def _multiselect_categorias(at: Any) -> Any:
    """Localiza o multiselect "Categorias" na árvore atual do app."""
    for elemento in at.multiselect:
        if getattr(elemento, "label", "") == "Categorias":
            return elemento
    raise AssertionError("multiselect 'Categorias' não encontrado")


def test_quatro_abas_sem_excecao() -> None:
    """O app deve renderizar 4 abas e nenhuma exceção."""
    if not APPTEST_DISPONIVEL:
        print("[SKIP] AppTest indisponível nesta versão do Streamlit.")
        return

    at = _novo_app()
    assert not at.exception, _rotulo_excecoes(at)
    assert len(at.tabs) == 4, f"esperava 4 abas, encontrei {len(at.tabs)}"


def test_defaults_raridade_e_craft() -> None:
    """Defaults: Raridade mínima = 4 e Qualidade de craft (R) = 5."""
    if not APPTEST_DISPONIVEL:
        print("[SKIP] AppTest indisponível nesta versão do Streamlit.")
        return

    at = _novo_app()
    valores = {box.label: box.value for box in at.selectbox}
    assert valores.get("Raridade mínima") == 4, valores
    assert valores.get("Qualidade de craft (R)") == 5, valores


def test_alternar_categorias_sem_excecao() -> None:
    """Trocar cada categoria não pode produzir exceção no app."""
    if not APPTEST_DISPONIVEL:
        print("[SKIP] AppTest indisponível nesta versão do Streamlit.")
        return

    from config import CATEGORIAS_WOW

    at = _novo_app()
    for chave in CATEGORIAS_WOW:
        _multiselect_categorias(at).set_value([chave])
        at.run()
        assert not at.exception, f"{chave}: {_rotulo_excecoes(at)}"


def test_fallback_import_e_defaults_em_cfg() -> None:
    """Alternativa sem AppTest: importa o app e inspeciona o ``CFG``."""
    import importlib

    modulo = importlib.import_module("app_streamlit")
    cfg = getattr(modulo, "CFG", {})
    assert cfg, "app_streamlit não expôs CFG"
    assert cfg.get("qualidade_min") == 4, cfg
    assert cfg.get("qualidade_craft_min") == 5, cfg


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
