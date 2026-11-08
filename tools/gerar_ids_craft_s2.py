#!/usr/bin/env python3
"""Gera ``data/season2_craft_ids.json`` a partir da base de conhecimento (P-13).

O requisito de produto é entregar **somente itens craftados R5 e épicos**. A
lista de IDs de gear de M+ contém drops que não são craftados; esta lista é a
fonte correta quando `exigir_craft` está ligado.

Fontes:
- ``base_conhecimento_ai_studio/craft_receitas_s2.json`` → campo ``id`` de
  cada receita (armaduras, escudos, armas, berloques de alquimia);
- ``base_conhecimento_ai_studio/craft_armas_s2.json`` → chaves numéricas de
  ``armas``.

Uso::

    python tools/gerar_ids_craft_s2.py
    python tools/gerar_ids_craft_s2.py --saida data/season2_craft_ids.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List, Set

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
BASE_CONHECIMENTO = RAIZ_PROJETO / "base_conhecimento_ai_studio"
DESTINO_PADRAO = RAIZ_PROJETO / "data" / "season2_craft_ids.json"

ARQUIVOS = ("craft_receitas_s2.json", "craft_armas_s2.json")


def _coletar_ids(no: Any, encontrados: Set[str]) -> None:
    """Percorre a estrutura coletando `id` numérico e chaves numéricas."""
    if isinstance(no, dict):
        for chave, valor in no.items():
            chave_txt = str(chave).strip()
            if chave_txt.isdigit() and chave_txt != "0":
                encontrados.add(chave_txt)
            if chave in ("id", "item_id", "id_item"):
                valor_txt = str(valor if valor is not None else "").strip()
                if valor_txt.isdigit() and valor_txt != "0":
                    encontrados.add(valor_txt)
            _coletar_ids(valor, encontrados)
    elif isinstance(no, (list, tuple)):
        for valor in no:
            _coletar_ids(valor, encontrados)


def extrair_ids(base: Path = BASE_CONHECIMENTO) -> List[str]:
    """Retorna os IDs únicos (ordem de aparição) das fontes de craft."""
    vistos: Set[str] = set()
    ids: List[str] = []

    for nome in ARQUIVOS:
        caminho = base / nome
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        encontrados: Set[str] = set()
        _coletar_ids(dados, encontrados)
        # Remove IDs que são apenas metadados de reagentes/crests: o filtro
        # final de raridade/craft do pipeline decide o que permanece.
        for ident in sorted(encontrados, key=lambda valor: int(valor)):
            if ident not in vistos:
                vistos.add(ident)
                ids.append(ident)
    return ids


def _parse_args() -> argparse.Namespace:  # pragma: no cover - CLI
    parser = argparse.ArgumentParser(
        description="Extrai IDs de itens craftados da base de conhecimento."
    )
    parser.add_argument(
        "--saida",
        default=str(DESTINO_PADRAO),
        help=f"JSON de saída (padrão: {DESTINO_PADRAO}).",
    )
    return parser.parse_args()


def main() -> int:  # pragma: no cover - CLI
    args = _parse_args()
    ids = extrair_ids()
    if not ids:
        print("[FAIL] nenhum ID de craft encontrado na base de conhecimento")
        return 1

    destino = Path(args.saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    dados = {
        "fonte": list(ARQUIVOS),
        "descricao": "IDs de itens craftados da Season 2 (R5)",
        "total": len(ids),
        "ids": ids,
    }
    destino.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"[OK] {len(ids)} IDs de craft gravados em {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
