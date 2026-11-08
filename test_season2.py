#!/usr/bin/env python3
"""
Testes offline (sem rede) dos utilitários e do parser da Season 2.

Execute com:
    python test_season2.py
"""

from __future__ import annotations

import sys

from bs4 import BeautifulSoup

from markdown_season2 import gerar_markdown as gerar_markdown_final
from recomendacoes import gerar_recomendacoes
from wow_season2 import (
    associar_icones_media,
    badges_trilha,
    chave_variacao,
    classificar_track,
    extrair_atributos,
    extrair_atributos_de_efeito,
    extrair_atributos_localizados,
    extrair_detalhes_item,
    extrair_efeito,
    classificar_tipo_item,
    extrair_fonte,
    extrair_gema_cor,
    extrair_qualidade_craft,
    extrair_rank,
    extrair_slot,
    extrair_slot_alvo,
    extrair_subtipo,
    extrair_tipo_armadura,
    extrair_vinculo_conteudo,
    finalizar_item,
    finalizar_item_bilingue,
    icone_de_style,
    montar_icone_url,
    parse_item_unico,
    parse_links_itens,
)

FIXTURE_LISTA = """
<html><body>
  <table>
    <tr>
      <td>
        <ins style="background-image:url('https://wow.zamimg.com/images/wow/icons/tiny/inv_sword_2h_d_01.gif')"></ins>
        <a class="q4" href="/pt/item=250001/lamina-do-vazio"
           data-wowhead="item=250001&ilvl=341&bonus=12838:12839">Lâmina do Vazio</a>
      </td>
    </tr>
    <tr>
      <td>
        <span class="quality-4">
          <a href="/pt/item=250002" data-wowhead="item=250002&ilvl=318">Berloque Etéreo</a>
        </span>
      </td>
    </tr>
  </table>
</body></html>
"""

FIXTURE_TOOLTIP = """
Lâmina do Vazio Forjado
Item Level 341
Arma de Duas Mãos
Épico
Força +1.420
Vigor +2.850
Aceleração +850
Maestria +620
Equip: Seus golpes têm chance de liberar energia do Vazio.
Voidforge 6/6
"""

FIXTURE_TOOLTIP_EN = """
Voidforged Blade
Item Level 341
Two-Hand
Sword
+1,420 Strength
+2,850 Stamina
+850 Haste
+620 Mastery
Equip: Your strikes have a chance to unleash Void energy.
Voidforge 6/6
"""

FIXTURE_ITEM = f"""
<html>
  <head>
    <meta property="og:image" content="https://wow.zamimg.com/images/wow/icons/large/inv_sword_2h_d_01.jpg">
  </head>
  <body>
    <h1 class="heading-size-1 q4">Lâmina do Vazio Forjado</h1>
    <div id="main-contents">
      <div class="wowhead-tooltip">
        <div class="text">{FIXTURE_TOOLTIP}</div>
      </div>
    </div>
  </body>
</html>
"""

# Página sem classe de qualidade no h1: a qualidade está em .q5 do tooltip
FIXTURE_ITEM_Q5 = """
<html><body>
  <h1 class="heading-size-1">Tormentária</h1>
  <div id="tt19019" class="wowhead-tooltip">
    <table>
      <tr><td><span class="q5">Tormentária</span></td></tr>
      <tr><td>Nível do Item:</td><td>40</td></tr>
      <tr><td>Uma Mão</td></tr>
      <tr><td>Espada</td></tr>
    </table>
  </div>
</body></html>
"""


def testar_icones() -> None:
    esperado = "https://wow.zamimg.com/images/wow/icons/large/inv_sword_2h_d_01.jpg"
    assert montar_icone_url("inv_sword_2h_d_01") == esperado
    assert montar_icone_url("inv_sword_2h_d_01.jpg") == esperado
    assert (
        montar_icone_url(
            "https://wow.zamimg.com/images/wow/icons/medium/inv_sword_2h_d_01.png"
        )
        == esperado
    )
    assert (
        icone_de_style(
            "background-image: url('https://wow.zamimg.com/images/wow/icons/tiny/spell_nature_healingway.gif')"
        )
        == "https://wow.zamimg.com/images/wow/icons/large/spell_nature_healingway.jpg"
    )
    assert montar_icone_url("") == ""
    print("[OK] Ícones/CDN")


def testar_tracks() -> None:
    casos = {
        305: ("Herói", False),
        321: ("Herói", False),
        328: ("Herói", True),
        322: ("Mito", False),
        334: ("Mito", False),
        341: ("Mito", True),
        344: ("Muito Raro", False),
        250: ("Base", False),
    }
    for ilvl, (track, void) in casos.items():
        obtido_track, obtido_void, _ = classificar_track(ilvl)
        assert (obtido_track, obtido_void) == (track, void), (
            ilvl,
            obtido_track,
            obtido_void,
        )

    track, void, stage = classificar_track(341, "Myth 4/6 Voidforged")
    assert track == "Mito" and void is True and stage == "4/6"

    assert badges_trilha(305) == ["Herói"]
    assert "Mito" in badges_trilha(318)
    assert "Voidforge" in badges_trilha(341, voidforged=True)
    print("[OK] Classificação de track/Voidforge/badges")


def testar_atributos() -> None:
    primarios, secundarios = extrair_atributos(FIXTURE_TOOLTIP)
    assert primarios == {"Força": 1420, "Vigor": 2850}, primarios
    assert secundarios == {"Aceleração": 850, "Maestria": 620}, secundarios

    # Localizado: nomes exatos conforme o idioma da fonte
    prim_pt, sec_pt = extrair_atributos_localizados(FIXTURE_TOOLTIP, "ptbr")
    assert prim_pt == {"Força": 1420, "Vigor": 2850}, prim_pt
    assert sec_pt == {"Aceleração": 850, "Maestria": 620}, sec_pt

    prim_en, sec_en = extrair_atributos_localizados(FIXTURE_TOOLTIP_EN, "en")
    assert prim_en == {"Strength": 1420, "Stamina": 2850}, prim_en
    assert sec_en == {"Haste": 850, "Mastery": 620}, sec_en

    # Formato real do tooltip PT-BR (frases + valor na linha seguinte)
    real_pt = """
Capuz do Porta-voz Sobressalente
Nível do Item:
334
Cabeça
Couro
147 Armadura
+189 [Agilidade ou Intelecto]
+3.910 Vigor
Aumenta o seu índice de acerto crítico em +
86
(1.87% @ L90)
Aumenta o seu índice de aceleração em +
115
(2.61% @ L90)
"""
    prim_real, sec_real = extrair_atributos_localizados(real_pt, "ptbr")
    assert prim_real == {"Agilidade ou Intelecto": 189, "Vigor": 3910}, prim_real
    assert sec_real == {"Acerto Crítico": 86, "Aceleração": 115}, sec_real

    # Formato real EN ("+" isolado antes do número)
    real_en = """
+189 [Agility or Intellect]
+3,910 Stamina
+
86 Critical Strike
(1.87% @ L90)
+
115 Haste
(2.61% @ L90)
"""
    prim_real_en, sec_real_en = extrair_atributos_localizados(real_en, "en")
    assert prim_real_en == {
        "Agility or Intellect": 189,
        "Stamina": 3910,
    }, prim_real_en
    assert sec_real_en == {
        "Critical Strike": 86,
        "Haste": 115,
    }, sec_real_en

    assert extrair_slot(FIXTURE_TOOLTIP) == "Arma de 2 Mãos"
    assert extrair_slot("Cabeça\nPlacas\nVigor +100") == "Cabeça"
    assert extrair_tipo_armadura("Cabeça\nPlacas\nVigor +100") == "Placas"
    assert extrair_tipo_armadura(FIXTURE_TOOLTIP) == ""

    efeito = extrair_efeito(FIXTURE_TOOLTIP)
    assert "Seus golpes" in efeito, efeito

    # Números da linha seguinte não devem ser capturados como atributo
    prim2, _ = extrair_atributos("+2 Agilidade\n+3 Vigor\n+1 de resistência a Fogo")
    assert prim2 == {"Agilidade": 2, "Vigor": 3}, prim2

    # Slot em linha própria ("Uma Mão"/"Duas Mãos") como no Wowhead
    assert extrair_slot("Uma Mão\nEspada\n9 - 16 de Dano") == "Arma de 1 Mão"
    assert extrair_slot("Duas Mãos\nCajado") == "Arma de 2 Mãos"

    # Procs ("Chance ao acertar:") também são efeitos
    assert "lança raios" in extrair_efeito("Chance ao acertar: lança raios")

    assert extrair_subtipo("Espada") == "Espada"
    assert extrair_fonte("Saqueado de: Zul'jan") == "Saqueado de: Zul'jan"
    assert extrair_vinculo_conteudo("Dungeon") == "Masmorra"
    assert extrair_slot_alvo("Encantamento de Ferramenta") == "Ferramenta"
    assert extrair_gema_cor("Gema Vermelha") == "Vermelha"
    assert extrair_rank("Rank 2") == 2

    prim_efeito, sec_efeito = extrair_atributos_de_efeito(
        "Encanta a ferramenta, aumentando em 30 a Engenhosidade.", "ptbr"
    )
    assert prim_efeito == {}
    assert sec_efeito.get("Engenhosidade") == 30, sec_efeito

    # Duas ocorrências: a primeira sem número, a segunda com o valor
    _, sec_efeito2 = extrair_atributos_de_efeito(
        "Encanta com Engenhosidade Ren'dorei, aumentando em 30 a Engenhosidade.",
        "ptbr",
    )
    assert sec_efeito2.get("Engenhosidade") == 30, sec_efeito2

    prim_generico, _ = extrair_atributos_de_efeito(
        "Diamante Talassiano (1) + 32 de Atributo Primário", "ptbr"
    )
    assert prim_generico.get("Atributo Primário") == 32

    # Gema PT multi-linha
    _, sec_gema = extrair_atributos_localizados(
        "Peridoto Mortal Impecável\nPeridoto\nNível do Item:\n295\n"
        "+\n16\nde Aceleração e +\n7\nde Acerto Crítico\nUso:",
        "ptbr",
    )
    assert sec_gema.get("Aceleração") == 16, sec_gema
    assert sec_gema.get("Acerto Crítico") == 7, sec_gema

    # Gema EN multi-linha
    _, sec_gema_en = extrair_atributos_localizados(
        "Flawless Deadly Peridot\nPeridot\nItem Level\n295\n"
        "+\n16\nHaste & +\n7\nCritical Strike\nUse:",
        "en",
    )
    assert sec_gema_en.get("Haste") == 16, sec_gema_en
    assert sec_gema_en.get("Critical Strike") == 7, sec_gema_en

    assert (
        classificar_tipo_item("Encantamento de Aceleração", "", "Encantamentos")
        == "encantamento"
    )
    assert classificar_tipo_item("Gema de Maestria", "", "Gemas") == "gema"
    assert (
        classificar_tipo_item(
            "Missiva Talassiana da Engenhosidade", "", "Missivas (tipos)"
        )
        == "missiva"
    )
    assert (
        classificar_tipo_item("Peitoral de Placas", "Peito\nPlacas", "Gear")
        == "gear"
    )
    # Catálogo genérico: item com slot de gear não vira encantamento/gema
    assert (
        classificar_tipo_item(
            "Gebbo's Bottomless Bag", "Berloque", "Encantamentos", "/items/enchants"
        )
        == "gear"
    )
    assert (
        classificar_tipo_item(
            "Peitoral Craftado", "Embellishment: ...", "Gear"
        )
        == "embelezamento"
    )
    print("[OK] Atributos, slot, armadura, subtipo, tipo e fonte")


def testar_listagem() -> None:
    itens = parse_links_itens(FIXTURE_LISTA, "https://www.wowhead.com/pt/guides/x")
    assert len(itens) == 2, itens

    primeiro = itens[0]
    assert primeiro["id"] == "250001"
    assert primeiro["nome"] == "Lâmina do Vazio"
    assert primeiro["item_level"] == 341
    assert primeiro["qualidade"] == 4
    assert primeiro["icone_url"].endswith("large/inv_sword_2h_d_01.jpg")
    assert primeiro["bonus_ids"] == ["12838", "12839"]
    assert primeiro["url"].startswith("https://www.wowhead.com/pt/item=250001")

    segundo = itens[1]
    assert segundo["id"] == "250002"
    assert segundo["item_level"] == 318
    assert segundo["qualidade"] == 4
    assert segundo["icone_url"] == ""

    # associação via result.media
    associar_icones_media(
        [segundo],
        [
            {
                "src": "https://wow.zamimg.com/images/wow/icons/large/inv_jewelry_trinket_04.jpg",
                "alt": "Berloque Etéreo",
            }
        ],
    )
    assert "inv_jewelry_trinket_04" in segundo["icone_url"], segundo
    print("[OK] Parsing de listagem + associação de media")


def testar_finalizacao() -> None:
    bruto = {
        "id": "250001",
        "nome": "Lâmina do Vazio Forjado",
        "item_level": 341,
        "qualidade": 4,
        "icone_url": "",
        "bonus_ids": ["12838"],
        "url": "https://www.wowhead.com/pt/item=250001",
        "_contexto": FIXTURE_TOOLTIP,
    }
    item = finalizar_item(bruto)

    assert item["id"] == 250001
    assert item["slot"] == "Arma de 2 Mãos"
    assert item["tipo_armadura"] == "N/A"
    assert item["qualidade"] == 4 and item["qualidade_nome"] == "Épico"
    assert item["item_level"] == 341
    assert item["track"] == "Mito"
    assert item["track_stage"] == "6/6"
    assert item["voidforged"] is True
    assert item["atributos_primarios"] == {"Força": 1420, "Vigor": 2850}
    assert item["atributos_secundarios"] == {"Aceleração": 850, "Maestria": 620}
    assert "Seus golpes" in item["efeito_equip_uso"]
    for campo in (
        "id",
        "nome_ptbr",
        "slot",
        "tipo_armadura",
        "qualidade",
        "item_level",
        "track",
        "voidforged",
        "atributos_primarios",
        "atributos_secundarios",
        "efeito_equip_uso",
        "icone_url",
    ):
        assert campo in item, campo
    print("[OK] Finalização do item com todos os campos exigidos")


def testar_pagina_item() -> None:
    unico = parse_item_unico(
        FIXTURE_ITEM, "https://www.wowhead.com/pt/item=250001/lamina-do-vazio"
    )
    assert unico is not None
    assert unico["nome"] == "Lâmina do Vazio Forjado"
    assert unico["item_level"] == 341
    assert unico["qualidade"] == 4
    assert unico["icone_url"].endswith("inv_sword_2h_d_01.jpg")

    detalhado = extrair_detalhes_item(FIXTURE_ITEM, unico)
    item = finalizar_item(detalhado)
    assert item["slot"] == "Arma de 2 Mãos"
    assert item["voidforged"] is True
    assert item["atributos_primarios"]["Força"] == 1420

    # Qualidade detectada via .q5 dentro do tooltip
    unico_q5 = parse_item_unico(
        FIXTURE_ITEM_Q5, "https://www.wowhead.com/pt/item=19019"
    )
    assert unico_q5 is not None
    assert unico_q5["qualidade"] == 5, unico_q5
    detalhado_q5 = finalizar_item(
        extrair_detalhes_item(FIXTURE_ITEM_Q5, unico_q5)
    )
    assert detalhado_q5["slot"] == "Arma de 1 Mão", detalhado_q5
    assert detalhado_q5["qualidade_nome"] == "Lendário"
    assert detalhado_q5["item_level"] == 40
    print("[OK] Página individual de item")


def testar_bilingue_e_variacoes() -> None:
    bruto = {
        "id": "250001",
        "nome": "Nome da listagem",
        "item_level": 341,
        "qualidade": 4,
        "icone_url": "inv_sword_2h_d_01",
        "bonus_ids": ["12838"],
        "url": "https://www.wowhead.com/pt/item=250001",
        "_pagina": "https://www.wowhead.com/pt/item=250001",
    }
    pt_bruto = {
        "nome": "Lâmina do Vazio Forjado",
        "item_level": 341,
        "qualidade": 4,
        "icone_url": "inv_sword_2h_d_01",
        "_contexto": FIXTURE_TOOLTIP,
    }
    en_bruto = {
        "nome": "Voidforged Blade",
        "item_level": 341,
        "qualidade": 4,
        "icone_url": "inv_sword_2h_d_01",
        "_contexto": FIXTURE_TOOLTIP_EN,
    }

    item = finalizar_item_bilingue(
        bruto,
        pt_bruto,
        en_bruto,
        "https://www.wowhead.com/pt/item=250001",
        "https://www.wowhead.com/item=250001",
    )

    assert item["nome_ptbr"] == "Lâmina do Vazio Forjado", item
    assert item["nome_en"] == "Voidforged Blade", item
    assert item["qualidade_nome"] == "Épico"
    assert item["qualidade_nome_en"] == "Epic"
    assert item["atributos_primarios"] == {"Força": 1420, "Vigor": 2850}
    assert item["atributos_primarios_en"] == {
        "Strength": 1420,
        "Stamina": 2850,
    }
    assert item["atributos_secundarios"] == {"Aceleração": 850, "Maestria": 620}
    assert item["atributos_secundarios_en"] == {"Haste": 850, "Mastery": 620}
    assert item["idioma_atributos_primarios"] == "ptbr"
    assert item["slot"] == "Arma de 2 Mãos"
    assert item["track"] == "Mito" and item["track_stage"] == "6/6"
    assert item["voidforged"] is True
    assert item["id_completo"] == "item=250001&bonus=12838&ilvl=341"
    assert item["url_en"].endswith("/item=250001")

    # Variações com Bonus IDs distintos são chaves distintas
    chave_a = chave_variacao("250001", 341, ["12838"], "6/6")
    chave_b = chave_variacao("250001", 341, ["12839"], "6/6")
    assert chave_a != chave_b
    assert chave_a == chave_variacao("250001", 341, ["12838"], "6/6")
    print("[OK] Consolidação bilíngue + chaves de variação")


def testar_qualidade_craft() -> None:
    # Extração do rótulo no tooltip (PT/EN) e ausência de dado
    assert extrair_qualidade_craft("Qualidade de criação: 5") == 5
    assert extrair_qualidade_craft("Crafting Quality: 4") == 4
    assert extrair_qualidade_craft("Qualidade do craft R5") == 5
    assert extrair_qualidade_craft("sem informação de craft") == 0

    bruto = {
        "id": "250001",
        "nome": "Lâmina do Vazio Forjado",
        "item_level": 341,
        "qualidade": 4,
        "bonus_ids": [],
        "url": "https://www.wowhead.com/pt/item=250001?crafting-quality=5",
        "_pagina": "https://www.wowhead.com/pt/item=250001?crafting-quality=5",
    }
    pt_bruto = {
        "nome": "Lâmina do Vazio Forjado",
        "item_level": 341,
        "qualidade": 4,
        "_contexto": FIXTURE_TOOLTIP,
        "_profissao_craft": "Ferraria",
    }

    item = finalizar_item_bilingue(
        bruto,
        pt_bruto,
        {},
        bruto["url"],
        "",
    )
    # Raridade continua Épico (4); craft é R5 e vem da URL
    assert item["qualidade"] == 4, item
    assert item["qualidade_nome"] == "Épico", item
    assert item["qualidade_craft"] == 5, item
    assert item["qualidade_craft_fonte"] == "url:crafting-quality", item

    # Sem profissão de craft, a qualidade de craft não se aplica
    sem_prof = dict(pt_bruto)
    sem_prof.pop("_profissao_craft")
    item_sem_prof = finalizar_item_bilingue(
        bruto, sem_prof, {}, bruto["url"], ""
    )
    assert item_sem_prof["qualidade_craft"] == 0, item_sem_prof
    assert item_sem_prof["qualidade_craft_fonte"] == "", item_sem_prof

    print("[OK] Qualidade de craft (R5) separada da raridade")


def testar_markdown_final() -> None:
    item = {
        "id": 250001,
        "id_completo": "item=250001&bonus=12838&ilvl=341",
        "nome_en": "Voidforged Blade",
        "nome_ptbr": "Lâmina do Vazio Forjado",
        "tipo_item": "gear",
        "subtipo": "Espada",
        "slot": "Arma de 2 Mãos",
        "slot_alvo": "",
        "profissao_craft": "Ferraria",
        "embelezamento": False,
        "missiva_atributo": "",
        "missivas_aplicaveis": ["Engenhosidade", "Finesse"],
        "gema_cor": "",
        "rank": 0,
        "fonte": "Saqueado de: Zul'jan",
        "vinculo_conteudo": "Masmorra",
        "tipo_armadura": "N/A",
        "qualidade": 4,
        "qualidade_nome": "Épico",
        "qualidade_nome_en": "Epic",
        "qualidade_craft": 5,
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
        "efeito_equip_uso": "Equip: libera energia do Vazio.",
        "efeito_equip_uso_en": "Equip: unleash Void energy.",
        "icone_url": "https://wow.zamimg.com/images/wow/icons/large/inv_sword_2h_d_01.jpg",
        "bonus_ids": ["12838"],
        "url": "https://www.wowhead.com/pt/item=250001",
        "url_en": "https://www.wowhead.com/item=250001",
    }
    variacao = dict(item)
    variacao["bonus_ids"] = ["12839"]
    variacao["id_completo"] = "item=250001&bonus=12839&ilvl=341"

    md = gerar_markdown_final(
        [item, variacao],
        metadata={
            "versao_scraper": "teste",
            "ilvl_min": 305,
            "ilvl_max": 350,
            "qualidade_min": 3,
        },
    )

    assert "| Ícone | Nome (EN) | Nome (PT-BR) | Tipo de Item | Slot | Subtipo |" in md, md[:800]
    assert "| Craft (R) |" in md, md[:800]
    assert "| R5 |" in md, md[:2000]
    assert "### Arma de 2 Mãos" in md, md[:1200]
    assert md.count('<img src="https://wow.zamimg.com') == 2, md.count(
        '<img src="https://wow.zamimg.com'
    )
    assert md.count("Voidforged Blade") >= 2
    assert md.count("Lâmina do Vazio Forjado") >= 2
    assert "12838" in md and "12839" in md
    assert "Strength +1420" not in md  # tabela principal usa PT
    assert "Força +1420" in md
    assert "Épico (Epic)" in md
    assert "Ferraria" in md
    assert "Masmorra" in md
    assert "Missivas aplicáveis" in md
    print("[OK] Markdown final com ícones, nomes EN/PT-BR e variações")


def testar_api_deepseek() -> None:
    import os

    from config import (
        chave_deepseek_configurada,
        configurar_deepseek_api_key,
        validar_chave_deepseek,
    )

    anterior = os.environ.get("DEEPSEEK_API_KEY")
    assert not validar_chave_deepseek("")
    assert not validar_chave_deepseek("curta")
    assert not validar_chave_deepseek("chave com espacos e longa demais")

    chave = "sk-" + "a" * 30
    assert validar_chave_deepseek(chave)
    assert configurar_deepseek_api_key(chave)
    assert chave_deepseek_configurada()
    assert not configurar_deepseek_api_key("inválida")

    if anterior is None:
        os.environ.pop("DEEPSEEK_API_KEY", None)
    else:
        os.environ["DEEPSEEK_API_KEY"] = anterior
    print("[OK] API DeepSeek: campo, persistência e validação")


def testar_recomendacoes() -> None:
    gear = {
        "id": 250001,
        "tipo_item": "gear",
        "nome_ptbr": "Lâmina do Vazio Forjado",
        "nome_en": "Voidforged Blade",
        "slot": "Arma de 2 Mãos",
        "item_level": 341,
        "atributos_primarios": {"Força": 1420},
        "atributos_secundarios": {"Aceleração": 850, "Maestria": 620},
    }
    catalogo = [
        {
            "tipo_item": "encantamento",
            "nome_ptbr": "Encantamento de Aceleração",
            "nome_en": "Enchant Haste",
            "slot_alvo": "Arma",
            "rank": 2,
            "atributos_secundarios": {"Aceleração": 1200},
        },
        {
            "tipo_item": "encantamento",
            "nome_ptbr": "Encantamento de Maestria",
            "nome_en": "Enchant Mastery",
            "slot_alvo": "Arma",
            "rank": 2,
            "atributos_secundarios": {"Maestria": 900},
        },
        {
            "tipo_item": "gema",
            "nome_ptbr": "Gema de Aceleração",
            "nome_en": "Haste Gem",
            "atributos_secundarios": {"Aceleração": 600},
            "gema_cor": "Vermelha",
        },
        {
            "tipo_item": "gema",
            "nome_ptbr": "Gema de Maestria",
            "nome_en": "Mastery Gem",
            "atributos_secundarios": {"Maestria": 500},
        },
    ]

    rec = gerar_recomendacoes(
        [gear] + catalogo,
        "Guerreiro",
        "Fúria",
        ["Aceleração", "Crítico", "Maestria"],
        limite=2,
    )
    assert rec["status"] == "ok"
    assert rec["primario"] == "Força"
    linha = rec["itens"][0]
    assert "Aceleração" in linha["melhor_encantamento"]
    assert "prioridade #1" in linha["encantamento_justificativa"]
    assert linha["encantamento_alternativas"]
    assert "Aceleração" in linha["melhor_gema"]
    assert "prioridade #1" in linha["gema_justificativa"]

    # Encantamento de ferramenta não pode ser sugerido para cabeça
    cabeca = dict(gear)
    cabeca["slot"] = "Cabeça"
    rec_cabeca = gerar_recomendacoes(
        [cabeca] + catalogo,
        "Guerreiro",
        "Fúria",
        ["Aceleração", "Crítico", "Maestria"],
    )
    linha_cabeca = rec_cabeca["itens"][0]
    assert linha_cabeca["melhor_encantamento"] == "", linha_cabeca
    assert linha_cabeca["melhor_gema"], linha_cabeca

    sem_catalogo = gerar_recomendacoes(
        [gear], "Guerreiro", "Fúria", ["Aceleração"]
    )
    assert sem_catalogo["status"] == "sem_catalogo"
    assert sem_catalogo["itens"] == []
    print("[OK] Recomendações com justificativa e alternativas")


def testar_config() -> None:
    from config import CATEGORIAS_WOW, montar_categorias_selecionadas

    assert "ferramentas_profissao" in CATEGORIAS_WOW
    assert "gear_season2" in CATEGORIAS_WOW

    categorias = montar_categorias_selecionadas(
        ["gear_season2", "ferramentas_profissao"], 318, 344
    )
    nomes = list(categorias)
    assert "Gear de Combate (Season 2)" in nomes
    assert "Equipamentos de Profissão" in nomes

    # P-01b/F-01: gear usa os IDs canônicos da temporada
    # (`item=<id>?bonus=12856`) porque a listagem genérica do Wowhead não
    # filtra `ilvl`/`bonus` server-side.
    from config import urls_gear_canonicas

    urls_gear = categorias["Gear de Combate (Season 2)"]
    assert urls_gear == urls_gear_canonicas(), len(urls_gear)
    assert urls_gear, "lista canônica de gear não pode ser vazia"
    for url in urls_gear:
        assert "/pt/item=" in url, url
        assert "bonus=12856" in url, url

    from config import normalizar_url_gear

    expandidas = normalizar_url_gear(
        "https://www.wowhead.com/pt/items/min-level:305/max-level:350"
    )
    assert len(expandidas) == 2, expandidas
    assert all("min-ilvl:305" in u and "max-ilvl:350" in u for u in expandidas)
    assert any("/armor/" in u for u in expandidas)
    assert any("/weapons/" in u for u in expandidas)
    print("[OK] Mapeamento de categorias do config.py")


def main() -> int:
    try:
        testar_icones()
        testar_tracks()
        testar_atributos()
        testar_listagem()
        testar_finalizacao()
        testar_pagina_item()
        testar_bilingue_e_variacoes()
        testar_qualidade_craft()
        testar_markdown_final()
        testar_api_deepseek()
        testar_recomendacoes()
        testar_config()
    except AssertionError as exc:
        print(f"[FALHOU] {exc}")
        return 1

    # Sanidade do BeautifulSoup disponível
    assert BeautifulSoup("<a href='/item=1'>x</a>", "html.parser") is not None
    print("\nTodos os testes da Season 2 passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
