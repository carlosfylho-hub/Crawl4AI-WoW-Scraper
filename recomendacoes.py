#!/usr/bin/env python3
"""
Recomendações determinísticas de encantamentos e gemas.

Regras (sem dados fictícios):
- A especialidade define o atributo primário (Força/Agilidade/Intelecto).
- A prioridade de atributos secundários é definida pelo usuário.
- A pontuação prioriza: compatibilidade de slot > atributo primário >
  ordem de prioridade > valor do atributo > rank/ilvl.
- As alternativas vêm do próprio catálogo raspado; se o catálogo estiver
  vazio, o status é `sem_catalogo` (nada é inventado).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from wow_season2 import (
    _ESTAT_PRIMARIA_EN,
    _ESTAT_PRIMARIA_PT,
    _ESTAT_SECUNDARIA_EN,
    _ESTAT_SECUNDARIA_PT,
    _chave_estat,
)

CLASSES_ESPECIALIDADES: Dict[str, Dict[str, str]] = {
    "Cavaleiro da Morte": {
        "Sangue": "Força",
        "Gelo": "Força",
        "Profano": "Força",
    },
    "Caçador de Demônios": {
        "Devastação": "Agilidade",
        "Vingança": "Agilidade",
    },
    "Druida": {
        "Equilíbrio": "Intelecto",
        "Feral": "Agilidade",
        "Guardião": "Agilidade",
        "Restauração": "Intelecto",
    },
    "Evocador": {
        "Devastação": "Intelecto",
        "Preservação": "Intelecto",
        "Aumento": "Intelecto",
    },
    "Caçador": {
        "Domínio de Bestas": "Agilidade",
        "Precisão": "Agilidade",
        "Sobrevivência": "Agilidade",
    },
    "Mago": {
        "Arcano": "Intelecto",
        "Fogo": "Intelecto",
        "Gelo": "Intelecto",
    },
    "Monge": {
        "Mestre Cervejeiro": "Intelecto",
        "Tecelão de Névoa": "Intelecto",
        "Andarilho do Vento": "Agilidade",
    },
    "Paladino": {
        "Sagrado": "Intelecto",
        "Proteção": "Força",
        "Retribuição": "Força",
    },
    "Sacerdote": {
        "Disciplina": "Intelecto",
        "Sagrado": "Intelecto",
        "Sombra": "Intelecto",
    },
    "Ladino": {
        "Assassinato": "Agilidade",
        "Fora da Lei": "Agilidade",
        "Subterfúgio": "Agilidade",
    },
    "Xamã": {
        "Elemental": "Intelecto",
        "Melhoria": "Agilidade",
        "Restauração": "Intelecto",
    },
    "Bruxo": {
        "Aflição": "Intelecto",
        "Demonologia": "Intelecto",
        "Destruição": "Intelecto",
    },
    "Guerreiro": {
        "Armas": "Força",
        "Fúria": "Força",
        "Proteção": "Força",
    },
}

ATRIBUTOS_PRIORIDADE = ["Aceleração", "Crítico", "Maestria", "Versatilidade"]


def primario_da_especialidade(classe: str, especialidade: str) -> str:
    """Atributo primário oficial da especialidade ("" se desconhecido)."""
    return CLASSES_ESPECIALIDADES.get(classe, {}).get(especialidade, "")


def _canonico(nome: str) -> str:
    chave = _chave_estat(nome)
    for mapa in (
        _ESTAT_PRIMARIA_PT,
        _ESTAT_PRIMARIA_EN,
        _ESTAT_SECUNDARIA_PT,
        _ESTAT_SECUNDARIA_EN,
    ):
        if chave in mapa:
            return mapa[chave]
    return nome


def atributos_canonicos(item: Dict[str, Any]) -> Dict[str, int]:
    """Une atributos PT/EN normalizando os nomes oficiais."""
    attrs: Dict[str, int] = {}
    for campo in (
        "atributos_primarios",
        "atributos_secundarios",
        "atributos_primarios_en",
        "atributos_secundarios_en",
    ):
        for nome, valor in (item.get(campo) or {}).items():
            canon = _canonico(nome)
            try:
                numero = int(valor)
            except (TypeError, ValueError):
                continue
            attrs[canon] = max(attrs.get(canon, 0), numero)
    return attrs


def _slot_compativel(slot_item: str, slot_alvo: str) -> bool:
    if not slot_alvo:
        return False
    if slot_item in ("Arma de 1 Mão",):
        return slot_alvo in ("Arma", "Arma de 1 Mão")
    if slot_item in ("Arma de 2 Mãos",):
        return slot_alvo in ("Arma", "Arma de 2 Mãos")
    if slot_item == "Anel":
        return slot_alvo in ("Anel", "Dedos")
    if slot_item == "Mão Secundária":
        return slot_alvo in ("Mão Secundária", "Escudo")
    return slot_alvo == slot_item


def _pontuar(
    candidato: Dict[str, Any],
    prioridade: List[str],
    primario: str,
    slot_ok: bool,
) -> Tuple[float, List[str]]:
    attrs = atributos_canonicos(candidato)
    score = 0.0
    justificativas: List[str] = []

    for nome, valor in attrs.items():
        if primario and nome in (primario, "Atributo Primário", "Primary Stat"):
            score += 200000 + valor
            justificativas.append(f"+{valor} {nome} (primário)")
        elif nome in prioridade:
            indice = prioridade.index(nome)
            peso = len(prioridade) - indice
            score += peso * 10000 + valor
            justificativas.append(f"+{valor} {nome} (prioridade #{indice + 1})")

    if slot_ok:
        score += 500000
        justificativas.append("slot compatível")

    score += int(candidato.get("item_level") or 0) * 10
    score += int(candidato.get("rank") or 0) * 100
    return score, justificativas


def _resumo_candidato(candidato: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "nome_en": candidato.get("nome_en") or "",
        "nome_ptbr": candidato.get("nome_ptbr") or "",
        "icone_url": candidato.get("icone_url") or "",
        "url": candidato.get("url") or "",
        "slot_alvo": candidato.get("slot_alvo") or "",
        "rank": int(candidato.get("rank") or 0),
        "atributos": atributos_canonicos(candidato),
        "tipo_item": candidato.get("tipo_item") or "",
        "gema_cor": candidato.get("gema_cor") or "",
    }


def _top(
    candidatos: List[Tuple[float, List[str], Dict[str, Any]]], limite: int
) -> List[Dict[str, Any]]:
    ordenados = sorted(candidatos, key=lambda t: t[0], reverse=True)[:limite]
    return [
        {
            "candidato": _resumo_candidato(item),
            "justificativa": "; ".join(just) or "Sem atributo compatível com a prioridade",
            "score": round(score, 1),
        }
        for score, just, item in ordenados
    ]


def recomendar_para_item(
    item: Dict[str, Any],
    catalogo: List[Dict[str, Any]],
    primario: str,
    prioridade: List[str],
    limite: int = 3,
) -> Dict[str, Any]:
    """Retorna recomendações e alternativas para um item de gear."""
    if item.get("tipo_item") not in ("gear", "embelezamento"):
        return {"encantamentos": [], "gemas": [], "status": "nao_gear"}

    if not catalogo:
        return {"encantamentos": [], "gemas": [], "status": "sem_catalogo"}

    enchants: List[Tuple[float, List[str], Dict[str, Any]]] = []
    gems: List[Tuple[float, List[str], Dict[str, Any]]] = []

    for candidato in catalogo:
        tipo = candidato.get("tipo_item")
        if tipo == "encantamento":
            slot_item = item.get("slot") or ""
            slot_alvo = candidato.get("slot_alvo") or ""
            slot_ok = _slot_compativel(slot_item, slot_alvo)
            # Encantamento com slot-alvo conhecido só concorre se for compatível
            if slot_item not in ("", "N/A") and slot_alvo and not slot_ok:
                continue
            score, just = _pontuar(candidato, prioridade, primario, slot_ok)
            enchants.append((score, just, candidato))
        elif tipo == "gema":
            score, just = _pontuar(candidato, prioridade, primario, False)
            gems.append((score, just, candidato))

    status = "ok"
    if not enchants and not gems:
        status = "catalogo_sem_tipos"

    return {
        "encantamentos": _top(enchants, limite),
        "gemas": _top(gems, limite),
        "status": status,
    }


def gerar_recomendacoes(
    itens: List[Dict[str, Any]],
    classe: str,
    especialidade: str,
    prioridade: List[str],
    primario_override: str = "",
    limite: int = 3,
) -> Dict[str, Any]:
    """
    Gera recomendações para todos os itens de gear.

    Retorna `{primario, status, itens: [...]}`; se não houver catálogo,
    `status` é `sem_catalogo` e nenhuma recomendação é inventada.
    """
    primario = primario_override or primario_da_especialidade(
        classe, especialidade
    )
    catalogo = [
        i
        for i in itens
        if i.get("tipo_item") in ("encantamento", "gema")
    ]
    gear = [
        i for i in itens if i.get("tipo_item") in ("gear", "embelezamento")
    ]

    if not catalogo:
        return {
            "primario": primario,
            "status": "sem_catalogo",
            "itens": [],
        }

    linhas: List[Dict[str, Any]] = []
    for item in gear:
        rec = recomendar_para_item(
            item, catalogo, primario, prioridade, limite=limite
        )
        ench = rec["encantamentos"]
        gem = rec["gemas"]
        linhas.append(
            {
                "id": item.get("id"),
                "nome_ptbr": item.get("nome_ptbr"),
                "nome_en": item.get("nome_en"),
                "slot": item.get("slot"),
                "tipo_armadura": item.get("tipo_armadura"),
                "item_level": item.get("item_level"),
                "melhor_encantamento": (
                    ench[0]["candidato"]["nome_ptbr"]
                    or ench[0]["candidato"]["nome_en"]
                    if ench
                    else ""
                ),
                "encantamento_justificativa": (
                    ench[0]["justificativa"] if ench else ""
                ),
                "encantamento_alternativas": "; ".join(
                    alt["candidato"]["nome_ptbr"]
                    or alt["candidato"]["nome_en"]
                    for alt in ench[1:]
                ),
                "melhor_gema": (
                    gem[0]["candidato"]["nome_ptbr"]
                    or gem[0]["candidato"]["nome_en"]
                    if gem
                    else ""
                ),
                "gema_justificativa": gem[0]["justificativa"] if gem else "",
                "gema_alternativas": "; ".join(
                    alt["candidato"]["nome_ptbr"]
                    or alt["candidato"]["nome_en"]
                    for alt in gem[1:]
                ),
                "status": rec["status"],
            }
        )

    return {"primario": primario, "status": "ok", "itens": linhas}
