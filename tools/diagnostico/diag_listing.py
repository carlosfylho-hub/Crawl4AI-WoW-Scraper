"""Diagnóstico: ilvl de itens M+ com bonus de track S2.

Movido de ``data/_diagnostico/`` (F-11). Executar da raiz do projeto::

    python tools/diagnostico/diag_listing.py
"""
import asyncio
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

import runtime  # noqa: E402,F401  (F-09: console UTF-8)

from scraper_season2 import WowheadSeason2Scraper  # noqa: E402
from wow_season2 import extrair_detalhes_item  # noqa: E402


async def main() -> None:
    s = WowheadSeason2Scraper(
        max_itens=20, gerar_markdown=False, buscar_ingles=False,
        qualidade_craft_min=5,
    )
    async with s:
        for ident in ("251199", "251232", "273785", "273773", "251185"):
            url = f"https://www.wowhead.com/pt/item={ident}?bonus=12846"
            itens, falha = await s.coletar_url(url, "Geral")
            if falha:
                print(ident, "falha", falha)
                continue
            it = itens[0]
            print(ident, "bonus", it.get("bonus_ids"), "ilvl_list", it.get("item_level"))
            u, html, _ = await s._crawl_locale(it, "ptbr")
            d = extrair_detalhes_item(html, s._base_locale(it, "ptbr"))
            print("   ", u, "len", len(html), "ilvl", d.get("item_level"),
                  "nome", (d.get("nome") or "")[:30])


asyncio.run(main())
