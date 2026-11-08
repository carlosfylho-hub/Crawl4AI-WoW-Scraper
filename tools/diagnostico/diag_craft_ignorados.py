#!/usr/bin/env python3
"""Audita `motivo_qualidade_craft` no JSON canônico (P-12/F-06).

Procura itens com `qualidade_craft=0` que **carregam** marca de craft
(`crafting-quality` em `craft_indicio`) mas ficaram como
``ignorado:sem_profissao``. Para cada suspeito, consulta o mapa local
receita→profissão (P-07): se o mapa agora resolve a profissão, o item é
"reprocessável" e deve ser validado numa nova rodada.

Uso::

    python tools/diagnostico/diag_craft_ignorados.py
    python tools/diagnostico/diag_craft_ignorados.py --json data/_diagnostico/craft_ignorados.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

import runtime  # noqa: E402,F401  (F-09: console UTF-8)

from wow_season2 import profissao_por_receita  # noqa: E402

CANONICO_PADRAO = os.path.join("data", "wowhead_itens_season2.json")


def _carregar_itens(caminho: str) -> List[Dict[str, Any]]:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    itens = dados.get("itens") if isinstance(dados, dict) else dados
    return [i for i in (itens or []) if isinstance(i, dict)]


def auditar(itens: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Classifica os motivos e separa os suspeitos de falso `sem_profissao`."""
    motivos = Counter(
        str(item.get("motivo_qualidade_craft") or "ausente") for item in itens
    )

    suspeitos: List[Dict[str, Any]] = []
    reprocessaveis: List[Dict[str, Any]] = []

    for item in itens:
        if int(item.get("qualidade_craft") or 0) != 0:
            continue

        motivo = str(item.get("motivo_qualidade_craft") or "")
        indicio = str(item.get("craft_indicio") or "")
        if "crafting-quality" not in indicio or "sem_profissao" not in motivo:
            continue

        registro = {
            "id": item.get("id"),
            "nome": item.get("nome_ptbr") or item.get("nome_en") or "",
            "motivo": motivo,
            "profissao_no_mapa": profissao_por_receita(item.get("id")),
        }
        suspeitos.append(registro)
        if registro["profissao_no_mapa"]:
            reprocessaveis.append(registro)

    return {
        "total_itens": len(itens),
        "motivos": dict(motivos),
        "suspeitos_sem_profissao": suspeitos,
        "reprocessaveis": reprocessaveis,
    }


def _imprimir(relatorio: Dict[str, Any]) -> None:
    print("=== Auditoria de motivo_qualidade_craft ===")
    print(f"itens: {relatorio['total_itens']}")
    print("motivos:")
    for motivo, quantidade in sorted(
        relatorio["motivos"].items(), key=lambda par: -par[1]
    ):
        print(f"  {quantidade:3d}  {motivo}")

    suspeitos = relatorio["suspeitos_sem_profissao"]
    reprocessaveis = relatorio["reprocessaveis"]
    print(f"\nsuspeitos (crafting-quality + sem_profissao): {len(suspeitos)}")
    print(f"reprocessáveis (mapa P-07 já resolve a profissão): {len(reprocessaveis)}")
    for registro in reprocessaveis[:20]:
        print(
            f"  id={registro['id']} | {registro['nome'][:40]} | "
            f"profissao={registro['profissao_no_mapa']}"
        )
    if len(reprocessaveis) > 20:
        print(f"  ... e mais {len(reprocessaveis) - 20}")


def _parse_args() -> argparse.Namespace:  # pragma: no cover - CLI
    parser = argparse.ArgumentParser(
        description="Audita itens com qualidade_craft=0 e marca de craft."
    )
    parser.add_argument(
        "--canonico",
        default=CANONICO_PADRAO,
        help=f"JSON canônico de entrada (padrão: {CANONICO_PADRAO}).",
    )
    parser.add_argument(
        "--json",
        default="",
        help="Caminho opcional para gravar o relatório em JSON.",
    )
    return parser.parse_args()


def main() -> int:  # pragma: no cover - CLI
    args = _parse_args()
    try:
        itens = _carregar_itens(args.canonico)
    except (OSError, ValueError) as exc:
        print(f"[FAIL] não foi possível ler {args.canonico}: {exc}")
        return 1

    if not itens:
        print(f"[AVISO] {args.canonico} não tem itens — regenere com o scraper.")
        return 1

    relatorio = auditar(itens)
    _imprimir(relatorio)

    if args.json:
        diretorio = os.path.dirname(args.json)
        if diretorio:
            os.makedirs(diretorio, exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as arquivo:
            json.dump(relatorio, arquivo, ensure_ascii=False, indent=2)
        print(f"\nRelatório salvo: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
