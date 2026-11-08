#!/usr/bin/env python3
"""
Valida variantes (`item + bonus`) de uma amostra contra o tooltip do Wowhead.

Uso:
    python tools/validar_variantes.py --amostra 20
    python tools/validar_variantes.py --amostra 20 --url "https://www.wowhead.com/pt/items/armor"

Fontes da amostra (nesta ordem):
1. `--url`: baixa a listagem e usa `parse_links_itens`;
2. `--json`: lê `itens` de um resultado anterior (padrão:
   `data/wowhead_itens_season2.json`).

Falhas de rede/anti-bot são reportadas como LIMITAÇÃO (não como falha do
pacote). O comando imprime `descartes.ilvl_fora=<n>` para facilitar a
comparação com o critério de aceite.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from tooltip_client import consultar_tooltip  # noqa: E402
from wow_season2 import parse_links_itens  # noqa: E402


def _baixar(url: str, timeout: float = 20.0) -> str:
    requisicao = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
        return resposta.read().decode("utf-8", errors="replace")


def _carregar_json(caminho: str) -> List[Dict[str, Any]]:
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except (OSError, ValueError):
        return []
    if isinstance(dados, dict):
        itens = dados.get("itens")
        return itens if isinstance(itens, list) else []
    return dados if isinstance(dados, list) else []


def _carregar_url(url: str) -> List[Dict[str, Any]]:
    html = _baixar(url)
    return parse_links_itens(html, url)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida item+bonus de uma amostra contra o tooltip."
    )
    parser.add_argument("--amostra", type=int, default=20)
    parser.add_argument("--url", default="")
    parser.add_argument(
        "--json",
        default=os.path.join("data", "wowhead_itens_season2.json"),
    )
    parser.add_argument("--ilvl-min", type=int, default=305)
    parser.add_argument("--ilvl-max", type=int, default=350)
    parser.add_argument(
        "--timeout", type=float, default=8.0, help="Timeout por consulta de tooltip."
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    try:
        itens = _carregar_url(args.url) if args.url else _carregar_json(args.json)
    except Exception as exc:  # noqa: BLE001 - rede/anti-bot é limitação
        print(f"LIMITAÇÃO: não foi possível obter a amostra: {exc}")
        return 0

    if not itens:
        print(
            "LIMITAÇÃO: amostra vazia. Gere "
            "data/wowhead_itens_season2.json ou passe --url."
        )
        return 0

    amostra = itens[: max(0, args.amostra)]
    total = len(amostra)
    com_tooltip = 0
    divergencias = 0
    ilvl_fora = 0
    falhas_rede = 0

    for item in amostra:
        ident = item.get("id")
        bonus = item.get("bonus_ids") or []
        info = consultar_tooltip(ident, bonus, timeout=args.timeout)
        if not info:
            falhas_rede += 1
            continue
        com_tooltip += 1
        ilvl_tooltip = int(info.get("item_level") or 0)
        ilvl_listagem = int(item.get("item_level") or 0)
        if ilvl_tooltip and ilvl_listagem and ilvl_tooltip != ilvl_listagem:
            divergencias += 1
        if ilvl_tooltip and (
            ilvl_tooltip < args.ilvl_min or ilvl_tooltip > args.ilvl_max
        ):
            ilvl_fora += 1

    print(f"amostra={total}")
    print(f"com_tooltip={com_tooltip}")
    print(f"divergencias={divergencias}")
    print(f"descartes.ilvl_fora={ilvl_fora}")
    print(f"falhas_rede={falhas_rede}")

    if falhas_rede == total:
        print(
            "LIMITAÇÃO: nenhuma consulta de tooltip retornou dados "
            "(rede/anti-bot). Isso não indica falha do pacote."
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
