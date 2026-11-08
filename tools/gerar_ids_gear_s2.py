#!/usr/bin/env python3
"""Gera ``data/season2_gear_ids.json`` a partir do banco de loot M+ (F-01/P-01b).

Motivo: o Wowhead **não** aplica filtro de `ilvl`/`bonus` server-side na
listagem (`/items?...`), então o crawl headless recebe o banco genérico de
itens. A fonte confiável de gear da Season 2 é a lista curada de IDs em
[`base_conhecimento_ai_studio/mplus_loot_database.md`](../base_conhecimento_ai_studio/mplus_loot_database.md).

Este script extrai os IDs das tabelas Markdown e grava o artefato consumido por
`config.SEASON2_GEAR_IDS`. É determinístico e não acessa a rede.

Uso::

    python tools/gerar_ids_gear_s2.py
    python tools/gerar_ids_gear_s2.py --saida data/season2_gear_ids.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
ORIGEM_PADRAO = (
    RAIZ_PROJETO / "base_conhecimento_ai_studio" / "mplus_loot_database.md"
)
DESTINO_PADRAO = RAIZ_PROJETO / "data" / "season2_gear_ids.json"

#: IDs de item nas tabelas Markdown aparecem como ``| 273781 |``.
_RE_ID_TABELA = re.compile(r"\|\s*(\d{5,6})\s*\|")


def extrair_ids(markdown: str) -> list:
    """Extrai IDs únicos (ordem de aparição) das tabelas Markdown."""
    vistos = set()
    ids = []
    for bruto in _RE_ID_TABELA.findall(markdown or ""):
        ident = str(bruto).strip()
        if not ident.isdigit() or ident in vistos:
            continue
        vistos.add(ident)
        ids.append(ident)
    return ids


def _parse_args() -> argparse.Namespace:  # pragma: no cover - CLI
    parser = argparse.ArgumentParser(
        description="Extrai os IDs de gear da Season 2 do banco de loot M+."
    )
    parser.add_argument(
        "--origem",
        default=str(ORIGEM_PADRAO),
        help="Markdown de origem (padrão: banco de loot M+).",
    )
    parser.add_argument(
        "--saida",
        default=str(DESTINO_PADRAO),
        help="JSON de saída (padrão: data/season2_gear_ids.json).",
    )
    return parser.parse_args()


def main() -> int:  # pragma: no cover - CLI
    args = _parse_args()
    origem = Path(args.origem)
    try:
        markdown = origem.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[FAIL] não foi possível ler {origem}: {exc}")
        return 1

    ids = extrair_ids(markdown)
    if not ids:
        print(f"[FAIL] nenhum ID encontrado em {origem}")
        return 1

    destino = Path(args.saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    dados = {
        "fonte": origem.name,
        "descricao": "IDs de gear da Season 2 extraídos do banco de loot M+",
        "total": len(ids),
        "ids": ids,
    }
    destino.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"[OK] {len(ids)} IDs gravados em {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
