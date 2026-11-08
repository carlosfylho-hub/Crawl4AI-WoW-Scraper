#!/usr/bin/env python3
"""
Gerador do documento Markdown final da Season 2 (Midnight).

- Tabelas agrupadas por slot para gear e por tipo para catálogos.
- Coluna de ícone renderizada via Markdown/HTML (`<img>`).
- Nomes em inglês e PT-BR extraídos de suas fontes localizadas.
- Tipo de item, subtipo, tipo de armadura, profissão de craft, missiva,
  embelezamento, rank, cor de gema, fonte e vínculo com conteúdo.
- Campos sem dado aparecem como "Indisponível"; a fonte fica na coluna Link.
- Uma linha por item/varição real (Bonus IDs distintos permanecem separados).
"""

from __future__ import annotations

import html
import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from tooltip_raidbots import montar_tooltip_raidbots

ORDEM_SLOTS = [
    "Cabeça",
    "Colar",
    "Ombros",
    "Costas",
    "Peito",
    "Pulso",
    "Mãos",
    "Cintura",
    "Pernas",
    "Pés",
    "Anel",
    "Berloque",
    "Arma de 1 Mão",
    "Arma de 2 Mãos",
    "Escudo",
    "Mão Secundária",
    "Ferramenta",
    "N/A",
]

ORDEM_GRUPOS = ORDEM_SLOTS + [
    "Encantamentos",
    "Gemas",
    "Missivas",
    "Consumíveis",
    "Reagentes",
    "Outros",
]

TIPOS_LABEL = {
    "gear": "Gear",
    "encantamento": "Encantamento",
    "gema": "Gema",
    "missiva": "Missiva",
    "embelezamento": "Embelezamento",
    "ferramenta": "Ferramenta",
    "consumivel": "Consumível",
    "reagente": "Reagente",
    "outro": "Outro",
}

CABECALHO_TABELA = (
    "| Ícone | Nome (EN) | Nome (PT-BR) | Tipo de Item | Slot | Subtipo "
    "| Armadura | Qualidade | Craft (R) | ilvl | Track | Voidforge "
    "| Profissão Craft | Slot-Alvo | Atributos Primários "
    "| Atributos Secundários | Efeito / Bônus | Missiva / Embelezamento "
    "| Rank / Cor | Fonte / Vínculo | Bonus IDs | ID | Link |"
)
SEPARADOR_TABELA = "|" + "---|" * 23


def _celula(valor: Any) -> str:
    """Normaliza uma célula de tabela Markdown (sem quebrar colunas)."""
    texto = "" if valor is None else str(valor)
    texto = texto.replace("\r", " ").replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto).strip()
    texto = html.escape(texto, quote=False)
    return texto.replace("|", "\\|")


def _ou_indisponivel(valor: Any) -> str:
    texto = "" if valor is None else str(valor).strip()
    return _celula(texto) if texto else "Indisponível"


def _formatar_atributos(
    atributos: Optional[Dict[str, Any]], idioma: str = "ptbr"
) -> str:
    if not atributos:
        return "—"
    itens = [f"{_celula(nome)} +{valor}" for nome, valor in atributos.items()]
    texto = " · ".join(itens)
    if idioma == "en":
        texto += " *(EN)*"
    return texto


def _icone_markdown(item: Dict[str, Any]) -> str:
    url = item.get("icone_url") or ""
    if not url:
        return "Indisponível"
    alt = item.get("nome_en") or item.get("nome_ptbr") or "ícone"
    return (
        f'<img src="{html.escape(url, quote=True)}" width="26" height="26" '
        f'alt="{html.escape(str(alt), quote=True)}"/>'
    )


def _link(item: Dict[str, Any]) -> str:
    url_pt = item.get("url") or ""
    url_en = item.get("url_en") or ""
    links = []
    if url_pt:
        links.append(f"[PT]({url_pt})")
    if url_en:
        links.append(f"[EN]({url_en})")
    return " · ".join(links) if links else "Indisponível"


def _texto_missiva_embelezamento(item: Dict[str, Any]) -> str:
    partes: List[str] = []
    if item.get("tipo_item") == "missiva" and item.get("missiva_atributo"):
        partes.append(f"Missiva: {item['missiva_atributo']}")
    if item.get("embelezamento"):
        partes.append("Embelezamento")
    aplicaveis = item.get("missivas_aplicaveis") or []
    if aplicaveis:
        partes.append("Missivas aplicáveis: " + ", ".join(aplicaveis))
    return " · ".join(partes) if partes else "—"


def _linha_tabela(item: Dict[str, Any]) -> str:
    tipo = item.get("tipo_item") or "outro"
    tipo_label = TIPOS_LABEL.get(tipo, "Outro")
    bonus = ":".join(str(b) for b in (item.get("bonus_ids") or [])) or "—"
    void = "Sim" if item.get("voidforged") else "Não"
    track = " ".join(
        parte
        for parte in (item.get("track") or "", item.get("track_stage") or "")
        if parte
    )
    qualidade = item.get("qualidade_nome") or item.get("qualidade") or ""
    if item.get("qualidade_nome_en"):
        qualidade = f"{qualidade} ({item['qualidade_nome_en']})"

    craft_r = int(item.get("qualidade_craft") or 0)
    craft = f"R{craft_r}" if craft_r else "—"

    rank = int(item.get("rank") or 0)
    rank_cor_partes = []
    if rank:
        rank_cor_partes.append(f"Rank {rank}")
    if item.get("gema_cor"):
        rank_cor_partes.append(f"Gema {item['gema_cor']}")
    rank_cor = " · ".join(rank_cor_partes)

    fonte_partes = [
        parte
        for parte in (item.get("fonte") or "", item.get("vinculo_conteudo") or "")
        if parte
    ]

    profissional = item.get("profissao_craft") or "Indisponível"
    slot_alvo = item.get("slot_alvo") or (
        "Indisponível" if tipo == "encantamento" else "N/A"
    )

    celulas = [
        _icone_markdown(item),
        _ou_indisponivel(item.get("nome_en")),
        _ou_indisponivel(item.get("nome_ptbr")),
        _celula(tipo_label),
        _ou_indisponivel(item.get("slot")),
        _ou_indisponivel(item.get("subtipo")),
        _ou_indisponivel(item.get("tipo_armadura")),
        _celula(qualidade) or "Indisponível",
        _celula(craft),
        str(int(item.get("item_level") or 0)),
        _celula(track) or "—",
        void,
        _ou_indisponivel(profissional),
        _celula(slot_alvo),
        _formatar_atributos(
            item.get("atributos_primarios"),
            item.get("idioma_atributos_primarios") or "ptbr",
        ),
        _formatar_atributos(
            item.get("atributos_secundarios"),
            item.get("idioma_atributos_secundarios") or "ptbr",
        ),
        _celula(item.get("efeito_equip_uso")) or "—",
        _celula(_texto_missiva_embelezamento(item)),
        _celula(rank_cor) or "Indisponível",
        _celula(" / ".join(fonte_partes)) or "Indisponível",
        _celula(bonus),
        _celula(item.get("id")),
        _link(item),
    ]
    return "| " + " | ".join(celulas) + " |"


def _secao_tooltips(itens: List[Dict[str, Any]]) -> List[str]:
    """Seção por item com o tooltip Raidbots (tabela principal já é larga).

    A tabela principal tem 23 colunas; adicionar uma coluna com blocos
    multilinha quebraria a renderização. Por isso o tooltip vai em blocos
    `text` logo abaixo da tabela do grupo.
    """
    linhas: List[str] = []
    for item in itens:
        tooltip = str(item.get("tooltip_raidbots") or "").strip()
        if not tooltip:
            tooltip = montar_tooltip_raidbots(item, "ptbr")
        if not tooltip:
            continue
        nome = item.get("nome_ptbr") or item.get("nome_en") or item.get("id") or "Item"
        linhas.append(f"#### Tooltip Raidbots — {_celula(nome)}")
        linhas.append("")
        linhas.append("```text")
        linhas.extend(tooltip.splitlines())
        linhas.append("```")
        linhas.append("")
    return linhas


def _grupo_item(item: Dict[str, Any]) -> str:
    tipo = item.get("tipo_item")
    if tipo in ("gear", "embelezamento", "ferramenta"):
        slot = item.get("slot") or "N/A"
        return slot if slot in ORDEM_SLOTS else "Outros"
    return {
        "encantamento": "Encantamentos",
        "gema": "Gemas",
        "missiva": "Missivas",
        "consumivel": "Consumíveis",
        "reagente": "Reagentes",
    }.get(tipo or "", "Outros")


def _tabela_contagem(
    itens: List[Dict[str, Any]], funcao, titulo: str
) -> str:
    contagem: Dict[str, int] = {}
    for item in itens:
        chave = funcao(item)
        contagem[chave] = contagem.get(chave, 0) + 1
    linhas = [f"| {titulo} | Itens |", "|---|---|"]
    for chave in sorted(contagem):
        linhas.append(f"| {_celula(chave)} | {contagem[chave]} |")
    return "\n".join(linhas)


def gerar_markdown(
    itens: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None,
    titulo: str = "World of Warcraft — Season 2 (Midnight)",
) -> str:
    """Retorna o documento Markdown completo, limpo e pronto para uso."""
    metadata = metadata or {}
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    linhas: List[str] = [
        f"# {titulo}",
        "",
        f"> Gerado em **{agora}** • **{len(itens)}** item(ns)/variação(ões).",
        "> Nomes em inglês e PT-BR foram extraídos das respectivas páginas "
        "localizadas do Wowhead (sem tradução automática).",
        "> Atributos vêm dos tooltips localizados; o marcador *(EN)* indica "
        "que aquele tooltip era a fonte disponível.",
        "> Campos não encontrados na página aparecem como **Indisponível**; "
        "a fonte consultada está na coluna Link.",
        "",
        "## Resumo",
        "",
        f"**Total:** {len(itens)}",
        "",
    ]

    if metadata:
        linhas.extend(
            [
                f"- Fonte: `{metadata.get('versao_scraper', 'scraper_season2')}`",
                "- Faixa de ilvl: "
                f"`{metadata.get('ilvl_min', '?')}–{metadata.get('ilvl_max', '?')}`",
                f"- Raridade mínima: `{metadata.get('qualidade_min', '?')}`",
                "- Qualidade de craft mínima: "
                f"`R{metadata.get('qualidade_craft_min', 5)}` "
                "(separada da raridade)",
            ]
        )
        if metadata.get("timestamp"):
            linhas.append(f"- Timestamp da coleta: `{metadata['timestamp']}`")
        avisos = metadata.get("avisos_catalogo") or []
        if avisos:
            linhas.append("")
            linhas.append("### Avisos de catálogo")
            linhas.append("")
            for aviso in avisos:
                linhas.append(
                    f"- **{aviso.get('categoria')}**: {aviso.get('aviso')} "
                    f"(fonte: {', '.join(aviso.get('urls') or [])})"
                )
        linhas.append("")

    linhas.extend(
        [
            "### Por Tipo de Item",
            "",
            _tabela_contagem(
                itens, lambda i: TIPOS_LABEL.get(i.get("tipo_item") or "outro", "Outro"), "Tipo"
            ),
            "",
            "### Por Tipo de Armadura",
            "",
            _tabela_contagem(
                itens, lambda i: i.get("tipo_armadura") or "N/A", "Armadura"
            ),
            "",
            "### Por Slot",
            "",
            _tabela_contagem(itens, _grupo_item, "Slot/Grupo"),
            "",
            "## Itens",
            "",
        ]
    )

    if not itens:
        linhas.append(
            "_Nenhum item foi extraído. Verifique as URLs/filtros e execute "
            "novamente._"
        )
        return "\n".join(linhas) + "\n"

    grupos: Dict[str, List[Dict[str, Any]]] = {}
    for item in itens:
        grupos.setdefault(_grupo_item(item), []).append(item)

    for grupo in [g for g in ORDEM_GRUPOS if g in grupos]:
        linhas.append(f"### {grupo}")
        linhas.append("")
        linhas.append(CABECALHO_TABELA)
        linhas.append(SEPARADOR_TABELA)
        itens_grupo = sorted(
            grupos[grupo],
            key=lambda x: (
                -int(x.get("item_level") or 0),
                (x.get("nome_ptbr") or x.get("nome_en") or "").lower(),
                ":".join(str(b) for b in (x.get("bonus_ids") or [])),
            ),
        )
        for item in itens_grupo:
            linhas.append(_linha_tabela(item))
        linhas.append("")
        linhas.extend(_secao_tooltips(itens_grupo))

    linhas.extend(
        [
            "---",
            "",
            "_Ícones servidos pelo CDN oficial do Wowhead "
            "(`wow.zamimg.com`). Cada linha corresponde a um item ou variação "
            "real (ID + ilvl + Bonus IDs). Recomendações de encantamento/gema "
            "são geradas separadamente pelo app, com base no catálogo raspado "
            "e na prioridade definida pelo usuário._",
        ]
    )
    return "\n".join(linhas) + "\n"


def salvar_markdown(
    itens: List[Dict[str, Any]],
    caminho: str = os.path.join("data", "wowhead_season2.md"),
    metadata: Optional[Dict[str, Any]] = None,
    titulo: str = "World of Warcraft — Season 2 (Midnight)",
) -> str:
    """Gera e salva o Markdown, retornando o caminho do arquivo."""
    diretorio = os.path.dirname(caminho)
    if diretorio:
        os.makedirs(diretorio, exist_ok=True)
    conteudo = gerar_markdown(itens, metadata=metadata, titulo=titulo)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return caminho


def salvar_json(
    itens: List[Dict[str, Any]],
    caminho: str = os.path.join("data", "wowhead_itens_season2.json"),
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    diretorio = os.path.dirname(caminho)
    if diretorio:
        os.makedirs(diretorio, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(
            {"metadata": metadata or {}, "itens": itens},
            f,
            ensure_ascii=False,
            indent=2,
        )
    return caminho
