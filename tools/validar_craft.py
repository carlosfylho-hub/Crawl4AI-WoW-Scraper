#!/usr/bin/env python3
"""Validação ao vivo de itens **craftados reais** do Wowhead (Pacote 4).

Recebe IDs de itens, roda o pipeline real do scraper (PT-BR + EN, com
`?crafting-quality=N` na URL de detalhe) e imprime/grava, por item:

    id, nome, qualidade, qualidade_craft, qualidade_craft_fonte,
    profissao_craft, item_level

Uso:
    python tools/validar_craft.py --ids 237831 237839
    python tools/validar_craft.py --ids 237831 --qualidade-craft 5 \
        --json data/_diagnostico/craft.json

Critério de sucesso (pendência 1): cada item deve sair com
`qualidade_craft=5`, `qualidade_craft_fonte="url:crafting-quality"` e
`profissao_craft` não vazio. Se a rede bloquear (403), o relatório registra
a limitação em vez de falhar silenciosamente.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from config import SEASON2_GEAR_BONUS  # noqa: E402
from scraper_season2 import WowheadSeason2Scraper  # noqa: E402

#: Campos exigidos no relatório de validação.
CAMPOS_RELATORIO = (
    "id",
    "nome_ptbr",
    "nome_en",
    "qualidade",
    "qualidade_craft",
    "qualidade_craft_fonte",
    "motivo_qualidade_craft",
    "profissao_craft",
    "profissao_craft_fonte",
    "craft_indicio",
    "item_level",
    # P-05/F-02: contexto de bônus e origem do ilvl, para comparar com o
    # JSON canônico (mesmo `bonus_ids`, mesmo `item_level`).
    "bonus_ids",
    "ilvl_origem",
)

#: JSON canônico usado como referência de `bonus_ids` (P-05).
CANONICO_PADRAO = os.path.join("data", "wowhead_itens_season2.json")


def carregar_bonus_por_id(caminho: str = CANONICO_PADRAO) -> Dict[str, List[str]]:
    """Lê `id -> bonus_ids` do JSON canônico (vazio se o arquivo não existir).

    O validador antigo montava `item=<id>` sem bônus, o que mudava o contexto
    de variante e produzia um `item_level` diferente do pipeline (F-02).
    """
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (OSError, ValueError):
        return {}

    itens = dados.get("itens") if isinstance(dados, dict) else dados
    if not isinstance(itens, list):
        return {}

    mapa: Dict[str, List[str]] = {}
    for item in itens:
        if not isinstance(item, dict):
            continue
        ident = str(item.get("id") or "").strip()
        if not ident:
            continue
        bonus = [str(b) for b in (item.get("bonus_ids") or []) if str(b)]
        if bonus:
            mapa[ident] = bonus
    return mapa


def montar_urls_itens(
    ids: List[str],
    bonus_por_id: Dict[str, List[str]],
    bonus_padrao: str = "",
) -> List[str]:
    """URLs `item=<id>?bonus=<...>` usando a variante registrada no canônico.

    Quando o ID não está no canônico, usa `bonus_padrao` (o track da temporada)
    para não cair no contexto base do item, que produz ilvl divergente (F-02).
    """
    urls: List[str] = []
    for ident in ids:
        bonus = bonus_por_id.get(str(ident)) or []
        if not bonus and bonus_padrao:
            bonus = [str(bonus_padrao)]
        sufixo = f"?bonus={':'.join(bonus)}" if bonus else ""
        urls.append(f"https://www.wowhead.com/pt/item={ident}{sufixo}")
    return urls


def _parse_args() -> argparse.Namespace:  # pragma: no cover - CLI
    parser = argparse.ArgumentParser(
        description="Valida itens craftados reais do Wowhead (qualidade R)."
    )
    parser.add_argument(
        "--ids",
        nargs="+",
        required=True,
        help="IDs de itens do Wowhead a validar (ex.: 237831 237839)",
    )
    parser.add_argument(
        "--qualidade-craft",
        type=int,
        default=5,
        help="Qualidade de craft usada na URL de detalhe (padrão: 5).",
    )
    parser.add_argument(
        "--sem-ingles",
        action="store_true",
        help="Não visitar a versão EN (mantém apenas PT-BR).",
    )
    parser.add_argument(
        "--json",
        default=os.path.join("data", "_diagnostico", "craft.json"),
        help="Caminho do relatório JSON de saída.",
    )
    parser.add_argument(
        "--canonico",
        default=CANONICO_PADRAO,
        help=(
            "JSON canônico usado como referência de `bonus_ids` "
            "(padrão: data/wowhead_itens_season2.json)."
        ),
    )
    return parser.parse_args()


def _resumo(item: Dict[str, Any]) -> Dict[str, Any]:
    return {campo: item.get(campo) for campo in CAMPOS_RELATORIO}


async def _validar(
    ids: List[str],
    qualidade_craft: int,
    buscar_ingles: bool,
    bonus_por_id: Optional[Dict[str, List[str]]] = None,
    bonus_padrao: str = "",
) -> Dict[str, Any]:
    bonus_por_id = bonus_por_id or {}
    urls = montar_urls_itens(ids, bonus_por_id, bonus_padrao)
    scraper = WowheadSeason2Scraper(
        ilvl_min=0,
        ilvl_max=0,
        qualidade_min=0,
        qualidade_craft_min=qualidade_craft,
        buscar_detalhes=True,
        buscar_ingles=buscar_ingles,
        gerar_markdown=False,
        max_itens=max(200, len(urls)),
        max_detalhes=None,
    )

    async with scraper:
        resultado = await scraper.executar(urls)

    itens = resultado.get("itens") or []
    metadata = resultado.get("metadata") or {}
    por_id = {str(i.get("id")): i for i in itens}

    resumos: List[Dict[str, Any]] = []
    faltantes: List[str] = []
    for ident in ids:
        item = por_id.get(str(ident))
        if item is None:
            faltantes.append(str(ident))
            continue
        resumos.append(_resumo(item))

    return {
        "timestamp": datetime.now().isoformat(),
        "ids_solicitados": [str(i) for i in ids],
        "qualidade_craft_min": qualidade_craft,
        "bonus_por_id": bonus_por_id,
        "bonus_padrao": bonus_padrao,
        "urls": urls,
        "itens": resumos,
        "faltantes": faltantes,
        "metadata": {
            "total_itens": metadata.get("total_itens"),
            "total_brutos": metadata.get("total_brutos"),
            "descartes": metadata.get("descartes"),
            "falhas": metadata.get("falhas"),
        },
    }


def _imprimir(relatorio: Dict[str, Any]) -> int:
    itens = relatorio.get("itens") or []
    print("=== Validação de itens craftados (Wowhead) ===")
    for item in itens:
        print(
            f"id={item.get('id')} | nome={item.get('nome_ptbr') or item.get('nome_en')}"
            f" | qualidade={item.get('qualidade')}"
            f" | qualidade_craft={item.get('qualidade_craft')}"
            f" | fonte={item.get('qualidade_craft_fonte')}"
            f" | motivo={item.get('motivo_qualidade_craft')}"
            f" | profissao_craft={item.get('profissao_craft')}"
            f" | item_level={item.get('item_level')}"
        )

    criterio = [
        item
        for item in itens
        if int(item.get("qualidade_craft") or 0) == int(
            relatorio.get("qualidade_craft_min") or 5
        )
        and item.get("qualidade_craft_fonte") == "url:crafting-quality"
        and (item.get("profissao_craft") or "").strip()
    ]
    print(
        f"\nCritério (R{relatorio.get('qualidade_craft_min')} + fonte URL + "
        f"profissão): {len(criterio)}/{len(relatorio.get('ids_solicitados') or [])} ok"
    )
    if relatorio.get("faltantes"):
        print(f"Itens não retornados: {', '.join(relatorio['faltantes'])}")
    if not itens:
        print(
            "[AVISO] Nenhum item retornado — possível bloqueio de rede (403) "
            "ou falha do crawler. Veja metadata.falhas no JSON."
        )
    return 0 if criterio and not relatorio.get("faltantes") else 1


def main() -> None:  # pragma: no cover - execução manual
    args = _parse_args()
    bonus_por_id = carregar_bonus_por_id(args.canonico)
    if not bonus_por_id:
        print(
            f"[AVISO] sem referência de bônus em {args.canonico}; "
            "as URLs serão montadas sem `bonus` (contexto pode divergir)."
        )
    relatorio = asyncio.run(
        _validar(
            args.ids,
            args.qualidade_craft,
            not args.sem_ingles,
            bonus_por_id,
            SEASON2_GEAR_BONUS,
        )
    )

    diretorio = os.path.dirname(args.json)
    if diretorio:
        os.makedirs(diretorio, exist_ok=True)
    with open(args.json, "w", encoding="utf-8") as arquivo:
        json.dump(relatorio, arquivo, ensure_ascii=False, indent=2)

    codigo = _imprimir(relatorio)
    print(f"Relatório salvo: {args.json}")
    sys.exit(codigo)


if __name__ == "__main__":  # pragma: no cover
    main()
