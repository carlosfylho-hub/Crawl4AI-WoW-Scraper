#!/usr/bin/env python3
"""Diagnóstico: de onde vêm os bonus_ids na listagem padrão.

Baixa o HTML da listagem, salva em ``data/_diagnostico/_listagem.html`` e
mostra todos os anchors que apontam para os itens suspeitos
(268265 / 252258), com o container da linha.

Movido de ``data/_diagnostico/`` (F-11). Executar da raiz do projeto::

    python tools/diagnostico/valida_anchors_bonus.py
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import runtime  # noqa: E402,F401  (F-09: console UTF-8)

from bs4 import BeautifulSoup  # noqa: E402

from config import SEASON2_ITEM_URLS  # noqa: E402
from scraper_season2 import WowheadSeason2Scraper  # noqa: E402

DIR_SAIDA = RAIZ / "data" / "_diagnostico"
SAIDA = DIR_SAIDA / "_listagem.html"


async def main() -> None:
    url = SEASON2_ITEM_URLS[0]
    scraper = WowheadSeason2Scraper(buscar_detalhes=False, gerar_markdown=False)
    async with scraper:
        result = await scraper.crawler.arun(url=url, config=scraper._run_config())
    html = getattr(result, "html", "") or ""
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(html, encoding="utf-8")
    print("html salvo:", SAIDA, len(html), "bytes")

    soup = BeautifulSoup(html, "html.parser")
    anchors = soup.select("a[href*='item='], a[data-wowhead*='item=']")
    print("anchors:", len(anchors))

    for alvo in ("268265", "252258"):
        print("=" * 70)
        print("ITEM", alvo)
        achados = [
            a
            for a in anchors
            if alvo in (a.get("href") or "")
            or alvo in (a.get("data-wowhead") or "")
        ]
        print("occurrences:", len(achados))
        vistos = set()
        for a in achados[:12]:
            chave = ((a.get("href") or ""), (a.get("data-wowhead") or ""))
            if chave in vistos:
                continue
            vistos.add(chave)
            pai = a.find_parent(["tr", "li"])
            print(
                {
                    "href": a.get("href"),
                    "data-wowhead": a.get("data-wowhead"),
                    "class": a.get("class"),
                    "nome_anchor": a.get_text(" ", strip=True)[:40],
                    "pai_tag": pai.name if pai is not None else None,
                    "pai_id": (pai.get("id") if pai is not None else None),
                    "pai_texto": (
                        pai.get_text(" ", strip=True)[:110] if pai is not None else ""
                    ),
                }
            )
        print("-- data-wowhead com bonus contendo o item --")
        pat = re.compile(r"item=%s[^\"']*bonus=([\d:]+)" % alvo)
        for a in anchors:
            dw = a.get("data-wowhead") or ""
            m = pat.search(dw)
            if m:
                print("dw:", dw[:120])


if __name__ == "__main__":
    asyncio.run(main())
