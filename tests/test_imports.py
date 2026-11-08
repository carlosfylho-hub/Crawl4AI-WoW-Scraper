#!/usr/bin/env python3
"""Teste de imports dos entrypoints ativos (sem arrastar módulos legados).

Objetivo (PACOTE 5):
- garantir que os módulos ativos importam sem erro;
- garantir que nenhum módulo ``legacy.*`` (e os scrapers antigos da raiz) é
  arrastado apenas por carregar um entrypoint ativo.

Execução:
    python -m pytest -q tests/test_imports.py
    python tests/test_imports.py        # fallback sem pytest
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


#: Entrypoints/módulos ativos após o PACOTE 5.
MODULOS_ATIVOS = [
    "app_streamlit",
    "iniciar_sistema",
    "scraper_season2",
    "scraper_sem_llm",
    "run_scraper",
    "coleta",
    "wow_season2",
    "markdown_season2",
    "recomendacoes",
    "tooltip_client",
    "runtime",
    "config",
    "mcp_server",
]

#: Scrapers legados que não devem ser arrastados por um entrypoint ativo.
#: Os arquivos foram movidos para ``legacy/``; o prefixo ``legacy`` também é
#: verificado em ``test_nao_arrasta_modulos_legados``.
MODULOS_LEGADOS = [
    "scraper",
    "scraper_completo",
]


def _limpar_legados_de_sys_modules() -> None:
    for nome in MODULOS_LEGADOS:
        sys.modules.pop(nome, None)
    for nome in [n for n in sys.modules if n == "legacy" or n.startswith("legacy.")]:
        sys.modules.pop(nome, None)


def test_importa_modulos_ativos() -> None:
    """Todos os módulos ativos devem importar sem erro."""
    for nome in MODULOS_ATIVOS:
        importlib.import_module(nome)


def test_nao_arrasta_modulos_legados() -> None:
    """Importar os ativos não pode colocar os legados em `sys.modules`."""
    _limpar_legados_de_sys_modules()

    for nome in MODULOS_ATIVOS:
        importlib.import_module(nome)

    arrastados = sorted(
        nome
        for nome in sys.modules
        if nome in MODULOS_LEGADOS
        or nome == "legacy"
        or nome.startswith("legacy.")
    )
    assert not arrastados, (
        "Entrypoints ativos arrastaram módulos legados: "
        f"{arrastados}. Use scraper_season2/scraper_sem_llm."
    )


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
            print(f"[FALHOU] {nome}")
            traceback.print_exc()
        else:
            print(f"[OK] {nome}")
    print(f"\n{'FALHAS' if falhas else 'SUCESSO'}: {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
