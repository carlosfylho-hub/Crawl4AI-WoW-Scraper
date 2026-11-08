#!/usr/bin/env python3
"""
Utilitários da Season 2 (Midnight) para o scraper do Wowhead.

Concentra:
- Faixas de item level (Hero/Myth/Voidforge/Very Rare)
- Classificação de track + detecção de Voidforge
- Normalização de ícones para o CDN de alta resolução (wow.zamimg.com)
- Parsers de atributos primários/secundários, slot, tipo de armadura e efeitos
- Extração de itens a partir do HTML (listas, guias e páginas individuais)
- Associação de imagens de `result.media` às linhas de itens

Este módulo é puro (sem rede) para permitir testes unitários.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from tooltip_raidbots import montar_tooltip_raidbots

# =============================================================================
# Faixas de Item Level (Season 2 / Midnight)
# =============================================================================

ILVL_ABSOLUTO_MIN = 200
ILVL_ABSOLUTO_MAX = 350

ILVL_PISO_PADRAO = 305            # Hero 1/6
ILVL_TETO_PADRAO = 350            # folga

ILVL_HERO_MIN = 305               # Hero 1/6
ILVL_HERO_MAX = 321               # Hero 6/6
ILVL_HERO_VOIDFORGE = 328         # Hero + Voidforge (+7)

ILVL_MYTH_MIN = 318               # Myth 1/6
ILVL_MYTH_MAX = 334               # Myth 6/6
ILVL_MYTH_VOIDFORGE = 341         # Myth + Voidforge (+7) em armas/berloques/colar

ILVL_VERY_RARE_MAX = 344          # Very Rare / Cantrip de chefes finais (9/6)
VOIDFORGE_BONUS = 7

QUALIDADE_POR_ID = {
    0: "Pobre",
    1: "Comum",
    2: "Incomum",
    3: "Raro",
    4: "Épico",
    5: "Lendário",
}
QUALIDADE_POR_ID_EN = {
    0: "Poor",
    1: "Common",
    2: "Uncommon",
    3: "Rare",
    4: "Epic",
    5: "Legendary",
}
QUALIDADE_MINIMA_PADRAO = 3

ICON_CDN = "https://wow.zamimg.com/images/wow/icons/large/{nome}.jpg"

# =============================================================================
# Ícones / mídia
# =============================================================================

_ICON_PATH_RE = re.compile(
    r"/icons/(?:large|medium|tiny|small)?/?([^/?#]+?)"
    r"\.(?:jpg|jpeg|png|gif|tga|webp|bmp)",
    re.IGNORECASE,
)
_ICON_NAME_RE = re.compile(r"^[a-z0-9_\-]+$", re.IGNORECASE)
_ICON_PREFIX_RE = re.compile(
    r"^(?:inv_|spell_|ability_|achievement_|trade_|ui_|interface_)", re.IGNORECASE
)


def _attr(element: Any, nome: str) -> str:
    """Lê um atributo HTML como string segura (evita `AttributeValueList`)."""
    valor = element.get(nome) if hasattr(element, "get") else None
    if valor is None:
        return ""
    if isinstance(valor, (list, tuple)):
        return " ".join(str(v) for v in valor)
    return str(valor)


def montar_icone_url(valor: Optional[str]) -> str:
    """
    Normaliza um `src`, `style` de background ou nome de ícone para a URL
    pública de alta resolução do CDN do Wowhead.

    Exemplos:
        inv_sword_2h_d_01          -> https://wow.zamimg.com/images/wow/icons/large/inv_sword_2h_d_01.jpg
        .../icons/medium/x.png     -> .../icons/large/x.jpg
        https://cdn/x/y.jpg        -> URL absoluta preservada
    """
    if not valor:
        return ""

    v = str(valor).strip().strip("'\"").strip()
    if not v:
        return ""

    if v.startswith("//"):
        v = "https:" + v

    m = _ICON_PATH_RE.search(v)
    if m:
        return ICON_CDN.format(nome=m.group(1).lower())

    if v.startswith("http://") or v.startswith("https://"):
        return v

    if "icons/" in v:
        resto = v.split("icons/")[-1].split("/")[-1]
        resto = re.sub(
            r"\.(?:jpg|jpeg|png|gif|tga|webp|bmp)$", "", resto, flags=re.IGNORECASE
        )
        if resto and _ICON_NAME_RE.match(resto):
            return ICON_CDN.format(nome=resto.lower())

    nome = re.sub(
        r"\.(?:jpg|jpeg|png|gif|tga|webp|bmp)$", "", v, flags=re.IGNORECASE
    )
    nome = nome.split("/")[-1].strip()
    if nome and _ICON_NAME_RE.match(nome):
        return ICON_CDN.format(nome=nome.lower())

    return ""


def icone_de_style(style: Optional[str]) -> str:
    """Extrai a URL do ícone de um `style="background-image:url(...)"`."""
    if not style:
        return ""
    m = re.search(r"url\(\s*(['\"]?)(.*?)\1\s*\)", style, re.IGNORECASE)
    if not m:
        return ""
    return montar_icone_url(m.group(2))


def _icone_do_elemento(tag: Any, profundidade: int = 0) -> str:
    """Procura a melhor URL de ícone em um elemento (ins/img) e descendentes."""
    if tag is None or profundidade > 2:
        return ""

    nome_tag = getattr(tag, "name", None)

    if nome_tag == "ins":
        url = icone_de_style(tag.get("style"))
        if url:
            return url
        for cls in tag.get("class") or []:
            if _ICON_PREFIX_RE.match(str(cls)):
                url = montar_icone_url(cls)
                if url:
                    return url

    if nome_tag == "img":
        for attr in ("src", "data-src", "data-original"):
            url = montar_icone_url(tag.get(attr))
            if url:
                return url

    for ins in tag.find_all("ins") if hasattr(tag, "find_all") else []:
        url = icone_de_style(ins.get("style"))
        if not url:
            for cls in ins.get("class") or []:
                if _ICON_PREFIX_RE.match(str(cls)):
                    url = montar_icone_url(cls)
                    break
        if url:
            return url

    for img in tag.find_all("img") if hasattr(tag, "find_all") else []:
        for attr in ("src", "data-src", "data-original"):
            url = montar_icone_url(img.get(attr))
            if url:
                return url

    # Irmãos próximos (ícone antes/depois do link)
    if profundidade < 2:
        for irmao in (tag.previous_sibling, tag.next_sibling):
            if irmao is not None and getattr(irmao, "name", None) in ("ins", "img"):
                url = _icone_do_elemento(irmao, profundidade + 1)
                if url:
                    return url

    return ""


def associar_icones_media(itens: List[Dict[str, Any]], media_images: Any) -> None:
    """
    Associa imagens de `result.media["images"]` aos itens correspondentes.

    Estratégia:
    1. Casa `alt`/`desc` da imagem com o nome do item.
    2. Se a página tem apenas 1 item, usa o primeiro ícone disponível.
    """
    imagens: List[Tuple[str, str]] = []
    for img in media_images or []:
        if not isinstance(img, dict):
            continue
        url = montar_icone_url(img.get("src") or img.get("url"))
        if not url:
            continue
        chave = str(
            img.get("alt") or img.get("desc") or img.get("title") or ""
        ).strip().lower()
        imagens.append((chave, url))

    if not imagens:
        return

    for item in itens:
        if item.get("icone_url"):
            continue
        nome = str(item.get("nome") or "").strip().lower()
        if nome:
            for chave, url in imagens:
                if chave and (nome in chave or chave in nome):
                    item["icone_url"] = url
                    break
        if not item.get("icone_url") and len(itens) == 1:
            item["icone_url"] = imagens[0][1]


# =============================================================================
# Qualidade / item level / bonus IDs
# =============================================================================

def qualidade_de_classes(classes: Iterable[str]) -> int:
    """Detecta a qualidade (3=Épico? não: 3=Raro, 4=Épico) a partir de classes CSS."""
    for cls in classes or []:
        c = str(cls).strip().lower()
        m = re.match(r"^quality-(\d)$", c) or re.match(r"^q(\d)$", c)
        if m:
            return int(m.group(1))
    return 0


_ILVL_PATTERNS = (
    re.compile(r"\bilvl\s*[=:]\s*(\d{2,4})", re.IGNORECASE),
    re.compile(
        r"(?:item\s*level|n[ií]vel\s*(?:de|do)\s*item|n[ií]vel\s*base\s*do\s*item)"
        r"\s*[:.]?\s*(\d{2,4})",
        re.IGNORECASE,
    ),
)


def extrair_ilvl(*fontes: Optional[str]) -> int:
    """Extrai o item level de atributos `data-wowhead`, tooltips ou texto."""
    for fonte in fontes:
        if not fonte:
            continue
        for pat in _ILVL_PATTERNS:
            m = pat.search(str(fonte))
            if m:
                try:
                    return int(m.group(1))
                except ValueError:
                    continue
    return 0


def extrair_bonus_ids(*fontes: Optional[str]) -> List[str]:
    """Extrai bonus/gem/ench IDs de URLs ou atributos `data-wowhead`."""
    for fonte in fontes:
        if not fonte:
            continue
        ids: List[str] = []
        for m in re.finditer(r"(?:bonus|gems|ench)=([\w:,\-]+)", str(fonte), re.I):
            for parte in re.split(r"[:,]", m.group(1)):
                if parte.isdigit():
                    ids.append(parte)
        if ids:
            return ids
    return []


# =============================================================================
# Track / Voidforge
# =============================================================================

def classificar_track(
    item_level: int, texto: str = ""
) -> Tuple[str, bool, str]:
    """
    Classifica o item em Herói / Mito / Muito Raro / Base.

    Retorna `(track, voidforged, track_stage)` onde `track_stage` é algo
    como "1/6" ou "6/6" quando a tag aparece no texto.

    Regras (Season 2):
      Hero  305-321  (+ Voidforge = 328)
      Myth  318-334  (+ Voidforge = 341)
      Very Rare / Cantrip 9/6 ate 344
    """
    texto = texto or ""
    baixo = texto.lower()

    voidforged = bool(
        re.search(
            r"voidforg|forjad[oa]?\s+no\s+vazio|forja\s+do\s+vazio", baixo, re.I
        )
    )

    stage = ""
    m_stage = re.search(r"(\d)\s*/\s*6\b", texto)
    if m_stage:
        stage = f"{m_stage.group(1)}/6"

    track = ""
    if re.search(r"\bher[oó]i\b|\bhero\b|\bheroic\b", baixo):
        track = "Herói"
    elif re.search(r"\bmito\b|\bmyth\b|\bmythic\b", baixo):
        track = "Mito"
    elif re.search(r"very\s*rare|muito\s+raro", baixo):
        track = "Muito Raro"

    ilvl = int(item_level or 0)

    if not track and ilvl:
        if ilvl == ILVL_HERO_VOIDFORGE:
            track = "Herói"
        elif ilvl == ILVL_MYTH_VOIDFORGE:
            track = "Mito"
        elif ILVL_HERO_MIN <= ilvl <= ILVL_HERO_MAX:
            track = "Herói"
        elif ILVL_MYTH_MIN <= ilvl <= ILVL_MYTH_MAX:
            track = "Mito"
        elif ILVL_MYTH_MAX < ilvl < ILVL_MYTH_VOIDFORGE:
            track = "Mito"
        elif ILVL_MYTH_VOIDFORGE < ilvl <= ILVL_VERY_RARE_MAX:
            track = "Muito Raro"

    if not voidforged and ilvl in (ILVL_HERO_VOIDFORGE, ILVL_MYTH_VOIDFORGE):
        voidforged = True

    return (track or "Base"), voidforged, stage


def badges_trilha(
    item_level: int, track: str = "", voidforged: bool = False
) -> List[str]:
    """
    Badges visuais para a UI:
      - Herói: 305-328
      - Mito: 318-344
      - Voidforge quando detectado
    """
    ilvl = int(item_level or 0)
    badges: List[str] = []

    if 305 <= ilvl <= 328:
        badges.append("Herói")
    if 318 <= ilvl <= 344:
        badges.append("Mito")
    if ilvl > ILVL_VERY_RARE_MAX:
        badges.append("Acima da faixa")
    if voidforged:
        badges.append("Voidforge")
    if not badges:
        badges.append(track or "Base")
    return badges


# =============================================================================
# Atributos
# =============================================================================

_PRIMARIOS_ALIASES = {
    "força": "Força",
    "forca": "Força",
    "agilidade": "Agilidade",
    "intelecto": "Intelecto",
    "vigor": "Vigor",
    "espírito": "Espírito",
    "espirito": "Espírito",
}

_SECUNDARIOS_ALIASES = {
    "aceleração": "Aceleração",
    "aceleracao": "Aceleração",
    "crítico": "Crítico",
    "critico": "Crítico",
    "acerto crítico": "Crítico",
    "acerto critico": "Crítico",
    "maestria": "Maestria",
    "versatilidade": "Versatilidade",
    "finesse": "Finesse",
    "engenhosidade": "Engenhosidade",
    "percepção": "Percepção",
    "percepcao": "Percepção",
    "desenvoltura": "Desenvoltura",
    "multicriação": "Multicriação",
    "multicriacao": "Multicriação",
    "robustez": "Robustez",
}

_NUM_CAPTURE = r"([0-9][0-9.,\u00a0 ]{0,12})"


def _parse_numero(txt: str) -> int:
    digitos = re.sub(r"[^\d]", "", txt or "")
    return int(digitos) if digitos else 0


def _buscar_atributos(
    aliases: Dict[str, str], texto: str
) -> Dict[str, int]:
    achados: Dict[str, int] = {}
    # IMPORTANTE: usar [ \t] (e não \s) para não capturar o número da
    # linha seguinte do tooltip. Ex.: "+2 Agilidade\n+3 Vigor".
    espaco = r"[ \t\u00a0]*"
    for alias, canonico in aliases.items():
        padroes = (
            re.compile(
                rf"\b{re.escape(alias)}\b{espaco}(?:\+{espaco})?{_NUM_CAPTURE}",
                re.IGNORECASE,
            ),
            re.compile(
                rf"\+\s*{_NUM_CAPTURE}{espaco}(?:de\s+)?\b{re.escape(alias)}\b",
                re.IGNORECASE,
            ),
        )
        for pat in padroes:
            m = pat.search(texto or "")
            if m:
                valor = _parse_numero(m.group(1))
                if valor > 0:
                    achados[canonico] = max(achados.get(canonico, 0), valor)
                    break
    return achados


def extrair_atributos(texto: str) -> Tuple[Dict[str, int], Dict[str, int]]:
    """Retorna `(atributos_primarios, atributos_secundarios)` extraídos do texto."""
    if not texto:
        return {}, {}
    return _buscar_atributos(_PRIMARIOS_ALIASES, texto), _buscar_atributos(
        _SECUNDARIOS_ALIASES, texto
    )


# -----------------------------------------------------------------------------
# Atributos localizados (nomes exatos como aparecem no tooltip do idioma)
# -----------------------------------------------------------------------------

_ESTAT_PRIMARIA_PT = {
    "força": "Força",
    "forca": "Força",
    "agilidade": "Agilidade",
    "intelecto": "Intelecto",
    "vigor": "Vigor",
    "espírito": "Espírito",
    "espirito": "Espírito",
}

_ESTAT_PRIMARIA_EN = {
    "strength": "Strength",
    "agility": "Agility",
    "intellect": "Intellect",
    "stamina": "Stamina",
    "spirit": "Spirit",
}

_ESTAT_SECUNDARIA_PT = {
    "aceleração": "Aceleração",
    "aceleracao": "Aceleração",
    "crítico": "Crítico",
    "critico": "Crítico",
    "acerto crítico": "Acerto Crítico",
    "acerto critico": "Acerto Crítico",
    "maestria": "Maestria",
    "versatilidade": "Versatilidade",
    "finesse": "Finesse",
    "engenhosidade": "Engenhosidade",
    "percepção": "Percepção",
    "percepcao": "Percepção",
    "desenvoltura": "Desenvoltura",
    "destreza": "Destreza",
    "multicriação": "Multicriação",
    "multicriacao": "Multicriação",
    "robustez": "Robustez",
}

_ESTAT_SECUNDARIA_EN = {
    "haste": "Haste",
    "critical strike": "Critical Strike",
    "crit": "Critical Strike",
    "mastery": "Mastery",
    "versatility": "Versatility",
    "finesse": "Finesse",
    "ingenuity": "Ingenuity",
    "perception": "Perception",
    "deftness": "Deftness",
    "multicraft": "Multicraft",
    "resourcefulness": "Resourcefulness",
}

# Linhas de tooltip: "Nome +123" / "+123 Nome" / "Nome 123"
_PADRAO_NUM_NOME = re.compile(
    r"^[+\-]?\s*([\d][\d.,\u00a0 ]*)\s*(?:de\s+|of\s+|to\s+)?([^\d]+)$",
    re.IGNORECASE,
)
_PADRAO_NOME_NUM = re.compile(
    r"^([^\d]+?)\s*[+\-]?\s*([\d][\d.,\u00a0 ]*)$",
    re.IGNORECASE,
)


def _chave_estat(nome: str) -> str:
    chave = re.sub(r"\s+", " ", (nome or "").strip().lower())
    chave = chave.strip(" :+-\u00a0")
    chave = re.sub(r"^(?:de|of|to)\s+", "", chave)
    return chave


def _classificar_estat(
    nome: str, locale: str = "ptbr"
) -> Optional[Tuple[str, str]]:
    """
    Retorna `(tipo, nome_oficial)` para um nome exibido.

    Suporta:
    - nome exato: "Aceleração", "Haste"
    - frase PT: "Aumenta o seu índice de acerto crítico em"
    - escolha combinada: "Agilidade ou Intelecto" / "Agility or Intellect"
    """
    chave = _chave_estat(nome)
    if not chave:
        return None

    if locale == "en":
        mapas = (
            (_ESTAT_PRIMARIA_EN, "primario"),
            (_ESTAT_PRIMARIA_PT, "primario"),
            (_ESTAT_SECUNDARIA_EN, "secundario"),
            (_ESTAT_SECUNDARIA_PT, "secundario"),
        )
        separador = " or "
    else:
        mapas = (
            (_ESTAT_PRIMARIA_PT, "primario"),
            (_ESTAT_PRIMARIA_EN, "primario"),
            (_ESTAT_SECUNDARIA_PT, "secundario"),
            (_ESTAT_SECUNDARIA_EN, "secundario"),
        )
        separador = " ou "

    # 1) Nome exato
    for mapa, tipo in mapas:
        if chave in mapa:
            return tipo, mapa[chave]

    # 2) Escolha combinada ("Agilidade ou Intelecto" / "Agility or Intellect")
    partes = [p.strip() for p in re.split(r"\s+(?:ou|or)\s+|[\/]", chave) if p.strip()]
    if len(partes) > 1:
        achados: List[Tuple[str, str]] = []
        for parte in partes:
            achado = None
            for mapa, tipo in mapas:
                if parte in mapa:
                    achado = (tipo, mapa[parte])
                    break
            if achado is None:
                break
            achados.append(achado)
        if len(achados) == len(partes):
            tipos = {tipo for tipo, _ in achados}
            if len(tipos) == 1:
                return achados[0][0], separador.join(nome_of for _, nome_of in achados)

    # 3) Frase localizada ("Aumenta o seu índice de acerto crítico em",
    #    "Improves your critical strike rating by"). Exige "índice/rating"
    #    para não confundir texto de efeitos com atributos.
    if re.search(r"\b(?:índice|indice|rating)\b", chave):
        for mapa, tipo in mapas:
            for alias, canonico in sorted(
                mapa.items(), key=lambda kv: -len(kv[0])
            ):
                if re.search(rf"\b{re.escape(alias)}\b", chave):
                    return tipo, canonico
    return None


def _atributo_da_linha(
    linha: str, locale: str = "ptbr"
) -> Optional[Tuple[str, str, int]]:
    """Interpreta uma linha de atributo preservando o nome exibido."""
    linha = re.sub(r"\s+", " ", linha).strip()
    if not linha or len(linha) > 120:
        return None
    # Não interpretar texto de efeitos como linha de atributo
    if re.match(
        r"^(?:equip(?:ado|ar|amento)?|use|usar|uso|chance ao acertar|"
        r"chance on hit|acerto)\b",
        linha,
        re.IGNORECASE,
    ):
        return None

    nome = ""
    valor_txt = ""

    m = _PADRAO_NUM_NOME.match(linha)
    if m:
        valor_txt, nome = m.group(1), m.group(2)
    else:
        m = _PADRAO_NOME_NUM.match(linha)
        if m:
            nome, valor_txt = m.group(1), m.group(2)

    if not nome:
        return None

    nome = nome.strip(" :;,\u00a0[]()")
    nome = re.sub(r"\s+", " ", nome)
    if not nome or len(nome) > 60 or any(ch.isdigit() for ch in nome):
        return None

    achado = _classificar_estat(nome, locale)
    if not achado:
        return None
    tipo, canonico = achado

    # Preserva a grafia exibida quando o nome é curto (não é uma frase)
    if len(nome) <= 30 and not re.search(r"\b(?:aumenta|índice|indice)\b", nome, re.I):
        nome_exibicao = nome
    else:
        nome_exibicao = canonico

    valor = _parse_numero(valor_txt)
    if valor <= 0 or valor > 1_000_000:
        return None
    return tipo, nome_exibicao, valor


def extrair_atributos_de_efeito(
    texto: str, locale: str = "ptbr"
) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Extrai atributos de textos de efeito de encantamentos/gemas:
    "aumentando em 30 a Engenhosidade" -> Engenhosidade: 30.
    Usado apenas quando o tooltip não tem linha numérica de atributo.
    """
    primarios: Dict[str, int] = {}
    secundarios: Dict[str, int] = {}
    if not texto:
        return primarios, secundarios

    if locale == "en":
        mapas = (
            (_ESTAT_PRIMARIA_EN, primarios),
            (_ESTAT_PRIMARIA_PT, primarios),
            (_ESTAT_SECUNDARIA_EN, secundarios),
            (_ESTAT_SECUNDARIA_PT, secundarios),
        )
    else:
        mapas = (
            (_ESTAT_PRIMARIA_PT, primarios),
            (_ESTAT_PRIMARIA_EN, primarios),
            (_ESTAT_SECUNDARIA_PT, secundarios),
            (_ESTAT_SECUNDARIA_EN, secundarios),
        )

    for mapa, alvo in mapas:
        for alias, canonico in sorted(
            mapa.items(), key=lambda kv: -len(kv[0])
        ):
            if canonico in alvo:
                continue
            for m in re.finditer(
                rf"\b{re.escape(alias)}\b", texto, re.IGNORECASE
            ):
                antes = texto[max(0, m.start() - 60) : m.start()]
                numeros = re.findall(r"\d[\d.,]*", antes)
                if not numeros:
                    continue
                valor = _parse_numero(numeros[-1])
                if valor:
                    alvo[canonico] = max(alvo.get(canonico, 0), valor)
                    break

    m = re.search(
        r"\+\s*(\d+)\s*(?:de\s+)?(Atributo Prim[áa]rio|Primary Stat)",
        texto,
        re.IGNORECASE,
    )
    if m:
        nome = m.group(2).strip()
        nome = "Atributo Primário" if nome.lower().startswith("atributo") else "Primary Stat"
        primarios[nome] = max(primarios.get(nome, 0), int(m.group(1)))

    return primarios, secundarios


def extrair_atributos_localizados(
    texto: str, locale: str = "ptbr"
) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Extrai atributos primários/secundários mantendo o nome EXATO do tooltip
    do idioma solicitado (ptbr ou en), sem tradução automática.
    """
    primarios: Dict[str, int] = {}
    secundarios: Dict[str, int] = {}
    if not texto:
        return primarios, secundarios

    # Gemas multi-linha:
    # PT: "+\n16\nde Aceleração e +\n7\nde Acerto Crítico"
    # EN: "+\n16\nHaste & +\n7\nCritical Strike"
    texto = re.sub(
        r"\+\s*\n\s*(\d+)\s*\n\s*(?:de\s+)?([A-Za-zÀ-ÿ' ]+?)\s*"
        r"(?:e|&|and)\s*\+\s*\n\s*(\d+)\s*\n\s*(?:de\s+)?"
        r"([A-Za-zÀ-ÿ' ]+)",
        r"\1 \2\n\3 \4",
        texto,
        flags=re.IGNORECASE,
    )
    texto = re.sub(
        r"\+\s*\n\s*(\d+)\s*\n\s*(?:de\s+)?([A-Za-zÀ-ÿ' ]+)",
        r"\1 \2",
        texto,
        flags=re.IGNORECASE,
    )

    # Junta "+" isolado com o número da linha seguinte:
    # PT: "... em +\n86" / EN: "+\n86 Critical Strike"
    texto = re.sub(r"\+\s*\n\s*(\d[\d.,]*)", r"+ \1", texto)

    for linha in texto.splitlines():
        achado = _atributo_da_linha(linha, locale)
        if not achado:
            continue
        tipo, nome, valor = achado
        alvo = primarios if tipo == "primario" else secundarios
        alvo[nome] = max(alvo.get(nome, 0), valor)

    return primarios, secundarios


def extrair_efeito(texto: str) -> str:
    """Captura efeitos de equipar/usar, procs e encantamentos do tooltip."""
    if not texto:
        return ""
    texto_limpo = re.sub(r"[ \t]+", " ", texto)
    m = re.search(
        r"(Encanta permanentemente.+?|Permanently enchants.+?)"
        r"(?=\n\s*\n|$)",
        texto_limpo,
        re.IGNORECASE | re.DOTALL,
    )
    if not m:
        m = re.search(
            r"(?:Equip(?:ado|ar|amento)?|Use|Usar|Uso|Chance ao acertar|"
            r"Acerto|Equip effect|Chance on hit)\s*:\s*(.+?)(?=\n\s*\n|$)",
            texto_limpo,
            re.IGNORECASE | re.DOTALL,
        )
    if not m:
        return ""
    efeito = re.sub(r"\s+", " ", m.group(1)).strip()
    # Remove rodapés do tooltip que podem entrar na captura
    for marcador in (
        " Requer Nível",
        " Preço de Venda",
        " Vendido por",
        " Venda:",
        " Durabilidade",
    ):
        posicao = efeito.find(marcador)
        if posicao > 0:
            efeito = efeito[:posicao].strip()
    return efeito[:800]


# =============================================================================
# Slot / tipo de armadura
# =============================================================================

# A ordem importa: regras de armas vêm antes de "Mãos" para que
# "Arma de Duas Mãos" não seja classificado como luva.
_SLOT_REGRAS = (
    (r"arma de (?:duas|2) m[ãa]os|\btwo.?hand", "Arma de 2 Mãos"),
    (r"arma de (?:uma|1) m[ãa]o|\bone.?hand", "Arma de 1 Mão"),
    (r"\bescudo\b|\bshield\b", "Escudo"),
    (r"m[ãa]o secund[áa]ria|\boff.?hand\b", "Mão Secundária"),
    (r"\bcajado\b|\bstaff\b", "Arma de 2 Mãos"),
    # Wowhead exibe o slot em linha própria: "Uma Mão" / "Duas Mãos"
    (r"^\s*(?:uma|1)\s*m[ãa]o\s*$", "Arma de 1 Mão"),
    (r"^\s*(?:duas|2)\s*m[ãa]os\s*$", "Arma de 2 Mãos"),
    (r"\bcabe[çc]a\b|\bhead\b", "Cabeça"),
    (r"\bpesco[çc]o\b|\bcolar\b|\bneck\b", "Colar"),
    (r"\bombros?\b|\bombreiras?\b|\bshoulders?\b", "Ombros"),
    (r"\bcostas?\b|\bcapa\b|\bback\b|\bcloak\b", "Costas"),
    (r"\bpeito\b|\bt[úu]nica\b|\bchest\b|\brobe\b", "Peito"),
    (r"\bpulsos?\b|\bpunhos?\b|\bwrist\b", "Pulso"),
    (r"\bm[ãa]os\b|\bluvas?\b|\bhands\b|\bgloves?\b", "Mãos"),
    (r"\bcintura\b|\bcinto\b|\bwaist\b|\bbelt\b", "Cintura"),
    (r"\bpernas\b|\bcal[çc]as\b|\blegs\b", "Pernas"),
    (r"\bp[ée]s\b|\bbotas?\b|\bfeet\b|\bboots?\b", "Pés"),
    (r"\banel\b|\bfinger\b|\bring\b", "Anel"),
    (r"\bberloque\b|\btrinket\b", "Berloque"),
)

_ARMADURA_REGRAS = (
    (r"\btecidos?\b|\bcloth\b", "Tecido"),
    (r"\bcouros?\b|\bleather\b", "Couro"),
    (r"\bmalhas?\b|\bmail\b", "Malha"),
    (r"\bplacas?\b|\bplate\b", "Placas"),
)


def extrair_slot_localizado(texto: str) -> Tuple[str, str]:
    """
    Retorna `(slot_normalizado, linha_fonte)` preservando a linha original
    do tooltip (ex.: "Uma Mão", "One-Hand").
    """
    if not texto:
        return "", ""
    linhas = [ln.strip() for ln in texto.splitlines() if ln.strip()]
    for linha in linhas:
        if len(linha) > 48:
            continue
        for padrao, nome in _SLOT_REGRAS:
            if re.search(padrao, linha, re.IGNORECASE):
                return nome, linha
    for padrao, nome in _SLOT_REGRAS:
        if re.search(padrao, texto, re.IGNORECASE):
            return nome, ""
    return "", ""


def extrair_slot(texto: str) -> str:
    """
    Detecta o slot do item. Prioriza linhas curtas do tooltip (evita
    falsos positivos em descrições de efeitos).
    """
    return extrair_slot_localizado(texto)[0]


def extrair_tipo_armadura_localizado(texto: str) -> Tuple[str, str]:
    """Retorna `(tipo_normalizado, linha_fonte)` do tipo de armadura."""
    if not texto:
        return "", ""
    linhas = [ln.strip() for ln in texto.splitlines() if ln.strip()]
    for linha in linhas:
        if len(linha) > 24:
            continue
        for padrao, nome in _ARMADURA_REGRAS:
            if re.search(padrao, linha, re.IGNORECASE):
                return nome, linha
    for padrao, nome in _ARMADURA_REGRAS:
        if re.search(padrao, texto, re.IGNORECASE):
            return nome, ""
    return "", ""


def extrair_tipo_armadura(texto: str) -> str:
    return extrair_tipo_armadura_localizado(texto)[0]


# =============================================================================
# Parsing de HTML
# =============================================================================

def _qualidade_da_pagina(soup: BeautifulSoup) -> int:
    """Procura a qualidade (q3/q4/q5/quality-N) dentro dos tooltips."""
    for sel in (".wowhead-tooltip", ".tooltip", "#main-contents", "h1"):
        try:
            elementos = soup.select(sel)
        except Exception:
            continue
        for el in elementos:
            qualidade = qualidade_de_classes(el.get("class") or [])
            if qualidade:
                return qualidade
            for sub in el.find_all(True):
                classes_sub = str(_attr(sub, "class")).split()
                qualidade = qualidade_de_classes(classes_sub)
                if qualidade:
                    return qualidade
    return 0


_TEXTOS_TOOLTIP_SELECTORES = (
    ".wowhead-tooltip",
    ".tooltip",
    "#tiptip_content",
    ".tiptip_content",
    ".wttooltip",
    "[id^='icontooltip']",
)


def _texto_tooltips(soup: BeautifulSoup, pagina_item: bool = False) -> str:
    partes: List[str] = []
    for sel in _TEXTOS_TOOLTIP_SELECTORES:
        try:
            for el in soup.select(sel):
                txt = el.get_text("\n", strip=True)
                if txt:
                    partes.append(txt)
        except Exception:
            continue

    if not partes and pagina_item:
        main = (
            soup.select_one("#main-contents")
            or soup.select_one("#content")
            or soup.select_one("main")
            or soup.body
        )
        if main is not None:
            partes.append(main.get_text("\n", strip=True))

    return "\n".join(partes)


#: Escala válida de `icone_fonte`.
#: `tooltip_http` vem do enriquecimento leve (F-05/P-03), sem browser.
FONTES_ICONE = (
    "pagina",
    "og_image",
    "cdn_inferido",
    "tooltip_http",
    "llm",
    "ausente",
)
#: Escala válida de `nome_ptbr_fonte` / `nome_en_fonte`.
FONTES_NOME = ("crawl_ptbr", "crawl_en", "tooltip_http", "llm", "ausente")
#: Escala válida de `atributos_fonte`.
FONTES_ATRIBUTOS = ("tooltip_pagina", "tooltip_http", "llm", "ausente")


def _fonte_declarada(
    brutos: Iterable[Dict[str, Any]],
    chaves: Tuple[str, ...],
    validas: Tuple[str, ...],
) -> str:
    """Lê a primeira fonte declarada explicitamente e válida nos brutos."""
    for bruto in brutos:
        if not isinstance(bruto, dict):
            continue
        for chave in chaves:
            valor = str(bruto.get(chave) or "").strip().lower()
            if valor in validas:
                return valor
    return ""


def _fonte_icone(icone_url: str, declarada: Any = "") -> str:
    """Normaliza a origem de um ícone para a escala `FONTES_ICONE`."""
    valor = str(declarada or "").strip().lower()
    if valor in FONTES_ICONE and valor != "ausente":
        return valor
    return "cdn_inferido" if icone_url else "ausente"


def _icone_da_pagina_com_fonte(soup: BeautifulSoup) -> Tuple[str, str]:
    """Retorna `(url, fonte)` do ícone: tooltip/img (`pagina`) ou og:image."""
    seletores = (
        ".wowhead-tooltip ins",
        ".tooltip ins",
        "#main-contents ins",
        "ins[style*='icons']",
        "ins[style*='icon']",
    )
    for sel in seletores:
        try:
            for el in soup.select(sel):
                url = _icone_do_elemento(el)
                if url:
                    return url, "pagina"
        except Exception:
            continue

    og = soup.select_one("meta[property='og:image']")
    conteudo_og = _attr(og, "content") if og is not None else ""
    if conteudo_og:
        url = montar_icone_url(conteudo_og)
        if url:
            return url, "og_image"

    for img in soup.select("img"):
        url = montar_icone_url(_attr(img, "src") or _attr(img, "data-src"))
        if url and "wow/icons" in url:
            return url, "pagina"
    return "", "ausente"


def _icone_da_pagina(soup: BeautifulSoup) -> str:
    """Compatibilidade: apenas a URL do ícone da página."""
    return _icone_da_pagina_com_fonte(soup)[0]


def _url_item(href: str, item_id: str, page_url: str) -> str:
    if href and "item=" in href and not href.startswith(("#", "javascript")):
        return urljoin(page_url or "https://www.wowhead.com", href)
    return f"https://www.wowhead.com/pt/item={item_id}"


_CLASSES_ANCHOR_NOME = ("listview-cleartext",)


def _container_da_linha(a: Any) -> Any:
    """Encontra o container de linha (`tr`/`li`) de um anchor de item."""
    if a is None:
        return None
    try:
        # BeautifulSoup (>=4) aceita uma lista de nomes de tag.
        return a.find_parent(["tr", "li"])
    except Exception:  # versões antigas que não aceitam lista
        for tag in ("tr", "li"):
            pai = a.find_parent(tag)
            if pai is not None:
                return pai
    return None


def _texto_atributos_anchor(a: Any) -> str:
    return " ".join(
        parte
        for parte in (
            _attr(a, "data-wowhead"),
            _attr(a, "data-tooltip"),
            _attr(a, "title"),
            _attr(a, "aria-label"),
        )
        if parte
    )


def _nome_do_anchor(a: Any) -> str:
    nome = a.get_text(" ", strip=True)
    if not nome:
        img = a.find("img")
        if img is not None:
            nome = _attr(img, "alt")
    return re.sub(r"\s+", " ", nome or "").strip()


def _qualidade_do_anchor(a: Any) -> int:
    """Detecta a qualidade a partir das classes do próprio anchor/ancestrais."""
    classes = [str(c) for c in (a.get("class") or [])]
    nivel = 0
    for ancestral in a.parents:
        nome_ancestral = getattr(ancestral, "name", None)
        if nome_ancestral in (None, "[document]", "html", "body"):
            break
        attrs_ancestral = getattr(ancestral, "attrs", None) or {}
        classes += [str(c) for c in (attrs_ancestral.get("class") or [])]
        nivel += 1
        if nivel >= 3:
            break
    return qualidade_de_classes(classes)


def _coletar_na_linha(linha: Any, item_id: str, extrair: Any) -> Any:
    """Aplica `extrair` somente a elementos da MESMA linha com o mesmo item."""
    if linha is None:
        return None
    for el in linha.find_all(True):
        data_wowhead = _attr(el, "data-wowhead")
        href = _attr(el, "href")
        m = re.search(r"item=(\d+)", data_wowhead) or re.search(
            r"item=(\d+)", href
        )
        if not m or m.group(1) != item_id:
            continue
        valor = extrair(el, data_wowhead, href)
        if valor:
            return valor
    return None


def _bonus_da_linha(linha: Any, item_id: str) -> List[str]:
    valor = _coletar_na_linha(
        linha, item_id, lambda el, dw, href: extrair_bonus_ids(dw, href)
    )
    return list(valor or [])


def _ilvl_da_linha(linha: Any, item_id: str) -> int:
    valor = _coletar_na_linha(
        linha,
        item_id,
        lambda el, dw, href: extrair_ilvl(
            dw,
            _attr(el, "data-tooltip"),
            _attr(el, "title"),
            _attr(el, "aria-label"),
        ),
    )
    return int(valor or 0)


def extrair_variante_anchor(
    a: Any, page_url: str = ""
) -> Optional[Dict[str, Any]]:
    """
    Extrai UMA variante (`item + bonus`) de um anchor de listagem.

    Regras:
    - o anchor é aceito se tiver nome não vazio OU `data-wowhead` com
      `ilvl`/`bonus`;
    - quando o próprio anchor não traz `bonus`/`ilvl`, procura apenas DENTRO
      do container da mesma linha (`tr`/`li`), nunca em outro item;
    - `variante_fonte` = "listagem" quando há bônus, "canonica" quando não há.
    """
    if a is None:
        return None

    href = _attr(a, "href")
    data_wowhead = _attr(a, "data-wowhead")
    m = re.search(r"item=(\d+)", data_wowhead) or re.search(r"item=(\d+)", href)
    if not m:
        return None
    item_id = m.group(1)

    nome = _nome_do_anchor(a)
    ilvl = extrair_ilvl(
        data_wowhead,
        _attr(a, "data-tooltip"),
        _attr(a, "title"),
        _attr(a, "aria-label"),
    )
    bonus_ids = extrair_bonus_ids(data_wowhead, href)

    # Aceita apenas anchors com nome ou atributo explícito de item.
    if not nome and not ilvl and not bonus_ids:
        return None

    # Completa bônus/ilvl ausentes a partir da linha do próprio item.
    if not bonus_ids or not ilvl:
        linha = _container_da_linha(a)
        if linha is not None:
            if not bonus_ids:
                bonus_ids = _bonus_da_linha(linha, item_id)
            if not ilvl:
                ilvl = _ilvl_da_linha(linha, item_id)

    classes = [str(c) for c in (a.get("class") or [])]
    if any(c in _CLASSES_ANCHOR_NOME for c in classes):
        prioridade_nome = 2
    elif nome:
        prioridade_nome = 1
    else:
        prioridade_nome = 0

    pai = a.find_parent(["tr", "li", "div"])
    icone = _icone_do_elemento(a)
    if not icone and pai is not None:
        icone = _icone_do_elemento(pai)

    return {
        "item_id": item_id,
        "nome": nome,
        "item_level": ilvl,
        "bonus_ids": bonus_ids,
        "qualidade": _qualidade_do_anchor(a),
        "url": _url_item(href, item_id, page_url),
        "icone_url": icone,
        "_icone_fonte": "pagina" if icone else "ausente",
        "_contexto": _texto_atributos_anchor(a),
        "variante_fonte": "listagem" if bonus_ids else "canonica",
        "_prioridade_nome": prioridade_nome,
    }


def parse_links_itens(html: str, page_url: str = "") -> List[Dict[str, Any]]:
    """
    Extrai itens brutos de uma listagem/guia (`a[href*=item]`,
    `[data-wowhead*=item]`).

    Emite **1 registro por variação** (`item + bonus`), fazendo merge dos
    anchors que apontam para a mesma variação: um anchor de ícone vazio
    (sem nome) não gera registro próprio quando existe um anchor nomeado
    na mesma linha para o mesmo item.
    """
    soup = BeautifulSoup(html or "", "html.parser")
    itens: List[Dict[str, Any]] = []
    vistos = set()

    variantes = [
        v
        for v in (
            extrair_variante_anchor(a, page_url)
            for a in soup.select(
                "a[href*='item='], a[data-wowhead*='item=']"
            )
        )
        if v
    ]

    grupos: Dict[Tuple[str, Tuple[str, ...]], Dict[str, Any]] = {}
    ordem_grupos: List[Tuple[str, Tuple[str, ...]]] = []
    for v in variantes:
        chave_grupo = (v["item_id"], tuple(v["bonus_ids"]))
        atual = grupos.get(chave_grupo)
        if atual is None:
            grupos[chave_grupo] = dict(v)
            ordem_grupos.append(chave_grupo)
            continue

        # Nome/qualidade: vence o anchor nomeado (ex.: listview-cleartext).
        if (
            v["_prioridade_nome"] > atual["_prioridade_nome"]
            or (not atual["nome"] and v["nome"])
        ):
            atual["_prioridade_nome"] = max(
                atual["_prioridade_nome"], v["_prioridade_nome"]
            )
            atual["nome"] = v["nome"] or atual["nome"]
        if v["item_level"] and (
            not atual["item_level"] or v["item_level"] > atual["item_level"]
        ):
            atual["item_level"] = v["item_level"]
        if v["qualidade"] and not atual["qualidade"]:
            atual["qualidade"] = v["qualidade"]
        if v["icone_url"] and not atual["icone_url"]:
            atual["icone_url"] = v["icone_url"]
        if v["url"] and not atual["url"]:
            atual["url"] = v["url"]
        if len(v["_contexto"]) > len(atual["_contexto"]):
            atual["_contexto"] = v["_contexto"]

    for chave_grupo in ordem_grupos:
        v = grupos[chave_grupo]
        # Nunca emitir um registro completamente vazio.
        if not v["nome"] and not v["bonus_ids"]:
            continue
        chave = chave_variacao(
            v["item_id"], int(v["item_level"] or 0), v["bonus_ids"], ""
        )
        if chave in vistos:
            continue
        vistos.add(chave)
        itens.append(
            {
                "id": v["item_id"],
                "nome": v["nome"],
                "item_level": v["item_level"],
                "qualidade": v["qualidade"],
                "icone_url": v["icone_url"],
                "_icone_fonte": v.get("_icone_fonte")
                or ("pagina" if v["icone_url"] else "ausente"),
                "bonus_ids": v["bonus_ids"],
                "url": v["url"],
                "_contexto": v["_contexto"],
                "variante_fonte": v["variante_fonte"],
            }
        )

    return itens


def parse_item_unico(html: str, page_url: str) -> Optional[Dict[str, Any]]:
    """Interpreta uma página individual de item (`/item=12345`)."""
    m = re.search(r"item=(\d+)", page_url or "")
    if not m:
        return None
    item_id = m.group(1)

    soup = BeautifulSoup(html or "", "html.parser")
    h1 = soup.select_one("h1.heading-size-1") or soup.select_one("h1")
    nome = h1.get_text(" ", strip=True) if h1 is not None else ""
    qualidade = (
        qualidade_de_classes(_attr(h1, "class").split()) if h1 is not None else 0
    )
    if not qualidade:
        qualidade = _qualidade_da_pagina(soup)

    contexto = _texto_tooltips(soup, pagina_item=True)
    icone, icone_fonte = _icone_da_pagina_com_fonte(soup)
    ilvl = extrair_ilvl(contexto)

    return {
        "id": item_id,
        "nome": re.sub(r"\s+", " ", nome or "").strip(),
        "item_level": ilvl,
        "qualidade": qualidade,
        "icone_url": icone,
        "_icone_fonte": icone_fonte,
        "bonus_ids": extrair_bonus_ids(page_url),
        "url": page_url,
        "_contexto": contexto,
    }


# =============================================================================
# Tipo de item, profissão de craft, embelezamento, missiva, gema e rank
# =============================================================================

PROFISSOES_CRAFT = {
    "Alquimia": ("alchemy", "alquimia"),
    "Ferraria": ("blacksmithing", "ferraria"),
    "Encantamento": ("enchanting", "encantamento"),
    "Engenharia": ("engineering", "engenharia"),
    "Couraria": ("leatherworking", "couraria"),
    "Alfaiataria": ("tailoring", "alfaiataria"),
    "Joalheria": ("jewelcrafting", "joalheria"),
    "Escrivania": ("inscription", "escrivania"),
    "Mineração": ("mining", "mineração", "mineracao"),
    "Herborismo": ("herbalism", "herborismo"),
    "Esfolamento": ("skinning", "esfolamento"),
    "Culinária": ("cooking", "culinária", "culinaria"),
    "Pesca": ("fishing", "pesca"),
}


#: Regex de marcador textual de craft ("Feito por", "Crafted by", ...).
_RE_FEITO_POR = re.compile(
    r"feito por|criado por|crafted by|created by|fabricado por", re.IGNORECASE
)

#: Diretório da base de conhecimento local usado no fallback receita→profissão.
_DIR_BASE_CONHECIMENTO = (
    Path(__file__).resolve().parent / "base_conhecimento_ai_studio"
)

#: Cache do mapa id/spell/receita → profissão (carregado sob demanda).
_MAPA_CRAFT_CACHE: Optional[Dict[str, Dict[str, str]]] = None


def _profissao_de_chave(chave: Any) -> str:
    """Converte uma chave de categoria/URL ("ferraria") no nome canônico."""
    baixo = str(chave or "").lower()
    if not baixo:
        return ""
    for nome, variantes in PROFISSOES_CRAFT.items():
        if nome.lower() == baixo or baixo in variantes:
            return nome
    return ""


def _varrer_mapa_craft(
    no: Any,
    profissao_atual: str,
    mapas: Dict[str, Dict[str, str]],
) -> None:
    """Percorre a base de conhecimento acumulando id/spell/receita→profissão."""
    if isinstance(no, dict):
        propria = _profissao_de_chave(no.get("profissao"))
        contexto = propria or profissao_atual
        if contexto:
            for chave in ("id", "item_id", "spell_id", "recipe_id", "recipe"):
                valor = no.get(chave)
                if valor in (None, "", 0):
                    continue
                mapas.setdefault(chave, {})[str(valor)] = contexto
        for chave_dict, valor in no.items():
            seguinte = contexto
            if isinstance(valor, (dict, list)):
                por_chave = _profissao_de_chave(chave_dict)
                if por_chave:
                    seguinte = por_chave
                # P-07/F-06: em `craft_armas_s2.json` os IDs de item são as
                # PRÓPRIAS CHAVES do mapa (ex.: "237831"), não campos `id`.
                # Sem isto, o mapa receita→profissão ficava vazio para armas.
                chave_id = str(chave_dict).strip()
                if chave_id.isdigit() and chave_id != "0":
                    propria_valor = (
                        _profissao_de_chave(valor.get("profissao"))
                        if isinstance(valor, dict)
                        else ""
                    )
                    alvo = propria_valor or seguinte
                    if alvo:
                        mapas.setdefault("id", {})[chave_id] = alvo
            _varrer_mapa_craft(valor, seguinte, mapas)
    elif isinstance(no, (list, tuple)):
        for valor in no:
            _varrer_mapa_craft(valor, profissao_atual, mapas)


def _mapa_craft() -> Dict[str, Dict[str, str]]:
    """Carrega (uma vez) o mapa receita→profissão da base de conhecimento."""
    global _MAPA_CRAFT_CACHE
    if _MAPA_CRAFT_CACHE is not None:
        return _MAPA_CRAFT_CACHE

    mapas: Dict[str, Dict[str, str]] = {}
    for nome_arquivo in ("craft_receitas_s2.json", "craft_armas_s2.json"):
        caminho = _DIR_BASE_CONHECIMENTO / nome_arquivo
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except (OSError, ValueError):
            continue
        _varrer_mapa_craft(dados, "", mapas)
    _MAPA_CRAFT_CACHE = mapas
    return mapas


def profissao_por_receita(*ids: Any) -> str:
    """
    Profissão de craft a partir de item/spell/recipe IDs conhecidos.

    É o fallback (3) da detecção de profissão: quando a página não traz link
    de profissão nem "Feito por", usa o inventário local de receitas.
    """
    mapas = _mapa_craft()
    for chave in ("id", "item_id", "spell_id", "recipe_id", "recipe"):
        mapa = mapas.get(chave) or {}
        for ident in ids:
            if ident in (None, "", 0):
                continue
            profissao = mapa.get(str(ident))
            if profissao:
                return profissao
    return ""


def _profissao_craft_com_fonte(soup: BeautifulSoup) -> Tuple[str, str]:
    """
    Detecta a profissão de craft e a origem da evidência.

    Hierarquia: link de guia de profissão → link de receita/spell →
    texto "Feito por/Crafted by" + nome de profissão.
    """
    # (1) Links de guias de profissão são específicos e seguros.
    for a in soup.select("a[href*='professions/']"):
        rotulo = f"{a.get_text(' ', strip=True)} {_attr(a, 'href')}".lower()
        for nome, chaves in PROFISSOES_CRAFT.items():
            if any(chave in rotulo for chave in chaves):
                return nome, "link"

    # (2) Link de receita (spell=) resolvido pelo mapa local de receitas.
    for a in soup.select("a[href*='spell='], a[href*='recipe=']"):
        m = re.search(r"(?:spell|recipe)=(\d+)", _attr(a, "href") or "")
        if not m:
            continue
        nome = profissao_por_receita(m.group(1))
        if nome:
            return nome, "receita"

    # (3) "Feito por/Crafted by" seguido de nome de profissão.
    texto = soup.get_text(" ", strip=True)
    if _RE_FEITO_POR.search(texto):
        baixo = texto.lower()
        for nome, chaves in PROFISSOES_CRAFT.items():
            if any(chave in baixo for chave in chaves):
                return nome, "texto"
    return "", ""


def _profissao_craft_da_pagina(soup: BeautifulSoup) -> str:
    """Detecta a profissão que crafta o item a partir de links/texto da página."""
    return _profissao_craft_com_fonte(soup)[0]


_SLOT_ALVO_REGRAS = (
    (r"ferramenta|tool", "Ferramenta"),
    (r"arma de duas m[ãa]os|two.?hand|arma de 2 m[ãa]os", "Arma de 2 Mãos"),
    (r"arma de uma m[ãa]o|one.?hand|arma de 1 m[ãa]o|\barma\b|weapon", "Arma"),
    (r"escudo|shield", "Escudo"),
    (r"m[ãa]o secund[áa]ria|off.?hand", "Mão Secundária"),
    (r"cabe[çc]a|\bhead\b", "Cabeça"),
    (r"ombros?|shoulders?", "Ombros"),
    (r"costas|back|cloak", "Costas"),
    (r"peito|chest", "Peito"),
    (r"pulseira|wrist", "Pulso"),
    (r"m[ãa]os|hands|gloves", "Mãos"),
    (r"cintura|waist", "Cintura"),
    (r"pernas|legs", "Pernas"),
    (r"botas|feet|boots", "Pés"),
    (r"dedos|fingers|anel|finger|ring", "Anel"),
    (r"colar|neck", "Colar"),
)


def extrair_slot_alvo(texto: str) -> str:
    """Slot-alvo de encantamentos/aplicações (ex.: Arma, Peito, Pulseira)."""
    if not texto:
        return ""
    linhas = [ln.strip() for ln in texto.splitlines() if ln.strip()][:80]
    for linha in linhas:
        if len(linha) > 60:
            continue
        for padrao, nome in _SLOT_ALVO_REGRAS:
            if re.search(padrao, linha, re.IGNORECASE):
                return nome
    for padrao, nome in _SLOT_ALVO_REGRAS:
        if re.search(padrao, texto, re.IGNORECASE):
            return nome
    return ""


def detectar_embelezamento(texto: str) -> bool:
    return bool(
        re.search(r"\bembellishment\b|\bembelezamento\b", texto or "", re.I)
    )


def extrair_missiva_atributo(nome: str, texto: str = "") -> str:
    """Atributo vinculado a uma missiva (ex.: Engenhosidade, Finesse)."""
    alvo = f"{nome} {texto}".lower()
    if "missiva" not in alvo and "missive" not in alvo:
        return ""
    for chave, canonico in sorted(
        _ESTAT_SECUNDARIA_PT.items(), key=lambda kv: -len(kv[0])
    ):
        if re.search(rf"\b{re.escape(chave)}\b", alvo):
            return canonico
    return ""


def extrair_gema_cor(texto: str) -> str:
    baixo = (texto or "").lower()
    regras = (
        (r"\bvermelh[ao]\b|\bred\b|\brubi\b|\bruby\b", "Vermelha"),
        (r"\bazul\b|\bblue\b|\bsafira\b|\bsapphire\b", "Azul"),
        (r"\bamarel[ao]\b|\byellow\b|\btop[áa]zio\b|\btopaz\b", "Amarela"),
        (r"\broxa\b|\bpurple\b|\bametista\b|\bamethyst\b", "Roxa"),
        (
            r"\bverde\b|\bgreen\b|\besmeralda\b|\bemerald\b|"
            r"\bperidoto\b|\bperidot\b",
            "Verde",
        ),
        (r"\blaranja\b|\borange\b|\bopala\b|\bopal\b", "Laranja"),
        (r"\bmeta\b|\bdiamante\b|\bdiamond\b", "Meta"),
    )
    for padrao, cor in regras:
        if re.search(padrao, baixo, re.IGNORECASE):
            return cor
    return ""


def extrair_rank(texto: str) -> int:
    m = re.search(r"\b(?:rank|grau)\s*(\d)\b", texto or "", re.IGNORECASE)
    return int(m.group(1)) if m else 0


#: Rótulo explícito de qualidade de craft (PT/EN) seguido do número.
_RE_ROTULO_QUALIDADE_CRAFT = re.compile(
    r"(?:Qualidade de cria[çc][ãa]o|Qualidade de fabrica[çc][ãa]o|"
    r"Crafting Quality|Craft Quality|Qualidade do craft)\s*:?\s*(\d)",
    re.IGNORECASE,
)

#: Marca `crafting-quality` no HTML (atributo com o valor da qualidade).
_RE_MARCA_CRAFTING_QUALITY = re.compile(
    r"crafting-quality[^>]{0,120}?(?:data-value|value|data-crafting-quality)"
    r"\s*=\s*[\"']?(\d)",
    re.IGNORECASE,
)

#: Contexto de craft na MESMA linha (exigido para R1..R5 / Rank N).
_RE_CONTEXTO_CRAFT = re.compile(
    r"\bcraft(?:ed|ing|s)?\b|\bfabricad?[oa]\b|\bfabrica[çc][ãa]o\b|"
    r"\bfeito por\b|\bcriado por\b",
    re.IGNORECASE,
)

#: Rótulo de rank de craft (R1..R5 ou Rank/Grau N).
_RE_ROTULO_RANK = re.compile(r"\bR(\d)\b|\b(?:rank|grau)\s*(\d)\b", re.IGNORECASE)


def extrair_qualidade_craft_detalhado(texto: str) -> Tuple[int, str]:
    """
    Extrai a qualidade de craft (R1..R5) e o motivo da decisão.

    Regras (da mais forte para a mais fraca):
    1. rótulo explícito "Qualidade de criação/Crafting Quality: N";
    2. marca `crafting-quality` no HTML com valor numérico;
    3. rótulo `R1..R5`/`Rank N` SOMENTE se a mesma linha tiver contexto de
       craft ("craft", "fabric", "feito por", "criado por").

    Texto genérico com a palavra "qualidade" (sem rótulo de craft) retorna 0,
    evitando falso positivo em itens não craftados.
    """
    bruto = texto or ""
    m = _RE_ROTULO_QUALIDADE_CRAFT.search(bruto)
    if m:
        return int(m.group(1)), f"texto:{m.group(0).strip()}"

    m = _RE_MARCA_CRAFTING_QUALITY.search(bruto)
    if m:
        return int(m.group(1)), "html:crafting-quality"

    for linha in bruto.splitlines():
        if not _RE_CONTEXTO_CRAFT.search(linha):
            continue
        m = _RE_ROTULO_RANK.search(linha)
        if not m:
            continue
        valor = int(m.group(1) or m.group(2))
        if not 1 <= valor <= 5:
            continue
        rotulo = f"R{m.group(1)}" if m.group(1) else f"Rank {m.group(2)}"
        return valor, f"texto:{rotulo}"
    return 0, ""


def extrair_qualidade_craft(texto: str) -> int:
    """Qualidade de craft (R1..R5), separada da raridade do item."""
    return extrair_qualidade_craft_detalhado(texto)[0]


MISSIVAS_TIPOS = [
    "Engenhosidade",
    "Finesse",
    "Desenvoltura",
    "Percepção",
    "Destreza",
    "Multicriação",
]

_SUBTIPO_REGRAS = (
    (r"\bespada\b|\bsword\b", "Espada"),
    (r"\bmachado\b|\baxe\b", "Machado"),
    (r"\bcajado\b|\bstaff\b", "Cajado"),
    (r"\badaga\b|\bdagger\b", "Adaga"),
    (r"\bma[çc]a\b|\bmace\b", "Maça"),
    (r"\blan[çc]a\b|\bpolearm\b", "Lança"),
    (r"\barco\b|\bbow\b", "Arco"),
    (r"\bbesta\b|\bcrossbow\b", "Besta"),
    (r"\bvarinha\b|\bwand\b", "Varinha"),
    (r"\bescudo\b|\bshield\b", "Escudo"),
    (r"\btotem\b", "Totem"),
)


def extrair_subtipo(texto: str) -> str:
    """Subtipo do item (Espada, Machado, Cajado, Escudo, ...)."""
    if not texto:
        return ""
    linhas = [ln.strip() for ln in texto.splitlines() if ln.strip()]
    for linha in linhas:
        if len(linha) > 40:
            continue
        for padrao, nome in _SUBTIPO_REGRAS:
            if re.search(padrao, linha, re.IGNORECASE):
                return nome
    for padrao, nome in _SUBTIPO_REGRAS:
        if re.search(padrao, texto, re.IGNORECASE):
            return nome
    return ""


_FONTE_RE = re.compile(
    r"^(?:Saqueado de|Dropped by|Vendido por|Sold by|Recompensa de|"
    r"Reward from|Contido em|Contained in|Fonte|Source|Feito por|"
    r"Crafted by|Criado por)\s*:?\s*.+$",
    re.IGNORECASE,
)


def extrair_fonte(texto: str) -> str:
    """Linha de fonte do item (drop, vendor, craft, recompensa, ...)."""
    if not texto:
        return ""
    for linha in texto.splitlines():
        linha = linha.strip()
        if _FONTE_RE.match(linha):
            return linha[:300]
    return ""


def extrair_vinculo_conteudo(texto: str) -> str:
    """Vínculo com conteúdo: Masmorra, Raid, Imersões, PvP, Profissão, etc."""
    baixo = (texto or "").lower()
    regras = (
        (r"\bmasmorra\b|\bdungeon\b", "Masmorra"),
        (r"\braid\b|\braide\b", "Raid"),
        (r"\bdelves?\b|\bimers[õo]es\b|\bimersoes\b", "Imersões"),
        (r"\bpvp\b|\bjx?j\b|\barena\b|\bcampo de batalha\b|\bbattleground\b", "PvP"),
        (r"\bprofiss[ãa]o\b|\bcrafted\b|\bfeito por\b|\bcriado por\b", "Profissão"),
        (r"\bmiss[ãa]o\b|\bquest\b", "Missão"),
        (r"\bvendedor\b|\bvendor\b|\bvendido por\b", "Vendedor"),
        (r"\bmundo\b|\bworld\b", "Mundo"),
    )
    encontrados = []
    for padrao, nome in regras:
        if re.search(padrao, baixo, re.IGNORECASE):
            encontrados.append(nome)
    return " / ".join(encontrados)


def classificar_tipo_item(
    nome: str, texto: str = "", categoria: str = "", url: str = ""
) -> str:
    """
    Classifica o item em gear/encantamento/gema/missiva/embelezamento/etc.

    Regra de segurança: se o tooltip tem slot de gear (Cabeça, Berloque,
    Arma...), o item NÃO é tratado como encantamento/gema apenas porque a
    URL do catálogo é genérica. Isso evita catálogos falsos.
    """
    nome_l = (nome or "").lower()
    cat_l = (categoria or "").lower()
    url_l = (url or "").lower()
    slot_detectado = extrair_slot(texto)

    if "missiva" in nome_l or "missiva" in cat_l:
        return "missiva"

    if detectar_embelezamento(texto):
        return "embelezamento"

    nome_indica_encantamento = (
        "encantamento" in nome_l or "enchant" in nome_l
    )
    if nome_indica_encantamento or (
        ("encantamento" in cat_l or "/items/enchants" in url_l)
        and not slot_detectado
    ):
        return "encantamento"

    # A rota /items/gems foi validada como catálogo real de gemas
    if "gema" in nome_l or "gemas" in cat_l or "/items/gems" in url_l:
        return "gema"

    if "ferramenta" in cat_l or "profiss" in cat_l:
        return "ferramenta"
    if "reagente" in cat_l:
        return "reagente"
    if "consum" in cat_l or "consum" in nome_l:
        return "consumivel"
    if slot_detectado or extrair_tipo_armadura(texto):
        return "gear"
    if re.search(
        r"\b(armadura|armor|peitoral|elmo|capacete|cal[çc]as|botas|luvas|"
        r"cinto|capa|manto|anel|colar|berloque|espada|machado|cajado|"
        r"adaga|ma[çc]a|arco|besta|escudo)\b",
        nome_l,
        re.IGNORECASE,
    ):
        return "gear"
    return "outro"


def extrair_detalhes_item(html: str, item: Dict[str, Any]) -> Dict[str, Any]:
    """Enriquece um item bruto com os dados do HTML da página individual."""
    soup = BeautifulSoup(html or "", "html.parser")
    novo = dict(item)

    h1 = soup.select_one("h1.heading-size-1") or soup.select_one("h1")
    if h1 is not None:
        nome = h1.get_text(" ", strip=True)
        if nome:
            novo["nome"] = re.sub(r"\s+", " ", nome)
        qualidade = qualidade_de_classes(_attr(h1, "class").split())
        if qualidade:
            novo["qualidade"] = qualidade

    contexto = _texto_tooltips(soup, pagina_item=True)
    if contexto:
        anterior = novo.get("_contexto") or ""
        novo["_contexto"] = (anterior + "\n" + contexto).strip()

    ilvl = extrair_ilvl(contexto)
    if ilvl:
        novo["item_level"] = ilvl

    if not novo.get("icone_url"):
        icone_novo, icone_fonte_nova = _icone_da_pagina_com_fonte(soup)
        novo["icone_url"] = icone_novo
        if icone_novo:
            novo["_icone_fonte"] = icone_fonte_nova

    if not novo.get("qualidade"):
        qualidade_pagina = _qualidade_da_pagina(soup)
        if qualidade_pagina:
            novo["qualidade"] = qualidade_pagina

    profissao_craft, profissao_fonte = _profissao_craft_com_fonte(soup)
    if profissao_craft:
        novo["_profissao_craft"] = profissao_craft
        novo["_profissao_craft_fonte"] = profissao_fonte

    return novo


def finalizar_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Consolida um item bruto no dicionário final com TODOS os campos exigidos:

    id, nome_ptbr, slot, tipo_armadura, qualidade, item_level, track,
    voidforged, atributos_primarios, atributos_secundarios,
    efeito_equip_uso, icone_url (+ extras: qualidade_nome, track_stage,
    bonus_ids, url).
    """
    contexto = item.get("_contexto") or ""
    nome = re.sub(r"\s+", " ", str(item.get("nome") or "")).strip()

    ilvl = int(item.get("item_level") or 0) or extrair_ilvl(contexto)
    qualidade = int(item.get("qualidade") or 0)

    primarios, secundarios = extrair_atributos(contexto)
    track, voidforged, stage = classificar_track(ilvl, f"{nome}\n{contexto}")

    slot = extrair_slot(contexto) or "N/A"
    tipo_armadura = extrair_tipo_armadura(contexto) or "N/A"

    icone = montar_icone_url(item.get("icone_url") or "")

    item_id: Any = item.get("id")
    if isinstance(item_id, str) and item_id.isdigit():
        item_id = int(item_id)

    return {
        "id": item_id,
        "nome_ptbr": nome,
        "slot": slot,
        "tipo_armadura": tipo_armadura,
        "qualidade": qualidade,
        "qualidade_nome": QUALIDADE_POR_ID.get(qualidade, "") if qualidade else "",
        "item_level": ilvl,
        "track": track,
        "track_stage": stage,
        "voidforged": bool(voidforged),
        "atributos_primarios": primarios,
        "atributos_secundarios": secundarios,
        "efeito_equip_uso": extrair_efeito(contexto),
        "icone_url": icone,
        "bonus_ids": item.get("bonus_ids") or [],
        "url": item.get("url") or "",
    }


# =============================================================================
# Consolidação bilíngue (EN + PT-BR) e variações por Bonus ID
# =============================================================================

def montar_id_completo(
    ident: Any, bonus_ids: Optional[List[str]], item_level: int
) -> str:
    """Monta um identificador completo `item=...&bonus=...&ilvl=...`."""
    partes = [f"item={ident}"]
    if bonus_ids:
        partes.append("bonus=" + ":".join(str(b) for b in bonus_ids))
    if item_level:
        partes.append(f"ilvl={int(item_level)}")
    return "&".join(partes)


def chave_variacao(
    ident: Any, item_level: int, bonus_ids: Optional[List[str]], stage: str = ""
) -> str:
    """
    Chave de unicidade de uma variação real do jogo.

    Inclui Bonus IDs para que dois itens de mesmo ID/ilvl com bônus diferentes
    permaneçam como linhas separadas.
    """
    bonus = ":".join(str(b) for b in (bonus_ids or []))
    return f"{ident}|{int(item_level or 0)}|{bonus}|{stage or ''}"


def finalizar_item_localizado(
    bruto: Dict[str, Any], locale: str = "ptbr"
) -> Dict[str, Any]:
    """Extrai campos de UM idioma a partir do HTML/tooltip daquele locale."""
    bruto = bruto or {}
    contexto = bruto.get("_contexto") or ""
    nome = re.sub(r"\s+", " ", str(bruto.get("nome") or "")).strip()

    primarios, secundarios = extrair_atributos_localizados(contexto, locale)
    slot, slot_fonte = extrair_slot_localizado(contexto)
    tipo, tipo_fonte = extrair_tipo_armadura_localizado(contexto)

    ilvl = int(bruto.get("item_level") or 0) or extrair_ilvl(contexto)
    qualidade = int(bruto.get("qualidade") or 0)
    track, voidforged, stage = classificar_track(ilvl, f"{nome}\n{contexto}")

    icone_url = montar_icone_url(bruto.get("icone_url") or "")

    return {
        "nome": nome,
        "atributos_primarios": primarios,
        "atributos_secundarios": secundarios,
        "slot": slot or "N/A",
        "slot_fonte": slot_fonte,
        "tipo_armadura": tipo or "N/A",
        "tipo_fonte": tipo_fonte,
        "efeito": extrair_efeito(contexto),
        "item_level": ilvl,
        "qualidade": qualidade,
        "track": track,
        "track_stage": stage,
        "voidforged": bool(voidforged),
        "icone_url": icone_url,
        "icone_fonte": _fonte_icone(icone_url, bruto.get("_icone_fonte")),
    }


def finalizar_item_bilingue(
    bruto: Dict[str, Any],
    pt_bruto: Optional[Dict[str, Any]] = None,
    en_bruto: Optional[Dict[str, Any]] = None,
    url_pt: str = "",
    url_en: str = "",
) -> Dict[str, Any]:
    """
    Consolida os dados das páginas PT-BR e EN sem traduzir nomes.

    - `nome_ptbr` vem exclusivamente da fonte PT-BR.
    - `nome_en` vem exclusivamente da fonte EN.
    - Atributos usam os nomes exatos do tooltip PT-BR; se o tooltip PT falhar,
      usa os nomes exatos do tooltip EN (registrado em `idioma_atributos_*`).
    """
    bruto = bruto or {}
    pagina = str(bruto.get("_pagina") or bruto.get("url") or "")
    locale_listagem = "ptbr" if "/pt/" in pagina else "en"

    if pt_bruto is None:
        pt_bruto = bruto if locale_listagem == "ptbr" else {}
    if en_bruto is None:
        en_bruto = bruto if locale_listagem == "en" else {}

    pt = finalizar_item_localizado(pt_bruto, "ptbr")
    en = finalizar_item_localizado(en_bruto, "en")

    nome_listagem = re.sub(r"\s+", " ", str(bruto.get("nome") or "")).strip()
    nome_ptbr = pt["nome"] or (nome_listagem if locale_listagem == "ptbr" else "")
    nome_en = en["nome"] or (nome_listagem if locale_listagem == "en" else "")

    prim_pt, sec_pt = pt["atributos_primarios"], pt["atributos_secundarios"]
    prim_en, sec_en = en["atributos_primarios"], en["atributos_secundarios"]

    primarios = prim_pt or prim_en
    secundarios = sec_pt or sec_en
    idioma_prim = "ptbr" if prim_pt else ("en" if prim_en else "")
    idioma_sec = "ptbr" if sec_pt else ("en" if sec_en else "")

    slot = pt["slot"] if pt["slot"] != "N/A" else en["slot"]
    tipo = (
        pt["tipo_armadura"]
        if pt["tipo_armadura"] != "N/A"
        else en["tipo_armadura"]
    )

    referencia = pt if pt["item_level"] else en
    ilvl = pt["item_level"] or en["item_level"] or int(bruto.get("item_level") or 0)
    qualidade = pt["qualidade"] or en["qualidade"] or int(bruto.get("qualidade") or 0)

    item_id: Any = bruto.get("id")
    if isinstance(item_id, str) and item_id.isdigit():
        item_id = int(item_id)

    bonus_ids = [str(b) for b in (bruto.get("bonus_ids") or [])]

    categoria = str(bruto.get("_categoria") or "")
    url_final = url_pt or bruto.get("url") or ""
    texto_total = "\n".join(
        parte
        for parte in (
            pt_bruto.get("_contexto") or "",
            en_bruto.get("_contexto") or "",
            nome_ptbr,
            nome_en,
        )
        if parte
    )
    url_classificacao = str(bruto.get("_pagina") or url_final)
    tipo_item = classificar_tipo_item(
        nome_ptbr or nome_en, texto_total, categoria, url_classificacao
    )

    # Catálogos (encantamento/gema) costumam trazer o valor no texto do efeito
    if tipo_item in ("encantamento", "gema") and not (
        prim_pt or sec_pt or prim_en or sec_en
    ):
        prim_efeito, sec_efeito = extrair_atributos_de_efeito(
            pt["efeito"] or "", "ptbr"
        )
        prim_efeito_en, sec_efeito_en = extrair_atributos_de_efeito(
            en["efeito"] or "", "en"
        )
        if prim_efeito or sec_efeito or prim_efeito_en or sec_efeito_en:
            prim_pt = prim_efeito
            sec_pt = sec_efeito
            prim_en = prim_efeito_en or prim_efeito
            sec_en = sec_efeito_en or sec_efeito
            primarios = prim_pt or prim_en
            secundarios = sec_pt or sec_en
            idioma_prim = (
                "ptbr" if prim_pt else ("en" if prim_en else "")
            )
            idioma_sec = "ptbr" if sec_pt else ("en" if sec_en else "")
    profissao_craft = (
        pt_bruto.get("_profissao_craft")
        or en_bruto.get("_profissao_craft")
        or ""
    )
    profissao_fonte = (
        pt_bruto.get("_profissao_craft_fonte")
        or en_bruto.get("_profissao_craft_fonte")
        or ""
    )

    # Fallback (3): mapa receita/item/spell → profissão da base de conhecimento.
    if not profissao_craft:
        ids_conhecidos: List[Any] = [
            item_id,
            bruto.get("spell_id"),
            bruto.get("recipe_id"),
        ]
        ids_conhecidos.extend(bruto.get("spell_ids") or [])
        ids_conhecidos.extend(bruto.get("recipe_ids") or [])
        profissao_mapeada = profissao_por_receita(*ids_conhecidos)
        if profissao_mapeada:
            profissao_craft = profissao_mapeada
            profissao_fonte = "receita"

    # Fallback (4): categoria da URL, SOMENTE para ferramentas de profissão.
    if not profissao_craft and tipo_item == "ferramenta":
        da_url = (
            pt_bruto.get("_profissao_url")
            or en_bruto.get("_profissao_url")
            or bruto.get("_profissao_url")
            or ""
        )
        if da_url:
            profissao_craft = str(da_url)
            profissao_fonte = "categoria"

    qualidade_craft = 0
    fonte_qualidade_craft = ""
    motivo_qualidade_craft = "ausente"
    for fonte in (url_pt, url_en, bruto.get("url"), bruto.get("_pagina")):
        m = re.search(
            r"crafting-quality=(\d+)", str(fonte or ""), re.IGNORECASE
        )
        if m:
            qualidade_craft = int(m.group(1))
            fonte_qualidade_craft = "url:crafting-quality"
            motivo_qualidade_craft = "url:crafting-quality"
            break
    if not qualidade_craft:
        qc_tooltip, motivo_tooltip = extrair_qualidade_craft_detalhado(texto_total)
        if qc_tooltip:
            qualidade_craft = qc_tooltip
            fonte_qualidade_craft = "tooltip"
            motivo_qualidade_craft = motivo_tooltip or "texto"
    # Só faz sentido para itens realmente craftados
    if not profissao_craft:
        if qualidade_craft or motivo_qualidade_craft != "ausente":
            motivo_qualidade_craft = (
                "ignorado:sem_profissao "
                f"({motivo_qualidade_craft})"
            )
        qualidade_craft = 0
        fonte_qualidade_craft = ""

    # Indício auditável de craft: o que foi observado, mesmo sem profissão.
    indicios: List[str] = []
    if profissao_craft:
        indicios.append(f"profissao:{profissao_fonte or 'desconhecida'}")
    if motivo_qualidade_craft != "ausente":
        indicios.append(f"qualidade_craft:{motivo_qualidade_craft}")
    if _RE_FEITO_POR.search(texto_total):
        indicios.append("texto:feito por")
    if re.search(r"\bR[1-5]\b|\bRank\s*[1-5]\b", texto_total, re.IGNORECASE):
        indicios.append("texto:rank")
    craft_indicio = "; ".join(indicios) or "ausente"

    subtipo = extrair_subtipo(texto_total) or (slot if slot != "N/A" else "")
    missivas_aplicaveis = (
        list(MISSIVAS_TIPOS)
        if tipo_item in ("gear", "embelezamento") and profissao_craft
        else []
    )

    # --- Normalização: nunca `None` em campos obrigatórios -------------------
    nome_ptbr = str(nome_ptbr or "").strip()
    nome_en = str(nome_en or "").strip()
    primarios = dict(primarios or {})
    secundarios = dict(secundarios or {})
    prim_pt = dict(prim_pt or {})
    sec_pt = dict(sec_pt or {})
    prim_en = dict(prim_en or {})
    sec_en = dict(sec_en or {})
    bonus_ids = [str(b) for b in (bonus_ids or []) if str(b or "").strip()]

    efeito_pt = str(pt.get("efeito") or "")
    efeito_en = str(en.get("efeito") or "")

    icone_url = (
        pt.get("icone_url")
        or en.get("icone_url")
        or montar_icone_url(bruto.get("icone_url") or "")
    )
    icone_fonte = (
        pt.get("icone_fonte")
        if pt.get("icone_url")
        else (
            en.get("icone_fonte")
            if en.get("icone_url")
            else _fonte_icone(icone_url, bruto.get("_icone_fonte"))
        )
    )

    # --- Rastreio de fonte dos nomes (sem tradução cruzada) ------------------
    nome_ptbr_fonte = _fonte_declarada(
        (pt_bruto, bruto), ("_nome_ptbr_fonte", "_nome_fonte"), FONTES_NOME
    )
    if not nome_ptbr_fonte:
        nome_ptbr_fonte = "crawl_ptbr" if nome_ptbr else "ausente"
    nome_en_fonte = _fonte_declarada(
        (en_bruto, bruto), ("_nome_en_fonte", "_nome_fonte"), FONTES_NOME
    )
    if not nome_en_fonte:
        nome_en_fonte = "crawl_en" if nome_en else "ausente"

    # --- Rastreio de fonte dos atributos ------------------------------------
    atributos_fonte = _fonte_declarada(
        (pt_bruto, en_bruto, bruto),
        ("_atributos_fonte", "atributos_fonte"),
        FONTES_ATRIBUTOS,
    )
    if not atributos_fonte:
        atributos_fonte = (
            "tooltip_pagina" if (primarios or secundarios) else "ausente"
        )

    item: Dict[str, Any] = {
        "id": item_id,
        "id_completo": montar_id_completo(item_id, bonus_ids, ilvl),
        "nome_en": nome_en,
        "nome_ptbr": nome_ptbr,
        "nome_ptbr_fonte": nome_ptbr_fonte,
        "nome_en_fonte": nome_en_fonte,
        "slot": str(slot or "N/A"),
        "slot_fonte_pt": pt["slot_fonte"],
        "slot_fonte_en": en["slot_fonte"],
        "slot_alvo": extrair_slot_alvo(texto_total),
        "tipo_item": tipo_item,
        "subtipo": subtipo,
        "tipo_armadura": str(tipo or "N/A"),
        "tipo_armadura_fonte_pt": pt["tipo_fonte"],
        "tipo_armadura_fonte_en": en["tipo_fonte"],
        "profissao_craft": str(profissao_craft or ""),
        "profissao_craft_fonte": str(profissao_fonte or ""),
        "craft_indicio": craft_indicio,
        "qualidade_craft": int(qualidade_craft or 0),
        "qualidade_craft_fonte": fonte_qualidade_craft,
        "motivo_qualidade_craft": motivo_qualidade_craft,
        "embelezamento": detectar_embelezamento(texto_total),
        "missiva_atributo": extrair_missiva_atributo(
            nome_ptbr or nome_en, texto_total
        ),
        "missivas_aplicaveis": missivas_aplicaveis,
        "gema_cor": extrair_gema_cor(texto_total),
        "rank": extrair_rank(texto_total),
        "fonte": extrair_fonte(texto_total),
        "vinculo_conteudo": extrair_vinculo_conteudo(texto_total),
        "fonte_consultada": url_final,
        "qualidade": int(qualidade or 0),
        "qualidade_nome": QUALIDADE_POR_ID.get(qualidade, "") if qualidade else "",
        "qualidade_nome_en": (
            QUALIDADE_POR_ID_EN.get(qualidade, "") if qualidade else ""
        ),
        "item_level": int(ilvl or 0),
        "track": referencia["track"],
        "track_stage": referencia["track_stage"],
        "voidforged": bool(referencia["voidforged"]),
        "atributos_primarios": primarios,
        "atributos_fonte": atributos_fonte,
        "atributos_primarios_ptbr": prim_pt,
        "atributos_primarios_en": prim_en,
        "idioma_atributos_primarios": idioma_prim,
        "atributos_secundarios": secundarios,
        "atributos_secundarios_ptbr": sec_pt,
        "atributos_secundarios_en": sec_en,
        "idioma_atributos_secundarios": idioma_sec,
        "efeito_equip_uso": efeito_pt or efeito_en,
        "efeito_equip_uso_ptbr": efeito_pt,
        "efeito_equip_uso_en": efeito_en,
        "icone_url": icone_url,
        "icone_fonte": icone_fonte,
        "bonus_ids": bonus_ids,
        "variante_fonte": str(
            bruto.get("variante_fonte") or bruto.get("_variante_fonte") or ""
        ),
        "url": url_pt or bruto.get("url") or "",
        "url_en": url_en or "",
    }

    # Tooltips derivados precisam ser os últimos campos consolidados.
    item["tooltip_raidbots"] = montar_tooltip_raidbots(item, "ptbr")
    item["tooltip_raidbots_en"] = montar_tooltip_raidbots(item, "en")
    return item


# =============================================================================
# Fallback LLM opcional (P-08)
# =============================================================================
#: Campos cuja ausência justifica o fallback LLM.
CAMPOS_LLM = (
    "nome_ptbr",
    "nome_en",
    "icone_url",
    "atributos_primarios",
    "atributos_secundarios",
)

_PROMPT_LLM = (
    "Extraia apenas os campos pedidos do tooltip do item. Responda SOMENTE "
    "JSON válido, sem markdown, no formato exato: "
    '{"nome_ptbr": "", "nome_en": "", "icone": "", '
    '"atributos_primarios": {}, "atributos_secundarios": {}}. '
    "Não invente valores ausentes: use string vazia ou objeto vazio."
)


def faltando_campos_llm(item: Dict[str, Any]) -> bool:
    """`True` quando falta nome, ícone ou todos os atributos."""
    if not (
        str(item.get("nome_ptbr") or "").strip()
        or str(item.get("nome_en") or "").strip()
    ):
        return True
    if not str(item.get("icone_url") or "").strip():
        return True
    if not (item.get("atributos_primarios") or item.get("atributos_secundarios")):
        return True
    return False


def _dict_int(valor: Any) -> Dict[str, int]:
    """Normaliza um mapa de atributos do LLM para `{nome: int > 0}`."""
    if not isinstance(valor, dict):
        return {}
    saida: Dict[str, int] = {}
    for chave, bruto in valor.items():
        nome = str(chave).strip()
        if not nome:
            continue
        try:
            numero = int(float(str(bruto).replace(",", ".")))
        except (TypeError, ValueError):
            continue
        if numero > 0:
            saida[nome] = numero
    return saida


def _completar_com_crawl4ai(prompt: str, texto: str) -> str:
    """Chamada real opcional via Crawl4AI. Requer `DEEPSEEK_API_KEY`."""
    from config import montar_llm_config

    try:
        from crawl4ai import perform_completion  # type: ignore
    except (ImportError, AttributeError) as exc:
        raise RuntimeError(
            "crawl4ai.perform_completion indisponível nesta versão; "
            "injete `completar` para o fallback LLM."
        ) from exc

    llm = montar_llm_config()
    return str(perform_completion(llm, prompt, [texto]) or "")


def _extrair_com_llm(
    texto: str,
    item: Dict[str, Any],
    completar: Optional[Callable[[str, str], str]] = None,
) -> Dict[str, Any]:
    """Fallback LLM **opcional**, desacoplado e tolerante a falhas.

    `completar(prompt, texto)` deve devolver JSON estrito. Quando `None`, tenta
    `crawl4ai.perform_completion` com `config.montar_llm_config()`. Nunca
    levanta exceção: em falha devolve campos vazios e `_llm_erro`.
    """
    vazio: Dict[str, Any] = {
        "nome_ptbr": "",
        "nome_en": "",
        "icone_url": "",
        "atributos_primarios": {},
        "atributos_secundarios": {},
        "_llm_usado": False,
        "_llm_campos": [],
        "_llm_erro": "",
    }
    if item is None:
        item = {}

    try:
        chamada = completar or _completar_com_crawl4ai
        resposta = chamada(_PROMPT_LLM, texto or "")
        if not resposta:
            return vazio
        dados = json.loads(resposta)
        if not isinstance(dados, dict):
            return vazio
    except Exception as exc:  # noqa: BLE001 - fallback nunca derruba o run
        vazio["_llm_erro"] = str(exc)
        return vazio

    nome_ptbr = str(dados.get("nome_ptbr") or "").strip()
    nome_en = str(dados.get("nome_en") or "").strip()
    icone = str(dados.get("icone") or dados.get("icone_url") or "").strip()
    icone_url = montar_icone_url(icone) if icone else ""
    primarios = _dict_int(dados.get("atributos_primarios"))
    secundarios = _dict_int(dados.get("atributos_secundarios"))

    campos = [
        nome
        for nome, valor in (
            ("nome_ptbr", nome_ptbr),
            ("nome_en", nome_en),
            ("icone_url", icone_url),
            ("atributos_primarios", primarios),
            ("atributos_secundarios", secundarios),
        )
        if valor
    ]
    return {
        "nome_ptbr": nome_ptbr,
        "nome_en": nome_en,
        "icone_url": icone_url,
        "atributos_primarios": primarios,
        "atributos_secundarios": secundarios,
        "_llm_usado": bool(campos),
        "_llm_campos": campos,
        "_llm_erro": "",
    }


def aplicar_llm_em_item(
    item: Dict[str, Any],
    texto: str = "",
    completar: Optional[Callable[[str, str], str]] = None,
) -> Dict[str, Any]:
    """Aplica o fallback LLM só quando faltam campos e sem sobrescrever.

    Grava as fontes `"llm"` nas escalas `FONTES_NOME`, `FONTES_ICONE` e
    `FONTES_ATRIBUTOS`. Nunca levanta exceção.
    """
    if not faltando_campos_llm(item):
        return item

    dados = _extrair_com_llm(
        texto or str(item.get("_contexto") or ""), item, completar
    )
    if not dados.get("_llm_usado"):
        item["_llm_erro"] = dados.get("_llm_erro") or ""
        return item

    if dados["nome_ptbr"] and not item.get("nome_ptbr"):
        item["nome_ptbr"] = dados["nome_ptbr"]
        item["nome_ptbr_fonte"] = "llm"
    if dados["nome_en"] and not item.get("nome_en"):
        item["nome_en"] = dados["nome_en"]
        item["nome_en_fonte"] = "llm"
    if dados["icone_url"] and not item.get("icone_url"):
        item["icone_url"] = dados["icone_url"]
        item["icone_fonte"] = "llm"
    if dados["atributos_primarios"] and not item.get("atributos_primarios"):
        item["atributos_primarios"] = dict(dados["atributos_primarios"])
        item["atributos_fonte"] = "llm"
    if dados["atributos_secundarios"] and not item.get("atributos_secundarios"):
        item["atributos_secundarios"] = dict(dados["atributos_secundarios"])
        item["atributos_fonte"] = "llm"

    item["_llm_usado"] = True
    item["_llm_campos"] = list(dados["_llm_campos"])
    item["_llm_erro"] = ""
    return item
