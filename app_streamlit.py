#!/usr/bin/env python3
"""
Aplicativo Streamlit do Scraper Wowhead Season 2 (Midnight).

- Extração completa de itens (texto, atributos estruturados e ícones/mídias).
- Faixa de item level da Season 2: Herói 305-321/328, Mito 318-334/341,
  Very Rare até 344 (piso/teto configuráveis entre 200 e 350).
- Filtros modulares por categoria, profissão e slot (sem "Partes 1..5").
- Tabela/cards com miniatura do ícone, badges Hero/Mito/Voidforge.
- Exportação em CSV, JSON e Markdown.
"""

import asyncio
import html
import json
import os
import queue
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pandas as pd
import streamlit as st

from markdown_season2 import (
    TIPOS_LABEL,
    gerar_markdown as gerar_markdown_season2,
)
from recomendacoes import (
    ATRIBUTOS_PRIORIDADE,
    CLASSES_ESPECIALIDADES,
    gerar_recomendacoes,
    primario_da_especialidade,
)
from runtime import configurar_event_loop_windows

try:
    from config import (
        CATEGORIAS_WOW,
        PROFISSOES_DISPONIVEIS,
        SLOTS_FOCO,
        montar_categorias_selecionadas,
        normalizar_url_gear,
        resolver_urls_categoria,
    )
    from tooltip_raidbots import montar_tooltip_raidbots
    from wow_season2 import (
        ILVL_ABSOLUTO_MAX,
        ILVL_ABSOLUTO_MIN,
        ILVL_PISO_PADRAO,
        ILVL_TETO_PADRAO,
        badges_trilha,
    )
except Exception as exc:  # pragma: no cover
    st.error(f"Falha ao carregar configurações locais: {exc}")
    st.stop()

# -----------------------------------------------------------------------------
# Configuração da página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="WoWhead Season 2 Scraper",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

VERSAO_APP = "2.2.0"
ARQUIVO_SEASON2 = Path("data") / "wowhead_itens_season2.json"
ARQUIVO_MD = Path("data") / "wowhead_season2.md"

CORES_BADGE = {
    "Herói": "#b45309",
    "Mito": "#6d28d9",
    "Voidforge": "#0369a1",
    "Muito Raro": "#a16207",
    "Acima da faixa": "#b91c1c",
    "Base": "#4b5563",
}

MAPEAMENTO_PARTES = {
    1: "parte1_ferramentas_producao",
    2: "parte2_ferramentas_coleta",
    3: "parte3_ferramentas_restante",
    4: "parte4_encantamentos",
    5: "parte5_missivas",
}

# Partes legadas derivadas das categorias modulares
PARTES_POR_CATEGORIA = {
    "ferramentas_profissao": [1, 2, 3],
    "aprimoramentos": [4, 5],
}


# =============================================================================
# Helpers de apresentação
# =============================================================================

def badges_html(item: Dict[str, Any]) -> str:
    """Badges HTML coloridos para Hero (305-328), Myth (318-344) e Voidforge."""
    badges = badges_trilha(
        item.get("item_level") or 0,
        item.get("track") or "",
        bool(item.get("voidforged")),
    )
    partes = []
    for badge in badges:
        cor = CORES_BADGE.get(badge, "#4b5563")
        partes.append(
            f"<span style='background:{cor};color:#fff;padding:2px 8px;"
            f"border-radius:10px;font-size:0.72rem;margin-right:4px;"
            f"white-space:nowrap;'>{html.escape(badge)}</span>"
        )
    return " ".join(partes)


def _join_atributos(atributos: Optional[Dict[str, Any]]) -> str:
    if not atributos:
        return ""
    return ", ".join(f"{k} {v}" for k, v in atributos.items())


def _resumo_missiva(item: Dict[str, Any]) -> str:
    partes = []
    if item.get("tipo_item") == "missiva" and item.get("missiva_atributo"):
        partes.append(f"Missiva: {item['missiva_atributo']}")
    if item.get("embelezamento"):
        partes.append("Embelezamento")
    if item.get("missivas_aplicaveis"):
        partes.append("Missivas: " + ", ".join(item["missivas_aplicaveis"]))
    return " · ".join(partes)


def itens_para_df(itens: List[Dict[str, Any]]) -> pd.DataFrame:
    linhas = []
    for item in itens:
        linhas.append(
            {
                "Ícone": item.get("icone_url") or None,
                "Badges": " ".join(
                    badges_trilha(
                        item.get("item_level") or 0,
                        item.get("track") or "",
                        bool(item.get("voidforged")),
                    )
                ),
                "Nome (PT-BR)": item.get("nome_ptbr") or "",
                "Nome (EN)": item.get("nome_en") or "",
                "Tipo": TIPOS_LABEL.get(item.get("tipo_item") or "outro", "Outro"),
                "Slot": item.get("slot") or "N/A",
                "Subtipo": item.get("subtipo") or "",
                "Armadura": item.get("tipo_armadura") or "N/A",
                "Prof. Craft": item.get("profissao_craft") or "",
                "Slot-Alvo": item.get("slot_alvo") or "",
                "Missiva/Emb.": _resumo_missiva(item),
                "Rank/Cor": " · ".join(
                    parte
                    for parte in (
                        f"Rank {item['rank']}" if item.get("rank") else "",
                        f"Gema {item['gema_cor']}" if item.get("gema_cor") else "",
                    )
                    if parte
                ),
                "Fonte/Vínculo": " / ".join(
                    parte
                    for parte in (
                        item.get("fonte") or "",
                        item.get("vinculo_conteudo") or "",
                    )
                    if parte
                ),
                "Qualidade": item.get("qualidade_nome")
                or item.get("qualidade")
                or "",
                "Craft (R)": (
                    f"R{int(item['qualidade_craft'])}"
                    if item.get("qualidade_craft")
                    else ""
                ),
                "ilvl": int(item.get("item_level") or 0),
                "Track": item.get("track") or "",
                "Stage": item.get("track_stage") or "",
                "Voidforge": "Sim" if item.get("voidforged") else "Não",
                "Primários": _join_atributos(item.get("atributos_primarios")),
                "Secundários": _join_atributos(item.get("atributos_secundarios")),
                "Efeito": item.get("efeito_equip_uso") or "",
                "Bonus IDs": ":".join(str(b) for b in (item.get("bonus_ids") or [])),
                "Profissão": item.get("profissao") or "",
                "ID": item.get("id"),
                "URL": item.get("url") or None,
            }
        )
    return pd.DataFrame(linhas)


def renderizar_cards(itens: List[Dict[str, Any]]) -> None:
    for item in itens:
        with st.container(border=True):
            col_icone, col_info, col_badges = st.columns([1, 6, 3])
            with col_icone:
                icone = item.get("icone_url")
                if icone:
                    st.markdown(
                        f"<img src='{html.escape(icone)}' width='52' "
                        "style='border-radius:10px;'/>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown("### 🧩")
            with col_info:
                nome = html.escape(item.get("nome_ptbr") or "Sem nome")
                st.markdown(
                    f"**{nome}** — ilvl `{int(item.get('item_level') or 0)}`",
                    unsafe_allow_html=True,
                )
                if item.get("nome_en"):
                    st.caption(f"EN: {html.escape(item['nome_en'])}")
                detalhes = [
                    item.get("slot") or "N/A",
                    item.get("tipo_armadura") or "N/A",
                    item.get("qualidade_nome") or "",
                    (
                        f"Craft R{int(item['qualidade_craft'])}"
                        if item.get("qualidade_craft")
                        else ""
                    ),
                    item.get("profissao") or "",
                ]
                st.caption(" • ".join(d for d in detalhes if d))
                prim = _join_atributos(item.get("atributos_primarios"))
                sec = _join_atributos(item.get("atributos_secundarios"))
                if prim or sec:
                    st.caption(f"Primários: {prim or '—'} | Secundários: {sec or '—'}")
                if item.get("efeito_equip_uso"):
                    st.caption(f"_{item['efeito_equip_uso'][:240]}_")
            with col_badges:
                st.markdown(badges_html(item), unsafe_allow_html=True)
                if item.get("url"):
                    st.markdown(f"[Abrir no Wowhead]({item['url']})")


def renderizar_itens(itens: List[Dict[str, Any]], key_prefix: str = "res") -> None:
    if not itens:
        st.info("Nenhum item para exibir com os filtros atuais.")
        return

    modo_exibicao = st.radio(
        "Visualização",
        ["Tabela", "Cards"],
        horizontal=True,
        key=f"{key_prefix}_view",
    )

    if modo_exibicao == "Tabela":
        df = itens_para_df(itens)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ícone": st.column_config.ImageColumn("Ícone", width="small"),
                "ilvl": st.column_config.NumberColumn("ilvl", format="%d"),
                "URL": st.column_config.LinkColumn(
                    "URL", display_text="Abrir", width="small"
                ),
                "Efeito": st.column_config.TextColumn("Efeito", width="large"),
            },
        )
    else:
        opcoes = [25, 50, 100, "Todos"]
        limite = st.selectbox("Itens exibidos", opcoes, index=0, key=f"{key_prefix}_lim")
        if limite == "Todos" or limite is None:
            recorte = itens
        else:
            recorte = itens[: int(limite)]
        renderizar_cards(recorte)


# =============================================================================
# Exportações
# =============================================================================

def gerar_csv(itens: List[Dict[str, Any]]) -> str:
    linhas = []
    for item in itens:
        linha = {
            "id": item.get("id"),
            "id_completo": item.get("id_completo"),
            "nome_ptbr": item.get("nome_ptbr"),
            "nome_en": item.get("nome_en"),
            "slot": item.get("slot"),
            "slot_fonte_pt": item.get("slot_fonte_pt"),
            "slot_fonte_en": item.get("slot_fonte_en"),
            "tipo_armadura": item.get("tipo_armadura"),
            "qualidade": item.get("qualidade"),
            "qualidade_nome": item.get("qualidade_nome"),
            "qualidade_nome_en": item.get("qualidade_nome_en"),
            "qualidade_craft": item.get("qualidade_craft"),
            "qualidade_craft_fonte": item.get("qualidade_craft_fonte"),
            "motivo_qualidade_craft": item.get("motivo_qualidade_craft"),
            "profissao_craft": item.get("profissao_craft"),
            "profissao_craft_fonte": item.get("profissao_craft_fonte"),
            "craft_indicio": item.get("craft_indicio"),
            "item_level": item.get("item_level"),
            "track": item.get("track"),
            "track_stage": item.get("track_stage"),
            "voidforged": item.get("voidforged"),
            "atributos_primarios": _join_atributos(item.get("atributos_primarios")),
            "atributos_primarios_en": _join_atributos(
                item.get("atributos_primarios_en")
            ),
            "atributos_secundarios": _join_atributos(
                item.get("atributos_secundarios")
            ),
            "atributos_secundarios_en": _join_atributos(
                item.get("atributos_secundarios_en")
            ),
            "idioma_atributos_primarios": item.get("idioma_atributos_primarios"),
            "idioma_atributos_secundarios": item.get("idioma_atributos_secundarios"),
            "efeito_equip_uso": item.get("efeito_equip_uso"),
            "efeito_equip_uso_en": item.get("efeito_equip_uso_en"),
            "icone_url": item.get("icone_url"),
            "icone_fonte": item.get("icone_fonte"),
            "nome_ptbr_fonte": item.get("nome_ptbr_fonte"),
            "nome_en_fonte": item.get("nome_en_fonte"),
            "atributos_fonte": item.get("atributos_fonte"),
            "tooltip_raidbots": item.get("tooltip_raidbots")
            or montar_tooltip_raidbots(item, "ptbr"),
            "tooltip_raidbots_en": item.get("tooltip_raidbots_en")
            or montar_tooltip_raidbots(item, "en"),
            "bonus_ids": ":".join(str(b) for b in (item.get("bonus_ids") or [])),
            "profissao": item.get("profissao"),
            "categoria": item.get("categoria"),
            "url": item.get("url"),
            "url_en": item.get("url_en"),
        }
        linhas.append(linha)
    return pd.DataFrame(linhas).to_csv(index=False)


def _escape_md(texto: Any) -> str:
    return str(texto or "").replace("|", "\\|").replace("\n", " ")


def gerar_markdown(
    itens: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Wrapper do gerador bilíngue de Markdown (markdown_season2.py)."""
    return gerar_markdown_season2(itens, metadata=metadata)


def gerar_markdown_legado(resultados: Dict[str, Any]) -> str:
    md = ["# Banco de Dados WoWhead Midnight (legado)", ""]
    if isinstance(resultados, dict):
        for chave, itens in resultados.items():
            if chave == "metadata" or not isinstance(itens, list) or not itens:
                continue
            md.append(f"## {chave}")
            md.append("")
            md.append(
                "| Nome | Profissão | Qualidade | Item Level | Atributo | Valor |"
            )
            md.append("|---|---|---|---|---|---|")
            for item in itens:
                md.append(
                    "| {nome} | {prof} | {qual} | {ilvl} | {atrib} | {valor} |".format(
                        nome=_escape_md(item.get("nome_ptbr")),
                        prof=_escape_md(item.get("profissao")),
                        qual=_escape_md(item.get("qualidade")),
                        ilvl=int(item.get("item_level") or 0),
                        atrib=_escape_md(
                            item.get("atributo_tipo")
                            or item.get("atributo_vinculado")
                            or ""
                        ),
                        valor=_escape_md(
                            item.get("atributo_valor")
                            or item.get("valor_atributo")
                            or ""
                        ),
                    )
                )
            md.append("")
    return "\n".join(md)


# =============================================================================
# Dados / filtros
# =============================================================================

def carregar_season2() -> Dict[str, Any]:
    if not ARQUIVO_SEASON2.exists():
        return {"metadata": {}, "itens": []}
    try:
        with open(ARQUIVO_SEASON2, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if isinstance(dados, list):
            return {"metadata": {}, "itens": dados}
        return dados
    except Exception:
        return {"metadata": {}, "itens": []}


def carregar_catalogo() -> List[Dict[str, Any]]:
    caminho = Path("data") / "wowhead_catalogo.json"
    if not caminho.exists():
        return []
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return dados.get("itens") or []
    except Exception:
        return []


def contar_por(items: List[Dict[str, Any]], campo: str) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=[campo, "Quantidade"])
    serie = pd.Series([str(i.get(campo) or "N/A") for i in items])
    contagem = serie.value_counts().reset_index()
    contagem.columns = [campo, "Quantidade"]
    return contagem


def filtrar_itens(itens: List[Dict[str, Any]], filtro: Dict[str, Any]) -> List[Dict[str, Any]]:
    saida = []
    busca = (filtro.get("busca") or "").strip().lower()
    tracks = filtro.get("tracks") or []
    for item in itens:
        ilvl = int(item.get("item_level") or 0)
        if ilvl:
            if ilvl < filtro["ilvl_min"] or ilvl > filtro["ilvl_max"]:
                continue
        if busca:
            alvo = " ".join(
                str(item.get(campo) or "")
                for campo in (
                    "nome_ptbr",
                    "nome_en",
                    "slot",
                    "profissao",
                    "tipo_armadura",
                )
            ).lower()
            if busca not in alvo:
                continue
        if tracks and (item.get("track") or "Base") not in tracks:
            continue
        if filtro.get("voidforged") and not item.get("voidforged"):
            continue
        if filtro.get("com_icone") and not item.get("icone_url"):
            continue
        if filtro.get("tipos") and (
            item.get("tipo_item") or "outro"
        ) not in filtro["tipos"]:
            continue
        if filtro.get("armaduras") and (
            item.get("tipo_armadura") or "N/A"
        ) not in filtro["armaduras"]:
            continue
        if filtro.get("profissoes_craft") and (
            item.get("profissao_craft") or ""
        ) not in filtro["profissoes_craft"]:
            continue
        if filtro.get("somente_embelezamento") and not item.get("embelezamento"):
            continue
        if filtro.get("somente_missiva") and item.get("tipo_item") != "missiva":
            continue
        saida.append(item)
    return saida


# =============================================================================
# Executores (assíncronos)
# =============================================================================

async def executar_season2(
    categorias_urls: Dict[str, List[str]],
    cfg: Dict[str, Any],
    progress_callback: Callable,
) -> Dict[str, Any]:
    from scraper_season2 import WowheadSeason2Scraper, profissao_de_url

    categorias_urls = dict(categorias_urls)

    # Filtro de profissão aplicado apenas às URLs de ferramentas de profissão
    profs = set(cfg.get("profissoes") or [])
    nome_ferramentas = CATEGORIAS_WOW["ferramentas_profissao"]["nome"]
    if profs and nome_ferramentas in categorias_urls:
        filtradas = [
            url
            for url in categorias_urls[nome_ferramentas]
            if profissao_de_url(url) in profs
        ]
        if filtradas:
            categorias_urls[nome_ferramentas] = filtradas
        else:
            categorias_urls.pop(nome_ferramentas, None)

    if not categorias_urls:
        raise ValueError(
            "Nenhuma URL corresponde às categorias/profissões selecionadas."
        )

    async with WowheadSeason2Scraper(
        ilvl_min=cfg["ilvl_min"],
        ilvl_max=cfg["ilvl_max"],
        qualidade_min=cfg["qualidade_min"],
        qualidade_craft_min=cfg.get("qualidade_craft_min", 5),
        exigir_craft=cfg.get("exigir_craft", True),
        buscar_detalhes=cfg["buscar_detalhes"],
        buscar_ingles=cfg.get("buscar_ingles", True),
        gerar_markdown=True,
        caminho_md=str(ARQUIVO_MD),
        max_itens=cfg["max_itens"],
        max_detalhes=cfg["max_detalhes"],
        slots_permitidos=cfg.get("slots_permitidos") or [],
        wait_for=cfg.get("wait_for") or "css:a[href*='item=']",
        headless=cfg.get("headless", True),
        magic_mode=cfg.get("magic_mode", True),
        js_lazy_load=cfg.get("js_lazy_load", True),
        progress_callback=progress_callback,
    ) as scraper:
        resultado = await scraper.executar_por_categorias(categorias_urls)
        scraper.salvar_resultados(resultado, str(ARQUIVO_SEASON2), str(ARQUIVO_MD))
    return resultado


async def executar_legado(
    partes: List[int],
    cfg: Dict[str, Any],
    progress_callback: Callable,
) -> Dict[str, Any]:
    """Executa o fluxo "Sem LLM" (parsers canônicos) por partes legadas.

    O modo "Com LLM (legado)" foi removido da UI: ele dependia do scraper LLM
    antigo, agora isolado em ``legacy/``. O fluxo "Sem LLM" continua ativo
    porque usa ``scraper_sem_llm`` + ``wow_season2``.
    """
    os.environ["CRAWL4AI_BROWSER_HEADLESS"] = str(cfg.get("headless", True)).lower()
    os.environ["CRAWL4AI_MAGIC_MODE"] = str(cfg.get("magic_mode", True)).lower()
    os.environ["ILVL_MIN"] = str(cfg["ilvl_min"])
    os.environ["ILVL_MAX"] = str(cfg["ilvl_max"])

    from dataclasses import asdict

    from config import PARTE1_URLS, PARTE2_URLS, PARTE3_URLS
    from scraper_sem_llm import WowheadScraperSemLLM

    resultado: Dict[str, Any] = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "versao_scraper": "1.0.0-sem-llm",
        }
    }
    async with WowheadScraperSemLLM(progress_callback=progress_callback) as scraper:
        if 1 in partes:
            itens = await scraper.extrair_ferramentas_parte(PARTE1_URLS, 1)
            resultado["parte1_ferramentas_producao"] = [asdict(i) for i in itens]
        if 2 in partes:
            itens = await scraper.extrair_ferramentas_parte(PARTE2_URLS, 2)
            resultado["parte2_ferramentas_coleta"] = [asdict(i) for i in itens]
        if 3 in partes:
            itens = await scraper.extrair_ferramentas_parte(PARTE3_URLS, 3)
            resultado["parte3_ferramentas_restante"] = [asdict(i) for i in itens]
        if 4 in partes:
            itens = await scraper.extrair_encantamentos()
            resultado["parte4_encantamentos"] = [asdict(i) for i in itens]
        if 5 in partes:
            itens = await scraper.extrair_missivas()
            resultado["parte5_missivas"] = [asdict(i) for i in itens]

    resultado["metadata"]["total_itens"] = sum(
        len(v) for v in resultado.values() if isinstance(v, list)
    )
    return resultado


async def executar_demo(progress_callback: Callable) -> Dict[str, Any]:
    progress_callback("Demonstração: simulando extração...", 0, 100)
    await asyncio.sleep(0.4)
    progress_callback("Demonstração: montando itens de exemplo...", 50, 100)
    await asyncio.sleep(0.4)

    itens = [
        {
            "id": 250001,
            "id_completo": "item=250001&bonus=12838&ilvl=341",
            "nome_ptbr": "Lâmina do Vazio Forjado",
            "nome_en": "Voidforged Blade",
            "slot": "Arma de 2 Mãos",
            "tipo_armadura": "N/A",
            "qualidade": 4,
            "qualidade_nome": "Épico",
            "qualidade_nome_en": "Epic",
            "item_level": 341,
            "track": "Mito",
            "track_stage": "6/6",
            "voidforged": True,
            "atributos_primarios": {"Força": 1420, "Vigor": 2850},
            "atributos_primarios_en": {"Strength": 1420, "Stamina": 2850},
            "atributos_secundarios": {"Aceleração": 850, "Maestria": 620},
            "atributos_secundarios_en": {"Haste": 850, "Mastery": 620},
            "idioma_atributos_primarios": "ptbr",
            "idioma_atributos_secundarios": "ptbr",
            "efeito_equip_uso": "Equip: seus golpes têm chance de liberar energia do Vazio.",
            "efeito_equip_uso_en": "Equip: your strikes have a chance to unleash Void energy.",
            "icone_url": "https://wow.zamimg.com/images/wow/icons/large/inv_sword_2h_d_01.jpg",
            "bonus_ids": ["12838"],
            "url": "https://www.wowhead.com/pt/item=250001",
            "url_en": "https://www.wowhead.com/item=250001",
            "profissao": "",
            "categoria": "Equipamentos de Combate (Gear)",
        },
        {
            "id": 250002,
            "id_completo": "item=250002&ilvl=328",
            "nome_ptbr": "Berloque do Eclipse",
            "nome_en": "Eclipse Trinket",
            "slot": "Berloque",
            "tipo_armadura": "N/A",
            "qualidade": 4,
            "qualidade_nome": "Épico",
            "qualidade_nome_en": "Epic",
            "item_level": 328,
            "track": "Herói",
            "track_stage": "6/6",
            "voidforged": True,
            "atributos_primarios": {"Agilidade": 1180},
            "atributos_primarios_en": {"Agility": 1180},
            "atributos_secundarios": {"Crítico": 910},
            "atributos_secundarios_en": {"Critical Strike": 910},
            "idioma_atributos_primarios": "ptbr",
            "idioma_atributos_secundarios": "ptbr",
            "efeito_equip_uso": "Use: libera um eclipse, causando dano ao redor.",
            "efeito_equip_uso_en": "Use: release an eclipse, dealing damage around you.",
            "icone_url": "https://wow.zamimg.com/images/wow/icons/large/spell_shadow_shadowfury.jpg",
            "bonus_ids": [],
            "url": "https://www.wowhead.com/pt/item=250002",
            "url_en": "https://www.wowhead.com/item=250002",
            "profissao": "",
            "categoria": "Equipamentos de Combate (Gear)",
        },
        {
            "id": 250003,
            "id_completo": "item=250003&ilvl=318",
            "nome_ptbr": "Elmo de Placas do Herói",
            "nome_en": "Hero's Plate Helm",
            "slot": "Cabeça",
            "tipo_armadura": "Placas",
            "qualidade": 4,
            "qualidade_nome": "Épico",
            "qualidade_nome_en": "Epic",
            "item_level": 318,
            "track": "Mito",
            "track_stage": "1/6",
            "voidforged": False,
            "atributos_primarios": {"Força": 980, "Vigor": 2100},
            "atributos_primarios_en": {"Strength": 980, "Stamina": 2100},
            "atributos_secundarios": {"Aceleração": 540, "Versatilidade": 470},
            "atributos_secundarios_en": {"Haste": 540, "Versatility": 470},
            "idioma_atributos_primarios": "ptbr",
            "idioma_atributos_secundarios": "ptbr",
            "efeito_equip_uso": "",
            "efeito_equip_uso_en": "",
            "icone_url": "https://wow.zamimg.com/images/wow/icons/large/inv_helm_plate_d_01.jpg",
            "bonus_ids": [],
            "url": "https://www.wowhead.com/pt/item=250003",
            "url_en": "https://www.wowhead.com/item=250003",
            "profissao": "",
            "categoria": "Equipamentos de Combate (Gear)",
        },
    ]
    progress_callback("Demonstração concluída", 100, 100)
    return {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "versao_scraper": "demo",
            "total_itens": len(itens),
        },
        "itens": itens,
    }


# =============================================================================
# Execução com barra de progresso
# =============================================================================

def executar_com_progresso(
    coro_factory: Callable[[Callable], Any], rotulo: str = "Executando..."
) -> Any:
    progress_data = {"message": "Iniciando...", "current": 0, "total": 100, "logs": []}

    def progress_callback(message: str, current=None, total=None) -> None:
        progress_data["message"] = message
        if current is not None:
            progress_data["current"] = current
        if total is not None:
            progress_data["total"] = max(int(total), 1)
        progress_data["logs"].append(str(message))

    fila: "queue.Queue[Any]" = queue.Queue()

    def run() -> None:
        # Streamlit/Tornado usa SelectorEventLoop no Windows, que não suporta
        # subprocessos do Playwright. O workaround está centralizado em
        # runtime.py; aqui precisamos de um loop novo para esta thread.
        loop = configurar_event_loop_windows(criar_loop=True)
        assert loop is not None, "event loop não pôde ser criado"
        try:
            resultado = coro_factory(progress_callback)
            if asyncio.iscoroutine(resultado):
                resultado = loop.run_until_complete(resultado)
            fila.put(resultado)
        except Exception as exc:  # noqa: BLE001
            fila.put(exc)
        finally:
            loop.close()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    barra = st.progress(0.0)
    logs_box = st.empty()
    with st.status(rotulo, expanded=True) as status:
        while thread.is_alive():
            total = progress_data["total"] or 1
            atual = progress_data["current"]
            barra.progress(min(atual / total, 1.0))
            status.update(label=f"{rotulo} — {progress_data['message']}")
            with logs_box.container():
                st.text("\n".join(progress_data["logs"][-8:]))
            time.sleep(0.4)
        thread.join()
        resultado = fila.get()
        barra.progress(1.0)
        if isinstance(resultado, Exception):
            status.update(label="Falhou", state="error")
            raise resultado
        status.update(label="Concluído", state="complete")
    return resultado


# =============================================================================
# Sidebar
# =============================================================================

st.sidebar.header("⚙️ Configurações")

modo_extracao = st.sidebar.radio(
    "Modo de extração",
    [
        "Season 2 - Itens (Recomendado)",
        "Sem LLM (legado)",
        "Demonstração",
    ],
    index=0,
    help="Season 2 usa o pipeline novo de gear (atributos + ícones + nomes "
    "EN/PT-BR). 'Sem LLM (legado)' usa os parsers canônicos por partes 1–5. "
    "O modo 'Com LLM (legado)' foi removido (scraper LLM antigo agora vive "
    "em legacy/).",
)

st.sidebar.subheader("🎯 Faixa de Item Level (Season 2)")
ilvl_min = st.sidebar.number_input(
    "Piso mínimo (ilvl)",
    min_value=ILVL_ABSOLUTO_MIN,
    max_value=ILVL_ABSOLUTO_MAX,
    value=ILVL_PISO_PADRAO,
    step=1,
    help="305 = Herói 1/6 em diante • 318 = somente Mito 1/6 em diante",
)
ilvl_max = st.sidebar.number_input(
    "Teto máximo (ilvl)",
    min_value=ILVL_ABSOLUTO_MIN,
    max_value=ILVL_ABSOLUTO_MAX,
    value=ILVL_TETO_PADRAO,
    step=1,
    help="Até 350 para folga (Voidforge 341 / Very Rare 344)",
)
if ilvl_max < ilvl_min:
    st.sidebar.error("O teto deve ser maior ou igual ao piso.")
    ilvl_max = ilvl_min

st.sidebar.subheader("🎯 Categorias para Extrair")
_OPCOES_CATEGORIAS = {chave: dados["nome"] for chave, dados in CATEGORIAS_WOW.items()}
categorias_selecionadas = st.sidebar.multiselect(
    "Categorias",
    options=list(_OPCOES_CATEGORIAS.keys()),
    default=["gear_season2"],  # foco principal: GEAR
    format_func=lambda chave: _OPCOES_CATEGORIAS[chave],
    key="categorias_v2",  # força o novo padrão em sessões antigas
    help="Padrão: apenas Gear de Combate. Marque outras categorias só se "
    "quiser incluí-las.",
)
st.sidebar.caption(f"Pipeline v{VERSAO_APP} • foco em gear")

# Detecta módulo antigo carregado em memória (Streamlit não recarrega imports)
try:
    _urls_verificacao = resolver_urls_categoria("gear_season2", 305, 350)
except Exception:
    _urls_verificacao = []
if any("min-level:" in url for url in _urls_verificacao):
    st.sidebar.error(
        "Configuração antiga em memória. Pare o Streamlit (Ctrl+C) e inicie "
        "novamente para carregar as URLs `min-ilvl`."
    )

if "gear_season2" in categorias_selecionadas:
    st.sidebar.success(
        "Foco: gear de combate — armaduras, armas, berloques, colares e anéis."
    )

st.sidebar.subheader("🛡️ Slots de Foco (Gear)")
slots_opcoes = st.sidebar.multiselect(
    "Slots",
    options=list(SLOTS_FOCO.keys()),
    default=[
        "Armas (Voidforge 341)",
        "Berloques & Colar (341)",
        "Armaduras (334)",
    ],
    help="Por padrão, apenas slots de gear. Selecione 'Todos' para não filtrar.",
)
slots_permitidos = sorted(
    {slot for opcao in slots_opcoes for slot in SLOTS_FOCO.get(opcao, [])}
)

# Profissões aparecem apenas quando o módulo de ferramentas é marcado
profissoes_filtro: List[str] = []
if "ferramentas_profissao" in categorias_selecionadas:
    st.sidebar.subheader("🧪 Profissões (módulo opcional)")
    todas_profissoes = st.sidebar.checkbox("Selecionar todas", value=True)
    profissoes_selecionadas = st.sidebar.multiselect(
        "Profissões (filtra guias de ferramentas)",
        options=PROFISSOES_DISPONIVEIS,
        default=PROFISSOES_DISPONIVEIS if todas_profissoes else [],
        disabled=todas_profissoes,
    )
    profissoes_filtro = (
        []
        if todas_profissoes
        or len(profissoes_selecionadas) == len(PROFISSOES_DISPONIVEIS)
        else profissoes_selecionadas
    )
else:
    st.sidebar.caption(
        "Filtros de profissão ficam ocultos porque o módulo "
        "'Equipamentos de Profissão' não está selecionado."
    )

st.sidebar.subheader("🔎 Extração")
qualidade_min = st.sidebar.selectbox(
    "Raridade mínima",
    options=[3, 4, 5],
    index=1,  # gear da Season 2 é predominantemente Épico (4)
    key="qualidade_v2",  # força o novo padrão em sessões antigas
    format_func=lambda q: {3: "Raro (3)", 4: "Épico (4)", 5: "Lendário (5)"}[q],
    help="Raridade do item: 3=Raro, 4=Épico, 5=Lendário. NÃO é a qualidade "
    "de craft (R1–R5), controlada no campo abaixo.",
)
if qualidade_min == 5:
    st.sidebar.warning(
        "Raridade 5 (Lendário) é raríssima em gear e provavelmente retornará "
        "0 itens. Use Épico (4). A qualidade de craft (R5) é independente."
    )
qualidade_craft_min = st.sidebar.selectbox(
    "Qualidade de craft (R)",
    options=[1, 2, 3, 4, 5],
    index=4,  # R5 = qualidade máxima de craft (padrão correto)
    key="craft_v2",
    format_func=lambda r: f"R{r}",
    help="Qualidade de craft do item craftado (R1–R5). Para gear craftado da "
    "Season 2, o padrão é R5. Isso é separado da raridade Épico/Lendário.",
)
exigir_craft = st.sidebar.checkbox(
    "Somente itens craftados no rank acima",
    value=True,
    key="exigir_craft_v1",
    help="Exclui itens sem qualidade de craft conhecida (não craftados). "
    "Desligue para incluir drops de M+/raid no resultado.",
)
buscar_detalhes = st.sidebar.checkbox(
    "Buscar detalhes individuais (atributos/efeitos/ícones)", value=True
)
buscar_ingles = st.sidebar.checkbox(
    "Buscar nomes em inglês (página EN do Wowhead)",
    value=True,
    help="Faz uma visita extra à versão em inglês para obter o nome oficial EN "
    "diretamente da fonte, sem tradução automática.",
)
max_itens = st.sidebar.number_input(
    "Máximo de itens",
    min_value=10,
    max_value=2000,
    value=50,
    step=10,
    help="Cada item gera 2 visitas (página EN + PT-BR). Valores altos tornam "
    "a extração demorada.",
)
max_detalhes = int(max_itens) if buscar_detalhes else 0

with st.sidebar.expander("🌐 Crawler", expanded=False):
    headless = st.checkbox("Modo Headless", value=True)
    magic_mode = st.checkbox("Magic Mode (Stealth)", value=True)
    js_lazy_load = st.checkbox("JS lazy-load (scroll)", value=True)
    wait_for = st.text_input(
        "wait_for (CSS selector)",
        value="css:a[href*='item=']",
        help="Aguardar o seletor das tabelas/listas de itens antes de ler o DOM.",
    )

# Configuração consolidada
CFG: Dict[str, Any] = {
    "ilvl_min": int(ilvl_min),
    "ilvl_max": int(ilvl_max),
    "qualidade_min": int(qualidade_min),
    "qualidade_craft_min": int(qualidade_craft_min),
    "exigir_craft": bool(exigir_craft),
    "buscar_detalhes": buscar_detalhes,
    "buscar_ingles": buscar_ingles,
    "max_itens": int(max_itens),
    "max_detalhes": max_detalhes,
    "slots_permitidos": slots_permitidos,
    "profissoes": profissoes_filtro,
    "headless": headless,
    "magic_mode": magic_mode,
    "js_lazy_load": js_lazy_load,
    "wait_for": wait_for,
}


# =============================================================================
# Cabeçalho e estado
# =============================================================================

st.title("⚔️ WoWhead Season 2 Gear Scraper")
st.markdown(
    "Foco em **gear de combate** (armaduras, armas, berloques, colares e "
    "anéis) da **Season 2**: Herói `305–321` (Voidforge `328`) e Mito "
    "`318–334` (Voidforge `341`), Very Rare até `344`. Nomes oficiais EN e "
    "PT-BR são extraídos das respectivas páginas do Wowhead."
)

if "s2_resultado" not in st.session_state:
    st.session_state["s2_resultado"] = carregar_season2()

tab_dashboard, tab_extrair, tab_resultados, tab_recomendacoes = st.tabs(
    ["📊 Dashboard", "🚀 Extrair", "📁 Resultados", "💎 Recomendações"]
)


# =============================================================================
# Tab 1 - Dashboard
# =============================================================================

with tab_dashboard:
    st.header("📊 Dashboard")
    resultado_atual = st.session_state.get("s2_resultado") or {}
    itens_atuais = resultado_atual.get("itens") or []

    if itens_atuais:
        hero = sum(1 for i in itens_atuais if 305 <= int(i.get("item_level") or 0) <= 328)
        myth = sum(1 for i in itens_atuais if 318 <= int(i.get("item_level") or 0) <= 344)
        void = sum(1 for i in itens_atuais if i.get("voidforged"))
        com_icone = sum(1 for i in itens_atuais if i.get("icone_url"))

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total de itens", len(itens_atuais))
        c2.metric("Herói (305–328)", hero)
        c3.metric("Mito (318–344)", myth)
        c4.metric("Voidforge", void)
        c5.metric("Com ícone", com_icone)

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Distribuição por Track")
            st.dataframe(
                contar_por(itens_atuais, "track"),
                use_container_width=True,
                hide_index=True,
            )
        with col_b:
            st.subheader("Distribuição por Slot")
            st.dataframe(
                contar_por(itens_atuais, "slot"),
                use_container_width=True,
                hide_index=True,
            )

        st.subheader("Amostra de itens")
        renderizar_cards(itens_atuais[:6])
    else:
        st.info(
            "Nenhum item Season 2 encontrado em `data/wowhead_itens_season2.json`. "
            "Use a aba **🚀 Extrair** para iniciar a coleta."
        )
        arquivos = list(Path("data").glob("*.json")) if Path("data").exists() else []
        if arquivos:
            st.caption(
                "Arquivos em data/: " + ", ".join(f.name for f in arquivos)
            )


# =============================================================================
# Tab 2 - Extrair
# =============================================================================

with tab_extrair:
    st.header("🚀 Extrair")

    modo_sem_llm = modo_extracao == "Sem LLM (legado)"
    modo_demo = modo_extracao == "Demonstração"
    modo_season2 = modo_extracao == "Season 2 - Itens (Recomendado)"

    categorias_urls = montar_categorias_selecionadas(
        categorias_selecionadas,
        int(ilvl_min),
        int(ilvl_max),
        limite=int(max_itens),
        somente_craft=bool(exigir_craft),
    )

    with st.expander("🔗 URLs que serão visitadas", expanded=False):
        if categorias_urls:
            for nome_categoria, urls in categorias_urls.items():
                st.markdown(f"**{nome_categoria}**")
                for url in urls:
                    st.caption(f"• {url}")
        else:
            st.warning("Nenhuma categoria selecionada.")

    urls_custom = st.text_area(
        "URLs personalizadas (uma por linha, opcional)",
        placeholder="https://www.wowhead.com/pt/item=250001\n"
        "https://www.wowhead.com/pt/items/min-level:305/max-level:350",
        height=90,
    )

    st.divider()

    if modo_season2:
        st.success(
            f"Pipeline Season 2 • ilvl **{int(ilvl_min)}–{int(ilvl_max)}** • "
            f"qualidade mínima **{qualidade_min}** • detalhes individuais: "
            f"**{'sim' if buscar_detalhes else 'não'}**"
        )
        partes_legado: List[int] = []
    elif modo_sem_llm:
        partes_legado = sorted(
            {
                parte
                for chave in categorias_selecionadas
                for parte in PARTES_POR_CATEGORIA.get(chave, [])
            }
        )
        if not partes_legado:
            st.warning(
                "Os modos legados cobrem apenas 'Equipamentos de Profissão' "
                "(partes 1-3) e 'Aprimoramentos e Consumíveis' (partes 4-5)."
            )
        st.info(f"Partes legadas que serão executadas: {partes_legado or 'nenhuma'}")
    else:
        partes_legado = []

    pode_executar = bool(categorias_urls) or bool(urls_custom.strip()) or modo_demo
    if not pode_executar:
        st.error("Selecione ao menos uma categoria ou informe URLs personalizadas.")

    if st.button(
        "🚀 Iniciar extração",
        type="primary",
        use_container_width=True,
        disabled=not pode_executar,
    ):
        try:
            if modo_demo:
                resultado = executar_com_progresso(
                    lambda cb: executar_demo(cb), "Executando demonstração"
                )
                st.session_state["s2_resultado"] = resultado

            elif modo_season2:
                urls_extras: List[str] = []
                for linha in urls_custom.splitlines():
                    if linha.strip():
                        urls_extras.extend(normalizar_url_gear(linha.strip()))
                categorias_exec = dict(categorias_urls)
                if urls_extras:
                    categorias_exec["URLs personalizadas"] = urls_extras

                resultado = executar_com_progresso(
                    lambda cb: executar_season2(categorias_exec, CFG, cb),
                    "Extraindo itens da Season 2",
                )
                st.session_state["s2_resultado"] = resultado

            else:
                resultado = executar_com_progresso(
                    lambda cb: executar_legado(partes_legado, CFG, cb),
                    "Executando scraper legado",
                )

            st.success("Extração concluída com sucesso!")

            if modo_season2 or modo_demo:
                resultado_novo = st.session_state.get("s2_resultado") or {}
                itens_novos = resultado_novo.get("itens", [])
                meta_novo = resultado_novo.get("metadata") or {}
                if not itens_novos:
                    desc = meta_novo.get("descartes") or {}
                    st.warning(
                        "Extração concluída, mas **0 itens passaram nos filtros**. "
                        f"Brutos detalhados: **{meta_novo.get('total_brutos', 0)}**. "
                        f"Descartes: ilvl fora={desc.get('ilvl_fora', 0)}, "
                        f"sem ilvl={desc.get('sem_ilvl', 0)}, "
                        f"qualidade={desc.get('qualidade', 0)}, "
                        f"slot={desc.get('slot', 0)}, "
                        f"profissão={desc.get('profissao', 0)}. "
                        "Confira as URLs (use `min-ilvl`/`max-ilvl`), o piso/teto "
                        "e a qualidade mínima."
                    )
                st.subheader("Resultado da execução")
                renderizar_itens(itens_novos, key_prefix="exec")
            else:
                total = sum(
                    len(v) for v in resultado.values() if isinstance(v, list)
                )
                st.metric("Itens extraídos (legado)", total)
                markdown_legado = gerar_markdown_legado(resultado)
                st.download_button(
                    "📥 Baixar Markdown (legado)",
                    data=markdown_legado,
                    file_name="database_midnight_legado.md",
                    mime="text/markdown",
                )

        except Exception as exc:  # noqa: BLE001
            st.error(f"Erro durante a extração: {exc}")
            import traceback

            st.code(traceback.format_exc())


# =============================================================================
# Tab 3 - Resultados e Exportação
# =============================================================================

with tab_resultados:
    st.header("📁 Resultados e Exportação")

    resultado_atual = st.session_state.get("s2_resultado") or {}
    itens_atuais = resultado_atual.get("itens") or []

    if not itens_atuais:
        st.info(
            "Nenhum resultado Season 2 carregado. Execute a extração na aba "
            "**🚀 Extrair**."
        )
        meta_vazio = resultado_atual.get("metadata") or {}
        if meta_vazio.get("descartes"):
            desc = meta_vazio["descartes"]
            st.warning(
                "A última extração não gerou itens. "
                f"Brutos detalhados: {meta_vazio.get('total_brutos', 0)}. "
                f"Descartes: ilvl fora={desc.get('ilvl_fora', 0)}, "
                f"sem ilvl={desc.get('sem_ilvl', 0)}, "
                f"qualidade={desc.get('qualidade', 0)}, "
                f"slot={desc.get('slot', 0)}, "
                f"profissão={desc.get('profissao', 0)}."
            )
    else:
        meta = resultado_atual.get("metadata") or {}
        st.caption(
            f"Fonte: `{ARQUIVO_SEASON2}` • "
            f"Gerado em {meta.get('timestamp', 'desconhecido')} • "
            f"{len(itens_atuais)} itens"
        )

        for aviso in meta.get("avisos_catalogo") or []:
            st.warning(
                f"{aviso.get('categoria')}: {aviso.get('aviso')} "
                f"Fonte: {', '.join(aviso.get('urls') or [])}"
            )

        st.subheader("Filtros de exibição")
        f1, f2, f3, f4 = st.columns([2, 2, 2, 2])
        with f1:
            filtro_busca = st.text_input("Buscar por nome/slot/profissão", "")
        with f2:
            filtro_ilvl = st.slider(
                "Faixa de ilvl exibida",
                min_value=ILVL_ABSOLUTO_MIN,
                max_value=ILVL_ABSOLUTO_MAX,
                value=(int(ilvl_min), int(ilvl_max)),
            )
        with f3:
            filtro_tracks = st.multiselect(
                "Tracks",
                options=["Herói", "Mito", "Muito Raro", "Base"],
                default=[],
            )
        with f4:
            filtro_void = st.checkbox("Somente Voidforge", value=False)
            filtro_icone = st.checkbox("Somente com ícone", value=False)

        f5, f6, f7, f8 = st.columns([2, 2, 2, 2])
        with f5:
            labels_tipos = st.multiselect(
                "Tipo de item", options=list(TIPOS_LABEL.values()), default=[]
            )
            filtro_tipos = [
                chave
                for chave, label in TIPOS_LABEL.items()
                if label in labels_tipos
            ]
        with f6:
            filtro_armaduras = st.multiselect(
                "Tipo de armadura",
                options=["Tecido", "Couro", "Malha", "Placas", "N/A"],
                default=[],
            )
        with f7:
            profs_craft = sorted(
                {
                    i.get("profissao_craft")
                    for i in itens_atuais
                    if i.get("profissao_craft")
                }
            )
            filtro_profs_craft = st.multiselect(
                "Profissão que crafta", options=profs_craft, default=[]
            )
        with f8:
            filtro_emb = st.checkbox("Somente embelezamentos", value=False)
            filtro_missiva = st.checkbox("Somente missivas", value=False)

        filtrados = filtrar_itens(
            itens_atuais,
            {
                "busca": filtro_busca,
                "ilvl_min": filtro_ilvl[0],
                "ilvl_max": filtro_ilvl[1],
                "tracks": filtro_tracks,
                "voidforged": filtro_void,
                "com_icone": filtro_icone,
                "tipos": filtro_tipos,
                "armaduras": filtro_armaduras,
                "profissoes_craft": filtro_profs_craft,
                "somente_embelezamento": filtro_emb,
                "somente_missiva": filtro_missiva,
            },
        )
        st.caption(f"{len(filtrados)} de {len(itens_atuais)} itens após filtros")

        renderizar_itens(filtrados, key_prefix="tab3")

        if filtrados:
            st.subheader("Tooltip Raidbots")
            opcoes_tooltip = list(range(len(filtrados)))

            def _rotulo_tooltip(indice: int) -> str:
                registro = filtrados[indice]
                nome_item = (
                    registro.get("nome_ptbr")
                    or registro.get("nome_en")
                    or "Item"
                )
                return (
                    f"{nome_item} — ilvl "
                    f"{int(registro.get('item_level') or 0)}"
                )

            indice_tooltip = st.selectbox(
                "Item para inspecionar o tooltip",
                opcoes_tooltip,
                format_func=_rotulo_tooltip,
                key="tab3_tooltip_item",
            )
            item_tooltip = filtrados[int(indice_tooltip)]
            with st.expander("Tooltip Raidbots", expanded=False):
                st.code(
                    item_tooltip.get("tooltip_raidbots")
                    or montar_tooltip_raidbots(item_tooltip, "ptbr"),
                    language="text",
                )
            with st.expander("Tooltip Raidbots (EN)", expanded=False):
                st.code(
                    item_tooltip.get("tooltip_raidbots_en")
                    or montar_tooltip_raidbots(item_tooltip, "en"),
                    language="text",
                )

        st.subheader("Exportar")
        col_csv, col_json, col_md = st.columns(3)
        with col_csv:
            st.download_button(
                "📥 CSV",
                data=gerar_csv(filtrados),
                file_name="wowhead_season2.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_json:
            st.download_button(
                "📥 JSON",
                data=json.dumps(
                    {"metadata": meta, "itens": filtrados},
                    ensure_ascii=False,
                    indent=2,
                ),
                file_name="wowhead_season2.json",
                mime="application/json",
                use_container_width=True,
            )
        with col_md:
            st.download_button(
                "📥 Markdown (EN/PT-BR)",
                data=gerar_markdown(filtrados, meta),
                file_name="wowhead_season2.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with st.expander("🧾 Prévia do Markdown"):
            st.code(gerar_markdown(filtrados[:20], meta))

    st.divider()
    with st.expander("🗂️ Arquivos de dados existentes", expanded=False):
        data_dir = Path("data")
        if data_dir.exists():
            arquivos = sorted(data_dir.glob("*.json"))
            if arquivos:
                for arquivo in arquivos:
                    tamanho = arquivo.stat().st_size / 1024
                    st.text(f"{arquivo.name} — {tamanho:.1f} KB")
            else:
                st.caption("Diretório `data` vazio.")
        else:
            st.caption("Diretório `data` inexistente.")


# =============================================================================
# Rodapé
# =============================================================================
# =============================================================================
# Tab 4 - Recomendações de encantamento e gema
# =============================================================================

with tab_recomendacoes:
    st.header("💎 Recomendações de Encantamento & Gema")

    resultado_atual = st.session_state.get("s2_resultado") or {}
    itens_atuais = resultado_atual.get("itens") or []
    catalogo = [
        i
        for i in itens_atuais
        if i.get("tipo_item") in ("encantamento", "gema")
    ]
    origem_catalogo = "resultado da extração atual"
    if not catalogo:
        catalogo = carregar_catalogo()
        if catalogo:
            origem_catalogo = "data/wowhead_catalogo.json"
            st.info(
                "Usando o catálogo salvo em `data/wowhead_catalogo.json` "
                f"({len(catalogo)} itens)."
            )
    gear = [
        i
        for i in itens_atuais
        if i.get("tipo_item") in ("gear", "embelezamento")
    ]

    st.caption(
        "As sugestões usam o catálogo raspado e regras explícitas: "
        "compatibilidade de slot > atributo primário da especialidade > "
        "prioridade de secundários > valor/rank. Não há dados fictícios; "
        "sem catálogo, a recomendação fica indisponível."
    )

    if not catalogo:
        st.warning(
            "Catálogo de encantamentos/gemas indisponível. Marque as "
            "categorias **Encantamentos** e **Gemas** na sidebar e execute a "
            "extração. Fontes validadas: "
            "`https://www.wowhead.com/pt/items/enchants` e "
            "`https://www.wowhead.com/pt/items/gems`."
        )
    elif not gear:
        st.info("Nenhum item de gear no resultado para receber recomendações.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            classe = st.selectbox(
                "Classe", list(CLASSES_ESPECIALIDADES.keys())
            )
        with c2:
            especialidade = st.selectbox(
                "Especialidade",
                list(CLASSES_ESPECIALIDADES[classe].keys()),
            )
        with c3:
            primario_auto = primario_da_especialidade(classe, especialidade)
            escolha_primario = st.selectbox(
                "Atributo primário",
                [
                    f"Automático ({primario_auto or 'indefinido'})",
                    "Força",
                    "Agilidade",
                    "Intelecto",
                ],
            )
            primario_override = (
                ""
                if escolha_primario.startswith("Automático")
                else escolha_primario
            )

        p1, p2, p3 = st.columns(3)
        with p1:
            prio1 = st.selectbox(
                "Prioridade #1", ATRIBUTOS_PRIORIDADE, index=0
            )
        with p2:
            prio2 = st.selectbox(
                "Prioridade #2", ATRIBUTOS_PRIORIDADE, index=1
            )
        with p3:
            prio3 = st.selectbox(
                "Prioridade #3", ATRIBUTOS_PRIORIDADE, index=2
            )
        prioridade: List[str] = []
        for prioridade_item in (prio1, prio2, prio3):
            if prioridade_item not in prioridade:
                prioridade.append(prioridade_item)

        rec = gerar_recomendacoes(
            itens_atuais,
            classe,
            especialidade,
            prioridade,
            primario_override=primario_override,
        )
        st.caption(
            f"Atributo primário usado: **{rec['primario'] or 'Indisponível'}** "
            f"• catálogo: {origem_catalogo}"
        )

        if rec["status"] == "sem_catalogo":
            st.warning(
                "Catálogo indisponível no momento da recomendação "
                "(fonte: páginas de Encantamentos/Gemas)."
            )
        elif rec["itens"]:
            df_rec = pd.DataFrame(rec["itens"])
            st.dataframe(
                df_rec,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "encantamento_justificativa": st.column_config.TextColumn(
                        "Justificativa (encantamento)", width="large"
                    ),
                    "gema_justificativa": st.column_config.TextColumn(
                        "Justificativa (gema)", width="large"
                    ),
                },
            )
            st.download_button(
                "📥 Baixar recomendações (CSV)",
                data=df_rec.to_csv(index=False),
                file_name="recomendacoes_season2.csv",
                mime="text/csv",
            )
        else:
            st.info(
                "Sem itens de gear para recomendar com o catálogo atual."
            )

        with st.expander("📚 Catálogo raspado (encantamentos/gemas)"):
            st.caption(f"{len(catalogo)} itens no catálogo.")
            renderizar_itens(catalogo, key_prefix="catalogo")


# =============================================================================
# Rodapé
# =============================================================================
st.divider()
st.markdown(
    "**WoWhead Season 2 Gear Scraper** • Crawl4AI + Streamlit • "
    "ícones via CDN `wow.zamimg.com`"
)
