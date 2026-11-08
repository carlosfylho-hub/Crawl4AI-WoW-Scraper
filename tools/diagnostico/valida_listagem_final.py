#!/usr/bin/env python3
"""Diagnóstico da validação final (não faz parte do produto).

Crawl da URL padrão de listagem e inspeção das linhas brutas:
quantos ids distintos, quais ilvl de listagem e de onde vêm os bonus_ids.

Movido de ``data/_diagnostico/`` (F-11). Executar da raiz do projeto::

    python tools/diagnostico/valida_listagem_final.py
"""
from __future__ import annotations

import asyncio
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import runtime  # noqa: E402,F401  (F-09: console UTF-8)

from config import SEASON2_ITEM_URLS  # noqa: E402
from scraper_season2 import WowheadSeason2Scraper  # noqa: E402


async def main() -> None:
    url = SEASON2_ITEM_URLS[0]
    print("URL:", url)
    scraper = WowheadSeason2Scraper(buscar_detalhes=False, gerar_markdown=False)
    async with scraper:
        itens, falha = await scraper.coletar_url(url, "Geral")
    print("falha:", falha)
    print("linhas brutas:", len(itens))
    ids = Counter(str(i.get("id")) for i in itens)
    print("ids distintos:", len(ids))
    print("top ids:", ids.most_common(5))
    print("ilvl de listagem:", Counter(i.get("item_level") for i in itens).most_common(8))
    print("variante_fonte:", Counter(i.get("variante_fonte") for i in itens))
    print("--- primeiras 8 linhas ---")
    for i in itens[:8]:
        print(
            {
                "id": i.get("id"),
                "nome": i.get("nome"),
                "item_level": i.get("item_level"),
                "bonus_ids": i.get("bonus_ids"),
                "variante_fonte": i.get("variante_fonte"),
                "track_stage": i.get("track_stage"),
            }
        )


if __name__ == "__main__":
    asyncio.run(main())
