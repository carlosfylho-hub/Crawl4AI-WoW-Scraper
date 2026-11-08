#!/usr/bin/env python3
"""Gerador do bloco de texto "Tooltip Raidbots" a partir do dict canônico.

O texto é puramente formado a partir de campos já extraídos do item. Não há
rede, cálculo de coeficientes de rating nem inferência de valores: quando um
dado não existe, a linha correspondente é omitida.

Uso:
    from tooltip_raidbots import montar_tooltip_raidbots
    texto = montar_tooltip_raidbots(item, locale="ptbr")
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

#: Valores que representam "sem dado" em slot/tipo de armadura.
_VAZIOS = {"", "n/a", "na", "-", "indisponível", "indisponivel", "none", "null"}

#: Rótulos canônicos PT-BR por alias (PT e EN) de atributo.
_LABELS_PTBR: Dict[str, str] = {
    # Primários
    "força": "Força",
    "forca": "Força",
    "strength": "Força",
    "agilidade": "Agilidade",
    "agility": "Agilidade",
    "intelecto": "Intelecto",
    "intellect": "Intelecto",
    "vigor": "Vigor",
    "stamina": "Vigor",
    "espírito": "Espírito",
    "espirito": "Espírito",
    "spirit": "Espírito",
    # Secundários
    "acerto crítico": "Acerto Crítico",
    "acerto critico": "Acerto Crítico",
    "crítico": "Acerto Crítico",
    "critico": "Acerto Crítico",
    "critical strike": "Acerto Crítico",
    "crit": "Acerto Crítico",
    "rapidez": "Rapidez",
    "haste": "Rapidez",
    "aceleração": "Rapidez",
    "aceleracao": "Rapidez",
    "maestria": "Maestria",
    "mastery": "Maestria",
    "versatilidade": "Versatilidade",
    "versatility": "Versatilidade",
}

#: Rótulos canônicos EN por alias (PT e EN) de atributo.
_LABELS_EN: Dict[str, str] = {
    # Primários
    "força": "Strength",
    "forca": "Strength",
    "strength": "Strength",
    "agilidade": "Agility",
    "agility": "Agility",
    "intelecto": "Intellect",
    "intellect": "Intellect",
    "vigor": "Stamina",
    "stamina": "Stamina",
    "espírito": "Spirit",
    "espirito": "Spirit",
    "spirit": "Spirit",
    # Secundários
    "acerto crítico": "Critical Strike",
    "acerto critico": "Critical Strike",
    "crítico": "Critical Strike",
    "critico": "Critical Strike",
    "critical strike": "Critical Strike",
    "crit": "Critical Strike",
    "rapidez": "Haste",
    "haste": "Haste",
    "aceleração": "Haste",
    "aceleracao": "Haste",
    "maestria": "Mastery",
    "mastery": "Mastery",
    "versatilidade": "Versatility",
    "versatility": "Versatility",
}

_SEPARADORES_COMBINADOS = re.compile(r"\s+(?:ou|or)\s+|[\/]", re.IGNORECASE)
_RE_INTEIRO = re.compile(r"\d+")


def _normalizar_chave(nome: Any) -> str:
    """Chave de comparação: minúscula, sem espaços extras ou pontuação."""
    texto = re.sub(r"\s+", " ", str(nome or "")).strip().lower()
    return texto.strip(" :+-\u00a0[]()")


def _rotulo_estat(nome: Any, locale: str) -> str:
    """Converte um nome de atributo (PT ou EN) para o rótulo do idioma."""
    mapa = _LABELS_EN if locale == "en" else _LABELS_PTBR
    separador = " or " if locale == "en" else " ou "

    original = re.sub(r"\s+", " ", str(nome or "")).strip()
    if not original:
        return ""

    chave = _normalizar_chave(original)
    if chave in mapa:
        return mapa[chave]

    # Escolha combinada: "Agilidade ou Intelecto" / "Agility or Intellect".
    partes = [p.strip() for p in _SEPARADORES_COMBINADOS.split(original) if p.strip()]
    if len(partes) > 1:
        convertidas: List[str] = []
        for parte in partes:
            chave_parte = _normalizar_chave(parte)
            convertidas.append(mapa.get(chave_parte, parte))
        return separador.join(convertidas)

    # Nome desconhecido (ex.: "Engenhosidade"): preservar como veio.
    return original


def _valor_inteiro(valor: Any) -> int:
    """Converte para inteiro sem casas/percentual; 0 quando não numérico."""
    if isinstance(valor, bool):
        return 0
    if isinstance(valor, (int, float)):
        try:
            return int(valor)
        except (TypeError, ValueError, OverflowError):
            return 0
    m = _RE_INTEIRO.search(str(valor or ""))
    if not m:
        return 0
    try:
        return int(m.group(0))
    except ValueError:
        return 0


def _linhas_atributos(
    atributos: Any, locale: str, limite: int = 2
) -> List[str]:
    """Gera as linhas indentadas de atributos com valor inteiro positivo."""
    if not isinstance(atributos, dict):
        return []
    linhas: List[str] = []
    for nome, valor in atributos.items():
        if len(linhas) >= limite:
            break
        numero = _valor_inteiro(valor)
        if numero <= 0:
            continue
        rotulo = _rotulo_estat(nome, locale)
        if not rotulo:
            continue
        linhas.append(f"  +{numero} {rotulo}")
    return linhas


def _limpar_texto(valor: Any) -> str:
    """Normaliza um campo de texto para uma única linha sem espaços sobrando."""
    texto = re.sub(r"\s+", " ", str(valor or "")).strip()
    return texto


def _nome_do_idioma(item: Dict[str, Any], locale: str) -> str:
    """Nome EXCLUSIVO do idioma (nunca traduz/infere o outro idioma)."""
    chave = "nome_en" if locale == "en" else "nome_ptbr"
    return _limpar_texto(item.get(chave))


def _efeito_do_idioma(item: Dict[str, Any], locale: str) -> str:
    """Efeito EXCLUSIVO do idioma (ptbr/en)."""
    chave = "efeito_equip_uso_en" if locale == "en" else "efeito_equip_uso_ptbr"
    return _limpar_texto(item.get(chave))


def _bonus_ids_texto(item: Dict[str, Any]) -> str:
    """Serializa a lista de Bonus IDs; lista vazia vira string vazia."""
    bonus = item.get("bonus_ids")
    if isinstance(bonus, (list, tuple, set)):
        partes = [str(b).strip() for b in bonus if str(b or "").strip()]
    elif bonus in (None, "", 0):
        partes = []
    else:
        partes = [str(bonus).strip()]
    return ":".join(partes)


def _qualidade_craft_int(item: Dict[str, Any]) -> int:
    return _valor_inteiro(item.get("qualidade_craft"))


def montar_tooltip_raidbots(item: dict, locale: str = "ptbr") -> str:
    """Monta o bloco textual do tooltip no formato esperado pelo Raidbots.

    Regras de omissão:
    - stat com valor ausente/0 não gera linha;
    - percentual nunca é incluído (apenas o inteiro do rating);
    - `Equipar:` some quando o efeito está vazio;
    - `Bônus IDs:` some quando a lista está vazia;
    - linha de craft some quando `qualidade_craft <= 0`;
    - linha de slot/tipo some quando ambos estão vazios/"N/A".

    Nunca levanta exceção: entrada inválida retorna o que existir (ou "").
    """
    try:
        if not isinstance(item, dict):
            return ""

        idioma = "en" if str(locale or "").strip().lower() == "en" else "ptbr"

        ilvl = _valor_inteiro(item.get("item_level"))
        nome = _nome_do_idioma(item, idioma)

        linhas: List[str] = []

        if nome and ilvl:
            linhas.append(f"{nome} (ilvl {ilvl})")
        elif nome:
            linhas.append(nome)
        elif ilvl:
            linhas.append(f"(ilvl {ilvl})")

        slot = _limpar_texto(item.get("slot"))
        tipo = _limpar_texto(item.get("tipo_armadura"))
        if slot.lower() in _VAZIOS:
            slot = ""
        if tipo.lower() in _VAZIOS:
            tipo = ""
        linha_slot = " / ".join(parte for parte in (slot, tipo) if parte)
        if linha_slot:
            linhas.append(linha_slot)

        linhas.extend(
            _linhas_atributos(item.get("atributos_primarios"), idioma, limite=2)
        )
        linhas.extend(
            _linhas_atributos(item.get("atributos_secundarios"), idioma, limite=2)
        )

        efeito = _efeito_do_idioma(item, idioma)
        if efeito:
            linhas.append(f"Equipar: {efeito}")

        bonus = _bonus_ids_texto(item)
        if bonus:
            linhas.append(f"Bônus IDs: {bonus}")

        craft = _qualidade_craft_int(item)
        if craft > 0:
            profissao = _limpar_texto(item.get("profissao_craft"))
            sufixo = f" ({profissao})" if profissao else ""
            linhas.append(f"Qualidade de craft: R{craft}{sufixo}")

        # Garantia final: nenhuma linha com espaço à direita ou em branco.
        return "\n".join(linha.rstrip() for linha in linhas if linha.strip())
    except Exception:  # noqa: BLE001 - contrato: nunca levantar exceção
        return ""


__all__ = ["montar_tooltip_raidbots"]
