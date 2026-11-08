#!/usr/bin/env python3
"""Diagnóstico (read-only) do funil de descartes da Season 2.

Instrumenta `_finalizar` para imprimir o estado de cada bruto (ilvl de
listagem/página/arbitragem) e, ao final, o resumo de `metadata`.

Não faz parte do pipeline de produção; serve para explicar por que uma
execução limitada (`--max-detalhes N`) termina com zero itens finais.

Uso:
    python tools/diagnostico/diag_descartes.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import scraper_season2 as s  # noqa: E402


_ORIGINAL = s.WowheadSeason2Scraper._finalizar


def _finalizar_instrumentado(self, brutos):  # type: ignore[no-untyped-def]
    for bruto in brutos:
        print(
            "BRUTO",
            bruto.get("id"),
            "| ilvl:", bruto.get("item_level"),
            "| origem:", bruto.get("_ilvl_origem"),
            "| pagina:", bruto.get("_ilvl_pagina"),
            "| listagem:", bruto.get("_ilvl_listagem"),
            "| vfont:", bruto.get("variante_fonte"),
            "| tem_pt:", bool(bruto.get("_pt")),
        )
    return _ORIGINAL(self, brutos)


s.WowheadSeason2Scraper._finalizar = _finalizar_instrumentado  # type: ignore[method-assign]


async def _main() -> None:
    async with s.WowheadSeason2Scraper(
        max_itens=20, max_detalhes=5
    ) as scraper:
        resultado = await scraper.executar()
    meta = resultado["metadata"]
    print("descartes:", meta.get("descartes"))
    print("ilvl_origem:", meta.get("ilvl_origem"))
    print("total_itens:", meta.get("total_itens"))
    for item in resultado.get("itens", []):
        print(
            "FINAL",
            item.get("id"),
            "| ilvl:", item.get("item_level"),
            "| origem:", item.get("ilvl_origem"),
        )


if __name__ == "__main__":
    asyncio.run(_main())
