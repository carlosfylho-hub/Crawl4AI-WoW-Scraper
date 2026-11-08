"""
Configurações do scraper WoWhead Midnight - Todas as 5 partes.
"""

import json
import os
import re
from typing import List, Optional

# ===== API DeepSeek (usada apenas pelos modos com LLM) =====
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")


def validar_chave_deepseek(chave: str) -> bool:
    """Validação de formato: não vazia, >= 20 caracteres e sem espaços."""
    chave = (chave or "").strip()
    return bool(chave) and len(chave) >= 20 and " " not in chave


def configurar_deepseek_api_key(chave: str) -> bool:
    """Persiste a chave no módulo e no ambiente para os scrapers LLM."""
    global DEEPSEEK_API_KEY
    chave = (chave or "").strip()
    if not validar_chave_deepseek(chave):
        return False
    DEEPSEEK_API_KEY = chave
    os.environ["DEEPSEEK_API_KEY"] = chave
    return True


def chave_deepseek_configurada() -> bool:
    return validar_chave_deepseek(os.getenv("DEEPSEEK_API_KEY", ""))


# ===== Provider LLM (litellm) =====
# O litellm exige o provider no formato "<fornecedor>/<modelo>"
# (ex.: "deepseek/deepseek-chat"). Aceitamos a forma curta "deepseek" na
# variável de ambiente e normalizamos para o formato aceito pelo litellm.
_PROVIDER_LLM_PADRAO = "deepseek/deepseek-chat"


def normalizar_provider(valor: str) -> str:
    """Normaliza o provider LLM para a forma aceita pelo litellm.

    - vazio -> ``deepseek/deepseek-chat``;
    - ``deepseek`` -> ``deepseek/deepseek-chat``;
    - ``deepseek/deepseek-chat`` (ou outro ``fornecedor/modelo``) -> mantém.
    """
    valor = (valor or "").strip()
    if not valor:
        return _PROVIDER_LLM_PADRAO
    if "/" in valor:
        return valor
    if valor.lower() == "deepseek":
        return _PROVIDER_LLM_PADRAO
    return valor


#: Provider/modelo usado pelos fluxos com LLM (nunca imprime o token).
LLM_PROVIDER = normalizar_provider(
    os.getenv("LLM_PROVIDER", _PROVIDER_LLM_PADRAO)
)
#: Modelo configurado (útil para logging/telemetria; sem segredos).
LLM_MODEL = os.getenv("LLM_MODEL", LLM_PROVIDER)


def montar_llm_config(api_token=None, **kwargs):
    """Monta um ``LLMConfig`` do Crawl4AI com o provider já normalizado.

    A chave de API vem do parâmetro ou do ``.env`` (``DEEPSEEK_API_KEY``).
    O token NUNCA é impresso por esta função.
    """
    from crawl4ai import LLMConfig  # import tardio: evita custo no import

    token = (api_token or os.getenv("DEEPSEEK_API_KEY", "")).strip()
    if not token:
        raise ValueError(
            "DEEPSEEK_API_KEY não configurada. Defina no .env antes de usar LLM."
        )
    return LLMConfig(provider=LLM_PROVIDER, api_token=token, **kwargs)


# ===== PARTE 1: Ferramentas de Produção (Grupo 1) =====
# Alquimia, Ferraria, Culinária, Encantamento e Engenharia
PARTE1_URLS = [
    "https://www.wowhead.com/pt/guide/midnight/professions/alchemy-overview-trainer-locations-recipes-tools#accessories-tools",
    "https://www.wowhead.com/pt/guide/midnight/professions/blacksmithing-overview-trainer-locations-recipes-tools#accessories-tools",
    "https://www.wowhead.com/pt/guide/midnight/professions/cooking-overview-trainer-leveling-recipes-tools",
    "https://www.wowhead.com/pt/guide/midnight/professions/enchanting-overview-trainer-locations-recipes-tools#accessories-tools",
    "https://www.wowhead.com/pt/guide/midnight/professions/engineering-overview-trainer-locations-recipes-tools#accessories-tools"
]

# ===== PARTE 2: Ferramentas de Coleta e Joalheria (Grupo 2) =====
# Pesca, Herborismo, Escrivania, Joalheria e Couraria
PARTE2_URLS = [
    "https://www.wowhead.com/pt/guide/midnight/professions/fishing-overview-trainer-locations-pools-tools#accessories-tools",
    "https://www.wowhead.com/pt/guide/midnight/professions/herbalism-overview-trainer-locations-treasures-tools#accessories-tools",
    "https://www.wowhead.com/pt/guide/midnight/professions/inscription-overview-trainer-locations-recipes-tools#accessories-tools",
    "https://www.wowhead.com/pt/guide/midnight/professions/jewelcrafting-overview-trainer-locations-recipes-tools#accessories-tools",
    "https://www.wowhead.com/pt/guide/midnight/professions/leatherworking-overview-trainer-locations-recipes-tools#accessories-tools"
]

# ===== PARTE 3: Restante das Profissões (Grupo 3) =====
# Mineração, Esfolamento e Alfaiataria
PARTE3_URLS = [
    "https://www.wowhead.com/pt/guide/midnight/professions/mining-overview-trainer-locations-ores-tools#accessories-tools",
    "https://www.wowhead.com/pt/guide/midnight/professions/skinning-overview-trainer-locations-hides-tracking-tools#accessories-tools",
    "https://www.wowhead.com/pt/guide/midnight/professions/tailoring-overview-trainer-locations-recipes-tools#accessories-tools"
]

# ===== PARTE 4: Encantamentos de Ferramenta =====
# Encantamentos com Rank 2 Max
PARTE4_URLS = [
    "https://www.wowhead.com/pt/item=244025/encantamento-da-engenhosidade-rendorei-ferramenta",
    "https://www.wowhead.com/pt/item=243995/encantamento-de-multicriação-haranir-ferramenta",
    "https://www.wowhead.com/pt/item=244023/encantamento-de-destreza-sindorei-ferramenta",
    "https://www.wowhead.com/pt/item=243993/encantamento-de-finesse-haranir-ferramenta",
    "https://www.wowhead.com/pt/item=243965/encantamento-de-percepção-amani-ferramenta",
    "https://www.wowhead.com/pt/item=243967/encantamento-de-desenvoltura-amani-ferramenta"
]

# ===== PARTE 5: Missivas Talassianas de Profissão =====
PARTE5_URLS = [
    "https://www.wowhead.com/pt/item=245815/missiva-talassiana-da-engenhosidade",
    "https://www.wowhead.com/pt/item=245823/missiva-talassiana-da-finesse",
    "https://www.wowhead.com/pt/item=245817/missiva-talassiana-da-desenvoltura",
    "https://www.wowhead.com/pt/item=245825/missiva-talassiana-da-percepção",
    "https://www.wowhead.com/pt/item=245827/missiva-talassiana-da-destreza",
    "https://www.wowhead.com/pt/item=245819/missiva-talassiana-da-multicriação"
]

# ===== Schemas JSON conforme especificações =====

# Schema para Partes 1, 2 e 3 (Ferramentas de Produção)
FERRAMENTAS_PRODUCAO_SCHEMA = {
    "ferramentas_producao": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id_item_completo": { "type": "string" },
                "nome_ptbr": { "type": "string" },
                "profissao": { "type": "string" },
                "qualidade": { "type": "string" },
                "item_level": { "type": "integer" },
                "rank": { "type": "integer", "const": 5 },
                "atributo_tipo": { "type": "string" },
                "atributo_valor": { "type": "integer" }
            },
            "required": ["id_item_completo", "nome_ptbr", "atributo_tipo"]
        }
    }
}

# Schema para Parte 4 (Encantamentos)
ENCANTAMENTOS_FERRAMENTA_SCHEMA = {
    "encantamentos_ferramenta": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": { "type": "string" },
                "nome_ptbr": { "type": "string" },
                "rank": { "type": "integer", "const": 2 },
                "atributo_tipo": { "type": "string" },
                "atributo_valor": { "type": "integer" }
            },
            "required": ["id", "nome_ptbr", "atributo_tipo"]
        }
    }
}

# Schema para Parte 5 (Missivas)
MISSIVAS_PROFISSOES_SCHEMA = {
    "missivas_profissoes": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": { "type": "string" },
                "nome_ptbr": { "type": "string" },
                "atributo_vinculado": { "type": "string" },
                "valor_atributo": { "type": "string" }
            },
            "required": ["id", "nome_ptbr", "atributo_vinculado"]
        }
    }
}

# =============================================================================
# SEASON 2 (MIDNIGHT) - Faixas de Item Level e filtros
# =============================================================================
try:
    from wow_season2 import (
        ILVL_ABSOLUTO_MIN,
        ILVL_ABSOLUTO_MAX,
        ILVL_PISO_PADRAO,
        ILVL_TETO_PADRAO,
        ILVL_HERO_MIN,
        ILVL_HERO_MAX,
        ILVL_HERO_VOIDFORGE,
        ILVL_MYTH_MIN,
        ILVL_MYTH_MAX,
        ILVL_MYTH_VOIDFORGE,
        ILVL_VERY_RARE_MAX,
        VOIDFORGE_BONUS,
        QUALIDADE_MINIMA_PADRAO,
    )
except ImportError:  # fallback mínimo para ambientes sem wow_season2.py
    ILVL_ABSOLUTO_MIN = 200
    ILVL_ABSOLUTO_MAX = 350
    ILVL_PISO_PADRAO = 305
    ILVL_TETO_PADRAO = 350
    ILVL_HERO_MIN = 305
    ILVL_HERO_MAX = 321
    ILVL_HERO_VOIDFORGE = 328
    ILVL_MYTH_MIN = 318
    ILVL_MYTH_MAX = 334
    ILVL_MYTH_VOIDFORGE = 341
    ILVL_VERY_RARE_MAX = 344
    VOIDFORGE_BONUS = 7
    QUALIDADE_MINIMA_PADRAO = 3

#: Raridade mínima padrão para **gear de combate** (4 = Épico).
#:
#: Separada de `QUALIDADE_MINIMA_PADRAO` (3), que continua valendo para o
#: fluxo legado de catálogo/profissão — assim gemas/encantamentos de qualidade
#: baixa não são descartados por engano.
QUALIDADE_MINIMA_GEAR_PADRAO = 4

#: Bonus IDs de track da Season 2 (Herói 6/6, Mítico 6/6, Mítico de raide e
#: o marcador `13440` de peitoral/berloque).
#:
#: Fonte: [`base_conhecimento_ai_studio/bonus_ids_s2.md`](base_conhecimento_ai_studio/bonus_ids_s2.md:1)
#: (seção 2 — série `128xx`; `13440` na seção 4).
#:
#: Uso: APENAS como **preferência de seleção de variante** (F-01). O item
#: level continua vindo do tooltip/página — nunca é derivado do bônus.
TRACKS_SEASON2 = (12846, 12854, 12856, 13440)

#: Query de filtro da Season 2 para listagens de gear (track + raridade Épica).
#:
#: F-01/P-01b (2026-11-06): mantida apenas como **fallback de listagem**. O
#: Wowhead aplica `ilvl`/`bonus` **client-side**, então esta URL não garante o
#: conjunto da temporada no crawl headless (medido: 192 linhas de 50 itens
#: antigos, todas com `item_level=0`). A fonte primária passou a ser
#: `SEASON2_GEAR_IDS` (ver `urls_gear_canonicas`).
GEAR_QUERY_SEASON2 = "bonus=12846:12854:12856:13440&quality=4"

#: Bônus canônico usado nas URLs de item da temporada.
#:
#: Medido em 2026-11-06 via tooltip: `12856` → ilvl 341; `12854` → 334;
#: `12846` → 321. O marcador `13440` **não** é track e corrompe o ilvl
#: (retornou 28..219), por isso nunca entra na URL de item.
SEASON2_GEAR_BONUS = "12856"

#: Artefato com os IDs curados de gear da Season 2.
#: Gerado por [`tools/gerar_ids_gear_s2.py`](tools/gerar_ids_gear_s2.py:1) a
#: partir de `base_conhecimento_ai_studio/mplus_loot_database.md`.
CAMINHO_IDS_GEAR_S2 = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "season2_gear_ids.json"
)


def _carregar_ids(caminho: str) -> List[str]:
    """Lê uma lista de IDs de um JSON (`{"ids": [...]}` ou lista pura)."""
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (OSError, ValueError):
        return []

    if isinstance(dados, dict):
        dados = dados.get("ids") or []
    if not isinstance(dados, list):
        return []

    vistos = set()
    ids: List[str] = []
    for valor in dados:
        ident = str(valor).strip()
        if ident.isdigit() and ident not in vistos:
            vistos.add(ident)
            ids.append(ident)
    return ids


def _carregar_ids_gear_s2(caminho: str = CAMINHO_IDS_GEAR_S2) -> List[str]:
    """Lê os IDs canônicos de gear (lista vazia se o artefato não existir)."""
    return _carregar_ids(caminho)


#: Artefato com os IDs de **itens craftados** da temporada (P-13).
#: Gerado por [`tools/gerar_ids_craft_s2.py`](tools/gerar_ids_craft_s2.py:1).
CAMINHO_IDS_CRAFT_S2 = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "season2_craft_ids.json"
)


def _carregar_ids_craft_s2(caminho: str = CAMINHO_IDS_CRAFT_S2) -> List[str]:
    """Lê os IDs de itens craftados (lista vazia se o artefato não existir)."""
    return _carregar_ids(caminho)


SEASON2_GEAR_IDS = _carregar_ids_gear_s2()
SEASON2_CRAFT_IDS = _carregar_ids_craft_s2()


def _fatiar_ids(ids: List[str], limite: Optional[int]) -> List[str]:
    """Aplica `limite` à lista de IDs (None = tudo)."""
    if limite is None:
        return ids
    try:
        return ids[: max(0, int(limite))]
    except (TypeError, ValueError):
        return ids


def _urls_itens(ids: List[str], bonus: str) -> List[str]:
    sufixo = f"?bonus={bonus}" if bonus else ""
    return [f"https://www.wowhead.com/pt/item={ident}{sufixo}" for ident in ids]


def urls_gear_canonicas(
    limite: Optional[int] = None, bonus: str = SEASON2_GEAR_BONUS
) -> List[str]:
    """URLs de item dos IDs canônicos da temporada (sem listagem genérica).

    `limite` evita coletar centenas de páginas quando o usuário pediu poucos
    itens (`--max-itens`).
    """
    return _urls_itens(_fatiar_ids(SEASON2_GEAR_IDS, limite), bonus)


def urls_craft_canonicas(
    limite: Optional[int] = None, bonus: str = SEASON2_GEAR_BONUS
) -> List[str]:
    """URLs de item dos IDs **craftados** da temporada (P-13).

    É a fonte correta quando `exigir_craft` está ligado: drops de M+/raid não
    entram, pois não têm qualidade de craft.
    """
    return _urls_itens(_fatiar_ids(SEASON2_CRAFT_IDS, limite), bonus)


# Fontes de listagem (fallback).
# --- anterior (mantida para referência) ---
# "https://www.wowhead.com/pt/items/min-ilvl:305/max-ilvl:350",
SEASON2_ITEM_URLS = [
    f"https://www.wowhead.com/pt/items?{GEAR_QUERY_SEASON2}"
    "&min-ilvl=305&max-ilvl=350",
]

# Profissões disponíveis (filtro da UI e da pipeline)
PROFISSOES_DISPONIVEIS = [
    "Alquimia",
    "Ferraria",
    "Encantamento",
    "Engenharia",
    "Couraria",
    "Alfaiataria",
    "Joalheria",
    "Escrivania",
    "Mineração",
    "Herborismo",
    "Esfolamento",
    "Culinária",
    "Pesca",
]

# Slots de foco (filtro por tipo de item)
SLOTS_FOCO = {
    "Todos": [],
    "Armas (Voidforge 341)": [
        "Arma de 1 Mão",
        "Arma de 2 Mãos",
        "Escudo",
        "Mão Secundária",
    ],
    "Berloques & Colar (341)": ["Berloque", "Colar"],
    "Armaduras (334)": [
        "Cabeça",
        "Ombros",
        "Costas",
        "Peito",
        "Pulso",
        "Mãos",
        "Cintura",
        "Pernas",
        "Pés",
        "Anel",
    ],
}

# =============================================================================
# CATEGORIAS DE EXTRAÇÃO (substitui as "Partes 1..5" engessadas da UI)
# =============================================================================
# `urls` = URLs fixas; `urls_template` = templates que recebem {min}/{max}.
CATEGORIAS_WOW = {
    # Foco principal: GEAR de combate (armaduras + armas)
    "gear_season2": {
        "nome": "Gear de Combate (Season 2)",
        "descricao": "Armaduras, armas, berloques, colares e anéis (Hero/Myth).",
        "urls": [],
        # P-01b: mesma query da CLI (`GEAR_QUERY_SEASON2`) para que a UI não
        # caia na listagem genérica do banco de itens.
        "urls_template": [
            "https://www.wowhead.com/pt/items/armor"
            f"?{GEAR_QUERY_SEASON2}&min-ilvl={{min}}&max-ilvl={{max}}",
            "https://www.wowhead.com/pt/items/weapons"
            f"?{GEAR_QUERY_SEASON2}&min-ilvl={{min}}&max-ilvl={{max}}",
        ],
        "url_filtro": "&min-ilvl=305&max-ilvl=344",
        "subtipos": ["Armaduras", "Armas", "Berloques", "Colares", "Anéis"],
    },
    "ferramentas_profissao": {
        "nome": "Equipamentos de Profissão",
        "descricao": "Ferramentas e acessórios de produção/coleta por profissão.",
        "urls": PARTE1_URLS + PARTE2_URLS + PARTE3_URLS,
        "url_filtro": "&class=16",
        "subtipos": ["Ferramentas", "Acessórios"],
    },
    "aprimoramentos": {
        "nome": "Aprimoramentos e Consumíveis",
        "descricao": "Encantamentos, gemas/joias, missivas e embelezamentos.",
        "urls": PARTE4_URLS + PARTE5_URLS,
        "url_filtro": "&class=7&subclass=16",
        "subtipos": ["Encantamentos", "Gemas", "Missivas", "Embelezamentos"],
    },
    "missivas": {
        "nome": "Missivas (tipos)",
        "descricao": "Missivas de atributo de profissão (Engenhosidade, Finesse, ...).",
        "urls": PARTE5_URLS,
        "url_filtro": "",
        "subtipos": [
            "Engenhosidade",
            "Finesse",
            "Desenvoltura",
            "Percepção",
            "Destreza",
            "Multicriação",
        ],
    },
    "encantamentos": {
        "nome": "Encantamentos",
        "descricao": "Encantamentos de arma, armadura e ferramenta.",
        # URLs de itens específicos (a rota /items/enchants retornou catálogo
        # genérico no Wowhead pt-BR e é tratada como indisponível).
        "urls": PARTE4_URLS,
        "url_filtro": "",
        "subtipos": ["Armas", "Armaduras", "Ferramentas"],
    },
    "gemas": {
        "nome": "Gemas",
        "descricao": "Gemas por cor e atributo.",
        "urls": [],
        "urls_template": [
            "https://www.wowhead.com/pt/items/gems",
        ],
        "url_filtro": "",
        "subtipos": [
            "Vermelha",
            "Azul",
            "Amarela",
            "Roxa",
            "Verde",
            "Laranja",
            "Meta",
        ],
    },
    "consumiveis": {
        "nome": "Consumíveis",
        "descricao": "Consumíveis e itens de uso da temporada.",
        "urls": [],
        "urls_template": [
            "https://www.wowhead.com/pt/items/consumables",
        ],
        "url_filtro": "",
        "subtipos": ["Consumíveis"],
    },
    "reagentes": {
        "nome": "Reagentes e Matérias-Primas",
        "descricao": "Minérios, ervas, couros, tecidos e demais reagentes.",
        "urls": [],
        "urls_template": [
            "https://www.wowhead.com/pt/items/trade-goods/min-ilvl:{min}/max-ilvl:{max}",
        ],
        "url_filtro": "&class=7",
        "subtipos": ["Minérios", "Ervas", "Couros", "Tecidos"],
    },
}


def normalizar_url_gear(url: str) -> list:
    """
    Corrige filtros antigos de item level e expande a lista genérica.

    Wowhead usa `min-ilvl`/`max-ilvl` para item level; `min-level`/`max-level`
    filtram nível de personagem. URLs genéricas `/items/min-ilvl:...` são
    expandidas para `/items/armor` + `/items/weapons`.
    """
    url = (url or "").strip()
    if not url or "/items/" not in url:
        return [url] if url else []

    url = url.replace("min-level:", "min-ilvl:").replace(
        "max-level:", "max-ilvl:"
    )

    if "/armor" in url or "/weapons" in url:
        return [url]

    m = re.search(
        r"/items/min-ilvl:(\d+)/max-ilvl:(\d+)", url
    )
    if m:
        base = "https://www.wowhead.com/pt/items"
        return [
            f"{base}/armor/min-ilvl:{m.group(1)}/max-ilvl:{m.group(2)}",
            f"{base}/weapons/min-ilvl:{m.group(1)}/max-ilvl:{m.group(2)}",
        ]
    return [url]


def _aplicar_url_filtro(url: str, filtro: str) -> str:
    """
    Acrescenta os parâmetros de `url_filtro` de forma idempotente.

    Parâmetros já presentes na URL (na query ou como `chave:valor` no path)
    não são duplicados. O fragmento `#...` é preservado no final.
    """
    filtro = (filtro or "").strip().lstrip("&")
    if not url or not filtro:
        return url

    base, marcador, fragmento = url.partition("#")
    adicionais = []
    for parte in filtro.split("&"):
        if not parte or "=" not in parte:
            continue
        chave = parte.split("=", 1)[0]
        if f"{chave}=" in base or f"{chave}:" in base:
            continue
        adicionais.append(parte)
    if not adicionais:
        return url

    separador = "&" if "?" in base else "?"
    novo = base + separador + "&".join(adicionais)
    return novo + (marcador + fragmento if marcador else "")


def resolver_urls_categoria(
    chave: str,
    ilvl_min: int = ILVL_PISO_PADRAO,
    ilvl_max: int = ILVL_TETO_PADRAO,
    limite: Optional[int] = None,
    somente_craft: bool = False,
) -> list:
    """Resolve as URLs de uma categoria, expandindo templates e url_filtro.

    `gear_season2` usa a lista canônica de IDs da temporada (F-01) — a
    listagem genérica não filtra `ilvl`/`bonus` server-side. Com
    `somente_craft=True`, usa a lista de **itens craftados** (P-13). `limite`
    corta a lista antes do crawl (o pipeline trunca por `max_itens` depois de
    coletar).
    """
    categoria = CATEGORIAS_WOW.get(chave) or {}

    if chave == "gear_season2" and somente_craft and SEASON2_CRAFT_IDS:
        return urls_craft_canonicas(limite)

    if chave == "gear_season2" and SEASON2_GEAR_IDS:
        return urls_gear_canonicas(limite)

    filtro = categoria.get("url_filtro") or ""
    urls = list(categoria.get("urls") or [])
    for template in categoria.get("urls_template") or []:
        try:
            urls.append(template.format(min=ilvl_min, max=ilvl_max))
        except (KeyError, ValueError):
            urls.append(template)
    if limite is not None:
        try:
            urls = urls[: max(0, int(limite))]
        except (TypeError, ValueError):
            pass
    return [_aplicar_url_filtro(url, filtro) for url in urls]


def montar_categorias_selecionadas(
    categorias: list,
    ilvl_min: int = ILVL_PISO_PADRAO,
    ilvl_max: int = ILVL_TETO_PADRAO,
    limite: Optional[int] = None,
    somente_craft: bool = False,
) -> dict:
    """Monta o dicionário {nome_categoria: [urls]} usado pela pipeline."""
    selecionadas = {}
    for chave in categorias or []:
        categoria = CATEGORIAS_WOW.get(chave)
        if not categoria:
            continue
        urls = resolver_urls_categoria(
            chave, ilvl_min, ilvl_max, limite, somente_craft
        )
        if urls:
            selecionadas[categoria["nome"]] = urls
    return selecionadas


# ===== Compatibilidade com código existente =====
# URLs para ferramentas de profissão (todas as partes combinadas)
PROFESSION_TOOLS_URLS = PARTE1_URLS + PARTE2_URLS + PARTE3_URLS

# URLs para encantamentos (PARTE 4)
ENCHANTMENT_URLS = PARTE4_URLS

# URLs para missivas (PARTE 5)
MISSIVE_URLS = PARTE5_URLS

# Schemas para compatibilidade
PROFESSION_TOOLS_SCHEMA = FERRAMENTAS_PRODUCAO_SCHEMA
ENCHANTMENT_SCHEMA = ENCANTAMENTOS_FERRAMENTA_SCHEMA
MISSIVE_SCHEMA = MISSIVAS_PROFISSOES_SCHEMA
